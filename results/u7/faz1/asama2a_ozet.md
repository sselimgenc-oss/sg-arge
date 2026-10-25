# Asama 2a: piyasa betasi testleri (T6a/T17)

BIST USD bazinda; rastgele giris (null) testi: PF ve ortalama R, null dagiliminin %95 yuzdeligini gecmeli.
Donem: gunluk ve kripto gun ici 2020-01-01 -> 2024-09-30; yfinance 1H arsivinin ilk 2/3'u (OOS ve on donem kullanilmadi).

Kart: 119 | T6b'ye gecen: 20 | elenen/dogrulanamaz: 99

## Satir sonuclari

| Kart | Piyasa | Para | Islem | PF | ortR | null PF p95 | null ortR p95 | p(PF) | p(ortR) | Tekrar | Karar |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A1-025 | ABD25 | yerel | 1470 | 1.17 | 0.015 | 1.26 | 0.023 | 0.234 | 0.269 | 200 | Reddedildi (piyasa betasi): PF p=0.234, ortR p=0.269 (esik 0.05) |
| A3-007 | BIST30 | USD | 230 | 1.52 | 0.235 | 2.09 | 0.404 | 0.393 | 0.269 | 200 | Reddedildi (piyasa betasi): PF p=0.393, ortR p=0.269 (esik 0.05) |
| A3-007 | ABD25 | yerel | 173 | 1.71 | 0.151 | 2.79 | 0.489 | 0.716 | 0.965 | 200 | Reddedildi (piyasa betasi): PF p=0.716, ortR p=0.965 (esik 0.05) |
| A3-007 | KRIPTO25 | yerel | 281 | 2.47 | 0.481 | 2.52 | 0.533 | 0.085 | 0.119 | 200 | Reddedildi (piyasa betasi): PF p=0.085, ortR p=0.119 (esik 0.05) |
| A3-007 | EMTIA | yerel | 155 | 1.19 | 0.057 | 1.83 | 0.276 | 0.806 | 0.881 | 200 | Reddedildi (piyasa betasi): PF p=0.806, ortR p=0.881 (esik 0.05) |
| A3-008a | KRIPTO25 | yerel | 57 | 2.44 | 1.270 | 6.77 | 9.301 | 0.692 | 0.483 | 200 | Reddedildi (piyasa betasi): PF p=0.692, ortR p=0.483 (esik 0.05) |
| A3-008b | BIST30 | USD | 505 | 1.18 | 0.060 | 1.40 | 0.080 | 0.373 | 0.229 | 200 | Reddedildi (piyasa betasi): PF p=0.373, ortR p=0.229 (esik 0.05) |
| A3-008b | ABD25 | yerel | 517 | 1.56 | 0.140 | 1.78 | 0.109 | 0.204 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.010 (esik 0.05) |
| A3-008b | KRIPTO25 | yerel | 595 | 1.58 | 0.139 | 1.79 | 0.121 | 0.294 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.294, ortR p=0.015 (esik 0.05) |
| A3-008b | EMTIA | yerel | 278 | 1.17 | 0.039 | 1.33 | 0.065 | 0.184 | 0.139 | 200 | Reddedildi (piyasa betasi): PF p=0.184, ortR p=0.139 (esik 0.05) |
| A3-009a | BIST30 | USD | 149 | 2.40 | 0.340 | 2.47 | 0.337 | 0.060 | 0.051 | 1000 | Reddedildi (piyasa betasi): PF p=0.060, ortR p=0.051 (esik 0.05) |
| A3-009a | ABD25 | yerel | 148 | 2.13 | 0.453 | 2.51 | 0.353 | 0.174 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.174, ortR p=0.015 (esik 0.05) |
| A3-009a | KRIPTO25 | yerel | 260 | 1.80 | 0.214 | 3.07 | 0.574 | 0.617 | 0.507 | 200 | Reddedildi (piyasa betasi): PF p=0.617, ortR p=0.507 (esik 0.05) |
| A3-009a | EMTIA | yerel | 101 | 1.25 | 0.115 | 2.62 | 0.333 | 0.905 | 0.806 | 200 | Reddedildi (piyasa betasi): PF p=0.905, ortR p=0.806 (esik 0.05) |
| A3-009b | ABD25 | yerel | 431 | 1.31 | 0.103 | 1.47 | 0.056 | 0.184 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.184, ortR p=0.005 (esik 0.05) |
| A3-009b | EMTIA | yerel | 155 | 1.43 | 0.119 | 1.58 | 0.080 | 0.154 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.154, ortR p=0.005 (esik 0.05) |
| A3-009c | BIST30 | USD | 48 | 3.76 | 1.308 | 6.84 | 2.326 | 0.194 | 0.149 | 200 | Reddedildi (piyasa betasi): PF p=0.194, ortR p=0.149 (esik 0.05) |
| A3-009c | ABD25 | yerel | 48 | 4.46 | 1.267 | 9.27 | 3.307 | 0.577 | 0.642 | 200 | Reddedildi (piyasa betasi): PF p=0.577, ortR p=0.642 (esik 0.05) |
| A3-009c | KRIPTO25 | yerel | 121 | 3.12 | 2.022 | 7.13 | 1.735 | 0.592 | 0.035 | 200 | Reddedildi (piyasa betasi): PF p=0.592, ortR p=0.035 (esik 0.05) |
| A3-009c | EMTIA | yerel | 55 | 1.50 | 0.333 | 3.87 | 0.738 | 0.826 | 0.507 | 200 | Reddedildi (piyasa betasi): PF p=0.826, ortR p=0.507 (esik 0.05) |
| A4-002 | ABD25 | yerel | 33 | 2.65 | 0.830 | 1.42 | 0.322 | 0.015 | 0.005 | 200 | Gecti (null) |
| A4-003 | ABD25 | yerel | 67 | 2.09 | 0.294 | 1.58 | 0.422 | 0.022 | 0.087 | 1000 | Reddedildi (piyasa betasi): PF p=0.022, CAGR p=0.087 (esit 0.05) |
| A4-005 | ABD25 | yerel | 49 | 0.98 | -0.003 | 5.05 | 0.435 | 0.766 | 0.761 | 200 | Reddedildi (piyasa betasi): PF p=0.766, CAGR p=0.761 (esit 0.05) |
| A5-009 | ABD25 | yerel | 1881 | 1.18 | 0.028 | 1.33 | 0.044 | 0.677 | 0.721 | 200 | Reddedildi (piyasa betasi): PF p=0.677, ortR p=0.721 (esik 0.05) |
| A6-001 | BIST30 | USD | 670 | 0.92 | -0.029 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| A6-001 | ABD25 | yerel | 847 | 1.11 | 0.036 | 1.42 | 0.064 | 0.881 | 0.567 | 200 | Reddedildi (piyasa betasi): PF p=0.881, ortR p=0.567 (esik 0.05) |
| A6-001 | EMTIA | yerel | 235 | 1.35 | 0.089 | 1.54 | 0.082 | 0.164 | 0.050 | 200 | Reddedildi (piyasa betasi): PF p=0.164, ortR p=0.050 (esik 0.05) |
| A6-003 | ABD25 | yerel | 400 | 1.29 | 0.038 | 1.39 | 0.048 | 0.184 | 0.164 | 200 | Reddedildi (piyasa betasi): PF p=0.184, ortR p=0.164 (esik 0.05) |
| A6-004 | ABD25 | yerel | 543 | 1.84 | 0.115 | 1.82 | 0.111 | 0.020 | 0.005 | 200 | Gecti (null) |
| A6-004 | KRIPTO25 | yerel | 354 | 1.34 | 0.165 | 1.35 | 0.161 | 0.070 | 0.032 | 1000 | Reddedildi (piyasa betasi): PF p=0.070, CAGR p=0.032 (esit 0.05) |
| A6-010 | BIST30 | USD | 446 | 0.99 | 0.024 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| A6-010 | ABD25 | yerel | 570 | 1.25 | 0.086 | 1.53 | 0.083 | 0.652 | 0.035 | 200 | Reddedildi (piyasa betasi): PF p=0.652, ortR p=0.035 (esik 0.05) |
| A6-010 | KRIPTO25 | yerel | 952 | 1.36 | 0.110 | 1.49 | 0.092 | 0.398 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.398, ortR p=0.010 (esik 0.05) |
| A6-010 | EMTIA | yerel | 319 | 1.38 | 0.068 | 1.27 | 0.049 | 0.020 | 0.020 | 200 | Gecti (null) |
| B1-002 | BIST30 | USD | 130 | 1.04 | 0.203 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| B1-002 | ABD25 | yerel | 116 | 2.02 | 0.603 | 3.09 | 0.598 | 0.502 | 0.055 | 200 | Reddedildi (piyasa betasi): PF p=0.502, ortR p=0.055 (esik 0.05) |
| B1-002 | KRIPTO25 | yerel | 116 | 2.49 | 0.764 | 7.33 | 13.123 | 0.542 | 0.284 | 200 | Reddedildi (piyasa betasi): PF p=0.542, ortR p=0.284 (esik 0.05) |
| B1-002 | EMTIA | yerel | 92 | 1.37 | 0.199 | 1.88 | 0.299 | 0.418 | 0.249 | 200 | Reddedildi (piyasa betasi): PF p=0.418, ortR p=0.249 (esik 0.05) |
| B3-001 | ABD25 | yerel | 1014 | 1.28 | 0.044 | 1.40 | 0.053 | 0.313 | 0.194 | 200 | Reddedildi (piyasa betasi): PF p=0.313, ortR p=0.194 (esik 0.05) |
| B3-005 | ABD25 | yerel | 351 | 1.32 | 0.068 | 1.95 | 0.152 | 0.736 | 0.756 | 200 | Reddedildi (piyasa betasi): PF p=0.736, ortR p=0.756 (esik 0.05) |
| B3-005 | KRIPTO25 | yerel | 233 | 1.62 | 0.096 | 2.21 | 0.208 | 0.393 | 0.557 | 200 | Reddedildi (piyasa betasi): PF p=0.393, ortR p=0.557 (esik 0.05) |
| B3-005 | EMTIA | yerel | 62 | 1.43 | 0.081 | 2.18 | 0.216 | 0.453 | 0.502 | 200 | Reddedildi (piyasa betasi): PF p=0.453, ortR p=0.502 (esik 0.05) |
| B3-010 | ABD25 | yerel | 756 | 1.23 | 0.040 | 1.39 | 0.040 | 0.289 | 0.060 | 200 | Reddedildi (piyasa betasi): PF p=0.289, ortR p=0.060 (esik 0.05) |
| B3-010 | EMTIA | yerel | 169 | 1.30 | 0.047 | 1.45 | 0.049 | 0.144 | 0.070 | 200 | Reddedildi (piyasa betasi): PF p=0.144, ortR p=0.070 (esik 0.05) |
| B3-014 | BIST30 | USD | 645 | 0.97 | -0.038 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| B3-014 | ABD25 | yerel | 619 | 1.17 | 0.132 | 1.48 | 0.324 | 0.821 | 0.786 | 200 | Reddedildi (piyasa betasi): PF p=0.821, CAGR p=0.786 (esit 0.05) |
| C01 | BIST30 | USD | 302 | 1.23 | 0.065 | 1.71 | 0.132 | 0.542 | 0.373 | 200 | Reddedildi (piyasa betasi): PF p=0.542, ortR p=0.373 (esik 0.05) |
| C01 | ABD25 | yerel | 376 | 1.41 | 0.162 | 1.88 | 0.177 | 0.587 | 0.085 | 200 | Reddedildi (piyasa betasi): PF p=0.587, ortR p=0.085 (esik 0.05) |
| C01 | KRIPTO25 | yerel | 231 | 2.09 | 0.241 | 2.43 | 0.193 | 0.124 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.124, ortR p=0.020 (esik 0.05) |
| C01 | EMTIA | yerel | 102 | 1.65 | 0.219 | 2.35 | 0.248 | 0.328 | 0.080 | 200 | Reddedildi (piyasa betasi): PF p=0.328, ortR p=0.080 (esik 0.05) |
| C02 | BIST30 | USD | 270 | 1.56 | 0.224 | 1.87 | 0.147 | 0.199 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.199, ortR p=0.005 (esik 0.05) |
| C02 | ABD25 | yerel | 371 | 1.59 | 0.188 | 1.87 | 0.123 | 0.264 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.005 (esik 0.05) |
| C02 | KRIPTO25 | yerel | 193 | 1.86 | 0.326 | 2.29 | 0.152 | 0.169 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.169, ortR p=0.005 (esik 0.05) |
| C02 | EMTIA | yerel | 103 | 1.87 | 0.262 | 2.53 | 0.213 | 0.274 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.274, ortR p=0.020 (esik 0.05) |
| G007 | KRIPTO25 | yerel | 270 | 1.73 | 0.050 | 1.03 | 0.003 | 0.005 | 0.005 | 200 | Gecti (null) |
| G011 | BIST30 | USD | 380 | 1.07 | 0.064 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| G011 | ABD25 | yerel | 369 | 1.75 | 0.201 | 1.67 | 0.089 | 0.030 | 0.005 | 200 | Gecti (null) |
| G011 | KRIPTO25 | yerel | 370 | 1.73 | 0.225 | 2.25 | 0.140 | 0.269 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.269, ortR p=0.005 (esik 0.05) |
| G012 | BIST30 | USD | 496 | 1.26 | 0.043 | 1.46 | 0.035 | 0.343 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.343, ortR p=0.020 (esik 0.05) |
| G012 | ABD25 | yerel | 375 | 2.24 | 0.058 | 1.90 | 0.039 | 0.005 | 0.005 | 200 | Gecti (null) |
| G012 | KRIPTO25 | yerel | 613 | 1.40 | 0.088 | 1.60 | 0.068 | 0.313 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.313, ortR p=0.005 (esik 0.05) |
| G012 | EMTIA | yerel | 177 | 1.35 | 0.027 | 1.73 | 0.030 | 0.383 | 0.104 | 200 | Reddedildi (piyasa betasi): PF p=0.383, ortR p=0.104 (esik 0.05) |
| M006 | BIST30 | USD | 60 | 1.14 | 0.129 | 2.02 | 0.445 | 0.756 | 0.672 | 200 | Reddedildi (piyasa betasi): PF p=0.756, ortR p=0.672 (esik 0.05) |
| M006 | ABD25 | yerel | 115 | 1.88 | 0.491 | 2.45 | 0.471 | 0.383 | 0.055 | 200 | Reddedildi (piyasa betasi): PF p=0.383, ortR p=0.055 (esik 0.05) |
| M008 | BIST30 | USD | 63 | 1.41 | 0.096 | 2.41 | 0.171 | 0.313 | 0.209 | 200 | Reddedildi (piyasa betasi): PF p=0.313, ortR p=0.209 (esik 0.05) |
| M008 | ABD25 | yerel | 30 | 1.39 | 0.090 | 9.42 | 0.260 | 0.453 | 0.388 | 200 | Reddedildi (piyasa betasi): PF p=0.453, ortR p=0.388 (esik 0.05) |
| M008 | KRIPTO25 | yerel | 149 | 1.43 | 0.061 | 1.75 | 0.066 | 0.154 | 0.070 | 200 | Reddedildi (piyasa betasi): PF p=0.154, ortR p=0.070 (esik 0.05) |
| M010 | ABD25 | yerel | 547 | 1.41 | 0.115 | 1.53 | 0.096 | 0.214 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.214, ortR p=0.015 (esik 0.05) |
| M014 | ABD25 | yerel | 449 | 1.16 | 0.034 | 1.41 | 0.048 | 0.522 | 0.244 | 200 | Reddedildi (piyasa betasi): PF p=0.522, ortR p=0.244 (esik 0.05) |
| M015 | ABD25 | yerel | 295 | 1.44 | 0.049 | 1.26 | 0.024 | 0.015 | 0.010 | 200 | Gecti (null) |
| M015 | EMTIA | yerel | 47 | 1.91 | 0.082 | 1.93 | 0.070 | 0.055 | 0.026 | 1000 | Reddedildi (piyasa betasi): PF p=0.055, ortR p=0.026 (esik 0.05) |
| M017 | ABD25 | yerel | 969 | 1.54 | 0.227 | 1.06 | 0.119 | 0.005 | 0.005 | 200 | Gecti (null) |
| M020a | ABD25 | yerel | 71 | 2.72 | 0.300 | 1.64 | 0.154 | 0.005 | 0.005 | 200 | Gecti (null) |
| M020a | KRIPTO25 | yerel | 61 | 1.32 | 0.400 | 1.22 | 0.251 | 0.020 | 0.010 | 200 | Gecti (null) |
| M036 | ABD25 | yerel | 810 | 1.41 | 0.059 | 1.40 | 0.048 | 0.048 | 0.005 | 1000 | Gecti (null) |
| M036 | KRIPTO25 | yerel | 429 | 1.29 | 0.045 | 1.37 | 0.039 | 0.108 | 0.031 | 1000 | Reddedildi (piyasa betasi): PF p=0.108, ortR p=0.031 (esik 0.05) |
| M037 | ABD25 | yerel | 689 | 1.23 | 0.039 | 1.47 | 0.059 | 0.507 | 0.373 | 200 | Reddedildi (piyasa betasi): PF p=0.507, ortR p=0.373 (esik 0.05) |
| M037 | EMTIA | yerel | 161 | 1.28 | 0.039 | 1.55 | 0.066 | 0.234 | 0.229 | 200 | Reddedildi (piyasa betasi): PF p=0.234, ortR p=0.229 (esik 0.05) |
| M038 | BIST30 | USD | 1294 | 0.92 | -0.021 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| M038 | ABD25 | yerel | 1344 | 1.40 | 0.059 | 1.40 | 0.052 | 0.048 | 0.015 | 1000 | Gecti (null) |
| O1-001 | BIST30 | USD | 130 | 1.04 | 0.203 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| O1-001 | ABD25 | yerel | 116 | 2.02 | 0.603 | 3.11 | 0.630 | 0.498 | 0.070 | 200 | Reddedildi (piyasa betasi): PF p=0.498, ortR p=0.070 (esik 0.05) |
| O1-001 | KRIPTO25 | yerel | 116 | 2.49 | 0.764 | 6.85 | 11.726 | 0.458 | 0.269 | 200 | Reddedildi (piyasa betasi): PF p=0.458, ortR p=0.269 (esik 0.05) |
| O1-001 | EMTIA | yerel | 92 | 1.37 | 0.199 | 1.95 | 0.334 | 0.483 | 0.313 | 200 | Reddedildi (piyasa betasi): PF p=0.483, ortR p=0.313 (esik 0.05) |
| O1-038 | BIST30 | USD | 123 | 1.02 | 0.044 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| O1-038 | ABD25 | yerel | 93 | 1.84 | 0.450 | 3.37 | 0.777 | 0.647 | 0.383 | 200 | Reddedildi (piyasa betasi): PF p=0.647, ortR p=0.383 (esik 0.05) |
| O1-038 | KRIPTO25 | yerel | 95 | 2.98 | 0.897 | 4.19 | 1.607 | 0.299 | 0.249 | 200 | Reddedildi (piyasa betasi): PF p=0.299, ortR p=0.249 (esik 0.05) |
| O1-038 | EMTIA | yerel | 71 | 1.59 | 0.442 | 2.61 | 0.636 | 0.517 | 0.179 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.179 (esik 0.05) |
| O1-039 | BIST30 | USD | 125 | 2.57 | 0.639 | 2.69 | 0.729 | 0.100 | 0.134 | 200 | Reddedildi (piyasa betasi): PF p=0.100, ortR p=0.134 (esik 0.05) |
| O1-039 | ABD25 | yerel | 106 | 2.18 | 0.419 | 2.96 | 0.606 | 0.308 | 0.333 | 200 | Reddedildi (piyasa betasi): PF p=0.308, ortR p=0.333 (esik 0.05) |
| O1-039 | KRIPTO25 | yerel | 157 | 2.27 | 0.431 | 2.89 | 0.761 | 0.294 | 0.512 | 200 | Reddedildi (piyasa betasi): PF p=0.294, ortR p=0.512 (esik 0.05) |
| O1-039 | EMTIA | yerel | 77 | 1.53 | 0.279 | 2.49 | 0.570 | 0.662 | 0.602 | 200 | Reddedildi (piyasa betasi): PF p=0.662, ortR p=0.602 (esik 0.05) |
| O1-075 | EMTIA | yerel | 275 | 1.18 | 0.031 | 1.44 | 0.101 | 0.438 | 0.637 | 200 | Reddedildi (piyasa betasi): PF p=0.438, ortR p=0.637 (esik 0.05) |
| O1-079 | BIST30 | USD | 113 | 1.15 | 0.405 | 2.58 | 0.960 | 0.632 | 0.289 | 200 | Reddedildi (piyasa betasi): PF p=0.632, ortR p=0.289 (esik 0.05) |
| O1-079 | ABD25 | yerel | 78 | 2.63 | 1.038 | 3.84 | 1.357 | 0.264 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.129 (esik 0.05) |
| O1-079 | KRIPTO25 | yerel | 120 | 2.50 | 1.547 | 3.44 | 4.900 | 0.204 | 0.224 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.224 (esik 0.05) |
| O2-025 | ABD25 | yerel | 119 | 2.15 | 2.241 | 1.56 | 0.538 | 0.010 | 0.005 | 200 | Gecti (null) |
| O2-027 | ABD25 | yerel | 126 | 2.08 | 1.951 | 1.32 | 0.436 | 0.010 | 0.005 | 200 | Gecti (null) |
| O3-001 | ABD25 | yerel | 588 | 1.22 | 0.025 | 1.31 | 0.040 | 0.154 | 0.244 | 200 | Reddedildi (piyasa betasi): PF p=0.154, ortR p=0.244 (esik 0.05) |
| O3-003 | ABD25 | yerel | 570 | 1.37 | 0.058 | 1.36 | 0.044 | 0.040 | 0.005 | 1000 | Gecti (null) |
| O3-003 | EMTIA | yerel | 142 | 1.34 | 0.056 | 1.34 | 0.043 | 0.053 | 0.023 | 1000 | Reddedildi (piyasa betasi): PF p=0.053, ortR p=0.023 (esik 0.05) |
| O3-004 | ABD25 | yerel | 632 | 1.21 | 0.033 | 1.32 | 0.041 | 0.239 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.239, ortR p=0.129 (esik 0.05) |
| O3-007 | BIST30 | USD | 228 | 0.96 | -0.007 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| O3-007 | ABD25 | yerel | 228 | 1.16 | 0.045 | 1.58 | 0.164 | 0.900 | 0.950 | 200 | Reddedildi (piyasa betasi): PF p=0.900, ortR p=0.950 (esik 0.05) |
| O3-007 | KRIPTO25 | yerel | 228 | 1.51 | 0.081 | 1.63 | 0.196 | 0.129 | 0.751 | 200 | Reddedildi (piyasa betasi): PF p=0.129, ortR p=0.751 (esik 0.05) |
| P01 | BIST30 | USD | 633 | 1.46 | 0.145 | 1.49 | 0.122 | 0.066 | 0.009 | 1000 | Reddedildi (piyasa betasi): PF p=0.066, ortR p=0.009 (esik 0.05) |
| P01 | ABD25 | yerel | 662 | 1.62 | 0.165 | 1.72 | 0.157 | 0.169 | 0.025 | 200 | Reddedildi (piyasa betasi): PF p=0.169, ortR p=0.025 (esik 0.05) |
| P01 | KRIPTO25 | yerel | 692 | 1.54 | 0.170 | 1.71 | 0.151 | 0.284 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.284, ortR p=0.010 (esik 0.05) |
| P01 | EMTIA | yerel | 226 | 1.39 | 0.153 | 1.85 | 0.191 | 0.567 | 0.209 | 200 | Reddedildi (piyasa betasi): PF p=0.567, ortR p=0.209 (esik 0.05) |
| P02 | BIST30 | USD | 396 | 1.19 | 0.145 | 1.46 | 0.231 | 0.692 | 0.438 | 200 | Reddedildi (piyasa betasi): PF p=0.692, ortR p=0.438 (esik 0.05) |
| P02 | ABD25 | yerel | 459 | 1.48 | 0.179 | 1.70 | 0.285 | 0.338 | 0.562 | 200 | Reddedildi (piyasa betasi): PF p=0.338, ortR p=0.562 (esik 0.05) |
| P02 | KRIPTO25 | yerel | 415 | 1.36 | 0.243 | 1.49 | 0.247 | 0.284 | 0.075 | 200 | Reddedildi (piyasa betasi): PF p=0.284, ortR p=0.075 (esik 0.05) |
| P02 | EMTIA | yerel | 123 | 1.24 | 0.116 | 1.72 | 0.304 | 0.443 | 0.493 | 200 | Reddedildi (piyasa betasi): PF p=0.443, ortR p=0.493 (esik 0.05) |
| P3-001 | BIST30 | USD | 124 | 1.49 | 0.232 | 2.80 | 0.784 | 0.716 | 0.756 | 200 | Reddedildi (piyasa betasi): PF p=0.716, ortR p=0.756 (esik 0.05) |
| P3-001 | ABD25 | yerel | 91 | 2.60 | 0.423 | 3.43 | 0.756 | 0.249 | 0.532 | 200 | Reddedildi (piyasa betasi): PF p=0.249, ortR p=0.532 (esik 0.05) |
| P3-001 | KRIPTO25 | yerel | 109 | 3.24 | 1.706 | 3.88 | 1.431 | 0.214 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.214, ortR p=0.015 (esik 0.05) |
| P3-001 | EMTIA | yerel | 93 | 1.18 | 0.090 | 2.33 | 0.454 | 0.940 | 0.940 | 200 | Reddedildi (piyasa betasi): PF p=0.940, ortR p=0.940 (esik 0.05) |
| P3-002 | BIST30 | USD | 494 | 0.98 | 0.018 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| P3-002 | ABD25 | yerel | 369 | 1.92 | 0.164 | 1.91 | 0.222 | 0.045 | 0.438 | 200 | Reddedildi (piyasa betasi): PF p=0.045, ortR p=0.438 (esik 0.05) |
| P3-002 | KRIPTO25 | yerel | 588 | 1.78 | 0.151 | 1.77 | 0.237 | 0.050 | 0.398 | 200 | Reddedildi (piyasa betasi): PF p=0.050, ortR p=0.398 (esik 0.05) |
| P3-002 | EMTIA | yerel | 349 | 1.22 | 0.037 | 1.70 | 0.165 | 0.920 | 1.000 | 200 | Reddedildi (piyasa betasi): PF p=0.920, ortR p=1.000 (esik 0.05) |
| P3-003 | BIST30 | USD | 506 | 1.16 | 0.059 | 1.37 | 0.109 | 0.423 | 0.363 | 200 | Reddedildi (piyasa betasi): PF p=0.423, ortR p=0.363 (esik 0.05) |
| P3-003 | ABD25 | yerel | 511 | 1.36 | 0.065 | 1.81 | 0.171 | 0.806 | 0.980 | 200 | Reddedildi (piyasa betasi): PF p=0.806, ortR p=0.980 (esik 0.05) |
| P3-003 | KRIPTO25 | yerel | 596 | 1.49 | 0.116 | 1.66 | 0.184 | 0.338 | 0.642 | 200 | Reddedildi (piyasa betasi): PF p=0.338, ortR p=0.642 (esik 0.05) |
| P3-003 | EMTIA | yerel | 417 | 1.26 | 0.083 | 1.61 | 0.133 | 0.741 | 0.657 | 200 | Reddedildi (piyasa betasi): PF p=0.741, ortR p=0.657 (esik 0.05) |
| P3-004 | BIST30 | USD | 211 | 1.36 | 0.244 | 2.20 | 0.413 | 0.721 | 0.373 | 200 | Reddedildi (piyasa betasi): PF p=0.721, ortR p=0.373 (esik 0.05) |
| P3-004 | ABD25 | yerel | 161 | 2.40 | 0.304 | 2.68 | 0.491 | 0.104 | 0.448 | 200 | Reddedildi (piyasa betasi): PF p=0.104, ortR p=0.448 (esik 0.05) |
| P3-004 | KRIPTO25 | yerel | 291 | 1.59 | 0.162 | 2.44 | 0.509 | 0.861 | 0.955 | 200 | Reddedildi (piyasa betasi): PF p=0.861, ortR p=0.955 (esik 0.05) |
| P3-004 | EMTIA | yerel | 139 | 1.22 | 0.104 | 1.98 | 0.305 | 0.856 | 0.856 | 200 | Reddedildi (piyasa betasi): PF p=0.856, ortR p=0.856 (esik 0.05) |
| P3-005 | BIST30 | USD | 506 | 1.16 | 0.059 | 1.36 | 0.098 | 0.433 | 0.398 | 200 | Reddedildi (piyasa betasi): PF p=0.433, ortR p=0.398 (esik 0.05) |
| P3-005 | ABD25 | yerel | 511 | 1.36 | 0.065 | 1.79 | 0.169 | 0.871 | 0.985 | 200 | Reddedildi (piyasa betasi): PF p=0.871, ortR p=0.985 (esik 0.05) |
| P3-005 | KRIPTO25 | yerel | 596 | 1.49 | 0.116 | 1.65 | 0.179 | 0.294 | 0.572 | 200 | Reddedildi (piyasa betasi): PF p=0.294, ortR p=0.572 (esik 0.05) |
| P3-005 | EMTIA | yerel | 417 | 1.26 | 0.083 | 1.55 | 0.131 | 0.756 | 0.617 | 200 | Reddedildi (piyasa betasi): PF p=0.756, ortR p=0.617 (esik 0.05) |
| P3-007 | BIST30 | USD | 87 | 1.60 | 0.294 | 3.21 | 1.020 | 0.677 | 0.771 | 200 | Reddedildi (piyasa betasi): PF p=0.677, ortR p=0.771 (esik 0.05) |
| P3-007 | ABD25 | yerel | 73 | 1.79 | 0.672 | 3.44 | 1.002 | 0.826 | 0.383 | 200 | Reddedildi (piyasa betasi): PF p=0.826, ortR p=0.383 (esik 0.05) |
| P3-007 | KRIPTO25 | yerel | 83 | 3.03 | 1.337 | 6.26 | 10.870 | 0.527 | 0.408 | 200 | Reddedildi (piyasa betasi): PF p=0.527, ortR p=0.408 (esik 0.05) |
| P3-007 | EMTIA | yerel | 58 | 1.93 | 0.450 | 2.48 | 0.596 | 0.214 | 0.229 | 200 | Reddedildi (piyasa betasi): PF p=0.214, ortR p=0.229 (esik 0.05) |
| P3-008 | BIST30 | USD | 790 | 0.99 | 0.010 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| P3-008 | ABD25 | yerel | 888 | 1.38 | 0.051 | 1.43 | 0.055 | 0.104 | 0.100 | 200 | Reddedildi (piyasa betasi): PF p=0.104, ortR p=0.100 (esik 0.05) |
| P3-008 | KRIPTO25 | yerel | 740 | 1.71 | 0.127 | 1.59 | 0.083 | 0.010 | 0.005 | 200 | Gecti (null) |
| P3-008 | EMTIA | yerel | 351 | 1.27 | 0.043 | 1.35 | 0.055 | 0.119 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.119, ortR p=0.129 (esik 0.05) |
| P3-011 | BIST30 | USD | 472 | 1.18 | 0.076 | 1.48 | 0.210 | 0.756 | 0.851 | 200 | Reddedildi (piyasa betasi): PF p=0.756, ortR p=0.851 (esik 0.05) |
| P3-011 | ABD25 | yerel | 543 | 1.32 | 0.142 | 1.70 | 0.234 | 0.786 | 0.652 | 200 | Reddedildi (piyasa betasi): PF p=0.786, ortR p=0.652 (esik 0.05) |
| P3-011 | KRIPTO25 | yerel | 404 | 1.75 | 0.317 | 1.64 | 0.247 | 0.030 | 0.005 | 200 | Gecti (null) |
| P3-011 | EMTIA | yerel | 161 | 1.56 | 0.221 | 1.86 | 0.303 | 0.204 | 0.179 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.179 (esik 0.05) |
| R01 | ABD25 | yerel | 214 | 2.02 | 0.373 | 1.74 | 0.211 | 0.005 | 0.005 | 200 | Gecti (null) |
| R01 | KRIPTO25 | yerel | 221 | 2.02 | 0.640 | 2.02 | 0.286 | 0.052 | 0.001 | 1000 | Reddedildi (piyasa betasi): PF p=0.052, ortR p=0.001 (esik 0.05) |
| R02 | BIST30 | USD | 1144 | 0.94 | -0.017 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| R05 | BIST30 | USD | 595 | 1.14 | 0.090 | 1.50 | 0.121 | 0.771 | 0.174 | 200 | Reddedildi (piyasa betasi): PF p=0.771, ortR p=0.174 (esik 0.05) |
| R05 | ABD25 | yerel | 618 | 1.68 | 0.182 | 1.88 | 0.168 | 0.254 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.254, ortR p=0.020 (esik 0.05) |
| R05 | KRIPTO25 | yerel | 581 | 1.70 | 0.260 | 1.87 | 0.162 | 0.189 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.189, ortR p=0.005 (esik 0.05) |
| R05 | EMTIA | yerel | 214 | 1.52 | 0.192 | 2.16 | 0.212 | 0.657 | 0.090 | 200 | Reddedildi (piyasa betasi): PF p=0.657, ortR p=0.090 (esik 0.05) |
| RD-01 | ABD25 | yerel | 1591 | 1.25 | 0.026 | 1.63 | 0.117 | 0.985 | 1.000 | 200 | Reddedildi (piyasa betasi): PF p=0.985, ortR p=1.000 (esik 0.05) |
| RD-02 | ABD25 | yerel | 373 | 1.34 | 0.060 | 1.81 | 0.246 | 0.826 | 1.000 | 200 | Reddedildi (piyasa betasi): PF p=0.826, ortR p=1.000 (esik 0.05) |
| RD-03 | ABD25 | yerel | 30 | 2.48 | 0.059 | 2.34 | 0.137 | 0.040 | 0.438 | 200 | Reddedildi (piyasa betasi): PF p=0.040, CAGR p=0.438 (esit 0.05) |
| T8-01 | BIST30 | USD | 163 | 1.40 | 0.135 | 2.09 | 0.216 | 0.403 | 0.189 | 200 | Reddedildi (piyasa betasi): PF p=0.403, ortR p=0.189 (esik 0.05) |
| T8-01 | ABD25 | yerel | 168 | 1.48 | 0.128 | 2.19 | 0.215 | 0.547 | 0.373 | 200 | Reddedildi (piyasa betasi): PF p=0.547, ortR p=0.373 (esik 0.05) |
| T8-01 | KRIPTO25 | yerel | 132 | 1.43 | 0.165 | 2.54 | 0.233 | 0.517 | 0.169 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.169 (esik 0.05) |
| T8-02 | BIST30 | USD | 331 | 1.25 | 0.144 | 1.40 | 0.105 | 0.254 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.254, ortR p=0.010 (esik 0.05) |
| T8-02 | ABD25 | yerel | 342 | 1.34 | 0.199 | 1.63 | 0.171 | 0.428 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.428, ortR p=0.010 (esik 0.05) |
| T8-02 | KRIPTO25 | yerel | 303 | 1.41 | 0.225 | 1.49 | 0.117 | 0.144 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.144, ortR p=0.005 (esik 0.05) |
| T8-02 | EMTIA | yerel | 137 | 1.23 | 0.132 | 1.65 | 0.167 | 0.517 | 0.124 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.124 (esik 0.05) |
| T8-04 | BIST30 | USD | 352 | 1.45 | 0.215 | 1.78 | 0.246 | 0.378 | 0.119 | 200 | Reddedildi (piyasa betasi): PF p=0.378, ortR p=0.119 (esik 0.05) |
| T8-04 | ABD25 | yerel | 456 | 1.51 | 0.172 | 1.84 | 0.235 | 0.537 | 0.468 | 200 | Reddedildi (piyasa betasi): PF p=0.537, ortR p=0.468 (esik 0.05) |
| T8-04 | KRIPTO25 | yerel | 353 | 1.54 | 0.248 | 1.85 | 0.272 | 0.378 | 0.104 | 200 | Reddedildi (piyasa betasi): PF p=0.378, ortR p=0.104 (esik 0.05) |
| T8-04 | EMTIA | yerel | 137 | 1.40 | 0.162 | 1.99 | 0.296 | 0.537 | 0.423 | 200 | Reddedildi (piyasa betasi): PF p=0.537, ortR p=0.423 (esik 0.05) |
| T8-05 | BIST30 | USD | 302 | 1.73 | 0.282 | 1.80 | 0.274 | 0.090 | 0.037 | 1000 | Reddedildi (piyasa betasi): PF p=0.090, ortR p=0.037 (esik 0.05) |
| T8-05 | ABD25 | yerel | 385 | 1.56 | 0.207 | 2.02 | 0.287 | 0.677 | 0.458 | 200 | Reddedildi (piyasa betasi): PF p=0.677, ortR p=0.458 (esik 0.05) |
| T8-05 | KRIPTO25 | yerel | 271 | 1.91 | 0.371 | 2.12 | 0.339 | 0.129 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.129, ortR p=0.015 (esik 0.05) |
| T8-05 | EMTIA | yerel | 107 | 1.62 | 0.237 | 2.13 | 0.346 | 0.353 | 0.254 | 200 | Reddedildi (piyasa betasi): PF p=0.353, ortR p=0.254 (esik 0.05) |
| TV-3BXWqwnF | KRIPTO25 | yerel | 140 | 2.46 | 1.222 | 2.99 | 1.325 | 0.204 | 0.080 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.080 (esik 0.05) |
| TV-3Q75d98D | KRIPTO25 | yerel | 467 | 2.29 | 0.511 | 3.03 | 0.698 | 0.517 | 0.458 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.458 (esik 0.05) |
| TV-5EGVP61U | ABD25 | yerel | 134 | 1.94 | 0.481 | 2.10 | 0.568 | 0.100 | 0.154 | 200 | Reddedildi (piyasa betasi): PF p=0.100, ortR p=0.154 (esik 0.05) |
| TV-6knHPR6c | KRIPTO25 | yerel | 378 | 2.03 | 0.218 | 2.32 | 0.451 | 0.264 | 0.831 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.831 (esik 0.05) |
| TV-70PkIvTL | ABD25 | yerel | 160 | 1.47 | 0.162 | 2.31 | 0.379 | 0.721 | 0.796 | 200 | Reddedildi (piyasa betasi): PF p=0.721, ortR p=0.796 (esik 0.05) |
| TV-97gxVA5b | ABD25 | yerel | 87 | 2.22 | 0.693 | 2.80 | 0.637 | 0.279 | 0.025 | 200 | Reddedildi (piyasa betasi): PF p=0.279, ortR p=0.025 (esik 0.05) |
| TV-AORNVoek | ABD25 | yerel | 232 | 1.48 | 0.292 | 1.69 | 0.379 | 0.294 | 0.294 | 200 | Reddedildi (piyasa betasi): PF p=0.294, ortR p=0.294 (esik 0.05) |
| TV-BJDRgy7z | KRIPTO25 | yerel | 291 | 1.32 | 0.218 | 1.42 | 0.156 | 0.134 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.134, ortR p=0.010 (esik 0.05) |
| TV-BjjAOuub | ABD25 | yerel | 411 | 1.14 | 0.099 | 1.42 | 0.237 | 0.587 | 0.522 | 200 | Reddedildi (piyasa betasi): PF p=0.587, ortR p=0.522 (esik 0.05) |
| TV-DUCODGjC | ABD25 | yerel | 385 | 1.32 | 0.155 | 1.53 | 0.174 | 0.264 | 0.100 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.100 (esik 0.05) |
| TV-FEnNQpAn | KRIPTO25 | yerel | 58 | 3.74 | 1.769 | 9.42 | 15.933 | 0.592 | 0.478 | 200 | Reddedildi (piyasa betasi): PF p=0.592, ortR p=0.478 (esik 0.05) |
| TV-GP3FEy2z | ABD25 | yerel | 88 | 2.50 | 0.424 | 3.53 | 0.777 | 0.333 | 0.572 | 200 | Reddedildi (piyasa betasi): PF p=0.333, ortR p=0.572 (esik 0.05) |
| TV-HPbRZvsV | KRIPTO25 | yerel | 571 | 1.26 | 0.090 | 1.64 | 0.173 | 0.881 | 0.806 | 200 | Reddedildi (piyasa betasi): PF p=0.881, ortR p=0.806 (esik 0.05) |
| TV-IMKs0OPw | ABD25 | yerel | 543 | 1.37 | 0.146 | 1.64 | 0.196 | 0.667 | 0.527 | 200 | Reddedildi (piyasa betasi): PF p=0.667, ortR p=0.527 (esik 0.05) |
| TV-KO7Qe4Xb | EMTIA | yerel | 89 | 1.60 | 0.336 | 1.98 | 0.479 | 0.313 | 0.299 | 200 | Reddedildi (piyasa betasi): PF p=0.313, ortR p=0.299 (esik 0.05) |
| TV-KW2v4SNI | ABD25 | yerel | 160 | 1.77 | 0.210 | 2.45 | 0.483 | 0.522 | 0.811 | 200 | Reddedildi (piyasa betasi): PF p=0.522, ortR p=0.811 (esik 0.05) |
| TV-LBcj22se | ABD25 | yerel | 141 | 1.21 | 0.089 | 2.55 | 0.485 | 0.821 | 0.811 | 200 | Reddedildi (piyasa betasi): PF p=0.821, ortR p=0.811 (esik 0.05) |
| TV-MI47rsio | KRIPTO25 | yerel | 981 | 1.12 | 0.059 | 1.20 | 0.038 | 0.204 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.005 (esik 0.05) |
| TV-NgSIfKQx | KRIPTO25 | yerel | 164 | 2.24 | 0.428 | 2.89 | 0.652 | 0.363 | 0.423 | 200 | Reddedildi (piyasa betasi): PF p=0.363, ortR p=0.423 (esik 0.05) |
| TV-PUEDA3c6 | ABD25 | yerel | 525 | 1.44 | 0.094 | 1.60 | 0.130 | 0.303 | 0.368 | 200 | Reddedildi (piyasa betasi): PF p=0.303, ortR p=0.368 (esik 0.05) |
| TV-Q9OQye4C | KRIPTO25 | yerel | 419 | 2.39 | 0.283 | 2.51 | 0.253 | 0.086 | 0.021 | 1000 | Reddedildi (piyasa betasi): PF p=0.086, ortR p=0.021 (esik 0.05) |
| TV-QEVAQHl6 | ABD25 | yerel | 51 | 2.89 | 2.236 | 7.92 | 2.412 | 0.547 | 0.070 | 200 | Reddedildi (piyasa betasi): PF p=0.547, ortR p=0.070 (esik 0.05) |
| TV-QTYaYuX7 | KRIPTO25 | yerel | 773 | 1.10 | 0.032 | 1.58 | 0.084 | 0.915 | 0.741 | 200 | Reddedildi (piyasa betasi): PF p=0.915, ortR p=0.741 (esik 0.05) |
| TV-TbK1rB5B | KRIPTO25 | yerel | 176 | 1.99 | 0.488 | 2.68 | 0.771 | 0.622 | 0.478 | 200 | Reddedildi (piyasa betasi): PF p=0.622, ortR p=0.478 (esik 0.05) |
| TV-VO6DY8s1 | KRIPTO25 | yerel | 195 | 1.88 | 0.323 | 3.00 | 0.799 | 0.811 | 0.881 | 200 | Reddedildi (piyasa betasi): PF p=0.811, ortR p=0.881 (esik 0.05) |
| TV-VOFjU544 | KRIPTO25 | yerel | 208 | 1.70 | 0.289 | 2.94 | 0.719 | 0.920 | 0.900 | 200 | Reddedildi (piyasa betasi): PF p=0.920, ortR p=0.900 (esik 0.05) |
| TV-W67tJltC | KRIPTO25 | yerel | 319 | 1.94 | 0.453 | 2.03 | 0.573 | 0.149 | 0.338 | 200 | Reddedildi (piyasa betasi): PF p=0.149, ortR p=0.338 (esik 0.05) |
| TV-WWuTjyDx | ABD25 | yerel | 195 | 1.12 | 0.019 | 1.65 | 0.059 | 0.612 | 0.552 | 200 | Reddedildi (piyasa betasi): PF p=0.612, ortR p=0.552 (esik 0.05) |
| TV-X0F9OE4L | KRIPTO25 | yerel | 672 | 1.58 | 0.167 | 1.29 | 0.052 | 0.005 | 0.005 | 200 | Gecti (null) |
| TV-XRZCjbFr | ABD25 | yerel | 294 | 1.26 | 0.093 | 1.24 | 0.026 | 0.040 | 0.001 | 1000 | Gecti (null) |
| TV-YsWWsOGs | KRIPTO25 | yerel | 523 | 1.60 | 0.160 | 2.27 | 0.187 | 0.726 | 0.134 | 200 | Reddedildi (piyasa betasi): PF p=0.726, ortR p=0.134 (esik 0.05) |
| TV-Z9O5w3SG | KRIPTO25 | yerel | 75 | 4.29 | 1.036 | 3.89 | 0.845 | 0.025 | 0.030 | 200 | Gecti (null) |
| TV-cz5KaioF | ABD25 | yerel | 199 | 1.88 | 0.173 | 2.76 | 0.287 | 0.672 | 0.423 | 200 | Reddedildi (piyasa betasi): PF p=0.672, ortR p=0.423 (esik 0.05) |
| TV-dpkq3n4O | ABD25 | yerel | 170 | 1.94 | 0.196 | 2.68 | 0.409 | 0.463 | 0.572 | 200 | Reddedildi (piyasa betasi): PF p=0.463, ortR p=0.572 (esik 0.05) |
| TV-egTb7TgJ | KRIPTO25 | yerel | 201 | 2.25 | 0.364 | 2.54 | 0.186 | 0.164 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.164, ortR p=0.005 (esik 0.05) |
| TV-hezSShJr | ABD25 | yerel | 90 | 2.13 | 0.644 | 3.90 | 0.952 | 0.672 | 0.572 | 200 | Reddedildi (piyasa betasi): PF p=0.672, ortR p=0.572 (esik 0.05) |
| TV-n3eosaZK | ABD25 | yerel | 265 | 1.80 | 0.190 | 2.18 | 0.217 | 0.264 | 0.194 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.194 (esik 0.05) |
| TV-oF6FmwfR | KRIPTO25 | yerel | 325 | 2.09 | 0.230 | 2.94 | 1.001 | 0.453 | 0.896 | 200 | Reddedildi (piyasa betasi): PF p=0.453, ortR p=0.896 (esik 0.05) |
| TV-qgTc4zie | KRIPTO25 | yerel | 399 | 1.42 | 0.126 | 1.96 | 0.320 | 0.940 | 0.985 | 200 | Reddedildi (piyasa betasi): PF p=0.940, ortR p=0.985 (esik 0.05) |
| TV-qo43NaGV | ABD25 | yerel | 382 | 1.40 | 0.091 | 1.71 | 0.123 | 0.433 | 0.269 | 200 | Reddedildi (piyasa betasi): PF p=0.433, ortR p=0.269 (esik 0.05) |
| TV-rvBgD3aP | ABD25 | yerel | 115 | 1.30 | 0.162 | 10.86 | 2.261 | 0.467 | 0.503 | 200 | Reddedildi (piyasa betasi): PF p=0.467, ortR p=0.503 (esik 0.05) |
| TV-uC1oajDr | KRIPTO25 | yerel | 565 | 1.31 | 0.171 | 1.32 | 0.107 | 0.053 | 0.001 | 1000 | Reddedildi (piyasa betasi): PF p=0.053, ortR p=0.001 (esik 0.05) |
| TV-vJc6IOTz | ABD25 | yerel | 197 | 1.45 | 0.203 | 2.69 | 0.527 | 0.920 | 0.905 | 200 | Reddedildi (piyasa betasi): PF p=0.920, ortR p=0.905 (esik 0.05) |
| TV-vpopCZIt | KRIPTO25 | yerel | 323 | 1.50 | 0.248 | 1.75 | 0.336 | 0.483 | 0.488 | 200 | Reddedildi (piyasa betasi): PF p=0.483, ortR p=0.488 (esik 0.05) |
| TV-wigMmPHd | ABD25 | yerel | 512 | 1.70 | 0.492 | 1.93 | 0.579 | 0.363 | 0.199 | 200 | Reddedildi (piyasa betasi): PF p=0.363, ortR p=0.199 (esik 0.05) |
| TV-zoY9DmsF | ABD25 | yerel | 138 | 1.58 | 0.174 | 1.89 | 0.182 | 0.204 | 0.060 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.060 (esik 0.05) |
| TV-zrDoqm9F | EMTIA | yerel | 72 | 1.26 | 0.143 | 1.58 | 0.333 | 0.289 | 0.358 | 200 | Reddedildi (piyasa betasi): PF p=0.289, ortR p=0.358 (esik 0.05) |
| U4-H1 | ABD25 | yerel | 103 | 2.40 | 0.522 | 3.38 | 0.690 | 0.373 | 0.174 | 200 | Reddedildi (piyasa betasi): PF p=0.373, ortR p=0.174 (esik 0.05) |
| U4-H1 | KRIPTO25 | yerel | 179 | 1.82 | 0.229 | 4.10 | 1.489 | 0.632 | 0.498 | 200 | Reddedildi (piyasa betasi): PF p=0.632, ortR p=0.498 (esik 0.05) |
| U4-H1 | EMTIA | yerel | 84 | 1.88 | 0.333 | 3.53 | 0.479 | 0.726 | 0.388 | 200 | Reddedildi (piyasa betasi): PF p=0.726, ortR p=0.388 (esik 0.05) |
| U4-H2 | ABD25 | yerel | 71 | 3.10 | 1.023 | 3.21 | 1.038 | 0.071 | 0.053 | 1000 | Reddedildi (piyasa betasi): PF p=0.071, ortR p=0.053 (esik 0.05) |
| U4-H2 | KRIPTO25 | yerel | 86 | 2.16 | 0.779 | 6.07 | 10.696 | 0.726 | 0.677 | 200 | Reddedildi (piyasa betasi): PF p=0.726, ortR p=0.677 (esik 0.05) |
| U4-H2 | EMTIA | yerel | 47 | 2.09 | 0.655 | 3.18 | 1.019 | 0.269 | 0.219 | 200 | Reddedildi (piyasa betasi): PF p=0.269, ortR p=0.219 (esik 0.05) |
| U4-H3 | ABD25 | yerel | 81 | 1.81 | 0.792 | 3.10 | 0.625 | 0.592 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.592, ortR p=0.015 (esik 0.05) |
| U4-H3 | KRIPTO25 | yerel | 83 | 4.35 | 1.821 | 6.93 | 1.762 | 0.199 | 0.055 | 200 | Reddedildi (piyasa betasi): PF p=0.199, ortR p=0.055 (esik 0.05) |
| U4-H3 | EMTIA | yerel | 41 | 2.39 | 0.711 | 5.83 | 0.857 | 0.587 | 0.189 | 200 | Reddedildi (piyasa betasi): PF p=0.587, ortR p=0.189 (esik 0.05) |
| U4-H4 | ABD25 | yerel | 757 | 1.23 | 0.040 | 1.36 | 0.041 | 0.239 | 0.060 | 200 | Reddedildi (piyasa betasi): PF p=0.239, ortR p=0.060 (esik 0.05) |
| U4-H4 | EMTIA | yerel | 170 | 1.32 | 0.049 | 1.50 | 0.052 | 0.164 | 0.075 | 200 | Reddedildi (piyasa betasi): PF p=0.164, ortR p=0.075 (esik 0.05) |
| V1A | BIST30 | USD | 489 | 1.33 | 0.120 | 1.89 | 0.161 | 0.761 | 0.313 | 200 | Reddedildi (piyasa betasi): PF p=0.761, ortR p=0.313 (esik 0.05) |
| V1A | ABD25 | yerel | 633 | 1.54 | 0.133 | 2.01 | 0.153 | 0.612 | 0.164 | 200 | Reddedildi (piyasa betasi): PF p=0.612, ortR p=0.164 (esik 0.05) |
| V1A | KRIPTO25 | yerel | 442 | 2.26 | 0.287 | 2.41 | 0.216 | 0.101 | 0.005 | 1000 | Reddedildi (piyasa betasi): PF p=0.101, ortR p=0.005 (esik 0.05) |
| V1A | EMTIA | yerel | 178 | 1.50 | 0.109 | 1.93 | 0.148 | 0.363 | 0.229 | 200 | Reddedildi (piyasa betasi): PF p=0.363, ortR p=0.229 (esik 0.05) |
| V1B | BIST30 | USD | 672 | 1.22 | 0.066 | 1.69 | 0.142 | 0.796 | 0.716 | 200 | Reddedildi (piyasa betasi): PF p=0.796, ortR p=0.716 (esik 0.05) |
| V1B | ABD25 | yerel | 742 | 1.81 | 0.155 | 1.97 | 0.154 | 0.174 | 0.055 | 200 | Reddedildi (piyasa betasi): PF p=0.174, ortR p=0.055 (esik 0.05) |
| V1B | KRIPTO25 | yerel | 631 | 1.56 | 0.160 | 2.19 | 0.180 | 0.652 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.652, ortR p=0.129 (esik 0.05) |
| V1B | EMTIA | yerel | 272 | 1.44 | 0.126 | 1.76 | 0.147 | 0.408 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.408, ortR p=0.129 (esik 0.05) |

## Karar ozeti

- T6b'ye gecen kartlar: A4-002, A6-004, A6-010, G007, G011, G012, M015, M017, M020a, M036, M038, O2-025, O2-027, O3-003, P3-008, P3-011, R01, TV-X0F9OE4L, TV-XRZCjbFr, TV-Z9O5w3SG
- Elenen kartlar (hicbir piyasada gecmedi): A1-025, A3-007, A3-008a, A3-008b, A3-009a, A3-009b, A3-009c, A4-003, A4-005, A5-009, A6-001, A6-003, B1-002, B3-001, B3-005, B3-010, B3-014, C01, C02, M006, M008, M010, M014, M037, O1-001, O1-038, O1-039, O1-075, O1-079, O3-001, O3-004, O3-007, P01, P02, P3-001, P3-002, P3-003, P3-004, P3-005, P3-007, R02, R05, RD-01, RD-02, RD-03, T8-01, T8-02, T8-04, T8-05, TV-3BXWqwnF, TV-3Q75d98D, TV-5EGVP61U, TV-6knHPR6c, TV-70PkIvTL, TV-97gxVA5b, TV-AORNVoek, TV-BJDRgy7z, TV-BjjAOuub, TV-DUCODGjC, TV-FEnNQpAn, TV-GP3FEy2z, TV-HPbRZvsV, TV-IMKs0OPw, TV-KO7Qe4Xb, TV-KW2v4SNI, TV-LBcj22se, TV-MI47rsio, TV-NgSIfKQx, TV-PUEDA3c6, TV-Q9OQye4C, TV-QEVAQHl6, TV-QTYaYuX7, TV-TbK1rB5B, TV-VO6DY8s1, TV-VOFjU544, TV-W67tJltC, TV-WWuTjyDx, TV-YsWWsOGs, TV-cz5KaioF, TV-dpkq3n4O, TV-egTb7TgJ, TV-hezSShJr, TV-n3eosaZK, TV-oF6FmwfR, TV-qgTc4zie, TV-qo43NaGV, TV-rvBgD3aP, TV-uC1oajDr, TV-vJc6IOTz, TV-vpopCZIt, TV-wigMmPHd, TV-zoY9DmsF, TV-zrDoqm9F, U4-H1, U4-H2, U4-H3, U4-H4, V1A, V1B

## Notlar

- Null model: ayni cikis kurallari ve portfoy limitleri; sembol basina ayni giris sayisi (rastgele barlar), toplam islem sayisini kartinkine yaklastirmak icin giris sayisi pilot kosuyla olceklenir; `null_islem_ort` ve `tutma_*` kontrol icindir.
- Sinir bolgedeki satirlar (p 0,03-0,10) daha cok tekrarla yeniden kosulur.
- Rotasyon kartlari (T23, `metrik: PF+CAGR`): islem basina stop/R yok; null modelde takvim, N, maliyet ve yurutme kartinki, yalniz secim rastgele (kesitsel/sirali: rastgele siralama, filtre ve rejim kapisi ayni; gecis: ayni gecis tarihlerinde agacin enstrumanlarindan biri). PF ve CAGR null %95'inin ustunde olmali; `ort_r`, `null_ortr_*`, `p_ortr` sutunlari bu satirlarda CAGR tasir.
- Gun ici arsivleri `--veri-kok` altindan okunur; BIST 1H veri kalitesi duzelene kadar null testine alinmaz.
- BIST: USD fiyat = TL fiyat / ayni gun USDTRY kapanisi. TL sonucu `PF_1x_tl`, `net_1x_tl` sutunlarinda yalniz bilgi.
