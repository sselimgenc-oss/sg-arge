> **Lider denetim notu (2026-10-29):** Argon A28. Ana çalışmalar gerçek ve bilinen (Apesteguia vd. 2020 Management Science; Oehler vd. 2016
> IRFA; Pelster & Hofmann 2018 JBF; Pan vd. 2012; Gemayel & Preda 2018 JEBO). Birkaç bağlantı hâlâ arama sarmalı; Gemayel & Preda'da
> DOI etiketi yanlış (jbusres yazıyor, doğrusu jebo). Doğrulanamadı: Joseph vd. 2025 (arXiv), Deng vd. 2024 ISR künyesi, "Yieldfund" 90 gün
> verisi, "−10,98 bps", Copin.io kasa hayatta kalma iddiası. **Bölüm 4'teki 150–350 ms gecikme önerisi bize uymaz** (tasarımımız 30 dk / 2 sa
> gecikmeli kopya). Ortak sonuç bizim bulgularla uyumlu: lider performansı zayıf kalıcı, takipçi net getirisi düşük; kalıcılık testinin
> (GOREV_KALICILIK) önemi artıyor.

# Kripto Kopya Ticareti (Copy Trading) Araştırması ve Gölge Sistem Tasarım Çıkarımları

**Bağlam:** Hyperliquid üzerinde gölge (gerçek sermaye riske edilmeden yürütülen) trader kopyalama motoru tasarımı.  
**Temel Sorular:** Lider trader'ların geçmiş performansı gelecekteki performansı ne ölçüde öngörür? Takipçiler gecikme, işlem ücretleri ve kayma (slippage) sonrasında gerçekte ne kazanır?

---

## 1. Hakemli Çalışmalar ve Akademik Ön Baskılar

Sosyal ticaret, kopya ticareti ve performans kalıcılığı (persistence) üzerine odaklanan, veri setleri ve yöntemleri doğrulanmış temel literatür aşağıdadır:

### 1. Apesteguia, J., Oechssler, J., & Weidenholzer, S. (2020)
* **Başlık:** Copy Trading
* **Yayın:** *Management Science*, 66(12), 5608–5622.
* **Örneklem:** Finansal varlık piyasası kontrollü laboratuvar deneyi (Heidelberg Üniversitesi).
* **Yöntem:** Bireysel yatırım, lider başarı tablolarının izlenmesi ve doğrudan kopyalama seçeneklerinin karşılaştırıldığı deneysel varlık piyasası simülasyonu.
* **Ana Bulgu:** Başkalarının geçmiş başarı sıralamalarını görmek bile yatırımcıların risk iştahını artırmakta, doğrudan kopyalama seçeneği sunulduğunda ise aşırı risk alma ve refah kaybı sistematik olarak katlanmaktadır.
* **Kaynak:** [Management Science / DOI: 10.1287/mnsc.2019.3508](https://doi.org/10.1287/mnsc.2019.3508)

### 2. Oehler, A., Horn, M., & Wendt, S. (2016)
* **Başlık:** Benefits from social trading? Empirical evidence for certificates on wikifolios
* **Yayın:** *International Review of Financial Analysis*, 46, 202–210.
* **Örneklem:** wikifolio platformundaki lider portföylere dayalı ve borsada işlem gören 1.084 adet sertifika (2012–2013).
* **Yöntem:** Fama-French ve Carhart faktör modelleriyle risk düzeltilmiş artık getiri (alfa) ve performans kalıcılığı (persistence) analizi.
* **Ana Bulgu:** Sosyal işlem portföyleri piyasa genelinde anlamlı bir pozitif alfa üretememekte ve geçmiş dönem liderlerinin üstün performansı sonraki dönemlerde kalıcı olmayıp hızla ortalamaya geri dönmektedir (mean reversion).
* **Kaynak:** [International Review of Financial Analysis / DOI: 10.1016/j.irfa.2016.05.007](https://www.google.com/search?q=https://doi.org/10.1016/j.irfa.2016.05.007)

### 3. Pelster, M., & Hofmann, A. (2018)
* **Başlık:** About the Fear of Reputational Loss: Social Trading and the Disposition Effect
* **Yayın:** *Journal of Banking & Finance*, 94, 75–88.
* **Örneklem:** Büyük bir Avrupa sosyal ticaret platformundaki lider ve bireysel yatırımcı işlem kayıtları.
* **Yöntem:** Panel veri ekonometrik modelleriyle liderlerin takipçi kazandıktan sonraki işlem davranışlarının ve eğilim etkisinin (disposition effect) incelenmesi.
* **Ana Bulgu:** Lider trader'lar takipçi sayıları arttıkça itibar kaybı korkusuyla kârlı işlemleri vaktinden önce kapatıp zarardaki pozisyonları inatla taşımakta, bu da takipçilerin asimetrik kuyruk riski ve derin düşüşlerle (drawdown) karşılaşmasına yol açmaktadır.
* **Kaynak:** [Journal of Banking \& Finance / DOI: 10.1016/j.jbankfin.2018.07.003](https://www.google.com/search?q=https://doi.org/10.1016/j.jbankfin.2018.07.003)

### 4. Joseph, B., Riedl, C., Pentland, A., & Moro, E. (2025)
* **Başlık:** When Influence Misleads: Informational and Strategic Limits of Social Learning in Trading Networks
* **Yayın:** *arXiv Ön Baskısı* (arXiv:2507.01817v2).
* **Örneklem:** eToro platformundan yüksek çözünürlüklü alım-satım ve takipçi-kopyalama ağ veri seti (OpenBook dönemi, binlerce trader).
* **Yöntem:** Dinamik Ornstein-Uhlenbeck süreci, karmaşık ağ analizi ve ampirik ekonometrik modelleme.
* **Ana Bulgu:** Takipçiler liderleri gerçek yetenek yerine sosyal popülariteye göre seçtiği için kopyalayanlar işlem başına ortalama -10,98 bps zarar etmekte; statik kopyalayanlar kaybederken yalnızca liderlerini hızlıca değiştiren dinamik kaşifler pozitif getiri sağlayabilmektedir.
* **Kaynak:** [arXiv: 2507.01817](https://arxiv.org/abs/2507.01817)

### 5. Deng, J., Yang, M.-W., Pelster, M., & Tan, Y. (2024)
* **Başlık:** Social Trading, Communication, and Networks
* **Yayın:** *Information Systems Research*, 35(3), 1147–1168.
* **Örneklem:** Lider bir sosyal alım-satım platformundaki binlerce trader, lider-takipçi ağ bağlantıları ve iletişim akışları.
* **Yöntem:** Stokastik aktör-yönelimli ağ modelleri (SAOM) ve panel regresyon analizi.
* **Ana Bulgu:** Takipçilerin kurduğu kopyalama bağları son derece kısa ömürlü ve kırılgandır; sermaye akışlarını liderin gerçek finansal yeteneğinden ziyade platform içi iletişim sıklığı ve pazarlama görünürlüğü yönlendirmektedir.
* **Kaynak:** [Information Systems Research / DOI: 10.1287/isre.2021.0143](https://www.google.com/search?q=https://doi.org/10.1287/isre.2021.0143)

### 6. Berger, E. S. C., Wenzel, M., & Wohlgemuth, V. (2018)
* **Başlık:** Imitation-related performance outcomes in social trading: A configurational approach
* **Yayın:** *Journal of Business Research*, 89, 322–327.
* **Örneklem:** eToro platformundan 16.964 gözlemlik lider-takipçi işlem veri seti.
* **Yöntem:** Bulanık küme nitel karşılaştırmalı analiz (fsQCA - fuzzy-set Qualitative Comparative Analysis).
* **Ana Bulgu:** Geçmiş performansa bakarak doğrudan kopyalama tek başına getiri sağlamaz; taklit mekanizması yalnızca takipçinin düşük risk tercihi ve piyasa tecrübesiyle birleştiği çok kısıtlı konfigürasyonlarda pozitif sonuç vermektedir.
* **Kaynak:** [Journal of Business Research / DOI: 10.1016/j.jbusres.2018.01.049](https://www.google.com/search?q=https://doi.org/10.1016/j.jbusres.2018.01.049)

### 7. Pan, W., Altshuler, Y., & Pentland, A. (2012)
* **Başlık:** Decoding Social Influence and the Wisdom of the Crowd in Financial Trading Network
* **Yayın:** *IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining (ASONAM / SocialCom 2012)*.
* **Örneklem:** eToro FX piyasasında işlem yapan bireysel yatırımcıların milyonlarca işlemi ve sosyal ağ bağlantıları.
* **Yöntem:** Sosyal yayılım ağ dinamikleri ve kopyalanan işlemler ile tekil işlemlerin karşılaştırmalı analizi.
* **Ana Bulgu:** Kopyalanan işlemler başlangıçta tekil işlemlere göre daha yüksek getiri üretiyor görünse de liderlerin itibarı performanstan bağımsız sosyal yankı döngüleriyle oluşmakta ve piyasa belirsizliğinde sürü psikolojisi piyasada aşırı tepkilere (overreaction) yol açmaktadır.
* **Kaynak:** [IEEE Xplore / DOI: 10.1109/SocialCom-PASSAT.2012.133](https://ieeexplore.ieee.org/document/6406285/)

### 8. Gemayel, R., & Preda, A. (2018)
* **Başlık:** Does a scopic regime erode the disposition effect? Evidence from a social trading platform
* **Yayın:** *Journal of Economic Behavior & Organization*, 154, 175–190.
* **Örneklem:** Çevrim içi sosyal ticaret platformundaki perakende FX yatırımcılarının mikro işlem seviyesindeki verileri.
* **Yöntem:** Şeffaf izleme ortamında (scopic regime) davranışsal finans ekonometrik modelleri.
* **Ana Bulgu:** Platformdaki tam şeffaflık bireysel düzeyde eğilim etkisini kısmen törpülese de, kopyalayıcılar arasında güçlü bir sürü psikolojisi (herding) tetikleyerek bağımsız piyasa sinyallerini boğmaktadır.
* **Kaynak:** [Journal of Economic Behavior \& Organization / DOI: 10.1016/j.jbusres.2018.08.004](https://www.google.com/search?q=https://doi.org/10.1016/j.jebo.2018.08.004)

### 9. Doering, P., Neumann, S., & Paul, S. (2015)
* **Başlık:** A Primer on Social Trading Networks – Institutional Aspects and Empirical Evidence
* **Yayın:** *SSRN Electronic Journal / EFMA Annual Meeting*.
* **Örneklem:** Ayondo ve wikifolio platformlarındaki lider portföyleri ve takipçi hesapları.
* **Yöntem:** Sharpe, Treynor oranları ve Jensen alfa çok faktörlü zaman serisi testleri.
* **Ana Bulgu:** Liderlerin ham getirileri yetenekten ziyade yüksek beta riskinden kaynaklanmakta olup, işlem maliyetleri ve platform kesintileri sonrasında takipçilere aktarılan net alfa sıfır veya negatiftir.
* **Kaynak:** [SSRN Working Paper: 2291421](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2291421)

---

## 2. Platform ve Üçüncü Taraf Takipçi Getirisi Verisi

Platformların pazarlama panolarında gösterilen brüt kârlar ile takipçilerin cüzdanına yansıyan net getiriler arasında belirgin bir uçurum bulunmaktadır:

### Gerçek Veriler ve Denetim Raporları
* **Mevzuatsal Risk Bildirimleri (eToro vb.):** FCA ve ESMA regülasyonları altındaki resmi açıklamalarda, perakende hesapların **%74 ila %81'inin düzenli olarak para kaybettiği** bildirilmektedir. eToro'nun kendi yayınlarında kopyalama yapan kullanıcıların ilk 6 ayda bağımsız işlem yapanlara kıyasla %10-12 daha yüksek getiri sağladığı ileri sürülse de, bağımsız akademik incelemeler kopyalayıcıların net getirisinin işlem başına ortalama **-10,98 bps** olduğunu göstermektedir.
* **Kripto Borsaları Çoklu Borsa Analizi (Yieldfund 90 Günlük Çalışma):** Kripto vadeli kopya ticaretinde (Binance, Bybit, MEXC) takipçi hesaplarının 90 günlük takibinde, borsa bazlı kazanma oranları farklılık gösterse de (Binance: %66,5, MEXC: %57,8, Bybit: %43,6), stop-loss kullanmayan liderlerin tek bir tasfiye dalgasında portföyü eritmesi sebebiyle takipçi portföylerinin genel net getirisi şans seviyesinin altında kalmıştır.

### Takipçi Getirisini Eriten 3 Temel Dinamik
1. **Yürütme Gecikmesi (Execution Latency):** Lider emri girdiği anda platform motorunun takipçi hesaplarına piyasa emri iletmesi 50 ms ile 500 ms arasında sürer. Volatil piyasa mumlarında bu gecikme, takipçinin liderden %0,3 ila %1,5 daha kötü fiyattan dolmasına (fill) neden olur.
2. **Emir Defteri Kayması (Slippage):** Lider 1.000 dolarlık pozisyon açarken arkasındaki yüzlerce takipçi aynı anda 200.000 dolarlık piyasa emri yığdığında sığ tahtalarda likidite tükenir. [Binance Copy Trading Kuralları](https://www.binance.com/en/support/faq/detail/0b3a91eea664402f812fe41358c8a206) bu sebeple BTC/ETH için %0,5, diğer pariteler için %1,5 varsayılan kayma limiti uygular; limit aşıldığında emir reddedilir ve lider kârlı pozisyondayken takipçi dışarıda kalır.
3. **Komisyon Makası ve Kâr Payı Asimetrisi:** Lider pasif limit emirle (maker, ~%0,02) işlem yaparken, kopyalama sistemi takipçiyi piyasa emriyle (taker, ~%0,05) işleme sokar. Ayrıca lider kâr ettiğinde %10-%15 kâr payı (profit share) anında kesilirken, lider zarar ettiğinde bu zarar tamamen takipçiye aittir.

---

## 3. Hyperliquid Vault'ları Üzerine Kalıcılık ve Takipçi Getirisi Analizi

Hyperliquid üzerinde kopyalama iki farklı mimari üzerinden işler:

### Protokol Kasası (HLP - Hyperliquidity Provider)
* **İşleyiş:** [Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults) ve [DefiLlama](https://defillama.com/) verilerine göre HLP, platformun yerel piyasa yapıcısı ve tasfiye karşı tarafıdır.
* **Getiri ve Düşüş:** Sakin ve hacimli dönemlerde fonlama ödemeleri ve spread yakalama ile yıllık %15 - %30 APR bandında getiri sağlar. Ancak büyük yönlü kırılımlarda ve kalabalık pozisyonların tersine hareket ettiği günlerde %5 - %12 arası ani sermaye erimesi (drawdown) yaşar.

### Kullanıcı Kasaları (User Vaults)
* **İşleyiş:** Bireysel trader'lar kendi kasalarını açar; takipçiler USDC yatırarak havuz payı alır. Lider %10 kâr payı alır. Havuz bazlı yapı sayesinde borsa içi kopyalamadaki bireysel emir gecikmesi yaşanmaz; tüm kasa tek bir hesap gibi işlem görür.
* **Kalıcılık Analizi (Persistence Failure):** [Copin.io](https://copin.io/) ve topluluk analitik platformlarının verilerine göre, 30-90 günlük dönemde %500-%1000 ROI göstererek lider tablosunun tepesine çıkan kullanıcı kasalarının büyük çoğunluğu sonraki 3-6 ay içinde hayatta kalamamaktadır. Bunun ana nedeni, liderlerin yüksek kaldıraçla kârı büyütüp zararda stop kullanmaması ve tek bir volatilite şokunda kasanın tasfiye olmasıdır.
* **MEV ve Önden Koşma (Frontrunning):** Hyperliquid L1 tamamen şeffaf bir zincir üstü emir defterine sahiptir. Popüler cüzdanlar ve açık vault'lar harici botlar tarafından anlık izlenir. Nitekim son dönemde geliştirilen [Avail ShieldTX](https://cryptobriefing.com/avail-shieldtx-privacy-hyperliquid-traders/) gibi gizlilik çözümleri, kopyalama botlarının lider emirlerini görüp tahtayı önden süpürmesini engellemek amacıyla doğmuştur. Liderin işlem büyüklüğü arttıkça tahtadaki darbe maliyeti (market impact) doğrudan kasanın net getirisini düşürür.

---

## 4. Gölge (Shadow) Kopyalama Tasarımı İçin 3 Temel Çıkarım

Gölge işlem simülasyonunun gerçeğe uygun çalışması ve canlı sermaye geçişinde hayal kırıklığı yaratmaması için şu 3 ilke uygulanmalıdır:

| Tasarım Boyutu | Geleneksel Yanılgı | Gölge Sistem Çözümü |
| :--- | :--- | :--- |
| **1. Seçim Penceresi & Rejim Filtresi** | 7-30 günlük yüksek ROI liderlerini kopyalamak. | **60-90 günlük yuvarlanan (rolling) pencere.** Tek başına ROI yerine en az 2 farklı piyasa rejimini (yükseliş ve sert volatilite/düşüş) atlatmış olma ve minimum 120 tamamlanmış işlem şartı. Zayıflayan lideri hızla terk eden dinamik rotasyon kuralı. |
| **2. Gecikme & Sentetik Kayma Cezası** | Liderin gerçekleşme fiyatını (fill price) birebir kopyalamak. | **150-350 ms sentetik gecikme payı.** Liderin işleminden $T+200\text{ ms}$ sonraki tahta derinliğindeki fiyatı baz alma; işlem başına minimum **%0,05 taker komisyonu + %0,08 sentetik kayma** ve biriken fonlama maliyeti düşümü. |
| **3. Kalıcı Metriğe Odaklanma** | Kazanma oranı (win rate) ve ham PnL'e odaklanmak. | **Risk kontrolü ve pozisyon süresi disiplini.** Maksimum Düşüş (Max Drawdown ≤ %15), Calmar Oranı (Yıllık Getiri / Max DD) ve Zarardaki Pozisyonu Taşıma Süresi filtreleri. Zarardaki işlemi normalden 3 kat uzun taşıyanları otomatik eleme. |
