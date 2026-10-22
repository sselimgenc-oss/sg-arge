# Asama 2b tam dogrulama (T6b)

OOS, on donem, 2x/3x/+1 bar stres, kaynak merkezli parametre platosu, 20 gunluk block bootstrap ve DSR birlikte raporlanir.
DSR paper trading icin bilgi; canliya geciste kotumser (5N) deger icin 0,95 kapisi uygulanir.

Satir: 24 | Kosullu: 3 | Reddedildi: 21

| ID | Piyasa | OOS islem/ortR | 2x PF | 3x net | +1 net | Plato + | Boot MDD95 | DSR 5N | Karar | Gerekce |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| C01 | BIST30 | 92/-0.015 | 1.14 | 3.2% | 12.4% | 100% | 23.1% | 0.008 | Reddedildi | null, OOS ortR<=0, 2x PF<1.2, bootstrap MDD>%15 |
| C02 | BIST30 | 101/-0.035 | 1.46 | 15.5% | 18.5% | 100% | 16.3% | 0.078 | Reddedildi | null, OOS ortR<=0, bootstrap MDD>%15 |
| C03 | BIST30 | 126/-0.111 | 1.30 | 8.8% | 18.8% | 100% | 14.6% | 0.077 | Reddedildi | null, OOS ortR<=0 |
| C04 | BIST30 | 23/-0.143 | 2.57 | 14.3% | 15.6% | 96% | 6.3% | 0.299 | Kosullu | on donem negatif, OOS ornek<30, survivorship yanliligi |
| C05 | BIST30 | 43/0.261 | 0.61 | -12.4% | -8.1% | 32% | 21.2% | 0.000 | Reddedildi | null, 2x PF<1.2, 3x net<=0, +1 bar net<=0, plato<%60, bootstrap MDD>%15 |
| C06 | BIST30 | 34/0.030 | 1.05 | -0.9% | 2.9% | 100% | 7.2% | 0.004 | Reddedildi | null, 2x PF<1.2, 3x net<=0 |
| C07 | ABD25 | 94/0.194 | 2.32 | 36.9% | 37.1% | 100% | 9.3% | 0.379 | Kosullu | survivorship yanliligi |
| C08 | ABD25 | 369/0.023 | 1.40 | 18.5% | 23.6% | 100% | 14.9% | 0.088 | Reddedildi | null |
| C09 | ABD25 | 184/-0.013 | 1.51 | 19.7% | 23.0% | 100% | 11.6% | 0.148 | Reddedildi | null, OOS ortR<=0 |
| C10 | ABD25 | 192/0.012 | 1.82 | 34.2% | 37.7% | 100% | 10.1% | 0.382 | Reddedildi | null |
| C11 | ABD25 | 205/0.049 | 1.78 | 35.4% | 32.7% | 100% | 11.8% | 0.330 | Reddedildi | null |
| C12 | ABD25 | 51/0.071 | 1.52 | 8.1% | 10.0% | 92% | 8.1% | 0.047 | Reddedildi | null |
| C13 | ABD25 | 95/-0.020 | 0.95 | -3.6% | 5.1% | 76% | 11.5% | 0.001 | Reddedildi | null, OOS ortR<=0, 2x PF<1.2, 3x net<=0 |
| C14 | KRIPTO25 | 60/0.177 | 1.99 | 32.4% | 34.5% | 100% | 14.6% | 0.147 | Reddedildi | null |
| C15 | KRIPTO25 | 73/-0.089 | 1.80 | 23.0% | 26.5% | 100% | 14.4% | 0.073 | Reddedildi | null, OOS ortR<=0 |
| C16 | EMTIA | 143/0.174 | 1.22 | 4.3% | 12.0% | 100% | 11.8% | 0.016 | Reddedildi | null |
| C17 | EMTIA | 56/0.370 | 1.76 | 11.7% | 15.2% | 100% | 7.8% | 0.092 | Reddedildi | null |
| C18 | EMTIA | 58/0.326 | 1.44 | 7.1% | 9.4% | 100% | 9.4% | 0.025 | Reddedildi | null |
| C19 | EMTIA | 67/0.489 | 1.57 | 9.4% | 12.4% | 100% | 8.2% | 0.057 | Reddedildi | null |
| C20 | EMTIA | 70/0.266 | 1.24 | 3.9% | 6.9% | 100% | 12.1% | 0.007 | Reddedildi | null |
| C21 | EMTIA | 30/0.518 | 1.35 | 3.6% | 3.4% | 100% | 9.2% | 0.007 | Reddedildi | null |
| A6-010 | EMTIA | 150/0.104 | 1.28 | 6.7% | 2.7% | 88% | 10.6% | 0.030 | Kosullu | on donem negatif |
| P3-011 | KRIPTO25 | 169/-0.112 | 1.66 | 50.9% | 61.6% | 100% | 14.6% | 0.395 | Reddedildi | OOS ortR<=0 |
| R01 | nan | -/- | - | - | - | - | - | - | Reddedildi | EndeksYok: R01 |

## Yontem notlari

- BIST fiyatlari USDTRY ile ayni gun USD'ye cevrilir.
- Plato merkezleri kaynak sinyal degerleridir; en iyi hucre secilmez ve stratejiye geri yazilmaz.
- DSR N = kaynak denemesi (yoksa 1) + tarama.csv satirlari + 21 Codex satiri.
- DSR'da denemeler arasi SR varyansi bilinmedigi icin stratejinin kendi SR standart hatasi kullanildi (yaklasim).
- BIST/ABD guncel evrenleri survivorship yanliligi nedeniyle en fazla `Kosullu` olabilir.
