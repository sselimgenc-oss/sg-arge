"""Seçim v1 (``docs/GOREV_SECIM_V1.md``): kapı sonucundan havuz, aday, oda, kontrol, taban ve elle liste.

Eşik yok: tüm sayılar ``kurallar.yaml``'daki ``secim_*`` anahtarlarından gelir. Yalnız herkese açık veri; emir yok.
Çıktı (veri dalına): ``secim/<tarih>/secim.json`` ve ``RAPOR.md``. İzleme listesi ``--izleme-listesi`` ile ``secim.json``'dan üretilir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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


def puan(row: dict[str, Any]) -> float | None:
    """Tarzın kapı gecikmesindeki maliyet sonrası net kopya getirisi; yoksa ``None`` (puansız)."""
    delay = _num(row.get("kapi_gecikme_dk"))
    return None if delay is None else _num(row.get(f"gecikme_{int(delay)}dk_net"))


def havuz(table: pd.DataFrame) -> list[dict[str, Any]]:
    """Adım 1 ve 2 Geçti, tarzı intraday/swing olan satırlar; ``puan`` eklenmiş, adrese göre sıralı."""
    rows = []
    for row in table.to_dict("records"):
        if row.get("adim1") == "Geçti" and row.get("adim2") == "Geçti" and row.get("tarz") in TARZLAR:
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


def tohum(date: str) -> int:
    """``secim-v1-<tarih>`` dizgesinin SHA-256'sının ilk 8 baytı."""
    return int.from_bytes(hashlib.sha256(f"secim-v1-{date}".encode()).digest()[:8], "big")


def kontrol_sec(pool: list[dict[str, Any]], count: int, date: str) -> list[dict[str, Any]]:
    """Havuzdan puana bakmadan rastgele ``count`` adres. Sıra = ``sha256(tohum-adres)``; kütüphane sürümünden bağımsız, tekrarlanabilir."""
    seed = tohum(date)
    ranked = sorted(pool, key=lambda r: hashlib.sha256(f"{seed}-{r['address']}".encode()).hexdigest())
    return ranked[:min(count, len(ranked))]


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
        bayrak_fn=None) -> dict[str, Any]:
    """``bayrak_fn(adres, hesap_degeri) -> {bayrak_*: …}``: yalnız aday katı için çağrılır; bilgi sütunudur, seçimi değiştirmez."""
    rules = rules or load_rules()
    pool = havuz(table)
    candidates = [r for r in adaylar(pool, rules)]
    room = oda_sec(candidates, rules)
    oda = room["oda"]
    control = kontrol_sec(pool, len(oda), date)
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
            "genc_aday": _flag(row.get("genc_aday")) if row else None,
            "medyan_kaldirac": _num(row.get("median_leverage")), "en_yuksek_kaldirac": _num(row.get("max_leverage")),
            "gecmis_gun": _num(row.get("gecmis_gun")), "hesap_degeri": _num(row.get("hesap_degeri_bugun")) or _num(row.get("account_value")),
            "iliskili_not": room["notlar"].get(address) or (str(row.get("iliskili_not")) if str(row.get("iliskili_not", "nan")) not in ("", "nan") else ""),
            "hesap_surumu": row.get("hesap") if isinstance(row.get("hesap"), str) else None}
        if address in sira and bayrak_fn is not None:
            value = _num(row.get("hesap_degeri_bugun")) or _num(row.get("account_value")) or 0.0
            entries[address].update(bayrak_fn(address, value))
    counts = {t: {"havuz": sum(r["tarz"] == t for r in pool), "puansiz": sum(r["tarz"] == t and r["puan"] is None for r in pool),
                  "aday": sum(r["tarz"] == t for r in candidates), "oda": sum(r["tarz"] == t for r in oda)} for t in TARZLAR}
    return {"surum": 1, "tarih": date, "tohum": tohum(date), "tohum_dizgesi": f"secim-v1-{date}",
            "sayilar": {"kapi_satiri": int(len(table)), "havuz": len(pool), "aday": len(candidates), "oda": len(oda),
                        "kontrol": len(control), "taban": len(base), "elle": len(manual), "tarz": counts},
            "oda_kisa": room["kisa"], "oda_kota": room["kota"],
            "kontrol": [r["address"] for r in control], "adresler": entries}


def _fmt(value: Any, digits: int = 3) -> str:
    return "–" if value is None else f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def ozet_sutunlar(table: pd.DataFrame) -> list[str]:
    lines = ["| sütun | dolu | min | medyan | max |", "|---|---|---|---|---|"]
    for name in table.columns:
        values = pd.to_numeric(table[name], errors="coerce").dropna()
        if len(values) and not table[name].dtype == bool:
            lines.append(f"| {name} | {len(values)} | {values.min():.4g} | {values.median():.4g} | {values.max():.4g} |")
    return lines


def rapor(result: dict[str, Any], table: pd.DataFrame, durum: dict[str, Any]) -> str:
    n = result["sayilar"]
    lines = [f"# Seçim v1 — {result['tarih']}", "",
             f"- Girdi: kapı satırı {n['kapi_satiri']}, hesap sürümü {durum.get('hesap')}, kapsam {durum.get('kapsam')}, durum `{durum.get('durum')}`.",
             f"- Havuz {n['havuz']} · aday {n['aday']} · oda {n['oda']} · kontrol {n['kontrol']} · taban {n['taban']} · elle {n['elle']}.", ""]
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
        lines += ["", "## Kırmızı bayraklar (bilgi; kimseyi elemez — oda üyeleri)", "",
                  "| adres | rol | vault oranı | funding payı | alt hesapta ters | 30 gün hacim/hesap | not |", "|---|---|---|---|---|---|---|"]
        lines += [f"| `{a}` | {e['bayrak_rol'] or '–'} | {_fmt(e['bayrak_vault_orani'])} | {_fmt(e['bayrak_funding_payi'])} | "
                  f"{e['bayrak_alt_hesap_ters']} | {_fmt(e['bayrak_hacim_orani'], 2)} | {e['bayrak_not'] or ''} |" for a, e in flagged]
    dropped = [(a, e["iliskili_not"]) for a, e in sorted(result["adresler"].items()) if e["iliskili_not"].startswith("ilişkili hesap")]
    if dropped:
        lines += ["", "## İlişkili hesap nedeniyle odaya girmeyenler", ""] + [f"- `{a}`: {note}" for a, note in dropped]
    lines += ["", "## Kontrol", "", f"Tohum: `{result['tohum_dizgesi']}` → {result['tohum']}. Seçilenler (oda üyeleri de çıkabilir):", ""]
    lines += [f"- `{a}`" for a in result["kontrol"]]
    lines += ["", "## Kapı tablosu sütun özeti (min/medyan/max)", ""] + ozet_sutunlar(table)
    return "\n".join(lines) + "\n"


def izleme_listesi(result: dict[str, Any], existing: list[dict[str, Any]], t0: str) -> list[dict[str, Any]]:
    """``secim.json``'dan izleme listesi: oda + kontrol + taban + elle. Var olan satırın id/t0'ı değişmez, yalnız ``kol``/``kollar`` eklenir."""
    by_address = {str(r["adres"]).lower(): dict(r) for r in existing}
    rows, counters = [], {k: 0 for k in ONEK}
    used = {r["id"] for r in existing}
    for address, e in result["adresler"].items():
        kollar = [k for k in e["kollar"] if k in LISTE_KOLLARI]
        if not kollar:
            continue
        row = by_address.get(address)
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
    parser.add_argument("--bayraksiz", action="store_true", help="kırmızı bayrak sütunlarını hesaplama (ağ isteği yok)")
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
    path = latest(args.root, "kapi/*/sonuc.csv")
    durum = json.loads((path.parent / "durum.json").read_text(encoding="utf-8"))
    rules = load_rules()
    if durum.get("durum") != "tamam":
        raise SystemExit(f"Kapı koşusu tamam değil (durum={durum.get('durum')}); seçim yapılmaz.")
    if float(durum.get("kapsam") or 0) < float(rules["secim_min_kapsam"]):
        raise SystemExit(f"Kapı kapsamı {durum.get('kapsam')} < {rules['secim_min_kapsam']}: tam koşu değil (hızlı koşu?); seçim yapılmaz.")
    table = pd.read_csv(path)
    if args.taban_dosyasi:
        board = json.loads(args.taban_dosyasi.read_text(encoding="utf-8"))
    else:
        from copytrade.tarama import PublicClient
        board = PublicClient().leaderboard()
    bayrak_fn = None
    if not args.bayraksiz:
        from copytrade import bayrak
        from copytrade.tarama import PublicClient
        client = PublicClient()
        bayrak_fn = lambda address, value: bayrak.hesapla(client, address, value)    # noqa: E731
    result = sec(table, date, board, elle_liste(list_path), rules, bayrak_fn)
    out = args.output / date
    out.mkdir(parents=True, exist_ok=True)
    (out / "secim.json").write_text(json.dumps(result, ensure_ascii=False, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    (out / "RAPOR.md").write_text(rapor(result, table, durum), encoding="utf-8")
    print(f"Seçim {date}: {result['sayilar']}")


if __name__ == "__main__":
    main()
