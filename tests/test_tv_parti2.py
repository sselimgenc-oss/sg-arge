"""U6 parti 2: TV-<id> kartlari (docs/GOREV_U6.md bolum 2 ve 5A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine.kart_sinyal import build_plan as dsl_plan, card_frame_signals
from engine.spec import validate_card
from strategies.ozel import build_plan as ozel_plan, has_strategy

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
PARTI_IDS = ['PDt7xwn2', 'HfxNiEab', 'ZvpONhex', 'zb7PgKWs', 'TQVitTEQ', 'ApE4pUTA', 'abjeWQD5', 'Dln4aFaM', '6ZReHYKn', '8zGpvRaM', '7S2pDMA5', 'KYB6AmC1', 'C1hyNDWO', 'Q1O23zJP', 'yMCa3XZD', 'qQ0MJCVL', 'Y9ppyIk2', '522xf0n5', 'xYflA6O7', 'vMuEblZr', '2TrSqi61', 'o9qty0BL', 'PUEDA3c6', 'zMwHN2Uu', 'ANmKXWWJ', 'adstHm9N', 'Qg1Jra51', '69ZFfJ5L', 'mpjNqADq', 'IMKs0OPw', '04erUlJM', 'Z9O5w3SG', '8YopUUSO', 'vrrutnMb', 'xDJH00mL', 'XRZCjbFr', '2wyXTTMc', '97gxVA5b', 'woRXiMlC', 'et8U6rd3', '71yKm18B', 'egTb7TgJ', '8iAYXXsS', '8GIAFRcP', '0BcdTWoV', 'VFzCk3HX', 'zrDoqm9F', 'OKxIjdsz', 'NeEiwmDq', 'VcRiudNf', 'b4HV7iJR', 'IFSv46kK']
TAM_IDS = ['PDt7xwn2', 'HfxNiEab', 'zb7PgKWs', '6ZReHYKn', 'qQ0MJCVL', 'xYflA6O7', 'vMuEblZr', 'o9qty0BL', 'PUEDA3c6', 'zMwHN2Uu', 'ANmKXWWJ', 'IMKs0OPw', 'Z9O5w3SG', 'XRZCjbFr', '97gxVA5b', 'zrDoqm9F', 'OKxIjdsz', 'VcRiudNf']
OZEL_IDS = ['xYflA6O7', 'vMuEblZr', 'o9qty0BL', 'PUEDA3c6', 'zMwHN2Uu', 'IMKs0OPw', 'Z9O5w3SG', '97gxVA5b']
SINIFLAR = ("KRIPTO", "ABD", "EMTIA")
NEDENLER = ("piyasa", "veri", "ceviri", "bekliyor:motor")


def load(script_id: str) -> dict:
    return yaml.safe_load((SPEC / f"TV-{script_id}.yaml").read_text(encoding="utf-8"))


def signals(script_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    card = load(script_id)
    if card.get("ozel_kod"):
        return ozel_plan(card, {"X": frame}).signals["X"]
    out, _ = card_frame_signals(card, frame, week_end="SUN")
    return out


def frame_from(close, high=None, low=None, open_=None, volume=None, freq: str = "1D") -> pd.DataFrame:
    close = np.asarray(close, dtype=float)
    open_ = close.copy() if open_ is None else np.asarray(open_, dtype=float)
    high = close.copy() if high is None else np.asarray(high, dtype=float)
    low = close.copy() if low is None else np.asarray(low, dtype=float)
    volume = np.full(len(close), 1.0) if volume is None else np.asarray(volume, dtype=float)
    index = pd.date_range("2020-01-01", periods=len(close), freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=index)


def walk(bars: int, seed: int, freq: str, sigma: float = 0.012) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.001, sigma, bars)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, bars))
    spread = rng.uniform(0.0, 0.01, bars)
    index = pd.date_range("2018-01-01", periods=bars, freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * (1 + spread),
                         "low": np.minimum(open_, close) * (1 - spread), "close": close,
                         "volume": rng.uniform(100, 1000, bars)}, index=index)


def freq_of(card: dict) -> str:
    return "4h" if card["tf"] == "4H" else "1D"


# ------------------------------------------------------------------------------------------------ sema
@pytest.mark.parametrize("script_id", PARTI_IDS)
def test_kart_semasi_ve_alanlari(script_id):
    card = load(script_id)
    result = validate_card(SPEC / f"TV-{script_id}.yaml", card, set())
    assert result.errors == []
    assert card["id"] == f"TV-{script_id}"
    assert card["deneme_sayisi_kaynakta"] == 205
    assert card["yalniz_long_bacak"] is True
    assert card["yayin_sembolu"] is None or ":" in card["yayin_sembolu"]
    assert card["tf"] in ("4H", "1D")
    assert isinstance(card["belirsiz"], list) and card["belirsiz"]
    assert all(value is None for key, value in card["rapor"].items() if key != "maliyet_dahil")  # yazar rakami yok
    if card["spec_durumu"] == "tam":
        assert card["piyasa_kisiti"] == [card["kol"].split("-")[0]]
        assert card["kol"].split("-")[0] in SINIFLAR
        assert card["kol"].endswith("1D") or card["kol"].startswith("KRIPTO")  # ABD/emtia 4H yok
        if card["ozel_kod"]:
            assert card["ozel_kod_nedeni"] and has_strategy(card["id"])
        else:
            assert card["stop_eklendi"] == (card["stop"] is None)
            assert card["giris"] and card["cikis"]
    else:
        assert card["spec_durumu"] == "eksik"
        assert card["dogrulanamaz"]["neden"] in NEDENLER and card["dogrulanamaz"]["ayrinti"]
        if card["dogrulanamaz"]["neden"] == "veri":
            assert card["kol"].split("-")[0] in ("ABD", "EMTIA") and card["tf"] == "4H"
        if card["dogrulanamaz"]["neden"] == "piyasa":
            assert card["kol"].split("-")[0] not in SINIFLAR


def test_tam_kart_listesi_kayitla_tutarli():
    assert sorted(i for i in PARTI_IDS if load(i)["spec_durumu"] == "tam") == sorted(TAM_IDS)
    assert sorted(i for i in TAM_IDS if load(i)["ozel_kod"]) == sorted(OZEL_IDS)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_motor_plani_kurulur(script_id):
    card = load(script_id)
    frame = walk(900, 5, freq_of(card))
    plan = ozel_plan(card, {"X": frame}) if card["ozel_kod"] else dsl_plan(card, {"X": frame}, week_end="SUN", market="KRIPTO25")
    assert plan.stop_eklendi == card["stop_eklendi"]
    if card.get("zaman_stop"):
        assert plan.engine_kwargs["time_stop_bars"] == card["zaman_stop"]["bar"]
    if card.get("dolum") == "kapanis":
        assert plan.engine_kwargs["fill_at_close"] is True


# ----------------------------------------------------------------------------------- ileriye bakma yok
@pytest.mark.parametrize("script_id", TAM_IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(script_id, seed):
    card = load(script_id)
    frame = walk(1000, seed, freq_of(card))
    full = signals(script_id, frame)
    rng = np.random.default_rng(seed + 100)
    for cut in (350, 600, 850):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.15, len(frame) - (cut + 1)).cumsum())  # cut+1 ve sonrasi tamamen farkli
        for column in ("open", "high", "low", "close"):
            altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
        altered.iloc[cut + 1:, altered.columns.get_loc("volume")] = rng.uniform(100, 1000, len(frame) - (cut + 1))
        again = signals(script_id, altered)
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_ornek_seri_sinyal_uretir_ya_da_nadir(script_id):
    """Ileriye bakma testi bos sinyallerle gecmesin: uzun sentetik seride giris ya da cikis en az bir kez olusmali."""
    card = load(script_id)
    total = 0
    for seed in (7, 8, 9):
        frame = walk(4000, seed, freq_of(card))
        if script_id == "o9qty0BL":   # kart 2021-09-25 oncesi islem uretmez (test penceresi)
            frame.index = frame.index + (pd.Timestamp("2021-10-01", tz="UTC") - pd.Timestamp("2018-01-01", tz="UTC"))
        sig = signals(script_id, frame)
        total += int(sig["entry"].sum()) + int(sig["exit"].sum())
    assert total > 0


# ----------------------------------------------------------------------------- elle hesaplanmis ornekler
def test_zrdoqmf9f_ema_kesisimi_elle_ornek():
    # 60 bar sabit 100: EMA(20) = EMA(50) = 100 (esitlik kesisim degil). Bar 60 kapanis 110, bar 61 kapanis 80.
    close = [100.0] * 60 + [110.0, 80.0]
    sig = signals("zrDoqm9F", frame_from(close))
    assert not sig["entry"].iloc[:60].any() and not sig["exit"].iloc[:60].any()
    # bar 60: EMA20 = 100 + 10*2/21 = 100.952, EMA50 = 100 + 10*2/51 = 100.392 -> hizli > yavas, bir onceki bar esit: yukari kesisim
    assert sig["entry"].iloc[60] and not sig["exit"].iloc[60]
    # bar 61: EMA20 = 100.952 + (80 - 100.952)*2/21 = 98.957, EMA50 = 100.392 + (80 - 100.392)*2/51 = 99.592 -> asagi kesisim
    assert sig["exit"].iloc[61] and not sig["entry"].iloc[61]


def test_vcriudnf_dip_alimi_elle_ornek():
    # 40 bar 100, bar 40 kapanis 90, bar 41 kapanis 95, bar 42 kapanis 100 (high = close)
    close = [100.0] * 40 + [90.0, 95.0, 100.0]
    sig = signals("VcRiudNf", frame_from(close))
    # bar 41: close[1] = 90; EMA20[1] = 100 + (90 - 100)*2/21 = 99.048; 99.048 * 0.992 = 98.26 > 90 ve 95 > 90: giris
    assert sig["entry"].iloc[41] and not sig["entry"].iloc[40]
    # bar 40: close[1] = 100 < EMA20[1] * 0.992 = 99.2 degil -> giris yok (yukaridaki satirin tersi, esik testi)
    # cikis: high >= EMA20. Bar 41: EMA20 = 98.662 > high 95 -> yok; bar 42: EMA20 = 98.79 <= 100 -> var
    assert not sig["exit"].iloc[41] and sig["exit"].iloc[42]


def test_anmkxwwj_donchian_kirilimi_ve_stop_elle_ornek():
    n = 205
    close = [100.0] * n + [102.0, 98.0]
    high = [101.0] * n + [102.5, 98.5]
    low = [99.0] * n + [101.0, 97.5]
    frame = frame_from(close, high=high, low=low)
    sig = signals("ANmKXWWJ", frame)
    # bar 205: onceki 20 barin en yuksek high'i 101 < 102 ve bar 204 kapanisi 100 <= 101: yukari kesisim; SMA(200) = (199*100 + 102)/200 = 100.01 < 102
    assert sig["entry"].iloc[205] and not sig["entry"].iloc[204]
    # stop = sinyal kapanisi - 2 x SMA(TR, 20): TR(186..204) = 2, TR(205) = max(1.5, |102.5-100|, |101-100|) = 2.5 -> (19*2 + 2.5)/20 = 2.025 -> 102 - 4.05 = 97.95
    plan = dsl_plan(load("ANmKXWWJ"), {"X": frame}, week_end="SUN", market="KRIPTO25")
    assert plan.engine_kwargs["level_fns"]["stop"]("X", 205, 102.0) == pytest.approx(97.95)
    # cikis: bar 206 kapanis 98 < onceki 20 barin (186..205) en dusuk low'u 99
    assert sig["exit"].iloc[206] and not sig["exit"].iloc[205]


def _tracker(cls, close, atr, exit_low, active=None, **attrs):
    tracker = object.__new__(cls)
    tracker.close = np.asarray(close, dtype=float)
    tracker.open = tracker.close.copy()
    tracker.size = len(close)
    tracker.atr = np.asarray(atr, dtype=float)
    tracker.exit_low = np.asarray(exit_low, dtype=float)
    tracker.active = np.ones(len(close), dtype=bool) if active is None else active
    for key, value in attrs.items():
        setattr(tracker, key, value)
    return tracker


def test_z9o5w3sg_risk_cizgisi_gevsemez_elle_ornek():
    from strategies.ozel.tv_z9o5w3sg import _Tracker

    # dolum bari 1, dolum fiyati 103, ATR = 2, carpan 3. Bar 1: zirve = kapanis 104, risk = 103 - 6 = 97.
    # Bar 2: zirve 108, risk = max(97, 108 - 6) = 102. Bar 3: kapanis 106 > 102. Bar 4: kapanis 101 <= 102 -> cikis.
    tracker = _tracker(_Tracker, [100, 104, 108, 106, 101, 99], [2.0] * 6, [90.0] * 6, mult=3.0)
    assert tracker.exit_bar(1, 103.0, 1) == 4
    # risk cizgisi gevsemez: ATR 4'e cikarsa zirve - 12 = 96 < 102, risk 102 kalir (bar 4 yine cikis)
    tracker = _tracker(_Tracker, [100, 104, 108, 106, 101, 99], [2.0, 2.0, 2.0, 4.0, 4.0, 4.0], [90.0] * 6, mult=3.0)
    assert tracker.exit_bar(1, 103.0, 1) == 4
    # Donchian cikisi: kapanis < onceki 10 barin en dusugu
    tracker = _tracker(_Tracker, [100, 104, 108, 106, 101, 99], [2.0] * 6, [0, 0, 0, 107.0, 0, 0], mult=3.0)
    assert tracker.exit_bar(1, 103.0, 1) == 3


def test_97gxva5b_chandelier_cikisi_elle_ornek():
    from strategies.ozel.tv_97gxva5b import _Tracker

    # giris bari 0 (kapanis 100, ATR 2): ilk stop = 100 - 2*2 = 96. Bar 1: zirve 105, seviye max(96, 105 - 6) = 99; kapanis 105.
    # Bar 2: zirve 110, seviye 104; kapanis 110. Bar 3: kapanis 108 > 104. Bar 4: kapanis 103 < 104 -> cikis.
    tracker = _tracker(_Tracker, [100, 105, 110, 108, 103, 90], [2.0] * 6, [0.0] * 6, stop_atr=2.0, trail_atr=3.0,
                       after_end=np.zeros(6, dtype=bool))
    assert tracker.exit_bar(0) == 4
    # giris barinin kendisinde cikis aranmaz: giris kapanisi 100, ATR 50 -> ilk stop 0; bar 1 kapanis 99 < seviye? seviye = max(0, 99 - 150) = 0 -> yok
    tracker = _tracker(_Tracker, [100, 99, 98], [50.0] * 3, [0.0] * 3, stop_atr=2.0, trail_atr=3.0, after_end=np.zeros(3, dtype=bool))
    assert tracker.exit_bar(0) is None


def test_xyfla6o7_regresyon_egimi_elle_ornek():
    from strategies.ozel.tv_xyfla6o7 import linreg_slope

    # y = [2, 4, 6]: egim 2; y = [1, 3, 2, 5, 4], n = 5: sum((x - 2) * y) / 10 = (-2*1 - 1*3 + 0 + 1*5 + 2*4)/10 = 0.8
    assert linreg_slope(pd.Series([2.0, 4.0, 6.0]), 3).iloc[-1] == pytest.approx(2.0)
    assert linreg_slope(pd.Series([1.0, 3.0, 2.0, 5.0, 4.0]), 5).iloc[-1] == pytest.approx(0.8)
