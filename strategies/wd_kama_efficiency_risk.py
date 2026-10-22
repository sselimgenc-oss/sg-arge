"""Weekly-direction KAMA efficiency strategy, Codex Algo 21 page 13."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr
from strategies.common import completed_weekly_regime, crossed_above, efficiency_ratio, kama


def signals(frame: pd.DataFrame, market: str, **params: float) -> pd.DataFrame:
    er_period = int(params.get("er_period", 10))
    kama_fast = int(params.get("kama_fast", 2))
    close = frame["close"]
    kama_line = kama(close, er_period, kama_fast, 30)
    er10 = efficiency_ratio(close, er_period)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly
            & crossed_above(close, kama_line)
            & (kama_line > kama_line.shift(5))
            & (er10 >= 0.30),
            "exit": (close < kama_line) | (er10 < 0.12) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
