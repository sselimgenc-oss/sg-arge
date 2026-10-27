# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-27 akşam, lider.

## Şu an
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

**3. Trader seçimi — ŞU AN:** görev `docs/GOREV_TRADER_SECIMI.md` (Codex, dal `codex/kapi-v1-1`). Teşhis: adım 3+4'ü
9 adres geçti; plasebo tüm coinlerde çakışmasız yerleştirme istediği için hepsinde hesaplanamadı (tasarım hatası).
Eski not: CT-Kapı tam sonucu incelenir (`copytrade/kapi/2026-10-27/`). Bilinen
sorunlar: 12.461 adresin 8.196'sı işlendi; adım 5 plasebo hiçbir adreste hesaplanmadı (p boş) → düzeltilecek.
"İlişkili hesaplar" kontrolü eklenecek (alt hesap, vault, iç transfer, ortak agent — Argon notu). Sonra gerçek
izleme listesi ve 3 aylık sanal izleme.

**Sonraya notlar:** Telegram mini uygulama; HIP-3 hafta sonu boşluğu uyarısı; mali müşavir soru listesi
(`arastirma/copytrade/argon_kalicilik_cloudflare_turkiye.md`); gerçek para yok (en erken sanal izleme + ölçütler sonrası).

## Değişmez kurallar
`AGENTS.md`. Repo herkese açık: anahtar ve kişisel veri yok. Gerçek para ve emir yok. `main`'e PR ile; lider birleştirir.
Para, hesap, eşik ve repo silme kararları kullanıcının.
