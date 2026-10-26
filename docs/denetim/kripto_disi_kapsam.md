# Kripto dışı TV-2 kuyruk kapsamı

Ölçüm: 2026-10-26 01:44 TR. Kaynak kuyruk `results/tv2/kuyruk_kripto_disi.txt`.

| Durum | Sayı | Açıklama |
| --- | ---: | --- |
| Kuyruk toplamı | 636 | Kripto dışı strateji |
| Satırı dalda olan | 80 | Parça 7 checkpoint’i ve önceki tekil yeniden koşular |
| Satırı olmayan | 556 | 0–6 artifact’ları indirme engeli nedeniyle henüz kurtarılamadı |
| geçti | 1 | Satırı olanlar içinde |
| kaldı | 1 | Satırı olanlar içinde |
| izle | 28 | Çoğu sürüm sonrası bir yıldan az veri |
| uygulanamaz | 2 | Nedensellik farkı |
| veri ücretli | 2 | CME footprint |
| veri yok | 46 | Çoğu Dukascopy önbelleği henüz indirilmemiş sembol |

Satırı olan 80 stratejide en sık karar gerekçeleri:

- 26: sürüm sonrası bir yıldan az veri.
- 16: gün içi/yerel piyasa, Dukascopy bekliyor.
- 13: Dukascopy XAUUSD önbelleği yok.
- 9: Dukascopy EURUSD önbelleği yok.
- 2: CME footprint ücretli.

556 satırın strateji düzeyinde bir sonucu yoktur: çalıştırılmadıkları değil, Actions artifact’larının 0–6 parçaları branşa checkpoint edilemediği ve ortamdan indirilemediği için henüz görünmezler. Yeniden çalıştırma kuyruğu `results/tv2/kuyruk_kripto_disi_kalan.txt` dosyasıdır.
