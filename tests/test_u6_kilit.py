from __future__ import annotations

import pandas as pd
import pytest

from backtests import u6_kilit


def _row(variant: str, karar: str, sharpe: float, dsr: float = .96, **changes) -> dict:
    row = {"varyant": variant, "karar": karar, "oos_sharpe": sharpe, "dsr": dsr,
           "is_islem": 40, "is_PF": 1.1, "null_gecti": True, "oos_ortR": .1,
           "oos_PF_2x": 1.3, "oos_net_3x": .1, "net_gecikme": .1, "mdd_p95": .1,
           "piyasa": "ABD25", "en_iyi_ay_haric_pf": 1.1, "on_net": .1}
    row.update(changes)
    return row


def test_candidate_order_limit_and_dsr_only_fallback() -> None:
    table = pd.DataFrame([
        _row("conditional", "Kosullu", .9), _row("passed-low", "Gecti", .2), _row("passed-high", "Gecti", .8),
        _row("dsr-only", "Reddedildi", .0, dsr=.4), _row("fails-other", "Reddedildi", .0, dsr=.99, oos_net_3x=-.1),
    ])
    chosen = u6_kilit.select_candidates(table, maximum=4)
    assert list(chosen["varyant"]) == ["passed-high", "passed-low", "conditional", "dsr-only"]


def test_retired_locked_command_has_no_environment_guard(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.delenv("KILIT_AC", raising=False)
    with pytest.raises(FileNotFoundError):
        u6_kilit.main(["--results-dir", str(tmp_path)])


def test_locked_command_rejects_a_selected_card_that_is_no_longer_runnable(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    pd.DataFrame([_row("TV-MISSING", "Gecti", 1.0)]).to_csv(tmp_path / "huni_ozet.csv", index=False)
    monkeypatch.setenv("KILIT_AC", "1")
    monkeypatch.setattr(u6_kilit.u6, "all_variants", lambda: [])
    with pytest.raises(ValueError, match="TV-MISSING"):
        u6_kilit.main(["--results-dir", str(tmp_path)])


@pytest.mark.parametrize(("metrics", "expected"), [
    ({"net_2x": .001, "PF_2x": 1.1, "mdd": -.15}, True),
    ({"net_2x": .1, "PF_2x": 1.2, "mdd": -.16}, False),  # calculate_metrics sign: a 16% drawdown is -0.16
    ({"net_2x": 0, "PF_2x": 1.2, "mdd": -.1}, False),
    ({"net_2x": .1, "PF_2x": 1.09, "mdd": -.1}, False),
])
def test_locked_pass_rule(metrics, expected) -> None:
    assert u6_kilit.passes_locked(metrics) is expected
