"""Point-in-time (PIT) index membership and entry-signal filtering.

Historical membership files are intentionally kept outside the current static
universe.  This module reads Argon's compact CSVs and filters *new entries*
only; an already-open position is never force-closed merely because its symbol
leaves an index.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BIST = ROOT / "data" / "T11_bist30.csv"
DEFAULT_BIST_ONCE = ROOT / "data" / "T11b_bist30_2015_2019.csv"  # T11b: 2015-2019 lists from Borsa Istanbul notices
# Old BIST codes in the 2015-2019 notices that trade under a new code today (same company; data layer uses the new one).
BIST_RENAMES = {"KOZAL": "TRALT", "KOZAA": "TRMET"}
DEFAULT_ABD = ROOT / "data" / "T11_abd25.csv"
DEFAULT_SYMBOLS = ROOT / "data" / "evren_pit_semboller.csv"
LOGGER = logging.getLogger(__name__)


def _utc(value: object) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    return stamp.tz_localize("UTC") if stamp.tz is None else stamp.tz_convert("UTC")


def normalize_symbol(symbol: object, market: str) -> str:
    """Map source notation to the same filenames/tickers used by the data layer."""
    value = str(symbol).strip().upper().replace(".", "-")
    if market == "BIST30":
        value = BIST_RENAMES.get(value, value)
    if market == "BIST30" and value and not value.endswith(".IS"):
        return f"{value}.IS"
    return value


@dataclass(frozen=True)
class PITUniverse:
    """Membership snapshots. BIST has period starts; ABD has calendar years."""

    bist: tuple[tuple[pd.Timestamp, frozenset[str]], ...] = ()
    abd: tuple[tuple[int, frozenset[str]], ...] = ()

    def members(self, market: str, date: object) -> frozenset[str] | None:
        """Return the known membership set, or None when PIT has no coverage."""
        if market == "BIST30":
            stamp = _utc(date)
            snapshots = [symbols for start, symbols in self.bist if start <= stamp]
            return snapshots[-1] if snapshots else None
        if market == "ABD25":
            year = _utc(date).year
            snapshots = [symbols for start, symbols in self.abd if start <= year]
            return snapshots[-1] if snapshots else None
        return None

    def all_symbols(self, market: str | None = None) -> set[str]:
        snapshots = self.bist if market in (None, "BIST30") else ()
        result = {symbol for _, values in snapshots for symbol in values}
        snapshots = self.abd if market in (None, "ABD25") else ()
        return result | {symbol for _, values in snapshots for symbol in values}


def _bist_snapshots(*paths: Path) -> tuple[tuple[pd.Timestamp, frozenset[str]], ...]:
    tables = [pd.read_csv(path, dtype=str, comment="#").fillna("") for path in paths if path.exists()]
    if not tables:
        return ()
    table = pd.concat(tables, ignore_index=True)
    required = {"donem_baslangic", "hisse_kodu"}
    missing = required.difference(table.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    output, previous = [], None
    for start, group in table.groupby("donem_baslangic", sort=True):
        symbols = {normalize_symbol(value, "BIST30") for value in group["hisse_kodu"] if value and value.lower() != "bulunamadi"}
        stamp = _utc(start)
        if not symbols:
            if previous is None:
                LOGGER.warning("PIT BIST %s bulunamadi; onceki evren yok", start)
                continue
            LOGGER.warning("PIT BIST %s bulunamadi; onceki gecerli liste tasindi", start)
            symbols = set(previous)
        previous = frozenset(symbols)
        output.append((stamp, previous))
    return tuple(output)


def _abd_snapshots(path: Path) -> tuple[tuple[int, frozenset[str]], ...]:
    if not path.exists():
        return ()
    table = pd.read_csv(path, dtype=str).fillna("")
    required = {"yil", "ticker"}
    missing = required.difference(table.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    output, previous = [], None
    for year, group in table.groupby("yil", sort=True):
        symbols = {normalize_symbol(value, "ABD25") for value in group["ticker"] if value and value.lower() != "bulunamadi"}
        if not symbols:
            if previous is None:
                LOGGER.warning("PIT ABD %s bulunamadi; onceki evren yok", year)
                continue
            LOGGER.warning("PIT ABD %s bulunamadi; onceki gecerli liste tasindi", year)
            symbols = set(previous)
        previous = frozenset(symbols)
        output.append((int(year), previous))
    return tuple(output)


def load_pit_universe(
    bist_path: Path = DEFAULT_BIST, abd_path: Path = DEFAULT_ABD, bist_early_path: Path | None = None
) -> PITUniverse:
    """Load whichever historical lists are available; no file means no coverage.

    The default BIST list (2020+) is joined with the T11b 2015-2019 list; a custom ``bist_path`` gets it only when asked."""
    if bist_early_path is None and bist_path == DEFAULT_BIST:
        bist_early_path = DEFAULT_BIST_ONCE
    bist_paths = (bist_path,) if bist_early_path is None else (bist_early_path, bist_path)
    return PITUniverse(_bist_snapshots(*bist_paths), _abd_snapshots(abd_path))


def filter_entry_signals(signals: dict[str, pd.DataFrame], universe: PITUniverse | None, market: str) -> dict[str, pd.DataFrame]:
    """Mask entry bars outside PIT membership, preserving all exit columns verbatim."""
    if universe is None or market not in {"BIST30", "ABD25"}:
        return signals
    filtered: dict[str, pd.DataFrame] = {}
    for symbol, frame in signals.items():
        memberships = [universe.members(market, date) for date in frame.index]
        # No historical coverage is deliberately non-destructive: it gives the
        # user the old result with an explicit warning instead of a false empty run.
        if all(members is None for members in memberships):
            LOGGER.warning("PIT %s icin %s tarihinde kapsama yok; girisler degismedi", market, symbol)
            filtered[symbol] = frame
            continue
        allowed = pd.Series([members is None or symbol in members for members in memberships], index=frame.index)
        copy = frame.copy(deep=False)
        copy["entry"] = frame["entry"].astype(bool) & allowed
        filtered[symbol] = copy
    return filtered


def write_extra_symbols(universe: PITUniverse, static_universe: Path, output: Path = DEFAULT_SYMBOLS) -> pd.DataFrame:
    """Write PIT-only BIST/ABD symbols so fetch.py can archive their daily bars."""
    current = pd.read_csv(static_universe, dtype=str).fillna("")
    known = set(current["sembol"])
    rows = []
    for market in ("BIST30", "ABD25"):
        for symbol in sorted(universe.all_symbols(market).difference(known)):
            rows.append({"sembol": symbol, "piyasa": market, "kaynak": "yfinance", "not": "PIT tarihsel evren"})
    table = pd.DataFrame(rows, columns=["sembol", "piyasa", "kaynak", "not"])
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False)
    return table


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bist", type=Path, default=DEFAULT_BIST)
    parser.add_argument("--abd", type=Path, default=DEFAULT_ABD)
    parser.add_argument("--evren", type=Path, default=ROOT / "data" / "evren.csv")
    parser.add_argument("--cikti", type=Path, default=DEFAULT_SYMBOLS)
    args = parser.parse_args()
    universe = load_pit_universe(args.bist, args.abd)
    table = write_extra_symbols(universe, args.evren, args.cikti)
    print(f"{len(table)} PIT ek sembol yazildi: {args.cikti}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
