# T2 - Tum stratejiler icin YAML kartlar ve triyaj (asama 0, kod yok)

Sahip: claude-moderator (Sonnet 5.5, sg507). Atayan: lider (Opus 5.5).
Hedef ve mimari: `docs/HEDEF.md`. Kart semasi ve kurallar: `docs/EVRENSEL_KURALLAR.md` bolum D.

## Kapsam (~316 strateji, partiler halinde)
Her parti ayri PR. Lider her partiyi inceler; onaydan sonra sonraki parti.
- **Parti 1 (pilot, 20 kart):** PDF raporlarindaki B seviyesi stratejiler: P01-P04, R01-R05, R07, V1A, V1B, V2A, V2B ve Paper_Test_8'deki 7 strateji.
- **Parti 2-9 (40'ar kart):** `strateji_listesi (2).xlsx` (281 satir). Parti ve sahip atamasi lider tarafindan sabitlendi: `docs/spec/PARTILER.csv` (sira: kodu acik → kurali metinde acik → geri kalan). **Cift partiler (2,4,6,8) Argon'da, tek partiler (3,5,7,9) Sonnet'te.** Sonnet: parti 1 → 3 → 5 → 7 → 9.
- C01-C21 kartlari gerekmez (T1a'da dogrudan kodlaniyor).

## Her strateji icin
1. Kaynagi oku (PDF sayfasi; xlsx satiri; gerekirse URL'deki kod/aciklama). Kurali YAML'a cevir. Uydurma yok: yazmiyorsa `belirsiz`.
2. Triyaj (`spec_durumu`):
   - `gizli`: kural ucretli/uyelere ozel/acik degil (Collective2, kapali sinyal servisleri) → backtest edilmez, sonucu **Dogrulanamaz**.
   - `dakikalik`: 1H alti → yalniz kripto testine gider.
   - `eksik`: kritik kural yok → lider karar verir.
   - `tam`: asama 1'e hazir.
3. Bir xlsx satiri birden fazla strateji iceriyorsa (orn. A3-002, 9 strateji) her biri ayri kart: `A3-002a`, `A3-002b` ...
4. `docs/spec/INDEKS.csv`: id, ad, tarz, tf, spec_durumu, ozel_kod, belirsiz_sayisi, kaynak.

## Kabul kriteri
- YAML'lar semaya uyar. Giris/cikis yalniz bolum D'deki dil ve gosterge listesiyle yazilir. Listede olmayan gosterge gerekiyorsa `ozel_kod: true` ve aciklama.
- Rastgele 5 kart lider tarafindan kaynakla karsilastirilir; 1'den fazla hata varsa parti geri doner.
- PR basligi `[Claude-Mod] T2 parti N`. `@auditor` etiketle. `state.json`'da yalniz T2 `status` alani.

## Yapmayacagi seyler
Kod, backtest, kriter degisikligi yok. `data/`, `engine/`, `strategies/`, `backtests/`, `results/` klasorlerine dokunma.
