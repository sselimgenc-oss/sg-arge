"""Kapı istatistikleri: plasebo dağılımı, maruziyet eşleşmiş NW alfa, DSR, N_eff kümeleme.

Strateji döneminden (backtests/plasebo.py) taşındı; copy trade kapısında kullanılacak.
"""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np
import pandas as pd

REPS = 1000


def deflated_sharpe_ratio(returns: pd.Series, trials: int) -> float:
    """Local DSR implementation; keeps this reporting tool independent of the card runner."""
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 3 or np.std(values, ddof=1) == 0:
        return np.nan
    sr = float(values.mean() / np.std(values, ddof=1))
    centered = values - values.mean()
    skew = float(np.mean(centered**3) / np.mean(centered**2) ** 1.5)
    kurtosis = float(np.mean(centered**4) / np.mean(centered**2) ** 2)
    std = math.sqrt(max(1 - skew * sr + (kurtosis - 1) * sr * sr / 4, 0) / (len(values) - 1))
    hurdle = 0.0
    if trials > 1:
        normal, gamma = NormalDist(), 0.5772156649015329
        hurdle = std * ((1 - gamma) * normal.inv_cdf(1 - 1 / trials) + gamma * normal.inv_cdf(1 - 1 / (trials * math.e)))
    z = (sr - hurdle) / std if std else 0.0
    return NormalDist().cdf(z)


def active_blocks(exposure: pd.Series) -> list[int]:
    """Return consecutive non-zero exposure lengths (including a final block)."""
    on = exposure.fillna(0).to_numpy(dtype=float) != 0
    starts = np.flatnonzero(on & np.r_[True, ~on[:-1]])
    ends = np.flatnonzero(on & np.r_[~on[1:], True])
    return [int(end - start + 1) for start, end in zip(starts, ends, strict=True)]


def random_exposure(index: pd.Index, blocks: list[int], rng: np.random.Generator) -> pd.Series:
    """Place every holding block once, without overlap; preserve count and durations."""
    if not blocks:
        return pd.Series(0.0, index=index)
    # One empty day between blocks keeps adjacent trades distinct.  Sampling
    # the surplus gaps directly avoids a greedy placement getting trapped.
    required = sum(blocks) + len(blocks) - 1
    if required > len(index):
        raise ValueError("blocks do not fit in the requested period")
    gaps = rng.multinomial(len(index) - required, np.full(len(blocks) + 1, 1 / (len(blocks) + 1)))
    taken = np.zeros(len(index), dtype=bool)
    cursor = int(gaps[0])
    for position, item in enumerate(rng.permutation(len(blocks))):
        length = blocks[int(item)]
        taken[cursor:cursor + length] = True
        cursor += length + 1 + int(gaps[position + 1])
    return pd.Series(taken.astype(float), index=index)


def placebo_distribution(
    market: pd.Series, exposure: pd.Series, *, repetitions: int = REPS, seed: int = 0,
    round_trip_cost: float = 0.001, scale: float = 1.0,
) -> np.ndarray:
    """Net-return distribution for random entries with identical holding blocks.

    ``scale`` is the position size relative to full investment (volatility matched to the strategy), so the
    placebo takes the same risk as the strategy; ``round_trip_cost`` is charged once per block on that size.
    """
    market = pd.to_numeric(market, errors="coerce").fillna(0.0)
    blocks = active_blocks(exposure.reindex(market.index, fill_value=0.0))
    if not blocks:
        return np.zeros(repetitions)
    rng = np.random.default_rng(seed)
    totals = np.empty(repetitions)
    for i in range(repetitions):
        w = random_exposure(market.index, blocks, rng)
        starts = int(((w > 0) & (w.shift(fill_value=0) == 0)).sum())
        totals[i] = float(np.prod(1 + scale * w.to_numpy() * market.to_numpy()) - 1 - starts * round_trip_cost * scale)
    return totals


def nw_alpha(strategy: pd.Series, benchmark: pd.Series, lags: int = 5, periods: int = 252,
             min_artik_varyans: float | None = None) -> dict[str, float | str]:
    """Annualised OLS alpha/beta and Newey-West t statistic for alpha.

    Regresyon artık varyansı ``min_artik_varyans``'ın (verilmezse ``kurallar.yaml`` ``alfa_min_artik_varyans``) altındaysa — birebir kopya ya da
    deterministik ilişki — t kayan nokta gürültüsüdür: ``nw_t`` NaN ve ``durum`` "yetersiz" döner, alfa ne olursa olsun (alfa bilgi olarak kalır).
    """
    frame = pd.concat([strategy.rename("y"), benchmark.rename("x")], axis=1).dropna()
    if len(frame) < 8 or frame.x.var() == 0:
        return {"beta": np.nan, "alfa_yillik": np.nan, "nw_t": np.nan, "durum": "yetersiz"}
    if min_artik_varyans is None:
        from copytrade.kurallar import load_rules
        min_artik_varyans = float(load_rules()["alfa_min_artik_varyans"])
    x = np.column_stack([np.ones(len(frame)), frame.x.to_numpy()])
    y = frame.y.to_numpy()
    inv = np.linalg.inv(x.T @ x)
    coef = inv @ x.T @ y
    residual = y - x @ coef
    out = {"beta": float(coef[1]), "alfa_yillik": float(coef[0] * periods)}
    if float(np.var(residual)) < float(min_artik_varyans):
        return {**out, "nw_t": np.nan, "durum": "yetersiz"}
    meat = np.zeros((2, 2))
    for lag in range(min(lags, len(frame) - 1) + 1):
        weight = 1.0 if lag == 0 else 1 - lag / (lags + 1)
        if lag == 0:
            term = (x * residual[:, None]).T @ (x * residual[:, None])
        else:
            term = (x[lag:] * residual[lag:, None]).T @ (x[:-lag] * residual[:-lag, None])
            term = term + term.T
        meat += weight * term
    se = math.sqrt(max(float((inv @ meat @ inv)[0, 0]), 0.0))
    return {**out, "nw_t": float(coef[0] / se) if se else np.nan, "durum": "gecerli" if se else "yetersiz"}


def neff_clusters(series: dict[str, pd.Series], threshold: float = 0.9) -> int:
    """Hierarchical single-link correlation clusters, returned as N_eff."""
    keys = list(series)
    parent = list(range(len(keys)))
    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def join(a: int, b: int) -> None:
        a, b = find(a), find(b)
        if a != b: parent[b] = a
    frame = pd.concat(series, axis=1).fillna(0.0)
    for i in range(len(keys)):
        for j in range(i):
            if frame.iloc[:, i].std() and frame.iloc[:, j].std() and frame.iloc[:, i].corr(frame.iloc[:, j]) >= threshold:
                join(i, j)
    return len({find(i) for i in range(len(keys))})
