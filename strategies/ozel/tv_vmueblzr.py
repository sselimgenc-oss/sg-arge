"""TV-vMuEblZr EW Bottom Signals 1.4X VOLUME: ZigZag dalga durumu (A/B/C), kapitulasyon mumu ve uc kademeli alim; olu carpraz (death cross) ile tek sefer cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, open_, high, low = frame["close"], frame["open"], frame["high"], frame["low"]
    depth = int(p["zigzag_depth"])
    is_high = (high.shift(depth) == T.highest(high, depth * 2 + 1)).fillna(False).to_numpy(dtype=bool)
    is_low = (low.shift(depth) == T.lowest(low, depth * 2 + 1)).fillna(False).to_numpy(dtype=bool)
    ma50, ma200 = T.sma(close, 50), T.sma(close, 200)
    body = (close - open_).abs()
    wick = (high - low) - body
    capitulation = ((open_ > close) & (wick > body) & (frame["volume"] > T.sma(frame["volume"], 20) * float(p["volume_spike"]))).fillna(False).to_numpy(dtype=bool)
    below200 = (close < ma200).fillna(False).to_numpy(dtype=bool)
    cross50 = T.crossover(close, ma50).to_numpy()
    golden = T.crossover(ma50, ma200).to_numpy()
    death = T.crossunder(ma50, ma200).to_numpy()
    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    swing_dir = 0
    state = 0
    allow = first = second = final = sold = False
    for i in range(size):
        if is_high[i]:
            swing_dir = -1
        if is_low[i]:
            swing_dir = 1
        if is_high[i] and swing_dir == -1 and state == 0:
            state = 1
        if is_low[i] and swing_dir == 1 and state == 1:
            state = 2
        if is_high[i] and swing_dir == -1 and state == 2:
            state = 3
        if state == 3 and is_low[i] and swing_dir == 1:
            state = 0
        if below200[i] and not allow and not sold:
            allow = True
        if allow and state == 3 and below200[i] and capitulation[i] and not first:
            first = True
            entry[i] = True
        if allow and first and cross50[i] and not second:
            second = True
            entry[i] = True
        if allow and second and golden[i] and not final:
            final = True
            entry[i] = True
        if final and death[i] and not sold:
            sold = True
            exit_[i] = True
            allow = False
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, pyramid_max=int(dict(card.get("piramit") or {}).get("en_cok", 0)))
