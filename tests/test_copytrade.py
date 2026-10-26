from __future__ import annotations

from pathlib import Path

from copytrade.izleme import update
from copytrade.kopya import simulate
from copytrade.kurallar import evaluate
from copytrade.olcut import calculate_metrics, closed_round_trips, martingale_ratio
from copytrade.tarama import RateLimiter, prefilter, run


def fill(time, side, size, position, pnl=0, fee=0, coin="BTC", price=100):
    return {"time": time, "side": side, "sz": size, "startPosition": position, "closedPnl": pnl,
            "fee": fee, "coin": coin, "px": price}


def test_round_trip_and_realized_net_pnl():
    fills = [fill(1_000, "B", 1, 0), fill(7_201_000, "A", 1, 1, pnl=10, fee=1)]
    trips = closed_round_trips(fills)
    assert len(trips) == 1
    assert trips[0]["net_pnl"] == 9
    assert trips[0]["holding_hours"] == 2


def test_martingale_only_flags_same_direction_addition_while_losing():
    bad = [fill(1_000, "B", 1, 0), fill(2_000, "B", 1, 1, pnl=-1)]
    safe = [fill(1_000, "B", 1, 0), fill(2_000, "A", 1, 1, pnl=-1)]
    assert martingale_ratio(bad) == 1
    assert martingale_ratio(safe) == 0


def test_metrics_include_signed_funding():
    fills = [fill(1_000, "B", 1, 0), fill(7_201_000, "A", 1, 1, pnl=10, fee=1)]
    metrics = calculate_metrics(fills, [{"time": 7_202_000, "delta": {"usdc": "-2"}}])
    assert metrics["closed_trades"] == 1
    assert metrics["history_days"] == 0


def test_rules_have_three_outcomes():
    assert evaluate({"history_days": 1, "closed_trades": 0})[0] == "yetersiz"
    base = {"history_days": 181, "closed_trades": 51, "profitable_month_ratio": .8, "largest_trade_share": .2,
            "profit_factor_without_best": 1.3, "sortino": 1.6, "calmar": 1.1, "median_holding_hours": 2,
            "median_leverage": 4, "max_leverage": 10, "liquid_coin_share": .9, "martingale_signal": False}
    assert evaluate(base)[0] == "aday"
    assert evaluate({**base, "max_leverage": 16})[0] == "elendi"


def test_watchlist_preserves_t0_and_never_removes(tmp_path: Path):
    path = tmp_path / "izleme.csv"
    update(path, ["0xA"], "2026-01-01", "v1", {"0xa": "aday"})
    rows = update(path, ["0xB"], "2026-02-01", "v2", {"0xa": "elendi", "0xb": "aday"})
    assert [(r["address"], r["t0"], r["status"]) for r in rows] == [("0xA", "2026-01-01", "elendi"), ("0xB", "2026-02-01", "aday")]


def test_copy_charges_friction_and_funding():
    ledger = simulate([fill(1_000, "B", 1, 0, pnl=10, price=100)], 1_000, slippage=.0005, taker_fee=.00045,
                      funding=[{"time": 2_000, "usdc": -2}])
    assert round(ledger.net_pnl.iloc[0], 3) == 7.905


def test_prefilter_keeps_watchlist_and_caps_ranked():
    rows = [{"ethAddress": f"0x{i}", "accountValue": 25_000, "monthRoi": 1, "allTimeRoi": 1, "allTimePnl": i}
            for i in range(301)]
    selected = prefilter(rows, [{"address": "0x0"}])
    assert len(selected) == 301
    assert selected[-1]["address"] == "0x0"


def test_prefilter_accepts_documented_window_performances_shape():
    row = {"ethAddress": "0xA", "accountValue": "25000", "windowPerformances": [
        {"window": "month", "roi": "1", "pnl": "3"}, {"window": "allTime", "roi": "2", "pnl": "4"}]}
    assert prefilter([row], [])[0]["address"] == "0xA"


def test_rate_limiter_waits_before_exceeding_limit():
    now = [0.0]
    limiter = RateLimiter(2, clock=lambda: now[0], sleep=lambda seconds: now.__setitem__(0, now[0] + seconds))
    limiter.acquire(2)
    limiter.acquire(1)
    assert now[0] >= 60


def test_daily_run_writes_public_archive_watchlist_and_report(tmp_path: Path):
    class Client:
        def leaderboard(self):
            return [{"ethAddress": "0xA", "accountValue": "25000", "monthROI": 1, "allTimeROI": 1, "allTimePnL": 1}]

        def fills(self, address, start):
            return [fill(1_000, "B", 1, 0), fill(7_201_000, "A", 1, 1, pnl=10, fee=1)]

        def info(self, payload, weight=20):
            if payload["type"] == "userFunding":
                return []
            return {"assetPositions": []}

    table = run(tmp_path, Client(), today="2026-10-27", limit=1)
    assert len(table) == 1
    assert (tmp_path / "veri/lider/2026-10-27.csv.gz").exists()
    assert (tmp_path / "veri/fills/0xa.csv.gz").exists()
    assert (tmp_path / "RAPOR.md").exists()
