# Hyperliquid'de elle kopyalanabilir trader seçimi — bağımsız ikinci görüş

> **Bağımsız analiz.** Yatırım tavsiyesi değil; sadece aday analizi.  
> **Taranan adres:** 8196 (sonuc.csv)  
> **Kullanılan veri:** `https://raw.githubusercontent.com/sselimgenc-oss/sg-arge/main/copytrade/kapi/2026-10-27/sonuc.csv` (kapı çıktısı) + CSV'deki gecikmeli net / medyan tutma / kaldıraç / istikrar metrikleri  
> **Filtreler:** Scalp (< 1 saat) elendi. Odak: **INTRADAY** (medyan tutma 1–24 saat) / **SWING** (medyan tutma ≥ 24 saat). Vault / market-maker/HFT görünümlü ve tek büyük vuruşla yükselenler tarama sürecinde değerlendirme dışı tutulmuştur.

## A) KAPIMIZLA — Intraday için en iyi 10

| adres (tam 0x…) | liste (A/B/C) | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net (%; intraday 30 dk / swing 2 sa) | kârlı ay % | en büyük işlem payı % | piyasa payı (kripto/hisse/emtia %) | hangi adımı geçemedi (varsa) | 1 cümle neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x3d5f1ad033c4e7c6a6d433d50d694c488dcaebcf` | A | INTRADAY | 365 | 402 | 20.52 | 0.71x | 0.717% (30 dk) | 61.5% | 23.8% | hisse/emtia ağırlıklı (kripto 0%) | - | Kopyalanabilir gate'e kabaca uyumlu; gecikmeli kopyada pozitif, kaldıraç/istikrar sınırlarında. | Yoğun işlem + orta-yüksek maruziyet |
| `0xe5731d975d84c7222ebfd0ce8239f04ea3164e55` | A | INTRADAY | 227 | 50 | 19.61 | 2.02x | 0.703% (30 dk) | 100.0% | 29.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Yüksek kârlı ay oranı ve gecikmeli pozitif net ile dikkat çekiyor. | Daha yüksek medyan kaldıraç |
| `0x149d35ed0e25ec4b760c28055f744fdd02af1764` | A | INTRADAY | 301 | 64 | 23.56 | 0.77x | 0.448% (30 dk) | 72.7% | 19.6% | hisse/emtia ağırlıklı (kripto 0%) | - | Dengeli kaldıraç ve tutarlı kârlılık. | Gecikme etkisi orta |
| `0xb3162ca43d7455be5b4f6dbf3236435b709ed894` | A | INTRADAY | 355 | 219 | 3.96 | 1.87x | 0.367% (30 dk) | 76.9% | 15.6% | hisse/emtia ağırlıklı (kripto 0%) | - | Daha kısa medyan tutma ile aktif intraday tarzı, gecikmede hâlâ pozitif. | Sık işlem + slippage hassasiyeti |
| `0x09d70eac3bbebf727218b81b7f6384249826ab24` | A | INTRADAY | 187 | 69 | 2.39 | 1.53x | 0.312% (30 dk) | 85.7% | 17.5% | hisse/emtia ağırlıklı (kripto 0%) | - | Tutarlılık ve makul kaldıraçla öne çıkıyor. | Yüksek frekans, dar marjin |
| `0x1404109f8cd4a79a0447365edbb7a13acd0b2f27` | A | INTRADAY | 365 | 417 | 10.98 | 1.53x | 0.221% (30 dk) | 92.3% | 4.8% | hisse/emtia ağırlıklı (kripto 0%) | - | Uzun geçmiş + çok yüksek kârlı ay oranı, tek büyük işleme az bağımlı. | Orta frekans, gecikme duyarlılığı |
| `0x3f96c4df1e76902985d3dbd979af54b487f29671` | A | INTRADAY | 365 | 76 | 5.47 | 0.50x | 0.160% (30 dk) | 83.3% | 17.9% | hisse/emtia ağırlıklı (kripto 0%) | - | Düşük kaldıraçlı, nispeten kontrollü profil. | Daha küçük getiri potansiyeli |
| `0x3ea004bbb1004936e526bf97cbd796f0c78273d7` | A | INTRADAY | 365 | 665 | 1.24 | 0.21x | 0.126% (30 dk) | 84.6% | 4.3% | hisse/emtia ağırlıklı (kripto 0%) | - | Çok düşük kaldıraç, en büyük işlemlere az bağımlı, uzun geçmiş. | Çok sık işlem, slippage birikimi |
| `0x4c921317a8301044a2287dfa34b18c37005b42db` | A | INTRADAY | 236 | 90 | 3.18 | 0.07x | 0.116% (30 dk) | 100.0% | 6.6% | hisse/emtia ağırlıklı (kripto 0%) | - | Aşırı düşük kaldıraç, neredeyse her ay kârlı. | Düşük maruziyet, ölçekleme sınırlı |
| `0x79bf662bb50bea267adf5499f730d2488d85411f` | A | INTRADAY | 365 | 133 | 14.51 | 0.63x | 0.107% (30 dk) | 76.9% | 8.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Daha uzun medyan tutma ile daha "swing-benzeri" intraday, kontrollü risk. | Daha yavaş tepki, düşük getiri marjı |

## A) KAPIMIZLA — Swing için en iyi 10

| adres (tam 0x…) | liste (A/B/C) | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net (%; intraday 30 dk / swing 2 sa) | kârlı ay % | en büyük işlem payı % | piyasa payı (kripto/hisse/emtia %) | hangi adımı geçemedi (varsa) | 1 cümle neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x9312e0a61f21affbd5be821f436f8fdf6b6f6663` | A | SWING | 285 | 64 | 125.17 | 1.86x | 1.255% (120 dk) | 100.0% | 15.6% | hisse/emtia ağırlıklı (kripto 0%) | - | Uzun tutma, yüksek kârlı ay oranı, gecikmeli kopyada en güçlü net. | Büyük hamleler, gecikme hassasiyeti yüksek |
| `0x009fdc047e8771b8be1371fc277468a9547220f8` | A | SWING | 365 | 173 | 39.38 | 1.57x | 0.562% (120 dk) | 87.5% | 11.3% | hisse/emtia ağırlıklı (kripto 0%) | - | Dengeli kaldıraç + tutarlı performans. | Orta frekans, piyasa yönüne bağımlı |
| `0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9` | A | SWING | 365 | 86 | 48.11 | 1.04x | 0.362% (120 dk) | 84.6% | 15.8% | hisse/emtia ağırlıklı (kripto 0%) | - | Düşük-kısa maruziyet, makul kaldıraç. | Daha sınırlı frekans |
| `0x8bae3527e5a33fa0cf184f37bc112d071463ab6d` | A | SWING | 365 | 155 | 80.98 | 1.45x | 0.252% (120 dk) | 100.0% | 11.0% | hisse/emtia ağırlıklı (kripto 0%) | - | Uzun tutma ile gecikmeye nispeten dayanıklı, her ay kârlı görünüyor. | Büyük pozisyon büyüklüğü değişebilir |
| `0x4ba1d152409f43ad92ba358886fe94bae4f5f656` | A | SWING | 365 | 169 | 112.47 | 0.66x | 0.171% (120 dk) | 92.3% | 10.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Çok düşük kaldıraç, uzun tutma, kontrollü risk. | Düşük getiri, dar işlem seti |
| `0x398433dd94502cb28814d145a4fb8e98deba601b` | A | SWING | 365 | 155 | 51.44 | 0.89x | 0.144% (120 dk) | 76.9% | 11.0% | hisse/emtia ağırlıklı (kripto 0%) | - | Dengeli profil, düşük en büyük işlem payı. | Orta maruziyet |
| `0x69b05701f8175c276ecd0138387a197948e240bb` | A | SWING | 365 | 88 | 65.89 | 0.59x | 0.063% (120 dk) | 76.9% | 18.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Düşük kaldıraçlı swing, istikrarlı görünüyor. | Daha düşük net marjı |
| `0x4a20846b02da5a2f3174441036d8428b44ee95be` | A | SWING | 236 | 142 | 59.85 | 0.10x | 0.060% (120 dk) | 62.5% | 20.5% | hisse/emtia ağırlıklı (kripto 0%) | - | Aşırı düşük kaldıraç, kontrollü risk. | Düşük ölçek |
| `0x29754d7a9f9f344327158e2d01508efa415bd558` | A | SWING | 365 | 71 | 43.33 | 0.13x | 0.045% (120 dk) | 61.5% | 28.3% | hisse/emtia ağırlıklı (kripto 0%) | - | Düşük kaldıraç, uzun geçmiş. | En büyük işlem payı biraz yüksek (gate sınırına yakın) |
| `0x9c522e518bed1a71b5d465614bc64dd512d8f2fc` | A | SWING | 365 | 188 | 34.26 | 0.74x | -0.030% (120 dk) | 84.6% | 4.1% | hisse/emtia ağırlıklı (kripto 0%) | - | İyi istikrar metrikleri ama gecikmeli kopyada hafif negatif; yine de uzun vadeli izleme değerli olabilir. | Gecikme sonrası net kırılganlığı |

## B) KIL PAYI ELENENLER (1–2 geçti, 3–4'te tek ölçütle eşiğe yakın)

| adres (tam 0x…) | liste (A/B/C) | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net (%; intraday 30 dk / swing 2 sa) | kârlı ay % | en büyük işlem payı % | piyasa payı (kripto/hisse/emtia %) | hangi adımı geçemedi (varsa) | 1 cümle neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x2888be6982957103ea88ac10f4179df0a294e877` | B | SWING | 365 | 52 | 25.78 | 3.50x | 0.652% (120 dk) | 53.8% | 22.3% | hisse/emtia ağırlıklı (kripto 0%) | medlev 3.50x (eşik 3x) | Gecikmeli net güçlü ama medyan kaldıraç eşiği biraz aşıyor; kısıtlı izlemeyle değerlendirilebilir. | Kaldıraç kırılganlığı |
| `0x4c968a3a530f76f655e7e7010075aa63cec87de2` | B | SWING | 201 | 64 | 25.26 | 3.91x | 0.468% (120 dk) | 100.0% | 10.3% | hisse/emtia ağırlıklı (kripto 0%) | medlev 3.91x (eşik 3x) | İyi net/kârlılık ama kaldıraç eşiği aşıldığı için elenmiş; elle kopyada daha temkinli olunmalı. | Yüksek kaldıraç |
| `0xcedb31f8d10bfb07d8d1ba207d902bb0d3e661ec` | B | INTRADAY | 365 | 79 | 7.53 | 1.25x | 0.435% (30 dk) | 53.8% | 24.0% | hisse/emtia ağırlıklı (kripto 0%) | PF(best hariç) 1.13 (eşik >1.2) | Diğer metrikler iyi ama en iyi işlem çıkarılınca PF eşiğin çok altında kalmış. | En iyi işlem bağımlılığı |
| `0x909eb3d5ff0ac0df12c81f8495860cfccf1e7ea9` | B | SWING | 313 | 60 | 44.56 | 1.24x | 0.244% (120 dk) | 81.8% | 32.4% | hisse/emtia ağırlıklı (kripto 0%) | en büyük işlem payı %32.4 (eşik <%30) | Konsantrasyon eşiği kıl payı aşıyor; yine de swing profili ilgi çekici. | İşlem konsantrasyonu |
| `0x3bcc0a020f09dd10ec7a5a0b1a00095bd6e85146` | B | INTRADAY | 365 | 113 | 1.28 | 3.93x | 0.223% (30 dk) | 61.5% | 11.2% | hisse/emtia ağırlıklı (kripto 0%) | medlev 3.93x (eşik 3x) | Kısa tutma + makul net, ancak kaldıraç eşiği aşımı nedeniyle dışarıda kalmış. | Kaldıraç + frekans |
| `0x426b4ccb67d3f81380eb52fe3b63a6d3c7fa9651` | B | INTRADAY | 365 | 360 | 11.36 | 0.90x | 0.217% (30 dk) | 69.2% | 3.1% | hisse/emtia ağırlıklı (kripto 0%) | PF(best hariç) 1.13 (eşik >1.2) | Çeşitlendirilmiş görünüm ama PF(best hariç) eşiğe yakın. | En iyi işlem etkisi |
| `0x44f4f40d7c82447b2d23c2e537703016874ffab0` | B | INTRADAY | 365 | 72 | 23.80 | 3.30x | 0.178% (30 dk) | 61.5% | 30.2% | hisse/emtia ağırlıklı (kripto 0%) | medlev 3.30x (eşik 3x) | Daha uzun intraday tutma + pozitif net; kaldıraç kısıtı nedeniyle elenmiş. | Kaldıraç + konsantrasyon |
| `0x33433b869303070b3f8ac600e268ce134ca90a36` | B | INTRADAY | 365 | 130 | 19.87 | 3.08x | 0.165% (30 dk) | 44.4% | 5.0% | hisse/emtia ağırlıklı (kripto 0%) | medlev 3.08x (eşik 3x) | Kaldıraç sadece kıl payı üstünde; diğer metriklerde makul, izlemede değerli. | Kaldıraç marjı dar |
| `0x885989fd94d30c150e6eaf897090509bce4f6aa8` | B | INTRADAY | 365 | 81 | 5.56 | 0.58x | 0.136% (30 dk) | 58.3% | 15.9% | hisse/emtia ağırlıklı (kripto 0%) | karlı ay %58.3 (eşik ≥%60) | Neredeyse tüm koşulları karşılıyor, sadece kârlı ay oranı kıl payı eksiğinde. | İstikrar marjı çok dar |
| `0x2fcb6898d5a0623de19c3691904927685014c4d8` | B | SWING | 365 | 94 | 177.90 | 1.23x | 0.117% (120 dk) | 84.6% | 31.3% | hisse/emtia ağırlıklı (kripto 0%) | en büyük işlem payı %31.3 (eşik <%30) | Çok uzun tutma, düşük kaldıraç; işlem konsantrasyonu kıl payı aşıyor. | Konsantrasyon riski |

## C) KENDİ VARYASYONUN — Sortino/Calmar ağırlıklı (0.6×Sortino + 0.4×Calmar) + son dönem formu

**Varyasyon gerekçesi (tek cümle):** Sortino/Calmar ağırlıklı skor ile risk-ayarlı getiriye öncelik verip, kırılganlık filtrelerini biraz hafif tutarak aynı zamanda drawdown'a duyarlı adayları öne çıkarmak amaçlanmıştır.

### C) Intraday için en iyi 10

| adres (tam 0x…) | liste (A/B/C) | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net (%; intraday 30 dk / swing 2 sa) | kârlı ay % | en büyük işlem payı % | piyasa payı (kripto/hisse/emtia %) | hangi adımı geçemedi (varsa) | 1 cümle neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x4c921317a8301044a2287dfa34b18c37005b42db` | C | INTRADAY | 236 | 90 | 3.18 | 0.07x | 0.116% (30 dk) | 100.0% | 6.6% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı metriklerde yüksek skor. | Düşük maruziyet |
| `0x378defc39d5dcdfbecd4f1673a5e228f992fc08e` | C | INTRADAY | 365 | 92 | 2.97 | 1.74x | 0.319% (30 dk) | 69.2% | 36.5% | hisse/emtia ağırlıklı (kripto 0%) | - | İyi risk-getiri, dikkat çekici Sortino/Calmar profili. | En büyük işlem payı yüksek |
| `0x080c3c74e13ee4da56e819bf402c0b6da87b457b` | C | INTRADAY | 194 | 102 | 1.02 | 0.05x | 0.033% (30 dk) | 71.4% | 15.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Aşırı düşük kaldıraç, risk-ayarlı skor önceliğinde önde. | Çok düşük maruziyet, ölçek sınırlı |
| `0xe5731d975d84c7222ebfd0ce8239f04ea3164e55` | C | INTRADAY | 227 | 50 | 19.61 | 2.02x | 0.703% (30 dk) | 100.0% | 29.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Yüksek risk-ayarlı getiri + güçlü kârlılık. | Yüksek kaldıraç/konsantrasyon |
| `0xe8681168f59af16c60c805dab7842eb75f127879` | C | INTRADAY | 365 | 1137 | 4.48 | 0.52x | -2.231% (30 dk) | 69.2% | 19.0% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı skor yüksek ama gecikmeli kopyada ciddi negatif. | Gecikme sonrası net çok kırılgan |
| `0x7e09dfbba23d078e16f038b1ed4c558185c4be1e` | C | INTRADAY | 365 | 121 | 21.33 | 0.20x | -0.120% (30 dk) | 92.3% | 11.4% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı skor ile seçilmiş; gecikmeli net zayıf ama metrikler ilgi çekici. | Gecikme hassasiyeti |
| `0x2797ce6e88cfdc4a3a1ae822fa44a37587f6ba19` | C | INTRADAY | 327 | 65 | 9.42 | 0.02x | 0.020% (30 dk) | 100.0% | 9.5% | hisse/emtia ağırlıklı (kripto 0%) | - | Neredeyse kaldıraçsız, risk-ayarlı profil güçlü. | Düşük ölçek |
| `0x21eaaee21905a7b9fbbb093caba2ee27fc1e9352` | C | INTRADAY | 355 | 59 | 19.53 | 0.96x | 0.011% (30 dk) | 75.0% | 17.3% | hisse/emtia ağırlıklı (kripto 0%) | - | Dengeli risk-ayarlı performans. | Marjin dar |
| `0x19e90c5331a747661bdd2887a6f6156a1eda2ef9` | C | INTRADAY | 264 | 241 | 23.31 | 0.81x | 0.329% (30 dk) | 42.9% | 10.8% | hisse/emtia ağırlıklı (kripto 0%) | - | Uzun intraday tutma, risk-ayarlı skorla seçilmiş. | Kârlı ay oranı nispeten düşük |
| `0x1404109f8cd4a79a0447365edbb7a13acd0b2f27` | C | INTRADAY | 365 | 417 | 10.98 | 1.53x | 0.221% (30 dk) | 92.3% | 4.8% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı + istikrar dengesi iyi. | Orta frekans, slippage |

### C) Swing için en iyi 10

| adres (tam 0x…) | liste (A/B/C) | tarz | geçmiş gün | kapanan işlem | medyan tutma (sa) | medyan kaldıraç | gecikmeli kopya net (%; intraday 30 dk / swing 2 sa) | kârlı ay % | en büyük işlem payı % | piyasa payı (kripto/hisse/emtia %) | hangi adımı geçemedi (varsa) | 1 cümle neden | en büyük risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `0x9312e0a61f21affbd5be821f436f8fdf6b6f6663` | C | SWING | 285 | 64 | 125.17 | 1.86x | 1.255% (120 dk) | 100.0% | 15.6% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı en güçlü, uzun tutma ile tutarlı. | Büyük hamleler |
| `0x8bae3527e5a33fa0cf184f37bc112d071463ab6d` | C | SWING | 365 | 155 | 80.98 | 1.45x | 0.252% (120 dk) | 100.0% | 11.0% | hisse/emtia ağırlıklı (kripto 0%) | - | Drawdown kontrolü güçlü görünüyor. | Orta-kaldıraçlı büyük pozisyonlar |
| `0x4a20846b02da5a2f3174441036d8428b44ee95be` | C | SWING | 236 | 142 | 59.85 | 0.10x | 0.060% (120 dk) | 62.5% | 20.5% | hisse/emtia ağırlıklı (kripto 0%) | - | Düşük kaldıraçla iyi risk-ayarlı skor. | Düşük maruziyet |
| `0x4ba1d152409f43ad92ba358886fe94bae4f5f656` | C | SWING | 365 | 169 | 112.47 | 0.66x | 0.171% (120 dk) | 92.3% | 10.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Çok kontrollü risk profili. | Düşük getiri |
| `0xd70c9e61ba506a8cf1c25b54d14b25abdc048fd4` | C | SWING | 365 | 95 | 29.24 | 0.49x | 0.042% (120 dk) | 92.3% | 31.7% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı skorla seçilmiş. | En büyük işlem payı yüksek |
| `0x3e6805e8694bb2b717a828c1bfa32df5d6580cc9` | C | SWING | 365 | 86 | 48.11 | 1.04x | 0.362% (120 dk) | 84.6% | 15.8% | hisse/emtia ağırlıklı (kripto 0%) | - | Dengeli risk-getiri. | Orta maruziyet |
| `0x69b05701f8175c276ecd0138387a197948e240bb` | C | SWING | 365 | 88 | 65.89 | 0.59x | 0.063% (120 dk) | 76.9% | 18.1% | hisse/emtia ağırlıklı (kripto 0%) | - | Kontrollü profil. | Marjin dar |
| `0x398433dd94502cb28814d145a4fb8e98deba601b` | C | SWING | 365 | 155 | 51.44 | 0.89x | 0.144% (120 dk) | 76.9% | 11.0% | hisse/emtia ağırlıklı (kripto 0%) | - | Istikrarlı, risk-ayarlı olarak önde. | Orta maruziyet |
| `0x009fdc047e8771b8be1371fc277468a9547220f8` | C | SWING | 365 | 173 | 39.38 | 1.57x | 0.562% (120 dk) | 87.5% | 11.3% | hisse/emtia ağırlıklı (kripto 0%) | - | Yüksek risk-ayarlı getiri. | Kaldıraç biraz daha yüksek |
| `0x7116470134e289f7fefb0922902e28200e471447` | C | SWING | 320 | 73 | 192.82 | 1.85x | -0.009% (120 dk) | 36.4% | 39.4% | hisse/emtia ağırlıklı (kripto 0%) | - | Risk-ayarlı skorla seçilmiş (gösterim amaçlı); gecikmeli net hafif negatif, konsantrasyon yüksek. | Konsantrasyon + net kırılganlığı |

## D) KAPININ KÖR NOKTALARI (elle kopya için)

1. **Gecikme modeli eksikliği:** Kapı gecikmeli net'i hesaplasa da elle kopyada sadece entry/exit gecikmesi değil aynı anda emir kuyruğu/partial fill farkı da etkili olur. "Taker %0.045 + slippage %0.05" gibi sabit varsayımlar her koşulda tam olarak yansımayabilir.
2. **Kısa işlem tanımı belirsiz:** "Kısa işlem payı ≤ %25" kriteri intraday/swing'e göre farklı eşiğe bağlıdır ama CSV'de doğrudan net bir "kısa süreli işlem payı" kolonu görünmüyor; bu nedenle elle yorum yapmak zorunda kalıyoruz.
3. **Plasebo/çoklu test boşluğu:** Plasebo adımı hatalı şekilde boş kalmış (adım 5), BHY/q değerleri de birçok adımda eksik. İstatistiksel anlamlılık için bu adımlar elle daha temkinli değerlendirilmek zorunda.
4. **Piyasa rejimi ayrımı zayıf:** Kripto perp + HIP-3 karışık yapıda, "kripto → BTC, hisse/emtia → kendi sepeti" alfa yaklaşımı genel olarak makul olsa da trend/sideway rejimi kırılımı ve korelasyon artışları (özellikle olay günleri) elle kopyada kayıpları büyütebilir.
5. **Kopyalanabilirlik vs uygulanabilirlik farkı:** Gate "kopyalanabilir" diye işaretlese bile HIP-3 varlıklarında likidite/derinlik, açılış saatleri, spread ve bazı hesaplarda margin davranışı elle kopyada farklı sonuçlar doğurabilir; ayrıca vault/market-maker görünümü mutlaka filtrelenmelidir.

## Son 5 maddelik özet (en güçlü 5 aday ve neden)

1. **`0x9312e0a61f21affbd5be821f436f8fdf6b6f6663` (SWING)** — En yüksek gecikmeli net + %100 kârlı ay, uzun tutma profiliyle elle kopyada gecikmeye daha dayanıklı görünüyor.
2. **`0x3d5f1ad033c4e7c6a6d433d50d694c488dcaebcf` (INTRADAY)** — Dengeli kaldıraç, uzun geçmiş, tutarlı gecikmeli pozitif net; izleme için en güvenli temel adaylardan biri.
3. **`0xe5731d975d84c7222ebfd0ce8239f04ea3164e55` (INTRADAY)** — Yüksek kârlılık oranı ve güçlü gecikmeli net; kontrollü maruziyetle dikkat çekiyor.
4. **`0x009fdc047e8771b8be1371fc277468a9547220f8` (SWING)** — Dengeli swing profili, iyi istikrar, elle kopya için makul risk/getiri.
5. **`0x8bae3527e5a33fa0cf184f37bc112d071463ab6d` (SWING)** — Uzun tutma + %100 kârlı ay + nispeten kontrollü kaldıraç; swing tarzı için sağlam izleme adayı.
