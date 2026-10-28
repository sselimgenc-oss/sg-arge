# Görev: Ofis görünümü — animasyonlu izometrik pano (2026-10-28, lider; kullanıcı onaylı)

Yapan: lider atar (herhangi bir işçi). Repo: `sg-pano` (GitHub Pages), yeni sayfa `ofis/`. Dal: `<işçi>/ofis-tasarim`. Tek PR; lider
denetler, birleştirir. Önce `sg-arge` `DURUM.md` ve `docs/GOREV_D_YOLU.md` (roller, katlar, kurallar).

## Amaç
Etre V2'nin ofisi kadar zengin ve eğlenceli, **bizim** içeriğimizi gösteren bir ofis ekranı. İlk sürüm **örnek veriyle** çalışır;
veri biçimi gerçek `durum.json`'a sonradan bağlanacak şekilde kurulur (D yolu Faz 5).

## Referans ve sınır
- Tarz referansı: `sg-arge/arastirma/etre/` (ekran görüntüleri, `README.md`, `tweetler.md`).
- **Kopya değil, aynı tarz.** Etre'nin görselleri, çizimleri, yerleşimi birebir kopyalanmaz, üzerinden çizilmez, ekran görüntüsünden
  parça kesilmez. Tarz (izometrik piksel sanatı, oda düzeni, yan panel yapısı) serbesttir.
- Hedef kalite: Etre görüntüleriyle yan yana konduğunda ayrıntı ve sıcaklık bakımından geri kalmamak.

## Görsel varlıklar
- Yalnız **açık lisanslı** varlıklar (tercihen CC0; örn. Kenney.nl izometrik paketleri) ya da işçinin kendi ürettiği çizimler.
- Her varlığın kaynağı ve lisansı `ofis/LISANSLAR.md`'ye yazılır. Lisansı belirsiz varlık kullanılmaz.
- Toplam varlık boyutu ≤ 15 MB; sprite sayfaları tercih edilir.

## Ekran düzeni (masaüstü)
1. **Üst çubuk:** logo, sekmeler (Genel, Havuz, Aday, Oda, Kohort ↔ Kontrol, Risk, Arşiv, Telegram, Ofis tam ekran), durum çipleri
   (`GÖLGE · SİM`, `TELEGRAM · AÇIK`), vardiya adı + saat, **`ÖRNEK VERİ`** etiketi (örnek veri kullanıldığı sürece).
2. **Sol panel** (kaydırılabilir):
   - Gölge kasası (sanal): değer, başlangıçtan değişim, mini eğri ya da "veri birikiyor".
   - Özet kutular: açık işlem, bugün, oda doluluğu (ör. 14/20), aday sayısı, işlem başı tutar.
   - **Açık gölge işlemleri** tablosu: coin, yön, kaldıraç, trader (kısa adres), süre, K/Z $ ve %, likidasyona uzaklık.
   - **Son kapananlar**: coin, yön, kapanış nedeni (trader kapattı / zarar kesme / süre), süre, K/Z.
   - Huni (havuz → aday → oda), Kohort ↔ Kontrol kartı (**performans kilitli**, hafta x/12), veri kalitesi, risk tavanları.
3. **Ofis (sağ, ana alan):** izometrik bina; çimen, ağaçlar, otopark, yol; içte odalar ve tabelaları.

## Odalar ve karakterler (`GOREV_D_YOLU.md` Roller tablosu)
Tarama, Kapı, Lab (havuz gölge), Kontrol grubu, Aday, Oda (kopya), Finans, Risk, Denetim, Arşiv, Haberleşme, Sekreterlik, Makam,
Çay ocağı. Her odada işlevine uygun mobilya (Arşiv: raflar; Denetim: sunucu dolapları; Haberleşme: büyük ekran; Oda: işlem masaları).
Trader'lar Lab/Aday/Oda masalarında oturan figürler; üstlerinde kısa adres etiketi (üzerine gelince ayrıntı).

## Animasyon kuralları
- **Her hareket bir olaydan doğar** (örnek veride olay akışı simüle edilir): terfi eden trader Lab → Aday → Oda yürür; yeni sinyalde
  ilgili masanın ekranı yanar; Risk tavanı dolunca Risk odasında alarm; bildirim gidince Haberleşme'den zarf çıkar; veri bayatlarsa
  ilgili oda grileşir.
- Boşta "çalışıyormuş gibi" sahte hareket yok; süs hareketleri (çaycı, ağaç sallanması) veri gibi görünmez.
- Gözcü kaydı: son olaylar listesi (zaman, oda, olay); olayın odası kısa süre vurgulanır.
- Gündüz/akşam vardiyası ışığı gerçek saate göre.
- `prefers-reduced-motion` açıksa animasyonlar durur.

## Veri
- Tek giriş dosyası `ofis/ornek_durum.json`; şeması `sg-arge/docs/VERI_SOZLESMESI.md` tarzında `ofis/SEMA.md`'de belgelenir:
  kasa, açık/kapanan gölge işlemleri, katlar, kollar, veri kalitesi, risk, olay akışı.
- Her sayının yanında zaman damgası ya da n; veri yoksa "bilinmiyor" (sıfır değil).
- Örnek veri gerçek adres içermez (ör. `0xAAAA…` biçiminde uydurma kısaltmalar) ve her yerde "örnek" diye işaretlenir.

## Teknik
- Statik site (GitHub Pages), derleme adımı gerekmiyorsa daha iyi. Kütüphane kullanılırsa (ör. PixiJS) sabit sürümlü CDN.
- Masaüstünde 60 fps hedefi; telefonda ofis ölçeklenir, paneller alta iner, yatay kaydırma yok.
- Erişilebilirlik: düğmeler gerçek `<button>`; metin kontrastı ≥ 4.5:1; ofis için kısa metin açıklaması.

## Kabul
- Masaüstü (1440×900) ve telefon (390×844) ekran görüntüleri + 15 sn ekran kaydı (GIF/MP4) PR açıklamasında.
- `LISANSLAR.md` tam; varlık boyutu raporu.
- Olay → animasyon eşlemesinin tablosu (`ofis/OLAYLAR.md`).
- Lider kontrolü: Etre görüntüleriyle yan yana kalite karşılaştırması; kopya değil.
- Durum: `sg-arge/docs/codex_durum_ofis.md` (ya da işçinin durum dosyası).

---

# Sürüm 2 — İçine girilebilen, etkileşimli ofis (2026-10-28, kullanıcı isteği)

Başlama koşulu: sürüm 1'in iki taslağından (sg-pano #17 Codex, #18 Sonnet) **esas alınacak olan seçildi** (Argon A5
karşılaştırması + kullanıcı kararı); diğerinin güçlü yanları içine taşındı. Öncelik trader seçiminin gerisinde; işçi seçim/gölge
işi bitmeden buna geçmez. Sürüm 1'in bütün kuralları (açık lisans, kopya değil, olaydan doğan hareket, erişilebilirlik) geçerli.

## 1. Oda içi görünüm (yakınlaşma)
- Bina görünümünde oda tabelasına ya da odaya tıklayınca o odanın **iç sahnesi** açılır: yalnız o oda, daha büyük ölçekte;
  masalar, dolaplar, ekranlar, kişiler ayrıntılı. Geri düğmesi + `Esc` + tarayıcı geri tuşu (adres `#oda=kapi` gibi) binaya döner.
- Her odanın iç sahnesi kendi işlevini gösterir (Arşiv: raflar ve kutular; Kapı: kontrol masası; Oda: işlem masaları ve trader
  ekranları; Risk: alarm paneli; Haberleşme: büyük ekran ve zarflar).

## 2. Tıklanabilir nesneler ve kişiler
- **Kişi** (çalışan ya da trader): bilgi kutusu — ad, rol, şu an ne yaptığı (son olaydan), ilgili sayılar (ör. trader: tarz, puan,
  açık işlem, gölge K/Z; zaman damgası ile) + kısa **replik**.
- **Nesne** (dolap, ekran, masa): bilgi kutusu — o birimin verisi (ör. Arşiv dolabı: tür başına satır, son kayıt zamanı, boşluk).
- **Reaksiyonlar:** tıklanan kişi küçük bir animasyonla tepki verir (bakar, el sallar, ekranı gösterir).

## 3. Birimler arası iletişim
- Olay akışındaki gerçek olaylar birimler arası işaretle gösterilir: ok/zarf/kağıt taşıyan figür (Tarama → Kapı: "yeni aday";
  Kapı → Aday: "terfi"; Risk → Oda: "tavan doldu"; Haberleşme → dışarı: "Telegram gönderildi").
- Konuşma balonları ve not kağıtları: kısa replik + olayın kendisi (tıklayınca ayrıntı ve zaman).
- Çalışan ↔ trader etkileşimi: ör. Denetim çalışanı trader masasına gidip "kırmızı bayrak: vault oranı yüksek" notu bırakır;
  yalnız gerçek bayrak/olay varsa.

## 4. Replik kuralları
- **Veri replikleri** (olaydan doğar, sayı içerir): yalnız gerçek olay/sayı varsa; şablonlar `ofis/replikler.json`'da
  (`{olay_turu, rol, sablon}`), sayı alanları veriden doldurulur.
- **Süs replikleri** (sohbet, espri): ayrı listede, görsel olarak farklı (ör. italik/gri balon); veri gibi görünmez, sayı içermez.
- Replikler Türkçe; dil dosyası yapısı ileride başka dile çevrilebilecek şekilde.

## 5. Kişiselleştirme
- Çalışan adları, avatar seçimi (varlık paketinden), oda tabelası adları kullanıcı tarafından değiştirilebilir: ayarlar paneli;
  tarayıcıda saklanır, dışa/içe aktarılabilir JSON. Varsayılan adlar `ofis/kadro.json`'da.
- Trader'lar gerçek adres yerine takma adla gösterilebilir (adres ilk 4 hane varsayılan).

## 6. İleride ürünleşme için mimari (şimdiden)
- **Veri bağdaştırıcısı:** ofis yalnız `durum.json` şemasını (`ofis/SEMA.md`) okur; sg-arge'ye özgü kod bağdaştırıcıda. Başka bir
  veri kaynağı aynı şemayı üretirse ofis değişmeden çalışır.
- **Varlık lisansları ticari kullanıma uygun** olmalı (CC0 ya da ticari izinli); lisansı belirsiz tek varlık bile kullanılmaz.
- Marka/isim: Etre'ye ve başka ürünlere benzemeyen özgün ad ve görünüm.
- Not (lider): pazarlama aşamasında yatırım tavsiyesi/kopya işlem hizmeti yasal izin gerektirebilir (Türkiye'de SPK); ürün
  "görselleştirme/araştırma aracı" olarak konumlanır. Bu, kullanıcı kararı ve ayrı bir hukuki inceleme konusudur.

## Kabul (sürüm 2)
- Her odanın iç sahnesi; her oda için en az 3 tıklanabilir nesne ve tüm kişiler tıklanabilir.
- Olay → iletişim işareti eşlemesi `ofis/OLAYLAR.md`'de güncel; örnek veride her olay türü en az bir kez tetiklenir.
- Ad değiştirme: sayfa yenilenince korunur; dışa/içe aktarma çalışır.
- Masaüstü + telefon ekran görüntüleri, 30 sn ekran kaydı (bina → oda → kişiye tıklama → iletişim işareti).
- `LISANSLAR.md` ticari kullanım sütunuyla.

## Sürüm 2 — araştırma sentezi (2026-10-28, lider; kaynak `arastirma/ofis/`)
Üç bağımsız emsal raporu (AI Town, Generative Agents, Pixel Agents, Agent Pixel Office, Kairosoft, Two Point Hospital vb.).

**Teknik karar:** seçilen taslağın mevcut teknolojisinde kalınır (yeniden yazma yok). PixiJS'e geçiş ancak gerçek cihazda
ölçülmüş 60 fps sorunu varsa. Panel, bilgi kutusu, tooltip HTML/CSS katmanında (erişilebilirlik).

**Varlık:** varsayılan kendi çizimimiz. Dış varlık yalnız lisansı kaynak sayfasından doğrulanıp `LISANSLAR.md`'ye ticari kullanım
sütunuyla yazılırsa. Sanatı ticari olmayan paketler (ör. Star Office UI sanatı) ve LimeZu gibi lisansı belirsizler kullanılmaz.

**Alınanlar (sürüm 2 kabulüne eklenir):**
- Odaya giriş aynı tuvalde kamera yakınlaşmasıyla; diğer odalar soluklaşır, seçili odanın duvar/çatısı kalkar. Adres `#oda/<ad>`.
- Telefonda iki seviye (bina / oda), bilgi alttan çekmece, dokunma hedefi ≥ 44 px, hover'a bağlı işlev yok.
- Ortak bilgi kutusu üç bölüm: **Kimlik** · **Gerçek veri** (zaman, n, geçerlilik) · **Replik** (ayrı görünüm, "ofis esprisi" etiketi).
- **"Neden burada?"**: her figür/ekran için o durumu doğuran olay, kural ve tarih; olay işaretine tıklayınca `olay_id` ve zaman.
- Olay çekmecesi: oda/trader/olay türü filtresi; olaya tıklayınca kamera o odaya gider.
- Olay kuyruğu: olaylar hızlı gelirse animasyon hızlanır ya da figür doğrudan yeni yerine geçer; pano hiçbir zaman eski bir
  animasyon yüzünden yanlış durum göstermez.
- Bayatlık: her ekran köşesinde "X dk önce"; veri bayatsa oda sislenir + açık `VERİ ESKİ` etiketi.
- Ad değiştirme yalnız etiketi değiştirir; bilgi kutusunda trader'ın gerçek adresi (kısaltılmış) ve kaşif bağlantısı sabit kalır.
- Süs repliklerinde rakam, adres, oran yasak — bunu denetleyen otomatik test.
- Olay yokken çizim döngüsü durur (pil ve sahte hareket).
- Sekreterlikte **ön kayıt kasası** (sürüm, commit, dondurma tarihi); her odada "bu birim ne yapar / ne yapmaz" kartı.
- Günlük özet yalnız olay günlüğünden ("dün: 3 terfi, 1 çıkış, 2 bildirim"; boş günde "değişiklik yok").
- Ses varsayılan kapalı, yalnız olay başına bir ton.

**Alınmayanlar (gerekçe):**
- Kâr/zarara göre renk değiştiren zemin, kâr rozetleri, "en çok kazandıran" manşeti, düşüşte "patron teftişi", seri (streak):
  performansı oyunlaştırır ve ön kayıttaki **performans körlüğünü** bozar.
- Trader pozisyonlarını espriye çeviren "dedikodu tahtası": veri ile süsü karıştırır.
- Ofis içine canlı fiyat grafiği: kapsam dışı.

**Performans körlüğü (ön kayıt "Ölçüm"):** canlı gölge süresince kohort ↔ kontrol karşılaştırması ve kol toplam getirileri
ofiste **kilitli** (yalnız "hafta x/12"). Tek tek işlem K/Z'si Telegram'daki kadar görünür; toplanmış kol performansı gösterilmez.
Ofisten hiçbir seçim/oda kararı verilmez.

**Ürünleşme:** veri bağdaştırıcısı + sürümlü şema (`surum`), salt-okunur paylaşım (`?durum=URL`), tema/düzen dışa-içe aktarma.
Her ekranda "araştırma/sanal, yatırım tavsiyesi değil" ibaresi; gerçek parayla kopyalamaya yönlendiren düğme yok.

**İlk 5 iş (sıralı):** 1) Lab odasında oda içi görünüm prototipi; 2) ortak bilgi kutusu (masaüstü panel / telefon çekmece);
3) `replikler.json` + süs repliği rakam testi; 4) `OLAYLAR.md`'ye zarf/not/ok eşlemesi; 5) ad değiştirme ayarları + dışa/içe aktarma.
