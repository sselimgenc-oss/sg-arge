# Görev: Kapı v3 — koşucu, kalibrasyon ve tüm stratejilerin yeniden değerlendirmesi (2026-10-26)

Kaynak: `docs/KAPI_V3.md` (**DONDURULDU**; eşik, sınıf ve kalibrasyon kuralı değiştirilmez). Dal: `codex/kapi-v3`
(`main`'den). Durum: `docs/codex_durum_kapi_v3.md`. Paper'a dokunulmaz. Belgede yazmayan karar gerekirse **dur** ve
durum dosyasına yaz.

**İki aşama:** İş 1 bitince PR açılır, lider kalibrasyonu denetler. **İş 2 lider onayından sonra başlar.**

## İş 1 — Koşucu ve kalibrasyon (`backtests/kapi_v3.py`)
### 1.1 Motor tabanlı plasebo (adım 4)
- **B ailesi (U7):** `backtests/asama2a.random_entry_signals` + `tarama.Prepared.run` (aynı çıkış kuralları, sembol
  başına aynı giriş sayısı), sınama 2023-01-01 sonrası, `gercekci` maliyet. 1.000 tekrar, tohum `zlib.crc32(kimlik)`.
- **A ailesi (TV-2):** Pine girişleri yorumlayıcının içinde olduğundan **işlem yerleştirme plasebosu**: stratejinin
  kendi işlem listesi (yön, tutma süresi bar cinsinden, boyut) korunur; başlangıç barları sınama penceresinde rastgele
  ve çakışmasız seçilir; dolum gerçek bar fiyatlarıyla (`backtests/tv2.veri`, aynı mintick ve tz kuralları), maliyet
  `gercekci`. 1.000 tekrar. Test istatistiği: net getiri; tek yönlü p = (1 + #{plasebo ≥ gerçek}) / (1 + 1.000).

### 1.2 Bir bar gecikme (adım 3)
- B: giriş ve çıkış sinyalleri bir bar kaydırılarak motor yeniden koşulur.
- A: her işlemin giriş ve çıkışı, orijinal dolum barından **sonraki barın açılışında** yeniden fiyatlanır.
- 2x maliyet (adım 3b) aynı işlem listesiyle.

### 1.3 Alfa ve çoklu test (adım 5–6)
`backtests/plasebo.py`'deki `nw_alpha` (tek yönlü t; kripto 365, diğer 252 gün) ve maruziyet eşleşmiş kıyas
(`_market`, TV-2'de kendi sembolü). Blok bootstrap: 20 günlük blok, 5.000 tekrar, alfa %90 alt sınırı. BHY: aile
içindeki **tüm test edilenlerin** plasebo p-değerlerine, q = 0,10. Sınıflandırma `KAPI_V3.md` §2 ve §2.1'deki gibi.

### 1.4 Güç ve yanlış-geçme kalibrasyonu (`KAPI_V3.md` §3) — gerçek sonuçlardan önce
- **Taban:** her gerçek strateji şablonu için bir motor tabanlı plasebo çekilişi (kenarı sıfır, gerçek yapıyı korur).
- **Kenar:** maruziyet süresince bar getirilerine sabit kayma eklenir; kayma, maruziyet eşleşmiş kıyasa göre fazla
  getirinin yıllık Sharpe'ı hedefe (0 / 0,5 / 1,0 / 1,5) eşit olacak biçimde seçilir.
- **Boru hattı:** adım 2–6 birlikte. Plasebo dağılımı kenara bağlı değildir → şablon başına bir kez hesaplanıp tüm
  simülasyonlarda paylaşılır (hesap süresi için).
- **BHY simülasyonu:** her tekrarda gerçek aile büyüklüğünde sentetik aile; üyelerin %10'u senaryo Sharpe'ında, kalanı
  Sharpe 0. Güç kenarlı üyelerde, yanlış geçme Sharpe 0 üyelerde ölçülür.
- **Hücreler:** aile × piyasa × tf × sınama uzunluğu (`KAPI_V3.md` §3). Hücre başına ≥ 1.000 simülasyon, Wilson %95 aralığı.
- **Çıktı:** `results/kapi_v3/kalibrasyon.csv` (hücre, senaryo, n, geçme oranı, aralık, t = 2,00 ve 1,65 için) ve
  `results/kapi_v3/t_esik.csv` (hücre başına t*, §3 kuralıyla otomatik). Gerçek stratejilerin sonucu bu iş'te **hesaplanmaz**.

### 1.5 Testler (ağsız)
Plasebo işlem sayısı, yön ve tutma süresini koruyor; çakışma yok; sabit tohumla aynı sonuç; gecikmede fiyatın bir bar
sonraki açılış olması; sentetik kenarın hedef Sharpe'ı vermesi (tolerans); BHY bilinen örnekte; t* kuralı (güç < %50 →
1,65; yanlış geçme bozulursa 2,00); §2.1 sınıflandırması (Kaldı/Yetersiz ayrımı) bilinen örneklerle.

### 1.6 Actions
`.github/workflows/kapi_v3.yml`: `workflow_dispatch` + `push` tetiği yalnız `codex/kapi-v3` dalında, yalnız
`backtests/kapi_v3.py` ve iş akışı değişince. Gerekirse matris (aile × hücre grubu). Sonuçları dala yazar
(`git pull --rebase` ile 3 deneme, `plasebo.yml`'deki gibi). Zaman sınırı aşılırsa parçalara böl, uydurma sonuç yazma.

## İş 2 — Tüm stratejiler (lider onayından sonra)
- A: TV-2'de **test edilen tüm** stratejiler (`results/tv2/satirlar/*.json`, veri olanlar; ~530). B: U7'nin 119 varyantı.
- Çıktı `results/kapi_v3/sonuc.csv`: kimlik, aile, piyasa, tf, sınama yıl/işlem, her adımın değeri ve geçti/kaldı,
  p, alfa, t, t*, BHY q, sınıf (Geçti/Yetersiz/Kaldı), kırılgan, bilgi sütunları (DSR, PSR, PF, eski null), küme.
- 13 paper kitabı için ayrı satır listesi. Özet `docs/kapi_v3_sonuc.md`: sınıf sayıları aile × hücre; geçenler tablosu;
  sınırlamalar. **Karar önerisi yok.**
- Yorumlayıcı paritesi (`KAPI_V3.md` §4 madde 4) bu iş'in dışında: lider ayrıca planlar.

## Başlarken / bitirirken
`git checkout main && git pull origin main && git checkout -b codex/kapi-v3`. `AGENTS.md` kuralları geçerli.
Bitince `python -m pytest -q` (sonuç PR'a) ve `git push -u origin codex/kapi-v3`. PR başlığı: `[Faz2] Kapı v3 — İş 1`.

## Lider denetimi 1 (2026-10-27) — `codex/kapi-v3` birleştirilmedi; düzeltilecekler
Korunacaklar: `aile_A.csv` (530), `aile_B.csv` (119), `bhy`, `wilson`, `delay_signals`, `tv_one_bar_delay`, `u7_placebo`, `classify`.
1. **Gerçek şablonlar:** `calibration_rows`'daki sentetik fikstür kaldırılır. Şablon = `aile_A`'dan sınamada ≥ 1 işlemi
   olanlar + `aile_B`'nin 119'u. Her şablon için motor tabanlı plasebo bir kez: 1.000 net (null dağılım) + 200'ünün
   **günlük getiri serisi** (kenarsız tabanlar).
2. **Kenar:** her simülasyonda rastgele bir taban serisi; aktif günlere `d = SR × σ_aktif / √periods`. Gerçekleşen
   ortalama çıkarılmaz, Sharpe hedefe eşitlenmez (`inject_sharpe_edge`'deki ortalama düzeltmesi kaldırılır). SR 0 = taban.
3. **Tam boru hattı (adım 2–6):** adım 2 şablonun kendi asgari kanıtı; adım 3 kaydırılmış net − şablonun gerçek gecikme
   kaybı (gerçek net − 1 bar gecikmeli net) > 0; adım 4 şablonun null dağılımına göre p; adım 5 NW t + blok bootstrap
   (kalibrasyonda 200 tekrar, sonuçta not); adım 6 her tekrarda gerçek aile büyüklüğünde aile (%10 kenarlı, kalan SR 0), BHY q ≤ 0,10.
4. **Hücreler:** aile × piyasa × tf × sınama uzunluğu; hücre başına ≥ 1.000 kenarlı ve ≥ 1.000 SR 0 gözlemi; Wilson.
   t* kuralı §3 metniyle aynı (SR 0 için Wilson üst ucu ≤ %10 dahil); t = 2'de SR 0 hedefi tutmuyorsa hücre "geçersiz".
5. **Hız:** `tv_trade_placebo`'da her işlem için `choices` listesi yeniden kurulmaz; boş aralıklardan vektörlü örnekleme.
   Actions'ta aile × piyasa matrisi, her iş < 6 saat.
6. **Testler:** SR 0'da geçme oranı 0 ya da 1 değil; SR 1,0'da gerçekleşen Sharpe ortalaması hedefe yakın ama
   tekrarlar arasında saçılıyor; BHY elle hesaplanmış örnek; TV yerleştirmede çakışma yok, işlem sayısı korunuyor.
