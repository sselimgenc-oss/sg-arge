from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import tarama, u1
from data.fetch import Asset, quality_metrics
from engine.kilit import kes
from scripts import kardes_rapor
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


def test_kilit_no_longer_cuts_the_former_locked_period() -> None:
    index = pd.DatetimeIndex(["2025-09-30 23:00", "2025-10-01 00:00"], tz="UTC")
    frame = _bars(index)
    assert len(kes(frame)) == 2
    assert len(kes(frame, env={"KILIT_AC": "1"})) == 2


def test_kardes_rapor_calculates_pooled_and_sibling_metrics() -> None:
    trades = pd.DataFrame(
        {
            "symbol": ["BTCUSDT", "BTCUSDT", "XRPUSDT", "XRPUSDT", "ADAUSDT"],
            "net_pnl": [10.0, -5.0, 4.0, -1.0, -2.0],
            "exit_date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-01", "2024-02-01", "2024-02-02"], utc=True),
        }
    )
    detail, summary = summarize_trades(trades, core=("BTCUSDT",), siblings=("XRPUSDT", "ADAUSDT"), repetitions=100, seed=1)
    assert set(detail["symbol"]) == {"BTCUSDT", "XRPUSDT", "ADAUSDT"}
    assert summary["pooled_profit_factor"] == (14 / 8)
    assert np.isclose(summary["sibling_pf_gt_1_1_ratio"], 0.5)
    assert summary["best_month_removed"] == "2024-01"


# ---------------------------------------------------------------------------------------------- U1a kalan maddeler

def _trades(rows: list[tuple[str, float, str]]) -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": [r[0] for r in rows], "net_pnl": [r[1] for r in rows],
        "exit_date": pd.to_datetime([r[2] for r in rows], utc=True),
    })


def test_bootstrap_sorts_trades_by_exit_date() -> None:
    """Blocks must be runs of consecutive trades in time: the result may not depend on the row order of the input."""
    rng = np.random.default_rng(0)
    days = pd.date_range("2024-01-01", periods=60, freq="D", tz="UTC")
    rows = [(("BTCUSDT", "ADAUSDT")[i % 2], float(rng.normal(0.2, 1.0)), str(days[i])) for i in range(60)]
    ordered = _trades(rows)
    shuffled = ordered.sample(frac=1.0, random_state=3).reset_index(drop=True)
    by_symbol = ordered.sort_values(["symbol", "exit_date"]).reset_index(drop=True)
    expect = summarize_trades(ordered, repetitions=300, seed=7)[1]
    for other in (shuffled, by_symbol):
        got = summarize_trades(other, repetitions=300, seed=7)[1]
        assert got["pooled_pf_ci90_low"] == expect["pooled_pf_ci90_low"]
        assert got["pooled_pf_ci90_high"] == expect["pooled_pf_ci90_high"]


def test_sibling_ratio_has_a_fixed_denominator_of_eight() -> None:
    assert len(kardes_rapor.SIBLINGS) == 8
    rows = [("ADAUSDT", 5.0, "2024-01-01"), ("ADAUSDT", -1.0, "2024-01-02"),  # PF 5: passes
            ("DOGEUSDT", 1.0, "2024-01-03"), ("DOGEUSDT", -1.0, "2024-01-04"),  # PF 1: fails
            ("LTCUSDT", 0.0, "2024-01-05"),  # PF undefined (0/0): not passed
            ("BTCUSDT", 9.0, "2024-01-06")]  # a core symbol never counts
    _, summary = summarize_trades(_trades(rows), repetitions=50, seed=1)
    assert summary["sibling_pf_gt_1_1_count"] == "1/8"
    assert summary["sibling_pf_gt_1_1_ratio"] == pytest.approx(1 / 8)  # LINK..NEAR have no trades and still count in the 8


def test_sibling_ratio_counts_every_sibling_when_all_pass() -> None:
    rows = [(symbol, 3.0, "2024-01-01") for symbol in kardes_rapor.SIBLINGS] + [(symbol, -1.0, "2024-01-02") for symbol in kardes_rapor.SIBLINGS]
    assert summarize_trades(_trades(rows), repetitions=20)[1]["sibling_pf_gt_1_1_ratio"] == 1.0


def _spec(card_id: str, tf: str = "15m") -> dict:
    card = yaml.safe_load((Path(__file__).resolve().parents[1] / "docs" / "spec" / f"{card_id}.yaml").read_text(encoding="utf-8"))
    card["tf"] = tf
    return card



def test_prepare_lock_compatibility_flag_does_not_cut_data() -> None:
    index = pd.date_range("2025-09-28", "2025-10-05", freq="15min", tz="UTC")
    rng = np.random.default_rng(1)
    close = pd.Series(100 + rng.normal(0, 0.1, len(index)).cumsum(), index=index)
    frame = pd.DataFrame({"open": close, "high": close + 0.1, "low": close - 0.1, "close": close, "volume": 5.0})
    card = _spec("U1-H2-A")
    card["id"] = "T8-07"  # a Hat 0 style id: the old "U1-" prefix test would have skipped the lock
    start, end = pd.Timestamp("2025-09-28", tz="UTC"), pd.Timestamp("2025-10-05", tz="UTC")
    locked = tarama.prepare(card, {"BTCUSDT": frame}, "KRIPTO25", start=start, end=end, kilit=True)
    assert locked.frames["BTCUSDT"].index.max() > pd.Timestamp("2025-09-30", tz="UTC")
    open_ = tarama.prepare(card, {"BTCUSDT": frame}, "KRIPTO25", start=start, end=end)
    assert open_.frames["BTCUSDT"].index.max() > pd.Timestamp("2025-09-30", tz="UTC")


def test_u1_trade_csv_feeds_kardes_rapor_directly(tmp_path, monkeypatch) -> None:
    from tests.test_u1 import crypto  # noqa: PLC0415

    root = tmp_path / "data"
    for folder, minutes in (("15m", 15), ("5m", 5)):
        (root / folder).mkdir(parents=True)
        for k, symbol in enumerate(u1.CORE[:3] + u1.SIBLINGS[:3]):
            crypto(minutes, 60, k).to_parquet(root / folder / f"{symbol}.parquet")
    monkeypatch.setitem(u1.PERIODS, "IS", (pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-03-01", tz="UTC")))
    out = tmp_path / "res"
    assert u1.main(["--hat", "2", "--kart-ids", "U1-H2-A", "--donem", "IS", "--veri-kok", str(root), "--results-dir", str(out)]) == 0
    csv = sorted(out.glob("islemler_*_IS.csv"))[0]
    monkeypatch.setattr(sys, "argv", ["kardes_rapor", str(csv), "--out-csv", str(tmp_path / "k.csv"), "--out-md", str(tmp_path / "k.md"), "--repetitions", "50"])
    assert kardes_rapor.main() == 0  # no conversion step between the runner and the report
    report = pd.read_csv(tmp_path / "k.csv")
    assert set(report["symbol"]) <= set(u1.CORE + u1.SIBLINGS) and report["trades"].sum() == len(pd.read_csv(csv))
    assert "sibling_pf_gt_1_1_count" in (tmp_path / "k.md").read_text(encoding="utf-8")
