# Veri zaman damgası ve arşiv notları

- Evren 2026-10 itibarıyla lider tarafından seçildi; bugünkü büyük şirketler → survivorship yanlılığı; PDF'teki 28/25/25/6 listesiyle birebir olmayabilir.
- Bütün Parquet dosyaları UTC, timezone-aware `timestamp` indeksine sahiptir.
- Zaman damgası **bar başlangıcını** ifade eder. Binance `/api/v3/klines` için bu doğrudan `open_time` alanıdır. Yfinance saatlik indeksleri de interval başlangıç etiketidir; indirilen ilk arşivde THYAO.IS seans hizası kalite raporuyla ayrıca doğrulanmalıdır.
- Yfinance günlük barları borsanın seans tarihini temsil eder; karşılaştırılabilir saklama için UTC gece yarısına yerleştirilir. Gün içi saat anlamı taşımaz.
- BIST seansı `Europe/Istanbul` saat diliminde 10:00–18:00 kabul edilir. `resample_4h()` iki kapalı kova üretir: 10:00–14:00 ve 14:00–18:00. Eksik dört saatlik kovalar varsayılan olarak atılır.
- Kripto 4H kovaları UTC 00:00, 04:00, 08:00, 12:00, 16:00 ve 20:00 başlangıçlarına hizalanır.
- `--append`, mevcut arşiv ile yeni indirmeyi zaman damgasına göre birleştirir; çakışmada yeni gözlem korunur. Böylece yfinance’ın kayan 730 günlük penceresinden düşen eski saatler kaybolmaz.
- Saatlik Parquet arşivi kaynağın kayan penceresi nedeniyle Git’e alınır. Günlük Parquet yeniden üretilebilir olduğundan `.gitignore` kapsamındadır; yalnız manifesti sürümlenir.
- `data/MANIFEST.csv` her sembol ve interval için dönem, satır sayısı, byte boyutu ve SHA-256 içerir. `results/veri_kalitesi_1h.md` tekrar, eksik saat, sıfır hacim ve BIST seans dışı barları raporlar.
