#!/usr/bin/env python3
"""Collect TradingView publication and Pine version metadata for TV-2."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import re
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "arastirma" / "U5_tv.csv"
TARGET = ROOT / "arastirma" / "tv2_surumler.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; sg-arge TV-2 metadata collector)"}


def _json_string(page: str, key: str) -> str:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"', page)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group(1)}"')
    except json.JSONDecodeError:
        return match.group(1)


def _pub(page: str) -> str:
    value = _json_string(page, "script_id_part") or _json_string(page, "scriptIdPart")
    return value if value.startswith("PUB;") else ""


def _page_metadata(page: str, fallback_tf: str) -> tuple[str, str]:
    # TradingView currently nests the selected chart in
    # ``"symbol":{"pro_symbol":"EXCHANGE:TICKER"}``; old pages used the
    # flat ticker/symbol keys.
    symbol = (_json_string(page, "pro_symbol") or _json_string(page, "symbol")
              or _json_string(page, "ticker"))
    interval = _json_string(page, "interval") or fallback_tf.removeprefix("grafik:")
    return symbol, interval


def _version_rows(client: requests.Session, pub: str) -> tuple[str, str, str, str, int]:
    encoded = requests.utils.quote(pub, safe="")
    versions = client.get(f"https://pine-facade.tradingview.com/pine-facade/versions/{encoded}", timeout=25)
    if versions.status_code in (401, 403):
        return "", "", "", "kaynak gizli", 0
    if versions.status_code == 404:
        return "", "", "", "script bulunamadi veya kapali", 0
    versions.raise_for_status()
    history = versions.json()
    if not isinstance(history, list) or not history:
        return "", "", "", "surum gecmisi yok", 0

    # The versions endpoint is the source of record.  Do not infer history
    # from numeric Pine endpoints: minor revisions are otherwise lost.
    dated = [item for item in history if isinstance(item, dict) and item.get("created")]
    if not dated:
        return "", "", "", "surum tarihinde created yok", len(history)
    dated.sort(key=lambda item: str(item["created"]))
    first, latest = dated[0], dated[-1]

    last = client.get(f"https://pine-facade.tradingview.com/pine-facade/get/{encoded}/last", timeout=25)
    if last.status_code in (401, 403):
        return "", "", "", "kaynak gizli", 0
    last.raise_for_status()
    payload: dict[str, Any] = last.json()
    if not payload.get("source"):
        return "", "", "", "kaynak gizli", 0
    return str(latest.get("version") or ""), str(latest["created"]), str(first["created"]), "acik", len(history)


def collect(row: dict[str, str]) -> dict[str, str]:
    out = {key: "" for key in ("id", "pub", "son_surum", "son_surum_tarihi", "ilk_yayin_tarihi", "surum_sayisi", "kaynak_acik", "yayin_sembolu", "tf")}
    out["id"] = row["id"]
    out["tf"] = row.get("tf", "").removeprefix("grafik:")
    try:
        with requests.Session() as client:
            client.headers.update(HEADERS)
            page_response = client.get(row["url"], timeout=25)
            if page_response.status_code in (401, 403, 404):
                out["kaynak_acik"] = f"sayfa kapali ({page_response.status_code})"
                return out
            page_response.raise_for_status()
            page = page_response.text
            pub = _pub(page)
            if not pub:
                out["kaynak_acik"] = "PUB kimligi sayfada yok"
                return out
            out["pub"] = pub
            out["yayin_sembolu"], out["tf"] = _page_metadata(page, out["tf"])
            version, last_date, first_date, status, count = _version_rows(client, pub)
            out.update(son_surum=version, son_surum_tarihi=last_date, ilk_yayin_tarihi=first_date,
                       kaynak_acik=status, surum_sayisi=str(count))
            if status == "acik":
                # A page-level timestamp is useful when the facade has retained only
                # its latest revision; use it only as a fallback to API history.
                out["ilk_yayin_tarihi"] = out["ilk_yayin_tarihi"] or _json_string(page, "created_at")
    except requests.RequestException as exc:
        out["kaynak_acik"] = f"erisim hatasi: {type(exc).__name__}"
    except (ValueError, json.JSONDecodeError) as exc:
        out["kaynak_acik"] = f"yanit okunamadi: {type(exc).__name__}"
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--target", type=Path, default=TARGET)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--retry-closed", action="store_true",
                        help="Mevcut tabloda acik olmayanlari eski alfanumerik script URL'siyle yeniden ara")
    args = parser.parse_args()
    with args.source.open(encoding="utf-8", newline="") as handle:
        source_rows = [row for row in csv.DictReader(handle) if row["suzgec_sonucu"] in {"elendi:tf_disi", "elendi:tf_belirsiz"}]
    rows = source_rows
    existing: list[dict[str, str]] = []
    if args.retry_closed:
        with args.target.open(encoding="utf-8", newline="") as handle:
            existing = list(csv.DictReader(handle))
        source_by_id = {row["id"]: row for row in source_rows}
        rows = [source_by_id[row["id"]] for row in existing
                if row.get("kaynak_acik") != "acik" and row["id"] in source_by_id]
    if args.limit:
        rows = rows[:args.limit]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        output = list(pool.map(collect, rows))
    fields = ["id", "pub", "son_surum", "son_surum_tarihi", "ilk_yayin_tarihi", "surum_sayisi", "kaynak_acik", "yayin_sembolu", "tf"]
    if args.retry_closed:
        refreshed = {row["id"]: row for row in output}
        merged: list[dict[str, str]] = []
        for old in existing:
            new = refreshed.get(old["id"])
            if new is None:
                merged.append(old)
            elif new["kaynak_acik"] == "acik":
                merged.append(new)
            else:
                # Keep the formerly observed publication/symbol, but make the retry
                # and its concrete failure visible rather than silently discarding it.
                old = dict(old)
                old["kaynak_acik"] = f"yeniden arandi: {new['kaynak_acik']}"
                merged.append(old)
        output = merged
    with args.target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
    print(f"{len(output)} satir: {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
