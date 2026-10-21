"""Card indicator library (``engine.gosterge``), following Pine/TradingView definitions.

Not to be confused with ``engine.indicators``: that module holds the Series-based
functions of the T1a reference engine (pandas ``ewm`` seeded with the first value)
and is left untouched so the accepted T1a results stay reproducible. Seeding
differs only during warm-up; ``tests/test_gosterge.py`` checks that both agree
after it.


Every indicator takes an OHLCV DataFrame (columns open, high, low, close,
volume) and returns a Series or a DataFrame with named columns. Conventions:

* RMA (Wilder) and EMA are seeded with the SMA of the first ``n`` valid values,
  like Pine's ``ta.rma`` / ``ta.ema``. RSI, ATR, DMI/ADX are RMA based.
* ``stdev`` is the population standard deviation (Pine ``ta.stdev`` default).
* Trend indicators (``supertrend``, ``pmax``, ``ott``) expose ``dir`` where
  **+1 is bullish and -1 is bearish** (Pine's ``ta.supertrend`` uses the
  opposite sign; cards use +1 = bullish).
* ``ha: true`` in a card spec computes the indicator on Heikin Ashi candles.
* ``{f: seri, ifade: "<expression>"}`` defines a derived series from earlier names.
* ``tf`` in a card spec evaluates the indicator on a higher timeframe and maps
  it back using only the previous *completed* higher-timeframe bar.
* ``kaydir: k`` lags the result by k bars.

Indicators outside the card list (SAR, Fisher RSI, TEMA, ZLSMA, ...) are not
implemented on purpose; ``engine.spec --kontrol`` reports cards needing them.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from . import expr as _expr

OHLCV = ("open", "high", "low", "close", "volume")
_AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


class UnknownIndicator(KeyError):
    """Raised when a card references an indicator that is not implemented."""


# ----------------------------------------------------------------- helpers
def _col(df: pd.DataFrame, name: str) -> pd.Series:
    return df[name].astype(float)


def hl2(df: pd.DataFrame) -> pd.Series:
    return (_col(df, "high") + _col(df, "low")) / 2


def hlc3(df: pd.DataFrame) -> pd.Series:
    return (_col(df, "high") + _col(df, "low") + _col(df, "close")) / 3


def ohlc4(df: pd.DataFrame) -> pd.Series:
    return (_col(df, "open") + _col(df, "high") + _col(df, "low") + _col(df, "close")) / 4


_NAMED_SOURCES = {"hl2": hl2, "hlc3": hlc3, "typical": hlc3, "ohlc4": ohlc4}


def source(df: pd.DataFrame, src: str | pd.Series = "close", extra: Mapping[str, Any] | None = None) -> pd.Series:
    """Resolve ``src``: a column, a named price (hl2/typical/...) or an expression."""
    if isinstance(src, pd.Series):
        return src.astype(float)
    if src in OHLCV:
        return _col(df, src)
    if src in _NAMED_SOURCES:
        return _NAMED_SOURCES[src](df)
    env: dict[str, Any] = {c: _col(df, c) for c in OHLCV if c in df}
    env.update(extra or {})
    return pd.Series(_expr.parse(str(src)).evaluate(env, index=df.index), index=df.index).astype(float)


def true_range(df: pd.DataFrame) -> pd.Series:
    high, low, close = _col(df, "high"), _col(df, "low"), _col(df, "close")
    prev = close.shift(1)
    tr = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0:1] = (high - low).iloc[0:1]
    return tr


def _seeded_smooth(values: pd.Series, n: int, alpha: float) -> pd.Series:
    """Recursive smoothing seeded with the SMA of the first n valid values."""
    arr = values.to_numpy(dtype=float)
    out = np.full(len(arr), np.nan)
    valid = np.flatnonzero(~np.isnan(arr))
    if len(valid) < n:
        return pd.Series(out, index=values.index)
    start = valid[0]
    # first window of n consecutive valid values
    while start + n <= len(arr) and np.isnan(arr[start:start + n]).any():
        nxt = np.flatnonzero(~np.isnan(arr[start + 1:]))
        if not len(nxt):
            return pd.Series(out, index=values.index)
        start = start + 1 + nxt[0]
    if start + n > len(arr):
        return pd.Series(out, index=values.index)
    state = arr[start:start + n].mean()
    out[start + n - 1] = state
    for i in range(start + n, len(arr)):
        if not np.isnan(arr[i]):
            state = alpha * arr[i] + (1 - alpha) * state
        out[i] = state
    return pd.Series(out, index=values.index)


def rma(values: pd.Series, n: int) -> pd.Series:
    return _seeded_smooth(values, int(n), 1.0 / int(n))


# -------------------------------------------------------------- indicators
def sma(df: pd.DataFrame, src: str = "close", n: int = 14) -> pd.Series:
    return source(df, src).rolling(int(n)).mean()


def ema(df: pd.DataFrame, src: str = "close", n: int = 14) -> pd.Series:
    return _seeded_smooth(source(df, src), int(n), 2.0 / (int(n) + 1))


def wma(df: pd.DataFrame, src: str = "close", n: int = 14) -> pd.Series:
    n = int(n)
    weights = np.arange(1, n + 1, dtype=float)
    return source(df, src).rolling(n).apply(lambda w: float(np.dot(w, weights) / weights.sum()), raw=True)


def stdev(df: pd.DataFrame, src: str = "close", n: int = 14, ddof: int = 0) -> pd.Series:
    return source(df, src).rolling(int(n)).std(ddof=int(ddof))


def highest(df: pd.DataFrame, src: str = "high", n: int = 14) -> pd.Series:
    return source(df, src).rolling(int(n)).max()


def lowest(df: pd.DataFrame, src: str = "low", n: int = 14) -> pd.Series:
    return source(df, src).rolling(int(n)).min()


def zscore(df: pd.DataFrame, src: str = "close", n: int = 20, ma: str = "sma") -> pd.Series:
    s = source(df, src)
    base = s.rolling(int(n)).mean() if ma == "sma" else _seeded_smooth(s, int(n), 2.0 / (int(n) + 1))
    return (s - base) / s.rolling(int(n)).std(ddof=0)


def roc(df: pd.DataFrame, src: str = "close", n: int = 10) -> pd.Series:
    s = source(df, src)
    return (s / s.shift(int(n)) - 1.0) * 100.0


def rsi(df: pd.DataFrame, src: str = "close", n: int = 14, ma: str = "rma") -> pd.Series:
    s = source(df, src)
    change = s.diff()
    smooth = rma if ma == "rma" else (lambda v, k: v.rolling(int(k)).mean())
    up = smooth(change.clip(lower=0), n)
    down = smooth((-change).clip(lower=0), n)
    out = 100.0 - 100.0 / (1.0 + up / down)
    out[(down == 0) & up.notna()] = 100.0
    out[(up == 0) & down.notna()] = 0.0
    return out


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    return rma(true_range(df), n)


def atr_ratio(df: pd.DataFrame, n: int = 14, sma_n: int = 40) -> pd.Series:
    a = atr(df, n)
    return a / a.rolling(int(sma_n)).mean()


def dmi(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """+DI, -DI and ADX as in Pine ``ta.dmi`` (ADX smoothing = n)."""
    high, low = _col(df, "high"), _col(df, "low")
    up, down = high.diff(), -low.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index).where(up.notna() & down.notna())
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index).where(up.notna() & down.notna())
    tr = rma(true_range(df), n)
    plus = (100.0 * rma(plus_dm, n) / tr).ffill()
    minus = (100.0 * rma(minus_dm, n) / tr).ffill()
    total = plus + minus
    adx_value = 100.0 * rma((plus - minus).abs() / total.where(total != 0, 1.0), n)
    return pd.DataFrame({"plus": plus, "minus": minus, "adx": adx_value})


def adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    return dmi(df, n)["adx"]


def cci(df: pd.DataFrame, n: int = 20) -> pd.Series:
    tp = hlc3(df)
    mean = tp.rolling(int(n)).mean()
    dev = tp.rolling(int(n)).apply(lambda w: float(np.abs(w - w.mean()).mean()), raw=True)
    return (tp - mean) / (0.015 * dev)


def macd(df: pd.DataFrame, src: str = "close", fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    s = source(df, src)
    line = _seeded_smooth(s, int(fast), 2.0 / (int(fast) + 1)) - _seeded_smooth(s, int(slow), 2.0 / (int(slow) + 1))
    sig = _seeded_smooth(line, int(signal), 2.0 / (int(signal) + 1))
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def bb(df: pd.DataFrame, src: str = "close", n: int = 20, carpan: float = 2.0) -> pd.DataFrame:
    s = source(df, src)
    basis = s.rolling(int(n)).mean()
    dev = float(carpan) * s.rolling(int(n)).std(ddof=0)
    return pd.DataFrame({"upper": basis + dev, "basis": basis, "lower": basis - dev})


def kc(df: pd.DataFrame, n: int = 20, carpan: float = 2.0, src: str = "close") -> pd.DataFrame:
    """Keltner channel as Pine ``ta.kc``: EMA basis +- mult * EMA(true range)."""
    basis = ema(df, src, n)
    spread = float(carpan) * _seeded_smooth(true_range(df), int(n), 2.0 / (int(n) + 1))
    return pd.DataFrame({"upper": basis + spread, "basis": basis, "lower": basis - spread})


def donchian(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    upper, lower = _col(df, "high").rolling(int(n)).max(), _col(df, "low").rolling(int(n)).min()
    return pd.DataFrame({"upper": upper, "lower": lower, "mid": (upper + lower) / 2})


def stoch(df: pd.DataFrame, k: int = 14, d: int = 3, smooth: int = 3) -> pd.DataFrame:
    """%K (smoothed with SMA ``smooth``; smooth=1 is the fast stochastic) and %D."""
    low_n, high_n = _col(df, "low").rolling(int(k)).min(), _col(df, "high").rolling(int(k)).max()
    spread = (high_n - low_n).where(lambda v: v != 0)
    raw = 100.0 * (_col(df, "close") - low_n) / spread
    k_line = raw.rolling(int(smooth)).mean() if int(smooth) > 1 else raw
    return pd.DataFrame({"k": k_line, "d": k_line.rolling(int(d)).mean()})


def obv(df: pd.DataFrame) -> pd.Series:
    sign = np.sign(_col(df, "close").diff()).fillna(0.0)
    return (sign * _col(df, "volume")).cumsum()


def mfi(df: pd.DataFrame, n: int = 14) -> pd.Series:
    tp = hlc3(df)
    flow = tp * _col(df, "volume")
    change = tp.diff()
    upper = flow.where(change > 0, 0.0).rolling(int(n)).sum()
    lower = flow.where(change < 0, 0.0).rolling(int(n)).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower)
    out[(lower == 0) & upper.notna()] = 100.0
    out[(upper == 0) & lower.notna()] = 0.0
    return out


def vwap(df: pd.DataFrame, anchor: str = "D") -> pd.Series:
    """Session VWAP reset each UTC day; for daily bars it equals hlc3."""
    tp, vol = hlc3(df), _col(df, "volume")
    if anchor != "D" or not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("only anchor='D' on a DatetimeIndex is supported")
    day = df.index.tz_localize(None).normalize() if df.index.tz is not None else df.index.normalize()
    pv = (tp * vol).groupby(day).cumsum()
    v = vol.groupby(day).cumsum()
    return (pv / v.where(v != 0)).fillna(tp)


def kama(df: pd.DataFrame, src: str = "close", n: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    s = source(df, src)
    n = int(n)
    er = (s - s.shift(n)).abs() / s.diff().abs().rolling(n).sum()
    fast_sc, slow_sc = 2.0 / (int(fast) + 1), 2.0 / (int(slow) + 1)
    sc = ((er * (fast_sc - slow_sc) + slow_sc) ** 2).to_numpy()
    values = s.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    if len(values) > n:
        out[n] = values[n]
        for i in range(n + 1, len(values)):
            if np.isnan(sc[i]):
                out[i] = out[i - 1]
            else:
                out[i] = out[i - 1] + sc[i] * (values[i] - out[i - 1])
    return pd.Series(out, index=s.index)


def ichimoku(df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou_b: int = 52, displacement: int = 26) -> pd.DataFrame:
    """Lines and cloud; the cloud is shifted forward (no look-ahead, chikou omitted)."""
    high, low = _col(df, "high"), _col(df, "low")

    def mid(k: int) -> pd.Series:
        return (high.rolling(int(k)).max() + low.rolling(int(k)).min()) / 2

    t, k = mid(tenkan), mid(kijun)
    return pd.DataFrame(
        {
            "tenkan": t,
            "kijun": k,
            "span_a": ((t + k) / 2).shift(int(displacement)),
            "span_b": mid(senkou_b).shift(int(displacement)),
        }
    )


def supertrend(df: pd.DataFrame, n: int = 10, carpan: float = 3.0) -> pd.DataFrame:
    """Pine ``ta.supertrend`` logic; ``dir`` is +1 bullish, -1 bearish."""
    close = _col(df, "close").to_numpy()
    src = hl2(df).to_numpy()
    atr_v = atr(df, n).to_numpy()
    size = len(close)
    upper, lower = src + carpan * atr_v, src - carpan * atr_v
    line = np.full(size, np.nan)
    direction = np.full(size, np.nan)  # Pine sign: -1 up, 1 down
    for i in range(size):
        if np.isnan(atr_v[i]):
            continue
        if i > 0 and not np.isnan(atr_v[i - 1]):
            prev_lower, prev_upper = lower[i - 1], upper[i - 1]
            if not (lower[i] > prev_lower or close[i - 1] < prev_lower):
                lower[i] = prev_lower
            if not (upper[i] < prev_upper or close[i - 1] > prev_upper):
                upper[i] = prev_upper
            if line[i - 1] == prev_upper:
                direction[i] = -1 if close[i] > upper[i] else 1
            else:
                direction[i] = 1 if close[i] < lower[i] else -1
        else:
            direction[i] = 1
        line[i] = lower[i] if direction[i] == -1 else upper[i]
    return pd.DataFrame({"line": line, "dir": -direction}, index=df.index)


def var(df: pd.DataFrame, src: str = "close", n: int = 9, cmo_n: int = 9) -> pd.Series:
    """Variable index dynamic average (VIDYA, K. Ozbilgic 'VAR'); seeded with the source."""
    s = source(df, src).to_numpy(dtype=float)
    alpha = 2.0 / (int(n) + 1)
    diff = np.diff(s, prepend=np.nan)
    up_sum = pd.Series(np.where(diff > 0, diff, 0.0)).where(~np.isnan(diff)).rolling(int(cmo_n)).sum().to_numpy()
    dn_sum = pd.Series(np.where(diff < 0, -diff, 0.0)).where(~np.isnan(diff)).rolling(int(cmo_n)).sum().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        cmo_abs = np.abs(up_sum - dn_sum) / (up_sum + dn_sum)
    out = np.full(len(s), np.nan)
    state = np.nan
    for i in range(len(s)):
        if np.isnan(s[i]):
            continue
        if np.isnan(state):
            state = s[i]
        k = alpha * (0.0 if np.isnan(cmo_abs[i]) else cmo_abs[i])
        state = k * s[i] + (1.0 - k) * state
        out[i] = state
    return pd.Series(out, index=df.index)


def _moving_average(df: pd.DataFrame, src: str, ma: str, n: int) -> pd.Series:
    if ma == "ema":
        return ema(df, src, n)
    if ma == "sma":
        return sma(df, src, n)
    if ma == "var":
        return var(df, src, n)
    raise ValueError(f"unknown ma type: {ma}")


def _trailing(ma_values: np.ndarray, offset: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """OTT / PMax band recursion; returns (long_stop, short_stop, trend +-1)."""
    size = len(ma_values)
    long_stop = np.full(size, np.nan)
    short_stop = np.full(size, np.nan)
    trend = np.full(size, np.nan)
    state = 1.0
    for i in range(size):
        if np.isnan(ma_values[i]) or np.isnan(offset[i]):
            continue
        long_now, short_now = ma_values[i] - offset[i], ma_values[i] + offset[i]
        prev_long = long_stop[i - 1] if i > 0 and not np.isnan(long_stop[i - 1]) else long_now
        prev_short = short_stop[i - 1] if i > 0 and not np.isnan(short_stop[i - 1]) else short_now
        if ma_values[i] > prev_long:
            long_now = max(long_now, prev_long)
        if ma_values[i] < prev_short:
            short_now = min(short_now, prev_short)
        if state == -1 and ma_values[i] > prev_short:
            state = 1.0
        elif state == 1 and ma_values[i] < prev_long:
            state = -1.0
        long_stop[i], short_stop[i], trend[i] = long_now, short_now, state
    return long_stop, short_stop, trend


def ott(df: pd.DataFrame, src: str = "close", n: int = 14, yuzde: float = 1.4, ma: str = "var", twin_katsayi: float | None = None) -> pd.DataFrame:
    """Optimized Trend Tracker (K. Ozbilgic). ``dir`` = +1 when MA is above OTT[2]."""
    ma_values = _moving_average(df, src, ma, n)
    long_stop, short_stop, trend = _trailing(ma_values.to_numpy(), (ma_values * float(yuzde) * 0.01).to_numpy())
    mt = np.where(trend == 1, long_stop, short_stop)
    line = np.where(ma_values.to_numpy() > mt, mt * (200 + yuzde) / 200, mt * (200 - yuzde) / 200)
    line[np.isnan(trend)] = np.nan
    ott_line = pd.Series(line, index=df.index).shift(2)
    columns = {
        "ma": ma_values,
        "ott": ott_line,
        "dir": pd.Series(np.where(ma_values > ott_line, 1.0, -1.0), index=df.index).where(ott_line.notna()),
        "long_stop": pd.Series(long_stop, index=df.index),
        "short_stop": pd.Series(short_stop, index=df.index),
    }
    if twin_katsayi is not None:
        columns["up"] = ott_line * (1 + float(twin_katsayi))
        columns["dn"] = ott_line * (1 - float(twin_katsayi))
    return pd.DataFrame(columns)


def pmax(df: pd.DataFrame, src: str = "hl2", ma: str = "ema", n: int = 10, atr_n: int = 10, carpan: float = 3.0) -> pd.DataFrame:
    """Profit Maximizer (K. Ozbilgic). ``dir`` +1 = long state."""
    ma_values = _moving_average(df, src, ma, n)
    long_stop, short_stop, trend = _trailing(ma_values.to_numpy(), (float(carpan) * atr(df, atr_n)).to_numpy())
    line = np.where(trend == 1, long_stop, short_stop)
    return pd.DataFrame(
        {"pmax": line, "ma": ma_values.to_numpy(), "dir": trend, "long_stop": long_stop, "short_stop": short_stop},
        index=df.index,
    )


def heikinashi(df: pd.DataFrame) -> pd.DataFrame:
    """Heikin Ashi candles (open, high, low, close); ha_open is seeded with (open + close) / 2."""
    o, h, l, c = (_col(df, name) for name in ("open", "high", "low", "close"))
    ha_close = (o + h + l + c) / 4
    ha_open = np.full(len(df), np.nan)
    closes, opens = ha_close.to_numpy(), o.to_numpy()
    raw_close = c.to_numpy()
    for i in range(len(df)):
        if i == 0:
            ha_open[i] = (opens[i] + raw_close[i]) / 2
        else:
            ha_open[i] = (ha_open[i - 1] + closes[i - 1]) / 2
    ha_open_s = pd.Series(ha_open, index=df.index)
    return pd.DataFrame(
        {
            "open": ha_open_s,
            "high": pd.concat([h, ha_open_s, ha_close], axis=1).max(axis=1),
            "low": pd.concat([l, ha_open_s, ha_close], axis=1).min(axis=1),
            "close": ha_close,
        }
    )


def alphatrend(df: pd.DataFrame, n: int = 14, carpan: float = 1.0, momentum: str = "mfi") -> pd.Series:
    """AlphaTrend (K. Ozbilgic): trailing support/resistance chosen by MFI/RSI >= 50.

    ATR is SMA(true range, n) as in the original script (not Wilder). Pine seeds the
    recursion with nz()=0; here it is seeded with the first candidate value so the
    warm-up does not create a fake cross.
    """
    tr_sma = true_range(df).rolling(int(n)).mean()
    up_t = _col(df, "low") - tr_sma * float(carpan)
    down_t = _col(df, "high") + tr_sma * float(carpan)
    strength = mfi(df, int(n)) if momentum == "mfi" else rsi(df, "close", int(n))
    bullish = (strength >= 50).to_numpy()
    valid = (strength.notna() & tr_sma.notna()).to_numpy()
    up, down = up_t.to_numpy(), down_t.to_numpy()
    out = np.full(len(df), np.nan)
    prev = np.nan
    for i in range(len(df)):
        if not valid[i]:
            continue
        if bullish[i]:
            value = prev if (not np.isnan(prev) and up[i] < prev) else up[i]
        else:
            value = prev if (not np.isnan(prev) and down[i] > prev) else down[i]
        out[i] = value
        prev = value
    return pd.Series(out, index=df.index)


def ut_bot(df: pd.DataFrame, carpan: float = 1.0, n: int = 10) -> pd.Series:
    """UT Bot ATR trailing stop (HPotter / QuantNomad); ATR is Wilder (Pine ``ta.atr``)."""
    close = _col(df, "close").to_numpy()
    loss = float(carpan) * atr(df, n).to_numpy()
    out = np.full(len(close), np.nan)
    prev, prev_close = 0.0, np.nan
    for i in range(len(close)):
        if np.isnan(loss[i]):
            prev_close = close[i]
            continue
        c, last = close[i], prev_close
        if c > prev and last > prev:
            value = max(prev, c - loss[i])
        elif c < prev and last < prev:
            value = min(prev, c + loss[i])
        elif c > prev:
            value = c - loss[i]
        else:
            value = c + loss[i]
        out[i] = value
        prev, prev_close = value, c
    return pd.Series(out, index=df.index)


def sar(df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
    """Parabolic SAR, a port of TA-Lib's ``TA_SAR`` (initial direction from -DM of the first bar pair)."""
    high, low = _col(df, "high").to_numpy(), _col(df, "low").to_numpy()
    size = len(high)
    out = np.full(size, np.nan)
    if size < 2:
        return pd.Series(out, index=df.index)
    step, cap = float(acceleration), float(maximum)
    up, down = high[1] - high[0], low[0] - low[1]
    is_long = not (down > up and down > 0)
    new_high, new_low = high[0], low[0]
    ep, value = (high[1], new_low) if is_long else (low[1], new_high)
    new_low, new_high = low[1], high[1]
    af = step
    for today in range(1, size):
        prev_low, prev_high = new_low, new_high
        new_low, new_high = low[today], high[today]
        if is_long:
            if new_low <= value:
                is_long = False
                value = max(ep, prev_high, new_high)
                out[today] = value
                af, ep = step, new_low
                value = value + af * (ep - value)
                value = max(value, prev_high, new_high)
            else:
                out[today] = value
                if new_high > ep:
                    ep, af = new_high, min(af + step, cap)
                value = value + af * (ep - value)
                value = min(value, prev_low, new_low)
        else:
            if new_high >= value:
                is_long = True
                value = min(ep, prev_low, new_low)
                out[today] = value
                af, ep = step, new_high
                value = value + af * (ep - value)
                value = min(value, prev_low, new_low)
            else:
                out[today] = value
                if new_low < ep:
                    ep, af = new_low, min(af + step, cap)
                value = value + af * (ep - value)
                value = max(value, prev_high, new_high)
    return pd.Series(out, index=df.index)


def fisher_rsi(df: pd.DataFrame, src: str = "close", n: int = 14) -> pd.Series:
    """Fisher transform of RSI as in the Freqtrade sample strategies: tanh(0.1 * (RSI - 50))."""
    return np.tanh(0.1 * (rsi(df, src, int(n)) - 50.0))


def rvol(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Relative volume: volume / SMA(volume, n), the current bar included."""
    vol = _col(df, "volume")
    return vol / vol.rolling(int(n)).mean()


def rrs(df: pd.DataFrame, n: int = 12, benchmark: pd.DataFrame | None = None) -> pd.Series:
    """Real relative strength vs a benchmark (ATR-normalised excess move over n bars)."""
    if benchmark is None:
        raise ValueError("rrs needs a benchmark DataFrame")
    n = int(n)
    bench = benchmark.reindex(df.index, method="ffill")
    power = (_col(bench, "close") - _col(bench, "close").shift(n)) / atr(bench, n).shift(1)
    asset_atr = atr(df, n).shift(1)
    expected = power * asset_atr
    return ((_col(df, "close") - _col(df, "close").shift(n)) - expected) / asset_atr


def _price(name: str) -> Callable[..., pd.Series]:
    return lambda df: _col(df, name)


REGISTRY: dict[str, Callable[..., pd.Series | pd.DataFrame]] = {
    "sma": sma, "ema": ema, "wma": wma, "rsi": rsi, "atr": atr, "adx": adx, "dmi": dmi, "cci": cci,
    "macd": macd, "bb": bb, "kc": kc, "donchian": donchian, "stoch": stoch, "obv": obv, "mfi": mfi,
    "vwap": vwap, "kama": kama, "ichimoku": ichimoku, "supertrend": supertrend, "roc": roc,
    "zscore": zscore, "highest": highest, "lowest": lowest, "ott": ott, "pmax": pmax, "rvol": rvol,
    "stdev": stdev, "var": var, "rrs": rrs, "atr_ratio": atr_ratio,
    "heikinashi": heikinashi, "alphatrend": alphatrend, "ut_bot": ut_bot, "sar": sar, "fisher_rsi": fisher_rsi,
    "open": _price("open"), "high": _price("high"), "low": _price("low"), "close": _price("close"), "volume": _price("volume"),
}

# Named output columns (None = plain Series); used by engine.spec to validate ``name.attr``.
COLUMNS: dict[str, tuple[str, ...] | None] = {
    "dmi": ("plus", "minus", "adx"), "macd": ("macd", "signal", "hist"), "bb": ("upper", "basis", "lower"),
    "kc": ("upper", "basis", "lower"), "donchian": ("upper", "lower", "mid"), "stoch": ("k", "d"),
    "ichimoku": ("tenkan", "kijun", "span_a", "span_b"), "supertrend": ("line", "dir"),
    "ott": ("ma", "ott", "dir", "long_stop", "short_stop", "up", "dn"),
    "pmax": ("pmax", "ma", "dir", "long_stop", "short_stop"),
    "heikinashi": ("open", "high", "low", "close"),
}

# Meta indicator evaluated by build_env, not a function of the frame: {f: seri, ifade: "<expression>"}
SERI = "seri"


# --------------------------------------------------------- multi-timeframe
def _htf_keys(index: pd.DatetimeIndex, tf: str) -> np.ndarray:
    naive = index.tz_localize(None) if index.tz is not None else index
    tf = tf.strip()
    unit, count = tf[-1], int(tf[:-1] or 1)
    if unit == "W":
        return naive.to_period("W-SUN").to_timestamp().to_numpy()
    if unit == "M" and tf.endswith("M") and count >= 1 and tf[:-1].isdigit() and tf != f"{count}m":
        return naive.to_period("M").to_timestamp().to_numpy()
    if unit == "D":
        return naive.floor(f"{count}D").to_numpy()
    if unit == "H":
        return naive.floor(f"{count}h").to_numpy()
    if unit == "m":
        return naive.floor(f"{count}min").to_numpy()
    raise ValueError(f"unsupported timeframe: {tf}")


def resample_htf(df: pd.DataFrame, tf: str) -> tuple[pd.DataFrame, np.ndarray]:
    """Aggregate ``df`` to ``tf`` bars; returns (htf frame, per-bar bin keys).

    Intraday bins floor the UTC clock; exchange-session-aware 4H bars come from
    ``engine.resample.resample_4h``.
    """
    keys = _htf_keys(df.index, tf)
    agg = {c: _AGG[c] for c in OHLCV if c in df.columns}
    htf = df.groupby(keys, sort=True).agg(agg)
    return htf, keys


def align_htf(htf_values: pd.Series | pd.DataFrame, keys: np.ndarray, index: pd.Index) -> pd.Series | pd.DataFrame:
    """Map higher-timeframe values to base bars using the previous completed HTF bar."""
    previous = htf_values.shift(1)
    mapped = previous.reindex(keys)
    mapped.index = index
    return mapped


def align_htf_label(htf_values: pd.Series | pd.DataFrame, index: pd.DatetimeIndex, week_end: str) -> pd.Series | pd.DataFrame:
    """Weekly values keyed by the calendar week-end label (Friday or Sunday), forward filled.

    A week counts as complete on its calendar end date, so that day's own close may use it
    (the T1a reference alignment). Earlier days of the week see the previous week.
    """
    offset = pd.DateOffset(days=4 if week_end.upper() == "FRI" else 6)
    labelled = htf_values.copy()
    labelled.index = pd.DatetimeIndex(htf_values.index) + offset
    naive = index.tz_localize(None) if index.tz is not None else index
    mapped = labelled.reindex(naive.normalize(), method="ffill")
    mapped.index = index
    return mapped


def compute(
    df: pd.DataFrame,
    spec: Mapping[str, Any],
    *,
    benchmarks: Mapping[str, pd.DataFrame] | None = None,
    week_end: str | None = None,
) -> pd.Series | pd.DataFrame:
    """Evaluate one card indicator spec (``{f, src, n, tf, kaydir, ...}``) on ``df``.

    ``hizalama: etiket`` (weekly ``tf`` only) uses :func:`align_htf_label`; ``week_end`` is
    ``"FRI"`` for exchange assets and ``"SUN"`` for crypto.
    """
    params = dict(spec)
    alignment = params.pop("hizalama", None)
    name = params.pop("f")
    if name not in REGISTRY:
        raise UnknownIndicator(name)
    func = REGISTRY[name]
    tf = params.pop("tf", None)
    lag = int(params.pop("kaydir", 0) or 0)
    on_ha = bool(params.pop("ha", False))
    if on_ha:
        df = heikinashi(df).join(df["volume"]) if "volume" in df.columns else heikinashi(df)
    bench_name = params.pop("benchmark", None)
    if bench_name is not None:
        if not benchmarks or bench_name not in benchmarks:
            raise ValueError(f"benchmark '{bench_name}' not provided")
        params["benchmark"] = benchmarks[bench_name]
    if tf:
        htf, keys = resample_htf(df, tf)
        if bench_name is not None:
            params["benchmark"] = resample_htf(params["benchmark"], tf)[0]
        htf_values = func(htf, **params)
        if alignment == "etiket":
            if not tf.strip().upper().endswith("W") or week_end is None:
                raise ValueError("hizalama: etiket needs a weekly tf and a week_end")
            result = align_htf_label(htf_values, df.index, week_end)
        elif alignment is not None:
            raise ValueError(f"unknown hizalama: {alignment}")
        else:
            result = align_htf(htf_values, keys, df.index)
    else:
        result = func(df, **params)
    return result.shift(lag) if lag else result


def build_env(df: pd.DataFrame, gostergeler: Mapping[str, Mapping[str, Any]], *, benchmarks: Mapping[str, pd.DataFrame] | None = None, week_end: str | None = None) -> dict[str, Any]:
    """Name -> Series/DataFrame environment for ``engine.expr`` evaluation."""
    env: dict[str, Any] = {c: _col(df, c) for c in OHLCV if c in df.columns}
    if benchmarks and "endeks" in benchmarks:
        env["endeks_close"] = _col(benchmarks["endeks"], "close").reindex(df.index, method="ffill")
    for key, spec in gostergeler.items():
        spec = dict(spec)
        if spec.get("f") == SERI:
            if set(spec) - {"f", "ifade"}:
                raise ValueError(f"seri '{key}' supports only 'ifade'")
            result = _expr.parse(spec["ifade"]).evaluate(env, index=df.index)
            env[key] = pd.Series(result, index=df.index) if not isinstance(result, pd.Series) else result
            continue
        if isinstance(spec.get("src"), str) and spec["src"] not in OHLCV and spec["src"] not in _NAMED_SOURCES:
            spec["src"] = source(df, spec["src"], extra=env)
        env[key] = compute(df, spec, benchmarks=benchmarks, week_end=week_end)
    return env
