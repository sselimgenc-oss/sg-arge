"""Kopya hesap v3 (E2 sabit tutar; `docs/GOREV_ETRE_GECIS.md`). v1 (`izleme_motoru.copy_results`) ve v2
(`kopya_v2.py`) silinmez, değişmez; v3 yan yana yayımlanır (`sanal_kopya_v3`, AGENTS.md kural 6).

Kullanıcı kararı 2026-10-30 ("Etre eğrisini enterpolasyonla port et"): v1/v2'nin trader hesabına ORANLI kopya
ölçeğinin yerine, Etre'nin `kasa.py`sindeki gibi, her taze açılış KOPYA HESABININ KENDİ o anki $ değerine göre
sabit tutarla açılır (`defter.sabit_tutar_egrisi`, kaynak `etre-trading-office etre2/kasa.py`+`ayar.py`, GPL-3.0,
DEĞİŞTİRİLMEDİ); ekleme mevcut kopya pozisyonuna trader'ın kendi oranı kadar eklenir (Etre `masa.py _ekle`);
azaltma/kapatma değişmedi (defterin ortak kuralı). Tek motor: aynı `defter.copy_ledger` (kural 7) — yalnız
`tutar_egrisi` parametresiyle.

**Kapsam dışı (bu sürümde HENÜZ yok — ayrı tasarım kararı gerektirir, v3'ün aşağıdaki alanları bu yüzden hep
boş/false döner, v2'den farklı olarak):**
- Çapraz teminat tasfiyesi ve pozisyon tavanı (`golge.py` `_denetle_ve_kapat`/`kirp_pozisyon`): ikisi de trader
  hesabına ORANLI ölçeklemeye (`capital_scale`) kodlanmış; sentetik "zorunlu çıkış" dolumlarının sabit tutar
  tabanında hangi ölçekte üretileceği ayrı bir tasarım kararı gerektiriyor — bu PR'da çözülmedi.
- Aşamalı zarar_kes/kar_al (E3, `golge.calistir(variant='V2')`): aynı sebepten HENÜZ bağlanmadı.
- Etre'nin kaldıraç kademesi, teminat/marj modeli, "ikna" (trader büyük alım) çarpanı: `GOREV_ETRE_GECIS.md` E2'nin
  ayrı alt maddeleri, bu PR'ın kapsamında değil.

v3'ü `sanal_kopya_v2`'nin YERİNE değil, YAN YANA okuyun: sabit tutar ölçeklemesinin gerçek veride nasıl davrandığını
izlemek içindir — risk katmanı (tasfiye/tavan/aşamalı çıkış) hâlâ v2'dedir.
"""

from __future__ import annotations

import math

import pandas as pd

from copytrade.defter import FundingRates, Market, copy_ledger, sabit_tutar_egrisi
from copytrade.kurallar import load_rules

MINUTE = 60_000
BASE_USD = 1000.0


def hesapla(fills: list[dict], saatlik: dict[str, list[dict]], isaret: dict[str, list[dict]],
            yurutme: dict[str, dict[int, float]], funding: list[dict],
            t0: pd.Timestamp, now: pd.Timestamp, delay: int, rules: dict | None = None) -> dict:
    """v3 sanal kopya sonucu (1.000 $ ölçeğinde, v1/v2 ile aynı ölçek). Girdiler `kopya_v2.hesapla` ile aynı anlamda;
    ``serisi`` (trader hesap değeri serisi) ve ``style`` burada gerekmez — sabit tutar trader'ın hesabına/tarzına
    bakmaz, yalnız kopyanın KENDİ değerine ve dolumun kendi before/after oranına."""
    rules = rules or load_rules()
    t0_ms, now_ms = int(t0.value // 1_000_000), int(now.value // 1_000_000)
    base = {'surum': 'v3', 'baslangic_usd': BASE_USD, 'gecikme_dk': delay, 't0': str(t0.date())}
    annotated = []
    for fill in fills:
        target = math.ceil((int(fill['time']) + delay * MINUTE) / MINUTE) * MINUTE
        price = yurutme.get(str(fill['coin']), {}).get(target)
        annotated.append(dict(fill, _execution_time=target, _execution_price=price) if price else dict(fill))
    candles = {coin: sorted(saatlik.get(coin, []) + isaret.get(coin, []), key=lambda c: c['t'])
               for coin in {*saatlik, *isaret}}
    ledger = copy_ledger(annotated, Market(candles), None, delay, t0_ms, now_ms, FundingRates(funding), rules,
                         daily=True, tutar_egrisi=sabit_tutar_egrisi(rules), base_usd=BASE_USD)
    if ledger.get('net') is None:
        return {**base, 'durum': 'hesaplanamadi', 'neden': 'yürütülebilir dolum yok'}
    days = pd.date_range(t0.normalize(), now.normalize(), freq='1D')
    net = pd.Series(0.0, index=days)
    if len(ledger['daily']):
        net = net.add(ledger['daily'].reindex(days, fill_value=0.0), fill_value=0.0)
    equity = (BASE_USD * (1 + net.cumsum())).clip(lower=0.0)
    balance = float(equity.iloc[-1]) if len(equity) else BASE_USD
    base_series = pd.concat([pd.Series([BASE_USD]), equity.reset_index(drop=True)])
    drawdown = float((1 - base_series / base_series.cummax()).max())
    return {**base, 'bakiye_usd': balance, 'getiri': balance / BASE_USD - 1, 'dusus': drawdown,
            'egri': [[str(day.date()), float(value)] for day, value in equity.items()],
            'gerceklesen': ledger['realized'] + ledger['funding'], 'acik': ledger['unrealized_end'],
            'toplam': ledger['net'], 'funding': ledger['funding'], 'maliyet': ledger['costs'],
            'fiyatsiz_eylem': int(ledger.get('missing', 0)),
            'tasfiye': False, 'tasfiye_zamani': None, 'tasfiye_kaynagi': None, 'kapanis_nedenleri': []}
