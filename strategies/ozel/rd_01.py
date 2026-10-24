"""RD-01 SPY/QQQ dip alimi (arastirma/reddit/ozet.md A): kapanis > SMA(200) iken RSI(2) < 10 ya da 3 dusen kapanis ya da IBS < 0,2
sinyalinde ertesi acilista al; ilk kapanis > SMA(5) ya da 10 gun dolunca ertesi acilista sat; %8 stop; stoptan sonra yeniden giris
icin once kapanis > SMA(5) beklenir (durum makinesi)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, open_, high, low = (frame[c].to_numpy(dtype=float) for c in ("close", "open", "high", "low"))
    sma_trend = T.sma(frame["close"], int(p["trend_sma"])).to_numpy(dtype=float)
    sma_exit = T.sma(frame["close"], int(p["exit_sma"])).to_numpy(dtype=float)
    rsi = T.rsi(frame["close"], int(p["rsi_length"])).to_numpy(dtype=float)
    span = high - low
    with np.errstate(divide="ignore", invalid="ignore"):
        ibs = np.where(span > 0, (close - low) / span, np.nan)
    falling = int(p["falling_closes"])
    n = len(close)
    entry, exit_ = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    stop_frac, max_days = float(p["stop_pct"]) / 100.0, int(p["max_days"])
    in_pos, fill_bar, fill_price, pending_entry = False, -1, np.nan, -1
    locked, stop_bar = False, -1
    for i in range(n):
        if pending_entry == i:  # emir bu barin acilisinda dolar
            in_pos, fill_bar, fill_price, pending_entry = True, i, open_[i], -1
        if locked and i > stop_bar and close[i] > sma_exit[i]:
            locked = False  # stoptan sonra once kapanis > SMA(5)
        if in_pos:
            if low[i] <= fill_price * (1.0 - stop_frac):  # motorun stopu bar icidir; yazarinki kapanis tabanli (belirsiz:)
                in_pos, locked, stop_bar = False, True, i
                continue
            if close[i] > sma_exit[i] or i - fill_bar + 1 >= max_days:
                exit_[i] = True
                in_pos = False  # cikis sonraki acilista; yeni sinyal sonraki barda aranir
                stop_bar = -1
                continue
            continue
        if pending_entry >= 0 or locked or i + 1 >= n:
            continue
        three_down = i >= falling and all(close[i - k] < close[i - k - 1] for k in range(falling))
        dip = rsi[i] < float(p["rsi_below"]) or three_down or ibs[i] < float(p["ibs_below"])
        if close[i] > sma_trend[i] and dip:
            entry[i] = True
            pending_entry = i + 1
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14), "stop_pct": stop_frac}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True)
