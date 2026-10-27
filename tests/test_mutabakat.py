"""Gecikmeli kopya mutabakatı (görev 13): ağsız, sabit yanıtlarla."""
from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from copytrade.kapi import delayed_copy, next_candle_open, prev_candle_open
from copytrade.mutabakat import breakdown, build_report, denominators, funding_all, render

HOUR = 3_600_000
NOW = datetime(2026, 10, 27, 12, tzinfo=UTC)
NOW_MS = int(NOW.timestamp() * 1000)


def fill(t, side, sz, before, px=100, coin="BTC", pnl=0, tid=0):
    return {"time": t, "coin": coin, "side": side, "sz": str(sz), "px": str(px), "startPosition": str(before), "closedPnl": str(pnl), "fee": "0", "tid": tid}


def candles(coin_prices):
    return {coin: [{"t": NOW_MS - 20 * 24 * HOUR + i * HOUR, "o": str(price + (i % 5))} for i in range(20 * 24 + 5)] for coin, price in coin_prices.items()}


def test_rounding_bounds_and_neutral_default():
    series = [{"t": 0, "o": "10"}, {"t": HOUR, "o": "20"}, {"t": 2 * HOUR, "o": "30"}]
    assert next_candle_open(series, 30 * 60_000, 30) == 20      # hedef 01:00 → 01:00 mumu (≥ hedef)
    assert next_candle_open(series, 10 * 60_000, 30) == 20      # hedef 00:40 → sonraki mum
    assert prev_candle_open(series, 10 * 60_000, 30) == 10      # hedef 00:40 → önceki mum
    assert prev_candle_open(series, 30 * 60_000, 30) == 20      # hedef tam 01:00
    assert prev_candle_open([], 0, 30) is None and prev_candle_open(series, -2 * HOUR, 0) is None


def test_breakdown_totals_equal_delayed_copy_and_split_by_coin():
    start = NOW_MS - 10 * 24 * HOUR
    fills = [fill(start, "B", 1, 0, coin="BTC", tid=1), fill(start + 5 * HOUR, "A", 1, 1, coin="BTC", tid=2),
             fill(start + HOUR, "A", 2, 0, coin="xyz:CL", tid=3), fill(start + 9 * HOUR, "B", 2, -2, coin="xyz:CL", tid=4)]
    market = candles({"BTC": 100, "xyz:CL": 70})
    funding = [{"time": start + 2 * HOUR, "delta": {"coin": "BTC", "usdc": "-1"}}]
    for rounding in ("up", "down"):
        info = breakdown(fills, market, 1000, 30, funding, rounding)
        series, _ = delayed_copy(fills, market, 1000, 30, funding, rounding=rounding)
        assert info["toplam"]["net"] == pytest.approx(float(series.sum())) == pytest.approx(info["net_seri"])
        assert set(info["coinler"]) == {"BTC", "xyz:CL"} and info["coinler"]["BTC"]["funding"] == pytest.approx(-0.001)
        assert info["toplam"]["maliyet"] == pytest.approx(sum(c["maliyet"] for c in info["coinler"].values()))
    default, _ = delayed_copy(fills, market, 1000, 30, funding)
    assert float(default.sum()) == pytest.approx(breakdown(fills, market, 1000, 30, funding, "up")["net_seri"])   # varsayılan değişmedi


def test_corrected_variant_does_not_open_inverse_position_for_inherited_exposure():
    start = NOW_MS - 10 * 24 * HOUR
    # Pencere öncesinden gelen 1 BTC long; pencerede kapanıyor. Kapı hesabı bunu yeni short sayar (before=0).
    fills = [fill(start, "A", 1, 1, pnl=5, tid=1)]
    market = candles({"BTC": 100})
    gate = breakdown(fills, market, 1000, 30, [], "up", corrected=False)
    fixed = breakdown(fills, market, 1000, 30, [], "up", corrected=True)
    assert gate["toplam"]["dolum"] == 1 and fixed["toplam"]["dolum"] == 0 and fixed["toplam"]["net"] == 0.0


def test_funding_pagination_and_denominators():
    pages = [[{"time": i, "delta": {"coin": "BTC", "usdc": "1"}} for i in range(500)],
             [{"time": 500 + i, "delta": {"coin": "BTC", "usdc": "1"}} for i in range(120)]]
    calls = []

    class Client:
        def info(self, payload, weight=20):
            calls.append(payload["startTime"])
            return pages.pop(0)
    assert len(funding_all(Client(), "0x1", 0, 10_000)) == 620 and calls == [0, 500]
    portfolio = [["allTime", {"accountValueHistory": [[1, "0"], [2, "100"], [3, "300"], [4, "200"]]}]]
    assert denominators(portfolio, 2, 250.0, 260.0) == {"lider_tablosu": 250.0, "clearinghouse_guncel": 260.0, "pencere_medyan": 200.0, "pencere_basi": 100.0}


def test_report_contains_range_trades_coins_hip3_denominator_and_costs():
    start = NOW_MS - 60 * 24 * HOUR
    fills = [fill(start, "B", 1, 0, coin="xyz:GOLD", tid=1), fill(start + 5 * HOUR, "A", 1, 1, coin="xyz:GOLD", pnl=3, tid=2),
             fill(start + 8 * HOUR, "B", 1, 0, coin="BTC", tid=3), fill(start + 9 * HOUR, "A", 1, 1, coin="BTC", pnl=1, tid=4)]
    report = build_report("0x" + "1" * 40, NOW, fills, [], candles({"xyz:GOLD": 3000, "BTC": 100}),
                          [["allTime", {"accountValueHistory": [[start, "900"], [NOW_MS, "1100"]]}]], 1000.0, 1010.0)
    window = report["pencereler"]["190"]
    assert report["hip3_dahil"] and report["hip3_dex"] == ["xyz"] and window["kapanmis_dongu"] == 2 and window["coin_sayisi"] == 2
    assert set(window["secenekler"]) >= {"30dk|kapi|up", "30dk|duzeltilmis|down", "120dk|kapi|up", "480dk|kapi|down", "0dk|kapi|up"}
    assert report["pencereler"]["200"]["baslangic"] < window["baslangic"]
    text = render(report)
    for needle in ("Son 190 gün", "Son 200 gün", "HIP-3 dahil: evet (xyz)", "Coin dökümü", "xyz:GOLD", "Payda duyarlılığı", "lider_tablosu", "Maliyet"):
        assert needle in text
    json.dumps(report, allow_nan=False)
