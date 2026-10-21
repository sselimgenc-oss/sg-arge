# Calisma protokolu (beniokuortak.md'nin uygulamasi)

- Gorev kuyrugu: `state.json.queue` + GitHub Issue (etiketler: `owner:codex`, `owner:claude`, `needs-audit`).
- Sira: `state.json.turn` alanı. Sahip degilsen yazma; 15 dk'da bir kontrol et, `@codex-worker` / `@claude-moderator` ile durt.
- Commit etiketleri: `[Claude-Mod]`, `[Codex-Sol]`, `[Opus-Audit]`.
- Faz: 1 dogrulama (A seviyesi) -> 2 B seviyesi stratejilerin kodlanip dogrulanmasi -> 3 short/kaldirac varyantlari -> 4 Opus denetimi -> 5 paper listesi.
- Hicbir sonuc "dogrulandi" sayilmaz: results/ altinda yeniden uretilmediyse.
