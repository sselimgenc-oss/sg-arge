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

## 5. Argon risk araştırması (2026-10-26)
Kaynak: `arastirma/risk/coklu_hesap_risk_mimarisi_2026.pdf` (17 sayfa, 20 kural K-01…K-20).

Öne çıkan kurallar:
- **K-01 bütçe:** %10 tek şemsiye; %3 Binance, %3 VİOP, %2 FX, %2 korelasyon/kayma tamponu.
- **K-02 kademeli kesinti:** alt hesap −%5 (toplam −%6) → pozisyonlar %50 küçülür; −%7,5…−%10 → hesap kapanır.
- **K-04/K-07 kaldıraç:** en fazla çeyrek Kelly; Binance vadeli izole marj 2–3x, VİOP 3–4x, FX CFD 3–5x.
- **K-08/K-09 taşıma maliyeti:** geri teste 8 saatlik fonlama, VİOP nema, FX 3x çarşamba swap'ı zorunlu.
- **K-10 günlük kill switch:** strateji −%1, hesap −%1,5, portföy −%2,5 → emirler silinir, gün sonuna kadar kilit.
- **K-11 ardışık kayıp:** 5 kayıp → %50 küçült; 7 kayıp → 24 saat teşhis.
- **K-12/K-13/K-14 teknik:** veri bayatlığı > 1,5 sn → yeni emir yok; Binance `countdownCancelAll` (30 sn, 10 sn'de bir yenile) ile ölü adam anahtarı; API ağırlığı %80 / 429 / 5xx → kill switch.
- **K-15/K-16/K-17 canlı izleme:** kayma geri test varsayımının 2 katı → dur; 60 gün sonra canlı Sharpe < 0,5 × geri test → bütçe yarı; 90 günde < 0,35 × ya da DD > 1,5 × geri test MaxDD → kapat; CUSUM erken uyarı.
- **K-18 aşamalı geçiş:** paper (30 işlem) → %10 (4 hafta) → %25–50 (6 hafta) → %100 (PSR ≥ 0,95).
- **K-19 alfa çürümesi:** yayımlanmış stratejilerde geri test Sharpe'ına baştan %50 iskonto.

**Lider yorumu:**
- Bölüm 3'teki 4., 5. ve 6. soruların (risk sınırları, güvenlik, aşamalı geçiş) somut karşılığı bu kurallar. K-10, K-13, K-15, K-16 ve K-18 doğrudan Faz 3 taslağına alınmaya aday; hepsi **yeni kural**, kullanıcı onayı gerekir.
- K-19 (%50 iskonto) ve t ≥ 3.0 mevcut kapıyı değiştirir; yalnız bilgi olarak tutulur, kapı değişikliği kullanıcı kararı.
- Bazı kaynaklar zayıf (Medium yazıları, "Ekim 2026 özeti" gibi doğrulanamayan tarihler). Eşikler uygulamadan önce birincil kaynaktan (Binance API belgesi, SPK/Takasbank) teyit edilmeli.

## 6. Argon emir yolu araştırması (2026-10-26)
Kaynak: `arastirma/emir_yolu_turkiye_2026.pdf` (12 sayfa). Bölüm 1'deki "doğrulanacak" maddelerin yanıtları:

- **Binance TradFi (yol A):**
  - XAUUSDT (ve XAG/XPT/XPD) USD-M vadeli (`fapi`) üzerinde işlem görüyor. NVIDIA kontratı Binance'te **NVDAUSDT**; NVDAXUSDT Binance'e değil Pionex'e ait (tokenize xStock).
  - API'den ilk TradFi emrinden önce `POST /fapi/v1/stock/contract` ile sözleşme onayı gerekiyor; sonra normal `POST /fapi/v1/order`.
  - **Türkiye hukuki durumu:** Binance TR (SPK izinli) yalnız spot; Türkiye'de izinli platformlarda kaldıraç/vadeli yasak. Binance Global vadeli işlemde ceza muhatabı platform, kullanıcı değil. Ama kullanıcı yatırımcı korumasından yararlanamaz. TR KYC'li hesabın TradFi sözleşmesine Binance'in izin verip vermediği **doğrulanamadı**.
- **Gedik forex (yol B):** MT5 doğrulandı. Ürünler SPK kaldıraçlı işlem kapsamında CFD; 1:10 kaldıraç sınırı, 50.000 TL asgari teminat. EA ve Python `MetaTrader5` paketi teknik olarak çalışır; Gedik sunucusunda EA kısıtı olup olmadığı **doğrulanamadı**. Her gece 23:58–00:05 işlem arası var.
- **BIST/VİOP (yol C), önemli düzeltme:** **Vakıf Yatırım da** Matriks IQ ve iDeal (ALGO/ROBOT) ile bağlı. 24 Ekim notundaki "Vakıf'ta algoritmik altyapı yok" bilgisi bu kaynağa göre yanlış. Gedik de Matriks IQ, iDeal ve ForInvest'e bağlı.
  - Matriks IQ: "Dışarıdan Emir Kabulü" API'si; Windows'ta açık terminalin `127.0.0.1:18890` TCP soketine Python'dan JSON emir. Algo lisansı gerekir.
  - iDeal Pro: C# sistem modülü dış sinyal dosyası/soket okuyup emir gönderir; yalnız Windows.
  - Bireysel yatırımcı BIST'e doğrudan bağlanamaz; aracı kurumda algoritmik işlem sözleşmesi ve her algoritma için ayrı kullanıcı gerekir.
- **ABD hisseleri (yeni seçenek):**
  - Interactive Brokers: Türkiye'den hesap açılır; TWS/Gateway API ücretsiz; komisyon hisse başı 0,005 $ (asgari 1 $).
  - Alpaca: ABD dışı yerleşiklere açık; bulut REST API, komisyonsuz, paper hesabı var.
  - Midas'ın bireysel API'si yok.
  - Yurt dışı kazançlar Türkiye'de beyana tabi.

**Lider yorumu:**
1. Vakıf düzeltmesi yol C'yi iki hesapta da mümkün kılıyor; kullanıcı Vakıf'a "Matriks IQ Algo / iDeal ALGO açılabilir mi, ücreti ne?" diye teyit etmeli.
2. ABD hisseleri için **Alpaca** yol A'ya en yakın seçenek (bulut REST, paper hesabı, Windows gerekmez). Hesap açmak kullanıcı kararı.
3. TV-2'de NVDAXUSDT verisi Binance USD-M yedeğinden alınmıştı. Rapor Binance'te bu sembolün olmadığını söylüyor; hangi verinin çekildiği denetimde kontrol edilecek.
4. Binance Global vadelide hukuki risk kullanıcıda değil ama koruma yok; gerçek parayla kullanmak kullanıcı kararı.
