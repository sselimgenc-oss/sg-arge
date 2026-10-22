# Asama 2a: piyasa betasi testleri (T6a)

BIST USD bazinda; rastgele giris (null) testi: PF ve ortalama R, null dagiliminin %95 yuzdeligini gecmeli.
Donem: IS 2020-01-01 -> 2024-09-30 (OOS ve 2015-2019 kullanilmadi).

Kart: 37 | T6b'ye gecen: 3 | elenen/dogrulanamaz: 34

## Satir sonuclari

| Kart | Piyasa | Para | Islem | PF | ortR | null PF p95 | null ortR p95 | p(PF) | p(ortR) | Tekrar | Karar |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
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
| A5-009 | ABD25 | yerel | 1878 | 1.17 | 0.027 | 1.30 | 0.043 | 0.716 | 0.736 | 200 | Reddedildi (piyasa betasi): PF p=0.716, ortR p=0.736 (esik 0.05) |
| A6-001 | BIST30 | USD | 670 | 0.92 | -0.029 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| A6-001 | ABD25 | yerel | 847 | 1.11 | 0.036 | 1.42 | 0.064 | 0.881 | 0.567 | 200 | Reddedildi (piyasa betasi): PF p=0.881, ortR p=0.567 (esik 0.05) |
| A6-001 | EMTIA | yerel | 235 | 1.35 | 0.089 | 1.54 | 0.082 | 0.164 | 0.050 | 200 | Reddedildi (piyasa betasi): PF p=0.164, ortR p=0.050 (esik 0.05) |
| A6-010 | BIST30 | USD | 446 | 0.99 | 0.024 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| A6-010 | ABD25 | yerel | 570 | 1.25 | 0.086 | 1.53 | 0.083 | 0.652 | 0.035 | 200 | Reddedildi (piyasa betasi): PF p=0.652, ortR p=0.035 (esik 0.05) |
| A6-010 | KRIPTO25 | yerel | 952 | 1.36 | 0.110 | 1.49 | 0.092 | 0.398 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.398, ortR p=0.010 (esik 0.05) |
| A6-010 | EMTIA | yerel | 319 | 1.38 | 0.068 | 1.27 | 0.049 | 0.020 | 0.020 | 200 | Gecti (null) |
| B1-002 | BIST30 | USD | 130 | 1.04 | 0.203 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| B1-002 | ABD25 | yerel | 116 | 2.02 | 0.603 | 3.09 | 0.598 | 0.502 | 0.055 | 200 | Reddedildi (piyasa betasi): PF p=0.502, ortR p=0.055 (esik 0.05) |
| B1-002 | KRIPTO25 | yerel | 116 | 2.49 | 0.764 | 7.33 | 13.123 | 0.542 | 0.284 | 200 | Reddedildi (piyasa betasi): PF p=0.542, ortR p=0.284 (esik 0.05) |
| B1-002 | EMTIA | yerel | 92 | 1.37 | 0.199 | 1.88 | 0.299 | 0.418 | 0.249 | 200 | Reddedildi (piyasa betasi): PF p=0.418, ortR p=0.249 (esik 0.05) |
| B3-010 | ABD25 | yerel | 756 | 1.23 | 0.040 | 1.39 | 0.040 | 0.289 | 0.060 | 200 | Reddedildi (piyasa betasi): PF p=0.289, ortR p=0.060 (esik 0.05) |
| B3-010 | EMTIA | yerel | 169 | 1.30 | 0.047 | 1.45 | 0.049 | 0.144 | 0.070 | 200 | Reddedildi (piyasa betasi): PF p=0.144, ortR p=0.070 (esik 0.05) |
| C01 | BIST30 | USD | 302 | 1.23 | 0.065 | 1.71 | 0.132 | 0.542 | 0.373 | 200 | Reddedildi (piyasa betasi): PF p=0.542, ortR p=0.373 (esik 0.05) |
| C01 | ABD25 | yerel | 376 | 1.41 | 0.162 | 1.88 | 0.177 | 0.587 | 0.085 | 200 | Reddedildi (piyasa betasi): PF p=0.587, ortR p=0.085 (esik 0.05) |
| C01 | KRIPTO25 | yerel | 231 | 2.09 | 0.241 | 2.43 | 0.193 | 0.124 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.124, ortR p=0.020 (esik 0.05) |
| C01 | EMTIA | yerel | 102 | 1.65 | 0.219 | 2.35 | 0.248 | 0.328 | 0.080 | 200 | Reddedildi (piyasa betasi): PF p=0.328, ortR p=0.080 (esik 0.05) |
| C02 | BIST30 | USD | 270 | 1.56 | 0.224 | 1.87 | 0.147 | 0.199 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.199, ortR p=0.005 (esik 0.05) |
| C02 | ABD25 | yerel | 371 | 1.59 | 0.188 | 1.87 | 0.123 | 0.264 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.005 (esik 0.05) |
| C02 | KRIPTO25 | yerel | 193 | 1.86 | 0.326 | 2.29 | 0.152 | 0.169 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.169, ortR p=0.005 (esik 0.05) |
| C02 | EMTIA | yerel | 103 | 1.87 | 0.262 | 2.53 | 0.213 | 0.274 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.274, ortR p=0.020 (esik 0.05) |
| O1-001 | BIST30 | USD | 130 | 1.04 | 0.203 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| O1-001 | ABD25 | yerel | 116 | 2.02 | 0.603 | 3.11 | 0.630 | 0.498 | 0.070 | 200 | Reddedildi (piyasa betasi): PF p=0.498, ortR p=0.070 (esik 0.05) |
| O1-001 | KRIPTO25 | yerel | 116 | 2.49 | 0.764 | 6.85 | 11.726 | 0.458 | 0.269 | 200 | Reddedildi (piyasa betasi): PF p=0.458, ortR p=0.269 (esik 0.05) |
| O1-001 | EMTIA | yerel | 92 | 1.37 | 0.199 | 1.95 | 0.334 | 0.483 | 0.313 | 200 | Reddedildi (piyasa betasi): PF p=0.483, ortR p=0.313 (esik 0.05) |
| O1-038 | BIST30 | USD | 123 | 1.02 | 0.044 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| O1-038 | ABD25 | yerel | 93 | 1.84 | 0.450 | 3.37 | 0.777 | 0.652 | 0.383 | 200 | Reddedildi (piyasa betasi): PF p=0.652, ortR p=0.383 (esik 0.05) |
| O1-038 | KRIPTO25 | yerel | 95 | 2.98 | 0.897 | 4.19 | 1.607 | 0.299 | 0.249 | 200 | Reddedildi (piyasa betasi): PF p=0.299, ortR p=0.249 (esik 0.05) |
| O1-038 | EMTIA | yerel | 71 | 1.59 | 0.442 | 2.61 | 0.636 | 0.517 | 0.179 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.179 (esik 0.05) |
| O1-066 | BIST30 | USD | 50 | 1.92 | 0.214 | 3.65 | 0.506 | 0.547 | 0.552 | 200 | Reddedildi (piyasa betasi): PF p=0.547, ortR p=0.552 (esik 0.05) |
| O1-066 | ABD25 | yerel | 49 | 2.81 | 0.366 | 4.73 | 0.588 | 0.279 | 0.313 | 200 | Reddedildi (piyasa betasi): PF p=0.279, ortR p=0.313 (esik 0.05) |
| O1-066 | KRIPTO25 | yerel | 31 | 4.61 | 1.565 | 17.88 | 5.505 | 0.453 | 0.119 | 200 | Reddedildi (piyasa betasi): PF p=0.453, ortR p=0.119 (esik 0.05) |
| O1-075 | EMTIA | yerel | 275 | 1.18 | 0.031 | 1.44 | 0.101 | 0.438 | 0.637 | 200 | Reddedildi (piyasa betasi): PF p=0.438, ortR p=0.637 (esik 0.05) |
| O1-079 | BIST30 | USD | 113 | 1.15 | 0.405 | 2.58 | 0.960 | 0.632 | 0.289 | 200 | Reddedildi (piyasa betasi): PF p=0.632, ortR p=0.289 (esik 0.05) |
| O1-079 | ABD25 | yerel | 78 | 2.63 | 1.038 | 3.84 | 1.357 | 0.264 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.264, ortR p=0.129 (esik 0.05) |
| O1-079 | KRIPTO25 | yerel | 120 | 2.50 | 1.547 | 3.44 | 4.900 | 0.204 | 0.224 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.224 (esik 0.05) |
| O3-007 | BIST30 | USD | 228 | 0.96 | -0.007 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| O3-007 | ABD25 | yerel | 228 | 1.16 | 0.045 | 1.58 | 0.164 | 0.900 | 0.950 | 200 | Reddedildi (piyasa betasi): PF p=0.900, ortR p=0.950 (esik 0.05) |
| O3-007 | KRIPTO25 | yerel | 228 | 1.51 | 0.081 | 1.63 | 0.196 | 0.129 | 0.751 | 200 | Reddedildi (piyasa betasi): PF p=0.129, ortR p=0.751 (esik 0.05) |
| P01 | BIST30 | USD | 633 | 1.46 | 0.145 | 1.49 | 0.122 | 0.066 | 0.009 | 1000 | Reddedildi (piyasa betasi): PF p=0.066, ortR p=0.009 (esik 0.05) |
| P01 | ABD25 | yerel | 662 | 1.62 | 0.165 | 1.72 | 0.157 | 0.169 | 0.025 | 200 | Reddedildi (piyasa betasi): PF p=0.169, ortR p=0.025 (esik 0.05) |
| P01 | KRIPTO25 | yerel | 692 | 1.54 | 0.170 | 1.71 | 0.151 | 0.284 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.284, ortR p=0.010 (esik 0.05) |
| P01 | EMTIA | yerel | 226 | 1.39 | 0.153 | 1.85 | 0.191 | 0.567 | 0.209 | 200 | Reddedildi (piyasa betasi): PF p=0.567, ortR p=0.209 (esik 0.05) |
| P02 | BIST30 | USD | 396 | 1.19 | 0.145 | 1.46 | 0.231 | 0.692 | 0.438 | 200 | Reddedildi (piyasa betasi): PF p=0.692, ortR p=0.438 (esik 0.05) |
| P02 | ABD25 | yerel | 459 | 1.48 | 0.180 | 1.69 | 0.285 | 0.338 | 0.572 | 200 | Reddedildi (piyasa betasi): PF p=0.338, ortR p=0.572 (esik 0.05) |
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
| P3-011 | BIST30 | USD | 472 | 1.18 | 0.076 | 1.48 | 0.210 | 0.756 | 0.851 | 200 | Reddedildi (piyasa betasi): PF p=0.756, ortR p=0.851 (esik 0.05) |
| P3-011 | ABD25 | yerel | 545 | 1.31 | 0.141 | 1.66 | 0.227 | 0.816 | 0.657 | 200 | Reddedildi (piyasa betasi): PF p=0.816, ortR p=0.657 (esik 0.05) |
| P3-011 | KRIPTO25 | yerel | 404 | 1.75 | 0.317 | 1.64 | 0.247 | 0.030 | 0.005 | 200 | Gecti (null) |
| P3-011 | EMTIA | yerel | 161 | 1.56 | 0.221 | 1.86 | 0.303 | 0.204 | 0.179 | 200 | Reddedildi (piyasa betasi): PF p=0.204, ortR p=0.179 (esik 0.05) |
| R01 | ABD25 | yerel | 214 | 2.02 | 0.373 | 1.74 | 0.211 | 0.005 | 0.005 | 200 | Gecti (null) |
| R01 | KRIPTO25 | yerel | 221 | 2.02 | 0.640 | 2.02 | 0.286 | 0.052 | 0.001 | 1000 | Reddedildi (piyasa betasi): PF p=0.052, ortR p=0.001 (esik 0.05) |
| R02 | BIST30 | USD | 1144 | 0.94 | -0.017 | - | - | - | - | - | Reddedildi (BIST USD): USD: PF_1x<1.1,net_2x<=0 |
| R05 | BIST30 | USD | 595 | 1.14 | 0.090 | 1.50 | 0.121 | 0.771 | 0.174 | 200 | Reddedildi (piyasa betasi): PF p=0.771, ortR p=0.174 (esik 0.05) |
| R05 | ABD25 | yerel | 618 | 1.68 | 0.182 | 1.88 | 0.168 | 0.254 | 0.020 | 200 | Reddedildi (piyasa betasi): PF p=0.254, ortR p=0.020 (esik 0.05) |
| R05 | KRIPTO25 | yerel | 581 | 1.70 | 0.260 | 1.87 | 0.162 | 0.189 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.189, ortR p=0.005 (esik 0.05) |
| R05 | EMTIA | yerel | 214 | 1.52 | 0.192 | 2.16 | 0.212 | 0.657 | 0.090 | 200 | Reddedildi (piyasa betasi): PF p=0.657, ortR p=0.090 (esik 0.05) |
| T8-01 | BIST30 | USD | 163 | 1.40 | 0.135 | 2.09 | 0.216 | 0.403 | 0.189 | 200 | Reddedildi (piyasa betasi): PF p=0.403, ortR p=0.189 (esik 0.05) |
| T8-01 | ABD25 | yerel | 168 | 1.48 | 0.128 | 2.19 | 0.215 | 0.547 | 0.373 | 200 | Reddedildi (piyasa betasi): PF p=0.547, ortR p=0.373 (esik 0.05) |
| T8-01 | KRIPTO25 | yerel | 132 | 1.43 | 0.165 | 2.54 | 0.233 | 0.517 | 0.169 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.169 (esik 0.05) |
| T8-02 | BIST30 | USD | 331 | 1.25 | 0.144 | 1.40 | 0.105 | 0.254 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.254, ortR p=0.010 (esik 0.05) |
| T8-02 | ABD25 | yerel | 342 | 1.34 | 0.199 | 1.63 | 0.171 | 0.428 | 0.010 | 200 | Reddedildi (piyasa betasi): PF p=0.428, ortR p=0.010 (esik 0.05) |
| T8-02 | KRIPTO25 | yerel | 303 | 1.41 | 0.225 | 1.49 | 0.117 | 0.144 | 0.005 | 200 | Reddedildi (piyasa betasi): PF p=0.144, ortR p=0.005 (esik 0.05) |
| T8-02 | EMTIA | yerel | 137 | 1.23 | 0.132 | 1.65 | 0.167 | 0.517 | 0.124 | 200 | Reddedildi (piyasa betasi): PF p=0.517, ortR p=0.124 (esik 0.05) |
| T8-04 | BIST30 | USD | 352 | 1.45 | 0.215 | 1.78 | 0.246 | 0.378 | 0.119 | 200 | Reddedildi (piyasa betasi): PF p=0.378, ortR p=0.119 (esik 0.05) |
| T8-04 | ABD25 | yerel | 456 | 1.51 | 0.172 | 1.85 | 0.236 | 0.537 | 0.483 | 200 | Reddedildi (piyasa betasi): PF p=0.537, ortR p=0.483 (esik 0.05) |
| T8-04 | KRIPTO25 | yerel | 353 | 1.54 | 0.248 | 1.85 | 0.272 | 0.378 | 0.104 | 200 | Reddedildi (piyasa betasi): PF p=0.378, ortR p=0.104 (esik 0.05) |
| T8-04 | EMTIA | yerel | 137 | 1.40 | 0.162 | 1.99 | 0.296 | 0.537 | 0.423 | 200 | Reddedildi (piyasa betasi): PF p=0.537, ortR p=0.423 (esik 0.05) |
| T8-05 | BIST30 | USD | 302 | 1.73 | 0.282 | 1.80 | 0.274 | 0.090 | 0.037 | 1000 | Reddedildi (piyasa betasi): PF p=0.090, ortR p=0.037 (esik 0.05) |
| T8-05 | ABD25 | yerel | 386 | 1.56 | 0.203 | 2.03 | 0.292 | 0.677 | 0.448 | 200 | Reddedildi (piyasa betasi): PF p=0.677, ortR p=0.448 (esik 0.05) |
| T8-05 | KRIPTO25 | yerel | 271 | 1.91 | 0.371 | 2.12 | 0.339 | 0.129 | 0.015 | 200 | Reddedildi (piyasa betasi): PF p=0.129, ortR p=0.015 (esik 0.05) |
| T8-05 | EMTIA | yerel | 107 | 1.62 | 0.237 | 2.13 | 0.346 | 0.353 | 0.254 | 200 | Reddedildi (piyasa betasi): PF p=0.353, ortR p=0.254 (esik 0.05) |
| V1A | BIST30 | USD | 489 | 1.33 | 0.120 | 1.89 | 0.161 | 0.761 | 0.313 | 200 | Reddedildi (piyasa betasi): PF p=0.761, ortR p=0.313 (esik 0.05) |
| V1A | ABD25 | yerel | 633 | 1.53 | 0.132 | 2.01 | 0.153 | 0.632 | 0.169 | 200 | Reddedildi (piyasa betasi): PF p=0.632, ortR p=0.169 (esik 0.05) |
| V1A | KRIPTO25 | yerel | 442 | 2.26 | 0.287 | 2.41 | 0.216 | 0.101 | 0.005 | 1000 | Reddedildi (piyasa betasi): PF p=0.101, ortR p=0.005 (esik 0.05) |
| V1A | EMTIA | yerel | 178 | 1.50 | 0.109 | 1.93 | 0.148 | 0.363 | 0.229 | 200 | Reddedildi (piyasa betasi): PF p=0.363, ortR p=0.229 (esik 0.05) |
| V1B | BIST30 | USD | 672 | 1.22 | 0.066 | 1.69 | 0.142 | 0.796 | 0.716 | 200 | Reddedildi (piyasa betasi): PF p=0.796, ortR p=0.716 (esik 0.05) |
| V1B | ABD25 | yerel | 743 | 1.77 | 0.162 | 1.98 | 0.158 | 0.249 | 0.045 | 200 | Reddedildi (piyasa betasi): PF p=0.249, ortR p=0.045 (esik 0.05) |
| V1B | KRIPTO25 | yerel | 631 | 1.56 | 0.160 | 2.19 | 0.180 | 0.652 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.652, ortR p=0.129 (esik 0.05) |
| V1B | EMTIA | yerel | 272 | 1.44 | 0.126 | 1.76 | 0.147 | 0.408 | 0.129 | 200 | Reddedildi (piyasa betasi): PF p=0.408, ortR p=0.129 (esik 0.05) |

## Karar ozeti

- T6b'ye gecen kartlar: A6-010, P3-011, R01
- Elenen kartlar (hicbir piyasada gecmedi): A3-007, A3-008a, A3-008b, A3-009a, A3-009b, A3-009c, A5-009, A6-001, B1-002, B3-010, C01, C02, O1-001, O1-038, O1-066, O1-075, O1-079, O3-007, P01, P02, P3-001, P3-002, P3-003, P3-004, P3-005, P3-007, R02, R05, T8-01, T8-02, T8-04, T8-05, V1A, V1B

## Notlar

- Null model: ayni cikis kurallari ve portfoy limitleri; sembol basina ayni giris sayisi (rastgele barlar), toplam islem sayisini kartinkine yaklastirmak icin giris sayisi pilot kosuyla olceklenir; `null_islem_ort` ve `tutma_*` kontrol icindir.
- Sinir bolgedeki satirlar (p 0,03-0,10) daha cok tekrarla yeniden kosulur.
- BIST: USD fiyat = TL fiyat / ayni gun USDTRY kapanisi. TL sonucu `PF_1x_tl`, `net_1x_tl` sutunlarinda yalniz bilgi.
