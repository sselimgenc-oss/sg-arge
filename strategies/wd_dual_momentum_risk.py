"""Weekly-direction dual momentum strategy, Codex Algo 21 pages 15/23."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, ema
from strategies.common import completed_weekly_regime, roc


def signals(frame: pd.DataFrame, market: str, **params: float) -> pd.DataFrame:
    short_momentum = int(params.get("short_momentum", 21))
    long_momentum = int(params.get("long_momentum", 63))
    close = frame["close"]
    roc21 = roc(close, short_momentum)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly & (close > ema(close, 100)) & (roc(close, long_momentum) > 0) & (roc21 > 0),
            "exit": (roc21 < 0) | (close < ema(close, 50)) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
