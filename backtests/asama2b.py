#!/usr/bin/env python3
"""T6b: OOS, stress, parameter plateau, block bootstrap and DSR validation.

Card rows are read from ``results/asama2a.csv`` after they pass T6a.  C01-C21
first receive the exact random-entry null test implemented in :mod:`asama2a`.
The program deliberately reports parameter neighbourhoods; it never selects a
best parameter combination or changes the source strategy.
"""

from __future__ import annotations

import argparse
import copy
import itertools
import math
import multiprocessing
import re
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from statistics import NormalDist
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import asama2a, tarama  # noqa: E402
from backtests import rotasyon_asama2 as rot  # noqa: E402
from backtests.run_codex21 import ROWS, RowConfig, _git_sha, _load_market  # noqa: E402
from data.fetch import normalize_ohlcv  # noqa: E402
from data.evren_pit import PITUniverse, filter_entry_signals, load_pit_universe  # noqa: E402
from engine.portfolio import BacktestResult, calculate_metrics, run_portfolio  # noqa: E402

BASE_SEED = asama2a.BASE_SEED
IS_START = pd.Timestamp("2020-01-01", tz="UTC")
IS_END = pd.Timestamp("2024-09-30", tz="UTC")
OOS_START = pd.Timestamp("2024-10-01", tz="UTC")
PRE_END = pd.Timestamp("2019-12-31", tz="UTC")
PLATEAU_FACTORS = (0.6, 0.8, 1.0, 1.2, 1.4)
INTRADAY_PLATEAU_FACTORS = (0.8, 1.0, 1.2)
INTRADAY_TFS = ("1H", "30m", "15m", "5m")
BOOTSTRAP_BLOCK = 20
RISK_BUDGET = 0.15

_CARD_WORK_STATE: dict[str, Any] = {}

OUTPUT_COLUMNS = [
    "id", "piyasa", "kaynak", "para", "null_tekrar", "null_pf_p95", "null_ortr_p95",
    "p_pf", "p_ortr", "null_gecti", "oos_islem", "oos_ort_r", "oos_net",
    "on_islem", "on_ort_r", "on_net", "stres_pf_2x", "stres_net_3x",
    "stres_net_gecikme", "plato_parametreleri", "plato_hucre", "plato_pf_medyan",
    "plato_pozitif_oran", "plato_en_iyi_kenarda", "bootstrap_mdd_p95",
    "bootstrap_cagr_p05", "dsr_n", "dsr_N", "dsr_2N", "dsr_5N", "karar",
    "neden", "evren", "data_hash", "git_sha", "metrik",
]


def max_drawdown(returns: np.ndarray) -> float:
    """Return maximum drawdown as a positive loss fraction."""
    values = np.nan_to_num(np.asarray(returns, dtype=float), nan=0.0)
    equity = np.concatenate(([1.0], np.cumprod(1.0 + values)))
    peaks = np.maximum.accumulate(equity)
    return float(np.max(1.0 - equity / peaks))


def block_bootstrap(
    returns: pd.Series | np.ndarray,
    *,
    repetitions: int = 1000,
    block: int = BOOTSTRAP_BLOCK,
    seed: int = BASE_SEED,
    annualization: int = 252,
) -> dict[str, Any]:
    """Circular fixed-block bootstrap of daily returns."""
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values) or repetitions < 1 or block < 1:
        raise ValueError("bootstrap needs returns, repetitions >= 1 and block >= 1")
    rng = np.random.default_rng(seed)
    blocks_needed = math.ceil(len(values) / block)
    mdds, cagrs = np.empty(repetitions), np.empty(repetitions)
    offsets = np.arange(block)
    for rep in range(repetitions):
        starts = rng.integers(0, len(values), size=blocks_needed)
        sample = values[(starts[:, None] + offsets) % len(values)].ravel()[: len(values)]
        mdds[rep] = max_drawdown(sample)
        terminal = float(np.prod(1.0 + sample))
        cagrs[rep] = terminal ** (annualization / len(sample)) - 1.0 if terminal > 0 else -1.0
    return {
        "mdd": mdds,
        "cagr": cagrs,
        "mdd_p95": float(np.percentile(mdds, 95)),
        "cagr_p05": float(np.percentile(cagrs, 5)),
    }


def probabilistic_sharpe_ratio(
    returns: pd.Series | np.ndarray, benchmark_sharpe: float = 0.0
) -> float:
    """Bailey/Lopez de Prado PSR using non-annualised Sharpe and raw kurtosis."""
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 3 or np.std(values, ddof=1) <= 0:
        return float("nan")
    centered = values - values.mean()
    sigma = np.std(values, ddof=1)
    sr = float(values.mean() / sigma)
    skew = float(np.mean(centered**3) / np.mean(centered**2) ** 1.5)
    kurtosis = float(np.mean(centered**4) / np.mean(centered**2) ** 2)
    variance_term = max(1.0 - skew * sr + (kurtosis - 1.0) * sr * sr / 4.0, 1e-15)
    z_score = (sr - benchmark_sharpe) * math.sqrt(len(values) - 1) / math.sqrt(variance_term)
    return NormalDist().cdf(z_score)


def deflated_sharpe_ratio(returns: pd.Series | np.ndarray, trials: int) -> float:
    """DSR probability after deflating for the expected maximum of ``trials`` tests."""
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]
    if trials <= 1:
        return probabilistic_sharpe_ratio(values, 0.0)
    if len(values) < 3 or np.std(values, ddof=1) <= 0:
        return float("nan")
    sr = float(values.mean() / np.std(values, ddof=1))
    centered = values - values.mean()
    skew = float(np.mean(centered**3) / np.mean(centered**2) ** 1.5)
    kurtosis = float(np.mean(centered**4) / np.mean(centered**2) ** 2)
    sr_std = math.sqrt(max(1.0 - skew * sr + (kurtosis - 1.0) * sr * sr / 4.0, 0.0) / (len(values) - 1))
    gamma = 0.5772156649015329
    normal = NormalDist()
    expected_max = (1 - gamma) * normal.inv_cdf(1 - 1 / trials) + gamma * normal.inv_cdf(1 - 1 / (trials * math.e))
    return probabilistic_sharpe_ratio(values, sr_std * expected_max)


def plateau_summary(
    cells: list[tuple[tuple[float, ...], float, float]],
    factors: tuple[float, ...] = PLATEAU_FACTORS,
) -> dict[str, Any]:
    """Summarise (factor tuple, PF, net return) cells without choosing parameters."""
    if not cells:
        raise ValueError("plateau requires at least one cell")
    pfs = np.asarray([cell[1] for cell in cells], dtype=float)
    nets = np.asarray([cell[2] for cell in cells], dtype=float)
    finite = np.isfinite(pfs)
    best = int(np.nanargmax(pfs)) if finite.any() else 0
    best_factors = cells[best][0]
    return {
        "cells": len(cells),
        "median_pf": float(np.nanmedian(pfs)),
        "positive_rate": float(np.mean(nets > 0)),
        "best_on_edge": any(factor in (factors[0], factors[-1]) for factor in best_factors),
    }


def _plateau_factor_cells(parameter_count: int, intraday: bool) -> list[tuple[float, ...]]:
    """Daily keeps its Cartesian grid; intraday varies every parameter ±20% one at a time."""
    if parameter_count == 0:
        return []
    if not intraday:
        return list(itertools.product(PLATEAU_FACTORS, repeat=parameter_count))
    center = (1.0,) * parameter_count
    cells = [center]
    for position in range(parameter_count):
        for factor in (0.8, 1.2):
            cell = list(center)
            cell[position] = factor
            cells.append(tuple(cell))
    return cells


def _numeric_parameter_paths(card: dict[str, Any], limit: int | None = 2) -> list[tuple[tuple[str, ...], float]]:
    """Source parameters (optionally limited): ``parametreler``, else indicator n/multiplier."""
    found: list[tuple[tuple[str, ...], float]] = []
    params = card.get("parametreler") or {}
    for key, value in params.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
            found.append((("parametreler", str(key)), float(value)))
    if not found:
        for indicator, spec in (card.get("gostergeler") or {}).items():
            if not isinstance(spec, dict):
                continue
            for key in ("n", "carpan"):
                value = spec.get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
                    found.append((("gostergeler", str(indicator), key), float(value)))
    return found if limit is None else found[:limit]


def _mutate_card(card: dict[str, Any], parameters: list[tuple[tuple[str, ...], float]], factors: tuple[float, ...]) -> dict[str, Any]:
    changed = copy.deepcopy(card)
    for (path, center), factor in zip(parameters, factors, strict=True):
        node: dict[str, Any] = changed
        for key in path[:-1]:
            node = node[key]
        original = node[path[-1]]
        value = center * factor
        replacement = max(1, int(round(value))) if isinstance(original, int) else value
        node[path[-1]] = replacement
        # ``parametreler`` is source metadata in the cards; build_plan executes
        # ``gostergeler`` and expression strings.  Mirror an explicit dotted
        # name first, otherwise every indicator scalar carrying the same source
        # value.  Numeric literals in entry/exit expressions are mirrored too.
        if path[0] == "parametreler":
            name = path[-1]
            if "." in name:
                indicator, field = name.rsplit(".", 1)
                spec = (changed.get("gostergeler") or {}).get(indicator)
                if isinstance(spec, dict) and field in spec:
                    spec[field] = replacement
            else:
                for spec in (changed.get("gostergeler") or {}).values():
                    if isinstance(spec, dict):
                        for field in ("n", "carpan", "yuzde", "fast", "slow", "signal"):
                            if field in spec and isinstance(spec[field], (int, float)) and float(spec[field]) == center:
                                spec[field] = replacement
                if name in ("hold_hours", "hold_bars") and isinstance(changed.get("zaman_stop"), dict):
                    if float(changed["zaman_stop"].get("bar", -1)) == center:
                        changed["zaman_stop"]["bar"] = replacement
            pattern = re.compile(rf"(?<![\w.]){re.escape(format(center, 'g'))}(?![\w.])")
            for field in ("giris", "cikis"):
                if isinstance(changed.get(field), str):
                    changed[field] = pattern.sub(format(float(replacement), "g"), changed[field])
            for spec in (changed.get("gostergeler") or {}).values():
                if isinstance(spec, dict) and isinstance(spec.get("ifade"), str):
                    spec["ifade"] = pattern.sub(format(float(replacement), "g"), spec["ifade"])
    return changed


@dataclass
class CodexPrepared:
    """Small adapter that makes C01-C21 compatible with asama2a.null_distribution."""

    config: RowConfig
    frames: dict[str, pd.DataFrame]
    start: pd.Timestamp
    end: pd.Timestamp
    plan: Any
    annualization: int
    runtime_cache: dict[str, Any] = field(default_factory=dict)

    def run(
        self,
        multiplier: float = 1.0,
        *,
        signals: dict[str, pd.DataFrame] | None = None,
        extra_delay_bars: int = 0,
        signal_params: dict[str, float] | None = None,
        trusted_inputs: bool = False,
        trades_only: bool = False,
        **engine_extra: Any,
    ) -> BacktestResult:
        computed = (
            {symbol: self.config.signal_function(frame, self.config.market, **signal_params)
             for symbol, frame in self.frames.items()}
            if signals is None and signal_params is not None else self.plan.signals
        )
        return run_portfolio(
            self.frames,
            self.config.signal_function,
            market=self.config.market,
            start=self.start,
            end=self.end,
            cost_rate=self.config.cost * multiplier,
            extra_delay_bars=extra_delay_bars,
            time_stop_bars=self.config.time_stop_bars,
            precomputed_signals=signals if signals is not None else computed,
            trusted_inputs=trusted_inputs,
            trades_only=trades_only,
            runtime_cache=self.runtime_cache if trusted_inputs else None,
            **engine_extra,
        )


def prepare_codex(config: RowConfig, data: dict[str, pd.DataFrame], start: pd.Timestamp, end: pd.Timestamp, pit_universe: PITUniverse | None = None) -> CodexPrepared:
    frames = {symbol: frame for symbol, frame in data.items() if not frame.loc[(frame.index >= start) & (frame.index <= end)].empty}
    if not frames:
        raise ValueError(f"{config.market}: donemde veri yok")
    signals = {symbol: config.signal_function(frame, config.market) for symbol, frame in frames.items()}
    if pit_universe is not None:
        signals = filter_entry_signals(signals, pit_universe, config.market)
    annualization = 365 if config.market == "KRIPTO25" else 252
    return CodexPrepared(config, frames, start, end, SimpleNamespace(signals=signals), annualization)


def trial_count(card: dict[str, Any] | None, results_dir: Path, *, intraday: bool = False) -> int:
    source = (card or {}).get("deneme_sayisi_kaynakta") or 1
    if not (results_dir / "tarama.csv").exists():
        scan_rows = 0
    else:
        scan = pd.read_csv(results_dir / "tarama.csv")
        scan_rows = int(scan["tf"].astype(str).isin(INTRADAY_TFS).sum()) if intraday and "tf" in scan else len(scan)
    if intraday:
        return max(1, scan_rows)
    return max(1, int(source) + scan_rows + len(ROWS))


def decide(row: dict[str, Any]) -> tuple[str, str]:
    """Paper-trading gate order from ELEME_KRITERLERI and GOREV_T6."""
    rejected = []
    conditional = []
    if not row.get("null_gecti", False):
        rejected.append("null")
    if row.get("oos_islem", 0) >= 30 and not row.get("oos_ort_r", float("nan")) > 0:
        rejected.append("OOS ortR<=0")
    if not row.get("stres_pf_2x", float("nan")) >= 1.2:
        rejected.append("2x PF<1.2")
    if not row.get("stres_net_3x", float("nan")) > 0:
        rejected.append("3x net<=0")
    if not row.get("stres_net_gecikme", float("nan")) > 0:
        rejected.append("+1 bar net<=0")
    if not row.get("plato_pozitif_oran", float("nan")) >= 0.60:
        rejected.append("plato<%60")
    if not row.get("bootstrap_mdd_p95", float("nan")) <= RISK_BUDGET:
        rejected.append("bootstrap MDD>%15")
    if row.get("on_islem", 0) and not row.get("on_ort_r", float("nan")) > 0:
        conditional.append("on donem negatif")
    if row.get("oos_islem", 0) < 30:
        conditional.append("OOS ornek<30")
    if row.get("_intraday_no_pre", False):
        conditional.append("on donem yok")
    if row.get("piyasa") == "BIST30" and row.get("evren") == "pit":
        conditional.append("survivorship: 2015-2019 PIT evren yok")  # T11: BIST30 lists only from 2020
    elif row.get("piyasa") in ("BIST30", "ABD25") and row.get("evren") not in ("pit", "enstruman"):  # named ETFs have no universe
        conditional.append("survivorship yanliligi")
    if row.get("on_veri_yok"):
        conditional.append("on donem Dogrulanamaz (veri yok)")
    if rejected:
        return "Reddedildi", ", ".join(rejected)
    if conditional:
        return "Kosullu", ", ".join(conditional)
    return "Gecti", "paper kapilari gecti; DSR canli oncesi degerlendirilmeli"


def _metrics(result: BacktestResult, annualization: int) -> dict[str, Any]:
    return calculate_metrics(result, annualization=annualization)


def _validation_returns(result: BacktestResult, daily_equity: bool = False) -> pd.Series:
    """Returns used by bootstrap/DSR; intraday equity is reduced to one close per UTC day."""
    equity = result.equity.resample("1D").last().dropna() if daily_equity else result.equity
    return equity.pct_change().dropna()


def _bootstrap_and_dsr(
    result: BacktestResult,
    annualization: int,
    n: int,
    repetitions: int,
    seed: int,
    *,
    daily_equity: bool = False,
) -> dict[str, float]:
    returns = _validation_returns(result, daily_equity)
    boot = block_bootstrap(returns, repetitions=repetitions, seed=seed, annualization=annualization)
    return {
        "bootstrap_mdd_p95": boot["mdd_p95"],
        "bootstrap_cagr_p05": boot["cagr_p05"],
        "dsr_n": n,
        "dsr_N": deflated_sharpe_ratio(returns, n),
        "dsr_2N": deflated_sharpe_ratio(returns, 2 * n),
        "dsr_5N": deflated_sharpe_ratio(returns, 5 * n),
    }


def evaluate_codex(
    config: RowConfig,
    data: dict[str, pd.DataFrame],
    *,
    results_dir: Path,
    null_reps: int,
    null_reps_high: int,
    bootstrap_reps: int,
    data_hash: str,
    pit_universe: PITUniverse | None = None,
) -> dict[str, Any]:
    row = {column: np.nan for column in OUTPUT_COLUMNS}
    row.update(id=config.row_id, piyasa=config.market, kaynak="Codex Algo", para="USD" if config.market == "BIST30" else "yerel", data_hash=data_hash, git_sha=_git_sha())
    seed = BASE_SEED ^ zlib.crc32(f"{config.row_id}|{config.market}".encode())
    prepared = prepare_codex(config, data, IS_START, IS_END, pit_universe)
    real = prepared.run()
    real_pf, real_ortr, real_count = asama2a.trade_stats(real.trades)
    if real_count < 5:
        row.update(null_gecti=False, karar="Reddedildi", neden="null testi icin islem yok/az")
        return row
    null = asama2a.null_distribution(prepared, real.trades, null_reps, seed)
    p_pf, p_ortr = asama2a.p_value(real_pf, null["pf"]), asama2a.p_value(real_ortr, null["ortr"])
    reps = null_reps
    if asama2a.BORDERLINE_P[0] <= max(p_pf, p_ortr) <= asama2a.BORDERLINE_P[1]:
        reps = null_reps_high
        null = asama2a.null_distribution(prepared, real.trades, reps, seed + 1)
        p_pf, p_ortr = asama2a.p_value(real_pf, null["pf"]), asama2a.p_value(real_ortr, null["ortr"])
    pf95 = float(np.nanpercentile(null["pf"], 95))
    ortr95 = float(np.nanpercentile(null["ortr"], 95))
    row.update(null_tekrar=reps, null_pf_p95=pf95, null_ortr_p95=ortr95, p_pf=p_pf, p_ortr=p_ortr, null_gecti=bool(real_pf > pf95 and real_ortr > ortr95))

    oos = prepare_codex(config, data, OOS_START, max(frame.index.max() for frame in data.values()), pit_universe).run()
    pre_start = pd.Timestamp("2018-01-01" if config.market == "KRIPTO25" else "2015-01-01", tz="UTC")
    pre = prepare_codex(config, data, pre_start, PRE_END, pit_universe).run()
    oos_m, pre_m = _metrics(oos, prepared.annualization), _metrics(pre, prepared.annualization)
    two, three, delay = prepared.run(2), prepared.run(3), prepared.run(extra_delay_bars=1)
    row.update(
        oos_islem=oos_m["islem"], oos_ort_r=oos_m["ortalama_r"], oos_net=oos_m["getiri"],
        on_islem=pre_m["islem"], on_ort_r=pre_m["ortalama_r"], on_net=pre_m["getiri"],
        stres_pf_2x=_metrics(two, prepared.annualization)["pf"],
        stres_net_3x=_metrics(three, prepared.annualization)["getiri"],
        stres_net_gecikme=_metrics(delay, prepared.annualization)["getiri"],
    )
    cells = []
    for factors in itertools.product(PLATEAU_FACTORS, repeat=len(config.plato_parametreleri)):
        signal_params = {
            name: max(1, int(round(center * factor)))
            for (name, center), factor in zip(config.plato_parametreleri, factors, strict=True)
        }
        result = prepared.run(signal_params=signal_params)
        metrics = _metrics(result, prepared.annualization)
        cells.append((factors, metrics["pf"], metrics["getiri"]))
    plateau = plateau_summary(cells)
    row.update(
        plato_parametreleri=",".join(name for name, _ in config.plato_parametreleri), plato_hucre=plateau["cells"],
        plato_pf_medyan=plateau["median_pf"], plato_pozitif_oran=plateau["positive_rate"],
        plato_en_iyi_kenarda=plateau["best_on_edge"],
        **_bootstrap_and_dsr(real, prepared.annualization, trial_count(None, results_dir), bootstrap_reps, seed),
    )
    row["evren"] = "pit" if pit_universe is not None else "sabit"
    row["karar"], row["neden"] = decide(row)
    return row


def _card_stage2_worker(job: tuple[str, Any]) -> tuple[str, Any, dict[str, Any]]:
    """Run one stress/plateau cell from fork-shared card data."""
    kind, value = job
    prepared: tarama.Prepared = _CARD_WORK_STATE["prepared"]
    if kind == "stress":
        multiplier, delay = value
        result = prepared.run(multiplier, extra_delay_bars=delay)
    else:
        factors = value
        variant = _mutate_card(_CARD_WORK_STATE["card"], _CARD_WORK_STATE["parameters"], factors)
        result = tarama.prepare(
            variant,
            _CARD_WORK_STATE["data"],
            _CARD_WORK_STATE["market"],
            benchmark=_CARD_WORK_STATE["benchmark"],
            start=IS_START,
            end=IS_END,
            pit_universe=_CARD_WORK_STATE["pit_universe"],
        ).run()
    return kind, value, _metrics(result, prepared.annualization)


def evaluate_card(
    card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], benchmark: pd.DataFrame | None,
    stage2a_row: pd.Series, *, results_dir: Path, bootstrap_reps: int, data_hash: str,
    pit_universe: PITUniverse | None = None, workers: int = 1,
) -> dict[str, Any]:
    row = {column: np.nan for column in OUTPUT_COLUMNS}
    row.update(
        id=card["id"], piyasa=market, kaynak="strateji karti", para="USD" if market == "BIST30" else "yerel",
        null_tekrar=stage2a_row.get("null_tekrar"), null_pf_p95=stage2a_row.get("null_pf_p95"),
        null_ortr_p95=stage2a_row.get("null_ortr_p95"), p_pf=stage2a_row.get("p_pf"),
        p_ortr=stage2a_row.get("p_ortr"), null_gecti=True, data_hash=data_hash, git_sha=_git_sha(),
    )
    row["metrik"] = "PF+ortR"
    tf = card["tf"]
    intraday = tf in INTRADAY_TFS
    seed = BASE_SEED ^ zlib.crc32(f"{card['id']}|{market}".encode())
    prepared = tarama.prepare(card, data, market, benchmark=benchmark, start=IS_START, end=IS_END, pit_universe=pit_universe)
    if isinstance(prepared, rot.RotationPrepared):
        return evaluate_rotation_card(card, market, data, benchmark, prepared, row, results_dir=results_dir, bootstrap_reps=bootstrap_reps, seed=seed, pit_universe=pit_universe)
    real = prepared.run()
    final = max(frame.index.max() for frame in data.values())
    oos = tarama.prepare(card, data, market, benchmark=benchmark, start=OOS_START, end=final, pit_universe=pit_universe).run()
    pre = None
    if intraday and market != "KRIPTO25":
        row["_intraday_no_pre"] = True
    else:
        pre_start = pd.Timestamp(
            "2017-01-01" if intraday and market == "KRIPTO25" else
            "2018-01-01" if market == "KRIPTO25" else "2015-01-01",
            tz="UTC",
        )
        try:
            pre = tarama.prepare(
                card, data, market, benchmark=benchmark, start=pre_start, end=PRE_END,
                pit_universe=pit_universe,
            ).run()
        except ValueError as exc:
            if intraday and market == "KRIPTO25" and "donemde veri yok" in str(exc):
                row.update(karar="Dogrulanamaz", neden="on donem verisi yok (2017-2019)")
                return row
            raise
    oos_m = _metrics(oos, prepared.annualization)
    pre_m = _metrics(pre, prepared.annualization) if pre is not None else {"islem": 0, "ortalama_r": np.nan, "getiri": np.nan}
    row.update(
        oos_islem=oos_m["islem"], oos_ort_r=oos_m["ortalama_r"], oos_net=oos_m["getiri"],
        on_islem=pre_m["islem"], on_ort_r=pre_m["ortalama_r"], on_net=pre_m["getiri"],
    )

    factors_grid = INTRADAY_PLATEAU_FACTORS if intraday else PLATEAU_FACTORS
    parameters = _numeric_parameter_paths(card, limit=None if intraday else 2)
    plateau_jobs = _plateau_factor_cells(len(parameters), intraday)
    jobs: list[tuple[str, Any]] = [
        ("stress", (2.0, 0)), ("stress", (3.0, 0)), ("stress", (1.0, 1)),
        *(("plateau", factors) for factors in plateau_jobs),
    ]
    _CARD_WORK_STATE.update(
        prepared=prepared, card=card, parameters=parameters, data=data, market=market,
        benchmark=benchmark, pit_universe=pit_universe,
    )
    parallel_workers = workers if intraday else 1  # daily execution order/output is a locked regression
    if parallel_workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(
            max_workers=min(parallel_workers, len(jobs)), mp_context=multiprocessing.get_context("fork")
        ) as pool:
            completed = list(pool.map(_card_stage2_worker, jobs))
    else:
        completed = [_card_stage2_worker(job) for job in jobs]
    stress = {value: metrics for kind, value, metrics in completed if kind == "stress"}
    row.update(
        stres_pf_2x=stress[(2.0, 0)]["pf"], stres_net_3x=stress[(3.0, 0)]["getiri"],
        stres_net_gecikme=stress[(1.0, 1)]["getiri"],
    )
    if parameters:
        cells = [(value, metrics["pf"], metrics["getiri"]) for kind, value, metrics in completed if kind == "plateau"]
        plateau = plateau_summary(cells, factors_grid)
        row.update(
            plato_parametreleri=",".join(".".join(path) for path, _ in parameters), plato_hucre=plateau["cells"],
            plato_pf_medyan=plateau["median_pf"], plato_pozitif_oran=plateau["positive_rate"],
            plato_en_iyi_kenarda=plateau["best_on_edge"],
        )
    else:
        row.update(plato_parametreleri="parametre_yok", plato_hucre=1, plato_pf_medyan=_metrics(real, prepared.annualization)["pf"], plato_pozitif_oran=float(_metrics(real, prepared.annualization)["getiri"] > 0), plato_en_iyi_kenarda=False)
    daily_annualization = 365 if market == "KRIPTO25" else 252
    row.update(**_bootstrap_and_dsr(
        real, daily_annualization if intraday else prepared.annualization,
        trial_count(card, results_dir, intraday=intraday), bootstrap_reps, seed,
        daily_equity=intraday,
    ))
    row["evren"] = "pit" if pit_universe is not None else "sabit"
    row["karar"], row["neden"] = decide(row)
    return row


def evaluate_rotation_card(
    card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], benchmark: pd.DataFrame | None, prepared: rot.RotationPrepared,
    row: dict[str, Any], *, results_dir: Path, bootstrap_reps: int, seed: int, pit_universe: PITUniverse | None,
) -> dict[str, Any]:
    """Rotation card (T23, ``metrik: PF+CAGR``): the same gates as ``evaluate_card``.

    There is no per-trade R, so the ``oos_ort_r`` / ``on_ort_r`` columns carry the period CAGR (sign gate). Stress runs fill at the
    next open (+1 bar delay = one more bar); the plateau moves every numeric parameter of the ``rotasyon:`` block alone by +-20 %
    and counts the share of cells with PF > 1 and a positive return."""
    row["metrik"] = rot.METRIC
    row["evren"] = "enstruman" if card["rotasyon"]["kip"] == "gecis" else ("pit" if pit_universe is not None else "sabit")
    ann = prepared.annualization
    real = prepared.run()
    pre_start = pd.Timestamp("2018-01-01" if market == "KRIPTO25" else "2015-01-01", tz="UTC")
    final = max(frame.index.max() for frame in (prepared.frames or data).values())
    oos = tarama.prepare(card, data, market, benchmark=benchmark, start=OOS_START, end=final, pit_universe=pit_universe).run()
    oos_m = _metrics(oos, ann)
    row.update(oos_islem=oos_m["islem"], oos_ort_r=oos_m["cagr"], oos_net=oos_m["getiri"])
    try:
        pre_m = _metrics(tarama.prepare(card, data, market, benchmark=benchmark, start=pre_start, end=PRE_END, pit_universe=pit_universe).run(), ann)
        row.update(on_islem=pre_m["islem"], on_ort_r=pre_m["cagr"], on_net=pre_m["getiri"])
    except (rot.rotasyon.RotasyonVeriYok, ValueError):
        row.update(on_islem=0, on_veri_yok=True)  # no 2015-2019 data for a needed instrument / the whole universe
    row.update(
        stres_pf_2x=_metrics(prepared.run(2), ann)["pf"], stres_net_3x=_metrics(prepared.run(3), ann)["getiri"],
        stres_net_gecikme=_metrics(prepared.run(extra_delay_bars=1), ann)["getiri"],
    )
    cells = rot.plateau_cells(prepared, data, benchmark, pit_universe)
    pfs = np.array([c[2] for c in cells], dtype=float)
    nets = np.array([c[3] for c in cells], dtype=float)
    row.update(
        plato_parametreleri=f"{len(cells) - 1} varyant (+-%20 tek tek)", plato_hucre=len(cells),
        plato_pf_medyan=float(np.nanmedian(pfs)), plato_pozitif_oran=float(np.mean((pfs > 1.0) & (nets > 0))),
        plato_en_iyi_kenarda=False,
    )
    row.update(**_bootstrap_and_dsr(real, ann, trial_count(card, results_dir), bootstrap_reps, seed))
    row["karar"], row["neden"] = decide(row)
    return row


def load_card_candidates(
    results_dir: Path,
    card_dir: Path,
    only: set[str] | None,
    timeframes: set[str] | None = None,
) -> list[tuple[dict[str, Any], str, pd.Series]]:
    path = results_dir / "asama2a.csv"
    if not path.exists():
        return []
    table = pd.read_csv(path)
    table = table[table["karar"] == "Gecti (null)"]
    cards = {card["id"]: card for card in (yaml.safe_load(path.read_text(encoding="utf-8")) for path in card_dir.glob("*.yaml"))}
    return [
        (cards[row.id], row.piyasa, pd.Series(row._asdict()))
        for row in table.itertuples()
        if row.id in cards
        and (not only or row.id in only)
        and (timeframes is None or str(row.tf) in timeframes)
        and cards[row.id].get("tf") == str(row.tf)
    ]


def merge_selected_results(existing: pd.DataFrame, fresh: pd.DataFrame, selected_ids: set[str]) -> pd.DataFrame:
    """Replace selected card/Codex rows while leaving unselected daily/PIT results untouched."""
    if existing.empty:
        return fresh
    kept = existing[~existing["id"].astype(str).isin(selected_ids)]
    return pd.concat([kept, fresh], ignore_index=True).reindex(columns=OUTPUT_COLUMNS)


def write_outputs(table: pd.DataFrame, results_dir: Path, card_input_missing: bool) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    table.reindex(columns=OUTPUT_COLUMNS).to_csv(results_dir / "asama2b.csv", index=False, float_format="%.6g")
    counts = table["karar"].value_counts().to_dict() if not table.empty else {}
    lines = [
        "# Asama 2b tam dogrulama (T6b/T24)", "",
        "OOS, on donem, 2x/3x/+1 bar stres, kaynak merkezli parametre platosu, 20 gunluk block bootstrap ve DSR birlikte raporlanir.",
        "DSR paper trading icin bilgi; canliya geciste kotumser (5N) deger icin 0,95 kapisi uygulanir.", "",
        f"Satir: {len(table)} | " + " | ".join(f"{key}: {value}" for key, value in sorted(counts.items())), "",
    ]
    if card_input_missing:
        lines += ["> `results/asama2a.csv` henuz yok; bu kosuda yalniz C01-C21 degerlendirildi. Kart satirlari T6a lider kosusundan sonra otomatik eklenir.", ""]
    lines += ["| ID | Piyasa | OOS islem/ortR | 2x PF | 3x net | +1 net | Plato + | Boot MDD95 | DSR 5N | Karar | Gerekce |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    def f(value: Any, fmt: str) -> str:
        return "-" if pd.isna(value) else format(float(value), fmt)
    for item in table.itertuples():
        lines.append(
            f"| {item.id} | {item.piyasa} | {f(item.oos_islem, '.0f')}/{f(item.oos_ort_r, '.3f')} | "
            f"{f(item.stres_pf_2x, '.2f')} | {f(item.stres_net_3x, '.1%')} | {f(item.stres_net_gecikme, '.1%')} | "
            f"{f(item.plato_pozitif_oran, '.0%')} | {f(item.bootstrap_mdd_p95, '.1%')} | {f(item.dsr_5N, '.3f')} | {item.karar} | {item.neden} |"
        )
    lines += ["", "## Yontem notlari", "",
              "- Rotasyon kartlari (T23, `metrik: PF+CAGR`): ortR yerine CAGR; `oos_ort_r`/`on_ort_r` sutunlari donem CAGR'i tasir. Asama 2'de dolum ertesi acilistir (Composer kartlarinin kapanis dolumu yalniz Asama 1 bilgisidir). "
              "Plato: `rotasyon:` blogu ve kullandigi gostergelerin her sayisal parametresi (pencere, esik, N) tek tek +-%20; hucre = PF>1 ve getiri>0. `evren: enstruman` = adli ETF'ler (survivorship notu yok).", "- BIST fiyatlari USDTRY ile ayni gun USD'ye cevrilir.",
              "- Plato merkezleri kaynak sinyal degerleridir; en iyi hucre secilmez ve stratejiye geri yazilmaz.",
              "- DSR N = kaynak denemesi (yoksa 1) + tarama.csv satirlari + 21 Codex satiri.",
              "- Gun ici platoda her sayisal parametre merkez etrafinda tek tek -%20/+%20 denenir; stres ve plato `--isci` ile paraleldir.",
              "- Gun ici bootstrap/DSR oncesinde ozkaynak UTC gun sonu degerlerine indirgenir; block uzunlugu 20 gundur. Gun ici DSR N tum gun ici kart-piyasa-tf tarama satirlarini kapsar.",
              "- DSR'da denemeler arasi SR varyansi bilinmedigi icin stratejinin kendi SR standart hatasi kullanildi (yaklasim).",
              "- BIST/ABD guncel evrenleri survivorship yanliligi nedeniyle en fazla `Kosullu` olabilir; `--evren pit` (T11) ile ABD tam, BIST 2020 sonrasi duzeltilir."]
    (results_dir / "asama2b_ozet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kartlar", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data", help="hourly/30m/15m/5m archive root")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tf", default="1D,1W", help="comma separated timeframes: 1D,1W,1H,30m,15m,5m")
    parser.add_argument("--null-tekrar", type=int, default=500)
    parser.add_argument("--null-tekrar-yuksek", type=int, default=1000)
    parser.add_argument("--bootstrap-tekrar", type=int, default=1000)
    parser.add_argument("--kart-ids", default="")
    parser.add_argument("--codex-ids", default=",".join(ROWS))
    parser.add_argument("--evren", choices=("sabit", "pit"), default="sabit")
    parser.add_argument("--isci", type=int, default=0, help="stress/plateau worker processes (0 = CPU count)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tarama.FIXED_DATA_DIR = args.data_dir
    timeframes = {value.strip() for value in args.tf.split(",") if value.strip()}
    supported = set(tarama.DAILY_TFS) | set(INTRADAY_TFS)
    invalid = timeframes.difference(supported)
    if invalid:
        raise SystemExit(f"desteklenmeyen tf: {','.join(sorted(invalid))}")
    only_cards = {value.strip() for value in args.kart_ids.split(",") if value.strip()} or None
    codex_ids = [value.strip() for value in args.codex_ids.split(",") if value.strip()]
    if not timeframes.intersection(tarama.DAILY_TFS):
        codex_ids = []
    unknown = set(codex_ids).difference(ROWS)
    if unknown:
        raise SystemExit(f"bilinmeyen Codex satiri: {sorted(unknown)}")
    card_input_missing = not (args.results_dir / "asama2a.csv").exists()
    cards = load_card_candidates(args.results_dir, args.kartlar, only_cards, timeframes)
    keys = {("1D", ROWS[row_id].market) for row_id in codex_ids} | {
        (card["tf"], market) for card, market, _ in cards
    }
    data, hashes, benchmarks = {}, {}, {}
    pit_universe = load_pit_universe() if args.evren == "pit" else None
    for tf, market in sorted(keys):
        directory = args.data_dir if tf in tarama.DAILY_TFS else args.veri_kok / tarama.TF_DIR[tf]
        data[(tf, market)], hashes[(tf, market)], _ = _load_market(
            market, directory, args.evren if tf in tarama.DAILY_TFS else "sabit"
        )
    if any(tf in tarama.DAILY_TFS and market == "BIST30" for tf, market in keys):
        fx_path = args.data_dir / "USDTRY_X.parquet"
        if not fx_path.exists():
            raise SystemExit(f"{fx_path} yok: BIST T6b USD fiyat gerektirir")
        rate = normalize_ohlcv(pd.read_parquet(fx_path))
        for tf, market in keys:
            if tf in tarama.DAILY_TFS and market == "BIST30":
                data[(tf, market)] = asama2a.usd_frames(data[(tf, market)], rate)
    for tf, market in keys:
        symbol = tarama.BENCHMARK_SYMBOL.get(market)
        if symbol:
            directory = args.data_dir if tf in tarama.DAILY_TFS else args.veri_kok / tarama.TF_DIR[tf]
            benchmarks[(tf, market)] = data[(tf, market)].get(symbol)
            if benchmarks[(tf, market)] is None and (directory / f"{symbol}.parquet").exists():
                benchmarks[(tf, market)] = normalize_ohlcv(pd.read_parquet(directory / f"{symbol}.parquet"))
    rows: list[dict[str, Any]] = []
    tasks: list[tuple[str, Callable[[], dict[str, Any]]]] = []
    for row_id in codex_ids:
        config = ROWS[row_id]
        key = ("1D", config.market)
        tasks.append((row_id, lambda config=config, key=key: evaluate_codex(config, data[key], results_dir=args.results_dir, null_reps=args.null_tekrar, null_reps_high=args.null_tekrar_yuksek, bootstrap_reps=args.bootstrap_tekrar, data_hash=hashes[key], pit_universe=pit_universe)))
    workers = args.isci or multiprocessing.cpu_count()
    for card, market, stage2a_row in cards:
        key = (card["tf"], market)
        card_pit = pit_universe if card["tf"] in tarama.DAILY_TFS else None
        tasks.append((card["id"], lambda card=card, market=market, stage2a_row=stage2a_row, key=key, card_pit=card_pit: evaluate_card(card, market, data[key], benchmarks.get(key), stage2a_row, results_dir=args.results_dir, bootstrap_reps=args.bootstrap_tekrar, data_hash=hashes[key], pit_universe=card_pit, workers=workers)))
    for number, (name, task) in enumerate(tasks, 1):
        try:
            row = task()
        except Exception as exc:  # one bad strategy must not abort a six-hour workflow
            row = {column: np.nan for column in OUTPUT_COLUMNS}
            row.update(id=name, karar="Reddedildi", neden=f"{type(exc).__name__}: {exc}"[:240], git_sha=_git_sha())
        rows.append(row)
        print(f"[{number}/{len(tasks)}] {name}: {row['karar']}", flush=True)
    table = pd.DataFrame(rows).reindex(columns=OUTPUT_COLUMNS)
    selected_ids = set(codex_ids)
    for path in args.kartlar.glob("*.yaml"):
        candidate = yaml.safe_load(path.read_text(encoding="utf-8"))
        if candidate.get("tf") in timeframes and (only_cards is None or candidate["id"] in only_cards):  # --kart-ids keeps the other rows
            selected_ids.add(candidate["id"])
    output_path = args.results_dir / "asama2b.csv"
    if output_path.exists():
        table = merge_selected_results(pd.read_csv(output_path), table, selected_ids)
    write_outputs(table, args.results_dir, card_input_missing)
    print(f"{len(table)} satir: " + ", ".join(f"{key}={value}" for key, value in table["karar"].value_counts().items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
