"""Weekly-direction daily momentum strategy, Codex Algo 21 pages 18/27."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, ema
from strategies.common import completed_weekly_regime, roc


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    ema20 = ema(close, 20)
    ema50 = ema(close, 50)
    roc20 = roc(close, 20)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly & (ema20 > ema50) & (roc20 > 5),
            "exit": (ema20 < ema50) | (roc20 < 0) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
