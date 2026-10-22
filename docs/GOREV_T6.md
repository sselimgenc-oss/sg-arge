# T6 - Asama 2 tam dogrulama ve sonuc raporu

Sahip: codex-worker (T1b'den sonra). Atayan: lider.
Girdi: `results/tarama.csv` icinde `asama2_aday = True` olan kart × piyasa satirlari (ilk tarama: 35 kart). Ayrica T1a/T1b Codex Algo satirlari.

## Test sirasi (pahali testler zayif adaylara harcanmaz)
1. **BIST USD donusumu** (`USDTRY=X`, yfinance): BIST satirlari USD fiyatlariyla yeniden kosulur.
2. **Rastgele giris (null model):** ayni cikislar, ayni islem sayisi ve tutma suresi, >=500 tekrar, sabit seed. PF ve ortalama R %95 yuzdeligi gecmeli. Gecemeyen → `Reddedildi (piyasa betasi)`.
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
