"""Kopya hesap v2 (K-9, madde 20-23): elle hesaplı altın örnekler. Maliyet oranı = taker 0,00045 + kayma 0,0005 = 0,00095 (kurallar.yaml)."""
import pytest
import pandas as pd

from copytrade import izleme_motoru as m
from copytrade import kopya_v2

T0 = pd.Timestamp('2026-10-27T00:00:00Z')
NOW = pd.Timestamp('2026-10-27T12:00:00Z')
ms = lambda s: m.millis(m.timestamp(s))


def fill(time, side, size, before, price, coin='BTC'):
    return {'time': ms(time), 'coin': coin, 'side': side, 'sz': str(size), 'startPosition': str(before), 'px': str(price),
            'tid': ms(time), 'oid': str(ms(time)), 'closedPnl': '0', 'fee': '0'}


def hourly(**prices):            # {'BTC': {'10:00': 100.0, ...}} -> saatlik açılışlar
    return {coin: [{'t': ms(f'2026-10-27T{h}:00Z'), 'o': p} for h, p in rows.items()] for coin, rows in prices.items()}


def run(fills, saatlik, yurutme, serisi, funding=(), isaret=None, delay=30):
    execution = {coin: {ms(f'2026-10-27T{h}:00Z'): p for h, p in rows.items()} for coin, rows in yurutme.items()}
    return kopya_v2.hesapla(fills, saatlik, isaret or {}, execution, serisi, list(funding), T0, NOW, delay, 'intraday')


ACCOUNT_1000 = [[ms('2026-10-27T00:00:00Z'), 1000.0]]


def test_tek_motor_v1_ile_ayni_girdi_ayni_sonuc():
    # Al 1 BTC 10:00 (yürütme 10:30 @100), sat 11:00 (yürütme 11:30 @110), hesap 1.000 $ → ölçek 0,001.
    # Brüt 0,001 × 10 = 0,01; maliyet 0,001×100×0,00095 + 0,001×110×0,00095 = 0,0001995 → net 0,0098005 → 1.009,8005 $.
    fills = [fill('2026-10-27T10:00:00Z', 'B', 1, 0, 99), fill('2026-10-27T11:00:00Z', 'A', 1, 1, 111)]
    v2 = run(fills, hourly(BTC={'10:00': 99.0, '11:00': 111.0}), {'BTC': {'10:30': 100.0, '11:30': 110.0}}, ACCOUNT_1000)
    assert v2['bakiye_usd'] == pytest.approx(1009.8005)
    candles = {'BTC': [{'t': ms('2026-10-27T10:30:00Z'), 'o': 100.0}, {'t': ms('2026-10-27T11:30:00Z'), 'o': 110.0}]}
    v1 = m.copy_results(fills, candles, [], 1000, T0, NOW, {})
    assert v1['bakiye_usd'] == pytest.approx(1009.8005)               # v1 ile v2 aynı girdide aynı sayı
    assert v2['tasfiye'] is False and v2['tasfiye_zamani'] is None and v2['payda_yontemi'] == 'ilk_okuma'


def test_tasfiye_bakiye_sifirda_kalir_ve_zaman_yayimlanir():
    # 20 BTC @100 (hesap 1.000 → ölçek 0,001 → kopya 0,02 BTC; trader kaldıracı 2x). 11:00 saatlik işaret 50 → K/Z = 0,02 × (50−100) = −1,0 ≤ −1,0 eşik:
    # 11:00'de tasfiye @50. Gerçekleşen −1,0, maliyet 0,02×100×0,00095 + 0,02×50×0,00095 = 0,00285 → özsermaye 1000×(1−1,00285) < 0 → bakiye 0.
    fills = [fill('2026-10-27T10:00:00Z', 'B', 20, 0, 100)]
    v2 = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 50.0, '12:00': 40.0}), {'BTC': {'10:30': 100.0}}, ACCOUNT_1000)
    assert v2['tasfiye'] is True and v2['tasfiye_kaynagi'] == 'mum'
    assert v2['tasfiye_zamani'] == '2026-10-27T11:00:00Z'
    assert v2['bakiye_usd'] == 0.0 and v2['getiri'] == -1.0
    assert v2['egri'][-1] == ['2026-10-27', 0.0]


def test_tasfiye_olmayan_derin_zarar_negatif_bakiye_uretmez():
    # Aynı pozisyon, işaret 60 → K/Z −0,8 (eşik altında değil): tasfiye yok; açık K/Z −0,8 → özsermaye 1000×(1−0,8−0,0019) ≈ 198,1 > 0.
    fills = [fill('2026-10-27T10:00:00Z', 'B', 20, 0, 100)]
    v2 = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 60.0}), {'BTC': {'10:30': 100.0}}, ACCOUNT_1000,
             isaret={'BTC': [{'t': ms('2026-10-27T11:59:00Z'), 'o': 60.0}]})
    assert v2['tasfiye'] is False
    assert v2['bakiye_usd'] == pytest.approx(1000 * (1 - 0.8 - 0.0019), rel=1e-9)


def test_zamanla_degisen_payda():
    # Hesap 1.000 $ → 10:45'te 2.000 $. 10:00 alımı (ölçek 1/1000) → 0,001 BTC; 11:00 alımı (ölçek 1/2000) → 0,0005 BTC.
    # İşaret fiyatı girişle aynı (100) → açık K/Z 0; yalnız maliyet: 0,001×100×0,00095 + 0,0005×100×0,00095 = 0,0001425 → 999,8575 $.
    serisi = [[ms('2026-10-27T00:00:00Z'), 1000.0], [ms('2026-10-27T10:45:00Z'), 2000.0]]
    fills = [fill('2026-10-27T10:00:00Z', 'B', 1, 0, 100), fill('2026-10-27T11:00:00Z', 'B', 1, 1, 100)]
    v2 = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 100.0}), {'BTC': {'10:30': 100.0, '11:30': 100.0}}, serisi,
             isaret={'BTC': [{'t': ms('2026-10-27T11:59:00Z'), 'o': 100.0}]})
    assert v2['bakiye_usd'] == pytest.approx(999.8575)
    assert v2['payda_yontemi'] == 'saatlik_okuma' and v2['payda_okuma_sayisi'] == 2
    sabit = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 100.0}), {'BTC': {'10:30': 100.0, '11:30': 100.0}}, ACCOUNT_1000,
                isaret={'BTC': [{'t': ms('2026-10-27T11:59:00Z'), 'o': 100.0}]})
    assert sabit['bakiye_usd'] == pytest.approx(1000 * (1 - 0.00019))         # sabit payda: 2 × 0,001 BTC → eski (yanlış) maruziyet


def test_funding_yalniz_kopyalanan_pozisyondan():
    # Trader t0 öncesi 5 BTC devralmış; 10:00'da 1 BTC ekler (startPosition 5). Kopya yalnız eklenen 1 BTC × 0,001 = 0,001 BTC (10:30'dan).
    # Funding saatlik oran 0,01: 11:00 saatinde −0,001 BTC × 100 × 0,01 = −0,001 (kesir). Devralınan 5 BTC'nin funding'i girmez.
    funding = [{'time': ms(f'2026-10-27T{h}:00:00Z'), 'delta': {'coin': 'BTC', 'fundingRate': '0.01', 'usdc': '-5', 'szi': '6'}} for h in ('10', '11', '12')]
    fills = [fill('2026-10-27T10:00:00Z', 'B', 1, 5, 100)]
    v2 = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 100.0}), {'BTC': {'10:30': 100.0}}, ACCOUNT_1000, funding=funding,
             isaret={'BTC': [{'t': ms('2026-10-27T11:59:00Z'), 'o': 100.0}]})
    assert v2['funding'] == pytest.approx(-0.001)
    assert v2['bakiye_usd'] == pytest.approx(1000 * (1 - 0.001 - 0.000095))
    fundingsiz = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 100.0}), {'BTC': {'10:30': 100.0}}, ACCOUNT_1000,
                         isaret={'BTC': [{'t': ms('2026-10-27T11:59:00Z'), 'o': 100.0}]})
    assert fundingsiz['funding'] == 0.0                                      # funding verisi yoksa sıfır


def test_dakika_mumu_funding_izgarasina_girmez():
    # Listede 11:59 işaret mumu olsa da funding'e fazladan saat eklenmez (yukarıdaki test aynı -0,001'i verir); tek başına doğrula.
    from copytrade.defter import FundingRates, Market
    market = Market({'BTC': [{'t': ms('2026-10-27T11:00:00Z'), 'o': 100.0}, {'t': ms('2026-10-27T11:59:00Z'), 'o': 100.0}]})
    times, cum = market.funding_cum('BTC', FundingRates([]))
    assert times == [ms('2026-10-27T11:00:00Z')]


def test_gecikme5_ozeti_altin_ornek():
    # Al 1 BTC @10:00, sat @11:00. 5 dk gecikme: giriş 10:05 @101, çıkış 11:05 @110 → brüt 0,009, maliyet 0,00020045 → 1.008,79955 $.
    # 30 dk gecikme: giriş 10:30 @103, çıkış 11:30 @108 → brüt 0,005, maliyet 0,00020045 → 1.004,79955 $. Fark (getiri) = 0,004.
    fills = [fill('2026-10-27T10:00:00Z', 'B', 1, 0, 100), fill('2026-10-27T11:00:00Z', 'A', 1, 1, 110)]
    saatlik = hourly(BTC={'10:00': 100.0, '11:00': 110.0})
    fast = run(fills, saatlik, {'BTC': {'10:05': 101.0, '11:05': 110.0}}, ACCOUNT_1000, delay=5)
    slow = run(fills, saatlik, {'BTC': {'10:30': 103.0, '11:30': 108.0}}, ACCOUNT_1000, delay=30)
    assert fast['bakiye_usd'] == pytest.approx(1008.79955) and slow['bakiye_usd'] == pytest.approx(1004.79955)
    ozet = m.gecikme5_ozeti([{'gecerli': True, 'sanal_kopya_v2_gecikme5': fast, 'sanal_kopya_v2': slow},
                             {'gecerli': False, 'sanal_kopya_v2_gecikme5': fast, 'sanal_kopya_v2': slow},          # geçersiz üye karşılaştırmaya girmez
                             {'gecerli': True, 'sanal_kopya_v2_gecikme5': {'durum': 'hesaplanamadi'}, 'sanal_kopya_v2': slow}])
    assert ozet['uye'] == 3 and ozet['karsilastirilan'] == 1
    assert ozet['fark'] == pytest.approx(0.004) and ozet['bakiye_usd'] == pytest.approx(1008.79955) and ozet['tasfiye'] == 0


def test_motor_yalniz_oda_uyelerine_gecikme5_ekler(tmp_path):
    import tests.test_izleme as ti
    rows = [{'id': 'O1', 'adres': ti.ADDRESS, 'takma_ad': 'Oda', 'durum': 'izlemede', 't0': str(ti.T0.date()), 'kol': 'oda', 'kollar': ['oda']},
            {'id': 'B1', 'adres': '0x' + '2' * 40, 'takma_ad': 'Taban', 'durum': 'izlemede', 't0': str(ti.T0.date()), 'kol': 'taban', 'kollar': ['taban']}]
    root = ti.project(tmp_path, rows)
    result = m.run(root, root / 'out', ti.Client(), ti.NOW)
    by_id = {t['id']: t for t in result['traderlar']}
    assert 'sanal_kopya_v2_gecikme5' in by_id['O1'] and by_id['O1']['sanal_kopya_v2_gecikme5']['gecikme_dk'] == 5
    assert 'sanal_kopya_v2_gecikme5' not in by_id['B1']
    assert result['gecikme5']['uye'] == 1 and result['gecikme5']['karsilastirilan'] == 1
