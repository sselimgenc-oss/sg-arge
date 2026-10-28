"""GitHub Actions iş akışları commit edilmeden önce geçerli YAML olmalı."""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_all_workflows_load_as_yaml():
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    assert workflows, "İş akışı bulunamadı"
    for workflow in workflows:
        with workflow.open(encoding="utf-8") as handle:
            assert isinstance(yaml.safe_load(handle), dict), workflow
