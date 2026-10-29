"""Geçiş kaydı (ön kayıt D v1.4, madde 1): oda giriş/çıkışlarının silinmeyen, yalnız eklenen kaydı.

Tek seçim kaynağı ``secim.py``'dir; bu modül seçimin sonucunu (``secim.json``) haftalık okuyup kayda yazar. Dosyalar JSONL ve yalnız
eklemelidir: silme/güncelleme yolu yoktur. Kayıt (``kayit.jsonl``): ``tarih, adres, kol, olay (giris|cikis), neden, secim_surumu, kapi_tarihi``.
Haftalık değerlendirme (``degerlendirme.jsonl``): oda üyesi bu hafta havuz puan sırasının alt ``secim_cikis_havuz_alt_dilim`` dilimine
düştü mü (``uygun`` = düşmedi ya da sıralanamadı). Odadan çıkış için ÜÇÜ BİRDEN gerekir (kurallar.yaml): etiketten (son girişten) bu yana en az
``secim_cikis_min_hafta`` haftalık değerlendirme ve en az ``secim_cikis_min_kapanmis_islem`` kapanmış işlem (veri yoksa değerlendirilemez, çıkış yok);
son ``secim_cikis_ardisik_hafta`` değerlendirmenin hepsi uygunsuz ve birbirini 7 günle izliyor. Araya uygun hafta ya da atlanmış hafta girerse sayaç
sıfırlanır. Seçim odasından düşmek tek başına çıkış sebebi DEĞİLDİR. ITT ölçümü bu kayıttan okunur: çıkan üye çıkış gününe kadar kohorttadır.
"""
from __future__ import annotations

import json
import math
import argparse
import hashlib
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from copytrade.kurallar import load_rules

ALANLAR = ("tarih", "adres", "kol", "olay", "neden", "secim_surumu", "kapi_tarihi")
DEGERLENDIRME_ALANLARI = ("tarih", "adres", "uygun", "secim_surumu", "kapi_tarihi")
OLAYLAR = ("giris", "cikis")
KOLLAR = ("oda", "kontrol", "taban", "elle")
TARIH = re.compile(r"\d{4}-\d{2}-\d{2}")
HAFTA_GUN = 7


def degisim_yaz(path: Path, row: dict[str, Any], rules: dict | None = None) -> None:
    """Ön kayıt 1.6'nın kullanıcı onaylı oda değişimini ayrı JSONL kaydına ekler."""
    rules = rules or load_rules()
    required = {'tarih', 'cikarilan', 'alinan', 'gerekce', 'not'}
    if set(row) != required or not TARIH.fullmatch(str(row['tarih'])):
        raise ValueError('değişim satırı tarih, cikarilan, alinan, gerekce, not alanlarını taşımalı')
    for key in ('cikarilan', 'alinan'):
        if not re.fullmatch(r'0x[0-9a-fA-F]{40}', str(row[key])):
            raise ValueError(f'{key} geçerli halka açık adres olmalı')
    if row['cikarilan'].lower() == row['alinan'].lower():
        raise ValueError('çıkarılan ve alınan adres aynı olamaz')
    if row['gerekce'] not in rules['degisim_gerekce_kodlari']:
        raise ValueError('gerekçe ön kayıt gerekçe kodlarından biri olmalı')
    today = date.fromisoformat(str(row['tarih']))
    counted = [r for r in oku(path) if r.get('gerekce') not in rules['degisim_tavan_disi']
               and 0 <= (today - date.fromisoformat(r['tarih'])).days < int(rules['degisim_tavan_gun'])]
    if row['gerekce'] not in rules['degisim_tavan_disi'] and len(counted) >= int(rules['degisim_tavan_adet']):
        raise ValueError('oda değişim tavanına ulaşıldı')
    if any(r.get('tarih') == row['tarih'] and str(r.get('cikarilan', '')).lower() == row['cikarilan'].lower() for r in oku(path)):
        raise ValueError('bu çıkarılan için aynı gün değişim kaydı zaten var')
    _ekle(path, row)


def degisim_uygula(liste_yolu: Path, kayit_yolu: Path, cikarilan: str, alinan: str, gerekce: str,
                   not_: str = '', tarih: str | None = None, rules: dict | None = None) -> dict[str, Any]:
    """Kayıt ekler ve izleme listesini oda→çıkarılan / yeni oda olarak günceller."""
    import yaml
    rules = rules or load_rules()
    tarih = tarih or datetime.now(timezone.utc).date().isoformat()
    row = {'tarih': tarih, 'cikarilan': cikarilan.lower(), 'alinan': alinan.lower(), 'gerekce': gerekce, 'not': not_}
    data = yaml.safe_load(liste_yolu.read_text(encoding='utf-8'))
    rows = data['traderlar'] if isinstance(data, dict) else data
    old = next((r for r in rows if r['adres'].lower() == cikarilan.lower()), None)
    if old is None or old.get('kol') != 'oda':
        raise ValueError('çıkarılan adres etkin oda üyesi olmalı')
    if any(r['adres'].lower() == alinan.lower() for r in rows):
        raise ValueError('alınan adres izleme listesinde zaten var')
    degisim_yaz(kayit_yolu, row, rules)
    # Sabit referans kolu (ön kayıt 1.5 madde 3): ilk seçimin oda üyesi çıkarılsa da referans_oda olarak kalıcı izlenir.
    referans = ['referans_oda'] if old.get('secim') == rules.get('referans_secim') else []
    old['kol'], old['kollar'], old['cikarilma_tarihi'] = 'cikarilan', ['cikarilan'] + referans, tarih
    rows.append({'id': 'O' + hashlib.sha1(alinan.lower().encode()).hexdigest()[:8], 'adres': alinan.lower(),
                 'takma_ad': alinan[2:6].lower(), 'durum': 'izlemede', 't0': tarih, 'kol': 'oda', 'kollar': ['oda']})
    liste_yolu.write_text(yaml.safe_dump({'traderlar': rows}, allow_unicode=True, sort_keys=False), encoding='utf-8')
    return row


def temizle_cikarilan(liste_yolu: Path, today: str, rules: dict | None = None) -> int:
    """İzleme süresi dolan çıkarılanı listeden siler; değişim kaydı korunur."""
    import yaml
    rules = rules or load_rules()
    data = yaml.safe_load(liste_yolu.read_text(encoding='utf-8'))
    rows = data['traderlar'] if isinstance(data, dict) else data
    cut = date.fromisoformat(today)
    kept = [r for r in rows if not (r.get('kol') == 'cikarilan' and r.get('cikarilma_tarihi') and 'referans_oda' not in (r.get('kollar') or []) and
                                    (cut - date.fromisoformat(str(r['cikarilma_tarihi']))).days >= int(rules['cikarilan_izleme_gun']))]
    if len(kept) != len(rows):
        liste_yolu.write_text(yaml.safe_dump({'traderlar': kept}, allow_unicode=True, sort_keys=False), encoding='utf-8')
    return len(rows) - len(kept)


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


def alt_dilimde(adres: str, puanlar: dict[str, float | None], oran: float) -> bool | None:
    """Adres, puanı olan havuz üyeleri arasında puan sırasının alt ``oran`` diliminde mi? Sıra: puan ↓, eşitlikte adres (seçimle aynı).
    Alt dilim büyüklüğü = ceil(n × oran). Havuzda yok ya da puansız: ``None`` (sıralanamaz; çıkış gerekçesi olmaz)."""
    scored = sorted(((a.lower(), p) for a, p in puanlar.items() if p is not None), key=lambda x: (-x[1], x[0]))
    names = [a for a, _ in scored]
    if adres.lower() not in names:
        return None
    bottom = math.ceil(round(len(names) * oran, 9))
    return names.index(adres.lower()) >= len(names) - bottom


def son_giris(kayit: list[dict[str, Any]], adres: str) -> str | None:
    """Adresin son oda girişi (etiket günü); yoksa ``None``."""
    days = [r["tarih"] for r in kayit if r["kol"] == "oda" and r["olay"] == "giris" and str(r["adres"]).lower() == adres.lower()]
    return max(days) if days else None


def cikis_gerekcesi(kayit: list[dict[str, Any]], degerlendirme: Path, adres: str, kapanmis: int | None, rules: dict) -> str | None:
    """v1.4 çıkış kuralı: üç koşul birlikte sağlanıyorsa gerekçe metni, aksi hâlde ``None``."""
    giris = son_giris(kayit, adres)
    if giris is None or kapanmis is None:
        return None
    since = [r for r in oku(degerlendirme) if str(r["adres"]).lower() == adres.lower() and r["tarih"] > giris]
    weeks, trades, ardisik = int(rules["secim_cikis_min_hafta"]), int(rules["secim_cikis_min_kapanmis_islem"]), int(rules["secim_cikis_ardisik_hafta"])
    if len(since) < weeks or kapanmis < trades or not cikmali_kayitlardan(since, ardisik):
        return None
    return (f"{len(since)} haftalık değerlendirme, {kapanmis} kapanmış işlem; havuz alt %{rules['secim_cikis_havuz_alt_dilim'] * 100:g} dilimi "
            f"{ardisik} ardışık hafta")


def cikmali_kayitlardan(rows: list[dict[str, Any]], ardisik: int) -> bool:
    last = sorted(rows, key=lambda r: r["tarih"])[-ardisik:]
    if len(last) < ardisik:
        return False
    days = [date.fromisoformat(r["tarih"]) for r in last]
    return all(not r["uygun"] for r in last) and all((b - a).days == HAFTA_GUN for a, b in zip(days, days[1:]))


def haftalik(kayit_yolu: Path, degerlendirme_yolu: Path, result: dict[str, Any], tarih: str, rules: dict | None = None,
             kapanmis_islem: dict[str, int | None] | None = None) -> list[dict[str, Any]]:
    """Haftalık geçiş: ``result`` = ``secim.json``. Seçimin odasında olup üye olmayanlar girer; üyelerin bu haftaki uygunluğu (havuz alt dilimine
    düşmedi mi) yazılır; v1.4 çıkış koşullarının üçü birden sağlayanlar çıkar. ``kapanmis_islem``: {adres: etiketten bu yana kapanmış işlem};
    verilmeyen ya da ``None`` adres için çıkış değerlendirilemez. Aynı hafta yeniden koşarsa yeni olay üretmez. Yazılan olayları döner."""
    rules = rules or load_rules()
    surum, kapi = result["secim_surumu"], result["kapi_tarihi"]
    secim_odasi = {str(a).lower() for a, e in result["adresler"].items() if "oda" in e["kollar"]}
    puanlar = {str(a).lower(): e.get("puan") for a, e in result["adresler"].items() if "havuz" in e["kollar"]}
    sayim = {str(a).lower(): v for a, v in (kapanmis_islem or {}).items()}
    written: list[dict[str, Any]] = []
    members = oda_uyeleri(oku(kayit_yolu))
    done_today = {str(r["adres"]).lower() for r in oku(degerlendirme_yolu) if r["tarih"] == tarih}
    for address in sorted(members):
        if address not in done_today:
            alt = alt_dilimde(address, puanlar, float(rules["secim_cikis_havuz_alt_dilim"]))
            degerlendirme_yaz(degerlendirme_yolu, {"tarih": tarih, "adres": address, "uygun": alt is not True, "secim_surumu": surum, "kapi_tarihi": kapi})
    for address in sorted(members):
        neden = cikis_gerekcesi(oku(kayit_yolu), degerlendirme_yolu, address, sayim.get(address), rules)
        if neden:
            row = {"tarih": tarih, "adres": address, "kol": "oda", "olay": "cikis", "neden": neden, "secim_surumu": surum, "kapi_tarihi": kapi}
            if not any(r["tarih"] == tarih and r["adres"] == address and r["olay"] == "cikis" for r in oku(kayit_yolu)):
                yaz(kayit_yolu, row)
                written.append(row)
    for address in sorted(secim_odasi - members):
        row = {"tarih": tarih, "adres": address, "kol": "oda", "olay": "giris", "neden": f"seçim {surum} odası", "secim_surumu": surum, "kapi_tarihi": kapi}
        if not any(r["tarih"] == tarih and r["adres"] == address and r["olay"] == "giris" for r in oku(kayit_yolu)):
            yaz(kayit_yolu, row)
            written.append(row)
    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Kullanıcı onaylı oda değişimini kaydeder.')
    parser.add_argument('--cikar', required=True)
    parser.add_argument('--al', required=True)
    parser.add_argument('--gerekce', required=True)
    parser.add_argument('--not', default='', dest='not_')
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--tarih', default=None, help='test/düzeltme için YYYY-MM-DD; normalde bugünün UTC tarihi')
    args = parser.parse_args(argv)
    row = degisim_uygula(args.root / 'copytrade/izleme_listesi.yaml', args.root / 'copytrade/degisim.jsonl',
                         args.cikar, args.al, args.gerekce, args.not_, args.tarih)
    print(f"Oda değişimi kaydedildi: {row['cikarilan']} → {row['alinan']} ({row['gerekce']})")


if __name__ == '__main__':
    main()
