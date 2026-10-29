# Faz 3 geçmiş prova (seçim v1.3 uyarlaması)

> Faz 3 yalnız **durdurabilir**; başlatma kanıtı sayılmaz. Karar kullanıcıda. Hiçbir pencere 2026-10-28 sonrasına taşmaz.

## Sentetik doğrulama (gerçek veriden önce)

- 200 tohum; karar ölçütü: V0 farkın %95 aralığının alt sınırı > 0.
- Sıfır etkili trader: yanlış pozitif 0,035 (bant [0.0, 0.1]); nokta tahmini > 0 oranı 0,500 (≈ 0,5 beklenir).
- Enjekte etki (q = 0.7): yakalanma 0,930 (asgari 0.8).
- Sonuç: **geçti**.

## Gerçek veri

- Kaynak: gerçek koşu yapılmadı (bu PR yalnız koşucu, sentetik doğrulama ve iş akışı).
- **Gerçek pencere koşusu yapılmadı**; Durdurma 1 henüz değerlendirilemedi.

## Not

- Gerçek koşu `faz3.yml` ile elle tetiklenir (sentetik doğrulama → T anları matrisi → rapor). Bir T için evren binlerce adrestir (adres başına yaklaşık bir dakika, API hız sınırı); bu yüzden pencereler ayrı işlerde parça parça koşar ve rapor onlardan birleşir.
- Gerçek rapor bu dosyanın yerine geçer; o zamana kadar Durdurma 1 **değerlendirilemedi**.
