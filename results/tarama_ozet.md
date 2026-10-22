# Asama 1 tarama ozeti (T5b-1: gunluk/haftalik kartlar)

Donem: IS 2020-01-01 -> 2024-09-30 (OOS ve 2015-2019 kullanilmadi). Maliyet 1x ve 2x (ELEME_KRITERLERI baz tablosu).
Gecis kurali: en az bir piyasada islem >= 30, 1x PF >= 1.1, 2x net > 0.

Kart: 42 | Asama 2 adayi: 35 | Dogrulanamaz: 3 | Reddedildi (asama 1): 4

## Karar tablosu

| Kart | Karar | Ayrinti |
|---|---|---|
| A2-007 | Reddedildi (asama 1) | BIST30: islem<30; ABD25: islem<30; KRIPTO25: islem<30; EMTIA: islem<30 |
| A3-003 | Reddedildi (asama 1) | ABD25: islem<30,PF_1x<1.1,net_2x<=0; KRIPTO25: islem<30,PF_1x<1.1,net_2x<=0 |
| A3-007 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| A3-008a | Asama 2 adayi | KRIPTO25 |
| A3-008b | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| A3-009a | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| A3-009b | Asama 2 adayi | ABD25,EMTIA |
| A3-009c | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| A5-009 | Asama 2 adayi | ABD25 |
| A6-001 | Asama 2 adayi | BIST30,ABD25,EMTIA |
| A6-010 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| B1-002 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| B3-010 | Asama 2 adayi | ABD25,EMTIA |
| C01 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| C02 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| O1-001 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| O1-038 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| O1-066 | Asama 2 adayi | BIST30,ABD25,KRIPTO25 |
| O1-075 | Asama 2 adayi | EMTIA |
| O1-078 | Dogrulanamaz | motor_destegi_yok:iz_suren.fiyat_adim; piyasa_ozgu:ABD |
| O1-079 | Asama 2 adayi | BIST30,ABD25,KRIPTO25 |
| O3-007 | Asama 2 adayi | BIST30,ABD25,KRIPTO25 |
| O3-014 | Reddedildi (asama 1) | BIST30: PF_1x<1.1,net_2x<=0; ABD25: PF_1x<1.1,net_2x<=0; KRIPTO25: PF_1x<1.1,net_2x<=0; EMTIA: PF_1x<1.1,net_2x<=0 |
| O3-015 | Reddedildi (asama 1) | BIST30: net_2x<=0; ABD25: net_2x<=0; KRIPTO25: PF_1x<1.1,net_2x<=0; EMTIA: PF_1x<1.1,net_2x<=0 |
| P01 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P02 | Dogrulanamaz | motor_destegi_yok:kismi_kar |
| P3-001 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P3-002 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P3-003 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P3-004 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P3-005 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P3-007 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| P3-011 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| R01 | Dogrulanamaz | motor_destegi_yok:kismi_kar |
| R02 | Asama 2 adayi | BIST30 |
| R05 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| T8-01 | Asama 2 adayi | BIST30,ABD25,KRIPTO25 |
| T8-02 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| T8-04 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| T8-05 | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| V1A | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |
| V1B | Asama 2 adayi | BIST30,ABD25,KRIPTO25,EMTIA |

## PF > 4 alarmi (asiri uyum suphesi)

- A3-008a / BIST30: PF_1x=19.28, islem=17
- A3-008a / EMTIA: PF_1x=5.36, islem=18
- A3-009a / BIST30: PF_1x=5.95, islem=104
- A3-009c / BIST30: PF_1x=21.77, islem=30
- A3-009c / ABD25: PF_1x=4.46, islem=48
- B1-002 / BIST30: PF_1x=4.36, islem=94
- O1-001 / BIST30: PF_1x=4.36, islem=94
- O1-038 / BIST30: PF_1x=6.44, islem=67
- O1-066 / BIST30: PF_1x=8.26, islem=32
- O1-066 / KRIPTO25: PF_1x=4.61, islem=31
- P3-007 / BIST30: PF_1x=6.78, islem=57

## Kapanis dolumu (MOC) kartlari: (a) kapanis 2x maliyet | (b) ertesi acilis

| Kart | Piyasa | (a) PF_1x | (a) net_1x | (b) PF_1x | (b) net_1x | Not |
|---|---|---:|---:|---:|---:|---|
| O3-007 | BIST30 | 1.37 | 10.72% | 1.53 | 14.57% |  |
| O3-007 | ABD25 | 1.16 | 4.94% | 1.24 | 7.69% |  |
| O3-007 | KRIPTO25 | 1.51 | 9.50% | 1.62 | 11.17% |  |
| O3-007 | EMTIA | 0.76 | -7.83% | 0.93 | -2.15% | Kosullu (b negatif) |
| O3-014 | BIST30 | 0.60 | -32.45% | 0.97 | -2.67% | Kosullu (b negatif) |
| O3-014 | ABD25 | 0.90 | -8.08% | 1.11 | 9.14% |  |
| O3-014 | KRIPTO25 | 0.77 | -17.90% | 0.91 | -7.02% | Kosullu (b negatif) |
| O3-014 | EMTIA | 0.70 | -8.63% | 0.76 | -8.73% | Kosullu (b negatif) |
| O3-015 | BIST30 | 1.10 | 8.44% | 1.29 | 25.47% |  |
| O3-015 | ABD25 | 1.11 | 10.81% | 1.28 | 27.60% |  |
| O3-015 | KRIPTO25 | 1.02 | 2.16% | 1.11 | 11.50% |  |
| O3-015 | EMTIA | 0.99 | -0.68% | 1.10 | 7.08% |  |

## Atlanan / dogrulanamayan satirlar

| Neden | Satir sayisi |
|---|---:|
| endeks_yok:BIST30 | 1 |
| endeks_yok:EMTIA | 1 |
| motor_destegi_yok:iz_suren.fiyat_adim | 1 |
| motor_destegi_yok:kismi_kar | 8 |
| piyasa_ozgu:ABD | 3 |

## Notlar

- Evren gunumuzun buyuk sirketleridir (survivorship yanliligi); BIST/ABD sonuclari en fazla Kosullu sayilir.
- BIST30 ve EMTIA icin endeks serisi yok: `endeks_close` kullanan kartlar bu piyasalarda Dogrulanamaz.
- Cikis alan anlamlari: docs/EVRENSEL_KURALLAR.md D5.
