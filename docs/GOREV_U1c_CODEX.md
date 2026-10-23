# U1c: Kripto verisi + U1 hunisinin gerçek koşusu (Codex)

**Sahip:** Codex (kullanıcı kararı, 2026-10-23: U1c liderden Codex'e verildi). **Denetim ve sonuç raporu:** lider.
**Ön koşul:** U1a, U1b, U1d main'de (PR #142, #147, #149, #152). Kod hazır; bu görev yeni hesap yazmaz, **koşar ve raporlar.**
**Kurallar kaynağı:** `docs/GOREV_U1.md` (ön kayıt). Bu dosya onunla çelişirse `GOREV_U1.md` geçerlidir.

## 0. Yasaklar (ön kayıt; ihlal = koşu geçersiz)
1. **Kilit açılmaz.** `KILIT_AC` ortam değişkeni tanımlanmaz. Kilitli dönem (2025-10-01 →) yalnız lider kararıyla açılır.
2. **Kart, ızgara, eşik, dönem, maliyet, evren değiştirilmez.** `docs/spec/U1-H2-*.yaml`, `T8-07.yaml`, `V2B.yaml` ve `backtests/u1*.py` içindeki sabitler olduğu gibi kalır.
3. **Hata bulursan sessizce düzeltme.** Koşuyu durdur, hatayı PR açıklamasına yaz (dosya:satır, beklenen/gözlenen). Lider karar verir; düzeltme kabul edilirse etkilenen her şey yeniden koşulur.
4. Sonuca bakıp yeni varyant, ek parametre, ek coin ya da ek tekrar denenmez. Ek deneme yalnız lider kararıyla `results/U1_deneme_kaydi.csv`'ye yazılarak yapılır.
5. Parquet veri dosyaları **commit edilmez** (`.gitignore` zaten dışlar). Yalnız `data/MANIFEST.csv` ve raporlar commit edilir.

## 1. Veri (14 coin × 1 saat, 15 dk, 5 dk)
Coinler: `BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT,TRXUSDT,ADAUSDT,DOGEUSDT,LTCUSDT,LINKUSDT,DOTUSDT,AVAXUSDT,BCHUSDT,NEARUSDT`

```bash
pip install -r requirements.txt
S=BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT,TRXUSDT,ADAUSDT,DOGEUSDT,LTCUSDT,LINKUSDT,DOTUSDT,AVAXUSDT,BCHUSDT,NEARUSDT
python data/fetch.py --interval 1h  --semboller $S --baslangic 2017-01-01
python data/fetch.py --interval 15m --semboller $S --baslangic 2017-01-01
python data/fetch.py --interval 5m  --semboller $S --baslangic 2017-01-01
```

- Kaynak: `data-api.binance.vision` (`api.binance.com` bulut IP'lerinde coğrafi engelli; kullanma). Lider ortamından 2026-10-23'te erişim doğrulandı.
- 5 dk indirmesi uzun sürer (14 coin × ~9 yıl ≈ 13 milyon bar, ~13 bin istek). Yarıda kesilirse aynı komutu `--append` ile tekrar çalıştır.
- Çıktı: `data/hourly/`, `data/15m/`, `data/5m/` altında `<SYM>.parquet`; `data/MANIFEST.csv` güncellenir; `results/veri_kalitesi_binance.md` (15m/5m: boşluk, tekrar, sıfır hacim).
- **Yan etki (1 saat komutu):** `--interval 1h` Faz 1'in `results/veri_kalitesi_1h.md` raporunu yalnız kripto satırlarıyla ezer ve `data/evren.csv` notlarına dokunabilir. 1 saat indirmesinden hemen sonra:
  ```bash
  mkdir -p results/u1 && mv results/veri_kalitesi_1h.md results/u1/veri_kalitesi_1h_kripto.md
  git checkout -- results/veri_kalitesi_1h.md data/evren.csv
  ```
- **Kontrol:** 14 coinin her biri üç aralıkta `status=ok` olmalı. İlk bar listelenme tarihinden önce olamaz (SOL, AVAX, NEAR 2020).
- Erişim engeli (403/451, proxy) çıkarsa **uydurma yok**: hatayı PR'a yaz, kalanını koşma. Alternatif: `data.binance.vision` aylık zip arşivleri (indirici yok; ihtiyaç olursa lider karar verir).

## 2. Kuru kontrol
```bash
python -m pytest -q                                   # tamamı geçmeli (main'de: 370 passed, 4 skipped)
python backtests/u1.py --sadece-say                    # varyant listesi; toplam deneme 14 olmalı
```
Deneme sayısı 14 değilse dur ve raporla.

## 3. IS/OOS metrikleri
```bash
python backtests/u1.py --hat 0,2 --donem IS,OOS --veri-kok data --results-dir results/u1
```
Çıktı: `results/u1/ozet_IS.csv`, `ozet_OOS.csv`, `islemler_<varyant>_<donem>.csv`.

## 4. Huni (null testi → 2b → kardeş raporu → karar)
Bellek için zaman dilimi sırayla, 5 dk en son. **Her koşu kendi klasörüne yazar**, çünkü `u1_huni.py` her koşuda `huni_ozet.csv`'yi baştan yazar (birleştirmez):
```bash
for TF in 1H 15m 5m; do
  python backtests/u1_huni.py --tf $TF --tekrar 200 --isci 0 --veri-kok data --results-dir results/u1/huni_$TF
done
# üç tabloyu birleştir (14 satır), md'yi aynı biçimle üret
python -c "
import pandas as pd; from pathlib import Path; from backtests import u1_huni as h
t = pd.concat([pd.read_csv(f'results/u1/huni_{tf}/huni_ozet.csv') for tf in ('1H','15m','5m') if Path(f'results/u1/huni_{tf}/huni_ozet.csv').exists()], ignore_index=True)
h.write_outputs(t[h.COLUMNS], Path('results/u1')); print(len(t), 'satir')"
```
- `--isci 0` = CPU sayısı, boş belleğe göre kendiliğinden kısılır. Bellek yetmezse `--isci 1` ile tekrar dene ve bunu PR'a yaz.
- Tohumlar varyant adından türetilir (deterministik); aynı veriyle ikinci koşu aynı sonucu vermeli.
- Sınırda p (0,03-0,10) için `--tekrar-yuksek` (1000) otomatik devreye girer; elle değiştirme.
- Birleşik `results/u1/huni_ozet.csv` **14 satır** olmalı (1H: 2, 15m: 6, 5m: 6). `karar=Hata` olan satır varsa nedeniyle raporla.
- 5 dk koşusu belleğe sığmazsa kesme: 1H ve 15m sonuçlarıyla PR aç, 5 dk satırlarını "koşulamadı (bellek)" diye yaz.

## 5. Teslim (PR, dal `codex/u1c-huni`)
Commit edilecekler:
- `data/MANIFEST.csv`, `results/veri_kalitesi_binance.md`
- `results/u1/` (özetler, `veri_kalitesi_1h_kripto.md`, birleşik `huni_ozet.csv/.md`, `huni_<tf>/` klasörleri: `kardes_*.csv/.md` ve işlem CSV'leri).
- `git diff --stat main` ile kontrol et: `docs/`, `engine/`, `backtests/`, `results/veri_kalitesi_1h.md`, `data/evren.csv` değişmemiş olmalı. Tek bir işlem CSV'si 50 MB'ı geçerse onu commit etme, PR'da adını ve satır sayısını yaz.

PR açıklamasına:
1. Çalıştırılan komutlar ve süreleri; makine (CPU, RAM).
2. Veri tablosu: coin × aralık, ilk/son bar, satır, boşluk.
3. `huni_ozet.md` tablosunun kopyası (varyant, karar, neden).
4. Karşılaşılan sorunlar ve ne yapıldığı (yasak 3'e göre).
5. `pytest` sonucu.

PR açılamazsa (API 403) dalı it ve `https://github.com/sselimgenc-oss/sg-arge/pull/new/codex/u1c-huni` bağlantısını teslim notuna yaz.

**Yapılmayacak:** `results/U1_SONUC.md`. Sonuç raporunu (250 bin TL uygulanabilirlik dahil) lider PR'ı denetledikten sonra yazar.

## 6. Kabul ölçütü (lider)
- 14 coin × 3 aralık veri tam, kalite raporu var.
- `huni_ozet.csv` 14 satır, her satırda karar ve neden dolu.
- Kilit kapalı (logda `KILIT_AC=1` uyarısı yok), kart/kod değişikliği yok.
- Tekrar koşuda aynı sonuç (lider örnekle doğrular).
