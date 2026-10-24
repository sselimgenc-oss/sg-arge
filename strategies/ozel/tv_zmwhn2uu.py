"""TV-zMwHN2Uu BTC 4H Breakout-Retest: pivot tabanli otomatik destek/direnc seviyeleri, retest ve kirilim girisi, %1,5 stop / %3 hedef, 6 bar bekleme."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from strategies.ozel import tv_ortak as T


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    close, high, low, open_ = frame["close"], frame["high"], frame["low"], frame["open"]
    pv = int(p["pvt_len"])
    auto_res = T.pivothigh(high, pv, pv).ffill()
    auto_sup = T.pivotlow(low, pv, pv).ffill()
    prev_close = close.shift(1)
    cross_up = (close > auto_res) & (prev_close <= auto_res)  # crossUp(autoRes); autoRes NaN ise False
    auto_flip = auto_res.where(cross_up).ffill()  # var autoFlip := autoRes yalniz kesisimde
    zone_top = auto_flip
    floor_u = auto_flip * (1.0 - float(p["auto_floor_perc"]))
    zone_ok = zone_top.notna() & floor_u.notna()

    sweep_low = T.lowest(low, int(p["sweep_lookback"]))
    prior_high_close = T.highest(close, int(p["prior_window"])).shift(int(p["sweep_lookback"]))
    retest_event = zone_ok & (close > zone_top) & (close > open_) & ((low <= zone_top) | (prev_close <= zone_top))
    came_from_above = zone_ok & prior_high_close.notna() & (prior_high_close > zone_top)
    not_collapsed = zone_ok & (sweep_low >= floor_u)
    breakout_event = cross_up  # res1 (elle seviye) yok; yalniz otomatik direnc kesisimi
    breakdown_event = (close < auto_sup) & (prev_close >= auto_sup)

    rsi = T.rsi(close, int(p["rsi_len"]))
    hist = g.macd(frame, "close", int(p["macd_fast"]), int(p["macd_slow"]), int(p["macd_sig"]))["hist"]
    sma_fast = T.sma(close, int(p["sma_fast_len"]))
    macd_up = (hist > 0) | (hist > hist.shift(1))
    retest_mom = (rsi > float(p["rsi_pull_min"])) & (rsi < float(p["rsi_pull_max"])) & macd_up
    sma_ok_up = sma_fast.isna() | (close > sma_fast)
    sma_ok_dn = sma_fast.isna() | (close < sma_fast)
    break_mom = (rsi > float(p["rsi_break_min"])) & (rsi < float(p["rsi_break_max"])) & (hist > 0) & sma_ok_up
    short_mom = (rsi > float(p["rsi_short_min"])) & (rsi < float(p["rsi_short_max"])) & (hist < 0) & sma_ok_dn
    ext = float(p["max_ext_perc"])
    not_ext_up = sma_fast.isna() | (close < sma_fast * (1.0 + ext))
    not_ext_dn = sma_fast.isna() | (close > sma_fast * (1.0 - ext))
    chase = float(p["max_chase_perc"])
    chase_retest = zone_top.notna() & (close <= zone_top * (1.0 + chase))
    chase_break = auto_res.notna() & (close <= auto_res * (1.0 + chase))
    chase_short = auto_sup.notna() & (close >= auto_sup * (1.0 - chase))

    retest_long = retest_event & came_from_above & not_collapsed & retest_mom & not_ext_up & chase_retest
    break_long = breakout_event & break_mom & not_ext_up & chase_break
    short_cond = breakdown_event & short_mom & not_ext_dn & chase_short
    levels_until = pd.Timestamp(str(p["levels_from"]), tz="UTC")  # bu tarihten sonra Pine elle (BTC'ye ozgu mutlak) seviyeler kullanir
    auto_now = pd.Series(frame.index < levels_until, index=frame.index)
    long_ok = ((retest_long | break_long) & auto_now).fillna(False).to_numpy(dtype=bool)
    short_ok = (short_cond & auto_now & ~(retest_long | break_long)).fillna(False).to_numpy(dtype=bool)

    c = close.to_numpy(dtype=float)
    sl, tp = float(p["sl_perc"]), float(p["tp_perc"])
    entry, _ = T.simulate_two_sided(
        frame, long_ok, short_ok, c * (1 - sl), c * (1 + tp), c * (1 + sl), c * (1 - tp),
        cooldown=int(p["cooldown_bars"]), exits_from_fill_bar=True, flat_only=True, cooldown_from_exit=True,
    )
    return pd.DataFrame({
        "entry": entry, "exit": False, "atr": T.atr(frame, 14),
        "_stop_level": close * (1 - sl), "_target_level": close * (1 + tp),
    }, index=frame.index)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
