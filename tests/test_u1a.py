from __future__ import annotations

import numpy as np
import pandas as pd

from data.fetch import Asset, quality_metrics
from engine.kilit import KILIT_SONU, kes
from scripts.kardes_rapor import summarize_trades


def _bars(index: pd.DatetimeIndex) -> pd.DataFrame:
    return pd.DataFrame(
        {"open": 1.0, "high": 1.1, "low": 0.9, "close": 1.0, "volume": 10.0},
        index=index,
    )


def test_binance_quality_uses_requested_interval() -> None:
    index = pd.DatetimeIndex(
        ["2026-01-01 00:00", "2026-01-01 00:15", "2026-01-01 00:45"], tz="UTC"
    )
    metrics = quality_metrics(_bars(index), Asset("BTCUSDT", "KRIPTO25", "binance"), "15m")
    assert metrics["missing_bars"] == 1


def test_kilit_cuts_locked_period_and_explicit_override() -> None:
    index = pd.DatetimeIndex(["2025-09-30 23:00", "2025-10-01 00:00"], tz="UTC")
    frame = _bars(index)
    assert kes(frame).index[-1] == index[0]
    assert len(kes(frame, env={"KILIT_AC": "1"})) == 2


def test_kardes_rapor_calculates_pooled_and_sibling_metrics() -> None:
    trades = pd.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT", "XRPUSDT", "XRPUSDT", "ADAUSDT"],
            "net_pnl": [10.0, -5.0, 4.0, -1.0, -2.0],
            "exit_date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01", "2024-02-01", "2024-02-02"], utc=True),
        }
    )
    detail, summary = summarize_trades(trades, core=("BTCUSDT",), repetitions=100, seed=1)
    assert set(detail["symbol"]) == {"BTCUSDT", "XRPUSDT", "ADAUSDT"}
    assert summary["pooled_profit_factor"] == (14 / 8)
    assert np.isclose(summary["sibling_pf_gt_1_1_ratio"], 0.5)
    assert summary["best_month_removed"] == "2024-01"
