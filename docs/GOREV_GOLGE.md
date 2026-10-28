# Görev: Gölge motoru + geçmiş prova (Faz 2–3, 2026-10-28, lider; kullanıcı onaylı)

Yapan: **Codex** (2026-10-28, lider; Sonnet seçimde). Dal: `codex/golge`. Başlama koşulu: `defter.py` `main`'de (var). Arşiv (`copytrade/arsiv.py`) dolum/mum verisini sağlar; geçmiş prova API'den çeker. Önce `DURUM.md`,
`docs/GOREV_D_YOLU.md`, `docs/ONKAYIT_D.md`. Ağ: Hyperliquid'e oturumdan erişim yok → koşular Actions'ta.

## Faz 2 — Gölge motoru (`copytrade/golge.py`)
- `defter.copy_ledger` üstüne kurulur; plasebo, kapı ve gölge aynı defterden geçer (ikinci motor yazılmaz).
- `GOREV_D_YOLU.md` "Gölge defter kuralları" 1–10 ve "Kopya kuralı varyantları" V0–V2; her kural için altın örnek testi.
- **Sağlama:** gecikme 0 + maliyet 0 → trader'ın gerçekleşmiş PnL'i orantılı yeniden üretilir (gerçek dolumlu en az 3 adreste).
- 10.000+ dolumlu adreste zaman penceresiyle sayfalama.
- Kat/kol mantığı `copytrade/kollar.py`: ön kayıttaki terfi, çıkış, kontrol seçimi (tohum kayda geçer), olaylar `olay` arşiv türüne.
- V2 sayıları ve gölge pozisyon üst sınırı (3x) `docs/ONKAYIT_D.md`'de (kullanıcı onayı 2026-10-28, dondu); yalnız `kurallar.yaml`'a yazılır. Altın örnek: 8. günde −%31 → çık; 6. günde −%49 → kal; 3x'i aşan ekleme kırpılır.

## Faz 3 — Yürüyen pencereli geçmiş prova
- **İlk iş: sentetik trader doğrulaması** (lider kararı 2026-10-28, Faz 2'den taşındı): rastgele yürüyüş fiyatlı sıfır etkili
  sentetik trader'lar gölge motoru + kohort–kontrol ölçümünden geçer → ≥200 tohumda yanlış pozitif ~%5; etkisi enjekte edilmiş
  trader'lar yakalanır. Bu geçmeden gerçek veriyle prova raporlanmaz.
- T anına kadarki veriyle etiketle (katlar + kollar), sonraki 60 günü gölge motoruyla ölç, pencereyi 2 haftada bir kaydır.
- Kollar: kohort, kontrol, taban, elle liste; varyantlar V0–V2; ek kol: çok alanlı puan.
- Çıktı: pencere başına kol farkı + bootstrap aralığı; güç hesabı (gerçek varyansla); durdurma kriteri 1'in sonucu.
- **Evren (hayatta kalan yanlılığı):** T günü evreni mümkünse geçmiş kaynaktan (`arastirma/copytrade/argon_gecmis_leaderboard.md`):
  Dune `hyperliquid.perp_accounts_daily` (API anahtarı GitHub Secrets'ta `DUNE_API_KEY`, kullanıcı kurar). Yoksa bugünkü leaderboard;
  o zaman sonuç "iyimser üst sınır" diye raporlanır. Hangi kaynağın kullanıldığı RAPOR'da yazılır.

## Kabul
- Altın örnekler + sağlama + sentetik testler; tam test paketi.
- Faz 3 raporu: pencere sayısı, kol başına adres, her sütunun min/medyan/max; durdurma kriteri sonucu açıkça.
- Durum: `docs/codex_durum_golge.md`.
