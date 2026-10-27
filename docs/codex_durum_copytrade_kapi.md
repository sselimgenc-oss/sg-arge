# CT-Kapı durum

- Durum: tamamlandı.
- Lider kararı (2026-10-27): Binance karşılığı yalnız bilgi sütunudur, eleme yapmaz.
- Kaynak: koşuda `https://fapi.binance.com/fapi/v1/exchangeInfo`; yalnız `status == TRADING`, `contractType == PERPETUAL`, `quoteAsset == USDT` sembolleri alınır. Çıktı `copytrade/kapi/<tarih>/binance_vadeli.txt`; ilk satır kaynak ve UTC zamandır. Sürüm bu tarihtir.
- Eşleme: `X` → `XUSDT`; `kX` → `1000XUSDT`; HIP-3 (`xyz:` vb.) ve spot (`@…`) → `yok`.
- Erişim 451/403 ise sütun `bilinmiyor` olur; rapora yazılır, koşu durmaz ve liste uydurulmaz.

- Durum: devam ediyor.
- Lider kararı (2026-10-27): adım 3 ve 5 için pencere son 200 gün, `candleSnapshot` aralığı `1h`; coin başına tek istek ve koşu içi ortak önbellek kullanılır. Bir saatten kısa işlem plaseboda bir bardır.
- Gecikme: 0 dk liderin dolum fiyatıdır; 5/30/120 dk, gecikme anından sonra açılan ilk saatlik mumun açılışıdır. Rapor gecikmenin saat başına yuvarlanmış muhafazakâr üst sınır olduğunu yazar.
- Veri bütünlüğü: bir trader'ın 200 günlük hacminin %10'undan fazlasında mum yoksa adım 1 `Yetersiz` olur.
- Teknik not: 1 saatlik mumun en çok 5.000 kayıt sınırı 200 günlük pencereyi kapsadığından mum çağrısı sayfalanmaz; her coin yanıtı bellek önbelleğinde paylaşılır.
- Lider denetimi 1 (2026-10-27): adım 5 için 1.000 sabit tohumlu plasebo ve tek yönlü p; adım 6 için 365 günlük BTC eşleşmiş NW alfa; adım 7 BHY, adım 8 günlük PnL kümelemesi uygulanacak. Nakit akışları sonraki portfolio örneğine atanır; `accountClassTransfer` dış akış değildir.
- Son doğrulama: `python -m pytest -q` — 36 geçti (2026-10-27).
