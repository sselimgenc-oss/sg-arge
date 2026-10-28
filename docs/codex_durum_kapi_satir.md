# Tam kapı satır teşhisi

Run: `40711594322` · gün: `2026-10-28`.

| Parça | Plan | İşlenen (bitti/log) | sonuc.csv | plan listesi | CSV−plan | plan−CSV | bitti.json |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| 0 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 1 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 2 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 3 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 4 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 5 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 6 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 7 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 8 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 9 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 10 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 11 | 423 | — | 389 | 92 | 386 | 89 | hayır |
| 12 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 13 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 14 | 423 | — | 182 | 92 | 179 | 89 | hayır |
| 15 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 16 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 17 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 18 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 19 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 20 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 21 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 22 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 23 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 24 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 25 | 423 | 423 | 423 | 423 | 0 | 0 | evet |
| 26 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 27 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 28 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 29 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 30 | 422 | 422 | 422 | 422 | 0 | 0 | evet |
| 31 | 422 | 422 | 422 | 422 | 0 | 0 | evet |

## Adres kümeleri

- Parça CSV toplamı: **13253**; tekil adres: **10061**; yinelenen satır: **3192**.
- Plan listesi toplamı: **12866**; tekil plan adresi: **9834**.
- `evren.json`: [13525, 13530]; tüm parçalarda aynı sayı: **hayır**.
- Boş/NaN address: **0**; yalnız büyük-küçük harften doğan ek çakışma: **0**.

### Parçalar arası kesişim

Çakışan parça çifti: **85**; çift-kesişim toplamı: **3192**.

| Parça A | Parça B | Ortak adres |
| ---: | ---: | ---: |
| 0 | 2 | 32 |
| 0 | 3 | 39 |
| 0 | 4 | 2 |
| 0 | 26 | 69 |
| 0 | 27 | 68 |

### Yinelenen adres örnekleri

| Adres | Parçalar |
| :--- | :--- |
| `0x00b724c689302b8eaad32a216f12a73b13d582cf` | 25, 26 |
| `0x00c3505d97ac9c16b1093e6be8e92b9e84ff2a0a` | 29, 30 |
| `0x00da40a7f1e25f8c1472a6760fccde10ee6d303a` | 1, 2 |
| `0x00fae28ab31daa75bda0249e8b10b30d56c4e47f` | 13, 14 |
| `0x01307fb492ef88e11a7e969ca84cabe16d8fea8e` | 25, 26 |
| `0x013f901e4794a3668d1fb2ed2078a3c5b135228a` | 29, 30 |
| `0x015354106478dda69c4aae3c0cf801290b738052` | 1, 2 |
| `0x01a996ef408d6197dba7820b6195b39109102c4f` | 13, 14 |
| `0x01cd055a4c422cd498d35c3691e965819758d479` | 25, 26 |
| `0x01dbf331f17b290ccda3f6d17bafe6a03a70f6eb` | 29, 30 |

## Bulgu

Tamamlanan parçalarda plan, bitti ve CSV sayıları eşitse satır parça içinde kaybolmamıştır. Ortak evren her işte yeniden API'den üretildiği için `evren.json` yalnız aynı **sayının** geldiğini gösterir; plan listelerindeki kesişimler farklı anlık görüntülerin aynı adresleri ayrı parçalara koyduğunu kanıtlar. Birleştirmedeki `drop_duplicates("address")` bu çakışan satırları tekile indirir.

Düzeltme: plan işi adres listesini içeren ortak anlık görüntü üretir; her `stage1` işi bu dosyadan kendi sabit dilimini seçer. Eşik, kapı ve karar hesabı değişmez.
