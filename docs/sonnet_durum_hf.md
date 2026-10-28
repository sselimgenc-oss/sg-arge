# Durum: HF doğrulama (dal `claude/hf-dogrulama`)

- [x] `copytrade/hf_dogrulama.py`: envanter (alt küme adı, satır, sütun, tarih aralığı, veri kartı metni), gün başına kapsam ve boşluk listesi,
      kapı adresleri (en son `sonuc.csv`, bugünkü hesap değeri dolu, adrese göre ilk 30) ↔ Hyperliquid `clearinghouseState` (ana / +HIP-3 / +spot USDC)
      ve `portfolio` en yakın nokta; ledger/yatırma-çekme sütunu taraması. Çıktı `hf_dogrulama.json`.
- [x] `.github/workflows/hf_dogrulama.yml` (kendi dalında push tetiği + elle); hata iş akışını kırmızı yapar, JSON yine yüklenir.
- [x] Testler `tests/test_hf_dogrulama.py`: yol üretimi, boşluk sayımı, göreli fark (elle hesaplı), yerel hive parquet üstünde DuckDB sorguları, çapraz doğrulama altın örneği.
- [ ] **Canlı Actions koşusu**: sonuç PR açıklamasına eklenecek. Tolerans/"kullanılır" kararı yok; sayılar raporlanır.

## Varsayımlar (belgede yazmıyordu)
- Bölüm düzeni `<alt küme>/date=YYYY-MM-DD/*.parquet`, `account_values` için `user` ve `account_value` sütunları (Argon notu). Farklı çıkarsa ilgili adım
  `hatalar`'a yazılır ve iş kırmızı olur.
- HF `account_value` bir adresin tüm dex/teminat satırlarının TOPLAMI alınır; karşılaştırma üç canlı toplamla (ana, ana+HIP-3, ana+HIP-3+spot USDC) ayrı ayrı raporlanır.
- Geçmiş tarihler en son günden 30/90/180 gün önceye en yakın mevcut bölüm günüdür; HF günü için karşılaştırma anı o günün UTC öğle vaktidir.
- `duckdb==1.3.2` `requirements.txt`'e eklendi (tüm iş akışlarının pip kurulumuna girer).
