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

**Lider notu 00:15 TR (B için):** U7 huni koşusu 40224968370 bitti; 10 işten yalnız `reddit_u7` başarısız: `git add results/u7/reddit/getiriler` → "pathspec did not match" (Reddit 2b aday çıkmadığı için klasör hiç oluşmamış). Düzeltme: commit adımında klasör yoksa atla (`[ -d ... ] && git add ...` veya `.gitkeep`). Diğer 9 işin sonuçlarını 3.3 için kullan; reddit işi yalnız düzeltmeden sonra tek başına yeniden koşulsun.

---

## GECE PLANI (2026-10-26 01:40 → 13:30 TR) — lider yok, sormadan devam

Lider (Claude) limiti bitiyor; 14:15'teki denetime kadar gözetim yok. Her oturum aşağıdaki **kendi listesini sırayla** yürütür, bitince ortak havuza (E1–E8 ve G1–G6) geçer. Kurallar yukarıdakilerle aynı, ek olarak:
- **Yasak:** `main`'e birleştirme, PR birleştirme, `paper/` ve para/hesap işleri, kapı/eşik/karar kodu değişikliği, sır/anahtar commit'i (repo **public**), test atlatma/silme.
- **Her 45 dk'da en az bir commit** + push; durum dosyasına `HH:MM — madde — ne yapıldı / sıradaki` satırı.
- Takılırsan `TAKILDI: sebep` yaz, **bekleme**, sıradakine geç. Karar gerektiren her şeyi `docs/denetim/kullanici_kararlari.md`'ye (C toplar) bir satır olarak yaz, kendin karar verme.
- Actions: aynı anda en fazla **2** koşu. Koşuları **B başlatır** (gh yetkisi B'de); A ihtiyacını `docs/codex_durum_A.md`'ye `KOSU_ISTEGI: dal, kuyruk, parca` diye yazar, B her 30 dk'da bu dosyaya bakıp başlatır ve run id'yi yanına yazar.
- **13:30 TR'de dur:** durum dosyasının sonuna `## Gece özeti` (biten, yarım, takılan, sayılar, açık riskler) yaz, son push.

### A — kripto dışı (dal `codex/kripto-disi`)
1. Lider notu 23:45'i uygula: 0–6 parçalarını artifact'tan kurtar (run 40226355510), `tv2.yml` commit adımı hatasını düzelt + test/kuru deneme.
2. Kuyruk kapsamı: 636'nın kaçı koştu, kaçı atlandı (sebep kırılımı) → `docs/denetim/kripto_disi_kapsam.md`.
3. Koşmayanlar için yeni kuyruk dosyası → `KOSU_ISTEGI`. Bitince yine kurtar/birleştir.
4. `--birlestir` + `tv2_sirala`; kripto dışı ilk 30'u `docs/denetim/tv2_supheli.md` ölçütleriyle tara (aşırı getiri, az işlem, lookahead).
5. 9 dış sembollü (`desteklenmiyor`) stratejiyi eşle (Dukascopy/yfinance), yeniden koşulacak listeye ekle.
6. yfinance gün içi sınırları (60 gün <1s) yüzünden kısa veriyle koşanları `veri_kisa` diye işaretle (yalnız bilgi sütunu, kapıya dokunma).
7. Bitti → G1, sonra E3/E4/E8.

### B — TV-2/U7 kapanış + Actions (dallar `codex/tv2-kosu`, `codex/u7-tum-stratejiler`)
1. Lider notu 00:15: huni `reddit_u7` commit adımını düzelt, yalnız reddit işini yeniden koş.
2. Uzun koşu 40213846730 bitti: sonuçları al, 2.3'ü yeniden üret, `tv2_sirala` güncelle.
3. 3.3'ü huni 40224968370 sonuçlarıyla bitir; 3.4 → 3.5 (#200 açıklamasını güncel sayılarla yaz, **birleştirme yok**).
4. A'nın `KOSU_ISTEGI`lerini her 30 dk'da işle (en fazla 2 eşzamanlı koşu).
5. `zaman_asimi` (13) stratejiler için tekil uzun koşu (`uzun=true`) — sırayla, aynı anda 1.
6. Bitti → E1, E5, G2.

### C — analiz + denetim hazırlığı (dal `codex/analiz`)
1. E6 → E2 (yarımsa bitir).
2. 6.6 copy trade doğrulama tablosu: her iddia için kaynak linki + doğrulandı/doğrulanamadı.
3. `results/tv2/lookahead_listesi.csv`'yi tüm dallardaki (kripto + kripto dışı + U7) sonuçlarla güncelle.
4. 6.4 Faz 3 eleştirisini bitir.
5. **G3 Denetim paketi** `docs/denetim/hazirlik_2026-10-26.md` — 14:15 denetimini ucuzlatmak için en önemli iş: dal başına commit listesi (son 24 s), açık PR'lar + CI durumu, birleştirilmeye hazır olanlar ve gerekçe, şüpheli sonuçlar tablosu, test sayısı/süresi, `kullanici_kararlari.md` özeti. 13:00'te son kez güncelle.
6. Bitti → E7, G4.

### Ortak ek havuz (E1–E8'e ek; `ALDIM: G<n>` ile al)
- **G1:** Sanal havuz (`docs/SANAL_HAVUZ.md`) için 20 gölge kitabın her biri için hangi stratejilerin gireceği önerisi (yalnız öneri, karar kullanıcıda).
- **G2:** Tüm `geçti` stratejiler için blok bootstrap p10 ve `dsr` bilgi sütunlarını tek tabloda topla (`results/tv2/gecenler_ozet.csv`).
- **G3:** (C'nin 5. maddesi.)
- **G4:** Yinelenen strateji (dedup) kontrolü: aynı kaynak/parametre farklı kimlik → `docs/denetim/dedup.md`.
- **G5:** Kırık/eksik testleri tara; kapsamı düşük modüller için test ekle (davranış değişmez).
- **G6:** `DURUM.md` için önerilen güncel metni `docs/denetim/durum_onerisi.md`'ye yaz (lider denetimde uygular).
