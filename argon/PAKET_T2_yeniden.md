# Argon görev paketi: T2 yeniden okuma (38 kart)

Bu mesajı olduğu gibi Argon'a yapıştır. Cevabı `argon/T2_yeniden.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_yeniden`).

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
- **A3-004** | Pairs_Trading (gün içi eş-bütünleşme, M1) | https://github.com/Neuvox512/Pairs_Trading | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **A4-009** | Volume Spikes in Oil Futures (embedded backtest) | https://www.quantconnect.com/terminal/cache/embedded_backtest_19dce81c99a5fcc437 | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **B1-002** | AlphaTrend Strategy (TradingView, Kıvanç Özbilgiç) | https://www.tradingview.com/script/3wdQu7P3-AlphaTrend-Strategy | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **B2-001** | Opening-Range Breakout (TradingView, vadeli) | https://pl.tradingview.com/script/8vjWAdLN-Opening-Range-Breakout/ | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **B2-005** | Athena Momentum Squeeze - Short, Lean, and Mean | https://in.tradingview.com/script/Oy4huVQ2-Athena-Momentum-Squeeze-Short-Lean-an | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-002** | FIRSATÇITRENDİFLİSİSTEMANILBy (Fırsatçı Trend + IF'li sistem) | https://algokutuphanesi.com/Sistem/Detay/Matriks/FIRSATÇITRENDİFLİSİSTEMANILBy | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-003** | PHL1 YİĞİT KAYNAK | https://algokutuphanesi.com/Sistem/Detay/Matriks/PHL1-YİGİT-KAYNAK | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-004** | PHL2 YIGITBOX | https://algokutuphanesi.com/Sistem/Detay/Matriks/PHL2YIGITBOX | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-005** | ROTT-SOTT | https://algokutuphanesi.com/Sistem/Detay/Matriks/ROTT-SOTT | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-006** | MOTT-4B Kurgu | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/MOTT-4B-Kurgu | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-007** | SÜPERTRENDMOSTOPTİMİZASYONLU | https://algokutuphanesi.com/Sistem/Detay/Matriks/SÜPERTRENDMOSTOPTİMİZASYONLU | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-008** | Anıl Özekşi Sistem 1 | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/Anil-Özekşi-Sistem-1 | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-009** | MOTT 4 Kurgu Stratejisi | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/MOTT-4-Kurgu-Stratejisi | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-010** | FirsatciTrend 4Bölge LONG | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/FirsatciTrend-4Bölge-LONG | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-011** | SuperTrendVadeliStratejisi | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/SuperTrendVadeliStratejisi | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-013** | OTT-STOCK-HHV-LLV-HOTT-LOTT-LONG | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/OTT-STOCK-HHV-LLV-HOTT-LOTT-LONG | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-019** | EMA 25/68 BIST30 Futures | https://www.tradingview.com/script/Tbh1KPxq/ | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-027** | PMax Explorer STRATEGY & SCREENER | https://www.tradingview.com/script/nHGK4Qtp/ | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-029** | Grover Llorens Activator Strategy Analysis | https://www.tradingview.com/script/VuYM89Tw-Grover-Llorens-Activator-Strategy-An | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-030** | Uhl MA System - Strategy Analysis | https://www.tradingview.com/script/4S9Yz3DB-Uhl-MA-System-Strategy-Analysis/ | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-031** | Trendline Breaks with Multi Fibonacci Supertrend Strategy (TMFS) | https://www.tradingview.com/script/aVzNdTMg-Trendline-Breaks-with-Multi-Fibonacci-Supertrend-Strategy | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-032** | Scalping Support Resistance Strategy | https://www.tradingview.com/script/gp332Dao-Scalping-Support-Resistance-Strategy | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-033** | Scalping with Bill Williams Alligator | https://www.tradingview.com/script/b2ShO5Fv-Scalping-with-Bill-Williams-Alligator | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-034** | [Sniper] SuperTrend + SSL Hybrid + QQE MOD | https://www.tradingview.com/script/6w9Jchj6/ | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **O1-035** | ORB Heikin Ashi SPY 5min Correlation Strategy | https://www.tradingview.com/script/QpJvYDzb-ORB-Heikin-Ashi-SPY-5min-Correlation | sonnet: kaynak sitesi Sonnet ortaminda engelli
- **A2-004** | SessionReopenEA | https://www.mql5.com/en/code/77060 | argon: varsayilan parametreler icin .mq5 kaynak kodu okunmali
- **A2-006** | Price Action Intraday Trading - Expert for MT5 | https://www.mql5.com/en/code/68704 | argon: varsayilan parametreler icin .mq5 kaynak kodu okunmali
- **A2-011** | APEX VELOCITY | https://www.mql5.com/en/code/78275 | argon: varsayilan parametreler icin .mq5 kaynak kodu okunmali
- **A2-012** | ORB Risk Managed - Opening Range Breakout | https://www.mql5.com/en/code/77967 | argon: varsayilan parametreler icin .mq5 kaynak kodu okunmali
- **A2-013** | Opening Range Breakout with NR4 / NR7 Contraction Filters | https://www.mql5.com/en/code/78259 | argon: varsayilan parametreler icin .mq5 kaynak kodu okunmali
- **A1-016** | VIOP Scalping - ATR SNIPER | https://www.tradingview.com/script/R0CTM8NR-VIOP-Scalping-ATR-SNIPER/ | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A1-017** | VIOP Scalping - Original | https://www.tradingview.com/script/4BcYQ0Ns-VIOP-Scalping-Original/ | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A1-019** | BIST30 to S&P 500 ATR Momentum Rider | https://www.tradingview.com/script/jd1KSVn7/ | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A1-020** | Antony.N4A - NQ ORB Quartile Str v6.3 | https://de.tradingview.com/script/uUtBQ59O-Antony-N4A-NQ-ORB-Quartile-Str-v6-3 | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A1-022** | Slight Swing Momentum Strategy | https://it.tradingview.com/script/6l9kcw7j | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A1-023** | ORB Breakout Strategy (chartsquare) | https://ru.tradingview.com/script/VJ9ZHgNB-ORB-Breakout-Strategy | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A1-024** | TrendMaster Pro 2.3 with Alerts | https://www.tradingview.com/script/mVkDf8qh-TrendMaster-Pro-2-3-with-Alerts/ | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
- **A2-010** | ICE (Impulse Confirmation Engine) | https://www.mql5.com/en/code/69651 | argon: TradingView okunamadi; ayna (Scribd, TradeSearcher, GitHub) aranmali
