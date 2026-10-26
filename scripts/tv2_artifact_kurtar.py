#!/usr/bin/env python3
"""TV-2 Actions artifact'larini satir kaybetmeden geri al."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "results" / "tv2" / "kuyruk_kripto_kalan.txt"
DEFAULT_RESULTS = ROOT / "results" / "tv2"


def _karar(path: Path) -> str | None:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("karar")
    except (OSError, ValueError, AttributeError):
        return None


def recover(artifact: Path, queue: Path, results: Path, part: int) -> tuple[int, int]:
    """Only merge IDs owned by *part*; preserve every local row except timeouts and missing data."""
    ids = queue.read_text(encoding="utf-8").splitlines()
    owned = set(ids[part::8])
    rows, returns = results / "satirlar", results / "getiriler"
    rows.mkdir(parents=True, exist_ok=True)
    returns.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    for ident in sorted(owned):
        source = artifact / "satirlar" / f"{ident}.json"
        if not source.exists():
            continue
        target = rows / source.name
        # Zaman aşımı ve veri yok satırları yeniden koşulabilir; yeni sonuç onları geçer.
        if target.exists() and _karar(target) not in {"zaman_asimi", "veri_yok"}:
            skipped += 1
            continue
        shutil.copy2(source, target)
        source_return = artifact / "getiriler" / f"{ident}.csv"
        if source_return.exists():
            shutil.copy2(source_return, returns / source_return.name)
        copied += 1
    return copied, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--part", type=int, required=True, choices=range(8))
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()
    copied, skipped = recover(args.artifact, args.queue, args.results, args.part)
    print(f"parca {args.part}: {copied} alindi, {skipped} mevcut satir korundu")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
