# Kart kontrol raporu

Kart sayisi: 203 | `tam` kartlarda hata: **0** | sorun bildirilen kart: 112
T5b taramasina hazir kart (`tam`, hatasiz, `ozel_kod: false`): **25**; ayrica `dakikalik` (yalniz kripto testi) hazir: **7**


## Durum dagilimi

| durum | kart |
|---|---|
| gizli | 2 |
| ihtiyari | 11 |
| sadece_short | 1 |
| eksik | 88 |
| dakikalik | 41 |
| tam | 58 |
| kapsam_disi | 2 |

## `tam` kartlarda hatalar (T5'e engel)

Yok.


## Kutuphanede olmayan gosterge adlari

| gosterge | kart sayisi | kartlar |
|---|---|---|
| alphatrend | 1 | O1-001 |
| chandelier | 1 | A3-002a |
| heikinashi | 1 | A3-010a |
| tema | 1 | O2-017 |
| zlsma | 1 | A3-002a |

## Ayristirilamayan giris/cikis ifadeleri

Toplam: 44 (durum `tam` olanlar once)

- A2-028 (eksik): giris: syntax error: invalid decimal literal :: mtf(1D, ema20_d1 > ema50_d1 and close > ema20_d1) and cross_over(stoch_ltf.k, 20)
- A3-005 (eksik): giris: syntax error: invalid syntax :: close ema200 yönünde and range_filtre
- A3-005 (eksik): cikis: syntax error: unterminated string literal (detected at line 1) :: stop %, hedef % (değerler README'de yok)
- O1-012 (gizli): giris: syntax error: invalid syntax :: formasyon onayı (ikili/üçlü dip, yükselen üçgen, bayrak)
- O1-012 (gizli): cikis: syntax error: invalid syntax. Perhaps you forgot a comma? :: (yarı hedef - onay)/onay*100 kâr al; zarar durdur
- O1-077 (eksik): giris: syntax error: invalid syntax :: close > ema_kisa and rsi > 50 and close > vwap and atr_volatilite_filtresi ; saat 12:30-16:30
- O1-077 (eksik): cikis: syntax error: invalid syntax :: iz süren stop / başabaş / zaman çıkışı / trend dönüşü / maks. düşüş eşiği
- O2-001 (ihtiyari): giris: syntax error: leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers :: 09:05-10:00 JST; 5 dk açılış aralığı kırılmış and (önceki gün H/L/C veya 2 günlük anchored VWAP destek olmuş) and close 
- O2-001 (ihtiyari): cikis: syntax error: invalid syntax :: geri çekilme dibi kırılırsa veya yeni zirvede veya 11:00 JST
- O2-002 (eksik): giris: syntax error: leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers :: 08:30 JST'ye kadar ADR +%100 hattının hemen üstüne buy limit
- O2-002 (eksik): cikis: syntax error: leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers :: ertesi gün 06:00 JST veya stop (ADR +%50 altı); dolmayan emir iptal
- O2-003 (ihtiyari): giris: syntax error: invalid syntax :: yükselen trendde (açık mavi mumlar) günlük açılış çizgisi üstünde long
- O2-004 (ihtiyari): cikis: syntax error: invalid syntax :: ilk hedef önceki tepe/dip (kısmi çıkış); stop önceki tepe/dip veya bir salınım öncesi
- O2-005 (ihtiyari): giris: syntax error: invalid syntax :: tdi_yesil cross_over tdi_kirmizi (3. mum veya sonrası ise girme) ; stoch(8,3,3) ve Heiken Ashi yön teyidi
- O2-005 (ihtiyari): cikis: syntax error: invalid syntax :: tdi_yesil yataylaşınca/kancalanınca
- O2-006 (ihtiyari): giris: syntax error: invalid syntax :: haftalık Fibonacci pivot 61-100 bölgesinde ; TDI yeşilin siyahı kesmesi ve fiyat aksiyonu teyidi
- O2-006 (ihtiyari): cikis: syntax error: invalid syntax :: tüccara bırakılmış (sabit kural yok)
- O2-007 (eksik): giris: syntax error: invalid syntax :: londra_acilisi_sonrasi and close > ema10 and tdi_yesil cross_over tdi_sari and close > ema200 ; (ema200 üstünde short yo
- O2-007 (eksik): cikis: syntax error: invalid syntax :: stop 20 pip; 12 pipte başabaş; TP 1:1 veya TDI ters kesişimi
- O2-010 (eksik): giris: syntax error: invalid syntax :: sunucu saati 11:00-14:59 and close > sma34 + 0.5 * stdev34 and macd_hist_atr < 0.2 and tick_hacim < 0.6 * normal ; sonra
- O2-010 (eksik): cikis: syntax error: invalid syntax :: SL 4*ATR, TP 3.5*ATR, 17:00 zorunlu kapanış
- O2-011 (eksik): giris: syntax error: unterminated string literal (detected at line 1) :: 4 sn pencerede hareket z-skoru > 3.0 (momentum veya ortalamaya dönüş modu) ; TP spread'in katı
- O2-011 (eksik): cikis: syntax error: invalid decimal literal :: ATR bazlı SL 0.55x / TP 0.35x ; süre aşımı ; günlük limit
- O2-012 (kapsam_disi): cikis: syntax error: invalid syntax :: SL modu (puan/%bakiye/USD), başabaş, emir süresi
- O2-017 (eksik): giris: syntax error: invalid decimal literal :: tema10 cross_over tema80 and adx > 40 and cmo_teyit ; 4h TEMA 20/70 trend filtresi
- O2-017 (eksik): cikis: syntax error: invalid syntax :: ATR bazlı stop/hedef (çarpanlar yok)
- O2-019 (eksik): cikis: syntax error: invalid syntax :: ATR bazlı SL/TP (çarpanlar yok)
- O2-025 (eksik): giris: syntax error: unterminated string literal (detected at line 1) :: kaldıraçlı ETF'ler arasında koşullu (RSI vb.) günlük geçişler (kural sayfada)
- O2-026 (eksik): giris: syntax error: unterminated string literal (detected at line 1) :: kaldıraçlı ETF'ler arasında koşullu (RSI vb.) günlük geçişler (kural sayfada)
- O2-027 (eksik): giris: syntax error: unterminated string literal (detected at line 1) :: kaldıraçlı ETF'ler arasında koşullu (RSI vb.) günlük geçişler (kural sayfada)
- O2-028 (eksik): giris: syntax error: unterminated string literal (detected at line 1) :: kaldıraçlı ETF'ler arasında koşullu (RSI vb.) günlük geçişler (kural sayfada)
- P3-003 (eksik): giris: syntax error: invalid syntax :: UT Bot ATR iz süren stop kırılımı (opsiyonel Heikin Ashi kaynağı)
- P3-003 (eksik): cikis: syntax error: invalid syntax :: ters UT Bot sinyali
- P3-004 (eksik): giris: syntax error: invalid syntax :: üç EMA eğim yönleri ve fiyat-EMA kesişimleri
- P3-004 (eksik): cikis: syntax error: invalid syntax :: ters pozisyona geçiş (sürekli long veya short)
- P3-006 (eksik): giris: syntax error: invalid syntax :: fiyat uyumsuzluğu (RicardoSantos Price Divergence V2) + Murrey Math Oscillator teyidi
- P3-008 (eksik): giris: syntax error: invalid syntax :: squeeze momentum (Bollinger/Keltner sıkışması + momentum) sinyali + özel filtreler
- P3-009 (eksik): giris: syntax error: invalid syntax :: Delta-RSI sinyal çizgisi kesişimi (+ seçilebilir filtreler)
- P3-009 (eksik): cikis: syntax error: invalid syntax :: ters sinyal veya TP/SL
- P3-011 (eksik): giris: syntax error: invalid syntax :: MACD sinyalleri
- P3-011 (eksik): cikis: syntax error: invalid syntax :: ATR iz süren stop
- P3-014 (eksik): giris: syntax error: invalid syntax :: pivot noktası kırılımı and stoch_rsi ile vwap kesişimi (mevcut/önceki mum) and kapanış trend yönünde
- P3-014 (eksik): cikis: syntax error: invalid syntax :: ters sinyal (belirtilmemiş)
- P3-015 (eksik): giris: syntax error: invalid syntax. Perhaps you forgot a comma? :: close > sma200 and close < sma10 (200 MA üstünde 10 MA altına geri çekilmede al; başlıktan)

## Tanimsiz adlar (ifadelerde kullanilan, gostergeler'de olmayan)

| ad | kullanim |
|---|---|
| major_trend_bull | 6 |
| mott_b1 | 4 |
| mott_b2 | 4 |
| mott_b3 | 4 |
| mott_b4 | 4 |
| mott_b5 | 4 |
| fisher_rsi | 3 |
| orb_high | 2 |
| ha_close | 2 |
| ha_open | 2 |
| sar | 2 |
| fastd | 2 |
| fastk | 2 |
| alphatrend | 2 |
| mov_var | 2 |
| ott_opt2 | 2 |
| session_time | 2 |
| pvt1 | 2 |
| pvt2 | 2 |
| willr3 | 2 |
| most | 2 |
| strend | 2 |
| sott1_bull | 2 |
| sott2_bull | 2 |
| tott1_bull | 2 |
| tott2_bull | 2 |
| sott3_bear | 2 |
| sott4_bear | 2 |
| tott3_bear | 2 |
| tott4_bear | 2 |
| lrsi | 2 |
| percb | 2 |
| tsi_val | 2 |
| hma60 | 2 |
| bull_power | 2 |
| box_bot | 2 |
| belirtilmemiş | 2 |
| ema_hizli | 2 |
| ema_yavas | 2 |
| lorentzian_skor | 2 |
| ml_skor | 2 |
| InpEntryHour | 1 |
| InpEntryWindowMin | 1 |
| InpMaxSpreadPts | 1 |
| InpSkipMonday | 1 |
| day_of_week | 1 |
| minute | 1 |
| server_hour | 1 |
| spread_pts | 1 |
| at_support | 1 |
| is_engulfing_bull | 1 |
| is_inside_bar_bull | 1 |
| is_pin_bar_bull | 1 |
| avg_vol | 1 |
| body | 1 |
| range | 1 |
| buffer | 1 |
| is_nr_day | 1 |
| offset | 1 |
| session_open | 1 |
| dir_flip_to_1 | 1 |
| chandelier_long_stop | 1 |
| down_fractal2 | 1 |
| abc_zigzag_deseni | 1 |
| sma_bulutu_trend | 1 |
| andean_bull_signal_cross | 1 |
| gunluk_yuksek_dusuk_onayi | 1 |
| macd_100_200_50_boga | 1 |
| mlcel_yeni_al_sinyali | 1 |
| nw_alt | 1 |
| nw_ust | 1 |
| linreg_sinyal | 1 |
| ut_bot_al | 1 |
| bb_typical_alt | 1 |
| cdl_hammer | 1 |
| stoch_slowk | 1 |
| fisher_rsi_norma | 1 |
| ott_hhv | 1 |
| stosk_ott | 1 |
| ott_llv | 1 |
| stosk_ott_sat | 1 |
| di | 1 |
| de | 1 |
| ott2_bull | 1 |
| ott3_bull | 1 |
| stoc1_bull | 1 |
| stoc2_bull | 1 |
| ott4_bear | 1 |
| ott5_bear | 1 |
| stoc3_bear | 1 |
| stoc4_bear | 1 |
| firsatci_bull | 1 |
| hhv11_ott | 1 |
| hhv8_ott | 1 |
| llv23_ott | 1 |
| hott1 | 1 |
| hott2 | 1 |
| lott1 | 1 |
| lott2 | 1 |
| qqe_mod_bull | 1 |
| ssl_baseline_bull | 1 |
| qqe_mod_bear | 1 |
| ssl_baseline_bear | 1 |
| lo | 1 |
| hi | 1 |
| angle | 1 |
| pente | 1 |
| trigger | 1 |
| hil | 1 |
| milieu | 1 |
| mm | 1 |
| surachat | 1 |
| tema5 | 1 |
| wt_cross_up | 1 |
| premarket_high | 1 |
| lod_bar_high | 1 |
| bmp | 1 |
| wae_explosion | 1 |
| wae_trend_up | 1 |
| wae_trend_down | 1 |
| box_top | 1 |
| cr3 | 1 |
| im2 | 1 |
| lr25 | 1 |
| entry_close | 1 |
| highest_close_since_entry | 1 |
| cam_r4 | 1 |
| cam_s3 | 1 |
| cam_r3 | 1 |
| cam_s4 | 1 |
| low_ref | 1 |
| yok | 1 |
| macd_signal | 1 |
| adx_teyit | 1 |
| bb_genislik_teyit | 1 |
| ichimoku_trend | 1 |
| order_block_boga | 1 |
| weekly_trend | 1 |
| confluence_puan | 1 |

## Diger kartlarda sorun sayisi

`tam` olmayan 90 kartta bilgi amacli bulgu var (ayrintilar yukaridaki tablolarda); kartlar degistirilmedi.

