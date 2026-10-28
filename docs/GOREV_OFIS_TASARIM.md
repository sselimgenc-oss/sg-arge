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
