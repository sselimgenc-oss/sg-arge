# TV-2: U5'te zaman dilimi yüzünden ayrılan 942 TradingView stratejisi

**Karar:** kullanıcı, 2026-10-24 (denetim K1: "Hepsi"). **Kaynak:** `arastirma/U5_tv.csv`, `suzgec_sonucu == elendi:tf_disi` (942) ve `elendi:tf_belirsiz` (60).
**Yöntem:** U6 ile aynı (`docs/GOREV_U6.md` bölüm 2 ve 5A; GOREV_U7 Ek 1 kol eşlemesi, Ek 4 motor alanları, Ek 5 huni). Yayın aralığı neyse o tf'de test edilir.

## Kol / veri
- Kripto: her tf (1m…1W) Binance'ten; 2H/6H/8H/12H 1H'den yeniden örneklenir.
- ABD/emtia/FX: 1D ve üstü yfinance; 1H-12H yfinance 1H (~2 yıl, Faz 1 1H dönem kuralı); 1H altı → Doğrulanamaz (veri) (denetim K8, Dukascopy kararı bekliyor).
- BIST → BIST30; diğer borsalar → ABD25 (GOREV_U7 Ek 1).

## Sıra (öncelik)
1. 1H-12H ve 1W/3D (~265), 2. `tf_belirsiz` (60), 3. 30m-45m (~59), 4. 15m ve altı (~600).

## İş bölümü
- Çeviri: Sonnet (limitine göre) ve Codex (U7'den sonra), 50'şerlik partiler, her parti ayrı PR `[TV-2] parti n`; ileriye bakma testi zorunlu.
- Koşu: Codex, `u6.py`/`u6_huni.py` ile; aile = TV-2 (DSR kendi N'i).
- Lider: her partiden 5 kartı Pine kaynağıyla karşılaştırır (denetim S1).
