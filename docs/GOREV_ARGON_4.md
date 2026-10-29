# Argon görevleri — 4. tur (2026-10-29, lider)

Kullanıcı kutulardan birini olduğu gibi Argon'a verir, cevabı getirir; lider `arastirma/copytrade/argon_*.md` olarak kaydeder ve
denetler. Sıra: A22 → A23 → A24 (bağımsız; paralel de olabilir).

---

## A22 — Bağımsız istatistik hakemi: Faz 3 karar kuralının yanlış alarm oranı ve pilotun gücü

```
Bağlam: Hyperliquid'de trader kopyalama araştırması (gerçek para yok, gölge hesap). 18 kişilik "oda" (seçilmiş traderlar) ile
18 kişilik eşleştirilmiş "kontrol" (rastgele) grubunun günlük net getirilerini kıyaslıyoruz. Eşit ağırlıklı iki portföy.
Fark serisi d_t = oda_t − kontrol_t; BTC betası düzeltilir: d_t = α + β·BTC_t + ε_t; karar istatistiği α (günlük).
Belirsizlik: 7 günlük örtüşen blok bootstrap (MBB), %95. Geçmiş prova kuralı: 60 günlük pencerelerde α ≤ 0 olan pencere
oranı > %50 ise "durdur".

İstenen — tek, bağımsız çalışan Python 3 betiği (numpy/pandas; ağ yok) ve kısa rapor:
1. Sıfır beceri simülasyonu: 36 trader, günlük getiri ~ t-dağılımı (df=4), trader oynaklığı %2–%8 arası, BTC'ye beta 0–1.5,
   traderlar arası korelasyon 0.2–0.5. Rastgele 18/18 böl. ≥200 tohum. (a) 60 günlük tek pencerede α>0 oranı (~%50 beklenir),
   (b) 2 hafta kaydırmalı 6–12 pencerede "durdur" kuralının yanlış tetiklenme oranı (pencereler örtüştüğü için bağımsız değil!),
   (c) MBB %95 aralığının gerçek kapsama oranı (n=60 ve n=84 gün).
2. Güç: odaya günlük +α (yıllık %10, %25, %50 karşılığı) enjekte et; 84 günde (12 hafta) ve 168 günde α'nın %95 alt sınırı > 0
   olma olasılığı. Sonuç tablosu.
3. Saptanabilir en küçük fark (MDE, %80 güç) 12 ve 24 haftada.
Kurallar: kod tek dosya, tohumlu, çalıştırma komutu ve süresi yazılı; her sayının hangi koşudan geldiği belli; varsayımlar açık.
Cevap Türkçe.
```

---

## A23 — Yeni seçim fikirleri: oda için alternatif kurallar (ileride ikinci deney)

```
Bağlam: Hyperliquid perp borsasında halka açık işlem verisinden (dolumlar, funding, saatlik mum, hesap değeri) trader seçiyoruz.
Bugünkü kural: geçmiş kopya getirisi sıralaması (gecikmeli kopya, maliyet sonrası), süzgeçler: en yüksek kaldıraç ≤ 10x, medyan
≤ 3x, en az ~1 yıl geçmiş, hesap ≥ 5.000 $. Amaç: aynı veriyle hesaplanabilecek 3–5 alternatif seçim kuralı.

İstenen:
1. Kopya ticaret / fon seçimi literatüründen (akademik + eToro, Bybit, Binance copy trading lider kriterleri, Hyperliquid vault
   metrikleri) "geleceği tahmin ettiği gösterilmiş" sinyaller: kalıcılık (persistence), risk ayarlı getiri, düşüş derinliği,
   tutarlılık (kârlı ay oranı), işlem disiplini, kapasite. Her biri için kaynak ve bulgunun gücü.
2. Her öneri için: tanım (formül), gereken veri alanı, hesaplama penceresi, bilinen tuzak (hayatta kalan yanlılığı, aşırı uyum).
3. Hangisinin bizim "geçmiş getiri sıralaması"ndan en farklı (düşük korelasyonlu) bilgi taşıyacağına dair gerekçeli sıralama.
Kurallar: kaynak bağlantısı + erişim tarihi; doğrulanamayan "doğrulanamadı"; tahmin tahmin diye. Cevap Türkçe, tablo.
```

---

## A24 — Pano ve ofis kullanılabilirlik denetimi (telefon öncelikli)

```
Bağlam: Kopya ticaret izleme panosu (salt okunur, gerçek para yok). Kullanıcı teknik değil, telefondan bakıyor. Adresler:
- Ana pano: https://sselimgenc-oss.github.io/sg-pano/
- Ofis görünümü: https://sselimgenc-oss.github.io/sg-pano/ofis/
İstenen: telefon genişliğinde (≈390 px) ve masaüstünde gez; şu soruların cevabını ekran ekran yaz:
1. İlk 10 saniyede "bugün durum ne, bir şey yapmam gerekiyor mu?" anlaşılıyor mu?
2. Anlaşılmayan terimler, İngilizce/teknik ifadeler, tutarsız adlandırma (ör. aynı şeye iki ad).
3. Okunmayan, taşan, üst üste binen, çok küçük öğeler; dokunma hedefleri.
4. Gereksiz ya da tekrar eden bilgiler; eksik olan en önemli 3 bilgi.
5. Öncelikli 10 maddelik düzeltme listesi: her biri "nerede · sorun · öneri · etkisi (yüksek/orta/düşük)".
Not: Bazı bölümler henüz veriye bağlı değil ve gri olabilir; bunu "eksik veri" diye ayrı işaretle. Kod yazma; yalnız rapor.
Cevap Türkçe.
```
