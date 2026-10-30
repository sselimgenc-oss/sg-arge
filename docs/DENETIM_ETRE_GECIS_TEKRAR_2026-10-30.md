# Etre geçişi: yeniden bağımsız denetim — 30 Ekim 2026

**Kullanıcının isteği yaklaşık %33 oranında karşılandı.**

Hesap: 12 alan eşit ağırlıkta; TAMAM = 1, KISMİ = 0,5, YOK = 0. Bir alan tamam, altı kısmi, beş yok: 4/12. Bu **ilerleme puanı**, çalışan Etre kopyasının tamamlanma yüzdesi değildir. E2–E5 hâlâ yapılmadı.

**Kesit:** 30 Ekim 2026, yaklaşık 19:32 TSİ. `sg-arge main` [`206086b`](https://github.com/sselimgenc-oss/sg-arge/commit/206086b2dab2009f69a13887740d163cd0d061e1), `sg-pano main` [`8bd1331`](https://github.com/sselimgenc-oss/sg-pano/commit/8bd133196a4f062e9f3be4f3eb75119251938217), Etre [`f3f5cff`](https://github.com/ismailkaraabc/etre-trading-office/commit/f3f5cff92d6db2fff62b6f7753c45343e00583ba). Eski [denetim #442](https://github.com/sselimgenc-oss/sg-arge/pull/442) 18:43 TSİ kesitidir; bu rapor onun güncellemesidir. Açık eski taslak [#434](https://github.com/sselimgenc-oss/sg-arge/pull/434) E2 yerine alınmış sayılmadı.

## Önceki rapora düzeltme

- Önceki raporda “dakikalık Worker oda yoklaması yok” demiştim. **Yanlıştı.** [Worker `runCron`:169–180](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/src/index.js#L169-L180) oda trader'larının `userFillsByTime` dolumlarını çekiyor; [wrangler:6](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/wrangler.toml#L6) cron'u her dakika. Bu yüzden “hız” artık **KISMİ**. Canlıda her dakikanın gerçekten sorunsuz çalıştığına ilişkin süre dağılımı yine doğrulanmadı.
- Önceki iki yüksek #441 bulgusu **kodda düzeltildi**: [pozisyon yaşı doğru adla](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/saglik_hatti.py#L44-L49) yayımlanıyor; üretim anında sıfır veren tazelik ölçüsü çıkarıldı, okuma anı tazeliği [Worker'da](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/src/index.js#L290-L301) kalıyor. [#441](https://github.com/sselimgenc-oss/sg-arge/pull/441) birleşti.
- [#439](https://github.com/sselimgenc-oss/sg-arge/pull/439) ve [sg-pano #46](https://github.com/sselimgenc-oss/sg-pano/pull/46) GPL-3.0/atıfla birleşti. [#445](https://github.com/sselimgenc-oss/sg-arge/pull/445) dolum→Worker algılama süresini ölçen kodu ekledi. **Canlı sonuç ve pano görünümü henüz kanıtlanmadı.**

## 12 alan: güncel tablo

| Alan | Etre kanıtı | Bizde main / açık PR | Durum ve açık iş |
|---|---|---|---|
| 1. Program, kullanılabilirlik | [Tek masaüstü/ofis, README](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/README.md#L5-L43) | main: [mobil pano ve ayrı ofis](https://github.com/sselimgenc-oss/sg-pano/blob/8bd1331/README.md#L3-L25). Açık Etre PR'ı yok. | **KISMİ**; Etre'nin tek canlı kasa/ofis akışı yok. |
| 2. Plan/yol haritası | [KULLANIM tek program](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/KULLANIM.md#L1-L22), [günlük](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/docs/GELISIM_GUNLUGU.md#L1-L11) | main: [DURUM hedef + çalışanlar](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/DURUM.md#L4-L17), [E1–E6 görev](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/GOREV_ETRE_GECIS.md#L27-L68), [günlük](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/GELISIM_GUNLUGU.md#L1-L22). | **KISMİ**; görevde istenen tek yol haritası tablosu DURUM başında yok. |
| 3. Veri hattı | [Ağırlık/429/fiyat koruması](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/hl/api.py#L20-L107), [WS ve katmanlı yoklama](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/hl/izle.py#L1-L73), [kalite](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kalite.py#L22-L82) | main: [#441 sağlık](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/saglik_hatti.py#L1-L12), [#445 gecikme](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/gecikme.py#L19-L49), Worker dolum yoklaması. Açık Etre PR'ı yok. | **KISMİ**; 429 sayacı/ağırlık bütçesi, giriş kayması, akış sessizliği, hata sayısı ve tek veri kaynağı yok. |
| 4. Risk ve çıkış | [Kaldıraç stop/zirve/süre/ana para](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kurallar.py#L34-L43), [ortak karar](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kurallar.py#L195-L239) | main: [eski gölge V2](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/golge.py#L64-L76); #434 taslak, geçiş kapsamında birleştirilmedi. | **YOK**; Etre çıkış seti ve ön kayıtlı paralel lab yok. |
| 5. Mimari | [Tek süreç/olay döngüsü](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/motor.py#L1-L9), [tek kasa](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kasa.py#L1-L10) | main: [ayrı saatlik motor](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/izleme_motoru.py#L694-L743), Worker ve pano; E2 motoru yok. | **YOK**; oda için tek kasa/motor ve v1 yanında v2 yok. |
| 6. Yönetim/sadelik | [Gerekçeli oda geçişleri](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/trader.py#L1-L5), [trader_log](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/trader.py#L83-L96) | main: [v1.3 seçim](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/secim.py#L134-L148), [#443 temizlik](https://github.com/sselimgenc-oss/sg-arge/pull/443/files). | **KISMİ**; Etre oda terfi/düşmesi yok; görevde “arşivle” denilen belgeler silindi. |
| 7. Mühendislik kalitesi | [Saf kural fonksiyonları](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kurallar.py#L1-L10), [kalite eşikleri](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kalite.py#L22-L40) | main: [altın örnek kuralı](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/AGENTS.md#L20-L25), #445 CI 523 Python + 39 Worker testi geçti. | **KISMİ**; canlı çıktı yok, eski testler #443 ile silindi, hata sayımı geniş `catch` altında kayboluyor. |
| 8. Pano/ofis | [Canlı kasa/açık/kapalı](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/web/canli.js#L25-L80), [izometrik ofis](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/web/ofis.js#L31-L49) | main: [eski pano sekmeleri](https://github.com/sselimgenc-oss/sg-pano/blob/8bd1331/index.html#L130-L145), [ofis uyarlayıcısı](https://github.com/sselimgenc-oss/sg-pano/blob/8bd1331/ofis/gercek.js#L62-L75). #46 lisans dışında E5 PR'ı yok. | **YOK**; Etre kartı, yeni ofis ve gerçek ekran görüntüsü yok; ekran hâlâ hesap yapıyor. |
| 9. Simülasyon gerçekliği | [Derinlik/makas dolumu](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/sim.py#L111-L126), [funding/tasfiye](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kaldirac/masa.py#L429-L483) | main: [eski gölge](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/golge.py#L111-L164), [sabit kayma](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/kurallar.yaml#L1-L13). | **YOK**; E2 gerçekçi v2 motoru gelmedi. |
| 10. Hız | [İlk 10 oda WS, diğerleri yoklama](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/hl/izle.py#L31-L73) | main: [Worker her dakika](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/wrangler.toml#L6), [oda dolumları](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/src/index.js#L169-L184), saatlik [durum üretimi](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/.github/workflows/izleme.yml#L1-L6). | **KISMİ**; Worker hızı var, ancak kopya motoru ve pano saatlik dosyaya bağlı. Gerçek gecikme dağılımı yok. |
| 11. Kopya mekaniği/çıkışlar | [open/increase/reduce/close](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/hl/izle.py#L1-L5), [orantılı azalt](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/etre2/kaldirac/masa.py#L277-L295) | main: [eski gölge dolum filtresi](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/golge.py#L23-L61), E2/E3 PR yok. | **YOK**; ortak portföy, tam ayna ve Etre kapanış nedeni kaydı yok. |
| 12. Hedef netliği | [README tek amaç](https://github.com/ismailkaraabc/etre-trading-office/blob/f3f5cff/README.md#L5-L9) | main: [DURUM başında tek hedef cümlesi](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/DURUM.md#L4-L7). | **TAMAM**; kapsam ve gerçek para yasağı görünür. |

## E1–E6 ve bitti tanımı

| Adım | Durum | Kanıt / eksik |
|---|---|---|
| Lisans | **TAMAM** | [#439](https://github.com/sselimgenc-oss/sg-arge/pull/439), [#46](https://github.com/sselimgenc-oss/sg-pano/pull/46) birleşti; Etre LICENSE ile aynı GPL-3.0 metni ve atıf. |
| E1 | **KISMİ** | [#441](https://github.com/sselimgenc-oss/sg-arge/pull/441) + [#445](https://github.com/sselimgenc-oss/sg-arge/pull/445) birleşti; sağlık ve dolum→Worker gecikme kodu var. Tek kaynak ve canlı gecikme çıktısı yok. |
| E2 | **YOK** | Sabit tutar/tek kasa/yeni motor v2 PR'ı yok. #434 taslak eski yöntem. |
| E3 | **YOK** | Etre çıkış seti, nedenler, ileri test labı yok. |
| E4 | **YOK** | Gerekçeli, beklemeli Etre oda işletimi yok; v1.3 seçim korunmuş. |
| E5 | **YOK** | Etre panel kartı/ofisi için kod PR'ı ve ekran görüntüsü yok. |
| E6 | **KISMİ** | [#443](https://github.com/sselimgenc-oss/sg-arge/pull/443) 164 dosya temizledi; iş akışı sayısı güncel main'de 12. Tek motor/ayar yok; eski belgeler `docs/arsiv/` yerine silindi. |

[Görevdeki “bitti” koşulları](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/GOREV_ETRE_GECIS.md#L79-L82): Etre kartı ve ekran görüntüsü **yok**; sabit tutarlı motor/çıkış/tasfiye **yok**; Etre oda işletimi **yok**; dolum→Worker gecikmesi **kodda var ama gerçek çıktı ve pano gösterimi yok**; tek veri kaynağı **yok**; eski parçaların görevde tarif edilen arşivi **yok**; temiz bağımsız denetim **yok**.

## Yeni bulgular

### YÜKSEK — #445 canlı gecikme kabul kanıtı eksik

**Kanıt:** [#445 izleme işi:73–79](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/.github/workflows/izleme.yml#L73-L79) yalnız `GECIKME_URL` varsa çalışıyor. `copytrade-izleme/izleme/gecikme.json` yeniden denetim anında **404**. Son [canlı `durum.json`](https://github.com/sselimgenc-oss/sg-arge/blob/copytrade-izleme/izleme/durum.json) `uretildi=2026-10-30T15:36:40Z`, 91 trader; `saglik_hatti` yok. Onu üreten [koşu 41082224874](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41082224874) eski `1ca8d28` commit'ini çalıştırdı, #441/#445'ten önce başladı. #445 sonrası [Worker dağıtımı 41089521540](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41089521540) başarılı; D1 şema ve dağıtım adımları yeşil. **Sonraki saatlik üretim henüz gözlenmedi.**

**Etki:** yeni ölçünün üretimde dolduğu, panoda gösterildiği ve beklenen yaklaşık 1–2 dk aralığında olduğu kanıtlanmadı. **Yapılacak:** ilk #445 tabanlı saatlik koşuda `gecikme.json` ve `saglik_hatti` içeren gerçek çıktıyı denetle; gerekirse `GECIKME_URL` yapılandırmasını tamamla; pano ekran görüntüsü ekle.

### YÜKSEK — #445 gecikme özeti eski/eksik örneklerden oluşabilir

**Kanıt:** [Worker:184–191](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/src/index.js#L184-L191) her trader için yalnız **en yeni dolumun** gecikmesini `son_gecikme`ye yazıyor. Birden çok dolumun daha yavaş eski olanları atlanıyor. [GET /gecikme:381–383](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/worker/src/index.js#L381-L383) bütün son kayıtları zaman süzmeden döndürüyor; [Python özet:19–27](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/copytrade/gecikme.py#L19-L27) eski kayıtları da aynı medyana katıyor.

**Etki:** yayımlanacak medyan “son saatlik oda sinyallerinin gecikmesi” anlamına gelmez; uzun süre işlem yapmayan trader'ın eski örneği ve aynı yoklamada atlanan yavaş dolumlar hızı olduğundan iyi gösterebilir. **Yapılacak:** her görülen yeni dolumu veya en azından en yavaş/yeni dolum sayacıyla pencere özetini sakla; örnek `zaman`ına göre taze pencere uygula; `n` ve kapsamı göster.

### YÜKSEK — #443 arşiv ve test koruma sözüyle çelişiyor

**Kanıt:** [GOREV:31–32](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/GOREV_ETRE_GECIS.md#L31-L32) biten/askıdaki `GOREV_*.md` dosyalarını `docs/arsiv/`e taşımayı, silmemeyi söylüyor. [#443 dosya listesi](https://github.com/sselimgenc-oss/sg-arge/pull/443/files) 29 görev belgesi ve 7 test dosyasını **sildi**; `docs/arsiv/` güncel ağaçta yok. [AGENTS:16](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/AGENTS.md#L14-L17) “testler silinmez” diyor. #443 açıklaması ayrı bir kullanıcı temizlik kararına dayanıyor; dosyalar Git geçmişinde duruyor.

**Etki:** yazılı kabul ölçütü ile fiili temizlik ayrıştı; eski testleri güncel depoda yeniden çalıştırmak ve eski görev kararını izlemek zorlaştı. **Yapılacak:** son kullanıcı kararının arşiv/test kuralını hangi kapsamda değiştirdiğini görevde açıkça kaydet; korunacak v1 ölçüm/test kanıtını erişilir sürümlü yerde tut. Bu bir sır sızıntısı veya çalışan akışta kanıtlanmış kırılma değildir.

### ORTA — pano hâlâ hesap yapıyor

**Kanıt:** [sg-pano `ofis/gercek.js`:68–75](https://github.com/sselimgenc-oss/sg-pano/blob/8bd1331/ofis/gercek.js#L68-L75) K/Z ve teminatı trader hesabından tekrar ölçekliyor; `lik_uzaklik` null. [AGENTS:52](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/AGENTS.md#L50-L52) ve [E5](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/GOREV_ETRE_GECIS.md#L60-L65) ekranın hazır tek JSON sayısını göstermesini istiyor.

**Etki:** ofis/pano/motor aynı ölçekte kalmayabilir; Etre kartı ve likidasyon mesafesi tamamlanmış sayılmaz. **Yapılacak:** hesapları motorda tek kez yapıp birimiyle `durum.json`a koy; pano/ofis/Telegram yalnız gösterim yapsın; gerçek çıktı sayılarını yan yana denetle.

### ORTA — günlük ve iş durumu güncel kodla tam eşleşmiyor

**Kanıt:** [günlük:16–19](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/GELISIM_GUNLUGU.md#L16-L19) v1.6 ve 37 Worker testi diyor; [sözleşme:1](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/docs/VERI_SOZLESMESI.md#L1) v1.7, #445 CI günlüğü 39 Worker testi gösteriyor. [DURUM:32–33](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/DURUM.md#L29-L33) D1 tablosunu hâlâ elle uygulama adımı olarak yazıyor; [Worker dağıtım iş akışı](https://github.com/sselimgenc-oss/sg-arge/blob/206086b/.github/workflows/worker.yml#L44-L55) şemayı uyguluyor ve başarılı koşuda bu adım geçti.

**Etki:** ilerleme ve dağıtım kanıtı yanlış okunabilir. **Yapılacak:** günlük/DURUM sayıları ile dağıtım talimatını gerçek sürüme eşitle.

## Test, güvenlik ve korunanlar

- [#441 CI 41085865181](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41085865181): **518 Python, 35 Worker geçti**. [#445 CI 41089279069](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41089279069): **523 Python, 39 Worker geçti**. [Worker üretim dağıtımı 41089521540](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41089521540) test, D1 şema ve deploy adımları yeşil. Git fetch bu ortamda proxy bağlantısı vermediği için güncel main testleri burada yeniden çalıştırılamadı; eski yerel `fe2161f` testini güncel sonuç diye kullanmadım.
- **Güvenlik:** #441/#445 değişen dosyalarda Etre'nin gerçek emir/cüzdan/çekme yolu yok. Güncel `sg-arge` ağaçtaki 150 dosya arasında `borsa.py`, `gercek.py`, `zincir/` veya secret dosya adı yok. Yeni değişikliklerde anahtar örüntüsü saptanmadı. **KRİTİK bulgu yok.** Tam Git geçmişi için sır taraması doğrulanamadı.
- **Korunanlar:** `secim.py` v1.3, `analiz_d.py`, `ONKAYIT_D.md`, `KAPI_V3.md`, `golge.py`, `defter.py`, R2/saatlik bulut yolları güncel ağaçta duruyor. #441/#445 bu seçim ve ön kayıt dosyalarını değiştirmedi. #443'ün eski test/belge silmesi yukarıdaki ayrı bulgudur.
- **Canlı akış:** `copytrade-izleme` son commit'i 19:23 TSİ (`4dafe0b`); içindeki veri 18:36 TSİ üretilmiş, 91 trader ve 200 olay. Bu, saatlik akışın sürdüğünü gösterir; #441/#445 sonrası uçtan uca üretimin başarılı olduğunu henüz göstermez.

## Karar ve sıradaki işler

Birleştirilmiş #441'in önceki iki yüksek bulgusu **giderildi**. Birleştirilmiş #445 için CI ve dağıtım **yeşil**, fakat canlı gecikme çıktısı, örnek kapsamı ve pano kanıtı eksik; **E1 tamamlandı denemez**. Açık [#434](https://github.com/sselimgenc-oss/sg-arge/pull/434) taslak, görevdeki E2 yerine birleştirilmemeli.

1. #445 sonrası ilk saatlik koşunun `gecikme.json` + `durum.json` gerçek sayılarını incele; boş/404 ise yapılandırmayı düzelt.
2. Gecikme ölçüsünde taze pencere, her dolum ve eksik kapsamı ele al; Worker'ın 429/hata/sessizlik sayacını sağlık kaydına bağla.
3. #443 temizlik kararı ile görevdeki “arşivle, silme” ve test kuralı çelişkisini belgeleyip v1 kanıtını erişilebilir tut.
4. E2 tek kasa/motoru v1 yanında v2 olarak, gerçek veri ve oda/kontrol/O10 yan yana kanıtıyla getir; ardından E3–E6.
