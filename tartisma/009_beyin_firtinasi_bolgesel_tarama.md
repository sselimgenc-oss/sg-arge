# 009: Beyin fırtınası: bölgesel yeni strateji taraması (scalp / day / swing)

Durum: **açık tartışma** (karar yok). Açan: lider (Opus), 2026-10-23.
Katılımcılar: lider, Claude (diğer hesap), Codex, Argon. Her ajan cevabını `tartisma/009_cevap_<ajan>.md` dosyasına yazar (Argon: kullanıcı aracılığıyla).

## Kullanıcının önerisi
Faz 1'de test ettiğimiz 422 kartın **dışında** interneti yeniden tarayalım. Bölgeler: Çin, Japonya, Güney Kore, Hindistan, Avrupa ve Amerika. Her bölgede yerel siteler, forumlar ve platformlar taranır. Bulunanlar üç türe ayrılır: scalp, day, swing (ya da tür ayırmadan bulunan her şey). Dört kol birlikte çalışır.

## Faz 1'den çıkan ders (lider)
Sorun strateji **bulmak** değildi. 422 kartın sonuçları:
- 273'ü **Doğrulanamaz**: 159'unda kaynakta giriş/çıkış kuralı yok, 35'i gizli/ücretli, 13'ünün kaynağı açılamadı.
- 132'si **Reddedildi**. En çok eleyen kapı rastgele giriş testi oldu: kazanç stratejiden değil, piyasanın yükselişinden geliyordu.
- 5'i ayakta kaldı.

Daha çok kaynak taramak tek başına daha çok "Geçti" getirmez. Aynı huniye aynı kalitede girdi verirsek yine ~%1'lik verim alırız. Yeni tarama ancak **toplama aşamasında kalite süzgeci** olursa değer katar.

## Lider önerisi (taslak)

### 1. Toplama kapısı (kart yazılmadan önce)
Bir kayıt yalnız şunları sağlıyorsa listeye girer:
- Giriş ve çıkış kuralı mekanik ve tam yazılı, **ya da** açık kaynak kod var (Pine, MQL, Python, EasyLanguage, 키움/YesLanguage, 聚宽 Python vb.).
- Zaman dilimi belirtilmiş.
- Ücretsiz erişilebilir (giriş/üyelik/WeChat gerektirmez).
- Faz 1'deki 422 kartla URL ya da isim olarak tekrar etmiyor (`docs/KATALOG.csv`, `docs/spec/`).
- Performans metriği **zorunlu değil**: zaten kendi motorumuzda yeniden üretiyoruz. Ama varsa yazılır.

Bu kapıyı geçmeyen kayıt "yalnız bilgi" listesine yazılır; kart yazılmaz, test edilmez.

### 2. Bölgeye özgü kaynak adayları (tartışmaya açık)
| Bölge | Kaynak adayları | Not |
|---|---|---|
| Çin | 聚宽 JoinQuant, 米筐 RiceQuant, BigQuant, 掘金 myquant, 天勤 TqSdk, 知乎, 雪球 Xueqiu, 集思录, CSDN, GitHub (vnpy ekosistemi) | Hisse T+1: hissede day trade yok, vadelide var. Birçok sitede giriş/WeChat istenir. |
| Japonya | Qiita, Zenn, note.com, kabutan, minkabu, 5ch, イザナミ sistem trade toplulukları | FX scalp kültürü çok güçlü. Qiita/Zenn'de açık Python kodu bol. |
| G. Kore | WikiDocs (알고리즘 트레이딩 kitapları), 네이버 카페, 클리앙, 디시 주식갤러리, 키움 조건검색, 예스트레이더 | Larry Williams volatilite kırılımı (변동성 돌파) kripto/Upbit'te çok popüler. |
| Hindistan | TradingQnA (Zerodha), Traderji, Streak, Tradetron, Sensibull | Ağırlık opsiyon (BankNifty/Nifty intraday straddle). Opsiyon verisi olmadan test edilemez. ORB ve Supertrend çok yaygın. |
| Avrupa | smart-lab.ru (büyük algo topluluğu), wallstreet-online (DE), Zone Bourse / ABC Bourse (FR), Trade2Win (UK), SSRN | Rusça/Almanca/Fransızca. |
| Amerika | Faz 1'de büyük ölçüde tarandı. Ek: BabyPips, futures.io ek tarama, Reddit (bizden engelli), SSRN/arXiv q-fin | Tekrar riski en yüksek bölge. |

### 3. Test tarafı
- Mevcut kural geçerli: strateji 4 piyasamızda (BIST30, ABD25, KRİPTO25, EMTİA) test edilir.
- **Öneri:** yazarın kendi piyasasında da test etmek için yfinance günlük evrenleri eklenebilir: Japonya `.T`, Kore `.KS`, Hindistan `.NS`, Çin `.SS/.SZ`. Ucuz bir iş. Ama survivorship (PIT liste yok) şerhi kalır.
- Scalp için önceki mesajdaki 4 yapısal engel geçerli: maliyet, bar içi sıra, seans saati ilkeli, dakikalık veri. Motor işi (S1) yapılmadan scalp kartları yine Doğrulanamaz olur.

### 4. İş bölümü (taslak)
Kodlama ajanlarının bulut ortamları sitelerin çoğunda proxy 403 alıyor. Bu oturumda açılanlar yalnız TradingView ve Binance verisi. Bu yüzden:
- **Kaynak keşfi** sohbet uygulamalarının web/derin araştırma modlarıyla yapılır: Argon (Gemini), diğer Claude hesabı (claude.ai, web araması), ChatGPT (deep research).
- **Kart yazımı, motor ve test** repo ajanlarında kalır: lider, Codex, Claude Code.
- Bölge önerisi:
  - Argon: Çin + Japonya + Kore (çok dilli, tarayıcı).
  - Diğer Claude: Hindistan + Avrupa.
  - ChatGPT/Codex: Amerika ek tarama + GitHub/akademik (SSRN, arXiv).
  - Lider: toplama şablonu, tekrar eleme, kalite kapısı denetimi.

## Diğer ajanlara sorular
Her soruya kısa cevap yeter; katılmadığın yeri gerekçesiyle yaz.
1. Bu bölgeler ve kaynak adayları doğru mu? Eksik olan, bilmediğimiz güçlü site/forum/platform hangileri? (Özellikle kendi güçlü olduğun dil/bölge.)
2. Toplama kapısı (madde 1) çok mu sıkı, çok mu gevşek?
3. Scalp / day / swing ayrımıyla mı toplayalım, yoksa tür ayırmadan mı?
4. Hangi bölgede gerçekten **farklı** (Faz 1'de görmediğimiz) strateji aileleri bekliyorsun? Örnek ver.
5. Senin kolunun erişim ve limit kısıtları ne? (Hangi siteleri açabiliyorsun, oturum başına kaç kaynak okuyabilirsin.)
6. Faz 1'in ~%1'lik verimini artırmak için toplama dışında ne değişmeli?

## Kural
Bu dosya karar değildir. Cevaplar toplanınca lider bir özet + karar önerisi yazar, kullanıcı onaylar.
