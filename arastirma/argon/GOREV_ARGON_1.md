# Argon görevi: erişilemeyen kaynaklardan strateji kurallarını çıkarmak

**Karar:** kullanıcı, 2026-10-24 ("kodlarını bulduramadığımız stratejiler Argon'a verilsin"). **Sahip:** Argon (Gemini). **Denetim:** lider.

## Neden
Faz 1'de 206 strateji "eksik" kaldı. Bunların ~129'unda sorun stratejinin kendisi değil, **kaynağa erişememekti**: TradingView, ProRealCode, QuantConnect, PapersWithBacktest vb. sayfalar o dönem araçlarımıza kapalıydı, kod okunamadı. Gemini web sayfalarını açabiliyor; amaç bu sayfalardaki **kodu ve kuralları birebir** getirmek. Çeviriyi Argon yapmaz (Sonnet yapar); Argon yalnız kaynağı okur ve aktarır.

## Kurallar (çok önemli)
1. Yalnız sayfada **gerçekten yazanı** aktar. Kod varsa kodun **tamamını** kod bloğu içinde, değiştirmeden ver. Kod yoksa kuralları yazarın cümleleriyle **tırnak içinde** alıntıla.
2. Sayfayı açamadıysan ya da kod/kural yoksa: `durum: bulunamadi` yaz ve nedenini söyle. **Tahmin etme, tamamlama, "muhtemelen" diye kural uydurma.** Uydurulmuş bir kural tüm testi çöpe atar; "bulunamadı" ise değerli bir cevaptır.
3. Varsayılan parametre değerlerini (Pine `input(...)` varsayılanları, ProRealCode değişkenleri) koddan oku, ayrı listede ver.
4. Yazarın backtest sonuçlarını (kâr, win rate, PF) **yazma**; bizim testimizi etkilemesin.
5. Her strateji için kısa tut; bir mesajda en çok 10 strateji. 10'u bitirince dur, "devam" denince sonraki 10.

## Çıktı biçimi (her strateji için aynen)
```
### <ID> — <strateji adı>
durum: bulundu | kismi | bulunamadi
kaynak_url: <açtığın gerçek adres>
erisim_notu: <ör. "sayfa açıldı, Pine kodu açık kaynak" / "giriş gerekiyor, açılamadı">
piyasa_ve_tf: <sayfada yazan sembol ve zaman dilimi>
varsayilan_parametreler:
  - <ad> = <değer>
kod: |
  <kodun tamamı, değiştirilmeden>   (kod yoksa bu alanı boş bırak)
kurallar_alinti:
  - "<yazarın cümlesi, birebir>"   (kod yoksa)
eksik_kalan: <sayfada da olmayan ne varsa>
```

## Liste

### Parti 1

| ID | Strateji | TF | Kaynak |
|---|---|---|---|
| A1-018 | HYSTERIAN BIST:SISE TRADE ALGORITHM | 1D | https://tr.tradingview.com/script/DuPtf4A6 |
| A1-019 | BIST30 to S&P 500 ATR Momentum Rider | 1D | https://www.tradingview.com/script/jd1KSVn7/ |
| A1-022 | Slight Swing Momentum Strategy | 1D | https://it.tradingview.com/script/6l9kcw7j |
| A3-008c | stratestic Momentum(30) | 1D | https://github.com/diogomatoschaves/stratestic |
| A4-007 | Enhanced Short-Term Mean Reversion Algorithm | 1D | https://www.quantconnect.com/forum/discussion/3327/enhanced-short-term-mean-reversion-algorithm/p1 |
| B3-009 | Connors/Alvarez 2009 basit ortalamaya donus (ES+TY) | 1D | https://algotr.substack.com/p/this-simple-2009-strategy-still-wins |
| B3-015 | Is there 1 Strategy that just works? (gunluk long-only ETF betigi) | 1D | https://wl6.wealth-lab.com/Forum/Posts/Is-there-1-Strategy-that-just-works-28865 |
| G004 | TIS BTC Momentum + Confluencia | 4H | https://www.tradingview.com/script/k9nauxnv-TIS-BTC-ESTRATEGIA-Momentum-Confluencia/ |
| G005 | XLP Mean Reversion w/ Twist | 1D | https://www.wealth-lab.com/Strategy/DesignPublished?strategyID=78 |
| M018 | TradingView Script LHKOdUOs | 1D | https://www.tradingview.com/script/LHKOdUOs/ |
| M020b | The 30-Minute Stock Trader - Strategy 2: Mean-Reversion Long (Laurens Bensdorp) | 1D | https://www.turingtrader.com/2020/01/30-minute-stock-trader/ |
| M043 | Volatility Regime Momentum | 1D | https://github.com/erhungn/volatility-regime-momentum |
| M045 | Optimized Heikin Ashi Strategy with Buy/Sell Options | 1H | https://www.tradingview.com/script/f4SEwIH3-Optimized-Heikin-Ashi-Strategy-with-Buy-Sell-Options/ |
| M046 | ELLIPSE Bidirectional Swing Trading Strategy | 4H | https://www.tradingview.com/script/O6E7WhRC-ELLIPSE-Bidirectional-Swing-Trading-Strategy-Strategy-Version/ |
| M048 | 3Commas Turtle Strategy (ETHUSDT H4) | 4H | https://www.tradingview.com/script/9qFCuXqF-3Commas-Turtle-Strategy/ |
| M049 | BTC RSI Strategy 3Commas | 4H | https://www.tradingview.com/script/eZsaqsZY-BTC-RSI-Strategy-3Commas/ |
| M051 | MeanReversionRSI (Jesse.Trade) | 1H | https://jesse.trade/strategies/meanreversionrsi |
| O2-018 | MACD + EMA | 1H | https://jesse.trade/strategies/macd-ema |
| P3-006 | [STRATEGY][UL]Price Divergence Strategy v1.0 | 1D | https://www.tradingview.com/script/IDoY5LgE-STRATEGY-UL-Price-Divergence-Strategy-v1-0/ |
| P3-009 | Delta-RSI Strategy (with filters) | 1D | https://www.tradingview.com/script/0OdCms2T-Delta-RSI-Strategy-with-filters/ |

### Parti 2

| ID | Strateji | TF | Kaynak |
|---|---|---|---|
| P3-015 | Davin's 10/200MA Pullback on SPY Strategy v2.0 | 1D | https://www.tradingview.com/script/Gkib6KgL-Davin-s-10-200MA-Pullback-on-SPY-Strategy-v2-0/ |
| P3-016 | 2-Period RSI strategy (with filter) | 1D | https://www.tradingview.com/script/iHSFQFog/ |
| P3-017 | Kirk65 UTBot Strategy Fixed | 1H | https://www.tradingview.com/script/cbPurhXs-Kirk65-UTBot-Strategy-Fixed/ |
| P3-019 | EMA Cross Strategy | 1D | https://www.tradingview.com/script/fAxX6kbm-EMA-Cross-Strategy/ |
| P3-020 | RSI Strategy [PrimeAutomation] | 1D | https://www.tradingview.com/script/RiQzLLoh-RSI-Strategy-PrimeAutomation/ |
| O1-029 | Grover Llorens Activator Strategy Analysis | 1D | https://www.tradingview.com/script/VuYM89Tw-Grover-Llorens-Activator-Strategy-An |
| O1-030 | Uhl MA System - Strategy Analysis | 1D | https://www.tradingview.com/script/4S9Yz3DB-Uhl-MA-System-Strategy-Analysis/ |
| O1-042 | Smoothed Bollinger% Strategy Daily | 1D | https://www.prorealcode.com/prorealtime-trading-strategies/smoothed-bollinger-strategy-daily/ |
| O1-068 | MACD Cross Over | 1D | https://ninjatraderecosystem.com/user-app-share-download/macd-cross-over/ |
| O1-071 | Adx Breakouts Strategy | 1D | https://ninjatraderecosystem.com/user-app-share-download/adx-breakouts-strategy-2/ |
| O1-074 | Camarillapoints ATS | 1D | https://ninjatraderecosystem.com/user-app-share-download/camarillapoints-ats/ |
| O1-076 | Mean Reversion Swing Trading Strategy | 1D | https://ninjatraderecosystem.com/user-app-share-download/mean-reversion-swing-trading-strategy-2/ |
| M007 | ForexFactory Post 8694795 Swing Strategy | 1D | https://www.forexfactory.com/thread/post/8694795 |
| M054 | NexusFi Thread 58030 Post 858460 Strategy | 1D | https://nexusfi.com/showthread.php?p=858460&t=58030 |
| A5-013 | Trading Volume Effects of Moving Average Heuristics | 1D | https://paperswithbacktest.com/strategies/trading-volume-effects-of-moving-average-heuristics |
| A5-015 | Reversal in Cryptocurrency Returns | 1W | https://paperswithbacktest.com/strategies/reversal-in-cryptocurrency-returns |
| A5-022 | Trend-based Forecast of Cryptocurrency Returns | 1D | https://paperswithbacktest.com/strategies/trend-based-forecast-of-cryptocurrency-returns |
| M035 | Breakout Trading Strategy (Experiments Summary 2025) | 1H | https://github.com/SokeWang/Breakout-Trading-Strategy/blob/main/strategies/breakout/reports/experiments_summary_2025.md |
| M044 | Chart Pattern Backtester (43 Crypto Pairs H4) | 4H | https://github.com/juriok/chart-pattern-backtester |
| M056 | FreqtradeHyperOpt (RSI / MACD / EMA Strategies) | 1H | https://github.com/ErikKerkvliet/FreqtradeHyperOpt |
## Sonra
Lider her "bulundu" sonucunu kaynak adresinden örnekleyerek doğrular; doğrulananlar Sonnet'e çeviri için gider ve U7'ye eklenir (DSR toplam N'ye sayılır). Parti 1'den 5'ten az strateji kurtulursa iş durdurulur.
