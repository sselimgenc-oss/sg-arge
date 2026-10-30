"""copytrade.gecikme.ozet — altın örnek testleri (elle hesaplanmış girdi + beklenen sayı)."""

from copytrade.gecikme import ozet

SIMDI = '2026-01-01T10:00:00Z'


def test_altin_ornek_uc_trader_taze():
    rows = [
        {'trader': 'T1', 'gecikme_dk': 1.0, 'zaman': '2026-01-01T09:59:00Z'},   # 1 dk önce
        {'trader': 'T2', 'gecikme_dk': 5.0, 'zaman': '2026-01-01T09:55:00Z'},   # 5 dk önce
        {'trader': 'T3', 'gecikme_dk': 3.0, 'zaman': '2026-01-01T09:58:00Z'},   # 2 dk önce
    ]
    assert ozet(rows, SIMDI) == {'n': 3, 'n_toplam': 3, 'gecikme_dk_medyan': 3.0, 'gecikme_dk_maks': 5.0}


def test_bos_liste_sifira_bolme_yapmaz():
    assert ozet([], SIMDI) == {'n': 0, 'n_toplam': 0, 'gecikme_dk_medyan': None, 'gecikme_dk_maks': None}


def test_eksik_gecikme_degeri_dislanir():
    rows = [{'trader': 'T1', 'gecikme_dk': None, 'zaman': SIMDI}, {'trader': 'T2', 'gecikme_dk': 2.0, 'zaman': SIMDI}]
    assert ozet(rows, SIMDI) == {'n': 1, 'n_toplam': 2, 'gecikme_dk_medyan': 2.0, 'gecikme_dk_maks': 2.0}


def test_cift_sayida_eleman_medyan_ortalamasi():
    rows = [{'trader': 'T1', 'gecikme_dk': 2.0, 'zaman': SIMDI}, {'trader': 'T2', 'gecikme_dk': 4.0, 'zaman': SIMDI}]
    assert ozet(rows, SIMDI) == {'n': 2, 'n_toplam': 2, 'gecikme_dk_medyan': 3.0, 'gecikme_dk_maks': 4.0}


def test_eski_ornek_medyandan_dislanir_ama_toplama_girer():
    # T1 uzun süre işlem yapmadı: en son örneği 1 gün önce (pencere 120 dk) -> medyana girmemeli.
    # Sol'un 2. denetimdeki YÜKSEK bulgusu: eski/eylemsiz trader örneği medyanı bozmamalı.
    rows = [
        {'trader': 'T1', 'gecikme_dk': 1440.0, 'zaman': '2025-12-31T09:00:00Z'},   # 25 sa önce, eski
        {'trader': 'T2', 'gecikme_dk': 2.0, 'zaman': '2026-01-01T09:58:00Z'},       # taze
    ]
    olcu = ozet(rows, SIMDI)
    assert olcu == {'n': 1, 'n_toplam': 2, 'gecikme_dk_medyan': 2.0, 'gecikme_dk_maks': 2.0}


def test_eksik_zaman_alani_dislanir():
    rows = [{'trader': 'T1', 'gecikme_dk': 9.0}, {'trader': 'T2', 'gecikme_dk': 1.0, 'zaman': SIMDI}]
    assert ozet(rows, SIMDI) == {'n': 1, 'n_toplam': 2, 'gecikme_dk_medyan': 1.0, 'gecikme_dk_maks': 1.0}


def test_bozuk_zaman_cokmez():
    rows = [{'trader': 'T1', 'gecikme_dk': 9.0, 'zaman': 'gecersiz'}, {'trader': 'T2', 'gecikme_dk': 1.0, 'zaman': SIMDI}]
    assert ozet(rows, SIMDI) == {'n': 1, 'n_toplam': 2, 'gecikme_dk_medyan': 1.0, 'gecikme_dk_maks': 1.0}


def test_varsayilan_simdi_ile_cagri_cokmez():
    assert ozet([])['n'] == 0
