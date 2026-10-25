# Faz 3: Gerçek hesaplarda yürütme (taslak, beyin fırtınası için)

**Kaynak:** kullanıcı, 2026-10-24.
- Bu belge karar değil, tartışma girdisidir.
- Para ve hesap kararları kullanıcınındır.
- "Doğrulanacak" işaretli maddeler varsayımdır. Kurumlarla ya da belgeleriyle teyit edilmeden kullanılmaz.

## 1. Hesaplar ve erişilebilen enstrümanlar (kullanıcının beyanı)

| Kurum | Piyasa | Enstrümanlar |
|---|---|---|
| VakıfBank (Vakıf Yatırım) | Borsa İstanbul | BIST pay piyasası, VİOP (vadeli/opsiyon) |
| Gedik Yatırım | Borsa İstanbul | BIST pay piyasası, VİOP |
| Gedik (forex hesabı) | Tezgâhüstü | Forex, ABD hisseleri, emtia (CFD olduğu varsayılıyor, **doğrulanacak**) |
| Binance | Kripto | Spot, vadeli (USDT-M/COIN-M) |
| Binance (TradFi) | Geleneksel varlıklar | ABD hisseleri ve emtia: spot ve vadeli (kapsam, kaldıraç ve Türkiye'den erişim **doğrulanacak**) |

**Not:** Testlerdeki piyasa ile gerçek enstrüman aynı olmayabilir. Örnek: test CME vadeli verisiyle yapılır ama işlem Gedik CFD'si ya da Binance TradFi vadelisiyle açılır. Bu durumda Adım 0'daki "uygulanabilir sonuç" o enstrümanın gerçek maliyetiyle yeniden hesaplanmalı: spread, komisyon, swap/fonlama, seans saatleri.

### Kullanıcı yanıtları (2026-10-24)
- **Gedik forex:** MetaTrader 5 var. Otomatik işleme (Expert Advisor / API) izin verilip verilmediği bilinmiyor; Gedik'e sorulacak.
- **Vakıf:** algoritmik işlem altyapısı yok. Vakıf hesabı yalnız manuel kullanılabilir (yol D).
- **Binance TradFi:** vadelide olduğu düşünülüyor. USDT-M vadeli listesindeyse aynı vadeli API'si geçerlidir. Bu ortamdan `fapi.binance.com` 451 (bölge engeli) döndüğü için sembol listesi buradan doğrulanamadı.

## 2. Emir yolu seçenekleri

| Yol | Kapsam | Otomasyon | Artı | Eksi / risk |
|---|---|---|---|---|
| **A. Binance API** | Kripto + TradFi | Tam otomatik | Belgeli REST/WebSocket API, `paper.yml` altyapısına en yakın. Test anahtarı (testnet) var. | API anahtarı güvenliği (yalnız işlem izni, çekim kapalı, IP kısıtı). TradFi ürünlerinin API'de olup olmadığı **doğrulanacak**. |
| **B. MetaTrader 5 (Gedik forex, MT5 sunuyorsa)** | Forex, CFD hisse/emtia | Otomatik (Expert Advisor ya da Python `MetaTrader5` paketi) | Yaygın, kurumdan bağımsız standart | Windows makine/VPS gerekir (Python paketi Windows'ta çalışır). Gedik'in MT5 ve otomatik işleme izin verip vermediği **doğrulanacak**. |
| **C. BIST/VİOP algoritmik platformu** (Matriks IQ vb. aracı kurum bağlantılı) | BIST, VİOP | Otomatik | Türkiye'de aracı kurumlara bağlanan yerleşik çözümler var | Ücretli lisans, kendi dili/ortamı. Hangi kurumun (Vakıf, Gedik) hangi platforma bağlandığı **doğrulanacak**. Strateji koduyla köprü gerekir. |
| **D. Telegram sinyali + manuel emir** | Hepsi | Yarı otomatik | Hesap entegrasyonu yok, hızlı başlar | İnsan gecikmesi ve kaçırılan sinyal (gece, iş saati), disiplin. Kayma ölçülmeli. Kısa zaman dilimli stratejiler için uygun değil. |

## 3. Tartışılacak sorular
1. **Hangi stratejiler hangi enstrümana düşüyor?** Gölge kitap ve TV-2 sıralamasından çıkan adayların piyasa dağılımı yolu belirler. Hepsi kriptoysa A yeter.
2. **Zaman dilimi ve manuel uygulanabilirlik.**
   - 1D/1W stratejiler (günde bir sinyal, sabah ya da akşam): manuel makul.
   - 1H/4H stratejiler: gece sinyali kaçar, otomasyon gerekir.
   - Dakikalık stratejiler: yalnız otomatik.
3. **Manuel yolda ölçüm.** Her Telegram sinyaline "uygulandı / atlandı + gerçek dolum fiyatı" geri bildirimi (Telegram butonu ya da pano). Böylece manuel kayma ve kaçırma oranı ölçülür; kâğıt sonuçla karşılaştırılır.
4. **Risk sınırları kurum bazında.** %10 zarar bütçesi tüm hesaplar toplamı mı, kurum başına mı? Kaldıraç sınırı (VİOP, CFD, Binance vadeli)?
5. **Güvenlik.**
   - API anahtarları GitHub Secrets'ta tutulur.
   - Çekim izni kapalı olur.
   - Emir öncesi son kontrol: pozisyon büyüklüğü sınırı ve günlük emir sınırı.
   - Acil durdurma: Telegram'dan "dur" komutu.
6. **Aşamalı geçiş.** Kâğıt → küçük gerçek (ör. bütçenin %10'u) → tam. Her aşamada kâğıtla gerçek arasındaki fark ölçülür.

## 4. Liderin ilk önerisi (tartışmaya açık)
- **Önce A:** Binance (kripto) tam otomatik. Altyapı (`paper.yml`, gölge kitap) zaten ona yakın.
- **Diğer piyasalar:** başlangıçta D (Telegram + manuel). Yalnız günlük ve üstü stratejilerle, geri bildirim butonlu.
- **B ya da C'ye geçiş şartı:** o piyasada ölçülmüş bir aday çıkması ve manuel kayma/kaçırma oranının sonucu bozduğunun görülmesi.
- **Doğrulama listesi** (kullanıcı ya da kurum):
  - Gedik forex MT5 sunuyor mu, otomatik işlem serbest mi?
  - Vakıf ve Gedik hangi algoritmik platforma bağlanıyor?
  - Binance TradFi ürünleri API'de var mı?

## Sol 6.1 eleştirisi

Bu bölüm tartışma girdisidir; emir yolu, eşik, hesap veya risk kararı
değiştirmez.

- **Emir yolu:** Copy trade veya strateji sinyali doğrudan canlı emre
  bağlanmamalı. Önce salt-okunur veri, sonra sanal defter, sonra kullanıcı
  onaylı küçük deneme; her geçişte emir kimliği, zaman damgası ve uzlaştırma
  kaydı tutulmalı. API anahtarında çekim yetkisi olmamalı.
- **Manuel ölçüm:** Sinyal zamanı, gözlem zamanı, kullanıcı/emir zamanı,
  gerçek dolum, ücret, fonlama ve kayma ayrı kaydedilmeli. Kaçırılan veya
  kısmi dolan sinyal de deftere yazılmalı; yalnız başarılı uygulamalar
  seçilerek sonuç güzelleştirilmemeli.
- **Test verisi / gerçek enstrüman:** TV-2 veya U7 sonucu, gerçek brokerın
  sembolü, seansı, spreadi, tick değeri, komisyonu, swap/fonlaması ve
  kaldıraç koşullarıyla aynı değildir. Canlıya geçiş öncesi aynı strateji,
  gerçek enstrüman verisi ve maliyetleriyle yeniden uygulanabilirlik kontrolü
  ister; sonuç yoksa `doğrulanamaz` kalır.
- **Risk bölüşümü:** Her kitap ve copy lideri için brüt açık risk, yön/
  sembol çakışması, kaldıraç, günlük zarar ve toplam zarar bütçesi birlikte
  izlenmeli. Liderin pozisyonu büyütmesi, veri/API kesintisi veya kayma
  bütçesinin aşılması yeni girişleri durdurmalı; otomatik tersleme yapılmamalı.
- **Güvenlik:** Salt-okunur anahtar varsayılan olmalı; emir anahtarı ayrı,
  çekimsiz, IP kısıtlı ve sır kasasında tutulmalı. Kullanıcı onayı olmadan
  emir gönderilmemeli. Acil durdurma, bağlantı kesilmesi, stale veri ve
  uzlaştırma uyuşmazlığı fail-closed davranmalı.
- **Aşamalı geçiş:** `kaynak doğrulama → sanal izleme (t0 sonrası) → paper /
  manuel küçük uygulama → kullanıcı onaylı sınırlı canlı` sırası korunmalı.
  Her aşamanın süresi ve geçiş kararı kullanıcıya aittir; bu metin geçiş
  eşiği tanımlamaz.
