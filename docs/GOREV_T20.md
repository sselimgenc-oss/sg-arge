# T20 — Özel kodlu kartları motora taşıma, parti 1 (sahibi: claude-moderator / Sonnet)

## Amaç
`tam`/`dakikalik` olup `ozel_kod: true` olan 76 kart taranamıyor. T20 bunların motor dışında kalan küçük grubunu (20 kart) açar. Seans saati (21) ve portföy rotasyonu (11) sonraki iş paketleridir (Codex); özel gösterge ve kaynağı belirsiz kartlar (20) Argon'un formül ve kaynak avından sonra ele alınacak.

## Kartlar
| Neden | Kartlar |
|---|---|
| bekleyen_emir (T15 ile destekleniyor, yalnız kartı çevir) | A2-014, A4-006 |
| sinyal_bari_referansi | A3-002c, M013 |
| durum_makinesi / durum_bilgisi | A2-020, A3-001, M019, O1-048, O2-008, R07 |
| desen | A1-027, A2-006, A3-002b, A3-002e, A6-015, O1-046, P3-010 |
| renko | A2-022, M027, O1-067 |
| cok_enstruman (yalnız değerlendir) | M010, O1-070 |

## Kurallar
1. **Mümkünse ifade diline çevir.** Mevcut göstergeler ve `engine/expr.py` yeterliyse yeni kod yazma.
2. **Yeni ilkel gerekiyorsa** `engine/gosterge.py` ya da `engine/kart_sinyal.py`'ye genel bir ilkel ekle, karta özel kod yazma.
   - Durum makinesi ilkeli örneği: "A olduktan sonra N bar içinde B" (`ardisik`/`sonra`).
   - Desenler: engulfing, inside bar, pin bar gibi standart tanımlarla, TA-Lib CDL fonksiyonlarına karşı test et.
   - Renko: kapanış bazlı tuğla, sabit ya da ATR kutu; **look-ahead olmamalı**, tuğla ancak kapanmış barla oluşur.
3. **Look-ahead testi:** Her yeni ilkel için şu test zorunlu: sinyal t anında yalnız t'ye kadarki veriyle hesaplanır. Seriyi t'de kesip yeniden hesaplayınca t'ye kadarki değerler aynı kalmalı.
4. **Kaynaktaki parametreler korunur;** tahmin yok. Kaynak yetmiyorsa kart `eksik` kalır, gerekçesi `belirsiz`e yazılır.
5. `cok_enstruman` kartları: çift/sepet işlemi gerektiriyorsa kapsam dışı olarak işaretle, gerekçeyi yaz; uzun-tek-enstrümana indirgenebiliyorsa çevir.
6. Taşınan kartta `ozel_kod: false`, `python -m engine.spec --kontrol docs/spec/` hatasız, `INDEKS.csv` yeniden üretilmiş olmalı.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. PR gövdesinde taşınan / kalan / kapsam dışı kart tablosu. Gerçek taramayı lider yapar.
