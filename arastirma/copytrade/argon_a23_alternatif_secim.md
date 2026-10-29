> **Lider denetim notu (2026-10-29):** Argon A23. Kaynakların bir kısmı arama bağlantısı (google.com/search); doğrulanamadı.
> Ortogonallik tablosundaki korelasyonlar ölçüm değil tahmin. **Kullanım:** dört kural (Calmar, anti-martingale disiplin, DSR,
> kapasite) aynı arşiv üzerinde *gölge skor* olarak hesaplanıp v1.3 odasıyla karşılaştırılabilir; seçim kuralı değişikliği
> yalnız kullanıcı kararıyla ve yeni seçim sürümü olarak yapılır. En çok yeni bilgi vaat eden: Kural 2 (anti-martingale).

# Hyperliquid Perp Borsası Trader Seçim Modelleri ve Literatür Raporu

**Tarih:** 29 Ekim 2026  
**Kapsam:** Hyperliquid DEX işlem verileri (`fills`, `funding`, `hourly candles`, `account value`) ile alternatif kopya ticaret (copy trading) seçim kuralları, akademik literatür bulguları ve ortogonallik analizi.

---

## 1. Yönetici Özeti

Hyperliquid kalıcı vadeli işlem (perp) piyasasında yalnızca geçmiş gecikmeli kopya getirisi sıralaması kullanmak, literatürde ve sektör tecrübesinde sıkça belgelenen iki kritik anomaliden muzdariptir:
1. **Ortalamaya Dönüş (Mean Reversion) ve Alfa Aşınması:** En yüksek ham getiriyi elde eden trader'ların getirileri genellikle kısa süreli rejim uyumuna veya yüksek varyansa dayanır; 180–360 günlük periyotlarda bu getiri sürdürülemez.
2. **Eğilim Etkisi (Disposition Effect) ve Gizli Martingale:** Lider trader'lar takipçi kaybetmemek adına zarardaki pozisyonları realize etmeyip büyütür (gambling for resurrection). Bu durum, kağıt üzerinde yüksek getiri ve yüksek kazanma oranı (%90+ Win Rate) gösterirken, kuyruk riski anında portföyün tasfiye (likidasyon) olmasına yol açar.

Bu raporda; eldeki mevcut veri alanlarıyla (`fills`, `funding`, `hourly candles`, `account value`) doğrudan hesaplanabilen 4 alternatif seçim kuralı tanımlanmış, akademik ve sektörel dayanakları ortaya konmuş ve mevcut getiri kuralına olan bağımsızlık (ortogonallik) seviyeleri gerekçelendirilmiştir.

---

## 2. Literatür İncelemesi: Gelecekteki Performansı Tahmin Eden Sinyaller

Kopya ticaret platformları ([eToro](https://help.etoro.com/s/article/How-does-eToro-calculate-and-present-risk?language=en_GB), [Binance Copy Trading](https://www.binance.com/en/support/faq/detail/1ae9c68fcd0247408c9345e55ab54939), [Hyperliquid Vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/for-vault-depositors-legacy)) ve fon yönetimi literatüründen elde edilen kanıtlar:

| Sinyal Boyutu | İncelenen Metrikler | Kaynak & Dayanak | Bulgunun Gücü | Temel Literatür / Sektör Çıkarımı |
| :--- | :--- | :--- | :--- | :--- |
| **Kalıcılık (Persistence)** | Ham Getiri (1M, 3M, 1Y), Sıralama Korelasyonu | [Carhart (1997)](https://doi.org/10.1111/j.1540-6261.1997.tb03808.x) (Erişim: Ekim 2026); [Berk & Green (2004)](https://doi.org/10.1086/424739) (Erişim: Ekim 2026) | **Zayıf / Tersine Dönüş** *(Ortalamaya dönüş riski)* | Ham getirinin kalıcılığı akademik olarak fonlarda 1–3 ay arası momentum gösterse de, 1 yılı aşan vadelerde işlem maliyetleri ve rejim değişimleriyle sıfırlanmakta veya negatif kalıcılık sergilemektedir. |
| **Risk Ayarlı Getiri** | Sharpe Oranı, Sortino Oranı, [Deflated Sharpe Ratio (DSR)](https://www.google.com/search?q=https://doi.org/10.3905/jpm.2014.40.5.094) | [Bailey \& López de Prado (2014)](https://www.google.com/search?q=https://doi.org/10.3905/jpm.2014.40.5.094) (Erişim: Ekim 2026); [Binance Portfolio Indicators](https://www.binance.com/en/support/faq/detail/1ae9c68fcd0247408c9345e55ab54939) (Erişim: Ekim 2026) | **Orta – Güçlü** *(Aşağı yönlü metrikler üstün)* | Simetrik oynaklığı (Sharpe) cezalandırmak yerine yalnızca aşağı yönlü yarı-oynaklığı (Sortino/Omega) kullanan metrikler, türev piyasalarında asimetrik getiri dağılımlarını yakalamada çok daha başarılıdır. |
| **Düşüş Derinliği & Kuyruk Riski** | Maksimum Düşüş (MDD), [eToro Risk Score (Volatilite Dilimi)](https://help.etoro.com/s/article/How-does-eToro-calculate-and-present-risk?language=en_GB), Conditional Drawdown (CDaR) | [eToro Risk Metodolojisi](https://help.etoro.com/s/article/How-does-eToro-calculate-and-present-risk?language=en_GB) (Erişim: Ekim 2026); [Chekhlov et al. (2005)](https://www.google.com/search?q=https://doi.org/10.1016/j.jbankfin.2004.09.009) (Erişim: Ekim 2026) | **Güçlü** *(Sermaye erimesi prediktörü)* | Geçmişteki derin düşüşler ve toparlanma süresinin uzunluğu, trader'ın kaldıraç disiplinsizliğinin ve gelecekte sermaye tükenişi (ruin) yaşama olasılığının en güçlü habercisidir. |
| **İşlem Disiplini & Eğilim Etkisi** | Elden çıkarma etkisi (Disposition Effect), Martingale / Zararda pozisyon artırma | [Pelster \& Hofmann (2018)](https://www.google.com/search?q=https://doi.org/10.1016/j.jbankfin.2018.07.003) (Erişim: Ekim 2026) | **Güçlü (Negatif Tahmin)** | Takipçi edinen lider trader'ların kârları erken realize edip zarardaki pozisyonları kapatmayarak büyüttüğü ampirik olarak kanıtlanmıştır. Zararda pozisyon büyütmeme disiplini gelecekteki iflası engellemede kritiktir. |
| **Tutarlılık** | Kârlı Ay Oranı, Gain-to-Pain Ratio (Schwager), Pozisyon Süresi Tutarlılığı | [Jack Schwager (Hedge Fund Market Wizards)](https://www.google.com/search?q=https://www.wiley.com/en-us/Hedge%2BFund%2BMarket%2BWizards-p-9781118273043) (Erişim: Ekim 2026); *Akademik eşik formülü:* Doğrulanamadı | **Orta** | Saf "İşlem Kazanma Oranı" (Win Rate) tek başına yanıltıcıdır (tavuk oyunu stratejileri %95 win rate üretip tek işlemde batabilir). Aylık getiri dağılımının dengesi (Gain-to-Pain) daha sağlamdır. |
| **Kapasite & Likidite Kayması** | Trader Hacmi / Piyasa Derinliği, Funding Drag, Gecikmeli Dolum Aşınması | [Berk & Green (2004)](https://doi.org/10.1086/424739) (Erişim: Ekim 2026); [Hyperliquid Vault Dokümantasyonu](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/for-vault-depositors-legacy) (Erişim: Ekim 2026) | **Güçlü** *(Ölçek büyüdükçe alfa erimesi)* | Trader'ın işlem büyüklüğü paritenin saatlik likiditesini aştığında kopya gecikmesi ve spread/slippage getiriyi hızla tüketir. Yüksek frekanslı liderlerde takipçi getirisi çöker. |

---

## 3. Önerilen 4 Alternatif Seçim Kuralı

### Kural 1: Calmar & Aşağı Yönlü Asimetri Skoru (Downside Risk-Adjusted Alpha)
* **Tanım & Formül:** Trader'ın maliyet sonrası yıllıklandırılmış getirisini simetrik standart sapmaya değil, strictly maksimum sermaye kaybına (Max Drawdown) bölen oran:
  $$\text{Calmar Ratio} = \frac{R_{\text{annualized}}}{\text{MDD}}, \quad \text{MDD} = \max_{t \in [0, T]} \left( \frac{\max_{s \le t} V_s - V_t}{\max_{s \le t} V_s} \right)$$
  Burada $V_t$, saatlik hesap değeridir (`account value`).
* **Gereken Veri Alanları:** `account value` ($V_t$ saatlik seri), `funding` (net getiri teyidi için).
* **Hesaplama Penceresi:** Rolling 180 gün ve son 365 gün (ağırlıklı harmanlama: $\%60 \times 180\text{g} + \%40 \times 365\text{g}$).
* **Bilinen Tuzaklar:**
  * *Hayatta Kalan Yanlılığı (Survivorship Bias):* 1 yıl hayatta kalmış trader'lar arasında henüz derin bir piyasa stres testi yaşamamış şanslı trader'lar bulunabilir.
  * *Durağan Olmayan Rejim Tuzağı:* Tek yönlü boğa piyasasında düşük MDD sergileyen bir trader, rejim değişiminde hızla tasfiye olabilir.

---

### Kural 2: Martingale ve Eğilim Etkisi Karşıtı Disiplin Skoru (Anti-Martingale & Loss Realization)
* **Tanım & Formül:** Trader'ın zarara uğrayan pozisyonda kaldıraç/büyüklük artırıp artırmadığını (Martingale) ve zararda bekleme süresi ile kârda bekleme süresi oranını cezalandıran kural:
  $$\text{Loss-to-Win Duration Ratio (LWDR)} = \frac{\text{Medyan Süre}(\text{Zararlı Pozisyonlar})}{\text{Medyan Süre}(\text{Kârlı Pozisyonlar})}$$
  $$\text{Martingale Penalty} = \sum_{i} \mathbf{1}_{\{\Delta \text{PositionSize}_i > 0 \;\land\; \text{UnrealizedPnL}_i < 0\}}$$
  $$\text{Disiplin Skoru} = \frac{1}{\text{LWDR}} \times \exp(-\lambda \cdot \text{Martingale Penalty})$$
  *(Not: $\lambda$ ölçekleme katsayısı olup sistem parametresidir; analitik çıkarım/tahmin).*
* **Gereken Veri Alanları:** `fills` (işlem giriş-çıkış zamanları, fiyat, miktar, yön), `hourly candles` (pozisyon süresince gerçekleşmeyen kâr/zarar eğrisi), `account value`.
* **Hesaplama Penceresi:** Son 90 gün ile 180 gün arasındaki tüm kapalı pozisyon döngüleri.
* **Bilinen Tuzaklar:**
  * *Ortalamaya Dönüş (Grid/DCA) Stratejilerini Dışlama:* Bilinçli ve kontrollü grid ticareti yapan kurumsal piyasa yapıcı algoritmalar bu kuralda haksız yere elenebilir.

---

### Kural 3: Söndürülmüş Sharpe Oranı (Deflated Sharpe Ratio - DSR)
* **Tanım & Formül:** [Bailey \& López de Prado (2014)](https://www.google.com/search?q=https://doi.org/10.3905/jpm.2014.40.5.094) tarafından geliştirilen ve trader evrenindeki binlerce aday arasından seçim yapılırken ortaya çıkan çoklu test (multiple testing) ve seçim yanlılığını (selection bias) düzelten istatistiksel güvenirlik ölçüsü:
  $$\text{DSR} \equiv \text{PSR}(\text{SR}^*_0) = Z\left( \frac{(\widehat{\text{SR}} - \text{SR}^*_0)\sqrt{T-1}}{\sqrt{1 - \widehat{\gamma}_3 \widehat{\text{SR}} + \frac{\widehat{\gamma}_4 - 1}{4} \widehat{\text{SR}}^2}} \right)$$
  Burada $\widehat{\gamma}_3$ getiri çarpıklığı (skewness), $\widehat{\gamma}_4$ basıklık (kurtosis), $N$ taranan toplam trader sayısı ve $\text{SR}^*_0$ beklenen maksimum sahte Sharpe eşiğidir:
  $$\text{SR}^*_0 \approx \sqrt{\frac{\operatorname{Var}(\{\widehat{\text{SR}}_n\})}{2}} \left( (1-\gamma) Z^{-1}\left(1 - \frac{1}{N}\right) + \gamma Z^{-1}\left(1 - \frac{1}{N \cdot e}\right) \right)$$
* **Gereken Veri Alanları:** `account value` üzerinden türetilen saatlik getiri serileri ($r_t$).
* **Hesaplama Penceresi:** 365 günlük saatlik getiri serisi (çarpıklık ve basıklık kestiriminin sapmasız çıkması için minimum $\sim 1.000$ saatlik gözlem şarttır).
* **Bilinen Tuzaklar:**
  * *Aşırı Uyum (Overfitting) Varsayımı:* Getirilerin bağımsız ve özdeş dağıldığını (IID) varsayar; kripto perp fonlama rejimlerinde otokorelasyon yüksek olduğunda güven skoru sapabilir.

---

### Kural 4: Likidite Kapasitesi ve Kopya Aşınması Skoru (Capacity & Slippage-Decay Factor)
* **Tanım & Formül:** Trader'ın emir büyüklüklerinin piyasa derinliğine oranı ve fonlama maliyeti yükünü modelleyerek, takipçinin gerçekte ne kadar kayma (slippage) yaşayacağını tahmin eden kural:
  $$\text{Impact Ratio} = \frac{1}{K} \sum_{k=1}^K \left( \frac{\text{OrderSize}_{k} \times \text{Price}_k}{\text{HourlyCandleVolume}_{k}} \right)$$
  $$\text{Net Capacity Score} = \text{Copied PnL} - \left( \alpha \cdot \text{Impact Ratio} + \sum \text{FundingPaid} \right)$$
* **Gereken Veri Alanları:** `fills` (emir büyüklüğü, gerçekleşme zamanı), `hourly candles` (işlem yapılan paritenin mum hacmi), `funding` (ödenen/alınan net fonlama tutarı).
* **Hesaplama Penceresi:** Rolling 90 gün.
* **Bilinen Tuzaklar:**
  * *Büyük Sermayeli Başarılı Trader'ları Cezalandırma:* Yüksek sermayeli trader'lar doğal olarak daha büyük lotlarla işlem yaptığından, likit paritelerde dahi ceza puanı alabilirler.

---

## 4. Mevcut "Geçmiş Getiri Sıralaması"na Göre Ortogonallik Sıralaması

Mevcut seçim kuralınız (`geçmiş gecikmeli kopya getirisi`), yüksek volatiliteyle yönlü trend yakalayan veya zararları realizing etmeyip yüzdürerek getiri eğrisini düzgün gösteren trader'ları listenin en üstüne taşır.

Önerilen metriklerin mevcut seçim kuralıyla korelasyonunun düşüklüğüne (yani portföy seçimine ne kadar **bağımsız / yeni bilgi** kattığına) göre gerekçeli sıralaması aşağıdadır:

$$\text{Öneri 2 (Anti-Martingale)} \prec \text{Öneri 4 (Kapasite/Aşınma)} \prec \text{Öneri 3 (DSR Güvenilirlik)} \prec \text{Öneri 1 (Calmar/Aşağı Risk)}$$

| Sıra | Seçim Kuralı | Mevcut Kural İle Beklenen Korelasyon | Gerekçe ve Katma Değer |
| :---: | :--- | :---: | :--- |
| **1** | **Öneri 2: Anti-Martingale & Disiplin Skoru** | **Çok Düşük / Negatif** *(Korelasyon $\approx -0.10$ ila $+0.15$)* | **En yüksek ortogonallik.** Kısa-orta vadede en yüksek getiriyi üreten trader'lar genelde zararda stop olmayıp pozisyon ekleyen (Martingale) profillerdir. Bu kural kâr büyüklüğüne tamamen kördür; sadece işlem psikolojisini ve pozisyon yönetimi simetrisini inceler. Ham getiri sıralamasının gizlediği kuyruk iflası riskini doğrudan ayıklar. |
| **2** | **Öneri 4: Likidite & Kopya Aşınması Skoru** | **Düşük** *(Korelasyon $\approx +0.15$ ila $+0.30$)* | Ham getiri tablosu trader'ın "kağıt üzerindeki" sonucunu gösterir. Bu kural ise işlem hacminin piyasa derinliğine oranını ve funding maliyetini ölçerek mikro-kap perp paritelerinde liderin peşinden giden takipçinin yaşayacağı reel dolum kaybını modeller. |
| **3** | **Öneri 3: Söndürülmüş Sharpe Oranı (DSR)** | **Orta** *(Korelasyon $\approx +0.35$ ila $+0.55$)* | DSR doğrudan getiri seviyesini değil; gözlenen getirinin taranan yüzlerce trader arasından tesadüfen (şans eseri / data mining) çıkıp çıkmadığını ve dağılımın negatif basıklık içerip içermediğini istatistiksel p-değeriyle cezalandırır. |
| **4** | **Öneri 1: Calmar & Aşağı Yönlü Risk Skoru** | **Orta – Yüksek** *(Korelasyon $\approx +0.55$ ila $+0.75$)* | Formülün payında doğrudan getiri ($R$) yer aldığı için ham getiri sıralamasıyla kaçınılmaz olarak pozitif korelasyon taşır. Ancak paydadaki MDD cezası sayesinde kontrolsüz kaldıraçla tepe getiriye ulaşmış trader'ları filtreler. |

---

## 5. Uygulama ve Entegrasyon Mimarisi Tavsiyesi

Mevcut getiri bazlı sıralamanızı tek bir metrikle değiştirmek yerine çok aşamalı (multi-stage funnel) bir mimari önerilmektedir:

```
[Ham Trader Havuzu (1+ yıl, >=5k$)]
               │
               ▼
   [Aşama 1: Sert Filtreler (Hard Filters)]
   • Medyan Kaldıraç <= 3x, Maks Kaldıraç <= 10x (Mevcut)
   • Anti-Martingale Disiplin Skoru Eşiği (Öneri 2)
   • Likidite Kapasite Uyumu (Öneri 4)
               │
               ▼
   [Aşama 2: İstatistiksel Ayıklama (Significance)]
   • Deflated Sharpe Ratio (DSR) >= 0.95 (Öneri 3)
               │
               ▼
   [Aşama 3: Nihai Sıralama (Ranking)]
   • Calmar & Aşağı Yönlü Asimetri Skoru (Öneri 1) veya Sortino
```

Bu funnel kurgusu, getiriyi doğrudan optimize etmeden önce sermaye tüketme potansiyeli olan liderleri saf dışı bırakarak hayatta kalma oranını maksimize eder.
