"""T13/T25: final report assembled from existing result files (no backtest)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from backtests.sonuc_raporu import build_report


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _setup(tmp_path: Path, cards: dict[str, str], *, yeniden: str = "") -> tuple[Path, Path]:
    spec, results = tmp_path / "spec", tmp_path / "results"
    spec.mkdir(); results.mkdir()
    rows = "".join(f"{i},{i},swing,1D,x\n" for i in cards)
    _write(spec / "INDEKS.csv", "id,ad,tarz,tf,kaynak\n" + rows)
    _write(spec / "YENIDEN.csv", "id,ad,url,neden\n" + yeniden)
    for identifier, body in cards.items():
        _write(spec / f"{identifier}.yaml", f"id: {identifier}\nad: {identifier}\n{body}\n")
    return spec, results


TAM = "spec_durumu: tam\nozel_kod: false"


def test_precedence_reasons_and_files(tmp_path: Path) -> None:
    spec, results = _setup(
        tmp_path, {"A": TAM, "B": TAM, "C": "spec_durumu: eksik\nozel_kod: false", "D": TAM, "E": "spec_durumu: eksik\nozel_kod: false\nerisim_engeli: true"},
        yeniden="E,E,u,engelli\n",
    )
    _write(results / "tarama.csv", "id,piyasa,tf,durum,asama2_aday,neden\nA,ABD25,1D,Hesaplandi,False,islem<30\nB,ABD25,1D,Hesaplandi,True,\nD,ABD25,1D,Hesaplandi,False,\"islem<30,PF_1x<1.1\"\n")
    _write(results / "asama2a.csv", "id,piyasa,karar,neden\nA,ABD25,Reddedildi (piyasa betasi),PF p=0.4\nB,ABD25,Gecti (null),\n")
    _write(results / "asama2b.csv", "id,piyasa,karar,neden\nA,ABD25,Gecti,tum kapilar\n")
    table = build_report(spec, results).set_index("id")
    assert table.loc["A", "nihai_durum"] == "Gecti"  # 2b outranks the 2a rejection of the same card
    assert (table.loc["B", "nihai_durum"], table.loc["B", "alt_neden"]) == ("Bekliyor", "asama2b: bekliyor")
    assert table.loc["C", "alt_neden"] == "dogrulanamaz: kaynakta sinyal tanimi yok"
    assert (table.loc["D", "nihai_durum"], table.loc["D", "alt_neden"]) == ("Reddedildi", "asama1: islem<30, PF_1x<1.1")
    assert table.loc["E", "alt_neden"] == "dogrulanamaz: kaynak erisilemedi"
    assert json.loads(table.loc["A", "ayrinti_json"])[0]["asama"] == "asama2b"
    assert (results / "SONUC.md").exists() and (results / "SONUC.csv").exists()
    assert list(pd.read_csv(results / "SONUC.csv").columns)[:6] == ["id", "ad", "kaynak", "tarz", "tf", "nihai_durum"]


def test_ported_card_leaves_the_unreachable_source_list(tmp_path: Path) -> None:
    spec, results = _setup(tmp_path, {"P": TAM}, yeniden="P,P,u,engelli\n")
    assert build_report(spec, results).set_index("id").loc["P", "nihai_durum"] == "Bekliyor"  # tam card: waiting for its scan


def test_pit_row_replaces_the_fixed_universe_row_of_the_same_market(tmp_path: Path) -> None:
    spec, results = _setup(tmp_path, {"X": TAM, "Y": TAM})
    head = "id,piyasa,kaynak,karar,neden,oos_net,bootstrap_mdd_p95,evren\n"
    _write(results / "asama2b.csv", head + "X,ABD25,strateji karti,Kosullu,survivorship yanliligi,0.05,0.1,sabit\nY,ABD25,strateji karti,Kosullu,survivorship yanliligi,0.05,0.1,sabit\n")
    _write(results / "asama2b_pit.csv", head + "X,ABD25,strateji karti,Gecti,paper kapilari gecti,0.08,0.09,pit\nY,ABD25,strateji karti,Reddedildi,OOS ortR<=0,-0.02,0.2,pit\n")
    table = build_report(spec, results).set_index("id")
    assert (table.loc["X", "nihai_durum"], table.loc["X", "evren"]) == ("Gecti", "pit")
    assert table.loc["Y", "nihai_durum"] == "Reddedildi" and table.loc["Y", "alt_neden"] == "asama2b: OOS ortR<=0"
    assert "| X |" in (results / "SONUC.md").read_text(encoding="utf-8").split("## Koşullu")[0]


def test_rotation_rows_are_judged_not_deferred(tmp_path: Path) -> None:
    rotation = TAM + "\nrotasyon: {kip: gecis}"
    spec, results = _setup(tmp_path, {"R1": rotation, "R2": rotation, "R3": rotation, "OLD": "spec_durumu: tam\nozel_kod: true\nozel_kod_nedeni: portfoy_rotasyonu"})
    _write(results / "tarama.csv", "id,piyasa,tf,durum,asama2_aday,neden\n")
    _write(results / "tarama_rotasyon.csv", "id,piyasa,tf,durum,asama2_aday,neden\nR1,ABD25,1D,Hesaplandi,True,\nR2,ABD25,1D,Hesaplandi,True,\nR3,ABD25,1D,Hesaplandi,False,PF_1x<1.1\nR3,BIST30,1D,Dogrulanamaz,False,piyasa_ozgu:ABD\n")
    _write(results / "asama2a.csv", "id,piyasa,tf,karar,neden,metrik\nR1,ABD25,1D,Gecti (null),,PF+CAGR\nR2,ABD25,1D,Reddedildi (piyasa betasi),PF p=0.2,PF+CAGR\n")
    _write(results / "asama2b.csv", "id,piyasa,karar,neden,oos_net,bootstrap_mdd_p95,evren,metrik\nR1,ABD25,Reddedildi,bootstrap MDD>%15,0.1,0.3,enstruman,PF+CAGR\n")
    table = build_report(spec, results).set_index("id")
    assert (table.loc["R1", "nihai_durum"], table.loc["R1", "alt_neden"], table.loc["R1", "metrik"]) == ("Reddedildi", "asama2b: bootstrap MDD>%15", "PF+CAGR")
    assert table.loc["R2", "alt_neden"].startswith("asama2a: null'u gecemedi (piyasa betasi)")
    assert table.loc["R3", "alt_neden"] == "asama1: PF_1x<1.1"
    assert table.loc["OLD", "nihai_durum"] == "Dogrulanamaz" and "portfoy_rotasyonu" in table.loc["OLD", "alt_neden"]  # never "Ertelendi"
    assert not (table["nihai_durum"] == "Ertelendi").any()


def test_best_record_across_markets_and_timeframes(tmp_path: Path) -> None:
    spec, results = _setup(tmp_path, {"X": TAM, "Z": TAM})
    _write(results / "tarama.csv", "id,piyasa,tf,durum,asama2_aday,neden\nX,ABD25,1D,Hesaplandi,False,PF_1x<1.1\nX,KRIPTO25,5m,Hesaplandi,True,\nX,BIST30,1H,Dogrulanamaz,False,veri_kalitesi:x\nZ,ABD25,1D,Dogrulanamaz,False,piyasa_ozgu:BIST\nZ,KRIPTO25,1D,Dogrulanamaz,False,veri_yok\n")
    _write(results / "asama2a.csv", "id,piyasa,tf,karar,neden\nX,BIST30,1D,Reddedildi (BIST USD),USD kapisi\n")
    row = build_report(spec, results).set_index("id").loc["X"]
    assert (row["nihai_durum"], row["en_iyi_piyasa"], row["en_iyi_tf"]) == ("Bekliyor", "KRIPTO25", "5m")  # the intraday crypto row outranks the daily rejection
    assert "ABD25/1D: Reddedildi" in row["piyasa_ayrintisi"] and "BIST30/1H" in row["piyasa_ayrintisi"]
    z = build_report(spec, results).set_index("id").loc["Z"]
    assert z["nihai_durum"] == "Dogrulanamaz" and "piyasa ozgu" not in z["alt_neden"]  # the informative reason wins


def test_missing_files_are_listed_and_deferred_statuses_are_standard(tmp_path: Path) -> None:
    spec, results = _setup(tmp_path, {"S": "spec_durumu: sadece_short\nozel_kod: true", "K": "spec_durumu: kapsam_disi\nozel_kod: false", "M": TAM,
                                      "AL": "spec_durumu: tam\nozel_kod: false\nalias_of: M"})
    table = build_report(spec, results).set_index("id")
    assert table.loc["S", "alt_neden"].startswith("ertelendi: sadece short") and table.loc["K", "nihai_durum"] == "Kapsam disi"
    assert (table.loc["M", "nihai_durum"], table.loc["M", "alt_neden"]) == ("Bekliyor", "asama1: tarama bekliyor")
    assert table.loc["AL", "alt_neden"].endswith("(alias: M)")  # an alias takes the verdict of its main card
    text = (results / "SONUC.md").read_text(encoding="utf-8")
    assert "Henüz yok: tarama.csv, tarama_rotasyon.csv, asama2a.csv, asama2b.csv, asama2b_pit.csv, codex21.csv, portfoy.md" in text
    assert "## Özet sayılar" in text and "## Önerilen portföy" in text and "## Yöntem özeti" in text
