#!/usr/bin/env python3
"""T27: paper parity. Replay the daily run bar by bar into a (temporary) ledger and compare it with one backtest of the same period.

If the paper run is the backtest, the ledger rebuilt day by day (each day only knowing that day's data) holds exactly the trades of
a single backtest over the whole period: same entry and exit dates, prices, quantities and net P&L, and the same open book at the end.
Any difference means look-ahead, a rule copy that drifted, or a ledger bug. ``--adim k`` replays every k-th day (the final day always);
the ledger is the same because every run recomputes the whole history from the paper start and only appends new keys.

    python paper/parite.py --baslangic 2025-01-01 --adim 5
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper import gunluk  # noqa: E402

TOLERANCE = 1e-6


def tekrar_oyna(
    portfoy: gunluk.Portfoy, veri: gunluk.Veri, defter: Path, *, adim: int = 1, git_sha: str = "parite", gunler: list[pd.Timestamp] | None = None,
) -> list[pd.Timestamp]:
    """Run the daily job for every ``adim``-th bar date from the paper start (data cut at that day); returns the days run.

    ``gunler`` replays exactly those days instead (a catch-up day followed by consecutive days keeps long replays cheap)."""
    dates = sorted({d for frames in veri.frames.values() for f in frames.values() for d in f.index if d >= portfoy.baslangic})
    days = list(gunler) if gunler is not None else dates[::adim]
    if gunler is None and dates and days[-1] != dates[-1]:
        days.append(dates[-1])
    for day in days:
        gunluk.calistir(portfoy, veri.kes(day), defter, git_sha=git_sha)
    return days


def defter_islemleri(defter: Path) -> pd.DataFrame:
    """Closed trades rebuilt from the ledger fills (entry -> partials -> exit), numeric."""
    fills = gunluk._read(defter, "dolumlar")  # noqa: SLF001
    if fills.empty:
        return pd.DataFrame(columns=["satir", "sembol", "giris_tarihi", "cikis_tarihi", "giris_fiyati", "cikis_fiyati", "adet", "net"])
    order = {"giris": 0, "kismi": 1, "cikis": 2}
    fills = fills.assign(_o=fills["tip"].map(order)).sort_values(["tarih", "_o"], kind="stable")
    book: dict[tuple[str, str], dict[str, Any]] = {}
    out = []
    for row in fills.to_dict("records"):
        key = (row["satir"], row["sembol"])
        if row["tip"] == "giris":
            book[key] = {"giris": row, "spent": row["adet"] * row["fiyat"], "got": 0.0, "cost": row["maliyet"], "qty_out": 0.0}
        elif key in book:
            b = book[key]
            b["got"] += row["adet"] * row["fiyat"]; b["cost"] += row["maliyet"]; b["qty_out"] += row["adet"]
            if row["tip"] == "cikis":
                entry = b["giris"]
                out.append({"satir": row["satir"], "sembol": row["sembol"], "giris_tarihi": entry["tarih"], "cikis_tarihi": row["tarih"],
                            "giris_fiyati": entry["fiyat"], "cikis_fiyati": row["fiyat"], "adet": entry["adet"], "net": b["got"] - b["spent"] - b["cost"]})
                del book[key]
    return pd.DataFrame(out)


def karsilastir(portfoy: gunluk.Portfoy, veri: gunluk.Veri, defter: Path) -> dict[str, Any]:
    """One backtest per row over the whole period vs the replayed ledger."""
    expected = []
    open_expected = []
    for satir in portfoy.satirlar:
        result, _ = gunluk.kitap(satir, veri, portfoy.baslangic, portfoy.sermaye * satir.agirlik)
        for t in result.trades.to_dict("records"):
            if str(t["exit_reason"]).startswith("end_of_test"):
                continue
            expected.append({"satir": satir.etiket, "sembol": t["symbol"], "giris_tarihi": gunluk._day(t["entry_date"]), "cikis_tarihi": gunluk._day(t["exit_date"]),  # noqa: SLF001
                             "giris_fiyati": t["entry_price"], "cikis_fiyati": None, "adet": t["quantity"], "net": t["net_pnl"]})
        for p in result.open_positions:
            open_expected.append({"satir": satir.etiket, "sembol": p["sembol"], "giris_tarihi": gunluk._day(p["giris_tarihi"]), "giris_fiyati": p["giris_fiyati"], "adet": p["adet"]})  # noqa: SLF001
    want = pd.DataFrame(expected)
    have = defter_islemleri(defter)
    diffs: list[str] = []
    key = ["satir", "sembol", "giris_tarihi"]
    if len(want) != len(have):
        diffs.append(f"islem sayisi: backtest {len(want)} defter {len(have)}")
    merged = want.merge(have, on=key, how="outer", suffixes=("_bt", "_df"), indicator=True) if len(want) or len(have) else pd.DataFrame()
    for row in merged[merged["_merge"] != "both"].to_dict("records") if len(merged) else []:
        diffs.append(f"{row['_merge']}: {row['satir']} {row['sembol']} giris {row['giris_tarihi']}")
    both = merged[merged["_merge"] == "both"] if len(merged) else merged
    for row in both.to_dict("records"):
        for field in ("cikis_tarihi",):
            if row[f"{field}_bt"] != row[f"{field}_df"]:
                diffs.append(f"{row['satir']} {row['sembol']} {row['giris_tarihi']}: {field} {row[field + '_bt']} != {row[field + '_df']}")
        for field in ("giris_fiyati", "adet", "net"):
            a, b = float(row[f"{field}_bt"]), float(row[f"{field}_df"])
            if abs(a - b) > TOLERANCE * max(1.0, abs(a)):
                diffs.append(f"{row['satir']} {row['sembol']} {row['giris_tarihi']}: {field} {a} != {b}")
    snapshot = gunluk._read(defter, "pozisyonlar")  # noqa: SLF001
    last = snapshot[snapshot["tarih"] == snapshot["tarih"].max()] if len(snapshot) else snapshot
    have_open = {(r["satir"], r["sembol"], r["giris_tarihi"]): r for r in last.to_dict("records")}
    want_open = {(r["satir"], r["sembol"], r["giris_tarihi"]): r for r in open_expected}
    for k in sorted(set(want_open) | set(have_open)):
        if k not in want_open or k not in have_open:
            diffs.append(f"acik pozisyon yalniz {'backtestte' if k in want_open else 'defterde'}: {k}")
        elif abs(want_open[k]["adet"] - have_open[k]["adet"]) > TOLERANCE * max(1.0, want_open[k]["adet"]):
            diffs.append(f"acik pozisyon adet: {k}")
    return {"islem_backtest": len(want), "islem_defter": len(have), "acik": len(want_open), "farklar": diffs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfoy", type=Path, default=gunluk.PORTFOLIO_PATH)
    parser.add_argument("--baslangic", help="paper start date (default: portfoy.yaml)")
    parser.add_argument("--adim", type=int, default=1)
    parser.add_argument("--veri-dir", type=Path, default=gunluk.DATA_DIR)
    args = parser.parse_args()
    portfoy = gunluk.yukle_portfoy(args.portfoy)
    if args.baslangic:
        portfoy.baslangic = pd.Timestamp(args.baslangic, tz="UTC")
    veri = gunluk.yukle_veri(portfoy, args.veri_dir)
    with tempfile.TemporaryDirectory() as tmp:
        days = tekrar_oyna(portfoy, veri, Path(tmp), adim=args.adim)
        report = karsilastir(portfoy, veri, Path(tmp))
    print(f"{len(days)} gun oynatildi; backtest {report['islem_backtest']} islem, defter {report['islem_defter']} islem, acik {report['acik']}")
    for line in report["farklar"]:
        print("FARK", line)
    print("PARITE BIREBIR" if not report["farklar"] else f"PARITE BOZUK ({len(report['farklar'])} fark)")
    return 0 if not report["farklar"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
