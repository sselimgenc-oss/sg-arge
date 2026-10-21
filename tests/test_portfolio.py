import pandas as pd
import pytest

from engine.portfolio import run_portfolio


def _frame(*, lows=None, opens=None) -> pd.DataFrame:
    index = pd.date_range("2024-01-02", periods=5, freq="B", tz="UTC")
    open_values = opens or [100.0, 100.0, 101.0, 102.0, 103.0]
    low_values = lows or [99.0, 98.0, 99.0, 100.0, 101.0]
    return pd.DataFrame(
        {
            "open": open_values,
            "high": [value + 2 for value in open_values],
            "low": low_values,
            "close": [100.0, 101.0, 102.0, 103.0, 104.0],
            "volume": 1_000,
        },
        index=index,
    )


def _entry_then_exit(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    del market
    signals = pd.DataFrame(False, index=frame.index, columns=["entry", "exit"])
    signals.loc[frame.index[0], "entry"] = True
    signals.loc[frame.index[2], "exit"] = True
    signals["atr"] = 1.0
    return signals


def _entry_only(frame: pd.DataFrame, market: str) -> pd.DataFrame:
    del market
    signals = pd.DataFrame(False, index=frame.index, columns=["entry", "exit"])
    signals.loc[frame.index[0], "entry"] = True
    signals["atr"] = 1.0
    return signals


def test_closed_bar_signal_fills_at_next_open_not_same_bar() -> None:
    frame = _frame()
    result = run_portfolio(
        {"TEST": frame},
        _entry_then_exit,
        market="ABD25",
        start=frame.index[0],
        end=frame.index[-1],
        cost_rate=0.0,
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == frame.index[1]
    assert trade["entry_price"] == frame.iloc[1]["open"]
    assert trade["exit_date"] == frame.index[3]
    assert trade["exit_reason"] == "signal"


def test_stop_is_active_on_entry_bar() -> None:
    frame = _frame(lows=[99.0, 96.0, 99.0, 100.0, 101.0])
    result = run_portfolio(
        {"TEST": frame},
        _entry_only,
        market="ABD25",
        start="2024-01-02",
        end="2024-01-08",
        cost_rate=0.0,
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == frame.index[1]
    assert trade["exit_date"] == frame.index[1]
    assert trade["exit_price"] == pytest.approx(97.0)
    assert trade["exit_reason"] == "stop"


def test_gap_through_stop_fills_at_first_available_open() -> None:
    frame = _frame(
        opens=[100.0, 100.0, 95.0, 102.0, 103.0],
        lows=[99.0, 98.0, 94.0, 100.0, 101.0],
    )
    result = run_portfolio(
        {"TEST": frame},
        _entry_only,
        market="ABD25",
        start=frame.index[0],
        end=frame.index[-1],
        cost_rate=0.0,
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == frame.index[2]
    assert trade["exit_price"] == 95.0
    assert trade["exit_reason"] == "gap_stop"
