"""TV-o9qty0BL PAXG 4H Supertrend + 40-Bar Breakout Add: Supertrend yukari donusunde ana giris, 40 bar kapanis kirilimiyla tek ek alim, asagi donuste cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    st = T.supertrend(frame, int(p["atr_length"]), float(p["st_multiplier"]))
    direction = st["dir"]  # +1 yukselis (Pine direction < 0)
    prev = direction.shift(1)
    bullish_flip = ((direction > 0) & (prev < 0)).fillna(False).to_numpy(dtype=bool)
    bearish_flip = ((direction < 0) & (prev > 0)).fillna(False).to_numpy(dtype=bool)
    breakout = (close > T.highest(close, int(p["breakout_length"])).shift(1)).fillna(False).to_numpy(dtype=bool)
    start, end = pd.Timestamp(str(p["start"]), tz="UTC"), pd.Timestamp(str(p["end"]), tz="UTC")
    in_range = (frame.index >= start) & (frame.index <= end)
    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    pos, added, pending = 0, False, None
    for i in range(size):
        if pending == "C":
            pos, added = 0, False
        elif pending == "L":
            pos = 1
        pending = None
        if in_range[i] and bullish_flip[i] and pos == 0:
            entry[i] = True
            pending = "L"
        elif in_range[i] and pos > 0 and not added and breakout[i]:
            entry[i] = True
            added = True
        if pos > 0 and bearish_flip[i]:
            exit_[i] = True
            pending = "C"
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, pyramid_max=int(dict(card.get("piramit") or {}).get("en_cok", 0)))
