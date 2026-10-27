# sg-arge Projesi: Hyperliquid Copy Trade Kapsamlı Araştırma Notu

## 1. Copy Trade'de Performans Kalıcılığı (Performance Persistence)

### Akademik ve Sektör Çalışmalarının Bulguları
*   **Ortalamaya Dönüş ve Kalıcılık Eksikliği:** Akademik literatür, sosyal ve kopya trading platformlarında (eToro, ZuluTrade, Darwinex vb.) geçmişte yüksek getiri sağlayan lider trader'ların bu başarıyı uzun vadede sürdüremediğini göstermektedir.
    *   Matthias Pelster ve Annette Hofmann tarafından yapılan çalışmada ([Pelster & Hofmann, 2018](https://ideas.repec.org/a/eee/jbfina/v94y2018icp75-88.html)), sosyal trading ortamında trader'ların takipçi kazandıkça ün kaybı korkusu (fear of reputational loss) yaşadığı ve bu durumun zarardaki pozisyonları inatla tutma eğilimini (*disposition effect*) şiddetlendirdiği saptanmıştır.
    *   Yatırım fonları literatüründeki kalıcılık eksikliğine benzer biçimde, kripto copy trading ve Hyperliquid vault'larındaki liderlik tabloları çoğunlukla tek yönlü piyasa koşullarında aşırı kaldıraç kullanan ve şans eseri hayatta kalan trader'ları (*survivorship bias*) öne çıkarmaktadır; piyasa rejimi değiştiğinde performans hızla negatife dönmektedir.

### Takipçilerin Liderden Geri Kalması (Performance Drag)
*   **Uygulama Gecikmesi ve Kayma (Slippage):** Takipçilerin getirisi, kopyalanan trader'ın getirisinin belirgin biçimde gerisinde kalmaktadır ([Copy Trading Slippage Analysis](https://tradedupe.com/blog/copy-trading-slippage)).
    *   Lider trader piyasa emri verdiğinde fiyat kademesini tüketir; hemen ardından gelen takipçi emirleri daha kötü fiyatlardan eşleşir (*arrival price vs fill price*).
    *   Türev piyasalarda saniyeler hatta milisaniyeler seviyesindeki gecikmeler, ani volatilitede takipçilerin kârını %1 ila %5 arasında aşındırmakta; liderin başa baş çıktığı sert dalgalanmalarda takipçiler zarara uğramaktadır.
*   **Maliyet Yapısı ve Asimetrik Risk:** Copy trade platformlarında ve Hyperliquid vault'larında liderler %10 ila %20 arasında kâr payı (*performance fee*) almaktadır. Kârlı dönemlerde getiri bu kesintiyle budanırken, zarar dönemlerinde kaybı tamamen takipçi üstlenmektedir (*asymmetric payoff*).

### "Form Kovalama" (Return / Form Chasing) Etkisi
*   **Sıcak El Yanılgısı:** Sosyal portföylere sermaye akışını inceleyen araştırmalar ([ResearchGate Social Trading Flows](https://www.researchgate.net/publication/330719366_WHAT_DRIVES_INVESTMENT_FLOWS_INTO_SOCIAL_TRADING_PORTFOLIOS)), bireysel yatırımcıların sermayelerini neredeyse tamamen son dönemde en yüksek getiriyi elde eden "yıldız" trader'lara yönelttiğini belgelemektedir.
*   **Ters Zamanlama:** Bu akışlar genellikle stratejinin getiri döngüsünün zirvesine ulaştığı dönemde yoğunlaşmakta; takipçiler tepe noktadan sisteme girip ilk ciddi düzeltmede (*drawdown*) panikle çıkarak reel zarara kilitlenmektedir.

### Gelecekteki Başarıyı Öngören Gerçek Ölçütler
*   **Risk Düzeltilmiş Getiri (Sharpe, Sortino ve Calmar Oranları):** Ham kâr (ROI) yerine getirinin hangi oynaklık ve aşağı yönlü riskle elde edildiği.
*   **Maksimum Sermaye Düşüşü (Max Drawdown - MDD) & Toparlanma Süresi:** Geçmişte sermayenin ne kadar eridiği ve toparlanma süresinin uzunluğu.
*   **Düşük Kaldıraç ve Marjin Disiplini:** Pozisyon başına toplam portföyün %5–10'undan fazlasını bağlamamak ve 2x–3x üzeri aşırı kaldıraçtan kaçınmak.
*   **Farklı Piyasa Rejimlerini Kapsayan Uzun Geçmiş:** En az 6–12 aylık, hem boğa hem ayı hem de yatay testere dönemlerini içeren işlem geçmişi.
*   **Öz Sermaye Katılımı (*Skin in the Game*):** Liderin kendi sermayesinin vault veya kopyalanan havuz içindeki payı. Liderin kendi parasını riske atması ahlaki tehlikeyi (*moral hazard*) sınırlar.

---

## 2. Cloudflare Workers Ücretsiz Plan: Uygulama Rehberi

### Sınırlar ve 20 Cüzdanın Sorgulanması
*   **CPU Süresi Sınırı:** Ücretsiz planda istek başına **10 ms CPU süresi** sınırı bulunmaktadır ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)). Bu sınır saf işlemci süresidir; ağ bekleme (I/O) süresini kapsamaz.
*   **Alt İstek (Subrequest) Sınırı:** İstek başına en fazla **50 alt istek** (`fetch`) yapılabilir ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)).
*   **Sığar mı?** Evet. 20 cüzdan için `POST https://api.hyperliquid.xyz/info` çağrısı tam 20 alt istek tüketir (20 < 50 limit). Yanıt olarak dönen 20 küçük JSON paketini ayrıştırmak ve önceki durumla karşılaştırmak modern V8 motorunda yaklaşık 1–2 ms CPU süresi alır (10 ms sınırının çok altındadır).

### Cloudflare KV Sınırları ve Veri Optimizasyonu
*   **Sınırlar:** Ücretsiz planda günlük **100.000 okuma** ve **1.000 yazma** hakkı verilir ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)).
*   **Kullanım Mimarisi:** 5 dakikada bir çalışan bir cron günde `24 × 12 = 288` kez tetiklenir. 20 cüzdanın anlık durumu tek bir JSON anahtarı (`positions_state`) altında saklanırsa günde en fazla 288 yazma yapılır; bu da 1.000 yazma kotasının rahatlıkla altındadır. Yalnızca pozisyon değişikliği olduğunda yazılırsa bu sayı günde 20–50 yazmaya kadar düşer.

### Telegram Webhook ve `answerCallbackQuery` Birlikteliği
*   Aynı Worker üzerinde hem zamanlanmış görev (`scheduled`) hem de HTTP dinleyici (`fetch`) tek bir modülde birleştirilir:
```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Telegram Webhook Endpoint
    if (url.pathname === "/webhook" && request.method === "POST") {
      // Güvenlik doğrulaması
      if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.TELEGRAM_SECRET) {
        return new Response("Unauthorized", { status: 403 });
      }
      
      const update = await request.json();
      if (update.callback_query) {
        // answerCallbackQuery hemen tetiklenir; arayüzdeki yükleme simgesi söner
        ctx.waitUntil(
          fetch(`https://api.telegram.org/bot${env.TELEGRAM_TOKEN}/answerCallbackQuery`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              callback_query_id: update.callback_query.id,
              text: "İşlem alındı"
            })
          })
        );
      }
      return new Response("OK", { status: 200 });
    }

    // Statik Web Arayüzü İçin Salt Okunur Veri API'si
    if (url.pathname === "/api/positions" && request.method === "GET") {
      const data = await env.WALLET_KV.get("positions_state");
      return new Response(data || "{}", {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS"
        }
      });
    }

    return new Response("Not Found", { status: 404 });
  },

  async scheduled(event, env, ctx) {
    // 5 dakikada bir 20 Hyperliquid cüzdanını sorgula ve KV ile delta karşılaştır
    ctx.waitUntil(checkWalletsAndNotify(env));
  }
};
```

### Statik Web Sayfasından KV Okuma (CORS ve Salt Okunur Uç Nokta)
*   **CORS Yapılandırması:** Worker'ın `/api/positions` uç noktası `Access-Control-Allow-Origin: *` başlığıyla yayınlanır. İstemci tarayıcısının gönderdiği `OPTIONS` preflight istekleri anında `204 No Content` ile karşılanır.
*   **İstemci Tarafı:** GitHub Pages veya Cloudflare Pages üzerinde barınan statik HTML/JS sayfası, standart `fetch('https://<worker-subdomain>.workers.dev/api/positions')` çağrısıyla KV'deki en güncel pozisyon verisini sunucuya gerek duymadan doğrudan çeker.

### Wrangler ve GitHub Actions CI/CD Kurulumu
1.  **Yerel Proje Yapılandırması (`wrangler.toml`):**
    ```toml
    name = "sg-arge-tracker"
    main = "src/index.js"
    compatibility_date = "2026-10-01"

    [triggers]
    crons = ["*/5 * * * *"]

    [[kv_namespaces]]
    binding = "WALLET_KV"
    id = "<CLOUDFLARE_KV_ID>"
    ```
2.  **Otomatik Dağıtım (`.github/workflows/deploy.yml`):**
    GitHub repository ayarlarına `CLOUDFLARE_API_TOKEN` ve `CLOUDFLARE_ACCOUNT_ID` gizli değişkenleri eklenir. `cloudflare/wrangler-action@v3` ile her `main` dalına push işleminde otomatik deploy tetiklenir.
3.  **Gizli Anahtarların Yönetimi:**
    `TELEGRAM_TOKEN` ve `TELEGRAM_SECRET` değerleri asla kod tabanında veya `wrangler.toml` dosyasında tutulmaz; terminalden `npx wrangler secret put TELEGRAM_TOKEN` ile doğrudan Cloudflare'in şifrelenmiş kasa sistemine yazılır.

---

## 3. Hyperliquid'e Özgü Riskler ve Türkiye

### Trader Manipülasyonları, Alt Hesaplar ve Gizli İlişkiler
*   **Tek Cüzdan İzlemenin Kör Noktaları:**
    *   **Çapraz Hedging (Risk Aktarımı):** Bir trader izlenen açık cüzdanda yüksek kaldıraçlı agresif Long açarak liderlik tablosunda üst sıralara tırmanabilirken; takipçilerin görmediği başka bir alt hesapta veya cüzdanda Short açarak kendini risksiz kılabilir. Takipçiler tasfiye olurken lider net arbitraj kârı sağlar.
    *   **Cüzdan Terk Etme (*Survivorship Game*):** Batan cüzdan sessizce terk edilip yeni bir cüzdanla temiz bir sayfa açılabilir.
    *   **Alt Hesaplar (*Subaccounts*):** Hyperliquid tek bir ana cüzdana bağlı alt hesapları destekler. İzleyici sadece ana cüzdana bakıyorsa, alt hesaplardaki koruma veya ters işlemler kaçırılır.
    *   **Vault Frontrunning:** Vault yöneticisi, vault'un büyük hacimli işleminden hemen önce kendi kişisel cüzdanıyla daha düşük likiditeli HIP-3 veya spot tahtasında pozisyon alarak vault likiditesini kendi lehine kullanabilir.
*   **İlişkili Cüzdanları Tespit Etme Yöntemleri:**
    *   **Fonlama Ağacı Analizi:** Cüzdanın Arbitrum köprüsüne yatırdığı USDC'lerin hangi Arbitrum cüzdanından veya merkezi borsa yatırma/çekme adresinden geldiğini Arbiscan üzerinden haritalandırmak.
    *   **İşlem Zamanlaması Korelasyonu:** Blok seviyesinde aynı saniye içinde ters veya paralel işlem açan cüzdanların tespiti.
    *   **Dahili L1 Transferleri:** Hyperliquid L1 üzerindeki cüzdanlar arası `usdTransfer` geçmişlerinin Hyperliquid API üzerinden taranması.

### HIP-3 (Hisse, Endeks, Emtia) Piyasaları
*   **Genel Yapı:** [HIP-3: Builder-deployed Perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals), bağımsız geliştiricilerin (ör. [trade.xyz](https://docs.trade.xyz/)) hisse senetleri, endeksler ve emtialar için vadeli işlem tahtaları açmasına olanak tanır.
*   **İşlem Saatleri ve Hafta Sonu Boşluğu (Gap Risk):** Hyperliquid blokzinciri 7/24 kesintisiz çalışır. Ancak dayanak varlıkların işlem gördüğü geleneksel borsalar (NYSE, NASDAQ, CME) geceleri ve hafta sonları kapalıdır ([trade.xyz Holiday Closures](https://docs.trade.xyz/perpetuals/specifications-and-schedules/holiday-closures)). Hafta sonu spot piyasa kapalıyken oracle fiyatı donar (*stale oracle*). Hafta başında piyasa açılışında meydana gelen sert fiyat boşlukları (*gap*), pozisyonların emir defterinde stoplanamadan anında likidasyona uğramasına yol açabilir.
*   **Likidite:** HIP-3 tahtaları Hyperliquid ana kripto havuzlarından ayrıdır ve bağımsız piyasa yapıcıların sağladığı likiditeye dayanır. Derinlik sığ olduğu için takipçilerin kopyalama emirlerinde ciddi slippage oluşur.
*   **Fiyat Kaynağı (Oracle):** Hyperliquid çekirdek oracle'ı yerine builder tarafından entegre edilen harici oracle ağlarına (Pyth, Stork veya builder'ın kendi fiyat beslemeleri) bağlıdır; oracle gecikmeleri ve manipülasyon riski deployer'ın mimarisine tabidir.

### Türkiye'de Hyperliquid Kullanımı ve Vergilendirme

#### USDC Giriş-Çıkış Rotası (Binance TR Üzerinden)
1.  **Giriş:** Türk bankasından Binance TR'ye TL yatırma → TL ile USDT/USDC satın alma → Arbitrum One ağı seçilerek kişisel Web3 cüzdanına (MetaMask / Rabby) çekim → Web3 cüzdanından Hyperliquid'in Arbitrum Köprü akıllı sözleşmesine USDC yatırma.
2.  **Çıkış:** Hyperliquid L1 arayüzünden Arbitrum One ağına para çekme talebi → Arbitrum'daki USDC'lerin Binance TR cüzdanına aktarılması → Binance TR'de USDC'nin Türk Lirasına çevrilmesi → Banka hesabına havale/EFT.

#### Vergilendirme Durumu (2026 İtibarıyla Bilinenler ve Belirsizlikler)
*   **Bilinenler:** Türkiye'de 2 Temmuz 2024'te yürürlüğe giren 7518 sayılı kanun ile kripto varlık hizmet sağlayıcıları (KVHS) SPK denetimine alınmıştır. Hyperliquid Türkiye'de lisanslı bir borsa değildir; merkeziyetsiz bir protokoldür.
*   **Belirsiz:** 2026 yılı itibarıyla bireysel kripto kazançlarının yıllık gelir vergisi beyannamesine tabi olup olmadığı, zarar mahsubunun yapılıp yapılamayacağı ve yurt dışı DeFi türev işlemlerinden sağlanan kazançların vergilendirilme modeli **belirsiz**dir (yasalaşması beklenen taslaklarda yerli borsalarda işlem başına on binde 3 işlem vergisi veya %10 stopaj tartışılmış, ancak yurt dışı / DeFi türev işlemlerinin gelir türü netleştirilmemiştir). Banka hesabına giren yüksek tutarlı transferler MASAK ve Gelir İdaresi Başkanlığı (GİB) tarafından ticari kazanç şüphesiyle incelemeye alınabilir.

---

## 4. Hazır Uyarı Servisleri Karşılaştırması ve Mimari Karar

### Hazır Servislerin Özellikleri

| Servis / Bot | Ücret | İzlenebilen Cüzdan | Bildirim Gecikmesi | Düğme / Not Ekleme | Veri Dışa Aktarma (API/Webhook) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **[Cielo Finance](https://cielo.finance/)** | Ücretsiz / Pro $59/ay | Ücretsiz planda sınırlı (~5–10 cüzdan), Pro'da 250+ | 1–5 saniye (gerçek zamanlı) | Sabit explorer linkleri var; özel buton/not eklenemez | Ücretsiz planda yok; yalnızca Pro/Enterprise API ile |
| **[EtherDrops (Drops Bot)](https://dropstab.com/products/drops-bot)** | Ücretsiz / Premium $15–$45/ay | Ücretsiz planda azami 10–20 cüzdan | 2–10 saniye (yoğunlukta gecikebilir) | Cüzdana özel etiket verilebilir; callback butonu eklenemez | Yok (Yalnızca Telegram/Discord mesajı) |
| **[HypurrScan](https://hypurrscan.io/) (Hype Alert)** | Ücretsiz | Tarayıcı eklentisinde sınırlı | Birkaç saniye | Özelleştirilebilir düğme/not yok | Yok |
| **[Hyperdash](https://hyperdash.com/)** | Ücretsiz web arayüzü | Web üzerinden takip | Terminalde anlık | Özel Telegram uyarı botu desteği **belirsiz** | Yok |
| **[CoinGlass](https://www.coinglass.com/)** | Ücretsiz / VIP $30–$80/ay | Genel borsa/balina listeleri | Mobil push bildirimleri | Rastgele Hyperliquid cüzdanı ekleme desteği **yok** | Yalnızca genel piyasa API'si |

### Karar Değerlendirmesi: Kendi Botumuz mu, Hazır Servis mi?
*   **Kesinlikle Kendi Botumuzu Yazmak Mantıklıdır:**
    1.  **Etkileşimli Butonlar ve Copy Trade Tetikleme:** Hazır servisler salt okunur bildirim iletir. Kendi botumuzda gelen mesajın altına `"🟢 0.5 ETH ile Kopyala"` veya `"❌ Yoksay"` gibi `callback_data` düğmeleri eklenip tek dokunuşla kendi hesabımızda emir açılabilir.
    2.  **Sıfır Maliyet ve Bağımsızlık:** Cloudflare Workers (günde 100.000 istek ücretsiz) ve Hyperliquid'in ücretsiz `/info` API'si ile 20 cüzdan üçüncü taraf servislerin aylık $50+ abonelik ücretlerine katlanmadan takip edilir.
    3.  **Özel Filtreleme:** Sadece $10.000 üzeri pozisyon açılışlarını bildirme, sadece belirli coinleri filtreleme veya stop-loss takibi yapma esnekliği yalnızca kendi botumuzda mümkündür.

---

## 5. Görünmeyen Hesaplar: Hyperliquid API İstekleri ve Zincir Üstü Analiz

### Hyperliquid API'sinde İlişkili Hesap İstekleri (`POST https://api.hyperliquid.xyz/info`)

#### 1. Alt Hesapları Listeleme (`subAccounts`)
*   **İstek:**
```json
{
  "type": "subAccounts",
  "user": "0x4352125f4a7c87c7a5f6a9e1e779a1d95392d77a"
}
```
*   **Yanıt Örneği:**
```json
[
  {
    "name": "Sub_Aggressive",
    "subAccountUser": "0x789b98721a34...",
    "master": "0x4352125f4a7c...",
    "clearinghouseState": {
      "marginSummary": { "accountValue": "45200.5" },
      "assetPositions": []
    }
  }
]
```

#### 2. Vault İlişkileri (`userVaultEquities` ve `vaultDetails`)
*   **Kullanıcının Katıldığı Vault'lar (`userVaultEquities`):**
```json
{
  "type": "userVaultEquities",
  "user": "0x4352125f4a7c87c7a5f6a9e1e779a1d95392d77a"
}
```
*   **Yanıt Örneği:**
```json
[
  {
    "vaultAddress": "0xabc123456789...",
    "equity": "25000.0"
  }
]
```
*   **Vault Detayları ve Lideri (`vaultDetails`):**
```json
{
  "type": "vaultDetails",
  "vaultAddress": "0xabc123456789..."
}
```
*   **Yanıt Örneği:**
```json
{
  "name": "AlphaWhaleVault",
  "leader": "0x4352125f4a7c...",
  "leaderFraction": 0.05,
  "leaderCommission": 0.10,
  "followers": [
    { "user": "0x1111...", "vaultEquity": "10000.0", "pnl": "450.0" }
  ]
}
```

#### 3. Cüzdanlar Arası USDC Transferleri (`userNonFundingLedgerUpdates`)
*   **İstek:**
```json
{
  "type": "userNonFundingLedgerUpdates",
  "user": "0x4352125f4a7c87c7a5f6a9e1e779a1d95392d77a"
}
```
*   **Yanıt Örneği:**
```json
[
  {
    "time": 1714567890000,
    "hash": "0x3f4a...",
    "delta": {
      "type": "internalTransfer",
      "usdc": "15000.0",
      "user": "0x4352125f4a7c...",
      "destination": "0x987fedcba321..."
    }
  }
]
```
*   *İpucu:* `destination` veya `user` alanındaki adres, trader'ın bizzat fon transfer ettiği ilişkili cüzdandır.

#### 4. Yetkilendirilmiş API Ajanları (`extraAgents`)
*   **İstek:**
```json
{
  "type": "extraAgents",
  "user": "0x4352125f4a7c87c7a5f6a9e1e779a1d95392d77a"
}
```
*   **Yanıt Örneği:**
```json
[
  {
    "address": "0xagent998877...",
    "name": "MarketMakingBot"
  }
]
```
*   *İpucu:* İki farklı kullanıcı cüzdanı aynı `agent` adresini yetkilendirmişse, bu cüzdanların arkasındaki emir imzalayıcı ve strateji sahibi aynı kişidir.

### İlişkili Cüzdanları Bulmak İçin Pratik Adımlar
1.  **Adım 1 (API Sorguları):** Hedef adrese sırasıyla `subAccounts`, `userVaultEquities`, `extraAgents` ve `userNonFundingLedgerUpdates` sorguları atılır. Resmi alt hesaplar, yöneticisi olduğu vault'lar ve iç USDC transferi yaptığı cüzdanlar doğrudan ortaya çıkar.
2.  **Adım 2 (Arbitrum Köprü Analizi):** Hedef adresin Hyperliquid Arbitrum Bridge sözleşmesine yatırdığı fonların kaynağı [Arbiscan](https://arbiscan.io/) üzerinden taranır. Bu cüzdana ilk gaz (ETH) veya USDC gönderen ana cüzdan incelenerek diğer paralel cüzdanlar haritalandırılır.
3.  **Adım 3 (Zaman ve Blok Korelasyonu):** Blok seviyesinde aynı saniye içinde ters yönlü (hedge) veya eşzamanlı emir ileten adresler kümelenerek gizli trader ağları saptanır.

### Zincir Üstü Analiz Araçları (Arkham, Nansen vb.)
*   **[Arkham Intelligence](https://info.arkm.com/announcements/hyperliquid-is-now-on-arkham):** HyperCore verilerini doğrudan sistemine entegre etmiştir. Görsel kümeleme (Visualizer / Entity Tracking) aracıyla Hyperliquid köprüsüne Arbitrum üzerinden fon aktaran ana cüzdanları kümeleyerek trader'ın diğer ağlardaki adreslerini ve ilişkili cüzdan ağını ortaya çıkarır.
*   **[Nansen](https://docs.nansen.ai/api/hyperliquid):** Hyperliquid için "Smart Money" etiketleri, portföy dağılımları ve liderlik tablosu API'si sunarak cüzdanların kurumsal veya piyasa yapıcı ilişkilerini analiz etmeyi sağlar.