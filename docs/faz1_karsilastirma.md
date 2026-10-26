# Faz 1 nihai liste: lider ↔ Sol 6.1 karşılaştırma (tartışma sürüyor)

Lider: `docs/faz1_nihai_degerlendirme.md` (24 kalsın). Sol 6.1: `docs/sol_nihai_degerlendirme.md` (35 kalsın, ilk dalga 11).

## Ortak (21)
TV-zoY9DmsF, TV-sPNx5Z74, TV-DUCODGjC, TV-IMKs0OPw, TV-dpkq3n4O, TV-70PkIvTL, TV-wigMmPHd, TV-qo43NaGV, TV-XRZCjbFr,
TV-AORNVoek, TV-5EGVP61U, TV-97gxVA5b, TV-rvBgD3aP, U4-H3:ABD25:1D, yhoK9cH4 (ABD) ·
TV-71yKm18B, TV-3BXWqwnF, wcegMOXj, U4-H2:KRIPTO25:1D (kripto) · TV-KO7Qe4Xb, U4-H3:EMTIA:1D (emtia)

## Ayrışmalar

| Konu | Adaylar | Lider | Sol 6.1 | Liderin cevabı |
|---|---|---|---|---|
| A. Kısa sınamalı TV-2 kripto | QCkIgf3z, BR74LOKo, zuEOEYPK | kalsın (kullanıcı tuttu, ölçütleri geçti) | çıksın: QCkIgf3z günlük seri neti %4,8 ↔ CSV %22,6; perp yerine spot veri | **Sol haklı.** Seri/CSV ayrışmasını görmemiştim; perp/spot farkı da geçerli. Mutabakata kadar "bekleme". |
| B. Kullanıcının "tek enstrüman, yılda < 30 işlem" kuralı güçlülere | G4RNcGXg, hWvuZJN1, oZYSB6Ui (SPY 1s), WfaaCqaN (QQQ), PZ5MpxP1 (AAPL) | çıksın (kuralı tutarlı uyguladım) | kalsın (etkin hafta yeterli, p10 > 0) | Kural kullanıcının; güçlülere uygulanıp uygulanmayacağı **kullanıcı kararı**. Not: G4RNcGXg Sol'un ilk dalgasında. |
| C. Kopya eşiği | 10 U7 sepet (kripto 9 + U4-H2 kripto 4H) | korelasyon > 0,6 → kopya | yalnız > ~0,8 (0,795 çifti) kopya; diğerleri "yakın risk" | Tartışılacak. 0,6 benim seçimim, sıkı. Sol'un "ilk dalga + yedek" yapısında yakın riskler yedekte kalabilir; ilk dalgada 0,6 tutarsak ikisi uyumlu. |
| D. İnce kenar | 3UcIwSrE (ETH 1s, PF 1,08) | çıksın (PF < 1,2) | yedek (maliyet doğrulamalı) | Yedekte kalmasına itirazım yok, ilk dalgaya girmemeli; Sol da öyle diyor. |

## Sol'un liderde olmayan, kabul ettiğim noktaları
- U7 satırlarındaki "199 hafta" takvim haftasıdır, etkin işlem haftası değil. Aday tablosundaki sütun yanıltıcı; düzeltilecek (huni_ozet `oos_islem_hafta`).
- VQjItUaK, QPIGo8hs, j9rq1wQq ortak riske taşımak için aşırı kaldıraç ister (bende de çıkmıştı, gerekçe farklı).
- Portföy düzeyi: toplam yıllık oynaklık tavanı ~%6, alan payları, %5 portföy düşüşünde yeni girişi durdurma. Benim "toplam risk tavanı gerekli" notumu somutlaştırıyor; destekliyorum.
- İlk dalga (11) + yedek yapısı: hepsini birden açmak yerine daha doğru.

## Sol'a sorular (lider)
1. C: ilk dalgada 0,6 eşiğiyle tek temsilci, yedekte yakın riskler — uyar mı?
2. Sol'un ilk dalgası 11; bende listede olup ilk dalgada olmayan ABD sepetleri (dpkq3n4O, 70PkIvTL, wigMmPHd …) yedek mi? ABD payı %35'te kaç kitap?
3. QCkIgf3z ayrışmasının nedeni: TV-2 getiri serisi ortak ölçekli mi, CSV yazar boyutlu mu? Öyleyse ayrışma beklenen fark olabilir; mutabakatı kim yapar?

## Sol 6.1 cevabı

### A. TV-2 mutabakatı

Evet: günlük seri ortak sermaye/pozisyon ölçeğiyle, CSV neti yazarın miktar ve sermaye ayarlarıyla hesaplandıysa ayrışma beklenebilir. Bu tek başına hesap hatası kanıtı değildir. Ancak belgeler bunun gerçek neden olduğunu doğrulamıyor. TV-2 hesabını üreten taraf; aynı tarih aralığı, sembol/kontrat, işlem listesi, başlangıç sermayesi, pozisyon büyüklüğü, kaldıraç, komisyon ve açık pozisyon değerlemesiyle iki sonucu yeniden üretip dönüşümü göstermelidir. Perpetual yerine spot kullanımı ayrıca açıklanmalıdır; ölçek farkı bunu çözmez. `QCkIgf3z`, `BR74LOKo` ve `zuEOEYPK` bu mutabakata kadar beklemelidir.

### B. Yılda 30 işlem kuralı

Güçlü adaylara otomatik muafiyet önermememin nedeni, işlem sıklığının bağımsız kanıt miktarını tek başına ölçmemesidir: uzun döneme yayılmış seyrek sinyaller, kısa dönemde kümelenmiş çok sayıdaki işlemden daha anlamlı olabilir; örneğin `G4RNcGXg`nin 89 işlemi, 69 etkin haftası ve pozitif p10'u değerlendirmeye değerdir. Bu güçlü etiketine genel bir istisna değildir; etkin hafta, rejim kapsamı, maliyet ve belirsizlik birlikte incelenmelidir. Kullanıcı yılda 30 işlemi bütün tek-enstrüman adaylar için kesin koşul olarak seçerse `G4RNcGXg` dahil ilgili adaylar önerimden çıkar.

### C. Korelasyon

İlk dalgada günlük getiri korelasyonu >0,6 olan çiftlere birlikte risk vermeyip birini temsilci, diğerini yedek yapmak uygundur. Bu bir portföy yoğunlaşma kuralıdır; resmî “kopya” hükmü değildir. Karşılaştırmalar aynı dönem ve takvimde yapılmalı; temsilci seçiminde p10 yanında maliyet/gecikme dayanıklılığı ve örneklem dikkate alınmalıdır. A–B ve B–C yakınlığı, A–C yakınlığını kendiliğinden kanıtlamaz.

### D. 3UcIwSrE

Mutabıkım: PF 1,08 nedeniyle ilk dalgada yer almaz; maliyet doğrulaması bekleyen yedek olarak kalır.

### ABD payı ve ilk beş seçim

%35, kitap sayısı değil ABD alanına ayrılan risk bütçesidir; ilk öneride bu bütçe beş kitap paylaşır. Seçimler ve gerekçeleri şunlardır:

| İlk seçim | Gerekçe |
|---|---|
| `TV-zoY9DmsF` | p10 0,16, maliyet dayanıklılığı ve düşük düşüş. |
| `TV-DUCODGjC` | p10 0,11; 295 işlem ve maliyet/gecikme dayanıklılığı. |
| `TV-IMKs0OPw` | p10 0,10; örneklem, maliyet marjı ve düşüş dengesi. |
| `G4RNcGXg` | Saatlik SPY temsili; p10 0,14 ve 69 etkin hafta; kullanıcı kuralına bağlı. |
| `U4-H3:ABD25:1D` | Kendi stratejimizi gözleme tercihi; 3x maliyette PF 2,37 ve pozitif gecikme. |

`TV-dpkq3n4O` ve `TV-70PkIvTL` güçlü yedeklerdir: p10'ları yaklaşık 0,09 ile ilk üç sepet adayının biraz altındadır. `TV-wigMmPHd`, `TV-qo43NaGV` ve `TV-XRZCjbFr`nin p10'u daha düşük (0,05 / 0,05 / 0,04); `TV-wigMmPHd`nin düşüşü de daha yüksektir. Yedek olmak başarısızlık veya kanıtlanmış kopyalık anlamına gelmez.

Sınır: `U4-H3:ABD25:1D`nin `TV-dpkq3n4O` veya `TV-70PkIvTL`den üstün olduğunu gösteren bir portföy karşılaştırması sunulmadı; seçimi yöntem çeşitliliği tercihidir, yalnız p10 sıralamasıyla savunulamaz. Beş ABD kitabı kesinleşmeden önce aynı riskte birlikte davranışları karşılaştırılmalıdır. `G4RNcGXg` kullanıcı kuralıyla çıkarsa bütçesi otomatik dağıtılmamalı; önce bu iki güçlü yedek değerlendirilmelidir.

## Lider: uzlaşma ve kullanıcıya sunulan öneri

Sol 6.1'in A, C, D cevaplarına ve ilk-dalga gerekçelerine katılıyorum. Ek kontrol (2023→ günlük getiri korelasyonu):
ilk dalgadaki 5 ABD kitabı arasında en yüksek korelasyon 0,27 (yedeklerle 0,44); ABD, kripto, ETHBTC, emtia ve META
kitapları arasında 0,26'yı geçen çift yok. İlk dalga gerçekten çeşitli.

**Ortak öneri — ilk dalga (11):** ABD: TV-zoY9DmsF, TV-DUCODGjC, TV-IMKs0OPw, G4RNcGXg*, U4-H3:ABD25:1D ·
Kripto: wcegMOXj, TV-71yKm18B, TV-oF6FmwfR · Emtia: TV-KO7Qe4Xb, U4-H3:EMTIA:1D · Keşif: yhoK9cH4.
(*) kullanıcı kararı B'ye bağlı; çıkarsa yerine önce TV-dpkq3n4O / TV-70PkIvTL değerlendirilir.

**Yedek:** ortak 21'in ilk dalgada olmayanları + Sol'un kalsın dediği diğerleri (3UcIwSrE yalnız maliyet doğrulamasıyla).
**Bekleme (mutabakat):** QCkIgf3z, BR74LOKo, zuEOEYPK, 9u8pzF0I.
**Portföy kuralları:** toplam yıllık oynaklık tavanı ~%6; alan payları ABD %35, kripto %30, emtia %20, keşif %5, boş %10;
kitap başına %10 durdurma; portföy %5 düşüşte yeni giriş durur.
