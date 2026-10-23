"""T36b: short / two-way engine, FXDK absolute cost, session flat-close and local-time calendar (docs D17)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import asama2a, tarama
from engine import expr, kart_sinyal, maliyet, spec, takvim
from engine.portfolio import run_portfolio
from tests.test_tarama import synthetic


def _noop(frame: pd.DataFrame, market: str) -> pd.DataFrame:  # pragma: no cover - signals are always precomputed
    raise RuntimeError


def _run(data, signals, **kwargs):
    start = min(frame.index[0] for frame in data.values())
    end = max(frame.index[-1] for frame in data.values())
    kwargs.setdefault("cost_rate", 0.0)
    if isinstance(signals, pd.DataFrame):
        signals = {symbol: signals for symbol in data}
    return run_portfolio(data, _noop, market="X", start=start, end=end, precomputed_signals=signals, **kwargs)


def _bars(opens, highs, lows, closes, *, freq="h", start="2024-01-02 00:00") -> pd.DataFrame:
    index = pd.date_range(start, periods=len(opens), freq=freq, tz="UTC")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": 1.0}, index=index)


def _signals(frame, *, entry=(), exit_=(), entry_short=(), exit_short=(), atr=1.0, stop_dist=None, target_dist=None, **cols):
    out = pd.DataFrame(False, index=frame.index, columns=["entry", "exit", "entry_short", "exit_short"])
    for name, rows in (("entry", entry), ("exit", exit_), ("entry_short", entry_short), ("exit_short", exit_short)):
        for row in rows:
            out.iloc[row, out.columns.get_loc(name)] = True
    out["atr"] = atr
    if stop_dist is not None:
        out["stop_dist"] = stop_dist
    if target_dist is not None:
        out["target_dist"] = target_dist
    for name, value in cols.items():
        out[name] = value
    return out


# ---- long-only behaviour is unchanged (golden values produced by the pre-T36b engine) -------------------------------

def _random_frame(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = pd.date_range("2020-01-01", periods=n, freq="h", tz="UTC")
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.004, n)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.001, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.002, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.002, n)))
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1000.0}, index=index)


def _random_signals(frame: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = len(frame)
    out = pd.DataFrame({"entry": rng.random(n) < 0.03, "exit": rng.random(n) < 0.04,
                        "atr": (frame["high"] - frame["low"]).rolling(14).mean().bfill()}, index=frame.index)
    out["stop_dist"], out["target_dist"], out["trail_atr"] = 2 * out["atr"], 3 * out["atr"], out["atr"]
    return out


@pytest.mark.parametrize("name,kwargs,trades,net,final", [
    ("baz", {}, 100, -1117.691058, 8882.308942),
    ("iz_high", {"trail_mode": "high"}, 101, -1098.518513, 8901.481487),
    ("moc_zaman", {"fill_at_close": True, "time_stop_bars": 10, "cooldown_bars": 2}, 101, -993.647075, 9006.352925),
])
def test_long_only_results_match_the_pre_t36b_engine(name, kwargs, trades, net, final) -> None:
    data = {f"S{i}": _random_frame(1500, i) for i in range(3)}
    signals = {symbol: _random_signals(frame, 10 + i) for i, (symbol, frame) in enumerate(data.items())}
    result = run_portfolio(
        data, _noop, market="X", start=pd.Timestamp("2020-01-05", tz="UTC"), end=pd.Timestamp("2020-03-01", tz="UTC"),
        cost_rate=0.0005, precomputed_signals=signals, **kwargs,
    )
    assert len(result.trades) == trades
    assert float(result.trades["net_pnl"].sum()) == pytest.approx(net, abs=1e-5)
    assert float(result.equity.iloc[-1]) == pytest.approx(final, abs=1e-5)
    assert "yon" not in result.trades.columns  # long-only runs keep the historical column set


# ---- short mirrors long -----------------------------------------------------------------------------------------------

def test_short_is_the_mirror_image_of_long_on_reflected_prices() -> None:
    """A short on prices P behaves exactly like a long on the reflection 2C - P (stop, target, trail, exit all mirror)."""
    data = {f"S{i}": _random_frame(1200, 30 + i) for i in range(2)}
    centre = 120.0
    mirror = {
        symbol: pd.DataFrame({
            "open": 2 * centre - frame["open"], "high": 2 * centre - frame["low"],
            "low": 2 * centre - frame["high"], "close": 2 * centre - frame["close"], "volume": frame["volume"],
        }) for symbol, frame in data.items()
    }
    signals = {symbol: _random_signals(frame, 50 + i) for i, (symbol, frame) in enumerate(data.items())}
    short_signals = {}
    for symbol, signal in signals.items():
        shorted = signal.copy()
        shorted["entry_short"], shorted["exit_short"] = signal["entry"], signal["exit"]
        short_signals[symbol] = shorted
    for extra in ({}, {"trail_mode": "high"}, {"trail_mode": None}, {"time_stop_bars": 8}, {"fill_at_close": True}):
        common = dict(initial_capital=1e13, max_total_risk=1.0, max_gross=1e9, risk_per_trade=0.0005)
        long_run = _run(mirror, signals, **common, **extra)
        short_run = _run(data, short_signals, direction="short", **common, **extra)
        assert len(long_run.trades) == len(short_run.trades) > 20
        np.testing.assert_allclose(long_run.trades["net_pnl"].to_numpy(), short_run.trades["net_pnl"].to_numpy(), rtol=1e-9, atol=1e-6)
        assert list(long_run.trades["exit_date"]) == list(short_run.trades["exit_date"])
        assert list(long_run.trades["exit_reason"]) == list(short_run.trades["exit_reason"])
        np.testing.assert_allclose(long_run.equity.to_numpy(), short_run.equity.to_numpy(), rtol=1e-9)
        assert set(short_run.trades["yon"]) == {"short"}


def test_short_stop_fills_above_entry_and_target_below_with_costs() -> None:
    frame = _bars(
        opens=[100, 100, 99, 98, 97, 97], highs=[100, 100, 99.5, 99, 98, 97], lows=[100, 99, 97.5, 95.5, 96.5, 96.5], closes=[100, 99, 98, 97, 97, 97],
    )
    # short signal on bar 0 fills at bar 1's open (100); stop 2.0 above (102), target 4.0 below (96) touched on bar 3
    signals = _signals(frame, entry_short=[0], stop_dist=2.0, target_dist=4.0)
    result = _run({"X": frame}, signals, direction="short", cost_rate=0.001, trail_mode=None)
    trade = result.trades.iloc[0]
    assert trade["entry_price"] == 100.0 and trade["initial_stop"] == pytest.approx(102.0)
    assert trade["exit_reason"] == "target" and trade["exit_price"] == pytest.approx(96.0)
    quantity = trade["quantity"]
    assert trade["net_pnl"] == pytest.approx(4.0 * quantity - 100.0 * quantity * 0.001 - 96.0 * quantity * 0.001)
    assert trade["r_multiple"] == pytest.approx(trade["net_pnl"] / (2.0 * quantity))


def test_short_same_bar_stop_and_target_counts_the_stop_first() -> None:
    frame = _bars(opens=[100, 100, 100], highs=[100, 103, 100], lows=[100, 94, 100], closes=[100, 98, 100])
    signals = _signals(frame, entry_short=[0], stop_dist=2.0, target_dist=4.0)
    trade = _run({"X": frame}, signals, direction="short", trail_mode=None).trades.iloc[0]
    assert trade["exit_reason"] == "stop" and trade["exit_price"] == pytest.approx(102.0)


def test_short_gap_through_stop_and_target_fill_at_the_open() -> None:
    gap_up = _bars(opens=[100, 100, 106], highs=[100, 101, 107], lows=[100, 99, 105], closes=[100, 100, 106])
    signals = _signals(gap_up, entry_short=[0], stop_dist=2.0, target_dist=10.0)
    trade = _run({"X": gap_up}, signals, direction="short", trail_mode=None).trades.iloc[0]
    assert trade["exit_reason"] == "gap_stop" and trade["exit_price"] == 106.0 and trade["net_pnl"] < 0
    gap_down = _bars(opens=[100, 100, 90], highs=[100, 101, 91], lows=[100, 99, 89], closes=[100, 100, 90])
    signals = _signals(gap_down, entry_short=[0], stop_dist=2.0, target_dist=5.0)
    trade = _run({"X": gap_down}, signals, direction="short", trail_mode=None).trades.iloc[0]
    assert trade["exit_reason"] == "gap_target" and trade["exit_price"] == 90.0 and trade["net_pnl"] > 0


def test_short_trailing_stop_ratchets_down_and_never_up() -> None:
    frame = _bars(
        opens=[100, 100, 98, 96, 96.5, 100], highs=[100, 100, 98.5, 97, 97.2, 101], lows=[100, 98, 96.5, 94, 96, 99], closes=[100, 99, 97, 95, 97.5, 100],
    )
    signals = _signals(frame, entry_short=[0], atr=1.0, stop_dist=3.0, trail_atr=1.0)
    trade = _run({"X": frame}, signals, direction="short", trail_mode="close", trail_multiple=2.0).trades.iloc[0]
    # stop 103 at the fill; close + 2 ATR after each bar: 101, 99, 97 (bar 3 close 95); bar 4's close 97.5 would loosen it to 99.5
    # but the stop stays at 97 and bar 4's high of 97.2 stops the trade out at 97
    assert trade["exit_reason"] == "stop" and trade["exit_price"] == pytest.approx(97.0)


def test_short_position_marks_to_market_negatively_with_price_rises() -> None:
    frame = _bars(opens=[100, 100, 104], highs=[100, 105, 106], lows=[100, 100, 103], closes=[100, 104, 105])
    signals = _signals(frame, entry_short=[0], stop_dist=10.0)
    result = _run({"X": frame}, signals, direction="short", trail_mode=None, initial_capital=10_000.0)
    quantity = result.trades.iloc[0]["quantity"]
    assert result.equity.iloc[1] == pytest.approx(10_000.0 - 4.0 * quantity)  # marked at the close 104 vs fill 100
    assert result.exposure.iloc[1] > 0


def test_direction_both_trades_each_side_with_its_own_rules() -> None:
    frame = _bars(
        opens=[100, 100, 101, 102, 101, 100, 99, 98, 99], highs=[100] + [103] * 8, lows=[100] + [97] * 8, closes=[100, 101, 102, 101, 100, 99, 98, 99, 100],
    )
    signals = _signals(frame, entry=[0], exit_=[2], entry_short=[4], exit_short=[6], stop_dist=5.0)
    result = _run({"X": frame}, signals, direction="both", trail_mode=None)
    assert list(result.trades["yon"]) == ["long", "short"]
    assert result.trades.iloc[0]["entry_price"] == 100.0 and result.trades.iloc[0]["exit_price"] == 102.0
    assert result.trades.iloc[1]["entry_price"] == 100.0 and result.trades.iloc[1]["exit_price"] == 98.0
    # a bar that signals both sides is ambiguous and skipped
    both = _signals(frame, entry=[0], entry_short=[0], stop_dist=5.0)
    assert _run({"X": frame}, both, direction="both", trail_mode=None).trades.empty


def test_short_direction_falls_back_to_entry_exit_columns_and_ignores_long_columns() -> None:
    frame = _bars(opens=[100, 100, 100, 100], highs=[100, 101, 101, 101], lows=[100, 99, 99, 99], closes=[100, 100, 100, 100])
    plain = pd.DataFrame({"entry": [True, False, False, False], "exit": [False, False, True, False], "atr": 1.0}, index=frame.index)
    plain["stop_dist"] = 5.0
    trade = _run({"X": frame}, {"X": plain}, direction="short", trail_mode=None).trades.iloc[0]
    assert trade["yon"] == "short" and trade["exit_date"] == frame.index[3]
    ignored = _signals(frame, entry=[0], stop_dist=5.0)  # long-only columns, direction short -> nothing
    assert _run({"X": frame}, ignored, direction="short", trail_mode=None).trades.empty


def test_long_only_features_are_rejected_for_short() -> None:
    frame = _bars(opens=[100] * 4, highs=[100] * 4, lows=[100] * 4, closes=[100] * 4)
    signals = _signals(frame, entry_short=[0], stop_dist=2.0)
    for kwargs in ({"roi_table": {0: 0.1}}, {"partial_profit": {"gun": 1, "oran": 0.5, "trigger_atr": 1.0, "stop_fn": lambda p: p}},
                   {"profit_lock": {"trigger_atr": 1.0, "stop_fn": lambda p: p}}, {"entry_order_type": "stop"}):
        with pytest.raises(ValueError, match="long-only"):
            _run({"X": frame}, signals, direction="short", **kwargs)
    with pytest.raises(ValueError, match="direction"):
        _run({"X": frame}, signals, direction="sideways")


# ---- absolute (pip) cost ----------------------------------------------------------------------------------------------

def test_cost_abs_is_charged_per_unit_on_entry_and_exit() -> None:
    frame = _bars(opens=[100, 100, 101, 101], highs=[100, 101, 102, 101], lows=[100, 99.5, 100.5, 100.5], closes=[100, 101, 101, 101])
    signals = _signals(frame, entry=[0], exit_=[1], stop_dist=5.0)
    free = _run({"X": frame}, signals, trail_mode=None).trades.iloc[0]
    costly = _run({"X": frame}, signals, trail_mode=None, cost_abs=0.02).trades.iloc[0]
    assert costly["entry_cost"] == pytest.approx(costly["quantity"] * 0.02)
    assert costly["exit_cost"] == pytest.approx(costly["quantity"] * 0.02)
    assert costly["net_pnl"] == pytest.approx(free["net_pnl"] * costly["quantity"] / free["quantity"] - 2 * costly["quantity"] * 0.02, rel=1e-6)
    short_costly = _run({"X": frame}, _signals(frame, entry_short=[0], exit_short=[1], stop_dist=5.0), direction="short", trail_mode=None, cost_abs=0.02).trades.iloc[0]
    assert short_costly["entry_cost"] == pytest.approx(short_costly["quantity"] * 0.02)


def test_fxdk_cost_model_uses_half_spread_plus_slippage_per_side() -> None:
    # USDJPY: 1 pip = 0.01; median spread 0.8 pip -> (0.4 + 0.2) pip = 0.006 per side
    assert maliyet.fxdk_tek_yon_maliyet("USDJPY", 0.8) == pytest.approx(0.006)
    assert maliyet.fxdk_tek_yon_maliyet("USDCHF", 0.8, carpan=3.0) == pytest.approx(3 * 0.6 * 0.0001)
    assert maliyet.pip_boyutu("USATECHIDXUSD") == 1.0
    assert maliyet.fxdk_tek_yon_maliyet("USDJPY", 0.8, spread_orani=1.0) == pytest.approx(0.01)
    with pytest.raises(ValueError):
        maliyet.fxdk_tek_yon_maliyet("USDJPY", -1.0)


# ---- session flat-close -----------------------------------------------------------------------------------------------

def test_session_close_flats_at_the_open_of_the_first_bar_after_the_local_time() -> None:
    # Tokyo 10:30 = 01:30 UTC. Hourly UTC bars from 2024-01-02 22:00 (Tokyo 07:00 on the 3rd).
    frame = _bars(
        opens=[100 + i for i in range(40)], highs=[200] * 40, lows=[50] * 40, closes=[100 + i for i in range(40)],
        start="2024-01-02 22:00",
    )
    signals = _signals(frame, entry=[0], stop_dist=60.0)
    trade = _run({"X": frame}, signals, trail_mode=None, session_close=("10:30", "Asia/Tokyo")).trades.iloc[0]
    assert trade["exit_reason"] == "seans_sonu"
    # entry fills at bar 1 (23:00 UTC = 08:00 JST); first bar with JST >= 10:30 is 02:00 UTC (11:00 JST) = bar 4
    assert trade["entry_date"] == frame.index[1] and trade["exit_date"] == frame.index[4]
    assert trade["exit_price"] == frame["open"].iloc[4]
    without = _run({"X": frame}, signals, trail_mode=None).trades.iloc[0]
    assert without["exit_reason"] == "end_of_test"


def test_session_close_works_for_short_and_takes_dst_from_the_tz_database() -> None:
    summer = _bars(opens=[100.0] * 30, highs=[110.0] * 30, lows=[90.0] * 30, closes=[100.0] * 30, start="2024-07-01 06:00")
    signals = _signals(summer, entry_short=[0], stop_dist=15.0)
    trade = _run({"X": summer}, signals, direction="short", trail_mode=None, session_close=("09:00", "Europe/London")).trades.iloc[0]
    # London is UTC+1 in July: 09:00 local = 08:00 UTC; entry at 07:00 UTC bar, first bar >= 09:00 BST is 08:00 UTC
    assert trade["entry_date"] == summer.index[1] and trade["exit_date"] == summer.index[2]
    with pytest.raises(ValueError, match="HH:MM"):
        _run({"X": summer}, signals, session_close=("25:00", "UTC"))


# ---- local-time calendar primitives ---------------------------------------------------------------------------------------

def _hourly(start: str, end: str) -> pd.DatetimeIndex:
    return pd.date_range(start, end, freq="h", tz="UTC")


def test_local_clock_primitives() -> None:
    index = pd.DatetimeIndex(["2024-01-02 23:00", "2024-01-03 00:30", "2024-07-01 23:15"], tz="UTC")
    assert list(takvim.saat_yerel(index, "Asia/Tokyo")) == [8, 9, 8]
    assert list(takvim.dakika_yerel(index, "Asia/Tokyo")) == [0, 30, 15]
    assert list(takvim.ay_gunu_yerel(index, "Asia/Tokyo")) == [3, 3, 2]
    assert list(takvim.haftanin_gunu_yerel(index, "Asia/Tokyo")) == [2, 2, 1]
    assert list(takvim.saat_yerel(index, "America/New_York")) == [18, 19, 19]  # EST in January, EDT in July
    naive = pd.DatetimeIndex(["2024-01-02 23:00"])
    assert list(takvim.saat_yerel(naive, "Asia/Tokyo")) == [8]  # naive index = UTC
    with pytest.raises(ValueError, match="saat dilimi"):
        takvim.saat_yerel(index, "Mars/Olympus")


def test_ay_son_is_gunu_follows_the_calendar_not_the_data() -> None:
    index = _hourly("2024-03-25 00:00", "2024-04-03 23:00")
    last = takvim.ay_son_is_gunu(index, "UTC")
    assert sorted({d.strftime("%Y-%m-%d") for d in index[last.to_numpy()]}) == ["2024-03-29"]
    second = takvim.ay_son_is_gunu(index, "UTC", 2)
    assert sorted({d.strftime("%Y-%m-%d") for d in index[second.to_numpy()]}) == ["2024-03-28"]
    # a frame that ends mid-month does not mislabel its last day as the month end
    partial = _hourly("2024-04-01 00:00", "2024-04-10 23:00")
    assert not takvim.ay_son_is_gunu(partial, "UTC").any()
    with pytest.raises(ValueError):
        takvim.ay_son_is_gunu(index, "UTC", 0)


def test_gotobi_days_shift_weekend_dates_back_to_friday_and_use_local_dates() -> None:
    index = _hourly("2024-06-01 00:00", "2024-06-30 23:00")
    days = sorted({d.strftime("%d") for d in index[takvim.gotobi(index, "UTC").to_numpy()]})
    # 5th Wed, 10th Mon (Sunday 9th? no: 10 June 2024 is Monday), 15th Sat->14th, 20th Thu, 25th Tue, 30th Sun->28th
    assert days == ["05", "10", "14", "20", "25", "28"]
    # 08:00 JST on the 5th is 23:00 UTC on the 4th: the *local* date decides
    tokyo = takvim.gotobi(index, "Asia/Tokyo")
    assert tokyo[pd.Timestamp("2024-06-04 23:00", tz="UTC")] and not tokyo[pd.Timestamp("2024-06-04 14:00", tz="UTC")]
    assert bool(tokyo[pd.Timestamp("2024-06-05 14:00", tz="UTC")])


def test_expression_language_exposes_the_local_primitives() -> None:
    index = _hourly("2024-06-03 00:00", "2024-06-05 23:00")
    env = {"close": pd.Series(1.0, index=index)}
    rule = expr.parse('saat_yerel("Asia/Tokyo") == 8 and dakika_yerel("Asia/Tokyo") == 0 and gotobi("Asia/Tokyo")')
    hits = index[rule.evaluate(env, index=index).to_numpy()]
    assert [h.strftime("%Y-%m-%d %H:%M") for h in hits] == ["2024-06-04 23:00"]  # 08:00 JST on the 5th
    assert expr.parse('ay_son_is_gunu("UTC")').funcs == {"ay_son_is_gunu"}
    assert expr.parse('ay_son_is_gunu("UTC", 2)').evaluate(env, index=index).sum() == 0
    with pytest.raises(expr.ExprError):
        expr.parse("saat_yerel(9)").evaluate(env, index=index)
    with pytest.raises(expr.ExprError):
        expr.parse("gotobi()").evaluate(env, index=index)


# ---- cards: yon / giris_short / cikis_short / seans_sonu_kapat ------------------------------------------------------------

def _card(**extra) -> dict:
    card = {"id": "T36B-X", "ad": "x", "kaynak": {}, "tarz": "day", "tf": "1H", "gostergeler": {"rsi": {"f": "rsi", "src": "close", "n": 3}},
            "giris": "rsi < 30", "cikis": "rsi > 50", "stop": {"tip": "puan", "deger": 1.0}, "spec_durumu": "tam", "belirsiz": [], "ozel_kod": False}
    card.update(extra)
    return card


def _frames(symbols=("X",)) -> dict:
    return {symbol: synthetic(seed, periods=400) for seed, symbol in enumerate(symbols)}


def test_short_card_maps_giris_cikis_to_the_short_columns_and_sets_direction() -> None:
    card = _card(yon="short", giris="rsi > 70", cikis="rsi < 50")
    plan = kart_sinyal.build_plan(card, _frames(), week_end="FRI")
    signals = plan.signals["X"]
    assert not signals["entry"].any() and not signals["exit"].any()
    assert signals["entry_short"].any() and plan.engine_kwargs["direction"] == "short"
    long_plan = kart_sinyal.build_plan(_card(), _frames(), week_end="FRI")
    assert "direction" not in long_plan.engine_kwargs and "entry_short" not in long_plan.signals["X"].columns


def test_two_way_card_builds_both_sides_and_session_close() -> None:
    card = _card(yon="iki", giris_short="rsi > 70", cikis_short="rsi < 50", seans_sonu_kapat="10:30 Asia/Tokyo")
    plan = kart_sinyal.build_plan(card, _frames(), week_end="FRI")
    signals = plan.signals["X"]
    assert signals["entry"].any() and signals["entry_short"].any()
    assert plan.engine_kwargs["direction"] == "both" and plan.engine_kwargs["session_close"] == ("10:30", "Asia/Tokyo")


def test_two_way_card_needs_giris_short_and_short_rejects_long_only_fields() -> None:
    assert kart_sinyal.desteklenmeyen_alan(_card(yon="iki")) == "yon.iki+giris_short_yok"
    assert kart_sinyal.desteklenmeyen_alan(_card(yon="short", roi_tablosu={"0": 0.1})).startswith("yon.short+roi_tablosu")
    assert kart_sinyal.desteklenmeyen_alan(_card(yon="short", stop={"tip": "seviye", "ifade": "sinyal_low"})) == "yon.short+stop.seviye"
    assert kart_sinyal.desteklenmeyen_alan(_card(yon="sideways")) == "yon.sideways"
    with pytest.raises(kart_sinyal.MotorDestegiYok):
        kart_sinyal.build_plan(_card(yon="short", kismi_kar={"gun": 1, "oran": 0.5, "tetik_atr": 1, "kalan_stop": "giris"}), _frames(), week_end="FRI")


def test_runtime_exit_of_a_short_uses_the_distance_above_the_fill() -> None:
    card = _card(yon="short", giris="rsi > 70", cikis="close > giris_fiyati + stop_mesafesi", stop={"tip": "puan", "deger": 0.5})
    plan = kart_sinyal.build_plan(card, _frames(), week_end="FRI")
    builder = plan.engine_kwargs["exit_builder"]
    frame = _frames()["X"]
    entry_date = frame.index[50]
    price = float(frame["open"].iloc[50])
    exit_series = builder("X", entry_date, price, price + 0.5, float("nan"))
    expected = (frame["close"] > price + 0.5).to_numpy()
    expected[:50] = False
    np.testing.assert_array_equal(np.asarray([exit_series[i] for i in range(len(frame))]) if not hasattr(exit_series, "to_numpy") else exit_series.to_numpy(), expected[: len(frame)])


def test_spec_validation_of_the_new_card_fields() -> None:
    def check(**extra):
        return [issue.kod for issue in spec.validate_card(__import__("pathlib").Path("T36B-X.yaml"), _card(**extra), {"T36B-X"}).issues]

    assert check() == []
    assert check(yon="iki", giris_short="rsi > 70", cikis_short="rsi < 50") == []
    assert "yon" in check(yon="sideways")
    assert "iki_giris_short" in check(yon="iki")
    assert "short_alan" in check(giris_short="rsi > 70")
    assert "seans_sonu_kapat" in check(seans_sonu_kapat="25:99 Asia/Tokyo")
    assert "seans_sonu_kapat" in check(seans_sonu_kapat="10:30 Mars/Olympus")
    assert check(seans_sonu_kapat="10:30 Asia/Tokyo") == []
    assert "tanimsiz_ad" in check(yon="iki", giris_short="rsi_yok > 70")


# ---- tarama FXDK + null model keeps the direction -----------------------------------------------------------------------------

def test_prepare_fxdk_scales_the_absolute_cost_with_the_stress_multiplier() -> None:
    data = {"USDJPY": synthetic(3, periods=400)}
    plan_card = _card(yon="short", giris="rsi > 70", cikis="rsi < 50")
    start, end = data["USDJPY"].index[0], data["USDJPY"].index[-1]
    prepared = tarama.prepare(plan_card, data, "FXDK", start=start, end=end, fxdk_spread_pip=0.8)
    assert prepared.base_cost == 0.0 and prepared.cost_abs == pytest.approx(0.006)
    assert prepared.annualization == tarama.annualization_for("1H", "FX8")
    one, two = prepared.run(1.0), prepared.run(2.0)
    assert len(one.trades) == len(two.trades) > 0
    first = one.trades.iloc[0]
    assert first["entry_cost"] == pytest.approx(first["quantity"] * 0.006)
    assert two.trades.iloc[0]["entry_cost"] == pytest.approx(two.trades.iloc[0]["quantity"] * 0.012)
    with pytest.raises(ValueError, match="fxdk_spread_pip"):
        tarama.prepare(plan_card, data, "FXDK", start=start, end=end)
    with pytest.raises(ValueError, match="tek enstruman"):
        tarama.prepare(plan_card, {"A": data["USDJPY"], "B": data["USDJPY"]}, "FXDK", start=start, end=end, fxdk_spread_pip=0.8)


def test_null_entries_keep_the_cards_direction() -> None:
    data = {"USDJPY": synthetic(5, periods=1500)}
    start, end = data["USDJPY"].index[0], data["USDJPY"].index[-1]
    rng = np.random.default_rng(1)

    short_card = _card(yon="short", giris="rsi > 70", cikis="rsi < 50")
    short = tarama.prepare(short_card, data, "FXDK", start=start, end=end, fxdk_spread_pip=0.5)
    out = asama2a.random_entry_signals(short, {"USDJPY": 12}, 1.0, rng)["USDJPY"]
    assert out["entry_short"].sum() == 12 and not out["entry"].any()
    trades = short.run(1.0, signals={"USDJPY": out}).trades
    assert len(trades) > 0 and set(trades["yon"]) == {"short"}

    two_way = _card(yon="iki", giris_short="rsi > 70", cikis_short="rsi < 50")
    both = tarama.prepare(two_way, data, "FXDK", start=start, end=end, fxdk_spread_pip=0.5)
    real = both.run(1.0).trades
    longs, shorts = asama2a.side_counts(both, real)
    assert sum(longs.values()) == (real["yon"] == "long").sum() and sum(shorts.values()) == (real["yon"] == "short").sum()
    out = asama2a.random_entry_signals(both, longs, 1.0, np.random.default_rng(2), shorts)["USDJPY"]
    assert out["entry"].sum() == sum(longs.values()) and out["entry_short"].sum() == sum(shorts.values())
    # long-only cards: counts come back as one dict, the random stream is consumed as before
    plain = tarama.prepare(_card(), data, "ABD25", start=start, end=end)
    counts, none = asama2a.side_counts(plain, pd.DataFrame({"symbol": ["USDJPY"] * 3}))
    assert counts == {"USDJPY": 3} and none is None


def test_two_way_run_through_the_engine_end_to_end() -> None:
    data = {"USDJPY": synthetic(9, periods=1200)}
    start, end = data["USDJPY"].index[0], data["USDJPY"].index[-1]
    card = _card(yon="iki", giris_short="rsi > 70", cikis_short="rsi < 50", seans_sonu_kapat="21:00 UTC")
    prepared = tarama.prepare(card, data, "FXDK", start=start, end=end, fxdk_spread_pip=0.5)
    result = prepared.run(1.0)
    assert set(result.trades["yon"]) <= {"long", "short"} and len(result.trades) > 5
    assert np.isfinite(result.equity.iloc[-1])
