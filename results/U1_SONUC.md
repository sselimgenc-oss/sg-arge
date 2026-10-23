# U1 sonuç raporu: kripto gün içi (lider, 2026-10-23)

**Karar: 14 varyantın 14'ü Reddedildi. Paper'a ya da kilitli döneme giden aday yok.** Kilitli dönem (2025-10-01 →) açılmadı.

Kaynak: Codex U1c koşusu (PR #159, dal `codex/u1c-huni`), ön kayıt `docs/GOREV_U1.md`. Veri: Binance spot, 14 coin × 1h/15m/5m, hepsi `status=ok` (`data/MANIFEST.csv`, `results/veri_kalitesi_binance.md`).

## 1. Sonuç tablosu (havuz, 14 coin, maliyet her yönde %0,15)

| Varyant | TF | IS işlem | IS PF | OOS işlem | OOS PF 1x / 2x / 3x | Karar | Nerede elendi |
|---|---|---:|---:|---:|---|---|---|
| T8-07 | 1H | 5351 | 0,84 | 2257 | 0,85 / 0,63 / 0,48 | Reddedildi | 2b: OOS, maliyet, +1 bar, MDD95, kardeş 0/8 |
| V2B | 1H | 9295 | 0,85 | 4999 | 0,73 / 0,48 / 0,36 | Reddedildi | 2b: aynı, kardeş 1/8 |
| U1-H2-A carpan=3 | 15m | 7301 | 0,69 | 3068 | 0,53 / 0,26 / 0,12 | Reddedildi | 2b |
| U1-H2-A carpan=5 | 15m | 5955 | 0,76 | 2483 | 0,64 / 0,40 / 0,25 | Reddedildi | 2b |
| U1-H2-B 17:00 | 15m | 2085 | 0,76 | 875 | 0,47 / 0,24 / 0,13 | Reddedildi | 2b |
| U1-H2-B 20:00 | 15m | 2092 | 0,77 | 863 | 0,57 / 0,34 / 0,21 | Reddedildi | 2a null + 2b |
| U1-H2-C N=12 | 15m | 10248 | 0,59 | 4636 | 0,55 / 0,32 / 0,20 | Reddedildi | 2a null + 2b |
| U1-H2-C N=24 | 15m | 7720 | 0,61 | 3634 | 0,57 / 0,35 / 0,22 | Reddedildi | 2b |
| U1-H2-A carpan=3 | 5m | 12096 | 0,55 | 5383 | 0,35 / 0,11 / – | Reddedildi | Aşama 1 (IS PF < 1) |
| U1-H2-A carpan=5 | 5m | 9187 | 0,63 | 4062 | 0,48 / 0,22 / – | Reddedildi | Aşama 1 |
| U1-H2-B 17:00 | 5m | 3290 | 0,77 | 1279 | 0,48 / 0,26 / – | Reddedildi | Aşama 1 |
| U1-H2-B 20:00 | 5m | 3258 | 0,78 | 1286 | 0,58 / 0,33 / – | Reddedildi | Aşama 1 |
| U1-H2-C N=12 | 5m | 25158 | 0,39 | 11281 | 0,39 / 0,16 / – | Reddedildi | Aşama 1 |
| U1-H2-C N=24 | 5m | 19689 | 0,37 | 9040 | 0,44 / 0,22 / – | Reddedildi | Aşama 1 |

- 1H/15m: `results/u1/huni_ozet.md` (null testi, 2b, kardeş raporu).
- 5m: huni koşusu kullanıcı kararıyla durduruldu. `results/u1/ozet_IS.csv`'de IS PF'i 6 varyantta da 1'in altında; Aşama 1 kuralıyla huniye girmezler. Karar sonucu görmeden verildi; deneme sayısı 14 olarak kalır.
- Coin düzeyinde: 196 coin × varyant OOS satırından 18'inde PF > 1 (~%9). Çoğu 40-300 işlem ve tek coin; şans düzeyinde, aday sayılmaz.

## 2. Neden: brüt kenar maliyeti karşılamıyor

İşlem dosyalarından maliyet geri eklenerek hesaplandı (lider, `results/u1/islemler_*.csv`). **Bu bir deneme değil, karar değiştirmez; yalnız teşhis.**

| Varyant (OOS) | Brüt PF (maliyetsiz) | PF, %0,05/yön | PF, %0,15/yön | İşlem başı brüt kâr (R) | İşlem başı maliyet (R) |
|---|---:|---:|---:|---:|---:|
| T8-07 1H | 1,27 | 1,10 | 0,85 | 0,08 | 0,13 |
| V2B 1H | 1,20 | 1,03 | 0,73 | 0,04 | 0,12 |
| 15m (6 varyant) | 0,88-1,10 | 0,71-0,91 | 0,47-0,64 | 0,00-0,05 | 0,34-0,41 |
| 5m (6 varyant) | 0,94-1,16 | 0,70-0,84 | 0,35-0,58 | −0,01-0,04 | 0,60-0,72 |

- **15m ve 5m'de kenar yok.** Maliyetsiz bile PF ≈ 1. Maliyet işlem başı 0,3-0,7 R; kural ne olursa olsun bu kadar kısa tutmada risk birimine göre çok büyük.
- **1H'de küçük bir brüt kenar var** (brüt PF IS 1,16-1,20, OOS 1,20-1,27), ama maliyeti üçte birine (%0,05/yön, yaklaşık Binance vadeli taker) indirsek bile PF 1,03-1,10; geçme kapısı 1,3, 2x stres 1,2. **Maliyeti düşürmek tek başına bu kuralları kurtarmaz.**
- IS de zararda: sorun aşırı uydurma değil, kuralların kendisi kriptoda bu tutma süresinde para kazanmıyor.

## 3. 250 bin TL ile uygulanabilirlik
Aday olmadığı için uygulanacak strateji yok. Yalnız ölçek fikri vermek için: işlem başı risk %0,5 = 1.250 TL. 15m'de işlem başı maliyet 0,34-0,41 R ≈ 425-510 TL, 5m'de 0,60-0,72 R ≈ 750-900 TL. Hesap büyüklüğü sonucu değiştirmez: maliyet pozisyonla orantılı, Binance asgari emir tutarı da kısıt değil.

## 4. Kayıt notları
- **Ön kayıt metninde yazım hatası:** `docs/GOREV_U1.md` §3 sonundaki uyarı "%0,15 gidiş-dönüş" diyor; ön kayıt tablosu (§1, %0,15/%0,30/%0,45) ve motor **her yönde** %0,15 uyguluyor (Faz 1 ile aynı). Koşu tabloya uygun; karar etkilenmez.
- Kilit kapalı kaldı; kart, kod ve eşik değiştirilmedi (`git diff` ile doğrulandı). Tekrar koşu yapılmadı: sonuç her varyantta IS'te de açık farkla negatif, karar yön değiştiremez.
- Veri kalite raporu 15m ve 5m satırlarını içeriyor; 503 hataları `--append` ile tamamlandı.

## 5. Sıradaki adım için seçenekler (karar kullanıcının)
1. **Daha seyrek işlem:** 4H ya da günlük kurulum, günde en çok birkaç işlem, işlem başı hedef ≥ 1 R. 1H'deki brüt kenar bu yönün denenmeye değer olduğunu gösteriyor. Yeni ön kayıt gerekir.
2. **Maliyet modeli (U2a):** vadeli komisyon + maker emir + funding. Tek başına yetmez (bkz. §2); 1. seçenekle birlikte anlamlı.
3. **U3 havuzu (53 kayıt, `arastirma/U3_mtf.csv`):** çoğu 5m/15m giriş. Bu sonuçtan sonra yalnız 1H/4H kurulumlu ve işlem başı hedefi geniş olanlar ön kayda alınmalı; 5m girişli kısa vadeli olanlara öncelik verilmez.
