"""Motor: bar basina yeniden kurulan stop/hedef (dinamik_cikis) ve bar ici limit kademeli cikis; elle hesaplanmis senaryolar."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from engine.kart_sinyal import build_plan, card_frame_signals
from engine.portfolio import run_portfolio
from engine.spec import validate_card

NAN = float("nan")


def _frame(opens, lows, highs=None, closes=None) -> pd.DataFrame:
    index = pd.date_range("2024-01-02", periods=len(opens), freq="B", tz="UTC")
    return pd.DataFrame({
        "open": opens, "low": lows,
        "high": highs if highs is not None else [value + 2 for value in opens],
        "close": closes if closes is not None else opens, "volume": 1_000,
    }, index=index, dtype=float)


def _signals(frame: pd.DataFrame, stop_dist: float, **columns) -> pd.DataFrame:
    out = pd.DataFrame(False, index=frame.index, columns=["entry", "exit"])
    out.iloc[0, 0] = True  # entry signal on bar 0 -> fill at bar 1's open
    out["atr"] = 1.0
    out["stop_dist"] = stop_dist
    for name, values in columns.items():
        out[name] = values
    return out


def _run(frame: pd.DataFrame, signals: pd.DataFrame, **kwargs):
    return run_portfolio(
        {"TEST": frame}, lambda _f, _m: signals, market="ABD25", start=frame.index[0], end=frame.index[-1],
        cost_rate=0.0, precomputed_signals={"TEST": signals}, trail_mode=None, initial_capital=10_000.0, **kwargs,
    )


def test_dynamic_stop_is_set_at_the_close_and_active_from_the_next_bar() -> None:
    # entry 100 (stop 80); bar 1 low 96 does not touch 80; the close of bar 1 sets the stop to 97, bar 2 low 96 hits it
    frame = _frame(opens=[100, 100, 101, 102, 103], lows=[99, 96, 96, 101, 102])
    signals = _signals(frame, 20.0, dyn_stop=[NAN, 97, 97, 97, 97])
    trade = _run(frame, signals).trades.iloc[0]
    assert trade["entry_date"] == frame.index[1]
    assert trade["exit_date"] == frame.index[2] and trade["exit_price"] == pytest.approx(97.0) and trade["exit_reason"] == "stop"


def test_dynamic_stop_can_be_lowered_unless_ratcheted() -> None:
    # stop 97 after bar 1, 90 after bar 2; bar 3 low 95 is below 97 but above 90
    frame = _frame(opens=[100, 100, 101, 101, 101], lows=[99, 99, 98, 95, 99])
    signals = _signals(frame, 20.0, dyn_stop=[NAN, 97, 90, NAN, NAN])
    free = _run(frame, signals).trades.iloc[0]
    assert free["exit_reason"] == "end_of_test"
    locked = _run(frame, signals, dynamic_ratchet=True).trades.iloc[0]
    assert locked["exit_date"] == frame.index[3] and locked["exit_price"] == pytest.approx(97.0)


def test_dynamic_distance_from_entry_and_dynamic_target() -> None:
    # dyn_stop_rel 2 -> stop 98 from bar 2: bar 2 low 97.5 exits at 98
    frame = _frame(opens=[100, 100, 100, 100], lows=[99, 99, 97.5, 99])
    rel = _run(frame, _signals(frame, 20.0, dyn_stop_rel=[NAN, 2.0, 2.0, 2.0])).trades.iloc[0]
    assert rel["exit_date"] == frame.index[2] and rel["exit_price"] == pytest.approx(98.0)
    # dyn_target 103 from bar 2: bar 2 high 104 exits at the target; the initial target (none) did not exist
    frame = _frame(opens=[100, 100, 100, 100], lows=[99, 99, 99, 99], highs=[101, 104, 104, 101])
    target = _run(frame, _signals(frame, 20.0, dyn_target=[NAN, 103, 103, 103])).trades.iloc[0]
    assert target["exit_date"] == frame.index[2] and target["exit_price"] == pytest.approx(103.0)
    assert target["exit_reason"] == "target"


def test_intrabar_scaled_exit_fills_at_the_limit_and_moves_the_stop_to_entry() -> None:
    # 5 units (50 risk / 10 stop distance). TP1 105 sells half inside bar 1 and the stop moves to 100; bar 2 stops the rest at 100
    frame = _frame(opens=[100, 100, 101, 101], lows=[99, 99, 99.5, 101], highs=[101, 106, 102, 102])
    levels = [{"trigger_fn": lambda price, _d: price + 5, "oran": .5, "intrabar": True, "stop_entry": True},
              {"trigger_fn": lambda price, _d: price + 10, "oran": .5, "intrabar": True}]
    result = _run(frame, _signals(frame, 10.0), scaled_exits=levels, record_state=True)
    partial = [fill for fill in result.fills if fill["tip"] == "kismi"]
    assert len(partial) == 1 and partial[0]["fiyat"] == pytest.approx(105.0) and partial[0]["adet"] == pytest.approx(2.5)
    trade = result.trades.iloc[0]
    assert trade["exit_date"] == frame.index[2] and trade["exit_price"] == pytest.approx(100.0)
    assert trade["net_pnl"] == pytest.approx(2.5 * 5)


def test_intrabar_levels_in_one_bar_close_the_position_and_a_gap_fills_at_the_open() -> None:
    frame = _frame(opens=[100, 100, 100, 100], lows=[99, 99, 99, 99], highs=[101, 111, 101, 101])
    levels = [{"trigger_fn": lambda price, _d: price + 5, "oran": .5, "intrabar": True},
              {"trigger_fn": lambda price, _d: price + 10, "oran": .5, "intrabar": True}]
    trade = _run(frame, _signals(frame, 10.0), scaled_exits=levels).trades.iloc[0]
    assert trade["exit_date"] == frame.index[1] and trade["exit_reason"] == "target+partial"
    assert trade["net_pnl"] == pytest.approx(2.5 * 5 + 2.5 * 10)
    gap = _frame(opens=[100, 100, 107, 100], lows=[99, 99, 106, 99], highs=[101, 101, 108, 101])
    result = _run(gap, _signals(gap, 10.0), scaled_exits=levels[:1], record_state=True)
    assert [fill["fiyat"] for fill in result.fills if fill["tip"] == "kismi"] == [pytest.approx(107.0)]


def test_intrabar_level_waits_for_the_stop_check_of_the_same_bar() -> None:
    # bar 1 touches both the stop (90) and TP1 (105): the stop wins (EVRENSEL A3), no partial
    frame = _frame(opens=[100, 100, 100], lows=[99, 89, 99], highs=[101, 106, 101])
    levels = [{"trigger_fn": lambda price, _d: price + 5, "oran": .5, "intrabar": True}]
    result = _run(frame, _signals(frame, 10.0), scaled_exits=levels, record_state=True)
    assert not [fill for fill in result.fills if fill["tip"] == "kismi"]
    assert result.trades.iloc[0]["exit_reason"] == "stop"


def test_several_scaled_exits_keep_every_partial_in_the_trade_row() -> None:
    # close-triggered levels (next open fills): 2.5 units at 100, +12 on every slice -> 30
    frame = _frame(opens=[100, 100, 106, 112, 112], lows=[99, 99, 105, 111, 111])
    levels = [{"trigger_fn": lambda price, _d: price + 5, "oran": .25}, {"trigger_fn": lambda price, _d: price + 10, "oran": .5}]
    trade = _run(frame, _signals(frame, 20.0), scaled_exits=levels).trades.iloc[0]
    assert trade["net_pnl"] == pytest.approx(2.5 * 12)


def _card(**extra) -> dict:
    card = {
        "id": "TEST-DIN", "ad": "test", "kaynak": "test", "tarz": "swing", "tf": "1D", "ozel_kod": False,
        "gostergeler": {"atr14": {"f": "atr", "n": 14}}, "giris": "close > close[1]", "cikis": "close < close[5]",
        "spec_durumu": "tam", "belirsiz": [],
    }
    card.update(extra)
    return card


def test_card_fields_build_columns_and_engine_arguments() -> None:
    index = pd.date_range("2024-01-01", periods=40, freq="D", tz="UTC")
    close = np.linspace(100, 120, 40)
    frame = pd.DataFrame({"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1.0}, index=index)
    card = _card(dinamik_cikis={"stop": "close - 2 * atr14", "hedef_giristen": "3 * atr14", "mandal": True},
                 kademeli_cikis=[{"tetik": "giris + 2 * stop_mesafesi", "oran": .5, "bar_ici": True, "stop_girise": True}])
    signals, _ = card_frame_signals(card, frame, week_end="SUN")
    atr = signals["atr"]
    assert np.allclose((signals["dyn_stop"] - (frame["close"] - 2 * atr)).dropna(), 0.0)
    assert np.allclose((signals["dyn_target_rel"] - 3 * atr).dropna(), 0.0)
    plan = build_plan(card, {"X": frame}, week_end="SUN")
    assert plan.engine_kwargs["dynamic_ratchet"] is True
    level = plan.engine_kwargs["scaled_exits"][0]
    assert level["intrabar"] and level["stop_entry"] and level["trigger_fn"](100.0, 5.0) == pytest.approx(110.0)


def test_spec_accepts_the_new_fields_and_rejects_bad_ones() -> None:
    good = _card(dinamik_cikis={"stop_giristen": "2.5 * atr14"}, kademeli_cikis=[{"tetik": "giris * 1.02", "oran": .5, "bar_ici": True}])
    assert validate_card(Path("TEST-DIN.yaml"), good, {"TEST-DIN"}).errors == []
    bad = _card(dinamik_cikis={"stop": "giris_fiyati - atr14", "mandal": "evet"})
    codes = {issue.kod for issue in validate_card(Path("TEST-DIN.yaml"), bad, {"TEST-DIN"}).errors}
    assert "dinamik_cikis" in codes
