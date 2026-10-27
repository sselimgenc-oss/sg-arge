"""Altın örnekler (görev 25): elle hesaplanmış küçük senaryolar. HER senaryo hem kopya defterinden hem plasebo motorundan (kimlik yerleştirmesi)
geçer ve ikisi de AYNI beklenen sayıyı verir (görev 20: gerçek skor ile plasebo skoru aynı fonksiyondan çıkar).

Ortak: hesap 1000 $, maliyet %0,095 (taker %0,045 + kayma %0,05) her dolumda; sonuçlar hesaba oranla.
"""
from __future__ import annotations

import pandas as pd
import pytest

from copytrade.defter import DAY, HOUR, FundingRates, Market, copy_ledger
from copytrade.kapi import placebo_scores
from copytrade.kurallar import load_rules

T0 = 20_833 * DAY
A = 1000.0
RULES = load_rules()


def candles(prices, coin="BTC"):
    return {coin: [{"t": T0 + h * HOUR, "o": str(p), "c": str(p)} for h, p in sorted(prices.items())]}


def fill(minutes, side, size, before, px, coin="BTC", tid=0):
    return {"time": T0 + minutes * 60_000, "coin": coin, "side": side, "sz": str(size), "startPosition": str(before), "px": str(px),
            "closedPnl": "0", "fee": "0", "tid": tid}


def identity(templates, start, end, seed, notes=None):
    return list(templates)


def both(fills, market, delay, end_hours, rates=None):
    """(kopya defteri neti, plasebo motorunun kimlik yerleştirmesi neti)."""
    start_ms, end_ms = T0 - DAY, T0 + end_hours * HOUR
    ledger = copy_ledger(fills, Market(market), A, delay, start_ms, end_ms, rates, RULES)["net"]
    scores, actual = placebo_scores(fills, market, A, pd.Timestamp(start_ms, unit="ms", tz="UTC"), pd.Timestamp(end_ms, unit="ms", tz="UTC"),
                                    1, delay, None, rates, RULES, place=identity, return_actual=True)
    return ledger, (scores[0] if scores else 0.0), actual


SCENARIOS = {
    # (açıklama) → (dolumlar, mumlar, gecikme dk, pencere sonu (saat), funding, beklenen net)
    "1 miras pozisyonun kapanışı (bizde yok → hiçbir şey)": (
        [fill(120, "A", 5, 5, 100)], candles({0: 100, 3: 100}), 0, 24, None, 0.0),
    "2 parçalı açılış ve kısmi kapanışlar (ortalama giriş 105)": (
        [fill(60, "B", 10, 0, 100), fill(120, "B", 10, 10, 110), fill(180, "A", 10, 20, 120), fill(240, "A", 10, 10, 130)],
        candles({0: 100}), 0, 24, None, (400 - 4.37) / 1000),
    "3 tersine dönüş (kapat + yeni ters pozisyon aç)": (
        [fill(60, "B", 10, 0, 100), fill(120, "A", 15, 10, 110), fill(180, "B", 5, -5, 105)],
        candles({0: 100}), 0, 24, None, (125 - 3.01625) / 1000),
    "4 gecikmede mum boşluğu (kapanış dolumu eksik, açık pozisyon fiyatlanır)": (
        [fill(10, "B", 10, 0, 100), fill(100, "A", 10, 10, 100)], candles({0: 99, 1: 100, 2: 104}), 30, 2, None, 0.03905),
    "5 açık pozisyonun fiyatlanması (kapanış yürütmesi pencere sonrasına düşer)": (
        [fill(60, "B", 10, 0, 100), fill(300, "A", 10, 10, 100)], candles({h: (100 if h < 5 else 106) for h in range(0, 8)}), 30, 5, None,
        (-1000 * 0.00095 + 10 * (106 - 100)) / 1000),
    "6 funding kopyanın kendi pozisyonundan (trader'ın usdc'si değil)": (
        [fill(60, "B", 10, 0, 100), fill(300, "A", 10, 10, 100)], candles({h: 100 for h in range(0, 8)}), 0, 7,
        FundingRates([{"time": T0 + h * HOUR + 5, "delta": {"coin": "BTC", "usdc": "999", "fundingRate": "0.0001"}} for h in range(1, 6)]),
        -0.0023),
    "7 gecikme: sonraki mum açılışı": (
        [fill(70, "B", 10, 0, 100), fill(190, "A", 10, 10, 100)], candles({1: 99, 2: 101, 3: 102, 4: 105, 5: 106}), 30, 6, None,
        (40 - 1.957) / 1000),
}


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_scenario_gives_the_hand_computed_number_in_both_engines(name):
    fills, market, delay, end_hours, rates, expected = SCENARIOS[name]
    ledger, placebo, actual = both(fills, market, delay, end_hours, rates)
    assert ledger == pytest.approx(expected, abs=1e-9)
    assert placebo == pytest.approx(expected, abs=1e-9)
    assert actual is None or actual == pytest.approx(expected, abs=1e-9)


def test_there_are_at_least_six_golden_scenarios():
    assert len(SCENARIOS) >= 6


def test_golden_8_account_value_floor_sums_main_and_hip3_dexes_and_stops_at_kaldi():
    """Görev 27. Bugünkü hesap değeri = ana piyasa + tüm HIP-3 dex toplamı; tabanın (10.000 $) altı 1. aşamada Kaldı, neden "hesap değeri tabanı".
    El hesabı: ana 6.000 + xyz 3.000 + flx 999 = 9.999 $ → Kaldı; ana 6.000 + xyz 3.000 + flx 1.000 = 10.000 $ → geçer (eşik dahil); 0 $ → Kaldı."""
    from datetime import datetime, timezone
    from test_asama1_payda import portfolio
    import copytrade.kapi as kapi

    def client(values):
        class Client:
            requests = 0
            def info(self, body, weight=1):
                if body["type"] == "perpDexs":
                    return [None, {"name": "xyz"}, {"name": "flx"}]
                return {"marginSummary": {"accountValue": str(values.get(body.get("dex", ""), 0))}}
            def portfolio(self, address):
                return portfolio([i * 100 for i in range(14)], [1000 + i * 100 for i in range(14)])   # 1. aşamayı geçen eğri
        return Client()

    assert kapi.hip3_dex_names(client({})) == ["xyz", "flx"]
    assert kapi.total_account_value(client({"": 6000, "xyz": 3000, "flx": 999}), "0xa", ["xyz", "flx"]) == 9999.0
    assert kapi.total_account_value(client({"": 6000, "xyz": 3000, "flx": 1000}), "0xa", ["xyz", "flx"]) == 10000.0
    rules = kapi.load_rules()
    for values, passes in (({}, False), ({"": 6000, "xyz": 3000, "flx": 999}, False), ({"": 6000, "xyz": 3000, "flx": 1000}, True)):
        row = kapi.evaluate_address({"address": "0xa", "accountValue": 50000.0}, client(values), type("C", (), {"requests": 0})(),
                                    datetime.now(timezone.utc), 0, 0, None, rules, dexes=["xyz", "flx"])
        if not passes:
            assert row["asama1"] == "Kaldı" and row["neden"] == "hesap değeri tabanı" and row["hesap_degeri_bugun"] < 10000
        else:
            # Taban geçildi: satır tabanda kesilmedi (sonraki aşamada bu sahte istemci dolum veremediğinden veri hatası olması beklenir).
            assert row.get("neden") != "hesap değeri tabanı" and row["asama1"] != "Kaldı" and row["hesap_degeri_bugun"] == 10000.0
    table = kapi.finalize(pd.DataFrame([{"address": "0xa", "asama1": "Kaldı", "neden": "hesap değeri tabanı"}]), rules)
    assert table.loc[0, "sinif"] == "Kaldı"
