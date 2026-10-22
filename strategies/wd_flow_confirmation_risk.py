"""Weekly-direction daily volume-flow confirmation, Codex Algo 21 page 10."""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.indicators import atr, ema
from strategies.common import completed_weekly_regime, crossed_above


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    high = frame["high"]
    low = frame["low"]
    volume = frame["volume"]
    spread = (high - low).replace(0, np.nan)
    multiplier = ((close - low) - (high - close)) / spread
    money_flow_volume = multiplier.fillna(0.0) * volume
    cmf20 = money_flow_volume.rolling(20, min_periods=20).sum() / volume.rolling(
        20, min_periods=20
    ).sum().replace(0, np.nan)
    adl = money_flow_volume.cumsum()
    obv = (np.sign(close.diff()).fillna(0.0) * volume).cumsum()
    obv_ema20 = ema(obv, 20)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly
            & (close > ema(close, 100))
            & crossed_above(cmf20, 0.0)
            & (adl > adl.shift(20))
            & (obv > obv_ema20),
            "exit": (cmf20 < -0.05) | (obv < obv_ema20) | (close < ema(close, 50)) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
