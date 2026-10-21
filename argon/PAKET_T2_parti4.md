# Argon görev paketi: T2 parti 4 (40 strateji)

Bu mesajı olduğu gibi Argon'a yapıştır. Cevabı `argon/T2_parti4.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_parti4`).

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
Aşağıdaki 40 strateji için kart çıkar. Bir satırda birden fazla strateji varsa ayrı kart (`ID` + a, b, c...). Şimdilik yalnız long kuralları; short kuralı varsa `belirsiz`e kısa not.

## Liste
- **O1-036** | Gold ORB Strategy (15-min Range, 5-min Entry) | https://www.tradingview.com/script/oYW9gdag-Gold-ORB-Strategy-15-min-Range-5-min-Entry/
- **O1-037** | Simple and Profitable Scalping Strategy (ForexSignals TV) | https://www.tradingview.com/script/x4za4NFZ-Simple-and-Profitable-Scalping-Strategy-ForexSignals-TV/
- **O1-038** | KPL Swing Strategy | https://www.tradingview.com/script/4mz6xvnK/
- **O1-039** | Laguerre RSI by KivancOzbilgic STRATEGY | https://www.tradingview.com/script/vWG3tMJh-Laguerre-RSI-by-KivancOzbilgic-STRATEGY/
- **O1-040** | Pathfinder DAX 4H | https://www.prorealcode.com/prorealtime-trading-strategies/pathfinder-dax-4h/
- **O1-041** | Optimization moving average crossing strategy with 'machine learning' | https://www.prorealcode.com/prorealtime-trading-strategies/optimization-ma-cross-machine-learning/
- **O1-042** | Smoothed Bollinger% Strategy Daily | https://www.prorealcode.com/prorealtime-trading-strategies/smoothed-bollinger-strategy-daily/
- **O1-043** | Navigator DAX Trading Strategy 4H | https://www.prorealcode.com/prorealtime-trading-strategies/navigator-dax-trading-strategy-4h/
- **O1-044** | ALEX AutoTradingBot INDEX | https://www.prorealcode.com/prorealtime-trading-strategies/alex-autotradingbot-index/
- **O1-045** | VECTORIAL DAX (M5) | https://www.prorealcode.com/prorealtime-trading-strategies/vectorial-dax-m5/
- **O1-046** | Fractal breakout intraday Strategy EUR/USD 1H | https://www.prorealcode.com/prorealtime-trading-strategies/fractal-breakout-intraday-strategy-eurusd-1h/
- **O1-047** | Kama & Sma Trading System DAX mtf | https://www.prorealcode.com/prorealtime-trading-strategies/kama-sma-trading-system-dax-mtf/
- **O1-048** | Stochastic Gold Trader | https://www.prorealcode.com/prorealtime-trading-strategies/stochastic-gold-trader/
- **O1-049** | Oil 10min 'hammernegated' pattern strategy | https://www.prorealcode.com/prorealtime-trading-strategies/oil-10min-hammernegated-pattern-strategy/
- **O1-050** | EURUSD 15-minutes timeframe Dhigh / Dlow Strategy | https://www.prorealcode.com/prorealtime-trading-strategies/eurusd-15-minutes-timeframe-dhigh-dlow-strategy/
- **O1-051** | Brent Oil 5 minutes trading strategy | https://www.prorealcode.com/prorealtime-trading-strategies/brent-oil-5-minutes-trading-strategy/
- **O1-052** | Wing's Resistance Breacher (DAX-30m) | https://www.prorealcode.com/prorealtime-trading-strategies/wings-resistance-breacher-dax-30m/
- **O1-053** | Open Range Breakout DAX 5/15M | https://www.prorealcode.com/prorealtime-trading-strategies/open-range-breakout-dax-515m/
- **O1-054** | End Of Day – YEN M15 | https://www.prorealcode.com/prorealtime-trading-strategies/end-of-day-yen-m15/
- **O1-055** | Intraday Profit Maker (Best with Automation) | https://www.wisestocktrader.com/indicators/4853-intraday-profit-maker-best-with-automation-for-amibroker-afl
- **O1-056** | Intraday Stochastic Trading System | https://www.wisestocktrader.com/indicators/5858-intraday-stochastic-trading-system-for-amibroker-afl
- **O1-058** | /ES Futures Trading Strategy on ThinkorSwim | https://usethinkscript.com/threads/es-futures-trading-strategy-on-thinkorswim.987/
- **O1-059** | Relative Volume Strategy and Momentum Scanner | https://usethinkscript.com/threads/relative-volume-strategy-and-momentum-scanner-for-thinkorswim.3002/
- **O1-060** | Strategy Based on EMAs, TSI, MACD, and Premarket Highs/Lows | https://usethinkscript.com/threads/strategy-based-on-emas-tsi-macd-and-premarket-highs-lows-for-thinkorswim.10866/
- **O1-061** | Chewie's Super Trend, Hull Average, Donchian Trend Ribbon Trading System | https://usethinkscript.com/threads/chewies-super-trend-hull-average-donchian-trend-ribbon-trading-system-for-thinkorswim.10894/
- **O1-062** | High and Low Reversals Indicator + Intraday Strategy | https://usethinkscript.com/threads/high-and-low-reversals-indicator-intraday-strategy-for-thinkorswim.49/
- **O1-063** | Renko Bar Based Trading System | https://usethinkscript.com/threads/renko-bar-based-trading-system-for-thinkorswim.3252/
- **O1-064** | Try this NQ Strategy + Code | https://usethinkscript.com/threads/try-this-nq-strategy-code-for-thinkorswim.1958/
- **O1-065** | Camarilla Pivot Points Day Trading System | https://usethinkscript.com/threads/camarilla-pivot-points-day-trading-system-for-thinkorswim.12988/
- **O1-066** | Accumulation/Distribution Range Breakout Strategy NT8 - August 2018 S&C | https://ninjatraderecosystem.com/user-app-share-download/accumulation-distribution-range-breakout-strategy/
- **O1-067** | Renko Trading Strategy NT8 - December 2019 S&C | https://ninjatraderecosystem.com/user-app-share-download/renko-trading-strategy-nt8/
- **O1-068** | MACD Cross Over | https://ninjatraderecosystem.com/user-app-share-download/macd-cross-over/
- **O1-069** | Woodies CCI Autotrader | https://ninjatraderecosystem.com/user-app-share-download/woodies-cci-autotrader-2/
- **O1-070** | Divergencesystem Strategy | https://ninjatraderecosystem.com/user-app-share-download/divergencesystem-strategy-2/
- **O1-071** | Adx Breakouts Strategy | https://ninjatraderecosystem.com/user-app-share-download/adx-breakouts-strategy-2/
- **O1-072** | Automated Strategy for trading NQ | https://ninjatraderecosystem.com/user-app-share-download/automated-strategy-for-trading-nq/
- **O1-073** | LargeTrades Strategy NT8 | https://ninjatraderecosystem.com/user-app-share-download/largetrades-strategy-nt8/
- **O1-074** | Camarillapoints ATS | https://ninjatraderecosystem.com/user-app-share-download/camarillapoints-ats/
- **O1-075** | MeanReversal Strategy NT8 | https://ninjatraderecosystem.com/user-app-share-download/meanreversal-strategy-nt8/
- **O1-076** | Mean Reversion Swing Trading Strategy | https://ninjatraderecosystem.com/user-app-share-download/mean-reversion-swing-trading-strategy-2/
