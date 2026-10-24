"""U6 parti 1: TV-<id> kartlari (docs/GOREV_U6.md bolum 2 ve 5A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

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
PARTI_IDS = ['uC1oajDr', 'DUCODGjC', 'ouvmvItR', 'rvBgD3aP', '1OnkbAiE', 'kbYTJ8V2', 'NgSIfKQx', 'buSJAz8o', 'M6uONKNI', 'X0F9OE4L', 'dwgn7hrE', 'TbK1rB5B', 'hezSShJr', 'W67tJltC', 'EcEYc8ap', 'zoY9DmsF', 'WWuTjyDx', 'V3NuuiPx', '7C1kIEOn', 'jc2hs2qK', 'roaahmoi', 'qDPWh3KO', 'Xr2xrNAY', 'TIpnJpU8', 'R9nsvSZR', 'OePmdMFg', 'N0nYQBlh', '70PkIvTL', 'Iv1wlVa8', 'yvDyq0pv', 'HjySseyp', 'kzp8e4X3', 'VO6DY8s1', '5zYcH3Gx', 'dpZLkrdx', 'gf21APTn', 'rjAoFt4N', 'HPbRZvsV', 'QTYaYuX7', 'jjhUHcje', 'zBaDqbla', 'tWS24Z2K', 'f80Cfpfp', 'Q9OQye4C', '16yhUQN3', 'NXbsqL9n', 'qSLcZSyw', 'ROM3crig', 'YsWWsOGs', '6knHPR6c', 'XnvfXLPF', '67fpKimh']
TAM_IDS = ['uC1oajDr', 'DUCODGjC', 'rvBgD3aP', 'NgSIfKQx', 'buSJAz8o', 'X0F9OE4L', 'dwgn7hrE', 'TbK1rB5B', 'W67tJltC', 'zoY9DmsF', 'WWuTjyDx', '7C1kIEOn', 'jc2hs2qK', 'roaahmoi', 'qDPWh3KO', 'Xr2xrNAY', 'TIpnJpU8', 'yvDyq0pv', 'VO6DY8s1', 'HPbRZvsV', 'QTYaYuX7', 'YsWWsOGs', '6knHPR6c']
OZEL_IDS = ['rvBgD3aP', 'buSJAz8o', 'dwgn7hrE', 'TbK1rB5B', 'W67tJltC', '7C1kIEOn', 'qDPWh3KO', 'Xr2xrNAY', 'TIpnJpU8', 'yvDyq0pv', 'QTYaYuX7']
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
        sig = signals(script_id, walk(4000, seed, freq_of(card)))
        total += int(sig["entry"].sum()) + int(sig["exit"].sum())
    assert total > 0


# ----------------------------------------------------------------------------- elle hesaplanmis ornekler
def test_roaahmoi_elle_ornek():
    # 300 bar sabit fiyat 100: tum EMA'lar 100. Bar 300 hl2 = close = 110, bar 301 hl2 = close = 80.
    close = [100.0] * 300 + [110.0, 80.0]
    sig = signals("roaahmoi", frame_from(close, freq="4h"))
    assert not sig["entry"].iloc[:300].any() and not sig["exit"].iloc[:300].any()   # esit EMA'lar: kosullar sert esitsizlik
    # bar 300: lips = EMA5 = 100 + 10*2/6 = 103.33, teeth = EMA9 = 100 + 10*2/10 = 102.0, jaw = EMA15 = 100 + 10*2/16 = 101.25,
    # trend = EMA200 = 100 + 10*2/201 = 100.0995 -> 110 > trend, lips > teeth > jaw: giris
    assert sig["entry"].iloc[300] and not sig["exit"].iloc[300]
    # bar 301: lips = 103.33 + (80 - 103.33)/3 = 95.56, teeth = 102 + (80 - 102)*0.2 = 97.6, jaw = 101.25 - 21.25/8 = 98.59,
    # trend = 100.0995 + (80 - 100.0995)*2/201 = 99.8995 -> 80 < trend, lips < teeth < jaw: cikis
    assert sig["exit"].iloc[301] and not sig["entry"].iloc[301]


def test_yswwsogs_elle_ornek():
    # SMA(28): 40 bar 100, bar 40 kapanis 110, bar 41 kapanis 90. Giris close > SMA, cikis close < SMA.
    close = [100.0] * 40 + [110.0, 90.0]
    sig = signals("YsWWsOGs", frame_from(close))
    assert not sig["entry"].iloc[:40].any()              # close == SMA: giris yok (sert esitsizlik)
    # bar 40: SMA = (27*100 + 110)/28 = 100.357 -> 110 > SMA: giris
    assert sig["entry"].iloc[40] and not sig["exit"].iloc[40]
    # bar 41: SMA = (26*100 + 110 + 90)/28 = 100.0 -> 90 < SMA: cikis
    assert sig["exit"].iloc[41] and not sig["entry"].iloc[41]


def test_jc2hs2qk_elle_ornek():
    n = 260
    close = [100.0] * n + [102.0] + [90.0] * 5
    high = [101.0] * n + [102.5] + [91.0] * 5
    low = [99.0] * n + [101.0] + [89.0] * 5
    volume = [10.0] * n + [11.0] + [10.0] * 5
    sig = signals("jc2hs2qK", frame_from(close, high=high, low=low, volume=volume, freq="4h"))
    # bar 260: onceki 60 barin en yuksek high'i 101 < kapanis 102; onceki 60 barin en yuksek hacmi 10 < 11;
    # SMA(200) = (199*100 + 102)/200 = 100.01 < 102: giris. Bar 259'da kapanis 100 < 101: giris yok.
    assert sig["entry"].iloc[260] and not sig["entry"].iloc[259]
    # cikis: son 5 kapanisin hepsi BUGUNKU SMA'nin altinda. Bar 264'te close[4] = bar 260'in 102'si SMA(~99.9) ustunde: yok.
    assert not sig["exit"].iloc[260:265].any()
    # bar 265: bar 261-265 kapanislari 90 < SMA(200) = 99.8: cikis
    assert sig["exit"].iloc[265]


def test_yvdyq0pv_ay_evresi_elle_ornek():
    # diff = ((2021-01-13 05:00 UTC ms + bar acilis ms + 2 gun) % 2551442876.8992) / 2551442876.8992. Gunluk adim = 86400000 / 2551442876.8992 = 0.033864.
    # 2022-01-01 00:00 UTC'de diff = 0.4483; 2022-01-02: 0.4821; 2022-01-03: 0.5160 (> 0.5 yukari kesisim = yeni ay -> cikis);
    # 2022-01-18 (k=17): diff 0.0240 < onceki 0.9901 (sarma = dolunay -> giris); 2022-02-02 (k=32): 0.5319, onceki 0.4980 -> yeni ay.
    frame = frame_from(np.full(40, 100.0))
    frame.index = pd.date_range("2022-01-01", periods=40, freq="1D", tz="UTC")
    sig = signals("yvDyq0pv", frame)
    assert list(np.flatnonzero(sig["entry"].to_numpy())) == [17]
    assert list(np.flatnonzero(sig["exit"].to_numpy())) == [2, 32]
