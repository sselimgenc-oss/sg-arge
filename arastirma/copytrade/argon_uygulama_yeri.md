# Argon — Kopyalanan işlem nerede açılır: Binance global vs Hyperliquid (2026-10-27)

### 1. Binance Global ve Türkiye Durumu
*   **Vadeli İşlem Yetkisi:** Türkiye’de ikamet eden kullanıcılar, KYC (kimlik doğrulama) adımlarını tamamlayarak Binance Global üzerinde USDⓈ-M ve COIN-M vadeli işlem (futures) pozisyonu açabilmektedir ([Binance Futures](https://www.binance.com/en/futures)).
*   **Mevzuat ve Kısıtlar (2025–2026):** 2 Temmuz 2024 tarihli 7518 sayılı kanun kapsamında doğrudan pazarlama kuralları nedeniyle Binance.com Türkçe dil seçeneğini kaldırmıştır; ancak Türkiye Cumhuriyeti vatandaşlarının platformu İngilizce arayüzle kullanması veya türev işlem yapması engellenmemiştir.
*   **Kaldıraç ve KYC:** Yeni açılan hesaplarda ilk 60 gün boyunca risk yönetimi gereği en fazla **20x kaldıraç** sınırı uygulanır; 60 günün ardından sembole göre 50x–125x seviyelerine izin verilir. Seviye 1 kimlik doğrulaması (TC Kimlik / Pasaport ve yüz taraması) olmadan işlem yapılamaz.
*   **Binance TR ile Farkı:** Binance TR (BN Teknoloji A.Ş.), SPK lisanslama sürecine tabi yerli bir kuruluştur. Binance TR’de mevzuat gereği **vadeli işlem bulunmaz**, yalnızca Türk Lirası ile spot alım-satım yapılır. Binance TR yalnızca bankadan TL yatırma/çekme köprüsü vazifesi görür.

---

### 2. Binance’teki Geleneksel Piyasa (TradFi) Perp Kontratları
*   **Mevcut TradFi Perp Piyasaları:** Binance, geleneksel varlıkları takip eden "TradFi USDS-Margined Perpetual" kontratlarını listelemiştir ([Binance TradFi Perpetual Contracts Launch](https://www.binance.com/en/support/announcement/detail/ecf7318c0d434c339e80878588e700d0)):
    *   *Emtia:* Altın (`XAUUSDT`), Gümüş (`XAGUSDT`), WTI Ham Petrol (`CLUSDT`), Brent Petrol (`BZUSDT`) ve Doğal Gaz (`NATGASUSDT`) ([Binance TradFi Assets Guide](https://www.binance.com/en/academy/articles/tradfi-assets-you-can-trade-on-binance-futures)).
    *   *Tek Hisse ve Endeksler:* Başta teknoloji şirketleri olmak üzere ABD hisse senetleri (NVDA, TSLA, AAPL vb.) için tokenize vadeli kontratlar ([Binance Stock Perpetuals](https://www.binance.com/en/academy/articles/how-to-trade-stock-perpetual-contracts-on-binance)).
*   **İşlem Saatleri ve Hafta Sonu:** Binance TradFi kontratları 7/24 kesintisiz işlem görür. Dayanak borsalar (CME, NYSE) kapalıyken gösterge fiyatı son kapanış fiyatına sabitlenir, fonlama oranlarında prim endeksi hariç tutulur.
*   **Ücretler ve Likidite:** Standart Taker %0.05, Maker %0.02 komisyon uygulanır (BNB ile %10 indirim). Altın (`XAUUSDT`) ve Petrol (`CLUSDT`) tahtalarında likidite kurumsal düzeydedir; tek hisse tahtalarında likidite orta/yüksek seviyededir.
*   **Hyperliquid HIP-3 Karşılıkları:**
    *   Altın: Binance `XAUUSDT` ↔ Hyperliquid `xyz:GOLD`
    *   WTI Ham Petrol: Binance `CLUSDT` ↔ Hyperliquid `xyz:CL`
    *   Gümüş: Binance `XAGUSDT` ↔ Hyperliquid `xyz:SILVER`
    *   Hisse Senetleri: Binance `NVDAUSDT`, `TSLAUSDT` ↔ Hyperliquid `xyz:NVDA`, `xyz:TSLA`
    *   S&P 500 Endeksi: Binance TradFi Index Perps ↔ Hyperliquid `xyz:SP500`

---

### 3. Hyperliquid’i Doğrudan Kullanmak
*   **Erişim ve Coğrafi Engel (Geo-block):** Hyperliquid web arayüzünde Türkiye IP adreslerine yönelik herhangi bir engelleme (**geo-block**) bulunmamaktadır ([Hyperliquid Terms of Use](https://app.hyperliquid.xyz/terms)). ABD, İngiltere ve yaptırımlı ülkeler erişim kısıtlamasına tabidir; Türkiye yasaklı listesinde yer almaz.
*   **Hesap Açma ve Fonlama:** E-posta, şifre ve KYC **yoktur**. Yalnızca bir Web3 cüzdanı (MetaMask veya Rabby) bağlanır. Arbitrum One ağındaki USDC bakiyesi doğrudan Hyperliquid Bridge sözleşmesine yatırılır.
*   **Ücretler:** Kripto tahtalarında Taker %0.035, Maker -%0.002 (komisyon iadesi) uygulanır ([Hyperliquid Fees Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees)). HIP-3 tahtalarında (`trade.xyz`) protokol ücretine deployer komisyonu eklenerek Taker ücreti yaklaşık %0.045–%0.06 bandına çıkar ([trade.xyz Fees](https://docs.trade.xyz/perpetuals/mechanics/fees)).
*   **HIP-3 Spread ve Derinlik:** Kripto tahtalarında spread 1 tiktir. HIP-3 hisse ve emtia tahtalarında New York seans saatlerinde (16:30–23:00 TSİ) spread %0.05–%0.15, derinlik $50k–$250k bandındadır. Seans dışı saatlerde ve hafta sonlarında spreadler %0.50–%1.50 seviyesine kadar açılabilir, tahta derinliği belirgin şekilde sığlaşır.

---

### 4. Karşılaştırma Tablosu

| Kriter | Binance Global (USDⓈ-M) | Hyperliquid (L1 + HIP-3) |
| :--- | :--- | :--- |
| **Kripto Perp Erişilebilirliği** | Yüksek (KYC ve TC Kimlik zorunlu, İngilizce arayüz) | Çok Yüksek (KYC yok, doğrudan Web3 cüzdanı bağlantısı) |
| **Hisse & Emtia Perp Çeşitliliği** | Yüksek (XAU, XAG, CL, BZ ve büyük ABD hisseleri) | Yüksek (trade.xyz altında NVDA, TSLA, SP500, GOLD vb.) |
| **İşlem Ücretleri (Taker / Maker)** | Taker: %0.05 / Maker: %0.02 | Kripto: %0.035 / -%0.002; HIP-3: ~%0.05 / %0.01 |
| **Kripto Likiditesi** | Devasa (Sektör lideri, minimum kayma) | Çok Yüksek (DEX alanında lider, derin tahta) |
| **Hisse & Emtia Likiditesi** | Yüksek (Geniş kullanıcı tabanı, dar spread) | Seans içi orta ($50k–$200k), seans dışı sığ ve geniş spread |
| **İşlem Saatleri** | 7/24 Kesintisiz (Piyasa kapalıyken endeks sabitlenir) | 7/24 Kesintisiz (Piyasa kapalıyken oracle donar / stale) |
| **Platform / Karşı Taraf Riski** | Merkezi borsa riski (CEX iflası, regülasyon dondurması) | Akıllı sözleşme / L1 köprü riski ve builder oracle riski |

---

### Önerim

1.  **Kripto İşlemleri İçin Her İki Platform da Uygundur:** Takip edilen trader yalnızca BTC, ETH, SOL gibi ana kripto vadeli işlemlerinde pozisyon açıyorsa, Binance Global (merkezi emir kolaylığı) veya doğrudan Hyperliquid (cüzdan anonimliği ve düşük komisyon) elle kopyalama için rahatlıkla kullanılabilir.
2.  **Hisse ve Emtia İşlemlerinde Likidite ve Spread Kontrolü Yapın:** Takip edilen cüzdan `xyz:NVDA` veya `xyz:GOLD` gibi HIP-3 tahtalarında işlem açtığında, Hyperliquid tarafında seans dışı saatlerde spread açılabileceğinden, Binance Global'deki TradFi karşılığı (`CLUSDT`, `XAUUSDT`, `NVDAUSDT`) üzerinden derinlik ve spread kıyaslaması yapılarak daha dar spreadli platform tercih edilmelidir.
3.  **Seans Dışı Hafta Sonu Taşımalarından Kaçının:** Geleneksel dayanak varlıkların borsaları (NYSE, CME) kapalıyken açılan pozisyonlar, Pazartesi borsa açılışında ani fiyat boşluklarına (*gap*) maruz kalabilir; elle kopyalama yaparken hafta sonu taşınan hisse/emtia pozisyonlarının risk çarpanını düşük tutun.

## Lider notları
- Rakamlar (spread, derinlik, kaldıraç sınırları, TradFi listesi) **doğrulanmadı**; gerçek paradan önce kullanıcı kendi
  hesabında kontrol eder. Vergi/hukuk: mali müşavir.
- **Bulunan hata:** `copytrade/kapi.binance_symbol` tüm HIP-3 coinlerini (`xyz:`) "yok" sayıyor. Binance TradFi perp'leri
  varsa karşılık tablosu gerekir (GOLD→XAUUSDT, SILVER→XAGUSDT, CL→CLUSDT, BRENTOIL→BZUSDT, NATGAS→NATGASUSDT, hisseler
  ad+USDT) ve Binance sembol listesinde gerçekten bulunanlar "var" olur. → `docs/GOREV_TRADER_SECIMI.md` iş 9.
- Pratik sonuç: kripto için Binance global yeter; hisse/emtia için önce Binance TradFi karşılığına bakılır, yoksa
  Hyperliquid (cüzdan + USDC) gerekir — o karar gerçek paradan önce kullanıcının.
