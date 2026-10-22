"""Weekly-direction daily breakout strategy, Codex Algo 21 pages 17/21/25."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, ema
from strategies.common import completed_weekly_regime


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    prior_high20 = frame["high"].shift(1).rolling(20, min_periods=20).max()
    prior_low10 = frame["low"].shift(1).rolling(10, min_periods=10).min()
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly & (close > prior_high20),
            "exit": (close < prior_low10) | (close < ema(close, 20)) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
