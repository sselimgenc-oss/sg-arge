# Dış proje incelemesi: ofis arayüzünden alınabilecek fikirler (2026-10-28)

Kaynak: <https://github.com/ismailkaraabc/etre-trading-office> (GPL-3.0); canlı sayfa: <https://ismailkaraabc.github.io/etre-trading-office/>.

**Yöntem ve sınır:** yalnız fikir analizi. Kaynak kod ve görseller sg-pano'ya alınmadı, kopyalanmadı, çevrilmedi; bu belgede kod parçası yok.
Her fikir sg-pano'da sıfırdan, kendi verimizle ve kendi görsel diliyle yazılır (GPL-3.0 koduna bağımlılık doğmasın diye).
İncelenen yerler: `etre2/web/` (`index.html`, `canli.js`, `odalar.js`, `ofis.js`, `ortak.js`, `uygulama.js`, `stil.css`), `docs/index.html`, `README.md`.
sg-pano karşılıkları şuradan kontrol edildi: `index.html`, `ofis/` (`main.js`, `office.js`, `cekmece.js`, `bilgi.js`, `OLAYLAR.md`, `SEMA.md`), `docs/TASARIM.md`, `README.md`.

## Kısa tanım: o proje ne yapıyor?
Windows masaüstü uygulaması; iki taraf (Solana meme token spot + Hyperliquid perps) için sanal kopya işlemi yapar. Arayüz iki bölmedir:
**solda canlı sayılar, sağda izometrik piksel ofis**. Üstte menü ve durum rozetleri, Telegram'a paralel bildirim.
Bizden temel farkı: kendi kasası ve gerçek-para geçişi var; sg-pano **salt okunur** (emir, para, gerçek mod yok) ve
**performans körlüğü** ön kaydına bağlı (kol toplamı / K-Z hafta 12'ye kadar kilitli). Bu yüzden bazı fikirler "K/Z olmadan" uyarlanır, bazıları hiç alınmaz (§ Alınmayacaklar).

Zorluk: **düşük** = bir iki saatlik, yalnız `sg-pano`; **orta** = bir gün, ya veri alanı ya da yeni bileşen; **yüksek** = `sg-arge` üretimi + panoda yeni bileşen + test.

## 1. Çözüm listesi ve değerlendirme

### 1.1 Düzen

| # | Çözüm (o projede) | sg-pano'da karşılığı | Uyarlanırsa kullanıcıya getirisi | Zorluk |
|---|---|---|---|---|
| D1 | **İki bölmeli ana ekran:** solda sayı paneli, sağda ofis tuvali, aynı anda; ofis tam ekran düğmesi/tuşu. | Kısmen: ofis ayrı sayfa (`ofis/`); orada kart sütunu varsayılan gizli, menüden açılan panel var. Ana pano ile ofis aynı ekranda değil. | Masaüstünde "sayıya da resme aynı anda bakma"; ama telefon-öncelikli yapımızda değeri düşük. Yalnız geniş ekran için isteğe bağlı iki sütun. | Orta |
| D2 | **Klavye kısayolları:** 1–9 bölüm, 0 ofis tam ekran, O ofisi aç/kapat, Esc kapatır; yazı alanındayken devre dışı. | Kısmen: ofiste `+`/`−`/`0`/Esc var; ana panoda kısayol yok. | Masaüstü kullanımda sekmeler arası hızlı geçiş (Özet / Trader'lar / Huni / Ayarlar). | Düşük |
| D3 | **Üstte durum rozetleri:** mod, Telegram açık/kapalı, motor sağlığı noktası (üzerine gelince açık kalma süresi, takılma sayısı). | Kısmen: sağ üstte tek "veri 01:21 · 4 dk önce" tazelik yazısı, 90 dk'dan eski kırmızı. Telegram/Worker ve izleme motoru ayrı gösterilmiyor. | "Sistem ayakta mı?" sorusunun tek bakışta cevabı: izleme motoru yaşı, kapı koşusu yaşı, Worker son kontrol. Eski veri ile bozuk sistem ayrılır. | Orta |
| D4 | **Sekme başlığında özet** (kasa getirisi başlıkta). | Yok. | Başlık: "SG · 2 kırmızı ışık · veri 4 dk" gibi; sekme arka plandayken bile durum görünür. K/Z yazılmaz (kilitli). | Düşük |
| D5 | **Gizli sekmede yenileme durur, dönünce anında yenilenir;** her döngü bir önceki bitmeden yeniden başlamaz; yenilemede kaydırma konumu korunur. | Kısmen: ofis `visibilitychange` ile uyanıyor; ana pano 5 dk `setInterval` gizliyken de çalışıyor. | Telefon pili ve veri kullanımı; sekmeye dönünce bayat sayı görülmez. | Düşük |
| D6 | **"Ofisi kapat" düğmesi:** ofis kodu hiç başlamaz, görseller yüklenmez; tercih saklanır. | Yok (yalnız `prefers-reduced-motion` ve `?hareket=0`). | Zayıf telefon/pilde ofis yükünü tamamen bırakma; Telegram ve ana pano etkilenmez. | Düşük |
| D7 | **Sürüm imzası denetimi:** sunucu imzası değişince sayfa kendini yeniler (form doluyken beklemez). | Yok (statik GitHub Pages; eski önbellek riski). | Pano güncellenince eski sürümde takılı kalan sekme olmaz. Statik karşılığı: küçük bir `surum.json` yoklaması. | Düşük |

### 1.2 Odalar

| # | Çözüm | sg-pano'da karşılığı | Getirisi | Zorluk |
|---|---|---|---|---|
| O1 | **Her oda bir departman sayfası** (Makam, Sekreterlik, Finans, Haberleşme, Denetim, Arşiv, trader odası, masa, lab, keşif); tıklayınca sol ekranda açılır, bilgi satır satır, her bloğun başında "bu ne anlatıyor" cümlesi. | **Var:** oda iç görünümü (`#oda/lab`, Kapı, Arşiv…), açılır panel, "?" ipuçları. Fark: bloğun başındaki açıklama cümlesi bizde ipucuna gizli. | Açık açıklama cümlesi acemi kullanıcıya "?" aramadan bağlam verir (kart başlığı altında tek satır). | Düşük |
| O2 | **Oda üzerine gelince canlı özet** ("n/en çok trader · k açık işlem"). | **Var** (oda ipucu); içeriği daha zengin yapılabilir (oda doluluğu, bayat/sağlıklı). | Küçük: ipucunda doluluk ve tazelik. | Düşük |
| O3 | **Keşif sayfası:** üç grup kıyası (kohort ↔ kontrol ↔ havuzun geri kalanı), üçlü karar durumu **GEÇTİ / GEÇMEDİ / VERİ BİRİKİYOR**, kararın hangi sayıya bağlı olduğu (en az gün, gölge, trader sayısı) sayfada yazılı. | Kısmen: Huni sekmesi (havuz → aday → oda); kohort ↔ kontrol kıyası kilitli ("hafta x/12"). Üçlü durum ve "karar ölçütü" kartı yok. | Ön kayıt kuralı ekranda açık olur: "hafta 7/12 · VERİ BİRİKİYOR" — kullanıcı sonucu beklerken neyi beklediğini bilir; sonuca bakıp kural değiştirme isteği azalır. Kilit açılınca üç grup kıyası hazır. | Orta |
| O4 | **İleri test kartı:** ölçütler test başlamadan yazılıp donduruluyor; kalan süre, açık gölge sayısı, ölçüt başına ✓/· işareti. | Kısmen: sekreterlik odasında kural kitabı / ön kayıt hash'i / DURUM.md metni var; ölçütlerin tek kartı ve ilerleme yok. | "Neye göre karar vereceğiz, şu an hangisi tamam" tek kartta; ön kaydın somutlaşması. | Orta |
| O5 | **Liderlik takibi kartı:** kaç trader izleniyor / aday / odada / elendi, son tarama zamanı. | Kısmen: Huni'de son tarama ve aday listesi var; "elendi" sayısı ve tarama tazeliği ayrı yok. | Hunideki kayıp trader sayısı ve neden; tarama durduysa fark edilir. | Düşük |
| O6 | **Çıkış/atlama nedenlerini tek Türkçe sözlükten göster;** bilinmeyen kodlar kural-yedekle okunur yapılır (ham kod ekranda görünmesin). | Kısmen: Kararlarım nedenleri ve terim sözlüğü var; yeni/bilinmeyen kod için yedek kural belgelenmemiş. | Yeni bir neden kodu eklendiğinde panoda "gec_gordum" gibi ham metin çıkmaz. | Düşük |

### 1.3 Ajan ve trader gösterimi

| # | Çözüm | sg-pano'da karşılığı | Getirisi | Zorluk |
|---|---|---|---|---|
| A1 | **Trader masada oturan figür;** görünüm trader kimliğinden türetilir (aynı trader hep aynı görünüm), üstünde ad. | **Var** (tohumlu görünüm üretimi, `ofis/kisiler.js`). | — | — |
| A2 | **Figür kartı (hover):** kısa durum. | **Var** (ipucu/sabitlenen kart). | — | — |
| A3 | **Vardiya:** gündüz/akşam/gece ışığı; çalışanlar vardiyaya göre odada. | Kısmen: `?saat=` ile gün ışığı var; kadro vardiyaya bağlı değil. Trader uyarlaması: figürü trader'ın **gerçek işlem saat bandına** göre masada/dışarıda göstermek. | Trader'ın hangi saatlerde işlem yaptığı (gece payı, saat bandı) resimle sezilir; 30 dk / 2 sa gecikmeli kopyalamada "bu saatte uyanık olmam gerek mi" sorusuna görsel cevap. | Orta (`gece_payi` / saat dağılımı alanı gerekir) |
| A4 | **Trader karnesi (pencere):** kimlik, durum, puan, lab testi ilerlemesi, **10 parametrenin yüzdelik sırası** (veri yoksa "veri yok — puanda 35 sayılır" yazılır), gölge sonuçları, **kadro geçmişi** (kim ne zaman hangi nedenle girdi/çıktı). | Kısmen: trader sayfası (Hyperdash düzeni, kapı sonucu, sanal kopya, Kararlarım) daha zengin. **Eksik:** kadro/oda giriş-çıkış günlüğü ve nedenleri; kapı ölçütlerinin havuza göre yüzdelik sırası. | "Bu trader neden odada / neden çıktı?" denetlenebilir olur; seçim v1 kararlarının izi. Yüzdelik sıra, tek başına sayıdan daha anlamlı. Eksik veri dürüstçe yazılır. | Yüksek (`sg-arge` kadro günlüğü + pano bölümü) |
| A5 | **İşlem efekti:** açılış/kapanışta masadan yükselen yazı ve taban halkası. | **Var** (olay → animasyon eşlemesi, `ofis/OLAYLAR.md`). Not: o projede yazı rengi kâr/zarara göre değişir; bizde ön kayıt nedeniyle **kullanılmaz**. | — | — |
| A6 | **Olay kuyruğu/çekmece filtresi**, günlük özet şeridi. | **Var.** | — | — |
| A7 | **Kamera:** tekerlek/sürükle/çift tıklama yakınlaştırma, `R` ile sıfırlama. | **Var** (+/−/0, tekerlek, sürükleme). | — | — |

### 1.4 Canlı kasa

| # | Çözüm | sg-pano'da karşılığı | Getirisi | Zorluk |
|---|---|---|---|---|
| K1 | **Kasa şeridi:** toplam değer, başlangıçtan getiri, kasa grafiği ("yatırılan" referans çizgisiyle), 8 ölçü hücresi (nakit, açık değer, açık K/Z, bugün, yatırılan, işlem başı, son 24 sa, oda doluluk). | Kısmen: yalnız trader başına "sanal kopya $1.000 → bugün" (trader sayfası); kol toplamı **kilitli**. | **K/Z'siz** hücreler uyarlanabilir: oda doluluğu, açık işlem sayısı, son 24 saatte açılan/kapanan işlem sayısı, "işlem başı sanal tutar". K/Z hücreleri hafta 12'den sonra. Telefonda tek satır özet. | Düşük (kilit dışı hücreler) |
| K2 | **Açık işlemler tablosu:** teminat, değer, K/Z $ ve %, zirve, süre, **likidasyona uzaklık %**, kâr/zarara göre hafif arka plan tonu, toplam satırı. | Kısmen: "Açık işlemler" bölümü; likidasyon fiyatı var, **yüzde uzaklık yok**. K/Z tonu ön kayıt gereği alınmaz. | Likidasyona uzaklık (%), sonuç değil risk bilgisidir: gecikmeli kopyalayan kullanıcı için "bu pozisyon ne kadar kırılgan" sezgisi. | Düşük |
| K3 | **Son kapananlar tablosu:** neden etiketi (stop / kâr / süre / trader sattı), süre, kapanış saati. | **Var** (İşlem geçmişi sekmesi). Neden etiketi bizde sonuç % ile gösteriliyor. | — | — |
| K4 | **Grafik tuvalini yeniden kullanma** (aynı seri ve boyutta çizmeyip eskisini yerine koyma), liste kaydırma konumunu koruma. | Gerekmiyor: 5 dk yenileme, grafikler SVG. | — | — |

### 1.5 Bildirimler

| # | Çözüm | sg-pano / Worker karşılığı | Getirisi | Zorluk |
|---|---|---|---|---|
| B1 | **Telegram durum kartı** (iki kasa, açık işlemler, son kapananlar) belirli aralıkla. | Kısmen: Worker `/durum` komutu (tek satır/trader ışık özeti) ve olay bildirimi var; periyodik özet kartı yok. | Telefona kendiliğinden gelen kısa özet: kaç trader yeşil, kaç açık işlem, veri yaşı. K/Z olmadan. | Orta |
| B2 | **Her alım/satışın teknik ayrıntısı** (gecikme, kayma, ücret, neden). | Kısmen: bildirimde coin, yön, fiyat, hesap payı var; gecikme ve kayma uyarısı Telegram v2 listesinde (planlı). | Kopyalama kararı için "giriş fiyatı şimdi ne kadar uzakta" bilgisi (zaten planlı). | Orta |
| B3 | **Gün sonu özeti** ve **odaya giren/çıkan trader bildirimi.** | Yok (tasarımda yok). | Kadro değişikliği (ör. trader odadan düştü) kaçırılmaz; gün sonunda "bugün ne oldu" tek mesaj. | Orta (Worker + kadro günlüğü; A4'e bağlı) |
| B4 | **Komut seti:** `/durum /kasa /oda /trader /kurallar`; ayar ve yönetim komutları yalnız tanımlı yöneticiye. | Kısmen: `/durum` var, sohbet kimliği doğrulaması var. | `/oda` (kim odada), `/trader <ad>` (tek satır özet), `/kurallar` (ön kayıt özeti) hızlı sorgu. Not: yönetim/emir komutu **eklenmez** (ilke: telegramdan ayar değişmez, emir yok). | Düşük |
| B5 | **Sayfa içi küçük bildirimler** (sağ altta 6 sn: "Kaydedildi", "Adres kopyalandı"). | **Var** (adres kopyalandı notu); ortak bir bildirim bileşeni yok. | Tutarlı geri bildirim; küçük. | Düşük |

### 1.6 Genel yaklaşım (ürün/anlatım)

| # | Çözüm | sg-pano'da karşılığı | Getirisi | Zorluk |
|---|---|---|---|---|
| G1 | **Dürüstlük bandı:** "finansal tavsiye değil; hiçbir kuralın kalıcı kâr ettiği kanıtlanmadı; görseller gerçek ve eksi sonuçlu." Sonuç kötüyse de gösterilir. | Kısmen: sabit üst bantta "araştırma / sanal, yatırım tavsiyesi değil". Başarısızlık/negatif sonuç özeti yok. | Hafta 12'de sonuç açıldığında "kontrol grubunu geçemedik" gibi sonuç da aynı sadelikte gösterilir (karar kuralı önceden yazılı). | Düşük |
| G2 | **Gelişim günlüğü/tarihçe:** her sürümün hatası ve çıkarılan ders kısa zaman çizgisi olarak. | Yok (kararlar `DURUM.md` ve belgelerde). | Kullanıcıya proje hafızası: plasebo pilotu → kapı v1.1 → seçim v1 gibi dönüm noktaları ve gerekçeleri tek sayfada. | Düşük (statik sayfa) |
| G3 | **Başka bir izleme ürününden gelen "kural değişikliği yalnız ileri testten sonra"** ilkesi. | **Var** (ön kayıt 1.1/1.2). | — | — |

## 2. Alınmayacaklar (ilkelerimize aykırı)
- **"Gerçeğe geç" sihirbazı, cüzdan, para çekme/yatırma talebi, durdur-başlat düğmeleri:** sg-pano salt okunur; gerçek para, emir ve aracı kurum bağlantısı yok (`AGENTS.md`).
- **K/Z'ye göre renk, sıralama, rozet, seri, kasa K/Z grafiği:** ön kayıt performans körlüğü (hafta 12'ye kadar). Açık işlem satırındaki tek tek K/Z görünür kalır, ama toplam/kol/kohort kıyasları kilitli.
- **Puan ve yüzdelik sıra ile trader sıralaması:** seçim kuralı `kurallar.yaml`; panoda yeni sıralama kuralı eklenmez. Yüzdelik sıra (A4) yalnız **bilgi** olarak, sıralama anahtarı olmadan.
- **Kod değişince kendini test edip yeniden başlatan gözetmen, masaüstü pencere düzeni:** masaüstü uygulamasına özgü; statik sayfada karşılığı yok (D7 hafif eşdeğeri).
- **Süs sahneleri/şakacı davranışlar:** sade ve ciddi görünüm tercih edilir; ayrıca seçim kararını dağıtır.

## 3. En faydalı 5 fikir (öncelik sırası)

1. **A4 — Kadro geçmişi + trader karnesinde yüzdelik sıra (yüksek zorluk, yüksek değer).**
   "Bu trader neden odada, neden çıktı?" sorusuna sayfa içinde cevap; seçim v1 kararlarının izlenebilir olması ön kaydın denetimini kolaylaştırır. Veri `sg-arge`'de üretilmeli (seçim günlüğü), pano yalnız gösterir. B3 bildirimleri de buna bağlı.
2. **O3 + O4 — Karar ölçütü kartı ve üçlü durum "GEÇTİ / GEÇMEDİ / VERİ BİRİKİYOR" (orta).**
   Hafta x/12 beklerken neyin beklendiğini (en az gün, gölge sayısı, trader sayısı, ölçütler) tek kartta gösterir; kilitli kıyas açılınca üç grup (kohort ↔ kontrol ↔ havuz) hazır. Sonuca bakıp kural değiştirme baskısını azaltır.
3. **B1 + B3 + B4 — Telegram: periyodik özet, gün sonu özeti, oda giriş/çıkış bildirimi, `/oda` `/trader` komutları (orta).**
   Kullanıcı panoyu açmadan durumu telefonda görür; yalnız okuma ve bilgilendirme, emir/ayar komutu yok.
4. **D3 + D4 — Sistem sağlığı rozetleri ve sekme başlığı özeti (orta/düşük).**
   İzleme motoru yaşı, kapı koşusu yaşı, Worker son kontrolü ve kırmızı ışık sayısı tek şeritte; "veri eski mi, sistem mi bozuk" ayrımı. Geçen haftalardaki sessiz zamanlama sorunlarını (ilk saatlerde tetiklenmeyen saatlik iş) erken gösterir.
5. **K1 + K2 — K/Z'siz kasa şeridi hücreleri ve likidasyona uzaklık % (düşük).**
   Oda doluluğu, açık işlem sayısı, son 24 saat açılan/kapanan, "işlem başı sanal tutar" ve açık pozisyonda likidasyona %-uzaklık: kilit kuralını bozmadan özet bilgi ve gecikmeli kopyalama için risk sezgisi.

Sıradaki ek adaylar (düşük çaba): D5 (gizli sekmede yenilemeyi durdurma), D6 (ofisi kapat düğmesi), G1 (negatif sonuç dahil dürüst özet), O6 (ham neden kodu yedeği).

## 4. Uygulama notu
Hiçbiri bu PR'da kodlanmadı. Birinci ve üçüncü fikirler `sg-arge`'de yeni veri alanı gerektirir (`docs/VERI_SOZLESMESI.md` sürüm artışı, lider onayı); ikinci, dördüncü ve beşinci yalnız `sg-pano` tarafında başlayabilir
(ikincisi için `golge` alanı ve ön kayıt ölçütleri `durum.json`'a eklenmelidir). Önce kullanıcı hangi fikirlerin yapılacağını seçer; tasarım değişikliği `docs/TASARIM.md`'ye yazılarak onaylanır.
