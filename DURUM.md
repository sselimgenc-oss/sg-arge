# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-26 (akşam), lider. Faz 1 kapanış: `docs/FAZ1_KAPANIS.md`.

## Şu an
**FAZ 1 KAPANDI (2026-10-26, kullanıcı onayı).** Rapor: `docs/FAZ1_KAPANIS.md`.
**Paper (yeni portföy, 2026-10-26'dan):** 11 kitap — ABD 4, kripto 5, emtia 2; tek portföy 5.000 USD sanal, %75 kitaplarda, %25 nakit (`paper/portfoy.yaml`). Gerçek para yok.
- Risk: kitap zirveden %10 → kitap durur; portföy zirveden %5 → yeni giriş durur.
- Eski Faz 2 paper kitapları (C07, R01, A6-010, gölge U4-H1/T8-07/V2B) emekli; defter `paper-defter` dalında `paper/defter/arsiv/2026-10-26/`.
- Pano: `sg-pano` (GitHub Pages), `PANEL_TOKEN` ile.

**Faz 2 başı (sıralı):** (1) TV-2 Pine paper motoru — G4RNcGXg, wcegMOXj (BTC→USD), yhoK9cH4; kaynaklar `paper/tv2_kaynak/`; (2) 200 günlük ortalama kuralı (nedensel); (3) QCkIgf3z, BR74LOKo, zuEOEYPK, 9u8pzF0I doğrulamaları. Repo temizliği yapıldı (madde 5).

## Faz 1 NİHAİ KARAR (kullanıcı onayı 2026-10-26)
`docs/faz1_son_denetim.md` → ilk dalga 11 risk kitabı + 3 gölge (kripto). Paper öncesi kontroller tamam (#246). **Kullanıcı onayı 2026-10-26: paper başlasın; "gölge" yok — 3 kripto kitabı normal kitap.** Kurulum: `docs/GOREV_PAPER_KURULUM.md` (Aşama A 11 U7 kitabı, Aşama B 3 TV-2 kitabı). Eski 6 paper kitabı arşive. Sonra: `paper/` uygulaması (kullanıcı onayı), Faz 1 sonuç raporu, repo temizliği.

## Faz 1 kapanış ölçütü (kullanıcı hedefi 2026-10-26: "şu faz 1 bitsin")
Faz 1 şu dört şart sağlanınca kapanır; sonrası Faz 2/3:
1. **Her test edilebilir stratejinin tek satır sonucu var:** TV-2 kripto + kripto dışı 636 + U7. `veri_yok` satırları **bir kez** ikinci kaynakla denenir (Argon veri raporu), bulunamazsa `veri_yok` olarak kapanır; kapanışı bekletmez.
2. **Sıralama tek tabloda:** TV-2 + U7 geçenler, aynı yöntemle (`tv2_sirala`, kopya ayıklama).
3. **Aday tablosu → kullanıcı seçimi:** geçen bütün küme temsilcileri (TV-2 + U7 + Dukascopy sonrası) tek tabloda (`results/faz1_adaylar.csv` + `.md`); paper'a hangilerinin gireceğini kullanıcı eleyerek seçer (kullanıcı kararı 2026-10-26).
4. **Faz 1 sonuç raporu** (lider): geçenler, kalanlar, kapanmayanların nedeni.
5. **Repo temizliği — YAPILDI (kullanıcı onayı 2026-10-26):** önceki durum `faz1-son` etiketinde. `main`'den kaldırılanlar: geçmeyen 837 TV-2 strateji satır/getiri dosyası, 10 eski görev/durum belgesi, 16 eski denetim notu. Tüm 933 TV-2 kararı tek dosyada: `results/faz1_tum_sonuclar.csv` (kimlik, sembol, tf, karar, neden, net, url; DSR deneme sayısı ve tekrar ayıklaması için). Kalanlar: geçen 96 TV-2 satırı, U7 kartları ve kodu, `results/u1`, `u4`, `u7`, veri, `arastirma/`, motor, paper; aday tablosunun okuduğu iki şüphe taraması notu (`docs/denetim/tv2_supheli.md`, `tv2_kripto_disi_supheli.md`).
Bu listeye yeni test turu eklenmez; yeni fikirler (BIST 8 fikir, radar) Faz 2 kuyruğuna gider.

**Durum 2026-10-26 16:30 TR (kullanıcı kararı: Faz 2/3 araştırması durduruldu, tüm güç Faz 1'e):**
- TV-2 (kripto + kripto dışı, 933 satır): geçti 32, kaldı 58, izle 373 (357'si "sürüm sonrası 1 yıldan az veri"), veri_yok 401 (365'i Dukascopy FX/CFD gün içi önbellek bekliyor), işlem_yok 32, diğer 37.
- **Döviz pariteleri (kullanıcı kararı 2026-10-26):** kullanılmayacak; FX stratejileri Dukascopy kuyruğundan çıkarıldı, `veri_yok` olarak kalır ve temizlikte gider. Dukascopy yalnız altın, gümüş ve ABD endeks CFD'leri için.
- **`izle` 373 (kullanıcı kararı 2026-10-26):** bekletilmez; eldeki kısa sınama penceresiyle aynı tek kapı uygulanır (`kisa_sinama=true` bilgi sütunu). Ön sayım ~66 geçer, hepsi paper'a.
- U7: 85 Geçti → 72 küme temsilcisi (`results/u7/siralama.csv`, PR #215); U1 5m kalan 8 varyant koşuyor.
- Kalan iş: (a) Dukascopy ikinci kaynak denemesi (veri_yok 365), (b) TV-2 + U7 tek sıralama, (c) geçen tüm temsilcilerin (~100) paper'a alınma planı, (d) Faz 1 sonuç raporu.
- Son Argon raporları arşivde: `arastirma/veri/`, `arastirma/bist/`, `arastirma/mt5/` (Faz 2/3 için; şimdilik işlenmeyecek).

## Sırada (kullanıcı kararı bekleyen)
- **Kararlar 2026-10-24 (denetim):** düşüş kapısı → getiri/düşüş ≥ 0,5; DSR aile bazlı, eleyici değil (Koşullu(DSR) → gölge kitapta canlı teyit); 942 TV stratejisinin hepsi test edilecek (`docs/GOREV_TV2.md`); short fazı U7'den sonra. Bekleyen: Dukascopy gün içi veri (K8), Pine içi ML (K5).
- **Test yapısı v2 (kullanıcı onayı 2026-10-24, `docs/TEST_YAPISI.md`):** huni eleyici değil. Nedensellik denetimi → sadık test (yazarın sembolü/tf/kodu, long+short; sınama = sürüm tarihi sonrası) → tek kapı (uygulanabilir sonuçta sınama net > 0) → belirsizlik + kopya ayıklama ile sıralama → sanal havuz + 20 gölge kitap → canlı karar (zarar bütçesi %10, aylık kalibre kontrol). Bütün ailelere uygulanır.
1. **U7** (`docs/GOREV_U7.md`, kullanıcı kararı 2026-10-24): kilit kaldırıldı; test edilebilir bütün kartlar (Faz 1 126, U1, U4, U6 74) bugüne kadar; değerlendirme `docs/TEST_YAPISI.md` (Ek 6).
0. ~~Yeni strateji arayışı~~ → **U4 bitti** (kullanıcı kararı 2026-10-24: kripto 4H/1D + ABD/emtia 1D, kendi hipotezlerimiz, yalnız long).
2. Faz 2 pano modülleri (`docs/FAZ2_NOTLAR.md`): koç bulguları, öğrenen koç (gölge mod), strateji radarı.
3. Küçük iyileştirmeler: hesap kartları saatlik değerlenmiyor (yalnız toplam); fiyat zamanı saatlik barın başlangıcını gösteriyor.

## Kapanan fazların özeti
- **Faz 1** (`docs/FAZ1_SONUC_RAPORU.md`, `faz1-son` etiketinde): 422 strateji, 137 test. Geçti 2 (C07, R01), Koşullu 3 (A6-010, T8-07, V2B emtia 1H), Reddedildi 132, Doğrulanamaz 273. Önerilen portföy OOS %7,5, MDD %2,9.
- **U5** (`arastirma/U5_ozet.md`): TradingView 1.298 script; 4H/1D süzgecinden 205 aday → U6/U7'de test. **942'si yalnız zaman dilimi yüzünden ayrıldı (denetim K1).**
- **U4** (`results/U4_SONUC.md`): seyrek işlem, 4 kart × 4 kol. 16/16 Reddedildi. Kripto 4H trend IS ve OOS'ta kârlı (3x maliyette de) ama MDD95 %28, DSR düşük, kâr büyük coinlerde.
- **U1** (`results/U1_SONUC.md`): kripto gün içi, 14 varyantın 14'ü Reddedildi. 15m/5m'de brüt kenar yok; 1H'de küçük ama maliyete yetmiyor.
- **U3** (`docs/GOREV_U3.md` `faz1-son` etiketinde, `arastirma/U3_mtf.csv`): 53 MTF strateji kaydı, test edilmedi.
- **T35** (`arastirma/TUM_KAYITLAR.csv`): 80 bölgesel strateji kaydı.

## Temizlik (2026-10-24, kullanıcı onayı)
Faz 1'in kaynak PDF/xlsx'leri, eski görev dosyaları (`docs/GOREV_T*`), `tartisma/`, `argon/`, `kaynak/`, `state.json`, Dukascopy kodu ve büyük işlem dökümleri (`results/tarama_islemler`, `results/trades`, `results/u1/**/islemler_*`) silindi. Hepsi git geçmişinde duruyor: `git log --diff-filter=D --name-only` ile bulunur, `git checkout <commit>^ -- <yol>` ile geri gelir. İşlem dökümleri artık commit edilmez (`.gitignore`); huni ve CI her koşuda yeniden üretir.

## Kural
Her ajanda aynı anda tek iş. İş bitip lider incelemeden yenisi açılmaz. Çalışma düzeni: `docs/PROTOKOL.md`.
