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
    sk = lambda v: {'egri': [['2026-10-02', v]], 'bakiye_usd': v}
    traders = [
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': sk(1010.0)},
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': False, 'veri_zamani': 'x', 'veri_durumu': 'okuma_hatasi', 'sanal_kopya': sk(1500.0)},
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': False, 'veri_zamani': None, 'veri_durumu': 'okuma_hatasi', 'sanal_kopya': sk(1000.0)},
        {'kol': 'oda', 'kollar': ['oda'], 'gecerli': False, 'veri_zamani': 'x', 'veri_durumu': 'perp_bos', 'sanal_kopya': sk(1000.0)},
        {'kol': 'elle', 'kollar': ['elle', 'kontrol'], 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': sk(990.0)},
    ]
    assert kasa_egrisi(traders, 'oda') == [['2026-10-02', 1010.0]]
    assert kasa_egrisi(traders, 'kontrol') == [['2026-10-02', 990.0]]
    # Altın örnek: A geçerli 1.010 $; B okuma_hatasi (önceki sonuç 1.500 $ ayrı alt toplam); C yer tutucu; D perp_bos. ITT: toplam 4 sabit.
    assert kapsam(traders, 'oda') == {'toplam': 4, 'gecerli': 1, 'fiyatsiz': 0, 'perp_bos': 1, 'yer_tutucu': 1, 'bayat': 0, 'okuma_hatasi': 1,
                                      'kapsama': 0.25, 'gecerli_bakiye_usd': 1010.0, 'gecersiz_bakiye_usd': 1500.0,
                                      'egri_eksik': 0, 'kasa_son_nokta_usd': 1010.0, 'kasa_fark_usd': 0.0, 'kasa_mutabik': True, 'eksik_degerleme': 0}
    assert kapsam(traders, 'kontrol') == {'toplam': 1, 'gecerli': 1, 'fiyatsiz': 0, 'perp_bos': 0, 'yer_tutucu': 0, 'bayat': 0, 'okuma_hatasi': 0,
                                          'kapsama': 1.0, 'gecerli_bakiye_usd': 990.0, 'gecersiz_bakiye_usd': 0.0,
                                          'egri_eksik': 0, 'kasa_son_nokta_usd': 990.0, 'kasa_fark_usd': 0.0, 'kasa_mutabik': True, 'eksik_degerleme': 0}


def test_bayat_ve_fiyatsiz_durum_kodlari():
    import pandas as pd
    from copytrade.izleme_motoru import with_data_error, veri_durumu, kapsam
    base = {'veri_zamani': '2026-10-27T12:00:00Z', 'gecerli': True, 'saglik': {'nedenler': []}}
    now = pd.Timestamp('2026-10-27T14:00:00Z')                     # 120 dk: eşik 180 altında
    assert with_data_error(base, RuntimeError('x'), now)['veri_durumu'] == 'okuma_hatasi'
    now = pd.Timestamp('2026-10-27T15:01:00Z')                     # 181 dk: bayat
    assert with_data_error(base, RuntimeError('x'), now)['veri_durumu'] == 'bayat'
    assert veri_durumu(None) == 'tamam'
    t = [{'kol': 'oda', 'gecerli': True, 'veri_durumu': 'fiyatsiz', 'veri_zamani': 'x', 'sanal_kopya': {'bakiye_usd': 1002.0}},
         {'kol': 'oda', 'gecerli': False, 'veri_durumu': 'bayat', 'veri_zamani': 'x', 'sanal_kopya': {'bakiye_usd': 900.0}}]
    k = kapsam(t, 'oda')
    assert (k['gecerli'], k['fiyatsiz'], k['bayat'], k['kapsama'], k['gecersiz_bakiye_usd']) == (1, 1, 1, 0.5, 900.0)


def test_egri_eksik_ve_kasa_mutabakati():
    from copytrade.izleme_motoru import kapsam
    # Altın örnek: A bakiye 1.010, eğri son nokta 1.010 (mutabık). B geçerli ama eğrisi boş → egri_eksik=1 (kasaya giremez, uydurulmaz).
    # C bakiye 1.000 ama eğrisi 1.030'da kalmış (bayat eğri) → fark +30 $ → mutabık değil.
    ok = [{'kol': 'oda', 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': {'bakiye_usd': 1010.0, 'egri': [['2026-10-02', 1010.0]]}},
          {'kol': 'oda', 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': {'bakiye_usd': 1000.0, 'egri': []}}]
    k = kapsam(ok, 'oda')
    assert (k['egri_eksik'], k['kasa_son_nokta_usd'], k['kasa_fark_usd'], k['kasa_mutabik']) == (1, 1010.0, 0.0, True)
    bad = [{'kol': 'oda', 'gecerli': True, 'veri_zamani': 'x', 'sanal_kopya': {'bakiye_usd': 1000.0, 'egri': [['2026-10-02', 1030.0]]}}]
    k = kapsam(bad, 'oda')
    assert k['kasa_fark_usd'] == 30.0 and k['kasa_mutabik'] is False
