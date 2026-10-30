# Görev — Etre'nin üstün olduğu her şeyi al, bizimkinin yerine koy (K‑11)

**Karar (kullanıcı, 2026-10-30, sorgusuz):** Etre'nin bizden iyi olduğu her alan Etre'deki gibi yapılır: program/kullanılabilirlik,
plan/yol haritası, veri hattı, risk ve çıkış mantığı, mimari, yönetim/sadelik, mühendislik kalitesi, pano ve ofis, simülasyon
gerçekçiliği, hız, kopya mekaniği ve çıkışlar, hedef netliği. Birebir alınır ya da bize çevrilir.
**Yürüten:** Sonnet (tek lider, birleştirme yetkili). **Denetçi:** Codex (Sol). Önceki görev listeleri (K‑9/K‑10, `GOREV_VERI_DUZELTME.md`) 2026-10-30 temizliğinde silindi (git geçmişinde); tek görev listesi budur.

Kaynak: <https://github.com/ismailkaraabc/etre-trading-office> (GPL‑3.0, son sürüm 2026-10-28). Önce `README.md`, `KULLANIM.md`,
`ALANLAR.md`, `docs/GELISIM_GUNLUGU.md` (tamamı) okunur. Bizdeki analiz: `docs/etre_envanter.md`, `docs/DENETIM_TRADER_2026-10-30.md`.

## 0. Değişmeyenler (bunlar bizde daha iyi, korunur)
- **Güvenlik (değişmez kurallar, `AGENTS.md`):** gerçek para, cüzdan anahtarı, emir, para çekme YOK. Etre'nin `etre2/hl/borsa.py`
  (emir/çekim), `etre2/zincir/` işlem gönderme, DPAPI cüzdan ve `gercek.py` gerçek mod yolları **alınmaz**. Mod yalnız `sim`.
  Anahtar/token commit edilmez; yalnız GitHub Secrets.
- **Ölçüm yöntemi:** kontrol grubu, ön kayıt, sürümleme, bağımsız denetim. Etre'nin ileri test bildirgesi (`araclar/ileri_test_*.json`)
  biçimi alınır ama **test penceresi içinde kural değiştirilmez** (Etre'nin hatası).
- **Strateji seçim mantığı:** gecikme + maliyet sonrası kopya getirisiyle seçim (`secim.py` v1.3) ve kontrol/taban kolları kalır.
  Etre'nin oda giriş/çıkış (terfi/düşme) mekaniği bunun **üstüne** gelir (aşağıda 3).
- **Bulut işletim:** bilgisayar kapalıyken de çalışır (Etre Windows'a ve açık PC'ye bağlı — alınmaz). Testler, 10.000+ dolum
  sayfalaması, R2 arşivi kalır.

## 1. Lisans (kod birebir alınacaksa ilk iş)
Etre GPL‑3.0. Kod kopyalanır/çevrilirse: `sg-arge` ve `sg-pano` köküne `LICENSE` (GPL‑3.0) + `NOTICE`/README'de "Etre v2 · Trading
Office (ismailkaraabc) tabanlı" atfı; alınan dosyalarda kaynak yolu yorumu. Repolar zaten herkese açık. Görsel atlaslar (`etre2/web/*.png,
*.webp`) da GPL kapsamında; aynı atıfla alınır.

## 2. Hedef ve plan (Etre gibi tek cümle)
**Hedef:** Hyperliquid kaldıraç trader'larını sanal kasada, küçük sabit tutarla, Etre'nin çıkış kurallarıyla kopyalayan; tek
ofis/panelde ve Telegram'da canlı izlenen; her kuralı ileri testle ölçen sistem. Solana spot (meme) tarafı **kapsam dışı**
(ücretli anahtar ve ayrı zincir; kullanıcı ayrıca isterse açılır).
**Yol haritası** `DURUM.md` başında tek tablo; gelişim/olay günlüğü `docs/GELISIM_GUNLUGU.md` (Etre biçimi: tarih-saat, ne değişti,
hangi ölçümü etkiledi, test sayısı). Belge sayısı azaltılır: biten/askıdaki `docs/GOREV_*.md` → `docs/arsiv/` (silinmez).

## 3. Yapılacaklar (sıra; her adım ayrı PR, önce küçük gerçek veri denemesi)
**E1 Hız ve veri hattı (Etre `hl/api.py`, `hl/izle.py`, `kalite.py`):**
Oda trader'ları için anlık izleme. Etre bunu sürekli çalışan süreçle (WebSocket) yapar; GitHub Actions bunu taşıyamaz. Seçenekler:
(a) Cloudflare Worker dakikalık cron ile oda trader'larının dolumlarını yoklama (ücretsiz, ~1–2 dk gecikme), (b) Cloudflare Durable
Object ile WS (ücretli plan olabilir), (c) küçük sunucu (VPS, ~5 $/ay; Etre motoru Linux'ta sürekli çalışır, saniyeler).
**(b)/(c) para gerektirir → kullanıcıya sor;** onaya kadar (a) ile başla. Ağırlık bütçeli istek kuyruğu, 429 sayacı, bayat fiyat
koruması Etre'deki gibi. `kalite.py` karşılığı: yetim gölge payı, giriş kayması, sinyal gecikmesi, akış sessizliği, hata sayısı → tek
sağlık kaydı + Telegram uyarısı. Veri tek yerden çekilir (arşiv/motor/Worker üçlemesi biter).

**E2 Kopya mekaniği ve simülasyon (Etre `kaldirac/masa.py`, `sim.py`, `kasa.py`, `kurallar.py`):**
Tek motor, tek kasa (oda için tek portföy). İşlem başı **sabit tutar** (Etre ayarı karşılığı `kurallar.yaml`), kaldıraç kademesi
(Etre S3x/S5x mantığı), teminat, **tasfiye ve tasfiyeye uzaklık**, funding saat başı yalnız kopyalanan pozisyondan, ölçülmüş/
derinliğe bağlı kayma (sabit %0,05 değil), ücretler. Trader azaltınca aynı oranda azalt, kapatınca kapat (ayna). Mevcut
`copy_ledger`/`golge` yerine bu motor; eski motor ve v1 seri `arsiv` sürümü olarak donar (silinmez). #434 (Sonnet'in eski PR'ı)
birleştirilmez; içinden yalnız işe yarayan parçalar (durum kodları, Worker telafi/sağlık, kalıcılık düzeltmesi) alınabilir.

**E3 Risk ve çıkış kuralları (Etre `kurallar.py`, `kaldirac/lab.py`):**
Stop, süreli stop/kâr, zirveden düşüş, kâr merdiveni, ana parayı çekme, ayna satış — Etre'deki gibi; her kapanışta **neden**
kaydı ("trader kapattı / azalttı / stop / süreli stop / zirveden düşüş / tasfiye"). Lab: her kural birkaç kolda gölge olarak paralel
denenir; kural değişikliği yalnız ileri testten geçince (bildirge test başlamadan dondurulur).

**E4 Oda yönetimi (Etre `odalar.py`, `trader.py`, `kadro.py`, `puan.py`):**
Ana oda 20 + aday sırası; giriş/çıkış gerekçeli, bekleme süreli, değişmez olay günlüğünde. Giriş havuzu bizim `secim.py` seçimimiz;
odadan düşme Etre kuralları (boşta kalma, art arda zarar). Kontrol/taban kolları sessiz ölçüm olarak kalır.

**E5 Pano ve ofis (Etre `web/index.html`, `canli.js`, `ofis.js`, `odalar.js`, atlaslar; Telegram `telegram/`):**
`sg-pano` Etre panelinin birebir karşılığı olur: solda canlı kasa kartı (kasa, eğri, nakit, açık teminat, açık K/Z, bugün, yatırılan,
işlem başı, son 24 sa, oda), **açık işlemler** (coin, kaldıraç etiketi, trader, süre, teminat, büyüklük, K/Z $/%, liq uzaklığı),
**son kapananlar** (neden, süre, trader, K/Z), sağda izometrik ofis (gündüz/akşam/gece). Veri motorun yayımladığı tek JSON'dan;
ekran hesap yapmaz. Güncelleme 5 dk (Etre gibi). Telegram: 5 dk durum kartı (kullanıcı şimdilik günlük özet + alarm istedi — kartı
açmadan önce sor), `/durum /kasa /oda /dur` komutları. Eski pano sekmeleri ve eski ofis **arşive** (silinmez).

**E6 Mühendislik ve sadelik (Etre süreci):**
Tek motor süreci, ayarlar tek dosyada (`kurallar.yaml`), geniş `except Exception` yok (Etre'nin 128 yerinden ders: hata sayılır ve
sağlık kaydına yazılır), tek seferlik yama betikleri repoya girmez. 17 iş akışından kullanılmayanlar listelenip arşive (kullanıcı onayı).
Testler zayıflatılmaz; Etre testlerinin karşılığı taşınan modülle birlikte gelir.

## 4. Çalışma kuralları
- `AGENTS.md` değişmez kuralları + kalite kuralları 1–3 geçerli. Kural 4 (yeni özellik dondurması) bu görev için **kalkar**;
  kural 5 (strateji kilidi) seçim sürümü için sürer; kural 6 (yan yana) eski motor için sürer.
- Sonnet tek lider: görev yazar, PR açar, **CI yeşil + Sol denetimi sonrası birleştirir**. main'e doğrudan push yok.
- Para, hesap, ücretli servis, eşik ve repo silme kararları kullanıcınındır; sor.
- Kullanıcıyla Türkçe, sade, telefon için kısa; saatler TR.
- Her E adımı sonunda `docs/GELISIM_GUNLUGU.md` satırı + Sol'a kısa denetim notu (ne değişti, gerçek çıktı nerede).
- Eski sistem yeni sistem canlıya geçene kadar çalışmaya devam eder (veri kesilmesin); geçişte eski iş akışları kapatılır.

## 5. Bitti tanımı
Panoda Etre'deki kart birebir çalışıyor (gerçek veriyle, ekran görüntüsüyle kanıt); kopya motoru sabit tutar + çıkış kuralları +
tasfiye ile çalışıyor; oda Etre gibi yönetiliyor; sinyal gecikmesi ölçülüyor ve panoda; tek veri kaynağı; eski parçalar arşivde;
Sol denetimi temiz.
