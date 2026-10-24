"""TV-buSJAz8o Fibonacci Golden Pocket + RSI Momentum Cross: pivot mandali, bolge temasi sayaci, son giristen bekleme."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    left, right = int(p["pivot_left"]), int(p["pivot_right"])
    ph = T.pivothigh(frame["high"], left, right).to_numpy()
    pl = T.pivotlow(frame["low"], left, right).to_numpy()
    size = len(frame)
    sh = np.full(size, np.nan); sl_ = np.full(size, np.nan)
    shb = np.full(size, np.nan); slb = np.full(size, np.nan)
    cur_h = cur_l = cur_hb = cur_lb = np.nan
    for i in range(size):
        if not np.isnan(ph[i]):
            cur_h, cur_hb = ph[i], i - right
        if not np.isnan(pl[i]):
            cur_l, cur_lb = pl[i], i - right
        sh[i], sl_[i], shb[i], slb[i] = cur_h, cur_l, cur_hb, cur_lb
    have = ~np.isnan(sh) & ~np.isnan(sl_)
    leg_up = have & (shb > slb)
    leg_dn = have & (slb > shb)
    diff = np.abs(sh - sl_)
    gl, gh = float(p["golden_low"]), float(p["golden_high"])
    zone_hi = np.where(leg_up, sh - diff * gl, np.where(leg_dn, sl_ + diff * gh, np.nan))
    zone_lo = np.where(leg_up, sh - diff * gh, np.where(leg_dn, sl_ + diff * gl, np.nan))
    stop_long = np.where(leg_up, sh - diff * float(p["stop_ratio"]), np.nan)
    stop_short = np.where(leg_dn, sl_ + diff * float(p["stop_ratio"]), np.nan)
    tgt_long = np.where(leg_up, sl_ + diff * float(p["ext_ratio"]), np.nan)
    tgt_short = np.where(leg_dn, sh - diff * float(p["ext_ratio"]), np.nan)
    low, high, close = (frame[k].to_numpy(dtype=float) for k in ("low", "high", "close"))
    touched = have & ~np.isnan(zone_hi) & (low <= zone_hi) & (high >= zone_lo)
    since = np.empty(size)
    count = 9999  # var int barsSinceTouch = 9999
    for i in range(size):
        count = 0 if touched[i] else count + 1
        since[i] = count
    valid = since <= int(p["zone_valid_bars"])
    ema = T.ema(frame["close"], int(p["ema_len"])).to_numpy()
    rsi = T.rsi(frame["close"], int(p["rsi_length"]))
    up_x = T.crossover(rsi, 50.0).to_numpy()
    dn_x = T.crossunder(rsi, 50.0).to_numpy()
    with np.errstate(invalid="ignore"):
        long_ok = leg_up & (close > ema) & valid & up_x & (close - stop_long > 0)
        short_ok = leg_dn & (close < ema) & valid & dn_x & (stop_short - close > 0)
    # qty > 0 kosulu yazarin boyut kodudur (equity, mintick, pointvalue); kuralin parcasi sayilmadi
    entry, flip = T.simulate_two_sided(frame, long_ok, short_ok, stop_long, tgt_long, stop_short, tgt_short, cooldown=int(p["cooldown_bars"]))
    return pd.DataFrame({"entry": entry, "exit": flip, "atr": T.atr(frame, 14),
                         "_stop_level": pd.Series(stop_long, index=frame.index), "_target_level": pd.Series(tgt_long, index=frame.index)}, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
