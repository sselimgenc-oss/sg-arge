# Codex görev listesi, 2026-10-25 → 2026-10-26 akşamı (lider limiti açılana kadar)

**Kullanıcı kararı:** lider (Claude) haftalık limiti dolduğu için yaklaşık 1,5 gün az çalışacak. Yürütme ve veri işleri Codex'te. Önemli kararlar ve yöntem lideri bekler (aşağıda "Codex yapmaz").

## Genel kurallar
- **Yöntem, eşik, karar kodu değişmez:** `docs/TEST_YAPISI.md`, `docs/GOREV_TV2.md` Ek 1-3, `docs/GOREV_U7.md`.
- **Dal:** `codex/tv2-kosu`, `origin/claude/magical-ride-c7apbp`'den açılır. Yorumlayıcının en güncel hâli ve footprint orada. U7 işleri `#200`'de (`codex/u7-tum-stratejiler`) sürer.
- **`main`'e birleştirme yok.** PR'ları lider birleştirir.
- **`paper/`, `paper.yml` ve gölge kitaplara dokunulmaz.**
- **Uzun koşular yalnız GitHub Actions'ta:** Codex ortamı arka plan süreçlerini öldürüyor.
  - Push öncesi `git pull --rebase` + 4 deneme döngüsü.
  - Sonuçlar artifact olarak da yüklenir.
- **Actions dakikası (özel repo aylık kota):** her koşudan sonra harcanan dakikayı bu dosyanın sonuna yaz. Bu ay toplam **1.500 dakikayı geçecekse durdur** ve kullanıcıya sor.
- **Her iş bitince:** kutuyu işaretle, commit'le, dosyanın sonuna 1-2 satır durum yaz.
- **Takılırsan:** sebebi yaz, sıradakine geç.

## A. TV-2 kripto, kalan 208 strateji (öncelik 1)
- [ ] **Yeni iş akışı `.github/workflows/tv2.yml`:**
  - `workflow_dispatch`, girdisi kuyruk dosyası.
  - Matris en az 8 parça; parçalar `results/tv2/kuyruk_kripto_kalan.txt` satırlarından bölünür.
  - Her parça `xargs -P2 -I{} timeout 7200 python -m backtests.tv2 --ayri --dakikalik {}`, `timeout-minutes: 350`.
  - `data/tv2` için `actions/cache`: Binance klines, `ast/` ayrıştırma önbelleği, `footprint/`.
- [ ] **Sonuçlar:** `results/tv2/satirlar/*.json` + `getiriler/*.csv` `codex/tv2-kosu`'ya commit'lenir. Var olan ve `zaman_asimi` olmayan satır ezilmez.
- [ ] **Hepsi bitince:** `python -m backtests.tv2 --birlestir` ve `python -m backtests.tv2_sirala`. Karar sayılarını (geçti/kaldı/izle/islem_yok/desteklenmiyor/veri_yok/veri_ucretli/hata) buraya yaz.
- [ ] **2 saatlik sınırda kesilenler:** ayrı listeye (`kuyruk_uzun.txt`) yaz, ikinci geçişte `timeout 18000` ile tek tek koş.

## B. U7 (öncelik 2, `#200`)
- [ ] Faz 1 Actions koşusu (40145166229) bitince sonuçları commit'le.
- [ ] **Denetim B6:** her grup bitince `python backtests/u7_ozet.py` çalıştır, `results/u7/huni_ozet.csv` (v2 kararı `karar_adim2`) commit'lensin. Grup `huni_ozet.md` dosyalarının başına "v1 tablo: bilgi, eleme değil; karar: results/u7/huni_ozet.csv karar_adim2" satırı ekle.
- [ ] Sıralama için **her varyantın günlük getiri dosyası** (`results/u7/<grup>/getiriler/<varyant>.csv`, sütun `getiri`, UTC tarih indeksi) eksiksiz olsun: U4, U6, Faz 1, Reddit. U1'de var.
- [ ] Reddit Aşama 2b.

## C. Kripto dışı veri (öncelik 3, `codex/tv2-kosu`)
- [ ] **Yükleyiciler:** `backtests/tv2.py::veri()`'ye Dukascopy (FX, metal, endeks CFD; dakikalık geçmiş) ve vnstock (HNX/HOSE) dalları; testleri `tests/test_tv2_kosucu.py`'de (ağ yok, sahte indirme). yfinance gün içi hazır (`_yfinance_gun_ici`).
- [ ] **Eşleme tablosu** `arastirma/tv2_veri_eslesme.csv`: 636 kripto dışı strateji. Sütunlar: id, yayin_sembolu, tf, kaynak, esdeger, en_eski, not. "Yok" yazmadan önce en az iki kaynak dene.
- [ ] **Kuyruk** `results/tv2/kuyruk_kripto_disi.txt`: önce son sürümü 2026'dan önce olanlar (~78), sonra kalanı. A'daki iş akışıyla koş.

## D. Kapsam (öncelik 4)
- [x] (2026-10-25: 33/33 denendi, hiçbiri açılmadı) **Kaynağı kapalı / bulunamadı 33 strateji:** eski alfanümerik id ve script sayfasındaki `script_id_part` ile yeniden ara. Bulunanları `arastirma/tv2_surumler.csv`'ye ekle (aynı sütunlar, `kaynak_acik=acik`).
- [ ] **Yeni kütüphane `import`'ları:** `arastirma/tv2_kutuphaneler.csv`'ye satır ekle. PUB kimliği kütüphane sayfasındaki `"script_id_part"`'tan alınır.

## E. Beyin fırtınası (Sol 6.1)
Her biri ilgili dosyanın sonuna "Sol 6.1 eleştirisi" başlığıyla yazılır.
- [ ] **`docs/FAZ3_YURUTME.md`:** emir yolu, manuel ölçüm, test verisi ile gerçek enstrüman farkı, risk bölüşümü, güvenlik, aşamalı geçiş.
- [x] (yazıldı) **`docs/FAZ2_NOTLAR.md` bölüm 4, copy trade:** yalnız biz kopyalarız (kullanıcı kararı). Kaynaklar, "başarılı" ölçütü (izlemeye başladıktan sonraki dönem), gecikme ve kayma, risk, vergi.
- [x] (yazıldı) **`docs/FAZ2_NOTLAR.md` bölüm 5, pano altyapısı:** statik / Streamlit-Dash / FastAPI+React / PWA-Telegram; Faz 3 ile uyum.

## F. Önemli işler (kullanıcı kararı 2026-10-25: Codex yapar, lider pazartesi 14:15 TR denetler)
Her biri ayrı commit; testsiz kod yok; tam paket (`pytest tests/`) yeşil olmadan push yok.
- [ ] **Yorumlayıcı eksikleri:** `strategy.risk.max_position_size`, `renko` (ticker.renko + security), `request.earnings` / `request.financial` (yfinance; olmayan veri na). Her biri `tests/test_pine_yorumlayici.py`'de bir testle. Mevcut kalıplar: `_cizim`, `_matris`, `_footprint`, `_kutuphane`. Anlam TradingView belgesine dayanmalı; belge yoksa yapma, listele.
- [ ] **Sıralama genişletme (TEST_YAPISI Adım 3):** `backtests/tv2_sirala.py` mantığı U7'nin `karar_adim2 == Geçti` varyantlarına uygulanır (aynı ölçek %10 oynaklık, blok bootstrap p10, kopya ayıklama, aynı tohum). Çıktı `results/u7/siralama.csv`. Eşikler ve yöntem değişmez.
- [ ] **Sanal havuz (TEST_YAPISI Adım 4) taslağı:** `docs/SANAL_HAVUZ.md`. Geçen ve sıralanan adayların (TV-2 + U7) eşit risk sepeti; 20 gölge kitap aday listesi (12 güçlü + 4 çeşitlendirici + 4 kura, tohum sabit). **Yalnız öneri.** Gölge kitaba ekleme ve `paper/` değişikliği yok; kullanıcı onaylar.
- [ ] **TV-2 S1 denetimi:** geçen ilk 5 stratejinin Pine kaynağını oku. Yorumlayıcının yaptığıyla karşılaştır (girişler, çıkışlar, boyut, security kullanımı); şüpheli her şeyi `docs/denetim/S1_codex.md`'ye yaz.

## Hâlâ Codex yapmaz
- `main`'e birleştirme. PR açılır, lider birleştirir.
- Kapı, eşik, karar kuralı, maliyet varsayımı değişikliği.
- `paper/`, `paper.yml`, gölge kitaplar; para, hesap, ücretli veri, yeni kural (kullanıcı kararı).

## Durum (Codex yazar)

**Lider notu 07:15 UTC:**
- **XAUUSDT / NVDAXUSDT `veri_yok`** (ip7Wyl0i, cXpZ682G, jLKPS0lF): bu semboller Binance USDⓈ-M futures'ta (TradFi perp) olabilir. `veri()` spot'ta yoksa `fapi/v1/klines`'ı da denesin, satıra `kaynak=binance_um` yazsın. Testi sahte indirmeyle yazılsın. Sonra bu üçü yeniden koşulsun.
- **Şüpheli sonuçlar:** w45uet8E −164%, anNnwsQo −139%, zCYYilCg −64% (18 işlem), jTHvkEVo +1136%. Bunları yeniden koşma. Lider pazartesi denetimde inceleyecek. -100%'ün altı spot için imkânsız (kaldıraç/piramit ya da emülatör).
- **Actions dakikası:** 8 parça × ~5 saat, 1.500 sınırı aşıldı. Yeni koşu başlatmadan önce kullanıcıya sor.

**Lider notu 08:20 UTC (öncelik 1):**
- **Koşu 40151651235'te 0/5/6/7. parçaların sonuçları dala yazılmadı.** Push adımı `rebase` çakışmasında kaldı: `CONFLICT (add/add) results/tv2/satirlar/0GhXXwWS.json`. İptal edilen koşu 40151685041 aynı dosyaları önceden commit'lemişti.
- **Sonuçları kurtar:** artifact'lar `tv2-{0,5,6,7}-40151651235` 2026-11-08'e kadar duruyor. İndir, satır kuralıyla (`zaman_asimi` olmayan mevcut satır ezilmez, yoksa yeni satır yazılır) `codex/tv2-kosu`'ya commit'le.
- **İş akışını düzelt:** commit adımı çakışmada `rebase --abort`, ardından `git fetch` + `git checkout origin/<dal> -- .` + yeni sonuçları satır kuralıyla kopyala + commit/push. Ya da her parçanın ayrı dosyaya yazması. Çakışmada sessizce sonuç kaybolmasın: adım hata vermeli.
