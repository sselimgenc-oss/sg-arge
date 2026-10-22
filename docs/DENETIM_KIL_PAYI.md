# Kıl payı denetimi (ön kayıt)

Tarih: 2026-10-22. Kullanıcı isteği: "Bu sertlikle iyi olup gözden kaçırdığımız olmasın."

Bu dosya **sonuçlar görülmeden önce** yazıldı ve commit'lendi. Kurallar koşudan sonra değiştirilmez. Mevcut eleme kriterleri (`docs/ELEME_KRITERLERI.md`) değişmiyor; bu denetim ayrı ve tek seferlik bir ikinci bakış.

## Neden
Mevcut huninin iki olası kör noktası var:
1. **Aşama 2a yalnız getiriyi ölçüyor (PF, ortalama R).** Değeri getiride değil riskte olan stratejiler bu testte "piyasa betası" diye elenebilir. Örnek: düşüşte nakde geçip kaybı küçülten bir zamanlama stratejisi.
2. **OOS penceresi kısa (2024-10 → bugün).** Az işlemde "OOS ortR ≤ 0" sonucu şanstan çıkabilir.

## Kapsam
- **A.** `results/asama2a.csv` içinde `karar == "Reddedildi (piyasa betasi)"` olan **tüm** satırlar. p değerine göre ön seçim yapılmaz. Kapsama `Reddedildi (BIST USD)` satırları girmez; onlar dolar bazında kârsız.
- **B.** `results/asama2b.csv` içinde `neden == "OOS ortR<=0"` olan satırlar, yani başka hiçbir kapıdan kalmamış olanlar.

## A — Risk testi
- **Dönem:** Aşama 2a ile aynı IS dönemi. Veri, piyasa ve maliyet (1x) de aynı.
- **Ölçü:** `getiri / |MDD|`. Portföy özkaynak eğrisinden hesaplanır (Calmar benzeri).
- **Null:** Aşama 2a'daki rastgele giriş modeli. Çıkışlar aynı, sembol başına giriş sayısı aynı, kalibrasyon aynı. Fark şu: her tekrarda tam özkaynak eğrisi hesaplanır.
- **Tekrar:** 200. p değeri 0.03–0.10 arasındaysa 1000 tekrarla yeniden koşulur (2a'daki kural).
- **p:** (1 + null ≥ gerçek sayısı) / (1 + N), tek yönlü.
- **Çoklu test düzeltmesi:** Kapsamdaki tüm satırlara birlikte Benjamini–Hochberg uygulanır, q = 0.10. Bu zorunlu; 151 testte %5 eşiğiyle şans eseri ~7 "geçen" çıkar.
- **BH'den geçen satır** Aşama 2b'ye girer, 2b kapıları değişmeden uygulanır: OOS, ön dönem, stres, plato, bootstrap MDD95 ≤ %15, DSR. ABD/BIST'te tarihsel evren (PIT) de koşulur.
- **Varılabilecek en iyi karar: Koşullu.** Şerhi: "risk kenarı (getiri kenarı değil; 2a null'unu geçemedi)". Bu denetimden doğrudan **Geçti çıkmaz.**

## B — OOS gücü
- **Hesap:** Satırın OOS işlem listesinden ortalama R ve bunun bootstrap güven aralığı hesaplanır (10.000 örnek, %95). Aynı satırın IS ortalama R'si de hesaplanır.
- **Test:** OOS ortalaması IS ortalamasından anlamlı ölçüde düşük mü? Tek yönlü Welch t-testi, α = 0.05.
  - **Anlamlı ölçüde düşük değilse:** karar "Reddedildi" yerine **"Belirsiz (OOS gücü yetersiz)"** olur.
  - **Anlamlı ölçüde düşükse:** "Reddedildi" kalır.
- **"Belirsiz" Koşullu değildir:** portföye girmez. Faz 2'de paper'da gözlem adayı olarak listelenir.

## Kapsam dışı
- Kaynak evreninden dar test evreni sorunu (ör. M008 Russell 3000 → ABD25). Ayrı veri gerektiriyor; bu denetimde ele alınmaz, raporda not edilir.
- Kriter eşiklerinin kendisi (PF 1.1, MDD %15, vb.) değiştirilmez.

## Çıktı
- `results/denetim_kil_payi.csv`
- `results/denetim_kil_payi.md`

Ana sonuç dosyalarına (`SONUC.*`) yalnız denetimden Koşullu ya da Belirsiz çıkan satırlar ayrı bir bölüm olarak eklenir. Mevcut kararlar silinmez.
