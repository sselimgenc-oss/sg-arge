# T32 — Eksik zaman dilimleri ve tek enstrüman piyasaları (sahibi: codex-worker; önerilen model: **Terra**)

## Neden
Doğrulanamaz ve Bekliyor durumundaki kartların bir bölümü kural eksikliğinden değil, **altyapı eksikliğinden** test edilemiyor (lider sayımı, `docs/spec/*.yaml`):

- **Zaman dilimi küçük harfle yazılmış (11 kart):**
  - `1h`: O2-003, O2-018, O2-021a/b/c, A2-024, A2-028, A2-029
  - `4h`: A2-027, O1-040, O1-043

  Motor `1H` ve `4H` bekliyor, bu yazım tanınmıyor.
- **2H/4H desteklenmiyor (10 kart):**
  - `4H`: M013, M044, M046, M048, M049, G004, O3-034, A1-010, A3-002g
  - `2H`: A3-002e
- **Piyasa yok (`piyasa_kisiti`, ~60 kart):**
  - FX (17), GER40 (14), ES (6), NQ (6), FR40 (4)
  - US100 (3), XAUUSD (3)
  - JP225, US30, CL, GC (birer)

  Bu piyasaların hepsinin ücretsiz verisi var (yfinance).

Kapsam dışı (yapma):
- 10s/tick/range (`10s`, `2r`, `10r`, `512t`);
- 45m/10m/4m;
- NSE.

## İki PR, sırayla
Limit erken biterse ilk PR tek başına birleştirilebilir olmalı.

### PR-1: Zaman dilimi
1. **Normalizasyon:** kart yüklenirken `tf` büyük harfe çevrilir (`1h`→`1H`, `4h`→`4H`). `engine.spec --kontrol` geçersiz `tf` için uyarı versin. YAML dosyalarını da düzelt (yalnız `tf:` satırı).
2. **2H/4H yeniden örnekleme:** 1H arşivinden türet; ayrı indirme yok.
   - **Kripto (Binance 1h):** UTC 00:00'a hizalı 2H/4H mumlar.
   - **ABD/EMTIA (yfinance 1h, ~2 yıl):** seans açılışına (09:30 ET) hizalı mumlar. Seans sonundaki kısa son mum korunur.
   - **BIST:** 1H kalite kapısı kapalı, kapsam dışı.
   - OHLCV birleştirme kuralı: `open`=ilk, `high`=maks, `low`=min, `close`=son, `volume`=toplam. Mum, kapanış zamanında kapanmış sayılır; look-ahead olmamalı.
   - Kuralı `docs/EVRENSEL_KURALLAR.md`'ye **D16** olarak yaz.
3. **Tarama entegrasyonu:**
   - `tarama.py`, `asama2a.py`, `asama2b.py`: `--tf 2H,4H` desteklenir.
   - `annualization_for` 2H/4H için doğru bar sayısını verir (kripto 7/24; ABD seans).
   - IS/OOS bölmesi 1H ile aynı kuralı kullanır: kripto takvim tarihleri, yfinance ilk 2/3.
4. **Testler:**
   - sentetik 1H → 4H birleştirme (hizalama, kısmi son mum);
   - sinyalin yalnız kapanmış mumla üretildiğini doğrulayan look-ahead testi;
   - `1h` kartın yüklendiğini gösteren test.

### PR-2: Tek enstrüman piyasaları
1. **Veri (`data/fetch.py`, yeni `--piyasa ENSTRUMAN` ya da benzeri):** yfinance günlük (2015+) ve 1H (730 gün).

   | Kod | Sembol |
   |---|---|
   | FX | EURUSD=X, GBPUSD=X, USDJPY=X, GBPJPY=X, AUDUSD=X, USDCHF=X, USDCAD=X, EURJPY=X |
   | GER40 | ^GDAXI |
   | FR40 | ^FCHI |
   | US100 ve NQ | ^NDX |
   | ES | ^GSPC |
   | US30 | ^DJI |
   | JP225 | ^N225 |
   | XAUUSD ve GC | GC=F |
   | CL | CL=F |

   Hacmi olmayan seriler (FX, endeks) için hacim 0 olabilir. Hacim kullanan göstergeler `veri_yok` ile atlanmalı, çökmemeli.
2. **Piyasa tanımı:** Kartın `piyasa_kisiti` kodu kendi enstrüman sepetine eşlenir. FX kartı FX sepetinde, GER40 kartı yalnız ^GDAXI'de koşar. Bu satırlar mevcut 4 piyasaya (ABD25/BIST30/KRIPTO25/EMTIA) eklenen yeni satırlardır; mevcut satırlar değişmez.
   - Evren `enstruman` (survivorship yok, D12'deki gibi).
   - Benchmark yok (beta testi 2a null'u ile yapılıyor).
3. **Maliyet (taraf başı, `BASE_COST`):**
   - FX %0.01
   - endeks %0.02
   - altın/petrol %0.03

   2x/3x stres mevcut kuralla uygulanır.
4. **Testler:** sentetik FX verisiyle hacimsiz seri; `piyasa_kisiti` eşlemesi; mevcut piyasaların satırlarının değişmediği.

## Parite (zorunlu, iki PR için de)
- CI `parite` işi yeşil olmalı. Mevcut kartlar ve piyasalar birebir aynı kalır.
- Yeni satırlar eklenir, var olanlar değişmez.
- `[parite-farki-bekleniyor]` etiketi **kullanma**. Fark çıkarsa bu bir hatadır.

Kapsam dışı: strateji kuralları, eleme kapıları, sonuç dosyaları. Huniyi lider koşar.

Teslim: PR-1 ve PR-2 ayrı (base `main`). Her PR gövdesinde etkilenen kart listesi ve pytest çıktısı yer alır.
