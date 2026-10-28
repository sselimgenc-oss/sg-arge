> **Lider notu (2026-10-28):** Argon (Gemini) çıktısı, kullanıcı elle getirdi; görev `docs/GOREV_ARGON_ALTYAPI.md`.
> Kaynaklı değerler olduğu gibi alındı, lider ayrıca doğrulamadı. Kaynaksız/tahmini olanlar: GitHub zamanlama gecikmesi
> "15–60+ dk" (resmî sayı değil), §7'deki "döngü başına ortalama 15 aktif adres" varsayımı.
> Sonuç: Worker ücretsiz planı 300 adresi taşıyamaz (50 alt istek, 10 ms CPU, 5 cron); seçenekler Worker ücretli (5 $/ay) ya da
> küçük VPS. Karar kullanıcının (`docs/KARARLAR_D.md` K8). 1 dk mumlar yalnız ~3,5 gün geriye alınabiliyor → arşiv en az günde
> bir kez mum çekmeli.

# Hyperliquid Gölge İşlem (Shadow Trading) ve Arşivleme Kılavuzu

Bu doküman, Hyperliquid üzerinde ~300 trader adresinin kaldıraçlı işlemlerini "gölge" (sanal) olarak kopyalamak ve verilerini arşivlemek üzere gerekli API sınırlarını, sunucusuz (serverless) altyapı alternatiflerini ve maliyet analizlerini resmî dokümantasyon verilerine dayanarak özetler.

---

## 1. Hyperliquid Info API Sınırları ve İstek Ağırlıkları

Hyperliquid REST API'si, tüm `/info` ve takas istekleri için IP başına dakikalık paylaşımlı bir ağırlık havuzu kullanır.

| Parametre / Uç Nokta | Resmî Değer / Açıklama | Resmî Kaynak | Erişim Tarihi |
| :--- | :--- | :--- | :--- |
| **IP Başına İstek Ağırlığı Sınırı** | **1.200 ağırlık / dakika** (tüm REST istekleri paylaşımlı) | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| `clearinghouseState` | Ağırlık: **2** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| `l2Book` | Ağırlık: **2** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| `userFillsByTime` | **Temel ağırlık: 20** + yanıtta dönen **her 20 öğe başına +1 ek ağırlık** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| `userFunding` | **Temel ağırlık: 20** + yanıtta dönen **her 20 öğe başına +1 ek ağırlık** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| `candleSnapshot` | **Temel ağırlık: 20** + yanıtta dönen **her 60 öğe başına +1 ek ağırlık** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| `leaderboard` | **Resmî dokümanda doğrulanamadı.** `/info` altında tanımlı bir `leaderboard` endpoint'i bulunmamaktadır. Dokümante edilmiş diğer tüm info isteklerinin varsayılan ağırlığı 20'dir; ancak topluluk leaderboard verilerini `stats-data.hyperliquid.xyz/Mainnet/leaderboard` adresindeki harici stats servisinden çeker. | [Hyperliquid Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) | 28 Ekim 2026 |
| `userFillsByTime` En Çok Dolum ve Sayfalama | **Yanıt başına en fazla 2.000 dolum** döner ve sadece en güncel 10.000 dolum erişilebilirdir. Sayfalama `startTime` (dahil, milisaniye) ve `endTime` (dahil) parametreleriyle yapılır; daha geniş aralıklar için dönen son dolum zaman damgası bir sonraki sorgunun `startTime` değeri olarak kullanılır. | [Hyperliquid Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) | 28 Ekim 2026 |
| `candleSnapshot` En Çok Mum ve 1dk Geriye Gitme | Yanıtta **en fazla son 5.000 mum** döner. 1 dakikalık (`1m`) periyot seçildiğinde geriye dönük en fazla **5.000 dakika (~83 saat 20 dakika / ~3,47 gün)** geçmiş veriye erişilebilir. | [Hyperliquid Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) | 28 Ekim 2026 |

---

## 2. Hyperliquid WebSocket Sınırları

Gerçek zamanlı veri akışı sağlayan WebSocket bağlantıları için IP bazlı limitler uygulanır.

| Parametre / Özellik | Resmî Değer / Kural | Resmî Kaynak | Erişim Tarihi |
| :--- | :--- | :--- | :--- |
| **IP Başına Bağlantı Sınırı** | En fazla **10 eşzamanlı bağlantı** (ve dakikada en fazla 30 yeni bağlantı denemesi) | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| **IP Başına Toplam Abonelik** | En fazla **1.000 aktif abonelik** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| **Kullanıcıya Özel Abonelikler (`userFills`, `userEvents`)** | Tüm kullanıcıya özel aboneliklerde **IP başına en fazla 10 benzersiz kullanıcı (unique user)** izlenebilir. | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| **Mesaj Gönderme Hızı** | Tüm bağlantılar genelinde dakikada en fazla **2.000 mesaj** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |
| **Eşzamanlı Mesaj Limiti** | Tüm bağlantılar genelinde eşzamanlı en fazla **100 bekleyen (inflight) post mesajı** | [Hyperliquid Rate Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) | 28 Ekim 2026 |

---

## 3. Cloudflare Workers: Ücretsiz ve Ücretli Plan Karşılaştırması

| Özellik | Workers Free (Ücretsiz) | Workers Paid (Ücretli - Standard) | Resmî Kaynak | Erişim Tarihi |
| :--- | :--- | :--- | :--- | :--- |
| **Aylık Ücret** | $0 / ay | **$5 / ay** taban ücret (10M istek ve 30M CPU ms dahil; aşımda +$0,30/milyon istek, +$0,02/milyon CPU ms) | [Cloudflare Workers Pricing](https://developers.cloudflare.com/workers/platform/pricing/) | 28 Ekim 2026 |
| **Cron Trigger Sıklığı** | Standart POSIX cron (en sık **dakikada 1 kez**, `* * * * *`), hesap başına en fazla **5 Cron Trigger** | Standart POSIX cron (en sık **dakikada 1 kez**), hesap başına en fazla **250 Cron Trigger** | [Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) | 28 Ekim 2026 |
| **Alt İstek (Subrequest) Sınırı** | Çağrı başına **50 alt istek** (`fetch`, KV, R2 vb.) | Çağrı başına **10.000 alt istek** (yapılandırma ile 10 milyona kadar artırılabilir) | [Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) | 28 Ekim 2026 |
| **Eşzamanlı Açık Bağlantı** | İlk başlıkları bekleyen en fazla **6 eşzamanlı bağlantı** | İlk başlıkları bekleyen en fazla **6 eşzamanlı bağlantı** | [Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) | 28 Ekim 2026 |
| **CPU Süresi (Cron Trigger)** | Çağrı başına **10 ms** | < 1 saat aralıklı cron için **30 saniye**; ≥ 1 saat aralıklı cron için **15 dakika** | [Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) | 28 Ekim 2026 |
| **Günlük İstek Sınırı** | 100.000 istek / gün | Sınırsız (kullanıma göre faturalandırılır) | [Cloudflare Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) | 28 Ekim 2026 |

---

## 4. Cloudflare R2 Nesne Depolama Ücretleri

Cloudflare R2, AWS S3 uyumlu bir nesne depolama servisidir ve veri çıkış (egress) ücreti almaz.

| Kalem | Ücretsiz Katman (Free Tier - Aylık) | Standart Depolama Aşım Ücreti | Resmî Kaynak | Erişim Tarihi |
| :--- | :--- | :--- | :--- | :--- |
| **Depolama Alanı** | **10 GB-ay / ay** | **$0,015 / GB-ay** | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) | 28 Ekim 2026 |
| **Sınıf A İşlemler (Yazma / Listeleme)** | **1 milyon istek / ay** | **$4,50 / milyon istek** | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) | 28 Ekim 2026 |
| **Sınıf B İşlemler (Okuma)** | **10 milyon istek / ay** | **$0,36 / milyon istek** | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) | 28 Ekim 2026 |
| **Veri Alma İşleme (Retrieval)** | Ücretsiz ($0) | Ücretsiz ($0 / GB) | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) | 28 Ekim 2026 |
| **Çıkış Ücreti (Data Transfer / Egress)** | **Ücretsiz ($0 / GB)** | **Ücretsiz ($0 / GB)** | [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/) | 28 Ekim 2026 |

---

## 5. GitHub Actions (Herkese Açık Depolar)

| Parametre / Kural | Resmî Değer / Dokümante Edilen Limit | Resmî Kaynak | Erişim Tarihi |
| :--- | :--- | :--- | :--- |
| **En Sık Zamanlama Aralığı** | Resmî olarak desteklenen en kısa cron aralığı **5 dakikada 1 kezdir** (`*/5 * * * *`). | [GitHub Actions Events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) | 28 Ekim 2026 |
| **Gerçek Gecikme (Jitter / Delay)** | Resmî dokümantasyona göre, sistem genelindeki yüksek yük dönemlerinde (özellikle saat başlarında) **zamanlanmış işler gecikebilir ve aşırı yük altında kuyruktaki işler doğrudan iptal edilerek düşürülebilir (drop)**. Gerçek ortamda bu gecikmeler **15 ila 60+ dakikaya** çıkabilmektedir. | [GitHub Troubleshooting Workflows](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows) | 28 Ekim 2026 |
| **İş Süresi Sınırı (Job Timeout)** | GitHub tarafından barındırılan (GitHub-hosted) standart runner'larda iş başına en fazla **6 saat** | [GitHub Actions Limits](https://docs.github.com/en/actions/reference/limits) | 28 Ekim 2026 |
| **Eşzamanlı İş Sayısı (Concurrency)** | Standart GitHub-hosted runner'larda plana göre: Free: **20**, Pro: **40**, Team: **60**, Enterprise: **500** eşzamanlı iş. | [GitHub Actions Limits](https://docs.github.com/en/actions/reference/limits) | 28 Ekim 2026 |

---

## 6. Hyperliquid Komisyon Yapısı ve HIP-3 Piyasaları

Hyperliquid'de komisyonlar son 14 günlük ağırlıklı hacme ve stake edilen HYPE miktarına göre belirlenir.

| Kademe / Piyasa | Taker Komisyonu | Maker Komisyonu | Resmî Kaynak | Erişim Tarihi |
| :--- | :--- | :--- | :--- | :--- |
| **Temel Kademe (Tier 0 - Perps)** | **%0,045 (4,5 bps)** (14 günlük hacim < $5M, staking indirimi yokken) | %0,015 (1,5 bps) | [Hyperliquid Trading Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) | 28 Ekim 2026 |
| **Temel Kademe (Tier 0 - Spot)** | **%0,070 (7 bps)** | %0,040 (4 bps) | [Hyperliquid Trading Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) | 28 Ekim 2026 |
| **HIP-3 Piyasalarında Durum** | **Farklıdır:**<br>1. **Deployer Payı (Deployer Fee Scale):** Deployer %0-%300 arası ek ücret payı belirleyebilir; bu oran protokol taker ücretine çarpan olarak yansır (`scaleIfHip3`).<br>2. **Growth Mode (Büyüme Modu):** Deployer growth mode açarsa tüm komisyonlarda **≥%90 indirim** uygulanır; taban taker oranı **%0,0045 - %0,009 aralığına** (5-10 kat daha düşük) geriler.<br>3. **Uyumlu Teminat (Aligned Quote):** Uyumlu stablecoin teminatlarında taker komisyonu **%20 ek indirim** alır. | [Hyperliquid Trading Fees](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) | 28 Ekim 2026 |

---

## 7. 300 Adresi Her 5 Dakikada Bir Taramak: Fizibilite ve Mimari Çözüm

### 7.1. API Yükü ve Hız Sınırı (Rate Limit) Analizi

* **WebSocket İle İzleme:** Tek bir IP adresi üzerinden `userFills` veya `userEvents` ile **yalnızca 10 kullanıcı** izlenebilir. 300 adresi WebSocket ile izlemek için 30 farklı çıkış IP'si (proxy havuzu) gereklidir.
* **REST API İle Polling:**
  * **Hatalı Yaklaşım (`userFillsByTime` doğrudan çağırma):** Her istek 20 ağırlıktır. 300 adres × 20 = 6.000 ağırlık / 5 dk = **1.200 ağırlık / dakika**. Bu değer, izin verilen azami 1.200 sınırına eşittir. Tek bir dolum gerçekleştiğinde (+1 ek ağırlık) IP hız sınırına takılır.
  * **Optimum İki Aşamalı Yaklaşım (`clearinghouseState` + `userFillsByTime`):**
    * 1. Aşama: Her 5 dakikada 300 adresin tamamı için `clearinghouseState` (ağırlık 2) sorgulanır. Toplam yük: 300 × 2 = **600 ağırlık / 5 dk (120 ağırlık / dakika)**. Bu, IP limitinin sadece %10'udur.
    * 2. Aşama: Yalnızca bakiye, marjin veya açık pozisyon zaman damgası değişmiş olan aktif adresler filtrelenir (örneğin döngü başına ortalama 15 adres). Sadece bu adresler için `userFillsByTime` (ağırlık 20) çağrılır: 15 × 20 = 300 ağırlık.
    * **Ortalama Toplam Tüketim:** ~900 ağırlık / 5 dk = **180 ağırlık / dakika**. 1.200 sınırının oldukça altında, güvenli çalışma sağlar.

### 7.2. Altyapı Seçeneklerinin Değerlendirilmesi

1. **Cloudflare Workers (Free): MÜMKÜN DEĞİL.**
   * Çağrı başına alt istek sınırı 50'dir. Tek bir cron tetiklenmesinde 300 adrese istek atılamaz.
   * Hesap başına azami 5 cron trigger tanımlanabildiği için (5 × 50 = 250), parçalama ile dahi 300 adrese ulaşılamaz. Ayrıca 10 ms CPU süresi yanıt ayrıştırma için yetersizdir.

2. **GitHub Actions (Herkese Açık Repo): PRATİKTE MÜMKÜN DEĞİL.**
   * Sözdizimsel olarak `*/5 * * * *` tanımlanabilse de, GitHub zamanlayıcısındaki gecikmeler (jitter) 15-60 dakikayı bulabilir ve yüksek yük altında işler doğrudan atlanabilir. 5 dakikalık periyotlarla gölge işlem takibi yapamaz.

3. **Cloudflare Workers (Paid - $5/ay): MÜMKÜN VE HESAPLI (Önerilen Serverless Çözüm).**
   * **Alt İstek:** Çağrı başına 10.000 subrequest sınırı 300 adres için fazlasıyla yeterlidir.
   * **Bağlantı Kontrolü:** 6 eşzamanlı bağlantı sınırına dikkat edilerek istekler p-limit veya gruplama (batching) ile 15-20 saniyede tamamlanır.
   * **CPU Süresi:** 30 saniyelik CPU sınırı vardır (ağ beklemesi CPU'ya sayılmaz, JSON ayrıştırma ~30-50 ms sürer).
   * **Arşivleme:** Çekilen veriler tek bir JSON dosyası olarak Cloudflare R2'ye yazılır (ayda ~8.640 yazma işlemi, R2'nin 1 milyonluk ücretsiz sınırının altındadır).
   * **Maliyet:** **$5 / ay** (Workers Paid taban fiyatı, R2 maliyeti $0).

4. **Küçük Bir VPS / Dedicated Sunucu ($4 - $6/ay, örn. Hetzner, DigitalOcean): EN SAĞLAM ALTERNATİF.**
   * Sürekli çalışan bir Python veya Node.js arka plan süreci (daemon) kurulur.
   * İstekler 5 dakikalık pencereye yayılarak saniyede 1 istek (`1 req/sn`) hızında gönderilir (300 saniye = tam 300 adres).
   * Sıfır zamanlayıcı gecikmesi, kesin IP hız kontrolü ve R2'ye doğrudan S3 API ile veri yazma avantajı sağlar.
