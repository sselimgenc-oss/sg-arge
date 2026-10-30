# Veri sözleşmesi — copy trade izleme (v1.5, 2026-10-28; v1.5 `kol`, v1.2 olay kimliği, v1.3 tarz, v1.4 veri geçerliliği ve karar gizliliği)

Üretici: **Codex** (sg-arge). Tüketici: **Sonnet** (sg-pano panosu) ve Telegram bildirimi. İkisi de yalnız bu
sözleşmeye göre çalışır; alan eklemek/değiştirmek lider onayıyla `surum` artırılarak yapılır.

## 1. Dosyalar ve yer
| Dosya | Nerede | Kim yazar | Sıklık |
|---|---|---|---|
| `izleme/durum.json` | sg-arge, `copytrade-izleme` dalı (main büyümesin) | Codex işi (Actions) | saatte bir |
| `izleme/ornek_durum.json` | sg-arge `main` (sabit örnek, 4 trader) | lider (hazır) | sabit; Sonnet bununla başlar |
| `izleme/kararlar.jsonl` (açtım/atladım) | sg-arge, `copytrade-izleme` dalı | saatlik iş, Worker'ın `GET /kararlar`'ından (Cloudflare'de GitHub anahtarı yok) | saatte bir |

Repolar herkese açık (kullanıcı kararı 2026-10-27). Bu yüzden karar kaydında **tutar, bakiye, hesap, isim yoktur**;
yalnız olay kimliği, karar ve neden. Trader adresleri zaten herkese açık zincir verisidir.

## 2. `durum.json` şeması
```json
{
  "surum": 1,
  "uretildi": "2026-10-27T14:20:00Z",
  "kaynak": "hyperliquid",
  "traderlar": [
    {
      "id": "T1",
      "adres": "0x378d…8e",
      "takma_ad": "Trader-1",
      "durum": "kopyala | izlemede | durdu",
      "t0": "2026-10-28",
      "veri_zamani": "2026-10-28T10:00:00Z",
      "gecerli": true,
      "kapi": {"sinif": "Geçti | Yetersiz | Kaldı", "tarih": "2026-10-27", "not": "en büyük işlem payı %36"},
      "saglik": {"isik": "yesil | sari | kirmizi", "nedenler": ["konide", "kaldıraç normal"]},
      "form": {"skor": 0.8, "getiri_30g": 0.042, "getiri_90g": 0.11},
      "hesap_degeri": 139680,
      "pozisyonlar": [
        {"coin": "BTC", "sinif": "kripto", "yon": "long", "giris": 68400.0, "buyukluk_usd": 11200,
         "hesap_payi": 0.08, "kaldirac": 2.0, "anlik_kz_usd": 310, "acilis": "2026-10-27T09:12:00Z",
         "binance": "var | yok | bilinmiyor"}
      ],
      "son_islem": {"coin": "ETH", "yon": "short", "acilis": "…", "kapanis": "…", "net_yuzde": 0.012},
      "egri": [["2026-08-01", 0.0], ["2026-08-02", 0.004]],
      "sanal_kopya": {"baslangic_usd": 1000, "bakiye_usd": 1043, "getiri": 0.043, "dusus": 0.021,
                      "gecikme_dk": 30, "t0": "2026-10-28",
                      "egri": [["2026-10-28", 1000.0], ["2026-10-29", 1004.2]]}
    }
  ],
  "olaylar": [
    {"id": "T1-20261027T091200-BTC-acilis", "zaman": "2026-10-27T09:12:00Z", "trader": "T1",
     "tur": "acilis | kapanis | buyutme | azaltma | isik", "coin": "BTC", "yon": "long", "fiyat": 68400.0,
     "hesap_payi": 0.08, "kaldirac": 2.0, "not": "",
     "sanal_sonuc": {"durum": "acik | kapandi", "net_yuzde": null, "kapanis": null}}
  ]
}
```
- `egri`: son 90 gün, günlük, t0'dan bağımsız trader'ın kümülatif PnL / hesap değeri (Hyperliquid `portfolio`).
- `olaylar` (v1.6): **kol başına** son 200 olay (kolların birleşimi), yeniden eskiye; yoğun bir taban trader'ı oda olaylarını
  düşüremez. Kesilmemiş tüm olaylar `olaylar/YYYY-MM-DDTHH.jsonl.gz` dosyalarında (saat UTC; gzip JSONL, eskiden yeniye, satır = olay; `sanal_sonuc` hariç, o türetilmiştir). Geçmiş saat dosyaları değişmez.
- `gunluk_sayac` (v1.6): son 30 gün, `{gun (UTC, YYYY-MM-DD), kol (ana etiket), acilis, kapanis (olay sayısı), trader_sayisi}`;
  `buyutme`/`azaltma`/`isik` sayılmaz; kesilmemiş olaylardan hesaplanır.
- `sanal_kopya.fiyatsiz_eylem` (v1.6, sayı) ve `fiyatsiz_coinler` (liste): yürütme fiyatı (1 dk/1 sa mum) bulunamayan kopya eylemleri.
  Fiyatlanamayan eylemler sanal defter dışı bırakılır, `not`: "fiyatsız eylem";
  diğer coinler ve trader geçerli kalır. Yalnız fiyatlanamayan eylem çıkar; sonraki eylemler defterdeki gerçek ele göre kırpılır
  (fazlası atılır, elde yokken azaltma atılır → ters pozisyon açılmaz). `fiyatsiz_acik_coinler`: fiyatsız eylemlerin net miktarı ≠ 0 olan
  coinler (gerçek kopya pozisyonu defterden farklı olabilir). Mum sonraki koşuda gelirse otomatik hesaplanır (önbellekte eksik saklanmaz).
- `traderlar[].veri_durumu` (v1.6, GOREV madde 15): `tamam` | `fiyatsiz` (trader geçerli; yalnız fiyatı bulunamayan coinler ölçüm dışı, bkz. `sanal_kopya.fiyatsiz_*`) |
  `perp_bos` (güncel perp hesap değeri 0; spot bakiye ayrı, "veri yok" değildir) | `okuma_hatasi` (son okuma başarısız, önceki sonuç gösteriliyor) |
  `bayat` (okuma hatası ve önceki başarılı okuma > 180 dk). `gecerli` geriye dönük uyumlu türevdir: `tamam`/`fiyatsiz` → true, diğerleri false.
  Hiç okunmamış trader için `yer_tutucu: true` (trader ve `sanal_kopya` düzeyinde) yayımlanır; bu satırdaki 1.000 $ / 0 değerleri ölçüm DEĞİLDİR
  ve hiçbir toplama girmez.
- `kapsam` (v1.6, üst düzey): kol adı (`kollar` üyeliğiyle; ana etiket değil) → `{toplam, gecerli, fiyatsiz, perp_bos, yer_tutucu, bayat, okuma_hatasi,
  kapsama, gecerli_bakiye_usd, gecersiz_bakiye_usd}`. `toplam` üye sayısıdır ve sabit kalır (ITT); her üye `gecerli | perp_bos | yer_tutucu | bayat |
  okuma_hatasi` kovalarından tam birindedir (`fiyatsiz`, `gecerli`nin alt kümesi). `kapsama` = gecerli/toplam (oran, 0,67 = %67). Bakiye alt
  toplamları 1.000 $ kopya ölçeğinde USD'dir; `gecersiz_bakiye_usd` eski sonuçların önceki bakiyeleridir (yer tutucu ve perp_bos hariç).
  `kasa_egri` ve kol toplamları yalnız `gecerli=true` traderları, `kollar` üyeliğiyle toplar. Eğri = kasa (madde 17): `egri_eksik` = eğrisi
  olmayan geçerli üye sayısı (eksik kapsama; kasaya girmez), `kasa_son_nokta_usd` = `kasa_egri`nin son noktası, `kasa_fark_usd` = o nokta − eğrisi olan
  geçerli üyelerin `bakiye_usd` toplamı, `kasa_mutabik` = |fark| < 0,5 $ (aksi halde ekranlar uyarı göstermelidir).
- `sanal_kopya.eksik_degerleme` (bool, v1.6, madde 18) = `isaret_eksik > 0`: açık lotlardan en az birinin işareti yok/bayat; bu satırın açık K/Z ve bakiyesi
  eksik değerlenmiştir. `kapsam[kol].eksik_degerleme` = böyle geçerli üye sayısı; >0 ise ekranlar kol kasasını "bilinmiyor/eksik" göstermelidir
  (sıfır varsaymaz). `null` teminat/değer 0 olarak toplanmaz.
- `sayac_24s` (v1.6, üst düzey, madde 16): kol → `{acilis, kapanis, trader_sayisi, kapanan, kazanan}`; koşu başlangıcından geriye 24 saat, kesilmemiş
  olaylardan. `kapanan`/`kazanan`: sanal sonucu (`sanal_sonuc.kapanis`) o pencerede biten kopyalar ve bunlardan `net_yuzde > 0` olanlar.
  Ekranlar 24 saat sayısı için `olaylar` listesini DEĞİL bunu kullanır.
- `olay_kapsami` (v1.6): `{baslangic (ilk işlem olayı, UTC ISO), tam (bu koşuda hiç trader hatası yoksa true), toplam, kol_basina_son, sayac_gun}`.
- Eski anlatım: son 200 olay, yeniden eskiye. `id` kalıcı ve tekildir (bildirim tekrarını ve kararı buna bağlarız).
- **Olay kimliği (v1.2):** `{trader}-{oid}-{tur}` (ör. `T1-123456789-acilis`); ışık olayı `{trader}-{ms}-isik`.
  Olaylar **emir (`oid`) düzeyinde** üretilir: aynı emrin dolumları birleştirilir (tek açılış sahte büyütmeler doğurmaz).
  Saatlik motor ve Cloudflare Worker aynı kuralla aynı kimliği üretir.
- `traderlar[].kol` (v1.5, ek alan; `surum` 1 kalır): `oda` | `kontrol` | `taban` | `elle` | `referans_oda` | `referans_kontrol` | `cikarilan` | `havuz` (K-8, sessiz ileri ölçüm); `kollar` adresin bulunduğu tüm kollar. İzleme listesinden
  aynen taşınır; Telegram Worker bildirimi yalnız `kol = oda` için gönderir (diğerleri sessiz izlenir).
- `traderlar[].secim` (v1.8, isteğe bağlı): izleme listesindeki değişmez seçim etiketi
  (`<secim_surumu>@<kapı tarihi>`). Tüketici, aynı etiketi en son `secim.json` ile
  eşleştirerek seçimin onaylı olduğunu gösterebilir. Sabit referans üyeleri eski
  `id`, `t0` ve etiketiyle `referans_oda` / `referans_kontrol` olarak sessiz izlenir.
- `traderlar[].yonsuz_bayrak` (isteğe bağlı, yalnız `kol` = `oda` | `kontrol`; `surum` 1 kalır; Argon A26, **yalnız bilgi**): `funding_payi`, `spot_perp_ters`, `maker_payi` — her biri `{deger, esik, asildi}`
  (`deger` hesaplanamazsa `null`; `spot_perp_ters` ayrıca `coin`), `bayrak` (herhangi biri aşıldıysa `true`), `pencere_gun` (90), `sezgisel: true`, okunamayan kaynak varsa `hata`.
  Funding ve spot durumu günde bir kez çekilir (önbellek `motor.json`'da). Eşikler `kurallar.yaml` `yonsuz_*`, sezgiseldir; seçim/kapı/oda kararını değiştirmez.
- `kalabalik` (üst düzey, isteğe bağlı, oda üyesi varsa; Argon A27): `{n_oda, coinler: [{coin, net_yon, net_pay, ayni_yon, toplam, cakisma}], uyari, uyari_metni, zaman, sezgisel}`.
  `net_pay` = |Σ x·yön| / Σ|x|, x = kopya ağırlığı × pozisyon nosyoneli / trader hesap değeri (kaldıraç ikinci kez çarpılmaz). `uyari_metni` yalnız `uyari` iken dolu (tek satır; Telegram `/durum` ve pano).
  Eşikler `kalabalik_*` (sezgisel). Otomatik işlem yoktur.
- `traderlar[].tarz` (v1.3): `intraday` | `swing` (izleme listesinde `tarz` varsa o, yoksa en son kapı sonucundan; ikisi de yoksa
  `bilinmiyor` ve 30 dk gecikme). Sanal kopya gecikmesi tarza göre (intraday 30 dk, swing 120 dk);
  Telegram mesajında `[Intraday]` / `[Swing]` etiketi.
- **Üst düzey zaman adları (v1.6, madde 19 / C#16):** `kosu_baslangic` (= `uretildi`) ve `kosu_bitis` (= `yayim_zamani`) eşanlamlı yeni adlardır; `kapsam[kol].en_eski_veri_zamani` = kolun en eski trader okuması (ekran veri yaşını buradan hesaplar, koşu zamanından değil).
- **Üç ayrı zaman (v1.6, hepsi UTC ISO):** `uretildi` = koşu başlangıcı; `traderlar[].veri_zamani` = o trader'ın hesap durumunun gerçekten okunduğu an
  (uzun koşuda trader'lar arasında dakikalar/saatler fark eder); `yayim_zamani` (üst düzey) = `durum.json`'ın yazıldığı an. Veri yaşı için `veri_zamani`,
  yayım gecikmesi için `yayim_zamani − uretildi` kullanılır.
- `traderlar[].veri_zamani` ve `gecerli` (v1.4): trader verisinin son başarılı okuma zamanı ve geçerliliği. Bir saatlik
  okuma hata verirse önceki trader gösterilir, `gecerli: false` olur ve sağlık nedenlerinde `veri hatası` yer alır.
  Önceki başarılı kayıt hiç yoksa trader yine yayımlanır: `veri_zamani: null`, `gecerli: false`, sarı sağlık ışığı ve
  boş `pozisyonlar`; böylece eksik trader liste dışına sessizce düşmez.
- `sanal_kopya.not` (v1.2, isteğe bağlı): ör. `"yaklaşık fiyat"` (1 dk mum kaçınca 1 saatlik mum kullanıldıysa).
- `saglik.nedenler` `"veri hatası: …"` içerebilir (v1.2): o trader bu saat güncellenemedi, önceki kayıt gösteriliyor.
- `buyutme`/`azaltma`: aynı yönde pozisyonun **%25'inden fazla** değişimi (lider kararı); daha küçükleri olay sayılmaz.
- `sanal_kopya.gerceklesen`, `.acik`, `.toplam`, `.son_isaret`, `.isaret_eksik` (v1.6): sonuç kanonik defterden (`defter.copy_ledger`) üretilir; `gerceklesen` (maliyet ve funding dahil), `acik` (işaretlenmiş açık K/Z) ve `toplam` hesap değerine oran kesirleridir (`bakiye_usd = 1000 × (1 + toplam)`); `son_isaret` açık pozisyonlarda kullanılan en eski işaretin 1 dk mum zamanı (açık pozisyon yoksa `null`); `isaret_eksik` işareti bulunamayan açık coin sayısı.
- `traderlar[].veri_kalitesi.mutabakat` (v1.7, yalnız oda üyeleri, isteğe bağlı): defter (dolumlardan türetilen pozisyon) ↔ `clearinghouseState` mutabakatı — `uyumlu, yetim, eksik, yon_farki, boy_farki, toplam, uyumsuz_oran, yetim_coinler, sorunlu[], bozuk_satir, zaman`. **Yalnız rapor**: hiçbir pozisyon otomatik kapatılmaz.
- `sanal_kopya.egri` (v1.1): t0'dan bugüne günlük sanal bakiye (USD).
- `olaylar[].sanal_sonuc` (v1.1, yalnız `acilis`/`buyutme`): bu olayın 30 dk gecikmeli kopyasının sonucu; pozisyon
  kapanınca `kapandi` ve maliyet sonrası `net_yuzde` (kopyalanan tutara göre). "Açtıklarım" istatistiği bununla
  hesaplanır: kararı `acti` olan olayların `sanal_sonuc`'u ↔ tüm olaylarınki.
- **Yetersiz veri eşiği** (v1.1): bir trader için kapanmış ve kararı verilmiş olay sayısı < 10 ise istatistik
  sekmesi "yetersiz veri" yazar.
- `sanal_kopya`: t0 sonrası, 30 dk gecikmeli, maliyetli (taker %0,045 + kayma %0,05 + funding) — CT-Kapı
  `delayed_copy` ile aynı hesap.

## 3. Sağlık ışığı ve form (hesap Codex'te, `pano/saglik.py` yeniden kullanılır)
| Işık | Koşul (herhangi biri) |
|---|---|
| **kırmızı** (eşikler v1; kullanıcı sonra gözden geçirecek) | t0 sonrası getiri t0 öncesi geçmişten kurulan blok bootstrap konisinin %5 altında; zirveden düşüş > t0 öncesi en büyük düşüş × 1,5; gerçek kaldıraç > 10x; martingale işareti |
| **sarı** | koninin %5–%20 bandında; CUSUM uyarısı; son 30 günde işlem yok; kaldıraç 3–10x |
| **yeşil** | hiçbiri |

**Form skoru** = son 30 gün sanal kopya getirisi / son 90 gün günlük oynaklık. **Yalnız ekran sıralaması içindir**;
kopyalama kararını değiştirmez (karar: kapı + ışık).

## 4. Kararlar (açtım / atladım)
Kayıt: `{"olay_id", "zaman", "karar": "acti | atladi", "neden": "gec_gordum | begenmedim | diger",
"not": ""}` — `zaman` yalnız `YYYY-MM-DD`; `not` izinli etiket listesinden yalnız boş değerdir. Tutar, bakiye,
hesap, isim ve serbest metin yazılmaz. Eski `bakiye_yok` kayıtları içe aktarmada `diger`e çevrilir.
`copytrade-izleme` dalında `izleme/kararlar.jsonl`; v1'de karar yalnız Telegram düğmesiyle verilir.
İstatistik: aynı trader için "tüm olaylar" ile "açtıklarım" sanal sonuçları ayrı hesaplanır.

## 5. Telegram
- Gönderen: Cloudflare Worker, 5 dakikada bir (`docs/GOREV_TELEGRAM.md`). Olay türleri: `acilis`, `kapanis`, `buyutme`,
  ışığın `kirmizi`ya dönmesi. Her `olay.id` bir kez bildirilir.
- Metin: `🟢 Trader-1 · BTC LONG açtı · giriş 68.400 · hesabın %8'i · 2x · Binance: var`
- Düğmeler (yalnız `acilis`/`buyutme`): **[Açtım] [Atladım]** → Atladım ise neden düğmeleri (Geç gördüm / Beğenmedim / Diğer).
- Gizlilik (v1.4, kullanıcı kararı): yayımlanan karar kaydında `zaman` yalnız tarih; `bakiye_yok` nedeni yok.
- Bot anahtarı ve sohbet kimliği yalnız GitHub Secrets'ta (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`,
  `TELEGRAM_WEBHOOK_SECRET`); dağıtım işi bunları Cloudflare secret'ına aktarır. Repoya, günlüğe, sohbete yazılmaz.


## Worker (v1.6, madde 19)
- Günlük özet: 06:00 UTC'den (09:00 TR) sonraki ilk dakikada ve o gün gönderilmediyse gider; 06:05'ten sonra kalırsa başlığa "(gecikmeli)" eklenir.
- D1 `saglik_kayit(kaynak, ardisik, son_hata, zaman)`: `durum_okuma`, `dolum`, `tetikleme:<iş akışı>`, `ozet_durum` kaynaklarının ardışık hata sayısı;
  3. ardışık hatada tek Telegram alarmı, başarıda sayaç sıfırlanır. Mevcut D1'e `worker/schema.sql`daki yeni tablo bir kez uygulanmalıdır.
- `GET /kararlar`: Cloudflare secret `KARAR_ANAHTARI` tanımlıysa `Authorization: Bearer <anahtar>` zorunlu (yoksa 401); tanımlı değilse eski açık davranış sürer.
  Saatlik içe aktarma (`izleme.yml`) aynı adlı GitHub secret'ını gönderir (boşsa başlıksız).
