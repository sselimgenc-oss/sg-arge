"""Weekly-direction daily CCI continuation strategy, Codex Algo 21 pages 9/16/22/24."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, cci, ema
from strategies.common import completed_weekly_regime, crossed_above


def signals(frame: pd.DataFrame, market: str, **params: float) -> pd.DataFrame:
    cci_period = int(params.get("cci_period", 20))
    ema_slow = int(params.get("ema_slow", 100))
    close = frame["close"]
    ema50 = ema(close, 50)
    ema100 = ema(close, ema_slow)
    cci20 = cci(frame, cci_period)
    weekly = completed_weekly_regime(frame, market)
    # VARSAYIM: "son 10 gün içinde negatif" means the ten completed sessions
    # before the crossing bar; the PDF does not state whether the crossing bar
    # belongs to that lookback window.
    recently_negative = cci20.shift(1).rolling(10, min_periods=10).min() < 0
    return pd.DataFrame(
        {
            "entry": weekly & (close > ema100) & recently_negative & crossed_above(cci20, 100.0),
            "exit": (cci20 < 0) | (close < ema50) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
