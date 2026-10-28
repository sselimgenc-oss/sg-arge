"""Hugging Face geçmiş hesap verisinin doğrulanması (``docs/GOREV_HF_DOGRULAMA.md``).

Kaynak: ``ProbioticFarmer/hyperliquid-augmented-copytrading``. Tamamı indirilmez: DuckDB ``hf://`` ile yalnız gereken sütun/tarih okunur.
Yöntemi ve kapıyı değiştirmez; yalnız veri kaynağını ölçer. **Tolerans ya da "kullanılır" kararı yoktur**; sayılar raporlanır.
Çıktı: ``hf_dogrulama.json``. Herhangi bir adım hata verirse hata JSON'a yazılır ve süreç sıfırdan farklı çıkar (sessiz geçilmez).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

REPO = "ProbioticFarmer/hyperliquid-augmented-copytrading"
BASE = f"hf://datasets/{REPO}"
HF_API = f"https://huggingface.co/api/datasets/{REPO}/tree/main"
HF_CARD = f"https://huggingface.co/datasets/{REPO}/raw/main/README.md"
ACCOUNT_SUBSET = "account_values"
LEDGER_WORDS = re.compile(r"ledger|deposit|withdraw|transfer|nonfunding|non_funding|flow", re.I)
ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
DAY_MS = 86_400_000


# ----------------------------------------------------------------------------------------------- saf hesaplar
def tarih_yolu(base: str, subset: str, day: str | None = None) -> str:
    """Tarih bölümü yolu: ``<base>/<alt küme>/date=<gün>/*.parquet``; gün yoksa tüm bölümler (``date=*``)."""
    return f"{base}/{subset}/date={day or '*'}/*.parquet"


def tarih_bolumleri(names: list[str]) -> list[str]:
    """Dizin adlarından ``date=YYYY-MM-DD`` bölümlerinin günleri (sıralı, tekrarsız); diğer adlar atılır."""
    days = {m.group(1) for n in names if (m := re.fullmatch(r"date=(\d{4}-\d{2}-\d{2})", n.rsplit("/", 1)[-1]))}
    return sorted(days)


def bosluklar(days: list[str]) -> list[str]:
    """İlk ile son gün arasında listede olmayan günler (ISO)."""
    parsed = sorted({date.fromisoformat(d) for d in days})
    if len(parsed) < 2:
        return []
    have = set(parsed)
    return [(parsed[0] + timedelta(days=i)).isoformat() for i in range((parsed[-1] - parsed[0]).days + 1)
            if parsed[0] + timedelta(days=i) not in have]


def goreli_fark(hf: float, ref: float) -> float | None:
    """|hf − ref| / |ref|; ref 0 ise tanımsız (``None``)."""
    return None if not ref else abs(hf - ref) / abs(ref)


def fark_ozeti(pairs: list[tuple[float, float]]) -> dict[str, Any]:
    """(hf, ref) çiftlerinin göreli fark dağılımı: n, ref'i 0 olan sayısı, min / medyan / max."""
    diffs = [d for hf, ref in pairs if (d := goreli_fark(hf, ref)) is not None]
    out: dict[str, Any] = {"n": len(diffs), "ref_sifir": len(pairs) - len(diffs), "min": None, "medyan": None, "max": None}
    if diffs:
        out.update(min=min(diffs), medyan=statistics.median(diffs), max=max(diffs))
    return out


def en_yakin(history: list, target_ms: int) -> tuple[float, int] | None:
    """``[[ms, değer], …]`` içinden hedef zamana en yakın nokta: (değer, |zaman farkı ms|). Boşsa ``None``."""
    points = [(int(t), float(v)) for t, v in history]
    if not points:
        return None
    t, v = min(points, key=lambda p: (abs(p[0] - target_ms), p[0]))
    return v, abs(t - target_ms)


def gecmis_tarihler(latest: str, available: list[str], offsets: tuple[int, ...] = (30, 90, 180)) -> list[str]:
    """En son tarihten ``offsets`` gün öncesine en yakın MEVCUT bölüm günü (eşitlikte erken olan); en son günün kendisi ve tekrarlar atılır."""
    base = date.fromisoformat(latest)
    days = sorted({date.fromisoformat(d) for d in available} - {base})
    out: list[str] = []
    for n in offsets:
        if days:
            target = base - timedelta(days=n)
            pick = min(days, key=lambda d: (abs((d - target).days), d)).isoformat()
            if pick not in out:
                out.append(pick)
    return out


def gun_ms(day: str) -> int:
    """Günün UTC öğle vakti (ms): gün bölümü için tek, tarafsız karşılaştırma anı."""
    return int(datetime.fromisoformat(day).replace(tzinfo=UTC).timestamp() * 1000) + DAY_MS // 2


# ----------------------------------------------------------------------------------------------- Hugging Face listeleme
def hf_ls(path: str = "", session: requests.Session | None = None) -> list[dict[str, Any]]:
    """HF API ağaç listesi (sayfalı: ``Link: next``). ``path`` boş = kök."""
    session = session or requests.Session()
    url, rows = HF_API + (f"/{path}" if path else ""), []
    while url:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        rows.extend(response.json())
        url = response.links.get("next", {}).get("url")
    return rows


def alt_kumeler(session: requests.Session | None = None) -> list[str]:
    return sorted(r["path"] for r in hf_ls("", session) if r.get("type") == "directory" and not r["path"].startswith("."))


def veri_karti(session: requests.Session | None = None) -> str:
    response = (session or requests.Session()).get(HF_CARD, timeout=60)
    response.raise_for_status()
    return response.text


# ----------------------------------------------------------------------------------------------- DuckDB
def baglan():
    import duckdb
    con = duckdb.connect()
    con.execute("SET enable_progress_bar=false")
    return con


def _sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sutunlar(con, glob: str) -> list[dict[str, str]]:
    return [{"ad": r[0], "tur": r[1]} for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet({_sql_str(glob)}, hive_partitioning=true)").fetchall()]


def satir_sayisi(con, glob: str) -> int:
    """Parquet altbilgilerinden toplam satır (veri okunmaz)."""
    return int(con.execute(f"SELECT coalesce(sum(num_rows), 0) FROM parquet_file_metadata({_sql_str(glob)})").fetchone()[0])


def gunluk_kapsam(con, glob: str) -> list[dict[str, Any]]:
    """Gün başına satır ve ayrık adres sayısı (``user`` sütunu; bölüm sütunu ``date``)."""
    rows = con.execute(f"SELECT CAST(date AS VARCHAR), count(*), count(DISTINCT lower(user)) "
                       f"FROM read_parquet({_sql_str(glob)}, hive_partitioning=true) GROUP BY 1 ORDER BY 1").fetchall()
    return [{"gun": d, "satir": int(n), "adres": int(a)} for d, n, a in rows]


def hf_degerleri(con, glob: str, addresses: list[str]) -> dict[str, dict[str, Any]]:
    """Bir gün bölümünde adres başına ``account_value`` toplamı (tüm dex ve teminat satırları) ve satır sayısı."""
    if not addresses:
        return {}
    listed = ", ".join(_sql_str(a.lower()) for a in addresses)
    rows = con.execute(f"SELECT lower(user), sum(account_value), count(*) FROM read_parquet({_sql_str(glob)}, hive_partitioning=true) "
                       f"WHERE lower(user) IN ({listed}) GROUP BY 1").fetchall()
    return {u: {"account_value": float(v), "satir": int(n)} for u, v, n in rows}


def ledger_adaylari(columns_by_subset: dict[str, list[dict[str, str]]]) -> dict[str, list[str]]:
    """Alt küme adı veya sütun adı yatırma/çekme/transfer sözcüğü içerenler (bulunamazsa boş sözlük = yok)."""
    out = {}
    for subset, columns in columns_by_subset.items():
        hits = [c["ad"] for c in columns if LEDGER_WORDS.search(c["ad"])]
        if LEDGER_WORDS.search(subset) or hits:
            out[subset] = hits
    return out


# ----------------------------------------------------------------------------------------------- adım 3: çapraz doğrulama
def kapi_adresleri(root: Path, count: int = 30) -> list[str]:
    """Kapı sonucundan (en son ``sonuc.csv``) bugünkü hesap değeri dolu, adrese göre ilk ``count`` adres (deterministik)."""
    import pandas as pd
    paths = sorted(root.glob("kapi/*/sonuc.csv"))
    if not paths:
        raise FileNotFoundError("kapı sonuc.csv yok (veri dalı alınmadı)")
    table = pd.read_csv(paths[-1])
    column = "hesap_degeri_bugun" if "hesap_degeri_bugun" in table else "account_value"
    table = table[table[column].notna() & (table[column] > 0)].copy()
    table["address"] = table["address"].str.lower()
    return sorted(set(table["address"]))[:count]


def capraz(con, base: str, client: Any, addresses: list[str], latest: str, past: list[str], now_ms: int | None = None) -> dict[str, Any]:
    """HF ``account_value`` ↔ Hyperliquid: en son tarihte güncel ``clearinghouseState`` parçaları (ana / +HIP-3 / +spot) ve ``portfolio`` geçmişinin
    aynı güne en yakın noktası; geçmiş tarihlerde yalnız ``portfolio``. Her karşılaştırma için göreli fark dağılımı."""
    from copytrade.kapi import _portfolio_history, account_value_parts, hip3_dex_names
    now_ms = now_ms or int(time.time() * 1000)
    dexes = hip3_dex_names(client)
    portfolio: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for address in addresses:
        try:
            portfolio[address] = client.portfolio(address)
        except Exception as exc:                                   # noqa: BLE001 — her adres ayrı raporlanır, sessiz geçilmez
            errors[address] = f"portfolio: {type(exc).__name__}: {exc}"[:200]

    def history(address: str) -> list:
        series = _portfolio_history(portfolio[address])
        return [[int(ts.timestamp() * 1000), float(v)] for ts, v in series.items()]

    report: dict[str, Any] = {"adres_sayisi": len(addresses), "dex": dexes, "hatalar": errors, "tarihler": {}}
    for day in [latest, *past]:
        hf = hf_degerleri(con, tarih_yolu(base, ACCOUNT_SUBSET, day), addresses)
        entry: dict[str, Any] = {"hf_adres": len(hf), "hf_eksik_adres": [a for a in addresses if a not in hf]}
        pairs = []
        for address, value in hf.items():
            if address in portfolio:
                near = en_yakin(history(address), gun_ms(day))
                if near:
                    pairs.append((value["account_value"], near[0], near[1]))
        entry["portfolio"] = {**fark_ozeti([(h, r) for h, r, _ in pairs]), "zaman_farki_gun_medyan":
                              statistics.median([d / DAY_MS for _, _, d in pairs]) if pairs else None}
        if day == latest:
            live: dict[str, dict[str, float]] = {}
            for address in hf:
                try:
                    live[address] = account_value_parts(client, address, dexes)
                except Exception as exc:                           # noqa: BLE001
                    errors[address] = f"clearinghouseState: {type(exc).__name__}: {exc}"[:200]
            entry["clearinghouse_yas_gun"] = (now_ms - gun_ms(day)) / DAY_MS
            for name, pick in (("ana", lambda p: p["ana"]), ("ana_hip3", lambda p: p["ana"] + p["hip3"]),
                               ("ana_hip3_spot", lambda p: p["ana"] + p["hip3"] + p["spot_usdc"])):
                entry[f"clearinghouse_{name}"] = fark_ozeti([(hf[a]["account_value"], pick(p)) for a, p in live.items()])
        report["tarihler"][day] = entry
    return report


# ----------------------------------------------------------------------------------------------- koşu
def calistir(args: argparse.Namespace, client: Any | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"surum": 1, "uretildi": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "kaynak": REPO,
                              "adimlar": {}, "hatalar": {}}

    def step(name: str, call):
        started = time.time()
        try:
            result["adimlar"][name] = call()
        except Exception as exc:                                    # noqa: BLE001 — hata JSON'a yazılır, süreç sonunda kırmızı çıkar
            result["hatalar"][name] = f"{type(exc).__name__}: {exc}"[:500]
        result.setdefault("sure_sn", {})[name] = round(time.time() - started, 1)

    con = baglan()
    base = args.base
    session = requests.Session()
    subsets: list[str] = []
    columns: dict[str, list[dict[str, str]]] = {}

    def envanter():
        nonlocal subsets
        subsets = args.alt_kume or alt_kumeler(session)
        out: dict[str, Any] = {}
        for subset in subsets:
            info: dict[str, Any] = {}
            try:
                days = tarih_bolumleri([r["path"] for r in hf_ls(subset, session)]) if base == BASE else \
                    tarih_bolumleri([p.name for p in (Path(base) / subset).iterdir()])
                info.update(gun_sayisi=len(days), ilk=days[0] if days else None, son=days[-1] if days else None)
                glob = tarih_yolu(base, subset, days[-1]) if days else f"{base}/{subset}/**/*.parquet"
                columns[subset] = info["sutunlar"] = sutunlar(con, glob)
                info["satir"] = satir_sayisi(con, tarih_yolu(base, subset) if days else f"{base}/{subset}/**/*.parquet")
            except Exception as exc:                                # noqa: BLE001
                info["hata"] = f"{type(exc).__name__}: {exc}"[:300]
                result["hatalar"][f"envanter/{subset}"] = info["hata"]
            out[subset] = info
        try:
            out["_veri_karti"] = veri_karti(session)[:20000] if base == BASE else ""
        except Exception as exc:                                    # noqa: BLE001
            result["hatalar"]["veri_karti"] = f"{type(exc).__name__}: {exc}"[:300]
        return out

    step("envanter", envanter)
    days: list[str] = []

    def kapsam():
        nonlocal days
        rows = gunluk_kapsam(con, tarih_yolu(base, ACCOUNT_SUBSET))
        days = [r["gun"] for r in rows]
        counts = [r["adres"] for r in rows]
        return {"ilk": days[0], "son": days[-1], "gun_sayisi": len(days), "bosluklar": bosluklar(days),
                "adres_min": min(counts), "adres_medyan": statistics.median(counts), "adres_max": max(counts), "gunluk": rows}

    step("kapsam", kapsam)

    def capraz_dogrulama():
        if not days:
            raise RuntimeError("kapsam adımı gün listesi üretmedi")
        from copytrade.tarama import PublicClient
        return capraz(con, base, client or PublicClient(), kapi_adresleri(args.root), days[-1], gecmis_tarihler(days[-1], days))

    step("capraz", capraz_dogrulama)
    step("ledger", lambda: {"aday_alt_kume_ve_sutunlar": ledger_adaylari(columns),
                            "sonuc": "var" if ledger_adaylari(columns) else "yok: hiçbir alt küme/sütun adı yatırma-çekme-transfer içermiyor",
                            "taranan_alt_kume": sorted(columns)})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("copytrade"), help="kapı sonuçlarının kökü (copytrade/kapi/*/sonuc.csv)")
    parser.add_argument("--base", default=BASE, help="hf://… ya da yerel dizin (test)")
    parser.add_argument("--alt-kume", action="append", default=None, help="yalnız bu alt küme(ler)")
    parser.add_argument("--output", type=Path, default=Path("hf_dogrulama.json"))
    args = parser.parse_args(argv)
    result = calistir(args)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1, allow_nan=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "adimlar"}, ensure_ascii=False, indent=1))
    return 1 if result["hatalar"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
