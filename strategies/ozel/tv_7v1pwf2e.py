"""TV-7v1PWf2e Adaptive Regime Momentum: ALMA + ZLMA kompozit ortalamasi egimi, hacim RSI ve RSI filtresi; cikis kompozit MA - 1,5 ATR altinda kapanis
ya da egim dususu; her barda yeniden verilen stop (giris - 2,5 ATR) ve hedef (giris + 4 ATR) `dyn_stop_rel` / `dyn_target_rel` sutunlaridir."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from strategies.ozel import tv_ortak as T
from strategies.ozel.tv_fennqpan import alma


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    length = int(p["ma_len"])
    ema1 = T.ema(close, length)
    zlma = T.ema(2.0 * ema1 - T.ema(ema1, length), length)
    combo = (alma(close, length, float(p["alma_offset"]), float(p["alma_sigma"])) + zlma) / 2.0
    rise = combo.diff()
    confirm = int(p["slope_confirm"])
    up = (rise > 0).astype(float).rolling(confirm).sum() >= confirm
    atr = T.atr(frame, int(p["atr_len"]))
    vol_ok = T.rsi(frame["volume"], int(p["vol_rsi_len"])) / 50.0 > float(p["vol_thresh"])
    rsi_ok = T.rsi(close, int(p["rsi_len"])) > float(p["rsi_bull_min"])
    entry = up & (close > combo) & vol_ok & rsi_ok
    exit_ = (close < combo - atr * float(p["trail_mult"])) | (rise < 0)
    return pd.DataFrame({"entry": entry.fillna(False), "exit": exit_.fillna(False), "atr": T.atr(frame, 14),
                         "dyn_stop_rel": float(p["stop_mult"]) * atr, "dyn_target_rel": float(p["tp_mult"]) * atr}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals)
