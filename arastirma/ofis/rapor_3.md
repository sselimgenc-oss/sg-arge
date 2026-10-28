# Ofis panosu v2: emsal araştırması ve öneriler

**Doğrulama notu:** "Doğrulandı" sütunundaki ✅ değeri, sayfayı (genelde GitHub deposunu) açıp okuduğum anlamına gelir. ◐ yalnız arama özetinden ya da ikincil kaynaktan geldi. ❌ bulunamadı ya da açılamadı.

**Etre bulunamadı.** "Etre" + Hyperliquid + piksel ofis için iki arama yaptım. İkisi de yalnız genel Hyperliquid copy-trade sayfaları döndürdü. X paylaşımına erişemiyorum. Etre'nin özelliklerini bildiğimi iddia etmiyorum. Yan yana kalite kontrolünü lider kendi gözüyle yapmalı.

---

## 1. Emsal tablosu

| Emsal | Ne yapıyor | Alınacak fikir | Altyapı | Lisans | Bağlantı | Doğrulandı |
|---|---|---|---|---|---|---|
| Generative Agents (Stanford, "Smallville") | Yapay zekâ ajanları sanal kasabada yaşıyor, planlıyor, konuşuyor. | Her eylemin kaydı tutuluyor. Biz de "her hareket bir olay" kuralını aynı mantıkla sürdürürüz. | Python sunucu, Django arayüz, Tiled haritaları, OpenAI API | Apache-2.0. Sanatçı kredileri: PixyMoon, LimeZu, ぴぽ. Yeniden kullanırsan destek istiyorlar. | [repo](https://github.com/joonspk-research/generative_agents) | ✅ |
| AI Town (a16z) | Ajanların yaşadığı, sohbet ettiği sanal kasaba başlangıç kiti. | Dağıtılabilir başlangıç kiti yaklaşımı. Sürekli çalışan simülasyonun tarayıcıya yansıtılması. | Convex (arka uç + motor), PixiJS (render), Clerk, Ollama/OpenAI | MIT. Tilesheet'ler OpenGameArt kaynaklı, lisansları tek tek kontrol edilmeli. | [repo](https://github.com/a16z-infra/ai-town) | ✅ |
| Pixel Agents (pablodelucca) | Her Claude Code oturumu için piksel ofiste animasyonlu karakter. Yazarken daktilo, ararken okuma, izin beklerken konuşma balonu. | En yakın teknik emsalimiz: olay → durum makinesi → animasyon. Düzen editörü, "Alan" kavramı, sesli bildirim. | React 19, Vite, **Canvas 2D**, Fastify, hook/JSONL olayları, WebSocket | MIT. Karakterler JIK-A-4 "Metro City" paketine dayanıyor. Varlık lisansı sayfada ayrıca belirtilmemiş. | [repo](https://github.com/pablodelucca/pixel-agents) | ✅ |
| Star Office UI | Ajan durumunu (idle, writing, error…) ofis bölgelerine eşleyen piksel pano. | Altı durum → altı bölge eşlemesi. "Dünün notları" kartı. Bayat durum otomatik idle'a döner. | Flask + Phaser, `POST /set_state` | **Kod MIT, sanat yalnız ticari olmayan kullanım için.** Misafir karakterler LimeZu ücretsiz paketinden. | [repo](https://github.com/ringhyacinth/Star-Office-UI) | ✅ |
| Agent Pixel Office (alex870715) | Çok ajanlı ekip için sıfır bağımlılıklı statik sayfa. | **Mimari olarak bizimkine en yakın örnek:** JSON dosyası → statik sayfa, 15 sn'de bir yeniden okuma. Devir-teslim animasyonu yalnız iki taraf da boş değilken. "Alarm" durumunda kırmızı parıltı. | Saf SVG karakterler, `office_status.json`, `board.json`, Vercel | MIT | [repo](https://github.com/alex870715/agent-pixel-office) | ✅ |
| OpenClaw Pixel Agents (SweetSophia) | OpenClaw ajanları için piksel ofis panosu. Ağ geçidi bağlı değilse örnek veri modu var. | Gerçek veri yokken "demo modu" bayrağı (bizim `ÖRNEK VERİ` etiketi gibi). Sürükle-bırak mobilya editörü. | React/TypeScript | MIT (arama özetinde) | [repo](https://github.com/SweetSophia/openclaw-pixel-agents) | ◐ |
| Pixel Office (gonzalonicolasr) | Düzenlenebilir roller, yönlendirici lider ajan, masaya yönlendirilen mesajlar. | **Çalışan/rol adlarını kullanıcının düzenlemesi** için örnek. Mesajın bir masadan diğerine gittiğini gösterme. | Three.js + React | MIT (arama özetinde) | [repo](https://github.com/gonzalonicolasr/pixel-office) | ◐ |
| WorkAdventure | 16-bit RPG görünümlü sanal ofis. Yaklaşınca görüntülü sohbet açılır. | Yakınlık = etkileşim. Harita editörü ve harita depolama servisi ayrı. | TypeScript, Docker/Helm, Redis, LiveKit. Phaser kullanımı doğrulanamadı. | **AGPL v3 + Commons Clause.** Çevrimiçi hizmet olarak satmak yasak. | [repo](https://github.com/workadventure/workadventure) · [lisans SSS](https://workadventu.re/faq/what-is-the-license-of-the-self-hosted-version-of-workadventure/) | ✅ |
| Gather (Town) | Ticari sanal ofis. | Fiyat çıpası (aşağıda). | Doğrulanamadı | Kapalı kaynak, ticari | [fiyat duyurusu](https://support.gather.town/hc/en-us/articles/39590892978196) | ✅ fiyat · ❌ altyapı |
| Kairosoft (Game Dev Story vb.) | İzometrik piksel yönetim oyunları. | Çalışanın üstünde **emoji/ikonlu kısa balonlar**: bir bakışta ne yaptığını anlatır, menüye girmeye gerek bırakmaz. | Doğrulanamadı | Ticari oyun | [PocketGamer](https://www.pocketgamer.com/articles/024481/game-dev-story/) · [Wikipedia](https://en.wikipedia.org/wiki/Kairosoft) | ◐ |
| Two Point Hospital | 3B hastane yönetimi. | Odayı tıklayınca bilgi paneli. Fareyle odanın üzerine gelince bekleyenlerin üstünde sayı. Personel sekmesinde maaş, ruh hali, beceri tablosu. | Doğrulanamadı | Ticari oyun | [UI rehberi](https://www.magicgameworld.com/two-point-hospital-ui-and-reading-your-menus/) | ◐ |
| Project Hospital | Hastane yönetimi. | Personel ihtiyaç göstergeleri (açlık, dinlenme…) yalnız bir mod sayfasından çıkarım. Eleştiri: küçük yazı tipi. | Doğrulanamadı | Ticari oyun | [ModDB](https://www.moddb.com/games/project-hospital) | ◐ |
| Prison Architect (2) | Hapishane yönetimi. | İhtiyaçlar hiyerarşisi (temel → iyi oluş → ıslah). Tablet sürümü dokunmatik için baştan tasarlandı. | Doğrulanamadı | Ticari oyun | [PA2 haberi](https://www.paradoxinteractive.com/zh-CN/games/prison-architect-2/news/feature-highlight-prisoner-needs) · [Wikipedia](https://en.wikipedia.org/wiki/Prison_Architect) | ◐ |
| The Sims (3/4) | Yaşam simülasyonu. | Portrenin yanında **ruh hali ikonları** ve "neden" bilgisi. İkon sayısı çok (4'te 1000+), yani ikon dilini küçük tutmak gerek. | Doğrulanamadı | Ticari oyun | [Moodlet wiki](https://sims.fandom.com/wiki/Moodlet) | ◐ |
| Game Dev Tycoon | Oyun şirketi simülasyonu. | **Kaçınılacak örnek:** personel yönetimi menülerin içinde gömülü, eleştiri alıyor. Biz doğrudan masaya tıklamayı tercih ederiz. | Doğrulanamadı | Ticari oyun | [TechRaptor](https://techraptor.net/content/tag/game-dev-tycoon) | ◐ |
| Habitica | Görevleri RPG'ye çeviren oyunlaştırma. | Seviye, ödül, grup görevi mantığı. Bağlılık öğeleri için referans. | Doğrulanamadı | Kaynaklar çelişiyor (GPL v3 / MIT). Bazı varlıklar CC-BY-SA ve CC-BY-NC-SA. Resmî LICENSE dosyasına bakılmadı. | [Wikipedia](https://www.wikipedia.org/wiki/Habitica) | ◐ |
| Hyperliquid copy-trade ürünleri (BitMEX entegrasyonu, Hyperdash, HyperX vb.) | Liderlik tablosu: PnL, düşüş (drawdown), kazanma oranı, AUM. | Hangi metriklerin "standart" sayıldığını gösterir. Hiçbirinde oyunlaştırma ya da ofis metaforu bulamadım. | Doğrulanamadı | Ticari | [BitMEX](https://www.bitmex.com/blog/how-to-copy-trade-hyperliquid) · [OneKey](https://onekey.so/blog/ecosystem/copy-trading-on-hyperliquid/) | ◐ |
| Etre (X'te paylaşılan copy-trade ofisi) | — | — | — | — | — | ❌ doğrulanamadı |

**Kapsam notu:** "Oyunlaştırılmış trading panosu" için açık kaynak ya da ticari doğrudan emsal bulamadım. Arama yalnız sıradan kripto panoları ve tasarım şablonları döndürdü. Boşluk gerçek olabilir ya da aramam yetersiz kalmış olabilir. Ek bulgu: ajan-ofis kategorisinde başka depolar da var (pixtuoid, Hermes Pixel Office, bit-office, pixeloffice.org). Açmadım, o yüzden tabloya almadım.

---

## 2. Tasarım önerileri

### Odaya girme geçişi
- **Aynı tuvalde kamera yakınlaştırması** (zaten `focusRoom` kameramız var). Yakınlaşırken diğer odalar soluklaşır, seçili odanın duvar ve çatısı kalkar. Ayrı sahneye geçmek yerine bağlam korunur.
- Pixel Agents'ın "Alan" kavramı gibi her odanın kendi sınırı olsun. Çıkış: `Esc`, geri düğmesi, boş yere tıklama.
- İç görünümde ayrıntılanacaklar: masa, ekran içeriği, dolap/raf, kişi. Veri gösteren her nesne (ekran, pano) gerçek alandan beslenir.
- Hareket azaltma tercihi açıksa geçiş anlıktır.

### Tıklama etkileşimi ve bilgi kutusu
- Kişi/nesneye tıklayınca **sabit konumlu panel** açılır (nesnenin üstünde değil), böylece telefonda da aynı bileşen kullanılır. Two Point Hospital'ın personel paneli düzeni ve Prison Architect'in öncelik sıralaması örnek.
- Panel üç bölüm: (1) **Kimlik** (ad, rol, oda), (2) **Gerçek veri** (zaman damgası ve n ile), (3) **Replik/eğlence**, görsel olarak ayrı ve "ofis esprisi" etiketli.
- Küçük tepki animasyonu: tıklanan figür bir kare başını çevirir ya da kısa bir baloncuk gösterir. Bu **veri değiştirmez**, kalıcı olmaz.

### İletişim işaretleri
- **Zarf taşıyan figür** (Haberleşme), **not kağıdı** (denetçi → trader masası), **ok** (Kapı → Lab). Pixel Agents'ta alt ajanların ebeveyne bağlı görünmesi ve Agent Pixel Office'teki "iki taraf da boş değilse devir-teslim" kuralı iyi ölçüt.
- Her işaret bir **olay kaydına** bağlı olsun (`OLAYLAR.md`'ye yeni satır). Olay yoksa işaret yok.
- Ok renk/biçimi olay türüne göre sabit olsun. Süs amaçlı ok/zarf çizmeyin, veriyle karışır.

### Replik sistemi
- Kairosoft'taki gibi **ikon önce, metin sonra**: balonda ikon, tıklayınca tam cümle.
- İki sınıf: **olay repliği** (gerçek olaydan, örn. "T031 terfi etti") ve **süs repliği** (çay/kahve esprisi). Süs repliği her zaman soluk, farklı çerçeveli; içinde **sayı, adres, oran asla bulunmasın**.
- Replik havuzu JSON'da dursun, kullanıcı değiştirebilsin.

### Bağlılık öğeleri

| Öğe | Fikir | Veriyi çarpıtma riski |
|---|---|---|
| Günlük özet | Açılışta "dün: 3 terfi, 1 elenme, 2 bildirim" | **Düşük**, olay günlüğünden türetilirse. Boş günde "değişiklik yok" demeli. |
| Başarı rozetleri | "İlk 30 gün", "10 terfi" | **Orta.** Kâr rozeti riskli, kullanıcıyı kötü kararlara iter. Süreç rozetleri (veri taze tutuldu) daha güvenli. |
| Zaman atlamalı tekrar | Günün olaylarını 30 sn'de oynat | **Orta.** Gerçek zamanlı olmadığı açık yazılmalı, "TEKRAR · 60×" etiketi sabit durmalı. Sıralama bozulmamalı. |
| Ses | Yeni olayda hafif tık, alarmda farklı ton | **Düşük**, olay başına bir ses, varsayılan kapalı. |
| Gün/gece | Gerçek saatle ışık (zaten var) | **Düşük.** Gece "piyasa kapalı" izlenimi vermesin. Hyperliquid 7/24 açık. |
| Seri (streak) | "7 gün üst üste açtın" | **Orta-yüksek.** Kullanıcıyı sürekli bakmaya iten alışkanlık yaratabilir. Önermem. |

### Telefon
- Tek sütun: önce **liste/özet**, ofis altta. Odaya dokunma = yakınlaşma, ikinci dokunma = bilgi paneli (alttan çekmece).
- Hover yok: bilgi dokunmayla açılır. Açık "bilgi" düğmesi.
- Dokunma hedefi ≥44 px. Küçük figürlerin yakalama alanı görselden büyük.
- Prison Architect tablet sürümü arayüzü dokunmatik için baştan tasarlamış ([kaynak](https://www.tag-games.com/prison-architect)). Masaüstünü küçültmekle yetinmeyelim.

---

## 3. Teknik ve ürün önerileri

### Kütüphane seçimi

| Seçenek | Artı | Eksi | Not |
|---|---|---|---|
| **Düz Canvas 2D** (şu anki) | Derleme yok, bağımlılık yok, tam kontrol. Pixel Agents de kullanıyor. | Sahne grafiği, giriş, kamera elle yazılır. | Zaten çalışıyor (~185 KB). |
| PixiJS (MIT) | WebGL/WebGPU, dokunma, filtreler. | Ek bağımlılık. Boyut doğrulanamadı. | Sprite sayısı artarsa. AI Town kullanıyor. |
| Phaser (MIT) | Eksiksiz oyun çatısı. | `phaser.min.js` **1,29 MB (345 KB gzip)** ([repo](https://github.com/phaserjs/phaser)). Bizim için fazla. | Etkileşim ağırlıklı oyun olsaydı. |
| KAPLAY (MIT) | Öğrenmesi kolay, bileşen tabanlı. | İzometrik/kamera desteği doğrulanamadı. | Prototip için. |
| SVG (Agent Pixel Office) | Sıfır bağımlılık, DOM erişilebilirliği. | Çok figürde yavaşlar (**tahmin**). | Arayüz öğeleri için. |

**Önerim: Canvas 2D'de kal.** Kod zaten bunun üzerine kurulu, derleme gerektirmiyor, Pixel Agents aynı yaklaşımla çalışan bir ürün. PixiJS'e geçiş, ancak gerçek GPU'lu makinede `?perf=1` ile ölçülen bir 60 fps sorunu çıkarsa gündeme gelsin. Bilgi kutusu ve tooltip'ler HTML/CSS katmanında kalsın (erişilebilirlik).

### Ticari izinli ücretsiz varlıklar

| Kaynak | Ne var | Lisans | Uyarı |
|---|---|---|---|
| [Kenney Isometric Assets](https://kenney.itch.io/kenney-isometric-assets) | Zindan, prototip, kütüphane, çiftlik karoları | CC0 | Sayfa indirmeyi "kullanılamıyor" gösteriyor. Piksel sanat mı render mi belirtilmemiş. Ofis mobilyası yok. |
| [Kenney Isometric Blocks (OGA)](https://opengameart.org/content/isometric-blocks) | 130+ blok karosu | CC0 | Ofis temalı değil. |
| [Kenney Isometric Miniature Dungeon (OGA)](https://opengameart.org/node/66688) | Duvar, zemin, mobilya | CC0 | Zindan teması. |
| [Screaming Brain Isometric Object Pack](https://screamingbrainstudios.itch.io/isometric-object-pack) | İzometrik nesneler | CC0 | Mobilya kategorisi "yakında". |
| [luke1985 Isometric office 1/2 (OGA)](https://opengameart.org/content/isometric-office-1) | SVG ofis **binası** | CC0 dahil çoklu | İç mekân değil. |
| LimeZu Modern Office | Üstten görünüm ofis karoları | **Doğrulanamadı** (kardeş paket için yorum: kredi şartıyla ticari kullanım) | İzometrik değil. Lisans README'den kontrol edilmeli. |

**Dürüst sonuç:** Doğrulanmış CC0 izometrik **piksel ofis mobilyası** paketi bulamadım. Kendi çizdiğimiz varlıklar (sıfır dış varlık) bu yüzden en güvenli yol. Star Office UI örneği ürünleşme için uyarı: kod MIT olsa da sanat ticari kullanıma kapalı.

### Ürünleşme
- **Mimari:** Veri kaynağından bağımsız olsun. Zaten bu yöndeyiz: `ornek_durum.json` + `SEMA.md`. Adımlar: "bağdaştırıcı" katmanı (Hyperliquid → şema), şema sürümü (`surum`), olay akışı ayrı uç nokta.
- **Kişiselleştirme:** Oda/çalışan adları, replik havuzu, renk teması, ofis düzeni (JSON içe/dışa aktarım). Ad değişikliği yalnız etiketi değiştirir, veri alan adlarını değil.
- **İş modeli (tahmin, doğrulanmadı):** (a) ücretsiz açık çekirdek + ücretli barındırma, (b) tema/varlık paketleri, (c) takım/kurum lisansı. WorkAdventure'ın Commons Clause'u, "başkası SaaS yapmasın" korumasının nasıl yazıldığını gösteriyor.
- **Fiyat çıpası:** Gather **$12/kullanıcı/ay (yıllık), $15 (aylık)**, ücretsiz katman yok ([kaynak](https://support.gather.town/hc/en-us/articles/39590892978196)). Bu bir sanal ofis, benzer ürün değil; yalnız "ofis metaforuna ödenen" tavanı gösterir. WorkAdventure ve diğerlerinin güncel fiyatını doğrulayamadım.
- **Yasal riskler** (hukuki görüş değildir, avukata danışılmalı):
  - **Yatırım tavsiyesi sayılma riski:** "terfi", "kopyala" gibi dil öneri gibi okunabilir. Her ekranda "araştırma/sanal, tavsiye değil" ibaresi; gerçek parayla kopyalamaya yönlendiren düğme olmamalı. Düzenleme ülkeye göre değişir (**tahmin:** AB'de MiCA, Türkiye'de SPK; doğrulamadım).
  - **Varlık lisansları:** Her varlık için kaynak/lisans tablosu (şu an `LISANSLAR.md`). Kredi şartları ürün içinde görünür olmalı.
  - **Başka ürüne benzerlik:** Etre'nin görsel diline yaklaşmamak. Kendi paletimiz ve karakter dilimiz tutarlı kalsın.

---

## Kendi önerilerim

| # | Fikir | Zorluk | Değer |
|---|---|---|---|
| 1 | **"Neden böyle?" düğmesi:** her figürün/ekranın yanında, o durumu doğuran olayı ve kaynağını gösteren tek satır. Güveni artırır. | Düşük | Yüksek |
| 2 | **Olay çekmecesi + filtre:** izleyici günlüğünü oda/trader/olay türüne göre filtrele, olaya tıklayınca kamera o odaya gitsin. | Düşük | Yüksek |
| 3 | **Dünden bu yana fark:** ofiste "değişenler" vurgusu (yeni masa, boşalan masa). | Orta | Yüksek |
| 4 | **Bayatlık göstergesi her yerde:** her ekranın köşesinde "X dk önce". Veri bayatlayınca ekran sönsün. | Düşük | Yüksek |
| 5 | **Aday karşılaştırma masası:** iki trader'ı yan yana gösteren özel oda görünümü. | Orta | Orta |
| 6 | **Salt-okunur paylaşım bağlantısı:** `?durum=URL` ile başkasının JSON'unu görme (ürünleşme için). | Orta | Yüksek |
| 7 | **Tema/ofis düzeni dışa-içe aktarma:** kullanıcı kendi düzenini paylaşır. | Orta | Orta |
| 8 | **Erişilebilir "metin ofisi":** tüm durumun klavyeyle gezilen liste hâli. | Orta | Orta |
| 9 | **"Sessiz gözlemci" ses profili:** yalnızca alarmda bir ton. | Düşük | Orta |

---

## İlk yapılacak 5 iş

1. **Oda içi görünüm prototipi** (tek oda, mevcut kamerayla yakınlaşma + duvar/çatı kaldırma + `Esc`), önce Lab odasında.
2. **Ortak bilgi kutusu bileşeni** (HTML katmanı: Kimlik / Gerçek veri / Replik ayrı bölümler, telefonda alttan çekmece).
3. **Replik sistemi şeması:** `repliks.json` (olay repliği ve süs repliği ayrı alanlar; süs repliklerde rakam yasağı için basit bir test).
4. **İletişim işaretleri için `OLAYLAR.md` genişletmesi:** zarf, not kağıdı, ok. Her biri bir olay türüne bağlı, olay yoksa çizilmez.
5. **Ad değiştirme (oda/çalışan) için `kullanici_ayarlari` şeması + yerel depolama**, ardından Faz 5'te gerçek `durum.json` bağlama ve gerçek GPU'da `?perf=1` ölçümü.
