# CT-Kapı v1.1

> **DURUM: EKSİK** — 32 parçanın yalnız 30 tanesi bitti (zaman aşımı / hata); kapsam %74.5 < hedef %98. Bu sonuç eksik koşudur; karar için kullanılmaz.

Hatalı adres: 154/10081 (hata sütunu; sınıf Yetersiz).

- Plasebo test ailesi **m = 22** (adım 1–4'ü geçen adresler; BHY bu aile üzerinde, p'si olmayan üye p = 1 sayılır); tekrar sayısı 10000
- İşlenen / evren: 10081 / 13530 (%74.5; hedef ≥ %98: ✗)
- 1. aşama (kâr eğrisi) geçti: 937
- Veri hatası: 154
- Sınıf: Yetersiz 8674, Kaldı 1406, Geçti 1

## Huni — tarza göre (geçen sayısı)

| tarz | adres | adım 1 | adım 2 | adım 3 | adım 4 | adım 5 | adım 6 | adım 7 | izleme_adayi | kopyalanabilir |
|---|---|---|---|---|---|---|---|---|---|---|
| intraday | 221 | 208 | 93 | 38 | 26 | 4 | 6 | 1 | 37 | 1 |
| swing | 287 | 268 | 81 | 31 | 17 | 6 | 6 | 1 | 31 | 0 |
| scalp | 132 | 127 | 67 | 0 | 39 | 0 | 12 | 0 | 0 | 0 |
| belirsiz | 9441 | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Katman

- yok: 10012
- izleme_adayi: 68
- kopyalanabilir: 1

## Dondurma (kurallar ve kod özeti)

- `kurallar.yaml` SHA-256: `01ec0fb03d80810c77e6b01eb1ab4b2b883d98a3469b4f64eab12714e9392141`
- `kapi.py` SHA-256: `b5e301c617386922bc8fd4512ed3e9c12fd89978ce30a3327d7dd9f4d5195fe5`
- `olcut.py` SHA-256: `fc6d1923aad8e25a643a5f27861b1a8d8c186d9b90f2090f0b29b5cc24ee98c4`
- `defter.py` SHA-256: `657a569b535798217a1ea6d5c93b3685aa91c2aab5d23f97786a9ceb151bfb1a`
- Aday listesi (69 adres: kopyalanabilir + izleme_adayi) özeti: `d96e0b15ae05214f2d5ea8e8d363b461380c4832d4b33a7b54686b37c1c196f7`

## Adım 2'yi geçenler (alfa t'ye göre ilk 15)

| address | tarz | katman | genc_aday | profitable_month_ratio | max_drawdown | return_12m | closed_trades | median_holding_hours | median_leverage | kisa_islem_payi | son90_dongu | son_islem_gun | gece_payi | gecikme_gun | gecikme_30dk_net | gecikme_120dk_net | gecikme_480dk_net | plasebo_p | nw_t | alfa_kiyas | bhy_q | adim3 | adim4 | adim5 | adim6 | adim7 | sinif |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x618d69438f6c5785a72d0024a8cb73b81c356e34 | scalp | yok | False | 1 | 0.0368 | 24.4 | 1.33e+03 | 0.329 | 0.337 | 0.453 | 223 | 0.1 | 0.549 | 199 | 0.0517 | 0.0134 | -0.0692 | nan | 4.19 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4ac1d48fe393ac94e7f9480af8abd9360abf48a | scalp | yok | False | 0.923 | 0.0288 | 0.387 | 1.58e+03 | 0.014 | 0.454 | 0.726 | 396 | 1.3 | 0.304 | 200 | -0.0524 | -0.113 | -0.0797 | nan | 3.72 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4178e3b8d7799cd472ceeb63b302b4a1344da19 | scalp | yok | False | 0.923 | 0.0362 | 1.62 | 649 | 0.00477 | 0.0839 | 0.966 | 167 | 1.4 | 0.468 | 197 | -0.112 | -0.073 | -0.0784 | nan | 3.55 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x8bae3527e5a33fa0cf184f37bc112d071463ab6d | swing | yok | False | 1 | 0.0842 | 18.1 | 155 | 81 | 0.549 | 0.0986 | 19 | 15.6 | 0.324 | 200 | 0.109 | 0.131 | 0.0928 | nan | 3.45 | BTC | nan | Yetersiz | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x6809111be108b5f2fc57ac50799039af8ee14f8f | scalp | yok | True | 1 | 0.0636 | 2.14 | 1.22e+03 | 0.00214 | 0.205 | 0.89 | 342 | 0.7 | 0.341 | 200 | -0.000765 | -0.0857 | -0.121 | nan | 3.12 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4b00205646b41142f8aadacee815a98ecd3b35c | scalp | yok | False | 0.846 | 0.111 | 12.9 | 943 | 0.000984 | 0.169 | 0.967 | 141 | 1.2 | 0.26 | 200 | -0.0912 | -0.106 | -0.197 | nan | 3.01 | sepet | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | swing | izleme_adayi | False | 0.846 | 0.181 | 1.19 | 86 | 48.1 | 0.454 | 0.119 | 27 | 3.9 | 0.476 | 199 | 0.556 | 0.509 | 0.435 | 0.0175 | 2.92 | sepet | 0.385 | Geçti | Geçti | Geçti | Geçti | Kaldı | Kaldı |
| 0x2312171890250347dbf1b082bdf7950504909e92 | swing | yok | False | 0.385 | 0.28 | 0.205 | 166 | 80.3 | 0.7 | 0.0798 | 45 | 4.2 | 0.0613 | 198 | 0.484 | 0.414 | 0.331 | nan | 2.67 | BTC | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x378defc39d5dcdfbecd4f1673a5e228f992fc08e | intraday | izleme_adayi | False | 0.692 | 0.202 | 2.33 | 92 | 2.97 | 2.47 | 0.198 | 86 | 2.7 | 0.209 | 80.9 | 0.387 | 0.397 | 0.197 | nan | 2.57 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xba939edf38c0ae0cc689c98b492e0535f43e4550 | swing | izleme_adayi | False | 0.846 | 0.107 | 0.153 | 175 | 53.3 | 0.159 | 0.076 | 50 | 1.7 | 0.444 | 200 | 0.105 | 0.0959 | 0.0937 | 0.0358 | 2.51 | BTC | 0.385 | Geçti | Geçti | Geçti | Geçti | Kaldı | Kaldı |
| 0xbd7b48a5f74fec74643899795b6964a8fac7e69a | scalp | yok | True | 0.7 | 0.0727 | 4.2 | 1.92e+03 | 0.00388 | 0.223 | 0.907 | 818 | 0.8 | 0.215 | 176 | -0.442 | -0.533 | -0.419 | nan | 2.5 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x398433dd94502cb28814d145a4fb8e98deba601b | swing | yok | False | 0.846 | 0.125 | 0.63 | 156 | 53.6 | 0.746 | 0.143 | 14 | 0.6 | 0.379 | 200 | 0.1 | 0.106 | 0.0403 | nan | 2.41 | sepet | nan | Yetersiz | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xb3162ca43d7455be5b4f6dbf3236435b709ed894 | intraday | yok | True | 0.769 | 0.164 | 8.34 | 219 | 3.96 | 1.38 | 0.174 | 22 | 12.1 | 0.113 | 197 | 0.453 | 0.364 | 0.412 | nan | 2.36 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x2604fe9dcc6b2df2c68ad45380bd6f908d412436 | scalp | yok | True | 0.875 | 0.0183 | 3.11 | 160 | 0.0864 | 0.194 | 0.6 | 31 | 1.9 | 0.219 | 200 | 0.149 | 0.141 | -0.0553 | nan | 2.33 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x987163b6b482c30c2f5f3aa2760109668eb0091d | scalp | yok | False | 0.538 | 0.179 | 1.19 | 141 | 0.548 | 8.55 | 0.397 | 31 | 1.7 | 0.214 | 197 | 1.57 | 1.64 | 1.55 | nan | 2.3 | BTC | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |

Gecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.
