"""Analiz koşucusu: tarih kilidi ve sonuç tablosunun biçimi (yalnız sentetik veri)."""
import json
from datetime import date

import pytest

from copytrade import analiz_kosu
from copytrade.kurallar import load_rules

RULES = load_rules()
A = [f"0x{i:040x}" for i in range(5)]


def secim():
    return {"adresler": {a: {"puan": float(i + 1), "kollar": ["havuz"], "tarz": "swing", "dilim": "swing/alt"} for i, a in enumerate(A)}}


GETIRI = {a: v for a, v in zip(A, [2, 1, 4, 3, 5])}


def test_yaml_anahtari():
    assert RULES["onkayit_analiz_tarihi"] == "2027-01-21"


def test_gercek_veri_tarihten_once_reddedilir_ve_dosya_okunmaz(tmp_path):
    with pytest.raises(analiz_kosu.TarihKilidi):
        analiz_kosu.main(["--secim", str(tmp_path / "yok.json"), "--getiri", str(tmp_path / "yok.json")], bugun=date(2027, 1, 20))


def test_gercek_veri_tarihte_ve_sonrasinda_calisir(tmp_path):
    (tmp_path / "s.json").write_text(json.dumps(secim()))
    (tmp_path / "g.json").write_text(json.dumps(GETIRI))
    metin = analiz_kosu.main(["--secim", str(tmp_path / "s.json"), "--getiri", str(tmp_path / "g.json")], bugun=date(2027, 1, 21))
    assert "GERÇEK" in metin


def test_sentetik_kilitten_muaf_ve_acikca_etiketli():
    metin = analiz_kosu.main(["--sentetik"], bugun=date(2026, 10, 29))
    assert "SENTETİK (gerçek veri değil)" in metin and "| ikincil | β |" in metin


def test_altin_ornek_tablo_bicimi():
    """n=5 puan 1..5, getiri [2,1,4,3,5]: ρ = 0,8; p = 0,0656; %90 GA [−0,0985; 0,9799] (tests/test_analiz_d.py ile aynı elle hesap)."""
    metin = analiz_kosu.tablo(analiz_kosu.kos(secim(), GETIRI, None, RULES), "GERÇEK", "2027-01-21")
    assert metin == "\n".join([
        "# 12. hafta analizi — GERÇEK — 2027-01-21", "",
        "> koşullar ne 'ise yarıyor' ne 'ise yaramıyor' için yeterli (24. haftada da sürerse 'bu ölçekte sınanamadı')", "",
        "| bölüm | ölçü | değer |", "|---|---|---|",
        "| birincil | n (havuz / eksik) | 5 (5 / 0) |", "| birincil | veri eksik | hayır |", "| birincil | ρ (Spearman) | 0,800 |",
        "| birincil | tek yönlü p | 0,066 |", "| birincil | %90 GA | [-0,099; 0,980] |",
        "| ikincil | durum | yok (oda eşiğin altında ya da günlük seri verilmedi) |", "| karar | sonuç | sinanamadi |", "",
        "## Tanımlayıcı kırılım (tarz, kaldıraç dilimi)", "", "| grup | n | ρ |", "|---|---|---|",
        "| kaldıraç: alt | 5 | 0,800 |", "| tarz: swing | 5 | 0,800 |", "| swing/alt | 5 | 0,800 |", ""])


def test_ikincil_oda_esiginin_altinda_denenmez():
    sonuc = analiz_kosu.kos(secim(), GETIRI, {"oda": [0.01] * 10, "kontrol": [0.0] * 10, "btc": [0.001 * i for i in range(10)]}, RULES)
    assert sonuc["ikincil"] is None and sonuc["karar"]["sonuc"] == "sinanamadi"
