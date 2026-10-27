# Görev: Telegram bildirimi — Cloudflare Worker (İş B) + motor düzeltmeleri (2026-10-27, lider)

Yapan: **Codex** (PC masaüstü uygulaması, yerel mod; ağ gerekir). Dal: `codex/telegram`. Tek PR, `main`'e; lider birleştirir.
Kaynaklar: `docs/VERI_SOZLESMESI.md` (v1.2), `arastirma/copytrade/argon_worker_teknik.md`, `copytrade/izleme_motoru.py`.

**Değişmez:** sistem emir göndermez, borsa hesabına bağlanmaz; düğmeler yalnız karar kaydeder. Anahtar ve token repoya,
günlüğe, hata mesajına, PR metnine yazılmaz. Repo herkese açık.

## 0. Önce motor düzeltmeleri (Python, `copytrade/izleme_motoru.py`)
1. **Olayları emir (`oid`) düzeyinde üret.** Bir emir birden çok dolumla gelir; dolum dolum bakınca tek açılış sonrası
   sahte "büyütme" olayları çıkar. Aynı `oid`'nin dolumlarını birleştir: önceki pozisyon = ilk dolumun `startPosition`'ı,
   sonraki = son dolumdan sonra. Tür kuralları aynı (açılış / kapanış / >%25 büyütme-azaltma; yön dönüşü = kapanış + açılış).
2. **Olay kimliği:** `{trader}-{oid}-{tur}` (ör. `T1-123456789-acilis`); ışık olayı değişmez. Eski kimlikli olaylar
   `motor.json`'dan atılır (yalnız test trader'ları var, karar kaydı yok). Worker aynı kimliği üretir — karar ↔
   `sanal_sonuc` eşleşmesi buna bağlı.
3. Tek trader'ın API/veri hatası koşuyu durdurmasın: o trader önceki başarılı kaydıyla ve `saglik.nedenler`'e
   `"veri hatası: <kısa neden>"` eklenerek yazılır; diğerleri güncellenir. Tüm trader'lar hatalıysa yayımlanmaz.
4. 1 dk mum penceresi (5.000 dk) kaçarsa kalıcı hata yerine eksik dolum için 1 saatlik mumun açılışı kullanılır ve
   `sanal_kopya`'ya `"not": "yaklaşık fiyat"` yazılır (sözleşme v1.2).
5. İlk koşuda (`saved['isik']` yokken) ışık olayı yazılmaz; yalnız değişimde.
6. `izleme.yml`'den `codex/izleme` push tetiğini kaldır.
7. **Kararları içe al:** saatlik iş, Worker'ın `GET /kararlar` adresinden kayıtları çeker ve `copytrade-izleme` dalında
   `izleme/kararlar.jsonl`'a yazar (olay_id başına son karar; sözleşme §4 alanları). Adres `izleme.yml`'de değişken
   (`KARAR_URL`, GitHub *variable*, secret değil); boşsa adım atlanır.

## 1. Worker (`worker/`, JavaScript, ücretsiz plan)
- **Depo: D1** (KV değil; tekrar bildirim olmasın). Tablolar: `imlec(trader, son_dolum)`, `bildirilen(olay_id PK, zaman)`,
  `kararlar(olay_id PK, zaman, karar, neden)`, `isik(trader, isik)`.
- **Cron `*/5 * * * *`:**
  1. `durum.json`'u ham GitHub adresinden oku (trader listesi, `hesap_degeri`, pozisyon kaldıraçları, ışık).
     Okunamazsa bu tur atlanır.
  2. Her trader için tek istek: `userFillsByTime` (`startTime` = imleç). HIP-3 dolumları (`xyz:` önekli) bunda gelir;
     dex başına ayrı sorgu gerekmez. Spot dolumlar (`@…`, `…/…`) atılır. Alt istek: ~20 trader + 1 + Telegram < 50.
  3. Olayları §0.1 kuralıyla üret (Python ile **aynı** sonuç: ortak test dosyası `tests/fixtures/olaylar.json` —
     girdi dolumları + beklenen olaylar; hem pytest hem Worker testi bunu okur).
  4. Yalnız `acilis`, `kapanis`, `buyutme` bildirilir (azaltma bildirilmez). `INSERT OR IGNORE INTO bildirilen` başarılıysa
     gönderilir; böylece aynı `olay_id` iki kez gitmez.
  5. `durum.json`'daki ışık bir trader için `kirmizi`ya döndüyse bir kez bildir.
  6. **İlk çalışmada imleç = şimdi** (geçmiş olaylarla telefon dolmasın). 429/ağ hatasında 1–2 sn sonra tek tekrar;
     olmazsa o trader bu tur atlanır, imleç ilerlemez.
- **Mesaj** (sözleşme §5): `🟢 Test-1 · BTC LONG açtı · giriş 68.400 · hesabın %8'i · 2x · Binance: var`
  (kapanış 🔴/⚪, büyütme 🔵, ışık 🔴; Türkçe sayı biçimi; saat Türkiye). Altında panoya bağlantı.
- **Düğmeler** (yalnız `acilis`/`buyutme`): `[Açtım] [Atladım]`; Atladım → `[Geç gördüm] [Beğenmedim] [Bakiye yok]
  [Diğer]`. `callback_data` ≤ 64 bayt (ör. `k|<olay_id>|a` / `k|<olay_id>|s|g`).
- **Webhook `POST /telegram`:** `X-Telegram-Bot-Api-Secret-Token` doğrulanır; yalnız `TELEGRAM_CHAT_ID`'den gelen kabul;
  `answerCallbackQuery` hemen; karar D1'e (yeniden basılırsa son karar geçerli); `editMessageReplyMarkup` ile düğmeler
  kalkar ve mesajın altına "✅ Açtım" / "⏭ Atladım — geç gördüm" eklenir.
- **`GET /kararlar`:** salt okunur, yalnız sözleşme §4 alanları (tutar/isim yok; kayıt zaten açık repoya gidiyor).
- **Komut:** `/durum` → her trader için ışık + açık pozisyon sayısı + veri yaşı (tek mesaj). Başka komut yok.

## 2. Kurulum (kullanıcı yalnız GitHub Secrets'a girer; ayrıntılı adımları PR metnine yaz)
- GitHub Secrets: `CLOUDFLARE_API_TOKEN` (yalnız "Edit Cloudflare Workers" + D1 yetkisi), `CLOUDFLARE_ACCOUNT_ID`,
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_WEBHOOK_SECRET` (rastgele uzun metin).
- `.github/workflows/worker.yml`: `worker/**` değişince ve elle: testler → `wrangler deploy` → secret'ları GitHub
  Secrets'tan Worker'a aktar → D1 tablolarını oluştur (idempotent) → `setWebhook` (secret_token ile). D1 veritabanı
  yoksa iş oluşturur; kimliği `wrangler.toml`'a elle yazdırma gerektirmeyen yolu seç.
- Secret'lar yoksa iş anlaşılır bir mesajla durur; değer hiçbir yerde yazdırılmaz (`::add-mask::`).

## 3. Testler (ağsız)
Python: oid birleştirme (çok dolumlu tek emir → tek açılış), kimlik biçimi, tek trader hatası, mum yedeği, ilk koşu ışık.
Worker (`node --test` veya vitest): ortak fixture ile olay eşitliği; tekrar bildirim yok; ilk çalışma imleci; spot atlama;
webhook gizli başlık / yabancı chat reddi; callback ayrıştırma ve 64 bayt; mesaj biçimi.

## 4. Kabul
- `python -m pytest -q` ve Worker testleri yeşil; CI yeşil.
- Kullanıcı secret'ları girince: Worker yayında, `/durum` cevap veriyor, test trader'larının yeni işleminde bildirim ve
  düğmeler çalışıyor, karar bir saat içinde `copytrade-izleme/izleme/kararlar.jsonl`'da ve panoda görünüyor.
- `docs/codex_durum_telegram.md`: yapılanlar, seçimler, bilinen sınırlar.
