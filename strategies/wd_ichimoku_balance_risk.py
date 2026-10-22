"""Weekly-direction Ichimoku balance strategy, Codex Algo 21 pages 11/19."""

from __future__ import annotations

import pandas as pd

from engine.indicators import atr
from strategies.common import completed_weekly_regime, crossed_above


def _midpoint(frame: pd.DataFrame, length: int) -> pd.Series:
    return (
        frame["high"].rolling(length, min_periods=length).max()
        + frame["low"].rolling(length, min_periods=length).min()
    ) / 2.0


def signals(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    close = frame["close"]
    tenkan = _midpoint(frame, 9)
    kijun = _midpoint(frame, 26)
    # Completed cloud at today's coordinate: spans calculated 26 bars earlier.
    span_a = ((tenkan + kijun) / 2.0).shift(26)
    span_b = _midpoint(frame, 52).shift(26)
    cloud_top = pd.concat([span_a, span_b], axis=1).max(axis=1)
    cloud_bottom = pd.concat([span_a, span_b], axis=1).min(axis=1)
    weekly = completed_weekly_regime(frame, market)
    return pd.DataFrame(
        {
            "entry": weekly
            & (tenkan > kijun)
            & (span_a > span_b)
            & crossed_above(close, cloud_top),
            "exit": (tenkan < kijun) | (close < cloud_bottom) | ~weekly,
            "atr": atr(frame, 14),
        },
        index=frame.index,
    )
