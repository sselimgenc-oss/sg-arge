# BIST 1H veri teşhisi

## Bulgular

- Yahoo BIST saatlik serisi `Europe/Istanbul` saatinde düzenli olarak `09:30, 10:30, …` etiketlidir. Örneğin `2023-11-22 06:30 UTC`, İstanbul'da `09:30` olur; bu nedenle sorun saat diliminin üç saat kayması değildir.
- `09:30` boş bir seans dışı kayıt değildir. AKBNK.IS için 2023-11-22 barı `O=30,90 H=31,14 L=30,66 C=30,80`, hacim `14.366.567`; THYAO.IS için aynı gün hacim `9.383.775`'tir. Fiyat keşfini/açılışı taşıyan Yahoo aralık etiketi olduğundan atılması fiyat bilgisini siler.
- `17:30` etiketi arşivde ağırlıkla 2024-04-01'den sonra görülür ve sürekli seansın son kısmını/kapanış sınırını taşır. Bu etiket `18:00` seans sınırına hizalanır. Ayrıca 18:00–18:10 kapanış seansı kaydı gelirse aynı `18:00` barına ilk open, en yüksek high, en düşük low, son close ve toplam hacimle birleştirilir.
- Sıfır hacim anomalisi çoğunlukla açılış etiketindedir ve gerçek bir hareketsiz bar değildir. Örneğin 2024-04-01:
  - AKBNK.IS `09:30`: `47,22 / 48,76 / 47,22 / 47,84`, hacim `0`.
  - THYAO.IS `09:30`: `297,75 / 302,00 / 294,00 / 300,75`, hacim `0`.
  Bu gözlemlere hacim uydurulmadı; fiyatı değişen sıfır hacimli bar olarak işaretlendi.

## Normalizasyon kararı

Yahoo'nun `:30` etiketleri bir sonraki tam saat seans sınırına taşınır (`09:30 → 10:00`, …, `17:30 → 18:00`). Gerçek seans dışı kayıtlar atılır. Aynı hedef etikete düşen kapanış seansı kayıtları OHLCV kuralıyla birleştirilir. Eksik bar doldurulmaz ve sıfır hacim değiştirilmez; `O=H=L=C` olan sıfır hacimli bar korunur, fiyatı değişen sıfır hacimli bar şüpheli sayılır.

## Kalite kapısı ve sonuç

Kapı sembol bazında `seans dışı = 0` ve `fiyatı değişen sıfır hacimli bar / tüm barlar < %1` koşullarını birlikte arar. Mevcut 29 BIST arşivinde normalizasyon sonrası seans dışı bar `0`'dır; ancak 179.962 barın 11.169'u fiyatı değişen sıfır hacimlidir. Sembol oranları `%5,15–%6,64` aralığındadır ve 29 sembolün hiçbiri kapıyı geçmez.

Sonuç olarak zaman etiketi sorunu deterministik biçimde giderildi, fakat kaynak hacim kusuru veri uydurmadan düzeltilemedi. Kalite kapısı mevcut arşivde kapalı kalır; `tarama.py` BIST 1H satırlarını `Doğrulanamaz (veri_kalitesi)` olarak tutar. Yahoo daha sonra temiz hacim sağlarsa aynı kod ve eşik herhangi bir elle müdahale olmadan kapıyı açar.
