# CT-Kapı v1.1

Durum: tamam (parça 24/24).

Hatalı adres: 0/92 (hata sütunu; sınıf Yetersiz).

- Plasebo test ailesi **m = 6** (adım 1–4'ü geçen adresler; BHY bu aile üzerinde, p'si olmayan üye p = 1 sayılır); tekrar sayısı 10000
- İşlenen / evren: 92 / 13748 (%0.7; hedef ≥ %98: ✗)
- 1. aşama (kâr eğrisi) geçti: 40
- Veri hatası: 0
- Sınıf: Kaldı 50, Yetersiz 42

## Huni — tarza göre (geçen sayısı)

| tarz | adres | adım 1 | adım 2 | adım 3 | adım 4 | adım 5 | adım 6 | adım 7 | izleme_adayi | kopyalanabilir |
|---|---|---|---|---|---|---|---|---|---|---|
| intraday | 15 | 15 | 10 | 5 | 6 | 0 | 0 | 0 | 5 | 0 |
| swing | 18 | 18 | 18 | 8 | 6 | 2 | 3 | 1 | 8 | 0 |
| scalp | 6 | 6 | 5 | 0 | 4 | 0 | 2 | 0 | 0 | 0 |
| belirsiz | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Katman

- yok: 79
- izleme_adayi: 13

## Dondurma (kurallar ve kod özeti)

- `kurallar.yaml` SHA-256: `67d0f2ae9110d6708311a173806b60ce471b4cce40c5ad9eb7914e90af5cab3e`
- `kapi.py` SHA-256: `c8f3b2025cd21c8724ec3ed1226f3c542f054b3f5a1aa6cb78e86baf7139d24c`
- `olcut.py` SHA-256: `18cefb2b55919bf1d65bc7364a89512664746f49507d2056897d939a0346a130`
- `defter.py` SHA-256: `4785cdf29da2464af1f3d955923a6a218e260c8aff7e3e896b590106ad4a898a`
- Aday listesi (13 adres: kopyalanabilir + izleme_adayi) özeti: `2b669b901c2df363c7e8a63f8ea49559e33dfd225833fb1f31e94b154d9713c2`

## Adım 2'yi geçenler (alfa t'ye göre ilk 15)

| address | tarz | katman | genc_aday | profitable_month_ratio | max_drawdown | return_12m | closed_trades | median_holding_hours | median_leverage | kisa_islem_payi | son90_dongu | son_islem_gun | gece_payi | gecikme_gun | gecikme_30dk_net | gecikme_120dk_net | gecikme_480dk_net | plasebo_p | nw_t | alfa_kiyas | bhy_q | adim3 | adim4 | adim5 | adim6 | adim7 | sinif |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | swing | izleme_adayi | False | 0.846 | 0.181 | 1.17 | 86 | 48.1 | 0.454 | 0.119 | 27 | 3.3 | 0.476 | 198 | 0.476 | 0.432 | 0.365 | 0.0169 | 2.89 | sepet | 0.124 | Geçti | Geçti | Geçti | Geçti | Kaldı | Kaldı |
| 0x6bc1341f6b601a4325e076e59f852e993108020c | scalp | yok | True | 0.846 | 0.126 | 8.95 | 2.88e+03 | 0.000555 | 0.00804 | 1 | 685 | 0.2 | 0.31 | 198 | -0.716 | -0.512 | -0.585 | nan | 2.52 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x84965752dc5abd206f1eeae2ff58b41e5e3c7806 | scalp | yok | True | 1 | 0.0498 | 2.34 | 463 | 0.0162 | 0.108 | 0.892 | 86 | 1.1 | 0.119 | 199 | -0.0182 | -0.0905 | -0.103 | nan | 2.41 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x398433dd94502cb28814d145a4fb8e98deba601b | swing | yok | False | 0.846 | 0.125 | 0.628 | 155 | 51.4 | 0.746 | 0.144 | 13 | 0 | 0.374 | 199 | 0.0649 | 0.0684 | 0.0131 | nan | 2.24 | sepet | nan | Yetersiz | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x9312e0a61f21affbd5be821f436f8fdf6b6f6663 | swing | izleme_adayi | True | 0.9 | 0.104 | 1.28 | 64 | 125 | 0.711 | 0.0938 | 37 | 3.3 | 0.156 | 199 | 1.13 | 1.04 | 0.949 | nan | 2.15 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x67870e072059b30eb06530cabebe2a8b50fecb04 | intraday | yok | True | 0.667 | 0.269 | 27.5 | 55 | 18 | 1.59 | 0.182 | 33 | 0.2 | 0.164 | 174 | 0.969 | 0.644 | 0.323 | nan | 1.99 | sepet | nan | Kaldı | Geçti | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0xe8681168f59af16c60c805dab7842eb75f127879 | intraday | izleme_adayi | False | 0.692 | 0.181 | 2.37 | 1.14e+03 | 4.48 | 0.042 | 0.0728 | 249 | 0.4 | 0.247 | 188 | 0.0127 | -0.0397 | -0.154 | 0.92 | 1.75 | BTC | 1 | Geçti | Geçti | Kaldı | Yetersiz | Kaldı | Kaldı |
| 0xd9d870eea60fe5ee868b4f7c8227b422c8520f2f | scalp | yok | False | 0.667 | 0.128 | 1.62 | 902 | 0.00928 | 0.0265 | 0.873 | 168 | 0.7 | 0.35 | 172 | -0.0932 | -0.101 | -0.135 | nan | 1.68 | BTC | nan | Kaldı | Geçti | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x4ba1d152409f43ad92ba358886fe94bae4f5f656 | swing | yok | False | 0.923 | 0.0848 | 0.629 | 169 | 112 | 0.286 | 0.0497 | 64 | 0.1 | 0.304 | 199 | 0.189 | 0.186 | 0.204 | nan | 1.67 | BTC | nan | Yetersiz | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x2fcb6898d5a0623de19c3691904927685014c4d8 | swing | izleme_adayi | False | 0.846 | 0.152 | 1.48 | 94 | 178 | 0.544 | 0.153 | 7 | 0.2 | 0.329 | 199 | 0.224 | 0.2 | 0.188 | nan | 1.53 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x43fa26c444767ea3b82ad2f998bc995305823a32 | swing | yok | False | 0.615 | 0.105 | 1.2 | 374 | 49 | 1.39 | 0.121 | 84 | 1.8 | 0.388 | 174 | 0.0395 | 0.0173 | -0.0194 | nan | 1.49 | sepet | nan | Yetersiz | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x909eb3d5ff0ac0df12c81f8495860cfccf1e7ea9 | swing | izleme_adayi | True | 0.727 | 0.251 | 1.02 | 60 | 64.1 | 1.54 | 0.133 | 8 | 3.3 | 0.25 | 194 | 0.367 | 0.356 | 0.301 | nan | 1.47 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x7116470134e289f7fefb0922902e28200e471447 | swing | yok | True | 0.455 | 0.11 | 0.71 | 73 | 193 | 2.19 | 0.11 | 15 | 5.5 | 0 | 199 | -0.00161 | -0.00836 | -0.00595 | nan | 1.36 | sepet | nan | Kaldı | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x7e09dfbba23d078e16f038b1ed4c558185c4be1e | intraday | izleme_adayi | False | 0.923 | 0.0727 | 0.67 | 121 | 21.3 | 0.134 | 0.0256 | 48 | 0.3 | 0.256 | 198 | 0.0627 | 0.0552 | 0.0336 | nan | 1.35 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x29754d7a9f9f344327158e2d01508efa415bd558 | swing | izleme_adayi | False | 0.615 | 0.255 | 0.795 | 71 | 43.3 | 0.175 | 0.132 | 8 | 25.5 | 0.118 | 193 | 0.036 | 0.0395 | 0.0484 | 0.555 | 1.3 | BTC | 1 | Geçti | Geçti | Kaldı | Yetersiz | Kaldı | Kaldı |

Gecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.
