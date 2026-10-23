# T34 — Kullanıcının 5 enstrümanı × 5 zaman dilimi (sahibi: claude-moderator / Sonnet)

## Neden
Kullanıcı yalnız kendi işlem yaptığı 5 enstrümanda sonuç istiyor:

| Kod | Enstrüman | Kaynak sembolü |
|---|---|---|
| XU030 | BIST 30 endeksi | yfinance `XU030.IS` |
| SPX | S&P 500 | yfinance `^GSPC` |
| XAUUSD | Altın | yfinance `GC=F` |
| UKOIL | Brent | yfinance `BZ=F` |
| BTCUSDT | Bitcoin | Binance `BTCUSDT` |

Zaman dilimleri: 1D, 4H, 1H, 15m, 5m. Kartın kendi piyasa kısıtı ve kendi zaman dilimi **yok sayılır**; her test edilebilir kart her enstrüman × zaman dilimi hücresinde denenir.

## Ön kayıt (değiştirilmez)
1. **Kart havuzu:** `spec_durumu` değeri `tam` ya da `dakikalik` olan, `ozel_kod` olmayan kartlar. Bunlara modülü olan özel kartlar (A1-027) ve rotasyon olmayan kartlar dahildir. Rotasyon ve çok enstrümanlı kartlar hariç tutulur.
2. **Zaman dilimi değiştirme:** Kart parametreleri **bar cinsinden aynen** kullanılır. Örneğin günlükte 20 bar olan parametre 1H'de de 20 bar kalır. Her (kart, enstrüman, tf) hücresi ayrı bir denemedir.
3. **Veri ve dönem:**

   | Zaman dilimi | Enstrümanlar | Kaynak ve dönem |
   |---|---|---|
   | 1D | 5'i de | 2015+ veri; IS 2020-01 → 2024-09; OOS 2024-10+; ön dönem 2015–2019 |
   | 1H, 4H | BTC | Binance, 2017+; IS/OOS kripto kuralıyla |
   | 1H, 4H | diğer 4 | yfinance ~730 gün; ilk 2/3 IS, son 1/3 OOS; ön dönem yok |
   | 15m, 5m | yalnız BTC | Binance |
   | 15m, 5m | diğer 4 | **Bu turda yok.** Dukascopy ücretsiz dakikalık verisi ikinci tura bırakıldı; kullanıcı onayı gerekir. |

   XU030 1H/4H satırlarında BIST 1H kalite kapısı (`data/bist_1h.py`) uygulanır. Kapı kapalıysa satır Doğrulanamaz olur.
4. **Maliyet (taraf başı):**

   | Enstrüman | Maliyet | Gerekçe |
   |---|---|---|
   | BTCUSDT | %0,10 | Binance |
   | SPX | %0,02 | ES vadeli / ETF |
   | XAUUSD | %0,03 | |
   | UKOIL | %0,04 | |
   | XU030 | %0,04 | VİOP vadeli |

   2x/3x stres mevcut kuralla uygulanır.
5. **Huni:** Aşama 1 → 2a → 2b mevcut kodla, kapılar aynen uygulanır.
   - **DSR deneme sayısı N** = bu turda koşulan **tüm** hücrelerin sayısı. `asama2b` DSR'ına bu N verilir.
   - **Tek enstrüman** olduğu için `islem<30` kapısı aynen kalır.
6. **Sonuç dili:** Satırlar ana `SONUC`'a karışmaz. Çıktı `results/t34/` dizinine yazılır: `tarama.csv`, `asama2a.csv`, `asama2b.csv`, `RAPOR.md`.

## İstenenler
1. **Piyasalar.** `data/fetch.py` ve `run_codex21._symbols_for_market` içinde `SINGLE_MARKETS`'e (FX8 yapısı) beş tek enstrümanlı piyasa ekle: `XU030`, `SPX`, `XAUUSD`, `UKOIL`, `BTC`. Günlük ve 1H indirme yapılır. BTC 5m/15m mevcut Binance arşivinden alınır.
2. **Zaman dilimi zorlama.** `tarama.py`, `asama2a.py` ve `asama2b.py`'ye `--tf-zorla <tf>` ve `--piyasa-zorla <liste>` ekle.
   - Kartın `tf` ve `piyasa_kisiti` alanları yalnız bellekte geçersiz kılınır.
   - Satırın `tf` sütunu zorlanan tf'yi gösterir; yeni `kart_tf` sütunu kartın özgün tf'sini taşır.
   - Bu seçenekler verilmezse davranış birebir aynı kalmalı (CI parite yeşil).
3. **DSR N.** `asama2b.py --dsr-n <sayı>` ile deneme sayısı dışarıdan verilebilsin. Varsayılan davranış değişmez.
4. **Koşu.** Tüm hücreleri koş: tarama → 2a → 2b (1D satırlarında XU030/SPX için PIT gerekmez, çünkü tek enstrüman).
   - `results/t34/RAPOR.md` içinde şunlar yer alır:
     - enstrüman × tf tablosu: kaç kart denendi, kaçı Aşama 1/2a/2b'yi geçti;
     - geçenlerin listesi: IS/OOS getiri, MDD, işlem sayısı.
   - Rapor **dürüst ve sade Türkçe** olmalı.
5. **Testler.** Zorlama seçeneklerinin birim testi; tek enstrüman piyasası; seçenek yokken eski davranış.

## Kapsam dışı
- Kartların kurallarına ve eleme eşiklerine dokunma.
- Ana `results/SONUC.*` dosyalarına dokunma.
- Dukascopy ikinci turda yapılacak.

## Teslim
İki PR (base `main`):
1. Kod ve testler.
2. `results/t34/` sonuçları.

Kod PR'ı birleşmeden koşuya başlama.
