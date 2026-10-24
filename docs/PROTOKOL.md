# Çalışma protokolü (güncel: 2026-10-24)

## Roller
- **Lider (Claude Opus, sselimgenc hesabı):** karar ve öncelik, görev yazımı (`docs/GOREV_*.md`), ön kayıt, PR denetimi, sonuç raporları. `DURUM.md`'yi yalnız lider günceller.
- **Codex:** uygulayıcı (kod, veri, gerçek koşular).
- **Sonnet (sg507 hesabı):** uygulayıcı (kod, araştırma). Karar vermez.
- **Argon (Gemini, repo erişimi yok):** araştırmacı ve denetçi; kullanıcı aracılığıyla çalışır. Çıktısını lider denetler.

## Akış
1. Lider görevi `docs/GOREV_*.md`'ye yazar, PR açar; kullanıcı birleştirir.
2. Lider Issue #1'e `[CODEX GÖREVİ]` / `[SONNET GÖREVİ]` başlıklı kısa yorum yazar ve kullanıcıya yapıştırmaya hazır mesaj verir.
3. Ajan main'i çeker, görevi yapar, PR ile teslim eder. Lider denetler: kabul ya da ret.
   **Birleştirme (kullanıcı onayı, 2026-10-24):** lider, denetlediği ve testleri geçen, mevcut plandaki PR'ları kendisi birleştirir. Şunlar kullanıcıya kalır: kilitli dönemi açmak, yeni deneme/strateji eklemek (ön kayıt dışı), paper/para ayarları, repo silme.
4. Ajanlar kendiliğinden tetiklenmez; görevi kullanıcı iletir.

## Kurallar
- Her ajanda aynı anda tek iş.
- Uydurma yok: her sayı koddan ya da kaynaktan gelir; bulunamayan "bulunamadı" yazılır.
- Test kuralları: `docs/EVRENSEL_KURALLAR.md`, eleme: `docs/ELEME_KRITERLERI.md`. Ön kayıt sonucu görmeden yapılır; kilitli dönem yalnız lider kararıyla açılır.
- Commit etiketleri: `[Opus-Lead]`, `[Codex]`, `[Claude-Mod]` (Sonnet), `[Argon]`.
