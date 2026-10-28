# Hyperliquid Copy Trading Açık Kaynak Projeleri ve Doğrulama Raporu

**Araştırma Bağlamı:** Hyperliquid üzerinde trader seçimi, gecikmeli işlem kopyalama simülasyonu (yürütme gecikmesi + işlem maliyetleri sonrası net getiri, Deflated Sharpe, plasebo kontrol grupları, ileriye dönük gölge ölçüm ve ön kayıtlı hipotez testi).  
**Tarih:** 28 Ekim 2026  
**Durum:** Bağımsız Doğrulama Tamamlandı

---

## 1. Yönetici Özeti ve Karşılaştırma Tablosu

Diğer yapay zekâ modellerinin raporlarında önerilen 5 projenin GitHub depoları, açık bilim arşivleri (OSF, arXiv, SSRN) ve genel web dizinleri taranarak çapraz doğrulaması yapılmıştır. Sonuç olarak önerilen projelerden **4 tanesinin tamamen veya kısmen yapay zekâ halüsinasyonu (uydurma)** olduğu, yalnızca **YieldFund çalışmasının doğrulanabilir gerçek bir araştırma** olduğu tespit edilmiştir.

| Proje | Var mı / Durum | Lisans | Yöntem Özeti | Alınabilecek Somut Parça | Bilinen Zayıflıklar / Kısıtlar | Bağlantı |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Dennim89 / hyperliquid-copytrade-study** | **Doğrulanamadı** (Halüsinasyon) | Yok | 389 hesaplık ön kayıtlı kalıcılık çalışması iddiası asılsızdır. GitHub veya OSF üzerinde böyle bir kullanıcı veya çalışma bulunmamaktadır. | Yok (İn-sample / out-of-sample Spearman rank korelasyonu konsepti teorik olarak geçerlidir). | Tamamen model tarafından sentezlenmiş sentetik veri ve hayali depo. | Doğrulanamadı |
| **2. winterchill-trading / copy-backtest** | **Kısmen Doğrulandı** (İz var, açık repo yok) | Belirsiz (Özel / Dahili) | `winterchill-trading` organizasyonu GitHub'da mevcuttur (OCaml tabanlı). Repo içi haritalarda `copy-backtest` bileşeni geçse de bağımsız açık repo yoktur. | Canlı ve backtest ayrışmasını kalemlere (kayma, gecikme, kısmi dolum, fonlama) bölen dekompozisyon mimarisi. | Kamuya açık kaynak kodu bulunmamaktadır (özel veya henüz yayınlanmamış modül). | [GitHub Organizasyonu](https://github.com/winterchill-trading/oxcaml-claude-skills/actions) |
| **3. winterchill-trading / hl-leaderboard** | **Doğrulanamadı** (Açık repo yok) | Belirsiz | Organizasyon içi dokümantasyonda `leader-scoring` ve `integrity gotchas` geçmektedir; ancak "34 metrikli hl-leaderboard" adlı açık bir repo yoktur. | Wash trade tespiti için açık faiz (OI) filtresi ve ilişkili cüzdan kümeleme (clustering) yaklaşımı. | Kod tabanı ve 34 metriğin parametrik eşikleri açık kaynakta mevcut değildir. | Doğrulanamadı |
| **4. hl-copy-core** | **Doğrulanamadı** (Halüsinasyon) | Yok | `hl-copy-core` isimli bir repo veya belirtilen formül literatürde ve GitHub'da bulunmamaktadır; LLM tarafından türetilmiştir. | Puanlama heuristiği: $\text{Getiri} \times (1 - \text{MDD}) \times (0.5 + 0.5 \times \text{Tutarlılık}) \times \min(1, \frac{N}{20})$. | Ampirik test desteği ve doğrulanmış bir kod tabanı yoktur. | Doğrulanamadı |
| **5. YieldFund "Is Copy Trading Profitable?"** | **Doğrulandı** (Gerçek) | Telifli Web Yayını (Açık kaynak kod değil) | 90 günlük pencere, 3 borsa (Binance, Bybit, MEXC), 1.486 lider, 100.236 takipçi işlem olayı. Ön kayıt yok. | Lider başarısı (%97) ile takipçi getirisi (%43,6) arasındaki asimetri ve takipçi getirisini eriten 4 maliyet kalemi. | Hyperliquid/DEX kapsam dışıdır (CEX odaklı); fees/slippage ayrıştırılmamıştır; liderlik tablosu hayatta kalma yanlılığı taşır. | [YieldFund Makalesi](https://www.yieldfund.com/news/is-copy-trading-profitable-a-90-day-multi-exchange-study) |

---

## 2. Proje Bazında Ayrıntılı İnceleme

### 2.1. Dennim89 / hyperliquid-copytrade-study
* **Doğrulama Durumu:** **Doğrulanamadı.**
* **GitHub Kullanıcısı ve Depo:** GitHub'da `Dennim89` adında bir kullanıcı profili ya da `hyperliquid-copytrade-study` adında bir depo bulunmamaktadır.
* **Akademik / Açık Bilim Doğrulaması:** OSF (Open Science Framework), AsPredicted, Zenodo veya arXiv veri tabanlarında 389 hesaplık örneklemle yapılmış bir Hyperliquid trader kalıcılık çalışması kaydı yoktur.
* **Metriklerin Niteliği:** Raporda sunulan sıralama korelasyonları (+0,54 / 0 / −0,44), LLM'lerin istatistiksel rapor kurgularken sıkça ürettiği tipik sentetik çıktılardır.
* **Değerlendirme:** Tamamen yapay zekâ halüsinasyonudur; kod veya veri seti mevcut değildir.

### 2.2. winterchill-trading / copy-backtest
* **Doğrulama Durumu:** **Kısmen Doğrulandı (Kurumsal iz mevcut, açık repo yok).**
* **Bulgular:**
  * `winterchill-trading` GitHub üzerinde Jane Street tarzı OCaml/OxCaml sistemleri geliştiren gerçek bir kantitatif altyapı organizasyonudur.
  * Organizasyonun iş akışı ve dokümantasyon kayıtlarında (`oxcaml-claude-skills`), modül haritasına `copy-backtest` ve `execution-algos` bileşenlerinin eklendiği açıkça görülmektedir (`docs: add execution-algos and copy-backtest to the repository map`).
  * Ancak `copy-backtest` adında kamuya açık, bağımsız bir GitHub deposu erişilebilir değildir (muhtemelen özel bir repo veya monorepo içi dahili kütüphanedir).
* **Bizim İçin Alınabilecek Somut Parça:**
  * **Canlı-Backtest Eşitliği:** Backtest motorunun, canlı yürütme (execution) algoritmasıyla birebir aynı emir durum makinelerini (state machine) ve emir tiplerini kullanması zorunluluğu.
  * **Varyans Ayrıştırma (Decomposition):** Canlı ile simülasyon arasındaki getiri farkının 4 temel kaleme ayrıştırılması:
    1. *Tetiklenme gecikmesi (Detection/Trigger Latency)*
    2. *Emir defteri etkisi ve kayma (L2 Impact & Slippage)*
    3. *Pozisyon parçalanması (Fragmentation - liderin kademeli giriş/çıkışlarında exit senkronizasyonunun bozulması)*
    4. *Fonlama oranları ve borsa komisyonları (Funding fees & Trading fees)*

### 2.3. winterchill-trading / hl-leaderboard
* **Doğrulama Durumu:** **Doğrulanamadı (Kamuya açık repo yok).**
* **Bulgular:**
  * Organizasyonun commit kayıtlarında `docs(gotchas): leader scoring track records, datasets, capacity` ve `gotchas from leader persistence, integrity and follow algorithms` başlıkları geçmektedir.
  * Ancak "34 metrikli hl-leaderboard" veya otomatik wash-trade bayrakları içeren açık kaynak bir repo yayınlanmamıştır.
* **Bizim İçin Alınabilecek Somut Parça (Bütünlük Bayrakları):**
  * **Wash Trade Tespiti:** Açık faiz (Open Interest - OI) değişimi yaratmadan anormal işlem hacmi üreten cüzdanların elenmesi.
  * **Hesaplar Arası / Kümeleme (Cluster) Bütünlüğü:** Aynı ana cüzdandan (funding account) beslenen veya aynı blokta/milisaniyede karşılıklı pozisyon açan (hedging/cross-wallet) adreslerin tek bir risk kümesi olarak etiketlenmesi.
  * **Ters Yönlü Risk Transferi:** Düşük likiditeli tahtalarda kendi diğer hesabına likidite sağlayarak kâr aktaran liderlerin puanlama dışı bırakılması.

### 2.4. hl-copy-core
* **Doğrulama Durumu:** **Doğrulanamadı.**
* **Bulgular:** GitHub, PyPI veya genel kod arşivlerinde `hl-copy-core` isimli bir kütüphane veya raporda belirtilen özgün formül bulunmamaktadır.
* **Önerilen Formülün İncelenmesi:**
  $$\text{Puan} = \text{Getiri} \times (1 - \text{MDD}) \times (0.5 + 0.5 \times \text{Tutarlılık}) \times \min\left(1, \frac{\text{İşlem}}{20}\right)$$
* **Bizim İçin Alınabilecek Parça:** Formül sentetik olsa da içerdiği sezgisel mantık Hyperliquid cüzdan seçim filtresine entegre edilebilir:
  * **İşlem Sayısı Cezası (Ramp):** $\min(1, \frac{N}{20})$ çarpanı, 20 işlemden az geçmişi olan şanslı cüzdanları doğrudan filtreler.
  * **Çekilme Düzeltmesi:** $(1 - \text{MDD})$ katsayısı yüksek kaldıraçla büyük kâr elde edip derin drawdown yaşayan kumarcı cüzdanları cezalandırır.
* **Zayıflık:** Puanlama tekil bir skaler üretir; sermaye kapasitesi, likidite kısıtları ve işlem tutma sürelerini (hold duration) hesaba katmaz.

### 2.5. YieldFund: "Is Copy Trading Profitable? A 90-Day, Multi-Exchange Study"
* **Doğrulama Durumu:** **Doğrulandı.**
* **Yayıncı / Yazar:** Vlad Hategan, YieldFund (Frontpay Capital B.V.), 24 Kasım 2025.
* **Veri Seti:** 24 Ekim 2025'te çekilen 90 günlük liderlik tablosu verileri (Binance, Bybit ve MEXC; toplam 1.486 lider ve 100.236 takipçi işlem sonucu).
* **Temel Bulgular:**
  1. **Lider vs. Takipçi Uçurumu:** Liderlerin **%97,04'ü** kendi hesaplarında kârlıyken (yeşil), bu liderlerin yalnızca **%43,61'i** takipçilerine kâr ettirebilmiştir.
  2. **Takipçi Kazanma Oranı:** Takipçi işlemlerinin yalnızca **%48,48'i** kârla kapanmıştır (48.592 kazanç vs 51.644 kayıp).
  3. **Borsa Bazlı Dağılım:**
     * *Binance:* %66,50 takipçi kazanma oranı, liderlerin %72,45'i takipçiye kâr sağladı (+572.979 USDT).
     * *Bybit:* %43,65 takipçi kazanma oranı, liderlerin %40,34'ü takipçiye kâr sağladı (+346.106 USDT).
     * *MEXC:* %57,79 kazanma oranına rağmen **net −210.040 USDT zarar** (büyük kuyruk kayıpları ve yetersiz stop-loss kullanımı nedeniyle asimetrik negatif getiri).
* **Bizim İçin Alınabilecek Somut Parça:**
  * Takipçi kârlılığını yok eden 4 ana bileşen ampirik olarak listelenmiştir:
    1. *Trading Fees:* Yüksek frekanslı liderlerde komisyon maliyeti getiriyi tamamen silmektedir.
    2. *Profit Sharing:* Kârlı dönemlerde kesilen yüksek paylar takipçinin net sermaye büyümesini engellemektedir.
    3. *Funding Fees:* Uzun süre taşınan ve zararda bekletilen pozisyonlarda biriken fonlama maliyetleri.
    4. *Spread & Slippage:* Liderin piyasa emri sonrası takipçinin daha kötü fiyattan dolması.
* **Bilinen Zayıflıklar:**
  * DEX/Hyperliquid verisi içermez; tamamen merkezi borsaların liderlik tablolarına dayanır.
  * Borsa vitrininde sadece hayatta kalan liderlerin sergilenmesinden kaynaklanan ciddi bir *survivorship bias* mevcuttur.
  * Ön kayıtlı bir bilimsel deney değildir; masa başı geriye dönük veri toplama çalışmasıdır.

---

## 3. Kalıcılık Çalışması Özeti (Ön Kayıt ve Sonuç Tablosu)

Kullanıcı talebinde yer alan 1. maddedeki kalıcılık çalışması (389 hesap, ön kayıt, $+0,54$ / $0$ / $-0,44$ korelasyon değerleri) bağımsız olarak arandığında şu sonuçlara ulaşılmıştır:

* **Ön Kayıt Belgesi (Pre-registration):** **Doğrulanamadı.** Açık bilim dizinlerinde zaman damgalı böyle bir hipotez protokolü mevcut değildir.
* **Sonuç Tablosu:** **Doğrulanamadı.** İddia edilen korelasyon değerleri sentetik bir kurgudur.

### Kendi Araştırmanız İçin Kalıcılık Testi Tasarım Protokolü
Açık kaynakta hazır bir kalıcılık çalışması bulunmadığından, Hyperliquid üzerinde kendi ön kayıtlı kalıcılık araştırmanızı yürütmek için uygulanması gereken metodolojik çerçeve:

1. **Örneklem Dondurma ($t_0$):**
   * Hyperliquid API'si üzerinden belirli bir tarihte en az 60 günlük işlem geçmişi ve en az 30 işlemi olan tüm cüzdanlar listelenir (ör. $N \ge 300$).
2. **Ön Kayıt (Pre-registration):**
   * Seçim kriterleri (In-Sample Sharpe, Sortino, Win Rate), gecikme varsayımları (ör. 500 ms ve 2000 ms), maliyet modeli (VIP0 taker fee + slippage) ve hipotezler OSF üzerinde zaman damgasıyla dondurulur.
3. **Kalıcılık Ölçümü (Rank Correlation):**
   * In-Sample ($t_{-90} \to t_0$) dönemindeki liderlik sıralaması ile Out-of-Sample ($t_0 \to t_{+90}$) dönemindeki gerçekleşen gecikmeli kopya getirisi arasındaki **Spearman Sıralama Korelasyonu ($\rho$)** hesaplanır:
     $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
   * **Hipotez:** $\rho \le 0$ ise liderlik tablosundaki geçmiş performans gelecekteki kopya getirisi için alfa taşımaz (tamamen gürültü veya hayatta kalma yanlılığıdır).
4. **Plasebo Kontrol Grubu:**
   * Aynı zaman diliminde aynı sayıda rastgele açılan işlemler ile lider kopyalama sonuçları Deflated Sharpe Ratio (DSR) kullanılarak çoklu test yanlılığına karşı düzeltilir.
