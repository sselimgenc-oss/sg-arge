# Kopya Trader Pilotu — Dürüst Değerlendirme ve Öncelik Önerisi

*Danışman görüşü — 29 Ekim 2026 — Hyperliquid sanal (gölge) kopya pilotu, v1.3*

---

## 0. Künye

Kurumun (oda + eşleştirilmiş kontrol + taban, plasebo testi, BTC-betası düzeltmesi, 7 günlük blok bootstrap) bir randomize deneyi aratmıyor. Zayıf nokta kurum değil, **istatistiksel güç**: kendi simülasyonun, 12 haftada yıllık bazda ~%150'lik farkı ancak görebileceğini söylüyor. Bu şu demek:

> **"Oda işe yarıyor mu?" sorusu bu sürede büyük olasılıkla cevaplanamayacak.** Buradaki her tartışma bu gerçeğin etrafında dönmeli. Bunun iki dürüst sonucu var:
>
> 1. Kararları getiri kıyasıyla değil, **süreç ve risk kıyasıyla** yapmalısın.
> 2. Katma değerin, tek bir 12 haftalık oda-kontrol testi değil; **kalıcılık (persistence) sorusu** ve **meta-düzeyde seçim sürecinin** ölçülmesidir (Bölüm 5, Katman 4).

Jargonlar (ilkinde açıklanır, sonrakilerde kısaltılır):
- **Güç (power):** gerçek bir fark varken onu yakalama olasılığı. Küçük örnekle güçten, en bariz avantaj bile "kanıt yok" sonucunu doğurur.
- **Aşırı uyum (overfitting):** kuralların geçmişe o kadar iyi oturtulması ki gelecekte tutmaz.
- **Çoklu test:** aynı anda çok hipotez test edince, salt şansla "bulunmuş" sahte bulguların birikmesi.
- **Veri gözetleme (data snooping / peeking):** test sürerken sık sık bakıp erken karar vermek; yanlış-pozitif olasılığını şişirir.
- **Önceden kayıt (pre-registration):** kuralı ve eşikleri uygulamadan *önce* yazılı hale getirme.
- **FDR (False Discovery Rate):** çoklu test yapılırken "anlamlı bulduklarımızın içinde gerçekten gerçek olanların oranı"nı kontrol eden yöntem.
- **DSR (Deflated Sharpe):** çoklu deneme ve normal olmayan getiriler düzeltmesi yapılmış Sharpe oranı.
- **mSPRT / always-valid p-değeri:** sürekli baksa bile yanlış-pozitif olasılığı sabit kalan sıralı test ailesi.
- **Calmar:** getirinin maksimum düşüşe oranı; bir tür düşüş-normalize edilmiş getiri.

---

## 1. Fikir tablosu

Kısaltmalar: **BM** = yeni backend/yetenek alanı gerektirir; **AY** = ağırlıklı kullanıcı zamanı ve karar disiplini gerektirir; **ÖK** = önceden kayıt olmadan yapılırsa risk yüksek.

| # | Fikir | Değer | Maliyet | İstatistiksel risk | Gerekçe (tek cümle) |
|---|---|---|---|---|---|
| 1 | Spot odası | **Düşük** | Orta, BM | **Yüksek**: yeni hipotez, güç daha da bölünür | Spot handikaplar (slipaj, funding yokluğu, kalıcılık) perp'ten farklı; Hyperliquid lider tablosu esasen perp'ye göre yapılandırılmıştır; yeni soru açar ama onu cevaplayacak güç yok |
| 2 | Atak / Dengeli / Temkinli odalar | Orta | Orta–Yüksek, AY | **Yüksek**: 3 oda = 3 test; her odada ~6 kişi → güç neredeyse sıfır | Kaldıraç bandı risk profilini belirlediği için anlamlı bir bölümleme; fakat "oda başına" test edemeyeceğin kadar örnek kaybı; oda sayısını artırmak yerine tek odada kalmayı düşür |
| 3 | Performans pencereleri (1 hafta, 1 ay, 1–3, 3–6, 6–12 ay) | **Yüksek** | Düşük–Orta | Orta: pencere sayısı çoğalırsa veri gözetleme | Projenin asıl bilimsel sorusu ("hangi geçmiş, geleceği söylüyor?") tam olarak bu; ama en fazla 3–5 pencereyle ve **tek bir önceden yazılmış karar kuralıyla** |
| 4 | Operasyon/mutabakat (yetim pozisyon, kopya↔trader sağlaması) | **Yüksek** | Orta, BM | **Sıfır** (temel altyapı) | Mutabakat bozuksa gördüğün farkın ne kadarının gerçek, ne kadarının veri hatası olduğunu ayırt edemezsin; bu olmadan diğer 11 fikir ölçülemez |
| 5 | Futbol takımı modeli (ilk 11 / yedek / U19 / U16) | Orta | Yüksek, AY | **Yüksek**: her terfi/düşürme yeni bir karar noktası; PnL ile terfi = PnL avı | Yapısal olarak güzel ama her seviye geçişi bir "test" ise toplam yanlış-bulma olasılığı hızla birikir; katı önceden kayıt olmadan zararı faydasından fazla |
| 6 | Panoyu sadeleştirme | Orta–Yüksek | **Düşük** | Sıfır | Teknik olmayan kullanıcının panelleri yanlış okuması sessizce kötü karar doğurur; en ucuz risk azaltma işlerinden biri |
| 7 | Karantina (payı %50, 2–4 hafta) | Orta | **Düşük** | Orta: süreyi gözlem sonrası ayarlıyorsan geriye dönük uydurma | Zarar kontrolü sonradan ayarlanmadığı sürece sağlıklı bir "yumuşatma" kuralı; karantinayı performansa göre değil **davranış iyileşmesine göre** bitir |
| 8 | Tarz kayması tespiti | **Yüksek** | Düşük–Orta | **Düşük** (uyarı üretir; PnL'den bağımsız sinyal) | "Geçmişle **davranışı** seçtin; davranış değiştiğinde seçimin geçersizdir" — PnL'den tamamen bağımsız, dolayısıyla temiz bir düşür/donma gerekçesi |
| 9 | Günlük kayıp soğuması | Düşük–Orta | **Düşük** | Orta: kullanılırsa çalkantılı trader'ları sistematik dışarıda bırakır | Tek gün kaybı bilgi olarak zayıftır (olay saatler içinde yaşanır); önceden mühürlü basit kural olarak sorun değil ama getiri beklentisi taşırma |
| 10 | Lider tablosu dışı keşif | Orta | Yüksek, BM | **Yüksek**: evren büyüdükçe test sayısı katlanır; API'nin 10.000 fill sınırı | Evren genişliği iyi ama filtresiz büyüme = hızla kendini ikna eden yeni bir tarama düzlemi; kural seti mühürlendikten sonra düşün |
| 11 | Paralel deney (aynı arşiv, yan yana kurallar) | **Yüksek** | Orta–Yüksek, BM | Orta: yalnız **keşif** etiketli olmalı, asla "kanıt" gibi sunulmamalı | Sınırlı veriden en çok kazanmanın tek dürüst yolu: pilot bozulmadan tüm kural varyantlarını aynı arşiv üzerinde hesapla; çıktısı "deney planı" olsun, liderlik tablosu değil |
| 12 | Alternatif seçim kuralları (a. Calmar, b. anti-martingale disiplin, c. DSR, d. kapasite/aşınma) | **Yüksek** | Orta–Yüksek, BM | Orta: hepsi aynı veri üzerinde "sınav" olursa çoklu test; panzehirleri var (Bölüm 5) | **a (Calmar)** daha düşük varyanslı birincil ölçüt; **b ve d** davranış-türetilmiş, PnL'le ilişkisi zayıf temiz sinyaller; **c (DSR)** çoklu deneme düzeltmesi yapar, tam senin durumun için geliştirildi |

---

## 2. İlk 3 öncelik ve ilişkiler

### Öncelik 1 — #4 Operasyon/mutabakat + veri doğrulama

Ölçüm zincirinde her parça bozuksa (yetim pozisyon, kopya↔trader sağlamasındaki boşluk, 10.000 fill sınırının pencere yarattığı yerler), oda-kontrol farkının ne kadarı gerçek, ne kadarı veri hatası ayırt edilemez. Bu, istatistiğin **ön şartı**. Yan paket olarak **#6 (panoyu sadeleştirme)** ile aynı iş: "kendini yanlış yönlendirmeyi engelleme", neredeyse bedava.

### Öncelik 2 — #3 Performans pencereleri, "kalıcılık" (persistence) sorusu olarak

Projenin ana kırılması şu: literatürde lider-trader performans kalıcılığı zayıf çıkıyor. Bir eToro "popülarite sıçraması" olay çalışması, sıçramadan **önceki** dönemde anormal pozitif getiri bulur ama sonraki dönemde eşleştirilmiş kontrole karşı kalıcı üstünlüğün **kaybolduğunu** gösteriyor (Bölüm 6'daki kaynaklar). Senin pencere-tarama deneyin bu literatüre doğrudan katkı yapabilecek **tek uygun ölçek**.

Kurallar: pencere sayısını 3–5'te tut; pencereleri uygulamadan **önce** yaz; "sonradan en iyi pencereyi seç" **yasak**; her pencere sonucu kayda girecek şekilde.

### Öncelik 3 — #11 Paralel deney

12 haftada tek bir kuralın kararına güç yok; ama aynı arşiv üzerinde onlarca **kural varyantını yan yana** hesaplayabilirsin. Bu, kararları veri-temelli yapar: üçüncü ay görürsün ki "Calmar skoru değişkenin X'i ile ilişkili, anti-martingale skoru hiçbir şey yakalamıyor" — örnek kaybı olmadan, pilot bozulmadan. Riski: bu tarz tarama çıktılarının hepsini **keşif** etiketiyle tutup, resmi test gibi göstermemek. Aksi, "biz zaten böyle demiştik" tuzağını doğurur.

### Tamamlayıcılık / çakışma
- **#3 + #12 + #8 birbirini tamamlıyor:** hepsinin konusu "seçim sinyali geçerli mi?" Bunları **tek bir "sinyal araştırma" bandına** topla.
- **#1, #2, #5 birbirini tekrarlıyor:** üçü de "daha fazla bölüm/oda"; hepsi **güç** sorununun kaçamağı. Bunlardan en fazla birini yap (en anlamlısı #2; o isteniyorsa 3 odadan **2'ye daralt** şeklinde düşün, artırarak değil).
- **#7 + #9 çakışıyor:** ikisi de "süreci yavaşlat"; ikisi de aynı anda aktifken trader'a üst üste müdahale edersin. Biri olsun: #7 (davranışa dayanıyor, PnL'e değil).
- **#10 en tehlikeli çakışma:** evren büyütmek tüm çoklu-test yüklerini katlar; en sona bırak.

---

## 3. "Kâra bakarak trader değiştirme" tuzağı

### Tuzağa düşüren fikirler, şiddet sırasıyla

1. **#5 (terfi/düşürme)** — terfiyi "son 4 haftalık getiri"ye göre yaparsan PnL avını formüle etmiş olursun. Düşürme kararı için PnL kullanılabilir ama asıl gerekçe davranış olsun (kaldıraç ihlali, tarz kayması); terfi için PnL'i **asla** gerekçe yapma.
2. **#7 karantina** — süresi "geçen ay işe yaradı, ~4 hafta yapmaya devam" diye ayarlanırsa, geçmişe uyan bir hamle olur.
3. **#3 pencere seçimi** — "1 aylık pencere en iyi işledi, artık o pencereyi kullanayım" cümlesi kurulduğu an ileri-dönüşümsel (look-ahead) gözlem yapıyorsun.
4. **#12 a/b/d** — skorları "hangisi işe yaradıysa onu seç" şeklinde uygulamak.
5. **#9 soğuma** — zararın ardındaki toparlanmayı (zarardaki trader'ın en iyi dönemleri) otomatik keserse, sessizce zayıf trader'ları dışarıda bırakır.

### Önleyici çerçeve (5 kural)

1. **İki ayrı gerekçe kodu:** `KOD=RISK` (mutabakat hatası, kaldıraç ihlali, tarz kayması, veri problemi, kapasite/aşınma değişimi) vs `KOD=PnL`. Gerçek odaya değişiklik **yalnız `RISK`** ile yapılabilir; `PnL` gerekçeli değişiklik **yalnız paralel deney kolunda** yürütülür.
2. **Değişiklik dondurma penceresi:** kararlaştırılan değişiklik en az 30 gün log'a yazıldıktan sonra uygulanır. Duygusal tepkiyi filtreler.
3. **Sabit referans kolu dokunulmaz:** zaten kur; onu hiçbir sürüm değişikliğiyle karıştırma.
4. **Her değişikliğin Telegram'da "karar fişeri" bas:** alanlar = gerekçe kodu, tarih, hangi kanıt, hangi alternatif düşünüldü, hangi eşiği ihlal etti. Geriye dönük "PnL için mi değiştirdim?" sorusu ölçülebilir hale gelir.
5. **Her değişiklikten sonra "did it help?" ölçümü:** hamle sonrası 30–60 günlük oda performansını, **değişikliği yapmış olmasaydın** ne olacağıyla (kontrafakt: eski oda sanki duruyormuş gibi sanal kopya) karşılaştır. Bunu **paralel deney (#11)** otomatik yapar; bu yüzden #11 en önemli tampon.

---

## 4. Listede olmayan, en önemli 3 fikir

### A. Sağ(kalam)ma / listeye erişim bias'ı ölçümü

Lider tablosu "bugün listede olan" hesapları gösterir: kötü performansa girmiş, kapatılmış, likide olmuş hesaplar listeye ulaşamaz. Senin 48 bin hesaptan süzme sürecin zaten bir selection bias içeriyor. Ölçüm: (i) her tarih noktasında **listeye yeni girenleri** kohort (grup) olarak etiketle; (ii) "listedeki hesap" ile o tarihe **yeni eklenenleri** ayrı izle; (iii) senin seçim kuralını geçmiş bir tarih noktasına, **o günün verisiyle** geriye dönük uygula; "o gün seçilecek olanlar" ile "o güne kadar hayatta kalarak listede olanlar" arasındaki farkı ölç. Bu fark, senin pilotunun **dış geçerlilik** boşluğunu kapatır.

### B. Korelasyon-farkında oda (portföy birleşimi, kümeleme)

18 trader birbirine benziyorsa (aynı gün aynı yöne yakın büyüklükte işlem yapıyorsa), oda etkin olarak **3 bağımsız bahis** değerinde. Bunu düzelmenin iki faydası: (i) etkin örnek boyutu artıyor → güç artıyor; (ii) oda varyansı azalıyor → oda-kontrol farkı testi **hemen** daha ayırt edici oluyor. Kod değişikliği gerektirmeden **istatistiksel güç** kazanmanın gerçek yolu budur. DSR literatürünün mantığı aynı: düzeltme "bağımsız deneme sayısına" bağlıdır; korelasyon yüksekse sayı gerçekte düşüktür.

**Uygulama:** oda üyelerini kümeleme ile düşük-korelasyonlu 3–4 grubun temsilcilerinden kur; aynı gruptan 2'den fazla üye alma.

### C. Karar günlüğü + sürümlenmiş önceden kayıt

Teknik olmayan kullanıcı için uzun vadeli en ciddi tehlike: **kararların gerekçesinin hatırlanamaması.** Sade bir `decisions.md` günlüğü yeterli alanlarla: sürüm, tarih, gerekçe kodu, eşik, hangi kuralın neden değiştiği, ne zaman yeniden incelenecek. Bu, Bölüm 3'teki "önceden kayıt" prensibinin tek gerçek uygulamasıdır.

**(Bonus, 4. sırada) — Birincil ölçütü düşüş tabanlı yap.** 12 haftada getiri farkına güç yetmez ama **maksimum düşüş (MDD: en derin tepe-dip kayıp) gibi risk ölçütleri** daha sık değişir, dolayısıyla daha az örneklem ister: örn. "oda, kontrolle kıyaslandığında aynı pencerede belirgin biçimde daha derin düşüş yaşadıysa, oda riskli kabul edilir" gibi bir kural. Risk tabanlı durdurma kuralları yüksek güçle çalışır; kâr tabanlı terfi kuralları çalışmaz.

---

## 5. Az örneklemde (36–61 trader, birkaç ay) anlam — en dürüst yol

Açık konuşma: MDE (saptanabilir en küçük fark) ~%150/yıl ise, tek başına performansa dayanan karar **yeterince zayıf.** Üç katmanlı yaklaşım öneriyorum.

### Katman 1 — Soruyu küçült: havuzlanmış çıkarım (pooled inference)

Oda ile kontrol kıyasını tek bir "oda ortalaması" testine sıkıştırmak yerine, **18 trader'ın her biri için ayrı** alfa ve kontrol-alfa farkları hesapla; sonra **FDR düzeltmesiyle** sonuçları toparla ve çıkarımı kişiye yay: "18 trader'dan X'i, düzeltme sonrası alfa taşıyor." Tek bir oda-kararı değil, **kişi bazında biriken kanıt**.

### Katman 2 — Bayesçi hiyerarşik model (kısmi havuzlama)

Her trader'ın yeteneğini tek başına tahmin etme; 48 bin hesaplık evrenin "yetenek dağılımından", **kısmi havuzlama (partial pooling: herkesin tahminini evren ortalamasına doğru küçültme)** ile ödünç alarak daha sağlam bir tahmin kur. Sonra:
- Her değişiklik adayı için **posterior olasılık** hesapla: `P(oda_alfa > kontrol_alfa | veri)`.
- **Karar eşikleri önceden yaz:** ör. `P > 0,90 → devam; P < 0,10 → risk denetimi başlat; arası → bekle`.
- Bu eşikler kararı otomatikleştirmez; "karar verilecek kadar kanıt var mı?" sorusunu saydam ve tartışmasız hale getirir.

Posterior yaklaşımı, küçük örneklemde frekansçı testin "kanıt yok" demesinin "henüz karar verilecek kadar bilgi yok" anlamına düştüğünde, **olasılıksal bir soru-cevap** sunar. Bu, senin durumundaki en dürüst cevabın biçimi.

### Katman 3 — Sıralı test (her hafta bakıp karar vermek istediğin senaryo)

Sürekli izlemede klasik p-değeriyle "her hafta bakıp erken karar vermek", yanlış-pozitif olasılığını nominalden kat kat büyütür. Çözüm: **bakma sıklığını hesaba katan sıralı test.** Doğru araç: **always-valid p-değeri** — her hafta baksan bile yanlış-pozitif olasılığı ≤ α kalan sıralı test. Standart varyant: **mSPRT** (Johari-Pekelis-Walsh; Optimizely gibi platformlarda üretim ölçeğinde kullanılıyor).

Bir asimetri önerisi: sıralı testi **zarar tarafında** rahatlat, **başarı tarafında** sıklaştır:
- `α_harm` (zarar tarafı durdurma eşiği) **%1** civarı: kötüye erken tepki verme maliyeti düşük, geri bildirimi hızlı;
- `α_gain` (başarı tarafı eşiği) **%0,1** civarı: yalnız çok güçlü kanıt birikince "başarı" olarak kayda geçsin.

Bu asimetri, kaybı çabuk ve görünür, kârı seyrek ama gerçek kaydetmeni sağlar; duygusal kararı da önceden bağlar.

### Katman 4 — Asıl ürün: meta-düzey deney

**Asıl cevabın, muhtemelen "12 haftalık oda-farkı" değil** — sürenin esas ürünü, **seçim sürecinin** ("v1.x kuralları değer kattı mı?") ölçülebilir hale gelmesi. Yol:

- **Sabit referans kolu** + her "yürüyen oda kuşağı" (v1.3, v1.4, …) birer sanal kopya olarak **arka arkaya** kurulur.
- Her bir kuşağın referansa göre üstün / eşit / zayıf sonucu **her kuşak için ayrı kaydet**.
- 6 ay sonra "3 kuşağın ikisi referansa üstün, bir tanesi şaşırtıcı" gibi **çapraz-kuşak** bir bilgi birikmiş olur.

Bu, **minimum iz uzunluğu (minimum track record length: kuralın sadeliğini dürüstçe ölçebileceğin en kısa geçmiş)** literatürünün birebir uygulamasıdır: her kuşak bir "deneme" sayılır; çapraz-kuşak karşılaştırmaların ortalaması, tek büyük bir örnekleme yakın bilgi üretir.

---

## 6. Kaynaklar

| İddia | Kaynak | Durum |
|---|---|---|
| DSR (Deflated Sharpe) çoklu test / selection düzeltmesi yapar; küçük örneklemde Sharpe abartısı | Bailey & López de Prado, "The Deflated Sharpe Ratio", Journal of Portfolio Management 2014 — [SSRN 2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) | Doğrulandı (özet ve ana metin erişimli) |
| "Minimum track record length" ve Probabilistic Sharpe | Bailey & López de Prado, "The Sharpe Ratio Efficient Frontier", Journal of Risk 2012 — [SSRN 1821643](https://papers.ssrn.com/abstract=1821643) | Doğrulandı |
| eToro'da popülarite sıçraması sonrası eşleştirilmiş kontrole karşı kalıcı üstünlük kayboluyor | "When popularity strikes…", Finance Research Letters, Ekim 2026 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1544612326010093) | Doğrulandı (özet üzerinden; tam metin erişimli kılmadım) |
| Kopya-trading bilgisi risk alımını artırıyor | "Copy Trading", Management Science 2020 — [INFORMS](https://pubsonline.informs.org/doi/10.1287/mnsc.2019.3508) | Doğrulandı |
| eToro'da trader'ların çoğu dönem zararında; lider-trader filtrelerinin gelecek üstünlüğü zayıf | Pan, Altshuler & Pentland 2012 (ikincil kaynak üzerinden); ayrıca "To follow or not to follow…", N. of B. & Finance 2018 — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S106297691730248X) | İkincil kaynak üzerinden; orijinal çalışmayı ayrıca doğrulayamadım |
| Sürekli bakma ("peeking") yanlış-pozitifi büyütür; çare always-valid p-value / mSPRT | Johari, Pekelis, Walsh — [arXiv:1512.04922](https://arxiv.org/abs/1512.04922); ayrıca Operations Research 2022 — [INFORMS](https://pubsonline.informs.org/doi/10.1287/opre.2021.2135) | Doğrulandı |
| Hyperliquid `userFills` yalnız en yeni **10.000** dolumu döndürür; `userFillsByTime` da aynı sınıra tabi | Hyperliquid resmi API docs — [Info endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) | Doğrulandı (docs). Üçüncü taraf (Hydromancer) "hard limit" tanımını teyit ediyor — [Hydromancer](https://hydromancer.xyz/resources/hyperliquid-rate-limits) |
| White's Reality Check (bootstrap bazlı çoklu test düzeltmesi) | White, "A Reality Check for Data Snooping", Econometrica 2000 | **Doğrulanamadı** — hangi nihai kaynak URL'yi güvenle veremiyorum; yalnızca literatür referansı olarak işaretliyorum |

---

## 7. Son söz

### En kritik üç eleştiri

1. **Güç küçükse kararı performansla değil, süreçle yap.** "Oda iyi miydi?" sorusunun cevabı 12 haftada büyük olasılıkla verilemeyecek; süreç kalitesi (mutabakat hatası yakalama, survivorship bias ölçümü, davranış kırılmalarının tespiti) esas gerçek metriktir.
2. **Kol sayısını değil, örneklemin etkin kalitesini artır.** #1 (spot) ve #2 (3 oda) aynı yanılgıya düşürüyor: **daha çok bölüm** = **daha az bağımsız bilgi.** Oda sayısını artırmak yerine korelasyon-farkında tek oda (Bölüm 4-B) kur.
3. **Ana ürün "kazanç" değil; karar fişeri + mutabakat verisi.** Getiri kıyası, bu ikisinin üzerine kurulmadığı sürece güvenilir değildir.

En sıkı paket: **#4 (mutabakat) → #3 (pencere-kalıcılık) → #11 (paralel deney)**; araya **karar fişeri altyapısı (Bölüm 4-C)** serpiştir; bunlar oturunca **#12b ve #12d** gibi davranış-temiz sinyallere geç.

Bu küçük projede bile, her kararın arkasında **yazılı bir fiş** olduğunda, işin "bilimsel" tarafı gerçekten güvenilir olur.
