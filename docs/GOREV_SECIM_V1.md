# Görev: Seçim v1 — havuz, aday, oda, kontrol + canlı izlemenin başlaması (2026-10-28, lider; kullanıcı onaylı)

Yapan: lider atar. Dal: `<işçi>/secim-v1`. Tek PR, `main`'e; lider birleştirir. Önce `DURUM.md`, `docs/GOREV_D_YOLU.md`,
`docs/ONKAYIT_D.md` (sürüm 1.1). Ağ: Hyperliquid'e bulut oturumundan erişim yok → koşular GitHub Actions'ta.
**Tek odak:** trader seçimini oturtmak (kullanıcı kararı 2026-10-28). Girdi: düzeltilmiş kapının **tam koşusu** (`copytrade-kapi`
veri dalı, en son tarihli `sonuc.csv`, `durum.json` `durum = tamam` olmalı; değilse dur).

## 1. Seçim (`copytrade/secim.py`)
Her satır kapı sonucundan; hiçbir eşik koda gömülmez, yeni sayılar `kurallar.yaml`'a.
- **Havuz:** adım 1 ve adım 2 `Geçti` (veri yeterliliği, tarz intraday/swing, kaldıraç, aktiflik, hesap değeri tabanı).
- **Puan:** tarzın gecikmesindeki maliyet sonrası net kopya getirisi (`gecikme_<kapi_gecikme_dk>dk_net`). Puanı boş satır puansızdır,
  havuzda kalır, adaya giremez.
- **Aday:** her tarz kendi içinde sıralanır; puanı > 0 olanlardan tarz başına en iyi %15 (`secim_aday_orani: 0.15`, yukarı yuvarla).
- **Oda:** aday katından en çok 20, en az 10 (`secim_oda_min: 10`, `secim_oda_max: 20`); tarzlar aday katındaki paylarıyla orantılı.
  Sıralama: önce `genc_aday` olmayanlar (≥ 365 gün), sonra puan. **İlişkili hesap:** `iliskili_adresler` ile bağlı iki adres odaya
  birlikte girmez; puanı yüksek olan kalır, diğeri `not`'a yazılır. Aday sayısı 10'dan azsa oda = tüm aday ve RAPOR'da açıkça yazılır.
- **Kontrol:** havuzdan puana bakmadan rastgele, oda ile aynı sayıda. Tohum = `secim-v1-<tarih>` dizgesinin SHA-256'sının ilk 8 baytı;
  tohum ve seçilenler kayda geçer. Oda üyeleri kontrolde de çıkabilir (çıkarılmaz).
- **Taban:** leaderboard'da 30 günlük PnL'e göre ilk N (N = oda sayısı), ön elemesiz.
- **Elle liste:** bugünkü `copytrade/izleme_listesi.yaml`.

## 2. Çıktı (`copytrade-kapi` veri dalı, `main`'e değil)
- `secim/<tarih>/secim.json`: her adres için `kol` (oda | aday | havuz | kontrol | taban | elle), `tarz`, puan, sıra, `genc_aday`,
  medyan/en yüksek kaldıraç, geçmiş gün, hesap değeri, ilişkili not, kapı satırının hesap sürümü.
- `secim/<tarih>/RAPOR.md`: kat sayıları (tarz kırılımlı), oda tablosu (adres, takma ad = ilk 4 hane, tarz, puan, kaldıraç, geçmiş,
  neden seçildi), kontrol listesi + tohum, sütun özeti (min/medyan/max).

## 3. Canlı izlemenin başlaması
- `copytrade/izleme_listesi.yaml`: yeni alan `kol`; oda + kontrol + taban + elle liste girer, `t0` = birleştirme günü. Liste
  `secim.json`'dan üretilir (`python -m copytrade.secim --izleme-listesi`); **elle yazılmaz.** Oda listesi **kullanıcı onayından sonra**
  birleştirilir (lider tabloyu kullanıcıya sunar).
- İzleme motoru: `kol` alanı `durum.json`'a taşınır (veri sözleşmesi sürüm notu). Sanal kopya tarz gecikmesiyle, bugünkü gibi.
- Telegram Worker: **bildirim yalnız `kol = oda`** için; diğer kollar sessiz izlenir.
- Kapasite: izleme saatlik; adres sayısı ve harcanan istek ağırlığı (≤ 1.200/dk) durum dosyasına.

## Kabul
- Altın örnekler: 12 satırlık elle hesaplanmış kapı tablosu → beklenen havuz/aday/oda/kontrol (tarz payı, yuvarlama, `genc_aday`
  önceliği, ilişkili hesap, puansız satır, aday < 10 durumu); aynı tarihle aynı kontrol, farklı tarihle farklı kontrol.
- Worker testi: `kol = oda` bildirim gider, `kontrol` gitmez.
- Tam test paketi; gerçek tam koşu sonucuyla üretilmiş RAPOR özeti PR açıklamasında.
- Durum: `docs/codex_durum_secim.md`.
