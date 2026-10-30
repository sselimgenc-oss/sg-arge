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
Lisans (`#439`, sg-pano `#46`), Sol'un denetim raporu (`#442`) ve veri hattı sağlığı (`#441`) birleşti. `#441`
Sol'un iki YÜKSEK bulgusuna göre düzeltilmişti (alan adı pozisyon yaşı oldu, yanlış tazelik kontrolü çıkarıldı).
Pano temizliği Opus'ta; bu dal (sg-arge) E1-E6'ya devam ediyor.

## E1 devamı (2026-10-30 akşam): gerçek algılama gecikmesi
`#445`: Worker'ın zaten çektiği dolumlardan **gerçek** algılama gecikmesi (Hyperliquid dolum zamanı → Worker'ın
görmesi) ölçülüyor (`son_gecikme` D1 tablosu, `GET /gecikme`, `copytrade/gecikme.py` → `izleme/gecikme.json`).
`#441`'deki pozisyon yaşından (tahmini) tamamen ayrı, gerçek ölçüm.
- **D1 şeması**: `worker.yml` her dağıtımda otomatik uyguluyor — önceki not ("bir kez elle uygulanmalı") yanlıştı,
  düzeltildi. Canlı kontrol: `https://sg-arge-telegram.sselimgenc-c18.workers.dev/gecikme` çalışıyor, gerçek veri
  dönüyor (2026-10-30 ~16:40 TR: medyan ≈ 0,31 dk, maks ≈ 0,52 dk — 2 örnek).
- **Kullanıcıdan gereken tek adım:** GitHub reponun Settings → Secrets and variables → Actions → Variables'a
  `GECIKME_URL` = `https://sg-arge-telegram.sselimgenc-c18.workers.dev/gecikme` eklemek (büyük olasılıkla
  `KARAR_URL`'in yanına, aynı yöntemle). Eklenmezse saatlik iş adımı sessizce atlanır, hiçbir şey bozulmaz.
- Sol'un 2. denetimindeki (`docs/DENETIM_ETRE_GECIS_TEKRAR_2026-10-30.md`) YÜKSEK bulgusu — eski/eylemsiz
  trader'ın tek D1 örneğinin oda medyanını bozması — `copytrade/gecikme.py`'de pencere filtresiyle (120 dk)
  düzeltildi (`#447`, birleşti).

## E2 (2026-10-30 gece): kopya hesabı v2 — tek motor, tasfiye, pozisyon tavanı
Canlı `sanal_kopya` (v1) `defter.copy_ledger`'ı çıplak çağırıyordu; araştırma gölgesindeki (`golge.py`) tasfiye ve
pozisyon tavanı mantığı canlıya bağlı değildi (K3/K5/K6, `DENETIM_TRADER_2026-10-30.md`). `copytrade/kopya_v2.py`
(eski taslak #434'ten güncel main'e uyarlanarak) bunu düzeltiyor; `sanal_kopya_v2` v1 yanında yayımlanıyor, v1
değişmedi. **Gerçek veri (canlı HL, O01):** v1 getiri +%7,18 ↔ v2 +%0,95 — fark açıklanabilir: O01'in gerçek açık
pozisyonu hesabın %163'ü notional (HL'den doğrulandı), v1 kapsız kopyalıyor, v2'nin pozisyon tavanı (3,0x) kırpıyor.
8 altın örnek testi; `python -m pytest -q` 535 geçti. Kapsam dışı (E3): sabit $ tutar, aşamalı zarar_kes/kar_al.
