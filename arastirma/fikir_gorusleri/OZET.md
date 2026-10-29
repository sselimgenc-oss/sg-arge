# Fikir görüşleri — lider özeti (2026-10-29)

6 dış görüş okundu. Görüşler veri sayılır; karar kullanıcıdadır. Kaynak bağlantıları lider tarafından doğrulanmadı.
Not: "18+18+18+8 = 62, 61 değil" sorusu: bir adres iki kolda (`kollar`), izleme listesi 61 satır. Hata değil.

## Altısının ortak görüşü
1. **Asıl sorun fikir azlığı değil, düşük istatistik gücü.** Yeni oda / pencere / kural eklemek gücü daha da böler ve
   şans eseri "kazanan" bulma riskini büyütür. En olası dürüst sonuç: "büyük fark yok" ya da "henüz bilinmiyor".
2. **Öncelik 1 (6/6): #4 mutabakat + veri doğruluğu.** Kopya ↔ trader pozisyon sağlaması, yetim pozisyon, kaçan dolum,
   para yatırma/çekme sıçramaları, 10.000 dolum sınırı. Yanına #6 pano sadeleştirme (sağlık ışığı).
3. **#11 paralel deney + deneme defteri (5/6).** Yeni kurallar canlı odada değil arşivde, önceden yazılarak sınanır;
   toplam deneme sayısı tutulur (Deflated Sharpe ve aşırı uyum hesabının girdisi). Sonuçlar "keşif" etiketli kalır.
4. **Kâra bakmayan sinyaller (5/6): #12b anti-martingale, #8 tarz kayması, #12d kopya kapasitesi.**
   Trader değiştirme gerekçesi bunlar olmalı; #7 karantina tetiği kâr değil tarz kayması olmalı.
5. **Tuzak uyarısı (6/6):** #5 futbol, #7 karantina, #9 kayıp soğuması kâr/zararla tetiklenirse veri gözetlemedir.
   #2 atak oda kapıdaki kaldıraç sınırıyla çelişir; #1 spot ayrı bir araştırma sorusudur (düşük öncelik).

## Somut önlemler (kullanıcının "gerekçeli değiştirme" hakkı için)
- **Gerekçe kodu listesi:** kaldıraç ihlali, tarz kayması, hareketsizlik, veri sorunu, anti-martingale davranışı,
  "araştırmacı takdiri" (ayrı işaretli). "Kötü gitti" geçerli kod değil.
- **Değişiklik tavanı:** ör. 4 haftada en çok 2.
- **Çıkarılanı izlemeye devam:** çıkan ve giren trader 4–8 hafta izlenir → "değişim alfası" (kararlarım değer kattı mı?).
  Oda düzeyinde sabit referans kolu zaten var; trader düzeyi eklenir.
- **Karar ekranında son getiriyi gizle** (bir görüş); karar günlüğü (tarih, gerekçe kodu, o anki veri).

## Listede olmayan, birden çok görüşün önerdiği fikirler
- **A. Tüm arşivde kalıcılık testi (3/6, gücün asıl çözümü):** her 2 haftada tüm hesapları seçim skoruna göre 5 dilime
  ayır, sonraki 4–8 haftanın gecikmeli kopya getirisine bak. Skor işe yarıyorsa üst dilimden alta düzenli düşüş görülür.
  18'e 18 canlı oda kanıt değil doğrulama olur. (#3 performans pencereleri bu çerçevede, 3–5 pencere önceden yazılarak.)
- **B. Sanal olduğu için ölçüm kolunu büyüt:** 100 oda + 100 kontrol izlemek gücü ek maliyetsiz artırır (bir görüş).
- **C. Plasebo oda dağılımı:** aynı seçim prosedürüyle 1.000 rastgele oda; gerçek oda dağılımın neresinde?
- **D. Oda içi kalabalıklaşma:** 18 trader düşüş günlerinde aynı pozisyonda mı (kuyruk korelasyonu)?
- **E. Funding / hedge ayrıştırması:** getirisi funding arbitrajından gelen hesabın yalnız perp bacağını kopyalamak yanıltır.
- **F. Rejime göre değerlendirme** (trend / yatay) ve çok faktör (BTC + ETH + altcoin sepeti).
- **G. Ekonomik karar eşiği:** "sıfırdan büyük mü" değil "uğraşa değer mi" (ör. haftalık net %0,25 ya da yıllık %20).

## Az veriyle karar: önerilen yöntem (görüşlerin ortak paydası)
- Ana ölçüt: haftalık, BTC'den arındırılmış **oda − kontrol farkı**; trader ya da saat değil.
- **Bayesçi rapor:** şüpheci başlangıç (fark ~ 0 ± yıllık %30); her ay `P(fark > 0)` ve `P(fark > %20/yıl)`.
  Önceden yazılı eşikler, ör.: P(fark > %20) > %70 ve P(fark > 0) > %95 → umut verici; P(fark > %20) < %10 → durdur;
  arası → belirsiz, odaya dokunma. Üst sınır 26 hafta.
- **Her hafta bakılacaksa:** her-an-geçerli sıralı test (e-değeri / mSPRT); ya da yalnız 4., 8., 12. haftada önceden
  belirli bakış. Bir görüş: zarar tarafında daha gevşek, başarı tarafında daha sıkı eşik.
- **Trader düzeyinde büzülme (shrinkage):** sıralama ham getiriyle değil, grup ortalamasına çekilmiş tahminle.
- Faz 3 notu: 60 gün ileri / 14 gün adım pencereleri ~4 kat örtüşür; "yarısından fazlası" bağımsız kanıt değil.
  Örtüşmeyen pencereler ayrıca raporlanmalı (Argon A22 bulgusuyla uyumlu).

## Lider önerisi (sıra; kullanıcı onayı gerekir)
1. **Mutabakat sağlık ışığı + pano sadeleştirme** (Codex; pano işinin devamı).
2. **Değiştirme kuralları:** gerekçe kodu, tavan, çıkarılanı izleme → ön kayıt 1.6 (kullanıcı kararı).
3. **Arşivde kalıcılık testi + deneme defteri** (Sonnet; Faz 3 altyapısını kullanır). Alternatif kurallar (#12a–d)
   burada keşif olarak sınanır.
4. **Haftalık Bayesçi özet** panoda tek satır: "oda kontrolün önünde olma olasılığı %X" (sonra).
Ertelenen: #1 spot, #2 atak oda, #5 futbol, #9 kayıp soğuması.
