#!/usr/bin/env python3
"""Build U7's v2 decision table from completed group funnel summaries.

The historical funnel remains intact as information.  ``karar_adim2`` is the
only decision under TEST_YAPISI v2; portfolio-dependent protection eligibility
is deliberately marked for the leader's shared-portfolio calculation rather
than guessed from an individual series.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _group_table(group: str, path: Path) -> pd.DataFrame:
    table = pd.read_csv(path)
    table.insert(0, "grup", group)
    table["aile_etiketi"] = "tarih_belirsiz"
    table["eski_huni_karari"] = table.get("karar", "")
    table["eski_huni_nedeni"] = table.get("neden", "")
    net = pd.to_numeric(table.get("oos_net_1x"), errors="coerce")
    if net.isna().all() and "net_1x" in table:
        net = pd.to_numeric(table["net_1x"], errors="coerce")
    table["oos_net_uygulanabilir"] = net
    weeks = pd.to_numeric(table.get("oos_islem_hafta"), errors="coerce")
    table["oos_islem_hafta"] = weeks
    runnable = ~table["eski_huni_karari"].astype(str).eq("Hata")
    table["adim0"] = runnable.map({True: "Gecti", False: "Uygulanamaz"})
    table["karar_adim2"] = "Reddedildi"
    table.loc[runnable & (net > 0), "karar_adim2"] = "Gecti"
    table["izle_listesi"] = (weeks < 10) & runnable
    table["koruma_listesi"] = (runnable & ~(net > 0)).map({True: "degerlendirilecek", False: ""})
    table["adim2_neden"] = "OOS uygulanabilir net<=0"
    table.loc[~runnable, "adim2_neden"] = "Adim 0 uygulanamadi"
    table.loc[runnable & (net > 0), "adim2_neden"] = "OOS uygulanabilir net>0"
    return table


def build(groups: dict[str, Path], target: Path) -> pd.DataFrame:
    tables = [_group_table(name, path) for name, path in groups.items() if path.exists()]
    if not tables:
        raise FileNotFoundError("tamamlanmis grup huni_ozeti yok")
    output = pd.concat(tables, ignore_index=True, sort=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(target, index=False)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u7")
    args = parser.parse_args(argv)
    root = args.results_dir
    groups = {name: root / name / "huni_ozet.csv" for name in ("u1", "u4", "u6", "faz1", "reddit")}
    table = build(groups, root / "huni_ozet.csv")
    print(f"{len(table)} satir: {root / 'huni_ozet.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
