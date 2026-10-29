# Görev — Pilot veri hattı (Sonnet, 2026-10-29, lider)

Bağlam: Seçim v1.3 onaylandı, canlı gölge pilotu 2026-10-29'da başladı (`DURUM.md`). Analiz fonksiyonları hazır ve dondurulmuş
(`copytrade/analiz_d.py`, Paket C). **Eksik olan, onları besleyen veri hattı:** `CT-Haftalık` (`copytrade_haftalik.yml`) yalnız elle
çalışıyor ve `--getiri`, `--kapanmis-islem`, `--risk` girdileri hiçbir yerde üretilmiyor. Bugünkü hâliyle haftalık rapor "ileri
getiri verisi yok" der, v1.4 çıkış kuralı değerlendirilemez, risk işaretleri boş kalır.

Kurallar (değişmez): yöntem, kapı, eşik ve karar kodu değişmez; `analiz_d.py` **değişmez** (dondurmada). Eşikler yalnız
`kurallar.yaml`'dan. Yeni kod altın örnekli testle gelir; testler zayıflatılmaz. main'e doğrudan push yok; PR açılır. Repo açık:
anahtar, şifre ve kişisel veri commit edilmez. Gerçek emir yok.

**Körlük (ön kayıt madde 6, K‑6):** Bu hat hiçbir çıktıda kol bazında getiri (oda, kontrol, taban toplamı ya da farkı) üretmez,
yazdırmaz, günlüğe basmaz. Adres başına ileri getiri yalnız `haftalik_rapor`'un puan ↔ ileri getiri bölümüne (rotasyon) girer.
Testlerde de gerçek veri kullanılmaz; yalnız sentetik.

## 1. Kaynak doğrulama (önce, kod yazmadan)
- `copytrade/arsiv.py` `pool()` havuzun (seçim v1.3 `secim.json` havuz katı, 185 adres) **tamamını** kapsıyor mu? `arsiv.yml`
  `gate_root` veriyor mu? Kapsamıyorsa düzelt (birincil test havuzun tamamında Spearman ister).
- Arşiv 2026-10-29 12:24Z'de ilk kez yeşil koştu (R2 anahtarları o gün düzeltildi). Ölçüm penceresi t0 = 2026-10-29; t0 ile ilk
  başarılı arşiv arasındaki boşluk Hyperliquid API'den (`userFillsByTime`) tamamlanabiliyor mu? Sonucu PR açıklamasına yaz.

## 2. Haftalık girdiler (`copytrade/pilot_veri.py`, yeni)
Arşivdeki dolum, funding ve mumlardan, etiket gününden (seçimin `tarih`i) hafta sonuna kadar, adres başına:
- `ileri_getiri`: V0 gölge net getirisi (`copytrade.golge.calistir` / `defter.copy_ledger`, maliyet ve tarz gecikmesi dahil;
  sermaye kuralı ön kayıt 1.2). Pasifleşen adres sıfır getirili gün olarak paydada kalır (ön kayıt "Katlar" son madde).
- `kapanmis_islem`: etiketten bu yana kapanmış işlem sayısı (v1.4 çıkış kuralı).
- `risk`: `risk_isaretleri.uye_isaretleri` girdisi `{etiket: {...}, son: {...}}` (yalnız oda üyeleri). `etiket` değerleri
  `secim.json` ve `bayrak.json`'dan.
- Haftalık veri eksikliği oranı (`analiz_d.veri_eksik`) adres başına; > eşik ise rapor "veri eksik" yazar.
Çıktı: üç JSON (`haftalik_rapor` biçiminde). Altın örnek: 2 adres × 1 hafta, elle hesaplanmış dolum/mum fikstürü.

## 3. İş akışı
- `copytrade_haftalik.yml`: önce `pilot_veri` (arşivi R2'den okur; `arsiv.yml`'deki gizli değişkenler), sonra
  `haftalik_rapor --getiri --kapanmis-islem --risk --gecis`. Haftalık zamanlama ekle (Perşembe, etiket günü; dakika 0 olmasın).
- Hata yutma yok: girdi üretilemezse koşu kırmızı biter.

## 4. Analiz koşucusu (12. hafta için, veri görülmeden)
`copytrade/analiz_kosu.py`: `analiz_d` fonksiyonlarını uçtan uca çağıran giriş noktası (birincil: havuzun tamamı puan ↔
12 hafta net getiri; ikincil: oda ↔ eşleştirilmiş kontrol günlük farkı, BTC beta düzeltilmiş; tanımlayıcılar). **Tarih kilidi:**
`kurallar.yaml` `onkayit_analiz_tarihi: "2027-01-21"` öncesinde gerçek veriyle çalışmayı reddeder (yalnız `--sentetik`).
Test yalnız sentetik veriyle; sonuç tablosunun biçimi altın örnekle sabitlenir.

## 5. Ek (lider, Argon A20/A21 sonrası)
- **Arşiv kesinti alarmı:** `arsiv.yml` art arda başarısız koşular 12 saati aşarsa kırmızı uyarı (haftalık raporda ve iş günlüğünde).
  Neden (A21): halka açık API yalnız son 10.000 dolumu verir; çok aktif adreste ~1 haftadan uzun boşluk geri alınamaz.
- **Maliyet duyarlılığı (K‑5, kullanıcı kararı):** `maliyet_rapor.py`'ye HIP‑3 için iki alt sınıf: büyüme modu ve standart mod
  (deployer ücret ölçeği API `perpDexs`/`meta` yanıtından), ayrıca seans içi/dışı (ABD hisse seansı). Oranlar `kurallar.yaml`'a
  (`maliyet_sinif_alt_uc` yanına), A20 tablosundaki aralıkların üst ucu. Ana karar maliyeti değişmez; yalnız rapor.

## Teslim
PR açıklamasında: 1. maddenin bulguları, yeni yaml anahtarları, test sayısı. Lider denetler ve birleştirir.
