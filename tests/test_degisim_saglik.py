import json

import pytest
import yaml

from copytrade import gecis
from copytrade.degisim_rapor import rapor
from copytrade.izleme_motoru import mutabakat_raporu, timestamp
from copytrade.kurallar import load_rules


def addr(char):
    return '0x' + char * 40


def test_degisimin_gecerli_gerekcesi_tavani_ve_istisnasi(tmp_path):
    path = tmp_path / 'degisim.jsonl'
    rules = load_rules()
    for day, char in [('2026-10-01', 'a'), ('2026-10-02', 'b')]:
        gecis.degisim_yaz(path, {'tarih': day, 'cikarilan': addr(char), 'alinan': addr(chr(ord(char) + 2)), 'gerekce': 'tarz_kaymasi', 'not': ''}, rules)
    with pytest.raises(ValueError, match='tavan'):
        gecis.degisim_yaz(path, {'tarih': '2026-10-03', 'cikarilan': addr('e'), 'alinan': addr('f'), 'gerekce': 'hareketsizlik', 'not': ''}, rules)
    gecis.degisim_yaz(path, {'tarih': '2026-10-03', 'cikarilan': addr('e'), 'alinan': addr('f'), 'gerekce': 'kaldirac_ihlali', 'not': ''}, rules)
    with pytest.raises(ValueError, match='gerekçe'):
        gecis.degisim_yaz(path, {'tarih': '2026-11-01', 'cikarilan': addr('a'), 'alinan': addr('b'), 'gerekce': 'serbest_metin', 'not': ''}, rules)


def test_degisim_oda_listesini_gunceller_ve_cikarilan_56_gun_sonra_silinir(tmp_path):
    root = tmp_path / 'copytrade'; root.mkdir()
    listing = root / 'izleme_listesi.yaml'
    listing.write_text(yaml.safe_dump({'traderlar': [{'id': 'O01', 'adres': addr('a'), 'takma_ad': 'aaaa', 'durum': 'izlemede', 't0': '2026-10-01', 'kol': 'oda', 'kollar': ['oda']}]}, sort_keys=False))
    gecis.degisim_uygula(listing, root / 'degisim.jsonl', addr('a'), addr('b'), 'tarz_kaymasi', tarih='2026-10-03')
    rows = yaml.safe_load(listing.read_text())['traderlar']
    assert [(r['adres'], r['kol'], r['t0']) for r in rows] == [(addr('a'), 'cikarilan', '2026-10-01'), (addr('b'), 'oda', '2026-10-03')]
    assert gecis.temizle_cikarilan(listing, '2026-11-28') == 1
    assert len(yaml.safe_load(listing.read_text())['traderlar']) == 1


def test_degisim_raporu_gerekceyi_ayri_ve_sanal_alfayi_yazar(tmp_path):
    record = tmp_path / 'degisim.jsonl'
    gecis.degisim_yaz(record, {'tarih': '2026-10-03', 'cikarilan': addr('a'), 'alinan': addr('b'), 'gerekce': 'kullanici_takdiri', 'not': ''})
    status = tmp_path / 'durum.json'
    status.write_text(json.dumps({'traderlar': [{'adres': addr('a'), 'sanal_kopya': {'toplam': .01}}, {'adres': addr('b'), 'sanal_kopya': {'toplam': .03}}]}))
    result = rapor(record, status)
    assert result['degisimler'][0]['degisim_alfasi'] == pytest.approx(.03)   # ilk raporda çıkarılanın tabanı = .01
    previous = tmp_path / 'degisim.json'
    previous.write_text(json.dumps(result))
    status.write_text(json.dumps({'traderlar': [{'adres': addr('a'), 'sanal_kopya': {'toplam': .02}}, {'adres': addr('b'), 'sanal_kopya': {'toplam': .03}}]}))
    result = rapor(record, status, previous)
    assert result['degisimler'][0]['degisim_alfasi'] == pytest.approx(.02)   # .03 − (.02 − .01)
    assert result['gerekce_toplamlari']['kullanici_takdiri'] == {'adet': 1, 'ortalama_degisim_alfasi': pytest.approx(.02)}


def test_referans_odasi_uyesi_cikarilsa_da_listeden_dusmez(tmp_path):
    listing = tmp_path / 'izleme_listesi.yaml'
    listing.write_text(yaml.safe_dump({'traderlar': [{'id': 'O01', 'adres': addr('a'), 'takma_ad': 'aaaa', 'durum': 'izlemede', 't0': '2026-10-29',
                                                      'kol': 'oda', 'kollar': ['oda'], 'secim': load_rules()['referans_secim']}]}, sort_keys=False))
    gecis.degisim_uygula(listing, tmp_path / 'degisim.jsonl', addr('a'), addr('b'), 'kullanici_takdiri', tarih='2026-10-30')
    old = yaml.safe_load(listing.read_text())['traderlar'][0]
    assert (old['kol'], old['kollar']) == ('cikarilan', ['cikarilan', 'referans_oda'])
    assert gecis.temizle_cikarilan(listing, '2027-06-01') == 0


def test_yetim_pozisyon_hesap_sicramasindan_once_gelir():
    now = timestamp('2026-10-29T00:00:00Z')
    fill = {'coin': 'BTC', 'time': 1, 'side': 'B', 'sz': '1', 'startPosition': '0'}
    report = mutabakat_raporu([fill], [{'assetPositions': []}], now, onceki_hesap_degeri=100.0, hesap_degeri=200.0)
    assert report['saglik']['isik'] == 'kirmizi'


def test_mutabakat_saglik_isigi_altin_ornekleri():
    now = timestamp('2026-10-29T00:00:00Z')
    fill = {'coin': 'BTC', 'time': 1, 'side': 'B', 'sz': '1', 'startPosition': '0'}
    green = mutabakat_raporu([fill], [{'assetPositions': [{'position': {'coin': 'BTC', 'szi': '1'}}]}], now)
    red = mutabakat_raporu([fill], [{'assetPositions': []}], now)
    yellow = mutabakat_raporu([], [{'assetPositions': ['bozuk']}], now)
    assert (green['saglik'], red['saglik'], yellow['saglik']) == (
        {'isik': 'yesil', 'neden': 'mutabakat uyumlu'}, {'isik': 'kirmizi', 'neden': 'yetim pozisyon'}, {'isik': 'sari', 'neden': 'bozuk mutabakat satırı'})
