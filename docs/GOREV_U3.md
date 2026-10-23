# U3: Dünya genelinde MTF strateji toplama (4 saat / 1 saat kurulum, 15 dk / 5 dk giriş)

**Sahip:** Sonnet. **Denetim:** lider. **Karar:** kullanıcı, 2026-10-23.
**Sıra:** hemen başlar. U2a (kripto short motoru) yapılmadı, U3'ten sonra sıraya girer (her ajanda aynı anda tek iş).
**Hedef:** en az **100 kayıt**.
**Backtest yok. Kod yazılmaz.** `engine/`, `backtests/`, `docs/spec/`, `state.json` ve `DURUM.md` değiştirilmez.

## Amaç
Kurulumu (yön, rejim, seviye) **4 saat ya da 1 saat** grafikte yapan, girişi **15 dk ya da 5 dk** grafikte veren stratejileri **dünyanın her yerinden** toplamak.
- T35'teki gibi ülkelere bölünmez. Dil ve bölge serbest; tek havuz.
- Piyasa serbest: kripto, FX, endeks vadeli, hisse, emtia. Ana işimiz kripto olduğu için kripto kaynaklarına öncelik ver, ama başka piyasaları dışlama.
- Bu liste ileride U1/U2 için yeni hipotez havuzu olacak. Bu aşamada hiçbiri test edilmez.

## Toplama kapısı: kayıt listeye girer, eğer
1. **Zaman dilimi şartı:** kaynakta açıkça iki katman var: kurulum TF ∈ {4H, 1H} **ve** giriş TF ∈ {15m, 5m}. Tek TF'li strateji girmez. Kurulum 2H ya da giriş 30m/1m ise `kirmizi_bayrak: tf_sinir_disi` ile girer (en fazla 10 kayıt).
2. **Strateji tanımlı:** en az bir paragraf açıklama ya da kod. Kurs, sinyal grubu ya da bot satışı reklamı girmez.
3. **Performans:** en az bir metrik (PF, WR, getiri, Sharpe, MDD) **ve** test dönemi yazılı. Metrik yok ama kural tam ve kod açıksa `kirmizi_bayrak: metrik_yok` ile girer (en fazla 30 kayıt). Bu kayıtlar ön kayıtlı test için yine değerli.
4. **Tekrar değil:**
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
