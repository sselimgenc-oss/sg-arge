"""TV-dwgn7hrE Coil Breaker: RSI araligi sikismasi (percentrank) sonrasi RSI kirilimi."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close = frame["close"]
    rsi = T.rsi(close, int(p["rsi_len"]))
    rsi_high = T.highest(rsi, int(p["coil_len"]))
    rsi_low = T.lowest(rsi, int(p["coil_len"]))
    rank = T.percentrank(rsi_high - rsi_low, int(p["pct_len"]))
    squeeze = rank <= float(p["coil_pct"])
    since = T.barssince(squeeze)
    recent = since.notna() & (since <= int(p["coil_memory"]))
    ema = T.ema(close, int(p["ema_len"]))
    slope_up = ema > ema.shift(int(p["slope_len"]))
    adx = T.dmi(frame, int(p["adx_len"]))["adx"]
    adx_ok = (adx >= float(p["adx_min"])) if p["use_adx"] else pd.Series(True, index=frame.index)
    trigger = T.crossover(rsi, rsi_high.shift(1)) & recent & slope_up & adx_ok
    atr14 = T.atr(frame, int(p["atr_len"]))
    stop_dist = atr14 * float(p["atr_mult"])
    stop_price = close - stop_dist
    return pd.DataFrame({
        "entry": trigger, "exit": False, "atr": T.atr(frame, 14),
        "_stop_level": stop_price,
        # Pine: targetPrice = close + stopPrice * rMultiple (yazar kodu, stopPrice bir FIYAT oldugundan hedef ~3x fiyat)
        "_target_level": close + stop_price * float(p["r_multiple"]),
    }, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
