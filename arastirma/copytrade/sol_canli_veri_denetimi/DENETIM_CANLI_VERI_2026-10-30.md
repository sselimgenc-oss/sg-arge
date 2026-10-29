# Canlı izleme verisi — bağımsız karşılaştırma

Denetim: 30 Ekim 2026, yaklaşık 00:45–00:52 Türkiye saati. Bütün ayrıntı zamanları aşağıda **UTC** olarak verilir. Sadece herkese açık, salt okunur sorgular kullanıldı. Uygulama kodu, eşikler ve canlı veriler değiştirilmedi.

**Sonuç: kasa ekranındaki sayılara bütün olarak “doğru sanal portföy muhasebesi” onayı veremiyorum.** Beş trader’ın mevcut pozisyonlarının coin/yön/kaldıraç alanları API ile örtüşüyor. Ancak sanal kasa açık işlem tablosu başka bir portföyü gösteriyor, olay listesi günlük istatistik için eksik, kontrolün bir üyesi hesap dışında ve geçersiz veriler bazı toplamlara geçerli gibi katılıyor. Üç kapanan işlemin fiyat zinciri hesaplandı; sadece O08 için toplam hesap getirisini yaklaşık olarak sınamak mümkün oldu. Diğer iki trader’ın toplam getirisi **doğrulanamadı**.

## 1. En önemli beş bulgu

| No | Önem | Bulgu ve ölçülen etki | Öneri |
|---|---|---|---|
| 1 | Yüksek | Kasa tablosunun K/Z toplamı **+2.968,02 $**, sanal kopyaların açık K/Z toplamı **−64,16 $**. Tablo trader’ın bütün mevcut pozisyonlarını güncel hesap değeriyle ölçekliyor; defter ise t0 sonrası, gecikmeli kopya pozisyonlarını ölçüyor. Satır yüzdesi de coine değil trader’ın bütün sanal açık K/Z’sine ait. | Tabloyu sanal defterin açık lotlarından üret; sabit kopya paydasını, miktarı, gecikmeli giriş fiyatını ve aynı işaretleme zamanını yayımla. Trader görünümünü ayrıca adlandır. |
| 2 | Yüksek | 200 olay **19:59:16–20:21:28**, sadece **22 dakika 12 saniye**. Listede 13 oda olayı var; bağımsız emir gruplamasıyla aynı gün 733 oda işlem olayı türetildi, 722 kimlik listede yok. “Son 24 saat 2 açılış / 0 kapanış” tam günlük sayı değil. | Günlük sayaçları kesilmemiş olay arşivinden üret; 200 satırlık sunum listesinden hesaplama. Tamlık ve pencere başlangıcı alanlarını ekle. |
| 3 | Yüksek | Kontrol aslında 18 üyeli. `E01`, `kol=elle`, `kollar=[elle,kontrol]` olduğu için pano 17 sayıyor. Gösterilen kontrol getirisi **%1,25079**, üyelikle doğru ortalama **%1,18459**; oda−kontrol farkı **−8,03059** yerine **−7,96438 yüzde puan**. | Üyelik hesaplarında `kollar` kullan; ana etiket ile deney kolunu ayır. Sabit referans ölçümünü de aynı üyelik sözleşmesiyle hesapla. |
| 4 | Yüksek | İstenen 7 adres dışında `K08` ve `O17` de geçersiz: toplam **9/61**. O17’nin 16:23 verisi 20:21 dosyasında taşınıyor. B17’de API verisi güçlü biçimde mevcutken bir eksik mum bütün trader’ı 1.000 $ yer tutucuya düşürüyor. Geçersiz üyeler kasa/toplamlarda dışlanmıyor veya eksik kapsam belirtilmiyor. | Geçerli/eksik/eski kapsamını toplamların yanında göster; eksik fiyatı açık durum olarak taşı; kâr/zararı sıfır veya bakiye 1.000 kabul ederek sessizce birleştirme. |
| 5 | Orta | “Yetim” O02/LITE ve O10/COPPER için API’de gerçekten kapalı. Fakat bunun kaçırılmış kapanış mı, borsa uzlaşması mı, eski geçmişin yetersizliği mi olduğu doğrulanamadı. Üstelik bu tarihsel trader mutabakatı t0 sonrası sanal pozisyonla aynı şey değil. O11 artık yeşil; O15 sarı hesap sıçraması. | Mutabakat alarmını “trader geçmişi” ve “sanal defter” olarak ayır; kapanış/uzlaşma kaynağını sakla. Hesap sıçramasını yatırma/çekme kanıtı olmadan teşhis olarak sunma. |

Kanıtlar: `durum.json`, `pano_gozlem.json`, `hesap_ozeti.json`, pozisyon ve olay CSV’leri; kod kanıtları aşağıda. Büyük hesap farkları eşzamanlı olmayan gözlemlerdir; tek başlarına motor hatası diye değerlendirilmemiştir.

## 2. Kaynak ve zaman sınırı

| Kaynak | Sabitlenen zaman / durum |
|---|---|
| İzleme dosyası | `uretildi=2026-10-29T20:21:28.440213Z`; 61 trader, 200 olay |
| Hyperliquid ana sorguları | `2026-10-29T21:45:58–21:46:34Z`; bütün mevcut perp DEX’ler `perpDexs` ile keşfedildi; beş oda trader’ı ve geçersiz adresler sorgulandı |
| Pano gözlemi | `2026-10-29T21:46:44.312Z`; tarayıcının okuduğu CT nesnesi sabitlenen `durum.json` ile **tam eşit** |
| Snapshot yaşı | Pano yakalandığında **85 dakika 16 saniye**; ekranda yuvarlanmış “1 sa önce” |
| O17 ve K08 | `gecerli=false`, son başarılı veri `16:23:32Z`; pano yakalandığında **5 saat 23 dakika** eski |

`uretildi` motorun **koşu başlangıcında** sabitleniyor; her trader’a da aynı zaman yazılıyor (`motor.py:694–695`, `679`, `729`). Gerçek API okuma/publish zamanı değildir. Son işaretlerin çoğu 20:21; O17 16:23. Global tazelik etiketi tek başına üyelerin tazeliğini anlatmıyor.

Bugünkü API durumu ile 85 dakika önceki snapshot’ın hesap değeri birebir eşit olmak zorunda değil. Geçmiş `clearinghouseState` sorgusu olmadığı için o andaki tam hesap değerlerini **doğrulanamadı** olarak bırakıyorum. Bu sınır özellikle O01/O11/O15 için önemli.

Tarayıcı bu ortamın proxy sertifikasını tanımadı. Görseller gerçek yayımlanmış sayfadan alındı; istekler TLS doğrulaması yapan `curl` üzerinden tarayıcıya iletildi. Örnek veri enjekte edilmedi. Pano kaynak metni `pano.html`, okunan veri ve ekran metinleri `pano_gozlem.json` içindedir. Taşıma ayrıntısı `pano.cjs` içindedir; 404 yan kaynak yanıtlarının bu aktarımda 200 gövde olarak iletilmesi nedeniyle yan kaynakların HTTP hata sunumu bu yöntemle doğrulanmış sayılmaz. Ana CT verisinin eşitliği ayrıca kontrol edildi.

## 3. Pozisyon ve kaldıraç doğruluğu

### Beş adresin hesap toplamı

Hesap = ana perp + bütün HIP-3 DEX `marginSummary.accountValue` toplamı. Sayılar dolar; API sağ sütunu yaklaşık 85 dakika daha yenidir.

| Trader | Dosya hesap değeri | API hesap değeri | Fark | Dosya/API açık coin | API etkin kaldıraç |
|---|---:|---:|---:|---:|---:|
| O01 | 10.801,68 | 14.609,37 | +%35,25 | 3 / 3 | 10,73x |
| O02 | 30.654,18 | 30.308,63 | −%1,13 | 1 / 1 | 6,92x |
| O10 | 13.628,84 | 12.803,25 | −%6,06 | 2 / 2 | 3,42x |
| O11 | 61.449,60 | 73.159,10 | +%19,06 | 1 / 1 | 4,85x |
| O15 | 79.060,38 | 48.476,68 | −%38,68 | 6 / 6 | 8,51x |

“Etkin kaldıraç” = bütün pozisyonların mutlak nosyoneli / hesap değeri. Coin yanındaki 20x/40x ise API’nin `position.leverage.value` ayarıdır; ikisi aynı ölçü değildir. Beş trader’ın **13 coin satırında yön ve kaldıraç ayarı örtüşüyor**. “40x” özelinde bütün traderlar denetlenmedi; genelleme yapılmıyor.

### Coin başına gözlem

| Trader / coin | Yön (iki kaynak) | Kaldıraç (iki kaynak) | Dosya büyüklüğü $ | API büyüklüğü $ |
|---|---|---:|---:|---:|
| O01 NEAR | satış | 10x | 38.307,02 | 36.914,59 |
| O01 SOL | satış | 20x | 19.488,72 | 70.792,02 |
| O01 xyz:STRC | satış | 10x | 49.026,78 | 49.002,69 |
| O02 xyz:GOLD | alış | 7x | 209.980,07 | 209.635,84 |
| O10 xyz:KR200 | satış | 3x | 67,62 | 67,21 |
| O10 xyz:SKHX | alış | 4x | 44.559,80 | 43.715,65 |
| O11 HYPE | alış | 10x | 295.602,42 | 354.503,26 |
| O15 ETH | satış | 20x | 635.879,75 | 318.094,00 |
| O15 LIT | satış | 5x | 30,25 | 29,67 |
| O15 WLFI | satış | 5x | 10.227,40 | 10.084,47 |
| O15 XLM | satış | 5x | 42.611,63 | 41.960,64 |
| O15 XRP | satış | 20x | 33.075,01 | 32.806,49 |
| O15 ZRO | alış | 5x | 9.984,60 | 9.672,60 |

Büyük farkların bir kısmı sonradan gerçekleşen dolumlarla açıklanıyor: snapshot sonrası API state zamanına kadar O01 SOL miktarı yaklaşık **−196,39 → −727,40**, O11 HYPE **3.184,17 → 3.809,61**, O15 ETH **−275 → −140**. Bu miktarlar state’ten sonraki dolumları geriye çıkararak hesaplandı (`*_sonraki_dolum.json`). Dolayısıyla O15’in dolar büyüklüğündeki yarılanmayı tek başına hatalı veri diye yorumlamıyorum. Aynı andaki bütün fiyatlar ve hesap değerleri **doğrulanamadı**.

### Yetim kırmızıları gerçek mi?

| Trader | Sabitlenen dosyadaki mutabakat | Bağımsız API | Karar |
|---|---|---|---|
| O02 | xyz:LITE defter +200, borsa 0; kırmızı | bütün DEX’lerde LITE açık değil; sadece GOLD açık. Eski API dolumunda 83,939 + 116,061 = 200 LITE görülüyor; t0 sonrası hiç dolum yok | **Açık tarihsel kayıt / kapalı borsa farkı gerçek.** Kapanışın neden kayda girmediği doğrulanamadı. Sanal kopyada LITE yetimi var denemez. |
| O10 | xyz:COPPER defter −6.000, borsa 0; kırmızı | bütün DEX’lerde COPPER kapalı; SKHX ve KR200 açık | Borsada kapalı olduğu doğrulandı. Defterin −6.000’lik son durumunun kaynağı ve kapanış olayı **doğrulanamadı**. |
| O11 | yeşil; yetim 0 | HYPE açık, başka açık coin yok | İstekteki “yetim kırmızısı” bu snapshot’ta yok. |
| O15 | sarı; yetim 0; hesap sıçraması %83,63 | altı coin açık | Yetim alarmı yok. Sarı sıçrama gözlemi, yatırma/çekme kanıtı değil. |

O10/O11/O15 için 90 günlük ilk dolum sorgusu 2.000 satır tavanına ulaştı; bunu tam tarihçe diye kullanmadım. Ek bir haftalık O10 sorgusu 1.759 satır verdi ama COPPER kapanışı yok. O02’nin 90 günlük sorgusu 1.591 satırla sonlandı; LITE kapanış dolumu bulunamadı. Ledger yanıtlarında da kapanışı açıklayan açık bir uzlaşma kanıtı yok. “Yanlış alarm kesin” veya “çıkış sinyali kesin kaçırılmış” demek için yeterli kanıt yok.

## 4. Üç kapanan işlemin elle fiyat zinciri

Motorun sonucunu çağırmadan API dolum miktarlarını ve API 1 dakikalık mum açılışlarını topladım. Dolumun zamanı + 30 dakika, sonraki tam dakikaya yuvarlandı. Her iki tarafta **%0,045 taker + %0,05 kayma = %0,095** uygulandı. Aynı milisaniyedeki dolumların API sırası korundu; giriş ve çıkış toplam miktarlarının eşitliği denetlendi. Kayma ayrıca ikinci kez fiyata eklenmedi. Üç örnek de gün içi; **2 saatlik swing örneği ayrıca doğrulanmadı**.

| Trader / son tam tur | Dolum sayısı / miktar | Gecikmeli giriş / çıkış (UTC) | Ağırlıklı fiyat giriş → çıkış | Brüt $ | Maliyet $ | Aralıktaki trader funding $ | Net $ / nosyonel getiri |
|---|---|---|---|---:|---:|---:|---:|
| O08 HYPE alış | 48 / 420,39 | 11:16 → 11:27 | 87,18 → 86,595 | −245,92815 | 69,40061 | 0 | **−315,32876 / −%0,86039** |
| O05 kPEPE satış | 48 / 8.321.063 | 18:45 → 19:43 | 0,005325 → 0,005282 | +357,80571 | 83,84844 | +0,548358 | **+274,50563 / +%0,61952** |
| O11 ZEC alış | 176 / 116,04 | ilk 16:04 → son 17:08 | 1.354,00172 → 1.345,86029 | −944,73200 | 297,62739 | 0 | **−1.242,35939 / −%0,79072** |

Örnek elle işlem: O08 `420,39 × (86,595 − 87,18) = −245,92815`; giriş + çıkış nosyoneli üzerinden `× 0,00095 = 69,40061`; net `−315,32876`.

| Trader | 1.000 $ ölçeğinde yaklaşık kontrol | Dosyada toplam sanal getiri | ±%20 sonucu |
|---|---|---|---|
| O08 | T0 öncesi en son halka açık perp hesap değeri 56.975,84 $ ile tur **−5,53 $** | **−5,38 $**; açık K/Z 0. Yeni BTC açılışı henüz 30 dk olgunlaşmamış | **Yaklaşık geçiyor:** büyüklük farkı yaklaşık %2,84; işaret aynı. Sabit motor paydasının birebir doğrulaması değil. |
| O05 | Aynı yaklaşımda son tur yaklaşık **+3,95 $** | Portföy toplamı **−24,18 $**; başka coinler ve açık lotlar var | **Doğrulanamadı:** son turu toplam portföyle eşitlemek yanlış. İşlem neti bağımsız hesaplandı, portföy onayı verilmedi. |
| O11 | Son ZEC turu zarar; önceden kalmış 9.300,94 $ payda bugünkü pozisyon boyutu için güvenilir ölçek sağlamıyor | Portföy toplamı **+163,29 $**; gerçekleşmiş −26,05 $, açık +189,34 $ | **Doğrulanamadı:** açık HYPE ve diğer işlemler toplamı değiştiriyor; tur zararı toplamın pozitif olmasına aykırı değil. |

Önemli sınır: motorun ilk okumada sabitlediği `kopya_paydasi` halka açık `durum.json` içinde yok (`motor.py:636`, `650`). `motor.json` URL’si 404; artık R2’de tutuluyor. Tam yeniden hesaplamayı onaylamak için sabit payda, bütün sanal lotlar ve ilgili işaretleme fiyatlarının yayımlanması gerekiyor. O05 funding’i trader’ın aynı coin/aralık ödemesidir; her sanal lota doğru dağıtıldığı ayrıca doğrulanmadı. Tam sonuç JSON’u bütün dolum/fiyat bacaklarıyla `islem_saglama.json` içindedir.

Ek sağlama uyarıları: O10 sanal bakiye **−52,87 $** (getiri −%105,29); negatif sanal bakiye için model davranışı ve bu büyük kaybın coin bazında kökü ayrıca sağlanmalı. O04’te **2 eksik işaret** açıkça raporlanıyor. Bunlar “kesin yanlış hesap” kanıtı değil; kasa için güvenilir toplam onayı vermeyi engelleyen açık maddeler.

## 5. Veri gelmeyen adresler

Bütün mevcut perp DEX’leri ayrıca sorgulandı; yalnız ana borsaya bakılıp HIP-3 yok sayılmadı. Sayılan dolumlar T0=29 Ekim 00:00 UTC ile snapshot zamanı arasındadır.

| Trader | Perp hesap / açık coin | Pencere dolumu | Başka veri var mı? | Boşluğun kanıtlı / olası açıklaması |
|---|---|---:|---|---|
| K02 | 0 $ / 0 | 0 | Spot USDC yaklaşık 505.666 $; `allTime` pozitif | API boş değil; mevcut perp hesap sıfır. Motor pozitif perp hesap şartında duruyor. |
| K06 | 0 $ / 0 | 0 | Spot USDC yaklaşık 139.480 $; `allTime` pozitif | Aynı pozitif perp hesap şartı. |
| K09 | 0 $ / 0 | 0 | Spot USDC yaklaşık 50.610 $; `allTime` pozitif | Aynı şart; geçmiş perp hesap değeri de var. |
| K11 | 0 $ / 0 | **333** | xyz:CL dolumları, spot USDC yaklaşık 5,26 milyon $ | “Hiç veri yok” yanlış: işlem verisi var, güncel perp hesabı kapanmış/boş. Motor güncel sıfır hesapta sonucu üretmiyor. Para hareketinin kesin nedeni doğrulanamadı. |
| B02 | 0 $ / 0 | 0 | Spot bakiyeler, pozitif `allTime`; `perpAllTime` son değer 0 | Dosyadaki hata t0 için pozitif hesap bulunamaması. Spot varlığı perp kopyalama için uygun payda olduğunu kanıtlamaz. |
| B07 | 0 $ / 0 | 0 | Spot bakiyeler, pozitif `allTime`; `perpAllTime` son değer 0 | Aynı t0 payda hatası. |
| B17 | **84,42 milyon $ / 66 coin** | **en az 14.178** | API’de çok yoğun dolum ve pozisyon var | Dosyadaki hata `mkts:US500` için `2026-10-29T15:36:00Z` gecikmeli 1 dk mum eksikliği. O dakikanın çevresini bağımsız sorgu da **[]** döndürdü. Veri toplama yokluğu değil, fiyatlanamayan tek eylemin tüm trader’ı engellemesi. |

B17 sayfalamasında 8 sayfa çekildi; milisaniye sınırındaki olası kayıp bağımsız olarak dışlanmadığından sayı alt sınır olarak sunuldu. API’nin sayfalama tavanları dolayısıyla “tam tarihçe” iddiası yok.

İstekte sayılmayan `K08` ve `O17` de bu snapshot’ta `gecerli=false`. Her ikisinde önceki başarılı sonuç korunmuş; kalan yedi adreste yer tutucu sonuç var. Bu ayrım toplam kapsama dahil edilmeli.

Kod kanıtı: `motor.py:626–635` sağlık paydası ve güncel pozitif hesap şartı; `647` fiyatlama; `715–726` hata sonrası eski sonuç veya yer tutucuya dönme. Veri hatası sonuç üretimini engelliyor, verinin hiç bulunmadığı anlamına gelmiyor.

## 6. Pano Özet / Kasa tutarlılığı

| Ölçü | JSON’dan bağımsız hesap | Gerçek pano | Sonuç |
|---|---:|---|---|
| Oda | 18 | 18 | Tutuyor |
| Kontrol ana etiketi / gerçek üyelik | 17 / **18** | 17 | Kodun ana etiket hesabıyla tutuyor, deney üyeliğiyle tutmuyor |
| Oda sanal kasa | 16.779,63725 $ | 16.780 $ | Yuvarlama dahil tutuyor |
| Oda başlangıç farkı | −1.220,36275 $ / −%6,77979 | −1.220 $ / −%6,78 | Tutuyor; O17’nin eski sonucu dahil |
| Kontrol ana etiket toplamı | 17.212,63505 $ / +%1,25079 | 17.213 $ / +%1,25 | Kodu karşılıyor; E01 dışarıda |
| Kontrol gerçek üyelik toplamı | **18.213,22599 $ / +%1,18459** | Gösterilmiyor | Üyelik eksik |
| Açık işlem sayısı | **1.014** tüm trader pozisyon satırı; **135** oda satırı | Özet 1.014, kasa 135 oda satırı | JSON’la tutuyor; sanal kopya açık işlem sayısı değil |
| Işıklar — tüm trader sağlık | 11 yeşil / 31 sarı / 19 kırmızı | Sağlık alanını kullanan görünüm | `saglik` sayıları; mutabakatla karıştırılmamalı |
| Işıklar — oda sağlık | 2 yeşil / 10 sarı / 6 kırmızı | Oda sağlık alanı | Ayrı seri |
| Işıklar — oda mutabakat | 7 yeşil / 6 sarı / 5 kırmızı | “🔴 Dikkat / İnceleme gerekli” | Beş kırmızı nedeniyle toplu kırmızı doğru |
| Kasa tablo K/Z | **+2.968,02420 $** | Tablo toplamı aynı | Trader pozisyonlarının ölçeklenmiş sonucu |
| Sanal açık K/Z | **−64,15994 $** | Üst kutu −64,16 $ | Sanal defter sonucu; tablodakiyle farklı |
| Kasa eğrisi | Yalnız 1 günlük nokta var | “en az iki saatlik nokta bekleniyor” | Veri yokluğu dürüst; “saatlik” açıklaması mevcut günlük seriyle uyumsuz |

**Ölçek sorusunun yanıtı:** Kasa tablosunda dolarlar çıplak trader dolarları olarak kalmamış: `p.anlik_kz_usd × 1000 / t.hesap_degeri` dönüşümü var (`pano.html:449–454`). Fakat güncel trader pozisyonu ile gerçek gecikmeli sanal portföy karışıyor. Ham oda trader K/Z’si 823.849,71 $; dönüştürülmüş tablo 2.968,02 $; gerçek sanal açık K/Z −64,16 $. Bunları aynı hesabın bileşenleri gibi kullanmak hatalıdır.

Satır yüzdesi `t.sanal_kopya.acik` olduğundan aynı trader’ın bütün coinlerine aynı toplam yüzde yazılıyor (`pano.html:467`). Bu dolar ve yüzde aynı satır pozisyonunun ölçüsü değil. “Nakit 4.432 $” da sanal bakiye eksi trader pozisyonlarından türetilen yaklaşık teminat: farklı portföylerin çıkarılması. API `marginUsed` ayrıca yayımlanmadığı için nosyonel/kaldıraç tahmini izole/cross teminatla da her zaman eşit değil.

“Son kapananlar” listesi trader kapanış zamanına değil, açılış olayına eklenmiş `sanal_sonuc` etiketine dayanıyor. Eski açılış olayları 200 olay sınırından düşünce kapananlar da kayboluyor. Bu snapshot’ta üç elle izlenen kapanış var ama kasa “Kapanan sanal işlem yok” gösteriyor. Açılış olayı 200 listesinin dışında olduğundan bu yokluk işlem olmadığına kanıt değil.

## 7. Olayların son 24 saat kapsamı

Sorgu penceresi 29 Ekim 00:00–20:21 UTC. Tam 24 saat değil, pilotun bu güne kadarki kesimi; 24 saatlik iddiayı çürütmek için bu kesimdeki eksikleri görmek yeterli.

| Kontrol | Sonuç |
|---|---:|
| API’den aynı gün oda dolumları, emir bazlı gruplama | 733 işlem olayı (bağımsız yaklaşık olay sınıflaması) |
| Snapshot’ta oda olayları | 13: 11 işlem kimliği + 2 ışık |
| Türetilen işlem kimliklerinden listede olmayan | 722 |
| Son 200 içindeki ilk / son zaman | 19:59:16 / 20:21:28 UTC |

Örnek: O08 HYPE 10:45 açılışı ve 10:56 kapanışı API’de var, yayımlanan olay listesinde yok. O05 kPEPE 18:14 açılışı ve 19:12 kapanışı da kapsam dışı. Ayrıntılar `oda_olay_karsilastirma.csv` içinde. Emir sınıflamasında tam motor eşitliği iddiası yok; birkaç uç durum toplamı değiştirse de yüzlerce eski kimliğin listede olmaması ve bilinen kapanışların kaybı kesin.

Motor kodunda bu sınır açık: `motor.py:729–731` bütün kolları ortak listede sıralayıp `[:200]` alıyor. Yoğun taban adresi B17 son 22 dakikadaki listeyi dolduruyor. Kasa günlük metrikleri bu kesilmiş listeden türetiliyor (`pano.html:463–471`).

## 8. Sorgu örnekleri ve dosyalar

Örnek herkese açık trader: O02 `0x2888be6982957103ea88ac10f4179df0a294e877`.

```sh
curl https://api.hyperliquid.xyz/info -H 'Content-Type: application/json' \
  --data '{"type":"clearinghouseState","user":"0x2888be6982957103ea88ac10f4179df0a294e877","dex":"xyz"}'

curl https://api.hyperliquid.xyz/info -H 'Content-Type: application/json' \
  --data '{"type":"userFillsByTime","user":"0x2888be6982957103ea88ac10f4179df0a294e877","startTime":1793232000000,"endTime":1793305288440}'

curl https://api.hyperliquid.xyz/info -H 'Content-Type: application/json' \
  --data '{"type":"portfolio","user":"0x2888be6982957103ea88ac10f4179df0a294e877"}'

curl https://api.hyperliquid.xyz/info -H 'Content-Type: application/json' \
  --data '{"type":"candleSnapshot","req":{"coin":"HYPE","interval":"1m","startTime":1793272560000,"endTime":1793273220000}}'
```

| Dosya | İçerik |
|---|---|
| `durum.json` | Denetimde sabitlenen yayımlanmış çıktı |
| `pano.html`, `motor.py`, `kurallar.yaml` | İncelenen yayımlanmış pano ve main kaynaklarının kopyası; satır referansları bu sabit dosyalaradır |
| `sorgular.json`, `ek_sorgular.json`, `son_sorgular.json`, `zaman_sorgular.json` | Her sorgunun gövdesi ve zaman damgası; karşılık gelen ham yanıt ayrı JSON dosyası |
| `pozisyon_karsilastirma.csv` | Beş trader, 13 coin için ham karşılaştırma |
| `hesap_ozeti.json` | Kol, kasa, ışık, olay ve eksik veri hesapları |
| `islem_saglama.json` | Üç turun bütün miktar/fiyat bacakları, maliyet ve funding toplamları |
| `oda_olay_karsilastirma.csv` | Emir bazında türetilen olay ve yayımlanmış kimlik karşılaştırması |
| `pano_gozlem.json` | Tarayıcı CT verisi, görünür metinler, yakalama zamanı |
| `pano_ozet.png`, `pano_kasa.png`, `pano_kasa_telefon.png` | Gerçek yayımlanmış ekran görüntüleri |
| `topla.py`, `ek_sorgu.py`, `hesapla.py`, `islem_saglama.py`, `pano.cjs` | Veri toplama / bağımsız hesap / ekran yakalama araçları |

Kaynaklar: [izleme çıktısı](https://raw.githubusercontent.com/sselimgenc-oss/sg-arge/copytrade-izleme/izleme/durum.json), [Hyperliquid API](https://api.hyperliquid.xyz/info), [canlı pano](https://sselimgenc-oss.github.io/sg-pano/), [motor](https://github.com/sselimgenc-oss/sg-arge/blob/main/copytrade/izleme_motoru.py). Harici sistemlere yazı, PR veya emir gönderilmedi.

## 9. Ekran görüntüleri

Özet, gerçek yayımlanmış verilerle:

![Pano Özet](pano_ozet.png)

Kasa, gerçek yayımlanmış verilerle (uzun tablo):

![Pano Kasa](pano_kasa.png)

Telefon görünümü `pano_kasa_telefon.png` dosyasındadır. CSV ve ham JSON dosyaları, ekrandaki yuvarlamaların ötesinde sayısal inceleme içindir.
