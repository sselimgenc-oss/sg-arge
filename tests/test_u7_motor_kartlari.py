"""U7 Ek 4: dinamik_cikis / bar ici kademeli_cikis ile yeniden cevrilen TV kartlari: sema, ileriye bakma yok, elle hesaplanmis ornekler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine import gosterge
from engine.kart_sinyal import build_plan as dsl_plan, card_frame_signals
from engine.spec import validate_card
from strategies.ozel import build_plan as ozel_plan

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


def _cards() -> dict[str, dict]:
    out = {}
    for path in sorted(SPEC.glob("TV-*.yaml")):
        card = yaml.safe_load(path.read_text(encoding="utf-8"))
        if any(str(b).startswith("U7 Ek 4") for b in card["belirsiz"]):
            out[card["id"][3:]] = card
    return out


KARTLAR = _cards()
TAM_IDS = [i for i, c in KARTLAR.items() if c["spec_durumu"] == "tam"]
DOG_IDS = [i for i, c in KARTLAR.items() if c["spec_durumu"] == "eksik"]


def load(script_id: str) -> dict:
    return yaml.safe_load((SPEC / f"TV-{script_id}.yaml").read_text(encoding="utf-8"))


def walk(bars: int, seed: int, freq: str, sigma: float = 0.012) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.001, sigma, bars)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, bars))
    spread = rng.uniform(0.0, 0.01, bars)
    index = pd.date_range("2018-01-01", periods=bars, freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * (1 + spread), "low": np.minimum(open_, close) * (1 - spread),
                         "close": close, "volume": rng.uniform(100, 1000, bars)}, index=index)


def freq_of(card: dict) -> str:
    return "4h" if card["tf"] == "4H" else "1D"


def signals(script_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    card = load(script_id)
    if card.get("ozel_kod"):
        return ozel_plan(card, {"X": frame}).signals["X"]
    return card_frame_signals(card, frame, week_end="FRI")[0]


def test_kart_listesi_bos_degil():
    assert TAM_IDS and DOG_IDS is not None


@pytest.mark.parametrize("script_id", list(KARTLAR))
def test_kart_semasi(script_id):
    card = KARTLAR[script_id]
    assert validate_card(SPEC / f"TV-{script_id}.yaml", card, set()).errors == []
    assert card["deneme_sayisi_kaynakta"] == 205 and card["yalniz_long_bacak"] is True and card["belirsiz"]
    assert all(v is None for k, v in card["rapor"].items() if k != "maliyet_dahil")
    if card["spec_durumu"] == "tam":
        assert card["dinamik_cikis"] if not card["ozel_kod"] and not card.get("kademeli_cikis") else True
        plan = ozel_plan(card, {"X": walk(500, 1, freq_of(card))}) if card["ozel_kod"] else dsl_plan(card, {"X": walk(500, 1, freq_of(card))}, week_end="FRI", market="ABD25")
        assert plan.stop_eklendi == card["stop_eklendi"]
    else:
        assert card["dogrulanamaz"]["ayrinti"] and card["dogrulanamaz"]["neden"] in ("ceviri", "veri", "piyasa", "seans")


@pytest.mark.parametrize("script_id", TAM_IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(script_id, seed):
    card = load(script_id)
    frame = walk(1000, seed, freq_of(card))
    full = signals(script_id, frame)
    rng = np.random.default_rng(seed + 100)
    for cut in (350, 600, 850):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.15, len(frame) - (cut + 1)).cumsum())
        for column in ("open", "high", "low", "close"):
            altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
        altered.iloc[cut + 1:, altered.columns.get_loc("volume")] = rng.uniform(100, 1000, len(frame) - (cut + 1))
        again = signals(script_id, altered)
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_sinyal_ya_da_cikis_uretir(script_id):
    card = load(script_id)
    total = 0
    for seed in (7, 8, 9):
        sig = signals(script_id, walk(4000, seed, freq_of(card)))
        total += int(sig["entry"].sum()) + int(sig["exit"].sum())
    assert total > 0


# ------------------------------------------------------------------------------------------------ elle ornekler
def test_ko7qe4xb_dinamik_mesafe_guncel_atr_elle():
    """dinamik_cikis stop_giristen = 3 x ATR14, hedef_giristen = 6 x ATR14: her bar kapanisinda guncel ATR ile hesaplanir."""
    frame = walk(120, 3, "1D")
    sig = signals("KO7Qe4Xb", frame)
    atr = gosterge.build_env(frame, load("KO7Qe4Xb")["gostergeler"])["atr14"]
    ok = atr.notna()
    assert np.allclose(sig.loc[ok, "dyn_stop_rel"], 3.0 * atr[ok]) and np.allclose(sig.loc[ok, "dyn_target_rel"], 6.0 * atr[ok])


def test_ospkem6i_seviyeler_guncel_kapanis_elle():
    """Stop = kapanis x 0,982, hedef = kapanis x 1,06: kapanis 200 -> 196,4 / 212; kapanis 100 -> 98,2 / 106."""
    frame = walk(60, 4, "4h")
    frame.loc[frame.index[10], "close"] = 200.0
    frame.loc[frame.index[11], "close"] = 100.0
    sig = signals("Ospkem6i", frame)
    assert sig["dyn_stop"].iloc[10] == pytest.approx(196.4) and sig["dyn_target"].iloc[10] == pytest.approx(212.0)
    assert sig["dyn_stop"].iloc[11] == pytest.approx(98.2) and sig["dyn_target"].iloc[11] == pytest.approx(106.0)


def test_mi47rsio_trend_sayaci_elle():
    """EMA20 > EMA50 ilk kez bar 0'da degil: sayac barssince ile; 10. ardisik yukselis barinda giris True, oncesinde False."""
    close = np.r_[np.linspace(100, 80, 60), np.linspace(80, 140, 80)]
    frame = pd.DataFrame({"open": close, "high": close + 0.1, "low": close - 0.1, "close": close, "volume": 1.0},
                         index=pd.date_range("2020-01-01", periods=len(close), freq="1D", tz="UTC"))
    sig = signals("MI47rsio", frame)
    env = gosterge.build_env(frame, load("MI47rsio")["gostergeler"])
    bull = (env["fastema"] > env["slowema"]).to_numpy()
    run = np.zeros(len(close), dtype=int)
    for i in range(len(close)):
        run[i] = (run[i - 1] + 1 if i else 1) if bull[i] else 0
    assert np.array_equal(sig["entry"].to_numpy(), bull & (run >= 10)) and sig["entry"].any()


def test_gauss_filtresi_sabit_girdide_bire_yakinsar():
    from strategies.ozel.tv_egtb7tgj import gaussian
    out = gaussian(np.ones(600), alpha=0.1, poles=4)
    assert out[-1] == pytest.approx(1.0, abs=1e-9) and out[0] == pytest.approx(0.1 ** 4)


def test_bjdrgy7z_dinamik_seviye_yalniz_yeni_sinyalde_degisir():
    """valuewhen(sig, close - atr): ayni sinyal sayisi icinde seviye sabit kalir, yeni sinyal barinda yenilenir."""
    frame = walk(1500, 11, "1D")
    card = load("BJDRgy7z")
    sig, _ = card_frame_signals(card, frame, week_end="FRI")
    env = gosterge.build_env(frame, card["gostergeler"])
    events = env["sig"].astype(bool).to_numpy()
    assert events.sum() >= 3
    atr = env["atr14"]
    expected = (frame["close"] - atr).where(pd.Series(events, index=frame.index)).ffill()
    assert np.allclose(sig["dyn_stop"].dropna(), expected.loc[sig["dyn_stop"].dropna().index])
    changes = sig["dyn_stop"].diff().abs() > 1e-12
    assert set(sig.index[changes.fillna(False)]) <= set(sig.index[events])


def test_pivot_dongusu_bagimsiz_referansla_ayni_iv1wlva8():
    """le / se durumlari (pivot sonrasi ilk kirilima kadar dogru) Pine'in ozyinelemeli tanimiyla ayni: bagimsiz dongu."""
    frame = walk(1500, 21, "4h")
    card = load("Iv1wlVa8")
    env = gosterge.build_env(frame, card["gostergeler"])
    high, low = frame["high"].to_numpy(), frame["low"].to_numpy()
    n = len(frame)
    le_ref, se_ref = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    hprice = lprice = np.nan
    le = se = False
    for t in range(n):
        if t >= 3 and high[t - 1] > high[t] and high[t - 1] > high[t - 2] and high[t - 1] > high[t - 3]:
            hprice, le = high[t - 1], True
        elif le and high[t] > hprice:
            le = False
        if t >= 3 and low[t - 1] < low[t] and low[t - 1] < low[t - 2] and low[t - 1] < low[t - 3]:
            lprice, se = low[t - 1], True
        elif se and low[t] < lprice:
            se = False
        le_ref[t], se_ref[t] = le, se
    assert np.array_equal(env["le"].astype(bool).to_numpy(), le_ref) and np.array_equal(env["se"].astype(bool).to_numpy(), se_ref)
    assert le_ref.sum() > 50 and se_ref.sum() > 50
