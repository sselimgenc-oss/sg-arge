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
1. **Kripto dışı koşu 40316028018** bitince: `codex/kripto-disi`'deki yeni satırları `codex/tv2-son`'a birleştir; 636 kimliğin kaçının satırı var say. Eksik varsa yalnız eksikler için yeni kuyruk → `KOSU_ISTEGI`.
2. `python -m backtests.tv2 --birlestir` + `python -m backtests.tv2_sirala`; kripto dışı geçenleri `docs/denetim/tv2_supheli.md` ölçütleriyle tara (aşırı getiri, < 30 işlem, `lookahead_on`, `veri_kisa`).
3. **NVDAXUSDT veri kaynağı:** Binance USD-M'de bu sembol yok (Argon raporu; Binance'te NVDAUSDT). Satırın verisi nereden geldi? Yanlışsa satırı `veri_yok` neden "sembol eşlemesi yanlış" olarak düzelt; doğru eşleme NVDAUSDT ise yeniden koş. Aynı denetimi diğer TradFi perp eşlemeleri için yap.
4. `zaman_asimi` 13 kimlik: `uzun=true` tekil koşu, aynı anda 1 (`KOSU_ISTEGI`).
5. `lookahead_baglami.md`'deki 3 riskli kaynak: geçti/izle kararı varsa satıra `lookahead_riskli=true` bilgi sütunu (kapı değişmez) ve kaynak satır numarası.
6. **`izle` → karar (kullanıcı kararı 2026-10-26):** "sürüm sonrası 1 yıldan az veri" ve "< 10 işlem haftası" nedeniyle `izle` kalan satırlara **eldeki sınama penceresiyle** aynı tek kapı uygulanır: uygulanabilir sınama net > 0 → `gecti`, değilse `kaldi`; sınamada hiç işlem yoksa `islem_yok`. Satıra `kisa_sinama=true` bilgi sütunu ve sınama hafta sayısı yazılır; yeniden koşu gerekmez (satırdaki değerler yeterli). `tv2_sirala` bu satırları da sıralar. Kapı eşiği değişmez. Lider ön sayımı: 373 izle → ~66 gecti, ~307 kaldi/islem_yok.
7. PR: `[TV-2] kripto dışı sonuçlar + eşleme düzeltmeleri + izle kararı`.
8. **`veri_yok` 401 — tek ikinci kaynak denemesi (Faz 1 kapanış ölçütü 1), ayrı PR `[TV-2] veri_yok ikinci kaynak`:**
   - **A. Dukascopy önbelleği (214; XAUUSD, EURUSD ve diğer FX, endeks CFD):** yükleyici ve eşleme var (`data/dukascopy.py`, `backtests/tv2.py`), arşiv boş. Bu satırların sembol listesini çıkar; `tv2.yml`'e (ya da ayrı iş akışına) Dukascopy dakikalık indirme adımı ekle, arşiv **Actions cache**'te tutulur, repoya veri yazılmaz (repo herkese açık). Sonra yalnız bu kimliklerle kuyruk → `KOSU_ISTEGI`.
   - **B. Gün içi / yerel piyasa (151):** VN30/HNX/HOSE → vnstock. NSE (NIFTY, BANKNIFTY, SENSEX), CME/COMEX mikro, BIST gün içi: ücretsiz çok yıllı gün içi kaynak yok (Argon raporu `arastirma/veri/`); Dukascopy'de karşılığı olan endeksler (ör. US30, NAS100, SPX500) A'ya taşınır, kalanlar `veri_yok` nedeni "ücretsiz gün içi kaynak yok" ile **kapanır**.
   - **C. Binance (30):** listeden kalkmış semboller için `data.binance.vision` aylık arşivi (spot + UM) denenir.
   - **D. yfinance/eşleme (6):** elle eşleme bir kez; olmazsa kapanır.
   - Kapı, maliyet, karar kodu değişmez. Ücretli veri yok.

## Oturum 2: U7 kapanış + havuz (dal `codex/u7-son`, `main`'den; durum `docs/codex_durum_2.md`)
1. **U1 5m:** 14 varyantın 6'sı bitti. `huni.yml` `u1_5m=true` + `--resume` ile kalan 8 (`KOSU_ISTEGI`); bitince `u7_ozet` yenile.
2. Faz 1 2b'deki 10 `Koşullu` satırın şerh nedenlerini tek tabloda topla (`results/u7/kosullu.md`); karar değiştirme.
3. `results/u7/siralama.csv`'yi `main`'deki U7 sonuçlarıyla yeniden üret (TV-2 ile aynı yöntem; `dsr`/`n_eff` bilgi).
4. Oturum 1'in 2. maddesi bitince: `docs/SANAL_HAVUZ.md` → **geçen tüm küme temsilcileri** (TV-2 kripto + kripto dışı + U7) listesi ve hepsinin paper'da tek işte koşma planı (Actions süresi tahmini). 20 seçim/kura **yok** (kullanıcı kararı 2026-10-26). **Yalnız plan**; `paper/` yok.
5. PR: `[U7] kapanış + sanal havuz önerisi`.

## Bekleyen (sırası gelmedi, kullanıcı/Argon girdisi bekliyor)
- Renko (E8): Argon raporu geldi (`arastirma/renko/`). TradingView ATR kutu boyunu **son barın ATR'siyle bütün geçmişe** uygular ve Renko geri testleri sentetik açılış fiyatından dolum yüzünden sistematik olarak sahte kâr üretir (TradingView belgesi). Öneri: Renko stratejileri yorumlanmaz, `desteklenmiyor` nedeni "renko geri testi güvenilmez" ile kapanır **Kullanıcı onayladı (2026-10-26).** Oturum 1, sırası gelince Renko kullanan stratejileri bu nedenle kapatsın.
- Faz 2 Telegram/Cloudflare: kullanıcı hesap kararı + Argon rehberi.
- Faz 3 risk kuralları: kullanıcı onayı.
