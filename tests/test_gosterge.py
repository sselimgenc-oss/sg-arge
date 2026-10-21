from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from engine import gosterge as ind
from engine import takvim


def frame(close, high=None, low=None, volume=None, open_=None, freq="D", start="2024-01-01"):
    close = np.asarray(close, dtype=float)
    idx = pd.date_range(start, periods=len(close), freq=freq)
    return pd.DataFrame(
        {
            "open": close if open_ is None else open_,
            "high": close if high is None else high,
            "low": close if low is None else low,
            "close": close,
            "volume": np.ones(len(close)) if volume is None else volume,
        },
        index=idx,
    )


WILDER = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64]


def test_sma_and_ema_seeded_with_sma():
    df = frame(range(1, 11))
    assert ind.sma(df, n=3).iloc[2:].tolist() == [2, 3, 4, 5, 6, 7, 8, 9]
    # seed = SMA(1,2,3) = 2, then alpha 0.5: 3, 4, 5, ...
    out = ind.ema(df, n=3)
    assert out.iloc[:2].isna().all()
    assert out.iloc[2:].tolist() == [2, 3, 4, 5, 6, 7, 8, 9]


def test_rma_wilder_smoothing():
    s = pd.Series([2.0, 4.0, 6.0, 8.0, 10.0])
    out = ind.rma(s, 2)  # seed 3, alpha .5: 3 -> 5 -> 7.5? (6+3)/2=4.5
    assert out.iloc[1] == 3.0
    assert out.iloc[2] == pytest.approx(4.5)
    assert out.iloc[3] == pytest.approx(6.25)


def test_rsi_matches_hand_calculation():
    # first 14 changes: gains 3.34, losses 1.40 -> RSI = 100 - 100 / (1 + 3.34 / 1.40)
    out = ind.rsi(frame(WILDER), n=14).dropna()
    assert out.iloc[0] == pytest.approx(100 - 100 / (1 + 3.34 / 1.40), abs=1e-6)
    assert out.iloc[0] == pytest.approx(70.46, abs=0.01)
    assert out.iloc[1] == pytest.approx(66.25, abs=0.01)


def test_rsi_all_gains_is_100():
    assert ind.rsi(frame(range(1, 30)), n=14).dropna().eq(100.0).all()


def test_true_range_and_atr_constant_range():
    df = frame([10] * 30, high=[11] * 30, low=[9] * 30)
    tr = ind.true_range(df)
    assert tr.eq(2.0).all()
    assert ind.atr(df, 14).dropna().eq(2.0).all()


def test_true_range_uses_gaps():
    df = frame([10, 20], high=[10, 21], low=[10, 19])
    assert ind.true_range(df).tolist() == [0.0, 11.0]  # |21 - 10| beats high-low=2


def test_stdev_population_and_bb():
    df = frame([1, 2, 3, 4, 5])
    assert ind.stdev(df, n=5).iloc[-1] == pytest.approx(np.sqrt(2.0))
    bands = ind.bb(df, n=5, carpan=2.0)
    assert bands["basis"].iloc[-1] == 3.0
    assert bands["upper"].iloc[-1] == pytest.approx(3 + 2 * np.sqrt(2.0))
    assert bands["lower"].iloc[-1] == pytest.approx(3 - 2 * np.sqrt(2.0))


def test_zscore_roc_wma_highest_lowest():
    df = frame([1, 2, 3, 4, 5])
    assert ind.zscore(df, n=5).iloc[-1] == pytest.approx(2 / np.sqrt(2.0))
    assert ind.roc(df, n=2).iloc[-1] == pytest.approx(100 * (5 / 3 - 1))
    assert ind.wma(df, n=3).iloc[-1] == pytest.approx((3 * 1 + 4 * 2 + 5 * 3) / 6)
    assert ind.highest(df, "close", 3).iloc[-1] == 5
    assert ind.lowest(df, "close", 3).iloc[-1] == 3


def test_stochastic_fast_and_smoothed():
    df = frame([5, 6, 7, 8, 9, 10], high=[6, 7, 8, 9, 10, 11], low=[4, 5, 6, 7, 8, 9])
    fast = ind.stoch(df, k=3, d=2, smooth=1)
    # last 3 bars: lowest low 7, highest high 11, close 10 -> (10 - 7) / (11 - 7) * 100
    assert fast["k"].iloc[-1] == pytest.approx(75.0)
    assert fast["d"].iloc[-1] == pytest.approx((75.0 + 75.0) / 2)


def test_macd_ema_difference_and_hist():
    df = frame(np.linspace(100, 130, 80))
    out = ind.macd(df, fast=12, slow=26, signal=9)
    expected = ind.ema(df, n=12) - ind.ema(df, n=26)
    assert out["macd"].dropna().iloc[-1] == pytest.approx(expected.iloc[-1])
    assert out["hist"].dropna().iloc[-1] == pytest.approx(out["macd"].iloc[-1] - out["signal"].iloc[-1])


def test_dmi_strong_uptrend():
    n = 60
    close = np.arange(n, dtype=float) + 100
    out = ind.dmi(frame(close, high=close + 1, low=close - 1), 14).dropna()
    assert (out["plus"] > out["minus"]).all()
    assert out["adx"].iloc[-1] > 80


def test_cci_known_value():
    df = frame([1, 2, 3, 4, 5])
    # tp = 1..5, mean 3, mean abs dev = 1.2 -> (5 - 3) / (0.015 * 1.2)
    assert ind.cci(df, 5).iloc[-1] == pytest.approx(2 / (0.015 * 1.2))


def test_obv_and_mfi_and_rvol():
    df = frame([1, 2, 1, 3], volume=[10, 20, 30, 40])
    assert ind.obv(df).tolist() == [0, 20, -10, 30]
    assert ind.rvol(frame([1] * 4, volume=[1, 1, 1, 5]), 4).iloc[-1] == pytest.approx(5 / 2)
    up = frame(np.arange(1, 20, dtype=float))
    assert ind.mfi(up, 14).dropna().eq(100.0).all()


def test_vwap_resets_each_day_and_equals_hlc3_on_daily():
    intraday = frame([10, 20, 30, 40], volume=[1, 1, 1, 3], freq="12h")
    out = ind.vwap(intraday)
    assert out.iloc[1] == pytest.approx(15.0)  # day 1: (10*1 + 20*1) / 2
    assert out.iloc[3] == pytest.approx((30 + 40 * 3) / 4)
    daily = frame([10, 20, 30])
    assert ind.vwap(daily).tolist() == [10, 20, 30]


def test_kama_converges_to_constant_price():
    assert ind.kama(frame([50.0] * 40), n=10).dropna().eq(50.0).all()


def test_ichimoku_lines_and_cloud_shift():
    close = np.arange(100, dtype=float)
    out = ind.ichimoku(frame(close, high=close, low=close))
    assert out["tenkan"].iloc[60] == (60 + 52) / 2
    assert out["kijun"].iloc[60] == (60 + 35) / 2
    assert np.isnan(out["span_b"].iloc[:77].to_numpy()).all()  # needs 52 bars + 26 shift


def test_supertrend_bullish_then_flips_on_crash():
    rising = np.concatenate([np.linspace(100, 160, 40), np.linspace(160, 80, 20)])
    out = ind.supertrend(frame(rising, high=rising + 1, low=rising - 1), n=10, carpan=2.0)
    assert out["dir"].iloc[30] == 1
    assert out["dir"].iloc[-1] == -1
    assert (out["line"].iloc[30] < rising[30]) and (out["line"].iloc[-1] > rising[-1])


def test_pmax_and_ott_directions():
    up = np.linspace(100, 200, 120)
    df = frame(up, high=up + 1, low=up - 1)
    assert ind.pmax(df, n=10, atr_n=10, carpan=3.0)["dir"].iloc[-1] == 1
    assert ind.ott(df, n=14, yuzde=1.4)["dir"].iloc[-1] == 1
    down = np.linspace(200, 100, 120)
    assert ind.pmax(frame(down, high=down + 1, low=down - 1), n=10, atr_n=10, carpan=3.0)["dir"].iloc[-1] == -1
    assert ind.ott(frame(down, high=down + 1, low=down - 1), n=14, yuzde=1.4)["dir"].iloc[-1] == -1


def test_ott_twin_columns():
    df = frame(np.linspace(100, 200, 120))
    out = ind.ott(df, n=14, yuzde=1.4, twin_katsayi=0.001)
    assert (out["up"].dropna() > out["dn"].dropna()).all()


def test_var_tracks_trend_and_is_smooth():
    df = frame(np.linspace(100, 200, 100))
    out = ind.var(df, n=9)
    assert out.iloc[-1] < 200 and out.iloc[-1] > 190
    assert out.is_monotonic_increasing


def test_atr_ratio_flat_volatility_is_one():
    df = frame([10.0] * 80, high=[11.0] * 80, low=[9.0] * 80)
    assert ind.atr_ratio(df, 14, 40).dropna().eq(1.0).all()


def test_rrs_zero_when_asset_moves_as_expected_and_positive_when_outperforming():
    n = 12
    close = 100 + np.arange(60, dtype=float)
    bench = frame(close, high=close + 1, low=close - 1)
    same = frame(close, high=close + 1, low=close - 1)
    assert ind.rrs(same, n=n, benchmark=bench).dropna().abs().max() < 1e-9
    strong = frame(close * 1.0 + np.arange(60) * 2.0, high=close + np.arange(60) * 2.0 + 1, low=close + np.arange(60) * 2.0 - 1)
    assert ind.rrs(strong, n=n, benchmark=bench).dropna().iloc[-1] > 0
    with pytest.raises(ValueError):
        ind.rrs(same, n=n)


def test_compute_kaydir_and_unknown_indicator():
    df = frame(range(1, 11))
    assert ind.compute(df, {"f": "sma", "src": "close", "n": 3, "kaydir": 1}).iloc[3] == 2.0
    with pytest.raises(ind.UnknownIndicator):
        ind.compute(df, {"f": "sar"})


def test_source_expression_and_build_env():
    df = frame([10, 12, 11, 13], high=[11, 13, 12, 14], low=[9, 11, 10, 12])
    env = ind.build_env(df, {"rng": {"f": "sma", "src": "high - low", "n": 2}, "hh": {"f": "highest", "src": "high", "n": 2, "kaydir": 1}})
    assert env["rng"].iloc[-1] == 2.0
    assert env["hh"].iloc[-1] == 13  # highest(high, 2) of bars 1..2, lagged one bar
    assert set(env) >= {"open", "high", "low", "close", "volume"}


def test_htf_alignment_uses_only_completed_weeks():
    idx = pd.bdate_range("2024-01-01", periods=15)  # 3 full weeks Mon-Fri
    close = np.concatenate([np.full(5, 10.0), np.full(5, 20.0), np.full(5, 30.0)])
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0}, index=idx)
    weekly_close = ind.compute(df, {"f": "close", "tf": "1W"})
    assert weekly_close.iloc[:5].isna().all()          # week 1: nothing completed yet
    assert weekly_close.iloc[5:10].eq(10.0).all()      # week 2 sees week 1 close
    assert weekly_close.iloc[10:15].eq(20.0).all()     # week 3 sees week 2 close
    # an indicator on weekly bars is aligned the same way
    weekly_sma = ind.compute(df, {"f": "sma", "src": "close", "n": 2, "tf": "1W"})
    assert weekly_sma.iloc[10:15].eq(15.0).all()


def test_htf_unsupported_timeframe():
    with pytest.raises(ValueError):
        ind.resample_htf(frame([1, 2, 3]), "1X")


def test_takvim_ranks():
    idx = pd.bdate_range("2024-01-01", "2024-02-29")
    assert idx[takvim.ay_islem_gunu_bastan(idx, 3).to_numpy()].strftime("%m-%d").tolist() == ["01-03", "02-05"]
    assert idx[takvim.ay_islem_gunu_sondan(idx, 5).to_numpy()].strftime("%m-%d").tolist() == ["01-25", "02-23"]
    assert takvim.haftanin_gunu(idx).iloc[0] == 0
    with pytest.raises(ValueError):
        takvim.ay_islem_gunu_bastan(idx, 0)


def test_takvim_intraday_marks_all_bars_of_the_day_and_handles_tz():
    idx = pd.date_range("2024-01-01", periods=48, freq="h", tz="UTC")
    flags = takvim.ay_islem_gunu_bastan(idx, 2)
    assert flags.sum() == 24
    assert idx[flags.to_numpy()].min() == pd.Timestamp("2024-01-02", tz="UTC")


def test_agrees_with_t1a_reference_functions_after_warmup():
    """engine.indicators (T1a, ewm seeded with the first value) and engine.gosterge
    (Pine, SMA seeded) differ only while the seed fades out."""
    from engine import indicators as ref

    rng = np.random.default_rng(7)
    close = 100 + np.cumsum(rng.normal(0, 1, 700))
    df = frame(close, high=close + rng.uniform(0.2, 1.5, 700), low=close - rng.uniform(0.2, 1.5, 700))
    start = 400
    checks = {
        "ema20": (ref.ema(df["close"], 20), ind.ema(df, n=20)),
        "rsi14": (ref.rsi(df["close"], 14), ind.rsi(df, n=14)),
        "atr14": (ref.atr(df, 14), ind.atr(df, 14)),
        "cci20": (ref.cci(df, 20), ind.cci(df, 20)),
    }
    for name, (reference, card) in checks.items():
        diff = (reference.iloc[start:] - card.iloc[start:]).abs().max()
        assert diff < 1e-6, f"{name}: max diff {diff}"
    assert (ref.true_range(df).iloc[1:] - ind.true_range(df).iloc[1:]).abs().max() == 0
