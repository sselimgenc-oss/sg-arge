"""TV-qUrvPAmT WLD 4H Auto Entry Confirmed: UT Bot izleyen stop kesisimi + MACD/EMA50 onayi, 4 bar tutma ya da karsit onayli sinyalle cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from strategies.ozel import tv_ortak as T


def _ut_stop(src: np.ndarray, n_loss: np.ndarray) -> np.ndarray:
    stop = np.full(len(src), np.nan)
    for i in range(len(src)):
        prev = stop[i - 1] if i > 0 else np.nan
        s1 = src[i - 1] if i > 0 else np.nan
        if np.isnan(prev):
            stop[i] = src[i] - n_loss[i]
        elif src[i] > prev and s1 > prev:
            stop[i] = max(prev, src[i] - n_loss[i])
        elif src[i] < prev and s1 < prev:
            stop[i] = min(prev, src[i] + n_loss[i])
        elif src[i] > prev:
            stop[i] = src[i] - n_loss[i]
        else:
            stop[i] = src[i] + n_loss[i]
    return stop


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    src = close.to_numpy(dtype=float)
    n_loss = float(p["key_value"]) * T.atr(frame, int(p["atr_period"])).to_numpy(dtype=float)
    stop = pd.Series(_ut_stop(src, n_loss), index=frame.index)
    macd = g.macd(frame, "close", 12, 26, 9)
    ema50 = T.ema(close, int(p["ema_length"]))
    above = T.crossover(close, stop)  # ta.ema(src, 1) = src
    below = T.crossover(stop, close)
    buy_signal = ((close > stop) & above).to_numpy()
    sell_signal = ((close < stop) & below).to_numpy()
    buy_ok = (buy_signal & (macd["macd"] > macd["signal"]) & (close > ema50) & (frame["low"] > ema50)).fillna(False).to_numpy(dtype=bool)
    sell_ok = (sell_signal & (macd["macd"] < macd["signal"]) & (close < ema50) & (frame["high"] < ema50)).fillna(False).to_numpy(dtype=bool)
    opp_long = (sell_signal & (close < ema50) & (macd["macd"] < macd["signal"])).fillna(False).to_numpy(dtype=bool)  # signalType == long iken
    opp_short = (buy_signal & (close > ema50) & (macd["macd"] > macd["signal"])).fillna(False).to_numpy(dtype=bool)
    hold = int(p["max_bars_hold"])
    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    pos, entry_bar, pending = 0, -1, None
    signal_bar, signal_type = None, "none"
    for i in range(size):
        if pending == "L":
            if pos != 1:
                pos, entry_bar = 1, i
        elif pending == "S":
            if pos != -1:
                pos, entry_bar = -1, i
        elif pending == "C":
            pos = 0
        pending = None
        if signal_bar is None or i > signal_bar + hold:
            if buy_ok[i]:
                signal_bar, signal_type = i, "long"
            elif sell_ok[i]:
                signal_bar, signal_type = i, "short"
        enter_long = signal_type == "long" and i == signal_bar
        enter_short = signal_type == "short" and i == signal_bar
        if enter_long:
            pending = "L"
            entry[i] = pos != 1
        elif enter_short:
            pending = "S"
            exit_[i] = pos == 1
        exit_trade = False
        if pos != 0 and i - entry_bar >= hold:
            exit_trade = True
        if pos != 0 and ((signal_type == "long" and opp_long[i]) or (signal_type == "short" and opp_short[i])):
            exit_trade = True
        if exit_trade:
            pending = "C"
            exit_[i] = exit_[i] or pos == 1
            signal_bar, signal_type = None, "none"
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
