# Argon görev paketi: T2 parti 12 

Bu mesajı olduğu gibi Argon'a yapıştır. **Dosya adı önemli:** cevabı kaydederken adını `T2_parti12.yaml` yap (Gemini'nin verdiği otomatik adı değiştir). Cevabı `argon/T2_parti12.yaml` adıyla `argon/` klasörüne yükle (commit mesajı `[Argon] T2_parti12`).

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
ozet: {paket: T2_parti12, kart_sayisi: N, tam: n, eksik: n, gizli: n, dakikalik: n, ihtiyari: n, sadece_short: n, okunamayan_url: [ID, ...]}
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



**Not:** ID'ler `G` ile başlar (güncellenmiş liste PDF'inden). Kaynak açılmazsa, kural özeti `day_trade_swing_trade_guncellenmis_strateji_listesi.pdf` içinde aynı başlık altında var; o zaman `kaynak.dosya` olarak PDF'i yaz ve belirsiz'e "yalnız PDF özeti" not et.

## Liste
- **G001** | KISS — Keep It Simple and Stupid | https://www.prorealcode.com/prorealtime-trading-strategies/keep-simple-stupid-strategy/
- **G002** | VWAP–RSI Scalper FINAL v1 | https://www.tradingview.com/script/S9hY3huK-VWAP-RSI-Scalper-FINAL-v1/
- **G003** | Reinforced Smooth Scalp | https://github.com/IvanLetteri/AITA---Strategies/blob/main/reinforced-smooth-scalp-berlinguyinca/reinforced-smoothscalp-results.txt
- **G004** | TIS BTC Momentum + Confluencia | https://www.tradingview.com/script/k9nauxnv-TIS-BTC-ESTRATEGIA-Momentum-Confluencia/
- **G005** | XLP Mean Reversion w/ Twist | https://www.wealth-lab.com/Strategy/DesignPublished?strategyID=78
- **G006** | AutoTune Filter | https://financial-hacker.com/the-autotune-filter/
- **G007** | Crude Oil Tuesday/Thursday Pullback | https://www.linkedin.com/posts/quantifiedstrategies_crude-oil-trading-strategies-backtest-activity-7473374012308381697-Z8iI
- **G008** | Holy Thursday Sprint | https://www.linkedin.com/posts/quantifiedstrategies_trading-activity-7443606957179154432-_BsV
- **G009** | Pre-Easter Week | https://www.linkedin.com/posts/quantifiedstrategies_trading-activity-7443606957179154432-_BsV
- **G010** | OPEX Week Long | https://www.linkedin.com/posts/quantifiedstrategies_quantifiedstrategies-activity-7440715064598405121-4a_l
- **G011** | PowerX — RSI + Stochastic + MACD | https://github.com/IvanLetteri/AITA---Strategies/blob/main/rsi-stoch-macd/powerx-results.txt
- **G012** | Riding Bollinger Bands | https://github.com/IvanLetteri/AITA---Strategies/blob/main/bb_riding/btst_bb_riding_hopt_results.txt
- **G013** | Trend Trigger | EMA + MTF Stochastic | URL yok: TradingView'da bu adla ara (yazar büyük ihtimalle blitz_locked ya da benzeri). Bulamazsan `erisim_engeli: true`.
