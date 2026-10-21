# Argon görev paketi: T2 parti 7 (40 strateji)

Bu mesajı olduğu gibi Argon'a yapıştır. **Dosya adı önemli:** cevabı kaydederken adını `T2_parti7.yaml` yap (Gemini'nin verdiği otomatik adı değiştir). Cevabı `argon/T2_parti7.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_parti7`).

---

Sen çok modelli bir algo trading araştırma ekibinin **kart çıkarıcısısın** (rol adı: Argon). Takım lideri Claude Opus. Çıktını lider denetleyecek.

**Proje amacı:** Yüzlerce yayımlanmış trading stratejisini ortak kurallarla backtest edip başarılı/başarısız listesi çıkarmak. Senin işin her stratejinin kurallarını kaynağından okuyup makinece okunur YAML karta çevirmek.

## Geri bildirim (lider, parti 2-4 ve yeniden okumalardan)
Parti 4 ve yeniden okumalar iyiydi: kodu okuyorsun, durum sırası doğru. Ek olarak: ifade dilinde `a ? b : c` yok, `(k and b) or (not k and c)` yaz; zaman dilimleri yalnız şu biçimde: dakika küçük `m` (`1m`, `5m`, `15m`, `30m`), saat/gün/hafta büyük harf (`1H`, `4H`, `1D`, `1W`); `1h` ya da `M15` yazma; `mtf("1W", x)` tırnaklı.

### Önceki kurallar
Parti 2 kabul edildi, kaynak okuman iyiydi. Düzeltilmesi gerekenler:
1. **Kod varsa kodu oku.** MQL5 sayfalarında kaynak kod "View code"/.mq5 olarak açık; varsayılan parametreleri (`input` satırları) koddan al. "Açıklamada yazmıyor, .mq5 içinde" diye bırakma.
2. **`spec_durumu` öncelik sırası:** `gizli` > `ihtiyari` > `sadece_short` > `eksik` > `dakikalik` > `tam`. Yani giriş/çıkış ya da parametre eksikse 1H altı olsa bile `eksik`. `dakikalik` yalnız kuralı tam olan 1H altı stratejiler için.
3. **Yeni durumlar:** `ihtiyari` = kurallar yoruma dayalı (göz kararı formasyon, destek/direnç çizme), mekanik test edilemez. `sadece_short` = long kuralı yok.
4. Giriş kuralı ifade diliyle yazılamıyorsa `giris: null` bırakma: `ozel_kod: true` yap ve mantığı `belirsiz`e adım adım, parametreleriyle yaz.
5. TradingView okunamazsa ayna dene: Scribd, TradeSearcher, GitHub'da aynı script adı, yazarın blogu. Bulduysan kaynağını `belirsiz`e yaz.
6. Kaynak okunamadıysa `erisim_engeli: true` ekle.

## Çıktı biçimi
**Tek bir YAML dosyası**, kartlar `---` ile ayrılır, başka açıklama yazma. Her karta `kart_yazari: argon` ekle. En sona:
```yaml
---
ozet: {paket: T2_parti7, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, ihtiyari: n, sadece_short: n, okunamayan_url: [ID, ...]}
```

## D. Strateji kartı şeması (`docs/spec/<id>.yaml`)
```yaml
id: A3-002            # xlsx ID veya KATALOG id
ad: ...
kaynak: {dosya: "strateji_listesi (2).xlsx", url: ..., sayfa: null}
tarz: day | swing
tf: 1D                # karar zaman dilimi
mtf: 1W               # varsa üst zaman dilimi, yoksa null
tf_varsayim: false
yazar_piyasasi: Forex
gostergeler:          # ortak kütüphaneden: sma, ema, wma, rsi, atr, adx, dmi, cci, macd, bb, kc, donchian, stoch, obv, mfi, vwap, kama, ichimoku, supertrend, roc, zscore, highest, lowest, ott, pmax, rvol, stdev, var, rrs, atr_ratio
  ema20: {f: ema, src: close, n: 20}
  rsi14: {f: rsi, src: close, n: 14}
giris: "cross_over(close, ema20) and rsi14 > 50"        # yalnız bu dil: karşılaştırma, and/or/not, cross_over/cross_under, [k] gecikme, mtf(...)
cikis: "close < ema50 or rsi14 < 40"
stop: {tip: atr, n: 14, carpan: 3}     # veya {tip: yuzde, deger: 2} veya null
hedef: null
stop_eklendi: false
parametreler: {ema20.n: 20}
deneme_sayisi_kaynakta: 1               # DSR için; bilinmiyorsa null
rapor: {pf: null, sharpe: null, getiri: null, mdd: null, islem: null, wr: null, maliyet_dahil: belirtilmemis}
spec_durumu: tam | eksik | gizli | dakikalik
belirsiz: ["çıkış kuralı yazmıyor"]
```
### D2. Şema ekleri (lider onaylı, T2 parti 1'den)
- Fiyat serileri gösterge olarak: `{f: close|open|high|low|volume, tf: 1W}`. `kaydir: k` = k bar gecikme.
- Ek çıkış alanları: `iz_suren: {tip: atr_zirve, n, carpan}`, `kar_kilidi`, `kismi_kar: {gun, tetik_atr, oran, kalan_stop}`, `zaman_stop: {bar}`, `cooldown_bar`, `varyantlar` (rapordaki ikinci kurgu; ana kart dışında ayrı test edilmez).
- `bias_varsayim: true`: üst zaman dilimi filtresinin formülü kaynakta yok, varsayıldı. **Lider kararı:** 1W yön filtresi tanımsızsa Paper_Test_4 S1 tanımı (1W EMA10 >= EMA20 veya 1W kapanış >= EMA20 × 0,985), 1D/4H filtresi tanımsızsa Supertrend(10; 2,5) yön = +1 kullanılır.
- Gösterge kütüphanesine eklenenler (`ozel_kod` gerektirmez, T5'te yazılacak): `ott`, `pmax`, `rvol`, `stdev`, `var` (VIDYA), `rrs` (göreceli güç), `atr_ratio`.
- `spec_durumu: tam`, `belirsiz` listesi yalnız yukarıdaki gibi açıkça yazılmış varsayımlar içeriyorsa kullanılabilir. Giriş ya da çıkış kuralı yoksa `eksik`.
- Kaynakta "kapanışta al" denmesi A1'i değiştirmez: emir sonraki açılışta.

Kural karta çevrilemiyorsa (ör. makine öğrenmesi, order flow, haber) → `spec_durumu: eksik` ve `belirsiz`'e neden yazılır; yorumlayıcıya özel kod gerekiyorsa `ozel_kod: true`.


## Görev
Aşağıdaki 40 strateji için kart çıkar. Bir satırda birden fazla strateji varsa ayrı kart (`ID` + a, b, c...). Şimdilik yalnız long kuralları; short kuralı varsa `belirsiz`e kısa not.

## Liste
- **A6-017** | Can Weakening Morning Order Flow Predict SPY Reversals? | https://quantpedia.com/can-weakening-morning-order-flow-predict-spy-reversals/
- **A6-019** | Overnight Seasonality in Bitcoin | https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin
- **A6-021** | Pairs Trading with Country ETFs | https://quantpedia.com/strategies/pairs-trading-with-country-etfs
- **A6-022** | How to Design a Simple Multi-Timeframe Trend Strategy on Bitcoin | https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin/
- **A6-023** | Attention Prop Traders: first half hour predicts last half hour | https://alphaarchitect.com/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/
- **A7-001** | NQ 5 dk trend-pullback scalp (37 strateji backtest'inden kalan) | https://www.elitetrader.com/et/threads/i-backtested-37-famous-strategies-with-fees-on-most-lose-mechanically-after-costs-data-one-that-didnt.390197/
- **A7-004** | S&P500-VIX diverjans stratejisi (Scherman, BI makalesi) | https://www.elitetrader.com/et/threads/strategy-with-75-win-ratio-and-3-to-1-profit-potential-count-me-as-a-skeptic.382581/
- **A7-007** | ES Renko/Donchian 21 pullback scalp (RichJamo günlüğü) | https://futures.io/trading-journals/33441-rich-s-es-s-p-500-futures-contract-intraday-strategy.html
- **O1-017** | Sistem 2: RSI ortalama kesişimi (VİOP30 5 dk, long) | https://www.bilgeyatirimci.com/i/sistem-tester-performans-testi-back-test-yaparken-nelere-dikkat-etmeliyiz/
- **O2-008** | Highest Open / Lowest Open Trade | https://www.forexfactory.com/thread/590623-highest-open-lowest-open-trade
- **O2-009** | M1 Countertrend Scalping Strategy | https://www.forexfactory.com/thread/1190104-m1-countertrend-scalping-strategy
- **O2-023** | Intraday Trading Strategy for Futures Contract NQ | https://www.quantconnect.com/forum/discussion/15192
- **O3-012** | MACD and RSI Strategy (73% win rate) | https://www.quantifiedstrategies.com/macd-and-rsi-strategy/
- **O3-013** | Turnaround Tuesday (SPY) | https://www.quantifiedstrategies.com/turnaround-tuesday-strategy/
- **O3-016** | Gap down + 25 MA filtresi (S&P 500 gün içi) | https://www.quantifiedstrategies.com/gap-trading-strategies/
- **O3-018** | VRT Levels – hacim tabanlı destek/direnç kırılım+reddi | https://reddit.com/r/algotrading/comments/1tbgqmn/my_strategy_outperformed_the_sp_500_over_3_years/
- **O3-022** | DAX Value Area günlük bias sistemi | https://nexusfi.com/showthread.php?t=44951
- **O3-023** | London Session ORB – GBP (mekanik kırılım günlüğü) | https://nexusfi.com/showthread.php?t=36245
- **O3-025** | Bollinger Prism – NQ reversal (PF 2.78) | https://www.elitetrader.com/et/threads/nq-reversal-strategy-backtest-reached-profit-factor-2-78.389985/
- **O3-027** | Mean Reversion Strategy Journal – Buy Sell Bands (ABD hisseleri) | https://elitetrader.com/et/threads/mean-reversion-strategy-journal.363044/
- **O3-030** | 75%+ win rate trend stratejisi (Jim Brown kitabından) – EURUSD | https://www.tradingheroes.com/75-win-rate-trading-strategy/
- **O3-031** | RSI Divergence swing – 27 parite günlük | https://www.tradingheroes.com/rsi-strategy-for-swing-trading/
- **O3-032** | RSI50 stratejisi – EURUSD günlük | https://www.tradingheroes.com/rsi-trading-strategy-results/
- **O3-033** | RSIDive (RSI uyumsuzluğu) – EURUSD günlük | https://www.tradingheroes.com/rsi-trading-strategy-results/
- **O3-034** | Trending Pin Bar v2 – EURUSD H4 | https://www.tradingheroes.com/backtesting-results-tpb-eurusd-h4/
- **A1-018** | HYSTERIAN BIST:SISE TRADE ALGORITHM | https://tr.tradingview.com/script/DuPtf4A6
- **A5-012** | Self-Imposed Limits to Arbitrage | https://paperswithbacktest.com/strategies/self-imposed-limits-to-arbitrage
- **A5-013** | Trading Volume Effects of Moving Average Heuristics | https://paperswithbacktest.com/strategies/trading-volume-effects-of-moving-average-heuristics
- **A5-014** | Seasonality, Trend-following, and Mean reversion in Bitcoin | https://paperswithbacktest.com/strategies/seasonality-trend-following-and-mean-reversion-in-bitcoin
- **A5-016** | Stock Market Predictability in the MENA: Evidence from New Variance Ratio Tests and Technical Trade Analysis | https://paperswithbacktest.com/strategies/stock-market-predictability-in-the-mena-evidence-from-new-variance-ratio-tests-and-technical-trade-analysis
- **A5-020** | Finding Consistent Trends with Strong Momentum – RSI for Trend-Following and Momentum Strategies | https://paperswithbacktest.com/strategies/finding-consistent-trends-with-strong-momentum-rsi-for-trend-following-and-momentum-strategies
- **A5-022** | Trend-based Forecast of Cryptocurrency Returns | https://paperswithbacktest.com/strategies/trend-based-forecast-of-cryptocurrency-returns
- **A5-023** | Signal Prediction in cryptocurrency tradeoperations: a machine learning-based approach | https://paperswithbacktest.com/strategies/signal-prediction-in-cryptocurrency-tradeoperations-a-machine-learning-based-approach
- **A5-024** | Impact of Earnings Announcements for Dow Jones Index Stocks | https://paperswithbacktest.com/strategies/impact-of-earnings-announcements-for-dow-jones-index-stocks
- **A6-020** | Market Sentiment and an Overnight Anomaly | https://quantpedia.com/strategies/market-sentiment-and-an-overnight-anomaly
- **A7-002** | RSI aşırı alım/satım Forex sistemi (PF 2.41) | https://www.elitetrader.com/et/threads/improved-trading-strategy-results-profit-factor-increased-to-2-41.382680/
- **A7-005** | Long-only ABD hisseleri dakikalık gün içi (Level4) | https://www.elitetrader.com/et/threads/analyzing-backtesting-results.387769/
- **A7-006** | Kripto 50 parite long-only gösterge tarayıcı sistemi | https://www.elitetrader.com/et/threads/automated-trading-feedback.382851/
- **B3-001** | RSI Mean Reversion Trading Strategy in Nasdaq100 (QQQ) | https://quantifiedstrategies.substack.com/p/rsi-mean-reversion-trading-strategy
- **B3-002** | RSI Pullback Strategy (SPY) | https://quantifiedstrategies.substack.com/p/rsi-pullback-strategy
