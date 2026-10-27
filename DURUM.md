# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-27, lider.

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

## Sıradaki iş
**Copy trade fazları ve yeni plan** (kullanıcıyla birlikte çizilecek; gerçek para yok, hemen başlanmıyor).
Taslak başlıklar: veri ve copy trade kapısı → sanal kopya + pano → karar ve pilot hazırlığı (mali müşavir görüşü) →
küçük canlı pilot. Eşikler kullanıcı onayıyla dondurulur.

## Değişmez kurallar
`AGENTS.md`. Repo herkese açık: anahtar ve kişisel veri yok. Gerçek para ve emir yok. `main`'e PR ile; lider birleştirir.
Para, hesap, eşik ve repo silme kararları kullanıcının.
