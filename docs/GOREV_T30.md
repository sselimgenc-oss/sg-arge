# T30 — Gün içi tarama ve Aşama 2'de bellek/hız (sahibi: claude-moderator / Sonnet)

## Neden
5m kripto verisi sembol başına yaklaşık 570-715 bin bar, toplam 25 sembol. Lider ortamında (16 GB) `tarama.py --tf 5m` 15 kartlık bir grupta **iki kez bellek yetersizliğinden öldü** (OOM, `Killed`). Gruplar 3 karta indirildiğinde bile tek bir grup 30 dakikadan uzun sürüyor (ör. A3-001, A3-002d, A3-002f). GitHub Actions makinesinin belleği **7 GB**. Bu sorun çözülmeden gün içi huni (`huni.yml`, T29) Actions'ta koşamaz.

## İstenenler
1. **Ölç.** Sorunlu kartlarda zirve bellek ve süreyi ölç: A1-009, A3-001, A3-002d, A3-002f, A3-010a, A3-010b, A3-010c (5m, KRIPTO25). `tracemalloc` ya da `/usr/bin/time -v` kullan. Bellek nerede şişiyor? Adaylar:
   - tüm sembollerin tüm göstergelerinin aynı anda tutulması;
   - float64 kopyaları;
   - `plan.signals` DataFrame'leri;
   - `equity_points` sözlükleri;
   - pandas ara nesneleri.

   Bulguyu PR'a tablo olarak yaz.
2. **Düzelt (davranış değişmeden):**
   - kart başına iş bittikçe belleği bırak;
   - göstergeleri sembol sembol hesapla, gereksiz kopyaları kaldır;
   - sinyal dizilerini bool/float32 tut. Fiyat ve özkaynak hesapları float64 kalmalı, sonuç birebir aynı olmalı;
   - `trades_only` yolunu taramada da kullan, eğer metrikler işlem listesinden türetilebiliyorsa.

   Hedef: tek kart × 25 sembol × 5m için **zirve bellek < 4 GB** ve kart başına **< 5 dk**.
3. **Aşama 2a/2b gün içi:** Aynı hedef geçerli; `--isci` işçi sayısı belleğe göre otomatik sınırlanmalı (ör. `min(cpu, bos_bellek / kart_zirvesi)`). `asama2a.py --tf 5m` ve `asama2b.py --tf 5m` tek aday için 7 GB'ta koşabilmeli.
4. **Parite (zorunlu):**
   - Günlük: C01/C09/G011/M015/C07/R01 tarama işlemleri ve R01/C07 asama2b birebir aynı kalmalı. CI (`ci.yml`) bunu zaten kontrol ediyor.
   - Gün içi: değişiklikten önce ve sonra 3 kartın (5m ve 15m) `tarama_islemler` çıktısı birebir aynı olmalı. Veriyi kendin indir (`data/fetch.py --interval 5m --baslangic 2020-01-01`); gerekirse 3-5 sembolle sınırla, ama bellek ölçümünü tam 25 sembolle yap.
5. **Testler:** bellek tavanını sentetik büyük veride doğrulayan bir test yaz (ör. 200 bin bar × 5 sembol; `tracemalloc` zirvesi eşik altında). Ayrıca birebir eşitlik testi.

Kapsam dışı: strateji kurallarına, eleme kapılarına ve sonuç dosyalarına dokunma.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. Ölçüm tablosu (önce/sonra: bellek, süre) PR gövdesinde olsun.
