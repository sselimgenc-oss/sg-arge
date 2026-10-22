"""Weekly-direction daily mean reversion strategy, Codex Algo 21 page 20."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, rsi
from strategies.common import completed_weekly_regime


def signals(frame: pd.DataFrame, market: str, **params: float) -> pd.DataFrame:
    bb_period = int(params.get("bb_period", 20))
    rsi_entry_threshold = float(params.get("rsi_entry_threshold", 10))
    close = frame["close"]
    basis = close.rolling(bb_period, min_periods=bb_period).mean()
    deviation = close.rolling(bb_period, min_periods=bb_period).std(ddof=0)
    lower = basis - 2.0 * deviation
    rsi2 = rsi(close, 2)
    weekly = completed_weekly_regime(frame, market)
    result = pd.DataFrame(
        {
            "entry": weekly & (close < lower) & (rsi2 < rsi_entry_threshold),
            "exit": (close >= basis) | (rsi2 > 70) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
    return result
