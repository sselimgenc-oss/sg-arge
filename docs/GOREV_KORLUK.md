# Görev — Sağlık ışığı körlüğü (K‑6 b) (Sonnet, 2026-10-29, lider)

Bağlam: Denetim B31. Sağlık ışığı bugün trader'ın t0 sonrası getirisini performans konisiyle kıyaslıyor
(`copytrade/izleme_motoru.py` ~207–242: "koni %5 altında", "koni %5–%20 bandında"). Işık panoda ve Telegram `/durum`'da kol
ile birlikte göründüğü için pilot süresince performans bilgisi sızdırıyor. Ön kayıt madde 6: arada yalnız veri kalitesi.

Kurallar: kapı, seçim, eşik ve karar kodu değişmez; `analiz_d.py` değişmez. Eşikler yalnız `kurallar.yaml`. Testler
zayıflatılmaz; değişen davranış yeni altın örnekle gelir. main'e doğrudan push yok; PR açılır.

## İş
1. `sg-arge`: sağlık ışığı yalnız şunlara bakar: veri hatası/bayatlık, kaldıraç (mevcut kural), likidasyon mesafesi (veri varsa).
   Koni ve K/Z'ye dayalı nedenler pilot süresince hesaplanmaz. Koni kodu silinmez: `kurallar.yaml` `saglik_performans_konisi:
   false` (pilot), `true` yalnız analiz tarihinden sonra. Mevcut koni testleri `true` ile aynen geçer; `false` için yeni test.
2. `durum.json` sözleşmesi (`docs/VERI_SOZLESMESI.md`) değişmez; `saglik.nedenler` yalnız izinli nedenleri taşır.
3. `sg-pano`: panoda kol ile birlikte trader'ın t0 sonrası toplam getirisini ya da K/Z eğrisini gösteren yer varsa pilot
   süresince "kilitli · hafta x/12" yazar (kol toplamlarında olduğu gibi). Tek tek işlem satırları kalır.
4. Testler: `pytest` ve `node test/pano.test.js` yeşil.

## Teslim
İki PR (sg-arge, sg-pano). Açıklamada: hangi neden kaldı, hangi ekran kilitlendi, ekran görüntüsü (telefon genişliği).
