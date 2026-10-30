from copytrade.izleme_motoru import kasa_egrisi


def test_kasa_egrisi_oda_toplamini_son_bilinen_bakiye_ile_toplar():
    traders = [
        {'kol': 'oda', 'sanal_kopya': {'egri': [['2026-10-01', 1000.0], ['2026-10-02', 1010.0]]}},
        {'kol': 'oda', 'sanal_kopya': {'egri': [['2026-10-02', 1000.0], ['2026-10-03', 980.0]]}},
        {'kol': 'kontrol', 'sanal_kopya': {'egri': [['2026-10-02', 2000.0]]}},
    ]
    assert kasa_egrisi(traders, 'oda') == [['2026-10-01', 1000.0], ['2026-10-02', 2010.0], ['2026-10-03', 1990.0]]
    assert kasa_egrisi(traders, 'kontrol') == [['2026-10-02', 2000.0]]


def test_gecersizler_toplama_girmez_kapsamda_ayri_sayilir_kollar_ile():
    # Altın örnek: oda = A (geçerli, 1.010 $), B (eski: okuma hatası, 1.500 $ önceki sonuç), C (hiç okunmadı, 1.000 $ yer tutucu),
    # D (perp hesabı boş, 1.000 $), E (kol=elle ama kollar=[elle, kontrol]: kontrolde sayılır, odada değil).
    from copytrade.izleme_motoru import kapsam
    sk = lambda v: {'egri': [['2026-10-02', v]]}
    traders = [
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': sk(1010.0)},
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': False, 'veri_zamani': 'x', 'veri_durumu': 'veri_hatasi', 'sanal_kopya': sk(1500.0)},
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': False, 'veri_zamani': None, 'veri_durumu': 'veri_hatasi', 'sanal_kopya': sk(1000.0)},
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': False, 'veri_zamani': 'x', 'veri_durumu': 'perp_hesabi_bos', 'sanal_kopya': sk(1000.0)},
        {'kol': 'elle', 'kollar': ['elle', 'kontrol'], 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': sk(990.0)},
    ]
    assert kasa_egrisi(traders, 'oda') == [['2026-10-02', 1010.0]]
    assert kasa_egrisi(traders, 'kontrol') == [['2026-10-02', 990.0]]
    assert kapsam(traders, 'oda') == {'toplam': 4, 'gecerli': 1, 'eski': 1, 'yer_tutucu': 1, 'perp_hesabi_bos': 1}
    assert kapsam(traders, 'kontrol') == {'toplam': 1, 'gecerli': 1, 'eski': 0, 'yer_tutucu': 0, 'perp_hesabi_bos': 0}
