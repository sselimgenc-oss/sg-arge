"""Pilot veri hattı: arşivden ``haftalik_rapor`` girdileri (``docs/GOREV_PILOT_VERI.md``).

Üç JSON üretir (``haftalik_rapor`` biçiminde): ``getiri.json`` ({adres: ileri getiri}), ``kapanmis_islem.json`` ({adres: sayı}),
``risk.json`` ({adres: {etiket, son}}; yalnız oda üyeleri). Yöntem, kapı ve eşik değişmez: getiri ``golge.calistir`` (V0) → ``defter.copy_ledger``.

**Körlük (ön kayıt madde 6):** hiçbir çıktıda ya da günlükte kol bazında getiri yoktur. Adres başına ileri getiri yalnız ``getiri.json``'a yazılır
(``haftalik_rapor``'un puan ↔ ileri getiri bölümü okur). Günlük satırları yalnız sayı (adres/eksik/dolum) taşır.
Boşluk: arşivin ilk yoklamasından önceki aralık (etiket → ilk yoklama) **bir kez** ``--bosluk-doldur`` ile API'den arşive yazılır; haftalık koşu
API'ye gitmez, yalnız arşivi okur. API yalnız son ``api_dolum_pencere_siniri`` dolumu verir: pencere dolup en eski dolum etiketten sonraysa adres
``pencere_disi`` (eksik) yazılır ve haftalık koşuda getiriden çıkar; sessiz sıfır yoktur.
"""
from __future__ import annotations

import argparse
import json
import time
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


def oku(root: Path, kind: str, *, gun_baslangic: str | None = None, adresler: set[str] | None = None) -> list[dict]:
    """``tur=<kind>/gun=*/parca-*.parquet`` satırları (``veri`` JSON'u açılır), tekilleştirilir. ``gun_baslangic`` (YYYY-MM-DD) öncesi günler okunmaz;
    ``adresler`` verilirse JSON açılmadan önce metin süzgeciyle yalnız o adresler okunur (sütun bazlı, ``iterrows`` yok)."""
    rows: dict[str, dict] = {}
    pattern = "|".join(sorted(a.lower() for a in adresler)) if adresler else None
    for part in sorted((Path(root) / f"tur={kind}").glob("gun=*/parca-*.parquet")):
        if gun_baslangic and part.parent.name.removeprefix("gun=") < gun_baslangic:
            continue
        frame = pd.read_parquet(part, columns=["_anahtar", "veri"])
        if pattern is not None:
            frame = frame[frame["veri"].str.lower().str.contains(pattern, regex=True)]
        for key, raw in zip(frame["_anahtar"].tolist(), frame["veri"].tolist()):
            row = json.loads(raw)
            rows.setdefault(_anahtar(kind, row, str(key)), row)
    return list(rows.values())


def _anahtar(kind: str, row: dict, stored: str) -> str:
    """Eski mum satırlarının ``_anahtar``ı coin içermiyordu (``None:<t>``): coin'ler birbirini ezmesin diye mumda anahtar içerikten kurulur."""
    if kind in {"mum_1dk", "mum_1sa"}:
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


def adres_verisi(adres: str, dolum: list[dict], funding: list[dict]) -> tuple[list[dict], list[dict]]:
    mine = [r for r in dolum if str(r.get("adres", "")).lower() == adres]
    fund = [r for r in funding if str(r.get("adres", "")).lower() == adres]
    return perp_fills(sorted(mine, key=lambda r: int(r["time"]))), fund


def mumlar(arsiv_dk: list[dict], arsiv_sa: list[dict]) -> dict[str, list[dict]]:
    """Saatlik mum: 1 dk arşivinden türetilen saatler öncelikli; boşluk dolumunun saatlik mumları (``mum_1sa``) yalnız eksik saatleri tamamlar."""
    out = saatlik(arsiv_dk)
    for coin, rows in saatlik(arsiv_sa).items():
        have = {c["t"] for c in out.get(coin, [])}
        extra = [c for c in rows if c["t"] not in have]
        if extra:
            out[coin] = sorted(out.get(coin, []) + extra, key=lambda c: c["t"])
    return out


def bosluk_yolu(root: Path) -> Path:
    return Path(root) / "tur=bosluk" / "bosluk.json"


def bosluk_doldur(arsiv_root: Path, result: dict, client, *, now: datetime | None = None, rules: dict | None = None) -> dict:
    """Etiketten arşivin ilk yoklamasına kadar olan aralığı API'den arşive yazar (TEK SEFER; haftalık koşu API'ye gitmez).
    Dolum penceresi dolup (``api_dolum_pencere_siniri``) en eski dolum etiketten sonraysa adres ``pencere_disi`` olarak kaydedilir ve günlüğe yazılır."""
    from copytrade.arsiv import Arsiv
    rules = rules or load_rules()
    now = now or datetime.now(UTC)
    etiket_ms = ms(result["tarih"])
    sinir = bosluk_baslangici(arsiv_root)
    if sinir is None:
        raise RuntimeError("Arşivde dolum yoklaması yok: boşluk sınırı belirlenemedi (arşiv hiç koşmamış).")
    kayit = {"etiket_ms": etiket_ms, "sinir_ms": sinir, "pencere_disi": [], "adres": 0, "dolum": 0, "funding": 0, "mum_1sa": 0}
    limit = int(rules["api_dolum_pencere_siniri"])
    archive = Arsiv(arsiv_root, now)
    addresses = sorted({a.lower() for a, e in result["adresler"].items() if _uye(e) or "oda" in e.get("kollar", [])})
    coins: set[str] = set()
    if sinir > etiket_ms:
        for adres in addresses:
            fills = [dict(r, adres=adres) for r in client.fills(adres, etiket_ms, end_ms=sinir)]
            if len(fills) >= limit and min(int(r["time"]) for r in fills) > etiket_ms:
                kayit["pencere_disi"].append(adres)
                print(f"UYARI pencere dışı: {adres[:6]}…{adres[-4:]} (API son {limit} dolumu verdi; boşluğun başı erişilemez)")
            fund = [dict(r, adres=adres) for r in client.info({"type": "userFunding", "user": adres, "startTime": etiket_ms, "endTime": sinir}) if "time" in r]
            kayit["dolum"] += archive.append("dolum", fills)
            kayit["funding"] += archive.append("funding", fund)
            coins.update(str(r["coin"]) for r in fills if r.get("coin"))
            kayit["adres"] += 1
        for coin in sorted(coins):
            rows = [dict(c, coin=coin) for c in client.candles(coin, etiket_ms // HOUR * HOUR, sinir, "1h") if int(c["t"]) < sinir]
            kayit["mum_1sa"] += archive.append("mum_1sa", rows)
    path = bosluk_yolu(arsiv_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(kayit, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return {k: (len(v) if isinstance(v, list) else v) for k, v in kayit.items()}


def bosluk_kontrol(arsiv_root: Path, etiket_ms: int) -> set[str]:
    """Haftalık koşu: arşiv etiketten sonra başladıysa boşluk dolumu yapılmış olmalı; yoksa koşu KIRMIZI biter. ``pencere_disi`` adresleri döner."""
    sinir = bosluk_baslangici(arsiv_root)
    if sinir is None:
        raise RuntimeError("Arşivde dolum yoklaması yok: getiri hesaplanamaz.")
    if sinir <= etiket_ms:
        return set()
    path = bosluk_yolu(arsiv_root)
    if not path.exists():
        raise RuntimeError("Arşiv etiketten sonra başladı ve boşluk doldurulmadı: önce `python -m copytrade.pilot_veri --bosluk-doldur` çalıştırın.")
    kayit = json.loads(path.read_text(encoding="utf-8"))
    return {a.lower() for a in kayit.get("pencere_disi", [])}


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


def uret(arsiv_root: Path, result: dict, bayrak: dict, tarih: str, cikti: Path, *, now: datetime | None = None,
         rules: dict | None = None) -> dict[str, int]:
    """Yalnız arşivi okur (API yok). Süre ve satır sayıları ``cikti/ozet.json``'a yazılır (kol bazında getiri yok)."""
    baslangic = time.monotonic()
    rules = rules or load_rules()
    now = now or datetime.now(UTC)
    etiket_ms = ms(result["tarih"])
    end_ms = min(int(now.timestamp() * 1000), ms(tarih) + DAY - 1)
    pencere_disi = bosluk_kontrol(arsiv_root, etiket_ms)
    members = {a.lower(): e for a, e in result["adresler"].items() if _uye(e)}
    oda = {a.lower(): e for a, e in result["adresler"].items() if "oda" in e.get("kollar", [])}
    week_day = datetime.fromtimestamp((end_ms - int(rules["onkayit_blok_gun"]) * DAY) / 1000, UTC).date().isoformat()
    dolum = oku(arsiv_root, "dolum", gun_baslangic=result["tarih"])
    funding = oku(arsiv_root, "funding", gun_baslangic=result["tarih"])
    mum = oku(arsiv_root, "mum_1dk", gun_baslangic=result["tarih"])
    mum_sa = oku(arsiv_root, "mum_1sa")
    pozisyon = oku(arsiv_root, "pozisyon", gun_baslangic=week_day, adresler=set(oda))
    data = {a: adres_verisi(a, dolum, funding) for a in sorted(set(members) | set(oda))}
    candles = mumlar(mum, mum_sa)
    ileri, kapanmis, riskler, eksik = {}, {}, {}, 0
    for adres in sorted(members):
        fills, fund = data[adres]
        value, miss, total = (None, 0, 0) if adres in pencere_disi else getiri(fills, fund, candles, members[adres], etiket_ms, end_ms, rules)
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
    sonuc = {"havuz": len(members), "getiri": len(ileri), "eksik": eksik, "pencere_disi": len(pencere_disi & set(members)), "oda_risk": len(riskler)}
    ozet = dict(sonuc, sure_sn=round(time.monotonic() - baslangic, 1), satir={"dolum": len(dolum), "funding": len(funding), "mum_1dk": len(mum), "pozisyon": len(pozisyon)})
    (cikti / "ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return sonuc


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arsiv", type=Path, required=True, help="R2'den indirilmiş arşiv kökü (tur=*/gun=*/parca-*.parquet)")
    parser.add_argument("--secim", type=Path, required=True)
    parser.add_argument("--bayrak", type=Path, default=None)
    parser.add_argument("--tarih", help="hafta etiketi (YYYY-MM-DD); haftalık koşuda zorunlu")
    parser.add_argument("--cikti", type=Path, default=Path("pilot_veri"))
    parser.add_argument("--bosluk-doldur", action="store_true", help="TEK SEFER: etiket → arşivin ilk yoklaması aralığını API'den arşive yaz (haftalık koşu API'ye gitmez)")
    args = parser.parse_args(argv)
    result = json.loads(args.secim.read_text(encoding="utf-8"))
    if args.bosluk_doldur:
        from copytrade.tarama import PublicClient
        print(bosluk_doldur(args.arsiv, result, PublicClient()))
        return
    if not args.tarih:
        parser.error("--tarih gerekir")
    bayrak = json.loads(args.bayrak.read_text(encoding="utf-8")) if args.bayrak and args.bayrak.exists() else {}
    print(uret(args.arsiv, result, bayrak, args.tarih, args.cikti))


if __name__ == "__main__":
    main()
