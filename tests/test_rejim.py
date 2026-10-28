"""test_rejim.py - rejim.py modülü için birim testler.

Testler pytest uyumludur ve her test için elle hesaplanan altın örnekler
yorum satırı olarak detaylıca açıklanmıştır.

Test Senaryoları:
(1) Düz artan seri -> beklenen etiketler ('yukselis')
(2) Sabit seri -> 'yatay'
(3) Tek günlük büyük sıçrama -> 'sok' (şok önceliği)
(4) Geçmiş yetersizken -> None
(5) Geleceğe bakmama (no look-ahead bias): sonradan gün eklenmesi eski etiketleri değiştirmez.
(+) rejim_ozeti fonksiyonunun metrik doğruluk testi.
"""

import numpy as np
import pandas as pd
from copytrade.rejim import rejim_etiketle, rejim_ozeti


def test_1_duz_artan_seri():
    """Test 1: Düz artan seri -> beklenen 'yukselis' etiketleri.

    ELLE HESAPLAMA:
    ----------------
    Parametreler:
      pencere_gun = 2
      getiri_esik = 0.10 (%10)
      sok_yuzdelik = 0.80 (%80)
      yuzdelik_pencere_gun = 2

    Fiyat serisi (6 gün, UTC):
      t0 (2024-01-01): 100.0
      t1 (2024-01-02): 110.0
      t2 (2024-01-03): 120.0
      t3 (2024-01-04): 130.0
      t4 (2024-01-05): 140.0
      t5 (2024-01-06): 150.0

    Günlük log getiriler:
      r_1 = ln(110/100) = ln(1.10)       ≈ 0.095310
      r_2 = ln(120/110) = ln(1.090909)   ≈ 0.087011
      r_3 = ln(130/120) = ln(1.083333)   ≈ 0.080043
      r_4 = ln(140/130) = ln(1.076923)   ≈ 0.074108
      r_5 = ln(150/140) = ln(1.071429)   ≈ 0.068993

    Pencere oynaklığı (pencere_gun=2, log getirilerin örneklem standart sapması):
      std([r_a, r_b]) = |r_a - r_b| / sqrt(2)
      t0, t1: NaN (yetersiz veri)
      t2: std([r_1, r_2]) = |0.095310 - 0.087011| / 1.414214 ≈ 0.005868
      t3: std([r_2, r_3]) = |0.087011 - 0.080043| / 1.414214 ≈ 0.004928
      t4: std([r_3, r_4]) = |0.080043 - 0.074108| / 1.414214 ≈ 0.004196
      t5: std([r_4, r_5]) = |0.074108 - 0.068993| / 1.414214 ≈ 0.003617

    Oynaklık eşiği (yuzdelik_pencere_gun=2, sok_yuzdelik=0.80):
      t0, t1, t2: NaN (en az 2 geçerli oynaklık değeri gerekir)
      t3: quantile([0.005868, 0.004928], 0.80) ≈ 0.005680
          oynaklık(t3) = 0.004928 < 0.005680 -> Şok DEĞİL.
          Getiri(t3) = 130/110 - 1 = 0.1818 (%18.18) > getiri_esik(0.10) -> 'yukselis'
      t4: quantile([0.004928, 0.004196], 0.80) ≈ 0.004781
          oynaklık(t4) = 0.004196 < 0.004781 -> Şok DEĞİL.
          Getiri(t4) = 140/120 - 1 = 0.1667 (%16.67) > getiri_esik(0.10) -> 'yukselis'
      t5: quantile([0.004196, 0.003617], 0.80) ≈ 0.004081
          oynaklık(t5) = 0.003617 < 0.004081 -> Şok DEĞİL.
          Getiri(t5) = 150/130 - 1 = 0.1538 (%15.38) > getiri_esik(0.10) -> 'yukselis'

    Beklenen etiketler: [None, None, None, 'yukselis', 'yukselis', 'yukselis']
    """
    tarihler = pd.date_range("2024-01-01", periods=6, freq="D", tz="UTC")
    kapanis = pd.Series([100.0, 110.0, 120.0, 130.0, 140.0, 150.0], index=tarihler)

    etiketler = rejim_etiketle(
        kapanis=kapanis,
        pencere_gun=2,
        getiri_esik=0.10,
        sok_yuzdelik=0.80,
        yuzdelik_pencere_gun=2,
    )

    beklenen = pd.Series(
        [None, None, None, "yukselis", "yukselis", "yukselis"],
        index=tarihler,
        dtype=object,
    )
    pd.testing.assert_series_equal(etiketler, beklenen)


def test_2_sabit_seri():
    """Test 2: Sabit seri -> 'yatay'.

    ELLE HESAPLAMA:
    ----------------
    Parametreler:
      pencere_gun = 2
      getiri_esik = 0.05 (%5)
      sok_yuzdelik = 0.80
      yuzdelik_pencere_gun = 2

    Fiyat serisi (5 gün, UTC):
      t0..t4: 100.0

    Tüm günler arası getiri:
      r_t = ln(100/100) = 0.0
      Pencere oynaklığı = std([0.0, 0.0]) = 0.0
      Oynaklık eşiği = quantile([0.0, 0.0], 0.80) = 0.0
      Şok kontrolü: 0.0 > 0.0 -> False (Şok değil)
      Pencere getirisi: 100/100 - 1 = 0.0
      Getiri kontrolü:
        0.0 > 0.05 -> False
        0.0 < -0.05 -> False
        Aralıkta -> 'yatay'

    Beklenen etiketler:
      t0, t1, t2: None (yetersiz geçmiş)
      t3: 'yatay'
      t4: 'yatay'
    """
    tarihler = pd.date_range("2024-01-01", periods=5, freq="D", tz="UTC")
    kapanis = pd.Series([100.0] * 5, index=tarihler)

    etiketler = rejim_etiketle(
        kapanis=kapanis,
        pencere_gun=2,
        getiri_esik=0.05,
        sok_yuzdelik=0.80,
        yuzdelik_pencere_gun=2,
    )

    beklenen = pd.Series(
        [None, None, None, "yatay", "yatay"], index=tarihler, dtype=object
    )
    pd.testing.assert_series_equal(etiketler, beklenen)


def test_3_tek_gunluk_buyuk_sicrama():
    """Test 3: Tek günlük büyük sıçrama -> 'sok' (şok önceliği).

    ELLE HESAPLAMA:
    ----------------
    Parametreler:
      pencere_gun = 2
      getiri_esik = 0.10 (%10)
      sok_yuzdelik = 0.80 (%80)
      yuzdelik_pencere_gun = 3

    Fiyat serisi (8 gün, UTC):
      t0..t4: 100.0
      t5: 200.0  <- tek günde %100 sıçrama
      t6..t7: 200.0

    Günlük log getiriler:
      r_1 = ln(100/100) = 0.0
      r_2 = ln(100/100) = 0.0
      r_3 = ln(100/100) = 0.0
      r_4 = ln(100/100) = 0.0
      r_5 = ln(200/100) = ln(2) ≈ 0.693147
      r_6 = ln(200/200) = 0.0
      r_7 = ln(200/200) = 0.0

    Pencere oynaklığı (pencere_gun=2):
      t2: std([r_1, r_2]) = std([0, 0]) = 0.0
      t3: std([r_2, r_3]) = std([0, 0]) = 0.0
      t4: std([r_3, r_4]) = std([0, 0]) = 0.0
      t5: std([r_4, r_5]) = std([0, ln(2)]) = ln(2) / sqrt(2) ≈ 0.490129
      t6: std([r_5, r_6]) = std([ln(2), 0]) = ln(2) / sqrt(2) ≈ 0.490129
      t7: std([r_6, r_7]) = std([0, 0]) = 0.0

    Oynaklık eşiği (yuzdelik_pencere_gun=3, sok_yuzdelik=0.80):
      t0..t3: NaN (yetersiz geçmiş)
      t4: quantile([0, 0, 0], 0.80) = 0.0
          oynaklık(t4) = 0.0 > 0.0 -> False, getiri(t4) = 0.0 -> 'yatay'
      t5: quantile([0.0, 0.0, 0.490129], 0.80)
          3 elemanlı dizide 0.80 yüzdeliği (linear):
          indeks = (3 - 1) * 0.80 = 1.6 -> 0.0 + 0.6 * (0.490129 - 0.0) ≈ 0.294077
          oynaklık(t5) = 0.490129 > 0.294077 -> TRUE! -> 'sok'
          (Not: t5 2 günlük getiri 200/100 - 1 = %100 > getiri_esik olmasına rağmen
           şok kuralı öncelikli olduğundan 'sok' etiketi atanır).

    Beklenen etiketler (t0..t5):
      t0..t3: None
      t4: 'yatay'
      t5: 'sok'
    """
    tarihler = pd.date_range("2024-01-01", periods=8, freq="D", tz="UTC")
    kapanis = pd.Series(
        [100.0, 100.0, 100.0, 100.0, 100.0, 200.0, 200.0, 200.0],
        index=tarihler,
    )

    etiketler = rejim_etiketle(
        kapanis=kapanis,
        pencere_gun=2,
        getiri_esik=0.10,
        sok_yuzdelik=0.80,
        yuzdelik_pencere_gun=3,
    )

    assert etiketler.iloc[4] == "yatay"
    assert etiketler.iloc[5] == "sok"


def test_4_gecmis_yetersizken_none():
    """Test 4: Yeterli geçmiş yoksa etiket None olmalıdır.

    ELLE HESAPLAMA:
    ----------------
    Gereken geçmiş gün sayısı:
      - 1 log getiri için 2 fiyat gerekir.
      - pencere_gun adet log getiri için (pencere_gun + 1) fiyat gerekir.
      - İlk oynaklık değeri indeksi: pencere_gun.
      - yuzdelik_pencere_gun adet oynaklık değeri için toplamda:
        pencere_gun + yuzdelik_pencere_gun fiyat gözlemi gerekir.
      - Eğer serideki gün sayısı < (pencere_gun + yuzdelik_pencere_gun) ise,
        hiçbir gün için oynaklık eşiği hesaplanamaz ve tüm değerler None olmalıdır.

    Örnek:
      pencere_gun = 3
      yuzdelik_pencere_gun = 4
      Gereken minimum gün sayısı = 3 + 4 = 7
      Seri uzunluğu: 6 gün (t0..t5)
      Sonuç: Tüm 6 günün etiketi None olmalıdır.
    """
    tarihler = pd.date_range("2024-01-01", periods=6, freq="D", tz="UTC")
    kapanis = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0, 105.0], index=tarihler)

    etiketler = rejim_etiketle(
        kapanis=kapanis,
        pencere_gun=3,
        getiri_esik=0.05,
        sok_yuzdelik=0.90,
        yuzdelik_pencere_gun=4,
    )

    assert len(etiketler) == 6
    assert etiketler.isna().all()
    for val in etiketler:
        assert val is None


def test_5_gelecege_bakmama():
    """Test 5: Geleceğe bakmama (no look-ahead bias).

    ELLE HESAPLAMA:
    ----------------
    Pencere hesapları yalnızca geriye dönük rolling() ile yapıldığından,
    zaman serisinin sonuna yeni günler (t10..t14) eklendiğinde,
    önceden hesaplanmış geçmiş günlerin (t0..t9) etiketleri KESİNLİKLE değişmemelidir.

    Örnek:
      İlk seri: 10 gün
      Genişletilmiş seri: 15 gün
      İlk 10 günün etiketleri iki hesaplamada birebir özdeş olmalıdır.
    """
    tarihler = pd.date_range("2024-01-01", periods=15, freq="D", tz="UTC")
    fiyatlar = [
        100.0, 102.0, 101.0, 105.0, 110.0,
        108.0, 115.0, 120.0, 118.0, 125.0,
        140.0, 135.0, 150.0, 160.0, 155.0,
    ]
    kapanis_tam = pd.Series(fiyatlar, index=tarihler)

    etiketler_kisa = rejim_etiketle(
        kapanis=kapanis_tam.iloc[:10],
        pencere_gun=2,
        getiri_esik=0.05,
        sok_yuzdelik=0.80,
        yuzdelik_pencere_gun=3,
    )

    etiketler_uzun = rejim_etiketle(
        kapanis=kapanis_tam,
        pencere_gun=2,
        getiri_esik=0.05,
        sok_yuzdelik=0.80,
        yuzdelik_pencere_gun=3,
    )

    pd.testing.assert_series_equal(etiketler_kisa, etiketler_uzun.iloc[:10])


def test_rejim_ozeti():
    """Ek Test: rejim_ozeti fonksiyonunun metrik doğruluk testi.

    ELLE HESAPLAMA:
    ----------------
    Verilen etiketler:
      ['yukselis', 'yukselis', 'yatay', 'dusus', 'sok', None]
    Verilen getiriler:
      [0.02, 0.04, 0.00, -0.03, -0.10, 0.05]

    Grup bazlı hesaplama:
      - 'yukselis':
          Gün sayısı: 2
          Ortalama: (0.02 + 0.04) / 2 = 0.03
          Medyan: 0.03
      - 'yatay':
          Gün sayısı: 1
          Ortalama: 0.00
          Medyan: 0.00
      - 'dusus':
          Gün sayısı: 1
          Ortalama: -0.03
          Medyan: -0.03
      - 'sok':
          Gün sayısı: 1
          Ortalama: -0.10
          Medyan: -0.10
      - None satırı elenir.
    """
    etiket = pd.Series(["yukselis", "yukselis", "yatay", "dusus", "sok", None])
    getiri = pd.Series([0.02, 0.04, 0.00, -0.03, -0.10, 0.05])

    ozet = rejim_ozeti(etiket, getiri)

    assert ozet.loc["yukselis", "gun_sayisi"] == 2
    assert np.isclose(ozet.loc["yukselis", "ortalama"], 0.03)
    assert np.isclose(ozet.loc["yukselis", "medyan"], 0.03)

    assert ozet.loc["yatay", "gun_sayisi"] == 1
    assert np.isclose(ozet.loc["yatay", "ortalama"], 0.00)
    assert np.isclose(ozet.loc["yatay", "medyan"], 0.00)

    assert ozet.loc["dusus", "gun_sayisi"] == 1
    assert np.isclose(ozet.loc["dusus", "ortalama"], -0.03)
    assert np.isclose(ozet.loc["dusus", "medyan"], -0.03)

    assert ozet.loc["sok", "gun_sayisi"] == 1
    assert np.isclose(ozet.loc["sok", "ortalama"], -0.10)
    assert np.isclose(ozet.loc["sok", "medyan"], -0.10)

    assert None not in ozet.index


def test_bosluklu_seri_reddedilir():
    """Lider eki: eksik gün varsa pencereler satırla kayacağı için hata verilir."""
    import pytest
    tarihler = pd.date_range("2024-01-01", periods=6, freq="D", tz="UTC").delete(3)
    with pytest.raises(ValueError):
        rejim_etiketle(pd.Series(range(100, 105), index=tarihler, dtype=float), 2, 0.1, 0.8, 2)


if __name__ == "__main__":
    test_1_duz_artan_seri()
    test_2_sabit_seri()
    test_3_tek_gunluk_buyuk_sicrama()
    test_4_gecmis_yetersizken_none()
    test_5_gelecege_bakmama()
    test_rejim_ozeti()
    print("Tüm testler başarıyla geçti (6/6).")