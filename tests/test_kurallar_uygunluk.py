"""Tek kural kaynağı ve uygunluk (görev 23): görev belgesindeki kullanıcı kararları ile kurallar.yaml aynı; kodda karar eşiği yok."""
from __future__ import annotations

import ast
from collections import Counter
import re
from pathlib import Path

import pytest

from copytrade.kurallar import load_rules

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/GOREV_TRADER_SECIMI.md").read_text(encoding="utf-8")
RULES = load_rules()


def grab(pattern: str) -> tuple[str, ...]:
    found = re.search(pattern, DOC, re.S)
    assert found, f"görev belgesinde bulunamadı (belge değiştiyse bu test bilerek gözden geçirilmeli): {pattern}"
    return found.groups()


def test_user_decisions_in_the_task_document_equal_kurallar_yaml():
    scalp, swing = grab(r"\| Medyan elde tutma \| 1–(\d+) saat \| ≥ (\d+) saat")[0], grab(r"≥ (\d+) saat \|")[0]
    assert RULES["tarz_scalp_alti_saat"] == 1.0 and RULES["tarz_swing_ustu_saat"] == float(swing) == float(scalp)
    share, intraday, swing_h = grab(r"kısa işlem payı ≤ %(\d+) \| < (\d+) dk süren işlemler \| < (\d+) saat süren")
    assert RULES["kisa_islem_payi_max"] == int(share) / 100
    assert RULES["kisa_islem_dk"] == {"intraday": int(intraday), "swing": int(swing_h) * 60}
    d_in, d_sw = grab(r"Adım 3 gecikme testi[^|]*\| (\d+) dk \| (\d+) saat")
    assert RULES["kopya_gecikme_dk"] == {"intraday": int(d_in), "swing": int(d_sw) * 60}
    s_in, s_sw = grab(r"Raporlanan stres gecikmesi[^|]*\| (\d+) saat \| (\d+) saat")
    assert RULES["stres_gecikme_dk"] == {"intraday": int(s_in) * 60, "swing": int(s_sw) * 60}
    median, maximum = grab(r"Kaldıraç kuralları aynı \(medyan ≤ (\d+)x, en fazla ≤ (\d+)x\)")
    assert (RULES["kapi_max_medyan_kaldirac"], RULES["kapi_max_kaldirac"]) == (float(median), float(maximum))
    history, young = grab(r"Geçmiş ≥ (\d+) gün aynı; ≥ (\d+) gün olanlar")
    assert (RULES["min_history_days"], RULES["genc_aday_gun"]) == (int(history), int(young))
    assert RULES["alfa_kripto_payi_esigi"] == int(grab(r"işlem hacminin ≥ %(\d+)'si kripto")[0]) / 100


def test_numbered_user_decisions_10_11_14():
    assert RULES["plasebo_tekrar"] == int(grab(r"Plasebo ([\d.]+) tekrar")[0].replace(".", ""))
    window, intraday, swing, last = grab(r"son (\d+) günde kapanmış düz-düz döngü \(dolum değil\) intraday ≥ (\d+),\s+swing ≥ (\d+); son işlem ≤ (\d+) gün")
    assert RULES["aktif_pencere_gun"] == int(window)
    assert RULES["aktif_son90_dongu"] == {"intraday": int(intraday), "swing": int(swing)}
    assert RULES["aktif_son_islem_max_gun"] == int(last)
    first, fourth = grab(r"1\. aşama ≥ %(\d+), adım 4 ≥ %(\d+)")
    assert RULES["asama1_min_karli_ay_orani"] == int(first) / 100 and RULES["adim4_min_karli_ay_orani"] == int(fourth) / 100


def test_kurallar_yaml_ust_duzey_anahtarlari_yinelenmez():
    """YAML yükleyicisi son anahtarı sessizce ezdiği için ham metni de denetler."""
    keys = [line.split(":", 1)[0].strip() for line in (ROOT / "copytrade/kurallar.yaml").read_text(encoding="utf-8").splitlines()
            if line and not line[0].isspace() and not line.startswith("#") and ":" in line]
    duplicate = sorted(key for key, count in Counter(keys).items() if count > 1)
    assert not duplicate, f"kurallar.yaml yinelenen üst düzey anahtarlar: {', '.join(duplicate)}"


def test_numbered_user_decision_27_account_floor():
    shown, key, literal = grab(r"\*\*≥ ([\d.]+) \$\*\* değilse Kaldı.*?`(hesap_degeri_min_usd): (\d+)`")
    assert RULES[key] == int(literal) == int(shown.replace(".", ""))


def test_account_floor_boundary_0_9999_fail_10000_pass():
    from copytrade.kapi import account_floor_pass
    assert not account_floor_pass(0.0, RULES) and not account_floor_pass(9999.0, RULES) and account_floor_pass(10000.0, RULES)


def test_gate_functions_use_the_yaml_thresholds_at_the_boundary():
    from copytrade.kapi import gate_status, stage1_pass
    stats = {"active_months": 6, "profitable_month_ratio": 0.44, "max_drawdown": 0.30, "return_12m": 0.01}
    assert stage1_pass(stats, RULES) and not stage1_pass({**stats, "profitable_month_ratio": 0.4399}, RULES)
    assert not stage1_pass({**stats, "max_drawdown": 0.3001}, RULES) and not stage1_pass({**stats, "active_months": 5}, RULES)
    metrics = {"complete_data": True, "history_days": 180, "closed_trades": 50, "active_months": 6, "median_holding_hours": 3, "median_leverage": 2,
               "max_leverage": 8, "profitable_month_ratio": 0.49, "largest_trade_share": 0.29, "profit_factor_without_best": 1.21, "martingale_signal": False}
    assert gate_status(metrics, 0.1, 0.05, {"alfa_yillik": 1, "nw_t": 2.0}, RULES)["adim4"] == "Geçti"
    assert gate_status({**metrics, "profitable_month_ratio": 0.4899}, 0.1, 0.05, None, RULES)["adim4"] == "Kaldı"


# Karar eşikleri koda gömülmez: karşılaştırmalarda "anlamlı" sayı sabiti yok (0, 1, işaret ve sayısal epsilon hariç)
ALLOWED = {0, 1, -1, 2, 100}
ALLOWED_BY_FILE = {"kesif.py": {3, 4, 5, 6, 7}}     # kesif.step_reasons: adım numaraları (eşik değil)
CHECKED = ["kapi.py", "defter.py", "kesif.py", "olcut.py"]


def numeric_comparisons(path: Path):
    allowed = ALLOWED | ALLOWED_BY_FILE.get(path.name, set())
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for side in [node.left, *node.comparators]:
                if isinstance(side, ast.Constant) and isinstance(side.value, (int, float)) and not isinstance(side.value, bool):
                    value = side.value
                    if abs(value) < 1e-9 or value in allowed:
                        continue
                    yield node.lineno, value


@pytest.mark.parametrize("name", CHECKED)
def test_no_decision_threshold_literals_in_code(name):
    found = list(numeric_comparisons(ROOT / "copytrade" / name))
    assert not found, f"{name}: karşılaştırmada sayı sabiti (eşik kurallar.yaml'da olmalı): {found}"


def test_freeze_summary_hashes_rules_and_code_and_candidate_list():
    import hashlib
    import pandas as pd
    from copytrade.kapi import FREEZE_FILES, freeze_report, freeze_summary
    table = pd.DataFrame({"address": ["0xB", "0xa", "0xc"], "katman": ["izleme_adayi", "kopyalanabilir", "yok"]})
    summary = freeze_summary(table)
    assert set(summary["dosyalar"]) == set(FREEZE_FILES) == {"kurallar.yaml", "kapi.py", "olcut.py", "defter.py"}
    assert summary["dosyalar"]["kurallar.yaml"] == hashlib.sha256((ROOT / "copytrade/kurallar.yaml").read_bytes()).hexdigest()
    assert summary["aday_sayisi"] == 2 and summary["aday_ozeti"] == hashlib.sha256(b"0xa\n0xb").hexdigest()     # sıralı, küçük harf
    assert freeze_summary(table.iloc[::-1]) == summary                                     # sıra özeti değiştirmez
    assert freeze_summary(table.assign(katman=["yok", "kopyalanabilir", "yok"]))["aday_ozeti"] != summary["aday_ozeti"]
    assert "kurallar.yaml" in freeze_report(table) and "Aday listesi (2 adres" in freeze_report(table)
