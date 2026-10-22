# Composer parite kontrolu (T22)

Kart `rotasyon` kural agaci, Composer sayfasindaki kendi backtest serisinin (`backtestData`) gunluk getirileriyle karsilastirildi: maliyet 0, kapanis dolumu (Composer kapanista dolar), 2016-06-01 sonrasi.

| Kart | Gun | Korelasyon | En buyuk gunluk fark | Not |
|---|---:|---:|---:|---|
| A4-002 | 2612 | 1.00000 | 0.0005 | |
| A4-003 | 2612 | 1.00000 | 0.0005 | |
| A4-004 | 2612 | 1.00000 | 0.0063 | |
| A4-005 | 2612 | 1.00000 | 0.0003 | |
| M017 | 1825 | 0.99991 | 0.0032 | |
| O2-025 | 2612 | 1.00000 | 0.0005 | |
| O2-026 | 1134 | 0.99541 | 0.1054 | |
| O2-027 | 2612 | 1.00000 | 0.0005 | |
| O2-028 | 711 | 0.99948 | 0.0231 | |

Sapma: A4/O2-025/O2-027 kartlarinda en buyuk gunluk fark %0,05 (fiyat duzeltmesi yuvarlamasi); M017 ve O2-028 daha buyuk tek gun farklari verir. O2-026'da 2023-01-03..05 ve 2023-01-27, 2023-03-07 (5 gun) varlik secimi Composer ile ayrisir (SOXL/TECL/SQQQ arasi gecis); sebebi bulunamadi (KMLM/SVIX ilk aylari ya da RSI esitlik/duzeltme farki), diger ~1130 gun birebir.
