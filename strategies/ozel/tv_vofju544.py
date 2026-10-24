"""TV-VOFjU544 GXG Trend Engine: ATR(1) x 3 tamponlu ozyinelemeli izleyen cizgi; cizgiyi yukari kesince long, asagi kesince cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    price = frame["close"].to_numpy(dtype=float)  # useHAFeed = false
    buffer = float(p["sens_factor"]) * T.atr(frame, int(p["atr_window"])).to_numpy(dtype=float)
    size = len(price)
    trail = np.full(size, np.nan)
    prev = 0.0  # var float trailLine = 0.0; nz(trailLine[1], 0.0)
    for i in range(size):
        if np.isnan(buffer[i]):
            continue
        p0 = price[i]
        p1 = price[i - 1] if i > 0 else np.nan
        if p0 > prev and p1 > prev:
            cur = max(prev, p0 - buffer[i])
        elif p0 < prev and p1 < prev:
            cur = min(prev, p0 + buffer[i])
        elif p0 > prev:
            cur = p0 - buffer[i]
        else:
            cur = p0 + buffer[i]
        trail[i] = cur
        prev = cur
    close = pd.Series(price, index=frame.index)
    line = pd.Series(trail, index=frame.index)
    long_signal = (close > line) & T.crossover(close, line)  # ta.ema(priceFeed, 1) = priceFeed
    short_signal = (close < line) & T.crossover(line, close)
    return pd.DataFrame({"entry": long_signal, "exit": short_signal, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
