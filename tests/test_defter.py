"""Kopya defteri altın örnekleri (elle hesaplanmış; docs/GOREV_TRADER_SECIMI.md 19 ve 25).

Ortak kurallar: hesap 1000 $, maliyet = %0,045 taker + %0,05 kayma = %0,095 (her dolumda, notional'a oranla), sonuçlar hesaba oranla.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from copytrade.defter import DAY, HOUR, FundingRates, Market, copy_ledger
from copytrade.kurallar import load_rules

T0 = 20_833 * DAY                  # UTC gece yarısı
C = 0.00095
A = 1000.0
RULES = load_rules()


def candles(prices: dict[int, float], coin="BTC"):
    """{saat: açılış} → saatlik mumlar; kapanış = aynı saatin açılışı (testte yalnız açılış kullanılır)."""
    return {coin: [{"t": T0 + h * HOUR, "o": str(p), "c": str(p)} for h, p in sorted(prices.items())]}


def fill(minutes, side, size, before, px=0.0, coin="BTC", tid=0):
    return {"time": T0 + minutes * 60_000, "coin": coin, "side": side, "sz": str(size), "startPosition": str(before), "px": str(px), "tid": tid}


def run(fills, market, delay=0, end_hours=24, funding=None, daily=False):
    return copy_ledger(fills, Market(market), A, delay, T0 - DAY, T0 + end_hours * HOUR, funding, RULES, daily)


def test_golden_1_inherited_position_closing_opens_nothing():
    """Trader pencere öncesinden 5 BTC long taşıyor ve kapatıyor; bizde yok → işlem yok, net 0 (eski hesap 5 BTC short açardı)."""
    out = run([fill(120, "A", 5, 5, px=100)], candles({0: 100, 3: 100}))
    assert out["executed"] == 0 and out["net"] == 0.0 and out["missing"] == 0


def test_golden_2_partial_entries_and_partial_closes_use_average_entry():
    """B10@100, B10@110 (ort. giriş 105), A10@120 (+150), A10@130 (+250); maliyet 4,37 $ → net (400 − 4,37) / 1000 = 0,39563."""
    fills = [fill(60, "B", 10, 0, 100), fill(120, "B", 10, 10, 110), fill(180, "A", 10, 20, 120), fill(240, "A", 10, 10, 130)]
    out = run(fills, candles({0: 100}))
    assert out["net"] == pytest.approx(0.39563) and out["realized"] == pytest.approx(0.39563) and out["unrealized_end"] == 0.0
    assert out["costs"] == pytest.approx(4.37 / 1000)


def test_golden_3_reversal_closes_old_and_opens_new_position():
    """B10@100; A15@110 (10'u kapatır +100, 5 short açar); B5@105 short'u kapatır (+25). Maliyet (1000+1650+525)·0,00095 = 3,01625 $ → 0,12198375."""
    fills = [fill(60, "B", 10, 0, 100), fill(120, "A", 15, 10, 110), fill(180, "B", 5, -5, 105)]
    out = run(fills, candles({0: 100}))
    assert out["net"] == pytest.approx((125 - 3.01625) / 1000)


def test_golden_4_candle_gap_marks_fill_missing_and_open_position_is_priced():
    """Mumlar yalnız 0–2. saatte. 00:10 alış → hedef 00:40, 1. saat mumu (100); 01:40 satış → hedef 02:10, sonraki mum yok → eksik.
    Pozisyon açık kalır; pencere sonu (02:00) mum açılışı 104 ile fiyatlanır: net = −10·100·0,00095/1000 + 10·4/1000 = 0,03905."""
    out = run([fill(10, "B", 10, 0, 100), fill(100, "A", 10, 10, 100)], candles({0: 99, 1: 100, 2: 104}), delay=30, end_hours=2)
    assert out["missing"] == 1 and out["executed"] == 1
    assert out["net"] == pytest.approx(0.03905) and out["unrealized_end"] == pytest.approx(0.04)


def test_golden_4b_candle_distance_limit_is_one_interval():
    market = Market(candles({0: 100, 3: 105}))
    assert market.execution("BTC", T0 + 2 * HOUR) == (T0 + 3 * HOUR, 105.0)           # tam 1 mum uzakta: olur
    assert market.execution("BTC", T0 + 2 * HOUR - 1) is None                         # 1 mum aralığı + 1 ms uzakta: eksik
    assert market.execution("BTC", T0 + HOUR + 1) is None
    assert market.execution("BTC", T0 + 4 * HOUR) is None                             # mum yok: eksik


def test_golden_5_open_position_is_marked_daily_and_at_the_end():
    """10:00'da 10 BTC @100. Gün sonu mumu 103, pencere sonu (48. saat) 106. Gün 0: −0,00095 + 10·3/1000 = 0,02905; gün 1: 10·3/1000 = 0,03; toplam 0,05905."""
    prices = {h: 100 for h in range(0, 10)} | {h: 103 for h in range(10, 25)} | {h: 106 for h in range(25, 49)}
    out = run([fill(600, "B", 10, 0, 100)], candles(prices), end_hours=48, daily=True)
    assert out["net"] == pytest.approx(0.05905)
    assert list(out["daily"].round(5)) == [0.02905, 0.03]
    assert out["max_drawdown"] == pytest.approx(0.0)
    # pencere T0 − 1 gün başlar; pozisyon 10:00'da açılır → gün −1: 0, gün 0: 14/24 (10:00–24:00), gün 1: 1
    assert out["exposure"].round(4).tolist() == [0.0, round(14 / 24, 4), 1.0]


def test_golden_6_funding_comes_from_the_copy_position_and_rate_not_from_the_trader_payment():
    """1. saatte 10 BTC alınır, 5. saatte satılır; açılış fiyatı hep 100; saatlik oran 0,0001. Pozisyonlu saatler 1–4: her biri −10·100·0,0001/1000 = −0,0001
    → −0,0004. Maliyet 2·1000·0,00095 = 1,9 $ → −0,0019. Net −0,0023. Trader'ın usdc ödemesi (burada 999) sonucu etkilemez."""
    rows = [{"time": T0 + h * HOUR + 5, "delta": {"coin": "BTC", "usdc": "999", "fundingRate": "0.0001", "szi": "10"}} for h in range(1, 6)]
    out = run([fill(60, "B", 10, 0, 100), fill(300, "A", 10, 10, 100)], candles({h: 100 for h in range(0, 8)}), end_hours=7, funding=FundingRates(rows))
    assert out["funding"] == pytest.approx(-0.0004) and out["net"] == pytest.approx(-0.0023)


def test_golden_7_delay_executes_at_next_candle_open():
    """1:10 alış, 3:10 satış, gecikme 30 dk → 2. saat (101) ve 4. saat (105) açılışları: kâr 10·4 = 40; maliyet (1010+1050)·0,00095 = 1,957 → 0,038043."""
    out = run([fill(70, "B", 10, 0, 100), fill(190, "A", 10, 10, 100)], candles({1: 99, 2: 101, 3: 102, 4: 105, 5: 106}), delay=30, end_hours=6)
    assert out["net"] == pytest.approx((40 - 1.957) / 1000) and out["missing"] == 0


def test_funding_rate_lookup_nearest_then_median():
    rows = [{"time": T0 + h * HOUR, "delta": {"coin": "BTC", "fundingRate": str(r), "usdc": "0"}} for h, r in ((2, 0.0002), (3, 0.0004), (50, 0.0010))]
    rates = FundingRates(rows)
    hours = np.array([T0 + h * HOUR for h in (2, 3, 4, 20, 40)], dtype=np.int64)
    got = rates.array("BTC", hours).tolist()
    assert got[:3] == [0.0002, 0.0004, 0.0004]           # tam saat ve en yakın (≤ 24 sa)
    assert got[3] == 0.0004                               # 20. saat: en yakın 3. saat (17 sa)
    assert got[4] == pytest.approx(0.0010)               # 50. saat 10 sa uzakta
    assert rates.array("ETH", hours).tolist() == [0.0] * 5   # satır yok → 0


def test_daily_curve_drawdown_includes_unrealized_losses():
    """Alış 100, gün sonu 90 (10·(−10)/1000 = −0,10), ertesi gün 100'e döner: eğri 1 → 0,89905 → 0,99905; düşüş 0,10095."""
    prices = {h: 100 for h in range(0, 10)} | {h: 90 for h in range(10, 25)} | {h: 100 for h in range(25, 49)}
    out = run([fill(600, "B", 10, 0, 100)], candles(prices), end_hours=48, daily=True)
    assert out["max_drawdown"] == pytest.approx(0.10095, abs=1e-9)
    assert out["net"] == pytest.approx(-0.00095)
