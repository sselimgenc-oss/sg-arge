# Görev: Copy trade 1. aşama — Hyperliquid aday taraması (kullanıcı onayı 2026-10-26)

Kaynak: `docs/FAZ2_NOTLAR.md` §4 (Sol 6.1 pilot tasarımı (c)) ve §10 (Argon Hyperliquid notu,
`arastirma/copytrade/hyperliquid_notu.md`). Dal: `codex/copytrade-tarama` (`main`'den). Durum: `docs/codex_durum_copytrade.md`.
PR: `[Faz2] copy trade tarama`. PR öncesi tam test paketi.

**Kapsam sınırı:** yalnız herkese açık zincir üstü veri okunur. **Cüzdan, anahtar, emir, gerçek para yok.** API anahtarı
gerekmez (Hyperliquid `/info` ve lider tablosu anahtarsız). Paper kitaplarına dokunulmaz. Cüzdan adresleri zaten
herkese açık zincir verisidir; başka kişisel veri toplanmaz.

## 1. Günlük iş akışı (`.github/workflows/copytrade.yml`)
- Zamanlama: her gün 03:17 UTC + `workflow_dispatch`. Sonuçlar `copytrade-veri` dalına yazılır (paper-defter gibi;
  `main` büyümesin). İstek hızı: REST ağırlık sınırı IP başına 1.200/dk → istemci tarafında ≤ 900/dk sınırlayıcı,
  429'da üstel bekleme.

## 2. Tarama (`copytrade/tarama.py`)
1. **Lider tablosu:** `GET https://stats-data.hyperliquid.xyz/Mainnet/leaderboard`. Ham dosya saklanmaz; ön süzgeçten
   geçen ilk 2.000 satır (adres, hesap değeri, gün/hafta/ay/tüm zaman PnL, ROI, hacim) `veri/lider/<tarih>.csv.gz`.
2. **Ön süzgeç** (sabit, dosya başında): hesap değeri ≥ 25.000 USD; aylık ve tüm zaman ROI > 0; en çok 300 adres
   (tüm zaman PnL / hesap değeri sırasına göre) + `izleme.csv`'deki adresler.
3. **Ayrıntı** (her adres): `/info` `userFillsByTime` (son 180 gün, sayfalı), `userFunding` (aynı dönem),
   `clearinghouseState` (açık pozisyon, kaldıraç). Ham fill'ler `veri/fills/<adres>.csv.gz` olarak birikir (yalnız
   yeni kayıt eklenir; API son 10.000 fill'i tutar, bizim kaydımız kalıcı olur).

## 3. Ölçütler (`copytrade/olcut.py`) — yalnız gerçekleşmiş net PnL
Fill'lerdeki `closedPnl − fee` ve funding'den günlük **gerçekleşmiş net** PnL serisi (lider tablosundaki açık
pozisyon kârı sayılmaz). Getiri paydası: günlük hesap değeri (`portfolio`) ya da yoksa ortalama hesap değeri.
- geçmiş gün sayısı (ilk fill), kapanmış işlem sayısı (pozisyonun sıfıra döndüğü tur = 1 işlem);
- aylık kârlı ay oranı; Sortino; Calmar; K-oranı; Ulcer indeksi;
- en büyük işlemin toplam kâra payı; en iyi işlem çıkarılınca PF;
- ortalama / medyan tutma süresi; medyan ve en yüksek kaldıraç;
- coin yoğunlaşması (en büyük coinin hacim payı), likit coin payı (hacimce ilk 20 coin);
- **martingale/zarara ekleme işareti:** açık pozisyon zarardayken aynı yönde boyut artıran fill oranı; kazanan
  işlemlerde MAE (fill fiyatları ve o anki mumlardan yaklaşık).

## 4. Aday kuralları (önceden yazılı; `copytrade/kurallar.yaml`, eşik değişikliği kullanıcı kararı)
geçmiş ≥ 180 gün · kapanmış işlem ≥ 50 · kârlı ay oranı ≥ %70 · en büyük işlem payı < %30 · en iyi işlem çıkarılınca
PF > 1,2 · Sortino > 1,5 · Calmar > 1 · medyan tutma ≥ 1 saat (kopyalanabilir) · medyan kaldıraç ≤ 5x, en yüksek ≤ 15x ·
likit coin payı ≥ %80 · martingale işareti yok. Sonuç üç değerli: **aday / yetersiz (veri az) / elendi (neden)**.
Kaç adresin test edildiği her gün kaydedilir (çoklu deneme sayısı; seçim yanlılığı raporu için).

## 5. İzleme kaydı ve t0 (Sol 6.1 tasarımı)
- `izleme.csv`: adres, ilk aday olduğu gün = **t0**, sürüm, durum. **Başarı yalnız t0 sonrasından ölçülür**; t0 öncesi
  yalnız seçimdir. Kural ya da liderin tarzı (kaldıraç, coin evreni) belirgin değişirse yeni sürüm ve yeni t0.
- Bir kez aday olan adres, kuralları sonradan bozsa da izlemede kalır (durum alanı değişir; silinmez — hayatta
  kalma yanlılığı olmasın). En çok 50 adres.

## 6. Yaklaşık sanal kopya (günlük, t0 sonrası)
Her izlenen adres için t0 sonrası fill'lerden sanal kopya defteri: sabit nominal ölçek (lider pozisyonunun hesap
değerine oranı × 1.000 USD sanal), dolum = lider fill fiyatı + **kayma %0,05** (ve ikinci senaryo %0,15) + taker
**%0,045** + gerçek funding. Gecikme günlük işte ölçülemez; bu yüzden "yaklaşık" etiketi. Çıktı: `kopya/<adres>.csv`
(günlük özkaynak), lider–kopya farkı. Anlık kopya (WebSocket, ≤ 10 cüzdan) 2. aşamada sunucuda.

## 7. Çıktı ve rapor
`veri/adaylar/<tarih>.csv` (tüm ölçütler + sonuç), `izleme.csv`, `kopya/`, `RAPOR.md` (günlük: test edilen adres
sayısı, aday sayısı, izlenenlerin t0 sonrası net/MDD/işlem, kırmızı bayraklar). Pano entegrasyonu sonra.

## 8. Testler (ağsız, sabit örnek yanıtlarla)
fill'lerden işlem turu ve gerçekleşmiş net PnL; funding işareti; martingale işareti (tetiklenen/tetiklenmeyen);
her ölçüt için bilinen değerli küçük örnek; kural motoru (aday/yetersiz/elendi); izleme kaydında t0 değişmezliği ve
adres silinmemesi; hız sınırlayıcı; sanal kopya maliyetleri.
