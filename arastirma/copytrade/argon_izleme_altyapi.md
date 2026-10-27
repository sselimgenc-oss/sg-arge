# sg-arge Projesi: Hyperliquid Cüzdan Takibi, Telegram Bot Mimarisi ve Mobil UI Araştırma Notu

## 1. Hyperliquid Cüzdan Takibi ve Altyapı Seçimi

*   **En İyi Yöntem (Periyodik REST Polling):** 10 dakikaya kadar gecikme toleransı olan bir senaryoda 7/24 ayakta kalması gereken bir WebSocket istemcisi yerine periyodik REST polling (`POST /info`) en yalın ve maliyetsiz yaklaşımdır.
    *   [Hyperliquid WebSocket](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions) akışları canlı veri sağlar ancak sürekli açık sunucu (EC2/VPS vb.) gerektirir.
    *   Periyodik REST sorgusu sunucusuz (serverless) ortamlarda uykuya geçip sadece belirlenen aralıklarda tetiklenebilir.
*   **İstek Sınırları ve Ağırlık Hesabı:**
    *   Hyperliquid API'sinde IP başına dakikalık 1.200 ağırlık (weight) kotası bulunur ([Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits)).
    *   Cüzdanların açık pozisyonlarını ve hesap özetini dönen `clearinghouseState` sorgusunun ağırlığı 2 birimdir ([Hyperliquid Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)).
    *   20 cüzdanın tek seferde taranması `20 × 2 = 40` ağırlık puanı tüketir. Bu miktar, dakikalık 1.200 kotasının yalnızca %3,3'üne denk gelir; oran limitlerine (rate limit) takılma riski yoktur.
*   **GitHub Actions Schedule (Cron) Güvenilirliği:**
    *   GitHub Actions üzerindeki `schedule` (cron) tetikleyicileri, küresel runner kuyruğundaki yoğunluğa bağlı olarak 10 ila 60 dakikaya varan gecikmeler yaşayabilir ([GitHub Actions Schedule Docs](https://www.google.com/search?q=https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows%23schedule)).
    *   Azami 10 dakika gecikme şartı bulunan kritik takip sistemleri için yerleşik GitHub Actions cron zamanlaması güvenilir değildir. Ayrıca ücretsiz hesaplardaki 2.000 dakika/ay limiti, 10 dakikada bir çalışan işlerde hızla tükenebilir.
*   **Önerilen Ücretsiz Alternatif (Cloudflare Workers Cron Triggers):**
    *   [Cloudflare Workers Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/) ücretsiz planda günlük 100.000 istek hakkı sunar ([Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/)).
    *   5 veya 10 dakikada bir (ör. `*/5 * * * *` veya `*/10 * * * *`) sapmasız şekilde doğrudan edge ağında tetiklenir.
    *   Cüzdanların önceki durumları ile yeni durumlarını karşılaştırmak (delta tespiti) için ücretsiz [Cloudflare KV](https://developers.cloudflare.com/kv/) (günlük 1.000 yazma / 100.000 okuma) kullanılabilir. 20 cüzdan için günde 288 yazma kotanın oldukça altında kalır.

---

## 2. Telegram Botunda Sunucusuz Düğme Yönetimi ve Güvenlik

*   **`getUpdates` ile 10 Dakikada Bir Okumanın Sınırları:**
    *   **Zaman Aşımı ve Arayüz Donması:** Kullanıcı satır içi düğmeye (inline button) bastığında Telegram istemcisinde bir yükleme çarkı (spinner) döner. [Telegram Bot API](https://core.telegram.org/bots/api#answercallbackquery) standartlarına göre botun kısa süre içinde [answerCallbackQuery](https://core.telegram.org/bots/api#answercallbackquery) metodunu çağırması zorunludur. 10 dakika sonra çağrıldığında Telegram `400 Bad Request: query is too old and response timeout expired` hatası verir ve kullanıcının düğmesindeki yükleme animasyonu takılı kalır.
    *   **Kullanıcı Deneyimi:** Kullanıcının bastığı düğmenin cevabını veya güncellenen mesajı görmek için 10 dakikaya kadar beklemesi interaktif kullanımı imkansız hale getirir.
*   **Sunucusuz Webhook Alternatifi:**
    *   Sunucusuz ortamda (örneğin [Cloudflare Workers](https://developers.cloudflare.com/workers/) üzerinde) bir HTTP endpoint oluşturulup bot [setWebhook](https://core.telegram.org/bots/api#setwebhook) metoduyla bu adrese bağlanmalıdır.
    *   Kullanıcı düğmeye bastığı anda Telegram sunucuları Worker'a milisaniyeler içinde bir HTTP POST gönderir.
    *   Worker hemen `answerCallbackQuery` ve gerekiyorsa `editMessageText` yanıtı döner. Böylece sıfır sunucu maliyetiyle anlık geri bildirim sağlanır.
*   **Güvenlik:**
    *   **Secret Token Doğrulaması:** `setWebhook` kaydı yapılırken rastgele bir gizli anahtar tanımlanmalıdır ([Telegram Webhook Security](https://core.telegram.org/bots/api#setwebhook)). Worker'a gelen her istekte `X-Telegram-Bot-Api-Secret-Token` başlığı kontrol edilmeli, eşleşmeyen istekler reddedilmelidir.
    *   **Belirteç İzolasyonu:** Telegram Bot Token kod içine gömülmemeli, `wrangler secret` ile şifreli ortam değişkeni olarak saklanmalıdır.
    *   **IP / Yol Koruması:** Webhook yolu tahmin edilemeyen bir rota (ör. `/webhook-gizli-id`) olarak yapılandırılmalıdır.

---

## 3. Platform Analizi ve Mobil Arayüz Önerileri

### Mevcut Platformların Göstergeleri

| Platform | Temel Odak | Cüzdan Sayfasında Gösterilen Bilgiler | Sunum Tarzı |
| :--- | :--- | :--- | :--- |
| **[HypurrScan](https://hypurrscan.io/)** | On-Chain Explorer | Net hesap değeri, spot bakiyeler, margin durumu, açık pozisyonlar (coin, yön, büyüklük, giriş fiyatı, likidasyon fiyatı, PnL, kaldıraç), açık emirler/TWAP, fill geçmişi | Masaüstü odaklı geniş veri tabloları ve sekme gezintisi |
| **[Hyperdash](https://hyperdash.com/)** | Analitik & Terminal | Kümülatif PnL zaman serisi grafiği, gerçekleşmiş/gerçekleşmemiş PnL, kazanma oranı (win rate), pozisyon değişimleri (position changes), likidasyon ısı haritası risk göstergeleri | Görsel grafik ağırlıklı gösterge panelleri (widget/dashboard) |
| **[CoinGlass](https://www.coinglass.com/)** | Türev Veri & Leaderboard | 7g/30g ROI, kümülatif PnL, borsa bazlı açık pozisyonlar (long/short oranı, giriş/mark fiyatı, teminat, kaldıraç), geçmiş emirler | Sıralamalı liderlik kartları, filtreli listeler ve özet tablolar |

### Telefon Ekranı (Mobil UI) İçin Tasarım Fikirleri

*   **Dikey Kart Mimarisi:** Masaüstündeki geniş tablolar yerine mobilde her pozisyon için bağımsız, dikey kart bileşenleri kullanılmalıdır (ör. `SOL-PERP • 10x LONG • PnL: +$420 (+18%)`).
*   **Renkli Rozetler ve Görsel Hiyerarşi:** Yön (`LONG` için yeşil, `SHORT` için kırmızı) ve kaldıraç bilgisi kompakt rozetlerle (badge) en üstte konumlandırılmalı; anlık kâr/zarar tek bakışta seçilecek puntoda yazılmalıdır.
*   **Akordeon (Açılır-Kapanır) Detay Katmanı:** Kartın ilk görünümünde yalnızca Coin, Yön, Büyüklük ve PnL yer almalı; karta dokunulduğunda giriş fiyatı, likidasyon fiyatı, fonlama oranı ve marjin detayları açılmalıdır.
*   **Yapışkan (Sticky) Başlık Çubuğu:** Toplam portföy değeri, günlük net PnL ve açık pozisyon adedi sayfa aşağı kaydırılsa dahi ekranın üstünde sabit kalmalıdır.
*   **Telegram Mini App (TMA):** Telegram botu içinde metin blokları yerine [Telegram WebApps](https://core.telegram.org/bots/webapps) (`web_app` butonu) kullanılarak tek dokunuşla tam ekran açılan, parmak hareketleriyle yönetilebilen kompakt bir SPA (Single Page App) sunulmalıdır.
