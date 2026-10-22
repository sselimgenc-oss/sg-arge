"""Weekly-direction daily mean reversion strategy, Codex Algo 21 page 20."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, rsi
from strategies.common import completed_weekly_regime


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    basis = close.rolling(20, min_periods=20).mean()
    deviation = close.rolling(20, min_periods=20).std(ddof=0)
    lower = basis - 2.0 * deviation
    rsi2 = rsi(close, 2)
    weekly = completed_weekly_regime(frame, market)
    result = pd.DataFrame(
        {
            "entry": weekly & (close < lower) & (rsi2 < 10),
            "exit": (close >= basis) | (rsi2 > 70) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
    return result
