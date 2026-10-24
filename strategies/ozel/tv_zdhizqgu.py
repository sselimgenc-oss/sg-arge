"""TV-ZDhizQgu Qing LRC + S/R + EMA: lineer regresyon kanali, pivot destegi yakini giris, kanal/EMA cikisi (kapanistan dolum)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    n = int(p["lrc_length"])
    mid = g.linreg(frame, "close", n, 0)
    dev = T.stdev(close, n)
    upper = mid + float(p["lrc_upper"]) * dev
    lower = mid - float(p["lrc_lower"]) * dev
    ema20 = T.ema(close, 20)
    upper_above = upper > ema20
    lower_below = lower < ema20
    pl = T.pivotlow(frame["low"], int(p["left_bars"]), int(p["right_bars"]))
    last_s = pl.ffill()
    near_support = frame["low"] <= last_s * 1.02
    buy = (upper_above & ((frame["low"] <= lower) | near_support) & (close > frame["open"])).fillna(False).to_numpy(dtype=bool)
    exit_cond = (lower_below | (frame["high"] >= upper)).fillna(False).to_numpy(dtype=bool)
    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    in_pos = False  # strategy.opentrades: kapanista dolan emir ayni barin sonunda pozisyonu degistirir
    for i in range(size):
        if in_pos and exit_cond[i]:
            exit_[i] = True
            in_pos = False
        elif not in_pos and buy[i]:
            entry[i] = True
            in_pos = True
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
