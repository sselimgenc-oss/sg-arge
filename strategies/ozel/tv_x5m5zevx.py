"""TV-X5M5zevX Code A - Terminal Core: HMA egimi + WaveTrend/para akisi/stokastik/PSAR/seri sayaci filtreleri; mandalli (var) tekrar sinyal engeli."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from strategies.ozel import tv_ortak as T


def _stoch(frame: pd.DataFrame, n: int) -> pd.Series:
    lo, hi = T.lowest(frame["low"], n), T.highest(frame["high"], n)
    return 100.0 * (frame["close"] - lo) / (hi - lo).where(hi != lo)


def _round1(x: pd.Series) -> pd.Series:
    return np.sign(x) * np.floor(np.abs(x) * 10.0 + 0.5) / 10.0


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, open_, high, low = frame["close"], frame["open"], frame["high"], frame["low"]
    hl2 = (high + low) / 2.0
    hlc3 = (high + low + close) / 3.0
    lookback = int(p["lookback"])
    hline = T.hma(hl2, int(p["trend_length"]))
    nxt = hline.shift(1) + (hline.shift(1) - hline.shift(lookback + 1)) / lookback
    curve = pd.Series(np.where(hline > nxt, 1, -1), index=frame.index)
    esa = T.ema(hlc3, 9)
    d = T.ema((hlc3 - esa).abs(), 9)
    w1 = T.ema((hlc3 - esa) / (0.015 * d), 12)
    w2 = T.sma(w1, 3)
    df = _round1(w1 - w2)
    mf = T.sma((close - open_) / (high - low) * 200.0, 60) - 2.25
    k1 = T.sma(_stoch(frame, 40), 2)
    k2 = T.sma(_stoch(frame, 80), 2)
    # f_a4: i = 11..20 icin close > close[i] ? +1 : -1 toplami, wma(.., smoothing)
    score = sum(np.where(close > close.shift(i), 1.0, -1.0) for i in range(11, 21))  # na karsilastirmasi yanlis -> -1
    bias = T.wma(pd.Series(score, index=frame.index), int(p["smoothing"])) * (100.0 / 12.0)
    ea, eb, ec = T.ema(close, 5), T.ema(close, 11), T.ema(close, 33)
    up_count = np.zeros(len(frame))
    dn_count = np.zeros(len(frame))
    c = close.to_numpy(dtype=float)
    for i in range(len(c)):
        up_count[i] = (up_count[i - 1] + 1.0) if i >= 4 and c[i] > c[i - 4] else 0.0
        dn_count[i] = (dn_count[i - 1] + 1.0) if i >= 4 and c[i] < c[i - 4] else 0.0
    up_s, dn_s = pd.Series(up_count, index=frame.index), pd.Series(dn_count, index=frame.index)
    run_up = up_s - T.valuewhen(up_s < up_s.shift(1), up_s, 1)
    run_dn = dn_s - T.valuewhen(dn_s < dn_s.shift(1), dn_s, 1)
    anchor = g.sar(frame, float(p["psar_step"]), float(p["psar_max"]))  # Pine ta.sar(0,01; 0,01; 0,1): baslangic = artis = 0,01
    r1, r3, r4, t0 = float(p["difference"]), float(p["bands1"]), float(p["bands2"]), float(p["max_series"])

    h_lime = (curve != -1) & (hline > hline.shift(1))
    h_red = (curve != 1) & (hline < hline.shift(1))
    xw_l = T.crossover(w1, w2) | T.crossover(w1.shift(2), w2.shift(2))
    xw_s = T.crossunder(w1, w2) | T.crossunder(w1.shift(2), w2.shift(2))
    x_l = T.crossover(eb, ec) | xw_l
    x_s = T.crossunder(ea, eb) | xw_s
    pa_l = (w2 > 0) & (mf > 0) & (w2 < r4)
    pa_s = (w2 < 0) & (mf <= 0) & (w2 > -r4)
    pb_l = (w2 < 0) & (k1 > k2) & (w2 < -r3)
    pb_s = (w2 > 0) & (k1 <= k2) & (w2 > r3)
    c6 = (bias > bias.shift(1)) | (bias >= 83) | (bias <= -83)
    c7 = (bias < bias.shift(1)) | (bias <= -83) | (bias >= 83)
    vol_ok = frame["volume"] >= float(p["min_volume"])
    a_l = (high.shift(1) < high) & x_l & (run_up <= t0) & (close > anchor)
    b_l = (open_ > open_.shift(1)) & (close > close.shift(1)) & (np.minimum(open_, close) == low) & (df >= r1)
    a_s = (low.shift(1) > low) & x_s & (run_dn <= t0) & (close < anchor)
    b_s = (open_ < open_.shift(1)) & (close < close.shift(1)) & (np.maximum(open_, close) == high) & (df <= -r1)
    c_l_base = (h_lime & (pa_l | pb_l) & c6 & vol_ok).to_numpy(dtype=bool)
    c_s_base = (h_red & (pa_s | pb_s) & c7 & vol_ok).to_numpy(dtype=bool)
    ab_l = (a_l & b_l).fillna(False).to_numpy(dtype=bool)
    ab_s = (a_s & b_s).fillna(False).to_numpy(dtype=bool)
    lime, red = h_lime.to_numpy(dtype=bool), h_red.to_numpy(dtype=bool)
    size = len(frame)
    sig_up = np.zeros(size, dtype=bool)
    sig_dn = np.zeros(size, dtype=bool)
    g_l = g_s = True
    for i in range(size):
        if not lime[i]:
            g_l = True
        if not red[i]:
            g_s = True
        sig_up[i] = ab_l[i] and c_l_base[i] and g_l
        sig_dn[i] = ab_s[i] and c_s_base[i] and g_s
        if sig_up[i]:
            g_l = False
        if sig_dn[i]:
            g_s = False
    exit_l = ((close < open_) & (df <= 0.2)).fillna(False).to_numpy(dtype=bool)
    return pd.DataFrame({"entry": sig_up, "exit": exit_l | sig_dn, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
