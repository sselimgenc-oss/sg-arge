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
