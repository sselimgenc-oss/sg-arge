# U1 huni ozeti

v1 tablo: bilgi, eleme değil; karar: results/u7/huni_ozet.csv karar_adim2.

IS: null testi (havuz, 14 coin); OOS: maliyet, +1 bar gecikme, bootstrap MDD95, DSR, kardes raporu. Kilitli donem acilmadi.

Karar sayilari: Reddedildi: 6

| varyant | tf | IS islem | null | OOS islem | OOS PF 1x/2x/3x | +1 bar net | MDD95 | DSR | kardes | en buyuk pay | en iyi ay haric PF | karar | neden |
|---|---|---:|---|---:|---|---:|---:|---:|---|---:|---:|---|---|
| U1-H2-A[tf=5m_carpan=3] | 5m | 10412 | True | 9433 | 0.41/0.16/0.05 | -1.000 | 1.000 | 0.000 | 0/8 | - | 0.41 | Reddedildi | OOS ortR<=0, 2x PF<1.2, 3x net<=0, +1 bar net<=0, bootstrap MDD95>%15, kardes PF>1,1 orani<%60 (0/8) |
| U1-H2-A[tf=5m_carpan=5] | 5m | 7846 | True | 6960 | 0.49/0.26/0.12 | -1.000 | 1.000 | 0.000 | 0/8 | - | 0.49 | Reddedildi | OOS ortR<=0, 2x PF<1.2, 3x net<=0, +1 bar net<=0, bootstrap MDD95>%15, kardes PF>1,1 orani<%60 (0/8) |
| U1-H2-B[tf=5m_cikis_saati=17:00] | 5m | 2860 | True | 2340 | 0.52/0.29/0.18 | -0.973 | 0.986 | 0.000 | 0/8 | - | 0.47 | Reddedildi | OOS ortR<=0, 2x PF<1.2, 3x net<=0, +1 bar net<=0, bootstrap MDD95>%15, kardes PF>1,1 orani<%60 (0/8) |
| U1-H2-B[tf=5m_cikis_saati=20:00] | 5m | 2838 | True | 2342 | 0.66/0.41/0.27 | -0.959 | 0.983 | 0.000 | 0/8 | - | 0.54 | Reddedildi | OOS ortR<=0, 2x PF<1.2, 3x net<=0, +1 bar net<=0, bootstrap MDD95>%15, kardes PF>1,1 orani<%60 (0/8) |
| U1-H2-C[tf=5m_n=12] | 5m | 22195 | False | 19084 | 0.40/0.20/0.11 | -1.000 | 1.000 | 0.000 | 0/8 | - | 0.40 | Reddedildi | null, OOS ortR<=0, 2x PF<1.2, 3x net<=0, +1 bar net<=0, bootstrap MDD95>%15, kardes PF>1,1 orani<%60 (0/8) |
| U1-H2-C[tf=5m_n=24] | 5m | 17471 | False | 14974 | 0.39/0.22/0.13 | -1.000 | 1.000 | 0.000 | 0/8 | - | 0.39 | Reddedildi | null, OOS ortR<=0, 2x PF<1.2, 3x net<=0, +1 bar net<=0, bootstrap MDD95>%15, kardes PF>1,1 orani<%60 (0/8) |
