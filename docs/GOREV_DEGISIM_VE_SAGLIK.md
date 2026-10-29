# Görev — Oda değişim kaydı (ön kayıt 1.6) + mutabakat sağlık ışığı (Codex, 2026-10-29, lider)

Kurallar: yöntem/eşik değişmez; değerler yalnız `kurallar.yaml`'da (1.6 bloğu). Testler zayıflatılmaz; yeni davranış testle gelir.
Sahte veri yok. Repo herkese açık: anahtar/kişisel veri yok. PR açılır; birleştirmeyi lider yapar.

## A. Değişim kaydı (sg-arge)
1. `copytrade/gecis.py`: `neden` alanı `degisim_gerekce_kodlari`ndan biri olmalı (değilse hata). Eski kayıtlar bozulmaz.
2. Tavan: yeni çıkış yazılırken son `degisim_tavan_gun` günde `degisim_tavan_disi` dışındaki çıkış sayısı `degisim_tavan_adet`e
   ulaştıysa yazma reddedilir ve nedeni söylenir. Test: 3. çıkış reddedilir; `kaldirac_ihlali` sayılmaz.
3. Kolay kullanım: `python -m copytrade.gecis --cikar <adres> --al <adres> --gerekce <kod> [--not "..."]` hem kaydı yazar hem
   izleme listesini günceller (yeni üye `oda`, `t0` = bugün; çıkan `cikarilan`). Lider bunu kullanıcı isteğiyle çalıştırır.
4. `cikarilan` kolu: `izleme_motoru` KOLLAR'a eklenir; Worker bildirim göndermez; `cikarilan_izleme_gun` dolunca satır listeden düşer
   (kayıt kalır). Sabit referans kolları etkilenmez.
5. Rapor: `copytrade/degisim_rapor.py` → `izleme/degisim.json` (veri dalı): her değişiklik için tarih, çıkan, giren, gerekçe,
   o tarihten bu yana giren ve çıkanın sanal kopya getirisi ve fark ("değişim alfası"); gerekçe koduna göre toplam
   (`kullanici_takdiri` ayrı). Saatlik izleme işinde üretilir.

## B. Mutabakat sağlık ışığı (sg-arge + sg-pano)
`izleme_motoru` oda için zaten `veri_kalitesi.mutabakat` üretiyor. Bunu tek ışığa indir: yeşil / sarı / kırmızı + kısa neden
(yetim pozisyon, kaçan dolum oranı, pozisyon oranı farkı, hesap değeri sıçraması = yatırma/çekme şüphesi). Eşikler `kurallar.yaml`'a
yeni anahtar olarak (lider onayıyla; PR'da önerilen değerleri gerekçesiyle yaz).
sg-pano: ana panonun en üstüne tek bakış kartı: "🟢 Her şey yolunda / 🟡 İzle / 🔴 Dikkat" + yapılacak bir şey var mı (Argon A24
madde 1–2). Değişim kaydı ve değişim alfası "Kararlarım" bölümünde. Telefonda dokunma alanları ≥ 44 px.

## Teslim
İki PR (sg-arge, sg-pano); test çıktısı; telefon ekran görüntüsü.
