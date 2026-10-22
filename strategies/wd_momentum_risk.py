"""Weekly-direction daily momentum strategy, Codex Algo 21 pages 18/27."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, ema
from strategies.common import completed_weekly_regime, roc


def signals(frame: pd.DataFrame, market: str, **params: float) -> pd.DataFrame:
    roc_period = int(params.get("roc_period", 20))
    ema_slow = int(params.get("ema_slow", 50))
    close = frame["close"]
    ema20 = ema(close, 20)
    ema50 = ema(close, ema_slow)
    roc20 = roc(close, roc_period)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly & (ema20 > ema50) & (roc20 > 5),
            "exit": (ema20 < ema50) | (roc20 < 0) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
