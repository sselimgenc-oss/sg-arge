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
## Lider notları
- Karar önerisi: kararlar seçenek (b) ile tutulur (Cloudflare'de GitHub token'ı yok), depo olarak KV yerine D1. İş B görevinde kesinleşir.
- **HIP-3 uyarısı:** `clearinghouseState` `dex` verilmezse yalnız ana kripto pozisyonlarını döndürür. İzleme motoru (İş A) da
  her dex için ayrı sorgu yapmalı; ana listeyi `perpDexs` verir.
- Alt istek bütçesi: 20 cüzdan × (1 + dex sayısı) sorgu 50 sınırını aşabilir; çözüm Argon'un sıradaki notunda.
- Argon'un "tek dokunuşla emir açan düğme" önerisi (bölüm 4) reddedildi: sistem emir göndermez.
