# Asama 2b tam dogrulama (T6b/T24)

OOS, on donem, 2x/3x/+1 bar stres, kaynak merkezli parametre platosu, 20 gunluk block bootstrap ve DSR birlikte raporlanir.
DSR paper trading icin bilgi; canliya geciste kotumser (5N) deger icin 0,95 kapisi uygulanir.

Satir: 39 | Kosullu: 9 | Reddedildi: 30

| ID | Piyasa | OOS islem/ortR | 2x PF | 3x net | +1 net | Plato + | Boot MDD95 | DSR 5N | Karar | Gerekce |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| C01 | BIST30 | 92/-0.015 | 1.14 | 3.2% | 12.4% | 100% | 23.1% | 0.008 | Reddedildi | null, OOS ortR<=0, 2x PF<1.2, bootstrap MDD>%15 |
| C02 | BIST30 | 101/-0.035 | 1.46 | 15.5% | 18.5% | 100% | 16.3% | 0.078 | Reddedildi | null, OOS ortR<=0, bootstrap MDD>%15 |
| C03 | BIST30 | 126/-0.111 | 1.30 | 8.8% | 18.8% | 100% | 14.6% | 0.077 | Reddedildi | null, OOS ortR<=0 |
| C04 | BIST30 | 23/-0.143 | 2.57 | 14.3% | 15.6% | 96% | 6.3% | 0.299 | Kosullu | on donem negatif, OOS ornek<30, survivorship yanliligi |
| C05 | BIST30 | 43/0.261 | 0.61 | -12.4% | -8.1% | 32% | 21.2% | 0.000 | Reddedildi | null, 2x PF<1.2, 3x net<=0, +1 bar net<=0, plato<%60, bootstrap MDD>%15 |
| C06 | BIST30 | 34/0.030 | 1.05 | -0.9% | 2.9% | 100% | 7.2% | 0.004 | Reddedildi | null, 2x PF<1.2, 3x net<=0 |
| C07 | ABD25 | 94/0.194 | 2.32 | 36.9% | 37.1% | 100% | 9.3% | 0.379 | Kosullu | survivorship yanliligi |
| C08 | ABD25 | 369/0.023 | 1.40 | 18.5% | 23.6% | 100% | 14.9% | 0.088 | Reddedildi | nan |
| C09 | ABD25 | 184/-0.013 | 1.51 | 19.7% | 23.0% | 100% | 11.6% | 0.148 | Reddedildi | null, OOS ortR<=0 |
| C10 | ABD25 | 192/0.012 | 1.82 | 34.2% | 37.7% | 100% | 10.1% | 0.382 | Reddedildi | nan |
| C11 | ABD25 | 205/0.049 | 1.78 | 35.4% | 32.7% | 100% | 11.8% | 0.330 | Reddedildi | nan |
| C12 | ABD25 | 51/0.071 | 1.52 | 8.1% | 10.0% | 92% | 8.1% | 0.047 | Reddedildi | nan |
| C13 | ABD25 | 95/-0.020 | 0.95 | -3.6% | 5.1% | 76% | 11.5% | 0.001 | Reddedildi | null, OOS ortR<=0, 2x PF<1.2, 3x net<=0 |
| C14 | KRIPTO25 | 60/0.177 | 1.99 | 32.4% | 34.5% | 100% | 14.6% | 0.147 | Reddedildi | nan |
| C15 | KRIPTO25 | 73/-0.089 | 1.80 | 23.0% | 26.5% | 100% | 14.4% | 0.073 | Reddedildi | null, OOS ortR<=0 |
| C16 | EMTIA | 143/0.174 | 1.22 | 4.3% | 12.0% | 100% | 11.8% | 0.016 | Reddedildi | nan |
| C17 | EMTIA | 56/0.370 | 1.76 | 11.7% | 15.2% | 100% | 7.8% | 0.092 | Reddedildi | nan |
| C18 | EMTIA | 58/0.326 | 1.44 | 7.1% | 9.4% | 100% | 9.4% | 0.025 | Reddedildi | nan |
| C19 | EMTIA | 67/0.489 | 1.57 | 9.4% | 12.4% | 100% | 8.2% | 0.057 | Reddedildi | nan |
| C20 | EMTIA | 70/0.266 | 1.24 | 3.9% | 6.9% | 100% | 12.1% | 0.007 | Reddedildi | nan |
| C21 | EMTIA | 30/0.518 | 1.35 | 3.6% | 3.4% | 100% | 9.2% | 0.007 | Reddedildi | nan |
| A6-010 | EMTIA | 150/0.104 | 1.28 | 6.7% | 2.7% | 88% | 10.6% | 0.030 | Kosullu | on donem negatif |
| P3-011 | KRIPTO25 | 169/-0.112 | 1.66 | 50.9% | 61.6% | 100% | 14.6% | 0.395 | Reddedildi | OOS ortR<=0 |
| R01 | ABD25 | 110/0.133 | 1.89 | 38.9% | 26.9% | 100% | 9.4% | 0.367 | Kosullu | survivorship yanliligi |
| G007 | KRIPTO25 | 129/-0.027 | 1.26 | -1.0% | 7.0% | 100% | 3.5% | 0.090 | Reddedildi | OOS ortR<=0, 3x net<=0 |
| G011 | ABD25 | 194/0.051 | 1.66 | 19.7% | 26.0% | 88% | 7.8% | 0.243 | Kosullu | survivorship yanliligi |
| M015 | ABD25 | 130/0.038 | 1.28 | 2.7% | 7.8% | 100% | 5.6% | 0.021 | Kosullu | on donem negatif, survivorship yanliligi |
| M038 | ABD25 | 620/0.072 | 1.31 | 16.4% | 33.0% | 100% | 10.3% | 0.407 | Kosullu | survivorship yanliligi |
| O3-003 | ABD25 | 279/0.050 | 1.12 | -4.0% | 15.5% | 100% | 6.5% | 0.089 | Reddedildi | 2x PF<1.2, 3x net<=0 |
| A4-002 | ABD25 | 17/0.248 | 2.61 | 1548.0% | 2027.9% | 100% | 91.6% | 0.200 | Reddedildi | bootstrap MDD>%15 |
| A6-004 | ABD25 | 273/0.071 | 1.68 | 43.1% | 27.5% | 100% | 15.8% | 0.250 | Reddedildi | bootstrap MDD>%15 |
| M017 | ABD25 | 445/0.155 | 1.40 | 79.7% | 92.1% | 100% | 29.5% | 0.298 | Reddedildi | bootstrap MDD>%15 |
| M020a | ABD25 | 43/-0.074 | 2.66 | 231.5% | 210.9% | 92% | 53.6% | 0.127 | Reddedildi | OOS ortR<=0, bootstrap MDD>%15 |
| M020a | KRIPTO25 | 28/0.191 | 1.30 | 335.0% | 475.1% | 100% | 85.4% | 0.072 | Reddedildi | bootstrap MDD>%15 |
| O2-025 | ABD25 | 46/0.506 | 2.11 | 20792.7% | 6807.4% | 100% | 85.0% | 0.794 | Reddedildi | bootstrap MDD>%15 |
| O2-027 | ABD25 | 33/0.369 | 2.03 | 13103.0% | 3087.0% | 100% | 81.9% | 0.718 | Reddedildi | bootstrap MDD>%15 |
| O1-004 | EMTIA | 652/0.042 | 1.10 | -2.1% | 12.1% | 67% | 15.4% | 0.024 | Reddedildi | 2x PF<1.2, 3x net<=0, bootstrap MDD>%15 |
| T8-07 | EMTIA | 212/0.068 | 1.46 | 6.1% | 9.7% | 100% | 7.9% | 0.106 | Kosullu | on donem yok |
| V2B | EMTIA | 718/0.006 | 1.33 | 1.4% | 14.3% | 100% | 8.3% | 0.091 | Kosullu | on donem yok |

## Yontem notlari

- Rotasyon kartlari (T23, `metrik: PF+CAGR`): ortR yerine CAGR; `oos_ort_r`/`on_ort_r` sutunlari donem CAGR'i tasir. Asama 2'de dolum ertesi acilistir (Composer kartlarinin kapanis dolumu yalniz Asama 1 bilgisidir). Plato: `rotasyon:` blogu ve kullandigi gostergelerin her sayisal parametresi (pencere, esik, N) tek tek +-%20; hucre = PF>1 ve getiri>0. `evren: enstruman` = adli ETF'ler (survivorship notu yok).
- BIST fiyatlari USDTRY ile ayni gun USD'ye cevrilir.
- Plato merkezleri kaynak sinyal degerleridir; en iyi hucre secilmez ve stratejiye geri yazilmaz.
- DSR N = kaynak denemesi (yoksa 1) + tarama.csv satirlari + 21 Codex satiri.
- Gun ici platoda her sayisal parametre merkez etrafinda tek tek -%20/+%20 denenir; stres ve plato `--isci` ile paraleldir.
- Gun ici bootstrap/DSR oncesinde ozkaynak UTC gun sonu degerlerine indirgenir; block uzunlugu 20 gundur. Gun ici DSR N tum gun ici kart-piyasa-tf tarama satirlarini kapsar.
- DSR'da denemeler arasi SR varyansi bilinmedigi icin stratejinin kendi SR standart hatasi kullanildi (yaklasim).
- BIST/ABD guncel evrenleri survivorship yanliligi nedeniyle en fazla `Kosullu` olabilir; `--evren pit` (T11) ile ABD tam, BIST 2020 sonrasi duzeltilir.
