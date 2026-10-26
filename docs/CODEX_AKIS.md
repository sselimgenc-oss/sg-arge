# Codex iş akışı (2026-10-26 denetiminden sonra)

25–26 Ekim işlerinin hepsi `main`'e birleşti (#200, #214). Eski dallar (`codex/tv2-kosu`, `codex/u7-tum-stratejiler`, `codex/analiz`) **kapandı, kullanılmaz**. `codex/kripto-disi` yalnız sürmekte olan koşunun sonuçları için açık; koşu bitince birleştirilir. Eski paralel plan ve gece planı git geçmişinde (`fc0a95f`).

**Oturum sayısı: 2** (limit tasarrufu; üçüncü oturum yok). Biri biterse diğerinin listesinden alt maddeyi `ALDIM:` ile alır.

## Kurallar (değişmedi)
- Yöntem, kapı, eşik, karar kodu değişmez (`docs/TEST_YAPISI.md`). Yeni sütun yalnız bilgi.
- `main`'e doğrudan push yok; PR açılır, lider birleştirir. `paper/`, para, hesap, sır yok (repo **public**).
- **Testler zayıflatılmaz** (bar/sembol sayısı küçültmek dahil; 2026-10-26 denetim bulgusu 2).
- Tam test paketi yalnız commit öncesi; arada değişen modülün testi. Büyük dosyalar `head`/`grep` ile.
- 2 denemede olmayan → durum dosyasına `TAKILDI: sebep`, sıradakine geç.
- Her madde: commit + push; durum dosyasına tek satır `HH:MM — madde — sonuç`.
- Actions koşularını başlatma yetkisi olan oturum başlatır; yoksa durum dosyasına `KOSU_ISTEGI: dal, iş akışı, girdiler` yaz, kullanıcı başlatır.

## Oturum 1: TV-2 sonuç (dal `codex/tv2-son`, `main`'den; durum `docs/codex_durum_1.md`)
**Kullanıcı 2026-10-26: yalnız stratejileri netleştiren işler. Başka iş yok.** Sıra:
1. `codex/kripto-disi` satırlarını birleştir (koşu 40316028018 bitti) + **`izle` kararı**: kısa sınama penceresiyle aynı tek kapı (net > 0 → `gecti`, değilse `kaldi`, işlem yoksa `islem_yok`; `kisa_sinama=true` bilgi). Yeniden koşu yok.
2. `python -m backtests.tv2 --birlestir` + `python -m backtests.tv2_sirala` → **PR hemen** (`[TV-2] kripto dışı + izle kararı`).
3. **Dukascopy (veri_yok 214 + Dukascopy karşılığı olan ABD endeks CFD'leri):** indirme adımı (Actions cache, repoya veri yok) + yalnız bu kimliklerle kuyruk → `KOSU_ISTEGI`. Ayrı PR.
4. Geri kalan bütün `veri_yok` (yerel piyasa, Binance'ten kalkmış, eşleme) ve `zaman_asimi` 13: **yeni deneme yok**, mevcut nedenle kapanır.
Kapı, maliyet, karar kodu değişmez.

## Oturum 2: U7 kapanış + havuz (dal `codex/u7-son`, `main`'den; durum `docs/codex_durum_2.md`)
**ACİL (lider, koşu 40324514036 başarısız):**
- (a) `u1_5m` işi yalnız 6 varyantı listeledi, hepsi zaten `checkpoint`; kalan 8 varyant **hiç koşmadı** (adım 1 sn). Neden listede yok? `u1_huni.py --tf 5m` ızgarasını `docs/GOREV_U1.md` ile karşılaştır; 14 değil 6 ise "kalan 8" yanlış sayımdır, durum dosyasına yaz.
- (b) Commit adımı: `git pull --rebase` "unstaged changes" ile 4 kez düştü, döngü sessizce bitti, `faa7e61` itilmedi. `huni.yml`'de pull'dan önce `git stash -u` (ya da `git checkout -- . && git clean -fd` yalnız izlenmeyen veri için) ve döngü sonunda başarısızsa `exit 1`. tv2.yml'deki düzeltmenin aynısı.
- (c) `sonuc_pr`: "GitHub Actions is not permitted to create pull requests". Sonuçlar `huni/40324514036` dalında (SONUC.csv/md). Bu dalı `codex/u7-son`'a birleştir; PR açma adımı başarısızsa işi düşürmesin (`|| echo`), lider PR'ı elle açar.
1. **U1 5m:** 14 varyantın 6'sı bitti. `huni.yml` `u1_5m=true` + `--resume` ile kalan 8 (`KOSU_ISTEGI`); bitince `u7_ozet` yenile.
2. Faz 1 2b'deki 10 `Koşullu` satırın şerh nedenlerini tek tabloda topla (`results/u7/kosullu.md`); karar değiştirme.
3. `results/u7/siralama.csv`'yi `main`'deki U7 sonuçlarıyla yeniden üret (TV-2 ile aynı yöntem; `dsr`/`n_eff` bilgi).
4. **Paper planı DURDU (kullanıcı 2026-10-26).** Yerine: `results/faz1_adaylar.csv` + `.md` — TV-2 `siralama.csv` + U7 `siralama.csv` küme temsilcileri tek tabloda, ortak sütunlar: kaynak, kimlik/ad, piyasa/sembol, tf, sınama hafta, sınama işlem, ölçekli yıllık getiri, p10 alt sınır, PF, MDD, kisa_sinama, şüphe işareti (`docs/denetim/tv2_kripto_disi_supheli.md`), lookahead_riskli. Sıra: ölçekli yıllık getiri. Kararı değiştirme, eleme yapma. Üreten betik `scripts/faz1_adaylar.py` (Dukascopy sonrası yeniden koşulacak). `docs/SANAL_HAVUZ.md`'ye ve `paper/`'a dokunma.
5. PR: `[U7] kapanış + sanal havuz önerisi`.

## Bekleyen (sırası gelmedi, kullanıcı/Argon girdisi bekliyor)
- Renko (E8): Argon raporu geldi (`arastirma/renko/`). TradingView ATR kutu boyunu **son barın ATR'siyle bütün geçmişe** uygular ve Renko geri testleri sentetik açılış fiyatından dolum yüzünden sistematik olarak sahte kâr üretir (TradingView belgesi). Öneri: Renko stratejileri yorumlanmaz, `desteklenmiyor` nedeni "renko geri testi güvenilmez" ile kapanır **Kullanıcı onayladı (2026-10-26).** Oturum 1, sırası gelince Renko kullanan stratejileri bu nedenle kapatsın.
- Faz 2 Telegram/Cloudflare: kullanıcı hesap kararı + Argon rehberi.
- Faz 3 risk kuralları: kullanıcı onayı.
