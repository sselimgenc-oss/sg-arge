from __future__ import annotations

import pandas as pd
import pytest

from engine.resample import resample_4h, resample_hourly


def _bars(index: pd.DatetimeIndex) -> pd.DataFrame:
    values = list(range(1, len(index) + 1))
    return pd.DataFrame(
        {
            "open": values,
            "high": [value + 1 for value in values],
            "low": [value - 1 for value in values],
            "close": [value + 0.5 for value in values],
            "volume": [10] * len(index),
        },
        index=index,
    )


def test_crypto_resample_is_aligned_to_utc_four_hour_boundaries() -> None:
    source = _bars(pd.date_range("2026-01-01", periods=8, freq="1h", tz="UTC", name="timestamp"))

    result = resample_4h(source, market="KRIPTO25")

    assert result.index.tolist() == [
        pd.Timestamp("2026-01-01 00:00", tz="UTC"),
        pd.Timestamp("2026-01-01 04:00", tz="UTC"),
    ]
    assert result.iloc[0].to_dict() == {
        "open": 1.0,
        "high": 5.0,
        "low": 0.0,
        "close": 4.5,
        "volume": 40.0,
    }


def test_bist_resample_does_not_cross_sessions() -> None:
    first_day = pd.date_range("2026-01-05 10:00", periods=8, freq="1h", tz="Europe/Istanbul")
    second_day = pd.date_range("2026-01-06 10:00", periods=8, freq="1h", tz="Europe/Istanbul")
    source = _bars(first_day.append(second_day).tz_convert("UTC").rename("timestamp"))

    result = resample_4h(source, market="BIST30")

    expected_local = pd.DatetimeIndex(
        [
            "2026-01-05 10:00",
            "2026-01-05 14:00",
            "2026-01-06 10:00",
            "2026-01-06 14:00",
        ],
        tz="Europe/Istanbul",
        name="timestamp",
    )
    assert result.index.equals(expected_local.tz_convert("UTC"))
    assert result["volume"].tolist() == [40, 40, 40, 40]


def test_incomplete_bucket_is_not_exposed_by_default() -> None:
    source = _bars(pd.date_range("2026-01-01", periods=5, freq="1h", tz="UTC"))

    result = resample_4h(source, market="KRIPTO25")

    assert len(result) == 1


def test_timezone_naive_input_is_rejected() -> None:
    source = _bars(pd.date_range("2026-01-01", periods=4, freq="1h"))
    with pytest.raises(ValueError, match="timezone-aware"):
        resample_4h(source, market="KRIPTO25")


def test_us_two_hour_buckets_start_at_new_york_session_open() -> None:
    # 09:30 ET is 14:30 UTC on this winter date.  The last 90 minutes of the
    # 6.5-hour session must not become an incomplete two-hour candle.
    index = pd.date_range("2026-01-05 14:30", periods=7, freq="h", tz="UTC", name="timestamp")
    result = resample_hourly(_bars(index), market="ABD25", timeframe="2H")

    assert result.index.tolist() == [
        pd.Timestamp("2026-01-05 14:30", tz="UTC"),
        pd.Timestamp("2026-01-05 16:30", tz="UTC"),
        pd.Timestamp("2026-01-05 18:30", tz="UTC"),
    ]
    assert result.iloc[0].to_dict() == {
        "open": 1.0, "high": 3.0, "low": 0.0, "close": 2.5, "volume": 20.0,
    }


def test_partial_bucket_never_revises_an_already_closed_candle() -> None:
    source = _bars(pd.date_range("2026-01-01", periods=5, freq="h", tz="UTC"))

    closed = resample_hourly(source.iloc[:2], market="KRIPTO25", timeframe="2H")
    later = resample_hourly(source.iloc[:3], market="KRIPTO25", timeframe="2H")

    assert len(later) == 1
    assert later.iloc[0].equals(closed.iloc[0])
