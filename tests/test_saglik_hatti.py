"""copytrade.saglik_hatti — altın örnek testleri (elle hesaplanmış girdi + beklenen sayı, AGENTS.md kabul kanıtı)."""

from copytrade import saglik_hatti


def _trader(id_, gecerli, isik, yetim, mutabakat_toplam, isaret_eksik, pozisyon_acilislar):
    return {
        'id': id_, 'kol': 'oda', 'kollar': ['oda'], 'gecerli': gecerli,
        'saglik': {'isik': isik, 'nedenler': []},
        'veri_kalitesi': {'mutabakat': {'yetim': yetim, 'toplam': mutabakat_toplam}},
        'sanal_kopya': {'isaret_eksik': isaret_eksik},
        'pozisyonlar': [{'coin': 'BTC', 'acilis': a} for a in pozisyon_acilislar],
    }


def test_altin_ornek_iki_trader_kirmizi():
    # Elle hesap: t1 yetim=1/4, isaret_eksik=2, pozisyon açılış uretildi'den 30 dk önce.
    # t2 gecersiz, yetim=0/2, pozisyon açılışları uretildi'den 500 dk (eski, dışlanır) ve 10 dk önce.
    durum = {
        'uretildi': '2026-01-01T10:00:00Z',
        'traderlar': [
            _trader('T1', True, 'sari', 1, 4, 2, ['2026-01-01T09:30:00Z']),
            _trader('T2', False, 'kirmizi', 0, 2, 0, ['2025-12-13T01:40:00Z', '2026-01-01T09:50:00Z']),
        ],
    }
    olcu = saglik_hatti.olc(durum, '2026-01-01T10:05:00Z')
    assert olcu['n'] == 2
    assert olcu['veri_tazeligi_dk'] == 5.0
    assert olcu['yetim_golge_orani'] == 1 / 6
    assert olcu['isaret_eksik_toplam'] == 2
    assert olcu['veri_hata_orani'] == 0.5
    assert olcu['kirmizi_sayisi'] == 1
    assert olcu['sari_sayisi'] == 1
    # 500 dk'lık açılış dışlanır (SINYAL_TAZELIK_DK=180); kalan [30, 10] -> medyan 20.
    assert olcu['sinyal_gecikme_dk_medyan'] == 20.0

    kontrol = saglik_hatti.kontrol(olcu)
    assert kontrol['isik'] == 'kirmizi'
    assert kontrol['nedenler'] == ['yetim gölge payı %17', 'veri hatası payı %50']


def test_bos_kol_sari_doner():
    olcu = saglik_hatti.olc({'uretildi': '2026-01-01T10:00:00Z', 'traderlar': []}, '2026-01-01T10:05:00Z')
    assert olcu == {
        'kol': 'oda', 'n': 0, 'veri_tazeligi_dk': None, 'yetim_golge_orani': None,
        'isaret_eksik_toplam': 0, 'veri_hata_orani': None, 'kirmizi_sayisi': 0, 'sari_sayisi': 0,
        'sinyal_gecikme_dk_medyan': None,
    }
    assert saglik_hatti.kontrol(olcu) == {'isik': 'sari', 'nedenler': ['kol boş']}


def test_eksik_alanlar_sifira_bolme_yapmaz_yesil_doner():
    # veri_kalitesi/sanal_kopya/saglik hiç yok (isteğe bağlı alanlar) — çökmemeli, payda sıfırsa oran None olmalı.
    durum = {'uretildi': '2026-01-01T10:00:00Z', 'traderlar': [{'id': 'T1', 'kol': 'oda'}]}
    olcu = saglik_hatti.olc(durum, '2026-01-01T10:01:00Z')
    assert olcu['yetim_golge_orani'] is None
    assert olcu['isaret_eksik_toplam'] == 0
    assert olcu['veri_hata_orani'] == 0.0
    assert olcu['sinyal_gecikme_dk_medyan'] is None
    assert saglik_hatti.kontrol(olcu) == {'isik': 'yesil', 'nedenler': []}


def test_bozuk_uretildi_tarihi_cokmez():
    durum = {'uretildi': 'gecersiz-tarih', 'traderlar': [{'id': 'T1', 'kol': 'oda', 'gecerli': True}]}
    olcu = saglik_hatti.olc(durum, '2026-01-01T10:01:00Z')
    assert olcu['veri_tazeligi_dk'] is None


def test_veri_bayatligi_kirmizi_esigi():
    durum = {'uretildi': '2026-01-01T07:00:00Z', 'traderlar': [{'id': 'T1', 'kol': 'oda', 'gecerli': True}]}
    olcu = saglik_hatti.olc(durum, '2026-01-01T10:00:00Z')  # 180 dk eski
    assert olcu['veri_tazeligi_dk'] == 180.0
    assert saglik_hatti.kontrol(olcu) == {'isik': 'kirmizi', 'nedenler': ['veri 180 dk önce']}


def test_kollar_filtresi_sadece_istenen_kolu_sayar():
    durum = {'uretildi': '2026-01-01T10:00:00Z', 'traderlar': [
        {'id': 'T1', 'kollar': ['oda'], 'gecerli': True},
        {'id': 'T2', 'kollar': ['kontrol'], 'gecerli': True},
    ]}
    assert saglik_hatti.olc(durum, '2026-01-01T10:00:00Z')['n'] == 1
    assert saglik_hatti.olc(durum, '2026-01-01T10:00:00Z', kol='kontrol')['n'] == 1
