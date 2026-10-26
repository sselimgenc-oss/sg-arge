# Kapımız adil mi? — 7 yapay zekânın görüşü ve lider değerlendirmesi (2026-10-26)

Soru metni: kullanıcı, aynı bağımsız istemi 7 modele sordu (Argon, BigPickle, Nemorton, Flint40b, DeepSeek, Beamfree,
GLM 5.3). Yanıtlar olduğu gibi: `arastirma/kapi/`. Sol 6.1'in yanıtı gelince eklenecek.

## 1. Ortak hüküm (7/7)
Kapı mühendislik açısından temiz (nedensellik kesimi, yayım sonrası sınama, gerçekçi maliyet, iki denetim), ama
**istatistiksel seçim kapısı olarak geçirgen**:
1. **"Net getiri > 0" bir anlamlılık testi değil.** Kenarsız bir strateji ~%50 geçer; boğa piyasasında yalnız alım
   yapan rastgele strateji maliyet sonrası **%60–85** geçer (Φ(SR·√T) yaklaşımı; maruziyet yükseldikçe artar).
2. **Piyasa etkisi ayrıştırılmıyor.** Al-ve-tut tek başına yetmez; **maruziyet eşleşmiş kıyas** (stratejinin piyasada
   kaldığı oranda piyasa + kalan nakit) ve **beta ayarlı alfa** (Newey-West t) gerekir.
3. **Çoklu test cezası yok.** ~1.050 denemede DSR bilgi amaçlı kaldı; **eleyici** olmalı, deneme sayısı kopyalar
   kümelenerek (N_eff) hesaplanmalı. Aile için BHY-FDR (q ≈ %10); son kısa listeye Hansen SPA / Romano–Wolf.
4. **Plasebo (rastgele giriş permütasyonu) en pratik ve en ikna edici ölçüm:** aynı sembol, dönem, işlem sayısı,
   tutma süresi, maruziyet ve maliyetle 1.000–2.000 rastgele strateji → kapının yanlış geçme oranı; strateji plasebo
   dağılımının %95'ini geçmeli. Hedef yanlış geçme ≤ %5–10.
5. **Kısa ve eşit olmayan sınama.** Ham getiri yerine PSR / Sharpe alt güven sınırı / t = SR·√T; asgari örneklem
   (≥ 50 işlem, çoğu ≥ 1–2 yıl önerdi). Kısa sınama "geçti" değil **"yetersiz"** sayılmalı (üç değerli sonuç).
6. **Kapı sonrası elle eleme** (p10, PF, 30 işlem/yıl, 0,6 korelasyon, "hata şüphesi") sonuçlar görüldükten sonra
   kondu → "çatallanan yollar". Kurallar **önceden yazılı** ve otomatik olmalı.
7. **26 hafta paper kenarı kanıtlamaz**; icra/operasyon doğrulamasıdır (Argon izleme notuyla aynı).
8. **ML'de kapı çöker:** yayım tarihi koruması yok olur, binlerce denemede beklenen en iyi Sharpe gürültüden ≈ 3,7–4,3
   (N = 10³–10⁴). Gerekenler: deneme kayıt defteri, kilitli tek kullanımlık holdout, CPCV/PBO, Arnott–Harvey–Markowitz
   (2019) protokolü, kapı kör ve sabit (Goodhart).

## 2. Haksız eleme tarafı (çoğunluk)
- **Yılda 30 işlem kuralı** seyrek ama geçerli trend stratejilerini atar (Argon, Beamfree, Flint) — kullanıcı kuralıydı.
- **Tek sembol** sadakati iyi stratejiyi kötü sembolde öldürür; sepette yeniden test önerildi.
- **401 veri yok** rastgele değil; evren likit/popüler sembollere kaydı.
- **Yorumlayıcı farkı:** 93 "işlem yok"un bir kısmı çeviri hatası olabilir; ≥ 50 stratejide TradingView çıktısıyla
  satır satır karşılaştırma önerildi (DeepSeek).

## 3. Yanıtlardaki hatalar (dikkate alınmadı)
- **BigPickle §0** "`stratejiler_final.json` 53 kayıt, kopyalar" — bu dosya bizim repoda yok; aracın kendi çalışma
  dizinindeki başka bir projeyi (büyük olasılıkla eski `strateji-test-pano` taslak verisi) taramış. Bizim 13 kitapla ilgisi yok.
- **Flint40b:** kaynak künyeleri hatalı (DSR yazarları, Hansen 2005 başlığı), "SPA p < 0,05 → reddet" yönü ters. Düşük ağırlık.
- **GLM 5.3:** §7'nin bir kısmı bozuk metin; okunabilen kısım diğerleriyle aynı yönde.
- **Nemorton:** "yayım sonrası kilit iyi stratejiyi eler" — bu bilinçli tasarım (yazarın ezberini dışlar), hata değil.

## 4. Argon'un önemli özel uyarısı
**Kendi hipotezlerimiz (U4) ve U7 sepet testleri gerçek örneklem dışı değil:** 2026'da tasarlanıp 2023–2026'da
sınandı; o dönemin rejimi bilinerek kurulan hipotez örtük gelecek bilgisi taşır. U7'deki TradingView stratejileri de
sepette **sabit 2023+** dönemiyle sınandı (yazarın yayım tarihi değil). Paper'daki 11 kitap bu aileden.

## 5. Lider bulgusu: paper kitaplarının plasebo sonucu zaten vardı
Eski hunide (`backtests/asama2a.py`, Aşama 2a) rastgele giriş testi var: aynı çıkış kuralları, sembol başına aynı
giriş sayısı, rastgele giriş barları; strateji PF **ve** ortalama R'de null dağılımının %95'ini geçmeli (yalnız IS
dönemi 2018–2022). TEST_YAPISI v2 (2026-10-24) bu hunisi eleyici olmaktan çıkardı. Sonuç (`results/u7/*/huni_ozet.csv`):

| Kitap | IS işlem | IS PF | p (PF) | p (ort R) | Null geçti |
|---|---:|---:|---:|---:|---|
| TV-71yKm18B | 231 | 3,02 | 0,010 | 0,005 | **evet** |
| TV-zoY9DmsF | 172 | 1,62 | 0,056 | 0,043 | hayır (sınırda) |
| TV-egTb7TgJ | 109 | 3,08 | 0,189 | 0,005 | hayır |
| TV-3BXWqwnF | 105 | 2,66 | 0,214 | 0,015 | hayır |
| TV-DUCODGjC | 382 | 1,33 | 0,129 | 0,100 | hayır |
| TV-dpkq3n4O | 163 | 1,81 | 0,129 | 0,398 | hayır |
| TV-Q9OQye4C | 292 | 2,13 | 0,244 | 0,144 | hayır |
| TV-70PkIvTL | 166 | 1,30 | 0,572 | 0,363 | hayır |
| TV-KO7Qe4Xb | 98 | 1,30 | 0,398 | 0,468 | hayır |
| U4-H2 kripto 1G | 53 | 2,73 | 0,687 | 0,403 | hayır |
| U4-H3 emtia 1G | 45 | 1,14 | 0,721 | 0,721 | hayır |

**Yorum:** 11 kitaptan 10'unun girişi, aynı çıkışlarla rastgele girişten anlamlı biçimde iyi değil. Getirileri
büyük olasılıkla çıkış kuralı + piyasa yönünden geliyor (son denetimde bulunan %35–70 piyasa payıyla tutarlı).
G4RNcGXg ve yhoK9cH4 (TV-2) bu testten hiç geçmedi. Bu, yedi yanıtın ana eleştirisinin bizim veride somut karşılığı.

## 6. Lider önerisi
**Paper'a dokunma.** Sanal, maliyetsiz ve karar 26 haftada; erken değişiklik ölçümü bozar. Ama beklenti dürüstçe
güncellenir: bu kitapların çoğu "piyasa + çıkış kuralı" kitabıdır.

**Hemen (Codex, bilgi amaçlı, paper'ı değiştirmez):**
1. **Plasebo kalibrasyonu:** mevcut kapının yanlış geçme oranı (TV-2 ve U7 için, zaman dilimi ve maruziyet kırılımlı).
2. **13 kitap için geriye dönük kontrol:** maruziyet eşleşmiş kıyas, beta ayarlı alfa (NW t), sınama dönemi plasebosu,
   DSR (N_eff ile).
3. **Panoya kıyas bandı:** sağlık matrisine her kitabın canlı sonucunun maruziyet eşleşmiş piyasa kıyası ve rastgele
   giriş bandı eklenir (DeepSeek'in "kontrol grubu" fikrinin maliyetsiz hâli).

**Yeni stratejiler için Kapı v3** (radar, copy trade, ML; kullanıcı onayıyla `docs/TEST_YAPISI.md`'ye):
0. Deneme kayıt defteri + önceden yazılı eşikler.
1. Nedensellik (mevcut) + `lookahead_on`/repaint taraması + ±1 bar kaydırma.
2. 1x maliyette net > 0 (gerekli, yeterli değil); 2x maliyet "kırılgan" etiketi.
3. Örneklem: ≥ 50 işlem ve ≥ 1 yıl, yoksa **Yetersiz** (geçti değil). Seyrek stratejiler sepette test edilir.
4. **Plasebo:** giriş permütasyonu, strateji %95'in üstünde.
5. **Alfa:** maruziyet eşleşmiş kıyasa göre beta ayarlı alfa, NW t ≥ 2 (ML üretimi için ≥ 3).
6. **Çoklu test:** DSR ≥ 0,95 (N_eff), aile için BHY q ≤ %10.
7. Sağlamlık: alt dönemlerin çoğunda pozitif, parametre ±%20'de işaret aynı.
8. Portföy: hiyerarşik kümeleme (sıra bağımlı 0,6 eşiği yerine).
9. Paper: icra doğrulaması + sağlık matrisi (mevcut).
ML için ayrıca: kilitli holdout (tek kullanım), CPCV/PBO < 0,2.

**Kullanıcı kararları:** (a) Kapı v3 yeni stratejiler için kabul mü; (b) "yılda 30 işlem" kuralı v3'te "≥ 50 işlem
toplam + sepet" ile değişsin mi; (c) 26 hafta sonunda 13 kitabın kararı v3 ölçülerini de içersin mi.
