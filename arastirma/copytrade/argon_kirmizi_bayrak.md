> **Lider notu (2026-10-28):** Argon (Gemini) çıktısı, kullanıcı getirdi. Eşikler Argon'un önerisidir, doğrulanmadı ve kapı kuralı
> değildir. Kapıda zaten karşılığı olanlar: 1 piyasa yapıcı (tarz: medyan tutma ≥ 1 sa, kısa işlem payı), 6 tek işlem (en büyük işlem
> payı ≤ %30), 7 aşırı kaldıraç (medyan ≤ 3x, en yüksek ≤ 10x), 8 martingale, 9 terk edilmiş hesap (hesap değeri ≥ 10.000 $),
> 4 ilişkili hesap (yalnız işaret), 10 HIP-3 (`pay_*`, `gece_payi`). **Eksikler** → `docs/GOREV_SECIM_V1.md` Ek: 2 funding toplayıcı,
> 3 vault/HLP oranı ve `userRole`, 4 alt hesapta ters pozisyon, 5 hacim çiftçisi.

# Hyperliquid Kopyalama Öncesi Trader Seçimi: "Kırmızı Bayrak" Tespit Rehberi

Bu rehber, Hyperliquid üzerinde kaldıraçlı işlem (perp) yapan trader'lar arasından kopyalanacak hesapları seçerken, geçmiş performansı yapay veya yanıltıcı olan ve özellikle **30 dakika – 2 saat gecikmeli manuel kopyalama** operasyonunda sermayeyi hızla eritebilecek hesap türlerini tespit etmek amacıyla hazırlanmıştır.

Tüm tespit yöntemleri, Hyperliquid'in herkese açık `/info` API uç noktalarına ve resmî dokümantasyon kurallarına dayanmaktadır.

---

## 1. Operasyonel Bağlam ve Gecikme (Latency) Riski

30 dakika ile 2 saat arasındaki gecikmeyle (manual execution latency) kopyalama yapmak, piyasa zamanlamasını tamamen devre dışı bırakır. Bu modelde bir trader'ın performansı şu üç temel nedenle sizin hesabınıza birebir yansımaz:
1. **Zaman Uyumsuzluğu:** Scalp veya HFT pozisyonları 1-15 dakika içinde kârla kapanırken, siz pozisyona girdiğinizde piyasa terse dönmüş olabilir.
2. **Komisyon Asimetrisi:** Piyasa yapıcılar maker komisyon iadesi (rebate) alırken (-%0,001 ila -%0,003), siz gecikmeli piyasa emriyle %0,045 taker komisyonu ödersiniz.
3. **Eksik Bacak / Unhedged Pozisyon:** Trader'ın spot piyasada veya başka bir borsadaki koruma (hedge) bacağını göremediğinizde, delta-nötr bir pozisyon sizde çıplak bir yönlü risk haline gelir.

---

## 2. Kopyalanmaya Uygun Olmayan 10 Hesap Türü ve API Tespit Kuralları

### 2.1. Piyasa Yapıcı / Yüksek Frekanslı Hesaplar (Market Maker / HFT)
* **(a) Neden Kopyalanamaz:**
  Bu hesaplar yönlü trend tahmini yapmaz; emir defterinin iki tarafına likidite sağlayarak alış-satış farkını (spread) ve negatif maker komisyon iadelerini (maker rebate) toplarlar. Pozisyonların ömrü saniyeler veya dakikalardır. 30 dk – 2 saat gecikmeyle girdiğinizde işlem çoktan kapanmıştır; siz %0,045 taker komisyonu öder, piyasa kayması (slippage) yaşar ve trader kâr ederken kesin zarar edersiniz.
* **(b) API ile Tespit:**
  * **Uç Nokta:** [`userFills`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `crossed`, `time`, `sz`, `startPosition`
  * **Eşik / Örüntü:**
    * `crossed == false` (maker emir) oranı **>%85**.
    * İki işlem arasındaki medyan zaman farkı `< 60 saniye`.
    * Günlük dolum adedi `> 300` ve `startPosition` ile `sz` sürekli birbirini sıfırlayan küçük miktarlı envanter yönetimi hareketleri.
* **(c) Yanlış Alarm Riski:**
  Düşük frekanslı sabırlı bir swing trader da komisyon tasarrufu için yalnızca limit emir (post-only) kullanabilir (`crossed: false`).
  * *Ayırt edici metrik:* Pozisyonda kalma süresi (holding time) saatler/günler mertebesindeyse ve günlük işlem sayısı azsa (örneğin < 10) bu hesap piyasa yapıcı değildir.

---

### 2.2. Funding Toplayıcı / Delta-Nötr Hesaplar (Cash & Carry / Basis Trading)
* **(a) Neden Kopyalanamaz:**
  Bu trader'lar tek yönlü piyasa riski almaz. Hyperliquid perp tarafında örneğin yüklü Short açarken, Hyperliquid spot piyasasında ya da harici bir CEX'te (Binance, Bybit vb.) eşdeğer miktarda Long tutarak delta-nötr kalırlar. Amaçları yalnızca saatlik funding getirisini toplamaktır. Siz sadece Hyperliquid perp bacağını kopyaladığınızda elinizde **tamamen korunmasız (unhedged) çıplak yönlü pozisyon** kalır. Varlık yukarı fırladığında sınırsız zarara uğrarsınız.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`userFunding`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals), [`clearinghouseState`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`portfolio`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `userFunding.delta.usdc`, `clearinghouseState.assetPositions[].cumFunding.allTime`, `portfolio.allTime.pnlHistory`
  * **Eşik / Örüntü:**
    * Kümülatif funding getirisi toplam gerçekleşen kârın büyük kısmını oluşturur: `cumFunding / Total Realized PnL > 0,60`.
    * Pozisyon yönü piyasa funding oranının tersinedir (funding pozitifken haftalarca sabit Short).
    * `portfolio.pnlHistory` eğrisi piyasa dalgalanmalarından bağımsız, neredeyse cetvelle çizilmiş gibi düz ve pürüzsüz bir şekilde yukarı tırmanır (sıfıra yakın drawdown).
* **(c) Yanlış Alarm Riski:**
  Trend yönünde uzun süre pozisyon taşıyan makro bir swing trader da yüksek funding toplayabilir.
  * *Ayırt edici metrik:* Yönlü trader'ın PnL grafiğinde dayanak varlığın fiyat hareketleriyle korelasyonlu sert düzeltmeler görülür; delta-nötr hesapta ise fiyat dalgalanması PnL eğrisine yansımaz.

---

### 2.3. Vault Lideri ve HLP / Pasif Vault Yatırımcısı
* **(a) Neden Kopyalanamaz:**
  Hyperliquid üzerinde kullanıcılar likidite sağlayıcı havuzuna ([HLP](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)) veya topluluk vault'larına mevduat yatırabilir. Bu hesapların PnL'i bireysel işlem başarısından değil, pasif protokol kâr payından gelir. Eğer hesap bir "Vault Lideri" ise, kendi parasından çok takipçilerin havuzdaki sermayesini yönetir; lider komisyonu (%10 kâr payı) aldığı için kendi risk toleransı sizinkinden farklıdır (takipçilerin parasını yüksek riskle kullanabilir - moral hazard).
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`userVaultEquities`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`vaultDetails`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userRole`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `userVaultEquities[].equity`, `userVaultEquities[].vaultAddress`, `userRole.role`, `vaultDetails.leader`
  * **Eşik / Örüntü:**
    * `userRole.role == "vault"` ise hesap zaten doğrudan bir vault kontratıdır.
    * `userVaultEquities[].equity / clearinghouseState.marginSummary.accountValue > 0,50` ise sermayenin yarısından fazlası HLP (`0xdfc24b077bc1425ad1dea75bcb6f8158e10df303`) veya başka bir vault'ta pasif yatmaktadır.
    * `vaultDetails.leader == hedef_cüzdan` ise hesap bir vault lideridir.
* **(c) Yanlış Alarm Riski:**
  Aktif bir trader boşta duran nakdinin küçük bir kısmıyla HLP'ye girmiş olabilir.
  * *Ayırt edici metrik:* Vault mevduatı toplam portföyün <%20'si ise ve trader düzenli bireysel perp emirleri veriyorsa kopyalanabilir.

---

### 2.4. Alt Hesaplar ve Çapraz Hedge (Subaccounts / Cherry-Picking)
* **(a) Neden Kopyalanamaz:**
  Bazı kullanıcılar ana hesaplarına bağlı çok sayıda alt hesap açar (subaccount). Bir alt hesapta 50x Long, diğerinde 50x Short açarak zıt yönlü işlem yaparlar (cross-hedging). Hesaplardan biri sıfırlanırken diğeri %400 kâr yazar. Yalnızca kazanan alt hesabı sosyal medyada veya liderlik tablosunda gösterirler. Siz sadece kazanan hesabı kopyalarsanız, aslında bir yazı-tura oyununun tek tarafını kopyalamış olursunuz; bir sonraki işlemde kopyaladığınız hesap tasfiye olabilir.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`subAccounts`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userRole`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `userRole.role`, `userRole.data.master`, `subAccounts[].clearinghouseState.assetPositions`
  * **Eşik / Örüntü:**
    * `userRole.role == "subAccount"` ise cüzdan bir alt hesaptır ve API doğrudan `master` cüzdan adresini verir.
    * Ana cüzdan adresi `subAccounts` uç noktasına sorgulandığında, ana hesaba bağlı tüm alt hesaplar listelenir.
    * Eğer `SubAccount-A` üzerinde BTC Long varken aynı anda `SubAccount-B` üzerinde benzer büyüklükte BTC Short pozisyonu varsa kesin çapraz hedge kurgusudur.
* **(c) Yanlış Alarm Riski:**
  Fonlar veya profesyonel tüccarlar farklı stratejilerini (örn. biri BTC swing, diğeri altcoin scalp) izole tutmak için alt hesap kullanır.
  * *Ayırt edici metrik:* Alt hesaplar arasında aynı varlıkta zıt yönlü ve simetrik pozisyonlar yoksa meşru bir portföy ayrımıdır.

---

### 2.5. Airdrop / Hacim Çiftçisi (Volume Farmer / Wash Trader)
* **(a) Neden Kopyalanamaz:**
  Bu hesapların amacı piyasadan yönlü kâr elde etmek değil; platform puanı (Points), token teşviki veya VIP komisyon kademesi kasmak için yapay işlem hacmi yaratmaktır. Pozisyonlar saniyeler içinde başa baş (breakeven) seviyeden kapatılır. 30 dk – 2 saat gecikmeyle girdiğinizde trader çoktan çıkmış olur; siz gereksiz taker komisyonu öder, piyasa gürültüsünde boş yere zarar edersiniz.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`portfolio`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userFills`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `portfolio.allTime.vlm`, `portfolio.allTime.pnlHistory`, `userFills.closedPnl`
  * **Eşik / Örüntü:**
    * Günlük işlem hacmi bakiyenin 100 katından fazladır: `Günlük Hacim / Bakiye > 100x`.
    * Toplam PnL hacme oranla sıfıra yakındır: `|Total PnL| / Total Volume < %0,01`.
    * `userFills` kayıtlarında pozisyonda kalma süresi < 2 dakika ve her işlemdeki `closedPnl` neredeyse 0'dır.
* **(c) Yanlış Alarm Riski:**
  Kötü bir piyasa gününde sürekli stop olan bir scalper da yüksek hacim ve sıfır PnL üretebilir.
  * *Ayırt edici metrik:* Scalper belirgin dalgalanmalarda işlem yapar; hacim çiftçisi ise spread'in en dar olduğu yatay piyasada mekanik olarak hacim basar.

---

### 2.6. Olay / Haber Odaklı ve İçeriden Bilgi Şüphesi (Insider / Announcement Sniping)
* **(a) Neden Kopyalanamaz:**
  Bu cüzdanlar genellikle yeni bir token listelemesi veya büyük bir protokol haberi duyurulmadan dakikalar önce pozisyon açıp, duyuru pompalamasında (pump) dakikalar içinde pozisyonu kapatırlar. Bu performans tekrarlanamaz ve asimetrik bilgiye dayanır. 30 dk – 2 saat sonra kopyalamaya çalıştığınızda, haber pompalamasının en tepesinden "çıkış likiditesi" (exit liquidity) olarak mal almış olursunuz ve anında %20-%50 terste kalırsınız.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`portfolio`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userFills`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `portfolio.allTime.pnlHistory`, `userFills.time`, `userFills.coin`
  * **Eşik / Örüntü:**
    * PnL grafiğinde aylarca sıfır hareket varken tek bir günde dikey bir sıçrama (%500+ artış) vardır.
    * Tek bir işlemin PnL katkısı kümülatif toplam kârın **>%70'ini** oluşturur.
    * İşlem geçmişindeki toplam trade sayısı aşırı düşüktür (`userFills` toplam kayıt sayısı < 15).
* **(c) Yanlış Alarm Riski:**
  Derin temel analiz yaparak katalizörü önceden tahmin eden başarılı bir swing trader da büyük tek seferlik kâr yakalayabilir.
  * *Ayırt edici metrik:* Meşru swing trader haber öncesinde ve sonrasında da istikrarlı risk yönetimiyle işlem yapmaya devam eder; içeriden bilgi avcısı ise vur-kaç sonrası hesabı uykuya alır.

---

### 2.7. Likidasyon Avcısı / Aşırı Kaldıraçlı Tek Seferlik Kumarbaz (Lucky Degenerate)
* **(a) Neden Kopyalanamaz:**
  Küçük bir bakiyeyle (örn. 500$) 40x–50x kaldıraçla tek bir yöne kumar oynamış ve şans eseri gelen sert bir mumla kasayı 50.000$ yapmıştır. Risk yönetimi sıfırdır, tasfiye seviyesi giriş fiyatına %1–2 mesafededir. 30 dk gecikmeyle bu pozisyona girdiğinizde, piyasadaki en ufak dalgalanmada siz tasfiye olursunuz. Bir sonraki işlemde ise trader'ın tüm kasayı sıfırlaması kaçınılmazdır.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`clearinghouseState`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userFills`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `clearinghouseState.assetPositions[].position.leverage.value`, `clearinghouseState.marginSummary.totalMarginUsed`, `clearinghouseState.assetPositions[].position.liquidationPx`
  * **Eşik / Örüntü:**
    * Kaldıraç değeri `> 25x` (özellikle 40x–50x).
    * Marjin kullanım oranı: `totalMarginUsed / accountValue > %85` (hesapta neredeyse hiç serbest teminat tamponu yok).
    * Tasfiye fiyatı mesafesi: `|entryPx - liquidationPx| / entryPx < %2,5`.
* **(c) Yanlış Alarm Riski:**
  Momentum patlamalarında çok dar stop-loss ile anlık yüksek kaldıraç kullanan profesyoneller olabilir.
  * *Ayırt edici metrik:* Profesyonel trader pozisyon terse gittiğinde hemen stop emriyle çıkar (`userFills` içinde küçük zararlı kapanışlar görülür); şans avcısı ise stop koymaz ve liq fiyatına kadar bekler.

---

### 2.8. Martingale / Zarardaki Pozisyona Sürekli Ekleme (Averaging Down)
* **(a) Neden Kopyalanamaz:**
  Pozisyon aleyhe gittikçe zararı kabul etmeyip pozisyon büyüklüğünü katlayarak artırır. Kağıt üzerinde kazanma oranı %90–95 görünür; çünkü piyasa küçük bir düzeltme yaptığında kârla çıkar. Ancak tek bir tek yönlü sert trendde tüm hesap sıfırlanır. 30 dk – 2 saat gecikmeyle kopyaladığınızda ekleme seviyelerini kaçırır, marjininizi erken tüketir ve trader'dan bile önce tasfiye olursunuz.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`userFills`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`clearinghouseState`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `userFills.px`, `userFills.sz`, `userFills.dir`, `clearinghouseState.assetPositions[].unrealizedPnl`, `clearinghouseState.assetPositions[].szi`
  * **Eşik / Örüntü:**
    * Aynı varlıkta fiyat terse gittikçe artan boyutlarla (`sz`) ardışık ekleme emirleri (`dir: "Open Long"` veya `"Open Short"`).
    * `unrealizedPnl / accountValue < -%30` seviyesine indiği halde pozisyon kapatılmayıp `szi` değerinin büyütülmesi.
    * Geçmişte gerçekleşmiş zararla kapatılmış (stop-loss) tek bir işlemin dahi bulunmaması.
* **(c) Yanlış Alarm Riski:**
  Önceden planlanmış kademeli alım (DCA / grid trading) stratejileriyle karışabilir.
  * *Ayırt edici metrik:* DCA stratejisinde emir boyutları sabittir ve önceden belirlenmiş bir maksimum zarar limiti vardır; Martingale'de ise boyutlar geometrik olarak büyür ve marjin bitene kadar sürer.

---

### 2.9. Para Çekip Terk Edilmiş Hesaplar (Zombie / Drained Account)
* **(a) Neden Kopyalanamaz:**
  Liderlik tablosunda tüm zamanlar PnL'i 200.000$ görünür ancak trader parasını çekmiş ve hesapta yalnızca 150$ bırakmıştır. Bakiye önemsizleştiği için trader artık o hesabı ciddiye almaz, test veya aşırı riskli işlemler yapar. Sizin sermaye bazlı pozisyon boyutlandırmanız tamamen kilitlenir (trader'ın 50$'lık pozisyonunu kendi kasanıza oranlamaya çalıştığınızda orantısız risk oluşur).
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`clearinghouseState`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userNonFundingLedgerUpdates`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals), [`portfolio`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `clearinghouseState.marginSummary.accountValue`, `userNonFundingLedgerUpdates[].delta.type`, `portfolio.allTime.pnlHistory`
  * **Eşik / Örüntü:**
    * Güncel hesap değeri çok düşüktür: `accountValue < $500`.
    * Geçmiş tepe PnL ile güncel bakiye uyumsuzdur: `accountValue / Peak Historical PnL < %0,05`.
    * `userNonFundingLedgerUpdates` içinde son dönemde yüklü `withdraw` hareketleri görülür.
* **(c) Yanlış Alarm Riski:**
  Düzenli kâr çekip kasasını hep sabit bir tutarda (örneğin 20.000$) tutan profesyonel para yönetimiyle karışabilir.
  * *Ayırt edici metrik:* Profesyonel trader kasasını anlamlı bir operasyonel seviyede sabit tutar; zombie hesapta ise bakiye mikroskobik seviyelere düşmüştür.

---

### 2.10. HIP-3 (Hisse/Emtia Perp) Ağırlıklı Hesaplar (Market Gap & Liquidity Risk)
* **(a) Neden Kopyalanamaz:**
  [HIP-3](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) ile Hyperliquid'de deployer'lar tarafından hisse senedi ve emtia türevleri (TSLA, NVDA gibi `xyz:` önekli kontratlar) listelenmektedir. Kripto 7/24 açıkken geleneksel hisse piyasaları geceleri ve hafta sonları kapalıdır. Hafta sonu gelen bir haberde piyasa açılışında devasa fiyat boşlukları (gap) oluşur. 30 dk – 2 saat gecikmeyle elle işlem yaparken hafta sonu kapanışını kaçırabilir, likiditenin kuruduğu saatlerde aşırı spread ve kayma (slippage) ile karşılaşabilirsiniz.
* **(b) API ile Tespit:**
  * **Uç Noktalar:** [`clearinghouseState`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint), [`userFills`](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint) (Erişim: 28 Ekim 2026)
  * **Alanlar:** `clearinghouseState.assetPositions[].position.coin`, `userFills.coin`
  * **Eşik / Örüntü:**
    * Pozisyon veya dolum listesindeki varlık isimlerinde `:` öneki bulunması (örneğin `xyz:XYZ100`, `xyz:TSLA`, `birb:PENGU`).
    * HIP-3 pozisyonlarının toplam açık pozisyona oranı: `HIP-3 Pozisyon Değeri / Toplam Pozisyon Değeri > %30`.
* **(c) Yanlış Alarm Riski:**
  Trader HIP-3 piyasalarında sadece seans içinde işlem yapıp piyasa kapanmadan önce pozisyonu tamamen kapatıyorsa (intraday flat) gap riskine girmez.
  * *Ayırt edici metrik:* 30 dk – 2 saatlik gecikmeyle elle kopyalayan kişi seans kapanışına yetişemeyebileceği için hesap yine de yüksek risk grubundadır.

---

## 3. Özet Tespit Kuralları Tablosu

| Hesap Türü | İncelenen API Alanı | Tek Satırlık Tespit Kuralı / Eşik | Güven Derecesi |
| :--- | :--- | :--- | :--- |
| **1. Piyasa Yapıcı (HFT/MM)** | `userFills.crossed`, `userFills.time` | `crossed == false` oranı > %85 VE medyan işlem aralığı < 60 saniye | **Yüksek** |
| **2. Funding Toplayıcı (Delta-Nötr)** | `userFunding.delta`, `clearinghouseState.assetPositions[].cumFunding` | `cumFunding / Realized PnL > 0,60` VE PnL eğrisi drawdown'suz düz çizgi | **Yüksek** |
| **3. Vault / Pasif HLP** | `userRole.role`, `userVaultEquities[].equity` | `role == "vault"` VEYA `userVaultEquities.equity / accountValue > 0,50` | **Yüksek** |
| **4. Alt Hesap / Çapraz Hedge** | `userRole.data.master`, `subAccounts[].clearinghouseState` | `role == "subAccount"` VE master'a bağlı diğer sub hesapta aynı coin'de ters pozisyon | **Yüksek** |
| **5. Hacim Çiftçisi (Wash Trading)** | `portfolio.vlm`, `portfolio.pnlHistory` | Günlük `Volume / Equity > 100x` VE `Total PnL / Total Volume < %0,01` | **Yüksek** |
| **6. İçeriden Bilgi / Haber Sniping** | `portfolio.pnlHistory`, `userFills.coin` | Tek işlemin kârı toplam PnL'in > %70'i VE toplam işlem sayısı < 15 | **Orta** |
| **7. Şanslı Kumarbaz (Aşırı Kaldıraç)** | `clearinghouseState.assetPositions[].leverage`, `marginSummary` | Kaldıraç > 25x VE `totalMarginUsed / accountValue > %85` VE Liq mesafesi < %2,5 | **Yüksek** |
| **8. Martingale (Zarara Ekleme)** | `userFills.sz`, `clearinghouseState.assetPositions[].unrealizedPnl` | Fiyat aleyhe gittikçe artan boyutlu ardışık alışlar VE Unrealized PnL < -%30 iken ekleme | **Yüksek** |
| **9. Zombie / Terk Edilmiş Bakiye** | `clearinghouseState.marginSummary.accountValue` | `accountValue < $500` VE `accountValue / Peak Historical PnL < %0,05` | **Yüksek** |
| **10. HIP-3 Ağırlıklı Hesaplar** | `clearinghouseState.assetPositions[].position.coin` | Pozisyonlarda `:` önekli varlık payı (`xyz:TSLA` vb.) toplam marjinin > %30'u | **Yüksek** |

---

## 4. Elle ve 30 Dk – 2 Saat Gecikmeli Kopya İçin En Tehlikeli 3 Profil

30 dakika ile 2 saat arasındaki gecikme (latency), piyasa zamanlamasını tamamen ortadan kaldırır. Bu operasyonel modelde hesabınızı en hızlı sıfırlayacak 3 profil şunlardır:

1. **Martingale / Zarara Ekleyen Hesaplar (1 Numaralı Portföy Katili):**
   Trader piyasaya karşı inatlaştıkça kademeli alım yapar. Siz 30 dk – 2 saat gecikmeyle girdiğinizde, trader'ın ilk düşük maliyetli girişlerini kaçırır, doğrudan en dipteki devasa pozisyon büyüklüklerine plansız şekilde ortak olursunuz. Trader'ın marjini henüz tükenmemişken, siz gecikmeli maliyetlenme yüzünden trader'dan bile önce tasfiye olursunuz.
2. **Piyasa Yapıcı / Yüksek Frekanslı Hesaplar (Kesin ve Hızlı Kan Kaybı):**
   HFT ve piyasa yapıcılar pozisyonlarını dakikalar içinde kapatır. 1 saat sonra girdiğinizde pozisyon çoktan bitmiş, piyasa yön değiştirmiş olur. Sürekli ters yönde, en kötü fiyattan ve **%0,045 taker komisyonu** ödeyerek işlem açarsınız. Birkaç gün içinde kasa komisyon ve slippage ile erir.
3. **Funding Toplayıcı / Delta-Nötr Hesaplar (Görünmez Tuzak):**
   Leaderboard'da kusursuz bir kâr grafiği görürsünüz; ancak trader'ın harici spot veya CEX hedge bacağını göremezsiniz. Trader'ın Hyperliquid'deki devasa Short pozisyonunu tek başına kopyaladığınız anda, delta-nötr bir strateji yerine tek yönlü çıplak bir kumar pozisyonuna girmiş olursunuz. Dayanak varlık ralli yaptığında tüm bakiyeniz silinir.
