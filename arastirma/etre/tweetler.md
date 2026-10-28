# Etre V2 — tweet metinleri (kullanıcının aktardığı, 2026-10-28)

Kaynak: @yavruetre_tr. Bağlantılar: status/2113004611678470294, 2115194215470678180, 2115199051444724110, 2115167944158167246.
Metinler kullanıcı tarafından yapıştırıldı; hangi metnin hangi bağlantıya ait olduğu doğrulanmadı.

## 1
Claude ile 2 aydır geliştirdiğim bir kripto token kopyalama botu var. V1'i 1.5 ay kadar kullandım. Kâra geçmesine rağmen sonrasında
üst üste katmanlar yazdığım için eski motorla yeni motor birbirine karıştı. V2'yi sıfırdan yazdırdım, dedim yazmışken buna bir de ofis
vereyim, içinde çalışan avatarlar olsun. 200$ kasa ile simülasyona başladım ve neredeyse her akşam 1-2 saat geliştirmeye devam ediyorum.

1- Her odanın ayrı bir işlevi var. Arşivci, mum grafikleri dahil tüm veriyi sürekli analiz ediyor ve saklıyor. 2 ayda 16 GB kadar veri
birikti. Lab'lar arkaplanda sürekli trader takibi yapıyor, analizlerini tamamlıyor. Sekreter kuralları not alıyor. Patron sadece gelip
puro içip milleti gazlıyor gibi.
2- İşlemler dahil her şey otomatik. Olay şu, iki ayrı bölümde 500 kişiyi sürekli takip ediyor. Bunları anlık işlemlerine, cüzdan
geçmişine, token tutma süresine vs. gibi 20 farklı alanda puanlayıp en iyi 100 kişiyi aday bölümüne alıyor. Oradan da farklı bir
filtreden geçirip 10 ila 20 kişiyi ana trader olarak belirliyor.
3- Bu 500 kişi de, 100 kişi de, 10-20 kişi de puanlarına göre sürekli güncelleniyor ve bot, ana trader odasına geçen kişilerin
işlemlerini birebir açıyor. (V1'i bir süre canlıda kullandım, işlem açma ve kapatmadaki sorunların tamamı giderildi, birebir takip
edebiliyor.)
4- -%30'da otomatik stop var spotta. İşlem 24 saati geçtiyse -%20'de, 18 saati geçtiyse -%15'te ya da tam tersi kâr durumunda işlemi
kapatıyor.
5- Cüzdan dahil her şey programın içinde, ayrı bir yerde bir şey yapmama gerek yok.
6- Ayrıca ofis kısmında her kişinin 100 farklı repliği var. Patron sabah 8, akşam 5 çalışıyor. Gün içinde rastgele repliklere göre
olaylar oluyor ve bot, anın ekran görüntüsünü alıp Telegram'a mesaj atıyor.
7- Bu eğlenceli görüntünün arkasında gerçekten ciddi bir emek ve planlanmış bir matematiksel bir sistem var. İşlem girişi trader'ın
fiyatının %1 üstünde ya da altındaysa girmemek gibi basit kuralları da var. Ya da ne bileyim traderın açtığı işlemin büyüklüğüne göre
benim işlemleri belirliyor, kasaya göre oranlı hareket ediyor.

Yapay zekaya yap dediğinizde yapıyor ama kendi bildiğine, standart duruma göre yapıyor. Ama her kuralı tek tek kendiniz düşünüp
yazarsanız, tam olarak onu verebiliyor size. Şimdilik V2 başladı, güncellemeleri paylaşırım. 1 hafta kadar simülasyonda kullandıktan
sonra yine canlıya geçmeyi planlıyorum, tabii ki küçük miktarlarla (200$).

## 2
Ben öyle yapmadım, 1000 adet trader seçiyor onları kendi aralarında puanlıyor ve işlemlerini kopyalıyor, oradan 100 adet aday seçiyor,
daha derin takip ediyor. En son da ana odaya 20 kişi alıyor, kötüleşirse çıkarıyor. Kaldıraç için de spot için de aynı şekilde.
2 aydır geliştirmeye devam ediyorum, sıfırdan tekrar başlattım şimdi. Para kaybettirmiyor en azından, ben kendim işlem yapıyor olsam
50 defa batmıştım :).

## 3
Bana en çok faydası olan konu bir arşiv sistemi kurmak oldu, tüm işlemleri, giriş çıkışları, mum hareketlerini, veriye çevirebilecek
tüm detayları ileride tekrar analiz etmesi kolay olacak şekilde, fazla yer kaplamayacak şekilde kaydeden bir arşiv sistemi kurup
geliştirdim. Çünkü trading konusunda evet yapay zeka düşünüyor bir şeyler ama elinde veri olur ve analiz ederse daha iyi sistemler
kurabiliyor.
