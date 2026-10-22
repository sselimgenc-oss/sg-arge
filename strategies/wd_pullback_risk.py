"""Weekly-direction daily pullback strategy from Codex Algo 21 pages 8/26."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, ema, rsi
from strategies.common import completed_weekly_regime, crossed_above


def signals(frame: pd.DataFrame, market: str, **params: float) -> pd.DataFrame:
    ema_fast = int(params.get("ema_fast", 20))
    ema_slow = int(params.get("ema_slow", 50))
    close = frame["close"]
    ema20 = ema(close, ema_fast)
    ema50 = ema(close, ema_slow)
    rsi14 = rsi(close, 14)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly & (ema20 > ema50) & crossed_above(close, ema20) & (rsi14 > 50),
            "exit": (close < ema50) | (rsi14 < 40) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
