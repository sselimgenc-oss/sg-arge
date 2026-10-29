# Kalıcılık testi: sentetik doğrulama

- 300 sentetik hesap, günlük kâr geçmişi (yatırma/çekme PnL'yi etkilemez), 26 T anı, 5 dilim, ileri 28/56 gün; blok bootstrap %95.
- Cevabı bilinen iki dünya: **kalıcı beceri var** (her hesabın sabit beklenen getirisi) ve **yok** (hepsi sıfır beklentili).
- Sonuç: beceri varken 6/6 skor-pencere çifti 'evet'; yokken 0/6. **Geçti** (ölçüt: ≥ 4/6 ve 0/6).

| Dünya | Skor | İleri | T | Üst − alt | Aralık | Spearman | Sonuç |
|---|---|---:|---:|---:|---|---:|---|
| beceri var | (a) 90 gün getiri | 28 gün | 26 | 0,0645 | [0,0463; 0,0876] | 0,64 | evet |
| beceri var | (a) 90 gün getiri | 56 gün | 26 | 0,1284 | [0,1067; 0,1623] | 0,80 | evet |
| beceri var | (b) Calmar (getiri / maksimum düşüş) | 28 gün | 26 | 0,0641 | [0,0441; 0,0852] | 0,76 | evet |
| beceri var | (b) Calmar (getiri / maksimum düşüş) | 56 gün | 26 | 0,1254 | [0,1015; 0,1607] | 0,87 | evet |
| beceri var | (c) 180 gün kârlı ay oranı | 28 gün | 21 | 0,0601 | [0,0508; 0,0702] | 0,79 | evet |
| beceri var | (c) 180 gün kârlı ay oranı | 56 gün | 21 | 0,1131 | [0,1050; 0,1305] | 0,82 | evet |
| beceri yok | (a) 90 gün getiri | 28 gün | 26 | 0,0013 | [-0,0406; 0,0342] | 0,10 | belirsiz |
| beceri yok | (a) 90 gün getiri | 56 gün | 26 | -0,0017 | [-0,0751; 0,0508] | 0,14 | belirsiz |
| beceri yok | (b) Calmar (getiri / maksimum düşüş) | 28 gün | 26 | 0,0054 | [-0,0205; 0,0259] | 0,21 | belirsiz |
| beceri yok | (b) Calmar (getiri / maksimum düşüş) | 56 gün | 26 | -0,0016 | [-0,0529; 0,0351] | 0,08 | belirsiz |
| beceri yok | (c) 180 gün kârlı ay oranı | 28 gün | 21 | -0,0007 | [-0,0225; 0,0142] | 0,10 | belirsiz |
| beceri yok | (c) 180 gün kârlı ay oranı | 56 gün | 21 | -0,0116 | [-0,0433; 0,0133] | 0,00 | belirsiz |
