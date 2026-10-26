# Faz 2 durumu

## İş 1 — TV-2 Pine paper kitapları

Durum: tamamlandı; dal uzak repoya gönderildi. PR oluşturma, geçersiz
`GH_TOKEN` nedeniyle GitHub API tarafından reddedildi.

### Yapılanlar

- `paper/tv2_kitap.py` eklendi. G4RNcGXg, wcegMOXj ve yhoK9cH4, TV-2'nin
  mevcut veri, Pine yorumlayıcı ve emülatör yollarıyla yalnız kapanmış
  barlarda çalışır; dolumlar sonraki barın açılışındadır.
- Her koşuda `paper/tv2_kaynak/SURUMLER.csv` SHA256 doğrulaması yapılır.
  SHA uyuşmazlığı veya kaynak/veri hatası yalnız ilgili kitabı durdurur ve
  deftere `DURDUR` alarmı ekler.
- yhoK9cH4, Actions'ta gerçek yayın anahtarı
  `PUB;561a4540b4d14f56b4c68cd3cecade24` ile sabit `/1.0` uç noktasından
  alınır; `last` kullanılmaz ve kaynak repoya yazılmaz. Yerel testler sahte
  kaynak sağlayıcı kullanır.
- wcegMOXj özkaynağı BTC bakiyesi × aynı zaman damgalı BTCUSDT kapanışıyla
  USD'ye çevrilir. Defter özkaynak kayıtlarında `btc_bakiye`, `btc_usd_kur`
  ve `usd_karsiligi` alanları eklendi.
- Portföye üç TV-2 satırı eklendi: toplam ağırlık %90, nakit rezerv %10.
  Satır başlangıçları `2026-10-27` (PR açılış gününün ertesi) olarak
  ayarlandı; öncesi yalnız gösterge ısınmasıdır.
- Panel, satırdaki alan etiketini (ABD / Kripto / Keşif) gösterir.

### Test ve yerel prova

- TV-2 özel testleri: kaynak SHA durdurması, sabit yho sürümü, kapanmamış
  barın atılması, BTC→USD dönüşümü, `kaynak: tv2` yönlendirmesi ve sabit
  veride emülatör tutarlılığı.
- Tam paket: `/tmp/sg-arge-venv/bin/python -m pytest -q` →
  **1348 geçti, 4 atlandı, 1375 uyarı** (170.91 sn).

### Açık soru

- PR açma yetkisi: mevcut `GH_TOKEN` geçersiz. Dal:
  `codex/faz2-basi` (PR oluşturma sayfası:
  `https://github.com/sselimgenc-oss/sg-arge/pull/new/codex/faz2-basi`).


## Lider denetimi (2026-10-26)

- **Düzeltildi — TV-2 kurulumu:** `PineStrateji` TV-2 `kos` ile aynı kurulmuyordu (mintick hep 0,01, saat dilimi hep
  UTC, dış veri sağlayıcısı yok). ETHBTC'de `stop = hprice + syminfo.mintick` ve 1 tick kayma %30 sapma demekti.
  Artık mintick Binance verisinde borsa tick'i, ABD'de 0,01; saat dilimi kripto UTC / ABD New York; kripto kuralı
  veri notuna göre. Test eklendi.
- **Düzeltildi — sabit adet kaldıracı:** G4RNcGXg `strategy.fixed` 3 adet, pyramiding 3, yazar sermayesi 10.000.
  250 USD kitapta 9 SPY ≈ 20x kaldıraçtı (prova: 2 ayda +%20). Koşu artık yazarın `initial_capital`'ıyla (TV-2 ile
  aynı) yapılır, adet/maliyet/PnL/özkaynak kitap sermayesine oranlanır. Prova: 2 ayda +%0,5. Test eklendi.
- **Kullanıcı kararı:** wcegMOXj portföyden çıktı (tek enstrüman ETHBTC). BTC→USD kodu kalır, kullanılmaz.
- İş 2 (200 günlük kural) bu dalda yok; İş 3 dalı (`codex/faz2-dogrulama`) uzak repoya gönderilmemiş.
- **Düzeltildi — kaynak hatası alarmı:** SHA/ağ/veri hatası artık kalıcı `DURDUR` değil `KAYNAK_HATASI`; kitap o koşuda çalışmaz, sonraki koşu yeniden dener (tek bir pine-facade hatası yho kitabını kalıcı kapatırdı).

## İş 3 — dört doğrulama (Codex)

- TV-2 Pine yorumlayıcısı ve mevcut gerçekçi maliyet ayarlarıyla çalışacak `backtests/faz2_dogrulama.py` eklendi.
- Coinbase sayfalama, perp funding işareti ve MNQ back-adjust için ağsız birim testleri eklendi.
- MNQ doğrulamasında emülatöre kontrat puan değeri tanımı eklendi (`$2`, `0,25` tick); varsayılan değer 1 olduğundan mevcut strateji sonuçlarını değiştirmez.
- `paper/` dizinine dokunulmadı.

## Açık durum

- Tam ağlı koşu denendi; ortam vekili `api.exchange.coinbase.com` için `403 Forbidden` verdi. Bu nedenle doğrulama verisi indirilemedi ve sayısal sonuç CSV'si üretilmedi; uydurma sonuç yazılmadı. Erişim sağlandığında `python -m backtests.faz2_dogrulama` tüm satırları üretir.
- Lider: bu ortamda da vekil Coinbase için 403 veriyor; koşu GitHub Actions'a taşındı (`.github/workflows/faz2_dogrulama.yml`).
