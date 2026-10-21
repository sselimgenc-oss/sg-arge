# Paper Trading Aday Eleme Kriterleri (v0.1 - Opus denetimine açık)

Hedef: BIST30, ABD, Kripto ve Emtia'da day trade + swing; temel mod long-only, kısa/kaldıraç (x2, x3) ayrı test edilen opsiyon.

## Kanıt seviyeleri
| Seviye | Anlam | Örnek |
|---|---|---|
| A | OOS + 2x/3x maliyet + 1 bar gecikme stresi geçmiş, kurallar tam | Codex Algo 21 portföy |
| B | Çok piyasalı backtest var ama OOS/stres testi yok, optimizasyon izi var | Paper_Test_4/8, Reddit, Voltran |
| C | Yalnız yayıncının beyanı, doğrulanmamış | guncellenmis_strateji_listesi, xlsx |

## Kapılar (hepsi gerekli)
1. Kurallar tam ve kodlanabilir (giriş, çıkış, stop, boyut, MTF kuralı).
2. Bağımsız yeniden üretim: Codex, kendi veri çekimi ile raporlanan PF/getiriyi +-%25 içinde tekrar üretmeli. Üretilemezse aday düşer.
3. Maliyet stresi: 2x ve 3x maliyette PF >= 1,2; +1 bar gecikmede pozitif.
4. OOS: veri son %30'u (veya >= 2 yıl) ayrı tutulur; OOS PF >= 1,1.
5. Örneklem: >= 100 işlem (swing için >= 60), tek enstrümana bağlı olmamak (en iyi işlem/enstrüman çıkarılınca pozitif).
6. Şüpheli iddia alarmı: PF > 4 veya net getiri > %500 -> otomatik "aşırı uyum şüphesi", ek doğrulama zorunlu (walk-forward, parametre komşuluk testi).
7. Kaldıraç/short: yalnız kapı 2-5 temel modda geçildikten sonra ayrı varyant olarak test edilir. Kaldıraçta MDD sınırı %25, tasfiye/marjin simülasyonu zorunlu.
8. Paper trading uygunluğu: sinyal bar kapanışında, emir sonraki bar açılışında; broker/API'ye eşlenebilir.

## Çıktı
Paper'a giren 3-6 strateji; her biri için: kural kartı, parametreler, piyasa listesi, risk limiti (işlem başı %0,5, toplam açık risk %2), kill-switch (paper'da MDD %10).
