# Aşama 2a (piyasa betası) lider değerlendirmesi

Koşu: lider ortamı, main @ acce559 (T6a), 2026-10-22 günlük veri, 200 tekrar (sınırda 1000), 4 işçi. Çıktı: `results/asama2a.csv`, `results/asama2a_ozet.md`. P02 ve R01 (`kismi_kar`) aynı koşuda taramaya eklendi (`results/tarama.csv`).

## Sonuç
125 kart × piyasa satırı (37 kart):
- **Geçti (null): 3**: A6-010 Emtia (Gap Momentum), P3-011 Kripto, R01 ABD (Qullamaggie)
- Reddedildi (piyasa betası): 114
- Reddedildi (BIST USD): 8. USD'ye çevrilince BIST kârı kayboldu.

## Bulgu: giriş sinyalleri rastgele girişten ayırt edilemiyor
- Strateji PF / rastgele giriş medyan PF oranının medyanı **1,03**. 117 satırın 68'i medyanın üstünde; bu yazı-tura düzeyi.
- Rastgele girişler aynı sayıda işlem yaptı (oran 0,97) ve pozisyonları daha kısa tuttu (0,72). Bu, trend stratejilerinin lehine bir fark; test stratejilere karşı katı değil.
- 125 satırda %5 eşikte şansla ~6 yanlış pozitif beklenir; 3 geçiş bunun altında. Yani geçen 3 satır da çoklu test düzeltmesine karşı kırılgan: T6b'de DSR ve OOS ile dikkatle değerlendirilecek.
- Yorum: Bu dönemde kârın kaynağı (a) piyasanın yükselişi, (b) çıkış/stop yapısı (rastgele girişler aynı çıkışları kullandı ve onlar da kârlıydı). Giriş kuralları neredeyse hiç katkı vermiyor.

## Kararlar
1. Test kuralı değiştirilmez (PF **ve** ortalama R, %95). Ortalama R tek başına 31 satırda anlamlı çıktı. Ancak PF'de anlamlı değilse kenar küçük ya da tutma süresi farkından geliyordur. Kriteri sonuca bakarak gevşetmiyoruz.
2. Geçen 3 satır + Codex Algo C03-C21 (null testini T6b içinde alacak) → T6b.
3. **Kullanıcı için önemli bulgu:** "Çıkış yapısı + piyasa yönü" kârın asıl kaynağı. Paper fazında giriş sinyalinden çok çıkış/risk yönetimi ve piyasa rejimi filtresi üzerinde durulmalı. Bu, sonuç raporunda ayrı bir bölüm olacak.

## Ek: ikinci koşu (2026-10-22)
Yeni taranan 26 karttan aşama 2 adayı 12 kart (21 satır) aynı testten geçti: **5 geçti**. G007 Kripto (Crude Oil Salı/Perşembe kuralı), G011 ABD (PowerX), M015 ABD (Connors Cumulative RSI), M038 ABD (QS mum formasyonu), O3-003 ABD (gece swing).
- Birleşik: 146 satır, **8 geçti**. %5 eşikte şansla ~7 yanlış pozitif beklenir; yani geçenlerin bir kısmı tesadüf olabilir. T6b'deki OOS, 2015-2019 ve DSR testleri belirleyici.
- Desen: Geçenlerin çoğu **ABD hisselerinde kısa vadeli ortalamaya dönüş** stratejileri; literatürde bilinen bir etki. Connors RSI-2 (M014) ise geçemedi.
