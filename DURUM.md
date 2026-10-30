# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-30, Claude (temizlik). Lider: Sonnet (K‑11, birleştirme yetkili). Denetçi: Codex (Sol).

## Hedef (K‑11)
Hyperliquid kaldıraç trader'larını sanal kasada, küçük sabit tutarla, Etre'nin çıkış kurallarıyla kopyalayan; tek panelde ve
Telegram'da canlı izlenen; her kuralı ileri testle ölçen sistem. Gerçek para/emir yok. Görev: `docs/GOREV_ETRE_GECIS.md` (E1–E6).

## Şu an çalışan (yeni sistem canlıya geçene kadar kalır)
- `izleme.yml` saatlik izleme (Worker tetikler, `TETIK_TOKEN`) → `copytrade-izleme` veri dalı (`izleme/durum.json`), motor durumu R2.
- `arsiv.yml` dolum arşivi (R2), `arsiv_alarm.yml`; `copytrade_kapi.yml` / `copytrade_secim.yml` seçim (v1.3); `copytrade_haftalik.yml` ön kayıt raporu.
- Worker: günlük özet 09:00 TR + alarm (işlem bildirimleri kapalı). Pano/ofis: `sg-pano`.

## Belgeler
`AGENTS.md` (kurallar) · `docs/KARARLAR_D.md` (kullanıcı kararları) · `docs/ONKAYIT_D.md` (ön kayıt) · `docs/VERI_SOZLESMESI.md` ·
`docs/GOREV_ETRE_GECIS.md` (tek görev listesi) · seçim yöntemi: `docs/GOREV_TRADER_SECIMI.md`, `docs/KAPI_V3.md`, `docs/GOREV_SECIM_V1.md`, `docs/GOREV_SECIM_V13.md` ·
`docs/WORKER_TETIKLEME.md` · `docs/etre_envanter.md` · `docs/DENETIM_TRADER_2026-10-30.md` · `docs/LIDER_DEVIR.md` · `docs/PROTOKOL.md`.

## Temizlik (kullanıcı kararı 2026-10-30: "yeni stratejide işe yaramayan her şey silinsin")
Silindi (git geçmişinde duruyor): Faz 3, kalıcılık, inceleme, maliyet/makas, mutabakat, rejim, kapı satır teşhisi modülleri ve iş akışları;
eski aday taraması; biten/askıdaki görev ve durum belgeleri (`GOREV_*`, `codex_*`, eski denetimler, fikirler); `arastirma/` (yalnız kapının okuduğu
`arastirma/copytrade/bagimsiz_secim` kaldı); eski kapı anlık görüntüsü. Eski dallar ve çalıştırmalar da temizlendi.

## E1 (2026-10-30 akşam, lider Sonnet)
Lisans (`#439`, sg-pano `#46`) ve Sol'un denetim raporu (`#442`) birleşti. `#441` (veri hattı sağlığı) Sol'un iki
YÜKSEK bulgusuna göre düzeltildi (alan adı pozisyon yaşı oldu, yanlış tazelik kontrolü çıkarıldı) — yeniden
denetim bekliyor. Pano temizliği Opus'ta; bu dal (sg-arge) E1-E6'ya devam ediyor.

## E1 devamı (2026-10-30 akşam): gerçek algılama gecikmesi
Yeni dal `claude/e1-gercek-gecikme`: Worker'ın zaten çektiği dolumlardan **gerçek** algılama gecikmesi (Hyperliquid
dolum zamanı → Worker'ın görmesi) ölçülüyor (`son_gecikme` D1 tablosu, `GET /gecikme`, `copytrade/gecikme.py` →
`izleme/gecikme.json`). `#441`'deki pozisyon yaşından (tahmini) tamamen ayrı, gerçek ölçüm. Dağıtım: D1'e
`son_gecikme` tablosu bir kez uygulanmalı, `GECIKME_URL` Actions değişkeni tanımlanmalı (yoksa adım atlanır).
