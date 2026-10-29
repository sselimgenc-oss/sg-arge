# Görev — Ofisi canlı izlemeye bağla (Sonnet, 2026-10-29, lider; öncelik: KORLUK ve PILOT_VERI'den sonra)

Bağlam: Pilot 2026-10-29'da başladı. `sg-pano/ofis/gercek.js` yalnız `secim.json` + kapı `durum.json` okuyor; onayı bilmiyor
(`onaylandi: false` sabit, şerit "ön izleme, onaylanmadı"), Lab/Finans/Risk "paper izleme başlamadı" diye gri, Gözcü kaydı boş.
Canlı izleme verisi zaten var: `sg-arge` `copytrade-izleme` dalı `izleme/durum.json` (saatlik; ana pano bunu okuyor).

Kurallar: salt okunur; sahte veri yok (okunamazsa hata/"veri yok"); `docs/VERI_SOZLESMESI.md` değişmez. **Körlük:** kasa değeri,
kol toplamı, kol karşılaştırması, trader başı toplam getiri ve puan gösterilmez (pilot boyunca "kilitli · hafta x/12").
Testler zayıflatılmaz; yeni davranış testle gelir. PR açılır; birleştirmeyi lider yapar.

## İş
1. **Onay ve hafta:** `izleme/durum.json`'daki traderlar seçim etiketini (`secim` = `<secim_surumu>@<kapı tarihi>`, izleme
   listesinden) taşıyorsa ve en son `secim.json` ile eşleşiyorsa `secim.onaylandi = true`; şerit "Seçim v1.3 — pilot, hafta x/12"
   (x = t0'dan bu yana tam hafta + 1). Alan motor çıktısında yoksa `sg-arge` `izleme_motoru` trader satırına `secim` alanını
   (izleme listesinden aynen) ekleyen küçük bir PR da açılır (sözleşmede isteğe bağlı alan olarak).
2. **Lab (gölge defteri):** `durum.json` `uretildi`/`veri_zamani` → veri kalitesi `lab` (tamam/uyari/bayat). Gri kalkar.
3. **Gözcü kaydı / olaylar:** `durum.json`'daki işlem açılış/kapanış olayları (adres kısa adı, coin, yön, zaman); K/Z rakamı yok.
4. **Risk:** oda üyelerinin kaldıraç ve sağlık ışığı (KORLUK görevinden sonraki hâli: yalnız veri kalitesi ve risk).
5. **Finans:** kilitli kalır ("kilitli · hafta x/12"), gri değil.
6. Testler: `node ofis/test/gercek.test.js`, `node ofis/test/gercek_ui.test.js` (+ yeni sentetik `durum.json` fikstürü);
   `node tools/surum.js` ile sürüm damgası.

## Teslim
PR; telefon ve masaüstü ekran görüntüsü.
