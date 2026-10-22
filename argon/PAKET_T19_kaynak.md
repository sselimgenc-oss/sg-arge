# Argon paketi T19: 13 stratejinin kaynağını oku ve kurallarını aynen yaz

## Görev
Aşağıdaki 13 sayfayı aç. Her birinde stratejinin kurallarını **kaynakta yazdığı gibi** çıkar. Bu sayfalar daha önce otomatik okunamadı (JavaScript ya da koruma nedeniyle). Senin tarayıcın açabilir.

## Kurallar (zorunlu)
- **Uydurma yok.** Kaynakta olmayan değeri yazma; "kaynakta yok" yaz. Tahmin, örnek ya da "genelde şöyle kullanılır" yorumu yasak.
- **Giriş yapma, form doldurma, kişisel veri girme.** Sayfa üyelik istiyorsa kartı "okunamadı (üyelik)" olarak işaretle ve geç.
- Çerez penceresi çıkarsa "Tümünü reddet"i seç.
- Kod varsa (Pine, MQL, ProRealCode, AFL, Python, Matriks), **kodu olduğu gibi** kopyala, kısaltma.

## Kartlar ve sayfalar
| Kart | URL | Not |
|---|---|---|
| M003 | https://usethinkscript.com/threads/5min-es-futures-strategy-for-thinkorswim.9911/ | "Price" girdisi high mı low mu? Açıkça yaz. |
| A6-014 | https://financial-hacker.com/why-90-of-backtests-fail/ | Zorro kodu (LowPass, MMI) |
| O1-045 | https://www.prorealcode.com/prorealtime-trading-strategies/vectorial-dax-m5/ | |
| O1-050 | https://www.prorealcode.com/prorealtime-trading-strategies/eurusd-15-minutes-timeframe-dhigh-dlow-strategy/ | |
| A2-011 | https://www.mql5.com/en/code/78275 | |
| O1-006 | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/MOTT-4B-Kurgu | |
| O1-009 | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/MOTT-4-Kurgu-Stratejisi | O1-006 ile aynı mı? Farkı yaz. |
| O1-008 | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/Anil-Özekşi-Sistem-1 | |
| O1-010 | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/FirsatciTrend-4Bölge-LONG | |
| O1-013 | https://algokutuphanesi.com/Sistem/Detay/MatriksIq/OTT-STOCK-HHV-LLV-HOTT-LOTT-LONG | |
| O1-055 | https://www.wisestocktrader.com/indicators/4853-intraday-profit-maker-best-with-automation-for-amibroker-afl | |
| O2-017 | https://jesse.trade/strategies/tematrendfollowing | |
| O2-019 | https://jesse.trade/strategies/cloudscalper | |

## Her kart için yazılacaklar
```
## <Kart> — <strateji adı>
- kaynak_url: ...
- durum: okundu | okunamadı (<neden>)
- zaman_dilimi: ... (kaynakta yazan)
- enstrüman/piyasa: ... (kaynakta yazan)
- göstergeler ve parametreler: ... (ad = değer)
- giriş kuralı (long): ...
- çıkış kuralı: ...
- stop: ... | kaynakta yok
- hedef/kâr al: ... | kaynakta yok
- short kuralı varsa: ...
- kod (varsa, aynen):
  ```<dil>
  ...
  ```
- belirsiz kalanlar: ...
```

## Teslim
Tek dosya: `T19_kaynaklar.md`. Repoda `argon/` klasörüne yüklenir. Dosyanın sonuna tek satırlık bir özet ekle: `# ozet: okundu=<n>, okunamadi=<n>`.
