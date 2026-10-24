# U4 sonuç raporu: seyrek işlem, kendi hipotezlerimiz (lider, 2026-10-24)

**Karar: 16 varyantın 16'sı Reddedildi** (ön kayıt `docs/GOREV_U4.md`). Kilitli dönem (2025-10-01 →) açılmadı.

Kaynak:
- Codex gerçek koşusu: PR #171, `results/u4/`.
- Lider bağımsız tekrar koşusu: aynı kod, ayrı veri indirmesi. 16 satırın 15'i birebir aynı. U4-H4:ABD25'te 731 ↔ 732 işlem, IS PF 0,98 ↔ 0,99 farkı var; bu, iki indirme arasındaki Yahoo düzeltilmiş fiyat farkı ve kararı etkilemiyor.
- Koşu öncesi lider düzeltmesi: kripto 4H çift yeniden örnekleme hatası (PR #172). Codex raporladı, kodu kendisi değiştirmedi.

## 1. Sonuç tablosu
| Varyant | IS PF / işlem | Null (p PF) | OOS PF 1x / 2x | OOS 3x net | +1 bar net | MDD95 | DSR | Kardeş | Elendiği kapılar |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| **H1 kripto 4H** | 1,87 / 807 | ✓ (0,005) | 1,46 / 1,27 | +%12 | +%69 | %27,8 | 0,47 | 0,38 | MDD95, DSR, kardeş |
| H1 kripto 1D | 2,48 / 121 | ✗ (0,62) | 1,97 / 1,85 | +%8 | +%13 | %14,1 | 0,16 | 0,63 | null, DSR |
| H1 ABD 1D | 1,70 / 115 | ✗ | 1,15 / 1,12 | +%1 | +%3 | %14,3 | 0,07 | – | null, 2x, DSR |
| H1 emtia 1D | 1,69 / 84 | ✗ | 2,32 / 2,22 | +%7 | +%2 | %8,3 | 0,27 | – | null, DSR |
| **H2 kripto 4H** | 1,52 / 368 | ✗ (0,29) | 2,15 / 1,92 | +%84 | +%136 | %28,6 | 0,85 | 0,25 | null, MDD95, DSR, kardeş |
| H2 kripto 1D | 2,72 / 53 | ✗ | 3,60 / 3,43 | +%28 | +%29 | %18,2 | 0,39 | 0,25 | null, MDD95, DSR, kardeş |
| H2 ABD 1D | 1,86 / 82 | ✗ | 1,16 / 1,12 | +%1 | +%5 | %14,5 | 0,08 | – | null, 2x, DSR |
| H2 emtia 1D | 2,83 / 44 | ✓ (0,047) | 1,18 / 1,12 | +%1 | +%2 | %16,1 | 0,06 | – | 2x, MDD95, DSR |
| H3 kripto 4H | 2,21 / 407 | ✓ (0,04) | 1,33 / 1,18 | +%4 | +%21 | %27,2 | 0,23 | 0,13 | 2x, MDD95, DSR, kardeş |
| H3 kripto 1D | 8,83 / 34 | ✗ | 5,37 / 5,12 | +%23 | +%20 | %14,6 | 0,38 | 0,25 | null, DSR, kardeş |
| H3 ABD 1D | 1,65 / 49 | ✗ | 4,70 / 4,59 | +%18 | +%15 | %6,8 | 0,72 | – | null, DSR |
| H3 emtia 1D | 1,14 / 45 | ✗ | 2,74 / 2,63 | +%8 | +%8 | %8,9 | 0,32 | – | null, DSR |
| H4 kripto 4H | 0,78 / 2030 | ✗ | 0,72 / 0,48 | −%68 | −%27 | %42,5 | 0,00 | 0,38 | hepsi |
| H4 kripto 1D | 1,19 / 288 | ✗ | 0,88 / 0,75 | −%8 | +%0 | %13,0 | 0,01 | 0,25 | null, OOS, 2x, 3x, DSR, kardeş |
| H4 ABD 1D | 0,99 / 732 | ✗ | 1,05 / 0,96 | −%5 | +%4 | %11,7 | 0,07 | – | IS, null, 2x, 3x, DSR |
| H4 emtia 1D | 1,00 / 150 | ✗ | 1,19 / 1,04 | −%1 | +%1 | %4,1 | 0,10 | – | IS, null, 2x, 3x, DSR |

## 2. Ne öğrendik
1. **U1'den farklı olarak gerçek bir kâr izi var: kripto 4H trend (H1, H2).** IS'te kârlı, OOS'ta da kârlı. 3x maliyette ve +1 bar gecikmede de kârlı. Kenar maliyete yetiyor; U1'de yetmiyordu.
2. **Ama kapıları geçmiyor; nedenleri önemli:**
   - **Düşüş çok büyük:** MDD95 %28, sınır %15. Kripto coinleri birlikte hareket ediyor; %0,5 risk ve %2 toplam açık riskle bile aynı anda düşen pozisyonlar düşüşü büyütüyor.
   - **Kâr büyük coinlerde:** H2'de çekirdek 6 coin +14.060, kardeş 8 coin −1.330. H1'de çekirdek +4.017, kardeş +332. Tek coin payı H2'de %51 (XRP).
   - **Giriş zamanlaması (H2) rastgeleden ayırt edilemiyor** (p 0,29). Kârın önemli kısmı trend çıkış kuralından ve kriptonun genel yükselişinden geliyor. H1'de giriş anlamlı (p 0,005).
   - **DSR 16 denemeyle düşük** (0,47-0,85). Bu kadar denemede bu sonuçlar şansla da çıkabilir.
3. **ABD ve emtia günlükte trend kartları kârlı ama zayıf;** null testini geçemiyorlar. Bu dönemde (2018-2025) piyasanın kendisi yükseldi; rastgele girişler de kazanıyor.
4. **H4 (RSI(2) geri çekilme) hiçbir yerde çalışmıyor.** Kriptoda açıkça zararlı, ABD/emtia'da başabaş.

## 3. Sonraki adım için seçenekler (karar kullanıcının; ön kayıt kuralları gereği bu sonuçlar yeni bir testin hem kaynağı hem kanıtı olamaz)
- **(a) Yeni ön kayıt: "kripto büyük coin 4H trend, düşük risk".** H1 ve H2 aynı kurallarla, yalnız çekirdek 6 coinde, işlem başı risk düşürülmüş (ör. %0,25) olarak.
  - Bu fikir U4 sonuçlarını görerek doğdu. Bu yüzden IS/OOS'ta yeniden "kanıtlanamaz"; tek dürüst sınav **kilitli dönemdir** (2025-10-01 → bugün, ~13 ay), **bir kez**, sonuç ne çıkarsa.
  - Geçerse paper'a (gölge kitap) alınır.
- **(b) Kripto trendini paper'da gölge kitap olarak izlemek** (H1 4H, çekirdek, düşük risk), kilit dönemini açmadan. Kanıt aylar içinde canlı veriden gelir. Daha yavaş ama kilidi harcamaz.
- **(c) Kriptoyu bırakıp başka bir yöne geçmek** (TradingView U5 adayları, short motoru U2a).

Lider önerisi: **(b)**. Kilitli dönem tek kullanımlık; onu, hipotezi sonuçlara bakarak daralttığımız bir aday için harcamak yerine, canlı paper'ın kendisi tarafsız bir sınavdır. (a) da savunulabilir; daha hızlı cevap verir.

## 4. Kayıt notları
- Deneme sayısı 16, ek deneme yapılmadı.
- İşlem dökümleri commit edilmedi.
- `GOREV_U4.md` bölüm 5'te sonuçtan önce yapılan netleştirme (en iyi ay / tek coin maddeleri Koşullu) hiçbir kararı değiştirmedi: bütün satırlar zaten eleyici kapılarda kaldı.
