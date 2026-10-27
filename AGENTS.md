# Ajan kuralları (Codex ve diğer ajanlar her oturumda okur)

Bu repo bir copy trade araştırma projesidir (Hyperliquid; 2026-10-27 itibarıyla strateji araştırması kapandı ve silindi). Lider: Claude (denetler, birleştirir). Karar: kullanıcı.

## Başlarken
1. `main`'i çek; işe `main`'den yeni bir dal aç: `codex/<iş-adı>`.
2. Önce `DURUM.md`'yi oku (güncel durum ve kararlar), sonra sana verilen görev belgesini (`docs/GOREV_*.md`).
3. Belgede yazmayan bir karar gerekiyorsa **dur**, soruyu `docs/codex_durum_<iş>.md`'ye yaz; tahminle ilerleme.

## Değişmez kurallar
- **Repo herkese açık:** API anahtarı, şifre, token, kişisel veri asla commit edilmez. Anahtarlar yalnız GitHub
  Secrets'ta; para çekme yetkisi kapalı.
- **Gerçek para, aracı kurum bağlantısı, emir yok.** Paper yalnız sanaldır.
- **Yöntem, kapı, eşik ve karar kodu değişmez** (`docs/KAPI_V3.md`, `copytrade/kurallar.yaml`) — görev belgesi
  açıkça istemedikçe. Yeni ölçümler bilgi amaçlıdır.
- **Testler zayıflatılmaz, atlanmaz, silinmez.** Yeni kod test ile gelir.
- **`main`'e doğrudan push yok.** PR açılır; birleştirmeyi lider yapar.
- Kapı istatistikleri `kapi/istatistik.py`'de, pano sağlık ölçümleri `pano/`'da; yeniden yazma, kullan.

## Kabul kanıtı (2026-10-27, Sol 6.1 denetimi sonrası)
- Hesap değiştiren her PR, elle hesaplanmış **altın örnek** testleriyle gelir (girdi + beklenen sayı).
- Veri üreten işlerde PR açıklamasına çıktı özeti eklenir: satır sayısı, kapsam, her sütunun min/medyan/max'ı.
- "Bitti" yalnız kabul kanıtı ve (varsa) canlı koşu sonucuyla söylenir; hata `|| true` ile örtülmez.
- Lider bu üçü olmadan birleştirmez.

## PR'dan önce
- Tam test paketi: `python -m pytest -q` — sonucu PR açıklamasına yaz.
- PR açılamazsa (yetki/ağ) dalı push etmek yeterli; durum dosyasına not düş.
- Ağ engeli (proxy 403 vb.) varsa uydurma sonuç yazma; işi GitHub Actions iş akışına taşı ya da durumu bildir.

## Dil
Belgeler ve durum notları Türkçe, kısa ve maddeli.
