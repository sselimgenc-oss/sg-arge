"""TV-sPNx5Z74 Percent Supertrend (Long Only): hl2 +/- %20 bantlari, kapanisla iz suren; trend -1 -> +1 giris, +1 -> -1 cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def trend_series(frame: pd.DataFrame, perc: float) -> pd.Series:
    close = frame["close"].to_numpy(dtype=float)
    hl2 = ((frame["high"] + frame["low"]) / 2.0).to_numpy(dtype=float)
    upper_basic, lower_basic = hl2 * (1 + perc), hl2 * (1 - perc)
    n = len(close)
    fu, fl, trend = np.full(n, np.nan), np.full(n, np.nan), np.ones(n)
    for i in range(n):
        if i == 0 or np.isnan(fu[i - 1]):
            fu[i], fl[i] = upper_basic[i], lower_basic[i]
        else:
            fu[i] = upper_basic[i] if close[i - 1] > fu[i - 1] else min(upper_basic[i], fu[i - 1])
            fl[i] = lower_basic[i] if close[i - 1] < fl[i - 1] else max(lower_basic[i], fl[i - 1])
        trend[i] = trend[i - 1] if i else 1.0
        if i and close[i] > fu[i - 1]:
            trend[i] = 1.0
        elif i and close[i] < fl[i - 1]:
            trend[i] = -1.0
    return pd.Series(trend, index=frame.index)


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    trend = trend_series(frame, float(p["perc"]) / 100.0)
    prev = trend.shift(1)
    return pd.DataFrame({"entry": (trend == 1) & (prev == -1), "exit": (trend == -1) & (prev == 1),
                         "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
