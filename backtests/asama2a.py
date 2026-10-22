#!/usr/bin/env python3
"""Stage 2a: market-beta tests (T6a) for the stage 1 candidates.

1. BIST rows are re-run on USD prices (price / USDTRY close of the same day); the decision
   uses the USD result, the TL result is information only.
2. Random-entry null model: same exit rules, same per-symbol number of entries (calibrated so
   the null produces about as many trades as the card), random entry bars. The card must beat
   the 95th percentile of the null distribution for both PF and mean R, otherwise the edge is
   the market's drift: ``Reddedildi (piyasa betasi)``.

Only the in-sample period (2020-01-01 -> 2024-09-30) is used; OOS and 2015-2019 stay unseen.
"""

from __future__ import annotations

import argparse
import multiprocessing
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import tarama  # noqa: E402
from backtests.run_codex21 import _git_sha, _load_market  # noqa: E402
from data.fetch import normalize_ohlcv  # noqa: E402
from engine.portfolio import calculate_metrics  # noqa: E402

BASE_SEED = 20261022
CALIBRATION_REPS = 6
MAX_ENTRY_FACTOR = 8.0
PF_CAP = 1e9  # an infinite PF (no losing trade) is capped so percentiles stay finite
PASS_PERCENTILE = 95.0
BORDERLINE_P = (0.03, 0.10)

OUTPUT_COLUMNS = [
    "id", "piyasa", "tf", "kart_yazari", "para", "islem", "PF_1x", "PF_2x", "net_1x", "net_2x", "ort_r",
    "PF_1x_tl", "net_1x_tl", "usd_kapi", "null_tekrar", "null_pf_p50", "null_pf_p95", "null_ortr_p50",
    "null_ortr_p95", "p_pf", "p_ortr", "null_islem_ort", "tutma_gercek", "tutma_null", "karar", "neden",
    "data_hash", "git_sha",
]

_STATE: dict[str, Any] = {}  # filled before the worker pool forks


def usd_frames(data: dict[str, pd.DataFrame], usdtry: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """TL prices -> USD with the same-day USDTRY close (forward filled over holidays)."""
    rate = usdtry["close"].where(usdtry["close"] > 0).sort_index()
    out = {}
    for symbol, frame in data.items():
        fx = rate.reindex(rate.index.union(frame.index)).ffill().reindex(frame.index)
        converted = frame.copy()
        for column in ("open", "high", "low", "close"):
            converted[column] = frame[column] / fx
        out[symbol] = converted.dropna(subset=["open", "high", "low", "close"])
    return out


def holding_bars(trades: pd.DataFrame, frames: dict[str, pd.DataFrame]) -> float:
    if trades.empty:
        return float("nan")
    spans = []
    for row in trades.itertuples():
        index = frames[row.symbol].index
        spans.append(index.get_loc(row.exit_date) - index.get_loc(row.entry_date))
    return float(np.mean(spans))


def trade_stats(trades: pd.DataFrame) -> tuple[float, float, int]:
    """(profit factor, mean R, trades); PF is NaN without trades and capped when no loss exists."""
    if trades.empty:
        return float("nan"), float("nan"), 0
    wins = trades.loc[trades["net_pnl"] > 0, "net_pnl"].sum()
    losses = -trades.loc[trades["net_pnl"] < 0, "net_pnl"].sum()
    pf = wins / losses if losses > 0 else PF_CAP
    return float(min(pf, PF_CAP)), float(trades["r_multiple"].mean()), len(trades)


def random_entry_signals(
    prepared: tarama.Prepared,
    per_symbol: dict[str, int],
    factor: float,
    rng: np.random.Generator,
) -> dict[str, pd.DataFrame]:
    """Plan signals with the entry column replaced by random entry bars (exits untouched)."""
    signals = {}
    for symbol, base in prepared.plan.signals.items():
        count = per_symbol.get(symbol, 0)
        entry = np.zeros(len(base), dtype=bool)
        if count:
            index = base.index
            eligible = np.flatnonzero(
                np.asarray(index >= prepared.start)
                & np.asarray(index <= prepared.end)
                & np.isfinite(base["atr"].to_numpy(dtype=float))
            )
            eligible = eligible[:-1] if len(eligible) > 1 else eligible
            if len(eligible):
                draws = min(len(eligible), max(1, int(round(count * factor))))
                entry[rng.choice(eligible, size=draws, replace=False)] = True
        frame = base.copy(deep=False)
        frame["entry"] = entry
        signals[symbol] = frame
    return signals


def null_distribution(prepared: tarama.Prepared, real_trades: pd.DataFrame, reps: int, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    per_symbol = real_trades["symbol"].value_counts().to_dict()
    target = len(real_trades)

    def one(factor: float):
        signals = random_entry_signals(prepared, per_symbol, factor, rng)
        return prepared.run(1.0, signals=signals).trades

    factor = 1.0
    for _ in range(4):  # calibrate: random entries that land inside an open position are ignored
        counts = [len(one(factor)) for _ in range(CALIBRATION_REPS)]
        mean_count = max(float(np.mean(counts)), 1.0)
        if abs(mean_count - target) / target <= 0.05:
            break
        factor = min(factor * target / mean_count, MAX_ENTRY_FACTOR)
    pf, ortr, count, hold = [], [], [], []
    for _ in range(reps):
        trades = one(factor)
        stats = trade_stats(trades)
        pf.append(stats[0]); ortr.append(stats[1]); count.append(stats[2])
        hold.append(holding_bars(trades, prepared.frames))
    return {
        "pf": np.array(pf), "ortr": np.array(ortr), "count": np.array(count), "hold": np.array(hold),
        "factor": factor,
    }


def p_value(real: float, null: np.ndarray) -> float:
    valid = null[np.isfinite(null)]
    return (1 + float((valid >= real).sum())) / (1 + len(valid)) if np.isfinite(real) else float("nan")


def evaluate_pair(task: dict[str, Any]) -> dict[str, Any]:
    card, market = task["card"], task["market"]
    base = {column: np.nan for column in OUTPUT_COLUMNS}
    base.update(id=card["id"], piyasa=market, tf=card["tf"], kart_yazari=card.get("kart_yazari") or "",
                para="USD" if market == "BIST30" else "yerel", git_sha=_STATE["git_sha"],
                data_hash=_STATE["hashes"][market])
    try:
        data = _STATE["usd"][market] if market == "BIST30" else _STATE["data"][market]
        benchmark = None if market == "BIST30" else _STATE["benchmarks"].get(market)  # BIST has no index series
        prepared = tarama.prepare(card, data, market, benchmark=benchmark)
        first, second = prepared.run(1.0), prepared.run(2.0)
        m1, m2 = (calculate_metrics(r, annualization=prepared.annualization) for r in (first, second))
        real_pf, real_ortr, real_count = trade_stats(first.trades)
        base.update(islem=m1["islem"], PF_1x=m1["pf"], PF_2x=m2["pf"], net_1x=m1["getiri"], net_2x=m2["getiri"],
                    ort_r=real_ortr, tutma_gercek=holding_bars(first.trades, prepared.frames))
        if market == "BIST30":
            tl = _STATE["tl_rows"].get((card["id"], market), {})
            base.update(PF_1x_tl=tl.get("PF_1x"), net_1x_tl=tl.get("net_1x"))
            gate, why = tarama._stage_decision({"islem": m1["islem"], "PF_1x": m1["pf"], "net_2x": m2["getiri"]})
            base["usd_kapi"] = bool(gate)
            if not gate:
                base.update(karar="Reddedildi (BIST USD)", neden=f"USD: {why}")
                return base
        if real_count < 5:
            base.update(karar="Dogrulanamaz", neden="null testi icin islem yok/az")
            return base
        seed = BASE_SEED ^ zlib.crc32(f"{card['id']}|{market}".encode())
        reps = task["reps"]
        result = null_distribution(prepared, first.trades, reps, seed)
        p_pf, p_ortr = p_value(real_pf, result["pf"]), p_value(real_ortr, result["ortr"])
        if max(p_pf, p_ortr) >= BORDERLINE_P[0] and max(p_pf, p_ortr) <= BORDERLINE_P[1]:
            reps = task["reps_high"]
            result = null_distribution(prepared, first.trades, reps, seed + 1)
            p_pf, p_ortr = p_value(real_pf, result["pf"]), p_value(real_ortr, result["ortr"])
        pf95 = float(np.nanpercentile(result["pf"], PASS_PERCENTILE))
        ortr95 = float(np.nanpercentile(result["ortr"], PASS_PERCENTILE))
        passed = bool(real_pf > pf95 and real_ortr > ortr95)
        base.update(
            null_tekrar=reps, null_pf_p50=float(np.nanpercentile(result["pf"], 50)), null_pf_p95=pf95,
            null_ortr_p50=float(np.nanpercentile(result["ortr"], 50)), null_ortr_p95=ortr95,
            p_pf=p_pf, p_ortr=p_ortr, null_islem_ort=float(np.mean(result["count"])),
            tutma_null=float(np.nanmean(result["hold"])),
            karar="Gecti (null)" if passed else "Reddedildi (piyasa betasi)",
            neden="" if passed else f"PF p={p_pf:.3f}, ortR p={p_ortr:.3f} (esik {1 - PASS_PERCENTILE / 100:.2f})",
        )
    except Exception as exc:  # noqa: BLE001 - one broken pair must not stop the run
        base.update(karar="Hata", neden=f"{type(exc).__name__}: {exc}"[:200])
    return base


def load_candidates(results_dir: Path, card_dir: Path, only: set[str] | None) -> list[dict[str, Any]]:
    table = pd.read_csv(results_dir / "tarama.csv")
    chosen = table[table["asama2_aday"].fillna(False).astype(bool)]
    cards = {}
    for path in card_dir.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cards[data["id"]] = data
    tasks = []
    for row in chosen.itertuples():
        if only and row.id not in only:
            continue
        tasks.append({"card": cards[row.id], "market": row.piyasa})
    return tasks


def write_outputs(table: pd.DataFrame, results_dir: Path) -> None:
    table.to_csv(results_dir / "asama2a.csv", index=False, float_format="%.6g")
    lines = ["# Asama 2a: piyasa betasi testleri (T6a)", "",
             "BIST USD bazinda; rastgele giris (null) testi: PF ve ortalama R, null dagiliminin %95 yuzdeligini gecmeli.",
             "Donem: IS 2020-01-01 -> 2024-09-30 (OOS ve 2015-2019 kullanilmadi).", ""]
    verdicts: dict[str, list[str]] = {}
    for row in table.itertuples():
        verdicts.setdefault(row.id, []).append(row.karar)
    through = sorted(i for i, v in verdicts.items() if any(x == "Gecti (null)" for x in v))
    rejected = sorted(i for i in verdicts if i not in through)
    lines += [f"Kart: {len(verdicts)} | T6b'ye gecen: {len(through)} | elenen/dogrulanamaz: {len(rejected)}", "",
              "## Satir sonuclari", "",
              "| Kart | Piyasa | Para | Islem | PF | ortR | null PF p95 | null ortR p95 | p(PF) | p(ortR) | Tekrar | Karar |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    def f(value, fmt="{:.2f}"):
        return "-" if pd.isna(value) else fmt.format(value)
    for row in table.itertuples():
        lines.append(
            f"| {row.id} | {row.piyasa} | {row.para} | {f(row.islem, '{:.0f}')} | {f(row.PF_1x)} | {f(row.ort_r, '{:.3f}')} | "
            f"{f(row.null_pf_p95)} | {f(row.null_ortr_p95, '{:.3f}')} | {f(row.p_pf, '{:.3f}')} | {f(row.p_ortr, '{:.3f}')} | "
            f"{f(row.null_tekrar, '{:.0f}')} | {row.karar}{(': ' + row.neden) if isinstance(row.neden, str) and row.neden and row.karar != 'Gecti (null)' else ''} |"
        )
    lines += ["", "## Karar ozeti", "", f"- T6b'ye gecen kartlar: {', '.join(through) or '-'}",
              f"- Elenen kartlar (hicbir piyasada gecmedi): {', '.join(rejected) or '-'}", "",
              "## Notlar", "",
              "- Null model: ayni cikis kurallari ve portfoy limitleri; sembol basina ayni giris sayisi (rastgele barlar), "
              "toplam islem sayisini kartinkine yaklastirmak icin giris sayisi pilot kosuyla olceklenir; `null_islem_ort` ve `tutma_*` kontrol icindir.",
              "- Sinir bolgedeki satirlar (p 0,03-0,10) daha cok tekrarla yeniden kosulur.",
              "- BIST: USD fiyat = TL fiyat / ayni gun USDTRY kapanisi. TL sonucu `PF_1x_tl`, `net_1x_tl` sutunlarinda yalniz bilgi."]
    (results_dir / "asama2a_ozet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kartlar", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tekrar", type=int, default=200, help="null repetitions (borderline rows rerun with --tekrar-yuksek)")
    parser.add_argument("--tekrar-yuksek", type=int, default=1000)
    parser.add_argument("--kart-ids", default="")
    parser.add_argument("--isci", type=int, default=0, help="worker processes (0 = CPU count)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    only = {item.strip() for item in args.kart_ids.split(",") if item.strip()} or None
    tasks = load_candidates(args.results_dir, args.kartlar, only)
    markets = sorted({task["market"] for task in tasks})
    data, hashes = {}, {}
    for market in markets:
        data[market], hashes[market], _missing = _load_market(market, args.data_dir)
    usdtry_path = args.data_dir / "USDTRY_X.parquet"
    usd: dict[str, dict[str, pd.DataFrame]] = {}
    if "BIST30" in markets:
        if not usdtry_path.exists():
            raise SystemExit(f"{usdtry_path} yok: USDTRY=X gunluk verisini indirin (data.fetch.fetch_asset)")
        usd["BIST30"] = usd_frames(data["BIST30"], normalize_ohlcv(pd.read_parquet(usdtry_path)))
    benchmarks = {}
    for market, symbol in tarama.BENCHMARK_SYMBOL.items():
        if market in data:
            benchmarks[market] = data[market].get(symbol)
            if benchmarks[market] is None and (args.data_dir / f"{symbol}.parquet").exists():
                benchmarks[market] = normalize_ohlcv(pd.read_parquet(args.data_dir / f"{symbol}.parquet"))
    previous = pd.read_csv(args.results_dir / "tarama.csv")
    tl_rows = {(r.id, r.piyasa): {"PF_1x": r.PF_1x, "net_1x": r.net_1x} for r in previous.itertuples()}
    _STATE.update(data=data, usd=usd, benchmarks=benchmarks, hashes=hashes, tl_rows=tl_rows, git_sha=_git_sha())
    for task in tasks:
        task["reps"], task["reps_high"] = args.tekrar, args.tekrar_yuksek

    workers = args.isci or multiprocessing.cpu_count()
    rows = []
    if workers > 1 and len(tasks) > 1:
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for done, row in enumerate(pool.map(evaluate_pair, tasks), start=1):
                rows.append(row)
                print(f"[{done}/{len(tasks)}] {row['id']} {row['piyasa']}: {row['karar']}", flush=True)
    else:
        for done, task in enumerate(tasks, start=1):
            rows.append(evaluate_pair(task))
            print(f"[{done}/{len(tasks)}] {rows[-1]['id']} {rows[-1]['piyasa']}: {rows[-1]['karar']}", flush=True)
    table = pd.DataFrame(rows).reindex(columns=OUTPUT_COLUMNS)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    write_outputs(table, args.results_dir)
    print(f"{len(table)} satir, {int((table['karar'] == 'Gecti (null)').sum())} gecti")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
