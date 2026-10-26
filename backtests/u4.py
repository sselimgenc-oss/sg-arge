#!/usr/bin/env python3
"""U4 runner: four fixed cards across crypto 4H/1D, ABD25 1D and EMTIA 1D.

The pre-registration in docs/GOREV_U4.md defines exactly 16 variants.  This
runner uses all available selected-period data and writes reproducible summaries only;
trade ledgers are disposable, ignored artefacts for the funnel.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import tarama
from backtests.run_codex21 import _load_market
from data.evren_pit import load_pit_universe
from data.fetch import normalize_ohlcv
from engine.portfolio import calculate_metrics
from engine.spec import normalize_timeframe

LOG = logging.getLogger("u4")
SPEC = ROOT / "docs" / "spec"
CARD_IDS = ("U4-H1", "U4-H2", "U4-H3", "U4-H4")
CORE = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "TRXUSDT")
SIBLINGS = ("ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT", "AVAXUSDT", "BCHUSDT", "NEARUSDT")
COSTS = (1.0, 2.0, 3.0)
PERIODS = {
    "ON": (pd.Timestamp("2015-01-01", tz="UTC"), pd.Timestamp("2017-12-31", tz="UTC")),
    "IS": (pd.Timestamp("2018-01-01", tz="UTC"), pd.Timestamp("2022-12-31", tz="UTC")),
    "OOS": (pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2100-01-01", tz="UTC")),
}
ARMS = (("KRIPTO25", "4H"), ("KRIPTO25", "1D"), ("ABD25", "1D"), ("EMTIA", "1D"))


def lock_check(end: pd.Timestamp) -> None:
    """Compatibility no-op after U7 removed the locked-period policy."""
    del end


def load_card(card_id: str, directory: Path = SPEC) -> dict[str, Any]:
    card = yaml.safe_load((directory / f"{card_id}.yaml").read_text(encoding="utf-8"))
    card["tf"] = normalize_timeframe(card.get("tf"))
    return card


def all_variants(directory: Path = SPEC) -> list[tuple[str, dict[str, Any], str]]:
    """The fixed 4 cards × 4 arms, with no grid expansion."""
    out = []
    for card_id in CARD_IDS:
        base = load_card(card_id, directory)
        for market, tf in ARMS:
            card = dict(base, tf=tf)
            out.append((f"{card_id}:{market}:{tf}", card, market))
    return out


def deneme_sayisi(items: list[tuple[str, dict[str, Any], str]]) -> int:
    return len(items)


def _daily(root: Path, market: str, *, pit: bool) -> dict[str, pd.DataFrame]:
    frames, _digest, _missing = _load_market(market, root / "daily", "pit" if pit else "sabit")
    return frames


def load_data(root: Path, market: str, tf: str) -> dict[str, pd.DataFrame]:
    if market == "KRIPTO25" and tf == "4H":
        frames = {s: normalize_ohlcv(pd.read_parquet(root / "hourly" / f"{s}.parquet")) for s in CORE + SIBLINGS
                  if (root / "hourly" / f"{s}.parquet").exists()}
        # raw 1H bars: tarama.prepare resamples a tf=4H card itself (UTC 00/04/.. buckets); resampling here too made
        # every 4H bar look incomplete and dropped the whole series (PR #171 run report)
        return {s: frame for s, frame in frames.items() if not frame.empty}
    if market == "KRIPTO25":
        frames = {s: normalize_ohlcv(pd.read_parquet(root / "daily" / f"{s}.parquet")) for s in CORE + SIBLINGS
                  if (root / "daily" / f"{s}.parquet").exists()}
        return {s: f for s, f in frames.items() if not f.empty}
    return _daily(root, market, pit=market == "ABD25")


def run_variant(variant: str, card: dict[str, Any], market: str, data: dict[str, pd.DataFrame], period: str):
    start, end = PERIODS[period]
    lock_check(end)
    pit = load_pit_universe() if market == "ABD25" else None
    prepared = tarama.prepare(card, data, market, start=start, end=end, kilit=True, pit_universe=pit)
    annual = tarama.annualization_for(card["tf"], market)
    runs = {cost: prepared.run(cost, trusted_inputs=True) for cost in COSTS}
    trades = runs[1.0].trades.copy()
    prepared.runtime_cache.clear()
    metrics = {cost: calculate_metrics(result, annualization=annual) for cost, result in runs.items()}
    row = {
        "varyant": variant, "kart": card["id"], "piyasa": market, "tf": card["tf"], "donem": period,
        "islem": metrics[1.0]["islem"], "PF_1x": metrics[1.0]["pf"], "PF_2x": metrics[2.0]["pf"], "PF_3x": metrics[3.0]["pf"],
        "net_1x": metrics[1.0]["getiri"], "net_2x": metrics[2.0]["getiri"], "net_3x": metrics[3.0]["getiri"],
        "ortR": metrics[1.0]["ortalama_r"], "mdd": metrics[1.0]["mdd"],
    }
    return row, trades


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donem", default="IS,OOS")
    parser.add_argument("--kart-ids", default="")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u4")
    parser.add_argument("--sadece-say", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    items = all_variants()
    wanted = {x for x in args.kart_ids.split(",") if x}
    if wanted:
        items = [item for item in items if item[1]["id"] in wanted]
    LOG.info("%d varyant (deneme sayisi)", deneme_sayisi(items))
    if args.sadece_say:
        print("\n".join(variant for variant, _card, _market in items))
        return 0
    args.results_dir.mkdir(parents=True, exist_ok=True)
    cache: dict[tuple[str, str], dict[str, pd.DataFrame]] = {}
    for period in args.donem.split(","):
        rows = []
        for variant, card, market in items:
            key = market, card["tf"]
            data = cache.setdefault(key, load_data(args.veri_kok, market, card["tf"]))
            if not data:
                LOG.warning("%s: veri yok", variant)
                continue
            row, _trades = run_variant(variant, card, market, data, period)
            rows.append(row)
            LOG.info("%s %s: %s islem PF %.2f", variant, period, row["islem"], row["PF_1x"])
        if rows:
            pd.DataFrame(rows).to_csv(args.results_dir / f"ozet_{period}.csv", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
