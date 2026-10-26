"""Kapı kontrolü için maruziyet-eşleşmiş giriş plasebosu.

Bu modül yeni bir backtest motoru değildir. ``tv2`` ve ``u7``nin kaydettiği
günlük net getiri serilerini kullanır; açık gün bloklarını aynı uzunluklarda
rastgele günlere yerleştirip ilgili piyasa getirisini uygular. Böylece işlem
sayısı ve tutma süresi korunur.  Tohum kimlikten türetilir.
"""
from __future__ import annotations

import argparse
import json
import math
import zlib
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
REPS = 1000


def deflated_sharpe_ratio(returns: pd.Series, trials: int) -> float:
    """Local DSR implementation; keeps this reporting tool independent of the card runner."""
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 3 or np.std(values, ddof=1) == 0:
        return np.nan
    sr = float(values.mean() / np.std(values, ddof=1))
    centered = values - values.mean()
    skew = float(np.mean(centered**3) / np.mean(centered**2) ** 1.5)
    kurtosis = float(np.mean(centered**4) / np.mean(centered**2) ** 2)
    std = math.sqrt(max(1 - skew * sr + (kurtosis - 1) * sr * sr / 4, 0) / (len(values) - 1))
    hurdle = 0.0
    if trials > 1:
        normal, gamma = NormalDist(), 0.5772156649015329
        hurdle = std * ((1 - gamma) * normal.inv_cdf(1 - 1 / trials) + gamma * normal.inv_cdf(1 - 1 / (trials * math.e)))
    z = (sr - hurdle) / std if std else 0.0
    return NormalDist().cdf(z)


def active_blocks(exposure: pd.Series) -> list[int]:
    """Return consecutive non-zero exposure lengths (including a final block)."""
    on = exposure.fillna(0).to_numpy(dtype=float) != 0
    starts = np.flatnonzero(on & np.r_[True, ~on[:-1]])
    ends = np.flatnonzero(on & np.r_[~on[1:], True])
    return [int(end - start + 1) for start, end in zip(starts, ends, strict=True)]


def random_exposure(index: pd.Index, blocks: list[int], rng: np.random.Generator) -> pd.Series:
    """Place every holding block once, without overlap; preserve count and durations."""
    if not blocks:
        return pd.Series(0.0, index=index)
    # One empty day between blocks keeps adjacent trades distinct.  Sampling
    # the surplus gaps directly avoids a greedy placement getting trapped.
    required = sum(blocks) + len(blocks) - 1
    if required > len(index):
        raise ValueError("blocks do not fit in the requested period")
    gaps = rng.multinomial(len(index) - required, np.full(len(blocks) + 1, 1 / (len(blocks) + 1)))
    taken = np.zeros(len(index), dtype=bool)
    cursor = int(gaps[0])
    for position, item in enumerate(rng.permutation(len(blocks))):
        length = blocks[int(item)]
        taken[cursor:cursor + length] = True
        cursor += length + 1 + int(gaps[position + 1])
    return pd.Series(taken.astype(float), index=index)


def placebo_distribution(
    market: pd.Series, exposure: pd.Series, *, repetitions: int = REPS, seed: int = 0,
    round_trip_cost: float = 0.001,
) -> np.ndarray:
    """Net-return distribution for random entries with identical holding blocks.

    ``round_trip_cost`` is charged once for each preserved block.  It is a
    conservative daily representation of the existing realistic cost model.
    """
    market = pd.to_numeric(market, errors="coerce").fillna(0.0)
    blocks = active_blocks(exposure.reindex(market.index, fill_value=0.0))
    if not blocks:
        return np.zeros(repetitions)
    rng = np.random.default_rng(seed)
    totals = np.empty(repetitions)
    for i in range(repetitions):
        w = random_exposure(market.index, blocks, rng)
        starts = int(((w > 0) & (w.shift(fill_value=0) == 0)).sum())
        totals[i] = float(np.prod(1 + w.to_numpy() * market.to_numpy()) - 1 - starts * round_trip_cost)
    return totals


def nw_alpha(strategy: pd.Series, benchmark: pd.Series, lags: int = 5) -> dict[str, float]:
    """Annualised OLS alpha/beta and Newey-West t statistic for alpha."""
    frame = pd.concat([strategy.rename("y"), benchmark.rename("x")], axis=1).dropna()
    if len(frame) < 8 or frame.x.var() == 0:
        return {"beta": np.nan, "alfa_yillik": np.nan, "nw_t": np.nan}
    x = np.column_stack([np.ones(len(frame)), frame.x.to_numpy()])
    y = frame.y.to_numpy()
    inv = np.linalg.inv(x.T @ x)
    coef = inv @ x.T @ y
    residual = y - x @ coef
    meat = np.zeros((2, 2))
    for lag in range(min(lags, len(frame) - 1) + 1):
        weight = 1.0 if lag == 0 else 1 - lag / (lags + 1)
        if lag == 0:
            term = (x * residual[:, None]).T @ (x * residual[:, None])
        else:
            term = (x[lag:] * residual[lag:, None]).T @ (x[:-lag] * residual[:-lag, None])
            term = term + term.T
        meat += weight * term
    se = math.sqrt(max(float((inv @ meat @ inv)[0, 0]), 0.0))
    return {"beta": float(coef[1]), "alfa_yillik": float(coef[0] * 252), "nw_t": float(coef[0] / se) if se else np.nan}


def neff_clusters(series: dict[str, pd.Series], threshold: float = 0.9) -> int:
    """Hierarchical single-link correlation clusters, returned as N_eff."""
    keys = list(series)
    parent = list(range(len(keys)))
    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    def join(a: int, b: int) -> None:
        a, b = find(a), find(b)
        if a != b: parent[b] = a
    frame = pd.concat(series, axis=1).fillna(0.0)
    for i in range(len(keys)):
        for j in range(i):
            if frame.iloc[:, i].std() and frame.iloc[:, j].std() and frame.iloc[:, i].corr(frame.iloc[:, j]) >= threshold:
                join(i, j)
    return len({find(i) for i in range(len(keys))})


def _returns(path: Path) -> pd.Series:
    table = pd.read_csv(path, index_col=0, parse_dates=True)
    value = "getiri" if "getiri" in table else "net_getiri"
    out = pd.to_numeric(table[value], errors="coerce").fillna(0.0)
    out.index = pd.to_datetime(out.index, utc=True)
    return out


def _market(kind: str, index: pd.Index) -> pd.Series:
    """Obtain the fixed class benchmark through the existing TV-2 data adapter."""
    from backtests.tv2 import veri
    symbol = {"ABD": "AMEX:SPY", "Kripto": "BINANCE:BTCUSDT", "Emtia": "AMEX:GLD"}[kind]
    data, note = veri(symbol, "1D")
    # The repository's immutable hourly cache is the offline fallback for the
    # two ETF controls.  It is still the same market-data input, just avoids a
    # transient public-yfinance outage from turning an entire report into NA.
    if data is None and kind in {"ABD", "Emtia"}:
        cached = ROOT / "data" / "hourly" / ("SPY.parquet" if kind == "ABD" else "GLD.parquet")
        if cached.exists():
            data = pd.read_parquet(cached).resample("1D").last().dropna(subset=["close"])
    if data is None:
        raise RuntimeError(note)
    returns = data["close"].pct_change().reindex(index).fillna(0.0)
    return returns


def _u7_rows() -> list[dict[str, object]]:
    table = pd.read_csv(OUT / "u7" / "huni_ozet.csv")
    rows = []
    for _, row in table.iterrows():
        if row.get("karar_adim2") != "Geçti":
            continue
        variant, group = str(row["varyant"]), str(row["grup"])
        path = OUT / "u7" / group / "getiriler" / (variant.replace(":", "_") + ".csv")
        if path.exists():
            rows.append({"id": variant, "kaynak": "U7", "piyasa": str(row.get("piyasa")), "tf": str(row.get("tf")), "path": path})
            rows[-1].update({"null_gecti_eski": row.get("null_gecti"), "p_pf_eski": row.get("p_pf"), "p_ortr_eski": row.get("p_ortr")})
    return rows


def _tv_rows() -> list[dict[str, object]]:
    rows = []
    for path in sorted((OUT / "tv2" / "satirlar").glob("*.json")):
        item = json.loads(path.read_text())
        result = OUT / "tv2" / "getiriler" / f"{item.get('id')}.csv"
        if item.get("karar") == "gecti" and result.exists():
            rows.append({"id": item["id"], "kaynak": "TV-2", "piyasa": str(item.get("sembol", "")), "tf": str(item.get("tf")), "path": result,
                         "surum": item.get("surum_tarihi")})
    return rows


def _kind(row: dict[str, object]) -> str:
    text = str(row["piyasa"]).upper()
    return "Kripto" if "KRIPTO" in text or any(x in text for x in ("BINANCE", "COINBASE", "KRAKEN", "BYBIT", "BITFINEX")) else "Emtia" if "EMTIA" in text else "ABD"


def evaluate(row: dict[str, object], repetitions: int = REPS) -> tuple[dict[str, object], pd.Series]:
    returns = _returns(Path(row["path"]))
    if row.get("surum"):
        returns = returns.loc[returns.index >= pd.Timestamp(row["surum"], tz="UTC")]
    kind = _kind(row)
    market = _market(kind, returns.index)
    # Daily zero returns are the persisted observable proxy for flat exposure.
    exposure = (returns != 0).astype(float)
    benchmark = exposure * market
    null = placebo_distribution(market, exposure, repetitions=repetitions,
                                seed=zlib.crc32(str(row["id"]).encode()),
                                round_trip_cost=0.002 if kind == "Kripto" else 0.001)
    real = float(np.prod(1 + returns) - 1)
    alpha = nw_alpha(returns, benchmark)
    return ({"kimlik": row["id"], "kaynak": row["kaynak"], "piyasa": row["piyasa"], "tf": row["tf"],
             "maruziyet": float(exposure.mean()), "gercek_net": real, "kiyas_net": float(np.prod(1 + benchmark) - 1),
             "fark_yillik": float((returns - benchmark).mean() * 252), **alpha,
             "plasebo_p50": float(np.percentile(null, 50)), "plasebo_p95": float(np.percentile(null, 95)),
             "plasebo_pozitif_oran": float(np.mean(null > 0)), "plasebo_yuzdelik": float(np.mean(null <= real)),
             "p_degeri": float((1 + np.sum(null >= real)) / (1 + len(null))),
             "null_gecti_eski": row.get("null_gecti_eski"), "p_pf_eski": row.get("p_pf_eski"),
             "p_ortr_eski": row.get("p_ortr_eski")} , returns)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reps", type=int, default=REPS)
    parser.add_argument("--only-13", action="store_true")
    args = parser.parse_args(argv)
    rows = _u7_rows() + _tv_rows()
    paper = __import__("yaml").safe_load((ROOT / "paper/portfoy.yaml").read_text())["satirlar"]
    if args.only_13:
        # U4 paper rows name the card (U4-H2/H3), while U7 persists each
        # market/timeframe expansion as ``U4-H2:KRIPTO25:1D``.
        def selected(row: dict[str, object]) -> bool:
            for book in paper:
                if row["id"] == book["id"]:
                    return True
                if str(row["id"]).startswith(str(book["id"]) + ":") and row["piyasa"] == book["piyasa"] and row["tf"] == book["tf"]:
                    return True
            return False
        rows = [row for row in rows if selected(row)]
    out, returns = [], {}
    for row in rows:
        try:
            record, series = evaluate(row, args.reps)
            out.append(record); returns[str(row["id"])] = series
        except Exception as exc:  # data availability must be explicit, not silently dropped
            out.append({"kimlik": row["id"], "kaynak": row["kaynak"], "piyasa": row["piyasa"], "tf": row["tf"], "hata": f"{type(exc).__name__}: {exc}"})
    table = pd.DataFrame(out)
    n_eff = neff_clusters(returns) if returns else np.nan
    if returns:
        table["N_eff"] = n_eff; table["N_ham"] = len(returns)
        table["dsr"] = [deflated_sharpe_ratio(returns.get(str(x), pd.Series(dtype=float)), max(int(n_eff), 1)) for x in table["kimlik"]]
    target = OUT / ("kapi_kontrol_13.csv" if args.only_13 else "plasebo.csv")
    table.to_csv(target, index=False)
    print(f"{len(table)} satır: {target}")


if __name__ == "__main__":
    main()
