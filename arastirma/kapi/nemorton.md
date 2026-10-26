Kısa cevap: **Hayır, bu kapı adil değil.** Aynı zamanda çok cömert (kötü stratejiyi geçirir) ve çok kaba (iyi ama kısa geçmişteki stratejiyi eler). Aşağıda eleştirel değerlendirme, sorularınızı sırayla ve bir öneri yer alıyor. Faydalandığım çalışmalar parantez içinde belirtilmiştir.

---

### 1. Kapının zayıflıkları — sıralı

**Kötü stratejiyi haksız yere geçirme (false positive), büyükten küçüğe:**

1. **Tek geçiş şartı “net getiri > 0”** — en büyük zayıflık. Maliyetli, kenarı yok (rastgele) bir strateji bu eşiği ciddi olasılıkla geçebilir (soru 2’ye bakın). ~1.050 strateji üzerinde bu, otuzlar kadar“sahte başarılı” üretir.
2. **Çoklu test düzeltmesi yok** — DSR hesaplanıyor ama “bilgi amaçlı”, eleme yapmıyor. 933 + 119 deneyde seçim yanlılığı (data mining) kesinlikle var.
3. **2023–2026 büyük ölçüde yükselen piyasa** — çoğu strateji long-only. Ham getiri > 0 olası sadece piyasa beta’sından; alfa yok olabilir.
4. **Farklı sınama süreleri düzleştirilmemiş** — 6 aylık pozitif varyans, 3 yıllıkla aynı eşikte değerlendiriliyor.
5. **Portföy düzeyinde risk bakılmıyor** — korelasyon filtresi tek baz alınan stratejiler için yeterli değil; toplam drawdown, volatilite hedefi yok.
6. **TradingView yayımlama bias’ı** — bir strateji yayımlanmış olması zaten onu “seçilmiş” bir hipotez haline getirir; yayın sonrası out-of-sample test bu tamamen gidermez.

**İyi stratejiyi haksız yere elenme (false negative):**

1. **Yayın tarihinden sonraki zaman dilimi kilidi** — iyi stratejinin en karlı dönemi yayından önceyse elenir (early-adopter / survivorship bias).
2. **%0 net getiri kesin eşiği** — tek kötü ay, bir komisyon değişikliği ya da tekslip, sınırda olan iyi stratejiyi çıkarır.
3. **Sonraki elenme eşikleri (p10 ≤ 0, PF < 1,2)** — p10 güveni kısa örneklemde çok geniş olur; sınırdaki iyi stratejiler buradan çıkar.
4. **Tek sembol + tek zaman dilimi tekilleştirmesi** — strateji başka bir piyasada/dilimde çalışabilir; tek kurulumla tek baştan reddedilir.
5. **Veri yok = test edilemedi (401)** — bu “eleme” değil, bilgi kaybıdır; bu kümelenmiş veri yokluğu strateji uzayı=sız bir görünüm verir.

---

### 2. “Net getiri > 0” geçme şartı uygun mu?

**Hayır. Gerekli, ancak çok yetersiz.**

Rastgele (kenarı yok) bir stratejinin bu kapıdan geçme olasılığı:

- İşlem başına ortalama getiri **maliyet sonrası sıfır**sa (mükemmel adil oyun): *n* işlemde toplam > 0 olasılığı yaklaşık **%50** (Merkezi Limit Teoremi), *n* ne kadar büyük olursa olsun.
- İşlem başına ortalama getiri **maliyet kadar negatif**sa (sadece kayıt gideri, kenar yok):  
  \[
  P(\text{toplam} > 0) = \Phi\left(\frac{-c\sqrt{n}}{\sigma}\right)
  \]
  Örnek: *c* = %0,05/işlem, \(\sigma\) = %1/işlem, *n* = 100 işlem → **≈ %31**; *n* = 20 → **≈ %43**; *n** = 1 000 → **≈ %3**.

Yani kısa işlem sayılı stratejiler bu eşiği çok daha kolay geçer (uç varyans). Binlerce ML ürettiğinde bu eşik büyük ölçüde rastgelelik filtresi olur.

**Nasıl ölçülür:**
- **Monte Carlo / permutasyon:** işlem kayıtlarını karıştırıp (seri korelasyonu bozdukça) binlerce “sahte” equity eğrisi üretip, net > 0 oranını empirical olarak ölç (placebo test).
- **Blok bootstrap:** zaman serisindeki bağlamı koruyarak weekly getiri dağılımı üret.
- **Kapalı form normalyaklaşma:** yukarıdaki formülle ciddi bir tahmin.

---

### 3. Çoklu test / seçim yanlılığı — hangi yöntem pratik?

| Yöntem | Pratiklik | Yorum |
|--------|-----------|-------|
| **DSR (Deflated Sharpe Ratio)** | Çok yüksek | Bailey & López de Prado (2014). Hızlı; deney sayısı *N* ve fazla kıvrancı (kurtosis) düzeltir. Binlerce ML fikir için en uygun ön-taramadır. Eşik: **DSR ≥ 0,95** (%95 güvence Sharpe > 0). |
| **Benjamini–Yekutieli (BHY/FDR)** | Yüksek | Bağımlı testler için false discovery rate kontrolü. q < 0,05–0,10 ile aday kümesini daraltır. (Bailey & López de Prado’ın PBO çalışmasıyla bağlantılı.) |
| **White’s Reality Check (2000)** | Düşük | Bootstrap tabanlı, 가족-wise hata oranı kontrolü. Çok yavaş; sadece finalistenler üzerinde çalıştırılmalı. |
| **Hansen SPA (2005)** | Düşük | White’den güçlüdür ama yine de ağır; sadece son liste üzerinde. |
| **Placebo / rastgele strateji** | Orta | Empirical “gerçek dünya” false positive oranı için en iyi karşılaştırma. Veriyi karıştırarak üretilen başarı oranını gerçek orandan çıkartın. |

**Öneri:** DSR ile **eleme eşiği** koyun (sadece bilgi amaçlı tutmayın); tüm adaylar arasında **BHY FDR kontrolü** uygulayın; son 10–20 finaliste **White/Hansen** çalıştırın. Binlerce ML fikir için White/Hansen’i her biri üzerinde çalıştırmak pratik değildir.

Kaynaklar: Bailey & López de Prado (2014), “The Deflated Sharpe Ratio” ve “Probability of Backtest Overfitting”; White (2000), “A Reality Check for Data Snooping”; Hansen (2005), SPA; Benjamini & Yekutieli (2001).

---

### 4. Yükselen piyasada long-only stratejilerde piyasa etkisini ayırmanın yolu

**Al-ve-tut (B&H) karşılaştırması yeterli değildir.** Yüksek beta’lı bir long strateji 2023–2026’da B&H’yi yenecek ama alfa sıfır (ya da negatif) olabilir.

Doğru yaklaşım:

- **Strateji fazlası getirisini piyasa fazlası getirisine regresyon et:** CAPM veya Fama–French 3/5 faktör modeli (Fama & French, 1993). Maliyet sonrası **alfa ve t-istatistiğine** bak; alfa ≤ 0 ya da *t* ≤ 1,65 (%90 güvence) ise elenin.
- **Rolling beta kullan:** Kripto ve 15 dk’lık verilerde beta sabit değildir; sabit beta varsayımı hatalı sonuç verir.
- **Ek raporlar:** up-market / down-market capture, korelasyon, β-ajustlı Sharpe (Treynor).
- **Kesin kural:** ham getiri > 0 ve B&H’den yüksek olmak **yeterli kabul edilemez**. α > 0 ve istatistiksel olarak anlamlı olmalı.

---

### 5. Farklı sınama sürelerini (6 ay – 3 yıl) adil karşılaştırma

- **Ham toplam getiriyi kıyaslama:** adil değil. Yıllıklaştırılmış Sharpe, Calmar ya da Sortino kullanın.
- **Minimum eşik koyun:** ≥ 1 yıl ve ≥ 50–100 işlem. 6 aylık deneyi “kısa sınama” etiketleyin ve paper trade’e almayın (ya da çok daha yüksek eşektan geçirin).
- **Güven aralığı genişliğiyle cezalandırın:** kısa örneklemde p10 çok geniş olur; blok bootstrap p10 ≤ 0 olanları otomatik elenin.
- **Stabilite istedi:** en az 2–3 alt dönemde (veya walk-forward) aynı işarette getiri.

---

### 6. Binlerce ML ürettiğinde bu kapı ne bozulur? Nasıl tasarlanmalı?

Bozulanlar:

- **Çoklu karşılaştırma patlaması:** binlerce deneyde rastgele “karlı” görünecek strateji bulma olasılığı yaklaşık 1’e yaklaşır (Bailey & López de Prado, 2014).
- **Aynı veri seti üzerinde tekrar test = aşırı uygunluk (overfitting).** DSR’deki *N* (gerçek deney sayısı) tüm başarısız deneyleri de içermelidir.
- **Backtest overfitting,** out-of-sample yoksa kaçınılmazdır.

Tasarım ilkeleri:

- **Kesin bir hold-out (out-of-sample) verisi tutun:** ML ürettiği hiçbir stratejinin bu veride değerlendirilmesi sırasında model üretimine katkısı olmasın.
- **Kombinasyonlu çapraz doğrulama (combinatorial purged cross-validation)** ve DSR ile deney sayısını cezalandırın (López de Prado, 2018).
- **Parametre hassasiyeti eşiği:** yakın parametrelerin (±10 %) aynı işarette getiri vermesi zorunlu kılın.
- **Son kapı her zaman canlı paper trade (26 hafta) olsun.** Backtest geçmişi bir filtre, garantisi değildir.

---

### 7. Önerilen kapı — somut adımlar ve eşikler

**Adım 1 — Birlikte / veri (otomatik kill)**
- Geleceği görme (look-ahead) kontrolü: kod ve olay sırası.
- Delisting / survivorship bias yok; kopya veri yok.
- Minimum veri süresi: **1 yıl**; minimum işlem sayısı: **50** (15 dk+ için 100 önerilir).

**Adım 2 — Gerçekçi maliyet modeli**
- Kripto: gerçek maker/taker komisyonu + 1–2 tick slippage.
- Hisse/ETF: %0,05/taraf + 1 tick (veya broker gerçekçi modeli).
- Short varsa borrow maliyeti dahil.

**Adım 3 — Temel karlılık (gerekli, yeterli değil)**
- Net getiri > 0 — geçmezse direkt çık.
- Profit factor ≥ **1,25**.
- Max drawdown ≤ **%30** (ya da Calmar ≥ 0,5).
- After-cost Sharpe ≥ **1,0** (hisse/ETF) — tek bir eşik istiyorsanız tüm varlık sınıfı için Sharpe ≥ 1,0.

**Adım 4 — Çoklu test düzeltmesi (eleme eşiği)**
- **DSR ≥ 0,95** (gerçek deney sayısı *N* ile hesaplanmalı).
- **BHY FDR q < 0,10** tüm adaylar arasında.
- Blok bootstrap haftalık getiri p10 > 0 (%90 güven).

**Adım 5 — Piyasa etkisi / alfa**
- CAPM/FF3 alfa > 0, **t-stat > 1,65**, maliyet sonrası.
- β raporu; up/down capture; B&H karşılaştırması rapor olarak (alfa t ≤ 1,65 ise çıkarsın).

**Adım 6 — Kararlılık**
- En az 2–3 alt dönemde / walk-forward pozitif getiri.
- Yakın parametreler aynı işarette.

**Adım 7 — Portföy düzeyi filtreleri**
- Çiftler aralık getiri korelasyonu |ρ| < **0,6** (rolling).
- Tek enstrüman üst sınırı (ör. portföyde %20).

**Adım 8 — Out-of-sample / paper trade**
- Aynı veri üzerinde optimizasyon ve değerlendirme bir arada olamaz.
- Minimum **12–26 hafta paper trade**, gerçek slippage ile.
- Canlı performans backtest beklentisinden belirli oranda (ör. %50) düşerse çıkar.

**Adım 9 — İnsan denetimi**
- İki bağımsız denetçi; kod incelemesi; mantıksal hipotez kontrolü.

---

### Beklenen etki

Mevcut akışınızda ~181 strateji “geçti”; yukarıdaki eşiklerle final listenin büyük kısmı (muhtemelen %70–%90) çıkar, ancak kalanın gerçek alfa taşıması olasılığı çok daha yüksek olur. Mevcut kapının en kritik hatası, **“net getiri > 0” ile çoklu test düzeltmesinin yokluğu**dır; bu, 2023–2026 bull piyasasında long-only stratejilerle beraber büyük miktarda “sahte başarılı” üretmeye devam eder.

**Kaynaklar:**
- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio*; (2014), *Probability of Backtest Overfitting*, Journal of Alternative Investments.
- White (2000), *A Reality Check for Data Snooping*, Econometrica.
- Hansen (2005), *A Test for Superior Predictive Ability*, JBES.
- Benjamini & Yekutieli (2001), FDR control under dependence.
- López de Prado (2018), *Advances in Financial Machine Learning*.
- Fama & French (1993), *Common risk factors in the returns on stocks and bonds*.