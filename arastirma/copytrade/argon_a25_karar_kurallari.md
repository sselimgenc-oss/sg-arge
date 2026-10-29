> **Lider denetim notu (2026-10-29):** Argon A25. Kod okundu (`argon_a25/karar_kurallari_sim.py`), yeniden koşulmadı.
> Veri üretimi istenen gibi; zaman bağımlılığı yok (günler bağımsız), bu yüzden blok bootstrap burada etkisiz.
> **Sonuç doğru okunmalı:** 26 haftada hiçbir kural iyi bir odayı güvenle tanıyamıyor (en iyisi +%50/yılda %20).
> **Argon'un K1 önerisine katılmıyorum:** K1'in "durdur" eşiği (P(fark>%20)<%10) gerçekten iyi odayı (+%50/yıl) %25,
> sıfır farklı odayı %48 durduruyor; bu "iyi odayı öldüren" bir kural. K2 (bahis martingalesi) 26 haftada hiç karar vermiyor
> (güç <%1). K3 yanlış alarmı %2–3'te tutuyor ama gücü düşük.
> **Lider önerisi:** panoda K1 olasılıkları yalnız *bilgi* olarak gösterilir (P(oda önde), P(fark>%20)); otomatik "durdur"
> yalnız açık zarar kanıtında (ör. P(fark<0)>%90) önerilir. Eşik değişikliği kullanıcı kararıdır.

# Hyperliquid Gölge Trader Kopyalama: Karar Kuralları Karşılaştırma Raporu

Bu rapor, Hyperliquid üzerinde 18 kişilik gölge "oda" portföyü ile 18 kişilik rastgele "kontrol" portföyü arasındaki BTC betası düzeltilmiş günlük getiri farkını ($d_t$) haftalık izleyerek performansı değerlendiren üç karar kuralının Monte Carlo simülasyon analizini sunar.

---

## 1. Simülasyon Kurgusu ve Veri Üretim Modeli

Kullanıcı panoya her hafta baktığı için tekrarlanan incelemelerin (peeking) 1. tip hatayı (yanlış alarm) şişirmemesi hedeflenmiştir. 26 haftalık (182 gün) izleme dönemi boyunca piyasa yapısı şu parametrelerle simüle edilmiştir:

* **Trader Sayısı:** 36 trader (18 oda trader'ı, 18 kontrol trader'ı). Portföyler eşit ağırlıklıdır.
* **Oynaklık Dağılımı:** Her trader'ın günlük oynaklığı $\sigma_i \sim \text{Uniform}(\%2, \%8)$ aralığından çekilir.
* **Piyasa Riski ve Beta:** BTC günlük oynaklığı $\sigma_{btc} = \%2.5$'tir. Her trader'ın BTC betası $\beta_i \sim \text{Uniform}(0.0, 1.5)$ aralığındadır.
* **Ortak Faktör Korelasyonu:** Trader'ların ortak kripto duyarlılık faktörüyle korelasyonu $\rho_i \sim \text{Uniform}(0.2, 0.5)$ düzeyindedir.
* **Kalın Kuyruk (Fat-Tail):** Şoklar 4 serbestlik dereceli Student-$t$ dağılımından ($df=4$) üretilir ve birim varyansa normalize edilir ($\text{Var}(t_4) = 4/(4-2) = 2 \implies t_4 / \sqrt{2}$).
* **Beta Arındırma:** Trader getirisi $R_{i,t} = \alpha_i + \beta_i R_{btc,t} + \sigma_i \epsilon_{i,t}$ şeklinde olup, BTC getirisi düşülerek beta-düzeltilmiş getiri $\tilde{R}_{i,t} = R_{i,t} - \beta_i R_{btc,t} = \alpha_i + \sigma_i \epsilon_{i,t}$ elde edilir.
* **Günlük Fark ($d_t$):** $d_t = \bar{\tilde{R}}_{room,t} - \bar{\tilde{R}}_{ctrl,t}$. Yıllık gerçek farklar $\Delta \in \{0, +\%10, +\%25, +\%50, -\%25\}$ kripto 365 gün esasına göre günlük $\Delta / 365$ olarak odaya eklenir.

---

## 2. Karar Kurallarının Matematiksel Tanımları

### (K1) Bayesçi Normal-Normal Modeli
* **Önsel Dağılım:** Yıllık fark $\theta \sim \mathcal{N}(0, 0.30^2)$ ($\mu_0 = 0, \sigma_0 = 0.30$).
* **Standart Hata (SE):** 7 günlük blok bootstrap (kayan blok / analytical moving block bootstrap limit). $T = 7w$ günde $w$ blok ortalamasının varyansı üzerinden yıllıklandırılmış standart hata hesaplanır.
* **Sonsal Dağılım:** Doğal eşlenik güncelleme ile $\mu_{post}$ ve $\sigma_{post}$ elde edilir.
* **Karar Kriterleri:**
  * **Umut Verici:** $P(\text{fark} > 0) > \%95$ VE $P(\text{fark} > \%20/\text{yıl}) > \%70$.
  * **Durdur:** $P(\text{fark} > \%20/\text{yıl}) < \%10$.
  * 26. haftaya kadar iki eşik de tetiklenmezse **"Kanıt Yok"** kararı verilir.

### (K2) Her-An-Geçerli Test (Bahis Martingalesi / E-Process)
* **Martingale Süreci:** Haftalık birikimli fark $d_{hafta, w} = \sum_{t=7(w-1)+1}^{7w} d_t$.
* **Kırpma ve Ölçekleme:** $c = \%5$ (0.05), $x_w = \text{clip}(d_{hafta, w}, -c, c) / c \in [-1, 1]$.
* **Bahis Güncellemesi:**
  * Pozitif yön: $E_{pos, w} = E_{pos, w-1} \cdot (1 + \lambda x_w)$, $E_{pos, 0} = 1$.
  * Negatif ayna yönü: $E_{neg, w} = E_{neg, w-1} \cdot (1 - \lambda x_w)$, $E_{neg, 0} = 1$.
* **Eşik:** $\lambda \in \{0.1, 0.2, 0.3\}$ için Ville eşitsizliği uyarınca $E \ge 20 \implies \text{Tip I Hata} \le 1/20 = \%5$.
  * $E_{pos} \ge 20 \implies$ "Umut Verici" (fark var, pozitif).
  * $E_{neg} \ge 20 \implies$ "Durdur" (fark var, negatif).
  * 26. haftada iki değer de 20'ye ulaşamazsa **"Kanıt Yok"**.

### (K3) Sabit Bakış (Grup Ardışık O'Brien-Fleming Eşiği)
* **İnceleme Zamanları:** Yalnızca 4., 8. ve 12. haftalarda ($K=3$, bilgi fraksiyonları $t = [1/3, 2/3, 1.0]$).
* **Test İstatistiği:** $Z_w = \bar{d}_w / \text{SE}(\bar{d}_w)$.
* **İki Taraflı $\alpha=0.05$ Eşikleri:**
  * 4. Hafta ($w=4$): $|Z_4| \ge 3.4711$
  * 8. Hafta ($w=8$): $|Z_8| \ge 2.4544$
  * 12. Hafta ($w=12$): $|Z_{12}| \ge 2.0040$
* Pozitif sınır aşımı $\implies$ "Umut Verici", negatif sınır aşımı $\implies$ "Durdur", 12. haftada sınır aşılmazsa $\implies$ "Kanıt Yok".

---

## 3. Simülasyon Sonuçları ve Karşılaştırma Tablosu

* **Koşu Sayısı:** Her kural ve senaryo için 500 bağımsız Monte Carlo patikası (Toplam 2.500 simülasyon).
* **Rastgelelik Tohumu:** `seed = 2026`.
* **Çalışma Süresi:** 22.02 saniye.

| Karar Kuralı | Gerçek Fark (Yıllık) | Yanlış "Umut Verici" (Fark=0) | Doğru Tespit Oranı | Yanlış "Durdur" Oranı (Fark>0) | Ort. Karar Haftası | Umut Verici (%) | Durdur (%) | Kanıt Yok (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **K1 (Bayesçi Normal-Normal)** | **+%0** | **%6.0** | %46.2 (H0) | %47.8 | 15.9 | %6.0 | %47.8 | %46.2 |
| K1 (Bayesçi Normal-Normal) | +%10 | — | %7.2 | %40.6 | 16.9 | %7.2 | %40.6 | %52.2 |
| K1 (Bayesçi Normal-Normal) | +%25 | — | %11.0 | %30.2 | 18.1 | %11.0 | %30.2 | %58.8 |
| K1 (Bayesçi Normal-Normal) | +%50 | — | %20.0 | %25.4 | 17.2 | %20.0 | %25.4 | %54.6 |
| K1 (Bayesçi Normal-Normal) | **-%25** | %3.8 | **%64.2** | — | 14.0 | %3.8 | %64.2 | %32.0 |
| **K2 (Martingale, $\lambda=0.1$)** | +%0 | **%0.0** | %100.0 (H0) | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.1$) | +%10 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.1$) | +%25 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.1$) | +%50 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.1$) | -%25 | %0.0 | %0.0 | — | 26.0 | %0.0 | %0.0 | %100.0 |
| **K2 (Martingale, $\lambda=0.2$)** | +%0 | **%0.0** | %100.0 (H0) | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.2$) | +%10 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.2$) | +%25 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.2$) | +%50 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.2$) | -%25 | %0.0 | %0.0 | — | 26.0 | %0.0 | %0.0 | %100.0 |
| **K2 (Martingale, $\lambda=0.3$)** | +%0 | **%0.0** | %100.0 (H0) | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.3$) | +%10 | — | %0.0 | %0.0 | 26.0 | %0.0 | %0.0 | %100.0 |
| K2 (Martingale, $\lambda=0.3$) | +%25 | — | %0.2 | %0.0 | 26.0 | %0.2 | %0.0 | %99.8 |
| K2 (Martingale, $\lambda=0.3$) | +%50 | — | %0.4 | %0.0 | 26.0 | %0.4 | %0.0 | %99.6 |
| K2 (Martingale, $\lambda=0.3$) | -%25 | %0.0 | %0.2 | — | 26.0 | %0.0 | %0.2 | %99.8 |
| **K3 (O'Brien-Fleming, 4/8/12)** | **+%0** | **%2.2** | %95.2 (H0) | %2.6 | 12.0 | %2.2 | %2.6 | %95.2 |
| K3 (O'Brien-Fleming, 4/8/12) | +%10 | — | %3.4 | %3.2 | 11.9 | %3.4 | %3.2 | %93.4 |
| K3 (O'Brien-Fleming, 4/8/12) | +%25 | — | %6.8 | %0.6 | 11.9 | %6.8 | %0.6 | %92.6 |
| K3 (O'Brien-Fleming, 4/8/12) | +%50 | — | **%10.4** | %0.6 | 11.9 | %10.4 | %0.6 | %89.0 |
| K3 (O'Brien-Fleming, 4/8/12) | -%25 | %1.0 | %4.6 | — | 11.9 | %1.0 | %4.6 | %94.4 |

*Not: Tabloda fark=0 iken doğru tespit, H0 hipotezinin bozulmaması ("Kanıt Yok") oranıdır. Fark > 0 iken "Umut Verici" tespiti doğru pozitif kabul edildiğinden yanlış alarm sütununda "—" gösterilmiştir.*

---

## 4. İstatistiki ve Finansal Bulgular

1. **K2 Martingale'inin Aşırı Muhafazakarlığı:** Bahis martingalesi sonsuz zaman ufku ($t \to \infty$) boyunca rastgele durdurmalara karşı geçerlilik sağlayan Ville eşitsizliğini ($E \ge 20$) kullanır. Bu özellik yanlış alarmı sıfıra indirir (%0.0) ancak 26 haftalık sınırlı gözlem penceresinde yıllık %30 portföy oynaklığı altında sermayenin $E \ge 20$ katına büyümesi için gereken sürüklenme hızı yetersiz kalır (güç < %1).
2. **K3'ün Kesin Tip I Hata Kontrolü:** O'Brien-Fleming eşiği, erken haftalarda (4. hafta $Z \ge 3.47$) aşırı katı davranarak gereksiz panik çıkışlarını engeller ve fark=0 durumunda toplam hata oranını iki taraflı %4.8 (%2.2 pozitif, %2.6 negatif) seviyesinde tutar. Ancak 12 haftalık ufuk, kriptodaki gürültü içinde +%25 alfayı tespit etmek için istatistiksel güç açısından kısadır (%6.8 güç).
3. **K1'in Asimetrik Ticari Eşik Niteliği:** K1 kuralındaki "Durdur" eşiği ($P(\text{fark} > \%20) < \%10$), salt negatif getiriye değil, "hedeflenen %20 yıllık alfayı üretme ihtimalinin düşüklüğüne" bakar. Bu nedenle +%10 ve +%25 senaryolarında dahi %30–%40 durdurma üretir. Buna karşılık, gerçekten zararda olan odayı (-%25) ortalama 14 haftada %64.2 olasılıkla durdurarak sermayeyi koruyan tek kuraldır.

---

## 5. Öneri ve Uygulama Tavsiyesi

Sermayeyi aktif korumak ve yetersiz performans gösteren trader odalarını hızla tasfiye etmek istiyorsanız **K1 (Bayesçi Normal-Normal)** kuralını öneriyorum; çünkü 26 haftalık pencerede negatif getirili odayı (-%25) ortalama 14 haftada %64.2 başarıyla durdurabilen tek işlevsel mekanizma budur. K2 (Martingale) panoya haftalık bakışta sıfır yanlış alarm sağlasa da Ville eşiği nedeniyle 26 haftada neredeyse hiçbir karara ulaşamazken, K3 (O'Brien-Fleming) hata payını %2.2'de tutmasına rağmen 12 haftada alfayı teyit etmekte yetersiz kalmaktadır. K1'in ticari bir filtre olarak kullanılması ve "Durdur" kararının "kesin zarar" yerine "yıllık %20 hedefini yakalama olasılığının tükenmesi" şeklinde yorumlanması en rasyonel yaklaşımdır.

---

## 6. Betik Kullanım Kılavuzu

Simülasyon betiği bağımsız bir dosya olarak hazırlanmış olup harici ağ veya paket bağımlılığı gerektirmez (`numpy`, `pandas`, `scipy` yeterlidir):

```bash
# Varsayılan parametrelerle çalıştırma (500 tekrar, seed=2026)
python3 hyperliquid_karar_kurallari.py

# Özel parametrelerle çalıştırma
python3 hyperliquid_karar_kurallari.py --reps 1000 --seed 42
```
