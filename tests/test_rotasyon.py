"""T22: rotation books (engine/rotasyon.py)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from engine import rotasyon
from engine.spec import validate_card
from pathlib import Path

START = pd.Timestamp("2019-06-03", tz="UTC")


def frame(close: np.ndarray, start: str = "2019-01-01") -> pd.DataFrame:
    index = pd.bdate_range(start, periods=len(close), tz="UTC")
    close = pd.Series(close, index=index)
    return pd.DataFrame({"open": close.shift(1).fillna(close) * 1.001, "high": close * 1.01, "low": close * 0.99, "close": close, "volume": 1000.0})


def walk(seed: int, n: int = 400, drift: float = 0.0004, vol: float = 0.01) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return 100 * np.exp(np.cumsum(rng.normal(drift, vol, n)))


def universe(count: int = 12, n: int = 400) -> dict[str, pd.DataFrame]:
    return {f"S{i:02d}": frame(walk(i, n)) for i in range(count)}


def kesitsel_card(**overrides) -> dict:
    block = {"kip": "kesitsel", "dengeleme": {"tip": "gun", "her": 5}, "skor": "-roc5", "n": 3}
    block.update(overrides)
    return {"gostergeler": {"roc5": {"f": "roc", "src": "close", "n": 5}, "sma50": {"f": "sma", "src": "close", "n": 50}}, "rotasyon": block}


def gecis_card() -> dict:
    return {
        "gostergeler": {
            "aaa_close": {"f": "close", "varlik": "AAA"},
            "aaa_sma5": {"f": "sma", "src": "close", "n": 5, "varlik": "AAA"},
            "aaa_rsi3": {"f": "rsi", "src": "close", "n": 3, "varlik": "AAA"},
            "bbb_rsi3": {"f": "rsi", "src": "close", "n": 3, "varlik": "BBB"},
            "ccc_rsi3": {"f": "rsi", "src": "close", "n": 3, "varlik": "CCC"},
        },
        "rotasyon": {
            "kip": "gecis", "dengeleme": {"tip": "gun"},
            "agac": {
                "eger": "aaa_close > aaa_sma5",
                "ise": {"eger": "aaa_rsi3 > 80", "ise": {"tut": "BBB"}, "degilse": {"tut": "AAA"}},
                "degilse": {"sec": {"adaylar": ["BBB", "CCC"], "skor": "{v}_rsi3", "yon": "yuksek", "n": 1}},
            },
        },
    }


def gecis_frames() -> dict[str, pd.DataFrame]:
    return {"AAA": frame(walk(1, 300, 0.001, 0.02)), "BBB": frame(walk(2, 300)), "CCC": frame(walk(3, 300))}


# ------------------------------------------------------------------------------------------ kesitsel
def test_kesitsel_holds_the_lowest_recent_returns_equal_weight() -> None:
    frames = universe()
    weights = rotasyon.agirliklar(kesitsel_card(), frames)
    decided = weights[weights.attrs["karar"]]
    date = decided.index[60]
    roc = pd.Series({s: f["close"].pct_change(5).at[date] for s, f in frames.items()})
    expected = set(roc.nsmallest(3).index)
    held = set(weights.columns[weights.loc[date] > 0])
    assert held == expected
    assert weights.loc[date].sum() == pytest.approx(1.0)
    assert np.allclose(weights.loc[date][weights.loc[date] > 0], 1 / 3)


def test_kesitsel_filter_and_regime_gate() -> None:
    frames = universe()
    card = kesitsel_card(filtre="close > sma50")
    weights = rotasyon.agirliklar(card, frames)
    date = weights.index[weights.attrs["karar"].to_numpy()][70]
    for symbol in weights.columns[weights.loc[date] > 0]:
        assert frames[symbol]["close"].at[date] > frames[symbol]["close"].rolling(50).mean().at[date]
    closed = rotasyon.agirliklar(kesitsel_card(filtre="close > sma50 * 100"), frames)
    assert closed.to_numpy().sum() == 0.0  # nothing passes the filter: all cash


def test_kesitsel_rebalance_calendars() -> None:
    frames = universe(10)
    weekly = rotasyon.agirliklar(kesitsel_card(dengeleme={"tip": "hafta"}), frames)
    days = weekly.index[weekly.attrs["karar"].to_numpy()][:-1]  # the last, partial week also counts as a decision bar
    assert (days.dayofweek == 4).all()  # business-day calendar: Friday closes each week
    monthly = rotasyon.agirliklar(kesitsel_card(dengeleme={"tip": "ay"}), frames)
    month_days = monthly.index[monthly.attrs["karar"].to_numpy()]
    assert len(month_days) == len(set(zip(month_days.year, month_days.month)))


def test_n_oran_scales_with_universe() -> None:
    block = {"n_oran": 0.1, "n_min": 3}
    assert rotasyon._count(block, 25) == 3  # noqa: SLF001
    assert rotasyon._count({"n_oran": 0.1, "n_min": 1}, 100) == 10  # noqa: SLF001


def test_small_universe_is_unverifiable() -> None:
    with pytest.raises(rotasyon.RotasyonVeriYok):
        rotasyon.agirliklar(kesitsel_card(), universe(5))


def test_sirali_giris_slots_ranking_and_exit() -> None:
    frames = universe(12)
    card = {
        "gostergeler": {"rsi2": {"f": "rsi", "src": "close", "n": 2}, "vol20": {"f": "stdev", "src": "close", "n": 20}},
        "rotasyon": {"kip": "sirali_giris", "dengeleme": {"tip": "gun"}, "giris": "rsi2 < 30", "cikis": "rsi2 > 60", "skor": "vol20", "max_pozisyon": 2},
    }
    weights = rotasyon.agirliklar(card, frames)
    assert (weights.gt(0).sum(axis=1) <= 2).all()
    assert weights.gt(0).sum(axis=1).max() == 2
    assert set(weights.to_numpy().ravel()) <= {0.0, 0.5}
    rsi = {s: _rsi(f["close"], 2) for s, f in frames.items()}
    held_before: set[str] = set()
    for date in weights.index[30:200]:
        held = set(weights.columns[weights.loc[date] > 0])
        for symbol in held_before - held:
            assert rsi[symbol].at[date] > 60  # a position only leaves through the exit rule
        for symbol in held - held_before:
            assert rsi[symbol].at[date] < 30
        held_before = held


def _rsi(close: pd.Series, n: int) -> pd.Series:
    from engine import gosterge

    return gosterge.compute(pd.DataFrame({"close": close}), {"f": "rsi", "src": "close", "n": n})


# ------------------------------------------------------------------------------------------ gecis
def test_gecis_tree_follows_the_branches() -> None:
    frames = gecis_frames()
    card = gecis_card()
    weights = rotasyon.agirliklar(card, frames)
    close, sma = frames["AAA"]["close"], frames["AAA"]["close"].rolling(5).mean()
    rsi = {s: _rsi(frames[s]["close"], 3) for s in frames}
    seen = set()
    for date in weights.index[10:]:
        row = weights.loc[date]
        if close.at[date] > sma.at[date]:
            expected = "BBB" if rsi["AAA"].at[date] > 80 else "AAA"
        else:
            expected = "BBB" if rsi["BBB"].at[date] >= rsi["CCC"].at[date] else "CCC"
        assert row[expected] == pytest.approx(1.0), date
        assert row.sum() == pytest.approx(1.0)
        seen.add(expected)
    assert seen == {"AAA", "BBB", "CCC"}  # every branch was exercised


def test_gecis_warmup_is_cash() -> None:
    weights = rotasyon.agirliklar(gecis_card(), gecis_frames())
    assert weights.iloc[:3].to_numpy().sum() == 0.0


def test_gecis_equal_and_inverse_vol_nodes() -> None:
    frames = gecis_frames()
    card = gecis_card()
    card["rotasyon"]["agac"] = {"esit": [{"tut": "AAA"}, {"ters_vol": {"pencere": 10, "varliklar": ["BBB", "CCC"]}}]}
    weights = rotasyon.agirliklar(card, frames)
    row = weights.iloc[-1]
    assert row["AAA"] == pytest.approx(0.5)
    returns = {s: frames[s]["close"].pct_change().rolling(10).std(ddof=1).iloc[-1] for s in ("BBB", "CCC")}
    inverse = {s: 1 / v for s, v in returns.items()}
    for symbol in ("BBB", "CCC"):
        assert row[symbol] == pytest.approx(0.5 * inverse[symbol] / sum(inverse.values()))


def test_gecis_needs_data_from_the_start() -> None:
    frames = gecis_frames()
    frames["CCC"] = frame(walk(9, 100), start="2019-10-01")
    with pytest.raises(rotasyon.RotasyonVeriYok) as caught:
        rotasyon.kos(gecis_card(), frames, start=START, end=pd.Timestamp("2020-01-31", tz="UTC"), cost_rate=0.001)
    assert caught.value.symbols == ["CCC"]


# ------------------------------------------------------------------------------------------ simulation
def test_fill_at_next_open_with_cost() -> None:
    close = np.array([100.0, 100, 100, 110, 121, 121, 121, 121])
    one = frame(close, "2019-01-01")
    one["open"] = [100.0, 100, 100, 105, 115, 121, 121, 121]
    weights = pd.DataFrame({"X": [0, 0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]}, index=one.index)
    weights.attrs["karar"] = pd.Series(True, index=one.index)
    result = rotasyon.simule({"X": one}, weights, start=one.index[0], end=one.index[-1], cost_rate=0.01, initial_capital=1000.0)
    # decided on bar 2's close -> buys at bar 3's open (105); the flat decision of bar 5 sells at bar 6's open (121)
    assert len(result.trades) == 1
    trade = result.trades.iloc[0]
    assert trade["entry_date"] == one.index[3] and trade["entry_price"] == 105.0
    assert trade["exit_date"] == one.index[6] and trade["exit_price"] == 121.0
    fee = 0.01
    quantity = 1000.0 / (105.0 * (1 + fee))  # the buy fee is paid out of the same 1000
    assert quantity * 105.0 * (1 + fee) == pytest.approx(1000.0, rel=1e-3)
    assert trade["net_pnl"] == pytest.approx(quantity * 121.0 * (1 - fee) - 1000.0, rel=1e-3)
    assert result.equity.iloc[-1] == pytest.approx(1000.0 + trade["net_pnl"], rel=1e-9)
    assert result.equity.iloc[2] == 1000.0  # nothing held before the fill


def test_cost_reduces_equity_and_scales_with_rate() -> None:
    frames = universe(12)
    weights = rotasyon.agirliklar(kesitsel_card(), frames)
    end = pd.Timestamp("2020-06-30", tz="UTC")
    cheap = rotasyon.simule(frames, weights, start=START, end=end, cost_rate=0.0005)
    dear = rotasyon.simule(frames, weights, start=START, end=end, cost_rate=0.0015)
    free = rotasyon.simule(frames, weights, start=START, end=end, cost_rate=0.0)
    assert free.equity.iloc[-1] > cheap.equity.iloc[-1] > dear.equity.iloc[-1]
    assert (cheap.exposure <= 1.0 + 1e-9).all()  # no leverage
    assert cheap.max_open_positions <= 3


def test_buy_and_hold_matches_the_asset() -> None:
    one = frame(walk(5, 200))
    weights = pd.DataFrame({"X": 1.0}, index=one.index)
    weights.attrs["karar"] = pd.Series(True, index=one.index)
    result = rotasyon.simule({"X": one}, weights, start=one.index[0], end=one.index[-1], cost_rate=0.0)
    # fills at bar 1's open, marks at closes
    expected = one["close"].iloc[-1] / one["open"].iloc[1]
    assert result.equity.iloc[-1] / 100_000.0 == pytest.approx(expected)


# ------------------------------------------------------------------------------------------ look-ahead
@pytest.mark.parametrize("name", ["kesitsel", "gecis", "sirali"])
def test_truncating_the_series_leaves_earlier_weights_unchanged(name: str) -> None:
    if name == "gecis":
        card, frames = gecis_card(), gecis_frames()
    elif name == "kesitsel":
        card, frames = kesitsel_card(filtre="close > sma50"), universe(12)
    else:
        card = {
            "gostergeler": {"rsi2": {"f": "rsi", "src": "close", "n": 2}, "vol20": {"f": "stdev", "src": "close", "n": 20}},
            "rotasyon": {"kip": "sirali_giris", "dengeleme": {"tip": "gun"}, "giris": "rsi2 < 30", "cikis": "rsi2 > 60", "skor": "vol20", "max_pozisyon": 3},
        }
        frames = universe(12)
    full = rotasyon.agirliklar(card, frames)
    cut = full.index[220]
    short = rotasyon.agirliklar(card, {s: f.loc[:cut] for s, f in frames.items()})
    pd.testing.assert_frame_equal(full.loc[:cut], short, check_freq=False, check_dtype=False)
    a = rotasyon.simule(frames, full, start=START, end=cut, cost_rate=0.001)
    b = rotasyon.simule({s: f.loc[:cut] for s, f in frames.items()}, short, start=START, end=cut, cost_rate=0.001)
    pd.testing.assert_series_equal(a.equity, b.equity)


# ------------------------------------------------------------------------------------------ schema
def card_for_spec(**block) -> dict:
    card = gecis_card()
    card.update({"id": "T", "ad": "x", "kaynak": {}, "tarz": "swing", "tf": "1D", "mtf": None, "giris": None, "cikis": None,
                 "spec_durumu": "tam", "belirsiz": [], "ozel_kod": False})
    card["rotasyon"].update(block)
    return card


def test_spec_accepts_a_valid_rotation_card_and_flags_bad_ones() -> None:
    assert not validate_card(Path("T.yaml"), card_for_spec(), {"T"}).errors
    bad = validate_card(Path("T.yaml"), card_for_spec(kip="belirsiz"), {"T"})
    assert any(i.kod == "rotasyon" for i in bad.errors)
    undefined = card_for_spec(agac={"eger": "yok_ad > 1", "ise": {"tut": "AAA"}, "degilse": {"tut": "nakit"}})
    assert any(i.kod == "tanimsiz_ad" for i in validate_card(Path("T.yaml"), undefined, {"T"}).errors)
    malformed = card_for_spec(agac={"eger": "aaa_close > 1", "ise": {"tut": "AAA"}})
    assert any(i.kod == "rotasyon" for i in validate_card(Path("T.yaml"), malformed, {"T"}).errors)


def test_entry_filter_applies_only_to_new_names() -> None:
    frames = universe(12)
    card = kesitsel_card(skor="roc5", giris_filtre="rsi3 < 50")
    card["gostergeler"]["rsi3"] = {"f": "rsi", "src": "close", "n": 3}
    weights = rotasyon.agirliklar(card, frames)
    rsi = {s: _rsi(f["close"], 3) for s, f in frames.items()}
    roc = pd.DataFrame({s: f["close"].pct_change(5) for s, f in frames.items()})
    days = weights.index[weights.attrs["karar"].to_numpy()][12:80]
    held_before: set[str] = set()
    for date in days:
        held = set(weights.columns[weights.loc[date] > 0])
        top = set(roc.loc[date].nlargest(3).index)
        assert held <= top  # nothing outside the ranking
        for symbol in held - held_before:
            assert rsi[symbol].at[date] < 50  # a new name needs the entry filter
        for symbol in (held_before & top):
            assert symbol in held  # a held name that is still ranked stays, whatever its RSI
        held_before = held
    assert any(weights.loc[d].sum() < 1.0 - 1e-9 for d in days)  # filtered slots stay in cash (1/N each, no rescale)


# ------------------------------------------------------------------------------------------ repository cards
SPEC_DIR = Path(__file__).resolve().parents[1] / "docs" / "spec"


def repository_rotation_cards() -> dict[str, dict]:
    import yaml

    cards = {}
    for path in sorted(SPEC_DIR.glob("*.yaml")):
        card = yaml.safe_load(path.read_text(encoding="utf-8"))
        if card.get("rotasyon"):
            cards[card["id"]] = card
    return cards


def test_repository_rotation_cards_validate() -> None:
    from engine.spec import validate_directory

    cards = repository_rotation_cards()
    assert len(cards) >= 13
    results = {r.card["id"]: r for r in validate_directory(SPEC_DIR) if r.card.get("id") in cards}
    for card_id, card in cards.items():
        assert not rotasyon.dogrula(card), card_id
        assert not results[card_id].errors, (card_id, results[card_id].errors)
        assert card["ozel_kod"] is False and card["spec_durumu"] == "tam"
        if card["rotasyon"]["kip"] == "gecis":
            assert card["piyasa_kisiti"] == ["ABD"] and card.get("dolum") == "kapanis"


def test_gecis_cards_run_on_synthetic_instruments() -> None:
    cards = repository_rotation_cards()
    for card_id in ("A4-003", "A4-005", "O2-025", "M017"):
        card = cards[card_id]
        frames = {s: frame(walk(i, 700, 0.0004, 0.02), start="2017-01-02") for i, s in enumerate(rotasyon.needed_symbols(card))}
        weights = rotasyon.agirliklar(card, frames)
        assert set(weights.columns) == set(rotasyon.tree_assets(card["rotasyon"]["agac"]))
        assert (weights.sum(axis=1) <= 1.0 + 1e-9).all(), card_id
        assert weights.sum(axis=1).max() > 0.0, card_id
        result = rotasyon.kos(card, frames, start=pd.Timestamp("2017-06-01", tz="UTC"), end=weights.index[-1], cost_rate=0.0005, fill_at_close=True)
        assert (result.exposure <= 1.0 + 1e-9).all()


# ------------------------------------------------------------------------------------------ tarama integration
def test_scan_runs_rotation_cards_and_reports_unverifiable_ones(tmp_path: Path) -> None:
    from backtests import tarama
    from backtests.run_codex21 import _filename

    cards = repository_rotation_cards()
    chosen = [cards[i] for i in ("A4-003", "O2-028", "B3-014", "M020a", "A6-004")]
    daily = tmp_path / "data" / "daily"
    daily.mkdir(parents=True)
    universe = pd.read_csv(Path(tarama.ROOT) / "data" / "evren.csv", dtype=str).fillna("")
    symbols = {row.sembol: n for n, row in universe.iterrows()}
    for symbol in rotasyon.needed_symbols(cards["A4-003"]) + ["BTCUSDT"]:
        symbols.setdefault(symbol, len(symbols))
    for symbol, number in symbols.items():
        data = frame(walk(number, 2400, 0.0004, 0.015), start="2014-06-02")
        data.index.name = "timestamp"
        data.to_parquet(daily / _filename(symbol))
    table = tarama.scan(chosen, daily, tmp_path / "results", data_root=tmp_path / "data")
    rows = table.set_index(["id", "piyasa"])
    assert (table["durum"] != "Hata").all(), table[table["durum"] == "Hata"][["id", "piyasa", "neden"]]
    swing = rows.loc[("A4-003", "ABD25")]
    assert swing["durum"] == "Hesaplandi" and swing["dolum"] == "kapanis" and pd.notna(swing["PF_1x_b"])
    assert rows.loc[("A4-003", "BIST30"), "neden"] == "piyasa_ozgu:ABD"
    assert rows.loc[("O2-028", "ABD25"), "durum"] == "Dogrulanamaz"  # files of the late instruments are missing
    assert rows.loc[("O2-028", "ABD25"), "neden"].startswith("veri_yok")
    assert rows.loc[("B3-014", "BIST30"), "durum"] == "Hesaplandi"
    assert rows.loc[("B3-014", "EMTIA"), "neden"].startswith("evren_kucuk")
    assert rows.loc[("M020a", "BIST30"), "neden"] == "endeks_yok:BIST30"
    assert rows.loc[("M020a", "ABD25"), "durum"] == "Hesaplandi"
    assert rows.loc[("A6-004", "KRIPTO25"), "durum"] == "Hesaplandi"
    assert (tmp_path / "results" / "tarama.csv").exists()
    from backtests.rotasyon_asama2 import RotationPrepared

    assert isinstance(tarama.prepare(cards["B3-014"], {f"S{i}": frame(walk(i, 400)) for i in range(9)}, "ABD25"), RotationPrepared)


def test_return_statistics_indicators() -> None:
    from engine import gosterge

    data = pd.DataFrame({"close": [100.0, 101.0, 99.0, 102.0, 103.0]})
    returns = np.array([1.0, (99 / 101 - 1) * 100, (102 / 99 - 1) * 100, (103 / 102 - 1) * 100])
    assert np.isnan(gosterge.getiri_ort(data, n=3).iloc[2])
    assert gosterge.getiri_ort(data, n=3).iloc[3] == pytest.approx(returns[0:3].mean())
    assert gosterge.getiri_std(data, n=3).iloc[4] == pytest.approx(np.std(returns[1:4], ddof=1))
    full = pd.DataFrame({"close": walk(4, 60)})
    cut = gosterge.getiri_std(full.iloc[:40], n=10)
    pd.testing.assert_series_equal(cut, gosterge.getiri_std(full, n=10).iloc[:40])  # no look-ahead
