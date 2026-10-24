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

## 2. strateji-test-pano: Faz 2 arayüzü
**Kullanıcı kararı:** Bu depo arayüz ve fikir taslağı olarak hazırlandı; içindeki stratejiler ve rakamlar önemli değil. Faz 1'den sonra bu arayüz bizim gerçek sonuçlarımızla doldurulup faaliyete alınacak.

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

## 3. Birleşik pano (kullanıcı kararı, 2026-10-22)
- **Arayüz:** `strateji-test-pano` (zengin arayüz) ile `sg-test-panel` (sade, `paper/panel.py` şeması zaten bu panoya uyuyor) birleştirilecek. Tek pano; veri `paper/` ve `results/`'tan gelir.
- **Kullanıcının en çok önem verdiği iki modül:**
  1. **Öğrenen koç (ML):** Pano açtığı işlemlerden öğrenir, stratejinin açıklarını bulur, düzeltme **önerisi** sunar.
  2. **Strateji radarı:** Bölüm 1.

### Öğrenen koç: güvenli tasarım (lider önerisi)
- **Veri:** Paper işlemleri tek başına az (birkaç strateji, yılda ~100 işlem). Öğrenme, backtest işlem kayıtlarından (`results/tarama_islemler`, huni koşusuyla yeniden üretilir; repoda tutulmaz) yapılır; paper işlemleri doğrulama içindir.
- **Ne öğrenir:** Kaybeden işlemlerin ortak özellikleri. Örnekler: rejim (trend/yatay, volatilite), giriş anındaki gösterge değerleri, gün/saat, sembol, çıkış nedeni dağılımı. Yöntem: yorumlanabilir modeller (karar ağacı, gradient boosting + SHAP). Kara kutu kullanılmaz.
- **Ne üretir:** Öneri kartı. Örnek: "ADX<15 iken girişlerin ortR −0.4; filtre eklenirse IS PF 1.3→1.6".
- **Öneri otomatik uygulanmaz.** Her öneri yeni bir **varyant kart** olur ve aynı huniden geçer: 2a, 2b, OOS.
- **Çoklu deneme sayacı:** Her denenen öneri DSR deneme sayısına eklenir. Koç ne kadar çok öneri denerse eşik o kadar yükselir. Aksi halde koç geçmişe uyan sahte iyileştirmeler üretir.
- **Doğrulama:** Önerilen varyant önce **gölge modda** paper'da en az 3–6 ay orijinalin yanında koşar. Yalnız orijinali anlamlı biçimde geçerse kullanıcı onayıyla devreye alınır.
- **Açıklama:** Her öneri "neden" ile gelir: hangi işlemler, kaç örnek, IS/OOS farkı, deneme sayısı.
