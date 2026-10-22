from __future__ import annotations

import pandas as pd
import pytest

from engine.expr import ExprError, parse


def _env():
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    return {
        "close": pd.Series([1, 2, 3, 2, 1, 4.0], index=idx),
        "ema": pd.Series([2.0] * 6, index=idx),
        "x": pd.Series([float("nan"), 1, 2, 3, 4, 5], index=idx),
        "dmi": pd.DataFrame({"plus": [1.0] * 6, "minus": [2.0] * 6}, index=idx),
    }


def test_cross_over_and_lag():
    env = _env()
    result = parse("cross_over(close, ema) and close[1] < 3").evaluate(env)
    assert result.tolist() == [False, False, True, False, False, True]


def test_cross_under_with_scalar_threshold():
    result = parse("cross_under(close, 2)").evaluate(_env())
    assert result.tolist() == [False, False, False, False, True, False]


def test_comparison_with_nan_is_false():
    assert parse("x > 0").evaluate(_env()).tolist() == [False, True, True, True, True, True]


def test_boolean_logic_and_not():
    env = _env()
    assert parse("not (close > 2) or close == 4").evaluate(env).tolist() == [True, True, False, True, True, True]
    assert parse("close > 1 and close < 4").evaluate(env).tolist() == [False, True, True, True, False, False]


def test_arithmetic_attributes_and_chained_compare():
    env = _env()
    assert parse("dmi.minus - dmi.plus == 1").evaluate(env).all()
    assert parse("0 < close < 3").evaluate(env).tolist() == [True, True, False, True, True, False]
    # max(close, 2) = [2,2,3,2,2,4]; abs(close - 4) = [3,2,1,2,3,0]; difference = [-1,0,2,0,-1,4]
    assert parse("max(close, ema) - abs(close - 4) > 0").evaluate(env).tolist() == [False, False, True, False, False, True]


def test_names_attrs_funcs_collected():
    expr = parse("cross_over(close, ema) and dmi.plus > dmi.minus")
    assert expr.names == {"close", "ema", "dmi"}
    assert expr.attrs == {("dmi", "plus"), ("dmi", "minus")}
    assert expr.funcs == {"cross_over"}


@pytest.mark.parametrize(
    "text",
    [
        "__import__('os').system('x')",
        "open('f').read()",
        "close.real.imag > 1",
        "(lambda: 1)()",
        "[c for c in close]",
        "close if ema else 1",
        "close[ema] > 1",
        "close[-1] > 1",
        "close ** 2 > 1",
        "close // 2 > 1",
        "eval('1')",
        "cross_over(a=close, b=ema)",
        "close[1:2]",
        "",
        "   ",
        "close > > 1",
        "b'bytes' == close",
    ],
)
def test_unsafe_or_invalid_expressions_rejected(text):
    with pytest.raises(ExprError):
        parse(text)


def test_undefined_name_raises_at_evaluation():
    with pytest.raises(ExprError):
        parse("missing > 1").evaluate(_env())


def test_mtf_requires_callable_and_passes_series():
    env = _env()
    expr = parse('mtf("1W", close) > 2')
    with pytest.raises(ExprError):
        expr.evaluate(env)
    calls = []

    def fake(tf, series):
        calls.append(tf)
        return series * 2

    assert expr.evaluate(env, mtf=fake).tolist() == [False, True, True, True, False, True]
    assert calls == ["1W"]


def test_calendar_primitives_in_expressions():
    idx = pd.bdate_range("2024-01-01", "2024-03-29")
    env = {"close": pd.Series(1.0, index=idx)}
    first = parse("ay_islem_gunu_bastan(1)").evaluate(env)
    assert idx[first.to_numpy()].strftime("%m-%d").tolist() == ["01-01", "02-01", "03-01"]
    last = parse("ay_islem_gunu_sondan(1)").evaluate(env)
    assert idx[last.to_numpy()].strftime("%m-%d").tolist() == ["01-31", "02-29", "03-29"]
    assert parse("haftanin_gunu() == 0").evaluate(env).sum() == (idx.weekday == 0).sum()


def test_valuewhen_highestsince_lowestsince_yeni_gun():
    idx = pd.to_datetime(["2024-01-01 10:00", "2024-01-01 11:00", "2024-01-02 10:00", "2024-01-02 11:00", "2024-01-03 10:00"])
    env = {"high": pd.Series([5, 7, 6, 9, 4.0], index=idx), "close": pd.Series([1, 2, 3, 4, 5.0], index=idx)}
    assert parse("yeni_gun()").evaluate(env).tolist() == [True, False, True, False, True]
    assert parse("valuewhen(yeni_gun(), close[1])").evaluate(env).fillna(-1).tolist() == [-1, -1, 2, 2, 4]
    assert parse("highestsince(yeni_gun(), high)").evaluate(env).fillna(-1).tolist() == [5, 7, 6, 9, 4]
    assert parse("lowestsince(yeni_gun(), high)").evaluate(env).fillna(-1).tolist() == [5, 5, 6, 6, 4]
    with pytest.raises(ExprError):
        parse("yeni_gun(1)").evaluate(env)
    with pytest.raises(ExprError):
        parse("valuewhen(close)").evaluate(env)


def test_paskalya_and_ay_gunu_calendar_primitives() -> None:
    import pandas as pd

    from engine import expr, takvim

    assert [takvim._easter_sunday(y).date().isoformat() for y in (2023, 2024, 2025, 2026)] == [
        "2023-04-09", "2024-03-31", "2025-04-20", "2026-04-05",
    ]
    index = pd.bdate_range("2024-03-01", "2024-04-30")
    env = {"close": pd.Series(1.0, index=index)}
    holy_thursday = expr.parse("paskalya(-3)").evaluate(env, index=index)
    assert list(index[holy_thursday]) == [pd.Timestamp("2024-03-28")]
    assert list(index[expr.parse("paskalya(-4)").evaluate(env, index=index)]) == [pd.Timestamp("2024-03-27")]
    assert list(index[expr.parse("paskalya(-9)").evaluate(env, index=index)]) == [pd.Timestamp("2024-03-22")]
    day = expr.parse("ay_gunu() == 15").evaluate(env, index=index)
    assert list(index[day]) == [pd.Timestamp("2024-03-15"), pd.Timestamp("2024-04-15")]
