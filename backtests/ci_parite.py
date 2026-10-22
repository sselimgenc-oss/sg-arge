#!/usr/bin/env python3
"""Compare the small real-data regression run of a PR with ``main``.

The workflow deliberately compares only columns both revisions understand.  A
new diagnostic column is therefore safe, whereas a changed shared result,
missing trade file, or changed number of stage-2b rows fails the PR.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

IGNORED_COLUMNS = frozenset({"git_sha", "data_hash"})


def _normalise(table: pd.DataFrame, *, key_columns: Iterable[str] = ()) -> pd.DataFrame:
    result = table.copy()
    columns = [column for column in key_columns if column in result]
    if columns:
        result = result.sort_values(columns, kind="stable", na_position="first")
    return result.reset_index(drop=True)


def compare_csv(
    pr_path: Path,
    main_path: Path,
    *,
    key_columns: Iterable[str] = (),
    only_ids: set[str] | None = None,
) -> list[str]:
    """Return readable differences, comparing only shared non-provenance columns."""

    label = pr_path.name
    if not pr_path.exists() or not main_path.exists():
        return [f"{label}: missing file (PR={pr_path.exists()}, main={main_path.exists()})"]
    pr, main = pd.read_csv(pr_path), pd.read_csv(main_path)
    if only_ids is not None:
        if "id" not in pr or "id" not in main:
            return [f"{label}: selected ID comparison requires id column"]
        pr, main = pr[pr["id"].astype(str).isin(only_ids)], main[main["id"].astype(str).isin(only_ids)]
        for side, table in (("PR", pr), ("main", main)):
            absent = sorted(only_ids.difference(table["id"].astype(str)))
            if absent:
                return [f"{label}: {side} missing selected IDs: {','.join(absent)}"]
    shared = sorted((set(pr.columns) & set(main.columns)).difference(IGNORED_COLUMNS))
    if not shared:
        return [f"{label}: no shared non-provenance columns"]
    order = [column for column in key_columns if column in shared]
    pr, main = _normalise(pr.loc[:, shared], key_columns=order), _normalise(main.loc[:, shared], key_columns=order)
    if len(pr) != len(main):
        return [f"{label}: row count differs (PR={len(pr)}, main={len(main)})"]
    differences: list[str] = []
    for column in shared:
        left, right = pr[column], main[column]
        equal = left.eq(right) | (left.isna() & right.isna())
        if not bool(equal.all()):
            examples = ", ".join(
                f"row {index}: PR={left.iloc[index]!r}, main={right.iloc[index]!r}"
                for index in equal.index[~equal][:3]
            )
            differences.append(f"{label}: column {column} differs ({examples})")
    return differences


def compare_tree(pr_dir: Path, main_dir: Path) -> list[str]:
    """Compare a trade-output tree byte for byte, including its file list."""

    pr_files = {path.relative_to(pr_dir) for path in pr_dir.rglob("*") if path.is_file()} if pr_dir.exists() else set()
    main_files = {path.relative_to(main_dir) for path in main_dir.rglob("*") if path.is_file()} if main_dir.exists() else set()
    differences: list[str] = []
    if pr_files != main_files:
        differences.append(
            "tarama_islemler: file list differs "
            f"(PR-only={','.join(map(str, sorted(pr_files - main_files))) or '-'}; "
            f"main-only={','.join(map(str, sorted(main_files - pr_files))) or '-'})"
        )
    for relative in sorted(pr_files & main_files):
        if (pr_dir / relative).read_bytes() != (main_dir / relative).read_bytes():
            differences.append(f"tarama_islemler: content differs: {relative}")
    return differences


def compare_parity(
    *,
    pr_results: Path,
    main_results: Path,
    asama2b_ids: set[str],
) -> list[str]:
    """Compare the workflow artifacts requested by T28."""

    differences = compare_csv(
        pr_results / "tarama.csv", main_results / "tarama.csv", key_columns=("id", "piyasa", "tf")
    )
    differences.extend(compare_tree(pr_results / "tarama_islemler", main_results / "tarama_islemler"))
    pr_stage2, main_stage2 = pr_results / "asama2b.csv", main_results / "asama2b.csv"
    if pr_stage2.exists() and main_stage2.exists():
        pr_count, main_count = len(pd.read_csv(pr_stage2)), len(pd.read_csv(main_stage2))
        if pr_count != main_count:
            differences.append(f"asama2b.csv: total row count differs (PR={pr_count}, main={main_count})")
    differences.extend(
        compare_csv(pr_stage2, main_stage2, key_columns=("id", "piyasa"), only_ids=asama2b_ids)
    )
    return differences


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-results", type=Path, required=True)
    parser.add_argument("--main-results", type=Path, required=True)
    parser.add_argument("--asama2b-ids", default="R01,C07")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ids = {value.strip() for value in args.asama2b_ids.split(",") if value.strip()}
    differences = compare_parity(pr_results=args.pr_results, main_results=args.main_results, asama2b_ids=ids)
    if differences:
        print("Parity differences:")
        print("\n".join(f"- {item}" for item in differences))
        return 1
    print("Parity passed: shared result columns, stage-2b row count, and trades match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
