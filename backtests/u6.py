#!/usr/bin/env python3
"""U6 translated TradingView cards runner; locked data is never selectable here."""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
import sys
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from backtests import u4
from engine.spec import normalize_timeframe

LOG = logging.getLogger("u6")
SPEC = ROOT / "docs" / "spec"

def market(card: dict) -> str | None:
    text = " ".join(map(str, card.get("piyasa_kisiti") or [])).upper()
    if "KRIPTO" in text: return "KRIPTO25"
    if "ABD" in text: return "ABD25"
    if "EMTIA" in text: return "EMTIA"
    return None

def all_variants(directory: Path = SPEC):
    out = []
    for path in sorted(directory.glob("TV-*.yaml")):
        card = yaml.safe_load(path.read_text(encoding="utf-8"))
        selected = market(card)
        if selected is None or card.get("spec_durumu") != "tam":
            continue
        card["tf"] = normalize_timeframe(card.get("tf"))
        if card["tf"] not in {"1D", "4H"}: continue
        if selected != "KRIPTO25" and card["tf"] == "4H": continue
        out.append((card["id"], card, selected))
    return out

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--donem", default="IS,OOS"); p.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    p.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u6"); p.add_argument("--kart-ids", default="")
    p.add_argument("--sadece-say", action="store_true")
    a = p.parse_args(argv); logging.basicConfig(level=logging.INFO, format="%(message)s")
    items = all_variants(); wanted = set(filter(None, a.kart_ids.split(",")))
    if wanted: items = [x for x in items if x[1]["id"] in wanted]
    LOG.info("%d U6 kart", len(items))
    if a.sadece_say: print("\n".join(v for v, _, _ in items)); return 0
    a.results_dir.mkdir(parents=True, exist_ok=True); cache = {}
    for period in a.donem.split(","):
        rows = []
        for variant, card, selected in items:
            key = selected, card["tf"]; data = cache.setdefault(key, u4.load_data(a.veri_kok, *key))
            if data: rows.append(u4.run_variant(variant, card, selected, data, period)[0])
        if rows: pd.DataFrame(rows).to_csv(a.results_dir / f"ozet_{period}.csv", index=False)
    return 0
if __name__ == "__main__": raise SystemExit(main())
