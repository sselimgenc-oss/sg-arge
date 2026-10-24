"""TV Ospkem6i: EMA + MACD + RSI Confluence Strategy (txts0370), BINANCE:BTCUSDT.P 4H.

Pine (birebir):
    longCondition  = close > ema(9) and close > ema(20) and rsi(14) > 50 and macd hist(12, 26, 9) > 0
    shortCondition = close < ema(9) and close < ema(20) and rsi(14) < 50 and hist < 0
    if longCondition:  strategy.entry("Long", long)
    if shortCondition: strategy.entry("Short", short)
    strategy.exit("Exit Long", "Long", stop=close*0.982, limit=close*1.06)      # her bar
    strategy.exit("Exit Short", "Short", stop=close*1.018, limit=close*0.94)    # her bar
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.tv_emulator import LONG, SHORT, Ayarlar
from strategies.ozel import tv_ortak as ta

KAYNAK = {"url": "https://www.tradingview.com/script/Ospkem6i/", "pub": "PUB;20aeb517962b4d318d6fe0e7393fb303",
          "sembol": "BINANCE:BTCUSDT.P", "tf": "240", "surum": "1.0", "surum_tarihi": "2026-04-23"}
AYARLAR = Ayarlar(default_qty_type="percent_of_equity", default_qty_value=10,
                  commission_type="percent", commission_value=0.04)


def hazirla(df: pd.DataFrame) -> dict[str, np.ndarray]:
    close = df["close"]
    fast, slow, rsi = ta.ema(close, 9), ta.ema(close, 20), ta.rsi(close, 14)
    hist = ta.ema(close, 12) - ta.ema(close, 26)
    hist = hist - ta.ema(hist, 9)
    long_ = (close > fast) & (close > slow) & (rsi > 50) & (hist > 0)
    short = (close < fast) & (close < slow) & (rsi < 50) & (hist < 0)
    return {"long": long_.to_numpy(bool), "short": short.to_numpy(bool), "close": close.to_numpy(float)}


def bar(ctx, i: int, v: dict[str, np.ndarray]) -> None:
    if v["long"][i]:
        ctx.entry("Long", LONG)
    if v["short"][i]:
        ctx.entry("Short", SHORT)
    c = v["close"][i]
    ctx.exit("Exit Long", "Long", stop=c * 0.982, limit=c * 1.06)
    ctx.exit("Exit Short", "Short", stop=c * 1.018, limit=c * 0.94)
