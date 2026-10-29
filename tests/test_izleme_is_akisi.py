"""Saatlik izleme işi hızlı kalır: test paketi PR kontrolünde koşar, izleme işinde koşmaz (kullanıcı kararı 2026-10-29)."""
from pathlib import Path

WORKFLOW = (Path(__file__).resolve().parents[1] / ".github/workflows/izleme.yml").read_text(encoding="utf-8")


def test_izleme_isinde_pytest_adimi_yok():
    assert "pytest" not in WORKFLOW


def test_izleme_adimlari_korundu():
    for step in ("python -m copytrade.izleme_motoru --root . --output izleme", "bash .github/scripts/izleme_yayimla.sh", "git archive FETCH_HEAD izleme"):
        assert step in WORKFLOW
    assert 'cron: "23 * * * *"' in WORKFLOW and "timeout-minutes: 150" in WORKFLOW


def test_motor_durumu_r2de_tutulur_veri_dalina_yazilmaz():
    """motor.json 61 trader'da ~270 MB (GitHub 100 MB sınırı): R2'den indirilir, R2'ye yüklenir, veri dalına eklenmez."""
    script = (Path(__file__).resolve().parents[1] / ".github/scripts/izleme_yayimla.sh").read_text(encoding="utf-8")
    assert "izleme/motor.json.gz" in WORKFLOW and WORKFLOW.count("R2_BUCKET: ${{ secrets.R2_BUCKET }}") == 2
    assert WORKFLOW.index("Motor durumunu R2'den indir") < WORKFLOW.index("copytrade.izleme_motoru") < WORKFLOW.index("Motor durumunu R2'ye yükle") < WORKFLOW.index("izleme_yayimla.sh")
    assert "for path in durum.json binance_vadeli.txt kararlar.jsonl degisim.json" in script and "94371840" in script
