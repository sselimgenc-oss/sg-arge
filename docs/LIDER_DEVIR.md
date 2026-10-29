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
