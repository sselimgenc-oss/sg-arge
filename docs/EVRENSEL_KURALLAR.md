# Evrensel uygulama ve test kuralları (lider, v1)

Amaç: ~316 stratejinin hepsi **aynı koşullarda** test edilsin, sonuçları karşılaştırılabilir olsun. Stratejinin kendi giriş/çıkış mantığına dokunulmaz; değişen yalnız ortam. Eleme eşikleri `ELEME_KRITERLERI.md`'de.

## A. Uygulama (her strateji için aynı)
1. Sinyal yalnız **kapanmış bar** ile üretilir; emir **sonraki barın açılışında** dolar. Aynı bar bilgisiyle aynı bar fiyatından dolum yasak.
2. Üst zaman dilimi (MTF) yalnız tamamlanmış barıyla kullanılır.
3. Aynı bar içinde hem stop hem hedef tetiklenirse **önce stop** sayılır (kötümser).
4. Gap: stop/hedef ilk uygulanabilir açılıştan dolar.
5. Temel mod **long-only, kaldıraçsız**. Short/kaldıraç ayrı faz.
6. **Pozisyon boyutu standart:** işlem başı risk özsermayenin %0,5'i; toplam açık risk %2; brüt %100. Stratejinin kendi boyutlaması yok sayılır (karşılaştırılabilirlik).
7. **Stop:** stratejinin kendi stopu varsa o; yoksa ATR14×3 standart stop eklenir ve kart `stop_eklendi: true` ile işaretlenir.
8. Maliyet: `ELEME_KRITERLERI.md` baz maliyet tablosu; 1x/2x/3x.
9. **Parametreler:** yazarın varsayılanı. Aşama 1'de optimizasyon yok. Plato taraması yalnız aşama 2'de, komşuluk olarak.
10. Repaint eden gösterge (gelecek barı kullanan zigzag, `security` lookahead, merkezlenmiş ortalama) → **Reddedildi (look-ahead)** ya da kapanmış bar versiyonu, kartta not.

## B. Evren ve veri
| Piyasa | Evren | Günlük veri | Gün içi veri |
|---|---|---|---|
| BIST30 | `data/evren.csv` (28) | yfinance 2015 → | yfinance 1h, ~730 gün |
| ABD | 25 büyük hisse + SPY, QQQ | yfinance 2015 → | yfinance 1h, ~730 gün |
| Kripto | 25 | Binance 2017 → | Binance 1m-1h, 2017 → |
| Emtia | 6 ETF | yfinance 2015 → | yfinance 1h, ~730 gün |

- Strateji hangi piyasa için yazılmış olursa olsun (forex dahil) **4 piyasanın hepsinde** çalıştırılır; yazarın piyasası raporda ayrıca belirtilir. Forex verisi kapsam dışı.
- **Zaman dilimi:** 1H ve üstü → doğal zaman diliminde. **1H altı (1m-30m)** → yalnız kripto (Binance) doğal zaman diliminde; BIST/ABD/emtia için **Doğrulanamaz (dakikalık veri yok)**. Zaman dilimi değiştirilerek "uyarlama" yapılmaz.
- Zaman dilimi belirtilmemişse: swing → 1D, day → 1H; kartta `tf_varsayim: true`.

## C. Dönemler
- Günlük: IS 2020-01-01 → 2024-09-30, OOS 2024-10-01 → son, ön dönem tutma 2015 (kripto 2018) → 2019-12-31.
- Saatlik (BIST/ABD/emtia): ilk 2/3 IS, son 1/3 OOS. Ön dönem yok → en fazla Koşullu.
- Kripto gün içi: 2018-2019 ön dönem, 2020 → 2024-09 IS, 2024-10 → OOS.

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
