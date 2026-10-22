#!/usr/bin/env python3
"""T18: portfolio of the `Kosullu` stage-2b candidates (equal risk, no optimisation).

Every candidate keeps its own sizing rules (0.5% risk per trade, 2% total open
risk inside its own book).  The portfolio gives each of the N candidates 1/N of
the capital, so the portfolio-level open risk is the mean of the books' open
risk and can never exceed the 2% cap.  Candidates were picked after looking at
in-sample results: the out-of-sample block is reported first and no weight is
fitted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import asama2a, asama2b, tarama  # noqa: E402
from backtests.run_codex21 import ROWS, _load_market  # noqa: E402
from data.evren_pit import load_pit_universe  # noqa: E402
from data.fetch import normalize_ohlcv  # noqa: E402
from engine.portfolio import BacktestResult  # noqa: E402

IS_START, IS_END, OOS_START = asama2b.IS_START, asama2b.IS_END, asama2b.OOS_START
OPEN_RISK_CAP = 0.02
STRESS_QUANTILE = 0.05
MIN_STRESS_DAYS = 20
GATE_MDD = asama2b.RISK_BUDGET
CORRELATION_COLUMNS = ["donem", "tip", "a", "b", "korelasyon", "gun"]


def daily_returns(result: BacktestResult) -> pd.Series:
    returns = result.equity.dropna().pct_change().dropna()
    returns.index = returns.index.normalize()
    return returns[~returns.index.duplicated(keep="last")]


def open_risk_series(result: BacktestResult) -> pd.Series:
    """Sum of `initial_risk` of trades open on each day, as a fraction of that day's equity."""
    equity = result.equity.dropna()
    equity.index = equity.index.normalize()
    risk = pd.Series(0.0, index=equity.index)
    trades = result.trades
    if not trades.empty:
        for trade in trades.itertuples():
            held = (risk.index >= pd.Timestamp(trade.entry_date).normalize()) & (risk.index < pd.Timestamp(trade.exit_date).normalize())
            risk[held] += float(trade.initial_risk)
    return risk / equity


def align(series: dict[str, pd.Series]) -> pd.DataFrame:
    """Union calendar; a day on which a market was closed counts as a 0 return."""
    return pd.DataFrame(series).sort_index().fillna(0.0)


def equal_risk_portfolio(returns: pd.DataFrame) -> pd.Series:
    """1/N capital per candidate, rebalanced daily (no fitted weights)."""
    return returns.mean(axis=1)


def portfolio_open_risk(risks: dict[str, pd.Series]) -> pd.Series:
    """Open risk of the 1/N portfolio = mean of each book's open-risk fraction."""
    frame = pd.DataFrame(risks).sort_index().fillna(0.0)
    return frame.mean(axis=1)


def profit_factor(returns: pd.Series | np.ndarray) -> float:
    values = np.asarray(returns, dtype=float)
    wins, losses = values[values > 0].sum(), -values[values < 0].sum()
    return float(wins / losses) if losses > 0 else (float("inf") if wins > 0 else float("nan"))


def period_metrics(returns: pd.Series, *, repetitions: int, seed: int, annualization: int) -> dict[str, float]:
    values = returns.to_numpy(dtype=float)
    if len(values) < 2:
        nan = float("nan")
        return {"getiri": nan, "cagr": nan, "pf": nan, "mdd": nan, "mdd_p95": nan, "cagr_p05": nan, "gun": float(len(values))}
    growth = float(np.prod(1.0 + values))
    years = max(len(values) / annualization, 1e-9)
    boot = asama2b.block_bootstrap(values, repetitions=repetitions, seed=seed, annualization=annualization)
    return {
        "getiri": growth - 1.0,
        "cagr": growth ** (1.0 / years) - 1.0 if growth > 0 else -1.0,
        "pf": profit_factor(values),
        "mdd": asama2b.max_drawdown(values),
        "mdd_p95": boot["mdd_p95"],
        "cagr_p05": boot["cagr_p05"],
        "gun": float(len(values)),
    }


def stress_days(market_proxy: pd.Series, index: pd.Index) -> pd.Index:
    """Days on which the market proxy is in its worst 5% (computed on the period's own days)."""
    proxy = market_proxy.reindex(index).dropna()
    if proxy.empty:
        return pd.Index([])
    return proxy.index[proxy <= proxy.quantile(STRESS_QUANTILE)]


def correlation_table(returns: pd.DataFrame, market_proxy: pd.Series, period: str) -> pd.DataFrame:
    rows = []
    stress = stress_days(market_proxy, returns.index)
    for kind, frame in (("tum", returns), ("stres", returns.loc[returns.index.intersection(stress)])):
        enough = len(frame) >= (MIN_STRESS_DAYS if kind == "stres" else 2)
        matrix = frame.corr() if enough else pd.DataFrame(np.nan, index=returns.columns, columns=returns.columns)
        for a in returns.columns:
            for b in returns.columns:
                rows.append({"donem": period, "tip": kind, "a": a, "b": b, "korelasyon": matrix.loc[a, b], "gun": len(frame)})
    return pd.DataFrame(rows, columns=CORRELATION_COLUMNS)


def mean_pairwise(table: pd.DataFrame, period: str, kind: str) -> float:
    part = table[(table.donem == period) & (table.tip == kind) & (table.a < table.b)]
    return float(part["korelasyon"].mean()) if not part.empty else float("nan")


def market_proxy(data: dict[str, dict[str, pd.DataFrame]]) -> pd.Series:
    """Equal-weight daily close-to-close return of every symbol in the candidates' markets
    (BIST in USD); markets are then averaged per day.  There is no single index for all four markets."""
    per_market = []
    for frames in data.values():
        closes = pd.DataFrame({symbol: frame["close"] for symbol, frame in frames.items()})
        closes.index = closes.index.normalize()
        per_market.append(closes.sort_index().pct_change(fill_method=None).mean(axis=1))
    return pd.concat(per_market, axis=1).mean(axis=1)


def select_candidates(results_dir: Path) -> tuple[pd.DataFrame, str]:
    """Gecti/Kosullu rows; a PIT rerun row replaces the fixed-universe row of the same id/market."""
    base, pit = results_dir / "asama2b.csv", results_dir / "asama2b_pit.csv"
    if not base.exists():
        raise SystemExit("results/asama2b.csv yok")
    table, name = pd.read_csv(base), "asama2b.csv"
    if pit.exists():
        rerun = pd.read_csv(pit)
        keys = set(zip(rerun["id"], rerun["piyasa"]))
        table = pd.concat([table[[(i, m) not in keys for i, m in zip(table["id"], table["piyasa"])]], rerun], ignore_index=True)
        name = "asama2b.csv + asama2b_pit.csv"
    return table[table["karar"].isin(["Gecti", "Kosullu"])].reset_index(drop=True), name


def _fmt(value: Any, fmt: str) -> str:
    return "-" if pd.isna(value) else format(float(value), fmt)


def write_report(
    results_dir: Path, source: str, names: list[str], per_candidate: pd.DataFrame, summary: dict[str, dict[str, float]],
    corr: pd.DataFrame, open_risk_max: float, evren: str,
) -> None:
    lines = [
        "# Portfoy analizi: Gecti + Kosullu adaylar (T18)", "",
        f"Kaynak: `results/{source}` (evren: {evren}) | Adaylar ({len(names)}): {', '.join(names)}", "",
        "> **Secim yanliligi uyarisi:** adaylar IS sonuclarina bakilarak secildi. Asil kanit **OOS** bloktur "
        "(2024-10-01 sonrasi, secime girmedi); IS rakamlari yalniz baglam icindir. Agirlik optimizasyonu yapilmadi: her aday 1/N.", "",
        "## Birlesik portfoy (esit risk, 1/N sermaye)", "",
        "| Donem | Gun | Getiri | CAGR | PF (gunluk) | MDD | Bootstrap MDD %95 | Bootstrap CAGR p05 | MDD kapisi (<=%15) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for period in ("OOS", "IS"):
        m = summary[period]
        gate = "-" if pd.isna(m["mdd_p95"]) else ("gecti" if m["mdd_p95"] <= GATE_MDD else "gecmedi")
        lines.append(
            f"| **{period}** | {m['gun']:.0f} | {_fmt(m['getiri'], '.1%')} | {_fmt(m['cagr'], '.1%')} | {_fmt(m['pf'], '.2f')} | "
            f"{_fmt(m['mdd'], '.1%')} | {_fmt(m['mdd_p95'], '.1%')} | {_fmt(m['cagr_p05'], '.1%')} | {gate} |"
        )
    lines += [
        "", f"Portfoy genelinde IS'te en yuksek acik baslangic riski (islemlerin `initial_risk` toplami / ozkaynak): **{open_risk_max:.2%}**. "
        f"Her kitap motorun %2 toplam risk tavaniyla calisir; 1/N agirlikla portfoy riski kitaplarin ortalamasidir, dolayisiyla tek kitabin tavanini asamaz.", "",
        "## Adaylar ayri ayri", "",
        "| Aday | OOS getiri | OOS MDD | IS getiri | IS MDD |", "|---|---:|---:|---:|---:|",
    ]
    for item in per_candidate.itertuples():
        lines.append(f"| {item.aday} | {_fmt(item.oos_getiri, '.1%')} | {_fmt(item.oos_mdd, '.1%')} | {_fmt(item.is_getiri, '.1%')} | {_fmt(item.is_mdd, '.1%')} |")
    lines += ["", "## Korelasyon (gunluk getiri; piyasa kapali gun = 0)", "",
              "| Donem | Tum gunler ort. cift korelasyonu | Stres gunleri (piyasanin en kotu %5'i) |", "|---|---:|---:|"]
    for period in ("OOS", "IS"):
        stress_days_count = corr[(corr.donem == period) & (corr.tip == "stres")]["gun"].max()
        lines.append(f"| {period} | {_fmt(mean_pairwise(corr, period, 'tum'), '.2f')} | {_fmt(mean_pairwise(corr, period, 'stres'), '.2f')} (n={_fmt(stress_days_count, '.0f')} gun) |")
    lines += [
        "", "Tam matrisler: `results/portfoy_korelasyon.csv`.", "",
        "## Yontem notlari", "",
        "- Getiri serileri `tarama.prepare(...).run()` / `asama2b.prepare_codex(...).run()` ile uretilir; BIST USD bazinda. Her kitap bagimsiz sermaye ile calisir; portfoy getirisi gunluk getirilerin ortalamasidir (gunluk yeniden dengeleme).",
        "- Takvimler farkli piyasalardan gelir: birlesik tarih ekseni, bir piyasanin kapali gunu 0 getiri sayilir. Bu, korelasyonlari asagi ceker.",
        "- Stres gunleri: aday piyasalarindaki tum sembollerin esit agirlikli gunluk getirisinin (BIST USD) piyasalar arasi ortalamasinin en kotu %5'lik gunleri. BIST/emtia icin tek bir endeks serisi yok.",
        "- Bootstrap: 20 gunluk dairesel block, `asama2b.block_bootstrap`. OOS ornegi kisadir; OOS bootstrap'i gevsek okunmalidir.",
        "- PF gunluk getirilerden hesaplanir (islem bazli PF degil).",
        "- Acik risk islem listesinden turetilir; veri sonunda acik kalan pozisyonlar listede yoktur ve gunluk ozkaynak degisimi orani oynatir (tavan giris aninda motorda uygulanir).",
    ]
    (results_dir / "portfoy.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kartlar", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--bootstrap-tekrar", type=int, default=1000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates, source = select_candidates(args.results_dir)
    if candidates.empty:
        raise SystemExit("Gecti/Kosullu aday yok")
    evren = str(candidates["evren"].iloc[0]) if "evren" in candidates else "sabit"
    pit = load_pit_universe() if evren == "pit" else None
    cards = {c["id"]: c for c in (yaml.safe_load(p.read_text(encoding="utf-8")) for p in args.kartlar.glob("*.yaml"))}
    data: dict[str, dict[str, pd.DataFrame]] = {}
    for market in sorted(set(candidates["piyasa"])):
        data[market], _, _ = _load_market(market, args.data_dir, evren)
    if "BIST30" in data:
        fx = args.data_dir / "USDTRY_X.parquet"
        if not fx.exists():
            raise SystemExit(f"{fx} yok: BIST USD fiyat gerektirir")
        data["BIST30"] = asama2a.usd_frames(data["BIST30"], normalize_ohlcv(pd.read_parquet(fx)))
    benchmarks = {}
    for market, symbol in tarama.BENCHMARK_SYMBOL.items():
        if market in data:
            benchmarks[market] = data[market].get(symbol)
            if benchmarks[market] is None and (args.data_dir / f"{symbol}.parquet").exists():
                benchmarks[market] = normalize_ohlcv(pd.read_parquet(args.data_dir / f"{symbol}.parquet"))

    series: dict[str, dict[str, pd.Series]] = {"IS": {}, "OOS": {}}
    risks: dict[str, pd.Series] = {}
    for row in candidates.itertuples():
        name = f"{row.id}:{row.piyasa}"
        frames = data[row.piyasa]
        final = max(frame.index.max() for frame in frames.values())
        for period, start, end in (("IS", IS_START, IS_END), ("OOS", OOS_START, final)):
            if row.kaynak == "Codex Algo":
                result = asama2b.prepare_codex(ROWS[row.id], frames, start, end, pit).run()
            else:
                result = tarama.prepare(cards[row.id], frames, row.piyasa, benchmark=benchmarks.get(row.piyasa), start=start, end=end, pit_universe=pit).run()
            series[period][name] = daily_returns(result)
            if period == "IS":
                risks[name] = open_risk_series(result)
        print(f"{name}: tamam", flush=True)

    names = list(series["IS"])
    proxy = market_proxy({m: data[m] for m in data})
    summary, corr_parts, per_candidate = {}, [], {name: {"aday": name} for name in names}
    for period in ("IS", "OOS"):
        frame = align(series[period])
        portfolio = equal_risk_portfolio(frame)
        summary[period] = period_metrics(portfolio, repetitions=args.bootstrap_tekrar, seed=asama2a.BASE_SEED, annualization=252)
        corr_parts.append(correlation_table(frame, proxy, period))
        for name in names:
            values = frame[name]
            per_candidate[name][f"{period.lower()}_getiri"] = float(np.prod(1.0 + values.to_numpy()) - 1.0)
            per_candidate[name][f"{period.lower()}_mdd"] = asama2b.max_drawdown(values.to_numpy())
    corr = pd.concat(corr_parts, ignore_index=True)
    corr.to_csv(args.results_dir / "portfoy_korelasyon.csv", index=False, float_format="%.6g")
    risk_max = float(portfolio_open_risk(risks).max())
    write_report(args.results_dir, source, names, pd.DataFrame(per_candidate.values()), summary, corr, risk_max, evren)
    print(f"portfoy.md yazildi ({len(names)} aday, OOS getiri {summary['OOS']['getiri']:.1%}, IS bootstrap MDD95 {summary['IS']['mdd_p95']:.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
