"""Session-aware OHLCV resampling.

Input frames use a timezone-aware UTC DatetimeIndex and bar-start labels.
Output frames keep the same convention. Incomplete 4-hour buckets are omitted
by default so a running session cannot leak a partially formed bar.
"""

from __future__ import annotations

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


def _aggregate(grouped: object, *, drop_incomplete: bool) -> pd.DataFrame:
    bars = grouped.agg(OHLCV_AGGREGATION)
    counts = grouped["close"].count()
    if drop_incomplete:
        bars = bars.loc[counts == 4]
    return bars.dropna(subset=["open", "high", "low", "close"])


def _resample_bist(frame: pd.DataFrame, *, drop_incomplete: bool) -> pd.DataFrame:
    local = frame.tz_convert("Europe/Istanbul")
    minute = local.index.hour * 60 + local.index.minute
    session_open = 10 * 60
    session_close = 18 * 60
    local = local[(minute >= session_open) & (minute < session_close)].copy()
    if local.empty:
        return local.tz_convert("UTC")

    session_start = local.index.normalize() + pd.offsets.Hour(10)
    bucket = ((local.index - session_start).total_seconds() // (4 * 60 * 60)).astype(int)
    labels = session_start + pd.to_timedelta(bucket * 4, unit="h")
    local["_bucket"] = labels
    grouped = local.groupby("_bucket", sort=True)
    result = _aggregate(grouped, drop_incomplete=drop_incomplete)
    result.index = pd.DatetimeIndex(result.index, name=frame.index.name).tz_convert("UTC")
    return result


def _resample_utc(frame: pd.DataFrame, *, drop_incomplete: bool) -> pd.DataFrame:
    grouped = frame.resample("4h", origin="start_day", label="left", closed="left")
    result = _aggregate(grouped, drop_incomplete=drop_incomplete)
    result.index.name = frame.index.name
    return result


def resample_4h(
    frame: pd.DataFrame,
    *,
    market: str,
    drop_incomplete: bool = True,
) -> pd.DataFrame:
    """Aggregate 1-hour bars into closed 4-hour bars.

    ``BIST30`` buckets start at 10:00 and 14:00 Europe/Istanbul without
    crossing a session boundary. Crypto buckets start at 00:00, 04:00, ...
    UTC. Other markets currently use the UTC alignment and should not be used
    for exchange-session strategies until a market calendar is added.
    """

    clean = _validate(frame)
    if market.upper() == "BIST30":
        return _resample_bist(clean, drop_incomplete=drop_incomplete)
    return _resample_utc(clean, drop_incomplete=drop_incomplete)
