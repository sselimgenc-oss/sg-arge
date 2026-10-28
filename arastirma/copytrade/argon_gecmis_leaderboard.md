> **Lider notu (2026-10-28):** Argon (Gemini) çıktısı. Doğrulanmadı; özellikle Dune tablolarının ücretsiz erişimi ("kısmi gated")
> ve tarih başlangıçları ilk sorguda sınanmalı. Faz 3 (geçmiş prova) için tercih sırası: (1) Dune `hyperliquid.perp_accounts_daily`
> ile T günü ilk N adres (ücretsiz ise), (2) Hyperliquid S3 ham veri (requester-pays, AWS hesabı ve ~GB başına ücret; kullanıcı
> kararı), (3) Nansen (ücretli). Hiçbiri yoksa bugünkü evren, sonuç "iyimser üst sınır" diye raporlanır (`GOREV_GOLGE.md`).

# Hyperliquid Geçmiş Tarihli Leaderboard (Sıralama) Verisi ve Hayatta Kalan Yanlılığı (Survivorship Bias) Araştırması

Bu doküman, Hyperliquid üzerinde geriye dönük testlerde (backtesting) **hayatta kalan yanlılığını (survivorship bias)** engellemek —yani 6 veya 12 ay önceki bir tarihte sıralamada olup sonradan batan, tasfiye olan veya bakiyesini çekerek listeden silinen trader'ları tespit etmek— amacıyla geçmiş tarihli anlık sıralama (point-in-time leaderboard snapshot) verilerine erişim imkânlarını ve ham zincir verisinden liderlik tablosunu yeniden inşa etme yöntemlerini kapsamaktadır.

---

## 1. Problem Tanımı: Hayatta Kalan Yanlılığı (Survivorship Bias)

Geriye dönük testlerde bugünün liderlik tablosunu (leaderboard) baz alıp geriye doğru bakmak yanıltıcıdır:
* **Hata:** Bugün listede olan adreslerin 6 ay önceki performansına bakmak, yalnızca bugüne kadar batmamış "kazananları" filtreler.
* **Doğru Yaklaşım:** 6 veya 12 ay önceki $T$ gününde listede ilk 100 veya 300'de yer alan trader havuzunu çekmek, bu havuzun sonraki 6-12 ayda ne yaptığını incelemektir. Bu sayede stratejinin gerçek hayattaki yıpranma (drawdown) ve batış oranları (ruin probability) gerçeğe uygun şekilde test edilebilir.

---

## 2. Potansiyel Veri Kaynaklarının Detaylı Analizi

### 2.1. Hyperliquid Resmî Stats Servisi (`stats-data.hyperliquid.xyz/Mainnet/leaderboard`)
* **(a) Ne Veriyor:** Sıralamadaki tüm cüzdanların listesi (`ethAddress`), hesap değeri (`accountValue`), takma adı (`displayName`) ve `day`, `week`, `month`, `allTime` pencereleri için `pnl`, `roi`, `vlm` verileri.
* **(b) Ne Kadar Geriye Gidiyor:** **Geçmiş tutmuyor.** Yalnızca o anki canlı durumu (rolling windows) yansıtan statik bir JSON dosyasıdır. Tarih parametresi veya geçmiş arşiv dizini yoktur.
* **(c) Erişim Yolu:** Doğrudan HTTP GET ([https://stats-data.hyperliquid.xyz/Mainnet/leaderboard](https://www.google.com/search?q=https://stats-data.hyperliquid.xyz/Mainnet/leaderboard)).
* **(d) Ücret ve Şartlar:** Tamamen ücretsiz, API anahtarı gerekmez.
* **(e) Güvenilirlik:** Resmî Hyperliquid arayüzünün doğrudan beslendiği kaynaktır; ancak **noktasal geçmiş veri sunmaz**. Ayrıca vault adresleri ve bireysel trader'lar aynı listededir ([vaults](https://www.google.com/search?q=https://stats-data.hyperliquid.xyz/Mainnet/vaults) ile ayıklanmalıdır).

---

### 2.2. Nansen API (`POST /api/v1/perp-leaderboard`)
* **(a) Ne Veriyor:** Belirli bir tarih aralığı için en kârlı trader adresleri (`trader_address`), etiketleri (`trader_address_label`: Smart Money vb.), `total_pnl`, `realized_pnl_usd`, `unrealized_pnl_usd`, `roi`, `volume_usd`, işlem adedi (`total_trades`), en büyük 5 açık pozisyonu ve `account_value`.
* **(b) Ne Kadar Geriye Gidiyor:** Resmî dokümantasyonuna göre **Mayıs 2025'ten itibaren** güvenilir geçmiş sunmaktadır (6 ay ve 12 ay öncesi sorgulanabilir).
* **(c) Erişim Yolu:** REST API ([`Nansen Hyperliquid Leaderboard API`](https://docs.nansen.ai/api/hyperliquid/hyperliquid-leaderboard)). İstekte `date: {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}` parametresi gönderilir.
* **(d) Ücret ve Şartlar:** Ücretli abonelik / API kredisi gerektirir (ücretsiz kademede standart etiketler döner, premium etiketler çağrı başına 150 kredi harcar).
* **(e) Güvenilirlik:** **Çok yüksek.** Hyperliquid perp işlemlerini L1 düzeyinde işleyip doğrudan tarih parametreli sıralama sunan en olgun hazır API'dir.

---

### 2.3. Dune Analytics (`hyperliquid.perp_*` ve `hyperliquid.node_fills_decoded`)
* **(a) Ne Veriyor:** Günlük hesap bazlı PnL, hacim, teminat ve funding hareketleri ([`hyperliquid.perp_accounts_daily`](https://docs.dune.com/data-catalog/community/hyperliquid/overview)), saatlik pozisyonlar (`perp_positions_hourly`) ve tekil dolumlar (`node_fills_decoded`).
* **(b) Ne Kadar Geriye Gidiyor:** Resmî Dune dokümanına göre işlem dolumları **27 Temmuz 2025'ten**, funding verileri **27 Eylül 2025'ten** itibaren mevcuttur. Daha eski tarihler topluluk tablolarında kısmi/eksiktir.
* **(c) Erişim Yolu:** Dune SQL arayüzü, Dune API veya sorgu sonucunu CSV olarak indirme.
* **(d) Ücret ve Şartlar:** Temel sorgular ücretsiz plana açıktır; ancak `hyperliquid.perp_*` küratörlü tablolarının bir kısmı kurumsal/özel veri paketi (gated dataset) kapsamındadır.
* **(e) Güvenilirlik:** **Çok yüksek.** Ham blok akışını SQL ile istenen geçmiş tarihe göre (`WHERE date = '2025-10-28' ORDER BY cumulative_pnl DESC`) sorgulama esnekliği sağlar.

---

### 2.4. Allium (`hyperliquid.raw.fills` ve PnL Veri Modelleri)
* **(a) Ne Veriyor:** Dolum seviyesi (`fills`), işlem seviyesi (`trades`), kullanıcı bazlı gerçekleşen PnL, kümülatif hacim ve tasfiyeler ([`Allium Hyperliquid PnL & Trades`](https://docs.allium.so/historical-data/supported-blockchains/hyperliquid/dex/trades)).
* **(b) Ne Kadar Geriye Gidiyor:** **Mart 2025 sonrasındaki tüm işlemler eksiksizdir.** Mart 2025 öncesi dönemde ise >10.000 işlem yapmış yaklaşık 4.000 yüksek frekanslı adres hariç tüm cüzdanlar geriye dönük işlenmiştir.
* **(c) Erişim Yolu:** SQL sorgusu (Snowflake / BigQuery entegrasyonu), REST API veya Allium Beam akışları.
* **(d) Ücret ve Şartlar:** Kurumsal ücretli B2B veri sağlayıcısı.
* **(e) Güvenilirlik:** **En yüksek.** Hyperliquid altyapı sağlayıcısı GoldRush ve Allium doğrudan doğrulayıcı blok akışından beslenir.

---

### 2.5. Hyperliquid Resmî AWS S3 Veri Deposu (`s3://hl-mainnet-node-data/`)
* **(a) Ne Veriyor:** Blok bazlı tüm işlem dolumları (`node_fills_by_block`), takas dışı tüm olaylar (`misc_events_by_block`: funding, transfer, staking), L2 derinlik anlık görüntüleri (`s3://hyperliquid-archive/market_data`) ve oracle/mark fiyatları (`asset_ctxs`).
* **(b) Ne Kadar Geriye Gidiyor:** Mainnet başlangıcından (Mayıs 2023) günümüze kadar **tüm blok geçmişi eksiksiz** mevcuttur.
* **(c) Erişim Yolu:** AWS CLI / S3 API ([`Hyperliquid Historical Data Docs`](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data)).
* **(d) Ücret ve Şartlar:** Veri tabanı erişimi ücretsizdir; ancak AWS veri transfer maliyeti indiren tarafa aittir (`--request-payer requester`, yaklaşık ~$0,09/GB transfer).
* **(e) Güvenilirlik:** **%100 Zemin Gerçeği (Ground Truth).** Üçüncü taraf aracı olmadan doğrudan protokolün ham blok kayıtlarıdır.

---

### 2.6. Hyperdash, Hypurrscan, ASXN, Coinglass ve Artemis
* **Hyperdash ([`hyperdash.com`](https://hyperdash.com/)):** Canlı trader skorlama ve 7g/30g/90g pencereleri sunar; belirli bir geçmiş günün sıralama anlık arşivini dışa aktaran bir API/servisi **bulunmamaktadır (doğrulanamadı)**.
* **Hypurrscan ([`hypurrscan.io`](https://hypurrscan.io/)):** Blok gezginidir; işlem ve blok detaylarını gösterir, ancak tarihsel trader PnL sıralaması servisi **yoktur**.
* **ASXN ([`hyperscreener.asxn.xyz`](https://hyperscreener.asxn.xyz/)):** Makro metrikler, açık faiz (OI) ve vault TVL analizleri sunar; tarihsel cüzdan sıralaması dökümü **bulunmamaktadır (doğrulanamadı)**.
* **Coinglass ([`coinglass.com`](https://www.coinglass.com/hyperliquid)):** Canlı balina takipçisi (Whale Tracker) ve anlık pozisyonları gösterir; geçmişe dönük PnL sıralama arşivi **sunmaz**.
* **Artemis ([`artemis.xyz`](https://about.artemis.ai/research)):** Yalnızca protokol düzeyinde temel metrikleri (günlük hacim, ücretler, aktif kullanıcı sayısı) takip eder; adres bazında geçmiş kârlılık listesi **vermez**.

---

### 2.7. Wayback Machine (archive.org) ve Açık Kaynak GitHub Projeleri
* **Wayback Machine:**
  * `app.hyperliquid.xyz/leaderboard`: İstemci taraflı (CSR / React) çalışan bir web uygulamasıdır. Wayback Machine sayfayı kazıdığında yalnızca boş HTML kabuğunu (`div id="root"`) kaydeder; arka planda çekilen dinamik sıralama verilerini çalıştırmaz ve saklamaz.
  * `stats-data.hyperliquid.xyz/Mainnet/leaderboard`: Ham JSON uç noktası Wayback Machine üzerinde sistematik/günlük olarak arşivlenmemiştir; tesadüfi birkaç enstantane dışında 6-12 aylık düzenli veri **elde edilemez**.
* **GitHub Projeleri:**
  * [`jadeapricot27/Hyperliquid-Leaderboard-Analytics`](https://github.com/jadeapricot27/Hyperliquid-Leaderboard-Analytics): Leaderboard verilerini analiz etmek için açık kaynaklı bir Python aracıdır; ancak geçmiş arşiv barındırmaz, kullanıcının o günden itibaren veriyi yerel diske/veritabanına kaydetmesi esasına dayanır.
  * [`bford21/hl-twap-api`](https://github.com/bford21/hl-twap-api): Hyperliquid S3 ham işlem verilerini indirip PostgreSQL'e yükleyen açık kaynak bir veri boru hattı (pipeline) örneğidir.

---

## 3. Ham Dolum Geçmişinden Geçmiş Leaderboard'u Sıfırdan Yeniden Kurmak

**Evet, deterministik olarak mümkündür; ancak yüksek veri işleme gücü ve altyapı gerektirir.**

### 3.1. Gerekli Veri Bileşenleri
1. **İşlem Dolumları:** `s3://hl-mainnet-node-data/node_fills_by_block` (her bir blokta gerçekleşen alış/satış fiyatı, miktarı, yönü, komisyonu ve realized PnL).
2. **Fonlama ve Bakiye Olayları:** `s3://hl-mainnet-node-data/misc_events_by_block` (saatlik funding ödemeleri, yatırma/çekme transferleri ve tasfiyeler).
3. **Piyasa Fiyatları:** `s3://hyperliquid-archive/asset_ctxs/` (belirli bir $T$ gününün kapanışında açık kalan pozisyonların unrealized PnL'ini ve hesap değerini hesaplamak için mark price verisi).

### 3.2. Veri Boyutu ve Hesaplama Karmaşıklığı
* **Ham Veri Boyutu:** Hyperliquid kümülatif olarak yüz milyonlarca dolum üretmiştir. S3'teki LZ4 sıkıştırmalı blok verileri son 12 ay için yaklaşık **250 GB – 600 GB** aralığındadır. Bu veri açılıp ilişkisel/sütun tabanlı tabloya dönüştürüldüğünde (Parquet/ClickHouse) **1,5 TB – 3+ TB** disk alanı kaplar.
* **Hesaplama:** Belirli bir $T$ tarihi (örneğin 28 Ekim 2025) için her adresin kümülatif realized kârı, ödediği/aldığı funding'ler ve o anki açık pozisyonlarının değeri toplanarak liderlik tablosu üretilir. Bu işlem ev tipi bir bilgisayarda değil; **ClickHouse, DuckDB veya AWS Athena / Spark** üzerinde çalıştırılmalıdır.

---

## 4. Kaynak Karşılaştırma Matrisi

| Kaynak / Platform | Sağlanan Veri Alanları | Tarihsel Kapsam | Erişim Formatı | Ücret Durumu | Güvenilirlik | Kaynak Bağlantısı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Nansen API** | Adres, Toplam PnL, Realized/Unrealized, ROI, Bakiye, İşlem Sayısı | **Mayıs 2025 → Günümüz** (İstenen tarih aralığı) | REST API (JSON) | Ücretli (API Kredisi) | **Çok Yüksek** | [Nansen API Docs](https://docs.nansen.ai/api/hyperliquid/hyperliquid-leaderboard) (28 Ekim 2026) |
| **Dune Analytics** | Günlük cüzdan PnL, hacim, bakiye, saatlik pozisyonlar, tekil dolumlar | **Temmuz/Eylül 2025 → Günümüz** | SQL / CSV İndirme / API | Ücretsiz/Ücretli (Kısmi Gated) | **Çok Yüksek** | [Dune Docs](https://docs.dune.com/data-catalog/community/hyperliquid/overview) (28 Ekim 2026) |
| **Hyperliquid S3** | Tüm ham dolumlar, funding'ler, transferler, blok olayları, L2 derinlik | **Mayıs 2023 → Günümüz** (Tam Geçmiş) | AWS S3 CLI (`lz4`/ikili) | Ücretsiz erişim (AWS Transfer Ücreti) | **%100 (Ground Truth)** | [Hyperliquid Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/historical-data) (28 Ekim 2026) |
| **Allium** | Dolum ve kullanıcı düzeyinde PnL, cüzdan geçmişi, hacim | **Mart 2025 → Günümüz** (Öncesi kısmi) | SQL (Snowflake/BQ) / API | Ücretli (Kurumsal B2B) | **Çok Yüksek** | [Allium Docs](https://docs.allium.so/historical-data/supported-blockchains/hyperliquid/dex/trades) (28 Ekim 2026) |
| **HL Stats Servisi** | Anlık adres, bakiye, PnL, ROI, hacim (`day`, `week`, `month`, `allTime`) | **Yalnızca Canlı Anlık Durum** (Geçmiş yok) | HTTP GET (JSON) | Ücretsiz | Yüksek (Ancak geçmiş yok) | [Stats Data](https://www.google.com/search?q=https://stats-data.hyperliquid.xyz/Mainnet/leaderboard) (28 Ekim 2026) |
| **Wayback Machine** | Yok (Sadece boş SPA HTML kabuğu kaydedilmiş) | Düzensiz / Kullanışsız | Web UI | Ücretsiz | **Düşük / Yetersiz** | [Archive.org](https://web.archive.org) (28 Ekim 2026) |
| **Hyperdash / ASXN** | Canlı metrikler, rolling pencereler (7g/30g/90g) | Geçmiş gün dökümü **yok (doğrulanamadı)** | Web Dashboard | Ücretsiz | Yetersiz (Snapshot yok) | [Hyperdash](https://hyperdash.com/) (28 Ekim 2026) |

---

## 5. Hayatta Kalan Yanlılığını Azaltmak İçin "En Uygulanabilir 2 Yol"

### 1. En Hızlı ve Zahmetsiz Yol: Nansen Perp Leaderboard API
* **Neden:** Kendi büyük veri altyapınızı kurmadan, yüzlerce gigabaytlık veri indirmeden ve karmaşık PnL muhasebesi yapmadan tek bir API çağrısıyla geçmiş snapshot verir.
* **Nasıl Uygulanır:** `https://api.nansen.ai/api/v1/perp-leaderboard` uç noktasına hedeflediğiniz geçmiş tarih parametresi (örneğin 6 ay öncesi için `{"from": "2026-04-28", "to": "2026-04-28"}`) gönderilir. O günün en kârlı cüzdan listesi, PnL ve hesap değerleriyle doğrudan çekilir. Bu liste bugünkü güncel liste ile kıyaslanarak aradan geçen sürede batan, bakiyesini çeken veya listeden düşen cüzdanlar filtrelenir.

### 2. En Bağımsız ve Maliyetsiz Yol: Dune Analytics SQL Sorgusu (veya S3 + DuckDB)
* **Neden:** Üçüncü taraf kapalı API aboneliklerine bağımlı kalmadan, doğrudan SQL esnekliğiyle geriye dönük sorgu çalıştırma imkânı sunar.
* **Nasıl Uygulanır:**
  * Dune Analytics üzerinde `hyperliquid.perp_accounts_daily` tablosu kullanılarak, 6 veya 12 ay önceki tarihte kümülatif kârı en yüksek olan ilk 500 cüzdan listelenir (`SELECT address, cumulative_pnl, balance FROM hyperliquid.perp_accounts_daily WHERE date = '2025-10-28' ORDER BY cumulative_pnl DESC LIMIT 500`).
  * Elde edilen geçmiş cüzdan kümesi, Hyperliquid'in bugünkü güncel `/info` (`portfolio` veya `clearinghouseState`) uç noktalarıyla taranır. Geçmişte tepeye oynayıp bugün bakiyesi sıfırlanmış olanlar ayıklanarak geriye dönük test modelinin gerçekçiliği doğrulanır.
