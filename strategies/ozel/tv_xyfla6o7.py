"""TV-xYflA6O7 Sadashi Market Reversion: fiyat/volatilite/katilim z-skorlarindan agirlikli 'edge' skoru; edge esik kesisimi ile giris/cikis."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def _score(z: pd.Series, scale: float) -> pd.Series:
    return 100.0 * (1.0 - np.exp(-z.abs() / scale))


def _zscore(s: pd.Series, mean: pd.Series, dev: pd.Series) -> pd.Series:
    return ((s - mean) / dev).where(dev != 0, 0.0)


def linreg_slope(s: pd.Series, n: int) -> pd.Series:
    """ta.linreg(s, n, 0) - ta.linreg(s, n, 1) = regresyon dogrusunun egimi (bar basina)."""
    x = np.arange(n, dtype=float)
    w = x - x.mean()
    sxx = float((w ** 2).sum())
    y = s.astype(float).to_numpy()
    out = np.full(len(y), np.nan)
    if len(y) >= n:
        windows = np.lib.stride_tricks.sliding_window_view(y, n)
        out[n - 1:] = windows @ w / sxx
    return pd.Series(out, index=s.index)


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, high, low = frame["close"], frame["high"], frame["low"]
    z_price = _zscore(close, T.sma(close, int(p["z_length"])), T.stdev(close, int(p["z_length"])))
    score_price = _score(z_price, float(p["price_scale"]))

    ret = (close - close.shift(1)) / close.shift(1)
    vol = T.stdev(ret, int(p["vol_length"]))
    z_vol = _zscore(vol, T.sma(vol, int(p["vol_norm"])), T.stdev(vol, int(p["vol_norm"])))
    score_vol = _score(z_vol, float(p["vol_scale"]))

    dollar = close * frame["volume"]
    z_part = _zscore(dollar, T.sma(dollar, int(p["part_norm"])), T.stdev(dollar, int(p["part_norm"])))
    score_part = _score(z_part, float(p["part_scale"]))

    n = int(p["trend_length"])
    normalized = linreg_slope(close, n) / close * 10000.0
    hi, lo = T.highest(high, n), T.lowest(low, n)
    hh = (hi > hi.shift(n)).astype(float) * 25.0
    hl = (lo > lo.shift(n)).astype(float) * 25.0
    slope_score = 50.0 * (1.0 / (1.0 + np.exp(-normalized / float(p["trend_scale"]))))
    score_trend = (slope_score + hh + hl).clip(lower=0.0, upper=100.0)

    weights = [float(p["price_weight"]), float(p["vol_weight"]), float(p["part_weight"]), float(p["trend_weight"])]
    total = sum(weights)
    edge = (score_price * weights[0] + score_vol * weights[1] + score_part * weights[2] + score_trend * weights[3]) / total

    cross_buy = T.crossover(edge, float(p["edge_buy"])).to_numpy()
    exit_long = T.crossunder(edge, float(p["edge_exit_long"])).to_numpy()
    cross_sell = T.crossover(edge, float(p["edge_sell"])).to_numpy()
    exit_short = T.crossunder(edge, float(p["edge_exit_short"])).to_numpy()
    common = ((z_vol >= float(p["min_vol_z"])) & (z_part >= float(p["min_part_z"]))).to_numpy()
    long_ok = cross_buy & common & (z_price < -float(p["min_z"])).to_numpy() & (score_trend >= float(p["min_trend_lvl"])).to_numpy()
    short_ok = cross_sell & common & (z_price > float(p["min_z"])).to_numpy() & (score_trend < 100.0 - float(p["min_trend_lvl"])).to_numpy()

    size = len(frame)
    entry = np.zeros(size, dtype=bool)
    exit_ = np.zeros(size, dtype=bool)
    pos, pending = 0, 0  # pending: 1 long ac, -1 short ac, 2 kapat; emir sonraki barin acilisinda dolar
    for i in range(size):
        if pending:
            pos = 0 if pending == 2 else pending
            pending = 0
        if pos == 0 and long_ok[i]:
            entry[i], pending = True, 1
        elif pos == 0 and short_ok[i]:
            pending = -1  # short bacak yok sayilir ama pozisyon kapisini (isFlat) kapatir
        elif pos == 1 and exit_long[i]:
            exit_[i], pending = True, 2
        elif pos == -1 and exit_short[i]:
            pending = 2
    return pd.DataFrame({"entry": entry, "exit": exit_, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
