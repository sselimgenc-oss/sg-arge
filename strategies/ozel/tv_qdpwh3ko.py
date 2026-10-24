"""TV-qDPWh3KO TrendGuard Flag Finder [presentTrading]: boga/ayi bayrak (flag) durum makineleri + Supertrend yonu."""

from __future__ import annotations

import math
from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from strategies.ozel import tv_ortak as T

NA = float("nan")


def _na(x: float) -> bool:
    return isinstance(x, float) and math.isnan(x)


def flag_events(frame: pd.DataFrame, p: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """(plotBO, plotBD): boga bayrak kirilimi ve ayi bayrak asagi kirilimi, Pine `var` degiskenleriyle bar bar."""
    high = frame["high"].to_numpy(dtype=float)
    low = frame["low"].to_numpy(dtype=float)
    close = frame["close"].to_numpy(dtype=float)
    size = len(frame)
    hi10 = T.highest(frame["high"], 10).to_numpy()
    lo10 = T.lowest(frame["low"], 10).to_numpy()
    max_depth, max_flag, min_flag = float(p["max_depth"]), int(p["max_flag"]), int(p["min_flag"])
    pole_min, pole_max_len, pole_min_len = float(p["pole_min"]), int(p["pole_max_len"]), int(p["pole_min_len"])
    max_rally, max_flag_b, min_flag_b = float(p["max_rally"]), int(p["max_flag_bear"]), int(p["min_flag_bear"])
    pole_min_b, pole_max_len_b, pole_min_len_b = float(p["pole_min_bear"]), int(p["pole_max_len_bear"]), int(p["pole_min_len_bear"])
    # var degiskenleri
    base_high, start_index, flag_length, base_low = high[0], 0.0, 0, low[0]
    low_index, flag_bool, pole_low, pole_low_index = 0.0, False, 0.0, 0.0
    flag_low_bear, start_index_bear, flag_length_bear, flag_high = high[0], 0.0, 0, low[0]
    high_index, flag_bool_bear, pole_high, pole_high_index = 0.0, False, 0.0, 0.0
    prev_base_high = prev_flag_low_bear = NA
    prev_flag = prev_bear_flag = False
    prev_flag_length = prev_flag_length_bear = 0
    plot_bo = np.zeros(size, dtype=bool)
    plot_bd = np.zeros(size, dtype=bool)
    for i in range(size):
        h, l, c = high[i], low[i], close[i]
        if h > base_high or _na(base_high):
            base_high, start_index, flag_length, base_low, low_index = h, float(i), 0, l, float(i)
        if h <= base_high and l < base_low:
            base_low, low_index = l, float(i)
        if h <= base_high and low_index == start_index:
            base_low, low_index = l, float(i)
        if l < flag_low_bear or _na(flag_low_bear):
            flag_low_bear, start_index_bear, flag_length_bear, flag_high, high_index = l, float(i), 0, h, float(i)
        if l >= flag_low_bear and h > flag_high:
            flag_high, high_index = h, float(i)
        if l >= flag_low_bear and high_index == start_index_bear:
            flag_high, high_index = h, float(i)
        find_depth = abs((base_low / base_high - 1.0) * 100.0)
        find_rally = abs((flag_high / flag_low_bear - 1.0) * 100.0)
        lower_close = i > 0 and c < close[i - 1]
        higher_close = i > 0 and c > close[i - 1]
        if (h < base_high and find_depth <= max_depth) or (h == base_high and lower_close):
            flag_length += 1
        else:
            flag_length = 0
        if (l > flag_low_bear and find_rally <= max_rally) or (l == flag_low_bear and higher_close):
            flag_length_bear += 1
        else:
            flag_length_bear = 0
        if h == base_high:
            for k in range(pole_min_len, pole_max_len + 1):
                if i - k >= 0 and (h / low[i - k] - 1.0) * 100.0 >= pole_min:
                    flag_bool, pole_low, pole_low_index = True, low[i - k], float(i - k)
                    break
        if l == flag_low_bear:
            for k in range(pole_min_len_b, pole_max_len_b + 1):
                if i - k >= 0 and abs((l / high[i - k] - 1.0) * 100.0) >= pole_min_b:
                    flag_bool_bear, pole_high, pole_high_index = True, high[i - k], float(i - k)
                    break
        if find_depth >= max_depth or flag_length > max_flag:
            flag_bool, flag_length = False, 0
            base_high = start_index = low_index = base_low = NA
        if find_rally >= max_rally or flag_length_bear > max_flag_b:
            flag_bool_bear, flag_length_bear = False, 0
            flag_low_bear = start_index_bear = high_index = flag_high = NA
        if h > prev_base_high and flag_length < min_flag:
            base_high, flag_length, start_index, low_index, base_low = h, 0, float(i), float(i), l
        if l < prev_flag_low_bear and flag_length_bear < min_flag_b:
            flag_low_bear, flag_length_bear, start_index_bear, high_index, flag_high = l, 0, float(i), float(i), h
        flag = flag_bool and flag_length < max_flag and find_depth < max_depth and flag_length >= min_flag and (start_index - pole_low_index <= pole_max_len)
        bear_flag = flag_bool_bear and flag_length_bear < max_flag_b and find_rally < max_rally and flag_length_bear >= min_flag_b and (start_index_bear - pole_high_index <= pole_max_len)
        breakout = h > prev_base_high and flag_length >= min_flag and flag_bool
        breakdown = find_depth >= max_depth or flag_length > max_flag
        plot_bo[i] = prev_flag and h > prev_base_high and prev_flag_length >= min_flag and flag_bool
        breakout_bear = l < prev_flag_low_bear and flag_length_bear >= min_flag_b and flag_bool_bear
        breakdown_bear = find_rally >= max_rally or flag_length_bear > max_flag_b
        plot_bd[i] = prev_bear_flag and l < prev_flag_low_bear and prev_flag_length_bear >= min_flag_b and flag_bool_bear
        if breakout:
            flag_length, base_high, start_index, low_index, base_low = 0, h, float(i), float(i), l
        if breakout_bear:
            flag_length_bear, flag_low_bear, start_index_bear, high_index, flag_high = 0, l, float(i), float(i), h
        if breakdown or flag_length == max_flag:
            flag_bool, base_high, start_index, low_index, base_low = False, hi10[i], float(i), float(i), l
        if breakdown_bear or flag_length_bear == max_flag_b:
            flag_bool_bear, flag_low_bear, start_index_bear, high_index, flag_high = False, lo10[i], float(i), float(i), h
        prev_base_high, prev_flag_low_bear = base_high, flag_low_bear
        prev_flag, prev_bear_flag = flag, bear_flag
        prev_flag_length, prev_flag_length_bear = flag_length, flag_length_bear
    return plot_bo, plot_bd


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    plot_bo, plot_bd = flag_events(frame, p)
    st = g.supertrend(frame, int(p["supertrend_period"]), float(p["supertrend_factor"]))
    bull = (st["dir"] == 1).to_numpy()
    bear = (st["dir"] == -1).to_numpy()
    bullish_entry = plot_bo & bull
    bearish_entry = plot_bd & bear
    return pd.DataFrame({"entry": bullish_entry, "exit": bearish_entry, "atr": T.atr(frame, 14), "_stop_level": st["line"]}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
