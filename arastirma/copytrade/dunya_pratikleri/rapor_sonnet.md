# Ham metin (PDF'ten çıkarıldı; kişi adı çıkarıldı) — rapor: sonnet

```text
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




Copytrade, Backtest ve Forward Test:
Dünyada Nasıl Yapılıyor?
  ​Oct 28, 2026         · ​@kullanıcı


Özet
Copytrade'de kazanan taraf çoğunlukla "en iyi traderı bulan" değil, lider seçimini bir
portföy ve risk yönetimi problemi olarak ele alan taraf. Veriler bunu net gösteriyor: 3
borsada 1.486 liderin %97'si kendi hesabında kârdayken, takipçilerine kâr ettirenlerin oranı
yalnızca %43,6 (YieldFund, 90 günlük çalışma).

     Kopya ≠ orijinal. Giriş fiyatı farkı, kayma (slippage), ücret, funding ve kâr payı liderin
     performansını takipçide aşındırıyor.
     Sıralamalar yanıltıcı. Liderlik tabloları hayatta kalanları gösterir (survivorship bias); kısa
     vadeli yüksek ROI çoğunlukla aşırı risk ya da şanstır.
     Profesyoneller üç aşamalı ilerliyor: geçmiş veriyle eleme (backtest) → kağıt üstünde ya
     da küçük sermayeyle canlı izleme (forward test) → kademeli sermaye artırımı.
     Sürdürülebilirlik kurallarla sağlanıyor: liderleri çeşitlendirmek, önceden yazılmış
     çıkış/kesme kuralları, periyodik yeniden puanlama ve rotasyon.
     Oyunlaştırma (puan, seviye, lig) disiplini artırabilir; ama araştırmalar sosyal sıralamanın
     risk iştahını da artırdığını gösteriyor, yani tasarım dikkat istiyor.


Tweet analizi
X iki tweet'e de dışarıdan erişimi engellediği için metin ve görselleri doğrudan
okuyamadım. Ekran görüntüleri ya da metin paylaşılırsa bu bölüm doldurulacak. Aşağıdaki
sorular, sistemi bu raporun bulgularına göre değerlendirme çerçevesi.


  Soru                                                          Neden önemli

  Puanlama formülü neye dayanıyor: ROI mi,                      Ham ROI, kaldıraçlı kumarı ödüllendirir
  risk-ayarlı getiri mi?

  Kopya maliyetleri (kayma, gecikme, ücret,                     Dahil değilse backtest sistematik olarak
  funding) simülasyona dahil mi?                                iyimser çıkar

  Elenen/likide olan cüzdanlar geçmişte                         Tutulmuyorsa survivorship bias var
  tutuluyor mu?




                                                                                                           Page 1 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




  Soru                                                                    Neden önemli

  Seçim dönemi ile test dönemi ayrı mı (out-                              Aynı veride seçip test etmek aşırı uyum
  of-sample)?                                                             (overfitting) demek

  Forward test kağıt üzerinde mi, gerçek                                  Kağıt test gerçek dolum fiyatlarını göremez
  küçük sermayeyle mi?

  Oyun mekaniği neyi ödüllendiriyor: kazancı                              Kazancı ödüllendiren oyun risk iştahını şişirir
  mı, kurala uymayı mı?

  Çıkış/rotasyon kuralları önceden tanımlı mı?                            Sürdürülebilirliğin asıl kaynağı bu




Copytrade nasıl yapılıyor
Hyperliquid'i farklı kılan, tüm pozisyon ve işlemlerin zincir üstünde açık olması: herhangi
bir cüzdan, lider olmayı kabul etmese bile izlenebilir ve kopyalanabilir. Bu yüzden
ekosistemde üç yol öne çıkıyor.


  Yöntem                               Nasıl çalışır            Maliyet               Kontrol            Başlıca risk

  Hyperliquid vault                    USDC yatırılır,          Lider kârın           Yok; tek tek       Diğer
                                       lider havuzu             %10'unu alır;         işlem/stop         yatırımcıların
                                       yönetir                  lider en az %5        ayarlanamaz        giriş-çıkışı
                                                                pay tutmak                               pozisyonları
                                                                zorunda                                  etkiler

  Üçüncü parti                         API                      Copin: açılışta       Boyut,             API anahtarı
  platformlar                          cüzdanıyla               işlem                 kaldıraç, risk     paylaşımı; ayrı
  (Copin,                              seçilen                  büyüklüğünün          limiti ayarlanır   alt hesap
  HyperDash,                           cüzdanın                 %0,05'i + borsa                          önerilir
  WunderTrading                        işlemleri                ücreti
  vb.)                                 aynalanır

  Kendi botun (hl-                     Cüzdan                   Altyapı + borsa       Tam                Kod hatası,
  copy-core gibi                       izlenir, hedef           ücreti                                   gecikme, bakım
  açık kaynak)                         pozisyon                                                          yükü
                                       hesaplanıp
                                       IOC emirle
                                       eşitlenir


Merkezi borsalarda (Binance, Bybit, eToro) model farklı: lider platforma başvurur, platform
metrikleri gösterir ve kâr payı alır. Hyperliquid'de ise lider kopyalandığını bilmeyebilir; bu
hem özgürlük hem de "bilgi akışı tersine dönebilir" riski demek (büyük balinaların




                                                                                                                        Page 2 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




izlendiğini bilip buna göre davranması gibi).

Pozisyon boyutlandırma genelde üç şekilde yapılıyor (hl-copy-core):

 1. Özkaynak oranı: lider pozisyonu × (takipçi özkaynak / lider özkaynak). Kaldıraç birebir
     kopyalanır.
 2. Çarpan: aynı oran × k. Kaldıraç bilinçli olarak küçültülür ya da büyütülür.
 3. Sabit nominal: her işleme sabit USD. Liderin boyut değişikliklerinden etkilenmez, ama
     "güvendiği işlemde büyük oynama" sinyalini kaybeder.

Ciddi kurulumlar bunların üstüne günlük zarar limiti, sembol başına nominal limit, kaldıraç
tavanı ve izinli sembol listesi ekliyor.


Trader seçimi: metrikler ve filtreler
Deneyimli kopyacılar tek bir metriğe bakmıyor; önce kaba filtreyle eliyor, sonra risk-ayarlı
bir skorla sıralıyor, en son davranışı nitel olarak inceliyor. Kaynaklarda tekrar eden eşikler:


  Metrik                              İyi sinyal                Uyarı              Not

  Geçmiş uzunluğu                     ≥ 90 gün, tercihen        < 30 gün           Tek bir yükseliş trendinde
                                      farklı piyasa rejimleri                      kazanmak beceri kanıtı
                                                                                   değil

  Maksimum düşüş                      < %20–25                  > %40              Düşüşün süresi de önemli
  (MDD)

  Sharpe oranı                        > 1,5                     < 0,5              Kısa geçmişte çok
                                                                                   gürültülü

  Pozitif ay oranı                    > %65                     < %50              Tutarlılık göstergesi

  En kötü gün                         < %5                      > %15              Kuyruk riski

  Kazanma oranı +                     Birlikte okunmalı         Yüksek win rate,   Yüksek win rate büyük
  profit factor                                                 düşük profit       tekil zararları gizleyebilir
                                                                factor

  İşlem sayısı                        ≥ 20–30 kapanmış          Bir-iki büyük      İstatistiksel anlam için
                                      işlem                     kazanç

  Lider payı (vault)                  > %20                     %5–10 (asgari)     Çıkar uyumu


Kaynaklar: OneKey vault çerçevesi, Hyperliquid kopyalama rehberi.

Birleşik skor örneği. Açık kaynak hl-copy-core liderleri şu formülle puanlıyor; ham getiriyi
düşüş, tutarlılık ve örneklem büyüklüğüyle cezalandırması iyi bir başlangıç şablonu:



                                                                                                            Page 3 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




Skor = getiri × (1 − MDD) × (0,5 + 0,5 × tutarlılık) × min(1, işlem sayısı / 20)

Buradaki tutarlılık, dönemin eşit parçalarından (ör. 4 pencere) kaçında ücret sonrası kâr
edildiğinin oranı.

Nitel elemeler (sayılarda görünmeyen riskler):

     Martingale / zarara ekleme: zarardaki pozisyonu büyütmek uzun süre pürüzsüz bir
     özkaynak eğrisi üretir, sonra hesabı bir seferde sıfırlar.
     Stopsuz yüksek kaldıraç: Hyperliquid'de 2025'te James Wynn gibi milyar dolarlık
     pozisyonlar açan balinaların kopyalanması, likidasyonların takipçilere de taşınması
     demekti (Arkham).
     Kopyalanamaz strateji: çok kısa süreli scalping, market making veya düşük likit
     altcoinler kopyada gecikme ve kayma yüzünden aynı sonucu vermez.
     Kapasite: liderin hacmi büyüdükçe performansın bozulup bozulmadığı.


Backtest ve forward test
Copytrade backtest'i klasik strateji backtest'inden farklı: test edilen şey bir strateji değil,
bir seçim kuralı ("her ay en yüksek skorlu 5 cüzdanı kopyala"). Bu yüzden asıl soru "bu
trader iyi miydi?" değil, "bu kuralı geçmişte uygulasaydım, o gün bilmediğim gelecekte ne
kazanırdım?".


Doğru backtest için kurallar
 1. Seçim ve test dönemini ayır (walk-forward). Örneğin Ocak–Mart verisiyle lider seç,
     Nisan'da test et; sonra pencereyi kaydır. Aynı veride seçip test etmek sonucu şişirir.
 2. Geçmişteki tüm evreni kullan. Bugün liderlik tablosunda olan cüzdanlarla geçmişi test
     etmek, o gün var olup sonra batıp kaybolanları dışarıda bırakır. Hayatta kalma yanlılığı
     yatırım fonlarında yılda ~150 baz puan, hedge fonlarda geriye dönük veri ekleme
     (backfill) ile birlikte 250–300 baz puana kadar çıkıyor; kriptoda muhtemelen daha
     büyük (NakedPnL derlemesi).
 3. Kopya maliyetlerini modelle. Gecikme (lider dolumundan sonraki fiyat), kayma, taker
     ücreti, funding, platform/kâr payı. Hyperliquid'de lider limit emirle (maker) girerken
     kopyacı genelde piyasa/IOC emriyle (taker) girer.
 4. Çoklu test düzeltmesi yap. Binlerce cüzdan arasından en iyisini seçmek, salt şansla
     yüksek Sharpe bulmanı garanti eder. Deflated Sharpe Ratio (Bailey & López de Prado)
     bu seçim yanlılığını düzeltmek için geliştirildi.
 5. Rejimlere böl. Yükseliş, düşüş, yatay ve şok günleri (ör. büyük likidasyon kaskadları)
     ayrı raporla.




                                                                                          Page 4 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




Forward test nasıl yapılıyor
Forward test, seçilen liderleri gerçek zamanda, onları seçtikten sonra izlemek demek.
Pratikte iki katman var:

     Kağıt kopya (paper): sinyaller gerçek zamanlı kaydedilir, kopya fiyatı o anın emir
     defterinden hesaplanır. Maliyetsizdir, ama gerçek dolumu ve kaydırmayı tam göremez.
     Küçük sermayeyle canlı test: hedeflenen tutarın %5–10'u ile 2–4 hafta. Amaç kâr değil;
     işlemlerin beyan edilen stratejiye uyması, düşüşün tolerans içinde kalması ve yatırma/
     çekmenin beklendiği gibi çalışmasını doğrulamak (OneKey).

En değerli çıktı "kopya verimi": takipçinin gerçekleşen getirisi / liderin aynı dönemdeki
getirisi. Bu oran düşükse lider iyi olsa bile kopyalanmaya uygun değildir.

Hyperliquid'de bu iş kolaylaşıyor çünkü tüm dolumlar zincir üstünde. Copin gibi araçlar
seçilen cüzdan için tek tıkla backtest sunuyor (Copin rehberi); ancak bu tek-cüzdan
backtest'leri genelde seçim yanlılığını düzeltmiyor, çünkü cüzdanı zaten iyi göründüğü için
seçmiş oluyorsun.


Veriler ne diyor
Akademik ve sektör verileri aynı yöne işaret ediyor: liderin kendi başarısı takipçiye zayıf
taşınıyor, sosyal sıralama da risk almayı artırıyor.


  Kaynak                                               Veri                         Bulgu

  YieldFund (2025)                                     Binance, Bybit, MEXC; 90     Kopyaların %48,5'i kârlı.
                                                       gün; 100.236 kopya sonucu,   Liderlerin %97'si kendi
                                                       1.486 lider                  hesabında kârda, ama
                                                                                    yalnızca %43,6'sı takipçisine
                                                                                    kâr ettirdi. MEXC'de kopya
                                                                                    kazanma oranı %57,8
                                                                                    olmasına rağmen net takipçi
                                                                                    PnL'i −210 bin USDT.

  Apesteguia, Oechssler,                               Laboratuvar deneyi, 176      En riskli varlığı seçenler
  Weidenholzer (2019)                                  katılımcı                    kontrol grubunda %32,5,
                                                                                    kopyalama açıkça %65.
                                                                                    Kopyacıların %71'i
                                                                                    sıralamadaki 1 numarayı,
                                                                                    %88'i en riskli seçimi yapanı
                                                                                    kopyaladı.




                                                                                                             Page 5 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




  Kaynak                                               Veri                          Bulgu

  Klocke, Müller-Okesson,                              Sosyal trading aracı kurumu   Akranları kazanınca
  Hasso, Pelster (2025)                                kayıtları                     yatırımcılar daha çok işlem
                                                                                     yapıyor; bu da daha düşük
                                                                                     performans ve daha yüksek
                                                                                     oynaklık getiriyor.

  Deng, Yang, Pelster, Tan                             Büyük sosyal trading ağı      Lider-takipçi bağları hızla
  (2024)                                                                             kopuyor. Bağ kurarken
                                                                                     performans ve demografi,
                                                                                     bağı sürdürürken performans
                                                                                     ve iletişim belirleyici.


Bu tabloda üç ders var:

     Kazanma oranı yanıltır. MEXC örneğinde olduğu gibi sık küçük kazanç, seyrek büyük
     zararla net negatife dönebiliyor.
     "1 numarayı kopyala" içgüdüsü riski seçer. Sıralamanın tepesi çoğunlukla en çok risk
     alanın en şanslı dönemidir.
     Takipçiler sık değiştiriyor. Sık lider değiştirmek, kötü dönemde çıkıp iyi dönemi kaçırma
     (çift taraflı zamanlama hatası) riskini artırır; rotasyonun kurallara bağlı olması bu
     yüzden önemli.

Not: YieldFund verisi olay ağırlıklı ve ücret/funding/kaymayı ayrıştırmıyor; Apesteguia
deneyi öğrenci örneklemli. Rakamlar yön gösterir, kesin ölçü değildir.


Sürdürülebilirlik: portföy, rotasyon, çıkış
Uzun vadede ayakta kalan kopyacılar liderleri bir "fon portföyü" gibi yönetiyor:
çeşitlendiriyor, sınırlıyor, düzenli yeniden puanlıyor ve çıkışı duyguya değil kurala bağlıyor.

1. Lider portföyü

     3–8 lider; farklı stil (trend takipçisi, swing, düşük kaldıraçlı makro), farklı enstrüman ve
     tercihen düşük korelasyon. Aynı anda BTC long açan 5 lider, tek bir büyük pozisyondur.
     Lider başına sermaye tavanı (ör. toplamın %20–25'i) ve toplam açık nominal tavanı.
     Ağırlık: eşit ağırlık ya da ters oynaklık (daha oynak lidere daha az sermaye). Geçmiş
     getiriye göre ağırlıklandırmak, şansı ödüllendirir.

2. Hesap seviyesinde koruma

     Günlük zarar limiti: aşılınca tüm kopyalar durur.
     Kaldıraç tavanı ve izinli sembol listesi (likiditesi düşük altcoinler hariç).




                                                                                                             Page 6 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




     Kopya için ayrı alt hesap/API cüzdanı; ana fonlar ayrı.

3. Önceden yazılmış çıkış kuralları (örnek kalibrasyon, kendi verine göre ayarlanmalı)

     Lideri takip ettiğin dönemde düşüş, backtest'teki maksimum düşüşün ~1,5 katını aşarsa
     çık.
     Stil değişimi (stil kayması): kaldıraç, işlem sıklığı ya da enstrüman belirgin şekilde
     değiştiğinde yeniden değerlendir.
     Zarara ekleme / martingale davranışı görüldüğünde anında çık.
     Kopya verimi belirli bir eşiğin (ör. %60) altında kalırsa çık.
     Lider hesap/vault'tan sermaye çekiyorsa ya da vault'taki payı azalıyorsa uyarı kabul et.

4. Rotasyon ritmi

     Skorları haftalık güncelle, portföyü aylık dengele. Daha sık değiştirmek zamanlama
     hatasını ve maliyeti artırır.
     Yeni aday her zaman önce forward test kuyruğuna girer; doğrudan tam sermayeye
     geçmez.
     Çıkarılan liderleri de kaydet; aksi halde kendi verin de hayatta kalma yanlılığına uğrar.

5. Platform ve karşı taraf riski

Vault'larda diğer yatırımcıların toplu çıkışı, marjin yetmezse pozisyonların %20'lik dilimlerle
kapatılmasına yol açabilir (Hyperliquid dokümanı). Üçüncü parti araçlarda API anahtarı
güvenliği ve aracın kesintiye uğraması ayrı risklerdir.


Oyunlaştırma: faydalar ve tuzaklar
Oyunlaştırma, ne ödüllendirdiğine göre ya disiplin aracı ya da risk hızlandırıcısı olur.
Araştırmalar sıralama ve akran görünürlüğünün risk almayı ve işlem sıklığını artırdığını
gösteriyor (Apesteguia vd., Klocke vd.).


  Mekanik                    İyi tasarım                                  Kötü tasarım

  Puan / XP                  Kural uyumu, risk-ayarlı getiri, düşük       Ham ROI veya PnL
                             düşüş

  Lig /                      Minimum süre ve işlem sayısı şartı,          Kısa dönem, sadece hayatta
  sıralama                   elenenler görünür                            kalanlar

  Seviye                     Forward test'i geçen lidere kademeli         Kazanan liderde hemen
  atlama                     sermaye                                      sermayeyi katlama

  Rozet /                    "30 gün kural ihlali yok", "çıkış kuralını   "En yüksek günlük kazanç"
  başarı                     uyguladı"




                                                                                                       Page 7 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




  Mekanik                    İyi tasarım                                 Kötü tasarım

  "Can" / ceza               Düşüş limiti aşılınca lider oyundan düşer   Ceza yok, sadece ödül


Kendi sistemini kurarken sınanacak soru: "Bu oyunda en yüksek puanı, beceri mi yoksa
en büyük riski almak mı getiriyor?" Eğer ikincisiyse, oyun kaldıraçlı kumarı seçecek bir
filtreye dönüşür.


Uygulanabilir çerçeve
Aşağıdaki döngü, araştırmadaki en iyi uygulamaları tek bir sürece topluyor: her lider önce
verisiyle, sonra küçük sermayeyle kendini kanıtlıyor; çıkış kuralı tetiklenince yerini
kuyruktaki yeni adaya bırakıyor.




lider seçim ve yönetim döngüsü · 6 adım

Kurulum için kontrol listesi:

     Geçmiş evreni sabitle: elenen ve likide olan cüzdanları da sakla
     Skor formülünü risk-ayarlı yaz (getiri × düşüş × tutarlılık × örneklem)
     Backtest'e gecikme, kayma, taker ücreti, funding ve kâr payını ekle
     Seçim ve test dönemlerini ayır (walk-forward)
     Forward test için sermaye oranı ve süreyi belirle
     Lider başına tavan, günlük zarar limiti ve kaldıraç tavanını tanımla
     Çıkış kurallarını işlem başlamadan yaz
     Haftalık skor güncelleme ve aylık dengeleme takvimini kur




                                                                                                 Page 8 of 9
Copytrade, Backtest ve Forward Test: Dünyada Nasıl Yapılıyor?




Kaynaklar
     Is Copy Trading Profitable? A 90-Day, Multi-Exchange Study — YieldFund
     Copy trading (deney) — Apesteguia, Oechssler, Weidenholzer
     The impact of peer returns in social trading — Klocke vd., 2025
     Social Trading, Communication, and Networks — Deng vd., 2024
     The Deflated Sharpe Ratio — Bailey & López de Prado
     Survivorship bias in trader rankings — NakedPnL
     For vault leaders — Hyperliquid Docs
     Hyperliquid vault selection framework — OneKey
     Hyperliquid Copy Trading Guide
     Copin analyser guide — CoinCodeCap
     hl-copy-core — GitHub
     James Wynn out of the market — Arkham

Bu rapor bilgi amaçlıdır, yatırım tavsiyesi değildir.




                                                                              Page 9 of 9
```
