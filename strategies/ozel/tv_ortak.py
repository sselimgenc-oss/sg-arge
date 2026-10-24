"""U6: TradingView Pine -> Python ortak ilkeller (docs/GOREV_U6.md 5A, ozel_kod yolu).

Her TV-<id> ozel kod modulu `signals(frame, p)` yazar ve `build_plan`'i `plan()` ile kurar. Sinyaller yalniz kapanmis
barlarla uretilir (gelecek bar yok); dolum, stop/hedef ve boyut motordadir (docs/EVRENSEL_KURALLAR.md). Ilkeller Pine
`ta.*` tanimlarini izler; NaN (`na`) karsilastirmalari yanlis sayilir.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from engine import gosterge as g
from engine.kart_sinyal import KartPlan


def _df(series: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({"close": series.astype(float)})


def sma(s: pd.Series, n: int) -> pd.Series:
    return g.sma(_df(s), "close", int(n))


def ema(s: pd.Series, n: int) -> pd.Series:
    return g.ema(_df(s), "close", int(n))


def rma(s: pd.Series, n: int) -> pd.Series:
    return g.rma(s.astype(float), int(n))


def wma(s: pd.Series, n: int) -> pd.Series:
    return g.wma(_df(s), "close", int(n))


def hma(s: pd.Series, n: int) -> pd.Series:
    """Pine hma: wma(2*wma(s, n/2) - wma(s, n), round(sqrt(n))); n/2 tam sayiya kesilir."""
    return wma(2.0 * wma(s, int(n) // 2) - wma(s, int(n)), int(round(np.sqrt(n))))


def stdev(s: pd.Series, n: int) -> pd.Series:
    return s.astype(float).rolling(int(n)).std(ddof=0)


def highest(s: pd.Series, n: int) -> pd.Series:
    return s.astype(float).rolling(int(n)).max()


def lowest(s: pd.Series, n: int) -> pd.Series:
    return s.astype(float).rolling(int(n)).min()


def change(s: pd.Series, n: int = 1) -> pd.Series:
    return s.astype(float).diff(n)


def atr(frame: pd.DataFrame, n: int = 14) -> pd.Series:
    return g.atr(frame, int(n))


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    return g.rsi(_df(s), "close", int(n))


def _pair(a: Any, b: Any) -> tuple[pd.Series, pd.Series]:
    index = a.index if isinstance(a, pd.Series) else b.index
    return _s(a, index), _s(b, index)


def crossover(a: pd.Series | float, b: pd.Series | float) -> pd.Series:
    a, b = _pair(a, b)
    return ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False)


def crossunder(a: pd.Series | float, b: pd.Series | float) -> pd.Series:
    a, b = _pair(a, b)
    return ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False)


def _s(x: Any, index: pd.Index | None) -> pd.Series:
    return x if isinstance(x, pd.Series) else pd.Series(float(x), index=index)


def barssince(cond: pd.Series) -> pd.Series:
    """Son True'dan beri gecen bar sayisi (True'da 0); hic True olmadiysa NaN."""
    c = cond.fillna(False).astype(bool)
    pos = pd.Series(np.arange(len(c), dtype=float), index=c.index)
    return pos - pos.where(c).ffill()


def valuewhen(cond: pd.Series, series: pd.Series, occurrence: int = 0) -> pd.Series:
    """Pine valuewhen: kosulun `occurrence` onceki True'sunda serinin degeri."""
    c = cond.fillna(False).astype(bool)
    values = series.astype(float).where(c)
    if occurrence == 0:
        return values.ffill()
    kept = values.dropna()
    shifted = kept.shift(occurrence)
    return shifted.reindex(series.index).ffill()


def percentrank(s: pd.Series, n: int) -> pd.Series:
    """Pine ta.percentrank: onceki `n` degerin (gecerli bar haric) simdikine esit ya da kucuk olanlarinin yuzdesi."""
    x = s.astype(float).to_numpy()
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        window = x[i - n:i]
        if np.isnan(x[i]) or np.isnan(window).any():
            continue
        out[i] = 100.0 * np.count_nonzero(window <= x[i]) / n
    return pd.Series(out, index=s.index)


def pivothigh(s: pd.Series, left: int, right: int) -> pd.Series:
    """Pine ta.pivothigh: s[right] sol `left` ve sag `right` barin ikisinden de SERT buyukse degerini `right` bar sonra verir."""
    x = s.astype(float).to_numpy()
    out = np.full(len(x), np.nan)
    for i in range(left + right, len(x)):
        c = i - right
        v = x[c]
        if np.isnan(v):
            continue
        if v > x[c - left:c].max() and v > x[c + 1:i + 1].max():
            out[i] = v
    return pd.Series(out, index=s.index)


def pivotlow(s: pd.Series, left: int, right: int) -> pd.Series:
    x = s.astype(float).to_numpy()
    out = np.full(len(x), np.nan)
    for i in range(left + right, len(x)):
        c = i - right
        v = x[c]
        if np.isnan(v):
            continue
        if v < x[c - left:c].min() and v < x[c + 1:i + 1].min():
            out[i] = v
    return pd.Series(out, index=s.index)


def plan(
    card: Mapping[str, Any],
    data: Mapping[str, pd.DataFrame],
    signal_fn: Callable[[pd.DataFrame, Mapping[str, Any]], pd.DataFrame],
    *,
    own_stop: bool = False,
    level_fns_factory: Callable[[dict[str, pd.DataFrame]], dict[str, Callable[..., float]]] | None = None,
    **engine_kwargs: Any,
) -> KartPlan:
    """Kartin `parametreler` blogunu Pine girdileri olarak `signal_fn`'e verir ve motor planini kurar.

    `signal_fn` en az `entry`, `exit` (bool) ve `atr` (ATR14, boyut) sutunlari dondurur; yazarin stopu yoksa A7
    (ATR14 x 3) `stop_dist` olarak eklenir ve plan `stop_eklendi` olur."""
    params = dict(card.get("parametreler") or {})
    signals: dict[str, pd.DataFrame] = {}
    for symbol, frame in data.items():
        out = signal_fn(frame, params).reindex(frame.index)
        out["entry"] = out["entry"].fillna(False).astype(bool)
        out["exit"] = out["exit"].fillna(False).astype(bool)
        if "atr" not in out:
            out["atr"] = atr(frame, 14)
        if not own_stop and "stop_dist" not in out:
            out["stop_dist"] = 3.0 * out["atr"]
        signals[symbol] = out
    kwargs: dict[str, Any] = {"trail_mode": None, "trail_multiple": None, "fill_at_close": card.get("dolum") == "kapanis"}
    if card.get("zaman_stop"):
        kwargs["time_stop_bars"] = int(card["zaman_stop"]["bar"])
    kwargs.update(engine_kwargs)
    if level_fns_factory is not None:
        kwargs["level_fns"] = level_fns_factory(signals)
    return KartPlan(signals, kwargs, stop_eklendi=not own_stop, dolum_kapanis=bool(kwargs["fill_at_close"]))


def supertrend(frame: pd.DataFrame, n: int, factor: "pd.Series | float") -> pd.DataFrame:
    """Pine `ta.supertrend(factor, n)`; `factor` seri olabilir (rejime gore degisen carpan). dir: +1 yukselis, -1 dusus.

    `engine.gosterge.supertrend` ile ayni dongu; tek fark carpanin bar basina dizi olmasi."""
    close = frame["close"].to_numpy(dtype=float)
    src = ((frame["high"] + frame["low"]) / 2).to_numpy(dtype=float)
    atr_v = atr(frame, n).to_numpy(dtype=float)
    mult = np.full(len(close), float(factor)) if np.isscalar(factor) else np.asarray(factor, dtype=float)
    size = len(close)
    upper, lower = src + mult * atr_v, src - mult * atr_v
    line = np.full(size, np.nan)
    direction = np.full(size, np.nan)
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
    return pd.DataFrame({"line": line, "dir": -direction}, index=frame.index)


def dmi(frame: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    return g.dmi(frame, int(n))


def stop_target_levels(signals: dict[str, pd.DataFrame]) -> dict[str, Callable[..., float]]:
    """`_stop_level` / `_target_level` sutunlarindan motor level_fns (docs D10): sinyal barinda sabitlenmis mutlak seviyeler."""
    stops = {symbol: out["_stop_level"].to_numpy(dtype=float) for symbol, out in signals.items() if "_stop_level" in out}
    targets = {symbol: out["_target_level"].to_numpy(dtype=float) for symbol, out in signals.items() if "_target_level" in out}
    levels: dict[str, Callable[..., float]] = {}
    if stops:
        levels["stop"] = lambda symbol, loc, _price: float(stops[symbol][loc])
    if targets:
        levels["target"] = lambda symbol, loc, _price, _stop: float(targets[symbol][loc])
    return levels


def simulate_two_sided(
    frame: pd.DataFrame,
    long_ok: np.ndarray, short_ok: np.ndarray,
    long_sl: np.ndarray, long_tp: np.ndarray, short_sl: np.ndarray, short_tp: np.ndarray,
    *, cooldown: int = 0, exits_from_fill_bar: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Pine `strategy.position_size` kapisi ve `lastTradeBar` bekleme suresi icin iki yonlu tek pozisyon benzetimi.

    Sinyal barinin kapanisinda kosullar (`*_ok`, pozisyon ve bekleme haric) degerlendirilir; emir sonraki acilista dolar,
    ters yon girisi acik pozisyonu kapatip cevirir. Stop/hedef seviyeleri sinyal barinda sabitlenir; varsayilan olarak
    `strategy.exit` dolum barinin kapanisinda verilir ve sonraki bardan etkindir (`exits_from_fill_bar=True`: dolum
    barindan, giris emriyle ayni barda verilen exit). Ayni barda stop once sayilir, gap'te acilistan dolar.

    Doner: (long giris sinyal bari, long'u ters cevirerek kapatan short giris sinyal bari)."""
    o, h, l, c = (frame[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    size = len(frame)
    long_entry = np.zeros(size, dtype=bool)
    long_flip = np.zeros(size, dtype=bool)
    pos = 0
    pending: tuple[int, float, float] | None = None  # (yon, stop, hedef) sonraki acilista dolacak
    sl = tp = np.nan
    fill_bar = -1
    last_trade = None
    for i in range(size):
        if pending is not None:
            side, p_sl, p_tp = pending
            pending = None
            pos, sl, tp, fill_bar = side, p_sl, p_tp, i
        if pos != 0 and (fill_bar < i or exits_from_fill_bar):
            if pos == 1:
                if o[i] <= sl or l[i] <= sl:
                    pos = 0
                elif h[i] >= tp or o[i] >= tp:
                    pos = 0
            else:
                if o[i] >= sl or h[i] >= sl:
                    pos = 0
                elif l[i] <= tp or o[i] <= tp:
                    pos = 0
        elapsed = last_trade is None or (i - last_trade) >= cooldown
        if long_ok[i] and elapsed and pos <= 0:
            pending = (1, long_sl[i], long_tp[i])
            long_entry[i] = True
            last_trade = i
        elif short_ok[i] and elapsed and pos >= 0:
            if pos == 1:
                long_flip[i] = True
            pending = (-1, short_sl[i], short_tp[i])
            last_trade = i
    return long_entry, long_flip
