# ChatGPT paketi T35 parti 2: Avrupa + Amerika strateji toplama

(Codex bulut ortamı açılmadığı için bu kol ChatGPT sohbetinde, web aramasıyla yapılıyor. Paket kendi içinde tamdır; repo erişimi gerekmez. Faz 1 tekrar kontrolünü lider yapar.)

Merhaba. Bir ekip olarak trading stratejisi araştırıyoruz. Senin kolun **Avrupa ve Amerika**.

## Amaç
Yazarının **rakamla** kârlı olduğunu iddia ettiği scalp, day ve swing stratejilerini, yazarın kendi piyasasıyla birlikte kaydetmek. **Backtest yapma, kod yazma.** Yalnız bul, oku ve kaydet.

## Hedef: 10-12 kayıt
- En az 3'ü scalp ya da day olsun: DAX/ES/NQ açılış, Euro Stoxx, MOEX vadeli, FTSE gibi.
- **arXiv/SSRN en fazla 2 kayıt**, yalnız mekanik kurallı olanlar. Yapay zekâ/ML modeli (LSTM, derin öğrenme, pekiştirmeli öğrenme) alma.

## Kaynaklar (sırayla dene)
- **Avrupa:**
  - smart-lab.ru (Rusça)
  - wallstreet-online.de ve trader-forum (Almanca)
  - ABC Bourse forum ve Zone Bourse (Fransızca)
  - X-Trader.net (İspanyolca)
  - Investire.biz ve FinanzaOnline (İtalyanca)
  - Trade2Win (İngiltere)
- **Amerika:**
  - AmiBroker AFL Library
  - TradeStation / EasyLanguage forumları
  - BabyPips
  - Myfxbook (doğrulanmış hesap ve açıklanmış strateji)
  - futures.io

**Kullanma:** TradingView, ProRealCode, MQL5, ForexFactory, QuantifiedStrategies, NinjaTrader, Collective2, Elite Trader, QuantConnect. Bunları daha önce taradık.
**Connors RSI2 ailesi de alınmaz;** bizde var.

## Kayıt kapısı: kayıt yalnız şu durumda girer
1. En az bir performans rakamı (PF, kazanma oranı, getiri, Sharpe, max düşüş) **ve** test dönemi yazılı. İşlem sayısı yoksa kayıt girer, kırmızı bayrağa `islem_sayisi_yok` yazılır.
2. Strateji açıklanmış: en az bir paragraf ya da kod. Kurs, sinyal ya da bot satışı reklamı girmez.

## Kurallar
- **Uydurma yok.** Sayfada okumadığın rakamı yazma, boş bırak. Arama sonucu özetinden rakam alma; sayfayı açıp oku.
- **`iddia_pf` yalnız profit factor.** Brüt kâr / brüt zarar. Kâr/zarar oranı ya da ortalama kazanç/kayıp gibi metrikleri `not` alanına birimiyle yaz.
- **Al-tut kıyası:** Yazar al-tut ya da endeks getirisini veriyorsa `not`'a yaz. Strateji al-tutun altındaysa `kirmizi_bayrak`'a `al_tut_altinda` ekle.
- **Deney başına satır:** Aynı strateji farklı piyasa ya da parametreyle ayrı sonuç vermişse ayrı satır aç: `EU-007a`, `EU-007b`.
- Giriş/çıkış kuralını orijinal dilde kısa bir alıntıyla da ver (`orijinal_alinti`).
- **Kırmızı bayraklar atılmaz, işaretlenir:** `islem_sayisi_yok`, `az_islem(<30)`, `pf_gt_4`, `maliyet_yok`, `kisa_donem(<1yil)`, `yalniz_ekran_goruntusu`, `iterasyon_izi`.

## Çıktı
**CSV** (virgüllü, metin alanları tırnak içinde), şu sütunlarla. Uymayanı boş bırak:

`id,ad,ad_orijinal,tur,ulke_bolge,dil,platform,url,yazar,yayin_tarihi,piyasa,enstruman,veri_kodu,zaman_dilimi,ozet,giris,cikis,stop,orijinal_alinti,kod_dili,kod_link,kural_tam,iddia_donem,iddia_islem,iddia_wr,iddia_pf,iddia_getiri,iddia_mdd,iddia_sharpe,iddia_turu,maliyet_dahil,referans_turu,dogrulama,kanit_notu,erisim,kirmizi_bayrak,not`

**Değer listeleri:**
- `id`: Avrupa `EU-011`'den, Amerika `US-005`'ten başlar.
- `tur`: scalp (1 saatin altı) / day / swing / belirsiz
- `kural_tam`: evet / kismen / hayir
- `iddia_turu`: backtest / canli / forward / karisik
- `maliyet_dahil`: evet / hayir / belirtilmemis
- `referans_turu`: forum / blog / kod_deposu / platform_raporu / canli_hesap / makale
- `dogrulama`: platform_dogrulamali (Myfxbook gibi) / yazar_beyani
- `erisim`: acik / giris_gerekli / ucretli
- `veri_kodu`: biliyorsan, ör. `FDAX`, `ES`, `^GDAXI`, `SBER.ME`.

**CSV'nin altına ikinci bölüm olarak bir erişim tablosu ekle:**
- denediğin her site;
- denenen sayfa;
- sonuç: açıldı / 403 / giriş gerekiyor / rakamlı içerik yok.

Son olarak kapıdan dönen yaklaşık aday sayısını ve en sık dönme nedenini yaz.
