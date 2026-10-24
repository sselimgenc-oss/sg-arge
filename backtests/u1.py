#!/usr/bin/env python3
"""U1 runner: crypto day-trade cards (Hat 2) and Faz 1 winners on crypto 1H (Hat 0), docs/GOREV_U1.md.

* Hat 0 runs ``T8-07`` and ``V2B`` UNCHANGED on the 14-coin U1 universe at 1H (market KRIPTO25 costs; their 4H higher
  timeframe is resampled from the 1H bars by the cards' own ``tf: 4H`` indicators).
* Hat 2 expands every ``izgara:`` of ``U1-H2-*`` (entry timeframe x parameter) into variants (14 trials in total with Hat 0).
* Every variant is one pooled portfolio over the 14 coins (Faz 1 sizing: 0.5 % risk per trade, 2 % open risk). Per-coin
  rows are sliced from that pooled trade list. Costs 0.15 / 0.30 / 0.45 % (1x/2x/3x).
* Periods: IS 2018-01-01 -> 2022-12-31, OOS 2023-01-01 -> the last closed archive bar (U7).

    python backtests/u1.py --hat 0,2 --donem IS,OOS --veri-kok data --results-dir results/u1
"""

from __future__ import annotations

import argparse
import copy
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import tarama  # noqa: E402
from data.fetch import normalize_ohlcv  # noqa: E402
from engine.portfolio import calculate_metrics  # noqa: E402
from engine.spec import normalize_timeframe  # noqa: E402

LOG = logging.getLogger("u1")
MARKET = "KRIPTO25"
PERIODS = {
    "IS": (pd.Timestamp("2018-01-01", tz="UTC"), pd.Timestamp("2022-12-31", tz="UTC")),
    "OOS": (pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2100-01-01", tz="UTC")),
    "KILITLI": (pd.Timestamp("2025-10-01", tz="UTC"), pd.Timestamp("2100-01-01", tz="UTC")),
}
CORE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "TRXUSDT"]
SIBLINGS = ["ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT", "AVAXUSDT", "BCHUSDT", "NEARUSDT"]
HAT0 = ("T8-07", "V2B")
HAT2 = ("U1-H2-A", "U1-H2-B", "U1-H2-C")
SPEC = ROOT / "docs" / "spec"
COSTS = (1.0, 2.0, 3.0)


# --------------------------------------------------------------------------------------------- cards and grids
def load_card(card_id: str, directory: Path = SPEC) -> dict[str, Any]:
    card = yaml.safe_load((directory / f"{card_id}.yaml").read_text(encoding="utf-8"))
    card["tf"] = normalize_timeframe(card.get("tf"))
    return card


def _set_path(card: dict[str, Any], path: str, value: Any) -> None:
    holder = card
    *parents, leaf = path.split(".")
    for key in parents:
        holder = holder[key]
    holder[leaf] = value


def variants(card: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """(variant id, card copy) for every point of the card's pre-registered ``izgara`` (none = the card itself)."""
    grid = card.get("izgara") or []
    if not grid:
        return [(card["id"], copy.deepcopy(card))]
    points: list[list[tuple[str, Any]]] = [[]]
    for axis in grid:
        points = [done + [(axis["yol"], value)] for done in points for value in axis["degerler"]]
    out = []
    for point in points:
        changed = copy.deepcopy(card)
        for path, value in point:
            _set_path(changed, path, value)
        changed["tf"] = normalize_timeframe(changed["tf"])
        label = "_".join(f"{path.split('.')[-1]}={value}" for path, value in point)
        out.append((f"{card['id']}[{label}]", changed))
    return out


def all_variants(hats: tuple[int, ...] = (0, 2), directory: Path = SPEC) -> list[tuple[str, dict[str, Any]]]:
    ids = (HAT0 if 0 in hats else ()) + (HAT2 if 2 in hats else ())
    return [item for card_id in ids for item in variants(load_card(card_id, directory))]


# --------------------------------------------------------------------------------------------- data and periods
def load_data(root: Path, tf: str, symbols: list[str]) -> dict[str, pd.DataFrame]:
    directory = root / tarama.TF_DIR[tf]
    frames = {}
    for symbol in symbols:
        path = directory / f"{symbol}.parquet"
        if path.exists():
            frame = normalize_ohlcv(pd.read_parquet(path))
            if not frame.empty:
                frames[symbol] = frame
    return frames


# --------------------------------------------------------------------------------------------- metrics
def profit_factor(pnl: pd.Series) -> float:
    gains, losses = pnl[pnl > 0].sum(), -pnl[pnl < 0].sum()
    return float(gains / losses) if losses > 0 else (float("inf") if gains > 0 else float("nan"))


def run_variant(variant: str, card: dict[str, Any], data: dict[str, pd.DataFrame], period: str) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    """Summary rows (per coin + pooled, 1x/2x/3x) and the 1x pooled trade list of one variant in one period."""
    start, end = PERIODS[period]
    data = {symbol: frame[frame.index <= end] for symbol, frame in data.items()}
    prepared = tarama.prepare(card, data, MARKET, start=start, end=end, kilit=True)
    annual = tarama.annualization_for(card["tf"], MARKET)
    results = {mult: prepared.run(mult, trusted_inputs=True) for mult in COSTS}
    trades = results[1.0].trades.copy()
    prepared.runtime_cache.clear()
    rows = []
    pooled = {mult: calculate_metrics(result, annualization=annual) for mult, result in results.items()}
    rows.append({
        "varyant": variant, "kart": card["id"], "tf": card["tf"], "donem": period, "sembol": "HAVUZ", "grup": "havuz",
        "islem": pooled[1.0]["islem"], **{f"PF_{int(m)}x": pooled[m]["pf"] for m in COSTS},
        **{f"net_{int(m)}x": pooled[m]["getiri"] for m in COSTS}, "mdd": pooled[1.0]["mdd"], "sharpe": pooled[1.0]["sharpe"],
        "kar_payi": float("nan"),
    })
    total = trades["net_pnl"].sum() if len(trades) else 0.0
    for symbol in data:
        own = {mult: result.trades[result.trades["symbol"] == symbol]["net_pnl"] for mult, result in results.items()}
        rows.append({
            "varyant": variant, "kart": card["id"], "tf": card["tf"], "donem": period, "sembol": symbol,
            "grup": "cekirdek" if symbol in CORE else "kardes", "islem": int(len(own[1.0])),
            **{f"PF_{int(m)}x": profit_factor(own[m]) for m in COSTS}, **{f"net_{int(m)}x": float(own[m].sum()) for m in COSTS},
            "mdd": float("nan"), "sharpe": float("nan"),
            "kar_payi": float(own[1.0].sum() / total) if total > 0 else float("nan"),
        })
    return rows, trades


def deneme_sayisi(items: list[tuple[str, dict[str, Any]]]) -> int:
    return len(items)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--hat", default="0,2", help="comma separated: 0 (Faz 1 winners on crypto 1H), 2 (U1-H2 cards)")
    parser.add_argument("--donem", default="IS,OOS", help="IS, OOS, or a named configured period")
    parser.add_argument("--kart-ids", default="", help="comma separated card ids to keep (default: all of the chosen hats)")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u1")
    parser.add_argument("--sadece-say", action="store_true", help="print the variant list and trial count, run nothing")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    items = all_variants(tuple(int(h) for h in args.hat.split(",")))
    keep = {c for c in args.kart_ids.split(",") if c}
    if keep:
        items = [(v, c) for v, c in items if c["id"] in keep]
    LOG.info("%d varyant (deneme sayisi)", deneme_sayisi(items))
    if args.sadece_say:
        for variant, _ in items:
            print(variant)
        return 0

    args.results_dir.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict[str, pd.DataFrame]] = {}
    for period in args.donem.split(","):
        rows: list[dict[str, Any]] = []
        for variant, card in items:
            tf = card["tf"]
            if tf not in cache:
                cache[tf] = load_data(args.veri_kok, tf, CORE + SIBLINGS)
            if not cache[tf]:
                LOG.warning("%s: %s verisi yok (%s)", variant, tf, args.veri_kok / tarama.TF_DIR[tf])
                continue
            summary, trades = run_variant(variant, card, cache[tf], period)
            rows += summary
            safe = variant.replace("[", "_").replace("]", "").replace("=", "-").replace(":", "")
            trades.to_csv(args.results_dir / f"islemler_{safe}_{period}.csv", index=False)
            LOG.info("%s %s: %s islem, PF_1x %.2f", variant, period, summary[0]["islem"], summary[0]["PF_1x"])
        if rows:
            pd.DataFrame(rows).to_csv(args.results_dir / f"ozet_{period}.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
