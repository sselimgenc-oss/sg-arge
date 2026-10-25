"""TV-2 koşucusu: aralık okuma, yeniden örnekleme, kapanmamış bar ve karar kuralı (TEST_YAPISI Adım 1-2)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtests import tv2


@pytest.mark.parametrize("tf, dk", [("60", 60), ("240", 240), ("45", 45), ("1D", 1440), ("D", 1440), ("1W", 10080), ("4H", 240), ("3D", 4320)])
def test_tradingview_interval_to_minutes(tf, dk) -> None:
    assert tv2.dakika(tf) == dk


def test_resample_and_unclosed_bar() -> None:
    index = pd.date_range("2024-01-01", periods=6, freq="15min", tz="UTC")
    df = pd.DataFrame({"open": [1, 2, 3, 4, 5, 6], "high": [2, 3, 4, 5, 6, 7], "low": [0, 1, 2, 3, 4, 5],
                       "close": [2, 3, 4, 5, 6, 7], "volume": 1.0}, index=index, dtype=float)
    out = tv2._yeniden_ornekle(df, 45)
    assert list(out["open"]) == [1, 4] and list(out["close"]) == [4, 7] and list(out["high"]) == [4, 7]
    simdi = pd.Timestamp.now(tz="UTC").floor("h")
    canli = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}, index=[simdi - pd.Timedelta("2h"), simdi])
    assert len(tv2._kapanmis(canli, 60)) == 1


def _sahte(monkeypatch, surum: str | None, trend: float) -> dict:
    n = 900
    index = pd.date_range("2022-01-01", periods=n, freq="D", tz="UTC")
    close = 100 * np.exp(np.cumsum(np.full(n, trend) + np.random.default_rng(1).normal(0, 0.01, n)))
    df = pd.DataFrame({"open": np.r_[close[0], close[:-1]], "close": close}, index=index)
    df["high"], df["low"] = df[["open", "close"]].max(axis=1) * 1.002, df[["open", "close"]].min(axis=1) * 0.998
    monkeypatch.setattr(tv2, "veri", lambda s, tf, bas=None: (df, "Binance TEST 1d"))
    monkeypatch.setattr(tv2, "SURUMLER", tv2.ROOT / "yok.csv")
    monkeypatch.setattr(tv2, "OUT", tv2.ROOT / ".pytest_cache" / "tv2")
    from strategies.tv2 import ospkem6i
    monkeypatch.setattr(ospkem6i, "KAYNAK", dict(ospkem6i.KAYNAK, surum_tarihi=surum))
    return tv2.kos("ospkem6i")


def test_decision_labels(monkeypatch) -> None:
    assert _sahte(monkeypatch, None, 0.002)["karar"] == "izle"                      # sürüm tarihi yok
    assert _sahte(monkeypatch, "2024-03-01", 0.002)["etiket"] == "yetersiz_kanit"   # sürüm sonrası < 1 yıl
    assert _sahte(monkeypatch, "2024-03-01", 0.002)["karar"] == "izle"
    satir = _sahte(monkeypatch, "2022-12-01", 0.002)
    assert satir["etiket"] == "temiz" and satir["karar"] in {"gecti", "kaldi", "izle"}
    assert satir["karar"] == ("izle" if satir["uyg_sinama_hafta"] < tv2.KAPI_HAFTA
                              else "gecti" if satir["uyg_sinama_net_yuzde"] > 0 else "kaldi")


def test_zero_trades_is_its_own_decision_not_watch(monkeypatch) -> None:
    from strategies.tv2 import ospkem6i
    monkeypatch.setattr(ospkem6i, "bar", lambda ctx, i, v: None)
    satir = _sahte(monkeypatch, "2023-01-01", 0.002)
    assert satir["karar"] == "islem_yok" and "0 işlem" in satir["neden"]


def test_yfinance_intraday_picks_largest_divisor_and_resamples(monkeypatch, tmp_path) -> None:
    import sys
    import types
    index = pd.date_range("2024-01-01", periods=48, freq="60min", tz="UTC")
    ham = pd.DataFrame({"Open": 1.0, "High": 2.0, "Low": 0.5, "Close": 1.5, "Volume": 1.0}, index=index)
    cagri = {}

    def indir(kod, period, interval, **_):
        cagri.update(kod=kod, period=period, interval=interval)
        return ham

    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=indir))
    monkeypatch.setattr(tv2, "CACHE", tmp_path)
    df, notu = tv2._yfinance_gun_ici("DX-Y.NYB", 240)
    assert cagri == {"kod": "DX-Y.NYB", "period": "730d", "interval": "60m"}
    assert len(df) == 12 and "UTC hizalı" in notu


def test_mapped_dukascopy_archive_is_used(monkeypatch, tmp_path) -> None:
    mapping = tmp_path / "map.csv"
    mapping.write_text("id,yayin_sembolu,tf,kaynak,veri_sembolu,esdeger_sembol\nX,OANDA:EURUSD,5,dukascopy,EURUSD,EURUSD\n", encoding="utf-8")
    monkeypatch.setattr(tv2, "ESLESME", mapping)
    frame = pd.DataFrame({"open": [1.], "high": [1.1], "low": [.9], "close": [1.], "volume": [1.]},
                         index=pd.DatetimeIndex([pd.Timestamp("2024-01-01", tz="UTC")]))
    monkeypatch.setattr("data.dukascopy.load_archive", lambda *_args: frame)

    data, note = tv2._eslenmis_veri("OANDA:EURUSD", 5)

    assert data is not None
    assert note == "Dukascopy EURUSD (eşleme)"
