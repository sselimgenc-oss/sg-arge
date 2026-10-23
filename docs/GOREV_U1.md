# U1: Kendi stratejilerimiz, kripto gün içi (ön kayıt + altyapı)

**Karar kaynağı:** `tartisma/012_ozet_karar.md`. Hedef seçeneği (a) kullanıcı tarafından onaylandı (2026-10-23).
**Hedef:** yılda %20-30 net, portföy MDD ≤ %15.
**Revizyon (kullanıcı, 2026-10-23):**
- Kullanıcının uzun vadeli yatırımı TEFAS fonlarında, bu yüzden **swing istenmiyor.** İlgi alanı **1 saatte kurulum, 15 dk / 5 dk'da işlem.**
- Algo-trade en kolay **kriptoda** yapıldığı için ana piyasa kripto.
- Faz 1 kazananlarının kriptoya taşınıp taşınmadığı test edilecek.
- Bu yüzden eski Hat 1 (swing sepeti) **iptal.** Önceki sürüm git geçmişinde.

**Token kuralı:** Lider kod/veri işi yapmaz. Lider görev yazar, ön kaydı belirler, PR'ları denetler, huniyi koşar ve sonuç raporunu yazar.

## 0. Değişmez kurallar (ön kayıt)
1. **Dönemler:**
   | Dönem | Aralık |
   |---|---|
   | Geliştirme (IS) | 2018-01-01 → 2023-09-30 |
   | Doğrulama (OOS) | 2023-10-01 → 2025-09-30 |
   | **Kilitli** | 2025-10-01 → bugün |

   Kilitli dönem yalnız nihai sınavda, lider kararıyla **bir kez** açılır.
2. **Deneme sayısı:** Aşağıdaki ızgaralar dışında varyant denenmez. Toplam **14 deneme**, hepsi DSR'ye eklenir. Sonradan yapılan her değişiklik `results/U1_deneme_kaydi.csv`'ye yeni deneme olarak yazılır.
3. **Ortak parametre:** Bir hattaki tüm coinler aynı parametreyi kullanır. Uzunluklar bar sayısıdır, eşikler ATR ile ölçeklenir.
4. **Evrensel kurallar:**
   - Sinyal kapanmış barda, dolum sonraki açılışta.
   - Aynı barda stop önce.
   - Long-only x1.
   - Risk işlem başına %0,5.
   - Maliyet Faz 1 kripto tablosu: %0,15 / %0,30 / %0,45 (1x/2x/3x).
   - **Gün içi:** her pozisyon en geç UTC 23:45'te kapanır.
5. **Üst zaman dilimi (1 saat):** Değeri yalnız **kapanmış** 1 saatlik bardan okunur (`mtf`, ileriye bakma yok).

## 1. Evren
- **Çekirdek (kullanıcının işlem evreni, geliştirme):** BTC, ETH, SOL, BNB, XRP, TRX (USDT).
- **Kardeşler (önceden kilitli, yalnız doğrulama):** ADA, DOGE, LTC, LINK, DOT, AVAX, BCH, NEAR (USDT).
- SOL, AVAX ve NEAR 2020'de listelendi. Dönemleri kısa olur, bu durum raporda belirtilir.

**Uyarı:** Çekirdek bugünün büyük coinlerinden seçildi, bu yüzden geriye dönük seçim yanlılığı var. Kardeş doğrulaması kısmen bu yüzden zorunlu.

## 2. Hat 0: Faz 1 kazananları kriptoda
Faz 1'de emtia 1 saatte Koşullu çıkan iki strateji, **kart ve parametreler değiştirilmeden** çekirdek ve kardeşlerde 1 saatte koşulur. Başka varyant yok.

| Kart | Faz 1 | Deneme |
|---|---|---|
| `T8-07` | StackLight MTF momentum (1H, üst 4H), emtia 1H Koşullu | 1 |
| `V2B` | VOLTRAN-2B saatlik momentum (1H, üst 4H), emtia 1H Koşullu | 1 |

**Not:**
- C07, R01 ve A6-010 günlük (swing) stratejiler olduğu için bu kapsamın dışında.
- Bu iki stratejinin Faz 1 DSR geçmişi (T8-07 kaynakta 256 havuz) aynen taşınır.

## 3. Hat 2: Yeni stratejiler (1 saat kurulum, 15 dk / 5 dk giriş)
Her kartta `giris_tf ∈ {15m, 5m}` ızgaranın bir parçasıdır. Stop, giriş TF'sinde ATR(14) × 2.

| Kart | Mekanizma | 1 saat kurulum (kapanmış bar) | Giriş (15m/5m) ve çıkış | Izgara | Deneme |
|---|---|---|---|---|---|
| `U1-H2-A` | Sıkışmadan kırılım | BB(20,2) genişliği son 100 barın en düşük %20'sinde **ve** `close > ema(50)` | Giriş: `close > 1s bb.ust`. Çıkış: hedef R × risk, gün sonu ya da stop | giris_tf × R ∈ {1,5, 2,5} | 4 |
| `U1-H2-B` | ABD seans açılışı akışı | UTC 13:00 1s barı kapandığında gün açılışından getiri > 0 **ve** `close > vwap` | Giriş: UTC 13:30-15:00 arasında `close > highest(high, 6)` (giriş TF). Günde en fazla 1 işlem. Çıkış: belirlenen saat ya da stop | giris_tf × çıkış ∈ {17:00, 20:00} | 4 |
| `U1-H2-C` | Trend içinde geri çekilme | `close > donchian(N).ust` son 3 barda gerçekleşmiş **ve** `close > ema(50)` | Giriş: fiyat giriş TF `ema(20)`'ye değip üstünde kapanır. Çıkış: iz süren stop ATR × 2 ya da gün sonu | giris_tf × N ∈ {12, 24} | 4 |

## 4. Geçme ölçütleri
**Kardeş doğrulama (ham parametrelerle, hepsi birlikte):**
1. Kardeşlerin ≥ %60'ında net PF > 1,1.
2. Havuzlanmış (14 coin) sonuç Faz 1 hunisini geçer: rastgele giriş null testi, 2x/3x maliyet, +1 bar gecikme, bootstrap MDD95.
3. Tek coin toplam kârın ≤ %35'ini getirir.
4. En iyi ay çıkarılınca PF > 1.

**Maliyet uyarısı:** Kriptoda %0,15 gidiş-dönüş maliyet, 5 dakikalık barların tipik hareketine göre büyüktür. 5m varyantları büyük olasılıkla maliyette elenir. Bu bilinçli bir test, sonuç ne çıkarsa raporlanır.

Short yok. PR #136 (T36b) short desteği içeriyor. U1 umut verirse U2'de ele alınır, kriptoda düşüş piyasası için önemli.

**Sonraki adım (U2, U1'den sonra):** ABD hisse ve emtia gün içi.
- Bu piyasalar için saatlik veri yalnız ~2 yıl, dakikalık veri yok.
- Dukascopy'den NQ, altın ve petrol CFD 1 dk verisi indirilip aynı kartlar orada koşulur.
- Kazanan kurallar kriptodan oraya da taşınabilir.

## 5. İşler
### U1a: Sonnet (Codex'ten devralındı, 2026-10-23; veri + denetim araçları)
1. **Binance gün içi arşivi:** 14 coin, **5 dk, 15 dk ve 1 saat**, 2017'den (ya da listelenmeden) bugüne. `data/fetch.py`'nin Binance yolu kullanılır. Parquet `.gitignore`'da kalır, `data/MANIFEST.csv` güncellenir. Kalite raporu: boşluk, tekrar, sıfır hacim.
2. **Kilit:** `engine/kilit.py`. Veri varsayılan olarak 2025-09-30'da kesilir. Kilit yalnız `KILIT_AC=1` ile açılır ve açılınca uyarı loglanır. Testi yazılır.
3. **Kardeş/havuz raporu:** `scripts/kardes_rapor.py`. Çıktı:
   - sembol başına net PF;
   - PF > 1,1 olan kardeş oranı;
   - havuzlanmış PF ve block-bootstrap %90 aralığı;
   - en büyük kâr payı;
   - en iyi ay çıkarılmış PF.
4. Testler ve CI paritesi (Faz 1 sonuçları değişmemeli). PR.

### U1b: Sonnet (kartlar + gerekli ilkeller)
**İptal:** Eski U1b'deki `rotasyon.py` işi (`ters_vol`, `sinif_butce`, `trend_sepet`) artık gerekmiyor. Başladıysan PR'a koyma, dalda bırak.

1. **Kartlar:** `docs/spec/U1-H2-A.yaml`, `U1-H2-B.yaml`, `U1-H2-C.yaml`. Kurallar ve ızgaralar 3. bölümle **birebir** aynı olmalı. Belirsizlik varsa `belirsiz:` alanına yaz, uydurma.
2. **Motorda gerekenler** (yoksa eklenir, testiyle birlikte):
   - giriş TF'si 5m/15m iken `mtf("1h", ...)` ile kapanmış 1 saatlik bar okuma;
   - gün açılışından getiri;
   - saat penceresi (`saat_utc` var);
   - günde en fazla 1 işlem;
   - gün sonu kapatma (UTC 23:45);
   - saat bazlı çıkış.
3. **Hat 0:** `T8-07` ve `V2B` kartlarını kripto 1 saatte koşacak çalıştırma ayarı. Kart **değişmez**, yalnız evren veya piyasa ayarı yapılır. Kripto 4H üst zaman dilimi 1 saatten yeniden örneklenir.
4. CI paritesi. PR.

### U1c: Lider
PR denetimi → huni koşusu (IS → OOS) → `results/U1_SONUC.md`. Raporda 250 bin TL ile uygulanabilirlik de yer alır: pozisyon büyüklüğü ve komisyon etkisi. Kilitli dönem en son, yalnız aday kalırsa açılır.

## 6. Sıra
U1a ve U1b paralel yürür. İkisi bitince U1c başlar.
