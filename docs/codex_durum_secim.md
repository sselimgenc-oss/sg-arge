# Durum: Seçim v1 (dal `claude/secim-v1`)

- [x] `copytrade/secim.py` (havuz, puan, aday, oda, kontrol, taban, elle, RAPOR, `--izleme-listesi`)
- [x] `kurallar.yaml`: `secim_aday_orani`, `secim_oda_min/max`, `secim_min_kapsam` (0,95: kullanıcı kararı 2026-10-28)
- [x] Altın örnekler `tests/test_secim.py` (12 satır); Worker testi `worker/test/events.test.js` (`kol = oda` bildirir, diğerleri sessiz)
- [x] `izleme_motoru`: `kol`, `kollar` alanları kabul edilir ve `durum.json`'a taşınır (`docs/VERI_SOZLESMESI.md` v1.5)
- [x] İş akışı `copytrade_secim.yml` (elle; veri dalına `secim/<tarih>/`)
- [x] Kırmızı bayraklar (`copytrade/bayrak.py`, `tests/test_bayrak.py`): `bayrak_rol`, `bayrak_vault_orani`, `bayrak_funding_payi`, `bayrak_alt_hesap_ters`,
      `bayrak_hacim_orani` (+ `bayrak_not`); yalnız aday katı, `secim.json` ve RAPOR bölümü; eşik yok, kimseyi elemez; `--bayraksiz` ağ isteğini kapatır.
- [ ] **Gerçek RAPOR bekliyor: veri dalındaki son koşu HIZLI koşudur (92 satır, kapsam 0,0067); tam koşu yok.** Seçim yalnız `durum = tamam` ve
      kapsam ≥ 0,95 ile çalışır; tam koşu bitince lider PR'ı birleştirir, `CALISTIR` değişikliği `main`de `CT-Seçim v1` iş akışını başlatır ve RAPOR özeti PR açıklamasına eklenir.
- [ ] **RAPOR: tam koşu bekleniyor.** Tarama `tamam` olmadan seçim tetiklenmez.

## Kararlar / varsayımlar (belgede yazmıyordu; lider denetlesin)
- `secim_min_kapsam` = 0,95 (kullanıcı kararı 2026-10-28; lider denetimi).
- Havuz ayrıca `tarz ∈ {intraday, swing}` ister (scalp tarz kovasına girmez).
- Aday sayısı = ceil(0,15 × tarzdaki puanı > 0 sayısı). Eşitlikte adres sırası.
- Oda boyutu = min(20, ilişki elemesinden sonra kalan aday); tarz kotası ilişki elemesinden ÖNCEKİ aday payıyla (en büyük kalan yöntemi);
  bir tarz kotasını dolduramazsa kalan yer öbür tarzdan aynı sırayla (genç olmayan, puan) dolar.
- İlişkili adresler yalnız aday katında karşılaştırılır; `iliskili_adresler` sütunu kapı `sonuc.csv`'sine `kesif` adımıyla yazılır.
- Kontrol sırası `sha256("<tohum>-<adres>")`; kütüphane sürümünden bağımsız ve tekrarlanabilir.
- Bir adres birden çok kolda olabilir: `kol` = oda > elle > taban > kontrol > aday > havuz; tamamı `kollar`'da. Bildirim `kol = oda`.
- Worker: `kol` alanı olmayan trader artık bildirmez (eski liste `kol` almadan çalıştırılırsa sessiz kalır).
- Taban lider tablosunu Hyperliquid'den çeker (`--taban-dosyasi` ile dosya verilebilir); bulut oturumundan erişim yok → Actions.
- Bayrak hesapları: `bayrak_rol` = `vault` | `subAccount:<master>` | diğer rol adı; funding payı = 365 gün `userFunding` toplamı / aynı dönem `closedPnl` toplamı
  (PnL 0 ise boş); vault oranı ve hacim oranı paydası kapı satırındaki güncel hesap değeri; hacim = `portfolio` `month` penceresi `vlm`;
  alt hesap kontrolü master'ın alt hesapları + (alt hesapsa) master'ın kendi pozisyonları.

## Seçim v1.3 — iş paketi A (`docs/GOREV_SECIM_V13.md`)
- [x] Havuz: adım 3 statik koşulları (kısa işlem payı, medyan ve en yüksek kaldıraç; `kapi.py` ile aynı eksik-veri kuralı)
- [x] Kontrol: odayla ayrık, tarz × en yüksek kaldıraç dilimi eşleştirmeli; `ikincil_kontrol` = havuz − oda; tohum = `secim-<sürüm>-<kapı tarihi>`
- [x] Seçim kimliği (`secim_surumu`, `kapi_tarihi`, `kurallar_sha256`, `secim_sha256`); aynı sürüm + kapı tarihi üzerine yazılmaz (kod + iş akışı)
- [x] Çıktı klasörü `secim/<tarih>-<sürüm>/`; bayraklar ayrı iş (`--bayrak` → `bayrak.json`), seçimi beklemez
- [x] RAPOR: "geçmiş getiri sıralaması (adım 1–3 süzgeçli)" açıklaması + oda ↔ kontrol dilim tablosu
- [ ] B (geçiş kaydı), C (analiz kodu), D (haftalık geri bildirim): ayrı PR'lar
## Seçim v1.3 — iş paketi B (geçiş kaydı)
- [x] `copytrade/gecis.py`: yalnız eklemeli `kayit.jsonl` (`tarih, adres, kol, olay giris|cikis, neden, secim_surumu, kapi_tarihi`) ve `degerlendirme.jsonl`; silme/güncelleme yolu yok; aynı olay iki kez yazılmaz
- [x] Çıkış: `secim_cikis_ardisik_hafta` (2) ardışık haftalık uygunsuz değerlendirme; araya uygun ya da atlanmış hafta sayacı sıfırlar
- [x] `copytrade/kollar.py` (ikinci aday/kontrol/terfi uygulaması) kaldırıldı; tek kaynak `secim.py`; ona ait eski testler silindi (kod yok)
- Not: `golge_terfi_*` anahtarları artık kodda kullanılmıyor (kural belgelerinde duruyor; temizlik ayrı karar)

## Seçim v1.3 — iş paketi C (analiz kodu; gölge verisi görülmeden)
- [x] `copytrade/analiz_d.py`: `birincil_spearman` (ρ, tek yönlü p, iki yönlü %90 GA, n), `ikincil_fark` (BTC betası düzeltilmiş, örtüşen blok bootstrap %95), `karar` (3 sonuç), `mde`, `duyarlilik_net`, `veri_eksik`
- [x] Sayılar yalnız `kurallar.yaml`: `onkayit_delta_rho` 0,10 · `onkayit_p_max` 0,05 · `onkayit_blok_gun` 7 · `onkayit_veri_eksik_max` 0,05 · `maliyet_duyarlilik_carpani_intraday` 2 · `onkayit_guc` 0,80 · `onkayit_ci_ikincil` 0,95 · `onkayit_bootstrap_tekrar` 2000 · `onkayit_spearman_varyans_carpani` 1,06
- [x] Elle hesaplanmış altın örnekler: ρ = 0,8 (n=5: p 0,065642; GA [−0,098538; 0,979941]), bağlı sıralar 0,948683, MDE 0,22875 %/gün (σ 0,02, ρ 0,3, n 10, 84 gün)

## Seçim v1.3 — iş paketi D (haftalık geri bildirim)
- [x] `copytrade/haftalik_rapor.py`: havuz genelinde puan ↔ ileri getiri Spearman'ı + tarz / kaldıraç dilimi kırılımı; **kol bazında getiri yazılmaz** (körlük testi); `--gecis` ile `gecis.haftalik` aynı çalışmada
- [x] `.github/workflows/copytrade_haftalik.yml`: elle çalışır (zamanlama yok), veri dalındaki en son seçimi okur, `rotasyon/` altına yazar
- Bekleyen: gölge ileri getiri dosyası (`--getiri`) gölge defteri yayımlanınca bağlanır; o güne dek rapor "ileri getiri verisi yok" der

## Seçim v1.3 — iş paketi E2–E4, E6 (motor düzeltmeleri)
- [x] E2: V1 atlanan ekleme sonrası kapanış gölgedeki pozisyona uygulanır (yetim yok); V2 kısmi azaltmada giriş ve pozisyon yaşı korunur; flip = çıkış + yeni giriş, yeni parça tavana tabi
- [x] E3: etiketten önceki (miras) pozisyonu kapatan dolum `ZeroDivisionError` vermez (V0/V1/V2)
- [x] E4: `Market.mark_at` işaret yaşı sınırı (`isaret_yas_max_dk` 120); aşılırsa `mark_missing`, canlı sonuç "eksik işaretleme" notu taşır
- [x] E6: `bayrak.json` sürümlü önbellek (kod hash + seçim sürümü + kapı tarihi), her adresten sonra checkpoint, iş akışı önceki/kısmi sonucu veri dalından geri yükler ve zaman aşımında da yazar

## Bayrak ek ölçüleri (Argon A12, `copytrade/bayrak_ek.py`)
- [x] Martingale (zararda ekleme), tek coin HHI, ekleme derinliği; saf ölçü, eşik yok. Pencere öncesinden taşınan pozisyonda giriş bilinmiyor sayılır, pozisyon sıfırlanana dek zararda ekleme ölçülmez; ayrıştırılamayan satırlar `atlanan_satir`; girdi `perp_fills` ile süzülür
- [x] `bayrak.json` / `BAYRAK.md` bilgi sütunları: `bayrak_zararda_ekleme`, `bayrak_katlama_orani`, `bayrak_coin_hhi`, `bayrak_en_buyuk_coin_payi`, `bayrak_ekleme_derinligi`; `bayrak_kat_esik` (2,0) yalnız katlama oranının tanımı, kimseyi elemez
## Ek 2 bilgi sütunları (#350'den taşındı)
- [x] Kapı/seçim çıktısı: `acik_pozisyon_sayisi`, `unrealized_end`, `mark_missing`, `acik_pozisyon_notional` (kanonik defter `copy_ledger`; E1 ile aynı kaynak), yönlü dolum farkı (`yonlu_dolum_*`; sıfır gecikmede üretilmez), `en_iyi_islem_haric_getiri`, `medyan_tutma_saat`, `gunluk_islem_sikligi`
- [x] Gölge sağlaması: trader'ın kendi açık K/Z'si ve toplam net kıyası (`trader_toplam_net`, `golge_toplam_net`, `toplam_net_fark`), eksik işaretleme notu
## Argon A13 — pozisyon mutabakatı (`copytrade/pozisyon_mutabakat.py`)
- [x] Defter ↔ `clearinghouseState` (uyumlu / yetim / eksik / yon_farki / boy_farki); `borsa_pozisyonlari` ve `mutabakat` bozuk satır sayısını dönüş değerinde verir; eşikler `kurallar.yaml` (`mutabakat_*_tolerans`)
- [x] İzleme motoru her koşuda oda üyeleri için çalıştırır, sonucu `veri_kalitesi.mutabakat` alanına yazar; yalnız rapor (otomatik kapatma yok)
## Argon A15 — mum akıl sağlığı (`copytrade/mum_saglik.py`)
- [x] bozuk / sıçrama / boşluk / hacimsiz; sıçrama **oranla** (`max(o/medyan, medyan/o) >= mum_sicrama_kat`, çöküşler de yakalanır), medyana yalnız geçerli mumların kapanışı girer
- [x] `defter.Market.mark_at`: bozuk/sıçrama mumla işaretlenmez, işaret yaşı son **geçerli** mumdan ölçülür; `isaret_yas_max_dk` aşılırsa `mark_missing` (E4 ile birleşik)
- [x] Kapı satırında `mum_*` sütunları; RAPOR.md "Mum sağlığı (A15)" bölümü ve `durum.json` `mum_ozeti`
## Argon A14 — oda yoğunlaşması ve puan tutarlılığı (`copytrade/yogunlasma.py`)
- [x] Ortalama bağlantılı kümeleme, etkin küme sayısı, yarı tutarlılığı (sıra korelasyonu `analiz_d` ile tek uygulama); eşikler `kurallar.yaml` (`yogunlasma_min_ortak_gun` 10, `yogunlasma_kume_esik` 0,5)
- [x] Kapı, adım 1–2'yi geçenlerin günlük kopya getirisini `gunluk.csv.gz` olarak yayımlar (parçalar + önceki dosya birleşir); seçim RAPOR'unda "Oda yoğunlaşması ve puan tutarlılığı (bilgi)" bölümü ve `secim.json` `yogunlasma`; seçimi değiştirmez
## Ön kayıt D v1.4 — performans çıkışı ve risk işaretleri (`copytrade/gecis.py`, `copytrade/risk_isaretleri.py`)
- [x] Çıkış: etiketten bu yana ≥ `secim_cikis_min_hafta` (4) haftalık değerlendirme **ve** ≥ `secim_cikis_min_kapanmis_islem` (60) kapanmış işlem **ve** havuz puan sırasında alt `secim_cikis_havuz_alt_dilim` (0,50) dilimi **ve** `secim_cikis_ardisik_hafta` (2) ardışık hafta; seçim odasından düşmek tek başına çıkış değil (`tests/test_cikis_v14.py`: 59/60 işlem, 3/4 hafta, araya giren uygun hafta)
- [x] Kapanmış işlem verisi yoksa çıkış değerlendirilemez (çıkış yok); havuzda olmayan/puansız üye sıralanamaz (çıkış gerekçesi olmaz)
- [x] Risk işaretleri (haftalık rapor `--risk`, yalnız bilgi, performans sayısı yok): kaldıraç sıçraması (2,5×), martingale başlangıcı (`bayrak_ek`), zararda uzun tutma (3×) (`tests/test_risk_isaretleri.py`)
