# Hyperliquid Gölge Kopya Araştırması — Dürüst Değerlendirme

**Tarih:** 29 Ekim 2026  
**Kapsam:** Gerçek para yok; yalnızca sanal/gölge kopya. Amaç, kopyalamaya değer trader seçmenin mümkün olup olmadığını ölçmek.  
**Not:** Bu dosya, sohbet içinde verilen değerlendirmenin tam ve indirilebilir sürümüdür. Değer/maliyet tahminleri, kod tabanı bilinmeden verilmiş kaba değerlendirmelerdir.

---

## İçindekiler

0. Kısa teşhis
1. Fikir tablosu
2. İlk 3 öncelik ve neden
3. "Kâra bakarak trader değiştirme" tuzağı
4. Listede olmayan 3 fikir
5. Az örnekle dürüst karar
6. Kaynaklar

---

## 0) Kısa teşhis: sorun istatistik değil, tasarımın kendisi

- **12 haftalık test, "kopyalamaya değer trader var mı?" sorusunu değil, "çok büyük bir fark var mı?" sorusunu yanıtlayabilir.** Sizin simülasyonunuz bunu zaten söylüyor: %50/yıl farkta ~%20 güç, 12 haftada saptanabilir en küçük fark ~%150/yıl. Bu, testin değil, örneklem ve sürenin sonucu.
- **Odayı performansa göre değiştirme serbestliği, bu zayıf testi daha da zayıflatır.** Aynı veride hem seçim yapıp hem değerlendirirseniz, "kararlarım değer kattı mı?" sorusu cevaplanamaz hale gelir; buna veri gözetleme ve çoklu test sorunu denir.
- **18 + 18 + 18 + 8 = 62, sizde 61 yazıyor.** Ya bir trader iki kolda, ya sayı güncel değil. Kollar birbirinden tamamen ayrı değilse karşılaştırma kirlenir; önce bunu netleştirin.
- **Lider tablosu PnL/ROI'ye göre sıralanmış bir evren** [6]. Bu, hayatta kalan ve yüksek PnL'li hesapları öne çıkarır; "48 bin bağımsız trader" varsayımı kanıtlanmalı.
- **API geçmişi sınırlı:** `userFills` en son 2.000, `userFillsByTime` yalnızca en son 10.000 fill'i veriyor [1]. Yüksek frekanslı bir trader'ın 10.000 fill'i birkaç günü kapsayabilir; 6–12 aylık geçmişi bu API'den kuramazsınız.
- **Kopya maliyeti hafife alınmamalı:** perp taker tabanı %0,045, spot taker tabanı %0,070 [4]; funding saatlik ve saatlik %4'e kadar çıkabiliyor [5]. 30 dakika gecikmeyle maker/HFT stratejilerini kopyalamak çoğu zaman matematiksel olarak imkânsızdır.

### Kapı hakkında 6 sert not

1. **BTC betası düzeltmesi tek başına yetmez.** Trader'lar altcoin, ETH, sektör ve momentum betası taşıyorsa, BTC'ye göre arındırılmış "alfa" bu riskleri içinde tutar. En az BTC + ETH + geniş altcoin sepeti ile düzeltin.
2. **Maliyet modeli taker + kayma + funding olmalı.** Kopya emirleri büyük olasılıkla taker'dır; maker rebate varsaymayın. Funding'i saatlik tahakkuk ettirin [5].
3. **Kaldıraç anlık değil, zaman içi gerçekleşen olmalı.** `clearinghouseState` anlık kaldıraç ve pozisyon değerini verir [2]; medyan/maks kaldıraç için günlük seri tutun.
4. **Fills geçmişi kısa olduğu için seçim penceresi de kısa kalabilir.** HFT'de 10.000 fill birkaç günse, "6 aylık iyi trader" seçimi yanlış kişiyi seçer [1].
5. **Plasebo, rastgele trader değil, aynı seçim prosedürünün plasebo veride çalıştırılması olmalı.** Aksi halde "oda rastgeleden iyi mi?" test edersiniz; "benim seçim kuralım katma değer katıyor mu?" test etmezsiniz.
6. **Eşleştirme değişkenlerini yazın.** Kontrolü geçmiş performansla eşleştirdiyseniz kontrol de seçilmiş olur; fark, eşleştirme değişkenlerinden gelebilir.

---

## 1) Fikir tablosu

Değer ve maliyetler benim kaba değerlendirmem; kod tabanınızı bilmeden verdiğim tahminlerdir.

| # | Fikir | Değer | Maliyet / zorluk | İstatistiksel risk | Tek cümle gerekçe |
|---:|---|---|---|---|---|
| 1 | **Spot odası** | Orta (uzun vade), düşük (şimdi) | Orta-yüksek | Orta-yüksek: yeni evren, çoklu test, likidite | Spot'un fee/funding/likidite yapısı farklı [4]; perp alfası spot'a aynen taşınmaz, ayrı ürün hattı pilotu böler. |
| 2 | **Kaldıraç odaları** (atak/dengeli/temkinli) | Orta | Düşük-orta | Orta: kaldıraç içsel, survivor yanlılığı | Risk bütçesini ayırmak mantıklı; ama "yüksek kaldıraç = yüksek getiri" avına dönüşürse yanıltır, gerçekleşen marjla ölçün [2]. |
| 3 | **Performans pencereleri** (1h, 1a, 1–3, 3–6, 6–12 ay) | Orta (iyi araştırma sorusu) | Düşük (arşiv varsa) | **Yüksek: 5 horizon × kurallar = çoklu test; kısa pencere gürültü** | "Hangi geçmiş horizon öngörür?" değerli bir soru; ama beş ayrı oda kurarsanız hangisinin şans olduğunu bilemezsiniz. |
| 4 | **Operasyon/mutabakat** (yetim pozisyon, kopya ↔ trader sağlaması) | **Yüksek (kritik)** | Orta | Düşük (istatistiksel değil, veri kalitesi) | Yetim pozisyon, çift sayım, eksik fill, yanlış fee/funding varsa tüm alfa hesabı çöp olur; önce ölçümü doğrulayın. |
| 5 | **Futbol takımı modeli** (ilk 11, yedek, U19, U16) | Orta (operasyon), düşük (araştırma) | Orta | **Yüksek: performansla terfi/düşme = gürültü kovalamak** | Metafor iyi; ama terfi/düşme getiriye bağlanırsa 2–3 haftalık şansı "yetenek" sanırsınız, sadece risk ihlali ve veri kalitesiyle düşürün. |
| 6 | **Panoyu sadeleştirme** | Yüksek (operasyonel) | Düşük | Düşük (karar kuralı değişmiyorsa) | Telefondan bakıyorsanız kalabalık ekran karar kalitesini düşürür; ama sadeleştirme belirsizliği gizlememeli. |
| 7 | **Karantina** (payı %50 indir, 2–4 hafta izle) | Orta (risk bazlı), düşük (getiri bazlı) | Düşük | **Yüksek: drawdown tetikliyse performans kovalamak; az olay** | Risk azaltma olarak iyi; tetik "kötü getiri" değil, önceden tanımlı risk ihlali olmalı. |
| 8 | **Tarz kayması tespiti** (sıklık, evren, yön asimetrisi) | Yüksek | Orta | Orta: yanlış alarm, çoklu test | Strateji değişirse geçmiş alfa anlamsızlaşır; CUSUM benzeri önceden eşikli izleme, getiriye dokunmadan yapılabilir [20]. |
| 9 | **Günlük kayıp soğuması** (24 saat kopyalamama) | Düşük-orta | Düşük | **Yüksek: tek gün gürültü; az olay; beta** | Sigorta gibi görünür ama 12 haftada test edilemez; kural olarak konabilir, "kanıt" olarak sunulamaz. |
| 10 | **Lider tablosu dışı keşif** | Yüksek (uzun vade), düşük (kısa vade) | Yüksek (on-chain tarama, kimlik, API) | Orta-yüksek: survivor, sybil, wash | 48 bin tablo PnL'ye göre seçilmiş [6]; gerçek yetenek havuzu dışarıda olabilir ama keşif maliyeti ve gürültüsü yüksek. |
| 11 | **Paralel deney** (aynı arşivde farklı kurallar) | **Yüksek (en iyi fikir)** | Orta | Orta: izlerken çoklu test, ortak veri | Pilotu bozmadan kuralları yarıştırmak doğru; ama her kuralı önceden kaydedin ve tek bir holdout'ta doğrulayın. |
| 12 | **Alternatif seçim kuralları** (Calmar, anti-martingale, DSR, kapasite) | Yüksek (özellikle DSR + kapasite) | Orta-yüksek | **Yüksek: Calmar kısa vadede gürültülü; DSR yanlış trial sayısıyla yanıltıcı** | Calmar/anti-martingale iyi bir risk filtresi, DSR iyi bir çoklu test muhasebesi, kapasite gerçek kopyalanabilirlik; üçünü aynı anda "seçim" yapmak overfit'tir. |

---

## 2) İlk 3 öncelik ve neden

### 1. Öncelik: #4 Operasyon/mutabakat + veri soy ağacı

**Neden:** Bütün istatistik, verinin doğru olduğu varsayımına dayanır. Yetim pozisyon, çift sayılmış fill, yanlış yönlendirilmiş spot sembolü (`@107` vs `HYPE`), eksik funding veya yanlış fee varsa, oda–kontrol farkı "seçim yeteneği" değil "muhasebe hatası" ölçer.

**Ne yapmalı:** Ham API cevabını zaman damgasıyla saklayın; ham → normalize fill → pozisyon → PnL zincirini versiyonlayın; her gün kopya pozisyonu ile trader pozisyonunu karşılaştırın; fark varsa alarm üretin.

### 2. Öncelik: #11 Paralel deney + ön kayıt/deneme defteri

**Neden:** Bu liste içindeki en iyi fikir. Pilotu bozmadan farklı seçim ve maliyet kurallarını yan yana test etmenizi sağlar. Ama ön kayıt olmadan yaparsanız, sonuçlara bakıp kural seçersiniz; bu da tam olarak kaçınmak istediğiniz veri gözetleme sorunudur [17].

**Ne yapmalı:** Her kural için tarih, hipotez, veri kesiti, eşik ve sonucu tek bir "deneme defterine" yazın. Bu defter, Deflated Sharpe için gereken "kaç deneme yaptım?" sayısının girdisidir [11]. Ön kayıt için OSF/COS gibi bir zaman damgası kullanabilirsiniz [25].

### 3. Öncelik: #8 Tarz kayması + #7'yi risk tetikleyicisi yapmak

**Neden:** Kopyaladığınız trader'ın stratejisi değişirse, geçmiş alfa bilgisi anlamsızlaşır. Bu, getiriye bakmadan yakalanabilecek bir risktir. #7 karantinayı getiriyle tetiklerse #5 tuzağına düşersiniz; tarz kaymasıyla tetiklerse risk yönetimi olur.

**Ne yapmalı:** İşlem sıklığı, varlık evreni, yön asimetrisi, maker/taker oranı ve pozisyon tutma süresi için önceden eşik koyun; CUSUM benzeri bir değişim tespiti kullanın [20]. Eşik aşılınca trader'ı "kötü" diye değil, "artık aynı strateji değil" diye karantinaya alın.

### Tamamlayanlar ve çakışanlar

| Kombinasyon | İlişki | Neden |
|---|---|---|
| **#4 + #11** | Tamamlar | Temiz veri olmadan paralel kurallar yanlış karşılaştırma yapar. |
| **#11 + #3 / #12** | Tamamlar | Farklı pencereler ve kurallar aynı pilotta yan yana test edilir; ama ön kayıt ve holdout şart. |
| **#8 + #7** | Tamamlar | Tarz kayması, karantina için meşru bir risk tetikleyicisi olur. |
| **#5 + #3** | Çakışır | İkisi de performansla terfi/düşürmeyi teşvik eder; çoklu test ve gürültüyü artırır. |
| **#2 + #5** | Çakışır | Kaldıraç kovaları + terfi/düşme = karşılaştırma sayısı patlar. |
| **#1 + #3** | Çakışır | Spot/perp + horizon = yeni evren ve yeni testler; pilotu böler. |
| **#10 + #12** | Çakışır | Evreni büyütüp kural sayısını artırmak, çoklu testi kontrol edilemez yapar. |
| **#7 + #9** | Kısmen çakışır | İki ayrı devre kesici; aynı anda koyarsanız hangisinin işe yaradığını bilemezsiniz. |
| **#6 + hepsi** | Tamamlar | Karar yüzeyini sadeleştirir; ama belirsizliği gizlememeli. |

---

## 3) "Kâra bakarak trader değiştirme" tuzağı

### Yüksek riskli fikirler

- **#3 Performans pencereleri:** Özellikle 1 hafta ve 1 ay. Kısa pencere, yetenekten çok şansı ölçer.
- **#5 Futbol takımı modeli:** Terfi/düşme getiriye bağlanırsa, her iyi 2 hafta "yükselme", her kötü 2 hafta "düşme" olur.
- **#7 Karantina:** Drawdown veya kötü getiriyle tetiklenirse, zarardan sonra satmak gibi çalışır; bu bir yatırım stratejisi olabilir ama "trader seçimi" değildir.
- **#9 Günlük kayıp soğuması:** Tek günlük kayıp çoğu zaman piyasa betasıdır; 24 saat durmak sizi alfadan değil betadan korur, ama bunu "yetenek testi" sanmayın.
- **#12a Calmar / #12b anti-martingale:** Sıralama kuralı olarak kullanılırsa yine geçmiş performansa dayalı seçim olur; kısa vadede maksimum düşüş tek bir olaya bağlıdır.
- **#2 Kaldıraç odaları:** Bütçeyi son 1 ayın iyi getirisine göre kovalar arasında kaydırırsanız, performans kovalamış olursunuz.
- **#10 Lider tablosu dışı keşif:** Yeni trader'ları yine PnL'ye göre seçerseniz, aynı tuzağın daha büyük evrende tekrarı olur.

### Orta riskli

- **#1 Spot odası:** Spot/perp arasında "hangisi iyi gidiyorsa" rotasyon yaparsanız performans kovalamış olursunuz.
- **#8 Tarz kayması:** "Kayma"yı getiri düşüşü olarak tanımlarsanız, risk göstergesi değil performans göstergesi olur.
- **#11 Paralel deney:** Kuralları sonuçlara bakarak seçerseniz, deney değil veri avı olur.

### Düşük riskli

- **#4 Operasyon/mutabakat**
- **#6 Pano sadeleştirme** (pano PnL sıralamasını öne çıkarıp sürekli trader değiştirme baskısı yaratmadığı sürece)

### Nasıl önlerim: 10 kural

1. **İki karar türünü ayırın:** Uygunluk/risk kararları hızlı ve kural bazlı olabilir; performans kararları yavaş ve kanıt bazlı olmalı.
2. **Oda değişikliği için meşru gerekçeleri sınırlayın:** trader durdu, kaldıraç/likidite limiti ihlal etti, veri kalitesi bozuldu, tarz kayması oldu, kapasite yetmiyor. "Kötü getiri" bunlardan biri değil.
3. **Performansla değişecekseniz trader'ı değil politikayı test edin:** "Her 4 haftada en kötü %10'u at" gibi bir kuralı önceden tanımlayın; sonra bu kuralın kendisini placebo ve holdout ile değerlendirin.
4. **Sabit referans kolu koruyun:** İlk oda + kontrol. "Kararlarım değer kattı mı?" sorusunun tek dürüst kıyası budur.
5. **Holdout ayırın:** Karar verdiğiniz dönemi doğrulama için ayırın; aynı veride hem seçip hem test etmeyin.
6. **Deneme defteri tutun:** Her kural, her bakış, her deneme kayıtlı olsun. DSR'nin anlamlı olması için trial sayısı gerekir [11].
7. **Plasebo/randomizasyon çıkarımı kullanın:** Aynı seçim prosedürünü plasebo veride çalıştırın; gerçek oda, placebo dağılımının içindeyse "beceri" demeyin.
8. **Minimum kanıt eşiği koyun:** "2 hafta iyi" yetmez; posterior olasılık veya güven aralığı eşiği kullanın.
9. **"Ne görürsem fikrimi değiştiririm"i önceden yazın:** Eşik, yön, test ve karar kuralı önceden yazılı olsun; sonradan "aslında şu alt gruba bakmalıydım" demeyin.
10. **Panoda "karar yok" seçeneğini görünür yapın:** Her hafta aksiyon alma baskısı, performans kovalamayı körükler. Bazen doğru karar hiçbir şey yapmamaktır.

---

## 4) Listede olmayan ama olması gereken 3 fikir

### 1. Ön kayıt + deneme defteri + plasebo seti (yönetişim katmanı)

**Neden kritik:** Kaç strateji denediğinizi bilmeden Deflated Sharpe hesaplanamaz; DSR'nin girdisi "denenen bağımsız deneme sayısı"dır [9][10][11]. Şu anda fikir listesi 12 madde ama pratikte her hafta yeni bir eşik, yeni bir pencere, yeni bir ağırlık deniyorsunuz. Bu sayı kaydedilmezse, "şansı eledim" iddiası kanıtsız kalır.

**Nasıl yapılır:**
- İki sayfalık protokol: soru, ana ölçüt, evren, dışlama kuralları, maliyet modeli, eşleştirme, durma kuralı, karar eşikleri.
- Zaman damgalı ön kayıt (OSF/COS gibi) [25].
- Basit bir CSV "deneme defteri": tarih, hipotez, kural, veri kesiti, sonuç.
- Plasebo seti: rastgele oda, aynı seçim prosedürünün plasebo veride çalıştırılması, ters kopya, gecikmeli kopya.

**Kanıt:** DSR, çoklu deneme ve seçim yanlılığını cezalandırır; ancak doğru trial sayısı ve Sharpe dağılımı verilirse [9][10]. Çoklu testin genel mantığı için Harvey ve arkadaşları, yeni faktörlerde t>3 eşiğini tartışıyor [12].

### 2. Kopyalanabilirlik simülatörü + strateji sınıflandırması

**Neden kritik:** "İyi trader" ile "kopyalanabilir trader" aynı şey değil. 30 dakika/2 saat gecikmeyle maker, HFT veya çok hızlı momentum stratejilerini kopyalamak çoğu zaman imkânsız. Kapı "maliyet sonrası kopya getirisi" hesaplıyor olabilir; ama bu hesabın gerçekçi olup olmadığı, emir defteri ve gecikme varsayımına bağlı.

**Nasıl yapılır:**
- Lider fill'ini gördükten sonra kopyayı bir sonraki 30 dk/2 saat barının açılışında yapın.
- Taker fee + kayma + saatlik funding + kısmi dolum ekleyin [4][5].
- Strateji sınıflandırması: `crossed` alanı taker/maker ayrımı verir; `dir` ve `startPosition` pozisyon değişimini; `fee` gerçek maliyeti gösterir [1].
- Kapasite: günlük hacim, emir defteri derinliği ve impact fiyatlarıyla "bu pozisyon benim büyüklüğümde döner mi?" sorusunu yanıtlayın [2].
- Yüksek maker oranı + yüksek fill sıklığı = kopyalanamaz; bunları odadan çıkarın, "kötü" diye değil "kopyalanamaz" diye.

**Kanıt:** Hyperliquid API'si fill'lerde `crossed`, `dir`, `startPosition`, `fee` alanlarını veriyor [1]; funding saatlik ve saatlik %4'e kadar çıkabiliyor [5]; fee tablosu taker/maker ayrımını veriyor [4]. Bu üçü, gerçekçi bir kopya maliyeti için yeterli ham veri sağlar.

### 3. Kimlik + survivorship + point-in-time katmanı

**Neden kritik:** Lider tablosundaki 48 bin hesap, 48 bin bağımsız trader olmayabilir. Bir operatör birden çok subaccount açabilir; Hyperliquid rate limit dokümanı subaccount'ları ayrı kullanıcı sayıyor [3]. Ayrıca deposit/withdrawal, wash/self-trading, delist edilen varlıklar ve cüzdan göçü PnL/ROI'yi bozabilir.

**Nasıl yapılır:**
- Ham lider tablosu ve API cevaplarını zaman damgasıyla saklayın; sonradan düzeltilmiş veriyle geçmişi değerlendirmeyin.
- Subaccount, master account ve vault ilişkilerini haritalayın [3].
- Deposit/withdrawal'ı PnL'den ayırın; ROI'yi time-weighted hesaplayın.
- Wash/self-trading ve anormal volume/PnL oranı için filtre koyun.
- "48 bin hesap = 48 bin bağımsız trader" varsayımını test edin; değilse odanın gerçek çeşitliliği düşer.

**Kanıt:** Rate limit dokümanı subaccount'ların ayrı kullanıcı sayıldığını söylüyor [3]. Lider tablosunun kendisi resmî `info` dokümanında listelenmiyor; pratikte `stats-data.hyperliquid.xyz/Mainnet/leaderboard` kullanılıyor [7][8]. Bu yüzden şema ve kapsam garantili değil; ayrı bir sağlık kontrolü gerekir.

**Doğrulanamadı:** Hyperliquid'e özgü, hakemli bir "kopya ticaretinde lider performansının kalıcılığı" çalışması bulamadım. Klasik fon literatürünü (Carhart [15][16], Barras ve arkadaşları [13][14]) yalnızca uyarı olarak kullanıyorum; kripto için doğrudan kanıt saymıyorum. Ayrıca 48 bin hesabın kaç bağımsız operatör olduğu da **doğrulanamadı**.

---

## 5) Az örnekle (36–61 trader, birkaç ay) anlamlı karar vermenin en dürüst yolu

### Önce kabul edin

36–61 trader ve 3 ayla "hangi trader daha iyi?" sorusuna güvenilir cevap veremezsiniz. Yapabileceğiniz üç şey var:

1. **Büyük negatifleri elemek:** "Bu oda kontrol kadar iyi mi, yoksa büyük zarar mı üretiyor?" sorusu cevaplanabilir.
2. **Karar kuralını test etmek:** "Seçim prosedürüm placebo'dan iyi mi?" sorusu test edilebilir.
3. **Belirsizliği dürüstçe raporlamak:** "Kanıt yok" demek, "yetenek yok" demek değildir.

### Önerdiğim protokol: iki ayrı ray

**Ray A — Keşif (12 hafta):** Oda sabit. Yeni kuralları, pencereleri ve ağırlıkları yalnızca "kum havuzunda" deneyin. Ana odaya dokunmayın. Bu dönemde amaç kanıt üretmek değil, veri kalitesini ve karar kuralını kalibre etmek.

**Ray B — Onay (12 hafta veya 6–12 ay):** Ana oda ve kontrol sabit; önceden kayıtlı tek hipotez; önceden kayıtlı durma kuralı. Onay bitmeden "yetenek" iddiası yok.

Eğer 24 hafta bekleyemiyorsanız, dürüst seçenek testi kısaltmak değil, **soruyu değiştirmektir**: "Kopyalama kârlı mı?" yerine "Bu oda büyük zarar üretiyor mu, veri kalitesi bozuk mu, risk limitleri ihlal ediliyor mu?" sorularına bakın.

### Bayesçi hiyerarşik model (somut)

Haftalık getiriler için:

\[
r_{i,t} = \alpha_i + \beta_i r_{BTC,t} + \gamma_i r_{ETH,t} + \delta_i r_{ALT,t} + \epsilon_{i,t}
\]

\[
\alpha_i \sim N(\mu_\alpha, \tau_\alpha^2), \quad
\mu_\alpha \sim N(0, 0.10^2), \quad
\tau_\alpha \sim \text{HalfNormal}(0.10)
\]

\[
\Delta = \frac{1}{18}\sum_{i \in oda}\alpha_i - \frac{1}{18}\sum_{j \in kontrol}\alpha_j
\]

- **Neden hiyerarşik:** Az verili trader'ın alfası grup ortalamasına doğru çekilir; 3 hafta iyi giden birini "yetenekli" sanmayı engeller. Buna kısmi havuzlama denir [21].
- **Neden şüpheci prior:** \(\mu_\alpha\) sıfır merkezli; veri sizi ikna etmedikçe "yetenek var" demezsiniz. Bu, "hiç yetenek yok" inancı değil, düşük taban oranına saygıdır.
- **Neden çok faktör:** BTC betası tek başına altcoin riskini temizlemez; en az BTC + ETH + geniş altcoin sepeti kullanın. (Bu benim değerlendirmem; Hyperliquid'e özgü faktör modeli kanıtı doğrulanamadı.)
- **Hata dağılımı:** Normal yerine Student-t kullanın; kripto getirileri kalın kuyrukludur.

**Raporlayın:**
- \(P(\Delta > 0)\): oda kontrolün önünde olma olasılığı.
- \(P(\Delta > 0.10)\): yıllık %10'dan fazla fark olasılığı.
- %80 ve %95 güvenilir aralık (credible interval).
- Tek bir "p-değeri" değil, belirsizlik dağılımı.

**Karar kuralı örneği:**
- **Devam:** \(P(\Delta > 0.10) \ge 0.90\) ve risk kontrolleri temiz.
- **Dur:** \(P(\Delta < -0.10) \ge 0.90\).
- **Kanıt yok:** Arada kalan her durum. Odayı değiştirmeyin; yalnızca veri/risk düzeltmesi yapın.

Bu eşikler 12 haftada neredeyse hiç tetiklenmez. Bu bir hata değil; tasarımın dürüst sonucudur.

### Sıralı test: üç bakış, önceden

Her hafta bakıp "posterior 0.95 oldu, duruyorum" demek de seçim yanlılığı yaratır; çünkü durma zamanı veriye bağlıdır. Bunun yerine:

- **3 bakış:** 4., 8. ve 12. hafta.
- **O'Brien–Fleming tipi alfa harcaması:** Erken bakışlarda çok sıkı, son bakışta normale yakın eşik [19].
- **Veya Bayesçi sıralı:** Önceden tanımlı üç bakış ve önceden tanımlı posterior eşikleri; her gün bakmak yok.

SPRT (sıralı olasılık oranı testi) klasik ve güçlüdür, ama getiriler i.i.d. değil; rejim değişimi ve otokorelasyon varken basit SPRT yanıltıcı olur. Bu yüzden grup sıralı veya Bayesçi yaklaşım daha uygun. (Bu benim değerlendirmem.)

### Randomizasyon çıkarımı: en dürüst "seçimim değer kattı mı?" testi

1. Geçmiş arşivde, her karar tarihinde yalnızca o anda bilinen veriyi kullanarak **aynı seçim prosedürünü** çalıştırın.
2. Bu prosedürle 1.000 "plasebo oda" oluşturun.
3. Gerçek odanın dış-örneklem \(\Delta\)'sını bu 1.000 odanın dağılımıyla karşılaştırın.
4. Gerçek oda 95. yüzdelik dilimin üzerindeyse "seçim katma değer kattı" kanıtı var; 60. yüzdelikteyse yok.

Bu yöntem, "oda rastgeleden iyi mi?" değil, "benim seçim prosedürüm rastgele seçimden iyi mi?" sorusunu test eder. Sizin mevcut plasebo testinizden farkı budur.

### Blok bootstrap uyarısı

7 günlük bloklarla 12 hafta = yalnızca 12 blok. Bu, yeniden örnekleme dağılımını çok kaba yapar; ayrıca trader'lar aynı piyasa şokuna maruz olduğu için bağımsızlık varsayımı bozulur [24]. En azından:

- Günlük bloklar + stationary bootstrap deneyin.
- Piyasa gününe göre bloklayın; aynı gün içindeki trader'ları bağımsız saymayın.
- Blok uzunluğu için duyarlılık analizi yapın.
- 12 haftada ne yaparsanız yapın, güven aralıkları geniş kalacak; bunu saklamayın.

### Karar tablosu

| Bulgu | Yorum | Aksiyon |
|---|---|---|
| \(P(\Delta > +10\%/yıl) \ge 0.90\) | Anlamlı pozitif | Devam; ama kapasite ve risk kontrolleri |
| \(P(\Delta < -10\%/yıl) \ge 0.90\) | Anlamlı negatif | Dur |
| Arada | Kanıt yok | Odayı değiştirme; veri/risk düzelt |
| Gerçek oda placebo dağılımının altında | Seçim katma değer katmıyor | Trader'ı değil, seçim kuralını değiştir |

### Ne söyleyebilirsiniz / ne söyleyemezsiniz

| Söyleyebilirsiniz | Söyleyemezsiniz |
|---|---|
| "12 haftada oda ile kontrol arasında büyük bir fark görmedim; belirsizlik geniş." | "Şu trader yetenekli." |
| "Veri kalitesi/risk ihlalleri şurada; şu trader'ı bu yüzden çıkardım." | "Kopyalama genel olarak işe yaramaz." |
| "Bu seçim prosedürü placebo'dan ayrışmadı." | "Kararlarım değer kattı." |
| "Bu örneklemle %150/yıl altındaki farkları ayırt edemem." | "Kanıt yok, o yüzden kesinlikle alfa yok." |

---

## 6) Kaynaklar

Aşağıdaki bağlantılar gerçek; bazı yayıncı sayfaları (SSRN, OUP) botlara 403 verebiliyor, bu linkin sahte olduğu anlamına gelmez.

1. Hyperliquid Info endpoint — fill'ler, mumlar, pozisyon, portföy:  
   https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint
2. Hyperliquid Perpetuals info — `clearinghouseState`, funding, meta:  
   https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals
3. Hyperliquid rate limits — subaccount'lar ayrı kullanıcı, istek ağırlıkları:  
   https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits
4. Hyperliquid fees — perp/spot taker/maker:  
   https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees
5. Hyperliquid funding — saatlik ödeme, saatlik %4 üst sınır:  
   https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding
6. Hyperliquid lider tablosu — ~48 bin hesap, PnL/ROI:  
   https://app.hyperliquid.xyz/leaderboard
7. Alphanet — lider tablosu endpoint'inin resmî dokümanda olmadığı notu:  
   https://alphanet.global/blog/faq/hyperliquid/hyperliquid-leaderboard-api/
8. eth_defi — `stats-data.hyperliquid.xyz/Mainnet/leaderboard` kullanımı:  
   https://web3-ethereum-defi.readthedocs.io/api/hyperliquid/_autosummary_hyperliquid/eth_defi.hyperliquid.api.fetch_leaderboard.html
9. Bailey & López de Prado — Deflated Sharpe Ratio (SSRN):  
   https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
10. Bailey — Deflated Sharpe Ratio PDF:  
    https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
11. Quantdare — DSR özeti; "tüm denemeleri kaydet" vurgusu:  
    https://quantdare.com/deflated-sharpe-ratio-how-to-avoid-been-fooled-by-randomness/
12. Harvey, Liu, Zhu — çoklu test ve t>3 eşiği (NBER):  
    https://www.nber.org/papers/w20592
13. Barras, Scaillet, Wermers — fonlarda sahte keşifler (SSRN):  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=869748
14. Barras ve arkadaşları — aynı çalışmanın açık PDF'i:  
    https://web.mit.edu/econometrics/fdr2version.pdf
15. Carhart — fon performansının kalıcılığı (Wiley):  
    https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1997.tb03808.x
16. Carhart — aynı çalışmanın SSRN kaydı:  
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=8036
17. Gelman & Loken — "garden of forking paths", çoklu karşılaştırma:  
    https://sites.stat.columbia.edu/gelman/research/unpublished/p_hacking.pdf
18. Barnett ve arkadaşları — regression to the mean:  
    https://pubmed.ncbi.nlm.nih.gov/15333621/
19. Ciolino ve arkadaşları — grup sıralı analiz / alfa harcaması:  
    https://pmc.ncbi.nlm.nih.gov/articles/PMC10260346/
20. CUSUM / değişim noktası tespiti — giriş:  
    https://www.lancaster.ac.uk/~romano/teaching/2425MATH337/1_intro_cusum.html
21. Bayesçi hiyerarşik modeller ve kısmi havuzlama:  
    http://seor.vse.gmu.edu/~klaskey/SYST664/Bayes_Unit7.pdf
22. CEPR/VoxEU — kopya ticaret ve risk alma deneyi:  
    https://cepr.org/voxeu/columns/financial-social-trading-networks-case-copy-trading-platforms
23. IOSCO — kopya ticaret üzerine düzenleyici rapor:  
    https://www.iosco.org/library/pubdocs/pdf/IOSCOPD793.pdf
24. Block bootstrap — zaman serisi için blok uzunluğu ve bağımlılık:  
    https://projecteuclid.org/journals/statistical-science/volume-17/issue-1/Bootstraps-for-Time-Series/10.1214/ss/1023798998.pdf
25. Center for Open Science — ön kayıt:  
    https://www.cos.io/initiatives/prereg

**Not:** Hyperliquid'e özgü kopya-trading kalıcılık çalışması, 48 bin hesabın kaç bağımsız operatör olduğu ve lider tablosunun resmî şeması konularında kanıt bulamadım; bunları **doğrulanamadı** olarak işaretledim.
