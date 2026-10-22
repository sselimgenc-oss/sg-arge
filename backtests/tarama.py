#!/usr/bin/env python3
"""Stage 1 quick scan: strategy cards -> shared T1a portfolio engine (T5b-1, daily/weekly cards).

Every ready card (`spec_durumu: tam`, `ozel_kod: false`) runs on each of the four
markets over the in-sample period only (2020-01-01 -> 2024-09-30) at 1x and 2x
cost. Stage 1 -> 2 rule (lider): in at least one market IS trades >= 30, 1x PF
>= 1.1 and 2x net > 0. The OOS (2024-10 ->) and 2015-2019 data are not looked at.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests.run_codex21 import _git_sha, _load_market  # noqa: E402
from data.evren_pit import PITUniverse, filter_entry_signals, load_pit_universe  # noqa: E402
from data.bist_1h import normalize_market_1h, quality_gate as bist_1h_quality_gate  # noqa: E402
from engine import gosterge, rotasyon  # noqa: E402
from engine.kart_sinyal import EndeksYok, MotorDestegiYok, PipsPiyasaDisi, build_plan  # noqa: E402
from engine.portfolio import calculate_metrics, run_portfolio  # noqa: E402
from engine.resample import resample_hourly  # noqa: E402
from engine.spec import normalize_timeframe  # noqa: E402
from strategies.ozel import has_strategy as has_special_strategy, build_plan as build_special_plan  # noqa: E402

IS_START = pd.Timestamp("2020-01-01", tz="UTC")
IS_END = pd.Timestamp("2024-09-30", tz="UTC")
MARKETS = ("BIST30", "ABD25", "KRIPTO25", "EMTIA")
BASE_COST = {"BIST30": 0.0015, "ABD25": 0.0005, "KRIPTO25": 0.0015, "EMTIA": 0.0005}
MARKET_TOKEN = {"BIST30": "BIST", "ABD25": "ABD", "KRIPTO25": "KRIPTO", "EMTIA": "EMTIA"}
BASE_COST["FX8"] = 0.0001
MARKET_TOKEN["FX8"] = "FX"
BENCHMARK_SYMBOL = {"ABD25": "SPY", "KRIPTO25": "BTCUSDT"}  # BIST30/EMTIA: no index series yet
MIN_TRADES, MIN_PF, PF_ALARM = 30, 1.1, 4.0
DAILY_TFS = ("1D", "1W")
RESAMPLED_HOURLY_TFS = ("2H", "4H")
SUBHOURLY_TFS = ("1m", "5m", "15m", "30m")
TF_DIR = {"1H": "hourly", "2H": "hourly", "4H": "hourly", "30m": "30m", "15m": "15m", "5m": "5m", "1m": "1m"}
TF_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "1H": 60, "2H": 120, "4H": 240}
IS_FRACTION = 2 / 3  # EVRENSEL_KURALLAR C: hourly yfinance markets, first 2/3 in-sample, last 1/3 unseen
MOC_COST_FACTOR = 2.0  # EVRENSEL_KURALLAR D4: close fills carry 2x base cost
FIXED_DATA_DIR = ROOT / "data" / "daily"  # daily bars of the named instruments of rotation `gecis` cards

OUTPUT_COLUMNS = [
    "id", "piyasa", "tf", "durum", "islem", "PF_1x", "PF_2x", "net_1x", "net_2x", "sharpe", "mdd",
    "maruziyet", "asama2_aday", "neden", "kart_yazari", "piyasa_kisiti", "stop_eklendi", "dolum",
    "PF_1x_b", "net_1x_b", "islem_b", "pf_alarmi", "data_hash", "git_sha",
]


def load_cards(directory: Path, tf: str) -> list[dict[str, Any]]:
    cards = []
    for path in sorted(directory.glob("*.yaml")):
        card = yaml.safe_load(path.read_text(encoding="utf-8"))
        card["tf"] = normalize_timeframe(card.get("tf"))
        runnable = not card.get("ozel_kod") or has_special_strategy(card["id"])
        if card.get("spec_durumu") in ("tam", "dakikalik") and runnable and card.get("tf") in tf.split(","):
            cards.append(card)
    return cards


def weekly_frame(frame: pd.DataFrame, week_end: str) -> pd.DataFrame:
    """Weekly OHLCV indexed by the week's first bar (the engine fills at the next week's open)."""
    del week_end  # Monday-keyed weeks cover both Friday and Sunday week ends
    keys = gosterge._htf_keys(frame.index, "1W")  # noqa: SLF001
    grouped = frame.groupby(keys, sort=True)
    weekly = grouped.agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    weekly.index = pd.DatetimeIndex(frame.index.to_series().groupby(keys, sort=True).first().to_numpy())
    return weekly


def annualization_for(tf: str, market: str) -> int:
    """Bars per year for the Sharpe annualisation (crypto trades around the clock)."""
    if tf == "1W":
        return 52
    if tf == "1D":
        return 365 if market == "KRIPTO25" else 252
    if market == "FX8":
        return (24 * 60 // TF_MINUTES[tf]) * 252  # 24h weekday FX archive
    # 2H/4H US/commodity bars include the closed short final session bucket.
    # Preserve the established 1H factor for existing CI parity results.
    if market != "KRIPTO25" and tf in RESAMPLED_HOURLY_TFS:
        if market == "BIST30":
            return {"2H": 4, "4H": 2}[tf] * 252
        return {"2H": 4, "4H": 2}[tf] * 252
    per_day = 24 * 60 // TF_MINUTES[tf] if market == "KRIPTO25" else max(7 * 60 // TF_MINUTES[tf], 1)
    return per_day * (365 if market == "KRIPTO25" else 252)


def period_for(tf: str, market: str, data: dict[str, pd.DataFrame]) -> tuple[pd.Timestamp, pd.Timestamp]:
    """In-sample window: crypto and daily use the fixed IS; yfinance hourly markets the first 2/3 of their span."""
    if market == "KRIPTO25" or tf in DAILY_TFS:
        return IS_START, IS_END
    first = min(frame.index[0] for frame in data.values())
    last = max(frame.index[-1] for frame in data.values())
    return first, first + (last - first) * IS_FRACTION


def _unused_signal_function(frame: pd.DataFrame, market: str) -> pd.DataFrame:  # pragma: no cover
    raise RuntimeError("signals are precomputed")


def _metrics(result, annualization: int) -> dict[str, float]:
    return calculate_metrics(result, annualization=annualization)


@dataclass
class Prepared:
    frames: dict[str, pd.DataFrame]
    plan: Any
    annualization: int
    base_cost: float
    market: str
    start: pd.Timestamp
    end: pd.Timestamp
    runtime_cache: dict[str, Any] = field(default_factory=dict)

    def run(
        self,
        multiplier: float = 1.0,
        *,
        close_fill: bool | None = None,
        signals: dict[str, pd.DataFrame] | None = None,
        extra_delay_bars: int = 0,
        trusted_inputs: bool = False,
        trades_only: bool = False,
        **engine_extra: Any,
    ):
        """One portfolio run; ``close_fill`` defaults to the card's own fill mode, ``signals`` may replace the plan's.

        ``engine_extra`` goes to ``run_portfolio`` unchanged (paper trading: ``record_state``, ``initial_capital``)."""
        kwargs = dict(self.plan.engine_kwargs)
        kwargs.update(engine_extra)
        fill = self.plan.dolum_kapanis if close_fill is None else close_fill
        kwargs["fill_at_close"] = fill
        cost = self.base_cost * multiplier * (MOC_COST_FACTOR if fill else 1.0)
        return run_portfolio(
            self.frames, _unused_signal_function, market=self.market, start=self.start, end=self.end,
            cost_rate=cost, extra_delay_bars=extra_delay_bars,
            precomputed_signals=signals if signals is not None else self.plan.signals, **kwargs,
            trusted_inputs=trusted_inputs, trades_only=trades_only,
            runtime_cache=self.runtime_cache if trusted_inputs else None,
        )


def prepare(
    card: dict[str, Any],
    data: dict[str, pd.DataFrame],
    market: str,
    *,
    benchmark: pd.DataFrame | None = None,
    start: pd.Timestamp = IS_START,
    end: pd.Timestamp = IS_END,
    pit_universe: PITUniverse | None = None,
) -> Prepared:
    """Card timeframe frames (weekly for 1W cards), signals and engine arguments for one market."""
    if card.get("rotasyon"):  # T23: rotation books (stage 2 fills at the next open)
        from backtests import rotasyon_asama2  # noqa: PLC0415 - rotasyon_asama2 imports this module

        return rotasyon_asama2.prepare_rotation(card, data, market, benchmark=benchmark, start=start, end=end, pit_universe=pit_universe)
    week_end = "SUN" if market == "KRIPTO25" else "FRI"
    if card["tf"] in RESAMPLED_HOURLY_TFS:
        data = {symbol: resample_hourly(frame, market=market, timeframe=card["tf"]) for symbol, frame in data.items()}
        if benchmark is not None:
            benchmark = resample_hourly(benchmark, market=market, timeframe=card["tf"])
    weekly_card = card["tf"] == "1W"
    if weekly_card:
        data = {symbol: weekly_frame(frame, week_end) for symbol, frame in data.items()}
        if benchmark is not None:
            benchmark = weekly_frame(benchmark, week_end)
    in_period = {s: f for s, f in data.items() if not f.loc[(f.index >= start) & (f.index <= end)].empty}
    if not in_period:
        raise ValueError(f"{market}: donemde veri yok")
    plan = (
        build_special_plan(card, in_period, week_end=week_end, benchmark=benchmark, market=market)
        if card.get("ozel_kod") else
        build_plan(card, in_period, week_end=week_end, benchmark=benchmark, market=market)
    )
    if pit_universe is not None:
        plan.signals = filter_entry_signals(plan.signals, pit_universe, market)
    if card["tf"] not in DAILY_TFS:
        plan.engine_kwargs["fill_at_close"] = False  # no MOC exception for intraday cards (D4)
        plan.dolum_kapanis = False
    return Prepared(in_period, plan, annualization_for(card["tf"], market), BASE_COST[market], market, start, end)


def run_card_market(
    card: dict[str, Any],
    data: dict[str, pd.DataFrame],
    market: str,
    *,
    benchmark: pd.DataFrame | None = None,
    start: pd.Timestamp = IS_START,
    end: pd.Timestamp = IS_END,
    pit_universe: PITUniverse | None = None,
) -> dict[str, Any]:
    """Run one card on one market's data; returns the metric fields of a tarama row."""
    if card.get("rotasyon"):
        return run_rotation_market(card, data, market, benchmark=benchmark, start=start, end=end, pit_universe=pit_universe)
    prepared = prepare(card, data, market, benchmark=benchmark, start=start, end=end, pit_universe=pit_universe)
    plan, annualization = prepared.plan, prepared.annualization
    out: dict[str, Any] = {}
    first, second = prepared.run(1.0), prepared.run(2.0)
    m1, m2 = _metrics(first, annualization), _metrics(second, annualization)
    out.update(
        islem=m1["islem"], PF_1x=m1["pf"], PF_2x=m2["pf"], net_1x=m1["getiri"], net_2x=m2["getiri"],
        sharpe=m1["sharpe"], mdd=m1["mdd"], maruziyet=m1["maruziyet"],
    )
    if plan.dolum_kapanis:
        variant_b = _metrics(prepared.run(1.0, close_fill=False), annualization)
        out.update(PF_1x_b=variant_b["pf"], net_1x_b=variant_b["getiri"], islem_b=variant_b["islem"])
    out["stop_eklendi"] = plan.stop_eklendi
    out["trades"] = first.trades
    return out


def pit_membership(pit_universe: PITUniverse | None, market: str, symbols: list[str], calendar: pd.DatetimeIndex) -> pd.DataFrame | None:
    """symbol x date membership of the point-in-time index lists; dates without coverage keep every symbol."""
    if pit_universe is None or market not in {"BIST30", "ABD25"}:
        return None
    table = pd.DataFrame(True, index=calendar, columns=symbols)
    cache: dict[Any, frozenset[str] | None] = {}
    for date in calendar:
        key = date.year if market == "ABD25" else date
        members = cache[key] if key in cache else cache.setdefault(key, pit_universe.members(market, date))
        if members is not None:
            table.loc[date] = [symbol in members for symbol in symbols]
    return table


def run_rotation_market(
    card: dict[str, Any],
    data: dict[str, pd.DataFrame],
    market: str,
    *,
    benchmark: pd.DataFrame | None = None,
    start: pd.Timestamp = IS_START,
    end: pd.Timestamp = IS_END,
    pit_universe: PITUniverse | None = None,
) -> dict[str, Any]:
    """Rotation card (``rotasyon:`` block, D12) on one market's universe; same metric fields as ``run_card_market``."""
    week_end = "SUN" if market == "KRIPTO25" else "FRI"
    kind = card["rotasyon"]["kip"]
    if kind != "gecis" and any(spec.get("veri") == "endeks" for spec in card["gostergeler"].values()) and benchmark is None:
        raise EndeksYok(market)
    membership = None
    if kind != "gecis":
        membership = pit_membership(pit_universe, market, list(data), rotasyon._calendar(data))  # noqa: SLF001
    weights = rotasyon.agirliklar(card, data, benchmark=benchmark, week_end=week_end, membership=membership)
    annualization = annualization_for("1D", market)
    close_fill = card.get("dolum") == "kapanis"  # D4: MOC exception, 2x base cost; variant (b) fills at the next open

    def run(multiplier: float, *, close: bool):
        cost = BASE_COST[market] * multiplier * (MOC_COST_FACTOR if close else 1.0)
        return rotasyon.kos(
            card, data, start=start, end=end, cost_rate=cost, benchmark=benchmark, week_end=week_end,
            weights=weights, fill_at_close=close,
        )

    first, second = run(1.0, close=close_fill), run(2.0, close=close_fill)
    m1, m2 = _metrics(first, annualization), _metrics(second, annualization)
    out = {
        "islem": m1["islem"], "PF_1x": m1["pf"], "PF_2x": m2["pf"], "net_1x": m1["getiri"], "net_2x": m2["getiri"],
        "sharpe": m1["sharpe"], "mdd": m1["mdd"], "maruziyet": m1["maruziyet"], "stop_eklendi": False,
        "trades": first.trades,
    }
    if close_fill:
        variant_b = _metrics(run(1.0, close=False), annualization)
        out.update(PF_1x_b=variant_b["pf"], net_1x_b=variant_b["getiri"], islem_b=variant_b["islem"])
    return out


def load_fixed_symbols(symbols: list[str], directory: Path) -> dict[str, pd.DataFrame]:
    """Daily bars of the named instruments of a ``gecis`` card (data/fetch.py --rotasyon)."""
    from data.fetch import normalize_ohlcv  # noqa: PLC0415

    frames, missing = {}, []
    for symbol in symbols:
        path = directory / (symbol.replace("/", "_").replace("=", "_") + ".parquet")
        frame = normalize_ohlcv(pd.read_parquet(path)) if path.exists() else pd.DataFrame()
        if frame.empty:
            missing.append(symbol)
        else:
            frames[symbol] = frame
    if missing:
        raise rotasyon.RotasyonVeriYok("veri_yok", missing)
    return frames


def _stage_decision(row: dict[str, Any]) -> tuple[bool, str]:
    reasons = []
    if not row["islem"] >= MIN_TRADES:
        reasons.append(f"islem<{MIN_TRADES}")
    pf = row["PF_1x"]
    if not (isinstance(pf, float) and (np.isinf(pf) or pf >= MIN_PF)):
        reasons.append(f"PF_1x<{MIN_PF}")
    if not row["net_2x"] > 0:
        reasons.append("net_2x<=0")
    return (not reasons), ",".join(reasons)


def _empty(card: dict[str, Any], market: str, durum: str, neden: str) -> dict[str, Any]:
    return {
        "id": card["id"], "piyasa": market, "tf": card["tf"], "durum": durum, "neden": neden,
        "asama2_aday": False, "kart_yazari": card.get("kart_yazari") or "",
        "piyasa_kisiti": ",".join(card.get("piyasa_kisiti") or []), "dolum": card.get("dolum") or "",
    }


def _load_benchmarks(market_data: dict, directory: Path) -> dict[str, pd.DataFrame | None]:
    benchmarks: dict[str, pd.DataFrame | None] = {}
    for market, symbol in BENCHMARK_SYMBOL.items():
        loaded = market_data[market][0]
        benchmarks[market] = loaded.get(symbol)
        if benchmarks[market] is None:
            path = directory / f"{symbol}.parquet"
            if path.exists():
                from data.fetch import normalize_ohlcv  # noqa: PLC0415
                benchmarks[market] = normalize_ohlcv(pd.read_parquet(path))
    return benchmarks


def _skip_reason(
    card: dict[str, Any], market: str, *, bist_1h_quality_ok: bool = False
) -> tuple[str, str] | None:
    """(durum, neden) when the card cannot be tested in this market, else None."""
    allowed = card.get("piyasa_kisiti")
    if allowed and MARKET_TOKEN[market] not in allowed:
        return "Dogrulanamaz", f"piyasa_ozgu:{','.join(allowed)}"
    if card["tf"] in SUBHOURLY_TFS and market != "KRIPTO25":
        return "Dogrulanamaz", "dakikalik_veri_yok"
    if card["tf"] == "1H" and market == "BIST30" and not bist_1h_quality_ok:
        return "Dogrulanamaz", "veri_kalitesi:BIST_1H_seans_disi_sifir_hacim (results/veri_kalitesi_1h.md)"
    return None


def markets_for_card(card: dict[str, Any]) -> tuple[str, ...]:
    """Preserve all historical rows and append FX8 only for FX-bound cards."""
    return MARKETS + (("FX8",) if "FX" in (card.get("piyasa_kisiti") or []) else ())


def _needs_volume(card: dict[str, Any]) -> bool:
    volume_indicators = {"volume", "obv", "mfi", "vwap", "rvol"}
    if any(spec.get("f") in volume_indicators for spec in (card.get("gostergeler") or {}).values() if isinstance(spec, dict)):
        return True
    return any("volume" in str(card.get(field) or "") for field in ("giris", "cikis"))


def scan(
    cards: list[dict[str, Any]],
    data_dir: Path,
    results_dir: Path,
    *,
    merge: bool = False,
    data_root: Path | None = None,
    summary_name: str | None = None,
    evren: str = "sabit",
) -> pd.DataFrame:
    git_sha = _git_sha()
    pit_universe = load_pit_universe() if evren == "pit" else None
    root = data_root or data_dir.parent
    loaded: dict[tuple[str, str], tuple[dict[str, pd.DataFrame], str, list[str]]] = {}
    benchmark_cache: dict[str, dict[str, pd.DataFrame | None]] = {}

    def directory_for(tf: str) -> Path:
        return data_dir if tf in DAILY_TFS else root / TF_DIR[tf]

    def market_data(tf: str, market: str):
        key = (str(directory_for(tf)), market)
        if key not in loaded:
            result = _load_market(market, directory_for(tf), evren if tf in DAILY_TFS else "sabit")
            if tf == "1H" and market == "BIST30":
                frames, data_hash, missing = result
                result = ({symbol: normalize_market_1h(frame, market) for symbol, frame in frames.items()}, data_hash, missing)
            loaded[key] = result
        return loaded[key]

    rows: list[dict[str, Any]] = []
    trade_dir = results_dir / "tarama_islemler"
    trade_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        if card.get("alias_of"):
            rows.append(_empty(card, "-", "Atlandi", f"alias:{card['alias_of']}"))
            continue
        tf = card["tf"]
        for market in markets_for_card(card):
            skip = _skip_reason(card, market, bist_1h_quality_ok=True)
            if skip:
                rows.append(_empty(card, market, *skip))
                continue
            data, data_hash, _missing = market_data(tf, market)
            if tf == "1H" and market == "BIST30":
                passed, _quality = bist_1h_quality_gate(data)
                if not passed:
                    rows.append(_empty(card, market, *_skip_reason(card, market)))
                    continue
            if (card.get("rotasyon") or {}).get("kip") == "gecis":
                try:
                    data = load_fixed_symbols(rotasyon.needed_symbols(card), directory_for(tf))
                except rotasyon.RotasyonVeriYok as exc:
                    rows.append(_empty(card, market, "Dogrulanamaz", f"{exc.reason}:{','.join(exc.symbols)}"))
                    continue
            if not data:
                rows.append(_empty(card, market, "Dogrulanamaz", "veri_yok"))
                continue
            if _needs_volume(card) and all((frame["volume"] <= 0).all() for frame in data.values()):
                rows.append(_empty(card, market, "Dogrulanamaz", "veri_yok:volume"))
                continue
            directory = str(directory_for(tf))
            if directory not in benchmark_cache:
                benchmark_cache[directory] = _load_benchmarks(
                    {m: market_data(tf, m) for m in BENCHMARK_SYMBOL}, directory_for(tf)
                )
            try:
                start, end = period_for(tf, market, data)
                result = run_card_market(
                    card, data, market, benchmark=benchmark_cache[directory].get(market), start=start, end=end,
                    pit_universe=pit_universe if tf in DAILY_TFS else None,
                )
            except MotorDestegiYok as exc:
                rows.append(_empty(card, market, "Atlandi", f"motor_destegi_yok:{exc.field_name}"))
                continue
            except EndeksYok:
                rows.append(_empty(card, market, "Dogrulanamaz", f"endeks_yok:{market}"))
                continue
            except PipsPiyasaDisi:
                rows.append(_empty(card, market, "Dogrulanamaz", "pips_yalniz_FX8"))
                continue
            except rotasyon.RotasyonVeriYok as exc:
                rows.append(_empty(card, market, "Dogrulanamaz", f"{exc.reason}:{','.join(exc.symbols)}"))
                continue
            except Exception as exc:  # noqa: BLE001 - one broken card must not stop the scan
                rows.append(_empty(card, market, "Hata", f"{type(exc).__name__}: {exc}"[:200]))
                continue
            trades = result.pop("trades")
            row = _empty(card, market, "Hesaplandi", "")
            row.update(result)
            passed, why = _stage_decision(row)
            row["asama2_aday"] = passed
            row["neden"] = why
            row["pf_alarmi"] = bool(isinstance(row["PF_1x"], float) and row["PF_1x"] > PF_ALARM)
            row["data_hash"], row["git_sha"] = data_hash, git_sha
            rows.append(row)
            if not trades.empty:
                trades.to_csv(trade_dir / f"{card['id']}_{market}.csv", index=False)
    table = pd.DataFrame(rows).reindex(columns=OUTPUT_COLUMNS)
    scanned = list(dict.fromkeys(table["id"]))
    results_dir.mkdir(parents=True, exist_ok=True)
    existing = results_dir / "tarama.csv"
    if merge and existing.exists():
        # keep earlier rows of cards that were not rescanned; rescanned cards replace theirs
        previous = pd.read_csv(existing)
        previous = previous[~previous["id"].isin(set(table["id"]))]
        table = pd.concat([previous, table], ignore_index=True).sort_values("id", kind="stable", ignore_index=True)
    table.to_csv(existing, index=False, float_format="%.6g")
    if summary_name is None:
        write_summary(table, list(dict.fromkeys(table["id"])), results_dir / "tarama_ozet.md")
    else:
        write_summary(
            table[table["id"].isin(scanned)], scanned, results_dir / summary_name,
            title="Gun ici / dakikalik tarama ozeti (T12)", gunici=True,
        )
    return table


def card_verdict(rows: pd.DataFrame) -> tuple[str, str]:
    calculated = rows[rows["durum"] == "Hesaplandi"]
    if not calculated.empty:
        passed = calculated[calculated["asama2_aday"] == True]  # noqa: E712
        if not passed.empty:
            return "Asama 2 adayi", ",".join(passed["piyasa"])
        return "Reddedildi (asama 1)", "; ".join(f"{r.piyasa}: {r.neden}" for r in calculated.itertuples())
    reasons = sorted(set(rows["neden"].fillna("")))
    return "Dogrulanamaz", "; ".join(reasons)


def write_summary(
    table: pd.DataFrame, card_ids: list[str], path: Path, *,
    title: str = "Asama 1 tarama ozeti (T5b-1: gunluk/haftalik kartlar)", gunici: bool = False,
) -> None:
    verdicts = {card_id: card_verdict(table[table["id"] == card_id]) for card_id in card_ids}
    count: dict[str, int] = {}
    for verdict, _ in verdicts.values():
        count[verdict] = count.get(verdict, 0) + 1
    lines = [
        f"# {title}", "",
        "Donem: IS 2020-01-01 -> 2024-09-30 (OOS ve 2015-2019 kullanilmadi). Maliyet 1x ve 2x (ELEME_KRITERLERI baz tablosu)."
        if not gunici else
        "Donem: kripto IS 2020-01-01 -> 2024-09-30; BIST/ABD/emtia 1H (yfinance ~2 yil) ilk 2/3 IS, son 1/3 gorulmez. "
        "Maliyet 1x ve 2x (ELEME_KRITERLERI baz tablosu). Gun ici kartlarda kapanis dolumu istisnasi yok.",
        f"Gecis kurali: en az bir piyasada islem >= {MIN_TRADES}, 1x PF >= {MIN_PF}, 2x net > 0.", "",
        f"Kart: {len(card_ids)} | " + " | ".join(f"{k}: {v}" for k, v in sorted(count.items())), "",
        "## Karar tablosu", "", "| Kart | Karar | Ayrinti |", "|---|---|---|",
    ]
    for card_id in card_ids:
        verdict, detail = verdicts[card_id]
        lines.append(f"| {card_id} | {verdict} | {detail} |")
    alarms = table[table["pf_alarmi"] == True]  # noqa: E712
    if not alarms.empty:
        lines += ["", f"## PF > {PF_ALARM:g} alarmi (asiri uyum suphesi)", ""]
        lines += [f"- {r.id} / {r.piyasa}: PF_1x={r.PF_1x:.2f}, islem={int(r.islem)}" for r in alarms.itertuples()]
    moc = table[(table["dolum"] == "kapanis") & (table["durum"] == "Hesaplandi")]
    if not moc.empty:
        lines += ["", "## Kapanis dolumu (MOC) kartlari: (a) kapanis 2x maliyet | (b) ertesi acilis", "",
                  "| Kart | Piyasa | (a) PF_1x | (a) net_1x | (b) PF_1x | (b) net_1x | Not |", "|---|---|---:|---:|---:|---:|---|"]
        for r in moc.itertuples():
            note = "Kosullu (b negatif)" if r.net_1x_b <= 0 else ""
            lines.append(f"| {r.id} | {r.piyasa} | {r.PF_1x:.2f} | {r.net_1x:.2%} | {r.PF_1x_b:.2f} | {r.net_1x_b:.2%} | {note} |")
    skipped = table[table["durum"].isin(["Atlandi", "Dogrulanamaz", "Hata"])]
    if not skipped.empty:
        lines += ["", "## Atlanan / dogrulanamayan satirlar", "", "| Neden | Satir sayisi |", "|---|---:|"]
        for reason, group in skipped.groupby("neden"):
            lines.append(f"| {reason} | {len(group)} |")
    lines += ["", "## Notlar", "",
              "- Evren gunumuzun buyuk sirketleridir (survivorship yanliligi); BIST/ABD sonuclari en fazla Kosullu sayilir.",
              "- BIST30 ve EMTIA icin endeks serisi yok: `endeks_close` kullanan kartlar bu piyasalarda Dogrulanamaz.",
              "- Cikis alan anlamlari: docs/EVRENSEL_KURALLAR.md D5."]
    if gunici:
        lines += ["- 1H altindaki kartlar yalniz kriptoda (Binance) test edilir; diger piyasalar `dakikalik_veri_yok` (Dogrulanamaz).",
                  "- BIST 1H yalnız kalite kapısı (seans dışı=0, fiyatı değişen sıfır hacim <%1/sembol) geçerse hesaplanır; aksi halde `veri_kalitesi` (Dogrulanamaz).",
                  "- Gercek (OOS) sonuclar ve 2018-2019 kripto donemi bu taramada gorulmez."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kartlar", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--tf", default="1D", help="comma separated card timeframes, e.g. 1D,1W,2H,4H")
    parser.add_argument("--kart-ids", default="", help="comma separated card ids (default: all)")
    parser.add_argument("--birlestir", action="store_true", help="merge into the existing results/tarama.csv (rescanned cards replace their rows)")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data", help="root of the hourly/1m/5m/15m/30m archives")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--evren", choices=("sabit", "pit"), default="sabit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cards = load_cards(args.kartlar, args.tf)
    if args.kart_ids:
        wanted = {item.strip() for item in args.kart_ids.split(",") if item.strip()}
        cards = [card for card in cards if card["id"] in wanted]
    intraday = not any(item in DAILY_TFS for item in args.tf.split(","))
    table = scan(
        cards, args.data_dir, args.results_dir, merge=args.birlestir or intraday, data_root=args.veri_kok,
        summary_name="tarama_gunici_ozet.md" if intraday else None, evren=args.evren,
    )
    print(f"{len(cards)} kart, {len(table)} satir, {int((table['durum'] == 'Hesaplandi').sum())} hesaplandi, "
          f"{int(table['asama2_aday'].fillna(False).astype(bool).sum())} satir asama 2 adayi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
