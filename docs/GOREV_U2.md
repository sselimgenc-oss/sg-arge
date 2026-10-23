# U2: Kripto short (hazırlık)

**Kapsam:** yalnız kripto (kullanıcı kararı, 2026-10-23).
**Neden:**
- Long-only bir kripto stratejisi düşüş piyasalarında (2018, 2022) yalnız bekleyebilir.
- Short desteği sepeti çeşitlendirir ve işlem fırsatını iki katına çıkarır.

**Ön kayıt kuralı:** Bu aşamada yalnız **motor ve veri** hazırlanır. Short strateji kartları ve ızgaraları U1 sonuçları görüldükten sonra lider tarafından ön kayıtla yazılır. U1 verisine bakarak kart yazılmaz.

## U2a: Codex (motor + maliyet + veri; U1c'den sonra, kullanıcı kararı 2026-10-23)
1. **Short motoru:** PR #136'daki (T36b) short desteğini main'e taşı. Gerekenler:
   - `yon: long | short | iki`;
   - aynalanmış stop, hedef ve iz süren;
   - aynı barda önce stop;
   - null testi yönü korusun.

   Kapsam kripto olduğu için PR'daki FXDK ve yerel saat/Gotobi kısımlarına gerek yok. Çakışma çıkarırlarsa çıkar.
   - PR #136 yerine yeni bir PR aç.
   - Long-only sonuçlar birebir aynı kalmalı (CI paritesi).
2. **Kripto short maliyeti (USDT-M perpetual varsayımı):**
   - İşlem maliyeti Faz 1 kripto tablosu: %0,15 / %0,30 / %0,45.
   - **Funding:** pozisyon her 8 saatlik funding anında (00:00, 08:00, 16:00 UTC) açıksa, `funding_rate × pozisyon değeri` uygulanır. Short pozitif oranda alır, negatif oranda öder. Long da aynı kurala tabidir; açıksa long'a da uygulanır.
   - Stres: 2x/3x maliyette funding'in yalnız **aleyhte** olan kısmı çarpanla büyütülür.
3. **Funding verisi:**
   - 14 U1 coini için Binance funding rate geçmişi indirilir (`fapi/v1/fundingRate`), `data/funding/<SYM>.parquet`, gitignore + MANIFEST.
   - Erişim engeli varsa (coğrafi blok) uydurma yapma. PR'da yaz, alternatif kaynak öner (ör. `data.binance.vision` aylık arşivleri).
   - Fiyat serisi olarak spot mumlar kullanılır. Perp ile spot arasındaki fark ihmal edilir ve bu varsayım belgeye yazılır.
4. **Koşucular:** `backtests/u1.py` ve `backtests/u1_huni.py` short ve iki yönlü kartları koşabilmeli. İşlem tablosunda `yon` sütunu olur, kardeş raporu da bunu raporlar.
5. **Testler:**
   - yansıtılmış fiyatta short = long;
   - funding hesabı (elle hesaplanmış örnek);
   - kilit.

   CI geçsin, PR aç.
