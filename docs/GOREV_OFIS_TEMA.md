# Görev — Ofis tema desteği + "İzometrik minyatür" tema (Codex, 2026-10-29, lider; kullanıcı seçimi)

Kullanıcı seçimi: **İzometrik 3B minyatür, tüm bina kesit görünümü** (oyun gibi ama gerçekçi ışık; sıcak ahşap, krem duvar, yeşil
bitkiler, gri dış kabuk, odalarda Türkçe tabelalar). Referans görsel: `docs/tema/ofis_izometrik_referans.webp` (yapay zekâ üretimi,
1536×1024; repo içi serbest kullanım). Mevcut piksel ofis **aynen kalır ve varsayılandır**.

Kurallar: salt okunur; sahte veri yok (okunamazsa "veri yok"); `gercek.js` veri uyarlayıcısı ve `ofis/SEMA.md` değişmez — tema yalnız
çizim katmanıdır. Testler zayıflatılmaz; yeni davranış testle gelir. PR açılır; birleştirmeyi lider yapar.

## 1. Tema altyapısı (sg-pano/ofis)
- Ayarlar'a "Tema": **Klasik (piksel)** (varsayılan) · **İzometrik**. Seçim `localStorage` (try/catch; okunamazsa varsayılan).
  Adres parametresi `?tema=izometrik` da çalışır.
- Çizici arayüzü: `ciz(data)`, `odaSec(anahtar)`, `temizle()`. Klasik tema bugünkü kodu sarar; panel, olay çekmecesi, oda iç görünümü
  iki temada ortaktır.

## 2. İzometrik tema — sürüm 1: görsel tabanlı (hafif, telefon dostu)
- Referans görsel arka plan (webp, ≤ 400 KB; masaüstü için 1536 px, telefon için 768 px sürüm). Görseldeki her oda için tıklanabilir
  bölge (çokgen, oranlı koordinat; `ofis/tema/izometrik.json`): Finans, Risk, Lab, Arşiv, Kapı, Oda, Makam, Sekreterlik, Çay Ocağı.
- Her odanın üstüne canlı **rozet**: Finans → kasa ve %; Risk → en kötü ışık + kalabalık uyarısı; Lab → veri tazeliği; Oda → 18 trader,
  🟢/🟡/🔴 sayıları; Kapı → son tarama; Arşiv → arşiv durumu; Makam → hafta ve kararlar; Çay Ocağı → rozet yok (süs).
- Odaya dokununca hafif yakınlaşma (CSS transform) + mevcut oda paneli açılır. Yakınlaştırma/kaydırma parmakla; "Binaya dön" düğmesi.
- Dokunma alanları ≥ 44 px; rozetler 390 px ekranda okunur.

## 3. Sürüm 2 (sonra, ayrı görev): gerçek 3B (Three.js, düşük poligon, aynı tarz). WebGL yoksa ya da cihaz zayıfsa sürüm 1'e döner.

## Teslim
PR; testler (tema seçimi kalıcılığı, geri dönüş, bölge→oda eşleşmesi, rozet verisi sentetik fikstürle); telefon ve masaüstü ekran
görüntüsü (iki tema).
