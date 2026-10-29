> **Lider denetim notu (2026-10-29):** Argon A29. "Ana pano 9 trader, veri 9 sa önce, mutabakat bekleniyor" bulgularının nedeni pano değil:
> saatlik izleme 61 trader'la yayımlanamadı (motor.json 267 MB > GitHub 100 MB; #414 ile R2'ye taşındı). Veri gelince bunlar kendiliğinden
> düzelir. Geçerli kalan işler: ofiste telefonda sol menünün haritayı daraltması, trader kartlarında BHY q / plasebo p / CUSUM gibi
> terimlerin sade etikete çevrilip "Teknik ayrıntı"ya alınması, veri tazeliği notunda saatlik döngünün yazılması. ("Günde bir tarama"
> önerisi yanlış; izleme saatliktir.)

# SG Pano & SG Ofis - Mobil UX Değerlendirme Raporu

**Tarih:** 29 Ekim 2026  
**Hedef Kitle:** Teknik olmayan son kullanıcı  
**Cihaz Profili:** Mobil ekran (≈390 px genişlik)  
**Sistem Tipi:** Sanal kopya / araştırma ortamı (gerçek emir veya finansal risk yok)  
**İncelenen Adresler:**
* [SG Pano Ana Gösterge Paneli](https://sselimgenc-oss.github.io/sg-pano/)
* [SG Ofis Sanal Kat Planı](https://sselimgenc-oss.github.io/sg-pano/ofis/)
* [SG Pano Ayarlar ve Sözlük](https://sselimgenc-oss.github.io/sg-pano/#ayarlar)

---

## 1. Yönetici Özeti

Önceki incelemeye kıyasla platformda kullanıcı deneyimini doğrudan etkileyen kritik adımlar atılmıştır:
* Kullanıcıda güvensizlik ve "ödeme yapmam mı gerekiyor?" şüphesi uyandıran **"kilitli" ifadeleri tamamen kaldırılmıştır**.
* Sayfanın tepesine eklenen kalıcı bilgilendirme bandı sayesinde sistemin **gerçek para içermeyen sanal bir simülasyon olduğu** netleştirilmiştir.
* Ofis sayfasına **61 trader masası** ve geriye dönük hareketleri listeleyen **Oda Değişim Kaydı (Olay Çekmecesi)** kazandırılmıştır.
* Ana panoya işlem güvenliğini denetleyen **Mutabakat Sağlığı** kartı eklenmiştir.

Buna karşın, 390 px dar ekranlarda sol menünün alanı daraltması, istatistiki jargondaki ağırlık ve iki sayfa arasındaki trader sayısı uyumsuzluğu çözülmesi gereken yeni öncelikler olarak öne çıkmaktadır.

---

## 2. Önceki 10 Maddelik Listenin Çözüm Durumu

| No | Konu / Önceki Sorun | Durum | Mevcut Durum Analizi ve Değerlendirme |
| :--- | :--- | :--- | :--- |
| **1** | **"Kilitli" / paralı özellik algısı** | **Çözüldü** | Tüm sekmelerdeki "kilitli" ibareleri ve kısıtlayıcı kilit simgeleri kaldırılmış; açık ve keşfedilebilir bir yapı kurulmuş. |
| **2** | **Sanal / gerçek para belirsizliği** | **Çözüldü** | Hem ana panoda hem ofiste `Araştırma / sanal, yatırım tavsiyesi değil · gerçek emir yok` uyarısı net biçimde sabitlenmiş. |
| **3** | **Mutabakat ve eşleşme sağlığı kartı** | **Kısmen** | [SG Pano Özet](https://sselimgenc-oss.github.io/sg-pano/) sekmesine kart eklendi; fakat şu an "Mutabakat verisi bekleniyor" gri durumunda bekliyor ve canlı metrik üretmiyor. |
| **4** | **Canlı izlenen trader sayısı (61 trader)** | **Kısmen** | [SG Ofis](https://sselimgenc-oss.github.io/sg-pano/ofis/) üzerinde 61 masa faal; ancak ana panoda "İzlenen trader: 9" yazdığı için iki sayfa arasında veri uyumsuzluğu algısı oluşuyor. |
| **5** | **Oda değişim ve olay geçmişi** | **Çözüldü** | Ofis sayfasına Olay Çekmecesi eklendi; oda, trader ve olay türü (pozisyon kapandı, ışık değişti vb.) bazında detaylı filtreleme sunuluyor. |
| **6** | **Mobil dar ekran (≈390 px) uyumu** | **Çözülmedi** | Ofis sayfasında sol menü ekranın %50'den fazlasını kaplayarak haritayı sıkıştırıyor; ana panoda sekmeler ve 5'li metrikler taşma sınırında. |
| **7** | **Ağır istatistik ve finans jargonu** | **Kısmen** | [Sözlük](https://sselimgenc-oss.github.io/sg-pano/#ayarlar) sekmesi eklenerek temel kavramlar tanımlanmış; fakat trader kartlarında doğrudan "BHY q", "plasebo p", "CUSUM" terimleri açıklamasız sürüyor. |
| **8** | **Veri tazeliği şeffaflığı** | **Kısmen** | `⚠️ Veri 9 sa önce · eski` uyarısı ve Yenile butonu mevcut; ancak sistemin neden 9 saat geride olduğu veya tarama döngüsü açıklanmıyor. |
| **9** | **İlk 10 saniye netliği** | **Kısmen** | Sanallık güvencesi ilk 3 saniyede anlaşılıyor; fakat "Gölge ölçüm", "Kohort", "Kol" gibi karmaşık terimler ilk ekranda zihni yoruyor. |
| **10** | **Tutar ve getiri simülatörü** | **Kısmen** | Ayarlar sekmesine bütçe hesaplayıcı entegre edilmiş; ancak ana özet ekranındaki -%0,05 sanal getiri ile doğrudan etkileşime girmiyor. |

---

## 3. Yeni Çıkan En Önemli 5 Mobil Sorun

### 1. Ofis Sayfasında Sol Menünün Mobili İstila Etmesi
* **Nerede:** [SG Ofis](https://sselimgenc-oss.github.io/sg-pano/ofis/) (Tüm ekran)
* **Sorun:** 390 px ekran genişliğinde sol gezinme menüsü (~200 px) sabit kalarak ekranın yarısından fazlasını yutmaktadır. Piksel sanat izometrik ofis haritasına yalnızca ~190 px kalmakta; masalara dokunmak veya olay çekmecesini incelemek imkansızlaşmaktadır.
* **Öneri:** Mobilde sol menüyü gizlenebilir bir hamburger çekmecesine veya alt gezinti çubuğuna (bottom sheet) dönüştürün; harita tuvaline tam ekran genişliği verin.
* **Etki:** **Kritik**. Mobil kullanıcının ofis haritasındaki etkileşimini ve dokunma hedeflerini felç etmektedir.

### 2. Ana Pano ile Ofis Arasındaki Trader Sayısı Çelişkisi
* **Nerede:** [SG Pano Özet](https://sselimgenc-oss.github.io/sg-pano/) vs [SG Ofis](https://sselimgenc-oss.github.io/sg-pano/ofis/)
* **Sorun:** Ana panodaki Gölge Ölçüm kartında "İzlenen trader: 9" ve "Kol başına trader: kol bilinmiyor (9)" yazarken, ofis sayfasında 61 trader canlı izlenmektedir. Teknik olmayan kullanıcı "Sistemde 9 kişi mi var yoksa 61 kişi mi?" şüphesine düşmektedir.
* **Öneri:** Ana panodaki kartı hiyerarşik olarak netleştirin: "Canlı İzlenen: 61 (Aktif İşlemdeki: 9, Aday Odası: 44, Ana Oda: 17)".
* **Etki:** **Yüksek**. Kullanıcı nezdinde veri tutarsızlığı ve güven zedelenmesi yaratır.

### 3. "Mutabakat Sağlığı" Kartının Pasif Kalması ve Tedirgin Edici Dili
* **Nerede:** [SG Pano](https://sselimgenc-oss.github.io/sg-pano/) (Özet sekmesi, 2. Kart)
* **Sorun:** Kart eklenmiş ancak gri göstergeyle "Mutabakat verisi bekleniyor", "Eylem: Veri bekleniyor" durumunda durmaktadır. Açıklamasında ise "yetim pozisyon, kaçan işlem, pozisyon farkı" gibi arıza çağrıştıran ifadeler yer almaktadır.
* **Öneri:** Veri beklenirken gri pasif durum yerine "Sistem Kontrolü: Hazır (Beklemede)" başlığı ve sade bir açıklama ("Kopya işlemler borsa ile birebir uyumlu mu denetlenir") yerleştirin.
* **Etki:** **Orta - Yüksek**. Kullanıcı sistemin aksadığı ya da bozulduğu hissine kapılabilir.

### 4. Trader Kartlarındaki İleri Düzey İstatistik Jargonu
* **Nerede:** [SG Pano](https://sselimgenc-oss.github.io/sg-pano/) (Trader'lar sekmesi)
* **Sorun:** Kartların üzerinde doğrudan "BHY q", "plasebo p > 0.05", "CUSUM uyarısı", "martingale işareti", "koni %5 altında" rozetleri sıralanmaktadır. Sözlük başka bir sekmede olduğu için kullanıcı kartı okurken anlamlandıramamaktadır.
* **Öneri:** Bu göstergeleri renkli ve günlük dile uygun etiketlere dönüştürün: "Risk: Yüksek (Saldırgan)", "Performans: Yetersiz", "Strateji: Dengeli". Matematiksel formülleri ise bir "Teknik Ayrıntı" açılır akordiyonuna saklayın.
* **Etki:** **Orta - Yüksek**. Kullanıcının trader tercihlerini anlamasını zorlaştırır, bilişsel aşırı yükleme yapar.

### 5. "9 Saat Önceki Veri" Uyarısının Mobilde Endişe Yaratması
* **Nerede:** [SG Pano](https://sselimgenc-oss.github.io/sg-pano/) (Üst durum çubuğu ve Veri Tazeliği kartı)
* **Sorun:** Ekranın en üstünde beliren sarı ikazlı `⚠️ Veri 9 sa önce · eski` uyarısı, "canlı izleme" vaadiyle tezat oluşturmakta ve sistemin çalışmadığı izlenimini vermektedir.
* **Öneri:** Uyarının yanına tarama frekansını açıklayan kısa bir bilgi notu ekleyin: "Son rutin tarama: 09:00 (Veriler piyasa kapanışında günde bir taranır)".
* **Etki:** **Orta**. Sistemin güncelliğine dair gereksiz güvensizlik yaratır.

---

## 4. İlk 10 Saniye Testi (Yeniden Değerlendirme)

* **0 – 3. Saniye:** Üstteki kalıcı sarı/gri şerit okunur: `Araştırma / sanal, yatırım tavsiyesi değil · gerçek emir yok`. Kullanıcı rahatlar: "Gerçek param riske girmiyor, güvenli bir simülasyon ortamındayım." (Önceki sürüme göre en belirgin iyileşme).
* **3 – 6. Saniye:** Göz altındaki ilk kartlara kayar: "Gölge ölçüm", "Hafta ?/12", "İzlenen: 9", `⚠️ Veri 9 sa önce`, "Mutabakat verisi bekleniyor". Kullanıcı duraklar: "Gölge ölçüm ne demek? Veri 9 saat gerideyse sistem çalışıyor mu yoksa takıldı mı?"
* **6 – 10. Saniye:** Kullanıcı "Ofis" sekmesine geçer. Piksel sanat harita ilgi çekicidir; ancak mobilde sol menü ekranı ikiye böldüğü için masalara tıklamak ve olayı kavramak güçleşir.
* **İlk 10 Saniye Skoru:** **6 / 10** *(Önceki incelemedeki 3/10 seviyesine kıyasla belirgin artış; ancak mobil ergonomi ve terim yoğunluğu ilk 10 saniye akıcılığını frenlemektedir).*

---

## 5. Öncelikli Eylem Planı (Hızlı Kazanımlar)

1. **Ofis Sayfasında Menü Daraltma (1. Gün):** CSS medya sorgusu (`@media (max-width: 600px)`) ekleyerek sol menüyü varsayılan olarak kapalı hamburger menüye çevirin.
2. **Trader Sayısı Senkronizasyonu (1. Gün):** Ana panodaki "İzlenen trader: 9" metnini "Aktif Takip: 9 / Toplam Havuz: 61" şeklinde revize edin.
3. **Kart Rozetlerini Sadeleştirme (2. Gün):** "BHY q", "plasebo p" gibi terimleri "İstatistiksel Güvenilirlik" başlığı altına gizleyip ön yüze yeşil/sarı/kırmızı durum etiketleri koyun.
