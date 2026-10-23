# U1: Kendi stratejilerimiz, ilk iki hat (ön kayıt + altyapı)

**Karar kaynağı:** `tartisma/012_ozet_karar.md` (K1-K7). **Kullanıcı onayı (2026-10-23):** seçenek (a).
**Hedef:** yılda %20-30 net (ayda ~%1,5-2,5), portföy MDD ≤ %15. Bu, tek tek stratejilerin değil, **sepetin** hedefidir.
**Token kuralı:** Lider kod/veri işi yapmaz. Lider görev yazar, ön kaydı belirler, PR'ları denetler, huniyi koşar ve sonuç raporunu yazar.

## 0. Değişmez kurallar (ön kayıt)
1. **Dönemler (tüm U kartları):**
   | Dönem | Aralık |
   |---|---|
   | Geliştirme (IS) | veri başı → 2023-09-30 |
   | Doğrulama (OOS) | 2023-10-01 → 2025-09-30 |
   | **Kilitli** | 2025-10-01 → bugün |

   Kilitli dönem yalnız nihai sınavda, lider kararıyla **bir kez** açılır.
2. **Deneme sayısı:** Aşağıdaki ızgaralar dışında varyant denenmez. Her ızgara noktası DSR deneme sayısına eklenir. Izgara sonradan değişirse yeni deneme sayılır ve `results/U1_deneme_kaydi.csv`'ye yazılır.
3. **Ortak parametre:** Bir hattaki tüm enstrümanlar aynı parametreyi kullanır. Uzunluklar bar sayısıdır, eşikler ATR/volatilite ile ölçeklenir.
4. **Evrensel kurallar aynen geçerli:**
   - sinyal kapanmış barda, dolum sonraki açılışta;
   - aynı barda stop önce;
   - long-only x1;
   - maliyet Faz 1 tablosuna göre, 2x/3x stres.

## 1. Hat 1: Swing, çok varlıklı sepet (günlük)
**Evren:** `data/evren.csv` → BIST30 (USD bazında), ABD25 (PIT üyelik), KRIPTO25, EMTIA (6 ETF). **Sınıf bütçesi:** 4 sınıf × %25.
**Mekanizma:** zaman serisi momentumu (Moskowitz-Ooi-Pedersen 2012) ve kesitsel momentum (Jegadeesh-Titman 1993). Literatürde onlarca piyasada ortak kuralla tekrar etmiş etkiler.

| Kart | Kural | Izgara | Deneme |
|---|---|---|---|
| `U1-H1-TS` | Her enstrüman, `getiri(L) > 0` **ve** `close > sma(200)` ise tutulur. Ağırlık sınıf bütçesi içinde ters volatilite (60 gün). Toplam ağırlık ≤ 1, kaldıraç yok. Yeniden dengeleme periyodik. Sinyali olmayan pay nakitte kalır. | L ∈ {63, 126, 252}; dengeleme ∈ {hafta, ay} | 6 |
| `U1-H1-XS` | Önce TS filtresi (yukarıdaki, L=126). Geçenler arasında `getiri(M)` sıralaması yapılır ve her sınıftan en güçlü k tutulur: hisse (BIST30 + ABD birlikte, sınıf içi z-skorla normalize) k=5, kripto k=3, emtia k=2. Ağırlık ters volatilite, aylık dengeleme. | M ∈ {63, 126}; k ölçeği ∈ {×1, ×2} | 4 |

**Geçme:**
- Faz 1 hunisi: rastgele giriş/rastgele sıralama null testi, 2x/3x maliyet, +1 bar gecikme, bootstrap MDD95.
- **Her sınıfta ayrı ayrı** net getiri > 0 olmalı. Tek bir sınıf toplam kârın en fazla %50'sini getirebilir.

## 2. Hat 2: Kripto day trade (15 dk / 1 saat)
- **Çekirdek (geliştirme):** BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT.
- **Kardeşler (önceden kilitli, yalnız doğrulama):** XRP, ADA, DOGE, TRX, LTC, LINK, DOT, AVAX, BCH, NEAR (USDT).
- **Gün içi kuralı:** her pozisyon en geç **UTC 23:45** kapanır (gece taşınmaz).
- **Stop:** ATR(14) × 2. **Risk:** işlem başına %0,5 (Faz 1).

| Kart | Mekanizma | Kural | Izgara | Deneme |
|---|---|---|---|---|
| `U1-H2-A` | Volatilite sıkışmasından kırılım | 15 dk. BB(20,2) genişliği son 100 barın en düşük %20'sindeyken `close > bb.ust` olursa giriş. Hedef ATR × 2R, aksi halde gün sonu çıkış. | genişlik yüzdeliği ∈ {%10, %20}; R ∈ {1,5, 2,5} | 4 |
| `U1-H2-B` | ABD seans açılışı akışı | 1 saat. UTC 13:00 barı kapanışında, gün açılışından bu yana getiri > 0 **ve** `close > vwap` ise giriş. Çıkış: UTC 20:00 ya da stop. | çıkış saati ∈ {17:00, 20:00} | 2 |
| `U1-H2-C` | Gün içi trend devamı | 1 saat. `close > donchian(N).ust` **ve** `close > ema(50)` ise giriş. İz süren stop ATR × 2, gün sonu çıkış. | N ∈ {12, 24}; ema filtresi ∈ {var, yok} | 4 |

**Geçme (K3, kardeş doğrulama):** ham parametrelerle aşağıdakilerin hepsi:
- kardeşlerin ≥ %60'ında net PF > 1,1;
- havuzlanmış (14 enstrüman) sonuç Faz 1 hunisini geçer;
- tek enstrüman toplam kârın ≤ %35'ini getirir;
- kâr tek bir şok ayına bağlı değildir (en iyi ay çıkarılınca PF > 1).

Short yok. Short desteği PR #136'da (T36b) beklemede; U1 sonucu umut verirse U2'de ele alınır.

## 3. İşler
### U1a: Codex (veri + denetim araçları)
1. **Binance gün içi arşivi:** 14 coin (çekirdek + kardeşler), **15 dk ve 1 saat**, Binance başlangıcından bugüne. `data/fetch.py` Binance yolu kullanılır. Günlük veri gibi yeniden üretilebilir: Parquet `.gitignore`'da kalır, `data/MANIFEST.csv` güncellenir. Kalite raporu: boşluk, tekrar, sıfır hacim.
2. **Kilit:** `engine/kilit.py`. Kart çalıştırılırken veri varsayılan olarak 2025-09-30'da kesilir. Kilit yalnız `KILIT_AC=1` ortam değişkeniyle açılır, açıldığında da uyarı loglanır. Test edilir.
3. **Kardeş/havuz raporu:** `scripts/kardes_rapor.py`. Girdi: sembol başına işlem kayıtları. Çıktı (CSV + kısa MD):
   - sembol başına net PF;
   - PF > 1,1 olan kardeş oranı;
   - havuzlanmış PF ve block-bootstrap %90 aralığı;
   - en büyük kâr payı (sembol);
   - en iyi ay çıkarılmış PF.
4. Testler, PR. Faz 1 sonuçları değişmemeli (CI paritesi).

### U1b: Sonnet (motor + kartlar)
1. **`engine/rotasyon.py`:**
   - `agirlik: esit | ters_vol` (`vol_n`, varsayılan 60);
   - `sinif_butce: {sinif: oran}`;
   - yeni mod `trend_sepet`: filtresi doğru olan her sembol tutulur, ağırlık sınıf bütçesi içinde ters volatilite, toplam ≤ 1.
   - Null testi bu modlar için de çalışmalı (rastgele tutma, aynı doluluk oranıyla).
   - Mevcut rotasyon sonuçları değişmemeli (CI paritesi).
2. **Kartlar:** `docs/spec/U1-H1-TS.yaml`, `U1-H1-XS.yaml`, `U1-H2-A.yaml`, `U1-H2-B.yaml`, `U1-H2-C.yaml`. Kurallar ve ızgaralar **birebir** bölüm 1-2'deki gibi olmalı. Belirsizlik varsa uydurma: karta `belirsiz:` yaz ve lidere sor.
3. Gerekirse eksik ifade ilkeli (ör. gün açılışından getiri, UTC saat kapanışı) eklenir, testi yazılır.

### U1c: Lider
PR denetimi → huni koşusu (IS → OOS) → `results/U1_SONUC.md`. Kilitli dönem en son, yalnız aday kalırsa açılır.

## 4. Sıra
U1a ve U1b paraleldir. Biri bitince lider denetler. İkisi bitince U1c başlar.
