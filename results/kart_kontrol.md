# Kart kontrol raporu

Kart sayisi: 403 | `tam` kartlarda hata: **0** | sorun bildirilen kart: 136
T5b taramasina hazir kart (`tam`, hatasiz, `ozel_kod: false`): **105**; ayrica `dakikalik` (yalniz kripto testi) hazir: **25**


## Durum dagilimi

| durum | kart |
|---|---|
| gizli | 35 |
| ihtiyari | 14 |
| sadece_short | 3 |
| eksik | 159 |
| dakikalik | 62 |
| tam | 126 |
| kapsam_disi | 4 |

## `tam` kartlarda hatalar (T5'e engel)

Yok.


## Kutuphanede olmayan gosterge adlari

| gosterge | kart sayisi | kartlar |
|---|---|---|
| - | 0 | |

## Ayristirilamayan giris/cikis ifadeleri

Toplam: 7 (durum `tam` olanlar once)

- A2-028 (eksik): giris: syntax error: invalid decimal literal :: mtf(1D, ema20_d1 > ema50_d1 and close > ema20_d1) and cross_over(stoch_ltf.k, 20)
- A3-005 (eksik): giris: syntax error: invalid syntax :: close ema200 yönünde and range_filtre
- A3-005 (eksik): cikis: syntax error: unterminated string literal (detected at line 1) :: stop %, hedef % (değerler README'de yok)
- O1-012 (gizli): giris: syntax error: invalid syntax :: formasyon onayı (ikili/üçlü dip, yükselen üçgen, bayrak)
- O1-012 (gizli): cikis: syntax error: invalid syntax. Perhaps you forgot a comma? :: (yarı hedef - onay)/onay*100 kâr al; zarar durdur
- O2-012 (kapsam_disi): cikis: syntax error: invalid syntax :: SL modu (puan/%bakiye/USD), başabaş, emir süresi
- O2-017 (dakikalik): giris: syntax error: invalid decimal literal :: cross_over(tema10, tema80) and adx14 > 40 and mtf(4h, tema20 > tema70)

## Tanimsiz adlar (ifadelerde kullanilan, gostergeler'de olmayan)

| ad | kullanim |
|---|---|
| major_trend_bull | 6 |
| upper_bound | 4 |
| mott_b1 | 4 |
| mott_b2 | 4 |
| mott_b3 | 4 |
| mott_b4 | 4 |
| mott_b5 | 4 |
| orb_high | 3 |
| halftrend | 2 |
| mov_var | 2 |
| ott_opt2 | 2 |
| session_time | 2 |
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
| percb | 2 |
| tsi_val | 2 |
| hma60 | 2 |
| bull_power | 2 |
| candle_color | 2 |
| daily_open | 2 |
| server_time | 2 |
| dynamic_avwap | 2 |
| lorentzian_skor | 2 |
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
| abc_zigzag_deseni | 1 |
| sma_bulutu_trend | 1 |
| macd_100_200_50_boga | 1 |
| mlcel_yeni_al_sinyali | 1 |
| up | 1 |
| down | 1 |
| ott_hhv | 1 |
| stosk_ott | 1 |
| ott_llv | 1 |
| stosk_ott_sat | 1 |
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
| blue | 1 |
| pink | 1 |
| pullback_confirmed | 1 |
| trendline_breakout | 1 |
| previous_swing_high | 1 |
| tdi_green | 1 |
| tdi_red | 1 |
| avg_vol_slot | 1 |
| tick_vol | 1 |
| burst_zscore | 1 |
| bbw_expansion | 1 |
| orb_low | 1 |
| order_block_boga | 1 |

## Diger kartlarda sorun sayisi

`tam` olmayan 126 kartta bilgi amacli bulgu var (ayrintilar yukaridaki tablolarda); kartlar degistirilmedi.

