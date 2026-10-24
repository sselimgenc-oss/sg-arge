#!/usr/bin/env python3
"""U4 funnel for the fixed 16 pre-registered variants (docs/GOREV_U4.md)."""

from __future__ import annotations

import argparse
import gc
import logging
import math
import sys
import zlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import asama2a, asama2b, tarama, u4
from engine.portfolio import calculate_metrics
from scripts import kardes_rapor

LOG = logging.getLogger("u4_huni")
TRIALS = 16
MIN_TRADES = 30
SWING_PAPER_TRADES = 60
MIN_PF_2X = 1.2
ANNUALIZATION = 365
COLUMNS = [
    "varyant", "kart", "piyasa", "tf", "is_islem", "is_PF", "is_swing60", "null_gecti", "p_pf", "p_ortr",
    "oos_islem", "oos_islem_hafta", "oos_ortR", "oos_sharpe", "oos_PF_1x", "oos_PF_2x", "oos_PF_3x", "oos_net_1x", "oos_net_3x", "net_gecikme", "mdd_p95", "dsr",
    "kardes_gecen", "kardes_oran", "en_buyuk_kar_payi", "en_iyi_ay_haric_pf", "on_net", "karar", "neden",
]


def _prepare(card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], period: str):
    start, end = u4.PERIODS[period]
    u4.lock_check(end)
    pit = u4.load_pit_universe() if market == "ABD25" else None
    return tarama.prepare(card, data, market, start=start, end=end, kilit=True, pit_universe=pit)


def decide(row: dict[str, Any]) -> tuple[str, str]:
    rejected, conditional = [], []
    if row.get("is_islem", 0) < MIN_TRADES:
        rejected.append("IS islem<30")
    if not row.get("is_PF", float("nan")) > 1:
        rejected.append("IS PF<=1")
    if not row.get("null_gecti", False):
        rejected.append("null")
    for key, label, threshold, op in (("oos_ortR", "OOS ortR<=0", 0, "gt"), ("oos_PF_2x", "2x PF<1.2", MIN_PF_2X, "ge"),
                                      ("oos_net_3x", "3x net<=0", 0, "gt"), ("net_gecikme", "+1 bar net<=0", 0, "gt"),
                                      ("mdd_p95", "bootstrap MDD95>%15", asama2b.RISK_BUDGET, "le"), ("dsr", "DSR<=0.95", .95, "gt")):
        value = row.get(key, float("nan"))
        valid = value > threshold if op == "gt" else value >= threshold if op == "ge" else value <= threshold
        if not valid:
            rejected.append(label)
    if row.get("piyasa") == "KRIPTO25":
        if not row.get("kardes_oran", float("nan")) >= .60:
            rejected.append("kardes PF>1,1 orani<%60")
        if not row.get("en_buyuk_kar_payi", float("nan")) <= .35:
            conditional.append("tek coin kar payi>%35")
    if not row.get("en_iyi_ay_haric_pf", float("nan")) > 1:
        conditional.append("en iyi ay haric PF<=1")
    if row.get("piyasa") in {"ABD25", "EMTIA"} and not row.get("on_net", float("nan")) >= 0:
        conditional.append("on donem net<0")
    if rejected:
        return "Reddedildi", ", ".join(rejected)
    return ("Kosullu", ", ".join(conditional)) if conditional else ("Gecti", "bolum 5 olcutlerinin hepsi gecti")


def stage_2a(variant: str, card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], reps: int, reps_high: int, workers: int) -> dict[str, Any]:
    prepared = _prepare(card, market, data, "IS")
    real = prepared.run(1, trusted_inputs=True)
    pf, ortr, count = asama2a.trade_stats(real.trades)
    out = {"is_islem": count, "is_PF": pf, "is_swing60": count >= SWING_PAPER_TRADES}
    if count < 5:
        prepared.runtime_cache.clear()
        return {**out, "null_gecti": False, "p_pf": float("nan"), "p_ortr": float("nan")}
    seed = asama2a.BASE_SEED ^ zlib.crc32(variant.encode())
    workers = tarama.bellek_isci(workers, data, is_basina=asama2a.NULL_WORKER_DATA_FACTOR)
    null = asama2a.null_distribution(prepared, real.trades, reps, seed, workers)
    p_pf, p_ortr = asama2a.p_value(pf, null["pf"]), asama2a.p_value(ortr, null["ortr"])
    if asama2a.BORDERLINE_P[0] <= max(p_pf, p_ortr) <= asama2a.BORDERLINE_P[1]:
        null = asama2a.null_distribution(prepared, real.trades, reps_high, seed + 1, workers)
        p_pf, p_ortr = asama2a.p_value(pf, null["pf"]), asama2a.p_value(ortr, null["ortr"])
    prepared.runtime_cache.clear()
    return {**out, "null_gecti": bool(p_pf < .05 and p_ortr < .05), "p_pf": p_pf, "p_ortr": p_ortr}


def _trade_summary(trades: pd.DataFrame) -> dict[str, Any]:
    _detail, summary = kardes_rapor.summarize_trades(trades, repetitions=100, seed=asama2a.BASE_SEED)
    return summary


def _write_daily_returns(returns: pd.Series, variant: str, results_dir: Path) -> None:
    safe = variant.replace(":", "_")
    target = results_dir / "getiriler" / f"{safe}.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    returns.rename("net_getiri").to_csv(target, index_label="tarih")


def _trading_weeks(trades: pd.DataFrame) -> int:
    if trades.empty or "entry_date" not in trades:
        return 0
    dates = pd.to_datetime(trades["entry_date"], utc=True, errors="coerce").dropna()
    return len(set(zip(dates.dt.isocalendar().year, dates.dt.isocalendar().week)))


def stage_2b(variant: str, card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], boot_reps: int, results_dir: Path) -> dict[str, Any]:
    prepared = _prepare(card, market, data, "OOS")
    annual = tarama.annualization_for(card["tf"], market)
    runs = {cost: prepared.run(cost, trusted_inputs=True) for cost in u4.COSTS}
    delayed = prepared.run(1, trusted_inputs=True, extra_delay_bars=1)
    prepared.runtime_cache.clear()
    metrics = {cost: calculate_metrics(result, annualization=annual) for cost, result in runs.items()}
    returns = asama2b._validation_returns(runs[1], daily_equity=True)  # noqa: SLF001
    _write_daily_returns(returns, variant, results_dir)
    out = {"oos_islem": metrics[1]["islem"], "oos_islem_hafta": _trading_weeks(runs[1].trades), "oos_ortR": metrics[1]["ortalama_r"], "oos_sharpe": metrics[1]["sharpe"], "oos_PF_1x": metrics[1]["pf"], "oos_net_1x": metrics[1]["getiri"],
           "oos_PF_2x": metrics[2]["pf"], "oos_PF_3x": metrics[3]["pf"], "oos_net_3x": metrics[3]["getiri"],
           "net_gecikme": calculate_metrics(delayed, annualization=annual)["getiri"]}
    if len(returns) >= 3:
        boot = asama2b.block_bootstrap(returns, repetitions=boot_reps, seed=asama2a.BASE_SEED ^ zlib.crc32(variant.encode()), annualization=ANNUALIZATION)
        out.update(mdd_p95=boot["mdd_p95"], dsr=asama2b.deflated_sharpe_ratio(returns, TRIALS))
    else:
        out.update(mdd_p95=float("nan"), dsr=float("nan"))
    summary = _trade_summary(runs[1].trades)
    out.update(en_iyi_ay_haric_pf=summary["best_month_removed_profit_factor"])
    if market == "KRIPTO25":
        safe = variant.replace(":", "_")
        detail, summary = kardes_rapor.summarize_trades(runs[1].trades, repetitions=boot_reps, seed=asama2a.BASE_SEED)
        kardes_rapor.write_report(detail, summary, results_dir / f"kardes_{safe}.csv", results_dir / f"kardes_{safe}.md")
        out.update(kardes_gecen=summary["sibling_pf_gt_1_1_count"], kardes_oran=summary["sibling_pf_gt_1_1_ratio"], en_buyuk_kar_payi=summary["largest_profit_share"])
    return out


def stage_preperiod(card: dict[str, Any], market: str, data: dict[str, pd.DataFrame]) -> float:
    if market == "KRIPTO25":
        return float("nan")
    prepared = _prepare(card, market, data, "ON")
    result = prepared.run(1, trusted_inputs=True)
    value = calculate_metrics(result, annualization=tarama.annualization_for(card["tf"], market))["getiri"]
    prepared.runtime_cache.clear()
    return value


def evaluate_variant(variant: str, card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], *, reps: int, reps_high: int, workers: int, boot_reps: int, results_dir: Path) -> dict[str, Any]:
    row = {column: float("nan") for column in COLUMNS}
    row.update(varyant=variant, kart=card["id"], piyasa=market, tf=card["tf"])
    try:
        row.update(stage_2a(variant, card, market, data, reps, reps_high, workers))
        row.update(stage_2b(variant, card, market, data, boot_reps, results_dir))
        row["on_net"] = stage_preperiod(card, market, data)
        row["karar"], row["neden"] = decide(row)
    except PermissionError:
        raise
    except Exception as exc:  # one failed card is reported, never hidden
        row.update(karar="Hata", neden=f"{type(exc).__name__}: {exc}"[:200])
    gc.collect()
    return row


def write_outputs(table: pd.DataFrame, results_dir: Path, *, trials: int | None = None, title: str = "U4") -> None:
    table.to_csv(results_dir / "huni_ozet.csv", index=False)
    trials = TRIALS if trials is None else trials
    lines = [f"# {title} huni ozeti", "", f"Kilitli donem acilmadi. DSR deneme sayisi: {trials}.", "",
             "| varyant | IS PF/islem | null | OOS PF 2x | DSR | karar | neden |", "|---|---|---|---|---:|---|---|"]
    for r in table.to_dict("records"):
        f = lambda value: "-" if pd.isna(value) else f"{value:.2f}"
        lines.append(f"| {r['varyant']} | {f(r['is_PF'])}/{f(r['is_islem'])} | {r['null_gecti']} | {f(r['oos_PF_2x'])} | {f(r['dsr'])} | {r['karar']} | {r['neden']} |")
    (results_dir / "huni_ozet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kart-ids", default="")
    parser.add_argument("--tekrar", type=int, default=200)
    parser.add_argument("--tekrar-yuksek", type=int, default=1000)
    parser.add_argument("--bootstrap-tekrar", type=int, default=1000)
    parser.add_argument("--isci", type=int, default=1)
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u4")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    items = u4.all_variants()
    wanted = {x for x in args.kart_ids.split(",") if x}
    if wanted:
        items = [item for item in items if item[1]["id"] in wanted]
    args.results_dir.mkdir(parents=True, exist_ok=True)
    rows, cache = [], {}
    for variant, card, market in items:
        key = market, card["tf"]
        data = cache.setdefault(key, u4.load_data(args.veri_kok, market, card["tf"]))
        if data:
            rows.append(evaluate_variant(variant, card, market, data, reps=args.tekrar, reps_high=args.tekrar_yuksek, workers=args.isci, boot_reps=args.bootstrap_tekrar, results_dir=args.results_dir))
    if rows:
        write_outputs(pd.DataFrame(rows, columns=COLUMNS), args.results_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
