# T23 — Rotasyon kartlarını Aşama 2a/2b ve portföye bağla (sahibi: claude-moderator / Sonnet)

## Neden
T22 (PR #80) birleşti. Lider gerçek veriyle taradı. 13 rotasyon kartından **12 satır Aşama 2 adayı** çıktı:

| Kart | Piyasa | İşlem | PF 1x | PF 2x | MDD |
|---|---|---:|---:|---:|---:|
| A4-002 | ABD | 32 | 2,62 | 2,56 | %82 |
| A4-003 | ABD | 67 | 2,56 | 2,37 | %23 |
| A4-005 | ABD | 49 | 7,02 | 5,42 | %15 |
| A6-004 | ABD | 543 | 1,84 | 1,68 | %8 |
| A6-004 | KRİPTO | 354 | 1,34 | 1,26 | %41 |
| B3-014 | BIST | 645 | 1,25 | 1,14 | %47 |
| B3-014 | ABD | 619 | 1,17 | 1,11 | %41 |
| M017 | ABD | 969 | 1,57 | 1,33 | %12 |
| M020a | ABD | 64 | 2,76 | 2,70 | %31 |
| M020a | KRİPTO | 58 | 1,26 | 1,25 | %69 |
| O2-025 | ABD | 118 | 2,29 | 2,21 | %48 |
| O2-027 | ABD | 125 | 2,62 | 2,49 | %54 |

Şu an `asama2a.py`, `asama2b.py` ve `portfoy.py` bu kartları `MotorDestegiYok: rotasyon_asama2` ile atlıyor. T23 bu boşluğu kapatır. **Eleme kriterleri gevşetilmez:** günlük kartlarla aynı kapılar uygulanır.

## İstenenler
1. **Aşama 2a: null modeli.** Gerçek kartla aynı takvim, aynı N, aynı maliyet ve aynı yürütme kullanılır. Yalnız **seçim rastgele** olur.
   - `kesitsel` ve `sirali_giris`: Skor yerine her dengelemede rastgele sıralama kullan. Filtre ve rejim kapısı aynen kalır, çünkü bunlar seçim değil koşul. Böylece null'u yenmek "sıralamada beceri" demek olur.
   - `gecis`: Ağacın karar tarihlerinde, ağacın yapraklarındaki enstrümanlardan biri rastgele seçilir (eşit olasılık). Geçiş tarihleri gerçek stratejiyle aynıdır.
   - En az 200 tekrar; sınırda kalan için 1000.
   - **Karar:** PF_1x **ve** net getiri (CAGR), null'un %95'lik değerinin üstünde olmalı. Rotasyonda işlem başına stop olmadığı için ortalama R yerine CAGR kullanılır. Bunu kodda ve `asama2a` çıktısında açıkça belirt (`metrik: PF+CAGR`).
2. **Aşama 2b.** Günlük kartlarla aynı kapılar:
   - OOS (2024-10-01 sonrası);
   - ön dönem (2015-2019; veri yoksa `Dogrulanamaz`);
   - stres: maliyet 2x/3x ve dolumu +1 bar geciktirme;
   - plato: `rotasyon:` bloğundaki her sayısal parametre (pencere, eşik, N) tek tek ±%20. Tamsayılar yuvarlanır. Composer ağaçlarında her eşik ayrı ayrı oynatılır; PF>1 kalan oran raporlanır;
   - 20 günlük block bootstrap, **MDD95 ≤ %15**;
   - DSR.

   Karar kuralları `decide()` ile aynı (Gecti/Kosullu/Reddedildi). İşlem başına R gerektiren kapılar varsa CAGR karşılığını kullan ve gerekçeyi yaz.
3. **Composer kartları (D4 MOC istisnası):** Aşama 2'de **ertesi açılış dolumu** esas alınır. Kapanış dolumu (2x maliyet) yalnız bilgi sütunu olarak kalır.
4. **PIT:** `--evren pit` kesitsel kartlarda (B3-014, M020a, A6-004) seçimi PIT üyeliğine bağlar. Sentetik bir üyelik tablosuyla test ekle: üyelikten çıkmış sembol seçilmemeli.
5. **Portföy:** `portfoy.py` rotasyon satırlarını da aday olarak kabul etsin. Getiri serisi rotasyon modülünden gelir.
6. **Testler:**
   - Null'un seçim dışında her şeyi koruduğunu gösteren test: takvim, N, maliyet.
   - Kesilmiş seride look-ahead testi.
   - Mevcut `results/asama2a.csv` ve `results/asama2b.csv` sonuçlarında günlük kartlar birebir aynı kalmalı (regresyon).
7. **Performans:** Ölçülen süreyi PR'a yaz.

## Kararlar (lider)
- **A6-021:** `sadece_short` kalır. EVRENSEL_KURALLAR madde 5 gereği short fazına ertelendi; ayrı long bacak kodlanmaz.
- **Evren yoğunluğu:** `n_oran` kabul edildi (0,10 / 0,02, en az 3).
- **A4-001:** kodlanmaz (228 düğüm, 52 ETF). `ozel_kod` kalır.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. Gerçek koşuyu lider yapar; gerçek sonuç dosyası üretme.
