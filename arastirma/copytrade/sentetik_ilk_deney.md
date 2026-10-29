# Sentetik doğrulama — ilk deney

Bu deney `copytrade.sentetik` ile yürütülen araştırma çıktısıdır. Kapı, eşik,
seçim puanı veya canlı izleme davranışını değiştirmez.

## Düzenek

- Tekrar: 200
- Ana tohum: `20261028` (her tekrarın veri ve şans tohumu bu üreticiden türetilir)
- Trader / gün: 100 / 252
- Gerçek yetenek oranı: %20; günlük alfa: %0,08; günlük oynaklık: %1,5
- Seçim: en yüksek 20 trader
- Şans açık senaryosu: yalnız yeteneksizlerin %10'una, son 10 günün birinde
  tek seferlik %8 getiri eklendi.
- Puanlar:
  - **Ortalama getiri:** günlük getiri ortalaması.
  - **Sharpe:** ortalama / günlük standart sapma (`ddof=0`).
  - **En iyi gün hariç ortalama:** `(toplam − en iyi gün) / 251`.

`isabet`, seçilen 20 trader içindeki gerçek yetenekli payıdır. `şanslı seçme
oranı`, tekrarlar boyunca seçilen 20 trader içindeki şanslı trader payıdır;
şans kapalıyken tanım gereği sıfırdır.

## Sonuç

| Puanlama | Şans | Ortalama isabet | Şanslı seçme oranı |
|---|---:|---:|---:|
| Ortalama getiri | kapalı | 0,4172 | 0,0000 |
| Ortalama getiri | açık | 0,4067 | 0,0888 |
| Sharpe | kapalı | 0,4190 | 0,0000 |
| Sharpe | açık | 0,4098 | 0,0842 |
| En iyi gün hariç ortalama | kapalı | 0,4182 | 0,0000 |
| En iyi gün hariç ortalama | açık | 0,4130 | 0,0735 |

Bu tek parametrik düzenekte en iyi günü hariç tutmak, şanslı trader seçimini
ortalama getiriye göre 1,53 yüzde puan, Sharpe'a göre 1,07 yüzde puan azalttı.
Bu gözlem yalnız bu veri üretim modeline aittir; canlı seçim kuralı için karar
ya da eşik önerisi değildir.
