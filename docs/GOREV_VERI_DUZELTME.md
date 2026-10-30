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
    pencere başına iş binlerce adres × ~1 dk. Bu tasarımla 12 pencerenin hiçbiri bitmez. Çözüm sırası: 1) dolum geçmişi
    önbelleği (her adres bir kez indirilir, 12 pencere aynı önbellekten; R2 arşivi kullanılabilir), 2) T anında ucuz ön eleme
    (portfolio: hesap değeri, aktiflik) — pahalı dolum yalnız elemeyi geçenlere, 3) gerekirse sabit tohumlu ön kayıtlı örneklem
    (raporda yazılır; küçük havuz yöntemi kötümser gösterir). Kaldığı yerden devam; her iş ≤ 5 sa. Önce 1 pencere × 50 hesap deneme.
    **K‑7a ile öncelik düştü:** kalıcılık (13) önce; Faz 3 zaman kalırsa.
13. **Kalıcılık sonucu sayısal olarak bozuk (yüksek):** 29.10 koşusu yeşil ama dilim ortalamaları milyonlarca (ör. D1 17.476.474),
    "trader getirisi 109.527.699" — payda (pencere hesap değeri medyanı) sıfıra yakın hesaplarda getiri patlıyor. Rapor bu haliyle
    yorumlanamaz. Çözüm (ön kayıtlı, deneme defterine yeni satır): asgari payda (ör. hesap değeri ≥ kapı tabanı), getiri kırpma
    ya da sıra tabanlı ölçü (dilim içi medyan + Spearman); sentetik doğrulamaya "küçük payda" vakası ekle. Ardından yeniden koşu.
14. **Kararsız test (orta):** PR #421'in CI koşusunda `tests/test_kalicilik.py` skor testi bir kez başarısız (calmar/kar_ay
    beklenen değerden farklı); yerelde 6/6 ve sonraki CI'lar yeşil. Sıra/ortak durum bağımlılığını bul ve düzelt.

## Ek 2 (lider, birleşik derin denetim — K‑9 onaylı) — Sonnet
Kaynak: `docs/DENETIM_TRADER_2026-10-30.md` + Codex derin denetimi (bulgu no'ları `C#`). Sıra: önce 15–19 (teknik), sonra 20–23 (v2), sonra 24–25.
Her madde test ile; önce küçük gerçek veri denemesi (AGENTS.md kalite kuralı 1); çıktıyı gerçek `durum.json`'da göster.

**Teknik / gösterim (onay gerekmez)**
15. **Geçerlilik ayrımı (C#3, C#8):** `gecerli` yerine durum kodu `tamam | fiyatsiz | perp_bos | okuma_hatasi | bayat`. 1.000 $ yer
    tutucu yayımlanmasın (`yer_tutucu=true` ya da null). Pano/Worker toplamları: geçerli alt toplam + geçersiz/eski alt toplam + kapsama %;
    üye sayısı (ITT) sabit gösterilir. Tek coin fiyatsızsa yalnız o coin ölçüm dışı (dışlama günlüğü), trader düşmez.
16. **Olaylar ve 24 saat (C#5):** `olaylar[:200]` kesmesi 24 saat sayacını bozuyor (200 olay ≈ 30 dk). Kol/gün sayaçları motorda
    hesaplansın (`sayac_24s`: açılış, kapanış, trader, kazanma); pano/Worker bunları kullansın. Arşiv şişmesi notunla birlikte çöz.
17. **Eğri = kasa (C#4):** `kasa_egri` üyeliği `kollar` ile; eğrisi olmayan "eksik kapsama". Son nokta kasa ile mutabık değilse uyarı.
18. **Eksik işaret fiyatı (C#9):** `mark_missing>0` satır ve kasa `eksik_degerleme=true`; pano "bilinmiyor" gösterir. Ofis teminat
    `null`'u 0 toplamasın (C#13).
19. **Worker (C#10, C#11, G1):** günlük özet "06:00 UTC sonrası ve bugün gönderilmedi" koşuluyla (kaçarsa telafi, "gecikmeli" etiketi);
    durum okuma/dolum/tetikleme hataları D1 sağlık kaydına + alarm; `GET /kararlar` anahtar ile (Secrets), pano okumuyorsa 404 iddiası kalksın.
    Zaman alanları (C#16): `kosu_baslangic`, `kosu_bitis`, trader `veri_zamani`, kol bazında en eski yaş.

**Kopya hesap v2 (K‑9: v1 silinmez, yan yana)**
20. **Tek motor (C#1):** canlı `copy_results` ile `golge.calistir` aynı yürütme + tasfiye fonksiyonunu kullansın. Altın örnek testi:
    aynı girdi → aynı sonuç (O10 dahil).
21. **Tasfiye / taban (C#2, K3):** sanal özsermaye ≤ 0 → tasfiye, bakiye 0'da kalır, `tasfiye_zamani` yayımlanır. O10 v2 değeri raporlanır.
22. **Zamanla değişen payda (C#7, K2):** `kopya_paydasi` sabit değil; `capital_scale` hesap değeri zaman serisiyle (saatlik okumalar;
    t0–ilk okuma arası veri yoksa ilk okuma, `payda_yontemi` etiketiyle). O10 13.629→28.550 vakası testte.
23. **Funding yalnız kopyalanan pozisyondan (K4):** t0 öncesi devralınan, kopyalanmayan pozisyonların funding'i sanal kasaya yazılmaz;
    sanal lot büyüklüğü × oran. Sanal açık lotlar `durum.json`'da (madde 6/8 ile birleşir); kasa tablosu yalnız bunlardan.

**Tanısal (K‑9: birincil analiz değişmez)**
24. **`gecikme5` kolu:** oda adresleri 5 dk gecikmeyle paralel v2 sanal kopya; Telegram yok; panoda oda yanında tek satır.
25. **Risk tanısı:** oda brüt kaldıraç (Σ|notional| / sermaye) ve en büyük tek coin payı yayımlansın; tavan (önce `kurallar.yaml`)
    aşılırsa uyarı. Eksik veri >%5 ise karar fonksiyonu `sinanamadi` döner (C#15). Oda–kontrol denge tablosu (coin, yön, kaldıraç,
    sıklık) tanısal rapor (C#14).

Teslim: her grup (15–19, 20–23, 24–25) ayrı PR; Sol'a tekrar denetim notu.

## Sadeleştirme (K‑10) — Sonnet; kurallar `AGENTS.md` 4–8
Hedef: her iş tek yerde. Ayrı yeniden yazım değil; aşağıdaki sırayla mevcut maddelerin içinde. Her adımda önce/sonra sayılar aynı
(ya da fark açıklanmış) olmalı; PR'da tablo.
- **S1 Hesap yalnız motorda (15–19 ile birlikte):** pano `kasaToplam`/`ortalama`/24 saat sayımı, ofis `gercek.js` 1.000 $ ölçekleme ve
  teminat, Worker günlük özet hesapları `durum.json`'a hazır alan olarak taşınır (`kol_ozet`: kasa, getiri, kapsama, `sayac_24s`, teminat);
  üç ekran yalnız okur. Ekranlarda kalan hesap kodu listelenip silinir.
- **S2 Tek motor (20–23 ile birlikte):** `izleme_motoru.copy_results` → `golge.calistir` (tek yürütme/kırpma/tasfiye/payda/funding).
  Canlıda kopyalanan ikinci defter mantığı kalmaz.
- **S3 Tek veri kaynağı:** dolumlar bir kez çekilir (arşiv → R2); motor oradan okur, eksikse yalnız eksik aralığı çeker. Worker dolum
  çekmez; bildirimi `durum.json`/olay arşivinden üretir. Önce 1 saatlik gerçek veriyle eşitlik denemesi (olay sayıları aynı).
- **S4 Şema testi:** `docs/VERI_SOZLESMESI.md` ↔ `durum.json` makine okunur şema (`copytrade/sema_durum.json`); motor çıktısı her
  testte şemaya karşı doğrulanır; pano/ofis/Worker okuduğu her alan şemada olmalı.
- **S5 Belge ve ölü kod:** görev dosyaları tek listede (`GOREV_VERI_DUZELTME.md`); biten/askıdaki görev dosyaları `docs/arsiv/`'e taşınır
  (silinmez). Kullanılmayan modül/iş akışı listesi çıkarılır; arşive alma kullanıcı onayıyla.
Ölçü: PR açıklamasında "kaldırılan yinelenen kod satırı" ve "aynı sayıyı hesaplayan yer sayısı" önce/sonra.
