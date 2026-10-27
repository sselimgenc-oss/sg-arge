# Trader incelemesi — istikrar, iki aşama (2026-10-27)

Lider tablosunda 47654 adres. **Havuz:** hesap ≥ 50.000 USD; hafta, ay ve tüm zaman ROI > 0; tüm zaman ROI %20–%500; aylık hacim / hesap 0,5–20 kat; tüm zaman PnL'e göre ilk 400.

**1. aşama (kâr eğrisi, son 12 ay):** en az 6 ay; kârlı ay ≥ %60; zirveden düşüş ≤ %30; 12 aylık getiri > 0.
**2. aşama (işlem geçmişi):** 1. aşamadan geçenlerin ilk 25'i; kural motoru (`copytrade/kurallar.yaml`) ve gerçek kaldıraç, emir düzeyinde martingale.

| Aşama | Adres |
|---|---:|
| Havuz | 400 |
| Kâr eğrisi okundu | 387 |
| 1. aşamadan geçti | 43 |
| 2. aşamada incelendi | 25 |

## 2. aşama özeti

| Adres | Kârlı ay | 12 ay getiri | Düşüş | İşlem | Medyan tutma (sa) | Gerçek kaldıraç medyan/en yüksek | Martingale | Kripto dışı hacim | Kural |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| `0xbcd4071d…` | 100% | 1745% | 0% | 0 | — | —/— | yok | — | yetersiz |
| `0x4d5f00be…` | 100% | 225% | 1% | 254 | 0.0 | 0.6/4.2 | yok | 43% | elendi |
| `0x249161f1…` | 100% | 110% | 2% | 759 | 0.0 | 1.0/5.9 | yok | 66% | elendi |
| `0x6809111b…` | 100% | 136% | 5% | 1220 | 0.0 | 1.2/3.0 | yok | 40% | elendi |
| `0xc9186f29…` | 92% | 87% | 3% | 551 | 0.0 | 0.3/4.7 | yok | 0% | yetersiz |
| `0xac5c66fb…` | 92% | 311% | 19% | 151 | 3.1 | 0.5/1.6 | yok | 5% | elendi |
| `0x6f97d329…` | 91% | 4503979% | 20% | 9 | 146.2 | 0.9/1.2 | yok | 0% | yetersiz |
| `0x44559ff9…` | 88% | 286% | 17% | 96 | 55.8 | 1.0/1.8 | VAR | 9% | elendi |
| `0x7c906312…` | 86% | 341% | 21% | 18 | 41.7 | 3.2/14.4 | VAR | 31% | yetersiz |
| `0x7e09dfbb…` | 85% | 168% | 4% | 120 | 21.2 | 0.2/1.0 | VAR | 4% | elendi |
| `0x9075c8f9…` | 85% | 172% | 7% | 221 | 1.6 | 1.5/3.9 | yok | 4% | aday |
| `0x71cfa5e2…` | 85% | 63% | 4% | 223 | 0.0 | 0.0/0.5 | yok | 0% | yetersiz |
| `0xba939edf…` | 85% | 13% | 8% | 176 | 53.3 | 0.3/0.6 | VAR | 0% | elendi |
| `0x1da5bcd7…` | 83% | 135% | 4% | 252 | 5.6 | 0.2/1.0 | yok | 6% | aday |
| `0x4ba1d152…` | 83% | 103% | 10% | 169 | 112.5 | 0.7/1.6 | VAR | 9% | elendi |
| `0x782e4322…` | 80% | 729% | 23% | 35 | 569.0 | 31.8/45.0 | yok | 37% | yetersiz |
| `0xe0afe5de…` | 77% | 181% | 7% | 875 | 23.6 | 0.7/3.4 | yok | 100% | elendi |
| `0x3f94463f…` | 77% | 326% | 30% | 70 | 106.2 | 1.1/2.1 | VAR | 29% | elendi |
| `0x7a6d5fc5…` | 77% | 87% | 28% | 151 | 0.1 | 6.6/7.0 | yok | 6% | yetersiz |
| `0xda51323f…` | 77% | 43% | 20% | 26 | 25.5 | 0.3/2.9 | yok | 0% | yetersiz |
| `0xaf0fdd39…` | 75% | 216% | 26% | 11 | 25.5 | 0.3/0.4 | yok | 0% | yetersiz |
| `0x327d7d42…` | 73% | 105090360% | 2% | 483 | 0.0 | 0.4/0.9 | yok | 56% | elendi |
| `0x885989fd…` | 73% | 31038030% | 19% | 81 | 5.6 | 0.6/1.7 | yok | 18% | elendi |
| `0x67070134…` | 73% | 376% | 4% | 27 | 15.3 | 0.4/2.0 | yok | 44% | yetersiz |
| `0x1271bf72…` | 73% | 210% | 14% | 8 | 86.1 | 0.3/0.8 | VAR | 0% | yetersiz |

## Ayrıntı (ilk 8)

Son 365 günün gerçekleşmiş net PnL'i (spot hariç). Adresi Hyperdash'te arama kutusuna yapıştırıp gözle de bakabilirsin. **Bu bir seçim değil, örnektir.**

## `0x9075c8f93cd30c1015e6fbe9718f0bf2dca4e2f0`
- Hesap değeri: 78,525 USD · lider tablosu tüm zaman PnL 120,920 USD, ROI %98 · aylık ROI %10.2
- Okunan fill: 5647 (ilk: 2025-10-28)
- Kapanmış işlem: 221 · kârlı ay oranı: 85% · Sortino 2.02 · Calmar 7.86
- En büyük işlemin kâr payı: 10% · en iyi işlem çıkınca PF 1.97
- Medyan tutma: 1.6 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 1.4505437874173661/3.881173336448294
- Martingale işareti: yok (zarara ekleme oranı 14%, 389 ekleme)
- Coin dağılımı (fill sayısıyla): HYPE %52, TON %9, BTC %8, ETH %8, LIT %6
- Varlık sınıfı (hacim): kripto %95, hisse %3, spot %2
- Açık pozisyon: 0
- **Kural sonucu: aday**

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2025-10 | 1,363 |
| 2025-11 | 14,689 |
| 2025-12 | 9,453 |
| 2026-01 | 1,638 |
| 2026-02 | 14,597 |
| 2026-04 | 402 |
| 2026-05 | 3,838 |
| 2026-06 | 9,618 |
| 2026-07 | 1,603 |
| 2026-08 | -9,359 |
| 2026-09 | 4,086 |
| 2026-10 | 1,523 |

## `0x1da5bcd75d2bdc41d8372e976f2f665479e73151`
- Hesap değeri: 117,091 USD · lider tablosu tüm zaman PnL 214,590 USD, ROI %116 · aylık ROI %5.1
- Okunan fill: 8850 (ilk: 2025-11-04)
- Kapanmış işlem: 252 · kârlı ay oranı: 75% · Sortino 3.28 · Calmar 10.87
- En büyük işlemin kâr payı: 6% · en iyi işlem çıkınca PF 2.36
- Medyan tutma: 5.6 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 0.21003448574378816/1.0417275742055527
- Martingale işareti: yok (zarara ekleme oranı 18%, 1373 ekleme)
- Coin dağılımı (fill sayısıyla): HYPE %69, LIT %16, ZEC %8, xyz:PURRDAT %4, xyz:SPCX %1
- Varlık sınıfı (hacim): kripto %97, hisse %2, emtia %1, spot %0
- Açık pozisyon: 0
- **Kural sonucu: aday**

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2025-11 | 14,896 |
| 2025-12 | -1,835 |
| 2026-01 | 7,703 |
| 2026-02 | 10,735 |
| 2026-03 | 4,376 |
| 2026-04 | 3,133 |
| 2026-05 | -2,508 |
| 2026-06 | 14,120 |
| 2026-07 | 3,437 |
| 2026-08 | 9,186 |
| 2026-09 | -2,266 |
| 2026-10 | 6,093 |

## `0xbcd4071d023bf2aae484d724c130b5af6f0ca0d2`
- Hesap değeri: 172,742 USD · lider tablosu tüm zaman PnL 257,212 USD, ROI %59 · aylık ROI %66.2
- Okunan fill: 13 (ilk: 2026-03-03)
- Kapanmış işlem: 0 · kârlı ay oranı: nan% · Sortino nan · Calmar nan
- En büyük işlemin kâr payı: nan% · en iyi işlem çıkınca PF nan
- Medyan tutma: nan saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: nan/nan
- Martingale işareti: yok (zarara ekleme oranı nan%, 0 ekleme)
- Coin dağılımı (fill sayısıyla): @230 %100
- Varlık sınıfı (hacim): spot %100
- Açık pozisyon: 0
- **Kural sonucu: yetersiz** — history_days<180,closed_trades<50

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|

## `0x4d5f00be06f2b553738dc6f01bfa5f90601de925`
- Hesap değeri: 158,054 USD · lider tablosu tüm zaman PnL 149,462 USD, ROI %149 · aylık ROI %1.0
- Okunan fill: 12757 (ilk: 2025-10-28) — API sınırı (10.000) dolmuş olabilir
- Kapanmış işlem: 254 · kârlı ay oranı: 92% · Sortino 9.38 · Calmar 54.59
- En büyük işlemin kâr payı: 9% · en iyi işlem çıkınca PF 7.67
- Medyan tutma: 0.0 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 0.5586927778248258/4.217560239914597
- Martingale işareti: yok (zarara ekleme oranı 9%, 562 ekleme)
- Coin dağılımı (fill sayısıyla): @260 %32, @156 %5, @188 %5, para:TOTAL2 %5, flx:XMR %4
- Varlık sınıfı (hacim): hisse %37, spot %31, kripto %25, emtia %6
- Açık pozisyon: 0
- **Kural sonucu: elendi** — median_holding_hours>=1.0,liquid_coin_share>=0.8

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2025-10 | 1,568 |
| 2025-11 | 9,375 |
| 2025-12 | 1,182 |
| 2026-01 | 12,154 |
| 2026-02 | 429 |
| 2026-03 | 3,253 |
| 2026-04 | 29,863 |
| 2026-05 | 984 |
| 2026-06 | -411 |
| 2026-07 | 209 |
| 2026-08 | 2,006 |
| 2026-09 | 773 |
| 2026-10 | 772 |

## `0x249161f12ffea65f52f3b3c56592c92676357448`
- Hesap değeri: 144,390 USD · lider tablosu tüm zaman PnL 101,068 USD, ROI %197 · aylık ROI %3.0
- Okunan fill: 11374 (ilk: 2026-01-06) — API sınırı (10.000) dolmuş olabilir
- Kapanmış işlem: 759 · kârlı ay oranı: 100% · Sortino 9.54 · Calmar 50.36
- En büyük işlemin kâr payı: 2% · en iyi işlem çıkınca PF 3.42
- Medyan tutma: 0.0 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 1.0170925902883647/5.865746038941055
- Martingale işareti: yok (zarara ekleme oranı 9%, 221 ekleme)
- Coin dağılımı (fill sayısıyla): xyz:CL %5, xyz:CBRS %3, CASHCAT %3, PUMP %3, xyz:NVDA %3
- Varlık sınıfı (hacim): hisse %44, emtia %22, endeks %20, kripto %13, spot %2
- Açık pozisyon: 0
- **Kural sonucu: elendi** — median_holding_hours>=1.0,liquid_coin_share>=0.8

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2026-01 | 2,698 |
| 2026-02 | 2,711 |
| 2026-03 | 16,035 |
| 2026-04 | 7,820 |
| 2026-05 | 16,761 |
| 2026-06 | 19,364 |
| 2026-07 | 4,956 |
| 2026-08 | 9,968 |
| 2026-09 | 7,780 |
| 2026-10 | 3,608 |

## `0x6809111be108b5f2fc57ac50799039af8ee14f8f`
- Hesap değeri: 137,943 USD · lider tablosu tüm zaman PnL 85,132 USD, ROI %89 · aylık ROI %2.2
- Okunan fill: 14874 (ilk: 2025-11-23) — API sınırı (10.000) dolmuş olabilir
- Kapanmış işlem: 1220 · kârlı ay oranı: 100% · Sortino 5.38 · Calmar 17.32
- En büyük işlemin kâr payı: 5% · en iyi işlem çıkınca PF 2.07
- Medyan tutma: 0.0 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 1.2356326872081655/2.993134808124476
- Martingale işareti: yok (zarara ekleme oranı 10%, 1095 ekleme)
- Coin dağılımı (fill sayısıyla): xyz:CL %10, CASHCAT %8, PURR %5, HYPE %5, LIT %4
- Varlık sınıfı (hacim): emtia %39, kripto %37, hisse %21, endeks %3, spot %1
- Açık pozisyon: 1
- **Kural sonucu: elendi** — median_holding_hours>=1.0,liquid_coin_share>=0.8

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2025-11 | 394 |
| 2025-12 | 353 |
| 2026-01 | 2,109 |
| 2026-02 | 2,055 |
| 2026-03 | 6,058 |
| 2026-04 | 13,241 |
| 2026-05 | 6,201 |
| 2026-06 | 16,835 |
| 2026-07 | 12,019 |
| 2026-08 | 8,061 |
| 2026-09 | 2,524 |
| 2026-10 | 1,633 |

## `0xc9186f29695cfe18b79e6a8ebf1be13905cac077`
- Hesap değeri: 507,855 USD · lider tablosu tüm zaman PnL 307,344 USD, ROI %139 · aylık ROI %1.3
- Okunan fill: 20000 (ilk: 2026-05-01) — API sınırı (10.000) dolmuş olabilir
- Kapanmış işlem: 551 · kârlı ay oranı: 82% · Sortino 1.40 · Calmar 5.44
- En büyük işlemin kâr payı: 13% · en iyi işlem çıkınca PF 1.70
- Medyan tutma: 0.0 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 0.342745666351205/4.744477050245955
- Martingale işareti: yok (zarara ekleme oranı 21%, 61 ekleme)
- Coin dağılımı (fill sayısıyla): ZEC %17, WLD %14, NEAR %8, ZRO %7, CRV %7
- Varlık sınıfı (hacim): kripto %100, hisse %0, spot %0
- Açık pozisyon: 0
- **Kural sonucu: yetersiz** — history_days<180

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2025-11 | 10 |
| 2025-12 | 1 |
| 2026-01 | -6 |
| 2026-02 | 0 |
| 2026-03 | -0 |
| 2026-04 | 54 |
| 2026-05 | 20,111 |
| 2026-06 | 19,166 |
| 2026-07 | 7,301 |
| 2026-08 | 19,503 |
| 2026-09 | 15,101 |

## `0xac5c66fbad98b49979cd1cbaa800ace76e947866`
- Hesap değeri: 115,050 USD · lider tablosu tüm zaman PnL 85,340 USD, ROI %228 · aylık ROI %2.2
- Okunan fill: 10357 (ilk: 2025-10-30) — API sınırı (10.000) dolmuş olabilir
- Kapanmış işlem: 151 · kârlı ay oranı: 92% · Sortino 5.59 · Calmar 11.34
- En büyük işlemin kâr payı: 13% · en iyi işlem çıkınca PF 8.21
- Medyan tutma: 3.1 saat · gerçek kaldıraç (pozisyon/hesap) medyan/en yüksek: 0.525015345258019/1.6264776745949256
- Martingale işareti: yok (zarara ekleme oranı 12%, 785 ekleme)
- Coin dağılımı (fill sayısıyla): HYPE %30, PUMP %28, FARTCOIN %8, CASHCAT %7, ETH %6
- Varlık sınıfı (hacim): kripto %89, emtia %6, hisse %3, spot %3
- Açık pozisyon: 0
- **Kural sonucu: elendi** — liquid_coin_share>=0.8

| Ay | Gerçekleşmiş net PnL (USD) |
|---|---:|
| 2025-11 | 4,942 |
| 2025-12 | -3,742 |
| 2026-01 | 1,150 |
| 2026-02 | 14,505 |
| 2026-03 | 2,664 |
| 2026-04 | 8,537 |
| 2026-05 | 12,390 |
| 2026-06 | 12,214 |
| 2026-07 | 10,564 |
| 2026-08 | 5,231 |
| 2026-09 | 1,100 |
| 2026-10 | 1,650 |
