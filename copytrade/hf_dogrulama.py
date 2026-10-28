"""Hugging Face geçmiş hesap verisinin doğrulanması (``docs/GOREV_HF_DOGRULAMA.md``).

Kaynak: ``ProbioticFarmer/hyperliquid-augmented-copytrading``. Tamamı indirilmez: DuckDB ``hf://`` ile yalnız gereken sütun/tarih okunur.
Yöntemi ve kapıyı değiştirmez; yalnız veri kaynağını ölçer. **Tolerans ya da "kullanılır" kararı yoktur**; sayılar raporlanır.
Çıktı: ``hf_dogrulama.json``. Herhangi bir adım hata verirse hata JSON'a yazılır ve süreç sıfırdan farklı çıkar (sessiz geçilmez).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import threading
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
T0 = time.time()


def log(message: str) -> None:
    """İlerleme satırı (stderr, anında): uzun koşuda iş akışı günlüğü boş kalmasın."""
    print(f"[{time.time() - T0:7.0f} sn] {message}", file=sys.stderr, flush=True)


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


# ----------------------------------------------------------------------------------------------- kaynaklar (HF ya da yerel dizin)
def dosya_gunu(path: str) -> str | None:
    m = re.search(r"date=(\d{4}-\d{2}-\d{2})", path)
    return m.group(1) if m else None


def parquet_dosyalari(tree: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ağaç listesinden ``.parquet`` dosyaları: ``{path, size, gun}`` (yola göre sıralı)."""
    return sorted(({"path": r["path"], "size": int(r.get("size") or 0), "gun": dosya_gunu(r["path"])}
                   for r in tree if r.get("type", "file") == "file" and r["path"].endswith(".parquet")), key=lambda r: r["path"])


def uzantilar(tree: list[dict[str, Any]]) -> dict[str, int]:
    """Parquet dışı dosyaların uzantı sayımı (ör. ``notebooks`` ``.ipynb``)."""
    out: dict[str, int] = {}
    for r in tree:
        if r.get("type", "file") == "file":
            ext = r["path"].rsplit(".", 1)[-1] if "." in r["path"].rsplit("/", 1)[-1] else "(uzantısız)"
            out[ext] = out.get(ext, 0) + 1
    return dict(sorted(out.items()))


def yeniden(call, tries: int = 6, base_wait: float = 5.0, sleep=time.sleep):
    """HTTP 429/5xx (HF hız sınırı) için üstel bekleme ile yeniden dene; başka hata ya da son deneme olduğu gibi fırlatılır."""
    for attempt in range(tries):
        try:
            return call()
        except Exception as exc:                                   # noqa: BLE001
            text = str(exc)
            transient = isinstance(exc, requests.HTTPError) and exc.response is not None and exc.response.status_code in (429, 500, 502, 503, 504) \
                or any(code in text for code in ("HTTP 429", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504", "429 Too Many"))
            if not transient or attempt == tries - 1:
                raise
            sleep(base_wait * 2 ** attempt)


class HFKaynak:
    """Hugging Face: alt kümeler ve dosya ağacı ``recursive`` API'siyle (alt küme başına birkaç sayfa); DuckDB'ye açık dosya URL'leri verilir
    (``date=*`` joker karakteri DuckDB'nin her dizini ayrı API çağrısıyla listelemesine ve 429'a yol açıyordu)."""
    ad = BASE

    def __init__(self, session: requests.Session | None = None, token: str | None = None):
        self.session = session or requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, url: str):
        def call():
            response = self.session.get(url, timeout=120)
            response.raise_for_status()
            return response
        return yeniden(call)

    def alt_kumeler(self) -> list[str]:
        return sorted(r["path"] for r in self._get(HF_API).json() if r.get("type") == "directory" and not r["path"].startswith("."))

    def agac(self, subset: str) -> list[dict[str, Any]]:
        url, rows = f"{HF_API}/{subset}?recursive=true", []
        while url:
            response = self._get(url)
            rows.extend(response.json())
            log(f"  ağaç {subset}: {len(rows)} kayıt")
            url = response.links.get("next", {}).get("url")
        return rows

    def url(self, path: str) -> str:
        return f"{BASE}/{path}"

    def veri_karti(self) -> str:
        return self._get(HF_CARD).text


class YerelKaynak:
    """Yerel dizin (test): aynı arayüz."""
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.ad = str(self.root)

    def alt_kumeler(self) -> list[str]:
        return sorted(p.name for p in self.root.iterdir() if p.is_dir())

    def agac(self, subset: str) -> list[dict[str, Any]]:
        return [{"path": p.relative_to(self.root).as_posix(), "size": p.stat().st_size, "type": "file"}
                for p in sorted((self.root / subset).rglob("*")) if p.is_file()]

    def url(self, path: str) -> str:
        return str(self.root / path)

    def veri_karti(self) -> str:
        return ""


# ----------------------------------------------------------------------------------------------- DuckDB
def baglan(token: str | None = None):
    import duckdb
    con = duckdb.connect()
    con.execute("SET enable_progress_bar=false")
    if token:
        con.execute(f"CREATE SECRET hf_gizli (TYPE HUGGINGFACE, TOKEN {_sql_str(token)})")
    return con


def _sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _liste(urls: list[str]) -> str:
    return "[" + ", ".join(_sql_str(u) for u in urls) + "]"


PARCA = 100      # tek sorguda en çok bu kadar dosya (bellek/URL boyutu sınırı; eşik değil)


def sutunlar(con, urls: list[str]) -> list[dict[str, str]]:
    return [{"ad": r[0], "tur": r[1]} for r in
            con.execute(f"DESCRIBE SELECT * FROM read_parquet({_liste(urls[-1:])}, hive_partitioning=true)").fetchall()]


def satir_sayisi(con, urls: list[str], bitis: float | None = None, ilerleme: dict[str, Any] | None = None) -> int:
    """Parquet altbilgilerinden toplam satır (veri okunmaz). ``bitis`` (epoch sn) aşılırsa parçalar arasında durur; taranan dosya sayısı ``ilerleme``ye yazılır."""
    total, done = 0, 0
    for i in range(0, len(urls), PARCA):
        if bitis and time.time() > bitis:
            break
        part = urls[i:i + PARCA]
        total += int(con.execute(f"SELECT coalesce(sum(num_rows), 0) FROM parquet_file_metadata({_liste(part)})").fetchone()[0])
        done += len(part)
        log(f"  satır sayımı: {done}/{len(urls)} dosya")
    if ilerleme is not None:
        ilerleme.update(taranan_dosya=done, toplam_dosya=len(urls))
    return total


def gunluk_kapsam(con, by_day: dict[str, list[str]], bitis: float | None = None, ilerleme: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Gün başına satır ve ayrık adres sayısı (``user``). Bir günün tüm dosyaları aynı sorguda (ayrık sayım toplanamaz); sorgu başına ~``PARCA`` dosya.
    ``bitis`` (epoch sn) aşılırsa parçalar arasında durur (kısmi sonuç); ``ilerleme`` taranan/toplam gün sayısını taşır."""
    days, out, i = sorted(by_day), [], 0
    while i < len(days):
        if bitis and time.time() > bitis:
            break
        chunk, files = [], 0
        while i < len(days) and (not chunk or files + len(by_day[days[i]]) <= PARCA):
            chunk.append(days[i]); files += len(by_day[days[i]]); i += 1
        urls = [u for d in chunk for u in by_day[d]]
        rows = con.execute(f"SELECT CAST(date AS VARCHAR), count(*), count(DISTINCT lower(user)) "
                           f"FROM read_parquet({_liste(urls)}, hive_partitioning=true) GROUP BY 1 ORDER BY 1").fetchall()
        out += [{"gun": d, "satir": int(n), "adres": int(a)} for d, n, a in rows]
        log(f"  kapsam: {len(out)}/{len(days)} gün")
    if ilerleme is not None:
        ilerleme.update(taranan_gun=len(out), toplam_gun=len(days))
    return out


def hf_degerleri(con, urls: list[str], addresses: list[str]) -> dict[str, dict[str, Any]]:
    """Bir gün bölümünün dosyalarında adres başına ``account_value`` toplamı (tüm dex ve teminat satırları) ve satır sayısı."""
    if not addresses or not urls:
        return {}
    listed = ", ".join(_sql_str(a.lower()) for a in addresses)
    rows = con.execute(f"SELECT user, sum(v), sum(n) FROM (SELECT lower(user) AS user, sum(account_value) AS v, count(*) AS n "
                       f"FROM read_parquet({_liste(urls)}, hive_partitioning=true) WHERE lower(user) IN ({listed}) GROUP BY 1) GROUP BY 1").fetchall()
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


def capraz(con, day_urls: dict[str, list[str]], client: Any, addresses: list[str], latest: str, past: list[str], now_ms: int | None = None) -> dict[str, Any]:
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
        hf = yeniden(lambda: hf_degerleri(con, day_urls.get(day, []), addresses))
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
def calistir(args: argparse.Namespace, client: Any | None = None, kaynak: Any | None = None) -> dict[str, Any]:
    token = os.environ.get("HF_TOKEN") or None
    kaynak = kaynak or (HFKaynak(token=token) if args.base == BASE else YerelKaynak(args.base))
    result: dict[str, Any] = {"surum": 1, "uretildi": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "kaynak": REPO,
                              "adimlar": {}, "hatalar": {}}

    con = baglan(token)
    budgets = {"envanter": getattr(args, "butce_envanter", 2400), "kapsam": getattr(args, "butce_kapsam", 3000),
               "capraz": getattr(args, "butce_capraz", 1800)}
    output = getattr(args, "output", None)

    def step(name: str, call):
        started = time.time()
        log(f"adım başladı: {name} (bütçe {budgets.get(name, '-')} sn)")
        # bütçe parçalar arasında kontrol edilir; tek bir takılan sorgu için güvenlik ağı: bütçe + 300 sn sonra DuckDB sorgusu kesilir
        watchdog = threading.Timer(budgets.get(name, 3600) + 300, con.interrupt)
        watchdog.daemon = True
        watchdog.start()
        try:
            result["adimlar"][name] = call()
        except Exception as exc:                                    # noqa: BLE001 — hata JSON'a yazılır, süreç sonunda kırmızı çıkar
            result["hatalar"][name] = f"{type(exc).__name__}: {exc}"[:500]
            log(f"adım HATA: {name}: {result['hatalar'][name]}")
        finally:
            watchdog.cancel()
        result.setdefault("sure_sn", {})[name] = round(time.time() - started, 1)
        log(f"adım bitti: {name} ({result['sure_sn'][name]} sn)")
        if output:                                                  # kısmi sonuç: koşu iptal olsa da o ana kadarki ölçümler dosyada kalır
            Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=1, allow_nan=False, default=str) + "\n", encoding="utf-8")

    columns: dict[str, list[dict[str, str]]] = {}
    files: dict[str, list[dict[str, Any]]] = {}

    def envanter():
        subsets = args.alt_kume or yeniden(kaynak.alt_kumeler)
        out: dict[str, Any] = {"alt_kume_sayisi": len(subsets), "alt_kumeler": subsets}
        started = time.time()
        for n, subset in enumerate(subsets):
            info: dict[str, Any] = {}
            log(f"envanter: {subset} ({n + 1}/{len(subsets)})")
            # kalan bütçe kalan alt kümelere eşit bölünür (en az 60 sn)
            deadline = time.time() + max(60.0, (budgets["envanter"] - (time.time() - started)) / (len(subsets) - n))
            try:
                tree = kaynak.agac(subset)
                files[subset] = parquet_dosyalari(tree)
                days = sorted({f["gun"] for f in files[subset] if f["gun"]})
                info.update(dosya=len(files[subset]), boyut_gb=round(sum(f["size"] for f in files[subset]) / 1e9, 2),
                            parquet_disi=uzantilar([r for r in tree if not r["path"].endswith(".parquet")]),
                            gun_sayisi=len(days), ilk=days[0] if days else None, son=days[-1] if days else None)
                if files[subset]:
                    urls = [kaynak.url(f["path"]) for f in files[subset]]
                    columns[subset] = info["sutunlar"] = yeniden(lambda: sutunlar(con, urls))
                    progress: dict[str, Any] = {}
                    info["satir"] = yeniden(lambda: satir_sayisi(con, urls, deadline, progress))
                    if progress["taranan_dosya"] < progress["toplam_dosya"]:
                        info["satir_kismi"] = progress          # bütçe doldu: satır yalnız taranan dosyalar için (alt sınır)
            except Exception as exc:                                # noqa: BLE001
                info["hata"] = f"{type(exc).__name__}: {exc}"[:300]
                result["hatalar"][f"envanter/{subset}"] = info["hata"]
            out[subset] = info
        try:
            out["_veri_karti"] = yeniden(kaynak.veri_karti)[:20000]
        except Exception as exc:                                    # noqa: BLE001
            result["hatalar"]["veri_karti"] = f"{type(exc).__name__}: {exc}"[:300]
        return out

    step("envanter", envanter)
    day_urls: dict[str, list[str]] = {}
    days: list[str] = []

    def kapsam():
        nonlocal days
        if ACCOUNT_SUBSET not in files:
            files[ACCOUNT_SUBSET] = parquet_dosyalari(yeniden(lambda: kaynak.agac(ACCOUNT_SUBSET)))
        for f in files[ACCOUNT_SUBSET]:
            if f["gun"]:
                day_urls.setdefault(f["gun"], []).append(kaynak.url(f["path"]))
        progress: dict[str, Any] = {}
        deadline = time.time() + budgets["kapsam"]
        rows = yeniden(lambda: gunluk_kapsam(con, day_urls, deadline, progress))
        days = [r["gun"] for r in rows]
        counts = [r["adres"] for r in rows]
        partial = {"kismi": progress} if progress["taranan_gun"] < progress["toplam_gun"] else {}
        return {**partial, "ilk": days[0], "son": days[-1], "gun_sayisi": len(days), "bosluklar": bosluklar(days),
                "adres_min": min(counts), "adres_medyan": statistics.median(counts), "adres_max": max(counts), "gunluk": rows}

    step("kapsam", kapsam)

    def capraz_dogrulama():
        if not days:
            raise RuntimeError("kapsam adımı gün listesi üretmedi")
        from copytrade.tarama import PublicClient
        return capraz(con, day_urls, client or PublicClient(), kapi_adresleri(args.root), days[-1], gecmis_tarihler(days[-1], days))

    step("capraz", capraz_dogrulama)
    found = ledger_adaylari(columns)
    step("ledger", lambda: {"aday_alt_kume_ve_sutunlar": found,
                            "sonuc": "var" if found else "yok: hiçbir alt küme/sütun adı yatırma-çekme-transfer içermiyor",
                            "taranan_alt_kume": sorted(columns)})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("copytrade"), help="kapı sonuçlarının kökü (copytrade/kapi/*/sonuc.csv)")
    parser.add_argument("--base", default=BASE, help="hf://… ya da yerel dizin (test)")
    parser.add_argument("--alt-kume", action="append", default=None, help="yalnız bu alt küme(ler)")
    parser.add_argument("--butce-envanter", type=int, default=2400, help="envanter adımı süre bütçesi (sn)")
    parser.add_argument("--butce-kapsam", type=int, default=3000, help="kapsam adımı süre bütçesi (sn)")
    parser.add_argument("--butce-capraz", type=int, default=1800, help="çapraz doğrulama süre bütçesi (sn; güvenlik ağı)")
    parser.add_argument("--output", type=Path, default=Path("hf_dogrulama.json"))
    args = parser.parse_args(argv)
    result = calistir(args)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1, allow_nan=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "adimlar"}, ensure_ascii=False, indent=1))
    return 1 if result["hatalar"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
