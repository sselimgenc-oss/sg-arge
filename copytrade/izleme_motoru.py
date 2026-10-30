"""Saatlik, salt okunur Hyperliquid izleme; yalnız sanal defter üretir.

Dış sözleşme durum.json'dur. Yeniden oynatılabilir ham veriler ve imleçler
motor.json'da ayrı tutulur; başarısız bir koşu iki dosyayı da yayımlamaz.
"""
from __future__ import annotations

import argparse
import copy
import csv
import gzip
import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from copytrade.defter import Market, copy_ledger
from copytrade.kapi import (SLIPPAGE, TAKER, binance_availability, delayed_copy,
                            write_binance_universe)
from copytrade.pozisyon_mutabakat import mutabakat, ozet
from copytrade.olcut import _funding_amount, asset_class, calculate_metrics, closed_round_trips, perp_fills
from copytrade.tarama import PublicClient, RateLimiter
from copytrade import kopya_v2, oda_risk
from copytrade.kurallar import load_rules
from pano.saglik import CUSUM_YELLOW, _cusum, _mdd, blok_bootstrap

MINUTE = 60_000
DAY = 86_400_000
STYLES = {'intraday', 'swing'}
KOLLAR = {'oda', 'kontrol', 'taban', 'elle', 'referans_oda', 'referans_kontrol', 'cikarilan', 'havuz'}


def timestamp(value) -> pd.Timestamp:
    result = pd.Timestamp(value)
    return result.tz_localize('UTC') if result.tzinfo is None else result.tz_convert('UTC')


def iso(value) -> str:
    return timestamp(value).isoformat().replace('+00:00', 'Z')


def at_ms(value: int) -> str:
    return iso(pd.to_datetime(value, unit='ms', utc=True))


def millis(value) -> int:
    return int(timestamp(value).timestamp() * 1000)


def read_json(path: Path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def load_list(path: Path) -> list[dict]:
    rows = yaml.safe_load(path.read_text(encoding='utf-8'))
    if isinstance(rows, dict) and set(rows) == {'traderlar'}:
        rows = rows['traderlar']
    if not isinstance(rows, list):
        raise ValueError('İzleme listesi YAML listesi olmalı (boş liste: []).')
    ids, addresses = set(), set()
    for row in rows:
        required = {'id', 'adres', 'takma_ad', 'durum', 't0'}
        if not isinstance(row, dict) or not required <= set(row) or set(row) - required - {'tarz', 'kol', 'kollar', 'secim', 'cikarilma_tarihi'}:
            raise ValueError('İzleme satırında yalnız id, adres, takma_ad, durum, t0 (ve isteğe bağlı tarz, kol, kollar, secim, cikarilma_tarihi) olmalı.')
        if 'kol' in row and row['kol'] not in KOLLAR:
            raise ValueError('Geçersiz kol.')
        if 'tarz' in row and row['tarz'] not in STYLES:
            raise ValueError('Geçersiz tarz (intraday | swing).')
        if not isinstance(row['id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]+', row['id']):
            raise ValueError('Geçersiz trader id.')
        if not isinstance(row['adres'], str) or not re.fullmatch(r'0x[0-9a-fA-F]{40}', row['adres']):
            raise ValueError('Geçersiz halka açık trader adresi.')
        if not isinstance(row['takma_ad'], str) or not row['takma_ad'].strip():
            raise ValueError('Takma ad boş olamaz.')
        if row['durum'] not in {'kopyala', 'izlemede', 'durdu'}:
            raise ValueError('Geçersiz izleme durumu.')
        row['t0'] = str(row['t0'])
        if pd.isna(timestamp(row['t0'])):
            raise ValueError('Geçersiz t0.')
        if row['id'] in ids or row['adres'].lower() in addresses:
            raise ValueError('Tekrarlanan trader id/adres.')
        ids.add(row['id']); addresses.add(row['adres'].lower())
    return rows


def fill_key(fill: dict) -> str:
    # tid may be numeric or a string in retained JSON; coin disambiguates markets.
    identity = [fill.get('coin'), str(fill['tid'])] if 'tid' in fill else fill
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24]


def merge_rows(old: list[dict], new: list[dict], key=fill_key) -> list[dict]:
    rows = {key(row): row for row in old}
    for row in new:
        rows.setdefault(key(row), row)
    return sorted(rows.values(), key=lambda row: int(row['time']))


def funding_key(row: dict) -> str:
    return json.dumps([row['time'], row.get('delta', {}).get('coin'), row.get('hash'),
                       _funding_amount(row)], sort_keys=True)


def funding_since(client, address: str, start: int, end: int) -> list[dict]:
    result = []
    while start <= end:
        page = client.info({'type': 'userFunding', 'user': address, 'startTime': start, 'endTime': end})
        if not isinstance(page, list):
            raise ValueError('Geçersiz funding yanıtı.')
        result = merge_rows(result, page, funding_key)
        if len(page) < 500:
            return result
        newest = max(int(row['time']) for row in page)
        if newest <= start:
            raise ValueError('Funding zaman imleci ilerlemiyor; veri eksik olabilir.')
        start = newest  # overlap boundary; deduplicate
    return result


def order_id(fill: dict) -> str:
    value = fill.get('oid')
    if value is None or str(value) == '':
        raise ValueError('Dolumda oid eksik; olay güvenle üretilemez.')
    return str(value)


def event_id(trader: str, oid: str, kind: str) -> str:
    return f'{trader}-{oid}-{kind}'


def event_oid(event: dict) -> str:
    prefix = f"{event['trader']}-"
    suffix = f"-{event['tur']}"
    value = str(event['id'])
    if not value.startswith(prefix) or not value.endswith(suffix):
        raise ValueError('Geçersiz emir olay kimliği.')
    return value[len(prefix):-len(suffix)]


def order_fills(fills: list[dict]) -> list[list[dict]]:
    """Group all fills belonging to one Hyperliquid order in deterministic order."""
    grouped: dict[str, list[dict]] = {}
    for fill in sorted(perp_fills(fills), key=lambda item: (int(item['time']), str(item.get('tid', '')))):
        grouped.setdefault(order_id(fill), []).append(fill)
    return sorted(grouped.values(), key=lambda rows: (int(rows[0]['time']), order_id(rows[0])))


def fill_events(trader: str, fills: list[dict], account: float, positions: list[dict]) -> list[dict]:
    """Emit one event per order; partial fills never become false size changes."""
    result = []
    by_coin = {p['coin']: p for p in positions}
    for rows in order_fills(fills):
        fill = rows[-1]
        oid = order_id(fill)
        before = float(rows[0].get('startPosition', 0))
        signed = sum(float(item['sz']) * (-1 if item['side'] == 'A' else 1) for item in rows)
        after = before + signed
        if abs(after) < 1e-10:
            after = 0.0
        price = sum(float(item['px']) * abs(float(item['sz'])) for item in rows) / sum(abs(float(item['sz'])) for item in rows)
        kinds = []
        if before and (not after or before * after < 0):
            kinds.append(('kapanis', before))
        if after and (not before or before * after < 0):
            kinds.append(('acilis', after))
        elif before * after > 0 and abs(abs(after) / abs(before) - 1) > .25 + 1e-12:
            kinds.append(('buyutme' if abs(after) > abs(before) else 'azaltma', after))
        for kind, size in kinds:
            position = by_coin.get(fill['coin'], {})
            event = {'id': event_id(trader, oid, kind), 'zaman': at_ms(int(fill['time'])),
                     'trader': trader, 'tur': kind, 'coin': fill['coin'],
                     'yon': 'long' if size > 0 else 'short', 'fiyat': price,
                     'hesap_payi': abs(after * price) / account if account > 0 else 0.0,
                     'kaldirac': position.get('kaldirac', abs(size * float(fill['px'])) / account if account > 0 else 0.0), 'not': ''}
            if kind in {'acilis', 'buyutme'}:
                event['sanal_sonuc'] = {'durum': 'acik', 'net_yuzde': None, 'kapanis': None}
            result.append(event)
    return result


def health_denominator(portfolio: list, t0: pd.Timestamp) -> float:
    """Freeze the health denominator at t0 so later account-value changes cannot rewrite history."""
    data = dict(portfolio).get('perpAllTime') or dict(portfolio).get('allTime') or {}
    values = pd.Series({pd.to_datetime(t, unit='ms', utc=True): float(v)
                        for t, v in data.get('accountValueHistory', [])}, dtype=float).sort_index()
    positive = values[values > 0]
    at_or_before = positive[positive.index <= t0]
    selected = at_or_before.iloc[-1] if len(at_or_before) else (positive[positive.index >= t0].iloc[0] if len(positive[positive.index >= t0]) else None)
    if selected is None:
        raise ValueError('t0 için pozitif hesap değeri yok; sağlık hesaplanamaz.')
    return float(selected)


def portfolio_curve(portfolio: list, now: pd.Timestamp, denominator: float) -> pd.Series:
    periods = dict(portfolio)
    data = periods.get('perpAllTime') or periods.get('allTime') or {}
    pnl = pd.Series({pd.to_datetime(t, unit='ms', utc=True): float(v)
                     for t, v in data.get('pnlHistory', [])}, dtype=float).sort_index()
    if pnl.empty or denominator <= 0:
        raise ValueError('Portfolio PnL/pozitif t0 hesap değeri eksik; sağlık hesaplanamaz.')
    pnl = pnl[pnl.index <= now].resample('1D').last().ffill()
    return pnl / denominator


def health(history: pd.Series, t0: pd.Timestamp, now: pd.Timestamp, leverage: float,
           martingale: bool, last_fill: int | None, performans_konisi: bool | None = None) -> dict:
    """Pilotta (``saglik_performans_konisi: false``) ışık yalnız veri bayatlığı ve kaldıraca bakar (K-6: performans sızmaz)."""
    if performans_konisi is None:
        performans_konisi = bool(load_rules()['saglik_performans_konisi'])
    daily = history.diff().dropna()
    before, live = daily[daily.index < t0], daily[daily.index >= t0]
    red, yellow = [], []
    # Additive PnL / account -> daily equity returns, for shared compounded bootstrap/CUSUM.
    def returns(series):
        equity = 1 + pd.concat([pd.Series([0.0], index=[series.index[0] - pd.Timedelta(days=1)]), series.cumsum()])
        return equity.pct_change().iloc[1:]
    if not performans_konisi:
        pass
    elif before.empty:
        yellow.append('t0 öncesi koni geçmişi yetersiz')
    elif len(live):
        base_returns, live_returns = returns(before), returns(live)
        cone = blok_bootstrap(base_returns, len(live), quantiles=(5, 20), block_size=28)
        actual = float(live.sum())
        if actual < cone['p5'][-1]:
            red.append('koni %5 altında')
        elif actual < cone['p20'][-1]:
            yellow.append('koni %5–%20 bandında')
        if _mdd(pd.concat([pd.Series([0.0]), live_returns])) > _mdd(pd.concat([pd.Series([0.0]), base_returns])) * 1.5:
            red.append('düşüş geçmişin 1,5 katından fazla')
        cusum = _cusum(live_returns, base_returns)
        if cusum is not None and cusum >= CUSUM_YELLOW:
            yellow.append('CUSUM uyarısı')
    if leverage > 10:
        red.append('gerçek kaldıraç > 10x')
    elif leverage >= 3:
        yellow.append('gerçek kaldıraç 3–10x')
    if martingale:
        red.append('martingale işareti')
    if last_fill is None or millis(now) - last_fill >= 30 * DAY:
        yellow.append('son 30 günde işlem yok')
    return {'isik': 'kirmizi' if red else 'sari' if yellow else 'yesil',
            'nedenler': red + yellow or (['konide', 'kaldıraç normal'] if performans_konisi else ['kaldıraç normal'])}


def cached_candle(value: object) -> tuple[float, bool]:
    """Read both v1 numeric entries and v1.2 entries with their price source."""
    if isinstance(value, dict):
        return float(value['fiyat']), bool(value.get('yaklasik', False))
    return float(value), False


def execution_candles(client, fills: list[dict], cache: dict, now_ms: int, delay: int = 30,
                      eksik: set | None = None) -> tuple[dict[str, list[dict]], bool]:
    """Use 1m opens when retained; fall back to the matching 1h opening, never a later price.

    ``eksik`` verilirse fiyatı bulunamayan (coin, hedef_ms) çiftleri hata yerine bu kümeye yazılır (madde 2:
    tek eksik mum bütün trader'ı düşürmez); verilmezse eski davranış: ValueError."""
    needed = {}
    approximate = any(cached_candle(value)[1] for rows in cache.values() for value in rows.values())
    for fill in fills:
        target = math.ceil((int(fill['time']) + delay * MINUTE) / MINUTE) * MINUTE
        if target <= now_ms and str(target) not in cache.get(fill['coin'], {}):
            needed.setdefault(fill['coin'], []).append(target)
    for coin, targets in needed.items():
        exact = [target for target in targets if target >= now_ms - 4999 * MINUTE]
        older = [target for target in targets if target < now_ms - 4999 * MINUTE]
        if exact:
            candles = client.candles(coin, min(exact), now_ms, interval='1m')
            prices = {int(c['t']): float(c['o']) for c in candles}
            for target in exact:
                if target not in prices or prices[target] <= 0:
                    if eksik is not None:
                        eksik.add((coin, target))
                        continue
                    raise ValueError(f'{coin}: gecikmeli 1 dk mum eksik ({target}); defter yayımlanmadı.')
                cache.setdefault(coin, {})[str(target)] = {'fiyat': prices[target], 'yaklasik': False}
        if older:
            hourly = client.candles(coin, min(target // (60 * MINUTE) * (60 * MINUTE) for target in older),
                                    now_ms, interval='1h')
            prices = {int(c['t']): float(c['o']) for c in hourly}
            for target in older:
                hour = target // (60 * MINUTE) * (60 * MINUTE)
                if hour not in prices or prices[hour] <= 0:
                    if eksik is not None:
                        eksik.add((coin, target))
                        continue
                    raise ValueError(f'{coin}: gecikmeli 1 saat mum eksik ({hour}); defter yayımlanmadı.')
                cache.setdefault(coin, {})[str(target)] = {'fiyat': prices[hour], 'yaklasik': True}
                approximate = True
    return ({coin: [{'t': int(t), 'o': cached_candle(value)[0]} for t, value in rows.items()]
             for coin, rows in cache.items()}, approximate)


def open_copy_coins(actions: list[dict]) -> set[str]:
    """Kopya eylemlerinin net işaretli toplamı sıfır olmayan coinler: pencere sonunda açık pozisyonu olanlar (işaretlenecek)."""
    net: dict[str, float] = {}
    for action in actions:
        net[action['coin']] = net.get(action['coin'], 0.0) + float(action['sz']) * (-1 if action['side'] == 'A' else 1)
    return {coin for coin, size in net.items() if abs(size) > 1e-10}


def mark_candles(client, actions: list[dict], now_ms: int) -> dict[str, list[dict]]:
    """Açık kopya pozisyonlu her coin için en son 1 dk mumun açılışı (işaretleme fiyatı); mumun zamanı da taşınır (işaret yaşı)."""
    marks: dict[str, list[dict]] = {}
    for coin in sorted(open_copy_coins(actions)):
        rows = [c for c in client.candles(coin, now_ms - 15 * MINUTE, now_ms, interval='1m') if int(c['t']) <= now_ms and float(c['o']) > 0]
        if rows:
            last = max(rows, key=lambda c: int(c['t']))
            marks[coin] = [{'t': int(last['t']), 'o': float(last['o'])}]
    return marks


def copy_actions(fills: list[dict]) -> list[dict]:
    """Copy post-t0 changes only; closing inherited exposure must not open an inverse position."""
    positions, result = {}, []
    for fill in fills:
        coin = fill['coin']
        before = float(fill.get('startPosition', 0))
        signed = float(fill['sz']) * (-1 if fill['side'] == 'A' else 1)
        held = positions.get(coin, 0.0)
        if before * signed < 0:
            leader_close = min(abs(before), abs(signed))
            close = min(abs(held), leader_close) if held * before > 0 else 0.0
            signed = (close + max(0.0, abs(signed) - leader_close)) * (1 if signed > 0 else -1)
        if abs(signed) > 1e-10:
            result.append(dict(fill, sz=str(abs(signed)), startPosition=str(held)))
        positions[coin] = held + signed
    return result


def fiyatli_eylemler(mature: list[dict], prices: dict, delay: int) -> tuple[list[dict], int, dict[str, float]]:
    """Fiyatlanamayan eylemleri ayırır; kalanları defterdeki gerçek elde tutulana göre kırpar.

    Dönüş: (deftere girecek eylemler, fiyatsız eylem sayısı, coin → fiyatsız eylemlerin net işaretli miktarı).
    """
    held: dict[str, float] = {}
    kept, net, count = [], {}, 0
    for fill in mature:
        coin = fill['coin']
        signed = float(fill['sz']) * (-1 if fill['side'] == 'A' else 1)
        execution = math.ceil((int(fill['time']) + delay * MINUTE) / MINUTE) * MINUTE
        if execution not in prices.get(coin, {}):
            count += 1
            net[coin] = net.get(coin, 0.0) + signed
            continue
        current = held.get(coin, 0.0)
        if current * signed < 0 and abs(signed) > abs(current):
            signed = -current                      # fazlası ters pozisyon açardı: at
        if abs(signed) < 1e-10:
            continue
        # Elde yokken azaltma/kapama (önceki açılış fiyatsızdı): deftere girmez.
        if current == 0.0 and float(fill.get('startPosition', 0)) * signed < 0:
            continue
        held[coin] = current + signed
        kept.append(dict(fill, sz=str(abs(signed)), startPosition=str(current)))
    return kept, count, net


def copy_results(fills: list[dict], candles: dict, funding: list[dict], account: float,
                 t0: pd.Timestamp, now: pd.Timestamp, events: dict, approximate: bool = False, delay: int = 30,
                 fiyatsiz_izin: bool = False) -> dict:
    prices = {coin: {int(c['t']): float(c['o']) for c in rows} for coin, rows in candles.items()}
    # Pending fills are not charged before their execution time (tarza göre gecikme: intraday 30, swing 120 dk).
    mature = [f for f in fills if math.ceil((int(f['time']) + delay * MINUTE) / MINUTE) * MINUTE <= millis(now)]
    # Fiyatsız eylem (yürütme mumu yok): yalnız o eylem defter dışı kalır, sayılır ve raporlanır. Defter ters pozisyon
    # doğurmasın diye sonraki eylemler defterdeki gerçek elde tutulana göre kırpılır (fazlalık atılır, elde yokken azaltma atılır).
    fiyatsiz_eylem, fiyatsiz_net = 0, {}
    if fiyatsiz_izin:
        mature, fiyatsiz_eylem, fiyatsiz_net = fiyatli_eylemler(mature, prices, delay)
    days = pd.date_range(t0.normalize(), now.normalize(), freq='1D')
    # Sonuç kanonik defterden (defter.copy_ledger) gelir: gerçekleşmiş + açık (işaretlenmiş) K/Z ayrı yayımlanır.
    ledger_fills = []
    for fill in mature:
        execution = math.ceil((int(fill['time']) + delay * MINUTE) / MINUTE) * MINUTE
        if execution not in prices.get(fill['coin'], {}):
            raise ValueError('Sanal defterde eksik mum var.')
        ledger_fills.append(dict(fill, _execution_time=execution, _execution_price=prices[fill['coin']][execution]))
    market = Market(candles)
    ledger = copy_ledger(ledger_fills, market, account, delay, millis(t0), millis(now), daily=True)
    if ledger['net'] is None:
        raise ValueError('Sanal defter için pozitif hesap değeri gerekli.')
    net = pd.Series(0.0, index=days)
    if len(ledger['daily']):
        net = net.add(ledger['daily'].reindex(days, fill_value=0.0), fill_value=0.0)
    funding_frac = 0.0
    for row in funding:                     # trader'ın funding'i hesap değerine oranlanır (kopya, trader'ı hesap oranıyla yansıtır)
        amount = _funding_amount(row) / account
        funding_frac += amount
        day = pd.Timestamp(int(row['time']), unit='ms', tz='UTC').normalize()
        if day in net.index:
            net[day] += amount
    equity = 1000 * (1 + net.cumsum())
    # FIFO lots allocate realized return and exact friction/funding to the event
    # that opened/increased them. An event may contain many partial fills/lots;
    # it closes only after every lot belonging to that event closes.
    lots = {}
    event_totals: dict[str, dict[str, float]] = {}
    event_by_order = {(e['trader'], event_oid(e)): e['id'] for e in events.values()
                      if e['tur'] in {'acilis', 'buyutme'}}
    trader_id = next((e['trader'] for e in events.values()), '')
    timeline = [(math.ceil((int(f['time']) + delay * MINUTE) / MINUTE) * MINUTE, 0, f) for f in mature]
    timeline += [(int(f['time']), 1, f) for f in funding]
    for time_ms, kind, row in sorted(timeline, key=lambda x: (x[0], x[1])):
        coin = row.get('coin') if kind == 0 else row.get('delta', {}).get('coin')
        active = lots.setdefault(coin, [])
        if kind == 1:
            total = sum(lot['remaining'] for lot in active)
            for lot in active:
                amount = _funding_amount(row) * lot['remaining'] / total if total else 0.0
                lot['pnl'] += amount
                if lot['event']:
                    event_totals[lot['event']]['pnl'] += amount
            continue
        execution = math.ceil(time_ms / MINUTE) * MINUTE
        price = prices[coin][execution]
        signed = float(row['sz']) * (-1 if row['side'] == 'A' else 1)
        remaining = abs(signed)
        direction = 1 if signed > 0 else -1
        while remaining > 1e-10 and active and active[0]['direction'] != direction:
            lot = active[0]
            closed = min(lot['remaining'], remaining)
            realized = closed * ((price - lot['price']) * lot['direction'] - price * (TAKER + SLIPPAGE))
            lot['pnl'] += realized
            if lot['event']:
                event_totals[lot['event']]['pnl'] += realized
            lot['remaining'] -= closed; remaining -= closed
            if lot['event']:
                total_event = event_totals[lot['event']]
                total_event['remaining'] -= closed
                if total_event['remaining'] < 1e-10 and lot['event'] in events:
                    events[lot['event']]['sanal_sonuc'] = {
                        'durum': 'kapandi', 'net_yuzde': total_event['pnl'] / total_event['notional'],
                        'kapanis': at_ms(execution)}
            if lot['remaining'] < 1e-10:
                active.pop(0)
        if remaining > 1e-10:
            ident = event_by_order.get((trader_id, order_id(row)), '')
            notional, entry_cost = remaining * price, -remaining * price * (TAKER + SLIPPAGE)
            active.append({'remaining': remaining, 'direction': direction, 'price': price,
                           'notional': notional, 'pnl': entry_cost, 'event': ident})
            if ident:
                total_event = event_totals.setdefault(ident, {'remaining': 0.0, 'notional': 0.0, 'pnl': 0.0})
                total_event['remaining'] += remaining
                total_event['notional'] += notional
                total_event['pnl'] += entry_cost
    # Sanal açık lotlar (1.000 $ kopya ölçeğinde): trader'ın coin miktarı × 1000 / kopya_paydasi. Giriş = gecikmeli yürütme fiyatı (FIFO ağırlıklı ort.).
    scale = 1000.0 / account
    acik_lotlar = []
    for coin, active in sorted(lots.items()):
        size = sum(lot['remaining'] for lot in active)
        if size < 1e-10:
            continue
        direction = active[0]['direction']
        entry = sum(lot['remaining'] * lot['price'] for lot in active) / size
        found = market.mark_at(coin, millis(now))
        quantity = size * scale
        row = {'coin': coin, 'yon': 'long' if direction > 0 else 'short', 'miktar': quantity, 'giris_fiyati': entry,
               'isaret_fiyati': found[1] if found else None, 'isaret_zamani': at_ms(found[0]) if found else None}
        row['notional_usd'] = quantity * (found[1] if found else entry)
        row['acik_kz_usd'] = quantity * (found[1] - entry) * direction if found else None
        acik_lotlar.append(row)
    peak = np.maximum.accumulate(np.r_[1000.0, equity.to_numpy()])
    drawdown = float(np.max(1 - np.r_[1000.0, equity.to_numpy()] / peak)) if len(equity) else 0.0
    balance = float(equity.iloc[-1]) if len(equity) else 1000.0
    result = {'baslangic_usd': 1000, 'bakiye_usd': balance, 'getiri': balance / 1000 - 1,
            'dusus': drawdown, 'gecikme_dk': delay, 't0': str(t0.date()),
            'egri': [[str(day.date()), float(value)] for day, value in equity.items()],
            # hesap değerine oranlı kesirler: gerçekleşmiş (maliyet + funding dahil), açık (işaretlenmiş) ve toplam; son işaret zamanı
            'gerceklesen': ledger['realized'] + funding_frac, 'acik': ledger['unrealized_end'], 'toplam': ledger['net'] + funding_frac,
            'son_isaret': at_ms(ledger['mark_time']) if ledger['mark_time'] is not None else None, 'isaret_eksik': int(ledger['mark_missing']),
            'eksik_degerleme': bool(ledger['mark_missing']), 'kopya_paydasi': account, 'acik_lotlar': acik_lotlar}
    result['fiyatsiz_eylem'] = fiyatsiz_eylem
    result['fiyatsiz_coinler'] = sorted(fiyatsiz_net)
    # Fiyatsız eylemlerin net işaretli toplamı sıfır değilse o coinde gerçek kopya pozisyonu defterden farklı olabilir.
    result['fiyatsiz_acik_coinler'] = sorted(coin for coin, size in fiyatsiz_net.items() if abs(size) > 1e-10)
    notes = (['yaklaşık fiyat'] if approximate else []) + (['eksik işaretleme'] if ledger['mark_missing'] else []) \
        + (['fiyatsız eylem'] if fiyatsiz_eylem else [])
    if notes:
        result['not'] = ', '.join(notes)
    return result


def positions_from_state(states: list[dict], fills: list[dict], symbols: set[str] | None, now: pd.Timestamp) -> tuple[float, list[dict]]:
    account = sum(float(state['marginSummary']['accountValue']) for state in states)
    result = []
    for state in states:
        for item in state['assetPositions']:
            p = item['position']
            size = float(p['szi'])
            if not size:
                continue
            coin = p['coin']
            openings = [f for f in fills if f['coin'] == coin and
                        (float(f.get('startPosition', 0)) == 0 or
                         float(f.get('startPosition', 0)) * (float(f.get('startPosition', 0)) +
                         float(f['sz']) * (-1 if f['side'] == 'A' else 1)) < 0)]
            result.append({'coin': coin, 'sinif': asset_class(coin), 'yon': 'long' if size > 0 else 'short',
                           'giris': float(p['entryPx']), 'buyukluk_usd': abs(float(p['positionValue'])),
                           'hesap_payi': abs(float(p['positionValue'])) / account if account > 0 else 0.0,
                           'kaldirac': float(p['leverage']['value']), 'anlik_kz_usd': float(p['unrealizedPnl']),
                           'acilis': at_ms(int(openings[-1]['time'])) if openings else '',
                           'binance': binance_availability(coin, symbols)})
    return account, result


def defter_pozisyonlari(fills: list[dict]) -> dict[str, float]:
    """Dolumlardan türetilen pozisyon (kaynak birimi): her coinin son dolumundan sonraki işaretli büyüklük (``startPosition`` + dolum)."""
    last: dict[str, tuple[int, float]] = {}
    for fill in sorted(perp_fills(fills), key=lambda f: int(f['time'])):
        signed = float(fill['sz']) * (-1 if fill['side'] == 'A' else 1)
        last[fill['coin']] = (int(fill['time']), float(fill.get('startPosition', 0)) + signed)
    return {coin: size for coin, (_, size) in last.items()}


def mutabakat_raporu(fills: list[dict], states: list[dict], now: pd.Timestamp, rules: dict | None = None,
                      onceki_hesap_degeri: float | None = None, hesap_degeri: float | None = None) -> dict:
    """Oda üyesi için defter ↔ ``clearinghouseState`` mutabakatı (A13): yalnız rapor; hiçbir pozisyon kapatılmaz, defter değişmez.
    ``veri_kalitesi.mutabakat``: durum sayıları, ``uyumsuz_oran``, ``yetim_coinler``, atlanan bozuk satır, zaman."""
    rules = rules or load_rules()
    exchange = {'assetPositions': [item for state in states for item in state.get('assetPositions', [])]}
    rows, broken = mutabakat(defter_pozisyonlari(fills), exchange, float(rules['mutabakat_goreli_tolerans']), float(rules['mutabakat_mutlak_tolerans']))
    summary = ozet(rows)
    jump = (abs(hesap_degeri / onceki_hesap_degeri - 1) if onceki_hesap_degeri and hesap_degeri else 0.0)
    health = mutabakat_sagligi(summary, broken, jump, rules)
    return {**summary, 'saglik': health, 'hesap_degeri_sicramasi': jump, 'yetim_coinler': [r['coin'] for r in rows if r['durum'] == 'yetim'],
            'sorunlu': [r for r in rows if r['durum'] != 'uyumlu'], 'bozuk_satir': broken, 'zaman': iso(now)}


def mutabakat_sagligi(summary: dict, broken: int, jump: float, rules: dict) -> dict:
    # Kırmızı nedenler sarıdan önce gelir: sıçrama, yetim pozisyonu gizlememeli.
    if summary['yetim']:
        health = {'isik': 'kirmizi', 'neden': 'yetim pozisyon'}
    elif summary['uyumsuz_oran'] >= float(rules['mutabakat_saglik_kirmizi_uyumsuz_oran']):
        health = {'isik': 'kirmizi', 'neden': 'pozisyon oranı uyumsuz'}
    elif jump >= float(rules['mutabakat_saglik_hesap_degeri_sicrama_oran']):
        health = {'isik': 'sari', 'neden': 'teşhis: hesap değeri sıçraması (yatırma/çekme kanıtı değil)'}
    elif summary['uyumsuz_oran'] >= float(rules['mutabakat_saglik_sari_uyumsuz_oran']):
        health = {'isik': 'sari', 'neden': 'kaçırılmış dolum olasılığı'}
    elif broken:
        health = {'isik': 'sari', 'neden': 'bozuk mutabakat satırı'}
    else:
        health = {'isik': 'yesil', 'neden': 'mutabakat uyumlu'}
    return health


def sanal_defter_mutabakati(actions: list[dict], paper: dict, now: pd.Timestamp, delay: int, rules: dict | None = None) -> dict:
    """Sanal defter mutabakatı (madde 7): "trader geçmişi" mutabakatından AYRI ışık. Beklenen = yürütmesi gelmiş kopya eylemlerinin coin başına net
    işaretli toplamı (trader birimi); gerçek = sanal defterin açık lotları (trader birimine çevrilmiş). Satır anlamı: ``defter`` = beklenen, ``borsa`` = sanal defter;
    ``yetim`` = beklenen pozisyon var ama sanal lot yok (ör. fiyatsız eylem), ``eksik`` = sanal lot var ama beklenen yok. Yalnız rapor."""
    rules = rules or load_rules()
    expected: dict[str, float] = {}
    for action in actions:
        if math.ceil((int(action['time']) + delay * MINUTE) / MINUTE) * MINUTE <= millis(now):
            expected[action['coin']] = expected.get(action['coin'], 0.0) + float(action['sz']) * (-1 if action['side'] == 'A' else 1)
    expected = {coin: size for coin, size in expected.items() if abs(size) > 1e-10}
    unit = float(paper.get('kopya_paydasi') or 0.0) / 1000.0         # 1.000 $ ölçeğinden trader birimine
    book = {'assetPositions': [{'position': {'coin': lot['coin'], 'szi': str((1 if lot['yon'] == 'long' else -1) * lot['miktar'] * unit)}}
                               for lot in paper.get('acik_lotlar', [])]}
    rows, broken = mutabakat(expected, book, float(rules['mutabakat_goreli_tolerans']), float(rules['mutabakat_mutlak_tolerans']))
    summary = ozet(rows)
    return {**summary, 'saglik': mutabakat_sagligi(summary, broken, 0.0, rules), 'yetim_coinler': [r['coin'] for r in rows if r['durum'] == 'yetim'],
            'sorunlu': [r for r in rows if r['durum'] != 'uyumlu'], 'bozuk_satir': broken, 'fiyatsiz_coinler': paper.get('fiyatsiz_coinler', []), 'zaman': iso(now)}


def gate_result(root: Path, address: str) -> dict:
    for path in sorted((root / 'copytrade/kapi').glob('*/sonuc.csv'), reverse=True):
        with path.open(encoding='utf-8', newline='') as handle:
            for row in csv.DictReader(handle):
                if row['address'].lower() == address.lower():
                    return {'sinif': row['sinif'] if row['sinif'] in {'Geçti', 'Yetersiz', 'Kaldı'} else 'Yetersiz',
                            'tarih': path.parent.name, 'not': row.get('neden', '')}
    return {'sinif': 'Yetersiz', 'tarih': '', 'not': 'Kapı sonucu bulunamadı'}


def gate_style(root: Path, address: str) -> str | None:
    """Adresin en son kapı sonucundaki ``tarz`` (intraday | swing | scalp); sonuç veya sütun yoksa ``None``."""
    for path in sorted((root / 'copytrade/kapi').glob('*/sonuc.csv'), reverse=True):
        with path.open(encoding='utf-8', newline='') as handle:
            for row in csv.DictReader(handle):
                if row['address'].lower() == address.lower():
                    return row.get('tarz') or None
    return None


def resolve_style(root: Path, row: dict) -> str:
    """İzleme listesindeki ``tarz``; yoksa kapı sonucundan; ikisi de yoksa ``bilinmiyor`` (gecikme 30 dk)."""
    return row.get('tarz') or gate_style(root, row['adres']) or 'bilinmiyor'


def delay_for_style(style: str, rules: dict | None = None) -> int:
    """Sanal kopya gecikmesi (dk): intraday 30, swing 120 (kurallar.yaml ``kopya_gecikme_dk``); scalp/bilinmiyor 30."""
    rules = rules or load_rules()
    return int(rules['kopya_gecikme_dk']['swing' if style == 'swing' else 'intraday'])


def perp_dex_names(response: object) -> list[str]:
    """Return every public HIP-3 dex name exactly once, in API order."""
    if not isinstance(response, list):
        raise ValueError('Geçersiz perpDexs yanıtı.')
    names: list[str] = []
    for dex in response:
        if dex is None:
            continue
        if not isinstance(dex, dict) or not isinstance(dex.get('name'), str) or not dex['name']:
            raise ValueError('Geçersiz perpDexs dex adı.')
        if dex['name'] not in names:
            names.append(dex['name'])
    return names


def clearinghouse_states(client: PublicClient, address: str, dexes: list[str]) -> list[dict]:
    """Read main perpetuals plus each HIP-3 dex; state responses are not interchangeable."""
    states = [client.info({'type': 'clearinghouseState', 'user': address}, weight=2)]
    for dex in dexes:
        states.append(client.info({'type': 'clearinghouseState', 'user': address, 'dex': dex}, weight=2))
    return states


class PerpHesapBos(ValueError):
    """Güncel perp hesap değeri 0: "veri yok" değil "perp hesabı boş/kapalı" (spot bakiye ayrı; madde 3)."""


BAYAT_DK = 180      # önceki başarılı okuma bundan eskiyse durum `bayat` (Worker veri-yaşı uyarısıyla aynı 3 saat)


def veri_durumu(error: Exception | None, yas_dk: float | None = None) -> str:
    """``tamam | fiyatsiz | perp_bos | okuma_hatasi | bayat`` (veri sözleşmesi v1.6; ``fiyatsiz`` başarılı okumada ayrıca atanır)."""
    if error is None:
        return 'tamam'
    if isinstance(error, PerpHesapBos):
        return 'perp_bos'
    return 'bayat' if yas_dk is not None and yas_dk > BAYAT_DK else 'okuma_hatasi'


def with_data_error(trader: dict, error: Exception, now: pd.Timestamp | None = None) -> dict:
    previous = copy.deepcopy(trader)
    short = data_error_reason(error)
    reasons = [reason for reason in previous['saglik']['nedenler'] if not reason.startswith('veri hatası:')]
    previous['saglik']['nedenler'] = reasons + [f'veri hatası: {short}']
    previous['gecerli'] = False
    age = (now - timestamp(previous['veri_zamani'])).total_seconds() / 60 if now is not None and previous.get('veri_zamani') else None
    previous['veri_durumu'] = veri_durumu(error, age)
    return previous


def kol_uyeleri(traderlar: list[dict], kol: str) -> list[dict]:
    """Kol üyeliği ``kollar`` ile (bir adres birden çok kolda olabilir; ana etiket ``kol`` yalnız gösterim içindir)."""
    return [t for t in traderlar if kol in (t.get('kollar') or [t.get('kol')])]


def kapsam(traderlar: list[dict], kol: str) -> dict:
    """Kolun veri kapsamı (üye sayısı ``toplam`` sabit kalır; ITT). Her üye tam bir kovaya düşer:
    ``gecerli`` (``fiyatsiz`` bunun alt kümesidir: trader geçerli, yalnız bazı coinler ölçüm dışı) | ``perp_bos`` | ``yer_tutucu`` (hiç
    okunmadı) | ``bayat`` | ``okuma_hatasi`` (son okuma başarısız, önceki sonuç gösteriliyor). ``kapsama`` = gecerli / toplam (oran).
    ``gecerli_bakiye_usd`` / ``gecersiz_bakiye_usd``: sanal kopya bakiyelerinin ayrı alt toplamları (yer tutucu ve perp_bos hariç).
    """
    result = {'toplam': 0, 'gecerli': 0, 'fiyatsiz': 0, 'perp_bos': 0, 'yer_tutucu': 0, 'bayat': 0, 'okuma_hatasi': 0,
              'kapsama': 0.0, 'gecerli_bakiye_usd': 0.0, 'gecersiz_bakiye_usd': 0.0}
    for trader in kol_uyeleri(traderlar, kol):
        result['toplam'] += 1
        balance = float((trader.get('sanal_kopya') or {}).get('bakiye_usd') or 0.0)
        if trader.get('gecerli', True):
            result['gecerli'] += 1
            result['gecerli_bakiye_usd'] += balance
            if trader.get('veri_durumu') == 'fiyatsiz':
                result['fiyatsiz'] += 1
        elif trader.get('veri_durumu') == 'perp_bos':
            result['perp_bos'] += 1
        elif trader.get('veri_zamani') is None:
            result['yer_tutucu'] += 1
        else:
            result['bayat' if trader.get('veri_durumu') == 'bayat' else 'okuma_hatasi'] += 1
            result['gecersiz_bakiye_usd'] += balance
    result['kapsama'] = result['gecerli'] / result['toplam'] if result['toplam'] else 0.0
    # Kol bazında en eski veri zamanı (madde 19 / C#16): kolun en bayat okuması; ekran yaşı bundan hesaplar, koşu zamanından değil.
    read_times = [t['veri_zamani'] for t in kol_uyeleri(traderlar, kol) if t.get('veri_zamani')]
    result['en_eski_veri_zamani'] = min(read_times) if read_times else None
    # Eksik değerleme (madde 18): açık lotu işaretlenemeyen (işaret yok/bayat) geçerli üye sayısı; >0 ise kol kasası "bilinmiyor" gösterilmeli.
    result['eksik_degerleme'] = sum(1 for t in kol_uyeleri(traderlar, kol) if t.get('gecerli', True) and (t.get('sanal_kopya') or {}).get('eksik_degerleme'))
    # Eğri = kasa (madde 17): eğrisi olmayan geçerli üye "eksik kapsama"dır; eğrinin son noktası geçerli bakiyelerin toplamıyla mutabık olmalı.
    with_curve = [t for t in kol_uyeleri(traderlar, kol) if t.get('gecerli', True) and (t.get('sanal_kopya') or {}).get('egri')]
    result['egri_eksik'] = result['gecerli'] - len(with_curve)
    curve = kasa_egrisi(traderlar, kol)
    balances = sum(float(t['sanal_kopya'].get('bakiye_usd') or 0.0) for t in with_curve)
    result['kasa_son_nokta_usd'] = curve[-1][1] if curve else None
    result['kasa_fark_usd'] = (curve[-1][1] - balances) if curve else None
    result['kasa_mutabik'] = abs(result['kasa_fark_usd']) < 0.5 if curve else (not with_curve)
    return result


def kasa_egrisi(traderlar: list[dict], kol: str, gun: int = 90) -> list[list[object]]:
    """Koldaki GEÇERLİ traderların sanal-kopya bakiyelerinin son ``gun`` günlük toplamı.

    Her trader kendi son bilinen günlük bakiyesiyle taşınır; eksik eğri uydurulmaz. ``gecerli=false`` (eski sonuç ya da
    1.000 $ yer tutucu) toplama girmez, `kapsam` ile ayrı sayılır. Bu isteğe bağlı pano alanıdır, kapı/seçim hesabına girmez.
    """
    curves = []
    for trader in kol_uyeleri(traderlar, kol):
        if not trader.get('gecerli', True):
            continue
        values = {str(day): float(value) for day, value in trader.get('sanal_kopya', {}).get('egri', [])}
        if values:
            curves.append(values)
    dates = sorted({day for curve in curves for day in curve})[-gun:]
    result = []
    for day in dates:
        total = 0.0
        for curve in curves:
            known = [key for key in curve if key <= day]
            if known:
                total += curve[max(known)]
        result.append([day, total])
    return result


def data_error_reason(error: Exception) -> str:
    return str(error).splitlines()[0][:120] or type(error).__name__


def unavailable_trader(root: Path, row: dict, error: Exception) -> dict:
    """Publish an explicit placeholder when a trader has never completed a read."""
    # Pano bu alanları koşulsuz okur; eksik alan sayfanın tamamını bozar.
    style = resolve_style(root, row)
    return {**{k: v for k, v in row.items() if k != 'tarz'}, 'tarz': style, 'veri_zamani': None, 'gecerli': False,
            'kapi': gate_result(root, row['adres']),
            'veri_durumu': veri_durumu(error), 'yer_tutucu': True,
            'saglik': {'isik': 'sari', 'nedenler': [f'veri hatası: {data_error_reason(error)}']},
            'form': {'skor': 0.0, 'getiri_30g': 0.0, 'getiri_90g': 0.0},
            'hesap_degeri': 0.0, 'pozisyonlar': [], 'egri': [],
            'son_islem': {'coin': '', 'yon': '', 'acilis': '', 'kapanis': '', 'net_yuzde': 0.0},
            'sanal_kopya_v2': {'surum': 'v2', 'durum': 'hesaplanamadi', 'yer_tutucu': True, 'neden': 'hiç okunmadı'},
            'sanal_kopya': {'yer_tutucu': True, 'baslangic_usd': 1000, 'bakiye_usd': 1000.0, 'getiri': 0.0, 'dusus': 0.0,
                            'gecikme_dk': delay_for_style(style), 't0': str(timestamp(row['t0']).date()), 'egri': []}}


def yonsuz_guncelle(client, address: str, saved: dict, states: list[dict], fills: list[dict], now: pd.Timestamp) -> dict:
    """Oda ve kontrol üyesi için ``yonsuz_bayrak`` (A26): funding geliri ve spot bakiyesi günde bir kez çekilip ``motor.json``'da önbelleğe alınır; maker payı ve spot↔perp örtüşmesi
    her saat eldeki dolum ve pozisyonlardan hesaplanır. Okunamayan kaynak ``None`` olur ve ``hata`` alanına yazılır (gizlenmez, o gün önbelleğe girmez → sonraki saat yeniden dener)."""
    rules, gun, hatalar = load_rules(), str(now.date()), []
    onbellek = saved.get('yonsuz_onbellek')
    if not onbellek or onbellek.get('gun') != gun:
        onbellek = {'gun': gun, 'funding_usd': None, 'spot': None}
        try:
            start = millis(now) - int(rules['yonsuz_pencere_gun']) * DAY
            onbellek['funding_usd'] = sum(_funding_amount(row) for row in funding_since(client, address, start, millis(now)))
        except Exception as error:
            hatalar.append(f'funding: {data_error_reason(error)}')
        try:
            spot = client.info({'type': 'spotClearinghouseState', 'user': address}, weight=2)
            onbellek['spot'] = {str(b['coin']): float(b['total']) for b in spot.get('balances', []) if float(b.get('total', 0))}
        except Exception as error:
            hatalar.append(f'spot: {data_error_reason(error)}')
        if not hatalar:
            saved['yonsuz_onbellek'] = onbellek
    perp = {item['position']['coin']: float(item['position']['szi']) for state in states for item in state['assetPositions'] if float(item['position']['szi'])}
    return oda_risk.yonsuz_bayrak(onbellek['funding_usd'], oda_risk.toplam_kar(saved.get('portfolio') or [], millis(now), rules), onbellek['spot'], perp, fills, millis(now), rules,
                                  '; '.join(hatalar) or None)


def update_trader(root: Path, client, dexes: list[str], state: dict, all_events: dict,
                  row: dict, now: pd.Timestamp, symbols: set[str] | None, clock=None) -> dict:
    ident, address, t0 = row['id'], row['adres'], timestamp(row['t0'])
    saved = state['traderlar'].setdefault(ident, {'adres': address.lower(), 't0': iso(t0),
                                                   'fills': [], 'funding': [], 'mumlar': {}})
    if saved['adres'] != address.lower() or saved['t0'] != iso(t0):
        raise ValueError(f'{ident}: adres/t0 değiştirilemez; yeni izleme için yeni id kullanın.')
    start = min(millis(t0), millis(now) - 90 * DAY)
    cursor = saved.get('son_dolum', start)
    fresh = client.fills(address, cursor)
    if not isinstance(fresh, list):
        raise ValueError('Geçersiz dolum yanıtı.')
    fills = merge_rows(saved['fills'], [f for f in fresh if int(f['time']) <= millis(now)])
    saved['fills'] = fills
    saved['son_dolum'] = max([cursor] + [int(f['time']) for f in fills])
    # Health is refreshed hourly. The t0 denominator is persisted once and never recalculated.
    saved['portfolio'] = client.portfolio(address)
    # t0 değişirse (liste yeniden başlatılınca) payda yeni t0'a göre bir kez yeniden sabitlenir.
    if saved.get('saglik_paydasi_t0') != str(t0.date()):
        saved['saglik_paydasi'] = health_denominator(saved['portfolio'], t0)
        saved['saglik_paydasi_t0'] = str(t0.date())
    history = portfolio_curve(saved['portfolio'], now, float(saved['saglik_paydasi']))
    states = clearinghouse_states(client, address, dexes)
    read_at = timestamp(clock()) if clock else now    # trader'ın hesap durumunun gerçekten okunduğu an
    account, positions = positions_from_state(states, fills, symbols, now)
    if account == 0:
        raise PerpHesapBos(f'{ident}: perp hesabı boş/kapalı (hesap değeri 0); spot bakiye ayrı, sanal defter hesaplanmadı.')
    if account < 0:
        raise ValueError(f'{ident}: pozitif hesap değeri gerekli; sanal defter hesaplanamadı.')
    saved.setdefault('kopya_paydasi', account)
    copy_fills = [f for f in perp_fills(fills) if int(f['time']) >= millis(t0)]
    new_funding = funding_since(client, address, saved.get('son_funding', millis(t0)), millis(now))
    saved['funding'] = merge_rows(saved['funding'], new_funding, funding_key)
    saved['son_funding'] = max([saved.get('son_funding', millis(t0))] + [int(f['time']) for f in saved['funding']])
    for event in fill_events(ident, copy_fills, account, positions):
        all_events[event['id']] = event
    own_events = {key: event for key, event in all_events.items() if event['trader'] == ident}
    actions = copy_actions(copy_fills)
    style = resolve_style(root, row)
    delay = delay_for_style(style)
    eksik: set = set()
    candles, approximate = execution_candles(client, actions, saved['mumlar'], millis(now), delay, eksik)
    marks = mark_candles(client, actions, millis(now))
    priced = {coin: rows + marks.get(coin, []) for coin, rows in {**{c: [] for c in marks}, **candles}.items()}
    paper = copy_results(actions, priced, saved['funding'], saved['kopya_paydasi'], t0, now, own_events, approximate, delay, fiyatsiz_izin=True)
    # v2 (K-9): tek motor + tasfiye + zamanla değişen payda + yalnız kopyalanan pozisyonun funding'i; v1 ile yan yana, hatası v1'i düşürmez.
    try:
        series = kopya_v2.hesap_serisi_guncelle(saved, millis(t0), millis(now), account)
        hourly = kopya_v2.saatlik_mumlar(client, saved.setdefault('mumlar_1s', {}), copy_fills, open_copy_coins(actions), millis(now))
        paper_v2 = kopya_v2.hesapla(copy_fills, hourly, marks, {coin: {int(c['t']): float(c['o']) for c in rows} for coin, rows in candles.items()},
                                    series, saved['funding'], t0, now, delay, style)
    except Exception as error:
        paper_v2 = {'surum': 'v2', 'durum': 'hesaplanamadi', 'neden': data_error_reason(error)}
    # gecikme5 (K-9, madde 24; tanısal): oda adresleri 5 dk gecikmeyle paralel v2. Telegram yok; birincil analiz değişmez.
    paper_g5 = None
    if 'oda' in (row.get('kollar') or [row.get('kol')]):
        try:
            candles5, _ = execution_candles(client, actions, saved['mumlar'], millis(now), GECIKME5_DK, set())
            paper_g5 = kopya_v2.hesapla(copy_fills, hourly, marks, {coin: {int(c['t']): float(c['o']) for c in rows} for coin, rows in candles5.items()},
                                        series, saved['funding'], t0, now, GECIKME5_DK, style)
        except Exception as error:
            paper_g5 = {'surum': 'v2', 'durum': 'hesaplanamadi', 'neden': data_error_reason(error)}
    leverage = sum(p['buyukluk_usd'] for p in positions) / account
    metrics = calculate_metrics(perp_fills(fills), account_value=account)
    light = health(history, t0, now, leverage, metrics['martingale_signal'],
                   max((int(f['time']) for f in perp_fills(fills)), default=None))
    if saved.get('isik') is not None and light['isik'] != saved['isik']:
        event = {'id': f'{ident}-{millis(now)}-isik', 'zaman': iso(now), 'trader': ident,
                 'tur': 'isik', 'coin': '', 'yon': '', 'fiyat': None, 'hesap_payi': None,
                 'kaldirac': None, 'not': light['isik']}
        all_events[event['id']] = event
    saved['isik'] = light['isik']
    saved['son_olaylar'] = [event for event in all_events.values() if event['trader'] == ident]
    equity = pd.Series([value for _, value in paper['egri']],
                       index=pd.DatetimeIndex([timestamp(day) for day, _ in paper['egri']], tz='UTC'), dtype=float)
    base_30 = equity[equity.index < now.normalize() - pd.Timedelta(days=29)]
    ret30 = float(equity.iloc[-1] / (base_30.iloc[-1] if len(base_30) else 1000) - 1) if len(equity) else 0.0
    recent = history[history.index >= now.normalize() - pd.Timedelta(days=89)]
    volatility = float(recent.diff().dropna().std()) if len(recent) > 2 else 0.0
    trades = closed_round_trips(perp_fills(fills))
    last = trades[-1] if trades else None
    last_trade = {'coin': '', 'yon': '', 'acilis': '', 'kapanis': '', 'net_yuzde': 0.0}
    if last:
        ending = next(f for f in reversed(fills) if f['coin'] == last['coin'] and int(f['time']) == millis(last['close_time']))
        traded = [f for f in fills if f['coin'] == last['coin'] and last['open_time'] is not None
                  and millis(last['open_time']) <= int(f['time']) <= millis(last['close_time'])]
        notional = sum(float(f['px']) * float(f['sz']) for f in traded if float(f.get('closedPnl', 0)) == 0)
        last_trade = {'coin': last['coin'], 'yon': 'long' if float(ending.get('startPosition', 0)) > 0 else 'short',
                      'acilis': iso(last['open_time']) if last['open_time'] is not None else '',
                      'kapanis': iso(last['close_time']), 'net_yuzde': last['net_pnl'] / notional if notional else 0.0}
    trader = {**{k: v for k, v in row.items() if k != 'tarz'}, 'tarz': style, 'veri_zamani': iso(read_at), 'gecerli': True, 'veri_durumu': 'fiyatsiz' if paper.get('fiyatsiz_eylem') else 'tamam',
              'kapi': gate_result(root, address), 'saglik': light,
              'form': {'skor': ret30 / volatility if volatility > 0 and math.isfinite(volatility) else 0.0,
                       'getiri_30g': ret30, 'getiri_90g': float(recent.iloc[-1] - recent.iloc[0]) if len(recent) else 0.0},
              'hesap_degeri': account, 'pozisyonlar': positions, 'son_islem': last_trade,
              'egri': [[str(day.date()), float(value)] for day, value in recent.items()], 'sanal_kopya': paper, 'sanal_kopya_v2': paper_v2}
    if paper_g5 is not None:
        trader['sanal_kopya_v2_gecikme5'] = paper_g5
    if row.get('kol') in oda_risk.YONSUZ_KOLLAR:
        trader['yonsuz_bayrak'] = yonsuz_guncelle(client, address, saved, states, fills, now)
    if row.get('kol') == 'oda':
        history = mutabakat_raporu(fills, states, now, onceki_hesap_degeri=saved.get('son_hesap_degeri'), hesap_degeri=account)
        # `mutabakat` geriye dönük uyumlu takma ad (= trader geçmişi); sanal defter uyumsuzluğu ayrı ışık.
        trader['veri_kalitesi'] = {'mutabakat': history, 'mutabakat_gecmis': history, 'mutabakat_sanal': sanal_defter_mutabakati(actions, paper, now, delay)}
    saved['son_hesap_degeri'] = account
    saved['son_trader'] = trader
    return trader


KOL_SON_OLAY = 200
SAYAC_GUN = 30


def olay_ozeti(all_events: dict, traders: list[dict], now: pd.Timestamp, tam: bool) -> tuple[list[dict], list[dict], dict, dict]:
    """Kesilmemiş olaylardan: kol başına son N olay, günlük sayaçlar ve kapsam (veri sözleşmesi v1.6)."""
    kol_of = {t['id']: t.get('kol', '') for t in traders}
    ordered = sorted(all_events.values(), key=lambda e: (e['zaman'], e['id']), reverse=True)
    taken: dict[str, int] = {}
    recent = []
    for event in ordered:
        kol = kol_of.get(event['trader'], '')
        if taken.get(kol, 0) < KOL_SON_OLAY:
            taken[kol] = taken.get(kol, 0) + 1
            recent.append(event)
    since = (now.normalize() - pd.Timedelta(days=SAYAC_GUN - 1)).strftime('%Y-%m-%d')
    counts: dict[tuple[str, str], dict] = {}
    for event in ordered:
        if event.get('tur') not in {'acilis', 'kapanis'} or event['zaman'][:10] < since:
            continue
        row = counts.setdefault((event['zaman'][:10], kol_of.get(event['trader'], '')), {'acilis': 0, 'kapanis': 0, 'traderlar': set()})
        row[event['tur']] += 1
        row['traderlar'].add(event['trader'])
    sayac = [{'gun': gun, 'kol': kol, 'acilis': row['acilis'], 'kapanis': row['kapanis'], 'trader_sayisi': len(row['traderlar'])}
             for (gun, kol), row in sorted(counts.items(), reverse=True)]
    # Son 24 saat (koşu başlangıcından geriye), kol başına: açılış/kapanış olayı, işlem yapan trader sayısı, sanal sonucu o pencerede biten
    # (sanal_sonuc.kapanis) kopyaların sayısı ve kazananı (net_yuzde > 0). Kesilmemiş olaylardan; yayımlanan olaylar listesi kısalsa da değişmez.
    since_24, until_24 = millis(now) - 24 * 60 * MINUTE, millis(now)
    last_24: dict[str, dict] = {}
    for event in ordered:
        kol = kol_of.get(event['trader'], '')
        row = last_24.setdefault(kol, {'acilis': 0, 'kapanis': 0, 'kapanan': 0, 'kazanan': 0, 'traderlar': set()})
        if event.get('tur') in {'acilis', 'kapanis'} and since_24 <= millis(timestamp(event['zaman'])) <= until_24:
            row[event['tur']] += 1
            row['traderlar'].add(event['trader'])
        outcome = event.get('sanal_sonuc') or {}
        if outcome.get('durum') == 'kapandi' and outcome.get('kapanis') and since_24 <= millis(timestamp(outcome['kapanis'])) <= until_24:
            row['kapanan'] += 1
            row['kazanan'] += 1 if (outcome.get('net_yuzde') or 0) > 0 else 0
    sayac_24s = {kol: {'acilis': r['acilis'], 'kapanis': r['kapanis'], 'trader_sayisi': len(r['traderlar']), 'kapanan': r['kapanan'],
                       'kazanan': r['kazanan']} for kol, r in sorted(last_24.items()) if kol}
    trade_times = [e['zaman'] for e in ordered if e.get('tur') != 'isik']
    scope = {'baslangic': min(trade_times) if trade_times else None, 'tam': bool(tam), 'toplam': len(ordered),
             'kol_basina_son': KOL_SON_OLAY, 'sayac_gun': SAYAC_GUN}
    return recent, sayac, scope, sayac_24s


def write_event_archive(output: Path, all_events: dict) -> None:
    """Kesilmemiş olay arşivi: saat (UTC) başına tek gzip JSONL, ``olaylar/YYYY-MM-DDTHH.jsonl.gz``.

    Değişmez parçalar: bayt-deterministik (mtime=0, sıralı) ve türetilmiş ``sanal_sonuc`` yazılmaz (kapanışta değişir). Böylece geçmiş saat
    dosyaları git'te yeni nesne üretmez; yalnız içinde bulunulan saatin dosyası değişir (veri dalı geçmişi şişmez).
    """
    by_hour: dict[str, list[dict]] = {}
    for event in sorted(all_events.values(), key=lambda e: (e['zaman'], e['id'])):
        by_hour.setdefault(event['zaman'][:13], []).append({k: v for k, v in event.items() if k != 'sanal_sonuc'})
    folder = output / 'olaylar'
    folder.mkdir(parents=True, exist_ok=True)
    for hour, events in by_hour.items():
        lines = ''.join(json.dumps(e, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n' for e in events)
        temporary = folder / f'{hour}.jsonl.gz.tmp'
        with open(temporary, 'wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as handle:
            handle.write(lines.encode('utf-8'))
        temporary.replace(folder / f'{hour}.jsonl.gz')


GECIKME5_DK = 5


def risk_tanisi(traderlar: list[dict], sayac_24s: dict | None = None, rules: dict | None = None) -> dict:
    """Kol başına sanal risk tanısı (madde 25; yalnız tanısal). Girdi: geçerli ve eksik değerlemesiz üyelerin v1 sanal açık lotları (1.000 $ ölçeği).

    ``brut_kaldirac`` = Σ|notional| / sermaye (sermaye = üyelerin v1 sanal bakiyeleri toplamı), ``net_kaldirac`` işaretli (long − short) / sermaye,
    ``en_buyuk_coin_payi`` = tek coinin brüt notional içindeki payı. ``coinler``: coin başına long/short notional (oda ↔ kontrol denge tablosu).
    ``islem_sikligi_24s`` = son 24 saatte üye başına açılış+kapanış. Tavanlar kurallar.yaml'da tanımlıysa (`oda_brut_kaldirac_tavani`,
    `oda_tek_coin_payi_tavani`) aşım ``uyarilar``a yazılır; tanımlı değilse yalnız ölçülür."""
    rules = rules if rules is not None else load_rules()
    result = {}
    for kol in ('oda', 'kontrol'):
        members = [t for t in kol_uyeleri(traderlar, kol) if t.get('gecerli', True) and not (t.get('sanal_kopya') or {}).get('eksik_degerleme')]
        capital = sum(float((t.get('sanal_kopya') or {}).get('bakiye_usd') or 0.0) for t in members)
        coins: dict[str, dict[str, float]] = {}
        for trader in members:
            for lot in (trader.get('sanal_kopya') or {}).get('acik_lotlar', []):
                row = coins.setdefault(lot['coin'], {'long_usd': 0.0, 'short_usd': 0.0})
                row['long_usd' if lot['yon'] == 'long' else 'short_usd'] += float(lot['notional_usd'])
        gross = sum(r['long_usd'] + r['short_usd'] for r in coins.values())
        net = sum(r['long_usd'] - r['short_usd'] for r in coins.values())
        biggest = max(coins.items(), key=lambda item: item[1]['long_usd'] + item[1]['short_usd'], default=(None, None))
        activity = (sayac_24s or {}).get(kol)
        result[kol] = {'uye': len(members), 'sermaye_usd': capital, 'brut_notional_usd': gross, 'net_notional_usd': net,
                       'brut_kaldirac': gross / capital if capital else None, 'net_kaldirac': net / capital if capital else None,
                       'en_buyuk_coin': biggest[0], 'en_buyuk_coin_payi': (biggest[1]['long_usd'] + biggest[1]['short_usd']) / gross if gross else None,
                       'islem_sikligi_24s': (activity['acilis'] + activity['kapanis']) / len(members) if activity and members else None,
                       'coinler': [{'coin': coin, **{k: v for k, v in values.items()}} for coin, values in sorted(coins.items(), key=lambda i: -(i[1]['long_usd'] + i[1]['short_usd']))],
                       'uyarilar': []}
    room = result['oda']
    cap, share = rules.get('oda_brut_kaldirac_tavani'), rules.get('oda_tek_coin_payi_tavani')
    if cap is not None and room['brut_kaldirac'] is not None and room['brut_kaldirac'] > float(cap):
        room['uyarilar'].append(f"oda brüt kaldıraç {room['brut_kaldirac']:.2f}x > tavan {float(cap):.2f}x")
    if share is not None and room['en_buyuk_coin_payi'] is not None and room['en_buyuk_coin_payi'] > float(share):
        room['uyarilar'].append(f"{room['en_buyuk_coin']} payı %{100 * room['en_buyuk_coin_payi']:.0f} > tavan %{100 * float(share):.0f}")
    return result


def gecikme5_ozeti(traderlar: list[dict]) -> dict:
    """`gecikme5` kolu (tanısal): oda üyelerinin 5 dk gecikmeli v2 sonuçları ↔ aynı adreslerin 30/120 dk gecikmeli v2 sonuçları (aynı hesap sürümü, aynı üyeler).

    Yalnız iki taraf da hesaplanabilir ve geçerli olan üyeler karşılaştırılır; getiriler 1.000 $ ölçeğinde kesirdir.
    """
    pairs = [(t['sanal_kopya_v2_gecikme5'], t['sanal_kopya_v2']) for t in traderlar
             if t.get('gecerli', True) and t.get('sanal_kopya_v2_gecikme5', {}).get('bakiye_usd') is not None and t.get('sanal_kopya_v2', {}).get('bakiye_usd') is not None]
    uye = sum(1 for t in traderlar if 'sanal_kopya_v2_gecikme5' in t)
    if not pairs:
        return {'uye': uye, 'karsilastirilan': 0, 'getiri': None, 'oda_v2_getiri': None, 'fark': None, 'bakiye_usd': None, 'tasfiye': 0}
    fast = sum(p['getiri'] for p, _ in pairs) / len(pairs)
    slow = sum(q['getiri'] for _, q in pairs) / len(pairs)
    return {'uye': uye, 'karsilastirilan': len(pairs), 'getiri': fast, 'oda_v2_getiri': slow, 'fark': fast - slow,
            'bakiye_usd': sum(p['bakiye_usd'] for p, _ in pairs), 'tasfiye': sum(1 for p, _ in pairs if p.get('tasfiye'))}


def run(root: Path, output: Path, client=None, now=None, symbols=None) -> dict:
    # Üç ayrı zaman: `uretildi` = koşu başlangıcı; trader `veri_zamani` = o trader'ın gerçek okuma anı; `yayim_zamani` = dosyanın yazıldığı an.
    # `now` verilirse (test/yeniden üretim) gerçek saat kullanılmaz, üçü de `now` olur.
    clock = None if now is not None else (lambda: datetime.now(UTC))
    now = timestamp(now or datetime.now(UTC))
    client = client or PublicClient(limiter=RateLimiter())
    watchlist = load_list(root / 'copytrade/izleme_listesi.yaml')
    state = read_json(output / 'motor.json', {'surum': 1, 'traderlar': {}, 'olaylar': {}})
    if state.get('surum') != 1:
        raise ValueError('Desteklenmeyen motor arşivi sürümü.')
    # v1.2 changes trade-event ids from a fill hash to trader/oid/type.  Keep
    # light events, then rebuild all trade events from retained public fills.
    traders = []
    all_events = {key: value for key, value in state['olaylar'].items() if value.get('tur') == 'isik'}
    state['olaylar'] = all_events
    dexes: list[str] = []
    if watchlist:
        dexes = perp_dex_names(client.info({'type': 'perpDexs'}))
    failed = 0
    for row in watchlist:
        retained = state['traderlar'].get(row['id'])
        if retained and (retained['adres'] != row['adres'].lower() or retained['t0'] != iso(timestamp(row['t0']))):
            raise ValueError(f"{row['id']}: adres/t0 değiştirilemez; yeni izleme için yeni id kullanın.")
        try:
            traders.append(update_trader(root, client, dexes, state, all_events, row, now, symbols, clock))
        except Exception as error:
            failed += 1
            print(f"{row['id']}: veri hatası: {data_error_reason(error)}")
            retained = state['traderlar'].get(row['id'], {})
            previous = retained.get('son_trader')
            if previous:
                traders.append(with_data_error(previous, error, now))
                for event in retained.get('son_olaylar', []):
                    all_events[event['id']] = event
            else:
                traders.append(unavailable_trader(root, row, error))
    if watchlist and failed == len(watchlist):
        raise RuntimeError('Tüm trader verileri hatalı; önceki durum yayımlanmadı.')
    finished = iso(clock() if clock else now)
    result = {'surum': 1, 'uretildi': iso(now), 'yayim_zamani': finished, 'kosu_baslangic': iso(now), 'kosu_bitis': finished,
              'kaynak': 'hyperliquid', 'traderlar': traders,
              'kasa_egri': {'oda': kasa_egrisi(traders, 'oda'), 'kontrol': kasa_egrisi(traders, 'kontrol')},
              'kapsam': {kol: kapsam(traders, kol) for kol in sorted({k for t in traders for k in (t.get('kollar') or [t.get('kol')]) if k})}}
    result['olaylar'], result['gunluk_sayac'], result['olay_kapsami'], result['sayac_24s'] = olay_ozeti(all_events, traders, now, failed == 0)
    result['risk'] = risk_tanisi(traders, result.get('sayac_24s'))
    if any('sanal_kopya_v2_gecikme5' in t for t in traders):
        result['gecikme5'] = gecikme5_ozeti(traders)
    oda_uyeleri = [t for t in traders if t.get('kol') == 'oda']
    if oda_uyeleri:
        result['kalabalik'] = {**oda_risk.kalabalik([t for t in oda_uyeleri if t.get('gecerli') and t.get('hesap_degeri')]), 'zaman': iso(now)}
    # Serialize both before replacing either; API/validation/NaN errors leave the archive untouched.
    payloads = {name: json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
                for name, value in [('motor.json', state), ('durum.json', result)]}
    output.mkdir(parents=True, exist_ok=True)
    write_event_archive(output, all_events)
    for name, value in payloads.items():
        temporary = output / (name + '.tmp')
        temporary.write_text(value, encoding='utf-8')
        temporary.replace(output / name)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, default=Path('izleme'))
    args = parser.parse_args()
    # Only a public symbol catalog; blocked access remains explicitly "bilinmiyor".
    symbols = None
    if load_list(args.root / 'copytrade/izleme_listesi.yaml'):
        args.output.mkdir(parents=True, exist_ok=True)
        symbols, _ = write_binance_universe(args.output)
    result = run(args.root, args.output, symbols=symbols)
    print(f"İzleme: {len(result['traderlar'])} trader, {len(result['olaylar'])} olay.")


if __name__ == '__main__':
    main()
