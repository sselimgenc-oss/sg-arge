from datetime import UTC, datetime

import pandas as pd

from copytrade.arsiv import Arsiv


def test_altin_ornek_dolum_tekillesir_ve_yol_zstd(tmp_path):
    archive = Arsiv(tmp_path, datetime(2026, 10, 28, tzinfo=UTC))
    fill = {"adres": "0xabc", "tid": 7, "time": 1}
    assert archive.append("dolum", [fill]) == 1
    assert archive.append("dolum", [fill]) == 0
    files = list((tmp_path / "tur=dolum" / "gun=2026-10-28").glob("*.parquet"))
    assert len(files) == 1
    row = pd.read_parquet(files[0]).iloc[0]
    assert row["sema_surumu"] == 1 and row["alindi_ms"] > 0


def test_altin_ornek_kapsam_bosluk_esigi(tmp_path, monkeypatch):
    monkeypatch.setattr("copytrade.arsiv.load_rules", lambda: {"arsiv_max_bosluk_orani": 0.05})
    archive = Arsiv(tmp_path, datetime(2026, 10, 28, tzinfo=UTC))
    try:
        archive.kapsam({"dolum": 9}, {"dolum": 10})
    except RuntimeError as error:
        assert "boşluk oranı" in str(error)
    else:
        raise AssertionError("%10 boşluk kabul edilmemeli")
