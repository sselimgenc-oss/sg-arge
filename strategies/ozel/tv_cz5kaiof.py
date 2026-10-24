"""TV-cz5KaioF EMA 40 Pullback Pyramid: EMA(40) egim donusu / geri cekilme / EMA kesisimi girisleri (en fazla 3 birim), egim ya da kesisim donusunde hepsini kapat."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, open_, low = frame["close"], frame["open"], frame["low"]
    fast = T.ema(close, int(p["fast_len"]))
    adx = T.dmi(frame, int(p["di_len"]))["adx"]
    atr = T.atr(frame, int(p["atr_len"]))
    col_up = (fast > fast.shift(1)).fillna(False)
    col_down = (fast < fast.shift(1)).fillna(False)
    bull_flip = (col_up & ~col_up.shift(1, fill_value=False)).to_numpy(dtype=bool)
    bear_flip = (col_down & ~col_down.shift(1, fill_value=False)).to_numpy(dtype=bool)
    adx_ok = (adx > float(p["adx_thresh"])).fillna(False).to_numpy(dtype=bool)
    trend_in = col_up.to_numpy(dtype=bool) & adx_ok
    base_entry = bull_flip & adx_ok
    touched = (low <= fast + atr * float(p["pullback_atr"])).fillna(False).to_numpy(dtype=bool)
    recovered = ((close > fast) & (close > open_)).fillna(False).to_numpy(dtype=bool)
    ema_buy = T.crossover(close, fast).to_numpy()
    ema_sell = T.crossunder(close, fast).to_numpy()
    start = pd.Timestamp(str(p["start"]), tz="UTC")
    time_ok = np.asarray(frame.index >= start)
    gap = int(p["min_bars_between_entries"])
    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    armed = False
    last_entry = None
    for i in range(size):
        candidate = trend_in[i] and (armed or touched[i]) and recovered[i] and not base_entry[i]
        exit_cond = (bear_flip[i] or ema_sell[i]) and time_ok[i]
        can_enter = last_entry is None or i - last_entry >= gap
        long_cond = (base_entry[i] or candidate or (ema_buy[i] and time_ok[i])) and can_enter and time_ok[i]
        if long_cond:
            entry[i] = True
            last_entry = i
        if exit_cond:
            exit_[i] = True
        if not trend_in[i] or exit_cond:
            armed = False
        elif candidate:
            armed = False
        elif touched[i]:
            armed = True
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, pyramid_max=int(dict(card.get("piramit") or {}).get("en_cok", 0)))
