"""Shared, closed-bar-only strategy helpers."""

from __future__ import annotations

import numpy as np
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


def crossed_below(left: pd.Series, right: pd.Series | float) -> pd.Series:
    if isinstance(right, pd.Series):
        return (left.shift(1) >= right.shift(1)) & (left < right)
    return (left.shift(1) >= right) & (left < right)


def roc(series: pd.Series, length: int) -> pd.Series:
    return (series / series.shift(length) - 1.0) * 100.0


def wilder(series: pd.Series, length: int) -> pd.Series:
    """Wilder smoothing compatible with the accepted reference indicators."""

    return series.ewm(alpha=1 / length, adjust=False, min_periods=length).mean()


def dmi(frame: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    high = frame["high"]
    low = frame["low"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=frame.index,
    ).where(up_move.notna() & down_move.notna())
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=frame.index,
    ).where(up_move.notna() & down_move.notna())
    from engine.indicators import true_range

    smoothed_range = wilder(true_range(frame), length)
    plus = 100.0 * wilder(plus_dm, length) / smoothed_range
    minus = 100.0 * wilder(minus_dm, length) / smoothed_range
    denominator = (plus + minus).replace(0, np.nan)
    adx = wilder(100.0 * (plus - minus).abs() / denominator, length)
    return pd.DataFrame({"plus": plus, "minus": minus, "adx": adx})


def efficiency_ratio(series: pd.Series, length: int = 10) -> pd.Series:
    direction = series.diff(length).abs()
    volatility = series.diff().abs().rolling(length, min_periods=length).sum()
    return direction / volatility.replace(0, np.nan)


def kama(
    series: pd.Series,
    length: int = 10,
    fast: int = 2,
    slow: int = 30,
) -> pd.Series:
    """Kaufman adaptive moving average using the first valid price as seed."""

    ratio = efficiency_ratio(series, length)
    fast_constant = 2.0 / (fast + 1.0)
    slow_constant = 2.0 / (slow + 1.0)
    smoothing = (ratio * (fast_constant - slow_constant) + slow_constant) ** 2
    values = series.to_numpy(dtype=float)
    constants = smoothing.to_numpy(dtype=float)
    output = np.full(len(series), np.nan)
    valid = np.flatnonzero(np.isfinite(constants) & np.isfinite(values))
    if len(valid):
        first = int(valid[0])
        # VARSAYIM: PDF KAMA başlangıç tohumunu belirtmiyor; ilk geçerli
        # ER barının kapanışı kullanılır (yaygın özyinelemeli uygulama).
        output[first] = values[first]
        for index in range(first + 1, len(values)):
            if np.isfinite(values[index]) and np.isfinite(constants[index]):
                output[index] = output[index - 1] + constants[index] * (
                    values[index] - output[index - 1]
                )
            else:
                output[index] = output[index - 1]
    return pd.Series(output, index=series.index, name="kama")
