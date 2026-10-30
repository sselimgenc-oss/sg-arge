# Lider devri — Sonnet ortak lider (2026-10-30 → 2026-11-02 Pazartesi), lider Claude (Opus) limitte

Okuma sırası: bu dosya → `DURUM.md` ("Şu an") → `AGENTS.md` (kurallar + **kalite kuralları**) → `docs/KARARLAR_D.md` (K‑5…K‑8) →
`docs/GOREV_VERI_DUZELTME.md`. Kullanıcı Türkçe, telefondan, teknik değil: kısa, sade, adım adım; TR saati (UTC+3).

## Yetki
- Sonnet bu süre için **ortak lider**: görev yazma, PR açma, sg-arge ve sg-pano PR'larını **denetleyip birleştirme** dahil.
- **Kullanıcıya sorulmadan yapılmaz:** para/hesap/anahtar, `kurallar.yaml` eşik değişikliği, ön kayıt (`docs/ONKAYIT_D.md`) değişikliği,
  oda/kontrol üyeliği değişikliği, repo/dal silme, gerçek emir (yasak: `AGENTS.md`, K‑7b; bot görevi askıda).
- Denetim: **Codex (Sol) bağımsız denetçi.** Senin yazdığın kodu Codex denetler (kalite kuralı 3: gerçek çıktıya bakılır).

## Durum (30.10 sabah)
- Pilot: 91 trader izleniyor (oda 18, kontrol 18 [E01 `kollar`'da], taban 18, elle 8, **havuz 30** — K‑8, t0 30.10, sessiz).
- Veri akışı: Cloudflare Worker her dakika bakar, `izleme.yml` (75 dk eşik) ve `arsiv.yml`'i (20 dk) workflow_dispatch ile tetikler
  (secret `TETIK_TOKEN`); son BİTEN koşuya bakar. Telegram: işlem mesajları kapalı (`BILDIRIM_KIPI=ozet`), 09:00 TR günlük özet,
  veri > 3 sa / kalabalık uyarısı. `motor.json` R2'de (`izleme/motor.json.gz`), veri dalında değil.
- Arşiv (`arsiv.yml`) günlük boşluk eşiğinde **bilerek kırmızı** biter ama veriyi R2'ye yazar — hata değil.
- İlk 91'lik izleme koşusu uzun (30 yeni trader 90 günlük geçmiş indirir). Bittiğinde: süre (motor adımı) ve 30 havuz trader'ının
  `gecerli` sayısı → makulse havuzun tamamı (`python -m copytrade.secim --izleme-listesi --secim <secim.json> --havuz-adet 154`,
  sonra izleme süresine bak; 150 dk iş sınırı).
- Faz 3: iptal edildi (süre sınırında bitemiyor) — isteğe bağlı, madde 12. Kalıcılık: sonucu sayısal bozuk — madde 13 (öncelikli).
- İzometrik tema tamamen kaldırıldı. Ofis tek görünüm (klasik). Telefonda menü → alttan bilgi paneli (sg-pano #43).

## Öncelik (Pazartesiye kadar; "önce veri" kuralı)
1. `docs/GOREV_VERI_DUZELTME.md` madde 1–11 (olay arşivi kesilmesi, tek fiyat eksiği, perp hesabı sıfır, geçersizlerin toplamlara
   girmesi, zaman damgası, sanal lot şeffaflığı/O10 negatif bakiye, mutabakat ikiye ayırma; pano: kasa tablosu sanal lotlardan,
   `kollar` üyeliği, son kapananlar, kapsam etiketleri). Her madde test + **küçük gerçek veri denemesi** (kural 1).
2. Madde 13 kalıcılık düzeltmesi → `kalicilik.yml` yeniden koşu → sade özet kullanıcıya.
3. Codex'in pano/ofis denetim bulguları (kullanıcı ayrı istedi) → düzelt.
4. Madde 14 kararsız test. Madde 12 (Faz 3) yalnız zaman kalırsa: önbellek → ön eleme → örneklem; önce 1 pencere × 50 hesap.

## Dikkat (ilk iki günün dersleri)
- Birimler: `sanal_kopya.getiri` **oran** (0,012 = %1,2); kaldıraç "x"; `hesap_degeri` trader hesabı $; sanal kopya 1.000 $ ölçeği;
  kol üyeliği için `kollar` (ana etiket `kol`). `uretildi` koşu başlangıcıdır.
- GitHub secret adı `GITHUB_` ile başlayamaz. Veri dalında dosya ≤ 90 MB. Bu ortamdan Hyperliquid API'ye erişim olmayabilir
  (proxy 403): deneme koşusunu Actions'ta küçük girdiyle yap.
- Her PR sonunda kullanıcıya 3 satır sade özet. Birleştirdiğin her şeyi `DURUM.md` "Şu an"a tek satırla yaz.
- Pazartesi: lider Claude döner; bu dosyanın sonuna "Devir notu" ekle (yapılan, açık kalan, kullanıcının kararını bekleyen).

## Devir notu (Sonnet doldurur)

**Yetki Opus'a (lider Claude) geri devredildi (kullanıcı, 2026-10-30). Sonnet durdu; yeni iş başlatmıyor.**

**Yapılan (hepsi `claude/zen-heisenberg-lx1ond` dalında, taslak PR sg-arge#434; hiçbiri `main`'de değil, Sonnet hiçbir şeyi birleştirmedi)**
- `GOREV_VERI_DUZELTME.md` 1–7 ve 13–25 (sg-arge motor/Worker): olay arşivi (kol başına 200 + saatlik değişmez parça), fiyatsız eylem, `veri_durumu`/`kapsam`, zaman alanları,
  `sayac_24s`, eğri=kasa, eksik değerleme, sanal lotlar, mutabakat ikiye ayrıldı, Worker (özet telafisi, `saglik_kayit`, `/kararlar` anahtarı), kopya hesap v2
  (`copytrade/kopya_v2.py`; `golge.calistir` tek motor, tasfiye, zamanla değişen payda, funding), `gecikme5`, `risk` tanısı, kalıcılık asgari payda + önbellek kimliği (kararsız test).
- K-10 S1'in sg-arge tarafı: `durum.json` `kol_ozet`; Worker günlük özeti yalnız onu okur. Veri sözleşmesi (`docs/VERI_SOZLESMESI.md`) güncel.
- Testler: `python -m pytest -q` 599 geçti; `cd worker && node --test` 37 geçti.
- Küçük gerçek veri: koşu 40986309943 (B17,O01,O02; kod madde 1–5/15–19 sürümü) okundu ve PR yorumuna yazıldı. Koşu 41069756677 (güncel baş, B17,O01,O02,O10) başlatıldı; **çıktısı okunmadı**.
- sg-arge#436: `.claude/settings.json` ile `add_repo` izni (kullanıcı onaylı); birleşmedi.

**Açık kalan**
- Koşu 41069756677 çıktısını oku (v2, O10 v2 değeri, `gecikme5`, `risk`, `acik_lotlar`, `mutabakat_sanal`, `kol_ozet`, motor süresi) ve #434'e ekle; sonra taslaktan çıkar. 91 trader'lık koşu süresine v2 saatlik mum okumasının etkisi ölçülmedi.
- S1'in pano/ofis kısmı (`sg-pano`: `kasaToplam`/ortalama/24 saat, ofis `gercek.js`, teminat) yapılmadı; `sg-pano` oturuma eklenemedi. Ofis teminat tanımı bilinmiyor; `kol_ozet`te `teminat` yok. Madde 8–11 (pano) ve 16/18'in ekran tarafı da bu repoda.
- S2 (canlı `copy_results` v1'in kaldırılması; şimdilik v1 ve v2 yan yana), S3 (tek veri kaynağı), S4 (`copytrade/sema_durum.json` şema testi), S5 (belge/ölü kod arşivi) başlamadı.
- Kalıcılık yeniden koşusu (`kalicilik.yml`) yapılmadı; #434 birleşince tetiklenmeli.
- Kural 4'e göre 15–23 bitene kadar yeni özellik yok; `gecikme5` (24) ve `risk` (25) Ek 2'de yazılı olduğu için erken yapıldı (sıra ihlali, bilgi için).

**Kullanıcının kararını bekleyen**
- Risk tavanı değerleri (`oda_brut_kaldirac_tavani`, `oda_tek_coin_payi_tavani`); yazılana kadar `risk` yalnız ölçer, uyarı üretmez.
- Madde 25 "eksik veri >%5 → `sinanamadi`": karar fonksiyonu dondurulmuş `analiz_d.py` (ön kayıt sha); değiştirmek kullanıcı kararı. **Yapılmadı.**
- Cloudflare D1'e `worker/schema.sql`daki `saglik_kayit` tablosunun uygulanması; isteğe bağlı `KARAR_ANAHTARI` secret'ı (Cloudflare + GitHub).
- #436'nın birleştirilmesi (sg-pano erişimi için; yeni oturumda etkili).
- `docs/arsiv/`'e taşıma (S5) kullanıcı onayıyla.

**Dikkat (denetçiye)**
- Değiştirdiğim mevcut testler (PR #434 açıklamasında listeli): `test_failure_preserves_last_successful_payloads` (hata başka yoldan), karşılaştırma testlerinde koşuyla ilerleyen alanlar dışarıda,
  `test_kalicilik.py` elle hesaplı örnekler `hesap_degeri_min_usd: 0` ile (taban yeni testlerle ayrıca), deneme defteri testi 4 önkayıt bekliyor.
- Kural 6 gereği PR'da eski ↔ yeni (oda, kontrol, O10) yan yana tablo henüz yok; deneme çıktısı okununca eklenmeli.
- Geriye dönük uyum: `gecerli`, `veri_kalitesi.mutabakat` (= `mutabakat_gecmis`), `olaylar` listesi duruyor; pano bunlara dokunmadan çalışmalı.

