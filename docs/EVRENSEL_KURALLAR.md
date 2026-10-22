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
- **Zaman dilimi:** 1H ve üstü → doğal zaman diliminde. **1H altı (1m-30m)** → yalnız kripto (Binance) doğal zaman diliminde; BIST/ABD/emtia için **Doğrulanamaz (dakikalık veri yok)**. Dakikalık stratejiler scalp diye elenmez (kullanıcı kararı 2026-10-22). Zaman dilimi değiştirilerek "uyarlama" yapılmaz.
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

### D3. Lider kararları (T2 parti 2-3 sonrası)
- **`spec_durumu` öncelik sırası:** `gizli` > `ihtiyari` > `sadece_short` > `eksik` > `dakikalik` > `tam`. Yeni durumlar: `ihtiyari` (yoruma dayalı kural, mekanik test edilemez → **Doğrulanamaz**), `sadece_short` (long kuralı yok → short fazına ertelenir), `kapsam_disi` (strateji değil: meta/örnek depo, ör. A3-012/013/014).
- `erisim_engeli: true`: kaynak okunamadı; kart `docs/spec/YENIDEN.csv` üzerinden yeniden okunur. Erişim sorunu stratejinin başarısızlığı değildir.
- **`reverse=true` varsayılanlı Pine'lar (CP1, LRCUTB):** yazarın raporladığı davranış esastır. Ters sinyal uygulanmış hâlin long kolu test edilir (formasyon "bearish" iken long). Kartta `ters_sinyal: true`.
- **Şema ekleri kabul:** `roi_tablosu` (Freqtrade), `alias_of` (aynı kural; ayrıca test edilmez, sonucu asıl karttan alır), stop/hedef ifadelerinde `giris`, `giris_stop`, `giris_hedef`, gösterge `tf: 1M`.
- **Piyasaya özgü saat kuralları** (BIST seansı 10:03-17:58 gibi): yalnız o piyasada test edilir; diğer piyasalarda `Doğrulanamaz (piyasa özgü)`.
- **`ozel_kod: true` kartlar** aşama 1 taramasında atlanır. Tarama bittikten sonra T5b'de, raporlanan kanıt kalitesi ve kaynak kodun açık olması sırasıyla elle kodlanır. Kaynak kodu karta bağlı olmalı.
- **Çok kısa yazar testleri** (10 gün ile birkaç ay arası pencere): rapor rakamı kanıt sayılmaz, yalnız bizim testimiz geçerli.

### D3b. Erişilemeyen kaynaklar (kullanıcı kararı)
`docs/spec/YENIDEN.csv`'de kalan ve Argon tarafından da okunamayan kartlar sonuç raporunda **Doğrulanamaz (kaynak erişilemedi)** olarak yer alır. Reddedilmiş sayılmaz; site ve neden raporda belirtilir.

### D4. Lider kararları (T2 parti 5 sonrası)
- **Kapanış dolumu (MOC) istisnası:** Kaynak açıkça "kapanışta al/sat" diyorsa ve karar zaman dilimi günlükse kartta `dolum: kapanis` yazılır. Bu kartlar iki şekilde test edilir: (a) sinyal barının kapanışından dolum, maliyet **2x baz** (kapanış seansı/MOC emri kayması için); (b) A1 (ertesi açılış). Rapor ikisini de verir. Karar (a)'ya göre verilir ama (b) negatifse **Koşullu**. Gün içi kartlarda istisna yok. Gerekçe: BIST kapanış seansı ve ABD MOC emirleri bu dolumu canlıda uygulanabilir kılar. Sinyal kapanıştan birkaç dakika önceki fiyatla hesaplanır, fark kayma olarak maliyete yansır.
- **Takvim ilkeli:** ifade diline `ay_islem_gunu_bastan(k)`, `ay_islem_gunu_sondan(k)`, `haftanin_gunu` eklenir (T5). Bu kartlar `ozel_kod` sayılmaz.
- **Evrenimizde olmayan piyasa/enstrüman** (JP225 CFD, ABD vadeli seans saatleri, tick verisi): kural genel ise 4 piyasada test edilir; enstrümana/seansa bağlıysa **Doğrulanamaz (piyasa özgü)**.
- **`piyasa_kisiti: [..]`**: mutlak fiyat/pip birimli ya da seans saatine bağlı kurallar yalnız listelenen piyasalarda test edilir (ör. O1-078 → `[ABD]`). Diğer piyasalar için sonuç **Doğrulanamaz (piyasa özgü)**.
- **Kaldıraçlı ETF rotasyonları** (Composer): kaldıraç fazına (faz 3) ertelenir, `ertelendi: kaldirac`.

Kural karta çevrilemiyorsa (ör. makine öğrenmesi, order flow, haber) → `spec_durumu: eksik` ve `belirsiz`'e neden yazılır; yorumlayıcıya özel kod gerekiyorsa `ozel_kod: true`.


### D5. Cikis alanlarinin motor anlamlari (T5b-1, Sonnet; lider onayina acik)
Hepsi `engine/portfolio.py` + `engine/kart_sinyal.py` ile uygulanir; tum emirler A1-A4 ile uyumludur (kapanmis bar sinyali, sonraki acilis, ayni barda stop once, gap'te acilistan dolum).
- **`stop`**: `atr` = giris - carpan x ATR(n) (sinyal barinin ATR'si, sabit); `yuzde` = giris x (1 - deger/100) (dolum fiyatina gore); `puan` = giris - deger; `max` = `secenekler` ifadelerinin sinyal barindaki en buyugu kadar mesafe. Karta stop yok ve `iz_suren` de yoksa A7: ATR14 x 3 sabit stop eklenir (`stop_eklendi: true` tarama satirinda). Karta stop yok ama `iz_suren` varsa baslangic stopu iz suren mesafesidir.
- **`hedef`**: `atr` = giris + carpan x ATR(n); `yuzde`; `puan`. Ayni barda stop ve hedef birlikte vurulursa stop.
- **`iz_suren`**: `atr_kapanis_zirve` = stop = max(stop, kapanis - carpan x ATR_t); `atr_zirve` = stop = max(stop, yuksek - carpan x ATR_t). Her ikisi bar kapanisinda hesaplanir, ertesi bardan gecerlidir (T1a motoruyla ayni).
- **`kar_kilidi {tetik_atr, stop}`**: bar yuksegi giris + tetik_atr x ATR(sinyal) degerine ulasinca stop `stop` ifadesindeki seviyeye (`giris` = dolum fiyati) cekilir; ertesi bardan gecerli, stop asla asagi inmez.
- **`zaman_stop {bar}`**: pozisyon `bar` bar piyasada kalinca cikis emri (sonraki acilista). Giris barindan sayilir.
- **`cooldown_bar`**: cikis barindan sonraki `cooldown_bar` barda gelen giris sinyalleri yok sayilir.
- **`dolum: kapanis`**: (a) sinyal barinin kapanisindan dolum, maliyet 2x baz; (b) A1 (sonraki acilis, baz maliyet). Tarama karari (a)'ya gore verir, (b) tablo olarak raporlanir, (b) negatifse not duser.
- **Calisma zamani adlari** (`giris_fiyati`, `giris`, `giris_stop`, `giris_hedef`, `bars_since_entry`, `stop_mesafesi`) yalniz `cikis` ve stop ifadelerinde; `bars_since_entry` dolum barinda 0'dir. `cikis` bunlari kullaniyorsa her pozisyon icin giriste yeniden hesaplanir.
- **`mtf("1W", x)`** = x'in onceki tamamlanmis haftalik barin son degeri. **`hizalama: etiket`** (gosterge alani, yalniz haftalik `tf`): hafta takvimsel bitis gununde (borsa Cuma, kripto Pazar) tamamlanmis sayilir ve o gunun kapanisinda kullanilabilir (T1a referans hizalamasi; C01/C02 paritesi icin).
- **Desteklenmeyenler** (`motor_destegi_yok:<alan>` olarak atlanir): `kismi_kar`, `roi_tablosu`, `stop.pips`, `iz_suren.fiyat_adim`, `giris_modu`.
- **Endeks**: `endeks_close` / `benchmark: endeks` ABD icin SPY, kripto icin BTCUSDT; BIST30 ve emtiada endeks serisi olmadigindan o piyasalarda Dogrulanamaz (`endeks_yok`).

### D6. `kismi_kar` ve asama 2a testleri (T6a, Sonnet; lider onayina acik)
- **`kismi_kar {gun, tetik_atr | tetik, oran, kalan_stop}`:** pozisyon `gun` bar piyasada kaldiktan sonra, bar kapanisindaki kar `tetik_atr x ATR(sinyal)` (veya `tetik` ifadesinin fiyat birimi; ifadede `stop_mesafesi` = giris - baslangic stopu, `giris`) esigini ilk kez gecince pozisyonun `oran` kadari **sonraki acilista** satilir (`dolum: kapanis` kartlarda ayni kapanista); kalan icin stop `kalan_stop` seviyesine (`giris` = dolum fiyati) cekilir, asla asagi inmez. Bir kez alinir. Islem tek satir kalir: `net_pnl` kismi satis dahil toplam, `exit_reason` `+partial` ile biter, `quantity` ilk miktar. Ayni anda cikis sinyali varsa cikis oncelikli.
- **BIST USD:** `USD fiyat = TL fiyat / ayni gun USDTRY kapanisi` (tatilde son kur); O/H/L/C'nin hepsi ayni kurla bolunur. Karar USD sonucuna gore; TL yalniz bilgi. USD'de asama 1 kapisi (islem >= 30, PF_1x >= 1,1, 2x net > 0) yeniden uygulanir, gecmeyen `Reddedildi (BIST USD)`.
- **Rastgele giris (null) modeli:** ayni piyasa, ayni cikis/stop/boyut/portfoy kurallari, 1x maliyet (MOC kartlarda kartin dolum modu ve maliyeti). Kartin sembol basina giris sayisi kadar giris, IS donemindeki gecerli (ATR hesaplanmis, son bar haric) barlardan rastgele secilir; pozisyondayken gelen rastgele girisler motorca yok sayildigindan giris sayisi pilot kosularla (en fazla 4 tur, 6 tekrar) olceklenir ki null islem sayisi kartinkine ~%5 yaklassin. Sabit tohum: `20261022 xor crc32(kart|piyasa)`. Karar: gercek PF **ve** ortalama R, null dagiliminin %95 yuzdeliginin ustunde olmali, aksi halde `Reddedildi (piyasa betasi)`. p = (1 + #{null >= gercek}) / (1 + tekrar). Sinir bolge (0,03 <= max(p) <= 0,10) 1000 tekrarla yeniden kosulur. Cikti `results/asama2a.csv`, `results/asama2a_ozet.md` (gercek/null islem sayisi ve ortalama tutma suresi kontrol icin yazilir).

### D7. Takvim ilkelleri: `ay_gunu()`, `paskalya(k)` (T2 parti 12, Sonnet; lider onayina acik)
- `ay_gunu()`: barin tarihinin ay gunu (1-31). Ayin 3. cumasi = `haftanin_gunu() == 4 and ay_gunu() >= 15 and ay_gunu() <= 21`.
- `paskalya(k)`: Bati (Gregoryen) Paskalya Pazari'ndan `k` takvim gunu sonraki tarihte True (k negatif olabilir). Kutsal Persembe `paskalya(-3)`, Paskalya oncesi carsamba `paskalya(-4)`, Paskalya haftasindan onceki cuma `paskalya(-9)`. Tatil gunu (bar yok) sinyal uretmez.
- Birlikte takvim kartlari G008, G009 (paskalya) ve G010 (ay_gunu) `ozel_kod` gerektirmez.

### D8. Bekleyen giris emirleri (T15, Codex)
- **`giris_emri {tip, seviye, gecerlilik_bar}`:** `giris` kurulum sinyalidir; `seviye` ifadesi sinyal barinda bir kez hesaplanip dondurulur. Emir sinyal barinda dolmaz, izleyen `gecerlilik_bar` bar boyunca (son bar dahil) aktiftir. Ayni sembolde yeni bir kurulum sinyali acik emrin seviyesini, boyutlama verilerini ve gecerlilik suresini yeniler.
- **Stop giris:** aktif barda `high >= seviye` ise dolum `max(open, seviye)` fiyatindadir; boylece seviyenin uzerine acilan gap iyimser fiyatlanmaz.
- **Limit giris:** aktif barda `low <= seviye` ise dolum `min(open, seviye)` fiyatindadir; boylece seviyenin altina acilan gap ilk erisilebilir fiyatla dolar.
- Stop/hedef giris barinda da etkindir. Giris ile koruyucu stop ayni barda, ya da stop ile hedef ayni barda gorulurse A3 uyarinca kotumser siralama uygulanir ve stop kazanir.
- Alan verilmezse A1'deki mevcut sonraki acilis dolumu aynen korunur. `dolum: kapanis` ile bekleyen giris birlikte kullanilmaz.

### D9. `roi_tablosu` ve gun ici tarama (T12, Sonnet; lider onayina acik)
- **`roi_tablosu {dakika: kar_orani}`** (Freqtrade `minimal_roi`): pozisyonun giris barinin acilis zamanindan bu yana gecen dakika (bar acilis zamani farki; giris barinda 0), tablodaki `dakika <= gecen` olan en buyuk anahtarin oranina ulasirsa cikilir. Bar yuksegi `giris x (1 + oran)` seviyesine ulasinca o fiyattan, bar bu seviyenin ustunde aciliyorsa acilistan dolar (`exit_reason: roi`). Stop ayni barda once kontrol edilir (A3). Son anahtar 0 ise (`{.., 600: 0}`) o sureden sonra basabasta (kar >= 0) cikis demektir.
- **Gun ici tarama (`tarama.py --tf 1H,30m,15m,5m,1m`):** 1H alti kartlar yalniz kriptoda (Binance); diger piyasalar `Dogrulanamaz (dakikalik_veri_yok)`. 1H kartlar dort piyasada: kripto IS 2020-01-01 -> 2024-09-30; BIST/ABD/emtia (yfinance ~2 yil) ilk 2/3 IS, son 1/3 gorulmez. BIST 1H, `results/veri_kalitesi_1h.md` sorunu (seans disi / sifir hacimli barlar) cozulene kadar `Dogrulanamaz (veri_kalitesi)`. Gun ici kartlarda kapanis dolumu istisnasi yok (D4): `dolum: kapanis` yok sayilir, A1 uygulanir. Sharpe yillik carpani bar sayisina gore (kripto 24/7, hisse 7 saat).

### D10. Sinyal bari referansli seviyeler, Williams fraktali, Renko sayaci, endeks verili gosterge (T20, Sonnet; lider onayina acik)
- **`stop: {tip: seviye, ifade}` / `hedef: {tip: seviye, ifade}`:** mutlak fiyat seviyesi, ifade **dolum aninda** hesaplanir. Kullanilabilir adlar: `giris` (dolum fiyati, sonraki bar acilisi ya da bekleyen emir dolumu), `sinyal_open/high/low/close/volume` ve her gosterge icin `sinyal_<ad>` (sinyal barindaki deger; cok sutunlu gostergelerde `sinyal_<ad>.<alan>`), hedefte ve kar kilidinde ayrica `stop_seviyesi` (cozulmus stop). Stop dolum fiyatinin altinda, hedef ustunde degilse (gap) **giris atlanir**. Boyutlandirma yine A6: risk = giris - stop.
- **`kar_kilidi: {tetik_seviye, stop}`:** bar yuksegi `tetik_seviye`'ye ulasinca stop `stop` seviyesine cekilir (yalniz yukari). `tetik_atr` formu degismedi; `tetik_seviye` ve `stop` ifadeleri `giris`, `sinyal_*`, `stop_seviyesi`, `hedef_seviyesi` kullanabilir.
- **`eger(kosul, a, b)`:** ifade dilinde if/else (skaler ya da seri).
- **`williams_fractal {n}`:** `.up`/`.down`, geraked Pine kaynagindaki dongulerin birebir portu (4 bar'a kadar esit/daha iyi onceki bar varyantlari dahil). Pivot `n` bar sonra bilinir; sinyal pivot barinin degil, onayin bari uzerindedir (look-ahead yok).
- **`renko_sayac {kutu, ilk_bar}`:** kapanis bazli sentetik Renko tugla sayaci (ProBuilder tarzi, `.up`/`.down`); sayaclar ters yonde tugla olusana kadar kalir.
- **`veri: endeks`** (gosterge alani): gosterge, islem gorulen enstruman yerine endeks (benchmark) serisinin kendi barlarindan hesaplanir ve takvime ffill ile hizalanir (ornek: endeks ATR'si). Endeks yoksa kart `EndeksYok` ile Dogrulanamaz olur.
- Her yeni ilkel icin look-ahead testi (seriyi t'de kesince t'ye kadarki degerler ayni) `tests/test_t20.py`'dedir.
