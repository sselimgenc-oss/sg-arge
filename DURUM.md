# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-28, lider (Claude).

## Şu an
**Kullanıcı kararı 2026-10-28: proje yeniden açıldı (sg-arge + sg-pano), lider Claude. Yeni yol: D** —
geçmiş kapı ön eleme olur, trader'ı ileriye dönük gölge ölçümü seçer (kohort ↔ rastgele kontrol, sürekli keşif).
Görev: `docs/GOREV_D_YOLU.md`. Aşağıdaki "Trader seçimi" adımı bu belgeyle değişti; 9 adreslik ön izleme listesi
"elle liste" kolu olarak kalır.

**Sıradaki iş: Faz 0** — `claude/kapi-v1-1` dalını (`defter.py`, altın örnekler, akıl sağlığı kapısı) gözden geçirip `main`'e
almak. Açık PR yok; hesap sürümü d ile final hızlı koşu veri dalında yok (son: c).
Kararlar K1–K11: lider önerileri onaylandı (`docs/KARARLAR_D.md`, ön kayıt `docs/ONKAYIT_D.md`).

**Ekip (kullanıcı kararı 2026-10-28):** Claude = lider, denetçi, kalite; yalnız yönetir, kod yazmaz, haftalık kullanım sınırını
gözetir. İşçiler: **Sonnet** (ayrı Claude Pro hesabı), **Codex**, **Argon** (Gemini; GitHub'a bağlanamaz — görevi kullanıcı elle
verir, çıktıyı elle getirir; lider `arastirma/`'ya koyar).

| Faz | Kim | Görev | Durum |
|---|---|---|---|
| 0 kapı v1.1 → main + tam koşu | lider | #309 birleşti; hızlı koşu 24 akıl sağlığı kapısında durdu (`binance_payi` boş) | engel |
| 0b kapı düzeltmesi | Sonnet | `docs/GOREV_KAPI_DUZELTME.md` | verilecek (kullanıcı) |
| A arşiv + tarama altyapısı | Codex | `docs/GOREV_ARSIV.md` | R2 kurulumunu bekliyor (kullanıcı) |
| altyapı sınırları araştırması | Argon | `docs/GOREV_ARGON_ALTYAPI.md` | verilecek (kullanıcı elle) |
| 2–3 gölge motoru + geçmiş prova | Sonnet | `docs/GOREV_GOLGE.md` | 0b ve tam koşu bitince |
| ofis görünümü (sg-pano, örnek veri) | atanacak | `docs/GOREV_OFIS_TASARIM.md` | verilecek (kullanıcı) |

## Geçmiş (2026-10-27)
**Kullanıcı kararı 2026-10-27: proje copy trade'e geçti.** Strateji araştırması kapandı ve silindi: strateji kodları,
TV-2/U7 koşucuları, motor, paper kitapları ve iş akışı, sonuçlar, veri, strateji belgeleri. Geçmiş git tarihçesinde
durur (son strateji hâli: `faz1-son` dalı ve bu temizlikten önceki `main`).

**Neden:** plasebo pilotu eski kapının rastgele stratejilerin %67'sini (TV-2) / %99,6'sını (U7) geçirdiğini gösterdi;
paper'daki 13 kitaptan yalnız 2'sinde zayıf alfa izi vardı (`docs/kapi_kontrol.md`). Makine öğrenmesi ve radar da yok.

**Kalanlar:**
- `copytrade/`: Hyperliquid tarama, ölçütler, kurallar, izleme kaydı, sanal kopya (`docs/GOREV_COPYTRADE_TARAMA.md`).
  İş akışı `copytrade.yml`: günlük zamanlama kapalı, `workflow_dispatch` ile; veri `copytrade-veri` dalına.
- `kapi/istatistik.py`: plasebo, maruziyet eşleşmiş NW alfa, DSR, N_eff. Kapı ilkeleri `docs/KAPI_V3.md`; copy trade
  kapısına uyarlanacak.
- `pano/`: sağlık ölçümleri (blok bootstrap konisi, CUSUM, ışıklar) ve koç kuralları (`docs/GOREV_FAZ2_PANO.md`).
  Copy trade yönetim panosuna çevrilecek; `pano/saglik.py`'deki strateji sonuçlarını okuyan yardımcılar o işte temizlenir.
  Arayüz ayrı repoda: `sg-pano` (GitHub Pages).

## SIRA (kullanıcı kararı 2026-10-27: kaos yok — bir adım bitmeden sıradakine geçilmez; her ajan tek iş)
**1. Pano — BİTTİ (2026-10-27):** sg-pano gerçek veriyi gösteriyor (sg-pano #9; motor sg-arge #277).
| Kim | İş | Durum |
|---|---|---|
| Codex | İzleme motoru (#277) + Telegram Worker (#283) | bitti |
| Sonnet | sg-pano: v1.1 + mobil (#6, #7), paper kaldırıldı (#8), canlı veri (#9) | bitti |
| Argon | Telegram ön araştırması (`arastirma/copytrade/argon_worker_teknik.md`) | bitti; sırası gelene kadar boşta |
| Lider | denetim, birleştirme | bitti |
Test listesi: `copytrade/izleme_listesi.yaml` (2 test trader'ı; kopyalama kararı değil).

**2. Telegram — BİTTİ (2026-10-27):** Cloudflare Worker `sg-arge-telegram` yayında (sg-arge #283–#286): 5 dk'da bir
bildirim, [Açtım]/[Atladım], `/durum`. Kararlar saatlik işle `copytrade-izleme/izleme/kararlar.jsonl`'a (`KARAR_URL`).
Açık kontrol: ilk gerçek bildirimde düğme → karar → panoya akış uçtan uca izlenecek. Not: saatlik zamanlama ilk
saatlerde tetiklenmedi (GitHub gecikmesi); düzelmezse incelenecek.

**3. Trader seçimi — ŞU AN:** görev `docs/GOREV_TRADER_SECIMI.md` (**Sonnet**, dal `claude/kapi-v1-1`; kullanıcı kararı).
Kullanıcı kararları (2026-10-27, Sol 6.1 görüşüyle): iki tarz — **Intraday** (medyan tutma 1–24 sa, 30 dk gecikme
testi) ve **Swing** (≥24 sa, 2 sa gecikme testi); iki katman — `izleme_adayi` (adım 1–3) / `kopyalanabilir` (1–7);
alfa kıyası kripto→BTC, hisse/emtia→kendi sepeti; pano **Keşif** sekmesi (sonra, **Codex**, sg-pano); Telegram her dakika.
Teşhis: plasebo tüm coinlerde çakışmasız yerleştirme istediği için hiç hesaplanamadı → coin başına.
Sonra: lider adayları inceler, izleme listesi kullanıcı onayıyla; 3 ay sanal izleme.

**Sol 6.1 denetimi (2026-10-27):** 3 aylık ölçüm henüz başlamaz. Kapı/ölçü düzeltmeleri Sonnet
(`GOREV_TRADER_SECIMI.md` 19–26), izleme+Worker düzeltmeleri Codex (`GOREV_IZLEME_DUZELTME.md`), kabul kanıtı kuralı
`AGENTS.md`. Ayrıntı `docs/DENETIM_2026-10-27.md`.

**Telegram v2 (sonra):** bildirimde trader girişine göre fiyat kayması ve tolerans aşılınca "atla"; spread; HIP-3
için "dayanak piyasa kapalı" uyarısı (Sol 6.1 önerisi).

**Sonraya notlar:** Telegram mini uygulama; HIP-3 hafta sonu boşluğu uyarısı; mali müşavir soru listesi
(`arastirma/copytrade/argon_kalicilik_cloudflare_turkiye.md`); gerçek para yok (en erken sanal izleme + ölçütler sonrası).

## Değişmez kurallar
`AGENTS.md`. Repo herkese açık: anahtar ve kişisel veri yok. Gerçek para ve emir yok. `main`'e PR ile; lider birleştirir.
Para, hesap, eşik ve repo silme kararları kullanıcının.
