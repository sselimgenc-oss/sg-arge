# Faz 1 kapanış raporu

Tarih: 2026-10-26 · Hazırlayan: lider (Claude) · Değerlendirme ortağı: Sol 6.1 (Codex) · Karar: kullanıcı

Faz 1'in hedefi: toplanan bütün stratejileri tek, önceden yazılmış kurallarla ve ücretsiz veriyle test etmek, paper'a girecek listeyi çıkarmak. Bu rapor 2026-10-23 tarihli ilk raporun (`docs/FAZ1_SONUC_RAPORU.md`, `faz1-son` etiketinde) yerine geçer.

## 1. Ne test edildi

| Aile | Test edilen | Sonuç |
|---|---:|---|
| Faz 1 kartları (strateji listesi, Reddit, kendi hipotezlerimiz U1–U4) | 638 kart | 411 doğrulanamaz (kaynakta sinyal tanımı yok / veri yok), 132 reddedildi, 83 bekliyor/kapsam dışı; U7 ile yeniden değerlendirildi |
| U7 (Faz 1 + U1 + U4 + U6: TradingView stratejileri 25'lik sepette) | 119 varyant | 85 geçti → 72 küme temsilcisi |
| TV-2 (TradingView stratejileri yazarın sembolünde, Pine koduyla) | 933 strateji | 96 geçti, 304 kaldı, 93 işlem yok, 401 veri yok, 39 diğer |

Tek kapı: gerçekçi maliyetle (kripto %0,1/taraf; diğerleri %0,05/taraf + 1 tick) yayım sonrası sınama döneminde net > 0 (`docs/TEST_YAPISI.md`).
Kapanmayanlar: döviz pariteleri (kullanıcı kullanmayacak), altın/endeks gün içi Dukascopy koşusu (kullanıcı kararıyla durduruldu), yerel piyasalar (ücretsiz gün içi veri yok).

## 2. Eleme zinciri

1. Geçen küme temsilcileri: 158 (TV-2 86 + U7 72).
2. Kullanıcı elemesi: 15 dk altı; tek enstrüman ve yılda < 30 işlem; zayıf listeden kullanıcı seçimi → 99 (`results/faz1_kullanici_eleme.csv`).
3. Lider ölçütleri R1–R6 (p10 ≤ 0, hata şüphesi, işlem sıklığı, PF < 1,2, 2x maliyette zarar, korelasyon > 0,6) → 24 (`docs/faz1_nihai_degerlendirme.md`).
4. Sol 6.1 bağımsız değerlendirmesi → 35 kalsın, ilk dalga 11 (`docs/sol_nihai_degerlendirme.md`); karşılaştırma ve uzlaşma `docs/faz1_karsilastirma.md`, kripto `docs/faz1_kripto.md`.
5. Son denetim (ikimiz): piyasa payı/alfa, mutabakat, ölü strateji taraması (`docs/faz1_son_denetim.md`).

## 3. Nihai liste — paper'da (2026-10-26'dan, tek portföy 5.000 USD sanal)

| Alan | Kitap | Pay | Durum |
|---|---|---:|---|
| ABD | TV-zoY9DmsF | 9 | paper |
| ABD | TV-DUCODGjC | 7 | paper |
| ABD | TV-dpkq3n4O | 7 | paper |
| ABD | TV-70PkIvTL | 7 | paper |
| ABD | G4RNcGXg (SPY 1s) | 5 | **Faz 2 başı** (Pine paper motoru) |
| Kripto | TV-71yKm18B (4s) | 10 | paper |
| Kripto | TV-3BXWqwnF | 6 | paper |
| Kripto | TV-egTb7TgJ | 3 | paper |
| Kripto | TV-Q9OQye4C | 3 | paper |
| Kripto | U4-H2 kripto 1G | 3 | paper |
| Kripto | wcegMOXj (ETHBTC 6s) | 5 | **Faz 2 başı** (Pine motoru + USD dönüşümü) |
| Emtia | TV-KO7Qe4Xb | 13 | paper |
| Emtia | U4-H3 emtia 1G | 7 | paper |
| Keşif | yhoK9cH4 (META 15dk) | 5 | **Faz 2 başı** (Pine motoru) |
| — | Nakit (Faz 2 başı payları 15 + rezerv 10) | 25 | |

Risk kuralları (paper'da çalışan): kitap kendi zirvesinden %10 gerilerse durur; portföy zirveden %5 gerilerse yeni giriş durur.
Henüz çalışmayan: SPY/BTC 200 günlük ortalama altında yeni uzun riskin yarıya inmesi (Faz 2 başı; her tarihte nedensel uygulanmalı).
Yedek: TV-oF6FmwfR, TV-jc2hs2qK, U4-H3 ABD. Bekleme (doğrulama): QCkIgf3z, BR74LOKo, zuEOEYPK, 9u8pzF0I. Çıkan: TV-IMKs0OPw (yazar kodunda 2025-01-01 tarih filtresi; ölü).

## 4. Dürüst değerlendirme

- Liste küçük, kuralları önceden sabitlenmiş bir **öğrenme denemesidir**; "alfası kanıtlanmış portföy" değildir.
- 2023–2026 hem ABD hem kripto için güçlü yükseliş dönemi; stratejilerin çoğu uzun yönlü, getirinin %35–70'i piyasadan. Piyasadan bağımsız kısım hepsinde pozitif, yalnız ikisinde nominal t ≈ 2 (zoY9DmsF, wcegMOXj) — seçilmiş adaylarda bu kanıt sayılmaz.
- Kripto kitapları 2023–24'te kazandı, 2025'te zayıf; sepet stratejileri birbirine 0,55–0,80 benzer (aynı piyasa riski).
- Asıl karar paper sonuçlarıyla verilecek: aylık kontrol, en az 26 canlı hafta (`docs/TEST_YAPISI.md` Adım 5).

## 5. Süreçten dersler

- Liderin hataları denetimde yakalandı: yılda-işlem hesabı yanlış pencere; TV-2 seri/rapor paydası; ölü strateji atlanması (Sol yakaladı). Bağımsız ikinci göz değerli.
- Codex'in paper değişikliği testleri koşmadan geldi (20 test kırıktı); birleştirmeden önce tam test zorunlu.
- Gün içinde çok sayıda kural değişikliği karışıklık yarattı; Faz 2'de kararlar tek belgede (DURUM) toplanacak.

## 6. Faz 2 başı (sıralı)

1. TV-2 Pine paper motoru: G4RNcGXg, wcegMOXj (BTC→USD), yhoK9cH4 (Actions'ta kaynak çek + SHA256 doğrula). Kaynaklar `paper/tv2_kaynak/`.
2. 200 günlük ortalama kuralı (nedensel).
3. Bekleyen doğrulamalar: QCkIgf3z (Coinbase ↔ Binance), BR74LOKo/zuEOEYPK (gerçek perp + funding), 9u8pzF0I (kontrat).
4. ~~Repo temizliği~~ yapıldı (2026-10-26): geçmeyen TV-2 satır/getiri dosyaları, eski görev ve denetim notları silindi; hepsi `faz1-son` etiketinde. Tüm TV-2 kararları tek dosyada: `results/faz1_tum_sonuclar.csv`.
