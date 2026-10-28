# CT-Kapı v1.1

Durum: tamam (parça 24/24).

Hatalı adres: 4/92 (hata sütunu; sınıf Yetersiz).

- Plasebo test ailesi **m = 9** (adım 1–4'ü geçen adresler; BHY bu aile üzerinde, p'si olmayan üye p = 1 sayılır); tekrar sayısı 10000
- İşlenen / evren: 92 / 13627 (%0.7; hedef ≥ %98: ✗)
- 1. aşama (kâr eğrisi) geçti: 56
- Veri hatası: 4
- Sınıf: Yetersiz 50, Kaldı 42

## Huni — tarza göre (geçen sayısı)

| tarz | adres | adım 1 | adım 2 | adım 3 | adım 4 | adım 5 | adım 6 | adım 7 | izleme_adayi | kopyalanabilir |
|---|---|---|---|---|---|---|---|---|---|---|
| intraday | 24 | 24 | 17 | 9 | 8 | 0 | 3 | 0 | 9 | 0 |
| swing | 23 | 23 | 21 | 10 | 7 | 3 | 4 | 1 | 10 | 0 |
| scalp | 4 | 4 | 3 | 0 | 2 | 0 | 1 | 0 | 0 | 0 |
| belirsiz | 41 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Katman

- yok: 73
- izleme_adayi: 19

## Dondurma (kurallar ve kod özeti)

- `kurallar.yaml` SHA-256: `564878f4dd907da7ad6ac78cfd7f97e0e2701d5c2dd1e82e772f4b75425705f5`
- `kapi.py` SHA-256: `1568e92afd5138291d861cd621a6da39ad209a13242f5bf806cd4244ffcab424`
- `olcut.py` SHA-256: `fc6d1923aad8e25a643a5f27861b1a8d8c186d9b90f2090f0b29b5cc24ee98c4`
- `defter.py` SHA-256: `657a569b535798217a1ea6d5c93b3685aa91c2aab5d23f97786a9ceb151bfb1a`
- Aday listesi (19 adres: kopyalanabilir + izleme_adayi) özeti: `b30f08e1f524f3ab2add2a357884ee23569d23ad1f229c6fe922a72f24c65a87`

## Adım 2'yi geçenler (alfa t'ye göre ilk 15)

| address | tarz | katman | genc_aday | profitable_month_ratio | max_drawdown | return_12m | closed_trades | median_holding_hours | median_leverage | kisa_islem_payi | son90_dongu | son_islem_gun | gece_payi | gecikme_gun | gecikme_30dk_net | gecikme_120dk_net | gecikme_480dk_net | plasebo_p | nw_t | alfa_kiyas | bhy_q | adim3 | adim4 | adim5 | adim6 | adim7 | sinif |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x8bae3527e5a33fa0cf184f37bc112d071463ab6d | swing | yok | False | 1 | 0.0842 | 18.2 | 155 | 81 | 0.549 | 0.0986 | 19 | 15.5 | 0.324 | 200 | 0.107 | 0.13 | 0.0914 | nan | 3.44 | BTC | nan | Yetersiz | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | swing | izleme_adayi | False | 0.846 | 0.181 | 1.19 | 86 | 48.1 | 0.454 | 0.119 | 27 | 3.9 | 0.476 | 199 | 0.558 | 0.51 | 0.436 | 0.0166 | 2.91 | sepet | 0.211 | Geçti | Geçti | Geçti | Geçti | Kaldı | Kaldı |
| 0x378defc39d5dcdfbecd4f1673a5e228f992fc08e | intraday | izleme_adayi | False | 0.692 | 0.202 | 2.33 | 92 | 2.97 | 2.47 | 0.198 | 86 | 2.6 | 0.209 | 80.9 | 0.387 | 0.397 | 0.197 | nan | 2.57 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x398433dd94502cb28814d145a4fb8e98deba601b | swing | yok | False | 0.846 | 0.125 | 0.629 | 156 | 53.6 | 0.746 | 0.143 | 14 | 0.5 | 0.379 | 200 | 0.0982 | 0.104 | 0.0384 | nan | 2.38 | sepet | nan | Yetersiz | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xb3162ca43d7455be5b4f6dbf3236435b709ed894 | intraday | yok | True | 0.769 | 0.164 | 8.33 | 219 | 3.96 | 1.38 | 0.174 | 22 | 12 | 0.113 | 197 | 0.453 | 0.364 | 0.412 | nan | 2.36 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x9312e0a61f21affbd5be821f436f8fdf6b6f6663 | swing | izleme_adayi | True | 0.9 | 0.104 | 1.25 | 64 | 125 | 0.706 | 0.0938 | 37 | 3.9 | 0.156 | 200 | 0.691 | 0.643 | 0.605 | nan | 2.21 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xe8681168f59af16c60c805dab7842eb75f127879 | intraday | izleme_adayi | False | 0.692 | 0.2 | 2.29 | 1.14e+03 | 4.48 | 0.042 | 0.0728 | 244 | 1 | 0.247 | 189 | 0.00823 | -0.0408 | -0.133 | 0.926 | 2.18 | BTC | 1 | Geçti | Geçti | Kaldı | Geçti | Kaldı | Kaldı |
| 0x84965752dc5abd206f1eeae2ff58b41e5e3c7806 | scalp | yok | True | 1 | 0.0498 | 2.35 | 463 | 0.0162 | 0.112 | 0.892 | 86 | 1.8 | 0.119 | 200 | -0.361 | -0.379 | -0.272 | nan | 2.18 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x080c3c74e13ee4da56e819bf402c0b6da87b457b | intraday | izleme_adayi | True | 0.714 | 0.0154 | 0.353 | 102 | 1.02 | 0.161 | 0.235 | 48 | 15.5 | 0.196 | 200 | 0.128 | 0.0473 | -0.0459 | nan | 1.96 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x69b05701f8175c276ecd0138387a197948e240bb | swing | izleme_adayi | False | 0.769 | 0.112 | 1.83 | 88 | 65.9 | 0.817 | 0.0698 | 27 | 6 | 0.128 | 200 | 0.458 | 0.441 | 0.362 | 0.0328 | 1.92 | BTC | 0.278 | Geçti | Geçti | Geçti | Yetersiz | Kaldı | Kaldı |
| 0xd9d870eea60fe5ee868b4f7c8227b422c8520f2f | scalp | yok | False | 0.667 | 0.128 | 1.62 | 902 | 0.00928 | 0.0265 | 0.873 | 164 | 1.3 | 0.35 | 172 | -0.103 | -0.11 | -0.152 | nan | 1.68 | BTC | nan | Kaldı | Geçti | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x79bf662bb50bea267adf5499f730d2488d85411f | intraday | izleme_adayi | False | 0.769 | 0.157 | 0.316 | 134 | 13.8 | 0.713 | 0.0833 | 43 | 0.3 | 0.242 | 200 | 0.151 | 0.189 | 0.245 | 0.167 | 1.66 | BTC | 0.71 | Geçti | Geçti | Kaldı | Yetersiz | Kaldı | Kaldı |
| 0x4ba1d152409f43ad92ba358886fe94bae4f5f656 | swing | izleme_adayi | False | 0.923 | 0.0848 | 0.628 | 169 | 112 | 0.288 | 0.0497 | 64 | 0.2 | 0.304 | 200 | 0.238 | 0.236 | 0.257 | nan | 1.65 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x909eb3d5ff0ac0df12c81f8495860cfccf1e7ea9 | swing | izleme_adayi | True | 0.727 | 0.251 | 0.976 | 60 | 64.1 | 1.54 | 0.133 | 8 | 3.9 | 0.25 | 194 | 0.878 | 0.863 | 0.759 | nan | 1.64 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x2fcb6898d5a0623de19c3691904927685014c4d8 | swing | yok | False | 0.846 | 0.152 | 1.46 | 94 | 178 | 0.539 | 0.153 | 7 | 0.1 | 0.329 | 200 | 0.189 | 0.172 | 0.162 | nan | 1.53 | BTC | nan | Yetersiz | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |

Gecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.
