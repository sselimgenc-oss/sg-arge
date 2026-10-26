# Görev: Kapı kontrolü — plasebo kalibrasyonu ve 13 paper kitabının geriye dönük kontrolü (2026-10-26)

Kaynak: `docs/kapi_degerlendirme.md` §5–6. Dal: `codex/kapi-kontrol` (`main`'den). Durum: `docs/codex_durum_kapi.md`.
PR: `[Faz2] kapı kontrolü`. **Bilgi amaçlı ölçüm:** yöntem, kapı, eşik, karar tabloları ve paper değişmez; karar
önerisi yazılmaz (karar kullanıcının). Mevcut motor kullanılır: `engine/tv_emulator.py`, `backtests/tv2.py`,
`backtests/tarama.py`, `backtests/asama2a.py` (`random_entry_signals` mantığı). Yeni backtest yöntemi icat edilmez.

## 1. Plasebo kalibrasyonu (`backtests/plasebo.py`)
Kapsam: TV-2'de geçen 96 strateji (`results/tv2/satirlar/*.json`, `karar == "gecti"`) ve U7'de geçen 85 varyant
(`results/u7/siralama.csv`).
- Her strateji için **1.000 rastgele giriş stratejisi**: aynı sembol(ler), aynı **sınama dönemi** (TV-2: sürüm
  tarihi sonrası; U7: 2023-01-01 sonrası), aynı yön karışımı (long/short), yaklaşık aynı işlem sayısı ve tutma süresi
  dağılımı (stratejinin kendi işlemlerinden), aynı maliyet (`gercekci`: kripto %0,1/taraf, diğer %0,05/taraf + 1 tick).
- Sabit tohum (`zlib.crc32(kimlik)`); sonuçlar yeniden üretilebilir.
- Çıktı `results/plasebo.csv`: kimlik, kaynak, piyasa, tf, maruziyet (pozisyonda geçen süre oranı), gerçek net %,
  plasebo net % p50/p95, **plasebolarda net > 0 oranı** (= kapının yanlış geçme oranı), gerçek stratejinin plasebo
  yüzdeliği ve p-değeri.
- Özet: yanlış geçme oranı zaman dilimi, piyasa ve maruziyet dilimlerine göre (tablo).
- Hesap uzunsa (`> 30 dk`) GitHub Actions iş akışına koy (`.github/workflows/plasebo.yml`, `workflow_dispatch` +
  `push` tetiği yalnız `codex/kapi-kontrol` dalında); sonucu dala yazsın.

## 2. 13 paper kitabının geriye dönük kontrolü (`results/kapi_kontrol_13.csv`)
Kitaplar: `paper/portfoy.yaml` satırları (11 U7 + G4RNcGXg + yhoK9cH4). Sınama dönemi günlük net getirileri
(`results/u7/**/getiriler`, `results/tv2/getiriler/<id>.csv`):
- **Maruziyet eşleşmiş kıyas:** günlük `w_t × piyasa_t + (1 − w_t) × 0` (w_t = o gün pozisyonda olan sermaye oranı;
  bilinmiyorsa ortalama maruziyet); piyasa: ABD → SPY, kripto → BTCUSDT, emtia → GLD. Strateji − kıyas yıllık fark.
- **Beta, beta ayarlı alfa** (günlük regresyon, yıllık) ve **Newey-West t** (gecikme 5).
- **Plasebo yüzdeliği:** madde 1'den.
- **DSR:** deneme sayısı N_eff = geçenlerin korelasyon kümelemesiyle (hiyerarşik, eşik 0,9) bulunan küme sayısı;
  ham N de ayrıca yazılır.
- Eski hunideki null sonucu (`results/u7/*/huni_ozet.csv`: `null_gecti`, `p_pf`, `p_ortr`) yan sütun.

## 3. Özet `docs/kapi_kontrol.md`
Tablo + en çok 10 madde yorum (ne ölçüldü, ne bulundu, sınırlamalar). Karar önerisi yok.

## 4. Testler (ağsız)
Plasebo üreticisi işlem sayısı ve tutma süresini koruyor; sabit tohumla aynı sonuç; bilinen alfalı sentetik seride
alfa anlamlı, alfasız seride anlamsız; maruziyet eşleşmiş kıyasın w = 0 ve w = 1 uç durumları; N_eff kümeleme.
