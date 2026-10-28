# D yolu — kullanıcı kararı bekleyen konular (2026-10-28, lider)

Her madde: ne, neden önemli, seçenekler, lider önerisi, karar verilmezse ne olur. Karar verildikçe tarih ve seçim buraya yazılır.
Görev: `docs/GOREV_D_YOLU.md`.

## Hemen gerekenler (iş bunlarsız başlamaz)

### K1. Faz 0: Sonnet'in kapı dalı `main`'e alınsın mı?
- **Ne:** `claude/kapi-v1-1` dalında düzeltilmiş kapı, kopya defteri (`defter.py`), altın örnek testleri, akıl sağlığı kapısı var. PR'ı yok.
- **Neden:** gölge motoru bu defterin üstüne kurulacak; trader seçimini yeniden yapmak için düzeltilmiş kapıyla tam koşu gerekiyor.
- **Seçenekler:** (a) lider denetler, PR açar, birleştirir, tam koşuyu başlatır; (b) dal bırakılır, gölge motoru sıfırdan yazılır.
- **Öneri:** (a). Sıfırdan yazmak, aynı hataları yeniden yapmak demek.
- **Verilmezse:** hiçbir faz başlamaz.

### K2. Arşiv şimdi, paralel başlasın mı?
- **Ne:** leaderboard fotoğrafı, dolumlar, funding, 1 dk mumlar, olaylar bugünden kaydedilir.
- **Neden:** Hyperliquid geçmişi sınırlı veriyor (dolumda son ~10.000, 1 saatlik mumda ~200 gün). Kaydedilmeyen gün geri gelmez.
- **Seçenekler:** (a) Faz 0 ile paralel; (b) sırası gelince (Faz 2 civarı, birkaç hafta sonra).
- **Öneri:** (a). Arşiv yalnız veri toplar, başka işi etkilemez; "bir iş bitmeden diğeri yok" kuralına tek istisna.
- **Verilmezse:** her gün veri kaybı; 3 ay sonraki analiz o kadar eksik olur.

### K3. Arşiv nerede dursun?
- **Seçenekler:**
  - (a) **Cloudflare R2:** ücretsiz katman yaklaşık 10 GB (doğrulanacak), okuması kolay. Kullanıcı R2 alanı açar, anahtarı GitHub Secrets'a koyar.
  - (b) **GitHub Release dosyaları:** yeni hesap yok; analiz için indirmek zahmetli, dosya başı boyut sınırı var.
  - (c) Git veri dalı: önerilmez, repo şişer.
- **Öneri:** (a).

## Ön kayıttan önce gerekenler (Faz 1)

### K4. Durdurma kriterleri
- **Ne:** hangi sonuçta "olmadı" deyip duracağımız; sonuç görülmeden yazılır.
- **Öneri:**
  1. Geçmiş provada pencerelerin yarısından fazlasında seçilen grup rastgele grubu geçemezse canlı gölgeye başlanmaz.
  2. Hiçbir grup gecikme ve maliyet sonrası kâr etmezse "bu yöntemle Hyperliquid copy trade işe yaramıyor" sonucu sunulur;
     araştırmayı kapatmak geçerli sonuçtur.
- **Neden:** önceden yazılmazsa sonuç kötü çıkınca "biraz daha bekleyelim" denir; eski kapının yaşadığı sorun.

### K5. Canlı gölge süresi ve analiz tarihi
- **Öneri:** en az 12 hafta; performansa yalnız o tarihte bakılır, arada yalnız veri kalitesi.
- **Bilinmesi gereken:** 12 haftada yalnız büyük farklar görünür; "belirsiz" sonucu olası. Uzatma gerekirse kuralı şimdiden yazılır
  (ör. belirsizse 12 hafta daha, bir kez).

### K6. Kat büyüklükleri ve terfi kuralları
- **Ne:** havuz (hepsi gölgede) → aday → oda.
- **Öneri:** aday = havuzun %15'i; oda = 10–20; terfi için en az 3 hafta ve 10 kapanmış işlem gölgede; odadan çıkış için puanın
  aday katının alt yarısına düşmesi (gidip gelmeyi önler).
- **Neden:** kural gevşekse şansa göre terfi olur (Etre'nin riski); sıkıysa oda boş kalır.

### K7. Kopya kuralı varyantlarının sayıları
- **V1 fiyat bandı:** trader girişinden en çok %X uzaksa gir. Öneri: intraday %1, swing %2 (gecikmemiz Etre'den uzun).
- **V2 zaman/zarar çıkışı:** Etre spotta −%30, 18 sa sonra ±%15, 24 sa sonra ±%20. Kaldıraçta teminata göre yazılmalı; öneri:
  teminatın −%50'si zarar kesme, süreye bağlı daralma swing için 7 / 14 gün.
- **Not:** hepsi aynı sinyallerde paralel gölge; kazananı veri seçer.

### K8. Tarama altyapısı ve havuz büyüklüğü
- **Ne:** havuzun tamamını gölgede izlemek 250–300 adresi sürekli taramak demek.
- **Seçenekler:** (a) Worker ücretsiz, adresler sırayla (her adres birkaç dakikada bir; 30 dk / 2 sa gecikme modeline yeter);
  (b) Worker ücretli plan (aylık ücret); (c) havuzu ~50 adresle sınırlamak.
- **Öneri:** (a) ile başla; Faz 2'de Hyperliquid istek sınırları doğrulanınca yetmezse (b).

### K9. İş dağılımı
- **Öneri:** Faz 0 ve denetim lider; arşiv tek ajan; Faz 2–3 (gölge motoru + geçmiş prova) tek ajan, tek dal. Sonnet kapıyı
  bildiği için Faz 2–3'e uygun; Codex izleme/Worker'ı bildiği için arşiv ve tarama altyapısına uygun.

## Sonraki kararlar

### K10. Ofis görünümü ne zaman?
- **Öneri:** ilk canlı gölge verisi gelince (Faz 4). O zamana kadar panoda sade durum tablosu. Her karakter gerçek bir modüle bağlı.

### K11. Otomatik emir (uzun vade)
- **Ne:** Etre'nin asıl gücü saniyelerle kopyalaması; bizde elle kopya 30 dk – 2 sa gecikmeli.
- **Durum:** `AGENTS.md` gereği emir ve gerçek para yok. Bu ancak D yolu olumlu sonuç verirse ve kullanıcı açıkça isterse konuşulur.
