# Faz 1 aday tablosu

Küme temsilcileri: **99** (TV-2 29, U7-u4 10, U7-u6 60); kullanıcının listeden çıkardığı 59 aday `faz1_kullanici_eleme.csv` dosyasında. Hepsi tek kapıyı geçti; bu tablo eleme yapmaz, paper seçimi kullanıcınındır.

Yıllık % = ortak risk ölçeğinde yıllık getiri. Net % = sınama dönemi (U7: 2023 sonrası) net getiri. İşaret: K = kısa sınama (sürüm sonrası < 1 yıl ya da < 10 işlem haftası), L = lookahead riski, S = şüphe taraması.

Kanıt (bilgi, eleme değil): güçlü = kısa sınama yok, şüphe işareti yok, ≥ 30 işlem → **91** güçlü, 8 zayıf. Sıra: temkinli haftalık alt sınır (p10), sonra yıllık getiri.

| # | Kanıt | Kaynak | Kimlik | Sembol | TF | Hafta | İşlem | Yıllık % | p10 haftalık % | Net % | PF | MDD % | İşaret |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | zayıf | TV-2 | [9u8pzF0I](https://www.tradingview.com/script/9u8pzF0I/) | CME_MINI:MNQ1! | 120 | 30 | 84 | 47.5 | 0.73 | 541.4 | 6.14 | 1.7 | K S (aşırı getiri) |
| 2 | zayıf | TV-2 | [yhoK9cH4](https://www.tradingview.com/script/yhoK9cH4/) | NASDAQ:META | 15 | 12 | 43 | 36.6 | 0.64 | 35.6 | 2.14 | 6.7 | K S (veri_kisa) |
| 3 | zayıf | TV-2 | [QCkIgf3z](https://www.tradingview.com/script/QCkIgf3z/) | COINBASE:ETHUSD | 15 | 33 | 300 | 36.2 | 0.41 | 22.6 | 2.96 | 0.2 | K |
| 4 | zayıf | TV-2 | [zuEOEYPK](https://www.tradingview.com/script/zuEOEYPK/) | BINGX:BTCUSDT.P | 180 | 30 | 50 | 28.8 | 0.26 | 1.1 | 2.76 | 0.2 | K |
| 5 | zayıf | TV-2 | [BR74LOKo](https://www.tradingview.com/script/BR74LOKo/) | BYBIT:BTCUSDT.P | 15 | 21 | 224 | 22.7 | 0.19 | 1.9 | 1.98 | 2.1 | K |
| 6 | güçlü | U7-u6 | TV-zoY9DmsF | ABD25 | 1D | 199 | 119 | 13.2 | 0.16 | 17.8 | 2.39 | 2.0 |  |
| 7 | güçlü | TV-2 | [G4RNcGXg](https://www.tradingview.com/script/G4RNcGXg/) | AMEX:SPY | 60 | 152 | 89 | 11.1 | 0.14 | 15.2 | 4.91 | 3.5 |  |
| 8 | güçlü | TV-2 | [wcegMOXj](https://www.tradingview.com/script/wcegMOXj/) | BINANCE:ETHBTC | 360 | 169 | 257 | 14.4 | 0.12 | 9.6 | 2.19 | 1.1 |  |
| 9 | zayıf | U7-u6 | TV-sPNx5Z74 | ABD25 | 1D | 199 | 23 | 11.0 | 0.12 | 29.0 | 6.29 | 5.5 |  |
| 10 | güçlü | U7-u6 | TV-DUCODGjC | ABD25 | 1D | 199 | 295 | 10.6 | 0.11 | 30.7 | 1.47 | 6.0 |  |
| 11 | güçlü | U7-u6 | TV-IMKs0OPw | ABD25 | 1D | 199 | 211 | 9.7 | 0.10 | 14.9 | 1.65 | 3.4 |  |
| 12 | güçlü | U7-u6 | TV-71yKm18B | KRIPTO25 | 4H | 199 | 226 | 13.5 | 0.10 | 56.0 | 1.99 | 11.1 |  |
| 13 | güçlü | U7-u6 | TV-dpkq3n4O | ABD25 | 1D | 199 | 150 | 9.9 | 0.09 | 24.6 | 2.07 | 4.5 |  |
| 14 | güçlü | U7-u6 | TV-70PkIvTL | ABD25 | 1D | 199 | 126 | 10.8 | 0.09 | 21.5 | 1.78 | 6.5 |  |
| 15 | zayıf | U7-u6 | TV-bZ815rmw | ABD25 | 1D | 199 | 26 | 9.5 | 0.08 | 24.5 | 5.65 | 6.1 |  |
| 16 | güçlü | U7-u6 | TV-KO7Qe4Xb | EMTIA | 1D | 199 | 76 | 8.1 | 0.07 | 13.9 | 1.70 | 3.4 |  |
| 17 | güçlü | U7-u6 | TV-3Q75d98D | KRIPTO25 | 1D | 199 | 307 | 12.4 | 0.07 | 76.4 | 2.62 | 16.7 |  |
| 18 | güçlü | U7-u6 | TV-3BXWqwnF | KRIPTO25 | 1D | 199 | 94 | 12.3 | 0.07 | 64.8 | 2.75 | 11.4 |  |
| 19 | güçlü | U7-u6 | TV-Q9OQye4C | KRIPTO25 | 1D | 199 | 285 | 11.2 | 0.06 | 31.3 | 1.90 | 8.5 |  |
| 20 | güçlü | U7-u6 | TV-ANmKXWWJ | KRIPTO25 | 4H | 199 | 394 | 11.1 | 0.05 | 97.3 | 1.44 | 18.1 |  |
| 21 | güçlü | TV-2 | [PZ5MpxP1](https://www.tradingview.com/script/PZ5MpxP1/) | NASDAQ:AAPL | 60 | 152 | 36 | 8.8 | 0.05 | 7.8 | 3.91 | 3.8 |  |
| 22 | güçlü | U7-u6 | TV-egTb7TgJ | KRIPTO25 | 1D | 199 | 129 | 9.9 | 0.05 | 20.5 | 2.38 | 5.0 |  |
| 23 | zayıf | U7-u6 | TV-6ZReHYKn | ABD25 | 1D | 199 | 11 | 7.0 | 0.05 | 35.3 | 9.46 | 11.4 |  |
| 24 | güçlü | U7-u6 | TV-wigMmPHd | ABD25 | 1D | 199 | 399 | 6.7 | 0.05 | 35.7 | 1.39 | 9.3 |  |
| 25 | güçlü | U7-u6 | TV-qo43NaGV | ABD25 | 1D | 199 | 344 | 7.6 | 0.05 | 14.4 | 1.37 | 4.4 |  |
| 26 | güçlü | U7-u6 | TV-oF6FmwfR | KRIPTO25 | 1D | 199 | 233 | 10.9 | 0.05 | 27.1 | 2.18 | 10.4 |  |
| 27 | güçlü | U7-u6 | TV-XRZCjbFr | ABD25 | 1D | 199 | 245 | 8.3 | 0.04 | 12.9 | 1.46 | 4.6 |  |
| 28 | güçlü | U7-u6 | TV-Z9O5w3SG | KRIPTO25 | 1D | 199 | 71 | 8.6 | 0.04 | 14.8 | 2.22 | 4.4 |  |
| 29 | güçlü | U7-u6 | TV-roaahmoi | KRIPTO25 | 4H | 199 | 375 | 10.3 | 0.04 | 82.5 | 1.75 | 21.8 |  |
| 30 | güçlü | U7-u6 | TV-HfxNiEab | KRIPTO25 | 4H | 199 | 800 | 9.9 | 0.03 | 62.6 | 1.38 | 15.9 |  |
| 31 | güçlü | U7-u4 | U4-H2:KRIPTO25:4H | KRIPTO25 | 4H | 199 | 372 | 11.1 | 0.03 | 97.5 | 1.51 | 19.3 |  |
| 32 | güçlü | U7-u4 | U4-H3:ABD25:1D | ABD25 | 1D | 199 | 54 | 7.0 | 0.03 | 15.5 | 2.48 | 6.9 |  |
| 33 | güçlü | U7-u4 | U4-H2:KRIPTO25:1D | KRIPTO25 | 1D | 199 | 59 | 6.3 | 0.03 | 29.7 | 2.68 | 13.0 |  |
| 34 | güçlü | U7-u6 | TV-TIpnJpU8 | KRIPTO25 | 4H | 199 | 625 | 10.3 | 0.03 | 68.7 | 1.47 | 19.6 |  |
| 35 | güçlü | U7-u6 | TV-jc2hs2qK | KRIPTO25 | 4H | 199 | 95 | 9.5 | 0.03 | 43.6 | 2.15 | 10.7 |  |
| 36 | güçlü | U7-u6 | TV-eDyfoKkr | ABD25 | 1D | 199 | 550 | 6.6 | 0.02 | 23.6 | 1.19 | 9.6 |  |
| 37 | güçlü | U7-u6 | TV-AORNVoek | ABD25 | 1D | 199 | 212 | 6.8 | 0.02 | 18.6 | 1.32 | 8.1 |  |
| 38 | güçlü | TV-2 | [hWvuZJN1](https://www.tradingview.com/script/hWvuZJN1/) | AMEX:SPY | 60 | 152 | 75 | 5.7 | 0.02 | 6.3 | 1.94 | 2.6 |  |
| 39 | güçlü | U7-u6 | TV-5EGVP61U | ABD25 | 1D | 199 | 108 | 7.0 | 0.02 | 12.2 | 1.47 | 7.2 |  |
| 40 | güçlü | U7-u6 | TV-97gxVA5b | ABD25 | 1D | 199 | 82 | 7.2 | 0.02 | 12.5 | 1.80 | 3.8 |  |
| 41 | güçlü | TV-2 | [oZYSB6Ui](https://www.tradingview.com/script/oZYSB6Ui/) | AMEX:SPY | 60 | 152 | 60 | 4.6 | 0.01 | 1.3 | 2.26 | 0.7 |  |
| 42 | güçlü | TV-2 | [3UcIwSrE](https://www.tradingview.com/script/3UcIwSrE/) | KRAKEN:ETHUSD | 60 | 367 | 2988 | 4.5 | 0.01 | 5.5 | 1.08 | 2.4 |  |
| 43 | güçlü | U7-u6 | TV-vpopCZIt | KRIPTO25 | 1D | 199 | 201 | 6.9 | 0.01 | 16.1 | 1.40 | 6.4 |  |
| 44 | güçlü | TV-2 | [WfaaCqaN](https://www.tradingview.com/script/WfaaCqaN/) | NASDAQ:QQQ | 60 | 152 | 35 | 7.0 | 0.01 | 40.6 | 1.93 | 16.9 |  |
| 45 | güçlü | U7-u6 | TV-NgSIfKQx | KRIPTO25 | 1D | 199 | 126 | 7.6 | 0.00 | 15.5 | 1.67 | 8.9 |  |
| 46 | güçlü | U7-u6 | TV-rvBgD3aP | ABD25 | 1D | 199 | 94 | 6.2 | 0.00 | 14.8 | 1.47 | 8.1 |  |
| 47 | güçlü | U7-u4 | U4-H3:EMTIA:1D | EMTIA | 1D | 199 | 35 | 4.7 | 0.00 | 15.6 | 3.40 | 12.0 |  |
| 48 | güçlü | TV-2 | [VQjItUaK](https://www.tradingview.com/script/VQjItUaK/) | BITFINEX:XRPUSD | 60 | 363 | 2902 | 4.6 | 0.00 | 0.0 | 1.11 | 0.0 |  |
| 49 | güçlü | U7-u6 | TV-KW2v4SNI | ABD25 | 1D | 199 | 145 | 4.9 | -0.00 | 8.2 | 1.44 | 4.7 |  |
| 50 | güçlü | TV-2 | [5jxP6TDu](https://www.tradingview.com/script/5jxP6TDu/) | AMEX:SPY | 60 | 152 | 48 | 5.0 | -0.00 | 2.0 | 2.41 | 1.3 |  |
| 51 | güçlü | U7-u6 | TV-n3eosaZK | ABD25 | 1D | 199 | 247 | 4.6 | -0.01 | 6.6 | 1.27 | 3.5 |  |
| 52 | güçlü | U7-u6 | TV-PUEDA3c6 | ABD25 | 1D | 199 | 480 | 4.6 | -0.01 | 9.0 | 1.17 | 5.8 |  |
| 53 | güçlü | U7-u6 | TV-o9qty0BL | KRIPTO25 | 4H | 199 | 259 | 8.1 | -0.01 | 47.6 | 1.45 | 15.2 |  |
| 54 | güçlü | U7-u6 | TV-tuC7aGNI | KRIPTO25 | 4H | 199 | 480 | 6.7 | -0.01 | 22.3 | 1.20 | 12.5 |  |
| 55 | güçlü | U7-u6 | TV-xYflA6O7 | ABD25 | 1D | 199 | 51 | 4.1 | -0.01 | 2.7 | 1.43 | 2.0 |  |
| 56 | güçlü | TV-2 | [j9rq1wQq](https://www.tradingview.com/script/j9rq1wQq/) | BINANCE:QTUMUSDT | 12H | 358 | 221 | 3.2 | -0.01 | 0.0 | 1.37 | 0.0 |  |
| 57 | güçlü | U7-u4 | U4-H4:ABD25:1D | ABD25 | 1D | 199 | 676 | 3.5 | -0.01 | 6.3 | 1.13 | 6.0 |  |
| 58 | güçlü | U7-u6 | TV-FEnNQpAn | KRIPTO25 | 1D | 199 | 38 | 5.8 | -0.02 | 16.7 | 2.76 | 10.1 |  |
| 59 | güçlü | U7-u6 | TV-W67tJltC | KRIPTO25 | 1D | 199 | 211 | 6.7 | -0.02 | 23.2 | 1.56 | 12.8 |  |
| 60 | güçlü | U7-u4 | U4-H2:EMTIA:1D | EMTIA | 1D | 199 | 40 | 4.5 | -0.02 | 18.2 | 2.37 | 12.4 |  |
| 61 | güçlü | U7-u6 | TV-HPbRZvsV | KRIPTO25 | 1D | 199 | 373 | 7.8 | -0.02 | 16.5 | 1.36 | 7.7 |  |
| 62 | güçlü | U7-u6 | TV-cz5KaioF | ABD25 | 1D | 199 | 171 | 4.4 | -0.02 | 7.2 | 1.37 | 6.2 |  |
| 63 | güçlü | U7-u6 | TV-VOFjU544 | KRIPTO25 | 1D | 199 | 158 | 8.1 | -0.02 | 19.6 | 1.61 | 9.9 |  |
| 64 | güçlü | TV-2 | [627VbHkS](https://www.tradingview.com/script/627VbHkS/) | BITFINEX:BTCUSD | 360 | 110 | 42 | 6.9 | -0.02 | 2.9 | 1.57 | 4.4 |  |
| 65 | güçlü | U7-u4 | U4-H3:KRIPTO25:4H | KRIPTO25 | 4H | 199 | 373 | 6.5 | -0.02 | 29.7 | 1.34 | 16.3 |  |
| 66 | güçlü | U7-u6 | TV-zrDoqm9F | EMTIA | 1D | 199 | 62 | 4.0 | -0.02 | 6.4 | 1.31 | 4.3 |  |
| 67 | güçlü | TV-2 | [QPIGo8hs](https://www.tradingview.com/script/QPIGo8hs/) | BINANCE:ETHBTC | 120 | 362 | 899 | 3.3 | -0.02 | 0.0 | 1.12 | 0.0 |  |
| 68 | güçlü | TV-2 | [mXygJWkv](https://www.tradingview.com/script/mXygJWkv/) | BINANCE:BTCUSDT | 60 | 314 | 638 | 2.7 | -0.02 | 30.8 | 1.06 | 34.8 |  |
| 69 | güçlü | U7-u6 | TV-BJDRgy7z | KRIPTO25 | 1D | 199 | 173 | 6.7 | -0.03 | 21.9 | 1.34 | 14.4 |  |
| 70 | güçlü | U7-u6 | TV-LBcj22se | ABD25 | 1D | 199 | 119 | 3.9 | -0.03 | 9.6 | 1.32 | 6.3 |  |
| 71 | güçlü | U7-u6 | TV-X0F9OE4L | KRIPTO25 | 1D | 199 | 395 | 6.1 | -0.03 | 11.5 | 1.21 | 5.9 |  |
| 72 | güçlü | TV-2 | [KUyDNRyQ](https://www.tradingview.com/script/KUyDNRyQ/) | BITSTAMP:ETHBTC | 60 | 324 | 620 | 3.3 | -0.03 | 10.7 | 1.66 | 16.9 |  |
| 73 | güçlü | TV-2 | [lGAXIACq](https://www.tradingview.com/script/lGAXIACq/) | NASDAQ:QQQ | 60 | 152 | 77 | 2.1 | -0.03 | 4.5 | 1.60 | 3.5 |  |
| 74 | güçlü | U7-u6 | TV-vJc6IOTz | ABD25 | 1D | 199 | 163 | 4.4 | -0.03 | 6.2 | 1.33 | 6.0 |  |
| 75 | güçlü | U7-u6 | TV-Xr2xrNAY | KRIPTO25 | 4H | 199 | 192 | 7.6 | -0.03 | 43.4 | 1.48 | 24.0 |  |
| 76 | güçlü | TV-2 | [zFKRj4Gi](https://www.tradingview.com/script/zFKRj4Gi/) | BITFINEX:BTCUSD | 480 | 165 | 117 | 5.3 | -0.04 | 7.8 | 1.31 | 5.1 |  |
| 77 | güçlü | U7-u4 | U4-H4:EMTIA:1D | EMTIA | 1D | 199 | 150 | 2.2 | -0.04 | 2.0 | 1.17 | 2.5 |  |
| 78 | güçlü | TV-2 | [YqnWtjnn](https://www.tradingview.com/script/YqnWtjnn/) | BITFINEX:BTCUSD | 360 | 82 | 126 | 9.0 | -0.04 | 3.9 | 1.60 | 1.8 |  |
| 79 | güçlü | TV-2 | [XJfWHHEc](https://www.tradingview.com/script/XJfWHHEc/) | BITFINEX:BTCUSD | 360 | 147 | 36 | 5.5 | -0.04 | 16.4 | 1.58 | 5.1 |  |
| 80 | güçlü | TV-2 | [warXbPtA](https://www.tradingview.com/script/warXbPtA/) | BITFINEX:BTCUSD | 480 | 145 | 49 | 5.6 | -0.04 | 9.1 | 1.44 | 4.6 |  |
| 81 | güçlü | U7-u6 | TV-VO6DY8s1 | KRIPTO25 | 1D | 199 | 141 | 5.7 | -0.04 | 11.7 | 1.48 | 9.5 |  |
| 82 | güçlü | TV-2 | [hLZPT7it](https://www.tradingview.com/script/hLZPT7it/) | BITFINEX:BTCUSD | 480 | 160 | 38 | 6.3 | -0.04 | 5.1 | 1.22 | 7.7 |  |
| 83 | güçlü | U7-u6 | TV-buSJAz8o | KRIPTO25 | 1D | 199 | 108 | 3.5 | -0.05 | 8.2 | 1.22 | 9.6 |  |
| 84 | güçlü | U7-u6 | TV-GP3FEy2z | ABD25 | 1D | 199 | 108 | 4.1 | -0.05 | 6.1 | 1.37 | 6.5 |  |
| 85 | güçlü | U7-u6 | TV-TbK1rB5B | KRIPTO25 | 1D | 199 | 131 | 6.9 | -0.05 | 17.5 | 1.53 | 13.7 |  |
| 86 | güçlü | U7-u6 | TV-yvDyq0pv | KRIPTO25 | 4H | 199 | 188 | 6.0 | -0.05 | 23.7 | 1.34 | 15.9 |  |
| 87 | güçlü | U7-u6 | TV-BjjAOuub | ABD25 | 1D | 199 | 368 | 2.3 | -0.05 | 7.4 | 1.06 | 12.3 |  |
| 88 | güçlü | U7-u6 | TV-hezSShJr | ABD25 | 1D | 199 | 66 | 2.4 | -0.06 | 2.4 | 1.19 | 5.6 |  |
| 89 | güçlü | U7-u6 | TV-qgTc4zie | KRIPTO25 | 1D | 199 | 295 | 4.9 | -0.06 | 9.2 | 1.23 | 11.2 |  |
| 90 | güçlü | U7-u6 | TV-dpZLkrdx | KRIPTO25 | 1D | 199 | 2259 | 4.6 | -0.06 | 17.4 | 1.12 | 18.6 |  |
| 91 | güçlü | U7-u4 | U4-H1:ABD25:1D | ABD25 | 1D | 199 | 132 | 1.4 | -0.07 | 2.7 | 1.16 | 9.3 |  |
| 92 | güçlü | TV-2 | [mUKDFKzn](https://www.tradingview.com/script/mUKDFKzn/) | AMEX:SPY | 60 | 152 | 86 | 1.7 | -0.08 | 4.4 | 1.10 | 18.4 |  |
| 93 | güçlü | U7-u6 | TV-WWuTjyDx | ABD25 | 1D | 199 | 151 | 0.8 | -0.08 | 0.7 | 1.05 | 3.0 |  |
| 94 | güçlü | TV-2 | [lncoD9BX](https://www.tradingview.com/script/lncoD9BX/) | BITFINEX:BTCUSD | 480 | 122 | 47 | 4.1 | -0.09 | 7.7 | 1.34 | 4.0 |  |
| 95 | güçlü | U7-u4 | U4-H2:ABD25:1D | ABD25 | 1D | 199 | 92 | 0.3 | -0.09 | 0.3 | 1.01 | 7.5 |  |
| 96 | güçlü | U7-u6 | TV-uC1oajDr | KRIPTO25 | 1D | 199 | 354 | 2.2 | -0.11 | 4.4 | 1.06 | 12.4 |  |
| 97 | güçlü | TV-2 | [VHbRaeUe](https://www.tradingview.com/script/VHbRaeUe/) | BITFINEX:BTCUSD | 360 | 128 | 79 | 1.8 | -0.11 | 2.8 | 1.11 | 9.0 |  |
| 98 | güçlü | TV-2 | [UUHabgvo](https://www.tradingview.com/script/UUHabgvo/) | BITFINEX:BTCUSD | 360 | 169 | 37 | 0.8 | -0.12 | 0.9 | 1.06 | 5.0 |  |
| 99 | güçlü | U7-u6 | TV-QTYaYuX7 | KRIPTO25 | 1D | 199 | 490 | 0.6 | -0.15 | 0.4 | 1.01 | 9.2 |  |
