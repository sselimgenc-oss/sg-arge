# Görev — Kopya botu, aşama 1: emir GÖNDERMEYEN karar + kayıt motoru (Codex, 2026-10-30, lider)

Dayanak: K‑7 / K‑7a (`docs/KARARLAR_D.md`): 1.12.2026 küçük tutarla otomatik canlı. Bu aşamada **hiçbir emir gönderilmez, hiçbir anahtar
kullanılmaz** (`AGENTS.md` "emir yok" kuralı geçerli). Amaç: canlıda çalışacak kodun tamamı, emir gönderme satırı hariç, hazır ve
2 hafta "canlı fiyatla gölge" koşabilecek durumda. Repo herkese açık: anahtar, kişisel veri yok. Testler zayıflatılmaz; yeni kod testle.
Eşikler `kurallar.yaml`'a yeni `bot_*` anahtarları (kullanıcı onayı gereken değerler PR'da "öneri" diye işaretli). PR'ı lider birleştirir.
Ön bilgi: Argon araştırması gelirse `arastirma/copytrade/argon_bot_*.md` (Hyperliquid agent anahtarı, SDK, emir türleri).

## Kapsam
1. **Sinyal:** canlı oda üyelerinin dolumları (mevcut Worker/izleme mantığı, emir/oid düzeyinde birleşik olaylar) → hedef pozisyon
   (sanal kopya ile aynı ölçek kuralı: sabit kopya paydası, trader hesap payı × bot sermayesi). Gecikme kuralı ön kayıttaki gibi
   (gün içi 30 dk, swing 2 sa) — ayrıca "gecikmesiz" kip ayarı (varsayılan kapalı; canlı kararı kullanıcının).
2. **Karar:** hedef − mevcut = emir taslağı (coin, yön, miktar, tür: IOC limit, reduce-only kapanışta). Kayma koruması: trader girişinden
   `bot_kayma_tolerans` (kripto %0,5 / diğer %1,5 öneri) kötüyse atla ve kaydet. Asgari emir büyüklüğü altında kalanı atla ve kaydet.
3. **Limitler (sert, kod içinde aşılmaz):** işlem başı en çok tutar, en yüksek kaldıraç, günlük zarar limiti (aşılınca o gün yeni emir yok),
   toplam zarar limiti (aşılınca tam duruş), aynı anda en çok açık pozisyon. Hepsi `kurallar.yaml`.
4. **Durdurma:** Telegram `/dur` (yeni emir yok) ve `/dur kapat` (tüm pozisyonları kapatma taslağı), `/devam`; durum D1'de; yalnız
   kullanıcının chat_id'si.
5. **Mutabakat:** her saat bot defteri ↔ (aşama 1'de) gölge defter; uyumsuzlukta otomatik duruş + Telegram uyarısı.
6. **Kayıt:** her karar (gönderilecek/atlanan + neden) yalnız eklenen günlükte (R2 ya da veri dalı ≤ 90 MB); panoda "bot (gölge)" satırı
   ve günlük özet satırı: karar sayısı, atlanan, limit tetiklenmeleri.
7. **Emir arayüzü:** `gonder(emir)` tek fonksiyon; aşama 1'de yalnız kaydeder. Gerçek gönderim kodu yazılmaz; yerine arayüz + sahte
   (test) uygulama. (Aşama 3'te, kullanıcı onayıyla, para çekme yetkisi olmayan agent anahtarıyla eklenecek.)
8. **Çalışma yeri:** Cloudflare Worker (dakikalık cron zaten var) önerilir; gerekçesiyle PR'da.

## Testler
Altın örnekler: ölçekleme, gecikme, kayma atlaması, her limitin tetiklenmesi, /dur, mutabakat duruşu, aynı olayın iki kez emre
dönüşmemesi (kimlik), ağ hatasında güvenli davranış (emir yok, kayıt var). Sentetik bir günün uçtan uca yeniden oynatması.

## Teslim
PR + kısa sade Türkçe özet (kullanıcıya: bot ne yapıyor, ne yapmıyor). Aşama 2 (15–28.11 canlı fiyatla gölge) bu kodla başlar.
