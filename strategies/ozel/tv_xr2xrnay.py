"""TV-Xr2xrNAY Volatility Capture RSI-Bollinger [presentTrading]: mandalli (var) present Bollinger bandi."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    n = int(p["length"])
    mult = float(p["multiplier"])
    price = (frame["high"] + frame["low"] + frame["close"]) / 3.0  # priceSource = hlc3
    upper = (T.sma(frame["high"], n) + T.stdev(frame["high"], n) * mult).to_numpy()
    lower = (T.sma(frame["low"], n) - T.stdev(frame["low"], n) * mult).to_numpy()
    rsi_sma = T.sma(T.rsi(price, int(p["rsi_period"])), int(p["sma_period"])).to_numpy()
    bought, sold = float(p["bought_range"]), float(p["sold_range"])
    use_rsi = bool(p["use_rsi"])
    x = price.to_numpy()
    close = frame["close"].to_numpy(dtype=float)
    size = len(frame)
    band = np.full(size, np.nan)  # her bar sonundaki present band (var)
    long_cond = np.zeros(size, dtype=bool)
    short_cond = np.zeros(size, dtype=bool)
    prev = np.nan
    for i in range(size):
        # crossover(priceSource, presentBollingBand): sinyal anindaki band bir onceki barin nihai degeridir
        if i > 0 and not np.isnan(prev):
            up_cross = x[i] > prev and x[i - 1] <= prev
            dn_cross = x[i] < prev and x[i - 1] >= prev
        else:
            up_cross = dn_cross = False
        if np.isnan(lower[i]) or np.isnan(upper[i]):
            cur = 0.0
        elif close[i] > prev:
            cur = max(prev, lower[i])
        elif close[i] < prev:
            cur = min(prev, upper[i])
        else:
            cur = 0.0
        long_cond[i] = up_cross and (not use_rsi or rsi_sma[i] > bought)
        short_cond[i] = dn_cross and (not use_rsi or rsi_sma[i] < sold)
        if long_cond[i]:
            cur = lower[i]
        if short_cond[i]:
            cur = upper[i]
        band[i] = cur
        prev = cur
    b = pd.Series(band, index=frame.index)
    exit_ = T.crossunder(frame["close"], b) | pd.Series(short_cond, index=frame.index)
    return pd.DataFrame({"entry": pd.Series(long_cond, index=frame.index), "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
