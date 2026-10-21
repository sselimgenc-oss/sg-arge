# Calisma protokolu (beniokuortak.md'nin uygulamasi)

- Gorev kuyrugu: `state.json.queue` + GitHub Issue (etiketler: `owner:codex`, `owner:claude`, `needs-audit`).
- Sira: `state.json.turn` alanı. Sahip degilsen yazma; 15 dk'da bir kontrol et, `@codex` / `@claude` (gercek tetikleyiciler; "-worker" gibi adlar GitHub hesabi olmadigi icin tetiklemez) ile durt.
- Commit etiketleri: `[Claude-Mod]`, `[Codex-Sol]`, `[Opus-Audit]`.
- Faz: 1 dogrulama (A seviyesi) -> 2 B seviyesi stratejilerin kodlanip dogrulanmasi -> 3 short/kaldirac varyantlari -> 4 Opus denetimi -> 5 paper listesi.
- Hicbir sonuc "dogrulandi" sayilmaz: results/ altinda yeniden uretilmediyse.

## Etiketler
- `@claude` moderator (Sonnet 5.5), `@auditor` denetci (Opus 5.5), `@codex` worker.
- Ayni anda yalniz `state.json.turn` sahibi dosya yazar; digerleri yalniz yorum yazar.

## Liderlik devri (2026-10-21)
- Takım lideri ve danışman: `@auditor` (sselimgenc hesabı, Opus 5.5). Önceliği, kriter onayını ve görev atamasını o yapar.
- sg507 hesabındaki Opus 5.5 rolü **pasif**; `@claude` (Sonnet 5.5) yalnız lider talimatıyla uygulama/koordinasyon yapar.
- Devir notu: `docs/DEVIR.md`.
