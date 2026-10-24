# U4: Seyrek işlem, kendi hipotezlerimiz (ön kayıt)

**Karar:** kullanıcı, 2026-10-24.
- Piyasalar: kripto 4H ve 1D; ABD hisse ve emtia ETF 1D.
- Strateji kaynağı: kendi hipotezlerimiz, az ve öz.
- Yön: yalnız long. Short ayrı bir faz olacak (U2a).

**Ön kayıt sahibi:** lider. Bu dosya sonuç görülmeden yazıldı. Kural, parametre, dönem, maliyet ve kapılar **sonuca bakılarak değiştirilmez**.

**Neden:** U1'de kripto 15m/5m'de brüt kenar çıkmadı. 1H'de küçük bir brüt kenar vardı (PF 1,15-1,27) ama maliyete yetmedi (`results/U1_SONUC.md`). Seyrek işlemde işlem başı hareket daha büyük, maliyet payı daha küçük.

## 1. Dönemler ve kilit
| Dönem | Kripto (4H, 1D) | ABD / emtia (1D) |
|---|---|---|
| Ön dönem (yalnız işaret) | — | 2015-01-01 → 2017-12-31 |
| **IS** (geliştirme) | 2018-01-01 → 2022-12-31 | 2018-01-01 → 2022-12-31 |
| **OOS** | 2023-01-01 → 2025-09-30 | 2023-01-01 → 2025-09-30 |
| **Kilitli** | 2025-10-01 → | 2025-10-01 → |

- Kilitli dönem `engine/kilit.py` ile kapalı (`KILIT_SONU` 2025-09-30). Yalnız Geçti/Koşullu aday kalırsa, lider kararıyla **bir kez** açılır.
- Göstergelerin ısınması için dönem başından önceki veri kullanılabilir; o dönemde işlem açılmaz.
- **Dürüstlük notu:** ABD/emtia 2015-2024 verisi Faz 1'de çok kez görüldü. Bu hipotezler de Faz 1'de trend/momentum stratejilerinin (C07, R01) iyi çıktığını bildiğimiz halde seçildi. Bu yüzden ABD/emtia'da asıl sınav kilitli dönemdir; OOS sonucu iyimser kabul edilir. Kriptoda 4H/1D trend kartları Faz 1'de test edilmedi.

## 2. Evren
- **Kripto:** U1 ile aynı 14 coin (Binance spot, USDT).
  - Çekirdek 6: BTC, ETH, SOL, BNB, XRP, TRX.
  - Kardeş 8: ADA, DOGE, LTC, LINK, DOT, AVAX, BCH, NEAR. Yalnız doğrulama için; kardeş ölçütleri U1 ile aynı.
  - 4H barlar 1H veriden yeniden örneklenir (UTC 00/04/08/12/16/20). 1D, Binance günlük bar (UTC 00:00).
- **ABD:** `ABD25`, tarihsel üyelikle (`data/evren_pit.py`, survivorship düzeltmesi).
- **Emtia:** `EMTIA` (6 ETF: GLD, SLV, USO, UNG, DBA, CPER).
- Coin ya da hisse eklenmez, çıkarılmaz.

## 3. Maliyet ve boyut
- Tek yön maliyet (komisyon + kayma):
  - kripto **%0,15**;
  - ABD **%0,05**;
  - emtia ETF **%0,05**.

  `tarama.BASE_COST` ile aynı. Stres: 2x ve 3x.
- Boyut `docs/EVRENSEL_KURALLAR.md` ile aynı: işlem başı risk %0,5, toplam açık risk %2, kitap brütü %100, kaldıraç yok.
- Sinyal bar kapanışında, dolum sonraki barın açılışında. Aynı barda stop ve hedef birlikte değerse önce stop sayılır.
- Her varyant bir havuz portföyüdür: kripto 14 coin, ABD 25 hisse, emtia 6 ETF.

## 4. Hipotezler (4 kart × 4 kol = 16 deneme)
Parametreler literatürdeki yaygın değerlerdir ve **sabittir**; ızgara yoktur. Her kart dört kolda aynı kuralla koşar: **kripto 4H, kripto 1D, ABD 1D, emtia 1D.** Bar sayıları o kolun barıdır (4H'de 100 bar ≈ 17 gün, 1D'de 100 gün).

Bütün kartlarda koruma stopu girişte **ATR(14) × 3**'tür. H2'nin kendi stopu vardır (ATR(20) × 2).

| Kart | Mekanizma ve kaynak | Giriş (bar kapanışı) | Çıkış |
|---|---|---|---|
| `U4-H1` | Zaman serisi momentumu / trend takibi (Moskowitz, Ooi, Pedersen 2012; kripto: Liu & Tsyvinski 2021) | `close > sma(close, 100)` **ve** `close > close[100]` (100 bar getirisi > 0) | `close < sma(close, 100)` ya da stop |
| `U4-H2` | Donchian kırılımı (Turtle sistemi 2; Faith 2007) | `close > highest(high, 55)` (önceki 55 bar, `kaydir: 1`) | `close < lowest(low, 20)` (önceki 20 bar, `kaydir: 1`) ya da stop **ATR(20) × 2** |
| `U4-H3` | Düşük volatilite rejiminde trend (volatilite kümelenmesi; Moreira & Muir 2017) | `ema(close, 20) > ema(close, 50)` **ve** `close > sma(close, 200)` **ve** `atr(14) / atr(100) < 1` | `ema(close, 20) < ema(close, 50)` ya da stop |
| `U4-H4` | Yükselen trendde kısa geri çekilme (Connors RSI(2)) | `close > sma(close, 200)` **ve** `rsi(close, 2) < 10` | `close > sma(close, 5)` ya da **zaman stopu 10 bar** ya da stop |

- Pozisyondayken aynı sembolde yeni giriş yok (piramit yok).
- Deneme sayısı **16**. DSR bu sayıyla hesaplanır. Ek deneme ancak lider kararıyla `results/u4/deneme_kaydi.csv`'ye yazılarak yapılır ve DSR'ye eklenir.

## 5. Geçme kapıları (Faz 1 ve U1 ile aynı huni)
1. **Aşama 1 (IS):** maliyet sonrası PF > 1. İşlem sayısı ≥ 30 (havuz). Swing paper eşiği ≥ 60 işlem ayrıca raporlanır.
2. **Aşama 2a (IS):** rastgele giriş testi. Aynı işlem sayısı ve tutma süresi, aynı çıkışlar, tekrar sayısı U1 ile aynı (200; sınırda p 0,03-0,10 için 1000). PF ve ortalama R p < 0,05.
3. **Aşama 2b (OOS):**
   - ortalama R > 0;
   - 2x maliyette PF ≥ 1,2;
   - 3x maliyette net > 0;
   - +1 bar gecikmeyle net > 0;
   - block bootstrap MDD95 ≤ %15;
   - DSR (N=16) > 0,95;
   - en iyi ay çıkarılınca PF > 1.
4. **Kripto kardeş ölçütü (U1 ile aynı):**
   - kardeşlerin ≥ %60'ında PF > 1,1;
   - tek coin kârın ≤ %35'i.
5. **ABD/emtia ön dönem:** 2015-2017 net getiri işareti raporlanır. Negatifse aday Koşullu olur.
6. **Karar:** Geçti / Koşullu / Reddedildi. Neden yazılır.

## 6. İş bölümü
### A. Sonnet: kartlar (`docs/spec/U4-H1..H4.yaml`)
- Dört kart, bölüm 4'teki kurallarla **birebir**.
  - `tf` alanı kart varyantında kol tarafından belirlenir.
  - `piyasa_kisiti: [KRIPTO, ABD, EMTIA]`.
  - `deneme_sayisi_kaynakta: 4`.
  - Kripto kolları için `cekirdek` ve `kardesler` listeleri U1 ile aynı.
- Belirsizlikler `belirsiz:` alanına yazılır, uydurulmaz. Örnekler: `close[100]` gösterimi; 4H'de zaman stopu 10 bar = 40 saat.
- `python -m engine.spec --kontrol docs/spec/` hatasız olmalı.
- Her kart için **ileriye bakma testi** (`tests/test_u4_kartlar.py`): sentetik seride bar t'deki sinyal, t+1 ve sonrası değiştirilince değişmemeli. Ayrıca her kartın giriş/çıkış koşulunu elle hesaplanmış küçük bir örnekle doğrulayan birim test.
- Teslim: PR `[U4] kartlar`. Backtest koşulmaz.

### B. Codex: koşucu ve gerçek koşu (`backtests/u4.py`, `backtests/u4_huni.py`)
- `u1.py` / `u1_huni.py` örnek alınır:
  - 4 kol × 4 kart = 16 varyant;
  - dönemler ve kilit bölüm 1'deki gibi;
  - maliyet ve boyut bölüm 3'teki gibi;
  - kapılar bölüm 5'teki gibi.
- Kod önce sentetik veriyle testlenir. Sonra gerçek koşu:
  - kripto 1h verisi Binance (`data/fetch.py --interval 1h`), 1d günlük;
  - ABD/emtia yfinance günlük.
- Çıktı: `results/u4/` (özetler, `huni_ozet.csv/.md`, kardeş raporları). **İşlem dökümleri commit edilmez** (`.gitignore`).
- Sonnet'in kart PR'ı birleşmeden gerçek koşu yapılmaz. Kod geliştirmesi paralel yürüyebilir.
- Yasaklar (U1c ile aynı):
  - `KILIT_AC` tanımlanmaz;
  - kart, kural, eşik, dönem değiştirilmez;
  - hata bulunursa sessizce düzeltilmez, PR'da raporlanır;
  - sonuca bakıp yeni varyant denenmez.
- Teslim: PR `[U4] koşucu + huni`, açıklamada 16 satırlık `huni_ozet.md` kopyası.

### C. Lider
- Kart ve koşucu PR'larını denetler.
- Örnek bir varyantı kendisi tekrar koşar.
- `results/U4_SONUC.md`'yi yazar.

## 7. Beklenti (sonuçtan önce, dürüstçe)
- Trend kartları (H1-H3) düşük isabet, yüksek kazanç/kayıp oranı verir. Kriptoda en olası aday bunlardır.
- H4 (geri çekilme) ABD'de belgelenmiş bir etki. Kriptoda zayıf olabilir.
- Paper'daki risk ayarıyla (%0,5/işlem) yıllık getiri düşük kalır (Faz 1 portföyü yılda ~%4). %20-30 hedefi ancak birden çok düşük korelasyonlu aday ve risk/ağırlık kararıyla mümkündür. Bu karar sonuçlardan sonra ayrıca konuşulur.
