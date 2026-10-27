from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from copytrade.kapi import (CandleCache, bhy, binance_availability, binance_symbol, candle_coverage, delayed_copy,
                             evidence_status, gate_status, next_candle_open,
                             placebo_pvalue, placebo_scores, randomize_trades, time_weighted_monthly, write_binance_universe)


def portfolio(values):
    return [["allTime", {"accountValueHistory": values}]]


def test_time_weighted_return_removes_deposit_and_keeps_no_flow_series():
    day = 86_400_000
    values = [[0, "100"], [day, "110"], [2 * day, "220"]]
    no_flow = time_weighted_monthly(portfolio(values), [])
    flow = time_weighted_monthly(portfolio(values), [{"time": 2 * day, "delta": {"type": "deposit", "usdc": "100"}}])
    assert round(no_flow.iloc[0], 3) == 1.2
    assert round(flow.iloc[0], 3) == 0.2
    withdrawn = time_weighted_monthly(portfolio([[0, "100"], [day, "110"], [2 * day, "20"]]),
                                      [{"time": 2 * day, "delta": {"type": "withdraw", "usdc": "100"}}])
    assert round(withdrawn.iloc[0], 3) == .2


def test_delayed_copy_uses_next_candle_open_not_fill_price():
    fills = [{"time": 0, "coin": "BTC", "side": "B", "sz": "1", "px": "1", "startPosition": "0"},
             {"time": 60_000, "coin": "BTC", "side": "A", "sz": "1", "px": "1", "startPosition": "1"}]
    candles = {"BTC": [{"t": 30 * 60_000, "o": "100"}, {"t": 31 * 60_000, "o": "110"}]}
    pnl, missing = delayed_copy(fills, candles, 1_000, 30)
    assert round(pnl.iloc[0], 5) == .0098  # 1% account return, less 0.045% + 0.05% on each side
    assert next_candle_open(candles["BTC"], 0, 30) == 100
    assert missing == 0


def test_zero_delay_uses_leader_fill_and_cache_requests_each_coin_once():
    fills = [{"time": 0, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0"},
             {"time": 60_000, "coin": "BTC", "side": "A", "sz": "1", "px": "110", "startPosition": "1"}]
    assert delayed_copy(fills, {}, 1_000, 0)[0].iloc[0] > 0

    class Client:
        def __init__(self): self.calls = 0
        def candles(self, *args, **kwargs): self.calls += 1; return [{"t": 0, "o": "100"}]
    client = Client()
    cache = CandleCache(client, 0, 1)
    assert cache.for_fills(fills) == cache.for_fills(fills) and client.calls == 1
    assert candle_coverage(fills, {"BTC": [{"t": 0, "o": "100"}, {"t": 3_600_000, "o": "100"}]}) == 1


def test_bhy_and_three_outcome_step_classes():
    q = bhy({"a": .01, "b": .04, "c": .2})
    assert round(q["a"], 3) == .055 and q["a"] <= q["b"] <= q["c"]
    assert evidence_status(179, 100, 8) == "Yetersiz"
    base = {"complete_data": True, "history_days": 180, "closed_trades": 50, "active_months": 6,
            "median_holding_hours": 1, "median_leverage": 3, "max_leverage": 10,
            "profitable_month_ratio": .6, "largest_trade_share": .2,
            "profit_factor_without_best": 1.3, "martingale_signal": False}
    assert gate_status(base, 1, .05, {"alfa_yillik": 1, "nw_t": 2})["adim6"] == "Geçti"
    assert gate_status(base, 1, .05, {"alfa_yillik": 1, "nw_t": 1.9})["adim6"] == "Yetersiz"
    assert gate_status(base, 1, .05, {"alfa_yillik": 0, "nw_t": 9})["adim6"] == "Kaldı"
    assert placebo_pvalue(2, [1, 2, 3]) == .75


def test_placebo_placement_preserves_trade_fields_is_non_overlapping_and_seeded():
    trades = [{"coin": "BTC", "side": "B", "size_ratio": .1, "holding_hours": 2},
              {"coin": "ETH", "side": "A", "size_ratio": .2, "holding_hours": 3}]
    start, end = pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-10", tz="UTC")
    first, second = randomize_trades(trades, start, end, 8), randomize_trades(trades, start, end, 8)
    assert first == second
    assert {(x["coin"], x["side"], x["size_ratio"], x["holding_hours"]) for x in first} == {
        (x["coin"], x["side"], x["size_ratio"], x["holding_hours"]) for x in trades}
    assert first[0]["close_time"] <= first[1]["open_time"]


def test_placebo_scores_runs_fixed_repetitions():
    fills = [{"time": 0, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0"},
             {"time": 3_600_000, "coin": "BTC", "side": "A", "sz": "1", "px": "101", "startPosition": "1"}]
    candles = {"BTC": [{"t": i * 3_600_000, "o": "100"} for i in range(30)]}
    assert len(placebo_scores(fills, candles, 1_000, pd.Timestamp(0, unit="ms", tz="UTC"),
                              pd.Timestamp(20 * 3_600_000, unit="ms", tz="UTC"), repetitions=3)) == 3


def test_binance_mapping_and_blocked_response_are_information_only(tmp_path):
    class Blocked:
        status_code = 451
    symbols, note = write_binance_universe(tmp_path, datetime(2026, 10, 27, tzinfo=UTC), get=lambda *_a, **_k: Blocked())
    assert symbols is None and note == "HTTP 451"
    assert binance_symbol("kPEPE") == "1000PEPEUSDT"
    assert binance_availability("BTC", symbols) == "bilinmiyor"
    assert binance_availability("xyz:SPX", {"SPXUSDT"}) == "yok"
