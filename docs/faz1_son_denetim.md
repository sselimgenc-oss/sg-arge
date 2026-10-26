# Faz 1 son denetim — lider (Sol 6.1 denetimi bekleniyor)

Kullanıcı: "Nihai karar içinize sindi mi? İkiniz de işlemleri denetleyin, B kararını da siz verin."

## Lider bulguları

### D1. Kendi hatam: "yılda işlem" hesabı yanlıştı
Yılda işlem sayısını sürüm tarihinden bugüne böldüm; oysa yfinance saatlik veri yalnız son ~2,9 yılı kapsıyor. Doğru pencereyle:
- **G4RNcGXg (SPY 1s): 30,6 işlem/yıl → kullanıcı kuralını geçiyor.** B kararı ortadan kalkıyor; aday kalır.
- hWvuZJN1 25,8 · oZYSB6Ui 20,7 · PZ5MpxP1 12,4 · WfaaCqaN 12,0 → yine kuralın altında, çıkar.
- Kullanıcının daha önce çıkardığı zayıflardan 4'ü (CSGmHoik TQQQ, xXrbltSH NQ, jn1rXKpM GOLD, MNBZqC72 MSI) doğru pencereyle ≥ 30/yıl; ama hepsi ~2,5 aylık veride 6–25 işlem. Kanıt yok denecek kadar az; çıkarılmış kalmaları önerilir.

### D2. Getirinin ne kadarı piyasa? (2023→, günlük; beta = piyasaya duyarlılık, alfa = piyasadan bağımsız kısım, t ≥ 2 anlamlı sayılır)

| Kimlik | Piyasa | Yıllık | Piyasa payı | Alfa | Alfa t |
|---|---|---:|---:|---:|---:|
| TV-zoY9DmsF | SPY | 4,4 | 1,7 | 2,6 | **2,1** |
| TV-DUCODGjC | SPY | 7,2 | 2,7 | 4,5 | 1,6 |
| TV-IMKs0OPw | SPY | 3,7 | 1,6 | 2,1 | 1,4 |
| G4RNcGXg | SPY | 4,7 | 2,6 | 2,1 | 1,2 |
| U4-H3:ABD25:1D | SPY | 3,9 | 2,7 | 1,2 | **0,6** |
| TV-dpkq3n4O (yedek) | SPY | 5,9 | 2,3 | 3,7 | 1,5 |
| TV-70PkIvTL (yedek) | SPY | 5,2 | 2,6 | 2,7 | 1,5 |
| TV-71yKm18B | BTC | 12,1 | 4,0 | 8,1 | 1,9 |
| TV-3BXWqwnF | BTC | 13,7 | 6,0 | 7,7 | 1,5 |
| U4-H2:KRIPTO25:1D | BTC | 7,5 | 4,0 | 3,5 | **0,6** |
| wcegMOXj (ETHBTC) | BTC | 1,9 | 0,1 | 1,8 | **2,2** |
| TV-egTb7TgJ (gölge) | BTC | 5,0 | 2,5 | 2,5 | 1,1 |
| TV-Q9OQye4C (gölge) | BTC | 7,4 | 4,4 | 3,0 | 1,1 |

(Yıllık değerler aynı ölçekte günlük ortalama × gün; aday tablosundaki "ölçekli yıllık" ile birebir aynı değil.)

Yorum: 2023-2026 hem ABD hem kripto için güçlü yükseliş dönemi. Stratejilerin çoğu uzun yönlü; getirinin %35-70'i piyasanın yükselişinden. Piyasadan bağımsız kısım (alfa) hepsinde pozitif ama yalnız 2'sinde istatistiksel olarak güçlü (zoY9DmsF, wcegMOXj). **Bu, stratejilerin kötü olduğu anlamına gelmez; beklentiyi düşürür ve paper'ın asıl test olduğunu gösterir.** Düşen piyasada bu kitapların birlikte zarar etmesi beklenmeli.

### D3. Mutabakat
wcegMOXj, G4RNcGXg, yhoK9cH4: günlük seri ile CSV neti tutarlı (fark ≤ 1,4 puan, günlük yeniden örnekleme). QCkIgf3z: tutarsız (4,8 ↔ 22,6) → beklemede kalır.

## Liderin karar önerisi (değişiklikler)
1. **U4-H3:ABD25:1D → yedek; yerine TV-dpkq3n4O.** Alfa t 0,6, getirinin çoğu piyasa; Sol da "yöntem çeşitliliği tercihi, p10 ile savunulamaz" demişti. dpkq3n4O'nun ilk dalgaya korelasyonu ≤ 0,31.
2. **G4RNcGXg kalır** (D1). Ama aktif günlerde SPY ile 0,87 korelasyon: fiilen "zamanlı SPY". Küçük boyut.
3. **U4-H2:KRIPTO25:1D çekirdekte kalır ama küçük** (alfa zayıf; tek değeri çekirdeğe düşük korelasyon 0,37/0,54). Alternatif yok: diğer sepetlerin hepsi çekirdeğe ≥ 0,6.
4. Portföy kuralına ekleme: **piyasa yönü tavanı** — ABD kitaplarının toplam SPY betası ve kripto kitaplarının toplam BTC betası ayrı izlenir; düşüş rejiminde (SPY/BTC 200 günlük ortalamanın altı) yeni giriş yarıya iner. (Öneri; Sol'un görüşü alınacak.)

## Sol 6.1 denetimi

### Kapsam ve hüküm

TV-2 JSON sonuçları, günlük getiri serileri, U7 özetleri, ilgili üretim kodu ve kartlar doğrudan incelendi. `data/daily/SPY.parquet` ve `data/tv2/BTCUSDT_12h.parquet` bu checkout'ta yoktu; SPY için yalnız Kasım 2023 sonrası mevcut `data/hourly/SPY.parquet`ten günlük kapanış vekili üretilebildi. Bu nedenle liderin tam SPY/BTC regresyonunu birebir doğruladığımı söylemiyorum.

Karar bütünüyle içime sinmiyor: küçük, kuralları sabitlenmiş paper denemesini destekliyorum; kanıtlanmış alfa portföyü iddiasını desteklemiyorum. Denetim, ilk dalgayı değiştiren bir tarih kısıtı, QCkIgf3z mutabakatını çözen payda farkı ve kripto çeşitlendirmesi iddiasını zayıflatan rejim bağımlılığı buldu.

### D1 — doğrulandı; B kararı bütün tek-enstrümanlara eşit uygulanmalı

Doğru pencere veri başlangıcı ile sürüm tarihinin geç olanından veri sonuna kadardır. JSON tarihleriyle `G4RNcGXg` 89 işlem ve yılda **30,64** işleme ulaşır; `hWvuZJN1` 25,82, `oZYSB6Ui` 20,66, `PZ5MpxP1` 12,39 ve `WfaaCqaN` 12,05'tir. Bu nedenle kullanıcı kuralı güçlü/zayıf etiketinden bağımsız bütün tek-enstrüman adaylara uygulanmalı: `G4RNcGXg` kalır, diğer dördü ilk dalgadan çıkar.

30,64 eşik üzerinde olmak güçlü kanıt değildir; pencere ve sürüm sabitlenmeli, sonraki küçük değişimler otomatik kitap değiştirmemelidir. Daha önce çıkarılmış `CSGmHoik`, `xXrbltSH`, `jn1rXKpM`, `MNBZqC72` doğru yıllık frekansla eşiği geçse de yalnız 6–25 işlemden yıllıklandırılır; geri alınmalarını önermiyorum.

### D2 — piyasa bağımlılığı gerçek; “güçlü alfa” hükmü fazla ileri

Ham yıllık ortalamalar liderin tablosuyla yuvarlama düzeyinde uyumludur. Saatlik SPY arşivinden günlük kapanış vekiliyle ortak Kasım 2023 sonrası dönemde `G4RNcGXg`nin ham getirisi %4,68, piyasa bileşeni %2,58, sabit terimi %2,10 ve HAC(20) t'si 1,34'tür; getiri günlerinde SPY korelasyonu **0,873**tür. “Zamanlı SPY” yorumu yerindedir.

Ancak seçilmiş adaylarda t≥2, kanıtlanmış alfa değildir: yerelde 933 TV-2 satırı (96 geçen) ve U7'de 119 satır (85 geçen) vardır; önce kazanan seçilip sonra alfa t'si yorumlanmaktadır. Sağlam standart hata çoklu-deneme sorununu çözmez. “Nominal t yaklaşık 2” denebilir, “alfa güçlü biçimde kanıtlandı” denmemelidir.

`wcegMOXj` lider regresyonunda sürüm öncesi veri karışmıştır: liderin %1,9 değeri 2023 başından itibaren seriye uyar; doğrulanmış sürüm tarihi 2023-08-05, sürüm sonrası yıllık günlük ortalama yaklaşık **%2,446**dır. BTC verisi eksik olduğundan doğru penceredeki alfa/t yeniden üretilmelidir. ETHBTC'nin düşük BTC korelasyonu da dolar bazında korunma kanıtı değildir; hesap para birimi ve BTC teminatının dolar dönüşümü belirlenmelidir.

### D3 — QCkIgf3z ayrışması açıklanıyor

`backtests/tv2.py` iki ayrı paydayı raporlar: kapanmış işlemlerin neti başlangıç sermayesine, günlük seri ise dönem başı özkaynağına göre yüzdeseldir. `QCkIgf3z` için sürüm öncesi özkaynak/başlangıç sermayesi **4,694776**, sürüm sonrası günlük bileşik **%4,814180**; çarpımları **%22,601495** olup JSON `uyg_sinama_net_yuzde` ile birebirdir. Önceki “açıklanamayan hesap hatası” gerekçesini geri çekiyorum.

Bu aday perpetual değildir: yazar sembolü `COINBASE:ETHUSD`, veri `Binance ETHUSDT 15m`dir. Borsa ve USD/USDT dolum farkı doğrulanmadan küçük keşif yedeği dışında rol verilmemelidir. `G4RNcGXg`, `wcegMOXj` ve `yhoK9cH4`deki küçük kalıntılar da günlük yeniden örnekleme diye kapatılmamalı; ilk gün, dönem sınırını aşan işlemler ve açık pozisyon değerlemesiyle ayrıştırılmalıdır. `9u8pzF0I` için de dönem başı özkaynak başlangıcın yaklaşık 19,504 katıdır; günlük seri %27,889 başlangıç sermayesine çevrilince yaklaşık %543,948 olur ve JSON %541,422'ye yaklaşır. Kalan kontrat/tick sorunu nedeniyle beklemede kalmalıdır.

### Atlanan somut hata: TV-IMKs0OPw

`docs/spec/TV-IMKs0OPw.yaml` kartı 2025-01-01 bitişli tanımlar; günlük seride son sıfır olmayan getiri 2025-02-13'tür ve 2026 tamamen sıfırdır. Sadık sürüm bugün yeni giriş üretemez. İlk dalgadan çıkarılmalı; bitiş tarihini uzatmak yeni varyanttır. Yerine 79 etkin hafta, 3x PF 1,69 ve `TV-dpkq3n4O` ile 0,183 korelasyonu bulunan `TV-70PkIvTL` alınabilir.

### Rejim bağımlılığı ve süreç sınırları

Kripto getirileri 2023–24'te yoğunlaşır: `TV-71yKm18B` 2023 %23,46 / 2024 %24,22; `TV-3BXWqwnF` %47,23 / %11,37; U4-H2 kripto %22,64 / %4,71 üretmiştir. 2025→ bileşikleri sırasıyla %1,73, %0,48 ve %0,97'dir. Bu, 2023–24 başarısını süreklilik varsayımıyla ileri taşımayı desteklemez.

U4-H2 kriptoyu çekirdekte tutmaya katılmıyorum: `TV-3BXWqwnF` ile tüm dönem korelasyonu 0,5395 olsa da 2023'te 0,9084, 2025'te 0,7888 ve 2026'da 0,7520'dir. Ayrıca yalnız 38 etkin haftası ve en büyük bileşenden %48,5 kâr payı vardır. Gölge/yedek olmalıdır.

Ek sınırlar: 2026 büyük şirket evreni survivorship yanlılığı taşır; U7 sonuçları `tarih_belirsiz`dir; `backtests/u7_ozet.py` eski ailelerde geriye dönük nedensellik denetimi bulunmadığını açıkça söyler. Çeviri testini tamamlanmış Adım 0 denetimi yerine koyamayız. Pozitif netle havuzu daraltıp aynı dönemde p10/alfa seçmek bağımsız doğrulama yaratmaz. Ortak ölçek kodunun tüm serilerde √365 kullanması, hisse serilerinde %10 yerine yaklaşık %8,31 gerçek yıllık oynaklığa karşılık gelir.

### Liderin dört önerisi

1. U4-H3 ABD'nin yedek, `TV-dpkq3n4O`nun ilk dalga olması: **katılıyorum**; bunun bağımsız portföy üstünlüğü testi olmadığını koruyorum.
2. `G4RNcGXg` küçük boyutla kalsın: **katılıyorum**; B koşulunu geçiyor, fakat SPY yön riski olarak bütçelenmeli.
3. U4-H2 kripto küçük de olsa çekirdek kalsın: **katılmıyorum**; rejim bazında yüksek korelasyon ve yoğunlaşma nedeniyle gölge/yedek olmalı.
4. Beta tavanı ve 200 günlük ortalama altında girişleri yarıya indirme: **ilkesine katılıyorum**, fakat kanıtlanmış iyileştirme değildir. Önceki kapanışa göre yalnız yeni uzun yön riskini artıran girişlere uygulanmalı; koruyucu pozisyonları otomatik küçültmemelidir.

### Koşullu ilk dalga: 11 aday

| Alan | Aday | Rol |
|---|---|---|
| ABD | TV-zoY9DmsF | İlk ABD temsilcisi. |
| ABD | TV-DUCODGjC | Geniş örneklem; maliyet marjı izlenecek. |
| ABD | TV-dpkq3n4O | U4-H3 ABD'nin yerine. |
| ABD | TV-70PkIvTL | Tarih sınırı dolmuş IMKs0OPw'nin yerine. |
| ABD | G4RNcGXg | Küçük, doğrudan SPY yön riski. |
| Kripto | TV-71yKm18B | Ana kripto temsilcisi. |
| Kripto | TV-3BXWqwnF | 71y ile ortak bütçeden daha küçük. |
| Kripto | wcegMOXj | Para birimi/teminat mutabakatıyla küçük ETHBTC denemesi. |
| Emtia | TV-KO7Qe4Xb | Ana emtia temsilcisi. |
| Emtia | U4-H3:EMTIA:1D | Küçük ikincil temsilci. |
| Keşif | yhoK9cH4 | Çok küçük keşif bütçesi. |

`TV-oF6FmwfR`, `TV-egTb7TgJ`, `TV-Q9OQye4C`, U4-H2 kripto ve U4-H3 ABD yedekte kalır. `TV-oF6FmwfR`–`TV-3BXWqwnF` korelasyonu 0,702'dir. Sayısal mutabakatı sağlanan `QCkIgf3z`, borsa/parite ve uygulama kontrolleri sonrası keşif yedeği olarak yeniden değerlendirilir; `BR74LOKo`/`zuEOEYPK` perpetual, `9u8pzF0I` kontrat ve özkaynak mutabakatı bekler.

### Risk ve uygulama kuralları

- Toplam yıllık oynaklık tavanı yaklaşık %6: ABD %35, kripto %30, emtia %20, keşif %5, boş %10; bunlar sermaye değil risk bütçesi payıdır ve tamamı kullanılmak zorunda değildir.
- Her kitap 5.000 USD sanal sermayeyle izlenir; miktar doğru takvimde ölçülen risk, uygulanabilir notional ve teminat sınırıyla belirlenir. Düşük geçmiş oynaklık sınırsız kaldıraç gerekçesi değildir.
- Aynı sembol/yöndeki pozisyonlar toplanır; en çok üç kitap sınırı korunur. Günlük korelasyon >0,6 olan çiftlere eşzamanlı bağımsız tam bütçe verilmez; haftalık ve son 90 günlük korelasyon uyarıdır.
- SPY/BTC beta tavanı risk açılmadan sayısal olarak kayda geçirilmeli; önceki kapanış 200 günlük ortalama altındaysa yeni uzun yön riski yarıya iner.
- Kitap %10 kayıpta durur; sermaye girişlerinden arındırılmış portföy özkaynağı zirveden %5 gerilerse yeni girişler durur ve mutabakat incelenir.
- Riskten önce sürüm/kaynak sabitlenmeli; ilgili U7 adaylarında Adım 0 nedensellik/dolum denetimi, hesap para birimi, miktar, maliyet ve günlük özkaynak mutabakatı tamamlanmalıdır.

İçime sinmeyenler: U7'nin tamamlanmamış Adım 0 denetimi, kriptonun 2023–24 bağımlılığı, ETHBTC'nin dolar bazında risk tanımı ve kısa META örneklemidir. Bu listeyi küçük öğrenme denemesi olarak destekliyorum; bunlar çözülmeden paper'a hazır, alfa doğrulanmış portföy demiyorum.

## Lider: Sol denetimine cevap ve ORTAK NİHAİ KARAR

Doğruladım:
- **TV-IMKs0OPw ölü strateji:** yazar kodunda tarih filtresi 2020-01-01..2025-01-01; son işlem 2025-02-13. Benim denetimimde atlanmıştı. Bütün 99 aday tarandı: bitiş tarihi geçmiş başka aday yok (o9qty0BL 2026-09-25 ama zaten çıkmıştı); 2026-06'dan beri sessiz başka aday yok.
- **Kripto rejim bağımlılığı:** 71yKm18B 2023 %23,5 / 2024 %24,2 / 2025 **−6,7** / 2026 %9,1; 3BXWqwnF %47,2 / %11,4 / **−2,9** / %3,5. ABD ve emtia adayları yıllara daha dengeli dağılıyor.
- **U4-H2 kripto:** Sol haklı (2023'te 3BXWqwnF ile 0,91 korelasyon, 38 etkin hafta, kârın %48,5'i tek bileşenden) → gölge.
- **QCkIgf3z:** payda farkı açıklaması doğru; "hesap hatası" gerekçemi de geri çekiyorum. Borsa/parite (Coinbase ETHUSD ↔ Binance ETHUSDT) kontrolüne kadar keşif yedeği.
- t ≥ 2 için "kanıtlanmış alfa" demiyoruz; seçilmiş adaylarda nominal t'dir. Kabul.

### Ortak nihai karar (lider + Sol 6.1)
**Kullanıcı B kararı:** "yılda 30 işlem" kuralı güçlü/zayıf ayırmadan bütün tek-enstrüman adaylara uygulanır → G4RNcGXg (30,6) kalır; hWvuZJN1, oZYSB6Ui, PZ5MpxP1, WfaaCqaN çıkar.

**İlk dalga — risk alan 11 kitap**
| Alan | Kitap |
|---|---|
| ABD (5) | TV-zoY9DmsF, TV-DUCODGjC, TV-dpkq3n4O, TV-70PkIvTL, G4RNcGXg (küçük) |
| Kripto (3) | TV-71yKm18B, TV-3BXWqwnF (daha küçük), wcegMOXj (küçük, para birimi/teminat mutabakatıyla) |
| Emtia (2) | TV-KO7Qe4Xb, U4-H3:EMTIA:1D (küçük) |
| Keşif (1) | yhoK9cH4 (çok küçük) |

**Gölge — paper'da izlenir, risk bütçesine sayılmaz (3, hepsi kripto):** TV-egTb7TgJ, TV-Q9OQye4C, U4-H2:KRIPTO25:1D
**Yedek:** TV-oF6FmwfR, TV-jc2hs2qK, U4-H3:ABD25:1D · **Bekleme:** QCkIgf3z (borsa/parite), BR74LOKo / zuEOEYPK (gerçek perp + funding), 9u8pzF0I (kontrat) · **Çıktı:** TV-IMKs0OPw (ölü).

**Risk kuralları:** toplam yıllık oynaklık ~%6 (ABD %35, kripto %30, emtia %20, keşif %5, boş %10); kitap %10 kayıpta durur; portföy zirveden %5 gerilerse yeni giriş durur; korelasyonu > 0,6 çiftlere eşzamanlı tam bütçe yok; SPY/BTC 200 günlük ortalama altındayken yeni **uzun** risk yarıya iner; SPY ve BTC betası kayda geçirilir.

**Paper'dan önce zorunlu (Sol'un şartları):** ilk dalgadaki U7 kitapları için Adım 0 nedensellik/dolum denetimi; sürüm ve kaynak dondurma; hesap para birimi, miktar ve günlük özkaynak mutabakatı; ortak ölçekte hisse serilerinde √365 yerine √252.

**İçimize sindi mi:** küçük, kuralları önceden sabitlenmiş bir **öğrenme denemesi** olarak evet. "Alfası kanıtlanmış portföy" olarak hayır: 2023-26 yükseliş dönemi, seçim yanlılığı ve kripto 2025 zayıflığı bunu söyletmiyor. Asıl karar paper sonuçlarıyla verilecek.
