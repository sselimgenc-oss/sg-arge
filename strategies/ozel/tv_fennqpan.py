"""TV-FEnNQpAn RORO System Oscillator: ALMA - VWMA egimi ve ROC momentumundan 0-100 osilator; yumusatilmis osilatorun 30'u yukari kesmesi."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def alma(s: pd.Series, length: int, offset: float, sigma: float) -> pd.Series:
    """ta.alma: pencere en eskiden en yeniye, agirlik exp(-(i - m)^2 / (2 s^2)), m = floor(offset (n - 1)), s = n / sigma."""
    m = np.floor(offset * (length - 1))
    sd = length / sigma
    weights = np.exp(-((np.arange(length) - m) ** 2) / (2.0 * sd * sd))
    weights = weights / weights.sum()
    x = s.astype(float).to_numpy()
    out = np.full(len(x), np.nan)
    if len(x) >= length:
        windows = np.lib.stride_tricks.sliding_window_view(x, length)
        out[length - 1:] = windows @ weights
    return pd.Series(out, index=s.index)


def _normalize(x: pd.Series) -> pd.Series:
    return x / (1.0 + x.abs())


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    src, volume = frame["close"], frame["volume"]
    a = alma(src, int(p["alma_length"]), float(p["alma_offset"]), float(p["alma_sigma"]))
    n = int(p["vwma_length"])
    vwma = T.sma(src * volume, n) / T.sma(volume, n)
    trend = _normalize((a - vwma) / vwma * float(p["scaling_factor"]))
    roc = (src / src.shift(int(p["roc_length"])) - 1.0) * 100.0
    momentum = _normalize(roc / T.stdev(roc, 50))
    score = trend * 0.6 + momentum * 0.4
    osc = (score * 100.0).clip(lower=-100.0, upper=100.0)
    smooth = alma(osc, int(p["alma_length"]), float(p["alma_offset"]), float(p["alma_sigma"]))
    buy = T.crossover(smooth, float(p["entry_level"])).to_numpy()
    sell = (smooth < float(p["exit_level"])).fillna(False).to_numpy()
    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    pos, pending = 0, 0
    for i in range(size):
        if pending:
            pos, pending = (1, 0) if pending == 1 else (0, 0)
        if buy[i] and pos == 0:
            entry[i], pending = True, 1
        elif sell[i] and pos == 1:
            exit_[i], pending = True, 2
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
