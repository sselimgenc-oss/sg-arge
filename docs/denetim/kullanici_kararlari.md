# Kullanıcı kararı gerekenler

Bu kayıt karar vermek için hazırlanmıştır; listedeki hiçbir madde varsayılan
olarak uygulanmaz.

| Öncelik | Karar | Neden gerekli | Seçenekler | Mevcut durum |
|---:|---|---|---|---|
| 1 | CME:MNQ1! 1 dakikalık footprint verisi | `6ve1ax1D` için uzun 1 dakikalık CME işlem akışı ücretli; ücretsiz kaynakla doğrulanamıyor. | Ücretli veri lisansı al / `veri ücretli` etiketiyle ayrı bırak. | bekliyor |
| 2 | DOGEUSDT.P footprint arşivi | İki DOGEUSDT.P stratejisi için Binance aggTrades arşivinden yaklaşık 170 günlük işlem verisi indirilmesi gerekiyor. | Ücretsiz arşivi indirip yeniden koş / mevcut `desteklenmiyor` sonucunu koru. | bekliyor |
| 3 | Vekil veriyle canlı uygunluk | Kraken, Bitfinex ve Bitstamp yayın sembollerinin bazı testleri Binance verisiyle yapıldı. Bu sonuçlar canlı uygulanabilirlik kanıtı değildir. | Her borsa için birincil veri sağla / bunları yalnız araştırma-sanal izleme adayı tut. | bekliyor |
| 4 | Türkiye’de copy-trade işlem akışı | Hukuki izin, ücret ve hesap erişimi iddiaları yeterince doğrulanmadı. | Lisanslı kurum/hukukçu yazılı teyidi al / yalnız sanal izleme yap ve otomasyonu kapalı tut. | bekliyor |

## Karar etkisi

- Bu kararlar gelene kadar kapılar, eşikler ve sıralamalar değişmez.
- Gerçek para, API anahtarı, emir gönderimi veya otomatik kopyalama başlatılmaz.
- Karar verildiğinde tarih, seçilen seçenek ve dayanak bu dosyaya eklenir;
  geçmiş satırlar silinmez.
