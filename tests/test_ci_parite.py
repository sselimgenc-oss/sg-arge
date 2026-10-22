from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtests.ci_parite import compare_parity


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def _results(root: Path, *, changed: bool = False, new_column: bool = False) -> Path:
    root.mkdir()
    tarama = [
        {"id": "C01", "piyasa": "BIST30", "tf": "1D", "PF_1x": 1.2, "git_sha": "a", "data_hash": "x"},
        {"id": "R01", "piyasa": "ABD25", "tf": "1D", "PF_1x": 1.3, "git_sha": "a", "data_hash": "x"},
    ]
    if changed:
        tarama[1]["PF_1x"] = 9.9
    if new_column:
        for row in tarama:
            row["new_diagnostic"] = "allowed"
    _write_csv(root / "tarama.csv", tarama)
    _write_csv(
        root / "asama2b.csv",
        [
            {"id": "C07", "piyasa": "ABD25", "karar": "Kosullu", "git_sha": "a", "data_hash": "x"},
            {"id": "R01", "piyasa": "ABD25", "karar": "Kosullu", "git_sha": "a", "data_hash": "x"},
            {"id": "X", "piyasa": "EMTIA", "karar": "Reddedildi", "git_sha": "a", "data_hash": "x"},
        ],
    )
    trades = root / "tarama_islemler"
    trades.mkdir()
    (trades / "R01_ABD25.csv").write_bytes(b"timestamp,pnl\n2026-01-01,1\n")
    return root


def test_parity_tolerates_new_columns_and_provenance(tmp_path: Path) -> None:
    main = _results(tmp_path / "main")
    pr = _results(tmp_path / "pr", new_column=True)

    assert compare_parity(pr_results=pr, main_results=main, asama2b_ids={"R01", "C07"}) == []


def test_parity_reports_shared_value_and_trade_differences(tmp_path: Path) -> None:
    main = _results(tmp_path / "main")
    pr = _results(tmp_path / "pr", changed=True)
    (pr / "tarama_islemler" / "R01_ABD25.csv").write_bytes(b"changed\n")

    differences = compare_parity(pr_results=pr, main_results=main, asama2b_ids={"R01", "C07"})

    assert any("tarama.csv: column PF_1x differs" in item for item in differences)
    assert any("tarama_islemler: content differs" in item for item in differences)
