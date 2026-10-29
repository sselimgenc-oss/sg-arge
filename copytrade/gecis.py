"""Geçiş kaydı (ön kayıt D v1.3, madde 3): oda giriş/çıkışlarının silinmeyen, yalnız eklenen kaydı.

Tek seçim kaynağı ``secim.py``'dir; bu modül seçimin sonucunu (``secim.json``) haftalık okuyup kayda yazar. Dosyalar JSONL ve yalnız
eklemelidir: silme/güncelleme yolu yoktur. Kayıt (``kayit.jsonl``): ``tarih, adres, kol, olay (giris|cikis), neden, secim_surumu, kapi_tarihi``.
Haftalık değerlendirme (``degerlendirme.jsonl``): oda üyesi bu haftaki seçimin odasında mı (``uygun``). Odadan çıkış için
``secim_cikis_ardisik_hafta`` (kurallar.yaml, 2) ardışık haftalık değerlendirmenin hepsi uygunsuz olmalıdır; araya uygun hafta ya da
atlanmış hafta girerse sayaç sıfırlanır. ITT ölçümü bu kayıttan okunur: çıkan üye çıkış gününe kadar kohorttadır.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from copytrade.kurallar import load_rules

ALANLAR = ("tarih", "adres", "kol", "olay", "neden", "secim_surumu", "kapi_tarihi")
DEGERLENDIRME_ALANLARI = ("tarih", "adres", "uygun", "secim_surumu", "kapi_tarihi")
OLAYLAR = ("giris", "cikis")
KOLLAR = ("oda", "kontrol", "taban", "elle")
TARIH = re.compile(r"\d{4}-\d{2}-\d{2}")
HAFTA_GUN = 7


def _denetle(row: dict[str, Any], alanlar: tuple[str, ...]) -> None:
    if set(row) != set(alanlar):
        raise ValueError(f"geçiş satırı tam olarak şu alanları taşımalı: {', '.join(alanlar)}")
    if not TARIH.fullmatch(str(row["tarih"])):
        raise ValueError("tarih YYYY-MM-DD olmalı")
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", str(row["adres"])):
        raise ValueError("adres 0x + 40 onaltılık hane olmalı")


def _ekle(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def oku(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def yaz(path: Path, row: dict[str, Any]) -> None:
    """Geçiş olayı ekler. Aynı (tarih, adres, kol, olay) ikinci kez yazılmaz; geçersiz satır dosyaya hiçbir şey yazmaz."""
    _denetle(row, ALANLAR)
    if row["olay"] not in OLAYLAR or row["kol"] not in KOLLAR:
        raise ValueError(f"olay {OLAYLAR}, kol {KOLLAR} içinden olmalı")
    if not str(row["neden"]).strip():
        raise ValueError("neden boş olamaz")
    key = (row["tarih"], str(row["adres"]).lower(), row["kol"], row["olay"])
    if any((r["tarih"], str(r["adres"]).lower(), r["kol"], r["olay"]) == key for r in oku(path)):
        raise ValueError(f"bu geçiş kaydı zaten var: {key}")
    _ekle(path, row)


def degerlendirme_yaz(path: Path, row: dict[str, Any]) -> None:
    _denetle(row, DEGERLENDIRME_ALANLARI)
    if not isinstance(row["uygun"], bool):
        raise ValueError("uygun true/false olmalı")
    if any(r["tarih"] == row["tarih"] and str(r["adres"]).lower() == str(row["adres"]).lower() for r in oku(path)):
        raise ValueError("bu hafta için değerlendirme zaten var")
    _ekle(path, row)


def cikmali(path: Path, adres: str, ardisik: int) -> bool:
    """Adresin son ``ardisik`` haftalık değerlendirmesi birbirini 7 günle izliyor ve hepsi uygunsuzsa ``True``."""
    rows = sorted((r for r in oku(path) if str(r["adres"]).lower() == adres.lower()), key=lambda r: r["tarih"])
    if len(rows) < ardisik:
        return False
    last = rows[-ardisik:]
    days = [date.fromisoformat(r["tarih"]) for r in last]
    return all(not r["uygun"] for r in last) and all((b - a).days == HAFTA_GUN for a, b in zip(days, days[1:]))


def oda_uyeleri(kayit: list[dict[str, Any]]) -> set[str]:
    """Kayıttan şu anki oda üyeleri (giris sonrası cikis olmayanlar)."""
    members: set[str] = set()
    for row in sorted(kayit, key=lambda r: r["tarih"]):
        if row["kol"] != "oda":
            continue
        (members.add if row["olay"] == "giris" else members.discard)(str(row["adres"]).lower())
    return members


def haftalik(kayit_yolu: Path, degerlendirme_yolu: Path, result: dict[str, Any], tarih: str, rules: dict | None = None) -> list[dict[str, Any]]:
    """Haftalık geçiş: ``result`` = ``secim.json``. Seçimin odasında olup üye olmayanlar girer; üyelerin bu haftaki uygunluğu yazılır;
    ardışık uygunsuz hafta sayısı kurala varanlar çıkar. Aynı hafta yeniden koşarsa yeni olay üretmez. Yazılan olayları döner."""
    rules = rules or load_rules()
    ardisik = int(rules["secim_cikis_ardisik_hafta"])
    surum, kapi = result["secim_surumu"], result["kapi_tarihi"]
    secim_odasi = {str(a).lower() for a, e in result["adresler"].items() if "oda" in e["kollar"]}
    written: list[dict[str, Any]] = []
    members = oda_uyeleri(oku(kayit_yolu))
    done_today = {str(r["adres"]).lower() for r in oku(degerlendirme_yolu) if r["tarih"] == tarih}
    for address in sorted(members):
        if address not in done_today:
            degerlendirme_yaz(degerlendirme_yolu, {"tarih": tarih, "adres": address, "uygun": address in secim_odasi, "secim_surumu": surum, "kapi_tarihi": kapi})
    for address in sorted(members):
        if cikmali(degerlendirme_yolu, address, ardisik) and address not in secim_odasi:
            row = {"tarih": tarih, "adres": address, "kol": "oda", "olay": "cikis", "neden": f"{ardisik} ardışık haftalık değerlendirmede odada değil",
                   "secim_surumu": surum, "kapi_tarihi": kapi}
            if not any(r["tarih"] == tarih and r["adres"] == address and r["olay"] == "cikis" for r in oku(kayit_yolu)):
                yaz(kayit_yolu, row)
                written.append(row)
    for address in sorted(secim_odasi - members):
        row = {"tarih": tarih, "adres": address, "kol": "oda", "olay": "giris", "neden": f"seçim {surum} odası", "secim_surumu": surum, "kapi_tarihi": kapi}
        if not any(r["tarih"] == tarih and r["adres"] == address and r["olay"] == "giris" for r in oku(kayit_yolu)):
            yaz(kayit_yolu, row)
            written.append(row)
    return written
