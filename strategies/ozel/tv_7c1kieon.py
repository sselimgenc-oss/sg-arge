"""TV-7C1kIEOn BBTrend w SuperTrend decision [presentTrading]: BBTrend osilatoru uzerinde yapay barlarla ozel Supertrend."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    mult = float(p["stddev_mult"])
    sm, sd_s = T.sma(close, int(p["short_len"])), T.stdev(close, int(p["short_len"])) * mult
    lm, sd_l = T.sma(close, int(p["long_len"])), T.stdev(close, int(p["long_len"])) * mult
    bbtrend = ((sm - sd_s) - (lm - sd_l)).abs() - ((sm + sd_s) - (lm + sd_l)).abs()
    bbtrend = bbtrend / sm * 100.0
    src = bbtrend.to_numpy()
    size = len(frame)
    prev_src = np.r_[np.nan, src[:-1]]
    o = np.nan_to_num(prev_src, nan=0.0)  # nz(src[1])
    h = np.maximum(o, src)
    low = np.minimum(o, src)
    c = src
    prev_c = np.r_[np.nan, c[:-1]]
    prev_h = np.r_[np.nan, h[:-1]]
    tr = np.where(np.isnan(prev_h), h - low, np.maximum(np.maximum(h - low, np.abs(h - prev_c)), np.abs(low - prev_c)))
    length = int(p["st_len"])
    atr_ = T.rma(pd.Series(tr, index=frame.index), length).to_numpy()
    factor = float(p["st_factor"])
    hl2 = (h + low) / 2.0
    up = np.zeros(size)
    dn = np.zeros(size)
    st = np.full(size, np.nan)
    direction = np.full(size, np.nan)
    for i in range(size):
        pu = 0.0 if i == 0 or np.isnan(up[i - 1]) else up[i - 1]  # nz(up[1])
        pdn = 0.0 if i == 0 or np.isnan(dn[i - 1]) else dn[i - 1]
        a = atr_[i]
        u = hl2[i] + factor * a
        d = hl2[i] - factor * a
        pc = prev_c[i]
        u = u if (u < pu or (not np.isnan(pc) and pc > pu)) else pu
        d = d if (d > pdn or (not np.isnan(pc) and pc < pdn)) else pdn
        up[i], dn[i] = u, d
        prev_atr = atr_[i - 1] if i > 0 else np.nan
        if np.isnan(prev_atr):
            direction[i] = 1.0
        else:
            prev_st = st[i - 1]
            if prev_st == pu:
                direction[i] = -1.0 if c[i] > u else 1.0
            else:
                direction[i] = 1.0 if c[i] < d else -1.0
        st[i] = d if direction[i] == -1.0 else u
    dirs = pd.Series(direction, index=frame.index)
    return pd.DataFrame({"entry": dirs < 0, "exit": dirs > 0, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
