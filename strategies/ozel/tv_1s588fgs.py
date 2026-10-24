"""TV-1s588fgS Bollinger + RSI Live Radar: bant geri alim (reclaim) girisi, EMA(200) filtresi, %3 hedef / %1,5 stop (dolum fiyatindan)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    basis = T.sma(close, int(p["bb_length"]))
    dev = float(p["bb_mult"]) * T.stdev(close, int(p["bb_length"]))
    upper, lower = basis + dev, basis - dev
    rsi = T.rsi(close, int(p["rsi_length"]))
    ema = T.ema(close, int(p["ema_length"]))
    prev = close.shift(1)
    long_signal = (prev < lower.shift(1)) & (close > lower) & (rsi > float(p["rsi_oversold"]))
    short_signal = (prev > upper.shift(1)) & (close < upper) & (rsi < float(p["rsi_overbought"]))
    long_ok = (long_signal & (close > ema)).fillna(False).to_numpy(dtype=bool)
    short_ok = (short_signal & (close < ema)).fillna(False).to_numpy(dtype=bool)
    nan = np.full(len(frame), np.nan)
    entry, _ = T.simulate_two_sided(
        frame, long_ok, short_ok, nan, nan, nan, nan,
        flat_only=True, fill_pct=(float(p["stop_loss_pct"]) / 100.0, float(p["take_profit_pct"]) / 100.0),
    )
    return pd.DataFrame({
        "entry": entry, "exit": False, "atr": T.atr(frame, 14),
        "stop_pct": float(p["stop_loss_pct"]) / 100.0, "target_pct": float(p["take_profit_pct"]) / 100.0,
    }, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True)
