"""Seçim v1 altın örnekleri (docs/GOREV_SECIM_V1.md): 12 satırlık, elle hesaplanmış kapı tablosu → havuz / aday / oda / kontrol."""
import re
import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from copytrade import secim
from copytrade.izleme_motoru import load_list
from copytrade.kurallar import load_rules

RULES = load_rules()
WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/copytrade_secim.yml"


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


def test_havuz_adim3_statik_kosullari_altin_ornek():
    # 36,5x en yüksek kaldıraçlı satır havuza girmez (kapi_max_kaldirac 10); kısa işlem payı > 0,25 ve medyan kaldıraç > 3 de girmez.
    table = pd.DataFrame([
        row("a", "intraday", 0.5),                                          # geçer
        row("b", "intraday", 0.9, max_leverage=36.5),                       # en yüksek kaldıraç 36,5 > 10
        row("c", "intraday", 0.8, kisa_islem_payi=0.30),                    # 0,30 > 0,25
        row("d", "intraday", 0.7, kisa_islem_payi=0.25),                    # sınır: ≤ geçer
        row("e", "swing", 0.6, median_leverage=3.5),                        # medyan 3,5 > 3
        row("f", "swing", 0.4, max_leverage=10.0),                          # sınır: ≤ geçer
        row("1", "swing", 0.3, max_leverage=None),                          # eksik en yüksek kaldıraç → geçmez (kapi.py ile aynı)
        row("2", "swing", 0.2, median_leverage=None),                       # eksik medyan → geçmez
        row("3", "swing", 0.1, kisa_islem_payi=None),                       # kısa işlem payı eksik → geçer (kapi.py: short is None)
    ])
    assert [r["address"] for r in secim.havuz(table, RULES)] == sorted([addr("a"), addr("d"), addr("f"), addr("3")])


def test_havuz_kurallar_yamlindan_gelir():
    table = pd.DataFrame([row("a", "intraday", 0.5, max_leverage=7.0)])
    assert len(secim.havuz(table, RULES)) == 1
    assert secim.havuz(table, {**RULES, "kapi_max_kaldirac": 6.0}) == []     # eşik kodda değil kurallar.yaml'da


def hrow(name, tarz, lev):
    return {"address": addr(name), "tarz": tarz, "max_leverage": lev, "puan": 0.0}


def test_kontrol_anahtari_altin_deger():
    assert secim.kontrol_anahtari("2026-10-27", addr("a")) == "e2408613a83804e45a32c2f49ed60bf67f29ea0e0536316b9dfdc636ed9c56c6"
    # sha256("secim-v1.3-2026-10-27-0xaaaa…"): sürüm, kapı tarihi ve adres sırayı belirler
    assert secim.kontrol_anahtari("2026-10-28", addr("a")) != secim.kontrol_anahtari("2026-10-27", addr("a"))


def test_kontrol_eslestirilmis_dilimli_ve_odayla_ayrik():
    # en yüksek kaldıraç: a2 b2 c6 d6 | e2 f6 → medyan (2+6)/2 = 4; alt ≤ 4 < üst
    pool = [hrow("a", "intraday", 2.0), hrow("b", "intraday", 2.0), hrow("c", "intraday", 6.0), hrow("d", "intraday", 6.0),
            hrow("e", "swing", 2.0), hrow("f", "swing", 6.0)]
    oda = [pool[0], pool[4]]                                                  # a (intraday/alt), e (swing/alt)
    control, pairs, secondary = secim.kontrol_sec(pool, oda, "2026-10-27")
    assert secim.dilim_medyani(pool) == 4.0
    assert {r["address"] for r in control} == {addr("b"), addr("f")}           # a → b (aynı dilim); e → swing/alt'ta aday yok → swing/üst: f
    assert {r["address"] for r in control}.isdisjoint({r["address"] for r in oda})
    assert [(p["oda"], p["kontrol"], p["dilim"], p["yedek_dilim"]) for p in pairs] == [
        (addr("a"), addr("b"), "intraday/alt", False), (addr("e"), addr("f"), "swing/alt", True)]
    assert sorted(r["address"] for r in secondary) == sorted([addr("b"), addr("c"), addr("d"), addr("f")])      # ikincil kontrol = havuz − oda


def test_kontrol_dilim_ve_tarz_bossa_kontrol_yok():
    pool = [hrow("a", "swing", 2.0), hrow("b", "intraday", 2.0)]
    control, pairs, _ = secim.kontrol_sec(pool, [pool[0]], "2026-10-27")       # swing'de oda dışı kimse yok (diğer tarzdan alınmaz)
    assert control == [] and pairs[0]["kontrol"] is None and pairs[0]["kullanilan_dilim"] is None


def test_kontrol_hash_sirasi_ve_puana_bakmaz():
    pool = [hrow("a", "intraday", 2.0)] + [hrow(c, "intraday", 2.0) for c in "bcdef"]
    for r, puan_ in zip(pool, (0.9, -5.0, 0.0, 3.0, None, 0.1)):
        r["puan"] = puan_
    control, _, _ = secim.kontrol_sec(pool, [pool[0]], "2026-10-27")
    best = min(pool[1:], key=lambda r: secim.kontrol_anahtari("2026-10-27", r["address"]))
    assert control[0]["address"] == best["address"]                           # en küçük sha256 anahtarı; puan etkisiz
    for r in pool[1:]:
        r["puan"] = 100.0 - ord(r["address"][2])                              # puanlar değişse de seçim aynı
    assert secim.kontrol_sec(pool, [pool[0]], "2026-10-27")[0][0]["address"] == best["address"]


def test_kontrol_kapi_tarihine_baglidir_secim_gunune_degil():
    one = secim.sec(TABLE, "2026-10-28", [], [], RULES, kapi_tarihi="2026-10-27")
    again = secim.sec(TABLE, "2026-11-04", [], [], RULES, kapi_tarihi="2026-10-27")             # seçim başka günde yeniden koştu
    assert one["kontrol"] == again["kontrol"] and one["kontrol_eslesme"] == again["kontrol_eslesme"]
    assert one == {**again, "tarih": "2026-10-28"}                                              # tüm çıktı aynı (yalnız seçim günü farklı)
    assert one == secim.sec(TABLE, "2026-10-28", [], [], RULES, kapi_tarihi="2026-10-27")       # aynı girdi → aynı çıktı
    other = secim.sec(TABLE, "2026-10-28", [], [], RULES, kapi_tarihi="2026-10-30")
    assert one["kapi_tarihi"] == "2026-10-27" and other["kapi_tarihi"] == "2026-10-30"


def test_sec_kimlik_ve_kontrol_oda_ayriligi():
    result = secim.sec(TABLE, "2026-10-28", [], [], RULES, kapi_tarihi="2026-10-27")
    import hashlib
    root = Path(secim.__file__).resolve().parents[1]
    assert result["secim_surumu"] == "v1.3" and result["kapi_tarihi"] == "2026-10-27"
    assert result["kurallar_sha256"] == hashlib.sha256((root / "copytrade/kurallar.yaml").read_bytes()).hexdigest()
    assert result["kod_sha256"] == hashlib.sha256((root / "copytrade/secim.py").read_bytes()).hexdigest()
    oda = {a for a, e in result["adresler"].items() if "oda" in e["kollar"]}
    assert oda and oda.isdisjoint(result["kontrol"]) and set(result["ikincil_kontrol"]) == {a for a, e in result["adresler"].items() if "havuz" in e["kollar"]} - oda
    assert result["sayilar"]["ikincil_kontrol"] == len(result["ikincil_kontrol"])


def test_ayni_surum_ve_kapi_tarihi_uzerine_yazilmaz(tmp_path: Path):
    out = tmp_path / "secim"
    (out / "2026-10-27-v1.3").mkdir(parents=True)
    (out / "2026-10-27-v1.3/secim.json").write_text(json.dumps({"secim_surumu": "v1.3", "kapi_tarihi": "2026-10-27"}), encoding="utf-8")
    (out / "2026-10-20").mkdir()
    (out / "2026-10-20/secim.json").write_text(json.dumps({"surum": 1, "tarih": "2026-10-20"}), encoding="utf-8")     # eski v1: sürümü yok
    assert secim.yayimlandi_mi(out, "v1.3", "2026-10-27") is True
    assert secim.yayimlandi_mi(out, "v1.3", "2026-10-28") is False
    assert secim.yayimlandi_mi(out, "v1.4", "2026-10-27") is False


def test_bayrak_ayri_dosya_secim_bayraksiz(tmp_path: Path):
    result = secim.sec(TABLE, "2026-10-28", [], [], RULES, kapi_tarihi="2026-10-27")
    assert not any("bayrak_rol" in e for e in result["adresler"].values())                       # seçim bayraksız yayımlanır
    calls = []

    def fn(address, value):
        calls.append((address, value))
        return {"bayrak_rol": "vault"}

    out = secim.bayrak_uret(result, fn)
    assert sorted(a for a, _ in calls) == [addr("2"), addr("a")] and out["secim_surumu"] == "v1.3" and out["kapi_tarihi"] == "2026-10-27"
    assert set(out["bayraklar"]) == {addr("2"), addr("a")} and calls[0][1] == 1000.0


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
    assert "oda 2 adres; en az 10" in text and "sha256(secim-v1.3-<kapi_tarihi>-<adres>)" in text and "| gecikme_30dk_net |" in text
    assert "Seçim = geçmiş getiri sıralaması (adım 1–3 süzgeçli)" in text and "### Oda ↔ kontrol dilim dağılımı" in text


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
    secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(tmp_path / "board.json"), "--bayraksiz"])
    assert json.loads((tmp_path / "secim/2026-10-28-v1.3/secim.json").read_text())["sayilar"]["oda"] == 2
    assert (tmp_path / "secim/2026-10-28-v1.3/RAPOR.md").exists()
    with pytest.raises(SystemExit, match="zaten yayımlanmış"):                  # aynı sürüm + kapı tarihi: üzerine yazılmaz (başka günde de)
        secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-29", "--taban-dosyasi", str(tmp_path / "board.json")])


def test_secim_main_calistir_dosyasi_ile_tetiklenir():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "branches:\n      - main" in workflow
    assert "- copytrade/secim/CALISTIR" in workflow


def test_bayrak_ayri_is_secimi_bekletmez_ve_yeterli_sure_tanir():
    # Run 1 (22 aday) 20 dk'da iptal oldu: aday başına 365 günlük dolum/funding çekimi. v1.3: bayraklar ayrı işte, seçim bekletilmez.
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    jobs = workflow["jobs"]
    assert set(jobs) == {"secim", "bayrak"} and jobs["bayrak"]["needs"] == "secim"
    assert jobs["bayrak"]["timeout-minutes"] >= 120
    secim_steps = "\n".join(str(step.get("run", "")) for step in jobs["secim"]["steps"])
    assert "--bayrak-uret" not in secim_steps and "python -m copytrade.secim --root copytrade" in secim_steps       # seçim bayraksız
    assert "--bayrak-uret" in "\n".join(str(step.get("run", "")) for step in jobs["bayrak"]["steps"])


def test_secim_yayimi_uzerine_yazmaz_ve_klasor_adi_surumludur():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert 'secim/$day-v1.3' in text and 'üzerine yazılmaz' in text
    assert 'git archive FETCH_HEAD secim' in text            # yayımlanmış seçimler getirilir: aynı sürüm + kapı tarihi reddi


def test_secim_yayimi_seçimle_ayni_gunu_kullanir():
    # Gece yarısını geçen koşu: yayım adımı günü yeniden hesaplarsa secim/<gün> bulunamaz (denetim B24).
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "--tarih \"$day\"" in workflow and "day=${{ steps.secim.outputs.day }}" in workflow
    assert "actions/upload-artifact" in workflow
