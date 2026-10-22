# T28 — PR kontrol iş akışı (CI) (sahibi: codex-worker; önerilen model: **Terra**; küçük iş)

## Neden
Bugün iki regresyonu lider elle yakaladı. T17 sonrası `asama2b` Codex satırları çöküyordu. T24'te ise `--kart-ids` ile koşulmayan satırlar siliniyordu. Lider her PR'da aynı kontrolü elle yapıyor: pytest, ardından main ile PR'ı aynı gerçek veride koşup karşılaştırmak. Bu iş otomatik olmalı.

## İstenenler
`.github/workflows/ci.yml`, `pull_request` (base `main`) tetikleyicisiyle iki iş içerir.

1. **`test`:** `pip install -r requirements.txt`, TA-Lib kurulumu (gerekiyorsa mevcut iş akışlarındaki yöntemle), `python -m pytest -q` ve `python -m engine.spec --kontrol docs/spec/`.
2. **`parite`** (main ile PR, **aynı veriyle**):
   - Günlük veriyi bir kez indir (ABD25 + BIST30 + USDTRY; `data/fetch.py --interval 1d --allow-partial`). Veriyi iki checkout'a da ver: `actions/checkout` ile `pr/` ve `main/` dizinleri.
   - İki checkout'ta da şunu koş: `backtests/tarama.py --kart-ids C01,C09,G011,M015,C07,R01 --results-dir <geçici>`.
   - `tarama_islemler/` birebir aynı olmalı. `tarama.csv` için `git_sha` ve `data_hash` dışındaki sütunlar aynı olmalı.
   - İki checkout'ta da şunu koş: `backtests/asama2b.py --kart-ids R01 --codex-ids C07 --null-tekrar 200 --bootstrap-tekrar 200`. Önce sonuç dosyalarını (`tarama.csv`, `asama2a.csv`, `asama2b.csv`, varsa `tarama_rotasyon.csv`) geçici dizine kopyala.
   - `asama2b.csv`'de R01 ve C07 satırları karşılaştırılır (`git_sha`/`data_hash` hariç); ayrıca toplam satır sayısı korunmalı. PR yeni sütun eklediyse yalnız ortak sütunlar karşılaştırılır.
   - Fark varsa iş kırmızı olur ve farkı özetler (hangi dosya, hangi sütun).
   - Karşılaştırmayı küçük bir betik yap: `backtests/ci_parite.py`. Bu betiğin birim testi sentetik CSV'lerle yazılır: fark yakalama ve yeni sütun toleransı.
3. **Bilinçli fark:** PR gövdesinde `[parite-farki-bekleniyor]` etiketi varsa `parite` işi uyarı verir ama başarısız olmaz. Motoru bilerek değiştiren PR'lar için.
4. Süre hedefi: toplam 20 dakikadan az. Pip önbelleği kullan.

Kapsam dışı: diğer iş akışlarına dokunma.

Teslim: Tek PR (base `main`). Kendi PR'ında CI'nın çalıştığını göster.
