# Fikir defteri

Durum etiketleri: **düşünülüyor** (karar yok, görev yok) · **seçildi** (görev yazılacak) · **reddedildi** (gerekçesiyle).
Fikirler uygulanmadan önce bu defterden seçilir; ön kayıt ve körlük kurallarıyla çelişen kısım seçimde açıkça yazılır.

## 2026-10-29 — Seçim v1.3 sonrası geliştirme fazı için (kullanıcı)

| # | Fikir | Durum | Lider notu |
|---|---|---|---|
| 1 | **Spot odası** (şu an yalnız kaldıraç) | düşünülüyor | HL spot sığ (HIP tokenları, memecoin); etre'nin en kötü sonuçları spot memecoin'deydi. Kapı ölçütleri perp için kurulu; spot ayrı kapı ister. Önce perp sonucu. |
| 2 | **Atak (>10x) / dengeli (3–10x) / temkinli (≤3x)**, para buna göre bölünür | düşünülüyor | Trader'ın kaldıracı ≠ bizim kaldıracımız: yüksek kaldıraçlı trader küçük ölçekle kopyalanabilir. Sepet = trader tarzı × bizim ayırdığımız para/ölçek. v1.3 havuzu 10x üstünü dışlıyor; "atak" ayrı, küçük deney kolu olabilir. |
| 3 | **Performans pencereleri:** 1 hafta, 1 ay, 1–3, 3–6, 6–12 ay iyi olanlar | düşünülüyor (öncelikli aday) | "Hangi geçmiş geleceği taşır" sorusu. Etre'de 1 hafta ≈ 0 öngörü; sentetikte 12 hafta isabet %30. Havuzun tamamı gölgede olduğundan ucuz: her pencerenin puanı haftalık geri bildirim raporunda karşılaştırılır. Deneme kolu etiketiyle (çoklu test). |
| 4 | **Kurumsal ofis bölümleri:** eksik olanlar (Ar-Ge, bilgi işlem…) | düşünülüyor | Eksik: **Operasyon/mutabakat** (yetim pozisyon), **Bilgi işlem/sistem sağlığı** (izleme sıklığı, arşiv), **İç denetim**. Boş: Risk, Finans. Her oda gerçek bir sistem işlevine bağlanırsa ofis sağlık panosu olur. |
| 5 | **Futbol takımı:** ilk 11 (oda), yedekler (aday), U19 (havuz), U16 (keşif); gelişen üst takıma çıkar | düşünülüyor | Rotasyonu ve v1.3 geçiş kaydını anlatır (transfer haberi, kadro değişikliği). Körlük: performans sayısı değil, yalnız kural olayı gösterilir ("terfi: ≥3 hafta + ≥10 işlem"). |
| 6 | **Panoda boşuna kalabalık yapan bölümler** | düşünülüyor | Denetimden: Keşif/Huni hep örnek veri (düzelt ya da kaldır), tazelik uyarısı sürekli kırmızı, trader sayfası sağlık ışığı körlükle çelişiyor. Kullanıcı hiç açmadığı bölümleri söyleyecek. |

**Birleşik görünüm (lider):** 2 + 3 + 5 tek yapı olabilir — takım = risk profili (para), yaş grubu = performans penceresi
(seçim sinyali), ofis = futbol dili (sunum). Hepsi çaprazlanırsa hücreler 2–3 trader'a düşer ve ölçülemez; önerilen ilk adım
3'ü yalnız ölçüm olarak eklemek, 4–6 hafta sonra hangi pencerenin işe yaradığına bakmak.

## 2026-10-29 — Argon A18'den (gerçek işlem fazı için)

| # | Fikir | Durum | Lider notu |
|---|---|---|---|
| 7 | **Karantina / sermaye kesintisi:** uyarı bandındaki trader'ın payını %50 indir, 2–4 hafta izle | düşünülüyor | Paper pilotta anlamı sınırlı; gerçek işlemde risk aracı. |
| 8 | **Tarz kayması tespiti:** işlem sıklığı, varlık evreni ve yön asimetrisi sapması | düşünülüyor | `bayrak_ek` ve tarz sütunlarıyla ölçülebilir. |
| 9 | **Günlük kayıp soğuması:** tek günde büyük kayıpta 24 saat kopyalamama | düşünülüyor | Performansa dayalı; pilot sırasında körlükle çelişir. |
| 10 | **Lider tablosu dışı keşif** (evreni büyütmenin asıl yolu) | düşünülüyor | Sayım: lider tablosu 47.849 hesapla sınırlı; eşik düşürmek evreni yalnız %10 büyüttü. |
