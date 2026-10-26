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

