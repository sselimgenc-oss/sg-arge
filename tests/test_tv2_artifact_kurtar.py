"""TV-2 artifact kurtarmasinda tamamlanmis sonuc korunur."""

import importlib.util
import json
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "tv2_artifact_kurtar", Path(__file__).parents[1] / "scripts" / "tv2_artifact_kurtar.py"
)
assert SPEC and SPEC.loader
kurtar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kurtar)


def _row(path: Path, karar: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"id": path.stem, "karar": karar}), encoding="utf-8")


def test_recover_replaces_only_timeout_rows_and_only_its_part(tmp_path: Path) -> None:
    queue = tmp_path / "queue.txt"
    queue.write_text("a\nb\nc\nd\ne\nf\ng\nh\ni\n", encoding="utf-8")  # part 0: a, i
    artifact, results = tmp_path / "artifact", tmp_path / "results"
    _row(artifact / "satirlar" / "a.json", "gecti")
    _row(artifact / "satirlar" / "i.json", "kaldi")
    _row(artifact / "satirlar" / "b.json", "gecti")
    (artifact / "getiriler").mkdir(parents=True)
    (artifact / "getiriler" / "a.csv").write_text("getiri\n1\n", encoding="utf-8")
    _row(results / "satirlar" / "a.json", "zaman_asimi")
    _row(results / "satirlar" / "i.json", "gecti")

    copied, skipped = kurtar.recover(artifact, queue, results, 0)

    assert (copied, skipped) == (1, 1)
    assert json.loads((results / "satirlar" / "a.json").read_text())["karar"] == "gecti"
    assert json.loads((results / "satirlar" / "i.json").read_text())["karar"] == "gecti"
    assert not (results / "satirlar" / "b.json").exists()
    assert (results / "getiriler" / "a.csv").exists()
