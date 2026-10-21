# Liderlik devri notu (Claude Sonnet 5.5 → Claude Opus 5.5 / sselimgenc)

## Hedef
Kullanıcının algo trading projesi için paper trading'e girecek stratejileri seçmek. Piyasalar: BIST30, ABD, kripto, emtia. Day trade + swing. Temel mod long-only; short ve x2/x3 kaldıraç ayrı varyant ve ayrı kapı.

## Depoda ne var
- 5 backtest PDF'i + liste PDF/MD/XLSX (kök dizin). `docs/KATALOG.csv`: ~35 strateji satırı, kanıt seviyeleri A/B/C. Rakamlar **PDF'lerden aktarıldı, hiçbiri yeniden üretilmedi.**
- `docs/ELEME_KRITERLERI.md` **v0.2 taslak**: Sonnet önerisi + Codex'in 15 maddelik görüşü (Issue #1) birleşik. **Senin denetimini bekliyor.**
- `docs/GOREV_T1.md`: Codex'e ilk görev (Codex Algo 21 portföyünü bağımsız yeniden üret). Kriterler onaylanmadan başlatılmadı.
- `tartisma/001_paper_kriterleri.md`: tartışmanın Git kopyası. Issue #1: https://github.com/sselimgenc-oss/sg-arge/issues/1

## Gözlemler (doğrulanmadı, denetle)
- En sağlam kaynak Codex Algo (OOS + 2x/3x maliyet + gecikme testi; long-only, kaldıraçsız; MDD %3-8, getiriler mütevazı).
- Twin OTT, Davey Donchian, R1, R5, R7, VOLTRAN-1A/1B: PF 3,6-5,4 ve %200-950 getiri → aşırı uyum şüphesi; Voltran hedefe ulaşana dek v1→v3 iterasyonla geliştirilmiş. 256 stratejiden en iyi 8'i seçilmiş (seçim yanlılığı).
- PDF'lerdeki "WR >= %40" kriteri anlamsız.
- Day trade adayları saatlik veri olmadan doğrulanamaz.

## Senden beklenenler (lider)
1. `docs/ELEME_KRITERLERI.md` v0.2 için en fazla 15 maddelik denetim: keyfi eşikler (t-stat, OOS PF 1,1, 2x'te PF 1,2, %25 replikasyon toleransı), deneme sayısı nasıl sayılacak (DSR), PBO'nun yeri.
2. Kullanıcıdan bekleyen kararlar: portföy MDD üst sınırı (öneri %15), saatlik veri kaynağı (BIST dahil).
3. Kriterler onaylanınca T1'i `state.json` üzerinden Codex'e ata (`turn: codex-worker`).

## Altyapı notları
- Köprü: `@claude` moderatör (Sonnet 5.5), `@auditor` sen (Opus 5.5), `@codex` worker. Secret'lar: `CLAUDE_OAUTH_MODERATOR`, `CLAUDE_OAUTH_AUDITOR` (kullanıcı ekleyecek; eklenene kadar Actions cevap vermez).
- Codex, Issues'a cevap yazabiliyor; Git dosyası kanalı da açık (`tartisma/`).
- Dallar `main`'e PR ile alınır; `issue_comment` workflow'ları yalnız `main`'de çalışır.
