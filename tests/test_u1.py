"""U1b: gun ici ilkeller (gosterge, kart_sinyal, portfolio), U1-H2 kartlari ve backtests/u1.py (docs/GOREV_U1.md)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from backtests import u1
from engine import gosterge
from engine.kart_sinyal import build_plan, intraday_cutoffs
from engine.portfolio import run_portfolio
from engine.spec import validate_card

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
U1_IDS = ["U1-H2-A", "U1-H2-B", "U1-H2-C"]


def crypto(minutes: int, days: int, seed: int = 3, start: str = "2024-01-01") -> pd.DataFrame:
    index = pd.date_range(start, periods=days * 1440 // minutes, freq=f"{minutes}min", tz="UTC")
    rng = np.random.default_rng(seed)
    block = 1600 // minutes * 6
    vol = np.where((np.arange(len(index)) // block) % 2 == 0, 0.0003, 0.004) * np.sqrt(minutes / 15)  # calm / wild stretches
    close = 100 * np.exp(np.cumsum(rng.normal(0.0002, vol)))
    open_ = np.r_[close[0], close[:-1]]
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * 1.001, "low": np.minimum(open_, close) * 0.999,
                         "close": close, "volume": rng.uniform(1, 5, len(index))}, index=index)


def load(card_id: str, tf: str | None = None) -> dict:
    card = yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))
    if tf:
        card["tf"] = tf
    return card


def simulate(card: dict, data: dict, cost: float = 0.0015):
    plan = build_plan(card, data, week_end="SUN", market="KRIPTO25")
    first = next(iter(data.values()))
    result = run_portfolio(data, None, market="KRIPTO25", start=first.index[0], end=first.index[-1], cost_rate=cost,
                           precomputed_signals=plan.signals, **plan.engine_kwargs)
    return plan, result


# --------------------------------------------------------------------------------------------- gosterge ilkelleri
def test_gun_acilis_is_first_open_of_the_utc_day():
    df = crypto(60, 5)
    out = gosterge.gun_acilis(df)
    for _, part in df.groupby(df.index.normalize()):
        assert (out[part.index] == part["open"].iloc[0]).all()


def test_bb_genislik_yuzdelik_range_warmup_and_look_ahead():
    df = crypto(15, 8)
    full = gosterge.bb_genislik_yuzdelik(df, "close", 20, 2, 100)
    assert full.dropna().between(0, 100).all()
    assert full.iloc[:118].isna().all() and full.iloc[119:].notna().all()
    cut = df.iloc[:400]
    pd.testing.assert_series_equal(full.iloc[:400], gosterge.bb_genislik_yuzdelik(cut, "close", 20, 2, 100))
    pd.testing.assert_series_equal(gosterge.gun_acilis(df).iloc[:400], gosterge.gun_acilis(cut))


def test_bb_genislik_yuzdelik_flat_stretch_ranks_low():
    close = np.r_[np.sin(np.arange(200) / 3.0) * 5 + 100, np.full(40, 100.0)]
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0},
                      index=pd.date_range("2024-01-01", periods=len(close), freq="15min", tz="UTC"))
    assert gosterge.bb_genislik_yuzdelik(df, "close", 20, 2, 100).iloc[-1] == 21.0  # 21 flat bars tie at width 0, ties count as <=


def test_donchian_kirilim_uses_previous_bars_and_keeps_signal_for_three_bars():
    close = np.r_[np.full(30, 100.0), 105.0, 104.0, 103.0, 102.0, 101.0]
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0},
                      index=pd.date_range("2024-01-01", periods=len(close), freq="1h", tz="UTC"))
    out = gosterge.donchian_kirilim(df, n=12, bar=3)
    assert out.iloc[29] == 0 and out.iloc[30] == 1  # breakout bar: close 105 > previous 12-bar high 100
    assert out.iloc[31] == 1 and out.iloc[32] == 1 and out.iloc[33] == 0  # remembered for 3 bars, then forgotten
    pd.testing.assert_series_equal(out.iloc[:32], gosterge.donchian_kirilim(df.iloc[:32], n=12, bar=3))


# --------------------------------------------------------------------------------------------- gun ici kurallari
@pytest.mark.parametrize(("minutes", "last_entry", "first_exit"), [(15, "23:15", "23:30"), (5, "23:35", "23:40"), (60, "21:00", "23:00")])
def test_gun_sonu_cutoffs(minutes, last_entry, first_exit):
    index = pd.date_range("2024-01-01", periods=1440 // minutes, freq=f"{minutes}min", tz="UTC")
    allow = pd.Series(True, index=index)
    entry, leave = intraday_cutoffs({"gun_sonu": "23:45"}, index, allow, pd.Series(False, index=index))
    assert index[entry.to_numpy()][-1].strftime("%H:%M") == last_entry  # its exit bar closes by the cutoff
    assert index[leave.to_numpy()][0].strftime("%H:%M") == first_exit  # bar closes at/after 23:45 -> fills at 23:45
    assert leave.iloc[-1] and not leave.iloc[0]


def test_cikis_saati_is_an_exit_hour_and_the_earliest_cutoff_limits_entries():
    index = pd.date_range("2024-01-01", periods=96, freq="15min", tz="UTC")
    entry, leave = intraday_cutoffs({"cikis_saati": "20:00", "gun_sonu": "23:45"}, index, pd.Series(True, index=index), pd.Series(False, index=index))
    assert index[leave.to_numpy()][0].strftime("%H:%M") == "19:45"
    assert index[entry.to_numpy()][-1].strftime("%H:%M") == "19:30"


def test_max_entries_per_day_counts_fills_per_symbol_and_day():
    frame = crypto(60, 4)
    signals = pd.DataFrame(False, index=frame.index, columns=["entry", "exit"])
    signals.iloc[1::3, 0] = True  # an entry signal every 3rd bar
    signals.iloc[2::3, 1] = True  # flat again right after the fill
    signals["atr"] = 1.0
    kwargs = {"precomputed_signals": {"X": signals}, "market": "KRIPTO25", "start": frame.index[0], "end": frame.index[-1], "cost_rate": 0.0}
    free = run_portfolio({"X": frame}, None, **kwargs).trades
    capped = run_portfolio({"X": frame}, None, max_entries_per_day=1, **kwargs).trades
    assert free.groupby(free["entry_date"].dt.date).size().max() > 1
    assert capped.groupby(capped["entry_date"].dt.date).size().max() == 1
    assert capped["entry_date"].dt.date.nunique() == len(capped) == free["entry_date"].dt.date.nunique()  # the first fill of each day only


# --------------------------------------------------------------------------------------------- kartlar
@pytest.mark.parametrize("card_id", U1_IDS)
def test_cards_validate(card_id):
    card = load(card_id)
    assert validate_card(SPEC / f"{card_id}.yaml", card, set(U1_IDS)).issues == []
    assert card["spec_durumu"] == "tam" and card["mtf"] == "1H" and card["tf"] == "15m"
    assert card["cekirdek"] + card["kardesler"] == u1.CORE + u1.SIBLINGS


def test_preregistered_trial_counts_total_fourteen():
    counts = {cid: len(u1.variants(load(cid))) for cid in U1_IDS}
    assert counts == {"U1-H2-A": 4, "U1-H2-B": 4, "U1-H2-C": 4}
    assert all(load(cid)["deneme_sayisi_kaynakta"] == counts[cid] for cid in U1_IDS)
    assert u1.deneme_sayisi(u1.all_variants((0, 2))) == 14  # + T8-07 and V2B
    tfs = {card["tf"] for _, card in u1.all_variants((2,))}
    assert tfs == {"15m", "5m"}


def test_hat0_cards_are_run_unchanged():
    for card_id in u1.HAT0:
        (variant, card), = u1.variants(u1.load_card(card_id))
        assert variant == card_id and card == u1.load_card(card_id) and card["tf"] == "1H"


@pytest.mark.parametrize("card_id", u1.HAT0)
def test_hat0_cards_run_on_crypto_hourly(card_id, monkeypatch):
    monkeypatch.setitem(u1.PERIODS, "IS", (pd.Timestamp("2024-03-01", tz="UTC"), pd.Timestamp("2025-01-15", tz="UTC")))
    (variant, card), = u1.variants(u1.load_card(card_id))
    rows, trades = u1.run_variant(variant, card, {s: crypto(60, 400, k) for k, s in enumerate(u1.CORE[:3])}, "IS")
    pooled = rows[0]
    assert pooled["sembol"] == "HAVUZ" and pooled["islem"] > 0 and len(trades) == pooled["islem"]
    assert {r["sembol"] for r in rows[1:]} == set(u1.CORE[:3])


@pytest.mark.parametrize("card_id", U1_IDS)
@pytest.mark.parametrize("minutes", [15, 5])
def test_day_cards_end_to_end(card_id, minutes):
    card = load(card_id, f"{minutes}m")
    data = {"BTCUSDT": crypto(minutes, 90, 1), "ETHUSDT": crypto(minutes, 90, 2)}
    plan, result = simulate(card, data)
    trades = result.trades
    assert sum(int(s.entry.sum()) for s in plan.signals.values()) > 0 and len(trades) > 0
    assert (trades["entry_date"].dt.date == trades["exit_date"].dt.date).all()  # nothing is carried over midnight
    assert trades["exit_date"].dt.strftime("%H:%M").max() <= "23:45"
    if card_id == "U1-H2-B":
        entry_clock = trades["entry_date"].dt.strftime("%H:%M")
        assert entry_clock.min() >= "13:30" and entry_clock.max() <= "15:00"
        assert trades.groupby(["symbol", trades["entry_date"].dt.date]).size().max() == 1
        assert trades["exit_date"].dt.hour.max() <= 20


@pytest.mark.parametrize("card_id", U1_IDS)
def test_setup_reads_only_closed_hourly_bars(card_id):
    """Rewriting every bar from 10:00 of the last day on (current hour onward) must not change any earlier signal."""
    card = load(card_id, "15m")
    data = crypto(15, 40, 5)
    base, _ = simulate(card, {"BTCUSDT": data})
    changed = data.copy()
    cut = changed.index[-1].normalize() + pd.Timedelta(hours=10)
    rows = changed.index >= cut
    changed.loc[rows, ["open", "high", "low", "close"]] *= 1.5
    other = build_plan(card, {"BTCUSDT": changed}, week_end="SUN", market="KRIPTO25")
    # signals are decided on closed bars: everything before the first rewritten bar is identical
    before = changed.index < cut
    pd.testing.assert_frame_equal(base.signals["BTCUSDT"].loc[before], other.signals["BTCUSDT"].loc[before])


def test_hourly_setup_matches_the_previous_completed_hour():
    """U1-H2-A: the 15m bar opening at 13:00 sees the hour that CLOSED at 13:00 (the 12:00 bar), never the running one."""
    data = crypto(15, 30, 7)
    hourly = data.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    card = load("U1-H2-A", "15m")
    env = gosterge.build_env(data, card["gostergeler"])
    stamp = pd.Timestamp("2024-01-20 13:00", tz="UTC")
    assert env["close_1s"][stamp] == hourly.loc[stamp - pd.Timedelta(hours=1), "close"]
    assert env["close_1s"][stamp + pd.Timedelta(minutes=45)] == hourly.loc[stamp - pd.Timedelta(hours=1), "close"]
    assert env["close_1s"][stamp + pd.Timedelta(hours=1)] == hourly.loc[stamp, "close"]


# --------------------------------------------------------------------------------------------- runner
def test_runner_end_to_end_and_lock(tmp_path, monkeypatch):
    root = tmp_path / "data"
    for folder, minutes in (("15m", 15), ("5m", 5), ("hourly", 60)):
        (root / folder).mkdir(parents=True)
        for k, symbol in enumerate(u1.CORE[:3] + u1.SIBLINGS[:2]):
            crypto(minutes, 60, k).to_parquet(root / folder / f"{symbol}.parquet")
    monkeypatch.setitem(u1.PERIODS, "IS", (pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2024-03-01", tz="UTC")))
    out = tmp_path / "res"
    assert u1.main(["--hat", "2", "--kart-ids", "U1-H2-B", "--donem", "IS", "--veri-kok", str(root), "--results-dir", str(out)]) == 0
    summary = pd.read_csv(out / "ozet_IS.csv")
    assert set(summary["kart"]) == {"U1-H2-B"} and summary["varyant"].nunique() == 4
    pooled = summary[summary["sembol"] == "HAVUZ"]
    assert len(pooled) == 4 and (pooled["islem"] > 0).all()
    assert set(summary["grup"]) == {"havuz", "cekirdek", "kardes"}
    assert summary.loc[summary["sembol"] != "HAVUZ", "islem"].sum() == pooled["islem"].sum()  # per-coin rows slice the pooled book
    assert len(list(out.glob("islemler_*_IS.csv"))) == 4
