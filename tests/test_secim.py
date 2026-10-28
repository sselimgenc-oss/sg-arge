"""Seçim v1 altın örnekleri (docs/GOREV_SECIM_V1.md): 12 satırlık, elle hesaplanmış kapı tablosu → havuz / aday / oda / kontrol."""
import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from copytrade import secim
from copytrade.izleme_motoru import load_list
from copytrade.kurallar import load_rules

RULES = load_rules()


def addr(name: str) -> str:
    return "0x" + name * 40


def row(name, tarz, net, genc=False, adim2="Geçti", **extra):
    delay = 30 if tarz == "intraday" else 120
    return {"address": addr(name), "tarz": tarz, "adim1": "Geçti", "adim2": adim2, "kapi_gecikme_dk": delay,
            f"gecikme_{delay}dk_net": net, "genc_aday": genc, "median_leverage": 1.5, "max_leverage": 4.0, "gecmis_gun": 400.0,
            "account_value": 1000.0, "hesap": "v1.1-test", **extra}


# intraday (gecikme 30 dk): a..g; swing (120 dk): 1..4 (hex hane '1'..'4'); x = adım 2 Kaldı (havuz dışı)
TABLE = pd.DataFrame([
    row("a", "intraday", 0.50),
    row("b", "intraday", 0.40, genc=True),
    row("c", "intraday", 0.30, iliskili_adresler=addr("a")),       # a ile bağlı, puanı düşük
    row("d", "intraday", 0.20),
    row("e", "intraday", 0.10),
    row("f", "intraday", -0.05),                                    # negatif puan: aday olamaz
    row("0", "intraday", None),                                     # puansız: havuzda, aday değil
    row("1", "swing", 0.60),
    row("2", "swing", 0.80, genc=True),
    row("3", "swing", 0.05),
    row("4", "swing", 0.02),
    row("9", "swing", 0.99, adim2="Kaldı"),                         # havuz dışı
])


def test_havuz_ve_puan():
    pool = secim.havuz(TABLE)
    assert len(pool) == 11 and addr("9") not in {r["address"] for r in pool}        # adım 2 Kaldı
    assert {r["address"]: r["puan"] for r in pool}[addr("0")] is None               # puansız satır havuzda
    assert {r["address"]: r["puan"] for r in pool}[addr("2")] == 0.80               # swing → 120 dk sütunu
    assert {r["address"]: r["puan"] for r in pool}[addr("a")] == 0.50               # intraday → 30 dk sütunu


def test_aday_gercek_kurallarla_yuvarla_yukari():
    # intraday pozitif 5 (a,b,c,d,e): ceil(5·0,15 = 0,75) = 1 → a;  swing pozitif 4: ceil(0,6) = 1 → 2 (en yüksek puan)
    candidates = secim.adaylar(secim.havuz(TABLE), RULES)
    assert [(r["address"], r["sira"]) for r in candidates] == [(addr("a"), 1), (addr("2"), 1)]


def test_aday_az_ise_oda_tum_aday_ve_kisa_uyarisi():
    candidates = secim.adaylar(secim.havuz(TABLE), RULES)
    room = secim.oda_sec(candidates, RULES)
    assert {r["address"] for r in room["oda"]} == {addr("a"), addr("2")} and room["kisa"] is True      # 2 < 10


def test_oda_kota_genc_oncelik_ve_iliskili_hesap():
    rules = {**RULES, "secim_aday_orani": 0.5, "secim_oda_max": 3, "secim_oda_min": 2}
    # intraday ceil(2,5)=3 → a,b,c;  swing ceil(2)=2 → 2,1  (aday 5)
    candidates = secim.adaylar(secim.havuz(TABLE), rules)
    assert [r["address"] for r in candidates] == [addr("a"), addr("b"), addr("c"), addr("2"), addr("1")]
    room = secim.oda_sec(candidates, rules)
    # c, a ile bağlı ve puanı düşük → elenir (not); uygun 4 (a, b, 2, 1), hedef min(3, 4) = 3
    assert room["notlar"] == {addr("c"): f"ilişkili hesap: {addr('a')[:6]} puanı daha yüksek, o kalır"}
    # kota (aday payı 3:2 → 1,8 / 1,2): taban 1 + 1; en büyük kalan intraday → intraday 2, swing 1
    assert room["kota"] == {"intraday": 2, "swing": 1}
    # swing kotası 1: genç olmayan 1 (0,60), genç 2 (0,80) → genç olmayan önce
    assert {r["address"] for r in room["oda"]} == {addr("a"), addr("b"), addr("1")}
    assert [r["address"] for r in room["oda"]] == [addr("1"), addr("a"), addr("b")]     # sıra: genç olmayanlar (puan ↓), sonra genç
    assert room["kisa"] is False                                                        # 3 ≥ secim_oda_min 2


def test_kotalar_en_buyuk_kalan():
    assert secim._kotalar({"intraday": 3, "swing": 2}, 4) == {"intraday": 2, "swing": 2}        # 2,4 / 1,6 → 2 + 1
    assert secim._kotalar({"intraday": 1, "swing": 1}, 3) == {"intraday": 2, "swing": 1}        # 1,5 / 1,5 eşit → tarz adı sırası
    assert secim._kotalar({"intraday": 0, "swing": 0}, 3) == {"intraday": 0, "swing": 0}


def test_tohum_altin_deger_ve_kontrol_tekrarlanabilir():
    assert secim.tohum("2026-10-28") == 5430774789319239683     # sha256("secim-v1-2026-10-28") ilk 8 bayt, büyük uçlu
    pool = secim.havuz(TABLE)
    first = [r["address"] for r in secim.kontrol_sec(pool, 4, "2026-10-28")]
    assert first == [r["address"] for r in secim.kontrol_sec(pool, 4, "2026-10-28")] and len(set(first)) == 4     # aynı tarih → aynı kontrol
    assert first != [r["address"] for r in secim.kontrol_sec(pool, 4, "2026-10-29")]                              # farklı tarih → farklı kontrol
    assert addr("9") not in first                                                                                 # havuz dışı çıkmaz
    assert len(secim.kontrol_sec(pool, 99, "2026-10-28")) == 11                                                   # havuzdan fazlası istenirse havuz kadar


def test_kontrol_puana_bakmaz_oda_uyeleri_cikabilir():
    pool = secim.havuz(TABLE)
    seen = set()
    for day in range(1, 29):
        seen |= {r["address"] for r in secim.kontrol_sec(pool, 4, f"2026-10-{day:02d}")}
    assert addr("f") in seen and addr("0") in seen and addr("a") in seen                                          # negatif, puansız ve oda üyesi dahil


def test_taban_30_gunluk_pnl():
    board = [{"ethAddress": addr("a"), "windowPerformances": [["day", {"pnl": "999"}], ["month", {"pnl": "100"}]]},
             {"ethAddress": addr("b"), "windowPerformances": [["month", {"pnl": "300"}]]},
             {"ethAddress": addr("c"), "windowPerformances": [["month", {"pnl": "-5"}]]}]
    assert secim.taban_sec(board, 2) == [addr("b"), addr("a")]


def test_sec_kol_onceligi_ve_ciktilar():
    board = [{"ethAddress": addr("a"), "windowPerformances": [["month", {"pnl": "9"}]]},
             {"ethAddress": addr("z"), "windowPerformances": [["month", {"pnl": "8"}]]}]
    result = secim.sec(TABLE, "2026-10-28", board, [addr("d"), addr("y")], RULES)
    assert result["sayilar"]["oda"] == 2 and result["sayilar"]["kontrol"] == 2 and result["sayilar"]["taban"] == 2   # N = oda sayısı
    entries = result["adresler"]
    assert entries[addr("a")]["kol"] == "oda" and set(entries[addr("a")]["kollar"]) >= {"oda", "aday", "havuz", "taban"}
    assert entries[addr("d")]["kol"] == "elle" and entries[addr("y")]["kol"] == "elle" and entries[addr("y")]["tarz"] is None
    assert entries[addr("z")]["kol"] == "taban" and entries[addr("z")]["puan"] is None
    assert entries[addr("2")]["genc_aday"] is True and entries[addr("2")]["hesap_surumu"] == "v1.1-test"
    assert addr("9") not in entries                                     # adım 2 Kaldı: hiçbir kolda yok
    text = secim.rapor(result, TABLE, {"hesap": "v1.1-test", "kapsam": 1.0, "durum": "tamam"})
    assert "oda 2 adres; en az 10" in text and "secim-v1-2026-10-28" in text and "| gecikme_30dk_net |" in text


def test_izleme_listesi_mevcut_satirlari_korur_ve_dogrulanir(tmp_path: Path):
    result = secim.sec(TABLE, "2026-10-28", [], [addr("d")], RULES)
    existing = [{"id": "T1", "adres": addr("a"), "takma_ad": "aaaa", "durum": "izlemede", "t0": "2026-10-20", "tarz": "intraday"},
                {"id": "T2", "adres": addr("d"), "takma_ad": "dddd", "durum": "izlemede", "t0": "2026-10-20"}]
    rows = secim.izleme_listesi(result, existing, "2026-10-29")
    by = {r["adres"]: r for r in rows}
    assert by[addr("a")]["id"] == "T1" and by[addr("a")]["t0"] == "2026-10-20" and by[addr("a")]["kol"] == "oda"       # var olan satır değişmez
    assert by[addr("d")]["kol"] == "elle" and by[addr("2")]["t0"] == "2026-10-29" and by[addr("2")]["id"].startswith("O")
    path = tmp_path / "liste.yaml"
    secim.yaz_izleme_listesi(rows, path)
    loaded = load_list(path)                                      # izleme motorunun doğrulaması kabul eder
    assert len(loaded) == len(rows) and len({r["id"] for r in loaded}) == len(rows)
    assert secim.elle_liste(path) == [addr("d")]                  # elle kolu yeniden okunur; oda/kontrol okunmaz


def test_tam_kosu_degilse_durur(tmp_path: Path):
    day = tmp_path / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    TABLE.to_csv(day / "sonuc.csv", index=False)
    (day / "durum.json").write_text(json.dumps({"durum": "tamam", "kapsam": 0.0067}), encoding="utf-8")
    with pytest.raises(SystemExit, match="tam koşu değil"):
        secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(tmp_path / "x")])
    (day / "durum.json").write_text(json.dumps({"durum": "tamam", "kapsam": 0.94}), encoding="utf-8")
    with pytest.raises(SystemExit, match="tam koşu değil"):                                   # 0,94 < 0,95 → dur
        secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(tmp_path / "x")])
    (day / "durum.json").write_text(json.dumps({"durum": "eksik", "kapsam": 1.0}), encoding="utf-8")
    with pytest.raises(SystemExit, match="tamam değil"):
        secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28"])
    (day / "durum.json").write_text(json.dumps({"durum": "tamam", "kapsam": 0.95, "hesap": "v1.1-test"}), encoding="utf-8")     # 0,95 → çalışır
    (tmp_path / "board.json").write_text("[]", encoding="utf-8")
    secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(tmp_path / "board.json")])
    assert json.loads((tmp_path / "secim/2026-10-28/secim.json").read_text())["sayilar"]["oda"] == 2
    assert (tmp_path / "secim/2026-10-28/RAPOR.md").exists()
