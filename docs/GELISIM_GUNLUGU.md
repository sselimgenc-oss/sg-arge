# Gelişim günlüğü — sg-arge (Etre biçimi: tarih-saat, ne değişti, hangi ölçümü etkiledi, test sayısı)

Kronolojik, en yeni üstte. İkinci doğru kaynak değil: kararların ayrıntısı `DURUM.md`, `docs/KARARLAR_D.md` ve
görev belgelerinde durur; burada yalnız hangi değişikliğin hangi ölçümü/veriyi etkilediği kısaca kayıtlıdır.

## 2026-10-30 21:00 TR — E4/E6 incelemesi: yeni kod yok (kural 7 — mevcut fonksiyonu kopyalama)
- **Yönetim kararı:** Sol (Codex) denetimi manuel oldu (kullanıcı); birleştirme koşulu artık yalnız CI yeşil.
- **E4 (oda yönetimi):** Etre'nin istediği gerekçeli giriş/çıkış + bekleme süresi + değişmez olay günlüğü +
  odadan düşme kuralı K-11'den önce kurulmuş: `copytrade/gecis.py` (alt dilim + ardışık hafta çıkış, 28 günde
  ≤2 çıkış tavanı) + `copytrade_haftalik.yml` (her Perşembe, ön kayıt 1.6 onaylı). Yeni kod yazmadım. Gerçek veri
  kontrolü: `rotasyon/kayit.jsonl` henüz yok (pilot 29.10 başladı, ilk Perşembe koşusu gelmedi — zamanlama).
- **E6 (mühendislik):** `except Exception` taraması — 11 yer, hepsi gerekçeli ve loglanıyor (Etre'nin sorunu yok).
  İş akışı sayısı 12 (#443 zaten indirmiş). Ayarlar tek dosyada. Kullanılmayan iş akışı arşivi kullanıcı onayı
  gerektiriyor, ayrı soru.
- E5 (pano/ofis) kapsam dışı — bu oturumun işi değil (sg-pano, kullanıcı kararıyla ayrı atandı).

## 2026-10-30 20:45 TR — E3: aşamalı zarar_kes/kar_al canlıya bağlandı
- Kullanıcı kararı: "Opus sana ne değişiklik verdiyse sırayla yap, sormana gerek yok" — E2'nin kalan parçası
  (sabit $ işlem tutarı) eşik/strateji kararı gerektirdiği için (AGENTS.md: eşik kararı kullanıcının) atlanıp
  E3'e geçildi: `golge.py`'de zaten yazılı, ön kayıtlı aşamalı çıkış kuralı (`v2_sinir`) canlıya hiç bağlı değildi.
- `copytrade/kopya_v2.py`: `golge.calistir(..., variant='V0')` → `variant='V2'` — tek satır, ama motoru Etre'nin
  kurallar.py'sindeki zamana bağlı stop/kâr mantığına denk hâle getiriyor (eşikler DEĞİŞMEDİ, zaten dondurulmuştu).
  Her zorunlu çıkışın nedeni+coin'i yeni `kapanis_nedenleri` alanında (Etre'nin "her kapanışta neden kaydı" isteği).
- Test: `tests/test_kopya_v2.py`'deki "tasfiye olmayan derin zarar" testi V2 altında artık erken zarar_kes'e
  giriyor (eşik -%50) — elle yeniden hesaplanıp güncellendi (bakiye 196,96 $, kapanış nedeni kaydı doğrulandı);
  eşiğe değmeyen bir senaryo için yeni ayrı test eklendi. 9 altın örnek, `pytest -q` 536 geçti.
- Küçük gerçek veri denemesi (canlı HL, O01, 7,5 sn): `kapanis_nedenleri: []` — mevcut pozisyon eşiğe değmiyor,
  yanlışlıkla tetiklenmedi (gerçek veriyle doğrulandı).
- Kapsam dışı (ayrı iş, kullanıcıya sorulacak): sabit $ işlem tutarı — Etre'nin tam eğrisi (200$→5,2$, 1.000$→20,7$,
  10.000$→150$, sonrası sabit) belgelerden yaklaşık çıkarılabilir ama kesin sayılar strateji/eşik kararı.

## 2026-10-30 20:15 TR — E2: kopya hesabı v2 (tek motor, tasfiye, pozisyon tavanı, doğru payda/funding)
- `copytrade/kopya_v2.py` (yeni): canlı `sanal_kopya` (v1, `izleme_motoru.copy_results`) `defter.copy_ledger`'ı
  çıplak çağırıyordu — araştırma gölgesinde (`golge.py`) zaten var olan tasfiye/pozisyon tavanı mantığı canlıya
  hiç bağlı değildi (DENETIM_TRADER_2026-10-30.md K3/K5/K6). v2 aynı motoru (`golge.calistir`, V0) kullanır: eski
  taslak PR #434'ten (birleştirilmeyecek) `sanal_kopya_v2` bölümü güncel main'e yeniden uyarlanıp getirildi.
- İki küçük destek düzeltmesi (tek motor çalışabilsin diye): `defter.Market.funding_cum` artık yalnız tam saatlik
  mumları funding ızgarasına alıyor (1 dk işaret mumu karışınca fazladan/eksik funding sayma riski); `golge.v2_cikislari`
  dolum üzerindeki hazır `_execution_*` alanını (v1'in zaten çektiği gecikmeli dakika mumu) kullanıyor.
- `izleme_motoru.update_trader()`: `sanal_kopya_v2` v1 yanında yazılıyor; hata olursa yalnız v2 `{"durum":"hesaplanamadi"}`
  döner, v1 düşmez (try/except, kural 6).
- **Küçük gerçek veri denemesi** (canlı Hyperliquid, tek gerçek oda trader'ı O01, 8 sn): v1 getiri **+%7,18**, v2
  getiri **+%0,95**. **Açıklanan fark:** O01'in gerçek açık pozisyonu (NEAR, 10x, hesabın %163'ü notional — HL'den
  doğrulandı) v1'de kapsız kopyalanıyor, v2'nin pozisyon tavanı (`golge_pozisyon_tavan_carpani`=3,0) bunu kırpıyor;
  tasfiye tetiklenmedi (`tasfiye=false`). Bu v2'nin **doğru çalıştığının** kanıtı, hata değil.
- Test: `tests/test_kopya_v2.py` 8 altın örnek (tek motor=v1 eşitliği, tasfiye, tasfiye olmayan derin zarar, zamanla
  değişen payda, yalnız kopyalanan pozisyonun funding'i, dakika mumu funding ızgarasına girmez, eksik hesap serisi,
  boş hesap). `tests/test_izleme.py` 2 küçük güncelleme (v2'nin koşuyla ilerleyen alanları karşılaştırma dışı;
  v2'nin kendi saatlik mum önbelleği ayrı sayaçla +1/koşu — regresyon değil, yeni, beklenen davranış).
- `python -m pytest -q`: 535 geçti. `docs/VERI_SOZLESMESI.md` v1.9: `sanal_kopya_v2` şeması belgelendi.
- **Kapsam dışı (ayrı iş, E3):** Etre'nin sabit $ işlem tutarı (hâlâ trader hesabına oranlı ölçek) ve aşamalı
  zarar_kes/kar_al çıkışları — `golge.calistir` bunları bilerek `variant='V0'` ile uygulamıyor.

## 2026-10-30 19:45 TR — Sol'un 2. denetimi (%33): #445'teki gerçek bulgu düzeltildi, canlı kanıt eklendi
- `docs/DENETIM_ETRE_GECIS_TEKRAR_2026-10-30.md` (#446): ilerleme puanı 4/12 (%33) — bu, 12 geniş Etre alanının
  kaba oranı, "bugünün işi eksik" anlamına gelmez; E2–E5 (kopya motoru, risk kuralları, oda yönetimi, pano) henüz
  başlamadı, sıradaki iş zaten bu. Rapordaki iki gerçek hata:
  1. **Önceki düzeltme:** "dakikalık Worker yoklaması yok" bulgusu rapor yazarının kendi hatasıydı — Worker
     zaten her dakika çalışıyor (`wrangler.toml` `crons`); "hız" alanı KISMİ'ye düzeltildi.
  2. **YÜKSEK, gerçek:** `son_gecikme` D1'de trader başına tek satır kalıcı olduğundan, uzun süre işlem yapmayan
     bir trader'ın eski örneği oda medyanına filtresiz giriyordu. `copytrade/gecikme.py::ozet()` artık `zaman`'ı
     120 dk'dan eski örnekleri medyandan/maks'tan dışlıyor (`n` taze, `n_toplam` hepsi) — `claude/e1-gecikme-pencere`.
- **Canlı kanıt (denetimin istediği, önceden eksikti):** Worker'ın gerçek adresi bulundu (deploy log'undan):
  `https://sg-arge-telegram.sselimgenc-c18.workers.dev`. `/gecikme` canlıda çalışıyor, gerçek veri dönüyor
  (2026-10-30 ~16:40 TR): 2 örnek, medyan ≈ 0,31 dk, maks ≈ 0,52 dk — **E1'in hedeflediği ≤5 dk'nın çok altında**.
  `/kararlar` da canlı. D1 şeması manuel adım değil, `worker.yml` her dağıtımda otomatik uyguluyor (önceki
  günlük/DURUM notu yanlıştı, düzeltildi). Tek gerçek eksik: `GECIKME_URL` GitHub Actions değişkeni henüz
  tanımlı değil (kullanıcı eklemeli); tanımlanınca saatlik iş bu canlı veriyi `izleme/gecikme.json`'a yazacak.
- Test: `tests/test_gecikme.py` 8 altın örnek (pencere filtresi dahil, eski örnek senaryosu elle hesaplandı).

## 2026-10-30 19:00 TR — E1 devamı: gerçek algılama gecikmesi
- Sol denetiminin (`docs/DENETIM_ETRE_GECIS_2026-10-30.md`) önerdiği "E1'in asıl hız kazanımı" maddesinin ilk
  parçası: Worker zaten her dakika oda trader'larının dolumlarını çekiyordu (`fills()`), yalnız bunu kullanıp
  **gerçek** algılama gecikmesini (Hyperliquid dolum zamanı → Worker'ın onu görmesi) ölçmeye başladık.
- Worker: yeni dolum görülünce (`newest` imleç ilerleyince) D1 `son_gecikme` tablosuna trader başına **en son**
  örnek yazılıyor (kota için geçmiş birikmiyor); `GET /gecikme` bu tabloyu listeler.
- `copytrade/gecikme.py` (yeni): saf `ozet()` fonksiyonu medyan/maks üretir; `izleme.yml`'e yeni adım
  (`GECIKME_URL` tanımlıysa, düşerse `continue-on-error`) → `izleme/gecikme.json`.
- **Bu, `copytrade/saglik_hatti.py`'deki `acik_pozisyon_yasi_dk_medyan`'dan (pozisyon yaşı) tamamen ayrı** — Sol'un
  önceki denetiminin ayırdığı iki kavram artık ikisi de gerçek veriyle ölçülüyor, karıştırılmıyor.
- `docs/VERI_SOZLESMESI.md` v1.6: `izleme/gecikme.json` şeması belgelendi.
- Test: `worker/test/gecikme.test.js` 4 altın örnek (saf fonksiyon + D1 yazma + yeni dolum yoksa yazmama + uç nokta);
  `tests/test_gecikme.py` 4 altın örnek (medyan, boş liste, eksik değer, çift eleman medyanı); `node --test` 37/37,
  `pytest -q` regresyonsuz.
- **Kullanıcı/dağıtım adımı (kod dışı):** Cloudflare D1'e `worker/schema.sql`'deki `son_gecikme` tablosu bir kez
  uygulanmalı; `GECIKME_URL` GitHub Actions değişkeni (Worker'ın `.../gecikme` adresi) tanımlanmalı — yoksa adım
  sessizce atlanır, saatlik akış bozulmaz.

## 2026-10-30 18:50 TR — Sol denetimi: #441'de iki YÜKSEK bulgu, düzeltildi
- `docs/DENETIM_ETRE_GECIS_2026-10-30.md` (#442, birleşti): `sinyal_gecikme_dk_medyan` adı yanıltıcı (gerçekte
  pozisyon yaşı ölçülüyor, algılama gecikmesi değil); sağlık ışığının tazelik kontrolü yayım anındaki `now` ile
  hesaplandığından her zaman ~0 dönüyor, durmuş akışı yakalayamıyor.
- Düzeltme: alan `acik_pozisyon_yasi_dk_medyan` olarak yeniden adlandırıldı, docstring/sözleşme bunun pozisyon
  yaşı olduğunu açıkça söylüyor. `veri_tazeligi_dk` ve eşikleri `saglik_hatti`'den tamamen çıkarıldı — tazelik tek
  yerde kalıyor: Worker'ın `checkStateAlerts`'teki mevcut gerçek-zamanlı 3 saatlik kontrolü (AGENTS.md kural 7).
  `olc()` artık `simdi` parametresi almıyor (gereksizleşti). Kaynak/atıf notu modül docstring'ine eklendi.
- Test: `tests/test_saglik_hatti.py` güncellendi (yeniden adlandırma + 2 yeni uç durum: bozuk `uretildi`, acilis
  `uretildi`'den sonra görünen saat kayması). `python -m pytest -q` ve worker testleri yeniden koşuldu.

## 2026-10-30 18:00 TR — E1: veri hattı sağlığı (Etre `kalite.py` deseni)
- `copytrade/saglik_hatti.py` eklendi: oda kolu için tek sağlık kaydı (yetim gölge payı, işaret eksikliği, veri
  hata oranı, açık pozisyon yaşı) → ışık + neden listesi. Saf fonksiyonlar (`olc`/`kontrol`). **Performans
  ışığından (`traderlar[].saglik.isik`) ayrı** — bu, veri hattının kendi sağlığı.
- `izleme_motoru.run()` her koşuda `durum.json["saglik_hatti"]` yazıyor (izleme listesi boşken eklenmiyor).
- Worker `checkStateAlerts` kırmızıya geçişte Telegram uyarısı gönderiyor (yeşil/sarıdan kırmızıya; aynı kırmızıda tekrarlamaz).
- `docs/VERI_SOZLESMESI.md` v1.6: yeni alan belgelendi.
- Küçük gerçek veri denemesi: canlı `durum.json` (91 trader, `uretildi` 2026-10-30T14:20Z) üzerinde dört kol için
  çalıştırıldı. Oda: n=18, yetim_golge_orani %0,37, pozisyon yaşı medyan ≈ 41 dk, **ışık yeşil**. Kontrol:
  veri_hata_orani %11 → sarı. Havuz (t0 30.10, 1 gün yeni): veri_hata_orani %20 → **kırmızı** (gerçek bulgu: yeni
  eklenen havuz trader'larında veri hata oranı oda'dan yüksek; izlenecek).
- Test: `tests/test_saglik_hatti.py` 6 altın örnek (elle hesap) + `tests/test_izleme.py` (70, regresyon yok) +
  `worker/test/bildirim.test.js` 2 yeni (toplam 9) — hepsi yeşil.

## 2026-10-30 17:11 TR — Lisans: GPL-3.0 + Etre v2 atfı birleşti
- sg-arge `#439`, sg-pano `#46`: `LICENSE` (GPL-3.0) + `NOTICE`/README atfı (Etre v2 · Trading Office, K-11).
  Kod/davranış değişikliği yok. E1'in kod devşirme ön koşulu.

## 2026-10-30 15:00 TR — K-11: Etre geçişi başladı
- Kullanıcı kararı: Etre'nin üstün olduğu her alan (mimari, veri hattı, risk/çıkış, pano/ofis, sim gerçekçiliği,
  mühendislik) devşirilir; güvenlik (gerçek para/emir/cüzdan yok), ölçüm yöntemi ve seçim mantığı korunur.
  Lider: Claude (Sonnet 5), tek lider ve birleştirme yetkili. Denetçi: Codex (Sol). Görev: `docs/GOREV_ETRE_GECIS.md`.
