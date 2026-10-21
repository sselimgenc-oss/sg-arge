"""Cross-check engine.gosterge against TA-Lib on random OHLCV (skipped when TA-Lib is not installed).

TA-Lib is a development-only reference (``pip install TA-Lib``); it is not a runtime dependency.
Differences are limited to warm-up: indicators are compared after the seed has faded out.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

talib = pytest.importorskip("talib")

from engine import gosterge as g  # noqa: E402


def _ohlcv(seed: int = 0, n: int = 800) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    return pd.DataFrame(
        {
            "open": close + rng.normal(0, 0.2, n),
            "high": close + rng.uniform(0.1, 1.5, n),
            "low": close - rng.uniform(0.1, 1.5, n),
            "close": close,
            "volume": rng.uniform(1e3, 5e3, n),
        },
        index=pd.date_range("2020-01-01", periods=n, freq="D"),
    )


def _max_diff(reference, ours, skip: int) -> float:
    a, b = np.asarray(reference, float), np.asarray(ours, float)
    ok = ~np.isnan(a) & ~np.isnan(b)
    ok[:skip] = False
    assert ok.sum() > 100, "too few comparable values"
    return float(np.max(np.abs(a[ok] - b[ok])))


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_sar_matches_talib_exactly(seed):
    df = _ohlcv(seed)
    assert _max_diff(talib.SAR(df.high.values, df.low.values, 0.02, 0.2), g.sar(df), 0) < 1e-9
    assert _max_diff(talib.SAR(df.high.values, df.low.values, 0.04, 0.3), g.sar(df, 0.04, 0.3), 0) < 1e-9


def test_indicators_match_talib_after_warmup():
    df = _ohlcv(0)
    h, l, c, v = df.high.values, df.low.values, df.close.values, df.volume.values
    macd_line, macd_signal, _ = talib.MACD(c, 12, 26, 9)
    stochf_k, stochf_d = talib.STOCHF(h, l, c, 5, 3)
    checks = {
        "rsi14": (talib.RSI(c, 14), g.rsi(df, n=14), 300),
        "ema20": (talib.EMA(c, 20), g.ema(df, n=20), 300),
        "sma20": (talib.SMA(c, 20), g.sma(df, n=20), 30),
        "atr14": (talib.ATR(h, l, c, 14), g.atr(df, 14), 300),
        "cci20": (talib.CCI(h, l, c, 20), g.cci(df, 20), 30),
        "mfi14": (talib.MFI(h, l, c, v, 14), g.mfi(df, 14), 30),
        "macd": (macd_line, g.macd(df)["macd"], 300),
        "macd_signal": (macd_signal, g.macd(df)["signal"], 300),
        "stochf_k": (stochf_k, g.stoch(df, 5, 3, 1)["k"], 30),
        "stochf_d": (stochf_d, g.stoch(df, 5, 3, 1)["d"], 30),
        "adx14": (talib.ADX(h, l, c, 14), g.adx(df, 14), 400),
        "plus_di": (talib.PLUS_DI(h, l, c, 14), g.dmi(df, 14)["plus"], 400),
        "minus_di": (talib.MINUS_DI(h, l, c, 14), g.dmi(df, 14)["minus"], 400),
        "stdev20": (talib.STDDEV(c, 20, 1), g.stdev(df, n=20), 30),
        "roc10": (talib.ROC(c, 10), g.roc(df, n=10), 30),
        "wma10": (talib.WMA(c, 10), g.wma(df, n=10), 30),
    }
    for name, (reference, ours, skip) in checks.items():
        assert _max_diff(reference, ours, skip) < 1e-7, name


def test_obv_differs_from_talib_only_by_the_first_volume():
    """TA-Lib starts OBV at the first volume; the Pine definition used here starts at 0."""
    df = _ohlcv(3)
    offset = talib.OBV(df.close.values, df.volume.values) - g.obv(df).to_numpy()
    assert np.allclose(offset, df.volume.values[0])
