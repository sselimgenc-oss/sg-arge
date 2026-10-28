# Ham metin (PDF'ten çıkarıldı; kişi adı çıkarıldı) — rapor: opus

```text
ARAŞTIRMA RAPORU · 28 EKİM 2026 · KULLANICI İÇİN


Copytrade'de trader seçimi,
backtest ve forward test
Hyperliquid tarzı açık defterli platformlarda insanlar kimi kopyalayacağına nasıl
karar veriyor, bunu geriye ve ileriye dönük nasıl test ediyor ve sistemi uzun
vadede nasıl ayakta tutuyor.
KISA CEVAP

Altı ana bulgu
    1. Liderlik tablosu bir aday listesidir, seçim değildir. Ciddi kullanıcılar PnL
       sıralamasını sadece havuzu daraltmak için kullanıyor; seçim risk davranışına
       (drawdown, kaldıraç, pozisyon büyüklüğü tutarlılığı) göre yapılıyor.
    2. Geçmiş başarı zayıf ve rejime bağlı biçimde sürüyor. Hyperliquid'de 389 hesapla
       yapılan ön kayıtlı bir çalışma, aylık sıralama korelasyonunun bir dönemde +0,54,
       öncekinde −0,44 olduğunu buldu. Yani "geçen ayın birincisi" stratejisi tek başına
       güvenilir değil.
    3. Saf backtest, kopyalayıcının gerçek sonucunu abartır. Gecikme, slipaj, ücret,
       funding, minimum emir büyüklüğü ve ölçekleme farkı birlikte modellenmeden
       yapılan test, liderin getirisini ölçer, sizinkini değil.
    4. Forward test şart ve kademeli yapılıyor. Ortak pratik: önce kağıt üzerinde takip,
       sonra hedef sermayenin %5–10'u ile 2–4 hafta, sonra ölçekleme.
    5. Sürdürülebilirlik sepet + kurallı çıkış + periyodik rotasyonla sağlanıyor. 3–5
       farklı stilde trader, trader başına sermayenin %10–15'i, önceden yazılmış çıkış
       kuralları ve aylık yeniden değerlendirme.
    6. Etre V2 tasarım olarak bu pratiklerin çoğunu içeriyor. Gölge kopyalama, ön
       kayıtlı karar kuralı ve kontrol grubu güçlü yanları. Eksikler: kısa test süresi, gölge
       sonuçlarında memecoin slipajı, lider bütünlüğü filtresi ve kasa düzeyinde net yön
       limiti (Bölüm 1).




BÖLÜM 1 · @YAVRUETRE_TR


Tweetlerin analizi: Etre V2 "Trading Office"
İki gönderi aynı projeyi anlatıyor: Claude ile yaklaşık 2 ayda yazılmış, Solana
memecoin'lerinde (spot) ve Hyperliquid'de (kaldıraçlı perp) başarılı trader'ları
bulup kopyalayan bir bot. V1 yaklaşık 1,5 ay canlıda kullanılmış ve kâra geçmiş,
ama üst üste eklenen katmanlar eski ve yeni motoru birbirine karıştırınca V2
sıfırdan yazılmış. V2 şu an simülasyon modunda, 200 dolarlık kasa ile çalışıyor.
Plan, yaklaşık 1 hafta simülasyondan sonra yine 200 dolarla canlıya geçmek.
Sistem nasıl çalışıyor
Her iş bir "ajan"a verilmiş ve ajanlar izometrik piksel bir ofiste yaşıyor. Görsel
taraf eğlence; asıl kararlar arkadaki kurallı kodda. Yazar bunu açıkça söylüyor:
kuralları tek tek kendiniz düşünüp yazarsanız yapay zekâ tam olarak onu
kodluyor, "sen yap" derseniz standart bir şey yapıyor.

 AJAN (ODA)      GÖREVİ                                                          DÜNYADAKİ KARŞILIĞI


 Patron          Değişiklikler için oylama yaptırır; çoğunluk gerekir, Finans,   Yatırım komitesi ve risk
                 Risk ve Denetçi'nin veto hakkı var.                             vetosu

 Lab             Yüzlerce trader'ı izler. Her yeni pozisyonu gerçek para         Kağıt üzerinde forward
 müdürleri       olmadan "gölge" olarak kopyalayıp sonucu ölçer; iyi gölge       test (Bölüm 5, adım 4)
                 sonuçlu trader odaya alınır.

 İşlem şefleri   Odadaki trader'ları gerçek kurallarla kopyalar: fiyat bandı,    Uygulama motoru
                 stop, kademeli kâr alma, teminat ve likidasyon kontrolü.

 Finans          İki kasayı (spot ve kaldıraç) tutar, işlem büyüklüğünü kasaya   Pozisyon boyutlama
                 göre ayarlar.

 Risk            Tek bir trader'a veya tek bir token'a fazla yüklenmeyi          Yoğunlaşma limitleri
                 engeller.

 Gözcü           Odalara kimin neden girip çıktığını kaydeder, veri akışlarını   Rotasyon kaydı
                 gözetir.

 Denetçi         Hataları, API kotalarını ve gecikmeleri izler; veri kalitesi    Operasyonel risk izleme
                 düşerse alarm verir.

 Sekreter,       Kural kitabı ve her kararın kaydı; mum grafikleri dahil tüm     Backtest için veri kaydı
 Arşivci         verinin arşivi (2 ayda yaklaşık 16 GB).

 Haber şefi      Telegram'a işlem bildirimleri, 5 dakikada bir durum görseli     Raporlama
                 ve gün sonu özeti.

Seçim hunisi ve kurallar
   Huni: İki bölümde 500'er kişi sürekli izleniyor. Anlık işlemler, cüzdan geçmişi,
   token tutma süresi gibi 20 alanda puanlanıp en iyi 100 kişi aday bölümüne,
   oradan farklıAna
   Kopyalama:   bir filtreyle
                     odadaki10–20  kişi "ana
                              trader'ların    trader birebir
                                           işlemleri odasına"  alınıyor.
                                                             açılıyor.    Üç katman
                                                                       Trader satıncada
                                                                                      bot
   puana göre sürekli   güncelleniyor.
   da kapatıyor (ekranda "trader sattı" / "trader kapattı" olarak görünüyor).
   Giriş filtresi: Fiyat trader'ın giriş fiyatından %1'den fazla uzaklaşmışsa işleme
   girilmiyor.
   Boyut: Trader'ın işlem büyüklüğüne göre, kasaya oranlı.
   Çıkış (spot): −%30'da otomatik stop. İşlem 24 saati geçerse −%20'de, 18 saati
   geçerse −%15'te (ya da tersine kârdaysa) kapatılıyor.



Görsellerden okunan durum

  Spot (Solana memecoin) · SİM                         Kaldıraç (Hyperliquid perp) · SİM
  Kasa $215,66 · başlangıçtan −                        Kasa $221,55 · başlangıçtan
  %0,31                                                +%6,33
  Bugün −$7,45 · 7 işlem açıldı                        Bugün +$11,98 · 42 işlem açıldı
  Ana oda 4/20 · aday 33 · işlem                       Ana oda 7/20 · aday 74 · işlem
  başı $5,55                                           başı $5,68
  Son kapananlar: DOPE +%4,1, DANIELLA −               Açık: SUI 5x, ZEN 5x (−%10,5), TAO 5x (−
  %9,9, VEIL −%3,1. Başka bir ekranda spot             %5,5), PONS 3x; hepsi LONG. Kapananlar:
  trader odası 19/20 dolu ve "14 deneme"               BTC −%1,5, ENA −%15,2, PENDLE −%0,6.
  yazıyor.

En ilginç kısım: "Keşif · Kalıcı kazanan arayışı" paneli
Bu panel, sistemin araştırmadaki en iyi pratiklere en yakın parçası. Tutarlı
bulunan trader'lar bir "kohort" olarak etiketleniyor ve sadece etiketten sonra
açılan lab gölgeleri sayılıyor. Kohort, havuzun geri kalanıyla ve bir kontrol
grubuyla karşılaştırılıyor. Kontrol grubu aynı kaynaktan (GeckoTerminal) gelen
ama ölçütü geçemeyen rastgele cüzdanlar; böylece işe yarayan şeyin kural mı
yoksa kaynak mı olduğu ayrılıyor. Karar ölçütü önceden sabitlenmiş: en az 5 gün,
en az 150 gölge, en az 8 trader, fark güven aralığının 0'ın üstünde olması ve
günlerin %60'ında kohortun önde olması. Şu an iki tarafta da kohort n=0, durum
"veri birikiyor". Örnek kohort adayları: 8 hafta, ayların %75'i kârlı; 7 hafta, %71
kârlı.

Dünya pratikleriyle karşılaştırma
KONU                      ETRE V2                     DEĞERLENDİRME


Forward test              Her pozisyon önce           Güçlü. Çoğu bireysel kullanıcı bu adımı atlıyor.
                          gölgede kopyalanıyor;
                          para sonra açılıyor.

Örneklem dışı ölçüm       Sadece kohort               Doğru. İleriye bakma yanlılığını engelliyor.
                          etiketinden sonraki
                          gölgeler sayılıyor.

Ön kayıtlı karar kuralı   Var; kural önceden sabit,   Akademik düzeyde iyi; Hyperliquid kalıcılık
+ kontrol grubu           kontrol grubu aynı          çalışmasındaki ön kayıtlı kapıyla aynı mantık.
                          kaynaktan.

Risk vetosu ve            Risk, Finans, Denetçi       İyi. Kurumsal komite yapısına benziyor.
yoğunlaşma limiti         veto; trader ve token
                          başına limit.

Kopyalanabilirlik         %1 fiyat bandı, tutma       İyi. Gecikmenin yarattığı kötü dolumları kesiyor.
                          süresi puanlamada.

İstatistiksel güç         5 gün ve 150 gölge eşiği.   Zayıf. Memecoin getirileri çok kalın kuyruklu; birkaç
                                                      gün tek bir piyasa rejimidir. 500 aday arasından
                                                      seçim yapıldığı için Sharpe'ın deneme sayısına
                                                      göre düzeltilmesi (DSR) gerekiyor.

Gölge ile gerçek          Gölge sonuçları             Risk. Solana memecoin'lerde slipaj, MEV/sandviç
dolum farkı               ölçülüyor; slipaj modeli    ve öncelik ücretleri, 5 dolarlık işlemde yüzde olarak
                          tweetlerde görünmüyor.      çok büyük. Gölge sonucu bu maliyetleri
                                                      içermiyorsa iyimser olur.

Lider bütünlüğü           20 alanlı puanlama; dev,    Risk. Memecoin'de "başarılı cüzdanların" bir kısmı
                          insider, bundler filtresi   token sahibi veya içeriden; onları kopyalamak çıkış
                          belirtilmemiş.              likiditesi olmak demek.

Yön ve korelasyon         Açık 4 perp pozisyonun      Eksik görünüyor. Trader ve token limiti var, ama net
                          hepsi LONG.                 yön (beta) ve kasa düzeyinde günlük zarar limiti
                                                      görünmüyor.

Rotasyon                  Puana göre sürekli          Fazla değişim riski. Giriş ve çıkış eşikleri arasında
                          güncelleme; spot odada      histerezis ve minimum kalma süresi önerilir.
                          14 deneme.
 Sim ile canlının aynı     V1'de motorlar karışmış,     Kritik ders. Simülasyon ve canlı aynı uygulama
 kod olması                V2 sıfırdan.                 kodunu çalıştırmalı, fark kalem kalem ölçülmeli.

Genel yorum
Oyunlaştırma burada PnL yarışı değil, bir organizasyon şeması. Bu, Bölüm 8'deki
"süreci puanla" yaklaşımına uyuyor ve iki fayda sağlıyor: sorumlulukları ayırıyor
(V1'deki katman karmaşasının çaresi) ve sahibinin sistemi her akşam takip
etmesini kolaylaştırıyor. Keşif panelindeki kohort, kontrol grubu ve önceden sabit
karar kuralı, incelediğim açık kaynak araçların çoğundan daha disiplinli.
Zayıf nokta ölçek ve süre. 1 haftalık simülasyon, kendi Keşif panelinin karar
verebilmesi için bile kısa; panel şu an "veri birikiyor" diyor. Görsellerdeki +%6,33
ve −%0,31 birkaç günlük, birkaç düzine işlemlik sonuçlar; istatistiksel olarak
gürültü. Sağlıklı sıra şu olur: Keşif kapısı geçilmeden canlıya geçmemek, gölge
sonuçlarına gerçekçi slipaj ve ücret eklemek, memecoin liderlerine bütünlük
filtresi koymak ve kasa düzeyinde net yön ve günlük zarar limiti eklemek.



BÖLÜM 2

Ekosistem: insanlar nerede ve nasıl kopyalıyor
 MODEL              ÖRNEKLER                NASIL ÇALIŞIR                        DİKKAT EDİLECEK


 Protokol           Hyperliquid             Lider havuzu yönetir, yatırımcı      Havuz riski (diğer
 vault'ları         kullanıcı vault'ları,   pay alır. Lider vault'un en az       yatırımcıların giriş-çıkışı),
                    HLP                     %5'ini tutmak zorunda, kâr payı      liderin düşük payı, kilit
                                            %10. Vault açmak için en az 100      süreleri.
                                            USDC yatırma ve 10.000 USDC
                                            ücret gerekir.

 Cüzdan             Copin, HyperDash,       Herhangi bir açık cüzdanın           Lider sizi bilmez, çıkarı
 aynalama           Nansen, Telegram        pozisyonları API cüzdanı ile sizin   hizalı değildir. Gecikme
 araçları           botları (pvp.trade      hesabınıza oranlanarak               ve fiyat kaynağı farkı
                    vb.)                    kopyalanır. Copin 20'den fazla       (Copin Pyth fiyatı
                                            perp DEX'te 700.000'den fazla        kullanıyor) PnL sapması
                                            trader'ı indeksliyor ve açılışta     yaratır.
                                            %0,05 ücret alıyor.
 Borsa içi copy    Binance, Bybit,       Borsa lider profillerini PnL, ROI,      Binance'in kendi rehberi
 trading           BitMEX                MDD, AUM, kopyalayıcı sayısı ile        bile "kopyalayıcı PnL'ine
                   (Hyperliquid          sıralar; 7, 30, 90 günlük filtreler     bakın, kârlı lider kârlı
                   trader'larını         sunar.                                  kopya demek değil"
                   kopyalama dahil)                                              diyor.

 Düzenlenmiş       eToro Popular         Platform liderlere kurallar koyar:      Ödeme yönetilen varlığa
 sosyal trading    Investor, wikifolio   eToro'da günlük risk skoru en           (AUC) bağlı; lider
                                         fazla 7, haftalık drawdown en           büyümek için kopyalayıcı
                                         kötü −%25, tek pozisyon                 çekmeye teşvikli.
                                         portföyün %50'sinden az, ayların
                                         en az %30'u kârlı.

Hyperliquid'i farklı kılan şey her pozisyonun, emrin ve likidasyon fiyatının zincir
üstünde açık olması. Bu, bağımsız analiz araçlarının ve "copiability"
(kopyalanabilirlik) skorlarının ortaya çıkmasını sağladı. Aynı şeffaflık balinaların
pozisyonlarına karşı işlem açmayı da kolaylaştırıyor. James Wynn vakasında,
takipçilerin izlediği yüksek kaldıraçlı tek bir hesap Mayıs 2025'te yaklaşık 100
milyon dolarlık likidasyon yaşadı.



BÖLÜM 3

Trader seçimi: hangi metrikler, hangi eşikler
Rehberler ve araçlar arasında en çok tekrarlanan eşikler aşağıda. Bunlar sektör
pratiği, akademik olarak doğrulanmış sınırlar değil.

 METRİK              İYİ                    UYARI               NOT


 Geçmiş              ≥ 90–180 gün           < 30 gün            BitMEX 180 günlük filtre öneriyor; vault
 uzunluğu                                                       rehberleri en az 3 ay diyor.

 Maksimum            < %20–25               > %40               Eşik stiline göre değişir; asıl önemli olan
 drawdown                                                       DD'nin getiriye oranı.

 Sharpe oranı        > 1,5                  < 0,5               Kısa geçmişte Sharpe gürültülüdür;
                                                                olasılıksal Sharpe (PSR) ile düzeltin.
 Profit factor       > 1,5                  < 1,0             %45 kazanma oranı ve 3,0 PF, %80
                                                              kazanma oranı ve 0,9 PF'den iyidir.

 Kârlı ay oranı      > %65                  < %50             Getirinin birkaç büyük işleme dayanıp
                                                              dayanmadığını gösterir.

 En kötü tek gün     < %5                   > %15             Kuyruk riskinin basit göstergesi.

 Kaldıraç            tutarlı, düşük         rutin 20x+        Ortalama kaldıracın aniden 2 katına
                                                              çıkması çıkış sinyali sayılıyor.

 Lider payı          > %20                  %5–10             Liderin kendi parasının riskte olması çıkar
 (vault)                                                      uyumu sağlar.

Getiriden davranışa geçiş
Son bir yılda araçların çoğu "reaktif" metriklerden (PnL, ROI, kazanma oranı)
"davranışsal" metriklere kaydı: pozisyon büyüklüğünün tutarlılığı, kaybeden
pozisyona ekleme yapıp yapmadığı, çıkış kalitesi, kalabalık işlemlerden kaçınma,
tutma süresi. Örneğin bir analiz sağlayıcısı her ay kohortu getiriye göre değil
disipline göre yeniden kurduğunu ve Ocak–Haziran 2026'da bu kohortun +%50,
ortalama trader'ın −%7,3 yaptığını iddia ediyor. Bu sonuç firmanın kendi beyanı,
denetlenmemiş ve tek bir altı aylık döneme ait.

Kopyalanabilirlik (copiability)
İyi trader ile kopyalanabilir trader aynı şey değil. Ayrı filtrelenmesi gerekenler:
   Tutma süresi: Saniyeler süren scalp'ler, 200 ms'lik kopyalama gecikmesinde bile
   farklı fiyattan doluyor. Saatler-günler süren pozisyonlar insan ve bot için takip
   edilebilir.
   Ölçek farkı: 500 dolarlık bir takipçi, büyük bir lideri yaklaşık %2 ölçekte kopyalar.
   Liderin küçük emirleri Hyperliquid'in 10 dolarlık minimum emrinin altında kalıp
   hiç kopyalanmayabilir.
   Likidite: Liderin işlem yaptığı coinlerin emir defteri sizin büyüklüğünüzü
   kaldırabilmeli.
   Hesap türü: Vault, alt hesap, market-maker ve botlar elenmeli. Bir açık kaynak
   araç 34 metrik hesaplıyor ve wash trade, hesaplar arası işlem, birlikte işlem yapan
   kümeler gibi bütünlük bayraklarını otomatik dışlıyor.
BÖLÜM 4

Backtest: liderin değil, sizin sonucunuzu ölçmek
Copytrade backtest'i iki katmanlıdır. Birinci katman "bu trader iyi mi?" sorusudur
(seçim istatistiği). İkinci katman "ben onu kopyalasaydım ne olurdu?" sorusudur
(uygulama simülasyonu). Çoğu ücretsiz araç yalnızca birincisini yapıyor.

  Saf backtest                                       Gerçekçi backtest
     Liderin dolum fiyatı + sabit slipaj                 Kayıtlı emir defteri üzerinde dolum,
     Ücret ve funding yok ya da kaba                     kuyruk pozisyonu
     Gecikme yok                                         Kopya gecikmesi (örn. 200 ms) + emir
                                                         gecikmesi (örn. 50 ms)
     Bugünkü liderlik tablosundan geriye
     bakış                                               Taker/maker ücret, saatlik funding, lot
                                                         ve tick yuvarlama
  Sonuç: iyimser, hayatta kalan
  yanlılığı içerir.                                      Canlı motorla aynı aynalama kodu
                                                     Sonuç: canlıyla fark
                                                     ayrıştırılabilir.


Açık kaynak copy-backtest projesi ikinci yaklaşımın iyi bir örneği. Canlı
kopyalama motoruyla aynı kodu kullanıyor, sonucu deterministik üretiyor ve
canlı sonuçla backtest arasındaki farkı ücret, slipaj, zamanlama, kısmi dolum ve
funding kalemlerine bölüyor. Kendi örneğinde fark 1,2 baz puan ve çoğu
zamanlamadan geliyor. Likidasyon ve marjin reddini modellemediğini açıkça
yazıyor.
Copin'in yerleşik backtest'i ise kullanıcı tarafı ayarlarla çalışıyor: sermaye, ilk
pozisyon marjini, kaldıraç, coin listesi, pozisyon başına stop, maksimum hacim
çarpanı ve "ters kopyalama" (liderin tersine işlem açma). Birden çok trader'ı aynı
anda test edip sıralayabiliyorsunuz.

Seçim yanlılığını düzeltmek
Binlerce cüzdan arasından en yüksek Sharpe'lıyı seçtiğinizde, o Sharpe'ın bir
kısmı şanstır. Profesyonel tarafta kullanılan düzeltmeler:
   Olasılıksal Sharpe (PSR): Gözlenen Sharpe'ın, getiri sayısı, çarpıklık ve basıklık
   hesaba katıldığında bir eşiğin üzerinde olma olasılığı.
   Deflated Sharpe (DSR, Bailey ve López de Prado): Kaç aday denediğinizi
   "deneme sayısı" olarak katıp Sharpe'ı aşağı düzeltir. Taranan her lider bir
   denemedir.
   Minimum track record uzunluğu: Belirli bir Sharpe'a güvenmek için gereken
   asgari gözlem sayısı.
   PBO (backtest overfitting olasılığı) ve SPA/Reality Check: Seçilen stratejinin
   örneklem dışında medyanın altında kalma olasılığını ve "en iyi"nin rastgeleden
   anlamlı farkını test eder.



BÖLÜM 5

Forward test: dünyada yaygın kademeli akış
Aşağıdaki sıra, incelenen rehberlerin, araçların ve vault çerçevelerinin ortak
noktası. Her adımın bir geçme koşulu var.

 Adım 1                              Adım 2                              Adım 3

 Tarama                              Skorlama                            Gerçekçi backtest
 Liderlik tablosu, min. hesap        Risk metrikleri, bütünlük           Gecikme, ücret, funding, ölçek;
 değeri, sadece perp, bot ve vault   bayrakları, kopyalanabilirlik.      DSR ile düzeltme.
 dışı.

 Adım 4                              Adım 5                              Adım 6

 Kağıt takip                         Küçük sermaye                       Ölçekle ve izle
 Seçimden sonraki dönemde            Hedefin %5–10'u, 2–4 hafta; canlı   Trader başına %10–15 tavan,
 gerçek para olmadan izleme.         ile backtest farkını ölç.           aylık gözden geçirme.

Forward testin neden atlanmaması gerektiğine dair somut bir örnek: Hyperliquid
çalışmasının yazarı daha önce Polymarket'te geçmiş sonuçlara göre 29 cüzdan
seçmiş, bunların sadece 5'i (%17) örneklem dışında pozitif kalmış ve yaklaşık 50
kapanmış işlemlik kağıt testi zararla bitmiş.



BÖLÜM 6
Kanıt: performans gerçekten devam ediyor mu?
 ÇALIŞMA                  VERİ                   BULGU


 Hyperliquid kopya        389 hesap, dört 30     Son blok çiftinde sıralama korelasyonu +0,54, ama
 çalışması (açık          günlük blok, Eylül     önceki çiftlerde +0,00 ve −0,44. İlk %10'un ek başarısı
 kaynak, ön kayıtlı)      2026'ya kadar          anlamlı değil. Yazar sonucu "piyasa fazına bağlı" diye
                                                 yorumluyor; örneklem küçük.

 Oehler, Horn, Wendt      1.084 wikifolio        Ortalamada piyasayı yenmiyorlar. En iyi performans
 (2016)                   sertifikası            gösterenlerin kısa vadeli anlamlı fazla getirisi var.

 Pelster ve ark. (2022)   24.101 wikifolio       Sıralamanın iki ucundaki sinyal sağlayıcılar piyango
                                                 benzeri hisselere yöneliyor; kaybedenler riski artırıyor.
                                                 Turnuva teşvikleri takipçiyi kumar profiline maruz
                                                 bırakıyor.

 Apesteguia,              176 katılımcılı        Kopyalayanların %88'i ilk beşten, %71'i birinciyi seçti.
 Oechssler,               laboratuvar deneyi     Kopyalama imkânı en riskli varlığı seçme oranını
 Weidenholzer (2020)                             %32,5'ten %51,6'ya çıkardı. Sonuç: "copy trading aşırı
                                                 risk almaya yol açar."

Ortak ders: sıralamanın en üstü, şans ve risk iştahının en yüksek olduğu yer.
Kalıcılık varsa bile zayıf ve dönemsel, bu yüzden sistemin "seçim doğru mu"
sorusunu sürekli yeniden sorması gerekiyor.



BÖLÜM 7

Sürdürülebilirlik: risk, bozulma ve rotasyon
Portföy kuralları
   Aynı anda 3–5 trader, birbirinden farklı stil (trend, mean-reversion, swing, farklı
   coin grupları).
   Tek trader'a sermayenin en fazla %10–15'i. Kopyalama için ayrı alt hesap.
   Kendi tarafınızda kaldıraç tavanı, pozisyon başına stop ve günlük zarar limiti;
   liderin kurallarına güvenmeyin.
Önceden yazılmış çıkış tetikleyicileri
   Kopyalanan pozisyonda %25 drawdown.
   Liderin ortalama kaldıracının 2 katından fazla artması (stil kayması).
   2 haftadan uzun işlem yapmama.
   Liderin AUM'u büyürken performansın düşmesi (kapasite sınırı).
   Canlı sonuçla backtest arasındaki farkın açıklanamayan biçimde büyümesi.

Rotasyon
Yaygın pratik aylık gözden geçirme. Daha sistematik olanlar kohortu her ay
sıfırdan, aynı kurallarla yeniden kuruyor ve eski üyeye ayrıcalık tanımıyor. Bu, "bir
kez seçtim, bırakamıyorum" yanlılığını önlüyor. Rotasyonun dezavantajı ücret ve
yeni trader'ın öğrenme maliyeti; bu yüzden eşiklerin histerezisli olması (girmek
için yüksek, çıkmak için daha düşük bar) dalgalanmayı azaltır.

Rejim ve kalabalık riski
Hyperliquid çalışmasındaki korelasyonun dönemden döneme işaret değiştirmesi,
trader becerisinin piyasa rejimine bağlı olduğunu gösteriyor. Ayrıca herkesin aynı
açık balinayı kopyalaması, o pozisyonları likidasyon avına açık hale getiriyor.



BÖLÜM 8
Oyunlaştırma: işe yarayan ve yaramayan
  Faydalı olduğu yer                                 Zarar verdiği yer
     Disiplini puanlamak: drawdown                       Sadece PnL'yi ödüllendiren sıralamalar:
     kontrolü, tutarlı boyut, kurala uyum.               risk iştahını artırır (Apesteguia, Pelster).
     Lig sistemi ile kademeli sermaye: trader            Kısa pencereli yarışmalar: 7 günlük
     "seviye atladıkça" daha fazla pay alır,             şampiyon genelde yüksek kaldıraçlı
     düşünce otomatik iner.                              şanslı hesaptır.
     Forward testi bir sezon gibi                        Rozet ve seri ödülleri, kullanıcının kötü
     kurgulamak; seçim ve test dönemlerini               trader'ı bırakmasını zorlaştırır.
     ayırmak.
     Kullanıcıyı kurallı çıkışa alıştırmak.

Örnek bir puan formülü, açık kaynak bir Hyperliquid sıralayıcısının kullandığı
basit yapı:

  skor = getiri × (1 − max_drawdown) × (0,5 + 0,5 × tutarlılık) × min(1, işlem_sayısı


Bu formül getiriyi drawdown ve tutarlılıkla cezalandırıyor ve az işlemli hesapları
kısıyor. Seçim yanlılığını düzeltmiyor, o yüzden aynı proje bunun üstüne DSR,
PBO ve kalıcılık testleri ekliyor.
BÖLÜM 9

Kendi sistemin için öneri
1. Aday havuzunu PnL ile, seçimi risk ve davranış metrikleriyle yap. Bütünlük
   bayrağı olanları ele.
2. Backtest'i kopyalayıcı perspektifinden kur: gecikme, ücret, funding, minimum
   emir ve senin sermaye ölçeğin.
3. Taradığın aday sayısını kaydet ve Sharpe'ı buna göre düzelt (DSR).
4. Seçimden sonra en az 2–4 hafta kağıt takip, ardından küçük sermaye.
5. Çıkış kurallarını kodla, aylık yeniden seçim yap, eşiklere histerezis ekle.
6. Oyunlaştırma kullanacaksan getiri yerine süreci puanla.



KAYNAKLAR


Kaynaklar
  Hyperliquid Docs: For vault leaders
  Hyperliquid Copy Trading Guide: Vaults, Copin & Third-Party Tools
  OneKey: A Practical Framework for Choosing Profitable Hyperliquid Vaults
  winterchill-trading/copy-backtest ve hl-leaderboard
  Dennim89/hyperliquid-copytrade-study
  Copin Docs: Backtesting
  Nansen: Find & Copytrade Wallets on Hyperliquid
  Dropstab: Hyperliquid Smart Money
  HyperSonnar: copiability leaderboard
  Binance: Essential Criteria for Selecting Lead Traders
  Whaleportal: BitMEX Hyperliquid Copy Trading
  eToro Popular Investor Program
  Apesteguia, Oechssler, Weidenholzer: Copy Trading (Management Science, 2020)
  Social trading: do signal providers trigger gambling? (Review of Managerial
  Science, 2022)
  Oehler, Horn, Wendt: Benefits from social trading? (IRFA, 2016)
  Bailey, López de Prado: The Deflated Sharpe Ratio
  Cointelegraph: Hyperliquid whale loss near $100M
  Delphi Digital: Hyperliquid's social trading arena
Bu rapor yatırım tavsiyesi değildir.
```
