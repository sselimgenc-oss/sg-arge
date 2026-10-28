# Ofis V2 araştırması ve öneri

Tarih: 2026-10-28

> Not: Etre'nin ekranını, sprite'ını veya oda yerleşimini birebir almıyoruz. Amaç; özgün varlıklar ve kendi veri sözleşmemizle aynı yoğun, canlı operasyon merkezi hissini kurmaktır.

## 1. Emsal araştırması

| Emsal | Ne yapıyor | Alınacak fikir | Altyapı | Lisans | Bağlantı | Doğrulandı mı? |
|---|---|---|---|---|---|---|
| Stanford Generative Agents / Smallville | Ajanların günlük hayatını küçük bir kasaba simülasyonunda görünür yapıyor. | Görünen hareketin arkasında bellek/olay kaydı; hareketten önce açıklanabilir olay günlüğü. | Araştırma kodu ve LLM ajan mimarisi. | Apache-2.0. | [Makale](https://arxiv.org/abs/2304.03442) · [kod](https://github.com/joonspk-research/generative_agents) | Evet |
| a16z AI Town | Birlikte yaşayan, konuşan AI karakterlerini tarayıcıda piksel-kasaba olarak gösteren demo. | Karaktere tıklayınca profil/geçmiş/konum; mekânı durum katmanı yapmak. | Convex + React + PixiJS örneği. | MIT. | [GitHub](https://github.com/a16z-infra/ai-town) | Evet |
| Gather | Avatarlarla gezilen, harita üstünde ses/video ve etkileşim alanları sunan sanal çalışma alanı. | Odaya girme, yaklaştıkça ayrıntı, nesneye tıklama ve alan tabanlı etkileşim. | Ticari web ürünü; motor ayrıntısı açık değil. | Tescilli. | [Ürün](https://www.gather.town/) · [fiyatlar](https://www.gather.town/pricing) | Evet |
| WorkAdventure | Harita üzerinde dolaşılan web tabanlı sanal ofis. | Tiled harita mantığı, alan tetikleyicileri ve URL ile derin bağlantı. | WebRTC + harita tabanlı web uygulaması. | Depoda tek satır lisans beyanı net doğrulanamadı; kullanım öncesi incelenmeli. | [Dokümantasyon](https://docs.workadventu.re/) · [GitHub](https://github.com/workadventure/workadventure) | Kısmen |
| Mozilla Hubs | Tarayıcıdan çok-kullanıcılı sosyal alanlar ve nesne etkileşimi sağlar. | Tıklanabilir nesne + yan bilgi paneli; oda/nesne kimliğinin veri katmanından gelmesi. | WebXR / Three.js ekosistemi. | MPL-2.0. | [GitHub](https://github.com/mozilla/hubs) | Evet |
| The Sims | Karakter ihtiyaçları, düşünce balonları, nesne etkileşimleri ve oda bağlamını görünür yapar. | Konuşma balonunu yalnız olay açıklamasında kullanmak; eğlence metnini veriden ayırmak. | Tescilli oyun motoru. | Tescilli. | [Resmî site](https://www.ea.com/games/the-sims) | Evet |
| Prison Architect | Oda, personel, rota ve darboğazları yönetim simülasyonu olarak gösterir. | Oda sınırlarının işlevi anlatması; rota/uyarı katmanının isteğe bağlı açılması. | Tescilli. | Tescilli. | [Resmî sayfa](https://www.paradoxinteractive.com/games/prison-architect/about) | Evet |
| Two Point Hospital | Operasyon durumunu mizahi karakterler, oda işlevleri ve kuyruklarla anlatır. | Kritikliği renk tekeline bırakmamak: ikon + metin + görünür sebep. | Tescilli. | Tescilli. | [Resmî site](https://www.twopointhospital.com/) | Evet |
| Project Hospital | Hastane odaları, çalışanlar, görevler ve akışı ayrıntılı simüle eder. | Oda içine zoom; ekipman ayrıntısı; görev durumunu kişinin yanında kısa açıklama. | Tescilli. | Tescilli. | [Steam](https://store.steampowered.com/app/868360/Project_Hospital/) | Evet |
| Game Dev Tycoon | Yönetim kararlarını personel, proje ve geri bildirim döngüsüyle görünür kılar. | Gün sonu özeti ve “ne değişti?” zaman çizelgesi. | Tescilli. | Tescilli. | [Resmî site](https://www.greenheartgames.com/game-dev-tycoon/) | Evet |
| Kairosoft yönetim oyunları | Küçük mekânda personel, masa/işletme ve ilerlemeyi okunaklı tutar. | Küçük ekranda ikon hiyerarşisi; odada az ama anlamlı odak noktası. | Tescilli. | Tescilli. | [Kairosoft](https://kairopark.jp/) | Evet |
| eToro CopyTrader | Yatırımcıları takip/kopyalama odaklı sosyal trading ürünü. | Trader kartında performans, risk açıklaması ve dönemi birlikte göstermek; kopya ile izlemeyi ayırmak. | Tescilli web/mobil ürün. | Tescilli. | [CopyTrader](https://www.etoro.com/copytrader/) | Kısmen — erişim otomasyonca engellendi |
| Investopedia Stock Simulator | Eğitim amaçlı sanal portföy ve piyasa simülasyonu. | Sanal işaretini her parasal bağlamda görünür kılmak; eğitim/araştırmayı gerçek işlemden ayırmak. | Tescilli web ürünü. | Tescilli. | [Simulator](https://www.investopedia.com/simulator/) | Kısmen — erişim otomasyonca kısıtlandı |
| Etre | Kullanıcının sağladığı ekran görüntülerindeki copy-trade ofisi. | Genel yoğunluk ve oda derinliği; sprite, harita, tabela ve yerleşim kopyalanmaz. | Doğrulanamadı. | Doğrulanamadı. | Kullanıcının sağladığı ekran görüntüleri | Hayır — kamuya açık kaynak/lisans bulunamadı |

## 2. Tasarım önerileri

### Odaya girme

- Tam sayfa kopuş yerine: oda vurgusu → 250–350 ms kamera yakınlaşması → oda modu.
- Sol panel tümüyle kaybolmamalı; veri zamanı, `n`, geçerlilik ve geri düğmesi dar şeritte kalmalı.
- Her odada en çok üç ana etkileşim noktası: işlevsel ekipman, sorumlu sistem/çalışan, son olay.
- Derin bağlantı: `/ofis/#oda/lab`, `/ofis/#oda/risk`.

### Kişi ve nesne etkileşimi

- Hover yalnız masaüstü kolaylığıdır; ana işlev tıklama/dokunma ile çalışmalı.
- Bilgi kutusu: ad/rol, gerçek durum (zaman/n/geçerlilik), son olay, “neden burada?” açıklaması.
- Trader figüründe “kâr ediyor” gibi dekoratif replik kullanılmamalı. Örnek: “Son sinyal: 14:20 UTC”, “Veri yaşı: 3 dk”, “Aday katı: 11 gündür”.
- Eğlence replikleri ayrı görsel dil taşımalı ve `SÜS` etiketiyle işaretlenmeli.

### İletişim işaretleri

- Zarf, ok, not ve balon yalnız bir `olay_id` olduğunda üretilmeli.
- Lab → Aday terfi kartı; Denetim → oda doğrulama/uyarı notu; Risk → Oda “atla” sınırı; Haberleşme → dışarı Telegram zarfı; Sekreterlik → odalara kural notu.
- Rota çizgisi üç saniye sonra kaybolmalı; olay kaydından tekrar açılabilmeli.

### Bağlılık öğeleri ve veri çarpıtma riski

| Öğe | Değer | Risk | Güvenli uygulama |
|---|---|---|---|
| Gün sonu özeti | Yüksek | Orta | Yalnız gerçekleşmiş olaylardan “bugün ne değişti?” üretir. |
| Zaman atlamalı tekrar | Yüksek | Orta | Her kare olay kaydına bağlı; veri boşluğu boşluk olarak gösterilir. |
| Gün/gece ışığı | Orta | Düşük | Yerel saat göstergesi; piyasa durumu gibi sunulmaz. |
| Başarı rozeti | Orta | Yüksek | “Kârlı trader” yok; yalnız süreç/veri kalitesi rozetleri. |
| Ses | Düşük | Orta | Varsayılan kapalı, bildirim anlamı açık yazılır. |
| Oda geçmişi | Yüksek | Düşük | Son 24 saat olaylarını veri boşluklarıyla birlikte gösterir. |

### Telefon

- Açılışta kampüs özeti; oda seçilince tam ekran oda modu.
- Pinch yerine iki seviye: kampüs / oda.
- Ayrıntılar bottom sheet içinde; hedef alanlar en az 44×44 px.
- Reduced-motion, düşük güç ve düşük bant genişliği için statik görünüm.

## 3. Teknik ve ürün önerileri

### Kütüphane seçenekleri

| Seçenek | Artı | Eksi | Uygunluk |
|---|---|---|---|
| Düz HTML/CSS/SVG | Erişilebilirlik, metin, SEO ve kartlarda güçlü; derleme gerekmez. | Yüzlerce sprite/etkileşimde zorlaşır. | Panel ve erişilebilir üst katman için ideal. |
| Canvas 2D | Bağımlılık yok, küçük sahnelerde hızlı. | Hit-test, kamera, metin, erişilebilirlik elle yapılır. | Küçük prototip için uygun. |
| [PixiJS](https://pixijs.com/) | WebGL, sprite, filtre ve kamera için güçlü; sabit CDN sürümü kullanılabilir. | Oyun mantığı ve erişilebilir UI katmanı sizin sorumluluğunuzda. | **Öneri:** ofis PixiJS, panel/tooltip HTML. [MIT](https://github.com/pixijs/pixijs/blob/main/LICENSE). |
| [Phaser](https://phaser.io/) | Sahne, input, tween, kamera ve oyun döngüsü hazır. | Dashboard için ağır; UI erişilebilirliği ek iş ister. | Çok figür/görev olursa. [MIT](https://github.com/phaserjs/phaser). |
| [Kaboom](https://kaboomjs.com/) | Hızlı oyun prototipi, sade API. | Ekosistem/bakım riski ayrıca incelenmeli. | Hızlı deney. [MIT](https://github.com/replit/kaboom/blob/master/LICENSE). |
| SVG + HTML | Tıklanabilir alan, metin ve erişilebilirlik iyi. | Yoğun piksel sahnesinde yük artabilir. | Şematik oda haritası için. |

Önerilen akış:

```text
durum.json / olaylar.jsonl
          │
          ▼
     veri-adaptörü
          │  (şema doğrulama + bilinmiyor + timestamp + n)
          ▼
   durum deposu / olay kuyruğu
       │                 │
       ▼                 ▼
HTML panel + a11y    PixiJS ofis sahnesi
       │                 │
       └──── HTML tooltip / oda ayrıntısı ────┘
```

- Her görsel varlık `source: data | decorative` taşımalı.
- Veri bağlı her işaret `olay_id`, `zaman`, `n`, `veri_gecerli` ile izlenebilir olmalı.
- İsimler, oda temaları ve dekor tercihleri `workspace_config.json` içinde; performans verisinden ayrı tutulmalı.
- İlk sürüm tek kullanıcı için `localStorage`; ürünleşmede kullanıcı/kurum profili sunucu tarafında.
- Olay yokken render döngüsü durmalı; bu pil tüketimini ve sahte hareket riskini azaltır.

### Ticari kullanıma uygun varlık kaynakları

- [Kenney](https://kenney.nl/assets): İlk tercih. Varlıkları [CC0](https://kenney.nl/license) olarak sunulur; yine de her varlık `LISANSLAR.md` içinde kayıt altına alınmalı.
- [Quaternius](https://quaternius.com/packs.html): Paket içi lisans doğrulanarak kullanılmalı; birçok paket CC0 olarak yayımlanır.
- [OpenGameArt](https://opengameart.org/): Tek lisanslı bir kütüphane değildir. Yalnız açıkça CC0 veya ticari kullanıma izin veren uyumlu lisanslı paketler seçilmeli.
- [Liberated Pixel Cup](https://lpc.opengameart.org/): Açık varlıklar sunar; çift lisans/attribution/share-alike şartları kapalı kaynak veya ticari plan için hukuk incelemesi gerektirir.

### Ürünleşme ve hukuk

- Ürün “copy-trade karar motoru” değil, “olay kaynaklarını görselleştiren operasyon çalışma alanı” olarak konumlanmalı.
- Adaptörler ayrı olmalı: Hyperliquid, CSV/JSON, demo. Görsel motor borsaya doğrudan bağlı olmamalı.
- Kişiselleştirme: oda/çalışan adları, marka teması, rol-oda eşlemesi, bildirim kanalları, görünürlük ve özel şema adaptörü.
- Modeller: tek seferlik tema paketi; ekip aboneliği; self-hosted kurum lisansı + SSO; markalı gömülebilir pano.
- Fiyat kıyasları doğrudan eşdeğer değildir. Güncel referans için [Gather fiyatları](https://www.gather.town/pricing) ve [SpatialChat fiyatları](https://www.spatial.chat/pricing) tekrar kontrol edilmelidir.
- “En iyi trader”, “kazanacak”, “al/sat” gibi ifadeler yatırım tavsiyesi algısı oluşturabilir. Araştırma/simülasyon, gecikme, maliyet ve veri boşluğu görünür olmalı.
- Gerçek hesap bakiyesi, kullanıcı kimliği, karar zamanı ve işlem miktarı kamuya açık panoda gösterilmemeli.
- Bu bölüm hukuki tavsiye değildir; satış öncesi hedef ülke ve yatırım iletişimi uzman incelemesi gerekir.

## Ek özgün fikirler

| Fikir | Zorluk | Değer |
|---|---|---|
| “Neden burada?”: trader/oda için katman, kural, tarih, n ve son olay açıklaması. | Orta | Yüksek |
| Olay kanıtı modu: sahnedeki zarf/uyarıya tıklayınca ham olay kimliği ve zamanını gösterme. | Orta | Yüksek |
| Veri boşluğu hava durumu: eksik/bayat veriyi açık `VERİ EKSİK` etiketiyle sis katmanı olarak anlatma. | Orta | Yüksek |
| Ön kayıt kasası: Sekreterlikte aktif ön kayıt hash’i, sürümü ve kilit tarihi. | Düşük | Yüksek |
| Geçmiş tekrar: yalnız değiştirilemez kayıttan hızlandırılmış olay görünümü. | Yüksek | Orta |
| Sessiz vardiya: yalnız kritik risk/denetim olayları görünür. | Düşük | Orta |
| Veri sağlığı zemini: oda zemini kendi veri kapsamı ve yaşına göre değişir. | Orta | Yüksek |
| Oda el kitabı: “bu modül ne yapar / ne yapmaz?” kartı. | Düşük | Yüksek |
| Finans dışı kozmetik: tema, bitki, masa kaplaması; performans renkleri özelleştirilemez. | Orta | Orta |

## İlk yapılacak 5 iş

1. PixiJS + HTML panel yaklaşımıyla mevcut ofisin yanında ayrı V2 prototip rotası oluşturun.
2. `oda`, `nesne`, `karakter`, `olay` ve `decorative` ayrımını içeren sürümlü sahne şeması yazın.
3. İlk olarak yalnız Lab için oda modu yapın: masa, ekran, trader, son olay ve geri dönüş.
4. “Neden burada?” bilgi kutusunu ve olay kimliği bağlantısını ekleyin; tüm veri görünümlerinde zaman/n/geçerlilik zorunlu olsun.
5. Kenney veya kendi üretiminiz olan varlıklarla sprite atlası hazırlayın; `LISANSLAR.md`'ye dosya bazında kaynak, lisans ve boyut raporu ekleyin.
