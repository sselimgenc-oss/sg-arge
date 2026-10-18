# Kağıt Hesaplar Pro: 7/24 Otonom Paper Trading & Bulut Panosu

Bu depo, sıfır sunucu maliyetiyle çalışan, canlı piyasa verileriyle işlem yapan ve 13 modüllü profesyonel kantitatif analiz panosunu barındıran tam otonom bir paper trading altyapısıdır.

---

## 🚀 3 Adımda 7/24 Canlı Kurulum

### Adım 1: Depo Oluşturun ve Dosyaları Yükleyin
1. [GitHub.com](https://github.com) üzerinde yeni bir depo açın (örneğin: `kagit-hesaplar`).
2. Deponun içine şu dosyaları yükleyin:
   - `index.html` (veya `paper_trading_dashboard.html`)
   - `bot_engine.py` (Kantitatif işlem ve fiyat motoru)
   - `data.json` (Merkezi veri tabanı)
   - `.github/workflows/paper_trader.yml` (Otomasyon betiği)

### Adım 2: GitHub Actions İzinlerini Açın
1. Deponuzda **Settings (Ayarlar) -> Actions -> General** sekmesine gidin.
2. Sayfanın en altındaki **Workflow permissions** bölümünde:
   - **"Read and write permissions"** seçeneğini işaretleyin ve **Save** butonuna basın.
   *(Bu ayar, botun saat başı `data.json` dosyasını güncelleyebilmesini sağlar).*

### Adım 3: GitHub Pages'i Etkinleştirin (Ücretsiz Web Sitesi)
1. Deponuzda **Settings -> Pages** sekmesine gidin.
2. **Build and deployment -> Source** kısmından **Deploy from a branch** seçin.
3. Branch olarak `main` ve `/ (root)` seçip **Save** butonuna basın.
4. Birkaç dakika sonra size özel canlı pano linkiniz hazır olacaktır (örneğin: `https://kullaniciadi.github.io/kagit-hesaplar/`).

---

## ⚙️ Nasıl Çalışır?
- **Zamanlama:** Her saat başını 11 geçe (`:11`) GitHub Actions arka planda ücretsiz sanal makineyi başlatır.
- **Veri Kaynağı:** Binance Public API ve Yahoo Finance üzerinden hiçbir API anahtarı gerektirmeden canlı fiyatları çeker.
- **Risk & İcra:** Stop loss, kâr al ve R-katı hesaplanır, açık/kapanan işlemler güncellenir.
- **Pano:** Web tarayıcınız veya telefonunuz panoyu açtığında her zaman en güncel durumu gösterir.
