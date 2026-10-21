# Proje hedefi ve ana plan (lider, 2026-10-21)

## Kullanıcının amacı (kendi sözleriyle, özet)
Algo trading. PDF'lerde ve listelerde yüzlerce strateji var; day trade ve swing olarak işlem yapmak istiyor.
1. Ekip **evrensel teknik analiz/uygulama kurallarını** ve **kurumsal trader'ların bir stratejiyi paper trade'e uygun bulma/bulmama kriterlerini** belirleyecek.
2. **Tüm stratejiler** bu kriterlere göre backtest edilecek; kullanıcıya **başarılı ve başarısız listesi** verilecek.
3. Paper trade sonraki faz; bu fazın kapsamı dışında.

## Ölçek
- `strateji_listesi (2).xlsx`: 281 strateji (138 day, 95 swing, 48 belirsiz; TradingView, ProRealCode, MQL5, Matriks, QuantifiedStrategies ...). Güncel liste budur; `strateji_listesi.xlsx` (243) eski sürüm.
- PDF raporları: ~35 strateji (`docs/KATALOG.csv`).
- Toplam ~316 aday.

## Mimari karar: huni + ortak strateji formatı
316 stratejiyi tek tek elle kodlamak bütçeyi bitirir. Bunun yerine:
1. **Aşama 0 - Triyaj ve kart (Sonnet, ucuz):** her strateji makinece okunur YAML karta çevrilir (`docs/spec/<id>.yaml`, şema `docs/EVRENSEL_KURALLAR.md`). Kuralı gizli/ücretli/üyelere özel olan → **Doğrulanamaz (spesifikasyon yok)**, backtest yok.
2. **Aşama 1 - Hızlı tarama (Codex, VectorBT):** YAML'ı okuyan tek yorumlayıcı + ortak gösterge kütüphanesi; evrensel kurallar, yazar varsayılan parametreleri, 1x ve 2x maliyet, 4 piyasa. Açık kaybedenler **Reddedildi**.
3. **Aşama 2 - Tam doğrulama (Codex, event-driven motor):** sağ kalanlara `ELEME_KRITERLERI.md` testleri 3-10.
4. **Çıktı:** `results/SONUC.md` + `results/sonuc.csv`: her strateji için Geçti / Koşullu / Doğrulanamaz / Reddedildi ve gerekçe. Bu, kullanıcıya teslim edilecek "başarılı/başarısız" listesidir.

T1a (Codex Algo pilotu) motoru ve veri katmanını kurar; aşama 2'nin referans uygulamasıdır.
