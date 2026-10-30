# Gelişim günlüğü — sg-arge (Etre biçimi: tarih-saat, ne değişti, hangi ölçümü etkiledi, test sayısı)

Kronolojik, en yeni üstte. İkinci doğru kaynak değil: kararların ayrıntısı `DURUM.md`, `docs/KARARLAR_D.md` ve
görev belgelerinde durur; burada yalnız hangi değişikliğin hangi ölçümü/veriyi etkilediği kısaca kayıtlıdır.

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
