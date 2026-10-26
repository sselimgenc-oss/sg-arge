Kurduğunuz test kapısı **mühendislik hijyeni açısından sağlam** (kesim noktalı nedensellik kontrolü, yayım tarihi sonrası gerçek örneklem dışı test ve 2 kat maliyet stres testi doğru adımlar), ancak **istatistiksel çıkarım açısından ciddi şekilde geçirgen ve yanlıdır**. Özellikle 119 varyanttan 85'inin (%71,4) geçmesi, kapının strateji yeteneğini (alfa) değil, **2023–2026 boğa piyasası betasından aldığı rüzgârı** ölçtüğünü gösteriyor. Bu haliyle makine öğrenmesi (ML) tabanlı binlerce strateji üretimine bağlanırsa yüksek oranda sahte keşif (false discovery) üretecektir.

### 1. Kapı Adil mi? (Tip I ve Tip II Hata Analizi)

**Kötü Stratejiyi Haksız Yere Geçiren Zayıflıklar (Tip I Hata / False Positive):**

* **Sıfır eşikli ham getiri şartı:** 2023–2026 döneminde S&P 500 ve kripto piyasaları güçlü bir boğa rejimi yaşadığı için yalnızca alım (long-only) yapan rastgele bir stratejinin "Net Getiri > 0" şartını geçmesi piyasa drift'i (pozitif beta) sayesinde son derece kolaydır.
* **Haftalık getiri üzerinden p10 hesabı:** Haftalık toplam getiri serisinin 10. yüzdelik dilimi (p10), negatif kalın kuyruk (tail) riski olan stratejilerde **pozitif medyanı** ölçer; ancak blok bootstrap ile **beklenen ortalama getirinin (mean) %10 alt güven sınırını** ölçmediğiniz sürece, sık küçük kazanç ve nadir yıkıcı zarar üreten (negatif çarpıklığa sahip) stratejiler p10 > 0 filtresinden sızar.
* **Seçim yanlılığının (multiple testing) elenmemesi:** [Deflated Sharpe Ratio (DSR)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) değerinin 4. adımda sadece "bilgi amaçlı" tutulup kesici filtre yapılmaması, 500+ test edilen strateji arasından şans eseri sağ kuyruğa düşen gürültü stratejilerinin 5. adıma geçmesine izin verir.
* **Veri sızıntısı (Data snooping) olan kendi varyantlarınız:** TradingView stratejilerinde yayım tarihi sonrası gerçek örneklem dışı (OOS) iken, 2026 yılında tasarladığınız 119 "kendi hipotezinizi" 2023–2026 verisinde test etmek gerçek OOS değildir; 2023–2026 piyasa rejimini bilerek hipotez kurduğunuz için örtük gelecek bilgisi (hindsight bias) içerir.

**İyi Stratejiyi Haksız Yere Eleyen Zayıflıklar (Tip II Hata / False Negative):**

* **Yılda 30 işlem alt sınırı:** Günlük (1D) veya 4 saatlik (4H) zaman diliminde çalışan meşru trend takip ve makro momentum stratejileri tek enstrümanda yılda ortalama 8–20 işlem açar; bu kural en yüksek kapasiteli ve maliyet direnci en yüksek stratejileri doğrudan çöpe atar.
* **2 kat maliyet şartının frekansa kör olması:** İşlem başına %0,10/taraf maliyeti 2 katına (%0,20/taraf, gidiş-dönüş %0,40) çıkarmak, yılda 15 işlem yapan bir swing stratejisi için önemsizken, 15 dakikalık yüksek frekanslı ortalamaya dönüş (mean-reversion) stratejilerinin gerçek alfasını tamamen siler.
* **Ücretsiz veri kaynaklı %43'lük kör nokta:** 933 stratejinin 401'inin veri eksikliğiyle elenmesi, likiditesi daha düşük veya özel veri gerektiren (ve dolayısıyla piyasa verimsizliğinin daha yüksek olabileceği) niş stratejileri baştan dışlar.
* **Yazarın tek sembolüne hapsolmak:** Yazar iyi bir sinyal mantığını yanlış veya o dönem yatay giden tek bir sembolde yayımlamışsa, 2. adımdaki tek sembol testi stratejiyi haksız yere eler.

### 2. “Net Getiri > 0” Şartı ve Rastgele Stratejinin Geçme Olasılığı

* **Eşiğin uygunluğu:** "Net Getiri > 0" tek başına bilimsel bir geçme şartı değildir; ne riski (volatilite/drawdown) ne de piyasa getirisini hesaba katar.
* **Rastgele stratejinin geçme olasılığı:** Yıllık piyasa drift'i $\mu_m$, volatilitesi $\sigma_m$ ve stratejinin piyasada kalma oranı (exposure) $p \in (0,1]$ iken, işlem başına maliyet $c$ ve yıllık işlem sayısı $N_{tr}$ için rastgele giriş-çıkış yapan bir long-only stratejinin $T$ yıllık sınamada pozitif net getiri üretme olasılığı yaklaşık olarak şu formülle belirlenir:

$$P(\text{Net Getiri} > 0) \approx \Phi\left( \frac{(p \cdot \mu_m - N_{tr} \cdot c)\sqrt{T}}{\sqrt{p} \cdot \sigma_m} \right)$$



2023–2026 gibi $\mu_m \approx \%25$, $\sigma_m \approx \%18$ olan bir ABD hisse/kripto boğa piyasasında, yılda 35 işlem yapan ve zamanın %50'sinde piyasada kalan ($p=0,5$) tamamen rastgele bir strateji bile maliyet sonrası **%65 ile %80 olasılıkla** "Net Getiri > 0" kapısından geçer (119 varyantınızın %71 oranında geçmesi bunun pratik kanıtıdır).
* **Nasıl ölçülür (Monte Carlo Permütasyon Testi):** [David Aronson'ın *Evidence-Based Technical Analysis* yaklaşımıyla](https://community.portfolio123.com/t/new-book-evidence-based-technical-analysis/22070) her strateji için iki farklı plasebo testi koşulmalıdır:
1. **Sinyal karıştırma (Trade-shuffling):** Stratejinin toplam işlem sayısını ($N_{tr}$) ve ortalama pozisyon tutma süresini sabit tutup giriş zamanlarını rastgele karıştırarak 1.000 sentetik getiri eğrisi üretin.
2. **Bar karıştırma (Return-shuffling):** Fiyat serisinin logaritmik bar değişimlerini bloklar halinde karıştırıp strateji kodunu bu sentetik fiyatlar üzerinde çalıştırın. Gerçek strateji, bu 1.000 rastgele stratejinin en az %95'ini ($p < 0,05$) geçemiyorsa elenmelidir.



### 3. Çoklu Test ve Seçim Yanlılığı: Hangi Yöntem Seçilmeli?

Test edilen 400+ geçerli strateji ve 119 varyant varken standart $t$-istatistiği veya ham Sharpe oranı kullanmak geçersizdir. Yöntemlerin pratik karşılaştırması:

| Yöntem | Ne Yapar? | Sizin Sisteminiz İçin Uygunluğu | Pratik Karar |
| --- | --- | --- | --- |
| **[White's Reality Check (2000)](https://www.ssc.wisc.edu/~bhansen/718/White2000.pdf)** | En iyi stratejiyi tüm havuzun maksimum dağılımıyla sınar (FWER kontrolü). | Havuzdaki çok kötü stratejiler testi aşırı muhafazakâr (düşük güçlü) yapar; tek bir en iyi strateji seçmek içindir. | **Uygun değil** (fazla katı, portföy seçimine uymaz). |
| **[Hansen's SPA (2005)](https://www.tandfonline.com/doi/abs/10.1198/073500105000000063)** | White RC'yi öğrenci-t (studentized) normalizasyonu ve kötü stratejileri budayarak iyileştirir. | Sadece "havuzda en az 1 iyi strateji var mı?" sorusunu yanıtlar; alt küme seçmek için [Romano-Wolf StepM (2005)](https://econpapers.repec.org/RePEc:ecm:emetrp:v:73:y:2005:i:4:p:1237-1282) uzantısı gerekir. | **İkinci aşama (küme doğrulama) için uygun.** |
| **[Deflated Sharpe Ratio - DSR (2014)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)** | Gözlenen Sharpe oranını; çarpıklık, basıklık, süre ve bağımsız deneme sayısı ($N_{eff}$) ile düzeltir. | Tekil strateji bazında hızlı hesaplanır, ancak tüm stratejilerin korelasyon matrisinden etkin bağımsız deneme sayısını ($N_{eff}$) doğru tahmin etmeyi gerektirir. | **Bireysel ön eleme filtresi olarak kullanılmalı.** |
| **[BHY / False Discovery Rate (2001)](https://projecteuclid.org/journals/annals-of-statistics/volume-29/issue-4/The-control-of-the-false-discovery-rate-in-multiple-testing/10.1214/aos/1013699998.full)** | Seçilen strateji sepetindeki beklenen yanlış keşif oranını (ör. $\text{FDR} \le \%10$) sınırlar ([Harvey, Liu & Zhu, 2016](https://academic.oup.com/rfs/article/29/1/5/1843824)). | Paper trade'e 1 değil 10–15 stratejilik bir portföy almak istediğiniz için FWER yerine FDR kontrolü amacınıza tam uyar. | **En uygun ana seçim mekanizması.** |

* **Pratik öneri:** Her stratejinin gerçek $p$-değerini **Blok Bootstrap / Monte Carlo Plasebo (Sinyal Karıştırma)** ile parametrik olmayan şekilde hesaplayın, ardından tüm aday havuzuna **[Benjamini-Hochberg-Yekutieli (BHY) FDR kontrolü](https://projecteuclid.org/journals/annals-of-statistics/volume-29/issue-4/The-control-of-the-false-discovery-rate-in-multiple-testing/10.1214/aos/1013699998.full)** ($q \le 0,10$) ve bireysel **[DSR](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) > 0,95** filtresi uygulayın.

### 4. Yükselen Piyasada Long-Only Stratejilerde Piyasa Etkisini Ayrıştırma

* **Neden ham Al-ve-Tut (Buy & Hold) karşılaştırması yanlıştır:** Long-only bir strateji zamanın sadece %35'inde pozisyonda kalıyorsa, ralli döneminde %100 piyasada kalan Al-ve-Tut'un toplam getirisinden düşük kalması normaldir; buna bakarak stratejiyi elemek hatadır. Tersine, kaldıracı veya yüksek betalı altcoin'leri seçerek Al-ve-Tut'u geçen bir strateji gerçekte sıfır zamanlama yeteneğine sahip olabilir.
* **Doğru ayrıştırma için 3 kural:**
1. **Zaman-Ağırlıklı (Exposure-Matched) Kıyaslama:** Stratejinin ortalama piyasada kalma oranı $p$ ise (ör. zamanın %40'ında long), kıyaslama ölçütü $\text{Benchmark}_t = p \cdot R_{\text{piyasa}, t} + (1-p) \cdot R_{\text{risksiz}, t}$ olmalı veya doğrudan **Piyasada Kalınan Bar Başına Getiri** tüm barların ortalama bar getirisiyle ($t$-testi ile) kıyaslanmalıdır.
2. **Beta-Ayarlı Alfa ve Information Ratio (IR):** Günlük strateji getirilerini ilgili enstrümanın (veya sepetin) getirisine regrese edin ($R_{s,t} - R_f = \alpha + \beta (R_{m,t} - R_f) + \epsilon_t$). Geçme şartı toplam getiri değil, **$\alpha > 0$ olması ve $\alpha$'nın Newey-West $t$-istatistiğinin $> 2,0$** (veya yıllıklandırılmış Information Ratio $\text{IR} = \alpha / \sigma(\epsilon) > 0,5$) olmasıdır.
3. **Rejim Alt-Dönem Kontrolü:** 2023–2026 dönemini piyasanın düştüğü veya yatay gittiği çeyreklik pencerelere bölün; strateji kazancının %90'ından fazlasını yalnızca piyasanın en güçlü 1–2 ralli ayında üretmişse stratejiyi eleyin.



### 5. Farklı Sınama Sürelerini (6 Ay – 3 Yıl) Adil Karşılaştırma

6 aylık sınamada yıllıklandırılmış Sharpe oranı 2,0 olan bir strateji ile 3 yıllık sınamada Sharpe oranı 1,3 olan bir stratejiyi doğrudan Sharpe veya toplam getiri ile kıyaslamak **kısa geçmişli stratejileri ödüllendirir** (kısa örneklemde tahmin varyansı çok yüksektir). Adil karşılaştırma yöntemleri:

* **[Probabilistic Sharpe Ratio (PSR)](http://boston.qwafafew.org/wp-content/uploads/sites/4/2017/01/Lopez_de_Prado_Sharpe.pdf) veya $t$-İstatistiği ile Sıralama:** Ham Sharpe ($\widehat{SR}$) yerine örneklem uzunluğu $T$, çarpıklık ($\hat{\gamma}_3$) ve basıklığı ($\hat{\gamma}_4$) içeren PSR istatistiğini kullanın:

$$\widehat{PSR}(SR^*) = \Phi\left( \frac{(\widehat{SR} - SR^*)\sqrt{T - 1}}{\sqrt{1 - \hat{\gamma}_3 \widehat{SR} + \frac{\hat{\gamma}_4 - 1}{4}\widehat{SR}^2}} \right)$$



Bu formül $\sqrt{T-1}$ çarpanı sayesinde 6 aylık stratejiye yüksek belirsizlik cezası keserken, 3 yıllık stratejiyi istatistiksel güvenle ödüllendirir.
* **Ampirik Bayes Büzülmesi (Empirical Bayes Shrinkage):** Kısa geçmişli stratejilerin gözlenen Sharpe oranını, tüm strateji havuzunun ortalama Sharpe oranına ($\mu_0 \approx 0$) doğru örneklem uzunluğuyla ters orantılı olarak büzün: $SR_{\text{shrunk}} = w \cdot \widehat{SR} + (1-w) \cdot \mu_0$, burada $w = \frac{T}{T + \kappa}$ (ör. $\kappa = 252$ iş günü).
* **Asgari Bağımsız Olay (Etkin Örneklem) Şartı:** Takvim süresine (1 yıl) ek olarak en az **30–50 bağımsız işlem döngüsü** ve en az **2 farklı volatilite/trend rejimi** görmemiş stratejileri ana havuzla aynı sıralamaya sokmayın.

### 6. Makine Öğrenmesi (Binlerce Fikir) Devreye Girerse Ne Bozulur?

Mevcut kapıyı binlerce ML stratejisini elemek için kullanırsanız **sistem tamamen çöker**:

* **"Yazarın yayım tarihi" kavramı yok olur:** ML modelleri geçmiş veriyi tarayarak kural ürettiği için 2. adımdaki "yayım tarihi sonrası doğal OOS" koruması ortadan kalkar.
* **Test setinin aşırı uyumu (Test-set Overfitting):** Aynı 2023–2026 OOS verisi üzerinde 10.000 ML stratejisi test edip geçenleri seçtiğiniz anda, OOS verisi fiilen eğitim (in-sample) verisine dönüşür. $N=10.000$ bağımsız sıfır-alfa strateji denendiğinde, [beklenen maksimum Sharpe oranı](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) $E[\max SR] \approx \sqrt{2 \ln(N)} \approx 4,29 \times \sigma_{SR}$ olur; yani salt gürültüden Sharpe oranı 2,5+ olan onlarca strateji kapıyı deler.
* **Korelasyon filtresinin (0,6) darboğazı:** ML genetik algoritmaları veya ağaç modelleri en yüksek skoru veren tek bir fiyat anomalisi etrafında yüzlerce ufak varyant üretir; ikili (pairwise) 0,6 korelasyon elemesi sıra bağımlıdır (hangi stratejinin önce geldiğine göre sonuç değişir).
* **Nasıl tasarlanmalı:**
1. **[Combinatorial Purged Cross-Validation (CPCV)](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf):** Tek bir tarih kesimi yerine veriyi $S$ alt kümeye bölüp tüm eğitim/test kombinasyonlarında **[Probability of Backtest Overfitting (PBO)](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)** değerini hesaplayın ($\text{PBO} < 0,10$ şartı koyun).
2. **Dokunulmaz "Vault" (Kasa) Verisi:** Son 1 yıllık veriyi ML sisteminden fiziksel olarak ayırın; ML adayları CPCV ve DSR aşamalarını geçtikten sonra kasa verisinde **yalnızca bir kez** test edilsin.
3. **Hiyerarşik Kümeleme (ONC):** 0,6 ikili korelasyon yerine strateji getiri matrisine hiyerarşik kümeleme uygulayıp her kümeden yalnızca medoid (merkez) veya doğrulama skoru en yüksek tek stratejiyi seçin.



### 7. Önerilen Yeni Test Kapısı (Somut Adımlar ve Eşikler)

Mevcut 5. adımdaki "elle eleme" kurallarını otomatikleştirip istatistiksel testleri "bilgi amaçlı" olmaktan çıkararak aşağıdaki 6 aşamalı ardışık huniyi (pipeline) kurmanızı öneririm:

1. **Aşama 1 – Teknik Doğruluk ve Nedensellik (Sert Filtre):**
* **Nedensellik (Look-ahead) testi:** Mevcut kesim testi + bar içi yüksek/düşük (intrabar high/low) sıra belirsizliğinde en kötü senaryo (worst-case fill) kontrolü.
* **Asgari örneklem büyüklüğü:** Tek sembolde en az $N_{\text{işlem}} \ge 40$ (veya 25'li sepette toplam $\ge 200$ işlem) **ve** en az 250 işlem günü aktif sinyal penceresi. (Trend takip stratejilerini kurtarmak için tek sembolde <40 işlem yapanları 25 sembollük likit evren sepetinde test edin).


2. **Aşama 2 – Maliyet ve Likidite Stres Testi (Sert Filtre):**
* **Taban maliyet (1x):** Kripto %0,10/taraf, Hisse/ETF %0,05/taraf + 1 tick kayma.
* **Stres maliyeti (1,5x + Gecikme):** Maliyetin 1,5 katında **ve** emrin sinyal barının kapanışı yerine bir sonraki barın açılışından (1 bar gecikmeli) gerçekleştiği senaryoda net alfa $> 0$ olmalı.


3. **Aşama 3 – Piyasa Etkisinden Arındırma ve Plasebo Testi (Sert Filtre):**
* **Beta/Maruziyet düzeltmeli alfa:** Stratejinin aynı piyasada kalma oranına ($p$) sahip pasif kıyaslama ölçütüne karşı yıllıklandırılmış **Information Ratio $\ge 0,50$** ve Newey-West **$\alpha$ $t$-istatistiği $\ge 2,0$**.
* **Monte Carlo Sinyal Permütasyonu:** 1.000 rastgele giriş-çıkış simülasyonuna karşı stratejinin net Sharpe oranı üst %5'lik dilimde ($p_{\text{perm}} < 0,05$) yer almalı.


4. **Aşama 4 – Çoklu Test (Multiple Testing) ve Kısa Süre Cezası (Sert Filtre):**
* **Bireysel güven:** Örneklem uzunluğu, çarpıklık ve etkin deneme sayısı ($N_{\text{eff}}$) ile düzeltilmiş **[Deflated Sharpe Ratio (DSR)](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) $\ge 0,95$**.
* **Çoklu test düzeltmesi:** Aşama 3'ten gelen permütasyon $p$-değerlerine **[Benjamini-Yekutieli (BHY)](https://projecteuclid.org/journals/annals-of-statistics/volume-29/issue-4/The-control-of-the-false-discovery-rate-in-multiple-testing/10.1214/aos/1013699998.full)** prosedürü uygulanarak yanlış keşif oranı **$\text{FDR} \le \%10$** altında kalanlar seçilir.
* **Kuyruk riski ve sağlamlık:** Stationary Bootstrap ([Politis & Romano](https://www.ssc.wisc.edu/~bhansen/718/White2000.pdf)) ile üretilen 1.000 yıllıklandırılmış getiri serisinin **%10 alt güven sınırı (p10) $> 0$**, Profit Factor $\ge 1,25$ ve Maksimum Drawdown Toparlanma Süresi (Time-Under-Water) $< 9$ ay.


5. **Aşama 5 – Kümeleme ve Portföy Seçimi (Otomatik Tekilleştirme):**
* Geçen stratejilerin günlük aktif getiri ($\epsilon_t$) korelasyon matrisi üzerinden hiyerarşik kümeleme (maksimum küme içi korelasyon $\rho \le 0,50$) yapılır; her kümeden yalnızca **PSR değeri en yüksek olan 1 strateji** seçilir.


6. **Aşama 6 – Canlıya Geçiş ve 26 Haftalık Paper Trade Kapısı:**
* Paper trade süresince sadece "kâr etti mi?" diye bakılmaz; **Gerçekleşen Kayma (Slippage) vs. Backtest Kayması** farkı ve canlı Sharpe oranının backtest dağılımının %5 alt sınırının altına düşüp düşmediği (**Sequential Probability Ratio Test - SPRT**) izlenir. 26 hafta sonunda $\text{IR}_{\text{paper}} > 0,3$ ve sinyal/dolum uyumu > %90 olanlar gerçek sermayeye alınır.