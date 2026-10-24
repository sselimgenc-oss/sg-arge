"""U4-H1..H4 kartlari (docs/GOREV_U4.md bolum 4): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine import gosterge
from engine.kart_sinyal import build_plan, card_frame_signals
from engine.spec import validate_card

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
IDS = ["U4-H1", "U4-H2", "U4-H3", "U4-H4"]


def load(card_id: str) -> dict:
    return yaml.safe_load((SPEC / f"{card_id}.yaml").read_text(encoding="utf-8"))


def signals(card_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    out, _ = card_frame_signals(load(card_id), frame, week_end="SUN")
    return out


def frame_from(close, high=None, low=None, open_=None) -> pd.DataFrame:
    close = np.asarray(close, dtype=float)
    open_ = np.r_[close[0], close[:-1]] if open_ is None else np.asarray(open_, dtype=float)
    high = np.maximum(open_, close) if high is None else np.asarray(high, dtype=float)
    low = np.minimum(open_, close) if low is None else np.asarray(low, dtype=float)
    index = pd.date_range("2020-01-01", periods=len(close), freq="1D", tz="UTC")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1.0}, index=index)


def walk(bars: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, bars)))
    open_ = np.r_[close[0], close[:-1]]
    spread = rng.uniform(0.001, 0.02, bars)
    return frame_from(close, high=np.maximum(open_, close) * (1 + spread), low=np.minimum(open_, close) * (1 - spread), open_=open_)


# ------------------------------------------------------------------------------------------------ sema
@pytest.mark.parametrize("card_id", IDS)
def test_kart_semasi_ve_on_kayit_alanlari(card_id):
    card = load(card_id)
    result = validate_card(SPEC / f"{card_id}.yaml", card, set(IDS))
    assert result.errors == []
    assert card["spec_durumu"] == "tam" and card["ozel_kod"] is False
    assert card["piyasa_kisiti"] == ["KRIPTO", "ABD", "EMTIA"]
    assert card["deneme_sayisi_kaynakta"] == 4
    u1 = yaml.safe_load((SPEC / "U1-H2-A.yaml").read_text(encoding="utf-8"))
    assert card["cekirdek"] == u1["cekirdek"] and card["kardesler"] == u1["kardesler"]
    assert card["belirsiz"] and not card.get("izgara")


def test_kurallar_on_kayitla_birebir():
    h1, h2, h3, h4 = (load(c) for c in IDS)
    assert h1["giris"] == "close > sma100 and close > close[100]" and h1["cikis"] == "close < sma100"
    assert h1["gostergeler"]["sma100"] == {"f": "sma", "src": "close", "n": 100}
    assert h2["giris"] == "close > yuksek55" and h2["cikis"] == "close < dusuk20"
    assert h2["gostergeler"]["yuksek55"] == {"f": "highest", "src": "high", "n": 55, "kaydir": 1}
    assert h2["gostergeler"]["dusuk20"] == {"f": "lowest", "src": "low", "n": 20, "kaydir": 1}
    assert h2["stop"] == {"tip": "atr", "n": 20, "carpan": 2}
    assert h3["giris"] == "ema20 > ema50 and close > sma200 and atr14 / atr100 < 1" and h3["cikis"] == "ema20 < ema50"
    assert (h3["gostergeler"]["atr14"]["n"], h3["gostergeler"]["atr100"]["n"]) == (14, 100)
    assert h4["giris"] == "close > sma200 and rsi2 < 10" and h4["cikis"] == "close > sma5"
    assert h4["gostergeler"]["rsi2"] == {"f": "rsi", "src": "close", "n": 2}
    assert h4["zaman_stop"] == {"bar": 10}
    for card in (h1, h3, h4):
        assert card["stop"] == {"tip": "atr", "n": 14, "carpan": 3}
    for card in (h1, h2, h3, h4):
        assert card["hedef"] is None and card.get("iz_suren") is None


def test_motor_planinda_stop_ve_zaman_stopu():
    frame = walk(300, 1)
    for card_id in IDS:
        card = load(card_id)
        plan = build_plan(card, {"X": frame}, week_end="SUN", market="KRIPTO25")
        n, mult = card["stop"]["n"], card["stop"]["carpan"]
        pd.testing.assert_series_equal(plan.signals["X"]["stop_dist"], mult * gosterge.atr(frame, n), check_names=False)
        assert not plan.stop_eklendi
        assert plan.engine_kwargs.get("time_stop_bars") == (10 if card_id == "U4-H4" else None)


# ----------------------------------------------------------------------------------- ileriye bakma yok
@pytest.mark.parametrize("card_id", IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(card_id, seed):
    frame = walk(700, seed)
    full = signals(card_id, frame)
    rng = np.random.default_rng(seed + 100)
    for t in (260, 400, 555):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.15, len(frame) - (t + 1)).cumsum())  # t+1 ve sonrasi tamamen farkli
        for column in ("open", "high", "low", "close"):
            altered.iloc[t + 1:, altered.columns.get_loc(column)] = frame[column].iloc[t + 1:].to_numpy() * shock
        again = signals(card_id, altered)
        pd.testing.assert_frame_equal(full.iloc[: t + 1], again.iloc[: t + 1], check_exact=False, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("card_id", IDS)
def test_ornek_seri_sinyal_uretir(card_id):
    """Ileriye bakma testi bos sinyallerle gecmesin: sentetik seride giris ve cikis en az bir kez dogru olmali."""
    sig = signals(card_id, walk(1500, 7))
    assert sig["entry"].sum() > 0 and sig["exit"].sum() > 0


# ----------------------------------------------------------------------------- elle hesaplanmis ornekler
def test_h1_elle_ornek():
    # bar 0-99 kapanis 10; bar 100 kapanis 12; bar 101 kapanis 8.
    sig = signals("U4-H1", frame_from([10.0] * 100 + [12.0, 8.0]))
    assert not sig["entry"].iloc[:100].any()          # bar 99: sma100 = 10, 10 > 10 degil
    # bar 100: sma100 = (99*10 + 12)/100 = 10.02; close[100] = close[0] = 10 -> 12 > 10.02 ve 12 > 10
    assert sig["entry"].iloc[100] and not sig["exit"].iloc[100]
    # bar 101: sma100 = (98*10 + 12 + 8)/100 = 10.0 -> 8 < 10: cikis, giris yok
    assert sig["exit"].iloc[101] and not sig["entry"].iloc[101]


def test_h1_getiri_kosulu_tek_basina_engeller():
    # bar 0 kapanis 20, sonra 10'da yatay, bar 100 kapanis 11
    sig = signals("U4-H1", frame_from([20.0] + [10.0] * 99 + [11.0]))
    # bar 100: sma100 = (99*10 + 11)/100 = 10.01 < 11 (trend tamam) ama close[100] = close[0] = 20 > 11
    assert not sig["entry"].iloc[100]


def test_h2_elle_ornek():
    close = [10.0] * 100 + [11.0, 9.0]
    high = [10.5] * 100 + [11.2, 9.5]
    low = [9.5] * 100 + [10.0, 9.0]
    sig = signals("U4-H2", frame_from(close, high=high, low=low, open_=[10.0] * 100 + [10.0, 11.0]))
    # bar 100: onceki 55 barin en yuksek high'i 10.5 -> 11 > 10.5 giris
    assert sig["entry"].iloc[100] and not sig["entry"].iloc[99]
    # bar 101: onceki 20 barin (81..100) en dusuk low'u 9.5 -> 9 < 9.5 cikis; mevcut bar pencerede degil
    assert sig["exit"].iloc[101] and not sig["exit"].iloc[100]
    # stop = ATR(20) x 2: yatay barlarda TR = high - low = 1, ATR20 = 1 -> stop_dist 2
    assert sig["stop_dist"].iloc[99] == pytest.approx(2.0)


def test_h2_esitlik_kirilim_degil():
    sig = signals("U4-H2", frame_from([10.0] * 100 + [10.5], high=[10.5] * 100 + [10.6], low=[9.5] * 101))
    assert not sig["entry"].iloc[100]                 # 10.5 > 10.5 degil


def test_h3_elle_ornek():
    # 300 bar adim 1; open = onceki kapanis, high = close, low = open -> TR = 1, ATR14 = ATR100 = 1, oran tam 1 (< 1 degil)
    close = 100.0 + np.arange(300)
    close = np.r_[close, close[-1] + 0.5 * np.arange(1, 6)]    # 5 bar adim 0.5 (TR = 0.5)
    close = np.r_[close, close[-1] - 3.0 * np.arange(1, 61)]   # 60 bar adim -3
    open_ = np.r_[close[0] - 1.0, close[:-1]]
    sig = signals("U4-H3", frame_from(close, high=np.maximum(open_, close), low=np.minimum(open_, close), open_=open_))
    assert not sig["entry"].iloc[250:300].any()       # oran tam 1: sinirda kosul saglanmaz
    # bar 300: ATR14 = (13*1 + 0.5)/14 = 0.9643; ATR100 = (99*1 + 0.5)/100 = 0.995 -> oran 0.969 < 1; EMA20 > EMA50; close > SMA200
    assert sig["entry"].iloc[300]
    assert not sig["exit"].iloc[250:305].any()        # yukselirken EMA20 > EMA50
    assert sig["exit"].iloc[-1]                       # 60 bar -3 dususten sonra EMA20 < EMA50


def test_h4_elle_ornek():
    # 250 bar yavas yukselis (adim 0.1; RSI(2) = 100), bar 250 -3 dusus, bar 251 toparlanma
    close = 100.0 + 0.1 * np.arange(250)
    close = np.r_[close, close[-1] - 3.0, 125.0]      # 124.9 -> 121.9 -> 125.0
    sig = signals("U4-H4", frame_from(close))
    assert not sig["entry"].iloc[205:250].any()       # RSI(2) = 100
    # bar 250 (Wilder n=2, alfa 0.5): ort. dusus = (0 + 3)/2 = 1.5, ort. yukselis = 0.1/2 = 0.05
    # RSI = 100 - 100/(1 + 0.05/1.5) = 3.23 < 10; close 121.9 > SMA200 (~115)
    assert sig["entry"].iloc[250] and not sig["exit"].iloc[250]   # 121.9 < SMA5 = 124.2
    # bar 251: SMA5 = (124.7 + 124.8 + 124.9 + 121.9 + 125.0)/5 = 124.26 < 125.0 -> cikis
    assert sig["exit"].iloc[251]


def test_h4_trend_filtresi():
    close = 200.0 - 0.1 * np.arange(300)              # asagi trend: close < SMA200
    close[-1] -= 3.0
    assert not signals("U4-H4", frame_from(close))["entry"].any()
