"""Actions'ta üç gerçek adres için sıfır gecikme/maliyet gölge sağlaması."""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from copytrade.golge import saglama
from copytrade.kapi import CandleCache, account_history
from copytrade.olcut import perp_fills
from copytrade.tarama import PublicClient


def run(addresses: list[str], days: int = 30) -> list[dict]:
    client, now = PublicClient(), datetime.now(UTC)
    start = int((now - timedelta(days=days)).timestamp() * 1000)
    end = int(now.timestamp() * 1000)
    cache = CandleCache(client, start, end)
    report = []
    for address in addresses:
        fills = perp_fills(client.fills(address, start))
        portfolio = client.portfolio(address)
        account = account_history(portfolio)
        if account is None or account.empty:
            report.append({"adres": address, "durum": "hesap_gecmisi_yok"})
            continue
        out = saglama(fills, cache.for_fills(fills), account, start, end)
        report.append({"adres": address, "durum": "tamam", "dolum": len(fills), "net": out["net"],
                       "eksik": out["missing"]})
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adresler", required=True, help="virgülle ayrılmış, en az üç public adres")
    parser.add_argument("--output", default="golge_saglama.json")
    args = parser.parse_args()
    addresses = [item.strip().lower() for item in args.adresler.split(",") if item.strip()]
    if len(addresses) < 3:
        raise SystemExit("en az üç adres gerekli")
    report = run(addresses)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if any(item["durum"] != "tamam" or item["eksik"] for item in report):
        raise SystemExit("gölge sağlama tamamlanmadı")


if __name__ == "__main__":
    main()
