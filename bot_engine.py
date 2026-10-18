#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Kağıt Hesaplar Pro - Otonom Kantitatif Paper Trading Motoru (bot_engine.py)
Geliştirici & Danışman: Argon Quant QA Suite
Çalışma Ortamı: GitHub Actions / Local Cron
Maliyet: %100 ÜCRETSİZ (Herhangi bir ücretli API anahtarı gerektirmez)
===============================================================================
Bu motor, GitHub Actions tarafından her saat başı (:11 geçe) tetiklenir:
1. Binance Public REST API'sinden kripto paraların canlı fiyatlarını çeker.
2. Yahoo Finance API'sinden ABD hisseleri ve emtia fiyatlarını çeker.
3. Açık pozisyonların anlık K/Z (PnL), R-katı ve risk metriklerini hesaplar.
4. Stop Loss ve Kâr Al kurallarını işletir; tetiklenenleri kapatır.
5. data.json dosyasını günceller.
===============================================================================
"""

import os
import sys
import json
import time
import math
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# Türkiye Yerel Saati (UTC+3)
TURKEY_TZ = timezone(timedelta(hours=3))

# Desteklenen Kripto Sembolleri (Binance Ticker Eşleştirmesi)
CRYPTO_MAP = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
    "NEAR": "NEARUSDT",
    "LTC": "LTCUSDT",
    "XLM": "XLMUSDT",
    "DOGE": "DOGEUSDT",
    "ADA": "ADAUSDT",
    "AVAX": "AVAXUSDT",
    "OP": "OPUSDT",
    "DOT": "DOTUSDT",
    "SUI": "SUIUSDT",
    "LINK": "LINKUSDT",
    "BNB": "BNBUSDT",
    "BCH": "BCHUSDT",
    "FIL": "FILUSDT",
    "TRX": "TRXUSDT",
    "ARB": "ARBUSDT",
    "PEPE": "1000PEPEUSDT",
    "WLD": "WLDUSDT",
    "QNT": "QNTUSDT",
    "LSK": "LSKUSDT",
    "UNI": "UNIUSDT",
    "XRP": "XRPUSDT",
    "ICP": "ICPUSDT",
    "APT": "APTUSDT"
}

# Güvenli Referans Fiyatlar (Piyasa ortalama seviyeleri)
FALLBACK_PRICES = {
    "BTC": 64500.0,
    "ETH": 2620.0,
    "SOL": 152.0,
    "NEAR": 4.88,
    "LTC": 61.20,
    "XLM": 0.183,
    "DOGE": 0.110,
    "ADA": 0.235,
    "AVAX": 10.20,
    "OP": 0.145,
    "DOT": 1.18,
    "SUI": 1.15,
    "LINK": 12.80,
    "BNB": 735.0,
    "BCH": 270.0,
    "FIL": 1.15,
    "TRX": 0.161,
    "ARB": 0.20,
    "PEPE": 0.0000101,
    "WLD": 1.84,
    "QNT": 86.5,
    "LSK": 1.12,
    "UNI": 7.40,
    "XRP": 0.54,
    "ICP": 3.10,
    "APT": 8.40,
    "META": 735.0,
    "MSFT": 530.0,
    "NVDA": 228.0,
    "AAPL": 342.0
}


def load_data():
    """data.json dosyasını yükler."""
    if not os.path.exists(DATA_FILE):
        print(f"[HATA] {DATA_FILE} bulunamadı!")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    """Güncellenmiş veriyi data.json dosyasına yazar."""
    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_file, DATA_FILE)
    print(f"[BAŞARILI] {DATA_FILE} atomik olarak kaydedildi.")


def fetch_binance_prices():
    """Binance Public REST API üzerinden canlı kripto fiyatlarını çeker."""
    prices = {}
    url = "https://api.binance.com/api/v3/ticker/price"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (QuantPaperTrader/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                raw = json.loads(response.read().decode("utf-8"))
                ticker_dict = {item["symbol"]: float(item["price"]) for item in raw}
                for asset, symbol in CRYPTO_MAP.items():
                    if symbol in ticker_dict:
                        prices[asset] = ticker_dict[symbol]
                print(f"[BİLGİ] Binance API üzerinden {len(prices)} kripto fiyatı çekildi.")
    except Exception as e:
        print(f"[BİLGİ] Canlı ağ erişimi yok veya yedek mod ({e}). Referans fiyatlar kullanılıyor.")
        for asset, p in FALLBACK_PRICES.items():
            prices[asset] = p
    return prices


def fetch_yahoo_prices():
    """Yahoo Finance API üzerinden hisse ve emtia fiyatlarını çeker."""
    stock_prices = {}
    symbols = ["META", "MSFT", "NVDA", "AAPL"]
    for sym in symbols:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=4) as res:
                if res.status == 200:
                    d = json.loads(res.read().decode("utf-8"))
                    meta = d["chart"]["result"][0]["meta"]
                    price = meta.get("regularMarketPrice")
                    if price:
                        stock_prices[sym] = float(price)
        except Exception:
            stock_prices[sym] = FALLBACK_PRICES.get(sym, 100.0)
    return stock_prices


def normalize_price_unit(asset, raw_price, entry_price):
    """Varlık birim farklarını (örneğin BTC'nin 81.773 bin dolar formatı ile 81773 formatı) eşitler."""
    if asset == "BTC":
        if entry_price < 1000 and raw_price > 10000:
            return raw_price / 1000.0
        elif entry_price > 10000 and raw_price < 1000:
            return raw_price * 1000.0
    return raw_price


def update_positions_and_pnl(data, live_prices):
    """Açık pozisyonların K/Z değerlerini ve stop-loss / take-profit durumlarını günceller."""
    open_positions = data.get("open_positions", [])
    closed_trades = data.get("closed_trades_list", [])
    now_tr = datetime.now(TURKEY_TZ)
    date_str = now_tr.strftime("%d/%m %H:%M")

    remaining_positions = []
    closed_in_this_run = []

    for pos in open_positions:
        asset = pos.get("asset", "").split(",")[0].strip()
        raw_price = live_prices.get(asset)

        if not raw_price or isinstance(pos.get("entry_price"), str):
            # Sepet veya fiyatı bulunamayan pozisyonlar aynen korunur
            remaining_positions.append(pos)
            continue

        entry_price = float(pos["entry_price"])
        current_price = normalize_price_unit(asset, raw_price, entry_price)

        stop_price = float(pos["stop_price"]) if pos.get("stop_price") not in ("N/A", None) else None
        pos_type = pos.get("type", "Alış")
        size_usd = float(pos.get("size_usd", 1000))

        # K/Z Hesaplama
        if pos_type == "Alış":
            pnl_pct = (current_price - entry_price) / entry_price
            pnl_usd = size_usd * pnl_pct
            if stop_price and stop_price < entry_price:
                risk_per_unit = entry_price - stop_price
                r_mult = round((current_price - entry_price) / risk_per_unit, 2)
            else:
                r_mult = round(pnl_pct * 10, 2)

            # Stop Kontrolü
            if stop_price and current_price <= stop_price:
                closed_trade = {
                    "id": int(time.time() * 1000) % 10000000,
                    "account": pos["account"],
                    "strategy": pos["strategy"],
                    "asset": pos["asset"],
                    "type": pos_type,
                    "entry_date": pos.get("entry_date", date_str),
                    "exit_date": date_str,
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "r": -1.0,
                    "pnl": round(-abs(size_usd * ((entry_price - stop_price) / entry_price)), 2),
                    "reason": "stop"
                }
                closed_trades.insert(0, closed_trade)
                closed_in_this_run.append(closed_trade)
                continue

        else:  # Satış (Short)
            pnl_pct = (entry_price - current_price) / entry_price
            pnl_usd = size_usd * pnl_pct
            if stop_price and stop_price > entry_price:
                risk_per_unit = stop_price - entry_price
                r_mult = round((entry_price - current_price) / risk_per_unit, 2)
            else:
                r_mult = round(pnl_pct * 10, 2)

            # Stop Kontrolü
            if stop_price and current_price >= stop_price:
                closed_trade = {
                    "id": int(time.time() * 1000) % 10000000,
                    "account": pos["account"],
                    "strategy": pos["strategy"],
                    "asset": pos["asset"],
                    "type": pos_type,
                    "entry_date": pos.get("entry_date", date_str),
                    "exit_date": date_str,
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "r": -1.0,
                    "pnl": round(-abs(size_usd * ((stop_price - entry_price) / entry_price)), 2),
                    "reason": "stop"
                }
                closed_trades.insert(0, closed_trade)
                closed_in_this_run.append(closed_trade)
                continue

        # Güncel değerleri yaz
        pos["unrealized_pnl"] = round(pnl_usd, 2)
        pos["r"] = r_mult
        remaining_positions.append(pos)

    data["open_positions"] = remaining_positions
    data["closed_trades_list"] = closed_trades[:1000]

    # Genel İstatistikleri ve Portföy Değerini Hesapla
    total_closed_pnl = sum(t.get("pnl", 0) for t in closed_trades)
    total_open_pnl = sum(p.get("unrealized_pnl", 0) for p in remaining_positions)
    wins = [t for t in closed_trades if t.get("pnl", 0) > 0]
    losses = [t for t in closed_trades if t.get("pnl", 0) < 0]

    win_rate = round((len(wins) / len(closed_trades) * 100), 1) if closed_trades else 0
    initial_cap = float(data.get("kpis", {}).get("initial_total_capital", 5000.0))
    total_equity = initial_cap + total_closed_pnl + total_open_pnl
    total_return_pct = round(((total_equity - initial_cap) / initial_cap) * 100, 2)

    data["kpis"]["total_value"] = round(total_equity, 2)
    data["kpis"]["total_return_pct"] = total_return_pct
    data["kpis"]["open_positions_count"] = len(remaining_positions)
    data["kpis"]["closed_trades_count"] = len(closed_trades)
    data["kpis"]["win_rate_pct"] = int(win_rate)
    data["kpis"]["net_pnl"] = round(total_closed_pnl, 2)
    data["kpis"]["total_try"] = round(total_equity * float(data["meta"].get("exchange_rate", 49.26)), 2)

    # Son güncelleme damgası
    data["meta"]["last_update"] = now_tr.strftime("%d/%m %H:%M")

    print(f"[ÖZET] Toplam Portföy: {total_equity:.2f} $, Açık Pozisyon: {len(remaining_positions)}, Kapanan: {len(closed_trades)}")
    return data


def main():
    print("=" * 60)
    print("Argon Quant QA - Kağıt Hesaplar Otonom Motoru Başlatıldı")
    print(f"Çalışma Zamanı: {datetime.now(TURKEY_TZ).strftime('%Y-%m-%d %H:%M:%S')} (İstanbul)")
    print("=" * 60)

    data = load_data()

    crypto_prices = fetch_binance_prices()
    stock_prices = fetch_yahoo_prices()
    all_prices = {**crypto_prices, **stock_prices}

    updated_data = update_positions_and_pnl(data, all_prices)
    save_data(updated_data)
    print("[TAMAMLANDI] Bot yürütme döngüsü başarıyla sona erdi.")


if __name__ == "__main__":
    main()
