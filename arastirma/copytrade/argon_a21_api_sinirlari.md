> **Lider denetim notu (2026-10-29):** Argon A21. Kaynaklar lider tarafından açılamadı (ağ kapalı); "doğrulanamadı" etiketleri
> Argon'un. Pilot için sonuç: arşiv 2026-10-29 12:24Z'de ilk kez yeşil koştu, t0 aynı gün → ölçüm penceresinde dolum boşluğu yalnız
> saatler; `userFillsByTime` (son 10.000 dolum) ile geri alınabilir. Günde ~1.500+ dolumlu adreslerde bir haftayı aşan boşluk
> geri alınamaz → arşiv kesintisi > 1 gün sürerse alarm gerekir (`GOREV_PILOT_VERI` §1 ile birlikte değerlendirilir).
> İstek bütçesi (1.200 ağırlık/dk) ve funding'in saatlik sorgulanması `arsiv.py` ile karşılaştırılmalı. Alt hesap uyarısı
> bayrak hesabındaki "alt hesapta ters" sütunuyla kısmen karşılanıyor; arşivde alt hesap dolumları ayrıca toplanmıyor.

# Hyperliquid Halka Açık API Geçmiş Veri Arşivleme ve Boşluk Doldurma Kılavuzu (A21)

**Erişim Tarihi:** 29 Ekim 2026  
**Bağlam:** `https://api.hyperliquid.xyz/info` (anahtarsız / public REST) uç noktası üzerinden ~200 adresin `userFills`, `userFunding` ve saatlik `candleSnapshot` verilerini 15 dakikada bir arşivleyen bir sistemde oluşan birkaç saatlik / haftalık veri boşluklarının geriye dönük telafisi ve hız sınırları optimizasyonu.

---

## 1. `userFills` ve `userFillsByTime` Analizi

### Kayıt Sayısı, Geçmiş Derinliği ve Sayfalama
* **`userFills` Uç Noktası:**
  * **Kayıt Sınırı:** Tek istekte en fazla en güncel **2.000 dolum (fills)** döner.
  * **Filtreleme:** Zaman aralığı parametresi kabul etmez; yalnızca en son dolumları verir.
* **`userFillsByTime` Uç Noktası:**
  * **Kayıt Sınırı:** İstek başına en fazla **2.000 dolum** döner (`200: OK Number of fills is limited to 2000`).
  * **Geçmiş Derinliği Sınırı:** Resmî belgede açıkça belirtildiği üzere: **"only the 10000 most recent fills are available"** (yalnızca en son 10.000 dolum erişilebilirdir).
  * **İstek Gövdesi:**
    ```json
    {
      "type": "userFillsByTime",
      "user": "0x...",
      "startTime": 1730000000000,
      "endTime": 1730050000000,
      "aggregateByTime": false
    }
    ```
  * **Sayfalama (Pagination):** Eğer sorgulanan zaman aralığında 2.000'den fazla dolum varsa, dönen listenin son elemanındaki `time` (milisaniye) değeri alınır ve bir sonraki isteğin `startTime` parametresi olarak atanır. *(Dikkat: `startTime` kapsayıcı olduğundan mükerrer kayıtları önlemek için istemci tarafında `tid`/`oid` bazında tekilleştirme yapılmalıdır).*

### Günde 1.000+ Dolum Yapan Çok Aktif Bir Adreste 1 Haftalık Boşluk Geri Alınabilir mi?
* **Şartlı Olarak Evet / Kritik Uyarı:**
  * Adres günde tam 1.000 dolum yapıyorsa 7 günlük toplam dolum sayısı $\approx 7.000$'dir. 7.000 kayıt, Hyperliquid'in koyduğu 10.000'lik tavanın altında kaldığından **sayfalama yapılarak (~4 istekte) eksiksiz kurtarılabilir**.
  * **Risk:** Eğer adres günde 1.500+ dolum yapıyorsa (haftalık >10.500 dolum) veya aradan geçen sürede adres yeni işlemler yaparak boşluğun başlangıcını son 10.000 işlem penceresinin dışına ittiyse, 10.000'den daha eski kayıtlar halka açık REST API üzerinden **geri getirilemez**. Bu durumda tek çözüm Hyperliquid'in resmî genel S3 veri arşivinden (`hyperliquid-archive`) ham L1 blok verilerini indirmektir.

* **Kaynak:** [Hyperliquid Docs - Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim tarihi: 29 Ekim 2026)

---

## 2. `userFunding` Analizi

### Kayıt Sayısı, Geçmiş Derinliği ve Sayfalama
* **Kayıt Sınırı:** Resmî belgenin *Pagination* genel kuralına göre zaman aralığı alan uç noktalar tek istekte en fazla **500 kayıt** (veya veri bloğu) döner.
* **Geçmiş Derinliği:** `userFunding` için `userFillsByTime`'daki gibi katı bir 10.000 işlem sınırı resmî belgede yer almamaktadır; aylar öncesine ait geçmiş fonlama ödemeleri zaman damgasıyla çekilebilir.
* **İstek Gövdesi:**
  ```json
  {
    "type": "userFunding",
    "user": "0x...",
    "startTime": 1730000000000,
    "endTime": 1730050000000
  }
  ```
* **Sayfalama:** 500 kayıt döndüğünde, son kaydın `time` değeri bir sonraki isteğin `startTime` değeri yapılarak ardışık sayfalanır.

### Aktif Bir Adreste 1 Haftalık Boşluk Geri Alınabilir mi?
* **Kesinlikle Evet:**
  * Fonlama ödemeleri saniye/dakika bazlı değil, **saatte bir kez** (her saat başı UTC :00'da) hesaplanır ve cüzdana yansıtılır.
  * Bir trader aynı anda 10 farklı pozisyon taşısa dahi haftalık toplam fonlama satırı:  
    $$7 \text{ gün} \times 24 \text{ saat} \times 10 \text{ coin} = 1.680 \text{ kayıt}$$
  * 500'lük sayfalarla sadece **3–4 API çağrısında** tüm bir haftalık fonlama geçmişi kayıpsız olarak tamamen kapatılabilir.

* **Kaynak:** [Hyperliquid Docs - Perpetuals Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals) (Erişim tarihi: 29 Ekim 2026)

---

## 3. `candleSnapshot` Analizi

### Saatlik Mum Sınırı ve Geçmiş Derinliği
* **Kayıt Sınırı:** Resmî belgede açıkça belirtilmiştir: **"Only the most recent 5000 candles are available"** (Yalnızca en güncel 5.000 mum erişilebilirdir).
* **Saatlik Mumda ("1h") Ne Kadar Geriye Gidilebilir?**
  * 5.000 adet 1 saatlik mum = **5.000 saat** $\approx$ **208,3 gün (~6,9 ay)**.
  * Dolayısıyla birkaç saatlik, birkaç günlük hatta birkaç aylık veri boşlukları `candleSnapshot` ile çok rahat bir şekilde geriye dönük doldurulabilir.
* **İstek Gövdesi:**
  ```json
  {
    "type": "candleSnapshot",
    "req": {
      "coin": "BTC",
      "interval": "1h",
      "startTime": 1730000000000,
      "endTime": 1730050000000
    }
  }
  ```

### HIP-3 Piyasaları İçin Coin Adı Formatı
* Resmî belgedeki kural: **"For HIP-3, you need to prefix with the dex name, e.g. 'xyz:XYZ100'"**.
* HIP-3 piyasalarında coin parametresi `dex_adı:sembol` şeklinde yazılmalıdır.
  * Örnekler: `xyz:NVDA`, `xyz:TSLA`, `xyz:GOLD`, `xyz:BRENTOIL`, `xyz:XYZ100`.
  * *(Not: Spot piyasalar için ise `PURR/USDC` veya `@107` formatı kullanılır).*

* **Kaynak:** [Hyperliquid Docs - Info Endpoint](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim tarihi: 29 Ekim 2026)

---

## 4. İstek Sınırları (Rate Limits) ve 200 Adreslik Mimari Önerisi

### Ağırlık Sistemi ve IP Başına Sınır
Hyperliquid REST API'sinde basit istek adedi yerine dinamik ağırlık (weight) sistemi uygulanır:
* **IP Başına REST Sınırı:** **Dakikada 1.200 ağırlık (1200 weight / minute)**.
* **Baz Ağırlıklar:**
  * Hafif uç noktalar (`l2Book`, `allMids`, `clearinghouseState`, `orderStatus`): **2 ağırlık**.
  * `userRole`: **60 ağırlık**.
  * Diğer tüm info uç noktaları (varsayılan taban): **20 ağırlık**.
* **Dönen Veri Başına Ek Ağırlık (Dynamic Weight Penalty):**
  * `userFills`, `userFillsByTime`, `userFunding`: Dönen **her 20 kayıt için +1 ağırlık** eklenir.  
    *(Örnek: 2.000 dolum dönen bir `userFillsByTime` çağrısı: $20 + (2.000 / 20) = 120$ ağırlık harcar).*
  * `candleSnapshot`: Dönen **her 60 mum için +1 ağırlık** eklenir.  
    *(Örnek: 120 mum dönen çağrı: $20 + (120 / 60) = 22$ ağırlık harcar).*

### 200 Adres × 3 İstek Tipini 15 Dakikaya Güvenle Sığdırma Planı

15 dakikalık bir pencerede IP bütçeniz:
$$\text{Toplam Kapasite} = 15 \text{ dakika} \times 1.200 \text{ ağırlık} = 18.000 \text{ ağırlık}$$

Rutin 15 dakikalık periyotlarda harcanacak ağırlık ve optimizasyon hesabı:
1. **`userFillsByTime` (200 Adres):**
   * Her 15 dakikada çoğu adreste 0–20 dolum olur. Dönen veri az olduğu için istek başına ağırlık ~20–21'dir.
   * $200 \text{ adres} \times 21 \text{ ağırlık} \approx 4.200 \text{ ağırlık}$.
2. **`userFunding` (Optimizasyon):**
   * **Kritik İpucu:** Fonlama ödemeleri **yalnızca saatte bir** gerçekleşir! `userFunding`'i her 15 dakikada bir 200 adrese sormak tamamen gereksizdir.
   * Yalnızca saat başlarında (:01 UTC) saatte bir kez çalıştırılmalıdır. 15 dakikalık döngüde çalıştırmazsanız bütçeniz sıfır harcar; çalıştırsanız bile $200 \times 21 \approx 4.200$ ağırlık tutar.
3. **`candleSnapshot` (Optimizasyon):**
   * **Kritik İpucu:** Mum verisi adrese özel değil, **coine özeldir**. 200 adresin işlem yaptığı tekil coin kümesi (unique coins) genellikle 20–40 adettir.
   * Adres başına değil, yalnızca aktif coinler için çağrılmalıdır ($30 \text{ coin} \times 22 \text{ ağırlık} \approx 660 \text{ ağırlık}$).
4. **Toplam Tüketim ve Dağıtım (Pacing):**
   * Optimize edilmiş toplam periyodik ağırlık: $\approx 4.200 + 660 \approx 4.860$ ağırlık (18.000'lik bütçenin yalnızca **%27'si**).
   * **Zaman Dağıtımı (Pacing / Rate Limiter):** Tüm istekleri aynı saniyede göndermek (burst) dakikalık 1.200 sınırını aşarak anında HTTP 429 almanıza yol açar.
   * **Öneri:** 15 dakika = 900 saniye. 230 isteği 900 saniyeye yayın $\rightarrow$ **Her 3,5–4 saniyede 1 istek** gönderecek sabit bir kuyruk (leaky bucket / token bucket) mekanizması kurun. Bu sayede dakikada yalnızca ~300 ağırlık harcanır ve hiçbir zaman hız sınırına takılmazsınız.

* **Kaynak:** [Hyperliquid Docs - Rate Limits and User Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits) (Erişim tarihi: 29 Ekim 2026)

---

## 5. Belgede Olmayan / Topluluk Kaynaklarındaki Sınırlamalar

*(Aşağıdaki maddeler resmî Hyperliquid GitBook belgelerinde açıkça yer almayan, topluluk geliştiricilerinin tecrübeleri, GitHub commit/issue'ları ve Discord teknik kanallarından derlenen durumlardır)*:

* **Milisaniye Eşitliğinde Sayfalama Takılması (Pagination Boundary Bug):** *(doğrulanamadı)*  
  Aynı milisaniyede (aynı blokta) birden fazla dolum gerçekleştiğinde, bir sonraki sorguya `startTime = son_dolum_zamani` verildiğinde son işlem mükerrer gelebilmekte; `startTime = son_dolum_zamani + 1` yapıldığında ise aynı milisaniyedeki diğer parçalı dolumlar atlanabilmektedir. Toplulukta önerilen çözüm: `aggregateByTime: true` kullanmak veya `startTime`'ı son işlem zamanı yapıp gelen verileri `(tid, hash, oid)` bileşimiyle istemci tarafında tekilleştirmektir.
* **Alt Hesapların (Subaccounts) Görünmezliği:** *(doğrulanamadı)*  
  Eğer takip ettiğiniz bir trader master hesap altında alt hesaplar (sub-account) açıp bot çalıştırıyorsa, ana cüzdan adresine yapılan `userFills` veya `userFunding` sorgularında bu işlemler **dönmemektedir**. Her alt hesabın kendine ait 42 karakterlik ayrı bir türev adresi bulunur; tam arşiv için önce `subAccounts` uç noktasından alt hesapların adresleri bulunup her biri ayrı ayrı arşivlenmelidir.
* **Ajan Cüzdanlar (Agent Wallets) Yanılgısı:** *(doğrulanamadı)*  
  API ile işlem yapan algoritmalar genellikle Hyperliquid'in yetkilendirdiği "Agent Wallet" adreslerini kullanır. Takip edilen adres bir ajan cüzdan ise `userFills` boş döner; mutlaka asıl cüzdanın (master/subaccount) adresi sorgulanmalıdır.
* **HTTP 429'da Standart Dışı Başlıklar:** *(doğrulanamadı)*  
  IP hız sınırı aşıldığında Hyperliquid doğrudan JSON hata mesajı veya HTML 429 gövdesi döner; yanıtta genellikle standart `Retry-After` başlığı bulunmaz. Geliştiricilerin sabit bir süre beklemek yerine üstel geri çekilme (*exponential backoff with jitter*, ör. 5s $\rightarrow$ 15s $\rightarrow$ 45s) uygulaması tavsiye edilir.
* **Kayıp Tarihsel Veri İçin S3 Arşivi:** *(doğrulanamadı)*  
  10.000 işlem sınırını aşan veya günlerce süren büyük veri boşluklarında API yerine Hyperliquid doğrulayıcılarının halka açık S3 deposundaki (`hyperliquid-archive`) günlük blok ve işlem dökümlerini indirip ayrıştırmak toplulukta standart kurtarma yöntemi olarak kabul edilir.
