from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from data.fetch import (
    Asset,
    load_universe,
    merge_archive,
    normalize_ohlcv,
    quality_metrics,
    update_manifest,
)


def _frame(index: pd.DatetimeIndex, start: int = 1) -> pd.DataFrame:
    values = list(range(start, start + len(index)))
    return pd.DataFrame(
        {
            "Open": values,
            "High": [value + 1 for value in values],
            "Low": [value - 1 for value in values],
            "Close": values,
            "Volume": [100] * len(index),
        },
        index=index,
    )


def test_normalize_ohlcv_converts_to_sorted_unique_utc() -> None:
    index = pd.DatetimeIndex(
        ["2026-01-01 11:00", "2026-01-01 10:00", "2026-01-01 11:00"],
        tz="Europe/Istanbul",
    )
    result = normalize_ohlcv(_frame(index))
    assert result.index.tz == timezone_utc()
    assert result.index.is_monotonic_increasing
    assert not result.index.has_duplicates
    assert result.loc[pd.Timestamp("2026-01-01 08:00", tz="UTC"), "close"] == 3


def timezone_utc():
    return pd.Timestamp("2026-01-01", tz="UTC").tz


def test_merge_archive_prefers_new_value_at_same_timestamp() -> None:
    existing = normalize_ohlcv(_frame(pd.date_range("2026-01-01", periods=2, freq="1h", tz="UTC")))
    incoming = normalize_ohlcv(_frame(pd.date_range("2026-01-01 01:00", periods=2, freq="1h", tz="UTC"), start=20))

    result = merge_archive(existing, incoming)

    assert len(result) == 3
    assert result.loc[pd.Timestamp("2026-01-01 01:00", tz="UTC"), "close"] == 20


def test_load_universe_rejects_duplicate_symbols(tmp_path: Path) -> None:
    path = tmp_path / "evren.csv"
    path.write_text(
        "symbol,market,source\nTHYAO.IS,BIST30,yfinance\nTHYAO.IS,BIST30,yfinance\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_universe(path)


def test_crypto_quality_counts_missing_hours_and_zero_volume() -> None:
    frame = normalize_ohlcv(
        pd.DataFrame(
            {
                "open": [1, 2],
                "high": [2, 3],
                "low": [0, 1],
                "close": [1, 2],
                "volume": [0, 10],
            },
            index=pd.DatetimeIndex(["2026-01-01 00:00", "2026-01-01 02:00"], tz="UTC"),
        )
    )
    metrics = quality_metrics(frame, Asset("BTCUSDT", "KRIPTO25", "binance"))
    assert metrics["missing_bars"] == 1
    assert metrics["zero_volume"] == 1


def test_manifest_records_total_archive_size(tmp_path: Path) -> None:
    path = tmp_path / "MANIFEST.csv"
    rows = [
        {"symbol": "AAA", "market": "ABD25", "interval": "1h", "source": "yfinance", "bytes": 10},
        {"symbol": "BBB", "market": "ABD25", "interval": "1h", "source": "yfinance", "bytes": 15},
        {"symbol": "CCC", "market": "ABD25", "interval": "1d", "source": "yfinance", "bytes": 5},
    ]

    update_manifest(rows, path)

    manifest = pd.read_csv(path)
    assert manifest.loc[manifest["interval"] == "1h", "archive_total_bytes"].tolist() == [25, 25]
    assert manifest.loc[manifest["interval"] == "1d", "archive_total_bytes"].tolist() == [5]
