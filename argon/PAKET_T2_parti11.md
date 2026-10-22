# Argon görev paketi: T2 parti 11 

Bu mesajı olduğu gibi Argon'a yapıştır. **Dosya adı önemli:** cevabı kaydederken adını `T2_parti11.yaml` yap (Gemini'nin verdiği otomatik adı değiştir). Cevabı `argon/T2_parti11.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_parti11`).

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
ozet: {paket: T2_parti11, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, ihtiyari: n, sadece_short: n, okunamayan_url: [ID, ...]}
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
- **M030** | BNB; kısa zamanlı grid | https://www.tradingview.com/script/9pHwOZsM-BNB-Grid-Bot-Long-Strategy/
- **M031** | ADAUSDT spot; 3 dk | https://www.tradingview.com/script/XbtQXDMb-3Commas-Pullback-Sniper-Strategy/
- **M032** | XAUTUSDT tokenleştirilmiş altın spot; 15 dk; grid/swing | https://www.tradingview.com/script/bjoh9PTd-XAU-Grid-Bot-Long-Strategy/
- **M033** | BTC; çoklu zaman; gün içi/swing geçişi | https://www.tradingview.com/script/QMvHkvdQ-SMC-Pro-BTC-ICT-Order-Blocks-FVG-DOE/
- **M034** | ES/NQ futures; M15 RTH; EOD flat | https://www.reddit.com/r/algotrading/comments/1sm6y5g/backtested_intraday_mean_reversion/
- **M035** | MT5; H1; gün içi/kısa swing | https://github.com/SokeWang/Breakout-Trading-Strategy/blob/main/strategies/breakout/reports/experiments_summary_2025.md
- **M036** | QQQ; günlük swing | https://www.reddit.com/r/algotrading/comments/1cwsco8/a_mean_reversion_strategy_with_211_sharpe/
- **M037** | SPY; günlük | https://quantifiedstrategies.substack.com/p/what-is-the-best-rsi-oversold-level
- **M038** | SPY; günlük; birkaç gün | https://quantifiedstrategies.substack.com/p/best-time-frame-for-candlestick-patterns
- **M039** | QQQ; günlük | https://quantifiedstrategies.substack.com/p/we-combined-rsi-ema-and-vwap-on-qqq
- **M040** | SPY; günlük | https://quantifiedstrategies.substack.com/p/a-simple-stochastic-pullback-strategy
- **M041** | QQQ; günlük | https://quantifiedstrategies.substack.com/p/new-low-trading-strategy
- **M042** | SSO; günlük; birkaç gün | https://quantifiedstrategies.substack.com/p/2-price-action-trading-strategies
- **M043** | Altı enstrüman; 10 günlük swing | https://github.com/erhungn/volatility-regime-momentum
- **M044** | 43 kripto çifti; H4; swing | https://github.com/juriok/chart-pattern-backtester
- **M045** | BTCUSD; H1 grafikte H4 Heikin Ashi | https://www.tradingview.com/script/f4SEwIH3-Optimized-Heikin-Ashi-Strategy-with-Buy-Sell-Options/
- **M046** | BTCUSDT; H4 | https://www.tradingview.com/script/O6E7WhRC-ELLIPSE-Bidirectional-Swing-Trading-Strategy-Strategy-Version/
- **M047** | Altın; H1 | https://www.tradingview.com/script/8b1AgVrV-Gold-Swing-More-Trades-50-SL-100-TP/
- **M048** | ETHUSDT spot; H4 | https://www.tradingview.com/script/9qFCuXqF-3Commas-Turtle-Strategy/
- **M049** | BTCUSDT perpetual; H4 | https://www.tradingview.com/script/eZsaqsZY-BTC-RSI-Strategy-3Commas/
- **M050** | En büyük 100 ABD hissesi; haftalık | https://quantpedia.com/strategies/short-term-reversal-in-stocks
- **M051** | BTCUSDT 1 saat; **+%45,36, WR %100, Sharpe 2,63, DD %1,63** | https://jesse.trade/strategies/meanreversionrsi
- **M052** | 2009: net $920,75; PF 1,14; WR %60,16; 251 işlem; DD %17,25; başlık 53 sayfa/380 abonelik | https://www.forexfactory.com/thread/post/3629700
- **M053** | Sistem paketi **7.036 indirme** | https://forex-station.com/attach/file/3477006
- **M054** | 2021 PF 2,2; sekiz yıllık PF 1,59; başlık 4.449 görüntülenme | https://nexusfi.com/showthread.php?p=858460&t=58030
- **M055** | %0,5 slippage ile yıllık %95 / DD %49 / WR %50; Rank>99 sürümünde yıllık %107 / DD %27 / W | https://community.portfolio123.com/t/testimonial/17867
- **M056** | RSI: +%25,12/Sharpe1,34/WR%67,8/DD%8,45; MACD: +%23,89/Sharpe1,56/WR%71,1/DD%6,23; EMA: +% | https://github.com/ErikKerkvliet/FreqtradeHyperOpt
- **M057** | 2.600+ NSE hissesi, 2 yıllık swing; bildirilen PF **1,20** | https://github.com/AaryavGangrade/nse-pattern-scanner
