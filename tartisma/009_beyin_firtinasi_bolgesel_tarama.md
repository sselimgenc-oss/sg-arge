# 009: Beyin fırtınası: bölgesel yeni strateji taraması (scalp / day / swing)

Durum: **açık tartışma.** Amaç ve bölge dağılımı kullanıcı kararıdır; toplama şablonu ve kaynak listesi tartışmaya açıktır. Açan: lider (Opus), 2026-10-23.
Katılımcılar: lider, Claude (diğer hesap), Codex, Argon. Her ajan cevabını `tartisma/009_cevap_<ajan>.md` dosyasına yazar (Argon: kullanıcı aracılığıyla).

## AMAÇ (kullanıcı kararı, 2026-10-23)
**Faz 1'de test ettiğimiz 422 stratejinin dışında, yazarının iddiasına göre kârlı ve işe yarar stratejileri dünya genelinde toplu halde bulmak.**

- **Bu aşamada backtest yapılmaz.** Yalnız bulunur, kaydedilir ve sınıflanır. Kendi backtestimizi sonra, ayrı bir aşamada yaparız.
- **Ölçüt yazarın iddiasıdır:** yazar stratejinin kârlı olduğunu rakamla gösteriyor mu? Örnek: backtest tablosu, PF, kazanma oranı, getiri, canlı/forward sonuç, işlem sayısı.
- **Strateji kendi yazıldığı piyasada değerlendirilir:** Japon hissesi için yazıldıysa Japon hissesi, B3 mini endeks için yazıldıysa B3. Sonradaki backtestimiz de yazarın piyasasında yapılır, bizim 4 piyasamıza zorlanmaz.
- **Önemli olan kârlılık.** Popülerlik (beğeni, indirme) tek başına yeterli değildir; yalnız ek bilgi olarak yazılır.
- **Türler:** scalp (1H altı), day (gün içi, pozisyon gün sonunda kapanır), swing (günler-haftalar). Tür belirsizse `belirsiz` yazılır; atılmaz.

## Faz 1'den çıkan ders (lider)
422 kartın 273'ü test edilemedi: 159'unda kaynakta giriş/çıkış kuralı yoktu, 35'i gizli/ücretliydi. Bu yüzden şimdi toplarken, sonraki backtest'i mümkün kılan bilgileri de **kaynakta varsa** kaydediyoruz: kural metni, kod linki, zaman dilimi. Bu bir eleme değildir. Kuralı eksik ama iddiası güçlü bir strateji de listeye girer, yalnız `kural_tam: hayir` olarak işaretlenir.

## Toplama kapısı
Bir kayıt listeye girer, eğer:
1. **Yazarın kârlılık iddiası rakamla var.** Yalnız "çok iyi çalışıyor" gibi rakamsız beyanlar girmez.
2. **Strateji tanımlı.** Ne yaptığı en az bir paragrafla anlatılmış ya da kodu var. Kurs/sinyal satışı reklamı girmez.
3. **Faz 1'in tekrarı değil.** `docs/KATALOG.csv`, `strateji_listesi (2).xlsx` ve `docs/spec/` ile URL ve isim karşılaştırılır.
4. **Ücretsiz okunabiliyor.** Giriş gerektiren kaynak yine yazılır, ama `erisim: giris_gerekli` olarak işaretlenir.

Kırmızı bayraklar atılmaz, işaretlenir:
- 30'dan az işlem;
- PF > 4;
- maliyet belirtilmemiş;
- çok kısa test dönemi;
- yalnız ekran görüntüsü.

## Toplama şablonu (her kayıt bir satır)
| Alan | Açıklama |
|---|---|
| id | `<bölge kodu>-<sıra>`: CN, JP, KR, IN, EU, US, SA (G. Amerika), AF |
| ad | Strateji adı (orijinal dil + Türkçe/İngilizce çeviri) |
| tur | scalp / day / swing / belirsiz |
| ulke_bolge, dil | |
| platform, url, yazar, yayin_tarihi | |
| piyasa, enstruman | Yazarın test ettiği piyasa (ör. Nikkei 225 vadeli, B3 WIN, KOSPI hisseleri, Upbit BTC) |
| zaman_dilimi | |
| ozet | 2-3 cümle: ne yapıyor |
| giris, cikis, stop | Kaynakta yazdığı kadarıyla, uydurmadan |
| kod_dili, kod_link | Pine, MQL, NTSL, Python, EasyLanguage, YesLanguage... |
| kural_tam | evet / hayır / kısmen |
| iddia_donem, iddia_islem, iddia_wr, iddia_pf, iddia_getiri, iddia_mdd, iddia_sharpe | Yazarın beyanı; yoksa boş |
| iddia_turu | backtest / canlı / forward / karışık |
| maliyet_dahil | evet / hayır / belirtilmemiş |
| erisim | acik / giris_gerekli / ucretli |
| populerlik | varsa (beğeni, indirme, yorum) |
| kirmizi_bayrak | yukarıdaki liste |
| not | |

Çıktı: `arastirma/<kol>.csv` (UTF-8). Argon için Markdown tablo da olur; lider CSV'ye çevirir.

## Bölge dağılımı (kullanıcı kararı)
Kodlama ajanlarının bulut ortamları sitelerin çoğunda proxy 403 alıyor; bu oturumda açılan kaynak sitesi yalnız TradingView. Bu yüzden keşif, sohbet uygulamalarının web/derin araştırma modlarıyla yapılır.

| Kol | Bölge |
|---|---|
| **Diğer Claude** | Çin, Japonya, Kore (Hindistan da bu kolda, son öncelik) |
| **Codex** | Avrupa + Amerika ek tarama |
| **Argon** | Afrika + Güney Amerika. Hafif yük; ekran görüntüsü yok, yalnız metin/kod kopyalanır |
| **Lider** | Şablon, tekrar eleme, kalite denetimi, TradingView (bölge etiketli: tr/ja/ko/zh/pt/es/ru/de/fr/it/in) |

## Kaynak adayları (tartışmaya açık; ajanlar ekler)
| Bölge | Kaynak adayları | Not |
|---|---|---|
| Çin | 聚宽 JoinQuant, 米筐 RiceQuant, BigQuant, 掘金 myquant, 天勤 TqSdk, 知乎, 雪球 Xueqiu, 集思录, CSDN, GitHub (vnpy ekosistemi) | Hisse T+1: hissede day trade yok, vadelide var. Birçok site giriş/WeChat ister. JoinQuant/BigQuant topluluk stratejilerinde platformun kendi backtest grafiği var. |
| Japonya | Qiita, Zenn, note.com, kabutan, minkabu, 5ch, イザナミ sistem trade toplulukları | FX scalp kültürü güçlü; Qiita/Zenn'de açık Python kodu bol. |
| G. Kore | WikiDocs (알고리즘 트레이딩 kitapları), 네이버 카페, 클리앙, 디시 주식갤러리, 키움 조건검색, 예스트레이더 | Larry Williams volatilite kırılımı (변동성 돌파) kripto/Upbit'te çok popüler. |
| Hindistan | TradingQnA (Zerodha), Traderji, Streak, Tradetron, Sensibull | Opsiyon ağırlıklı (BankNifty/Nifty intraday straddle); ORB, Supertrend yaygın. Tradetron'da canlı sonuçlu strateji pazarı var. |
| Avrupa | smart-lab.ru, wallstreet-online (DE), Zone Bourse / ABC Bourse (FR), Trade2Win (UK), X-Trader.net (ES), Investire (IT), SSRN | Rusça, Almanca, Fransızca, İspanyolca, İtalyanca. |
| Amerika | BabyPips, futures.io ek tarama, GitHub, arXiv q-fin, SSRN, Reddit (bizden engelli) | Faz 1'de büyük ölçüde tarandı; tekrar riski en yüksek bölge. |
| Brezilya | Nelogica ProfitChart NTSL paylaşımları, TradersClub, ADVFN Brasil forum, Rankia Brasil, GitHub (pt-BR) | B3 mini endeks (WIN) / mini dolar (WDO) day trade-scalp kültürü güçlü; NTSL açık kod. |
| İspanyolca LatAm | Rankia, Rava foros (Arjantin), investing.com es | |
| Güney Afrika | MyBroadband forum, Moneyweb, JSE blogları | |
| Nijerya / Kenya | Nairaland Business/Forex bölümü, Kenya forex grupları | Kurs/sinyal satışı çok; 2. kapı sıkı uygulanır. |
| Mısır / K. Afrika | Mubasher, Arapça forex forumları | |

## Sonraki aşama (bu tartışmanın kapsamı dışında, bilgi için)
Toplama bitince lider tekrarları eler ve listeyi kullanıcıya verir. Backtest aşamasında yazarın piyasası için veri gerekecek:
- yfinance günlük `.T`, `.KS`, `.NS`, `.SS/.SZ`, `.SA`, `.JO`;
- vadeli/forex/dakikalık için ayrıca kaynak.

Scalp için motorda 4 yapısal eksik var: maliyet modeli, bar içi sıra, seans saati ilkeli, dakikalık veri. Bunlar o aşamanın işi.

## Diğer ajanlara sorular
Kısa cevap yeter; katılmadığın yeri gerekçesiyle yaz.
1. Kolundaki bölgelerde kaynak listesi doğru mu? Eksik olan, kârlılık iddiası rakamla paylaşılan güçlü site/forum/platform hangileri?
2. Toplama kapısı ve şablon uygun mu? Eklenmesi ya da çıkarılması gereken alan var mı?
3. Kolunda hangi **farklı** (Faz 1'de görmediğimiz) strateji ailelerini bekliyorsun? Örnek ver.
4. Erişim ve limit kısıtın ne? Hangi siteleri açabiliyorsun, oturum başına yaklaşık kaç kaynak okuyabilirsin?
5. İlk partide (deneme) kaç kayıt hedefleyelim?

## Kural
Cevaplar toplanınca lider bir özet ve görev paketlerini yazar; kullanıcı onaylar, sonra toplama başlar.
