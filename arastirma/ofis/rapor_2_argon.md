# Hyperliquid Sanal Copy-Trade Ofisi — Sürüm 2 Araştırma, Tasarım ve Mimari Raporu

**Proje Bağlamı:** Hyperliquid üzerinde algoritmik olarak trader seçen, eleyen ve sanal ortamda kopyalayan araştırma projemizin durum panosu. Sürüm 1'deki statik genel görünüm, Sürüm 2 ile derinlemesine etkileşimli, odaya girilebilen, tıklanabilir figür ve nesneler barındıran, gerçek olayların fiziksel ofis hareketlerine dönüştüğü bir simülasyon panosuna dönüştürülmektedir.

**Altın Kural:** Veri gibi görünen her öğe (puan, PnL, oda durumu, terfi, uyarı) %100 Hyperliquid ve bot motorunun gerçek verisine dayanır; eğlence ve atmosfer amaçlı hareket/replikler ise asla veri sanılmayacak biçimde ayırt edilir.

---

## 1. Emsal Araştırması (Benchmark Tablosu)

Aşağıdaki tablo; yapay zekâ simülasyonları, sanal ofisler, yönetim oyunları, finansal oyunlaştırma araçları ve ilham kaynakları olmak üzere 14 emsali detaylandırmaktadır. Halka açık olarak doğrulanabilen tüm projeler orijinal bağlantılarıyla sunulmuş, indekslenemeyen veya kapalı kaynaklar açıkça belirtilmiştir.

| Emsal | Ne Yapıyor? | Projemiz İçin Alınacak Fikir | Altyapı | Lisans | Bağlantı | Doğrulandı mı? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **a16z AI Town** | Sanal 2D piksel kasabada özerk yapay zekâ ajanlarının serbestçe dolaşmasını, konuşmasını ve ilişki kurmasını simüle eden açık kaynaklı platform. | Durum odaklı (state-driven) karakter dolaşımı, konuşma balonu zamanlaması, ajan bilgi kartı tasarımı. | TypeScript, Next.js, PixiJS, Convex DB | [MIT](https://github.com/a16z-infra/ai-town) | [GitHub: a16z-infra/ai-town](https://github.com/a16z-infra/ai-town) | Evet |
| **Stanford Generative Agents (Smallville)** | 25 LLM ajanının Smallville adlı piksel kasabada rutinlerini yaşadığı, hafıza ve iletişim kurduğu akademik simülasyon. | Mekanlar arası seyahat tetikleyicileri (Lab → Aday → Oda), etkileşim anı düşünce balonları, gün özeti akışı. | Python (Django), Phaser 3 istemcisi, OpenAI API | [Apache-2.0](https://github.com/joonspk-research/generative_agents) | [GitHub: joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents) | Evet |
| **Pixel Agents (VS Code)** | Terminalde koşan AI kodlama ajanlarını (Claude Code vb.) sanal bir piksel ofiste masalarında çalışan figürler olarak canlandıran araç. | Masa tahsis mantığı (seat assignment), göreve başlarken yürüyüp oturma, terminal çıktı durumuna göre animasyon. | TypeScript, VS Code Webview API, Canvas/CSS | [MIT](https://github.com/pixel-agents-hq/pixel-agents) | [GitHub: pixel-agents-hq/pixel-agents](https://github.com/pixel-agents-hq/pixel-agents) | Evet |
| **ChatDev (OpenBMB)** | CEO, CTO, Yazılımcı gibi rollerin sanal bir ofiste toplantılar yaparak yazılım geliştirdiği çoklu ajan simülasyonu. | Departmanlar arası hiyerarşik iş akışı, birimler arası mesaj zarfı transferi görselleştirmesi, rol bazlı replik motoru. | Python (FastAPI), Vue 3 Web Console | [Apache-2.0](https://github.com/OpenBMB/ChatDev) | [GitHub: OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev) | Evet |
| **WorkAdventure** | 16-bit RPG video oyunu tarzında tasarlanmış, self-hosted çalışabilen sanal iş birliği ve ofis platformu. | Tiled harita katmanları, odalara giriş-çıkış tetikleyicileri (zone collision), nesne etkileşimi (Jitsi/Iframe entegrasyonu). | TypeScript, Phaser 3, Node.js, WebRTC | [AGPL-3.0 + Commons Clause](https://github.com/workadventure/workadventure) | [GitHub: workadventure/workadventure](https://github.com/workadventure/workadventure) | Evet |
| **Gather (Gather.town)** | Kullanıcıların piksel avatarlarla ofis odalarında dolaştığı, masalara oturarak toplantı yaptığı popüler SaaS sanal ofis platformu. | Odaya odaklanma (camera pan/zoom), nesneye tıklayınca açılan modal çekmece, "rahatsız etmeyin" durum lambaları. | React, TypeScript, HTML5 Canvas / PixiJS | Ticari (Kapalı Kaynak) | [Gather Web](https://www.gather.town) | Evet |
| **Game Dev Tycoon** | Garajdan başlayıp büyük bir stüdyoya dönüşen oyun geliştirme şirketi yönetim simülasyonu. | Çalışanların kafasında uçuşan veri/puan parçacıkları, çalışan teftiş kartı, yorgunluk/verim animasyonları. | JavaScript, HTML5 Canvas, Node-Webkit | Ticari (Kapalı Kaynak) | [Greenheart Games](https://www.greenheartgames.com/app/game-dev-tycoon/) | Evet |
| **Two Point Hospital** | Hastane odalarının tasarlandığı, doktor ve hastaların tedavi aşamalarını takip eden mizahi yönetim oyunu. | Odaya çift tıklama ile zoom-in, tavanı kaldırma kesit görünümü, hasta/doktor ayrıntı kartında geçmiş ve ruh hali verisi. | Unity C# | Ticari (SEGA) | [Two Point Studios](https://www.twopointhospital.com) | Evet |
| **Project Hospital** | Departman hiyerarşisi ve gerçek tıbbi teşhis akışını izometrik derinlikle işleyen detaylı hastane simülasyonu. | Departman bazlı katman filtreleme (Risk, Finans vb.), seçili odayı aydınlatıp çevreyi karartma (dimming), oda durum ikonları. | Unity C# | Ticari (Oxymoron Games) | [Oxymoron Games](https://oxymoron.games/projecthospital/) | Evet |
| **Kairosoft Oyunları** | Game Dev Story, Mega Mall Story gibi piksel sanat izometrik yönetim ve işletme oyunları serisi. | Kompakt piksel replik kutuları, emoji reaksiyonları (ter damlası, alev, ampul), mikro animasyonlar. | C++ / Özel Mobil Motor | Ticari (Kairosoft Co.) | [Kairosoft Resmi Sitesi](https://kairosoft.net) | Evet |
| **Prison Architect** | Üstten bakış ve izometrik hapishane yönetim simülasyonu; lojistik ve güvenlik devriyeleri. | Birimler arası veri/emir akışını gösteren noktalı ok hatları (overlay layer), acil durum tecrit (lockdown) görseli. | C++, SDL, OpenGL | Ticari (Paradox Interactive) | [Introversion Software](https://www.introversion.co.uk/prisonarchitect/) | Evet |
| **Aggr.trade (Tucsky)** | Çoklu borsalardan anlık kripto vadeli işlem emirlerini ve likidasyonları görselleştiren gerçek zamanlı web panosu. | Canlı WebSocket beslemesi, işlem büyüklüğüne göre ses efektleri ve dinamik patlama parçacıkları (işlem hacmi = etki boyutu). | JavaScript, Vue.js, HTML5 Canvas, WebSockets | [GPL-3.0](https://github.com/Tucsky/aggr) | [GitHub: Tucsky/aggr](https://github.com/Tucsky/aggr) | Evet |
| **CryptoBubbles** | Kripto para performanslarını ve piyasa hacimlerini dinamik kabarcıklarla sunan görselleştirme aracı. | Tıklanan varlıkta kayan alt panel (bottom-sheet), renk kodlu gerçek performans göstergeleri (yeşil/kırmızı), yüksek scannability. | JavaScript / HTML5 Canvas (PWA) | Ticari (Ücretsiz Araç) | [CryptoBubbles Web](https://cryptobubbles.net/) | Evet |
| **Etre (X Copy Trade Ofisi)** | X üzerinde paylaşılan, algoritmik bir copy trade motorunu izometrik piksel ofis olarak tasvir eden konsept dashboard. | Odaların mantıksal ayrımı (Eleme, Aday, Kopyalanan Oda), trader'ların masalara atanması ve görselleştirilmesi. | *Doğrulanamadı* (Yalnızca X akışında video/görsel paylaşıldı; halka açık kaynak kodu veya teknik dokümantasyon yok) | *Doğrulanamadı* (Telif hakları özgün üreticisine ait) | *Doğrulanamadı* (Kalıcı açık URL / GitHub bağlantısı teyit edilemedi) | Doğrulanamadı |

---

## 2. Tasarım Önerileri

### 2.1. Odaya Girme, Etkileşim, Bilgi Kutusu ve Replik Sistemi
1. **Odaya Girme Geçişi (Zoom-In & Focus):**
   - *Two Point Hospital* ve *Project Hospital* modelleri esas alınmalıdır: Kullanıcı bina görünümünde bir odaya (örneğin "Oda" veya "Risk") tıkladığında kamera pan-ve-zoom yaparak odayı ekranın merkezine alır (yaklaşık 2.5x ölçek).
   - Çevre odalar kaldırılmaz; bunun yerine %25 opaklığa düşürülür veya hafif bir siyah sis (vignette) ile karartılır. Böylece kullanıcı bağlamdan kopmaz.
   - Odadan çıkış için sol üst köşede "Genel Bina Görünümü" (ESC tuşu veya geri butonu) ve ekrana çift tıklama kısayolu sunulmalıdır.
2. **Kişi ve Nesne Tıklama Etkileşimleri:**
   - Masadaki bir trader'a tıklandığında figür hafifçe zıplar (squash & stretch piksel zıplaması) veya dönüp kullanıcıya selam verir.
   - Nesneler (ör. Çay ocağındaki semaver, Denetim odasındaki dosya dolabı) tıklandığında küçük bir mekanik animasyon (buhar çıkması, dolabın açılması) sergiler.
3. **Bilgi Kutusu Düzeni (Modal & Drawer):**
   - Masaüstünde: Seçilen figürün sağ tarafında ekrandan kayan şık bir yan çekmece (Side Drawer).
   - İçerik Hiyerarşisi:
     - *Başlık:* Trader Rumuzu/Cüzdanı + Mevcut Statü Rozeti (Kopyalanıyor, Aday, Elemeyi Geçti).
     - *Gerçek Veri Bölümü:* 30G PnL, Win Rate, Sharpe Oranı, Kaldıraç, Max Drawdown, Aktif Pozisyonlar (Hyperliquid doğrulanmış verisi).
     - *Simülasyon Geçmişi:* Hangi tarihte Lab'dan çıktı, ne zaman odaya alındı.
4. **Birimler Arası İletişim İşaretleri:**
   - *Haberleşme Zarfı:* Telegram bildirimi tetiklendiğinde Haberleşme odasından bir ulak figürü çıkar, zarfı ilgili odaya taşır veya odanın üzerinden minik bir kağıt uçak uçar.
   - *Denetim / Risk Uyarısı:* Denetim odasındaki denetçi çalışan, risk eşiğini aşan trader'ın masasına doğru yürüyüp masaya sarı/kırmızı "Post-it" notu yapıştırır.
   - *Veri Boru Hatları (Pipeline Overlays):* Kullanıcı üst bardaki "Akış Çizgilerini Göster" düğmesine bastığında odalar arasında veri transferini gösteren noktalı neon akış çizgileri belirir.
5. **Replik ve Düşünce Balonları (Mizah vs. Veri Ayrımı):**
   - Replikler kesinlikle veri gibi sunulmamalıdır. Düşünce balonları piksel piksel yazı ile belirmeli ve esprili olmalıdır (ör. Çay Ocağında: *"RSI 80 oldu ama çay taze*", Risk Masasında: *"Kaldıraç 20x mi? Tansiyonum fırladı"*).
   - Gerçek sistem verisi içeren uyarılar ise köşeli, neon renkli "Sistem Kayıt Kartı" (Log Snippet) olarak gösterilerek görsel dil net biçimde ayrıştırılır.

---

### 2.2. Kullanıcı Bağlılığını Artıran Öğeler ve "Veri Çarpıtma Riski" Matrisi

Oyunlaştırma öğeleri kullanıcıyı ekrana bağlarken, projenin bilimsel/finansal güvenilirliğini zedelememelidir.

| Özellik | Açıklama ve Bağlayıcılık Mekanizması | Veriyi Çarpıtma Riski ve Alınacak Önlem |
| :--- | :--- | :--- |
| **Günlük Ofis Özeti (Morning Briefing)** | Her sabah açılışta gazete manşeti biçiminde dünün en çok kazandıran trader'ı, elenenler ve sistem PnL'ini gösteren piksel gazete sayfası. | **Risk (Düşük):** Finansal getiriyi sansasyonel kılabilir.<br>**Önlem:** Gazetenin altında küçük harflerle net kümülatif net PnL ve komisyon düşülmüş net rakam verilmelidir. |
| **Başarı Rozetleri (Badges)** | "Mükemmel Hafta", "Sıfır Tasfiye", "Risk Disiplini", "Kayıp Serisini Kırma" gibi trader başarı rozetleri. | **Risk (Yüksek):** Geçmiş başarı geleceğin garantisi değildir. Kullanıcı rozetli trader'a aşırı güvenebilir.<br>**Önlem:** Rozetler tamamen objektif formüllere bağlanmalı; rozetin yanına "Mevcut Drawdown: -%4.2" gibi gerçek risk metrikleri sabitlenmelidir. |
| **Zaman Atlamalı Tekrar (Timelapse Replay)** | Son 24 saat veya son 1 haftadaki ofis hareketlerini (terfiler, alarmlar, koşuşturmalar) 60 saniyede hızlandırılmış video/oynatıcı olarak izleme. | **Risk (Orta):** Hareket sıklığı piyasa volatilitesinin büyüklüğü ile yanlış eşleşebilir.<br>**Önlem:** Alt kısımda senkronize bir Hyperliquid PnL eğrisi akıtılmalı; zaman atlamasının hız çarpanı ekranda açıkça yazmalıdır. |
| **Ses Tasarımı (Chiptune & Ambient)** | 8-bit klavye tıkırtısı, faks/daktilo sesi, kâr alındığında hafif zil (ding!), tasfiye/stop alarmında hafif siren. | **Risk (Orta):** Aşırı ödül sesleri (slot machine etkisi) kumar algısı yaratabilir.<br>**Önlem:** Sesler varsayılan olarak kapalı (muted) gelmeli; ses seviyesi hafif ve profesyonel olmalı; kâr sesleri abartılı olmamalıdır. |
| **Dinamik Gün/Gece Döngüsü** | Kullanıcının yerel saatine veya New York/Tokyo seans saatlerine göre ofisin ışıklarının değişmesi, gece lambalarının yanması. | **Risk (Sıfır):** Tamamen estetik ve atmosferiktir; finansal veriye doğrudan etkisi yoktur, ancak veri bayatlığını (stale) örtmemelidir. |

---

### 2.3. Mobil Uyumluluk ve Telefonda Çalışma Stratejisi
- **Doğrudan İzometrik Görünümün Mobildeki Zorluğu:** Küçük ekranda 14 odayı aynı anda izometrik render etmek tıklamayı imkansızlaştırır (fat-finger problemi).
- **Mobil Çözüm Mimarisi:**
  1. *Varsayılan Mobil Modu (Oda Kartı / Akıllı Kamera):* Mobil cihaz algılandığında (ekran genişliği < 768px), ekran tüm binayı sığdırmak yerine doğrudan en aktif odaya ("Oda" veya "Adaylar") odaklanır.
  2. *Yatay Kaydırma ve Pinch-to-Zoom:* Kullanıcı iki parmağıyla yakınlaşıp uzaklaşabilir; çift dokunuş odayı tam ekrana yayar.
  3. *Alt Navigasyon Barı (Oda Seçici):* Ekranın altında ikonik bir "Oda Listesi" karuseli yer alır. Kullanıcı "Lab", "Finans", "Çay Ocağı" butonlarına basarak kamerayı doğrudan o odaya kaydırabilir.
  4. *Bottom Sheet (Aşağıdan Açılan Kart):* Figüre tıklandığında yan panel yerine mobil ergonomisine uygun olarak ekranın altından yukarı kayan yarım-ekran kart (Bottom Sheet) açılır.

---

## 3. Teknik ve Ürün Önerileri

### 3.1. Kütüphane Seçenekleri (Statik Site / GitHub Pages İçin)

GitHub Pages üzerinde derleme adımı olmadan veya çok hafif bir Vite/Vanilla kurulumuyla çalışacak kütüphanelerin kıyaslaması:

| Kütüphane | Artıları | Eksileri | Performans | Öğrenme Kolaylığı | Öneri Notu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PixiJS (v8)** | • Saf 2D render canavarı (WebGL/WebGPU).<br>• Sprite ve parçacık yönetiminde rakipsiz.<br>• Oyun döngüsü dayatmaz, pano mimarisine tam uyar. | • Kendi fizik motoru veya UI kütüphanesi yoktur; tıklama ve harita mantığını kendiniz kurarsınız. | ⭐⭐⭐⭐⭐ (En yüksek) | ⭐⭐⭐⭐ (Kolay-Orta) | **EN ÇOK ÖNERİLEN:** Statik bir web panosu için idealdir. Yalnızca görselleştirmeye odaklanır, gereksiz oyun motoru ağırlığı taşımaz. CDN üzerinden tek `<script>` ile derlemesiz çalışabilir. |
| **Phaser 3** | • Eksiksiz oyun motoru (kamera, animasyon, tilemap, ses, fizik hazır).<br>• WorkAdventure ve Smallville bunu kullanır. | • Paket boyutu büyüktür (~1MB bundle).<br>• Geleneksel DOM UI ile entegrasyonu Pixi'ye göre daha hantaldır. | ⭐⭐⭐⭐ (Yüksek) | ⭐⭐⭐ (Orta) | **Alternatif:** Eğer odalar arası karakter yürüyüşlerinde A* yol bulma (pathfinding) ve karmaşık fizik çarpışmaları gerekecekse tercih edilmelidir. |
| **Kaboom.js / Kaplay** | • Çok hafif, eğlenceli ve hızlı prototipleme.<br>• Kod tabanı son derece basittir. | • İzometrik projeksiyon ve derinlik sıralaması (Z-ordering / Y-sorting) için yerel desteği zayıftır. | ⭐⭐⭐⭐ (İyi) | ⭐⭐⭐⭐⭐ (Çok Kolay) | **Önerilmez:** İzometrik ofis derinlik sıralaması karmaşıklaştığında yetersiz kalır. |
| **Düz Canvas (Vanilla 2D)** | • Sıfır bağımlılık, sıfır derleme adımı.<br>• Tam kontrol. | • Her şeyi (kamera zoom, sprite animasyonu, fare tıklama koordinat dönüşümü) baştan yazmak gerekir. | ⭐⭐⭐ (Orta) | ⭐ (Zor/Zaman Alıcı) | **Önerilmez:** İzometrik tıklama koordinat matematiğini ve sprite batching'i elle yapmak gereksiz efor kaybıdır. |

**Nihai Teknik Karar:** **PixiJS (v8) + Vanilla JS / Vite**. PixiJS, izometrik Y-sorting (öndeki nesnenin arkadakini örtmesi) ve kamera zoom işlemlerinde GPU gücünü kullanırken, arayüz butonları ve modal bilgi kartları standart HTML/CSS ile kolayca çözülebilir.

---

### 3.2. Ticari Kullanıma İzin Veren Ücretsiz İzometrik Piksel Varlık Kaynakları

1. **Kenney.nl — Isometric Tiles & Furniture:**
   - *Açıklama:* 120'den fazla izometrik karo, duvar, masa, sandalye, bilgisayar ve ofis nesnesi.
   - *Lisans:* [CC0 1.0 Universal (Public Domain)](https://kenney.nl/assets/isometric-tiles-buildings) — Ticari kullanım, değiştirme ve atıfsız kullanım serbesttir.
   - *Kaynak:* [Kenney Isometric Assets](https://kenney.nl/assets/tag:isometric)
2. **Vexed — Isometric Template 32x32:**
   - *Açıklama:* İzometrik oda yapıları, zemin karoları ve eşyalar için temiz piksel karo şablonları.
   - *Lisans:* [CC0 1.0 Universal](https://v3x3d.itch.io/isometric-template) — Ticari kullanım serbest.
   - *Kaynak:* [itch.io Vexed Isometric Template](https://v3x3d.itch.io/isometric-template)
3. **Riclmbr — Interiors & City (509 Isometric Pixel Art Assets):**
   - *Açıklama:* İç mekan, ofis zeminleri (ahşap, seramik), masalar, bitkiler, ofis gereçleri.
   - *Lisans:* [CC0 1.0 Universal](https://riclmbr.itch.io/pixel-isometric-interiors-city-509-isometric-pixel-art-assets) — Ticari projeler dahil ücretsiz.
   - *Kaynak:* [itch.io Riclmbr Interiors](https://riclmbr.itch.io/pixel-isometric-interiors-city-509-isometric-pixel-art-assets)
4. **Kipperfalcon — Space & Modern Isometric Tileset:**
   - *Açıklama:* Modern/laboratuvar tipi elektronik masalar, paneller ve bilgisayar odaları için ideal karolar.
   - *Lisans:* [CC0 1.0 Universal](https://kipperfalcon.itch.io/free-space-isometric-pixel-art-32x32-tileset) — Ticari ve kişisel kullanım serbest.
   - *Kaynak:* [itch.io Kipperfalcon Isometric](https://kipperfalcon.itch.io/free-space-isometric-pixel-art-32x32-tileset)
5. **Screaming Brain Studios — 1,008 Isometric Floor Tiles:**
   - *Açıklama:* Farklı oda tipleri (Lab karo zemin, Makam halısı, Çay ocağı fayansı) için zengin zemin kütüphanesi.
   - *Lisans:* [CC0 1.0 Universal](https://itch.io/game-assets/assets-cc0/tag-isometric) — Ticari kullanım serbest.
   - *Kaynak:* [itch.io Screaming Brain Studios](https://screamingbrainstudios.itch.io/)

---

### 3.3. Ürünleşme, İş Modelleri ve Yasal Riskler

#### A. Veri Kaynağından Bağımsız Mimari (Data-Agnostic Engine)
Ofis motoru, Hyperliquid'e sıkı sıkıya bağlı (tightly coupled) olmamalıdır. Mimari 3 katmana ayrılmalıdır:
1. **Veri Bağdaştırıcısı (Data Adapter):** REST/WebSocket üzerinden Hyperliquid, Binance veya sentetik bir JSON beslemesini dinler; ham veriyi normalize edilmiş olaylara dönüştürür.
2. **Olay Veri Yolu (Event Bus):** `TRADER_PROMOTED`, `ALERT_TRIGGERED`, `DATA_STALE`, `POSITION_CLOSED` gibi olayları yayınlar.
3. **Görsel Sunum Katmanı (Office Renderer):** Hangi verinin nereden geldiğini bilmez; sadece olaylara göre animasyon oynatır. Bu sayede yarın aynı ofis bir hisse senedi fonu panosuna veya GitHub PR takip sistemine dönüştürülebilir.

#### B. Kişiselleştirme
- Oda ve çalışan isimleri, masaların yerleri ve ses ayarları `localStorage` üzerinde saklanmalı; "Ayarları Dışa Aktar / İçe Aktar (JSON)" imkanı sunulmalıdır.
- Kullanıcı dilediğinde Makam odasına kendi belirlediği patron avatarını ve sloganını koyabilmelidir.

#### C. Olası İş Modelleri ve Benzer Ürün Fiyatları
1. **Açık Kaynak Çekirdek + PRO Dağıtım (Open-Core):**
   - Temel GitHub Pages panosu açık kaynak.
   - *PRO Sürüm ($19 - $49/ay veya $299 tek seferlik):* Canlı Telegram/Discord bot entegrasyonu, çoklu cüzdan izleme, özelleştirilmiş kurumsal temalar. *(Emsal: Popüler crypto trading dashboard'ları aylık $20–$100 bandındadır).*
2. **Kişisel Klonlama Şablonu (Boilerplate Satışı):**
   - Kod tabanının kendi fonunu veya araştırma grubunu görselleştirmek isteyenlere Gumroad/GitHub Sponsors üzerinden satılması ($49 - $99).

#### D. Yasal Riskler ve Koruma Kalkanları
1. **Yatırım Tavsiyesi Riski (Regulatory Compliance):**
   - *Tehlike:* Trader kopyalama panosu, kullanıcılara "Bu trader'ı takip et kâr et" izlenimi verirse SPK, MiCA (AB) veya SEC nezdinde lisanssız portföy yöneticiliği veya yatırım danışmanlığı kapsamına girebilir.
   - *Önlem:* Sitenin açılışında net yasal uyarı (Disclaimer): *"Bu platform yalnızca akademik bir simülasyon ve görselleştirme araştırmasıdır. Buradaki hiçbir veri veya kurgusal temsil yatırım tavsiyesi niteliğinde değildir."* Panoda doğrudan "Hemen Kopyala / Gerçek Para Yatır" butonu yer almamalıdır.
2. **Varlık (Asset) Lisansları:**
   - CC0 lisanslı varlıklar güvenlidir; ancak internetten rastgele toplanan oyun sprite'ları (Habbo, Pokemon vb.) kesinlikle kullanılmamalıdır.
3. **Fikri Mülkiyet ve Etre Benzerliği:**
   - Etre'nin piksel tasarım öğeleri, renk paleti veya UI düzeni birebir kopyalanmamalı; ofis yerleşimi, oda tipleri (Çay ocağı, Makam vb.) özgün Türk ofis mizahı ve kendi araştırma dinamiklerimizle tasarlanmalıdır.

---

## 4. Ofisi Bağlayıcı ve Kullanışlı Yapacak 8 Özgün Fikir

| No | Özgün Fikir | Açıklama | Zorluk | Değer |
| :---: | :--- | :--- | :---: | :---: |
| **1** | **Çay Ocağı Dedikodu Tahtası (Alpha Feed)** | Çay ocağındaki kara tahtada, taranan trader'ların en son açtığı sıra dışı pozisyonlar veya piyasa anormallikleri mizahi dedikodu notları olarak akar (örn. *"Ahmet Abi BTC'de 50x long açmış, çayı yarım bıraktı"*). Gerçek Hyperliquid büyük pozisyon verisinden beslenir. | Düşük | Yüksek |
| **2** | **Likidasyon Siren ve Ambulans Animasyonu** | Kopyalanan havuzda veya takip edilen piyasada büyük bir tasfiye (liquidation) gerçekleştiğinde ofisin ışıkları anlık kırmızı yanıp söner ve sekreterlikten sedyeyle bir trader figürü revire/arşive taşınır. | Orta | Yüksek |
| **3** | **PnL Isı Haritası Halısı (Dynamic Floor Tint)** | Odaların veya trader masalarının altındaki halıların rengi, o günkü kümülatif PnL oranına göre dinamik olarak renk değiştirir (Yeşilin tonları = Kâr, Kırmızının tonları = Zarar). Sayı okumadan bir bakışta genel durum anlaşılır. | Düşük | Yüksek |
| **4** | **Zaman Makinesi (Tarihsel Replay Çubuğu)** | Ekranın altında bir zaman kaydırıcı (timeline slider). Kullanıcı geçmiş bir tarihi veya büyük bir piyasa çöküşü gününü seçtiğinde ofis o anki durumuna geri döner; figürler o günkü masalarına geçer. | Yüksek | Yüksek |
| **5** | **Stale Data "Ofis Grevi / Sis" Efekti** | Hyperliquid API'sinden veri akışı kesilirse veya 5 dakikadan uzun süre bayat kalırsa, çalışanlar masaları terk edip ofisin ortasında pankart açar veya ofisi gri bir sis kaplar. Gerçek veri ile bağlantı koptuğu anında anlaşılır. | Düşük | Yüksek |
| **6** | **Makam Odası "Patron Teftişi"** | Kümülatif drawdown %5'i aştığında Makam odasından takım elbiseli patron figürü hışımla çıkıp Risk ve Lab odalarını dolaşır; masalara kırmızı dosya çarpar. | Orta | Orta |
| **7** | **İnteraktif Terminal Masası (Mini TradingView)** | Lab odasındaki büyük sunucu ekranına tıklandığında ekran içinde gömülü piksel tarzında mini bir Hyperliquid canlı fiyat grafiği penceresi açılır. | Orta | Yüksek |
| **8** | **Ofis İçi Telegram Zarf Mancınığı** | Haberleşme odasında biriken bildirimler tek tek yürümek yerine küçük bir piksel mancınıkla ilgili odanın posta kutusuna fırlatılır. | Düşük | Orta |

---

## 5. Argon'un Denetim ve Mimari İnceleme Notları

> **Denetçi Notu (Argon):** *"Sistem tasarımını inceledim. Fikir vizyoner ve görsel olarak çekici, ancak bir mühendis ve risk denetçisi gözüyle şu kritik tuzakları masaya koymak zorundayım:"*

1. **GitHub Pages ve Statik Sitede Canlı Veri İllüzyonu:**
   - *Sorun:* GitHub Pages tamamen statiktir. Hyperliquid API'sine doğrudan tarayıcıdan bağlanmak isterseniz CORS kısıtlamalarına ve tarayıcı bazlı rate limit'lere (IP başına kota) takılabilirsiniz.
   - *Argon'un Çözümü:* İstemciyi doğrudan borsaya bağlamak yerine, arka planda koşan botunuzun durumu periyodik olarak (ör. 10-30 saniyede bir) bir `state.json` dosyasına yazmasını sağlayın veya Cloudflare Workers / hafif bir WebSocket relay üzerinden besleyin. Statik siteniz bu JSON dosyasını `fetch` etsin.
2. **Animasyon-Veri Senkronizasyonu (Gecikme Tuzağı):**
   - *Sorun:* Bir trader Lab'dan Aday odasına yürürken yürüyüş animasyonu 4 saniye sürebilir; bu sırada bot o trader'ı çoktan elemiş veya odaya terfi ettirmiş olabilir.
   - *Argon'un Çözümü:* Animasyonlar "Event Queue" (Olay Kuyruğu) mantığıyla çalışmalıdır. Eğer arka arkaya hızlı olaylar gelirse animasyon hızı 3x'e çıkmalı veya figür "ışınlanarak" anlık gerçek duruma kilitlenmelidir. Pano asla geçmiş bir animasyonun esiri olarak yanlış durum göstermemelidir.
3. **Piksel Art Y-Sorting (Derinlik Karmaşası):**
   - *Sorun:* İzometrik ofiste karakter masanın arkasından önüne geçerken katmanlama hatası olursa karakter masanın içine gömülür veya masanın üstüne basar.
   - *Argon'un Çözümü:* PixiJS içinde her hareketli ve sabit nesneye dinamik `zIndex = y + x` derinlik formülü uygulanmalı ve konteynerde `sortableChildren = true` aktif tutulmalıdır.
4. **Veri Kirliliği ve Regülasyon Koruması:**
   - *Sorun:* Kullanıcının oda ve çalışan isimlerini değiştirebilmesi güzel bir özellik; ancak bu isimler kopyalanan trader'ın gerçek cüzdan adresini gizlememeli veya tahrif etmemelidir.
   - *Argon'un Çözümü:* Kullanıcı görünen adı "Ahmet" yapsa bile, bilgi kartında orijinal Hyperliquid cüzdan adresi ve Explorer bağlantısı her zaman sabit ve değiştirilemez bir rozet olarak yer almalıdır.

---

## 6. İlk Yapılacak 5 İş (Sıralı Yol Haritası)

1. **Varlık Kütüphanesinin ve Karo Setinin İndirilip Hazırlanması:** Kenney CC0 Isometric setinden ofis masaları, sandalyeler, zeminler ve 4 yönlü yürüyen piksel karakter sprite-sheet'lerinin derlenip bir `assets/` klasöründe optimize edilmesi.
2. **Statik JSON Durum Şemasının (Schema) Tanımlanması:** Botun üreteceği ve panonun tüketeceği standart `office_state.json` şemasının (odalar, aktif trader'lar, koordinatlar, metrikler, son olaylar) dondurulması.
3. **PixiJS İzometrik Izgara ve Kamera İskeletinin Kurulması:** Derlemesiz hafif bir HTML/JS ortamında 14 odalık izometrik ızgaranın çizilmesi; tıklanan odaya yumuşak geçiş (zoom-in/pan) ve geri çıkış kontrollerinin kodlanması.
4. **Olay Yönetim Motoru (Event Engine) ve Yürüme Algoritmasının Yazılması:** `state.json` değiştiğinde trader figürlerinin eski masadan yeni odaya A* veya basit ızgara yoluyla yürümesini sağlayan olay dinleyicisinin entegre edilmesi.
5. **Bilgi Kutusu (Side Drawer) ve Yasal Sorumluluk Reddi Arayüzünün Eklenmesi:** Figüre tıklandığında açılan gerçek metrik panelinin, esprili replik balonlarının ve yasal uyarı metninin eklenerek GitHub Pages üzerinde ilk prototipin canlıya alınması.
