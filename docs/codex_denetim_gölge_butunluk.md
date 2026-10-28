# Gölge bütünlük denetimi — giriş, çıkış ve açık zarar

Tarih: 2026-10-29. Kapsam yalnız kod okumadır; kod, eşik ve karar mantığı değiştirilmedi.
Satır numaraları denetlenen `main` sürümüne göredir. Seçim kodu `main`de henüz yok olduğu için
ilgili kanıt, açık seçim dalı `claude/secim-v1` üzerindeki `copytrade/secim.py`den alınmıştır.

## Sonuç özeti

| Risk | Değerlendirme | Kısa sonuç |
| --- | --- | --- |
| Trader dolumundan daha iyi gölge giriş/çıkış fiyatı | **Kısmen** | Sıfır gecikmede kaynak fiyatı kullanılır; gecikmede sonraki saatlik mum açılışı yönlü koruma olmadan daha iyi olabilir. |
| Kaçırılmış trader çıkışı | **Var** | Bağımsız pozisyon uzlaştırması yok; eksik çıkışta pozisyon pencere sonuna kadar işaretlenir. |
| Açık, zarardaki pozisyonun kapı/seçime etkisi | **Kısmen** | Gecikmeli net ve alfa açık K/Z'yi içerir; kapanış-temelli yardımcı metrikler ve sağlama kıyası içermez. |

## 1. Gölge giriş ve çıkış fiyatı

### Kanıt

- Gecikmeli yürütme, hedef zamandan sonraki ilk saatlik mumun **açılışıdır**; mum hedefe en fazla bir aralık uzaksa kabul edilir:
  `copytrade/defter.py:60-66`. Aynı fiyat pencere sonu işaretlemesinde de kullanılır: `defter.py:68-72`.
- Sıfır gecikmede doğrudan trader dolumundaki `px` kullanılır: `defter.py:191-200`. Bu yol, sıfır maliyet/ gecikme sağlamasında
  da kullanılır: `copytrade/golge.py:236-243`.
- Gecikmeli açılış ve kapanışta aynı yürütme kuralı uygulanır; PnL yürütme fiyatı ile hesaplanır: `defter.py:206-220`.
- V1 bandı, gecikmeli yürütme fiyatı ile trader fiyatı arasındaki **mutlak** farkı sınırlar; daha iyi fiyat yönünü engellemez:
  `copytrade/golge.py:23-48`. V2 de gecikmeli yürütme fiyatını kullanır: `golge.py:136-140`.

### Değerlendirme: **Kısmen**

Saatlik mumun hedef zamanından sonra seçilmesi geleceğe bakmayı önler ve sıfır gecikme sağlama yolu trader fiyatıyla aynıdır.
Ancak gecikmeli long girişte mum açılışı trader dolumundan daha düşük, short girişte daha yüksek olabilir; bu ekonomik olarak
olası bir piyasa hareketi olsa da model bunu ayrıca "iyileşmiş dolum" olarak işaretlemez. V1 bandı farkın büyüklüğünü sınırlar,
fakat yönünü sınırlamaz. Bu nedenle bayat kaynak fiyatı olmasa bile sahte iyi dolumun toplu etkisi ayrı raporlanamaz.

### Düzeltme önerisi (ayrı karar/PR)

Önce yalnız bilgi amaçlı olarak her yürütmede `trader_px`, yürütme fiyatı, fiyat zamanı ve yönlü iyileşme/kötüleşme oranı
raporlanmalı; bu rapor için altın örnek eklenmeli. Daha sonra lider kararıyla, gecikmeli girişte yönlü iyileşmeyi sınırlayan
muhafazakâr bir fiyat kuralı gerekip gerekmediği tartışılmalı; bu kapı eşiği veya karar kodu değişikliği olur ve bu denetimin
kapsamı dışındadır.

## 2. Kaçırılmış trader çıkışı

### Kanıt

- Defter yalnız kendisine verilen dolumlardan pozisyon üretir; kaynak kapanış dolumu gelmezse `held` içindeki pozisyonu kapatacak
  ayrı bir mevcut-pozisyon sorgusu veya mutabakatı yoktur: `copytrade/defter.py:152-172`, `defter.py:206-223`.
- Açık kalan pozisyon pencere sonunda kapanmış sayılmaz; son mum açılışında gerçekleşmemiş K/Z olarak `net`e eklenir:
  `defter.py:252-267`. Günlük eğri de bu işaretleme farkını taşır: `defter.py:269-288`.
- Mark fiyatı yoksa `unrealized_at` yalnız `unknown` sayacını artırır; ilgili PnL `net`e girmez: `defter.py:252-263`. Bu sayaç
  `mark_missing` olarak döner, ama genel `missing` dolum sayısından ayrıdır: `defter.py:265-267`.
- V2, likidasyon/ön kayıt eşiği tetiklenirse sentetik çıkış üretir ve sonraki kaynak dolumlarını trader sıfıra dönene dek bastırır:
  `copytrade/golge.py:115-176`. Bu, kaçan trader çıkışını saptayan uzlaştırma değildir.
- Sağlama betiği gerçek trader ile gölgeyi yalnız `realized` alanında kıyaslar: `copytrade/golge_saglama.py:80-89`. Açık kalmış,
  zarardaki pozisyonun `unrealized_end`i ve `mark_missing`i bu fark hesabına dahil değildir.

### Değerlendirme: **Var**

Çıkış dolumu API sayfalama/akış sorunu yüzünden gelmezse gölge pozisyonu kapanmaz; pencere sonuna kadar mumla değerlenir ve
funding taşır. Mark mevcutsa bu, zararı bütünüyle gizlemez; fakat mark yoksa PnL sıfır katkıyla kalır ve yalnız `mark_missing`
alanında görünür. Ayrıca sağlama koşusu gerçekleşmiş PnL ile sınırlı olduğundan bu tür açık pozisyon farkını "geçti" sonucu
altında gizleyebilir.

### Düzeltme önerisi (ayrı karar/PR)

Kalıcı gölge pozisyon durumunu, aynı adres/coin için sonraki API anlık görüntüsü veya dolum sayfasıyla uzlaştıran bir denetim
tasarlanmalı. Uyuşmazlıkta ham olayı silmek yerine `veri_kalitesi` ve neden kaydı bırakılmalı; mark yoksa sağlama sonucu
"eksik" olmalı ve realized kıyasının yanına toplam net/işaretlenemeyen açık pozisyon kıyası eklenmeli. Sentetik kapanış zamanı
ve fiyatı yeni karar gerektirir; otomatik kural olarak bu denetimden çıkarılamaz.

## 3. Açık, zarardaki pozisyonların kapı ve seçime etkisi

### Kanıt

- Gecikme metrikleri `copy_ledger(...).net`ten gelir: `copytrade/kapi.py:536-565`. `net`, gerçekleşmiş K/Z, maliyet, funding
  ve pencere sonu gerçekleşmemiş K/Z toplamıdır: `copytrade/defter.py:265-267`.
- Kapının adım 3'ü tarz gecikmesindeki `copy_net > 0` koşulunu kullanır: `kapi.py:694-725`; dolayısıyla işaretlenmiş açık zarar
  bu sonucu düşürür. Alfa için kullanılan günlük defter de açık pozisyon değerlemesi içerir: `kapi.py:904-912`, `defter.py:269-288`.
- Buna karşılık kapanış-temelli kanıt sayısı, tutma süresi, kâr oranı, en iyi işlem payı ve PF yalnız sıfıra dönen/ters dönen
  işlemlerden üretilir: `copytrade/olcut.py:51-112`, `olcut.py:271-292`. Aktiflikteki son 90 gün döngü sayısı da kapanış
  döngülerine dayanır: `kapi.py:642-658`.
- Seçim puanı kapıdaki gecikmeli net sütunudur: `copytrade/secim.py` (`claude/secim-v1`):39-42; aday seçimi yalnız bu puanı
  pozitif olanlarda yapar: aynı dosya:54-62. Havuz ise önce adım 1 ve 2'yi ister: aynı dosya:45-51.

### Değerlendirme: **Kısmen**

Kapıdaki ana ekonomik karar olan gecikmeli net ve alfa, mumla işaretlenebilen açık zararları kapsar; seçim de bu neti kullandığı
için aday puanına taşır. Buna karşılık kapının kanıt/kalite yardımcı metrikleri kapatılmamış zararı işlem sonucu olarak saymaz.
Bu tasarım açık pozisyonu iki kez gerçekleşmiş zarar saymaktan kaçınır, fakat çok sayıda açık zarar varken kapanış-temelli
metrikler trader'ı olduğundan güçlü gösterebilir. Mark eksikse ana net de bu açık zararı sayamaz.

### Düzeltme önerisi (ayrı karar/PR)

Kapı ve seçim raporlarına karar değiştirmeyen `acik_pozisyon_sayisi`, `unrealized_end`, `mark_missing` ve açık pozisyon
notionalı eklenmeli; tümü için altın örnek gerekli. Bu görünürlükten sonra lider, açık riskin adım 2/4 veya seçim havuzuna
etki edip etmeyeceğine karar vermeli. Mevcut eşik, kapı ve seçim karar koduna bu denetimde dokunulmamalı.

## Sınırlar

- Bu denetim çalışma zamanı API verisini veya gerçek bir sağlama koşusunu yeniden çalıştırmadı; kod yolu ve mevcut test/rapor
  sözleşmesini inceledi.
- `copytrade/secim.py` denetlenen `main` ağacında bulunmadığından seçim bulgusu açık seçim dalındaki kaynak üzerinden verildi.
- Bu belge yeni eşik veya otomatik düzeltme önermiyor; öneriler ayrı lider kararı ve altın örnekli PR gerektirir.
