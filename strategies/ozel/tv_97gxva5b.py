"""TV-97gxVA5b Compression Breakout System: Bollinger genislik percentrank sikismasi + 20 gun kirilimi + hacim/trend filtresi; Chandelier izleyen cikis.

Cikis pozisyon durumuna baglidir (sinyal kapanisindan sabit ilk stop, en yuksek kapanis): motorda `exit_builder` ile verilir.
process_orders_on_close = true: giris ve cikis sinyal barinin kapanisinda dolar (kartta dolum: kapanis)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


class _Tracker:
    def __init__(self, frame: pd.DataFrame, p: Mapping[str, Any]) -> None:
        close = frame["close"]
        self.close = close.to_numpy(dtype=float)
        self.size = len(frame)
        basis = T.sma(close, int(p["bb_len"]))
        dev = T.stdev(close, int(p["bb_len"])) * float(p["bb_mult"])
        width = 2.0 * dev / basis * 100.0
        squeeze = T.percentrank(width, int(p["rank_len"])) < float(p["sqz_pct"])
        recent = squeeze.astype(float).rolling(int(p["sqz_age"])).sum() > 0
        brk = T.highest(frame["high"], int(p["brk_len"])).shift(1)
        vol_ok = frame["volume"] > T.sma(frame["volume"], 20)
        trend_ok = close > T.sma(close, int(p["sma_len"]))
        start, end = pd.Timestamp(str(p["start"]), tz="UTC"), pd.Timestamp(str(p["end"]), tz="UTC")
        in_window = pd.Series((frame.index >= start) & (frame.index <= end), index=frame.index)
        self.cond = (in_window & recent & (close > brk) & vol_ok & trend_ok).fillna(False).to_numpy(dtype=bool)
        self.atr = T.atr(frame, int(p["atr_len"])).to_numpy(dtype=float)
        self.stop_atr, self.trail_atr = float(p["stop_atr"]), float(p["trail_atr"])
        self.after_end = (frame.index > end)

    def exit_bar(self, entry_loc: int) -> int | None:
        """Giris barindan sonraki ilk cikis (kapanis < max(ilk stop, zirve - 3 x ATR)) ya da pencere sonu."""
        entry_stop = self.close[entry_loc] - self.stop_atr * self.atr[entry_loc]
        hwm = self.close[entry_loc]
        for i in range(entry_loc + 1, self.size):  # giris barinda inPos henuz yok (emir kapanista dolar)
            hwm = max(hwm, self.close[i])
            if self.after_end[i]:
                return i
            level = max(entry_stop, hwm - self.trail_atr * self.atr[i])
            if self.close[i] < level:
                return i
        return None

    def entries(self) -> np.ndarray:
        entry = np.zeros(self.size, dtype=bool)
        i = 0
        while i < self.size:
            if not self.cond[i]:
                i += 1
                continue
            entry[i] = True
            out = self.exit_bar(i)
            if out is None:
                break
            i = out + 1  # cikis emri o barin kapanisinda dolar; sonraki barda yeniden flat
        return entry


def build_plan(card, data, **_):
    params = dict(card.get("parametreler") or {})
    trackers = {symbol: _Tracker(frame, params) for symbol, frame in data.items()}
    by_id = {id(frame): symbol for symbol, frame in data.items()}
    frames = dict(data)

    def builder(symbol, date, _price, _stop, _target):
        frame = frames[symbol]
        out = trackers[symbol].exit_bar(int(frame.index.get_loc(date)))
        flags = np.zeros(len(frame), dtype=bool)
        if out is not None:
            flags[out] = True
        return pd.Series(flags, index=frame.index)

    return T.plan(
        card, data,
        lambda frame, p: pd.DataFrame(
            {"entry": trackers[by_id[id(frame)]].entries(), "exit": False, "atr": T.atr(frame, 14)}, index=frame.index),
        exit_builder=builder,
    )
