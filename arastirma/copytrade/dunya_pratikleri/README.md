# Dünyada copy trade seçimi, backtest ve forward test — üç rapor ve lider analizi (2026-10-28)

Kullanıcı aynı soruyu üç modele sordu (Sonnet, Codex, Opus); PDF'ler metne çevrildi, kişi adı çıkarıldı (`rapor_*.md`).
**Kaynaklar lider tarafından açılıp doğrulanmadı**; sayılar yön gösterir. Doğrulama işi: `docs/GOREV_ARGON_2.md` A6.

## Bizi doğrulayanlar (zaten yapıyoruz)
| Dünya pratiği / bulgu | Bizde |
|---|---|
| Liderlerin ~%97'si kendi hesabında kârlı, takipçisine kâr ettiren ~%44 (YieldFund, 90 gün) | Kapı trader'ı değil, **gecikme + maliyet sonrası kopya getirisini** ölçüyor (`defter.copy_ledger`) |
| Seçim ve test dönemini ayır (walk-forward) | Faz 3 yürüyen pencere; canlı gölgede yalnız etiketten sonrası sayılır |
| Hayatta kalan yanlılığı | Elenen adres kayıttan silinmez; geçmiş evren için HF verisi doğrulanıyor |
| Binlerce adaydan seçim → Deflated Sharpe | Kapıda DSR, N_eff, plasebo |
| Ön kayıtlı karar + kontrol grubu (Etre "Keşif" paneli de aynı mantık) | `ONKAYIT_D`, kohort ↔ rastgele kontrol, tohum kayıtlı |
| Scalp kopyalanamaz | Tarz: < 1 sa scalp adım 3'te kalır; tarz gecikmesi 30/120 dk |
| Martingale/zarara ekleme, vault/alt hesap eleme | Kapı martingale ölçütü; kırmızı bayraklar (rol, vault oranı, alt hesap ters) |
| Giriş fiyat bandı (%1) | V1 bandı (intraday %1, swing %2) |
| Rotasyonda histerezis | Terfi: 3 hafta + 10 işlem; çıkış: aday katının alt yarısı |
| Simülasyon ve canlı aynı kod | Tek defter (plasebo, kapı, gölge) |
| Oyunlaştırma süreci puanlamalı, PnL'i değil | Ofis sürüm 2 sentezi: kâr rozeti/renk yok, performans körlüğü |

## Beklentiyi düzelten bulgular
- **Hyperliquid kalıcılık çalışması** (Dennim89, 389 hesap, ön kayıtlı): ardışık 30 günlük bloklarda sıralama korelasyonu
  +0,54 / 0,00 / −0,44 — beceri kalıcılığı zayıf ve rejime bağlı. Argon A3 güç hesabıyla aynı yön: 12 haftada küçük fark
  görülemez; "belirsiz" sonuç olası. Kontrol grubunun neden şart olduğunu da gösteriyor.
- Laboratuvar/saha: sıralamanın tepesi en çok risk alanı seçer (Apesteguia vd.); takipçi artınca trader kötüleşir (Xu vd.).
  Bizim puan zaten ham PnL değil, kopya getirisi; yine de "taban" kolu (leaderboard ilk N) bunu ölçecek.

## Açıklarımız ve öneriler (hiçbiri dondurulmuş yöntemi değiştirmez; bilgi amaçlı ya da sonraki faz)
1. **Kopya verimi** = gölge getirisi / trader'ın aynı dönem getirisi. Oda tablosuna bilgi sütunu. (Sonnet, seçim sonrası)
2. **Minimum emir:** Hyperliquid'de ~10 $ altı emir yok. Küçük sermayede trader'ın küçük dolumları hiç kopyalanamaz. Bilgi
   sütunu: trader başına 200 $ ve 1.000 $ sermayede min emrin altında kalan dolum oranı. Gerçek sermaye kararı kullanıcının.
3. **Stil kayması:** son 30 gün medyan kaldıraç / önceki medyan, işlemsiz gün sayısı. Canlı izlemede bilgi bayrağı (çıkış kuralı
   değil; kural yapmak kullanıcı kararı).
4. **Faz 3 raporuna:** (a) pencere başına **kalıcılık** (etiket dönemi puanı ↔ sonraki 60 gün kopya getirisi sıra korelasyonu);
   (b) **rejim kırılımı** (BTC 30 gün getirisi ve oynaklığına göre yükseliş/düşüş/yatay/şok). Kalıcılık çalışmasıyla doğrudan
   karşılaştırılabilir.
5. **Bütünlük bayrakları:** wash trade, hesaplar arası işlem, birlikte işlem yapan kümeler (hl-leaderboard'un yöntemi). Önce
   Argon A6 ile yöntem ve lisans doğrulanır.
6. **Gerçek paraya geçiş ön koşulları (taslak, ileride kullanıcı kararı):** kasa düzeyinde net yön (long/short) limiti ve günlük
   zarar limiti; trader başına sermaye tavanı; min emir ve lot/tick yuvarlama; önce hedefin %5–10'u ile 2–4 hafta küçük
   sermaye; canlı ↔ gölge farkının kalem kalem ayrıştırılması (ücret, kayma, zamanlama, kısmi dolum, funding).

## Almadıklarımız
- Sektör eşikleri (Sharpe > 1,5, MDD < %20, kârlı ay > %65, "kopya verimi < %60 → çık"): kaynakları doğrulanmadı, verimize
  göre kalibre değil; eşik koymak kullanıcı kararı ve ön kayıt gerektirir.
- "Ters kopyalama" (Copin): ayrı bir hipotez; şimdi kapsam dışı.
- Davranış kohortunun "+%50" iddiası: firma beyanı, denetlenmemiş.
