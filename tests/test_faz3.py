"""Faz 3 geçmiş prova (``copytrade/faz3.py``): pencere takvimi, Durdurma 1 kararı, çekirdek, sentetik doğrulama, T kesmeli istemci, rapor."""
import json
from datetime import date
from pathlib import Path

import pytest

from copytrade import faz3
from copytrade.kurallar import load_rules

RULES = load_rules()
ROOT = Path(__file__).resolve().parents[1]


def test_yaml_lider_kararlari():
    assert (RULES["faz3_ileri_gun"], RULES["faz3_adim_gun"], RULES["faz3_min_pencere"]) == (60, 14, 6)
    assert RULES["faz3_durdurma_orani"] == 0.50 and RULES["faz3_son_tarih"] == "2026-10-28"


def test_pencere_tarihleri_hicbiri_son_tarihi_asmaz_ve_14_gun_adim():
    t = faz3.pencere_tarihleri(RULES)
    assert len(t) == 12 and t[-1] == date(2026, 8, 29) and t[0] == date(2026, 3, 28)      # son T = 28 Ekim − 60 gün
    assert all((b - a).days == 14 for a, b in zip(t, t[1:]))
    assert max(x.toordinal() + 60 for x in t) == date(2026, 10, 28).toordinal()               # son pencere tam 28 Ekim'de biter, sonrasına taşmaz


def test_pencere_son_tarihi_asarsa_calismaz():
    with pytest.raises(AssertionError, match="faz3_son_tarih"):
        faz3.pencere_kos("2026-09-01", [], lambda a: None, {}, RULES)


def p(gecti):
    return {"gecti": gecti}


def test_durdurma_1_esik_siniri_yarisi_dahil_degil_ve_yetersiz_pencere():
    # 6 değerlendirilen: 3 geçemedi = tam 0,50 → "durdurma yok" (oran > 0,50 aranır); 4 geçemedi → öneri
    assert faz3.ozet([p(False)] * 3 + [p(True)] * 3, RULES)["sonuc"] == "durdurma yok"
    assert faz3.ozet([p(False)] * 4 + [p(True)] * 2, RULES)["sonuc"] == "durdurma önerisi"
    assert faz3.ozet([p(False)] * 5, RULES)["sonuc"] == "değerlendirilemedi"                      # 6'dan az
    o = faz3.ozet([p(False)] * 4 + [p(True)] * 2 + [p(None)] * 3, RULES)
    assert o["degerlendirilen"] == 6 and o["pencere"] == 9 and o["gecemeyen_oran"] == pytest.approx(4 / 6)       # değerlendirilemeyen pencere paydada değil


def test_sentetik_pencere_tohumla_ayni_ve_secim_kurali_isler():
    a = faz3.sentetik_pencere(7, 0.0, RULES, n_trader=40)
    b = faz3.sentetik_pencere(7, 0.0, RULES, n_trader=40)
    assert a[0] == b[0] and a[3] == b[3] == faz3.pencere_tarihleri(RULES)[0]
    with faz3.kural_onbellegi(RULES):
        sonuc = faz3.pencere_kos(a[3], a[0], a[1], a[2], RULES, tekrar=100, varyantlar=("V0", "V1", "V2"))
    assert sonuc["havuz"] == 40 and sonuc["oda"] >= 2 and sonuc["kontrol"] == sonuc["oda"] - sonuc["eslesmeyen"]
    assert set(sonuc["varyant"]) == {"V0", "V1", "V2"} and sonuc["gecti"] in (True, False) and sonuc["spearman"]["n"] == 40
    assert sonuc["disarida"] == {"sayi": 0, "nedenler": {}} and "taban" in sonuc["not"]


def test_disarida_kalan_adres_sayilir_ve_cift_kaybolur():
    satirlar, ileri, mumlar, t = faz3.sentetik_pencere(7, 0.0, RULES, n_trader=40)
    with faz3.kural_onbellegi(RULES):
        tam = faz3.pencere_kos(t, satirlar, ileri, mumlar, RULES, tekrar=100, spearman=False, varyantlar=("V0",))
        kesik = faz3.pencere_kos(t, satirlar, lambda a: "pencere dışı" if int(a, 16) % 2 == 0 else ileri(a), mumlar, RULES, tekrar=100, spearman=False, varyantlar=("V0",))
    assert kesik["disarida"]["sayi"] > 0 and kesik["disarida"]["nedenler"]["pencere dışı"] == kesik["disarida"]["sayi"]
    assert kesik["varyant"]["V0"]["cift"] < tam["varyant"]["V0"]["cift"]


def test_sentetik_dogrulama_yapisi_ve_etki_sifir_etkiden_cok_yakalanir():
    """Küçük (3 tohum, 40 trader) hızlı koşu: yapı + yön. Tam doğrulama (200 tohum) `python -m copytrade.faz3 --sentetik` ve RAPOR'da."""
    d = faz3.sentetik_dogrulama(RULES, n_tohum=3, tekrar=100, n_trader=40)
    assert set(d) == {"tohum", "q", "sifir_etki", "etki", "gecti"} and d["sifir_etki"]["degerli"] >= 1
    assert d["etki"]["nokta_pozitif"] >= d["sifir_etki"]["nokta_pozitif"]


class SahteIstemci:
    def __init__(self, t_ms):
        self.t_ms, self.sorgular = t_ms, []

    def portfolio(self, address):
        ileri = self.t_ms + 86_400_000
        return [["allTime", {"accountValueHistory": [[self.t_ms - 1000, "500"], [self.t_ms, "600"], [ileri, "9000"]], "pnlHistory": [[self.t_ms - 1, "5"], [ileri, "700"]]}]]

    def fills(self, address, start_ms, max_rows=None, end_ms=None):
        self.sorgular.append(("fills", end_ms))
        return []

    def candles(self, coin, start_ms, end_ms, interval="1m"):
        self.sorgular.append(("candles", end_ms))
        return []

    def info(self, payload, weight=20):
        self.sorgular.append((payload["type"], payload.get("endTime")))
        return []

    def leaderboard(self):
        return []


def test_gecmis_istemci_t_sonrasini_gostermez():
    t_ms = faz3.ms("2026-08-29")
    c = SahteIstemci(t_ms)
    g = faz3.GecmisIstemci(c, t_ms)
    pf = dict(g.portfolio("0xa"))["allTime"]
    assert [v for _, v in pf["accountValueHistory"]] == ["500", "600"] and [v for _, v in pf["pnlHistory"]] == ["5"]
    assert g.info({"type": "clearinghouseState", "user": "0xa"})["marginSummary"]["accountValue"] == "600.0"     # bugünkü (9000) değil
    g.fills("0xa", t_ms - 10, end_ms=t_ms + 10 ** 9)
    g.fills("0xa", t_ms - 10)
    g.candles("BTC", t_ms - 10, t_ms + 10 ** 9)
    g.info({"type": "userFunding", "user": "0xa", "startTime": 0, "endTime": t_ms + 10 ** 9})
    assert all(end == t_ms for _, end in c.sorgular)                                                           # her sorgu T ile kesildi
    assert g.info({"type": "perpDexs"}) == [] and g.info({"type": "spotClearinghouseState", "user": "0xa"}) == {"balances": []}


def test_gercek_kaynak_ileri_veri_pencere_disi_ve_hesapsiz_adres_disarida():
    t = date(2026, 8, 29)
    c = SahteIstemci(faz3.ms(t))
    limit = int(RULES["api_dolum_pencere_siniri"])
    c.fills = lambda address, start_ms, max_rows=None, end_ms=None: [{"time": 1}] * (limit if max_rows else 5)
    satirlar, ileri, mumlar = faz3.gercek_kaynak(t, [], c, RULES)
    assert satirlar == [] and ileri("0xa").startswith("pencere dışı")
    c.fills = lambda address, start_ms, max_rows=None, end_ms=None: []
    assert ileri("0xa") == "hesap değeri yok"                       # etiket satırı yoksa hesap değeri bilinmez → sessiz sıfır değil, dışarıda


def test_rapor_bicimi_durdurma_ve_iyimser_ust_sinir():
    pencere = {"t": "2026-03-28", "havuz": 100, "oda": 10, "kisa_oda": False, "eslesmeyen": 0, "sigma": 0.01, "rho": 0.1, "fark": -0.0002, "gecti": False,
               "varyant": {"V0": {"cift": 9, "ga_alt": -0.0004, "ga_ust": 0.0001}, "V1": {"cift": 9, "fark": 0.0001}, "V2": {"cift": 9, "fark": -0.0003}},
               "spearman": {"rho": 0.12}, "rejim": "yatay", "disarida": {"sayi": 3, "nedenler": {"pencere dışı": 3}}}
    dogrulama = {"tohum": 200, "q": 0.7, "gecti": True, "sifir_etki": {"degerli": 200, "ga_alt_pozitif": 0.03, "nokta_pozitif": 0.5}, "etki": {"degerli": 200, "ga_alt_pozitif": 0.95, "nokta_pozitif": 1.0}}
    metin = faz3.rapor([pencere] * 6, dogrulama, RULES, kaynak="test")
    assert "yanlış pozitif 0,030" in metin and "**geçti**" in metin and "iyimser üst sınır" in metin
    assert "**Sonuç: durdurma önerisi.**" in metin and "geçemeyen 6 (oran 1,000" in metin and "pencere dışı 18" in metin and "## Güç (gerçek varyansla)" in metin
    assert "Gerçek pencere koşusu yapılmadı" in faz3.rapor([], dogrulama, RULES)
    assert "gerçek veriyle rapor yok" in faz3.rapor([], None, RULES)


def test_is_akisi_elle_sentetik_once_ve_hata_yutmaz():
    text = (ROOT / ".github/workflows/faz3.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text and "schedule:" not in text and "--sentetik" in text and "--planla" in text and "--birlestir" in text
    assert text.index("--sentetik") < text.index("--pencere") and "needs:" in text and "matrix:" in text and "timeout-minutes" in text
    assert "|| true" not in text and "continue-on-error" not in text
