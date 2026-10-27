"""Tek seferlik örnek inceleme: lider tablosundan birkaç trader'ın 365 günlük geçmişini okunur bir rapora döker.

Yalnız herkese açık veri okunur; emir, anahtar, cüzdan yok. Kural motoru ve ölçütler mevcut koddan.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from copytrade.kurallar import evaluate, load_rules
from copytrade.olcut import _funding_amount, calculate_metrics
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


def monthly(fills: list[dict], funding: list[dict]) -> pd.Series:
    """Ay ay gerçekleşmiş net PnL (closedPnl − fee + funding), USD."""
    rows = [(int(f["time"]), float(f.get("closedPnl", 0)) - float(f.get("fee", 0))) for f in fills]
    rows += [(int(x["time"]), _funding_amount(x)) for x in funding]
    if not rows:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(rows, columns=["time", "pnl"])
    frame["ay"] = pd.to_datetime(frame.time, unit="ms", utc=True).dt.strftime("%Y-%m")
    return frame.groupby("ay").pnl.sum()


def section(row: dict, fills: list[dict], funding: list[dict], state: dict, rules: dict) -> str:
    address, account = row["address"], row["accountValue"]
    positions = [x.get("position", {}) for x in state.get("assetPositions", [])]
    leverage = [float(p.get("leverage", {}).get("value", 0)) for p in positions]
    metrics = calculate_metrics(fills, funding=funding, liquid_coins=LIQUID, leverages=leverage, account_value=account,
                                martingale_max_ratio=float(rules["martingale_max_ratio"]),
                                martingale_min_additions=int(rules["martingale_min_additions"]))
    decision, reason = evaluate(metrics, rules)
    by_month = monthly(fills, funding)
    coins = pd.Series([f.get("coin") for f in fills]).value_counts(normalize=True).head(5) if fills else pd.Series(dtype=float)
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
             f"- Açık pozisyon: {len(positions)}",
             f"- **Kural sonucu: {decision}**" + (f" — {reason}" if reason else ""),
             "", "| Ay | Gerçekleşmiş net PnL (USD) |", "|---|---:|"]
    lines += [f"| {ay} | {v:,.0f} |" for ay, v in by_month.items()]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adet", type=int, default=8)
    parser.add_argument("--cikti", default="copytrade/inceleme/RAPOR.md")
    args = parser.parse_args(argv)
    client, rules = PublicClient(), load_rules()
    board = client.leaderboard()
    leaders = pick(board, args.adet)
    start = int((datetime.now(UTC) - timedelta(days=365)).timestamp() * 1000)
    parts = [f"# Örnek trader incelemesi ({datetime.now(UTC).date()})", "",
             f"Lider tablosunda {len(board)} adres. Seçim: hesap ≥ 100.000 USD, aylık ve tüm zaman ROI > 0; tüm zaman "
             f"PnL / hesap değerine göre ilk {len(leaders)}. Son 365 günün gerçekleşmiş net PnL'i (açık pozisyon kârı hariç). "
             "Adresi Hyperdash'te arama kutusuna yapıştırıp gözle de bakabilirsin. **Bu bir seçim değil, örnektir.**", ""]
    for row in leaders:
        try:
            fills = client.fills(row["address"], start)
            funding = client.info({"type": "userFunding", "user": row["address"], "startTime": start})
            state = client.info({"type": "clearinghouseState", "user": row["address"]}, weight=2)
            parts.append(section(row, fills, funding, state, rules))
        except Exception as exc:  # tek adresin hatası raporu durdurmaz
            parts.append(f"## `{row['address']}`\n- Veri okunamadı: {type(exc).__name__}\n")
    out = Path(args.cikti)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
