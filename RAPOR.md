# Trader seçimi örneklem dışı doğrulama (walk-forward) — RAPOR

**Özet (teknik olmayan okuyucu için):**
1. Ana hüküm (A kolu, spec kuralları): **Birinci turda GEÇMEDİ (kurallar şu haliyle değer katmıyor; tek revizyon hakkı kullanıcıda)**.
2. Şart 1 (seçilenlerin ortanca getirisi rastgele çekilişlerin %90'ından iyi mi): +6% → hayır.
3. Şart 2 (tarihlerin en az 8/11'inde kontrolden iyi): 1 → hayır.
4. Şart 3 (maliyet sonrası ortanca getiri > 0): -2.0% → hayır (getiri = 4 haftada 200 $ slota göre).
5. B: 1. tur GEÇMEDİ (T12 kilitli; tek revizyon hakkı kullanıcıda) — şart1 yüzdelik +10% (≥%90), şart2 3/11 (≥8), şart3 ortanca -2.0% (> 0).
6. C: 1. tur GEÇMEDİ (T12 kilitli; tek revizyon hakkı kullanıcıda) — şart1 yüzdelik +80% (≥%90), şart2 7/11 (≥8), şart3 ortanca +0.2% (> 0).
7. D: 1. tur GEÇMEDİ (T12 kilitli; tek revizyon hakkı kullanıcıda) — şart1 yüzdelik +6% (≥%90), şart2 3/11 (≥8), şart3 ortanca -1.4% (> 0).
8. Bugünkü aday havuzu: A 4, B 3, C 0 (yalnız örneklemden), D 8 kişi.
9. Mutlak getiriler hayatta kalma yanlılığı yüzünden şişkin olabilir; yalnız seçilen − kontrol farkı yorumlanmalı.
10. 4 haftalık pencereler örtüştüğü için 12 tarih ≈ 3.8 bağımsız dönemdir; sonuç istatistiksel olarak zayıf kanıttır.

_Tur: tur1. Çapa (şimdi): 2026-11-11 22:00 UTC. Slot 200 $; getiri ve düşüşler slot oranıdır._

## Boyutlar
- lider_tablosu: 48230
- bugun_10k_ustu_islemli: 16092
- bugun_10k_alti_buyuk_zarar_ya_da_hacim: 18641
- evren: 34733
- portfolio_okunan: 34733
- k50_herhangi_T: 8749
- k10_herhangi_T: 11748
- ornek50: 700
- ornek10: 300
- ucuz_kural_adayi_(>=10k ve kural2, herhangi T): 2252
- dolum_seti: 3033

## Kol A — spec kuralları (hesap ≥ 50k)

- Tur 1 (T1–T11): {"s1_yuzdelik": 0.063, "s2_iyi": 1, "s2_gerek": 8, "s3_ortanca": -0.019519596535254036, "gecti": false}
- T12: kilitli (1. tur geçmedi: revizyon kullanıcı kararı; `python calistir.py --t12-ac A` ile mevcut kurallarla açılır)

| T | tarih | seçilen | kontrol | çıkarılan (aday/kontrol) | seçilen ortanca | kontrol ortanca | yüzdelik sıra | en büyük düşüş | ilk 5 ortanca (yüzdelik) |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2026-07-29 | 6 | 180 | 161/80 | -0.5% | +0.0% | 13 | +19.0% | +2.5% (96) |
| T2 | 2026-08-05 | 2 | 177 | 150/69 | -2.8% | +0.0% | 22 | +10.1% | -2.8% (17) |
| T3 | 2026-08-12 | 5 | 191 | 161/66 | -3.5% | +0.0% | 4 | +14.3% | -3.5% (3) |
| T4 | 2026-08-19 | 2 | 176 | 151/65 | -11.8% | +0.0% | 10 | +27.9% | -11.8% (11) |
| T5 | 2026-08-26 | 2 | 208 | 153/73 | -2.3% | +0.0% | 15 | +11.1% | -2.3% (14) |
| T6 | 2026-09-02 | 7 | 231 | 164/93 | -1.0% | +0.0% | 0 | +28.4% | -4.9% (0) |
| T7 | 2026-09-09 | 6 | 236 | 178/78 | -3.1% | +0.0% | 1 | +37.9% | -8.1% (0) |
| T8 | 2026-09-16 | 8 | 254 | 183/88 | -2.0% | +0.0% | 2 | +36.2% | -2.1% (4) |
| T9 | 2026-09-23 | 5 | 234 | 169/65 | +0.0% | +0.0% | 91 | +12.6% | +0.0% (93) |
| T10 | 2026-09-30 | 3 | 274 | 192/82 | +0.0% | +0.0% | 61 | +3.9% | +0.0% (60) |
| T11 | 2026-10-07 | 3 | 293 | 183/73 | -2.9% | +0.0% | 20 | +9.0% | -2.9% (18) |

<details><summary>İlk 5 (t-istatistiği sırası) — her T</summary>

- T1 2026-07-29: 0xf25df197… t=2.23 getiri -18.0% düşüş +19.0%; 0xfdb03a25… t=1.65 getiri +5.2% düşüş +2.8%; 0x4b6d234f… t=1.10 getiri -10.2% düşüş +13.0%; 0xed7c40e1… t=1.04 getiri +6.3% düşüş +4.5%; 0x4c921317… t=0.48 getiri +2.5% düşüş +0.4%
- T2 2026-08-05: 0xac5c66fb… t=4.68 getiri +3.9% düşüş +0.0%; 0xc0ad5d21… t=1.76 getiri -9.4% düşüş +10.1%
- T3 2026-08-12: 0x4b6d234f… t=2.26 getiri -12.7% düşüş +13.0%; 0xc0ad5d21… t=2.02 getiri -9.0% düşüş +9.2%; 0x1c1083dd… t=1.93 getiri +9.4% düşüş +3.4%; 0x5beae772… t=1.71 getiri -3.5% düşüş +14.3%; 0x4c921317… t=0.44 getiri +1.1% düşüş +0.0%
- T4 2026-08-19: 0x5beae772… t=1.88 getiri -27.9% düşüş +27.9%; 0xa9062f5b… t=1.82 getiri +4.3% düşüş +7.5%
- T5 2026-08-26: 0x1c1083dd… t=1.52 getiri -6.6% düşüş +11.1%; 0x94484626… t=1.15 getiri +2.0% düşüş +0.5%
- T6 2026-09-02: 0x0a28e545… t=2.67 getiri -4.9% düşüş +11.3%; 0x1c1083dd… t=1.48 getiri -8.8% düşüş +11.5%; 0x01d8296a… t=1.39 getiri +3.1% düşüş +3.8%; 0x7f24852f… t=1.00 getiri +0.0% düşüş +4.4%; 0x2a0b9f2f… t=0.89 getiri -20.8% düşüş +28.4%
- T7 2026-09-09: 0x2a0b9f2f… t=1.73 getiri -19.6% düşüş +25.0%; 0x8f8f014e… t=1.73 getiri +12.6% düşüş +4.1%; 0x01d8296a… t=1.63 getiri +4.2% düşüş +3.8%; 0xf37bb31d… t=1.50 getiri -27.8% düşüş +37.9%; 0x1c1083dd… t=1.13 getiri -8.1% düşüş +8.4%
- T8 2026-09-16: 0x8f8f014e… t=2.32 getiri -1.0% düşüş +9.2%; 0xf37bb31d… t=2.03 getiri -35.4% düşüş +36.2%; 0x1c1083dd… t=1.79 getiri -13.2% düşüş +13.4%; 0x7f24852f… t=1.74 getiri +8.2% düşüş +1.7%; 0xdd14ff1c… t=1.45 getiri -2.1% düşüş +6.3%
- T9 2026-09-23: 0x8f8f014e… t=3.47 getiri -4.9% düşüş +12.6%; 0x0a28e545… t=2.18 getiri -7.6% düşüş +10.8%; 0x7f24852f… t=1.61 getiri +5.9% düşüş +1.3%; 0xc1791da8… t=1.59 getiri +0.0% düşüş +0.7%; 0xa12156da… t=1.31 getiri +2.4% düşüş +0.4%
- T10 2026-09-30: 0x94484626… t=3.01 getiri -3.6% düşüş +3.7%; 0x399ccf8a… t=2.16 getiri +0.9% düşüş +3.9%; 0xc1791da8… t=1.96 getiri +0.0% düşüş +0.0%
- T11 2026-10-07: 0x399ccf8a… t=2.20 getiri -5.8% düşüş +9.0%; 0x21a1faec… t=1.80 getiri -2.9% düşüş +5.6%; 0x8950868c… t=-0.24 getiri -0.5% düşüş +0.7%

</details>

**Bugünkü aday havuzu (A, 4 kişi)**

| adres | hesap $ | t | kopya getirisi 28g (slot) | kopya işlem 28g / 56g | devir (x/hafta) | tutma (dk) | kaldıraç | veto |
|---|---|---|---|---|---|---|---|---|
| 0x1a19f1eb20023906accb989289645a5bf6300562 | 104,663 | 1.27 | +2.8% | 3 / 7 | 0.8 | 1298 | 0.38 | - |
| 0x915f49be1efad69bf644a500274db9b7ec24840f | 82,521 | 1.21 | +8.2% | 46 / 97 | 13.0 | 524 | 1.57 | - |
| 0xe69a487b1b9b74122dc8e6afc5fc046aca799125 | 113,182 | 1.00 | +19.6% | 4 / 6 | 3.2 | 1438 | 1.60 | veto_zarara_ekleme |
| 0x4854b8835c434edf95adf27f81ab9588ca6739be | 156,528 | 0.62 | +0.8% | 7 / 11 | 1.4 | 470 | 0.58 | - |

## Kol B — A + iki veto

- Tur 1 (T1–T11): {"s1_yuzdelik": 0.101, "s2_iyi": 3, "s2_gerek": 8, "s3_ortanca": -0.020014908157048317, "gecti": false}
- T12: kilitli (1. tur geçmedi: revizyon kullanıcı kararı; `python calistir.py --t12-ac B` ile mevcut kurallarla açılır)

| T | tarih | seçilen | kontrol | çıkarılan (aday/kontrol) | seçilen ortanca | kontrol ortanca | yüzdelik sıra | en büyük düşüş | ilk 5 ortanca (yüzdelik) |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2026-07-29 | 4 | 180 | 161/80 | -6.9% | +0.0% | 2 | +19.0% | -6.9% (2) |
| T2 | 2026-08-05 | 1 | 177 | 150/69 | +3.9% | +0.0% | 86 | +0.0% | +3.9% (85) |
| T3 | 2026-08-12 | 3 | 191 | 161/66 | -3.5% | +0.0% | 5 | +14.3% | -3.5% (6) |
| T4 | 2026-08-19 | 2 | 176 | 151/65 | -11.8% | +0.0% | 11 | +27.9% | -11.8% (9) |
| T5 | 2026-08-26 | 2 | 208 | 153/73 | -2.3% | +0.0% | 12 | +11.1% | -2.3% (13) |
| T6 | 2026-09-02 | 6 | 231 | 164/93 | -2.4% | +0.0% | 1 | +28.4% | -4.9% (0) |
| T7 | 2026-09-09 | 5 | 236 | 178/78 | +1.9% | +0.0% | 92 | +25.0% | +1.9% (92) |
| T8 | 2026-09-16 | 7 | 254 | 183/88 | -2.0% | +0.0% | 3 | +20.5% | -2.0% (6) |
| T9 | 2026-09-23 | 5 | 234 | 169/65 | +0.0% | +0.0% | 93 | +12.6% | +0.0% (92) |
| T10 | 2026-09-30 | 3 | 274 | 192/82 | +0.0% | +0.0% | 62 | +3.9% | +0.0% (62) |
| T11 | 2026-10-07 | 2 | 293 | 183/73 | -4.4% | +0.0% | 32 | +9.0% | -4.4% (33) |

<details><summary>İlk 5 (t-istatistiği sırası) — her T</summary>

- T1 2026-07-29: 0xf25df197… t=2.23 getiri -18.0% düşüş +19.0%; 0x4b6d234f… t=1.10 getiri -10.2% düşüş +13.0%; 0xed7c40e1… t=1.04 getiri +6.3% düşüş +4.5%; 0x009fdc04… t=0.35 getiri -3.6% düşüş +8.7%
- T2 2026-08-05: 0xac5c66fb… t=4.68 getiri +3.9% düşüş +0.0%
- T3 2026-08-12: 0x4b6d234f… t=2.26 getiri -12.7% düşüş +13.0%; 0x1c1083dd… t=1.93 getiri +9.4% düşüş +3.4%; 0x5beae772… t=1.71 getiri -3.5% düşüş +14.3%
- T4 2026-08-19: 0x5beae772… t=1.88 getiri -27.9% düşüş +27.9%; 0xa9062f5b… t=1.82 getiri +4.3% düşüş +7.5%
- T5 2026-08-26: 0x1c1083dd… t=1.52 getiri -6.6% düşüş +11.1%; 0x94484626… t=1.15 getiri +2.0% düşüş +0.5%
- T6 2026-09-02: 0x0a28e545… t=2.67 getiri -4.9% düşüş +11.3%; 0x1c1083dd… t=1.48 getiri -8.8% düşüş +11.5%; 0x01d8296a… t=1.39 getiri +3.1% düşüş +3.8%; 0x7f24852f… t=1.00 getiri +0.0% düşüş +4.4%; 0x2a0b9f2f… t=0.89 getiri -20.8% düşüş +28.4%
- T7 2026-09-09: 0x2a0b9f2f… t=1.73 getiri -19.6% düşüş +25.0%; 0x8f8f014e… t=1.73 getiri +12.6% düşüş +4.1%; 0x01d8296a… t=1.63 getiri +4.2% düşüş +3.8%; 0x1c1083dd… t=1.13 getiri -8.1% düşüş +8.4%; 0x7f24852f… t=1.00 getiri +1.9% düşüş +2.5%
- T8 2026-09-16: 0x8f8f014e… t=2.32 getiri -1.0% düşüş +9.2%; 0x1c1083dd… t=1.79 getiri -13.2% düşüş +13.4%; 0x7f24852f… t=1.74 getiri +8.2% düşüş +1.7%; 0xdd14ff1c… t=1.45 getiri -2.1% düşüş +6.3%; 0x01d8296a… t=1.31 getiri -2.0% düşüş +6.7%
- T9 2026-09-23: 0x8f8f014e… t=3.47 getiri -4.9% düşüş +12.6%; 0x0a28e545… t=2.18 getiri -7.6% düşüş +10.8%; 0x7f24852f… t=1.61 getiri +5.9% düşüş +1.3%; 0xc1791da8… t=1.59 getiri +0.0% düşüş +0.7%; 0xa12156da… t=1.31 getiri +2.4% düşüş +0.4%
- T10 2026-09-30: 0x94484626… t=3.01 getiri -3.6% düşüş +3.7%; 0x399ccf8a… t=2.16 getiri +0.9% düşüş +3.9%; 0xc1791da8… t=1.96 getiri +0.0% düşüş +0.0%
- T11 2026-10-07: 0x399ccf8a… t=2.20 getiri -5.8% düşüş +9.0%; 0x21a1faec… t=1.80 getiri -2.9% düşüş +5.6%

</details>

**Bugünkü aday havuzu (B, 3 kişi)**

| adres | hesap $ | t | kopya getirisi 28g (slot) | kopya işlem 28g / 56g | devir (x/hafta) | tutma (dk) | kaldıraç | veto |
|---|---|---|---|---|---|---|---|---|
| 0x1a19f1eb20023906accb989289645a5bf6300562 | 104,663 | 1.27 | +2.8% | 3 / 7 | 0.8 | 1298 | 0.38 | - |
| 0x915f49be1efad69bf644a500274db9b7ec24840f | 82,521 | 1.21 | +8.2% | 46 / 97 | 13.0 | 524 | 1.57 | - |
| 0x4854b8835c434edf95adf27f81ab9588ca6739be | 156,528 | 0.62 | +0.8% | 7 / 11 | 1.4 | 470 | 0.58 | - |

## Kol C — yalnız kopyalanabilirlik kapıları (3–7) + vetolar, sıralama yok

- Tur 1 (T1–T11): {"s1_yuzdelik": 0.801, "s2_iyi": 7, "s2_gerek": 8, "s3_ortanca": 0.0023780401883699565, "gecti": false}
- T12: kilitli (1. tur geçmedi: revizyon kullanıcı kararı; `python calistir.py --t12-ac C` ile mevcut kurallarla açılır)

| T | tarih | seçilen | kontrol | çıkarılan (aday/kontrol) | seçilen ortanca | kontrol ortanca | yüzdelik sıra | en büyük düşüş | ilk 5 ortanca (yüzdelik) |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2026-07-29 | 1 | 180 | 80/80 | -7.4% | +0.0% | 9 | +10.5% | — |
| T2 | 2026-08-05 | 2 | 177 | 69/69 | -4.2% | +0.0% | 17 | +10.5% | — |
| T3 | 2026-08-12 | 1 | 191 | 66/66 | -2.9% | +0.0% | 18 | +3.1% | — |
| T4 | 2026-08-19 | 1 | 176 | 65/65 | +9.5% | +0.0% | 92 | +3.1% | — |
| T5 | 2026-08-26 | 1 | 208 | 73/73 | +1.4% | +0.0% | 73 | +2.0% | — |
| T6 | 2026-09-02 | 2 | 231 | 93/93 | +1.8% | +0.0% | 64 | +11.3% | — |
| T7 | 2026-09-09 | 1 | 236 | 78/78 | +2.5% | +0.0% | 75 | +1.3% | — |
| T8 | 2026-09-16 | 1 | 254 | 88/88 | +20.7% | +0.0% | 100 | +3.1% | — |
| T9 | 2026-09-23 | 4 | 234 | 65/65 | +0.6% | +0.0% | 89 | +10.8% | — |
| T10 | 2026-09-30 | 2 | 274 | 82/82 | +0.4% | +0.0% | 82 | +1.6% | — |
| T11 | 2026-10-07 | 1 | 293 | 73/73 | -1.7% | +0.0% | 33 | +3.1% | — |

## Kol D — A, hesap ≥ 10k (bugünkü canlı eşik)

- Tur 1 (T1–T11): {"s1_yuzdelik": 0.056, "s2_iyi": 3, "s2_gerek": 8, "s3_ortanca": -0.0141185979636832, "gecti": false}
- T12: kilitli (1. tur geçmedi: revizyon kullanıcı kararı; `python calistir.py --t12-ac D` ile mevcut kurallarla açılır)

| T | tarih | seçilen | kontrol | çıkarılan (aday/kontrol) | seçilen ortanca | kontrol ortanca | yüzdelik sıra | en büyük düşüş | ilk 5 ortanca (yüzdelik) |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2026-07-29 | 9 | 87 | 206/26 | +0.7% | +0.0% | 88 | +19.0% | +3.8% (92) |
| T2 | 2026-08-05 | 5 | 84 | 192/23 | -9.4% | +0.0% | 3 | +13.7% | -9.4% (2) |
| T3 | 2026-08-12 | 8 | 88 | 198/26 | -3.6% | +0.0% | 2 | +36.9% | -3.7% (4) |
| T4 | 2026-08-19 | 6 | 84 | 193/29 | +3.0% | +0.0% | 97 | +27.9% | +4.3% (97) |
| T5 | 2026-08-26 | 8 | 106 | 191/31 | +4.2% | +0.0% | 91 | +15.9% | +4.7% (84) |
| T6 | 2026-09-02 | 11 | 122 | 201/33 | -1.0% | +0.0% | 2 | +28.4% | -4.9% (1) |
| T7 | 2026-09-09 | 9 | 120 | 216/34 | -2.0% | +0.0% | 0 | +37.9% | +1.3% (82) |
| T8 | 2026-09-16 | 11 | 120 | 225/35 | -2.0% | +0.0% | 1 | +36.2% | -1.9% (10) |
| T9 | 2026-09-23 | 8 | 116 | 206/29 | -0.3% | +0.0% | 41 | +12.6% | -2.9% (15) |
| T10 | 2026-09-30 | 7 | 116 | 244/29 | -1.3% | +0.0% | 27 | +19.8% | +0.0% (71) |
| T11 | 2026-10-07 | 10 | 119 | 229/27 | -1.7% | -1.1% | 39 | +20.1% | -2.9% (33) |

<details><summary>İlk 5 (t-istatistiği sırası) — her T</summary>

- T1 2026-07-29: 0xf25df197… t=2.23 getiri -18.0% düşüş +19.0%; 0xfdb03a25… t=1.65 getiri +5.2% düşüş +2.8%; 0xcff9c002… t=1.57 getiri +3.8% düşüş +4.8%; 0x4b6d234f… t=1.10 getiri -10.2% düşüş +13.0%; 0xed7c40e1… t=1.04 getiri +6.3% düşüş +4.5%
- T2 2026-08-05: 0xac5c66fb… t=4.68 getiri +3.9% düşüş +0.0%; 0xe006b02e… t=3.66 getiri -13.5% düşüş +13.7%; 0x4b6d234f… t=2.68 getiri -11.2% düşüş +13.0%; 0xc0ad5d21… t=1.76 getiri -9.4% düşüş +10.1%; 0x7630cc11… t=1.53 getiri -7.9% düşüş +12.3%
- T3 2026-08-12: 0x22dfa5d3… t=2.27 getiri -3.7% düşüş +5.3%; 0x4b6d234f… t=2.26 getiri -12.7% düşüş +13.0%; 0xc0ad5d21… t=2.02 getiri -9.0% düşüş +9.2%; 0x1c1083dd… t=1.93 getiri +9.4% düşüş +3.4%; 0x5beae772… t=1.71 getiri -3.5% düşüş +14.3%
- T4 2026-08-19: 0x22dfa5d3… t=2.48 getiri +1.8% düşüş +4.9%; 0x5beae772… t=1.88 getiri -27.9% düşüş +27.9%; 0xa9062f5b… t=1.82 getiri +4.3% düşüş +7.5%; 0x7f24852f… t=1.00 getiri +6.8% düşüş +9.7%; 0x424d756e… t=0.42 getiri +12.8% düşüş +2.4%
- T5 2026-08-26: 0x0a28e545… t=2.63 getiri +5.6% düşüş +11.6%; 0x75f0f24a… t=2.06 getiri +4.7% düşüş +2.1%; 0x22dfa5d3… t=1.95 getiri -15.9% düşüş +15.9%; 0xb1decfd7… t=1.57 getiri +12.8% düşüş +4.2%; 0x1c1083dd… t=1.52 getiri -6.6% düşüş +11.1%
- T6 2026-09-02: 0x0a28e545… t=2.67 getiri -4.9% düşüş +11.3%; 0x7b72875c… t=2.27 getiri -3.3% düşüş +11.8%; 0xde29121a… t=1.81 getiri -5.7% düşüş +10.3%; 0x1c1083dd… t=1.48 getiri -8.8% düşüş +11.5%; 0x01d8296a… t=1.39 getiri +3.1% düşüş +3.8%
- T7 2026-09-09: 0xde29121a… t=2.18 getiri +1.3% düşüş +10.3%; 0x2a0b9f2f… t=1.73 getiri -19.6% düşüş +25.0%; 0x8f8f014e… t=1.73 getiri +12.6% düşüş +4.1%; 0x01d8296a… t=1.63 getiri +4.2% düşüş +3.8%; 0xf37bb31d… t=1.50 getiri -27.8% düşüş +37.9%
- T8 2026-09-16: 0x8f8f014e… t=2.32 getiri -1.0% düşüş +9.2%; 0xf37bb31d… t=2.03 getiri -35.4% düşüş +36.2%; 0x1c1083dd… t=1.79 getiri -13.2% düşüş +13.4%; 0x7f24852f… t=1.74 getiri +8.2% düşüş +1.7%; 0xde29121a… t=1.70 getiri -1.9% düşüş +10.3%
- T9 2026-09-23: 0x8f8f014e… t=3.47 getiri -4.9% düşüş +12.6%; 0xde29121a… t=3.08 getiri -2.9% düşüş +10.4%; 0x0a28e545… t=2.18 getiri -7.6% düşüş +10.8%; 0x7f24852f… t=1.61 getiri +5.9% düşüş +1.3%; 0x888d5db3… t=1.61 getiri +5.2% düşüş +6.5%
- T10 2026-09-30: 0x37594c27… t=3.21 getiri -12.8% düşüş +19.8%; 0x94484626… t=3.01 getiri -3.6% düşüş +3.7%; 0x399ccf8a… t=2.16 getiri +0.9% düşüş +3.9%; 0xc1791da8… t=1.96 getiri +0.0% düşüş +0.0%; 0x888d5db3… t=1.95 getiri +14.6% düşüş +6.9%
- T11 2026-10-07: 0x37594c27… t=3.51 getiri -16.8% düşüş +19.5%; 0xf208ff0e… t=3.29 getiri +7.2% düşüş +20.1%; 0x888d5db3… t=2.25 getiri -0.1% düşüş +7.9%; 0x399ccf8a… t=2.20 getiri -5.8% düşüş +9.0%; 0x21a1faec… t=1.80 getiri -2.9% düşüş +5.6%

</details>

**Bugünkü aday havuzu (D, 8 kişi)**

| adres | hesap $ | t | kopya getirisi 28g (slot) | kopya işlem 28g / 56g | devir (x/hafta) | tutma (dk) | kaldıraç | veto |
|---|---|---|---|---|---|---|---|---|
| 0xc22db2c04e054786426671cec0b766c07304fb20 | 17,852 | 3.65 | +4.9% | 41 / 74 | 4.1 | 201 | 1.23 | veto_omur_zarar |
| 0xde29121a6858d90ae486855b127f9d5ee4035232 | 20,699 | 3.41 | +3.4% | 11 / 35 | 2.3 | 109 | 0.92 | veto_omur_zarar |
| 0x1f3aae75dfd99dee9890fcebe3fc3e48b633bf87 | 44,974 | 2.07 | +2.5% | 5 / 22 | 5.6 | 854 | 3.13 | - |
| 0x1a19f1eb20023906accb989289645a5bf6300562 | 104,663 | 1.27 | +2.8% | 3 / 7 | 0.8 | 1298 | 0.38 | - |
| 0x8c5676eb3ca69d96143b3a8ee02f706d56877dac | 20,675 | 1.27 | +3.8% | 4 / 16 | 5.9 | 36 | 2.22 | veto_omur_zarar |
| 0x915f49be1efad69bf644a500274db9b7ec24840f | 82,521 | 1.21 | +8.2% | 46 / 97 | 13.0 | 524 | 1.57 | - |
| 0xe69a487b1b9b74122dc8e6afc5fc046aca799125 | 113,182 | 1.00 | +19.6% | 4 / 6 | 3.2 | 1438 | 1.60 | veto_zarara_ekleme |
| 0x4854b8835c434edf95adf27f81ab9588ca6739be | 156,528 | 0.62 | +0.8% | 7 / 11 | 1.4 | 470 | 0.58 | - |

## Kol D (ikincil) — D seçilenleri 50k kontrol havuzuna karşı

- Tur 1 (T1–T11): {"s1_yuzdelik": 0.013, "s2_iyi": 3, "s2_gerek": 8, "s3_ortanca": -0.0141185979636832, "gecti": false}

| T | tarih | seçilen | kontrol | çıkarılan (aday/kontrol) | seçilen ortanca | kontrol ortanca | yüzdelik sıra | en büyük düşüş | ilk 5 ortanca (yüzdelik) |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2026-07-29 | 9 | 180 | 206/80 | +0.7% | +0.0% | 96 | +19.0% | +3.8% (96) |
| T2 | 2026-08-05 | 5 | 177 | 192/69 | -9.4% | +0.0% | 1 | +13.7% | -9.4% (0) |
| T3 | 2026-08-12 | 8 | 191 | 198/66 | -3.6% | +0.0% | 1 | +36.9% | -3.7% (2) |
| T4 | 2026-08-19 | 6 | 176 | 193/65 | +3.0% | +0.0% | 99 | +27.9% | +4.3% (99) |
| T5 | 2026-08-26 | 8 | 208 | 191/73 | +4.2% | +0.0% | 99 | +15.9% | +4.7% (97) |
| T6 | 2026-09-02 | 11 | 231 | 201/93 | -1.0% | +0.0% | 0 | +28.4% | -4.9% (0) |
| T7 | 2026-09-09 | 9 | 236 | 216/78 | -2.0% | +0.0% | 0 | +37.9% | +1.3% (89) |
| T8 | 2026-09-16 | 11 | 254 | 225/88 | -2.0% | +0.0% | 1 | +36.2% | -1.9% (6) |
| T9 | 2026-09-23 | 8 | 234 | 206/65 | -0.3% | +0.0% | 19 | +12.6% | -2.9% (5) |
| T10 | 2026-09-30 | 7 | 274 | 244/82 | -1.3% | +0.0% | 8 | +19.8% | +0.0% (60) |
| T11 | 2026-10-07 | 10 | 293 | 229/73 | -1.7% | +0.0% | 13 | +20.1% | -2.9% (13) |

## Yanlılıklar ve sınırlamalar

- **Hayatta kalma:** aday evreni bugünkü lider tablosundan kuruldu. Azaltmak için bugün < 10k olup ömür boyu ≥ 10k $ zarar etmiş ya da ≥ 50M $ hacimli hesaplar da evrene alındı; para çekip küçülmüş ya da lider tablosundan tamamen düşmüş hesaplar yine eksik. İki grup aynı evrenden geldiği için yalnız göreli fark yorumlanır; mutlak getiriler şişkin olabilir.
- **Dolum geçmişi:** adres başına en çok 10.000 dolum çekildi (en yeni kısım); geçmişi T − 56 g'ye yetmeyen hesaplar o T'de İKİ gruptan da çıkarıldı (tablolarda 'çıkarılan').
- **Bağımsız dönem:** haftalık kaydırmalı 12 tarih × 4 haftalık ileri pencere örtüşür; etkin bağımsız dönem ≈ 3–4.
- **Kopya yaklaşımı:** eski haftalar için 1 dk mum yok; kopya trader'ın dolum fiyatıyla (gecikmesiz) + tam maliyet (taker %0,045 + kayma %0,05) + saatlik funding; işaret ve tasfiye denetimi saatlik mumdan (kalicilik_testi yaklaşımı). Mutlak seviye gerçek gecikmeli kopyadan biraz iyimser; iki gruba aynı uygulanır.
- **Portfolio çözünürlüğü:** eski tarihlerde perp pnl/hesap serisi allTime'dan gelir (seyrek noktalar; T'den önceki son nokta kullanılır). K-65 'motor tanımı' payda düzeltmesi geçmişe uygulanamaz.
- **Azami kaldıraç (HL coin sınırı)** bugünkü meta değeridir; likidite her pencerenin saatlik mum hacminden (≥ 1M $/gün) ölçülür. HIP-3 coinleri kopyada atlanır (K-43), likidite kuralında sayılır.
- **Kontrol örneklemi:** kontrol havuzu, herhangi bir T'de kontrol tanımına uyan hesaplardan sabit tohumla rastgele 700 (50k) + 300 (10k, yalnız D) adresten oluşur; her T'de bunların o T'de tanıma uyanları. C kolu yalnız bu örneklem üzerinde ölçülür.

## Sonraki adım (yalnız öneri)

- Geçerse canlı başlangıç boyutu kullanıcı kararıdır: (a) 2 × 200 $ ile başla, 4 hafta uyumluysa 5 slota çık (düşük risk, yavaş kanıt); (b) doğrudan 5 × 200 $ (daha hızlı istatistik, 2,5 kat risk); (c) 3 × 200 $ ara yol. Geçmezse canlıya seçim kuralına güvenerek çıkılmamalı.
- Lider tablosunun **haftalık kaydı** bugünden başlatılmalı: haftada bir `stats-data.hyperliquid.xyz/Mainnet/leaderboard` tam yanıtı tarihli gzip olarak (ör. veri dalında `lider/YYYY-MM-DD.json.gz`) saklanır; ileride evren o tarihteki tablodan kurulur ve batmış hesaplar da görünür.

