#!/usr/bin/env python3
"""Update dashboard-only hourly marks for the final open positions in the paper ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper import gunluk

PANEL_PATH = Path(__file__).resolve().parent / "panel" / "data.json"
ANLIK_NOT = "Açık pozisyonlar saatlik fiyatla değerlenir; işlemler ve defter yalnız günlük kapanışta güncellenir."


def saatlik_fiyat(symbol: str) -> tuple[float, pd.Timestamp] | None:
    """Return the latest available one-hour close without writing an archive."""
    history = yf.Ticker(symbol).history(period="5d", interval="1h", auto_adjust=False)
    if history.empty:
        return None
    timestamp = pd.Timestamp(history.index[-1])
    timestamp = timestamp.tz_localize("UTC") if timestamp.tzinfo is None else timestamp.tz_convert("UTC")
    return float(history["Close"].iloc[-1]), timestamp


def guncelle(
    defter: Path = gunluk.LEDGER_DIR,
    cikti: Path = PANEL_PATH,
    *,
    fiyat_al: Callable[[str], tuple[float, pd.Timestamp] | None] = saatlik_fiyat,
    simdi: pd.Timestamp | None = None,
) -> dict[str, Any]:
    """Mark open positions in data.json; the append-only ledger is deliberately read-only."""
    payload = json.loads(cikti.read_text(encoding="utf-8"))
    positions = gunluk._read(defter, "pozisyonlar")  # noqa: SLF001
    latest = positions[positions["tarih"] == positions["tarih"].max()] if not positions.empty else positions
    by_key = {(str(row["satir"]), str(row["sembol"])): row for row in latest.to_dict("records")}
    changes, times, all_live = [], [], bool(payload.get("open_positions"))
    for item in payload.get("open_positions", []):
        key = (str(item["account"]).replace(" · ", ":"), str(item["asset"]))
        row = by_key.get(key)
        if row is None:
            all_live = False
            continue
        quote = fiyat_al(key[1])
        if quote is None:
            price = float(row["son_kapanis"])
            timestamp = pd.Timestamp(row["tarih"], tz="UTC")
            all_live = False
        else:
            price, timestamp = quote
            timestamp = pd.Timestamp(timestamp)
            timestamp = timestamp.tz_localize("UTC") if timestamp.tzinfo is None else timestamp.tz_convert("UTC")
        pnl = (price - float(row["giris_fiyati"])) * float(row["adet"])
        previous = float(item.get("unrealized_pnl") or 0.0)
        changes.append(pnl - previous)
        times.append(timestamp)
        item["current_price"] = round(price, 4)
        item["size_usd"] = round(price * float(row["adet"]), 2)
        item["unrealized_pnl"] = round(pnl, 2)
    kpis = payload["kpis"]
    total = float(kpis["total_value"]) + sum(changes)
    initial = float(kpis["initial_total_capital"])
    kpis["total_value"] = round(total, 2)
    kpis["total_return_pct"] = round((total / initial - 1) * 100, 2)
    now = simdi or pd.Timestamp.now(tz="UTC")
    now = pd.Timestamp(now)
    now = now.tz_localize("UTC") if now.tzinfo is None else now.tz_convert("UTC")
    meta = payload.setdefault("meta", {})
    meta["updated_at"] = now.isoformat()
    meta["fiyat_zamani"] = (max(times) if times else now).isoformat()
    meta["fiyat_kaynagi"] = "anlik" if all_live else "son_kapanis"
    meta["anlik_not"] = ANLIK_NOT
    cikti.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--defter", type=Path, default=gunluk.LEDGER_DIR)
    parser.add_argument("--cikti", type=Path, default=PANEL_PATH)
    args = parser.parse_args()
    payload = guncelle(args.defter, args.cikti)
    print(f"{args.cikti} anlık değerleme: {len(payload.get('open_positions', []))} açık, {payload['meta']['fiyat_zamani']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
