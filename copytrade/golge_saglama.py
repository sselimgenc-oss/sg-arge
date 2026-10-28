"""Actions'ta üç gerçek adres için sıfır gecikme/maliyet gölge sağlaması."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from datetime import UTC, datetime, timedelta
from pathlib import Path

from copytrade.golge import saglama
from copytrade.defter import capital_scale
from copytrade.kapi import CandleCache, account_history
from copytrade.olcut import perp_fills
from copytrade.tarama import PublicClient


def pencere_ici_dolumlar(fills: list[dict]) -> list[dict]:
    """Pencere öncesinden taşınan pozisyonun kapanışını sağlama kıyasından çıkarır.

    Defter, bu pozisyonu bilinçli olarak sıfırdan başlatır; trader'ın eski
    girişe ait ``closedPnl``'ini onunla karşılaştırmak geçerli bir sağlama değildir.
    Pencere içinde sıfırdan açılan pozisyonun pencere sonunda açık kalan kısmı
    ise atılmaz: önceki kısmi/tam kapanışların gerçekleşmiş PnL'i geçerlidir.
    """
    blocked: set[str] = set()
    seen: set[str] = set()
    buffers: dict[str, list[dict]] = {}
    out: list[dict] = []
    for row in sorted(fills, key=lambda item: int(item["time"])):
        coin = str(row["coin"])
        # API'nin ondalık miktarları ikilik kayan noktayla toplandığında sıfır
        # dönüşü kaçabilir; döngü sınırı için kaynak miktarını aynen kullan.
        before = Decimal(str(row.get("startPosition", 0)))
        signed = (-1 if row["side"] in {"A", "Sell", "sell"} else 1) * Decimal(str(row["sz"]))
        after = before + signed
        if coin in blocked or (coin not in seen and before != 0):
            blocked.add(coin)
            if after == 0:
                blocked.discard(coin)
                seen.add(coin)
            elif before * after < 0:
                blocked.discard(coin)
                seen.add(coin)
                buffers[coin] = [dict(row, sz=str(abs(after)), startPosition="0", closedPnl="0")]
            continue
        seen.add(coin)
        if before * after < 0:
            buffers.setdefault(coin, []).append(dict(row, sz=str(abs(before))))
            out.extend(buffers.pop(coin))
            buffers[coin] = [dict(row, sz=str(abs(after)), startPosition="0", closedPnl="0")]
        else:
            buffers.setdefault(coin, []).append(row)
        if after == 0:
            out.extend(buffers.pop(coin))
    # Açık kalan pencere-içi pozisyonlar, gerçekleşmiş kısmi kapanışları
    # taşıyabilir. Sağlama ``realized`` kıyasladığı için bunlar dahil edilir.
    for coin in sorted(buffers):
        out.extend(buffers[coin])
    return sorted(out, key=lambda item: int(item["time"]))


def pozisyon_dokumu(fills: list[dict]) -> dict[str, dict]:
    """Sağlama ayıklamasının coin bazında pozisyon tanısı (API ondalıklarıyla)."""
    out: dict[str, dict] = {}
    for row in sorted(fills, key=lambda item: int(item["time"])):
        coin = str(row["coin"])
        before = Decimal(str(row.get("startPosition", 0)))
        signed = (-1 if row["side"] in {"A", "Sell", "sell"} else 1) * Decimal(str(row["sz"]))
        after = before + signed
        item = out.setdefault(coin, {"son_pozisyon": "0", "en_kucuk_mutlak_pozisyon": None, "sifira_donus_sayisi": 0})
        item["son_pozisyon"] = str(after)
        magnitude = abs(after)
        if item["en_kucuk_mutlak_pozisyon"] is None or magnitude < Decimal(item["en_kucuk_mutlak_pozisyon"]):
            item["en_kucuk_mutlak_pozisyon"] = str(magnitude)
        if after == 0:
            item["sifira_donus_sayisi"] += 1
    return out


def _summary(fills: list[dict], candles: dict[str, list[dict]], account, start: int, end: int,
             fixed_scale: bool = False) -> dict:
    used_account = 1.0 if fixed_scale else account
    out = saglama(fills, candles, used_account, start, end)
    scale = capital_scale(used_account)
    trader = sum(float(row.get("closedPnl", 0)) * scale(int(row["time"])) for row in fills)
    shadow = float(out["realized"])
    diff = shadow - trader
    return {"dolum": len(fills), "trader_gerceklesen": trader, "golge_gerceklesen": shadow,
            "fark": diff, "goreli_hata": abs(diff) / abs(trader) if trader else None, "eksik": out["missing"]}


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
        all_candles = cache.for_fills(fills)
        full = _summary(fills, all_candles, account, start, end)
        inside = pencere_ici_dolumlar(fills)
        inside_candles = {coin: all_candles[coin] for coin in {x["coin"] for x in inside}}
        closed_inside = _summary(inside, inside_candles, account, start, end)
        fixed_inside = _summary(inside, inside_candles, account, start, end, fixed_scale=True)
        coins = {}
        diagnostics = pozisyon_dokumu(fills)
        for coin in sorted({str(row["coin"]) for row in fills}):
            rows = [row for row in fills if str(row["coin"]) == coin]
            coin_inside = pencere_ici_dolumlar(rows)
            coin_inside_candles = {coin: all_candles[coin]} if coin_inside else {}
            coins[coin] = {**_summary(rows, {coin: all_candles[coin]}, account, start, end),
                           "ilk_start_position": float(rows[0].get("startPosition", 0)),
                           "pencere_oncesi_acik": float(rows[0].get("startPosition", 0)) != 0,
                           **diagnostics[coin],
                           "sabit_olcekli_pencere_ici": _summary(coin_inside, coin_inside_candles, account, start, end, fixed_scale=True)}
        report.append({"adres": address, "durum": "tamam", "tum_dolumlar": full,
                       "pencerede_acilip_kapanan": closed_inside, "sabit_olcekli_pencere_ici": fixed_inside,
                       "coinler": coins})
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
    if any(item["durum"] != "tamam" or item["tum_dolumlar"]["eksik"] for item in report):
        raise SystemExit("gölge sağlama tamamlanmadı")


if __name__ == "__main__":
    main()
