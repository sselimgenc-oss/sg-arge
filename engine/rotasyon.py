"""Portfolio rotation books (T22, docs/EVRENSEL_KURALLAR.md D12).

``engine/portfolio.py`` runs every symbol on its own. Rotation cards instead decide *which instruments to hold*
from a comparison across instruments. Three modes, all declared in the card's ``rotasyon:`` block:

* ``kesitsel``      rank the universe by ``skor`` on each rebalance date, hold the top N equal-weight
                    (optional absolute ``filtre`` per symbol, optional market ``rejim`` gate).
* ``sirali_giris``  per-symbol ``giris``/``cikis`` rules, at most ``max_pozisyon`` slots, new entries ranked by ``skor``.
* ``gecis``         named instruments and an if/else tree (``agac``) that is evaluated every bar.

Execution follows EVRENSEL_KURALLAR A: the decision uses closed bars only and fills at the next bar's open;
cost is charged on traded notional; no leverage (leveraged ETFs are plain instruments). There is no per-trade stop
unless the source has one, so risk is measured on the portfolio MDD in the later stages.
"""

from __future__ import annotations

import math
from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import expr as _expr
from engine import gosterge as _ind
from engine.portfolio import BacktestResult

MODES = ("kesitsel", "sirali_giris", "gecis")
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


def _kesitsel_weights(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex,
                      benchmark: pd.DataFrame | None, week_end: str, membership: pd.DataFrame | None) -> pd.DataFrame:
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
    weights = pd.DataFrame(0.0, index=calendar, columns=score.columns)
    # giris_filtre gates only symbols that are not held yet: a held name stays while it is still in the top N
    entry_gate = tables["giris_filtre"].fillna(False).astype(bool) if "giris_filtre" in tables else None
    held: set[str] = set()
    for date in calendar[decide.to_numpy()]:
        row = score.loc[date].where(eligible.loc[date]).dropna()
        chosen = list(row.sort_values(ascending=False, kind="stable").index[:count])
        if entry_gate is not None:
            chosen = [s for s in chosen if s in held or bool(entry_gate.at[date, s])]
            held = set(chosen)
        if chosen:
            weights.loc[date, chosen] = 1.0 / count
    weights.attrs["karar"] = decide
    return weights


def _sirali_weights(card: Mapping[str, Any], frames: Mapping[str, pd.DataFrame], calendar: pd.DatetimeIndex,
                    benchmark: pd.DataFrame | None, week_end: str, membership: pd.DataFrame | None) -> pd.DataFrame:
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
    score_values, entry_values, leave_values = score.to_numpy(float), entry.to_numpy(bool), leave.to_numpy(bool)
    decide_values = decide.to_numpy()
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
    table = pd.DataFrame(rows, index=calendar).reindex(columns=score.columns).fillna(0.0)
    table.attrs["karar"] = decide
    return table


def agirliklar(
    card: Mapping[str, Any],
    frames: Mapping[str, pd.DataFrame],
    *,
    benchmark: pd.DataFrame | None = None,
    week_end: str = "FRI",
    membership: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Target weights decided on each bar's close (index = signal bar, columns = instruments)."""
    block = card["rotasyon"]
    calendar = _calendar(frames)
    prepared = {symbol: _ffilled(frame, calendar) for symbol, frame in frames.items()}
    if block["kip"] == "gecis":
        return _gecis_weights(card, prepared, calendar)
    if len(frames) < int(block.get("min_evren", 8)):
        raise RotasyonVeriYok("evren_kucuk", [str(len(frames))])
    if block["kip"] == "kesitsel":
        return _kesitsel_weights(card, frames, calendar, benchmark, week_end, membership)
    return _sirali_weights(card, frames, calendar, benchmark, week_end, membership)


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
) -> BacktestResult:
    """One rotation book over ``[start, end]``; indicators warm up on all earlier data (``weights``: reuse a computed table)."""
    if weights is None:
        weights = agirliklar(card, frames, benchmark=benchmark, week_end=week_end, membership=membership)
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
