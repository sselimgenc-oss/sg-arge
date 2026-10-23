# 009 cevap: Claude (diğer hesap), kol: Çin, Japonya, Kore, Hindistan / Avrupa ve Amerika

Not: Bu cevap dosyayı okuyarak yazıldı; hiçbir kaynak sitesi açılmadı, tarama yapılmadı. Erişimle ilgili her şey (soru 4) denenmemiş varsayımdır.

## 1. Kaynak listesi doğru mu? Eksikler?
Genel olarak doğru. Eklemeler ve uyarılar:

- **Çin:** JoinQuant, BigQuant, RiceQuant listesi iyi, çünkü platformun kendi backtest grafiği yazarın beyanını doğrulanabilir kılıyor. Eklenecekler: **优矿 Uqer (DataYes)** ve **Ricequant 社区**. **聚宽 "策略分享" ve BigQuant "策略广场"** topluluk sayfaları ilk durak olmalı. Zhihu ve Xueqiu'da rakam çok ama çoğu ekran görüntüsü ve yeniden anlatım; "yalnız ekran görüntüsü" bayrağı sık çıkar.
- **Japonya:** Qiita/Zenn/note listesi yeterli. Eklenecekler: **はてなブログ** (bireysel sistem trade blogları, MT4/MT5 EA sonuç tabloları) ve **MQL5 Japonca topluluk / FX 自動売買 (EA) sitesi FX-On**. Not: note.com'da kurs/sinyal satışı yoğun, 2. kapı sıkı uygulanmalı.
- **Kore:** WikiDocs, Naver Cafe, DC Gallery tamam. Naver Cafe'ler büyük ölçüde giriş ister (`giris_gerekli`). Ekle: **Quantiwise/퀀터** ve **Upbit 변동성 돌파 GitHub/블로그** (Larry Williams varyantları için çok sayıda açık Python kodu var).
- **Hindistan:** Tradetron'un canlı sonuç pazarı en güçlü aday; ayrıca **Streak** paylaşımları ve **Traderji**. Eklenecek: **StockEdge/Chartink** tarayıcı paylaşımları. Opsiyon stratejilerinde maliyet (STT, slippage) çoğu zaman belirtilmez, kırmızı bayrak olur.
- **Avrupa/Amerika:** Listeye Quantopian arşivi (GitHub), QuantConnect topluluk paylaşımları, Quantpedia ve SSRN/arXiv uyarlaması eklenmeli. İngilizce Avrupa için **Elite Trader** ve **Forex Factory** (ayrıca Myfxbook doğrulanmış hesap sonuçları, "canlı" iddianın en güçlü kaynağı).

## 2. Toplama kapısı ve şablon
Uygun. Önerilen değişiklikler:

- **Ekle `dogrulama`:** `platform_dogrulamali` (JoinQuant grafiği, Myfxbook, Tradetron canlı) / `yazar_beyani`. Aynı rakamın değeri bu ikisinde çok farklı.
- **Ekle `veri_kaynagi_piyasa_kodu`:** sonraki aşamada veri bulmak için (örn. `7203.T`, `005930.KS`, `BANKNIFTY`).
- **Ekle `cevirisi_dogrulandi`:** özet makine çevirisiyse kural metninin çevirisinde hata riski var; giriş/çıkış alanlarına orijinal metinden bir alıntı konmalı.
- **Kapı 1 ince ayar:** "rakamla" ifadesine örnek verilmeli: "günlük +%0,3" tek başına yetmez, dönem ve işlem sayısı da gerekir (yoksa kırmızı bayrak). Aksi halde kapıdan çok az geçer ya da herkes farklı yorumlar.
- Çıkarılacak alan yok.

## 3. Beklenen yeni strateji aileleri
- **Kore:** 변동성 돌파 (Larry Williams) kripto/KOSPI varyantları, 갭 상승 단타, 조건검색 (Kiwoom) sinyalleri.
- **Çin:** 可转债 (dönüştürülebilir tahvil) düşük fiyat/çifte düşük rotasyonu, ETF rotasyonu, 打板 (tavan avı; T+1 nedeniyle swing), 股指期货 (CSI 300 vadeli) gün içi, 商品期货 CTA trend (螺纹钢, 铁矿石).
- **Japonya:** 日経225ミニ gün içi ve 先物 (vadeli) trend, 優待 (hissedar kuponu) arbitrajı, FX 東京ボックス (Tokyo box) kırılımı, 配当落ち (temettü sonrası) ve dönem sonu etkileri.
- **Hindistan:** BankNifty/Nifty opsiyon satış (short straddle/strangle), expiry-day stratejileri, ORB, Supertrend.
- **Avrupa/Amerika:** Rus MOEX vadeli (smart-lab), DAX açılış kırılımı (Almanya), Euro Stoxx vadeli, 0DTE opsiyon (ABD).

## 4. Erişim ve limit
- Bulut ortamı proxy'den 403 alıyor (dosyanın kendi tespiti); bu oturumda sitelerin hiçbirini denemedim, bu yüzden hangilerinin açılacağını **bilmiyorum**. Dürüst varsayım: yalnız bazı GitHub/TradingView/arXiv benzeri açık sitelere erişim olabilir, Çin ve Kore sitelerinin çoğuna olmaz.
- Web arama aracı varsa onunla arama sonuç özetlerinden keşif yapılabilir; sayfa içeriğini okumak ayrı bir erişim ister.
- Oturum başına kaynak sayısı için sayı vermiyorum: denemeden tahmin etmek yanıltıcı olur. İlk partide (deneme) ölçüp bildiririm.
- Dil: Çince, Japonca, Korece okuyabiliyorum, çeviri sorun değil. Eksik olan erişimdir.

## 5. İlk parti hedefi
Kol başına **15-20 kayıt**, dört bölgeden de en az birkaç tane (Çin, Japonya, Kore, Hindistan), ilk partinin amacı kayıt sayısı değil **şablonun ve kapının işleyip işlemediğini** görmek olmalı. Lider ilk partiden sonra kapıdan geçme oranına bakıp ikinci parti hedefini belirlesin.
