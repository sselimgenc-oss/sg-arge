# U6: TradingView açık kaynak 205 stratejinin testi (ön kayıt)

**Karar:** kullanıcı, 2026-10-24: "205'in hepsi test edilsin."
**Ön kayıt sahibi:** lider. Sonuç görülmeden yazıldı. Kurallar sonuca bakılarak değiştirilmez.
**Kaynak:** `arastirma/U5_tv.csv`, `suzgec_sonucu == gecti` (205 script, PR #173).

## 1. İlke: geniş tarama + kilitli dönem teyidi
205 strateji test edilince bir kısmı şans eseri iyi görünür. Bu ön kayıtta bunu iki adımla çözüyoruz:
1. **Tarama:** IS ve OOS'ta U4 ile aynı huni, **DSR deneme sayısı N = 205**.
2. **Teyit:** huniden en iyi çıkan **en çok 5 strateji**, kilitli dönemde (2025-10-01 → koşu günü) **bir kez** test edilir. Kilit yalnız bu 5 strateji için, lider kararıyla açılır.

## 2. Her stratejinin test koşulları (sabit)
- **Piyasa kolu:** script sayfasındaki **yayın sembolünün** varlık sınıfı. Tek kol, sınıf değiştirilmez.
  - kripto → `KRIPTO25`, U1/U4'teki 14 coin havuzu;
  - ABD hisse ya da endeks (SPX, NDX, SPY, QQQ, tek hisse) → `ABD25` (PIT);
  - altın, gümüş, petrol, doğalgaz, tarım, bakır → `EMTIA`;
  - FX, BIST, diğer → **kapsam dışı**, "Doğrulanamaz (piyasa)" olarak kaydedilir.
- **Zaman dilimi:** yayın aralığı (4H ya da 1D, `U5_tv.csv` `tf`). Kripto 4H, 1H Binance verisinden; ABD/emtia 4H için uzun veri yok, "Doğrulanamaz (veri)".
- **Parametreler:** Pine `input` varsayılanları, olduğu gibi. Optimizasyon yok.
- **Yön:** yalnız long bacak. Long+short stratejilerde short girişleri yok sayılır; short sinyali long pozisyonu kapatıyorsa çıkış olarak kalır. Kayıtta `yalniz_long_bacak: true`.
- **Boyut ve maliyet:** `docs/EVRENSEL_KURALLAR.md`: işlem başı risk %0,5, toplam açık risk %2, kaldıraç yok. Yazarın boyut kodu (`strategy.equity * …`, `qty`) kullanılmaz. Maliyet `tarama.BASE_COST` (kripto %0,15, ABD/emtia %0,05). Stres 2x/3x.
- **Stop:** yazarın stopu varsa o; yoksa ATR(14) × 3 koruma stopu (EVRENSEL_KURALLAR A7). Kayıtta `stop_eklendi: true`.
- **Dönemler:** U4 ile aynı. IS 2018-01-01 → 2022-12-31, OOS 2023-01-01 → 2025-09-30; ABD/emtia ön dönem 2015-2017.
- **Çevrilemeyen:** motorun desteklemediği yapılar (kademeli kâr alma, piramit, sermayeye bağlı koşul, dış veri, Pine içi ML) → "Doğrulanamaz (çeviri)", nedeniyle. Yaklaşık değiştirme yapılmaz.
  - *Ek (lider, 2026-10-24, sonuç görülmeden):* piramit, çok seviyeli kısmi çıkış ve başa baş stopu motora eklenince (`docs/GOREV_U6_MOTOR.md`) çevrilebilir sayılır; bu yapılar yüzünden Doğrulanamaz olan kartlar yeniden çevrilir.

## 3. Kapılar (U4 huni, `backtests/u4_huni.decide` ile aynı; N = 205)
Aşama 1: IS PF > 1, ≥ 30 işlem. 2a: rastgele giriş testi p < 0,05. 2b: OOS ortalama R > 0, 2x PF ≥ 1,2, 3x net > 0, +1 bar net > 0, MDD95 ≤ %15, DSR (N=205) > 0,95. Kripto kardeş ölçütü. Koşullu sebepleri U4 ile aynı.

## 4. Kilitli döneme gidecek en çok 5 aday (sonuçtan önce sabit)
1. Önce **Geçti**, sonra **Koşullu** olanlar, OOS Sharpe'a göre sıralanır.
2. Beşten azsa, **DSR dışındaki bütün eleyici kapıları geçenler** eklenir, DSR'ye göre sıralanır.
3. Hiçbiri yoksa kilit açılmaz; U6 "aday çıkmadı" diye kapanır.

**Kilitli dönemde geçme:** 2x maliyette net > 0 **ve** PF ≥ 1,1 **ve** dönem MDD ≤ %15. Geçen strateji paper'a gölge kitap olarak önerilir. Ana portföye alma kararı kullanıcınındır.

## 5. İş bölümü
### A. Sonnet: çeviri (partiler halinde, 4 parti × ~50)
- Her script için `docs/spec/TV-<id>.yaml`:
  - Pine kuralı birebir: giriş, çıkış, stop, varsayılan input değerleri;
  - kol (piyasa ve tf), yayın sembolü;
  - `yalniz_long_bacak`, `stop_eklendi`;
  - `kaynak.url`, `deneme_sayisi_kaynakta: 205`.
- Yayın sembolü script sayfasından okunur (`symbol` alanı). Bulunamazsa kayıt "Doğrulanamaz (piyasa)".
- Motor diline doğrudan çevrilemeyen ama tek anlamlı kural → `ozel_kod: true` ile Python (Faz 1 özel kod kartları gibi). Anlamı belirsizse çevrilmez, "Doğrulanamaz (çeviri)".
- `belirsiz:` alanı zorunlu: Pine ↔ motor farkları. Örnekler: `ta.rma` ↔ Wilder, bar içi `strategy.exit` stop/limit sırası, `calc_on_every_tick`.
- Her parti için `tests/test_tv_parti<n>.py`: ileriye bakma testi (U4'teki gibi) + rastgele 3 kart için elle hesaplanmış örnek.
- Yazarın backtest rakamları hiçbir yere yazılmaz.
- Teslim: her parti ayrı PR `[U6] çeviri parti n`, açıklamada çevrilen / Doğrulanamaz sayıları ve nedenleri.

### B. Codex: koşucu (önce F2-GÖLGE'yi bitirir)
- `backtests/u6.py` + `u6_huni.py`. `u4.py`/`u4_huni.py` genellenir: her kart kendi kolunda koşar; N = 205 sabit (kartlara bağlı değil).
- Her çeviri partisi birleştikçe o parti koşulur. `results/u6/huni_ozet.csv` partiler halinde büyür. Satırlar sonradan değişmez; hata düzeltmesi lider kararıyla tüm partiyi yeniden koşar.
- Kilitli dönem koşusu ayrı komut. Yalnız lider bölüm 4 listesini yazdıktan sonra, `KILIT_AC=1` ile **lider** çalıştırır.
- İşlem dökümleri commit edilmez.

### C. Lider
- Her çeviri partisinden rastgele 5 kartı Pine kaynağıyla karşılaştırır.
- Her koşu partisinden 1 varyantı tekrar koşar.
- Bölüm 4 listesini yazar, kilitli dönemi bir kez koşar, `results/U6_SONUC.md`'yi yazar.

## 6. Beklenti (sonuçtan önce, dürüstçe)
Faz 1'de 70 TradingView stratejisinden 0 aday çıktı. U4'te düz trend kartları DSR'de kaldı. N = 205 ile DSR çıtası çok yüksek; büyük ihtimalle tarama aşamasında Geçti çıkmayacak. Gerçek eleme kilitli dönemde olacak. "Hiçbiri tutmadı" da geçerli ve değerli bir sonuçtur.
