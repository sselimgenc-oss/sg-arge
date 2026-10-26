"""Append-only candidate watchlist; t0 is never rewritten."""
from __future__ import annotations

import csv
from pathlib import Path


FIELDS = ("address", "t0", "version", "status")


def load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def update(path: Path, candidates: list[str], today: str, version: str, statuses: dict[str, str], limit: int = 50) -> list[dict[str, str]]:
    rows = load(path)
    by_address = {row["address"].lower(): row for row in rows}
    for address, row in by_address.items():
        row["status"] = statuses.get(address, row.get("status", "izleniyor"))
    for address in candidates:
        key = address.lower()
        if key not in by_address and len(rows) < limit:
            row = {"address": address, "t0": today, "version": version, "status": statuses.get(key, "izleniyor")}
            rows.append(row)
            by_address[key] = row
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows
