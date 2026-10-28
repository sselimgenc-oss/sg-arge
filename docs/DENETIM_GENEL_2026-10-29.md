# Genel bağımsız denetim — sg-arge + sg-pano (2026-10-29)

**Kapsam:** yalnız okuma ve analiz. Kod, eşik ve karar kodu değiştirilmedi. Etre reposu ([bağlantı](https://github.com/ismailkaraabc/etre-trading-office), GPL-3.0)
yalnız fikir karşılaştırması için okundu; kod veya metin alınmadı.

**Denetlenen sürümler:** sg-arge `main` @ `93c9f14`; sg-pano `main` @ `9a5b506`; veri dalları `copytrade-kapi` @ `db01758` (tam koşu 2026-10-28),
`copytrade-izleme` @ `16f4339`. Sentetik modül `origin/codex/sentetik` @ `02a760f` (birleşmemiş).

**Yöntem:**
- Belgeler: `DURUM.md`, `docs/ONKAYIT_D.md`, `docs/KAPI_V3.md`, `copytrade/kurallar.yaml`, `docs/etre_envanter.md`, `docs/codex_denetim_gölge_butunluk.md`,
  `arastirma/copytrade/` (`argon_rejim_kalicilik.md`, `argon_maliyet_dogrulama.md`, `sentetik_ilk_deney.md`), sg-pano `docs/etre_fikirler.md`.
- Kod: `tarama.py`, `kapi.py`, `kapi/istatistik.py`, `defter.py`, `golge.py`, `golge_saglama.py`, `secim.py`, `bayrak.py`, `kollar.py`, `kalicilik.py`,
  `kesif.py`, `izleme_motoru.py`, `worker/src/index.js`, tüm `.github/workflows/*.yml` ve `.github/scripts/*`, sg-pano `index.html` ve testleri.
- Veri: tam koşu `sonuc.csv` (13.767 satır) indirildi. Seçim v1 yerelde yeniden üretildi:
  `python -m copytrade.secim --root <kopya> --tarih 2026-10-28 --taban-dosyasi <boş> --bayraksiz` → `havuz 226 · aday 22 · oda 20 · kontrol 20`
  (bilinen durumla birebir).
- Testler: `python -m pytest -q` → **265 geçti**.
- Güç analizi: `copytrade/sentetik.py` üreticisiyle simülasyon (Ek A; betikler repo dışında, yöntem ve çıktı ekte).
- Actions: iş akışı koşu geçmişi ve günlükleri GitHub API ile okundu.

Kanıtsız iddialar **(şüphe)** diye işaretlidir.

---

## 1. Yönetici özeti — en kritik 5 bulgu

1. **Ön kayıtlı test, beklenen etki büyüklüğünü saptayamaz (B1, B2).**
   - **Saptanabilir en küçük fark (%80 güç):** 20 kişilik oda ve 12 haftalık gölgede günlük kohort–kontrol farkı **%0,11–0,15**. Bu, dönem içinde
     **%10–13**, yıllıklandırıldığında **~%42–56** fazla getiri demektir.
   - **Beklenen fark:** gerçekçi senaryoda (sentetik deneyin yetenek oranı ve alfası, isabet %41 ↔ %20) farkın beklenen değeri günde
     **~%0,02–0,03**. Bu durumda güç **%5–16**; bir kez 12 hafta uzatılsa bile **%8–16**.
   - **Karar kuralındaki boşluk:** en olası sonuç "belirsiz → uzat → yine belirsiz". Ön kayıtta bu dal ve "kohort > 0 ama fark belirsiz" dalı
     tanımlı değil.
2. **Seçim, ön kayıttaki ön elemeyle çelişiyor ve tek bir örneklem içi sayıya dayanıyor (B3–B6).**
   - **Havuz tanımı:** havuz = kapı adım 1+2. Ön kayıttaki **kaldıraç** ön elemesi uygulanmıyor. Odadaki 3 adres kapının kaldıraç sınırını
     aşıyor (en yüksek 11,8x / 12,0x / 36,5x; sınır 10x).
   - **Puan:** risk düzeltmesiz, eşit olmayan pencerelerde (72–200 gün) kümülatif kopya neti. Odadaki 4 adresin dolum geçmişi API sınırında
     kesik.
   - **Kapının istatistiksel adımları:** plasebo, alfa ve BHY seçime hiç girmiyor.
   - **Kaldıraç dengesizliği:** oda, kontrolden belirgin biçimde daha kaldıraçlı (medyan en yüksek kaldıraç 4,9x ↔ 3,2x). Birincil ölçüt beta
     düzeltmesiz olduğundan sonuç, seçimden çok piyasa yönünü ölçebilir.
3. **Operasyon: sonuç kaybettiren tarih hatası ve durmuş veri toplama (B24–B26).**
   - **Tarih hatası:** seçim iş akışı çıktı klasörünün gününü başlangıçta Python'da, yayımlarken bash'te ayrı hesaplıyor. Gece yarısını
     geçen koşu sonucu kaybeder. Koşu 2 22:47 UTC'de 150 dk sınırla başladı; bu risk şu an canlı.
   - **İzleme:** "saatlik" izleme 28 Ekim'de 24 yerine 3 kez çalıştı.
   - **Arşiv:** 7/7 koşu başarısız (R2 adresi geçersiz); D yolunun "gerçek geçmiş evren" dayanağı boş.
4. **Pano Keşif/Huni her zaman örnek (sahte) veriyi gösteriyor (B34).**
   - **Yol uyumsuzluğu:** pano `kesif.json`'u `copytrade/kapi/<tarih>/` altında arıyor; yayıncı `kesif/kesif.json` yazıyor.
   - **Görünürlük:** canlı okuma her seferinde düşüyor ve yalnız küçük bir "ÖRNEK VERİ" etiketiyle örnek aday listesine geçiyor.
   - **Testler:** pano testleri GitHub API'yi her zaman 500 ile kestiği için bu yol hiç sınanmıyor.
5. **Kapsam ve köken denetlenemiyor (B14, B23).**
   - **Kapsam ölçüsü:** "kapsam" = satır sayısı / evren sayısı. Tam koşuda 13.767 / 13.710 = **1,0042**.
   - **Köken:** satırların 12.584'ü önceki koşulardan birleşti, `evren.json` yalnız bir sayı tutuyor.
   - **Sonuç:** hangi güncel evren adresinin işlenmediği, hangi satırın evren dışı olduğu ve satırı hangi kodun hesapladığı yayımlanan veriden
     bulunamıyor. Seçim kapısı (`secim_min_kapsam`) bu sayıya dayanıyor.

---

## 2. Bulgu tablosu

Ciddiyet: **K** kritik · **Y** yüksek · **O** orta · **D** düşük. Emek: S ≤ yarım gün, M 1–3 gün, L > 3 gün.

### 2.1 Strateji ve istatistik

| No | Alan | Ciddiyet | Bulgu | Kanıt | Öneri | Emek |
|---|---|---|---|---|---|---|
| B1 | Güç | **K** | **Etki büyüklüğü:** 20 oda / 12 hafta için saptanabilir en küçük günlük fark (%80 güç) %0,115–0,154; 10 odada %0,17–0,22. Gerçekçi beklenen fark %0,02–0,03/gün; ön kayıt kuralının gücü %5–16. **Null geçme oranı:** %1–5, yani kural ihtiyatlı ama kör. | Ek A tablo A1–A3. σ ≈ %2/gün, havuz puanının dağılımından: std 0,283 / √200. | Karar K‑1: ya birincil tasarımı güçlendir (havuz geneli sıra korelasyonu, tabakalı kontrol, daha uzun süre), ya da "bu ölçekte sınanamaz" sonucunu önceden kabul et. | — (karar) |
| B2 | Karar kuralı | Y | **Tanımsız dallar:** "12 hafta uzatma sonrası yine belirsiz" ve "kohort mutlak > 0, fark aralığı 0'ı içeriyor" sonuçları tanımsız. **Eksik karşıt hipotez:** "seçim işe yaramadı" için eşdeğerlik ya da üst sınır ölçütü yok; Durdurma 2 yalnız "hiçbir kol > 0 değilse" durumunu kapsıyor. | `docs/ONKAYIT_D.md:33-39` | Üç sonuçlu kural yaz: başarılı / işe yaramadı (ör. fark üst sınırı < önceden seçilmiş δ) / sınanamadı. Veri görülmeden, yeni sürüm olarak. | S (belge) + karar |
| B3 | Seçim yöntemi | Y | **Tek puan:** puan = tarz gecikmesindeki tek, örneklem içi, risk düzeltmesiz kümülatif kopya neti. **Kullanılmayan adımlar:** kapı adım 3–7 (plasebo 10.000 tekrar, maruziyet eşleşmiş alfa, BHY) seçime girmiyor. **Havuzdaki dağılım (226):** adım 5'i 10, adım 6'yı 15, yedi adımın tamamını 1 adres geçiyor. Odada adım 5'i geçen yalnız 3. **Dış kanıt:** etre'nin ileri ölçümünde puan–sonuç sıra korelasyonu ≈ 0. | `copytrade/secim.py:40-62`; yerel seçim çıktısı; etre `docs/GELISIM_GUNLUGU.md` 24 Eki 05:00 ve 16:40 | Bilgi: seçimin ne seçtiği raporda açıkça yazılsın ("geçmiş getiri sıralaması"). İkincil kohort tanımı (ör. adım 5–6'yı geçenler) ön kayda eklenebilir. | Karar K‑4 |
| B4 | Seçim ↔ ön kayıt | Y | **Kaldıraç ön elemesi yok:** ön kayıt havuzu "veri yeterliliği, tarz, **kaldıraç**, hesap değeri" ön elemesiyle tanımlıyor. `secim.havuz` yalnız adım 1+2'ye bakıyor; kaldıraç adım 3'te. **Odadaki ihlaller:** en yüksek kaldıraç 11,8x, 12,0x, 36,5x (sınır 10x); bir adreste medyan 3,57x (sınır 3x); bir adreste kısa işlem payı > %25. Havuzda 27 adres en yüksek kaldıraç sınırını aşıyor. | `docs/ONKAYIT_D.md:8`; `copytrade/secim.py:46-52`; `copytrade/kapi.py:714-721`; veri | Karar K‑2: havuza adım 3'ün statik süzgeci (tarz, kısa işlem, kaldıraç) eklensin ya da ön kayıt v1.3 ile seçime uydurulsun. Oda onayından önce. | S |
| B5 | Rejim / beta | Y | **Oda kontrolden daha riskli:** medyan en yüksek kaldıraç oda 4,9x, kontrol 3,2x, havuz 2,9x; medyan ulcer endeksi 0,033 ↔ 0,018. Puan ile kaldıraç arasında Spearman 0,25. **Sonuç:** birincil fark beta düzeltmesiz; yükselen piyasada kohort, düşen piyasada kontrol "kazanır". Tek 12 haftalık dönem tek rejimdir. | `docs/ONKAYIT_D.md:31-32`; yerel analiz | Karar K‑3: birincil ölçüt BTC betası düzeltilmiş fark olsun ya da kontrol kaldıraç/tarz dilimine göre tabakalı çekilsin; `rejim.py` kırılımı önceden ikincil diye yazılsın. | M |
| B6 | Puan tutarlılığı | O | **Eşit olmayan pencereler:** puan, ilk dolumdan bugüne kümülatif net; pencere uzunluğu (`gecikme_gun`) odada 72–200 gün. **Kesik geçmiş:** API'nin 10.000 dolum sınırında kesik geçmiş (`dolum_siniri`) odada 4/20, havuzda 58/226; bu satırlarda puan yalnız son dönemi ölçüyor. Havuzda `kopya_eksik` 59. | `copytrade/kapi.py:545-559, 671-674`; veri | Karar K‑4: puanı günlük ortalama ya da aynı pencerede hesapla; `dolum_siniri` satırlarını işaretle veya ayır. | S |
| B7 | Kontrol tohumu | O | **Tohum koşu gününe bağlı:** tohum = SHA‑256(`secim-v1-<koşu günü>`). Seçim başka gün yeniden koşarsa farklı kontrol çıkar. "Hangi seçim koşusu geçerli" kuralı ve `secim/<tarih>` üzerine yazma engeli yok. | `copytrade/secim.py:128-140, 296` | Tarihi kapı koşusunun tarihinden al. İlk yayımlanan seçimi hash'iyle DURUM'a dondur; yeniden koşu yeni sürüm olsun. | S |
| B8 | Dondurma | O | **Ön kayıt donmadı:** ön kayıt "commit hash'i DURUM'a yazılır" diyor; DURUM'da hash yok. Sürüm 1.1 canlı izlemeyi Faz 3'ten önce başlattığı için dondurma şimdi gerekli. | `docs/ONKAYIT_D.md:5`; `DURUM.md` (hash yok) | Oda onayından önce hash'i yaz. | S |
| B9 | Kohort tanımı | O | **ITT tanımlı değil:** haftalık terfi/çıkış varken birincil serinin "etiket anındaki kohort, sonraki tüm günler" mi, değişen kohort mu olacağı yazılı değil. Değişen kohort, ölçüm penceresi içinde gölge sonucuna göre seçim demektir. **Histerezis yok:** çıkışta asgari süre yok (etre'deki "oda gir‑çık döngüsü" dersi). | `docs/ONKAYIT_D.md:11-12, 44-45`; `copytrade/kollar.py:23-38` | Karar K‑9: ITT kuralı ve çıkış asgari süresi. | S |
| B10 | Faz 3 yanlılığı | O | **Hayatta kalma yanlılığı:** Faz 3 bugünkü leaderboard'la kuruluyor. Geçmişte batmış yüksek kaldıraçlı hesaplar evrende yok; bu, kohortu (daha kaldıraçlı) kontrolden fazla kayırır. **Sonuç:** Durdurma 1 sahte biçimde geçilebilir. "İyimser üst sınır" etiketi var ama durdurma kuralında yönü belirtilmemiş. | `docs/ONKAYIT_D.md:38, 54`; B5 | Karar K‑7: Faz 3 yalnız *durdurabilir*, başlatma kanıtı sayılmaz; arşiv evreni gelince tekrar. | S |
| B11 | Aykırı değer | O | **Tek trader sonucu taşıyabilir:** birincil fark eşit ağırlıklı ortalama, havuz puanı en yüksek 1,29 (%129). Kırpılmış ya da winsorize ikincil yok. Etre aynı sorunu önceden yazılmış kırpmayla ele almış. | `docs/ONKAYIT_D.md:30-33`; veri | Karar K‑11: önceden kayıtlı kırpılmış ikincil fark (eşik veri görülmeden). | S |
| B12 | Evren | D | **Süzgeçsiz dış adaylar:** 92 dış aday (`dis_aday`, elle derlenmiş, ön süzgeçsiz) havuza ve kontrole giriyor: havuzda 38, odada 3. Ön kayıttaki havuz leaderboard evrenidir. | `copytrade/kapi.py:781-799`; veri | Karar K‑10: tabakala, ayrı raporla ya da dışla. | S |
| B13 | Tek kaynak | D | **Aday tanımı farklı:** seçim v1'de "tarz başına puanı > 0 olanların %15'i" (22 aday), ön kayıtta "havuzun %15'i" (34). **İkili uygulama:** `kollar.py`'de aday ve kontrol (`random.Random`) ayrıca uygulanmış; hiçbir üretim kodu onu çağırmıyor. | `copytrade/secim.py:55-62`; `copytrade/kollar.py:9-20`; `docs/ONKAYIT_D.md:9` | Tek uygulama; gölge motoru `secim.py` fonksiyonlarını kullansın. | S |

### 2.2 Motor doğruluğu

| No | Alan | Ciddiyet | Bulgu | Kanıt | Öneri | Emek |
|---|---|---|---|---|---|---|
| B14 | Kapsam | Y | **Kapsam evreni doğrulamıyor:** kapsam = birleşik tablo satırı / evren sayısı. Birleşik tablo, önceki koşuların aynı sürüm satırlarını da içeriyor, bu yüzden kapsam 1'i aşabiliyor (1,0042). `evren.json` yalnız bir sayı. Evren dışı (eski anlık görüntülerden) satırlar havuza girebilir; güncel evrenden eksik adres bulunamaz. | `copytrade/kapi.py:979, 1292-1301, 1325-1336`; `durum.json` (`islenen 13767`, `evren 13710`, `onceki_dosya_ayni_hesap 12584`) | Evren adres listesini yayımla; kapsam = \|sonuç ∩ evren\| / \|evren\|; evren dışı satırı işaretle; altın örnek. | S–M |
| B15 | Alfa (adım 6) | O | **Dejenere alfa:** alfa ≈ 0 (1e‑19) iken NW t ≈ ±5,8 olan 15 satır var. Standart hata ≈ 0 için koruma yok; biri adım 6 "Geçti" (0x31dea…, scalp). RAPOR'un "alfa t'ye göre ilk 15" tablosu bu satırla başlıyor. Seçimi etkilemiyor (scalp, adım 3 Kaldı). Alfa akıl sağlığı aralığı (−365…36.500) fiilen sınırsız. | `kapi/istatistik.py:84-104`; `copytrade/kapi.py:731-736, 1246-1251`; veri | Sinyal/varyans alt sınırı (dejenere seri → "Yetersiz"); altın örnek. | S |
| B16 | Bayat fiyat | O | **İşaret fiyatında yaş sınırı yok:** `Market.mark` son mumun açılışını yaşa bakmadan kullanıyor. İşlem görmeyen, listeden çıkmış ya da hafta sonu kapalı HIP‑3 coinlerinde pencere sonu K/Z'si ve V2 eşik denetimi eski fiyatla yapılır. Etre'nin "bayat fiyat" dersi bizde yürütme tarafında kapalı (1 mum sınırı), işaretleme tarafında açık. | `copytrade/defter.py:60-72`; `copytrade/golge.py:90-99` | İşarete yaş sınırı; aşılırsa `mark_missing` say. | S |
| B17 | Maliyet | O | **Tek oran:** maliyet tek oran (taker %0,045 + kayma %0,05). Lider notu: küçük coin ve HIP‑3'te iyimser. Odanın 5/20'sinde kripto dışı (HIP‑3) hacim > %50; kontrolde 3/20. Bu, kohort lehine sistematik iyimserlik riski. **Asgari emir değeri modellenmiyor (şüphe: 10 $):** defter trader dolumunu kesirli ölçekleyip çok küçük dolumları da kopyalıyor. | `copytrade/kurallar.yaml:86-88`; `copytrade/defter.py:181-188`; `arastirma/copytrade/argon_maliyet_dogrulama.md` (lider notu); veri | Karar K‑5: önce ölç (arşive `l2Book`), sonra coin sınıfı maliyeti; asgari emir etkisini bilgi olarak raporla. | M |
| B18 | Gölge likidasyonu | O | **Coin başına tasfiye:** gölge likidasyonu coin başına (o pozisyonun K/Z'si ≤ −1). Aynı trader'ın birden çok pozisyonunun toplam zararı 1 birimi aşsa bile tasfiye yok. Çapraz teminatta iyimser (kodda "iyimser sınır" notu var, ama toplam düzeyi kapsamıyor). | `copytrade/golge.py:83-99` | Trader düzeyinde toplam K/Z denetimi; altın örnek. | S–M |
| B19 | Yetim / kaçan çıkış | O | **Uzlaştırma yok:** kaynak kapanış dolumu gelmezse gölge pozisyonu açık kalıyor. Sağlama yalnız gerçekleşmiş K/Z'yi kıyaslıyor. Etre'nin "yetim pozisyon" dersi bizde kapanmadı. | `docs/codex_denetim_gölge_butunluk.md` §2; `copytrade/defter.py:152-223`; `copytrade/golge_saglama.py:80-89` | O belgedeki öneri: anlık görüntüyle uzlaştırma, `veri_kalitesi` alanı. | M |
| B20 | Dolum sayfalama | D | **Sayfa sınırında kayıp riski:** sayfa sınırında `cursor = newest + 1`; aynı milisaniyede sayfa sınırına düşen dolumlar kaybolabilir (şüphe: API'nin sayfa içi sıralamasına bağlı). İzleme yolu için aynı ms testi var, kapı yolu için yok. | `copytrade/tarama.py:91-106`; `tests/test_golge.py:166-181` (benzersiz ms) | `cursor = newest` + `tid` tekilleştirme; altın örnek. | S |
| B21 | İlişkili hesap | D | **Kontrol eksik kapsamda:** ilişkili hesap işareti yalnız katmanı olan (87) adreslere bakılıyor. Odanın 6/20'si ve kontrolün 10/20'si hiç kontrol edilmedi; seçim bu kuralı onlarda sessizce uygulamıyor. | `copytrade/kesif.py:254-265`; veri (`iliskili_not` boş) | Keşfi havuzun tamamına (226) koş. | S |
| B22 | Parçalar arası tutarlılık | D | **IP'ye bağlı sütun:** `binance_payi` 13.767 satırın yalnız 2'sinde dolu (Binance listesi bir parçada alınmış). "Tamamen boş sütun" kapısı 2 değerle geçiyor. Bilgi sütunu. | veri; `copytrade/kapi.py:593-609` | Tüm parçalarda aynı kaynak ya da sütunu kaldır. | S |
| B23 | Sürüm / köken | O | **Köken izlenemiyor:** satırlar farklı koşulardan ve farklı `now` anlarıyla birleşiyor (her parça kendi `datetime.now`'unu alıyor). RAPOR'daki dondurma SHA'ları birleştirme anındaki kodu gösteriyor, satırı hesaplayan kodu değil. Hesap sürümü elle artırılıyor; örneğin 28 Ekim'deki birleştirme ve akıl sağlığı değişiklikleri sürüm değiştirmedi. Bugün karışan satırların metrik farkı bulunamadı; risk süreçte. | `copytrade/kapi.py:968, 1325-1347`; `git log` 2026-10-28 | Satıra `kod_hash` ve `now_ms` yaz; birleştirmede farklı hash'i ayrı raporla. | S |

### 2.3 Operasyon

| No | Alan | Ciddiyet | Bulgu | Kanıt | Öneri | Emek |
|---|---|---|---|---|---|---|
| B24 | Gece yarısı | **K** | **Seçim:** Python günü başlangıçta alıyor, yayım adımı `date -u +%F` ile yeniden hesaplıyor. 00:00 UTC'yi geçen koşuda `cp -r secim/<yeni gün>` başarısız olur, sonuç kaybolur; artefakt da yok. Koşu 2 22:47'de 150 dk sınırla başladı. **Kapı:** plan işi günü bir kez hesaplıyor, her parça kendi `today`'ini alıyor; gece yarısını geçen parçanın çıktısı paketlenmez (eksik). | `.github/workflows/copytrade_secim.yml:23, 41`; `copytrade/secim.py:296`; `.github/workflows/copytrade_kapi.yml:71, 119-124`; `copytrade/kapi.py:968-969` | Günü tek yerde üret, parametre geçir (`--tarih`); çıktıyı artefakt olarak da yükle. | S |
| B25 | Zamanlama | Y | **Saatlik izleme saatlik değil:** 28 Ekim'de yalnız 3 kez çalıştı (08:40, 16:07, 21:09). Pano 90 dk eşiğiyle çoğu zaman "eski" gösteriyor. Her izleme koşusu tam test paketini koşuyor (koşu 8: 25 dk). K8 kararı ("ücretsiz Actions saatlik yeter") pratikte tutmuyor. | `.github/workflows/izleme.yml:5, 28`; Actions koşu listesi; `copytrade-izleme` commit saatleri | Karar K‑8. Teknik: test adımını kaldır; Worker cron'undan `repository_dispatch` ile tetikle (ücretsiz). | S–M |
| B26 | Arşiv | Y | **Arşiv hiç çalışmıyor:** 7/7 koşu başarısız; son hata `aws: Invalid endpoint` (R2 hesap kimliği secret'ının biçimi şüpheli). R2 indirme adımı toplamadan önce olduğu için hiçbir veri toplanmıyor. Günde ~120 yerine 2 zamanlanmış koşu. D yolunun "gerçek geçmiş evren" ve maliyet ölçümü dayanağı boş. | `.github/workflows/arsiv.yml:4-6, 23-30`; Actions koşu 40761095875 günlüğü | Secret'ı düzelt (yalnız hesap kimliği); toplamayı R2'den bağımsız yap; 24 saat kapsam kanıtı. | S |
| B27 | Tek seferlik iş akışı | O | **Sabit değerli iş akışı main'de:** `kapi_yeniden_birlestir.yml` sabit `run-id` ve `day=2026-10-28` içeriyor. İki özellik dalına `kapi.py` push'unda tetikleniyor ve 28 Ekim sonucunu yeni kodla, hesap sürümü değişmeden yeniden yayımlayabilir. | `.github/workflows/kapi_yeniden_birlestir.yml:5, 28, 42, 53` | Sil ya da yalnız `workflow_dispatch` + girdi. | S |
| B28 | Kritik yol | O | **Bilgi sütunu seçimi tıkıyor:** kırmızı bayraklar (aday başına 365 gün dolum + funding) seçim işinin içinde. 20 dk aşıldı (koşu 1 iptal), 150 dk'ya çıkarıldı; bu, B24 riskini büyüttü. Bilgi sütunu kritik sonucu bekletiyor. | `.github/workflows/copytrade_secim.yml:23`; `copytrade/secim.py:319-325`; koşu 40778018614 | Seçimi bayraksız yayımla, bayrakları ayrı iş yap. | S |
| B29 | Hata yutma | D | **Kalıntı `\|\| true`:** eski inceleme aracında komut çıkışı `\|\| true` ile örtülüyor (AGENTS kuralı). Diğer iş akışları ve betikler temiz: `set -euo pipefail`, eksik koşu kırmızı. | `.github/workflows/inceleme.yml:21` | Kaldır ya da iş akışını arşivle. | S |

### 2.4 Test kalitesi

| No | Alan | Ciddiyet | Bulgu | Kanıt | Öneri | Emek |
|---|---|---|---|---|---|---|
| B30 | Testsiz kritik yollar | O | **Testi olmayan riskli yollar:** (a) iş akışı tarih mantığı (B24); (b) dejenere alfa (B15); (c) kapı dolum sayfalamasında aynı ms (B20); (d) kapsamın küme denetimi (B14); (e) pano canlı Keşif yolu: testler GitHub API'yi hep 500'le kesiyor (B34); (f) **ön kayıt birincil analizinin (kohort–kontrol günlük fark, haftalık blok bootstrap, karar) kodu yok.** Analiz günü yazılırsa "sonucu gördükten sonra yazılmış analiz" riski doğar. | sg-pano `test/pano_yardim.js:28`; `grep -rn kohort copytrade` → yalnız `kollar.py`; 265 test listesi | Birincil analiz fonksiyonu ve altın örnekleri şimdi, veri görülmeden yazılsın ve ön kayıtla birlikte dondurulsun. | M |

### 2.5 Güvenlik ve kurallar

| No | Alan | Ciddiyet | Bulgu | Kanıt | Öneri | Emek |
|---|---|---|---|---|---|---|
| B31 | Performans körlüğü | O | **Körlük yalnız arayüzde:** pano kol toplamlarını ve trader başı gölge sonucunu kilitliyor. Ancak (1) herkese açık `copytrade-izleme/izleme/durum.json` trader başına `sanal_kopya.getiri` içeriyor ve izleme listesi kol alınca `kol` da yazılacak, yani kohort–kontrol farkı ham veriden hesaplanabilir; (2) trader sayfasında trader'ın kendi K/Z eğrisi ve t0 sonrası performans konisine dayalı **sağlık ışığı** kol ile birlikte görünüyor. Bu, ön kayıttaki "arada yalnız veri kalitesi" ilkesiyle çelişiyor; Telegram `/durum` da ışığı gösteriyor. Ajanların (rapor/sağlık işlerinde) farkı yanlışlıkla hesaplaması da açık risk. | `copytrade/izleme_motoru.py:207-221, 486, 562`; `worker/src/index.js` `/durum`; sg-pano `index.html:518`; `docs/ONKAYIT_D.md:34` | Karar K‑6. | S–M |
| B32 | Kişisel davranış verisi | D | **Kararlar açık:** Worker `GET /kararlar` kimlik doğrulamasız. Kararlar (açtı/atladı) zaten açık veri dalında da duruyor. Anahtar değil, ama kullanıcının kişisel karar kaydı. | `worker/src/index.js:195-197`; `.github/workflows/izleme.yml` (kararlar adımı) | Bilinçli kabul ya da gizli başlık / ayrı özel depo. | S |
| B33 | Kişisel veri (git) | D | **E-posta açık:** açık repo commit'lerinin yaklaşık 124'ünde yazar e-postası kişisel bir adres (değer buraya yazılmadı). | `git log --format=%ae` | GitHub "noreply" e-postasına geç; geçmiş için kullanıcı kararı. | S |

### 2.6 Pano

| No | Alan | Ciddiyet | Bulgu | Kanıt | Öneri | Emek |
|---|---|---|---|---|---|---|
| B34 | Keşif/Huni verisi | Y | **Canlı okuma hep düşüyor:** pano `copytrade/kapi/<tarih>/kesif.json` arıyor; yayıncı `kesif/kesif.json` yazıyor; veri dalındaki tarih klasöründe `kesif.json` yok. Canlı okuma her seferinde düşüyor ve örnek aday listesine geçiliyor; Huni/aday görünümü sahte veri gösteriyor. **API sınırı:** her tarih klasörü için kimliksiz GitHub API çağrısı yapılıyor (60/saat sınırı). | sg-pano `index.html:154, 648-666`; `.github/scripts/kapi_yayimla.sh:12, 26`; `git ls-tree origin/copytrade-kapi` | Yolu düzelt (`raw.githubusercontent` + sabit yol); örneğe düşüşte tam genişlikte uyarı; canlı yol için sözleşme testi. | S |
| B35 | Tazelik | O | **Alarm yorgunluğu:** 90 dk "eski" eşiği gerçek izleme sıklığıyla (4–8 sa) uyumsuz; uyarı sürekli yanıyor. Ofis sayfası doğru biçimde "örnek veri" şeridi taşıyor; ana panoda "ÖRNEK VERİ" yalnız `kaynak` alanına bağlı. | sg-pano `index.html:156, 389-400`; B25 | B25 çözülünce eşiği gerçek sıklığa bağla; ayrıca "son başarılı koşu" saatini göster. | S |

---

## 3. Karar gerektirenler (proje sahibine seçenekler; bu denetimde uygulanmadı)

| No | Konu | Seçenekler | Denetçi notu |
|---|---|---|---|
| K‑1 | **Güç (B1)** | (a) **Birincil ölçütü değiştir:** havuzun tamamında geçmiş puan ↔ ileri getiri sıra korelasyonu (kalıcılık testi, `kalicilik.py`). Gölge zaten "havuzun hepsi" için planlı. Gerçekçi senaryoda güç %15–25 (12 hf), %18–41 (24 hf); güçlü senaryoda %75–99. Kohort–kontrol testinde aynı değerler %5–16 ve %26–66 (Ek A2). (b) **Kontrolü oda ile eşleştir:** tarz ve kaldıraç dilimine göre tabakalı kontrol; varyansı düşürür. (c) **Süreyi uzat:** 24–36 hafta (B1 tablosu). (d) **Sınırı kabul et:** "bu ölçekte yalnız büyük (yıllık > %40) farklar sınanabilir" ifadesini ön kayda yaz. | Ön kayıt veri görülmeden değişmeli; şu an gölge verisi yok, değişiklik meşru. a ve b birlikte en büyük kazancı verir. |
| K‑2 | **Havuz tanımı (B4)** | (a) Havuza statik adım 3 süzgeci (tarz, kısa işlem payı ≤ %25, kaldıraç ≤ 3x/10x) ekle ve odayı yeniden üret. (b) Ön kaydı v1.3 ile "havuz = adım 1+2" diye düzelt, gerekçesini yaz. | Oda onayı öncesi. a, ön kayıtla uyumlu olan. |
| K‑3 | **Beta / rejim (B5)** | (a) Birincil = BTC betası düzeltilmiş fark (bugün ikincil). (b) Ham fark birincil kalsın, beta düzeltilmiş fark eş-zorunlu koşul olsun. (c) Kaldıraç tabakalı kontrol (K‑1b ile aynı). | Oda kontrolden belirgin daha kaldıraçlı; ham fark piyasa yönünü ölçer. |
| K‑4 | **Puan tanımı (B3, B6)** | (a) Günlük ortalama net (pencere uzunluğundan bağımsız). (b) Aynı takvim penceresi zorunlu (kısa geçmişli → puansız). (c) `dolum_siniri` satırlarını puansız say. (d) İkincil kohort: adım 5–6'yı geçenler (ayrı kol, bilgi). | Seçim v1 başlangıç etiketi; değişiklik oda onayından önce. |
| K‑5 | **Maliyet (B17)** | (a) Önce ölç (arşive `l2Book`), sonra coin sınıfı maliyeti. (b) Şimdilik HIP‑3/küçük coin için muhafazakâr ikinci oran ile duyarlılık raporu (bilgi). | Kararı değiştirmeyen duyarlılık raporu hemen yapılabilir. |
| K‑6 | **Körlük (B31)** | (a) Analiz tarihine kadar `kol`'u açık `durum.json`'a yazma; eşleme ayrı, şifreli ya da gecikmeli dosyada dursun. (b) Sağlık ışığını yalnız veri kalitesi ve risk (kaldıraç, likidasyon mesafesi) ile sınırla; performans konisini analiz sonrasına bırak. (c) Mevcut hâli bilinçli kabul et ve ajan görevlerine "kol bazında getiri hesaplama" yasağı ekle. | Açık repoda tam körlük zor; b ve c ucuz. |
| K‑7 | **Faz 3 / Durdurma 1 (B10)** | (a) Faz 3 yalnız durdurabilir, başlatma kanıtı sayılmaz. (b) Arşivin gerçek geçmiş evrenini bekle. | — |
| K‑8 | **İzleme sıklığı (B25)** | (a) Worker cron'u saatlik `repository_dispatch` atsın (ücretsiz). (b) Ücretli plan. (c) Gecikmeyi kabul et ve pano eşiğini güncelle. | Gölgenin kendisi dolumdan hesaplandığı için gecikme sonucu bozmaz; bildirim ve tazelik etkilenir. |
| K‑9 | **ITT ve histerezis (B9)** | (a) Birincil: etiket anındaki kohortun sonraki tüm günleri (terfi edenler yeni alt kohort). (b) Çıkış için asgari süre / ardışık iki hafta şartı. | — |
| K‑10 | **Dış adaylar (B12)** | (a) Havuzdan ve kontrolden çıkar. (b) Tabakala ve ayrı raporla. | — |
| K‑11 | **Aykırı değer (B11)** | Önceden kayıtlı ikincil: trader başı dönem getirisi kırpılmış / winsorize fark (eşik veri görülmeden). | — |
| K‑12 | **Seçim kimliği (B7, B8)** | Tohum tarihi = kapı tarihi; ilk yayımlanan seçim + ön kayıt hash'i DURUM'a; yeniden koşu yeni sürüm. | Oda onayından önce. |

---

## 4. Etre'den alınacaklar (öncelik sırasıyla; yalnız fikir)

`docs/etre_envanter.md`'nin kapsadığı maddeler (deney bildirgesi, geçerlilik günlüğü, çalışma kalitesi bekçisi, trader yaşam döngüsü,
gelişim günlüğü) burada tekrar edilmedi. Aşağıdakiler envanterde **olmayan** ya da eksik kalanlardır.

1. **Güç bilinciyle raporlama.** Etre ileri analizinde "|rho| > 0,1 dışlandı, daha küçükleri dışlanamaz" diye saptanabilirliği yazmış.
   Bizim ön kayıtta saptanabilir en küçük fark yok (B1). Önerim: her karar raporuna MDE satırı.
2. **Havuz dışı kontrol.** Etre'nin keşfinde, ölçütü **geçemeyen** ama aynı kaynaktan gelen rastgele hesaplardan oluşan bir kontrol grubu var.
   Bu, "işe yarayan kural mı, kaynak mı" sorusunu ayırıyor. Bizde kontrol yalnız havuzdan. Kapı ön elemesinin kendi değerini sınayan ikinci
   bir kontrol kolu (adım 1–2'yi geçemeyen ama aktif hesaplar) ucuz bir eklemedir.
3. **Puan ↔ ileri sonuç geriye dönük analizi.** Etre'de bu, çakışmasız pencerelerle ve kırpmalı yapılmış. Bizde `kalicilik.py` var ama veriye
   bağlanmadı (Faz 3). K‑1a ile birincil ölçüte dönüşebilir.
4. **Kırpmalı (trimmed) sonuç ikincili.** Etre aykırı kazancın sonucu taşımasını önceden belirlenmiş kırpmayla sınamış (B11). Sayılar
   taşınmamalı; kavram ön kayda ikincil olarak girmeli.
5. **"Temiz veri" başlangıç damgası.** Etre, bir veri hatası bulunca analizi damgadan sonrasına kesip eski deneyi korumuş. Bizde hesap sürümü
   var, ama gölge/izleme için "temiz başlangıç" alanı yok (B23 ile birlikte).
6. **Fiyat sıçrama koruması.** Etre, yanlış kaynaktan gelen mumların sahte kâr yarattığını bulup "kendi örneğimizden 20 kat uzak mumu reddet"
   kuralı koymuş. Bizde mum için akıl sağlığı yok (HIP‑3 sığ piyasalarda tek işlemli saatlik açılış). B16 ile birlikte.
7. **Oda giriş/çıkış histerezisi.** Etre'de eşik sıfırlanması ve gir-çık döngüsü yaşanmış (B9).
8. **Arayüz küçükleri** (düşük öncelik; ayrıntı sg-pano `docs/etre_fikirler.md`): sistem sağlığı rozeti (B25/B35'i görünür yapar), sekme
   başlığında durum, gizli sekmede yenilemeyi durdurma.

### Onların yaptığı, bizim kaçınmamız gereken hatalar

| Hata (etre günlüğü) | Bizdeki durum |
|---|---|
| Ön kayıtlı ileri test penceresi **içinde** çıkış kuralını değiştirmek | Ön kayıt "değişiklik yeni sürüm" diyor; ama dondurma hash'i yok (B8). Önce dondur. |
| Kısa ve kirli veride ağırlık öğrenmek, çakışan 48 sa pencerelerle iyimser ileri test | Bizde öğrenen puan yok (iyi). Haftalık terfi/çıkış penceresi tanımı (B9) bu tuzağa açılmasın. |
| Çok sayıda eşzamanlı hipotez (ileri test ailesi) ve çoklu test düzeltmesi yok | Bizde birincil tek (V0, oda ↔ kontrol). V1/V2, taban, elle, aday kolları "keşif" diye etiketlenmeli. |
| Yanlış kaynaktan fiyat → sahte lab kârı | Mum kaynağımız Hyperliquid'in kendisi (risk düşük); sıçrama/bayatlık koruması yok (B16). |
| Yeniden başlatmada funding'i iki kez yazmak (bellekte durum) | **Sorun yok:** bizde funding durumsuz, saatlik ızgaradan yeniden hesaplanıyor (`defter.py:224-244`). |
| Aynı coinde ters yönlü ikinci pozisyon (borsa net tutar) | **Sorun yok:** defter coin başına net pozisyon tutuyor (`defter.py:164-221`). |
| İzlemeden çıkarılan trader'ın sinyallerini atıp yetim pozisyon bırakmak | Kısmen açık (B19). Kural: kol değişse de açık gölge pozisyonu kapanana kadar izlensin. |
| Seçimin havuzu yendiğini varsayıp gerçek paraya geçiş yolu kurmak | **Sorun yok:** bizde emir yolu yok (Bölüm 5). |

---

## 5. "Sorun yok" diye kontrol edilen alanlar

- **Gerçek emir / para çekme yolu kapalı.** Kodda `exchange` uç noktası, imza, özel anahtar, emir veya çekim yok
  (`git grep` ile `exchange|sign|privateKey|withdraw|order` aramaları boş). `requirements.txt` ve Worker `package.json`'da borsa SDK'sı yok.
  Worker yalnız Telegram mesajı ve karar kaydı yapıyor.
- **Anahtar ve token sızıntısı yok.** Desen taraması (API anahtarı, GitHub/Slack/OpenAI token biçimleri, Telegram bot token biçimi, özel
  anahtar başlığı) yalnız belge ve iş akışlarındaki secret **adlarını** buldu. `wrangler.toml`'da hesap kimliği yok. Actions günlüklerinde
  secret'lar maskeli.
- **Geleceğe bakma (kapı defteri).** Gecikmeli yürütme, hedeften sonraki ilk mumun açılışı; işaretleme o ana kadar açılan son mum. Sermaye
  ölçeği dolum anındaki hesap değeri (`defter.py:60-72, 129-150`). Kontrol, puana bakmadan ve tekrarlanabilir tohumla çekiliyor
  (`secim.py:128-140`; altın örnek `tests/test_secim.py`). Rejim ve kalıcılık modüllerinin geleceğe bakmama testi lider denetiminde 0 fark
  (`argon_rejim_kalicilik.md`).
- **Çoklu test (kapı içinde).** BHY, adım 1–4'ü geçen tüm aile üzerinde (m = 24), p'si olmayan üye p = 1 (RAPOR). Plasebo 10.000 tekrar.
- **Null altında yanlış geçme.** Ön kayıt kuralı (alt sınır > 0 ve kohort > 0) simülasyonda null'da %1–5 geçiyor (Ek A1): kural fazla
  serbest değil.
- **Funding ve net pozisyon muhasebesi** (yukarıdaki tablo). Miras pozisyonların kapanışı yeni ters pozisyon açmıyor (`defter.py:182-188`).
- **Hata gizleme.** Kapı ve izleme yayımlama betikleri `set -euo pipefail`; eksik koşu işi kırmızı yapıyor; akıl sağlığı kapısı yayımı durduruyor
  (son örnek: run 27). Tek istisna B29.
- **Eşzamanlılık.** Veri dalına yazan işler `pull --rebase` + 3 deneme ile yazıyor; izleme ve seçim `concurrency` grubu tanımlı.
- **"KeyError: 'evren'" düzeltmesi** regresyon testiyle korunuyor (`tests/test_eksik_koşu_dis_aday.py:108-113`).
- **Test paketi** yeşil (265). Defter, gölge V0/V1/V2, seçim, bayrak, akıl sağlığı kapısı, ön kayıt ↔ yaml (V2 eşikleri) için altın örnekler var.
- **Pano örnek ↔ gerçek ayrımı (ana pano izleme verisi ve ofis).** Ana pano canlı `durum.json`'u okuyor; ofis sayfası sabit "örnek veri"
  şeridi taşıyor. Sorun yalnız Keşif yolunda (B34).
- **Telegram'da performans içeriği.** Bildirim metni yalnız coin, yön, fiyat ve hesap payı içeriyor; K/Z, kol toplamı ve kıyas yok
  (`worker/src/index.js:42-48`). Işık bilgisi için B31.

---

## Ek A — Güç analizi (yöntem ve çıktı)

**Üretici:** `copytrade/sentetik.py` (`origin/codex/sentetik`) `trader_uret`. Yetenekli trader'ın günlük beklenen getirisi α, diğerinin 0,
normal gürültü σ. Ortak piyasa etkeni eklendi (ρ = 0,3).

**Düzenek:**
- 226 trader (havuz), %20'si yetenekli (sentetik deneyle aynı).
- Seçim: ilk 200 günün ortalamasına göre en iyi N (secim v1'in idealize hali).
- Kontrol: rastgele N.
- İleri dönem: 84 gün (12 hafta) ya da 168 gün (24 hafta). Yetenek ileride aynen sürüyor (iyimser varsayım).
- Ön kayıt kuralı: günlük fark ortalamasının haftalık (7 gün) çakışmasız blok bootstrap %95 alt sınırı > 0 **ve** kohort ortalaması > 0.
- 300 tekrar, 1.000 bootstrap.

**σ dayanağı:** havuzdaki 226 adresin ~200 günlük puanının standart sapması 0,283. Saf gürültü olsaydı σ ≈ 0,283 / √200 ≈ **%2,0/gün**
(gerçek farklar da içerdiği için üst sınır). %1,5 de denendi.

**A1 — Ön kayıt kuralının geçme oranı**

| α (günlük) | σ | Oda | 84 gün | 168 gün | Ortalama fark (günlük) |
|---|---|---|---|---|---|
| 0 (null) | %1,5–2 | 10 / 20 | %2 / %5 | %2 / %1 | ≈ 0 |
| %0,08 | %1,5 | 10 / 20 | %9 / %13 | %11 / %16 | %0,026–0,030 |
| %0,08 | %2 | 10 / 20 | %5 / %8 | %7 / %8 | %0,018–0,020 |
| %0,16 | %1,5 | 10 / 20 | %51 / %66 | %71 / %87 | %0,10–0,12 |
| %0,16 | %2 | 10 / 20 | %26 / %33 | %41 / %49 | %0,08–0,09 |

**A2 — Alternatif birincil: havuz geneli Spearman (geçmiş puan ↔ ileri ortalama), tek yönlü %5**

| α | σ | 84 gün | 168 gün |
|---|---|---|---|
| 0 | %1,5–2 | %3–6 | %3–6 |
| %0,08 | %1,5 / %2 | %25 / %15 | %41 / %18 |
| %0,16 | %1,5 / %2 | %99 / %75 | %100 / %92 |

**A3 — Saptanabilir en küçük fark (%80 güç, ≈ 2,8 × SE; null altında 400 tekrar)**

| σ | Oda | Gün | SE (günlük) | MDE (günlük) | MDE (dönem) | MDE (yıllık) |
|---|---|---|---|---|---|---|
| %1,5 | 10 | 84 | %0,061 | %0,170 | %14,2 | ~%62 |
| %1,5 | 20 | 84 | %0,041 | %0,115 | %9,6 | ~%42 |
| %1,5 | 20 | 168 | %0,029 | %0,082 | %13,8 | ~%30 |
| %2,0 | 10 | 84 | %0,079 | %0,222 | %18,6 | ~%81 |
| %2,0 | 20 | 84 | %0,055 | %0,154 | %12,9 | ~%56 |
| %2,0 | 20 | 168 | %0,041 | %0,114 | %19,1 | ~%41 |

**Sınırlar:** üretici homojen σ'lı. Gerçekte oda daha yüksek σ'lı (B5); bu, MDE'yi büyütür. Yeteneğin ileride aynen sürmesi iyimser. Kalın
kuyruk ve trader arası farklı korelasyon modellenmedi. Simülasyon betikleri repo dışında tutuldu (kod değişikliği yok). Aynı düzenek
`sentetik.py` üzerine yaklaşık 40 satırla yeniden kurulabilir.

## Ek B — Veri kontrolleri (yerel, `copytrade-kapi` @ `db01758`)

| Kontrol | Sonuç |
|---|---|
| Satır / tekil adres | 13.767 / 13.767; `kaynak`: leaderboard 13.675, dis_aday 92 |
| Satır kaynağı | önceki dosya (aynı hesap) 12.584, bu koşu 1.183; hesap sürümü tek (`v1.1-2026-10-27d`) |
| Havuz (adım 1+2, tarz intraday/swing) | 226 (intraday 127, swing 99); puanı > 0: 141 |
| Oda / kontrol / ortak | 20 / 20 / 1 |
| Odada kapı adımları | adım 3 Geçti 14 / Kaldı 4 / Yetersiz 2; adım 4 Geçti 8; adım 5 Geçti 3; adım 6 Geçti 2 |
| Dejenere alfa (\|alfa\| < 1e‑9, \|t\| ≥ 2) | 15 satır; 1'i adım 6 Geçti |
| `binance_payi` dolu | 2 / 13.767 |
| İlişkili hesap bakılmamış | oda 6/20, kontrol 10/20 |
