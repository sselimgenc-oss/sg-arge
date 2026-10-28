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
- `olaylar`: son 200 olay, yeniden eskiye. `id` kalıcı ve tekildir (bildirim tekrarını ve kararı buna bağlarız).
- **Olay kimliği (v1.2):** `{trader}-{oid}-{tur}` (ör. `T1-123456789-acilis`); ışık olayı `{trader}-{ms}-isik`.
  Olaylar **emir (`oid`) düzeyinde** üretilir: aynı emrin dolumları birleştirilir (tek açılış sahte büyütmeler doğurmaz).
  Saatlik motor ve Cloudflare Worker aynı kuralla aynı kimliği üretir.
- `traderlar[].kol` (v1.5, ek alan; `surum` 1 kalır): `oda` | `kontrol` | `taban` | `elle`; `kollar` adresin bulunduğu tüm kollar. İzleme listesinden
  aynen taşınır; Telegram Worker bildirimi yalnız `kol = oda` için gönderir (diğerleri sessiz izlenir).
- `traderlar[].tarz` (v1.3): `intraday` | `swing` (izleme listesinde `tarz` varsa o, yoksa en son kapı sonucundan; ikisi de yoksa
  `bilinmiyor` ve 30 dk gecikme). Sanal kopya gecikmesi tarza göre (intraday 30 dk, swing 120 dk);
  Telegram mesajında `[Intraday]` / `[Swing]` etiketi.
- `traderlar[].veri_zamani` ve `gecerli` (v1.4): trader verisinin son başarılı okuma zamanı ve geçerliliği. Bir saatlik
  okuma hata verirse önceki trader gösterilir, `gecerli: false` olur ve sağlık nedenlerinde `veri hatası` yer alır.
  Önceki başarılı kayıt hiç yoksa trader yine yayımlanır: `veri_zamani: null`, `gecerli: false`, sarı sağlık ışığı ve
  boş `pozisyonlar`; böylece eksik trader liste dışına sessizce düşmez.
- `sanal_kopya.not` (v1.2, isteğe bağlı): ör. `"yaklaşık fiyat"` (1 dk mum kaçınca 1 saatlik mum kullanıldıysa).
- `saglik.nedenler` `"veri hatası: …"` içerebilir (v1.2): o trader bu saat güncellenemedi, önceki kayıt gösteriliyor.
- `buyutme`/`azaltma`: aynı yönde pozisyonun **%25'inden fazla** değişimi (lider kararı); daha küçükleri olay sayılmaz.
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
