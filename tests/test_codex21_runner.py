from backtests.run_codex21 import ROWS


def test_complete_codex21_row_catalog() -> None:
    assert list(ROWS) == [f"C{number:02d}" for number in range(1, 22)]
    assert len({config.family for config in ROWS.values()}) == 11


def test_each_row_has_pdf_reference_metrics() -> None:
    for config in ROWS.values():
        assert config.pdf_return > 0
        assert config.pdf_pf > 1
        assert config.pdf_trades >= 30
        assert config.pdf_mdd < 0
