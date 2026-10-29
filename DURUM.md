# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-29, lider (Claude).

## Şu an (2026-10-29): canlı gölge pilotu başladı

**K‑8 (kullanıcı, 2026-10-30):** izleme 61 → 91 (havuzdan 30 sessiz `havuz` trader'ı, t0 30.10); koşu süresi iyiyse havuzun tamamı. Canlı oda: ileri veriyle eleme + kapı puanıyla sıralama.

**Kalite kuralları (kullanıcı, 2026-10-30):** `AGENTS.md` sonu — küçük gerçek veri denemesi, birimli veri sözleşmesi, denetimde gerçek çıktı.

**K‑7b (kullanıcı, 2026-10-30): canlı tarihi iptal, sabit süre yok; eski yöntem (pilot + önce veri) sürer. Bot görevi askıda.**
Hf2 bot biter + canlı oda seçimi; 15–28.11 canlı fiyatla gölge (≥14 gün); 29–30.11 hesap/anahtar/onay; 1.12 canlı. Faz 3 isteğe bağlı (iptal edildi 30.10).

**K‑7 (tarih K‑7b ile iptal):** canlıya geçişte güvenlik şartları geçerli (`docs/KARARLAR_D.md`).
Faz 3 süre sınırında bitemiyor, kalıcılık sonucu sayısal bozuk (madde 12–13). Sıradaki iş: `docs/GOREV_VERI_DUZELTME.md` (Sol canlı veri denetimi: olay listesi 200'de kesiliyor, kasa tablosu yanlış portföy,
kontrol 18 değil 17 sayılıyor, geçersizler toplamlara giriyor). Worker yedek tetikleme ve günlük özet devrede (TETIK_TOKEN).

**Kural (kullanıcı kararı 2026-10-29): önce veri.** Faz 4 verisi oturmadan (düzenli tetiklenen, doğru, ofis↔pano tutarlı) görünüm/tema işi
yok; yeni fikir önce `docs/FIKIRLER.md`'ye. İzometrik tema tamamen kaldırıldı (kullanıcı kararı 2026-10-30); ofis tek görünüm (klasik). Sıra: 1) Worker ile saatlik
tetikleme, 2) izleme ve pano veri doğruluğu, 3) Telegram sadeleştirme (işlem bildirimleri kapalı; günlük özet + uyarı), 4) Faz 3 ve kalıcılık sonuçları.

**Gün sonu özeti (2026-10-29 19:30 TR; limitler azaldı → yavaş tempo, yalnız önemli işler):**
- Açık sorun: 61 trader'lık izleme yayımlanamıyordu (motor.json 267 MB > 100 MB) → #414 ile R2'ye taşındı; doğrulama koşusu (run 40911015820) sürüyor.
- Koşuyor/kuyrukta: arşiv (#20), Faz 3 gerçek prova, kalıcılık testi, pilot boşluk doldur (#6). Boşluk doldur #5 yeşil.
- Bugün biten: ön kayıt 1.5 (körlük kalktı) ve 1.6 (değişim kuralları); değişim kaydı + mutabakat ışığı; referans kolu; kasa sekmesi;
  oda risk bayrakları (yönsüz, kalabalık); Faz 3 ve kalıcılık kodu (sentetik doğrulama geçti); Argon A20–A29 (denetimli).
- Sıradaki (öncelik): 1) izleme yeşil + pano 61 trader; 2) Faz 3 sonucu → kullanıcı kararı; 3) kalıcılık sonucu; 4) pano sadeleştirme (A29).

**Ön kayıt 1.6 (kullanıcı "evet"):** oda değişikliği gerekçe kodu, 28 günde en çok 2 çıkış, çıkan 56 gün izlenir. Görev: Codex `docs/GOREV_DEGISIM_VE_SAGLIK.md`. Dış görüş özeti: `arastirma/fikir_gorusleri/OZET.md`.
**Kullanıcı onayı 2026-10-29: Seçim v1.3 odası onaylandı ("onaylıyorum").** Pilot başlangıcı (t0) = 2026-10-29; analiz 12. ve
24. haftada (ön kayıt madde 6).

**Dondurma (ön kayıt madde 9):**
- Ön kayıt: `docs/ONKAYIT_D.md` sürüm 1.4, commit `c3c372a722d3dcc5d207754e4e690098ce21387c`.
- İlk v1.3 seçimi: `copytrade-kapi` dalı `secim/2026-10-29-v1.3/` (kapı 2026-10-28, tohum `secim-v1.3-2026-10-28`,
  kurallar sha256 `7624e1d96c23ad813585aeaacc97f4399c98f76c4fd4db9cbf07f662f5f1a817`,
  secim.py sha256 `578cc5aa254864ae44f2973ca4552832880ba8abed769f0053c9da1f5ae7899b`). Oda 18, kontrol 18, taban 18, ikincil 167.
- İzleme listesi `copytrade/izleme_listesi.yaml` bu seçimden üretildi (`--izleme-listesi`, 61 satır: oda 18, kontrol 18
  (`kollar`), taban 18, elle 8).
- Analiz kodu (madde 9, veri görülmeden yazıldı): `copytrade/analiz_d.py` sha256 `ffdf2bb104fcd7f9269ac005dfbf8e5776e4f1f6d97bec78b285547fe1bd2e2e`.
- Bayraklar (`bayrak.json`) bilgi amaçlı; kimse elenmedi. Dikkat: f208 (%100 tek coin), 84d7 (%90 tek coin, derin ekleme),
  86d2 (%88), 582e (%65); 50e2 vault.

**Körlük kalktı — ön kayıt 1.5 (kullanıcı kararı 2026-10-29):** pano, ofis ve Telegram kâr/zararı ve oda ↔ kontrolü her an
gösterir; oda kullanıcı kararıyla değişebilir (gerekçeli geçiş kaydı). Seçim v1.3 odası + kontrolü **sabit referans** olarak
değiştirilmeden izlenir ("Kararlarım değer kattı mı?" = yönetilen oda ↔ sabit referans). K‑6 (c) geçersiz.

**Maliyet (K‑5), kullanıcı kararı 2026-10-29 ("tamam"):** ana karar maliyeti (`maliyet_taker` + `maliyet_kayma`, tek oran)
pilot boyunca değişmez. Coin sınıfı ve saate göre maliyet yalnız bilgi amaçlı duyarlılık raporunda (`maliyet_rapor.py`); HIP‑3
büyüme/standart mod ve seans içi/dışı ayrımı eklenecek (Argon A20, `arastirma/copytrade/argon_a20_hip3_maliyet.md`).

**Açık işler (2026-10-29 akşam):** Sonnet: #393 (§5) çakışması, sonra `docs/GOREV_FAZ3.md` (geçmiş prova). Codex:
`docs/GOREV_OFIS_CANLI.md` (körlük kalktı, bütün odalar aktif, ana pano kilitleri, sabit referans kolu), sonra
`docs/GOREV_CODEX_TEMIZLIK.md` (gunluk.csv.gz, B21–B23, B29). Bitti: KORLUK (#387), PILOT_VERI (#389), Argon A20/A21 (#388),
Telegram kuruldu. Bekleyen: ilk 61 traderlı izleme koşusu, pilot boşluk doldurma (arşiv dolum yoklamasından sonra).

## Önceki (2026-10-28)
**Kullanıcı kararı 2026-10-28: proje yeniden açıldı (sg-arge + sg-pano), lider Claude. Yeni yol: D** —
geçmiş kapı ön eleme olur, trader'ı ileriye dönük gölge ölçümü seçer (kohort ↔ rastgele kontrol, sürekli keşif).
Görev: `docs/GOREV_D_YOLU.md`. Aşağıdaki "Trader seçimi" adımı bu belgeyle değişti; 9 adreslik ön izleme listesi
"elle liste" kolu olarak kalır.

**Tek odak (kullanıcı kararı 2026-10-28): trader seçimini oturtmak.** Kritik yol: kapı düzeltmesi (#317) → tam koşu →
Seçim v1 (`docs/GOREV_SECIM_V1.md`: havuz, aday, oda, kontrol) → kullanıcı oda onayı → canlı izleme (ön kayıt sürüm 1.1:
geçmiş prova paralel). Arşiv ve ofis ikinci planda.

**Ekip (kullanıcı kararı 2026-10-28):** Claude = lider, denetçi, kalite; yalnız yönetir, kod yazmaz, haftalık kullanım sınırını
gözetir. İşçiler: **Sonnet** (ayrı Claude Pro hesabı), **Codex**, **Argon** (Gemini; GitHub'a bağlanamaz — görevi kullanıcı elle
verir, çıktıyı elle getirir; lider `arastirma/`'ya koyar).

| Faz | Kim | Görev | Durum |
|---|---|---|---|
| 0 kapı v1.1 → main + tam koşu | lider | #309, #317 birleşti; hızlı koşu 25 yeşil (hesap d); tam koşu run 27 kuyrukta (2026-10-28) | sürüyor |
| 1 Seçim v1 | Sonnet | `docs/GOREV_SECIM_V1.md` (#322; kırmızı bayrak sütunları dahil) | kod hazır; tam koşu sonucunu bekliyor |
| 0b kapı düzeltmesi | Sonnet | `docs/GOREV_KAPI_DUZELTME.md` | bitti (#317) |
| A arşiv + tarama altyapısı | Codex | `docs/GOREV_ARSIV.md` | birleşti (#319, #321); ilk 24 saat kapsam kanıtı bekleniyor |
| Argon araştırmaları | Argon | altyapı sınırları, kırmızı bayrak, geçmiş leaderboard (`arastirma/copytrade/argon_*.md`) | bitti |
| 2–3 gölge motoru + geçmiş prova | Codex | `docs/GOREV_GOLGE.md` | Faz 2 #327 denetimde (V2 tamam; likidasyon, sentetik, sağlama açık); Faz 3 Faz 2'den sonra |
| ofis görünümü (sg-pano, örnek veri) | Codex + Sonnet | `docs/GOREV_OFIS_TASARIM.md` | iki taslak: sg-pano #17 (Codex), #18 (Sonnet); karşılaştırma sonra |

**Kararlar (kullanıcı, 2026-10-28):**
- V2 teminatı = trader'a ayrılan gölge sermayesinin tamamı (ön kayıt sürüm 1.2).
- Dune yok (API ücretli). Faz 3 evreni bugünkü leaderboard; sonuç "iyimser üst sınır" diye raporlanır. Arşivin haftalık
  leaderboard görüntüleri ileride gerçek geçmiş evreni verir.
- K8: şimdilik ücretsiz GitHub Actions (canlı izleme saatlik); gecikme sorun olursa yeniden açılır. Ücretli plan yok.

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

**2. Telegram — KOD HAZIR, KURULMADI (düzeltme 2026-10-29):** `worker.yml` dağıtımı GitHub Secrets eksik diye hiç
başarılı olmadı (son: 2026-10-28, "Eksik GitHub Secret: CLOUDFLARE_API_TOKEN"); beş secret kullanıcıda. Tasarım: Cloudflare Worker `sg-arge-telegram` (sg-arge #283–#286): 5 dk'da bir
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
