"""Paket C — ön kayıt D v1.3 analiz kodu (gölge verisi görülmeden, elle hesaplanmış altın örneklerle dondurulur)."""
import math

import numpy as np
import pytest

from copytrade import analiz_d
from copytrade.kurallar import load_rules

RULES = load_rules()


def test_yaml_esikleri_onkayitla_ayni():
    assert (RULES["onkayit_delta_rho"], RULES["onkayit_p_max"], RULES["onkayit_blok_gun"], RULES["onkayit_veri_eksik_max"]) == (0.10, 0.05, 7, 0.05)
    assert RULES["maliyet_duyarlilik_carpani_intraday"] == 2.0 and RULES["secim_cikis_ardisik_hafta"] == 2


def test_spearman_altin_n5():
    """puan 1..5, getiri [2,1,4,3,5]: sıralar aynı → d = (−1, 1, −1, 1, 0), Σd² = 4, ρ = 1 − 6·4 / (5·24) = 0,8.
    Fisher z = atanh(0,8) = 1,098612; SE = √(1,06 / (n − 3)) = 0,728011; z/SE = 1,509060 → tek yönlü p = 0,065642;
    iki yönlü %90 GA = tanh(1,098612 ± 1,644854 × 0,728011) = [−0,098538, 0,979941]."""
    out = analiz_d.birincil_spearman([1, 2, 3, 4, 5], [2, 1, 4, 3, 5], RULES)
    assert out["n"] == 5 and out["rho"] == pytest.approx(0.8)
    assert out["p_tek_yonlu"] == pytest.approx(0.0656417, abs=1e-6)
    assert out["ga90_alt"] == pytest.approx(-0.0985384, abs=1e-6) and out["ga90_ust"] == pytest.approx(0.9799415, abs=1e-6)


def test_spearman_baglar_ortalama_sira():
    """puan [1,1,2,3] (sıralar 1,5 1,5 3 4), getiri [1,2,3,4]: ρ = 4,5 / √(4,5 × 5) = 0,948683."""
    assert analiz_d.birincil_spearman([1, 1, 2, 3], [1, 2, 3, 4], RULES)["rho"] == pytest.approx(0.948683, abs=1e-6)


def test_spearman_ters_ve_sabit_ve_kucuk_n():
    assert analiz_d.birincil_spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], RULES)["rho"] == pytest.approx(-1.0)
    flat = analiz_d.birincil_spearman([1, 2, 3, 4, 5], [7, 7, 7, 7, 7], RULES)
    assert flat["rho"] is None and flat["p_tek_yonlu"] is None                      # sabit getiri: sıra korelasyonu tanımsız
    small = analiz_d.birincil_spearman([1, 2, 3], [1, 2, 3], RULES)                  # n ≤ 3: Fisher z tanımsız → GA/p yok
    assert small["rho"] == pytest.approx(1.0) and small["p_tek_yonlu"] is None and small["ga90_ust"] is None
    with pytest.raises(ValueError):
        analiz_d.birincil_spearman([1, 2], [1], RULES)


def test_spearman_n12_altin():
    """n = 12, ρ = 0,5 (örnek özet): SE = √(1,06/9) = 0,343188; z = 0,549306 → p = 0,054733; GA = [−0,015186, 0,805401]."""
    out = analiz_d.spearman_ozeti(0.5, 12, RULES)
    assert out["p_tek_yonlu"] == pytest.approx(0.0547328, abs=1e-6)
    assert out["ga90_alt"] == pytest.approx(-0.0151862, abs=1e-6) and out["ga90_ust"] == pytest.approx(0.8054014, abs=1e-6)


BTC = np.array([0.01, -0.02, 0.03, 0.0, 0.02, -0.01, 0.01, 0.02, -0.03, 0.01, 0.0, 0.02, -0.02, 0.01])


def test_ikincil_beta_duzeltmesi_tam_uyum_altin():
    """fark = 0,002 + 0,5 × BTC tam doğrusal: β = 0,5, düzeltilmiş günlük fark = 0,002; her yeniden örneklemde aynı → GA daralır."""
    kontrol = np.full(14, 0.001)
    kohort = kontrol + 0.002 + 0.5 * BTC
    out = analiz_d.ikincil_fark(kohort, kontrol, BTC, rules=RULES, tekrar=200, tohum=1)
    assert out["beta"] == pytest.approx(0.5) and out["fark"] == pytest.approx(0.002)
    assert out["ga_alt"] == pytest.approx(0.002) and out["ga_ust"] == pytest.approx(0.002) and out["n"] == 14 and out["blok"] == 7


def test_ikincil_btc_sabitse_beta_sifir_fark_ortalama():
    out = analiz_d.ikincil_fark([0.01, 0.03, 0.01, 0.03], [0.0] * 4, [0.0] * 4, blok=2, rules=RULES, tekrar=50, tohum=3)
    assert out["beta"] == 0.0 and out["fark"] == pytest.approx(0.02)


def test_ikincil_mbb_tekrarlanabilir_ve_noktayi_kapsar():
    rng = np.random.default_rng(7)
    btc = rng.normal(0, 0.02, 84)
    kontrol = rng.normal(0, 0.01, 84)
    kohort = kontrol + 0.001 + 0.4 * btc + rng.normal(0, 0.004, 84)
    a = analiz_d.ikincil_fark(kohort, kontrol, btc, rules=RULES, tekrar=500, tohum=11)
    b = analiz_d.ikincil_fark(kohort, kontrol, btc, rules=RULES, tekrar=500, tohum=11)
    assert a == b                                                                  # aynı tohum → aynı sonuç
    assert a["ga_alt"] < a["fark"] < a["ga_ust"] and a["beta"] == pytest.approx(0.4, abs=0.1) and a["fark"] == pytest.approx(0.001, abs=0.002)
    assert analiz_d.ikincil_fark(kohort, kontrol, btc, rules=RULES, tekrar=500, tohum=12) != a
    assert "iyimser" in a["not"]                                                   # küçük örneklemde MBB aralığı iyimser (kapama ≈ %83)
    with pytest.raises(ValueError):
        analiz_d.ikincil_fark([0.0] * 3, [0.0] * 4, [0.0] * 4, rules=RULES)


def birincil(rho, n):
    return analiz_d.spearman_ozeti(rho, n, RULES)


def test_karar_uc_sonuc_altin_ornekler():
    guclu, kohort = birincil(0.6, 40), 0.05
    assert analiz_d.karar(guclu, {"fark": 0.001}, kohort, RULES)["sonuc"] == "ise_yariyor"
    # sıfır etki, büyük örneklem: GA üst sınırı (≈ 0,04) < δρ = 0,10 → işe yaramıyor
    yok = birincil(0.0, 400)
    assert yok["ga90_ust"] < 0.10 and analiz_d.karar(yok, {"fark": 0.0}, 0.05, RULES)["sonuc"] == "ise_yaramiyor"
    # küçük örneklem, etki belirsiz → sınanamadı
    belirsiz = birincil(0.3, 12)
    assert belirsiz["ga90_ust"] > 0.10 and analiz_d.karar(belirsiz, {"fark": 0.001}, 0.05, RULES)["sonuc"] == "sinanamadi"


def test_karar_yariyor_dort_kosulun_hepsi_gerekir():
    guclu = birincil(0.6, 40)
    assert guclu["p_tek_yonlu"] < 0.05
    assert analiz_d.karar(guclu, {"fark": -0.0001}, 0.05, RULES)["sonuc"] == "sinanamadi"      # ikincil nokta tahmini ≤ 0
    assert analiz_d.karar(guclu, {"fark": 0.001}, -0.01, RULES)["sonuc"] == "sinanamadi"       # kohort mutlak getirisi ≤ 0
    assert analiz_d.karar(birincil(0.2, 40), {"fark": 0.001}, 0.05, RULES)["sonuc"] == "sinanamadi"    # p ≥ 0,05
    assert analiz_d.karar(birincil(-0.4, 40), {"fark": 0.001}, 0.05, RULES)["sonuc"] != "ise_yariyor"  # ρ ≤ 0
    assert analiz_d.karar(guclu, None, 0.05, RULES)["sonuc"] == "sinanamadi"                   # ikincil yok (oda < 10 → tanımlayıcıya düşer): yarıyor denemez


def test_karar_sinir_ve_gerekce():
    edge = analiz_d.karar({"rho": 0.1, "p_tek_yonlu": 0.2, "ga90_alt": -0.1, "ga90_ust": 0.10}, None, 0.0, RULES)   # üst sınır = δρ: "< δρ" sağlanmaz
    assert edge["sonuc"] == "sinanamadi"
    just = analiz_d.karar({"rho": 0.0, "p_tek_yonlu": 0.5, "ga90_alt": -0.05, "ga90_ust": 0.0999}, None, 0.0, RULES)
    assert just["sonuc"] == "ise_yaramiyor" and "δρ" in just["gerekce"]


def test_mde_altin():
    """σ = 0,02, ρ = 0,3, n = 10, 84 gün: SD(ort. fark) = √(2 (1 − ρ) σ² / (n × gün)) = 0,000816497; k = z(0,975) + z(0,80) = 2,801585;
    MDE = 0,0022875 günlük (%0,2287), dönem toplamı = %19,21."""
    out = analiz_d.mde(0.02, 0.3, 10, 84, RULES)
    assert out["sd"] == pytest.approx(0.000816497, abs=1e-9) and out["mde_gunluk"] == pytest.approx(0.0022875, abs=1e-7)
    assert out["mde_donem"] == pytest.approx(0.1921487, abs=1e-6)
    assert "MDE" in out["satir"] and "σ=" in out["satir"] and "%0,23" in out["satir"].replace(".", ",")
    assert analiz_d.mde(0.02, 0.3, 20, 84, RULES)["mde_gunluk"] < out["mde_gunluk"]            # daha çok trader → daha küçük MDE
    with pytest.raises(ValueError):
        analiz_d.mde(0.02, 1.0, 10, 84, RULES)


def test_maliyet_duyarliligi_yalniz_intraday_iki_kat():
    assert analiz_d.duyarlilik_net(0.10, 0.02, "intraday", RULES) == pytest.approx(0.06)       # 0,10 − 2 × 0,02
    assert analiz_d.duyarlilik_net(0.10, 0.02, "swing", RULES) == pytest.approx(0.08)


def test_hafta_veri_eksik_siniri():
    assert analiz_d.veri_eksik(5, 100, RULES) is False and analiz_d.veri_eksik(6, 100, RULES) is True       # > %5 eksik
    assert analiz_d.veri_eksik(0, 0, RULES) is True                                                         # hiç veri yok = eksik
