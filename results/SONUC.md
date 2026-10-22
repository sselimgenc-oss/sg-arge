# Strateji sonuç listesi (başarılı / başarısız)

Bu rapor mevcut sonuç dosyalarını birleştirir; yeni backtest veya istatistik hesaplamaz. Kart başına tek nihai durum vardır (en iyi piyasa/zaman dilimi satırı): **Geçti > Koşullu > Bekliyor > Reddedildi > Doğrulanamaz > Ertelendi > Kapsam dışı**. `Bekliyor`, sonraki aşamanın henüz koşmadığı geçici durumdur. Diğer piyasalar `results/SONUC.csv` içindeki `piyasa_ayrintisi` sütunundadır.

## Özet sayılar

| Durum | Toplam | Günlük/swing | Gün içi (day) |
|---|---:|---:|---:|
| Geçti | 2 | 2 | 0 |
| Koşullu | 1 | 1 | 0 |
| Bekliyor | 49 | 13 | 36 |
| Reddedildi | 93 | 93 | 0 |
| Doğrulanamaz | 270 | 117 | 153 |
| Ertelendi | 3 | 2 | 1 |
| Kapsam dışı | 4 | 2 | 2 |
| **Toplam** | **422** | 230 | 192 |

## Paper trade'e hazır (Geçti)

| ID | Strateji | Piyasa/tf | PF (IS, 1x) | OOS getiri | Bootstrap MDD95 | Evren |
|---|---|---|---:|---:|---:|---|
| C07 | Codex Algo 21: wd_adx_breakout_risk | ABD25 | 2.18 | 13.0% | 10.1% | pit |
| R01 | Qullamaggie breakout continuation + episodic pivot | ABD25/1D | 2.02 | 1.6% | 13.8% | pit |

## Koşullu

| ID | Strateji | Piyasa/tf | PF (IS, 1x) | OOS getiri | Bootstrap MDD95 | Şerh |
|---|---|---|---:|---:|---:|---|
| A6-010 | The Gap Momentum System | EMTIA/1D | 1.38 | 7.8% | 10.6% | on donem negatif |

## Bekliyor (sonraki aşama koşmadı)

| ID | Strateji | Piyasa/tf | Bekleyen aşama |
|---|---|---|---|
| A1-009 | 1% per week on NASDAQ100 | - | asama1: tarama bekliyor |
| A1-025 | TASC 2026.03 One Percent A Week | - | asama1: tarama bekliyor |
| A2-002 | Stochastic Daily Breakout for Gold | - | asama1: tarama bekliyor |
| A2-021 | Magic 100 | - | asama1: tarama bekliyor |
| A2-030 | Channel MA Short-Term System | - | asama1: tarama bekliyor |
| A3-002a | geraked CEZLSMA | - | asama1: tarama bekliyor |
| A3-002b | geraked 3MAF | - | asama1: tarama bekliyor |
| A3-002c | geraked CP1 | - | asama1: tarama bekliyor |
| A3-002d | geraked BBRSI | - | asama1: tarama bekliyor |
| A3-002f | geraked DHLAOS | - | asama1: tarama bekliyor |
| A3-002h | geraked NWERSIASF | - | asama1: tarama bekliyor |
| A3-002i | geraked LRCUTB | - | asama1: tarama bekliyor |
| A3-010a | Freqtrade Strategy001 | - | asama1: tarama bekliyor |
| A3-010b | Freqtrade Strategy002 | - | asama1: tarama bekliyor |
| A3-010c | Freqtrade Strategy003 | - | asama1: tarama bekliyor |
| A3-010d | Freqtrade Strategy004 | - | asama1: tarama bekliyor |
| A3-011a | pandianmn fork: Strategy001 (A3-010a ile aynı kural varsayımı) | - | asama1: tarama bekliyor (alias: A3-010a) |
| A3-011b | pandianmn fork: Strategy002 (A3-010b ile aynı kural varsayımı) | - | asama1: tarama bekliyor (alias: A3-010b) |
| A3-011c | pandianmn fork: Strategy003 (A3-010c ile aynı kural varsayımı) | - | asama1: tarama bekliyor (alias: A3-010c) |
| A3-011d | pandianmn fork: Strategy004 (A3-010d ile aynı kural varsayımı) | - | asama1: tarama bekliyor (alias: A3-010d) |
| A3-011e | pandianmn fork: Strategy005 (resmi depo kodu) | - | asama1: tarama bekliyor |
| A6-003 | Simple Ideas for a Mean Reversion Strategy with Good Results | - | asama1: tarama bekliyor |
| A6-019 | Overnight Seasonality in Bitcoin | - | asama1: tarama bekliyor |
| A6-022 | How to Design a Simple Multi-Timeframe Trend Strategy on Bitcoin | - | asama1: tarama bekliyor |
| G003 | Reinforced Smooth Scalp (Freqtrade, hyperopt parametreleri) | - | asama1: tarama bekliyor |
| M008 | RSI2 Strategy: Pullback on Ex-Russell 3000 Stocks | - | asama1: tarama bekliyor |
| M010 | RSI Volatility Spread | - | asama1: tarama bekliyor |
| M013 | Simple H4 Mobile Trading System | - | asama1: tarama bekliyor |
| M016 | One Percent a Week Strategy (TQQQ) | - | asama1: tarama bekliyor |
| M027 | Renko Automated Trading System | - | asama1: tarama bekliyor |
| M036 | A Mean Reversion Strategy with 2.11 Sharpe (QQQ with Dynamic SMA300 Stop) | - | asama1: tarama bekliyor |
| O1-003 | PHL1 YİĞİT KAYNAK | - | asama1: tarama bekliyor |
| O1-004 | PHL2 YIGITBOX | - | asama1: tarama bekliyor |
| O1-011 | SuperTrendVadeliStratejisi | - | asama1: tarama bekliyor |
| O1-017 | Sistem 2: RSI ortalama kesisimi (VIOP30 5 dk, long) | - | asama1: tarama bekliyor |
| O1-027 | PMax Explorer STRATEGY & SCREENER | - | asama1: tarama bekliyor |
| O1-037 | Simple and Profitable Scalping Strategy (ForexSignals TV) | - | asama1: tarama bekliyor |
| O1-039 | Laguerre RSI by KivancOzbilgic STRATEGY | - | asama1: tarama bekliyor |
| O1-064 | Try this NQ Strategy + Code | - | asama1: tarama bekliyor |
| O2-005 | Trading Made Simple | - | asama1: tarama bekliyor |
| P03 | 4H Sweet Spot (1D/4H/1H) PMax + ADX rejim (aynı strateji: R6) | - | asama1: tarama bekliyor |
| P04 | VOLTRAN-R2 intraday hibrit (RRS göreceli güç + RVOL ORB) (aynı strateji: S8/R8) | - | asama1: tarama bekliyor |
| P3-008 | Strategy based on Squeeze Momentum Indicator [LazyBear] | - | asama1: tarama bekliyor |
| P3-014 | EmperorBTC's VWAP Strategy | - | asama1: tarama bekliyor |
| R03 | RealDayTrading göreceli güç (RRS) 1H momentum | - | asama1: tarama bekliyor |
| R04 | Stocks in Play (Zarattini) RVOL açılış kırılımı | - | asama1: tarama bekliyor |
| T8-07 | StackLight MTF momentum stack + Stochastic | - | asama1: tarama bekliyor |
| V2A | VOLTRAN-2A saatlik adaptif kanal (TOTT) + seans kırılım (v3) | - | asama1: tarama bekliyor |
| V2B | VOLTRAN-2B saatlik momentum şeridi + likidite dönüşü (v3) | - | asama1: tarama bekliyor |

## Önerilen portföy

Kaynak: `results/asama2b.csv + asama2b_pit.csv` (evren: pit) | Adaylar (3): A6-010:EMTIA, C07:ABD25, R01:ABD25

**Birleşik portföy (eşit risk, 1/N sermaye):**

| Donem | Gun | Getiri | CAGR | PF (gunluk) | MDD | Bootstrap MDD %95 | Bootstrap CAGR p05 | MDD kapisi (<=%15) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **OOS** | 516 | 7.5% | 3.6% | 1.20 | 2.9% | 4.7% | 0.4% | gecti |
| **IS** | 1193 | 21.1% | 4.1% | 1.24 | 4.6% | 6.7% | 1.3% | gecti |

Portfoy genelinde IS'te en yuksek acik baslangic riski (islemlerin `initial_risk` toplami / ozkaynak): **2.16%**. Her kitap motorun %2 toplam risk tavaniyla calisir; 1/N agirlikla portfoy riski kitaplarin ortalamasidir, dolayisiyla tek kitabin tavanini asamaz.

Ayrıntı (adaylar tek tek, korelasyon, yöntem): [`results/portfoy.md`](portfoy.md).

## Reddedildi

### Aşama 1 (hızlı tarama): 15

| ID | Strateji | Piyasa/tf | Alt neden |
|---|---|---|---|
| A2-007 | Pro MA Crossover EA for MT5 | ABD25/1D | islem<30 |
| A3-003 | Sector-Momentum-Pullback (NSE, RSI pullback + ATR iz süren stop) | ABD25/1D | islem<30, PF_1x<1.1, net_2x<=0 |
| A4-004 | RSI 82 | ABD25/1D | islem<30 |
| A5-020 | Finding Consistent Trends with Strong Momentum - RSI for Trend-Following and Momentum Strategies | ABD25/1D | islem<30 |
| G008 | Holy Thursday Sprint | ABD25/1D | islem<30, PF_1x<1.1, net_2x<=0 |
| G009 | Pre-Easter Week | ABD25/1D | islem<30, net_2x<=0 |
| G010 | OPEX Week Long | ABD25/1D | PF_1x<1.1, net_2x<=0 |
| M012a | 5 Swing Trading Strategies for Beginners - Strategy 1: The Mean Reversion Band and IBS | ABD25/1D | net_2x<=0 (alias: O3-002) |
| M012c | 5 Swing Trading Strategies for Beginners - Strategy 3: The 5-Day Low Entry | ABD25/1D | net_2x<=0 |
| M012d | 5 Swing Trading Strategies for Beginners - Strategy 4: Volatility Contraction | ABD25/1D | PF_1x<1.1, net_2x<=0 |
| O3-002 | Overnight swing strategy in the S&P 500 (10 Best Swing #2) | ABD25/1D | net_2x<=0 |
| O3-011 | 5-Day Low of the Range (IBS<0.25) - S&P 500 | ABD25/1D | PF_1x<1.1, net_2x<=0 |
| O3-013 | Turnaround Tuesday (SPY) | ABD25/1D | PF_1x<1.1, net_2x<=0 |
| O3-014 | 3 Days Down Overnight (S&P 500) | ABD25/1D | PF_1x<1.1, net_2x<=0 |
| O3-015 | IBS (Internal Bar Strength) SPY – IBS<0.2 al / >0.8 sat | ABD25/1D | net_2x<=0 |

### Aşama 2a (rastgele seçim/giriş testi, piyasa betası): 45

| ID | Strateji | Piyasa/tf | Alt neden |
|---|---|---|---|
| A3-007 | Backtesting.py örnek SmaCross(10,20) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.716, ortR p=0.965 (esik 0.05) |
| A3-008a | stratestic MA Crossover(20,150) | KRIPTO25/1D | null'u gecemedi (piyasa betasi) - PF p=0.692, ortR p=0.483 (esik 0.05) |
| A3-008b | stratestic MACD(26,12,9) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.204, ortR p=0.010 (esik 0.05) |
| A3-009a | Systematic-Trading-Backtester: MA 20/50 | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.174, ortR p=0.015 (esik 0.05) |
| A3-009b | Systematic-Trading-Backtester: Bollinger ortalamaya dönüş | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.184, ortR p=0.005 (esik 0.05) |
| A3-009c | Systematic-Trading-Backtester: 252 günlük momentum | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.577, ortR p=0.642 (esik 0.05) |
| A4-003 | Overbought or Oversold SPY else UVXY | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.022, CAGR p=0.087 (esit 0.05) |
| A4-005 | SPY RSI 30 Test | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.766, CAGR p=0.761 (esit 0.05) |
| A5-009 | XLP mean reversion (IBS + 25 günlük bant) (10 Best Swing #7) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.716, ortR p=0.736 (esik 0.05) |
| A6-001 | Double 7's Strategy | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.881, ortR p=0.567 (esik 0.05) |
| B1-002 | AlphaTrend Strategy (TradingView, Kıvanç Özbilgiç) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.502, ortR p=0.055 (esik 0.05) |
| B3-001 | RSI Mean Reversion Trading Strategy in Nasdaq100 (QQQ) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.303, ortR p=0.219 (esik 0.05) |
| B3-005 | Triple RSI Strategy (90.36% win rate) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.736, ortR p=0.756 (esik 0.05) |
| B3-010 | RSI-2 Larry Connors (ProRealCode) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.289, ortR p=0.060 (esik 0.05) |
| B3-014 | Cross-Sectional Equity Mean Reversion (Quantpedia #13) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.816, CAGR p=0.806 (esit 0.05) |
| M006 | RSI Double-Bottom for Amibroker (AFL) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.383, ortR p=0.055 (esik 0.05) |
| M011 | Double 7's Strategy (Larry Connors) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.881, ortR p=0.567 (esik 0.05) (alias: A6-001) |
| M012b | 5 Swing Trading Strategies for Beginners - Strategy 2: Turnaround Tuesday | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.154, ortR p=0.229 (esik 0.05) (alias: O3-001) |
| M014 | Larry Connors' 2-Day RSI Holy Grail (Multi-Stock Adaptation) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.522, ortR p=0.249 (esik 0.05) |
| M037 | What Is the Best RSI Oversold Level? We Tested 1 Through 50 | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.502, ortR p=0.368 (esik 0.05) |
| M050 | Short-Term Reversal Effect in Stocks (Quantpedia #013) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.816, CAGR p=0.806 (esit 0.05) (alias: B3-014) |
| O1-001 | AlphaTrend Strategy (Matriks) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.498, ortR p=0.070 (esik 0.05) |
| O1-038 | KPL Swing Strategy | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.652, ortR p=0.383 (esik 0.05) |
| O1-066 | Accumulation/Distribution Range Breakout Strategy NT8 - August 2018 S&C | ABD25/1W | null'u gecemedi (piyasa betasi) - PF p=0.279, ortR p=0.313 (esik 0.05) |
| O1-075 | MeanReversal Strategy NT8 | EMTIA/1D | null'u gecemedi (piyasa betasi) - PF p=0.438, ortR p=0.637 (esik 0.05) |
| O1-079 | Golden Triangle Strategy | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.264, ortR p=0.129 (esik 0.05) |
| O3-001 | Monday reversal in the S&P 500 (10 Best Swing #1) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.154, ortR p=0.229 (esik 0.05) |
| O3-004 | Monday/Tuesday trade in Nasdaq (10 Best Swing #4) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.224, ortR p=0.129 (esik 0.05) |
| O3-007 | Turn of the month strategy S&P 500 (10 Best Swing #9) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.900, ortR p=0.950 (esik 0.05) |
| P01 | Twin OTT (TOTT) çift bantlı trend sistemi | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.169, ortR p=0.025 (esik 0.05) |
| P02 | Kevin Davey Donchian + ADX rejim filtreli kırılım | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.338, ortR p=0.572 (esik 0.05) |
| P3-001 | SuperTrend STRATEGY | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.249, ortR p=0.532 (esik 0.05) |
| P3-002 | BUY and SELL - Backtest single EMA cross By che_trader | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.045, ortR p=0.438 (esik 0.05) |
| P3-003 | UT Bot Strategy | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.806, ortR p=0.980 (esik 0.05) |
| P3-004 | EMA Slope + EMA Cross Strategy (by ChartArt) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.104, ortR p=0.448 (esik 0.05) |
| P3-005 | UT Bot Strategy with Backtesting Range [QuantNomad] | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.871, ortR p=0.985 (esik 0.05) |
| P3-007 | Heikin Ashi Supertrend | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.826, ortR p=0.383 (esik 0.05) |
| R02 | IBS < 0.30 + 25 günlük volatilite bandı ortalamaya dönüş | BIST30/1D | BIST USD kapisi - USD: PF_1x<1.1,net_2x<=0 |
| R05 | Dual Signal Trend Sentinel: 65 günlük Z-skor rejimi | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.254, ortR p=0.020 (esik 0.05) |
| T8-01 | TrendShift Supertrend + ADX rejim adaptif | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.547, ortR p=0.373 (esik 0.05) |
| T8-02 | TrendLock MTF Supertrend + Donchian kırılımı | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.428, ortR p=0.010 (esik 0.05) |
| T8-04 | ORB Pro seans kırılımı (rapor uyarlaması: 10 bar Donchian) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.537, ortR p=0.483 (esik 0.05) |
| T8-05 | MTF Range Flip HTF market structure bias | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.677, ortR p=0.448 (esik 0.05) |
| V1A | VOLTRAN-1A swing kırılım ve rejim motoru (v3) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.632, ortR p=0.169 (esik 0.05) |
| V1B | VOLTRAN-1B SMC + ML geri çekilme motoru (v3) | ABD25/1D | null'u gecemedi (piyasa betasi) - PF p=0.249, ortR p=0.045 (esik 0.05) |

### Aşama 2b (OOS, stres, plato, bootstrap): 33

| ID | Strateji | Piyasa/tf | Alt neden |
|---|---|---|---|
| A4-002 | Simple TQQQ RSI mean reversion | ABD25/1D | bootstrap MDD>%15 |
| A6-004 | Mean Reversion Entry Timing | ABD25/1D | bootstrap MDD>%15 |
| C01 | Haftalik yonlu gunluk geri cekilme (wd_pullback_risk, Codex Algo 21) | BIST30/1D | null, OOS ortR<=0, 2x PF<1.2, bootstrap MDD>%15 |
| C02 | Haftalik yonlu gunluk CCI devam (wd_cci_continuation_risk, Codex Algo 21) | BIST30/1D | null, OOS ortR<=0, bootstrap MDD>%15 |
| C03 | Codex Algo 21: wd_flow_confirmation_risk | BIST30 | null, OOS ortR<=0 |
| C04 | Codex Algo 21: wd_ichimoku_balance_risk | BIST30 | gerekce sonuc dosyasinda bos |
| C05 | Codex Algo 21: wd_dmi_trend_risk | BIST30 | null, 2x PF<1.2, 3x net<=0, +1 bar net<=0, plato<%60, bootstrap MDD>%15 |
| C06 | Codex Algo 21: wd_kama_efficiency_risk | BIST30 | null, 2x PF<1.2, 3x net<=0 |
| C08 | Codex Algo 21: wd_dual_momentum_risk | ABD25 | gerekce sonuc dosyasinda bos |
| C09 | Codex Algo 21: wd_cci_continuation_risk | ABD25 | null, OOS ortR<=0 |
| C10 | Codex Algo 21: wd_breakout_risk | ABD25 | gerekce sonuc dosyasinda bos |
| C11 | Codex Algo 21: wd_momentum_risk | ABD25 | gerekce sonuc dosyasinda bos |
| C12 | Codex Algo 21: wd_ichimoku_balance_risk | ABD25 | gerekce sonuc dosyasinda bos |
| C13 | Codex Algo 21: wd_reversion_risk | ABD25 | null, OOS ortR<=0, 2x PF<1.2, 3x net<=0 |
| C14 | Codex Algo 21: wd_breakout_risk | KRIPTO25 | gerekce sonuc dosyasinda bos |
| C15 | Codex Algo 21: wd_cci_continuation_risk | KRIPTO25 | null, OOS ortR<=0 |
| C16 | Codex Algo 21: wd_dual_momentum_risk | EMTIA | gerekce sonuc dosyasinda bos |
| C17 | Codex Algo 21: wd_cci_continuation_risk | EMTIA | gerekce sonuc dosyasinda bos |
| C18 | Codex Algo 21: wd_breakout_risk | EMTIA | gerekce sonuc dosyasinda bos |
| C19 | Codex Algo 21: wd_pullback_risk | EMTIA | gerekce sonuc dosyasinda bos |
| C20 | Codex Algo 21: wd_momentum_risk | EMTIA | gerekce sonuc dosyasinda bos |
| C21 | Codex Algo 21: wd_adx_breakout_risk | EMTIA | gerekce sonuc dosyasinda bos |
| G007 | Crude Oil Tuesday/Thursday Pullback | KRIPTO25/1D | OOS ortR<=0, 3x net<=0 |
| G011 | PowerX - RSI + Stochastic + MACD (Freqtrade powerxhopt) | ABD25/1D | OOS ortR<=0 |
| M012e | 5 Swing Trading Strategies for Beginners - Strategy 5: New Highs with Low IBS | ABD25/1D | 2x PF<1.2, 3x net<=0 (alias: O3-003) |
| M015 | Larry Connors' Cumulative RSI Strategy | ABD25/1D | 2x PF<1.2 |
| M017 | RSI 2 Portfolio (Composer Symphony) | ABD25/1D | bootstrap MDD>%15 |
| M020a | The 30-Minute Stock Trader - Strategy 1: Weekly Rotation (Laurens Bensdorp) | ABD25/1D | OOS ortR<=0, bootstrap MDD>%15 |
| M038 | Best Time Frame for Candlestick Patterns (3 Candlestick Patterns Strategy on SPY) | ABD25/1D | 2x PF<1.2 |
| O2-025 | The Holy Grail | ABD25/1D | bootstrap MDD>%15 |
| O2-027 | TQQQ For The Long Term (Reddit Post Link) | ABD25/1D | bootstrap MDD>%15 |
| O3-003 | Buy when S&P 500 makes new intraday high (10 Best Swing #3) | ABD25/1D | 2x PF<1.2, 3x net<=0 |
| P3-011 | MACD Strategy with trailing ATR stop | KRIPTO25/1D | OOS ortR<=0 |

## Doğrulanamaz (270)

<details><summary><b>kaynak erisilemedi</b> (117)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A1-001 | DAX 15Min - False Breakout / SuperTrend | - |
| A1-003 | CAC40 Trend Following on 10-sec Timeframe | - |
| A1-005 | DOW Breakout 15Min | - |
| A1-007 | Morning CAC40 | - |
| A1-011 | DAX40 H1 Long Trend System | - |
| A1-013 | Strategy 3 CANDLES with CAC40 | - |
| A1-014 | Blue Monday DAX | - |
| A1-016 | VIOP Scalping - ATR SNIPER | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| A1-017 | VIOP Scalping - Original | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| A1-018 | HYSTERIAN BIST:SISE TRADE ALGORITHM | - |
| A1-019 | BIST30 to S&P 500 ATR Momentum Rider | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| A1-021 | Pivot Master LITE | - |
| A1-022 | Slight Swing Momentum Strategy | T16: sinyal tanimi eksik (formul ve cikis kurallari) |
| A1-023 | ORB Breakout Strategy (chartsquare) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| A1-024 | TrendMaster Pro 2.3 with Alerts | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| A1-026 | LongBuyLongSell 90% profit Excellent Win Rate Strategy | - |
| A2-010 | ICE (Impulse Confirmation Engine) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| A3-004 | Pairs_Trading (gün içi eş-bütünleşme, M1) | - |
| A4-007 | Enhanced Short-Term Mean Reversion Algorithm | T22: kaynak yeniden okundu (QuantConnect forumu, Jing Wu, Reider 'Enhancing Short-Term Mean-Reversion Strategies'); kod eki sayfa metninde yok. Kurallar: aylik evren (fiyat>5$, temel verisi olan en yuksek dolar hacimli 50 hisse, EV/EBITDA>0), son gunu atlayan |
| A4-008 | RSI Extremes Intraday E-mini (embedded backtest) | - |
| A4-009 | Volume Spikes in Oil Futures (embedded backtest) | - |
| A4-010 | Intraday Mean Reversion BTCUSD (r/algotrading yaklasimi, embedded backtest) | - |
| A5-012 | Self-Imposed Limits to Arbitrage | - |
| A5-013 | Trading Volume Effects of Moving Average Heuristics | - |
| A5-015 | Reversal in Cryptocurrency Returns | T22: kaynak yeniden okundu (https://paperswithbacktest.com/strategies/reversal-in-cryptocurrency-returns, Kiefer & Nowotny, Haziran 2026): 8-10 haftalik olusum penceresinde kaybedenleri al / kazananlari sat (LMW), Jegadeesh-Titman ust uste binen portfoyler, ha |
| A5-016 | Stock Market Predictability in the MENA: Evidence from New Variance Ratio Tests and Technical Trade Analysis | - |
| A5-021 | The 8-K Trading Gap | - |
| A5-022 | Trend-based Forecast of Cryptocurrency Returns | - |
| A5-023 | Signal Prediction in cryptocurrency tradeoperations: a machine learning-based approach | - |
| A5-024 | Impact of Earnings Announcements for Dow Jones Index Stocks | - |
| A6-012 | Better Tests with Oversampling (3 mum fiyat aksiyonu) | - |
| A6-016 | Building and Testing Trend-Following Strategies on One-Minute SPY Data | - |
| A7-006 | Kripto 50 parite long-only gosterge tarayici sistemi | - |
| A7-007 | ES Renko/Donchian 21 pullback scalp (RichJamo gunlugu) | - |
| B2-001 | Opening-Range Breakout (TradingView, vadeli) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| B2-005 | Athena Momentum Squeeze - Short, Lean, and Mean | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| B3-009 | Connors/Alvarez 2009 basit ortalamaya donus (ES+TY) | - |
| B3-015 | Is there 1 Strategy that just works? (gunluk long-only ETF betigi) | - |
| M007 | ForexFactory Post 8694795 Swing Strategy | - |
| M018 | TradingView Script LHKOdUOs | - |
| M022 | Quadrant Strategy (DAX 5m) | - |
| M023 | Quadrant 2.0 DAX 5 min | - |
| M024 | MQL5 Code 8688 (EURUSD M1 Day Trade) | - |
| M025 | MQL5 Code 8970 (EURUSD M5) | - |
| M028 | TradingView Script Qh7OYDvf (BTC/Crypto 5m) | - |
| M029 | Geometric Grid Machine 3Commas (HYPEUSDT 15m) | - |
| M030 | BNB Grid Bot Long Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M031 | 3Commas Pullback Sniper Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M032 | XAU Grid Bot Long Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M033 | SMC Pro BTC ICT Order Blocks FVG DOE | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M035 | Breakout Trading Strategy (Experiments Summary 2025) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M043 | Volatility Regime Momentum | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M044 | Chart Pattern Backtester (43 Crypto Pairs H4) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M045 | Optimized Heikin Ashi Strategy with Buy/Sell Options | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M046 | ELLIPSE Bidirectional Swing Trading Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M047 | Gold Swing More Trades 50 SL 100 TP | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M048 | 3Commas Turtle Strategy (ETHUSDT H4) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M049 | BTC RSI Strategy 3Commas | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M051 | MeanReversionRSI (Jesse.Trade) | T16: sinyal tanimi eksik (kesin RSI parametreleri ve kural kodu) |
| M052 | ForexFactory Post 3629700 Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M053 | Forex-Station Attachment 3477006 System Package | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M054 | NexusFi Thread 58030 Post 858460 Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M055 | Portfolio123 Testimonial 17867 Ranking Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M056 | FreqtradeHyperOpt (RSI / MACD / EMA Strategies) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| M057 | NSE Pattern Scanner (2600+ NSE Stocks Swing) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| O1-005 | ROTT-SOTT | - |
| O1-015 | Algoritmik Trade Sistem Sinyalleri ve Gercek Hesap Paylasimli (Seffaf) - klasik trend sistemi | - |
| O1-018 | MACD/RSI/MA/DEMA sistemi (VIOP ornekleri) | - |
| O1-019 | EMA 25/68 BIST30 Futures | T16: sinyal tanimi eksik (ek filtreler, seans saatleri ve cikis kurali) |
| O1-029 | Grover Llorens Activator Strategy Analysis | - |
| O1-030 | Uhl MA System - Strategy Analysis | - |
| O1-031 | Trendline Breaks with Multi Fibonacci Supertrend Strategy (TMFS) | - |
| O1-032 | Scalping Support Resistance Strategy | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| O1-033 | Scalping with Bill Williams Alligator | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| O1-034 | [Sniper] SuperTrend + SSL Hybrid + QQE MOD | - |
| O1-035 | ORB Heikin Ashi SPY 5min Correlation Strategy | - |
| O1-036 | Gold ORB Strategy (15-min Range, 5-min Entry) | - |
| O1-040 | Pathfinder DAX 4H | - |
| O1-042 | Smoothed Bollinger% Strategy Daily | - |
| O1-043 | Navigator DAX Trading Strategy 4H | - |
| O1-044 | ALEX AutoTradingBot INDEX | T16: sinyal tanimi eksik (kurallar kaynakta okunamadi) |
| O1-047 | Kama & Sma Trading System DAX mtf | - |
| O1-049 | Oil 10min 'hammernegated' pattern strategy | - |
| O1-051 | Brent Oil 5 minutes trading strategy | T16: sinyal tanimi eksik (kurallar kaynakta okunamadi) |
| O1-052 | Wing's Resistance Breacher (DAX-30m) | T16: sinyal tanimi eksik (kurallar kaynakta okunamadi) |
| O1-054 | End Of Day – YEN M15 | - |
| O1-068 | MACD Cross Over | T16: sinyal tanimi eksik (periyotlar ve filtreler .zip icindeki C# kodunda) |
| O1-069 | Woodies CCI Autotrader | - |
| O1-071 | Adx Breakouts Strategy | - |
| O1-072 | Automated Strategy for trading NQ | T16: sinyal tanimi eksik (kurallar .zip icindeki C# kodunda) |
| O1-073 | LargeTrades Strategy NT8 | - |
| O1-074 | Camarillapoints ATS | - |
| O1-076 | Mean Reversion Swing Trading Strategy | - |
| O1-077 | Automated Strategy StrategyPeakHoursTradingNQ | T16: sinyal tanimi eksik (kurallar .zip icindeki C# kodunda) |
| O2-001 | JP225 Opening Range Break Strategy | - |
| O2-002 | JP225 ADR Extension-Based Momentum Model | - |
| O2-018 | MACD + EMA | T16: sinyal tanimi eksik (cikis ve parametreler) |
| O2-021a | Jesse: Simple Bollinger Bands Strategy | T16: sinyal tanimi eksik (tekil strateji kodu ve parametreler) |
| O2-021b | Jesse: RSI Trend | T16: sinyal tanimi eksik (tekil strateji kodu ve parametreler) |
| O2-021c | Jesse: IchimokuCloud | T16: sinyal tanimi eksik (tekil strateji kodu ve cikis kurali) |
| O2-024 | BeatTheMarketMomentum (SPY intraday momentum, embedded backtest) | - |
| O3-018 | VRT Levels - hacim tabanli destek/direnc kirilim+reddi | - |
| O3-019 | Hisse swing stratejisi (aciklanmamis, %96 kazanma) | - |
| O3-020 | 1 dk long-only gun ici strateji (1:1 RR) | - |
| O3-021 | TS Trend Strategy - DAX 5 dk long-only | - |
| O3-022 | DAX Value Area gunluk bias sistemi | - |
| O3-023 | London Session ORB - GBP (mekanik kirilim gunlugu) | - |
| O3-024 | NQ long/short otomatik trend stratejisi | - |
| O3-026 | Bollinger Bands + RSI tick chart (ninZa) - PF 1.5-1.86 | - |
| P3-006 | [STRATEGY][UL]Price Divergence Strategy v1.0 | - |
| P3-009 | Delta-RSI Strategy (with filters) | T16: sinyal tanimi eksik (giris/cikis kurali ve gostergeler kaynakta okunamadi) |
| P3-015 | Davin's 10/200MA Pullback on SPY Strategy v2.0 | - |
| P3-016 | 2-Period RSI strategy (with filter) | T16: sinyal tanimi eksik (kaynak scriptin esik ve filtre degerleri) |
| P3-017 | Kirk65 UTBot Strategy Fixed | T16: sinyal tanimi eksik (key_value ve atr_period varsayilanlari) |
| P3-018 | Long-Only Opening Range Breakout (ORB) with Pivot Points | - |
| P3-019 | EMA Cross Strategy | T16: sinyal tanimi eksik (EMA periyotlari ve filtreler) |
| P3-020 | RSI Strategy [PrimeAutomation] | T16: sinyal tanimi eksik (RSI periyodu, esikler ve cikis) |

</details>

<details><summary><b>kural kaynakta gizli</b> (35)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A1-020 | Antony.N4A - NQ ORB Quartile Str v6.3 | - |
| B3-002 | RSI Pullback Strategy (SPY) | - |
| B3-003 | GBPUSD Forex Strategy (Python Code Included) | - |
| B3-004 | Trend Following and Mean Reversion Strategy - Combined (QQQ) | - |
| M034 | Backtested Intraday Mean Reversion (ES & NQ Futures) | - |
| M039 | We Combined RSI, EMA, and VWAP on QQQ | - |
| M040 | A Simple Stochastic Pullback Strategy for Uptrending Markets | - |
| M041 | New Low Trading Strategy (QQQ) | - |
| M042a | 2 Price Action Trading Strategies With Small Drawdowns - Strategy 1: Price Compression Strategy (GLD) | - |
| M042b | 2 Price Action Trading Strategies With Small Drawdowns - Strategy 2: Turnaround Tuesday (SSO) | - |
| O1-012 | Yükselen Formasyon Stratejisi | - |
| O2-013 | NoPain MT5 | - |
| O2-014 | MSC Gold Stable Pro | - |
| O2-015 | FXtrading | - |
| O2-016 | World PEACE Multi FX Algo | - |
| O3-006 | MACD-Histogram on the S&P 500 (10 Best Swing #8) | - |
| O3-008 | Day trading strategy #78 (SPY, acilis->kapanis) | - |
| O3-010 | Opening Range Breakout - QS gizli varyant (S&P 500) | - |
| O3-012 | MACD and RSI Strategy (73% win rate) | - |
| O3-017 | RSI SPY trading strategy (RSI(2) on SPY) | - |
| O3-025 | Bollinger Prism - NQ reversal (PF 2.78) | - |
| O3-027 | Mean Reversion Strategy Journal - Buy Sell Bands (ABD hisseleri) | - |
| O3-030 | 75%+ win rate trend stratejisi (Jim Brown kitabindan) - EURUSD | - |
| P3-021 | NQ Alpha Engine | - |
| P3-022 | HTP Momentum2 MNQ1 | - |
| P3-023 | ares | - |
| P3-024 | Calicut Commodities | - |
| P3-025 | Easy Value | - |
| P3-026 | Adaptive Investments | - |
| P3-027 | Iberia Capital Strategy | - |
| P3-028 | US Stock Momentum | - |
| P3-029 | Quant AI SP500 | - |
| P3-030 | AIB STOCKS and FUT | - |
| P3-031 | AEA Algo MES | - |
| P3-032 | SQT Stocks Long Portfolio 2x | - |

</details>

<details><summary><b>kaynakta sinyal tanimi yok</b> (22)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A1-029 | SPX Trading Strategy for ThinkorSwim | - |
| A2-005 | GDS Renko RSI + MACD 4-Mode Demo EA | - |
| A2-009 | The Playground Series v1 to V4 | - |
| A2-017 | ZoneUS30 | - |
| A2-024 | Most Famous Blessing 3.9.6 EA and Setfiles | - |
| A2-025 | The Equilibrium, a key to success! | - |
| A2-026 | v2v dynamic trading system | - |
| A2-027 | Happs Trading System | - |
| A2-028 | TCO Trader EA | - |
| A2-029 | Simple Zigzag + Fibonacci Strategy | - |
| A3-005 | Indice-Trading-Strategy (EMA200 + range filtresi, Pine) | T16: sinyal tanimi eksik (range filtresi parametreleri, stop/TP yuzdeleri) |
| A3-008c | stratestic Momentum(30) | T16: sinyal tanimi eksik (giris/cikis kurali kutuphane kodunda, kaynakta yok) |
| A3-012 | freqtrade/freqtrade-strategies (resmi örnek depo) | T16: sinyal tanimi eksik (toplu depo; tek bir strateji tanimi yok) |
| A3-013 | NostalgiaForInfinity (NFI) | - |
| A3-014 | nateemma/strategies (MomentumRegimeBasket15mFast, ML stratejileri) | - |
| G004 | TIS BTC Momentum + Confluencia | T16: sinyal tanimi eksik (SMA50 zaman dilimi, ATR periyodu, ters 2 ATR mum tanimi) |
| O1-002 | FIRSATÇITRENDİFLİSİSTEMANILBy (Fırsatçı Trend + IF'li sistem) | - |
| O1-007 | SÜPERTRENDMOSTOPTİMİZASYONLU | - |
| O1-041 | Optimization moving average crossing strategy with 'machine learning' | - |
| O1-062 | High and Low Reversals Indicator + Intraday Strategy | - |
| T8-03 | SMC Pro BTC - ICT order block + FVG [DOE] | - |
| T8-08 | Lorentzian Classification (k-NN ML) | - |

</details>

<details><summary><b>ozel kod (seans_saat)</b> (22)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A1-004 | ADX strategy with NASDAQ 30-minutes timeframe | - |
| A1-010 | Monday in Dax40 with 1% | - |
| A1-015 | Late lunch trade DAX40 strategy | - |
| A2-001 | GER40 Evening Coil | - |
| A2-003 | Buy GBPJPY Every Monday | - |
| A2-004 | SessionReopenEA | - |
| A2-012 | ORB Risk Managed - Opening Range Breakout | - |
| A2-013 | Opening Range Breakout with NR4 / NR7 Contraction Filters | - |
| A2-015 | EMA Cross Scalper M15 (XAUUSD) | - |
| A2-019 | Williams%R, SAR X-over 15 minute candles | - |
| A6-023 | Attention Prop Traders: first half hour predicts last half hour | - |
| A7-001 | NQ 5 dk trend-pullback scalp (37 strateji backtest'inden kalan) | - |
| M004 | Beat the Market: Intraday Momentum Strategy for S&P500 ETF (SPY) | - |
| M005 | Intraday Momentum for ES and NQ (Noise Area 90-Day Variant) | - |
| O1-053 | Open Range Breakout DAX 5/15M | - |
| O1-056 | Intraday Stochastic Trading System | - |
| O1-060 | Strategy Based on EMAs, TSI, MACD, and Premarket Highs/Lows | - |
| O2-007 | Another simple system - Time-Frame 15 | - |
| O2-010 | JPN225 QuietDrift (The Nikkei EA That Only Buys When Volume Is Quiet) | - |
| O3-009 | Stocks in Play – 5 dk ORB + Relative Volume (Zarattini/Barbon/Aziz) | - |
| O3-016 | Gap down + 25 MA filtresi (S&P 500 gun ici) | - |
| P3-013 | ORB Strategy [LuciTech] | - |

</details>

<details><summary><b>ihtiyari/yoruma dayali kural (mekanik degil)</b> (14)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A2-018 | TMS for M30 charts | - |
| A2-023 | Up and under price pattern | - |
| O1-058 | /ES Futures Trading Strategy on ThinkorSwim | - |
| O1-059 | Relative Volume Strategy and Momentum Scanner | - |
| O1-063 | Renko Bar Based Trading System | - |
| O1-065 | Camarilla Pivot Points Day Trading System | - |
| O2-003 | XARD - Simple Trend Following Trading System | - |
| O2-004 | Trading Pullbacks System | - |
| O2-006 | Pivot Trading | - |
| O2-009 | M1 Countertrend Scalping Strategy | - |
| O3-031 | RSI Divergence swing - 27 parite gunluk | - |
| O3-032 | RSI50 stratejisi - EURUSD gunluk | - |
| O3-033 | RSIDive (RSI uyumsuzlugu) - EURUSD gunluk | - |
| O3-034 | Trending Pin Bar v2 - EURUSD H4 | - |

</details>

<details><summary><b>ozel kod (tanim_belirsiz)</b> (11)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A2-011 | APEX VELOCITY | T21: kaynak erisilemedi (https://www.mql5.com/en/code/78275) -> Argon T19. cikis kurallari (ATR carpanli basabas, iz suren, maks. hesap dususu) sayisal degerleriyle kartta yok |
| A5-014 | Seasonality, Trend-following, and Mean reversion in Bitcoin | - |
| O1-006 | MOTT-4B Kurgu | T21: kaynak erisilemedi (https://algokutuphanesi.com/Sistem/Detay/MatriksIq/MOTT-4B-Kurgu) -> Argon T19. 5 MOTT bandinin (OTT(HHV)/OTT(LLV) ve ara ortalamalar) formulu kartta yok; O1-009 ile ayni sistemin kopyasi gorunuyor |
| O1-008 | Anıl Özekşi Sistem 1 | T21: kaynak erisilemedi (https://algokutuphanesi.com/Sistem/Detay/MatriksIq/Anil-Özekşi-Sistem-1) -> Argon T19. OTT/StochSlow(500,200,111) bolge kosullari (ott2_bull, stoc1_bull ...) ve seans penceresi Matriks tanimlariyla kartta yok |
| O1-009 | MOTT 4 Kurgu Stratejisi | T21: kaynak erisilemedi (https://algokutuphanesi.com/Sistem/Detay/MatriksIq/MOTT-4-Kurgu-Stratejisi) -> Argon T19. 5 MOTT bandinin formulu kartta yok; O1-006 ile ayni sistemin kopyasi gorunuyor |
| O1-010 | FirsatciTrend 4Bölge LONG | T21: kaynak erisilemedi (https://algokutuphanesi.com/Sistem/Detay/MatriksIq/FirsatciTrend-4Bölge-LONG) -> Argon T19. TOTT/SOTT/HHV-OTT bolge kosullari kartta tanimli degil; seans penceresi |
| O1-013 | OTT-STOCK-HHV-LLV-HOTT-LOTT-LONG | T21: kaynak erisilemedi (https://algokutuphanesi.com/Sistem/Detay/MatriksIq/OTT-STOCK-HHV-LLV-HOTT-LOTT-LONG) -> Argon T19. TOTT/SOTT ve HOTT/LOTT bolge kosullari kartta tanimli degil; seans penceresi |
| O1-055 | Intraday Profit Maker (Best with Automation) | T21: kaynak erisilemedi (https://www.wisestocktrader.com/indicators/4853-intraday-profit-maker-best-with-automation-for-amibroker-afl) -> Argon T19. 'aLPivs == 1' pivot tanimi (cok barli onay mi, low == LLV(12) mi) ve repaint eden ZigZag belirsiz |
| O2-017 | TemaTrendFollowing | T21: kaynak erisilemedi (https://jesse.trade/strategies/tematrendfollowing) -> Argon T19. CMO esigi ve TEMA 20/70 (4H) parametre degerleri kartta yok, 'tema' kutuphanede yok |
| O2-019 | CloudScalper | T21: kaynak erisilemedi (https://jesse.trade/strategies/cloudscalper) -> Argon T19. bbw_expansion tanimi (Bollinger genisligi genislemesi) ve esikleri kartta yok |
| T8-06 | TOTT/OTT tek bantlı (Twin Optimized Trend Tracker, saatlik kurgu) | - |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: tanim_belirsiz)</b> (10)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A6-020 | Market Sentiment and an Overnight Anomaly | - |
| A7-002 | RSI asiri alim/satim Forex sistemi (PF 2.41) | - |
| A7-005 | Long-only ABD hisseleri dakikalik gun ici (Level4) | - |
| G005 | XLP Mean Reversion w/ Twist | - |
| G013 | Trend Trigger | EMA + MTF Stochastic (TradingView) | - |
| M001 | Opening Range Breakout (ORB) 0DTE Options Strategy | - |
| M009 | 5-Year SPY Put Credit Spread Backtest | - |
| M020b | The 30-Minute Stock Trader - Strategy 2: Mean-Reversion Long (Laurens Bensdorp) | - |
| O1-016 | Sistem 1 (piyasa sartlarina gore sekillenen sistem) | - |
| O2-023 | Intraday Trading Strategy for Futures Contract NQ | - |

</details>

<details><summary><b>ozel kod (desen)</b> (6)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A1-027 | Bjorgum Double Tap | T20: motorda kalmadi. 5x3 pivot matrisli cift dip/tepe algoritmasi (Bjorgum Pine); genel bir desen ilkeline indirgenemedi, Pine kaynagi raw.githubusercontent'ta yok |
| A2-006 | Price Action Intraday Trading - Expert for MT5 | T20: motorda kalmadi. 'Destek seviyesinde' kosulunun tanimi kaynakta yok (SRLookback=20 yalniz parametre adi); pin bar/engulfing/inside bar tanimlari ise standart, ama destek tanimi olmadan sinyal eksik kalir |
| A3-002e | geraked ABSAR | T20: motorda kalmadi. Pine kaynagi (ABSAR.pine, raw.githubusercontent) okundu: ZigZag dizisi + ABC fibonacci orani + 6 ortalamali bulut + Parabolic SAR + son 6 bar stochastic donusu, durumlu dizi algoritmasi; stop = lowest(low, 5), hedef = giris + 2 x risk (ka |
| A6-015 | Double Bottom Country ETF Trading | T20: motorda kalmadi. Aylik yeniden tarama, 24 ulke ETF evreni (evrenimizde yok), gecmise donuk merkezli yerel dip teyidi ve limit alim emri; evren disi |
| O1-046 | Fractal breakout intraday Strategy EUR/USD 1H | T20: motorda kalmadi. FX, pip cinsinden hedef/iz suren (stop tipi pips motorda yok) ve 10:00-23:00 seans penceresi (seans saati paketi); piyasa_kisiti FX |
| P3-010 | Dynamic Swing Anchored VWAP STRAT (Zeiierman/PineIndicators) | T20: motorda kalmadi. Zeiierman dinamik cipali VWAP: cipanin pivotta mi onayda mi basladigi ve swing_length=10'un pivot tanimi kaynaktan dogrulanamadi (kaynak okunamadi); tahmin yazilmadi |

</details>

<details><summary><b>ozel kod (durum_makinesi)</b> (6)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A2-020 | Quantum London Trading | T20: motorda kalmadi. Artan lotlu sepet (grid: ayni yonde 40'a kadar kademeli pozisyon) ve repaint eden Quantum gostergesi; motor sembol basina tek pozisyon tutar, gostergenin periyodu kaynakta yok |
| A3-001 | XAUUSD Pullback Window (4 fazlı durum makinesi) | T20: motorda kalmadi. 4 fazli durum makinesi (SCANNING/ARMED/WINDOW_OPEN/ENTRY); EMA egim acisi, ATR bandi ve saat filtresi parametreleri kartta yok, kaynak kodu (sunrise_ogle_xauusd.py) okunmadi. Kaynak okunursa ayri is (genel 'sonra/ardisik' durum ilkeli ger |
| M019 | FullStochastic with Filters - Buy&Sell for Amibroker (AFL) | T20: motorda kalmadi. AFL kodu PositionScore (portfoy siralamasi), ExRem/BarsSince zincirleri ve ForeNmSth3 3 barlik tahmin fonksiyonunu kullanir; tahmin formulu kartta yok |
| O1-048 | Stochastic Gold Trader | T20: motorda kalmadi. 2 asamali kurulum/tetik durum makinesi: kurulumun ne zaman sifirlandigi ve RSI sayaci (RSICounter/RSICounterAdj, LastRSI) kartta yalnizca ozet olarak var; kaynak kodu okunamadi, tahmin yazilmadi |
| O1-061 | Chewie's Super Trend, Hull Average, Donchian Trend Ribbon Trading System | - |
| O2-008 | Highest Open / Lowest Open Trade | T20: motorda kalmadi. Gun ici en yuksek/en dusuk 1H acilis seviyeleri, 'asagi kirip geri donus' durumu ve NY 08:00-12:00 seans penceresi (seans saati paketi) gerektirir |

</details>

<details><summary><b>ozel kod (ozel_gosterge)</b> (5)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A6-009 | Trading the Channel (Inside Channel, Kaufman) | - |
| A6-014 | Trend trading system with Market Meanness Index (Why 90% of Backtests Fail) | T21: kaynak erisilemedi (https://financial-hacker.com/why-90-of-backtests-fail/) -> Argon T19. Zorro LowPass (2. derece) ve MMI tanimlari kartta yalniz sozle var; resmi Zorro kodu bu sandbox'tan okunamadi, bellekten yazilmadi |
| M003 | 5min /ES Futures Strategy For ThinkOrSwim (HalfTrend with Deviation Bands) | T21: kaynak erisilemedi (https://usethinkscript.com/threads/5min-es-futures-strategy-for-thinkorswim.9911/) -> Argon T19. Price girdisi celisiyor: kart high kullanir, kaynak metni 5m ayarinda low der; ayrica yalniz ES vadeli (piyasa_kisiti ES). HalfTrend adiml |
| O1-045 | VECTORIAL DAX (M5) | T21: kaynak erisilemedi (https://www.prorealcode.com/prorealtime-trading-strategies/vectorial-dax-m5/) -> Argon T19. ATAN acisi pipsize'a bagli (GER40 piyasa_kisiti), 10:00-22:00 seans ve zararda zaman stopu (seans saati paketi) |
| O1-050 | EURUSD 15-minutes timeframe Dhigh / Dlow Strategy | T21: kaynak erisilemedi (https://www.prorealcode.com/prorealtime-trading-strategies/eurusd-15-minutes-timeframe-dhigh-dlow-strategy/) -> Argon T19. pip cinsinden kismi kar/izsuren (FX), TEMA/ucgen MA ve cari gun Dhigh/Dlow, seans penceresi; ProBuilder kodu oku |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: ml)</b> (2)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A6-011 | Better Strategies 5: A Short-Term Machine Learning System | - |
| M021 | Intraday Application of Hidden Markov Models | - |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: ozel_gosterge)</b> (2)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| G006 | AutoTune Filter (Financial Hacker) | - |
| M026 | A simple RKD Expert Advisor based on a specified custom RKD indicator (autoRKD_EA) | - |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: seans_saat)</b> (2)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| G001 | KISS - Keep It Simple and Stupid (DAX 5m) | - |
| G002 | VWAP-RSI Scalper FINAL v1 | - |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: tick_veri)</b> (2)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A1-006 | SCALPING CAC40 10 SECONDS | - |
| A6-017 | Can Weakening Morning Order Flow Predict SPY Reversals? | - |

</details>

<details><summary><b>ozel kod (portfoy_rotasyonu)</b> (2)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A4-001 | Short Term Momentum that Works 2.0 - Macro Filter + Mean Reversion | T22: kural agaci Composer acik uc noktasindan okunabildi (https://stagehand-api.composer.trade/api/v1/public/symphonies/dsPSLcRMdQldkyolwGon/score); eski 'erisim engellendi' notu gecersiz. Kurallar tam (RSI/cumulative-return/moving-average-return pencereleri k |
| A4-006 | Opening Range Breakout for Stocks in Play | T22: bu is paketine girmedi (5 dakikalik ABD gun ici veri yok); kural Codex'in seans/rotasyon paketinde. |

</details>

<details><summary><b>ozel kod (renko)</b> (2)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A2-022 | Lets Automate a Simple Renko Strategy! | T20: motorda kalmadi. 10 pip Renko (EURUSD, FX) ve 20-30 pip izsuren; pips stop tipi motorda yok, 'kirmizidan yesile donus + 2 yesil tugla' kurali kaynakta tam degil |
| O1-067 | Renko Trading Strategy NT8 - December 2019 S&C | T20: motorda kalmadi. NT8 Renko tugla boyutu ('2r' = 2 tugla/adaptif ATR) ve hisse basina dolar iz suren stop tanimlari kartta kesin degil; ABD gun ici veri de yok |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: cok_enstruman)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A7-004 | S&P500-VIX diverjans stratejisi (Scherman, BI makalesi) | - |

</details>

<details><summary><b>kaynakta sinyal tanimi yok (ozel kod: desen)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| M002 | Key Reversal Patterns Using Kase Bars | - |

</details>

<details><summary><b>motor destegi yok (iz_suren.fiyat_adim)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| O1-078 | Atr Breakout | - |

</details>

<details><summary><b>motor destegi yok (roi_tablosu)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| G012 | Riding Bollinger Bands (Freqtrade bb_riding, hyperopt) | - |

</details>

<details><summary><b>ozel kod (bekleyen_emir)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A2-014 | Gold MT5 Fractal Breakout EA | T20: motorda kalmadi. Bekleyen Buy Stop (T15) ifade edilebilir; ancak swing high pivot ilkeli (5 sol/5 sag, 200 bar) ve kaynaktaki pozisyon yonetimi yok: yuzde tetikli basabas kilidi, +%0,2'de baslayan %0,2 mesafeli yuzde izsuren ve -%1'de TP'yi giristen %0,15 |

</details>

<details><summary><b>ozel kod (durum_bilgisi)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| R07 | VOLTRAN-R1 swing hibrit (Qullamaggie + Z-skor + IBS dip avcısı) | T20: motorda kalmadi. Cikis giris moduna (MOD_A/MOD_B) bagli; iz_suren ve kismi_kar yalniz MOD_B icin gecerli (pozisyon basina mod). Motorda pozisyon bazli 'giris_modu' yok; ayrica 1W_Bias tanimi lider onayi bekliyor (bias_varsayim). Ayri is |

</details>

<details><summary><b>ozel kod (ml)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A3-002g | geraked MLCEL_MACD | - |

</details>

<details><summary><b>ozel kod (tick_veri)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| O2-011 | PulseStrike Scalper - Statistical Burst Detection EA | - |

</details>

<details><summary><b>veri yok (SPYU,SVIX,KMLM)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| O2-028 | SVIX/XXXX KMLM switcher (single pops) | BT 12/19/23 = 786/10.5 | T22: kural agaci Composer acik uc noktasindan (https://stagehand-api.composer.trade/api/v1/public/symphonies/D9oE44Y87boHDOYQ9rPm/score) okundu ve rotasyon.agac olarak birebir cevrildi (esik, pencere ve varlik listesi kaynaktan; RSI Wilder, SMA/RSI gunluk kapa |

</details>

<details><summary><b>veri yok (SVIX,KMLM)</b> (1)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| O2-026 | KMLM Switcher of Simon97 - Original | T22: kural agaci Composer acik uc noktasindan (https://stagehand-api.composer.trade/api/v1/public/symphonies/syMn9OgFREE0wo8LtYsG/score) okundu ve rotasyon.agac olarak birebir cevrildi (esik, pencere ve varlik listesi kaynaktan; RSI Wilder, SMA/RSI gunluk kapa |

</details>

## Ertelendi (3)

<details><summary><b>sadece short (long-only temel modda test yok)</b> (3)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| A2-016 | RSI Exhaustion Reversal - EURUSD | - |
| A6-021 | Pairs Trading with Country ETFs | T22: motora alinmadi. Strateji piyasa-notr ikili (pairs) kurgusudur: her ikilinin ucuz bacagi long, pahali bacagi esit tutarla SHORT acilir (Distance en kucuk ilk 5 cift, 120 gun olusum, 0,5 std esik); ucuz bacagi tek basina long tutmak kaynak stratejiyi degil |
| M020c | The 30-Minute Stock Trader - Strategy 3: Mean-Reversion Short (Laurens Bensdorp) | - |

</details>

## Kapsam dışı (4)

<details><summary><b>strateji degil (meta/ornek)</b> (4)</summary>

| ID | Strateji | Gerekçe (karttaki not) |
|---|---|---|
| O1-070 | Divergencesystem Strategy | T20: kapsam disi. Sinyal DXJ (Nikkei ETF) fiyatini FXY (yen ETF) ve SPY ile 50 gunluk regresyon uyumsuzlugundan uretir (IM2, CR3); DXJ ve FXY evrenimizde yok, sinyal ikinci/ucuncu enstrumanin serisini gerektirir ve tek-enstrumana indirgenemez |
| O2-012 | OHLCMTF Scalper EA - Multi-Timeframe Price Action | - |
| O2-031 | je-suis-tm/quant-trading (London Breakout, Dual Thrust vb.) | - |
| P3-033 | Index Futures Trading | - |

</details>

## Yöntem özeti

Her strateji kartı aynı koşullarda ([`docs/EVRENSEL_KURALLAR.md`](../docs/EVRENSEL_KURALLAR.md), eşikler [`docs/ELEME_KRITERLERI.md`](../docs/ELEME_KRITERLERI.md)) sınandı: long-only, kaldıraçsız, sinyal kapanmış barla, dolum sonraki açılışta, işlem başı %0,5 risk ve ATR14×3 standart stop (kaynak stopu yoksa). **Aşama 1** IS dönemde (2020-01 → 2024-09) hızlı tarama yapar: işlem ≥ 30, PF ≥ 1,1 ve 2x maliyette net > 0. **Aşama 2a** aynı çıkış kurallarıyla rastgele girişli (rotasyon kartlarında rastgele seçimli) bir null dağılımı kurar; kart PF ve ortalama R'de (rotasyonda PF ve CAGR'de) null'un %95'ini geçmelidir, aksi halde getiri piyasanın kendi sürüklenmesidir (piyasa betası); BIST USD bazında değerlendirilir. **Aşama 2b** OOS (2024-10 sonrası), ön dönem (2015-2019), 2x/3x maliyet ve +1 bar gecikme stresi, kaynak merkezli parametre platosu (komşuluklarda pozitif oran ≥ %60), 20 günlük block bootstrap ile **MDD95 ≤ %15** ve DSR'yi birlikte uygular. Geçmeyen **Reddedildi**; her kapıyı geçip ön dönem negatif, OOS örneği küçük ya da evren yanlılığı gibi şerhi olan **Koşullu**; hepsini geçen **Geçti**. Test edilemeyenler (kaynakta sinyal yok, gizli, özel kod, dakikalık veri yok, kaynak erişilemedi) **Doğrulanamaz**, short fazına bırakılanlar **Ertelendi** sayılır; bu başarısızlık değildir.

## Uyarılar

- BIST ve ABD evrenlerinde survivorship yanlılığı vardır; tarihsel (PIT) evren satırı varsa sabit evren satırının yerine geçer (ABD tam, BIST 2020 sonrası). Olumlu sonuç canlı kanıt değildir.
- Çok sayıda strateji denendiği için şansla geçenler beklenir; DSR paper trading için bilgi niteliğindedir.
- Gün içi kartlarda 1H altı zaman dilimleri yalnız kriptoda (Binance) test edilir; BIST/ABD/emtia için dakikalık veri yoktur.
