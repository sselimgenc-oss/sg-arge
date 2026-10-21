"""Indicator implementations used by the event-driven reference engine."""

from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False, min_periods=length).mean()


def true_range(frame: pd.DataFrame) -> pd.Series:
    previous_close = frame["close"].shift(1)
    ranges = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous_close).abs(),
            (frame["low"] - previous_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(frame: pd.DataFrame, length: int = 14) -> pd.Series:
    return true_range(frame).ewm(alpha=1 / length, adjust=False, min_periods=length).mean()


def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / length, adjust=False, min_periods=length).mean()
    relative_strength = gain / loss.replace(0, float("nan"))
    result = 100 - (100 / (1 + relative_strength))
    result = result.mask((loss == 0) & (gain > 0), 100.0)
    return result.mask((loss == 0) & (gain == 0), 50.0)


def cci(frame: pd.DataFrame, length: int = 20) -> pd.Series:
    typical = (frame["high"] + frame["low"] + frame["close"]) / 3
    average = typical.rolling(length, min_periods=length).mean()
    mean_deviation = typical.rolling(length, min_periods=length).apply(
        lambda values: abs(values - values.mean()).mean(), raw=True
    )
    return (typical - average) / (0.015 * mean_deviation.replace(0, float("nan")))
