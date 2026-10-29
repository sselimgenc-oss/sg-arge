"""Pilot veri hattı: arşivden ``haftalik_rapor`` girdileri (``docs/GOREV_PILOT_VERI.md``).

Üç JSON üretir (``haftalik_rapor`` biçiminde): ``getiri.json`` ({adres: ileri getiri}), ``kapanmis_islem.json`` ({adres: sayı}),
``risk.json`` ({adres: {etiket, son}}; yalnız oda üyeleri). Yöntem, kapı ve eşik değişmez: getiri ``golge.calistir`` (V0) → ``defter.copy_ledger``.

**Körlük (ön kayıt madde 6):** hiçbir çıktıda ya da günlükte kol bazında getiri yoktur. Adres başına ileri getiri yalnız ``getiri.json``'a yazılır
(``haftalik_rapor``'un puan ↔ ileri getiri bölümü okur). Günlük satırları yalnız sayı (adres/eksik/dolum) taşır.
Boşluk: arşiv ilk koşusundan (``son.json`` imleçleri) önceki dolum/funding/saatlik mumlar API'den tamamlanır (``bosluk_baslangici``).
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from copytrade import analiz_d, golge, risk_isaretleri
from copytrade.kurallar import load_rules
from copytrade.olcut import closed_round_trips, perp_fills

HOUR = 3_600_000
DAY = 24 * HOUR


def ms(day: str) -> int:
    return int(datetime.fromisoformat(day).replace(tzinfo=UTC).timestamp() * 1000)


def oku(root: Path, kind: str) -> list[dict]:
    """``tur=<kind>/gun=*/parca-*.parquet`` satırları (``veri`` JSON'u açılır), ``_anahtar``a göre tekilleştirilir."""
    rows: dict[str, dict] = {}
    for part in sorted((Path(root) / f"tur={kind}").glob("gun=*/parca-*.parquet")):
        for _, item in pd.read_parquet(part).iterrows():
            row = json.loads(item["veri"])
            rows.setdefault(_anahtar(kind, row, str(item["_anahtar"])), row)
    return list(rows.values())


def _anahtar(kind: str, row: dict, stored: str) -> str:
    """Eski mum satırlarının ``_anahtar``ı coin içermiyordu (``None:<t>``): coin'ler birbirini ezmesin diye mumda anahtar içerikten kurulur."""
    if kind == "mum_1dk":
        return f"{row.get('coin', row.get('s'))}:{row.get('t')}"
    return stored


def bosluk_baslangici(root: Path) -> int | None:
    """Arşivin ilk başarılı dolum/funding yoklaması: bundan önceki aralık API'den tamamlanır. Hiç yoklama yoksa ``None`` (hepsi API)."""
    times = []
    for path in (Path(root) / "tur=kapsam").glob("gun=*/yoklamalar.json"):
        times += [int(p["zaman_ms"]) for p in json.loads(path.read_text()) if p.get("tur") in {"dolum", "funding"}]
    return min(times) if times else None


def saatlik(mumlar: list[dict]) -> dict[str, list[dict]]:
    """1 dk arşiv mumları → saatlik mum (açılış = saatin ilk dakikası). :00 dakikası yoksa o saat üretilmez (uydurulmaz, yürütme eksik sayılır)."""
    by: dict[tuple[str, int], list[dict]] = {}
    for row in mumlar:
        by.setdefault((str(row["coin"] if "coin" in row else row.get("s")), int(row["t"]) // HOUR * HOUR), []).append(row)
    out: dict[str, list[dict]] = {}
    for (coin, hour), rows in sorted(by.items()):
        rows.sort(key=lambda r: int(r["t"]))
        if int(rows[0]["t"]) != hour:
            continue
        out.setdefault(coin, []).append({"t": hour, "o": float(rows[0]["o"]), "h": max(float(r["h"]) for r in rows),
                                         "l": min(float(r["l"]) for r in rows), "c": float(rows[-1]["c"])})
    return out


def _tid(row: dict) -> str:
    return str(row.get("tid", row.get("hash", row.get("time"))))


def birlestir(arsiv: list[dict], api: list[dict], sinir: int | None) -> list[dict]:
    """Arşiv + (``sinir``dan önceki) API satırları; ``tid``/``hash``/zaman tekilleştirmesi. Arşiv öncelikli."""
    seen, out = set(), []
    for row in arsiv + [r for r in api if sinir is not None and int(r["time"]) < sinir]:
        key = (str(row.get("coin")), int(row["time"]), _tid(row))
        if key not in seen:
            seen.add(key)
            out.append(row)
    return sorted(out, key=lambda r: int(r["time"]))


def adres_verisi(adres: str, etiket_ms: int, dolum: list[dict], funding: list[dict], client, sinir: int | None) -> tuple[list[dict], list[dict]]:
    mine = [r for r in dolum if str(r.get("adres", "")).lower() == adres]
    fund = [r for r in funding if str(r.get("adres", "")).lower() == adres]
    if client is not None and (sinir is None or sinir > etiket_ms):
        end = sinir if sinir is not None else None
        mine = birlestir(mine, [r for r in client.fills(adres, etiket_ms)], end if end is not None else 1 << 62)
        fund = birlestir(fund, [r for r in client.info({"type": "userFunding", "user": adres, "startTime": etiket_ms}) if "time" in r],
                         end if end is not None else 1 << 62)
    return perp_fills(sorted(mine, key=lambda r: int(r["time"]))), fund


def mumlar(coins: set[str], arsiv_mum: list[dict], client, etiket_ms: int, sinir: int | None) -> dict[str, list[dict]]:
    out = saatlik(arsiv_mum)
    if client is not None and (sinir is None or sinir > etiket_ms):
        end = (sinir if sinir is not None else int(datetime.now(UTC).timestamp() * 1000))
        for coin in sorted(coins):
            have = {c["t"] for c in out.get(coin, [])}
            rows = [{"t": int(c["t"]), "o": float(c["o"]), "h": float(c["h"]), "l": float(c["l"]), "c": float(c["c"])}
                    for c in client.candles(coin, etiket_ms // HOUR * HOUR, end, "1h") if int(c["t"]) not in have and int(c["t"]) < end]
            if rows:
                out[coin] = sorted(out.get(coin, []) + rows, key=lambda c: c["t"])
    return out


def _uye(entry: dict) -> bool:
    return entry.get("puan") is not None and "havuz" in entry.get("kollar", [])


def getiri(fills: list[dict], funding: list[dict], candles: dict[str, list[dict]], entry: dict, etiket_ms: int, end_ms: int,
           rules: dict) -> tuple[float | None, int, int]:
    """(ileri getiri | None, eksik dolum, toplam dolum). Dolumu olmayan (pasif) adres 0,0 getirilidir ve veri eksik sayılmaz."""
    if not [f for f in fills if int(f["time"]) >= etiket_ms]:
        return 0.0, 0, 0
    account = entry.get("hesap_degeri")
    if account is None or float(account) <= 0:
        return None, 0, 1
    coins = {str(f["coin"]) for f in fills}
    out = golge.calistir(fills, {c: candles.get(c, []) for c in coins}, float(account), style=entry.get("tarz") or "intraday",
                         etiket_ms=etiket_ms, end_ms=end_ms, funding=funding, variant="V0", rules=rules)
    ledger = out["defter"]
    missing, total = int(ledger.get("missing", 0)), int(ledger.get("missing", 0)) + int(ledger.get("executed", 0))
    if ledger.get("net") is None or analiz_d.veri_eksik(missing, total, rules):
        return None, missing, total
    return float(ledger["net"]), missing, total


def kapanmis_islem(fills: list[dict], etiket_ms: int) -> int:
    since = [f for f in fills if int(f["time"]) >= etiket_ms]
    return sum(1 for t in closed_round_trips(since) if int(t["close_time"].value // 1_000_000) >= etiket_ms)


def _son_durum(pozisyon: list[dict], adres: str, end_ms: int) -> dict | None:
    rows = [r for r in pozisyon if str(r.get("adres", "")).lower() == adres and isinstance(r.get("durum"), dict) and int(r.get("alindi_ms", 0)) <= end_ms]
    return max(rows, key=lambda r: int(r["alindi_ms"])) if rows else None


def _kaldirac(durum: dict) -> float | None:
    summary = durum.get("marginSummary") or {}
    value, notional = float(summary.get("accountValue", 0) or 0), float(summary.get("totalNtlPos", 0) or 0)
    return notional / value if value > 0 else None


def risk(adres: str, entry: dict, bayrak: dict, fills: list[dict], pozisyon: list[dict], end_ms: int, rules: dict) -> dict:
    """``risk_isaretleri.uye_isaretleri`` girdisi. Veri yoksa alan eksik bırakılır (işaret ``None`` olur, uydurulmaz)."""
    week_start = end_ms - int(rules["onkayit_blok_gun"]) * DAY
    etiket = {"medyan_kaldirac": entry.get("medyan_kaldirac"), "katlama_orani": (bayrak or {}).get("bayrak_katlama_orani"),
              "medyan_tutma_saat": entry.get("medyan_tutma_saat")}
    son: dict[str, Any] = {"dolumlar": fills, "hafta_baslangic_ms": week_start}
    snaps = [r for r in pozisyon if str(r.get("adres", "")).lower() == adres and isinstance(r.get("durum"), dict)
             and week_start <= int(r.get("alindi_ms", 0)) <= end_ms]
    levs = [x for x in (_kaldirac(r["durum"]) for r in snaps) if x is not None]
    if levs:
        son["en_yuksek_kaldirac"] = max(levs)
    last = _son_durum(pozisyon, adres, end_ms)
    if last:
        ages = []
        for item in last["durum"].get("assetPositions", []):
            position = item.get("position", {})
            if float(position.get("unrealizedPnl", 0) or 0) < 0:
                opened = [int(f["time"]) for f in fills if f["coin"] == position.get("coin") and float(f.get("startPosition", 0)) == 0]
                if opened:
                    ages.append((int(last["alindi_ms"]) - max(opened)) / HOUR)
        son["zarardaki_acik_yaslar_saat"] = ages
    return {"etiket": {k: v for k, v in etiket.items() if v is not None}, "son": son}


def uret(arsiv_root: Path, result: dict, bayrak: dict, tarih: str, cikti: Path, *, client=None, now: datetime | None = None,
         rules: dict | None = None) -> dict[str, int]:
    rules = rules or load_rules()
    now = now or datetime.now(UTC)
    etiket_ms = ms(result["tarih"])
    end_ms = min(int(now.timestamp() * 1000), ms(tarih) + DAY - 1)
    sinir = bosluk_baslangici(arsiv_root)
    dolum, funding, mum, pozisyon = (oku(arsiv_root, k) for k in ("dolum", "funding", "mum_1dk", "pozisyon"))
    members = {a.lower(): e for a, e in result["adresler"].items() if _uye(e)}
    oda = {a.lower(): e for a, e in result["adresler"].items() if "oda" in e.get("kollar", [])}
    data = {a: adres_verisi(a, etiket_ms, dolum, funding, client, sinir) for a in sorted(set(members) | set(oda))}
    coins = {str(f["coin"]) for fills, _ in data.values() for f in fills}
    candles = mumlar(coins, mum, client, etiket_ms, sinir)
    ileri, kapanmis, riskler, eksik = {}, {}, {}, 0
    for adres in sorted(members):
        fills, fund = data[adres]
        value, miss, total = getiri(fills, fund, candles, members[adres], etiket_ms, end_ms, rules)
        if value is None:
            eksik += 1
        else:
            ileri[adres] = value
        kapanmis[adres] = kapanmis_islem(fills, etiket_ms)
    bay = (bayrak or {}).get("bayraklar", {})
    for adres in sorted(oda):
        riskler[adres] = risk(adres, oda[adres], bay.get(adres, {}), [f for f in data[adres][0] if int(f["time"]) >= etiket_ms], pozisyon, end_ms, rules)
    cikti.mkdir(parents=True, exist_ok=True)
    for name, value in (("getiri", ileri), ("kapanmis_islem", kapanmis), ("risk", riskler)):
        (cikti / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True, default=str), encoding="utf-8")
    return {"havuz": len(members), "getiri": len(ileri), "eksik": eksik, "oda_risk": len(riskler)}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arsiv", type=Path, required=True, help="R2'den indirilmiş arşiv kökü (tur=*/gun=*/parca-*.parquet)")
    parser.add_argument("--secim", type=Path, required=True)
    parser.add_argument("--bayrak", type=Path, default=None)
    parser.add_argument("--tarih", required=True)
    parser.add_argument("--cikti", type=Path, default=Path("pilot_veri"))
    parser.add_argument("--api-yok", action="store_true", help="boşluğu API'den tamamlama (varsayılan: tamamlar)")
    args = parser.parse_args(argv)
    result = json.loads(args.secim.read_text(encoding="utf-8"))
    bayrak = json.loads(args.bayrak.read_text(encoding="utf-8")) if args.bayrak and args.bayrak.exists() else {}
    client = None
    if not args.api_yok:
        from copytrade.tarama import PublicClient
        client = PublicClient()
    print(uret(args.arsiv, result, bayrak, args.tarih, args.cikti, client=client))


if __name__ == "__main__":
    main()
