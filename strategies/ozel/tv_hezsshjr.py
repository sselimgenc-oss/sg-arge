"""TV-hezSShJr Hybrid Breakout (NASDAQ:GOOGL): MA50/150/200 yukari trend + daralma (aralik yuzdeligi ya da kapanis araligi) + hacim filtresi;
giris `highest(high, 3)[1]` seviyesinde alis STOP emri; stop %8, 3 kademe: %25 @ +%10, %50 @ +%20, kalan @ +%30 (bar ici limit)."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from engine.kart_sinyal import KartPlan
from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, high, low = frame["close"], frame["high"], frame["low"]
    src = close
    ma50, ma150, ma200 = (T.sma(src, int(p[k])) for k in ("len50", "len150", "len200"))
    trend = (close > ma50) & (ma50 > ma150) & (ma150 > ma200) & (ma200 > ma200.shift(1)) & (ma200 > ma200.shift(int(p["ma_up_lookback"]))) & (ma50 >= ma50.shift(1))
    n = int(p["range_len"])
    h_range, l_range = T.highest(high, n), T.lowest(low, n)
    range_pct = (h_range - l_range) / h_range * 100.0
    h_close, l_close = T.highest(close, n), T.lowest(close, n)
    close_range_pct = (h_close - l_close) / h_close * 100.0
    squeeze = (T.percentrank(range_pct, int(p["percentile_lookback"])) <= float(p["percentile_max"])) | (close_range_pct <= float(p["close_range_max"]))
    volume_ok = frame["volume"] > T.sma(frame["volume"], int(p["vol_ma_len"])) * float(p["vol_mult"])
    signal = (trend & squeeze & volume_ok).fillna(False)
    level = T.highest(high, int(p["breakout_lookback"])).shift(1)
    return pd.DataFrame({"entry": signal, "exit": False, "atr": T.atr(frame, 14), "entry_level": level,
                         "stop_pct": float(p["stop_pct"]) / 100.0, "target_pct": float(p["take3_pct"]) / 100.0}, index=frame.index)


def build_plan(card: Mapping[str, Any], data: Mapping[str, pd.DataFrame], **_) -> KartPlan:
    p = dict(card.get("parametreler") or {})
    levels = [{"oran": 0.25, "trigger_fn": lambda price, _d, k=float(p["take1_pct"]) / 100.0: price * (1.0 + k), "intrabar": True},
              {"oran": 0.50, "trigger_fn": lambda price, _d, k=float(p["take2_pct"]) / 100.0: price * (1.0 + k), "intrabar": True}]
    return T.plan(card, data, signals, own_stop=True, entry_order_type="stop", entry_order_validity=1, scaled_exits=levels)
