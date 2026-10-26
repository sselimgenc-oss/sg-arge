"""Rank completed U7 candidates with the shared TEST_YAPISI Adım 3 method.

Only U7 v2 ``Geçti`` rows with at least ten active OOS weeks participate.
The decision remains in ``huni_ozet.csv``; this script only produces the
volatility-normalised, bootstrap-ranked comparison and copy clusters.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from backtests.asama2b import deflated_sharpe_ratio
from backtests.tv2_sirala import (
    TOHUM,
    alt_sinir,
    etkin_deneme_sayisi,
    kumele,
    olcekle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "u7"


def _getiri(row: pd.Series) -> pd.Series:
    """Load a group's saved OOS daily return series for one U7 variant."""
    filename = str(row["varyant"]).replace(":", "_") + ".csv"
    path = OUT / str(row["grup"]) / "getiriler" / filename
    table = pd.read_csv(path, index_col=0, parse_dates=True)
    column = "getiri" if "getiri" in table else "net_getiri"
    series = pd.to_numeric(table[column], errors="coerce")
    series.index = pd.to_datetime(series.index, utc=True)
    return series


def build(results_dir: Path = OUT) -> pd.DataFrame:
    table = pd.read_csv(results_dir / "huni_ozet.csv")
    passed = table[(table["karar_adim2"] == "Geçti") & (table["oos_islem_hafta"] >= 10)].copy()
    rng = np.random.default_rng(TOHUM)
    records: list[dict[str, object]] = []
    series_by_id: dict[str, pd.Series] = {}
    for _, row in passed.iterrows():
        key = str(row["varyant"])
        annualization = 365 if row.get("piyasa") == "KRIPTO25" else 252
        returns = olcekle(_getiri(row), annualization).fillna(0.0)
        series_by_id[key] = returns
        weekly = (1 + returns).resample("W").prod() - 1
        records.append({
            "varyant": key,
            "grup": row["grup"],
            "piyasa": row.get("piyasa"),
            "tf": row.get("tf"),
            "sinama_hafta": len(weekly),
            "sinama_islem": row.get("oos_islem"),
            "olcekli_yillik_getiri": float(weekly.mean() * 52) if len(weekly) else np.nan,
            "alt_sinir_haftalik_p10": alt_sinir(weekly, rng),
            "oos_net_1x": row.get("oos_net_1x"),
            "oos_sharpe": row.get("oos_sharpe"),
        })
    n_eff = etkin_deneme_sayisi(series_by_id)
    trials = max(1, int(np.ceil(n_eff))) if np.isfinite(n_eff) else 1
    for record in records:
        record["n_eff"] = n_eff
        record["dsr"] = deflated_sharpe_ratio(series_by_id[str(record["varyant"])], trials)
    ranked = pd.DataFrame(records).sort_values(
        "alt_sinir_haftalik_p10", ascending=False, na_position="last", kind="stable"
    )
    clusters = kumele(series_by_id, list(ranked["varyant"]))
    ranked["kume_temsilcisi"] = ranked["varyant"].map(clusters)
    ranked["temsilci"] = ranked["varyant"] == ranked["kume_temsilcisi"]
    ranked.insert(0, "sira", range(1, len(ranked) + 1))
    return ranked


def main() -> None:
    ranked = build()
    ranked.to_csv(OUT / "siralama.csv", index=False)
    print(f"{len(ranked)} aday, {ranked['temsilci'].sum()} temsilci; {OUT / 'siralama.csv'}")


if __name__ == "__main__":
    main()
