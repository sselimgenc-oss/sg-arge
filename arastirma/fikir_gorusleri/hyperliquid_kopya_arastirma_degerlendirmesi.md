# Hyperliquid Gölge Kopya (Copy-Trading) Araştırması: Kantitatif ve Ürün Değerlendirmesi

## 1. Mevcut Mimari Güçlü Olsa da "Gerekçeli Müdahale" Kararı İstatistiksel Gücü Zedeliyor

Kurduğun araştırma mimarisi (eşleştirilmiş kontrol grubu, 7 günlük blok bootstrap, gecikmeli kopya maliyeti ve güç analizi) bireysel kripto projelerinin büyük çoğunluğundan çok daha sağlam bir temele oturuyor. Buna karşın **12 hafta kuralını esnetip "gerekçeli kayıtla odayı değiştirme" kararın, istatistiksel güç eksikliğini çözmek yerine projeye en tehlikeli insan önyargısını sokuyor.**

İstatistiksel gücün (gerçek bir üstünlüğü şanstan ayırt edebilme olasılığı) %20 olması, "daha sık müdahale et" anlamına gelmez; **"müdahale ettiğinde şansı yetenek sanma ihtimalin %80"** anlamına gelir. Sabit referans kolunu ("ilk oda + kontrol") tutman harika bir sigorta, ancak fikir listendeki birçok madde seni veri madenciliği (*data snooping* — aynı veriyi kurcalayarak şansa bağlı kalıplar bulma) tuzağına çekiyor.

## 2. Fikir Listesinin Değer, Zorluk ve İstatistiksel Risk Tablosu

Aşağıdaki tablo, listedeki 12 fikri (ve alt kırılımlarını) ürün değeri, uygulama zorluğu ve istatistiksel yanlılık riski açısından değerlendirmektedir:

| # | Fikir | Değer | Zorluk / Maliyet | İstatistiksel Risk | Tek Cümle Gerekçe |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Spot odası** | Düşük | Orta | Orta (örneklem bölünmesi) | Perp tarafında henüz alfa kanıtlanmamışken veri hattını ve dikkatini ikinci bir piyasa yapısına bölmek odak kaybıdır. |
| **2** | **Atak / dengeli / temkinli odalar** | Düşük | Düşük | Yüksek (örneklem seyrelmesi) | 18 kişiyi 3 alt odaya bölmek oda başına ~6 trader bırakır ve zaten %20 olan istatistiksel gücü sıfıra indirir. |
| **3** | **Performans pencereleri (1h–12a)** | Orta | Düşük | Çok Yüksek (çoklu test — *multiple testing*) | 5 farklı pencereyi aynı anda izleyip "en iyi çalışanı" seçmek, şansa iyi giden pencereyi kural sanmana yol açar; sadece paralel deney (Fikir 11) içinde bakılmalıdır. |
| **4** | **Operasyon / mutabakat (yetim pozisyon vb.)** | **Yüksek** | Orta | Sıfır | Gölge muhasebede kopya ile trader arasındaki kayma ve yetim pozisyonlar düzeltilmezse ölçtüğün tüm getiri ve alfa rakamları hayalidir. |
| **5** | **Futbol takımı modeli (Lig usulü)** | Çok Düşük | Yüksek | Çok Yüksek (ortalamaya dönüş — *mean reversion*) | Kısa vadeli şansla parlayanı "İlk 11"e alıp şanssızlık yaşayanı küme düşürmek, sistematik olarak tepeden alıp dipten satma makinesidir. |
| **6** | **Panoyu sadeleştirmek** | **Yüksek** | Düşük | Sıfır (risk azaltır) | Telefondan bakan teknik olmayan bir kullanıcı için ekrandaki her gereksiz metrik, duygusal müdahale ("kaşıntı") tetikleyicisidir. |
| **7** | **Karantina (%50 pay indirimi)** | Düşük | Düşük | Yüksek (gizli parametre ekleme) | Karantina eşiği ve süresi yeni serbestlik dereceleri (modele eklenen keyfi ayarlar) yaratır; tarz kayması (Fikir 8) yoksa düşüşte pay kesmek toparlanmayı kaçırtır. |
| **8** | **Tarz kayması tespiti** | **Yüksek** | Orta | Düşük | Getiriye (PnL) değil davranışsal yapıya (kaldıraç, işlem sıklığı, varlık evreni) baktığı için aşırı uyum riski olmadan gerçek bozulmayı yakalar. |
| **9** | **Günlük kayıp soğuması (24 sa durma)** | Çok Düşük | Düşük | Yüksek (kuyruk yakalama kaybı) | Kripto volatilitesinde büyük kayıp günlerinin hemen ardından en sert tepki yükselişleri gelir; 24 saat çıkmak düşüşü yiyip tepkiyi kaçırmayı garantiler. |
| **10** | **Lider tablosu dışı keşif** | Orta | Yüksek | Düşük | [Hyperliquid Info API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) cüzdan adresini bilmeden tüm evreni taramaya izin vermez; L1 blok verisi kazımak (*indexing*) teknik olmayan biri için aşırı maliyetlidir. |
| **11** | **Paralel deney (gölge motor)** | **Çok Yüksek** | Orta | Orta (kontrollü) | Canlı odaya dokunma dürtüsünü sıfırlayan, tüm fikirleri (3, 7, 12) aynı veri üzerinde yan yana ve dürüstçe sınamanı sağlayan tek güvenli laboratuvardır. |
| **12a** | **Calmar / Maks. düşüşe göre getiri** | Orta | Düşük | Yüksek | Maksimum düşüş (*Max Drawdown*) tek bir uç olaya dayandığı için örneklem büyüklüğüne aşırı duyarlıdır ve geçmişi geleceğe zayıf taşır. |
| **12b** | **Anti-martingale disiplin skoru** | **Yüksek** | Orta | Düşük | Zarardaki pozisyonu tutma eğilimi ([Odean 1998 — Disposition Effect](https://www.semanticscholar.org/paper/Are-Investors-Reluctant-to-Realize-Their-Losses-Odean/9796374d3a3b4b496a330d762c7ca81f85df799a)) kriptoda hesap patlatmanın bir numaralı sebebidir; bunu elemek kalıcı yapısal alfa sağlar. |
| **12c** | **Deflated Sharpe Ratio (DSR)** | Orta | Düşük | Düşük (koruyucu) | [Bailey ve López de Prado (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) tarafından geliştirilen bu ölçüt ~48 bin hesaptan seçim yapmanın yarattığı şans yanlılığını törpüler, ancak kısa serilerde tek başına mucize yaratmaz. |
| **12d** | **Likidite kapasitesi / kopya aşınması** | **Yüksek** | Orta | Sıfır | 30 dk / 2 sa gecikmeyle sığ altcoin'lerde işlem yapan birini kopyalamak kağıt üzerinde kârlı görünse de emir defteri derinliği (*slippage*) hesaba katıldığında imkansız olabilir. |

## 3. İlk Üç Öncelik Paralel Deney, Veri Mutabakatı ve Davranışsal Filtreler Olmalıdır

### En Yüksek Etkiyi Sağlayacak İlk 3 Öncelik

1. **Paralel Deney Altyapısı (Fikir 11) + Pano Sadeleştirme (Fikir 6):** Canlı odaya müdahale etme ihtiyacını ortadan kaldırır. Tüm yeni kuralları arka planda sessizce yarıştırırken, mobil panoda yalnızca "Sabit Oda vs. Müdahaleli Oda vs. Kontrol" özetini görmeni sağlar.
2. **Operasyon / Mutabakat Sağlaması (Fikir 4) + Likidite Kapasitesi (Fikir 12d):** Araştırmanın veri temelini doğrular. [Hyperliquid API limitleri](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) ve `userFills` uç noktasının en fazla son 2.000–10.000 işlemi döndürmesi ([Chainstack Hyperliquid Docs](https://docs.chainstack.com/reference/hyperliquid-info-user-fills)) nedeniyle yüksek frekanslı trader'larda kaçan işlemler veya sığ tahtalardaki fiyat kayması (*slippage*) sanal getiriyi şişirir. Önce ölçümün gerçek olduğundan emin olmalısın.
3. **Davranışsal Filtreler: Anti-Martingale Skoru (Fikir 12b) + Tarz Kayması Tespiti (Fikir 8):** Getiri gibi gürültülü bir çıktı yerine, trader'ın **nasıl** işlem yaptığına (süreç kalitesine) odaklanır.

### Birbirini Tamamlayan ve Çakışan Fikirler

* **Tamamlayıcı İkililer:** **Fikir 11 (Paralel Deney)** ile **Fikir 3 (Performans Pencereleri)** ve **Fikir 12 (Alternatif Seçim Kuralları)** doğrudan bütünleşir; 12a–12d kurallarını canlı odayı bozmadan paralel motorlarda test edersin. Aynı şekilde **Fikir 8 (Tarz Kayması)** ile **Fikir 12b (Anti-Martingale)** birleştiğinde "davranışsal risk kalkanı" oluşturur: biri girişte disiplinli trader seçer, diğeri içerideki trader disiplini bozarsa (örneğin zararda kaldıraç artırırsa) alarm verir.
* **Çakışan / Birbirini Bozanlar:** **Fikir 5 (Futbol Takımı)**, **Fikir 7 (Karantina)** ve **Fikir 9 (Günlük Kayıp Soğuması)** hem birbirleriyle hem de istatistiksel test disipliniyle doğrudan çakışır. Üçü de aynı soruna (düşüş / *drawdown*) farklı kurallarla müdahale etmeye çalışır; birlikte uygularsan hangi kuralın işe yaradığını veya sistemi bozduğunu asla ayrıştıramazsın (atfedilebilirlik kaybı).

## 4. Getiri Kovalama Tuzağını Önlemek İçin "Getiri Körlüğü" Protokolü Uygulanmalıdır

Finans literatüründe bireysel ve kurumsal yatırımcıların fon seçerken yaptığı en yıkıcı hata, son dönemin kazananını alıp kaybedenini satmaktır ([Fama & French 2010 — Luck versus Skill](https://mba.tuck.dartmouth.edu/bespeneckbo/default/AFA611-Eckbo%20web%20site/AFA611-S8C-FamaFrench-LuckvSkill-JF10.pdf)). Listendeki şu 4 madde bu tuzağın doğrudan kılıfıdır:

* **Fikir 5 (Futbol Takımı Modeli):** Alt ligden üst lige çıkma kriterin son haftaların getirisi (PnL) ise, sadece şans serisi yakalayanları (pozitif uç değerleri) odaya alır, normal bir düşüş (*drawdown*) yaşayan yetenekli trader'ı küme düşürürsün.
* **Fikir 7 (Karantina) ve Fikir 9 (Günlük Kayıp Soğuması):** İkisi de "zarar edeni cezalandır" mantığına dayanır. Eğer trader'ın stratejisi istatistiksel olarak ortalamaya dönüş (*mean-reversion*) içeriyorsa, tam beklenen getirinin yükseldiği yerde payını kesmiş olursun.
* **Mevcut "Gerekçeli Kayıtla Değiştirme" Esnekliğin:** İnsan beyni, bir trader para kaybederken onu odadan atmak için her zaman "mantıklı" bir bahane üretir (geriye dönük rasyonalizasyon — *hindsight bias*).

### "Getiri Körlüğü" Çözüm Protokolü

1. **PnL Bazlı Çıkarmayı Yasakla:** Bir trader'ı odadan çıkarmanın veya karantinaya almanın **tek** geçerli sebebi **Fikir 8 (Tarz Kayması)** veya **Fikir 12b (Anti-Martingale İhlali)** olmalıdır. Trader kendi geçmiş dağılımına uygun şekilde para kaybediyorsa (örneğin geçmişte de %15 düşüş yaşamışsa ve kaldıracı/işlem sıklığı değişmemişse) ona dokunmak yasaktır.
2. **Kör Karar Kartı Uygulaması:** Telefondan "gerekçeli değişiklik" onayı verirken, panonun sana trader'ın son 2 haftalık kâr/zararını göstermesini kapat; ekranda yalnızca davranışsal sapma metriklerini (ör. "Medyan kaldıraç 2.5x'ten 8x'e çıktı", "Zararda bekleme süresi 3 katına çıktı") görerek karar ver.

## 5. Listede Olmayan Ancak Araştırmanın Geçerliliği İçin Şart Olan Üç Yapısal Fikir

1. **Kuyruk Korelasyonu ve Kalabalıklaşma (Crowding) Filtresi:** Seçtiğin 18 trader normal günlerde birbirinden bağımsız görünebilir, ancak piyasa çöküşlerinde hepsi aynı anda aynı altcoin'lerde likidite sıkışıklığına yakalanıyor olabilir (kuyruk korelasyonu — *tail dependence*). Odaya 18 ayrı kişi aldığını sanırken gerçekte **tek bir dev pozisyonu 18 kez** kopyalıyor olabilirsin. Seçim kapısına "oda içi pozisyon çakışması ve düşüş günlerindeki getiri korelasyonu" sınırı eklemelisin.
2. **Piyasa Rejimi Koşullu Değerlendirme (Trend vs. Yatay/Çalkantılı Piyasa):** 12 haftalık test dönemin tek bir makro rejime (örneğin sadece yatay ve hacimsiz bir döneme) denk gelirse, trend takipçisi trader'ların hepsi başarısız görünür. Performansı düz zamana göre değil, BTC'nin volatilite ve trend rejimlerine bölerek ("trend varken kim çalıştı, yatay piyasada kim korudu?") ölçmelisin.
3. **Kısmi Kapanış / Ters İşlem ve Funding Sömürüsü (Carry) Ayrıştırması:** Hyperliquid'de birçok lider tablosu hesabı yönsel tahminle değil, **Funding Rate arbitrajıyla** (fonlama oranı toplamak için perp'te short açıp başka yerde veya spotta long tutarak) ya da piyasa yapıcılıkla (*market making*) para kazanır. Sen bu hesabı **30 dk veya 2 saat gecikmeyle** ve sadece perp bacağını kopyaladığında, onun hedge (koruma) bacağını almadığın için saf yönsel kumar oynamış olursun. Seçim kapısına "getirinin ne kadarı funding'den, ne kadarı fiyat değişiminden geliyor?" ayrıştırması şarttır.

## 6. Küçük Örneklemde (36–61 Trader, Birkaç Ay) Anlamlı Karar Vermek İçin Bayesçi ve Sıralı Test Çerçevesi

Klasik p-değeri testi (12 hafta bekle, sonunda tek bir "evet/hayır" testi yap) bu örneklem boyutunda işlevsizdir; yıllık %50 farkı %20 güçle aramak yazı-tura atmaktır. Bunun yerine elindeki yapıyı aşağıdaki üç somut yönteme dönüştürmelisin:

### A. Trader Düzeyinde Değil, "İşlem / Epizot" Düzeyinde Hiyerarşik Bayesçi Model (Empirik Bayes / Shrinkage)

61 trader'ın 12 haftalık toplam getirisine bakarsan elinde sadece 61 veri noktası olur. Oysa bu 61 trader 12 haftada toplam **binlerce bağımsız işlem döngüsü (sıfırdan pozisyon açıp kapatma epizodu)** gerçekleştirir. Her trader'ın gerçek yeteneğini ($\theta_i$), tüm havuzun ortalama yetenek dağılımından ($\mu, \tau$) beslenen bir **Hiyerarşik Bayesçi (Empirik Bayes)** modelle tahmin et. Az işlemi olan ama %200 kazanmış bir trader'ın tahmini, otomatik olarak havuz ortalamasına doğru çekilir (büzülme — *shrinkage*); böylece şanslı uç değerlere kanmazsın.

### B. Sabit Süreli Test Yerine Sıralı Olasılık Oranı Testi (SPRT) ve E-Değerleri (Anytime-Valid Inference)

Veriye her gün/hafta bakıp karar vermek istiyorsan klasik istatistik bozulur. Bunun yerine [Abraham Wald'un Sıralı Olasılık Oranı Testi (SPRT)](https://en.wikipedia.org/wiki/Sequential_probability_ratio_test) veya modern karşılığı olan **Güvenli Her-An-Geçerli Çıkarım / E-değerleri (Safe Anytime-Valid Inference — [Ramdas vd. 2023](https://arxiv.org/abs/2210.01948))** yöntemini kullan:

* **Günlük Güncelleme Formülü:** Her gün oda ile kontrol grubu arasındaki BTC-düzeltilmiş getiri farkını ($d_t$) ölç. Sıfır hipotezi ($H_0$: fark = %0) ile hedef hipotezin ($H_1$: yıllıklandırılmış fark = +%30, yani günlük $\mu_1 \approx 0.0008$) olasılık oranını (test martingalı / servet süreci $E_t$) her gün çarpımsal olarak güncelle:
  $$E_t = E_{t-1} \times \exp\left(\frac{\mu_1 \cdot d_t}{\sigma^2} - \frac{\mu_1^2}{2\sigma^2}\right)$$
* **Kesin Karar Sınırları ($E_0 = 1$ başlangıç değeriyle):**
  * **$E_t \ge 10$ olursa (%90 güven sınırı):** Seçim kuralın çalışıyor, kanıt yeterli.
  * **$E_t \le 0.1$ olursa:** Seçim kuralın çalışmıyor, 12 haftayı beklemeden deneyi dürüstçe durdur.
  * **$0.1 < E_t < 10$ arasında kaldığı sürece:** Panoda yalnızca **"Kanıt yetersiz (Kararsız Bölge)"** ibaresi yer alır ve sisteme müdahale edilmez. Bu yöntemle panoya her saat baksan bile yanlış pozitif (şansı yetenek sanma) oranını matematiksel olarak şişirmezsin ([Project Euclid — Statistical Science](https://projecteuclid.org/journals/statistical-science/volume-38/issue-4/Game-Theoretic-Statistics-and-Safe-Anytime-Valid-Inference/10.1214/23-STS894.pdf)).

### C. Karar Kriterini "İstatistiksel Anlamlılıktan" "Beklenen Değer ve Asimetrik Kayba" Çevirmek

Akademik makale yazmadığın (%95 güven şart olmadığı) ve bir ürün kararı verdiğin için Bayesçi sonsal (*posterior*) dağılımı hesaplayıp panoya tek bir özet koymalısın: **"Odanın kontrolden iyi olma olasılığı: %X ve beklenen net üstünlük: yıllık %Y."** Eğer 8 hafta sonunda üstünlük olasılığı %75 ve beklenen kayıp riski (alt %5'lik dilim) kabul edilebilir düzeydeyse, klasik test "p < 0.05 değil (kanıt yok)" dese bile rasyonel bir ürün yöneticisi olarak o kuralı bir sonraki aşamaya taşıyabilirsin.

## 7. Doğrulanmış Kaynaklar

* **Çoklu Test ve Deflated Sharpe Ratio:** [Bailey, D. H., & López de Prado, M. (2014) — The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
* **Disposition Effect (Zarardaki Pozisyonu Tutma Eğilimi):** [Odean, T. (1998) — Are Investors Reluctant to Realize Their Losses? (Journal of Finance)](https://www.semanticscholar.org/paper/Are-Investors-Reluctant-to-Realize-Their-Losses-Odean/9796374d3a3b4b496a330d762c7ca81f85df799a)
* **Fon Seçiminde Şans ve Yetenek Ayrımı:** [Fama, E. F., & French, K. R. (2010) — Luck versus Skill in the Cross-Section of Mutual Fund Returns](https://mba.tuck.dartmouth.edu/bespeneckbo/default/AFA611-Eckbo%20web%20site/AFA611-S8C-FamaFrench-LuckvSkill-JF10.pdf)
* **Sıralı Olasılık Oranı Testi (SPRT):** [Wald, A. — Sequential Probability Ratio Test](https://en.wikipedia.org/wiki/Sequential_probability_ratio_test)
* **Güvenli Her-An-Geçerli Çıkarım (E-Değerleri ve Test Martingalları):** [Ramdas, A., Grünwald, P., Vovk, V., & Shafer, G. (2023) — Game-Theoretic Statistics and Safe Anytime-Valid Inference (arXiv)](https://arxiv.org/abs/2210.01948) ve [Statistical Science (Project Euclid)](https://projecteuclid.org/journals/statistical-science/volume-38/issue-4/Game-Theoretic-Statistics-and-Safe-Anytime-Valid-Inference/10.1214/23-STS894.pdf)
* **Hyperliquid API Kısıtları ve Info Uç Noktası:** [Hyperliquid Docs — Rate Limits and User Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits), [Hyperliquid Docs — Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) ve [Chainstack — Hyperliquid userFills Reference](https://docs.chainstack.com/reference/hyperliquid-info-user-fills)
