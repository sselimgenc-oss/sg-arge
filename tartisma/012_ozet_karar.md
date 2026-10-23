# 012 Özet ve lider kararı: Niş enstrüman mı, evren mi?

**Tarih:** 2026-10-23. **Kaynaklar:** `012_cevap_sonnet.md`, `012_cevap_codex.md`, `012_cevap_argon.md`.
**Durum:** Kararlar alındı. **Kullanıcı (2026-10-23) seçenek (a)'yı onayladı:** yılda %20-30 net, MDD ≤ %15. Görev: `docs/GOREV_U1.md`.

## 1. Uzlaşı (4 görüşün ortak noktası)
1. **"Niş geliştir, geniş doğrula" doğru ama tek başına yetmez.** Üç katılımcı da aynı açığı gösterdi: kardeş listesi ve geçme eşiği test **öncesi** yazılmazsa kardeş doğrulaması da aşırı uyum kapısına döner (Argon: ardışık seçim yanlılığı).
2. **Ortak parametre seti.** Enstrümana özel ayar yasak. Parametreler volatiliteye göre normalize edilir (ATR katı, z-skor, yüzdelik), sabit fiyat ya da pip eşiği kullanılmaz. Oybirliği.
3. **Korelasyonlu kardeş bağımsız kanıt değildir.** BTC ve ETH birlikte yaklaşık 1,2 bağımsız örnek sayılır. Karar havuzlanmış sonuca ve bootstrap güven aralığına göre verilir, "kaçında PF > 1" sayısı tek başına belirleyici değildir.
4. **Scalp ilk iş değil.** Maliyet payı yüksek ve temiz dakika verisi yalnız birkaç enstrümanda var. Day trade likit kripto ve majör FX/CFD'de yapılır; swing evrende yapılır.
5. **Aylık %5 net, %15 MDD bütçesiyle gerçekçi değil.** Dört görüş de bu yönde. Ayrıntı bölüm 3'te.

## 2. Kararlar (lider)
### K1. Geliştirme birimi: mini-evren, tek enstrüman değil
- Strateji en baştan **4-8 likit enstrümanlık bir çekirdek** üzerinde, havuzlanmış olarak tasarlanır (Argon önerisi).
- Tek enstrümanda geliştirme yalnız **yazılı bir yapısal mekanizma** varsa yapılır (ör. Gotobi/fixing, seans açılışı, vade dönüşü). İddia da yalnız o enstrümanla sınırlı tutulur (Codex).

### K2. Ön kayıt zorunlu
Test başlamadan `docs/spec/U-<id>.yaml` kartına şunlar yazılır:
- hipotez ve mekanizma;
- çekirdek ve kardeş listesi;
- parametre ızgarası (deneme sayısı DSR'ye eklenir);
- geçme eşikleri.

Sonradan değiştirilen her şey yeni deneme sayılır.

### K3. Kardeş doğrulama eşiği
Ham parametrelerle (ince ayar yok) şu koşullar birlikte sağlanmalı:
- kardeşlerin **≥ %60'ında net PF > 1,1**;
- **havuzlanmış** sonuç Faz 1 hunisini geçer (null testi, 2x/3x maliyet, bootstrap MDD);
- tek bir enstrüman toplam kârın en fazla **%35**'ini getirir;
- kâr tek bir şok dönemine bağlı değildir.

### K4. Saklı dönem
- **Son 12 ay (2025-10 → 2026-10)** hiçbir geliştirme adımında kullanılmaz; yalnız nihai sınavda bir kez açılır.
- Faz 1'in OOS'u artık "görülmüş" sayılır.

### K5. Evren ve veri: kullanıcının evreni zaten elimizde
| Sınıf | Arşiv | Not |
|---|---|---|
| BIST30 | `data/evren.csv` | |
| ABD büyükler | ABD25 | PIT evren de var |
| Kripto | KRIPTO25 | |
| Emtia | EMTIA6 | |

- Günlük veri 2015→ (kripto Binance başlangıcından), saatlik veri ~2 yıl.
- Kripto dakikalık veri Binance'te 2017'den beri var.
- **Swing için veri hazır.** Day trade için kripto hazır, FX/CFD Dukascopy indirmesini bekliyor.

### K6. İlk iki hat
- **Hat 1 (swing, günlük):** 4 sınıflı sepette **zaman serisi trend + volatilite hedefleme** (Sonnet önerisi; literatürde en güçlü kenar: Moskowitz-Ooi-Pedersen 2012, Hurst-Ooi-Pedersen). Üstüne **sınıf içi kesitsel göreli güç** (Argon'un ikili momentum yapısı). Kesitsel kısım için hisseler (BIST30 + ABD) normalize edilerek birleştirilir, çünkü 20 isimlik dilim çok gürültülü (Sonnet).
- **Hat 2 (day, kripto 15 dk-1 saat):** Çekirdek BTC, ETH, SOL, BNB. Kardeşler sonraki 6-10 likit coin. Ortak parametre ve maliyet stresi uygulanır (Codex ve Argon önerisi).
- **Ertelendi:** FX/CFD gün içi hattı (USDJPY fixing/Gotobi, XAU, NQ açılış kırılımı). Dukascopy verisi indirilip spread modeli kurulunca açılır. Scalp şimdilik yok.

### K7. Portföy mantığı
Hedef tek bir "kutsal kâse" değil, **düşük korelasyonlu 6-8 stratejilik bir sepettir.** Grinold-Kahn temel yasası: bağımsız bahis sayısı, kenarın kendisi kadar önemlidir. Hat 1 ve Hat 2 bu sepetin ilk iki parçası.

## 3. Hedef ve risk: kullanıcı kararı gerekiyor
| Görüş | Değerlendirme |
|---|---|
| Sonnet | %15 MDD ile gerçekçi hedef yılda ~%15-25. Aylık %5 için Sharpe ~3 ya da %50+ MDD gerekir. |
| Argon | %15 MDD ile mükemmel senaryo aylık %2-3. Aylık %5 ancak %25-30 MDD ile yaklaşılabilir. |
| Codex | Aylık %5 hedef değil, üst senaryo olabilir; güvenilir biçimde vaat edilemez. |
| Lider | Katılıyorum. Sürdürülebilir hedef yılda %20-30, MDD ≤ %15-20. |

**Kullanıcıya seçenekler:**
- **(a) Önerilen:** hedef yılda %20-30 (ayda ~%1,5-2,5), MDD ≤ %15.
- **(b) Agresif:** hedef ayda %3-5, MDD bütçesi %25-30. Daha yüksek risk; iflas riski ve psikolojik yük belirgin.
- **(c)** Kullanıcının kendi tanımı.

Seçim üretimin yönünü değiştirmez, yalnız risk ayarını (işlem başı risk, kaldıraç sınırı) ve eleme eşiklerini değiştirir. Bu yüzden Hat 1 ve Hat 2'nin hazırlığı beklemeden başlayabilir.

## 4. Sonraki adım
`docs/GOREV_U1.md` yazıldı.

**Not:** Codex literatür adı vermedi (uydurmamak için); Sonnet ve Argon'un verdiği kaynak adları kullanılmadan önce doğrulanacak.
