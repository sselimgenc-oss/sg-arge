# Copy trade tarama durumu

- Durum: uygulandı, ağsız birim testleri eklendi.
- Kapsam: yalnız herkese açık Hyperliquid HTTP verisi; cüzdan, anahtar, emir ve gerçek para kodu yok.
- Karar: API'nin fill geçmişi son 10.000 kayıtla sınırlı olduğundan yerel gzip arşivi `tid` ile eklemeli tutulur.
- Karar: günlük iş gecikmeyi ölçemediği için `kopya/` çıktıları iki kayma senaryolu **yaklaşık** sanal kopyadır; canlı kopya değildir.
- Açık nokta: `userFunding` yanıtındaki imzalı tutar alanı gerçek API örneğiyle ilk Actions koşusunda doğrulanmalıdır; hata olursa iş akışı başarısız olur, sonuç uydurulmaz.
