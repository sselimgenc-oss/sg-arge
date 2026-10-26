# Ajan kuralları (Codex ve diğer ajanlar her oturumda okur)

Bu repo bir sistematik işlem araştırma projesidir. Lider: Claude (denetler, birleştirir). Karar: kullanıcı.

## Başlarken
1. `main`'i çek; işe `main`'den yeni bir dal aç: `codex/<iş-adı>`.
2. Önce `DURUM.md`'yi oku (güncel durum ve kararlar), sonra sana verilen görev belgesini (`docs/GOREV_*.md`).
3. Belgede yazmayan bir karar gerekiyorsa **dur**, soruyu `docs/codex_durum_<iş>.md`'ye yaz; tahminle ilerleme.

## Değişmez kurallar
- **Repo herkese açık:** API anahtarı, şifre, token, kişisel veri asla commit edilmez. Anahtarlar yalnız GitHub
  Secrets'ta; para çekme yetkisi kapalı.
- **Gerçek para, aracı kurum bağlantısı, emir yok.** Paper yalnız sanaldır.
- **Yöntem, kapı, eşik ve karar kodu değişmez** (`docs/TEST_YAPISI.md`, `paper/portfoy.yaml` ağırlık/risk kuralları,
  `results/` karar tabloları) — görev belgesi açıkça istemedikçe. Yeni ölçümler bilgi amaçlıdır.
- **Testler zayıflatılmaz, atlanmaz, silinmez.** Yeni kod test ile gelir.
- **`main`'e doğrudan push yok.** PR açılır; birleştirmeyi lider yapar.
- Mevcut motoru kullan (`engine/`, `backtests/tv2.py`, `backtests/tarama.py`); yeni backtest yöntemi icat etme.

## PR'dan önce
- Tam test paketi: `python -m pytest -q` — sonucu PR açıklamasına yaz.
- PR açılamazsa (yetki/ağ) dalı push etmek yeterli; durum dosyasına not düş.
- Ağ engeli (proxy 403 vb.) varsa uydurma sonuç yazma; işi GitHub Actions iş akışına taşı ya da durumu bildir.

## Dil
Belgeler ve durum notları Türkçe, kısa ve maddeli.
