# U4 gerçek koşu — durduruldu

Tarih: 2026-10-24 (UTC)

## Çalıştırılan komutlar

1. `python data/fetch.py --interval 1h --semboller BTCUSDT,...,NEARUSDT`
   - Başarılı: 14/14 Binance 1H arşivi; süre **5m 02.501s**.
2. `python data/fetch.py --interval 1d --evren pit --semboller <U4 kripto + ABD PIT + EMTIA evreni>`
   - Başarılı; süre **1m 20.440s**.
3. `python backtests/u4.py --sadece-say`
   - Başarılı: **16 varyant**.
4. `python backtests/u4.py --donem IS,OOS --results-dir results/u4`
   - Durduruldu; süre **1.294s**.

`u4_huni.py` başlatılmadı. Başarısız koşudan sonra huni çalıştırmak geçerli sonuç üretmez.

## Hata

- Beklenen: kripto 4H kolu, 14 adet Binance 1H arşivini UTC 4H barlarına dönüştürerek IS dönemini koşturur.
- Gözlenen: ilk varyant `U4-H1:KRIPTO25:4H` için `backtests/u4.py:95` içinden `tarama.prepare()` çağrısı `ValueError: KRIPTO25: donemde veri yok` verdi.
- Neden: `backtests/u4.py:80` 1H arşivini zaten 4H'a dönüştürüyor. Ardından `backtests/tarama.py:180`, kartın `tf=4H` olmasına göre aynı çerçeveyi yeniden 4H'a dönüştürüyor. İkinci dönüşüm 4H kaynak barlarını eksik 1H kovası kabul edip atıyor.
- Kanıt: kaynak 1H çerçeveleri `tarama.prepare(..., tf='4H')`'a doğrudan verildiğinde 14 çerçeve ve ilk çerçevede 17.747 bar oluşuyor; bu, IS verisinin mevcut olduğunu gösteriyor.

Ön kayıt gereği kart, dönem, eşik, maliyet, varyant ve kilit değiştirilmedi; hata sessizce düzeltilmedi. Bu nedenle 16 satırlık `huni_ozet.md` üretilmedi.
