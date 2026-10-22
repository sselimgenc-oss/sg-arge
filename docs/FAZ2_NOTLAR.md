# Faz 2 notları (kullanıcı istekleri, Faz 1 kapanınca ele alınacak)

## 1. Strateji radarı (yeni strateji yakalama)
- **Amaç:** Haftalık bir GitHub Actions işi, mevcut kartların geldiği sitelerden yeni stratejileri toplar.
- **Kaynaklar (kart sayısına göre):** TradingView 54, GitHub 41, ProRealCode 32, MQL5 26, ForexFactory 21, QuantifiedStrategies 34.
- **Kolay kaynaklar:**
  - RSS: QuantifiedStrategies, Substack;
  - GitHub arama API'si;
  - PapersWithBacktest;
  - r/algotrading;
  - ProRealCode kütüphanesi.
- **Zor kaynaklar:** TradingView (kullanım şartları, JavaScript), MQL5 ve ForexFactory (forum, giriş gerektiren içerik). Bunlar dışarıda kalır ya da linkleri kullanıcı elle ekler.
- **Akış:** tara → mevcut 422 kartla tekrar ele (URL + isim benzerliği) → `docs/radar/<yıl>-W<hafta>.md` PR'ı → ajan kartı yazar (uydurma yok) → `huni.yml`.
- **Kısıtlar:** Yalnız ücretsiz kaynaklar. Giriş yapılmaz, form doldurulmaz. Kart yazımı ajanla yapılır; otomatik LLM çağrısı ücretli olduğu için yalnız kullanıcı onayıyla eklenir.

## 2. strateji-test-pano'dan alınacak fikirler
Lider analizi (2026-10-22): Bu depodaki özellikler **arayüz taslağı**. Değerleri `data.json` içine elle yazılmış; onları üreten kod yok.
- `bot_engine.py` yalnız Binance'ten 10 kripto fiyatı çekip açık pozisyonların kâr/zararını günceller.
- "Claude'a sor" gerçek bir yapay zekâ çağrısı değil; anahtar kelimeye göre önceden yazılmış cevap seçer.
- "Gölge mod" (makine öğrenmesi filtresi) ve "Koç" bulguları `data.json`'da sabit metin. Model eğitimi ya da hesap kodu yok.
- Paneldeki performans rakamları (271 işlem, Sharpe 2.44, CAGR %42.6 vb.) doğrulanmış bir backtest'ten gelmiyor; kullanılmamalı.

Faz 2'de gerçek veriyle kurulabilecek olanlar:
- **a. İşlem açıklamaları:** Motor her işlemin giriş/çıkış nedenini zaten kaydediyor (`stop`, `hedef`, `gap_target`, `zaman_stop`...). Paper defterine "neden açıldı / neden kapandı" sütunu eklenebilir. Kolay iş.
- **b. Koç bulguları:** `results/` ve paper defterinden otomatik üretilebilir: hangi strateji zararda, hangi çıkış nedeni baskın, korelasyon. Kurallı metin, kolay iş.
- **c. Gölge mod (ML filtresi):** Her sinyal için geçmiş işlemlerden "bu işlemin R'si" tahmin edilir; negatifler pas geçilir, ama yalnız gölgede, yani gerçek defter etkilenmez. Aşırı uyum riski yüksek olduğu için:
  - walk-forward eğitim;
  - ön kayıt;
  - en az 6 ay gölge kayıt;
  - filtreli ve filtresiz defter karşılaştırması.

  Önce gölgede kanıtlanmadan kullanılmaz.
- **d. "Claude'a sor":** Gerçek bir soru-cevap için ya ücretli bir API ya da artifact yetenekleri (runtime) gerekir. Kullanıcı kararı.
