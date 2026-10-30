"""E2 sabit tutar altın örnekleri (kullanıcı kararı 2026-10-30: "Etre eğrisini enterpolasyonla port et").

Kaynak: etre-trading-office etre2/kasa.py (Kasa.islem_usd) + etre2/ayar.py varsayılanları (GPL-3.0). Burada,
``copy_ledger``'a ``tutar_egrisi`` verildiğinde: açılış kopya hesabının KENDİ değerine göre sabit $ tutarla (trader
hesabına ORANLI değil); ekleme mevcut kopya pozisyonuna trader'ın oranı kadar (Etre `masa.py _ekle`); azaltma/kapatma
değişmedi (defterin ortak kuralı, ayrı test gerekmez).

Ortak kurallar: maliyet = %0,045 taker + %0,05 kayma = %0,095 (her dolumde, notional'a oranla); base_usd = 1.000 $.
"""
from __future__ import annotations

import pytest

from copytrade.defter import DAY, HOUR, Market, copy_ledger, sabit_tutar_egrisi
from copytrade.kurallar import load_rules

T0 = 20_833 * DAY
C = 0.00095
BASE = 1000.0
RULES = load_rules()


def candles(prices: dict[int, float], coin="BTC"):
    return {coin: [{"t": T0 + h * HOUR, "o": str(p), "c": str(p)} for h, p in sorted(prices.items())]}


def fill(minutes, side, size, before, px=0.0, coin="BTC"):
    return {"time": T0 + minutes * 60_000, "coin": coin, "side": side, "sz": str(size), "startPosition": str(before), "px": str(px)}


def run(fills, market, tutar, end_hours=24):
    return copy_ledger(fills, Market(market), 1.0, 0, T0 - DAY, T0 + end_hours * HOUR, None, RULES, False,
                       tutar_egrisi=tutar, base_usd=BASE)


def test_sabit_tutar_egrisi_etre_varsayilanlariyla_eslesir():
    """kasa.py Kasa.islem_usd portu: tutar_usd = ref_islem × (clamp(hesap,1,tavan)/ref_kasa) ** us (DEĞİŞTİRİLMEDİ)."""
    f = sabit_tutar_egrisi(RULES)
    assert f(200.0) == pytest.approx(5.2)                      # ref noktası, tam
    assert f(1000.0) == pytest.approx(5.2 * 5.0 ** 0.86)        # ~20,75$ (KULLANIM.md: ~20,7$)
    assert f(10_000.0) == pytest.approx(5.2 * 50.0 ** 0.86)     # ~150,35$ (KULLANIM.md: ~150$)
    assert f(50_000.0) == f(10_000.0)                            # tavan: fazlası büyütmez
    assert f(0.0) == f(1.0)                                      # taban: hesap ≤ 0 ise 1$ gibi okunur (bölme hatası yok)


def test_acilis_sabit_tutarla_trader_islem_buyuklugunden_bagimsiz():
    """İki ayrı trader aynı anda açıyor: biri 10 BTC, öteki 3 BTC — ikisinin kopyası da AYNI $50 tutarla açılır
    (v1/v2'nin oranlı kopyasından fark: trader'ın kendi işlem büyüklüğü artık kopya boyutunu etkilemiyor)."""
    tutar = lambda hesap: 50.0  # noqa: E731 — sabit, hesaba bakmaz (eğrinin kendisi ayrı testte)
    buyuk = run([fill(0, "A", 10, 0, px=100)], candles({0: 100, 24: 100}), tutar)
    kucuk = run([fill(0, "A", 3, 0, px=100)], candles({0: 100, 24: 100}), tutar)
    # own (normalize) = sign*(50/100)/1000 = 0,0005; fiyat sabit kaldığından gerçekleşmemiş K/Z = 0; maliyet = 0,0005*100*0,00095
    beklenen_maliyet = 0.0005 * 100 * C
    assert buyuk["net"] == pytest.approx(-beklenen_maliyet)
    assert kucuk["net"] == pytest.approx(-beklenen_maliyet)
    assert buyuk["net"] == pytest.approx(kucuk["net"])
    assert buyuk["executed"] == 1 and buyuk["missing"] == 0


def test_ekleme_mevcut_kopya_pozisyonuna_oranla_acilis_egriye_degil():
    """Açılış (B10@100) sabit $50; trader %50 artırınca (B5 ek, before=10) kopya da KENDİ pozisyonunun %50'si kadar
    eklenir (Etre masa.py _ekle), eğriden yeniden okunmaz. Ağırlıklı ortalama giriş: (100×0,0005+110×0,00025)/0,00075."""
    tutar = lambda hesap: 50.0  # noqa: E731
    out = run([fill(0, "B", 10, 0, px=100), fill(60, "B", 5, 10, px=110)],
              candles({0: 100, 1: 110, 24: 110}), tutar)
    own_acilis = 0.0005
    ek = own_acilis * 0.5
    after = own_acilis + ek
    entry = (100 * own_acilis + 110 * ek) / after
    maliyet_acilis = own_acilis * 100 * C
    maliyet_ekleme = ek * 110 * C
    # pencere sonunda mark=110=entry'nin üstünde: gerçekleşmemiş K/Z = after*(110-entry)
    gerceklesmemis = after * (110 - entry)
    beklenen = -(maliyet_acilis + maliyet_ekleme) + gerceklesmemis
    assert out["net"] == pytest.approx(beklenen)
    assert out["executed"] == 2


def test_flip_kapanan_kisim_oranli_yeni_yon_egriyle_acilir():
    """B10@100 açılış ($50 sabit) sonra trader flip yapıyor: A15@110 (before=10 → −5). Kapanan 10'un tamamı kopyanın
    mevcut pozisyonunu kapatır (oranlı, değişmedi); kalan 5'lik fazla YENİ bir açılıştır — eğriyle (sabit $50, kapanıştan
    SONRAKİ hesap değerine göre, ama hesap burada sabit döndüğü için yine $50) kısa taraf açılır."""
    tutar = lambda hesap: 50.0  # noqa: E731
    out = run([fill(0, "B", 10, 0, px=100), fill(60, "A", 15, 10, px=110)],
              candles({0: 100, 1: 110, 24: 110}), tutar)
    own = 0.0005                       # açılış
    maliyet_acilis = own * 100 * C
    opened = -1 * (50.0 / 110.0) / BASE         # flip'in yeni (kısa) tarafı, eğriyle
    close = own                                  # kapanan kısım tam
    signed_flip = -close + opened
    after = own + signed_flip
    pnl_kapanis = close * (110 - 100) * 1.0      # uzun kapanıyor, kâr
    maliyet_flip = abs(signed_flip) * 110 * C
    # pencere sonunda mark=110=yeni girişin (110) kendisi: gerçekleşmemiş K/Z = 0
    beklenen = pnl_kapanis - maliyet_acilis - maliyet_flip
    assert out["net"] == pytest.approx(beklenen)
    assert after < 0                              # kısa tarafa geçti


def test_hesaplanamadi_donusu_sabit_tutar_modunda_hesaba_bakmaz():
    """Sabit tutar modunda ``account`` okunmaz (kopyanın KENDİ değeri kullanılır); geçersiz/None account bile çalışır."""
    out = copy_ledger([fill(0, "B", 10, 0, px=100)], Market(candles({0: 100, 24: 100})), None, 0,
                      T0 - DAY, T0 + 24 * HOUR, None, RULES, False, tutar_egrisi=lambda h: 50.0, base_usd=BASE)
    assert out["net"] is not None
