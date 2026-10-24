"""TV-TIpnJpU8 PresentTrend [presentTrading]: ozyinelemeli esik takibi (PresentTrend) ve barssince ile mandalli trend yonu."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    n = int(p["length"])
    mult = float(p["multiplier"])
    hlc3 = (frame["high"] + frame["low"] + frame["close"]) / 3.0
    prev_close = frame["close"].shift(1)
    tr = pd.concat([frame["high"] - frame["low"], (frame["high"] - prev_close).abs(), (frame["low"] - prev_close).abs()], axis=1).max(axis=1, skipna=False)
    atr_ = T.sma(tr, n)  # ta.sma(ta.tr, length): ilk barin tr'si na
    upper_th = (frame["low"] - atr_ * mult).to_numpy()
    lower_th = (frame["high"] + atr_ * mult).to_numpy()
    flow = (T.rsi(hlc3, n) >= 50) if p["indicator_rsi"] else (g.mfi(frame, n) >= 50)
    bullish = flow.to_numpy()
    size = len(frame)
    pt = np.full(size, np.nan)
    prev = 0.0  # nz(PresentTrend[1])
    for i in range(size):
        if bullish[i]:
            value = prev if upper_th[i] < prev else upper_th[i]
        else:
            value = prev if lower_th[i] > prev else lower_th[i]
        pt[i] = value
        prev = 0.0 if np.isnan(value) else value
    pts = pd.Series(pt, index=frame.index)
    long_sig = T.crossover(pts, pts.shift(2))
    short_sig = T.crossunder(pts, pts.shift(2))
    bars_buy, bars_sell = T.barssince(long_sig), T.barssince(short_sig)
    previous_buy, previous_sell = T.barssince(long_sig.shift(1, fill_value=False)), T.barssince(short_sig.shift(1, fill_value=False))
    set_long = (long_sig & (previous_buy > bars_sell)).to_numpy()
    set_short = (short_sig & (previous_sell > bars_buy)).to_numpy()
    direction = np.zeros(size)
    state = 0.0
    for i in range(size):
        if set_long[i]:
            state = 1.0
        elif set_short[i]:
            state = -1.0
        direction[i] = state
    d = pd.Series(direction, index=frame.index)
    return pd.DataFrame({"entry": d == 1, "exit": d == -1, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
