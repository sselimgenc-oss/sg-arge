> **Lider denetim notu (2026-10-29):** Argon A24. İnceleme, Codex'in ofis/pano canlı işinden (GOREV_OFIS_CANLI) ve 61 traderlık
> ilk izleme koşusundan **önceki** görüntüye dayanıyor (9 trader, "hafta ?", "kilitli", "paper izleme başlamadı"); bu maddelerin
> çoğu o işle kapanır. Kalanlar bir sonraki pano görevine girer: en üstte tek bakışta durum kartı, sade Türkçe ve tek terminoloji
> (Sanal Takip / Olay Geçmişi), 44 px dokunma hedefleri, mobilde ofis için liste görünümü, teknik metriklerin "Ayrıntı"ya alınması,
> adres kodu yerine üretilmiş takma ad (gerçek kişi adı yok). Gerçekleşmiş işlemler için K/Z gösterimi artık serbest (ön kayıt 1.5).

# Kopya Ticaret İzleme Panosu UX/UI İnceleme Raporu

**Hedef Kitle & Bağlam:** Teknik bilgisi olmayan, akıllı telefonundan (≈390 px) durumu kontrol eden kullanıcı. Salt okunur, sanal takip (gerçek para yok).  
**İncelenen Adresler:**
* [Ana Pano](https://sselimgenc-oss.github.io/sg-pano/)
* [Ofis Görünümü](https://sselimgenc-oss.github.io/sg-pano/ofis/)

---

## 1. İlk 10 Saniye Testi: "Bugün Durum Ne, Bir Şey Yapmam Gerekiyor mu?"

### Ana Pano (`/sg-pano/`)
* **Sonuç:** **Başarısız (Anlaşılmıyor).**
* **Gözlem:** Kullanıcı sayfayı açtığında ilk 10 saniyede hesabın güvende olup olmadığını veya bir eylem gerekip gerekmediğini anlayamaz.
* **Nedenleri:**
  1. **Eylem ve Durum Göstergesi Yok:** En üstte "Sistem çalışıyor, müdahale gerekmiyor" veya "Dikkat: İşlem yapmanız gerekiyor" şeklinde tek bakışta algılanabilecek bir ana durum kartı bulunmuyor.
  2. **Endişe Yaratan Uyarı Rozetleri:** Sayfanın hemen üst-orta kısmında beliren sarı ikazlar (`⚠ Veri 7 sa önce · eski`, `⚠ Veri 3 sa önce · eski`, `Fiyatlar: bekleniyor`) teknik olmayan kullanıcıda "Sistem çöktü mü? Param kayboldu mu?" paniği yaratıyor.
  3. **Belirsiz Değerler ve Soru İşaretleri:** `Hafta ?`, `Oda doluluğu ?`, `kol bilinmiyor 9` gibi placeholder metinler güvensizlik oluşturuyor.
  4. **Kriptik Olay Akışı:** "Son 5 olay" alanında `e573 Işık: ışık -> 🔴 kırmızı` uyarısı doğrudan göze çarpıyor. Kırmızı ışık acil bir sorun hissi veriyor; ancak kullanıcının ne yapması gerektiği yazmıyor.

### Ofis Görünümü (`/sg-pano/ofis/`)
* **Sonuç:** **Başarısız (Anlaşılmıyor).**
* **Gözlem:** Sayfa finansal bir panodan ziyade piksel-art tarzında simülasyon oyununu andırıyor.
* **Nedenleri:**
  1. **Yetersiz Günlük Özet:** Üst bantta yer alan `GÜNLÜK ÖZET dünü: değişiklik yok · bugün: değişiklik yok` ibaresi teknik olmayan kullanıcıya hiçbir şey ifade etmiyor. "Değişiklik yok" kar mı etti, zarar mı etti, işlemler açık mı sorularına yanıt vermiyor.
  2. **Pasiflik / Hata İzlenimi:** Sol menüdeki `KAYIT KİPİ: paper izleme başlamadı` ve `HABER HATTI: bilinmiyor` ibareleri sistemin çalışmadığı izlenimini pekiştiriyor.
  3. **Aşırı Bilişsel Yük:** İzometrik ofis haritası mobilde karmaşık bir labirent gibi görünüyor; kullanıcının aradığı kritik durum bilgisi odaların ardına gizlenmiş durumda.

---

## 2. Terminoloji, Dil ve İsimlendirme Analizi

### A. Anlaşılmayan ve Korkutan Terimler (Jargon)
* **İstatistiki / Algoritmik:**
  * `BHY q (0.385 > 0.1)` ve `Plasebo p (0.554 > 0.05)`: Sıradan kullanıcı için tamamen anlamsız formüller.
  * `Kohort ↔ kontrol`, `Taban`, `Kilitli`, `Geç kaldın`, `Giriş altında`.
  * `Medyan kaldıraç (3.07 > 3.0)`: Formül mantığı kullanıcıya aktarılmıyor.
* **Finansal Terimler:**
  * `PnL`, `Drawdown`, `ROI`, `Winrate`, `Margin`, `Execution`, `Slippage`, `PF (Profit Factor)`.
  * Pozisyon açıklamalarında yer alan `0,3x`, `xyz:AMZN`, `hesabın %0` gibi kodlamalar.
* **Kullanıcı/Trader Tanımlamaları:**
  * Trader'ların isim yerine 16'lık hex kodlarıyla gösterilmesi (`09d7`, `1404`, `2975`, `3e68`, `3f96`, `4c92`, `8bae`, `9312`, `e573`). Kullanıcı bu kişileri ayırt edemiyor ve güven duyamıyor.

### B. İngilizce ve Yarı Türkçe İfadeler
* `LONG` ve `SHORT` (Türkçe karşılıkları veya açıklamaları: Alış / Satış veya Yükseliş / Düşüş beklentisi).
* `Intraday` (Gün içi işlem) ve `Swing` (Dalga/Orta vade işlem).
* `paper izleme`: "Paper" kelimesi Türkçe metin içinde yabancı kalıyor; "sanal izleme" veya "deneme kipi" denmeli.

### C. Tutarsız Adlandırmalar
* **Sanal İzleme İfadeleri:** Aynı kavram için Ana Pano'da *Gölge ölçüm* ve *Sanal kopya*, Ofis görünümünde ise *Paper izleme* terimleri kullanılmış.
* **Akış ve Olay İfadeleri:** Ana Pano'da *Tüm akış* ve *Son 5 olay* denirken, Ofis görünümünde *Gözcü kaydı* ve *Olaylar* deniyor.
* **Filtreleme Süreci:** Ana Pano'da *Huni* denilen yapıya Ofis görünümünde *Hat (Pipeline)* deniyor.
* **Yazım Hataları:** Ana pano açıklamasında "kol" yerine teknik veritabanı değişken adı olan `"ko1 alanı"` yazılmış (`Veride henüz ko1 alanı yok`).

---

## 3. Ekran ve Tipografi Sorunları (Masaüstü & 390 px Mobil)

### A. Mobil (≈390 px Genişlik) İncelemesi
* **Taşan ve Ezilen Metinler:**
  * Rozet metinleri (örn. `Sanal kopya (hepsi), kol toplamları, kohort ↔ kontrol 🔒 kilitli · hafta ?/12 ?`) 390 px ekranda kenarlara yapışıyor ve okunması zor satır kırılmalarına yol açıyor.
  * Trader kartlarındaki çoklu rozetler yan yana sığmayıp dikeyde düzensizleşiyor.
* **Ofis Görünümü Mobil Uyumsuzluğu:**
  * Piksel-art izometrik harita 390 px ekranda çok küçülüyor; oda başlıkları (`SEKRETERLİK`, `ÇAY OCAĞI`, `MAKAM`) okunamaz hale geliyor.
  * Menüye dokunulduğunda açılan çekmece (drawer) tüm ekranı kaplayarak haritayı tamamen örtüyor; kapatma butonu (`X`) küçük ve ulaşılması zor bir noktada kalıyor.
* **Dokunma Hedefleri (Touch Targets):**
  * Üst gezinme sekmeleri (`Özet`, `Trader'lar`, `Huni`, `Ayarlar`, `Ofis`) birbirine çok yakın (yükseklik < 32 px).
  * Filtre rozetleri (`Oda 0`, `Aday 0`, `Kontrol 0`), bilgi simgeleri (`?`) ve akordiyon okları (`›`) 24 px'in altında kalıyor. Mobil dokunma ergonomisi için en az 44x44 px olmalıdır.

### B. Masaüstü İncelemesi
* **Metin Hiyerarşisi:** Metrik değerleri ile alt etiketlerin kontrastı düşük, 11-12 px fontlar geniş ekranda kayboluyor.
* **Harita Gezinimi:** Ofis haritasında fareyle pan/zoom yapma gerekliliği, hızlı bilgiye ulaşmak isteyen kullanıcı için lüks ve yorucu bir arayüz deneyimi sunuyor.

---

## 4. Bilgi Mimarisi: Fazlalıklar ve En Önemli 3 Eksik

### A. Gereksiz veya Tekrar Eden Bilgiler
1. **Tekrarlayan Eski Veri Rozetleri:** `⚠ Veri 7 sa önce · eski` uyarısı hem ana sayfada hem huni sekmesinde hem de kart diplerinde gereksiz yere birden fazla kez tekrarlanıyor.
2. **Çok Sayıda Sorumluluk Reddi (Disclaimer):** "Araştırma / sanal, yatırım tavsiyesi değil · gerçek emir yok" ibaresi ekranın 3 farklı yerinde yineleniyor.
3. **İşlevsiz Ofis Odaları:** Ofis görünümündeki *Çay Ocağı* odasına tıklandığında `"Yalnız ofis süsü. Veri göstermez, olay üretmez"` panelinin çıkması kullanıcının dikkatini dağıtıyor.
4. **Geliştirici Notları:** Kullanıcıyı ilgilendirmeyen `"Veride henüz ko1 alanı yok; gelince burada dolar"` gibi sistem/veritabanı notları arayüzde yer almamalıdır.

### B. Eksik Olan En Önemli 3 Bilgi
1. **🟢 Ana Durum ve Eylem Kartı (Bugünkü Durum & Yapılacaklar):**
   * *Neden gerekli:* Kullanıcı panoya girdiğinde tek bir saniyede "Her şey yolunda mı, işlem yapmam gerekiyor mu?" sorusunun cevabını görmelidir.
   * *Örnek içerik:* `🟢 Sistem Normal Çalışıyor · Takip edilen 9 trader aktif · Yapmanız gereken bir işlem yok.`
2. **💰 Sade Sanal Kar/Zarar ve Bakiye Özeti:**
   * *Neden gerekli:* Kullanıcı teknik çarpanlar (`0,3x`, `AMZN LONG`) yerine ne kadar sanal para kazandığını/kaybettiğini görmek ister.
   * *Örnek içerik:* `Bugünkü Net Durum: +$14,20 (+%0,8) · Toplam Sanal Bakiye: $1.045,00`
3. **👤 İnsanileştirilmiş Trader Kartları ve Basit Risk Rozetleri:**
   * *Neden gerekli:* Hexadecimal kodlar (`e573`) yerine anlaşılır rumuzlar ve sade risk seviyeleri olmalıdır.
   * *Örnek içerik:* `Trader Atlas · Düşük Risk · 3 Açık İşlem · Başarı Oranı: %72`

---

## 5. Eksik Veri (Henüz Bağlanmamış Alanlar)

Aşağıdaki bölümler henüz arka uç verisine bağlanmamış olup gri/varsayılan durumdadır:

* **Ana Pano:**
  * `[Eksik Veri]` **Hafta Durumu:** `Hafta ?` ve `hafta ?/12 ?`
  * `[Eksik Veri]` **Oda Doluluğu:** `Oda doluluğu ?` ve Huni içerisindeki `Oda (bilinmiyor)`
  * `[Eksik Veri]` **Kol Dağılımı:** `kol bilinmiyor 9` ve `"Veride henüz ko1 alanı yok; gelince burada dolar."` notu
  * `[Eksik Veri]` **Piyasa Fiyatları:** `Fiyatlar: bekleniyor` rozeti
* **Ofis Görünümü:**
  * `[Eksik Veri]` **Kayıt Kipi:** `KAYIT KİPİ: paper izleme başlamadı`
  * `[Eksik Veri]` **Haberleşme:** `HABER HATTI: bilinmiyor`
  * `[Eksik Veri]` **Işık Saati:** `IŞIK SAATİ: --:--`
  * `[Eksik Veri]` **Gözcü / Olay Kayıtları:** `Henüz olay yok — paper izleme başlamadı` ve `N=0 / Bu filtreyle olay yok.`

---

## 6. Öncelikli 10 Maddelik Düzeltme Listesi

| No | Nerede | Sorun | Öneri | Etkisi |
| :---: | :--- | :--- | :--- | :---: |
| **1** | Ana Pano · Tepe Alanı | "Bugün durum ne, ne yapmalıyım?" sorusuna tek bakışta cevap veren bir özet yok. | En üste yeşil/sarı durum kartı ekleyin: `🟢 Her şey yolunda · Müdahale gerekmiyor`. | **Yüksek** |
| **2** | Ana Pano · Veri Tazeliği | `⚠ Veri eski` ve `Fiyatlar bekleniyor` sarı uyarıları panik yaratıyor. | Uyarıları arka plana alın veya sadeleştirin: `Son güncelleme: 7 sa önce (Otomatik yenilenir)`. | **Yüksek** |
| **3** | Ana Pano & Ofis · Genel | Sanal bakiye ve günlük/toplam net kâr-zarar ($ / %) görünmüyor. | En üste basit finansal özet ekleyin: `Günlük Sanal K/Z: +$12,50 (%0,6)`. | **Yüksek** |
| **4** | Ana Pano · Trader Kartları | Trader'lar anlamsız hex kodlarıyla gösteriliyor (`e573`, `09d7`). | Kodları takma isimlere dönüştürün (örn. `Trader-Alfa`, `Strateji-Kaya`) ve basit risk rozeti ekleyin. | **Yüksek** |
| **5** | Mobil (390px) · Tüm Dokunma Alanları | Sekmeler, filtre butonları ve `?` simgelerinin tıklama alanı çok küçük (< 30 px). | Tüm buton ve dokunma hedeflerini mobil standart olan en az 44x44 px boyutuna getirin. | **Yüksek** |
| **6** | Ofis Görünümü · Mobil Harita | Piksel-art harita 390 px telefonda minyatür kalıyor, çekmeceler ekranı tamamen kilitliyor. | Mobilde harita yerine kartlı/liste görünüm sunun; haritayı isteğe bağlı masaüstü modu yapın. | **Yüksek** |
| **7** | Ana Pano · Akış & Olaylar | İşlem detaylarında karmaşık terimler var (`xyz:AMZN LONG 0,3x`, `Işık -> kırmızı`). | Dili sadeleştirin: `Amazon Alış İşlemi Kapatıldı`, `Risk Seviyesi Değişti`. | **Orta** |
| **8** | Ana Pano · Huni ve Ayarlar | İstatistiki formül ve teknik jargon (`BHY q`, `Plasebo p`, `Kohort`, `Medyan kaldıraç`). | Bu metrikleri "Gelişmiş / Teknik Detay" sekmesine gizleyin; ana ekranda başarı yüzdesi verin. | **Orta** |
| **9** | Ana Pano & Ofis · Terminoloji | Aynı kavramlar için farklı adlar kullanılmış (*Gölge ölçüm / Sanal kopya / Paper izleme*). | Tek tip Türkçe terminolojiye geçin: her yerde *Sanal Takip*, *Olay Geçmişi*, *Filtreleme*. | **Orta** |
| **10** | Ofis Görünümü · Departmanlar | "Çay Ocağı" gibi işlevsiz dekoratif öğeler kullanıcıda kafa karışıklığı yaratıyor. | Yalnızca veri üreten departmanları gösterin; dekoratif/boş odaları kaldırın veya gizleyin. | **Düşük** |
