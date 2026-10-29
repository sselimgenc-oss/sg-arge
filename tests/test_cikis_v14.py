"""Ön kayıt D v1.4 madde 1: performansa dayalı çıkış (≥ 4 hafta + ≥ 60 kapanmış işlem + havuz alt dilimi + 2 ardışık hafta)."""
from __future__ import annotations

import pytest

from copytrade import gecis
from copytrade.kurallar import load_rules

RULES = load_rules()
HAFTALAR = ["2026-11-05", "2026-11-12", "2026-11-19", "2026-11-26", "2026-12-03", "2026-12-10"]


def addr(ad: str) -> str:
    return "0x" + ad * 40


def sonuc(puanlar: dict[str, float], oda: list[str]):
    """Havuz: ad → puan; ``oda`` üyeleri secim odasında. Sıra: puan ↓."""
    return {"secim_surumu": "v1.3", "kapi_tarihi": "2026-10-28", "tarih": "2026-10-28",
            "adresler": {addr(a): {"kol": "oda" if a in oda else "havuz", "kollar": (["oda"] if a in oda else []) + ["havuz"], "puan": p}
                         for a, p in puanlar.items()}}


# 10 kişilik havuz: a (0,9) … j (0,0); alt dilim 0,50 → alt 5 kişi (f, g, h, i, j). Sınav adresi "0".
IYI = {c: 0.9 - 0.1 * i for i, c in enumerate("abcdefghij")}


def havuz_x(x_puan: float) -> dict[str, float]:
    """x'in puanı x_puan olan 10 kişilik havuz (x dahil, a–i)."""
    return {**{c: 0.9 - 0.1 * i for i, c in enumerate("abcdefghi")}, "0": x_puan}


def calistir(tmp_path, haftalar, puan_x, islem, oda_baslangic=True):
    tmp_path.mkdir(parents=True, exist_ok=True)
    """x ilk haftada girer; sonraki haftalar x'in puanı ``puan_x[hafta]`` olan havuzla değerlendirilir. Çıkış olaylarını döner."""
    kayit, deg = tmp_path / "kayit.jsonl", tmp_path / "deg.jsonl"
    olaylar = []
    for tarih in haftalar:
        px = puan_x[tarih]
        oda = ["0"] if tarih == haftalar[0] and oda_baslangic else []
        olaylar += gecis.haftalik(kayit, deg, sonuc(havuz_x(px), oda), tarih, RULES, kapanmis_islem={addr("0"): islem.get(tarih)} if islem else None)
    return [o for o in olaylar if o["olay"] == "cikis"], kayit, deg


def test_kurallar_v14_degerleri():
    assert RULES["secim_cikis_min_hafta"] == 4 and RULES["secim_cikis_min_kapanmis_islem"] == 60
    assert RULES["secim_cikis_havuz_alt_dilim"] == 0.50 and RULES["secim_cikis_ardisik_hafta"] == 2


def test_alt_dilim_siniri_10_kisilik_havuzda_alt_5():
    puanlar = {addr(c): 0.9 - 0.1 * i for i, c in enumerate("abcdefghij")}
    alt = {a for a in puanlar if gecis.alt_dilimde(a, puanlar, 0.50)}
    assert alt == {addr(c) for c in "fghij"}                         # sıra 6–10: alt %50 (sınırdaki f dahil)
    assert gecis.alt_dilimde(addr("e"), puanlar, 0.50) is False        # sıra 5 üst yarıda
    assert gecis.alt_dilimde(addr("zz"), puanlar, 0.50) is None        # havuzda yok: sıralanamaz → karar yok
    assert gecis.alt_dilimde(addr("a"), {addr("a"): None}, 0.50) is None


def test_alt_dilim_tek_sayida_havuz_yukari_yuvarlar():
    puanlar = {addr(c): 0.9 - 0.1 * i for i, c in enumerate("abcdefghi")}      # 9 kişi: alt = ceil(4,5) = 5 → sıra 5–9
    assert {a for a in puanlar if gecis.alt_dilimde(a, puanlar, 0.50)} == {addr(c) for c in "efghi"}


ALT = 0.05            # x alt dilimde (a–i arasında en düşük)
UST = 0.95            # x birinci
H = HAFTALAR


def test_4_hafta_ve_60_islem_ikisi_saglaninca_cikar(tmp_path):
    puan = {h: ALT for h in H}
    # H[0] giriş; değerlendirmeler H[1..]: H[4]'te 4. değerlendirme. Çıkış H[4]'te, 60 işlemle.
    cikis, kayit, _ = calistir(tmp_path, H[:5], puan, {h: 60 for h in H})
    assert [(c["tarih"], c["adres"]) for c in cikis] == [(H[4], addr("0"))]
    assert "4 haftalık" in cikis[0]["neden"] and "60 kapanmış" in cikis[0]["neden"]


def test_3_hafta_yetmez(tmp_path):
    cikis, _, _ = calistir(tmp_path, H[:4], {h: ALT for h in H}, {h: 500 for h in H})      # 3 değerlendirme (H1–H3), 500 işlem, alt dilim
    assert cikis == []


def test_59_islem_yetmez_60_yeter(tmp_path):
    p = {h: ALT for h in H}
    cikis59, _, _ = calistir(tmp_path / "a", H[:5], p, {h: 59 for h in H})
    assert cikis59 == []
    cikis60, _, _ = calistir(tmp_path / "b", H[:5], p, {h: 60 for h in H})
    assert len(cikis60) == 1


def test_islem_verisi_yoksa_cikis_degerlendirilemez_ve_cikmaz(tmp_path):
    cikis, _, _ = calistir(tmp_path, H[:6], {h: ALT for h in H}, None)
    assert cikis == []


def test_arada_uygun_hafta_ardisikligi_bozar(tmp_path):
    # H1 alt, H2 alt, H3 ÜST (uygun), H4 alt → H4'te yalnız 1 ardışık: çıkış yok. H5 alt → 2 ardışık (H4, H5), 5 değerlendirme: çıkar.
    p = {H[0]: UST, H[1]: ALT, H[2]: ALT, H[3]: UST, H[4]: ALT, H[5]: ALT}
    cikis4, _, _ = calistir(tmp_path / "k", H[:5], p, {h: 100 for h in H})
    assert cikis4 == []
    cikis5, _, _ = calistir(tmp_path / "m", H[:6], p, {h: 100 for h in H})
    assert [c["tarih"] for c in cikis5] == [H[5]]


def test_tek_alt_dilim_haftasi_yetmez(tmp_path):
    p = {h: UST for h in H}
    p[H[4]] = ALT                                                   # yalnız son hafta alt dilimde: 1 ardışık
    cikis, _, _ = calistir(tmp_path, H[:5], p, {h: 100 for h in H})
    assert cikis == []


def test_odadan_secim_odasinda_olmak_cikisi_engellemez_ama_ustte_olmak_engeller(tmp_path):
    """Alt dilimdeki üye seçim odasından düşmüş olsa bile v1.3'teki gibi iki hafta sonra çıkmaz: v1.4 yalnız dilim ve eşiklere bakar."""
    cikis, _, deg = calistir(tmp_path, H[:3], {h: UST for h in H}, {h: 100 for h in H})   # hep üstte, secim odasında değil: v1.3'te çıkardı
    assert cikis == []
    assert all(r["uygun"] is True for r in gecis.oku(deg))
