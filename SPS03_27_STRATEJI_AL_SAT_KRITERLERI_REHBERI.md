# SPS-03: 27 Lider Stratejinin Kesin Al-Sat Kriterleri ve Uygulama Rehberi
**Hazırlayan:** Baş Quant Danışmanı Argon & Algobot Ar-Ge Ekibi  
**Kapsam:** 5 Temel Araştırma Raporundan Derlenen 27 Stratejinin Matematiksel Formülleri, İndikatör Eşikleri, Giriş/Çıkış ve Kâr Kilidi Kuralları  
**Tarih:** 18 Ekim 2026  

---

## 1. Yönetici Özeti ve Argon Danışman Metodolojisi

SPS-03 genişletilmiş test evreninde sınıfı geçen **27 strateji** (17 Kontrollü Pilot [%5 risk bütçesi] ve 10 Öğrenme Pilotu [%1 risk bütçesi]), salt geçmiş getiriye göre değil, **kesin matematiksel kurallara** göre alım-satım yapmaktadır.

Her strateji 4 aşamalı katı bir kural disipliniyle çalıştırılır:
1. **Üst Zaman Dilimi Yön Filtresi (HTF Bias - 1W veya 1D/4H):** Henüz kapanmamış mumlar asla hesaba katılmaz (look-ahead ve repaint sıfırlanır). Sadece üst zaman dilimi trend yönünde işlem açılır (Long-Only).
2. **Alt Zaman Dilimi Giriş Tetiği (Entry Trigger - 1D veya 1H):** Çoklu indikatör teyidi (hacim, momentum, kanal kırılımı veya kurumsal likidite/FVG).
3. **Kâr Kilidi (Profit Ratchet):** Fiyat hedeflenen ATR kârına (+0.95x ila +1.5x ATR) ulaştığı anda stop-loss seviyesi otomatik olarak **Giriş + %0.2 / %0.50 başabaş kâr noktasına kilitlenir**. Böylece kâra geçen işlemlerin zarara dönmesi engellenir (bu mekanizma kazanma oranını ortalama %14 artırmaktadır).
4. **Çıkış ve Dinamik İz Süren Stop (Trailing Exit):** Kalan pozisyon, Chandelier veya ATR iz süren stop (2.3x - 3.2x ATR) ya da karşıt indikatör dönüşüyle trendin sonuna kadar taşınır.

---

## 2. 17 Kontrollü Pilot Stratejisinin Kesin Al-Sat Kuralları (≥75 Puan, %5 Tahsis)

### #1 R05_ZSCORE — 65-Günlük Z-Skor Rejim Sentinel & Momentum Trend
- **Kaynak PDF & Bölüm:** `Reddit_ve_Quant_Stratejileri_Backtest_Raporu.pdf (Sayfa 6-7, R5)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Swing` | **Puan:** `100.0`
- **Matematiksel İndikatörler:**
  - **baseline:** `EMA(Close, 65)`
  - **volatility:** `StDev(Close, 65)`
  - **z_score:** `(Close - Baseline) / Vol_65`
  - **atr:** `ATR(14)`
  - **ibs:** `(Close - Low) / (High - Low)`
- **1. Yön Filtresi (HTF Bias):** Haftalık yön filtresi Boğa (1W_Bias == 1, Close_1W >= EMA20_1W). Henüz kapanmamış hafta kullanılmaz.
- **2. Alış / Long Giriş Kriteri:** 1W_Bias == 1 iken, günlük Z_Score > +0.55 (boğa eşiği) üzerine çıktığında, Close > EMA(20) ve IBS > 0.55 onayıyla gün kapanışında Long pozisyon açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Nötr Tutuş: Z_Score -0.10 ile +0.55 arasında kaldığı sürece trend sürülür. Ayı Çıkışı: Z_Score < -0.10 altına indiğinde nakde geçilir.
- **4. Kâr Kilidi & İz Süren Stop:** Kâr Kilidi: Fiyat +1.8 * ATR(14) kâra ulaştığında stop başabaşa kilitlenir. İz Süren Stop: Zirveden 2.8 * ATR(14) geriden takip eder.
- **Argon QA / Quant Notu:** *"Fiyatı 10 TL'den 300 TL'ye veya 10k$'dan 90k$'a giden varlıklarda sabit osilatörler bozulur; Z-Skoru volatiliteye bölerek tüm piyasa rejimlerini normalize eder. 4.93 PF ve 1.64 Sharpe ile sistemin 1 numarasıdır."*

---
### #2 S1_TWIN_OTT_DUAL — Twin OTT (TOTT) Çift Bantlı Trend ve Momentum Sistemi
- **Kaynak PDF & Bölüm:** `Paper_Test_4_Lider_Day_ve_Swing_Strateji_Raporu.pdf (Sayfa 2-3, S1)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Trend kolları` | **Puan:** `100.0`
- **Matematiksel İndikatörler:**
  - **fast_tott:** `MAVG=EMA(Close,14), Fark=MAVG*0.008 (%0.8), Stop=MAVG-Fark`
  - **slow_tott:** `MAVG=EMA(Close,28), Fark=MAVG*0.016 (%1.6), Stop=MAVG-Fark`
  - **htf_bias:** `1W_EMA(10) >= 1W_EMA(20) veya 1W_Close >= 1W_EMA(20)*0.985`
  - **vol_filter:** `Volume > SMA(Volume, 20) * 1.10`
  - **atr:** `ATR(14)`
- **1. Yön Filtresi (HTF Bias):** Üst Zaman Dilimi (1W): 1W_Bias == 1 (1 bar gecikmeli, repaint engelli).
- **2. Alış / Long Giriş Kriteri:** 1W_Bias == 1 iken, Hem Hızlı OTT (14, %0.8) hem de Yavaş OTT (28, %1.6) aynı anda AL (TOTT_Fast == 1 AND TOTT_Slow == 1) olmalı, Close > EMA(50) ve seanslık hacim Volume > SMA(Volume, 20) * 1.10 olmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Hem Hızlı OTT hem de Yavaş OTT eğrisi birden SAT durumuna geçtiğinde pozisyon derhal nakde kapatılır.
- **4. Kâr Kilidi & İz Süren Stop:** Başabaş Kâr Kilidi (Profit Ratchet): Girişten +1.5 * ATR(14) kâra ulaşıldığında stop derhal Giriş + %0.2 kilitlenir. Dinamik İz Süren Stop: Zirveden 2.5 * ATR(14).
- **Argon QA / Quant Notu:** *"Tek ortalamanın yatayda ürettiği testere kayıplarını çift OTT bandı mükemmel süzer. 20 enstrümanda ortalama 5.37 PF ve %61.1 kazanma oranı üretmiştir."*

---
### #3 VR1_SWING — VOLTRAN-R1: Reddit-Quant Çift Motorlu Swing Hibrit
- **Kaynak PDF & Bölüm:** `Reddit_ve_Quant_Stratejileri_Backtest_Raporu.pdf (Sayfa 8-9, Voltran-R1)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Swing` | **Puan:** `100.0`
- **Matematiksel İndikatörler:**
  - **motor_a:** `IBS < 0.28, Close < HH10 - 2.15*SMA(H-L, 25), Close > SMA100*0.95`
  - **motor_b:** `Z_Score_65 > +0.48, Close >= HH15*0.997, RVOL_20 > 1.20, IBS > 0.65`
  - **atr:** `ATR(14)`
- **1. Yön Filtresi (HTF Bias):** 1W_Bias == 1 (Haftalık trend pozitif).
- **2. Alış / Long Giriş Kriteri:** Motor A (Dip Avcısı): Derin düzeltmede Close < HH10 - 2.15*Range_25 ve IBS < 0.28 panik kapanışında Long. Motor B (Ralli/Kırılım): Z_Score_65 > +0.48 ve 15 barlık tepe hacimli kırıldığında (RVOL > 1.20) Long.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Mod-Duyarlı Çıkış: Motor A ile açılmışsa ertesi gün ilk Close > High[1] tepki anında kâr alınır. Motor B ile açılmışsa Z_Score_65 < -0.15 olduğunda çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** Motor B için 4. günde +1.2 ATR kârda %30 kısmi kâr alınır, stop başabaşa çekilir. Kalan %70 pozisyon zirveden 2.5 * ATR(14) iz süren stopla taşınır.
- **Argon QA / Quant Notu:** *"IBS dip avcılığı (%68.9 WR) ile Qullamaggie trend ralisini tek portföyde birleştirir. Para hiçbir zaman boşta beklemez; 4.29 PF ve 1.54 Sharpe üretir."*

---
### #4 V1B_SWING_SMC_ML — VOLTRAN-1B: Kurumsal Likidite (SMC) & Makine Öğrenmesi Geri Çekilme
- **Kaynak PDF & Bölüm:** `Voltran_4_Super_Strateji_Mimari_ve_Backtest_Raporu.pdf (Sayfa 3, Voltran-1B)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Algo` | **Puan:** `93.75`
- **Matematiksel İndikatörler:**
  - **fvg:** `Low > High[2] * 0.990 (3 Mumluk Boğa Dengesizliği)`
  - **ema_ribbon:** `EMA(21), EMA(34), EMA(100)`
  - **lorentzian_ml:** `4 Boyutlu k-NN Özellik Skoru: [(RSI14-45)/20] + [Close>EMA34? 0.9:-0.9] + [+DI>-DI? 0.6:-0.6] + [EMA13>EMA34? 0.5:-0.5]`
  - **rsi:** `RSI(14)`
- **1. Yön Filtresi (HTF Bias):** 1W trend Boğa (+1) ve Günlükte Close > EMA(34).
- **2. Alış / Long Giriş Kriteri:** Günlükte Bullish FVG oluşmalı VEYA fiyat EMA(21) dinamik destek bandına çekilip üzerinde yeşil mumla tutunmalı (Close > Open). Aynı anda 4D Lorentzian ML Skoru >= 1.10 ve RSI(14) >= 46 olmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Lorentzian ML skoru <= -0.7'ye düştüğünde ve fiyat EMA(34) * 0.985 altına indiğinde ana çıkış gerçekleşir.
- **4. Kâr Kilidi & İz Süren Stop:** Profit Ratchet (Kâr Kilidi): Fiyat girişin +1.05 * ATR(14) üzerine ulaştığında stop Başabaş + %0.50 seviyesine kilitlenir. Kalan pozisyon 3.0 * ATR(14) iz süren stop ile korunur.
- **Argon QA / Quant Notu:** *"Tepe kırılımlarını kovalamak yerine, kurumsal emir blokları (Order Block / FVG) düzeltmelerini yapay zeka olasılık kapısıyla yakalar. NVDA, AAPL, META'da 3.60+ PF üretmiştir."*

---
### #5 V1A_SWING_BREAK — VOLTRAN-1A: Volatilite Sıkışması Patlaması & Donchian Kırılımı
- **Kaynak PDF & Bölüm:** `Voltran_4_Super_Strateji_Mimari_ve_Backtest_Raporu.pdf (Sayfa 3, Voltran-1A)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Strateji` | **Puan:** `93.75`
- **Matematiksel İndikatörler:**
  - **supertrend:** `1W Supertrend(10, 2.5), 1D Supertrend(10, 2.4)`
  - **donchian:** `Highest(High[1], 12)`
  - **dmi_adx:** `DMI(14) +DI > -DI, ADX(14) > 15.0`
  - **volume:** `Volume >= SMA(Volume, 20) * 0.95`
- **1. Yön Filtresi (HTF Bias):** 1W Supertrend(10, 2.5) == 1 VEYA 1W Kapanış >= EMA(21)*0.985 ve EMA(8) > EMA(21).
- **2. Alış / Long Giriş Kriteri:** Günlük Supertrend Boğa (+1), +DI > -DI ve ADX(14) > 15.0 iken; Kapanış son 12 günün en yüksek kanalını (Donchian High[1], 12 * 0.985) kırdığında ve Volume >= SMA20 * 0.95 olduğunda Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Günlük Supertrend negatife (-1) döndüğünde veya Kapanış < EMA(21) olduğunda pozisyon kapatılır.
- **4. Kâr Kilidi & İz Süren Stop:** Profit Ratchet: Kapanış fiyatı girişin +1.05 * ATR(14) üzerine çıktığı an stop Başabaş + %0.50 noktasına kilitlenir (kazanma oranını %54'ten %71'e fırlatır). Kalan kısım 3.0 * ATR(14) Chandelier Stop ile sürülür.
- **Argon QA / Quant Notu:** *"Yatay konsolidasyondan patlayan trend dalgalarını en düşük sahte kırılım oranıyla yakalar. ADX > 22 olduğunda pozisyon boyutu otomatik 1.15x'e çıkar."*

---
### #6 S2_KEVIN_DAVEY — Kevin Davey Donchian + ADX Rejim Filtreli Kanal Kırılımı
- **Kaynak PDF & Bölüm:** `Paper_Test_4_Lider_Day_ve_Swing_Strateji_Raporu.pdf (Sayfa 4-5, S2)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Swing` | **Puan:** `93.75`
- **Matematiksel İndikatörler:**
  - **donchian_high:** `Highest(High[1], 15)`
  - **donchian_low:** `Lowest(Low[1], 20)`
  - **adx_dmi:** `ADX(14) > 20.0, +DI > -DI`
  - **ema_support:** `EMA(20)`
  - **atr:** `ATR(14)`
- **1. Yön Filtresi (HTF Bias):** 1W_Bias == 1 (Haftalık rejim pozitif).
- **2. Alış / Long Giriş Kriteri:** Günlük kapanış son 15 günün en yüksek seviyesini (Close >= Donchian_High * 0.998) yukarı kırmalı, ADX(14) > 20.0, +DI > -DI olmalı ve Close > EMA(20) destek üzerinde kalmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Kalan pozisyon, fiyat 20 günlük Donchian alt kanalının altına indiğinde (Close < Donchian_Low) tamamen kapatılır.
- **4. Kâr Kilidi & İz Süren Stop:** İlk Stop: Girişin 1.6 * ATR(14) altı. 4. Gün Kuralı: İşlemin 4. gününde fiyat +1.2 * ATR kâra ulaşmışsa pozisyonun %35'i kapatılır, kalan %65 başabaş (Giriş + %0.2) stopa çekilir ve zirveden 2.3 * ATR ile sürülür.
- **Argon QA / Quant Notu:** *"Vadeli İşlem Dünya Şampiyonu Kevin Davey'in aşırı optimizasyondan arındırılmış efsane modelidir. 4. gün kısmi kâr realizasyonu kazanma oranını %73.1'e taşır."*

---
### #7 C01_PULLBACK — Codex 01 Trend İçi Düzeltme & Destek Dönüşü (Pullback)
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 8, 01/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Strateji` | **Puan:** `87.5`
- **Matematiksel İndikatörler:**
  - **htf_ema:** `1W EMA(20) > 1W EMA(40), 1W Close > EMA(20)`
  - **daily_ema:** `Daily EMA(20) > Daily EMA(50)`
  - **rsi:** `RSI(14) > 50`
  - **atr:** `ATR(14)`
- **1. Yön Filtresi (HTF Bias):** Yalnız tamamlanmış haftalık mum: 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde günlük EMA20 > EMA50 olmalı. Kapanış önceki gün EMA20'nin altında veya eşitken, bugün EMA20 üzerine geri çıkar ve RSI(14) > 50 olursa alış sinyali üretilir.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Günlük kapanış EMA50 altına inerse, RSI14 40 altına düşerse veya haftalık rejim bozulursa çıkış sinyali oluşur.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 başlangıç/takip stopu; işlem başına özsermayenin %0,5'i risk edilir. Gap stopu ilk açılıştan uygulanır.
- **Argon QA / Quant Notu:** *"Yükselen ana trend içindeki geçici silkelemeleri ve düzeltmeleri yakalar. Düşük kazanma oranına rağmen 2.21 Kâr Faktörü ve asimetrik kazanç/kayıp dengesi sunar."*

---
### #8 VR2_S4_INTRADAY — VOLTRAN-R2: Intraday Hibrit (4H Sweet Spot + RRS + RVOL ORB)
- **Kaynak PDF & Bölüm:** `Paper_Test_4_Lider_Day_ve_Swing_Strateji_Raporu.pdf (Sayfa 6-7, S4)`
- **İşlem Tarzı & MTF:** `1D/4H → 1H (Intraday)` | **Bağlı Havuz:** `Day trade` | **Puan:** `87.5`
- **Matematiksel İndikatörler:**
  - **rrs:** `Real Relative Strength (Endekse göre 12 bar normalize alfa) > 0.25`
  - **rvol:** `RVOL_14 = Volume / SMA(Volume, 14) > 1.45`
  - **pmax:** `PMax(10, 2.7) == 1`
  - **adx:** `ADX(14) > 18.0`
  - **ibs:** `IBS > 0.70`
- **1. Yön Filtresi (HTF Bias):** Günlük trend yukarı (1D_Bias == 1, Close > EMA50) ve 4H EMA8 > EMA20.
- **2. Alış / Long Giriş Kriteri:** Motor A: PMax == 1, ADX > 18 VE enstrüman endekse göre pozitif ayrışmışken (RRS > 0.25) Long. Motor B: Açılışta RVOL > 1.45 hacim patlaması, son 6 barlık tepe kırılımı (Close >= HH6 * 0.998) ve IBS > 0.70 ile anında Long.
- **3. Satış / Kâr Alma / Trend Çıkışı:** 1H PMax == -1 sat sinyaline döndüğünde veya RRS < -0.35 altına inip Close < EMA10 olduğunda çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** Hızlı Kâr Kilidi: Fiyat Giriş + 1.35 * ATR(14) seviyesine ulaştığı anda stop Giriş + %0.2 başabaş seviyesine kilitlenir. Zirveden 2.35 * ATR(14) iz süren stop işletilir.
- **Argon QA / Quant Notu:** *"Saatlik işlemlerde komisyona yenilmeyi önler. Sadece endeksten güçlü (RRS > 0.25) ve kurumsal hacim desteği olan (RVOL > 1.45) lider tahtaları seçer."*

---
### #9 V2A_INTRA_TOTT_ORB — VOLTRAN-2A: Saatlik Adaptif TOTT Kanalı & Seans Kırılımı
- **Kaynak PDF & Bölüm:** `Voltran_4_Super_Strateji_Mimari_ve_Backtest_Raporu.pdf (Sayfa 3-4, Voltran-2A)`
- **İşlem Tarzı & MTF:** `1D/4H → 1H (Intraday)` | **Bağlı Havuz:** `Day trade` | **Puan:** `81.25`
- **Matematiksel İndikatörler:**
  - **tott_hourly:** `TOTT / OTT(VAR 14, %1.35)`
  - **orb_high:** `Highest(High[1], 10)`
  - **confluence_score:** `5 Faktörlü Skor: TOTT Boğa (+35), ORB Kırılım (+25), ADX>15 (+20), Close>EMA34 (+15), Vol>SMA20 (+10)`
  - **adx_dmi:** `ADX(14) > 15, +DI >= -DI * 0.95`
- **1. Yön Filtresi (HTF Bias):** 1 Günlük ve 4 Saatlik üst zaman diliminde Supertrend Boğa (+1) veya Kapanış >= EMA(21)*0.985.
- **2. Alış / Long Giriş Kriteri:** 1 Saatlik (1H) grafikte 5 Faktörlü Confluence Skoru >= 70 olduğunda ve +DI >= -DI * 0.95 iken Long pozisyon açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** TOTT(14, %1.35) yönü negatife (-1) dönüp fiyat EMA(34) altına indiğinde pozisyon kapatılır.
- **4. Kâr Kilidi & İz Süren Stop:** Saatlik Kâr Kilidi (Intraday Ratchet): Kapanış fiyatı girişin +0.95 * ATR(14) üzerine çıktığında stop-loss Başabaş + %0.50 kilitlenir. Kalan pozisyon 3.2 * ATR(14) iz süren stopla taşınır.
- **Argon QA / Quant Notu:** *"Fitil ve iğne tuzaklarını VAR hareketli ortalamasıyla filtreler. 1.83 Sharpe ve %60.2 kazanma oranıyla saatlik grafikte altın standarttır."*

---
### #10 R06_S3_PMAX_4H — 4H Sweet Spot (1D/4H/1H) MTF Hizalama + PMax & ADX Rejim
- **Kaynak PDF & Bölüm:** `Paper_Test_4_Lider_Day_ve_Swing_Strateji_Raporu.pdf (Sayfa 5-6, S3)`
- **İşlem Tarzı & MTF:** `1D/4H → 1H (Intraday)` | **Bağlı Havuz:** `Algo` | **Puan:** `81.25`
- **Matematiksel İndikatörler:**
  - **pmax:** `MAVG = EMA((H+L)/2, 10), 2.7 * ATR(10) İz Süren Bant`
  - **chop_filter:** `ATR_Ratio = ATR(14) / SMA(ATR(14), 40) > 0.85 (Yatay testere filtresi)`
  - **4h_sweet_spot:** `4H EMA(8) > 4H EMA(20) ve 4H ADX(14) > 18.0 (+DI > -DI)`
- **1. Yön Filtresi (HTF Bias):** Günlük (1D) grafikte fiyat EMA(50) üzerinde ve günlük bias pozitif (1D_Bias == 1).
- **2. Alış / Long Giriş Kriteri:** 4H grafikte EMA(8) > EMA(20) ve ADX > 18 onaylı iken; 1H grafikte PMax == 1 (yeşil boğa) durumuna geçtiğinde ve ATR_Ratio > 0.85 iken Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** 1H grafikte PMax == -1 (kırmızı sat) durumuna geçtiğinde pozisyon derhal kapatılır.
- **4. Kâr Kilidi & İz Süren Stop:** Kâr Kilidi: Fiyat Giriş + 1.5 * ATR(14) seviyesine ulaştığında stop başabaş noktasına çekilir. Zirveden 2.3 * ATR(14) iz süren stop işletilir.
- **Argon QA / Quant Notu:** *"Gürültüden arındırılmış 3 zaman dilimli (1D makro -> 4H sweet spot -> 1H tetik) kurumsal disiplindir. Kripto ve BIST30'da 2.83 PF üretir."*

---
### #11 L01_TRENDSHIFT_1D — TrendShift Günlük Dalga Doğrulama & Supertrend-ADX
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 3, Lider 1)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Trend kolları` | **Puan:** `81.25`
- **Matematiksel İndikatörler:**
  - **supertrend:** `Supertrend(10, 2.6)`
  - **adx_dmi:** `ADX(14) > 16.0, +DI > -DI`
  - **htf_st:** `1W Supertrend(10, 2.5) + EMA(8/21)`
  - **atr_stop:** `2.8 * ATR(14)`
- **1. Yön Filtresi (HTF Bias):** 1W grafikte tamamlanmış mumda Supertrend(10, 2.5) yönü Yeşil (+1) VEYA 1W Kapanış >= EMA(21)*0.985 ve EMA(8) > EMA(21).
- **2. Alış / Long Giriş Kriteri:** 1W yön Boğa (+1) iken, 1D grafikte kapanış Supertrend(10, 2.6) üst bandını yukarı kırarak yeşile dönmeli, +DI > -DI ve ADX(14) > 16.0 olmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Alt zaman dilimi Supertrend(10, 2.6) aşağı kırıldığında (-1) VEYA 1W trendi negatife döndüğünde pozisyon kapatılır. 3 bar cooldown uygulanır.
- **4. Kâr Kilidi & İz Süren Stop:** Zirveden 2.8 * ATR(14) iz süren stop işletilir. Trend kırılmadıkça büyük dalgalar sonuna kadar taşınır.
- **Argon QA / Quant Notu:** *"256 stratejilik havuzun 1W->1D MTF genel lideridir. 3.53 PF ve %367 net kâr ortalamasıyla güçlü trend dalgalarını kaçırmaz."*

---
### #12 R01_QULLAMAGGIE — Kristjan Qullamaggie High Tight Flag (HTF) & Episodic Pivot
- **Kaynak PDF & Bölüm:** `Reddit_ve_Quant_Stratejileri_Backtest_Raporu.pdf (Sayfa 3, R1)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Day trade hisse` | **Puan:** `81.25`
- **Matematiksel İndikatörler:**
  - **adr_20:** `SMA((High - Low)/Close, 20) * 100`
  - **base_width:** `(Highest(High[1], 15) - Lowest(Low[1], 15)) / Close`
  - **rvol:** `Volume / SMA(Volume, 20)`
  - **ibs:** `(Close - Low) / (High - Low)`
- **1. Yön Filtresi (HTF Bias):** Pazar endeksi (SPY/XU030/BTC) SMA10 >= SMA20*0.99 VE hisse 1W Kapanış >= EMA20_1W olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Öncül Ralli: Son 40 günde en az +%8-25 ralli yapılmış olmalı. Sıkışma: Base_Width < 9.5 * ADR_20 daralmışken, Close > Highest(High[1], 15), RVOL > 1.25 ve IBS > 0.65 ile Long girilir.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Kalan %60 pozisyon, 5. günden itibaren günlük kapanış SMA(10) veya EMA(20)*0.995 altına inene kadar sürülür.
- **4. Kâr Kilidi & İz Süren Stop:** İlk Stop: max(1.05*ADR_20, 1.35*ATR(14)). 4. Gün Kuralı: +0.6*Stop kârda %40 satılır, kalan stop Giriş + %0.1'e (başabaş) çekilir.
- **Argon QA / Quant Notu:** *"Kristjan Kullamägi'nin onlarca milyon dolarlık hisse momentum modelidir. 4. gün kısmi kâr alma kuralı BIST30'da kazanma oranını %77.9'a çıkarır."*

---
### #13 L01_TRENDSHIFT_1H — TrendShift Saatlik İntraday Momentum & Tepki Girişi
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 3 & 6, Lider 1)`
- **İşlem Tarzı & MTF:** `4H/1D → 1H (Intraday)` | **Bağlı Havuz:** `Day trade` | **Puan:** `75.0`
- **Matematiksel İndikatörler:**
  - **htf_bias:** `4H veya 1D Supertrend(10, 2.5) == 1`
  - **1h_supertrend:** `Supertrend(10, 2.6)`
  - **adx_dmi:** `ADX(14) > 16.0, +DI > -DI`
  - **atr_stop:** `2.6 * ATR(14)`
- **1. Yön Filtresi (HTF Bias):** 4 Saatlik ve 1 Günlük grafiklerde makro trend yeşil (+1) Boğa olmalıdır.
- **2. Alış / Long Giriş Kriteri:** 1 Saatlik (1H) grafikte kapanış Supertrend üst bandını yukarı kırarak yeşile döndüğünde, +DI > -DI ve ADX(14) > 16.0 iken Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** 1H Supertrend negatife (-1) döndüğünde veya zirveden 2.6 * ATR(14) iz süren stop kırıldığında çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** Zirveden 2.6 * ATR(14) iz süren stop. 3 bar yeniden giriş bekleme süresi (cooldown).
- **Argon QA / Quant Notu:** *"Saatlik periyotta 2.79 Kâr Faktörü ve 1.26 Sharpe ile test edilen en yüksek getirili seans içi trend izleyicisidir."*

---
### #14 C04_ICHIMOKU — Codex 04 Ichimoku Kumo Bulut Kırılımı & Kijun Denge
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 11, 04/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `TradingView` | **Puan:** `75.0`
- **Matematiksel İndikatörler:**
  - **tenkan_kijun:** `Tenkan-sen(9), Kijun-sen(26)`
  - **kumo_cloud:** `Senkou Span A(52), Senkou Span B(52)`
  - **htf_ema:** `1W EMA(20) > EMA(40)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde Tenkan > Kijun ve Senkou A > Senkou B olmalı. Günlük kapanış tamamlanmış Ichimoku bulutunun üstüne ilk kez çıktığında Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Tenkan Kijun altına inerse, günlük kapanış bulutun alt sınırının altına düşerse veya haftalık rejim bozulursa çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 başlangıç ve iz süren stop. Maksimum açık stop riski %2.
- **Argon QA / Quant Notu:** *"Fiyatı, denge çizgilerini ve bulut yapısını birlikte doğrular. Düşük işlem sıklığına rağmen 2.58 Kâr Faktörü ve sadece -%4.45 maksimum düşüş üretir."*

---
### #15 C05_DMI_TREND — Codex 05 DMI Trend Gücü & ADX Yönsel İvme
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 12, 05/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `TradingView` | **Puan:** `75.0`
- **Matematiksel İndikatörler:**
  - **dmi:** `+DI(14), -DI(14)`
  - **adx:** `ADX(14) >= 20`
  - **ema_base:** `EMA(100), EMA(50)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde fiyat günlük EMA100 üzerindeyken; +DI, -DI'yi yukarı keser ve ADX14 en az 20 olursa alış sinyali üretilir.
- **3. Satış / Kâr Alma / Trend Çıkışı:** +DI tekrar -DI altına iner, kapanış EMA50 altına düşer veya haftalık rejim bozulursa çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 başlangıç/iz süren takip stopu; işlem başına güncel özsermayenin %0,5'i riske edilir.
- **Argon QA / Quant Notu:** *"Trend yönünü ve gücünü DMI/ADX ile matematiksel olarak doğrular. 10.8 yıllık genişletilmiş testte kanıt tavanını aşıp %5 bütçeye terfi etmiştir."*

---
### #16 C02_CCI_CONT — Codex 02 CCI Sıfır Çizgisi Aşımı & Trend Devam Modeli
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 9, 02/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Strateji` | **Puan:** `75.0`
- **Matematiksel İndikatörler:**
  - **cci:** `CCI(20)`
  - **ema_base:** `EMA(100), EMA(50)`
  - **htf_ema:** `1W EMA(20) > EMA(40)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde fiyat günlük EMA100 üzerinde olmalı. CCI(20) son 10 gün içinde negatif bölgeyi gördükten sonra +100 seviyesini yukarı keserse alış.
- **3. Satış / Kâr Alma / Trend Çıkışı:** CCI(20) sıfır altına iner, günlük kapanış EMA50 altına düşer veya haftalık rejim bozulursa çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 takip stopu; emir sonraki günlük barın açılışında uygulanır.
- **Argon QA / Quant Notu:** *"Dört piyasanın tamamında (BIST, ABD, Kripto, Emtia) sağlamlık kapısını geçen ender strateji ailesidir. Düşük drawdown (-%6.0) ile çok dayanıklıdır."*

---
### #17 C06_KAMA_EFF — Codex 06 Kaufman Adaptif Hareketli Ortalama (KAMA) Verimlilik
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 13, 06/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Algo` | **Puan:** `75.0`
- **Matematiksel İndikatörler:**
  - **kama:** `KAMA(10, 2, 30)`
  - **efficiency_ratio:** `ER(10) >= 0.30`
  - **htf_ema:** `1W EMA(20) > EMA(40)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde günlük kapanış KAMA(10,2,30) çizgisini yukarı geri alır, KAMA son 5 güne göre yükselir ve Verimlilik Oranı ER10 en az 0.30 ise alış oluşur.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Kapanış KAMA altına iner, ER10 0.12 altına düşer veya haftalık rejim bozulursa çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 koruma stopu; sermaye tahsisi %5.
- **Argon QA / Quant Notu:** *"Piyasanın gürültülü ve verimsiz testere dönemlerini Kaufman Verimlilik Katsayısı ile süzerek sadece net trend akışlarında işlem açar."*

---

## 3. 10 Öğrenme Pilotu Stratejisinin Kesin Al-Sat Kuralları (62.50–68.75 Puan, %1 Tahsis)

### #18 L08_LORENTZIAN_1D — Lorentzian Distance Çok Boyutlu Makine Öğrenmesi (k-NN) Sınıflandırıcı
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 5, Özel 8)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Algo` | **Puan:** `68.75`
- **Matematiksel İndikatörler:**
  - **distance_metric:** `Lorentzian Uzayı: Sigma log(1 + |x_i - y_i|)`
  - **features:** `RSI(14), ADX/DMI(14), EMA(50), EMA(150)`
  - **knn_threshold:** `Komşuluk Skoru >= 1.10`
- **1. Yön Filtresi (HTF Bias):** Yalnızca 1W trendi Boğa (+1) olduğunda ve Günlükte fiyat EMA(150) üzerinde olduğunda çalışır.
- **2. Alış / Long Giriş Kriteri:** 1W yön filtresi pozitif iken, 4 boyutlu Lorentzian uzayında hesaplanan k-NN komşuluk skoru >= 1.1 eşik değerine ulaştığında Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Lorentzian sınıflandırma skoru negatife (<= -1.1) döndüğünde veya nötrleştiğinde çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** Zirveden 2.8 * ATR(14) iz süren stop. 1W->1D'de 3.16 PF ve 1.09 Sharpe üretir.
- **Argon QA / Quant Notu:** *"Öklid yerine bükümlü Lorentzian uzayını kullanarak aşırı uyumu (curve-fitting) önler. Gölge modda %1 riskle izlenir."*

---
### #19 V2B_INTRA_SWEEP — VOLTRAN-2B: Saatlik Likidite Süpürmesi & FVG Dengesizlik Dönüşü
- **Kaynak PDF & Bölüm:** `Voltran_4_Super_Strateji_Mimari_ve_Backtest_Raporu.pdf (Sayfa 4, Voltran-2B)`
- **İşlem Tarzı & MTF:** `1D/4H → 1H (Intraday)` | **Bağlı Havuz:** `Day trade` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **ema_ribbon:** `EMA(13) > EMA(34) * 0.998, Close > EMA(34)`
  - **stochastic:** `Stochastic(14,3,3) K >= D * 0.98, K > 35`
  - **rsi:** `RSI(14) > 48`
  - **sweep_level:** `Sweep Low[1, 8] likidite seviyesi`
- **1. Yön Filtresi (HTF Bias):** 1 Günlük / 4 Saatlik üst zaman dilimi trendi Boğa (+1) konumunda olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Saatlik EMA şeridi pozitif dizilimli iken, Stochastic K>35 ve RSI>48 ile geri çekilme bitişi onaylanmalı, mum yeşil kapanmalı veya son 8 saatin dip likiditesini süpürüp üzerinde tutunmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** EMA(13) < EMA(34)*0.995 ve RSI(14) < 45 olduğunda veya 3.2 * ATR(14) iz süren stop tetiklendiğinde çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** Saatlik Kâr Kilidi: Fiyat +0.95 * ATR(14) kâra ulaştığında stop Başabaş + %0.50 seviyesine kilitlenir.
- **Argon QA / Quant Notu:** *"Tepe kırılımı yerine, seans içi panik fitillerini ve likidite temizliğini (sweep) toplar. 2.65 PF ile öğrenme pilotundadır."*

---
### #20 L05_RANGEFLIP_1D — MTF Range Flip & Piyasa Yapısı (BOS) Kırılımı
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 4, Çekirdek 5)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `TradingView` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **market_structure:** `1W / 1D Bullish BOS (Break of Structure)`
  - **range_box:** `Range High = Highest(High[1], 15), Range Low = Lowest(Low[1], 15)`
  - **ema_trend:** `EMA(50)`
- **1. Yön Filtresi (HTF Bias):** Üst zaman diliminde (1W) piyasa yapısı yukarı yönlü kırılmış (Bullish BOS) olmalıdır.
- **2. Alış / Long Giriş Kriteri:** 1W piyasa yapısı Boğa iken, alt zaman diliminde fiyat EMA(50) üzerinde olmalı ve son 15 mumluk yatay konsolidasyon kutusunun üst bandını yukarı kırmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Fiyat 15 barlık kanalın alt bandını (Range Low) aşağı kırdığında ve EMA(50) altına sarktığında çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** 2.8 * ATR(14) iz süren stop seviyesi. %50,4 kazanma oranıyla en yüksek isabetli yapı kırılım modelidir.
- **Argon QA / Quant Notu:** *"Destek-direnç kutularının polarite değişimini (flip) kurumsal seviyelerle doğrular. Tam istikrarlı %1 öğrenme pilotudur."*

---
### #21 C08_DUAL_MOM — Codex 08 Gary Antonacci Çift Momentum (Mutlak + Göreceli)
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 15, 08/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Trend kolları` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **roc_medium:** `ROC(63) (3 Aylık Değişim)`
  - **roc_short:** `ROC(21) (1 Aylık Değişim)`
  - **ema_base:** `Daily EMA(100), Daily EMA(50)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde fiyat günlük EMA100 üzerinde olmalı, ROC(63) > 0 VE ROC(21) > 0 birlikte pozitif olduğunda alış sinyali oluşur.
- **3. Satış / Kâr Alma / Trend Çıkışı:** ROC(21) sıfır altına iner, kapanış EMA50 altına düşer veya haftalık rejim bozulursa çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 başlangıç/takip stopu; %1 risk bütçesi.
- **Argon QA / Quant Notu:** *"Kısa ve orta vadeli ivmenin aynı yönde hizalanmasını arar. OOS döneminde 1.00 Sharpe üreterek sağlamlığını kanıtlamıştır."*

---
### #22 L04_ORBPRO_1D — ORB Pro Seans & Volatilite Kanal Kırılımı
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 4, Çekirdek 4)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Day trade hisse` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **lookback:** `10 Bar (Highest High[1, 10], Lowest Low[1, 10])`
  - **trend_filter:** `EMA(34)`
  - **atr:** `ATR(14)`
- **1. Yön Filtresi (HTF Bias):** 1W yön Boğa (+1) olmalı ve Kapanış > EMA(34) üzerinde bulunmalıdır.
- **2. Alış / Long Giriş Kriteri:** 1W Boğa ve Kapanış > EMA(34) iken, son 10 barın en yüksek seviyesi (Highest High[1, 10]) yukarı kırıldığında bar kapanışında Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Fiyat son 10 barın en düşük seviyesini aşağı kırdığında ve EMA(34) altına indiğinde pozisyondan çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** 2.6 - 2.8 * ATR(14) iz süren stop tetiklendiğinde çıkılır. Ons Altın, Gümüş ve BIST30 rallilerinde etkilidir.
- **Argon QA / Quant Notu:** *"Açılış aralığı kırılımını (ORB) günlük ölçeğe taşır. Sıkışan volatilite patlamalarını yakalar."*

---
### #23 L02_TRENDLOCK_1D — TrendLock Multi-Timeframe Supertrend Donchian Kırılımı
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 3-4, Çekirdek 2)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Trend kolları` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **htf_supertrend:** `1W Supertrend(10, 3.0)`
  - **donchian_20:** `Highest(High[1], 20)`
  - **volume_filter:** `Volume > SMA(Volume, 20) * 1.15`
  - **atr:** `ATR(14)`
- **1. Yön Filtresi (HTF Bias):** 1W üst zaman dilimi Supertrend(10, 3.0) kesinlikle Boğa (+1) olmalıdır.
- **2. Alış / Long Giriş Kriteri:** 1W Supertrend (+1) ve 1D Supertrend (+1) aynı anda hizalıyken; Kapanış 20 günlük Donchian üst kanalını yukarı kırmalı ve Volume > SMA20 * 1.15 olmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Supertrend(10, 3.0) yönü negatife döndüğünde veya 3.0 * ATR(14) TP/iz süren stop seviyesine ulaşıldığında çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** Girişten 2.0 - 2.8 * ATR(14) dinamik Stop-Loss ve 3.0 * ATR(14) kâr hedefi.
- **Argon QA / Quant Notu:** *"Donchian kanal kırılımını Supertrend trend kilidiyle mühürler. TÜPRAŞ'ta 6.25 PF ve ETH'de 6.50 PF üretmiştir."*

---
### #24 L03_SMCPRO_1D — SMC Pro ICT Kurumsal Likidite Blokları & Fair Value Gap (FVG)
- **Kaynak PDF & Bölüm:** `Paper_Test_8_Lider_Strateji_Ozet_ve_Backtest_Raporu.pdf (Sayfa 4, Çekirdek 3)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Algo` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **macro_regime:** `EMA(100) ve EMA(200)`
  - **bullish_fvg:** `Low[0] > High[2] (3 Mumluk Fiyat Dengesizliği)`
  - **order_block:** `Son Düşüş Mumunun Gövde/Fitil Bölgesi`
  - **momentum:** `RSI(14) > 50`
- **1. Yön Filtresi (HTF Bias):** 1W trend Boğa (+1) ve fiyat alt zaman diliminde EMA(100) ve EMA(200) üzerinde işlem görmelidir.
- **2. Alış / Long Giriş Kriteri:** Fiyat EMA(100) üzerinde ve 1W Boğa rejimindeyken; 3 mumluk Boğa FVG ve Boğa Order Block oluşmalı, RSI(14) > 50 ile momentum onaylanmalıdır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Fiyat EMA(100) altına inip RSI(14) < 45 olduğunda (yapı bozulması - CHoCH) pozisyon kapatılır.
- **4. Kâr Kilidi & İz Süren Stop:** Order Block alt sınırı veya 2.8 * ATR(14) iz süren stop kırıldığında çıkılır.
- **Argon QA / Quant Notu:** *"Bireysel indikatörler yerine kurumsal akıllı para (Smart Money Concepts) ayak izlerini sürer. ABD teknoloji hisselerinde 3.04 PF üretir."*

---
### #25 C07_ADX_BREAK — Codex 07 55-Günlük Tepe Kırılımı & ADX Volatilite Patlaması
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 14, 07/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `TradingView` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **donchian_55:** `Highest(High[1], 55)`
  - **donchian_exit_20:** `Lowest(Low[1], 20)`
  - **adx:** `ADX(14) >= 20`
  - **htf_ema:** `1W EMA(20) > EMA(40)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 yükseliş rejimi aktif olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde ADX(14) en az 20 iken; günlük kapanış önceki 55 günün tepesini yukarı kırarsa alış sinyali oluşur.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Kapanış önceki 20 günün dibinin altına inerse, ADX14 15'in altına düşerse veya haftalık rejim bozulursa çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 başlangıç stopu; %1 risk payı.
- **Argon QA / Quant Notu:** *"Klasik Turtle Trader 55 günlük kırılımını ADX trend gücü filtresiyle modernize eder. Sadece ölçülebilir ivme varken kırılımı kabul eder."*

---
### #26 C11_REVERSION — Codex 11 İstatistiki Ortalamaya Dönüş & Bollinger Squeeze
- **Kaynak PDF & Bölüm:** `Codex_Algo_21_Strateji_Detayli_Rapor.pdf (Sayfa 20, 13/21)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Strateji` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **bollinger:** `Bollinger(20, 2) Alt ve Orta Bandı`
  - **rsi_2:** `RSI(2) < 10 (Aşırı Panik)`
  - **htf_ema:** `1W EMA(20) > EMA(40)`
- **1. Yön Filtresi (HTF Bias):** 1W Kapanış > EMA20 ve EMA20 > EMA40 (Yalnızca pozitif ana rejimde çalışır).
- **2. Alış / Long Giriş Kriteri:** Haftalık yükseliş rejiminde günlük kapanış Bollinger(20, 2) alt bandının altına ve RSI(2) 10'un altına indiğinde alış sinyali oluşur.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Kapanış Bollinger orta banda (SMA20) ulaştığında, RSI(2) 70'i geçtiğinde, haftalık rejim bozulduğunda veya en geç 10 günlük tutma süresinde çıkılır.
- **4. Kâr Kilidi & İz Süren Stop:** ATR14 * 3 felaket stopu ve 10 gün zaman stopu. Kazanma oranı %58.45 ile trend sistemlerinden çok daha yüksektir.
- **Argon QA / Quant Notu:** *"Larry Connors tarzı 2 günlük aşırı satım dönüş modelidir. Pozitif trend içindeki geçici likidite paniklerini kâra çevirir."*

---
### #27 R02_IBS_MEANREV — Internal Bar Strength (IBS < 0.30) & 25G Volatilite Bandı Ortalamaya Dönüş
- **Kaynak PDF & Bölüm:** `Reddit_ve_Quant_Stratejileri_Backtest_Raporu.pdf (Sayfa 4, R2)`
- **İşlem Tarzı & MTF:** `1W → 1D (Swing)` | **Bağlı Havuz:** `Day trade hisse` | **Puan:** `62.5`
- **Matematiksel İndikatörler:**
  - **range_25:** `SMA(High - Low, 25)`
  - **lower_band:** `Highest(High[1], 10) - 2.15 * Range_25`
  - **ibs:** `(Close - Low) / (High - Low) < 0.30`
  - **trend_filter:** `Close > SMA(100) * 0.94`
- **1. Yön Filtresi (HTF Bias):** Düşen bıçağı tutmamak için Close > SMA(100)*0.94 ve 1W_Bias == 1 olmalıdır.
- **2. Alış / Long Giriş Kriteri:** Günlük kapanış son 10 günün tepesinden 2.15*Range_25 kadar aşağı çekilen alt bandın altına inip (Close < Lower_Band * 1.012), aynı gün IBS < 0.30 ile günün en alt diliminde kapanırsa Long açılır.
- **3. Satış / Kâr Alma / Trend Çıkışı:** Yesterday's High Kuralı: Fiyat herhangi bir gün bir önceki günün en yüksek seviyesinin üzerinde kapattığı anda (Close > High[1]) pozisyon kârla kapatılır (3-6 gün tutuş).
- **4. Kâr Kilidi & İz Süren Stop:** 2.6 * ATR(14) dinamik felaket stopu ve 18 bar maksimum zaman stopu.
- **Argon QA / Quant Notu:** *"20-25 yıllık akademik testlerde %70-%75 kazanma oranı kanıtlanmış kantitatif klasiktir. THYAO'da %78.9, NVDA'da %83.3 kazanma oranı üretmiştir."*

---

## 4. Panoya Gömülü Çalışma Mekanizması ve Doğrulama
Bu kriterler panoya ve arka plan motoruna şu şekilde gömülmüştür:
1. **İnteraktif Web UI Teftiş Paneli:** `Sg Test Panel` Stratejiler sekmesinde herhangi bir stratejiye tıklandığında açılan modal, yukarıdaki kriterlerin tamamını, indikatör formüllerini ve Argon değerlendirmesini dinamik olarak sunar.
2. **Otonom Bot Motoru (`bot_engine.py`):** GitHub Actions üzerinde her saat başı (:11 geçe) çalışarak 40 varlığın mum verilerini çeker, yukarıdaki kuralları çalıştırır ve üretilen açık/kapalı pozisyonları `data.json` dosyasına yazar.
3. **Piyasa ve Rejim Boyutlandırması:** ADX > 22 iken pozisyon çarpanı 1.15x'e çıkarılır; yatay testere piyasasında ise komisyon aşınmasını önlemek için ATR_Ratio > 0.85 filtresi devreye girer.
