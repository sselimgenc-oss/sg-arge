"""Test Modülü: test_kalicilik.py

kalicilik.py içerisindeki Spearman korelasyonu, pencere bazlı kalıcılık ve
hareketli blok bootstrap fonksiyonlarının doğrulamalarını içerir.

Tüm testler elle hesaplanmış beklenen değerleri ve adım adım türetimleri
yorum olarak içerir.
"""

import math
import numpy as np
import pandas as pd
from copytrade.kalicilik import spearman, pencere_kaliciligi, blok_bootstrap_ortalama


def test_1_spearman_altin_ornek_esitlik_dahil():
  """Test 1: Elle hesaplı 5 elemanlı Spearman (eşitlik dahil) altın örneği.

  ELLE HESAPLAMA ADIMLARI:
  -------------------------------------------------------------------------
  Girdi Serileri (n = 5):
    x = [10.0, 20.0, 20.0, 40.0, 50.0]
    y = [10.0, 30.0, 30.0, 20.0, 50.0]

  Adım 1: Sıraların Belirlenmesi (Eşit Değerlerde Ortalama Sıra):
    x serisi sıraları:
      10.0 -> En küçük değer, sıra: 1
      20.0, 20.0 -> 2. ve 3. sıralar paylaşılıyor; ortalama = (2 + 3) / 2 = 2.5
      40.0 -> Sıra: 4
      50.0 -> Sıra: 5
      rx = [1.0, 2.5, 2.5, 4.0, 5.0]
      rx_ort = (1.0 + 2.5 + 2.5 + 4.0 + 5.0) / 5 = 15.0 / 5 = 3.0

    y serisi sıraları:
      10.0 -> Sıra: 1
      20.0 -> Sıra: 2
      30.0, 30.0 -> 3. ve 4. sıralar paylaşılıyor; ortalama = (3 + 4) / 2 = 3.5
      50.0 -> Sıra: 5
      ry = [1.0, 3.5, 3.5, 2.0, 5.0]
      ry_ort = (1.0 + 3.5 + 3.5 + 2.0 + 5.0) / 5 = 15.0 / 5 = 3.0

  Adım 2: Ortalamadan Farklar (dx = rx - 3.0, dy = ry - 3.0):
    dx = [1.0 - 3.0, 2.5 - 3.0, 2.5 - 3.0, 4.0 - 3.0, 5.0 - 3.0]
       = [-2.0, -0.5, -0.5, 1.0, 2.0]
    dy = [1.0 - 3.0, 3.5 - 3.0, 3.5 - 3.0, 2.0 - 3.0, 5.0 - 3.0]
       = [-2.0, 0.5, 0.5, -1.0, 2.0]

  Adım 3: Kareler Toplamı:
    sum(dx^2) = (-2.0)^2 + (-0.5)^2 + (-0.5)^2 + (1.0)^2 + (2.0)^2
              = 4.0 + 0.25 + 0.25 + 1.0 + 4.0 = 9.5
    sum(dy^2) = (-2.0)^2 + (0.5)^2 + (0.5)^2 + (-1.0)^2 + (2.0)^2
              = 4.0 + 0.25 + 0.25 + 1.0 + 4.0 = 9.5

  Adım 4: Çapraz Çarpımlar Toplamı (Kovaryans Payı):
    sum(dx * dy) = (-2.0)*(-2.0) + (-0.5)*(0.5) + (-0.5)*(0.5) + (1.0)*(-1.0) +
    (2.0)*(2.0)
                 = 4.0 - 0.25 - 0.25 - 1.0 + 4.0 = 6.5

  Adım 5: Spearman Sıra Korelasyonu (Sıraların Pearson Korelasyonu):
    r = sum(dx * dy) / sqrt(sum(dx^2) * sum(dy^2))
      = 6.5 / sqrt(9.5 * 9.5) = 6.5 / 9.5 = 13 / 19
      = 0.6842105263157895
  -------------------------------------------------------------------------
  """
  x = pd.Series(
      [10.0, 20.0, 20.0, 40.0, 50.0], index=["t1", "t2", "t3", "t4", "t5"]
  )
  y = pd.Series(
      [10.0, 30.0, 30.0, 20.0, 50.0], index=["t1", "t2", "t3", "t4", "t5"]
  )

  sonuc = spearman(x, y)
  beklenen = 13.0 / 19.0

  assert math.isclose(
      sonuc, beklenen, rel_tol=1e-12
  ), f"Test 1 Başarısız: beklenen={beklenen}, hesaplanan={sonuc}"


def test_2_spearman_tam_ters_sira():
  """Test 2: Tam ters sırada Spearman korelasyonunun -1 dönmesi.

  ELLE HESAPLAMA ADIMLARI:
  -------------------------------------------------------------------------
  Girdi Serileri (n = 4):
    x = [10.0, 20.0, 30.0, 40.0]
    y = [400.0, 300.0, 200.0, 100.0]

  Adım 1: Sıralar:
    rx = [1.0, 2.0, 3.0, 4.0], rx_ort = 2.5
    ry = [4.0, 3.0, 2.0, 1.0], ry_ort = 2.5

  Adım 2: Sapmalar:
    dx = [-1.5, -0.5,  0.5,  1.5]
    dy = [ 1.5,  0.5, -0.5, -1.5]
    Burada her i için dy_i = -dx_i geçerlidir.

  Adım 3: Kareler ve Çarpımlar:
    sum(dx^2) = (-1.5)^2 + (-0.5)^2 + 0.5^2 + 1.5^2 = 2.25 + 0.25 + 0.25 + 2.25
    = 5.0
    sum(dy^2) = 1.5^2 + 0.5^2 + (-0.5)^2 + (-1.5)^2 = 2.25 + 0.25 + 0.25 + 2.25
    = 5.0
    sum(dx * dy) = (-1.5)*(1.5) + (-0.5)*(0.5) + (0.5)*(-0.5) + (1.5)*(-1.5)
                 = -2.25 - 0.25 - 0.25 - 2.25 = -5.0

  Adım 4: Spearman Korelasyonu:
    r = sum(dx * dy) / sqrt(sum(dx^2) * sum(dy^2))
      = -5.0 / sqrt(5.0 * 5.0) = -5.0 / 5.0 = -1.0
  -------------------------------------------------------------------------
  """
  x = pd.Series([10.0, 20.0, 30.0, 40.0])
  y = pd.Series([400.0, 300.0, 200.0, 100.0])

  sonuc = spearman(x, y)
  beklenen = -1.0

  assert math.isclose(
      sonuc, beklenen, rel_tol=1e-12
  ), f"Test 2 Başarısız: beklenen={beklenen}, hesaplanan={sonuc}"


def test_3_ortak_adres_kucuktur_uc_nan_doner():
  """Test 3: Ortak adres sayısı < 3 olan pencere için Spearman'ın NaN dönmesi.

  ELLE HESAPLAMA ADIMLARI:
  -------------------------------------------------------------------------
  Pencereler: '2026-01-01' (1. Pencere) ve '2026-01-15' (2. Pencere)
  Trader Havuzu: ['t1', 't2', 't3', 't4']

  1. Pencere ('2026-01-01'):
    puan satırı:   [10.0, 20.0,  NaN,  NaN]
    getiri satırı: [ 0.1,  0.2,  0.3,  NaN]
    Her iki tabloda da geçerli (NaN olmayan) ortak adresler:
      't1' -> puan=10.0, getiri=0.1
      't2' -> puan=20.0, getiri=0.2
      (t3 ve t4 en az birinde eksiktir)
    Ortak geçerli adres sayısı: n = 2.
    Kural gereği: n < 3 olan pencerelerde sıra korelasyonu güvenilir olarak
    tahmin edilemeyeceğinden sonuç kesinlikle NaN (np.nan) olmalıdır.
    Beklenen: n = 2, spearman = NaN.

  2. Pencere ('2026-01-15'):
    puan satırı:   [10.0, 20.0, 30.0,  NaN]
    getiri satırı: [ 0.1,  0.2,  0.3,  0.4]
    Ortak geçerli adresler:
      't1', 't2', 't3' (üçü de mevcuttur).
    Ortak geçerli adres sayısı: n = 3 (>= 3).
    Sıralar: rx = [1, 2, 3], ry = [1, 2, 3]. Tam doğrusal uyum -> r = 1.0.
    Beklenen: n = 3, spearman = 1.0.
  -------------------------------------------------------------------------
  """
  tarihler = ["2026-01-01", "2026-01-15"]
  adresler = ["t1", "t2", "t3", "t4"]

  puan_df = pd.DataFrame(
      [
          [10.0, 20.0, np.nan, np.nan],
          [10.0, 20.0, 30.0, np.nan],
      ],
      index=tarihler,
      columns=adresler,
  )

  getiri_df = pd.DataFrame(
      [
          [0.1, 0.2, 0.3, np.nan],
          [0.1, 0.2, 0.3, 0.4],
      ],
      index=tarihler,
      columns=adresler,
  )

  cikti = pencere_kaliciligi(puan_df, getiri_df)

  # 1. Pencere doğrulaması (n = 2 < 3 -> spearman NaN)
  assert cikti.loc["2026-01-01", "n"] == 2
  assert np.isnan(cikti.loc["2026-01-01", "spearman"])

  # 2. Pencere doğrulaması (n = 3 >= 3 -> spearman 1.0)
  assert cikti.loc["2026-01-15", "n"] == 3
  assert math.isclose(cikti.loc["2026-01-15", "spearman"], 1.0, rel_tol=1e-12)


def test_4_ayni_tohumla_ayni_aralik():
  """Test 4: Aynı tohumla çalıştırıldığında birebir aynı güven aralığının elde

  edilmesi.

  ELLE HESAPLAMA ADIMLARI:
  -------------------------------------------------------------------------
  Girdi: 8 pencerelik Spearman korelasyon serisi:
    degerler = [0.15, 0.22, -0.05, 0.18, 0.30, 0.12, -0.02, 0.25]
    blok = 3, tekrar = 500, tohum = 42, alfa = 0.05

  Sözde-Rastgele Sayı Üreteci Determinizmi:
    NumPy'ın default_rng(42) üreteci, tohum sabitlendiğinde tamamen
    deterministik bir sözde-rastgele dizi üretir.
    Aynı tohum ve parametrelerle fonksiyon ardışık çağrıldığında:
      1. Çekilen blok başlangıç matrisi bit düzeyinde özdeş olur.
      2. 500 bootstrap replikasyonunun her birinin ortalaması özdeş çıkar.
      3. Dolayısıyla hesaplanan %2.5 ve %97.5 yüzdelik değerleri de tam eşittir:
         alt_1 == alt_2, ust_1 == ust_2, ortalama_1 == ortalama_2, n_1 == n_2.
  -------------------------------------------------------------------------
  """
  degerler = pd.Series([0.15, 0.22, -0.05, 0.18, 0.30, 0.12, -0.02, 0.25])

  sonuc_1 = blok_bootstrap_ortalama(
      degerler, blok=3, tekrar=500, tohum=42, alfa=0.05
  )
  sonuc_2 = blok_bootstrap_ortalama(
      degerler, blok=3, tekrar=500, tohum=42, alfa=0.05
  )

  assert sonuc_1["n"] == sonuc_2["n"] == 8
  assert math.isclose(sonuc_1["ortalama"], sonuc_2["ortalama"], rel_tol=1e-14)
  assert math.isclose(sonuc_1["alt"], sonuc_2["alt"], rel_tol=1e-14)
  assert math.isclose(sonuc_1["ust"], sonuc_2["ust"], rel_tol=1e-14)


def test_5_sabit_seride_aralik_esittir_ortalama():
  """Test 5: Sabit değerli bir seride güven aralığının doğrudan ortalamaya eşit

  olması.

  ELLE HESAPLAMA ADIMLARI:
  -------------------------------------------------------------------------
  Girdi Serisi (n = 6):
    degerler = [0.35, 0.35, 0.35, 0.35, 0.35, 0.35]
    blok = 2, tekrar = 1000, tohum = 999, alfa = 0.05

  Adım 1: Örneklem Ortalaması:
    ortalama = (0.35 * 6) / 6 = 0.35

  Adım 2: Hareketli Bloklar:
    Blok boyutu b = 2. Olası tüm bloklar: [0.35, 0.35].
    Bootstrap ile hangi blok seçilirse seçilsin, türetilen örneklemin
    tüm elemanları istisnasız 0.35 değerini alır.

  Adım 3: Bootstrap Ortalamaları Dağılımı:
    Her k yinelemesinde:
      boot_mean_k = sum([0.35, ..., 0.35]) / 6 = 0.35.
    1000 yinelemenin tamamında ortalama 0.35'tir.

  Adım 4: Güven Aralığı Sınırları:
    %2.5 yüzdeliği (alt) = 0.35
    %97.5 yüzdeliği (üst) = 0.35

  Sonuç:
    alt == ortalama == 0.35 ve ust == ortalama == 0.35
    Aralık genişliği: ust - alt = 0.0 (noktasal kütle).
  -------------------------------------------------------------------------
  """
  degerler = pd.Series([0.35, 0.35, 0.35, 0.35, 0.35, 0.35])

  sonuc = blok_bootstrap_ortalama(
      degerler, blok=2, tekrar=1000, tohum=999, alfa=0.05
  )

  assert sonuc["n"] == 6
  assert math.isclose(sonuc["ortalama"], 0.35, rel_tol=1e-12)
  assert math.isclose(sonuc["alt"], 0.35, rel_tol=1e-12)
  assert math.isclose(sonuc["ust"], 0.35, rel_tol=1e-12)
  assert math.isclose(sonuc["alt"], sonuc["ortalama"], rel_tol=1e-12)
  assert math.isclose(sonuc["ust"], sonuc["ortalama"], rel_tol=1e-12)


if __name__ == "__main__":
  test_1_spearman_altin_ornek_esitlik_dahil()
  test_2_spearman_tam_ters_sira()
  test_3_ortak_adres_kucuktur_uc_nan_doner()
  test_4_ayni_tohumla_ayni_aralik()
  test_5_sabit_seride_aralik_esittir_ortalama()
  print("Tüm testler (1-5) başarıyla tamamlandı ve doğrulandı.")