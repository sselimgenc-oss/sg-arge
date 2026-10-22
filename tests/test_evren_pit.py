from __future__ import annotations

import logging

import pandas as pd

from data.evren_pit import filter_entry_signals, load_pit_universe, write_extra_symbols
from tests.test_tarama import synthetic


def _write(path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_bist_pit_carries_previous_list_and_masks_only_new_entries(tmp_path, caplog) -> None:
    bist, abd = tmp_path / "bist.csv", tmp_path / "abd.csv"
    _write(bist, "donem_baslangic,hisse_kodu,kaynak_url,not\n2020-01-01,AAA,u,\n2020-01-01,BBB,u,\n2020-04-01,bulunamadi,,\n2020-07-01,BBB,u,\n")
    _write(abd, "yil,sira,ticker,sirket,kaynak_url,not\n2020,1,MSFT,Microsoft,u,\n")
    with caplog.at_level(logging.WARNING):
        universe = load_pit_universe(bist, abd)
    assert universe.members("BIST30", "2020-05-01") == frozenset({"AAA.IS", "BBB.IS"})
    assert "onceki gecerli liste tasindi" in caplog.text
    index = pd.to_datetime(["2020-02-01", "2020-05-01", "2020-08-01"], utc=True)
    signals = {"AAA.IS": pd.DataFrame({"entry": [True, True, True], "exit": [False, True, False]}, index=index)}
    filtered = filter_entry_signals(signals, universe, "BIST30")
    assert filtered["AAA.IS"]["entry"].tolist() == [True, True, False]
    assert filtered["AAA.IS"]["exit"].tolist() == [False, True, False]
    assert signals["AAA.IS"]["entry"].tolist() == [True, True, True]


def test_abd_membership_is_year_based_and_extra_symbols_exclude_static_universe(tmp_path) -> None:
    bist, abd, static, output = tmp_path / "bist.csv", tmp_path / "abd.csv", tmp_path / "evren.csv", tmp_path / "pit.csv"
    _write(bist, "donem_baslangic,hisse_kodu,kaynak_url,not\n2020-01-01,AAA,u,\n")
    _write(abd, "yil,sira,ticker,sirket,kaynak_url,not\n2020,1,MSFT,Microsoft,u,\n2021,1,BRK.B,Berkshire,u,\n")
    _write(static, "sembol,piyasa,kaynak,not\nMSFT,ABD25,yfinance,\nAAA.IS,BIST30,yfinance,\n")
    universe = load_pit_universe(bist, abd)
    assert universe.members("ABD25", "2021-06-01") == frozenset({"BRK-B"})
    extra = write_extra_symbols(universe, static, output)
    assert extra.to_dict("records") == [{"sembol": "BRK-B", "piyasa": "ABD25", "kaynak": "yfinance", "not": "PIT tarihsel evren"}]


def test_no_pit_universe_is_bit_for_bit_identity() -> None:
    frame = synthetic(11, periods=30)
    signals = {"X": pd.DataFrame({"entry": [True] * len(frame), "exit": [False] * len(frame)}, index=frame.index)}
    assert filter_entry_signals(signals, None, "BIST30") is signals


def test_t11b_early_bist_lists_join_the_2020_list(tmp_path) -> None:
    early = tmp_path / "early.csv"
    early.write_text("donem_baslangic,hisse_kodu,kaynak_url,not\n2019-10-01,KOZAL,u,n\n2019-10-01,AKBNK,u,n\n# ozet: x\n", encoding="utf-8")
    late = tmp_path / "late.csv"
    late.write_text("donem_baslangic,hisse_kodu,kaynak_url,not\n2015-01-02,bulunamadi,,\n2020-01-02,TRALT,u,n\n2020-01-02,GARAN,u,n\n", encoding="utf-8")
    abd = tmp_path / "abd.csv"
    abd.write_text("yil,ticker,kaynak_url,not\n", encoding="utf-8")
    universe = load_pit_universe(late, abd, early)
    assert universe.members("BIST30", "2019-12-01") == frozenset({"TRALT.IS", "AKBNK.IS"})  # old code KOZAL -> TRALT
    assert universe.members("BIST30", "2020-02-01") == frozenset({"TRALT.IS", "GARAN.IS"})
    assert universe.members("BIST30", "2019-09-01") is None
