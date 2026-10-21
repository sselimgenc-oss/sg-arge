"""Shared, closed-bar-only strategy helpers."""

from __future__ import annotations

import pandas as pd

from engine.indicators import ema


def completed_weekly_regime(frame: pd.DataFrame, market: str) -> pd.Series:
    """Map a completed weekly close/EMA regime onto daily bars.

    # VARSAYIM: Exchange-traded assets complete their week on Friday, while
    # Binance spot completes it on Sunday UTC. The PDF says only "completed
    # weekly candle" and does not define the calendar boundary.
    """

    week_end = "W-SUN" if market.upper() == "KRIPTO25" else "W-FRI"
    weekly_close = frame["close"].resample(week_end).last().dropna()
    weekly_regime = (weekly_close > ema(weekly_close, 20)) & (
        ema(weekly_close, 20) > ema(weekly_close, 40)
    )
    mapped = weekly_regime.reindex(frame.index, method="ffill").astype("boolean")
    return mapped.fillna(False).astype(bool)


def crossed_above(left: pd.Series, right: pd.Series | float) -> pd.Series:
    if isinstance(right, pd.Series):
        return (left.shift(1) <= right.shift(1)) & (left > right)
    return (left.shift(1) <= right) & (left > right)
