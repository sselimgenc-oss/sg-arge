# İlk tarama (T5b-1) lider değerlendirmesi

Koşu: lider ortamında, `main` @ 8a0ecbc kodu, 2026-10-22'de indirilen günlük veri (87/88 sembol; KOZAL yok). Süre 22 dk. Çıktı: `results/tarama.csv`, `results/tarama_ozet.md`, `results/tarama_islemler/`.

## Sonuç
42 günlük/haftalık kart × 4 piyasa = 168 satır. **35 kart aşama 2 adayı**, 4 kart reddedildi (A2-007, A3-003, O3-014, O3-015), 3 kart Doğrulanamaz (motor desteği yok: P02, R01 `kismi_kar`; O1-078 `fiyat_adim`).

## Bulgu: birinci aşama kapısı bu dönemde neredeyse bedava
IS döneminde (2020-01 → 2024-09) al-tut getirisi (eşit ağırlık, medyan):

| Piyasa | Al-tut medyan | Tarama medyan PF |
|---|---:|---:|
| BIST30 (TL) | +%1.037 | 2,07 |
| Kripto | +%332 | 1,64 |
| ABD | +%109 | 1,55 |
| Emtia ETF | +%63 | 1,36 |

TL enflasyonu ve kripto boğa piyasası, uzun pozisyonla trend izleyen her kuralı kârlı gösteriyor. BIST'teki PF > 4 alarmlarının (11 satır) çoğu bu etkiden geliyor. **Aşama 1 sonucu "strateji iyi" demek değildir; yalnız "açıkça kötü değil" demektir.**

## Lider kararları (aşama 2 = T6'ya eklenen sert testler)
1. **BIST USD bazında:** BIST fiyatları `USDTRY=X` ile USD'ye çevrilerek test edilir. Karar USD sonucuna göre verilir; TL sonucu yalnız bilgi amaçlıdır.
2. **Rastgele giriş (null model) testi:** Her kart ve piyasa için aynı çıkış kuralları, aynı işlem sayısı ve aynı ortalama tutma süresiyle rastgele giriş tarihleri seçilir (≥ 500 tekrar). Stratejinin PF'i ve işlem başı ortalama R'si, rastgele dağılımın **%95 yüzdeliğini** geçmelidir. Geçemiyorsa kenar piyasanın yükselişinden geliyordur → **Reddedildi (piyasa betası)**. Bu test boğa piyasası yanlılığını tüm piyasalarda giderir.
3. Diğer aşama 2 testleri (`ELEME_KRITERLERI.md` 3b-10) aynen geçerlidir. Bunlara OOS 2024-10 → ve 2015-2019 dahildir; bu dönemler taramada görülmedi.

## Diğer notlar
- **MOC kartları:** O3-007'de ertesi açılış dolumu kapanış dolumundan daha iyi çıktı (BIST PF 1,53 / 1,37). O3-014 (3 gün düşüş) iki varyantta da zayıf → reddedildi.
- **`kismi_kar` desteği** eklenmeli (P02 Davey, R01 Qullamaggie: PDF'lerin en çok iddia edilen iki stratejisi). Sonnet'in limiti yenilenince küçük bir iş.
