from copytrade.izleme_motoru import kasa_egrisi


def test_kasa_egrisi_oda_toplamini_son_bilinen_bakiye_ile_toplar():
    traders = [
        {'kol': 'oda', 'sanal_kopya': {'egri': [['2026-10-01', 1000.0], ['2026-10-02', 1010.0]]}},
        {'kol': 'oda', 'sanal_kopya': {'egri': [['2026-10-02', 1000.0], ['2026-10-03', 980.0]]}},
        {'kol': 'kontrol', 'sanal_kopya': {'egri': [['2026-10-02', 2000.0]]}},
    ]
    assert kasa_egrisi(traders, 'oda') == [['2026-10-01', 1000.0], ['2026-10-02', 2010.0], ['2026-10-03', 1990.0]]
    assert kasa_egrisi(traders, 'kontrol') == [['2026-10-02', 2000.0]]
