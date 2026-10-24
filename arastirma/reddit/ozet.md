# Reddit taraması: yazı ve yorumlardaki stratejiler

**Kaynak:** kullanıcının yüklediği 14 Reddit sayfası (2026-10-24; "Your best scalping strategy so far" yüklenmedi). Yaklaşık 1.300 yorum okundu (lider).
**Sonuç:** yorumların büyük çoğunluğu genel tavsiye ("disiplin", "risk yönetimi", "tek setup'a odaklan") ya da kuralı verilmeyen/satılan sistemler. **Kuralı tam verilen 4 strateji** ve kısmen verilen 2 strateji çıktı.

## A. Kuralı tam, test edilebilir

| No | Strateji | Kaynak | Kurallar (yazarın sözleriyle) | Bizde benzeri |
|---|---|---|---|---|
| RD-01 | **SPY/QQQ dip alımı** | r/algotrading, tanweer919 ("100+ strateji test ettim" yazısı, hayatta kalan 3'ten biri) | Yalnız kapanış > SMA(200) iken. Ertesi açılışta al, şunlardan biri varsa: RSI(2) < 10, ya da art arda 3 düşen kapanış, ya da IBS < 0,2. İlk kapanış > SMA(5) olunca ertesi açılışta sat, en çok 10 gün. Stop: kapanış girişin %8 altı → ertesi açılış. Stoptan sonra yeniden giriş için önce kapanış > SMA(5) beklenir. Piyasa: SPY ve QQQ, 1D. | Faz 1'de RSI(2)/IBS ortalamaya dönüş kartları (B3-001, M012a/e, O3-002) **ABD25 hisse evreninde** elendi (çoğu null testinde: "piyasa betası"). Bu sürüm **yalnız endeks ETF'i** üzerinde ve bileşik tetikli; yeni kart. Not: yazarın kendi rastgele giriş karşılaştırması 100 denemenin 78'ini geçmiş (≈ p 0,22); bizim null kapısında zorlanması beklenir. |
| RD-02 | **Ay sonu SPY/TLT** | aynı yazar | Ay bitimine 4 işlem günü kala SPY ve TLT'nin ay başından beri getirisini karşılaştır. SPY TLT'nin %2+ gerisindeyse: o kapanışta SPY al, ayın son kapanışında sat. SPY %2+ öndeyse: ayın son kapanışında SPY al, gelecek ayın 3. işlem günü kapanışında sat. Arada fark yoksa işlem yok. TLT yalnız ölçüt, alınmaz. | O3-007 (ay dönümü takvim kartı) var ama koşulsuz; bu **TLT'ye göre koşullu** sürüm yeni. Kapanışta dolum (`dolum: kapanis`) gerekir. |
| RD-03 | **Faber GTAA** (taktik varlık dağılımı) | r/algotrading, ReporterCalm6238 ("Faber's GTAA, plain and simple") | Yazarın kendi verdiği kural yok; Faber (2007) yayınlı kuralı: 5 ETF (SPY, EFA, IEF, DBC/GSG, VNQ) eşit ağırlık; her ay sonu kapanış > 10 aylık SMA ise o varlıkta kal, değilse o pay nakitte. Aylık yeniden dengeleme. | Yok. Rotasyon altyapısı (`tarama_rotasyon`) var. |
| RD-04 | **4H "washout" dönüşü** | r/algotrading, Specialist-Bank-832 (yorum) | US500 4H: Williams %R(30) < −90 iken gir, %R > −50 olunca çık. %3 felaket stopu (yazar: %2 stop kenarı yarıya indirdi). 27 komşu ayarın hepsi pozitif demiş. | Williams %R kartları var (A2-019, A2-028 vb.) ama bu eşik/çıkış birleşimi yok. **Veri sınırı:** ABD 4H için yalnız ~2 yıllık yfinance 1H var (Faz 1 1H kuralı: ilk 2/3 IS). |

## B. Kuralı kısmen verilmiş (eksik parametre)

| No | Strateji | Kaynak | Verilen | Eksik |
|---|---|---|---|---|
| RD-05 | **Kalıntı (residual) momentum + %50 SPY** | tanweer919 | Hisse: ortalama günlük hacim ≥ 100M $, fiyat ≥ 10 $. Skor: son 12 ayın SPY ile açıklanmayan günlük getirileri (1 yıllık kayan beta), son ay atlanır, oynaklığa bölünür. En iyi 30, eşit ağırlık, ay sonu karar, ertesi açılışta dengeleme. Portföyün yarısı SPY. | Evren: bizim PIT ABD25 yalnız 25 hisse; "en iyi 30" için geniş PIT evren gerekir (yazar ölü şirketler dahil QuantConnect kullanmış). Mevcut veriyle **birebir test edilemez**. |
| RD-06 | **"Çalışma bölgesi" alımı** | Cool_Big2955 (yorum) | Kapanış > SMA(50) ve > EMA(200); kapanış 20 günlük aralığın alt %30'unda; yerel dipten 3 barda %2 yükseliş teyidi; 90 günlük zirveye %2'den yakınsa alma; ATR izleyen stop; geniş %8 felaket stopu. | ATR çarpanı ve "yerel dip" tanımı yok; haber/duygu filtresi dış veri. |

## C. Kural yok ya da test edilemez (yalnız kayıt)
- **ICT/FVG modeli** (r/Daytrading, 1.538 oy): PD array + likidite süpürmesi/SMT + "displacement" + FVG girişi. Yorumcular kuralların öznel olduğunu soruyor; bir kullanıcı "backtest ettim, çalışmadı" diyor. Mekanik tanım yok → Doğrulanamaz.
- **NAS100 + Altın algo** ("9 yıl, bonkers"): ORB girişi + Supertrend iz süren çıkış; kod satılık/kapalı. Yorumcular aşırı uyum (overfit) şüphesinde.
- **XAUUSD Donchian kırılımı** 1H: periyot ve çıkış verilmedi. Donchian kartlarımız zaten var (A7-007, P02, T8-02…).
- EMA 9/20 kesişimi 5m, 13/48 EMA 10m, MTF stokastik + MACD (NQ): çıkış/parametre yok.
- PEAD (kazanç sonrası sürüklenme, küçük hisseler): kazanç tarihi verisi gerekir (dış veri).
- 0DTE opsiyon, kapalı opsiyon satışı, Polymarket, arbitraj: kapsam dışı.
- İşlem yönetimi önerileri (strateji değil): 2R'de yarısını sat, kalanını MA altı kapanışta kapat; +1,25R'de başa baş; hedefe varınca %75 sat, kalanı iz sür.

## D. Yöntem notları (bizim süreçle karşılaştırma)
Yazıların en değerlisi (tanweer919) bizim kullandığımız kontrolleri bağımsız olarak savunuyor: kapanışta sinyal / ertesi açılışta dolum, 2x maliyet, **aynı stop/süreli rastgele giriş karşılaştırması**, ölü şirketler dahil evren (survivorship), dokunulmamış dönem, kural önceden yazılır, ikinci kodla bağımsız tekrar. Onun da vardığı sonuç bizimkine benziyor: ~700 sürümün çoğu elendi, kalanlar sıkıcı bilinen kurallar.

## Öneri
RD-01, RD-02, RD-03 ve RD-04 kart olarak yazılıp U7'nin arkasından küçük bir parti ("U8-Reddit") olarak aynı huniden geçirilir; DSR deneme sayısına eklenir. RD-05/06 eksik parametre yüzünden Doğrulanamaz kalır.
