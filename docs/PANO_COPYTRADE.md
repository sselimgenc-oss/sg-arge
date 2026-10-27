# İzleme ekranı tanımı — copy trade sekmesi (v1, 2026-10-27, TASLAK: kullanıcı onayı bekliyor)

Yapan: **Sonnet**, sg-pano reposunda. Veri: `docs/VERI_SOZLESMESI.md` (sg-arge). Önce sabit örnekle
(`izleme/ornek_durum.json`) çalışır; canlı veri hazır olunca yalnız kaynak adresi değişir.
Kullanıcı tek kişi; **telefon öncelikli**, bilgisayarda da aynı sayfa (uygulama kurulmaz).

## 1. Ana ekran — kartlar
- Kartlar **form skoruna göre** sıralı (en iyi üstte). `kirmizi` ışıklı kart en alta iner, soluk görünür,
  "izlemede — kopyalama" etiketi alır. Sıralama yalnız görünüm içindir (bkz. sözleşme §3).
- Üst şerit: güncelleme zamanı ve veri yaşı (ör. "8 dk önce"); 30 dakikadan eskiyse sarı uyarı.
- Kart içeriği:
  - takma ad · sağlık ışığı 🟢🟡🔴 · kapı sınıfı rozeti
  - açık pozisyonlar (coin, yön, giriş, büyüklük, hesap payı, kaldıraç, anlık K/Z; Binance karşılığı ikonla)
  - **son işlem** (coin, yön, sonuç %)
  - küçük kâr eğrisi (son 90 gün)
  - sanal kopya: "1.000 $ → 1.043 $ (t0'dan beri, 30 dk gecikmeli)"
- Açık pozisyonu olmayan trader: "pozisyon yok" satırı.

## 2. Ayrıntı sayfası (karta dokununca)
Tam kâr eğrisi; işlem geçmişi (sayfalı); sağlık ışığının nedenleri; kapı sonucu ve tarihi; t0; sanal kopya eğrisi;
bu trader için "açtıklarım" ile "tümü" karşılaştırması (karar kaydı varsa).

## 3. Akış sekmesi
Son olaylar zaman sırasıyla (açılış/kapanış/büyütme/ışık). Her açılış satırında karar durumu: Açtım · Atladım ·
cevapsız. Telegram'dan verilen karar burada görünür; burada da verilebilir (aynı kayıt).

## 4. İstatistik sekmesi
- Trader başına: tüm olayların sanal sonucu ↔ açtıklarımın sanal sonucu; atlama nedenleri dağılımı.
- Toplam: kararlarımın değer katıp katmadığı (fark ve işlem sayısı). Az veride "yetersiz veri" yazılır.

## 5. Kurallar
- Gizlilik: kararlar ve kullanıcıya dair hiçbir bilgi herkese açık dosyaya yazılmaz (sözleşme §4).
- Sayılar Türkçe biçim (1.043,20 $; %4,3). Saat Türkiye saati.
- Erişim mevcut pano gibi (`PANEL_TOKEN`); yeni hesap/şifre sistemi kurulmaz.
- Hiçbir ekran emir göndermez; para hareketi yok.
- Kabul: telefonda (iPhone, dar ekran) kartlar okunur, yatay kaydırma yok; örnek veriyle 4 trader (biri kırmızı,
  biri pozisyonsuz) doğru sıralanır; veri yaşı uyarısı çalışır.
