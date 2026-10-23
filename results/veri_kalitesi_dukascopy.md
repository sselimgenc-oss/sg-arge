# Dukascopy 1 dakika veri kalite raporu (T36a)

Durum: **indirici ve kalite kontrolleri hazır; veri çekimi bu ortamda henüz çalıştırılamadı.**

`datafeed.dukascopy.com` için bulut egress kontrolü `CONNECT tunnel ... 403` döndürdü. Bu nedenle bu çalışma alanına Parquet veri yazılmadı. `.github/workflows/dukascopy.yml`, GitHub Actions üzerinde eksik günleri indirip yıllık dosyaları checkpoint ederek commit etmek üzere eklendi.

## Kapsam

- `USDJPY`: 2010'dan itibaren
- `USDCHF`: 2010'dan itibaren
- `USATECHIDXUSD`: 2012'den itibaren
- Çıktı: `data/dakika/<sembol>/<yil>.parquet`
- Zaman damgası: UTC; OHLC bid/ask orta fiyatı; `spread` ask kapanış eksi bid kapanışıdır.

## Kontroller

İndirici her günlük `BID` ve `ASK` dosyasını LZMA ile açar, bozuk 24-byte kayıt uzunluklarını reddeder, 429/5xx yanıtlarını yeniden dener ve istekler arasına 0,75 saniye bekleme koyar. Yıllık Parquet mevcutsa tamamlanmış günler atlanır; kesilen koşu kaldığı yerden devam eder.

GitHub Actions koşusu tamamlandıktan sonra aşağıdaki ölçümler her sembol/yıl için rapora eklenmelidir:

1. toplam bar, benzersiz UTC zaman damgası ve yinelenen bar sayısı;
2. beklenen dakika aralıkları dışındaki boşluklar (hafta sonu ayrı raporlanır);
3. spread için min/medyan/p95/maks ve negatif spread sayısı;
4. son ortak gün kapanışının yfinance günlük kapanışıyla yüzde farkı (`check_scale`, tolerans %5).

FX sembolleri için yfinance karşılaştırma sembolleri `JPY=X` ve `CHF=X`; endeks vekili için kullanılan sembol ve fark ayrıca açıkça yazılmalıdır. Yfinance veya Dukascopy verisi erişilemezse bu ölçüm başarısız/eksik olarak işaretlenmeli, başarılı kabul edilmemelidir.

## Yerel doğrulama

```bash
.venv/bin/pytest -q tests/test_dukascopy.py
python data/dukascopy.py USDJPY --yillar 2010
```
