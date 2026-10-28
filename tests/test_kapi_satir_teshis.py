"""Kapı satır teşhis aracının adres çakışması altın örneği."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from copytrade.kapi_satir_teshis import inspect


def _shard(root: Path, part: int, result: list[str], plan: list[str]) -> None:
    folder = root / f"stage1-{part}" / "2026-10-28"
    folder.mkdir(parents=True)
    (folder / "evren.json").write_text(json.dumps({"evren": 4}))
    (folder / "bitti.json").write_text(json.dumps({"islenen": len(result)}))
    (folder / "sonuc.csv").write_text("address\n" + "\n".join(result) + "\n")
    with gzip.open(folder / "asama1.csv.gz", "wt") as handle:
        handle.write("address\n" + "\n".join(plan) + "\n")


def test_altin_ornek_teshis_parcalar_arasi_adres_cakismasini_gosterir(tmp_path):
    _shard(tmp_path, 0, ["0xa", "0xb"], ["0xa", "0xb"])
    _shard(tmp_path, 1, ["0xb", "0xc"], ["0xb", "0xc"])
    report = inspect(tmp_path)
    assert "tekil adres: **3**" in report
    assert "yinelenen satır: **1**" in report
    assert "| 0 | 1 | 1 |" in report
    assert "`0xb` | 0, 1" in report
