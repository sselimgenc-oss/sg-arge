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

## Liste biterse: ortak ek iş havuzu (boş durmak yok)
Kullanıcı: "lider limiti yenilenene kadar ne kadar çok iş varsa yapsın". Kendi listesi biten oturum bu havuzdan **ilk boş maddeyi** alır. Aldığını hemen durum dosyasına `ALDIM: E<n>` diye yazıp push eder; başka oturum aynı maddeyi almaz.
- **E1:** Ertelenen 5.5. Yavaş 7 betik için profil + davranış değiştirmeyen hızlandırma + test.
- **E2:** Ertelenen 6.5. Eksik kütüphane `import`'ları, csv'ye ekle, ilgili stratejileri yeniden koş.
- **E3:** `veri_yok` kripto stratejileri (31) için ikinci kaynak dene (Bybit/OKX klines, CoinGecko). Bulunanları yeniden koş.
- **E4:** `desteklenmiyor` (12) ve `hata` çıkan stratejilerin hata metinlerini grupla (`docs/denetim/desteklenmiyor_gruplari.md`). En sık 3 eksik Pine özelliğini, TradingView belgesine dayanarak test + kodla ekle.
- **E5:** `islem_yok` (11) stratejileri. Gerçekten sinyal yok mu, yoksa yorumlayıcı hatası mı? Kaynağı oku, her biri için 1 satır sonuç.
- **E6:** Test paketi süresini ölç; 10 saniyeden uzun testleri hızlandır (davranış aynı).
- **E7:** `docs/SANAL_HAVUZ.md` taslağını TV-2'nin son sayılarıyla güncelle (yalnız öneri).
- **E8:** Ertelenen 5.2 renko. TradingView belgesinde yalnız açıkça yazan kısmı (kutu boyu, kapanış tabanlı) uygula; belirsizi listele.

**Lider notu 23:45 TR (A için):** Kripto dışı koşu 40226355510 8/8 başarılı bitti ama dala yalnız parça 7 commit'i düştü (a7482e3). Diğer parçalarda commit adımında push reddedildi, kurtarma "nothing to commit" dedi; satırlar commit edilmedi (log: job 121268458337). Yapılacak: (1) artifact kurtarma betiğiyle 0–6 parçalarını dala al, (2) tv2.yml commit adımını düzelt: reddedilen push sonrası `git fetch` + `git reset --soft`/rebase yerine yeni HEAD üstüne satırları yeniden kopyalayıp commit et, (3) `--birlestir` + `tv2_sirala`. Parça başına satır sayısı az görünüyor (parça 1: 2 satır); kuyruğun kaçının koşulduğunu say, atlananları sebebiyle raporla.
