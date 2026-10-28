> **Lider notu (2026-10-28):** Ücret sayıları resmi belgeyle uyumlu (taban taker %0,045). **Kayma sayıları tahmin**: tek
> kaynak bir rehber sitesi, ölçülmüş emir defteri verisi yok. Sonuç yönü makul: %0,095 BTC/ETH'de kötümser, küçük coin ve
> HIP-3'te iyimser. Kapı ve gölge şimdilik tek oran kullanır (kural değişikliği kullanıcı kararı). Öneri: önce ölç — arşive
> seçili coinlerin `l2Book` görüntüsü eklenir, gerçek kayma 1.000/10.000 $ için hesaplanır; oda tablosunda her trader'ın
> hacminin küçük coin/HIP-3 payı bilgi olarak gösterilir. Gecikme kayması (T+30/120 fiyatı) zaten modelde.

# Hyperliquid Copy Trading Simülasyon Analizi
**Gecikmeli Kopyalama Stratejisi İçin Ücret, Kayma ve Funding Modeli**

---

## 1. Yönetici Özeti

Hyperliquid üzerinde bir trader'ın işlemlerini **30 dakika** (kısa vadeli) veya **120 dakika** (uzun vadeli) gecikmeyle kopyalamayı hedefleyen küçük hesap simülasyonunda (işlem başına 1.000 $ – 10.000 $), işlem başına varsayılan **%0,095 dolum maliyeti (%0,045 taker komisyonu + %0,050 kayma)** varlık sınıfına göre çok farklı sonuçlar üretir:

* **BTC ve ETH İçin:** **Kötümser (Aşırı Muhafazakâr).** Gerçek kayma 10.000 $ için dahi %0,005'in altındadır. Toplam dolum maliyeti ~%0,050 civarındadır.
* **Orta Hacimli Varlıklar (SOL, HYPE) İçin:** **Makul ve Güvenli.** Toplam dolum maliyeti ortalama %0,055 – %0,075 aralığındadır.
* **Küçük Hacimli Altcoin'ler İçin:** **İyimser.** 10.000 $'lık bir piyasa emrinde kayma tek başına %0,15 – %0,30 seviyelerine çıkarak toplam maliyeti %0,20 – %0,35 bandına taşır.
* **HIP-3 Piyasaları İçin:** **Aşırı İyimser.** Hem geliştirici komisyon payları (%0 – %300) hem de sığ defter derinliği nedeniyle maliyet %0,20 – %0,50+ seviyelerine ulaşır.

Ayrıca Hyperliquid'de funding ödemeleri 8 saatlik değil, **saatliktir (1 saat)**. Simülasyonda 30 ve 120 dakikalık tutma süreleri boyunca en az bir saat devri snapshot'ına yakalanma ihtimali göz önünde bulundurulmalıdır.

---

## 2. Hyperliquid Ücret Yapısı ve HIP-3 Mekanizması

Hyperliquid, kendi Katman-1 blokzinciri üzerinde merkezi limit emir defteri (CLOB) mimarisiyle çalışır.

### Standart Sürekli Vadeli (Perpetual) Ücretleri (Tier 0)
[Hyperliquid Docs: Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) resmi tablosuna göre en alt kademedeki (14 günlük hacmi 5 milyon doların altındaki) standart hesap ücretleri:

* **Taker Komisyonu:** `%0,045` (4,5 bps)
* **Maker Komisyonu:** `%0,015` (1,5 bps)

*İndirim Mekanizmaları:*
* **Referans İndirimi:** İlk 25 milyon dolarlık hacim için %4 komisyon indirimi sağlar (net taker: ~%0,0432).
* **HYPE Staking:** Kullanıcının stake ettiği HYPE miktarına bağlı olarak %40'a varan ek komisyon indirimi sunar.
* **Hacim Kademeleri:** 14 günlük yuvarlanan hacim 5 milyon doları aştıkça taker ücreti kademeli olarak %0,024'e kadar iner.

### HIP-3 (Kullanıcı / Geliştirici Tarafından Dağıtılan) Piyasaları
[Hyperliquid HIP-3 Spesifikasyonu](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) kapsamında harici geliştiriciler kendi kalıcı vadeli paritelerini (örneğin hisse senedi, emtia veya niş token perpleri) deploy edebilirler. Bu piyasalarda ücretler standart paritelerden farklılaşır:

1. **Deployer Ek Ücret Payı:** Piyasayı oluşturan geliştirici, baz protokol ücretine ek olarak **%0 ile %300** arasında bir ek komisyon payı (builder fee) belirleyebilir. Örneğin deployer %100 ek pay belirlediğinde, taker komisyonu standart %0,045 yerine %0,090 olur.
2. **Büyüme Modu (Growth Mode):** Deployer büyüme modunu etkinleştirdiğinde, protokolün baz ücretleri %90 oranında düşürülür (Tier 0 taker %0,0045, maker %0,0015). Bu modda deployer ek payı en fazla %100 olabilir; dolayısıyla net taker ücreti **%0,0045 ile %0,0090** aralığında gerçekleşir.
3. **Net Durum:** HIP-3 piyasalarında taker ücreti sabit değildir; ilgili sözleşmenin konfigürasyonuna göre **%0,0045 ile %0,180+** arasında değişir.

---

## 3. Funding Oranları ve Ödeme Aralığı

[Hyperliquid Docs: Funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding) ve [CoinGlass Live Funding Tracker](https://www.coinglass.com/FundingRate/HYPE) referanslarına göre:

* **Uzlaşma Sıklığı:** Funding ödemeleri **saatliktir (her 1 saatte bir, günde 24 kez)**. Binance, Bybit ve OKX gibi borsalardaki 8 saatlik döngüden farklı olarak saat başlarında (top-of-the-hour, örn. 14:00, 15:00 UTC) snapshot alınır.
* **Eşler Arası (P2P) Takas:** Fonlama tamamen uzun (long) ve kısa (short) pozisyon sahipleri arasında el değiştirir; borsa bu akıştan komisyon kesmez.
* **Premium Endeksi:** Hyperliquid mark fiyatı ile harici spot oracle fiyatı arasındaki farkın zaman ağırlıklı ortalaması (TWAP) üzerinden sürekli hesaplanır.
* **Kopyalama Simülasyonu Etkisi:**
  * Aynı saat dilimi içinde açılıp kapatılan (saat devrini görmeyen) pozisyonlar **sıfır fonlama** öder/alır.
  * 30 dakikalık kopyalama gecikmesinde pozisyon açılışı ile kapanışı saat başını geçiyorsa 1 saatlik fonlama tahakkuk eder.
  * 120 dakikalık gecikmeli pozisyonlarda ise en az 2 saatlik fonlama ödemesi/tahsilatı kesinleşir.

---

## 4. Likidite, Emir Defteri Derinliği ve Tipik Kayma (Slippage)

Hyperliquid'de likiditenin çekirdeğini [HLP Vault](https://www.google.com/search?q=https://hyperliquid.gitbook.io/hyperliquid-docs/trading/hlp) oluşturur. HLP, piyasa yapıcı algoritmalarıyla defterin her iki tarafına da sürekli likidite sağlar.

[Hyperliquid Guide: Slippage Analizi](https://hyperliquidguide.com/guides/trading/slippage-explained) verilerine göre varlık sınıflarına göre emir defteri derinliği ve gerçekleşen kaymalar:

### Varlık Sınıflarına Göre Dinamikler
1. **Majörler (BTC, ETH):**
   * Alış-satış makası (bid-ask spread) çoğunlukla 0,10 $ – 1,00 $ (%0,001'den az) seviyesindedir.
   * İlk 3 kademede yüz binlerce dolarlık bekleyen limit emir bulunur.
   * 1.000 $ ve 10.000 $'lık piyasa emirleri neredeyse sıfır kaymayla (<%0,005) gerçekleşir.
2. **Büyük / Orta Hacimli Kriptolar (SOL, HYPE):**
   * Tipik makas %0,01 – %0,03 civarındadır.
   * 10.000 $'a kadar olan piyasa emirlerinde kayma %0,01 – %0,03 bandında kalır. 50.000 $'da ise defterin üst kademeleri süpürülerek kayma %0,05 – %0,08 seviyesine ulaşır.
3. **Küçük Hacimli Altcoin'ler:**
   * Makas %0,05 – %0,10 aralığına genişler.
   * Tahtada kademe başına likidite düşüktür. 10.000 $'lık ani piyasa emri birden fazla fiyat basamağını tüketir (%0,10 – %0,30 kayma).
4. **HIP-3 Piyasaları:**
   * Likidite yalnızca ilgili piyasayı başlatan taraf ve onun teşvik ettiği botlarca sağlandığı için genellikle en sığ piyasalardır.
   * 10.000 $ büyüklüğündeki piyasa emirleri tahtayı ciddi oranda bozabilir (%0,30 – %1,00+ kayma).

---

## 5. Kapsamlı Maliyet Matrisi

Aşağıdaki tablo, tekil dolum (giriş veya çıkış) başına **Tier 0 Taker Komisyonu (%0,045 baz; HIP-3 için ortalama %0,060)** ve **tahmini anlık emir defteri kaymasını** özetler:

| Piyasa / Varlık Türü | Emir Büyüklüğü | Taker Komisyonu | Tahmini Kayma | Toplam Dolum Maliyeti |
| :--- | :--- | :--- | :--- | :--- |
| **BTC** | 1.000 $ | %0,045 | ~%0,002 | **%0,047** |
| **BTC** | 10.000 $ | %0,045 | ~%0,005 | **%0,050** |
| **BTC** | 50.000 $ | %0,045 | ~%0,020 | **%0,065** |
| **ETH** | 1.000 $ | %0,045 | ~%0,003 | **%0,048** |
| **ETH** | 10.000 $ | %0,045 | ~%0,008 | **%0,053** |
| **ETH** | 50.000 $ | %0,045 | ~%0,025 | **%0,070** |
| **Orta Hacim (SOL / HYPE)** | 1.000 $ | %0,045 | ~%0,008 | **%0,053** |
| **Orta Hacim (SOL / HYPE)** | 10.000 $ | %0,045 | ~%0,025 | **%0,070** |
| **Orta Hacim (SOL / HYPE)** | 50.000 $ | %0,045 | ~%0,060 | **%0,105** |
| **Küçük Hacim (Altcoin)** | 1.000 $ | %0,045 | ~%0,035 | **%0,080** |
| **Küçük Hacim (Altcoin)** | 10.000 $ | %0,045 | ~%0,150 | **%0,195** |
| **Küçük Hacim (Altcoin)** | 50.000 $ | %0,045 | ~%0,750 | **%0,795** |
| **HIP-3 Piyasası** | 1.000 $ | %0,060* | ~%0,080 | **%0,140** |
| **HIP-3 Piyasası** | 10.000 $ | %0,060* | ~%0,400 | **%0,460** |
| **HIP-3 Piyasası** | 50.000 $ | %0,060* | ~%2,000 | **%2,060** |

*\*HIP-3 komisyonu standart senaryolarda ortalama deployer payı eklenerek hesaplanmıştır.*

---

## 6. %0,095 Varsayımının Değerlendirilmesi ve Model Önerileri

Hesap büyüklüğünüzün işlem başı **1.000 $ – 10.000 $** olduğu varsayımı altında:

1. **BTC ve ETH İçin:**
   * **Değerlendirme:** **Kötümser.**
   * **Gerekçe:** Gerçek hayatta 10.000 $'lık BTC emri defterde yalnızca 1-2 fiyat kademesini tüketir (~0,50 $ fiyat hareketi). Toplam dolum maliyeti %0,050 civarındadır. %0,095 almak simülasyonun kârlılığını gereksiz yere cezalandırır.
   * **Önerilen Değer:** **%0,055** (Taker %0,045 + Kayma %0,010).

2. **Orta Hacimli Varlıklar (SOL, HYPE) İçin:**
   * **Değerlendirme:** **Makul ve Gerçekçi.**
   * **Gerekçe:** Normal piyasa koşullarında 1.000 $ – 10.000 $ büyüklük için toplam dolum maliyeti %0,055 – %0,075 civarındadır. Ancak volatilite anlarında tahta incelmesiyle %0,095 mükemmel bir tampon sunar.
   * **Önerilen Değer:** **%0,075 – %0,095**.

3. **Küçük Hacimli Altcoin'ler İçin:**
   * **Değerlendirme:** **İyimser (Özellikle 10.000 $ için).**
   * **Gerekçe:** 1.000 $ için %0,095 makul olsa da, 10.000 $'lık piyasa emri tahtayı süpürdüğünde kayma tek başına %0,15 – %0,25'e ulaşır.
   * **Önerilen Değer:** 1.000 $ için **%0,090**, 10.000 $ için **%0,200 – %0,250**.

4. **HIP-3 Piyasaları İçin:**
   * **Değerlendirme:** **Aşırı İyimser.**
   * **Gerekçe:** Defter derinliği çok dardır ve deployer ücretleri nedeniyle komisyon %0,045'in üzerinde olabilir.
   * **Önerilen Değer:** Minimum **%0,350 – %0,500** veya modelde piyasa emri yerine Limit/TWAP kullanımı zorunluluğu.

---

## 7. Simülasyon Metodolojisi Uyarısı: Anlık Kayma vs. Zaman Gecikmesi Sapması

Modelinizin güvenilirliği için iki kavramı birbirinden ayırmak zorunludur:

* **Emir İcra Kayması (Execution Slippage):** Emrin Hyperliquid eşleştirme motoruna vardığı andaki emir defteri derinliğinin yol açtığı sapmadır (yukarıdaki tablonun konusu).
* **Zaman Gecikmesi Sapması (Latency Alpha Decay / Price Drift):** Kopyalama 30 dakika ya da 120 dakika gecikmeyle yapıldığından, orijinal işlem ile sizin emriniz arasındaki sürede piyasa fiyatı hedef yönünde ilerlemiş olacaktır. 

> **Önemli Metodolojik İlke:**  
> Kopyalanan trader kârlı bir strateji izliyorsa, 30 veya 120 dakika sonra fiyat büyük olasılıkla kopyalayanın aleyhine hareket etmiş olacaktır. Backtest motorunuzda giriş fiyatı olarak **$T_0$ fiyatı değil, mutlaka $T_{30}$ veya $T_{120}$ anındaki gerçek piyasa fiyatı** baz alınmalı; yukarıdaki dolum maliyeti (% komisyon + % kayma) bu gecikmeli fiyata uygulanmalıdır.

---

## 8. Kaynakça ve Resmi Dokümantasyon

* [Hyperliquid Docs — Fee Structure & Tiers](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees)
* [Hyperliquid Docs — HIP-3 Builder-Deployed Perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals)
* [Hyperliquid Docs — Funding Mechanics](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding)
* [Hyperliquid Guide — Slippage Mechanics & Order Book Depth](https://hyperliquidguide.com/guides/trading/slippage-explained)
* [CoinGlass — Hyperliquid Funding Rates & OI Analytics](https://www.coinglass.com/FundingRate/HYPE)
