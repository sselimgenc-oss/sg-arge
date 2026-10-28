> **Lider notu (2026-10-28):** Bağlantılar resmi Hyperliquid belgelerine; içerik daha önce bildiklerimizle tutarlı (1.200 ağırlık/dk,
> websocket'te 10 kullanıcı, `clearinghouseState` 2). Lider bağlantıları ayrıca açmadı. Kullanım:
> - **En küçük emir 10 $** (perp, HIP-3 USDC dahil) → `GOREV_SECIM_V1.md` Ek 2 `min_emir_alti_*` eşiği; `kurallar.yaml`'a kaynağıyla.
> - Reduce-only için resmi muafiyet yok; tam kapatma pratikte kabul ediliyor (ikincil kaynak). Gerçek para aşamasında "10 $ altına
>   düşecek kısmi çıkışta tamamen kapat" kuralı adayı (kullanıcı kararı).
> - **Bakım teminatı = 1 / (2 × maxLeverage)**: gölgedeki likidasyon (1 birim sermaye bitince) bundan iyimser; gerçekçi likidasyon
>   gerçek para öncesi eklenir.
> - 10'dan fazla trader için canlı izleme websocket ile değil REST yoklamayla (bugünkü tasarım zaten böyle).

# Hyperliquid Perp Copy-Trading Simülasyonu: Resmi Emir, Marjin ve API Kuralları

Bu belge, küçük sermayeli ($200 – $1.000) Hyperliquid sürekli vadeli (perp) copy-trading simülasyonları için borsa motoru (HyperCore) ve API kısıtlamalarını resmi kaynaklara dayalı olarak özetler.

---

## 1. En Küçük Emir Büyüklüğü (Notional Minimum) & HIP-3 Piyasaları

* **Sabit Notional Tabanı:** Hyperliquid perp piyasalarında minimum emir büyüklüğü tüm varlıklarda sabit **10 USD**'dir ($\text{Emir Büyüklüğü (sz)} \times \text{Fiyat (px)} \ge 10\text{ USD}$). Coine göre değişmez.
* **Hata Kodu:** 10 USD altındaki perp emirleri API motoru tarafından doğrudan reddedilir:
  ```json
  { "error": "Order must have minimum value of $10." }
  ```
  *(Hata tipi: `MinTradeNtl`)*
* **HIP-3 (Builder-Deployed Perps) Durumu:** HIP-3 perp piyasaları doğrudan HyperCore çekirdek eşleşme motoru üzerinde çalıştığı için aynı kurallara tabidir. Teminat birimi USDC olan HIP-3 piyasalarında minimum sınır yine 10 USD'dir. Farklı bir teminat/kotasyon varlığı kullanan piyasalarda kural `MinTradeSpotNtl: "Order must have minimum value of 10 {quote_token}."` şeklindedir.
* **Simülasyon Etkisi:** Küçük sermayeli hesaplarda lider trader'ın pozisyon büyüklüğü ölçeklendiğinde hesaplanan emir değeri 10 USD'nin altında kalıyorsa emir doğrudan reddedileceğinden ya emrin taban değer olan 10 USD'ye yuvarlanması ya da emrin atlanması gerekir.
* **Resmi Kaynaklar:**
  * [Hyperliquid Docs - Error Responses](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/error-responses)
  * [Hyperliquid Docs - HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals)
* **Erişim Tarihi:** 28 Ekim 2026

---

## 2. Büyüklük (`szDecimals`) ve Fiyat (Tick / Anlamlı Basamak) Yuvarlama Kuralları

Hem fiyat (`px`) hem de büyüklük (`sz`) borsa tarafından kabul edilen belirli ondalık ve anlamlı basamak sınırlarına sahiptir.

### Büyüklük (Size / Lot) Kuralları
* Her varlığın büyüklük hassasiyeti kendisine özel `szDecimals` parametresi ile sınırlandırılmıştır.
* Emir büyüklüğü (`sz`), varlığın `szDecimals` basamak sayısına yuvarlanmalıdır.
  * *Örnek:* Bir varlık için `szDecimals = 3` ise `1.001` geçerlidir; ancak `1.0001` geçersizdir ve reddedilir.

### Fiyat (Price / Tick) Kuralları
1. **Anlamlı Basamak Sınırı:** Fiyatlar en fazla **5 anlamlı basamağa (significant figures)** sahip olabilir.
2. **Maksimum Ondalık Sınırı:** Fiyat ondalık basamak sayısı perp piyasalarında en fazla `6 - szDecimals` olabilir (`MAX_DECIMALS` perp için 6, spot için 8'dir).
   * *Örnek 1:* `1234.5` geçerlidir; ancak `1234.56` 6 anlamlı basamak içerdiği için geçersizdir.
   * *Örnek 2:* `0.001234` geçerlidir; ancak `0.0012345` 7 ondalık basamak içerdiği için geçersizdir.
   * *Örnek 3:* `szDecimals = 1` ise izin verilen maksimum fiyat ondalığı `6 - 1 = 5` basamaktır. `0.01234` geçerli iken `0.012345` geçersizdir.
3. **Tam Sayı İstisnası:** Tam sayı fiyatlar (integers) anlamlı basamak kuralından muaftır (ör. `123456` geçerli bir fiyattır).

### `meta` Uç Noktasındaki Alanlar
POST `https://api.hyperliquid.xyz/info` adresine `{"type": "meta"}` (veya HIP-3 için `{"type": "meta", "dex": "<dex_name>"}`) gönderildiğinde dönen yanıtta `universe` dizisi bulunur. Her coin için incelenmesi gereken temel alanlar şunlardır:

| Alan Adı | Tip | Açıklama |
| :--- | :--- | :--- |
| `name` | `string` | Varlık sembolü (ör. `"BTC"`, `"ETH"`) |
| `szDecimals` | `number` | İzin verilen lot boyutu ondalık basamak sayısı |
| `maxLeverage` | `number` | Varlık için tanımlı maksimum kaldıraç çarpanı |
| `onlyIsolated` | `boolean` | Varlığın yalnızca izole marjinde işlem görüp görmediği |

* **Resmi Kaynaklar:**
  * [Hyperliquid Docs - Tick and lot size](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size)
  * [Hyperliquid Docs - Info endpoint (Perpetuals)](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals)
* **Erişim Tarihi:** 28 Ekim 2026

---

## 3. Piyasa Emrinin (Market Order) Çalışma Mantığı ve Kayma Sınırları

* **Protokol / API Düzeyi:** Hyperliquid L1 eşleşme motorunda yerel bir "market order" tipi bulunmaz. Tüm piyasa emirleri, defterin karşı tarafındaki fiyatı süpürecek agresif bir limit fiyatla gönderilen **IOC (Immediate or Cancel)** limit emirleri olarak yürütülür:
  ```json
  {
    "order_type": {
      "limit": { "tif": "Ioc" }
    }
  }
  ```
  Defterdeki likidite ile anında eşleşmeyen bakiye defterde beklemez, otomatik olarak iptal edilir.
* **Kayma (Slippage) Hesabı:** Alış emirlerinde `limit_px = mid_price * (1 + slippage)`, satış emirlerinde `limit_px = mid_price * (1 - slippage)` formülüyle hesaplanır ve 5 anlamlı basamak / `szDecimals` kuralına göre yuvarlanır.
* **Varsayılan Kayma (Slippage) Oranları:**
  * **Resmi Python SDK (`hyperliquid-python-sdk`):** `market_open` ve `market_close` fonksiyonlarında varsayılan kayma toleransı **%5** (`DEFAULT_SLIPPAGE = 0.05`) olarak tanımlanmıştır.
  * **Web Arayüzü / TP-SL:** Tetiklenen piyasa Take Profit / Stop Loss emirlerinde arayüz varsayılanı **%10**'dur.
  * **TWAP Alt Emirleri:** TWAP kapsamında gönderilen alt piyasa emirleri en fazla **%3** kayma ile sınırlandırılmıştır.
* **Resmi Kaynaklar:**
  * [Hyperliquid Docs - Order types](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-types)
  * [Hyperliquid Docs - My TP/SL did not execute correctly](https://hyperliquid.gitbook.io/hyperliquid-docs/support/faq/trade-outcome-looks-incorrect/my-tp-sl-did-not-execute-correctly)
  * [Hyperliquid Official Python SDK GitHub (exchange.py)](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
* **Erişim Tarihi:** 28 Ekim 2026

---

## 4. Azaltma Emirleri (Reduce-Only) ve Küçük Pozisyon Kapatma

* **Resmi Dokümantasyon Durumu:** **Resmi kaynakta reduce-only emirler için $10 sınırından muafiyet sağlayan bir kural YOKTUR.**
  * Resmi API hata listesinde `MinTradeNtl: "Order must have minimum value of $10."` kuralı koşulsuz olarak yer alır; `reduceOnly: true` olan emirlerin bu kontrolden muaf tutulduğuna dair resmi bir istisna belirtilmemiştir.
* **İkincil / Topluluk Kaynakları:**
  * İkincil geliştirici kılavuzları ve pratik testler, pozisyonun **tamamını tek seferde kapatan** bir emir gönderildiğinde sistemin 10 USD altındaki pozisyon kapatmalarını kabul edebildiğini belirtmektedir.
  * Ancak kısmi kapatmalar sonucunda pozisyon büyüklüğü 10 USD'nin altına düşerse ("dust" pozisyon), sonraki azaltma emirlerinin `MinTradeNtl` engeline takılabileceği vurgulanmaktadır.
* **Simülasyon Önerisi:** Küçük sermayeli hesaplarda oransal çıkış yapılırken kalan pozisyonun 10 USD altına inmesi engellenmeli; bakiye kritik sınıra yaklaştığında pozisyon tek seferde tamamen kapatılmalıdır.
* **Resmi ve İkincil Kaynaklar:**
  * Resmi: [Hyperliquid Docs - Error responses](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/error-responses)
  * İkincil Kaynak: [Cipher Intelligence - Hyperliquid Minimum Order Size](https://cipher-intelligence.io/blog/dex-minimum-trade-size-comparison/)
* **Erişim Tarihi:** 28 Ekim 2026

---

## 5. API İstek Sınırları (Rate Limits)

API kısıtlamaları IP bazlı ve adres (hesap) bazlı olmak üzere iki katmandan oluşur.

### IP Başına REST Sınırları
* **Toplam Kota:** IP başına dakikada toplam **1.200 ağırlık (weight)**.
* **Uç Nokta Ağırlıkları (İstenenler):**
  * `clearinghouseState`: **2**
  * `l2Book`: **2**
  * `candleSnapshot`: Temel **20** + yanıtta dönen her 60 mum için **+1** ek ağırlık
  * `userFillsByTime`: Temel **20** + yanıtta dönen her 20 işlem için **+1** ek ağırlık
  *(Genel Kural: Liste dönen geçmiş veri uç noktaları her 20 öğe için +1 ek ağırlık alır; belgelenmiş diğer `info` istekleri varsayılan 20 ağırlığındadır; toplu işlem emirleri ise `1 + floor(batch_length / 40)` ağırlığındadır).*

### WebSocket Sınırları
* Maksimum **10 aktif bağlantı**.
* Dakikada en fazla **30 yeni bağlantı**.
* Maksimum **1.000 abonelik (subscription)**.
* **İzlenebilecek Kullanıcı Sayısı:** Kullanıcıya özel websocket aboneliklerinde (user-specific subscriptions) toplamda en fazla **10 benzersiz kullanıcı (unique users)** dinlenebilir. *(Copy-trading mimarisinde 10'dan fazla lider trader takip edilecekse REST polling veya çoklu IP/bağlantı stratejisi gereklidir).*
* Tüm websocket bağlantıları üzerinden Hyperliquid'e gönderilebilecek mesaj sayısı: **dakikada en fazla 2.000**.
* Eşzamanlı bekleyen (inflight) istek sınırı: **en fazla 100**.

### Adres Başına Sınırlar (Address-Based Limits)
* Sadece `exchange` (emir/iptal) işlemlerine uygulanır; `info` veri sorgularını etkilemez.
* **Hacim Orantılı İstek:** Adresin açılışından itibaren kümülatif yapılan her **1 USDC işlem hacmi için 1 isteğe** izin verilir (örneğin 100 USDC'lik bir emir için en az %1 gerçekleşme oranı gerekir).
* **Başlangıç Tamponu:** Her adres başlangıçta **10.000 istekli** bir kredi tamponu ile başlar.
* **Ceza Rejimi:** Limit aşıldığında adres her 10 saniyede yalnızca 1 istek yapabilir. İptal emirleri için tavan $\min(\text{limit} + 100.000, \text{limit} \times 2)$ formülüyle esnetilir; böylece emir gönderme kısıtlansa dahi açık emirler iptal edilebilir.
* **Açık Emir Sayısı:** Varsayılan açık emir tavanı 1.000'dir; her 5M USDC hacim için +1 eklenir (üst tavan 5.000).
* **Resmi Kaynak:** [Hyperliquid Docs - Rate limits and user limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits)
* **Erişim Tarihi:** 28 Ekim 2026

---

## 6. Kaldıraç, Teminat ve Likidasyon Fiyatı Formülü

### Varlık Başına En Yüksek Kaldıraç
POST `https://api.hyperliquid.xyz/info` adresine `{"type": "meta"}` veya `{"type": "metaAndAssetCtxs"}` gönderilerek varlığın `universe[i].maxLeverage` değerinden okunur (ör. BTC için 40x, ETH için 25x, SOL için 20x).

### İzole ve Çapraz (Cross) Marjin Farkı
* **Çapraz Marjin (Cross - Varsayılan):** Hesap bakiyesi ve gerçekleşmemiş kâr/zarar (uPnL) tüm çapraz pozisyonlar arasında ortak teminat olarak paylaşılır. Sermaye verimliliği sağlar ancak tasfiye anında tüm çapraz pozisyonlar ve bakiye likidatör kasasına devredilir.
* **İzole Marjin (Isolated):** Teminat yalnızca ilgili varlığa tahsis edilir. Varlığın tasfiyesi veya zararı diğer pozisyonları ve ana hesap bakiyesini etkilemez. Pozisyona manuel teminat eklenebilir veya çekilebilir.

### Likidasyon Fiyatı Formülü
Hyperliquid motorunda bir pozisyonun likidasyon fiyatı şu formülle hesaplanır:

$$\text{liq\_price} = \text{price} - \frac{\text{side} \times \text{margin\_available}}{\text{position\_size} \times (1 - l \times \text{side})}$$

**Değişkenler ve Parametreler:**
* $\text{side}$: Long pozisyonlar için $+1$, Short pozisyonlar için $-1$
* $\text{margin\_available}$ (Çapraz): $\text{account\_value} - \text{maintenance\_margin\_required}$
* $\text{margin\_available}$ (İzole): $\text{isolated\_margin} - \text{maintenance\_margin\_required}$
* $l = \frac{1}{\text{MAINTENANCE\_LEVERAGE}}$
  * Bakım marjı, maksimum kaldıraçtaki başlangıç marjının yarısıdır:
    $$\text{Maintenance Margin Ratio} = \frac{1}{2 \times \text{maxLeverage}}$$
  * Dolayısıyla bakım kaldıracı $\text{MAINTENANCE\_LEVERAGE} = 2 \times \text{maxLeverage}$ olur (örneğin 40x maksimum kaldıraçlı BTC için bakım marjı %1,25, yani bakım kaldıracı 80x'tir; $l = 1/80 = 0,0125$).
* **Resmi Kaynaklar:**
  * [Hyperliquid Docs - Margining](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining)
  * [Hyperliquid Docs - Liquidations](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations)
  * [Hyperliquid Docs - Info endpoint (Perpetuals)](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals)
* **Erişim Tarihi:** 28 Ekim 2026
