"""Seçim v1.3 (``docs/GOREV_SECIM_V13.md``, ön kayıt D sürüm 1.3): kapı sonucundan havuz, aday, oda, kontrol, taban ve elle liste.

Eşik yok: tüm sayılar ``kurallar.yaml``'daki ``secim_*`` anahtarlarından gelir. Yalnız herkese açık veri; emir yok.
Çıktı (veri dalına): ``secim/<tarih>-<sürüm>/secim.json`` ve ``RAPOR.md``; kırmızı bayraklar ayrı iş: ``--bayrak`` → ``bayrak.json``.
Yayımlanan sürümün (aynı ``secim_surumu`` + kapı tarihi) üzerine yazılmaz. İzleme listesi ``--izleme-listesi`` ile ``secim.json``'dan üretilir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from copytrade.kurallar import load_rules

TARZLAR = ("intraday", "swing")
KOLLAR = ("oda", "elle", "taban", "kontrol", "aday", "havuz")     # ``kol`` = bu sıradaki ilk (bildirim yalnız ``oda``)
LISTE_KOLLARI = ("oda", "elle", "taban", "kontrol")
ONEK = {"oda": "O", "kontrol": "K", "taban": "B", "elle": "E"}


def _num(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _flag(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "1.0"}


KURALLAR_YOLU = Path(__file__).with_name("kurallar.yaml")


def _sha256_dosya(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statik_gecer(row: dict[str, Any], rules: dict) -> bool:
    """Adım 3'ün statik koşulları (``kapi.py`` ile aynı sütunlar ve eksik-veri kuralı): kısa işlem payı yoksa geçer, kaldıraç yoksa kalır."""
    short, median, top = _num(row.get("kisa_islem_payi")), _num(row.get("median_leverage")), _num(row.get("max_leverage"))
    return ((short is None or short <= float(rules["kisa_islem_payi_max"]))
            and median is not None and median <= float(rules["kapi_max_medyan_kaldirac"])
            and top is not None and top <= float(rules["kapi_max_kaldirac"]))


def puan(row: dict[str, Any]) -> float | None:
    """Tarzın kapı gecikmesindeki maliyet sonrası net kopya getirisi; yoksa ``None`` (puansız)."""
    delay = _num(row.get("kapi_gecikme_dk"))
    return None if delay is None else _num(row.get(f"gecikme_{int(delay)}dk_net"))


def havuz(table: pd.DataFrame, rules: dict | None = None) -> list[dict[str, Any]]:
    """Adım 1 ve 2 Geçti, tarz intraday/swing, adım 3 statik koşulları sağlayan satırlar; ``puan`` eklenmiş, adrese göre sıralı."""
    rules = rules or load_rules()
    rows = []
    for row in table.to_dict("records"):
        if (row.get("adim1") == "Geçti" and row.get("adim2") == "Geçti" and row.get("tarz") in TARZLAR
                and statik_gecer(row, rules)):
            rows.append({**row, "address": str(row["address"]).lower(), "puan": puan(row)})
    return sorted(rows, key=lambda r: r["address"])


def adaylar(pool: list[dict[str, Any]], rules: dict) -> list[dict[str, Any]]:
    """Her tarz kendi içinde: puanı > 0 olanlardan en iyi ``secim_aday_orani`` (yukarı yuvarla). Sıra 1 = en iyi."""
    out = []
    for tarz in TARZLAR:
        positive = sorted((r for r in pool if r["tarz"] == tarz and r["puan"] is not None and r["puan"] > 0),
                          key=lambda r: (-r["puan"], r["address"]))
        keep = math.ceil(round(len(positive) * float(rules["secim_aday_orani"]), 9))
        out += [{**r, "sira": i + 1} for i, r in enumerate(positive[:keep])]
    return out


def _oda_sirasi(row: dict[str, Any]) -> tuple:
    return (_flag(row.get("genc_aday")), -row["puan"], row["address"])      # önce ≥ 365 gün (genc_aday olmayan), sonra puan


def iliski_ele(candidates: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Aday katındaki bağlı adresler tek grup sayılır; puanı en yüksek kalır, diğerleri ``not``'a yazılır."""
    by_address = {r["address"]: r for r in candidates}
    parent = {a: a for a in by_address}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for address, row in by_address.items():
        for other in str(row.get("iliskili_adresler") or "").replace(",", ";").split(";"):
            other = other.strip().lower()
            if other in by_address and other != address:
                parent[find(address)] = find(other)
    groups: dict[str, list[dict[str, Any]]] = {}
    for address, row in by_address.items():
        groups.setdefault(find(address), []).append(row)
    kept, notes = [], {}
    for members in groups.values():
        best = min(members, key=lambda r: (-r["puan"], r["address"]))
        kept.append(best)
        for row in members:
            if row is not best:
                notes[row["address"]] = f"ilişkili hesap: {best['address'][:6]} puanı daha yüksek, o kalır"
    return kept, notes


def _kotalar(counts: dict[str, int], target: int) -> dict[str, int]:
    """Tarz payıyla orantılı kota; en büyük kalan yöntemi (eşitlikte tarz adı sırası). Toplam = target."""
    total = sum(counts.values())
    if not total:
        return {t: 0 for t in counts}
    exact = {t: target * c / total for t, c in counts.items()}
    quota = {t: math.floor(round(v, 9)) for t, v in exact.items()}
    for t in sorted(counts, key=lambda t: (-(exact[t] - quota[t]), t))[:target - sum(quota.values())]:
        quota[t] += 1
    return quota


def oda_sec(candidates: list[dict[str, Any]], rules: dict) -> dict[str, Any]:
    """Odayı kurar. Boyut = min(secim_oda_max, ilişki elemesinden sonra kalan aday); < secim_oda_min ise ``kisa`` (RAPOR'da yazılır)."""
    eligible, notes = iliski_ele(candidates)
    target = min(int(rules["secim_oda_max"]), len(eligible))
    counts = {t: sum(r["tarz"] == t for r in candidates) for t in TARZLAR}       # kota: ilişki elemesinden önceki aday katı payı
    quota = _kotalar(counts, target)
    chosen: list[dict[str, Any]] = []
    for tarz in TARZLAR:
        chosen += sorted((r for r in eligible if r["tarz"] == tarz), key=_oda_sirasi)[:quota[tarz]]
    if len(chosen) < target:                      # bir tarzda yeterli aday yoksa eksik, kalan adaylardan aynı sırayla tamamlanır
        taken = {r["address"] for r in chosen}
        chosen += sorted((r for r in eligible if r["address"] not in taken), key=_oda_sirasi)[:target - len(chosen)]
    chosen.sort(key=_oda_sirasi)
    return {"oda": chosen, "notlar": notes, "kota": quota, "kisa": len(chosen) < int(rules["secim_oda_min"]),
            "hedef_ilk": int(rules["secim_oda_max"])}


def tohum_dizgesi(surum: str, kapi_tarihi: str) -> str:
    return f"secim-{surum}-{kapi_tarihi}"


def tohum(surum: str, kapi_tarihi: str) -> int:
    """``secim-<sürüm>-<kapı tarihi>`` dizgesinin SHA-256'sının ilk 8 baytı (bilgi amaçlı; sıralama adres başına sha256 kullanır)."""
    return int.from_bytes(hashlib.sha256(tohum_dizgesi(surum, kapi_tarihi).encode()).digest()[:8], "big")


def dilim_esigi(pool: list[dict[str, Any]]) -> float | None:
    """Havuzun en yüksek kaldıraç medyanı (dilim sınırı); kaldıraç bilgisi olmayan havuzda ``None``."""
    values = [v for v in (_num(r.get("max_leverage")) for r in pool) if v is not None]
    return statistics.median(values) if values else None


def dilim(row: dict[str, Any], esik: float | None) -> tuple[str, str]:
    """Tarz × en yüksek kaldıraç (medyanın altı/eşiti = ``alt``, üstü = ``ust``)."""
    top = _num(row.get("max_leverage"))
    return row["tarz"], "alt" if esik is None or top is None or top <= esik else "ust"


def kontrol_sec(pool: list[dict[str, Any]], oda: list[str], kapi_tarihi: str, surum: str) -> dict[str, Any]:
    """Odayla ayrık, dilim-eşleştirilmiş kontrol (puana bakmaz). Her oda üyesi (adres sırasıyla) için aynı dilimden, yoksa aynı tarzın
    öbür diliminden, ``sha256(secim-<sürüm>-<kapı tarihi>-<adres>)`` sırasındaki ilk kullanılmamış havuz-oda adresi. ``ikincil`` = havuz − oda."""
    prefix = tohum_dizgesi(surum, kapi_tarihi)
    room = set(oda)
    rest = sorted((r for r in pool if r["address"] not in room), key=lambda r: hashlib.sha256(f"{prefix}-{r['address']}".encode()).hexdigest())
    esik = dilim_esigi(pool)
    by_address = {r["address"]: r for r in pool}
    used: set[str] = set()
    pairs: dict[str, str] = {}
    unmatched: list[str] = []
    for address in sorted(room):
        want = dilim(by_address[address], esik)
        for same in (True, False):
            pick = next((r for r in rest if r["address"] not in used and r["tarz"] == want[0] and (dilim(r, esik) == want) == same), None)
            if pick:
                used.add(pick["address"])
                pairs[address] = pick["address"]
                break
        else:
            unmatched.append(address)
    return {"kontrol": sorted(pairs.values()), "eslesme": pairs, "eslesmeyen": unmatched, "esik": esik,
            "ikincil": sorted(r["address"] for r in rest)}


def taban_sec(board: list[dict[str, Any]], count: int) -> list[str]:
    """Lider tablosunda 30 günlük PnL'e göre ilk ``count`` adres; ön eleme yok."""
    from copytrade.tarama import _address, _window
    rows = [(_address(r).lower(), _window(r, "month", "pnl")) for r in board if _address(r)]
    return [a for a, _ in sorted(rows, key=lambda x: (-x[1], x[0]))[:count]]


def elle_liste(path: Path) -> list[str]:
    """Bugünkü ``izleme_listesi.yaml``: ``kol`` yoksa ya da ``elle`` ise elle liste."""
    if not path.exists():
        return []
    rows = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = rows["traderlar"] if isinstance(rows, dict) else rows
    return [str(r["adres"]).lower() for r in rows or [] if r.get("kol", "elle") == "elle"]


def sec(table: pd.DataFrame, date: str, board: list[dict[str, Any]] | None, manual: list[str], rules: dict | None = None,
        bayrak_fn=None, kapi_tarihi: str | None = None) -> dict[str, Any]:
    """``bayrak_fn(adres, hesap_degeri) -> {bayrak_*: …}``: yalnız aday katı için çağrılır; bilgi sütunudur, seçimi değiştirmez.
    Komut satırı bayrakları seçimde değil ayrı işte hesaplar (``bayrak_hesapla``); ``kapi_tarihi`` yoksa ``date``."""
    rules = rules or load_rules()
    kapi_tarihi = kapi_tarihi or date
    surum = str(rules["secim_surumu"])
    pool = havuz(table, rules)
    candidates = [r for r in adaylar(pool, rules)]
    room = oda_sec(candidates, rules)
    oda = room["oda"]
    kontrol_sonuc = kontrol_sec(pool, [r["address"] for r in oda], kapi_tarihi, surum)
    control = [r for r in pool if r["address"] in set(kontrol_sonuc["kontrol"])]
    esik = kontrol_sonuc["esik"]
    slices = {r["address"]: dilim(r, esik) for r in pool}
    base = taban_sec(board, len(oda)) if board is not None else []
    by_address = {r["address"]: r for r in table.assign(address=table["address"].str.lower()).to_dict("records")}
    kollar: dict[str, set[str]] = {r["address"]: {"havuz"} for r in pool}
    for r in candidates:
        kollar[r["address"]].add("aday")
    sira = {r["address"]: r.get("sira") for r in candidates}
    for name, addresses in (("oda", [r["address"] for r in oda]), ("kontrol", [r["address"] for r in control]), ("taban", base), ("elle", manual)):
        for address in addresses:
            kollar.setdefault(address, set()).add(name)
    puan_of = {r["address"]: r["puan"] for r in pool}
    entries = {}
    for address, names in sorted(kollar.items()):
        row = by_address.get(address, {})
        entries[address] = {
            "kol": next(k for k in KOLLAR if k in names), "kollar": [k for k in KOLLAR if k in names],
            "tarz": row.get("tarz") if isinstance(row.get("tarz"), str) else None,
            "puan": puan_of.get(address), "sira": sira.get(address),
            "dilim": "/".join(slices[address]) if address in slices else None,
            "esli_oda": next((o for o, k in kontrol_sonuc["eslesme"].items() if k == address), None),
            "genc_aday": _flag(row.get("genc_aday")) if row else None,
            "medyan_kaldirac": _num(row.get("median_leverage")), "en_yuksek_kaldirac": _num(row.get("max_leverage")),
            "acik_pozisyon_sayisi": _num(row.get("acik_pozisyon_sayisi")),
            "unrealized_end": _num(row.get("unrealized_end")), "mark_missing": _num(row.get("mark_missing")),
            "acik_pozisyon_notional": _num(row.get("acik_pozisyon_notional")),
            "en_iyi_islem_haric_getiri": _num(row.get("en_iyi_islem_haric_getiri")),
            "medyan_tutma_saat": _num(row.get("median_holding_hours")),
            "gunluk_islem_sikligi": _num(row.get("gunluk_islem_sikligi")),
            "yonlu_dolum_sayisi": _num(row.get("yonlu_dolum_sayisi")),
            "yonlu_dolum_iyi_orani": _num(row.get("yonlu_dolum_iyi_orani")),
            "yonlu_dolum_kotu_orani": _num(row.get("yonlu_dolum_kotu_orani")),
            "yonlu_dolum_ortalama_bp": _num(row.get("yonlu_dolum_ortalama_bp")),
            "gecmis_gun": _num(row.get("gecmis_gun")), "hesap_degeri": _num(row.get("hesap_degeri_bugun")) or _num(row.get("account_value")),
            "iliskili_not": room["notlar"].get(address) or (str(row.get("iliskili_not")) if str(row.get("iliskili_not", "nan")) not in ("", "nan") else ""),
            "hesap_surumu": row.get("hesap") if isinstance(row.get("hesap"), str) else None}
        if address in sira and bayrak_fn is not None:
            value = _num(row.get("hesap_degeri_bugun")) or _num(row.get("account_value")) or 0.0
            started = time.monotonic()
            entries[address].update(bayrak_fn(address, value))
            print(f"bayrak {address} {time.monotonic() - started:.0f} sn", flush=True)
    counts = {t: {"havuz": sum(r["tarz"] == t for r in pool), "puansiz": sum(r["tarz"] == t and r["puan"] is None for r in pool),
                  "aday": sum(r["tarz"] == t for r in candidates), "oda": sum(r["tarz"] == t for r in oda)} for t in TARZLAR}
    dilim_tablosu: dict[str, dict[str, int]] = {}
    for address in [r["address"] for r in oda]:
        dilim_tablosu.setdefault("/".join(slices[address]), {"oda": 0, "kontrol": 0, "havuz": 0})["oda"] += 1
    for address in kontrol_sonuc["kontrol"]:
        dilim_tablosu.setdefault("/".join(slices[address]), {"oda": 0, "kontrol": 0, "havuz": 0})["kontrol"] += 1
    for address in slices:
        dilim_tablosu.setdefault("/".join(slices[address]), {"oda": 0, "kontrol": 0, "havuz": 0})["havuz"] += 1
    return {"surum": 1, "secim_surumu": surum, "tarih": date, "kapi_tarihi": kapi_tarihi,
            "kurallar_sha256": _sha256_dosya(KURALLAR_YOLU), "secim_sha256": _sha256_dosya(Path(__file__)),
            "tohum": tohum(surum, kapi_tarihi), "tohum_dizgesi": tohum_dizgesi(surum, kapi_tarihi),
            "sayilar": {"kapi_satiri": int(len(table)), "havuz": len(pool), "aday": len(candidates), "oda": len(oda),
                        "kontrol": len(control), "ikincil_kontrol": len(kontrol_sonuc["ikincil"]), "taban": len(base), "elle": len(manual), "tarz": counts},
            "oda_kisa": room["kisa"], "oda_kota": room["kota"],
            "kontrol": kontrol_sonuc["kontrol"], "eslesme": kontrol_sonuc["eslesme"], "eslesmeyen": kontrol_sonuc["eslesmeyen"],
            "ikincil_kontrol": kontrol_sonuc["ikincil"], "dilim_esigi": esik, "dilim_tablosu": dict(sorted(dilim_tablosu.items())),
            "adresler": entries}


def _fmt(value: Any, digits: int = 3) -> str:
    return "–" if value is None else f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def ozet_sutunlar(table: pd.DataFrame) -> list[str]:
    lines = ["| sütun | dolu | min | medyan | max |", "|---|---|---|---|---|"]
    for name in table.columns:
        values = pd.to_numeric(table[name], errors="coerce").dropna()
        if len(values) and not table[name].dtype == bool:
            lines.append(f"| {name} | {len(values)} | {values.min():.4g} | {values.median():.4g} | {values.max():.4g} |")
    return lines


BAYRAK_BASLIK = ("adres", "rol", "vault oranı", "funding payı", "alt hesapta ters", "30 gün hacim/hesap", "zararda ekleme", "katlama oranı", "coin HHI",
                 "en büyük coin payı", "ekleme derinliği", "not")


def bayrak_tablosu(items: list[tuple[str, dict[str, Any]]]) -> list[str]:
    """Kırmızı bayrak bilgi tablosu (RAPOR ve BAYRAK.md): satır = (adres, bayrak_* alanları). Eksik/None değerler "–"."""
    lines = ["| " + " | ".join(BAYRAK_BASLIK) + " |", "|" + "---|" * len(BAYRAK_BASLIK)]
    for address, e in items:
        lines.append(f"| `{address}` | {e.get('bayrak_rol') or '–'} | {_fmt(e.get('bayrak_vault_orani'))} | {_fmt(e.get('bayrak_funding_payi'))} | "
                     f"{e.get('bayrak_alt_hesap_ters', '–')} | {_fmt(e.get('bayrak_hacim_orani'), 2)} | {_fmt(e.get('bayrak_zararda_ekleme'))} | "
                     f"{_fmt(e.get('bayrak_katlama_orani'))} | {_fmt(e.get('bayrak_coin_hhi'))} | {_fmt(e.get('bayrak_en_buyuk_coin_payi'))} | "
                     f"{_fmt(e.get('bayrak_ekleme_derinligi'))} | {e.get('bayrak_not') or ''} |")
    return lines


def bayrak_raporu(result: dict[str, Any], body: dict[str, Any]) -> str:
    """``BAYRAK.md``: bayrak.json'daki aday katı bilgi tablosu (oda üyeleri önce). Bilgidir, kimseyi elemez; puan ve getiri yoktur."""
    room = [a for a, e in sorted(result["adresler"].items()) if "oda" in e["kollar"]]
    candidates = [a for a in sorted(body["bayraklar"]) if a not in room]
    items = [(a, body["bayraklar"][a]) for a in room + candidates if a in body["bayraklar"]]
    head = [f"# Kırmızı bayraklar — seçim {body['secim_surumu']} (kapı {body['kapi_tarihi']})", "",
            f"Bilgi sütunlarıdır, kimseyi elemez. Katlama oranı: kat ≥ `bayrak_kat_esik` olan zararda eklemelerin payı. Hesaplama {'tamam' if body.get('tamam') else 'KISMİ (zaman aşımı/hata)'}; "
            f"oda üyeleri önce ({len(room)}), sonra diğer adaylar.", ""]
    return "\n".join(head + bayrak_tablosu(items)) + "\n"


def rapor(result: dict[str, Any], table: pd.DataFrame, durum: dict[str, Any]) -> str:
    n = result["sayilar"]
    lines = [f"# Seçim {result['secim_surumu']} — {result['tarih']} (kapı tarihi {result['kapi_tarihi']})", "",
             "- **Seçim = geçmiş getiri sıralaması (adım 1–3 süzgeçli).** Havuz: adım 1+2 Geçti, tarz intraday/swing, adım 3 statik koşulları "
             "(kısa işlem payı, medyan ve en yüksek kaldıraç). Bu sıralamanın ileriyi taşıyıp taşımadığı pilotun sorusudur; kanıt sayılmaz.",
             f"- Kimlik: kurallar `{result['kurallar_sha256'][:12]}` · secim.py `{result['secim_sha256'][:12]}` · tohum `{result['tohum_dizgesi']}`.",
             f"- Girdi: kapı satırı {n['kapi_satiri']}, hesap sürümü {durum.get('hesap')}, kapsam {durum.get('kapsam')}, durum `{durum.get('durum')}`.",
             f"- Havuz {n['havuz']} · aday {n['aday']} · oda {n['oda']} · kontrol {n['kontrol']} (ikincil kontrol {n['ikincil_kontrol']}) · taban {n['taban']} · elle {n['elle']}.", ""]
    if result["oda_kisa"]:
        lines += [f"> **Uyarı:** oda {n['oda']} adres; en az 10 hedefiydi, aday katı yetersiz. Oda = ilişki elemesinden sonra tüm aday.", ""]
    lines += ["## Kat sayıları (tarz kırılımlı)", "", "| tarz | havuz | puansız | aday | oda |", "|---|---|---|---|---|"]
    lines += [f"| {t} | {c['havuz']} | {c['puansiz']} | {c['aday']} | {c['oda']} |" for t, c in n["tarz"].items()]
    lines += ["", "## Oda", "", "| # | adres | takma ad | tarz | puan | medyan kaldıraç | en yüksek kaldıraç | geçmiş gün | neden seçildi |", "|---|---|---|---|---|---|---|---|---|"]
    room = sorted((a, e) for a, e in result["adresler"].items() if "oda" in e["kollar"])
    room.sort(key=lambda x: (x[1]["genc_aday"], -x[1]["puan"], x[0]))
    for i, (address, e) in enumerate(room, 1):
        why = f"{e['tarz']} aday sırası {e['sira']}" + (" (genç aday, 365 günden az)" if e["genc_aday"] else "")
        lines.append(f"| {i} | `{address}` | {address[2:6]} | {e['tarz']} | {_fmt(e['puan'], 4)} | {_fmt(e['medyan_kaldirac'], 2)} | "
                     f"{_fmt(e['en_yuksek_kaldirac'], 2)} | {_fmt(e['gecmis_gun'], 0)} | {why} |")
    flagged = [(a, e) for a, e in room if "bayrak_rol" in e]
    if flagged:
        lines += ["", "## Kırmızı bayraklar (bilgi; kimseyi elemez — oda üyeleri)", ""] + bayrak_tablosu([(a, e) for a, e in flagged])
    dropped = [(a, e["iliskili_not"]) for a, e in sorted(result["adresler"].items()) if e["iliskili_not"].startswith("ilişkili hesap")]
    if dropped:
        lines += ["", "## İlişkili hesap nedeniyle odaya girmeyenler", ""] + [f"- `{a}`: {note}" for a, note in dropped]
    lines += ["", "## Oda ↔ kontrol dilim dağılımı", "",
              f"Dilim = tarz × en yüksek kaldıraç (havuz medyanı {_fmt(result['dilim_esigi'], 2)}; alt = medyan ve altı). Kontrol odayla ayrıktır.", "",
              "| dilim | havuz | oda | kontrol |", "|---|---|---|---|"]
    lines += [f"| {d} | {c['havuz']} | {c['oda']} | {c['kontrol']} |" for d, c in result["dilim_tablosu"].items()]
    if result["eslesmeyen"]:
        lines += ["", f"Eşi bulunamayan oda üyeleri: {', '.join('`' + a + '`' for a in result['eslesmeyen'])}."]
    lines += ["", "## Kontrol", "", f"Sıra: `sha256({result['tohum_dizgesi']}-<adres>)`; her oda üyesine aynı dilimden bir kontrol. Eşleşmeler (oda → kontrol):", ""]
    lines += [f"- `{o}` → `{k}`" for o, k in sorted(result["eslesme"].items())]
    lines += ["", "## Kapı tablosu sütun özeti (min/medyan/max)", ""] + ozet_sutunlar(table)
    return "\n".join(lines) + "\n"


def bayrak_surumu() -> str:
    """Bayrak hesabının kod kimliği (``bayrak.py`` sha256'sı): kod değişince önbellek geçersiz olur."""
    return _sha256_dosya(Path(__file__).with_name("bayrak.py"))


def bayrak_hesapla(result: dict[str, Any], bayrak_fn, onbellek: dict[str, Any] | None = None, kaydet=None) -> dict[str, Any]:
    """Aday katı (``aday`` kolundaki adresler) için kırmızı bayraklar; ``bayrak.json`` gövdesi. Seçimi değiştirmez, ``secim.json``'a dokunmaz.

    ``onbellek``: önceki (kısmi olabilir) ``bayrak.json`` gövdesi; ``bayrak_surumu`` (kod hash'i), ``secim_surumu`` ve ``kapi_tarihi`` aynıysa o adresin
    sonucu yeniden hesaplanmaz (E6: yeniden koşu tüm ağ çağrılarını tekrarlamaz). ``kaydet(gövde)``: her yeni adresten sonra (``tamam: False``) ve
    sonda (``tamam: True``) çağrılır; zaman aşımı/hata kısmi sonucu korur."""
    body: dict[str, Any] = {"secim_surumu": result["secim_surumu"], "kapi_tarihi": result["kapi_tarihi"], "bayrak_surumu": bayrak_surumu(),
                            "tamam": False, "bayraklar": {}}
    reusable = {}
    if onbellek and all(onbellek.get(k) == body[k] for k in ("secim_surumu", "kapi_tarihi", "bayrak_surumu")):
        reusable = dict(onbellek.get("bayraklar", {}))
    for address, e in sorted(result["adresler"].items()):
        if "aday" not in e["kollar"]:
            continue
        if address in reusable:
            body["bayraklar"][address] = reusable[address]
            continue
        started = time.monotonic()
        body["bayraklar"][address] = bayrak_fn(address, e["hesap_degeri"] or 0.0)
        print(f"bayrak {address} {time.monotonic() - started:.0f} sn", flush=True)
        if kaydet:
            kaydet(body)
    body["tamam"] = True
    if kaydet:
        kaydet(body)
    return body


def izleme_listesi(result: dict[str, Any], existing: list[dict[str, Any]], t0: str) -> list[dict[str, Any]]:
    """``secim.json``'dan izleme listesi: oda + kontrol + taban + elle.

    Seçim kolundaki (oda/kontrol/taban) bir adres listede zaten varsa ve satırı bu seçim sürümünün etiketini (``secim`` =
    ``<secim_surumu>@<kapı tarihi>``) taşımıyorsa **yeni id ve yeni t0** alır: eski t0'dan yeniden oynatma olmaz, ITT ölçümü sürümün
    etiket gününden başlar (E5). Eski id yeniden kullanılmaz (motor arşivi aynı id'de adres/t0 değişimini reddeder). Etiketi aynıysa satır
    değişmez (aynı seçimi yeniden yazmak idempotent). ``elle`` satırlar ve seçimde çıkmayan satırlar olduğu gibi korunur."""
    label = f"{result.get('secim_surumu', 'v1')}@{result.get('kapi_tarihi') or result['tarih']}"
    by_address = {str(r["adres"]).lower(): dict(r) for r in existing}
    rows, counters = [], {k: 0 for k in ONEK}
    used = {r["id"] for r in existing}
    replaced: set[str] = set()
    for address, e in result["adresler"].items():
        kollar = [k for k in e["kollar"] if k in LISTE_KOLLARI]
        if not kollar:
            continue
        row = by_address.get(address)
        selected = bool(set(kollar) & {"oda", "kontrol", "taban"})
        if row is not None and selected and row.get("secim") != label:
            replaced.add(address)
            row = None
        if row is None:
            kind = kollar[0]
            while True:
                counters[kind] += 1
                ident = f"{ONEK[kind]}{counters[kind]:02d}"
                if ident not in used:
                    break
            used.add(ident)
            row = {"id": ident, "adres": address, "takma_ad": address[2:6], "durum": "izlemede", "t0": t0}
            if e["tarz"] in TARZLAR:
                row["tarz"] = e["tarz"]
        if selected:
            row["secim"] = label
        row["kol"], row["kollar"] = kollar[0], kollar
        rows.append(row)
    kept = {r["adres"].lower() for r in rows}
    rows += [{**r, "kol": r.get("kol", "elle")} for a, r in by_address.items() if a not in kept]     # listede olup seçimde çıkmayan (korunur)
    return rows


def yaz_izleme_listesi(rows: list[dict[str, Any]], path: Path) -> None:
    header = ("# İZLEME LİSTESİ — `python -m copytrade.secim --izleme-listesi` ile secim.json'dan üretilir; ELLE YAZILMAZ.\n"
              "# kol: oda (Telegram bildirimi var) | kontrol | taban | elle (sessiz izleme). kollar: adresin bulunduğu tüm kollar.\n")
    path.write_text(header + yaml.safe_dump({"traderlar": rows}, allow_unicode=True, sort_keys=False), encoding="utf-8")


def latest(root: Path, pattern: str) -> Path:
    paths = sorted(root.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"{root}/{pattern} yok")
    return paths[-1]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("copytrade"))
    parser.add_argument("--output", type=Path, default=Path("secim"))
    parser.add_argument("--tarih", default=None, help="varsayılan: bugün (UTC)")
    parser.add_argument("--taban-dosyasi", type=Path, default=None, help="lider tablosu JSON'u (yoksa Hyperliquid'den çekilir)")
    parser.add_argument("--bayraksiz", action="store_true", help="(v1.3'te varsayılan) seçim kırmızı bayrak hesaplamaz; bayraklar --bayrak ile ayrı işte")
    parser.add_argument("--bayrak", action="store_true", help="--secim (varsayılan: en son) secim.json'daki aday katı için bayrak.json üret (ağ isteği)")
    parser.add_argument("--izleme-listesi", action="store_true", help="secim.json'dan copytrade/izleme_listesi.yaml üret")
    parser.add_argument("--secim", type=Path, default=None, help="--izleme-listesi için secim.json (varsayılan: en son)")
    args = parser.parse_args(argv)
    date = args.tarih or datetime.now(UTC).strftime("%Y-%m-%d")
    list_path = args.root / "izleme_listesi.yaml"
    if args.izleme_listesi:
        source = args.secim or latest(args.output, "*/secim.json")
        existing = yaml.safe_load(list_path.read_text(encoding="utf-8")) if list_path.exists() else []
        existing = existing["traderlar"] if isinstance(existing, dict) else existing or []
        rows = izleme_listesi(json.loads(source.read_text(encoding="utf-8")), existing, date)
        yaz_izleme_listesi(rows, list_path)
        print(f"İzleme listesi: {len(rows)} satır ({source}).")
        return
    if args.bayrak:
        from copytrade import bayrak
        from copytrade.tarama import PublicClient
        source = args.secim or latest(args.output, "*/secim.json")
        client = PublicClient()
        target = source.parent / "bayrak.json"
        previous = json.loads(target.read_text(encoding="utf-8")) if target.exists() else None      # önceki (kısmi) sonuç = önbellek

        secim_json = json.loads(source.read_text(encoding="utf-8"))

        def write(body):                                                                              # her adresten sonra checkpoint (kısmi sonuç da okunur)
            (source.parent / "BAYRAK.md").write_text(bayrak_raporu(secim_json, body), encoding="utf-8")
            temporary = target.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(body, ensure_ascii=False, indent=1, allow_nan=False) + "\n", encoding="utf-8")
            temporary.replace(target)
        body = bayrak_hesapla(secim_json, lambda address, value: bayrak.hesapla(client, address, value), previous, write)
        print(f"Bayrak: {len(body['bayraklar'])} adres ({source.parent}).")
        return
    path = latest(args.root, "kapi/*/sonuc.csv")
    kapi_tarihi = path.parent.name
    durum = json.loads((path.parent / "durum.json").read_text(encoding="utf-8"))
    rules = load_rules()
    if durum.get("durum") != "tamam":
        raise SystemExit(f"Kapı koşusu tamam değil (durum={durum.get('durum')}); seçim yapılmaz.")
    if float(durum.get("kapsam") or 0) < float(rules["secim_min_kapsam"]):
        raise SystemExit(f"Kapı kapsamı {durum.get('kapsam')} < {rules['secim_min_kapsam']}: tam koşu değil (hızlı koşu?); seçim yapılmaz.")
    out = args.output / f"{date}-{rules['secim_surumu']}"
    for published in args.output.glob("*/secim.json"):
        old = json.loads(published.read_text(encoding="utf-8"))
        if published.parent == out or (old.get("secim_surumu") == rules["secim_surumu"] and old.get("kapi_tarihi") == kapi_tarihi):
            raise SystemExit(f"{published} yayımlı (sürüm {old.get('secim_surumu')}, kapı {old.get('kapi_tarihi')}): yayımlanan seçimin üzerine yazılmaz.")
    table = pd.read_csv(path, low_memory=False)
    if args.taban_dosyasi:
        board = json.loads(args.taban_dosyasi.read_text(encoding="utf-8"))
    else:
        from copytrade.tarama import PublicClient
        board = PublicClient().leaderboard()
    result = sec(table, date, board, elle_liste(list_path), rules, None, kapi_tarihi)
    out.mkdir(parents=True, exist_ok=True)
    (out / "secim.json").write_text(json.dumps(result, ensure_ascii=False, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    (out / "RAPOR.md").write_text(rapor(result, table, durum), encoding="utf-8")
    print(f"Çıktı: {out}")
    print(f"Seçim {date}: {result['sayilar']}")


if __name__ == "__main__":
    main()
