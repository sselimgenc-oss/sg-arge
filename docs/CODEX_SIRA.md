# Codex iş sırası, 2026-10-25 16:00 TR → 2026-10-26 14:15 TR (lider denetimi)

**Nasıl çalışılır:** sırayla yürü. Her iş bitince:
- satırın başındaki `[ ]` → `[x]`, yanına 1 satır sonuç;
- commit + `git pull --rebase` + push (4 deneme);
- **sormadan sıradakine geç.**

**Takılırsan:**
- sebebi satıra `TAKILDI: ...` diye yaz ve bir sonrakine geç;
- durmak yok; kullanıcı yalnız "devam" yazacak.

Kurallar `docs/GOREV_CODEX_2026-10-25.md` "Genel kurallar" ve "Hâlâ Codex yapmaz" ile aynı:
- yöntem, eşik ve karar kodu değişmez;
- `main`, `paper/` ve gölge kitaplara dokunulmaz;
- testsiz kod yok; `pytest tests/` yeşil olmadan push yok.

**Actions dakikası:** kullanıcı "yarına kadar full çalıştıralım" dedi. Koşu başlatmak serbest. Yine de:
- bir seferde en fazla 1 matris koşusu (8 parça);
- her koşu sonrası harcanan dakikayı bu dosyanın sonuna yaz;
- GitHub kota/fatura hatası verirse Actions'ı bırak, yerel/kısa işlere geç.

**Dallar:**
- TV-2 işleri `codex/tv2-kosu`;
- U7 işleri `codex/u7-tum-stratejiler` (#200);
- yorumlayıcı ve kod işleri `codex/tv2-kosu`'dan açılan `codex/yorumlayici-ek`. Bitince PR aç, lider birleştirir.

---

## 1. Kurtarma ve iş akışı onarımı (önce bunlar, Actions gerektirmez)
- [x] **1.1** Koşu 40151651235'in `tv2-0`, `tv2-5`, `tv2-6`, `tv2-7` artifact'larını indir (`gh run download 40151651235 -n tv2-0-40151651235` ...). (2026-10-25: 26/26/26/24 satır kurtarıldı; iki tamamlanmış mevcut satır korundu, `8fba59a`.)
  - Satır kuralıyla `results/tv2/satirlar` + `getiriler`'e kopyala: mevcut satır `zaman_asimi` değilse ezilmez.
  - Commit: `tv2: 0/5/6/7 artifact'tan kurtarıldı`.
- [x] **1.2** `.github/workflows/tv2.yml` "Commit result checkpoints" adımını düzelt: (2026-10-25: satır-birleştirme betiği + birim testi, rebase abort/fetch/uzak baştan birleştirme ve dördüncü denemede `exit 1`; `aeb117c`, `f65ae43`.)
  - Çakışmada sonuç kaybolmasın: `pull --rebase` başarısızsa `git rebase --abort`.
  - Sonra `git fetch` + `git reset --hard origin/<dal>`, ardından runner'daki yeni satırları satır kuralıyla yeniden kopyala, commit, push.
  - 4 deneme de başarısızsa adım **exit 1** versin (sessiz başarı yok).
  - Kopyalama mantığını `backtests/tv2_birlestir_satir.py` gibi küçük bir betiğe koy ve testini yaz.
- [x] **1.3** Lider notu 07:15: `backtests/tv2.py::veri()` Binance spot'ta sembol yoksa USDⓈ-M futures'ı (`https://fapi.binance.com/fapi/v1/klines`) denesin; satıra `kaynak=binance_um` yazsın. (2026-10-25: sahte indirme testi; altı veri_yok satırı yeniden denendi, spot/UM'de de yok, `a605f59`, `a8c59af`.)
  - Testi sahte indirmeyle yaz.
  - Sonra ip7Wyl0i, cXpZ682G, jLKPS0lF, 2wxKTakm, N18VdyZl, 6tlWqaYm için `veri_yok` satırlarını yeniden koş (kısa koşular; yerelde zaman aşımı olursa 2. turdaki koşuya ekle).
- [x] **1.4** `kuyruk_kripto_kalan.txt`'yi yenile: satırı olmayan + `zaman_asimi` olanlar. Sayıyı buraya yaz. (2026-10-25: 208 → 17, `bc419b7`.)

## 2. TV-2 kripto, ikinci tur (Actions)
- [x] **2.1** Yenilenen kalan kuyrukla `tv2.yml` koşusu (8 parça, parça başı `timeout 7200`). Bitince 1.1'deki kuralla sonuçları doğrula: her parçanın commit'i dala gelmiş olmalı. (2026-10-25: run `40197100719` 8/8 başarılı; commit yarışı nedeniyle artifact'lar satır kuralıyla kurtarıldı ve `93f7984` ile itildi. 4 satır sonuçlandı, 13 satır 7200 sn sınırında kaldı.)
- [ ] **2.2** 2 saatte kesilenler → `results/tv2/kuyruk_uzun.txt`. Tek tek `timeout 18000` ile (`--dakikalik`) ayrı koşu. Yine kesilen olursa satırına `zaman_asimi_uzun` notu.
- [ ] **2.3** `python -m backtests.tv2 --birlestir` + `python -m backtests.tv2_sirala`. Karar sayılarını (gecti/kaldi/izle/islem_yok/desteklenmiyor/veri_yok/veri_ucretli/hata/zaman_asimi) buraya yaz.
- [ ] **2.4** **Şüpheli sonuç listesi** `docs/denetim/tv2_supheli.md`: net getirisi −100%'ün altında veya +300%'ün üstünde olanlar (örn. w45uet8E, anNnwsQo, jTHvkEVo, zCYYilCg).
  - Yorumlayıcıyla 1-2 satır neden tahmini: kaldıraç, `pyramiding`, `default_qty_type`, komisyon.
  - **Kararı değiştirme**, yalnız listele.

## 3. U7 (#200)
- [ ] **3.1** Faz 1 Actions sonuçları commit'li mi kontrol et; eksikse artifact'tan al.
- [ ] **3.2** Denetim B6:
  - `python backtests/u7_ozet.py` çalıştır, `results/u7/huni_ozet.csv` (`karar_adim2`) commit'lensin.
  - Her grubun `huni_ozet.md` başına "v1 tablo: bilgi, eleme değil; karar: results/u7/huni_ozet.csv karar_adim2" satırı.
- [ ] **3.3** Günlük getiri dosyaları:
  - `results/u7/<grup>/getiriler/<varyant>.csv` (sütun `getiri`, UTC tarih indeksi) U4, U6, Faz 1, Reddit için eksiksiz.
  - Eksik olanları üret; hangi varyantta eksik kaldığını yaz.
- [ ] **3.4** Reddit Aşama 2b (görev tanımı `docs/GOREV_U7.md`).
- [ ] **3.5** #200 PR açıklamasını güncelle (yapılanlar, sayılar), taslaktan çıkar. CI yeşil olsun.

## 4. Kripto dışı veri (C)
- [ ] **4.1** `veri()`'ye Dukascopy dalı (FX, XAU/XAG, endeks CFD; dakikalık, UTC). Testi sahte indirmeyle.
- [ ] **4.2** `veri()`'ye vnstock dalı (HOSE/HNX). Paket yoksa ya da erişilemezse `TAKILDI` yaz, geç.
- [ ] **4.3** `arastirma/tv2_veri_eslesme.csv`:
  - 636 kripto dışı strateji; sütunlar `id, yayin_sembolu, tf, kaynak, esdeger, en_eski, not`.
  - "Yok" demeden önce en az iki kaynak dene: yfinance gün içi, Dukascopy, Binance TradFi perp, stooq.
- [ ] **4.4** `results/tv2/kuyruk_kripto_disi.txt`: önce son sürümü 2026'dan önce olanlar, sonra kalan.
- [ ] **4.5** Kripto dışı koşu (Actions, `tv2.yml`'e kuyruk girdisiyle). Bitince 2.3'teki gibi birleştir, sayıları yaz.

## 5. Yorumlayıcı eksikleri (dal `codex/yorumlayici-ek`, PR)
Her biri ayrı commit ve `tests/test_pine_yorumlayici.py`'de test. Anlam TradingView belgesine dayanmalı; belge yoksa yapma, listele.
- [x] **5.1** `strategy.risk.max_position_size` (4QubxEEw). Kalıp: `_gun_ici_risk`. (2026-10-25: entry dolum adedi açık aynı-yön pozisyonla birlikte sınırı aşmayacak biçimde kısıtlandı; birim testi ve tam paket 1328 geçti/4 atlandı, `1f00e8f`.)
- [ ] **5.2** `ticker.renko` + `request.security` (CmZUAjHp). Kutu boyu: Traditional/ATR. Belgeye göre yalnız kapanış tabanlı tuğlalar. **TAKILDI:** resmî belge yalnız ticker kimliğinin `request.security` ile kullanılacağını ve örnek ATR çağrısını veriyor; Traditional/ATR tuğla oluşumu, ters dönüş ve zaman eşleme algoritmasını tanımlamıyor. Bunları varsaymak stratejiyi sadık olmayan biçimde koşturur; ayrıntılı resmî algoritma ya da referans seri gerekli.
- [x] **5.3** `request.earnings` / `request.financial` (R0hKtaEP, rDM9AoU1, fnPiNvdV). Kaynak yfinance; olmayan veri `na`. (2026-10-25: earnings actual/estimate ve TOTAL_SHARES_OUTSTANDING/FQ sağlayıcısı, gaps eşlemesi ve sahte-sağlayıcı testi eklendi; tam paket 1329 geçti/4 atlandı, `99e2030`.)
- [x] **5.4** `array.get` na (DcjBbnzh) ve "dizi sınır dışı" (uGP5w2ki): kök nedeni bul, TradingView davranışına uyan düzeltme + test. (2026-10-25: kök neden Python'un negatif indeksini son elemana sarmalamaktı; Pine indeksleri 0'dan başlar. Negatif/`na` indeks artık açık Pine hatası, testli; tam paket 1330 geçti/4 atlandı, `d680c65`.)
- [ ] **5.5** Yavaş betikler (LA06Kpl1, OvE4qQgh, JeRCEqWU, wQ1dtwbW, nmnHkA02, qetKgBK2, b4EWZCPJ):
  - `cProfile` ile en sıcak 3 fonksiyonu `docs/denetim/yavas_profil.md`'ye yaz;
  - davranış değiştirmeyen hızlandırma varsa yap.
- [ ] **5.6** Tam test paketi yeşil → PR aç (`codex/yorumlayici-ek` → `claude/magical-ride-c7apbp`). Düzelen stratejileri kalan kuyruğa ekle.

## 6. Sıralama, havuz, denetim (yalnız analiz)
- [ ] **6.1** `backtests/tv2_sirala.py` mantığını U7 `karar_adim2 == Geçti` varyantlarına uygula.
  - Aynı ölçek (%10 oynaklık), blok bootstrap p10, kopya ayıklama, aynı tohum.
  - Çıktı `results/u7/siralama.csv`.
- [ ] **6.2** `docs/SANAL_HAVUZ.md` taslağı:
  - TV-2 + U7 geçenlerin eşit risk sepeti;
  - 20 gölge aday (12 güçlü + 4 çeşitlendirici + 4 kura, sabit tohum).
  - **Yalnız öneri**; `paper/` yok.
- [ ] **6.3** S1 denetimi `docs/denetim/S1_codex.md`: TV-2'de geçen ilk 5 stratejinin Pine kaynağını oku, yorumlayıcının yaptığıyla karşılaştır (giriş, çıkış, boyut, security).
- [ ] **6.4** `docs/FAZ3_YURUTME.md` sonuna "Sol 6.1 eleştirisi":
  - emir yolu;
  - manuel ölçüm;
  - test verisi ile gerçek enstrüman farkı;
  - risk bölüşümü;
  - güvenlik;
  - aşamalı geçiş.
- [ ] **6.5** Yeni `import` eden kütüphaneler: kapsam taramasında `eksik_kutuphane` çıkanları `arastirma/tv2_kutuphaneler.csv`'ye ekle (PUB = sayfadaki `"script_id_part"`), ilgili stratejileri yeniden koş.

- [ ] **6.6** Copy trade, Sol 6.1 değerlendirmesi (kullanıcı isteği 2026-10-25). Kaynaklar: `arastirma/copytrade/copy_trading_derin_arastirma_2026.pdf` (Argon) ve `docs/FAZ2_NOTLAR.md` bölüm 4 özeti. `docs/FAZ2_NOTLAR.md` sonuna "Sol 6.1 eleştirisi: copy trade araştırması" başlığıyla yaz:
  - (a) Rapordaki iddialardan en az 10 kritik olanını kaynağından doğrula ve tabloya `doğrulandı / yanlış / doğrulanamadı` yaz. Öncelik: Binance TradFi copy, Hyperdash ücretleri, Hyperliquid API alanları, SPK'ya göre BIST kopyalama yasağı, akademik makaleler, link uyuşmazlıkları.
  - (b) Varlık sınıfı başına önerilere katıl ya da itiraz et, gerekçesiyle.
  - (c) Sanal izleme pilotu tasarla (kod yazma, yalnız tasarım):
    - Hyperliquid'den aday cüzdan ve vault seçimi;
    - günlük veri toplama;
    - TEST_YAPISI ile uyumlu değerlendirme: izleme başlangıcından sonraki dönem, maliyet ve kayma, kırmızı bayrak filtreleri;
    - Binance lider verisini günlük kaydetme.
  - (d) Kullanıcıya sorulacak kararlar. Para, hesap ve hukuk soruları Codex'e değil kullanıcıya.

- [ ] **6.7** ML araştırması, Sol 6.1 değerlendirmesi (kullanıcı isteği 2026-10-25). Kaynaklar: `arastirma/ml/algoritmik_trading_makine_ogrenmesi_2026.pdf` ve `docs/FAZ2_NOTLAR.md` bölüm 6. Dosyanın sonuna "Sol 6.1 eleştirisi: ML" yaz:
  - (a) Kritik iddiaları kaynağından doğrula: DSR formülü ve N_eff, `arch.bootstrap.StepM` API'si, skfolio `CombinatorialPurgedCV`/HRP, jdehorty kaynağındaki etiket satırı, 2026 kaynakları.
  - (b) 3 pilotun sırası ve kapsamı hakkında görüş.
  - (c) **Kod (yalnız bilgi, karar değiştirmez):** `backtests/tv2_sirala.py` çıktısına `dsr` ve `n_eff` sütunlarını ekle. Kapı, sıralama ve eşik **değişmez**; test yaz.
  - (d) TV-2'de `lookahead_on` + üst zaman dilimi okuyan stratejileri listele (`results/tv2/lookahead_listesi.csv`: id, satır, ifade, karar).

## 7. Liste bittiyse
- [ ] **7.1** `DURUM.md`'ye ve bu dosyanın sonuna 10 satırlık özet: ne bitti, sayılar, takılanlar, lider kararı gerekenler.

---
## Durum ve Actions dakikası (Codex yazar)

**Lider notu 13:10 UTC: Actions DURDU.** Aylık 2.000 dakikalık kota 05:20 UTC'de doldu. Yeni koşular 3-4 saniyede başarısız oluyor (run 40195741964, paper.yml de). Kullanıcı karar verene kadar:
- **Actions koşusu başlatma.** 2.1, 2.2 ve 4.5 bekler; satırına `BEKLİYOR: Actions kotası` yaz.
- **Actions gerektirmeyen işlere geç:** 1.1 (artifact indirmek dakika harcamaz), 1.2, 1.3 (yalnız kod + test), 2.4, 3.x, 4.1-4.4, 5.x, 6.x.
- **Uzun koşuları yerelde başlatma:** ortam arka plan süreçlerini öldürüyor. Kısa tekil koşular (`timeout 600`) olur.

**Lider notu 13:20 UTC: Actions AÇIK.** Repo herkese açık yapıldı (kullanıcı kararı), Actions dakikası artık sınırsız. `BEKLİYOR: Actions kotası` maddeleri serbest:
- **Hemen:** 2.1'i başlat. Bitince 2.2'yi, sonra 4.5'i başlat.
- **Aynı anda en fazla 1 matris koşusu.**
- **Repo herkese açık:** secret, anahtar ya da kişisel veriyi commit'leme.

**Lider notu 13:30 UTC: başarısız koşuları yeniden koş** (kullanıcı isteği; sırayla, aynı anda 1 matris):
1. **TV-2 kripto, run 40195741964:** kota yüzünden 4 sn'de düştü. 2.1 olarak yeniden başlat (`gh workflow run tv2.yml --ref codex/tv2-kosu`).
2. **Uçtan uca huni, run 40145166229:**
   - `asama2a` işi düştü, diğer 8 iş geçti.
   - Önce logda sebebi bul (`gh run view 40145166229 --log-failed`).
   - Kod hatasıysa düzelt + test, sonra yalnız düşen işi koş (`gh run rerun 40145166229 --failed`, ya da `huni.yml`'i yalnız aşama 2a ile).
   - Sonuçları #200'e commit'le; 3.1/3.4 ile birleştir.
3. **Paper trade (12, 13. koşular):**
   - Saatlik zamanlayıcı (:17) kendisi yeniden deniyor. Dokunma (`paper/` Codex yapmaz).
   - Lider kontrol eder.
4. Her biri bitince sonucu bu dosyaya 1 satır yaz.
