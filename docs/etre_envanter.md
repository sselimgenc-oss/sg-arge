# ETRE mimari envanteri — yalnız analiz

Kaynak: <https://github.com/ismailkaraabc/etre-trading-office> (GPL-3.0).

Bu belge işlevsel karşılaştırmadır; kaynak kod veya metin aktarmaz. GPL-3.0 lisanslı
koddaki hiçbir parça `sg-arge` içine alınmamalıdır; notlar yalnız bağımsız tasarım
fikridir. İncelenen depoda işlem veritabanı bulunmadığı için ileri testlerin gerçekleşmiş
çıktısı doğrulanamadı. `ileri_test_*.json` dosyaları sonuç değil; hipotez, pencere ve
başarı ölçütlerini önceden donduran kayıtlardır.

## Öncelik özeti

| Konu | Karşılık | Öncelik | Getiri / maliyet |
| --- | --- | --- | --- |
| Dondurulmuş ileri test bildirgesi + genel raporlayıcı | Onlarınki daha iyi | Yüksek | D yolu için ön kayıt izini güçlendirir; şema ve veri sürümü gerekir. |
| Geçerlilik/dışlama kaydı | Var | Yüksek | Hatalı gölge satırlarını silmeden ayırır; ortak maske ve tersine çevirme gerekir. |
| Çalışma zamanı veri kalitesi | Onlarınki daha iyi | Yüksek | Kayma, yetim, tazelik ve gecikmeyi tek rapora toplar; gözlem şeması gerekir. |
| Trader yaşam döngüsü | Onlarınki daha iyi | Yüksek | Nedenli geçiş ve olay izi sağlar; `kollar.py` ile uyumlu ortak kayıt gerekir. |
| Gerçek zamanlı HL olay akışı | Onlarınki daha iyi | Orta | Gecikme ölçümünü iyileştirir; kalıcı servis/yeniden bağlanma maliyetlidir. |
| Çok kaynaklı keşif | Yok | Düşük | Evreni genişletir; ücretli kaynak ve farklı zincir riski yüksektir. |
| Ağırlıklı trader puanı | Var | Düşük | Tanısal olabilir; kısa veriyle ağırlık güncellemesi aşırı uyum riski taşır. |
| Gerçek emir katmanı | Yok | Düşük | Proje kapsamı dışı gerçek para/emir işlevi. |
| Kronolojik gelişim günlüğü | Onlarınki daha iyi | Yüksek | Veri sürümü–incident–karar bağını görünür yapar; ikinci doğru kaynak yaratmamalı. |

## Modül incelemesi

### `etre2/hl/api.py`

- **Ne yapıyor?** Anahtarsız Hyperliquid bilgi isteklerini ağırlık bütçesine göre sıraya alıyor; hata/429 sayacı ve bayat fiyat
  koruması tutuyor. Orta fiyatlar ile kullanıcı dolumlarını WebSocket olaylarına bağlayabiliyor.
- **Bizde karşılığı:** **Var.** `copytrade/tarama.py` oran sınırlama/tekrar, `defter.py` dolum defteri ve `izleme_motoru.py`
  periyodik izleme sağlar. Bizdeki 10.000+ dolum sayfalaması ve defter denetimi daha güçlü; gerçek zamanlı abonelik onlarda daha ileri.
- **Getiri, maliyet, öncelik:** Giriş zamanı ve kayma raporunu iyileştirebilir. Bağlantı kopması, ilk snapshotın olay üretmemesi ve
  kısa aç-kapa hareketlerini kaçırma riski nedeniyle kalıcı servis gerekir. **Orta.**

### `etre2/hl/lider.py`

- **Ne yapıyor?** Ağır liderlik tablosunu ana döngüden ayrı indirip tekrar deniyor, süzüyor ve sade aday çıktısı yazıyor.
- **Bizde karşılığı:** **Var.** `tarama.py`, `kapi.build_universe` ve arşiv iş akışı aynı evreni kullanır; ortak evren snapshotı
  shardlar arası çakışma sorununu kapatır. Ayrı süreç yaklaşımı operasyonel olarak daha dayanıklı, ancak sezgisel filtreleri alınmamalı.
- **Getiri, maliyet, öncelik:** Kesintinin ana koşuyu durdurmamasını sağlar; yeni artefakt/süreç yönetimi gerektirir. **Düşük.**

### `etre2/hl/izle.py`

- **Ne yapıyor?** Pozisyon anlık görüntülerini önceki durumla karşılaştırarak açılış, kapanış, ekleme ve yön dönüşü olaylarına ayırıyor.
- **Bizde karşılığı:** **Var.** `defter.copy_ledger` ve `golge.py` dolumlar üzerinden aynı ekonomik olayları tekrar kuruyor. Düşük
  gecikmeli olay üretimi onlarda daha iyi; bizdeki defter geriye dönük denetlenebilirlikte daha uygun.
- **Getiri, maliyet, öncelik:** Gecikme zincirini daha doğru zamanlayabilir; poll farkı kısa işlemi kaçırabilir ve WS işletimi gerekir.
  **Orta.**

### `etre2/hl/borsa.py`

- **Ne yapıyor?** İmza, fiyat/boy yuvarlama, gerçek emir, çekim ve küçük boyutlu canlı geçiş denemesini kapsıyor.
- **Bizde karşılığı:** **Yok.** Projede gerçek para, emir ve cüzdan yetkisi bilinçli olarak yoktur.
- **Getiri, maliyet, öncelik:** Araştırma için getiri yok; güvenlik ve geri döndürülemez işlem maliyeti yüksek. **Düşük; uyarlanmayacak.**

### `etre2/kesif.py`

- **Ne yapıyor?** Birden çok dış kaynaktan trader ekliyor, liderlik bilgisini saklıyor, önce adayları doğruluyor ve kota baskısında
  istekleri önceliklendiriyor. Cüzdan eşleştirme/geçmiş özeti puan için bilgi alanı oluyor.
- **Bizde karşılığı:** **Yok.** `copytrade/kesif.py` ilişkili hesap incelemesine, `tarama.py` açık HL liderlik evrenine odaklıdır.
- **Getiri, maliyet, öncelik:** Keşif yanlılığını azaltabilir; ücretli sağlayıcı, kota, zincir farklılığı ve veri kalitesi maliyetidir.
  **Düşük** — D yolunun bugünkü açık Hyperliquid evreni kararı korunmalı.

### `etre2/puan.py`

- **Ne yapıyor?** Birden çok özelliği yüzdelik sıra ve ağırlıkla tek puanda topluyor; gölge sonuçlarını büzülmüş özetlere çevirip
  ağırlıkları ileriye dönük gözlemle sınırlı biçimde güncellemeyi hedefliyor.
- **Bizde karşılığı:** **Var.** Kapı ölçütleri ve `secim.py` maliyet sonrası puanı ile `kollar.py` seçim/kontrolü bulunuyor.
  Kaynak günlükte bu puanın ileri sonucu güvenilir taşımadığı da kaydedildiğinden, doğrudan üstün değil.
- **Getiri, maliyet, öncelik:** Eksik veri ve sıra kalıcılığını tanısal raporlamak yararlı olabilir. Öğrenen ağırlıklar çoklu deneme ve
  kısa örneklemde aşırı uyum yaratır. **Düşük.**

### `etre2/kalite.py`

- **Ne yapıyor?** Yetim gölge, giriş kayması/gecikmesi, akış sessizliği, kuyruk kaybı, hata, takılma, yedek ve kota durumunu tek
  sağlık sözleşmesinde ölçüyor; uyarı ve gün sonu özeti üretiyor.
- **Bizde karşılığı:** **Var**, ancak parçalı: `kapi.sanity_check`, `golge_saglama.py`, arşiv boşluk denetimi ve pano sağlığı ayrı.
  Çalışma zamanı veri tazeliği ile yetim oranını birlikte raporlama yönü **onlarınki daha iyi**.
- **Getiri, maliyet, öncelik:** Kirli verinin kohort sonucuna etkisini erken görünür yapar. Ortak gözlem şeması ve yalnız raporlayan
  ilk sürüm gerekir; yeni otomatik eşik eklenmemeli. **Yüksek.**

### `etre2/trader.py`

- **Ne yapıyor?** Kimlik, gerekçeli durum geçişi, bekleme süresi, parametre birleştirme ve olay günlüğünü kilitli kayıt katmanında
  tutuyor. Eski bir ağ cevabının güncel parametreleri ezmesini önlemeye çalışıyor.
- **Bizde karşılığı:** **Var**, fakat dağınık: `secim.py` kolları üretir, `kollar.py` terfi/çıkış olayı kaydeder, izleme listesi
  sözleşmesi vardır. Merkezi durum makinesi ve değişmez neden günlüğü bakımından **onlarınki daha iyi**.
- **Getiri, maliyet, öncelik:** Kohort/kontrol adresinin neden ve sürüm geçmişini denetlenebilir yapar. Şema göçü gerekir; kısa
  dönem performansla otomatik terfi D yoluna aykırıdır. **Yüksek.**

### `etre2/ileri_test.py`

- **Ne yapıyor?** Önceden yazılmış ölçüt belgesinden grupları, örneklemi, kırpılmış sonuç farkını ve karar durumunu ortak biçimde
  değerlendiriyor. Pencere bitmeden veya açık gölgeler kapanmadan karar vermeme ilkesini koruyor.
- **Bizde karşılığı:** **Var**, ancak dağınık: `ONKAYIT_D.md`, `kollar.py`, `kalicilik.py` ve gölge sağlama aynı ilkelerin parçalarıdır.
  Bildirge → genel değerlendirici → karar artefaktı zinciri bakımından **onlarınki daha iyi**.
- **Getiri, maliyet, öncelik:** Hipotez değiştirme ve erken bakış riskini azaltır. Bağımsız YAML/JSON şema, sürümleme ve sonuç
  artefaktı gerekir. **Yüksek.**

### `araclar/ileri_test_*.py` ve `araclar/ileri_test_*.json`

- **Ne yapıyor?** Aile; büyük işlem, fikir/rejim, ilk sıralar, kalabalık, ana karar, sinyal ve çıkış varyantlarını ayrı
  değerlendiriyor. JSON bildirgeleri grup tanımı, pencere, kırpma, minimum örneklem, kümeli bootstrap ve karar metnini donduruyor.
- **Bizde karşılığı:** **Onlarınki daha iyi.** `ONKAYIT_D.md` ile `kalicilik.py` ön kayıt/blok bootstrap sağlar; her deney için
  makinece okunur bildiri, veri sürümü, açık pozisyon kapanış kuralı ve genel rapor zarfı yoktur.
- **Getiri, maliyet, öncelik:** Kohort–kontrol farkını tekrar üretilebilir kılar. Deney kimliği, contamination etiketi, bootstrap
  birimi ve sürüm politikası gerekir. **Yüksek.** Sayısal eşikler/kırpmalar taşınmamalıdır.

Kaynak günlüğü, trader seçiminin havuzu ileriye dönük güvenilir biçimde aşamadığını ve sonraki pencere içinde funding, izleme
ve oda bileşiminde müdahaleler bulunduğunu da kaydediyor. Bu, tasarımın en önemli dersidir: çıktı verisi olmadan üstünlük
iddiası kurulmaz; pencere içi müdahale deney sürümüne yazılmadan sonuç karşılaştırılamaz.

| İleri test ailesi | Kavramsal ders | Bizdeki değerlendirme |
| --- | --- | --- |
| Büyük işlem, sinyal, kalabalık | Sinyal kovasını uygun kontrolle ayırır. | Yalnız HL dolum özellikleri için ileride araştırma kaydı olabilir. |
| İlk sıralar, trader kararı | Seçimin rastgele/havuza göre ileri sonucu taşıyıp taşımadığını sınar. | D yolunun asıl sorusuyla uyumlu. |
| Çıkış varyantı | Aynı pozisyonda tek değişkenli, eşli karşılaştırma yapar. | `golge.py` V2 değişikliği öncesi tasarım dersi. |
| Sürüm v1/v2 | Veri kirliliğinde eski deneyi koruyup yeni pencere açar. | Yüksek öncelikli veri sürümü ilkesi. |

### Gölge işaretleme araçları

- **Ne yapıyor?** Bayat fiyatla açılmış veya trader kapanışıyla eşleşmeyen gölgeleri nedenleriyle işaretleyip test evreninden
  hariç tutuyor; geri alma listesi bırakıyor. Araçlar belirli olay düzeltmeleri olup genel amaçlı çerçeve değildir.
- **Bizde karşılığı:** **Var.** `golge_saglama.py` kayma/farkı ölçer, `defter.py` olayları korur; deney bazlı dışlama günlüğü sınırlıdır.
- **Getiri, maliyet, öncelik:** Ham satırı silmeden geçerlilik durumunu saklamak ölçüm denetimini güçlendirir. Kol adına ek koymak
  yerine ayrı `veri_kalitesi` ve `reddetme_nedeni` alanı tasarlanmalı; dry-run/apply ve geri alma kaydı gerekir. **Yüksek.**

### `docs/GELISIM_GUNLUGU.md`

- **Ne yapıyor?** Zaman damgalı kararları, incidentleri, düzeltmenin hangi ölçümü etkilediğini ve açık riskleri kronolojik kayıtta
  birleştiriyor. Veri kirliliği bulunduğunda eski testin korunup yeni sürüm/pencere açıldığını da açıklıyor.
- **Bizde karşılığı:** **Onlarınki daha iyi.** `DURUM.md`, görevler, ön kayıt ve `docs/codex_durum_*.md` var; incident–veri sürümü–
  araştırma etkisini tek çizgide bağlayan kısa günlük yok.
- **Getiri, maliyet, öncelik:** Lider denetiminde hangi veriyle hangi kararın verildiğini hızla gösterir. İkinci doğru kaynak
  yaratmamak için yalnız büyük koşu/incident için standart ek bölüm gerekir. **Yüksek** — maliyet düşük/orta.

## Önerilen sıra ve sınır

1. **Yüksek:** `ONKAYIT_D.md` ile uyumlu, bağımsız deney bildirgesi; sonuç artefaktında veri sürümü, dışlama etiketi, pencere ve
   açık pozisyon kapanış durumu yer alsın.
2. **Yüksek:** Gözlemlenmiş bayat fiyat/yetim kapanış sınıfları için silmeyen geçerlilik günlüğü ve sağlama raporu.
3. **Yüksek:** Kayma, gecikme, yetim oranı ve veri tazeliğini yalnız raporlayan çalışma kalitesi bölümü.
4. **Yüksek:** Kohort/kontrol için gerekçeli, sürümlü geçiş olayı; kısa gölge performansıyla otomatik terfi yok.
5. **Yüksek:** Her deney sürümünde pencere içi müdahale ve veri kaynağı değişikliklerini kaydeden kısa gelişim/incident bölümü.
6. **Sonra:** Gerçek zamanlı abonelik, yeni keşif kaynakları ve puan öğrenimi ancak ihtiyaç/güç kanıtından sonra değerlendirilir.

Gerçek emir, çekim, kaynak koddaki parametre/ağırlıklar ve ücretli üçüncü taraf veriler kapsam dışıdır.
