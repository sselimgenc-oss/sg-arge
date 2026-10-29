# Görev — Ofisi canlı izlemeye bağla (Codex, 2026-10-29, lider; kullanıcı: ofisteki tüm odalar aktif olsun)

Bağlam: Pilot 2026-10-29'da başladı. `sg-pano/ofis/gercek.js` yalnız `secim.json` + kapı `durum.json` okuyor; onayı bilmiyor
(`onaylandi: false` sabit, şerit "ön izleme, onaylanmadı"), Lab/Finans/Risk "paper izleme başlamadı" diye gri, Gözcü kaydı boş.
Canlı izleme verisi zaten var: `sg-arge` `copytrade-izleme` dalı `izleme/durum.json` (saatlik; ana pano bunu okuyor).

Kurallar: salt okunur; sahte veri yok (okunamazsa hata/"veri yok"); `docs/VERI_SOZLESMESI.md` yalnız isteğe bağlı alanla genişler.
**Körlük kalktı (ön kayıt 1.5, kullanıcı 2026-10-29):** kâr/zarar, kasa, kol toplamları ve oda ↔ kontrol karşılaştırması gösterilir;
"kilitli · hafta x/12" yazıları kaldırılır. Testler zayıflatılmaz; yeni davranış testle gelir. PR açılır; birleştirmeyi lider yapar.

## İş
1. **Onay ve hafta:** `izleme/durum.json`'daki traderlar seçim etiketini (`secim` = `<secim_surumu>@<kapı tarihi>`, izleme
   listesinden) taşıyorsa ve en son `secim.json` ile eşleşiyorsa `secim.onaylandi = true`; şerit "Seçim v1.3 — pilot, hafta x/12"
   (x = t0'dan bu yana tam hafta + 1). Alan motor çıktısında yoksa `sg-arge` `izleme_motoru` trader satırına `secim` alanını
   (izleme listesinden aynen) ekleyen küçük bir PR da açılır (sözleşmede isteğe bağlı alan olarak).
2. **Lab (gölge defteri):** `durum.json` `uretildi`/`veri_zamani` → veri kalitesi `lab` (tamam/uyari/bayat). Gri kalkar.
3. **Gözcü kaydı / olaylar:** `durum.json`'daki işlem açılış/kapanış olayları (adres kısa adı, coin, yön, zaman, K/Z).
4. **Risk:** oda üyelerinin kaldıraç ve sağlık ışığı.
5. **Finans:** kasa (sanal kopya bakiyesi), oda ve kontrol toplamları, "Kararlarım değer kattı mı?" (yönetilen oda ↔ sabit referans
   oda; referans kolu yoksa bugünkü oda referanstır). **Bütün odalar aktif**, hiçbiri gri değil (veri yoksa "veri yok").
5b. **Ana pano (`index.html`):** "kilitli · hafta x/12" kilitleri kaldırılır: sanal kopya (hepsi), kol toplamları, kohort ↔ kontrol,
   trader başı getiri ve K/Z'ye göre sıralama açılır. README "Performans körlüğü" maddesi güncellenir.
6. Testler: `node ofis/test/gercek.test.js`, `node ofis/test/gercek_ui.test.js` (+ yeni sentetik `durum.json` fikstürü);
   `node tools/surum.js` ile sürüm damgası.

## Teslim
PR; telefon ve masaüstü ekran görüntüsü.

## Ek — sabit referans kolu (sg-arge, ön kayıt 1.5 madde 3)
`copytrade/secim.py` `izleme_listesi`: yeni bir seçim sürümü odayı değiştirdiğinde, v1.3 odası ve kontrolü listeden düşmez;
`kollar`'a `referans_oda` / `referans_kontrol` eklenir, `t0` ve `id` değişmez (yeniden oynatma yok). Motor ve Worker bu kolları
sessiz izler (bildirim yalnız `oda`). Test: oda değişince eski oda üyesi `referans_oda` olarak kalır.
