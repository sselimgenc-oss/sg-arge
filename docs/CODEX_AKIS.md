# Codex paralel akışlar (2026-10-25 21:30 TR → 2026-10-26 14:15 TR)

Kullanıcı kararı: hız için işler 3 paralel Codex oturumuna bölündü. Madde ayrıntıları `docs/CODEX_SIRA.md`'de. Kurallar aynı (yöntem, eşik ve karar kodu değişmez; `main`/`paper/` yok; testsiz kod yok).

**Çakışmayı önleme:**
- Her oturum yalnız **kendi dalında** ve **kendi dosyalarında** çalışır.
- Durumunu yalnız **kendi durum dosyasına** yazar. `CODEX_SIRA.md`'yi işaretlemez; lider birleştirir.
- Bir madde **45 dakikadan uzun** sürerse durum dosyasına `TAKILDI: sebep` yazar ve sıradakine geçer.
- Her madde bitince commit + `git pull --rebase` + push yapar, sormadan devam eder.
- Actions: aynı anda en fazla 1 matris koşusu. Koşu A'nındır; B yalnız 2.2 tekil uzun koşuları başlatır.

## A: Kripto dışı veri ve koşu (en önemli)
- **Dal:** `codex/kripto-disi`, `codex/tv2-kosu`'dan açılır. `codex/tv2-veri-esleme`'deki Dukascopy/vnstock yükleyici başlangıcını önce oraya birleştir.
- **Durum dosyası:** `docs/codex_durum_A.md`
- **Maddeler:** 4.1 → 4.2 → 4.3 → 4.4 → 4.5.
  - 4.5'te kripto dışı kuyruk `tv2.yml` matrisiyle koşulur. Önce son sürümü 2026'dan önce olanlar.
- **Dokunulacak dosyalar:** `backtests/tv2.py::veri()` ve veri yükleyicileri, `tests/test_tv2_kosucu.py`, `arastirma/tv2_veri_eslesme.csv`, `results/tv2/kuyruk_kripto_disi.txt`, kripto dışı `results/tv2/satirlar|getiriler`.

## B: TV-2 kripto kapanışı + U7 (mevcut oturum)
- **Dallar:** `codex/tv2-kosu` (TV-2), `codex/u7-tum-stratejiler` (#200).
- **Durum dosyası:** `docs/codex_durum_B.md`
- **Maddeler:** önce 5.4'ü bitir. Sonra 2.2 → 2.3 → 2.4 → 3.1 → 3.2 → 3.3 → 3.4 → 3.5.
- **Dokunulacak dosyalar:** kripto `results/tv2/*`, `docs/denetim/tv2_supheli.md`, `results/u7/*`, `backtests/u7_*`, #200 açıklaması.

## C: Analiz ve denetim (yeni oturum)
- **Dal:** `codex/analiz`, `claude/magical-ride-c7apbp`'den açılır.
- **Durum dosyası:** `docs/codex_durum_C.md`
- **Maddeler:** 6.3 (S1 denetimi) → 6.7 (ML; (c) maddesindeki `dsr`/`n_eff` yalnız bilgi sütunu, (d) `lookahead_on` listesi) → 6.1 (U7 sıralaması) → 6.6 (copy trade doğrulaması) → 6.4 (Faz 3 eleştirisi).
- **Dokunulacak dosyalar:** `docs/denetim/S1_codex.md`, `backtests/tv2_sirala.py` (yalnız yeni bilgi sütunları), `results/u7/siralama.csv`, `results/tv2/lookahead_listesi.csv`, `docs/FAZ2_NOTLAR.md` ve `docs/FAZ3_YURUTME.md` sonları.
- Sonuç dosyalarını okumak için `codex/tv2-kosu` ve `codex/u7-tum-stratejiler`'i salt okunur birleştirebilir (`git merge --no-commit` gerekmez, `git show` ile oku).

## Ertelenen (sonra)
5.2 renko (takıldı), 5.5 yavaş betikler, 5.6 PR (B 5.4'ü bitirince lider değerlendirir), 6.5 kütüphaneler.
