"""strategies/ozel/tv_ortak.py ilkelleri: elle hesaplanmis Pine ta.* davranislari ve ileriye bakma yok."""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def series(values) -> pd.Series:
    return pd.Series(values, index=pd.date_range("2020-01-01", periods=len(values), freq="1D", tz="UTC"), dtype=float)


def test_pivothigh_ve_pivotlow_sag_bar_sonra_bilinir():
    s = series([1, 2, 5, 3, 2, 1, 1])
    out = T.pivothigh(s, 2, 2)
    assert out.iloc[4] == 5.0 and out.drop(out.index[4]).isna().all()   # bar 2 pivotu bar 4'te (right=2 sonra) bilinir
    low = T.pivotlow(series([5, 4, 1, 3, 4, 5, 5]), 2, 2)
    assert low.iloc[4] == 1.0 and low.drop(low.index[4]).isna().all()
    assert T.pivothigh(series([1, 5, 5, 3, 2, 1]), 2, 2).isna().all()    # esit zirve: sert esitsizlik, pivot yok


def test_percentrank_onceki_n_degere_gore():
    # x=[5,1,2,3]: n=3'te bar 3 (=3) icin onceki [5,1,2] icinden <= 3 olanlar {1,2} = 2/3 -> 66.67
    out = T.percentrank(series([5, 1, 2, 3]), 3)
    assert out.iloc[:3].isna().all() and abs(out.iloc[3] - 200 / 3) < 1e-9
    assert T.percentrank(series([1, 2, 3, 4]), 3).iloc[3] == 100.0


def test_hma_dogrusal_rampayi_aynen_verir():
    ramp = series(np.arange(1, 41, dtype=float))
    out = T.hma(ramp, 4)   # wma(2*wma(x,2) - wma(x,4), 2): x + 1/3 - 1/3 = x
    assert np.allclose(out.dropna().to_numpy(), ramp.loc[out.dropna().index].to_numpy())


def test_barssince_ve_valuewhen():
    cond = pd.Series([False, True, False, False, True, False], index=series([0] * 6).index)
    bs = T.barssince(cond)
    assert bs.isna().iloc[0] and list(bs.iloc[1:]) == [0, 1, 2, 0, 1]
    vals = series([10, 11, 12, 13, 14, 15])
    assert list(T.valuewhen(cond, vals, 0).iloc[1:]) == [11, 11, 11, 14, 14]
    assert list(T.valuewhen(cond, vals, 1).iloc[4:]) == [11, 11]        # bir onceki True'daki deger


def test_simulate_two_sided_bekleme_suresi_son_giristen_sayilir():
    n = 12
    price = np.full(n, 100.0)
    frame = pd.DataFrame({"open": price, "high": price.copy(), "low": price.copy(), "close": price.copy(), "volume": 1.0},
                         index=pd.date_range("2020-01-01", periods=n, freq="1D", tz="UTC"))
    frame.iloc[6, frame.columns.get_loc("low")] = 89.0          # bar 6'da stop (90) vurulur (stop bar 4'ten etkin)
    long_ok = np.zeros(n, dtype=bool)
    long_ok[[2, 4, 6, 7]] = True
    nan = np.full(n, np.nan)
    entry, flip = T.simulate_two_sided(frame, long_ok, np.zeros(n, dtype=bool), np.full(n, 90.0), np.full(n, 110.0), nan, nan, cooldown=5)
    # bar 2 sinyali: bar 3'te dolar (stop bar 4'ten etkin). Bar 4: pozisyon acik -> yok. Bar 6: stop vurulur, ama 6-2 = 4 < 5 -> bekleme.
    # Bar 7: 7-2 = 5 >= 5 ve pozisyon yok -> ikinci giris.
    assert list(np.flatnonzero(entry)) == [2, 7] and not flip.any()


def test_ilkeller_ileriye_bakmaz():
    rng = np.random.default_rng(3)
    base = pd.Series(100 + rng.normal(0, 1, 300).cumsum(), index=pd.date_range("2020-01-01", periods=300, freq="1D", tz="UTC"))
    for fn in (lambda s: T.pivothigh(s, 3, 2), lambda s: T.pivotlow(s, 3, 2), lambda s: T.percentrank(s, 20), lambda s: T.hma(s, 14),
               lambda s: T.barssince(s > s.shift(1)), lambda s: T.ema(s, 10), lambda s: T.rma(s, 10)):
        full = fn(base)
        cut = fn(base.iloc[:200])
        pd.testing.assert_series_equal(full.iloc[:200], cut, check_names=False)


def test_simulate_two_sided_flat_only_ve_kapanistan_bekleme():
    n = 30
    idx = pd.date_range("2022-01-01", periods=n, freq="1D", tz="UTC")
    price = np.full(n, 100.0)
    frame = pd.DataFrame({"open": price, "high": price + 1, "low": price - 1, "close": price, "volume": 1.0}, index=idx)
    frame.loc[idx[3], "low"] = 85.0  # bar 3: dolum sonrasi stop (90) vurulur
    long_ok = np.zeros(n, dtype=bool)
    long_ok[[1, 4, 5, 12]] = True
    nan = np.full(n, np.nan)
    # bar 1 sinyal -> bar 2 dolum; stop 90 / hedef 110 sinyalde sabit; bar 3'te stop. Bekleme 6: bar 3'ten itibaren bar 9'a kadar yeni giris yok.
    entry, _ = T.simulate_two_sided(frame, long_ok, np.zeros(n, dtype=bool), np.full(n, 90.0), np.full(n, 110.0), nan, nan,
                                    cooldown=6, exits_from_fill_bar=True, flat_only=True, cooldown_from_exit=True)
    assert list(np.flatnonzero(entry)) == [1, 12]  # 4 ve 5 bekleme icinde, 12 bekleme disinda


def test_simulate_two_sided_fill_pct_dolum_fiyatindan_olcer():
    n = 12
    idx = pd.date_range("2022-01-01", periods=n, freq="1D", tz="UTC")
    price = np.full(n, 100.0)
    frame = pd.DataFrame({"open": price, "high": price + 1, "low": price - 1, "close": price, "volume": 1.0}, index=idx)
    frame.loc[idx[3], "low"] = 98.0   # dolum (bar 2) acilisi 100: stop %1,5 = 98.5 -> bar 3'te vurulur
    long_ok = np.zeros(n, dtype=bool)
    long_ok[[1, 4, 6]] = True
    nan = np.full(n, np.nan)
    entry, _ = T.simulate_two_sided(frame, long_ok, np.zeros(n, dtype=bool), nan, nan, nan, nan, flat_only=True, fill_pct=(0.015, 0.03))
    # bar 1 giris (bar 2 dolum), bar 3'te stop -> bar 4 sinyali yeni giris olur; bar 5'te pozisyon (bar 5 dolum) acik, bar 6 sinyali yok sayilir
    assert list(np.flatnonzero(entry)) == [1, 4]
