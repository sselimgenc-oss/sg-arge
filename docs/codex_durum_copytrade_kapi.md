# CT-Kapı durum

- Durum: devam ediyor.
- Lider kararı (2026-10-27): Binance karşılığı yalnız bilgi sütunudur, eleme yapmaz.
- Kaynak: koşuda `https://fapi.binance.com/fapi/v1/exchangeInfo`; yalnız `status == TRADING`, `contractType == PERPETUAL`, `quoteAsset == USDT` sembolleri alınır. Çıktı `copytrade/kapi/<tarih>/binance_vadeli.txt`; ilk satır kaynak ve UTC zamandır. Sürüm bu tarihtir.
- Eşleme: `X` → `XUSDT`; `kX` → `1000XUSDT`; HIP-3 (`xyz:` vb.) ve spot (`@…`) → `yok`.
- Erişim 451/403 ise sütun `bilinmiyor` olur; rapora yazılır, koşu durmaz ve liste uydurulmaz.

- Durum: durdu — karar bekliyor.
- Engel: `candleSnapshot` için mum çözünürlüğü tanımlı değil. 0/5/30/120 dakika gecikmede "sonraki mum açılışı" 1 dakika, 5 dakika veya 30 dakika mum kullanıldığında farklı gerçekleşir; bu sanal kopya netini ve CT-Kapı adım 3 sonucunu değiştirir.
- Gerekli karar: Gecikmeli kopya ve plasebo için kullanılacak `candleSnapshot` aralığını belirtin. Aynı zamanda uzun dönem mum verisinin sayfalanmasında kabul edilecek kaynak sınırı varsa belirtin.
