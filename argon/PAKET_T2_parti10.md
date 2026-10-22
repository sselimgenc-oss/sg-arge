# Argon görev paketi: T2 parti 10 

Bu mesajı olduğu gibi Argon'a yapıştır. **Dosya adı önemli:** cevabı kaydederken adını `T2_parti10.yaml` yap (Gemini'nin verdiği otomatik adı değiştir). Cevabı `argon/T2_parti10.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_parti10`).

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
ozet: {paket: T2_parti10, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, ihtiyari: n, sadece_short: n, okunamayan_url: [ID, ...]}
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
Aşağıdaki stratejiler için kart çıkar. Bir satırda birden fazla strateji varsa ayrı kart (`ID` + a, b, c...). Şimdilik yalnız long kuralları; short kuralı varsa `belirsiz`e kısa not.


**Not:** Bu partideki ID'ler `M` ile başlar (Markdown listelerinden). Ad sütunu listedeki kısa açıklamadır; gerçek strateji adını kaynaktan al.

## Liste
- **M001** | SPX/SPY 0DTE; ilk 60 dakikanın üst kırılımında short put spread, alt kırılımında short cal | https://optionalpha.com/blog/opening-range-breakout-0dte-options-trading-strategy-explained
- **M002** | SPY; 1 dakikalık veriden 1 puanlık Kase bar; $200 hedef/stop, 100 hisse | https://cdn.tradestation.com/uploads/Key-Reversal-Patterns-Using-Kase-Bars.pdf
- **M003** | ES; 5 dk; HalfTrend ve deviation-band yön/sinyal mantığı; tam thinkScript paylaşılmış | https://usethinkscript.com/threads/5min-es-futures-strategy-for-thinkorswim.9911/
- **M004** | SPY; 1 dk veri, yarım saatte karar, EOD flat; 14 günlük saat-eşlemeli hareket bandı ve VWA | https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf
- **M005** | ES/NQ; Noise Area ailesi; 90 günlük bakış, %3 vol hedefi, azami 8x kaldıraç, kapanışta fla | https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq
- **M006** | Swing | https://www.wisestocktrader.com/indicators/371-rsi-double-bottom-for-amibroker-afl
- **M007** | Swing | https://www.forexfactory.com/thread/post/8694795
- **M008** | Swing | https://alvarezquanttrading.com/blog/rsi2-strategy-double-returns-with-a-simple-rule-change/
- **M009** | Swing | https://optionalpha.com/blog/spy-put-credit-spread-backtest
- **M010** | Swing | https://cdn.tradestation.com/uploads/RSI-Volatility-Spread.pdf
- **M011** | Swing | https://tradingstrategy.ai/docs/programming/old-strategies/double-7.html
- **M012** | Swing | https://quantifiedstrategies.substack.com/p/5-swing-trading-strategies-for-beginners
- **M013** | 830795-simple-h4-mobile-trading-system | https://www.forexfactory.com/thread/830795-simple-h4-mobile-trading-system
- **M014** | larry-connors-2-day-rsi-holy-grail-adapting-a-strategy-to-deliver-30-annual-return-since-1999.379926 | https://www.elitetrader.com/et/threads/larry-connors-2-day-rsi-holy-grail-adapting-a-strategy-to-deliver-30-annual-return-since-1999.379926/
- **M015** | larry-connors-cumulative-rsi-26-annual-return-now-with-sensitivity-analysis.379982 | https://www.elitetrader.com/et/threads/larry-connors-cumulative-rsi-26-annual-return-now-with-sensitivity-analysis.379982/
- **M016** | 8011 | https://www.wealth-lab.com/Discussion/8011
- **M017** | rsi-2-portfolio-dszxqiwmqcc8lxiliusf | https://www.composer.trade/trading-strategies/rsi-2-portfolio-DszXqIWmqcC8lxiliUsf
- **M018** | lhkoduos | https://www.tradingview.com/script/LHKOdUOs/
- **M019** | 3565-fullstochastic-with-filters-buy-sell-for-amibroker-afl | https://www.wisestocktrader.com/indicators/3565-fullstochastic-with-filters-buy-sell-for-amibroker-afl
- **M020** | 30-minute-stock-trader | https://www.turingtrader.com/2020/01/30-minute-stock-trader/
- **M021** | En büyük 10 ABD hissesi; birkaç dakikalık barlar | https://www.quantconnect.com/research/17900/intraday-application-of-hidden-markov-models/
- **M022** | DAX; 5 dk; 09:00-17:30 | https://www.prorealcode.com/prorealtime-trading-strategies/quadrant-strategy/
- **M023** | DAX; 5 dk; azami 145 dk tutuş | https://www.prorealcode.com/wp-content/uploads/2017/04/Quadrant-2.0-DAX-5-min.itf
- **M024** | EURUSD; M1; day trade | https://www.mql5.com/en/code/8688
- **M025** | EURUSD; M5 | https://www.mql5.com/en/code/8970
- **M026** | GBPUSD; H1 (M30-H2 öneriliyor) | https://www.mql5.com/en/code/126
- **M027** | DAX; 15 dk Renko; day trade | https://www.prorealcode.com/prorealtime-trading-strategies/renko-automated-trading-system/
- **M028** | BTC/kripto; 5 dk | https://www.tradingview.com/script/Qh7OYDvf/
- **M029** | HYPEUSDT perpetual; 15 dk | https://www.tradingview.com/script/8N8DT3Pv-Geometric-Grid-Machine-3Commas/
