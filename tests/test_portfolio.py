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


def test_maximum_holding_period_exits_at_next_open() -> None:
    frame = _frame(lows=[99.0, 98.0, 99.0, 100.0, 101.0])
    result = run_portfolio(
        {"TEST": frame},
        _entry_only,
        market="ABD25",
        start=frame.index[0],
        end=frame.index[-1],
        cost_rate=0.0,
        time_stop_bars=3,
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == frame.index[1]
    assert trade["exit_date"] == frame.index[4]
    assert trade["exit_reason"] == "signal"


def test_pyramid_respects_the_entry_limit_and_shared_open_risk_cap() -> None:
    frame = _frame(opens=[100.0] * 5, lows=[99.0] * 5)
    signals = _entry_only(frame, "ABD25")
    signals["entry"] = True
    signals["stop_dist"] = 10.0
    result = run_portfolio(
        {"TEST": frame}, lambda _f, _m: signals, market="ABD25", start=frame.index[0], end=frame.index[-1],
        cost_rate=0.0, precomputed_signals={"TEST": signals}, trail_mode=None, pyramid_max=10,
        initial_capital=10_000.0, risk_per_trade=.005, max_total_risk=.02, record_state=True,
    )
    entries = [fill for fill in result.fills if fill["tip"] == "giris"]
    assert len(entries) == 4  # 4 x 0.5% is the complete 2% shared risk budget
    assert sum(fill["adet"] * 10.0 for fill in entries) == pytest.approx(200.0)


def test_scaled_exits_sell_fractions_of_the_original_quantity() -> None:
    frame = _frame(opens=[100, 100, 106, 112, 112], lows=[99, 99, 105, 111, 111])
    frame["close"] = [100, 100, 106, 112, 112]
    signals = _entry_only(frame, "ABD25")
    signals["stop_dist"] = 20.0
    result = run_portfolio(
        {"TEST": frame}, lambda _f, _m: signals, market="ABD25", start=frame.index[0], end=frame.index[-1],
        cost_rate=0.0, precomputed_signals={"TEST": signals}, trail_mode=None,
        scaled_exits=[{"trigger_fn": lambda price, _risk: price + 5, "oran": .25},
                      {"trigger_fn": lambda price, _risk: price + 10, "oran": .50}], record_state=True,
    )
    entries = [fill for fill in result.fills if fill["tip"] == "giris"]
    partials = [fill for fill in result.fills if fill["tip"] == "kismi"]
    assert len(entries) == 1 and len(partials) == 2
    assert sum(fill["adet"] for fill in partials) == pytest.approx(entries[0]["adet"] * .75)


def test_break_even_stop_is_active_only_on_the_bar_after_its_trigger() -> None:
    frame = _frame(opens=[100, 100, 101, 101, 101], lows=[99, 96, 99, 99, 99])
    frame["high"] = [101, 106, 102, 102, 102]  # bar 1 reaches +1R, its low remains above the original stop
    signals = _entry_only(frame, "ABD25")
    signals["stop_dist"] = 5.0
    result = run_portfolio(
        {"TEST": frame}, lambda _f, _m: signals, market="ABD25", start=frame.index[0], end=frame.index[-1],
        cost_rate=0.0, precomputed_signals={"TEST": signals}, trail_mode=None, break_even_r=1.0,
    )
    trade = result.trades.iloc[0]
    assert trade["exit_date"] == frame.index[2] and trade["exit_price"] == pytest.approx(100.0)


def _pending_signals(frame: pd.DataFrame, *, level: float, stop_dist: float = 20.0, target_dist=None) -> pd.DataFrame:
    signals = pd.DataFrame(False, index=frame.index, columns=["entry", "exit"])
    signals.iloc[0, signals.columns.get_loc("entry")] = True
    signals["atr"] = 1.0
    signals["entry_level"] = level
    signals["stop_dist"] = stop_dist
    if target_dist is not None:
        signals["target_dist"] = target_dist
    return signals


def test_pending_stop_and_limit_use_pessimistic_gap_prices() -> None:
    stop_frame = _frame(opens=[100.0, 105.0, 101.0, 102.0, 103.0])
    stop = _pending_signals(stop_frame, level=103.0)
    stop_result = run_portfolio(
        {"TEST": stop_frame}, lambda f, m: stop, market="ABD25",
        start=stop_frame.index[0], end=stop_frame.index[-1], cost_rate=0.0,
        precomputed_signals={"TEST": stop}, entry_order_type="stop", entry_order_validity=1,
    )
    assert stop_result.trades.iloc[0]["entry_price"] == 105.0

    limit_frame = _frame(opens=[100.0, 95.0, 101.0, 102.0, 103.0], lows=[99.0, 94.0, 99.0, 100.0, 101.0])
    limit = _pending_signals(limit_frame, level=97.0)
    limit_result = run_portfolio(
        {"TEST": limit_frame}, lambda f, m: limit, market="ABD25",
        start=limit_frame.index[0], end=limit_frame.index[-1], cost_rate=0.0,
        precomputed_signals={"TEST": limit}, entry_order_type="limit", entry_order_validity=1,
    )
    assert limit_result.trades.iloc[0]["entry_price"] == 95.0


def test_pending_order_expires_and_entry_bar_stop_wins() -> None:
    expired_frame = _frame(opens=[100.0] * 5)
    expired = _pending_signals(expired_frame, level=110.0)
    expired_result = run_portfolio(
        {"TEST": expired_frame}, lambda f, m: expired, market="ABD25",
        start=expired_frame.index[0], end=expired_frame.index[-1], cost_rate=0.0,
        precomputed_signals={"TEST": expired}, entry_order_type="stop", entry_order_validity=2,
    )
    assert expired_result.trades.empty

    both_frame = _frame(opens=[100.0] * 5, lows=[99.0, 94.0, 99.0, 100.0, 101.0])
    both_frame.loc[both_frame.index[1], "high"] = 110.0
    both = _pending_signals(both_frame, level=100.0, stop_dist=5.0, target_dist=5.0)
    result = run_portfolio(
        {"TEST": both_frame}, lambda f, m: both, market="ABD25",
        start=both_frame.index[0], end=both_frame.index[-1], cost_rate=0.0,
        precomputed_signals={"TEST": both}, entry_order_type="stop", entry_order_validity=1,
    )
    trade = result.trades.iloc[0]
    assert trade["entry_date"] == both_frame.index[1]
    assert trade["exit_date"] == both_frame.index[1]
    assert trade["exit_reason"] == "stop" and trade["exit_price"] == 95.0


def test_intrabar_pending_fill_has_no_same_bar_open_or_target_exit() -> None:
    # A limit filled inside the bar happened after its open: the open cannot be an exit
    # price (look-ahead) and a target touched the same day has an unknown order with the fill.
    frame = _frame(opens=[100.0, 100.0, 101.0, 102.0, 103.0], lows=[99.0, 96.0, 99.0, 100.0, 101.0])
    frame.loc[frame.index[1], "high"] = 110.0
    signals = _pending_signals(frame, level=98.0, stop_dist=10.0, target_dist=1.0)
    result = run_portfolio(
        {"TEST": frame}, lambda f, m: signals, market="ABD25",
        start=frame.index[0], end=frame.index[-1], cost_rate=0.0,
        precomputed_signals={"TEST": signals}, entry_order_type="limit", entry_order_validity=1,
    )
    trade = result.trades.iloc[0]
    assert trade["entry_date"] == frame.index[1] and trade["entry_price"] == 98.0
    assert trade["exit_date"] == frame.index[2]
    assert trade["exit_reason"] == "gap_target" and trade["exit_price"] == 101.0
