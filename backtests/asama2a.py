#!/usr/bin/env python3
"""Stage 2a: market-beta tests (T6a) for the stage 1 candidates.

1. BIST rows are re-run on USD prices (price / USDTRY close of the same day); the decision
   uses the USD result, the TL result is information only.
2. Random-entry null model: same exit rules, same per-symbol number of entries (calibrated so
   the null produces about as many trades as the card), random entry bars. The card must beat
   the 95th percentile of the null distribution for both PF and mean R, otherwise the edge is
   the market's drift: ``Reddedildi (piyasa betasi)``.

Only the stage-1 in-sample period is used; OOS and the pre-period stay unseen. Daily and
crypto intraday use 2020-01-01 -> 2024-09-30; yfinance 1H uses the archive's first 2/3.
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

from backtests import rotasyon_asama2 as rot  # noqa: E402
from backtests import tarama  # noqa: E402
from backtests.run_codex21 import _git_sha, _load_market  # noqa: E402
from data.fetch import normalize_ohlcv  # noqa: E402
from engine.portfolio import calculate_metrics  # noqa: E402

BASE_SEED = 20261022
CALIBRATION_REPS = 6
MAX_ENTRY_FACTOR = 8.0
NULL_WORKER_DATA_FACTOR = 1.0  # a forked null worker adds about the size of the bar data (T30 measurement)
PF_CAP = 1e9  # an infinite PF (no losing trade) is capped so percentiles stay finite
PASS_PERCENTILE = 95.0
BORDERLINE_P = (0.03, 0.10)
SUPPORTED_TFS = (*tarama.DAILY_TFS, *tarama.RESAMPLED_HOURLY_TFS, "1H", "30m", "15m", "5m")

OUTPUT_COLUMNS = [
    "id", "piyasa", "tf", "kart_yazari", "para", "islem", "PF_1x", "PF_2x", "net_1x", "net_2x", "ort_r",
    "PF_1x_tl", "net_1x_tl", "usd_kapi", "null_tekrar", "null_pf_p50", "null_pf_p95", "null_ortr_p50",
    "null_ortr_p95", "p_pf", "p_ortr", "null_islem_ort", "tutma_gercek", "tutma_null", "karar", "neden",
    "data_hash", "git_sha", "metrik",
]

_STATE: dict[str, Any] = {}  # filled before the worker pool forks
_NULL_PREPARED: tarama.Prepared | None = None  # inherited by intraday repetition workers (fork)


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


def _one_null(args: tuple[float, int]) -> tuple[float, float, int, float]:
    """Run one null draw in a forked worker without serialising the large intraday archive."""
    factor, seed = args
    if _NULL_PREPARED is None:  # pragma: no cover - protects unsupported multiprocessing start methods
        raise RuntimeError("null worker was not initialised")
    rng = np.random.default_rng(seed)
    per_symbol = _STATE["null_per_symbol"]
    signals = random_entry_signals(_NULL_PREPARED, per_symbol, factor, rng)
    trades = _NULL_PREPARED.run(1.0, signals=signals, trusted_inputs=True, trades_only=True).trades
    pf, ortr, count = trade_stats(trades)
    return pf, ortr, count, holding_bars(trades, _NULL_PREPARED.frames)


def null_distribution(
    prepared: tarama.Prepared,
    real_trades: pd.DataFrame,
    reps: int,
    seed: int,
    workers: int = 1,
) -> dict[str, Any]:
    """Build the null distribution; intraday repetitions can run concurrently.

    The workers use ``fork`` so the potentially multi-gigabyte prepared archive remains
    copy-on-write shared.  The default path is deliberately the original serial RNG stream,
    which keeps every daily result reproducible byte for byte.
    """
    rng = np.random.default_rng(seed)
    per_symbol = real_trades["symbol"].value_counts().to_dict()
    target = len(real_trades)

    def one(factor: float):
        signals = random_entry_signals(prepared, per_symbol, factor, rng)
        return prepared.run(1.0, signals=signals, trusted_inputs=True, trades_only=True).trades

    factor = 1.0
    if workers <= 1:
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
    else:
        global _NULL_PREPARED
        _NULL_PREPARED = prepared
        _STATE["null_per_symbol"] = per_symbol
        # A single pool is retained through calibration and the measured repetitions.
        with ProcessPoolExecutor(
            max_workers=workers, mp_context=multiprocessing.get_context("fork")
        ) as pool:
            for _ in range(4):
                seeds = rng.integers(0, np.iinfo(np.uint32).max, size=CALIBRATION_REPS, dtype=np.uint32)
                samples = list(pool.map(_one_null, [(factor, int(item)) for item in seeds]))
                mean_count = max(float(np.mean([item[2] for item in samples])), 1.0)
                if abs(mean_count - target) / target <= 0.05:
                    break
                factor = min(factor * target / mean_count, MAX_ENTRY_FACTOR)
            seeds = rng.integers(0, np.iinfo(np.uint32).max, size=reps, dtype=np.uint32)
            samples = list(pool.map(_one_null, [(factor, int(item)) for item in seeds]))
        pf, ortr, count, hold = map(list, zip(*samples, strict=True))
        _NULL_PREPARED = None
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
                data_hash=_STATE["hashes"][(card["tf"], market)], metrik="PF+ortR")
    try:
        key = (card["tf"], market)
        data = _STATE["usd"][key] if market == "BIST30" else _STATE["data"][key]
        benchmark = None if market == "BIST30" else _STATE["benchmarks"].get(key)  # BIST has no index series
        start, end = tarama.period_for(card["tf"], market, data)
        prepared = tarama.prepare(card, data, market, benchmark=benchmark, start=start, end=end)
        if isinstance(prepared, rot.RotationPrepared):
            return evaluate_rotation(task, base, prepared)
        intraday = card["tf"] not in tarama.DAILY_TFS  # daily rows keep the engine's defensive copies (locked regression)
        first, second = prepared.run(1.0, trusted_inputs=intraday), prepared.run(2.0, trusted_inputs=intraday)
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
        null_workers = tarama.bellek_isci(task.get("null_workers", 1), data, is_basina=NULL_WORKER_DATA_FACTOR)
        result = null_distribution(prepared, first.trades, reps, seed, null_workers)
        p_pf, p_ortr = p_value(real_pf, result["pf"]), p_value(real_ortr, result["ortr"])
        if max(p_pf, p_ortr) >= BORDERLINE_P[0] and max(p_pf, p_ortr) <= BORDERLINE_P[1]:
            reps = task["reps_high"]
            result = null_distribution(prepared, first.trades, reps, seed + 1, null_workers)
            p_pf, p_ortr = p_value(real_pf, result["pf"]), p_value(real_ortr, result["ortr"])
        prepared.runtime_cache.clear()  # engine arrays of the real run (shared with the forked null workers)
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


def evaluate_rotation(task: dict[str, Any], base: dict[str, Any], prepared: rot.RotationPrepared) -> dict[str, Any]:
    """Rotation card (T23): same gates as ``evaluate_pair`` but the null randomises the selection and compares PF **and CAGR**
    (there is no per-trade stop, hence no R multiple): ``metrik: PF+CAGR``. ``ort_r`` / ``null_ortr_*`` / ``p_ortr`` carry the CAGR."""
    card, market = task["card"], task["market"]
    base["metrik"] = rot.METRIC
    first, second = prepared.run(1.0), prepared.run(2.0)
    m1, m2 = (calculate_metrics(r, annualization=prepared.annualization) for r in (first, second))
    real_pf, real_cagr, real_count = rot.stats(first, prepared.annualization)
    base.update(islem=m1["islem"], PF_1x=m1["pf"], PF_2x=m2["pf"], net_1x=m1["getiri"], net_2x=m2["getiri"],
                ort_r=real_cagr, tutma_gercek=rot.holding_days(first.trades))
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
    result = rot.null_distribution(prepared, reps, seed)
    p_pf, p_cagr = p_value(real_pf, result["pf"]), p_value(real_cagr, result["cagr"])
    if BORDERLINE_P[0] <= max(p_pf, p_cagr) <= BORDERLINE_P[1]:
        reps = task["reps_high"]
        result = rot.null_distribution(prepared, reps, seed + 1)
        p_pf, p_cagr = p_value(real_pf, result["pf"]), p_value(real_cagr, result["cagr"])
    pf95 = float(np.nanpercentile(result["pf"], PASS_PERCENTILE))
    cagr95 = float(np.nanpercentile(result["cagr"], PASS_PERCENTILE))
    passed = bool(real_pf > pf95 and real_cagr > cagr95)
    base.update(
        null_tekrar=reps, null_pf_p50=float(np.nanpercentile(result["pf"], 50)), null_pf_p95=pf95,
        null_ortr_p50=float(np.nanpercentile(result["cagr"], 50)), null_ortr_p95=cagr95,
        p_pf=p_pf, p_ortr=p_cagr, null_islem_ort=float(np.mean(result["count"])), tutma_null=float(np.nanmean(result["hold"])),
        karar="Gecti (null)" if passed else "Reddedildi (piyasa betasi)",
        neden="" if passed else f"PF p={p_pf:.3f}, CAGR p={p_cagr:.3f} (esit {1 - PASS_PERCENTILE / 100:.2f})",
    )
    return base


def load_candidates(
    results_dir: Path,
    card_dir: Path,
    only: set[str] | None,
    timeframes: set[str] | None = None,
) -> list[dict[str, Any]]:
    table = pd.read_csv(results_dir / "tarama.csv")
    rotation_scan = results_dir / "tarama_rotasyon.csv"  # T22/T23: rotation cards are scanned into their own file
    if rotation_scan.exists():
        table = pd.concat([table, pd.read_csv(rotation_scan)], ignore_index=True)
        table = table.drop_duplicates(["id", "piyasa"], keep="last")
    chosen = table[table["asama2_aday"].fillna(False).astype(bool)]
    cards = {}
    for path in card_dir.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cards[data["id"]] = data
    tasks = []
    for row in chosen.itertuples():
        if only and row.id not in only:
            continue
        tf = str(row.tf)
        if timeframes is not None and tf not in timeframes:
            continue
        if tf not in SUPPORTED_TFS or cards[row.id]["tf"] != tf:
            continue
        if tf == "1H" and row.piyasa == "BIST30":
            continue  # D9/T17: remains Dogrulanamaz until the hourly quality issue is fixed
        tasks.append({"card": cards[row.id], "market": row.piyasa})
    return tasks


def merge_selected_results(
    existing: pd.DataFrame, fresh: pd.DataFrame, timeframes: set[str], only: set[str] | None = None
) -> pd.DataFrame:
    """Replace selected TF rows (only the ``--kart-ids`` cards when given) while preserving the other results exactly."""
    if existing.empty:
        return fresh
    replaced = existing["tf"].astype(str).isin(timeframes)
    if only:
        replaced &= existing["id"].astype(str).isin(only)
    kept = existing[~replaced]
    return pd.concat([kept, fresh], ignore_index=True).reindex(columns=OUTPUT_COLUMNS)


def write_outputs(table: pd.DataFrame, results_dir: Path) -> None:
    table.to_csv(results_dir / "asama2a.csv", index=False, float_format="%.6g")
    lines = ["# Asama 2a: piyasa betasi testleri (T6a/T17)", "",
             "BIST USD bazinda; rastgele giris (null) testi: PF ve ortalama R, null dagiliminin %95 yuzdeligini gecmeli.",
             "Donem: gunluk ve kripto gun ici 2020-01-01 -> 2024-09-30; yfinance 1H arsivinin ilk 2/3'u "
             "(OOS ve on donem kullanilmadi).", ""]
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
              "- Rotasyon kartlari (T23, `metrik: PF+CAGR`): islem basina stop/R yok; null modelde takvim, N, maliyet ve yurutme kartinki, yalniz secim rastgele "
              "(kesitsel/sirali: rastgele siralama, filtre ve rejim kapisi ayni; gecis: ayni gecis tarihlerinde agacin enstrumanlarindan biri). "
              "PF ve CAGR null %95'inin ustunde olmali; `ort_r`, `null_ortr_*`, `p_ortr` sutunlari bu satirlarda CAGR tasir.",
              "- Gun ici arsivleri `--veri-kok` altindan okunur; BIST 1H veri kalitesi duzelene kadar null testine alinmaz.",
              "- BIST: USD fiyat = TL fiyat / ayni gun USDTRY kapanisi. TL sonucu `PF_1x_tl`, `net_1x_tl` sutunlarinda yalniz bilgi."]
    (results_dir / "asama2a_ozet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kartlar", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data", help="hourly/30m/15m/5m archive root")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tf", default="1D,1W", help="comma separated timeframes: 1D,1W,1H,2H,4H,30m,15m,5m")
    parser.add_argument("--tekrar", type=int, default=200, help="null repetitions (borderline rows rerun with --tekrar-yuksek)")
    parser.add_argument("--tekrar-yuksek", type=int, default=1000)
    parser.add_argument("--kart-ids", default="")
    parser.add_argument("--isci", type=int, default=0, help="worker processes (0 = CPU count)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tarama.FIXED_DATA_DIR = args.data_dir
    only = {item.strip() for item in args.kart_ids.split(",") if item.strip()} or None
    timeframes = {item.strip() for item in args.tf.split(",") if item.strip()}
    invalid = timeframes.difference(SUPPORTED_TFS)
    if invalid:
        raise SystemExit(f"desteklenmeyen tf: {','.join(sorted(invalid))}")
    tasks = load_candidates(args.results_dir, args.kartlar, only, timeframes)
    keys = sorted({(task["card"]["tf"], task["market"]) for task in tasks})
    data, hashes = {}, {}
    for tf, market in keys:
        directory = args.data_dir if tf in tarama.DAILY_TFS else args.veri_kok / tarama.TF_DIR[tf]
        data[(tf, market)], hashes[(tf, market)], _missing = _load_market(market, directory)
    usdtry_path = args.data_dir / "USDTRY_X.parquet"
    usd: dict[tuple[str, str], dict[str, pd.DataFrame]] = {}
    if any(tf in tarama.DAILY_TFS and market == "BIST30" for tf, market in keys):
        if not usdtry_path.exists():
            raise SystemExit(f"{usdtry_path} yok: USDTRY=X gunluk verisini indirin (data.fetch.fetch_asset)")
        for tf, market in keys:
            if tf in tarama.DAILY_TFS and market == "BIST30":
                usd[(tf, market)] = usd_frames(data[(tf, market)], normalize_ohlcv(pd.read_parquet(usdtry_path)))
    benchmarks = {}
    for tf, market in keys:
        symbol = tarama.BENCHMARK_SYMBOL.get(market)
        if symbol:
            directory = args.data_dir if tf in tarama.DAILY_TFS else args.veri_kok / tarama.TF_DIR[tf]
            benchmarks[(tf, market)] = data[(tf, market)].get(symbol)
            if benchmarks[(tf, market)] is None and (directory / f"{symbol}.parquet").exists():
                benchmarks[(tf, market)] = normalize_ohlcv(pd.read_parquet(directory / f"{symbol}.parquet"))
    previous = pd.read_csv(args.results_dir / "tarama.csv")
    if (args.results_dir / "tarama_rotasyon.csv").exists():
        previous = pd.concat([previous, pd.read_csv(args.results_dir / "tarama_rotasyon.csv")], ignore_index=True)
    tl_rows = {(r.id, r.piyasa): {"PF_1x": r.PF_1x, "net_1x": r.net_1x} for r in previous.itertuples()}
    _STATE.update(data=data, usd=usd, benchmarks=benchmarks, hashes=hashes, tl_rows=tl_rows, git_sha=_git_sha())
    for task in tasks:
        task["reps"], task["reps_high"] = args.tekrar, args.tekrar_yuksek

    workers = args.isci or multiprocessing.cpu_count()
    rows = []
    intraday = any(task["card"]["tf"] not in tarama.DAILY_TFS for task in tasks)
    if not intraday and workers > 1 and len(tasks) > 1:
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for done, row in enumerate(pool.map(evaluate_pair, tasks), start=1):
                rows.append(row)
                print(f"[{done}/{len(tasks)}] {row['id']} {row['piyasa']}: {row['karar']}", flush=True)
    else:
        for done, task in enumerate(tasks, start=1):
            task["null_workers"] = workers if task["card"]["tf"] not in tarama.DAILY_TFS else 1
            rows.append(evaluate_pair(task))
            print(f"[{done}/{len(tasks)}] {rows[-1]['id']} {rows[-1]['piyasa']}: {rows[-1]['karar']}", flush=True)
    table = pd.DataFrame(rows).reindex(columns=OUTPUT_COLUMNS)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.results_dir / "asama2a.csv"
    if output_path.exists() and (only or not timeframes.issuperset(SUPPORTED_TFS)):
        table = merge_selected_results(pd.read_csv(output_path), table, timeframes, only)
    write_outputs(table, args.results_dir)
    print(f"{len(table)} satir, {int((table['karar'] == 'Gecti (null)').sum())} gecti")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
