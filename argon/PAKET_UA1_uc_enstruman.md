# ARGON PAKETİ U-A1: Üç enstrüman araştırması (XU030 endeks kontratı, SPX, XAUUSD)

Merhaba Argon. Biz bir algo-trading Ar-Ge ekibiyiz: Opus (lider), Sonnet ve Codex (kod), sen (araştırma ve denetim) ve kullanıcı.
Faz 1'de internetten ~420 strateji topladık ve kendi motorumuzda test ettik. Şimdiki ana işimiz kripto. Bu paket ayrı bir **araştırma ve denetim** işi: test yok, kod yok.
Repo erişimin yok, gerek de yok. Paket kendi içinde tam.

**Rolün (kullanıcı kararı, 2026-10-23):** araştırmacı + denetçi. Bulduğun her bilgiyi kaynağıyla yazarsın; ekibin yaklaşımındaki zayıflıkları açıkça söylersin.

## Kesin kurallar
1. **Uydurma yok.** Her sayının ya da tarihin yanında kaynak URL'si olsun. Bulamadıysan "bulunamadı" yaz; tahmin edersen "tahmin" diye işaretle.
2. **Geçmiş sonuçlara bakarak seçim yapma.** Kart listesinde Faz 1 sonucu bilerek yok. Ayrımı yalnız stratejinin **mekanizmasına** göre yap.
3. Kod ya da backtest çalıştırma. İstersen tabloyu saymak için kod kullanabilirsin.
4. Kısa yaz. Teslimin en fazla ~3 sayfa olsun; C bölümündeki CSV bu sınıra dahil değil.

## Üç enstrüman (yalnız bunlar; hisse sepeti ya da ETF yok)
| Kod | Enstrüman | Not |
|---|---|---|
| **XU030** | Borsa İstanbul BIST 30 endeksi; işlem VİOP XU030 endeks vadeli kontratı | TL bazlı. Faz 1'de BIST kararları USD bazında verildi (`USD = TL / USDTRY`). |
| **SPX** | S&P 500 endeksi; işlem endeks kontratı (ES/MES vadeli ya da US500 CFD) | Hangisinin daha uygun olduğunu sen değerlendir. |
| **XAUUSD** | Spot altın / USD | Faz 1'de altın yalnız GLD ETF'i ile (ABD seans saatleri) test edildi. |

## Bizim test kurallarımız (bilmen gerekenler)
- Sinyal kapanmış barda üretilir, dolum sonraki barın açılışında olur. Aynı barda stop önce sayılır. Long-only, kaldıraçsız. İşlem başına risk %0,5.
- Zaman dilimleri: günlük (1D) ve saatlik (1H). Dakikalık testler yalnız uzun ve temiz dakika verisi varsa yapılır.
- Dönemler (günlük): geliştirme 2020-01 → 2024-09, OOS 2024-10 → bugün, ön dönem 2015-2019.
- Baz maliyet (tek yön, komisyon + kayma): BIST %0,15, ABD hisse %0,05, emtia ETF %0,05. Stres testi 2x ve 3x maliyetle yapılır.
- Eleme ölçütleri: maliyet sonrası kâr; en az 30 işlem (paper için day trade ≥ 100, swing ≥ 60); rastgele giriş testi; OOS; +1 bar gecikme; bootstrap MDD95 ≤ %15; DSR (çoklu deneme düzeltmesi).

## Görevler

### A. Veri kaynakları (ücretsiz, mümkün olan en uzun geçmiş)
Her enstrüman için bulabildiğin kaynakları tabloya yaz:

| enstrüman | seri (spot endeks / sürekli vadeli / CFD) | kaynak + URL | aralık (1d/1h/15m/5m) | ilk tarih | ücretsiz mi, nasıl alınır (API/CSV/kütüphane) | bilinen sorun |
|---|---|---|---|---|---|---|

- Aday kaynaklar (doğrula, kör kabul etme): yfinance (`XU030.IS`, `^GSPC`, `ES=F`, `GC=F`, `XAUUSD=X`), Dukascopy (XAUUSD, USA500IDXUSD), Stooq, Borsa İstanbul / VİOP veri sayfaları, Investing.
- **XU030 için özellikle:** VİOP sürekli (vade birleştirmeli) seri ücretsiz bulunabiliyor mu? Bulunamıyorsa spot XU030 endeksi vekil olarak kullanılabilir mi? Vadeli ile spot farkı (baz, vade dönüşü) ne kadar önemli?
- Saatlik veri için kayan pencere sınırlarını yaz (ör. yfinance 1h ≈ 730 gün).

### B. Kontrat ve maliyet bilgisi
Her enstrüman için (kaynaklı):
- kontrat çarpanı ya da lot büyüklüğü, en küçük fiyat adımı (tick) ve değeri;
- işlem saatleri (UTC) ve seans aralarının saatleri, hafta sonu boşluğu;
- vade dönüşü (hangi aylar, hangi gün);
- tipik bireysel yatırımcı komisyonu ve spread; XAUUSD ve CFD için gecelik swap;
- yaklaşık teminat.

Sonunda bizim tablomuz gibi bir **önerilen baz maliyet** satırı yaz (tek yön, fiyatın %'si) ve nasıl hesapladığını göster.

### C. Kart uygunluk ayrımı (128 kart, aşağıdaki CSV)
Her kart için her enstrümana bir etiket ver:
- **U** = tek enstrümanda olduğu gibi çalışır.
- **K** = koşullu, bir şey gerekir. Örnekler: hacim kullanıyor ama spot XAUUSD'de gerçek hacim yok; endeks serisi istiyor; seans açılış ya da kapanış saatine bağlı; boşluk (gap) kullanıyor ama 23 saat açık piyasada gap neredeyse yok.
- **D** = uygulanamaz. Örnekler: kesitsel ya da rotasyon stratejisi (birden çok enstrüman arasında seçim yapar), hisseye özgü (bilanço, temettü), ETF'e özgü (kaldıraçlı ETF geçişi).

Sütunlar:
- `tip`: kartın genel yapısı.
- `giris` / `cikis`: kural ifadesi (kısaltılmış).
- `kod (Codex Algo / ozel)`: kural Python kodunda. Mekanizmayı addan çıkar; emin değilsen K yaz ve nedenini belirt.
- `endeks_*` ifadeleri: piyasa endeksi serisi kullanıyor demektir. Enstrümanın kendisi endeks olduğunda (XU030, SPX) bu genelde sorun değildir; nedenine yaz.

Çıktı CSV biçimi (her kart bir satır, 128 satır):
```
id,XU030,SPX,XAUUSD,neden
```

### D. Denetim (en fazla 10 madde)
Bu üç enstrümanda ileride test yapılırsa bizim yöntemimizin nerede yanılabileceğini yaz. Örnek başlıklar (hepsini yazmak zorunda değilsin):
- Tek enstrümanda işlem sayısı azlığı. 128 kart × 3 enstrüman deneme sayısı DSR'yi nasıl etkiler?
- VİOP vade dönüşü ve sürekli seri kurma hataları.
- XU030'da TL/USD seçimi: enflasyon ve kur etkisi.
- XAUUSD'de hafta sonu boşluğu, swap, hacim yokluğu.
- SPX'te nakit endeks ile vadeli arasındaki seans farkı (vadeli 23 saat açık).
- Yaz saati (DST) geçişleri.
- Faz 1'de altının yalnız GLD ile test edilmesinin XAUUSD'ye taşınma riski.

## Teslim
Tek bir Markdown metni:
~~~
# U-A1 Cevap: Argon
## A. Veri kaynakları
(tablo)
## B. Kontrat ve maliyet
(tablo + önerilen baz maliyet)
## C. Kart uygunluk
(özet sayılar: her enstrüman için U/K/D adedi)
```csv
id,XU030,SPX,XAUUSD,neden
...
```
## D. Denetim
(en fazla 10 madde)
~~~
Kullanıcı bunu bize yapıştıracak. Lider (Opus) denetler.

---

## Kart listesi (128 kart, Faz 1'de test edilebilenler)
```csv
id,ad,tarz,tf,tip,giris,cikis
A1-025,TASC 2026.03 One Percent A Week,swing,1D,tek enstruman,haftanin_gunu() == 0,high >= giris_fiyati * 1.01
A2-002,Stochastic Daily Breakout for Gold,day,1H,tek enstruman,stoch_custom.d < stoch_custom.d[1] and stoch_custom.d[1] > stoch_custom.d[2] and open[3] < bb9.upper[3],
A2-007,Pro MA Crossover EA for MT5,swing,1D,tek enstruman,"cross_over(ma100, ma200) and close > ma100","cross_under(close, ma100)"
A2-021,Magic 100,day,1H,tek enstruman,close > ema100 and close < open,close < 0
A2-030,Channel MA Short-Term System,day,15m,tek enstruman,"cross_over(ema33_close, ema55_high)","cross_under(ema33_close, ema55_low)"
A3-002b,geraked 3MAF,day,30m,tek enstruman,ema20 > ema50 and ema50 > ema100 and low > ema100 and low < ema20 and fraktal2.down,
A3-002h,geraked NWERSIASF,day,15m,tek enstruman,low[1] < nw.lower[1] and close > open and close < nw.lower + 0.5 * (nw.upper - nw.lower) and rsi5[1] < 30,
A3-002i,geraked LRCUTB,day,15m,tek enstruman,"cross_under(close, utstop) and close < lr_signal",lr_close[1] < lr_open[1] and lr_close > lr_open
A3-003,"Sector-Momentum-Pullback (NSE, RSI pullback + ATR iz sü",swing,1D,tek enstruman +endeks,"sektor_aylik_rsi > 55 and rsi14_ay > 60 and rsi14_hafta > 58 and cross_over(rsi14, 50)",
A3-007,"Backtesting.py örnek SmaCross(10,20)",swing,1D,tek enstruman,"cross_over(sma10, sma20)","cross_under(sma10, sma20)"
A3-008a,"stratestic MA Crossover(20,150)",swing,1D,tek enstruman,"cross_over(sma20, sma150)","cross_under(sma20, sma150)"
A3-008b,"stratestic MACD(26,12,9)",swing,1D,tek enstruman,macd.macd > macd.signal,macd.macd <= macd.signal
A3-009a,Systematic-Trading-Backtester: MA 20/50,swing,1D,tek enstruman,sma20 > sma50,sma20 <= sma50
A3-009b,Systematic-Trading-Backtester: Bollinger ortalamaya dön,swing,1D,tek enstruman,close < bb.lower,close >= bb.basis
A3-009c,Systematic-Trading-Backtester: 252 günlük momentum,swing,1D,tek enstruman,close / close[252] - 1 > 0,close / close[252] - 1 <= 0
A3-010a,Freqtrade Strategy001,day,5m,tek enstruman,"cross_over(ema20, ema50) and ha.close > ema20 and ha.open < ha.close","cross_over(ema50, ema100) and ha.close < ema20 and ha.open > ha.close"
A3-010b,Freqtrade Strategy002,day,5m,tek enstruman,rsi14 < 30 and slow.k < 20 and bb.lower > close and hammer == 100,sar > close and fisher > 0.3 and close > giris_fiyati
A3-010c,Freqtrade Strategy003,day,5m,tek enstruman,rsi14 < 28 and rsi14 > 0 and close < sma40 and fisher < -0.94 and mfi < 16 and (ema50 > ema100 or cross_over(e,sar > close and fisher > 0.3
A3-010d,Freqtrade Strategy004,day,5m,tek enstruman,(adx14 > 50 or adx35 > 26) and cci14 < -100 and fast.k[1] < 20 and fast.d[1] < 20 and slowfast.k[1] < 30 and s,adx35 < 25 and (fast.k > 70 or fast.d > 70) and fast.k[1] < fast.d[1] 
A3-011e,pandianmn fork: Strategy005 (resmi depo kodu),day,5m,tek enstruman,volume > vol_sma70 * 4 and close < sma40 and fast.d > fast.k and rsi14 > 30 and fast.d > 30 and fisher_norma <,"cross_over(rsi14, 70) and macd.macd < 0 and dmi14.minus > 50"
A4-002,Simple TQQQ RSI mean reversion,swing,1D,kesitsel/rotasyon,,
A4-003,Overbought or Oversold SPY else UVXY,swing,1D,kesitsel/rotasyon,,
A4-004,RSI 82,swing,1D,kesitsel/rotasyon,,
A4-005,SPY RSI 30 Test,swing,1D,kesitsel/rotasyon,,
A5-009,XLP mean reversion (IBS + 25 günlük bant) (10 Best Swin,swing,1D,tek enstruman,close < hh25 - 2 * range25 and (close - low) / (high - low) > 0.4,close > high[1]
A5-020,Finding Consistent Trends with Strong Momentum - RSI fo,swing,1D,tek enstruman,min_rsi100 >= 40 and max_rsi100 > 70,min_rsi100 < 40 and max_rsi100 <= 70
A6-001,Double 7's Strategy,swing,1D,tek enstruman,close > sma200 and close <= llv7,close >= hhv7
A6-003,Simple Ideas for a Mean Reversion Strategy with Good Re,swing,1D,tek enstruman,close > sma100 and close < sma5 and low < low[1] and low[1] < low[2] and low[2] < low[3],close > close[1]
A6-004,Mean Reversion Entry Timing,swing,1D,kesitsel/rotasyon +endeks,,
A6-010,The Gap Momentum System,swing,1D,tek enstruman,signals > signals[1],signals < signals[1]
A6-019,Overnight Seasonality in Bitcoin,day,1H,tek enstruman,saat_utc() == 21,
A6-022,How to Design a Simple Multi-Timeframe Trend Strategy o,swing,1H,tek enstruman,"mtf('1D', macd_1d.macd) > mtf('1D', macd_1d.signal) and cross_over(macd_1h.macd, macd_1h.signal)",close < open
B1-002,"AlphaTrend Strategy (TradingView, Kıvanç Özbilgiç)",swing,1D,tek enstruman,"cross_over(alphatrend, alphatrend[2])","cross_under(alphatrend, alphatrend[2])"
B3-001,RSI Mean Reversion Trading Strategy in Nasdaq100 (QQQ),swing,1D,tek enstruman,rsi2 < 10,close > high[1]
B3-005,Triple RSI Strategy (90.36% win rate),swing,1D,tek enstruman,rsi5 < 30 and rsi5 < rsi5[1] and rsi5[1] < rsi5[2] and rsi5[2] < rsi5[3] and rsi5[3] < 60 and close > sma200,"cross_over(rsi5, 50)"
B3-010,RSI-2 Larry Connors (ProRealCode),swing,1D,tek enstruman +endeks,close > sma200 and close < sma5 and rsi2 < 10,close > sma5
B3-014,Cross-Sectional Equity Mean Reversion (Quantpedia #13),swing,1D,kesitsel/rotasyon,,
C01,"Haftalik yonlu gunluk geri cekilme (wd_pullback_risk, C",swing,1D,tek enstruman,"rejim and ema20 > ema50 and cross_over(close, ema20) and rsi14 > 50",close < ema50 or rsi14 < 40 or not rejim
C02,Haftalik yonlu gunluk CCI devam (wd_cci_continuation_ri,swing,1D,tek enstruman,"rejim and close > ema100 and cci_min10 < 0 and cross_over(cci20, 100)",cci20 < 0 or close < ema50 or not rejim
C03,Codex Algo 21: wd_flow_confirmation_risk,swing,1D,kod (Codex Algo / ozel),,
C04,Codex Algo 21: wd_ichimoku_balance_risk,swing,1D,kod (Codex Algo / ozel),,
C05,Codex Algo 21: wd_dmi_trend_risk,swing,1D,kod (Codex Algo / ozel),,
C06,Codex Algo 21: wd_kama_efficiency_risk,swing,1D,kod (Codex Algo / ozel),,
C07,Codex Algo 21: wd_adx_breakout_risk,swing,1D,kod (Codex Algo / ozel),,
C08,Codex Algo 21: wd_dual_momentum_risk,swing,1D,kod (Codex Algo / ozel),,
C09,Codex Algo 21: wd_cci_continuation_risk,swing,1D,kod (Codex Algo / ozel),,
C10,Codex Algo 21: wd_breakout_risk,swing,1D,kod (Codex Algo / ozel),,
C11,Codex Algo 21: wd_momentum_risk,swing,1D,kod (Codex Algo / ozel),,
C12,Codex Algo 21: wd_ichimoku_balance_risk,swing,1D,kod (Codex Algo / ozel),,
C13,Codex Algo 21: wd_reversion_risk,swing,1D,kod (Codex Algo / ozel),,
C14,Codex Algo 21: wd_breakout_risk,swing,1D,kod (Codex Algo / ozel),,
C15,Codex Algo 21: wd_cci_continuation_risk,swing,1D,kod (Codex Algo / ozel),,
C16,Codex Algo 21: wd_dual_momentum_risk,swing,1D,kod (Codex Algo / ozel),,
C17,Codex Algo 21: wd_cci_continuation_risk,swing,1D,kod (Codex Algo / ozel),,
C18,Codex Algo 21: wd_breakout_risk,swing,1D,kod (Codex Algo / ozel),,
C19,Codex Algo 21: wd_pullback_risk,swing,1D,kod (Codex Algo / ozel),,
C20,Codex Algo 21: wd_momentum_risk,swing,1D,kod (Codex Algo / ozel),,
C21,Codex Algo 21: wd_adx_breakout_risk,swing,1D,kod (Codex Algo / ozel),,
G003,"Reinforced Smooth Scalp (Freqtrade, hyperopt parametrel",day,15m,tek enstruman,"cross_over(stochf.k, stochf.d) and stochf.d < 19 and adx14 > 35 and sma50_75m < close and volume > 0",open > ema_high5 and stochf.k > 57 and cci20 > 114 and adx14 < 100 and
G007,Crude Oil Tuesday/Thursday Pullback,swing,1D,tek enstruman,(haftanin_gunu() == 1 or haftanin_gunu() == 3) and close < close[1] - ort_aralik25,bars_since_entry >= 1
G008,Holy Thursday Sprint,swing,1D,tek enstruman,paskalya(-4),paskalya(-3)
G009,Pre-Easter Week,swing,1D,tek enstruman,paskalya(-9),paskalya(-3)
G010,OPEX Week Long,swing,1D,tek enstruman,haftanin_gunu() == 4 and ay_gunu() >= 8 and ay_gunu() <= 14,haftanin_gunu() == 4 and ay_gunu() >= 15 and ay_gunu() <= 21
G011,PowerX - RSI + Stochastic + MACD (Freqtrade powerxhopt),swing,1D,tek enstruman,rsi7 > 65 and slow.d > 69 and macd.hist > 0,slow.d < 69
M006,RSI Double-Bottom for Amibroker (AFL),swing,1D,tek enstruman,close > 2 and vol_sma50 > 10000 and rsi_low8 < 30 and rsi_low21 < rsi_low8 and rsi8 < 50,rsi_high8 > 70 and rsi_high21 > rsi_high8 and rsi8 > 60
M008,RSI2 Strategy: Pullback on Ex-Russell 3000 Stocks,swing,1D,tek enstruman +endeks,close > 1 and close > sma100 and rsi2 < 10,rsi2 > 50
M010,RSI Volatility Spread,swing,1D,tek enstruman +endeks,avg_spread_diff < 0 and rsi_atr_mkt > rsi_atr_sec,avg_spread_diff > 0
M012c,5 Swing Trading Strategies for Beginners - Strategy 3: ,swing,1D,tek enstruman,close < low5,close > high[1]
M012d,5 Swing Trading Strategies for Beginners - Strategy 4: ,swing,1D,tek enstruman,adx5 > 40 and (high - low) <= range_min6,close > high[1]
M013,Simple H4 Mobile Trading System,swing,4H,tek enstruman,close > ema30 and close > open and high > high[1] and low < low[1],
M014,Larry Connors' 2-Day RSI Holy Grail (Multi-Stock Adapta,swing,1D,tek enstruman,rsi2 < 5 and close > sma200,close > high[1] or close < sma200
M015,Larry Connors' Cumulative RSI Strategy,swing,1D,tek enstruman,(rsi2 + rsi2[1]) < 10 and close > sma200,(rsi2 + rsi2[1]) > 65 or close < sma200
M016,One Percent a Week Strategy (TQQQ),swing,1D,tek enstruman,haftanin_gunu() == 0,high >= (giris_fiyati * 1.01)
M017,RSI 2 Portfolio (Composer Symphony),swing,1D,kesitsel/rotasyon,,
M020a,The 30-Minute Stock Trader - Strategy 1: Weekly Rotatio,swing,1D,kesitsel/rotasyon +endeks,,
M036,A Mean Reversion Strategy with 2.11 Sharpe (QQQ with Dy,swing,1D,tek enstruman,close < high10 - 2.5 * range_sma25 and (close - low) / (high - low) < 0.3 and close > sma300,close > high[1] or close < sma300
M037,What Is the Best RSI Oversold Level? We Tested 1 Throug,swing,1D,tek enstruman,close > sma200 and rsi2 < 9,close > high[1]
M038,Best Time Frame for Candlestick Patterns (3 Candlestick,swing,1D,tek enstruman,(close[1] > open[1] and close < open and open >= close[1] and close <= open[1]) or (close[2] > open[2] and clo,close > high[1]
O1-001,AlphaTrend Strategy (Matriks),belirsiz,1D,tek enstruman,"cross_over(alphatrend, alphatrend[2])","cross_under(alphatrend, alphatrend[2])"
O1-003,PHL1 YİĞİT KAYNAK,day,1H,tek enstruman,close > di,close < de
O1-004,PHL2 YIGITBOX,day,1H,tek enstruman,close > pvt2 and close > pvt1 and willr3 > -20,close < pvt2 and close < pvt1 and willr3 < -70
O1-011,SuperTrendVadeliStratejisi,day,5m,tek enstruman,"cross_over(close, st10.line)","cross_under(close, st10.line)"
O1-017,"Sistem 2: RSI ortalama kesisimi (VIOP30 5 dk, long)",day,5m,tek enstruman,"cross_over(ma_rsi15, ma_rsi98)","cross_under(ma_rsi15, ma_rsi98)"
O1-027,PMax Explorer STRATEGY & SCREENER,swing,1H,tek enstruman,"cross_over(ema10, pmax10.pmax)","cross_under(ema10, pmax10.pmax)"
O1-038,KPL Swing Strategy,swing,1D,tek enstruman,"cross_over(close, res20[1])","cross_under(close, sup20[1])"
O1-039,Laguerre RSI by KivancOzbilgic STRATEGY,swing,1D,tek enstruman,"cross_over(lrsi, 0.2)","cross_under(lrsi, 0.8)"
O1-066,Accumulation/Distribution Range Breakout Strategy NT8 -,swing,1W,tek enstruman,close > box_top and box_bot > box_bot[12] and vol_sma4[4] > 1.0 * vol_sma4[8],close < box_bot
O1-075,MeanReversal Strategy NT8,swing,1D,tek enstruman,"cross_under(zs10, -1.0) and sma10 > sma100","cross_over(zs10, -0.5) or cross_under(sma10, sma100)"
O1-079,Golden Triangle Strategy,swing,1D,tek enstruman,close > sma50 and sma50 > sma50[1] and low <= sma50 and close > open and sma5 > sma5[1] and volume > vol_sma50,close < sma50
O2-005,Trading Made Simple,swing,1H,tek enstruman,"cross_over(tdi_green, tdi_red) and tdi_green > 50 and close > ema5 and ha.close > ha.open","cross_under(tdi_green, tdi_red) or tdi_green < tdi_green[1]"
O2-025,The Holy Grail,swing,1D,kesitsel/rotasyon,,
O2-027,TQQQ For The Long Term (Reddit Post Link),swing,1D,kesitsel/rotasyon,,
O3-001,Monday reversal in the S&P 500 (10 Best Swing #1),swing,1D,tek enstruman,haftanin_gunu() == 0 and close < close[1] and close[1] < close[2],close > high[1]
O3-002,Overnight swing strategy in the S&P 500 (10 Best Swing ,swing,1D,tek enstruman,close < hh10 - 2.5 * range25 and (close - low) / (high - low) < 0.3,close > high[1]
O3-003,Buy when S&P 500 makes new intraday high (10 Best Swing,swing,1D,tek enstruman,high > hh10 and (close - low) / (high - low) < 0.15,close > high[1]
O3-004,Monday/Tuesday trade in Nasdaq (10 Best Swing #4),swing,1D,tek enstruman,(haftanin_gunu() == 0 or haftanin_gunu() == 1) and (close - low) / (high - low) <= 0.1,close > high[1]
O3-007,Turn of the month strategy S&P 500 (10 Best Swing #9),swing,1D,tek enstruman +endeks,ay_islem_gunu_sondan(5),ay_islem_gunu_bastan(3)
O3-011,5-Day Low of the Range (IBS<0.25) - S&P 500,swing,1D,tek enstruman,close < ll5 and (close - low) / (high - low) < 0.25,close > high[1]
O3-013,Turnaround Tuesday (SPY),swing,1D,tek enstruman,haftanin_gunu() == 0 and close <= close[1] * 0.99,bars_since_entry >= 1
O3-014,3 Days Down Overnight (S&P 500),swing,1D,tek enstruman +endeks,close < close[1] and close[1] < close[2] and close[2] < close[3],bars_since_entry >= 1
O3-015,IBS (Internal Bar Strength) SPY – IBS<0.2 al / >0.8 sat,swing,1D,tek enstruman +endeks,(close - low) / (high - low) < 0.2,(close - low) / (high - low) > 0.8
P01,Twin OTT (TOTT) çift bantlı trend sistemi,swing,1D,tek enstruman,(ema10w >= ema20w or close_1w >= ema20w * 0.985) and ott_fast.dir == 1 and ott_slow.dir == 1 and close > ema50,ott_fast.dir == -1 and ott_slow.dir == -1
P02,Kevin Davey Donchian + ADX rejim filtreli kırılım,swing,1D,tek enstruman,(ema10w >= ema20w or close_1w >= ema20w * 0.985) and close >= hh15 * 0.998 and adx14 > 20 and dmi14.plus > dmi,close < ll20
P03,4H Sweet Spot (1D/4H/1H) PMax + ADX rejim (aynı stratej,day,1H,tek enstruman,close_1d > ema50d and ema8_4h > ema20_4h and adx4h > 18 and dmi4h.plus > dmi4h.minus and pmax.dir == 1 and atr,pmax.dir == -1
P04,VOLTRAN-R2 intraday hibrit (RRS göreceli güç + RVOL ORB,day,1H,tek enstruman +endeks,close_1d > ema50d and ((ema8 > ema20 and pmax.dir == 1 and adx14 > 18 and rrs > 0.25) or (pmax.dir == 1 and rv,pmax.dir == -1
P3-001,SuperTrend STRATEGY,swing,1D,tek enstruman,"cross_over(close, st10.line)","cross_under(close, st10.line)"
P3-002,BUY and SELL - Backtest single EMA cross By che_trader,swing,1D,tek enstruman,"cross_over(close, ema20)","cross_under(close, ema20)"
P3-003,UT Bot Strategy,swing,1D,tek enstruman,"cross_over(close, utbot) and ema1 > utbot","cross_under(close, utbot) and ema1 < utbot"
P3-004,EMA Slope + EMA Cross Strategy (by ChartArt),swing,1D,tek enstruman,"cross_over(ema5, ema20) and ema5 > ema5[1] and ema20 > ema20[1]","cross_under(ema5, ema20)"
P3-005,UT Bot Strategy with Backtesting Range [QuantNomad],swing,1D,tek enstruman,"cross_over(close, utbot) and ema1 > utbot","cross_under(close, utbot) and ema1 < utbot"
P3-007,Heikin Ashi Supertrend,swing,1D,tek enstruman,"cross_over(ha.close, st_ha.line)","cross_under(ha.close, st_ha.line)"
P3-008,Strategy based on Squeeze Momentum Indicator [LazyBear],swing,1D,tek enstruman,bb20.lower < ma20 - 1.5 * rangema and bb20.upper > ma20 + 1.5 * rangema and val > 0 and val > val[1],val < val[1]
P3-011,MACD Strategy with trailing ATR stop,swing,1D,tek enstruman,"close > ema200 and cross_over(macd_ind.macd, macd_ind.signal)",
P3-014,EmperorBTC's VWAP Strategy,day,30m,tek enstruman,"cross_over(close, vwap_val) and close > ema20","cross_under(close, vwap_val)"
R01,Qullamaggie breakout continuation + episodic pivot,swing,1D,tek enstruman +endeks,endeks_sma10 >= endeks_sma20 * 0.99 and (ema10w >= ema20w or close_1w >= ema20w * 0.985) and (close / close[40,close < sma10 or close < ema20 * 0.995
R02,IBS < 0.30 + 25 günlük volatilite bandı ortalamaya dönü,swing,1D,tek enstruman +endeks,close > sma100 * 0.94 and (ema10w >= ema20w or close_1w >= ema20w * 0.985) and close < (hh10 - 2.15 * range25),close > high[1]
R03,RealDayTrading göreceli güç (RRS) 1H momentum,day,1H,tek enstruman +endeks,(st_htf.dir == 1 or close_1d >= ema21h * 0.985) and rrs > 1.10 and ema8 > ema20 and close > ema8 and (close - ,rrs < -0.35 and close < ema10
R04,Stocks in Play (Zarattini) RVOL açılış kırılımı,day,1H,tek enstruman,rvol14 > 1.45 and atr14 / close > 0.007 and (st_htf.dir == 1 or close_1d >= ema21h * 0.985) and close_1d > ema,bars_since_entry >= 6 and close < ema10
R05,Dual Signal Trend Sentinel: 65 günlük Z-skor rejimi,swing,1D,tek enstruman,(ema10w >= ema20w or close_1w >= ema20w * 0.985) and (close - ema65) / sd65 > 0.55 and close > ema20 and (clos,(close - ema65) / sd65 < -0.10
T8-01,TrendShift Supertrend + ADX rejim adaptif,swing,1D,tek enstruman,"(st_w.dir == 1 or (close_1w >= ema21w * 0.985 and ema8w > ema21w)) and cross_over(st.dir, 0) and dmi14.plus > ",st.dir == -1 or (st_w.dir == -1 and close < giris_fiyati)
T8-02,TrendLock MTF Supertrend + Donchian kırılımı,swing,1D,tek enstruman,st_w.dir == 1 and st.dir == 1 and close > hh20 * 0.992 and volume > vol_sma20 * 1.15,st.dir == -1
T8-04,ORB Pro seans kırılımı (rapor uyarlaması: 10 bar Donchi,swing,1D,tek enstruman,htf.dir == 1 and close > ema34 and close > hh10,close < ll10 and close < ema34
T8-05,MTF Range Flip HTF market structure bias,swing,1D,tek enstruman,htf.dir == 1 and close > ema50 and close > hh15,close < ll15 and close < ema50
T8-07,StackLight MTF momentum stack + Stochastic,day,1H,tek enstruman,"htf.dir == 1 and ema13 > ema34 and ema34 > ema89 and cross_over(stoch.k, 45)",ema13 < ema34 or stoch.k < 45
V1A,VOLTRAN-1A swing kırılım ve rejim motoru (v3),swing,1D,tek enstruman,(st_w.dir == 1 or (close_1w >= ema21w * 0.985 and ema8w > ema21w)) and st.dir == 1 and dmi14.plus > dmi14.minu,st.dir == -1 and close < ema21
V1B,VOLTRAN-1B SMC + ML geri çekilme motoru (v3),swing,1D,tek enstruman,weekly_trend == 1 and close > ema34 and ((low > high[2] * 0.990) or (low <= ema21 * 1.02 and close > ema21 and,(ml_skor <= -0.7 and close < ema34 * 0.985)
V2A,VOLTRAN-2A saatlik adaptif kanal (TOTT) + seans kırılım,day,1H,tek enstruman,(st_htf.dir == 1 or close_1d >= ema21h * 0.985) and confluence_puan >= 70 and dmi14.plus >= dmi14.minus * 0.95,ott.dir == -1 and close < ema34
V2B,VOLTRAN-2B saatlik momentum şeridi + likidite dönüşü (v,day,1H,tek enstruman,(st_htf.dir == 1 or close_1d >= ema21h * 0.985) and ema13 > ema34 * 0.998 and close > ema34 and stoch.k >= sto,(ema13 < ema34 * 0.995 and rsi14 < 45)
```
