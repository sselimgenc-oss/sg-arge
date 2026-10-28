# Olay → animasyon eşlemesi (v1)

**İlke:** ofisteki her hareket bir olaydan doğar; boşta "çalışıyormuş gibi" sahte hareket yoktur. Olay akışı örnekte
`ornek_durum.json` → `olaylar[]` içinde simüle edilir (şema: `SEMA.md`). Her olay ayrıca **Gözcü kaydına** (`zaman · oda · olay`) yazılır
ve olayın odası ~3 sn **vurgulanır** (sarı çerçeve + yumuşak parıltı). Animasyon süreleri `office.js` içindedir.

| Olay (`tur`) | Tetikleyen durum | Ofiste ne olur | Panelde ne değişir |
|---|---|---|---|
| `yeni_adres` | Haftalık tarama yeni adres buldu | Yeni figür binanın önünden girişe yürür, Kapı'da turnike arasında bekler. Tarama odası vurgulanır, balonda büyüteç, Tarama duvar ekranında tarama çizgisi gezer | Gözcü kaydı |
| `kapi_gecti` | Ön eleme geçti | Figür Kapı'dan Hol'e, oradan Lab'ın boş masasına yürüyüp oturur. Kapı + Lab vurgulanır, balonda onay | Havuz sayısı +1 (Özet, Huni) |
| `kapi_elendi` | Ön eleme kaldı (neden olayda) | Figür geldiği yoldan çıkışa yürür, kapıdan çıkınca kaybolur. Kapı vurgulanır, kırmızı uyarı balonu | Gözcü kaydı (neden) |
| `havuzdan_cikar` | Havuz kuralı: adres düştü | Lab'daki figür kalkar, Kapı'dan çıkıp kaybolur; masa boş sandalye kalır | Havuz −1 |
| `terfi` | Kat geçiş kuralı sağlandı (Lab → Aday → Oda) | Figür masasından kalkıp hedef katın boş masasına yürür (Hol ve kapılardan). İki oda vurgulanır, hedefte yukarı-ok balonu | Kat sayıları, Oda doluluğu |
| `kat_dusur` | Histerezis / zarar kesme: kat düştü | Aynı yürüyüş, ters yönde; aşağı-ok balonu (kırmızı) | Kat sayıları |
| `islem_acildi` | Yeni gölge işlem (yeni sinyal) | İlgili masanın **monitörü parlar** (4 sn), sonra işlem sürdükçe mum grafiği yanık kalır (yeşil kâr / kırmızı zarar). Masanın odası vurgulanır | Açık işlem tablosuna satır; Özet: açık işlem, "bugün açıldı" |
| `islem_kapandi` | İşlem kapandı (trader kapattı / zarar kesme / süre) | Masanın ekranı söner (başka işlem yoksa). **Finans**: kasadan para parıltısı yükselir, duvar eğrisi yanıp söner, oda vurgulanır | Tablo → Son kapananlar (neden, süre, K/Z); kasa ve "bugün K/Z" |
| `bildirim` | Telegram bildirimi gitti | Haberleşme'de posta kutusundan **zarf çıkar**, sağ üste süzülüp kaybolur; Haberleşme duvar ekranı mavi parlar | Telegram kartı: bugün n, son bildirimler |
| `risk_tavan` | Bir risk tavanı doldu (≥ %100) | Risk odasında **alarm lambası** yanıp söner (kırmızı ışık), duvardaki çubuk ekranın çerçevesi kırmızı yanıp söner; oda vurgulanır | Risk kartı: çubuk kırmızı, "TAVAN DOLU" |
| `risk_normal` | Tavan altına indi | Alarm lambası söner; onay balonu | Risk çubuğu normale döner |
| `veri_bayat` | Oda verisi eşikten eski (`yas_dk`) | Oda **renksizleşir** (gri), tabelaya "BAYAT" eklenir, odadaki ekranlar söner; saat balonu | Veri kalitesi satırı sarı "bayat" |
| `veri_taze` | Bayat veri yenilendi | Oda rengine döner, tabela normalleşir | Satır tekrar "tamam" |
| `denetim` | Denetçi sağlama / kalite kontrolü | Sunucu dolabı LED'leri yeşil (tamam) ya da amber (uyarı) olur; Denetim vurgulanır, onay/göz balonu | "Sağlama" satırı |
| `arsiv_yazildi` | Arşive yeni satırlar yazıldı | Arşiv rafı yanındaki yığına **yeni koli** konur (yığın 5'e çıkınca 3'e döner), parıltı | Arşiv satır sayısı |
| `kasa_guncelle` | Kasa değişti (funding vb.) | Finans'ta para parıltısı + duvar eğrisi parlar | Gölge kasası değeri |
| `kural_kitabi` | Kural kitabı / ön kayıt kaydedildi | Sekreterlik'te belge balonu, oda vurgusu | Gözcü kaydı |
| `kullanici_karari` | Kullanıcı kararı işlendi | Makam'da onay balonu, oda vurgusu | Gözcü kaydı |
| `veri_yenile` | Saatlik veri yenilemesi | Finans + Oda vurgulanır | Açık işlemlerde K/Z, lik. uzaklığı güncellenir |
| `sistem` | Örnek akış başa sardı | — (yalnız örnek akışta) | Gözcü kaydı; sayılar ilk veriye döner |

## Ekran ve ışık durumları (olaydan değil, durumdan)
- **Masa monitörleri:** işlemi olan trader'ın ekranı grafik gösterir (yeşil/kırmızı), olmayanınki kapalıdır. Bayat odada tüm ekranlar kapalıdır.
- **Boş koltuk:** boş sandalye olarak çizilir (Oda 14/20 → 6 boş koltuk).
- **Gün ışığı:** gerçek saate göre (sabah turuncu, gündüz açık, akşam alacakaranlık, gece mavi; gece lambalar ve pencereler yanar). Vardiya adı:
  07:00–19:00 gündüz, kalanı akşam. `?saat=SS:DD` ile denenir.

## Süs hareketleri (veri değildir, etiketsizdir)
- **Çaycı:** ~38 sn'de bir Çay ocağından Hol'e yürüyüp döner. Tooltip'i "yalnız ofis süsü" der.
- **Ağaç sallanması:** yaprakların ±1 piksellik salınımı.
Başka hiçbir figür boşta hareket etmez; masadakiler olay olmadıkça kıpırdamaz.

## `prefers-reduced-motion: reduce`
Çizim döngüsü durur (yaklaşık 0,7 sn'de bir yenilenir): yürüme yerine figür hedefine **hemen** geçer, vurgu ve alarm yanıp sönmez
(sabit yanık kalır), zarf/para/koli efektleri sabit çizilir, çaycı yürümez, ağaç sallanmaz, kamera geçişleri anlıktır. Olaylar yine işlenir
(Gözcü kaydı ve paneller güncellenir). `?hareket=0` aynı davranışı zorlar.
