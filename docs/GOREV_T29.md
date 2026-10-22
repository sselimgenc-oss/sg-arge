# T29 — Uçtan uca huni iş akışı (sahibi: codex-worker; önerilen model: **Terra**; küçük/orta iş)

## Neden
Nihai liste (`results/SONUC.md`) şu an lider ortamında elle, adım adım üretiliyor: tarama → 2a → 2b (sabit) → 2b (PIT) → portföy → sonuç raporu. Bu sıra hem hataya açık (bugün iki satır silme hatası yakalandı) hem tekrarlanamaz. Ayrıca mevcut `tarama.yml`, `asama2a.yml`, `asama2b.yml` ve `portfoy.yml` sonuçları **doğrudan main'e push** ediyor. Bu yüzden T28'de kurulan PR kontrolünden geçmiyorlar.

## İstenenler
1. **`.github/workflows/huni.yml`:** yalnız `workflow_dispatch` ile tetiklenir. Girdiler:
   - `kartlar` (boş = hepsi)
   - `tf` (varsayılan `1D,1W`)
   - `null_tekrar` (200)
   - `bootstrap_tekrar` (1000)
   - `evren_pit` (true)
2. **Sıra** (her adım bir öncekinin sonuç dosyalarını kullanır):
   1. Veri indirme, bir kez yapılır: günlük piyasalar, rotasyon ETF'leri, USDTRY ve PIT ek sembolleri. Ayrı bir iş olarak çalışır ve sonucu `actions/upload-artifact` ile paylaşılır.
   2. `tarama.py --birlestir`; varsa rotasyon kartları `tarama_rotasyon.csv`'ye yazılır.
   3. `asama2a.py`
   4. `asama2b.py` (sabit evren)
   5. `asama2b.py --evren pit`; çıktı `asama2b_pit.csv`. Mevcut adlandırma neyse ona uy.
   6. `portfoy.py`
   7. `sonuc_raporu.py`

   GitHub'ın 6 saatlik iş sınırına takılmamak için adımları ayrı işlere böl. Sonuç dosyaları işler arasında artifact olarak taşınır.
3. **Main'e doğrudan push yok.** Son adım sonuçları `huni/<run_id>` dalına commit eder ve main'e **PR açar**. `GITHUB_TOKEN` yeterliyse onu kullan; `permissions: contents: write, pull-requests: write`. PR gövdesinde şunlar yer alır: özet sayılar (SONUC.md'deki tablo), çalışma süresi, `git_sha`. Böylece T28 kontrolü sonuçlardan da geçer.
4. **Mevcut 4 iş akışı** (`tarama`, `asama2a`, `asama2b`, `portfoy`): "commit + push main" adımını aynı "dal + PR" yöntemine çevir. Başka davranışı değiştirme.
5. **Test:** İş akışı YAML'larını `actionlint` ile denetle (CI'ya ekleme zorunlu değil; PR'da çıktısını göster). Küçük bir kartla (ör. `kartlar: C01`) `huni.yml`'yi kendi dalında **bir kez çalıştır** ve çalışma bağlantısını PR'a koy.

Kapsam dışı: backtest koduna dokunma.

Teslim: Tek PR (base `main`).
