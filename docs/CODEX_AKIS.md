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
1. **U1 5m:** 14 varyantın 6'sı bitti. `huni.yml` `u1_5m=true` + `--resume` ile kalan 8 (`KOSU_ISTEGI`); bitince `u7_ozet` yenile.
2. Faz 1 2b'deki 10 `Koşullu` satırın şerh nedenlerini tek tabloda topla (`results/u7/kosullu.md`); karar değiştirme.
3. `results/u7/siralama.csv`'yi `main`'deki U7 sonuçlarıyla yeniden üret (TV-2 ile aynı yöntem; `dsr`/`n_eff` bilgi).
4. Oturum 1'in 2. maddesi bitince: `docs/SANAL_HAVUZ.md` → **geçen tüm küme temsilcileri** (TV-2 kripto + kripto dışı + U7) listesi ve hepsinin paper'da tek işte koşma planı (Actions süresi tahmini). 20 seçim/kura **yok** (kullanıcı kararı 2026-10-26). **Yalnız plan**; `paper/` yok.
5. PR: `[U7] kapanış + sanal havuz önerisi`.

## Bekleyen (sırası gelmedi, kullanıcı/Argon girdisi bekliyor)
- Renko (E8): Argon raporu geldi (`arastirma/renko/`). TradingView ATR kutu boyunu **son barın ATR'siyle bütün geçmişe** uygular ve Renko geri testleri sentetik açılış fiyatından dolum yüzünden sistematik olarak sahte kâr üretir (TradingView belgesi). Öneri: Renko stratejileri yorumlanmaz, `desteklenmiyor` nedeni "renko geri testi güvenilmez" ile kapanır **Kullanıcı onayladı (2026-10-26).** Oturum 1, sırası gelince Renko kullanan stratejileri bu nedenle kapatsın.
- Faz 2 Telegram/Cloudflare: kullanıcı hesap kararı + Argon rehberi.
- Faz 3 risk kuralları: kullanıcı onayı.
