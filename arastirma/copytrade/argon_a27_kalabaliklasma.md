> **Lider denetim notu (2026-10-29):** Argon A27. Fikirler doğru, iki düzeltme gerekli: (1) Net maruziyet formülünde nosyonel
> büyüklük kaldıraçla bir kez daha çarpılıyor; nosyonel zaten kaldıraçlıdır → çift sayım. Doğrusu: kopya portföyündeki
> ağırlık × (pozisyon nosyoneli / trader hesap değeri). (2) Etkin trader sayısı trader'ın kendi büyüklüğüyle değil, bizim
> kopya ağırlığımızla hesaplanmalı (eşit ağırlıkta 18 olur; asıl bilgi coin/yön yoğunlaşmasında). "Yeni bakiye yatıran
> kullanıcıya uyarı" bizim için geçersiz. Ang & Chen (2002) kaynağı doğru. Düşüş korelasyonu 18 kişide aylar ister (Argon da
> söylüyor). **Kullanım:** coin başına net yön payı + aynı yön sayısı, panoda tek satır uyarı (otomasyon yok).

# Sanal Kopya Odası Portföy Risk ve Yığılma Yönetimi

Bu doküman, 18 trader'dan oluşan bir sanal kopya ticaret (copy trading) odasında sakin piyasa koşullarında bağımsız görünen stratejilerin stres/düşüş günlerinde aynı yönde kümelenmesiyle oluşan tekil yönlü maruziyet (crowding) ve kuyruk bağımlılığı riskini izlemek için geliştirilen operasyonel risk kılavuzudur.

---

## 1. Hesaplanabilen Temel Risk Ölçütleri

Mevcut veriler (saatlik pozisyonlar, günlük getiri serileri ve 1 dakikalık mumlar) kullanılarak hesaplanacak 4 temel metrik aşağıdadır:

### 1.1. Coin Başına Net Maruziyet Payı (Oda Net Maruziyeti)
* **Amaç:** Toplam kaldıraca göre düzeltilmiş oda riskinin tek bir coine ve tek bir yöne ne derecede yığıldığını ölçer.
* **Formül:**
  $$\text{Net Maruziyet}_c = \frac{\left| \sum_{i=1}^{18} d_{i,c} \cdot S_{i,c} \cdot L_{i,c} \right|}{\sum_{k} \sum_{i=1}^{18} S_{i,k} \cdot L_{i,k}}$$
  * $d_{i,c} \in \{+1, -1\}$: Trader $i$'nin $c$ coinindeki işlem yönü (+1 Long, -1 Short).
  * $S_{i,c}$: Pozisyonun nosyonel (nominal) büyüklüğü (USD cinsinden).
  * $L_{i,c}$: Kullanılan kaldıraç çarpanı.
  * Payda: Odadaki tüm coinlerin toplam brüt kaldıraçlı büyüklüğü.
* **Gereken Veri:** Saatlik açık pozisyon tablosu (coin, yön, nosyonel hacim, kaldıraç).
* **Uyarı Eşiği:** Tek bir coin için $> \%35$.
* **Gerekçesi:** 18 farklı trader takip edilse dahi, sermayenin yönlü net maruziyetinin %35'inden fazlası tek bir varlığa bağlıysa, sistemik bir likidasyon veya sert iğne atma durumunda oda tek bir varlığın volatilitesine teslim olur.

### 1.2. Etkin Bağımsız Trader Sayısı ($N_{eff}$)
* **Amaç:** Trader'lar arasındaki sermaye/risk dengesini ölçerek fiili çeşitlenmeyi belirler.
* **Formül:** Trader $i$'nin toplam oda riski içindeki payı $w_i = \frac{\sum_c S_{i,c} \cdot L_{i,c}}{\sum_{j=1}^{18} \sum_c S_{j,c} \cdot L_{j,c}}$ olmak üzere ters Herfindahl indeksi:
  $$N_{eff} = \frac{1}{\sum_{i=1}^{18} w_i^2}$$
* **Gereken Veri:** Saatlik açık pozisyon büyüklükleri ve kaldıraçları.
* **Uyarı Eşiği:** $N_{eff} < 6.0$.
* **Gerekçesi:** [Herfindahl-Hirschman İndeksi (HHI)](https://en.wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index) ve [Attilio Meucci'nin Etkin Bahis Sayısı](https://www.bayes.citystgeorges.ac.uk/__data/assets/pdf_file/0003/213699/Meucci-ReDefining-and-Managing-Diversification.pdf) prensibine dayanır. Kağıt üzerinde 18 kişi işlem yapsa bile, 2-3 trader devasa kaldıraç veya bakiye ile pozisyon açtığında fiili risk tek merkezde toplanır. $N_{eff} < 6$, odanın 18 kişi tarafından değil fiilen 3-4 kişi tarafından sürüklendiğini gösterir.

### 1.3. Aynı Coinde Yönsel Çakışma Oranı (Sürüleşme Payı)
* **Amaç:** Belirli bir coin üzerinde işlem yapan trader'ların kaçının aynı yöne kümelendiğini belirler.
* **Formül:** $c$ coininde açık pozisyonu bulunan aktif trader sayısı $N_c$ olmak üzere:
  $$\text{Çakışma}_c = \frac{\max\left( N_{c,\text{Long}}, N_{c,\text{Short}} \right)}{N_c}$$
* **Gereken Veri:** Saatlik açık pozisyonlar (coin, yön ve aktif trader sayısı).
* **Uyarı Eşiği:** $N_c \ge 6$ olmak şartıyla $\text{Çakışma}_c \ge \%80$ (veya 18 trader'dan en az 10'unun aynı coin ve aynı yönde olması).
* **Gerekçesi:** Düşüş günlerinde tüm trader'lar aynı makro panikle örneğin ETH Short pozisyonuna geçerse, odanın stratejik bağımsızlığı sıfırlanır. Ani bir kısa sıkışmada (short squeeze) tüm portföy aynı anda stop/tasfiye olur.

### 1.4. Düşüş Koşullu Getiri Korelasyonu (Aşağı Yönlü Kuyruk Bağımlılığı)
* **Amaç:** Normal günlerde düşük korelasyonlu görünen trader'ların piyasa düşüş anlarında senkronize batma eğilimini ölçer.
* **Formül:** Piyasa getirisi $R_{m,t}$ belirli bir negatif eşiğin altına indiğinde ($R_{m,t} < -\%3$) trader ikilileri arasındaki getiri korelasyonu:
  $$\rho_{i,j}^- = \text{Corr}(r_{i,t}, r_{j,t} \mid R_{m,t} < -\%3)$$
  Oda genel korelasyon skoru ise 153 ikili çiftin ortalamasıdır:
  $$\bar{\rho}^- = \frac{2}{18 \times 17} \sum_{i < j} \rho_{i,j}^-$$
* **Gereken Veri:** Günlük getiri serileri ($r_{i,t}$) ve 1 dakikalık mumlardan türetilen piyasa endeksi/BTC getirisi ($R_{m,t}$).
* **Uyarı Eşiği:** $\bar{\rho}^- > 0.60$ veya koşullu düşüş korelasyonunun genel sakin gün korelasyonundan farkı $(\bar{\rho}^- - \bar{\rho}_{\text{genel}}) > 0.30$.
* **Gerekçesi:** [Ang ve Chen (2002)](https://doi.org/10.1016/S0304-405X(02)00068-5) çalışmasında kanıtlanan asimetrik korelasyon riski: Varlıklar ve fon yöneticileri düşüş anlarında normal piyasaya göre çok daha senkronize hareket eder ("birlikte batma" etkisi).

---

## 2. Eşik Aşımında Operasyonel Süreç ve Panoda Gösterim

### 2.1. Uygulanacak Protokol
Sistem politikanız gereği **kesinlikle otomatik emir iptali, zorla pozisyon kapatma veya kaldıraç düşürme yapılmaz**. Süreç tamamen bilgilendirme ve koruyucu risk farkındalığı odaklıdır:
1. **Görsel Rozet Tetikleme:** Pano üzerinde ilgili coinin satırı kırmızı/sarı alarm moduna geçer.
2. **Kopya Dağıtım Uyarı Bayrağı:** Odaya yeni bakiye yatıran veya yeni pozisyon kopyalayacak kullanıcılara *"Bu varlıkta yüksek yönlü yoğunlaşma tespit edildi"* uyarısı gösterilir.
3. **Manuel İnceleme Günlüğü:** Risk yöneticisine durum kaydı (log) iletilir.

### 2.2. Panoda Tek Satır Gösterim Formatı
İzleme ekranında karmaşık tablolar yerine tek bakışta anlaşılan standart tek satır şablonu:

```text
[🔴 UYARI: YIĞILMA] ETH/USDT | 13/18 Trader SHORT (%87) | Net Maruziyet: %44.2 (Eşik: %35) | Etkin Trader: 4.8 (Min: 6.0) | Durum: İzlemede (Otomasyon Yok)
```

---

## 3. 18 Kişilik Küçük Örneklemde Güvenilirlik ve Gereken Veri Süresi

Ölçütlerin istatistiksel gücü, verinin anlık durum mu yoksa tarihsel tahmin mi olduğuna göre ikiye ayrılır:

### 3.1. Pozisyon Tabanlı Anlık Ölçütler (Net Maruziyet, $N_{eff}$, Çakışma Oranı)
* **Güvenilirlik:** **%100 deterministiktir.** İstatistiki tahmin hatası, serbestlik derecesi kaybı veya örneklem varyansı içermez. O anki açık defterin kesin aritmetik yansımasıdır.
* **Gereken Veri:** **0 gün geçmiş gerekir.** Yalnızca ilgili saatin anlık açık pozisyon dökümü yeterlidir.

### 3.2. Getiri Tabanlı Korelasyon Ölçütleri (Düşüş Korelasyonu)
* **Güvenilirlik ve Kısıt:** 18 trader için $18 \times 17 / 2 = 153$ serbest ikili korelasyon parametresi tahmin edilir. [Marchenko-Pastur Dağılımı](https://en.wikipedia.org/wiki/Marchenko%E2%80%93Pastur_distribution) ve rastgele matris teorisi uyarınca kovaryans matrisinin gürültüden arınması için gözlem sayısının trader sayısının en az 3–5 katı ($T \ge 60\text{--}90$) olması gerekir.
* **Gereken Veri Süresi:**
  * **Günlük Getiri İle:** Sert piyasa düşüş günleri zamanın yalnızca %10–15'ini oluşturduğundan, düşüş koşulunu sağlayan yeterli veri noktasına ulaşmak için en az **180–250 işlem günü** gerekir. 18 kişilik küçük grupta 30 günlük günlük veriyle korelasyon hesaplamak tamamen istatistiki gürültü üretir.
  * **1 Dakikalık Mumlar İle (Tavsiye Edilen):** Elinizdeki 1 dakikalık mumlar üzerinden trader'ların saatlik veya gün içi realize getirileri hesaplanarak yüksek frekanslı korelasyona geçilebilir. Bu yöntemle **30–45 günlük veri**, istatistiksel olarak güvenilir bir düşüş korelasyonu üretmek için yeterli hale gelir.

---

## 4. Akademik Kaynaklar ve Doğrulama Durumu

* **Etkin Bahis ve Çeşitlenme Ölçümü:** [Attilio Meucci — Managing Diversification / Effective Number of Bets](https://www.bayes.citystgeorges.ac.uk/__data/assets/pdf_file/0003/213699/Meucci-ReDefining-and-Managing-Diversification.pdf) ve [Herfindahl-Hirschman Yoğunlaşma İndeksi](https://en.wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index).
* **Asimetrik Düşüş Korelasyonu ve Kuyruk Riski:** [Andrew Ang & Joseph Chen (2002) — Asymmetric Correlations of Equity Portfolios](https://doi.org/10.1016/S0304-405X(02)00068-5).
* **Küçük Örneklem Kovaryans Gürültüsü ve Matris Sönümleme:** [Marchenko-Pastur Yasası ve Finansal Korelasyon Matrisleri](https://en.wikipedia.org/wiki/Marchenko%E2%80%93Pastur_distribution).
* **Kripto Kopya Odalarına Özel Resmî Eşik Değerleri:** Kripto sosyal ticaretine ilişkin evrensel veya regüle edilmiş standart bir eşik değeri akademik literatürde **doğrulanamadı**; dokümanda önerilen %35 maruziyet ve %80 çakışma sınırları hedge fon risk yönetimi standartlarından uyarlanmış ampirik heuristiklerdir.
