"""U6 runner contracts: every non-runnable translated card remains visible."""

from __future__ import annotations

import pandas as pd
import pytest
import yaml

from backtests import u4, u4_huni, u6, u6_huni


def _write_card(directory, card_id: str, **changes) -> None:
    card = {"id": card_id, "spec_durumu": "tam", "piyasa_kisiti": ["KRIPTO"], "tf": "1D"}
    card.update(changes)
    (directory / f"TV-{card_id}.yaml").write_text(yaml.safe_dump(card), encoding="utf-8")


def test_count_contract_and_unverifiable_report(tmp_path, capsys) -> None:
    spec, output = tmp_path / "spec", tmp_path / "results"
    spec.mkdir()
    _write_card(spec, "OK")
    _write_card(spec, "INCOMPLETE", spec_durumu="eksik")
    _write_card(spec, "NO-MARKET", piyasa_kisiti=["FX"])
    _write_card(spec, "US-4H", piyasa_kisiti=["ABD"], tf="4H")
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(u6, "SPEC", spec)
    try:
        assert u6.main(["--sadece-say", "--results-dir", str(output)]) == 0
    finally:
        monkeypatch.undo()
    assert capsys.readouterr().out.strip() == "OK"
    report = pd.read_csv(output / "dogrulanamaz.csv").set_index("id")["neden"].to_dict()
    assert report == {"INCOMPLETE": "spec_durumu != tam", "NO-MARKET": "piyasa bulunamayan", "US-4H": "ABD25 4H veri yok"}


def test_funnel_uses_fixed_205_trials_in_its_heading(tmp_path) -> None:
    row = {column: float("nan") for column in u4_huni.COLUMNS}
    row.update(varyant="TV-X", kart="TV-X", piyasa="KRIPTO25", tf="4H", karar="Reddedildi", neden="test")
    u4_huni.write_outputs(pd.DataFrame([row]), tmp_path, trials=u6_huni.TRIALS, title="U6")
    heading = (tmp_path / "huni_ozet.md").read_text(encoding="utf-8")
    assert "# U6 huni ozeti" in heading and "DSR deneme sayisi: 205." in heading
    assert u6_huni.TRIALS == 205


def test_locked_period_remains_closed() -> None:
    with pytest.raises(PermissionError):
        u4.lock_check(pd.Timestamp("2025-10-01", tz="UTC"))
