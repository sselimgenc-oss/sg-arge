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

## Codex yapmaz (lideri bekler)
- **Yorumlayıcı ve emülatör** anlamını değiştiren kod (`engine/pine`, `engine/tv_emulator.py`). Desteklenmeyen özellik çıkarsa listele, ekleme.
- **Kapı, eşik ve sıralama yöntemi; sanal havuz ve gölge kitap aday seçimi.**
- **`main`'e birleştirme, denetim raporları, kullanıcı kararı gereken her şey.** Para, hesap, ücretli veri, yeni kural.

## Durum (Codex yazar)
