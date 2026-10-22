"""Session-aware OHLCV resampling.

Input frames use a timezone-aware UTC DatetimeIndex and bar-start labels.
Output frames keep the same convention. Incomplete 2/4-hour buckets are omitted
by default so a running session cannot leak a partially formed bar.
"""

from __future__ import annotations

import math

import pandas as pd

OHLCV_AGGREGATION = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


def _validate(frame: pd.DataFrame) -> pd.DataFrame:
    missing = set(OHLCV_AGGREGATION).difference(frame.columns)
    if missing:
        raise ValueError(f"missing OHLCV columns: {sorted(missing)}")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise TypeError("frame index must be a DatetimeIndex")
    if frame.index.tz is None:
        raise ValueError("frame index must be timezone-aware UTC")
    result = frame.sort_index().copy()
    result.index = result.index.tz_convert("UTC")
    if result.index.has_duplicates:
        raise ValueError("frame index contains duplicate timestamps")
    return result


def _aggregate(grouped: object, *, expected_bars: int | pd.Series, drop_incomplete: bool) -> pd.DataFrame:
    bars = grouped.agg(OHLCV_AGGREGATION)
    counts = grouped["close"].count()
    if drop_incomplete:
        expected = expected_bars.reindex(counts.index) if isinstance(expected_bars, pd.Series) else expected_bars
        bars = bars.loc[counts == expected]
    return bars.dropna(subset=["open", "high", "low", "close"])


def _resample_session(
    frame: pd.DataFrame,
    *,
    timezone: str,
    session_open_minutes: int,
    session_close_minutes: int,
    hours: int,
    drop_incomplete: bool,
) -> pd.DataFrame:
    """Aggregate whole 1H buckets anchored at a market's session open.

    The final short session bucket is retained only when every 1H source bar
    available before the session close is present. This keeps the final candle
    while still withholding a running or incomplete bucket.
    """
    local = frame.tz_convert(timezone)
    minute = local.index.hour * 60 + local.index.minute
    local = local[(minute >= session_open_minutes) & (minute < session_close_minutes)].copy()
    if local.empty:
        return local.tz_convert("UTC")

    session_start = local.index.normalize() + pd.to_timedelta(session_open_minutes, unit="m")
    bucket = ((local.index - session_start).total_seconds() // (hours * 60 * 60)).astype(int)
    labels = session_start + pd.to_timedelta(bucket * hours, unit="h")
    local["_bucket"] = labels
    grouped = local.groupby("_bucket", sort=True)
    bucket_labels = pd.DatetimeIndex(grouped.size().index)
    session_end = bucket_labels.normalize() + pd.to_timedelta(session_close_minutes, unit="m")
    # Bars are start-labelled. A 13:30 ET bucket ending at 16:00 therefore
    # needs the 13:30, 14:30 and 15:30 source bars: ceil(2.5) == 3.
    remaining = (session_end - bucket_labels).total_seconds() / 3600
    expected = pd.Series(remaining, index=bucket_labels).map(math.ceil).clip(upper=hours).astype(int)
    result = _aggregate(grouped, expected_bars=expected, drop_incomplete=drop_incomplete)
    result.index = pd.DatetimeIndex(result.index, name=frame.index.name).tz_convert("UTC")
    return result


def _resample_utc(frame: pd.DataFrame, *, hours: int, drop_incomplete: bool) -> pd.DataFrame:
    grouped = frame.resample(f"{hours}h", origin="start_day", label="left", closed="left")
    result = _aggregate(grouped, expected_bars=hours, drop_incomplete=drop_incomplete)
    result.index.name = frame.index.name
    return result


def resample_hourly(
    frame: pd.DataFrame,
    *,
    market: str,
    timeframe: str,
    drop_incomplete: bool = True,
) -> pd.DataFrame:
    """Aggregate 1-hour bars into closed 2H or 4H bars.

    Crypto buckets start at UTC midnight.  US equities and commodities start
    at 09:30 America/New_York, including daylight-saving transitions. BIST
    keeps its established 10:00 Europe/Istanbul session anchor.
    """
    if timeframe not in {"2H", "4H"}:
        raise ValueError(f"unsupported hourly resample timeframe: {timeframe}")
    clean = _validate(frame)
    hours = int(timeframe[:-1])
    if market.upper() == "BIST30":
        return _resample_session(
            clean, timezone="Europe/Istanbul", session_open_minutes=10 * 60,
            session_close_minutes=18 * 60, hours=hours, drop_incomplete=drop_incomplete,
        )
    if market.upper() in {"ABD25", "EMTIA"}:
        return _resample_session(
            clean, timezone="America/New_York", session_open_minutes=9 * 60 + 30,
            session_close_minutes=16 * 60, hours=hours, drop_incomplete=drop_incomplete,
        )
    return _resample_utc(clean, hours=hours, drop_incomplete=drop_incomplete)


def resample_4h(frame: pd.DataFrame, *, market: str, drop_incomplete: bool = True) -> pd.DataFrame:
    """Backward-compatible 4H wrapper; prefer :func:`resample_hourly`."""
    return resample_hourly(frame, market=market, timeframe="4H", drop_incomplete=drop_incomplete)
