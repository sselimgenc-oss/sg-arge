# Argon görev paketi: T2 parti 8 (40 strateji)

Bu mesajı olduğu gibi Argon'a yapıştır. **Dosya adı önemli:** cevabı kaydederken adını `T2_parti8.yaml` yap (Gemini'nin verdiği otomatik adı değiştir). Cevabı `argon/T2_parti8.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_parti8`).

---

Sen çok modelli bir algo trading araştırma ekibinin **kart çıkarıcısısın** (rol adı: Argon). Takım lideri Claude Opus. Çıktını lider denetleyecek.

**Proje amacı:** Yüzlerce yayımlanmış trading stratejisini ortak kurallarla backtest edip başarılı/başarısız listesi çıkarmak. Senin işin her stratejinin kurallarını kaynağından okuyup makinece okunur YAML karta çevirmek.

## Geri bildirim (lider, parti 2-4 ve yeniden okumalardan)
Parti 4 ve yeniden okumalar iyiydi: kodu okuyorsun, durum sırası doğru. Ek olarak: ifade dilinde `a ? b : c` yok, `(k and b) or (not k and c)` yaz; zaman dilimleri yalnız şu biçimde: dakika küçük `m` (`1m`, `5m`, `15m`, `30m`), saat/gün/hafta büyük harf (`1H`, `4H`, `1D`, `1W`); `1h` ya da `M15` yazma; `mtf("1W", x)` tırnaklı. **Yer tutucu ifade yazma:** kuralı bilmiyorsan `close < close[1]` gibi uydurma ifade koyma; `giris: null` / `cikis: null` bırak ve `belirsiz`'e yaz. `cikis: 'false'` gibi metin de yazma, `null` kullan.

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
ozet: {paket: T2_parti8, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, ihtiyari: n, sadece_short: n, okunamayan_url: [ID, ...]}
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
- **B3-003** | GBPUSD Forex Strategy (Python Code Included) | https://quantifiedstrategies.substack.com/p/gbpusd-forex-strategy-python-code
- **B3-004** | Trend Following and Mean Reversion Strategy - Combined (QQQ) | https://quantifiedstrategies.substack.com/p/trend-following-and-mean-reversion
- **B3-005** | Triple RSI Strategy (90.36% win rate) | https://quantifiedstrategies.substack.com/p/triple-rsi-strategy-9036-win-rate-2c5
- **B3-009** | Connors/Alvarez 2009 basit ortalamaya dönüş (ES+TY) | https://algotr.substack.com/p/this-simple-2009-strategy-still-wins
- **B3-014** | Cross-Sectional Equity Mean Reversion (Quantpedia #13) | https://quantpedia.com/quantopian-quantpedia-trading-strategy-series-cross-sectional-equity-mean-rever/
- **B3-015** | Is there 1 Strategy that just works? (günlük long-only ETF betiği) | https://wl6.wealth-lab.com/Forum/Posts/Is-there-1-Strategy-that-just-works-28865
- **O1-015** | Algoritmik Trade Sistem Sinyalleri ve Gerçek Hesap Paylaşımlı (Şeffaf) – klasik trend sistemi | https://www.hisse.net/topluluk/threads/31870
- **O1-016** | Sistem 1 (piyasa şartlarına göre şekillenen sistem) | https://www.bilgeyatirimci.com/i/sistem-tester-performans-testi-back-test-yaparken-nelere-dikkat-etmeliyiz/
- **O1-018** | MACD/RSI/MA/DEMA sistemi (VİOP örnekleri) | https://en.geisttrading.com/viop3
- **O2-013** | NoPain MT5 | https://www.mql5.com/en/signals/2262642
- **O2-014** | MSC Gold Stable Pro | https://www.mql5.com/en/signals/2231030
- **O2-015** | FXtrading | https://www.mql5.com/en/signals/2356441
- **O2-016** | World PEACE Multi FX Algo | https://www.mql5.com/en/signals/2379208
- **O2-024** | BeatTheMarketMomentum (SPY intraday momentum, embedded backtest) | https://www.quantconnect.com/terminal/cache/embedded_backtest_fd22e7bd368af4d6bd31153c9f8c4dad.html
- **O3-001** | Monday reversal in the S&P 500 (10 Best Swing #1) | https://www.quantifiedstrategies.com/swing-trading-strategies/
- **O3-002** | Overnight swing strategy in the S&P 500 (10 Best Swing #2) | https://www.quantifiedstrategies.com/swing-trading-strategies/
- **O3-003** | Buy when S&P 500 makes new intraday high (10 Best Swing #3) | https://www.quantifiedstrategies.com/swing-trading-strategies/
- **O3-004** | Monday/Tuesday trade in Nasdaq (10 Best Swing #4) | https://www.quantifiedstrategies.com/swing-trading-strategies/
- **O3-006** | MACD-Histogram on the S&P 500 (10 Best Swing #8) | https://www.quantifiedstrategies.com/swing-trading-strategies/
- **O3-008** | Day trading strategy #78 (SPY, açılış→kapanış) | https://www.quantifiedstrategies.com/day-trading-strategies/
- **O3-010** | Opening Range Breakout – QS gizli varyant (S&P 500) | https://www.quantifiedstrategies.com/opening-range-breakout-strategy/
- **O3-011** | 5-Day Low of the Range (IBS<0.25) – S&P 500 | https://www.quantifiedstrategies.com/5-day-low-of-the-range-strategy/
- **O3-017** | RSI SPY trading strategy (RSI(2) on SPY) | https://www.quantifiedstrategies.com/rsi2-on-spy/
- **O3-019** | Hisse swing stratejisi (açıklanmamış, %96 kazanma) | https://reddit.sentinel-team.org/posts/1sctlkd/snapshots/2026-04-06T18%3A02%3A16.13595Z
- **O3-020** | 1 dk long-only gün içi strateji (1:1 RR) | https://lr.sudovanilla.org/r/Daytrading/comments/1f6w20d/it_looks_good_enough
- **O3-021** | TS Trend Strategy – DAX 5 dk long-only | https://nexusfi.com/showthread.php?t=55903
- **O3-024** | NQ long/short otomatik trend stratejisi | https://www.elitetrader.com/et/threads/nq-short-and-long-automated-strategy.372986/
- **O3-026** | Bollinger Bands + RSI tick chart (ninZa) – PF 1.5–1.86 | https://elitetrader.com/et/threads/bollinger-bands-rsi-tick-chart-backtests-reached-pfs-as-high-as-1-86.390009/
- **P3-021** | NQ Alpha Engine | https://collective2.eu/details/154954998
- **P3-022** | HTP Momentum2 MNQ1 | https://collective2.eu/details/157216142
- **P3-023** | ares | https://collective2.eu/grid
- **P3-024** | Calicut Commodities | https://collective2.eu/grid
- **P3-025** | Easy Value | https://collective2.eu/grid
- **P3-026** | Adaptive Investments | https://collective2.eu/grid
- **P3-027** | Iberia Capital Strategy | https://collective2.eu/grid
- **P3-028** | US Stock Momentum | https://collective2.eu/grid
- **P3-029** | Quant AI SP500 | https://collective2.eu/grid
- **P3-030** | AIB STOCKS and FUT | https://collective2.eu/grid
- **P3-031** | AEA Algo MES | https://collective2.eu/grid
- **P3-032** | SQT Stocks Long Portfolio 2x | https://collective2.eu/grid
