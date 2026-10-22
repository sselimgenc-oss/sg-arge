# Faz 1 sonuç raporu

Tarih: 2026-10-23 | Hazırlayan: lider (Opus) | Ekip: Sonnet (claude-moderator), Codex (Terra/Sol), Argon (Gemini)

Hedef (`docs/HEDEF.md`): toplanan stratejilerin hepsini tek ve evrensel kurallarla, ücretsiz verilerle test etmek ve başarılı/başarısız listesini çıkarmak. Paper trade Faz 2'nin işi.

## 1. Sonuç

| Durum | Adet | Anlamı |
|---|---:|---|
| ✅ **Geçti** | **2** | Bütün kapıları şerhsiz geçti. Paper'a hazır. |
| 🟡 **Koşullu** | **3** | Kârlı ve sağlam, ama birer şerhi var. |
| ❌ Reddedildi | 134 | Test edildi, bir kapıda elendi. |
| ⚪ Doğrulanamaz | 273 | Kural, kaynak ya da veri eksik; test edilemedi. |
| ⏸ Ertelendi / Kapsam dışı | 7 | |
| ⏳ Bekliyor | 3 | 1 dakikalık veri gerekiyor (bkz. bölüm 5). |
| **Toplam** | **422** | |

Test edilebilen 139 stratejinin 5'i (%3,6) ayakta kaldı.

### Geçenler

| ID | Strateji | Piyasa | PF (IS) | OOS getiri | Bootstrap MDD95 |
|---|---|---|---:|---:|---:|
| **C07** | Codex: ADX kırılım + risk | ABD25, günlük | 2.18 | +13.0% | 10.1% |
| **R01** | Qullamaggie kırılım devamı + episodic pivot | ABD25, günlük | 2.02 | +1.6% | 13.8% |

İkisi de tarihsel hisse listesiyle (PIT) test edildi, yani survivorship yanlılığı yok.

### Koşullular

| ID | Strateji | Piyasa | PF (IS) | OOS getiri | MDD95 | Şerh |
|---|---|---|---:|---:|---:|---|
| A6-010 | Gap Momentum | EMTIA, günlük | 1.38 | +7.8% | 10.6% | 2015–2019 ön dönemi zararda |
| T8-07 | StackLight MTF momentum | EMTIA, 1 saat | 1.39 | +5.8% | 7.9% | Ön dönem verisi yok (yfinance ~2 yıl) |
| V2B | VOLTRAN-2B saatlik momentum | EMTIA, 1 saat | 1.28 | +3.1% | 8.3% | Ön dönem verisi yok |

### Önerilen portföy (günlük adaylar, eşit ağırlık)
C07 + R01 + A6-010 (`results/portfoy.md`):

| Dönem | Getiri | Yıllık | En büyük düşüş | Bootstrap MDD95 |
|---|---:|---:|---:|---:|
| OOS (2024-10 → bugün, ~2 yıl) | 7.5% | 3.6% | 2.9% | 4.7% |
| IS (2020–2024/09) | 21.1% | 4.1% | 4.6% | 6.7% |

- Stratejiler arası ortalama korelasyon 0,20; stres günlerinde 0,22.
- %15 portföy kayıp sınırı rahatça karşılanıyor.
- Getiriler mütevazı (yıllık ~%4), ama risk de çok düşük. Kaldıraç ya da ağırlık kararı Faz 2'de alınacak.
- Saatlik iki Koşullu (T8-07, V2B) bu tabloya dahil değil, çünkü saatlik veri yalnız ~2 yıl. Faz 2'de ayrı bir "gözlem" kitabı olarak eklenebilirler.

## 2. Eleme hunisi: nerede, neden elendiler

| Aşama | Ne soruyor | Elenen |
|---|---|---:|
| Aşama 1 (tarama) | Maliyetle kâr var mı, en az 30 işlem var mı? | 44 |
| Aşama 2a (rastgele giriş) | Kazanç stratejiden mi, piyasanın yükselişinden mi geliyor? | 54 |
| Aşama 2b (son eleme) | OOS, ön dönem, 2x/3x maliyet, parametre platosu, bootstrap MDD ≤ %15, DSR | 36 |

**En çok eleyen kapı Aşama 2a oldu.** İnternetteki stratejilerin çoğu 2020–2024 boğa piyasasında iyi görünüyor, ama rastgele günlerde girmekten daha iyi değil.

**Kıl payı denetimi** (`results/denetim_kil_payi.md`). Ön kayıtlı, kurallar sonuçlardan önce yazıldı.
- **Soru:** Aşama 2a'da elenen 147 satırda kaybı küçültme (risk) avantajı var mı?
- **Bulgu:** Benjamini–Hochberg düzeltmesinden sonra keşif çıkmadı. 7 satırda p < 0.05 vardı; şans beklentisi 7,4.
- **OOS bozulması:** Yalnız OOS yüzünden elenen 2 stratejinin bozulması istatistiksel olarak anlamlı.
- **Sonuç:** Eleme, iyi bir stratejiyi gözden kaçırmamış.

## 3. Doğrulanamaz 273: neden test edilemedi

| Neden | Adet |
|---|---:|
| Kaynakta giriş/çıkış kuralı eksik | 159 |
| Kural tam, ama genel kart diliyle yazılamıyor (özel kod) | 45 |
| Gizli ya da ücretli kaynak | 35 |
| Yoruma dayalı (ihtiyari) | 14 |
| Kaynak sayfası açılamadı | 13 |
| Veri ya da motor kısıtı | 7 |

- **T16:** 50 eksik kart yeniden denendi, hiçbiri tamamlanamadı. Uydurma yapılmadı.
- **T33 (özel kod):**
  - 15 test edilebilir kartın 4'üne bakıldı.
  - A1-027 yazıldı ve elendi (işlem < 30). Diğer 3'ünde kaynakta formül tanımsız.
  - Kalan 11 kart Codex'in limiti bittiği için denenmedi.
- **T31 (13 erişilemeyen kaynak):** Kullanıcı kararıyla iptal edildi.

## 4. Yol boyunca bulunan ve düzeltilen önemli hatalar
- **Motorda look-ahead (#104):** Bar içinde dolan bekleyen emirler aynı barın açılışıyla kâra çıkıyordu. Düzeltilince iki strateji PF 3–5'ten ~1'e düştü; listedeki sonuçlar etkilenmedi.
- **Satır silme hataları:** `--kart-ids` ile koşmak, Aşama 2a ve 2b'de koşulmayan satırları siliyordu. Düzeltildi. Bu hatalar artık CI'daki parite testiyle otomatik yakalanıyor (T28).
- **Survivorship:** BIST ve ABD için 2015–2026 tarihsel endeks listeleri kuruldu (T11, T11b). Geçenler bu listelerle doğrulandı.
- **Gün içi bellek/hız (T30):** 5 dakikalık kart taraması 41 dakikadan 2,5 dakikaya indi; sonuçlar birebir aynı.

## 5. Açık kalanlar
- **Bekliyor 3:** A3-002a ve A3-002c (kripto, 1 dakikalık) ve O1-064 (Nasdaq vadelisi, 1 dakikalık). Ücretsiz 1 dakikalık veri yok ya da çok büyük. Kriptonun 30m/15m/5m kartlarından hiç aday çıkmadığı için beklenti çok düşük.
- **T33'ün kalan 11 kartı:** Codex yeniden açılırsa yapılabilir.
- **Saatlik Koşullular:** T8-07 ve V2B için ön dönem verisi ücretsiz kaynakta yok. Bu yüzden Koşullu kalırlar; ancak paper'da kanıtlanırlarsa yükselirler.

## 6. Faz 2'ye geçiş (kullanıcı kararı gerekiyor)
Altyapı hazır: `paper/` dizini (günlük sinyal, sanal defter, parite, panel çıktısı) ve kapalı duran `paper.yml` zamanlaması.

**Karar 1: Paper'a hangi stratejiler girecek?**
- **a.** Yalnız Geçti (C07, R01). En temiz kanıt.
- **b.** Geçti + günlük Koşullu (C07, R01, A6-010). Önerilen portföy bu; çeşitlendirmesi daha iyi.
- **c.** b + saatlik Koşullular, ayrı bir gözlem kitabında.

**Lider önerisi:** b ile başlamak, saatlikleri ayrı gözlem kitabında izlemek.

**Karar 2:** Paper süresi ve başarı kriteri. Öneri: en az 6 ay; paper PF ve MDD'si backtest'in %95 bandı içinde kalmalı.

Faz 2 iş listesi `docs/FAZ2_NOTLAR.md`'de:
- birleşik pano (`strateji-test-pano` arayüzü);
- işlem açıklamaları;
- koç bulguları;
- öğrenen koç (ML, gölge modda);
- strateji radarı.
