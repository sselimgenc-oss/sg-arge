# Argon — Cloudflare Worker + Hyperliquid + Telegram teknik notu (2026-10-27)

Kaynak: Argon cevabı (bölüm 6). Lider notları en altta.


### 1. Cloudflare Ücretsiz Plan Sınırları
*   **Cron Trigger Aralığı:** Cloudflare Workers Cron Trigger'ın en kısa çalıştırma aralığı **1 dakikadır** (`* * * * *`) ([Cloudflare Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/)). 5 dakikalık aralık (`*/5 * * * *`) standart desteklenir.
*   **Alt İstek (Subrequest) Sınırı:** İstek başına en fazla **50 alt istek** (`fetch`) yapılabilir ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)). 20 Hyperliquid cüzdanı tek bir Cron çağrısında 20 bağımsız `fetch` ile sorgulanabilir (20 < 50).
*   **CPU Süresi Sınırı:** Ücretsiz planda istek başına sınır **10 ms CPU süresidir** ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)). Dış ağ çağrıları (`fetch`) sırasında yanıt beklerken geçen I/O süresi CPU süresine **sayılmaz** (duvar saati süresi azami 30 saniyedir). 20 JSON yanıtını işlemek yaklaşık 1–2 ms CPU süresi harcar.
*   **KV Sınırları ve 5 Dakikalık Yazma:** Ücretsiz planda günlük **100.000 okuma** ve **1.000 yazma** hakkı verilir ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)). 5 dakikada bir yazma işlemi günde tam 288 kez gerçekleşir ve 1.000 yazma sınırının rahatlıkla altındadır (288 < 1.000).
*   **KV Tutarlılığı ve Alternatifler:** KV nihai tutarlıdır (*eventually consistent*, uçlar arası önbellek süresi 60 saniyeye kadar çıkabilir). 5 dakikalık aralıkta aynı olayın iki kez bildirilme riski çok düşüktür ancak sıfır değildir. Daha sağlam bir alternatif olarak [Cloudflare D1](https://developers.cloudflare.com/d1/) (SQLite tabanlı, ücretsiz planda günlük 100.000 satır yazma ve 5 milyon satır okuma) anlık güçlü tutarlılık sunar; ayrıca [Durable Objects](https://developers.cloudflare.com/durable-objects/) ücretsiz katmanda SQLite desteğiyle mevcuttur.

### 2. Hyperliquid API ve Ağ Özellikleri
*   **`clearinghouseState` ve HIP-3 Piyasaları:** Varsayılan `clearinghouseState` sorgusunda `dex` parametresi verilmezse yalnızca ana kripto vadeli işlemleri döner ([Hyperliquid ClearinghouseState Docs](https://docs.chainstack.com/reference/hyperliquid-info-clearinghousestate)). HIP-3 kapsamındaki hisse, endeks veya emtia pozisyonlarını (ör. `xyz:NVDA`) alabilmek için istek gövdesine `dex: "xyz"` eklenmelidir. Sistemdeki tüm DEX'lerin listesi `POST /info` adresine `{"type": "perpDexs"}` gönderilerek alınır ([Hyperliquid PerpDexs Docs](https://www.google.com/search?q=https://docs.chainstack.com/reference/hyperliquid-info-perpdexs)).
*   **Paylaşımlı Egress IP ve 429 Riski:** Hyperliquid IP başına dakikada 1.200 ağırlık sınırı uygular ([Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits)). Cloudflare Workers çıkış (egress) IP'leri tüm Cloudflare kullanıcılarıyla paylaşıldığı için aynı veri merkezindeki yoğunluktan ötürü nadiren geçici HTTP 429 hatası alınabilir; kalıcı bir IP engeli vakası **doğrulanmadı**.
*   **Kalıcı WebSocket İmkânı:** Worker durumsuz (stateless) bir ortamdır; bir istek veya cron bittiğinde çalışma sonlanır. Ücretsiz planda Hyperliquid'e bağlı 7/24 açık kalıcı bir istemci WebSocket bağlantısı sürdürmek **mümkün değildir**; periyodik cron yoklaması zorunludur.

### 3. Telegram Bot Entegrasyonu
*   **`secret_token` Doğrulaması:** Bot `setWebhook` çağrısında rastgele bir `secret_token` belirlenir ([Telegram Webhook Security](https://core.telegram.org/bots/api#setwebhook)). Worker'a gelen isteklerde `request.headers.get("X-Telegram-Bot-Api-Secret-Token") === env.SECRET_TOKEN` kontrolü yapılarak sahte istekler 403 ile reddedilir.
*   **`answerCallbackQuery` Zorunluluğu ve Süresi:** Zorunludur ([Telegram Bot API](https://core.telegram.org/bots/api#answercallbackquery)). Çağrılmadığında Telegram istemcisindeki buton animasyonu (spinner) takılı kalır. Yaklaşık 20–30 saniyelik zaman aşımı süresi vardır; gecikilirse `400 Bad Request: query is too old` hatası döner.
*   **Düğmeleri Kaldırma (`editMessageReplyMarkup`):** Karar verildikten sonra düğmeleri tamamen kaldırmak için `reply_markup: { inline_keyboard: [] }` gönderilir; ya da buton metni `{ inline_keyboard: [[{ text: "✅ İşlendi", callback_data: "done" }]] }` şeklinde pasif hale getirilir ([Telegram Bot API editMessageReplyMarkup](https://core.telegram.org/bots/api#editmessagereplymarkup)).
*   **Tek Kullanıcı Güvenliği:** Worker secret kasasında `MY_CHAT_ID` saklanır; gelen `update.callback_query.from.id` veya `message.chat.id` bu ID ile eşleşmiyorsa istek anında yok sayılır.

### 4. Kararların Saklanması: Seçenek (a) vs Seçenek (b)
*   **Seçenek (a) — Worker'ın Doğrudan GitHub'a Yazması:**
    *   *Risk & Karmaşıklık:* Cloudflare Worker üzerinde GitHub Personal Access Token (PAT) saklamak gerekir. GitHub Contents API'de dosya güncellemek için önce mevcut dosyanın `sha` değerini çekmek (`GET`), içeriğe satır ekleyip base64 kodlayarak `PUT` göndermek şarttır. Arka arkaya iki butona basıldığında veya repoya eşzamanlı bir commit geldiğinde `409 Conflict` (eski SHA) hatası oluşur ve Worker tarafında karmaşık yeniden deneme (retry) mantığı gerektirir.
*   **Seçenek (b) — Worker'ın KV/D1'de Tutması, Actions'ın Çekmesi:**
    *   *Güvenlik & Sadelik:* Cloudflare üzerinde hiçbir GitHub yetkisi bulunmaz; token sızıntı riski sıfırdır. Butona basıldığında Telegram yanıtı gecikmesiz verilir. Saatlik GitHub Actions işi, Worker'ın gizli anahtarla korunan salt-okunur uç noktasından (`/api/kararlar`) yeni kayıtları çeker ve yerel git komutlarıyla `izleme/kararlar.jsonl` dosyasına çakışmasız yazar.

---

### Önerim (5 Maddelik Özet)
1.  **Mimari Ayrım (Seçenek b):** Kararları Worker içinde KV/D1'e kaydedin; saatlik GitHub Actions işi bu verileri Worker'dan çekip repoya yazsın (Cloudflare'de GitHub token'ı tutmayın).
2.  **Veri Depolama (D1 Tercihi):** Nihai tutarlılık gecikmelerini ve mükerrer bildirim riskini tamamen sıfırlamak için KV yerine ücretsiz [Cloudflare D1](https://developers.cloudflare.com/d1/) kullanın.
3.  **HIP-3 Kapsamı:** Takip ettiğiniz cüzdanlar hisse/emtia tahtalarında işlem yapıyorsa, `clearinghouseState` çağrısını hem ana borsa hem de `dex: "xyz"` parametresiyle ayrı ayrı yapın.
4.  **Hata Yönetimi ve 429 Toleransı:** Paylaşımlı Cloudflare çıkış IP'lerinden kaynaklanabilecek olası geçici 429 yanıtlarına karşı 1–2 saniyelik tek bir yeniden deneme (*retry with backoff*) ekleyin.
5.  **Kullanıcı Arayüzü Temizliği:** Kullanıcı `[Açtım]` veya `[Atladım]` butonuna bastığı anda `answerCallbackQuery` ile bildirimi onaylayın ve `editMessageReplyMarkup` ile düğmeleri kaldırıp mesaj metnine seçilen kararı ekleyin.
## 7. Argon: Worker İstek Bütçesi ve HIP-3 Piyasa Analizi

### 1. `perpDexs` Listesi ve Aktif DEX'ler
*   `POST /info` adresine `{"type": "perpDexs"}` gönderildiğinde dönen dizinin ilk elemanı varsayılan ana kripto borsasını (`null`), devamı ise builder DEX'leri listeler ([Hyperliquid PerpDexs Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals)).
*   **Aktif DEX'ler ve Hacim:**
    *   **`xyz` ([trade.xyz](https://docs.trade.xyz/)):** HIP-3 ekosistemindeki tek ana ve likit DEX'tir. Tokenize ABD hisseleri (NVDA, TSLA, AAPL, MU), endeksler (SP500, Nifty 50), emtialar (Altın, Petrol) ve döviz listeler. Günlük işlem hacmi yaklaşık 10M–50M dolar bandındadır ve HIP-3 hacminin %95'inden fazlasını oluşturur.
    *   **Diğerleri (`flx`, `para`, `vntl` vb.):** Felix, Parallel veya Ventuals gibi diğer builder DEX'ler listelenmiş olsa da günlük hacimleri çoğunlukla 100 bin doların altındadır ve pratik olarak **kullanılmamaktadır**.

### 2. Tüm DEX Pozisyonlarını Tek İstekte Veren Uç Nokta
*   **YOK.** [webData2](https://docs.chainstack.com/reference/hyperliquid-info-web-data2) veya [clearinghouseState](https://docs.chainstack.com/reference/hyperliquid-info-clearinghousestate) uç noktaları `dex` parametresi alır ve varsayılan olarak yalnızca ana kripto tahtasını (`""`) döner. Bir kullanıcının tüm builder DEX'lerdeki pozisyonlarını tek bir JSON yanıtında toplayan resmi birleşik bir istek türü **yoktur**.

### 3. Kullanıcının Hangi DEX'lerde Olduğunu Ucuza Anlama
*   **Son İşlemler (`userFills`):** `POST /info` ile `{"type": "userFills", "user": "0x..."}` çağrıldığında dönen `coin` alanında iki nokta (`:`) öneki (ör. `xyz:NVDA`) aranır ([Hyperliquid Info Endpoint Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)). Önek içeren işlem yoksa cüzdanın HIP-3 tahtalarında aktif olmadığı anlaşılır.
*   **D1/KV Önbellek Bayrağı (*Lazy Polling*):** Trader'ların büyük kısmı yalnızca ana kripto tahtasında işlem yapar. Cüzdan veritabanında `uses_hip3: false` olarak işaretlenir; gereksiz yere her 5 dakikada bir `dex: "xyz"` sorgusu atılmayarak istek kotası korunur.

### 4. 50 Alt İstek Sınırına Göre Seçenekler
*   **Mevcut Durum Hesabı:** Sistemde fiilen izlenmesi gereken yalnızca 2 DEX vardır (Ana kripto + `xyz`). 20 cüzdan × 2 DEX = **40 istek**. 40 alt istek, Cloudflare'in 50'lik tavan sınırının altındadır (40 < 50) ve şu an tek cron'a sığmaktadır.
*   **Seçenek (a) — Yalnız Kullanılan DEX'leri Sormak:** İstek sayısını 20–25 bandına çekerek en güvenli marjı sağlar; önerilen temel yöntemdir.
*   **Seçenek (b) — Cüzdanları 2 Cron'a Bölmek:** Cüzdan sayısı 25'i aştığında veya ikinci bir aktif DEX devreye girdiğinde en temiz ve hatasız büyüme yoludur.
*   **Seçenek (c) — Cloudflare Diğer Yolları:** Cloudflare Queues ücretsiz planda **yoktur** (ücretli plandır) ([Cloudflare Workers Pricing](https://developers.cloudflare.com/workers/platform/pricing/)). Durable Objects ise bu ölçek için gereksiz karmaşıktır.

### 5. HIP-3 Bildirim Gecikmesi ve Piyasa Saatleri
*   **İşlem Saatleri:** trade.xyz hisse ve endeks tahtaları geleneksel borsa seanslarına (NYSE/NASDAQ 09:30–16:00 EST) tabidir; hafta sonları ve gece seans dışı saatlerde resmi piyasalar kapalıdır ([trade.xyz Specification Index](https://docs.trade.xyz/perpetuals/specifications-and-schedules/specification-index)).
*   **Gecikmenin Pratikteki Anlamı:**
    *   *Gece ve Hafta Sonu:* Dayanak piyasalar kapalıyken oracle fiyatı donar, işlem hacmi durur. Bu saatlerde 10 dakikalık gecikme sıfır risk taşır.
    *   *Hafta İçi Seans İçi:* ABD piyasa açılışında (16:30 TSİ) hisselerdeki ilk 10 dakikalık oynaklık yüksek olabileceğinden 5 dakikalık kontrol aralığı korunmalıdır.
    *   *Temel Risk:* Gecikmeden ziyade, hafta sonu açık bırakılan pozisyonların Pazartesi piyasa açılışında oluşan fiyat boşluğuyla (*gap risk*) doğrudan likidasyona uğramasıdır.

---

### Önerim (3 Maddelik Özet)
1.  **Sorguları Sadece Ana Borsa ve `xyz` ile Sınırlayın:** Diğer DEX'ler hacimsiz olduğundan 20 cüzdan için yalnızca varsayılan tahta (`""`) ve `dex: "xyz"` sorgusu atarak toplam 40 alt istekle 50 sınırının altında kalın.
2.  **Dinamik DEX Filtresi Ekleyin:** Cüzdanları D1'de `uses_hip3` bayrağı ile etiketleyin; geçmişinde hisse/emtia işlemi olmayan cüzdanlara `xyz` sorgusu atmayarak alt istek sayısını 20–25'e düşürün.
3.  **Seans Dışı Saatlerde `xyz` Sorgularını Kapatın:** Hafta sonları ve New York seansı kapalıyken Worker kodunda `xyz` sorgularını çalıştırmayarak CPU ve istek bütçesinden tasarruf edin.

## Lider notları
- Karar önerisi: kararlar seçenek (b) ile tutulur (Cloudflare'de GitHub token'ı yok), depo olarak KV yerine D1. İş B görevinde kesinleşir.
- **HIP-3 uyarısı:** `clearinghouseState` `dex` verilmezse yalnız ana kripto pozisyonlarını döndürür. İzleme motoru (İş A) da
  her dex için ayrı sorgu yapmalı; ana listeyi `perpDexs` verir.
- Argon'un "tek dokunuşla emir açan düğme" önerisi (bölüm 4) reddedildi: sistem emir göndermez.
- **Alt istek bütçesi kararı (bölüm 7):** Worker her trader için ana tahta + yalnız o trader'ın kullandığı dex'leri sorar.
  Hangi dex'leri kullandığını saatlik Actions işi `userFills` coin öneklerinden (`xyz:` vb.) bulur ve `durum.json`'a yazar;
  Worker bunu okur. Dex adı sabit yazılmaz (yalnız `xyz` değil). 50'yi aşarsa trader'lar iki cron'a bölünür.
- **Reddedildi:** "seans dışında `xyz` sorgularını kapat" önerisi. HIP-3 tahtaları 7/24 işlem görür (kapanan dayanak piyasa,
  tahta değil); trader gece/hafta sonu açıp kapatabilir, olay kaçar. Argon'un hacim rakamları doğrulanmadı.
