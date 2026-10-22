"""Weekly-direction daily DMI trend strategy, Codex Algo 21 page 12."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr, ema
from strategies.common import completed_weekly_regime, crossed_above, crossed_below, dmi


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    values = dmi(frame, 14)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly
            & (close > ema(close, 100))
            & crossed_above(values["plus"], values["minus"])
            & (values["adx"] >= 20),
            "exit": crossed_below(values["plus"], values["minus"])
            | (close < ema(close, 50))
            | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
