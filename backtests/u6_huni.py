#!/usr/bin/env python3
"""U6 funnel: delegates U4 gates with the pre-registered N=205 trial count."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from backtests import u4, u4_huni, u6

TRIALS = 205


def _checkpoint_path(results_dir: Path, variant: str) -> Path:
    return results_dir / "parca" / f"{variant.replace(':', '_')}.csv"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tekrar", type=int, default=200); p.add_argument("--tekrar-yuksek", type=int, default=1000)
    p.add_argument("--bootstrap-tekrar", type=int, default=1000); p.add_argument("--isci", type=int, default=0)
    p.add_argument("--veri-kok", type=Path, default=ROOT / "data"); p.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u6")
    p.add_argument("--resume", action="store_true", help="reuse completed per-card checkpoint rows")
    a = p.parse_args(argv); a.results_dir.mkdir(parents=True, exist_ok=True)
    rows=[]; cache={}
    items, skipped = u6.variants_and_skips()
    u6.write_skips(skipped, a.results_dir)
    original_trials = u4_huni.TRIALS
    try:
        u4_huni.TRIALS = TRIALS  # DSR inside evaluate_variant must use U6's fixed N.
        for variant, card, selected in items:
            checkpoint = _checkpoint_path(a.results_dir, variant)
            if a.resume and checkpoint.exists():
                saved = pd.read_csv(checkpoint)
                if len(saved) == 1 and saved.loc[0, "varyant"] == variant:
                    rows.append(saved.iloc[0].to_dict())
                    continue
            key=selected, card["tf"]; data=cache.setdefault(key, u4.load_data(a.veri_kok,*key))
            if data:
                row = u4_huni.evaluate_variant(variant,card,selected,data,reps=a.tekrar,reps_high=a.tekrar_yuksek,workers=a.isci or 1,boot_reps=a.bootstrap_tekrar,results_dir=a.results_dir)
                rows.append(row)
                checkpoint.parent.mkdir(parents=True, exist_ok=True)
                pd.DataFrame([row], columns=u4_huni.COLUMNS).to_csv(checkpoint, index=False)
                u4_huni.write_outputs(pd.DataFrame(rows, columns=u4_huni.COLUMNS), a.results_dir, trials=TRIALS, title="U6")
    finally:
        u4_huni.TRIALS = original_trials
    if rows: u4_huni.write_outputs(pd.DataFrame(rows,columns=u4_huni.COLUMNS),a.results_dir, trials=TRIALS, title="U6")
    return 0
if __name__ == "__main__": raise SystemExit(main())
