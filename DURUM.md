# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-25 01:30 UTC, lider (Opus).

## Şu an
**Faz 2: paper trade çalışıyor.** C07 + R01 (ABD günlük) + A6-010 (emtia günlük), eşit ağırlık, 5.000 USD sanal (`paper/portfoy.yaml`). Gerçek para yok.
- Defter 2026-09-01'den geriye dönük (aynı kurallar, gerçek veri); **canlı paper 2026-10-24'ten itibaren.** Karar canlı döneme bakılarak verilir.
- `paper.yml` saat :17'ye zamanlı ama GitHub cron'u atlıyor: pratikte ~3,5-5 saatte bir. **Kullanıcı kararı 2026-10-24: kabul** (denetim A1 kapandı; defter günlük kapanışla çalıştığı için işlemler etkilenmez, yalnız pano gecikir). Defter yalnız kapanmış günlük barla (yarım bar koruması); açık pozisyonlar saatlik fiyatla yalnız panoda değerlenir.
- Pano: `sg-pano` reposu, GitHub Pages (https://sselimgenc-oss.github.io/sg-pano/). Veri `PANEL_TOKEN` ile gönderilir.
- Alarmlar: portföy MDD %10 uyarı, %15 yeni giriş durur; bir satır 30 kapanmış işlemden sonra PF < 1 ise inceleme.
- **Gölge kitap** (ana portföyden ayrı, `docs/GOREV_F2_GOLGE.md` Ek 2): U4-H1 (kripto 4H), T8-07 ve V2B (emtia 1H); her biri 5.000 USD, risk %0,25; 2026-09-01'den geriye dönük, canlı 2026-10-24'ten. Karar yalnız canlı döneme bakılarak, 6 ay sonra.

| Ajan | Görev |
|---|---|
| Lider | Lider + **denetçi** (6 saatte bir, `docs/denetim/`). U7 denetimi, `results/U7_SONUC.md`. |
| Codex | **U7** (#200, taslak): U4, U6 (97/97), U1 5m bitti; Reddit 1/2a bitti; Faz 1 GitHub Actions'ta koşuyor (uzun koşular Actions'ta: Codex ortamı arka plan süreçlerini öldürüyor). Sonra `[TV-2] veri eşleme` (Dukascopy, vnstock). Gece görev listesi: `docs/GOREV_GECE_2026-10-24.md`. |
| Sonnet | **Limit bitti, 2026-10-27 Salı 18:00'e kadar görev yok.** Son iş: GOREV_U7 Ek 4 (#206, birleşti): 17 kart çevrildi, 21 Doğrulanamaz (çoğu durum makinesi/açık kâr/izleyen stop: TV-2 yürütücüsüyle yeniden ele alınır). |
| Argon | **İptal** (kullanıcı, 2026-10-24). `arastirma/argon/GOREV_ARGON_1.md` uygulanmayacak; erişilemeyen kaynaklar (K2) Codex/lider işine döner. |

**TV-2** (`docs/GOREV_TV2.md`, `docs/TEST_YAPISI.md`): Pine kodu çeviri yapılmadan yürütülür (`engine/pine`, `engine/tv_emulator.py`, `backtests/tv2.py`). Açık kaynak 969 (+33 kapalı/bulunamadı); kapsam kuralı Ek 2: her strateji sonuç ya da çözüm görevi. Kripto 296: 92+ koşuldu (19 geçti), kalan 204 lider ortamında kuyrukta. Kripto dışı 636 veri eşlemesi bekliyor (yfinance gün içi hazır; Dukascopy/vnstock Codex). Yorumlayıcı 2026-10-24/25 gecesi: calc_on_order_fills, gün içi risk, Heikin Ashi, matrix, alt dilim, kütüphane import, enum, FIFO kapanış, hızlı ayrıştırıcı (~100x). Yapay veri taraması: 969'un ~%90'ı çalışıyor.

**Denetim 2026-10-24** (`docs/denetim/2026-10-24.md`, ek: `docs/denetim/2026-10-24-1846.md`): kendi koyduğumuz sınırlar listesi (K1-K11), yöntem bulguları (MDD95 boyuta bağlı, DSR N tek havuz), kullanıcı kararı bekleyenler.

## Sırada (kullanıcı kararı bekleyen)
- **Kararlar 2026-10-24 (denetim):** düşüş kapısı → getiri/düşüş ≥ 0,5; DSR aile bazlı, eleyici değil (Koşullu(DSR) → gölge kitapta canlı teyit); 942 TV stratejisinin hepsi test edilecek (`docs/GOREV_TV2.md`); short fazı U7'den sonra. Bekleyen: Dukascopy gün içi veri (K8), Pine içi ML (K5).
- **Test yapısı v2 (kullanıcı onayı 2026-10-24, `docs/TEST_YAPISI.md`):** huni eleyici değil. Nedensellik denetimi → sadık test (yazarın sembolü/tf/kodu, long+short; sınama = sürüm tarihi sonrası) → tek kapı (uygulanabilir sonuçta sınama net > 0) → belirsizlik + kopya ayıklama ile sıralama → sanal havuz + 20 gölge kitap → canlı karar (zarar bütçesi %10, aylık kalibre kontrol). Bütün ailelere uygulanır.
1. **U7** (`docs/GOREV_U7.md`, kullanıcı kararı 2026-10-24): kilit kaldırıldı; test edilebilir bütün kartlar (Faz 1 126, U1, U4, U6 74) bugüne kadar; değerlendirme `docs/TEST_YAPISI.md` (Ek 6).
0. ~~Yeni strateji arayışı~~ → **U4 bitti** (kullanıcı kararı 2026-10-24: kripto 4H/1D + ABD/emtia 1D, kendi hipotezlerimiz, yalnız long).
2. Faz 2 pano modülleri (`docs/FAZ2_NOTLAR.md`): koç bulguları, öğrenen koç (gölge mod), strateji radarı.
3. Küçük iyileştirmeler: hesap kartları saatlik değerlenmiyor (yalnız toplam); fiyat zamanı saatlik barın başlangıcını gösteriyor.

## Kapanan fazların özeti
- **Faz 1** (`docs/FAZ1_SONUC_RAPORU.md`): 422 strateji, 137 test. Geçti 2 (C07, R01), Koşullu 3 (A6-010, T8-07, V2B emtia 1H), Reddedildi 132, Doğrulanamaz 273. Önerilen portföy OOS %7,5, MDD %2,9.
- **U5** (`arastirma/U5_ozet.md`): TradingView 1.298 script; 4H/1D süzgecinden 205 aday → U6/U7'de test. **942'si yalnız zaman dilimi yüzünden ayrıldı (denetim K1).**
- **U4** (`results/U4_SONUC.md`): seyrek işlem, 4 kart × 4 kol. 16/16 Reddedildi. Kripto 4H trend IS ve OOS'ta kârlı (3x maliyette de) ama MDD95 %28, DSR düşük, kâr büyük coinlerde.
- **U1** (`results/U1_SONUC.md`): kripto gün içi, 14 varyantın 14'ü Reddedildi. 15m/5m'de brüt kenar yok; 1H'de küçük ama maliyete yetmiyor.
- **U3** (`docs/GOREV_U3.md`, `arastirma/U3_mtf.csv`): 53 MTF strateji kaydı, test edilmedi.
- **T35** (`arastirma/TUM_KAYITLAR.csv`): 80 bölgesel strateji kaydı.

## Temizlik (2026-10-24, kullanıcı onayı)
Faz 1'in kaynak PDF/xlsx'leri, eski görev dosyaları (`docs/GOREV_T*`), `tartisma/`, `argon/`, `kaynak/`, `state.json`, Dukascopy kodu ve büyük işlem dökümleri (`results/tarama_islemler`, `results/trades`, `results/u1/**/islemler_*`) silindi. Hepsi git geçmişinde duruyor: `git log --diff-filter=D --name-only` ile bulunur, `git checkout <commit>^ -- <yol>` ile geri gelir. İşlem dökümleri artık commit edilmez (`.gitignore`); huni ve CI her koşuda yeniden üretir.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz. Çalışma düzeni: `docs/PROTOKOL.md`.
