#!/usr/bin/env python3
"""Kil payi denetimi (docs/DENETIM_KIL_PAYI.md, on kayitli tek seferlik ikinci bakis).

A. Asama 2a'da ``Reddedildi (piyasa betasi)`` olan her satir icin risk testi: getiri/|MDD|
   (portfoy ozkaynak egrisi), 2a'nin rastgele giris null'una karsi; tum satirlara birlikte
   Benjamini-Hochberg (q=0.10).
B. Asama 2b'de yalniz ``OOS ortR<=0`` ile elenen satirlar icin OOS gucu: OOS ortalama R'nin
   bootstrap %95 araligi ve IS ortalamasina karsi tek yonlu Welch t-testi.

Mevcut kararlar degismez; cikti ``results/denetim_kil_payi.{csv,md}``.
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
import math

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import asama2a, tarama  # noqa: E402
from backtests.asama2b import OOS_START  # noqa: E402
from backtests.run_codex21 import _load_market  # noqa: E402
from data.fetch import normalize_ohlcv  # noqa: E402
from engine.portfolio import calculate_metrics  # noqa: E402

SEED_SALT = 0x5249534B  # "RISK": keeps the risk null independent of the 2a null stream
BH_Q = 0.10
OOS_ALPHA = 0.05
OOS_BOOT = 10_000

_STATE: dict[str, Any] = {}


def risk_ratio(result, annualization: int) -> float:
    """getiri / |MDD| of the portfolio equity curve; a curve without drawdown is capped."""
    metrics = calculate_metrics(result, annualization=annualization)
    mdd = abs(float(metrics["mdd"]))
    getiri = float(metrics["getiri"])
    if not np.isfinite(getiri):
        return float("nan")
    return getiri / max(mdd, 1e-6)


def benjamini_hochberg(p_values: np.ndarray, q: float) -> np.ndarray:
    """Boolean mask of discoveries at FDR ``q`` (NaN p-values are never discoveries)."""
    p = np.asarray(p_values, dtype=float)
    mask = np.zeros(len(p), dtype=bool)
    valid = np.flatnonzero(np.isfinite(p))
    if not len(valid):
        return mask
    order = valid[np.argsort(p[valid], kind="stable")]
    thresholds = q * np.arange(1, len(order) + 1) / len(order)
    passed = np.flatnonzero(p[order] <= thresholds)
    if len(passed):
        mask[order[: passed[-1] + 1]] = True
    return mask


def risk_null(prepared: tarama.Prepared, real_trades: pd.DataFrame, reps: int, seed: int) -> np.ndarray:
    """2a's calibrated random-entry null, but every repetition keeps the full equity curve."""
    rng = np.random.default_rng(seed)
    per_symbol = real_trades["symbol"].value_counts().to_dict()
    target = len(real_trades)

    def one(factor: float, trades_only: bool):
        signals = asama2a.random_entry_signals(prepared, per_symbol, factor, rng)
        return prepared.run(1.0, signals=signals, trusted_inputs=True, trades_only=trades_only)

    factor = 1.0
    for _ in range(4):  # same calibration as asama2a.null_distribution
        counts = [len(one(factor, True).trades) for _ in range(asama2a.CALIBRATION_REPS)]
        mean_count = max(float(np.mean(counts)), 1.0)
        if abs(mean_count - target) / target <= 0.05:
            break
        factor = min(factor * target / mean_count, asama2a.MAX_ENTRY_FACTOR)
    return np.array([risk_ratio(one(factor, False), prepared.annualization) for _ in range(reps)])


def evaluate_risk(task: dict[str, Any]) -> dict[str, Any]:
    card, market = task["card"], task["market"]
    row: dict[str, Any] = {"bolum": "A", "id": card["id"], "piyasa": market, "tf": card["tf"]}
    try:
        key = (card["tf"], market)
        data = _STATE["usd"][key] if market == "BIST30" else _STATE["data"][key]
        benchmark = None if market == "BIST30" else _STATE["benchmarks"].get(key)
        start, end = tarama.period_for(card["tf"], market, data)
        prepared = tarama.prepare(card, data, market, benchmark=benchmark, start=start, end=end)
        real = prepared.run(1.0)
        metrics = calculate_metrics(real, annualization=prepared.annualization)
        ratio = risk_ratio(real, prepared.annualization)
        row.update(islem=len(real.trades), getiri=float(metrics["getiri"]), mdd=float(metrics["mdd"]), oran=ratio)
        seed = asama2a.BASE_SEED ^ SEED_SALT ^ zlib.crc32(f"{card['id']}|{market}".encode())
        reps = task["reps"]
        null = risk_null(prepared, real.trades, reps, seed)
        p = asama2a.p_value(ratio, null)
        if asama2a.BORDERLINE_P[0] <= p <= asama2a.BORDERLINE_P[1]:
            reps = task["reps_high"]
            null = risk_null(prepared, real.trades, reps, seed + 1)
            p = asama2a.p_value(ratio, null)
        row.update(
            tekrar=reps, null_oran_p50=float(np.nanpercentile(null, 50)),
            null_oran_p95=float(np.nanpercentile(null, 95)), p=p,
        )
    except Exception as exc:  # noqa: BLE001 - one broken pair must not stop the audit
        row.update(p=float("nan"), hata=f"{type(exc).__name__}: {exc}"[:200])
    return row


def load_scope_a(results_dir: Path, card_dir: Path, timeframes: set[str]) -> list[dict[str, Any]]:
    table = pd.read_csv(results_dir / "asama2a.csv")
    scope = table[table["karar"] == "Reddedildi (piyasa betasi)"]
    cards = {}
    for path in card_dir.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cards[data["id"]] = data
    return [
        {"card": cards[row.id], "market": row.piyasa}
        for row in scope.itertuples()
        if str(row.tf) in timeframes and row.id in cards and cards[row.id].get("tf") == str(row.tf)
    ]


def load_state(tasks: list[dict[str, Any]], data_dir: Path, veri_kok: Path) -> None:
    """Same market data, USD conversion and benchmarks as asama2a.main."""
    keys = sorted({(task["card"]["tf"], task["market"]) for task in tasks})
    data, usd, benchmarks = {}, {}, {}
    for tf, market in keys:
        directory = data_dir if tf in tarama.DAILY_TFS else veri_kok / tarama.TF_DIR[tf]
        data[(tf, market)], _hash, _missing = _load_market(market, directory)
        if tf in tarama.DAILY_TFS and market == "BIST30":
            usdtry = normalize_ohlcv(pd.read_parquet(data_dir / "USDTRY_X.parquet"))
            usd[(tf, market)] = asama2a.usd_frames(data[(tf, market)], usdtry)
        symbol = tarama.BENCHMARK_SYMBOL.get(market)
        if symbol:
            benchmarks[(tf, market)] = data[(tf, market)].get(symbol)
            if benchmarks[(tf, market)] is None and (directory / f"{symbol}.parquet").exists():
                benchmarks[(tf, market)] = normalize_ohlcv(pd.read_parquet(directory / f"{symbol}.parquet"))
    _STATE.update(data=data, usd=usd, benchmarks=benchmarks)


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction of the regularised incomplete beta (Numerical Recipes 6.4)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
            c = 1.0 + aa / c
            c = c if abs(c) > 1e-300 else 1e-300
            h *= d * c
        if abs(d * c - 1.0) < 1e-12:
            break
    return h


def student_t_cdf(t: float, df: float) -> float:
    """CDF of Student's t (no scipy in requirements)."""
    if t == 0:
        return 0.5
    x = df / (df + t * t)
    front = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2) - math.lgamma(0.5)
                     + (df / 2) * math.log(x) + 0.5 * math.log1p(-x))
    a, b = df / 2, 0.5
    if x < (a + 1) / (a + b + 2):
        ibeta = front * _betacf(a, b, x) / a
    else:
        front_c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2) - math.lgamma(0.5)
                           + b * math.log1p(-x) + a * math.log(x))
        ibeta = 1.0 - front_c * _betacf(b, a, 1.0 - x) / b
    tail = 0.5 * ibeta
    return 1.0 - tail if t > 0 else tail


def welch_less(sample: np.ndarray, reference: np.ndarray) -> float:
    """One-sided Welch t-test p-value for mean(sample) < mean(reference)."""
    v1, v2 = sample.var(ddof=1) / len(sample), reference.var(ddof=1) / len(reference)
    t = (sample.mean() - reference.mean()) / math.sqrt(v1 + v2)
    df = (v1 + v2) ** 2 / (v1 ** 2 / (len(sample) - 1) + v2 ** 2 / (len(reference) - 1))
    return student_t_cdf(t, df)


def bootstrap_mean_ci(values: np.ndarray, reps: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = rng.choice(values, size=(reps, len(values)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def evaluate_oos(card: dict[str, Any], market: str, data_dir: Path) -> dict[str, Any]:
    data, _hash, _missing = _load_market(market, data_dir)
    symbol = tarama.BENCHMARK_SYMBOL.get(market)
    benchmark = data.get(symbol) if symbol else None
    final = max(frame.index.max() for frame in data.values())
    is_trades = tarama.prepare(card, data, market, benchmark=benchmark, start=tarama.IS_START, end=tarama.IS_END).run().trades
    oos_trades = tarama.prepare(card, data, market, benchmark=benchmark, start=OOS_START, end=final).run().trades
    is_r = is_trades["r_multiple"].dropna().to_numpy(dtype=float)
    oos_r = oos_trades["r_multiple"].dropna().to_numpy(dtype=float)
    low, high = bootstrap_mean_ci(oos_r, OOS_BOOT, zlib.crc32(f"{card['id']}|{market}|oos".encode()))
    p_value = welch_less(oos_r, is_r)
    worse = bool(p_value < OOS_ALPHA)
    return {
        "bolum": "B", "id": card["id"], "piyasa": market, "tf": card["tf"],
        "is_islem": len(is_r), "is_ort_r": float(is_r.mean()), "oos_islem": len(oos_r), "oos_ort_r": float(oos_r.mean()),
        "oos_ci_alt": low, "oos_ci_ust": high, "p": float(p_value),
        "karar": "Reddedildi (OOS IS'ten anlamli kotu)" if worse else "Belirsiz (OOS gucu yetersiz)",
    }


def write_report(table: pd.DataFrame, results_dir: Path) -> None:
    a, b = table[table["bolum"] == "A"], table[table["bolum"] == "B"]
    lines = [
        "# Kil payi denetimi", "",
        "On kayit: `docs/DENETIM_KIL_PAYI.md`. Mevcut kararlar degismez.", "",
        f"## A. Risk testi (getiri/|MDD| vs rastgele giris; BH q={BH_Q})", "",
        f"- Test edilen satir: {len(a)}; ham p<0.05: {int((a['p'] < 0.05).sum())}; "
        f"BH sonrasi kesif: {int(a['bh_kesif'].sum())}", "",
    ]
    if len(a):
        shown = a.sort_values("p").head(20)
        lines += ["En dusuk p'li 20 satir:", "", "| id | piyasa | tf | islem | getiri | MDD | oran | null p95 | p | BH |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for r in shown.itertuples():
            lines.append(f"| {r.id} | {r.piyasa} | {r.tf} | {r.islem:.0f} | {r.getiri:.3f} | {r.mdd:.3f} | {r.oran:.2f} | "
                         f"{r.null_oran_p95:.2f} | {r.p:.3f} | {'evet' if r.bh_kesif else 'hayir'} |")
    lines += ["", f"## B. OOS gucu (Welch tek yonlu, alfa={OOS_ALPHA})", ""]
    if len(b):
        lines += ["| id | piyasa | IS islem | IS ortR | OOS islem | OOS ortR | OOS %95 aralik | p | karar |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r in b.itertuples():
            lines.append(f"| {r.id} | {r.piyasa} | {r.is_islem} | {r.is_ort_r:.3f} | {r.oos_islem} | {r.oos_ort_r:.3f} | "
                         f"[{r.oos_ci_alt:.3f}, {r.oos_ci_ust:.3f}] | {r.p:.3f} | {r.karar} |")
    (results_dir / "denetim_kil_payi.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kartlar", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--tf", default="1D,1W,1H")
    parser.add_argument("--tekrar", type=int, default=200)
    parser.add_argument("--tekrar-yuksek", type=int, default=1000)
    parser.add_argument("--isci", type=int, default=0)
    args = parser.parse_args()
    tarama.FIXED_DATA_DIR = args.data_dir
    timeframes = {item.strip() for item in args.tf.split(",") if item.strip()}
    cards = {yaml.safe_load(p.read_text(encoding="utf-8"))["id"]: yaml.safe_load(p.read_text(encoding="utf-8"))
             for p in args.kartlar.glob("*.yaml")}

    rows = []
    stage2b = pd.read_csv(args.results_dir / "asama2b.csv")
    for r in stage2b[stage2b["neden"] == "OOS ortR<=0"].itertuples():
        rows.append(evaluate_oos(cards[r.id], r.piyasa, args.data_dir))
        print(f"[B] {r.id} {r.piyasa}: {rows[-1]['karar']}", flush=True)

    tasks = load_scope_a(args.results_dir, args.kartlar, timeframes)
    load_state(tasks, args.data_dir, args.veri_kok)
    for task in tasks:
        task["reps"], task["reps_high"] = args.tekrar, args.tekrar_yuksek
    workers = args.isci or multiprocessing.cpu_count()
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
        for done, row in enumerate(pool.map(evaluate_risk, tasks), start=1):
            rows.append(row)
            print(f"[A {done}/{len(tasks)}] {row['id']} {row['piyasa']} {row['tf']}: p={row.get('p', float('nan')):.3f}", flush=True)

    table = pd.DataFrame(rows)
    is_a = table["bolum"] == "A"
    table["bh_kesif"] = False
    table.loc[is_a, "bh_kesif"] = benjamini_hochberg(table.loc[is_a, "p"].to_numpy(), BH_Q)
    table.loc[is_a, "karar"] = np.where(table.loc[is_a, "bh_kesif"], "Asama 2b'ye (risk kenari)", "Reddedildi kalir")
    args.results_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.results_dir / "denetim_kil_payi.csv", index=False)
    write_report(table, args.results_dir)
    print(f"A: {int(is_a.sum())} satir, {int(table['bh_kesif'].sum())} BH kesfi; B: {int((~is_a).sum())} satir")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
