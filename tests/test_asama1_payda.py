"""1. aşama payda düzeltmesi (görev 15): düşüş/getiri/calmar zaman ağırlıklı getiri zincirinden; elle hesaplı örnekler."""
from __future__ import annotations

import pytest

from copytrade.kapi import stage1_stats

DAY_MS = 86_400_000
T0 = 1_700_000_000_000


def portfolio(pnl, values, step_days=30):
    return [["allTime", {"pnlHistory": [[T0 + i * step_days * DAY_MS, str(v)] for i, v in enumerate(pnl)],
                         "accountValueHistory": [[T0 + i * step_days * DAY_MS, str(v)] for i, v in enumerate(values)]}]]


def test_golden_steady_gains_chain_to_thirty_percent_without_drawdown():
    """Hesap 1000'den 100'er artar: dönem getirileri 100/1000, 100/1100, 100/1200 → 1,1 · 1,2/1,1 · 1,3/1,2 = 1,30 (elle)."""
    stats = stage1_stats(portfolio([0, 100, 200, 300], [1000, 1100, 1200, 1300]))
    assert stats["return_12m"] == pytest.approx(0.30) and stats["max_drawdown"] == pytest.approx(0.0)
    assert stats["calmar"] is None                      # düşüş yok → calmar tanımsız (eski sürüm 10^13 üretiyordu)


def test_golden_deposit_is_not_a_return():
    """İkinci dönemde 500 $ yatırılır (PnL değişmez): o dönem getirisi 0; toplam yalnız ilk ve son dönemden gelir."""
    with_deposit = stage1_stats(portfolio([0, 100, 100, 200], [1000, 1100, 1600, 1700]))
    # dönem 1: 100/1000 = %10; dönem 2: PnL 0 → %0; dönem 3: 100 / (1600 + 0) = %6,25 → 1,1 · 1,0625 = 1,16875
    assert with_deposit["return_12m"] == pytest.approx(1.1 * 1.0625 - 1)
    assert with_deposit["max_drawdown"] == pytest.approx(0.0)


def test_golden_withdrawal_is_not_a_loss():
    """Dönem 2'de 600 $ çekilir (PnL +50): hesap 1100 → 550; net akış = (550 − 1100) − 50 = −600; sermaye = 1100 − 300 = 800; getiri 50/800."""
    stats = stage1_stats(portfolio([0, 100, 150], [1000, 1100, 550]))
    assert stats["return_12m"] == pytest.approx(1.1 * (1 + 50 / 800) - 1) and stats["max_drawdown"] == pytest.approx(0.0)


def test_golden_losses_give_bounded_drawdown_and_calmar():
    """PnL 0, −100, −300; hesap 1000, 900, 700: getiriler −0,1 ve −200/900 → eğri 0,9 · 0,7778 = 0,70; düşüş 0,30 (0–1)."""
    stats = stage1_stats(portfolio([0, -100, -300], [1000, 900, 700]))
    assert stats["max_drawdown"] == pytest.approx(0.30) and stats["return_12m"] == pytest.approx(-0.30)
    assert stats["calmar"] == pytest.approx((0.7 ** (365.25 / 60) - 1) / 0.30)      # 60 günlük pencere


def test_impossible_values_of_the_old_denominator_cannot_occur():
    """Denetimdeki hata: PnL / medyan hesap değeri → düşüş 1,5e12. Yeni zincirde düşüş ∈ [0,1], getiri ≥ −1, hepsi sonlu."""
    pnl = [0, 50_000, -2_000_000, 10_000, 20_000, 1_000_000]
    values = [100, 1_000_000, 80, 5_000_000, 3, 900_000]            # uç yatırma/çekme ve neredeyse boş hesap
    stats = stage1_stats(portfolio(pnl, values))
    assert 0.0 <= stats["max_drawdown"] <= 1.0 and stats["return_12m"] >= -1.0
    assert stats["calmar"] is None or abs(stats["calmar"]) < 1e6
