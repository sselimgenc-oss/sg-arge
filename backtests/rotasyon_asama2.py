#!/usr/bin/env python3
"""T23: stage 2 machinery for rotation cards (``rotasyon:`` block, D12).

``tarama.prepare`` returns a :class:`RotationPrepared` for these cards, so ``asama2a`` / ``asama2b`` / ``portfoy`` can run
them like any other candidate (``run(multiplier, extra_delay_bars=...)``).  Stage 2 always fills at the next open, also for
the Composer cards of the D4 MOC exception: the close fill stays an information column of the stage 1 scan.

Rotation books have no per-trade stop, so the null test of stage 2a compares PF **and CAGR** (``metrik: PF+CAGR``) instead
of PF and mean R.  The null keeps calendar, N, cost and execution of the card; only the selection is random.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from backtests import tarama
from engine import rotasyon
from engine.portfolio import BacktestResult, calculate_metrics

METRIC = "PF+CAGR"
_FIXED_CACHE: dict[tuple[tuple[str, ...], str], dict[str, pd.DataFrame]] = {}




def is_rotation(card: dict[str, Any]) -> bool:
    return bool(card.get("rotasyon"))


def fixed_frames(card: dict[str, Any], directory: Path | None = None) -> dict[str, pd.DataFrame]:
    """Daily bars of the named instruments of a ``gecis`` card (cached: plateau variants reuse them)."""
    symbols, folder = tuple(rotasyon.needed_symbols(card)), directory or tarama.FIXED_DATA_DIR
    key = (symbols, str(folder))
    if key not in _FIXED_CACHE:
        _FIXED_CACHE[key] = tarama.load_fixed_symbols(list(symbols), folder)
    return _FIXED_CACHE[key]


@dataclass
class RotationPrepared:
    """Same surface as ``tarama.Prepared`` for the parts stage 2 uses (``frames``, ``run``, ``annualization``)."""

    card: dict[str, Any]
    frames: dict[str, pd.DataFrame]
    market: str
    start: pd.Timestamp
    end: pd.Timestamp
    base_cost: float
    annualization: int
    base: rotasyon.Baglam
    plan: Any = field(default=None)  # parity with Prepared; rotation books have no per-symbol signal plan

    def run(
        self,
        multiplier: float = 1.0,
        *,
        close_fill: bool | None = None,  # noqa: ARG002 - stage 2 never fills at the close
        signals: Any = None,  # noqa: ARG002
        extra_delay_bars: int = 0,
        weights: pd.DataFrame | None = None,
    ) -> BacktestResult:
        return rotasyon.kos(
            self.card, self.frames, start=self.start, end=self.end, cost_rate=self.base_cost * multiplier,
            weights=self.base.weights if weights is None else weights, extra_delay_bars=extra_delay_bars,
        )

    def run_null(self, rng: np.random.Generator) -> BacktestResult:
        return self.run(1.0, weights=self.base.null(rng))


def prepare_rotation(
    card: dict[str, Any],
    data: dict[str, pd.DataFrame],
    market: str,
    *,
    benchmark: pd.DataFrame | None = None,
    start: pd.Timestamp = tarama.IS_START,
    end: pd.Timestamp = tarama.IS_END,
    pit_universe: Any = None,
) -> RotationPrepared:
    week_end = "SUN" if market == "KRIPTO25" else "FRI"
    kind = card["rotasyon"]["kip"]
    if kind == "gecis":
        frames = fixed_frames(card)
        membership = None
    else:
        frames = {s: f for s, f in data.items() if not f.loc[(f.index >= start) & (f.index <= end)].empty}
        if not frames:
            raise ValueError(f"{market}: donemde veri yok")
        if benchmark is None and any(spec.get("veri") == "endeks" for spec in card["gostergeler"].values()):
            raise tarama.EndeksYok(market)
        membership = tarama.pit_membership(pit_universe, market, list(frames), rotasyon._calendar(frames))  # noqa: SLF001
    base = rotasyon.hazirla(card, frames, benchmark=benchmark, week_end=week_end, membership=membership)
    return RotationPrepared(
        card, frames, market, start, end, tarama.BASE_COST[market], tarama.annualization_for("1D", market), base,
    )


def stats(result: BacktestResult, annualization: int) -> tuple[float, float, int]:
    """(profit factor, CAGR, trades) of one run; PF is capped like ``asama2a.trade_stats``."""
    metrics = calculate_metrics(result, annualization=annualization)
    pf = metrics["pf"]
    return (float(min(pf, 1e9)) if np.isfinite(pf) or pf == np.inf else float("nan")), float(metrics["cagr"]), int(metrics["islem"])


def null_distribution(prepared: RotationPrepared, reps: int, seed: int) -> dict[str, np.ndarray]:
    """PF / CAGR / trade count / mean holding bars of ``reps`` random-selection runs."""
    rng = np.random.default_rng(seed)
    pf, cagr, count, hold = [], [], [], []
    for _ in range(reps):
        result = prepared.run_null(rng)
        one_pf, one_cagr, one_count = stats(result, prepared.annualization)
        pf.append(one_pf); cagr.append(one_cagr); count.append(one_count); hold.append(holding_days(result.trades))
    return {"pf": np.array(pf), "cagr": np.array(cagr), "count": np.array(count), "hold": np.array(hold)}


def holding_days(trades: pd.DataFrame) -> float:
    if trades.empty:
        return float("nan")
    return float(np.mean([(pd.Timestamp(t.exit_date) - pd.Timestamp(t.entry_date)).days for t in trades.itertuples()]))


def plateau_cells(
    prepared: RotationPrepared, data: dict[str, pd.DataFrame], benchmark: pd.DataFrame | None, pit_universe: Any,
    factors: tuple[float, ...] = (0.8, 1.2),
) -> list[tuple[str, float, float, float]]:
    """(parameter, factor, PF, net return) for the centre and every numeric parameter moved alone by +-20 %."""
    centre = prepared.run()
    metrics = calculate_metrics(centre, annualization=prepared.annualization)
    cells = [("merkez", 1.0, metrics["pf"], metrics["getiri"])]
    for parameter in rotasyon.parametreler(prepared.card):
        for factor in factors:
            variant = parameter.uygula(prepared.card, factor)
            run = prepare_rotation(variant, data, prepared.market, benchmark=benchmark, start=prepared.start, end=prepared.end, pit_universe=pit_universe).run()
            m = calculate_metrics(run, annualization=prepared.annualization)
            cells.append((parameter.etiket, factor, m["pf"], m["getiri"]))
    return cells
