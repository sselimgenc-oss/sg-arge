"""Ön kayıt D v1.4 madde 2: risk işaretleri (yalnız bilgi). Her kural için altın örnek, sınırlar dahil."""
from __future__ import annotations

import json

import pytest

from copytrade import haftalik_rapor, risk_isaretleri as ri
from copytrade.kurallar import load_rules

RULES = load_rules()
HAFTA0 = 1_000_000_000_000


def test_kurallar_v14_degerleri():
    assert RULES["risk_kaldirac_sicrama_kat"] == 2.5 and RULES["risk_tutma_anomali_kat"] == 3.0 and RULES["bayrak_kat_esik"] == 2.0


def test_kaldirac_sicramasi_sinir():
    assert ri.kaldirac_sicramasi(2.0, 5.0, RULES) is False         # tam 2,5 kat: işaretlenmez
    assert ri.kaldirac_sicramasi(2.0, 5.01, RULES) is True
    assert ri.kaldirac_sicramasi(2.0, 1.0, RULES) is False
    assert ri.kaldirac_sicramasi(None, 5.0, RULES) is None and ri.kaldirac_sicramasi(2.0, None, RULES) is None
    assert ri.kaldirac_sicramasi(0.0, 5.0, RULES) is None            # medyan 0: oran tanımsız


def test_tutma_anomalisi_sinir():
    assert ri.tutma_anomalisi([30.0], 10.0, RULES) is False         # tam 3 kat: işaretlenmez
    assert ri.tutma_anomalisi([5.0, 30.1], 10.0, RULES) is True     # en az biri aşarsa
    assert ri.tutma_anomalisi([], 10.0, RULES) is False             # zararda açık pozisyon yok
    assert ri.tutma_anomalisi(None, 10.0, RULES) is None and ri.tutma_anomalisi([50.0], None, RULES) is None


def dolum(dk, taraf, miktar, once, px, tid):
    return {"time": HAFTA0 + dk * 60_000, "coin": "BTC", "side": taraf, "sz": str(miktar), "startPosition": str(once), "px": str(px), "tid": tid, "closedPnl": "0"}


# long 1@100 açılır, 90'a düşünce 2 eklenir (kat 2/1 = 2 = bayrak_kat_esik: katlama), zararda ekleme 1, katlama oranı 1,0
KATLAMA = [dolum(0, "B", 1, 0, 100, 1), dolum(60, "B", 2, 1, 90, 2)]


def test_martingale_baslangici_altin_ornek_ve_sinirlar():
    assert ri.martingale_baslangici(0.0, KATLAMA, HAFTA0, RULES) is True                       # oran 0 → 1,0 ve son haftada 1 katlama
    assert ri.martingale_baslangici(1.0, KATLAMA, HAFTA0, RULES) is False                      # oran etiketle eşit: yüksek değil
    assert ri.martingale_baslangici(0.0, KATLAMA, HAFTA0 + 61 * 60_000, RULES) is False        # katlama son haftadan önce
    assert ri.martingale_baslangici(0.0, KATLAMA, HAFTA0 + 60 * 60_000, RULES) is True         # katlama tam hafta başında: son hafta sayılır
    az = [dolum(0, "B", 1, 0, 100, 1), dolum(60, "B", 1.99, 1, 90, 2)]                         # kat 1,99 < 2: katlama değil
    assert ri.martingale_baslangici(0.0, az, HAFTA0, RULES) is False
    assert ri.martingale_baslangici(None, KATLAMA, HAFTA0, RULES) is None and ri.martingale_baslangici(0.0, None, HAFTA0, RULES) is None


def test_uye_isaretleri_toplu_ve_eksik_veri():
    etiket = {"medyan_kaldirac": 2.0, "katlama_orani": 0.0, "medyan_tutma_saat": 10.0}
    son = {"en_yuksek_kaldirac": 6.0, "dolumlar": KATLAMA, "hafta_baslangic_ms": HAFTA0, "zarardaki_acik_yaslar_saat": [31.0]}
    assert ri.uye_isaretleri(etiket, son, RULES) == {"kaldirac_sicramasi": True, "martingale_baslangici": True, "tutma_anomalisi": True}
    assert ri.uye_isaretleri({}, {}, RULES) == {"kaldirac_sicramasi": None, "martingale_baslangici": None, "tutma_anomalisi": None}


def test_rapor_bolumu_yalniz_bilgi_performans_yok_ve_cli(tmp_path):
    adres = "0x" + "a" * 40
    risk = {adres: {"etiket": {"medyan_kaldirac": 2.0, "katlama_orani": 0.0, "medyan_tutma_saat": 10.0},
                    "son": {"en_yuksek_kaldirac": 6.0, "dolumlar": KATLAMA, "hafta_baslangic_ms": HAFTA0, "zarardaki_acik_yaslar_saat": [1.0]}}}
    result = {"secim_surumu": "v1.3", "kapi_tarihi": "2026-10-28", "adresler": {adres: {"kollar": ["oda", "havuz"], "puan": 0.4, "tarz": "swing"}}}
    (tmp_path / "secim.json").write_text(json.dumps(result), encoding="utf-8")
    (tmp_path / "risk.json").write_text(json.dumps(risk), encoding="utf-8")
    haftalik_rapor.main(["--secim", str(tmp_path / "secim.json"), "--risk", str(tmp_path / "risk.json"), "--tarih", "2026-11-05", "--cikti", str(tmp_path / "o")])
    text = (tmp_path / "o/haftalik_2026-11-05.md").read_text(encoding="utf-8")
    satir = next(line for line in text.splitlines() if line.startswith("| `0xaaaa"))
    assert "**işaretli** | **işaretli** | –" in satir                       # kaldıraç, martingale işaretli; zararda uzun tutma değil
    assert "yalnız bilgi" in text and "Otomatik çıkış yoktur" in text
    bolum = text[text.index("## Risk işaretleri"):]
    assert not any(k in bolum.lower() for k in ("getiri", "kâr", "kar ", "pnl", "0,4"))   # performans/puan sayısı yok
    haftalik_rapor.main(["--secim", str(tmp_path / "secim.json"), "--tarih", "2026-11-12", "--cikti", str(tmp_path / "o")])
    assert "Risk işaretleri" not in (tmp_path / "o/haftalik_2026-11-12.md").read_text(encoding="utf-8")     # --risk yoksa bölüm yok
