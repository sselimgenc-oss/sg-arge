"""İş A: ağsız yanıtlar, kalıcı arşiv ve sözleşme kabul testleri."""
import copy
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from copytrade import izleme_motoru as m
from copytrade.kararlar import merge
from copytrade.kapi import delayed_copy
from pano.saglik import blok_bootstrap

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = '0x' + '1' * 40
NOW = m.timestamp('2026-10-27T12:00:00Z')
T0 = m.timestamp('2026-10-27')


def fill(t='2026-10-27T10:00:00Z', tid=1, side='B', size=1, before=0, price=100, coin='BTC', oid=None):
    return {'time': m.millis(t), 'tid': tid, 'oid': str(tid if oid is None else oid), 'coin': coin, 'side': side, 'sz': str(size),
            'startPosition': str(before), 'px': str(price), 'closedPnl': '0', 'fee': '0'}


def test_shared_order_fixture_has_one_event_for_multi_fill_order():
    fixture = json.loads((ROOT / 'tests/fixtures/olaylar.json').read_text())
    events = m.fill_events(fixture['trader'], fixture['fills'], fixture['account'], [])
    actual = [{key: event[key] for key in ('id', 'tur', 'coin', 'yon')} for event in events]
    assert actual == fixture['expected']
    assert all(event['coin'] != '@1' for event in events)


def test_first_health_value_does_not_emit_light_event(tmp_path):
    root, client = project(tmp_path), Client()
    result = m.run(root, root / 'out', client, NOW)
    assert all(event['tur'] != 'isik' for event in result['olaylar'])


def test_one_trader_error_retains_its_last_successful_payload(tmp_path):
    rows = [
        {'id': 'T1', 'adres': ADDRESS, 'takma_ad': 'Bir', 'durum': 'izlemede', 't0': str(T0.date())},
        {'id': 'T2', 'adres': '0x' + '2' * 40, 'takma_ad': 'İki', 'durum': 'izlemede', 't0': str(T0.date())},
    ]
    root = project(tmp_path, rows)
    class SometimesBroken(Client):
        broken = False
        def fills(self, address, start):
            if self.broken and address == rows[1]['adres']:
                raise RuntimeError('429 kısa hata')
            return super().fills(address, start)
    client = SometimesBroken()
    first = m.run(root, root / 'out', client, NOW)
    client.broken = True
    result = m.run(root, root / 'out', client, NOW + pd.Timedelta(hours=1))
    old = next(trader for trader in first['traderlar'] if trader['id'] == 'T2')
    retained = next(trader for trader in result['traderlar'] if trader['id'] == 'T2')
    assert retained['hesap_degeri'] == old['hesap_degeri']
    assert retained['saglik']['nedenler'][-1] == 'veri hatası: 429 kısa hata'


def test_hourly_fallback_marks_virtual_copy_approximate(tmp_path):
    root, client = project(tmp_path), Client()
    config = root / 'copytrade/izleme_listesi.yaml'
    config.write_text(config.read_text().replace('2026-10-27', '2026-10-01'))
    old = fill('2026-10-01T10:00Z')
    client.rows = [old]
    now = m.timestamp('2026-10-27T12:00Z')
    result = m.run(root, root / 'out', client, now)
    assert result['traderlar'][0]['sanal_kopya']['not'] == 'yaklaşık fiyat'


def test_kararlar_merges_last_decision_without_personal_fields(tmp_path):
    path = tmp_path / 'kararlar.jsonl'
    rows = merge(path, [
        {'olay_id': 'T1-1-acilis', 'zaman': '2026-10-27T10:00:00Z', 'karar': 'acti', 'neden': 'diger', 'not': ''},
        {'olay_id': 'T1-1-acilis', 'zaman': '2026-10-27T10:01:00Z', 'karar': 'atladi', 'neden': 'gec_gordum', 'not': ''},
    ])
    assert rows == [{'olay_id': 'T1-1-acilis', 'zaman': '2026-10-27T10:01:00Z', 'karar': 'atladi', 'neden': 'gec_gordum', 'not': ''}]
    with pytest.raises(ValueError):
        merge(path, [{'olay_id': 'x', 'zaman': 'now', 'karar': 'acti', 'neden': 'diger', 'not': '', 'tutar': '1'}])


def position(size=1, coin='BTC', value=100):
    return {'position': {'coin': coin, 'szi': str(size), 'entryPx': '100', 'positionValue': str(value),
                         'leverage': {'value': 2}, 'unrealizedPnl': '1'}}


def portfolio():
    days = pd.date_range('2026-07-01', '2026-10-28', freq='1D', tz='UTC')
    return [['perpAllTime', {'pnlHistory': [[m.millis(t), str(i * .2)] for i, t in enumerate(days)],
                             'accountValueHistory': [[m.millis(t), '1000'] for t in days]}]]


class Client:
    def __init__(self, fills=None):
        self.rows = fills if fills is not None else [fill()]
        self.calls = []
        self.positions = [position()]
        self.account = 1000
        self.portfolio_reads = 0
        self.candle_reads = 0
        self.dexes = [None]
        self.funding = []

    def info(self, payload, weight=20):
        self.calls.append(copy.deepcopy(payload))
        if payload['type'] == 'perpDexs':
            return self.dexes
        if payload['type'] == 'clearinghouseState':
            return {'marginSummary': {'accountValue': str(self.account if not payload.get('dex') else 0)},
                    'assetPositions': self.positions if not payload.get('dex') else [position(coin='xyz:CL', value=50)]}
        if payload['type'] == 'userFunding':
            return [x for x in self.funding if payload['startTime'] <= x['time'] <= payload['endTime']]
        raise AssertionError(payload)

    def fills(self, address, start):
        self.calls.append({'type': 'userFillsByTime', 'user': address, 'startTime': start})
        return [copy.deepcopy(f) for f in self.rows if int(f['time']) >= start]

    def portfolio(self, address):
        self.portfolio_reads += 1
        return portfolio()

    def candles(self, coin, start, end, interval='1m'):
        assert interval in {'1m', '1h'}
        self.candle_reads += 1
        return [{'t': t, 'o': '102'} for t in range(start, end + 1, m.MINUTE)]


def project(tmp_path, rows=None):
    (tmp_path / 'copytrade').mkdir()
    rows = rows if rows is not None else [{'id': 'T1', 'adres': ADDRESS, 'takma_ad': 'Test',
                                         'durum': 'izlemede', 't0': str(T0.date())}]
    (tmp_path / 'copytrade/izleme_listesi.yaml').write_text(yaml.safe_dump({'traderlar': rows}))
    return tmp_path


def test_empty_list_writes_contract_and_never_uses_network(tmp_path):
    root = project(tmp_path, [])
    class NoNetwork:
        def __getattr__(self, name):
            raise AssertionError(name)
    result = m.run(root, root / 'out', NoNetwork(), NOW)
    assert result == {'surum': 1, 'uretildi': '2026-10-27T12:00:00Z', 'kaynak': 'hyperliquid', 'traderlar': [], 'olaylar': []}
    assert json.loads((root / 'out/durum.json').read_text()) == result


def test_uses_current_main_list_without_changing_it():
    path = ROOT / 'copytrade/izleme_listesi.yaml'
    before = path.read_bytes()
    rows = m.load_list(path)
    assert [row['id'] for row in rows] == ['T1', 'T2']
    assert all(row['durum'] == 'izlemede' for row in rows)
    assert path.read_bytes() == before


@pytest.mark.parametrize('change', [dict(id='T1'), dict(adres=ADDRESS), dict(durum='canli'), dict(t0='wrong')])
def test_invalid_or_duplicate_watchlist_rejected(tmp_path, change):
    row = {'id': 'T2', 'adres': '0x' + '2' * 40, 'takma_ad': 'Test-2', 'durum': 'izlemede', 't0': '2026-10-27'}
    row.update(change)
    first = {'id': 'T1', 'adres': ADDRESS, 'takma_ad': 'Test', 'durum': 'izlemede', 't0': '2026-10-27'}
    root = project(tmp_path, [first, row])
    with pytest.raises((ValueError, TypeError)):
        m.load_list(root / 'copytrade/izleme_listesi.yaml')


def test_incremental_overlap_daily_portfolio_and_repeatable_ledger(tmp_path):
    root = project(tmp_path)
    client = Client()
    one = m.run(root, root / 'out', client, NOW)
    two = m.run(root, root / 'out', client, NOW + pd.Timedelta(hours=1))
    assert one['traderlar'] == two['traderlar']
    assert one['olaylar'] == two['olaylar']
    assert client.portfolio_reads == 1
    assert client.candle_reads == 1
    starts = [x['startTime'] for x in client.calls if x['type'] == 'userFillsByTime']
    assert starts[-1] == client.rows[-1]['time']  # inclusive boundary is deduplicated
    saved = json.loads((root / 'out/motor.json').read_text())
    assert len(saved['traderlar']['T1']['fills']) == 1
    assert two['traderlar'][0]['sanal_kopya']['bakiye_usd'] == pytest.approx(1000 - 102 * .00095)
    client.rows.append(fill('2026-10-27T12:30:00Z', 2, 'A', 1, 1, 110))
    client.positions = []
    three = m.run(root, root / 'out', client, NOW + pd.Timedelta(hours=2))
    assert len([e for e in three['olaylar'] if e['tur'] == 'acilis']) == 1
    assert len([e for e in three['olaylar'] if e['tur'] == 'kapanis']) == 1
    opened = next(e for e in three['olaylar'] if e['tur'] == 'acilis')
    assert opened['sanal_sonuc']['durum'] == 'kapandi'
    assert opened['sanal_sonuc']['net_yuzde'] == pytest.approx(-.0019)
    m.run(root, root / 'out', client, NOW + pd.Timedelta(days=1))
    assert client.portfolio_reads == 2


def test_pinned_scale_does_not_rewrite_prior_copy_pnl(tmp_path):
    root, client = project(tmp_path), Client()
    first = m.run(root, root / 'out', client, NOW)
    client.account = 2000
    second = m.run(root, root / 'out', client, NOW + pd.Timedelta(hours=1))
    assert first['traderlar'][0]['sanal_kopya'] == second['traderlar'][0]['sanal_kopya']


def test_fills_at_same_millisecond_are_all_retained(tmp_path):
    root, client = project(tmp_path), Client()
    m.run(root, root / 'out', client, NOW)
    client.rows += [fill(tid=2, before=1, size=.5)]
    result = m.run(root, root / 'out', client, NOW)
    assert {e['tur'] for e in result['olaylar']} >= {'acilis', 'buyutme'}
    assert len(json.loads((root / 'out/motor.json').read_text())['traderlar']['T1']['fills']) == 2


def test_address_or_t0_rebinding_cannot_overwrite_history(tmp_path):
    root, client = project(tmp_path), Client()
    m.run(root, root / 'out', client, NOW)
    path = root / 'out/durum.json'
    before = path.read_bytes()
    config = root / 'copytrade/izleme_listesi.yaml'
    config.write_text(config.read_text().replace('2026-10-27', '2026-10-26'))
    with pytest.raises(ValueError, match='adres/t0'):
        m.run(root, root / 'out', client, NOW)
    assert path.read_bytes() == before


@pytest.mark.parametrize('before,size,side,kinds', [
    (0, 1, 'B', ['acilis']), (1, 1, 'A', ['kapanis']),
    (1, .25, 'B', []), (1, .251, 'B', ['buyutme']),
    (1, .25, 'A', []), (1, .251, 'A', ['azaltma']),
    (-1, .3, 'A', ['buyutme']), (-1, .3, 'B', ['azaltma']),
    (1, 2, 'A', ['kapanis', 'acilis']),
])
def test_fill_events_strict_size_threshold_and_flip(before, size, side, kinds):
    f = fill(before=before, size=size, side=side)
    events = m.fill_events('T1', [f], 1000, [])
    assert [e['tur'] for e in events] == kinds
    assert events == m.fill_events('T1', [f], 1000, [])
    assert len({e['id'] for e in events}) == len(events)
    for event in events:
        assert ('sanal_sonuc' in event) == (event['tur'] in {'acilis', 'buyutme'})


def test_copy_execution_delay_cost_funding_and_event_net():
    opening = fill()
    closing = fill('2026-10-27T11:00:00Z', 2, 'A', 1, 1, 500)  # source price is never execution price
    events = {e['id']: e for e in m.fill_events('T1', [opening, closing], 1000, [])}
    funding = [{'time': m.millis('2026-10-27T10:45:00Z'), 'delta': {'coin': 'BTC', 'usdc': '-.5'}}]
    candles = {'BTC': [{'t': m.millis('2026-10-27T10:30:00Z'), 'o': 100},
                       {'t': m.millis('2026-10-27T11:30:00Z'), 'o': 110}]}
    pending = m.copy_results([opening], {}, [], 1000, T0, m.timestamp('2026-10-27T10:29:00Z'), events)
    assert pending['bakiye_usd'] == 1000
    result = m.copy_results([opening, closing], candles, funding, 1000, T0, NOW, events)
    expected = 1000 + 10 - 210 * .00095 - .5
    assert result['bakiye_usd'] == pytest.approx(expected)
    opened = next(e for e in events.values() if e['tur'] == 'acilis')
    assert opened['sanal_sonuc'] == {'durum': 'kapandi', 'net_yuzde': pytest.approx((expected - 1000) / 100),
                                    'kapanis': '2026-10-27T11:30:00Z'}
    reference, _ = delayed_copy([opening, closing], candles, 1000, 30, funding)
    assert result['getiri'] == pytest.approx(float(reference.sum()))


def test_partial_close_keeps_open_event_until_final_exit():
    fills = [fill(), fill('2026-10-27T11:00Z', 2, 'A', .5, 1), fill('2026-10-27T11:20Z', 3, 'A', .5, .5)]
    events = {e['id']: e for e in m.fill_events('T1', fills, 1000, [])}
    candles = {'BTC': [{'t': f['time'] + 30 * m.MINUTE, 'o': 100} for f in fills]}
    m.copy_results(fills[:2], candles, [], 1000, T0, NOW, events)
    assert events[m.event_id('T1', m.order_id(fills[0]), 'acilis')]['sanal_sonuc']['durum'] == 'acik'
    m.copy_results(fills, candles, [], 1000, T0, NOW, events)
    assert events[m.event_id('T1', m.order_id(fills[0]), 'acilis')]['sanal_sonuc']['durum'] == 'kapandi'


def test_midnight_cost_is_booked_on_execution_day():
    f = fill('2026-10-26T23:45Z')
    now = m.timestamp('2026-10-27T01:00Z')
    candles = {'BTC': [{'t': f['time'] + 30 * m.MINUTE, 'o': 100}]}
    result = m.copy_results([f], candles, [], 1000, m.timestamp('2026-10-26'), now, {})
    assert result['egri'][0] == ['2026-10-26', 1000]
    assert result['egri'][1][1] == pytest.approx(999.905)


def test_exact_candle_required_and_cache_survives_window_rollover():
    client, cache = Client(), {}
    f = fill()
    candles, approximate = m.execution_candles(client, [f], cache, m.millis(NOW))
    assert candles['BTC'][0]['o'] == 102
    assert not approximate
    m.execution_candles(client, [f], cache, m.millis(NOW) + 10 * m.DAY)
    assert client.candle_reads == 1
    candles, approximate = m.execution_candles(client, [f], {}, m.millis(NOW) + 10 * m.DAY)
    assert approximate and candles['BTC'][0]['o'] == 102
    client.candles = lambda *args, **kwargs: [{'t': f['time'] + 31 * m.MINUTE, 'o': 999}]
    with pytest.raises(ValueError, match='mum eksik'):
        m.execution_candles(client, [f], {}, m.millis(NOW))


def test_failure_preserves_last_successful_payloads(tmp_path):
    root, client = project(tmp_path), Client()
    m.run(root, root / 'out', client, NOW)
    previous = {p.name: p.read_bytes() for p in (root / 'out').iterdir()}
    client.rows.append(fill('2026-10-27T12:00Z', 2, 'B', 1, 1))
    client.candles = lambda *args, **kwargs: []
    with pytest.raises(RuntimeError, match='Tüm trader'):
        m.run(root, root / 'out', client, NOW + pd.Timedelta(hours=1))
    assert previous == {p.name: p.read_bytes() for p in (root / 'out').iterdir()}


def test_hip3_positions_and_actual_account_leverage(tmp_path):
    root, client = project(tmp_path), Client()
    client.dexes = [{'name': 'xyz'}, {'name': 'flx'}, {'name': 'xyz'}]
    client.positions = [position(value=4000)]
    result = m.run(root, root / 'out', client, NOW)
    trader = result['traderlar'][0]
    assert trader['hesap_degeri'] == 1000
    assert trader['saglik']['isik'] == 'sari'  # gross notional / account, not the 2x setting
    assert {p['coin'] for p in trader['pozisyonlar']} == {'BTC', 'xyz:CL'}
    assert next(p for p in trader['pozisyonlar'] if p['coin'] == 'xyz:CL')['sinif'] == 'emtia'
    states = [call for call in client.calls if call['type'] == 'clearinghouseState']
    assert states == [
        {'type': 'clearinghouseState', 'user': ADDRESS},
        {'type': 'clearinghouseState', 'user': ADDRESS, 'dex': 'xyz'},
        {'type': 'clearinghouseState', 'user': ADDRESS, 'dex': 'flx'},
    ]


def test_invalid_perp_dex_response_is_not_silently_ignored():
    with pytest.raises(ValueError, match='perpDexs'):
        m.perp_dex_names({'name': 'xyz'})
    with pytest.raises(ValueError, match='dex adı'):
        m.perp_dex_names([{'name': ''}])


def test_portfolio_uses_pnl_not_deposits():
    data = portfolio()
    curve = m.portfolio_curve(data, NOW)
    data[0][1]['accountValueHistory'][-1][1] = '100000000'
    changed = m.portfolio_curve(data, NOW)
    pd.testing.assert_series_equal(curve, changed)  # robust median ignores one deposit
    assert (curve.diff().dropna() > 0).all()


def history(live=None):
    daily = np.r_[np.tile([.002, -.001, .001, 0], 20), live if live is not None else [.001]]
    return pd.Series(np.r_[0, daily.cumsum()], index=pd.date_range('2026-08-07', periods=len(daily) + 1, tz='UTC'))


@pytest.mark.parametrize('leverage,martingale,last,expected,reason', [
    (2.9, False, m.millis(NOW), 'yesil', 'normal'),
    (3, False, m.millis(NOW), 'sari', '3–10'),
    (10, False, m.millis(NOW), 'sari', '3–10'),
    (10.01, False, m.millis(NOW), 'kirmizi', '> 10'),
    (1, True, m.millis(NOW), 'kirmizi', 'martingale'),
    (1, False, m.millis(NOW) - 30 * m.DAY, 'sari', 'işlem yok'),
])
def test_health_leverage_martingale_inactivity(leverage, martingale, last, expected, reason):
    h = history()
    result = m.health(h, h.index[-1], NOW, leverage, martingale, last)
    assert result['isik'] == expected
    assert any(reason in x for x in result['nedenler'])


def test_health_cone_yellow_red_and_cusum(monkeypatch):
    h = history([-.00001])
    # A fixed known cone isolates the bands from the separate drawdown condition.
    monkeypatch.setattr(m, '_mdd', lambda returns: .1)
    monkeypatch.setattr(m, 'blok_bootstrap', lambda *a, **kw: {'p5': [-.001], 'p20': [.001]})
    result = m.health(h, h.index[-1], NOW, 1, False, m.millis(NOW))
    assert result['isik'] == 'sari'
    assert 'koni %5–%20 bandında' in result['nedenler']
    h.iloc[-1] -= .1
    result = m.health(h, h.index[-1], NOW, 1, False, m.millis(NOW))
    assert result['isik'] == 'kirmizi'
    assert 'koni %5 altında' in result['nedenler']
    assert 'CUSUM uyarısı' in result['nedenler']


def test_health_drawdown_is_red_even_with_permissive_cone(monkeypatch):
    h = history([.01, -.03])
    monkeypatch.setattr(m, 'blok_bootstrap', lambda *a, **kw: {'p5': [-1], 'p20': [-.9]})
    result = m.health(h, h.index[-2], NOW, 1, False, m.millis(NOW))
    assert result['isik'] == 'kirmizi'
    assert 'düşüş geçmişin 1,5 katından fazla' in result['nedenler']


def test_shared_bootstrap_supports_p20_without_changing_default_results():
    series = pd.Series([.01, -.005, .002])
    default = blok_bootstrap(series, 4)
    extended = blok_bootstrap(series, 4, quantiles=(5, 20), block_size=4)
    assert extended['p5'] == default['p5']
    assert all(a <= b for a, b in zip(extended['p5'], extended['p20']))


def check_shape(actual, examples):
    if actual is None:
        assert any(example is None for example in examples)
    elif isinstance(actual, dict):
        matching = [e for e in examples if isinstance(e, dict) and set(e) == set(actual)]
        assert matching, actual.keys()
        for key, value in actual.items():
            check_shape(value, [e[key] for e in matching])
    elif isinstance(actual, list):
        pool = [x for e in examples if isinstance(e, list) for x in e]
        for item in actual:
            check_shape(item, pool)
    else:
        assert any(isinstance(actual, type(e)) or isinstance(actual, (int, float)) and isinstance(e, (int, float))
                   for e in examples if e is not None), (actual, examples)


def test_nonempty_status_matches_example_keys_types_and_event_variants(tmp_path):
    root, client = project(tmp_path), Client()
    result = m.run(root, root / 'out', client, NOW, symbols={'BTCUSDT'})
    example = json.loads((ROOT / 'izleme/ornek_durum.json').read_text())
    check_shape(result, [example])
    assert result['traderlar'][0]['pozisyonlar'][0]['binance'] == 'var'
    assert result['traderlar'][0]['kapi']['sinif'] == 'Yetersiz'
    assert json.loads((root / 'out/durum.json').read_text()) == result


def test_future_t0_does_not_copy_or_create_trade_events(tmp_path):
    root, client = project(tmp_path), Client()
    config = root / 'copytrade/izleme_listesi.yaml'
    config.write_text(config.read_text().replace('2026-10-27', '2026-10-28'))
    result = m.run(root, root / 'out', client, NOW)
    assert result['traderlar'][0]['sanal_kopya']['bakiye_usd'] == 1000
    assert result['traderlar'][0]['sanal_kopya']['egri'] == []
    assert all(e['tur'] == 'isik' for e in result['olaylar'])
    assert client.candle_reads == 0


def git(cwd, *args):
    return subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


def test_publication_creates_orphan_and_preserves_worker_decisions(tmp_path):
    remote, checkout = tmp_path / 'remote.git', tmp_path / 'checkout'
    remote.mkdir(); checkout.mkdir()
    git(remote, 'init', '--bare')
    git(checkout, 'init')
    git(checkout, 'config', 'user.name', 'Test')
    git(checkout, 'config', 'user.email', 'test@example.com')
    git(checkout, 'remote', 'add', 'origin', str(remote))
    (checkout / 'source.py').write_text('source must stay off data branch')
    git(checkout, 'add', '.')
    git(checkout, 'commit', '-m', 'source')
    (checkout / 'izleme').mkdir()
    for name in ['motor.json', 'durum.json']:
        (checkout / 'izleme' / name).write_text('{}')
    command = ['bash', str(ROOT / '.github/scripts/izleme_yayimla.sh')]
    subprocess.run(command, cwd=checkout, env={**os.environ, 'GITHUB_ACTIONS': 'true'}, check=True, capture_output=True)
    assert git(checkout, 'rev-list', '--count', 'HEAD') == '1'
    assert not (checkout / 'source.py').exists()
    (checkout / 'izleme/kararlar.jsonl').write_text('{"olay_id":"public-test"}\n')
    git(checkout, 'add', '.')
    git(checkout, 'commit', '-m', 'worker decision')
    git(checkout, 'push', 'origin', 'copytrade-izleme')
    (checkout / 'izleme/durum.json').write_text('{"uretildi":"next"}')
    subprocess.run(command, cwd=checkout, env={**os.environ, 'GITHUB_ACTIONS': 'true'}, check=True, capture_output=True)
    assert (checkout / 'izleme/kararlar.jsonl').read_text() == '{"olay_id":"public-test"}\n'
    assert json.loads((checkout / 'izleme/durum.json').read_text())['uretildi'] == 'next'
    assert git(checkout, 'rev-parse', 'HEAD') == git(remote, 'rev-parse', 'refs/heads/copytrade-izleme')


def test_closing_pre_t0_position_never_opens_inverse_copy():
    inherited_close = fill(side='A', before=5, size=5)
    assert m.copy_actions([inherited_close]) == []
    flip = fill(side='A', before=5, size=7)
    actions = m.copy_actions([flip])
    assert float(actions[0]['sz']) == 2
    assert float(actions[0]['startPosition']) == 0


def test_current_two_trader_list_runs_offline(tmp_path):
    (tmp_path / 'copytrade').mkdir()
    (tmp_path / 'copytrade/izleme_listesi.yaml').write_bytes((ROOT / 'copytrade/izleme_listesi.yaml').read_bytes())
    result = m.run(tmp_path, tmp_path / 'out', Client(), NOW)
    assert [t['id'] for t in result['traderlar']] == ['T1', 'T2']
    example = json.loads((ROOT / 'izleme/ornek_durum.json').read_text())
    check_shape(result, [example])
    assert all(t['sanal_kopya']['bakiye_usd'] == 1000 for t in result['traderlar'])


def test_event_feed_is_recent_200_with_stable_archive(tmp_path):
    root, client = project(tmp_path), Client([])
    output = root / 'out'
    output.mkdir()
    events = {str(i): {'id': str(i), 'zaman': m.at_ms(m.millis(NOW) - i * m.MINUTE),
                      'trader': 'retained', 'tur': 'isik'} for i in range(250)}
    (output / 'motor.json').write_text(json.dumps({'surum': 1, 'traderlar': {}, 'olaylar': events}))
    result = m.run(root, output, client, NOW)
    assert len(result['olaylar']) == 200
    assert '249' not in {e['id'] for e in result['olaylar']}
    assert len(json.loads((output / 'motor.json').read_text())['olaylar']) == 250
