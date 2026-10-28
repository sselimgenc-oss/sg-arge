# Ham metin (PDF'ten çıkarıldı; kişi adı çıkarıldı) — rapor: codex

```text
  Copy Trading: Trader Seçimi, Backtest ve İleri
  Test
  Hyperliquid benzeri platformlarda sürdürülebilir kopyalama sistemi üzerine araştırma ve iki X
  paylaşımının değerlendirmesi · 28 Ekim 2026

  Yönetici özeti. Paylaşımlardaki yaklaşım; geniş bir trader havuzunu izlemek, adayları puanlamak, önce sanal
  işlemlerle sınamak ve yalnızca uygun bulunanları kopyalamak. Fikir güçlü bir araştırma çerçevesi sunuyor. Ancak
  görünen ekranlar kârlılık veya sürdürülebilirlik kanıtı değil. Karar verdiren ölçü, traderın kendi getirisi değil,
  takipçinin gecikme ve tüm maliyetler sonrasındaki gerçekleşen net getirisidir.


  1. İki paylaşımın analizi
  21 Ekim paylaşımında geliştirici yaklaşık 500 cüzdanı izlediğini, 20 ölçütle 100 adayı, ardından 10-20 ana traderı
  seçtiğini söylüyor. Havuz sürekli güncelleniyor. Spot stop ve süreye bağlı çıkış, giriş fiyatından %1’den fazla
  sapınca işlemi atlama ve kasa büyüklüğüne göre pozisyon ayarlama kuralları tarif ediliyor. V1’in kâra geçtiği ifade
  ediliyor; bağımsız işlem dökümü paylaşılmıyor.

  İlk iki görselde oyunlaştırılmış ofis, spot ve kaldıraç odaları, kasa özetleri ve “kohort/kontrol” keşif ekranı var.
  Karşılaştırma ekranındaki görünen örnek sayıları n=0 olduğundan yüzdeler deneysel üstünlük göstermez. Kasa
  değerleri de simülasyon bağlamında okunmalıdır.

  28 Ekim paylaşımında araştırma, gölge kopyalama, gerçek işlem, finans, risk, gözlem, kayıt ve bildirim görevleri
  ayrı “ajanlara” dağıtılıyor. Görsel, botun hâlen simülasyon modunda olduğunu ve önceden yazılmış ileri test
  kuralları geçilmeden gerçek paraya geçilmeyeceğini belirtiyor. Bu iyi bir disiplin niyeti; yayımlanmış ileri test
  sonucu değildir.


  2. Traderlar dünyada nasıl seçiliyor?
  Platformlar ilk elemede farklı dönem getirileri, kâr/zarar, maksimum düşüş, Sharpe oranı, işlem süresi ve takipçi
  sonuçlarını sunuyor. Binance’in futures kopyalama filtreleri 7, 30, 90 ve 180 günlük dönemleri ve bu risk ölçülerini
  içeriyor. Yalnızca sıralama tablosunu kullanmak yetersizdir. Binance filtreleri

    Kriter                                   Sorulacak soru

    Getiri kalitesi                          Kâr birkaç sıra dışı işleme mi bağlı; farklı piyasa koşullarında sürüyor mu?

    Açık risk                                Kapanmış işlemler iyi görünürken büyük zarardaki pozisyonlar açık mı?

    Kopyalanabilirlik                        Sinyalden sonra yeterli likiditeyle benzer fiyat alınabiliyor mu?

    Davranış                                 Takipçi artınca kaldıraç veya işlem sıklığı değişiyor mu?

    Çeşitlendirme                            Seçilen traderlar aynı varlık ve piyasa yönünde mi yoğunlaşıyor?


  Bir kripto sosyal işlem platformundaki rastgele saha deneyi, takipçi sayısı artan traderların daha sık ve daha
  yüksek kaldıraçla işlem yapıp daha kötü performans gösterme eğilimini buluyor. Bu her platform için kesin hüküm
  değildir; popülerliği beceri puanı saymamak için uyarıdır. Xu ve çalışma arkadaşları

  Çıkarım: 500 → 100 → 10-20 hunisi ancak puanlama kopyalanabilirlik, açık risk ve takip edildikten sonraki net
  sonucu da içeriyorsa değerlidir. Geçmiş getiri tek başına şanslı veya aşırı risk alan cüzdanları öne çıkarabilir.




Copy trading araştırma raporu · 28.10.2026                                                                                  1
  3. Backtest ve ileri test nasıl kurulmalı?
  Backtest, yalnızca geçmişte o anda bilinebilen verilerle kuralların yeniden oynatılmasıdır. İleri test, bugün
  dondurulan kuralların bundan sonra oluşacak işlemlerde sınanmasıdır. Bugün başarılı olduğu bilinen cüzdanları
  seçip eski işlemlerini test etmek geleceğin bilgisini geçmişe sızdırır. Çok sayıda kural deneyip en iyi grafiği
  seçmek de sonucu şişirir. Backtest aşırı uyumu araştırması

  • Her cüzdanın keşif zamanını ve her sinyalin ilk görüldüğü zamanı sakla; geçmiş simülasyonda yalnızca o anda
  bilinen adayları kullan.

  • Puanlama ağırlıklarını, giriş/çıkış kurallarını ve yeniden seçim takvimini ileri test başlamadan dondur;
  değişiklikleri yeni test sürümü say.

  • Gölge emirleri traderın işlem fiyatıyla değil, botun gecikmeden sonra karşılaşacağı emir defteri ve
  gerçekleşebilir büyüklükle fiyatla.

  • Ücret, spread, kayma, funding ve başarısız/atlanmış emirleri net sonuca kat; farklı piyasa rejimlerinde ve kontrol
  grubuna karşı ölç.

  • Küçük canlı aşamada her sanal emir ile gerçek gerçekleşmeyi eşleştir; kopyalama açığı ve hata oranı sınırları
  aşılırsa sistemi durdur.

  Hyperliquid kullanıcı dolumlarını ve anlık akışları belgeler, fakat bazı API sorgularının geçmiş işlem sınırları
  vardır. Tarihsel veri arşivinde gecikme veya eksik veri olabileceğini de belirtir. Toplanan veri miktarı, tek başına
  tarihsel test kalitesini göstermez. API · Tarihsel veri


  4. Sürdürülebilirlik: trader getirisi ile takipçi getirisi
  Takipçi aynı fiyatı ve aynı sonucu otomatik elde etmez. Düşük likidite, gecikme, emir büyüklüğü veya fiyat
  kayması nedeniyle emir daha kötü fiyattan gerçekleşebilir ya da atlanabilir. Tweetlerdeki %1 giriş sınırı bu sorunu
  hedefliyor; çıkış likiditesi ve gerçekleşmeyen işlemler de ayrıca ölçülmeli. Binance belgeleri bu yürütme farklarını
  açıkça listeliyor. Spot kopyalama · Futures sorunları

  Spot için %30 stop, 200 dolarlık kasanın tamamı tek pozisyondaysa teorik olarak 60 dolar kayıp anlamına gelir;
  gerçek çıkış daha kötü olabilir. Pozisyon kasanın %5’i ise aynı fiyat hareketinin kasa etkisi yaklaşık %1,5 olur. Bu
  nedenle stop fiyatı kadar pozisyon payı ve eşzamanlı toplam risk önemlidir. Kaldıraçta funding, teminat ve mark
  fiyatına dayalı likidasyon ayrıca yönetilir. Hyperliquid likidasyon

  Günlük izlenecek dört sonuç: (1) kaynak traderın net işlemleri, (2) gerçekleşebilir fiyatlarla gölge takipçi, (3)
  gerçek takipçi, (4) atlanan/başarısız işlemler. Bu kayıtlar kopyalama açığını gösterir. Ek olarak maksimum düşüş,
  toparlanma süresi, en kötü gün, açık zarar, tek trader/token yoğunluğu, ortak yön riski ve kural sürümleri
  izlenmelidir.

  Sonuç. Projenin güçlü yanı oyun arayüzünden çok dinamik trader havuzu, gölge takip ve risk rollerini
  birleştirmesi. İddianın kanıtı; önceden dondurulmuş kurallarla, yeterli işlem sayısında, maliyetler sonrası takipçi
  sonucunun ve kontrol grubuna göre farkının gösterilmesidir. Paylaşılan görsellerde bu kanıt henüz yoktur.




Copy trading araştırma raporu · 28.10.2026                                                                               2
```
