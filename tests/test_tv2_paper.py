"""Faz 2 TV-2 paper katmanı: kaynak kapısı ve emülatör paritesi."""

from __future__ import annotations

import hashlib
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from backtests import tv2
from engine.pine.yorumlayici import PineStrateji
from engine.tv_emulator import calistir, gercekci
from paper import gunluk, tv2_kitap


def _frame(periods: int = 120, freq: str = "h") -> pd.DataFrame:
    index = pd.date_range("2026-10-20", periods=periods, freq=freq, tz="UTC")
    close = 100 + np.sin(np.arange(periods) / 5) * 10 + np.arange(periods) * .1
    return pd.DataFrame({"open": close - .2, "high": close + 1, "low": close - 1, "close": close, "volume": 1.0}, index=index)


def test_source_hash_mismatch_stops_the_book(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tv2_kitap, "surum", lambda _id: tv2_kitap.Surum("G4RNcGXg", "1.0", "0" * 64, "paper/tv2_kaynak/G4RNcGXg.pine"))
    with pytest.raises(tv2_kitap.KaynakDogrulamaHatasi, match="SHA256"):
        tv2_kitap.kaynak("G4RNcGXg")


def test_yho_uses_fixed_version_and_checks_the_download(monkeypatch: pytest.MonkeyPatch) -> None:
    text = "strategy('test')"
    monkeypatch.setattr(tv2_kitap, "surum", lambda _id: tv2_kitap.Surum("yhoK9cH4", "1.0", hashlib.sha256(text.encode()).hexdigest(), ""))
    seen = []

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"source": text}

    assert tv2_kitap.kaynak("yhoK9cH4", fetch=lambda url: seen.append(url) or Response()) == text
    assert seen and "/1.0?" in seen[0] and "/last" not in seen[0]


def test_tv2_path_is_selected_by_kaynak(monkeypatch: pytest.MonkeyPatch) -> None:
    satir = gunluk.Satir("G4RNcGXg", "ABD25", "tv2", .05, "60")
    frame = _frame()
    seen = {}
    result = SimpleNamespace()
    monkeypatch.setattr(tv2_kitap, "calistir_kitap", lambda *args, **_kwargs: (seen.update({"args": args}) or result, frame.index[-1]))
    got, end = gunluk.kitap(satir, gunluk.Veri({}, {}, "x"), frame.index[50], 250.0)
    assert got is result and end == frame.index[-1] and seen["args"][0] is satir


def test_source_failure_writes_a_per_book_stop_alarm(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    satir = gunluk.Satir("G4RNcGXg", "ABD25", "tv2", .05, "60")
    start = pd.Timestamp("2026-10-27", tz="UTC")
    portfolio = gunluk.Portfoy(5000.0, start, [satir], {"mdd_durdur": .05})
    monkeypatch.setattr(tv2_kitap, "calistir_kitap", lambda *_args, **_kwargs: (_ for _ in ()).throw(tv2_kitap.KaynakDogrulamaHatasi("SHA256 uyuşmuyor")))
    gunluk.calistir(portfolio, gunluk.Veri({}, {}, "sabit"), tmp_path, bugun=start)
    alarms = gunluk._read(tmp_path, "alarmlar")  # noqa: SLF001
    assert ((alarms["tip"] == "DURDUR") & (alarms["satir"] == satir.etiket) & alarms["mesaj"].str.contains("SHA256")).any()


def test_open_bar_is_not_given_to_tv2_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _frame()
    monkeypatch.setattr(tv2_kitap, "_closed", lambda value, _tf: value.iloc[:-1])
    satir = SimpleNamespace(id="G4RNcGXg")
    result, end = tv2_kitap.calistir_kitap(satir, frame.index[70], 250.0, veri_al=lambda *_: (frame, "sabit"))
    assert end == frame.index[-2] and result.equity.index[-1] == frame.index[-2]


def test_ethbtc_equity_records_btc_rate_and_usd_equivalent(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _frame(140, "4h")
    btc = frame.copy()
    btc[["open", "high", "low", "close"]] *= 500
    monkeypatch.setattr(tv2_kitap, "_closed", lambda value, _tf: value)
    satir = SimpleNamespace(id="wcegMOXj")
    result, _ = tv2_kitap.calistir_kitap(
        satir, frame.index[70], 250.0,
        veri_al=lambda symbol, _tf: (btc if symbol.endswith("BTCUSDT") else frame, "sabit"),
    )
    assert result.btc_bakiye is not None and result.btc_usd_kur is not None
    pd.testing.assert_series_equal(result.equity, result.btc_bakiye * result.btc_usd_kur, check_names=False)


def test_paper_runner_matches_the_tv2_emulator_on_same_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _frame(180)
    monkeypatch.setattr(tv2_kitap, "_closed", lambda value, _tf: value)
    satir = SimpleNamespace(id="G4RNcGXg")
    paper, _ = tv2_kitap.calistir_kitap(satir, frame.index[80], 250.0, veri_al=lambda *_: (frame, "sabit"))
    source = tv2_kitap.kaynak("G4RNcGXg")
    _, info = tv2.strateji("G4RNcGXg")
    module = PineStrateji(source, sembol=info["sembol"], tf=info["tf"], kimlik="G4RNcGXg", surum=1)
    direct = calistir(tv2_kitap._BaslangicKapisi(module, frame.index[80]), frame, initial_capital=250.0,
                      **gercekci(module.AYARLAR, False))
    assert list(paper.trades["net_pnl"]) == list(direct.islemler["net"])
