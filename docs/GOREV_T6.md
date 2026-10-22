# T6 - Asama 2 tam dogrulama ve sonuc raporu

Atayan: lider. Iki parca:
- **T6a (Sonnet, simdi):** madde 0, 1, 2 → piyasa betasi testleri. `results/asama2a.csv`.
- **T6b (Codex, T1b'den sonra):** madde 3-6, yalniz T6a'yi gecen satirlara. `results/asama2.csv`, `results/SONUC.md`.
Girdi: `results/tarama.csv` icinde `asama2_aday = True` olan kart × piyasa satirlari (ilk tarama: 35 kart). Ayrica T1a/T1b Codex Algo satirlari.

## Test sirasi (pahali testler zayif adaylara harcanmaz)
0. **On kosul (T6a):** motora `kismi_kar` destegi (P02 Davey, R01 Qullamaggie). D5'e anlami yazilir; T1a ve tarama paritesi bozulmamali. P02 ve R01 taramadan gecirilir.
1. **BIST USD donusumu** (`USDTRY=X`, yfinance): BIST satirlari USD fiyatlariyla yeniden kosulur.
2. **Rastgele giris (null model):** ayni cikislar, ayni islem sayisi ve tutma suresi, >=500 tekrar, sabit seed. PF ve ortalama R %95 yuzdeligi gecmeli. Gecemeyen → `Reddedildi (piyasa betasi)`.
   - Uygulama (T6a): kartin giris sinyali yerine, ayni piyasada ayni sembol dagilimiyla rastgele secilmis giris barlari; cikis/stop/boyut kurallari ve portfoy limitleri aynen. Donem IS (taramayla ayni; OOS ve 2015-2019 hala gorulmez).
   - Cikti satiri: kart, piyasa, PF, ortR, null PF %50/%95, null ortR %50/%95, p-degeri, karar.
   - Hesap yuku: 35 kart × ~4 piyasa × 500 tekrar. Gerekirse once 200 tekrar, sinirda kalanlar (p 0,03-0,10) icin 1000. Sure Actions'ta 6 saati gecmemeli.
3. **OOS** 2024-10-01 → son ve **on donem** 2015 (kripto 2018) → 2019-12-31: maliyet sonrasi pozitif beklenti (ELEME_KRITERLERI 3b, 5).
4. Maliyet/gecikme stresi: 2x PF >= 1,2; 3x ve +1 bar pozitif.
5. Parametre platosu (2-3 boyut komsuluk), block bootstrap MDD, DSR (N: kaynak denemeleri + tarama satir sayisi 168 + T1), ornek/anlamlilik.
6. Karar: Gecti / Kosullu / Dogrulanamaz / Reddedildi + gerekce.

## Cikti
- `results/asama2.csv` (kart, piyasa, her testin sonucu, karar, gerekce)
- `results/SONUC.md`: kullaniciya teslim edilecek liste. Tum ~316 strateji: tarama ve asama 2 kararlari + Dogrulanamaz olanlar (neden: kaynak erisilemedi / ozel kod / piyasa ozgu / veri yok). Basarili adaylar ust tabloda.
- Gercek kosu GitHub Actions'ta (`workflow_dispatch`); push oncesi `git pull --rebase`.

## Yapmayacaklari
Parametre optimizasyonu yok (plato yalniz komsuluk testi). Kart kurali degistirilmez.

## T6b ayrintili gorev (lider, 2026-10-22) — Codex
**Onerilen model seviyesi: GUCLU** (istatistiksel test tasarimi; hata sonuclari bozar).

Girdiler:
- Kart satirlari: `results/asama2a.csv`'de `karar` = aday kalan kart × piyasa satirlari (lider kosusu bitince main'e gelir; o zamana kadar sentetik veri ve birkac ornek kartla gelistir).
- Codex Algo satirlari: C01-C21 (`strategies/*.py`). **Bunlar henuz rastgele giris testinden gecmedi:** once `backtests/asama2a.py`'deki `random_entry_signals` / `null_distribution` mantigini `strategies/*.py` sinyallerine uygula (ayni null kurallari, ayni seed politikasi; BIST satirlari USD). Kod tekrari yerine ortak fonksiyonu kullan; `asama2a.py`'nin karta ozel kismina dokunma.

Yapilacaklar (`backtests/asama2b.py`, tek giris noktasi):
1. **OOS** (2024-10-01 → son) ve **on donem** (2015-01-01, kripto 2018 → 2019-12-31): 1x maliyet. Kapı: OOS islem >= 30 ise ortalama R > 0; on donem negatifse `Kosullu`.
2. **Stres:** 2x PF >= 1,2; 3x ve +1 bar gecikmede net > 0 (IS donemi).
3. **Plato:** kartin `parametreler` alanindaki (yoksa gostergelerin `n`/`carpan` alanlari) en fazla 2 parametre, ±%20 ve ±%40 komsuluk (5×5 izgara). Rapor: komsu medyan PF, pozitif hucre orani, merkez izgara kenarinda mi. Kapı: pozitif hucre orani >= %60. **Optimizasyon degil:** merkez hep kaynak degeri.
4. **Block bootstrap:** gunluk portfoy getirileri, blok 20 gun, 1000 tekrar, sabit seed. %95 MDD ve CAGR alt %5. Kapı: %95 MDD portfoy risk butcesi (%15) icinde.
5. **DSR:** Bailey & Lopez de Prado. N = kaynaktaki deneme sayisi (`deneme_sayisi_kaynakta`, yoksa 1) + bizim tarama satir sayisi (`results/tarama.csv` satir sayisi) + T1 satirlari. N, 2N, 5N icin raporla; karar kotumser olana gore. Kapı (canli icin): DSR >= 0,95; paper icin yalniz raporlanir.
6. **Karar:** her satir icin `Gecti` / `Kosullu` / `Reddedildi` + gerekce (hangi test). ELEME_KRITERLERI kapı ozeti tablosuna gore.

Ciktilar:
- `results/asama2b.csv`, `results/asama2b_ozet.md`
- `.github/workflows/asama2b.yml` (`workflow_dispatch`, push oncesi `git pull --rebase`)
- `tests/`: her test icin sentetik veride bilinen sonuclu birim testi (or. rastgele yuruyus serisinde DSR dusuk; trendli seride plato pozitif).

Kurallar: `engine/` cekirdegine dokunma (gerekirse ince sarmalayici). Sonuclari ben (lider) ayrica kendi ortamimda kosup kontrol ederim.
PR: `[Codex-Sol] T6b asama 2 tam dogrulama`.
