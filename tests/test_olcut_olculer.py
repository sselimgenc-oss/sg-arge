"""Ölçü düzeltmeleri (görev 22): kaldıraç, ters dönüşte ücret, "en iyisiz PF", martingale sırası. Elle hesaplı altın örnekler."""
from __future__ import annotations

import pandas as pd
import pytest

from copytrade.olcut import calculate_metrics, closed_round_trips, effective_leverage, martingale_ratio

H = 3_600_000
T0 = 1_800_000_000_000


def fill(hours, side, size, before, px, pnl=0.0, fee=0.0, oid=None, tid=0, coin="BTC"):
    return {"time": T0 + int(hours * H), "coin": coin, "side": side, "sz": str(size), "startPosition": str(before), "px": str(px),
            "closedPnl": str(pnl), "fee": str(fee), "oid": oid if oid is not None else tid, "tid": tid}


def test_golden_leverage_uses_the_account_value_of_that_moment_and_time_weighted_median():
    """10 BTC @100 (1 sa; hesap 1000 → 1,0x), 10 BTC daha (11 sa; hesap 500 → 2000/500 = 4,0x), tamamı kapanır (31 sa).
    Pozisyon açıkken süreler: 1,0x 10 sa, 4,0x 20 sa → zaman ağırlıklı medyan 4,0x, en yüksek 4,0x.
    Hesap değeri sabit alınırsa (eski hesap): 1000 ile 1x/2x → medyan 2x; 500 ile 2x/4x → medyan 4x; zamana eşleşmiş seriyle 1x/4x."""
    fills = [fill(1, "B", 10, 0, 100, tid=1), fill(11, "B", 10, 10, 100, tid=2), fill(31, "A", 20, 20, 100, tid=3)]
    history = pd.Series([1000.0, 500.0], index=pd.to_datetime([T0, T0 + 10 * H], unit="ms", utc=True))
    assert effective_leverage(fills, history) == (4.0, 4.0)
    assert effective_leverage(fills, 1000.0) == (2.0, 2.0)          # sabit 1000: örnekler 1x (10 sa) ve 2x (20 sa)
    assert effective_leverage(fills, 500.0) == (4.0, 4.0)           # sabit 500: 2x ve 4x → ağırlıklı medyan 4x
    assert effective_leverage(fills, 0.0) == (None, None) and effective_leverage([], 1000.0) == (None, None)


def test_golden_reversal_fee_is_split_by_quantity_between_closing_and_opening_trade():
    """B10@100 ücret 1,0; A15@110 ücret 3,0 closedPnl 100 (10'u kapatır, 5 short açar); B5@105 ücret 0,5 closedPnl 25.
    İşlem 1: −1,0 + (100 − 3,0·10/15) = 97,0.  İşlem 2: −3,0·5/15 + (25 − 0,5) = 23,5 (eski kod: 96,0... tüm ücret kapanana)."""
    fills = [fill(1, "B", 10, 0, 100, 0, 1.0, tid=1), fill(2, "A", 15, 10, 110, 100, 3.0, tid=2), fill(3, "B", 5, -5, 105, 25, 0.5, tid=3)]
    trips = closed_round_trips(fills)
    assert [round(t["net_pnl"], 6) for t in trips] == [97.0, 23.5]
    assert [t["holding_hours"] for t in trips] == [1.0, 1.0]
    first, second = trips
    assert [(f["side"], f["sz"], f["startPosition"]) for f in first["fills"]] == [("B", 10.0, 0.0), ("A", 10.0, 10.0)]
    assert [(f["side"], f["sz"], f["startPosition"]) for f in second["fills"]] == [("A", 5.0, 0.0), ("B", 5.0, -5.0)]


def test_golden_profit_factor_without_best_removes_exactly_one_best_trade():
    """İşlem sonuçları +100, +100, −50, −25: bir en iyi çıkınca (+100 / 75) = 1,3333 (eski hesap iki +100'ü de çıkarıp 0 verirdi)."""
    fills = []
    for index, pnl in enumerate([100, 100, -50, -25]):
        fills += [fill(2 * index, "B", 1, 0, 100, tid=2 * index), fill(2 * index + 1, "A", 1, 1, 100, pnl, tid=2 * index + 1)]
    metrics = calculate_metrics(fills, account_value=10_000)
    assert metrics["profit_factor_without_best"] == pytest.approx(100 / 75)
    assert metrics["largest_trade_share"] == pytest.approx(100 / 200)


def martingale_fills():
    return [fill(1, "B", 1, 0, 100, oid=1, tid=1), fill(2, "B", 1, 1, 97, oid=2, tid=2), fill(3, "B", 1, 2, 98, oid=3, tid=3),
            fill(4, "B", 0.5, 3, 90, oid=4, tid=4), fill(5, "B", 0.5, 3.5, 92, oid=4, tid=5)]


def test_golden_martingale_counts_orders_in_real_sequence_and_measures_against_running_average():
    """Giriş 100. Ekleme 1 (97 → %−3 < %−2: zararda); ortalama 98,5. Ekleme 2 (98 → %−0,5: değil); ortalama 98,333.
    Ekleme 3 tek emir iki dolumla (90 ve 92 → ağırlıklı 91 → %−7,46: zararda). 3 ekleme, 2 zararda → 2/3."""
    ratio, additions = martingale_ratio(martingale_fills(), 0.02)
    assert additions == 3 and ratio == pytest.approx(2 / 3)
    shuffled = list(reversed(martingale_fills()))
    assert martingale_ratio(shuffled, 0.02) == (ratio, additions)     # girdi sırası sonucu değiştirmez: zaman/tid sırası


def test_golden_leverage_unsorted_same_timestamp_fills_regression_for_indexerror():
    """Canlı koşuda 18 parçayı çökerten hata (0x67870e07…cb04, 16 coin, 13.978 dolum): sırasız ve aynı milisaniyeli dolumlar süre dizisini
    bozup searchsorted'ı sona taşıyordu (IndexError). Küçültülmüş hali (eski kodda çöker): girdi sırası 2. saat, 1. saat, 1. saat.
    Zamana göre sıralı: 1. saat A2 satış (miras pozisyon 2 → 0, 0x), 1. saat B1 (0,1x), 2. saat B2 (pozisyon 2 → 0,2x), hesap 1000.
    Süreler: 0 sn ve 1 sa (son örnek dışlanır) → yalnız 0,1x ağırlık taşır: medyan 0,1x, en yüksek 0,2x."""
    fills = [fill(2, "B", 2, 0, 100, tid=1), fill(1, "A", 2, 2, 100, tid=2), fill(1, "B", 1, 0, 100, tid=3)]
    median, top = effective_leverage(fills, 1000.0)
    assert (round(median, 6), round(top, 6)) == (0.1, 0.2)


def test_leverage_survives_nan_price_and_all_zero_weights():
    fills = [fill(1, "B", 5, 0, "nan", tid=1), fill(2, "A", 5, 5, 100, tid=2)]
    median, top = effective_leverage(fills, 1000.0)
    assert median is not None and top is not None
    same_instant = [fill(1, "B", 5, 0, 100, tid=1), fill(1, "A", 5, 5, 100, tid=2)]
    assert effective_leverage(same_instant, 1000.0)[0] is not None
