"""Weekly-direction ADX breakout strategy, Codex Algo 21 pages 14/28."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr
from strategies.common import completed_weekly_regime, dmi


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    adx14 = dmi(frame, 14)["adx"]
    prior_high55 = frame["high"].shift(1).rolling(55, min_periods=55).max()
    prior_low20 = frame["low"].shift(1).rolling(20, min_periods=20).min()
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly & (adx14 >= 20) & (close > prior_high55),
            "exit": (close < prior_low20) | (adx14 < 15) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
