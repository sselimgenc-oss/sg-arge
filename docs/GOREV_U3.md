# U3: Dünya genelinde MTF strateji toplama (4 saat / 1 saat kurulum, 15 dk / 5 dk giriş)

**Sahip:** Sonnet. **Denetim:** lider. **Karar:** kullanıcı, 2026-10-23.
**Sıra:** hemen başlar.
**Hedef:** en az **100 kayıt**.
**Backtest yok. Kod yazılmaz.** `engine/`, `backtests/`, `docs/spec/`, `state.json` ve `DURUM.md` değiştirilmez.

## Amaç
Kurulumu (yön, rejim, seviye) **4 saat ya da 1 saat** grafikte yapan, girişi **15 dk ya da 5 dk** grafikte veren stratejileri **dünyanın her yerinden** toplamak.
- T35'teki gibi ülkelere bölünmez. Dil ve bölge serbest; tek havuz.
- Piyasa serbest: kripto, FX, endeks vadeli, hisse, emtia. Ana işimiz kripto olduğu için kripto kaynaklarına öncelik ver, ama başka piyasaları dışlama.
- Bu liste ileride U1/U2 için yeni hipotez havuzu olacak. Bu aşamada hiçbiri test edilmez.

## Toplama kapısı (revize, lider, 2026-10-23: ilk tur 0 kayıt verdi)
**Neden revize:** ilk turda metrik + dönem şartı hiç kayıt bıraktırmadı. Biz her stratejiyi zaten kendi motorumuzda yeniden test ediyoruz; Faz 1'de yazar rakamları zaten tutmadı. Bu yüzden **ana kapı artık kuralın tam olması.** Yazarın rakamı varsa yazılır, yoksa kayıt yine girer.

Kayıt listeye girer, eğer:
1. **Zaman dilimi şartı (değişmedi):** kurulum TF ∈ {4H, 1H} **ve** giriş TF ∈ {15m, 5m}, kaynakta ya da kodda açık.
   - Freqtrade'de **5m taban + `@informative('1h')` / `informative_timeframe = '1h'` / `'4h'`** geçerli. 5m taban + yalnız 15m bilgi katmanı geçmez.
   - Kurulum 2H ya da giriş 30m/1m ise `kirmizi_bayrak: tf_sinir_disi` ile girer (en fazla 10 kayıt). Kurulum 1D/4H + giriş 1H olanlar **girmez**.
2. **Kural tam:** giriş ve çıkış kuralı koddan ya da metinden tek anlamlı okunuyor (gösterge parametreleri dahil). `kural_tam: evet` olmayan girmez.
3. **Performans (artık zorunlu değil):** yazarın metriği ve dönemi varsa `iddia_*` alanlarına yazılır. Yoksa `kirmizi_bayrak: metrik_yok`; üst sınır yok.
4. Kurs, sinyal grubu ya da bot satışı reklamı girmez.
5. **Tekrar değil:**
   - Faz 1 ile tekrar kontrolü: `strateji_listesi (2).xlsx` (URL sütunu), `docs/KATALOG.csv`, `docs/spec/*.yaml` (`kaynak.url`, `ad`).
   - T35 ile tekrar kontrolü: `arastirma/TUM_KAYITLAR.csv`.
   - Şüphe varsa `faz1_tekrar: supheli <id>`.

Giriş gerektiren ya da ücretli kaynak atılmaz, `erisim` alanında işaretlenir. Kırmızı bayraklar da atılmaz, işaretlenir:
`islem_sayisi_yok`, `az_islem(<30)`, `pf_gt_4`, `maliyet_yok`, `kisa_donem(<1yil)`, `yalniz_ekran_goruntusu`, `iterasyon_izi`, `metrik_yok`, `tf_sinir_disi`, `repaint_supheli` (ör. `request.security` lookahead, zigzag).

## Şablon
`arastirma/SABLON.csv` alanları, **sonuna iki sütun eklenerek**: `kurulum_tf,giris_tf` (ör. `1H`, `5m`).
- `id`: `MTF-<3 hane>`, aynı stratejinin farklı piyasa ya da parametre sonucu `MTF-012a`, `MTF-012b`.
- `kol`: `sonnet`.
- `zaman_dilimi`: `"1H kurulum / 5m giris"` biçiminde.
- `ulke_bolge`, `dil`: kaynağın bölgesi ve dili (bilgi amaçlı).
- `iddia_*`: **yalnız yazarın beyanı**, birimiyle. Yoksa boş. Tahmin yok.
- `orijinal_alinti`: kurulum ve giriş kuralının orijinal dilde kısa alıntısı.
- `motor_notu`: `short`, `cok_bacakli`, `seans_saati`, `tick_veri`, `orderbook`, `funding` vb.; yoksa boş.

Çıktı: `arastirma/U3_mtf.csv` (UTF-8, virgüllü, metin alanları tırnaklı). Açılamayan siteler `arastirma/U3_erisim.md` dosyasına "site, ne denendi, sonuç" olarak yazılır.

## Arama yöntemi (revize)
Genel web araması yerine **MTF'yi koddan tanıyan anahtarlar** ile ara. Bulduğun her dosyayı kural tamlığı ve TF şartı için oku:

| Platform | Kodda aranacak iz | Nasıl ulaşılır |
|---|---|---|
| Freqtrade | `@informative('1h')`, `@informative('4h')`, `informative_timeframe`, `merge_informative_pair` (taban `timeframe = '5m'` ya da `'15m'`) | `git clone` ile açık depolar; depo adlarını WebSearch ile bul (`"informative_timeframe = '1h'" freqtrade strategy github`) |
| TradingView Pine | `request.security(..., "60", ...)`, `"240"` ve grafik 5/15 dk | WebSearch `site:tradingview.com/script` + "multi timeframe" / "MTF" / "HTF bias"; script sayfası açık kaynaksa kod sayfada |
| ProRealCode | `TIMEFRAME(1 hour)`, `TIMEFRAME(4 hours)` ve `TIMEFRAME(default)` 5/15 dk | WebSearch `site:prorealcode.com "TIMEFRAME(1 hour)"` |
| MQL4/5 | `PERIOD_H1` / `PERIOD_H4` ile 5/15 dk grafik (`PERIOD_M5`, `PERIOD_M15`) | mql5.com/en/code ve /articles; WebSearch `site:mql5.com "PERIOD_H1" "PERIOD_M5"` |
| Jesse | `self.get_candles(..., '1h')` ya da `extra_candles` + `timeframe: 5m/15m` | `git clone` |
| NinjaTrader / cTrader | `AddDataSeries(BarsPeriodType.Minute, 60)`, `MarketData.GetBars(TimeFrame.Hour)` | Ecosystem / cTrader Algo sayfaları |

**Asgari çaba:** "hedefe ulaşılamadı" demeden önce en az **40 kaynak/depo/sayfa** incele ve hepsini `U3_erisim.md`'ye yaz (ne bulundu, neden girdi ya da girmedi). İlk tur (12 arama, 1 depo) yeterli değildi.

## Kaynak önerileri (sıra serbest; T35-P2 erişim notlarındaki API yöntemleri işe yarar)
| Tür | Kaynak |
|---|---|
| Kripto bot toplulukları | freqtrade stratejileri (`informative_pairs` / `@informative('1h')` ile 5m/15m), Jesse, Hummingbot, OctoBot, Superalgos; `raw.githubusercontent.com` üzerinden açık dosyalar |
| Platform kod kütüphaneleri | TradingView açık kaynak stratejiler (`request.security` ile üst TF), MQL5 CodeBase/Articles, ProRealCode, NinjaTrader Ecosystem, cTrader, QuantConnect forum |
| Forumlar | Forex Factory (MTF sistem başlıkları), BabyPips, Trade2Win, Elite Trader, futures.io, r/algotrading, r/Daytrading |
| Bölgesel | note.com, Qiita, Zenn (JP); BigQuant, 知乎 (CN); velog, WikiDocs (KR); smart-lab.ru (RU); TradingQnA, Marketcalls (IN); wallstreet-online (DE) |
| Akademik | arXiv/SSRN gün içi çoklu zaman dilimi çalışmaları (yalnız kural ve dönem açıksa) |

GitHub notu: oturumun GitHub araçları yalnız `sg-arge` deposuna bakar. Başka depoları `curl` ile `raw.githubusercontent.com` / `github.com` açık sayfalarından okumayı dene; olmazsa `U3_erisim.md`'ye yaz.

## Karışım hedefi (yönlendirici, zorunlu değil)
- Kripto ≥ 40, FX ≥ 15, endeks vadeli ≥ 15, diğer serbest.
- Kurulum 4H ve 1H dengeli; giriş 15m ve 5m dengeli.
- Mekanizma çeşitliliği: trend devamı, geri çekilme, kırılım, ortalamaya dönüş, seans açılışı, likidite süpürme / yapı kırılımı (SMC kurallı olanlar).

## Teslim
- **Ara teslim:** ilk 50 kayıtta PR aç, başlık `[U3] MTF toplama parti 1`. Lider örneklem denetimi yapar; sorun yoksa aynı yöntemle devam.
- **Son teslim:** toplam ≥ 100 kayıtla ikinci PR, başlık `[U3] MTF toplama parti 2`.
- PR açıklamasında: kayıt sayısı, piyasa ve TF dağılımı, kapıdan dönen aday sayısı ve en sık dönme nedeni, açılamayan siteler.
- **Dürüstlük kuralı:** erişilebilir kaynaklar tükendiği halde 100'e ulaşılamazsa sayıyı şişirme. Kaç kayıt bulduğunu, nereleri taradığını ve neden durduğunu yaz.
- **Yasak:** uydurma metrik ya da kural, tahminle doldurulmuş alan, aynı stratejiyi küçük farklarla çoğaltıp sayı tamamlamak.

## Lider denetimi
Her partiden rastgele 5 kayıt kaynaktan kontrol edilir. Uydurma bulunursa parti geri döner.
