# CT-Kapı v1.1

- Plasebo test ailesi **m = 7** (adım 1–4'ü geçen adresler; BHY bu aile üzerinde, p'si olmayan üye p = 1 sayılır); tekrar sayısı 10000
- İşlenen / evren: 8196 / 13724 (%59.7; hedef ≥ %98: ✗)
- 1. aşama (kâr eğrisi) geçti: 1108
- Veri hatası: 66
- Sınıf: Yetersiz 8011, Kaldı 182, Geçti 3

## Huni — tarza göre (geçen sayısı)

| tarz | adres | adım 1 | adım 2 | adım 3 | adım 4 | adım 5 | adım 6 | adım 7 | izleme_adayi | kopyalanabilir |
|---|---|---|---|---|---|---|---|---|---|---|
| intraday | 5 | 5 | 4 | 3 | 4 | 3 | 1 | 2 | 3 | 0 |
| swing | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 1 | 3 |
| belirsiz | 8187 | 389 | 182 | 48 | 53 | 0 | 36 | 0 | 48 | 0 |

## Katman

- yok: 8141
- izleme_adayi: 52
- kopyalanabilir: 3

## Adım 2'yi geçenler (alfa t'ye göre ilk 15)

| address | tarz | katman | genc_aday | profitable_month_ratio | max_drawdown | return_12m | closed_trades | median_holding_hours | median_leverage | kisa_islem_payi | son90_dongu | son_islem_gun | gece_payi | gecikme_gun | gecikme_30dk_net | gecikme_120dk_net | gecikme_480dk_net | plasebo_p | nw_t | alfa_kiyas | bhy_q | adim3 | adim4 | adim5 | adim6 | adim7 | sinif |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x4c968a3a530f76f655e7e7010075aa63cec87de2 | nan | yok | True | 1 | 0.192 | 0.585 | 64 | 25.3 | 3.91 | nan | nan | nan | nan | nan | 0.433 | 0.468 | nan | nan | 5.35 | nan | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x4c921317a8301044a2287dfa34b18c37005b42db | nan | izleme_adayi | True | 1 | 0.168 | 0.132 | 90 | 3.18 | 0.0663 | nan | nan | nan | nan | nan | 0.116 | 0.0858 | nan | nan | 5.17 | nan | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x8bae3527e5a33fa0cf184f37bc112d071463ab6d | swing | kopyalanabilir | False | 1 | 0.114 | 2.52 | 155 | 81 | 1.44 | 0.0986 | 19 | 14.8 | 0.324 | 199 | 0.21 | 0.245 | 0.197 | 0.027 | 4.49 | BTC | 0.0817 | Geçti | Geçti | Geçti | Geçti | Geçti | Geçti |
| 0x7186d081136f6984d48bfab5dce77f4ed06bc905 | nan | yok | False | 0.769 | 0.253 | 1.69 | 599 | 0.328 | 0.438 | nan | nan | nan | nan | nan | 0.196 | 0.174 | nan | nan | 3.44 | nan | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xe5731d975d84c7222ebfd0ce8239f04ea3164e55 | nan | izleme_adayi | True | 1 | 0.196 | 1.39 | 50 | 19.6 | 2.02 | nan | nan | nan | nan | nan | 0.703 | 0.713 | nan | nan | 3.12 | nan | nan | Geçti | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x6809111be108b5f2fc57ac50799039af8ee14f8f | nan | yok | True | 1 | 0.0514 | 0.934 | 1.22e+03 | 0.00213 | 1.23 | nan | nan | nan | nan | nan | -0.027 | -0.0688 | nan | nan | 3.03 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x4e994d450c7c710ba4baeda5e249acc71f80aa1b | nan | yok | False | 0.846 | 0.0478 | 1.02 | 204 | 0.00305 | 1.94 | nan | nan | nan | nan | nan | -0.147 | -0.129 | nan | nan | 3.01 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0xa4b00205646b41142f8aadacee815a98ecd3b35c | nan | yok | False | 0.846 | 0.125 | 1.75 | 951 | 0.000988 | 6.71 | nan | nan | nan | nan | nan | -0.0936 | -0.105 | nan | nan | 3.01 | nan | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x8cbe593aa5b6fffb5254429d1812abdbd1f06959 | nan | yok | True | 1 | 0.143 | 3.51 | 344 | 0.702 | 3.23 | nan | nan | nan | nan | nan | 0.769 | 0.588 | nan | nan | 3.01 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x6bc1341f6b601a4325e076e59f852e993108020c | nan | yok | True | 0.846 | 0.235 | 1.97 | 2.88e+03 | 0.000555 | 4.7 | nan | nan | nan | nan | nan | -0.672 | -0.471 | nan | nan | 2.94 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9 | swing | kopyalanabilir | False | 0.846 | 0.205 | 0.822 | 86 | 48.1 | 1.06 | 0.119 | 27 | 3.2 | 0.476 | 198 | 0.408 | 0.367 | 0.299 | 0.0001 | 2.87 | sepet | 0.000454 | Geçti | Geçti | Geçti | Geçti | Geçti | Geçti |
| 0x3f1c0f2130158c4ff45acd214fd81b37441a9ab5 | nan | yok | False | 0.846 | 0.0428 | 1.45 | 75 | 0.192 | 1.05 | nan | nan | nan | nan | nan | -0.0647 | -0.0705 | nan | nan | 2.85 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x8f308355ce0604dd4fd872309d5761167655b07c | nan | yok | False | 0.769 | 0.0312 | 1.25 | 207 | 0.0027 | 4.29 | nan | nan | nan | nan | nan | -0.0693 | -0.07 | nan | nan | 2.82 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x6a32a55c7eb57cc6efd218e5590c10c330b0bc1c | nan | yok | False | 0.917 | 0.022 | 0.287 | 114 | 0.0286 | 0.179 | nan | nan | nan | nan | nan | 0.00278 | 0.0225 | nan | nan | 2.82 | nan | nan | Kaldı | Kaldı | Kaldı | Geçti | Yetersiz | Kaldı |
| 0x71cfa5e263e866f7961091e01ebc5a2d11616c20 | nan | yok | False | 0.769 | 0.0587 | 0.535 | 223 | 0.0464 | 0.0291 | nan | nan | nan | nan | nan | 0.000916 | 0.00709 | nan | nan | 2.74 | nan | nan | Kaldı | Geçti | Kaldı | Geçti | Yetersiz | Kaldı |

Gecikme saat başına yuvarlandı (üst sınır). Karar önerisi yok.
