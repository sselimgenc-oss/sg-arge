"""Gecikmeli kopya mutabakatı (görev 13): tek adres için sonucun ayrıntılı dökümü.

Yalnız herkese açık Hyperliquid verisi (Actions'ta koşar). ``delayed_copy`` hesabını çalıştırır;
yanında üç şey gösterir: (1) saatlik mum yuvarlama aralığı (hedeften sonraki ilk mum = kapı, hedeften önceki son mum = karşı
sınır), (2) pencerede önceden açık pozisyonu azaltan dolumları yeni ters pozisyon saymayan güncel kapı hesabı (`kapi`) ile eski ham hesap (`ham`), (3) payda
seçenekleri. Kapı kuralları ve eşikler değişmez; bu bir tanılama raporudur.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from copytrade.izleme_motoru import copy_actions
from copytrade.kapi import SLIPPAGE, TAKER, CandleCache, delayed_copy
from copytrade.kurallar import load_rules
from copytrade.olcut import asset_class, closed_round_trips, perp_fills
from copytrade.tarama import PublicClient, RateLimiter

DAY = 86_400_000
DELAYS = (0, 30, 120, 480)


def funding_all(client: Any, address: str, start_ms: int, end_ms: int) -> list[dict]:
    """Tüm funding kayıtları: API sayfa başına en çok 500 döndürür; imleç son kayıttan ilerler (kapı tek sayfa okur)."""
    rows, cursor, seen = [], start_ms, set()
    while True:
        page = client.info({"type": "userFunding", "user": address, "startTime": cursor, "endTime": end_ms}, weight=20) or []
        fresh = [x for x in page if (x.get("time"), str(x.get("delta", {}).get("coin"))) not in seen]
        for item in fresh:
            seen.add((item.get("time"), str(item.get("delta", {}).get("coin"))))
        rows.extend(fresh)
        if len(page) < 500 or not fresh:
            return rows
        cursor = max(int(x["time"]) for x in page) + 1


def breakdown(fills: list[dict], candles: dict[str, list[dict]], account: float, delay: int, funding: list[dict],
              rounding: str = "up", corrected: bool = False) -> dict[str, Any]:
    """Bir gecikme/yuvarlama/düzeltme seçeneği için coin bazında brüt, maliyet, funding ve net (hesap payı olarak)."""
    used = copy_actions(sorted(perp_fills(fills), key=lambda x: int(x["time"]))) if corrected else perp_fills(fills)
    trace: list[dict] = []
    series, missing = delayed_copy(used, candles, account, delay, funding, rounding=rounding, trace=trace)
    coins: dict[str, dict[str, float]] = {}
    for row in trace:
        item = coins.setdefault(row["coin"], {"dolum": 0, "nominal": 0.0, "brut": 0.0, "maliyet": 0.0, "funding": 0.0})
        item["dolum"] += 1 if row["notional"] else 0
        item["nominal"] += row["notional"]
        item["brut"] += row["gross"]
        item["maliyet"] += row["cost"]
        item["funding"] += row["funding"]
    for item in coins.values():
        item["net"] = item["brut"] - item["maliyet"] + item["funding"]
    totals = {key: sum(c[key] for c in coins.values()) for key in ("dolum", "nominal", "brut", "maliyet", "funding", "net")}
    return {"toplam": totals, "coinler": coins, "eksik_dolum": missing, "net_seri": float(series.sum()) if series is not None else 0.0,
            "kopyalanan_dolum": len(used)}


def denominators(portfolio: list, since_ms: int, leaderboard_value: float | None, clearing_value: float | None) -> dict[str, float | None]:
    """Payda seçenekleri: lider tablosu (kapının kullandığı), güncel clearinghouse, penceredeki pozitif hesap değeri medyanı ve
    pencere başındaki ilk pozitif hesap değeri."""
    periods = {name: value for name, value in portfolio if isinstance(value, dict)} if portfolio else {}
    values = (periods.get("perpAllTime") or periods.get("allTime") or {}).get("accountValueHistory", [])
    window = [(int(t), float(v)) for t, v in values if int(t) >= since_ms and float(v) > 0]
    return {"lider_tablosu": leaderboard_value, "clearinghouse_guncel": clearing_value,
            "pencere_medyan": float(pd.Series([v for _, v in window]).median()) if window else None,
            "pencere_basi": window[0][1] if window else None}


def own_results(fills: list[dict], since_ms: int) -> dict[str, float]:
    """Liderin kendi gerçekleşen sonucu (``closedPnl`` − ücret) ve devir (nominal toplamı), pencere içi."""
    window = [f for f in perp_fills(fills) if int(f["time"]) >= since_ms]
    return {"closedPnl": sum(float(f.get("closedPnl", 0)) for f in window), "ucret": sum(float(f.get("fee", 0)) for f in window),
            "nominal": sum(abs(float(f.get("px", 0)) * float(f.get("sz", 0))) for f in window), "dolum": len(window)}


def pct(value: float | None, digits: int = 1) -> str:
    return "—" if value is None or not math.isfinite(value) else f"{100 * value:+.{digits}f}%".replace(".", ",")


def build_report(address: str, now: datetime, fills: list[dict], funding: list[dict], candles: dict[str, list[dict]],
                 portfolio: list, leaderboard_value: float | None, clearing_value: float | None,
                 windows_days: tuple[int, ...] = (200, 190), rules: dict | None = None) -> dict[str, Any]:
    rules = rules or load_rules()
    now_ms = int(now.timestamp() * 1000)
    base = leaderboard_value or clearing_value
    out: dict[str, Any] = {"adres": address, "uretildi": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "payda_kapi": base, "pencereler": {}}
    perp = perp_fills(fills)
    classes: dict[str, float] = {}
    for fill in perp:
        notional = abs(float(fill.get("px", 0)) * float(fill.get("sz", 0)))
        classes[asset_class(fill["coin"])] = classes.get(asset_class(fill["coin"]), 0.0) + notional
    total = sum(classes.values()) or 1.0
    out["varlik_sinifi_payi"] = {k: v / total for k, v in sorted(classes.items())}
    out["hip3_dahil"] = any(":" in str(f["coin"]) for f in perp)
    out["hip3_dex"] = sorted({str(f["coin"]).split(":")[0] for f in perp if ":" in str(f["coin"])})
    for days in windows_days:
        since = now_ms - days * DAY
        window = [f for f in fills if int(f["time"]) >= since]
        funding_w = [x for x in funding if int(x["time"]) >= since]
        trips = [t for t in closed_round_trips(perp_fills(window)) if t["close_time"] is not None]
        entry: dict[str, Any] = {
            "baslangic": datetime.fromtimestamp(since / 1000, UTC).strftime("%Y-%m-%d"),
            "ilk_dolum": datetime.fromtimestamp(min((int(f["time"]) for f in window), default=since) / 1000, UTC).strftime("%Y-%m-%d"),
            "dolum": len(perp_fills(window)), "kapanmis_dongu": len(trips), "funding_kaydi": len(funding_w),
            "coin_sayisi": len({f["coin"] for f in perp_fills(window)}),
            "lider": own_results(window, since), "paydalar": denominators(portfolio, since, leaderboard_value, clearing_value),
            "secenekler": {}}
        for delay in DELAYS:
            for corrected in (False, True):
                for rounding in (("up", "down") if delay else ("up",)):
                    key = f"{delay}dk|{'kapi' if corrected else 'ham'}|{rounding}"
                    entry["secenekler"][key] = breakdown(window, candles, base, delay, funding_w, rounding, corrected)
        out["pencereler"][str(days)] = entry
    return out


def render(report: dict[str, Any]) -> str:
    lines = [f"# Gecikmeli kopya mutabakatı — `{report['adres']}`", "", f"Üretildi: {report['uretildi']} · kapı paydası (lider tablosu hesap değeri): "
             f"{report['payda_kapi']:,.0f} $".replace(",", "."), "",
             "Net = brüt fiyat PnL − maliyet (taker %0,045 + kayma %0,05, her dolumda) + funding; hepsi **hesap değerine oranla**. "
             "`ham` = `delayed_copy`'nin pozisyonu pencere başında 0 sayan eski kullanımı; `kapi` = güncel kapı (pencere öncesinden gelen pozisyonu azaltan dolum yeni ters pozisyon sayılmaz, `copy_actions`). "
             "`up` = hedef zamandan sonraki ilk saatlik mum açılışı (kapının kullandığı), `down` = hedeften önceki son mum.", "",
             f"Varlık sınıfı payları (nominal): " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in report["varlik_sinifi_payi"].items()),
             f" · HIP-3 dahil: {'evet (' + ', '.join(report['hip3_dex']) + ')' if report['hip3_dahil'] else 'hayır'}", ""]
    for days, w in report["pencereler"].items():
        lines += [f"## Son {days} gün ({w['baslangic']} → bugün)", "",
                  f"- Dolum {w['dolum']}, kapanmış döngü {w['kapanmis_dongu']}, coin {w['coin_sayisi']}, funding kaydı {w['funding_kaydi']} (ilk dolum {w['ilk_dolum']})",
                  f"- Liderin kendi sonucu: closedPnl {w['lider']['closedPnl']:,.0f} $, ücret {w['lider']['ucret']:,.0f} $, devir {w['lider']['nominal']:,.0f} $ "
                  f"({w['lider']['dolum']} dolum)".replace(",", "."),
                  "- Paydalar: " + ", ".join(f"{k} {('—' if v is None else format(v, ',.0f').replace(',', '.'))}" for k, v in w["paydalar"].items()), "",
                  "| Seçenek | Brüt | Maliyet | Funding | **Net** | Devir (× hesap) | Eksik dolum |", "|---|---:|---:|---:|---:|---:|---:|"]
        for key, r in w["secenekler"].items():
            t = r["toplam"]
            lines.append(f"| {key} | {pct(t['brut'])} | {pct(-t['maliyet'])} | {pct(t['funding'])} | **{pct(t['net'])}** | {t['nominal']:.1f}× | {r['eksik_dolum']} |")
        base = report["payda_kapi"]
        lines += ["", "**Payda duyarlılığı** — 30 dk, up (net, hesap değerine oranla; net ∝ 1 / payda)", "",
                  "| Payda | Değer | Ham (eski) | Kapı (güncel) |", "|---|---:|---:|---:|"]
        for name, value in w["paydalar"].items():
            scale = (base / value) if value else None
            row = [pct(w["secenekler"][f"30dk|{kind}|up"]["toplam"]["net"] * scale) if scale else "—" for kind in ("ham", "kapi")]
            lines.append(f"| {name} | {'—' if value is None else format(value, ',.0f').replace(',', '.')} | {row[0]} | {row[1]} |")
        for title, key in (("Coin dökümü — 30 dk, ham (eski kapı hesabı), up", "30dk|ham|up"), ("Coin dökümü — 30 dk, kapı (güncel), up", "30dk|kapi|up")):
            coins = sorted(w["secenekler"][key]["coinler"].items(), key=lambda kv: -abs(kv[1]["net"]))[:15]
            lines += ["", f"**{title}** (|net|'e göre ilk 15)", "", "| Coin | Dolum | Brüt | Maliyet | Funding | Net |", "|---|---:|---:|---:|---:|---:|"]
            lines += [f"| {c} | {int(v['dolum'])} | {pct(v['brut'])} | {pct(-v['maliyet'])} | {pct(v['funding'])} | {pct(v['net'])} |" for c, v in coins]
        lines.append("")
    return "\n".join(lines) + "\n"


def run(address: str, output: Path, client: PublicClient | None = None, now: datetime | None = None) -> dict[str, Any]:
    client = client or PublicClient(limiter=RateLimiter(1000))
    now = now or datetime.now(UTC)
    now_ms = int(now.timestamp() * 1000)
    start = now_ms - int(load_rules()["fills_lookback_days"]) * DAY
    rows = client.leaderboard()
    leader = next((r for r in rows if str(r.get("ethAddress", r.get("address", ""))).lower() == address.lower()), None)
    leaderboard_value = float(leader.get("accountValue", 0)) if leader else None
    state = client.info({"type": "clearinghouseState", "user": address}, weight=2)
    clearing = float(state["marginSummary"]["accountValue"]) if isinstance(state, dict) and "marginSummary" in state else None
    fills = client.fills(address, start)
    funding = funding_all(client, address, start, now_ms)
    cache = CandleCache(client, now_ms - 200 * DAY, now_ms)
    candles = cache.for_fills([f for f in fills if int(f["time"]) >= now_ms - 200 * DAY])
    report = build_report(address, now, fills, funding, candles, client.portfolio(address), leaderboard_value, clearing)
    output.mkdir(parents=True, exist_ok=True)
    stem = address.lower()[:8]
    (output / f"{stem}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, allow_nan=False), encoding="utf-8")
    text = render(report)
    (output / f"{stem}.md").write_text(text, encoding="utf-8")
    print(text, flush=True)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adres", required=True)
    parser.add_argument("--output", type=Path, default=Path("mutabakat"))
    args = parser.parse_args(argv)
    run(args.adres, args.output)


if __name__ == "__main__":
    main()
