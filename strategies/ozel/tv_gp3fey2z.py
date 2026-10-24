"""TV-GP3FEy2z SIS (EUREX:FDXS1!): Tenkan/Kijun, Supertrend benzeri 'avg' dongusunden; long: tenkan kijun'u yukari keserse, assagi keserse kapat."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def _pmax(a: float, b: float) -> float:
    return np.nan if np.isnan(a) or np.isnan(b) else max(a, b)


def _pmin(a: float, b: float) -> float:
    return np.nan if np.isnan(a) or np.isnan(b) else min(a, b)


def avg_line(frame: pd.DataFrame, length: int, mult: float) -> pd.Series:
    """Pine `avg(close, length, mult)`: ATR bantli supertrend durumu; max/min zincirinin ortalamasi (na yayilir)."""
    src = frame["close"].to_numpy(dtype=float)
    hl2 = ((frame["high"] + frame["low"]) / 2.0).to_numpy(dtype=float)
    atr = T.atr(frame, length).to_numpy(dtype=float) * mult
    up, dn = hl2 + atr, hl2 - atr
    n = len(src)
    upper, lower = np.full(n, np.nan), np.full(n, np.nan)
    os_, spt = np.full(n, np.nan), np.full(n, np.nan)
    mx, mn, out = np.full(n, np.nan), np.full(n, np.nan), np.full(n, np.nan)
    for i in range(n):
        up_prev = upper[i - 1] if i else np.nan
        lo_prev = lower[i - 1] if i else np.nan
        upper[i] = min(up[i], up_prev) if i and src[i - 1] < up_prev and not np.isnan(up[i]) else up[i]
        lower[i] = max(dn[i], lo_prev) if i and src[i - 1] > lo_prev and not np.isnan(dn[i]) else dn[i]
        os_prev = os_[i - 1] if i else np.nan
        if src[i] > upper[i]:
            os_[i] = 1.0
        elif src[i] < lower[i]:
            os_[i] = 0.0
        else:
            os_[i] = os_prev
        spt[i] = lower[i] if os_[i] == 1.0 else upper[i]
        cross = False
        if i and not (np.isnan(spt[i]) or np.isnan(spt[i - 1])):
            cross = (src[i] > spt[i] and src[i - 1] <= spt[i - 1]) or (src[i] < spt[i] and src[i - 1] >= spt[i - 1])
        mx_prev = mx[i - 1] if i else np.nan
        mn_prev = mn[i - 1] if i else np.nan
        mx[i] = _pmax(src[i], mx_prev) if (cross or os_[i] == 1.0) else spt[i]
        mn[i] = _pmin(src[i], mn_prev) if (cross or os_[i] == 0.0) else spt[i]
        out[i] = (mx[i] + mn[i]) / 2.0
    return pd.Series(out, index=frame.index)


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    tenkan = avg_line(frame, int(p["tenkan_len"]), float(p["tenkan_mult"]))
    kijun = avg_line(frame, int(p["kijun_len"]), float(p["kijun_mult"]))
    return pd.DataFrame({"entry": T.crossover(tenkan, kijun), "exit": T.crossunder(tenkan, kijun),
                         "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
