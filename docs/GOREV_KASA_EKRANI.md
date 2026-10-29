# Görev — Kasa ekranı (Codex, 2026-10-29, lider; kullanıcı Etre ekranını örnek gösterdi)

Etre'nin **kodu kopyalanmaz** (GPL); yalnız düzen fikri alınır. Salt okunur, sahte veri yok (okunamazsa "veri yok").
Veri: `copytrade-izleme/izleme/durum.json` (saatlik). Yalnız `oda` kolu kasaya girer; kontrol karşılaştırma satırıdır.
Testler zayıflatılmaz; yeni davranış testle gelir. PR açılır; birleştirmeyi lider yapar.

## İş (sg-pano, ana panoda yeni sekme `#kasa`; telefon öncelikli, dokunma ≥ 44 px)
1. **Üst kart:** kasa ($, oda sanal kopya toplamı), başlangıçtan % ve $; altında kontrol kolunun aynı ölçüsü (tek satır).
2. **Kasa eğrisi:** oda toplamının zaman serisi (veride yoksa sg-arge'de `durum.json`'a isteğe bağlı `kasa_egri` alanı ekleyen
   küçük PR: saatlik nokta, son 90 gün; sözleşmeye isteğe bağlı alan olarak).
3. **Dört kutu:** nakit (serbest), açık teminat, gerçekleşmemiş K/Z, son 24 sa (açılan/kapanan işlem, kazanma oranı).
4. **Açık işlemler tablosu:** coin, trader takma adı, süre, kaldıraç, likidasyona uzaklık, teminat, K/Z $ ve %; toplam satırı.
5. **Son kapananlar:** coin, kapanış nedeni (trader kapattı / yön değiştirdi / likidasyon), süre, K/Z $ ve %.
6. Sade Türkçe (LONG/SHORT yerine "alış/satış yönü" ipucu), tek terim: "sanal kasa".
Testler: `node test/pano.test.js` + yeni sentetik fikstür; telefon ekran görüntüsü.
