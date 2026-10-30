"""copytrade.gecikme.ozet — altın örnek testleri (elle hesaplanmış girdi + beklenen sayı)."""

from copytrade.gecikme import ozet


def test_altin_ornek_uc_trader():
    rows = [{'trader': 'T1', 'gecikme_dk': 1.0}, {'trader': 'T2', 'gecikme_dk': 5.0}, {'trader': 'T3', 'gecikme_dk': 3.0}]
    assert ozet(rows) == {'n': 3, 'gecikme_dk_medyan': 3.0, 'gecikme_dk_maks': 5.0}


def test_bos_liste_sifira_bolme_yapmaz():
    assert ozet([]) == {'n': 0, 'gecikme_dk_medyan': None, 'gecikme_dk_maks': None}


def test_eksik_gecikme_degeri_dislanir():
    rows = [{'trader': 'T1', 'gecikme_dk': None}, {'trader': 'T2', 'gecikme_dk': 2.0}]
    assert ozet(rows) == {'n': 1, 'gecikme_dk_medyan': 2.0, 'gecikme_dk_maks': 2.0}


def test_cift_sayida_eleman_medyan_ortalamasi():
    rows = [{'trader': 'T1', 'gecikme_dk': 2.0}, {'trader': 'T2', 'gecikme_dk': 4.0}]
    assert ozet(rows) == {'n': 2, 'gecikme_dk_medyan': 3.0, 'gecikme_dk_maks': 4.0}
