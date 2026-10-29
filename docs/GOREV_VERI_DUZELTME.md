# Görev — Canlı veri doğruluğu düzeltmeleri (Sonnet ya da Codex, 2026-10-30, lider)

Dayanak: Sol 6.1 bağımsız canlı veri denetimi (`arastirma/copytrade/sol_canli_veri_denetimi/DENETIM_CANLI_VERI_2026-10-30.md`;
Hyperliquid API ile karşılaştırmalı). Öncelik: `DURUM.md` "önce veri" kuralı; K‑7 takvimi (canlı en geç 31.12).
Kurallar: yöntem, eşik ve kurallar.yaml değerleri değişmez; sahte veri yok; testler zayıflatılmaz/silinmez; yeni davranış testle.
PR'ları lider birleştirir (sg-pano kısmı Sol denetimiyle Sonnet birleştirebilir).

## sg-arge (izleme motoru)
1. **Olay arşivi kesilmesin (yüksek):** `olaylar` tüm kollarda ortak sıralanıp `[:200]` alınıyor; bir yoğun taban trader'ı (B17) listeyi
   22 dakikada dolduruyor; 29.10'da 733 oda olayından 722'si listede yok. Çözüm: kesilmemiş olay arşivi (R2 ya da günlük ayrı dosya,
   veri dalında ≤ 90 MB), `durum.json`'da kol başına son N olay + günlük sayaçlar (`gunluk_sayac`: kol, açılış/kapanış, trader sayısı)
   ve `olay_kapsami` (başlangıç zamanı, tam mı). Pano ve Worker günlük özeti sayaçları buradan okur.
2. **Tek fiyat eksiği trader'ı düşürmesin (yüksek):** B17'de tek bir 1 dk mum eksikliği (mkts:US500) bütün trader'ı geçersiz yapıyor.
   Fiyatlanamayan eylem açık "fiyatsız" durumla taşınsın (sayılır, raporlanır), diğerleri hesaplansın.
3. **Perp hesabı sıfır olanlar (orta):** K02, K06, K09, K11, B02, B07'de güncel perp hesap 0 (spot bakiye var). Bunlar "veri yok" değil
   "perp hesabı boş/kapalı" durumu; ayrı durum kodu ve panoda açık etiket. Kontrol/taban üyeliği değişmez (ön kayıt); analizde
   kapsam dışı sayımı raporlanır.
4. **Geçersizler toplamlara geçerli gibi girmesin (yüksek):** `gecerli=false` (eski sonuç ya da 1.000 $ yer tutucu) trader'lar kasa ve kol
   toplamlarında ayrı sayılsın; `durum.json`'a kol başına `kapsam` (geçerli / eski / yer tutucu sayısı).
5. **Zaman damgası (orta):** `uretildi` koşu başlangıcı; trader başına gerçek okuma zamanı (`veri_zamani`) ve dosyanın yayım zamanı ayrı.
6. **Sanal defter şeffaflığı (orta):** `kopya_paydasi` ve sanal açık lotlar (coin, yön, miktar, gecikmeli giriş fiyatı, işaret fiyatı ve
   zamanı) `durum.json`'da yayımlansın; kasa tablosu bunlardan üretilebilsin. O10 sanal bakiyesi −52,87 $ (getiri −%105): negatif bakiye
   davranışını teşhis et (likidasyon/taban kuralı ön kayıtta nasıl?), raporla.
7. **Mutabakat ikiye ayrılsın (orta):** "trader geçmişi" (90 gün dolum ↔ borsa; O02 LITE, O10 COPPER kapanışı geçmişte görünmüyor)
   ile "sanal defter" uyumsuzluğu ayrı ışık; hesap sıçraması yatırma/çekme kanıtı değil "teşhis" diye yazılsın.

## sg-pano
8. **Kasa açık işlemler tablosu sanal lotlardan (yüksek):** bugün trader'ın güncel pozisyonları hesap değeriyle ölçekleniyor (+2.968 $),
   gerçek sanal açık K/Z −64 $. Tablo madde 6'daki sanal lotlardan; satır yüzdesi o lotun; "nakit" sanal defterden.
9. **Kol üyeliği `kollar` ile (yüksek):** E01 `kollar=[elle, kontrol]`; kontrol 18 sayılmalı (pano 17). Kontrol getirisi %1,18459,
   oda − kontrol −7,96 puan (pano −8,03). Ana etiket ile deney kolu ayrı.
10. **Son kapananlar** açılış olayına bağlı `sanal_sonuc`'tan değil, kapanış kayıtlarından (madde 1).
11. Kapsam etiketleri: "açık işlem 1.014 (tüm trader pozisyonları) / oda 135" gibi; geçersiz/eski sayısı toplamların yanında.

## Teslim
Her madde için test; sg-arge ve sg-pano ayrı PR; Sol 6.1'e tekrar denetim için kısa not (hangi maddeler kapandı).

## Ek (lider, 2026-10-30 gece denetimi) — Faz 3 ve kalıcılık koşuları
12. **Faz 3 bitemiyor (yüksek):** `faz3.yml` ilk üç pencere (2026-03-28, 04-11, 04-25) 350 dk süre sınırında sonuçsuz iptal oldu;
    pencere başına iş binlerce adres × ~1 dk. Bu tasarımla 12 pencerenin hiçbiri bitmez. Çözüm: pencere başına evreni ön kayıtlı
    bir örnekleme (ör. kapı adım 1–2'yi geçen havuz, sabit tohum) ya da adres parçalama + ara sonuç önbelleği (kaldığı yerden
    devam); her pencere ≤ 5 sa. Önce tek pencerelik deneme koşusu.
13. **Kalıcılık sonucu sayısal olarak bozuk (yüksek):** 29.10 koşusu yeşil ama dilim ortalamaları milyonlarca (ör. D1 17.476.474),
    "trader getirisi 109.527.699" — payda (pencere hesap değeri medyanı) sıfıra yakın hesaplarda getiri patlıyor. Rapor bu haliyle
    yorumlanamaz. Çözüm (ön kayıtlı, deneme defterine yeni satır): asgari payda (ör. hesap değeri ≥ kapı tabanı), getiri kırpma
    ya da sıra tabanlı ölçü (dilim içi medyan + Spearman); sentetik doğrulamaya "küçük payda" vakası ekle. Ardından yeniden koşu.
14. **Kararsız test (orta):** PR #421'in CI koşusunda `tests/test_kalicilik.py` skor testi bir kez başarısız (calmar/kar_ay
    beklenen değerden farklı); yerelde 6/6 ve sonraki CI'lar yeşil. Sıra/ortak durum bağımlılığını bul ve düzelt.
