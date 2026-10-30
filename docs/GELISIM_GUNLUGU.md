# Gelişim günlüğü — sg-arge (Etre biçimi: tarih-saat, ne değişti, hangi ölçümü etkiledi, test sayısı)

Kronolojik, en yeni üstte. İkinci doğru kaynak değil: kararların ayrıntısı `DURUM.md`, `docs/KARARLAR_D.md` ve
görev belgelerinde durur; burada yalnız hangi değişikliğin hangi ölçümü/veriyi etkilediği kısaca kayıtlıdır.

## 2026-10-30 — E1: veri hattı sağlığı (Etre `kalite.py` karşılığı)
- `copytrade/saglik_hatti.py` eklendi: oda kolu için tek sağlık kaydı (veri tazeliği, yetim gölge payı, işaret
  eksikliği, veri hata oranı, sinyal gecikme medyanı) → ışık + neden listesi. Saf fonksiyonlar (`olc`/`kontrol`),
  Etre deseni. **Performans ışığından (`traderlar[].saglik.isik`) ayrı** — bu, veri hattının kendi sağlığı.
- `izleme_motoru.run()` her koşuda `durum.json["saglik_hatti"]` yazıyor (izleme listesi boşken eklenmiyor).
- Worker `checkStateAlerts` kırmızıya geçişte Telegram uyarısı gönderiyor (yeşil/sarıdan kırmızıya; aynı kırmızıda tekrarlamaz).
- `docs/VERI_SOZLESMESI.md` v1.6: yeni alan belgelendi.
- Küçük gerçek veri denemesi: canlı `durum.json` (91 trader, `uretildi` 2026-10-30T14:20Z) üzerinde dört kol için
  çalıştırıldı. Oda: n=18, veri_tazeliği 39 dk, yetim_golge_orani 0,37%, sinyal_gecikme_dk_medyan ≈ 41 dk, **ışık yeşil**.
  Kontrol: veri_hata_orani %11 → sarı. Havuz (t0 30.10, 1 gün yeni): veri_hata_orani %20 → **kırmızı** (gerçek bulgu:
  yeni eklenen havuz trader'larında veri hata oranı oda'dan yüksek; izlenecek).
- Test: `tests/test_saglik_hatti.py` 6 altın örnek (elle hesap) + `tests/test_izleme.py` (70, regresyon yok) +
  `worker/test/bildirim.test.js` 2 yeni (toplam 9) — hepsi yeşil.
- Önce: `LICENSE` (GPL-3.0) + `NOTICE` eklendi (Etre v2 · Trading Office atfı, K-11).

## 2026-10-30 — K-11: Etre geçişi başladı
- Kullanıcı kararı: Etre'nin üstün olduğu her alan (mimari, veri hattı, risk/çıkış, pano/ofis, sim gerçekçiliği,
  mühendislik) devşirilir; güvenlik (gerçek para/emir/cüzdan yok), ölçüm yöntemi ve seçim mantığı korunur.
  Lider: Claude (Sonnet 5), tek lider ve birleştirme yetkili. Denetçi: Codex (Sol). Görev: `docs/GOREV_ETRE_GECIS.md`.
