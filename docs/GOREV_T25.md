# T25 — Nihai sonuç raporu v2: başarılı/başarısız listesi (sahibi: claude-moderator / Sonnet)

## Neden
Projenin asıl çıktısı (docs/HEDEF.md), kullanıcıya verilecek **başarılı/başarısız strateji listesidir**. `backtests/sonuc_raporu.py` (T13) bu listeyi üretiyor, ama yazıldığından beri gelen sonuçları bilmiyor:
- `results/asama2b_pit.csv` (PIT evren; C07 ve R01 burada **Geçti**). PIT satırı varsa sabit evren satırının yerine geçmeli.
- `results/tarama_rotasyon.csv` ve rotasyon satırları (`metrik: PF+CAGR`, T23). Rapor şu an rotasyon kartlarını "Ertelendi (portföy rotasyonu)" sayıyor; bu artık yanlış.
- Gün içi satırlar (`tf` 1H/30m/15m/5m; T12/T17/T24). Aynı kart birden fazla tf ve piyasada olabilir.
- `results/portfoy.md`: önerilen paper portföy.
- T16/T19/T20/T21/T22 gerekçeleri (`belirsiz` notları, `ozel_kod_nedeni`, `spec_durumu`: eksik, sadece_short, ihtiyari, kapsam_disi).

## İstenenler
1. **Kart başına tek nihai durum.** Öncelik sırası:
   **Geçti > Koşullu > Reddedildi > Doğrulanamaz > Ertelendi > Kapsam dışı**.

   En iyi piyasa/tf satırı esas alınır. Diğer piyasa/tf satırları `piyasa_ayrintisi` sütununda kısaca listelenir.
2. **Alt neden standart olmalı.** Kullanıcı "neden elendi?" sorusunun cevabını tek bakışta görmeli. Örnekler:
   - `asama1: PF<1.2`
   - `asama2a: null'u gecemedi (piyasa betasi)`
   - `asama2b: bootstrap MDD95>%15`
   - `asama2b: OOS ortR<=0`
   - `dogrulanamaz: kaynakta sinyal tanimi yok`
   - `dogrulanamaz: dakikalik veri yok (DAX)`
   - `ertelendi: sadece short`
3. **`results/SONUC.md` yapısı (Türkçe, kullanıcı için):**
   - **Özet sayılar:** durumlara göre adet; ayrıca günlük/swing ve gün içi (day) olarak ayrı ayrı.
   - **Paper trade'e hazır (Geçti):** kart, piyasa, tf. Tablo sütunları: PF, OOS getiri, bootstrap MDD95, evren (pit/sabit).
   - **Koşullu:** her satırın şerhi (survivorship, ön dönem negatif vb.).
   - **Önerilen portföy:** `results/portfoy.md` özeti ve bağlantısı.
   - **Reddedildi:** aşamaya göre gruplu (1 / 2a / 2b), alt nedenle.
   - **Doğrulanamaz ve Ertelendi:** nedene göre gruplu, adetli; kart listesi katlanabilir (`<details>`).
   - **Yöntem özeti:** EVRENSEL_KURALLAR'a bağlantı ve kapıların bir paragraflık açıklaması.
4. **`results/SONUC.csv`:** aynı tablo, makine okunur biçimde.
5. **Ek hesap yok.** Rapor yalnız mevcut sonuç dosyalarını birleştirir; backtest koşmaz. Eksik dosya varsa raporun başında "Henüz yok: …" yazar.
6. **Testler:** sentetik sonuç dosyalarıyla şunlar sınanmalı:
   - öncelik sırası;
   - PIT satırının sabit evren satırını ezmesi;
   - rotasyon satırının "Ertelendi" sayılmaması;
   - gün içi + günlük aynı kartta en iyi satırın seçilmesi;
   - eksik dosya uyarısı.
7. Mevcut `results/*.csv` dosyalarıyla raporu **sen üret ve commit et**. Bu bir backtest değil, birleştirme; gerçek koşu gerekmez. Lider son sonuçlar gelince yeniden üretecek.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç.
