# T21 — Özel gösterge ve belirsiz tanımlı kartlar (sahibi: claude-moderator / Sonnet)

T20'de A3-002b/c için Pine kaynağını raw.githubusercontent üzerinden okuyabildin. Aynı yöntemle şu 20 kartı ele al. Senin erişemediğin kaynakları sonra Argon arayacak (T19).

| Neden | Kartlar |
|---|---|
| ozel_gosterge (11) | A3-002a, A3-002f, A3-002h, A3-002i, A3-010b, A6-014, M003, O1-039, O1-045, O1-050, P3-008 |
| tanim_belirsiz (9) | A2-011, O1-006, O1-008, O1-009, O1-010, O1-013, O1-055, O2-017, O2-019 |

## Kurallar (T20 ile aynı)
1. Göstergeyi `engine/gosterge.py`'ye **genel ilkel** olarak ekle. Karta özel kod yazma.
2. Kaynak Pine/Python ise birebir port et. Literal port ile karşılaştıran bir test yaz; T20'deki `williams_fractal` testi gibi.
3. Her yeni ilkel için look-ahead testi yaz: seriyi t'de kesince t'ye kadarki değerler değişmemeli.
4. Parametreleri kaynaktan al, tahmin yok. Kaynağa erişemezsen kart olduğu gibi kalır. `belirsiz`e `T21: kaynak erisilemedi (<url>) -> Argon T19` yaz.
5. Taşınan kartlarda `ozel_kod: false` olmalı, `python -m engine.spec --kontrol docs/spec/` hatasız geçmeli ve INDEKS kartlardan yeniden üretilmeli.

## Lider kararları (T20 PR notlarına)
- **A3-002e (ABSAR):** Karta özel port **şimdilik yapılmıyor**; kart `ozel_kod` olarak kalıyor. Gerekçe: ZigZag + ABC durum makinesi genel bir ilkele inmiyor. Tek kart için motor riskine değmez.
- **A4-006:** Nedeni `portfoy_rotasyonu`; Codex'in seans/rotasyon paketine taşındı.
- **R07 (VOLTRAN):** `bias_varsayim` kullanıcı onayı bekliyor. Şimdilik ertelendi.

Teslim: Tek PR (base `main`); push'tan sonra PR'ı sen aç. PR gövdesinde taşınan kartlar ile Argon'a kalan kartların URL listesi ayrı ayrı yer alsın.
