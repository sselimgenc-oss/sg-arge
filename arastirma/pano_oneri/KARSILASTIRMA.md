# Pano önerileri — karşılaştırma (lider, 2026-10-27)

Kaynaklar (bu klasör): **A** `Emsal taramasının…txt` (özet), **B** `WebFetch bu oturumda…txt` (özet), **C** `Öncelik yeni grafikler…txt`,
**D** `# Kopya İşlem Panosu…txt`, **E** `Tam metni…txt`, **F** `copy_trade_panosu_gelistirme_onerileri.md`, **L** lider.
A ve B yalnız özet; tam raporları kendi oturumlarında kaldı. D'nin metni yer yer bozuk (karışık dil) → yalnız tablo başlıkları kullanıldı.

## Uyarılar (denetim)
- **10.000 dolum sınırı:** C, E, F "zamanlı sorguda yalnız son 10.000 dolum" diyor. Bizim 27 Ekim koşumuzda tek adres için
  18.428 farklı dolum geldi → iddia bizim veride tutmuyor. Karar verirken buna dayanılmaz.
- **Tarayıcıdan Hyperliquid API (CORS):** A doğrulayamadı. Faz 1'in ilk işi bunu denemek; olmazsa Worker ara katmanı.
- Emsal bağlantılarının bir kısmı ikincil kaynak/arama özeti (B: sayfa açılamadı). Özellik fikri olarak alındı, "emsalde kesin var" sayılmadı.
- Eşikler (ör. "fiyat kaçtı" sınırı) **kullanıcı kararıdır**; aşağıdaki sayılar yalnız öneri.

## Uzlaşı (kaç kaynakta)
| # | Öneri | Kaynak | Soru | Veri | Zorluk |
|---|---|---|---|---|---|
| 1 | **Giriş farkı / kayma rozeti** (trader girişi ↔ şimdiki fiyat, yöne göre; renk + metin) | A B C D E F L | Hâlâ girebilir miyim? | `durum.json` + HL `allMids` | S |
| 2 | **Açtım ↔ Atladım karnesi** (nedene göre sanal sonuç; "kaçırdın" dili yok) | A B C D E F L | Kararlarım iyi mi? | elimizde (olay `sanal_sonuc` + karar) | M |
| 3 | **Coin × yön yoğunlaşması** (izlenen traderlar; tutar girilirse yalnız localStorage) | A B C D E F L | Aynı bahse mi yükleniyorum? | elimizde | S |
| 4 | **Veri tazeliği damgası** (son başarılı güncelleme, eski veri kırmızı) | A B C D E L (+F mobil) | Veri güncel mi? | elimizde | S |
| 5 | **Işığın nedeni** (hangi ölçüt bozdu, tek cümle) | A B C D E | Trader hâlâ iyi mi? | elimizde (`saglik.nedenler`) | S |
| 6 | **Telegram mesajını zenginleştir + bağlantı doğrudan o olayın kartına** | A B C D E F | Telefonda hızlı karar | Worker + HL | M |
| 7 | **Kopya kaybı:** trader getirisi ↔ gecikmeli sanal kopya, gecikme maliyeti | A C D E L | Kopyalamak işe yarıyor mu? | elimizde | M |
| 8 | **Canlı pozisyonlar + son işlemler + Hyperdash/Hyperliquid bağlantısı** (Keşif ve trader kartı) | L (kullanıcı isteği), F (#5 açık emirler, derin bağlantı) | Şu an ne yapıyor? | HL `clearinghouseState`, `userFills` | S |
| 9 | **Oransal tutar hesaplayıcı** (trader hesabının %'si → senin bütçen; yalnız localStorage) | F L | Ne kadar açmalıyım? | elimizde + localStorage | S |
| 10 | **Tarz/davranış kayması** (tutma süresi, kaldıraç, büyütme sıklığı) | C E F | Alıştığım trader mı? | geçmiş dolum | M |
| 11 | Likidasyon fiyatı, açık TP/SL emirleri | B E F | Nerede çıkar? | HL `clearinghouseState`, `frontendOpenOrders` | S |
| 12 | Saat ısı haritası (TSİ) / seans | D F L | Pratikte takip edebilir miyim? | elimizde | S |

Tek kaynakta ama değerli: "Açtım dediğin işlemde trader çıktı" öncelikli bildirimi (A); localStorage ayarlarını dışa/içe aktarma (F);
olay bildirim eşiği / günlük bildirim bütçesi (E).

## Hepsinin "yapma" dediği
Saniyelik canlı PnL/sayaç; tek tık emir; ROI/kazanma oranı/takipçi sayısıyla sıralama; açıklamasız tek skor; her küçük büyütmeye
bildirim; oyunlaştırma ve "kaçırdın" baskısı; bakiye/tutarı sunucuya taşıyan eşitleme. **F'nin "ters kopyalama" fikri reddedilir.**

## Önerilen sıra (Codex, sg-pano; kapı işi bittikten sonra)
- **Faz 1 (S, mevcut veri + tarayıcıdan tek HL çağrısı):** 4 tazelik · 8 canlı pozisyon/işlem + bağlantılar · 1 kayma rozeti ·
  5 ışık nedeni · 3 yoğunlaşma · 9 hesaplayıcı. Önce CORS denemesi.
- **Faz 2 (M):** 2 karar karnesi · 7 kopya kaybı · 6 Telegram zenginleştirme ve derin bağlantı.
- **Faz 3:** 10 tarz kayması · 11 likidasyon/TP-SL · 12 saat haritası.
- Mobil (hepsinde): kart düzeni, ≥44 px dokunma, yatay kaydırma yok, renk + metin, ayrıntı açılır bölümde.

## Kullanıcı kararı gerekenler
1. Kayma rozeti eşikleri: öneri — yalnız % ve renk; "geç" sınırı tarzın kapı gecikme testindeki ortalama hareket (ör. intraday %0,5, swing %1,5).
2. Hesaplayıcı istensin mi (bütçe yalnız tarayıcıda)?
3. Faz 1'in başlama zamanı.
