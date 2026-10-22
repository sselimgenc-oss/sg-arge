#!/usr/bin/env python3
"""T22 parity check: Composer ``gecis`` cards against the symphony's own published backtest series.

Composer's page carries the daily value series of the symphony (``backtestData``). Our ``rotasyon`` engine, run with
zero cost and close fills (Composer trades at the close), must reproduce its daily returns. Needs network access and the
daily archive (``python data/fetch.py --interval 1d --rotasyon``). Writes ``results/rotasyon_parite.md``.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import tarama  # noqa: E402
from engine import rotasyon  # noqa: E402

START = pd.Timestamp("2016-06-01", tz="UTC")  # after the 200-day warm-up of the 2015 archive start


def composer_series(url: str) -> pd.Series:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(request, timeout=60).read().decode("utf-8", "ignore")  # noqa: S310
    blob = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1)
    data = json.loads(blob)["props"]["pageProps"]["backtestData"]["series"][0]["data"]
    return pd.Series([v for _, v in data], index=pd.to_datetime([t for t, _ in data], unit="ms").tz_localize("UTC"))


def main() -> int:
    rows = []
    for path in sorted((ROOT / "docs" / "spec").glob("*.yaml")):
        card = yaml.safe_load(path.read_text(encoding="utf-8"))
        block = card.get("rotasyon") or {}
        if block.get("kip") != "gecis" or "composer.trade" not in card["kaynak"]["url"]:
            continue
        try:
            theirs = composer_series(card["kaynak"]["url"])
            frames = tarama.load_fixed_symbols(rotasyon.needed_symbols(card), ROOT / "data" / "daily")
            weights = rotasyon.agirliklar(card, frames)
            ours = rotasyon.simule(frames, weights, start=START, end=theirs.index[-1], cost_rate=0.0, fill_at_close=True).equity
        except Exception as exc:  # noqa: BLE001 - one card must not stop the table
            rows.append(f"| {card['id']} | - | - | - | {type(exc).__name__}: {str(exc)[:60]} |")
            continue
        joined = pd.concat([theirs.pct_change(), ours.pct_change()], axis=1, keys=["c", "o"], sort=True).dropna()
        joined = joined[joined.index >= START]
        diff = (joined["c"] - joined["o"]).abs()
        rows.append(f"| {card['id']} | {len(joined)} | {joined.corr().iloc[0, 1]:.5f} | {diff.max():.4f} | |")
    lines = [
        "# Composer parite kontrolu (T22)", "",
        "Kart `rotasyon` kural agaci, Composer sayfasindaki kendi backtest serisinin (`backtestData`) gunluk getirileriyle karsilastirildi: "
        f"maliyet 0, kapanis dolumu (Composer kapanista dolar), {START.date()} sonrasi.", "",
        "| Kart | Gun | Korelasyon | En buyuk gunluk fark | Not |", "|---|---:|---:|---:|---|", *rows, "",
        "Sapma: A4/O2-025/O2-027 kartlarinda en buyuk gunluk fark %0,05 (fiyat duzeltmesi yuvarlamasi); M017 ve O2-028 daha buyuk tek gun farklari verir. O2-026'da 2023-01-03..05 ve 2023-01-27, 2023-03-07 (5 gun) varlik secimi Composer ile ayrisir (SOXL/TECL/SQQQ arasi gecis); sebebi bulunamadi (KMLM/SVIX ilk aylari ya da RSI esitlik/duzeltme farki), diger ~1130 gun birebir.", "",
    ]
    (ROOT / "results" / "rotasyon_parite.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
