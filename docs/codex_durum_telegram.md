# Codex durum — Telegram Worker

- Dal: `codex/telegram`; kapsam yalnız `docs/GOREV_TELEGRAM.md`.
- İş B: emir gönderme, borsa hesabı bağlantısı veya token/anahtar dosyası yok.
- Motor v1.2: olaylar dolum değil `oid` düzeyinde üretilir; kimlik
  `{trader}-{oid}-{tur}`. Aynı emrin çoklu dolumu tek olaya iner. Eski
  dolum-karmalı işlem olayları motor arşivinden kaldırılıp eldeki dolumlardan
  yeniden üretilir; ışık olayları korunur.
- Bir trader'ın API/veri hatasında önceki başarılı kartı ve olayları kalır;
  sağlık nedenlerine kısa `veri hatası:` notu eklenir. Bütün trader'lar
  hatalıysa arşiv yayımlanmaz.
- 1 dk mum geçmiş penceresi kaçırılmışsa aynı gecikme hedefinin 1 saatlik
  mum açılışı kullanılır ve sanal kopya `not: yaklaşık fiyat` taşır.
  İlk sağlık hesaplaması ışık olayı üretmez.
- `worker/`: ücretsiz Cloudflare Worker + D1. D1, imleçleri, gönderilmiş
  olayları, kararları ve ışıkları saklar. Worker hiçbir GitHub yetkisi
  tutmaz. Saatlik Actions, `KARAR_URL` GitHub variable'ı tanımlıysa
  Worker'ın salt-okunur `/kararlar` yanıtını `kararlar.jsonl` içine alır.
- Worker her 5 dakikada durum dosyasını ve trader dolumlarını okur; spotu
  atlar, ilk turda imleci başlatır, 429 için bir kez bekleyip tekrar dener.
  `acilis`, `kapanis`, `buyutme` ve kırmızı ışık bildirilebilir; D1 tekil
  anahtarı tekrar bildirimi engeller. Webhook yalnız doğru Telegram gizli
  başlığı ve sohbet kimliğiyle kabul edilir.
- Ortak `tests/fixtures/olaylar.json`, Python ve JavaScript'te aynı oid
  olaylarını doğrular. Kurulum/dagıtım için gereken secret adları PR
  açıklamasında yer alır; değerleri kullanıcı GitHub'a girer.
