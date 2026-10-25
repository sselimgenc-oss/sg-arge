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
- **"Başarılı" ölçütü:** TEST_YAPISI'na göre tanımlanır. Liderin bizim izlemeye başladığımız tarihten sonraki dönemi, gerçekçi maliyet, düşüş, kaldıraç ve hesap yaşı esas alınır. Önce sanal havuzda (gölge) izlenir, gerçek para sonra.

## 5. Pano: HTML'den uygulama altyapısına geçiş (kullanıcı isteği, 2026-10-25)
Bugünkü durum: `paper/panel/data.json` → `sg-pano` statik HTML (GitHub Pages), 3,5-5 saatte bir güncelleniyor. Sol 6.1 de fikir sunacak. Değerlendirilecek seçenekler:
- **Statik kalıp güçlendirme:** aynı JSON, modern ön yüz (React/Vite ya da Svelte), GitHub Pages. En ucuzu; canlı veri yok.
- **Python panosu:** Streamlit / Dash / Panel. Hızlı, Python kodumuzla aynı dil; sunucu gerekir (Streamlit Community Cloud, Fly.io, küçük VPS).
- **Arka uç + ön yüz:** FastAPI + veritabanı (SQLite/Postgres) + React. Canlı fiyat, emir geçmişi, kullanıcı girişi, Telegram geri bildirimi (Faz 3 "uyguladım/atladım" butonu) için doğru temel; bakım yükü yüksek.
- **Mobil:** PWA (aynı web uygulaması telefona kurulur) ya da Telegram bot arayüzü.
- **Ölçütler:** güncelleme sıklığı (canlı mı, saatlik mi), kimlik doğrulama (gerçek hesap verisi görünecekse şart), maliyet, bakım, Faz 3 emir yoluyla uyum, sırların güvenliği (API anahtarları panoda olmaz).

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
