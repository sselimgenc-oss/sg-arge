"""Download and archive normalized OHLCV bars for the configured universe."""

from __future__ import annotations

import argparse
import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
UNIVERSE_PATH = DATA_DIR / "evren.csv"
MANIFEST_PATH = DATA_DIR / "MANIFEST.csv"
QUALITY_PATH = ROOT / "results" / "veri_kalitesi_1h.md"
BINANCE_KLINES_URL = "https://data-api.binance.vision/api/v3/klines"
BINANCE_START = pd.Timestamp("2017-01-01", tz="UTC")
DAILY_START = "2015-01-01"
REQUIRED_UNIVERSE_COLUMNS = {"sembol", "piyasa", "kaynak", "not"}
OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]
INTERVALS = ("1d", "1h", "30m", "15m", "5m", "1m")
SUBHOURLY = ("30m", "15m", "5m", "1m")  # Binance only; archives are not committed (large)


def archive_dir(interval: str) -> Path:
    return DATA_DIR / {"1d": "daily", "1h": "hourly"}.get(interval, interval)


@dataclass(frozen=True)
class Asset:
    symbol: str
    market: str
    source: str

    @property
    def filename(self) -> str:
        safe = self.symbol.replace("/", "_").replace("=", "_")
        return f"{safe}.parquet"


def load_universe(path: Path = UNIVERSE_PATH) -> list[Asset]:
    table = pd.read_csv(path, dtype=str).fillna("")
    missing = REQUIRED_UNIVERSE_COLUMNS.difference(table.columns)
    if missing:
        raise ValueError(f"evren.csv missing columns: {sorted(missing)}")
    if table["sembol"].duplicated().any():
        duplicate = table.loc[table["sembol"].duplicated(), "sembol"].tolist()
        raise ValueError(f"duplicate universe symbols: {duplicate}")
    assets = [
        Asset(row.sembol.strip(), row.piyasa.strip(), row.kaynak.strip().lower())
        for row in table.itertuples(index=False)
    ]
    unsupported = sorted({asset.source for asset in assets} - {"yfinance", "binance"})
    if unsupported:
        raise ValueError(f"unsupported sources: {unsupported}")
    return assets


def update_universe_notes(
    successful: set[str],
    failures: dict[str, str],
    path: Path = UNIVERSE_PATH,
) -> None:
    """Keep leader notes while reflecting the latest per-symbol fetch state."""

    table = pd.read_csv(path, dtype=str).fillna("")
    for index, row in table.iterrows():
        symbol = row["sembol"]
        retained = [
            part.strip()
            for part in row["not"].split(";")
            if part.strip() and not part.strip().lower().startswith("eksik:")
        ]
        if symbol in failures:
            reason = " ".join(failures[symbol].split())[:200]
            retained.append(f"eksik: {reason}")
        elif symbol not in successful:
            continue
        table.at[index, "not"] = "; ".join(retained)
    table.to_csv(path, index=False)


def _utc_index(index: pd.Index) -> pd.DatetimeIndex:
    timestamps = pd.DatetimeIndex(pd.to_datetime(index))
    if timestamps.tz is None:
        return timestamps.tz_localize("UTC")
    return timestamps.tz_convert("UTC")


def normalize_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=OHLCV_COLUMNS, index=pd.DatetimeIndex([], tz="UTC"))
    clean = frame.copy()
    if isinstance(clean.columns, pd.MultiIndex):
        clean.columns = clean.columns.get_level_values(0)
    clean.columns = [str(column).strip().lower().replace(" ", "_") for column in clean.columns]
    if "adj_close" in clean.columns and "close" not in clean.columns:
        clean["close"] = clean["adj_close"]
    missing = set(OHLCV_COLUMNS).difference(clean.columns)
    if missing:
        raise ValueError(f"download missing OHLCV columns: {sorted(missing)}")
    clean = clean.loc[:, OHLCV_COLUMNS]
    clean.index = _utc_index(clean.index)
    clean.index.name = "timestamp"
    clean = clean.apply(pd.to_numeric, errors="coerce")
    clean = clean.dropna(subset=["open", "high", "low", "close"])
    return clean.loc[~clean.index.duplicated(keep="last")].sort_index()


def fetch_yfinance(asset: Asset, interval: str) -> pd.DataFrame:
    options: dict[str, object] = {
        "tickers": asset.symbol,
        "interval": interval,
        "auto_adjust": True,
        "actions": False,
        "progress": False,
        "threads": False,
    }
    if interval == "1h":
        options["period"] = "730d"
    else:
        options["start"] = DAILY_START
    return normalize_ohlcv(yf.download(**options))


def _binance_rows_to_frame(rows: list[list[object]]) -> pd.DataFrame:
    if not rows:
        return normalize_ohlcv(pd.DataFrame())
    frame = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_base",
            "taker_quote",
            "ignore",
        ],
    )
    frame.index = pd.to_datetime(frame.pop("open_time"), unit="ms", utc=True)
    return normalize_ohlcv(frame)


def fetch_binance(
    asset: Asset,
    interval: str,
    *,
    start: pd.Timestamp | None = None,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    client = session or requests.Session()
    cursor = max(start or BINANCE_START, BINANCE_START)
    end = pd.Timestamp.now(tz="UTC")
    pages: list[pd.DataFrame] = []
    while cursor < end:
        response = client.get(
            BINANCE_KLINES_URL,
            params={
                "symbol": asset.symbol,
                "interval": interval,
                "startTime": int(cursor.timestamp() * 1000),
                "endTime": int(end.timestamp() * 1000),
                "limit": 1000,
            },
            timeout=30,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            break
        page = _binance_rows_to_frame(rows)
        pages.append(page)
        next_cursor = page.index[-1] + pd.Timedelta(1, unit="ms")
        if next_cursor <= cursor:
            raise RuntimeError(f"Binance pagination did not advance for {asset.symbol}")
        cursor = next_cursor
        if len(rows) < 1000:
            break
        time.sleep(0.05)
    if not pages:
        return normalize_ohlcv(pd.DataFrame())
    return normalize_ohlcv(pd.concat(pages))


def merge_archive(existing: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
    return normalize_ohlcv(pd.concat([existing, incoming]))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_parquet_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_parquet(temporary, index=True, compression="zstd")
    temporary.replace(path)


def _read_archive(path: Path) -> pd.DataFrame:
    if not path.exists():
        return normalize_ohlcv(pd.DataFrame())
    return normalize_ohlcv(pd.read_parquet(path))


def _manifest_row(
    asset: Asset,
    interval: str,
    path: Path,
    frame: pd.DataFrame | None,
    *,
    status: str,
    error: str = "",
) -> dict[str, object]:
    return {
        "symbol": asset.symbol,
        "market": asset.market,
        "interval": interval,
        "source": asset.source,
        "first_timestamp": "" if frame is None or frame.empty else frame.index[0].isoformat(),
        "last_timestamp": "" if frame is None or frame.empty else frame.index[-1].isoformat(),
        "rows": 0 if frame is None else len(frame),
        "bytes": path.stat().st_size if path.exists() else 0,
        "sha256": _sha256(path) if path.exists() else "",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "error": error,
    }


def update_manifest(rows: Iterable[dict[str, object]], path: Path = MANIFEST_PATH) -> None:
    incoming = pd.DataFrame(rows)
    if path.exists():
        current = pd.read_csv(path, dtype=str).fillna("")
        keys = set(zip(incoming["symbol"], incoming["interval"]))
        current = current[
            ~current.apply(lambda row: (row["symbol"], row["interval"]) in keys, axis=1)
        ]
        incoming = pd.concat([current, incoming], ignore_index=True)
    incoming["bytes"] = pd.to_numeric(incoming["bytes"], errors="coerce").fillna(0).astype(int)
    incoming["archive_total_bytes"] = incoming.groupby("interval")["bytes"].transform("sum")
    incoming = incoming.sort_values(["interval", "market", "symbol"])
    incoming.to_csv(path, index=False)


def quality_metrics(frame: pd.DataFrame, asset: Asset) -> dict[str, int]:
    duplicate = int(frame.index.duplicated().sum())
    zero_volume = int((frame["volume"] <= 0).sum()) if not frame.empty else 0
    missing = 0
    outside_session = 0
    if not frame.empty and asset.source == "binance":
        expected = pd.date_range(frame.index[0], frame.index[-1], freq="1h", tz="UTC")
        missing = len(expected.difference(frame.index))
    if not frame.empty and asset.market.upper() == "BIST30":
        local = frame.index.tz_convert("Europe/Istanbul")
        minute = local.hour * 60 + local.minute
        outside_session = int(((minute < 10 * 60) | (minute >= 18 * 60)).sum())
    return {
        "duplicates": duplicate,
        "missing_bars": missing,
        "zero_volume": zero_volume,
        "outside_session": outside_session,
    }


def write_quality_report(records: list[dict[str, object]], path: Path = QUALITY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Saatlik veri kalite raporu",
        "",
        f"Üretim zamanı (UTC): {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Toplam Parquet boyutu: {sum(int(record['bytes']) for record in records)} byte.",
        "",
        "Eksik bar yalnız kesintisiz işlem gören Binance serilerinde saatlik takvime göre ölçülür. "
        "BIST seans dışı kontrolü bar-başı etiketiyle 10:00–18:00 Europe/Istanbul aralığını kullanır.",
        "",
        "| Sembol | Piyasa | Satır | Eksik bar | Sıfır hacim | Seans dışı | Tekrar |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for record in sorted(records, key=lambda item: (str(item["market"]), str(item["symbol"]))):
        lines.append(
            "| {symbol} | {market} | {rows} | {missing_bars} | {zero_volume} | "
            "{outside_session} | {duplicates} |".format(**record)
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch_asset(
    asset: Asset, interval: str, *, append: bool, start_override: pd.Timestamp | None = None
) -> tuple[Path, pd.DataFrame]:
    path = archive_dir(interval) / asset.filename
    existing = _read_archive(path) if append else normalize_ohlcv(pd.DataFrame())
    if asset.source == "binance":
        start = existing.index[-1] + pd.Timedelta(1, unit="ms") if not existing.empty else start_override
        incoming = fetch_binance(asset, interval, start=start)
    else:
        incoming = fetch_yfinance(asset, interval)
    if incoming.empty:
        raise RuntimeError("source returned no bars")
    combined = merge_archive(existing, incoming) if append else incoming
    _write_parquet_atomic(combined, path)
    return path, combined


def run(
    interval: str, *, append: bool, allow_partial: bool = False, start: pd.Timestamp | None = None
) -> int:
    manifest_rows: list[dict[str, object]] = []
    quality_rows: list[dict[str, object]] = []
    successful: set[str] = set()
    failure_reasons: dict[str, str] = {}
    failures = 0
    for asset in load_universe():
        if interval in SUBHOURLY and asset.source != "binance":
            continue  # sub-hourly bars exist only for crypto (EVRENSEL_KURALLAR B)
        path = archive_dir(interval) / asset.filename
        try:
            path, frame = fetch_asset(asset, interval, append=append, start_override=start)
            manifest_rows.append(
                _manifest_row(asset, interval, path, frame, status="ok")
            )
            successful.add(asset.symbol)
            if interval == "1h":
                quality_rows.append(
                    {
                        "symbol": asset.symbol,
                        "market": asset.market,
                        "rows": len(frame),
                        "bytes": path.stat().st_size,
                        **quality_metrics(frame, asset),
                    }
                )
            print(f"OK {asset.symbol}: {len(frame)} rows")
        except Exception as exc:  # continue the universe and record each failure
            failures += 1
            failure_reasons[asset.symbol] = str(exc)
            retained = _read_archive(path) if path.exists() else None
            manifest_rows.append(
                _manifest_row(
                    asset,
                    interval,
                    path,
                    retained,
                    status="error" if retained is not None else "missing",
                    error=str(exc),
                )
            )
            print(f"ERROR {asset.symbol}: {exc}")
    if interval not in SUBHOURLY:  # sub-hourly runs only cover crypto: do not mark other symbols missing
        update_universe_notes(successful, failure_reasons)
    update_manifest(manifest_rows)
    if interval == "1h":
        write_quality_report(quality_rows)
    return 1 if failures and not allow_partial else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", choices=INTERVALS, required=True)
    parser.add_argument(
        "--baslangic",
        help="ISO start date for Binance downloads (default 2017-01-01); the scan only needs 2020-01-01 for sub-hourly bars",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="merge downloads into an existing archive without duplicate timestamps",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="record per-symbol failures but return success when at least part of the universe downloads",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        run(
            arguments.interval,
            append=arguments.append,
            allow_partial=arguments.allow_partial,
            start=pd.Timestamp(arguments.baslangic, tz="UTC") if arguments.baslangic else None,
        )
    )
