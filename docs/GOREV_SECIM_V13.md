# Görev — Seçim v1.3 (ön kayıt v1.3 uygulaması)

Kaynak: `docs/ONKAYIT_D.md` "Sürüm 1.3". Kapı eşikleri ve karar kodu (`kapi.py` adımları) değişmez. Yeni sayılar yalnız
`copytrade/kurallar.yaml`'a. Her madde altın örnekli test ile gelir; tam paket yeşil. main'e doğrudan push yok; PR açılır.

## İş paketi A — seçim (`copytrade/secim.py`)
1. `havuz`: adım 1+2 Geçti + tarz intraday/swing + adım 3 statik koşulları (`kisa_islem_payi_max`, `kapi_max_medyan_kaldirac`,
   `kapi_max_kaldirac`; sütunlar `kapi.py`'nin adım 3'te kullandıklarıyla aynı). Altın örnek: 36,5x en yüksek kaldıraçlı satır havuza girmez.
2. `kontrol_sec`: havuz − oda; dilim = tarz × en yüksek kaldıraç (havuz medyanı altı/üstü); her oda üyesine aynı dilimden bir kontrol,
   sıra `sha256(secim-<sürüm>-<kapı tarihi>-<adres>)`; dilim boşsa aynı tarzın diğer dilimi. Oda ile kesişim boş (test).
   `ikincil_kontrol` = havuz − oda (tam liste) çıktıya yazılır.
3. Tohum ve tarih kapı koşusunun tarihinden (`copytrade/kapi/<tarih>/durum.json`); seçim yeniden koşsa da aynı sonuç (test).
4. Seçim kimliği: `secim_surumu: "v1.3"`, kapı tarihi, `kurallar.yaml` ve `secim.py` sha256'sı `secim.json`'a. Veri dalında aynı
   sürüm + kapı tarihi varsa üzerine yazılmaz (iş akışı adımı reddeder).
5. Kırmızı bayraklar ayrı iş: seçim bayraksız yayımlanır; `copytrade_secim.yml`'de ikinci iş bayrakları hesaplayıp `bayrak.json`
   olarak aynı klasöre ekler (seçimi bekletmez).
6. RAPOR: "Seçim = geçmiş getiri sıralaması (adım 1–3 süzgeçli)" açıklaması; oda ↔ kontrol dilim dağılımı tablosu.

## İş paketi B — geçiş kaydı (`copytrade/kollar.py` veya yeni `copytrade/gecis.py`)
- Ekle-only kayıt: `tarih, adres, kol, olay (giris/cikis), neden, secim_surumu, kapi_tarihi`. Silme yok. Çıkış için 2 ardışık
  haftalık değerlendirme şartı. `kollar.py`'deki ikinci aday/kontrol uygulaması kaldırılır; tek kaynak `secim.py`.

## İş paketi C — analiz kodu (veri görülmeden; dondurmaya girer) `copytrade/analiz_d.py`
- `birincil_spearman(puan, ileri_getiri)`: ρ, tek yönlü p, iki yönlü %90 GA (Fisher z), n.
- `ikincil_fark(kohort_gunluk, kontrol_gunluk, btc_gunluk, blok=7, tekrar, tohum)`: beta düzeltilmiş günlük fark, MBB %95.
- `karar(birincil, ikincil, kohort_mutlak, delta_rho)`: "ise_yariyor" / "ise_yaramiyor" / "sinanamadi".
- `mde(sigma, rho, n, gun)`: rapor satırı.
- `kurallar.yaml`: `onkayit_delta_rho: 0.10`, `onkayit_p_max: 0.05`, `onkayit_blok_gun: 7`, `onkayit_veri_eksik_max: 0.05`,
  `secim_cikis_ardisik_hafta: 2`, `maliyet_duyarlilik_carpani_intraday: 2.0`.
- Her fonksiyon için elle hesaplanmış altın örnek.

## İş paketi D — haftalık geri bildirim raporu (rotasyon)
- Havuz genelinde puan ↔ o ana kadarki ileri getiri Spearman'ı ve kaldıraç/tarz kırılımı. Kol bazında getiri farkı **yazılmaz** (körlük).

## Kabul
- Tam test paketi yeşil; yerelde `python -m copytrade.secim --bayraksiz` gerçek kapı verisiyle: havuz/aday/oda/kontrol sayıları,
  oda ↔ kontrol kesişimi 0, dilim tablosu PR açıklamasında.

## İş paketi E — motor düzeltmeleri (Astra denetimi, 2026-10-29; pilot sonuçlarından önce)
Kaynak: ikinci genel denetim (Astra) bulguları 2, 5, 6, 7, 9. Her madde önce hatayı yeniden üreten altın örnekle gelir.
1. **Canlı sonuç = kanonik defter (kritik).** `izleme_motoru.copy_results` eski `delayed_copy` gerçekleşmiş-PnL yolunu kullanıyor;
   açık zarar (`unrealized_end`) ve `mark_missing` sonuca girmiyor (denetim probu: 10 BTC, giriş 100, mark 50 → canlı −%0,095,
   kanonik −%50,095). Canlı sonuç `defter.copy_ledger` ile üretilsin; gerçekleşmiş / açık / toplam ve son işaret zamanı ayrı yayımlansın.
   Canlı yol ↔ kanonik defter sözleşme testi.
2. **Gölge V1/V2/flip uçları:** V1'de atlanan ekleme sonrası kapanış bastırılıp gölgede tutulan pozisyon yetim kalmasın (kapanış,
   gölgedeki miktara uygulanır); V2 kısmi azaltmada kalan pozisyonun girişi ağırlıklı ortalama kalsın (son azaltma fiyatına
   sıfırlanmasın); flip = çıkış + yeni giriş, yeni parça tavana tabi. (`copytrade/golge.py:25-48, 65-78, 156-165`)
3. **Miras pozisyon 0/0:** V0'da miras pozisyonu kapatan ilk dolumda `ZeroDivisionError` (denetim probu). Düzelt + altın örnek.
4. **İşaret fiyatı yaşı:** `Market.mark` yaş sınırı; aşılırsa `mark_missing` sayılır ve sonuç "eksik işaretleme" notu taşır.
5. **İzleme listesi t0:** listede zaten olan adres v1.3 kohortuna girince yeni id/t0 alır (eski t0'dan yeniden oynatma yok);
   ITT etiketi seçim sürümüne bağlanır.
6. **Bayrak önbelleği:** aday başına bayrak sonucu sürümlü önbellek/checkpoint; yeniden koşu tüm çağrıları tekrarlamasın.
