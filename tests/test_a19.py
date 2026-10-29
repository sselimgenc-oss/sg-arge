"""Argon A19 — mevcut kodda üç düzeltme: dejenere alfa, trader düzeyinde gölge likidasyonu, dolum sayfalaması sınır kaybı.

Her test düzeltmeden ÖNCE yazıldı ve eski kodda düşer (PR açıklamasında kırmızı çıktılar).
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

from copytrade.defter import DAY, HOUR
from copytrade.golge import calistir
from copytrade.kurallar import load_rules
from copytrade.tarama import PublicClient
from kapi.istatistik import nw_alpha

RULES = load_rules()


# ----------------------------------------------------------------------------------------------- 1. dejenere alfa
def _piyasa(tohum: int, n: int = 500) -> pd.Series:
    index = pd.date_range("2020-01-01", periods=n, tz="UTC")
    return pd.Series(np.random.default_rng(tohum).normal(0, 0.01, n), index=index)


def test_kurallar_a19_anahtarlari():
    assert RULES["alfa_min_artik_varyans"] == 1.0e-12 and RULES["golge_likidasyon_esigi"] == -1.0 and RULES["api_sayfa_boyutu_dolum"] == 2000


@pytest.mark.parametrize("tohum", [4, 42, 7])
def test_nw_alpha_birebir_kopya_seri_yetersiz_doner(tohum):
    """Birebir kopyada artık varyans ~1e-35: eski kodda t = +19,8 / +131,3 gibi yapay değerler çıkar."""
    market = _piyasa(tohum)
    sonuc = nw_alpha(market, market)
    assert np.isnan(sonuc["nw_t"]) and sonuc["durum"] == "yetersiz" and abs(sonuc["alfa_yillik"]) < 1e-10


def test_nw_alpha_alfa_ne_olursa_olsun_artik_varyans_sifirsa_yetersiz():
    """market + 0,002: alfa gerçekten pozitif ama artık varyans sıfır; t anlamsız (eski kodda dev bir sayı). Alfa ne olursa olsun yetersiz."""
    market = _piyasa(2)
    sonuc = nw_alpha(market + 0.002, market)
    assert sonuc["durum"] == "yetersiz" and np.isnan(sonuc["nw_t"])
    assert sonuc["alfa_yillik"] == pytest.approx(0.002 * 252)         # alfa bilgi olarak korunur


def test_nw_alpha_gurultulu_gercek_alfa_gecerli_kalir():
    market = _piyasa(2)
    gurultu = pd.Series(np.random.default_rng(9).normal(0, 0.002, len(market)), index=market.index)
    sonuc = nw_alpha(market + 0.002 + gurultu, market)
    assert sonuc["durum"] == "gecerli" and sonuc["nw_t"] > 2


def test_nw_alpha_esik_kurallar_yamlindan_gelir():
    """Eşik fonksiyonda sabit değil: küçük bir gürültü eşiği geçerse geçerli, eşik yükseltilince aynı seri yetersiz."""
    market = _piyasa(2)
    gurultu = pd.Series(np.random.default_rng(9).normal(0, 1e-5, len(market)), index=market.index)         # artık varyans ~1e-10
    seri = market + 0.002 + gurultu
    assert nw_alpha(seri, market, min_artik_varyans=1e-12)["durum"] == "gecerli"
    assert nw_alpha(seri, market, min_artik_varyans=1e-8)["durum"] == "yetersiz"



def test_kapi_adim6_yetersiz_durum_alfa_ne_olursa_olsun_yetersiz():
    """Eski kodda alfa_yillik <= 0 → "Kaldı", pozitif ve t büyük → "Geçti"; artık varyansı sıfır seri her iki durumda da "Yetersiz"."""
    from copytrade.kapi import gate_status
    metrics = {"complete_data": True, "history_days": 400, "closed_trades": 500, "active_months": 12}
    for alfa, t_degeri in ((0.5, 131.3), (0.0, float("nan")), (-0.2, float("nan"))):
        alpha = {"beta": 1.0, "alfa_yillik": alfa, "nw_t": t_degeri, "durum": "yetersiz"}
        assert gate_status(metrics, 0.1, 0.01, alpha, RULES)["adim6"] == "Yetersiz"
    assert gate_status(metrics, 0.1, 0.01, {"beta": 1.0, "alfa_yillik": 0.5, "nw_t": 3.0, "durum": "gecerli"}, RULES)["adim6"] == "Geçti"


# ----------------------------------------------------------------------------------------------- 2. gölge likidasyonu
T0 = 20_833 * DAY


def _iki_pozisyon(zarar_fiyat: float, ikinci_coin: str = "ETH"):
    rows = [{"time": T0, "coin": "BTC", "side": "B", "sz": "10", "startPosition": "0", "px": "100", "tid": 1},
            {"time": T0, "coin": ikinci_coin, "side": "B", "sz": "10", "startPosition": "0", "px": "100", "tid": 2}]
    candles = {c: [{"t": T0, "o": 100, "c": 100}, {"t": T0 + HOUR, "o": zarar_fiyat, "c": zarar_fiyat}] for c in ("BTC", ikinci_coin)}
    return rows, candles


def test_trader_duzeyinde_toplam_likidasyon_tetiklenir():
    """Her pozisyon tek başına -0,6, toplam -1,2: çapraz teminatta hesap tasfiye olur. Eski kodda coin başına -0,6 > -1 olduğundan hiçbir olay yok."""
    rows, candles = _iki_pozisyon(40)
    out = calistir(rows, candles, 1000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR, variant="V0", delay_min=0)
    lik = [x for x in out["olaylar"] if x["durum"] == "likidasyon"]
    assert len(lik) == 2 and {x["coin"] for x in lik} == {"BTC", "ETH"} and all(x["zaman_ms"] == T0 + HOUR for x in lik)


def test_toplam_esigin_hemen_ustunde_likidasyon_yok():
    """Her biri -0,45 (toplam -0,9 > -1,0): tasfiye yok."""
    rows, candles = _iki_pozisyon(55)
    out = calistir(rows, candles, 1000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR, variant="V0", delay_min=0)
    assert not [x for x in out["olaylar"] if x["durum"] == "likidasyon"]


def test_toplam_tam_esikte_likidasyon():
    """Toplam tam -1,0 (her biri -0,5): eşik 'küçük eşit' olduğundan tasfiye."""
    rows, candles = _iki_pozisyon(50)
    out = calistir(rows, candles, 1000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR, variant="V0", delay_min=0)
    assert len([x for x in out["olaylar"] if x["durum"] == "likidasyon"]) == 2


def test_karda_pozisyon_toplami_dengeler_tekil_likidasyon_korunur():
    """BTC tek başına -1,08 (kendi 1 birimi bitti: eski davranış korunur), ETH +0,4: toplam -0,68 ama yalnız BTC tasfiye."""
    rows = [{"time": T0, "coin": "BTC", "side": "B", "sz": "15", "startPosition": "0", "px": "100", "tid": 1},
            {"time": T0, "coin": "ETH", "side": "B", "sz": "10", "startPosition": "0", "px": "100", "tid": 2}]
    candles = {"BTC": [{"t": T0, "o": 100, "c": 100}, {"t": T0 + HOUR, "o": 28, "c": 28}],
               "ETH": [{"t": T0, "o": 100, "c": 100}, {"t": T0 + HOUR, "o": 140, "c": 140}]}
    out = calistir(rows, candles, 1000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR, variant="V0", delay_min=0)
    assert [x["coin"] for x in out["olaylar"] if x["durum"] == "likidasyon"] == ["BTC"]


def test_likidasyon_esigi_kurallar_yamlindan_gelir():
    """Eşik kodda sabit değil: -0,5'e çekilince toplam -1,2'nin yanında -0,6'lık tek pozisyonlar bile tasfiye olur (her biri eşiği aşar); -5'te hiçbiri."""
    rows, candles = _iki_pozisyon(40)
    for esik, beklenen in ((-0.5, 2), (-5.0, 0)):
        out = calistir(rows, candles, 1000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR, variant="V0", delay_min=0,
                       rules={**RULES, "golge_likidasyon_esigi": esik})
        assert len([x for x in out["olaylar"] if x["durum"] == "likidasyon"]) == beklenen


# ----------------------------------------------------------------------------------------------- 3. sayfalama
class _SinirIstemci:
    fills = PublicClient.fills

    def __init__(self):
        self.all_fills = [{"tid": i, "time": 1000 + i, "coin": "BTC", "sz": "1"} for i in range(1998)]
        self.all_fills += [{"tid": i, "time": 1000 + 1998, "coin": "BTC", "sz": "1"} for i in range(1998, 2001)]        # sayfa sınırında 3 dolum aynı ms
        self.all_fills.append({"tid": 2001, "time": 1000 + 1999, "coin": "BTC", "sz": "1"})

    def info(self, payload, weight=20):
        return [f for f in self.all_fills if f["time"] >= int(payload["startTime"])][:2000]


def test_sayfa_sinirinda_ayni_milisaniyeli_dolumlar_kaybolmaz():
    """Eski kodda imleç newest + 1: 2. sayfaya sarkan tid 2000 kaybolur, len 2001 kalır."""
    sonuc = _SinirIstemci().fills("0x123", 1000)
    assert sorted(f["tid"] for f in sonuc) == list(range(2002))


class _HepsiAyniMs:
    fills = PublicClient.fills

    def info(self, payload, weight=20):
        return [{"tid": i, "time": 1000, "coin": "BTC", "sz": "1"} for i in range(2000)]


def test_tum_sayfa_ayni_milisaniyede_ise_dongu_sonlanir():
    """Sunucu startTime'ı yok sayıp hep aynı sayfayı verse bile döngü biter (yeni dolum gelmiyor)."""
    t0 = time.time()
    sonuc = _HepsiAyniMs().fills("0x123", 1000)
    assert len(sonuc) == 2000 and time.time() - t0 < 1.0


class _TamSayfaAyniMs:
    """Gerçek sunucu gibi startTime'a uyar: 2000 dolum t=1000'de, sonra 3 dolum t=1001'de. Sayfanın tamamı aynı ms: 1 ms ilerleyip devam edilmeli."""
    fills = PublicClient.fills

    def __init__(self):
        self.all_fills = [{"tid": i, "time": 1000, "coin": "BTC", "sz": "1"} for i in range(2000)]
        self.all_fills += [{"tid": 2000 + i, "time": 1001 + i, "coin": "BTC", "sz": "1"} for i in range(3)]

    def info(self, payload, weight=20):
        return [f for f in self.all_fills if f["time"] >= int(payload["startTime"])][:2000]


def test_tum_sayfa_ayni_milisaniyede_bir_ms_ilerleyip_devam_eder():
    """Eski kodda `newest <= cursor` çıkışı: sonraki 3 dolum hiç alınmaz (2000'de kalır)."""
    sonuc = _TamSayfaAyniMs().fills("0x123", 1000)
    assert sorted(f["tid"] for f in sonuc) == list(range(2003))
