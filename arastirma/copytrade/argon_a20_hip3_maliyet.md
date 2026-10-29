> **Lider denetim notu (2026-10-29):** Argon A20. Kaynakları lider açamadı (oturum ağı `hyperliquid.gitbook.io`'ya kapalı);
> sayılar doğrulanmadı. Argon canlı `l2Book` ölçümü **yapmadı** (kendi notu); makas/kayma tablosu üçüncü taraf raporlarından
> derleme, §4 sayıları "tahmin". Ücret yapısı (taban taker %0,045; HIP-3 deployerFeeScale; büyüme modunda %90 indirim) resmî belgeye
> dayandırılmış; kod içinde kullanılmadan önce API `meta`/`perpDexs` yanıtıyla doğrulanmalı.
> **Sonuç:** B17'nin "HIP-3'te tek oran iyimser" varsayımı her HIP-3 piyasası için doğru değil: büyüme modundaki hisse perp'lerinde
> (ABD seansı) gerçek maliyet tek oranımızdan (%0,095) düşük; standart mod, gece/hafta sonu ve küçük coinlerde yüksek. Yön coin
> ve saate bağlı → K‑5 (a) "önce ölç" geçerli. Ana karar maliyeti (`maliyet_taker`, `maliyet_kayma`) değişmez (yöntem); sınıf
> ayrımı yalnız `maliyet_rapor.py` duyarlılık raporuna (HIP-3'ü büyüme/standart ve seans içi/dışı diye ayırarak) girer.

# Hyperliquid HIP-3 Piyasaları ve Maliyet Modellemesi Raporu (A20)

**Erişim Tarihi:** 29 Ekim 2026  
**Bağlam:** Hyperliquid sürekli vadeli (perp) borsasında trader'ları gölge olarak (gerçek parasız / paper trading) kopyalama araştırması için güncel ücret ve kayma (slippage) maliyet modeli.

---

## 1. HIP-3 Piyasalarının Güncel Ücret Yapısı

HIP-3 (*Builder-Deployed Perpetuals*), bağımsız geliştiricilerin (deployer) 500.000 $HYPE$ stake ederek kendi vadeli işlem tahtalarını açmasına olanak tanır. Ücret mekanizması doğrudan protokol düzeyinde formüle edilmiştir:

* **Standart Protokol Baz Ücreti (Tier 0):** Taker **%0,045** (4,5 bps), Maker **%0,015** (1,5 bps).
* **Piyasa Kurucusu (Deployer) Ek Ücret Çarpanı:** Deployer, ek ücret payını `%0` ile `%300` arasında belirleyebilir (`deployerFeeScale`: `0` ila `3.0`).
  * `deployerFeeScale < 1` ise: $\text{Çarpan} = \text{deployerFeeScale} + 1$
  * `deployerFeeScale >= 1` ise: $\text{Çarpan} = \text{deployerFeeScale} \times 2$ (Deployer payı %100'ün üzerindeyse protokol komisyonu da deployer komisyonuna eşit olacak şekilde artırılır).
  * **Uygulamadaki Standart (Örn. trade[XYZ]):** Varsayılan olarak `deployerFeeScale = 1.0` uygulanır. Bu durumda standart ücret çarpanı **2x** olur; Taker **%0,090** (9 bps), Maker **%0,030** (3 bps) olur ve toplanan komisyon %50 protokol, %50 deployer arasında paylaşılır.
* **Büyüme Modu (Growth Mode):** Kripto dışı varlıklar (hisse senetleri, emtialar, endeksler) için deployer büyüme modunu açabilir:
  * Protokol komisyonları ve iadeler **%90 oranında indirilir** (`growthModeScale = 0.1`).
  * Büyüme modunda deployer ücret payı en fazla %100 olabilir (`deployerFeeScale: 0 - 1.0`).
  * **Büyüme Modu Baz Taker Oranı (Tier 0):** **%0,0045 – %0,0090** (0,45 – 0,90 bps); Maker oranı ise **%0,0015 – %0,0030** aralığına iner (TradeXYZ hisse perp'lerinde varsayılan Taker %0,0090'dır).
  * *İstisna:* Kripto sepetleri, kripto hisseleri (MSTR vb.) ve PAXG ile örtüşen altın gibi varlıklar büyüme moduna uygun değildir; bu varlıklarda standart 2x oran geçerlidir.

### Özet Ücret Tablosu (Tier 0)

| Piyasa / Mod | Deployer Çarpanı | Taker Ücreti (Tier 0) | Maker Ücreti (Tier 0) | Dağılım (Protokol / Deployer) |
| :--- | :--- | :--- | :--- | :--- |
| **Doğrulayıcı Kripto (BTC/ETH)** | 1x (Çarpan yok) | %0,0450 | %0,0150 | %100 Protokol / %0 Deployer |
| **HIP-3 Büyüme Modu (TradFi/Hisse)** | 0,1x Taban × (1 ila 2) | %0,0045 – %0,0090 | %0,0015 – %0,0030 | %50 Protokol / %50 Deployer |
| **HIP-3 Standart Mod (Kripto/Genel)** | 2x (Ölçek 1.0) | %0,0900 | %0,0300 | %50 Protokol / %50 Deployer |
| **HIP-3 Tavan (Maks. İzin Verilen)** | 6x (Ölçek 3.0) | %0,2700 | %0,0900 | Eşit paylaşımlı tavan |

* **Kaynaklar:**
  * [Hyperliquid Docs - Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) (Erişim tarihi: 29 Ekim 2026)
  * [Hyperliquid Docs - HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) (Erişim tarihi: 29 Ekim 2026)
  * [trade[XYZ] Docs - Fees](https://docs.trade.xyz/perpetuals/mechanics/fees) (Erişim tarihi: 29 Ekim 2026)

---

## 2. Kayma (Slippage) ve Alış-Satış Makası Ölçütleri

Doğrudan Hyperliquid halka açık API'si (`l2Book`) verilerini inceleyen piyasa mikro yapısı araştırmaları ([Castle Labs Perp DEX Raporu](https://castlelabs.io/research/reports/mapping-the-perpetual-trading-ecosystem) ve [Hyperliquid Guide Slippage Raporu](https://hyperliquidguide.com/guides/trading/slippage-explained)) temel alınmıştır.

* **Ölçüm Künyesi:**
  * **Veri Kaynağı:** Halka açık Hyperliquid L2 API (`https://api.hyperliquid.xyz/info`, `{"type": "l2Book"}`) ve eşzamanlı emir defteri derinlik snapshot'ları.
  * **Örneklem & Dönem:** Castle Labs tarafından 17 Ağustos – 15 Eylül 2026 tarihleri arasında, 45–60 saniyelik aralıklarla 10–20 dakikalık oturumlarda toplanan derinlik verileri; 23 Eylül 2026 kesiti.
  * **İncelenen Varlıklar:** BTC, ETH, SOL, HYPE, ZEC ve TradeXYZ üzerindeki 7 TradFi varlığı (NVDA, BRENTOIL vb.).

### Tipik Makas ve 1.000 $ – 10.000 $ Emirde Fiyat Etkisi

| Varlık Grubu | Tipik Alış-Satış Makası (Spread) | 1.000 $ Emirde Kayma | 10.000 $ Emirde Kayma | Piyasa Notu / Likidite Durumu |
| :--- | :--- | :--- | :--- | :--- |
| **BTC & ETH** | < %0,001 (0,1 – 0,3 bps) | <%0,001 (0,1 bps) | <%0,005 (0,2 – 0,5 bps) | Defter son derece derin; $100k emirde dahi kayma ~0,21 bps (%0,0021). |
| **Büyük Altcoinler (SOL, AVAX vb.)** | %0,005 – %0,015 (0,5 – 1,5 bps) | ~%0,005 (0,5 bps) | %0,010 – %0,025 (1 – 2,5 bps) | HLP piyasa yapıcılığı aktiftir, $10k emri rahat karşılar. |
| **Küçük / Düşük Hacimli Coinler** | %0,050 – %0,250 (5 – 25 bps) | %0,030 – %0,100 (3 – 10 bps) | %0,100 – %0,450+ (10 – 45+ bps) | Defter kademeleri boştur; $10k piyasa emri kademe süpürür. |
| **HIP-3 (Hisse/Emtia - ABD Seansı / RTH)** | %0,0035 – %0,0100 (0,35 – 1 bps) | <%0,002 (0,2 bps) | %0,005 – %0,015 (0,5 – 1,5 bps) | Castle Labs medyan TradeXYZ spread'i 0,35 bps; $100k kayması 0,84 bps. |
| **HIP-3 (Hisse/Emtia - Gece / Hafta Sonu)** | %0,050 – %0,200 (5 – 20 bps) | %0,020 – %0,080 (2 – 8 bps) | %0,100 – %0,350 (10 – 35 bps) | Dayanak piyasa kapalıyken 30 dk EWMA fiyatlaması çalışır, likidite daralır. |
| **HIP-3 (Pre-IPO / Niş: Anthropic vb.)** | %0,500 – %2,000+ (50 – 200 bps) | %0,150 – %0,500 (15 – 50 bps) | %0,500 – %1,500+ (50 – 150+ bps) | Aşırı sığ tahta; 10 bps aralığında toplam derinlik ~$160.000 ile sınırlıdır. |

* *Not:* Doğrudan sandbox ortamından canlı web soket/API testi dış ağ kısıtlaması nedeniyle yapılamamış, bu nedenle yukarıdaki ölçümler doğrulanmış üçüncü taraf API analizlerinden derlenmiştir.

---

## 3. Asgari Emir Değeri (Minimum Order Notional)

Hyperliquid resmî sistem hata tanımları (`error-responses`) uyarınca:

* **Sürekli Vadeli İşlemler (Perps):** Asgari işlem değeri net olarak **10 $ (10 USDC)**'dir.
  * İlgili API Hata Kodu: `MinTradeNtl: Order must have minimum value of $10.`
* **Spot Piyasalar:** Asgari işlem değeri **10 {quote_token}**'dır (`MinTradeSpotNtl`).
* **TWAP Emirleri:** Algoritmik TWAP emirlerinde toplam asgari sepet büyüklüğü **100 $** olup, alt parçalar yaklaşık 10 $'a kadar bölünebilir.
* **HIP-3 Piyasalarında Durum:** **Farklı değildir.** HIP-3 tahtaları bağımsız deployer'lar tarafından tanımlansa da mutabakat ve emir eşleme katmanı olarak doğrudan HyperCore L1 motorunu kullanır. Dolayısıyla HIP-3 piyasalarında da asgari emir büyüklüğü **10 $** olarak uygulanır.
* **Format Kısıtı:** Minimum nominal değere ek olarak her varlığın `szDecimals` (lot hassasiyeti) ve en fazla 5 anlamlı basamak içeren `tick size` kurallarına uyulması şarttır.

* **Kaynak:** [Hyperliquid Docs - Error Responses](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/error-responses) (Erişim tarihi: 29 Ekim 2026)

---

## 4. Önerilen Tek Yön Maliyet Modeli

Mevcut araştırmanızda kullandığınız sabit `%0,045 Taker + %0,050 Kayma = %0,095 (9,5 bps)` varsayımı; BTC/ETH için fazla temkinli, küçük coinler için aşırı iyimser, HIP-3 Büyüme Modu hisseleri içinse gerçeğin yaklaşık 4-6 katı yüksektir.

Aşağıdaki tabloda $1.000 – $10.000 arası piyasa emirleri (taker) için Tier 0 baz alınarak hesaplanan gerçekçi tek yön maliyet aralıkları sunulmuştur:

| Varlık Sınıfı | Taker Ücreti | Ortalama Kayma ($1k–$10k) | Önerilen Tek Yön Maliyet Aralığı | Hesap / Dayanak Gerekçesi |
| :--- | :--- | :--- | :--- | :--- |
| **(a) BTC / ETH** | %0,0450 | %0,0010 – %0,0050 *(tahmin)* | **%0,046 – %0,050** *(~4,6 – 5,0 bps)* | L2 defteri aşırı kalındır; $10k emirde kayma neredeyse sıfırdır (<0,5 bps). Mevcut %0,095 varsayımınız burada %90 oranında maliyet şişirmektedir. |
| **(b) Diğer Büyük Coinler (SOL, AVAX vb.)** | %0,0450 | %0,0100 – %0,0250 *(tahmin)* | **%0,055 – %0,070** *(~5,5 – 7,0 bps)* | HLP piyasa yapıcılığı derinliği korur; $10k emirde ortalama 1–2 bps fiyat kayması gerçekleşir. |
| **(c1) Küçük Coinler (Düşük Hacimli Altcoin)** | %0,0450 | %0,1000 – %0,4500 *(tahmin)* | **%0,145 – %0,495+** *(~14,5 – 50+ bps)* | Defter sığdır. $10k taker emri kademeleri eritir. Mevcut %0,05 kayma varsayımınız bu sınıfta **ciddi derecede iyimserdir**. |
| **(c2) HIP-3: Büyüme Modu (Hisse/TradFi - ABD Seansı)** | %0,0090 | %0,0050 – %0,0150 *(tahmin)* | **%0,014 – %0,024** *(~1,4 – 2,4 bps)* | Büyüme modu protokol ücretini %90 düşürür (%0,009 taker). TradeXYZ üzerinde ABD seansında derinlik CEX düzeyindedir. |
| **(c3) HIP-3: Standart Mod veya Hafta Sonu İşlemleri** | %0,0900 | %0,0500 – %0,2500 *(tahmin)* | **%0,140 – %0,340** *(~14,0 – 34,0 bps)* | 2x deployer çarpanı (%0,09 taker) uygulanır. Hafta sonu borsa kapalıyken makas ve kayma belirgin şekilde açılır. |
