#!/usr/bin/env python3
"""Run the complete 21-row Codex Algo replication portfolio."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.fetch import normalize_ohlcv  # noqa: E402
from engine.portfolio import calculate_metrics, run_portfolio  # noqa: E402
from strategies.wd_adx_breakout_risk import signals as adx_breakout_signals  # noqa: E402
from strategies.wd_breakout_risk import signals as breakout_signals  # noqa: E402
from strategies.wd_cci_continuation_risk import signals as cci_signals  # noqa: E402
from strategies.wd_dmi_trend_risk import signals as dmi_signals  # noqa: E402
from strategies.wd_dual_momentum_risk import signals as dual_momentum_signals  # noqa: E402
from strategies.wd_flow_confirmation_risk import signals as flow_signals  # noqa: E402
from strategies.wd_ichimoku_balance_risk import signals as ichimoku_signals  # noqa: E402
from strategies.wd_kama_efficiency_risk import signals as kama_signals  # noqa: E402
from strategies.wd_momentum_risk import signals as momentum_signals  # noqa: E402
from strategies.wd_pullback_risk import signals as pullback_signals  # noqa: E402
from strategies.wd_reversion_risk import signals as reversion_signals  # noqa: E402

SignalFunction = Callable[[pd.DataFrame, str], pd.DataFrame]
REPLICATION_START = pd.Timestamp("2020-01-02", tz="UTC")
REPLICATION_END = pd.Timestamp("2026-10-14", tz="UTC")
PREPERIOD_START = pd.Timestamp("2015-01-01", tz="UTC")
PREPERIOD_END = pd.Timestamp("2019-12-31", tz="UTC")


@dataclass(frozen=True)
class RowConfig:
    row_id: str
    market: str
    family: str
    signal_function: SignalFunction
    cost: float
    oos_start: str
    pdf_return: float
    pdf_pf: float
    pdf_sharpe: float
    pdf_mdd: float
    pdf_trades: int
    pdf_oos_return: float
    pdf_cost_2x_return: float
    pdf_cost_3x_return: float
    pdf_delay_return: float
    pdf_best_excluded_return: float
    pdf_exposure: float
    pdf_max_positions: int
    time_stop_bars: int | None = None


ROWS = {
    item.row_id: item
    for item in [
        RowConfig("C01", "BIST30", "wd_pullback_risk", pullback_signals, .0015, "2024-10-03", .7274, 2.21, 1.61, -.0589, 489, .0570, .5965, .4815, .6488, .6779, .1412, 14),
        RowConfig("C02", "BIST30", "wd_cci_continuation_risk", cci_signals, .0015, "2024-10-03", .5630, 1.90, 1.34, -.0601, 551, .0168, .4406, .3348, .6019, .4852, .1388, 16),
        RowConfig("C03", "BIST30", "wd_flow_confirmation_risk", flow_signals, .0015, "2024-10-03", .4777, 1.60, 1.22, -.0659, 781, .0018, .3090, .1684, .5990, .4073, .1281, 17),
        RowConfig("C04", "BIST30", "wd_ichimoku_balance_risk", ichimoku_signals, .0015, "2024-10-03", .4100, 2.58, 1.48, -.0445, 159, .0098, .3546, .3051, .4462, .3659, .0710, 8),
        RowConfig("C05", "BIST30", "wd_dmi_trend_risk", dmi_signals, .0015, "2024-10-03", .3700, 2.07, 1.24, -.0481, 325, .0373, .2882, .2164, .3067, .2833, .0781, 18),
        RowConfig("C06", "BIST30", "wd_kama_efficiency_risk", kama_signals, .0015, "2024-10-03", .3102, 2.27, 1.30, -.0611, 235, .0099, .2437, .1848, .3201, .2454, .0414, 10),
        RowConfig("C07", "ABD25", "wd_adx_breakout_risk", adx_breakout_signals, .0005, "2024-09-30", .2824, 1.78, .98, -.0473, 238, .0219, .2552, .2294, .2534, .2472, .2029, 10),
        RowConfig("C08", "ABD25", "wd_dual_momentum_risk", dual_momentum_signals, .0005, "2024-09-30", .2640, 1.31, .77, -.0757, 1056, .0967, .1949, .1312, .2317, .2327, .2951, 19),
        RowConfig("C09", "ABD25", "wd_cci_continuation_risk", cci_signals, .0005, "2024-09-30", .2288, 1.34, .73, -.0611, 559, .0226, .1864, .1466, .1708, .1989, .2512, 14),
        RowConfig("C10", "ABD25", "wd_breakout_risk", breakout_signals, .0005, "2024-09-30", .2042, 1.32, .68, -.0631, 510, .0205, .1668, .1317, .1600, .1750, .2516, 17),
        RowConfig("C11", "ABD25", "wd_momentum_risk", momentum_signals, .0005, "2024-09-30", .1873, 1.30, .59, -.0768, 491, .0296, .1534, .1212, .1321, .1566, .2493, 17),
        RowConfig("C12", "ABD25", "wd_ichimoku_balance_risk", ichimoku_signals, .0005, "2024-09-30", .1081, 1.50, .62, -.0347, 141, .0284, .0943, .0810, .0759, .0814, .0937, 8),
        RowConfig("C13", "ABD25", "wd_reversion_risk", reversion_signals, .0005, "2024-09-30", .0701, 1.25, .49, -.0395, 373, .0191, .0395, .0107, .0836, .0630, .0569, 9, 10),
        RowConfig("C14", "KRIPTO25", "wd_breakout_risk", breakout_signals, .0015, "2024-10-01", .4218, 2.15, .99, -.0675, 244, .0076, .3900, .3600, .2512, .3089, .0379, 14),
        RowConfig("C15", "KRIPTO25", "wd_cci_continuation_risk", cci_signals, .0015, "2024-10-01", .3561, 1.98, .87, -.0552, 281, .0084, .3245, .2948, .2170, .2274, .0343, 18),
        RowConfig("C16", "EMTIA", "wd_dual_momentum_risk", dual_momentum_signals, .0005, "2024-09-30", .1283, 1.42, .59, -.0689, 278, .0574, .0805, .0375, .1484, .0950, .1321, 6),
        RowConfig("C17", "EMTIA", "wd_cci_continuation_risk", cci_signals, .0005, "2024-09-30", .1229, 1.60, .64, -.0327, 141, .0604, .0947, .0691, .1467, .0916, .0993, 5),
        RowConfig("C18", "EMTIA", "wd_breakout_risk", breakout_signals, .0005, "2024-09-30", .1135, 1.52, .58, -.0476, 130, .0553, .0876, .0639, .1328, .0809, .1014, 5),
        RowConfig("C19", "EMTIA", "wd_pullback_risk", pullback_signals, .0005, "2024-09-30", .0892, 1.56, .63, -.0347, 116, .0341, .0678, .0481, .0997, .0616, .0768, 4),
        RowConfig("C20", "EMTIA", "wd_momentum_risk", momentum_signals, .0005, "2024-09-30", .0864, 1.45, .47, -.0525, 110, .0372, .0678, .0506, .1052, .0542, .0843, 5),
        RowConfig("C21", "EMTIA", "wd_adx_breakout_risk", adx_breakout_signals, .0005, "2024-09-30", .0339, 1.37, .27, -.0467, 53, .0044, .0226, .0123, .0452, .0058, .0543, 5),
    ]
}

OUTPUT_COLUMNS = [
    "satir", "piyasa", "aile", "donem", "senaryo", "baslangic", "bitis",
    "maliyet_tek_yon", "ek_gecikme_bar", "durum", "neden", "getiri", "cagr",
    "pf", "sharpe", "mdd", "islem", "ortalama_r", "maruziyet",
    "azami_acik_pozisyon", "en_iyi_islem_haric_getiri", "oos_getiri",
    "oos_sharpe", "data_hash", "git_sha",
]


def _git_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _symbols_for_market(market: str) -> list[str]:
    universe = pd.read_csv(ROOT / "data" / "evren.csv", dtype=str).fillna("")
    selected = universe.loc[universe["piyasa"] == market]
    if market == "ABD25":
        selected = selected.loc[~selected["not"].str.lower().str.contains("referans")]
    return selected["sembol"].tolist()


def _filename(symbol: str) -> str:
    return symbol.replace("/", "_").replace("=", "_") + ".parquet"


def _load_market(market: str, data_dir: Path) -> tuple[dict[str, pd.DataFrame], str, list[str]]:
    loaded: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    digest = hashlib.sha256()
    for symbol in _symbols_for_market(market):
        path = data_dir / _filename(symbol)
        if not path.exists():
            missing.append(symbol)
            continue
        try:
            frame = normalize_ohlcv(pd.read_parquet(path))
        except Exception as exc:
            missing.append(f"{symbol} ({type(exc).__name__})")
            continue
        if frame.empty:
            missing.append(f"{symbol} (bos)")
            continue
        loaded[symbol] = frame
        digest.update(symbol.encode("utf-8"))
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return loaded, digest.hexdigest(), missing


def _empty_row(config: RowConfig, period: str, scenario: str, reason: str, git_sha: str) -> dict[str, object]:
    start, end = (
        (REPLICATION_START, REPLICATION_END)
        if period == "replikasyon"
        else (PREPERIOD_START, PREPERIOD_END)
    )
    row = {column: np.nan for column in OUTPUT_COLUMNS}
    row.update(
        {
            "satir": config.row_id, "piyasa": config.market, "aile": config.family,
            "donem": period, "senaryo": scenario, "baslangic": start.date().isoformat(),
            "bitis": end.date().isoformat(), "durum": "Dogrulanamaz", "neden": reason,
            "data_hash": "", "git_sha": git_sha,
        }
    )
    return row


def _trade_path(results_dir: Path, config: RowConfig, period: str) -> Path:
    return results_dir / "trades" / f"{config.row_id}_{period}.csv"


def run_rows(row_ids: list[str], data_dir: Path, results_dir: Path) -> pd.DataFrame:
    git_sha = _git_sha()
    outputs: list[dict[str, object]] = []
    cache: dict[str, tuple[dict[str, pd.DataFrame], str, list[str]]] = {}
    scenarios = [("1x", 1.0, 0), ("2x", 2.0, 0), ("3x", 3.0, 0), ("gecikme_+1", 1.0, 1)]
    for row_id in row_ids:
        config = ROWS[row_id]
        if config.market not in cache:
            cache[config.market] = _load_market(config.market, data_dir)
        market_data, data_hash, missing = cache[config.market]
        precomputed_signals = {
            symbol: config.signal_function(frame, config.market)
            for symbol, frame in market_data.items()
        }
        for period, start, end in [
            ("replikasyon", REPLICATION_START, REPLICATION_END),
            ("on_donem", PREPERIOD_START, PREPERIOD_END),
        ]:
            period_data = {
                symbol: frame for symbol, frame in market_data.items()
                if not frame.loc[(frame.index >= start) & (frame.index <= end)].empty
            }
            for scenario, multiplier, delay in scenarios:
                if not period_data:
                    reason = f"{config.market} icin {period} araliginda veri yok"
                    outputs.append(_empty_row(config, period, scenario, reason, git_sha))
                    continue
                try:
                    result = run_portfolio(
                        period_data, config.signal_function, market=config.market,
                        start=start, end=end, cost_rate=config.cost * multiplier,
                        extra_delay_bars=delay,
                        time_stop_bars=config.time_stop_bars,
                        precomputed_signals={
                            symbol: precomputed_signals[symbol] for symbol in period_data
                        },
                    )
                    metrics = calculate_metrics(
                        result, annualization=365 if config.market == "KRIPTO25" else 252,
                        oos_start=pd.Timestamp(config.oos_start, tz="UTC") if period == "replikasyon" else None,
                    )
                    reason = ""
                    if missing:
                        reason = "Eksik semboller: " + ", ".join(missing)
                    outputs.append(
                        {
                            "satir": row_id, "piyasa": config.market, "aile": config.family,
                            "donem": period, "senaryo": scenario,
                            "baslangic": start.date().isoformat(), "bitis": end.date().isoformat(),
                            "maliyet_tek_yon": config.cost * multiplier,
                            "ek_gecikme_bar": delay, "durum": "Hesaplandi", "neden": reason,
                            **metrics, "data_hash": data_hash, "git_sha": git_sha,
                        }
                    )
                    if scenario == "1x":
                        trade_path = _trade_path(results_dir, config, period)
                        trade_path.parent.mkdir(parents=True, exist_ok=True)
                        result.trades.to_csv(trade_path, index=False)
                except Exception as exc:
                    outputs.append(
                        _empty_row(
                            config, period, scenario,
                            f"{type(exc).__name__}: {exc}", git_sha,
                        )
                    )
    table = pd.DataFrame(outputs).reindex(columns=OUTPUT_COLUMNS)
    results_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(results_dir / "codex21.csv", index=False, float_format="%.10g")
    write_comparison(table, results_dir / "codex21_karsilastirma.md")
    return table


def _pct(value: object) -> str:
    return "—" if pd.isna(value) else f"{float(value):.2%}"


def _num(value: object) -> str:
    return "—" if pd.isna(value) else f"{float(value):.2f}"


def _replication_status(config: RowConfig, row: pd.Series) -> tuple[str, str]:
    if row["durum"] != "Hesaplandi":
        return "Dogrulanamaz", str(row["neden"])
    count_ok = abs(float(row["islem"]) - config.pdf_trades) / config.pdf_trades <= .15
    sign_ok = np.sign(float(row["getiri"])) == np.sign(config.pdf_return)
    pf_ok = np.isfinite(float(row["pf"])) and abs(float(row["pf"]) - config.pdf_pf) / config.pdf_pf <= .25
    metric_ok = count_ok and sign_ok and pf_ok
    # Lider kararı (tartisma/004): işlem listesi yoksa üç metrik yeterlidir.
    status = "Sapma" if not metric_ok else "Gecti (metrik)"
    details = (
        f"islem={'uygun' if count_ok else 'sapma'}, isaret={'uygun' if sign_ok else 'sapma'}, "
        f"PF={'uygun' if pf_ok else 'sapma'}; PDF islem listesi yok"
    )
    return status, details


def write_comparison(table: pd.DataFrame, path: Path) -> None:
    lines = [
        "# Codex Algo 21 karşılaştırması", "",
        "Yüzdeler ondalık motor çıktısından biçimlendirilmiştir. PDF işlem tarihlerini yayımlamadığı için "
        "giriş tarihi örtüşmesi ölçülemez. Lider kararı gereği işlem sayısı, getiri işareti ve PF "
        "uyumluysa sonuç `Geçti (metrik)` sayılır (`tartisma/004_t1a_lider_degerlendirme.md`).",
        "", "## Replikasyon (baz maliyet)", "",
        "| Satır | PDF getiri | Bizim getiri | PDF PF | Bizim PF | PDF işlem | Bizim işlem | Durum | Gerekçe |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row_id in ROWS:
        if row_id not in set(table["satir"]):
            continue
        config = ROWS[row_id]
        row = table.loc[
            (table["satir"] == row_id) & (table["donem"] == "replikasyon") & (table["senaryo"] == "1x")
        ].iloc[0]
        status, reason = _replication_status(config, row)
        lines.append(
            f"| {row_id} | {_pct(config.pdf_return)} | {_pct(row['getiri'])} | {_num(config.pdf_pf)} | "
            f"{_num(row['pf'])} | {config.pdf_trades} | {_num(row['islem'])} | {status} | {reason} |"
        )
    lines.extend([
        "", "## Replikasyon ayrıntıları ve stresler", "",
        "| Satır | Sharpe PDF/biz | MDD PDF/biz | OOS getiri PDF/biz | 2x getiri PDF/biz | 3x getiri PDF/biz | +1 bar PDF/biz | En iyi hariç PDF/biz | Maruziyet PDF/biz | Azami poz. PDF/biz |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row_id in ROWS:
        if row_id not in set(table["satir"]):
            continue
        config = ROWS[row_id]
        candidates = table.loc[
            (table["satir"] == row_id) & (table["donem"] == "replikasyon")
        ].set_index("senaryo")
        base = candidates.loc["1x"]
        cost_2x = candidates.loc["2x"]
        cost_3x = candidates.loc["3x"]
        delay = candidates.loc["gecikme_+1"]
        lines.append(
            f"| {row_id} | {_num(config.pdf_sharpe)} / {_num(base['sharpe'])} | "
            f"{_pct(config.pdf_mdd)} / {_pct(base['mdd'])} | "
            f"{_pct(config.pdf_oos_return)} / {_pct(base['oos_getiri'])} | "
            f"{_pct(config.pdf_cost_2x_return)} / {_pct(cost_2x['getiri'])} | "
            f"{_pct(config.pdf_cost_3x_return)} / {_pct(cost_3x['getiri'])} | "
            f"{_pct(config.pdf_delay_return)} / {_pct(delay['getiri'])} | "
            f"{_pct(config.pdf_best_excluded_return)} / {_pct(base['en_iyi_islem_haric_getiri'])} | "
            f"{_pct(config.pdf_exposure)} / {_pct(base['maruziyet'])} | "
            f"{config.pdf_max_positions} / {_num(base['azami_acik_pozisyon'])} |"
        )
    lines.extend([
        "", "## Ön dönem tutma testi (baz maliyet)", "",
        "| Satır | Getiri | CAGR | PF | Sharpe | MDD | İşlem | Ortalama R | Maruziyet |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row_id in ROWS:
        candidates = table.loc[
            (table["satir"] == row_id) & (table["donem"] == "on_donem") & (table["senaryo"] == "1x")
        ]
        if candidates.empty:
            continue
        row = candidates.iloc[0]
        lines.append(
            f"| {row_id} | {_pct(row['getiri'])} | {_pct(row['cagr'])} | {_num(row['pf'])} | "
            f"{_num(row['sharpe'])} | {_pct(row['mdd'])} | {_num(row['islem'])} | "
            f"{_num(row['ortalama_r'])} | {_pct(row['maruziyet'])} |"
        )
    lines.extend([
        "", "## Yorumlama notları", "",
        "- PDF baz maliyeti belirtmediği için liderin v0.3 maliyet tablosu kullanıldı.",
        "- BIST/ABD evrenleri güncel bileşenlerden oluşur; point-in-time üyelik ve delisted veri olmadığı için survivorship riski vardır.",
        "- Haftalık rejim borsa/ETF için Cuma, Binance spot için Pazar UTC kapanışında tamamlanır.",
        "- CCI 'son 10 gün negatif' ifadesi, kesişim barından önceki 10 tamamlanmış seans olarak uygulandı.",
        "- KAMA ilk geçerli ER barının kapanışıyla tohumlanır; PDF başlangıç tohumunu belirtmez.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", default=",".join(ROWS), help="comma-separated row IDs")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "daily")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    row_ids = [item.strip().upper() for item in args.rows.split(",") if item.strip()]
    unknown = sorted(set(row_ids).difference(ROWS))
    if unknown:
        raise SystemExit(f"unknown row IDs: {', '.join(unknown)}")
    table = run_rows(row_ids, args.data_dir, args.results_dir)
    calculated = int((table["durum"] == "Hesaplandi").sum())
    print(f"Wrote {len(table)} scenario rows ({calculated} calculated) to {args.results_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
