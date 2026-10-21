# Argon görev paketi: T2 yeniden okuma 2 (parti 5, 36 kart)

Bu mesajı olduğu gibi Argon'a yapıştır. Cevabı `argon/T2_yeniden2.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_yeniden2`).

---

Sen çok modelli bir algo trading araştırma ekibinin **kart çıkarıcısısın** (rol adı: Argon). Takım lideri Claude Opus. Çıktını lider denetleyecek.

**Proje amacı:** Yüzlerce yayımlanmış trading stratejisini ortak kurallarla backtest edip başarılı/başarısız listesi çıkarmak. Senin işin her stratejinin kurallarını kaynağından okuyup makinece okunur YAML karta çevirmek.

## Parti 2 geri bildirimi (lider)
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
ozet: {paket: <ad>, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, ihtiyari: n, sadece_short: n, okunamayan_url: [ID, ...]}
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
Bu kartlar daha önce kaynak okunamadığı ya da eksik okunduğu için tamamlanamadı. Her birini kaynağından yeniden oku ve **tam kartı baştan yaz** (aynı ID). Sonnet'in ortamı algokutuphanesi.com, tradingview.com, quantconnect.com, github.com sitelerine erişemiyor; sen erişebiliyorsun. algokutuphanesi.com (Matriks) kartları BIST için özellikle önemli: formül/kodu birebir aktar.

## Liste
- **O1-077** | Automated Strategy StrategyPeakHoursTradingNQ | https://ninjatraderecosystem.com/user-app-share-download/automated-strategy-strategypeakhourstradingnq/
- **O1-078** | Atr Breakout | https://ninjatraderecosystem.com/user-app-share-download/atr-breakout-2/
- **O1-079** | Golden Triangle Strategy | https://ninjatraderecosystem.com/user-app-share-download/golden-triangle-strategy/
- **O2-001** | JP225 Opening Range Break Strategy | https://forex-station.com/jp225-opening-range-break-strategy-t8476395.html
- **O2-002** | JP225 ADR Extension-Based Momentum Model | https://forex-station.com/jp225-adr-extension-based-momentum-model-t8476400.html
- **O2-003** | XARD - Simple Trend Following Trading System | https://forex-station.com/xard-simple-trend-following-trading-system-t8416709.html
- **O2-004** | Trading Pullbacks System | https://forex-station.com/trading-pullbacks-system-t8474130.html
- **O2-005** | Trading Made Simple | https://www.forexfactory.com/thread/291622-trading-made-simple
- **O2-006** | Pivot Trading | https://www.forexfactory.com/thread/588764-pivot-trading
- **O2-007** | Another simple system - Time-Frame 15 | https://www.forexfactory.com/thread/345586-another-simple-system-time-frame-15
- **O2-010** | JPN225 QuietDrift (The Nikkei EA That Only Buys When Volume Is Quiet) | https://www.mql5.com/en/code/78027
- **O2-011** | PulseStrike Scalper - Statistical Burst Detection EA | https://www.mql5.com/en/code/77167
- **O2-017** | TemaTrendFollowing | https://jesse.trade/strategies/tematrendfollowing
- **O2-018** | MACD + EMA | https://jesse.trade/strategies/macd-ema
- **O2-019** | CloudScalper | https://jesse.trade/strategies/cloudscalper
- **O2-021a** | Jesse: Simple Bollinger Bands Strategy | https://jesse.trade/strategies
- **O2-021b** | Jesse: RSI Trend | https://jesse.trade/strategies
- **O2-021c** | Jesse: IchimokuCloud | https://jesse.trade/strategies
- **O2-025** | The Holy Grail | https://www.composer.trade/trading-strategies/the-holy-grail-MmQbpf2U5TMQFmr9Nt2e
- **O2-026** | KMLM Switcher of Simon97 - Original | https://www.composer.trade/trading-strategies/kmlm-switcher-of-simon97-original-syMn9OgFREE0wo8LtYsG
- **O2-027** | TQQQ For The Long Term (Reddit Post Link) | https://www.composer.trade/trading-strategies/tqqq-for-the-long-term-reddit-post-link-HukRwDJLlYPLMbrQbua5
- **O2-028** | SVIX/XXXX KMLM switcher (single pops) | BT 12/19/23 = 786/10.5 | https://www.composer.trade/trading-strategies/svixxxxx-kmlm-switcher-single-pops-bt-121923-786105-D9oE44Y87boHDOYQ9rPm
- **P3-001** | SuperTrend STRATEGY | https://www.tradingview.com/script/P5Gu6F8k/
- **P3-002** | BUY and SELL - Backtest single EMA cross By che_trader | https://www.tradingview.com/script/j9rq1wQq-BUY-and-SELL-Backtest-single-EMA-cross-By-che-trader/
- **P3-003** | UT Bot Strategy | https://www.tradingview.com/script/VKMgZdYr-UT-Bot-Strategy/
- **P3-004** | EMA Slope + EMA Cross Strategy (by ChartArt) | https://www.tradingview.com/script/XLGBqrZq-EMA-Slope-EMA-Cross-Strategy-by-ChartArt/
- **P3-005** | UT Bot Strategy with Backtesting Range [QuantNomad] | https://www.tradingview.com/script/RHagaXIp-UT-Bot-Strategy-with-Backtesting-Range-QuantNomad/
- **P3-006** | [STRATEGY][UL]Price Divergence Strategy v1.0 | https://www.tradingview.com/script/IDoY5LgE-STRATEGY-UL-Price-Divergence-Strategy-v1-0/
- **P3-007** | Heikin Ashi Supertrend | https://www.tradingview.com/script/9z16eauD-Heikin-Ashi-Supertrend/
- **P3-008** | Strategy based on Squeeze Momentum Indicator [LazyBear] | https://www.tradingview.com/script/qp9BoNyS-Strategy-based-on-Squeeze-Momentum-Indicator-LazyBear/
- **P3-009** | Delta-RSI Strategy (with filters) | https://www.tradingview.com/script/0OdCms2T-Delta-RSI-Strategy-with-filters/
- **P3-010** | Dynamic Swing Anchored VWAP STRAT (Zeiierman/PineIndicators) | https://www.tradingview.com/script/gjFSGRCo-Dynamic-Swing-Anchored-VWAP-STRAT-Zeiierman-PineIndicators/
- **P3-011** | MACD Strategy with trailing ATR stop | https://www.tradingview.com/script/2jDHQAJc-MACD-Strategy-with-trailing-ATR-stop/
- **P3-013** | ORB Strategy [LuciTech] | https://www.tradingview.com/script/10yYqaY7-ORB-Strategy-LuciTech/
- **P3-014** | EmperorBTC's VWAP Strategy | https://www.tradingview.com/script/wmJ1ovZQ-EmperorBTC-s-VWAP-Strategy/
- **P3-015** | Davin's 10/200MA Pullback on SPY Strategy v2.0 | https://www.tradingview.com/script/Gkib6KgL-Davin-s-10-200MA-Pullback-on-SPY-Strategy-v2-0/
