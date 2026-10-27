# Veri sözleşmesi — copy trade izleme (v1.1, 2026-10-27, kullanıcı onayı)

Üretici: **Codex** (sg-arge). Tüketici: **Sonnet** (sg-pano panosu) ve Telegram bildirimi. İkisi de yalnız bu
sözleşmeye göre çalışır; alan eklemek/değiştirmek lider onayıyla `surum` artırılarak yapılır.

## 1. Dosyalar ve yer
| Dosya | Nerede | Kim yazar | Sıklık |
|---|---|---|---|
| `izleme/durum.json` | sg-arge, `copytrade-izleme` dalı (main büyümesin) | Codex işi | 10 dakikada bir |
| `izleme/ornek_durum.json` | sg-arge `main` (sabit örnek, 4 trader) | lider (hazır) | sabit; Sonnet bununla başlar |
| `izleme/kararlar.jsonl` (açtım/atladım) | sg-arge, `copytrade-izleme` dalı (repolar açık; ikinci repoya yazma anahtarı gerekmesin) | Telegram işi | her karar |

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
Kayıt: `{"olay_id", "zaman", "karar": "acti | atladi", "neden": "gec_gordum | begenmedim | bakiye_yok | diger",
"not": ""}` — `not` serbest metin değil, kısa etiket; tutar/kişisel bilgi yazılmaz. `copytrade-izleme` dalında `izleme/kararlar.jsonl`; v1'de karar yalnız Telegram düğmesiyle verilir.
İstatistik: aynı trader için "tüm olaylar" ile "açtıklarım" sanal sonuçları ayrı hesaplanır.

## 5. Telegram
- Olay türleri: `acilis`, `kapanis`, `buyutme`, ışığın `kirmizi`ya dönmesi. Her `olay.id` bir kez bildirilir.
- Metin: `🟢 Trader-1 · BTC LONG açtı · giriş 68.400 · hesabın %8'i · 2x · Binance: var`
- Düğmeler (yalnız `acilis`/`buyutme`): **[Açtım] [Atladım]** → Atladım ise neden düğmeleri.
- Bot anahtarı ve sohbet kimliği yalnız GitHub Secrets'ta (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`); repoya,
  günlüğe, sohbete yazılmaz.
