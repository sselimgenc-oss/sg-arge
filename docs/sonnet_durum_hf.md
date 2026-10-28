# Durum: HF doğrulama (dal `claude/hf-dogrulama`)

- [x] `copytrade/hf_dogrulama.py`: envanter (alt küme adı, satır, sütun, tarih aralığı, veri kartı metni), gün başına kapsam ve boşluk listesi,
      kapı adresleri (en son `sonuc.csv`, bugünkü hesap değeri dolu, adrese göre ilk 30) ↔ Hyperliquid `clearinghouseState` (ana / +HIP-3 / +spot USDC)
      ve `portfolio` en yakın nokta; ledger/yatırma-çekme sütunu taraması. Çıktı `hf_dogrulama.json`.
- [x] `.github/workflows/hf_dogrulama.yml` (kendi dalında push tetiği + elle); hata iş akışını kırmızı yapar, JSON yine yüklenir.
- [x] Testler `tests/test_hf_dogrulama.py`: yol üretimi, boşluk sayımı, göreli fark (elle hesaplı), yerel hive parquet üstünde DuckDB sorguları, çapraz doğrulama altın örneği.
- [x] Koşu 1 ([40722531503](https://github.com/sselimgenc-oss/sg-arge/actions/runs/40722531503)) kırmızı: HF `date=*` joker listelemesi 429 verdi (DuckDB her dizini ayrı API çağrısıyla listeliyor); gerçek alt kümeler 11 (görev 9 demişti): account_values, asset_ctxs, candles_1s, liquidations, notebooks, orderbook_1m, outcome_fills, perp_fills_all, snapshots_perp, snapshots_spot, spot_fills. Düzeltme: alt küme başına tek `recursive` ağaç listesi, DuckDB'ye açık dosya URL'leri, 429/5xx için üstel bekleme, parquet olmayan alt kümeler (notebooks) bilgi olarak raporlanır, isteğe bağlı `HF_TOKEN`.
- [ ] **Canlı Actions koşusu (2.)**: sonuç PR açıklamasına eklenecek. Tolerans/"kullanılır" kararı yok; sayılar raporlanır.

## Varsayımlar (belgede yazmıyordu)
- Bölüm düzeni `<alt küme>/date=YYYY-MM-DD/*.parquet`, `account_values` için `user` ve `account_value` sütunları (Argon notu). Farklı çıkarsa ilgili adım
  `hatalar`'a yazılır ve iş kırmızı olur.
- HF `account_value` bir adresin tüm dex/teminat satırlarının TOPLAMI alınır; karşılaştırma üç canlı toplamla (ana, ana+HIP-3, ana+HIP-3+spot USDC) ayrı ayrı raporlanır.
- Geçmiş tarihler en son günden 30/90/180 gün önceye en yakın mevcut bölüm günüdür; HF günü için karşılaştırma anı o günün UTC öğle vaktidir.
- `duckdb==1.3.2` `requirements.txt`'e eklendi (tüm iş akışlarının pip kurulumuna girer).

## Koşu 2 ([40728025308](https://github.com/sselimgenc-oss/sg-arge/actions/runs/40728025308)): iptal (iş zaman aşımı)
- Kuyrukta beklemedi: 16:39'da başladı, `Doğrulama` adımı 3 saat sessizce çalıştı (günlükte hiç çıktı yok) ve 180 dk iş zaman aşımında (19:39) iptal edildi; JSON üretilemedi. Neden büyük olasılıkla alt küme başına tüm parquet altbilgilerinin (satır sayımı) tek tek uzaktan okunması: bilinmiyor, günlük olmadığı için doğrulanamadı.
- Düzeltme: anlık ilerleme günlüğü (`python -u`, stderr), adım başına süre bütçesi (`--butce-envanter/-kapsam/-capraz`; bütçe dolunca parçalar arasında durur, **kısmi sonuç açıkça işaretlenir**: `satir_kismi`, `kismi`), her adımdan sonra kısmi JSON yazımı, `Doğrulama` adımına 150 dk sınırı (özet + artefakt yine çalışır), güvenlik ağı olarak bütçe+300 sn sonra DuckDB sorgusu kesilir. Yöntem aynı; yalnız süre yönetimi.
- [ ] Koşu 3 sonucu PR açıklamasına eklenecek.
