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
    single_market_assets,
    update_manifest,
    update_universe_notes,
)
from data.bist_1h import normalize_bist_1h, normalize_market_1h, quality, quality_gate


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


def test_normalize_ohlcv_accepts_volume_free_fx_bars() -> None:
    result = normalize_ohlcv(_frame(pd.date_range("2026-01-01", periods=2, freq="D", tz="UTC")).drop(columns="Volume"))
    assert result["volume"].tolist() == [0.0, 0.0]


def test_fx8_assets_are_the_approved_eight_pairs() -> None:
    assert [asset.symbol for asset in single_market_assets(("FX8",))] == [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "GBPJPY=X", "AUDUSD=X", "USDCHF=X", "USDCAD=X", "EURJPY=X",
    ]


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
        "sembol,piyasa,kaynak,not\nTHYAO.IS,BIST30,yfinance,\nTHYAO.IS,BIST30,yfinance,\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_universe(path)


def test_project_universe_has_leader_approved_counts() -> None:
    assets = load_universe()
    counts = pd.Series([asset.market for asset in assets]).value_counts().to_dict()

    assert counts == {"BIST30": 30, "ABD25": 27, "KRIPTO25": 25, "EMTIA": 6}
    assert all(asset.symbol.endswith(".IS") for asset in assets if asset.market == "BIST30")
    assert all(asset.symbol.endswith("USDT") for asset in assets if asset.market == "KRIPTO25")


def test_universe_notes_preserve_reference_and_refresh_missing_state(tmp_path: Path) -> None:
    path = tmp_path / "evren.csv"
    path.write_text(
        "sembol,piyasa,kaynak,not\nSPY,ABD25,yfinance,referans; eksik: eski hata\n"
        "KOZAL.IS,BIST30,yfinance,\n",
        encoding="utf-8",
    )

    update_universe_notes({"SPY"}, {"KOZAL.IS": "sembol bulunamadı\nikinci satır"}, path)

    table = pd.read_csv(path).fillna("").set_index("sembol")
    assert table.loc["SPY", "not"] == "referans"
    assert table.loc["KOZAL.IS", "not"] == "eksik: sembol bulunamadı ikinci satır"


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


def test_bist_hourly_normalization_aligns_timezone_merges_ohlcv_and_drops_outside() -> None:
    index = pd.DatetimeIndex(
        [
            "2026-01-02 09:00",  # truly outside: dropped
            "2026-01-02 09:30",  # Yahoo first bar -> 10:00
            "2026-01-02 17:30",  # last continuous bar -> 18:00
            "2026-01-02 18:05",  # closing auction -> merge at 18:00
            "2026-01-02 18:30",  # truly outside: dropped
        ],
        tz="Europe/Istanbul",
    )
    frame = normalize_ohlcv(_frame(index))
    result = normalize_bist_1h(frame)

    assert result.index.tolist() == [
        pd.Timestamp("2026-01-02 07:00", tz="UTC"),
        pd.Timestamp("2026-01-02 15:00", tz="UTC"),
    ]
    last = result.iloc[-1]
    assert last["open"] == 3
    assert last["high"] == 5
    assert last["low"] == 2
    assert last["close"] == 4
    assert last["volume"] == 200
    pd.testing.assert_frame_equal(normalize_bist_1h(result), result)  # idempotent archive/load path


def test_non_bist_hourly_markets_are_unchanged() -> None:
    source = normalize_ohlcv(_frame(pd.date_range("2026-01-02", periods=4, freq="h", tz="UTC")))
    assert normalize_market_1h(source, "ABD25") is source
    assert normalize_market_1h(source, "KRIPTO25") is source


def test_bist_quality_gate_has_pass_and_fail_directions() -> None:
    # Keep all synthetic observations inside the session on separate days.
    index = pd.date_range("2026-01-02 10:00", periods=101, freq="D", tz="Europe/Istanbul")
    good = normalize_ohlcv(_frame(index))
    good.iloc[0, good.columns.get_loc("volume")] = 0
    assert quality(good).zero_volume_changed == 1
    assert quality_gate({"AAA.IS": good})[0]

    bad = good.copy()
    bad.iloc[1, bad.columns.get_loc("volume")] = 0
    assert quality_gate({"AAA.IS": bad})[0] is False


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
