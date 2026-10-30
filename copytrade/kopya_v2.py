"""Kopya hesap v2 (K-9, GOREV_VERI_DUZELTME madde 20-23). v1 (`izleme_motoru.copy_results`) silinmez; ikisi yan yana yayımlanır.

Tek motor: v2, araştırma gölgesiyle AYNI fonksiyonları kullanır (`golge.calistir` → `defter.copy_ledger` + saatlik tasfiye denetimi).
- Tasfiye (madde 21): kopya K/Z'si ayrılmış 1 birimin `golge_likidasyon_esigi`ne (kurallar.yaml, -1,0) inerse pozisyonlar tasfiye edilir;
  sanal özsermaye <= 0 ise bakiye 0'da kalır ve `tasfiye_zamani` yayımlanır.
- Zamanla değişen payda (madde 22): `capital_scale` hesap değeri zaman serisiyle (`hesap_serisi`); `payda_yontemi` etiketli.
- Funding (madde 23): kopyalanan pozisyonun büyüklüğü x saatlik oran; t0 öncesi devralınan pozisyonun funding'i girmez.
"""
from __future__ import annotations

import math

import pandas as pd

from copytrade import golge
from copytrade.defter import HOUR

MINUTE = 60_000
SERI_SINIR = 3000          # hesap_serisi: en çok bu kadar son okuma tutulur (saatlik okumayla ~125 gün)


def hesap_serisi_guncelle(saved: dict, t0_ms: int, now_ms: int, account: float) -> list[list[float]]:
    """Trader'ın hesap değeri okumaları [[ms, değer]]. İlk kayıt t0'da sabitlenen `kopya_paydasi`dır (t0 ↔ ilk okuma arası ilk okuma kullanılır)."""
    series = saved.setdefault('hesap_serisi', [[t0_ms, float(saved.get('kopya_paydasi', account))]])
    if series[-1][0] < now_ms:
        series.append([now_ms, float(account)])
    del series[:-SERI_SINIR]
    return series


def saatlik_mumlar(client, cache: dict, fills: list[dict], open_coins: set[str], now_ms: int) -> dict[str, list[dict]]:
    """Tasfiye denetimi için coin başına saatlik açılışlar. Tamamlanmış saatler `cache`te kalır (artımlı); süren saat her koşuda yeniden okunur."""
    first: dict[str, int] = {}
    last: dict[str, int] = {}
    for fill in fills:
        coin, moment = str(fill['coin']), int(fill['time'])
        first.setdefault(coin, moment)
        last[coin] = max(last.get(coin, 0), moment)
    result: dict[str, list[dict]] = {}
    for coin in first:
        rows = cache.setdefault(coin, {})
        done = max((int(t) for t in rows), default=None)
        start = first[coin] // HOUR * HOUR if done is None else done + HOUR
        end = now_ms if coin in open_coins else last[coin] + HOUR
        running: dict[int, float] = {}
        if start <= end:
            for candle in client.candles(coin, start, end, interval='1h'):
                moment, price = int(candle['t']), float(candle['o'])
                if moment % HOUR or price <= 0 or not math.isfinite(price):
                    continue
                if moment + HOUR <= now_ms:
                    rows[str(moment)] = price
                else:
                    running[moment] = price
        result[coin] = [{'t': int(t), 'o': price} for t, price in sorted({**{int(t): p for t, p in rows.items()}, **running}.items())]
    return result


def hesapla(fills: list[dict], saatlik: dict[str, list[dict]], isaret: dict[str, list[dict]], yurutme: dict[str, dict[int, float]],
            serisi: list[list[float]], funding: list[dict], t0: pd.Timestamp, now: pd.Timestamp, delay: int, style: str) -> dict:
    """v2 sanal kopya sonucu (1.000 $ ölçeğinde). ``fills``: t0 sonrası perp dolumları (kopya eylemleri DEĞİL; devralınan pozisyon `startPosition`
    ile ayıklanır). ``yurutme``: coin -> {hedef_ms: açılış fiyatı} (v1'in dakika mumları); ``isaret``: son 1 dk mum (açık K/Z işareti)."""
    t0_ms, now_ms = int(t0.value // 1_000_000), int(now.value // 1_000_000)
    account = pd.Series([float(v) for _, v in serisi], index=pd.DatetimeIndex([pd.Timestamp(int(t), unit='ms', tz='UTC') for t, _ in serisi]))
    annotated = []
    for fill in fills:
        target = math.ceil((int(fill['time']) + delay * MINUTE) / MINUTE) * MINUTE
        price = yurutme.get(str(fill['coin']), {}).get(target)
        annotated.append(dict(fill, _execution_time=target, _execution_price=price) if price else dict(fill))
    candles = {coin: sorted(saatlik.get(coin, []) + isaret.get(coin, []), key=lambda c: c['t']) for coin in {*saatlik, *isaret}}
    run = golge.calistir(annotated, candles, account, style=style, etiket_ms=t0_ms, end_ms=now_ms, funding=funding, variant='V0', delay_min=delay)
    ledger = run['defter']
    method = 'saatlik_okuma' if len(serisi) >= 2 else 'ilk_okuma'
    base = {'surum': 'v2', 'baslangic_usd': 1000, 'gecikme_dk': delay, 't0': str(t0.date()), 'payda_yontemi': method, 'payda_okuma_sayisi': len(serisi)}
    if ledger.get('net') is None:
        return {**base, 'durum': 'hesaplanamadi', 'neden': 'geçerli hesap değeri serisi yok'}
    days = pd.date_range(t0.normalize(), now.normalize(), freq='1D')
    net = pd.Series(0.0, index=days)
    if len(ledger['daily']):
        net = net.add(ledger['daily'].reindex(days, fill_value=0.0), fill_value=0.0)
    equity = 1000 * (1 + net.cumsum())
    liquidation = [e['zaman_ms'] for e in run['olaylar'] if e.get('durum') == 'likidasyon']
    when, source = (min(liquidation), 'mum') if liquidation else (None, None)
    broke = equity[equity <= 0]
    if when is None and len(broke):
        when, source = int(broke.index[0].value // 1_000_000), 'gunluk_ozsermaye'
    if when is not None:                              # tasfiye: bakiye 0'da kalır, sonrası sermaye yok
        day = pd.Timestamp(int(when), unit='ms', tz='UTC').normalize()
        equity[equity.index >= day] = 0.0
    equity = equity.clip(lower=0.0)
    balance = float(equity.iloc[-1]) if len(equity) else 1000.0
    peak = pd.concat([pd.Series([1000.0]), equity.reset_index(drop=True)]).cummax()
    drawdown = float((1 - pd.concat([pd.Series([1000.0]), equity.reset_index(drop=True)]) / peak).max())
    result = {**base, 'bakiye_usd': balance, 'getiri': balance / 1000 - 1, 'dusus': drawdown,
              'egri': [[str(day.date()), float(value)] for day, value in equity.items()],
              'gerceklesen': ledger['realized'] + ledger['funding'], 'acik': ledger['unrealized_end'], 'toplam': ledger['net'],
              'funding': ledger['funding'], 'maliyet': ledger['costs'], 'fiyatsiz_eylem': int(ledger.get('missing', 0)),
              'tasfiye': when is not None, 'tasfiye_zamani': pd.Timestamp(int(when), unit='ms', tz='UTC').strftime('%Y-%m-%dT%H:%M:%SZ') if when is not None else None,
              'tasfiye_kaynagi': source}
    return result
