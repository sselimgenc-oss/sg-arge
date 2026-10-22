from __future__ import annotations

import json

import pandas as pd

from backtests.sonuc_raporu import build_report


def _write(path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def test_report_applies_stage_precedence_and_survives_missing_inputs(tmp_path) -> None:
    spec, results = tmp_path / "spec", tmp_path / "results"
    spec.mkdir(); results.mkdir()
    _write(spec / "INDEKS.csv", "id,ad,tarz,tf,kaynak\nA,Alpha,swing,1D,x\nB,Beta,swing,1D,x\nC,Gamma,day,1D,x\nD,Delta,day,1D,x\nE,Epsilon,day,1D,x\n")
    _write(spec / "YENIDEN.csv", "id,ad,url,neden\nE,Epsilon,u,engelli\n")
    _write(spec / "A.yaml", "id: A\nad: Alpha\nspec_durumu: tam\nozel_kod: false\n")
    _write(spec / "B.yaml", "id: B\nad: Beta\nspec_durumu: tam\nozel_kod: false\n")
    _write(spec / "C.yaml", "id: C\nad: Gamma\nspec_durumu: eksik\nozel_kod: false\n")
    _write(spec / "D.yaml", "id: D\nad: Delta\nspec_durumu: tam\nozel_kod: false\n")
    _write(spec / "E.yaml", "id: E\nad: Epsilon\nspec_durumu: eksik\nozel_kod: false\n")
    _write(results / "tarama.csv", "id,piyasa,durum,asama2_aday,neden\nA,ABD25,Hesaplandi,False,islem<30\nB,ABD25,Hesaplandi,True,\nD,ABD25,Hesaplandi,False,islem<30\n")
    _write(results / "asama2a.csv", "id,piyasa,karar,neden\nA,ABD25,Reddedildi (piyasa betasi),PF p=0.4\nB,ABD25,Gecti (null),\n")
    _write(results / "asama2b.csv", "id,piyasa,karar,neden\nA,ABD25,Gecti,tum kapilar\n")

    table = build_report(spec, results).set_index("id")
    assert table.loc["A", "nihai_durum"] == "Gecti"  # 2b outranks 2a rejection
    assert table.loc["B", "nihai_durum"] == "Bekliyor"
    assert table.loc["B", "alt_neden"] == "asama 2b bekliyor"
    assert table.loc["C", "alt_neden"] == "eksik"
    assert table.loc["D", "nihai_durum"] == "Reddedildi"
    assert table.loc["E", "alt_neden"] == "kaynak erisilemedi"
    assert json.loads(table.loc["A", "piyasa_ayrintisi"])[0]["asama"] == "tarama"
    assert (results / "SONUC.md").exists() and (results / "sonuc.csv").exists()


def test_best_market_uses_passed_asama2a_instead_of_another_market_rejection(tmp_path) -> None:
    spec, results = tmp_path / "spec", tmp_path / "results"
    spec.mkdir(); results.mkdir()
    _write(spec / "INDEKS.csv", "id,ad,tarz,tf,kaynak\nX,X,swing,1D,x\n")
    _write(spec / "YENIDEN.csv", "id,ad,url,neden\n")
    _write(spec / "X.yaml", "id: X\nad: X\nspec_durumu: tam\nozel_kod: false\n")
    _write(results / "asama2a.csv", "id,piyasa,karar,neden\nX,BIST30,Reddedildi (BIST USD),USD kapisi\nX,KRIPTO25,Gecti (null),\n")

    row = build_report(spec, results).set_index("id").loc["X"]
    assert row["nihai_durum"] == "Bekliyor"
    assert row["en_iyi_piyasa"] == "KRIPTO25"
    assert "asama2b.csv" in (results / "SONUC.md").read_text(encoding="utf-8")


def test_waiting_and_deferred_statuses_are_not_dogrulanamaz(tmp_path) -> None:
    spec, results = tmp_path / "spec", tmp_path / "results"
    spec.mkdir(); results.mkdir()
    _write(spec / "INDEKS.csv", "id,ad,tarz,tf,kaynak\nM,M,day,1D,x\nS,S,day,1D,x\nP,P,day,1D,x\nK,K,day,1D,x\n")
    _write(spec / "YENIDEN.csv", "id,ad,url,neden\n")
    _write(spec / "M.yaml", "id: M\nspec_durumu: tam\nozel_kod: false\n")
    _write(spec / "S.yaml", "id: S\nspec_durumu: sadece_short\nozel_kod: false\n")
    _write(spec / "P.yaml", "id: P\nspec_durumu: tam\nozel_kod: true\nozel_kod_nedeni: portfoy_rotasyonu\n")
    _write(spec / "K.yaml", "id: K\nspec_durumu: kapsam_disi\nozel_kod: false\n")
    table = build_report(spec, results).set_index("id")
    assert (table.loc["M", "nihai_durum"], table.loc["M", "alt_neden"]) == ("Bekliyor", "tarama bekliyor")
    assert table.loc["S", "nihai_durum"] == "Ertelendi"
    assert table.loc["P", "nihai_durum"] == "Ertelendi"
    assert table.loc["K", "nihai_durum"] == "Kapsam disi"
