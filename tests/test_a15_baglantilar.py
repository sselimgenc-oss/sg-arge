"""A15 bağlantıları: defter işaret yaşı geçerli mumla ölçülür (E4 ile birleşik); kapı akıl sağlığı raporunda mum özeti."""
import pytest

from copytrade.defter import DAY, HOUR, Market, copy_ledger
from copytrade.kurallar import load_rules

RULES = load_rules()
T0 = 20_833 * DAY


def mum(hour, o, h=None, l=None, c=None):
    return {"t": T0 + hour * HOUR, "T": T0 + (hour + 1) * HOUR - 1, "s": "BTC", "i": "1h", "o": str(o), "c": str(c if c is not None else o),
            "h": str(h if h is not None else o + 1), "l": str(l if l is not None else o - 1), "v": "10", "n": 5}


def test_market_mark_bozuk_ve_sicrama_mumlarini_atlar_son_gecerli_mumu_kullanir():
    candles = {"BTC": [mum(0, 100), mum(1, 100), mum(2, 7, h=3, l=9, c=7), mum(3, 40)]}      # saat 2 bozuk (h<l), saat 3 çöküş (100 → 40, ÷2,5)
    market = Market(candles)
    assert market.mark_at("BTC", T0 + 3 * HOUR + 30 * 60_000) is None                         # son geçerli mum 2,5 sa önce > 120 dk: işaret yok (çöküş mumu 40 kullanılmaz)
    assert market.mark_at("BTC", T0 + 2 * HOUR + 30 * 60_000) == (T0 + 1 * HOUR, 100.0)      # yaş 1,5 sa ≤ 120 dk: bozuk mum atlanır
    assert market.mark_at("BTC", T0 + 1 * HOUR + 30 * 60_000) == (T0 + 1 * HOUR, 100.0)


def test_market_mark_yas_sinirini_gecerli_mumdan_olcer():
    market = Market({"BTC": [mum(0, 100), mum(1, 7, h=3, l=9, c=7)]})
    limit = int(RULES["isaret_yas_max_dk"]) * 60_000
    assert market.mark_at("BTC", T0 + limit) == (T0, 100.0)                                  # sınırda geçerli
    assert market.mark_at("BTC", T0 + limit + 1) is None and market.mark("BTC", T0 + limit + 1) is None


def test_eksik_alanli_mumlar_kontrol_edilmez_ozet_mumlar_eskisi_gibi_calisir():
    market = Market({"BTC": [{"t": T0, "o": 100, "c": 100}, {"t": T0 + HOUR, "o": 90}]})     # canlı yürütme/işaret mumları yalnız t, o taşır
    assert market.mark_at("BTC", T0 + HOUR + 1) == (T0 + HOUR, 90.0)


def test_defter_bozuk_son_mum_yuzunden_mark_missing_sayar_ve_acigi_isaretlemez():
    """Uçtan uca: 10 BTC @100 açık; son iki mum bozuk/çöküş, son geçerli mum 5 saat önce → mark_missing 1, açık K/Z 0 (bayat/bozuk fiyatla işaretlenmez)."""
    candles = {"BTC": [mum(0, 100), mum(1, 7, h=3, l=9, c=7), mum(4, 40), mum(5, 40, h=39, l=41)]}
    fills = [{"time": T0, "coin": "BTC", "side": "B", "sz": "10", "startPosition": "0", "px": "100", "tid": 1, "_execution_time": T0, "_execution_price": 100.0}]
    out = copy_ledger(fills, Market(candles), 1000, 0, T0, T0 + 5 * HOUR + 1000)
    assert out["mark_missing"] == 1 and out["unrealized_end"] == 0.0 and out["mark_time"] is None
    ok = copy_ledger(fills, Market({"BTC": [mum(0, 100), mum(1, 90)]}), 1000, 0, T0, T0 + HOUR + 1000)
    assert ok["mark_missing"] == 0 and ok["unrealized_end"] == pytest.approx(10 * (90 - 100) / 1000)


# ---------------------------------------------------------------- kapı akıl sağlığı raporu: mum özeti
def _shard(base, rows):
    import json
    import pandas as pd
    folder = base / "stage1-0" / "2026-10-28"
    folder.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(folder / "sonuc.csv", index=False)
    (folder / "evren.json").write_text(json.dumps({"evren": len(rows)}))
    (folder / "bitti.json").write_text("{}")


def test_candle_cache_mum_saglik_ozeti_coin_basina_bir_kez_hesaplanir():
    from copytrade.kapi import CandleCache

    class Client:
        calls = 0
        def candles(self, coin, s, e, interval="1h"):
            return [mum(0, 100), mum(1, 100, h=90, l=110), mum(2, 100), mum(5, 100)]            # 1 bozuk + 1 boşluk (2→5)

    cache = CandleCache(Client(), T0, T0 + 10 * HOUR)
    first = cache.saglik("BTC")
    assert first == {"mum_sayisi": 4, "mum_bozuk": 1, "mum_sicrama": 0, "mum_bosluk": 1, "mum_hacimsiz": 0, "mum_gecerli": 2}
    assert cache.saglik("BTC") is first and cache.requests == 1                                  # önbellek: yeniden hesap/istek yok


def test_kapi_satirina_mum_ozeti_ve_birlestirmede_rapor_ve_durum(tmp_path):
    """Uçtan uca: iki adresin mum sütunları → RAPOR.md 'Mum sağlığı' bölümü ve durum.json `mum_ozeti` (toplamlar, geçerli oran)."""
    import json
    import pandas as pd
    from copytrade.kapi import merge_shards
    rows = [{"address": "0xa", "asama1": "Yetersiz", "mum_sayisi": 100, "mum_bozuk": 2, "mum_sicrama": 1, "mum_bosluk": 3, "mum_hacimsiz": 0, "mum_gecerli": 94},
            {"address": "0xb", "asama1": "Yetersiz", "mum_sayisi": 300, "mum_bozuk": 0, "mum_sicrama": 3, "mum_bosluk": 0, "mum_hacimsiz": 2, "mum_gecerli": 295}]
    _shard(tmp_path / "shards", rows)
    status = merge_shards(tmp_path / "shards", tmp_path / "root", 1, "tam")["2026-10-28"]
    assert status["mum_ozeti"] == {"mum_sayisi": 400, "mum_bozuk": 2, "mum_sicrama": 4, "mum_bosluk": 3, "mum_hacimsiz": 2, "mum_gecerli": 389, "gecerli_orani": 389 / 400}
    report = (tmp_path / "root/kapi/2026-10-28/RAPOR.md").read_text(encoding="utf-8")
    assert "## Mum sağlığı (A15)" in report and "bozuk 2" in report and "sıçrama 4" in report and "%97,2" in report
    assert json.loads((tmp_path / "root/kapi/2026-10-28/durum.json").read_text())["mum_ozeti"]["mum_sayisi"] == 400


def test_mum_sutunlari_bos_olabilir_listesinde():
    for name in ("mum_sayisi", "mum_bozuk", "mum_sicrama", "mum_bosluk", "mum_hacimsiz", "mum_gecerli"):
        assert name in RULES["saglik_bos_olabilir"]
