"""Saatlik, salt okunur Hyperliquid izleme; yalnız sanal defter üretir.

Dış sözleşme durum.json'dur. Yeniden oynatılabilir ham veriler ve imleçler
motor.json'da ayrı tutulur; başarısız bir koşu iki dosyayı da yayımlamaz.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from copytrade.kapi import (SLIPPAGE, TAKER, binance_availability, delayed_copy,
                            write_binance_universe)
from copytrade.olcut import _funding_amount, asset_class, calculate_metrics, closed_round_trips, perp_fills
from copytrade.tarama import PublicClient, RateLimiter
from pano.saglik import CUSUM_YELLOW, _cusum, _mdd, blok_bootstrap

MINUTE = 60_000
DAY = 86_400_000


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
        if not isinstance(row, dict) or set(row) != {'id', 'adres', 'takma_ad', 'durum', 't0'}:
            raise ValueError('İzleme satırında yalnız id, adres, takma_ad, durum, t0 olmalı.')
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
        signed = float(fill['sz']) * (-1 if fill['side'] == 'A' else 1)
        after = float(fill.get('startPosition', before)) + signed
        if abs(after) < 1e-10:
            after = 0.0
        volume = sum(abs(float(item['px']) * float(item['sz'])) for item in rows)
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
                     'hesap_payi': abs(after * float(fill['px'])) / account if account > 0 else 0.0,
                     'kaldirac': position.get('kaldirac', abs(size * float(fill['px'])) / account if account > 0 else 0.0), 'not': ''}
            if kind in {'acilis', 'buyutme'}:
                event['sanal_sonuc'] = {'durum': 'acik', 'net_yuzde': None, 'kapanis': None}
            result.append(event)
    return result


def portfolio_curve(portfolio: list, now: pd.Timestamp) -> pd.Series:
    periods = dict(portfolio)
    data = periods.get('perpAllTime') or periods.get('allTime') or {}
    pnl = pd.Series({pd.to_datetime(t, unit='ms', utc=True): float(v)
                     for t, v in data.get('pnlHistory', [])}, dtype=float).sort_index()
    values = pd.Series({pd.to_datetime(t, unit='ms', utc=True): float(v)
                        for t, v in data.get('accountValueHistory', [])}, dtype=float)
    if pnl.empty or values[values > 0].empty:
        raise ValueError('Portfolio PnL/pozitif hesap geçmişi eksik; sağlık hesaplanamaz.')
    # Same stable normalization as CT-Kapı; cash deposits are never counted as PnL.
    denominator = float(values[values > 0].median())
    pnl = pnl[pnl.index <= now].resample('1D').last().ffill()
    return pnl / denominator


def health(history: pd.Series, t0: pd.Timestamp, now: pd.Timestamp, leverage: float,
           martingale: bool, last_fill: int | None) -> dict:
    daily = history.diff().dropna()
    before, live = daily[daily.index < t0], daily[daily.index >= t0]
    red, yellow = [], []
    # Additive PnL / account -> daily equity returns, for shared compounded bootstrap/CUSUM.
    def returns(series):
        equity = 1 + pd.concat([pd.Series([0.0], index=[series.index[0] - pd.Timedelta(days=1)]), series.cumsum()])
        return equity.pct_change().iloc[1:]
    if before.empty:
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
            'nedenler': red + yellow or ['konide', 'kaldıraç normal']}


def cached_candle(value: object) -> tuple[float, bool]:
    """Read both v1 numeric entries and v1.2 entries with their price source."""
    if isinstance(value, dict):
        return float(value['fiyat']), bool(value.get('yaklasik', False))
    return float(value), False


def execution_candles(client, fills: list[dict], cache: dict, now_ms: int) -> tuple[dict[str, list[dict]], bool]:
    """Use 1m opens when retained; fall back to the matching 1h opening, never a later price."""
    needed = {}
    approximate = any(cached_candle(value)[1] for rows in cache.values() for value in rows.values())
    for fill in fills:
        target = math.ceil((int(fill['time']) + 30 * MINUTE) / MINUTE) * MINUTE
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
                    raise ValueError(f'{coin}: gecikmeli 1 dk mum eksik ({target}); defter yayımlanmadı.')
                cache.setdefault(coin, {})[str(target)] = {'fiyat': prices[target], 'yaklasik': False}
        if older:
            hourly = client.candles(coin, min(target // (60 * MINUTE) * (60 * MINUTE) for target in older),
                                    now_ms, interval='1h')
            prices = {int(c['t']): float(c['o']) for c in hourly}
            for target in older:
                hour = target // (60 * MINUTE) * (60 * MINUTE)
                if hour not in prices or prices[hour] <= 0:
                    raise ValueError(f'{coin}: gecikmeli 1 saat mum eksik ({hour}); defter yayımlanmadı.')
                cache.setdefault(coin, {})[str(target)] = {'fiyat': prices[hour], 'yaklasik': True}
                approximate = True
    return ({coin: [{'t': int(t), 'o': cached_candle(value)[0]} for t, value in rows.items()]
             for coin, rows in cache.items()}, approximate)


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


def copy_results(fills: list[dict], candles: dict, funding: list[dict], account: float,
                 t0: pd.Timestamp, now: pd.Timestamp, events: dict, approximate: bool = False) -> dict:
    prices = {coin: {int(c['t']): float(c['o']) for c in rows} for coin, rows in candles.items()}
    # Pending fills are not charged before their 30-minute execution time.
    mature = [f for f in fills if math.ceil((int(f['time']) + 30 * MINUTE) / MINUTE) * MINUTE <= millis(now)]
    series, missing = delayed_copy(mature, candles, account, 30, funding)
    if missing:
        raise ValueError('Sanal defterde eksik mum var.')
    days = pd.date_range(t0.normalize(), now.normalize(), freq='1D')
    net = pd.Series(0.0, index=days)
    if series is not None:
        # delayed_copy dates its entries at source time; shift each replayed fill to
        # execution time (notably across midnight) without changing its calculation.
        shifted_fills = []
        shifted_candles = {}
        for fill in mature:
            execution = math.ceil((int(fill['time']) + 30 * MINUTE) / MINUTE) * MINUTE
            price = prices[fill['coin']][execution]
            shifted_fills.append(dict(fill, time=execution, px=price))
        shifted, _ = delayed_copy(shifted_fills, shifted_candles, account, 0, funding)
        net = shifted.reindex(days, fill_value=0.0)
    equity = 1000 * (1 + net.cumsum())
    # FIFO lots allocate realized return and exact friction/funding to the event
    # that opened/increased that lot. Partial closes do not finish an event early.
    lots = {}
    event_by_order = {(e['trader'], event_oid(e)): e['id'] for e in events.values()
                      if e['tur'] in {'acilis', 'buyutme'}}
    trader_id = next((e['trader'] for e in events.values()), '')
    timeline = [(math.ceil((int(f['time']) + 30 * MINUTE) / MINUTE) * MINUTE, 0, f) for f in mature]
    timeline += [(int(f['time']), 1, f) for f in funding]
    for time_ms, kind, row in sorted(timeline, key=lambda x: (x[0], x[1])):
        coin = row.get('coin') if kind == 0 else row.get('delta', {}).get('coin')
        active = lots.setdefault(coin, [])
        if kind == 1:
            total = sum(lot['remaining'] for lot in active)
            for lot in active:
                lot['pnl'] += _funding_amount(row) * lot['remaining'] / total if total else 0.0
            continue
        execution = math.ceil(time_ms / MINUTE) * MINUTE
        price = prices[coin][execution]
        signed = float(row['sz']) * (-1 if row['side'] == 'A' else 1)
        remaining = abs(signed)
        direction = 1 if signed > 0 else -1
        while remaining > 1e-10 and active and active[0]['direction'] != direction:
            lot = active[0]
            closed = min(lot['remaining'], remaining)
            lot['pnl'] += closed * ((price - lot['price']) * lot['direction'] - price * (TAKER + SLIPPAGE))
            lot['remaining'] -= closed; remaining -= closed
            if lot['remaining'] < 1e-10:
                if lot['event'] in events:
                    events[lot['event']]['sanal_sonuc'] = {
                        'durum': 'kapandi', 'net_yuzde': lot['pnl'] / lot['notional'],
                        'kapanis': at_ms(execution)}
                active.pop(0)
        if remaining > 1e-10:
            ident = event_by_order.get((trader_id, order_id(row)), '')
            active.append({'remaining': remaining, 'direction': direction, 'price': price,
                           'notional': remaining * price, 'pnl': -remaining * price * (TAKER + SLIPPAGE),
                           'event': ident})
    peak = np.maximum.accumulate(np.r_[1000.0, equity.to_numpy()])
    drawdown = float(np.max(1 - np.r_[1000.0, equity.to_numpy()] / peak)) if len(equity) else 0.0
    balance = float(equity.iloc[-1]) if len(equity) else 1000.0
    result = {'baslangic_usd': 1000, 'bakiye_usd': balance, 'getiri': balance / 1000 - 1,
            'dusus': drawdown, 'gecikme_dk': 30, 't0': str(t0.date()),
            'egri': [[str(day.date()), float(value)] for day, value in equity.items()]}
    if approximate:
        result['not'] = 'yaklaşık fiyat'
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


def gate_result(root: Path, address: str) -> dict:
    for path in sorted((root / 'copytrade/kapi').glob('*/sonuc.csv'), reverse=True):
        with path.open(encoding='utf-8', newline='') as handle:
            for row in csv.DictReader(handle):
                if row['address'].lower() == address.lower():
                    return {'sinif': row['sinif'] if row['sinif'] in {'Geçti', 'Yetersiz', 'Kaldı'} else 'Yetersiz',
                            'tarih': path.parent.name, 'not': row.get('neden', '')}
    return {'sinif': 'Yetersiz', 'tarih': '', 'not': 'Kapı sonucu bulunamadı'}


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


def with_data_error(trader: dict, error: Exception) -> dict:
    previous = copy.deepcopy(trader)
    short = str(error).splitlines()[0][:120] or type(error).__name__
    reasons = [reason for reason in previous['saglik']['nedenler'] if not reason.startswith('veri hatası:')]
    previous['saglik']['nedenler'] = reasons + [f'veri hatası: {short}']
    return previous


def update_trader(root: Path, client, dexes: list[str], state: dict, all_events: dict,
                  row: dict, now: pd.Timestamp, symbols: set[str] | None) -> dict:
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
    if saved.get('portfolio_gunu') != str(now.date()):
        saved['portfolio'] = client.portfolio(address)
        saved['portfolio_gunu'] = str(now.date())
    history = portfolio_curve(saved['portfolio'], now)
    states = clearinghouse_states(client, address, dexes)
    account, positions = positions_from_state(states, fills, symbols, now)
    if account <= 0:
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
    candles, approximate = execution_candles(client, actions, saved['mumlar'], millis(now))
    paper = copy_results(actions, candles, saved['funding'], saved['kopya_paydasi'], t0, now, own_events, approximate)
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
    trader = {**row, 'kapi': gate_result(root, address), 'saglik': light,
              'form': {'skor': ret30 / volatility if volatility > 0 and math.isfinite(volatility) else 0.0,
                       'getiri_30g': ret30, 'getiri_90g': float(recent.iloc[-1] - recent.iloc[0]) if len(recent) else 0.0},
              'hesap_degeri': account, 'pozisyonlar': positions, 'son_islem': last_trade,
              'egri': [[str(day.date()), float(value)] for day, value in recent.items()], 'sanal_kopya': paper}
    saved['son_trader'] = trader
    return trader


def run(root: Path, output: Path, client=None, now=None, symbols=None) -> dict:
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
            traders.append(update_trader(root, client, dexes, state, all_events, row, now, symbols))
        except Exception as error:
            failed += 1
            retained = state['traderlar'].get(row['id'], {})
            previous = retained.get('son_trader')
            if previous:
                traders.append(with_data_error(previous, error))
                for event in retained.get('son_olaylar', []):
                    all_events[event['id']] = event
    if watchlist and failed == len(watchlist):
        raise RuntimeError('Tüm trader verileri hatalı; önceki durum yayımlanmadı.')
    result = {'surum': 1, 'uretildi': iso(now), 'kaynak': 'hyperliquid', 'traderlar': traders,
              'olaylar': sorted(all_events.values(), key=lambda e: (e['zaman'], e['id']), reverse=True)[:200]}
    # Serialize both before replacing either; API/validation/NaN errors leave the archive untouched.
    payloads = {name: json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
                for name, value in [('motor.json', state), ('durum.json', result)]}
    output.mkdir(parents=True, exist_ok=True)
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
