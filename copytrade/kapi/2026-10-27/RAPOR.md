# CT-Kapı v1.1

Durum: tamam (parça 24/24).

Hatalı adres: 0/92 (hata sütunu; sınıf Yetersiz).

- Plasebo test ailesi **m = 6** (adım 1–4'ü geçen adresler; BHY bu aile üzerinde, p'si olmayan üye p = 1 sayılır); tekrar sayısı 10000
- İşlenen / evren: 92 / 13748 (%0.7; hedef ≥ %98: ✗)
- 1. aşama (kâr eğrisi) geçti: 58
- Veri hatası: 0
- Sınıf: Yetersiz 49, Kaldı 43

## Huni — tarza göre (geçen sayısı)

| tarz | adres | adım 1 | adım 2 | adım 3 | adım 4 | adım 5 | adım 6 | adım 7 | izleme_adayi | kopyalanabilir |
|---|---|---|---|---|---|---|---|---|---|---|
| intraday | 27 | 27 | 18 | 6 | 9 | 0 | 2 | 0 | 6 | 0 |
| swing | 24 | 24 | 21 | 10 | 7 | 2 | 4 | 1 | 10 | 0 |
| scalp | 6 | 6 | 5 | 0 | 4 | 0 | 2 | 0 | 0 | 0 |
| belirsiz | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Katman

- yok: 76
- izleme_adayi: 16

## Dondurma (kurallar ve kod özeti)

- `kurallar.yaml` SHA-256: `67844b12693291ddba1a106869a5e0d023526dd1edf01efd8e59b4404d018b8e`
- `kapi.py` SHA-256: `79b37acd66088b7f8424d0f1285bceda8276e798f634312918f0ad1028b263c1`
- `olcut.py` SHA-256: `18cefb2b55919bf1d65bc7364a89512664746f49507d2056897d939a0346a130`
- `defter.py` SHA-256: `4785cdf29da2464af1f3d955923a6a218e260c8aff7e3e896b590106ad4a898a`
- Aday listesi (16 adres: kopyalanabilir + izleme_adayi) özeti: `0558e8051cf83f7d69d8eb364ebc6d5dc144896c7df1a4215ae63b277eb1119f`

## Adım 2'yi geçenler (alfa t'ye göre ilk 15)

| address | tarz | katman | genc_aday | profitable_month_ratio | max_drawdown | return_12m | closed_trades | median_holding_hours | median_leverage | kisa_islem_payi | son90_dongu | son_islem_gun | gece_payi | gecikme_gun | gecikme_30dk_net | gecikme_120dk_net | gecikme_480dk_net | plasebo_p | nw_t | alfa_kiyas | bhy_q | adim3 | adim4 | adim5 | adim6 | adim7 | sinif |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | swing | izleme_adayi | False | 0.846 | 0.181 | 1.17 | 86 | 48.1 | 0.454 | 0.119 | 27 | 3.2 | 0.476 | 198 | 0.475 | 0.431 | 0.364 | 0.0164 | 2.89 | sepet | 0.121 | Geçti | Geçti | Geçti | Geçti | Kaldı | Kaldı |
| 0x6bc1341f6b601a4325e076e59f852e993108020c | scalp | yok | True | 0.846 | 0.126 | 8.95 | 2.88e+03 | 0.000555 | 0.00804 | 1 | 685 | 0.2 | 0.31 | 198 | -0.715 | -0.511 | -0.584 | nan | 2.53 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x378defc39d5dcdfbecd4f1673a5e228f992fc08e | intraday | izleme_adayi | False | 0.692 | 0.202 | 2.33 | 92 | 2.97 | 2.47 | 0.198 | 86 | 1.9 | 0.209 | 80.2 | 0.318 | 0.329 | 0.172 | nan | 2.5 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x84965752dc5abd206f1eeae2ff58b41e5e3c7806 | scalp | yok | True | 1 | 0.0498 | 2.34 | 463 | 0.0162 | 0.108 | 0.892 | 86 | 1.1 | 0.119 | 199 | -0.0189 | -0.0912 | -0.103 | nan | 2.41 | sepet | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x398433dd94502cb28814d145a4fb8e98deba601b | swing | yok | False | 0.846 | 0.125 | 0.627 | 155 | 51.4 | 0.741 | 0.144 | 13 | 1 | 0.374 | 199 | 0.0661 | 0.0695 | 0.0142 | nan | 2.25 | sepet | nan | Yetersiz | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x9312e0a61f21affbd5be821f436f8fdf6b6f6663 | swing | izleme_adayi | True | 0.9 | 0.104 | 1.28 | 64 | 125 | 0.711 | 0.0938 | 37 | 3.3 | 0.156 | 199 | 1.13 | 1.04 | 0.95 | nan | 2.15 | sepet | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xb3162ca43d7455be5b4f6dbf3236435b709ed894 | intraday | yok | True | 0.769 | 0.164 | 8.39 | 219 | 3.96 | 1.38 | 0.174 | 22 | 11.4 | 0.113 | 196 | 0.199 | 0.137 | 0.161 | nan | 2.08 | BTC | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x69b05701f8175c276ecd0138387a197948e240bb | swing | izleme_adayi | False | 0.769 | 0.112 | 1.83 | 88 | 65.9 | 0.817 | 0.0698 | 27 | 5.4 | 0.128 | 200 | 0.347 | 0.323 | 0.288 | 0.0549 | 2.06 | BTC | 0.269 | Geçti | Geçti | Kaldı | Geçti | Kaldı | Kaldı |
| 0x67870e072059b30eb06530cabebe2a8b50fecb04 | intraday | yok | True | 0.667 | 0.269 | 27.5 | 55 | 18 | 1.59 | 0.182 | 33 | 0.2 | 0.164 | 174 | 0.969 | 0.644 | 0.323 | nan | 1.99 | sepet | nan | Kaldı | Geçti | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x080c3c74e13ee4da56e819bf402c0b6da87b457b | intraday | izleme_adayi | True | 0.714 | 0.0154 | 0.353 | 102 | 1.02 | 0.161 | 0.235 | 48 | 14.8 | 0.196 | 199 | 0.0337 | 0.0139 | -0.00822 | nan | 1.98 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0xe8681168f59af16c60c805dab7842eb75f127879 | intraday | izleme_adayi | False | 0.692 | 0.181 | 2.37 | 1.14e+03 | 4.48 | 0.042 | 0.0728 | 249 | 0.3 | 0.247 | 188 | 0.0129 | -0.0395 | -0.154 | 0.918 | 1.75 | BTC | 1 | Geçti | Geçti | Kaldı | Yetersiz | Kaldı | Kaldı |
| 0xd9d870eea60fe5ee868b4f7c8227b422c8520f2f | scalp | yok | False | 0.667 | 0.128 | 1.62 | 902 | 0.00928 | 0.0265 | 0.873 | 168 | 0.6 | 0.35 | 172 | -0.0932 | -0.101 | -0.135 | nan | 1.68 | BTC | nan | Kaldı | Geçti | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x4ba1d152409f43ad92ba358886fe94bae4f5f656 | swing | yok | False | 0.923 | 0.0848 | 0.629 | 169 | 112 | 0.286 | 0.0497 | 64 | 0.1 | 0.304 | 199 | 0.188 | 0.186 | 0.203 | nan | 1.66 | BTC | nan | Yetersiz | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x79bf662bb50bea267adf5499f730d2488d85411f | intraday | yok | False | 0.769 | 0.157 | 0.309 | 135 | 14.5 | 0.713 | 0.0821 | 45 | 0 | 0.254 | 199 | 0.116 | 0.141 | 0.192 | nan | 1.57 | BTC | nan | Yetersiz | Geçti | Kaldı | Yetersiz | Yetersiz | Kaldı |
| 0x353bd2e5da5f01707dfad0dd86907561ac66cc38 | swing | izleme_adayi | False | 0.462 | 0.107 | 0.383 | 99 | 29.8 | 0.595 | 0.0938 | 17 | 5.4 | 0.271 | 196 | 0.163 | 0.158 | 0.15 | nan | 1.54 | BTC | nan | Geçti | Kaldı | Kaldı | Yetersiz | Yetersiz | Kaldı |

Gecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.
