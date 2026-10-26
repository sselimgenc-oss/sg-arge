# TV-2 kapalı veri sonuçları

Tarih: 2026-10-26. Bu kayıt, `results/tv2/satirlar/` altındaki mevcut
`veri_yok` gerekçelerini kapatır; yeni veri denemesi, karar değişikliği veya
eşik değişikliği yapmaz.

Dukascopy kuyruğundaki 214 kimlik bu kayda dahil değildir: onlar
`results/tv2/kuyruk_dukascopy.txt` ve kayıtlı Actions isteğiyle ayrı
işlenecektir.

| Mevcut neden sınıfı | Kimlik sayısı | Sonuç |
|---|---:|---|
| Yerel piyasa / ikinci kaynak yok | 151 | Mevcut `veri_yok` nedeni korunarak kapatıldı. |
| Binance sembolü yok veya kalkmış | 30 | Mevcut `veri_yok` nedeni korunarak kapatıldı. |
| Eşleme yok veya yanlış | 3 | Mevcut `veri_yok` nedeni korunarak kapatıldı. |
| yfinance gün içi verisi yok | 3 | Mevcut `veri_yok` nedeni korunarak kapatıldı. |
| `zaman_asimi` | 13 | Mevcut "koşu süre sınırında kesildi" nedeni korunarak kapatıldı; yeni uzun koşu istenmedi. |

Toplam 187 `veri_yok` ve 13 `zaman_asimi` satırı bu kapsamda kapalıdır.
