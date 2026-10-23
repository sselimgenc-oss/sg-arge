"""Download Dukascopy 1-minute candles (bid + ask) and archive them as yearly Parquet (T36a).

Dukascopy serves one LZMA-compressed file per day and side:
``https://datafeed.dukascopy.com/datafeed/<SYM>/<YYYY>/<MM-1:02d>/<DD:02d>/<BID|ASK>_candles_min_1.bi5``.
Each record is 24 bytes, big-endian: seconds from day start (uint32), open, close, low, high
(uint32, price / point) and volume (float32). Month is zero-based in the URL.

Archived bars are UTC, labelled by bar start, with mid OHLC = (bid + ask) / 2 and the
spread (ask close - bid close) kept for the cost model (T36b ``FXDK``).
"""

from __future__ import annotations

import argparse
import lzma
import struct
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "dakika"
BASE_URL = "https://datafeed.dukascopy.com/datafeed"
RECORD = struct.Struct(">IIIIIf")
COLUMNS = ["sec", "open", "close", "low", "high", "volume"]
REQUEST_DELAY = 0.75

# Price divisor (1 / point). Index CFD divisors must be confirmed against a reference
# close before the archive is used (see ``check_scale``).
POINT_DIVISOR = {
    "USDJPY": 1_000,
    "USDCHF": 100_000,
    "EURUSD": 100_000,
    "USATECHIDXUSD": 1_000,
}
START = {
    "USDJPY": date(2010, 1, 1),
    "USDCHF": date(2010, 1, 1),
    "USATECHIDXUSD": date(2012, 1, 1),
}


def day_url(symbol: str, day: date, side: str) -> str:
    return f"{BASE_URL}/{symbol}/{day.year}/{day.month - 1:02d}/{day.day:02d}/{side}_candles_min_1.bi5"


def decode(raw: bytes, day: date, divisor: int) -> pd.DataFrame:
    """Decode one compressed daily file into UTC-indexed OHLCV (empty frame for no data)."""
    if not raw:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    payload = lzma.decompress(raw)
    if len(payload) % RECORD.size:
        raise ValueError(f"bi5 length {len(payload)} is not a multiple of {RECORD.size}")
    frame = pd.DataFrame(list(RECORD.iter_unpack(payload)), columns=COLUMNS)
    base = pd.Timestamp(day, tz="UTC")
    frame.index = base + pd.to_timedelta(frame.pop("sec"), unit="s")
    frame.index.name = "timestamp"
    for col in ("open", "close", "low", "high"):
        frame[col] = frame[col] / divisor
    return frame[["open", "high", "low", "close", "volume"]]


def merge_sides(bid: pd.DataFrame, ask: pd.DataFrame) -> pd.DataFrame:
    """Mid OHLC from bid/ask candles; drops flat no-trade minutes (zero volume on both sides)."""
    joined = bid.join(ask, lsuffix="_bid", rsuffix="_ask", how="inner")
    out = pd.DataFrame(index=joined.index)
    for col in ("open", "high", "low", "close"):
        out[col] = (joined[f"{col}_bid"] + joined[f"{col}_ask"]) / 2
    out["volume"] = joined["volume_bid"] + joined["volume_ask"]
    out["spread"] = joined["close_ask"] - joined["close_bid"]
    return out[out["volume"] > 0]


def fetch_day(
    session: requests.Session,
    symbol: str,
    day: date,
    retries: int = 4,
    delay: float = REQUEST_DELAY,
) -> pd.DataFrame:
    divisor = POINT_DIVISOR[symbol]
    sides = {}
    for side in ("BID", "ASK"):
        needs_spacing = bool(sides)
        for attempt in range(retries):
            if needs_spacing:
                time.sleep(delay)
                needs_spacing = False
            resp = session.get(day_url(symbol, day, side), timeout=30)
            if resp.status_code == 404:
                sides[side] = decode(b"", day, divisor)
                break
            if resp.ok:
                sides[side] = decode(resp.content, day, divisor)
                break
            if resp.status_code not in (429, 500, 502, 503, 504):
                raise RuntimeError(f"{symbol} {day} {side}: HTTP {resp.status_code}")
            retry_after = resp.headers.get("Retry-After", "")
            try:
                backoff = max(delay, float(retry_after))
            except ValueError:
                backoff = delay * (2**attempt)
            time.sleep(backoff)
            needs_spacing = False
        else:
            raise RuntimeError(f"{symbol} {day} {side}: HTTP {resp.status_code}")
    return merge_sides(sides["BID"], sides["ASK"])


def archive_path(symbol: str, year: int) -> Path:
    return DATA_DIR / symbol / f"{year}.parquet"


def fetch_year(
    symbol: str,
    year: int,
    *,
    session: requests.Session | None = None,
    existing: pd.DataFrame | None = None,
    delay: float = REQUEST_DELAY,
    on_day: Callable[[pd.DataFrame], None] | None = None,
) -> pd.DataFrame:
    """Fetch a year, skipping dates already present in *existing*.

    ``on_day`` is called after each newly fetched day.  The CLI uses it to
    checkpoint the Parquet file, so an interrupted run can resume safely.
    """
    session = session or requests.Session()
    existing = existing.copy() if existing is not None else pd.DataFrame()
    present = set(existing.index.date) if not existing.empty else set()
    start = max(date(year, 1, 1), START.get(symbol, date(year, 1, 1)))
    end = min(date(year, 12, 31), date.today() - timedelta(days=1))
    frames = [existing] if not existing.empty else []
    day = start
    while day <= end:
        if day.weekday() != 5 and day not in present:  # Saturday has no data
            frame = fetch_day(session, symbol, day, delay=delay)
            if not frame.empty:
                frames.append(frame)
                present.add(day)
            if on_day is not None:
                on_day(pd.concat(frames).sort_index())
        day += timedelta(days=1)
    out = pd.concat([f for f in frames if not f.empty]).sort_index() if frames else pd.DataFrame()
    return out[~out.index.duplicated(keep="last")] if not out.empty else out


def check_scale(frame: pd.DataFrame, reference_close: float, tolerance: float = 0.05) -> None:
    """Fail loudly if the divisor is wrong: last mid close must be near a reference close."""
    last = float(frame["close"].iloc[-1])
    if abs(last / reference_close - 1) > tolerance:
        raise ValueError(f"scale check failed: archive {last} vs reference {reference_close}")


def load_archive(symbol: str, year: int) -> pd.DataFrame:
    path = archive_path(symbol, year)
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()


def save_archive(frame: pd.DataFrame, symbol: str, year: int) -> Path:
    path = archive_path(symbol, year)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, compression="zstd")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("semboller", nargs="+", choices=sorted(POINT_DIVISOR))
    parser.add_argument("--yillar", nargs="+", type=int, required=True)
    args = parser.parse_args(argv)
    session = requests.Session()
    for symbol in args.semboller:
        for year in args.yillar:
            existing = load_archive(symbol, year)
            frame = fetch_year(
                symbol,
                year,
                session=session,
                existing=existing,
                on_day=lambda current, s=symbol, y=year: save_archive(current, s, y),
            )
            if frame.empty:
                print(f"{symbol} {year}: veri yok")
                continue
            path = save_archive(frame, symbol, year)
            print(f"{symbol} {year}: {len(frame)} bar, medyan spread {frame['spread'].median():.5f} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
