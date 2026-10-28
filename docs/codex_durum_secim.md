# Durum: Seçim v1 (dal `claude/secim-v1`)

- [x] `copytrade/secim.py` (havuz, puan, aday, oda, kontrol, taban, elle, RAPOR, `--izleme-listesi`)
- [x] `kurallar.yaml`: `secim_aday_orani`, `secim_oda_min/max`, `secim_min_kapsam` (son biri uygulayıcı güvenliği; lider onayı gerekir)
- [x] Altın örnekler `tests/test_secim.py` (12 satır); Worker testi `worker/test/events.test.js` (`kol = oda` bildirir, diğerleri sessiz)
- [x] `izleme_motoru`: `kol`, `kollar` alanları kabul edilir ve `durum.json`'a taşınır (`docs/VERI_SOZLESMESI.md` v1.5)
- [x] İş akışı `copytrade_secim.yml` (elle; veri dalına `secim/<tarih>/`)
- [ ] **Gerçek RAPOR bekliyor: veri dalındaki son koşu HIZLI koşudur (92 satır, kapsam 0,0067); tam koşu yok.** Seçim yalnız `durum = tamam` ve
      kapsam ≥ 0,5 ile çalışır; tam koşu bitince `CT-Seçim v1` iş akışı elle tetiklenir, RAPOR özeti PR açıklamasına eklenir.

## Kararlar / varsayımlar (belgede yazmıyordu; lider denetlesin)
- Havuz ayrıca `tarz ∈ {intraday, swing}` ister (scalp tarz kovasına girmez).
- Aday sayısı = ceil(0,15 × tarzdaki puanı > 0 sayısı). Eşitlikte adres sırası.
- Oda boyutu = min(20, ilişki elemesinden sonra kalan aday); tarz kotası ilişki elemesinden ÖNCEKİ aday payıyla (en büyük kalan yöntemi);
  bir tarz kotasını dolduramazsa kalan yer öbür tarzdan aynı sırayla (genç olmayan, puan) dolar.
- İlişkili adresler yalnız aday katında karşılaştırılır; `iliskili_adresler` sütunu kapı `sonuc.csv`'sine `kesif` adımıyla yazılır.
- Kontrol sırası `sha256("<tohum>-<adres>")`; kütüphane sürümünden bağımsız ve tekrarlanabilir.
- Bir adres birden çok kolda olabilir: `kol` = oda > elle > taban > kontrol > aday > havuz; tamamı `kollar`'da. Bildirim `kol = oda`.
- Worker: `kol` alanı olmayan trader artık bildirmez (eski liste `kol` almadan çalıştırılırsa sessiz kalır).
- Taban lider tablosunu Hyperliquid'den çeker (`--taban-dosyasi` ile dosya verilebilir); bulut oturumundan erişim yok → Actions.
