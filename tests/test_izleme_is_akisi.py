"""Saatlik izleme işi hızlı kalır: test paketi PR kontrolünde koşar, izleme işinde koşmaz (kullanıcı kararı 2026-10-29)."""
from pathlib import Path

WORKFLOW = (Path(__file__).resolve().parents[1] / ".github/workflows/izleme.yml").read_text(encoding="utf-8")


def test_izleme_isinde_pytest_adimi_yok():
    assert "pytest" not in WORKFLOW


def test_izleme_adimlari_korundu():
    for step in ("python -m copytrade.izleme_motoru --root . --output izleme", "bash .github/scripts/izleme_yayimla.sh", "git archive FETCH_HEAD izleme"):
        assert step in WORKFLOW
    assert 'cron: "23 * * * *"' in WORKFLOW and "timeout-minutes: 150" in WORKFLOW
