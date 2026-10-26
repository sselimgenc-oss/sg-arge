# Faz 2 notları (kullanıcı istekleri, Faz 1 kapanınca ele alınacak)

## 1. Strateji radarı (yeni strateji yakalama)
- **Amaç:** Haftalık bir GitHub Actions işi, mevcut kartların geldiği sitelerden yeni stratejileri toplar.
- **Kaynaklar (kart sayısına göre):** TradingView 54, GitHub 41, ProRealCode 32, MQL5 26, ForexFactory 21, QuantifiedStrategies 34.
- **Kolay kaynaklar:**
  - RSS: QuantifiedStrategies, Substack;
  - GitHub arama API'si;
  - PapersWithBacktest;
  - r/algotrading;
  - ProRealCode kütüphanesi.
- **Zor kaynaklar:** TradingView (kullanım şartları, JavaScript), MQL5 ve ForexFactory (forum, giriş gerektiren içerik). Bunlar dışarıda kalır ya da linkleri kullanıcı elle ekler.
- **Akış:** tara → mevcut 422 kartla tekrar ele (URL + isim benzerliği) → `docs/radar/<yıl>-W<hafta>.md` PR'ı → ajan kartı yazar (uydurma yok) → `huni.yml`.
- **Kısıtlar:** Yalnız ücretsiz kaynaklar. Giriş yapılmaz, form doldurulmaz. Kart yazımı ajanla yapılır; otomatik LLM çağrısı ücretli olduğu için yalnız kullanıcı onayıyla eklenir.

## 2. strateji-test-pano: Faz 2 arayüzü
**Kullanıcı kararı:** Bu depo arayüz ve fikir taslağı olarak hazırlandı; içindeki stratejiler ve rakamlar önemli değil. Faz 1'den sonra bu arayüz bizim gerçek sonuçlarımızla doldurulup faaliyete alınacak.

Lider analizi (2026-10-22): Bu depodaki özellikler **arayüz taslağı**. Değerleri `data.json` içine elle yazılmış; onları üreten kod yok.
- `bot_engine.py` yalnız Binance'ten 10 kripto fiyatı çekip açık pozisyonların kâr/zararını günceller.
- "Claude'a sor" gerçek bir yapay zekâ çağrısı değil; anahtar kelimeye göre önceden yazılmış cevap seçer.
- "Gölge mod" (makine öğrenmesi filtresi) ve "Koç" bulguları `data.json`'da sabit metin. Model eğitimi ya da hesap kodu yok.
- Paneldeki performans rakamları (271 işlem, Sharpe 2.44, CAGR %42.6 vb.) doğrulanmış bir backtest'ten gelmiyor; kullanılmamalı.

Faz 2'de gerçek veriyle kurulabilecek olanlar:
- **a. İşlem açıklamaları:** Motor her işlemin giriş/çıkış nedenini zaten kaydediyor (`stop`, `hedef`, `gap_target`, `zaman_stop`...). Paper defterine "neden açıldı / neden kapandı" sütunu eklenebilir. Kolay iş.
- **b. Koç bulguları:** `results/` ve paper defterinden otomatik üretilebilir: hangi strateji zararda, hangi çıkış nedeni baskın, korelasyon. Kurallı metin, kolay iş.
- **c. Gölge mod (ML filtresi):** Her sinyal için geçmiş işlemlerden "bu işlemin R'si" tahmin edilir; negatifler pas geçilir, ama yalnız gölgede, yani gerçek defter etkilenmez. Aşırı uyum riski yüksek olduğu için:
  - walk-forward eğitim;
  - ön kayıt;
  - en az 6 ay gölge kayıt;
  - filtreli ve filtresiz defter karşılaştırması.

  Önce gölgede kanıtlanmadan kullanılmaz.
- **d. "Claude'a sor":** Gerçek bir soru-cevap için ya ücretli bir API ya da artifact yetenekleri (runtime) gerekir. Kullanıcı kararı.

## 3. Birleşik pano (kullanıcı kararı, 2026-10-22)
- **Arayüz:** `strateji-test-pano` (zengin arayüz) ile `sg-test-panel` (sade, `paper/panel.py` şeması zaten bu panoya uyuyor) birleştirilecek. Tek pano; veri `paper/` ve `results/`'tan gelir.
- **Kullanıcının en çok önem verdiği iki modül:**
  1. **Öğrenen koç (ML):** Pano açtığı işlemlerden öğrenir, stratejinin açıklarını bulur, düzeltme **önerisi** sunar.
  2. **Strateji radarı:** Bölüm 1.

### Öğrenen koç: güvenli tasarım (lider önerisi)
- **Veri:** Paper işlemleri tek başına az (birkaç strateji, yılda ~100 işlem). Öğrenme, backtest işlem kayıtlarından (`results/tarama_islemler`, huni koşusuyla yeniden üretilir; repoda tutulmaz) yapılır; paper işlemleri doğrulama içindir.
- **Ne öğrenir:** Kaybeden işlemlerin ortak özellikleri. Örnekler: rejim (trend/yatay, volatilite), giriş anındaki gösterge değerleri, gün/saat, sembol, çıkış nedeni dağılımı. Yöntem: yorumlanabilir modeller (karar ağacı, gradient boosting + SHAP). Kara kutu kullanılmaz.
- **Ne üretir:** Öneri kartı. Örnek: "ADX<15 iken girişlerin ortR −0.4; filtre eklenirse IS PF 1.3→1.6".
- **Öneri otomatik uygulanmaz.** Her öneri yeni bir **varyant kart** olur ve aynı huniden geçer: 2a, 2b, OOS.
- **Çoklu deneme sayacı:** Her denenen öneri DSR deneme sayısına eklenir. Koç ne kadar çok öneri denerse eşik o kadar yükselir. Aksi halde koç geçmişe uyan sahte iyileştirmeler üretir.
- **Doğrulama:** Önerilen varyant önce **gölge modda** paper'da en az 3–6 ay orijinalin yanında koşar. Yalnız orijinali anlamlı biçimde geçerse kullanıcı onayıyla devreye alınır.
- **Açıklama:** Her öneri "neden" ile gelir: hangi işlemler, kaç örnek, IS/OOS farkı, deneme sayısı.

## 4. Copy trade (kullanıcı isteği, 2026-10-25)
Araştırılacak; Sol 6.1 (Codex) de fikir sunacak.
**Yön (kullanıcı kararı, 2026-10-25):** yalnız başarılı olanları **biz kopyalayacağız**. Kendi sinyallerimizi kopyalatmak ya da yayımlamak amaç değil.
Sorular:
- **Kaynaklar:** Binance copy trading lider portföyleri, Bybit/OKX/Bitget lider listeleri, eToro, ZuluTrade, MT5 sinyalleri. Hangisi Türkiye'den ve bizim hesaplarımızdan (Binance, Gedik MT5) kullanılabilir?
- **Kopyalanan lider için doğrulama:** yayımlanan performans hayatta kalma yanlılığı taşır. Kendi test yapımız uygulanabilir mi: sadece katıldıktan sonraki dönem, gerçekçi maliyet, kayma, gecikme?
- **Teknik yol:** Binance copy trading API var mı, sınırları ne? Lider işlemleri nasıl okunur? Kopyalama gecikmesi ve kaymanın ölçülmesi.
- **Risk:** %10 zarar bütçesine dahil mi, ayrı mı? Lider başına sınır, kaldıraç sınırı, ani lider değişimi.
- **Hukuk ve vergi:** Türkiye'den yabancı platformda kopyalama ve kazancın vergisi (kullanıcı ve uzman kararı).
- **Bakılacak platform (kullanıcı notu, 2026-10-25):** [Hyperdash copy trading](https://hyperdash.com/copytrading).
  - Hyperliquid (zincir üstü perp DEX) üzerindeki cüzdanları izleyip kopyalama.
  - Artısı: işlemler zincir üstünde açık, bu yüzden liderin geçmişi doğrulanabilir; hayatta kalma yanlılığını kendi verimizle ölçebiliriz.
  - Bakılacaklar:
    - kopyalama nasıl yürütülüyor: kendi cüzdanımız mı, emanet mi, API ajan anahtarı mı;
    - ücret ve kayma;
    - Türkiye'den erişim ve hukuki durum;
    - Binance hesabımızla ilişkisi: ayrı cüzdan ve USDC gerekir.
- **Argon derin araştırması (2026-10-25):** `arastirma/copytrade/copy_trading_derin_arastirma_2026.pdf` (23 s.). Kapsam: kripto, BIST/VİOP, ABD hisse, emtia/forex.
  - **Önerdiği seçenekler (varlık sınıfı başına 2):**

    | Varlık | Öneri 1 | Öneri 2 |
    |---|---|---|
    | Kripto | Hyperliquid vault/cüzdan + Hyperdash/Copin. Zincir üstü tam geçmiş, ücretsiz API (`api.hyperliquid.xyz/info`), kendi cüzdan | Binance Copy Trading. Önce sanal izleme; kâr payı ödemek yerine kendi API botumuzla kopyalama |
    | BIST/VİOP | Türkiye'de üçüncü kişiyi kopyalamak SPK'ya göre yasal değil (izinsiz danışmanlık). Yasal yol: Gedik + Matriks IQ/İdealAlgo ile kendi algoritmamız | Başarılı yöneticilerin TEFAS hisse/serbest fonları + Gedik model portföy |
    | ABD hisse | SEC EDGAR 13F (ücretsiz resmi API): düşük devirli 5-10 fon, Gedik MT5/IBKR ile. Autopilot/Dub Türkiye'ye kapalı | Hyperliquid HIP-3 hisse perp'leri (USDC teminat) |
    | Emtia | Binance Futures copy trading TradFi perp (XAU, XAG, CL, BZ) | MQL5 Signals + Gedik MT5 (SPK 1:10 kaldıraç sınırına uygun sinyaller) |

  - **Akademik kanıt:**
    - Takipçilerin ortalama net getirisi sıfır ya da negatif (Apesteguia ve ark. 2020; Dorfleitner ve ark. 2018).
    - Lider takipçi kazanınca performansı bozuluyor: ortalamaya dönüş ve eğilim etkisi (Pelster ve Hofmann 2018).
    - Politikacı işlemlerini kopyalamada bildirim gecikmesi (30-45 gün) avantajı siliyor.
    - 13F kopyalama yalnız düşük devirli, yoğun portföylü fonlarda işe yarıyor.
  - **Kırmızı bayraklar:**
    - %90+ kazanma oranı ama özsermaye sarkıyor (martingale/grid);
    - açık pozisyonlarını gizleyen lider;
    - 180 günden genç hesap ya da liderin kendi sermayesi az (ikiz hesap hilesi);
    - sığ altcoinlerde işlem;
    - Telegram/WhatsApp "VIP sinyal" grupları.
  - **Sanal izleme için veri:** Hyperliquid ve Copin (geçmiş silinmez), Darwinex API, MQL5/Myfxbook (silinebilir, günlük kayıt gerekir), SEC EDGAR, Binance/OKX/Bybit (lider kapanınca geçmiş silinir; yalnız bizim kaydettiğimiz ileriye dönük veri güvenilir).
    - Rapor her platform için maliyet ve kayma modeli de öneriyor (Tablo 5).
  - **Lider yorumu:** Yön bizim TEST_YAPISI ile uyumlu: önce sanal izleme, liderin izlemeye başladığımız günden sonraki dönemi, gerçekçi maliyet. Dikkat:
    - Bazı tarih ve kaynaklar doğrulanmalı. Örneğin "UPenn Mayıs 2026" ve "Meng & Fang Haziran 2026": son kaynak listesindeki link başka bir başlığa gidiyor.
    - Hukuk ve vergi kısımları (SPKn m.107/109, 32 sayılı karar, %10 stopaj) uzmana sorulacak; karar kullanıcının.
    - En hızlı başlanacak deney: Hyperliquid cüzdan/vault sanal izleme. Ücretsiz API, tam geçmiş, para bağlamadan.
- **"Başarılı" ölçütü:** TEST_YAPISI'na göre tanımlanır. Liderin bizim izlemeye başladığımız tarihten sonraki dönemi, gerçekçi maliyet, düşüş, kaldıraç ve hesap yaşı esas alınır. Önce sanal havuzda (gölge) izlenir, gerçek para sonra.

## 5. Pano: HTML'den uygulama altyapısına geçiş (kullanıcı isteği, 2026-10-25)
Bugünkü durum: `paper/panel/data.json` → `sg-pano` statik HTML (GitHub Pages), 3,5-5 saatte bir güncelleniyor. Sol 6.1 de fikir sunacak. Değerlendirilecek seçenekler:
- **Statik kalıp güçlendirme:** aynı JSON, modern ön yüz (React/Vite ya da Svelte), GitHub Pages. En ucuzu; canlı veri yok.
- **Python panosu:** Streamlit / Dash / Panel. Hızlı, Python kodumuzla aynı dil; sunucu gerekir (Streamlit Community Cloud, Fly.io, küçük VPS).
- **Arka uç + ön yüz:** FastAPI + veritabanı (SQLite/Postgres) + React. Canlı fiyat, emir geçmişi, kullanıcı girişi, Telegram geri bildirimi (Faz 3 "uyguladım/atladım" butonu) için doğru temel; bakım yükü yüksek.
- **Mobil:** PWA (aynı web uygulaması telefona kurulur) ya da Telegram bot arayüzü.
- **Ölçütler:** güncelleme sıklığı (canlı mı, saatlik mi), kimlik doğrulama (gerçek hesap verisi görünecekse şart), maliyet, bakım, Faz 3 emir yoluyla uyum, sırların güvenliği (API anahtarları panoda olmaz).

## 6. Makine öğrenmesi katmanı (kullanıcı isteği, 2026-10-25)
Argon derin araştırması: `arastirma/ml/algoritmik_trading_makine_ogrenmesi_2026.pdf` (18 s.).

**Ana fikir:**
- Ham fiyat yönü tahmini neredeyse işe yaramıyor: örneklem dışı R² %0,1-0,4, yön doğruluğu %51-54.
- ML'in değeri mevcut stratejilerin **üstünde** bir katman olmasında.
- Bizim hat (yazar ayarı, yayın sonrası sınama, maliyet) parametre aşırı uyumunu zaten yapısal olarak önlüyor.

**Önerilen 3 pilot:**

| # | Pilot | Ne yapar | Emek |
|---|---|---|---|
| 1 | Çoklu test elemesi + HRP | Tek kapıyı geçenlerde şans eseri geçenleri ayıklar (Deflated Sharpe, efektif bağımsız deneme sayısı N_eff, Romano-Wolf StepM / BH-FDR q≤0,10). Korelasyon kümelemesiyle 20 gölge kitap seçer, ağırlıkları HRP (CVaR) ile belirler. Ek veri gerekmez | 2-3 gün |
| 2 | Meta-labeling + rejim filtresi | Strateji sinyallerini sığ LightGBM / lojistik modelle veto eder ya da boyutlar. Özellikler: rejim (HMM, volatilite oranı, Hurst, ADX), stratejinin son işlemleri, funding/taker oranı. Doğrulama: CPCV + PBO < 0,15 | 5-7 gün |
| 3 | Volatilite tahmini | %10 oynaklık ölçeklemesinde geriye dönük standart sapma yerine HAR-RV + kuantil LightGBM | 2-3 gün |

**Lider yorumu:**
- **Pilot 1 en değerli ve en ucuz.** 942 stratejiden seçim yaptığımız için en iyisinin Sharpe'ı yalnız şans eseri yaklaşık 3,25 σ şişebilir.
  - Ancak DSR/StepM'i kapıya eklemek **yöntem ve kural değişikliği**dir (TEST_YAPISI).
  - Önce yalnız **bilgi sütunu** olarak hesaplanır; kapıya ya da sıralamaya almak kullanıcı kararı.
- **Pilot 3** ölçekleme yöntemini değiştirir. O da önce gölge karşılaştırma olarak yapılır, karar kullanıcının.
- **Pilot 2** en çok veri ister: strateji başına yeterli işlem gerekir. Gölge kitaplar birkaç ay işlem biriktirdikten sonra yapılmalı.
- **Hemen yapılacak denetim:**
  - Rapordaki kırmızı bayrak 4: `request.security(..., lookahead=barmerge.lookahead_on)` ile üst zaman diliminin henüz kapanmamış barını okuyan stratejiler geleceği görür.
  - Yorumlayıcımız TradingView'ı birebir taklit ediyor; TV'de de bu sızıntı var.
  - Bu yüzden böyle stratejiler "geçti" çıksa bile canlıda aynı sonucu vermez. TV-2'de bunlar işaretlenmeli (S1 denetimi kapsamı).
- **TradingView "ML" betikleri:** jdehorty Lorentzian Classification aslında KNN. Rapora göre etiketi geçmiş 4 barlık momentum ve komşu seçimi yarı rastgele. Gelecek tahmini değil, trend filtresi gibi davranıyor. Bizim testte diğer stratejiler gibi değerlendirilir; ayrıca güven verilmez.
- **Doğrulanacaklar:** bazı 2026 kaynakları (Rahimikia Mart 2026, PickMyTrade, Quant67). Sol 6.1 doğrulayacak.

## Sol 6.1 eleştirisi (Codex, 2026-10-25)

### 4. Copy trade

- **Yön:** Yalnız biz kopyalayalım; sinyal yayımlamak ayrı bir ürün, müşteri/uygunluk yükü ve
  düzenleyici riski getirir. Kopyalama bile yatırım tavsiyesi değildir: lider seçimi ve her gerçek
  para kararı kullanıcıda kalmalı.
- **Temel sorun:** Liderin ekrandaki geçmişi backtest değildir. Hayatta kalma yanlılığı,
  sonradan değişen kaldıraç/sermaye, açık işlemlerin sakladığı zarar ve kapatılmış lider hesabı
  yüzünden ``yüksek ROI`` tek başına bilgi değildir. Platformun verdiği işlem zaman damgası ve
  dolum fiyatı yoksa lider sadece izleme havuzunda kalır.
- **TEST_YAPISI uyarlaması:** Lideri katıldığımız gün ``t0`` ile dondur; t0 öncesini yalnız
  keşif bilgisi say. t0 sonrası her sinyal için lider zamanı/fiyatı, bizim gözlem zamanımız,
  emir zamanı, dolum fiyatı, ücret ve fonlama kaydedilsin. Kendi gölge defterimizde aynı
  nominal-risk ve iki maliyet senaryosuyla hesaplanan net sonuç liderin yayınladığı ROI'den
  önceliklidir. Lider değişirse (kaldıraç, sembol evreni, pozisyon boyutu) yeni sürüm ve yeni
  t0 açılır; eski sonuçla birleştirilmez.
- **Gecikme/kayma:** Her işlem için ``gözlem−lider``, ``emir−gözlem`` ve
  ``bizim_dolum−lider_fiyat`` dağılımı saklanmalı; p50/p95 gecikme ve p95 ters kayma bütçesi
  aşılırsa lider başarısız sayılmalı. API yoksa veya sadece periyodik portföy anlık görüntüsü
  varsa gecikme ölçülemez; otomatik kopyalama yapılmaz. Kısmi dolum, fonlama, spread ve liderin
  kapanışından sonra gelen sinyal ayrıca maliyettir.
- **Risk:** Copy trade ana portföyün dışında teknik bir kitap olabilir ama ekonomik olarak
  toplam zarar bütçesine dahil edilmelidir. Başlangıçta toplam copy tahsisi en çok %10, lider
  başına %2, tek platform başına %5; kaldıraç için mutlak üst sınır ve her lider için günlük
  zarar/azami düşüş kesicisi tanımlanmalı. Aynı sembol ve yönlü beta çakışmaları liderler
  arasında da netleştirilmelidir. Liderin ani risk artışı, API kesintisi veya veri bütünlüğü
  bozulması yeni girişleri derhal durdurur; kör biçimde pozisyon tersleme yapılmaz.
- **Canlı karar:** ``30 işlem veya 3 ay`` tek başına zayıf; 30 korelasyonlu işlem çok az
  bağımsız kanıt taşır. En az 90 gün *ve* yeterli aktif hafta, net sonuç pozitif, önceden
  tanımlı maliyet/kayma altında PF eşiği ve MDD sınırı birlikte aranmalı. Buna ek olarak,
  ardışık Bayesçi izleme kullanılabilir: her kapalı işlemden sonra pozitif beklenti olasılığı
  güncellenir; örneğin P(E[R]>0) >= %95 ve gözlenen MDD bütçe içinde değilse tahsis artmaz.
  Çok lider tarandığı için bu olasılık/karar eşiği deneme sayısına göre sıkılaştırılmalı;
  sıralamaya bakıp seçme yanlılığı aksi halde geri gelir.
- **Hukuk/vergi:** Türkiye'de SPK düzenlemeleri, platformun Türkiye'ye hizmet koşulları,
  türev/kaldıraç uygunluğu ve vergi yükümlülüğü hukukçu/mali müşavir tarafından işlem öncesi
  yazılı doğrulanmalı. Bu kayıt teknik tasarım önerisidir, hukuki görüş değildir. API anahtarı
  yalnız emir yetkisi kadar dar olmalı; para çekme izni, pano/CI sırrı ve üçüncü taraf günlükleri
  yasaktır.

### 5. Pano

- **Öneri:** İki aşamalı ilerleyelim. Faz 2'de GitHub Pages üzerinde statik React/Vite (veya
  Svelte) + sürümlü JSON/CSV özetleri: ucuz, denetlenebilir ve bugünkü saatlik akışa yeterli.
  Faz 3'te emir ve kullanıcı geri bildirimi gerçekten devreye alınacaksa FastAPI + Postgres +
  React/PWA'ya geçilsin. Streamlit/Dash araştırma ve iç prova için hızlıdır, fakat yetkilendirme,
  denetim izi ve emir akışı için kalıcı ürün temeli olmamalıdır.
- **Neden şimdi FastAPI değil:** Gerçek kullanıcı, gerçek zamanlı emir ya da gizli veri yokken
  sunucu, kimlik doğrulama, yedekleme ve saldırı yüzeyi getirir. Buna karşılık statik panel,
  sonuçların yeniden üretilebilir snapshot'larını ve PR denetimini korur. Telegram ise alarm ve
  kısa onay kanalıdır; tablo/analiz panosunun yerine geçmez.
- **Sözleşme önce:** ``paper`` ve ``results`` doğrudan UI'ın veritabanı değildir. Önce sürümlü
  bir okuma modeli tanımlansın: strateji/kitap kimliği, hesaplama zamanı, veri kesim zamanı,
  kaynak commit'i, pozisyonlar, özkaynak, karar/uyarı ve açıklama. Şema geriye uyumlu olmalı;
  UI yalnız bu yayınlanmış API/JSON'u tüketmeli. Böylece statik ön yüz daha sonra API'ye düşük
  maliyetle bağlanır.
- **Faz 3 birleşimi:** Emir önerisi ``önerildi → kullanıcı onayladı/atladı → gönderildi →
  broker kabul/dolum → uzlaştırıldı`` durum makinesiyle, her geçişte kullanıcı/zaman/idempotency
  anahtarı ve denetim kaydıyla taşınmalı. PWA bu onay ekranını telefona getirir; Telegram yalnız
  imzalı bağlantı/uyarı üretir, emir parametresini chat metninden kabul etmez. Başlangıçta
  varsayılan yalnız-okunur ve paper modudur; gerçek emir için MFA, rol tabanlı yetki, ayrı emir
  servisi ve sır kasası gerekir.
- **Geçiş eşiği:** Statik panel saatlik güncelleme, geçmiş görüntüleme ve koç/radar için
  yeterliyse orada kalın. Birden çok kullanıcı, dakikalık veri, kişiye özel portföy veya onaylı
  emir gereksinimi ortaya çıktığında FastAPI/Postgres'e geçin. SQLite yerel/prova için yeterli;
  eşzamanlılık ve kalıcı denetim ihtiyacında Postgres seçin.

## 7. Argon araştırmaları (2026-10-26): radar ve pano
**Radar** (`arastirma/radar/strateji_toplama_ve_eleme_2026.pdf`):
- Yasal ve sağlam kaynaklar: arXiv `q-fin` API, OpenAlex (SSRN DOI), GitHub Search API (kod araması 10 istek/dk), PapersWithBacktest (Hugging Face veri setleri), QuantifiedStrategies / ProRealCode / MQL5 / Substack RSS, Reddit OAuth (100 istek/dk ücretsiz).
- TradingView: kullanım şartları otomatik kazımayı yasaklıyor, reCAPTCHA var → radar dışı, linkleri kullanıcı elle ekler (bölüm 1 ile aynı karar).
- Önerilen ön eleme: K ≤ 4 parametre, N ≥ 100 işlem, t ≥ 3.0, 2× maliyet stresi. Haftalık 300+ ham içerikten 1–2 aday kalır.
- **Lider yorumu:** kaynak listesi bölüm 1'i doğruluyor, uygulanabilir. Ön eleme ölçütleri yeni bir kapı demek; TEST_YAPISI v2'nin tek kapısını değiştirmez. Ancak radar girişinde yalnız **sıralama/öncelik** bilgisi olarak kullanılabilir. Kapı olarak kullanmak kullanıcı kararı.

**Pano** (`arastirma/pano/pano_altyapi_karsilastirmasi_2026.pdf`):
- Öneri ($0/ay): iki katman.
  1. Telegram bot + Cloudflare Worker (+ D1 SQLite): sinyal mesajı, "Uyguladım / Atladım / Panoyu aç" butonları; kararlar sonraki Actions koşusunda okunur.
  2. Svelte/React statik PWA, Cloudflare Pages + Zero Trust Access (yalnız kullanıcının e-postası); canlı fiyat tarayıcıdan Binance public WebSocket ile.
- Uyarı: GitHub Pages ücretsiz planda public depo gerektirir; gerçek hesap verisi orada gösterilmemeli.
- İlk günden FastAPI + Postgres + React kurmak bakım yükü yüzünden önerilmiyor.
- **Lider yorumu:** bölüm 5 seçenekleriyle uyumlu ve Faz 3 yol D'nin (Telegram + manuel, geri bildirim butonu) ihtiyacını doğrudan karşılıyor. Repo artık public olduğundan gerçek hesap verisi kesinlikle `paper/panel/data.json`'a girmemeli. Cloudflare hesabı açmak kullanıcı kararı.

## Sol 6.1 eleştirisi: ML

### Kaynak iddiaları denetimi

| İddia | Sonuç | Denetim notu |
|---|---|---|
| DSR formülü ve beklenen maksimum düzeltmesi | doğrulandı | PDF’deki Bailey–López de Prado formülü, mevcut `backtests/asama2b.py` DSR hesabının PSR/çarpıklık/basıklık bileşenleriyle uyumlu. |
| `N_eff=(Σλ)^2/Σλ²` | doğrulandı | PDF’deki özdeğer formülü uygulandı; yalnız bilgi sütunu olarak `results/tv2/siralama.csv` içine yazılıyor. |
| `arch.bootstrap.StepM` API’si | doğrulanamadı | PDF iddiayı ve API adını veriyor; mevcut `.venv` içinde `arch` kurulu değil, çalıştırılabilir API doğrulaması yapılmadı. |
| `skfolio` `CombinatorialPurgedCV` / HRP API’si | doğrulanamadı | PDF’de yöntem ve sınıf adları var; mevcut `.venv` içinde `skfolio` kurulu değil. |
| `jdehorty` Lorentzian’ın KNN/etiket yapısı | doğrulanamadı | PDF’de kaynak incelemesi var, ancak bu denetimde orijinal Pine kaynak dosyası bağımsız olarak alınmadı. |
| 2026 kaynakları ve güncel kütüphane sürümleri | doğrulanamadı | PDF bibliyografyasında yer alıyor; dış kaynak ve paket kurulumu olmadan tarih/sürüm teyidi yapılmadı. |

### Pilot görüşü

Önerilen sıra korunmalı: (1) kapıyı ve mevcut sıralamayı değiştirmeyen bilgi
amaçlı DSR/`N_eff` ve korelasyon kümeleri; (2) yeterli gölge işlem biriktikten
sonra purged/embargo CPCV ile meta-labeling; (3) en son volatilite tahmini.
Pilot 1’de DSR, StepM veya HRP sonuçları mevcut kapı, sıra ve eşiklere
uygulanmamalı; yalnız raporlanmalıdır. Pilot 2 ve 3, karar üretmeden gölgede
karşılaştırılmalıdır.

### Bilgi amaçlı kod değişikliği

`backtests/tv2_sirala.py` mevcut ortak ölçekleme, blok bootstrap p10 ve kopya
ayıklama mantığını değiştirmeden iki bilgi sütunu üretir: korelasyon
özdeğerlerinden `n_eff` ve `n_eff` denemesiyle hesaplanan `dsr`. Sıralama,
temsilci seçimi, kapı ve eşik bu sütunları kullanmaz. `tests/test_tv2_sirala.py`
bu ayrımı ve korelasyonla beklenen `N_eff` davranışını doğrular.

### `lookahead_on` denetimi

TV-2 sonuçları `origin/codex/tv2-kosu` dalından `git show` ile okundu. Üst
zaman dilimiyle birlikte `lookahead_on` kullanan satırlar
`results/tv2/lookahead_listesi.csv` dosyasına; satır numarası, ifade ve mevcut
karar ile yazıldı. `close[1]` kullanan satırlar da listede bırakıldı: bu,
gelecek sızıntısını azaltan bir kullanım olabilir, fakat `lookahead_on` seçimi
ayrıca denetim işaretidir. Liste kararları değiştirmez.

## Sol 6.1 eleştirisi: copy trade araştırması

### (a) Kritik iddiaların kaynak denetimi

PDF’deki iddialar, PDF’nin kaynakça bağlantıları ve erişilebilen birincil
belgelerle karşılaştırıldı. “Doğrulandı” yalnızca iddianın ilgili birincil
kaynakta açıkça desteklendiği anlamına gelir; bir URL’nin HTTP 200 dönmesi
içerik veya hukuk iddiasını tek başına doğrulamaz.

| # | İddia | Sonuç | Kaynak ve denetim notu |
|---:|---|---|---|
| 1 | Binance’in copy-trading API dokümantasyonu vardır. | doğrulandı | [Binance Copy Trading API Introduction](https://developers.binance.com/docs/copy_trading/Introduction), copy-trading API kapsamını açıklar. |
| 2 | Binance’te takipçinin tüm lider geçmişini indiren genel bir Follower API vardır. | doğrulanamadı | [Binance Copy Trading API Introduction](https://developers.binance.com/docs/copy_trading/Introduction) erişildi; yokluk iddiasını tam API kataloğuyla kanıtlamaz. Pilot öncesi yeniden kontrol gerekir. |
| 3 | Hyperliquid vault’ları zincir üstü ve vault dokümantasyonu mevcuttur. | doğrulandı | [Hyperliquid protocol vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults), vault yapısını ve protokol vault’larını açıklar. |
| 4 | Hyperdash herhangi bir Hyperliquid cüzdanını non-custodial biçimde kopyalar. | doğrulanamadı | [Hyperdash Copy Trade](https://docs.hyperdash.com/copy-trade) erişildi; kapsam/emanet iddiası bu denetimde sayfa içeriğinden kesinleştirilmedi. |
| 5 | Hyperdash kopyalama ücreti tam olarak 5 bps ve ayrıca builder fee uygulanır. | doğrulanamadı | [Hyperdash ücretler](https://docs.hyperdash.com/fees-referrals-rewards) erişildi; oranların ürün, tarih ve işlem türüne göre ayrımı teyit edilmedi. |
| 6 | Hyperdash’te minimum bakiye 100 USDC’dir. | doğrulanamadı | [Hyperdash Copy Trade](https://docs.hyperdash.com/copy-trade) erişildi; minimumun hangi koşullarda geçerli olduğu birincil belgede teyit edilmedi. |
| 7 | Hyperliquid API ücretsiz ve cüzdan işlemleri geçmişten doğrulanabilir. | doğrulandı | [Hyperliquid protocol vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults) zincir üstü vault kayıtlarını destekler; API ücretinin tüm uç noktalar için kapsamı ayrıca sürüm kontrolü gerektirir. |
| 8 | BIST/VİOP’ta üçüncü kişinin işlemlerini otomatik kopyalama SPK izni gerektirir. | doğrulanamadı | [SPK mevzuat portalı](https://mevzuat.spk.gov.tr/) ve [Borsa İstanbul VİOP](https://www.borsaistanbul.com/tr/sayfa/288/vadeli-islem-ve-opsiyon-piyasasi) erişildi; somut hukuk yorumu uzman teyidi olmadan sonuçlandırılamaz. |
| 9 | TEFAS/serbest fon veya lisanslı model portföy, BIST’te kopyalamaya alternatif olabilir. | doğrulanamadı | [TEFAS](https://www.tefas.gov.tr/) erişildi; bu bir ürün/uygunluk önerisidir ve koşullar tek tek incelenmedi. |
| 10 | SEC 13F verisi yaklaşık 45 gün gecikmelidir. | doğrulandı | [SEC Form 13F FAQ](https://www.sec.gov/divisions/investment/13ffaq.htm), bildirim dönemi sonundan itibaren 45 günlük süreyi açıklar. |
| 11 | MQL5 Signals, Gedik MT5 üzerinde teknik olarak doğrudan çalışır. | doğrulanamadı | [MQL5 Signals](https://www.mql5.com/en/signals) ve [Gedik yatırım ürünleri](https://www.gedik.com/yatirim-urunleri) erişildi; Gedik hesabı için kurumsal teknik teyit alınmadı. |
| 12 | Copy-trade lider performansı hayatta kalma yanlılığı taşır. | doğrulandı | [Bailey ve López de Prado, *The Probability of Backtest Overfitting*](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253), seçilmiş geçmiş performansın yanlılık riskini destekler; burada aktif lider listesindeki örnekleme riski olarak kullanıldı. |

Sonuç: Hyperliquid vault dokümantasyonu ve Binance copy-trade dokümantasyonunun
varlığı doğrulandı; ücret, erişim, takipçi API’si ve Türkiye hukukuna ilişkin
kesin operasyon kararları doğrulanmadı. Bu maddeler gerçek para veya hesap
kararı olarak kullanılmayacak.

### (b) Varlık sınıfı başına öneri değerlendirmesi

- **Kripto:** Hyperliquid cüzdan/vault izleme önerisine katılıyorum; zincir
  üstü zaman damgası denetlenebilir. Otomatik kopyalama ancak aşağıdaki sanal
  pilotta gecikme, ücret, fonlama ve ters kayma ölçüldükten sonra tartışılmalı.
  Binance Copy Trading yalnızca ayrı bir izleme kolu olmalı; resmi takipçi
  geçmiş API’si doğrulanmadan bot yazılmamalı.
- **BIST/VİOP:** “Kopyalama” yerine lisanslı kurumun model portföyü veya
  kullanıcının kendi algoritması önerisine katılıyorum. PDF’deki SPK yorumunu
  hukuki görüş olarak kabul etmiyorum; lisanslı hukukçu/kurum yazılı teyidi
  olmadan sinyal kopyalama ve hesap erişimi yapılmamalı.
- **ABD hisseleri:** 13F düşük devirli araştırma girdisi olabilir, ancak 45
  günlük gecikme nedeniyle gerçek zamanlı copy trade değildir. PDF’nin bunu
  ayrı, gecikmeli bir sinyal ailesi sayma önerisine katılıyorum; HIP-3 perp
  alternatifi ise farklı teminat, erişim ve hukuk riski nedeniyle ayrı
  değerlendirilmeli.
- **Emtia/forex:** Binance TradFi perp ve MQL5 önerileri veri/erişim ve
  kaldıraç koşulları doğrulanmadan öneri olarak kalmalı. Bu sınıfta önce
  sanal izleme ve broker sembol/ücret teyidi gerekir; doğrudan canlı kopyaya
  katılmıyorum.

### (c) Sanal izleme pilotu (kod değil, tasarım)

1. **Aday seçimi:** Hyperliquid API’den cüzdan ve vault adaylarını günlük
   snapshot olarak al; adres, vault, sembol, yön, notional, kaldıraç,
   gerçekleşmiş/gerçekleşmemiş PnL, fonlama ve zaman damgasını sakla. Aynı
   kişi/strateji görünen adresleri tek kimlikte birleştirme; ilişkiyi yalnız
   kanıt varsa işaretle.
2. **t0 ve sürüm:** Her aday için izleme başlangıcı `t0` olarak dondurulur.
   t0 öncesi yalnız keşif ve seçim yanlılığı denetimidir; başarı ölçümüne
   katılmaz. Lider kaldıraç, sembol evreni, vault kuralı veya API yöntemi
   değiştirirse yeni sürüm ve yeni `t0` açılır.
3. **Günlük kayıt:** Lider işlemi zamanı/fiyatı, bizim gözlem zamanı,
   emir varsayım zamanı/fiyatı, varsayılan dolum, ücret, fonlama, tahmini
   kayma ve blok/API gecikmesi ayrı alanlardır. Pozisyon snapshot’ı tek başına
   işlem kanıtı sayılmaz; açılış/kapanış eşleştirmesi yapılır.
4. **TEST_YAPISI uyumu:** t0 sonrası dönemde aynı nominal-risk ölçeğiyle
   sanal kopya özkaynak eğrisi üret; komisyon, builder/kopyalama ücreti,
   fonlama, spread, gecikme ve en az iki kayma senaryosu düş. Liderin ilan
   ettiği ROI değil, bizim maliyet sonrası sanal defterimiz birincil ölçümdür.
5. **Kırmızı bayraklar:** görünmeyen açık zarar, tasfiye sonrası yeni hesap,
   kaldıraç sıçraması, martingale/grid, tek sembol yoğunlaşması, API veya
   snapshot boşluğu, ters kopya ve kısmi dolum ayrı işaretlenir. Veri eksikse
   aday başarısız sayılmaz; **doğrulanamaz** olarak izleme havuzunda kalır.
6. **Başarı raporu:** günlük net getiri, MDD, aktif hafta, PF, lider-kopya
   farkı, p50/p95 gözlem-emir gecikmesi ve p95 ters kayma dağılımı raporlanır.
   30 işlem/3 ay otomatik geçiş eşiği değildir; yeterli dönem ve bağımsızlık
   ayrıca denetlenir. Gerçek para tahsisi bu pilotun dışında ve kullanıcı
   kararındadır.
7. **Binance lider verisi:** Binance için yalnız resmi ve izinli uç noktalar
   kullanılmalı; liderin işlem zaman damgası/dolum fiyatı alınamıyorsa Binance
   kolu yalnız lider snapshot’ı olarak etiketlenmeli, Hyperliquid ile aynı
   doğrulanabilirlik sınıfına konmamalıdır.

### (d) Kullanıcıya bırakılacak kararlar

- Hangi platform ve hangi ayrı cüzdan/hesap izleme pilotuna dahil edilecek?
- Sanal pilot için başlangıç tarihi (`t0`), süre ve minimum aktif hafta nedir?
- Toplam copy riski ana zarar bütçesine nasıl dahil edilecek; lider/platform
  başına azami tahsis ve kaldıraç sınırı nedir?
- Hangi ücret/kayma/gecikme senaryosu kabul edilebilir ve hangi kırmızı bayrak
  pilotu durdurur?
- Binance/Hyperliquid erişimi, KYC, Türkiye’den kullanım ve vergi/hukuk
  uygunluğu hangi yetkili kurum veya hukukçu tarafından yazılı teyit edilecek?
- Başarılı sanal izleme sonrasında canlı işlem hiç yapılmayacak mı, yoksa
  ayrı kullanıcı onayı ve güvenlik incelemesi mi gerekecek?

## 8. Argon: Telegram + Cloudflare kurulum rehberi (2026-10-26)
`arastirma/pano/telegram_cloudflare_rehberi_2026.pdf`: BotFather ile bot, chat_id, inline butonlar; Cloudflare Worker webhook (gizli başlık `X-Telegram-Bot-Api-Secret-Token` + `ALLOWED_CHAT_ID` kontrolü, parametreli SQL ile D1); GitHub Actions'ın D1'i yalnız-okuma API token'ıyla okuması; Pages + Zero Trust ile tek e-postaya açık site. Bölüm 7'deki pano önerisinin uygulama adımları hazır. **Başlamak için kullanıcı kararı: Cloudflare hesabı ve Telegram botu açılsın mı.** Bot token ve API anahtarları yalnız GitHub Secrets / Cloudflare secrets'ta; public repoda asla.

## 9. BIST strateji fikirleri (Argon, 2026-10-26)
`arastirma/bist/bist_viop_maliyet_anomaliler_2026.pdf` bölüm 3: 8 fikir (gece/kapanış seansı, 1 hafta atlamalı momentum + PD/DD, temettü sonrası sürüklenme, bilgi şoku, yabancı akışı, pay geri alım duyurusu, endeksten çıkarılma, bayram öncesi). Raporun brüt alfa rakamları doğrulanmadı. Günlük veriyle test edilebilenler (momentum, endeksten çıkarılma, bayram, temettü) radar kartı olarak sıraya alınabilir; veri (temettü/endeks değişikliği tarihleri, KAP) eksik olanlar sonra.
