# Durum: Seçim v1 (dal `claude/secim-v1`)

- [x] `copytrade/secim.py` (havuz, puan, aday, oda, kontrol, taban, elle, RAPOR, `--izleme-listesi`)
- [x] `kurallar.yaml`: `secim_aday_orani`, `secim_oda_min/max`, `secim_min_kapsam` (0,95: kullanıcı kararı 2026-10-28)
- [x] Altın örnekler `tests/test_secim.py` (12 satır); Worker testi `worker/test/events.test.js` (`kol = oda` bildirir, diğerleri sessiz)
- [x] `izleme_motoru`: `kol`, `kollar` alanları kabul edilir ve `durum.json`'a taşınır (`docs/VERI_SOZLESMESI.md` v1.5)
- [x] İş akışı `copytrade_secim.yml` (elle; veri dalına `secim/<tarih>/`)
- [x] Kırmızı bayraklar (`copytrade/bayrak.py`, `tests/test_bayrak.py`): `bayrak_rol`, `bayrak_vault_orani`, `bayrak_funding_payi`, `bayrak_alt_hesap_ters`,
      `bayrak_hacim_orani` (+ `bayrak_not`); yalnız aday katı, `secim.json` ve RAPOR bölümü; eşik yok, kimseyi elemez; `--bayraksiz` ağ isteğini kapatır.
- [ ] **Gerçek RAPOR bekliyor: veri dalındaki son koşu HIZLI koşudur (92 satır, kapsam 0,0067); tam koşu yok.** Seçim yalnız `durum = tamam` ve
      kapsam ≥ 0,95 ile çalışır; tam koşu bitince lider PR'ı birleştirir, `CALISTIR` değişikliği `main`de `CT-Seçim v1` iş akışını başlatır ve RAPOR özeti PR açıklamasına eklenir.
- [ ] **RAPOR: tam koşu bekleniyor.** Tarama `tamam` olmadan seçim tetiklenmez.

## Kararlar / varsayımlar (belgede yazmıyordu; lider denetlesin)
- `secim_min_kapsam` = 0,95 (kullanıcı kararı 2026-10-28; lider denetimi).
- Havuz ayrıca `tarz ∈ {intraday, swing}` ister (scalp tarz kovasına girmez).
- Aday sayısı = ceil(0,15 × tarzdaki puanı > 0 sayısı). Eşitlikte adres sırası.
- Oda boyutu = min(20, ilişki elemesinden sonra kalan aday); tarz kotası ilişki elemesinden ÖNCEKİ aday payıyla (en büyük kalan yöntemi);
  bir tarz kotasını dolduramazsa kalan yer öbür tarzdan aynı sırayla (genç olmayan, puan) dolar.
- İlişkili adresler yalnız aday katında karşılaştırılır; `iliskili_adresler` sütunu kapı `sonuc.csv`'sine `kesif` adımıyla yazılır.
- Kontrol sırası `sha256("<tohum>-<adres>")`; kütüphane sürümünden bağımsız ve tekrarlanabilir.
- Bir adres birden çok kolda olabilir: `kol` = oda > elle > taban > kontrol > aday > havuz; tamamı `kollar`'da. Bildirim `kol = oda`.
- Worker: `kol` alanı olmayan trader artık bildirmez (eski liste `kol` almadan çalıştırılırsa sessiz kalır).
- Taban lider tablosunu Hyperliquid'den çeker (`--taban-dosyasi` ile dosya verilebilir); bulut oturumundan erişim yok → Actions.
- Bayrak hesapları: `bayrak_rol` = `vault` | `subAccount:<master>` | diğer rol adı; funding payı = 365 gün `userFunding` toplamı / aynı dönem `closedPnl` toplamı
  (PnL 0 ise boş); vault oranı ve hacim oranı paydası kapı satırındaki güncel hesap değeri; hacim = `portfolio` `month` penceresi `vlm`;
  alt hesap kontrolü master'ın alt hesapları + (alt hesapsa) master'ın kendi pozisyonları.

## Seçim v1.3 — iş paketi A (`docs/GOREV_SECIM_V13.md`)
- [x] Havuz: adım 3 statik koşulları (kısa işlem payı, medyan ve en yüksek kaldıraç; `kapi.py` ile aynı eksik-veri kuralı)
- [x] Kontrol: odayla ayrık, tarz × en yüksek kaldıraç dilimi eşleştirmeli; `ikincil_kontrol` = havuz − oda; tohum = `secim-<sürüm>-<kapı tarihi>`
- [x] Seçim kimliği (`secim_surumu`, `kapi_tarihi`, `kurallar_sha256`, `secim_sha256`); aynı sürüm + kapı tarihi üzerine yazılmaz (kod + iş akışı)
- [x] Çıktı klasörü `secim/<tarih>-<sürüm>/`; bayraklar ayrı iş (`--bayrak` → `bayrak.json`), seçimi beklemez
- [x] RAPOR: "geçmiş getiri sıralaması (adım 1–3 süzgeçli)" açıklaması + oda ↔ kontrol dilim tablosu
- [ ] B (geçiş kaydı), C (analiz kodu), D (haftalık geri bildirim): ayrı PR'lar
