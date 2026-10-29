"""Maliyet duyarlılık raporu (``copytrade/maliyet_rapor.py``): doğrusal maliyet ayrıştırması, sınıf bölme, oda değişimi, rapor metni."""
from __future__ import annotations

import pytest

from copytrade import maliyet_rapor as m
from copytrade.defter import DAY, HOUR, Market, copy_ledger, cost_rate
from copytrade.kurallar import load_rules

RULES = load_rules()
T0 = 20_833 * DAY
A = 1000.0


def mumlar(coin, fiyat):
    return {coin: [{"t": T0 + h * HOUR, "o": str(fiyat), "c": str(fiyat)} for h in range(0, 30)]}


def dolum(dk, taraf, miktar, once, px, coin):
    return {"time": T0 + dk * 60_000, "coin": coin, "side": taraf, "sz": str(miktar), "startPosition": str(once), "px": str(px), "tid": dk}


def test_coin_sinifi_kurallardan():
    assert m.coin_sinifi("BTC", RULES) == "buyuk" and m.coin_sinifi("sol", RULES) == "buyuk"
    assert m.coin_sinifi("DOGE", RULES) == "kucuk"
    assert m.coin_sinifi("xyz:TSLA", RULES) == "hip3"


def test_senaryo_oranlari_a17_alt_uc_ve_hip3_ucret_carpani():
    oranlar = m.sinif_oranlari(RULES)
    assert oranlar["a"] == {"buyuk": 0.00095, "kucuk": 0.00095, "hip3": 0.00095}
    assert oranlar["b"] == {"buyuk": 0.00055, "kucuk": 0.00125, "hip3": 0.0034}
    # (c): HIP-3 taker ücreti 2× = 0,0009 + kayma 0,0005
    assert oranlar["c"]["hip3"] == pytest.approx(0.0014) and oranlar["c"]["buyuk"] == 0.00095


def test_senaryo_puani_elle_hesap():
    # puan 0,10; HIP-3 maliyeti 0,02 (oran 0,00095'te) → oran 0,0014: 0,02 × (0,0014/0,00095 − 1) = 0,009474 düşer
    got = m.senaryo_puani(0.10, {"buyuk": 0.01, "kucuk": 0.0, "hip3": 0.02}, m.sinif_oranlari(RULES)["c"], cost_rate(RULES))
    assert got == pytest.approx(0.10 - 0.02 * (0.0014 / 0.00095 - 1))
    assert m.senaryo_puani(None, {}, m.sinif_oranlari(RULES)["c"], cost_rate(RULES)) is None
    assert m.senaryo_puani(0.1, {"buyuk": 0.01, "kucuk": 0.0, "hip3": 0.0}, m.sinif_oranlari(RULES)["a"], cost_rate(RULES)) == pytest.approx(0.1)


def test_dogrusal_ayristirma_gercek_defterle_tutar():
    """Sınıf defterlerinin net toplamı tam defterin netidir; senaryo puanı oranı gerçekten değiştirerek koşulan defterle aynıdır."""
    fills = [dolum(60, "B", 10, 0, 100, "BTC"), dolum(120, "A", 10, 10, 110, "BTC"),
             dolum(60, "B", 5, 0, 20, "DOGE"), dolum(180, "A", 5, 5, 25, "DOGE"),
             dolum(90, "B", 8, 0, 50, "xyz:TSLA"), dolum(200, "A", 8, 8, 40, "xyz:TSLA")]
    piyasa = Market({**mumlar("BTC", 100), **mumlar("DOGE", 20), **mumlar("xyz:TSLA", 50)})
    bas, son = T0 - DAY, T0 + 24 * HOUR
    siniflar = m.sinif_defterleri(fills, piyasa, A, 0, bas, son, None, RULES)
    tam = copy_ledger(fills, piyasa, A, 0, bas, son, None, RULES)
    assert sum(v["net"] for v in siniflar.values()) == pytest.approx(tam["net"])
    assert sum(v["costs"] for v in siniflar.values()) == pytest.approx(tam["costs"])
    assert all(v["costs"] > 0 for v in siniflar.values())
    # bağımsız doğrulama: (b) oranlarıyla her sınıf defteri gerçekten yeniden koşulur
    oranlar = m.sinif_oranlari(RULES)["b"]
    tahmin = m.senaryo_puani(tam["net"], {k: v["costs"] for k, v in siniflar.items()}, oranlar, cost_rate(RULES))
    gercek = sum(copy_ledger([f for f in fills if m.coin_sinifi(f["coin"], RULES) == k], piyasa, A, 0, bas, son, None,
                             {**RULES, "maliyet_taker": oranlar[k] - RULES["maliyet_kayma"]})["net"] for k in m.SINIFLAR)
    assert tahmin == pytest.approx(gercek)


def test_hip3_hacim_payi_perp_hacmi():
    fills = [dolum(1, "B", 1, 0, 100, "BTC"), dolum(2, "B", 3, 0, 100, "xyz:TSLA"), dolum(3, "B", 1, 0, 1, "@107")]      # spot sayılmaz
    pay = m.hip3_hacim_payi(fills, RULES)
    assert pay["hip3"] == pytest.approx(0.75) and pay["buyuk"] == pytest.approx(0.25) and pay["kucuk"] == 0.0
    assert m.hip3_hacim_payi([], RULES)["hip3"] is None


KURAL = {**RULES, "secim_oda_max": 2, "secim_oda_min": 1, "secim_aday_orani": 1.0}


def satir(ad, puan):
    return {"address": "0x" + ad * 40, "tarz": "swing", "puan": puan, "genc_aday": False, "iliskili_adresler": ""}


def test_oda_degisimi_puan_degisince_giren_ve_cikan():
    havuz = [satir("a", 0.30), satir("b", 0.20), satir("c", 0.10)]
    a = m.oda_kumeleri(havuz, {r["address"]: r["puan"] for r in havuz}, KURAL)
    assert a["oda"] == ["0x" + "a" * 40, "0x" + "b" * 40]
    yeni = {"0x" + "a" * 40: -0.05, "0x" + "b" * 40: 0.20, "0x" + "c" * 40: 0.10}          # a eksiye düşer: aday olmaz
    s = m.oda_kumeleri(havuz, yeni, KURAL)
    assert s["oda"] == ["0x" + "b" * 40, "0x" + "c" * 40]
    assert m.degisim(a["oda"], s["oda"]) == {"giren": ["0x" + "c" * 40], "cikan": ["0x" + "a" * 40]}


def ozet(cs, ar, atlanan=0):
    return {"corwin_schultz": {"medyan_bps": cs}, "abdi_ranaldo": {"makas_bps": ar}, "atlanan_mum": atlanan}


def test_sinif_makas_medyani():
    out = m.sinif_makas({"BTC": ozet(1.0, 2.0), "ETH": ozet(3.0, 4.0), "DOGE": ozet(10.0, 12.0, 2), "xyz:TSLA": ozet(30.0, None)}, RULES)
    assert out["buyuk"] == {"coin": 2, "cs_medyan_bps": 2.0, "ar_medyan_bps": 3.0, "atlanan_mum": 0}
    assert out["kucuk"]["atlanan_mum"] == 2 and out["hip3"]["ar_medyan_bps"] is None and out["hip3"]["cs_medyan_bps"] == 30.0


def test_rapor_metni_uc_senaryo_ve_giren_cikan():
    havuz = []
    for ad, puan, hip3 in (("a", 0.30, 0.0), ("b", 0.20, 0.0), ("c", 0.10, 0.0)):
        havuz.append({**satir(ad, puan), "maliyet": {"buyuk": 0.0, "kucuk": 0.0, "hip3": 0.0},
                      "hacim_payi": {"hip3": hip3, "buyuk": 1.0, "kucuk": 0.0}})
    havuz[0]["maliyet"]["hip3"] = 0.5            # a'nın maliyeti HIP-3'te yoğun: senaryo (b)'de oran 3,6× → çok düşer
    havuz[0]["hacim_payi"] = {"hip3": 0.9, "buyuk": 0.1, "kucuk": 0.0}
    veri = {"kapi_tarihi": "2026-10-28", "havuz": havuz, "dolum_eslesme": [3, 3],
            "makas": m.sinif_makas({"BTC": ozet(1.0, 2.0), "DOGE": ozet(10.0, 12.0), "xyz:TSLA": ozet(30.0, 25.0)}, RULES)}
    metin = m.rapor(veri, KURAL)
    assert "(a) mevcut maliyet" in metin and "(b) A17" in metin and "(c) HIP-3 ücreti ×2" in metin
    assert "| giren |" in metin and "| çıkan |" in metin and "90,0 %" in metin
    assert "karar değildir" in metin


# ---------------------------------------------------------------- HIP-3 alt sınıfları (K-5)
def ms_utc(y, mo, d, h, mi):
    from datetime import UTC, datetime
    return int(datetime(y, mo, d, h, mi, tzinfo=UTC).timestamp() * 1000)


def test_seans_ici_yaz_ve_kis_saati_sinirlari():
    # 2026-10-29 Perşembe, New York yaz saati (EDT = UTC−4): 13:29Z = 09:29 dışı, 13:30Z = 09:30 içi, 19:59Z içi, 20:00Z = 16:00 dışı
    assert [m.seans_ici(ms_utc(2026, 10, 29, h, mi), RULES) for h, mi in ((13, 29), (13, 30), (19, 59), (20, 0))] == [False, True, True, False]
    # 2026-11-02 Pazartesi, kış saati (EST = UTC−5): 14:29Z dışı, 14:30Z içi, 20:59Z içi, 21:00Z dışı
    assert [m.seans_ici(ms_utc(2026, 11, 2, h, mi), RULES) for h, mi in ((14, 29), (14, 30), (20, 59), (21, 0))] == [False, True, True, False]
    assert m.seans_ici(ms_utc(2026, 10, 31, 15, 0), RULES) is False          # Cumartesi
    assert m.seans_ici(ms_utc(2026, 11, 1, 15, 0), RULES) is False           # Pazar


class SahteApi:
    def info(self, body, weight=1):
        if body["type"] == "perpDexs":
            return [None, {"name": "xyz"}, {"name": "flx"}]
        meta = {"xyz": [{"name": "xyz:TSLA", "growthMode": "enabled", "deployerFeeScale": "1.0"}, {"name": "xyz:STRC", "deployerFeeScale": "0.5"}],
                "flx": [{"name": "flx:GOLD", "growthMode": "enabled", "deployerFeeScale": "0.0"}]}
        return {"universe": meta[body["dex"]]}


def test_dex_ayarlari_apidan_ve_ucret_formulu_a20_tablosu():
    ayar = m.dex_ayarlari(SahteApi())
    assert ayar["xyz:TSLA"] == {"buyume": True, "olcek": 1.0} and ayar["xyz:STRC"] == {"buyume": False, "olcek": 0.5}
    # A20 §1: büyüme + ölçek 1,0 → 0,045 × 2 × 0,1 = %0,0090; büyüme + ölçek 0 → %0,0045; standart + ölçek 1,0 → %0,0900; standart + ölçek 0,5 → ×1,5
    assert m.taker_ucreti(ayar["xyz:TSLA"], RULES) == pytest.approx(0.00009)
    assert m.taker_ucreti(ayar["flx:GOLD"], RULES) == pytest.approx(0.0000450)
    assert m.taker_ucreti({"buyume": False, "olcek": 1.0}, RULES) == pytest.approx(0.0009)
    assert m.taker_ucreti(ayar["xyz:STRC"], RULES) == pytest.approx(0.000675)


def test_hip3_alt_sinif_mod_ve_seans():
    ayar = m.dex_ayarlari(SahteApi())
    ici, disi = ms_utc(2026, 10, 29, 15, 0), ms_utc(2026, 10, 31, 15, 0)
    assert m.hip3_alt_sinif("xyz:TSLA", ici, ayar, RULES) == "buyume_seans_ici"
    assert m.hip3_alt_sinif("xyz:TSLA", disi, ayar, RULES) == "buyume_seans_disi"
    assert m.hip3_alt_sinif("xyz:STRC", ici, ayar, RULES) == "standart"
    assert m.hip3_alt_sinif("zzz:BILINMEZ", ici, ayar, RULES) == "standart"        # dex ayarı yok → üst uç


def test_alt_sinif_maliyetleri_toplami_hip3_sinif_maliyetine_esit_ve_elle_hesap():
    """İki HIP-3 coin'i: TSLA (büyüme) seans içi, STRC (standart); her biri 1 birim, hesap 1000. Maliyet = notional × mevcut oran."""
    ayar = m.dex_ayarlari(SahteApi())
    t = ms_utc(2026, 10, 29, 15, 0)
    mumlar_ = {c: [{"t": t - 3 * HOUR + h * HOUR, "o": "100", "c": "100"} for h in range(0, 12)] for c in ("xyz:TSLA", "xyz:STRC")}
    fills = [{"time": t, "coin": "xyz:TSLA", "side": "B", "sz": "2", "startPosition": "0", "px": "100", "tid": 1},
             {"time": t, "coin": "xyz:STRC", "side": "B", "sz": "3", "startPosition": "0", "px": "100", "tid": 2}]
    market = Market(mumlar_)
    alt = m.alt_sinif_defterleri(fills, market, 1000.0, 0, t - HOUR, t + 5 * HOUR, None, RULES, ayar)
    sinif = m.sinif_defterleri(fills, market, 1000.0, 0, t - HOUR, t + 5 * HOUR, None, RULES)["hip3"]["costs"]
    oran = cost_rate(RULES)
    assert alt["buyume_seans_ici"] == pytest.approx(2 / 1000 * 100 * oran) and alt["standart"] == pytest.approx(3 / 1000 * 100 * oran) and alt["buyume_seans_disi"] == 0.0
    assert sum(alt.values()) == pytest.approx(sinif)
    assert m.alt_hacim_payi(fills, RULES, ayar) == {"buyume_seans_ici": pytest.approx(0.4), "buyume_seans_disi": 0.0, "standart": pytest.approx(0.6)}


def test_alt_puani_elle_hesap_ve_eksik_veri():
    # mevcut oran 0,00095; üst uçlar 0,00024 / 0,0034 / 0,0034
    alt = {"buyume_seans_ici": 0.010, "buyume_seans_disi": 0.002, "standart": 0.004}
    beklenen = 0.20 - 0.010 * (0.00024 / 0.00095 - 1) - 0.002 * (0.0034 / 0.00095 - 1) - 0.004 * (0.0034 / 0.00095 - 1)
    assert m.alt_puani(0.20, alt, RULES) == pytest.approx(beklenen)
    assert m.alt_puani(0.20, {**alt, "standart": None}, RULES) is None and m.alt_puani(None, alt, RULES) is None


def test_rapor_bolum4_alt_sinif_ve_eksik_veri_uyarisi():
    havuz = []
    for ad, puan in (("a", 0.30), ("b", 0.20), ("c", 0.10)):
        havuz.append({**satir(ad, puan), "maliyet": {"buyuk": 0.0, "kucuk": 0.0, "hip3": 0.0}, "hacim_payi": {"hip3": 0.0, "buyuk": 1.0, "kucuk": 0.0},
                      "alt_maliyet": {"buyume_seans_ici": 0.0, "buyume_seans_disi": 0.0, "standart": 0.0},
                      "alt_hacim_payi": {"buyume_seans_ici": 0.0, "buyume_seans_disi": 0.0, "standart": 0.0}})
    havuz[0]["alt_maliyet"]["standart"] = 1.0                      # a'nın HIP-3 standart maliyeti büyük: senaryo d'de oran 3,6× → odadan düşer
    havuz[0]["alt_hacim_payi"]["standart"] = 0.8
    veri = {"kapi_tarihi": "2026-10-28", "havuz": havuz, "dolum_eslesme": [3, 3], "makas": m.sinif_makas({}, RULES),
            "dex_ozet": {"xyz": {"coin": 10, "buyume": 9}}}
    metin = m.rapor(veri, KURAL)
    assert "## 4. HIP-3 alt sınıf duyarlılığı" in metin and "Standart mod 0,340 %" in metin and "Büyüme modu · ABD seansı içi 0,024 %" in metin
    assert "1 çıkan" in metin and "xyz: 10 coin, büyüme 9" in metin and "yalnız rapordur" in metin
    del havuz[1]["alt_maliyet"]
    assert "bölüm üretilmedi" in m.rapor(veri, KURAL) and "Ham veride alt sınıf maliyeti 2 / 3" in m.rapor(veri, KURAL)
