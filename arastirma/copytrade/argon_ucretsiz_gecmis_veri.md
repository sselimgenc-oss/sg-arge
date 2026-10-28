> **Lider notu (2026-10-28):** En önemli bulgu Hugging Face `ProbioticFarmer/hyperliquid-augmented-copytrading`
> (iddia: Temmuz 2025'ten beri günlük `account_value`, ~460 bin adres). **Henüz doğrulanmadı:** rapordaki bağlantı bir Google
> arama yönlendirmesi, lider ortamından huggingface.co erişimi kapalı. Doğrulama: kullanıcı sayfayı tarayıcıda açar; varsa
> Codex Actions'ta bir tarih dosyasını okuyup satır/adres/sütun özetini çıkarır. Doğrulanırsa Faz 3 evreni buradan kurulur ve
> "iyimser üst sınır" etiketi kalkar. Tek başına `account_value` leaderboard PnL sıralaması değildir; sıralama için iki tarih
> arası değer farkı + `portfolio` geçmişi gerekir (para yatırma/çekme ayrımı yok, dikkat).

# Hyperliquid Copy Trade: Geçmiş Leaderboard ve Bakiye Veri Kaynakları Araştırması

## 1. Yönetici Özeti ve Problem Tanımı

Hyperliquid üzerinde karlı cüzdanları geriye dönük (backtest) analiz etmek ve kopyalama stratejileri (copy trading) geliştirmek için en kritik metodolojik zorluk **hayatta kalan yanlılığıdır (survivorship bias)**. 

Bugünkü liderlik tablosundaki (leaderboard) başarılı adresleri seçip geçmişe dönük simülasyon yapmak, o tarihte zirvede olup sonradan likidite olan veya tüm bakiyesini kaybeden hesapları göz ardı eder. Bu yanlılığı önlemek için, araştırmacıların geçmiş bir referans noktasındaki (örneğin 6 ay önceki) tam cüzdan evrenini, o tarihteki hesap büyüklüklerini (`account_value`) ve gerçekleşmiş/gerçekleşmemiş PnL değerlerini bilmesi şarttır.

Dune Analytics ve Nansen gibi ücretli kurumsal sağlayıcılar ile AWS faturalandırması gerektiren Hyperliquid S3 (requester-pays) kovası haricinde, **tamamen ücretsiz (kredi kartı gerektirmeyen)** açık veri kaynakları taranmış ve doğrulanmıştır.

---

## 2. Karşılaştırmalı Veri Kaynakları Matrisi

| Kaynak | Geçmiş Derinliği | Adres Kapsamı | Erişim Modeli | Ücretsiz Sınırı | Doğrulandı mı? | Bağlantı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hugging Face (`ProbioticFarmer`)** | Temmuz 2025 – Günümüz (390+ günlük Parquet) | ~460.000 cüzdan (Tüm aktif taban) | Parquet dosyaları, Hugging Face Hub / DuckDB streaming | Tamamen Açık (Kartsız, sınırsız indirme/sorgulama) | **Evet** | [Hugging Face Repo](https://www.google.com/search?q=https://huggingface.co/datasets/ProbioticFarmer/hyperliquid-augmented-copytrading) |
| **Hyperliquid Stats JSON** | Yalnızca ANLIK (anlık snapshot) | ~1.000 – 3.000 sıralı cüzdan | Doğrudan HTTP GET (JSON) | Ücretsiz / API anahtarı gerekmez | **Evet** | [Stats Leaderboard JSON](https://stats-data.hyperliquid.xyz/Mainnet/leaderboard) |
| **Hyperliquid Info API (`portfolio`)** | Tüm geçmiş (~1+ yıl, haftalık PnL noktaları) | Tekil adres sorgusu (Herhangi bir cüzdan) | REST POST API (`/info`) | Ücretsiz (IP limiti: ~1.200 ağırlık/dk) | **Evet** | [Hyperliquid Info API Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) |
| **HypurrScan** | Cüzdan bazlı işlem geçmişi (tüm zamanlar) | Tüm adresler | Web arayüzü + Swagger API | Ücretsiz (1.000 req/dk IP limiti) | **Evet (Tarihsel snapshot yok)** | [HypurrScan API UI](https://api.hypurrscan.io/ui/) |
| **HyperDash** | Canlı / cari dönem sıralamaları ve cüzdan geçmişi | İlk 100+ ve aranan cüzdanlar | Web arayüzü (Kurumsal sentry API) | Kısmen (Web ücretsiz, toplu API kapalı) | **Evet (Tarihsel snapshot yok)** | [Hyperdash Leaderboard](https://hyperdash.com/leaderboard) |
| **Allium** | Mart 2025 – Günümüz (DEX trades) | Tüm DEX cüzdanları | SQL / REST API | 20.000 kredi ücretsiz (Kartsız deneme, sonrası ücretli) | **Evet (Hazır snapshot tablosu yok)** | [Allium Hyperliquid Docs](https://docs.allium.so/historical-data/supported-blockchains/hyperliquid/overview) |
| **Goldsky** | Genesis'ten bu yana ham HyperCore L1 verisi | Tüm bloklar / olaylar | Subgraph / Mirror Pipeline | $100 deneme kredisi (Kartsız, ham veri) | **Evet (Hazır leaderboard yok)** | [Goldsky Hyperliquid](https://goldsky.com/chains/hyperliquid) |
| **Artemis** | 1+ yıl (Protokol makro metrikleri) | Yok (Yalnızca protokol geneli) | Web / API | Freemium | **Evet (Cüzdan verisi yok)** | [Artemis Research](https://about.artemis.ai/) |
| **ASXN Data** | 1+ yıl (Makro hacim, OI, fonlama) | Yok (Yalnızca ekosistem geneli) | Web dashboard | Ücretsiz | **Evet (Cüzdan verisi yok)** | [ASXN Dashboard](https://data.asxn.xyz/dashboard/hyperliquid-ecosystem) |
| **Flipside Crypto** | Yalnızca Arbitrum köprüsü / EVM tarafı | Sınırlı (HyperCore L1 defteri yok) | SQL Studio | Ücretsiz | **Evet (L1 Perp verisi yok)** | [Flipside Crypto](https://flipsidecrypto.xyz/) |
| **Kaggle (`marvingozo`)** | 5 gün (Mayıs 2026 mikro yapı) | 10 piyasa / işlem yapan cüzdanlar | Parquet indirme | Tamamen ücretsiz | **Evet (6 ay öncesi bakiye yok)** | [Kaggle Hyperliquid Dataset](https://www.kaggle.com/datasets/marvingozo/hyperliquid-l1-order-flow-microstructure-10-perps) |

---

## 3. Doğrulanan En İyi Çözümler ve Uygulama Rehberi

### Öneri 1 (Birincil Kaynak): Hugging Face `ProbioticFarmer/hyperliquid-augmented-copytrading`

Bu veri seti, doğrudan kopya ticaret araştırmalarında **hayatta kalan yanlılığını gidermek** amacıyla yayınlanmıştır.

* **Dizin Yapısı:** Veri seti içerisinde `account_values/date=YYYY-MM-DD/` şeklinde bölümlenmiş Parquet dosyaları yer alır (391 dosya, 18.12 GB).
* **Veri Alanları:** Cüzdan adresi (`user`), anlık toplam özkaynak (`account_value`), pozisyon marjinleri ve ilgili tarih damgaları.
* **Kapsam:** Yaklaşık 460.000 tekil cüzdan.
* **Kullanım Yöntemi:** Tüm veri setini indirmeden, DuckDB'nin HTTPFS veya Hugging Face entegrasyonu sayesinde doğrudan buluttan sorgulanabilir.

#### Örnek Python & DuckDB Kodu:
```python
import duckdb

# DuckDB bağlantısı oluştur
con = duckdb.connect()

# 6 ay öncesine ait belirli bir tarihin (ör. 2025-08-09) en yüksek bakiyeli ilk 100 cüzdanı
query = """
SELECT 
    user AS wallet_address, 
    account_value AS equity_usd
FROM 'hf://datasets/ProbioticFarmer/hyperliquid-augmented-copytrading/account_values/date=2025-08-09/*.parquet'
WHERE account_value > 10000
ORDER BY account_value DESC 
LIMIT 100;
"""

top_traders_then = con.execute(query).df()
print(top_traders_then.head(10))
```

---

### Öneri 2 (Tamamlayıcı / Canlı Doğrulama): Hyperliquid Resmi API'leri

Hugging Face üzerindeki tarihsel listeden seçilen cüzdanların performansını resmi düğümlerden teyit etmek için Hyperliquid'in iki ücretsiz uç noktası kullanılabilir:

#### A. Güncel Liderlik Tablosu (Stats Feed)
Hyperliquid web uygulamasının leaderboard ekranı doğrudan bu JSON dosyasını okur:
* **Uç Nokta:** `GET https://stats-data.hyperliquid.xyz/Mainnet/leaderboard`
* **İçerik:** `ethAddress`, `accountValue`, `windowPerformances` (günlük, haftalık, aylık, tüm zamanlar PnL, ROI, hacim).
* **Örnek Çağrı:**
  ```bash
  curl -s https://stats-data.hyperliquid.xyz/Mainnet/leaderboard | jq '.leaderboardRows[:5]'
  ```

#### B. Tekil Cüzdan Geçmiş PnL Eğrisi (`portfolio`)
Geçmiş bir tarihten seçtiğiniz herhangi bir cüzdan adresinin tüm zamanlar haftalık PnL geçmişini çeker:
* **Uç Nokta:** `POST https://api.hyperliquid.xyz/info`
* **Gövde:** `{"type": "portfolio", "user": "0x5b5d51203a0f9079f8aeb098a6523a13f298c060"}`
* **Örnek Çağrı:**
  ```bash
  curl -X POST https://api.hyperliquid.xyz/info \
    -H "Content-Type: application/json" \
    -d '{"type": "portfolio", "user": "0x5b5d51203a0f9079f8aeb098a6523a13f298c060"}'
  ```
* **Dönen Veri:** `perpAllTime.pnlHistory` dizisi içinde `[timestamp_ms, pnl_usd]` ikilileri döner. Bu veriden geriye dönük 6 aylık delta PnL doğrudan hesaplanabilir.

---

## 4. İncelenen Diğer Kaynakların Durumu

1. **HypurrScan (`hypurrscan.io`):** Popüler bir blok kaşifidir. Bireysel adreslerin emir ve dolum (fill) geçmişini CSV olarak dışa aktarır. Ancak geçmiş bir tarihteki genel liderlik tablosu sıralamasını toplu olarak sunan bir uç noktası yoktur.
2. **HyperDash (`hyperdash.com`):** Profesyonel bir arayüzdür. Trader profillerinde geçmiş metrikleri sunar, fakat tarihsel toplu veri çekmeye izin veren açık bir REST/GraphQL API sağlamaz.
3. **Allium (`allium.so`):** Hyperliquid L1 işlemlerini doğrudan indekslemektedir. Kredi kartı gerektirmeyen 20.000 kredilik bir ücretsiz katmanı mevcuttur; ancak hazır bir "historical leaderboard snapshot" tablosu sunmadığından, trade loglarından cüzdan bakiyelerini sıfırdan yeniden inşa etmek gerekir.
4. **Goldsky (`goldsky.com`):** HyperCore L1 için $100 ücretsiz deneme kredisi sunar; ancak sağladığı veri ham blok/eylem verisidir.
5. **Flipside Crypto:** Hyperliquid'in tescilli L1 Tendermint defterini doğrudan indekslememektedir.
6. **Artemis & ASXN:** Yalnızca protokol düzeyinde kümülatif hacim, açık pozisyon ve gelirleri gösteren makro gösterge panelleridir; cüzdan düzeyinde veri içermezler.
7. **Kaggle:** Yalnızca 5 günlük L1 emir akışı mikro yapı verisi içermektedir (Mayıs 2026). 6 ay öncesine ait bakiye/PnL sıralaması barındırmaz.

---

## 5. Önerilen Araştırma Boru Hattı

1. **Adım 1 (Evren Tespiti):** Hugging Face `ProbioticFarmer/hyperliquid-augmented-copytrading` veri setinden incelemek istediğiniz referans tarihine (ör. `date=2025-08-01`) ait `account_values` Parquet dosyasını DuckDB ile çekin.
2. **Adım 2 (Sıralama ve Filtreleme):** İlgili gündeki `account_value` değerine göre ilk N cüzdanı belirleyin. HLP ve vault adreslerini (`stats-data.hyperliquid.xyz/Mainnet/vaults`) eleyerek bireysel trader havuzunu oluşturun.
3. **Adım 3 (İleriye Dönük Takip):** Belirlenen bu cüzdanların sonraki aylardaki (`2025-09-01`, `2025-10-01` vb.) bakiyelerini yine veri setindeki sonraki tarihlerden veya Hyperliquid'in canlı `portfolio` API'sinden çekerek stratejinizin hayatta kalma ve getiri oranını test edin.
