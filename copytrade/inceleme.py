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


def curve_stats(portfolio: list, days: int = 365) -> dict | None:
    """1. aşama: ``portfolio`` yanıtındaki kümülatif PnL ve hesap değeri geçmişinden aylık tutarlılık.

    Aylık PnL = ay sonu kümülatif PnL farkı; aylık getiri = PnL / o ayın ortalama hesap değeri. Para yatırma/çekme
    PnL'i etkilemez (hesap değerini etkiler). Düşüş, ortalama hesap değeri + kümülatif PnL eğrisinin zirveden kaybı.
    """
    periods = {name: data for name, data in portfolio} if portfolio else {}
    data = periods.get("perpAllTime") or periods.get("allTime")
    if not data or not data.get("pnlHistory"):
        return None
    pnl = pd.Series({pd.to_datetime(t, unit="ms", utc=True): float(v) for t, v in data["pnlHistory"]}).sort_index()
    value = pd.Series({pd.to_datetime(t, unit="ms", utc=True): float(v) for t, v in data.get("accountValueHistory", [])}).sort_index()
    since = pnl.index[-1] - pd.Timedelta(days=days)
    before = pnl[pnl.index < since]
    base = float(before.iloc[-1]) if len(before) else float(pnl.iloc[0])
    window = pnl[pnl.index >= since]
    if len(window) < 2:
        return None
    month_end = window.resample("ME").last().dropna()
    monthly = month_end.diff()
    if len(before):
        monthly.iloc[0] = month_end.iloc[0] - base
    else:
        monthly = monthly.iloc[1:]  # geçmiş pencereden önce başlamıyorsa ilk ay kısmi ve tabansız
    av = value[value.index >= since].resample("ME").mean().reindex(monthly.index).ffill().bfill()
    av = av.where(av > 0)
    returns = (monthly / av).dropna()
    if returns.empty:
        return None
    mean_value = float(av.mean())
    equity = mean_value + (window - base)
    drawdown = float((1 - equity / equity.cummax()).max()) if mean_value > 0 else float("nan")
    total = float(returns.sum())
    return {"ay": int(len(returns)), "karli_ay": float((returns > 0).mean()), "getiri_12a": total,
            "en_kotu_ay": float(returns.min()), "dusus": drawdown,
            "getiri_dusus": total / drawdown if drawdown > 0 else (float("inf") if total > 0 else 0.0)}


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
             f"- Medyan tutma: {metrics.get('median_holding_hours', float('nan')):.1f} saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: "
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
                             martingale_min_additions=int(rules["martingale_min_additions"]),
                             martingale_min_adverse=float(rules.get("martingale_min_adverse", 0.02)))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adet", type=int, default=8)
    parser.add_argument("--mod", choices=["kar", "istikrar"], default="kar")
    parser.add_argument("--havuz", type=int, default=400)
    parser.add_argument("--ikinci", type=int, default=25)
    parser.add_argument("--cikti", default="copytrade/inceleme/RAPOR.md")
    args = parser.parse_args(argv)
    client, rules = PublicClient(), load_rules()
    board = client.leaderboard()
    start = int((datetime.now(UTC) - timedelta(days=365)).timestamp() * 1000)
    out = Path(args.cikti)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.mod == "kar":
        rows = pick(board, args.adet)
        parts = [f"# Örnek trader incelemesi — kâr ({datetime.now(UTC).date()})", ""]
        for row in rows:
            fills, funding, state = load(client, row, start)
            parts.append(section(row, fills, funding, state, rules))
        out.write_text("\n".join(parts), encoding="utf-8")
        return

    pool = stable_pool(board, args.havuz)
    stage1, errors = [], []
    for row in pool:
        try:
            stats = curve_stats(client.info({"type": "portfolio", "user": row["address"]}, weight=20))
        except Exception:
            errors.append(f"- `{row['address']}` (1. aşama): {traceback.format_exc().strip().splitlines()[-1]}")
            continue
        if stats:
            stage1.append((row, stats))
    passed1 = [x for x in stage1 if x[1]["ay"] >= 6 and x[1]["karli_ay"] >= 0.6 and x[1]["dusus"] <= 0.30
               and x[1]["getiri_12a"] > 0]
    passed1.sort(key=lambda x: (x[1]["karli_ay"], x[1]["getiri_dusus"]), reverse=True)
    chosen = passed1[:args.ikinci]
    parts = [f"# Trader incelemesi — istikrar, iki aşama ({datetime.now(UTC).date()})", "",
             f"Lider tablosunda {len(board)} adres. **Havuz:** hesap ≥ 50.000 USD; hafta, ay ve tüm zaman ROI > 0; tüm zaman ROI "
             f"%20–%500; aylık hacim / hesap 0,5–20 kat; tüm zaman PnL'e göre ilk {len(pool)}.", "",
             "**1. aşama (kâr eğrisi, son 12 ay):** en az 6 ay; kârlı ay ≥ %60; zirveden düşüş ≤ %30; 12 aylık getiri > 0.",
             "**2. aşama (işlem geçmişi):** 1. aşamadan geçenlerin ilk "
             f"{len(chosen)}'i; kural motoru (`copytrade/kurallar.yaml`) ve gerçek kaldıraç, emir düzeyinde martingale.", "",
             "| Aşama | Adres |", "|---|---:|", f"| Havuz | {len(pool)} |", f"| Kâr eğrisi okundu | {len(stage1)} |",
             f"| 1. aşamadan geçti | {len(passed1)} |", f"| 2. aşamada incelendi | {len(chosen)} |", "",
             "## 2. aşama özeti", "",
             "| Adres | Kârlı ay | 12 ay getiri | Düşüş | İşlem | Medyan tutma (sa) | Gerçek kaldıraç medyan/en yüksek | Martingale | Kripto dışı hacim | Kural |",
             "|---|---:|---:|---:|---:|---:|---:|---|---:|---|"]
    details = []
    for row, stats in chosen:
        try:
            fills, funding, state = load(client, row, start)
        except Exception:
            errors.append(f"- `{row['address']}` (2. aşama): {traceback.format_exc().strip().splitlines()[-1]}")
            continue
        metrics = metrics_for(row, fills, funding, state, rules)
        decision, reason = evaluate(metrics, rules)
        classes = pd.Series([asset_class(f.get("coin", "")) for f in perp_fills(fills)])
        other = float((~classes.isin(["kripto"])).mean()) if len(classes) else float("nan")
        f = lambda v, fmt: "—" if v is None or v != v else format(v, fmt)
        parts.append(f"| `{row['address'][:10]}…` | {stats['karli_ay']:.0%} | {stats['getiri_12a']:.0%} | {stats['dusus']:.0%} | "
                     f"{metrics.get('closed_trades', 0)} | {f(metrics.get('median_holding_hours'), '.1f')} | "
                     f"{f(metrics.get('median_leverage'), '.1f')}/{f(metrics.get('max_leverage'), '.1f')} | "
                     f"{'VAR' if metrics.get('martingale_signal') else 'yok'} | {f(other, '.0%')} | {decision} |")
        details.append((decision != "aday", -stats["karli_ay"], row, fills, funding, state, metrics))
        out.write_text("\n".join(parts), encoding="utf-8")  # kesilse de o ana kadarki sonuç kalır
    details.sort(key=lambda x: (x[0], x[1]))
    parts += ["", f"## Ayrıntı (ilk {min(args.adet, len(details))})", "",
              "Son 365 günün gerçekleşmiş net PnL'i (spot hariç). Adresi Hyperdash'te arama kutusuna yapıştırıp gözle de bakabilirsin. "
              "**Bu bir seçim değil, örnektir.**", ""]
    parts += [section(row, fills, funding, state, rules, metrics) for _, _, row, fills, funding, state, metrics in details[:args.adet]]
    if errors:
        parts += ["## Okunamayan adresler", *errors, ""]
    out.write_text("\n".join(parts), encoding="utf-8")


def load(client, row: dict, start: int) -> tuple[list, list, dict]:
    fills = client.fills(row["address"], start, max_rows=20000)
    funding = client.info({"type": "userFunding", "user": row["address"], "startTime": start}) or []
    state = client.info({"type": "clearinghouseState", "user": row["address"]}, weight=2) or {}
    return fills, funding, state


if __name__ == "__main__":
    main()
