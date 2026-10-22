# T33 — Özel kod kartları (sahibi: codex-worker; önerilen model: **Sol**)

## Neden
Bu kartların kuralları kaynakta **tam**. Ancak genel kart dili (`engine/kart_sinyal.py`, YAML ifadeleri) ile yazılamıyorlar. Bu yüzden `ozel_kod: true` işaretli ve Doğrulanamaz kaldılar. Her biri için ayrı bir Python sinyal modülü yazılırsa standart huniden geçebilirler: tarama → 2a → 2b.

Lider sayımı: Doğrulanamaz 273 kartın 58'i bu gruptan ve kuralı tam. 11'inde formül tanımsız, 1'i ML, ~20'sinin verisi yok (DAX/NQ/ES, ABD dakikalık, FX 15m). Test edilebilir kalanlar aşağıdaki 15 kart.

## Kartlar (öncelik sırasıyla, partiler halinde)

| Parti | Kart | tf | Neden (`ozel_kod_nedeni`) | Piyasa |
|---|---|---|---|---|
| 1 | A1-027 | 1D | desen | tüm |
| 1 | A6-015 | 1D | desen | tüm |
| 1 | P3-010 | 1D | desen | tüm |
| 1 | M019 | 1D | durum_makinesi | tüm |
| 2 | A6-009 | 1D | ozel_gosterge | tüm |
| 2 | A6-014 | 1D | ozel_gosterge | tüm |
| 2 | R07 | 1D | durum_bilgisi | tüm |
| 2 | A4-001 | 1D | portfoy_rotasyonu | kartın kendi enstrümanları |
| 3 | A2-014 | 1H | bekleyen_emir | tüm |
| 3 | O1-048 | 1H | durum_makinesi | tüm |
| 3 | A2-003 | 1H | seans_saat | FX8 |
| 3 | O1-046 | 1H | desen | FX8 |
| 4 | A3-001 | 5m | durum_makinesi | KRIPTO25 |
| 4 | A3-002e | 2H | desen | KRIPTO25 (ve 1H piyasaları) |
| 4 | O1-050 | 15m | ozel_gosterge | KRIPTO25 |

Her parti ayrı bir PR'dır. Limit biterse bitmiş partiler tek başına birleştirilebilir olmalı.

## Kurallar
1. **Kaynak:** Kural `docs/spec/<ID>.yaml` içindeki metin, `kaynak.url` ve kartın notlarından alınır.
   - **Uydurma yok.** Kart bir eşiği, formülü ya da sırayı tanımlamıyorsa o kartı yazma. PR gövdesinde kart için `tanim_belirsiz: <neyin eksik olduğu>` notu düş.
   - Varsayım yapman gerekirse (ör. "dip" için pivot penceresi) kaynağın kendi örneğinden al, kodda yorum olarak belirt ve PR gövdesinde listele.
2. **Mimari:** `strategies/ozel/<ID>.py` (ya da mevcut `strategies/` düzenine uygun bir yer).
   - Her modül sembol başına standart sinyal çerçevesi döndürür: `entry`, `exit`, `stop_dist`/`target_dist` gibi alanlar, `kart_sinyal.card_frame_signals` çıktısıyla aynı sözleşmede.
   - `tarama.prepare`, `ozel_kod: true` olup modülü bulunan kartı bu modülle kurar. Böylece motor, maliyet, Aşama 2a/2b ve PIT aynı kalır.
   - Modülü olmayan `ozel_kod` kartlar eskisi gibi atlanır.
3. **Look-ahead yok:** Desenler yalnız kapanmış barlarla tanınır. Pivot/fraktal onayı sağ taraftaki N bar kapandıktan sonra gelir; sinyal o bara yazılır, desenin başladığı bara değil. Her modül için bir look-ahead testi yaz: geleceğe ait barları değiştirmek geçmiş sinyalleri değiştirmemeli.
4. **Kart başına birim testi:** Sentetik veride en az bir giriş ve bir çıkış üretildiğini göster.
5. **Parite:** CI `parite` yeşil olmalı. Mevcut kartların sonuçları birebir aynı kalır. `[parite-farki-bekleniyor]` etiketi kullanma.

Kapsam dışı: eleme kapıları, sonuç dosyaları. Huniyi lider koşar.

Teslim: Parti başına bir PR (base `main`). Gövdede şunlar yer alır:
- yazılan kartlar;
- yazılamayanlar ve nedenleri;
- yapılan varsayımlar;
- pytest çıktısı.
