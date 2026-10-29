"""Ek 2 bilgi sütunları — kapı tablosuna yazım güvenliği: sanity_check tamamen boş sütunu kırar; sıfır gecikmede tanımsız sütun üretilmemeli."""
import pandas as pd

from copytrade.kapi import DAY_MS, CandleCache, copy_window_metrics, load_rules, sanity_check

RULES = load_rules()
HOUR = 3_600_000


def test_sifir_gecikmede_yonlu_dolum_sutunlari_uretilmez_diger_gecikmelerde_dolu():
    now_ms = 1_800_000_000_000
    start = now_ms - 50 * DAY_MS
    market = {"BTC": [{"t": start - DAY_MS + i * HOUR, "o": str(100 + (i % 3))} for i in range(60 * 24)]}

    class Client:
        def candles(self, coin, s, e, interval="1h"): return market[coin]

    fills = [{"time": start + 3 * DAY_MS, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0", "closedPnl": "0", "fee": "0", "tid": 1},
             {"time": start + 4 * DAY_MS, "coin": "BTC", "side": "A", "sz": "1", "px": "100", "startPosition": "1", "closedPnl": "1", "fee": "0", "tid": 2}]
    metrics, _ = copy_window_metrics(fills, [], 1000.0, CandleCache(Client(), start, now_ms), now_ms, 6)
    assert "gecikme_0dk_yonlu_dolum_ortalama_bp" not in metrics and "gecikme_0dk_yonlu_dolum_iyi_orani" not in metrics    # sıfır gecikme: kaynak fiyat = yürütme fiyatı
    for delay in (5, 30, 120, 480):
        assert metrics[f"gecikme_{delay}dk_yonlu_dolum_sayisi"] == 2 and metrics[f"gecikme_{delay}dk_yonlu_dolum_ortalama_bp"] is not None
    assert metrics["gecikme_30dk_acik_pozisyon_sayisi"] == 0 and metrics["gecikme_30dk_mark_missing"] == 0           # pozisyon kapandı


def test_yeni_bilgi_sutunlari_akil_sagligi_kapisini_kirmaz():
    """Bütün satırlarda None olabilecek yeni sütunlar saglik_bos_olabilir listesinde değilse yayım kırılır; dolu sütunlar kırmaz."""
    row = {"address": "0xa", "adim1": "Geçti", "adim2": "Geçti", "sinif": "Geçti", "neden": "ok", "acik_pozisyon_sayisi": 0, "unrealized_end": 0.0, "mark_missing": 0,
           "acik_pozisyon_notional": 0.0, "yonlu_dolum_sayisi": 3, "yonlu_dolum_iyi_orani": 0.4, "yonlu_dolum_kotu_orani": 0.5, "yonlu_dolum_ortalama_bp": 1.0,
           "en_iyi_islem_haric_getiri": 0.01, "gunluk_islem_sikligi": 1.0}
    problems = sanity_check(pd.DataFrame([row]), RULES)
    assert not [p for p in problems if "boş sütun" in p]
