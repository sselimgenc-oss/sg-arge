# T26 — BIST 1H veri temizliği (sahibi: codex-worker; önerilen model: **Terra**)

## Neden
BIST saatlik verisinde (yfinance) hisse başına yaklaşık 727 seans dışı ve 385 sıfır hacimli bar var (`results/veri_kalitesi_1h.md`). Bu yüzden `tarama.py` BIST 1H satırlarını `Dogrulanamaz (veri_kalitesi)` yazıyor (`backtests/tarama.py` ~312. satır). Toplam 45 adet 1H kart BIST'te test edilemiyor.

## İstenenler
1. **Teşhis.** Önce `results/veri_kalitesi_1h_teshis.md` yaz (kısa). Seans dışı barlar ne?
   - Yahoo'nun 09:30 açılış etiketi mi, kapanış seansı (18:00-18:10) mı, saat dilimi kayması mı?
   - Sıfır hacimli barlar seans içinde mi?

   Birkaç hisse için örnek tarih ve saat ver.
2. **Normalizasyon.** `data/fetch.py`'de (ya da ayrı bir `data/bist_1h.py`'de) BIST 1H için deterministik bir temizlik yaz:
   - Barlar Europe/Istanbul seansına (10:00-18:00 sürekli işlem; açılış/kapanış seansları teşhise göre) hizalanır.
   - Seans dışı barlar ya en yakın seans barına birleştirilir (OHLC birleştirme kuralı: ilk open, max high, min low, son close, toplam hacim) ya da atılır. Hangisi doğruysa teşhise göre seç ve gerekçesini yaz.
   - Sıfır hacimli seans içi barlar: fiyat değişmiyorsa (O=H=L=C) olduğu gibi kalır. Değişiyorsa işaretlenir.
   - Uydurma veri yok: eksik bar doldurulmaz.
3. **Kapı.** Temizlenmiş veride kalite raporu eşiği tanımla; örneğin seans dışı = 0 ve şüpheli sıfır hacim < %1. Eşik geçilirse `tarama.py` BIST 1H satırlarını artık Dogrulanamaz yazmaz. Kapı koda bağlı olmalı: rapor eşiği geçmezse eski davranış sürer.
4. **Testler:**
   - sentetik BIST saatlik veride normalizasyon (seans dışı birleştirme/atma, OHLC kuralı, saat dilimi);
   - kapının iki yönü;
   - ABD/kripto 1H verisi değişmemeli (regresyon).
5. Kalite raporunu yeniden üret (`results/veri_kalitesi_1h.md`). Gerçek BIST 1H taramasını lider koşar.

Kapsam dışı: asama2a/asama2b koduna dokunma (T24 incelemede).

Teslim: Tek PR (base `main`). PR gövdesine değişiklik özeti, teşhis bulgusu ve test çıktısını yaz.
