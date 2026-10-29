"""`copytrade/yogunlasma.py` testleri (Argon A14 altın örnekleri; yarı tutarlılığı rho'su tanımsızsa None) ve seçim raporu bağlantısı."""
import unittest

import numpy as np
import pandas as pd

from copytrade.yogunlasma import korelasyon_matrisi, kumele, yari_tutarliligi, yogunlasma_ozeti


class TestKorelasyonMatrisi(unittest.TestCase):
    """korelasyon_matrisi fonksiyonu için testler."""

    def test_temel_korelasyon(self):
        """Doğrusal bağımlı serilerin korelasyonu doğru hesaplanmalı."""
        df = pd.DataFrame({
            "trader_1": [0.01, 0.02, 0.03, 0.04, 0.05],
            "trader_2": [0.02, 0.04, 0.06, 0.08, 0.10],
            "trader_3": [-0.01, -0.02, -0.03, -0.04, -0.05],
        })
        corr = korelasyon_matrisi(df, min_ortak_gun=3)
        self.assertAlmostEqual(corr.loc["trader_1", "trader_2"], 1.0, places=6)
        self.assertAlmostEqual(corr.loc["trader_1", "trader_3"], -1.0, places=6)
        self.assertAlmostEqual(corr.loc["trader_1", "trader_1"], 1.0, places=6)

    def test_min_ortak_gun_kurali(self):
        """Ortak gün sayısı min_ortak_gun'ün altındaysa NaN dönmeli."""
        df = pd.DataFrame({
            "t1": [0.01, 0.02, 0.03, np.nan, np.nan],
            "t2": [0.02, 0.04, np.nan, np.nan, 0.10],
            "t3": [0.01, 0.02, 0.03, 0.04, 0.05],
        })
        # t1 ve t2 arasında sadece 2 ortak gün var ([0, 1])
        corr_min3 = korelasyon_matrisi(df, min_ortak_gun=3)
        self.assertTrue(np.isnan(corr_min3.loc["t1", "t2"]))

        corr_min2 = korelasyon_matrisi(df, min_ortak_gun=2)
        self.assertFalse(np.isnan(corr_min2.loc["t1", "t2"]))
        self.assertAlmostEqual(corr_min2.loc["t1", "t2"], 1.0, places=6)

    def test_sifir_varyans(self):
        """Sabit getirili seride varyans 0 olduğundan korelasyon NaN olmalı."""
        df = pd.DataFrame({
            "t1": [0.01, 0.01, 0.01, 0.01],
            "t2": [0.01, 0.02, 0.03, 0.04],
        })
        corr = korelasyon_matrisi(df, min_ortak_gun=2)
        self.assertTrue(np.isnan(corr.loc["t1", "t2"]))
        self.assertTrue(np.isnan(corr.loc["t1", "t1"]))


class TestKumele(unittest.TestCase):
    """kumele fonksiyonu için testler."""

    def test_birebir_ayni_iki_seri_tek_kumeye_girmeli(self):
        """Birebir aynı iki seri (korelasyon = 1.0) tek kümeye girmeli."""
        corr = pd.DataFrame(
            [[1.0, 1.0], [1.0, 1.0]],
            index=["trader_A", "trader_B"],
            columns=["trader_A", "trader_B"]
        )
        kumeler = kumele(corr, esik=0.7)
        self.assertEqual(kumeler["trader_A"], kumeler["trader_B"])
        self.assertEqual(kumeler["trader_A"], 0)

        ozet = yogunlasma_ozeti(kumeler)
        self.assertEqual(ozet["kume_sayisi"], 1)
        self.assertEqual(ozet["en_buyuk_kume_payi"], 1.0)
        self.assertAlmostEqual(ozet["etkin_kume_sayisi"], 1.0, places=6)

        # Getiri serisi üzerinden uçtan uca
        np.random.seed(42)
        r = np.random.normal(0.001, 0.02, size=30)
        df_getiri = pd.DataFrame({
            "trader_1": r,
            "trader_2": r,
        })
        matris = korelasyon_matrisi(df_getiri, min_ortak_gun=10)
        kume_sonucu = kumele(matris, esik=0.8)
        self.assertEqual(kume_sonucu["trader_1"], kume_sonucu["trader_2"])

    def test_bagimsiz_seriler_ayri_kumelerde_kalmali(self):
        """Bağımsız / ilişkisiz seriler ayrı kümelerde kalmalı."""
        corr = pd.DataFrame(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            index=["trader_1", "trader_2", "trader_3"],
            columns=["trader_1", "trader_2", "trader_3"]
        )
        kumeler = kumele(corr, esik=0.5)

        self.assertNotEqual(kumeler["trader_1"], kumeler["trader_2"])
        self.assertNotEqual(kumeler["trader_1"], kumeler["trader_3"])
        self.assertNotEqual(kumeler["trader_2"], kumeler["trader_3"])

        ozet = yogunlasma_ozeti(kumeler)
        self.assertEqual(ozet["kume_sayisi"], 3)
        self.assertAlmostEqual(ozet["en_buyuk_kume_payi"], 1.0 / 3.0, places=6)
        self.assertAlmostEqual(ozet["etkin_kume_sayisi"], 3.0, places=6)

    def test_esik_sinirinda_davranis(self):
        """Eşik sınırında davranış: ortalama korelasyon eşiğin altına düşünce birleştirme durmalı."""
        corr = pd.DataFrame(
            [[1.0, 0.60], [0.60, 1.0]],
            index=["A", "B"],
            columns=["A", "B"]
        )

        # 1. Eşik = 0.60 iken: Eşiğin altına düşmemiştir, BİRLEŞMELİDİR.
        kumeler_esit = kumele(corr, esik=0.60)
        self.assertEqual(kumeler_esit["A"], kumeler_esit["B"])

        # 2. Eşik = 0.61 iken: Eşiğin altına düşmüştür, BİRLEŞMEMELİDİR.
        kumeler_altinda = kumele(corr, esik=0.61)
        self.assertNotEqual(kumeler_altinda["A"], kumeler_altinda["B"])

        # 3. Çoklu kümede ortalama bağlantı eşik sınırı testi:
        corr3 = pd.DataFrame(
            [
                [1.0, 0.90, 0.80],
                [0.90, 1.0, 0.40],
                [0.80, 0.40, 1.0],
            ],
            index=["A", "B", "C"],
            columns=["A", "B", "C"]
        )
        # esik = 0.60 -> (0.80 + 0.40)/2 = 0.60 >= esik -> C birleşir
        res_esik60 = kumele(corr3, esik=0.60)
        self.assertEqual(res_esik60["A"], res_esik60["B"])
        self.assertEqual(res_esik60["A"], res_esik60["C"])

        # esik = 0.65 -> 0.60 < 0.65 -> C birleşemez
        res_esik65 = kumele(corr3, esik=0.65)
        self.assertEqual(res_esik65["A"], res_esik65["B"])
        self.assertNotEqual(res_esik65["A"], res_esik65["C"])

    def test_nanli_veri(self):
        """Hesaplanamayan (NaN) çiftler bağlantısız sayılmalı ve kümelenmeyi bozmamalı."""
        corr = pd.DataFrame(
            [
                [1.0, 0.95, np.nan],
                [0.95, 1.0, np.nan],
                [np.nan, np.nan, 1.0],
            ],
            index=["A", "B", "C"],
            columns=["A", "B", "C"]
        )
        kumeler = kumele(corr, esik=0.7)
        self.assertEqual(kumeler["A"], kumeler["B"])
        self.assertNotEqual(kumeler["A"], kumeler["C"])

        # Ayrık iki grup: {A, B} ve {C, D}
        corr_groups = pd.DataFrame(
            [
                [1.0, 0.9, np.nan, np.nan],
                [0.9, 1.0, np.nan, np.nan],
                [np.nan, np.nan, 1.0, 0.85],
                [np.nan, np.nan, 0.85, 1.0],
            ],
            index=["A", "B", "C", "D"],
            columns=["A", "B", "C", "D"]
        )
        res_groups = kumele(corr_groups, esik=0.7)
        self.assertEqual(res_groups["A"], res_groups["B"])
        self.assertEqual(res_groups["C"], res_groups["D"])
        self.assertNotEqual(res_groups["A"], res_groups["C"])

        # Tamamen NaN korelasyon matrisi: Hiçbir eleman birleşmemeli
        corr_all_nan = pd.DataFrame(
            [
                [1.0, np.nan, np.nan],
                [np.nan, 1.0, np.nan],
                [np.nan, np.nan, 1.0],
            ],
            index=["X", "Y", "Z"],
            columns=["X", "Y", "Z"]
        )
        res_all_nan = kumele(corr_all_nan, esik=0.5)
        self.assertEqual(len(set(res_all_nan.values())), 3)

    def test_bos_ve_tekli_matris(self):
        """Boş ve tek elemanlı girişler doğru işlenmeli."""
        self.assertEqual(kumele(pd.DataFrame(), esik=0.5), {})
        self.assertEqual(kumele(pd.DataFrame([[1.0]], index=["A"], columns=["A"]), esik=0.5), {"A": 0})


class TestYogunlasmaOzeti(unittest.TestCase):
    """yogunlasma_ozeti fonksiyonu için testler."""

    def test_metrikler(self):
        """Etkin küme sayısı (Herfindahl tersi), küme sayısı ve en büyük pay doğru olmalı."""
        kumeler = {"A": 0, "B": 0, "C": 1, "D": 1}
        ozet = yogunlasma_ozeti(kumeler)
        self.assertEqual(ozet["kume_sayisi"], 2)
        self.assertEqual(ozet["en_buyuk_kume_payi"], 0.5)
        self.assertEqual(ozet["etkin_kume_sayisi"], 2.0)

        kumeler_asym = {"A": 0, "B": 0, "C": 0, "D": 1}
        ozet_asym = yogunlasma_ozeti(kumeler_asym)
        self.assertEqual(ozet_asym["kume_sayisi"], 2)
        self.assertEqual(ozet_asym["en_buyuk_kume_payi"], 0.75)
        self.assertAlmostEqual(ozet_asym["etkin_kume_sayisi"], 1.6, places=6)

        ozet_bos = yogunlasma_ozeti({})
        self.assertEqual(ozet_bos["kume_sayisi"], 0)
        self.assertEqual(ozet_bos["en_buyuk_kume_payi"], 0.0)
        self.assertEqual(ozet_bos["etkin_kume_sayisi"], 0.0)


class TestYariTutarliligi(unittest.TestCase):
    """yari_tutarliligi fonksiyonu için testler."""

    def test_elle_hesaplanmis_ornek_bagli_siralar(self):
        """Kullanıcı gereksinimi: yari_tutarliligi için elle hesaplanmış örnek (bağlı sıralar içeren)."""
        df = pd.DataFrame([
            [3.0, 6.0, 6.0, 10.0],
            [3.0, 7.0, 7.0, 10.0],
            [4.0, 7.0, 7.0, 10.0],  # İlk yarı toplamı: A=10, B=20, C=20, D=30
            [1.0, 5.0, 8.0, 11.0],
            [2.0, 5.0, 8.0, 12.0],
            [2.0, 5.0, 9.0, 12.0],  # İkinci yarı toplamı: A=5, B=15, C=25, D=35
        ], columns=["A", "B", "C", "D"])

        def sum_score(df_half):
            return df_half.sum()

        res = yari_tutarliligi(df, sum_score)
        expected_rho = 4.5 / np.sqrt(22.5)

        self.assertEqual(res["n"], 4)
        self.assertAlmostEqual(res["rho"], expected_rho, places=10)

    def test_elle_hesaplanmis_ornek_bagsiz_siralar(self):
        """Elle hesaplanmış örnek 2 (bağsız / eşit değersiz sıralar): rho = 0.60."""
        df = pd.DataFrame([
            [1.0, 2.0, 3.0, 4.0],  # 1. yarı
            [2.0, 1.0, 4.0, 3.0],  # 2. yarı
        ], columns=["A", "B", "C", "D"])

        def first_row_score(df_half):
            return df_half.iloc[0]

        res = yari_tutarliligi(df, first_row_score)
        self.assertEqual(res["n"], 4)
        self.assertAlmostEqual(res["rho"], 0.60, places=10)

    def test_tam_ayni_ve_tam_ters_tutarlilik(self):
        """Tam uyumlu ve tam ters puanlamada rho sırasıyla 1.0 ve -1.0 olmalı."""
        df_ayni = pd.DataFrame([
            [10.0, 20.0, 30.0],
            [1.0, 2.0, 3.0],
        ], columns=["A", "B", "C"])
        res_ayni = yari_tutarliligi(df_ayni, lambda d: d.iloc[0])
        self.assertEqual(res_ayni["n"], 3)
        self.assertAlmostEqual(res_ayni["rho"], 1.0, places=10)

        df_ters = pd.DataFrame([
            [10.0, 20.0, 30.0],
            [3.0, 2.0, 1.0],
        ], columns=["A", "B", "C"])
        res_ters = yari_tutarliligi(df_ters, lambda d: d.iloc[0])
        self.assertEqual(res_ters["n"], 3)
        self.assertAlmostEqual(res_ters["rho"], -1.0, places=10)

    def test_sabit_puan_veya_yetersiz_veri(self):
        """Sabit puanlarda varyans 0 olduğundan ve n < 2 durumunda rho NaN olmalı."""
        df_sabit = pd.DataFrame([
            [5.0, 5.0, 5.0],
            [1.0, 2.0, 3.0],
        ], columns=["A", "B", "C"])
        res_sabit = yari_tutarliligi(df_sabit, lambda d: d.iloc[0])
        self.assertIsNone(res_sabit["rho"])

        df_tek = pd.DataFrame([[1.0], [2.0]], columns=["A"])
        res_tek = yari_tutarliligi(df_tek, lambda d: d.iloc[0])
        self.assertEqual(res_tek["n"], 1)
        self.assertIsNone(res_tek["rho"])


