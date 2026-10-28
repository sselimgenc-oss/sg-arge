# Görev: Arşiv + tarama altyapısı (Faz A, 2026-10-28, lider; kullanıcı onaylı)

Yapan: **Codex**. Dal: `codex/arsiv`. Tek PR, `main`'e; lider birleştirir. Önce `DURUM.md`, `docs/GOREV_D_YOLU.md` (Faz A),
`docs/VERI_SOZLESMESI.md`. Ağ: Hyperliquid'e bulut oturumundan erişim yok → koşular GitHub Actions'ta.

## Amaç
Hyperliquid'in sınırlı verdiği ve sonradan alınamayan verileri bugünden, az yer kaplayan ve kolay analiz edilen biçimde saklamak.

## İşler
1. **Yazıcı** `copytrade/arsiv.py`: Parquet (zstd), yol `tur=<tur>/gun=YYYY-MM-DD/<parca>.parquet`; yalnız ekleme; her satırda
   `sema_surumu`, `alindi_ms`. Aynı kaydı iki kez yazmamak için tür başına tekil anahtar (ör. dolum: `adres, tid`).
2. **Türler:**
   - `leaderboard`: haftalık tam anlık görüntü (tüm satırlar ve sütunlar).
   - `dolum`: havuzdaki adreslerin dolumları (`userFillsByTime`, son kayıttan devam; 10.000 sınırına dayanan adres işaretlenir).
   - `funding`: aynı adreslerin `userFunding` kayıtları.
   - `mum_1dk`: havuzun işlem gördüğü coinler (HIP-3 dahil) için 1 dakikalık mumlar.
   - `pozisyon`: havuzdaki adreslerin `clearinghouseState` anlık görüntüsü (gölge motoru bunu kullanacak).
   - `olay`: kat/kol giriş-çıkışları (şimdilik boş şema; Sonnet'in gölge motoru yazacak).
3. **Havuz listesi:** şimdilik kapı sonucunun ön elemeyi geçen adresleri + `izleme_listesi.yaml`; kaynak dosyası tek yerde.
4. **Depo:** Cloudflare R2 (S3 uyumlu). Anahtarlar yalnız GitHub Secrets (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`,
   `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`); kodda/logda asla görünmez. Yerel geliştirmede klasöre yazar (aynı yol yapısı).
5. **İş akışı** `arsiv.yml`: mum + pozisyon sık (hedef 15 dk; GitHub zamanlaması gecikebilir, boşluk kaydedilir), dolum + funding
   saatlik, leaderboard haftalık. Hata `|| true` ile örtülmez.
6. **Kapsam özeti:** her gün `tur=kapsam/` altına: tür başına adres, satır, ilk/son zaman, boşluk (beklenen aralıkta veri yok) sayısı.
   Boşluk oranı `kurallar.yaml` eşiğini aşarsa iş kırmızı.
7. **Tarama altyapısı ölçümü (K8):** 300 adresi Worker ücretsiz planında dönüşümlü taramanın süresini ve Hyperliquid istek
   ağırlığını ölç; sonucu durum dosyasına yaz. Worker'a taşıma bu görevde yok, yalnız ölçüm ve öneri.

## Kabul
- Altın örnek testleri: tekilleştirme (aynı dolum iki kez gelir → bir satır), sınır işareti, boşluk sayımı, yol yapısı.
- Canlı koşu: en az 24 saat çalışmış arşivin kapsam özeti PR açıklamasında (tür başına satır, adres, boşluk; sütun min/medyan/max).
- Toplam boyut ve günlük büyüme tahmini (R2 ücretsiz katmanına kaç gün/ay sığar).
- Durum: `docs/codex_durum_arsiv.md`.
