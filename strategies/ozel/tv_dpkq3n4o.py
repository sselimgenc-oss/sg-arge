"""TV-dpkq3n4O LinReg Scale-In: correlation(close, bar_index, 20) 0,25 / 0,50 / 0,75 yukari kesisimlerinde kademeli alim; 0,25 asagi kesisiminde hepsini kapat."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def correlation_with_index(s: pd.Series, length: int) -> pd.Series:
    """ta.correlation(s, bar_index, length): pencere ici Pearson korelasyonu; bar_index pencerede 0..length-1 ile ayni korelasyonu verir."""
    x = s.astype(float).to_numpy()
    t = np.arange(length, dtype=float)
    t = t - t.mean()
    out = np.full(len(x), np.nan)
    if len(x) >= length:
        windows = np.lib.stride_tricks.sliding_window_view(x, length)
        centered = windows - windows.mean(axis=1, keepdims=True)
        denom = np.sqrt((centered ** 2).sum(axis=1) * (t ** 2).sum())
        with np.errstate(divide="ignore", invalid="ignore"):
            out[length - 1:] = (centered @ t) / denom
    return pd.Series(out, index=s.index)


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    coeff = correlation_with_index(frame["close"], int(p["length"]))
    entry = (T.crossover(coeff, 0.25) | T.crossover(coeff, 0.50) | T.crossover(coeff, 0.75))
    exit_ = T.crossunder(coeff, 0.25)
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, pyramid_max=int(dict(card.get("piramit") or {}).get("en_cok", 0)))
