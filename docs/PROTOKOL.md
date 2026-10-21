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

## Lider kurallari (v0.3, 2026-10-21)
- Paralel calisma serbest: her gorev sahibi yalniz kendi gorev dosyalarina (GOREV_Tx.md'deki kapsam) ve `state.json`'da kendi kaydinin `status` alanina yazar. `turn`, kuyruk ekleme/cikarma, kriter degisikligi yalniz lider.
- Her teslim PR ile gelir; lider (`@auditor`) inceler ve kabul/ret yazar. Lider onayi olmadan sonraki asama (or. T1b) baslamaz.
- Itirazlar `tartisma/NNN_*.md` dosyalari uzerinden; kriter dosyasi dogrudan degistirilmez.

## Argon (Gemini) - GitHub'a bagli degil
- Lider `argon/PAKET_<gorev>.md` paketini hazirlar (kendi icinde tam: talimat + sema + liste). Kullanici Argon'a yapistirir.
- Kullanici Argon'un ciktisini `argon/<gorev>.yaml` olarak web arayuzunden yukler, commit `[Argon] ...`.
- Lider inceler; kabul edilen kartlari `docs/spec/<id>.yaml`'a boler. Argon dogrudan `docs/` ya da `state.json`'a yazmaz.

## Tetikleme durumu (2026-10-21)
- `@codex`: Codex Cloud environment kurulu, Issue yorumuyla otomatik tetiklenir.
- `@claude` (Sonnet): secret yok, **kullanici manuel tetikler**. Lider gorevi `docs/GOREV_*.md` + Issue yorumuna yazar; kullanici Sonnet oturumuna iletir. Issue'da `@claude` etiketi kullanilmaz (Actions bos yere hata verir).
- Argon: kullanici araciligiyla (`argon/PAKET_*.md`).

## B plani (2026-10-21): web okuma tamamen Argon'da
- Sonnet'in bulut ortami (Full ag izni verilmesine ragmen) kaynak sitelerine proxy 403 aliyor. Tum web kaynakli kart cikarma isi Argon'a gecti: xlsx partileri 4, 6, 7, 8, 9 ve `docs/spec/YENIDEN.csv`.
- Sonnet: kod ve denetim (T5a yorumlayici cekirdegi, kart tutarlilik denetimi). Kaynak okuma gerektiren is verilmez.
- Codex: `@codex` otomatik tetikleme calismiyor; kullanici "gorev geldi" der, Codex Issue #1'deki son `@codex` yorumunu okur.
