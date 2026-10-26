# Görev: Faz 2 başı — TV-2 Pine kitapları ve 200 günlük kural (kullanıcı onayı 2026-10-26)

Kaynak: `docs/FAZ1_KAPANIS.md` §3 ve §6, `docs/GOREV_PAPER_KURULUM.md` Aşama B, `docs/PAPER_PLAN.md`.
Dal: `codex/faz2-basi` (`main`'den). Durum: `docs/codex_durum_faz2.md`. Ayrı PR'lar: İş 1, İş 2 sırayla; İş 3 ayrı oturumda paralel yapılabilir (dal `codex/faz2-dogrulama`, `paper/`'a dokunmaz).

**Değişmez:** yöntem, kapılar, eşikler, karar kodu, mevcut 11 kitabın kartları ve ağırlıkları. Testler zayıflatılmaz.
Gerçek para / aracı kurum yok. Repo herkese açık: anahtar ve kişisel veri yok. PR açmadan önce **tam test paketi**
(`python -m pytest -q`) koşulur ve sonucu PR açıklamasına yazılır. Belirsizlikte durup `codex_durum_faz2.md`'ye soru yazılır.

## İş 1 — TV-2 Pine paper kitapları (PR: `[Faz2] TV-2 Pine paper kitapları`)

| Kitap | Sembol | TF | Ağırlık | Not |
|---|---|---|---:|---|
| G4RNcGXg | SPY | 60 | .05 | ABD |
| wcegMOXj | BINANCE:ETHBTC | 360 | .05 | Kripto; PnL BTC → USD |
| yhoK9cH4 | META | 15 | .05 | Keşif |

Ağırlık toplamı .75 → .90 olur; kalan .10 nakit rezerv.

1. `paper/tv2_kitap.py`: `backtests/tv2.py` emülatörünü (aynı yorumlayıcı, aynı varsayılan parametreler, aynı maliyet:
   kripto %0,1/taraf, diğerleri %0,05/taraf + 1 tick; dolum sonraki bar açılışı) bu 3 kitap için **yalnız kapanmış
   barlarla** çalıştıran ince katman. Yeni bir backtest yöntemi yazılmaz; TV-2'nin `veri()` ve `strateji` yolları kullanılır.
2. **Kaynak doğrulama:** her koşuda `paper/tv2_kaynak/SURUMLER.csv` SHA256'sı kontrol edilir; uyuşmazsa o kitap çalışmaz,
   DURDUR alarmı yazılır. G4RNcGXg ve wcegMOXj dosyadan; yhoK9cH4 Actions'ta pine-facade'den çekilir (gerçek anahtar `PUB;561a4540b4d14f56b4c68cd3cecade24`, `arastirma/tv2_surumler.csv`; sürüm **1.0** sabit: `.../get/<pub>/1.0`, `last` değil), repoya **yazılmaz** (lisans belirtilmemiş), yalnız önbellekte/çalışma dizininde tutulur.
3. **wcegMOXj USD:** her değerlemede aynı zaman damgalı BTCUSDT kapanışıyla USD'ye çevrilir; defterde BTC bakiyesi,
   kur ve USD karşılığı ayrı kolon. Portföy özkaynağına USD girer.
4. **Portföye bağlama:** `paper/portfoy.yaml` satırlarına `kaynak: tv2` ile eklenir; `gunluk.py` `kaynak` alanına göre
   kart motoru ya da `tv2_kitap` yolunu seçer. Mevcut risk kuralları bu kitaplara da uygulanır (kitap %10 zirve
   düşüşü → kitap durur; portföy %5 → yeni giriş yok). Başlangıç: satır düzeyinde `baslangic` alanı (ör. `{id: G4RNcGXg, ..., kaynak: tv2, baslangic: 2026-10-27}`); varsa portföy `baslangic`'ını o kitap için geçersiz kılar. Codex PR'ı açtığı günün ertesini yazar; birleşme kayarsa lider birleştirmeden önce tarihi düzeltir. Bu tarihten önceki barlar işlenmez (ısınma hariç), geriye dönük dolum yok.
5. **Veri tazeliği:** SPY 1s ve META 15dk gün içi veri (yfinance sınırları: 60dk ≈ 730 gün, 15dk ≈ 60 gün) yalnız
   canlı dönem için yeterli; ısınma için gereken bar sayısı kaynaktan hesaplanıp kontrol edilir, yetmezse alarm.
   Saatlik iş (`.github/workflows/paper.yml`) 15dk kitabı için ek tetik gerektirmez; her koşuda kapanmış barları işler.
6. **Panel:** 3 kitap alan etiketiyle (ABD / Kripto / Keşif) görünür.
7. **Testler:** SHA uyuşmazlığında kitap durur; açık (kapanmamış) bar işlenmez; BTC→USD çevrimi; `kaynak: tv2` yolu
   seçimi; TV-2 backtest çıktısıyla paper koşucusunun aynı veride aynı işlemleri ürettiği tutarlılık testi (en az biri
   için, sabit örnek veriyle).
8. Yerel prova çıktısı PR açıklamasına.

## İş 2 — İPTAL (kullanıcı kararı 2026-10-26: stratejiler bu kuralla test edilmedi; uygulanmayacak)

~~200 günlük ortalama kuralı~~

Kural (`docs/PAPER_PLAN.md`): bir kitabın **yeni uzun** girişinde, referansın **sinyal gününden önceki kapanmış günlük
kapanışı** 200 günlük basit ortalamasının altındaysa giriş büyüklüğü **yarıya** iner. Referans (lider kararı): ABD ve Emtia kitapları
SPY, Kripto kitapları BTCUSDT; Keşif (META) SPY. Açık pozisyonlar ve çıkışlar etkilenmez; kısa girişler etkilenmez.

1. **Nedensellik zorunlu:** her tarih için yalnız o tarihten önceki veri kullanılır (bugünün kapanmamış barı yok,
   tüm seriden tek seferlik hesap yok). Test: geleceğe ait bir bar değiştirildiğinde geçmiş kararlar değişmez.
2. Kart motorunda (`tarama.prepare` sonrası boyutlandırma) ve `tv2_kitap`'ta aynı yardımcı fonksiyon kullanılır.
3. Defterde her girişe `rejim_carpani` (1 ya da 0,5) ve referans/ortalama değerleri yazılır; panelde bugünkü rejim.
4. Testler: eşik altı/üstü, sınırda eşitlik (altında değilse 1), kısa girişte etkisiz, nedensellik testi.

## İş 3 — Bekleyen 4 doğrulama (PR: `[Faz2] 4 doğrulama`)

Kaynak: Gemini araştırma notu (`arastirma/faz2_dogrulama_veri_notu.md`). Amaç: TV-2'de vekil veriyle geçen 4 stratejiyi
asıl piyasaya yakın **ücretsiz** veriyle, **aynı TV-2 emülatörü, aynı maliyet ve aynı kapıyla** (uygulanabilir sınama
net > 0) yeniden koşmak. Yöntem, kapı, eşik değişmez; yalnız veri (ve perp için funding) değişir.
Çıktı: `results/faz2_dogrulama.csv` (kimlik, veri, sınama işlem, net %, PF, MDD, TV-2 ilk sonuç, fark) + kısa
`docs/faz2_dogrulama.md`. Paper'a ekleme **yok**; karar kullanıcının.

| Kimlik | Asıl sembol | TV-2'de kullanılan | Doğrulama verisi |
|---|---|---|---|
| QCkIgf3z | COINBASE:ETHUSD 15 | Binance ETHUSDT 15m | Coinbase Exchange API `GET /products/ETH-USD/candles`, granularity 900 (anahtarsız, 300 mum/istek, sayfala) |
| BR74LOKo | BYBIT:BTCUSDT.P 15 | Binance spot BTCUSDT 15m | Binance USDⓈ-M perp BTCUSDT 15m (`data.binance.vision` futures/um) + funding |
| zuEOEYPK | BINGX:BTCUSDT.P 180 | Binance spot 1h → 180 | Binance USDⓈ-M perp 1h → 180 + funding |
| 9u8pzF0I | CME_MINI:MNQ1! 120 | yfinance MNQ=F 60m (düzeltilmemiş) | aşağıda |

1. **Perp + funding:** Binance UM perp klines ve funding geçmişi (`data.binance.vision` futures/um monthly
   `fundingRate`; yoksa `fapi/v1/fundingRate`). Bybit API GitHub Actions (ABD IP) tarafından engellenebilir; Binance UM
   vekil kabul (notta borsalar arası fark 1–5 bps). Funding anında (00/08/16 UTC) açık pozisyona
   `pozisyon_değeri × oran` uygulanır (uzun öder, kısa alır, oran negatifse tersi). Funding'li ve funding'siz sonuç
   ayrı kolon.
2. **9u8pzF0I (MNQ):** (a) Pine kaynağında pozisyon büyüklüğü / `default_qty` / kontrat çarpanı nasıl
   yorumlanıyor, emülatör MNQ için $2 çarpanı ve 0,25 tick'i doğru kullanıyor mu — yaz. (b) Vade devri:
   MNQ=F serisinde çeyreklik devir günlerini (Mar/Haz/Eyl/Ara 3. Cuma'dan önceki Pazartesi civarı, boşluğa göre tespit)
   bul, serinin geçmişini fark kadar kaydırarak geriye dönük düzeltilmiş (back-adjusted) seri üret, yeniden koş.
   (c) Vade boşluğu olmayan vekil olarak QQQ 60m → 120 ile koş (yalnız seans saatleri olduğunu not et).
   Üç sonuç ayrı satır. Devir barında açık pozisyon PnL'i kaç puan katkı yaptı, ayrıca raporla.
3. Her doğrulama için TV-2 ilk sonucuyla fark tablosu; kapıyı geçip geçmediği.
4. Testler: funding hesabı (uzun/kısa, işaret), back-adjust (devir boşluğu kapanır, devir sonrası fiyatlar
   değişmez), Coinbase sayfalama (örnek yanıtla, ağ yok).

## Teslim

`docs/codex_durum_faz2.md`: yapılanlar, test sonucu, açık sorular. Lider (Claude) denetler ve birleştirir.
