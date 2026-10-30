# Etre geçişi bağımsız denetimi — 30 Ekim 2026

**Kullanıcının isteği yaklaşık %25 oranında karşılandı.**

Denetim puanı: 12 alan eşit ağırlıkta; **TAMAM = 1, KISMİ = 0,5, YOK = 0**. Altı kısmi, altı yok: 3/12 = %25. İşlevsel olarak tamamlanmış alan sayısı **0/12**.

**Kesit:** 30 Ekim 2026, 18:43 TSİ. `sg-arge main` = `1ca8d28` (#440), `sg-pano main` = `b43529d` (#45). Açık PR uçları: #439 `b7be479`, #441 `545c1b6`, #46 `75b31e7`. Bu rapor açık PR'ları **main'den ayrı** değerlendirir. [Görev](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L1-L8), [K-11](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/KARARLAR_D.md#L132-L136), [kurallar](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/AGENTS.md#L10-L28).

**Kesit sonrası değişiklik:** `sg-arge` main'e 18:45 TSİ'de [#346](https://github.com/sselimgenc-oss/sg-arge/pull/346/files) (`d1a4f28`) birleşti. Altı dosyası HF geçmiş doğrulaması, yeni bir test ve yeni bir iş akışıyla ilgili; Etre geçiş dosyalarını değiştirmiyor. Dolayısıyla aşağıdaki Etre durumları aynı, fakat iş akışı sayısı kesitte 18 iken artık 19. Bu PR'ın hedefi güncel main'dir.

## 12 alan

| Alan | Etre'de | Bizde: main / açık PR | Durum; eksik |
|---|---|---|---|
| 1. Program ve kullanılabilirlik | [README: masaüstü ve tek ofis](https://github.com/ismailkaraabc/etre-trading-office/blob/main/README.md#L31-L43), [KULLANIM: açma/ekran](https://github.com/ismailkaraabc/etre-trading-office/blob/main/KULLANIM.md#L8-L22) | main: [pano mobil web](https://github.com/sselimgenc-oss/sg-pano/blob/b43529d/README.md#L3-L19) ve ayrı ofis var. PR: [#46](https://github.com/sselimgenc-oss/sg-pano/pull/46/files) yalnız lisans/metin. | **KISMİ**; Etre benzeri tek kullanıcı akışı ve canlı kasa ekranı yok. Bulut erişimi korunmalı. |
| 2. Plan/yol haritası | [README: tek ürün amacı ve parçalar](https://github.com/ismailkaraabc/etre-trading-office/blob/main/README.md#L24-L43), [gelişim günlüğü](https://github.com/ismailkaraabc/etre-trading-office/blob/main/docs/GELISIM_GUNLUGU.md#L1-L11) | main: [görevde E1–E6 planı](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L28-L35), fakat [DURUM başında](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/DURUM.md#L1-L23) tek geçiş tablosu yok. PR: [#441 DURUM listesi](https://github.com/sselimgenc-oss/sg-arge/pull/441/files), günlük taslağı. | **KISMİ**; tarih-saatli ölçüm günlüğü ve tek yol haritası tamamlanmadı. |
| 3. Veri hattı | [HL ağırlık/429/fiyat koruması](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/hl/api.py#L20-L107), [WS + katmanlı yoklama](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/hl/izle.py#L1-L5), [kalite](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kalite.py#L3-L7) | main: [saatlik Action](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/.github/workflows/izleme.yml#L1-L6), [motor](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/izleme_motoru.py#L694-L743), [Worker](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/worker/src/index.js#L85-L92). PR: [#441 sağlık kaydı](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/copytrade/saglik_hatti.py#L1-L121). | **KISMİ**; dakikalık oda yoklaması, ağırlıklı kuyruk, 429 sayacı, ham sinyal gecikmesi ve tek veri çekimi yok. |
| 4. Risk ve çıkış mantığı | [teminat bazlı stop/merdiven/süre/zirve](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kurallar.py#L34-L43), [ortak çıkış fonksiyonu](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kurallar.py#L195-L239), [lab kolları](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kaldirac/lab.py#L108-L155) | main: [V2 sınırları ve tasfiye](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/golge.py#L64-L76), [çapraz eşik](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/golge.py#L111-L144). PR: #439/#441/#46 bu davranışı değiştirmiyor. | **YOK**; Etre çıkış kümesi ve ön kayıtlı paralel kural labı aktarılmadı. |
| 5. Mimari | [tek olay döngüsü](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/motor.py#L1-L9), [tek kasa](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kasa.py#L1-L10) | main: [izleme motoru](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/izleme_motoru.py#L694-L743), [gölge ve defter](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/golge.py#L1-L7), ayrı Worker/pano. PR: #441 yalnız rapor alanı ekliyor. | **YOK**; oda için tek kopya motoru/kasa ve geçiş arşivi yok. |
| 6. Yönetim ve sadelik | [gerekçeli trader geçişleri](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/trader.py#L1-L5), [olay günlüğü](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/trader.py#L83-L96) | main: [K-10 sadeleştirme kuralları](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/AGENTS.md#L41-L52), [v1.3 oda seçimi](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/secim.py#L134-L148). PR: [#441 günlük ekliyor](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/docs/GELISIM_GUNLUGU.md#L1-L24). | **KISMİ**; Etre oda giriş/çıkış işletimi ve eski görevlerin arşivi yok. Günlükte saat yok. |
| 7. Mühendislik kalitesi | [saf ortak kurallar](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kurallar.py#L1-L10), [akış kalite ölçüleri](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kalite.py#L22-L40) | main: [altın örnek/test kuralları](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/AGENTS.md#L20-L38). PR: #441 [6 test ekliyor](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/tests/test_saglik_hatti.py#L1-L82); CI 573 Python + 35 Worker geçti. | **KISMİ**; sağlık ölçüsünde anlam hatası var, geniş `except` [motor:716](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/izleme_motoru.py#L710-L728) sürüyor, iş akışları arşivlenmedi. |
| 8. Pano ve ofis | [canlı kasa/açık/kapalı kartı](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/web/canli.js#L25-L80), [izometrik vardiyalar](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/web/ofis.js#L31-L49), [oda sayfaları](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/web/odalar.js#L1-L35) | main: [pano sekmeleri](https://github.com/sselimgenc-oss/sg-pano/blob/b43529d/index.html#L130-L145), [ayrı ofis veri uyarlayıcısı](https://github.com/sselimgenc-oss/sg-pano/blob/b43529d/ofis/gercek.js#L1-L15); #45 teminat hesabını düzeltti. PR #46 yalnız lisans. | **YOK**; E5 kartı, yeni ofis ve ekran görüntülü gerçek veri kanıtı yok. |
| 9. Simülasyon gerçekliği | [HL derinlik/makas dolumu](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/sim.py#L111-L126), [funding/likidasyon](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kaldirac/masa.py#L429-L483) | main: [gölge V2](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/golge.py#L111-L164), [sabit kayma ayarı](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/kurallar.yaml#L1-L13). PR: davranış değişmedi. | **YOK**; Etre derinlikli dolum, sabit işlem tutarı ve yeni teminat hesabı yok. Mevcut v1 ölçümü korunmalı. |
| 10. Hız | [ilk 10 oda WS, öbürleri yoklama](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/hl/izle.py#L31-L35), [oda aralığı](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/hl/izle.py#L55-L73) | main: [saatlik cron](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/.github/workflows/izleme.yml#L1-L6); son başarılı izleme koşusu 47 dk sürdü (14:20–15:07 UTC). PR #441 yoklamayı hızlandırmıyor. | **YOK**; E1'in ücretsiz Worker dakikalık oda yoklaması uygulanmadı. |
| 11. Kopya mekaniği ve çıkışlar | [open/increase/reduce/close](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/hl/izle.py#L1-L5), [aynı oranda azaltma](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kaldirac/masa.py#L277-L295), [neden kaydı](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kurallar.py#L245-L253) | main: [gölge dolum filtresi](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/golge.py#L23-L61), [V2 çıkışları](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/golge.py#L160-L211). PR: yeni motor yok. | **YOK**; oda ortak portföy, Etre ayna oranı/çıkış nedeni bütünlüğü yok. |
| 12. Hedef netliği | [README tek cümle](https://github.com/ismailkaraabc/etre-trading-office/blob/main/README.md#L5-L9), [KULLANIM tek program](https://github.com/ismailkaraabc/etre-trading-office/blob/main/KULLANIM.md#L1-L5) | main: [hedef cümlesi görevde](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L28-L33); [DURUM başı](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/DURUM.md#L1-L23) hâlâ eski planı taşıyor. PR #441 K-11'i üste alıyor fakat ürün hedefini tek satırda vermiyor. | **KISMİ**; görünür README/DURUM hedefi ve tek sıra eksik. |

## E1–E6 ve bitti tanımı

| Madde | Sonuç | Kanıt / açık iş |
|---|---|---|
| Lisans ön koşulu | **KISMİ** | [#439](https://github.com/sselimgenc-oss/sg-arge/pull/439/files) ve [#46](https://github.com/sselimgenc-oss/sg-pano/pull/46/files) açık. İki LICENSE, Etre LICENSE ile aynı blob `e3b5ef7`; atıf metni var. main'de henüz yok. |
| E1 hız ve veri hattı | **KISMİ** | [#441](https://github.com/sselimgenc-oss/sg-arge/pull/441/files) sağlık raporu ve Worker alarmı ekliyor; gerçek veride oda 18, yetim 2/542, havuz hata 6/30 doğrulandı. Dakikalık toplama/tek kaynak/gerçek sinyal gecikmesi yok. |
| E2 kopya ve simülasyon | **YOK** | Açık PR'ların dosya listesinde motor/kasa hesap değişimi yok; [görev E2](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L44-L50). |
| E3 risk ve çıkış | **YOK** | Etre kural seti/labı için PR yok; [görev E3](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L51-L56). |
| E4 oda yönetimi | **YOK** | v1.3 seçim kalıyor, Etre gerekçeli terfi/düşme işine PR yok; [görev E4](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L57-L61). |
| E5 pano ve ofis | **YOK** | #46 yalnız lisans; Etre kartı, 5 dk veri ve gerçek ekran görüntüsü yok; [görev E5](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L62-L66). |
| E6 mühendislik/sadelik | **KISMİ** | #441 test/günlük ekliyor; tek motor, tek ayar dosyası, kullanılmayan iş akışlarının arşivi yok (kesitte 18, #346 sonrası 19). Kullanıcı onayı gereken arşivleme yapılmamış; [görev E6](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L67-L70). |

[Bitti tanımının](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L81-L83) tekil kontrolü:

| Kabul koşulu | Sonuç ve kanıt |
|---|---|
| Panoda Etre kartı, gerçek veri ve ekran görüntüsü | **YOK**; #46 görünüm değiştirmiyor, ekran görüntüsü yok. |
| Sabit tutarlı tek kopya motoru, çıkış kuralları, tasfiye | **YOK**; #441 yalnız rapor, E2/E3 PR yok. Mevcut [v1 tasfiye eşiği](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/kurallar.yaml#L193-L194) yeni motorun kanıtı değil. |
| Oda Etre gibi yönetiliyor | **YOK**; E4 PR yok. |
| Sinyal gecikmesi ölçülüyor ve panoda | **YOK**; #441 ölçüsü pozisyon yaşı, pano değişmiyor. |
| Tek veri kaynağı | **YOK**; [motor](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/izleme_motoru.py#L694-L708) ve [Worker](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/worker/src/index.js#L85-L93) ayrı Hyperliquid erişimine sahip. |
| Eski parçalar arşivde | **YOK**; açık PR dosya listelerinde arşiv taşıması yok. |
| Bağımsız denetim temiz | **YOK**; aşağıdaki yüksek bulgular açık. |

## Bulgular — önem sırasıyla

### YÜKSEK — #441 sinyal gecikmesini yanlış adlandırıyor

**Kanıt:** [#441 `saglik_hatti.py`:75–85](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/copytrade/saglik_hatti.py#L75-L85) `uretildi - pozisyonlar[].acilis` medyanını `sinyal_gecikme_dk_medyan` diye yayımlıyor. [Sözleşme](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/docs/VERI_SOZLESMESI.md#L66-L75) bunun pozisyon yaşı olduğunu da söylüyor. Etre [gerçek olay `ts` ve algılama gecikmesini](https://github.com/ismailkaraabc/etre-trading-office/blob/main/etre2/kaldirac/masa.py#L96-L108) ayrı tutuyor. Gerçek dosyada oda medyanı 40,73 dk, yalnız 5 açık pozisyondan geliyor; işlem algılama gecikmesi olduğu doğrulanmadı.

**Etki:** E1 hız başarısı yanlış ölçüyle ilan edilebilir; gecikme alarmı yapılamaz. **Yapılacak:** alanı `acik_pozisyon_yasi_dk_medyan` olarak adlandır; gerçek sinyal zamanı, Worker algılama zamanı ve kopya karar zamanını ayrı kaydet; ölçüyü o zaman ekle. Yanlış adı ileriye taşımadan sözleşme/testi düzelt.

### YÜKSEK — #441 sağlık ışığı durmuş akışı yeni başına yakalamaz

**Kanıt:** [motor:694 ve 729](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/copytrade/izleme_motoru.py#L694-L736) `now` değerini koşu başında alıp `uretildi`ye koyuyor; hemen [aynı `now` ile](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/copytrade/izleme_motoru.py#L733-L737) sağlık hesaplanıyor. Sonuçta `veri_tazeligi_dk = 0`; koşu bitene kadar geçen yaklaşık 47 dk bile görünmüyor. Dosya güncellenmezse ışık da değişmez. Mevcut Worker'ın ayrı [3 saatlik eski veri alarmı](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/worker/src/index.js#L281-L288) var; bu bulgu onun yokluğu iddiası değildir.

**Etki:** yeni `saglik_hatti.isik` yeşil kalabilir ve kesilmiş akışı temsil etmez. **Yapılacak:** ölçüm zamanını yayımlama/okuma zamanından ayır, Worker'da her okumada tazeliği yeniden denetle; sessizlik ve 429/hata sayısı için gerçek kaynak sayaçları ekle, test et.

### YÜKSEK — E1'in asıl hız ve tek kaynak koşulları henüz uygulanmadı

**Kanıt:** [görev E1](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L36-L43) dakika cron, ağırlıklı kuyruk, 429, bayat fiyat ve tek veri çekimi ister. [#441 değişen dosyalar](https://github.com/sselimgenc-oss/sg-arge/pull/441/files) Worker dolum yoklaması/D1 sinyal deposu içermiyor; PR açıklaması bunu sonraya bıraktığını söylüyor. [main izleme cron'u](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/.github/workflows/izleme.yml#L1-L6) saatlik.

**Etki:** Etre hızı ve kopya gecikmesi kazanımı oluşmadı. **Yapılacak:** E1'i ayrı devam PR'larında gerçek oda dolumlarıyla, 1 saatlik küçük deneme ve uçtan uca gecikme dağılımıyla tamamla.

### ORTA — #441 atıf ve günlük ön koşulu tutarsız

**Kanıt:** [#441 modül başı](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/copytrade/saglik_hatti.py#L1-L8) `Etre kalite.py karşılığı` diyor; [görev lisans maddesi](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/GOREV_ETRE_GECIS.md#L23-L27) çevrilen dosyada kaynak yolu ve GPL ister. Modülde `etre2/kalite.py, GPL-3.0` tam kaynak notu yok. [#441 günlük:18](https://github.com/sselimgenc-oss/sg-arge/blob/545c1b6/docs/GELISIM_GUNLUGU.md#L18-L24) lisans eklendi diyor, fakat #439 ve #46 hâlâ açık. Günlük başlıklarında saat de yok.

**Etki:** aktarımın kaynağı ve birleşme sırası belirsizleşir. **Yapılacak:** #439/#46 sonrası #441'i yeniden sırala; Etre'den çevrildiği iddia edilen modüle tam yol/lisans notu ekle; günlüğü fiilen birleşen duruma ve tarih-saat biçimine getir.

### ORTA — “gerçek veri denemesi” geçişin çalıştığını kanıtlamıyor

**Kanıt:** [#441 açıklaması](https://github.com/sselimgenc-oss/sg-arge/pull/441) canlı `durum.json` üzerinde saf `olc()` çalıştırmış. Aynı dosyada bağımsız yeniden hesap: oda `n=18`, yetim `2/542 = %0,369`; kontrol `2/18 = %11,1`, taban `3/18 = %16,7`, havuz `6/30 = %20` hata. [canlı veri dalı](https://github.com/sselimgenc-oss/sg-arge/blob/copytrade-izleme/izleme/durum.json) hâlâ `saglik_hatti` alanını taşımıyor; #441 main'e girmedi.

**Etki:** hesap örneği doğru olsa da yeni üretim, D1 alarmı, pano sunumu ve gerçek sinyal gecikmesi doğrulanmış sayılmaz. **Yapılacak:** PR düzeltmesinden sonra küçük gerçek koşu çıktısı, JSON alanı, Worker alarmı ve ekranı birlikte kontrol et.

## Test, lisans, güvenlik ve korunanlar

- **Bağımsız yerel test sınırı:** Git fetch, proxy bağlantısı yüzünden çalışmadı. Yerel kopya `fe2161f` (#435), güncel main/#441 değil. Bu kopyada `.venv/bin/python -m pytest -q` → **567 geçti** (1345 uyarı); `worker` içinde `npm test` → **3 test dosyası geçti**. Varsayılan `python -m pytest -q` → `No module named pytest`; yerel `.venv` kullanıldı. Bu sonuçlar #441 testi diye sunulmuyor.
- **PR CI:** [#441 koşu 41080759212](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41080759212) test işi başarılı; iş günlüğünde **573 Python ve 35 Worker testi geçti**. [#439 koşu 41078072129](https://github.com/sselimgenc-oss/sg-arge/actions/runs/41078072129) başarılı. #46 ucunda GitHub check run sayısı **0**; pano testinin bu PR ucunda çalıştığı doğrulanamadı. #46 yalnız belge/lisans değiştiriyor.
- **Lisans:** #439 ve #46 LICENSE içerikleri Etre LICENSE ile **aynı SHA** (`e3b5ef763810ebc7bdc5ebf1956deb4613449668`). [#439 NOTICE](https://github.com/sselimgenc-oss/sg-arge/pull/439/files) ve [#46 README](https://github.com/sselimgenc-oss/sg-pano/pull/46/files) Etre v2 ve sahibini/kaynağı anıyor. Dosya bazlı tam atıf için #441 düzeltmesi yukarıda.
- **Güvenlik:** #439/#441/#46 eklenen satırlarında anahtar/token örüntüsü eşleşmesi **0**. `sg-arge main` ve #441 ağaçları sırasıyla 296/299 dosya; `borsa.py`, `gercek.py`, `zincir/`, cüzdan/secret dosya adı yok. Açık PR yamalarında emir, para çekme veya zincir işlem gönderme kodu yok. **KRİTİK bulgu saptanmadı.** Tüm Git geçmişi ve her içerik için kapsamlı sır taraması yapılmadı; o kapsam doğrulanamadı.
- **Korunanlar:** [#441 değişen 8 dosya](https://github.com/sselimgenc-oss/sg-arge/pull/441/files) içinde `secim.py`, `ONKAYIT_D.md`, `kurallar.yaml`, bulut iş akışı, mevcut test silmesi yok. [v1.3 seçim](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/secim.py#L1-L5), [kontrol eşlemesi](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/copytrade/secim.py#L172-L193), [ön kayıt](https://github.com/sselimgenc-oss/sg-arge/blob/1ca8d28/docs/ONKAYIT_D.md#L1-L20) main'de mevcut. PR yamalarında test zayıflatma görülmedi. Yeni motor olmadığı için v1/v2 yan yana üretim henüz doğrulanamaz.
- **Canlı veri:** [copytrade-izleme dalı](https://github.com/sselimgenc-oss/sg-arge/tree/copytrade-izleme) son commit'i `ee4d010` (30 Ekim 18:07 TSİ); JSON içindeki `uretildi` 17:20 TSİ, 91 trader ve 200 olay. Son başarılı [izleme koşuları](https://github.com/sselimgenc-oss/sg-arge/actions/workflows/izleme.yml): 13:05 UTC zamanlı koşu, ardından 14:20 UTC elle/Worker tetiklemeli koşu; 15:36 UTC tetiklemeli koşu denetim anında sürüyordu. Dolayısıyla veri üretimi sürüyor, **her saat kesin yayımlanıyor** denemez. #441 henüz main'e girmediği için mevcut akışı bozduğu canlıda doğrulanamaz; diff eski yayın yolunu değiştirmiyor.

## Açık PR kararı

| PR | Karar | Neden |
|---|---|---|
| [sg-arge #439](https://github.com/sselimgenc-oss/sg-arge/pull/439) | **Birleştirilebilir** | GPL metni birebir, NOTICE yeterli, kod değişmiyor, CI yeşil. Geçişin lisans ön koşulu olarak önce alınmalı. |
| [sg-pano #46](https://github.com/sselimgenc-oss/sg-pano/pull/46) | **Birleştirilebilir** | GPL metni birebir, README atfı mevcut, kod/görünüm değişmiyor. Bu PR ucunda CI/test koşusu doğrulanamadı; sonraki kod aktarımında dosya bazlı atıf yeniden incelenmeli. |
| [sg-arge #441](https://github.com/sselimgenc-oss/sg-arge/pull/441) | **Düzeltme gerekir** | CI ve hesap örneği yeşil; fakat sinyal gecikmesi yanlış adlandırılmış, yeni tazelik ışığı durmuş akışa tepki vermez, lisans sırası/günlük tutarsız. **E1 tamamlandı diye birleştirilmemeli.** |

## Sonnet'e sıradaki işler

1. #439 ve #46 lisans PR'larını al; #441'i bunların üstüne güncelle.
2. #441'de pozisyon yaşı ile gerçek sinyal gecikmesini ayır; tazelik ve sessizlik alarmını okuma anında ölç; tam Etre kaynak notu ve günlük saati ekle. Altın örnek + küçük gerçek çıktı ile tekrar denetime ver.
3. E1 devamında oda için dakikalık Worker dolum yoklaması, ağırlık/429/fiyat koruması ve tek kaynak hattını ayrı PR'larla kanıtla. Mevcut saatlik akışı geçiş tamamlanana dek açık tut.
4. Sonra E2 tek kasa/motoru v1 yanında v2 olarak kur; eski-yeni oda/kontrol/O10 sayılarını ve gerçek veri çıktısını karşılaştır.
5. E3–E6'yı görev sırasıyla, her biri ayrı PR ve gerçek çıktı ile getir. Pano/Telegram için mevcut kullanıcı tercihlerini ve ücret/eşik kararlarını görevdeki karar kapısına göre ele al.
