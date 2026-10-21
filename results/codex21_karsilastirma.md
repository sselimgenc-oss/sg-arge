# Codex Algo 21 T1a karşılaştırması

Yüzdeler ondalık motor çıktısından biçimlendirilmiştir. PDF işlem tarihlerini yayımlamadığı için v0.3'teki >=%70 giriş tarihi örtüşmesi ölçülemez; metrikler uyumlu olsa bile satır `Geçti` sayılmaz.

## Replikasyon (baz maliyet)

| Satır | PDF getiri | Bizim getiri | PDF PF | Bizim PF | PDF işlem | Bizim işlem | Durum | Gerekçe |
|---|---:|---:|---:|---:|---:|---:|---|---|
| C01 | 72.74% | 68.08% | 2.21 | 2.04 | 489 | 449.00 | Dogrulanamaz | islem=uygun, isaret=uygun, PF=uygun; PDF islem listesi yok, giris ortusmesi olculemedi |
| C19 | 8.92% | 30.84% | 1.56 | 2.15 | 116 | 168.00 | Sapma | islem=sapma, isaret=uygun, PF=sapma; PDF islem listesi yok, giris ortusmesi olculemedi |
| C02 | 56.30% | 45.20% | 1.90 | 1.70 | 551 | 456.00 | Sapma | islem=sapma, isaret=uygun, PF=uygun; PDF islem listesi yok, giris ortusmesi olculemedi |
| C09 | 22.88% | 21.93% | 1.34 | 1.30 | 559 | 554.00 | Dogrulanamaz | islem=uygun, isaret=uygun, PF=uygun; PDF islem listesi yok, giris ortusmesi olculemedi |
| C15 | 35.61% | 23.48% | 1.98 | 1.54 | 281 | 264.00 | Dogrulanamaz | islem=uygun, isaret=uygun, PF=uygun; PDF islem listesi yok, giris ortusmesi olculemedi |
| C17 | 12.29% | 25.73% | 1.60 | 2.00 | 141 | 158.00 | Sapma | islem=uygun, isaret=uygun, PF=sapma; PDF islem listesi yok, giris ortusmesi olculemedi |

## Replikasyon ayrıntıları ve stresler

| Satır | Sharpe PDF/biz | MDD PDF/biz | OOS getiri PDF/biz | 2x getiri PDF/biz | 3x getiri PDF/biz | +1 bar PDF/biz | En iyi hariç PDF/biz | Maruziyet PDF/biz | Azami poz. PDF/biz |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C01 | 1.61 / 1.29 | -5.89% / -7.20% | 5.70% / 9.04% | 59.65% / 60.19% | 48.15% / 52.67% | 64.88% / 63.95% | 67.79% / 61.85% | 14.12% / 18.43% | 14 / 12.00 |
| C19 | 0.63 / 1.11 | -3.47% / -5.45% | 3.41% / 17.11% | 6.78% / 28.65% | 4.81% / 26.49% | 9.97% / 32.51% | 6.16% / 26.07% | 7.68% / 15.84% | 4 / 6.00 |
| C02 | 1.34 / 1.07 | -6.01% / -7.06% | 1.68% / 0.55% | 44.06% / 38.10% | 33.48% / 31.34% | 60.19% / 38.12% | 48.52% / 37.73% | 13.88% / 15.43% | 16 / 11.00 |
| C09 | 0.73 / 0.65 | -6.11% / -6.97% | 2.26% / -2.67% | 18.64% / 17.84% | 14.66% / 13.90% | 17.08% / 22.53% | 19.89% / 18.66% | 25.12% / 28.31% | 14 / 10.00 |
| C15 | 0.87 / 0.56 | -5.52% / -12.02% | 0.84% / -1.93% | 32.45% / 20.58% | 29.48% / 17.75% | 21.70% / 23.34% | 22.74% / 10.79% | 3.43% / 4.27% | 18 / 8.00 |
| C17 | 0.64 / 0.97 | -3.27% / -4.65% | 6.04% / 10.05% | 9.47% / 23.60% | 6.91% / 21.52% | 14.67% / 28.52% | 9.16% / 20.98% | 9.93% / 13.82% | 5 / 6.00 |

## Ön dönem tutma testi (baz maliyet)

| Satır | Getiri | CAGR | PF | Sharpe | MDD | İşlem | Ortalama R | Maruziyet |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C01 | 27.11% | 4.92% | 1.76 | 1.09 | -8.40% | 279.00 | 0.29 | 18.50% |
| C19 | -3.61% | -0.73% | 0.62 | -0.42 | -6.17% | 48.00 | -0.15 | 4.65% |
| C02 | 29.24% | 5.27% | 1.89 | 1.22 | -6.54% | 250.00 | 0.29 | 16.73% |
| C09 | 19.77% | 3.68% | 1.50 | 0.86 | -4.93% | 347.00 | 0.18 | 32.10% |
| C15 | 0.36% | 0.15% | 1.34 | 0.13 | -1.81% | 9.00 | 0.08 | 0.30% |
| C17 | 5.24% | 1.03% | 1.71 | 0.53 | -3.99% | 41.00 | 0.26 | 6.17% |

## Yorumlama notları

- PDF baz maliyeti belirtmediği için liderin v0.3 maliyet tablosu kullanıldı.
- BIST/ABD evrenleri güncel bileşenlerden oluşur; point-in-time üyelik ve delisted veri olmadığı için survivorship riski vardır.
- Haftalık rejim borsa/ETF için Cuma, Binance spot için Pazar UTC kapanışında tamamlanır.
- CCI 'son 10 gün negatif' ifadesi, kesişim barından önceki 10 tamamlanmış seans olarak uygulandı.
