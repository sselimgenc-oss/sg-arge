"""TV-qgTc4zie Kaufman Moving Average Adaptive Strategy by MKB: ozyinelemeli KAMA (tohum 0) + standart sapma ust bandi kirilimi."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    src = frame["close"]
    length = int(p["length"])
    noise = src.diff().abs().rolling(length).sum()
    signal = (src - src.shift(length)).abs()
    ef = (signal / noise).where(noise != 0, 0.0)
    fast_end, slow_end = float(p["fast_end"]), float(p["slow_end"])
    smooth = ((ef * (fast_end - slow_end) + slow_end) ** 2).to_numpy()
    x = src.to_numpy(dtype=float)
    kama = np.zeros(len(x))
    prev = 0.0  # var float kama = 0.0; nz(kama[1]) ilk barda 0
    for i in range(len(x)):
        s = smooth[i]
        if np.isnan(s):  # math.sum(...) length bar dolmadan na: kama[i] = na, bir sonraki nz() 0 verir
            kama[i] = np.nan
            prev = 0.0
            continue
        prev = prev + s * (x[i] - prev)
        kama[i] = prev
    kama_s = pd.Series(kama, index=frame.index)
    upper = kama_s + float(p["stdev_mult"]) * T.stdev(src, int(p["stdev_length"]))
    buy = T.crossover(src, upper).to_numpy()
    sell = T.crossunder(src, kama_s).to_numpy()
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
