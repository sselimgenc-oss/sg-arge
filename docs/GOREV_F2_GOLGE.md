# F2-GÖLGE: Kripto 4H trend gölge kitabı (canlı, paper)

**Karar:** kullanıcı, 2026-10-24. `results/U4_SONUC.md` bölüm 3, seçenek (b).
**Sahip:** Codex. **Denetim:** lider.

## Amaç
U4'te kripto 4H trend kartı U4-H1 IS ve OOS'ta kârlıydı ama kapılarda elendi (MDD95 %28, DSR, kardeş). Kilitli dönemi harcamadan, kartı **canlı veride, ana portföyden ayrı bir gölge kitapta** izlemek.

## Tanım (sabit; sonuca bakılarak değişmez)
- **Kart:** `U4-H1`, değiştirilmeden. `tf: 4H`, 1H Binance verisinden UTC 00/04/08/12/16/20 kovalarıyla.
- **Evren:** yalnız çekirdek 6 coin: BTC, ETH, SOL, BNB, XRP, TRX (USDT, spot).
- **Boyut:** işlem başı risk **%0,25** (ana portföyün yarısı), toplam açık risk %1, kitap brütü %100, kaldıraç yok.
- **Maliyet:** tek yön %0,15 (KRIPTO25).
- **Sermaye:** ayrı, 5.000 USD sanal. **Ana portföy özkaynağına, alarmlarına ve DURDUR kuralına karışmaz.**
- **Başlangıç:** kitap **canlı başlar** (`baslangic` = birleştirme günü, UTC). **Geriye dönük doldurma yapılmaz:** 2025-10-01 sonrası kilitli dönemdir; orayı doldurmak kilidi dolaylı yoldan açmak olur. Göstergelerin ısınması için geçmiş veri kullanılır, işlem açılmaz.
- **Alarm (yalnız bilgi):** gölge kitap MDD ≥ %15 olursa panoda uyarı. Durdurma kararı kullanıcınındır.

## Yapılacaklar (Codex)
1. `paper/portfoy.yaml`'a ayrı bir `golge:` bölümü. Örnek: `{id: U4-H1, piyasa: KRIPTO25, tf: 4H, semboller: [...6...], risk: 0.0025, sermaye: 5000, baslangic: <gün>}`. `gunluk.py` bu bölümü ana satırlardan **ayrı** koşar ve ayrı deftere yazar: `paper/defter/golge/*.csv`, aynı ekleme-yalnız kurallar.
2. **Veri:** kripto 1H Binance (`data/fetch.py`, `--append`). Saatlik koşuda yalnız 6 coin indirilir.
3. **Yarım bar koruması (4H):** içinde bulunulan 4 saatlik kova kapanmadan o 4H bar kullanılmaz. Kova kapanışı + 5 dk sonrası kapanmış sayılır. Test zorunlu: kova içi bir saatte son 4H barın atıldığını, kapanıştan sonra kullanıldığını doğrula.
4. **Pano:** `paper/panel.py` `data.json`'a ayrı bir `golge` anahtarı ekler: özkaynak, açık pozisyonlar, kapanmış işlemler, MDD, başlangıç tarihi ve "gölge kitap: ana portföyden ayrı, kilitli dönem kullanılmadı" notu. Ana `kpis` değişmez.
5. `paper.yml` aynı saatlik iş içinde gölge kitabı da koşar. Süre sınırı 10 dk aşılmamalı.

## Kabul
- `pytest -q` tamamı geçer. Yeni testler: yarım 4H bar, ayrı defter, ana özkaynağa etki yok, geriye dönük işlem yok (başlangıçtan önce dolum yok).
- Yerel prova: gölge kitap boş defterle başlar; ilk koşuda yalnız başlangıç sonrası barlar işlenir.
- PR `[F2] gölge kitap: kripto 4H trend`. Açıklamada prova çıktısı.

## Pano reposu (lider)
`sg-pano/index.html`'e "Gölge kitap" sekmesi lider tarafından eklenir: `data.json` `golge` anahtarı, ana portföyden ayrı gösterilir.

## Ek 2: üç stratejili gölge kitap, 2026-09-01'den (kullanıcı kararı, 2026-10-24)
**Karar:** kullanıcı: "T8-07 ve V2B'yi gölge kitaba al; gölgedeki 3 stratejiyi 1 Eylül'den itibaren koştur." Bu ek yukarıdaki "geriye dönük doldurma yapılmaz" maddesinin yerine geçer. Sonuç görülmeden yazıldı.

### Kitaplar (sabit; sonuca bakılarak değişmez)
| Kitap | Kart | Piyasa / tf | Evren | Kaynak |
|---|---|---|---|---|
| U4-H1 | `U4-H1`, değiştirilmeden | KRIPTO25 / 4H | çekirdek 6 coin (yukarıdaki gibi) | U4, seçenek b |
| T8-07 | `T8-07`, değiştirilmeden | EMTIA / 1H | Faz 1 Aşama 2b'deki EMTIA evreni aynen | Faz 1 Koşullu (ön dönem yok) |
| V2B | `V2B`, değiştirilmeden | EMTIA / 1H | Faz 1 Aşama 2b'deki EMTIA evreni aynen | Faz 1 Koşullu (ön dönem yok) |

- Her kitap **ayrı**: 5.000 USD sanal sermaye, işlem başı risk %0,25, toplam açık risk %1, kaldıraç yok, maliyet `tarama.BASE_COST` (KRIPTO25 %0,15, EMTIA %0,05). Kitaplar birbirine ve ana portföye karışmaz.
- **Dönem:** `baslangic: 2026-09-01` (geriye dönük, aynı kurallar, gerçek veri), `canli_baslangic: 2026-10-24`. Ana portföyle aynı düzen.
- **Yarım bar koruması:** 4H kitapta mevcut kural; 1H kitaplarda içinde bulunulan saat kapanmadan (kapanış + 5 dk) o 1H bar kullanılmaz.

### Kilit notu (dürüstlük kaydı)
2026-09-01 → 2026-10-23 aralığı kilitli dönemin (2025-10-01 →) içindedir. Bu üç kartın bu aralıktaki sonucu görüleceği için **bu üç kart ileride temiz bir kilitli dönem testine giremez**; değerlendirmeleri yalnız canlı paper ile yapılır. Kilit başka kartlar (U6 adayları) için geçerliliğini korur.

### Değerlendirme kuralı (önceden yazıldı)
- **Yalnız canlı dönem sayılır** (2026-10-24 →). Geriye dönük kısım panoda ayrı etiketle gösterilir, kararda kullanılmaz.
- Herhangi bir anda kitap MDD ≥ %15 → panoda uyarı, lider kitaptan çıkarmayı önerir.
- 6 ay canlı (2027-04-24) sonunda: net > 0 **ve** PF ≥ 1,1 **ve** ≥ 20 kapanmış işlem → lider ana portföye almayı önerir. Değilse gölgede kalır ya da çıkar. Karar kullanıcınındır.

### Yapılacaklar (Codex)
1. `paper/portfoy.yaml` `golge:` bölümü kitap listesine dönüşür (her kitapta `id, piyasa, tf, semboller|evren, risk, sermaye, baslangic, canli_baslangic`).
2. Defter: `paper/defter/golge/<kitap_id>/*.csv`, ekleme-yalnız. Mevcut U4-H1 gölge defteri (2026-10-24'ten) **bir kez** silinip 2026-09-01'den yeniden kurulur; PR açıklamasında belirtilir.
3. Veri: EMTIA 1H yfinance (`60m`, son 730 gün içinde kalır). Göstergelerin ısınması için başlangıçtan önceki veri kullanılır, işlem açılmaz.
4. Özkaynak gün içi işlemleri yansıtır (saatlik/4H çözünürlük ya da dolumlardan); mevcut "[F2] gölge özkaynak saatlik" işi buna dahildir.
5. `data.json` `golge` anahtarı: `{"not": ..., "kitaplar": [{id, piyasa, tf, baslangic, canli_baslangic, ozkaynak, mdd, mdd_uyari, acik_pozisyonlar, kapanmis_islemler, ozkaynak_serisi}]}`. Ana `kpis` değişmez. Pano sekmesini lider günceller.
6. Saatlik iş 10 dk sınırını aşmaz.

### Kabul
- `pytest -q` tamamı geçer. Yeni testler: 1H yarım bar, kitaplar arası ayrılık (bir kitabın işlemi diğerinin özkaynağını değiştirmez), ana defter biçimi ve paritesi değişmez, `baslangic` öncesi dolum yok, gün içi kapanan işlem özkaynağa yansır.
- Yerel prova: üç kitap 2026-09-01'den kurulur; PR açıklamasında kitap başına işlem sayısı ve son özkaynak (yalnız prova kanıtı, karar için değil).
- PR `[F2] gölge kitap: 3 strateji, 2026-09-01'den`.

## Ek 3 (kullanıcı onayı, 2026-10-24): test yapısı v2
- Gölge kitaplar `docs/TEST_YAPISI.md` Adım 4-5'e göre yönetilir; kapasite 20 kitap.
- **Durdurma:** kitap başlangıç sanal sermayesinin %10'unu kaybederse durur. MDD ≥ %15 uyarısı bilgi olarak kalır.
- **İlerleme:** Ek 2'deki "6 ay, PF ≥ 1,1, ≥ 20 işlem" kuralının yerine Adım 5 (aylık kontrol, canlı haftalık getiriler, kalibre edilmiş eşik). Mevcut 3 kitapta yine yalnız canlı dönem (2026-10-24 →) sayılır.
- **Deneme kaydı:** `results/canli/denemeler.csv`; mevcut 3 kitap ilk satırlardır.
- **Sanal havuz:** ayrı iş, ayrı görev (lider tanımlar).
