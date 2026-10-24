"""TV-WrEqzgAo PPO Divergence Strategy: PPO ve fiyat pivot dibi ayrismasi (pozitif uyumsuzluk) long girisi; stop %2 / hedef %4 sinyal
kapanisindan, ayni yonlu tekrar sinyal (yoksayilan giris) acik pozisyonun stop/hedef emrini yeniler (`dyn_stop` / `dyn_target`)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    slow = T.ema(close, int(p["slow_len"]))
    ppo = (T.ema(close, int(p["fast_len"])) - slow) / slow * 100.0
    lookback = int(p["pivot_len"])
    price_low = T.pivotlow(frame["low"], lookback, lookback).to_numpy(dtype=float)
    ppo_low = T.pivotlow(ppo, lookback, lookback).to_numpy(dtype=float)
    price_high = T.pivothigh(frame["high"], lookback, lookback).to_numpy(dtype=float)
    ppo_high = T.pivothigh(ppo, lookback, lookback).to_numpy(dtype=float)
    n = len(frame)
    bull, bear = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    prev_pl = prev_pp = last_pl = last_pp = np.nan
    prev_ph = prev_pph = last_ph = last_pph = np.nan
    for i in range(n):
        if not np.isnan(price_low[i]):
            prev_pl, prev_pp, last_pl, last_pp = last_pl, last_pp, price_low[i], ppo_low[i]
            bull[i] = not np.isnan([prev_pl, prev_pp, last_pl, last_pp]).any() and last_pl < prev_pl and last_pp > prev_pp
        if not np.isnan(price_high[i]):
            prev_ph, prev_pph, last_ph, last_pph = last_ph, last_pph, price_high[i], ppo_high[i]
            bear[i] = not np.isnan([prev_ph, prev_pph, last_ph, last_pph]).any() and last_ph > prev_ph and last_pph < prev_pph
    sl, tp = 1.0 - float(p["sl_pct"]) / 100.0, 1.0 + float(p["tp_pct"]) / 100.0
    signal_close = close.where(pd.Series(bull, index=frame.index))
    stop_level = (signal_close * sl).ffill()  # her yeni long sinyali (yoksayilan giris dahil) emri yeniler
    target_level = (signal_close * tp).ffill()
    return pd.DataFrame({"entry": bull, "exit": bear, "atr": T.atr(frame, 14), "dyn_stop": stop_level, "dyn_target": target_level,
                         "_stop_level": signal_close * sl, "_target_level": signal_close * tp}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
