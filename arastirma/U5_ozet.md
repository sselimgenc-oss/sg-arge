# U5: TradingView açık kaynak strateji toplama, özet

Kayıtlar: `arastirma/U5_tv.csv`, 1298 satır (her tekil script bir satır).
Geçenler: `suzgec_sonucu == gecti`, **205 script**. Adayları bunlardan seçeceksin (en çok 10).

**Yazarın backtest rakamlarına bakılmadı ve hiçbir yere yazılmadı.** Sayfa açıklamaları yalnız zaman dilimi anahtar sözcüğü taraması (adım 2) için okundu. Süzgeç ve etiketler yalnız mekanizma ve koda dayanır.

## 1. Bağlantılar

| | sayı |
|---|---|
| "Takip edilen yazarlar" sayfası | 355 script bağlantısı |
| "Topluluk / popüler" sayfası | 1000 script bağlantısı |
| İki sayfada da olan | 57 |
| **Tekil script** | **1298** |

- Çıkarma: iki HTML'deki bütün `tradingview.com/script/<ID>` bağlantıları, her kart için başlık ve yazar ayrıca okundu. Sayfalardaki 1355 kartın hepsi "Strateji" rozetli (filtre: Strateji + yalnız açık kaynak).
- Kaynak çekme (U3 yöntemi): script sayfası → sayfadaki `script_id_part` (PUB kimliği) → `pine-facade.tradingview.com/pine-facade/get/<PUB>/last`.

## 2. Huni (sırayla, her elenen için `neden` CSV'de)

| Adım | Elenen | Kalan |
|---|---:|---:|
| Başlangıç | | 1298 |
| 0. Kaynak alınamadı (`erisim_yok`) | 1 | 1297 |
| 1. Strateji değil (`strategy()` çağrısı yok) | 2 | 1295 |
| 2a. Zaman dilimi dışı (`tf_disi`) | 942 | 353 |
| 2b. Zaman dilimi belirsiz (`tf_belirsiz`) | 60 | 293 |
| 3. Kural eksik (`kural_eksik`) | 10 | 283 |
| 4. Repaint / lookahead izi (`repaint`) | 64 | 219 |
| 5. Tekrar (`tekrar`) | 14 | **205** |

Ayrıntılar:

- **0.** 1 script sayfası 404 verdi (kaldırılmış). Bu kayıt `kaynak_durumu = erisim_yok`.
- **1.** `strategy()` çağrısı olmayanlar: 2 adet.
- **2.** Zaman dilimi, scriptin yayınlandığı grafik aralığıdır (sayfadaki `interval`). 4H (`240`) ve 1D (`1D`, `D`) kabul edildi.
  - 293 script geçti: 166 tanesi 1D, 127 tanesi 4H.
  - Dışarıda kalanların çoğu 5m (221), 1H (175), 15m (162), 1m (131).
  - `tf_belirsiz` (60): grafik aralığı 4H/1D değil ama başlık ya da açıklamada 4H/1D'ye işaret eden bir sözcük var (neden sütununda sözcük yazılı). Gerekirse bu 60 elle gözden geçirilebilir.
- **3.** Kural tamlığı: giriş çağrısı (`strategy.entry/order`) ve çıkış (`strategy.exit/close/close_all` ya da ters yönde giriş) kodda var mı. 10 eleme:
  - 5'i otomatik: `strategy.entry` yok ya da çıkış yok.
  - 5'i elle okumadan sonra:
    - al-tut karşılaştırma betikleri (HODL, kaldıraçlı benchmark);
    - periyodik alım (DCA) betiği;
    - sinyali dış kaynaktan alan "Universal Strategy Feed";
    - girişi `bar_index % 333` ile üreten pozisyon boyutu örneği.
- **4.** Repaint izi, 64 script:
  - `kaydirilmamis_security` (57): `request.security` çağrısı, ifadede `[1]` kayması olmadan, grafik zaman diliminden farklı bir zaman diliminde.
  - `lookahead_on_varsayilan_v1/v2` (6): Pine v1/v2'de `security` varsayılan lookahead açıktır.
  - `lookahead_on_kaydirmasiz` (1).
  - `[1]` ile kaydırılmış `lookahead_on` kalıbı güvenli sayıldı, elenmedi.
  - `[-N]` ile gelecek bar erişimi bulunmadı.
- **5.** Tekrar, 14 script:
  - 5'i Faz 1 / U3 / T35'te aynı script kimliğiyle kayıtlı: AlphaTrend, PMax Explorer, SuperTrend STRATEGY, EMA Slope + EMA Cross (ChartArt), BIST30 to SP 500 ATR Momentum Rider.
  - 4'ü aynı yazar + ad ya da aynı kod (MultiCross, Vix FIX/StochRSI, LuxAlgo SMC Pro, EMA Golden/Dead Cross).
  - 5'i aynı mantığın sürümü (ilk kayıt kalır, diğerleri elenir): EMA-RSI-ATR şablonunun 2 ikizi, BTC/USD trend motoru v2, Gaussian kanal BTC sürümü, SMA14/28 kesişim örneği.
  - Faz 1 `docs/KATALOG.csv`'de isim eşleşmesi çıkmadı. `docs/spec` ve `TUM_KAYITLAR.csv` ile isim ve kimlik eşleştirmesi yapıldı.

## 3. Geçen 205 scriptin dağılımı

- Zaman dilimi: 1D 126, 4H 79.
- Liste: yalnız popüler 137, yalnız takip 54, ikisinde de 14.
- Yön: 125'i hem long hem short, geri kalanı tek yönlü (49'unun `neden` alanında "yalniz long" yazılı). Yalnız long isteniyorsa `neden` ve `giris` sütunlarından süzülür.
- Açık stop kodu olmayan 92 kayıt: çıkış başka bir kurala bağlı (`stop` alanı "kodda sabit stop yok").

Mekanizma dağılımı (anahtar sözcükle atanmış tek etiket, yaklaşık):

| Mekanizma | sayı |
|---|---:|
| Trend takibi: Supertrend, hareketli ortalama kesişimi, Hull, KAMA, Ichimoku | 89 |
| Desen / piyasa yapısı: SMC, Elliott, order block, pivot, Fibonacci, mum, uyumsuzluk, zigzag | 35 |
| Kırılım: Donchian, Turtle, kanal, sıkışma | 30 |
| Rejim / pozisyon oranı / kademeli birikim: DCA, volatilite hedefi, rotasyon | 19 |
| Momentum / osilatör ve diğer koşullu kombinasyonlar | 16 |
| Ortalamaya dönüş / dip alım: RSI, Bollinger, VWAP, IBS | 11 |
| Takvim / astronomi (ay evresi, haftanın günü) | 3 |
| ML / regresyon ağırlıklı model (Pine içinde XGBoost, sabit Lasso katsayıları) | 2 |

## 4. Sınırlar

- **`giris`, `cikis`, `stop` alanları kodun otomatik çıkarımıdır.** Değişken tanımları iki seviye açılır, `input` varsayılanları `ad(=değer)` biçiminde yazılır. Uzun ifadeler 420 karakterde kesilir ve parametreler Pine'daki varsayılan değerlerdir. Seçtiğin adayların kuralı kart yazılırken Pine kaynağından yeniden okunmalı. Çıkarım çok satırlı `if (` bloklarında ve kullanıcı fonksiyonlarında eksik kalabilir. Bu durumda `mekanizma` alanındaki elle yazılmış özet geçerlidir.
- **Zaman dilimi yayın aralığına dayanır.** Yazar başka aralıkta da çalıştırılabilir diye tasarlamış olabilir; `tf_disi` olanlar bu yüzden kesin "bu zaman diliminde çalışmaz" demek değildir.
- **`kural_eksik` mekanik bir kapıdır.** Giriş ve çıkış çağrısı var diye kuralın tam, mantıklı ya da tekrarlanabilir olduğu anlamına gelmez. Bazıları eğitim örneğidir (`neden` alanında "egitim ornegi / sablon"). Bazıları çok koşullu ya da karmaşık (SMC, Elliott, order block). Bunlar `neden` alanında işaretli.
- **Repaint taraması regex ile yapıldı.** Kullanıcı fonksiyonunun içinde `[1]` kaydırması olan ama çağrı ifadesinde görünmeyen durumlar yanlışlıkla elenmiş olabilir (yanlış pozitif).
- Çok enstrümanlı (VIX, SPX, QQQ), kazanç verisi isteyen (`request.earnings`) ve opsiyon benzetimi yapan scriptler `neden` alanında işaretli.
- Kaldıraç kullanan scriptlerde (3x, 4x, 5x) kaldıraç `neden` alanında yazılı.
