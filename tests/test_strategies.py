import numpy as np
import pandas as pd
import pytest

from strategies.common import completed_weekly_regime
from strategies.wd_cci_continuation_risk import signals as cci_signals
from strategies.wd_pullback_risk import signals as pullback_signals


def _market_frame(periods: int = 420) -> pd.DataFrame:
    index = pd.date_range("2022-01-03", periods=periods, freq="B", tz="UTC")
    trend = np.linspace(80.0, 140.0, periods)
    close = trend + 4.0 * np.sin(np.arange(periods) / 5.0)
    return pd.DataFrame(
        {
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": 10_000.0,
        },
        index=index,
    )


@pytest.mark.parametrize("strategy", [pullback_signals, cci_signals])
def test_future_prices_do_not_change_historical_signals(strategy) -> None:
    original = _market_frame()
    cutoff = original.index[349]
    changed = original.copy()
    changed.loc[changed.index > cutoff, ["open", "high", "low", "close"]] *= 7.0

    expected = strategy(original, "ABD25").loc[:cutoff, ["entry", "exit"]]
    actual = strategy(changed, "ABD25").loc[:cutoff, ["entry", "exit"]]
    pd.testing.assert_frame_equal(expected, actual)


def test_partial_week_does_not_change_weekly_regime() -> None:
    full = _market_frame(300)
    wednesday = full.index[full.index.weekday == 2][-2]
    friday = wednesday + pd.Timedelta(2, unit="D")
    before = completed_weekly_regime(full, "ABD25")
    changed = full.copy()
    changed.loc[wednesday:friday, "close"] *= 10.0
    after = completed_weekly_regime(changed, "ABD25")

    monday = wednesday - pd.Timedelta(2, unit="D")
    pd.testing.assert_series_equal(before.loc[monday:wednesday], after.loc[monday:wednesday])
