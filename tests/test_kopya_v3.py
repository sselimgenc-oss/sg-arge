"""Kopya hesap v3 (E2 sabit tutar, docs/GOREV_ETRE_GECIS.md): elle hesaplı altın örnekler.
Maliyet oranı = taker 0,00045 + kayma 0,0005 = 0,00095 (kurallar.yaml). Eğri: `defter.sabit_tutar_egrisi`
(Etre kasa.py Kasa.islem_usd portu, varsayılanlar DEĞİŞTİRİLMEDİ): tutar(1.000$) = 5,2×5**0,86 ≈ 20,754752$."""
import pytest
import pandas as pd

from copytrade import izleme_motoru as m
from copytrade import kopya_v3
from copytrade.defter import sabit_tutar_egrisi
from copytrade.kurallar import load_rules

T0 = pd.Timestamp('2026-10-27T00:00:00Z')
NOW = pd.Timestamp('2026-10-27T12:00:00Z')
ms = lambda s: m.millis(m.timestamp(s))
RULES = load_rules()
TUTAR_1000 = sabit_tutar_egrisi(RULES)(1000.0)             # ≈ 20,754751953822...


def fill(time, side, size, before, price, coin='BTC'):
    return {'time': ms(time), 'coin': coin, 'side': side, 'sz': str(size), 'startPosition': str(before), 'px': str(price),
            'tid': ms(time), 'oid': str(ms(time)), 'closedPnl': '0', 'fee': '0'}


def hourly(**prices):
    return {coin: [{'t': ms(f'2026-10-27T{h}:00Z'), 'o': p} for h, p in rows.items()] for coin, rows in prices.items()}


def run(fills, saatlik, yurutme, funding=(), isaret=None, delay=30):
    execution = {coin: {ms(f'2026-10-27T{h}:00Z'): p for h, p in rows.items()} for coin, rows in yurutme.items()}
    return kopya_v3.hesapla(fills, saatlik, isaret or {}, execution, list(funding), T0, NOW, delay, RULES)


def test_acilis_kopyanin_kendi_1000_degerine_gore_sabit_tutarla():
    # Al 1 BTC 10:00 (yürütme 10:30 @100), sat 11:00 (yürütme 11:30 @110): v1/v2 trader hesabına (1.000 $) oranlı
    # 0,001 ölçekle kopyalardı (1 BTC -> 0,001 BTC); v3 trader'ın işlem büyüklüğüne bakmaz, kopyanın KENDİ 1.000 $
    # değerine göre eğriden sabit tutar açar: own = tutar(1.000)/100/1.000.
    fills = [fill('2026-10-27T10:00:00Z', 'B', 1, 0, 99), fill('2026-10-27T11:00:00Z', 'A', 1, 1, 111)]
    v3 = run(fills, hourly(BTC={'10:00': 99.0, '11:00': 111.0}), {'BTC': {'10:30': 100.0, '11:30': 110.0}})
    own = TUTAR_1000 / 100.0 / 1000.0
    net = own * (110 - 100) - own * 100 * 0.00095 - own * 110 * 0.00095
    assert v3['bakiye_usd'] == pytest.approx(1000 * (1 + net))
    assert v3['tasfiye'] is False and v3['tasfiye_zamani'] is None and v3['kapanis_nedenleri'] == []


def test_acilis_trader_islem_buyuklugunden_bagimsiz():
    # Aynı senaryo, trader 1 BTC yerine 5 BTC alıp satsa bile (before/after oranı aynı: tam açılış, tam kapanış)
    # v3'ün sonucu DEĞİŞMEZ — v1/v2'nin oranlı kopyasından ayrışan asıl nokta.
    buyuk = [fill('2026-10-27T10:00:00Z', 'B', 5, 0, 99), fill('2026-10-27T11:00:00Z', 'A', 5, 5, 111)]
    kucuk = [fill('2026-10-27T10:00:00Z', 'B', 1, 0, 99), fill('2026-10-27T11:00:00Z', 'A', 1, 1, 111)]
    saatlik, yurutme = hourly(BTC={'10:00': 99.0, '11:00': 111.0}), {'BTC': {'10:30': 100.0, '11:30': 110.0}}
    v3_buyuk = run(buyuk, saatlik, yurutme)
    v3_kucuk = run(kucuk, saatlik, yurutme)
    assert v3_buyuk['bakiye_usd'] == pytest.approx(v3_kucuk['bakiye_usd'])


def test_ekleme_mevcut_pozisyona_oranla():
    # Açılış (10:00, B10@100, eğriyle); trader %50 ekliyor (11:00, B5, before=10): kopya da kendi pozisyonunun
    # %50'si kadar ekler (eğriden yeniden okumaz — Etre masa.py _ekle).
    fills = [fill('2026-10-27T10:00:00Z', 'B', 10, 0, 100), fill('2026-10-27T11:00:00Z', 'B', 5, 10, 110)]
    v3 = run(fills, hourly(BTC={'10:00': 100.0, '11:00': 110.0, '12:00': 110.0}),
             {'BTC': {'10:30': 100.0, '11:30': 110.0}})
    own = TUTAR_1000 / 100.0 / 1000.0
    ek = own * 0.5
    after = own + ek
    entry = (100 * own + 110 * ek) / after
    net = -(own * 100 * 0.00095) - (ek * 110 * 0.00095) + after * (110 - entry)
    assert v3['bakiye_usd'] == pytest.approx(1000 * (1 + net))


def test_dolum_yoksa_bakiye_1000de_kalir():
    # v3 trader hesabına bakmadığından (v2'nin "geçerli hesap değeri serisi yok" kontrolü burada yok), boş dolum
    # listesi bir hata değil, yalnız hareketsizliktir: bakiye başlangıçta kalır.
    v3 = run([], hourly(BTC={'10:00': 100.0}), {})
    assert v3.get('durum') is None
    assert v3['bakiye_usd'] == pytest.approx(1000.0) and v3['getiri'] == 0.0
