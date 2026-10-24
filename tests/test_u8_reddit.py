"""U8 Reddit kartlari RD-01..RD-04 (arastirma/reddit/ozet.md bolum A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine import rotasyon
from engine.kart_sinyal import card_frame_signals
from engine.spec import validate_card
from strategies.ozel import build_plan as ozel_plan, has_strategy

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
IDS = ["RD-01", "RD-02", "RD-03", "RD-04"]


def load(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


def walk(bars: int, seed: int, freq: str = "1D", sigma: float = 0.01) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0004, sigma, bars)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, bars))
    spread = rng.uniform(0.0, 0.006, bars)
    index = pd.bdate_range("2015-01-01", periods=bars, tz="UTC") if freq == "1D" else pd.date_range("2015-01-01", periods=bars, freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * (1 + spread), "low": np.minimum(open_, close) * (1 - spread),
                         "close": close, "volume": rng.uniform(100, 1000, bars)}, index=index)


def frame_of(close, high=None, low=None, open_=None, freq="1D") -> pd.DataFrame:
    close = np.asarray(close, dtype=float)
    index = pd.bdate_range("2020-01-01", periods=len(close), tz="UTC") if freq == "1D" else pd.date_range("2020-01-01", periods=len(close), freq=freq, tz="UTC")
    return pd.DataFrame({"open": close if open_ is None else open_, "high": close if high is None else high,
                         "low": close if low is None else low, "close": close, "volume": 1.0}, index=index)


@pytest.mark.parametrize("card_id", IDS)
def test_kart_semasi(card_id):
    card = load(card_id)
    assert validate_card(SPEC / f"{card_id}.yaml", card, set()).errors == []
    assert card["id"] == card_id and card["spec_durumu"] == "tam" and card["piyasa_kisiti"] == ["ABD"]
    assert card["belirsiz"] and all(v is None for k, v in card["rapor"].items() if k != "maliyet_dahil")  # yazar rakami yok
    assert card["kol"] in ("ABD-1D", "ABD-4H") or card_id == "RD-03"
    if card["ozel_kod"]:
        assert card["ozel_kod_nedeni"] and has_strategy(card_id)


def test_kart_kolari_ve_alanlari():
    assert load("RD-01")["semboller"] == ["SPY", "QQQ"] and load("RD-01")["tf"] == "1D"
    assert load("RD-02")["dolum"] == "kapanis" and load("RD-02")["olcut_sembolleri"] == ["TLT"] and load("RD-02")["stop_eklendi"] is True
    assert load("RD-04")["tf"] == "4H" and load("RD-04")["kol"] == "ABD-4H" and load("RD-04")["stop"] == {"tip": "yuzde", "deger": 3.0}
    gtaa = load("RD-03")
    assert gtaa["rotasyon"]["kip"] == "gecis" and gtaa["rotasyon"]["dengeleme"] == {"tip": "ay"}
    assert sorted(rotasyon.needed_symbols(gtaa)) == ["DBC", "EFA", "IEF", "SPY", "VNQ"]


# ------------------------------------------------------------------------------------------------ ileriye bakma
def _shocked(frame: pd.DataFrame, cut: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    altered = frame.copy()
    shock = np.exp(rng.normal(0, 0.1, len(frame) - (cut + 1)).cumsum())
    for column in ("open", "high", "low", "close"):
        altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
    return altered


def _rd01(frame):
    return ozel_plan(load("RD-01"), {"X": frame}).signals["X"]


def _rd04(frame):
    return card_frame_signals(load("RD-04"), frame, week_end="FRI")[0]


@pytest.mark.parametrize("seed", [1, 2, 3])
@pytest.mark.parametrize("name,fn,freq", [("RD-01", _rd01, "1D"), ("RD-04", _rd04, "4h")])
def test_ileriye_bakma_yok(name, fn, freq, seed):
    frame = walk(1500, seed, freq)
    full = fn(frame)
    for cut in (500, 900, 1300):
        again = fn(_shocked(frame, cut, seed + 7))
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("name,fn,freq", [("RD-01", _rd01, "1D"), ("RD-04", _rd04, "4h")])
def test_sinyal_uretir(name, fn, freq):
    total = sum(int(fn(walk(4000, s, freq, sigma=0.012 if freq == "1D" else 0.006))["entry"].sum()) for s in (4, 5, 6))
    assert total > 0


def test_rd02_ileriye_bakma_yok():
    spy, tlt = walk(1200, 1), walk(1200, 2, sigma=0.008)
    card = load("RD-02")
    run = lambda s, t: ozel_plan(card, {"SPY": s, "TLT": t}).signals["SPY"]  # noqa: E731
    full = run(spy, tlt)
    assert int(full["entry"].sum()) > 0
    for cut in (400, 700, 1000):
        again = run(_shocked(spy, cut, 5), _shocked(tlt, cut, 6))
        # ay sonu cikislari kesimden sonraki gunlere isaret eder (planlanan takvim); kesime kadar olan giris/cikis ayni olmali
        # (kesimin ayni ay icinde kalan gelecek takvim gunleri ayni kalir; deger kosullari yalniz gecmis veriden gelir)
        pd.testing.assert_series_equal(full["entry"].iloc[: cut - 30], again["entry"].iloc[: cut - 30])


# ------------------------------------------------------------------------------------------------ RD-04 elle
def test_rd04_williams_r_elle():
    """30 bar dar aralik (100-110): en yuksek 110, en dusuk 100. Kapanis 100,5 -> %R = -100 x (110 - 100,5) / 10 = -95 (< -90): giris.
    Sonra kapanis 104 -> %R = -60 (esik -50 altinda, cikis degil); kapanis 106 -> %R = -40 (> -50): cikis."""
    n = 40
    close = np.full(n, 105.0)
    high = np.full(n, 110.0)
    low = np.full(n, 100.0)
    close[35], close[36], close[37] = 100.5, 104.0, 106.0
    sig = _rd04(frame_of(close, high=high, low=low, freq="4h"))
    assert sig["entry"].iloc[35] and not sig["entry"].iloc[36] and not sig["entry"].iloc[37]  # 36'da %R = -60: giris esigi degil
    assert not sig["exit"].iloc[35] and not sig["exit"].iloc[36] and sig["exit"].iloc[37]


# ------------------------------------------------------------------------------------------------ RD-01 elle
def _dip_frame():
    """Yukari egimli seri (kapanis > SMA200); 250. barda kapanis = dusuk (IBS = 0) ve kapanis < SMA(5): giris.
    251. bar kapanisi SMA(5) uzerinde: cikis sinyali."""
    n = 270
    close = 100 + 0.1 * np.arange(n)
    open_ = np.r_[close[0], close[:-1]]
    high, low = close + 0.05, close - 0.05
    close[250] = 124.3
    low[250], high[250] = 124.3, 125.3
    open_[251] = 124.5
    close[251], high[251], low[251] = 126.0, 126.1, 124.4
    return frame_of(close, high=high, low=low, open_=open_)


def test_rd01_dip_alim_ve_sma5_cikis_elle():
    frame = _dip_frame()
    sig = _rd01(frame)
    assert sig["entry"].tolist().index(True) == 250 and int(sig["entry"].sum()) == 1
    ibs = (frame["close"].iloc[250] - frame["low"].iloc[250]) / (frame["high"].iloc[250] - frame["low"].iloc[250])
    assert ibs == 0.0
    sma5 = frame["close"].rolling(5).mean()
    assert frame["close"].iloc[250] < sma5.iloc[250] and frame["close"].iloc[251] > sma5.iloc[251]
    assert sig["exit"].iloc[251] and int(sig["exit"].sum()) == 1


def test_rd01_stop_sonrasi_kilit_elle():
    """Dolum 251'de acilis 124,5; dusuk 114 < 0,92 x 124,5 = 114,54: stop. Stop sonrasi, kapanis > SMA(5) olmadan yeni dip sinyali verilmez."""
    frame = _dip_frame()
    close, low, high, open_ = (frame[c].to_numpy().copy() for c in ("close", "low", "high", "open"))
    low[251], close[251], high[251] = 114.0, 115.0, 124.6
    close[252:256] = [114.0, 113.0, 112.0, 111.0]  # surekli dusus: kapanis SMA(5) altinda (3 dusen kapanis da var)
    low[252:256], high[252:256] = close[252:256] - 0.0, close[252:256] + 1.0  # IBS = 0
    open_[252:256] = np.r_[115.0, close[252:255]]
    sig = _rd01(frame_of(close, high=high, low=low, open_=open_))
    assert not sig["exit"].iloc[251]  # stop bar icinde (cikis sinyali degil)
    assert not sig["entry"].iloc[251:256].any()  # kilit
    # kilit acilir: 256'da kapanis SMA(5) ustune cikar; 257'de yeni dip sinyali artik gecerli
    close2 = close.copy()
    close2[256] = 130.0
    high2, low2, open2 = high.copy(), low.copy(), open_.copy()
    high2[256], low2[256], open2[256] = 130.5, 110.0, 111.0
    close2[257], low2[257], high2[257], open2[257] = 116.5, 116.5, 117.0, 118.0
    sig2 = _rd01(frame_of(close2, high=high2, low=low2, open_=open2))
    assert not sig2["entry"].iloc[251:257].any()
    sma200 = pd.Series(close2).rolling(200).mean()
    assert close2[257] > sma200.iloc[257]  # SMA(200) filtresi hala saglanir
    assert sig2["entry"].iloc[257]


# ------------------------------------------------------------------------------------------------ RD-02 elle
def test_rd02_gerideyse_ay_sonu_elle():
    """Mart 2021 (23 islem gunu): ayin sondan 5. gunu 2021-03-25. Subat sonu SPY = TLT = 100. 25 Mart: SPY 97 (-3%), TLT 101 (+1%):
    fark -4 puan <= -2: o kapanista al (entry 25 Mart), ayin son kapanisinda (31 Mart) sat."""
    idx = pd.bdate_range("2021-01-01", "2021-05-31", tz="UTC")
    spy = pd.Series(100.0, index=idx)
    tlt = pd.Series(100.0, index=idx)
    spy.loc["2021-03-25":] = 97.0
    tlt.loc["2021-03-25":] = 101.0
    frames = lambda s: pd.DataFrame({"open": s, "high": s, "low": s, "close": s, "volume": 1.0})  # noqa: E731
    sig = ozel_plan(load("RD-02"), {"SPY": frames(spy), "TLT": frames(tlt)}).signals["SPY"]
    entry_days = [d.strftime("%Y-%m-%d") for d in sig.index[sig["entry"]]]
    exit_days = [d.strftime("%Y-%m-%d") for d in sig.index[sig["exit"]]]
    assert "2021-03-25" in entry_days and "2021-03-31" in exit_days
    assert not [d for d in entry_days if d.startswith("2021-02") or d.startswith("2021-04")]  # fark yok: islem yok


def test_rd02_onde_ise_sonraki_ayin_3_gunu_elle():
    """Nisan 2021: sondan 5. gun = 2021-04-26 (22 islem gunu). Mart sonu SPY = TLT = 100. 26 Nisan: SPY 103 (+3%), TLT 100 (0%):
    fark +3 >= 2: ayin son kapanisinda (30 Nisan) al, Mayis'in 3. islem gunu kapanisinda (2021-05-05) sat."""
    idx = pd.bdate_range("2021-03-01", "2021-06-30", tz="UTC")
    spy = pd.Series(100.0, index=idx)
    tlt = pd.Series(100.0, index=idx)
    spy.loc["2021-04-26":"2021-04-30"] = 103.0
    frames = lambda s: pd.DataFrame({"open": s, "high": s, "low": s, "close": s, "volume": 1.0})  # noqa: E731
    sig = ozel_plan(load("RD-02"), {"SPY": frames(spy), "TLT": frames(tlt)}).signals["SPY"]
    entry_days = [d.strftime("%Y-%m-%d") for d in sig.index[sig["entry"]]]
    exit_days = [d.strftime("%Y-%m-%d") for d in sig.index[sig["exit"]]]
    assert "2021-04-30" in entry_days and "2021-04-26" not in entry_days
    assert "2021-05-05" in exit_days  # Mayis 2021 islem gunleri: 3, 4, 5 -> 3. gun 5 Mayis (1 Mayis cumartesi)


# ------------------------------------------------------------------------------------------------ RD-03 elle
def test_rd03_gtaa_agirliklari_aylik_sma_ile_ayni():
    card = load("RD-03")
    index = pd.bdate_range("2018-01-01", "2021-12-31", tz="UTC")
    rng = np.random.default_rng(3)
    frames = {}
    for asset in ["SPY", "EFA", "IEF", "DBC", "VNQ"]:
        close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0004, 0.01, len(index)))), index=index)
        frames[asset] = pd.DataFrame({"open": close, "high": close * 1.001, "low": close * 0.999, "close": close, "volume": 1.0})
    weights = rotasyon.agirliklar(card, frames)
    month_end = (index.to_series().groupby(index.tz_localize(None).to_period("M")).transform("max") == index).to_numpy()
    checked = 0
    for day in index[month_end][12:]:
        for asset, frame in frames.items():
            monthly = frame["close"].groupby(frame.index.tz_localize(None).to_period("M")).last()
            sma10 = monthly.iloc[: monthly.index.get_loc(day.tz_localize(None).to_period("M")) + 1].iloc[-10:].mean()
            expected = 0.2 if frame["close"].loc[day] > sma10 else 0.0
            assert weights.loc[day, asset] == pytest.approx(expected)
            checked += 1
    assert checked == 5 * len(index[month_end][12:])
    changed = (weights.diff().abs().sum(axis=1) > 1e-12).to_numpy()
    assert not (changed & ~month_end).any()  # agirlik yalniz ay sonu kararinda degisir
    assert weights.sum(axis=1).max() <= 1.0 + 1e-12  # nakit payi dahil toplam <= 1
