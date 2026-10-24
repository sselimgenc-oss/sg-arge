"""TV-Z9O5w3SG Execution-Aware Trend [BSL]: EMA trend + Donchian(20) kirilim girisi; kapanis tabanli ATR izleyen risk cizgisi ve Donchian(10) cikisi.

Pozisyon durumuna bagli cikis (en yuksek kapanis, dolum fiyati) motorda `exit_builder` ile verilir: cikis sinyali dolum barindan
itibaren Pine ile ayni sirayla izlenir; dolum fiyati motorun gercek dolum fiyatidir (strategy.position_avg_price)."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from strategies.ozel import tv_ortak as T


class _Tracker:
    """Bir cerceve icin Pine durum makinesi: giris niyeti, risk cizgisi ve cikis niyeti dizileri."""

    def __init__(self, frame: pd.DataFrame, p: Mapping[str, Any]) -> None:
        close = frame["close"]
        self.close = close.to_numpy(dtype=float)
        self.open = frame["open"].to_numpy(dtype=float)
        self.size = len(frame)
        self.mult = float(p["atr_multiple"])
        fast, slow = T.ema(close, int(p["fast_length"])), T.ema(close, int(p["slow_length"]))
        self.atr = T.atr(frame, int(p["atr_length"])).to_numpy(dtype=float)
        n_in, n_out = int(p["entry_length"]), int(p["exit_length"])
        entry_high = T.highest(frame["high"], n_in).shift(1)
        entry_low = T.lowest(frame["low"], n_in).shift(1)
        exit_high = T.highest(frame["high"], n_out).shift(1)
        exit_low = T.lowest(frame["low"], n_out).shift(1)
        lookback = int(p["slope_lookback"])
        slow_back = slow.shift(lookback)
        ready = fast.notna() & slow_back.notna() & pd.Series(self.atr, index=frame.index).notna() & entry_high.notna() & entry_low.notna() & exit_high.notna() & exit_low.notna()
        start, end = pd.Timestamp(str(p["sample_start"]), tz="UTC"), pd.Timestamp(str(p["sample_end"]), tz="UTC")
        self.active = ((frame.index >= start) & (frame.index <= end))
        trend_up = ready & (fast > slow) & (slow > slow_back)
        trend_dn = ready & (fast < slow) & (slow < slow_back)
        eligible = pd.Series(self.active, index=frame.index) & ready
        self.long_intent = (eligible & trend_up & (close > entry_high)).to_numpy(dtype=bool)
        self.short_intent = (eligible & trend_dn & (close < entry_low)).to_numpy(dtype=bool)
        self.exit_low = exit_low.to_numpy(dtype=float)
        self.exit_high = exit_high.to_numpy(dtype=float)

    def exit_bar(self, fill_loc: int, fill_price: float, side: int) -> int | None:
        """Dolum barindan itibaren ilk cikis niyeti barinin konumu (yoksa None)."""
        peak = np.nan
        risk = np.nan
        for i in range(fill_loc, self.size):
            if not self.active[i]:
                return i  # boundaryExit
            c, a = self.close[i], self.atr[i]
            if i == fill_loc:
                peak = c
                risk = fill_price - side * self.mult * a
            elif side == 1:
                peak = max(peak, c)
                risk = max(risk, peak - self.mult * a)
            else:
                peak = min(peak, c)
                risk = min(risk, peak + self.mult * a)
            if side == 1:
                if c <= risk or c < self.exit_low[i]:
                    return i
            elif c >= risk or c > self.exit_high[i]:
                return i
        return None

    def long_entries(self) -> np.ndarray:
        """Long giris sinyal barlari; short bacak ve long beklemeleri pozisyon kapisi (flat) icin benzetilir."""
        entry = np.zeros(self.size, dtype=bool)
        i = 0
        while i < self.size - 1:
            if self.long_intent[i]:
                side = 1
            elif self.short_intent[i]:
                side = -1
            else:
                i += 1
                continue
            if side == 1:
                entry[i] = True
            fill = i + 1
            out = self.exit_bar(fill, self.open[fill], side)
            if out is None:
                break
            i = out + 1  # kapanis emri sonraki acilista dolar; o barin kapanisinda yeniden flat
        return entry


def signals(frame: pd.DataFrame, p: Mapping[str, Any]) -> pd.DataFrame:
    return pd.DataFrame({"entry": _Tracker(frame, p).long_entries(), "exit": False, "atr": T.atr(frame, 14)}, index=frame.index)


def build_plan(card, data, **_):
    params = dict(card.get("parametreler") or {})
    trackers = {symbol: _Tracker(frame, params) for symbol, frame in data.items()}
    frames = {symbol: frame for symbol, frame in data.items()}

    def builder(symbol, date, price, _stop, _target):
        tracker, frame = trackers[symbol], frames[symbol]
        fill_loc = frame.index.get_loc(date)
        out = tracker.exit_bar(int(fill_loc), float(price), 1)
        flags = np.zeros(len(frame), dtype=bool)
        if out is not None:
            flags[out] = True
        return pd.Series(flags, index=frame.index)

    by_id = {id(frame): symbol for symbol, frame in data.items()}
    return T.plan(
        card, data,
        lambda frame, p: pd.DataFrame(
            {"entry": trackers[by_id[id(frame)]].long_entries(), "exit": False, "atr": T.atr(frame, 14)}, index=frame.index),
        exit_builder=builder,
    )
