"""Kalıcılık keşif testi (``copytrade/kalicilik.py``) ve deneme defteri (``copytrade/deneme.py``). Yalnız sentetik veri; cevabı bilinen dünyalar."""
import json
from pathlib import Path

import numpy as np
import pytest

from copytrade import deneme, kalicilik as k
from copytrade.kurallar import load_rules

RULES = load_rules()
ROOT = Path(__file__).resolve().parents[1]
DAY = 86_400_000
NOW = 1_793_000_000_000


# ------------------------------------------------------------------ deneme defteri
def test_deneme_defteri_yalniz_eklemeli_onkayit_sonuctan_once(tmp_path):
    y = tmp_path / "d.jsonl"
    with pytest.raises(ValueError, match="önkayıt yok"):
        deneme.sonuc("d1", "x", yol=y)
    deneme.onkayit("d1", "h", "skor", "pencere", "ölçüt", yol=y, tarih="2026-10-29", sha="abc")
    onceki = y.read_text()
    with pytest.raises(ValueError, match="zaten kayıtlı"):
        deneme.onkayit("d1", "h", "skor", "pencere", "ölçüt", yol=y)
    assert deneme.sayim(y) == {"toplam": 1, "sonuclu": 0, "bekleyen": 1}
    deneme.sonuc("d1", "sonuç metni", yol=y, tarih="2026-10-30")
    with pytest.raises(ValueError, match="zaten yazıldı"):
        deneme.sonuc("d1", "tekrar", yol=y)
    assert y.read_text().startswith(onceki)                      # eski satırlar aynen duruyor (silme/değiştirme yok)
    assert deneme.sayim(y) == {"toplam": 1, "sonuclu": 1, "bekleyen": 0}
    on, sonuc = deneme.oku(y)
    assert on["kod_sha"] == "abc" and on["tur"] == "onkayit" and sonuc["tur"] == "sonuc" and sonuc["id"] == "d1"


def test_deneme_defterinde_bos_alan_olamaz_ve_bu_gorevin_uc_denemesi_kayitli():
    with pytest.raises(ValueError, match="boş alan"):
        deneme.onkayit("x", " ", "s", "p", "o", yol=Path("/tmp/yok_defter.jsonl"), sha="a")
    satirlar = deneme.oku(ROOT / "arastirma/copytrade/deneme_defteri.jsonl")
    on = [r for r in satirlar if r["tur"] == "onkayit"]
    assert [r["id"] for r in on] == ["kalicilik-getiri-90", "kalicilik-calmar-90", "kalicilik-karli-ay-180"]
    assert all(r["kod_sha"] not in ("", "bilinmiyor") and r["basari_olcutu"] for r in on)
    assert not [r for r in satirlar if r["tur"] == "sonuc"]      # sonuçlar gerçek koşudan sonra eklenir


# ------------------------------------------------------------------ skorlar (elle hesap) ve geleceğe bakmama
def dogrusal(gun=300, artis=10.0):
    z = [NOW - (gun - i) * DAY for i in range(gun + 1)]
    return {"av": [[t, 1000.0] for t in z], "pnl": [[t, artis * i] for i, t in enumerate(z)]}


def test_skorlar_elle_hesap_dogrusal_artis():
    # günde +10 $, hesap 1000 $: 90 günde +900 → getiri 0,9; düşüş 0 → Calmar = 0,9 / taban 0,01 = 90; 6 ayın 6'sı kârlı → 1,0
    s = k.skorlar(dogrusal(), NOW, RULES)
    assert s["getiri"] == pytest.approx(0.9) and s["calmar"] == pytest.approx(0.9 / RULES["kalicilik_mdd_taban"]) and s["kar_ay"] == 1.0


def test_skorlar_dusus_ve_zararli_ay():
    h = dogrusal()
    # son 90 günün ortasında −400 $'lık çukur: tepe sonrası düşüş (1000+450−... ) elle: dolayısıyla Calmar < taban payı
    pnl = h["pnl"]
    for i in range(len(pnl) - 60, len(pnl) - 30):
        pnl[i][1] -= 400.0
    s = k.skorlar(h, NOW, RULES)
    assert s["calmar"] < 90 and s["getiri"] == pytest.approx(0.9)
    assert s["kar_ay"] == pytest.approx(5 / 6)                    # çukurun içinden geçen ay (−400 + 300) zararlı


def test_gelecege_bakma_yok_t_sonrasi_veri_skoru_degistirmez():
    h = dogrusal()
    t = NOW - 100 * DAY
    once = k.skorlar(h, t, RULES)
    bozuk = {"av": [[a, b] for a, b in h["av"]], "pnl": [[a, b + (1e6 if a > t else 0.0)] for a, b in h["pnl"]]}
    k._SERI.clear()
    assert k.skorlar(bozuk, t, RULES) == once                       # T'den sonraki noktalar değiştirildi → skor aynı
    eski = {"av": h["av"], "pnl": [[a, b + (5000.0 if t - 30 * DAY < a <= t else 0.0)] for a, b in h["pnl"]]}
    k._SERI.clear()
    assert k.skorlar(eski, t, RULES) != once                        # T öncesi değişince skor değişir (test duyarlı)


def test_ileri_getiri_yatirma_cekme_arindirilir_ve_veri_bosluğu_disarida():
    h = dogrusal()
    t = NOW - 100 * DAY
    f = k.ileri_getiri(h, t, 28, RULES)
    assert f == pytest.approx(280.0 / 1000.0)                      # 28 gün × 10 $ / pencere hesap değeri medyanı
    para = {"av": [[a, b + (700.0 if a > t else 0.0)] for a, b in h["av"]], "pnl": h["pnl"]}
    k._SERI.clear()
    assert k.ileri_getiri(para, t, 28, RULES) == pytest.approx(f)  # T sonrası yatırma PnL'yi ve T anı payda'yı etkilemez
    kesik = {"av": h["av"], "pnl": [[a, b] for a, b in h["pnl"] if not (t < a <= t + 28 * DAY)]}
    k._SERI.clear()
    assert k.ileri_getiri(kesik, t, 28, RULES) is None              # pencere sonunda 7 günden uzun boşluk → dışarıda
    assert k.ileri_getiri(h, NOW - 5 * DAY, 28, RULES) is None      # henüz geçmemiş pencere


def test_t_anlari_26_adet_14_gun_adim_son_t_en_uzun_ileri_pencere_oncesi():
    t = k.t_anlari(NOW, RULES)
    assert len(t) == 26 and t[-1] == NOW - 56 * DAY and all(b - a == 14 * DAY for a, b in zip(t, t[1:]))


# ------------------------------------------------------------------ dilim testi
def test_dilim_testi_tam_duzenli_dunya_ve_az_hesapta_atlama():
    veri = {f"0x{i:03x}": {"skor": {"getiri": float(i), "calmar": None, "kar_ay": None}, "ileri": {28: 0.001 * i, 56: None}} for i in range(100)}
    r = k.dilim_testi(veri, "getiri", 28, RULES)
    assert r["n"] == 100 and r["rho"] == pytest.approx(1.0)
    assert r["dilim_ort"][0] == pytest.approx(0.001 * np.mean(range(80, 100))) and r["ust_alt"] == pytest.approx(0.001 * (89.5 - 9.5))
    assert k.dilim_testi(veri, "getiri", 56, RULES) is None and k.dilim_testi(veri, "calmar", 28, RULES) is None      # ileri/skor yok → hesap sayılmaz
    az = dict(list(veri.items())[:49])
    assert k.dilim_testi(az, "getiri", 28, RULES) is None            # 5 dilim × 10 hesap = 50 altı


def test_blok_bootstrap_sabit_seri_ve_tekrarlanabilirlik():
    kural = {**RULES, "kalicilik_bootstrap_tekrar": 200}
    assert k.blok_bootstrap_ci([0.05] * 12, kural) == pytest.approx((0.05, 0.05, 0.05))
    x = [0.01, 0.03, -0.01, 0.02, 0.04, 0.0, 0.05, 0.02]
    assert k.blok_bootstrap_ci(x, kural) == k.blok_bootstrap_ci(x, kural)
    ort, alt, ust = k.blok_bootstrap_ci(x, kural)
    assert alt <= ort <= ust and ort == pytest.approx(np.mean(x))


def test_sentetik_dogrulama_beceri_varken_evet_yokken_asla_evet_degil():
    """Cevabı bilinen iki dünya (n=120 hesap, hızlı bootstrap): kalıcı beceri → en az 4/6 skor-pencere 'evet'; beceri yok → 0/6."""
    kural = {**RULES, "kalicilik_bootstrap_tekrar": 300}
    d = k.sentetik_dogrulama(kural, n=120)
    assert d["evet_var"] >= 4 and d["evet_yok"] == 0 and d["gecti"]
    assert all(h != "ters yönde" for s in d["hukum"]["yok"].values() for h in s.values())


# ------------------------------------------------------------------ kopya notu
class SahteIstemci:
    def __init__(self, t_ms, dolumlar, tam_pencere=False):
        self.t, self.dolumlar, self.tam = t_ms, dolumlar, tam_pencere

    def fills(self, adres, start_ms, max_rows=None, end_ms=None):
        if max_rows and self.tam:
            return [{"time": 1}] * max_rows
        return list(self.dolumlar.get(adres, []))

    def candles(self, coin, start_ms, end_ms, interval="1m"):
        return [{"t": self.t + h * 3_600_000, "o": 100.0 if h < 5 else 110.0, "h": 110.0, "l": 100.0, "c": 100.0 if h < 5 else 110.0} for h in range(0, 24 * 30 + 1)]


def test_kopya_notu_elle_hesap_ve_pencere_disi_dislanir():
    t = NOW - 100 * DAY
    adres = "0x" + "a" * 40
    hesap = {adres: dogrusal()}
    hesap[adres]["pnl"] = [[a, (0.0 if a <= t else 12.0 * min(1.0, (a - t) / (28 * DAY))) + (b * 0 if False else 0.0)] for a, b in hesap[adres]["pnl"]]
    hesap[adres]["pnl"] = [[a, (0.0 if a <= t else 12.0)] for a, _ in hesap[adres]["pnl"]]        # T'de 0, sonra 12 $ → trader getirisi 12 / 1000
    dolum = {adres: [{"time": t + 3_600_000, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0", "tid": 1},
                     {"time": t + 5 * 3_600_000, "coin": "BTC", "side": "A", "sz": "1", "px": "110", "startPosition": "1", "tid": 2}]}
    sonuc = k.kopya_notu([adres], hesap, t, 28, SahteIstemci(t, dolum), RULES, log=lambda *a: None)
    beklenen = 0.01 - 0.001 * (100 + 110) * (RULES["maliyet_taker"] + RULES["maliyet_kayma"])        # 1/1000 ölçek, 10 $ fark, iki yön maliyet
    for g in ("30", "120"):
        o = sonuc["ortalama"][g]
        assert o["n"] == 1 and o["trader"] == pytest.approx(0.012) and o["kopya"] == pytest.approx(beklenen, abs=1e-9) and o["asinma"] == pytest.approx(0.012 - beklenen, abs=1e-9)
    kesik = k.kopya_notu([adres], hesap, t, 28, SahteIstemci(t, dolum, tam_pencere=True), RULES, log=lambda *a: None)
    assert kesik["disarida"] == {"pencere dışı (API son dolumlar penceresi)": 1} and kesik["ortalama"]["30"]["n"] == 0


# ------------------------------------------------------------------ rapor ve iş akışı
def test_rapor_ilk_satir_soru_kanit_yok_ve_evet_durumlari():
    kural = {**RULES, "kalicilik_bootstrap_tekrar": 100}
    hesaplar = k.sentetik_hesaplar(100, NOW, False, 5)
    sonuc = k.analiz(hesaplar, NOW, kural)
    metin = k.rapor(sonuc, {"toplam": 3, "sonuclu": 0, "bekleyen": 3}, None, kural, kaynak="sentetik")
    ilk5 = metin.splitlines()[:5]
    assert ilk5[0] == "# Kalıcılık testi: skor gelecek getiriyi söylüyor mu?" and "**Kanıt yok:**" in ilk5[2] and "toplam 3 deneme" in metin
    assert "hayatta kalan yanlılığı" in metin and "| (a) 90 gün getiri | 28 gün |" in metin and "## Sınırlamalar" in metin
    vars_ = k.analiz(k.sentetik_hesaplar(100, NOW, True, 6), NOW, kural)
    assert "**Kısmen evet:**" in k.rapor(vars_, {"toplam": 3, "sonuclu": 0, "bekleyen": 3}, None, kural)


def test_is_akisi_elle_parcali_zaman_asimi_korumali_ve_sentetik_once():
    text = (ROOT / ".github/workflows/kalicilik.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text and "schedule:" not in text and "--sentetik" in text and "--topla" in text and "--sure-sn" in text and "matrix:" in text
    assert text.index("--sentetik") < text.index("--topla") and "timeout-minutes" in text and "needs:" in text
    assert "|| true" not in text and "continue-on-error" not in text


def test_yaml_anahtarlari():
    assert [RULES[x] for x in ("kalicilik_getiri_gun", "kalicilik_kar_ay_gun", "kalicilik_dilim", "kalicilik_adim_gun")] == [90, 180, 5, 14]
    assert RULES["kalicilik_ileri_gun"] == [28, 56] and RULES["kalicilik_kopya_ornek"] == 100 and RULES["kalicilik_kopya_gecikme_dk"] == [30, 120]
