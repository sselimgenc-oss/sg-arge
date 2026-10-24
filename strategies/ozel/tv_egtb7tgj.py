"""TV-egTb7TgJ Gaussian Channel ETH: 4 kutuplu Gauss filtresi (hlc3) ve filtrelenmis gercek aralik bantlari, Stoch RSI ve SMA(200) rejim
kapisi; cikis bant alti kapanis ya da filtre dususu; stop her barda alt banttir (`dyn_stop`)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def gaussian(values: np.ndarray, alpha: float, poles: int) -> np.ndarray:
    """Ehlers n-kutuplu Gauss filtresi (Pine f_filt9x): f = a^n s + sum_k (-1)^(k+1) C(n, k) (1 - a)^k f[k]; nz(f[k]) = 0."""
    from math import comb  # noqa: PLC0415

    x = 1.0 - alpha
    out = np.zeros(len(values))
    for i in range(len(values)):
        total = alpha ** poles * (values[i] if not np.isnan(values[i]) else 0.0)
        for k in range(1, poles + 1):
            prior = out[i - k] if i - k >= 0 else 0.0
            total += (-1) ** (k + 1) * comb(poles, k) * x ** k * prior
        out[i] = total
    return out


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, high, low = frame["close"], frame["high"], frame["low"]
    poles, per, mult = int(p["poles"]), int(p["period"]), float(p["tr_mult"])
    beta = (1 - np.cos(4 * np.arcsin(1) / per)) / (1.414 ** (2 / poles) - 1)
    alpha = -beta + np.sqrt(beta ** 2 + 2 * beta)
    source = ((high + low + close) / 3.0).to_numpy(dtype=float)
    prev_close = close.shift(1)
    true_range = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1, skipna=True)
    true_range = true_range.where(prev_close.notna(), high - low)  # ta.tr(true): ilk bar high - low
    filt = pd.Series(gaussian(source, alpha, poles), index=frame.index)
    filt_tr = pd.Series(gaussian(true_range.to_numpy(dtype=float), alpha, poles), index=frame.index)
    hband, lband = filt + filt_tr * mult, filt - filt_tr * mult
    rsi = T.rsi(close, int(p["rsi_len"]))
    lo, hi = T.lowest(rsi, int(p["stoch_len"])), T.highest(rsi, int(p["stoch_len"]))
    stoch = 100.0 * (rsi - lo) / (hi - lo).where(hi != lo)
    k = T.sma(stoch, int(p["stoch_k"]))
    rising = filt > filt.shift(1)
    regime = close > T.sma(close, int(p["regime_sma"]))
    entry = rising & (close > hband) & ((k > float(p["rsi_upper"])) | (k < float(p["rsi_lower"]))) & regime & (close > frame["open"])
    exit_ = (close < hband) | (filt < filt.shift(1))
    return pd.DataFrame({"entry": entry.fillna(False), "exit": exit_.fillna(False), "atr": T.atr(frame, 14), "dyn_stop": lband}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
