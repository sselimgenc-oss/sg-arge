# T16 (Sonnet) ve T17 (Codex)

## T16 — `eksik` kart triyajı (sahibi: claude-moderator / Sonnet; kaynak okuma yok)

Kapsam: `spec_durumu: eksik` **ve** `ozel_kod: false` olan **47 kart** (`docs/spec/INDEKS.csv` filtresi).

Her kart için `belirsiz` listesini oku ve karar ver:

1. **`tam`'a terfi:** Eksik olan yalnız EVRENSEL_KURALLAR varsayılanlarıyla kapanabilen bir şeyse terfi et:
   - stop yoksa ATR14×3 stop (`stop_eklendi: true`);
   - pozisyon büyüklüğü, maliyet;
   - "kapanışta işlem" gibi yürütme ayrıntıları.

   Giriş/çıkış kuralı ve göstergeler kaynakta açık olmalı. Kaynakta yazan sayısal parametreleri değiştirme.
2. **`eksik` kalır:** Sinyal mantığı kaynakta yoksa kart eksik kalır. Bu, giriş/çıkış kuralı ya da gösterge parametresinin eksik olması demek. `belirsiz` listesine tek satır standart gerekçe ekle: `T16: sinyal tanimi eksik (<ne eksik>)`. Tahmin ya da uydurma parametre yazma.
3. Terfi eden her kart `python engine/spec.py --kontrol` ile hatasız geçmeli. `INDEKS.csv`'yi kartlardan yeniden üret.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. PR gövdesinde terfi edenler ve eksik kalanlar tablosu, her kart için bir satır gerekçe. Terfi edenleri lider taratır.

## T17 — Gün içi adaylar için null testi (sahibi: codex-worker; önerilen model: **Sol**)

Onaylı karar (3): `backtests/asama2a.py` şu an gün içi (tf ≠ 1D/1W) adayları atlıyor; T17 bunu kapatır.

1. `asama2a.py --tf 1H,30m,15m,5m` desteği. Adaylar `results/tarama.csv`'de gün içi `tf`'li ve aşama 1'i geçmiş satırlardır. Veri `--veri-kok` altındaki arşivlerden, `tarama.py` ile aynı yükleyiciyle okunur.
2. **Null modeli:** Günlük mantık aynen kalır:
   - havuz tüm geçerli barlar;
   - en az 200 tekrar, sınırda kalanlar için 1000;
   - işlem sayısı ve elde tutma dağılımı gerçek stratejiden alınır; stop ve çıkış kuralları aynıdır.

   Karar kuralı: PF **ve** ortalama R, null'un %95'lik değerinin üstünde olmalı.
3. **Performans:** 5m kripto ≈ 500k bar × 25 sembol; tek koşu ~100 sn. Vektörleştirilmiş null örnekleme ya da `--isci` paralelliği kullan. Hedef: aday başına 15 dakikadan az. Ölçülen süreyi PR'a yaz.
4. **BIST 1H:** `veri_kalitesi` nedeniyle Doğrulanamaz kalır, null testine girmez.
5. **Testler:**
   - sentetik gün içi veride uçtan uca test;
   - günlük adaylarda mevcut `results/asama2a.csv` sonucu birebir korunmalı (regresyon testi ya da C01 karşılaştırması).
6. `asama2a.yml` iş akışına `tf` girdisi ekle.

Gerçek koşuyu lider yapar. Teslim: Tek PR (base `main`).
