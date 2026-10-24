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
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tekrar", type=int, default=200); p.add_argument("--tekrar-yuksek", type=int, default=1000)
    p.add_argument("--bootstrap-tekrar", type=int, default=1000); p.add_argument("--isci", type=int, default=0)
    p.add_argument("--veri-kok", type=Path, default=ROOT / "data"); p.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u6")
    a = p.parse_args(argv); a.results_dir.mkdir(parents=True, exist_ok=True)
    rows=[]; cache={}; u4_huni.TRIALS = TRIALS
    for variant, card, selected in u6.all_variants():
        key=selected, card["tf"]; data=cache.setdefault(key, u4.load_data(a.veri_kok,*key))
        if data: rows.append(u4_huni.evaluate_variant(variant,card,selected,data,reps=a.tekrar,reps_high=a.tekrar_yuksek,workers=a.isci or 1,boot_reps=a.bootstrap_tekrar,results_dir=a.results_dir))
    if rows: u4_huni.write_outputs(pd.DataFrame(rows,columns=u4_huni.COLUMNS),a.results_dir, trials=TRIALS, title="U6")
    return 0
if __name__ == "__main__": raise SystemExit(main())
