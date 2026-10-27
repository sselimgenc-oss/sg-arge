# Trader sayfası — altın örnekler

## Dört dolumlu tek işlem

| Zaman | İşlem | Fiyat | `closedPnl` | Ücret |
|---|---:|---:|---:|---:|
| 10:00 | 1 al | 100 | 0 | 0,10 |
| 10:05 | 1 al | 110 | 0 | 0,11 |
| 11:00 | 1 sat | 120 | 20 | 0,12 |
| 11:05 | 1 sat | 130 | 20 | 0,13 |

Giriş = `(1×100 + 1×110) / 2 = 105`; giriş tutarı `210`.
Kapanış = `(1×120 + 1×130) / 2 = 125`.
Toplam sonuç = `(20 + 20 − 0,10 − 0,11 − 0,12 − 0,13) / 210 = 0,188285… = +%18,83`.

## Ters dönüş

| Zaman | İşlem | Fiyat | `closedPnl` | Ücret |
|---|---:|---:|---:|---:|
| 10:00 | 1 al | 100 | 0 | 0,10 |
| 11:00 | 2 sat | 110 | 10 | 0,22 |

İkinci işlem önce long işlemi kapatır, ardından yeni short açar.
Kapanan long sonucu = `(10 − 0,10 − 0,11) / 100 = +%9,79`; kalan `0,11` ücret yeni açık short'a yazılır.
