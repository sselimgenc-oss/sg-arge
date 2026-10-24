"""U6 parti 1: TV-<id> kartlari (docs/GOREV_U6.md bolum 2 ve 5A): sema, ileriye bakma yok, elle hesaplanmis ornekler."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from engine.kart_sinyal import build_plan, card_frame_signals
from engine.spec import validate_card

SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"
PARTI_IDS = ['16yhUQN3', '1OnkbAiE', '5zYcH3Gx', '67fpKimh', '6knHPR6c', '70PkIvTL', '7C1kIEOn', 'DUCODGjC', 'EcEYc8ap', 'HPbRZvsV', 'HjySseyp', 'Iv1wlVa8', 'M6uONKNI', 'N0nYQBlh', 'NXbsqL9n', 'NgSIfKQx', 'OePmdMFg', 'Q9OQye4C', 'QTYaYuX7', 'R9nsvSZR', 'ROM3crig', 'TIpnJpU8', 'TbK1rB5B', 'V3NuuiPx', 'VO6DY8s1', 'W67tJltC', 'WWuTjyDx', 'X0F9OE4L', 'XnvfXLPF', 'Xr2xrNAY', 'YsWWsOGs', 'buSJAz8o', 'dpZLkrdx', 'dwgn7hrE', 'f80Cfpfp', 'gf21APTn', 'hezSShJr', 'jc2hs2qK', 'jjhUHcje', 'kbYTJ8V2', 'kzp8e4X3', 'ouvmvItR', 'qDPWh3KO', 'qSLcZSyw', 'rjAoFt4N', 'roaahmoi', 'rvBgD3aP', 'tWS24Z2K', 'uC1oajDr', 'yvDyq0pv', 'zBaDqbla', 'zoY9DmsF']
TAM_IDS = ['6knHPR6c', 'DUCODGjC', 'HPbRZvsV', 'NgSIfKQx', 'VO6DY8s1', 'WWuTjyDx', 'X0F9OE4L', 'YsWWsOGs', 'jc2hs2qK', 'roaahmoi', 'uC1oajDr', 'zoY9DmsF']
SINIFLAR = ("KRIPTO", "ABD", "EMTIA")
NEDENLER = ("piyasa", "veri", "ceviri")


def load(script_id: str) -> dict:
    return yaml.safe_load((SPEC / f"TV-{script_id}.yaml").read_text(encoding="utf-8"))


def signals(script_id: str, frame: pd.DataFrame) -> pd.DataFrame:
    out, _ = card_frame_signals(load(script_id), frame, week_end="SUN")
    return out


def frame_from(close, high=None, low=None, open_=None, volume=None, freq: str = "1D") -> pd.DataFrame:
    close = np.asarray(close, dtype=float)
    open_ = close.copy() if open_ is None else np.asarray(open_, dtype=float)
    high = close.copy() if high is None else np.asarray(high, dtype=float)
    low = close.copy() if low is None else np.asarray(low, dtype=float)
    volume = np.full(len(close), 1.0) if volume is None else np.asarray(volume, dtype=float)
    index = pd.date_range("2020-01-01", periods=len(close), freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": volume}, index=index)


def walk(bars: int, seed: int, freq: str) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.025, bars)))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.003, bars))
    spread = rng.uniform(0.002, 0.03, bars)
    index = pd.date_range("2018-01-01", periods=bars, freq=freq, tz="UTC")
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) * (1 + spread),
                         "low": np.minimum(open_, close) * (1 - spread), "close": close,
                         "volume": rng.uniform(100, 1000, bars)}, index=index)


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
        assert card["ozel_kod"] is False and card["piyasa_kisiti"] == [card["kol"].split("-")[0]]
        assert card["kol"].split("-")[0] in SINIFLAR
        assert card["kol"].endswith("1D") or card["kol"].startswith("KRIPTO")  # ABD/emtia 4H yok
        assert card["stop_eklendi"] == (card["stop"] is None)
        assert card["giris"] and card["cikis"]
    else:
        assert card["spec_durumu"] == "eksik"
        assert card["dogrulanamaz"]["neden"] in NEDENLER and card["dogrulanamaz"]["ayrinti"]


def test_tam_kart_listesi_kayitla_tutarli():
    assert sorted(i for i in PARTI_IDS if load(i)["spec_durumu"] == "tam") == sorted(TAM_IDS)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_motor_plani_kurulur(script_id):
    card = load(script_id)
    frame = walk(900, 5, "4h" if card["tf"] == "4H" else "1D")
    plan = build_plan(card, {"X": frame}, week_end="SUN", market="KRIPTO25")
    assert plan.stop_eklendi == card["stop_eklendi"]
    if card.get("zaman_stop"):
        assert plan.engine_kwargs["time_stop_bars"] == card["zaman_stop"]["bar"]


# ----------------------------------------------------------------------------------- ileriye bakma yok
@pytest.mark.parametrize("script_id", TAM_IDS)
@pytest.mark.parametrize("seed", [1, 2])
def test_ileriye_bakma_yok(script_id, seed):
    card = load(script_id)
    frame = walk(1000, seed, "4h" if card["tf"] == "4H" else "1D")
    full = signals(script_id, frame)
    rng = np.random.default_rng(seed + 100)
    for cut in (350, 600, 850):
        altered = frame.copy()
        shock = np.exp(rng.normal(0, 0.15, len(frame) - (cut + 1)).cumsum())  # cut+1 ve sonrasi tamamen farkli
        for column in ("open", "high", "low", "close"):
            altered.iloc[cut + 1:, altered.columns.get_loc(column)] = frame[column].iloc[cut + 1:].to_numpy() * shock
        altered.iloc[cut + 1:, altered.columns.get_loc("volume")] = rng.uniform(100, 1000, len(frame) - (cut + 1))
        again = signals(script_id, altered)
        pd.testing.assert_frame_equal(full.iloc[: cut + 1], again.iloc[: cut + 1], check_exact=False, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("script_id", TAM_IDS)
def test_ornek_seri_sinyal_uretir_ya_da_nadir(script_id):
    """Cikis ve giris sinyallerinin ikisi de hic uretilmiyorsa ileriye bakma testi bos gecer: en az biri dolu olmali."""
    card = load(script_id)
    sig = signals(script_id, walk(3000, 7, "4h" if card["tf"] == "4H" else "1D"))
    assert int(sig["entry"].sum()) + int(sig["exit"].sum()) > 0


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
