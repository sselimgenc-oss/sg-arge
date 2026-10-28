"""Belirli bir CT-Kapı Actions koşusunun parça artefaktlarını satır sayısı için inceler."""
from __future__ import annotations
import csv, json
from pathlib import Path


def inspect(root: Path, day: str = "2026-10-28") -> str:
    rows = []
    for part in range(32):
        bases = list(root.glob(f"stage1-{part}/**/{day}"))
        base = bases[0] if bases else None
        universe = json.loads((base / "evren.json").read_text())["evren"] if base and (base / "evren.json").exists() else None
        planned = (universe - part + 31) // 32 if universe is not None else None
        result = sum(1 for _ in csv.DictReader((base / "sonuc.csv").open())) if base and (base / "sonuc.csv").exists() else 0
        done = json.loads((base / "bitti.json").read_text()).get("islenen") if base and (base / "bitti.json").exists() else None
        rows.append((part, planned, done, result, "evet" if done is not None else "hayır"))
    lines = ["# Tam kapı satır teşhisi", "", "Run: `40711594322` · gün: `2026-10-28`.", "",
             "| Parça | Plan | İşlenen (bitti/log) | sonuc.csv | bitti.json |", "| ---: | ---: | ---: | ---: | :---: |"]
    lines += [f"| {part} | {plan or '—'} | {done if done is not None else '—'} | {result} | {finished} |" for part, plan, done, result, finished in rows]
    lines += ["", "## Bulgu", "", "`bitti.json` işlenen sayısı ile `sonuc.csv` satırı ayrışıyorsa kayıp parça içindedir; evren tüm parçalarda aynıysa evren sayımı kaynak değildir."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(); p.add_argument("root", type=Path); p.add_argument("--output", type=Path, required=True)
    a = p.parse_args(); a.output.write_text(inspect(a.root), encoding="utf-8")
