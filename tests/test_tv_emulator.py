"""TV-2 yürütücüsü: TradingView strateji test aracı semantiği; elle hesaplanmış senaryolar."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from engine.tv_emulator import LONG, SHORT, Ayarlar, calistir, gercekci, nedensellik


def _df(rows) -> pd.DataFrame:
    """rows: (open, high, low, close)."""
    index = pd.date_range("2024-01-01", periods=len(rows), freq="4h", tz="UTC")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=index, dtype=float)


def _modul(govde, ayarlar: Ayarlar | None = None):
    return SimpleNamespace(AYARLAR=ayarlar or Ayarlar(initial_capital=10_000), hazirla=lambda df: {}, bar=govde)


def test_market_entry_fills_at_next_open_and_close_at_the_following_open_with_commission() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=2)
        if i == 1:
            ctx.close("L")
    df = _df([(100, 101, 99, 100), (102, 103, 101, 102), (105, 106, 104, 105), (105, 106, 104, 105)])
    t = calistir(_modul(govde, Ayarlar(initial_capital=10_000, commission_value=0.1)), df).islemler
    assert len(t) == 1
    row = t.iloc[0]
    assert row["giris_bar"] == 1 and row["giris_fiyat"] == 102 and row["cikis_bar"] == 2 and row["cikis_fiyat"] == 105
    assert row["net"] == pytest.approx(2 * 3 - 0.001 * (204 + 210))


@pytest.mark.parametrize("bar_row, beklenen", [
    ((100, 103, 90, 95), 102.0),   # yüksek açılışa yakın: açılış -> yüksek -> düşük: limit önce
    ((100, 110, 98, 105), 99.0),   # düşük açılışa yakın: açılış -> düşük -> yüksek: stop önce
])
def test_intrabar_path_decides_which_bracket_leg_fills(bar_row, beklenen) -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=1)
        ctx.exit("X", "L", stop=99 if bar_row[2] == 98 else 95, limit=102 if bar_row[1] == 103 else 108)
    df = _df([(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), bar_row, (100, 100.5, 99.5, 100)])
    t = calistir(_modul(govde), df).islemler
    assert t.iloc[0]["cikis_bar"] == 2 and t.iloc[0]["cikis_fiyat"] == pytest.approx(beklenen)


def test_gap_through_stop_fills_at_open_with_slippage() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=1)
        ctx.exit("X", "L", stop=95)
    df = _df([(100, 101, 99, 100), (100, 101, 99, 100), (93, 94, 92, 93)])
    t = calistir(_modul(govde, Ayarlar(initial_capital=10_000, slippage=2, mintick=0.5)), df).islemler
    # giriş piyasa: 100 + 2 x 0,5 = 101; stop boşlukta açılıştan: 93 - 1 = 92
    assert t.iloc[0]["giris_fiyat"] == 101 and t.iloc[0]["cikis_fiyat"] == 92


def test_opposite_entry_reverses_the_position() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=1)
        if i == 1:
            ctx.entry("S", SHORT, qty=2)
    df = _df([(100, 101, 99, 100), (100, 101, 99, 100), (104, 105, 103, 104), (100, 101, 99, 100)])
    sonuc = calistir(_modul(govde), df)
    t = sonuc.islemler
    assert list(t["entry_id"]) == ["L"] and t.iloc[0]["exit_id"] == "S" and t.iloc[0]["cikis_fiyat"] == 104
    assert sonuc.ozkaynak.iloc[-1] == pytest.approx(10_000 + 4 + 2 * (104 - 100))


def test_pyramiding_limits_same_direction_entries() -> None:
    df = _df([(100, 101, 99, 100)] * 6)
    for piramit, beklenen in ((1, 1.0), (3, 3.0)):
        boyut = []

        def govde(ctx, i, v):
            ctx.entry("L", LONG, qty=1)
            boyut.append(ctx.position_size)
        calistir(_modul(govde, Ayarlar(initial_capital=10_000, pyramiding=piramit)), df)
        assert boyut[-1] == beklenen


def test_exit_issued_with_a_pending_stop_entry_is_active_on_the_fill_bar() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=1, stop=101)
            ctx.exit("TP", "L", limit=104)
    # bar 1: düşük açılışa yakın -> açılış 100 -> düşük 99,5 -> yüksek 105: 101'de giriş, 104'te çıkış aynı barda
    df = _df([(100, 100.5, 99.5, 100), (100, 105, 99.5, 103), (103, 103.5, 102.5, 103)])
    t = calistir(_modul(govde), df).islemler
    assert t.iloc[0]["giris_fiyat"] == 101 and t.iloc[0]["cikis_fiyat"] == 104 and t.iloc[0]["cikis_bar"] == 1


def test_qty_percent_exits_split_the_original_entry() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=4)
        ctx.exit("TP1", "L", qty_percent=50, limit=105)
        ctx.exit("TP2", "L", qty_percent=50, limit=110)
    df = _df([(100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100), (104, 106, 103.9, 105), (108, 111, 107.9, 110), (110, 110, 110, 110)])
    t = calistir(_modul(govde), df).islemler
    assert list(t["exit_id"]) == ["TP1", "TP2"] and list(t["adet"]) == [2, 2]
    assert t["net"].sum() == pytest.approx(2 * 5 + 2 * 10)


def test_trailing_stop_activates_and_follows_the_extreme_along_the_path() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG, qty=1)
        ctx.exit("TR", "L", trail_points=20, trail_offset=10)
    a = Ayarlar(initial_capital=10_000, mintick=0.1)
    df = _df([
        (100, 100.2, 99.8, 100),
        (100, 104, 99.5, 103.5),       # düşük yakın: 100 -> 99,5 -> 104 (102'de aktif, uç 104) -> 103,5 (stop 103 değmez)
        (103.8, 104.5, 102.5, 103),    # yüksek yakın: 103,8 -> 104,5 (uç) -> 102,5: stop 104,5 - 1 = 103,5
        (103, 103, 103, 103),
    ])
    t = calistir(_modul(govde, a), df).islemler
    assert t.iloc[0]["cikis_bar"] == 2 and t.iloc[0]["cikis_fiyat"] == pytest.approx(103.5)


def test_percent_of_equity_size_and_process_orders_on_close() -> None:
    def govde(ctx, i, v):
        if i == 0:
            ctx.entry("L", LONG)
        if i == 2:
            ctx.close_all()
    a = Ayarlar(initial_capital=10_000, default_qty_type="percent_of_equity", default_qty_value=10)
    df = _df([(100, 101, 99, 100), (110, 111, 109, 110), (120, 121, 119, 120), (130, 131, 129, 130)])
    t = calistir(_modul(govde, a), df).islemler.iloc[0]
    assert t["adet"] == pytest.approx(10.0) and t["giris_fiyat"] == 110 and t["cikis_fiyat"] == 130
    t2 = calistir(_modul(govde, a), df, process_orders_on_close=True).islemler.iloc[0]
    assert t2["giris_fiyat"] == 100 and t2["giris_bar"] == 0 and t2["cikis_fiyat"] == 120


def test_realistic_cost_override() -> None:
    a = Ayarlar(commission_value=0.0, slippage=0)
    assert gercekci(a, kripto=True) == {"commission_type": "percent", "commission_value": 0.1, "slippage": 0}
    assert gercekci(a, kripto=False)["slippage"] == 1


def _random_df(n: int = 400, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, n))
    return _df(list(zip(open_, high, low, close)))


def test_causality_check_flags_a_strategy_that_reads_the_next_bar() -> None:
    def hazirla_temiz(df):
        return {"up": (df["close"] > df["close"].shift(1)).to_numpy()}

    def hazirla_kopya(df):
        return {"up": (df["close"].shift(-1) > df["close"]).to_numpy()}

    def govde(ctx, i, v):
        if v["up"][i]:
            ctx.entry("L", LONG, qty=1)
        else:
            ctx.close("L")
    df = _random_df()
    temiz = SimpleNamespace(AYARLAR=Ayarlar(), hazirla=hazirla_temiz, bar=govde)
    kopya = SimpleNamespace(AYARLAR=Ayarlar(), hazirla=hazirla_kopya, bar=govde)
    assert nedensellik(temiz, df) == []
    assert nedensellik(kopya, df)


def test_ospkem6i_translation_runs_long_and_short_and_is_causal() -> None:
    from strategies.tv2 import ospkem6i
    df = _random_df(800, seed=3)
    sonuc = calistir(ospkem6i, df)
    yonler = set(sonuc.islemler["yon"])
    assert yonler == {LONG, SHORT}
    # her çıkış, girişten önceki bar kapanışının %1,8 / %6 bandında (ya da ters giriş)
    assert nedensellik(ospkem6i, df) == []
