> **Lider notu (2026-10-28):** Formüller doğru; bir düzeltme: kripto 7/24, hafta = 7 gün → 12 hafta = 84 gün (rapor 60 aldı).
> MDE'ler √(60/84) ≈ 0,85 ile küçülür; yıllıklaştırma 365 ile. Ana sonuç değişmiyor: 12 haftada yalnız büyük farklar
> görülebilir. Ön kayıt zaten "belirsizse bir kez 12 hafta uzatılır" diyor; Faz 3 güç hesabını gerçek varyansla yapacak.
> Gücü artıran meşru yollar (ön kayıtta ikincil olarak var): aday katı ikincil kohort (daha çok trader), BTC betası
> düzeltilmiş fark (Model B'ye yaklaşır), geçmiş provanın çok penceresi.

# Trader Grubu İstatistiksel Güç Analizi (12 ve 24 Hafta Karşılaştırması)

## 1. Bağlam ve Deney Tasarımı

* **Deney ve Kontrol Grupları:** Seçilmiş trader grubu (oda) $N = 15$ trader, rastgele seçilmiş kontrol grubu $N = 15$ trader.
* **Sanal Portföy Modeli:** Her iki grup da eşit ağırlıklı, sabit sermayeli sanal portföyler olarak modellenir:
  $$R_{T, t} = \frac{1}{15} \sum_{i=1}^{15} R_{T, i, t}, \quad R_{C, t} = \frac{1}{15} \sum_{j=1}^{15} R_{C, j, t}$$
* **Temel Ölçüm Metriği:** İki portföyün günlük net getiri farkı:
  $$D_t = R_{T, t} - R_{C, t}$$
* **Belirsizlik ve Başarı Kriteri:**
  * Haftalık blok bootstrap ile %95 güven aralığı ($CI_{95\%}$).
  * Başarı tanımı: Güven aralığının alt sınırının sıfırdan büyük olması ($CI_{\text{alt}} > 0$).
  * İki yönlü %95 güven aralığı alt sınırı $\bar{D} - 1{,}960 \cdot \text{SE} > 0$ koşulu, tek yönlü $\alpha = 0{,}025$ anlamlılık düzeyine (veya iki yönlü $\alpha = 0{,}05$) karşılık gelir.
  * Hedeflenen istatistiksel güç: $1 - \beta = 0{,}80$ ($z_{1-\beta} = 0{,}8416$).
* **Zaman Pencereleri ve İşlem Günleri:**
  * Standart piyasa haftası: $K = 5$ işlem günü.
  * 12 hafta: $T_{12} = 12 \times 5 = 60$ işlem günü.
  * 24 hafta: $T_{24} = 24 \times 5 = 120$ işlem günü.
  * Yıllıklaştırma bazı: Finansal standart olan 252 işlem günü ($\text{Getiri}_{\text{yıllık}} = \text{Getiri}_{\text{günlük}} \times 252$). *(Kripto gibi 7/24 piyasalar için 12 hafta = 84 gün, çarpan 365'tir).*

---

## 2. Adım Adım Matematiksel Çıkarım ve Formüller

### Adım 1: Tek Portföy Varyansı
Her bir trader'ın günlük getiri varyansı $\text{Var}(R_i) = \sigma^2$ ve herhangi iki trader arasındaki ortalama korelasyon $\text{Corr}(R_i, R_j) = \rho$ iken, $N$ varlıktan oluşan eşit ağırlıklı bir portföyün varyansı:
$$\text{Var}(R_p) = \frac{1}{N^2} \left[ \sum_{i=1}^N \text{Var}(R_i) + \sum_{i=1}^N \sum_{j \neq i} \text{Cov}(R_i, R_j) \right]$$
$$\text{Var}(R_p) = \frac{1}{N^2} \left[ N\sigma^2 + N(N - 1)\rho\sigma^2 \right] = \frac{\sigma^2}{N} \left[ 1 + (N - 1)\rho \right]$$
$N = 15$ için:
$$\text{Var}(R_T) = \text{Var}(R_C) = \frac{\sigma^2}{15} \left( 1 + 14\rho \right)$$

### Adım 2: Günlük Getiri Farkının Standart Sapması ($\sigma_D$)
İki portföyün farkı $D_t = R_{T, t} - R_{C, t}$ için varyans:
$$\text{Var}(D_t) = \text{Var}(R_{T, t}) + \text{Var}(R_{C, t}) - 2\text{Cov}(R_{T, t}, R_{C, t})$$

Bu hesaplamada finansal ve istatistiksel iki model mevcuttur:

1. **Model A (Bağımsız Gruplar / Klasik Deney Modeli):**
   Korelasyon $\rho$, yalnızca grup içi trader'lar arasındadır; test grubu ile kontrol grubu arasında ortak bir bağ yoktur ($\text{Cov}(R_T, R_C) = 0$).
   $$\text{Var}(D) = 2 \cdot \text{Var}(R_p) = \frac{2\sigma^2}{15} (1 + 14\rho) \implies \sigma_D = \sigma \sqrt{\frac{2(1 + 14\rho)}{15}}$$
   *Bu modelde $\rho$ arttıkça grup içi çeşitlendirme azalır, portföy oynaklıkları büyür ve farkın standart sapması $\sigma_D$ yükselir.*

2. **Model B (Ortak Piyasa Faktörü / Eşlenik Karşılaştırma Modeli):**
   Tüm trader'lar aynı piyasa riskine maruzdur ve gruplar arası ikili korelasyon da $\rho$'dur ($\text{Cov}(T_i, C_j) = \rho\sigma^2$).
   $$\text{Var}(D) = \frac{2\sigma^2}{15}(1 + 14\rho) - 2\rho\sigma^2 = \frac{2\sigma^2(1 - \rho)}{15} \implies \sigma_D = \sigma \sqrt{\frac{2(1 - \rho)}{15}}$$
   *Bu modelde ortak piyasa şokları long-short farkta nötrlendiği için $\rho$ arttıkça $\sigma_D$ küçülür.*

### Adım 3: Blok Bootstrap Standart Hatası (SE)
Haftalık $B$ blok üzerinden ortalama günlük farkın standart hatası (hafta içi seri korelasyon sıfır kabul edildiğinde):
$$\text{SE}(\bar{D}) = \frac{\sigma_D}{\sqrt{T}} = \frac{\sigma_D}{\sqrt{B \times 5}}$$

### Adım 4: Saptanabilecek En Küçük Ortalama Fark (MDE)
* %95 iki yönlü güven aralığı kritik değeri: $z_{1 - \alpha/2} = z_{0{,}975} \approx 1{,}9600$.
* %80 istatistiksel güç kritik değeri: $z_{1 - \beta} = z_{0{,}80} \approx 0{,}8416$.
* Minimum Detectable Effect (MDE):
  $$\text{MDE}_{\text{günlük}} = (z_{1 - \alpha/2} + z_{1 - \beta}) \cdot \text{SE}(\bar{D}) = (1{,}9600 + 0{,}8416) \cdot \frac{\sigma_D}{\sqrt{T}} \approx 2{,}8016 \cdot \frac{\sigma_D}{\sqrt{T}}$$
* Yıllıklandırılmış değer:
  $$\text{MDE}_{\text{yıllık}} = \text{MDE}_{\text{günlük}} \times 252$$

---

## 3. İstatistiksel Güç Analizi Sonuç Tablosu

Aşağıdaki tablo, standart deney yaklaşımı olan **Model A (Bağımsız Gruplar)** baz alınarak hazırlanmıştır. Parantez içi değerler yıllıklandırılmış karşılıkları ifade eder.

| sd ($\sigma$) | korelasyon ($\rho$) | Farkın SD ($\sigma_D$) | 12 hafta en küçük fark (Günlük / Yıllık) | 24 hafta en küçük fark (Günlük / Yıllık) |
| :---: | :---: | :---: | :---: | :---: |
| **%1** | 0,1 | %0,566 | **%0,205** (%51,6) | **%0,145** (%36,5) |
| **%1** | 0,3 | %0,833 | **%0,301** (%75,9) | **%0,213** (%53,7) |
| **%1** | 0,5 | %1,033 | **%0,374** (%94,1) | **%0,264** (%66,6) |
| **%3** | 0,1 | %1,697 | **%0,614** (%154,7) | **%0,434** (%109,4) |
| **%3** | 0,3 | %2,498 | **%0,903** (%227,7) | **%0,639** (%161,0) |
| **%3** | 0,5 | %3,098 | **%1,121** (%282,4) | **%0,792** (%199,7) |
| **%5** | 0,1 | %2,828 | **%1,023** (%257,8) | **%0,723** (%182,3) |
| **%5** | 0,3 | %4,163 | **%1,506** (%379,5) | **%1,065** (%268,3) |
| **%5** | 0,5 | %5,164 | **%1,868** (%470,7) | **%1,321** (%332,8) |

*(Referans: Ortak piyasa faktörünün gruplar arası farkta elendiği **Model B** altında $\sigma_D$ sırasıyla %0,258–%1,732'ye iner; 12 haftalık yıllık MDE %23,5–%157,9, 24 haftalık yıllık MDE %16,6–%111,6 olur).*

---

## 4. Hafta İçi Otokorelasyonun Etkisi

Haftalık blok bootstrap kullanılmasının temel nedeni, finansal zaman serilerindeki ardışık bağımlılıkları (otokorelasyon ve volatilite kümelenmesi) korumaktır. Hafta içi gecikmeli korelasyonlar $\rho_k = \text{Corr}(D_t, D_{t+k})$ sıfırdan farklı olduğunda:

1. **Pozitif Otokorelasyon (Momentum / Trend):**
   Günlük getiri farklarında trend veya momentum varsa ($\rho_k > 0$), 5 günlük bloğun toplam varyansı bağımsız günlerin toplamından daha büyük olur ($\text{VIF} = 1 + 2\sum_{k=1}^4 \frac{5-k}{5}\rho_k > 1$). Standart hata büyür, güven aralığı genişler ve saptanabilecek en küçük fark **daha da büyür** (testin gücü düşer).
2. **Negatif Otokorelasyon (Ortalamaya Dönüş / Bid-Ask Bounce):**
   Stratejiler mean-reversion içeriyorsa ($\rho_k < 0$), günler birbirini dengeler, blok varyansı küçülür, standart hata daralır ve saptanabilecek fark **daha küçük seviyelere iner** (testin gücü artar).
3. **IID Varsayımının Riski:**
   Veride pozitif otokorelasyon varken standart IID varsayımı yapılırsa, standart hata yapay olarak dar hesaplanır ve Tip I hata oranı (%5 sahte pozitiflik) katlanarak gerçeği yansıtmayan sahte başarılar üretir. Haftalık blok bootstrap bu riski engeller.

---

## 5. Değerlendirme ve Sonuç: "12 Haftada Makul Bir Farkı Görebilir Miyiz?"

12 haftalık (60 işlem günü) bir test süresi, finansal piyasalarda makul ve sürdürülebilir bir trader üstünlüğünü (alfayı) istatistiksel olarak ayırt edebilmek için kesinlikle yetersizdir. En iyimser düşük oynaklık senaryosunda dahi (%1 SD) saptanabilecek en küçük fark yıllık %51,6 iken; tipik bireysel trader oynaklığında (%3–%5 SD) bu eşik yıllık %150 ile %470 gibi piyasa gerçeklerinden kopuk seviyelere ulaşmaktadır. Kurumsal standartlarda yıllık %10–%25 aralığındaki net alfa dahi üstün bir performans kabul edildiğinden, 12 haftada güven aralığının alt sınırının sıfırın üzerinde kalması sistematik bir beceriden ziyade %80 ihtimalle kısa vadeli piyasa şansından veya aşırı kaldıraç riskinden kaynaklanacaktır. Güvenilir ve makul büyüklükteki bir farkı saptayabilmek için test süresi en az 1–2 yıla uzatılmalı veya örneklemdeki bağımsız trader sayısı belirgin biçimde artırılmalıdır.
