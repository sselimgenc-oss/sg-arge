# Görev: Kapı düzeltmesi — `binance_payi` boş sütunu (Faz 0 engeli, 2026-10-28, lider)

Yapan: **Sonnet**. Dal: `claude/kapi-duzeltme`. Küçük PR, `main`'e; lider birleştirir. `docs/GOREV_GOLGE.md`'den önce yapılır.

## Bulgu
Hızlı koşu [run 24](https://github.com/sselimgenc-oss/sg-arge/actions/runs/40615667914): 24 parçanın hepsi başarılı; birleştirmede
akıl sağlığı kapısı durdurdu (doğru davranış, yayım olmadı):
`binance_payi: tabloda tamamen boş sütun`.

## Kök neden (lider teşhisi)
`copytrade/kapi.py` ~600–608: `out["binance_payi"] = None` yazılıyor; `if not total: return out` erken dönüşü, Binance sembol
listesi alınamadığında (Actions'ta HTTP 451) sütunu silen `out.pop(...)` satırına hiç ulaşmıyor. Hacmi 0 olan satırlar sütunu `None`
ile taşıyor → sütun var ama tamamen boş.

## İş
1. Sembol listesi yoksa sütun her yolda yazılmasın; liste varken hacim 0 ise değer tanımlı bir boş olsun (karar: `None`, ve bu durumda
   sütun kapı kuralında boş sayılmamalı mı — `saglik_bos_olabilir`'e ekleme yapma; liste varken hacim 0 olan satır zaten kapı dışı mı,
   kontrol et ve durum dosyasına yaz).
2. Altın örnek: `symbols=None` + hacim 0 → anahtar yok; `symbols=None` + hacim > 0 → anahtar yok; liste var + hacim > 0 → doğru oran.
3. Hızlı koşuyu yeniden tetikle (`copytrade/kapi/CALISTIR`, `mod=hizli`), kapı yeşil ve sütun özeti PR açıklamasında.

## Kabul
Tam test paketi; hızlı koşu yeşil; sütun özeti (satır, her sütun min/medyan/max). Sonra lider tam koşuyu başlatır.
