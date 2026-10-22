"""Stage 1 scan: card engine parity with T1a, engine extras, and repository card smoke run."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import tarama
from engine.kart_sinyal import EndeksYok, MotorDestegiYok, build_plan, desteklenmeyen_alan, needs_benchmark
from engine.portfolio import run_portfolio
from strategies.wd_cci_continuation_risk import signals as cci_signals
from strategies.wd_pullback_risk import signals as pullback_signals

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def synthetic(seed: int, periods: int = 3200, calendar: bool = False) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = (
        pd.date_range("2012-01-01", periods=periods, freq="D", tz="UTC")
        if calendar
        else pd.bdate_range("2012-01-02", periods=periods, tz="UTC")
    )
    close = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.015, periods)))
    open_ = close * (1 + rng.normal(0, 0.004, periods))
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) * (1 + abs(rng.normal(0, 0.006, periods))),
            "low": np.minimum(open_, close) * (1 - abs(rng.normal(0, 0.006, periods))),
            "close": close,
            "volume": rng.uniform(1e5, 2e6, periods),
        },
        index=index,
    )


def card(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "card_id, strategy, market, calendar",
    [
        ("C01", pullback_signals, "BIST30", False),
        ("C02", cci_signals, "BIST30", False),
        ("C01", pullback_signals, "KRIPTO25", True),
        ("C02", cci_signals, "KRIPTO25", True),
    ],
)
def test_card_matches_t1a_strategy_trade_for_trade(card_id, strategy, market, calendar) -> None:
    """The YAML card and the hand-written T1a strategy must give identical trade lists."""
    data = {f"S{i}": synthetic(i, calendar=calendar) for i in range(6)}
    window = dict(start=pd.Timestamp("2018-01-01", tz="UTC"), end=pd.Timestamp("2022-12-31", tz="UTC"))
    reference = run_portfolio(data, strategy, market=market, cost_rate=0.0015, **window)
    plan = build_plan(card(card_id), data, week_end="SUN" if market == "KRIPTO25" else "FRI")
    result = run_portfolio(
        data, tarama._unused_signal_function, market=market, cost_rate=0.0015,
        precomputed_signals=plan.signals, **plan.engine_kwargs, **window,
    )
    assert len(reference.trades) > 20
    keys = ["symbol", "entry_date", "exit_date", "entry_price", "exit_price", "exit_reason"]
    pd.testing.assert_frame_equal(reference.trades[keys], result.trades[keys])
    # quantities may differ in the last digits only (T1a vs card library ATR seeding)
    np.testing.assert_allclose(reference.trades["quantity"], result.trades["quantity"], rtol=1e-3)


def _flat_frame(highs, lows, opens=None, closes=None) -> pd.DataFrame:
    index = pd.date_range("2024-01-02", periods=len(highs), freq="B", tz="UTC")
    closes = closes or [100.0] * len(highs)
    opens = opens or [100.0] * len(highs)
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": 1000.0}, index=index)


def _signals(frame, entry_at=0, exit_at=None, **columns) -> pd.DataFrame:
    out = pd.DataFrame(False, index=frame.index, columns=["entry", "exit"])
    out.loc[frame.index[entry_at], "entry"] = True
    if exit_at is not None:
        out.loc[frame.index[exit_at], "exit"] = True
    out["atr"] = 2.0
    for name, value in columns.items():
        out[name] = value
    return out


def _run(frame, signals, **kwargs):
    return run_portfolio(
        {"X": frame}, lambda f, m: signals, market="ABD25", start=frame.index[0], end=frame.index[-1],
        cost_rate=0.0, precomputed_signals={"X": signals}, **kwargs,
    )


def test_target_fills_at_target_and_stop_wins_same_bar() -> None:
    frame = _flat_frame(highs=[101, 110, 101, 101, 101], lows=[99, 99, 99, 99, 99])
    result = _run(frame, _signals(frame, stop_dist=5.0, target_dist=8.0), trail_mode=None)
    trade = result.trades.iloc[0]
    assert trade["exit_reason"] == "target" and trade["exit_price"] == pytest.approx(108.0)
    # same bar touches both: pessimistic stop first
    both = _flat_frame(highs=[101, 110, 101, 101, 101], lows=[99, 90, 99, 99, 99])
    stopped = _run(both, _signals(both, stop_dist=5.0, target_dist=8.0), trail_mode=None).trades.iloc[0]
    assert stopped["exit_reason"] == "stop" and stopped["exit_price"] == pytest.approx(95.0)


def test_close_fill_enters_at_signal_close_and_charges_cost() -> None:
    frame = _flat_frame(
        highs=[103, 103, 103, 103, 103], lows=[97, 97, 97, 97, 97],
        opens=[100, 101, 102, 103, 104], closes=[100, 102, 104, 103, 104],
    )
    signals = _signals(frame, entry_at=0, exit_at=2, stop_dist=20.0)
    result = _run(frame, signals, fill_at_close=True, trail_mode=None)
    trade = result.trades.iloc[0]
    assert trade["entry_date"] == frame.index[0] and trade["entry_price"] == 100.0
    assert trade["exit_date"] == frame.index[2] and trade["exit_price"] == 104.0


def test_time_stop_cooldown_and_profit_lock() -> None:
    frame = _flat_frame(highs=[101] * 12, lows=[99] * 12)
    signals = _signals(frame, stop_dist=5.0)
    signals["entry"] = True
    timed = _run(frame, signals, trail_mode=None, time_stop_bars=3, cooldown_bars=2)
    entries = list(timed.trades["entry_date"])
    exits = list(timed.trades["exit_date"])
    assert exits[0] == frame.index[4]  # held bars 1-3, order fills at the next open
    assert (entries[1] - exits[0]).days >= 3  # cooldown: signal bars within 2 bars of the exit are ignored

    lock_frame = _flat_frame(highs=[101, 112, 103, 103], lows=[99, 99, 95, 99], opens=[100, 100, 102, 102])
    result = _run(
        lock_frame, _signals(lock_frame, stop_dist=5.0), trail_mode=None,
        profit_lock={"trigger_atr": 3.0, "stop_fn": lambda price: price * 1.001},
    )
    trade = result.trades.iloc[0]
    assert trade["exit_reason"] == "stop" and trade["exit_price"] == pytest.approx(100.1)


def test_runtime_exit_builder_uses_entry_state() -> None:
    frame = _flat_frame(highs=[101] * 8, lows=[99] * 8)
    captured = {}

    def builder(symbol, entry_date, price, stop, target):
        captured.update(symbol=symbol, price=price, stop=stop)
        flag = pd.Series(False, index=frame.index)
        flag.iloc[4:] = True
        return flag

    result = _run(frame, _signals(frame, stop_dist=5.0), trail_mode=None, exit_builder=builder)
    assert captured["symbol"] == "X" and captured["stop"] == pytest.approx(95.0)
    assert result.trades.iloc[0]["exit_date"] == frame.index[5]


def test_unsupported_and_benchmark_cards_are_reported_not_ignored() -> None:
    assert desteklenmeyen_alan({"giris": "close > 1", "kismi_kar": {"gun": 4}}) is None
    assert desteklenmeyen_alan({"giris": "close > 1", "iz_suren": {"tip": "fiyat_adim", "deger": 2}}) == "iz_suren.fiyat_adim"
    assert desteklenmeyen_alan({"giris": "close > 1", "stop": {"tip": "pips", "deger": 30}}) == "stop.pips"
    assert desteklenmeyen_alan({"giris": "close > 1", "roi_tablosu": {"0": 0.1}}) is None
    assert needs_benchmark(card("A3-003"))
    with pytest.raises(MotorDestegiYok):
        build_plan(card("O1-078"), {"X": synthetic(1)}, week_end="FRI")
    with pytest.raises(EndeksYok):
        tarama.run_card_market(card("A3-003"), {"X": synthetic(1)}, "BIST30", benchmark=None)


def test_stage_decision_rule() -> None:
    good = {"islem": 40, "PF_1x": 1.3, "net_2x": 0.01}
    assert tarama._stage_decision(good)[0]
    assert not tarama._stage_decision({**good, "islem": 29})[0]
    assert not tarama._stage_decision({**good, "PF_1x": 1.05})[0]
    assert not tarama._stage_decision({**good, "net_2x": -0.01})[0]
    assert "net_2x<=0" in tarama._stage_decision({**good, "net_2x": 0.0})[1]


@pytest.mark.skipif(not SPEC.is_dir(), reason="docs/spec not present")
def test_all_ready_daily_cards_run_or_are_skipped_with_a_reason() -> None:
    """No ready 1D/1W card may crash the scan: it either produces metrics or a named skip."""
    data = {f"S{i}": synthetic(i, periods=2800) for i in range(4)}
    benchmark = synthetic(99, periods=2800)
    cards = tarama.load_cards(SPEC, "1D,1W")
    assert len(cards) >= 40
    failures, ran, skipped = [], 0, 0
    for item in cards:
        if item.get("alias_of"):
            continue
        try:
            result = tarama.run_card_market(item, data, "ABD25", benchmark=benchmark)
            assert np.isfinite(result["net_1x"])
            ran += 1
        except (MotorDestegiYok, EndeksYok):
            skipped += 1
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{item['id']}: {type(exc).__name__}: {exc}")
    assert not failures, "\n".join(failures)
    assert ran >= 35 and skipped <= 5


def test_partial_profit_sells_fraction_once_and_locks_the_rest() -> None:
    # entry day 1 open 100; held bars: day1=1, day2=2. Close of day 2 is +6 >= trigger, so
    # 40% sells at day 3 open (108) and the stop for the rest moves to 100.1.
    frame = _flat_frame(
        highs=[101, 104, 109, 109, 109, 109], lows=[99, 99, 99, 99, 95, 95],
        opens=[100, 100, 105, 108, 108, 108], closes=[100, 103, 106, 108, 108, 100],
    )
    result = run_portfolio(
        {"X": frame}, lambda f, m: None, market="ABD25", start=frame.index[0], end=frame.index[-1], cost_rate=0.0,
        precomputed_signals={"X": _signals(frame, stop_dist=20.0)}, trail_mode=None,
        partial_profit={"gun": 2, "oran": 0.4, "trigger_atr": 2.0, "stop_fn": lambda price: price * 1.001},
    )
    assert len(result.trades) == 1
    trade = result.trades.iloc[0]
    assert trade["exit_reason"] == "stop+partial" and trade["exit_price"] == pytest.approx(100.1)
    full = trade["quantity"]
    expected = 0.4 * full * (108 - 100) + 0.6 * full * (100.1 - 100)
    assert trade["net_pnl"] == pytest.approx(expected)


def test_partial_profit_not_taken_below_trigger() -> None:
    frame = _flat_frame(highs=[101] * 6, lows=[99] * 6, closes=[100.5] * 6)
    result = run_portfolio(
        {"X": frame}, lambda f, m: None, market="ABD25", start=frame.index[0], end=frame.index[-1], cost_rate=0.0,
        precomputed_signals={"X": _signals(frame, stop_dist=20.0)}, trail_mode=None,
        partial_profit={"gun": 2, "oran": 0.4, "trigger_atr": 2.0, "stop_fn": lambda price: price},
    )
    assert not result.trades["exit_reason"].str.contains("partial").any()


def test_roi_table_exits_by_elapsed_minutes_and_after_the_stop() -> None:
    # entry day 1 open 100. ROI: 0 min -> 20%, 2 days (2880 min) -> 3%. High 104 on day 3 (elapsed 2 days) reaches 103.
    frame = _flat_frame(highs=[101, 101, 101, 104, 101], lows=[99] * 5)
    result = run_portfolio(
        {"X": frame}, lambda f, m: None, market="ABD25", start=frame.index[0], end=frame.index[-1], cost_rate=0.0,
        precomputed_signals={"X": _signals(frame, stop_dist=20.0)}, trail_mode=None,
        roi_table={0.0: 0.20, 2880.0: 0.03},
    )
    trade = result.trades.iloc[0]
    assert trade["exit_reason"] == "roi" and trade["exit_price"] == pytest.approx(103.0)
    # the stop wins on a bar that touches both
    both = _flat_frame(highs=[101, 101, 101, 104, 101], lows=[99, 99, 99, 90, 99])
    stopped = run_portfolio(
        {"X": both}, lambda f, m: None, market="ABD25", start=both.index[0], end=both.index[-1], cost_rate=0.0,
        precomputed_signals={"X": _signals(both, stop_dist=5.0)}, trail_mode=None,
        roi_table={0.0: 0.20, 2880.0: 0.03},
    ).trades.iloc[0]
    assert stopped["exit_reason"] == "stop"
