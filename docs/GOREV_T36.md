# T36: T35 kısa listesinin testi (Faz 1 hunisiyle)

Karar: kullanıcı, lider önerisi (b) ile kabul etti (2026-10-23). Kaynak: `tartisma/011_t35_parti2_degerlendirme.md`, "Lider kısa listesi".
Amaç: yazar beyanıyla toplanan 10 adayı **kendi motorumuzda**, Faz 1'in evrensel kuralları ve hunisiyle (Aşama 1 → 2a null → 2b) yeniden üretmek. Her strateji **yazarın kendi piyasasında** test edilir.

## 1. Veri durumu: hangi aday test edilebilir
| # | id | Piyasa / TF | Ücretsiz veri | Durum |
|---|---|---|---|---|
| 1 | JP-005 | USDJPY 5 dk, 2010→ | Dukascopy 1 dk (2003→) | **Test edilecek.** Alan adı izni gerekiyor |
| 3 | JP-004 | USDJPY 1 dk, 2020→ | Dukascopy | **Test edilecek.** Alan adı izni gerekiyor |
| 6 | US-009 | NQ overnight | Dukascopy USATECHIDXUSD (Nasdaq-100 CFD, 1 dk) | **Test edilecek (vekil).** CFD, Globex vadeli değil; şerh: `vekil_enstruman` |
| — | US-006 | NQ ORB 09:30-09:45 | Dukascopy USATECHIDXUSD | Test edilecek (vekil). Kural kısmi; kart yazılabilirse |
| — | TH-001 | USDCHF 30 dk | Dukascopy | Kural kısmi (Fib swing tanımı); kart yazılabilirse |
| 9 | IN-004 | SBIN 1 saat, 2016→ | yfinance 1h yalnız ~730 gün | Kısmi test → en fazla **Koşullu** |
| 8 | SA-003 | ITUB4 120 dk, 2013→ | yfinance 1h ~730 gün (2H yeniden örnekleme) | Kısmi test → en fazla **Koşullu** |
| 2,4,5 | CN-007a, CN-008b, CN-001 | Çin endeks/vadeli 1 dk | Ücretsiz uzun dakikalık veri yok (JoinQuant/RiceQuant hesap ister; bu ortamdan erişim yok) | **Doğrulanamaz (veri).** Kullanıcı hesap açarsa yeniden ele alınır |
| 7 | IN-002 | Nifty 15 dk, 2017→ | yfinance 15m yalnız 60 gün | **Doğrulanamaz (veri)** |
| 10 | SA-006 | WDO 15 dk | Ücretsiz B3 vadeli dakikalık yok | **Doğrulanamaz (veri)** |

**Kullanıcı ayarı (tek seferlik):** Bulut ortamının ağ ayarında Allowed domains'e `datafeed.dukascopy.com` eklenmeli. Adımlar: https://code.claude.com/docs/en/cloud-environments#network-access
Eklenmezse B planı: veri GitHub Actions'ta (açık internet) çekilir ve repoya Parquet olarak yazılır (`.github/workflows/dukascopy.yml`).

## 2. İşler
### T36a: Veri (Sonnet; Codex ortamı açılırsa Codex). Taslak: `data/dukascopy.py` (lider, test edilmedi)
- `data/dukascopy.py`: bi5 (LZMA) tick/1 dk mum indirici, UTC, bid/ask ortası. Spread bilgisi ayrıca saklanır (maliyet modeli için).
- Semboller: USDJPY, USDCHF (2010→); USATECHIDXUSD (mevcut ilk tarih→).
- Depolama: `data/dakika/<sembol>/<yil>.parquet` (1 dk). Repo boyutu için yalnız 1 dk; 5 dk/30 dk yeniden örneklenir.
- Kalite raporu `results/veri_kalitesi_dukascopy.md`: boşluk, hafta sonu, spread dağılımı.

### T36b: Motor (Sonnet; Codex ortamı açılırsa Codex)
1. **Short desteği** (`yon: long | short | iki`): stop/hedef/iz süren aynalanır. A3 kötümser sıra korunur. Rastgele giriş testi yönü korur. Long-only sonuçlar değişmemeli (CI paritesi).
2. **Gün içi FX/CFD maliyet modeli:** `FXDK` piyasası (dakikalık FX/CFD). Maliyet = Dukascopy'den ölçülen medyan spread (pip) + 0,2 pip kayma; 2x/3x stres. Baz tablo `docs/ELEME_KRITERLERI.md`'ye lider ekler.
3. **Yerel saat ilkeli:** `saat_yerel("Asia/Tokyo")`, `dakika_yerel(...)`. Gotobi (ayın 5/10/15/20/25 ve son iş günü) için `ay_gunu()` zaten var; "son iş günü" ilkeli eklenir.
4. **Seans sonu kapatma:** `seans_sonu_kapat: "HH:MM tz"`.
5. Testler + CI paritesi (Faz 1 sonuçları birebir aynı kalmalı).

### T36c: Kartlar (Sonnet; note.com API erişimi var)
`docs/spec/T35-<id>.yaml` kartları, uydurma yok. Kaynakta olmayan parametre `belirsiz`'e yazılır. Öncelik: JP-005, JP-004, US-009, IN-004, SA-003; sonra US-006, TH-001.
Kart için kaynak metin gerekiyor: lider oturumu note.com / stsfutures / quantbrasil'i açamıyor. Kural metinleri T35 kayıtlarından (`orijinal_alinti`, `giris/cikis/stop`) alınır; eksikse Sonnet (note.com API erişimi var) kaynaktan tamamlar.

### T36d: Huni (lider)
Aşama 1 (maliyet, ≥30 işlem) → 2a (rastgele giriş, yön korunarak) → 2b (OOS, 2x/3x maliyet, +1 bar gecikme, plato, bootstrap MDD) → `results/T36_SONUC.md`.
Dönemler: FX/CFD dakikalık için IS 2010-2019, OOS 2020→ (JP-004 için yazarın dönemi 2020→ olduğundan IS 2020-2023, OOS 2024→; ön dönem 2010-2019 "gerçek OOS" olarak ayrıca koşulur).

## 3. Sıra
1. Kullanıcı: alan adı izni.
2. Sonnet sırayla: T36b (motor) → T36a (veri: taslağı tamamla, testleri yaz, ağ izni varsa indir; yoksa `.github/workflows/dukascopy.yml` ile Actions'ta indir) → T36c (kartlar). Codex ortamı açılırsa T36a'yı o alır.
3. Lider: her PR'ı denetler; T36d (huni koşusu ve sonuç raporu).

**Token tasarrufu (kullanıcı kararı, 2026-10-23):** Lider kod/veri işi yapmaz; yalnız görev, denetim, karar ve sonuç raporu.
