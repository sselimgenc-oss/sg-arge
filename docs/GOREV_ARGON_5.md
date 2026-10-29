# Argon görevleri — 5. tur (2026-10-29, lider)

Kullanıcı kutulardan birini olduğu gibi Argon'a verir, cevabı getirir; lider `arastirma/copytrade/argon_*.md` olarak kaydeder ve
denetler. A25 → A26 → A27 (bağımsız; paralel olabilir).

---

## A25 — Karar kuralı karşılaştırması: Bayesçi eşik, sıralı test, sabit bakış

```
Bağlam: Hyperliquid'de gölge (gerçek para yok) trader kopyalama. 18 kişilik "oda" ile 18 kişilik rastgele "kontrol"un eşit
ağırlıklı günlük getiri farkı d_t, BTC betası düzeltilmiş. Önceki simülasyonun veri üretimi aynen kullanılacak: 36 trader,
Student-t (df=4), trader oynaklığı günlük %2–8, BTC betası 0–1.5, ortak faktörle korelasyon 0.2–0.5, BTC günlük oynaklık %2.5.
Kullanıcı panoya her hafta bakıyor; bu yüzden "bakma" sayısı yanlış alarmı şişirmemeli.

İstenen — tek, bağımsız Python 3 betiği (numpy/pandas/scipy; ağ yok), tohumlu, ≥500 tekrar, ve kısa Türkçe rapor:
Üç karar kuralını haftalık bakışla 26 haftaya kadar karşılaştır:
 (K1) Bayesçi normal-normal: önsel yıllık fark ~ N(0, %30²); se blok bootstrap (7 gün). "Umut verici": P(fark>0)>%95 ve
      P(fark>%20/yıl)>%70. "Durdur": P(fark>%20/yıl)<%10. 26. haftada karar yoksa "kanıt yok".
 (K2) Her-an-geçerli test: bahis martingalesi E ← E·(1+λ·clip(d_hafta,±c)/c), c=%5, λ∈{0.1,0.2,0.3}; E≥20 → "fark var".
      Zarar tarafı için ayna testi.
 (K3) Sabit bakış: yalnız 4., 8., 12. hafta, O'Brien–Fleming tipi eşik.
Gerçek fark: yıllık 0, +%10, +%25, +%50, −%25. Her kural ve fark için: yanlış "umut verici" oranı (fark=0'da), doğru tespit oranı,
yanlış "durdur" oranı (fark>0'da), ortalama karar haftası. Tek tablo + hangi kuralı neden önerdiğin (3–5 cümle).
Kurallar: her sayının hangi koşudan geldiği belli; çalıştırma komutu ve süresi yazılı; varsayımlar açık.
```

---

## A26 — Funding/hedge ve piyasa yapıcı hesapları tespit etmek

```
Bağlam: Hyperliquid perp trader'larını gecikmeli (30 dk / 2 sa) yalnız perp bacağıyla kopyalıyoruz (gerçek para yok). Uyarı: lider
tablosundaki bazı hesaplar yönsel tahminle değil funding (fonlama) arbitrajı, delta-nötr hedge (spot ya da başka borsada ters
bacak) ya da piyasa yapıcılıkla kazanıyor; bunları kopyalamak hedge'siz yönsel kumara dönüşür.
Elimizdeki herkese açık veri: dolumlar (son 10.000; fiyat, miktar, yön, maker/taker bilgisi varsa, ücret, closedPnl), funding
ödemeleri (userFunding), hesap durumu (clearinghouseState: pozisyonlar, kaldıraç), spot bakiyeleri (spotClearinghouseState),
hesap değeri/kâr geçmişi (portfolio), 1 dk mumlar.

İstenen (Türkçe, sade):
1. Bu veriyle hesaplanabilen 4–6 ölçüt: ör. funding geliri / toplam kâr, maker payı, aynı coinde spot ↔ perp ters pozisyon,
   ortalama tutma süresi, pozisyon yönü ile funding işaretinin ilişkisi, işlem başına kâr dağılımı. Her biri için formül,
   gereken alan, önerilen eşik ve eşiğin gerekçesi.
2. "Kopyalanamaz" etiketi için karar ağacı (en çok 5 adım).
3. Yanlış pozitif riski: gerçek yönsel trader'ı yanlışlıkla eleyen durumlar.
4. Kaynak: Hyperliquid resmi dokümanı ve varsa akademik/sektör çalışması; gerçek bağlantı ver, emin değilsen "doğrulanamadı".
```

---

## A27 — Oda içi kalabalıklaşma (aynı pozisyonu 18 kez kopyalamak)

```
Bağlam: 18 trader'lık sanal kopya odası. Risk: normal günlerde bağımsız görünen trader'lar düşüş günlerinde aynı coinde aynı yönde
olabilir; o zaman 18 kişi değil tek dev pozisyon kopyalanmış olur. Elimizdeki veri: her trader'ın saatlik açık pozisyonları
(coin, yön, büyüklük, kaldıraç), günlük getiri serileri, 1 dk mumlar.

İstenen (Türkçe, sade):
1. Hesaplanabilen 3–4 ölçüt: ör. oda net maruziyeti (coin başına toplam yönlü pay), etkin trader sayısı (çeşitlenme), düşüş
   günlerindeki getiri korelasyonu (kuyruk bağımlılığı), aynı coinde aynı yön payı. Formül, gereken veri, uyarı eşiği ve gerekçesi.
2. Bir ölçüt eşiği aşarsa ne yapılmalı (yalnız uyarı; otomatik değişiklik yok) — panoda nasıl gösterilmeli (tek satır).
3. 18 kişilik küçük örnekte bu ölçütlerin güvenilirliği; kaç gün veri gerekir.
4. Kaynak: gerçek bağlantı; emin değilsen "doğrulanamadı".
```
