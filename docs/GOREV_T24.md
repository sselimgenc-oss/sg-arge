# T24 — Gün içi adaylar için Aşama 2b + saat/gün ilkelleri (sahibi: codex-worker; önerilen model: **Sol**)

## Neden
T17 (PR #82) birleşti. Lider doğruladı: pytest geçti, günlük null sonuçları birebir aynı, gerçek veri işlem paritesi birebir aynı. Gün içi kripto adayları artık Aşama 2a'ya girebiliyor. Ancak `backtests/asama2b.py` yalnız günlük/haftalık satırları işliyor. 2a'yı geçen gün içi adayların son elemeden geçebilmesi için 2b'nin gün içi desteği gerekiyor.

## İstenenler
1. **`asama2b.py --tf 1H,30m,15m,5m` ve `--veri-kok` desteği.** Veri `tarama.py` / `asama2a.py` ile aynı yükleyiciden okunur. Adaylar, `results/asama2a.csv`'de null'u geçmiş gün içi satırlardır. Kapılar günlükle aynıdır; gevşetme yok:
   - **OOS:** 2024-10-01 sonrası.
   - **Ön dönem:** Kripto için 2017-01-01 → 2019-12-31 (Binance verisi `--baslangic 2017-01-01` ile iner). Sembolün o dönemde verisi yoksa sembol düşer; hiç sembol kalmazsa satır `Dogrulanamaz` olur.
   - **Stres:** Maliyet 2x/3x ve dolumu +1 bar geciktirme.
   - **Plato:** Her sayısal parametre için ±%20.
   - **Bootstrap:** 20 günlük block bootstrap, MDD95 ≤ %15. Ozkaynak eğrisi **günlüğe toplanır**, ardından bootstrap uygulanır; böylece günlük kartlarla aynı ölçekte olur.
   - **DSR:** Deneme sayısı tüm gün içi kart × piyasa × tf satırlarıdır.
2. **Performans:** 5m ≈ 600–700 bin bar × 25 sembol. Plato ve stres koşuları `--isci` ile paralel çalışmalı. Hedef aday başına 30 dakikadan az; ölçülen süreyi PR'a yaz.
3. **Saat/gün ilkelleri:** İfade diline şunları ekle:
   - `saat_utc` (0-23, barın açılış saati);
   - `dakika`;
   - `haftanin_gunu` (0=Pzt).

   Bunlar look-ahead içermez, yine de testlerini yaz. EVRENSEL_KURALLAR'a **D13** olarak ekle.
   - Bununla **A6-019** (Overnight Seasonality in Bitcoin, 1H, kripto) kartını taşı. Kural kaynakta tam.
   - Diğer `seans_saat` kartları EVRENSEL_KURALLAR 81. satır gereği **Doğrulanamaz (piyasa özgü)** kalır. Bu kartlar DAX/ABD vadeli/döviz seansına bağlı ve bu piyasaların dakikalık verisi bizde yok; onlara dokunma.
4. **Testler:**
   - Sentetik gün içi veride uçtan uca 2b testi.
   - Günlük satırlarda mevcut `results/asama2b.csv` ve `results/asama2b_pit.csv` sonuçları birebir korunmalı (regresyon).
   - Saat ilkellerinin birim testleri.
5. `asama2b.yml` iş akışı varsa ona `tf` girdisini ekle.

Gerçek koşuyu lider yapar; gerçek sonuç dosyası üretme. Teslim: Tek PR (base `main`). PR gövdesine değişiklik özeti, test çıktısı ve ölçülen süreyi yaz.
