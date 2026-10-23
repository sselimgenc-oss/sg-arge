"""Portfolio rotation books (T22, docs/EVRENSEL_KURALLAR.md D12).

``engine/portfolio.py`` runs every symbol on its own. Rotation cards instead decide *which instruments to hold*
from a comparison across instruments. Three modes, all declared in the card's ``rotasyon:`` block:

* ``kesitsel``      rank the universe by ``skor`` on each rebalance date, hold the top N equal-weight
                    (optional absolute ``filtre`` per symbol, optional market ``rejim`` gate).
* ``sirali_giris``  per-symbol ``giris``/``cikis`` rules, at most ``max_pozisyon`` slots, new entries ranked by ``skor``.
* ``gecis``         named instruments and an if/else tree (``agac``) that is evaluated every bar.
* ``trend_sepet``   (U1) every symbol whose ``filtre`` is true is held; the weight comes from a per-class budget
                    (``sinif_butce``) split by inverse volatility (``agirlik: ters_vol``). Optional cross-sectional
                    cut: ``skor`` + ``grup`` + ``k`` keep only the top-k symbols of each group.

``agirlik`` (``esit`` | ``ters_vol``, ``vol_n`` default 60) is also read by ``kesitsel`` (weights of the chosen N, total 1).

Execution follows EVRENSEL_KURALLAR A: the decision uses closed bars only and fills at the next bar's open;
cost is charged on traded notional; no leverage (leveraged ETFs are plain instruments). There is no per-trade stop
unless the source has one, so risk is measured on the portfolio MDD in the later stages.
"""

from __future__ import annotations

import copy
import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from engine import expr as _expr
from engine import gosterge as _ind
from engine.portfolio import BacktestResult

MODES = ("kesitsel", "sirali_giris", "gecis", "trend_sepet")
WEIGHTINGS = ("esit", "ters_vol")
REBALANCE_TYPES = ("gun", "hafta", "ay")
CASH = "nakit"
_CARRY_BARS = 3


class RotasyonVeriYok(Exception):
    """The instruments a rotation book needs are not available over the test window."""

    def __init__(self, reason: str, symbols: list[str] | None = None) -> None:
        super().__init__(f"{reason}: {','.join(symbols or [])}" if symbols else reason)
        self.reason = reason
        self.symbols = symbols or []


# --------------------------------------------------------------------------------------------- card structure
def _tree_nodes(node: Any):
    yield node
    if not isinstance(node, Mapping):
        return
    if "eger" in node:
        yield from _tree_nodes(node.get("ise"))
        yield from _tree_nodes(node.get("degilse"))
    for child in node.get("esit") or []:
        yield from _tree_nodes(child)


def tree_assets(node: Any) -> list[str]:
    """Every instrument named in a ``gecis`` tree, in first-seen order."""
    found: list[str] = []
    for item in _tree_nodes(node):
        if not isinstance(item, Mapping):
            continue
        if "tut" in item and item["tut"] != CASH:
            found += [item["tut"]] if isinstance(item["tut"], str) else list(item["tut"])
        if "sec" in item:
            found += list(item["sec"].get("adaylar") or [])
        if "ters_vol" in item:
            found += list(item["ters_vol"].get("varliklar") or [])
    return list(dict.fromkeys(found))


def _rebalance_ok(value: Any) -> bool:
    if not isinstance(value, Mapping) or value.get("tip") not in REBALANCE_TYPES:
        return False
    every = value.get("her", 1)
    return value["tip"] != "gun" or (isinstance(every, int) and not isinstance(every, bool) and every >= 1)


def expressions(card: Mapping[str, Any]) -> list[tuple[str, str]]:
    """(field, text) of every expression in the block; ``{v}`` templates are expanded with the first candidate."""
    block = card.get("rotasyon") or {}
    out: list[tuple[str, str]] = []
    for key in ("skor", "filtre", "giris_filtre", "rejim", "giris", "cikis"):
        if isinstance(block.get(key), str):
            out.append((f"rotasyon.{key}", block[key]))
    for node in _tree_nodes(block.get("agac")):
        if not isinstance(node, Mapping):
            continue
        if isinstance(node.get("eger"), str):
            out.append(("rotasyon.agac.eger", node["eger"]))
        pick = node.get("sec")
        if isinstance(pick, Mapping) and isinstance(pick.get("skor"), str) and pick.get("adaylar"):
            out.append(("rotasyon.agac.sec.skor", pick["skor"].replace("{v}", str(pick["adaylar"][0]).lower())))
    return out


def dogrula(card: Mapping[str, Any]) -> list[str]:
    """Structural problems of the ``rotasyon`` block (empty list = fine); expressions are checked by ``engine.spec``."""
    block = card.get("rotasyon")
    if not isinstance(block, Mapping):
        return ["rotasyon bir sozluk olmali"]
    problems: list[str] = []
    mode = block.get("kip")
    if mode not in MODES:
        return [f"rotasyon.kip gecersiz: {mode!r} (gecerli: {', '.join(MODES)})"]
    if not _rebalance_ok(block.get("dengeleme")):
        problems.append("rotasyon.dengeleme {tip: gun|hafta|ay, her: k (yalniz gun)} olmali")
    if mode in ("kesitsel", "sirali_giris") and not (isinstance(block.get("skor"), str) and block["skor"].strip()):
        problems.append("rotasyon.skor bos olmayan bir ifade olmali")
    if mode == "kesitsel":
        count, ratio = block.get("n"), block.get("n_oran")
        if (count is None) == (ratio is None):
            problems.append("kesitsel: n ya da n_oran (yalniz biri) gerekli")
        if count is not None and not (isinstance(count, int) and not isinstance(count, bool) and count >= 1):
            problems.append("rotasyon.n pozitif tam sayi olmali")
        if ratio is not None and not (isinstance(ratio, (int, float)) and 0 < ratio <= 1):
            problems.append("rotasyon.n_oran (0, 1] araliginda olmali")
    if mode == "sirali_giris":
        for key in ("giris", "cikis"):
            if not (isinstance(block.get(key), str) and block[key].strip()):
                problems.append(f"sirali_giris: rotasyon.{key} gerekli")
        slots = block.get("max_pozisyon")
        if not (isinstance(slots, int) and not isinstance(slots, bool) and slots >= 1):
            problems.append("sirali_giris: rotasyon.max_pozisyon pozitif tam sayi olmali")
    if mode == "gecis":
        problems += _check_tree(block.get("agac"), card)
    if mode == "trend_sepet":
        problems += _check_sepet(block)
    if block.get("agirlik") is not None and block["agirlik"] not in WEIGHTINGS:
        problems.append(f"rotasyon.agirlik gecersiz: {block['agirlik']!r} (gecerli: {', '.join(WEIGHTINGS)})")
    if block.get("vol_n") is not None and not (isinstance(block["vol_n"], int) and not isinstance(block["vol_n"], bool) and block["vol_n"] >= 2):
        problems.append("rotasyon.vol_n >= 2 tam sayi olmali")
    return problems


def _check_sepet(block: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if not (isinstance(block.get("filtre"), str) and block["filtre"].strip()):
        problems.append("trend_sepet: rotasyon.filtre gerekli")
    budget = block.get("sinif_butce")
    if not (isinstance(budget, Mapping) and budget and all(isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 for v in budget.values())):
        problems.append("trend_sepet: rotasyon.sinif_butce {sinif: oran > 0} gerekli")
    elif sum(budget.values()) > 1 + 1e-9:
        problems.append("trend_sepet: sinif_butce toplami 1'i gecemez (kaldirac yok)")
    ranked = [key for key in ("skor", "grup", "k") if block.get(key) is not None]
    if ranked and len(ranked) != 3:
        problems.append("trend_sepet: kesitsel kesim icin skor, grup ve k birlikte verilmeli")
    if len(ranked) == 3:
        group, picks = block["grup"], block["k"]
        if not (isinstance(group, Mapping) and isinstance(picks, Mapping)):
            problems.append("trend_sepet: grup {sinif: grup} ve k {grup: sayi} sozluk olmali")
        else:
            if isinstance(budget, Mapping) and set(group) != set(budget):
                problems.append("trend_sepet: grup anahtarlari sinif_butce siniflariyla ayni olmali")
            if set(group.values()) != set(picks):
                problems.append("trend_sepet: k anahtarlari grup adlariyla ayni olmali")
            if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 1 for v in picks.values()):
                problems.append("trend_sepet: k degerleri pozitif tam sayi olmali")
    scale = block.get("k_carpan", 1)
    if not (isinstance(scale, (int, float)) and not isinstance(scale, bool) and scale > 0):
        problems.append("trend_sepet: k_carpan pozitif sayi olmali")
    return problems


def _check_tree(node: Any, card: Mapping[str, Any]) -> list[str]:  # noqa: ARG001
    problems: list[str] = []
    for item in _tree_nodes(node):
        if not isinstance(item, Mapping):
            problems.append(f"agac dugumu sozluk olmali: {item!r}")
            continue
        kinds = [key for key in ("eger", "tut", "esit", "sec", "ters_vol") if key in item]
        if len(kinds) != 1:
            problems.append(f"agac dugumu tam bir tur icermeli (eger|tut|esit|sec|ters_vol): {sorted(item)}")
        elif kinds[0] == "eger" and not (isinstance(item.get("ise"), Mapping) and isinstance(item.get("degilse"), Mapping)):
            problems.append("eger dugumunde ise ve degilse gerekli")
        elif kinds[0] == "sec":
            pick = item["sec"]
            if not (isinstance(pick, Mapping) and pick.get("adaylar") and isinstance(pick.get("skor"), str)
                    and pick.get("yon") in ("yuksek", "dusuk") and isinstance(pick.get("n", 1), int)):
                problems.append("sec: {adaylar, skor ({v} sablonu), yon: yuksek|dusuk, n} gerekli")
        elif kinds[0] == "ters_vol":
            pick = item["ters_vol"]
            if not (isinstance(pick, Mapping) and pick.get("varliklar") and isinstance(pick.get("pencere"), int)):
                problems.append("ters_vol: {varliklar, pencere} gerekli")
    return problems


def needed_symbols(card: Mapping[str, Any]) -> list[str]:
    """Fixed instruments of a card (``gecis`` assets plus the ``varlik`` of indicators), empty for a market universe."""
    block = card.get("rotasyon") or {}
    names = tree_assets(block.get("agac")) if block.get("kip") == "gecis" else []
    for spec in (card.get("gostergeler") or {}).values():
        if isinstance(spec, Mapping) and spec.get("varlik"):
            names.append(spec["varlik"])
    return list(dict.fromkeys(names))


# --------------------------------------------------------------------------------------------- environments
def _evaluate(text: str, env: Mapping[str, Any], index: pd.Index, frame: pd.DataFrame | None = None) -> tuple[pd.Series, pd.Series]:
    """Value and validity (every named input is non-NaN) of an expression over ``index``."""
    from engine.kart_sinyal import mtf_callback  # noqa: PLC0415 - kart_sinyal imports this package's siblings

    parsed = _expr.parse(text)
    callback = mtf_callback(frame) if frame is not None else None
    value = parsed.evaluate(env, index=index, mtf=callback)
    if not isinstance(value, pd.Series):
        value = pd.Series(value, index=index)
    valid = pd.Series(True, index=index)
    for name in parsed.names:
        item = env.get(name)
        if isinstance(item, pd.Series):
            valid &= item.reindex(index).notna()
        elif isinstance(item, pd.DataFrame):
            attrs = [a for n, a in parsed.attrs if n == name]
            columns = [c for c in attrs if c in item.columns] or list(item.columns)
            valid &= item[columns].reindex(index).notna().all(axis=1)
    return value, valid & value.notna()


def _calendar(frames: Mapping[str, pd.DataFrame]) -> pd.DatetimeIndex:
    index = None
    for frame in frames.values():
        index = frame.index if index is None else index.union(frame.index)
    return index


def _ffilled(frame: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    """Frame on the shared calendar; a missing bar repeats the last close (flat, no volume)."""
    out = frame.reindex(calendar)
    out["close"] = out["close"].ffill()
    for column in ("open", "high", "low"):
        out[column] = out[column].fillna(out["close"])
    out["volume"] = out["volume"].fillna(0.0)
    return out.loc[out.index >= frame.index[0]]


def _own_specs(card: Mapping[str, Any], fixed: bool) -> dict[str, Mapping[str, Any]]:
    return {k: v for k, v in (card.get("gostergeler") or {}).items() if bool(v.get("varlik")) == fixed}


def _strip(spec: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in spec.items() if k != "varlik"}


def _asset_env(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex) -> dict[str, Any]:
    """gecis: every indicator is computed on its own instrument and aligned to the shared calendar."""
    env: dict[str, Any] = {}
    for name, spec in card["gostergeler"].items():
        symbol = spec.get("varlik")
        if symbol not in frames:
            raise RotasyonVeriYok("veri_yok", [str(symbol)])
        result = _ind.compute(frames[symbol], _strip(spec))
        env[name] = result.reindex(calendar, method="ffill")
    return env


# --------------------------------------------------------------------------------------------- gecis (tree)
def _gecis_weights(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex) -> pd.DataFrame:
    block = card["rotasyon"]
    env = _asset_env(card, frames, calendar)
    tree = block["agac"]
    assets = tree_assets(tree)
    cache: dict[int, Any] = {}
    returns = {a: frames[a]["close"].reindex(calendar, method="ffill").pct_change() for a in assets}

    def prepare(node: Mapping[str, Any]) -> None:
        if "eger" in node:
            cache[id(node)] = _evaluate(node["eger"], env, calendar)
            prepare(node["ise"])
            prepare(node["degilse"])
        elif "esit" in node:
            for child in node["esit"]:
                prepare(child)
        elif "sec" in node:
            pick = node["sec"]
            scores = {}
            for asset in pick["adaylar"]:
                value, valid = _evaluate(pick["skor"].replace("{v}", asset.lower()), env, calendar)
                scores[asset] = value.where(valid)
            cache[id(node)] = pd.DataFrame(scores)
        elif "ters_vol" in node:
            spec = node["ters_vol"]
            cache[id(node)] = pd.DataFrame({a: returns[a].rolling(spec["pencere"]).std(ddof=1) for a in spec["varliklar"]})

    prepare(tree)
    rows: list[dict[str, float]] = []

    def walk(node: Mapping[str, Any], loc: int) -> dict[str, float] | None:
        if "tut" in node:
            named = [node["tut"]] if isinstance(node["tut"], str) else list(node["tut"])
            return {a: 1.0 / len(named) for a in named if a != CASH}
        if "eger" in node:
            value, valid = cache[id(node)]
            if not valid.iloc[loc]:
                return None
            return walk(node["ise"] if bool(value.iloc[loc]) else node["degilse"], loc)
        if "esit" in node:
            share = 1.0 / len(node["esit"])
            total: dict[str, float] = {}
            for child in node["esit"]:
                got = walk(child, loc)
                if got is None:
                    return None
                for asset, weight in got.items():
                    total[asset] = total.get(asset, 0.0) + weight * share
            return total
        if "sec" in node:
            pick = node["sec"]
            row = cache[id(node)].iloc[loc].dropna()
            if len(row) < len(pick["adaylar"]):
                return None
            count = int(pick.get("n", 1))
            ordered = row.sort_values(ascending=pick["yon"] == "dusuk", kind="stable")
            chosen = list(ordered.index[:count])
            return {a: 1.0 / count for a in chosen}
        spec = node["ters_vol"]
        vols = cache[id(node)].iloc[loc]
        if vols.isna().any() or (vols <= 0).any():
            return None
        inverse = 1.0 / vols
        return (inverse / inverse.sum()).to_dict()

    for loc in range(len(calendar)):
        rows.append(walk(tree, loc) or {})
    table = pd.DataFrame(rows, index=calendar).reindex(columns=assets).fillna(0.0)
    table.attrs["karar"] = pd.Series(True, index=calendar)
    return table


# --------------------------------------------------------------------------------------------- kesitsel / sirali
def _decision_days(calendar: pd.DatetimeIndex, rule: Mapping[str, Any]) -> pd.Series:
    """Bars on which a (re)allocation is decided: the last bar of the week / month, or every k-th bar."""
    index = pd.Series(np.arange(len(calendar)), index=calendar)
    if rule["tip"] == "gun":
        return pd.Series(index.to_numpy() % int(rule.get("her", 1)) == 0, index=calendar)
    naive = calendar.tz_localize(None)
    key = np.asarray(naive.to_period("W") if rule["tip"] == "hafta" else naive.to_period("M"))
    last = pd.Series(calendar, index=calendar).groupby(key).transform("max")
    return pd.Series(calendar == last.to_numpy(), index=calendar)


def _universe_env(card: Mapping[str, Any], frame: pd.DataFrame, benchmark: pd.DataFrame | None, week_end: str) -> dict[str, Any]:
    specs = _own_specs(card, fixed=False)
    benchmarks = {"endeks": benchmark} if benchmark is not None else None
    if benchmark is None and any(spec.get("veri") == "endeks" for spec in specs.values()):
        from engine.kart_sinyal import EndeksYok  # noqa: PLC0415

        raise EndeksYok("endeks")
    return _ind.build_env(frame, specs, benchmarks=benchmarks, week_end=week_end)


def _per_symbol(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex,
                benchmark: pd.DataFrame | None, week_end: str, fields: tuple[str, ...]) -> dict[str, pd.DataFrame]:
    block = card["rotasyon"]
    out: dict[str, dict[str, pd.Series]] = {field: {} for field in fields}
    for symbol, frame in frames.items():
        env = _universe_env(card, frame, benchmark, week_end)
        for field in fields:
            text = block.get(field)
            if not text:
                continue
            value, valid = _evaluate(text, env, frame.index, frame)
            series = value if field in ("skor",) else value.astype(bool)
            out[field][symbol] = series.where(valid) if field == "skor" else (series & valid)
    # a symbol's own holiday must not drop it from the ranking: carry the last decided value for a few bars
    return {
        field: pd.DataFrame(items).reindex(calendar).ffill(limit=_CARRY_BARS) for field, items in out.items() if items
    }


def _count(block: Mapping[str, Any], size: int) -> int:
    if block.get("n") is not None:
        return int(block["n"])
    return max(int(block.get("n_min", 1)), math.ceil(block["n_oran"] * size - 1e-9))


def _member(table: pd.DataFrame, membership: pd.DataFrame | None) -> pd.DataFrame:
    """Mask a symbol x date table with point-in-time index membership (True = member), when given."""
    if membership is None:
        return table
    return table & membership.reindex(index=table.index, columns=table.columns).fillna(False).astype(bool)


def _random_scores(score: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Same shape and missing values as ``score``, with random ranks (the null model of T23)."""
    return pd.DataFrame(np.where(score.notna().to_numpy(), rng.random(score.shape), np.nan), index=score.index, columns=score.columns)


def _kesitsel_weights(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex,
                      benchmark: pd.DataFrame | None, week_end: str, membership: pd.DataFrame | None):
    """(real weights, null function): the null keeps eligibility, filters, regime, calendar and N and randomises the ranking."""
    block = card["rotasyon"]
    tables = _per_symbol(card, frames, calendar, benchmark, week_end, ("skor", "filtre", "giris_filtre", "rejim"))
    score = tables["skor"]
    eligible = _member(score.notna(), membership)
    if "filtre" in tables:
        eligible &= tables["filtre"].fillna(False).astype(bool)
    if "rejim" in tables:
        gate = tables["rejim"].fillna(False).astype(bool).any(axis=1)  # one market-wide series, identical in every column
        eligible = eligible.mul(gate, axis=0)
    decide = _decision_days(calendar, block["dengeleme"])
    count = _count(block, len(frames))
    # giris_filtre gates only symbols that are not held yet: a held name stays while it is still in the top N
    entry_gate = tables["giris_filtre"].fillna(False).astype(bool) if "giris_filtre" in tables else None

    columns = list(score.columns)
    eligible_values = eligible.to_numpy(bool)
    gate_values = entry_gate.to_numpy(bool) if entry_gate is not None else None
    decision_locs = np.flatnonzero(decide.to_numpy())
    inverse = _inverse_vol(frames, calendar, columns, block) if block.get("agirlik") == "ters_vol" else None

    def assign(values: pd.DataFrame) -> pd.DataFrame:
        scores = values.to_numpy(float)
        out = np.zeros(scores.shape)
        held: set[int] = set()
        for loc in decision_locs:
            usable = np.flatnonzero(eligible_values[loc] & ~np.isnan(scores[loc]))
            if not len(usable):
                continue
            order = usable[np.argsort(-scores[loc, usable], kind="stable")][:count]  # ties keep the column order
            chosen = [int(i) for i in order]
            if gate_values is not None:
                chosen = [i for i in chosen if i in held or gate_values[loc, i]]
                held = set(chosen)
            out[loc, chosen] = 1.0 / count if inverse is None else _split(inverse[loc, chosen], 1.0)
        weights = pd.DataFrame(out, index=calendar, columns=columns)
        weights.attrs["karar"] = decide
        return weights

    return assign(score), lambda rng: assign(_random_scores(score, rng))


# --------------------------------------------------------------------------------------------- weighting (U1)
def _inverse_vol(frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex, columns: list[str], block: Mapping[str, Any]) -> np.ndarray:
    """1 / (std of the symbol's own daily returns over ``vol_n`` bars), calendar x columns; NaN until the window fills."""
    window = int(block.get("vol_n", 60))
    table = {symbol: frames[symbol]["close"].pct_change().rolling(window).std() for symbol in columns}
    vol = pd.DataFrame(table).reindex(calendar).ffill(limit=_CARRY_BARS)
    return (1.0 / vol.replace(0.0, np.nan)).to_numpy(float)


def _split(inverse: np.ndarray, total: float) -> np.ndarray:
    """``total`` shared by inverse volatility; a symbol without history gets the average share."""
    usable = ~np.isnan(inverse)
    if not usable.any():
        return np.full(len(inverse), total / len(inverse))
    shares = np.where(usable, inverse, np.nanmean(inverse))
    return total * shares / shares.sum()


def _sepet_weights(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex,
                   benchmark: pd.DataFrame | None, week_end: str, membership: pd.DataFrame | None,
                   classes: Mapping[str, str] | None):
    """(real weights, null function) of a ``trend_sepet`` book.

    Trend-only: a symbol is held when its ``filtre`` is true and receives ``sinif_butce[class]`` x its inverse-vol share
    among *all* tradable members of the class, so the slice of a symbol without a signal stays in cash.
    With ``skor``/``grup``/``k``: scores are z-scored inside each class, the filter passers of a group are ranked and the
    top ``k x k_carpan`` are kept; the group's budget (sum of its classes' budgets) is split by inverse vol among them.
    The null keeps the holding count of every unit (class, or group when ranking) and picks the holdings at random.
    """
    block = card["rotasyon"]
    columns = list(frames)
    if not classes or any(s not in classes for s in columns):
        raise RotasyonVeriYok("sinif_yok", [s for s in columns if not classes or s not in classes])
    budget = {name: float(v) for name, v in block["sinif_butce"].items()}
    unknown = sorted({classes[s] for s in columns} - set(budget))
    if unknown:
        raise RotasyonVeriYok("sinif_butcesi_yok", unknown)
    ranked = block.get("grup") is not None
    tables = _per_symbol(card, frames, calendar, benchmark, week_end, ("skor", "filtre") if ranked else ("filtre",))
    passes = tables["filtre"].reindex(columns=columns).fillna(False).astype(bool)
    inverse = _inverse_vol(frames, calendar, columns, block)
    tradable = _member(pd.DataFrame(~np.isnan(inverse), index=calendar, columns=columns), membership)
    tradable_values = tradable.to_numpy(bool)
    pass_values = (passes & tradable).to_numpy(bool)
    equal = block.get("agirlik", "ters_vol") == "esit"
    cls = np.array([classes[s] for s in columns])
    unit_of = np.array([block["grup"][classes[s]] for s in columns]) if ranked else cls
    units = list(dict.fromkeys(unit_of))
    unit_budget = {u: sum(v for c, v in budget.items() if (block["grup"][c] if ranked else c) == u) for u in units}
    limits = {u: max(1, int(round(block["k"][u] * float(block.get("k_carpan", 1))))) for u in units} if ranked else {}
    decide = _decision_days(calendar, block["dengeleme"])
    decision_locs = np.flatnonzero(decide.to_numpy())

    z_values = None
    if ranked:
        score = tables["skor"].reindex(columns=columns)
        z = score.copy()
        for name in dict.fromkeys(cls):  # z-score inside a class on every date, so BIST and US stocks rank on one scale
            members = [i for i, c in enumerate(cls) if c == name]
            part = score.iloc[:, members].where(tradable.iloc[:, members])
            spread = part.std(axis=1, ddof=0).replace(0.0, np.nan)
            z.iloc[:, members] = part.sub(part.mean(axis=1), axis=0).div(spread, axis=0)
        z_values = z.to_numpy(float)
        pass_values = pass_values & ~np.isnan(z_values)

    def shares(loc: int, held: list[int], unit: str) -> dict[int, float]:
        if not held:
            return {}
        if equal:
            return {i: unit_budget[unit] / len(held) for i in held}
        if ranked:  # the picks share the group's budget
            return dict(zip(held, _split(inverse[loc, held], unit_budget[unit])))
        pool = np.flatnonzero((unit_of == unit) & tradable_values[loc])
        total = float(np.nansum(inverse[loc, pool]))
        return {i: unit_budget[unit] * inverse[loc, i] / total for i in held} if total > 0 else {}

    def assign(pick: Callable[[int, str, list[int]], list[int]]) -> pd.DataFrame:
        out = np.zeros((len(calendar), len(columns)))
        for loc in decision_locs:
            for unit in units:
                members = np.flatnonzero(unit_of == unit)
                real = [int(i) for i in members if pass_values[loc, i]]
                if ranked and real:
                    real = sorted(real, key=lambda i: -z_values[loc, i])[: limits[unit]]  # stable: ties keep the column order
                for i, share in shares(loc, pick(loc, unit, real), unit).items():
                    out[loc, i] = share
        weights = pd.DataFrame(out, index=calendar, columns=columns)
        weights.attrs["karar"] = decide
        return weights

    def null(rng: np.random.Generator) -> pd.DataFrame:
        def pick(loc: int, unit: str, real: list[int]) -> list[int]:
            ready = tradable_values[loc] & ~np.isnan(z_values[loc]) if ranked else tradable_values[loc]
            pool = np.flatnonzero((unit_of == unit) & ready)
            count = min(len(real), len(pool))
            return sorted(int(i) for i in rng.choice(pool, size=count, replace=False)) if count else []

        return assign(pick)

    return assign(lambda loc, unit, real: real), null


def _sirali_weights(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex,
                    benchmark: pd.DataFrame | None, week_end: str, membership: pd.DataFrame | None):
    """(real weights, null function): the null randomises which of the day's entry candidates takes a free slot."""
    block = card["rotasyon"]
    tables = _per_symbol(card, frames, calendar, benchmark, week_end, ("skor", "giris", "cikis", "rejim"))
    entry = _member(tables["giris"].fillna(False).astype(bool), membership)
    leave = tables["cikis"].fillna(False).astype(bool)
    score = tables["skor"]
    if "rejim" in tables:
        entry = entry.mul(tables["rejim"].fillna(False).astype(bool).any(axis=1), axis=0)
    decide = _decision_days(calendar, block["dengeleme"])
    slots = int(block["max_pozisyon"])
    columns = list(score.columns)
    entry_values, leave_values = entry.to_numpy(bool), leave.to_numpy(bool)
    decide_values = decide.to_numpy()

    def assign(values: pd.DataFrame) -> pd.DataFrame:
        score_values = values.to_numpy(float)
        held: list[int] = []
        rows = []
        for loc in range(len(calendar)):
            if decide_values[loc]:
                held = [i for i in held if not leave_values[loc, i]]
                if len(held) < slots:
                    taken = set(held)
                    ready = [i for i in range(len(columns)) if entry_values[loc, i] and i not in taken and not np.isnan(score_values[loc, i])]
                    ready.sort(key=lambda i: -score_values[loc, i])  # stable: ties keep the column order
                    held += ready[: slots - len(held)]
            rows.append({columns[i]: 1.0 / slots for i in held})
        table = pd.DataFrame(rows, index=calendar).reindex(columns=columns).fillna(0.0)
        table.attrs["karar"] = decide
        return table

    return assign(score), lambda rng: assign(_random_scores(score, rng))


def _gecis_null(real: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Same switch dates as the real tree; on each switch one of the tree's instruments is held at random (cash stays cash)."""
    values = real.to_numpy(float)
    out = np.zeros_like(values)
    for i in range(len(values)):
        if i and np.allclose(values[i], values[i - 1]):
            out[i] = out[i - 1]
        elif values[i].sum() > 1e-12:
            out[i, rng.integers(values.shape[1])] = 1.0
    table = pd.DataFrame(out, index=real.index, columns=real.columns)
    table.attrs["karar"] = real.attrs.get("karar", pd.Series(True, index=real.index))
    return table


@dataclass
class Baglam:
    """Real target weights of a card plus a generator of its random-selection null (T23)."""

    weights: pd.DataFrame
    null: Callable[[np.random.Generator], pd.DataFrame]


def hazirla(
    card: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    *,
    benchmark: pd.DataFrame | None = None,
    week_end: str = "FRI",
    membership: pd.DataFrame | None = None,
    siniflar: Mapping[str, str] | None = None,
) -> Baglam:
    """Weights decided on each bar's close and the null generator (index = signal bar, columns = instruments)."""
    block = card["rotasyon"]
    calendar = _calendar(frames)
    if block["kip"] == "gecis":
        prepared = {symbol: _ffilled(frame, calendar) for symbol, frame in frames.items()}
        real = _gecis_weights(card, prepared, calendar)
        return Baglam(real, lambda rng: _gecis_null(real, rng))
    if len(frames) < int(block.get("min_evren", 8)):
        raise RotasyonVeriYok("evren_kucuk", [str(len(frames))])
    if block["kip"] == "trend_sepet":
        real, null = _sepet_weights(card, frames, calendar, benchmark, week_end, membership, siniflar)
        return Baglam(real, null)
    build = _kesitsel_weights if block["kip"] == "kesitsel" else _sirali_weights
    real, null = build(card, frames, calendar, benchmark, week_end, membership)
    return Baglam(real, null)


def agirliklar(
    card: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    *,
    benchmark: pd.DataFrame | None = None,
    week_end: str = "FRI",
    membership: pd.DataFrame | None = None,
    siniflar: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Target weights decided on each bar's close (index = signal bar, columns = instruments)."""
    return hazirla(card, frames, benchmark=benchmark, week_end=week_end, membership=membership, siniflar=siniflar).weights


# --------------------------------------------------------------------------------------------- simulation
def simule(
    frames: Mapping[str, pd.DataFrame],
    weights: pd.DataFrame,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    cost_rate: float,
    initial_capital: float = 100_000.0,
    extra_delay_bars: int = 0,
    fill_at_close: bool = False,
) -> BacktestResult:
    """Next-open execution of the target weights; sells and buys pay ``cost_rate`` on traded notional.

    ``fill_at_close`` is the D4 market-on-close exception: a decision on a bar's close fills at that same close.
    """
    calendar = weights.index
    prepared = {s: _ffilled(frames[s], calendar) for s in weights.columns}
    names = list(weights.columns)
    opens = pd.DataFrame({s: f["open"] for s, f in prepared.items()}).reindex(calendar).to_numpy(float)
    closes = pd.DataFrame({s: f["close"] for s, f in prepared.items()}).reindex(calendar).to_numpy(float)
    targets = weights.to_numpy(float)
    decide = weights.attrs.get("karar", pd.Series(True, index=calendar)).to_numpy(bool)
    fills = closes if fill_at_close else opens
    window = np.flatnonzero((calendar >= start) & (calendar <= end))
    shares = np.zeros(len(names))
    cash = initial_capital
    current: np.ndarray | None = None
    equity, exposure, trades = [], [], []
    episode: dict[int, dict[str, Any]] = {}
    max_open = 0
    delay = (0 if fill_at_close else 1) + extra_delay_bars
    for loc in window:
        date = calendar[loc]
        signal = loc - delay
        if signal >= 0 and decide[signal]:
            target = targets[signal]
            if current is None or not np.allclose(target, current):
                price = fills[loc]
                live = ~np.isnan(price)
                value = cash + float((shares[live] * price[live]).sum())
                scale = 1.0  # fees come out of the book: shrink the targets until trades plus fees fit the equity
                wanted = shares.copy()
                for _ in range(5):
                    wanted = shares.copy()
                    wanted[live] = target[live] * value * scale / price[live]
                    fees = float((np.abs(wanted - shares)[live] * price[live]).sum()) * cost_rate
                    scale = max((value - fees) / value, 0.0) if value > 0 else 0.0
                for i in np.flatnonzero(live):
                    delta = float(wanted[i] - shares[i])
                    if abs(delta) < 1e-12:
                        continue
                    fee = abs(delta) * float(price[i]) * cost_rate
                    cash -= delta * float(price[i]) + fee
                    book = episode.get(i)
                    if delta > 0:
                        if book is None:
                            book = episode[i] = {"date": date, "price": float(price[i]), "qty": 0.0, "spent": 0.0, "got": 0.0, "fee": 0.0}
                        book["spent"] += delta * float(price[i])
                        book["qty"] = max(book["qty"], float(shares[i] + delta))
                    else:
                        book["got"] += -delta * float(price[i])
                    book["fee"] += fee
                    shares[i] += delta
                    if shares[i] <= 1e-9:
                        shares[i] = 0.0
                        trades.append(_trade(names[i], book, date, float(price[i]), "yeniden_dengeleme"))
                        episode.pop(i)
                current = target
        mark = float((shares * np.nan_to_num(closes[loc])).sum())
        equity.append(cash + mark)
        exposure.append(mark / equity[-1] if equity[-1] > 0 else 0.0)
        max_open = max(max_open, int((shares > 0).sum()))
    last = window[-1]
    for i, book in list(episode.items()):
        book["got"] += float(shares[i] * closes[last, i])
        trades.append(_trade(names[i], book, calendar[last], float(closes[last, i]), "donem_sonu"))
    index = calendar[window]
    frame = pd.DataFrame(trades, columns=_TRADE_COLUMNS)
    return BacktestResult(initial_capital, pd.Series(equity, index=index), pd.Series(exposure, index=index), frame, max_open)


_TRADE_COLUMNS = [
    "symbol", "entry_date", "exit_date", "entry_price", "exit_price", "quantity", "initial_stop", "initial_risk",
    "entry_cost", "exit_cost", "net_pnl", "r_multiple", "exit_reason",
]


def _trade(symbol: str, book: Mapping[str, Any], date: pd.Timestamp, price: float, reason: str) -> dict[str, Any]:
    return {
        "symbol": symbol, "entry_date": book["date"], "exit_date": date, "entry_price": book["price"],
        "exit_price": price, "quantity": book["qty"], "initial_stop": float("nan"), "initial_risk": float("nan"),
        "entry_cost": book["fee"], "exit_cost": 0.0, "net_pnl": book["got"] - book["spent"] - book["fee"],
        "r_multiple": float("nan"), "exit_reason": reason,
    }


def kos(
    card: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    cost_rate: float,
    benchmark: pd.DataFrame | None = None,
    week_end: str = "FRI",
    extra_delay_bars: int = 0,
    membership: pd.DataFrame | None = None,
    weights: pd.DataFrame | None = None,
    fill_at_close: bool = False,
    siniflar: Mapping[str, str] | None = None,
) -> BacktestResult:
    """One rotation book over ``[start, end]``; indicators warm up on all earlier data (``weights``: reuse a computed table)."""
    if weights is None:
        weights = agirliklar(card, frames, benchmark=benchmark, week_end=week_end, membership=membership, siniflar=siniflar)
    if card["rotasyon"]["kip"] == "gecis":
        late = [s for s in needed_symbols(card) if frames[s].index[0] > start + pd.Timedelta(days=7)]
        if late:
            raise RotasyonVeriYok("veri_yok_baslangic_sonra", late)
    if not ((weights.index >= start) & (weights.index <= end)).any():
        raise RotasyonVeriYok("donemde_veri_yok")
    return simule(
        frames, weights, start=start, end=end, cost_rate=cost_rate, extra_delay_bars=extra_delay_bars,
        fill_at_close=fill_at_close,
    )


# --------------------------------------------------------------------------------------------- plateau parameters (T23)
_LITERAL = re.compile(r"(?<![\w.{}])\d+(?:\.\d+)?(?![\w.}])")
_INDICATOR_KEYS = ("n", "carpan")


@dataclass
class Parametre:
    """One numeric parameter of a rotation card; ``uygula(card, factor)`` returns a changed deep copy."""

    etiket: str
    deger: float
    uygula: Callable[[dict[str, Any], float], dict[str, Any]]


def _scaled(value: float, factor: float, integer: bool) -> float | int:
    return max(1, int(round(value * factor))) if integer else value * factor


def _literal_params(text: str, label: str, locate: Callable[[dict[str, Any]], tuple[Any, Any]]) -> list[Parametre]:
    """Every non-zero numeric literal of an expression (windows inside names stay untouched)."""
    found = []
    for k, match in enumerate(_LITERAL.finditer(text)):
        value = float(match.group())
        if value == 0.0:
            continue

        def apply(card: dict[str, Any], factor: float, k: int = k, raw: str = match.group(), value: float = value) -> dict[str, Any]:
            changed = copy.deepcopy(card)
            holder, key = locate(changed)
            hits = list(_LITERAL.finditer(holder[key]))
            new = _scaled(value, factor, "." not in raw)
            holder[key] = holder[key][: hits[k].start()] + format(new, "g") + holder[key][hits[k].end():]
            return changed

        found.append(Parametre(f"{label}#{k}:{match.group()}", value, apply))
    return found


def parametreler(card: Mapping[str, Any]) -> list[Parametre]:
    """Numeric parameters of the ``rotasyon`` block and of the indicators it uses (windows, thresholds, N), in card order."""
    found: list[Parametre] = []
    for name, spec in (card.get("gostergeler") or {}).items():
        for key in _INDICATOR_KEYS:
            value = spec.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                def apply(c: dict[str, Any], f: float, name: str = name, key: str = key, v: float = value) -> dict[str, Any]:
                    changed = copy.deepcopy(c)
                    changed["gostergeler"][name][key] = _scaled(v, f, isinstance(v, int))
                    return changed

                found.append(Parametre(f"gostergeler.{name}.{key}", float(value), apply))
    block = card["rotasyon"]
    for key in ("n", "n_oran", "max_pozisyon"):
        value = block.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            def apply(c: dict[str, Any], f: float, key: str = key, v: float = value) -> dict[str, Any]:
                changed = copy.deepcopy(c)
                changed["rotasyon"][key] = _scaled(v, f, isinstance(v, int))
                return changed

            found.append(Parametre(f"rotasyon.{key}", float(value), apply))
    every = (block.get("dengeleme") or {}).get("her")
    if isinstance(every, int) and not isinstance(every, bool):
        def apply(c: dict[str, Any], f: float, v: int = every) -> dict[str, Any]:
            changed = copy.deepcopy(c)
            changed["rotasyon"]["dengeleme"]["her"] = _scaled(v, f, True)
            return changed

        found.append(Parametre("rotasyon.dengeleme.her", float(every), apply))
    for key in ("skor", "filtre", "giris_filtre", "rejim", "giris", "cikis"):
        if isinstance(block.get(key), str):
            found += _literal_params(block[key], f"rotasyon.{key}", lambda c, key=key: (c["rotasyon"], key))
    # tree: walk by path so a variant edits exactly the node that was listed
    def walk(node: Any, path: tuple[Any, ...]) -> None:
        if not isinstance(node, Mapping):
            return
        def at(c: dict[str, Any], path: tuple[Any, ...] = path) -> Any:
            target = c["rotasyon"]["agac"]
            for step in path:
                target = target[step]
            return target

        if isinstance(node.get("eger"), str):
            found.extend(_literal_params(node["eger"], "agac" + "/".join(map(str, path)) + ".eger", lambda c, at=at: (at(c), "eger")))
            walk(node["ise"], path + ("ise",))
            walk(node["degilse"], path + ("degilse",))
        for i, child in enumerate(node.get("esit") or []):
            walk(child, path + ("esit", i))
        for key, field in (("sec", "n"), ("ters_vol", "pencere")):
            if isinstance(node.get(key), Mapping) and isinstance(node[key].get(field), int):
                def apply(c: dict[str, Any], f: float, at=at, key=key, field=field, v: int = node[key][field]) -> dict[str, Any]:
                    changed = copy.deepcopy(c)
                    at(changed)[key][field] = _scaled(v, f, True)
                    return changed

                found.append(Parametre("agac" + "/".join(map(str, path)) + f".{key}.{field}", float(node[key][field]), apply))

    walk(block.get("agac"), ())
    return found
