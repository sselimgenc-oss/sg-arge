"""Eksik koşu (görev 24) ve dış adaylar (görev 16). Ağsız."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from copytrade.kapi import build_universe, external_candidates, load_rules, merge_shards, run_status

RULES = load_rules()
A, B, C = "0x" + "a" * 40, "0x" + "b" * 40, "0x" + "c" * 40
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "copytrade_kapi.yml"


def board_row(address, value, pnl):
    return {"ethAddress": address, "accountValue": str(value), "windowPerformances": [["allTime", {"pnl": str(pnl), "roi": "1", "vlm": "1"}]]}


class FakeClient:
    def __init__(self, value=None): self.value, self.calls = value, []
    def info(self, payload, weight=20):
        self.calls.append(payload)
        if self.value is None: raise KeyError("yok")
        return {"marginSummary": {"accountValue": str(self.value)}}


def test_external_candidates_are_unique_lowercase_addresses_from_all_files(tmp_path):
    (tmp_path / "x.md").write_text(f"- {A.upper().replace('0X', '0x')} ve {B}\nkısa 0x1234 değil")
    (tmp_path / "y.txt").write_text(f"{A} {C}")
    assert external_candidates(tmp_path) == sorted([A, B, C]) and external_candidates(tmp_path / "yok") == []
    assert len(external_candidates()) > 50      # gerçek bağımsız seçim notları


def test_universe_marks_external_and_bypasses_prefilter():
    board = [board_row(A, 500_000, 10), board_row(B, 100, 5), board_row(C, 900_000, -5)]        # B çok küçük, C zararda
    universe = {row["address"]: row for row in build_universe(board, [B, C, "0x" + "d" * 40], FakeClient(value=1234))}
    assert universe[A]["kaynak"] == "leaderboard"
    assert universe[B]["kaynak"] == "dis_aday" and universe[B]["accountValue"] == 100        # süzgeçe takılsa da girer, değer lider tablosundan
    assert universe[C]["kaynak"] == "dis_aday"
    assert universe["0x" + "d" * 40]["accountValue"] == 1234                                  # lider tablosunda yok → clearinghouseState
    assert len(universe) == 4
    assert build_universe(board, [A], None)[0]["kaynak"] == "dis_aday"                         # süzgeçten geçen de dış adaysa işaretlenir
    assert build_universe([], [A], FakeClient())[0]["accountValue"] == 0.0                     # değer alınamazsa 0


def test_run_status_incomplete_when_shard_missing_or_coverage_low():
    assert run_status(32, 32, 985, 1000, "tam", RULES)["durum"] == "tamam"
    missing = run_status(31, 32, 990, 1000, "tam", RULES)
    assert missing["durum"] == "eksik" and "31" in missing["neden"]
    low = run_status(32, 32, 100, 1000, "tam", RULES)
    assert low["durum"] == "eksik" and "kapsam" in low["neden"]
    assert run_status(24, 24, 40, 1000, "hizli", RULES)["durum"] == "tamam"                    # hızlı koşu evrenin tamamını işlemez


def make_shard(base: Path, index: int, address: str, finished: bool):
    folder = base / f"stage1-{index}" / "2026-10-28"
    folder.mkdir(parents=True)
    row = {"address": address, "asama1": "Yetersiz"}
    pd.DataFrame([row]).to_csv(folder / "sonuc.csv", index=False)
    (folder / "evren.json").write_text(json.dumps({"evren": 2}))
    if finished:
        (folder / "bitti.json").write_text("{}")


def test_merge_publishes_incomplete_run_as_eksik(tmp_path):
    make_shard(tmp_path / "shards", 0, "0xa", True)
    make_shard(tmp_path / "shards", 1, "0xb", False)         # zaman aşımı: bitti.json yok
    statuses = merge_shards(tmp_path / "shards", tmp_path / "root", 2, "tam")
    day = tmp_path / "root" / "kapi" / "2026-10-28"
    durum = json.loads((day / "durum.json").read_text())
    assert statuses["2026-10-28"]["durum"] == "eksik" and durum["durum"] == "eksik" and durum["parca_biten"] == 1 and durum["parca_beklenen"] == 2
    assert "DURUM: EKSİK" in (day / "RAPOR.md").read_text(encoding="utf-8")
    assert sorted(pd.read_csv(day / "sonuc.csv").address) == ["0xa", "0xb"]         # sonuç yine de yayımlanır


def test_merge_complete_run_is_tamam(tmp_path):
    make_shard(tmp_path / "shards", 0, "0xa", True)
    make_shard(tmp_path / "shards", 1, "0xb", True)
    assert merge_shards(tmp_path / "shards", tmp_path / "root", 2, "tam")["2026-10-28"]["durum"] == "tamam"
    assert "DURUM: EKSİK" not in (tmp_path / "root" / "kapi" / "2026-10-28" / "RAPOR.md").read_text(encoding="utf-8")


def test_workflow_does_not_hide_errors_and_skips_kesif_when_incomplete():
    text = WORKFLOW.read_text(encoding="utf-8")
    kapi_line = next(line for line in text.splitlines() if "python -m copytrade.kapi --root copytrade --shard-index" in line)
    assert "|| true" not in kapi_line and "continue-on-error" not in text
    assert re.search(r"if: steps\.birlestir\.outputs\.durum == 'tamam'.*\n\s+run: python -m copytrade\.kesif", text)
    assert "durum == 'eksik'" in text and "exit 1" in text
