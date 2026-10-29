# CT-Kapı v1.1

Durum: tamam (parça 32/32).

Hatalı adres: 221/15131 (hata sütunu; sınıf Yetersiz).

- Plasebo test ailesi **m = 26** (adım 1–4'ü geçen adresler; BHY bu aile üzerinde, p'si olmayan üye p = 1 sayılır); tekrar sayısı 10000
- İşlenen / evren: 15131 / 14684 (%103.0; hedef ≥ %98: ✓)
- 1. aşama (kâr eğrisi) geçti: 1353
- Veri hatası: 221
- Sınıf: Yetersiz 13179, Kaldı 1951, Geçti 1

## Huni — tarza göre (geçen sayısı)

| tarz | adres | adım 1 | adım 2 | adım 3 | adım 4 | adım 5 | adım 6 | adım 7 | izleme_adayi | kopyalanabilir |
|---|---|---|---|---|---|---|---|---|---|---|
| intraday | 310 | 292 | 139 | 49 | 40 | 4 | 9 | 1 | 48 | 1 |
| swing | 399 | 373 | 102 | 42 | 22 | 6 | 7 | 1 | 42 | 0 |
| scalp | 208 | 198 | 104 | 0 | 61 | 0 | 18 | 0 | 0 | 0 |
| belirsiz | 14214 | 40 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Katman

- yok: 15040
- izleme_adayi: 90
- kopyalanabilir: 1

## Dondurma (kurallar ve kod özeti)

- `kurallar.yaml` SHA-256: `8319f56be91036a27503092bd2cb432f56c09152ce70ebe7f55a670a7536d794`
- `kapi.py` SHA-256: `a0a0bd8aaa3a8cf5d5d52e16b37a1d1d511e4c849f7883804295b1c198fbde6d`
- `olcut.py` SHA-256: `fc6d1923aad8e25a643a5f27861b1a8d8c186d9b90f2090f0b29b5cc24ee98c4`
- `defter.py` SHA-256: `6f13ede90f23f536b4f505d3a9338f1bae9aca6dd92b46c579704818c33f96a3`
- Aday listesi (91 adres: kopyalanabilir + izleme_adayi) özeti: `ffcd61ef3c6fd3eed05bd39dbbafb142fc11c59cae76e1fa1bd87a64b31fe581`

## Adım 2'yi geçenler (alfa t'ye göre ilk 15)

| address | tarz | katman | genc_aday | profitable_month_ratio | max_drawdown | return_12m | closed_trades | median_holding_hours | median_leverage | kisa_islem_payi | son90_dongu | son_islem_gun | gece_payi | gecikme_gun | gecikme_30dk_net | gecikme_120dk_net | gecikme_480dk_net | plasebo_p | nw_t | alfa_kiyas | bhy_q | adim3 | adim4 | adim5 | adim6 | adim7 | sinif |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x31dea2516beee92135b96f464eeec3cf292a13f2 | scalp | yok | False | 1 | 0.0569 | 0.653 | 63 | 0.208 | 0.114 | 0.545 | 63 | -0 | 0.145 | 0.7 | -0.00111 | -0.002 | -0.000597 | nan | 5.8 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x618d69438f6c5785a72d0024a8cb73b81c356e34 | scalp | yok | False | 1 | 0.0368 | 24.4 | 1.33e+03 | 0.329 | 0.337 | 0.453 | 223 | 0.1 | 0.549 | 199 | 0.0517 | 0.0134 | -0.0692 | nan | 4.19 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4ac1d48fe393ac94e7f9480af8abd9360abf48a | scalp | yok | False | 0.923 | 0.0288 | 0.387 | 1.58e+03 | 0.014 | 0.454 | 0.726 | 396 | 1.3 | 0.304 | 200 | -0.0524 | -0.113 | -0.0797 | nan | 3.72 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4178e3b8d7799cd472ceeb63b302b4a1344da19 | scalp | yok | False | 0.923 | 0.0362 | 1.62 | 649 | 0.00477 | 0.0839 | 0.966 | 167 | 1.4 | 0.468 | 197 | -0.112 | -0.073 | -0.0784 | nan | 3.55 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x8bae3527e5a33fa0cf184f37bc112d071463ab6d | swing | yok | False | 1 | 0.0842 | 18.1 | 155 | 81 | 0.549 | 0.0986 | 19 | 15.6 | 0.324 | 200 | 0.109 | 0.131 | 0.0928 | nan | 3.45 | BTC | nan | Yetersiz | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xac5c66fbad98b49979cd1cbaa800ace76e947866 | intraday | yok | False | 0.917 | 0.153 | 2.82 | 151 | 3.06 | 3.55e-05 | 0.245 | 29 | 2.7 | 0.278 | 200 | 0.172 | 0.0728 | 0.0557 | nan | 3.22 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x6809111be108b5f2fc57ac50799039af8ee14f8f | scalp | yok | True | 1 | 0.0636 | 2.14 | 1.22e+03 | 0.00214 | 0.205 | 0.89 | 342 | 0.7 | 0.341 | 200 | -0.000765 | -0.0857 | -0.121 | nan | 3.12 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4b00205646b41142f8aadacee815a98ecd3b35c | scalp | yok | False | 0.846 | 0.111 | 12.9 | 943 | 0.000984 | 0.169 | 0.967 | 141 | 1.2 | 0.26 | 200 | -0.0912 | -0.106 | -0.197 | nan | 3.01 | sepet | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xf97ad6704baec104d00b88e0c157e2b7b3a1ddd1 | intraday | izleme_adayi | False | 0.923 | 0.186 | 1.64 | 701 | 9.19 | 0.27 | 0.0858 | 296 | 0.1 | 0.192 | 200 | 0.307 | 0.32 | 0.201 | nan | 3.01 | BTC | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | swing | izleme_adayi | False | 0.846 | 0.181 | 1.19 | 86 | 48.1 | 0.454 | 0.119 | 27 | 3.9 | 0.476 | 199 | 0.556 | 0.509 | 0.435 | 0.0175 | 2.92 | sepet | 0.475 | Geçti | Geçti | Geçti | Geçti | Kaldı | Kaldı |
| 0xa046c1c83a3b295ca99bb9efdd19836b12409373 | scalp | yok | False | 0.538 | 0.0477 | 33.9 | 221 | 0.0243 | 0.119 | 0.882 | 221 | 0.5 | 0.0588 | 62 | -0.061 | -0.0173 | -0.11 | nan | 2.92 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x8f308355ce0604dd4fd872309d5761167655b07c | scalp | yok | False | 0.75 | 0.0375 | 1.53 | 211 | 0.00268 | 0.0549 | 0.991 | 124 | 0 | 0.265 | 199 | -0.0916 | -0.0926 | -0.0921 | nan | 2.74 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x2312171890250347dbf1b082bdf7950504909e92 | swing | yok | False | 0.385 | 0.28 | 0.205 | 166 | 80.3 | 0.7 | 0.0798 | 45 | 4.2 | 0.0613 | 198 | 0.484 | 0.414 | 0.331 | nan | 2.67 | BTC | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x6177b5bf3aa32a9c3a962c7a5197c5d9a5433b00 | intraday | yok | False | 0.923 | 0.0527 | 2.07 | 112 | 3.91 | 2.3 | 0.284 | 23 | 1.5 | 0.229 | 200 | 0.139 | 0.14 | 0.18 | nan | 2.6 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x378defc39d5dcdfbecd4f1673a5e228f992fc08e | intraday | izleme_adayi | False | 0.692 | 0.202 | 2.33 | 92 | 2.97 | 2.47 | 0.198 | 86 | 2.7 | 0.209 | 80.9 | 0.387 | 0.397 | 0.197 | nan | 2.57 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |

Gecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.
