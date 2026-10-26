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
    required = ("oos_net_1x", "oos_islem_hafta")
    missing = [column for column in required if column not in table or table[column].isna().all()]
    if missing:
        raise ValueError(f"{group}: zorunlu U7 v2 sutunu eksik/bos: {', '.join(missing)}")
    table.insert(0, "grup", group)
    table["aile_etiketi"] = "tarih_belirsiz"
    table["eski_huni_karari"] = table.get("karar", "")
    table["eski_huni_nedeni"] = table.get("neden", "")
    net = pd.to_numeric(table["oos_net_1x"], errors="coerce")
    table["oos_net_uygulanabilir"] = net
    weeks = pd.to_numeric(table["oos_islem_hafta"], errors="coerce")
    table["oos_islem_hafta"] = weeks
    runnable = ~table["eski_huni_karari"].astype(str).eq("Hata")
    # Existing families have translation tests, but no retrospective causality
    # audit.  Do not present that as a passed causality gate.
    table["adim0"] = "ceviri_testleri"
    table["karar_adim2"] = "Kaldı"
    table.loc[runnable & (net > 0), "karar_adim2"] = "Geçti"
    table.loc[runnable & (weeks < 10), "karar_adim2"] = "İzle"
    table.loc[~runnable, "karar_adim2"] = "Uygulanamaz"
    table["izle_listesi"] = runnable & (weeks < 10)
    table["koruma_listesi"] = (runnable & ~(weeks < 10) & ~(net > 0)).map({True: "degerlendirilecek", False: ""})
    table["adim2_neden"] = "OOS uygulanabilir net<=0"
    table.loc[runnable & (net > 0), "adim2_neden"] = "OOS uygulanabilir net>0"
    table.loc[runnable & (weeks < 10), "adim2_neden"] = "OOS işlem haftası<10"
    table.loc[~runnable, "adim2_neden"] = "Uygulanamaz: koşu hatası"
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
