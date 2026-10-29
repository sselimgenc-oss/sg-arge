# Seçim v1.3 — 2026-10-29 (kapı tarihi 2026-10-28)

- **Seçim = geçmiş getiri sıralaması (adım 1–3 süzgeçli).** Havuz: adım 1+2 Geçti, tarz intraday/swing, adım 3 statik koşulları (kısa işlem payı, medyan ve en yüksek kaldıraç). Bu sıralamanın ileriyi taşıyıp taşımadığı pilotun sorusudur; kanıt sayılmaz.
- Kimlik: kurallar `7624e1d96c23` · secim.py `578cc5aa2548` · tohum `secim-v1.3-2026-10-28`.
- Girdi: kapı satırı 15131, hesap sürümü v1.1-2026-10-27d, kapsam 1.0, durum `tamam`.
- Havuz 185 · aday 18 · oda 18 · kontrol 18 (ikincil kontrol 167) · taban 18 · elle 9.

## Kat sayıları (tarz kırılımlı)

| tarz | havuz | puansız | aday | oda |
|---|---|---|---|---|
| intraday | 98 | 0 | 9 | 9 |
| swing | 87 | 0 | 9 | 9 |

## Oda

| # | adres | takma ad | tarz | puan | medyan kaldıraç | en yüksek kaldıraç | geçmiş gün | neden seçildi |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x34246e62e88dec68f57bf21ca16d8c773d26c507` | 3424 | intraday | 1.1471 | 0.57 | 6.41 | 510 | intraday aday sırası 1 |
| 2 | `0x58d70b61a2837fe764c2456d6dad26c266a8ac02` | 58d7 | intraday | 1.1382 | 0.81 | 4.45 | 1000 | intraday aday sırası 2 |
| 3 | `0x86d2161a18a6eb5be550d5253496e5a161cdf731` | 86d2 | intraday | 0.9820 | 0.11 | 5.95 | 1098 | intraday aday sırası 4 |
| 4 | `0x183c6497814803574c23866c7662dea4c044d0f9` | 183c | swing | 0.8072 | 2.21 | 7.57 | 538 | swing aday sırası 2 |
| 5 | `0xf53cab0c6f25f48f985d1e2c40e03fc7c1963364` | f53c | swing | 0.8069 | 1.82 | 3.19 | 1042 | swing aday sırası 3 |
| 6 | `0xe63d6f9d856cb10b44e892291612d2385f273f53` | e63d | intraday | 0.7894 | 0.94 | 3.86 | 461 | intraday aday sırası 5 |
| 7 | `0xa1d4fc32f21d9d77a4c20a6ac4b748815912c07c` | a1d4 | swing | 0.7125 | 0.85 | 4.42 | 370 | swing aday sırası 4 |
| 8 | `0x4860d039cbc7cffb0267f86e63f4b4442b71505e` | 4860 | swing | 0.6694 | 0.39 | 2.58 | 811 | swing aday sırası 5 |
| 9 | `0x2888be6982957103ea88ac10f4179df0a294e877` | 2888 | swing | 0.6415 | 0.21 | 6.46 | 699 | swing aday sırası 6 |
| 10 | `0x582e0cbcf29b1a86be93c0f5105345546214db9a` | 582e | intraday | 0.6344 | 1.38 | 3.05 | 685 | intraday aday sırası 6 |
| 11 | `0x50e2fe552727a4b8692c192b4f96d1a6b0d44394` | 50e2 | swing | 0.6252 | 0.36 | 2.85 | 447 | swing aday sırası 8 |
| 12 | `0x84d76e64be483a615e2447ccf3b52e938cb40688` | 84d7 | intraday | 0.6138 | 1.52 | 4.80 | 1161 | intraday aday sırası 7 |
| 13 | `0x888e000c78b8f1aada5b3c99f880794907b76d77` | 888e | swing | 0.5501 | 0.64 | 3.28 | 664 | swing aday sırası 9 |
| 14 | `0x3d5f1ad033c4e7c6a6d433d50d694c488dcaebcf` | 3d5f | intraday | 0.5313 | 0.29 | 4.21 | 692 | intraday aday sırası 8 |
| 15 | `0x452ea0373056462c8e3b301c996ecfab3511d712` | 452e | intraday | 0.5203 | 1.03 | 3.82 | 895 | intraday aday sırası 9 |
| 16 | `0xf208ff0e4d31aa30def8af97348e9dee9b38dba9` | f208 | intraday | 1.0228 | 1.47 | 5.85 | 267 | intraday aday sırası 3 (genç aday, 365 günden az) |
| 17 | `0x909eb3d5ff0ac0df12c81f8495860cfccf1e7ea9` | 909e | swing | 0.8558 | 1.54 | 5.05 | 314 | swing aday sırası 1 (genç aday, 365 günden az) |
| 18 | `0x9312e0a61f21affbd5be821f436f8fdf6b6f6663` | 9312 | swing | 0.6342 | 0.71 | 2.42 | 286 | swing aday sırası 7 (genç aday, 365 günden az) |

## Oda yoğunlaşması ve puan tutarlılığı (bilgi)

Günlük getiri dosyası yok (`gunluk.csv.gz`: kapı koşusu yayımlamadı); bu bölüm hesaplanamadı. Seçimi değiştirmez.

## Oda ↔ kontrol dilim dağılımı

Dilim = tarz × en yüksek kaldıraç (havuz medyanı 2.44; alt = medyan ve altı). Kontrol odayla ayrıktır.

| dilim | havuz | oda | kontrol |
|---|---|---|---|
| intraday/alt | 45 | 0 | 0 |
| intraday/ust | 53 | 9 | 9 |
| swing/alt | 48 | 1 | 1 |
| swing/ust | 39 | 8 | 8 |

## Kontrol

Sıra: `sha256(secim-v1.3-2026-10-28-<adres>)`; her oda üyesine aynı dilimden bir kontrol. Eşleşmeler (oda → kontrol):

- `0x183c6497814803574c23866c7662dea4c044d0f9` → `0x7eb9026d0183942458bd4660371c3cc0a2df3beb`
- `0x2888be6982957103ea88ac10f4179df0a294e877` → `0x8bae3527e5a33fa0cf184f37bc112d071463ab6d`
- `0x34246e62e88dec68f57bf21ca16d8c773d26c507` → `0x66d1f704749ced8c60df03cd0ccfce05c5d87fae`
- `0x3d5f1ad033c4e7c6a6d433d50d694c488dcaebcf` → `0x1fbe7279da134c53fa521f5ee65891948e775e17`
- `0x452ea0373056462c8e3b301c996ecfab3511d712` → `0x44e044712a7f32ad47b4ff74dbe7e99c4c8b5a73`
- `0x4860d039cbc7cffb0267f86e63f4b4442b71505e` → `0x2c9632dd4adbffe07cd311c82e6738537e6195ae`
- `0x50e2fe552727a4b8692c192b4f96d1a6b0d44394` → `0x221284041f07f1e9af30beadbd08bb14f5e5838c`
- `0x582e0cbcf29b1a86be93c0f5105345546214db9a` → `0x378defc39d5dcdfbecd4f1673a5e228f992fc08e`
- `0x58d70b61a2837fe764c2456d6dad26c266a8ac02` → `0xfeca598e3909b1c5574b4d77828d40a75cc57fd4`
- `0x84d76e64be483a615e2447ccf3b52e938cb40688` → `0xe0afe5de6831901db80d7ca9d17475f78b1a870c`
- `0x86d2161a18a6eb5be550d5253496e5a161cdf731` → `0xd750d35610fa0c07190169e0003160574368827b`
- `0x888e000c78b8f1aada5b3c99f880794907b76d77` → `0x2fcb6898d5a0623de19c3691904927685014c4d8`
- `0x909eb3d5ff0ac0df12c81f8495860cfccf1e7ea9` → `0xe9c2df5b14c7f476e8a5895d5b0c6b015e87bf2e`
- `0x9312e0a61f21affbd5be821f436f8fdf6b6f6663` → `0xcab90bb2b3a2f57f40326093de037c655c7fa8ae`
- `0xa1d4fc32f21d9d77a4c20a6ac4b748815912c07c` → `0xb16395a96326a115102335ffb4da07ee2a90a72f`
- `0xe63d6f9d856cb10b44e892291612d2385f273f53` → `0x22dfa5d3751aa194a119a4eaebce903cc5a635b5`
- `0xf208ff0e4d31aa30def8af97348e9dee9b38dba9` → `0x7cb42a9fd91d7f2b506de9205254e41bede28439`
- `0xf53cab0c6f25f48f985d1e2c40e03fc7c1963364` → `0x398433dd94502cb28814d145a4fb8e98deba601b`

## Kapı tablosu sütun özeti (min/medyan/max)

| sütun | dolu | min | medyan | max |
|---|---|---|---|---|
| account_value | 15131 | 0.00579 | 1.872e+05 | 7.961e+08 |
| active_months | 14786 | 1 | 13 | 13 |
| profitable_month_ratio | 14786 | 0 | 0.6 | 1 |
| max_drawdown | 14786 | 0 | 0.4389 | 1 |
| return_12m | 14786 | -1 | 0.627 | 1.712e+11 |
| calmar | 14126 | -5.636 | 2.294 | 4.483e+68 |
| pnl_history_days | 14786 | 27 | 365 | 365 |
| account_age_days | 14786 | 27 | 475.5 | 1337 |
| hesap_degeri_bugun | 2961 | -1.456e+07 | 55.39 | 9.928e+07 |
| hesap_ana | 2961 | 0 | 0 | 3.269e+07 |
| hesap_hip3 | 2961 | 0 | 0 | 6.861e+07 |
| hesap_spot_usdc | 2961 | -2.639e+07 | 0.4736 | 1.843e+07 |
| sure_dolum_sayisi | 1353 | 0 | 2771 | 1.441e+05 |
| history_days | 1132 | 181 | 365 | 365 |
| closed_trades | 1132 | 0 | 23 | 4245 |
| sortino | 952 | -19.1 | 1.271 | 4442 |
| ulcer_index | 964 | 0 | 0.01424 | 2.039 |
| largest_trade_share | 895 | 0.01066 | 0.3039 | 1 |
| profit_factor_without_best | 842 | 0 | 1.123 | 7974 |
| median_holding_hours | 917 | 0.0003544 | 14.8 | 7020 |
| median_leverage | 964 | 0 | 0.3501 | 155.6 |
| max_leverage | 964 | 0 | 1.993 | 200 |
| kaldirac_supheli_ornek | 964 | 0 | 0 | 556 |
| martingale_ratio | 964 | 0 | 0.07105 | 1 |
| martingale_additions | 964 | 0 | 137 | 3.255e+04 |
| martingale_aleyhe_ekleme | 964 | 0 | 10 | 4553 |
| martingale_signal | 1132 | 0 | 0 | 1 |
| candle_coverage | 1132 | 0 | 1 | 1 |
| complete_data | 1132 | 0 | 1 | 1 |
| gecikme_0dk_eksik_dolum | 1132 | 0 | 0 | 0 |
| gecikme_0dk_dolum | 1132 | 0 | 580 | 1.031e+05 |
| gecikme_5dk_eksik_dolum | 1132 | 0 | 0 | 6356 |
| gecikme_5dk_dolum | 1132 | 0 | 580 | 1.031e+05 |
| gecikme_30dk_eksik_dolum | 1132 | 0 | 0 | 7530 |
| gecikme_30dk_dolum | 1132 | 0 | 580 | 1.031e+05 |
| gecikme_120dk_eksik_dolum | 1132 | 0 | 0 | 8414 |
| gecikme_120dk_dolum | 1132 | 0 | 576 | 1.031e+05 |
| gecikme_480dk_eksik_dolum | 1132 | 0 | 0 | 1.08e+04 |
| gecikme_480dk_dolum | 1132 | 0 | 574.5 | 1.031e+05 |
| kisa_islem_payi | 917 | 0 | 0.137 | 1 |
| son90_dongu | 1132 | 0 | 4 | 4245 |
| son_islem_gun | 964 | -0.1 | 6.5 | 359.1 |
| aktif | 1132 | 0 | 0 | 1 |
| gece_payi | 917 | 0 | 0.25 | 1 |
| gecikme_gun | 1041 | 0.1 | 187.8 | 200 |
| kopya_eksik | 1132 | 0 | 0 | 1 |
| kopya_eksik_orani | 1132 | 0 | 0 | 0.6977 |
| dolum_siniri | 1132 | 0 | 0 | 1 |
| pay_kripto | 1132 | 0 | 0.8121 | 1 |
| pay_hisse | 1132 | 0 | 0 | 1 |
| pay_endeks | 1132 | 0 | 0 | 1 |
| pay_emtia | 1132 | 0 | 0 | 1 |
| plasebo_p | 26 | 0.0006999 | 0.1076 | 0.9259 |
| kapi_gecikme_dk | 1132 | 30 | 30 | 120 |
| alfa_yillik | 858 | -3.599 | 0.02373 | 26.78 |
| nw_t | 858 | -5.814 | 0.4474 | 5.814 |
| gecikme_0dk_net | 1132 | -0.8964 | 0 | 13.87 |
| gecikme_5dk_net | 1132 | -0.9016 | 0 | 14.55 |
| gecikme_30dk_net | 1132 | -0.8804 | 0 | 20.84 |
| gecikme_120dk_net | 1132 | -0.9641 | 0 | 25.74 |
| gecikme_480dk_net | 1132 | -0.9087 | 0 | 83.22 |
| sure_portfolio_sn | 15131 | 0.1 | 0.3 | 49.8 |
| sure_hesap_sn | 2961 | 1.4 | 2.1 | 50.5 |
| sure_fills_sn | 1353 | 0.1 | 3.6 | 537.7 |
| sure_funding_sn | 1353 | 0.1 | 0.7 | 352.6 |
| sure_mumlar_sn | 1197 | 0 | 0.9 | 1309 |
| sure_metrik_sn | 1132 | 0 | 0.2 | 18.2 |
| sure_plasebo_sn | 1132 | 0 | 0 | 3066 |
| sure_alfa_sn | 1132 | 0 | 0.4 | 54.8 |
| sure_toplam_sn | 15131 | 0.1 | 0.3 | 3504 |
| sure_yeni_mum_istegi | 15131 | 0 | 0 | 227 |
| plasebo_gercek_skor | 26 | -0.4226 | 0.1388 | 1.213 |
| bhy_q | 26 | 0.07014 | 0.798 | 1 |
| gecmis_gun | 14786 | 27 | 475.5 | 1337 |
| binance_payi | 2 | 0 | 0.4349 | 0.8698 |
