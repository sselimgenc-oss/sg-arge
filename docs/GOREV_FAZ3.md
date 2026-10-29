# Görev — Faz 3 geçmiş prova, v1.3 uyarlaması (Sonnet, 2026-10-29, lider; kullanıcı onayı "evet")

Bağlam: Ön kayıt Durdurma 1 (`docs/ONKAYIT_D.md`): geçmiş prova pencerelerinin yarısından fazlasında kohort kontrolü geçemiyorsa
canlı izleme durdurulur (sürüm 1.1: prova canlıyla paralel yürür). Pilot 2026-10-29'da başladı; prova hiç koşmadı. Ana tanım
`docs/GOREV_GOLGE.md` "Faz 3" bölümündedir; bu belge onu **seçim v1.3'e** uyarlar. Faz 3 yalnız **durdurabilir**, başlatma kanıtı
sayılmaz (ön kayıt 1.3 madde 8). Öncelik: `GOREV_PILOT_VERI` (#389) birleştikten sonra, `GOREV_OFIS_CANLI`'dan önce.

Kurallar: kapı, seçim, gölge motoru ve `analiz_d.py` değişmez (yalnız çağrılır). Yeni sayılar yalnız `kurallar.yaml`'a. Altın örnekli
test; tam paket yeşil. PR açılır; birleştirmeyi lider yapar. **Hiçbir pencere 2026-10-28'den sonraya taşmaz** (pilot verisi
görülmez; körlük).

## Lider kararları (ön kayıt yetki devri; veri görülmeden, bu belgeyle dondurulur)
`kurallar.yaml`:
- `faz3_ileri_gun: 60`; `faz3_adim_gun: 14` (GOREV_GOLGE ile aynı); `faz3_min_pencere: 6`.
- **"Kohort kontrolü geçemiyor"** (Durdurma 1) = pencerede oda ↔ eşleştirilmiş kontrol **V0** 60 günlük net getiri farkı (eşit ağırlık,
  BTC betası düzeltilmiş, `analiz_d.ikincil_fark` nokta tahmini) **≤ 0**. Geçemeyen pencere oranı > 0,50 → durdurma önerisi
  (karar kullanıcıda).
- Bilgi (karar dışı): pencere başına havuz geneli Spearman (`analiz_d.birincil_spearman`), V1/V2, taban, rejim kırılımı.

## İş
1. **Önce sentetik doğrulama** (GOREV_GOLGE Faz 3 ilk madde): ≥200 tohumda sıfır etkili trader yanlış pozitif ~%5; enjekte etki
   yakalanır. Geçmezse gerçek veriyle rapor yok.
2. **Veri kaynağı:** T anı etiketlemesi için kapının kullandığı geçmiş dolumlar. API yalnız son 10.000 dolumu verir (Argon A21):
   T'de etiketlenebilen ve T+60'a kadar dolumu eksiksiz olan adresler kullanılır; dışarıda kalan adres sayısı her pencerede
   raporlanır (sessiz eleme yok). HF verisi (#346) yalnız lider onayıyla.
3. **Koşucu** `copytrade/faz3.py`: her T için `secim.py` v1.3 kuralı (havuz süzgeci, oda, dilim eşleşmeli kontrol, tohum
   `secim-v1.3-faz3-<T>`) → T..T+60 gölge (`golge.calistir`, V0/V1/V2) → pencere satırı. Elle tetiklenen iş akışı
   (`faz3.yml`, `timeout-minutes` yeterli, ağır iş parça parça).
4. **Rapor** `arastirma/copytrade/faz3/RAPOR.md`: pencere sayısı, kol başına adres, fark ve aralık (min/medyan/max), geçemeyen
   pencere oranı ve Durdurma 1 sonucu açıkça, "iyimser üst sınır (bugünkü leaderboard evreni)" notu, MDE (gerçek varyansla).

## Teslim
PR; açıklamada sentetik doğrulama sonucu ve Durdurma 1 sonucu.
