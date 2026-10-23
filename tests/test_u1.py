"""U1b: trend_sepet / agirlik (engine/rotasyon.py), yeni gosterge ilkelleri ve U1 kartlari (docs/GOREV_U1.md)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine import gosterge, rotasyon
from engine.kart_sinyal import build_plan
from engine.portfolio import run_portfolio
from engine.spec import validate_card

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
U1_IDS = ["U1-H1-TS", "U1-H1-XS", "U1-H2-A", "U1-H2-B", "U1-H2-C"]
CLASSES = {"A1": "AA", "A2": "AA", "A3": "AA", "B1": "BB", "B2": "BB", "C1": "CC", "C2": "CC", "C3": "CC"}


def frame(close: np.ndarray, start: str = "2018-01-01") -> pd.DataFrame:
    index = pd.bdate_range(start, periods=len(close), tz="UTC")
    close = pd.Series(close, index=index)
    return pd.DataFrame({"open": close.shift(1).fillna(close), "high": close * 1.01, "low": close * 0.99, "close": close, "volume": 1000.0})


def walk(seed: int, drift: float, vol: float, n: int = 500) -> np.ndarray:
    return 100 * np.exp(np.cumsum(np.random.default_rng(seed).normal(drift, vol, n)))


def universe() -> dict[str, pd.DataFrame]:
    """AA: all rising (a: low vol, b: high vol), BB: one falling one rising, CC: falling."""
    drifts = {"A1": 0.002, "A2": 0.002, "A3": 0.002, "B1": 0.002, "B2": -0.002, "C1": -0.002, "C2": -0.002, "C3": -0.002}
    vols = {"A1": 0.004, "A2": 0.012, "A3": 0.008, "B1": 0.008, "B2": 0.008, "C1": 0.008, "C2": 0.008, "C3": 0.008}
    return {s: frame(walk(i, drifts[s], vols[s])) for i, s in enumerate(CLASSES)}


def sepet_card(**overrides) -> dict:
    block = {
        "kip": "trend_sepet", "dengeleme": {"tip": "ay"}, "filtre": "roc60 > 0 and close > sma100",
        "agirlik": "ters_vol", "vol_n": 60, "sinif_butce": {"AA": 0.5, "BB": 0.3, "CC": 0.2},
    }
    block.update(overrides)
    return {"gostergeler": {"roc60": {"f": "roc", "src": "close", "n": 60}, "sma100": {"f": "sma", "src": "close", "n": 100}}, "rotasyon": block}


def last_weights(card: dict, frames=None, **kwargs) -> pd.Series:
    table = rotasyon.agirliklar(card, frames or universe(), siniflar=CLASSES, **kwargs)
    decided = table.attrs["karar"].to_numpy(bool) & (table.abs().sum(axis=1) > 0).to_numpy()
    return table[decided].iloc[-1]


# --------------------------------------------------------------------------------------------- trend_sepet
def test_trend_only_budget_inverse_vol_and_cash():
    row = last_weights(sepet_card())
    assert row.sum() <= 1 + 1e-9
    assert (row >= 0).all()
    assert row[["C1", "C2", "C3"]].sum() == 0  # falling class: no signal, budget stays in cash
    # A class: all three pass the filter, the whole class budget is split by inverse vol
    assert row[["A1", "A2", "A3"]].sum() == pytest.approx(0.5)
    assert row["A1"] > row["A3"] > row["A2"]  # lower volatility, larger weight
    # B class: only B1 passes; B2's slice stays in cash, so the class holds less than its budget
    assert row["B2"] == 0 and 0 < row["B1"] < 0.3


def test_trend_only_equal_weight_option():
    row = last_weights(sepet_card(agirlik="esit"))
    assert row[["A1", "A2", "A3"]].tolist() == pytest.approx([0.5 / 3] * 3)


def test_trend_sepet_no_leverage_when_budgets_sum_to_one():
    table = rotasyon.agirliklar(sepet_card(sinif_butce={"AA": 0.4, "BB": 0.3, "CC": 0.3}), universe(), siniflar=CLASSES)
    assert table.sum(axis=1).max() <= 1 + 1e-9


def test_trend_sepet_needs_class_map():
    with pytest.raises(rotasyon.RotasyonVeriYok):
        rotasyon.agirliklar(sepet_card(), universe())
    with pytest.raises(rotasyon.RotasyonVeriYok):
        rotasyon.agirliklar(sepet_card(sinif_butce={"AA": 0.5, "BB": 0.5}), universe(), siniflar=CLASSES)


def ranked_card(**overrides) -> dict:
    card = sepet_card(skor="roc60", grup={"AA": "g1", "BB": "g1", "CC": "g2"}, k={"g1": 2, "g2": 1}, sinif_butce={"AA": 0.25, "BB": 0.25, "CC": 0.5})
    card["rotasyon"].update(overrides)
    return card


def test_ranked_top_k_per_group_and_group_budget():
    row = last_weights(ranked_card())
    held = row[row > 0]
    assert len(held) <= 2  # g1 keeps at most 2, g2 has no filter passer
    assert row[["C1", "C2", "C3"]].sum() == 0
    assert held.sum() == pytest.approx(0.5)  # the group's budget (AA + BB) is fully split among the picks
    wide = last_weights(ranked_card(k_carpan=2))
    assert (wide > 0).sum() <= 4 and (wide > 0).sum() >= (row > 0).sum()


def test_ranked_scores_are_z_scored_inside_a_class():
    """A class whose raw scores are all 10x larger must not crowd out the other class of the same group."""
    frames = universe()
    for s in ("A1", "A2", "A3"):  # same direction, much steeper trend
        frames[s] = frame(walk(abs(hash(s)) % 50, 0.006, 0.01))
    for s in ("B1",):
        frames[s] = frame(walk(77, 0.002, 0.008))
    frames["B2"] = frame(walk(78, 0.0022, 0.008))
    row = last_weights(ranked_card(k={"g1": 3, "g2": 1}), frames)
    assert row[["B1", "B2"]].sum() > 0  # raw ranking would hand all three picks to class AA


def test_trend_sepet_decisions_look_ahead_free():
    card, frames = sepet_card(), universe()
    full = rotasyon.agirliklar(card, frames, siniflar=CLASSES)
    month = pd.Series(full.index.tz_localize(None).to_period("M"), index=full.index)
    cut = pd.Timestamp(full.index[400:][(month[400:] != month[400:].shift(-1)).to_numpy()][0])  # a real month end
    part = rotasyon.agirliklar(card, {s: f[f.index <= cut] for s, f in frames.items()}, siniflar=CLASSES)
    pd.testing.assert_frame_equal(full.loc[:cut], part.loc[:cut], check_freq=False, check_exact=False, atol=1e-12)


def test_null_keeps_holding_counts_per_unit():
    card, frames = sepet_card(), universe()
    ctx = rotasyon.hazirla(card, frames, siniflar=CLASSES)
    rng = np.random.default_rng(1)
    shuffled = ctx.null(rng)
    decided = ctx.weights.attrs["karar"].to_numpy(bool)
    for group in (["A1", "A2", "A3"], ["B1", "B2"], ["C1", "C2", "C3"]):
        real_count = (ctx.weights[group] > 0).sum(axis=1).to_numpy()[decided]
        null_count = (shuffled[group] > 0).sum(axis=1).to_numpy()[decided]
        assert (real_count == null_count).all()
    assert not ctx.weights.equals(shuffled)


def test_run_end_to_end_no_leverage():
    card, frames = sepet_card(), universe()
    result = rotasyon.kos(card, frames, start=pd.Timestamp("2019-06-03", tz="UTC"), end=frames["A1"].index[-1], cost_rate=0.001, siniflar=CLASSES)
    assert (result.exposure <= 1 + 1e-6).all()
    assert result.equity.iloc[-1] > 0


def test_validation_errors():
    assert rotasyon.dogrula(sepet_card()) == []
    assert rotasyon.dogrula(ranked_card()) == []
    assert any("sinif_butce" in p for p in rotasyon.dogrula(sepet_card(sinif_butce={"AA": 0.8, "BB": 0.5})))
    assert any("birlikte" in p for p in rotasyon.dogrula(sepet_card(skor="roc60")))
    assert any("agirlik" in p for p in rotasyon.dogrula(sepet_card(agirlik="kelly")))
    assert any("k anahtarlari" in p for p in rotasyon.dogrula(ranked_card(k={"g1": 2, "zz": 1})))
    assert any("filtre" in p for p in rotasyon.dogrula(sepet_card(filtre="")))


# --------------------------------------------------------------------------------------------- kesitsel agirlik
def test_kesitsel_inverse_vol_sums_to_one_and_default_unchanged():
    frames = universe()
    base = {"gostergeler": {"roc60": {"f": "roc", "src": "close", "n": 60}}, "rotasyon": {"kip": "kesitsel", "dengeleme": {"tip": "ay"}, "skor": "roc60", "n": 3}}
    equal = rotasyon.agirliklar(base, frames)
    last = equal[equal.abs().sum(axis=1) > 0].iloc[-1]
    assert last[last > 0].tolist() == pytest.approx([1 / 3] * 3)
    base["rotasyon"]["agirlik"] = "ters_vol"
    weighted = rotasyon.agirliklar(base, frames)
    row = weighted[weighted.abs().sum(axis=1) > 0].iloc[-1]
    assert row.sum() == pytest.approx(1.0)
    held = row[row > 0]
    assert len(held) == 3
    vols = {s: frames[s]["close"].pct_change().rolling(60).std().iloc[-1] for s in held.index}
    ordered = sorted(held.index, key=lambda s: vols[s])
    assert list(held[ordered]) == sorted(held, reverse=True)  # lower vol, larger weight


# --------------------------------------------------------------------------------------------- gosterge ilkelleri
def intraday(freq: str, bars: int, seed: int = 3) -> pd.DataFrame:
    index = pd.date_range("2024-03-01", periods=bars, freq=freq, tz="UTC")
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, bars)))
    open_ = np.r_[close[0], close[:-1]]
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * 1.001, "low": np.minimum(open_, close) * 0.999, "close": close, "volume": 5.0}, index=index)


def test_gun_acilis_is_first_open_of_the_utc_day():
    df = intraday("1h", 24 * 5)
    out = gosterge.gun_acilis(df)
    for day, part in df.groupby(df.index.normalize()):
        assert (out[part.index] == part["open"].iloc[0]).all()


def test_bb_genislik_yuzdelik_range_and_look_ahead():
    df = intraday("15min", 600)
    full = gosterge.bb_genislik_yuzdelik(df, "close", 20, 2, 100)
    assert full.dropna().between(0, 100).all()
    assert full.iloc[:118].isna().all() and full.iloc[119:].notna().all()  # 20 + 100 - 2 warm-up bars
    cut = df.iloc[:400]
    pd.testing.assert_series_equal(full.iloc[:400], gosterge.bb_genislik_yuzdelik(cut, "close", 20, 2, 100))
    pd.testing.assert_series_equal(gosterge.gun_acilis(df).iloc[:400], gosterge.gun_acilis(cut))


def test_bb_genislik_yuzdelik_narrowest_bar_is_low_rank():
    close = np.r_[np.sin(np.arange(200) / 3.0) * 5 + 100, np.full(40, 100.0)]
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": 1.0}, index=pd.date_range("2024-01-01", periods=len(close), freq="15min", tz="UTC"))
    rank = gosterge.bb_genislik_yuzdelik(df, "close", 20, 2, 100)
    assert rank.iloc[-1] == 21.0  # 21 flat bars all tie at width 0 (ties count as <=), every other bar is wider


# --------------------------------------------------------------------------------------------- kartlar
def load(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("card_id", U1_IDS)
def test_cards_validate(card_id):
    card = load(card_id)
    result = validate_card(SPEC / f"{card_id}.yaml", card, set(U1_IDS))
    assert result.issues == []
    assert card["spec_durumu"] == "tam"


def test_preregistered_trial_counts():
    counts = {cid: load(cid)["deneme_sayisi_kaynakta"] for cid in U1_IDS}
    assert counts == {"U1-H1-TS": 6, "U1-H1-XS": 4, "U1-H2-A": 4, "U1-H2-B": 2, "U1-H2-C": 4}
    for cid in U1_IDS:
        grid = load(cid)["izgara"]
        assert int(np.prod([len(item["degerler"]) for item in grid])) == counts[cid]


def test_swing_cards_match_the_preregistered_rules():
    ts, xs = load("U1-H1-TS")["rotasyon"], load("U1-H1-XS")["rotasyon"]
    assert ts["sinif_butce"] == xs["sinif_butce"] == {"BIST30": 0.25, "ABD25": 0.25, "KRIPTO25": 0.25, "EMTIA": 0.25}
    assert xs["k"] == {"hisse": 5, "kripto": 3, "emtia": 2} and xs["grup"]["BIST30"] == xs["grup"]["ABD25"] == "hisse"
    assert ts["vol_n"] == xs["vol_n"] == 60 and ts["agirlik"] == "ters_vol"


def crypto(freq: str, days: int, seed: int) -> pd.DataFrame:
    per_day = 96 if freq == "15min" else 24
    index = pd.date_range("2024-01-01", periods=days * per_day, freq=freq, tz="UTC")
    rng = np.random.default_rng(seed)
    vol = np.where((np.arange(len(index)) // 400) % 2 == 0, 0.0003, 0.004)  # alternate calm / wild stretches
    close = 100 * np.exp(np.cumsum(rng.normal(0.0001, vol)))
    open_ = np.r_[close[0], close[:-1]]
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * 1.001, "low": np.minimum(open_, close) * 0.999, "close": close, "volume": rng.uniform(1, 5, len(index))}, index=index)


@pytest.mark.parametrize(("card_id", "freq"), [("U1-H2-A", "15min"), ("U1-H2-B", "1h"), ("U1-H2-C", "1h")])
def test_day_cards_never_carry_overnight(card_id, freq):
    card = load(card_id)
    data = {"BTCUSDT": crypto(freq, 60, 1), "ETHUSDT": crypto(freq, 60, 2)}
    plan = build_plan(card, data, week_end="SUN", market="KRIPTO25")
    assert sum(int(s.entry.sum()) for s in plan.signals.values()) > 0
    result = run_portfolio(data, None, market="KRIPTO25", start=data["BTCUSDT"].index[0], end=data["BTCUSDT"].index[-1],
                           cost_rate=0.001, precomputed_signals=plan.signals, **plan.engine_kwargs)
    trades = result.trades
    assert len(trades) > 0
    assert (trades["entry_date"].dt.date == trades["exit_date"].dt.date).all()
    if card_id == "U1-H2-B":
        assert set(trades["entry_date"].dt.hour) == {14}  # the 13:00 bar closes at 14:00, the fill is the next open
        assert trades["exit_date"].dt.hour.max() <= 20
    if card_id == "U1-H2-A":
        assert trades["exit_date"].dt.strftime("%H:%M").max() <= "23:45"
