#!/usr/bin/env python3
"""Leader-only U6 locked-period confirmation for the pre-registered candidates."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import tarama, u4, u4_huni, u6
from engine import kilit
from engine.portfolio import calculate_metrics

LOCK_START = pd.Timestamp("2025-10-01", tz="UTC")
MAX_CANDIDATES = 5


def _number(row: pd.Series | dict, name: str, default: float = float("-inf")) -> float:
    value = row.get(name, default)
    return float(value) if pd.notna(value) else default


def _passes_without_dsr(row: pd.Series) -> bool:
    """Apply all U4 rejection gates other than the pre-registered DSR gate."""
    candidate = dict(row)
    candidate["dsr"] = 1.0
    return u4_huni.decide(candidate)[0] != "Reddedildi"


def select_candidates(table: pd.DataFrame, maximum: int = MAX_CANDIDATES) -> pd.DataFrame:
    """Section 4 ordering: Gecti, Kosullu by OOS Sharpe; then DSR-only misses."""
    if maximum < 1:
        return table.iloc[0:0].copy()
    ranked = table.copy()
    ranked["_oos_sharpe"] = ranked.apply(lambda row: _number(row, "oos_sharpe"), axis=1)
    ranked["_dsr"] = ranked.apply(lambda row: _number(row, "dsr"), axis=1)
    direct = ranked[ranked["karar"].isin(["Gecti", "Kosullu"])].copy()
    direct["_priority"] = direct["karar"].map({"Gecti": 0, "Kosullu": 1})
    direct = direct.sort_values(["_priority", "_oos_sharpe", "varyant"], ascending=[True, False, True], kind="stable")
    chosen = direct.head(maximum)
    if len(chosen) < maximum:
        known = set(chosen["varyant"])
        fallback = ranked[~ranked["varyant"].isin(known)].copy()
        fallback = fallback[fallback.apply(_passes_without_dsr, axis=1)]
        fallback = fallback.sort_values(["_dsr", "varyant"], ascending=[False, True], kind="stable")
        chosen = pd.concat([chosen, fallback.head(maximum - len(chosen))], ignore_index=True)
    return chosen.drop(columns=[column for column in ("_oos_sharpe", "_dsr", "_priority") if column in chosen], errors="ignore")


def passes_locked(metrics: dict[str, float | int]) -> bool:
    return bool(metrics["net_2x"] > 0 and metrics["PF_2x"] >= 1.1 and metrics["mdd"] <= .15)


def last_closed_bar(data: dict[str, pd.DataFrame], tf: str, now: pd.Timestamp | None = None) -> pd.Timestamp:
    """Latest completed UTC bar; never use the currently forming daily/4H bucket."""
    if not data:
        raise ValueError("kilitli kosu icin veri yok")
    current = pd.Timestamp.now(tz="UTC") if now is None else pd.Timestamp(now)
    current = current.tz_localize("UTC") if current.tzinfo is None else current.tz_convert("UTC")
    boundary = current.floor("4h" if tf == "4H" else "D")
    return min(min(frame.index[-1] for frame in data.values()), boundary - pd.Timedelta(nanoseconds=1))


def run_candidate(variant: str, card: dict, market: str, data: dict[str, pd.DataFrame], end: pd.Timestamp) -> dict:
    pit = u4.load_pit_universe() if market == "ABD25" else None
    prepared = tarama.prepare(card, data, market, start=LOCK_START, end=end, kilit=True, pit_universe=pit)
    result = prepared.run(2.0, trusted_inputs=True)
    prepared.runtime_cache.clear()
    stats = calculate_metrics(result, annualization=tarama.annualization_for(card["tf"], market))
    row = {"varyant": variant, "kart": card["id"], "piyasa": market, "tf": card["tf"], "bitis": end,
           "islem": stats["islem"], "PF_2x": stats["pf"], "net_2x": stats["getiri"], "mdd": stats["mdd"]}
    row["karar"] = "Gecti" if passes_locked(row) else "Reddedildi"
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u6")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    args = parser.parse_args(argv)
    if not kilit.acik():
        raise PermissionError("U6 kilitli donem yalniz liderin KILIT_AC=1 komutuyla calisir")
    source = args.results_dir / "huni_ozet.csv"
    if not source.exists():
        raise FileNotFoundError(f"{source} yok")
    selected = select_candidates(pd.read_csv(source))
    if selected.empty:
        print("aday cikmadi; kilitli donem acilmadi")
        return 0
    by_id = {variant: (card, market) for variant, card, market in u6.all_variants()}
    rows, cache = [], {}
    for variant in selected["varyant"]:
        if variant not in by_id:
            continue
        card, market = by_id[variant]
        key = market, card["tf"]
        data = cache.setdefault(key, u4.load_data(args.veri_kok, *key))
        if data:
            rows.append(run_candidate(variant, card, market, data, last_closed_bar(data, card["tf"])))
    pd.DataFrame(rows).to_csv(args.results_dir / "kilitli_ozet.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
