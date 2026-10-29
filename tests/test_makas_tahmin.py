"""`copytrade/makas_tahmin.py` testleri (Argon A16 sentetik doğrulama ve altın örnekleri; Abdi–Ranaldo özeti ve bozuk mum sayımı düzeltmeleri)."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from copytrade.makas_tahmin import abdi_ranaldo_makas, abdi_ranaldo_s2, coin_makas_ozeti, corwin_schultz, kopya_kaymasi

# ============================================================================
# 1. Sentetik Veri Üreticisi
# ============================================================================

def _sentetik_mum_serisi_uret(
    mum_sayisi: int,
    hedef_makas_bps: float,
    tohum: int,
    dakika_ici_adim: int = 60,
    dakikalik_oynaklik: float = 0.0004,
) -> list[dict[str, object]]:
    """
    Bilinen makas ve rastgele yürüyüş ile sentetik OHLC mumları üretir.

    Model:
        Gerçek verimli fiyat P*_t geometrik Brown hareketi izler.
        Her saat 60 işlem adımı gerçekleşir.
        İşlemler %50 olasılıkla alış (Ask = P* * (1 + s/2))
        ve %50 olasılıkla satış (Bid = P* * (1 - s/2)) olarak gerçekleşir.
        Saatlik Açılış, Yüksek, Düşük ve Kapanış bu gerçekleşen işlem fiyatlarından türetilir.
    """
    rng = np.random.default_rng(tohum)
    s = hedef_makas_bps / 10000.0
    yarim_s = s / 2.0

    p_mid = 1000.0
    baz_zaman_ms = 1700000000000
    mumlar: list[dict[str, object]] = []

    for h in range(mum_sayisi):
        adim_fiyatlari = []
        for _ in range(dakika_ici_adim):
            getiri = rng.normal(0.0, dakikalik_oynaklik)
            p_mid *= math.exp(getiri)

            alis_mi = bool(rng.random() > 0.5)
            p_islem = p_mid * (1.0 + yarim_s) if alis_mi else p_mid * (1.0 - yarim_s)
            adim_fiyatlari.append(p_islem)

        o_px = adim_fiyatlari[0]
        h_px = max(adim_fiyatlari)
        l_px = min(adim_fiyatlari)
        c_px = adim_fiyatlari[-1]
        t_ms = baz_zaman_ms + h * 3600 * 1000

        mumlar.append({
            "t": t_ms,
            "o": f"{o_px:.6f}",
            "h": f"{h_px:.6f}",
            "l": f"{l_px:.6f}",
            "c": f"{c_px:.6f}",
            "v": f"{float(rng.uniform(10.0, 100.0)):.2f}",
            "n": dakika_ici_adim,
        })

    return mumlar



# ============================================================================
# 4. Kayma (Slippage) İçin Elle Hesaplanmış Altın Örnek: Long & Short Simetrisi
# ============================================================================

def test_kopya_kaymasi_altin_ornek_long_ve_short_simetrisi():
    """
    Elle hesaplanmış deterministik altın örnek ile Long ve Short kayma simetrisini doğrular.

    Senaryo:
        Referans fiyat: 100.0, Fiyat farkı: %1 = 100 baz puan (bps)

        1. Alış (B): Trader px = 100.0, Kopya px = 101.0 -> fark = +100.0 bps (Kötü)
        2. Satış (A): Trader px = 100.0, Kopya px = 99.0  -> fark = +100.0 bps (Kötü)
        3. Alış (B): Trader px = 100.0, Kopya px = 99.0   -> fark = -100.0 bps (İyi)
        4. Satış (A): Trader px = 100.0, Kopya px = 101.0 -> fark = -100.0 bps (İyi)
        5. Alış (B): Trader px = 100.0, Kopya px = 100.0 -> fark = 0.0 bps (Nötr)
        6. Satış (A): Trader px = 100.0, Kopya px = 100.0 -> fark = 0.0 bps (Nötr)

    Beklenen İstatistikler:
        - Kayma listesi: [+100, +100, -100, -100, 0, 0]
        - Ortalama: 0.0 bps
        - Medyan: 0.0 bps
        - Yüzde 90'lık dilim: 100.0 bps
        - Kötü oranı: 2 / 6 = 1/3
        - İyi oranı: 2 / 6 = 1/3
        - Nötr oranı: 2 / 6 = 1/3
    """
    mumlar = [
        {"t": 1000000, "o": "101.0", "h": "105.0", "l": "95.0", "c": "101.0", "v": "10", "n": 5},
        {"t": 2000000, "o": "99.0",  "h": "105.0", "l": "95.0", "c": "99.0",  "v": "10", "n": 5},
        {"t": 3000000, "o": "99.0",  "h": "105.0", "l": "95.0", "c": "99.0",  "v": "10", "n": 5},
        {"t": 4000000, "o": "101.0", "h": "105.0", "l": "95.0", "c": "101.0", "v": "10", "n": 5},
        {"t": 5000000, "o": "100.0", "h": "105.0", "l": "95.0", "c": "100.0", "v": "10", "n": 5},
        {"t": 6000000, "o": "100.0", "h": "105.0", "l": "95.0", "c": "100.0", "v": "10", "n": 5},
    ]

    trader_dolumlari = [
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "B", "time": "940000"},   # 1 dk gecikmeyle 1000000 ms mumuna açılır -> 101.0 (+100 bps)
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "A", "time": "1940000"},  # 2000000 ms mumuna açılır -> 99.0 (+100 bps)
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "B", "time": "2940000"},  # 3000000 ms mumuna açılır -> 99.0 (-100 bps)
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "A", "time": "3940000"},  # 4000000 ms mumuna açılır -> 101.0 (-100 bps)
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "B", "time": "4940000"},  # 5000000 ms mumuna açılır -> 100.0 (0 bps)
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "A", "time": "5940000"},  # 6000000 ms mumuna açılır -> 100.0 (0 bps)
    ]

    sonuc = kopya_kaymasi(trader_dolumlari, mumlar, gecikme_dk=1.0)

    assert sonuc["toplam_dolum"] == 6
    assert sonuc["eslesen_dolum"] == 6
    assert sonuc["eslesmeyen_dolum"] == 0

    assert pytest.approx(sonuc["medyan_bps"], abs=1e-5) == 0.0
    assert pytest.approx(sonuc["ortalama_bps"], abs=1e-5) == 0.0
    assert pytest.approx(sonuc["yuzde_90_bps"], abs=1e-5) == 100.0
    assert pytest.approx(sonuc["iyi_orani"], abs=1e-5) == 2.0 / 6.0
    assert pytest.approx(sonuc["kotu_orani"], abs=1e-5) == 2.0 / 6.0
    assert pytest.approx(sonuc["notr_orani"], abs=1e-5) == 2.0 / 6.0




# ============================================================================
# Düzeltilmiş tahmin doğrulamaları ve uç durumlar
# ============================================================================
HEDEFLER = ((50.0, 1500, 42), (0.0, 1000, 123), (20.0, 1500, 7), (100.0, 1500, 9))


@pytest.mark.parametrize("hedef_bps, mum_sayisi, tohum", HEDEFLER)
def test_sentetik_bilinen_makas_duzeltilmis_abdi_ranaldo_ve_corwin_schultz(hedef_bps, mum_sayisi, tohum):
    """Düzeltilmiş AR (özet = sqrt(max(ortalama(s²), 0))) bilinen makasa ±5 bps, Corwin–Schultz medyanı ±15 bps (sıfır kesme yanlılığı) içinde."""
    ozet = coin_makas_ozeti(_sentetik_mum_serisi_uret(mum_sayisi, hedef_bps, tohum), yuzdelikler=[25.0, 50.0, 75.0, 90.0])
    assert ozet["mum_sayisi"] == mum_sayisi and ozet["atlanan_mum"]["toplam"] == 0
    assert abs(ozet["abdi_ranaldo"]["makas_bps"] - hedef_bps) < 5.0, ozet["abdi_ranaldo"]
    assert abs(ozet["corwin_schultz"]["medyan_bps"] - hedef_bps) < (10.0 if hedef_bps == 0 else 15.0)


def test_abdi_ranaldo_ozet_ortalama_s2_uzerinden_karekok_ve_negatifte_sifir():
    """Elle: s² = [1e-8, 3e-8] → ortalama 2e-8 → √ = 1,41421e-4 (1,414 bps). Tek tek √max(s²,0) ortalaması (1e-4 + 1,732e-4)/2 = 1,366e-4 farklıdır.
    Ortalama negatifse özet 0 (eski kod negatif çiftleri 0'a keserek yanlı büyütürdü)."""
    assert abdi_ranaldo_makas(np.array([1e-8, 3e-8])) == pytest.approx(math.sqrt(2e-8))
    assert abdi_ranaldo_makas(np.array([-4e-8, 1e-8])) == 0.0
    assert abdi_ranaldo_makas(np.array([])) is None
    eski = (math.sqrt(1e-8) + math.sqrt(3e-8)) / 2
    assert abs(eski - math.sqrt(2e-8)) > 1e-6                                                  # iki yöntem gerçekten ayrışır


def test_abdi_ranaldo_cift_basina_s2_elle_hesap():
    mumlar = [{"t": 0, "o": "100", "h": "110", "l": "90", "c": "105", "v": "10", "n": 5},
              {"t": 3_600_000, "o": "105", "h": "112", "l": "98", "c": "100", "v": "10", "n": 5}]
    eta1, eta2 = 0.5 * (math.log(110) + math.log(90)), 0.5 * (math.log(112) + math.log(98))
    beklenen = 4.0 * (math.log(105) - eta1) * (math.log(105) - eta2)
    s2 = abdi_ranaldo_s2(mumlar)
    assert len(s2) == 1 and s2.iloc[0] == pytest.approx(beklenen)
    assert coin_makas_ozeti(mumlar, [50.0])["abdi_ranaldo"]["makas_bps"] == pytest.approx(math.sqrt(max(beklenen, 0.0)) * 1e4)


def _saatlik(n: int) -> list[dict]:
    return [{"t": i * 3_600_000, "o": "100", "h": "102", "l": "98", "c": "100.5", "v": "10", "n": 5} for i in range(n)]


def test_bozuk_mumlar_atlanir_sayilir_ve_ardisik_olmayan_cift_kullanilmaz():
    """10 saatlik mumdan #5 bozuk (h<l): atlanır, sayılır; (4,6) çifti ardışık değildir ve kullanılmaz → 9 yerine 7 çift."""
    mumlar = _saatlik(10)
    mumlar[5] = {**mumlar[5], "h": "90", "l": "110"}
    ozet = coin_makas_ozeti(mumlar, yuzdelikler=[50.0])
    assert ozet["atlanan_mum"] == {"bozuk": 1, "sicrama": 0, "hacimsiz": 0, "toplam": 1} and ozet["kullanilan_mum"] == 9
    assert ozet["abdi_ranaldo"]["cift_sayisi"] == 7 and len(corwin_schultz(mumlar)) == 7
    assert len(corwin_schultz(_saatlik(10))) == 9


def test_a15_mum_kontrol_ile_birlesik_sicrama_hacimsiz_ve_sayisal_olmayan_mumlar():
    mumlar = _saatlik(12)
    mumlar[4] = {**mumlar[4], "o": "300", "h": "301", "l": "299", "c": "300"}                    # sıçrama (×3)
    mumlar[7] = {**mumlar[7], "v": "0", "n": 0}                                                  # hacimsiz
    mumlar[9] = {**mumlar[9], "o": "abc"}                                                        # sayısal değil → bozuk
    ozet = coin_makas_ozeti(mumlar, yuzdelikler=[50.0])
    assert ozet["atlanan_mum"] == {"bozuk": 1, "sicrama": 1, "hacimsiz": 1, "toplam": 3} and ozet["kullanilan_mum"] == 9


def test_bozuk_mum_istisna_firlatmaz_gecersiz_dolum_firlatir():
    mumlar = _saatlik(3) + [{"t": 3 * 3_600_000, "o": "100", "h": "90", "l": "95", "c": "92"}, {"t": 4_000_000_000, "o": "x"}]
    assert coin_makas_ozeti(mumlar, [50.0])["atlanan_mum"]["bozuk"] == 2
    with pytest.raises(TypeError):
        coin_makas_ozeti("liste degil", [50.0])  # type: ignore[arg-type]
    gecerli = _saatlik(3)
    with pytest.raises(ValueError, match="geçersiz yön"):
        kopya_kaymasi([{"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "BUY", "time": "500"}], gecerli, gecikme_dk=0)
    with pytest.raises(ValueError, match="pozitif olmalıdır"):
        kopya_kaymasi([{"coin": "BTC", "px": "-10.0", "sz": "1.0", "side": "B", "time": "500"}], gecerli, gecikme_dk=0)


def test_kopya_kaymasi_bozuk_mumu_yurutme_fiyati_yapmaz():
    """Gecikme sonrası ilk mum bozuksa (açılış aralık dışı) atlanır: yürütme fiyatı sonraki geçerli mum açılışı olur."""
    mumlar = _saatlik(4)
    mumlar[1] = {**mumlar[1], "o": "500", "h": "102", "l": "98"}                                   # bozuk (o > h)
    out = kopya_kaymasi([{"coin": "BTC", "px": "100", "sz": "1", "side": "B", "time": str(3_600_000 - 60_000)}], mumlar, gecikme_dk=1)
    assert out["atlanan_mum"]["bozuk"] == 1 and out["medyan_bps"] == pytest.approx(0.0)           # 2. saat mumu (açılış 100) → kayma 0


def test_bos_ve_tek_mum_durumu():
    assert len(corwin_schultz([])) == 0 and len(abdi_ranaldo_s2([])) == 0
    ozet = coin_makas_ozeti([], yuzdelikler=[25.0])
    assert ozet["mum_sayisi"] == 0 and ozet["corwin_schultz"]["medyan_bps"] is None and ozet["abdi_ranaldo"]["makas_bps"] is None
    assert coin_makas_ozeti(_saatlik(1), [50.0])["corwin_schultz"]["medyan_bps"] is None
    assert kopya_kaymasi([], _saatlik(1), gecikme_dk=0)["toplam_dolum"] == 0


def test_parametre_disaridan_gelme_kurali():
    with pytest.raises(TypeError):
        coin_makas_ozeti(_saatlik(3))  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        kopya_kaymasi([{"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "B", "time": "500"}], _saatlik(3))  # type: ignore[call-arg]
    with pytest.raises(ValueError):
        coin_makas_ozeti(_saatlik(3), None)  # type: ignore[arg-type]
