# Argon görev paketi: T2 parti 2 (40 strateji)

Bu mesajı olduğu gibi Argon'a (Gemini) yapıştır. Argon'un cevabını `argon/T2_parti2.yaml` adıyla GitHub'a yükle (repo → `argon/` klasörü → Add file → Upload files, commit mesajı `[Argon] T2 parti 2`).

---

Sen çok modelli bir algo trading araştırma ekibinin **kart çıkarıcısısın** (rol adı: Argon). Takım lideri Claude Opus. Ekipte Claude Sonnet ve OpenAI Codex de var. Çıktını lider denetleyecek.

**Proje amacı:** Yüzlerce yayımlanmış trading stratejisini ortak kurallarla backtest edip başarılı/başarısız listesi çıkarmak. Senin işin backtest değil. Her stratejinin kurallarını kaynağından okuyup makinece okunur bir YAML karta çevirmen gerekiyor. Kartları daha sonra Codex'in motoru çalıştıracak.

## Görev
Aşağıdaki 40 stratejinin her biri için:
1. URL'yi aç. Kod açıksa (Pine Script, MQL5, ProBuilder, AFL, Python) **koddan** oku, açıklama metninden değil. Kod ile açıklama çelişirse kod esastır; çelişkiyi `belirsiz`e yaz.
2. Kuralları aşağıdaki şemaya çevir. **Asla uydurma.** Kaynakta yoksa alanı `null` bırak ve `belirsiz` listesine yaz. Parametre değerleri yazarın varsayılanlarıdır.
3. Triyaj (`spec_durumu`):
   - `gizli`: kural ücretli, üyelere özel ya da kapalı.
   - `dakikalik`: karar zaman dilimi 1 saatin altında.
   - `eksik`: kritik bir kural (giriş ya da çıkış) yok.
   - `tam`: giriş, çıkış ve parametreler net.
4. Tek satırda birden fazla strateji varsa (örneğin bir GitHub reposunda 9 strateji) her birini ayrı kart yap: `ID` + `a`, `b`, `c`...
5. Gelecek barı kullanan (repaint) göstergeleri `belirsiz`e "REPAINT: ..." diye yaz. Örnekler: `request.security` içinde `lookahead_on`, zigzag, merkezlenmiş ortalama.
6. Giriş/çıkış ifadeleri **yalnız** aşağıdaki ifade dili ve gösterge listesiyle yazılır. Listede olmayan bir şey gerekiyorsa `ozel_kod: true` yap ve mantığı `belirsiz`e düz Türkçe yaz.
7. Şimdilik yalnız **long** kurallarını yaz. Short kuralları varsa `belirsiz`e "short kuralı var: ..." diye kısa not düş.

## Çıktı biçimi
**Tek bir YAML dosyası.** Kartları `---` ile ayır. Başka açıklama yazma. En sona şu özet kartı ekle:
```yaml
---
ozet: {parti: 2, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, okunamayan_url: [ID, ...]}
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
gostergeler:          # ortak kütüphaneden: sma, ema, wma, rsi, atr, adx, dmi, cci, macd, bb, kc, donchian, stoch, obv, mfi, vwap, kama, ichimoku, supertrend, roc, zscore, highest, lowest
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
Kural karta çevrilemiyorsa (ör. makine öğrenmesi, order flow, haber) → `spec_durumu: eksik` ve `belirsiz`'e neden yazılır; yorumlayıcıya özel kod gerekiyorsa `ozel_kod: true`.


## Strateji listesi (parti 2)
- **A1-016** | VIOP Scalping - ATR SNIPER | Day | TradingView | TF: belirtilmemiş | Kod: Pine Script (Açık kaynak) | https://www.tradingview.com/script/R0CTM8NR-VIOP-Scalping-ATR-SNIPER/
- **A1-017** | VIOP Scalping - Original | Day | TradingView | TF: belirtilmemiş | Kod: Pine Script (Açık kaynak) | https://www.tradingview.com/script/4BcYQ0Ns-VIOP-Scalping-Original/
- **A1-019** | BIST30 to S&P 500 ATR Momentum Rider | Swing | TradingView | TF: Günlük | Kod: Pine Script (Açık kaynak) | https://www.tradingview.com/script/jd1KSVn7/
- **A1-020** | Antony.N4A - NQ ORB Quartile Str v6.3 | Day | TradingView | TF: 5 dk onay; ORB 09:30-09:45 | Kod: Pine Script (Kapalı (korumalı, ücretsiz kullanım)) | https://de.tradingview.com/script/uUtBQ59O-Antony-N4A-NQ-ORB-Quartile-Str-v6-3
- **A1-022** | Slight Swing Momentum Strategy | Swing | TradingView | TF: Günlük | Kod: Pine Script (Açık kaynak) | https://it.tradingview.com/script/6l9kcw7j
- **A1-023** | ORB Breakout Strategy (chartsquare) | Day | TradingView | TF: 5 dk | Kod: Pine Script (Açık kaynak) | https://ru.tradingview.com/script/VJ9ZHgNB-ORB-Breakout-Strategy
- **A1-024** | TrendMaster Pro 2.3 with Alerts | Day | TradingView | TF: Belirtilmemiş (HTF MA 50) | Kod: Pine Script (Açık kaynak) | https://www.tradingview.com/script/mVkDf8qh-TrendMaster-Pro-2-3-with-Alerts/
- **A1-025** | TASC 2026.03 One Percent A Week | Swing | TradingView | TF: Haftalık döngü, gün içi limit | Kod: Pine Script (Açık kaynak) | https://www.tradingview.com/script/nVECqIQx-TASC-2026-03-One-Percent-A-Week/
- **A1-027** | Bjorgum Double Tap | Swing | TradingView | TF: belirtilmemiş | Kod: Pine Script (Açık kaynak) | https://www.tradingview.com/script/rLkjr2sQ-Bjorgum-Double-Tap/
- **A1-029** | SPX Trading Strategy for ThinkorSwim | Day | useThinkScript | TF: 10 dk (Heikin Ashi) | Kod: thinkScript (ThinkorSwim) (Forumda açık / tos.mx paylaşım linki) | https://usethinkscript.com/threads/spx-trading-strategy-for-thinkorswim.5087/
- **A2-001** | GER40 Evening Coil | Day | MQL5 Code Base | TF: H1 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/78380
- **A2-002** | Stochastic Daily Breakout for Gold | Day | MQL5 Code Base | TF: H1 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77900
- **A2-003** | Buy GBPJPY Every Monday | Day | MQL5 Code Base | TF: M1'e eklenir (barsız çalışır; orijinal test H1) | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77835
- **A2-004** | SessionReopenEA | Day | MQL5 Code Base | TF: H1/M1 verisi | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77060
- **A2-005** | GDS Renko RSI + MACD 4-Mode Demo EA | Day | MQL5 Code Base | TF: M1 (Renko 12.00 brick) | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/78581
- **A2-006** | Price Action Intraday Trading - Expert for MT5 | Day | MQL5 Code Base | TF: M15/H1/H4 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/68704
- **A2-007** | Pro MA Crossover EA for MT5 | Swing | MQL5 Code Base | TF: D1 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/70916
- **A2-009** | The Playground Series v1 to V4 | Day | MQL5 Code Base | TF: FVG zaman dilimi ayarlanabilir | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/68125
- **A2-010** | ICE (Impulse Confirmation Engine) | Day | MQL5 Code Base | TF: M15-H1 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/69651
- **A2-011** | APEX VELOCITY | Day | MQL5 Code Base | TF: M5 (H1 onayı) | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/78275
- **A2-012** | ORB Risk Managed - Opening Range Breakout | Day | MQL5 Code Base | TF: Herhangi (M1 verisiyle) | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77967
- **A2-013** | Opening Range Breakout with NR4 / NR7 Contraction Filters | Day | MQL5 Code Base | TF: Herhangi (M1/D1 verisi) | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/78259
- **A2-014** | Gold MT5 Fractal Breakout EA | Swing | MQL5 Code Base | TF: H1 swing, D1 de kullanılmış | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/78308
- **A2-015** | EMA Cross Scalper M15 (XAUUSD) | Day | MQL5 Code Base | TF: M15 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77180
- **A2-016** | RSI Exhaustion Reversal - EURUSD | Day | MQL5 Code Base | TF: M5 | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77738
- **A2-017** | ZoneUS30 | Swing | MQL5 Code Base | TF: Girdi (varsayılan belirtilmemiş) | Kod: MQL5 (Ücretsiz indirme (Code Base); indirme sayısı belirtilmemiş) | https://www.mql5.com/en/code/77748
- **A2-018** | TMS for M30 charts | Day | Forex Factory | TF: M30 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/526735-tms-for-m30-charts
- **A2-019** | Williams%R, SAR X-over 15 minute candles | Day | Forex Factory | TF: M15 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/989455-williamsr-sar-x-over-15-minute-candles
- **A2-020** | Quantum London Trading | Day | Forex Factory | TF: M1 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/551382-quantum-london-trading
- **A2-021** | Magic 100 | Day | Forex Factory | TF: H1 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/989445-magic-100
- **A2-022** | Lets Automate a Simple Renko Strategy! | Day | Forex Factory | TF: 10 pip Renko (M2 çevrimdışı) | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/531783-lets-automate-a-simple-renko-strategy
- **A2-023** | Up and under price pattern | Day | Forex Factory | TF: M30 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/444458-up-and-under-price-pattern
- **A2-024** | Most Famous Blessing 3.9.6 EA and Setfiles | Day | Forex Factory | TF: H1/M5 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/792598-most-famous-blessing-396-ea-and-setfiles
- **A2-025** | The Equilibrium, a key to success! | Day | Forex Factory | TF: Tüm zaman dilimleri | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/727775-the-equilibrium-a-key-to-success
- **A2-026** | v2v dynamic trading system | Day | Forex Factory | TF: M1 veri, çoklu | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/901713-v2v-dynamic-trading-system
- **A2-027** | Happs Trading System | Swing | Forex Factory | TF: H4 (örnek) | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/259419-happs-trading-system
- **A2-028** | TCO Trader EA | Day | Forex Factory | TF: Günlük trend + alt zaman dilimi | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/430840-tco-trader-ea
- **A2-029** | Simple Zigzag + Fibonacci Strategy | Swing | Forex Factory | TF: belirtilmemiş | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/987910-simple-zigzag-fibonacci-strategy
- **A2-030** | Channel MA Short-Term System | Day | Forex Factory | TF: M15 | Kod: belirtilmemiş (Forum başlığında ücretsiz paylaşım; ekler başlık içinde) | https://www.forexfactory.com/thread/707474-channel-ma-short-term-system
- **A3-001** | XAUUSD Pullback Window (4 fazlı durum makinesi) | Day | GitHub | TF: 5 dakika | Kod: Python (Backtrader) (Açık (MIT)) | https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd
