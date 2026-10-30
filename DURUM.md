# DURUM (lider günceller; tek doğru kaynak budur)

Son güncelleme: 2026-10-30, Claude (temizlik). Lider: Sonnet (K‑11, birleştirme yetkili).

**Kullanıcı kararı (2026-10-30 gece):** Sol (Codex) denetimi artık **manuel** — zorunlu birleştirme koşulu değil,
yalnız kullanıcı isterse ayrıca devreye girer. Birleştirme koşulu: **CI yeşil** (lider kendi birleştirir, denetim
beklemez).

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

## E3 (2026-10-30 gece): aşamalı zarar_kes/kar_al canlıya bağlandı
Kullanıcı: "sırayla yap, sormana gerek yok." `golge.py`'deki ön kayıtlı aşamalı çıkış kuralı (intraday −%50; swing
gün 0/7/14 kademeli) `kopya_v2`'ye `variant='V2'` ile bağlandı; eşikler değişmedi (zaten dondurulmuştu). Her
zorunlu çıkışın nedeni `kapanis_nedenleri`de. 9 altın örnek, `pytest -q` 536 geçti. Gerçek veride (O01) henüz
tetiklenmedi (pozisyon eşiğe değmiyor) — doğru, yanlış tetiklenme yok. **Sabit $ işlem tutarı sorulmadan
atlandı** (eşik/strateji kararı, AGENTS.md): Etre'nin eğrisi (200$→5,2$, 1.000$→20,7$, 10.000$→150$, sonrası
sabit) kesin sayı gerektiriyor, kullanıcı onayı bekliyor.

## E4 (2026-10-30 gece): zaten büyük ölçüde mevcut — yeni kod yazılmadı
İncelemede: Etre'nin "gerekçeli giriş/çıkış, bekleme süreli, değişmez olay günlüğü, odadan düşme kuralı" istekleri
K-11'den ÖNCE kurulmuş, kullanıcı onaylı (ön kayıt 1.6) `copytrade/gecis.py` + `copytrade_haftalik.yml` (her
Perşembe) tarafından zaten sağlanıyor: alt dilim + ardışık hafta çıkış kuralı, 28 günde ≤2 çıkış tavanı, değişmez
`rotasyon/kayit.jsonl` olay günlüğü. Yeni kod yazmadım (kural 7: mevcut fonksiyonu kopyalama). Gerçek veri kontrolü:
`rotasyon/kayit.jsonl` henüz yok — pilot 29.10'da başladı, ilk Perşembe koşusu henüz gerçekleşmedi (zamanlama,
hata değil). "Aday sırası" kavramı `havuz` kolu ile zaten karşılanıyor.

## E6 (2026-10-30 gece): mühendislik — mevcut durum zaten iyi
`except Exception` taraması: `copytrade/`+`worker/`'da 11 yer, hepsi `# noqa: BLE001` ile gerekçeli ve hata
sayılıp/loglanıyor (Etre'nin "128 yerde sessiz yutma" sorunu yok). Ayarlar tek dosyada (`kurallar.yaml`).

**İş akışı arşivi (kullanıcı onayı "onaylıyorum devam et" ile, 2026-10-30 gece):** 12 iş akışı incelendi (GOREV'in
andığı 17 değil; #443 temizliği zaten indirmiş). İkisi tamamlanmış tek seferlik işti, Actions geçmişinden
doğrulanıp kaldırıldı (git geçmişinde duruyor):
- `hf_dogrulama.yml` — HF geçmiş veri doğrulaması (`docs/GOREV_HF_DOGRULAMA.md`), son koşu (28.10) başarılı, görev bitti.
- `pilot_bosluk.yml` — dosyasında "TEK SEFER, elle" yazıyordu; son koşu (29.10 16:03) başarılı, boşluk dolduruldu.

Dokunulmayanlar (hâlâ kullanılan, yeniden kullanılabilir araçlar): `golge_saglama.yml` (manuel `golge.py` sağlık
kontrolü), `izleme_deneme.yml` (kural 1'in gerektirdiği "küçük gerçek veri denemesi" aracı — zorunlu, silinmez).
İş akışı sayısı 12 → 10.
