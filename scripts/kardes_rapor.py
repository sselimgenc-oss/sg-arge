"""Summarize per-symbol trades for U1 sibling and pooled validation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

CORE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "TRXUSDT")


def _column(frame: pd.DataFrame, names: tuple[str, ...]) -> str:
    for name in names:
        if name in frame.columns:
            return name
    raise ValueError(f"CSV sütunlarından biri gerekli: {', '.join(names)}")


def _pf(values: pd.Series | np.ndarray) -> float:
    numbers = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
    gains = float(numbers[numbers > 0].sum())
    losses = float(-numbers[numbers < 0].sum())
    if losses == 0:
        return float("inf") if gains > 0 else float("nan")
    return gains / losses


def _bootstrap_pf(values: pd.Series, repetitions: int, seed: int) -> tuple[float, float]:
    numbers = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if len(numbers) == 0 or repetitions < 1:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    block = max(1, int(round(np.sqrt(len(numbers)))))
    blocks = int(np.ceil(len(numbers) / block))
    starts = rng.integers(0, len(numbers), size=(repetitions, blocks))
    offsets = np.arange(block)
    draws = (starts[:, :, None] + offsets[None, None, :]) % len(numbers)
    samples = numbers[draws].reshape(repetitions, -1)[:, : len(numbers)]
    gains = np.maximum(samples, 0).sum(axis=1)
    losses = -np.minimum(samples, 0).sum(axis=1)
    pfs = np.divide(gains, losses, out=np.full(repetitions, np.inf), where=losses > 0)
    return tuple(float(x) for x in np.nanquantile(pfs, [0.05, 0.95]))


def summarize_trades(
    trades: pd.DataFrame,
    *,
    core: tuple[str, ...] = CORE,
    repetitions: int = 1000,
    seed: int = 42,
) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    """Return symbol-level rows and pooled metrics from a trade table."""

    symbol_col = _column(trades, ("symbol", "sembol"))
    pnl_col = _column(trades, ("net_pnl", "net", "pnl", "profit"))
    work = trades.copy()
    work["_symbol"] = work[symbol_col].astype(str)
    work["_pnl"] = pd.to_numeric(work[pnl_col], errors="coerce")
    work = work.dropna(subset=["_pnl"])
    date_col = next((name for name in ("exit_date", "entry_date", "date", "timestamp") if name in work), None)
    if date_col:
        dates = pd.to_datetime(work[date_col], utc=True, errors="coerce").dt.tz_localize(None)
        work["_month"] = dates.dt.to_period("M").astype(str)
    else:
        work["_month"] = ""

    rows: list[dict[str, object]] = []
    for symbol, group in work.groupby("_symbol", sort=True):
        pnl = group["_pnl"]
        rows.append({
            "symbol": symbol,
            "trades": len(group),
            "net_pnl": float(pnl.sum()),
            "profit_factor": _pf(pnl),
            "gross_profit": float(pnl[pnl > 0].sum()),
            "gross_loss": float(-pnl[pnl < 0].sum()),
            "is_core": symbol in core,
        })
    detail = pd.DataFrame(rows)
    siblings = detail.loc[~detail["is_core"]] if not detail.empty else detail
    sibling_ratio = float((siblings["profit_factor"] > 1.1).mean()) if len(siblings) else float("nan")

    pooled = work["_pnl"]
    low, high = _bootstrap_pf(pooled, repetitions, seed)
    best_month = ""
    best_month_removed = _pf(pooled)
    dated = work[work["_month"] != ""]
    if not dated.empty:
        best_month = str(dated.groupby("_month")["_pnl"].sum().idxmax())
        best_month_removed = _pf(work.loc[work["_month"] != best_month, "_pnl"])
    max_symbol_share = float("nan")
    if pooled.sum() > 0 and not detail.empty:
        max_symbol_share = float(detail["net_pnl"].max() / pooled.sum())
    summary: dict[str, float | int | str] = {
        "symbols": int(work["_symbol"].nunique()),
        "trades": int(len(work)),
        "pooled_profit_factor": _pf(pooled),
        "pooled_pf_ci90_low": low,
        "pooled_pf_ci90_high": high,
        "sibling_pf_gt_1_1_ratio": sibling_ratio,
        "largest_profit_share_symbol": str(detail.loc[detail["net_pnl"].idxmax(), "symbol"]) if not detail.empty else "",
        "largest_profit_share": max_symbol_share,
        "best_month_removed": best_month,
        "best_month_removed_profit_factor": best_month_removed,
    }
    return detail, summary


def write_report(detail: pd.DataFrame, summary: dict[str, object], output_csv: Path, output_md: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    detail.to_csv(output_csv, index=False)
    lines = ["# Kardeş/havuz raporu", "", "## Havuz", ""]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "## Sembol özeti", ""]
    if detail.empty:
        lines.append("İşlem yok.")
    else:
        columns = list(detail.columns)
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("|" + "|".join("---" for _ in columns) + "|")
        for row in detail.itertuples(index=False, name=None):
            lines.append("| " + " | ".join(str(value) for value in row) + " |")
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trades", type=Path, help="symbol ve net_pnl içeren işlem CSV'si")
    parser.add_argument("--out-csv", type=Path, default=Path("results/U1_kardes_rapor.csv"))
    parser.add_argument("--out-md", type=Path, default=Path("results/U1_kardes_rapor.md"))
    parser.add_argument("--core", default=",".join(CORE), help="çekirdek semboller")
    parser.add_argument("--repetitions", type=int, default=1000)
    args = parser.parse_args()
    detail, summary = summarize_trades(pd.read_csv(args.trades), core=tuple(x for x in args.core.split(",") if x), repetitions=args.repetitions)
    write_report(detail, summary, args.out_csv, args.out_md)
    print(f"OK {args.out_md}: {summary['trades']} işlem, PF={summary['pooled_profit_factor']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
