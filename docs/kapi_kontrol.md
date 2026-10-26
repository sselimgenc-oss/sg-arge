# Kapı kontrolü — plasebo kalibrasyonu ve geriye dönük kıyas

Bu ölçüm `backtests/plasebo.py` ile üretilir. Paper, kapı, eşik ve karar tablolarını değiştirmez.

| Çıktı | Kapsam | Açıklama |
|---|---|---|
| `results/plasebo.csv` | TV-2'de geçenler ve U7'de geçenler | Aynı gün sayısı/tutma bloklarıyla 1.000 rastgele giriş. |
| `results/kapi_kontrol_13.csv` | `paper/portfoy.yaml`daki 13 kitap | Maruziyet eşleşmiş kıyas, alfa, NW t, plasebo ve DSR. |

- Rastgeleleştirme kimliğin `crc32` tohumu ile yeniden üretilebilir.
- Günlük getiri serisindeki ardışık sıfır olmayan günler, saklanan sonuçlarda gözlenebilen maruziyet bloklarıdır. Blokların sayısı ve uzunlukları korunur; her blok için gerçekçi maliyet bir kez düşülür.
- Plasebo piyasası: TV-2'de stratejinin **kendi sembolü** (aynı enstrüman, rastgele giriş); U7 sepetlerinde sınıf kıyası (ABD SPY, kripto BTCUSDT, emtia GLD). Kıyas açık günlerde bu piyasa, diğer günlerde nakit.
- **Ölçek (lider düzeltmesi):** plasebo pozisyonu stratejinin aktif günlerdeki oynaklığına eşitlenir (`olcek` sütunu); aksi halde %100 yatırımlı plasebo, sermayenin küçük kısmıyla işlem yapan stratejiyle kıyaslanmaz. Maliyet de bu ölçekle düşülür.
- Sınırlama: U7 sepet stratejilerinde neredeyse her gün açık pozisyon olduğundan blok permütasyonu zayıftır; orada asıl ölçü beta ayarlı alfadır.
- Alfa günlük OLS ile hesaplanır, yıllıklaştırılır; alfa t-istatistiği Newey–West (5 gecikme) standard hatasıyladır.
- `N_eff`, günlük getiri korelasyonu ≥ 0,9 olanları tek bağlaçlı hiyerarşik kümeye koyan küme sayısıdır. Ham N ve DSR ayrıca CSV'dedir.
- Ağ/veri bulunamayan bir satır atılmaz: CSV'de `hata` alanına yazılır. Böyle bir satırdan sonuç veya karar çıkarılmaz.
- Çalıştırma: `python -m backtests.plasebo`; yalnız paper kontrolü: `python -m backtests.plasebo --only-13`.
- Tam 1.000 tekrar uzun sürdüğünde `.github/workflows/plasebo.yml` yalnız bu dalda tetiklenir ve çıktıları tekrar üretir.

Bu rapor bilgi amaçlıdır; hangi kitabın kalacağına dair öneri içermez.

## Çalıştırma notu

1.000 tekrarlı hesap yerelde çalıştırılmaz. `.github/workflows/plasebo.yml`, yalnız `codex/kapi-kontrol` dalında tam kalibrasyon ile 13 kitap kontrolünü üretir ve iki CSV'yi aynı dala commitler.

- Çıktı, geçme/kalma kararı değildir.
- Eski huni null sütunları U7 satırlarında korunur; TV-2 için eski huni sonucu yoktur.
- Ağ erişimi sağlandığında aynı tohumla yeniden koşmak sonuçları yeniden üretir.
