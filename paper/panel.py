#!/usr/bin/env python3
"""T27: paper ledger -> ``paper/panel/data.json`` in the schema of the user's dashboard (sselimgenc-oss/sg-test-panel).

The dashboard (``index.html``) is used as is; this file only produces its ``data.json``. Everything comes from the append-only
ledger (``paper/defter``) and from ``results/SONUC.csv`` (status, PF, OOS, bootstrap MDD95 of each row). Nothing is invented:

* no fallback prices, no fixed scores; ``luck_prob``, leveraged Monte Carlo, shadow mode and coach advice stay empty / ``null``
  (the dashboard shows "veri yok" / "-" for them);
* the TRY rate is the last real ``USDTRY=X`` close of the data archive (``null`` when the archive has none);
* a day without data adds nothing: orders wait and ``meta.veri_notu`` says so.

``index.html`` keeps three hard-coded return columns (``swing``, ``trend``, ``daytrade``) in ``periodic_returns``; the paper rows are all
daily swing books, so the whole portfolio's daily return is written to ``swing`` (the other two stay ``null``).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper import gunluk  # noqa: E402

PANEL_PATH = Path(__file__).resolve().parent / "panel" / "data.json"
DATA_VERSION = "sgarge_paper_v1"
MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
REQUIRED_KEYS = (
    "meta", "kpis", "alerts", "last_24h", "accounts", "closed_trades_list", "open_positions", "pending_orders", "stats",
    "scorecards", "shadow_mode", "calendar", "coach", "risk", "periodic_returns", "strategies_27",
)


def _clean(value: Any, digits: int | None = None) -> Any:
    """JSON-safe number: NaN/inf -> None, numpy scalars -> python."""
    if value is None:
        return None
    if isinstance(value, (np.floating, float)):
        value = float(value)
        if not math.isfinite(value):
            return None
        return round(value, digits) if digits is not None else value
    if isinstance(value, np.integer):
        return int(value)
    return value


def _ad(label: str) -> str:
    """Account name shown by the dashboard: ``C07:ABD25`` -> ``C07 · ABD25``."""
    return label.replace(":", " · ")


def _tf(value: Any) -> str:
    return value if isinstance(value, str) and value else "1D"


def _dmy(day: str | pd.Timestamp) -> str:
    return pd.Timestamp(day).strftime("%d.%m.%Y")


def _read(directory: Path, name: str) -> pd.DataFrame:
    return gunluk._read(directory, name)  # noqa: SLF001


# ----------------------------------------------------------------------------------------------- closed trades from fills
def kapanmis_islemler(fills: pd.DataFrame, names: dict[str, str]) -> list[dict[str, Any]]:
    """Pair entry / partial / exit fills of the ledger into closed trades (long only)."""
    if fills.empty:
        return []
    order = {"giris": 0, "kismi": 1, "cikis": 2}
    fills = fills.assign(_o=fills["tip"].map(order)).sort_values(["tarih", "_o"], kind="stable")
    open_book: dict[tuple[str, str], dict[str, Any]] = {}
    trades: list[dict[str, Any]] = []
    for row in fills.to_dict("records"):
        key = (row["satir"], row["sembol"])
        if row["tip"] == "giris":
            open_book[key] = {
                "giris": row, "adet": float(row["adet"]), "cost": float(row["maliyet"]), "spent": float(row["adet"]) * float(row["fiyat"]),
                "got": 0.0, "sold_qty": 0.0, "partial": False,
            }
            continue
        book = open_book.get(key)
        if book is None:
            continue  # exit of a position opened before the ledger started: not a paper trade
        qty, price = float(row["adet"]), float(row["fiyat"])
        book["got"] += qty * price
        book["cost"] += float(row["maliyet"])
        book["sold_qty"] += qty
        if row["tip"] == "kismi":
            book["partial"] = True
            continue
        entry = book["giris"]
        pnl = book["got"] - book["spent"] - book["cost"]
        stop = entry.get("stop")
        risk = book["adet"] * (float(entry["fiyat"]) - float(stop)) if stop is not None and pd.notna(stop) else float("nan")
        trades.append({
            "id": len(trades) + 1, "account": _ad(row["satir"]), "_satir": row["satir"], "strategy": names.get(row["satir"], row["satir"]), "asset": row["sembol"], "type": "Alış",
            "entry_date": _dmy(entry["tarih"]), "exit_date": _dmy(row["tarih"]), "entry_price": _clean(float(entry["fiyat"]), 4),
            "exit_price": _clean(book["got"] / book["sold_qty"], 4) if book["sold_qty"] else None,
            "r": _clean(pnl / risk, 2) if risk and math.isfinite(risk) and risk > 0 else None, "pnl": _clean(pnl, 2),
            "reason": str(row.get("neden") or "signal") + ("+partial" if book["partial"] else ""),
            "_entry": str(entry["tarih"]), "_exit": str(row["tarih"]), "_hold": (pd.Timestamp(row["tarih"]) - pd.Timestamp(entry["tarih"])).days,
        })
        del open_book[key]
    return trades


# ----------------------------------------------------------------------------------------------- statistics
def _pf(values: list[float]) -> float | None:
    wins, losses = sum(v for v in values if v > 0), -sum(v for v in values if v < 0)
    return wins / losses if losses > 0 else None


def _stats(trades: list[dict[str, Any]], daily_returns: pd.Series) -> dict[str, Any]:
    pnl = [t["pnl"] for t in trades if t["pnl"] is not None]
    rs = [t["r"] for t in trades if t["r"] is not None]
    wins, losses = [v for v in pnl if v > 0], [v for v in pnl if v < 0]
    n = len(pnl)
    win_rate = len(wins) / n if n else None
    avg_win = float(np.mean(wins)) if wins else None
    avg_loss = float(np.mean(losses)) if losses else None
    streak = best = 0
    for value in pnl:
        streak = streak + 1 if value < 0 else 0
        best = max(best, streak)
    returns = daily_returns.dropna()
    enough = len(returns) >= 20 and returns.std(ddof=1) > 0
    downside = returns[returns < 0]
    kelly = (win_rate - (1 - win_rate) / (avg_win / -avg_loss)) if win_rate is not None and avg_win and avg_loss else None
    return {
        "net_pnl": _clean(sum(pnl), 2), "total_trades": n, "win_rate": _clean(win_rate * 100, 1) if win_rate is not None else None,
        "profit_factor": _clean(_pf(pnl), 2), "avg_win": _clean(avg_win, 2), "avg_loss": _clean(avg_loss, 2),
        "win_loss_ratio": _clean(avg_win / -avg_loss, 2) if avg_win and avg_loss else None,
        "expectancy_per_trade": _clean(float(np.mean(pnl)), 2) if n else None,
        "sqn": _clean(float(np.mean(rs) / np.std(rs, ddof=1) * math.sqrt(len(rs))), 2) if len(rs) > 2 and np.std(rs, ddof=1) > 0 else None,
        "max_win": _clean(max(pnl), 2) if pnl else None, "max_loss": _clean(min(pnl), 2) if pnl else None,
        "max_consecutive_losses": f"{best} Z" if n else None,
        "avg_holding_time_hours": _clean(float(np.mean([t["_hold"] for t in trades])) * 24, 1) if trades else None,
        "kelly_criterion": _clean(kelly, 3), "best_day_gain": _clean(float(returns.max() * 100), 2) if len(returns) else None,
        "green_days_pct": _clean(float((returns > 0).mean() * 100), 1) if len(returns) else None,
        "sharpe_annual": _clean(float(returns.mean() / returns.std(ddof=1) * math.sqrt(252)), 2) if enough else None,
        "sortino": _clean(float(returns.mean() / math.sqrt((downside**2).mean()) * math.sqrt(252)), 2) if enough and len(downside) else None,
        "long_trades": n, "short_trades": 0, "long_pnl": _clean(sum(pnl), 2), "short_pnl": 0.0,
    }


def _turkish_month(day: pd.Timestamp) -> str:
    return f"{MONTHS[day.month - 1]} {day.year}"


# ----------------------------------------------------------------------------------------------- the file
def uret(
    defter: Path = gunluk.LEDGER_DIR, portfoy: gunluk.Portfoy | None = None, sonuc_csv: Path = gunluk.RESULTS_DIR / "SONUC.csv",
    *, usdtry: float | None = None, simdi: pd.Timestamp | None = None, veri_notu: str | None = None,
) -> dict[str, Any]:
    portfoy = portfoy or gunluk.yukle_portfoy()
    sonuc = pd.read_csv(sonuc_csv) if sonuc_csv.exists() else pd.DataFrame()
    equity, fills = _read(defter, "ozkaynak"), _read(defter, "dolumlar")
    positions, orders, alarms = _read(defter, "pozisyonlar"), _read(defter, "emirler"), _read(defter, "alarmlar")
    now_trt = (simdi or pd.Timestamp.now(tz="UTC")).tz_convert("Europe/Istanbul")
    capital = {r.etiket: portfoy.sermaye * r.agirlik for r in portfoy.satirlar}
    info = {}
    for r in portfoy.satirlar:
        row = sonuc[sonuc["id"].astype(str) == r.id] if not sonuc.empty else sonuc
        info[r.etiket] = row.iloc[0].to_dict() if len(row) else {}
    names = {e: str(i.get("ad") or e) for e, i in info.items()}

    series = {}
    if not equity.empty:
        for label, group in equity.groupby("satir"):
            series[label] = group.sort_values("tarih").set_index("tarih")["ozkaynak"].astype(float)
    total = series.get(gunluk.PORTFOLIO_ROW, pd.Series(dtype=float))
    last_day = total.index[-1] if len(total) else None
    trades = kapanmis_islemler(fills, names)
    stopped = (not alarms.empty) and (alarms["tip"] == "DURDUR").any()

    open_rows = positions[positions["tarih"] == positions["tarih"].max()] if not positions.empty else positions
    entry_stop = {}
    if not fills.empty:
        for row in fills[fills["tip"] == "giris"].to_dict("records"):
            entry_stop[(row["satir"], row["sembol"], str(row["tarih"]))] = row.get("stop")
    open_positions = []
    for row in open_rows.to_dict("records"):
        stop0 = entry_stop.get((row["satir"], row["sembol"], str(row["giris_tarihi"])))
        risk = float(row["adet"]) * (float(row["giris_fiyati"]) - float(stop0)) if stop0 is not None and pd.notna(stop0) else float("nan")
        unrealized = float(row["acik_kar"])
        open_positions.append({
            "account": _ad(row["satir"]), "strategy": names.get(row["satir"], row["satir"]), "asset": row["sembol"], "type": "Alış",
            "entry_date": _dmy(row["giris_tarihi"]), "duration": f"{(pd.Timestamp(row['tarih']) - pd.Timestamp(row['giris_tarihi'])).days} gün",
            "entry_price": _clean(float(row["giris_fiyati"]), 4), "stop_price": _clean(float(row["stop"]), 4),
            "size_usd": _clean(float(row["adet"]) * float(row["son_kapanis"]), 2), "unrealized_pnl": _clean(unrealized, 2),
            "r": _clean(unrealized / risk, 2) if math.isfinite(risk) and risk > 0 else None,
        })
    pending = []
    if not orders.empty and last_day is not None:
        for row in orders[orders["sinyal_tarihi"] == orders["sinyal_tarihi"].max()].to_dict("records"):
            if row["tip"] not in ("giris", "cikis"):
                continue
            stop = row.get("stop")
            reference = float(row["referans_fiyat"])
            pending.append({
                "account": _ad(row["satir"]), "strategy": names.get(row["satir"], row["satir"]), "asset": row["sembol"], "signal_date": _dmy(row["sinyal_tarihi"]),
                "order": "Alış (yarın açılışta)" if row["tip"] == "giris" else "Sat (yarın açılışta)",
                "stop": _clean(float(stop), 4) if stop is not None and pd.notna(stop) else None,
                "stop_distance": _clean(reference - float(stop), 4) if row["tip"] == "giris" and stop is not None and pd.notna(stop) else None,
            })

    daily = total.pct_change().dropna() if len(total) else pd.Series(dtype=float)
    total_value = float(total.iloc[-1]) if len(total) else portfoy.sermaye
    initial = portfoy.sermaye
    last_day_pct = float(daily.iloc[-1] * 100) if len(daily) else None
    stats = _stats(trades, daily)

    accounts, strategies = [], []
    for rank, satir in enumerate(portfoy.satirlar, start=1):
        label, i = satir.etiket, info[satir.etiket]
        series_row = series.get(label, pd.Series(dtype=float))
        mine = [t for t in trades if t["_satir"] == label]
        own_pnl = [t["pnl"] for t in mine if t["pnl"] is not None]
        value = float(series_row.iloc[-1]) if len(series_row) else capital[label]
        peak = series_row.cummax() if len(series_row) else series_row
        mdd = float(((peak - series_row) / peak).max() * 100) if len(series_row) else None
        row_daily = series_row.pct_change().dropna() if len(series_row) else series_row
        held = int((open_rows["satir"] == label).sum()) if not open_rows.empty else 0
        wins = [v for v in own_pnl if v > 0]
        expectation = (
            f"Backtest: {i.get('nihai_durum', 'veri yok')} · PF (IS, 1x) {_fmt(i.get('pf_is'), '.2f')} · OOS getiri {_fmt(i.get('oos_getiri'), '.1%')} · "
            f"bootstrap MDD95 {_fmt(i.get('bootstrap_mdd_p95'), '.1%')} · evren {i.get('evren') or '-'}"
        )
        common = {
            "current_value": _clean(value, 2), "initial_capital": _clean(capital[label], 2),
            "total_return_pct": _clean((value / capital[label] - 1) * 100, 2), "last_day_pct": _clean(float(row_daily.iloc[-1] * 100), 2) if len(row_daily) else None,
            "max_drawdown_pct": _clean(mdd, 2), "win_rate_pct": _clean(len(wins) / len(own_pnl) * 100, 1) if own_pnl else None,
            "profit_factor": _clean(_pf(own_pnl), 2), "closed_trades": len(mine), "open_trades": held,
            "avg_holding_time": f"{np.mean([t['_hold'] for t in mine]):.1f} gün" if mine else None,
            "last_run": _dmy(series_row.index[-1]) if len(series_row) else None, "sparkline": [_clean(float(v), 2) for v in series_row.tail(7)],
        }
        status = "durduruldu (MDD kapısı)" if stopped else ("pozisyonda" if held else "tetikte bekliyor")
        accounts.append({
            "id": satir.id, "name": f"{satir.id} · {satir.piyasa}", "strategies_label": names[label], "status": status, **common,
            "luck_prob": "veri yok", "expectation_desc": expectation, "expectation_60d": f"Kaynak: {i.get('kaynak') or '-'} · {i.get('en_iyi_piyasa') if isinstance(i.get('en_iyi_piyasa'), str) else satir.piyasa}/{_tf(i.get('en_iyi_tf'))}",
            "score": None,
        })
        strategies.append({
            "rank": rank, "code": satir.id, "name": names[label], "mtf": f"{_tf(i.get('en_iyi_tf'))} ({i.get('tarz') if isinstance(i.get('tarz'), str) else 'swing'})", "score": None,
            "status": i.get("nihai_durum") or "veri yok", "allocation": f"%{satir.agirlik * 100:.0f}", "account": f"{satir.id} · {satir.piyasa}",
            "j_score": None, "p_main": None, "dd_pct": f"%{float(i['bootstrap_mdd_p95']) * 100:.1f}" if pd.notna(i.get("bootstrap_mdd_p95")) else None,
            "status_badge": i.get("nihai_durum") or "veri yok", "desc": i.get("alt_neden") or "", "display_title": f"{satir.id} · {satir.piyasa}",
            "subtitle": names[label], "live_status_tag": status, "is_active_trade": held > 0,
            "active_trade_symbol": ", ".join(open_rows[open_rows["satir"] == label]["sembol"]) if held else "Nakit",
            "active_trade_detail": f"{held} açık pozisyon" if held else "Açık pozisyon yok", "balance_usd": _clean(value, 2),
            **{k: common[k] for k in ("total_return_pct", "last_day_pct", "max_drawdown_pct", "win_rate_pct", "profit_factor", "closed_trades", "open_trades", "avg_holding_time", "last_run", "sparkline", "initial_capital")},
            "alpha_conf": "hesaplanmadı", "footer_badge_1": f"Backtest OOS getiri {_fmt(i.get('oos_getiri'), '.1%')} · PF (IS) {_fmt(i.get('pf_is'), '.2f')}",
            "footer_badge_2": f"Bootstrap MDD95 {_fmt(i.get('bootstrap_mdd_p95'), '.1%')} · durum {i.get('nihai_durum') or 'veri yok'}",
        })

    alerts = [{"id": "sgarge_1", "type": "info", "title": "Sanal defter: gerçek para ve aracı kurum bağlantısı yok. Sinyal ve dolumlar backtest motoruyla aynı yoldan üretilir."}]
    for k, row in enumerate(alarms.to_dict("records") if not alarms.empty else [], start=2):
        kind = "danger" if row["tip"] == "DURDUR" else "warning"
        alerts.append({"id": f"sgarge_{k}", "type": kind, "title": f"{row['tarih']} · {row['tip']} · {row['satir']}: {row['mesaj']}"})

    fills_last = fills[fills["tarih"] == fills["tarih"].max()] if not fills.empty else fills
    chips = [{"label": f"{r['sembol']} {'alış' if r['tip'] == 'giris' else 'satış'}", "type": "open" if r["tip"] == "giris" else "close",
              "action": r["tip"], "asset": r["sembol"]} for r in fills_last.to_dict("records")]
    summary = (f"Son bar {_dmy(last_day)}: {len(fills_last)} dolum, {len(pending)} emir yarın açılışta bekliyor, {len(open_positions)} açık pozisyon."
               if last_day is not None else "Henüz defter kaydı yok.")

    # calendar of the last month in the ledger
    days, selected = [], None
    if len(total):
        month_start = pd.Timestamp(last_day).replace(day=1)
        month_total = total[(pd.to_datetime(total.index) >= month_start)]
        prev = total[pd.to_datetime(total.index) < month_start]
        previous_value = float(prev.iloc[-1]) if len(prev) else initial
        closed_by_day: dict[str, list[float]] = {}
        for t in trades:
            closed_by_day.setdefault(t["_exit"], []).append(t["pnl"] or 0.0)
        values = list(month_total.items())
        change = {}
        for k, (day, value) in enumerate(values):
            before = values[k - 1][1] if k else previous_value
            change[day] = float(value) - float(before)
        for n in range(1, pd.Timestamp(last_day).day + 1):
            key = month_start.replace(day=n).strftime("%Y-%m-%d")
            days.append({"day": n, "pnl": _clean(change[key], 2) if key in change else None, "closed": len(closed_by_day.get(key, []))})
        last_key = str(last_day)
        closed_pnl = sum(closed_by_day.get(last_key, []))
        selected = {
            "date": f"{pd.Timestamp(last_day).day} {MONTHS[pd.Timestamp(last_day).month - 1]} {pd.Timestamp(last_day).year}", "pnl": _clean(change[last_key], 2),
            "closed_pnl": _clean(closed_pnl, 2), "open_pnl_change": _clean(change[last_key] - closed_pnl, 2), "account_breakdown": [],
        }
        for satir in portfoy.satirlar:
            sr = series.get(satir.etiket, pd.Series(dtype=float))
            diff = float(sr.iloc[-1] - (sr.iloc[-2] if len(sr) > 1 else capital[satir.etiket])) if len(sr) else 0.0
            closed_here = sum(t["pnl"] or 0.0 for t in trades if t["_satir"] == satir.etiket and t["_exit"] == last_key)
            selected["account_breakdown"].append({"account": f"{satir.id} · {satir.piyasa}", "closed": _clean(closed_here, 2), "open": _clean(diff - closed_here, 2), "total": _clean(diff, 2)})
        green = sum(1 for d in days if d["pnl"] and d["pnl"] > 0)
        month_net = sum(d["pnl"] or 0.0 for d in days)
        month_trades = sum(d["closed"] for d in days)
        summary_month = f"{MONTHS[month_start.month - 1]} Ayı Net: {month_net:.0f} $ | {green} yeşil gün | Toplam {month_trades} kapanan işlem"
    else:
        summary_month = "Henüz defter kaydı yok."
    calendar = {"month": _turkish_month(pd.Timestamp(last_day)) if last_day is not None else _turkish_month(now_trt.tz_localize(None)),
                "month_summary": summary_month, "selected_day": selected or {"date": None, "pnl": None, "closed_pnl": None, "open_pnl_change": None, "account_breakdown": []},
                "days": days}

    periodic = [{"day": _dmy(day), "swing": _clean(float(value) * 100, 2), "trend": None, "daytrade": None} for day, value in daily.tail(30)[::-1].items()]
    gross = sum(float(p["size_usd"] or 0) for p in open_positions)
    held_text = (f"{len(open_positions)} açık pozisyon, brüt maruziyet özkaynağın %{gross / total_value * 100:.0f}'i." if open_positions
                 else "Açık pozisyon yok: sanal sermayenin tamamı nakitte.")
    first_day = pd.Timestamp(total.index[0]) if len(total) else portfoy.baslangic
    day_count = (pd.Timestamp(last_day) - portfoy.baslangic.tz_localize(None)).days + 1 if last_day is not None else 0
    meta = {
        "title": "Kağıt Hesaplar", "subtitle": f"sg-arge Paper Portföyü: {', '.join(r.id for r in portfoy.satirlar)} / {initial:,.0f} $ sanal sermaye (1/N)",
        "last_update": now_trt.strftime("%d/%m %H:%M"), "test_period": f"gün {day_count} - {_dmy(portfoy.baslangic)} başlangıç (yer tutucu, kullanıcı onayı bekler)",
        "exchange_rate": _clean(usdtry, 4), "currency": "USD", "fiat_currency": "TRY",
        "footer_note": "Kağıt üzerinde al-sat: sanal defter, gerçek emir gönderilmez. Sinyal ve dolumlar sg-arge backtest motoruyla aynı yoldan üretilir; "
                       "durum, PF, OOS ve bootstrap MDD95 results/SONUC.csv'den gelir. Saatler İstanbul saatidir.",
        "data_version": DATA_VERSION, "veri_notu": veri_notu,
    }
    return {
        "meta": meta,
        "kpis": {
            "total_value": _clean(total_value, 2), "total_return_pct": _clean((total_value / initial - 1) * 100, 2), "last_day_pct": _clean(last_day_pct, 2),
            "open_positions_count": len(open_positions), "closed_trades_count": len(trades), "win_rate_pct": stats["win_rate"],
            "total_try": _clean(total_value * usdtry, 0) if usdtry else None, "initial_total_capital": initial, "net_pnl": _clean(total_value - initial, 2),
        },
        "alerts": alerts, "last_24h": {"summary": summary, "chips": chips}, "accounts": accounts,
        "closed_trades_list": [{k: v for k, v in t.items() if not k.startswith("_")} for t in reversed(trades)],
        "open_positions": open_positions, "pending_orders": pending, "stats": stats,
        "scorecards": [],  # no validated score exists for these rows: results/SONUC.csv carries status, PF, OOS and bootstrap MDD95 instead
        "shadow_mode": {"closed_count": None, "actual_pnl": None, "shadow_filtered_pnl": None, "filtered_skipped_trades": None, "accuracy_pct": None, "trades": []},
        "calendar": calendar,
        "coach": {"findings": [], "simulator_strategies": [
            {"id": s.id, "name": f"{s.id} · {s.piyasa}", "pnl": _clean(sum(t["pnl"] or 0.0 for t in trades if t["_satir"] == s.etiket), 2),
             "trades": sum(1 for t in trades if t["_satir"] == s.etiket), "active": not stopped} for s in portfoy.satirlar]},
        "risk": {"concentrations": [], "leverage_drawdown_montecarlo": [], "correlation_note": held_text},
        "periodic_returns": periodic, "strategies_27": strategies,
    }


def _fmt(value: Any, fmt: str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "veri yok"
    return "veri yok" if number != number else format(number, fmt)


def usdtry_son(directory: Path = gunluk.DATA_DIR) -> float | None:
    path = directory / "USDTRY_X.parquet"
    if not path.exists():
        return None
    from data.fetch import normalize_ohlcv  # noqa: PLC0415

    frame = normalize_ohlcv(pd.read_parquet(path))
    return float(frame["close"].iloc[-1]) if len(frame) else None


def yaz(payload: dict[str, Any], path: Path = PANEL_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--defter", type=Path, default=gunluk.LEDGER_DIR)
    parser.add_argument("--portfoy", type=Path, default=gunluk.PORTFOLIO_PATH)
    parser.add_argument("--sonuc", type=Path, default=gunluk.RESULTS_DIR / "SONUC.csv")
    parser.add_argument("--cikti", type=Path, default=PANEL_PATH)
    parser.add_argument("--veri-dir", type=Path, default=gunluk.DATA_DIR)
    args = parser.parse_args()
    payload = uret(args.defter, gunluk.yukle_portfoy(args.portfoy), args.sonuc, usdtry=usdtry_son(args.veri_dir))
    yaz(payload, args.cikti)
    print(f"{args.cikti} yazildi: ozkaynak {payload['kpis']['total_value']}, {len(payload['closed_trades_list'])} kapanmis, {len(payload['open_positions'])} acik")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
