"""TV-W67tJltC Multi-Factor Adaptive Z-Score (Z-Edge): bilesik z-skor, ATR yuzdeligine gore uyarlanan ozyinelemeli yumusatma."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def zscore(s: pd.Series, n: int) -> pd.Series:
    sd = T.stdev(s, n)
    z = (s - T.sma(s, n)) / sd
    return z.where(sd > 0, 0.0).where(sd.notna())  # sd > 0 ? (s-m)/sd : 0.0


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    src = frame["close"]
    period = int(p["zscore_period"])
    roc = (src - src.shift(int(p["momentum_length"]))) / src.shift(int(p["momentum_length"])) * 100.0
    vol_ratio = frame["volume"] / T.sma(frame["volume"], int(p["vol_length"]))
    wp, wr, wv = float(p["w_price"]), float(p["w_rsi"]), float(p["w_vol"])
    wsum = wp + wr + wv
    composite = (zscore(roc, period) * wp + zscore(T.rsi(src, int(p["rsi_length"])), period) * wr + zscore(vol_ratio, period) * wv) / (1.0 if wsum == 0 else wsum)
    atr_val = T.atr(frame, int(p["atr_length"]))
    rank = T.percentrank(atr_val, int(p["atr_rank_length"]))
    lo, hi = float(p["min_smoothing"]), float(p["max_smoothing"])
    dyn = (hi - (hi - lo) * (rank / 100.0)) if p["adaptive_on"] else pd.Series(float(p["smoothing_base"]), index=frame.index)
    dyn_len = np.maximum(np.floor(dyn.to_numpy() + 0.5), 1.0)  # math.max(math.round(x), 1); NaN korunur
    dyn_len = np.where(np.isnan(dyn.to_numpy()), np.nan, dyn_len)
    alpha = 2.0 / (dyn_len + 1.0)
    comp = composite.to_numpy()
    smooth = np.full(len(frame), np.nan)
    prev = np.nan
    for i in range(len(frame)):
        smooth[i] = comp[i] if np.isnan(prev) else prev + alpha[i] * (comp[i] - prev)
        prev = smooth[i]
    sc = pd.Series(smooth, index=frame.index)
    long_entry = T.crossover(sc, 0.0) if p["entry_mode"] == "Zero Cross" else T.crossover(sc, float(p["long_threshold"]))
    long_exit = T.crossunder(sc, float(p["exit_level_long"]))
    short_entry = T.crossunder(sc, 0.0) if p["entry_mode"] == "Zero Cross" else T.crossunder(sc, float(p["short_threshold"]))
    stop_dist = atr_val * float(p["atr_mult_stop"])
    return pd.DataFrame({
        "entry": long_entry, "exit": long_exit | short_entry, "atr": T.atr(frame, 14),
        "_stop_level": frame["close"] - stop_dist,
    }, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
