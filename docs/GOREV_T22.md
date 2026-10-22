# T22 — Portföy rotasyonu modülü (sahibi: claude-moderator / Sonnet)

## Neden
`ozel_kod_nedeni: portfoy_rotasyonu` olan 18 kart var; 11'i `tam` ve günlük/haftalık. Veri yfinance'ten alınabildiği için hepsi test edilebilir. Mevcut motor her sembolü bağımsız işliyor. Bu kartlar ise ya sembolleri birbirine göre sıralayıp en iyi N'yi seçiyor ya da adı verilen birkaç enstrüman arasında geçiş yapıyor (SPY/TQQQ/UVXY/KMLM gibi).

## Kartlar
- **`tam` (11):** A4-002, A4-004, A6-004, A6-021, B3-014, M020a, M050, O2-025, O2-026, O2-027, O2-028
- **`eksik` (6):** A4-001, A4-003, A4-005, A4-007, A5-015, M017. Yalnız kaynakta sinyal tanımı tamsa ele al; T16 kuralları geçerli, tahmin yok.
- **A4-006** 5m ABD gün içi veri istiyor. Bu iş paketine girmez; `belirsiz`e not düş.

## İstenenler
1. **Motor modülü:** Ayrı bir modül yaz (`engine/rotasyon.py`). `engine/portfolio.py`'nin olay döngüsünü değiştirme. İki kip olmalı:
   - `kesitsel`: Her yeniden dengeleme gününde (günlük/haftalık/aylık) bir skor ifadesiyle sembolleri sırala. İlk N'yi eşit ağırlıkla tut; isteğe bağlı mutlak filtre olsun (örneğin `close > sma200`).
   - `gecis`: Kural sırasıyla değerlendirilen "eğer A ise X'i tut, değilse Y" ağacı. Varlıklar adıyla verilir (TQQQ, UVXY, BIL vb.).
2. **Kart şeması:** `rotasyon:` bloğu. İçinde kip, evren (sembol listesi ya da mevcut piyasa evreni), skor/kural ifadeleri (mevcut ifade dili), dengeleme sıklığı ve N.
   - EVRENSEL_KURALLAR'a **D12** olarak ekle.
   - Yürütme kuralları aynı: sinyal kapanmış barla, dolum bir sonraki açılışta, maliyet D bölümündeki gibi, kaldıraç yok.
   - Kaldıraçlı ETF'ler (TQQQ, UPRO gibi) **enstrüman olarak** kabul edilir; motor ek kaldıraç uygulamaz.
3. **Risk:** Rotasyon kitaplarında işlem başına ATR stop yok (kaynakta yoksa). Risk ölçümü portföy MDD'siyle yapılır; aşama 2b'deki bootstrap MDD95 ≤ %15 kapısı aynen geçerli. Kaynakta stop varsa uygulanır.
4. **Veri:** Gereken ETF'leri `data/fetch.py` ile indirilebilir yap. Örnek bir sembol listesi dosyası: `data/rotasyon_semboller.csv`. Sembol yahoo'da yoksa ya da başlangıç tarihi IS'ten sonraysa kart için `Dogrulanamaz (veri_yok)` yaz. Örnek: SVIX 2022'de başladı.
5. **Tarama entegrasyonu:** `tarama.py` rotasyon kartlarını yeni modülle koşturmalı; çıktı aynı `tarama.csv` sütunlarında.
6. **Testler:**
   - Sentetik veride kesitsel sıralama ve geçiş ağacı için birim testleri.
   - Look-ahead testi: seriyi t'de kesince t'ye kadarki pozisyonlar değişmemeli.
   - Mevcut kartların sonuçları değişmemeli.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. Gerçek taramayı lider yapar.

## T21 kararı
O1-039 ve P3-008 kabul edildi. Formüller standart (Ehlers Laguerre RSI, LazyBear Squeeze) ve Argon kaynaktan okumuştu. `belirsiz`deki "T19'da doğrulanacak" notu kalsın.
