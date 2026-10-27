"""Tek seferlik örnek inceleme: lider tablosundan birkaç trader'ın 365 günlük geçmişini okunur bir rapora döker.

Yalnız herkese açık veri okunur; emir, anahtar, cüzdan yok. Kural motoru ve ölçütler mevcut koddan.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from copytrade.kurallar import evaluate, load_rules
import traceback

from copytrade.olcut import _funding_amount, asset_class, calculate_metrics, perp_fills
from copytrade.tarama import PublicClient, _window

LIQUID = {"BTC", "ETH", "SOL", "HYPE", "XRP", "DOGE", "ADA", "AVAX", "LINK", "SUI", "LTC", "BCH", "PEPE", "WIF", "AAVE",
          "CRV", "ARB", "OP", "APT", "INJ"}


def pick(rows: list[dict], count: int, min_account: float = 100_000) -> list[dict]:
    """Hesabı büyük, aylık ve tüm zaman ROI'si pozitif; tüm zaman PnL / hesap değerine göre ilk ``count``."""
    chosen = []
    for row in rows:
        account = float(row.get("accountValue", 0) or 0)
        if account >= min_account and _window(row, "month", "roi") > 0 and _window(row, "allTime", "roi") > 0:
            chosen.append(dict(row, address=str(row.get("ethAddress", "")), accountValue=account))
    return sorted(chosen, key=lambda r: _window(r, "allTime", "pnl") / r["accountValue"], reverse=True)[:count]


def stable_pool(rows: list[dict], count: int) -> list[dict]:
    """İstikrar havuzu: hesap ≥ 50.000 USD; hafta, ay ve tüm zaman ROI > 0; tüm zaman ROI %20–%500 (piyango
    kazananlarını dışarıda bırakır); aylık hacim / hesap 0,5–20 kat (swing devir hızı; botlar ve scalp dışarıda);
    tüm zaman PnL'e göre ilk ``count`` adres."""
    pool = []
    for row in rows:
        account = float(row.get("accountValue", 0) or 0)
        roi_all = _window(row, "allTime", "roi")
        if (account >= 50_000 and _window(row, "week", "roi") > 0 and _window(row, "month", "roi") > 0
                and 0.2 <= roi_all <= 5 and 0.5 <= _window(row, "month", "vlm") / account <= 20):
            pool.append(dict(row, address=str(row.get("ethAddress", "")), accountValue=account))
    return sorted(pool, key=lambda r: _window(r, "allTime", "pnl"), reverse=True)[:count]


def monthly(fills: list[dict], funding: list[dict]) -> pd.Series:
    """Ay ay gerçekleşmiş net PnL (closedPnl − fee + funding), USD."""
    rows = [(int(f["time"]), float(f.get("closedPnl", 0)) - float(f.get("fee", 0))) for f in fills]
    rows += [(int(x["time"]), _funding_amount(x)) for x in funding]
    if not rows:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(rows, columns=["time", "pnl"])
    frame["ay"] = pd.to_datetime(frame.time, unit="ms", utc=True).dt.strftime("%Y-%m")
    return frame.groupby("ay").pnl.sum()


def section(row: dict, fills: list[dict], funding: list[dict], state: dict, rules: dict, metrics: dict | None = None) -> str:
    address, account = row["address"], row["accountValue"]
    positions = [x.get("position", {}) for x in state.get("assetPositions", [])]
    leverage = [float(p.get("leverage", {}).get("value", 0)) for p in positions]
    metrics = metrics or calculate_metrics(fills, funding=funding, liquid_coins=LIQUID, leverages=leverage, account_value=account,
                                martingale_max_ratio=float(rules["martingale_max_ratio"]),
                                martingale_min_additions=int(rules["martingale_min_additions"]))
    decision, reason = evaluate(metrics, rules)
    metrics = {k: (float("nan") if v is None else v) for k, v in metrics.items()}  # rapor biçimi için
    by_month = monthly(perp_fills(fills), funding)
    coins = pd.Series([f.get("coin") for f in fills]).value_counts(normalize=True).head(5) if fills else pd.Series(dtype=float)
    volume = pd.Series({}, dtype=float)
    if fills:
        frame = pd.DataFrame({"sinif": [asset_class(f.get("coin", "")) for f in fills],
                              "hacim": [abs(float(f.get("px", 0)) * float(f.get("sz", 0))) for f in fills]})
        volume = frame.groupby("sinif").hacim.sum() / max(frame.hacim.sum(), 1e-9)
    first = pd.to_datetime(min(int(f["time"]) for f in fills), unit="ms", utc=True).date() if fills else "—"
    lines = [f"## `{address}`",
             f"- Hesap değeri: {account:,.0f} USD · lider tablosu tüm zaman PnL {_window(row, 'allTime', 'pnl'):,.0f} USD, "
             f"ROI %{_window(row, 'allTime', 'roi') * 100:.0f} · aylık ROI %{_window(row, 'month', 'roi') * 100:.1f}",
             f"- Okunan fill: {len(fills)} (ilk: {first}){' — API sınırı (10.000) dolmuş olabilir' if len(fills) >= 10000 else ''}",
             f"- Kapanmış işlem: {metrics.get('closed_trades')} · kârlı ay oranı: {metrics.get('profitable_month_ratio', float('nan')):.0%} · "
             f"Sortino {metrics.get('sortino', float('nan')):.2f} · Calmar {metrics.get('calmar', float('nan')):.2f}",
             f"- En büyük işlemin kâr payı: {metrics.get('largest_trade_share', float('nan')):.0%} · en iyi işlem çıkınca PF "
             f"{metrics.get('profit_factor_without_best', float('nan')):.2f}",
             f"- Medyan tutma: {metrics.get('median_holding_hours', float('nan')):.1f} saat · açık pozisyon kaldıracı medyan/en yüksek: "
             f"{metrics.get('median_leverage', float('nan'))}/{metrics.get('max_leverage', float('nan'))}",
             f"- Martingale işareti: {'VAR' if metrics.get('martingale_signal') else 'yok'} "
             f"(zarara ekleme oranı {metrics.get('martingale_ratio', float('nan')):.0%}, {metrics.get('martingale_additions', 0)} ekleme)",
             f"- Coin dağılımı (fill sayısıyla): " + ", ".join(f"{c} %{v * 100:.0f}" for c, v in coins.items()),
             f"- Varlık sınıfı (hacim): " + ", ".join(f"{k} %{v * 100:.0f}" for k, v in volume.sort_values(ascending=False).items()),
             f"- Açık pozisyon: {len(positions)}",
             f"- **Kural sonucu: {decision}**" + (f" — {reason}" if reason else ""),
             "", "| Ay | Gerçekleşmiş net PnL (USD) |", "|---|---:|"]
    lines += [f"| {ay} | {v:,.0f} |" for ay, v in by_month.items()]
    return "\n".join(lines) + "\n"


def metrics_for(row: dict, fills: list[dict], funding: list[dict], state: dict, rules: dict) -> dict:
    positions = [x.get("position", {}) for x in state.get("assetPositions", [])]
    leverage = [float(p.get("leverage", {}).get("value", 0)) for p in positions]
    return calculate_metrics(fills, funding=funding, liquid_coins=LIQUID, leverages=leverage, account_value=row["accountValue"],
                             martingale_max_ratio=float(rules["martingale_max_ratio"]),
                             martingale_min_additions=int(rules["martingale_min_additions"]))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adet", type=int, default=8)
    parser.add_argument("--mod", choices=["kar", "istikrar"], default="kar")
    parser.add_argument("--havuz", type=int, default=60)
    parser.add_argument("--en-cok-dolum", type=int, default=6000)
    parser.add_argument("--cikti", default="copytrade/inceleme/RAPOR.md")
    args = parser.parse_args(argv)
    client, rules = PublicClient(), load_rules()
    board = client.leaderboard()
    leaders = pick(board, args.adet) if args.mod == "kar" else stable_pool(board, args.havuz)
    start = int((datetime.now(UTC) - timedelta(days=365)).timestamp() * 1000)
    loaded, errors, scalp = [], [], []
    for number, row in enumerate(leaders, 1):
        try:
            fills = client.fills(row["address"], start, max_rows=args.en_cok_dolum) if args.mod == "istikrar" else client.fills(row["address"], start)
            if args.mod == "istikrar" and len(fills) >= args.en_cok_dolum:
                scalp.append(row["address"])  # yılda bu kadar dolum swing değil; ayrıntı çekilmez
                continue
            funding = client.info({"type": "userFunding", "user": row["address"], "startTime": start}) or []
            state = client.info({"type": "clearinghouseState", "user": row["address"]}, weight=2) or {}
            loaded.append((row, fills, funding, state, metrics_for(row, fills, funding, state, rules)))
        except Exception:  # tek adresin hatası raporu durdurmaz
            errors.append(f"- `{row['address']}`: {traceback.format_exc().strip().splitlines()[-1]}")
        finally:
            write_report(args, board, leaders, loaded, errors, scalp, rules, number)


def write_report(args, board, leaders, loaded, errors, scalp, rules, done: int) -> None:
    """Her adresten sonra yeniden yazılır: koşu süre sınırına takılsa da o ana kadarki sonuç kalır."""
    parts = [f"# Örnek trader incelemesi — {args.mod} ({datetime.now(UTC).date()})", "",
             f"İşlenen adres: {done}/{len(leaders)}" + (" (tamamlandı)" if done == len(leaders) else " (koşu sürüyor ya da kesildi)"), ""]
    if args.mod == "kar":
        parts.append(f"Lider tablosunda {len(board)} adres. Seçim: hesap ≥ 100.000 USD, aylık ve tüm zaman ROI > 0; "
                     f"tüm zaman PnL / hesap değerine göre ilk {len(leaders)}.")
        shown = loaded
    else:
        swing = [x for x in loaded if (x[4].get("median_holding_hours") or 0) >= 4]
        calm = [x for x in swing if not x[4].get("martingale_signal") and (x[4].get("median_leverage") or 0) <= 5]
        enough = [x for x in calm if x[4].get("history_days", 0) >= 180 and x[4].get("closed_trades", 0) >= 20]
        shown = sorted(enough or calm, key=lambda x: (x[4].get("profitable_month_ratio") or 0, x[4].get("sortino") or 0),
                       reverse=True)[:args.adet]
        parts += [f"Lider tablosunda {len(board)} adres. **İstikrar havuzu:** hesap ≥ 50.000 USD; hafta, ay ve tüm zaman "
                  f"ROI > 0; tüm zaman ROI %20–%500; aylık hacim / hesap 0,5–20 kat; tüm zaman PnL'e göre ilk {len(leaders)} adres.", "",
                  "| Süzgeç | Kalan |", "|---|---:|", f"| Havuz | {len(leaders)} |", f"| Çok sık işlem (≥ {args.en_cok_dolum} dolum/yıl, scalp; ayrıntı çekilmedi) | {len(scalp)} |",
                  f"| Veri okundu | {len(loaded)} |",
                  f"| Swing: medyan tutma ≥ 4 saat | {len(swing)} |",
                  f"| Martingale yok, açık pozisyon kaldıracı ≤ 5x | {len(calm)} |",
                  f"| ≥ 180 gün, ≥ 20 kapanmış işlem | {len(enough)} |", "",
                  ("Son süzgeçten kimse geçmedi; aşağıda bir önceki adımda kalanlar. " if not enough else "") + f"Aşağıda kalanların kârlı ay oranı ve Sortino'ya göre ilk {len(shown)}'i (kural motoru sonucu ayrıca yazılı)."]
    parts += ["Son 365 günün gerçekleşmiş net PnL'i (açık pozisyon kârı hariç; spot işlemler hariç). Adresi Hyperdash'te "
              "arama kutusuna yapıştırıp gözle de bakabilirsin. **Bu bir seçim değil, örnektir.**", ""]
    parts += [section(row, fills, funding, state, rules, metrics) for row, fills, funding, state, metrics in shown]
    if errors:
        parts += ["## Okunamayan adresler", *errors, ""]
    out = Path(args.cikti)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
