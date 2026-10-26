# Faz 1 nihai değerlendirme — lider taslağı (Sol 6.1 eleştirisi bekleniyor)

Tarih: 2026-10-26. Girdi: kullanıcı elemesinden sonra kalan **99** aday (91 güçlü + 8 zayıf), `results/faz1_adaylar.csv`.
Dukascopy (altın/endeks) koşusu kullanıcı kararıyla durduruldu; dahil değil.

## Ölçütler (eşikler bir kez kondu, sonuca göre ayarlanmadı)

| Kod | Ölçüt | Neden |
|---|---|---|
| R1 | Temkinli haftalık alt sınır (p10) ≤ 0 → çıkar | Kârın şans eseri olma payı yüksek; TEST_YAPISI Adım 3'ün sıralama ölçütü. |
| R2 | Hesap/veri hatası şüphesi → çıkar | 9u8pzF0I (MNQ 2s): sınama net %541, yalnız 2 yıllık yfinance verisi; doğrulanmadı. |
| R3 | Tek enstrüman (TV-2) ve sınamada yılda < 30 işlem → çıkar | Kullanıcı kuralı (zayıflara uygulanmıştı), güçlülere de tutarlı uygulandı. |
| R4 | PF < 1.2 → çıkar | Kenar çok ince; maliyet/kayma sapmasına dayanmaz. |
| R5 | U7: 2x maliyette OOS PF < 1 → çıkar | Maliyet varsayımına duyarlı. |
| R6 | Kalanlar arasında 2023→ günlük getiri korelasyonu > 0.6 → p10'u düşük olan çıkar | Aynı işi yapan kopyalar portföyü şişirir. |

Not: "Kanıt" (güçlü/zayıf) etiketi karar ölçütü değildir; kullanıcının tuttuğu zayıflar aynı ölçütlerden geçti. Kalan zayıflar "kısa sınama" uyarısı taşır.

## Sonuç

Çıkan: R1 51 · R4 19 · R3 14 · R5 6 · R2 1 (bir aday birden çok ölçüte takılabilir) · R6 kopya 15.

**Nihai liste: 24 strateji.**

| | Günlük | 4–6 saat | 3 saat | 15 dk | Toplam |
|---|---:|---:|---:|---:|---:|
| ABD | 14 | 0 | 0 | 1 | 15 |
| Kripto | 2 | 2 | 1 | 2 | 7 |
| Emtia | 2 | 0 | 0 | 0 | 2 |

## Nihai liste (kalsın)

| Kategori | TF | Kaynak | Kimlik | Sembol | Kanıt | İşlem | Yıllık % | p10 % | PF | MDD % | Gerekçe |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| ABD | 15 dk | TV-2 | yhoK9cH4 | NASDAQ:META | zayıf | 43 | 36.6 | 0.64 | 2.14 | 6.7 | kısa sınama (<1 yıl): paper'da doğrulanmalı |
| ABD | Günlük | U7-u6 | TV-zoY9DmsF | ABD25 | güçlü | 119 | 13.2 | 0.16 | 2.39 | 2.0 |  |
| ABD | Günlük | U7-u6 | TV-sPNx5Z74 | ABD25 | zayıf | 23 | 11.0 | 0.12 | 6.29 | 5.5 |  |
| ABD | Günlük | U7-u6 | TV-DUCODGjC | ABD25 | güçlü | 295 | 10.6 | 0.11 | 1.47 | 6.0 |  |
| ABD | Günlük | U7-u6 | TV-IMKs0OPw | ABD25 | güçlü | 211 | 9.7 | 0.10 | 1.65 | 3.4 |  |
| ABD | Günlük | U7-u6 | TV-dpkq3n4O | ABD25 | güçlü | 150 | 9.9 | 0.09 | 2.07 | 4.5 |  |
| ABD | Günlük | U7-u6 | TV-70PkIvTL | ABD25 | güçlü | 126 | 10.8 | 0.09 | 1.78 | 6.5 |  |
| ABD | Günlük | U7-u6 | TV-wigMmPHd | ABD25 | güçlü | 399 | 6.7 | 0.05 | 1.39 | 9.3 |  |
| ABD | Günlük | U7-u6 | TV-qo43NaGV | ABD25 | güçlü | 344 | 7.6 | 0.05 | 1.37 | 4.4 |  |
| ABD | Günlük | U7-u6 | TV-XRZCjbFr | ABD25 | güçlü | 245 | 8.3 | 0.04 | 1.46 | 4.6 |  |
| ABD | Günlük | U7-u4 | U4-H3:ABD25:1D | ABD25 | güçlü | 54 | 7.0 | 0.03 | 2.48 | 6.9 |  |
| ABD | Günlük | U7-u6 | TV-AORNVoek | ABD25 | güçlü | 212 | 6.8 | 0.02 | 1.32 | 8.1 |  |
| ABD | Günlük | U7-u6 | TV-5EGVP61U | ABD25 | güçlü | 108 | 7.0 | 0.02 | 1.47 | 7.2 |  |
| ABD | Günlük | U7-u6 | TV-97gxVA5b | ABD25 | güçlü | 82 | 7.2 | 0.02 | 1.80 | 3.8 |  |
| ABD | Günlük | U7-u6 | TV-rvBgD3aP | ABD25 | güçlü | 94 | 6.2 | 0.00 | 1.47 | 8.1 |  |
| Emtia | Günlük | U7-u6 | TV-KO7Qe4Xb | EMTIA | güçlü | 76 | 8.1 | 0.07 | 1.70 | 3.4 |  |
| Emtia | Günlük | U7-u4 | U4-H3:EMTIA:1D | EMTIA | güçlü | 35 | 4.7 | 0.00 | 3.40 | 12.0 |  |
| Kripto | 15 dk | TV-2 | QCkIgf3z | COINBASE:ETHUSD | zayıf | 300 | 36.2 | 0.41 | 2.96 | 0.2 | kısa sınama (<1 yıl): paper'da doğrulanmalı |
| Kripto | 3 saat | TV-2 | zuEOEYPK | BINGX:BTCUSDT.P | zayıf | 50 | 28.8 | 0.26 | 2.76 | 0.2 | kısa sınama (<1 yıl): paper'da doğrulanmalı |
| Kripto | 15 dk | TV-2 | BR74LOKo | BYBIT:BTCUSDT.P | zayıf | 224 | 22.7 | 0.19 | 1.98 | 2.1 | kısa sınama (<1 yıl): paper'da doğrulanmalı |
| Kripto | 6 saat | TV-2 | wcegMOXj | BINANCE:ETHBTC | güçlü | 257 | 14.4 | 0.12 | 2.19 | 1.1 |  |
| Kripto | 4 saat | U7-u6 | TV-71yKm18B | KRIPTO25 | güçlü | 226 | 13.5 | 0.10 | 1.99 | 11.1 |  |
| Kripto | Günlük | U7-u6 | TV-3BXWqwnF | KRIPTO25 | güçlü | 94 | 12.3 | 0.07 | 2.75 | 11.4 |  |
| Kripto | Günlük | U7-u4 | U4-H2:KRIPTO25:1D | KRIPTO25 | güçlü | 59 | 6.3 | 0.03 | 2.68 | 13.0 |  |

## Çıkanlar

| Kategori | TF | Kaynak | Kimlik | Sembol | Kanıt | İşlem | Yıllık % | p10 % | PF | MDD % | Gerekçe |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| ABD | 1 saat | TV-2 | G4RNcGXg | AMEX:SPY | güçlü | 89 | 11.1 | 0.14 | 4.91 | 3.5 | R3 tek enstrüman <30 işlem/yıl |
| ABD | Günlük | U7-u6 | TV-bZ815rmw | ABD25 | zayıf | 26 | 9.5 | 0.08 | 5.65 | 6.1 | kopya: TV-sPNx5Z74 ile r=0.74 |
| ABD | 1 saat | TV-2 | PZ5MpxP1 | NASDAQ:AAPL | güçlü | 36 | 8.8 | 0.05 | 3.91 | 3.8 | R3 tek enstrüman <30 işlem/yıl |
| ABD | Günlük | U7-u6 | TV-6ZReHYKn | ABD25 | zayıf | 11 | 7.0 | 0.05 | 9.46 | 11.4 | kopya: TV-sPNx5Z74 ile r=0.63 |
| ABD | Günlük | U7-u6 | TV-eDyfoKkr | ABD25 | güçlü | 550 | 6.6 | 0.02 | 1.19 | 9.6 | R4 PF<1.2 |
| ABD | 1 saat | TV-2 | hWvuZJN1 | AMEX:SPY | güçlü | 75 | 5.7 | 0.02 | 1.94 | 2.6 | R3 tek enstrüman <30 işlem/yıl |
| ABD | 1 saat | TV-2 | oZYSB6Ui | AMEX:SPY | güçlü | 60 | 4.6 | 0.01 | 2.26 | 0.7 | R3 tek enstrüman <30 işlem/yıl |
| ABD | 1 saat | TV-2 | WfaaCqaN | NASDAQ:QQQ | güçlü | 35 | 7.0 | 0.01 | 1.93 | 16.9 | R3 tek enstrüman <30 işlem/yıl |
| ABD | Günlük | U7-u6 | TV-KW2v4SNI | ABD25 | güçlü | 145 | 4.9 | -0.00 | 1.44 | 4.7 | R1 p10≤0 |
| ABD | 1 saat | TV-2 | 5jxP6TDu | AMEX:SPY | güçlü | 48 | 5.0 | -0.00 | 2.41 | 1.3 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| ABD | Günlük | U7-u6 | TV-n3eosaZK | ABD25 | güçlü | 247 | 4.6 | -0.01 | 1.27 | 3.5 | R1 p10≤0 |
| ABD | Günlük | U7-u6 | TV-PUEDA3c6 | ABD25 | güçlü | 480 | 4.6 | -0.01 | 1.17 | 5.8 | R1 p10≤0; R4 PF<1.2 |
| ABD | Günlük | U7-u6 | TV-xYflA6O7 | ABD25 | güçlü | 51 | 4.1 | -0.01 | 1.43 | 2.0 | R1 p10≤0 |
| ABD | Günlük | U7-u4 | U4-H4:ABD25:1D | ABD25 | güçlü | 676 | 3.5 | -0.01 | 1.13 | 6.0 | R1 p10≤0; R4 PF<1.2 |
| ABD | Günlük | U7-u6 | TV-cz5KaioF | ABD25 | güçlü | 171 | 4.4 | -0.02 | 1.37 | 6.2 | R1 p10≤0 |
| ABD | Günlük | U7-u6 | TV-LBcj22se | ABD25 | güçlü | 119 | 3.9 | -0.03 | 1.32 | 6.3 | R1 p10≤0 |
| ABD | 1 saat | TV-2 | lGAXIACq | NASDAQ:QQQ | güçlü | 77 | 2.1 | -0.03 | 1.60 | 3.5 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| ABD | Günlük | U7-u6 | TV-vJc6IOTz | ABD25 | güçlü | 163 | 4.4 | -0.03 | 1.33 | 6.0 | R1 p10≤0 |
| ABD | Günlük | U7-u6 | TV-GP3FEy2z | ABD25 | güçlü | 108 | 4.1 | -0.05 | 1.37 | 6.5 | R1 p10≤0 |
| ABD | Günlük | U7-u6 | TV-BjjAOuub | ABD25 | güçlü | 368 | 2.3 | -0.05 | 1.06 | 12.3 | R1 p10≤0; R4 PF<1.2; R5 2x maliyette PF<1 |
| ABD | Günlük | U7-u6 | TV-hezSShJr | ABD25 | güçlü | 66 | 2.4 | -0.06 | 1.19 | 5.6 | R1 p10≤0; R4 PF<1.2 |
| ABD | Günlük | U7-u4 | U4-H1:ABD25:1D | ABD25 | güçlü | 132 | 1.4 | -0.07 | 1.16 | 9.3 | R1 p10≤0; R4 PF<1.2 |
| ABD | 1 saat | TV-2 | mUKDFKzn | AMEX:SPY | güçlü | 86 | 1.7 | -0.08 | 1.10 | 18.4 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl; R4 PF<1.2 |
| ABD | Günlük | U7-u6 | TV-WWuTjyDx | ABD25 | güçlü | 151 | 0.8 | -0.08 | 1.05 | 3.0 | R1 p10≤0; R4 PF<1.2; R5 2x maliyette PF<1 |
| ABD | Günlük | U7-u4 | U4-H2:ABD25:1D | ABD25 | güçlü | 92 | 0.3 | -0.09 | 1.01 | 7.5 | R1 p10≤0; R4 PF<1.2; R5 2x maliyette PF<1 |
| Emtia | Günlük | U7-u4 | U4-H2:EMTIA:1D | EMTIA | güçlü | 40 | 4.5 | -0.02 | 2.37 | 12.4 | R1 p10≤0 |
| Emtia | Günlük | U7-u6 | TV-zrDoqm9F | EMTIA | güçlü | 62 | 4.0 | -0.02 | 1.31 | 4.3 | R1 p10≤0 |
| Emtia | Günlük | U7-u4 | U4-H4:EMTIA:1D | EMTIA | güçlü | 150 | 2.2 | -0.04 | 1.17 | 2.5 | R1 p10≤0; R4 PF<1.2 |
| Kripto | Günlük | U7-u6 | TV-3Q75d98D | KRIPTO25 | güçlü | 307 | 12.4 | 0.07 | 2.62 | 16.7 | kopya: TV-71yKm18B ile r=0.61 |
| Kripto | Günlük | U7-u6 | TV-Q9OQye4C | KRIPTO25 | güçlü | 285 | 11.2 | 0.06 | 1.90 | 8.5 | kopya: TV-71yKm18B ile r=0.61 |
| Kripto | 4 saat | U7-u6 | TV-ANmKXWWJ | KRIPTO25 | güçlü | 394 | 11.1 | 0.05 | 1.44 | 18.1 | kopya: TV-3BXWqwnF ile r=0.61 |
| Kripto | Günlük | U7-u6 | TV-egTb7TgJ | KRIPTO25 | güçlü | 129 | 9.9 | 0.05 | 2.38 | 5.0 | kopya: TV-71yKm18B ile r=0.61 |
| Kripto | Günlük | U7-u6 | TV-oF6FmwfR | KRIPTO25 | güçlü | 233 | 10.9 | 0.05 | 2.18 | 10.4 | kopya: TV-3BXWqwnF ile r=0.7 |
| Kripto | Günlük | U7-u6 | TV-Z9O5w3SG | KRIPTO25 | güçlü | 71 | 8.6 | 0.04 | 2.22 | 4.4 | kopya: TV-3BXWqwnF ile r=0.79 |
| Kripto | 4 saat | U7-u6 | TV-roaahmoi | KRIPTO25 | güçlü | 375 | 10.3 | 0.04 | 1.75 | 21.8 | kopya: TV-71yKm18B ile r=0.63 |
| Kripto | 4 saat | U7-u6 | TV-HfxNiEab | KRIPTO25 | güçlü | 800 | 9.9 | 0.03 | 1.38 | 15.9 | kopya: TV-3BXWqwnF ile r=0.66 |
| Kripto | 4 saat | U7-u4 | U4-H2:KRIPTO25:4H | KRIPTO25 | güçlü | 372 | 11.1 | 0.03 | 1.51 | 19.3 | kopya: TV-71yKm18B ile r=0.67 |
| Kripto | 4 saat | U7-u6 | TV-TIpnJpU8 | KRIPTO25 | güçlü | 625 | 10.3 | 0.03 | 1.47 | 19.6 | kopya: TV-71yKm18B ile r=0.69 |
| Kripto | 4 saat | U7-u6 | TV-jc2hs2qK | KRIPTO25 | güçlü | 95 | 9.5 | 0.03 | 2.15 | 10.7 | kopya: TV-3BXWqwnF ile r=0.7 |
| Kripto | 1 saat | TV-2 | 3UcIwSrE | KRAKEN:ETHUSD | güçlü | 2988 | 4.5 | 0.01 | 1.08 | 2.4 | R4 PF<1.2 |
| Kripto | Günlük | U7-u6 | TV-vpopCZIt | KRIPTO25 | güçlü | 201 | 6.9 | 0.01 | 1.40 | 6.4 | kopya: TV-3BXWqwnF ile r=0.63 |
| Kripto | Günlük | U7-u6 | TV-NgSIfKQx | KRIPTO25 | güçlü | 126 | 7.6 | 0.00 | 1.67 | 8.9 | kopya: TV-3BXWqwnF ile r=0.72 |
| Kripto | 1 saat | TV-2 | VQjItUaK | BITFINEX:XRPUSD | güçlü | 2902 | 4.6 | 0.00 | 1.11 | 0.0 | R4 PF<1.2 |
| Kripto | 4 saat | U7-u6 | TV-o9qty0BL | KRIPTO25 | güçlü | 259 | 8.1 | -0.01 | 1.45 | 15.2 | R1 p10≤0 |
| Kripto | 4 saat | U7-u6 | TV-tuC7aGNI | KRIPTO25 | güçlü | 480 | 6.7 | -0.01 | 1.20 | 12.5 | R1 p10≤0 |
| Kripto | 12 saat | TV-2 | j9rq1wQq | BINANCE:QTUMUSDT | güçlü | 221 | 3.2 | -0.01 | 1.37 | 0.0 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-FEnNQpAn | KRIPTO25 | güçlü | 38 | 5.8 | -0.02 | 2.76 | 10.1 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-W67tJltC | KRIPTO25 | güçlü | 211 | 6.7 | -0.02 | 1.56 | 12.8 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-HPbRZvsV | KRIPTO25 | güçlü | 373 | 7.8 | -0.02 | 1.36 | 7.7 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-VOFjU544 | KRIPTO25 | güçlü | 158 | 8.1 | -0.02 | 1.61 | 9.9 | R1 p10≤0 |
| Kripto | 6 saat | TV-2 | 627VbHkS | BITFINEX:BTCUSD | güçlü | 42 | 6.9 | -0.02 | 1.57 | 4.4 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| Kripto | 4 saat | U7-u4 | U4-H3:KRIPTO25:4H | KRIPTO25 | güçlü | 373 | 6.5 | -0.02 | 1.34 | 16.3 | R1 p10≤0 |
| Kripto | 2 saat | TV-2 | QPIGo8hs | BINANCE:ETHBTC | güçlü | 899 | 3.3 | -0.02 | 1.12 | 0.0 | R1 p10≤0; R4 PF<1.2 |
| Kripto | 1 saat | TV-2 | mXygJWkv | BINANCE:BTCUSDT | güçlü | 638 | 2.7 | -0.02 | 1.06 | 34.8 | R1 p10≤0; R4 PF<1.2 |
| Kripto | Günlük | U7-u6 | TV-BJDRgy7z | KRIPTO25 | güçlü | 173 | 6.7 | -0.03 | 1.34 | 14.4 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-X0F9OE4L | KRIPTO25 | güçlü | 395 | 6.1 | -0.03 | 1.21 | 5.9 | R1 p10≤0 |
| Kripto | 1 saat | TV-2 | KUyDNRyQ | BITSTAMP:ETHBTC | güçlü | 620 | 3.3 | -0.03 | 1.66 | 16.9 | R1 p10≤0 |
| Kripto | 4 saat | U7-u6 | TV-Xr2xrNAY | KRIPTO25 | güçlü | 192 | 7.6 | -0.03 | 1.48 | 24.0 | R1 p10≤0 |
| Kripto | 8 saat | TV-2 | zFKRj4Gi | BITFINEX:BTCUSD | güçlü | 117 | 5.3 | -0.04 | 1.31 | 5.1 | R1 p10≤0 |
| Kripto | 6 saat | TV-2 | YqnWtjnn | BITFINEX:BTCUSD | güçlü | 126 | 9.0 | -0.04 | 1.60 | 1.8 | R1 p10≤0 |
| Kripto | 6 saat | TV-2 | XJfWHHEc | BITFINEX:BTCUSD | güçlü | 36 | 5.5 | -0.04 | 1.58 | 5.1 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| Kripto | 8 saat | TV-2 | warXbPtA | BITFINEX:BTCUSD | güçlü | 49 | 5.6 | -0.04 | 1.44 | 4.6 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| Kripto | Günlük | U7-u6 | TV-VO6DY8s1 | KRIPTO25 | güçlü | 141 | 5.7 | -0.04 | 1.48 | 9.5 | R1 p10≤0 |
| Kripto | 8 saat | TV-2 | hLZPT7it | BITFINEX:BTCUSD | güçlü | 38 | 6.3 | -0.04 | 1.22 | 7.7 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| Kripto | Günlük | U7-u6 | TV-buSJAz8o | KRIPTO25 | güçlü | 108 | 3.5 | -0.05 | 1.22 | 9.6 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-TbK1rB5B | KRIPTO25 | güçlü | 131 | 6.9 | -0.05 | 1.53 | 13.7 | R1 p10≤0 |
| Kripto | 4 saat | U7-u6 | TV-yvDyq0pv | KRIPTO25 | güçlü | 188 | 6.0 | -0.05 | 1.34 | 15.9 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-qgTc4zie | KRIPTO25 | güçlü | 295 | 4.9 | -0.06 | 1.23 | 11.2 | R1 p10≤0 |
| Kripto | Günlük | U7-u6 | TV-dpZLkrdx | KRIPTO25 | güçlü | 2259 | 4.6 | -0.06 | 1.12 | 18.6 | R1 p10≤0; R4 PF<1.2; R5 2x maliyette PF<1 |
| Kripto | 8 saat | TV-2 | lncoD9BX | BITFINEX:BTCUSD | güçlü | 47 | 4.1 | -0.09 | 1.34 | 4.0 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl |
| Kripto | Günlük | U7-u6 | TV-uC1oajDr | KRIPTO25 | güçlü | 354 | 2.2 | -0.11 | 1.06 | 12.4 | R1 p10≤0; R4 PF<1.2; R5 2x maliyette PF<1 |
| Kripto | 6 saat | TV-2 | VHbRaeUe | BITFINEX:BTCUSD | güçlü | 79 | 1.8 | -0.11 | 1.11 | 9.0 | R1 p10≤0; R4 PF<1.2 |
| Kripto | 6 saat | TV-2 | UUHabgvo | BITFINEX:BTCUSD | güçlü | 37 | 0.8 | -0.12 | 1.06 | 5.0 | R1 p10≤0; R3 tek enstrüman <30 işlem/yıl; R4 PF<1.2 |
| Kripto | Günlük | U7-u6 | TV-QTYaYuX7 | KRIPTO25 | güçlü | 490 | 0.6 | -0.15 | 1.01 | 9.2 | R1 p10≤0; R4 PF<1.2; R5 2x maliyette PF<1 |
| Vadeli | 2 saat | TV-2 | 9u8pzF0I | CME_MINI:MNQ1! | zayıf | 84 | 47.5 | 0.73 | 6.14 | 1.7 | R2 hesap/veri şüphesi |

## Liderin yorumu

- Nihai listenin ağırlığı **sepet stratejilerinde** (U7: aynı kural 25 ABD hissesinde / 25 coinde). Tek enstrüman TradingView stratejilerinin çoğu R1/R3/R4'e takıldı; BTC 6-8 saat ailesi (Bitfinex) yılda 11-20 işlemle ve p10 ≤ 0 ile tamamen çıktı.
- ABD günlük ağır (14). Korelasyon eşiği 0.6 olduğu için bunlar birbirinin kopyası değil, ama hepsi ABD hisse piyasasına bağlı: piyasa çöküşünde birlikte zarar edebilirler. Paper'da toplam risk tavanı gerekir.
- Listedeki 4 kısa sınamalı TradingView stratejisi (META 15dk, ETH 15dk, BTC perp 15dk/3s) kullanıcı seçimiyle tutuldu ve ölçütlerden geçti; ama yayım sonrası 1 yıldan kısa veri var. Paper'da en sıkı izlenecekler bunlar.
- TV-sPNx5Z74: 23 işlem, PF 6.3. Ölçütlerden geçiyor ama PF az işlemden şişmiş olabilir.
- Emtia yalnız 2 günlük sepet stratejisi; altın gün içi koşusu durdurulduğu için emtia zayıf temsil ediliyor.

## Sol 6.1 eleştirisi

(bekleniyor)

## Anlaşmazlıklar ve kullanıcı kararı

(Sol 6.1 cevabından sonra)
