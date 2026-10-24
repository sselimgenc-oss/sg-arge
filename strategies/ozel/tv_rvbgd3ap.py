"""TV-rvBgD3aP Elliott Wave Impulse Strategy: ZigZag pivot dizisi (5 dalga) -> itki sonu donus ve dalga-5 girisleri."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


def _impulse(p: list[float], d: int) -> bool:
    p0, p1, p2, p3, p4, p5 = p
    if d == 1:
        w1, w3, w5 = p1 - p0, p3 - p2, p5 - p4
        return w3 != min(w1, w3, w5) and p5 > p3 and p2 > p0 and p4 > p1
    w1, w3, w5 = p0 - p1, p2 - p3, p4 - p5
    return w3 != min(w1, w3, w5) and p3 > p5 and p0 > p2 and p1 > p4


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    high, low, close = (frame[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    size = len(frame)
    atr = T.atr(frame, int(p["atr_len"])).to_numpy()
    ph = T.pivothigh(frame["high"], int(p["zz_len"]), 1).to_numpy()
    pl = T.pivotlow(frame["low"], int(p["zz_len"]), 1).to_numpy()
    mode = p["entry_mode"]
    zy: list[float] = []  # en yeni basta (array.unshift)
    zdir = 0
    entry = np.zeros(size, dtype=bool)
    stop_lvl = np.full(size, np.nan)
    tgt_lvl = np.full(size, np.nan)
    for i in range(size):
        flipped = False
        if not np.isnan(ph[i]):
            y2 = 0.0 if i == 0 else float(np.nan_to_num(high[i - 1], nan=0.0))
            if zdir < 1:
                zy.insert(0, y2); zdir = 1; flipped = True
            elif ph[i] > zy[0]:
                zy[0] = y2
        if not np.isnan(pl[i]):
            y2 = 0.0 if i == 0 else float(np.nan_to_num(low[i - 1], nan=0.0))
            if zdir > -1:
                zy.insert(0, y2); zdir = -1; flipped = True
            elif pl[i] < zy[0]:
                zy[0] = y2
        if len(zy) > 8:
            zy.pop()
        sig_dir, sig_stop, sig_tgt, sig_imp = 0, np.nan, np.nan, np.nan
        a = atr[i]
        if flipped and len(zy) >= 7 and mode != "Wave 5":
            d = 1 if zdir == -1 else -1
            pts = [zy[6], zy[5], zy[4], zy[3], zy[2], zy[1]]
            if _impulse(pts, d):
                diff = abs(pts[5] - pts[0])
                sgn = -1.0 if d == 1 else 1.0
                sig_dir = -1 if d == 1 else 1
                sig_stop = pts[5] + p["stop_buf"] * a if d == 1 else pts[5] - p["stop_buf"] * a
                sig_tgt = pts[5] + sgn * diff * p["tgt_fib"]
                sig_imp = diff
        if flipped and sig_dir == 0 and len(zy) >= 5 and mode != "Reversal":
            d = 1 if zdir == -1 else -1
            p4, p3, p2, p1, p0 = zy[0], zy[1], zy[2], zy[3], zy[4]
            ok = False
            w1 = w3 = 0.0
            if d == 1:
                w1, w3 = p1 - p0, p3 - p2
                ret = (p3 - p4) / w3 if w3 > 0 else np.nan
                ok = w3 > w1 and w1 > 0 and p2 > p0 and p4 > p1 and not np.isnan(ret) and p["min_ret4"] <= ret <= p["max_ret4"]
            else:
                w1, w3 = p0 - p1, p2 - p3
                ret = (p4 - p3) / w3 if w3 > 0 else np.nan
                ok = w3 > w1 and w1 > 0 and p0 > p2 and p1 > p4 and not np.isnan(ret) and p["min_ret4"] <= ret <= p["max_ret4"]
            if ok:
                sig_dir = d
                sig_stop = p4 - p["stop_buf"] * a if d == 1 else p4 + p["stop_buf"] * a
                sig_tgt = p4 + w1 * p["w5_ext"] if d == 1 else p4 - w1 * p["w5_ext"]
                sig_imp = w3
        if sig_dir == 1 and i > 50 and not np.isnan(a):
            risk, reward = close[i] - sig_stop, sig_tgt - close[i]
            rr = reward / risk if risk > 0 and reward > 0 else 0.0
            if sig_imp >= p["min_imp"] * a and rr >= p["min_rr"]:
                entry[i] = True
                stop_lvl[i], tgt_lvl[i] = sig_stop, sig_tgt
    idx = frame.index
    return pd.DataFrame({"entry": entry, "exit": False, "atr": T.atr(frame, 14),
                         "_stop_level": stop_lvl, "_target_level": tgt_lvl}, index=idx)


def build_plan(card, data, **_):
    return T.plan(card, data, signals, own_stop=True, level_fns_factory=T.stop_target_levels)
