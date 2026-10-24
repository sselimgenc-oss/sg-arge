"""TV-TbK1rB5B TrendShift: ADX rejimine gore degisen carpanli Supertrend yon degisimi (BTCUSD 1D)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    adx = T.dmi(frame, int(p["adx_len"]))["adx"].to_numpy()
    trending = adx > float(p["adx_trend"])
    choppy = adx < float(p["adx_chop"])
    mult = np.empty(len(frame))
    current = float(p["tight_mult"])  # var effectiveMult = tightMult; NEUTRAL'de onceki deger korunur
    for i in range(len(frame)):
        if trending[i]:
            current = float(p["tight_mult"])
        elif choppy[i]:
            current = float(p["wide_mult"])
        mult[i] = current
    st = T.supertrend(frame, int(p["atr_len"]), mult)
    direction = st["dir"]
    flip = direction.diff()
    bull_flip = (flip != 0) & flip.notna() & (direction == 1)
    bear_flip = (flip != 0) & flip.notna() & (direction == -1)
    allowed = pd.Series(~(choppy & bool(p["disable_chop"])), index=frame.index)
    return pd.DataFrame({"entry": bull_flip & allowed, "exit": bear_flip & allowed, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
