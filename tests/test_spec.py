from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from engine import spec

GOOD = {
    "id": "X1", "ad": "demo", "kaynak": {"dosya": "x", "url": None, "sayfa": None}, "tarz": "swing", "tf": "1D", "mtf": "1W",
    "tf_varsayim": False, "yazar_piyasasi": None,
    "gostergeler": {"ema20": {"f": "ema", "src": "close", "n": 20}, "dmi14": {"f": "dmi", "n": 14}},
    "giris": "cross_over(close, ema20) and dmi14.plus > dmi14.minus",
    "cikis": "close < ema20 or bars_since_entry >= 20",
    "stop": None, "hedef": None, "spec_durumu": "tam", "ozel_kod": False, "belirsiz": [],
}


def write(tmp_path: Path, **overrides):
    card = {**GOOD, **overrides}
    path = tmp_path / f"{card['id']}.yaml"
    path.write_text(yaml.safe_dump(card, allow_unicode=True), encoding="utf-8")
    return path


def result_for(tmp_path, **overrides):
    write(tmp_path, **overrides)
    return spec.validate_directory(tmp_path)[0]


def codes(result):
    return {i.kod for i in result.issues}


def test_valid_card_has_no_issues(tmp_path):
    assert result_for(tmp_path).issues == []


def test_missing_required_field_and_bad_enums(tmp_path):
    card = dict(GOOD)
    del card["giris"]
    (tmp_path / "X1.yaml").write_text(yaml.safe_dump(card), encoding="utf-8")
    result = spec.validate_directory(tmp_path)[0]
    assert "eksik_alan" in codes(result)
    assert "durum" in codes(result_for(tmp_path, spec_durumu="belki"))
    assert "tarz" in codes(result_for(tmp_path, tarz="scalp"))
    assert "tf" in codes(result_for(tmp_path, tf="1h"))
    assert "mtf" in codes(result_for(tmp_path, mtf="haftalik"))


def test_id_must_match_file_name(tmp_path):
    (tmp_path / "other.yaml").write_text(yaml.safe_dump(GOOD), encoding="utf-8")
    assert "id_dosya" in codes(spec.validate_directory(tmp_path)[0])


def test_unparsable_and_unsafe_expressions_flagged(tmp_path):
    assert "ifade_ayristirilamadi" in codes(result_for(tmp_path, giris="close > __import__('os')"))
    assert "ifade_ayristirilamadi" in codes(result_for(tmp_path, cikis="stop: lowest(low,7) ; hedef: x"))


def test_undefined_names_and_fields(tmp_path):
    assert "tanimsiz_ad" in codes(result_for(tmp_path, giris="close > ema50"))
    bad_attr = result_for(tmp_path, giris="dmi14.rsi > 1")
    assert "tanimsiz_alan" in codes(bad_attr)
    plain = result_for(tmp_path, giris="ema20.upper > 1")
    assert "tanimsiz_alan" in codes(plain)


def test_runtime_names_allowed_in_exit_but_not_entry(tmp_path):
    assert result_for(tmp_path, cikis="close < giris_fiyati * 0.95").issues == []
    assert "tanimsiz_ad" in codes(result_for(tmp_path, giris="close > giris_fiyati"))


def test_unknown_indicator_is_error_unless_ozel_kod(tmp_path):
    gost = {"sar": {"f": "sar"}}
    strict = result_for(tmp_path, gostergeler=gost, giris="close > sar", cikis="close < sar")
    assert [i for i in strict.issues if i.kod == "tanimsiz_gosterge"][0].ciddi is True
    lenient = result_for(tmp_path, gostergeler=gost, giris="close > sar", cikis="close < sar", ozel_kod=True)
    assert [i for i in lenient.issues if i.kod == "tanimsiz_gosterge"][0].ciddi is False


def test_tam_requires_expressions(tmp_path):
    assert "tam_bos_ifade" in codes(result_for(tmp_path, giris=None))
    assert "tam_bos_ifade" not in codes(result_for(tmp_path, giris=None, spec_durumu="eksik"))


def test_alias_must_exist(tmp_path):
    assert "alias" in codes(result_for(tmp_path, alias_of="NOPE"))


def test_stop_expression_fields_validated_with_runtime_names(tmp_path):
    ok = result_for(tmp_path, kar_kilidi={"tetik_atr": 1.5, "stop": "giris * 1.002"})
    assert ok.issues == []
    bad = result_for(tmp_path, kar_kilidi={"tetik_atr": 1.5, "stop": "giris * * 2"})
    assert "ifade_ayristirilamadi" in codes(bad)


def test_cards_are_not_modified_and_report_counts(tmp_path):
    path = write(tmp_path, giris="close > ema50")
    before = path.read_bytes()
    results = spec.validate_directory(tmp_path)
    report = spec.render_report(results)
    assert path.read_bytes() == before
    assert "tanimsiz ad" in report or "tanimsiz_ad" in report
    assert "Kart sayisi: 1" in report


def test_main_writes_report_and_exit_code(tmp_path):
    cards, out = tmp_path / "cards", tmp_path / "out" / "rapor.md"
    cards.mkdir()
    write(cards)
    assert spec.main(["--kontrol", str(cards), "--out", str(out)]) == 0
    assert out.exists()
    write(cards, id="X2", giris="close > nowhere")
    assert spec.main(["--kontrol", str(cards), "--out", str(out)]) == 1


def test_non_tam_findings_do_not_fail_the_run(tmp_path):
    cards = tmp_path / "cards"
    cards.mkdir()
    write(cards, id="X3", giris="close > nowhere", spec_durumu="eksik")
    assert spec.main([str(cards)]) == 0


REPO_SPEC = Path(__file__).resolve().parents[1] / "docs" / "spec"


@pytest.mark.skipif(not REPO_SPEC.is_dir(), reason="docs/spec not present")
def test_repository_cards_load_and_report_renders():
    results = spec.validate_directory(REPO_SPEC)
    assert len(results) > 50
    report = spec.render_report(results)
    assert "Durum dagilimi" in report and "Kutuphanede olmayan gosterge adlari" in report


def _synthetic_ohlcv(periods: int = 3000, seed: int = 1):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(seed)
    index = pd.date_range("2022-01-03", periods=periods, freq="h")
    close = 100 + np.cumsum(rng.normal(0, 0.5, periods))
    return pd.DataFrame(
        {
            "open": close + rng.normal(0, 0.1, periods),
            "high": close + rng.uniform(0.1, 1.0, periods),
            "low": close - rng.uniform(0.1, 1.0, periods),
            "close": close,
            "volume": rng.uniform(1_000, 5_000, periods),
        },
        index=index,
    )


@pytest.mark.skipif(not REPO_SPEC.is_dir(), reason="docs/spec not present")
def test_repository_cards_evaluate_on_synthetic_data():
    """Every non-ozel `tam`/`dakikalik` card must not only parse but run: indicators
    compute and giris/cikis evaluate to boolean Series on synthetic OHLCV."""
    import pandas as pd

    from engine import expr, gosterge

    frame = _synthetic_ohlcv()
    benchmarks = {"endeks": _synthetic_ohlcv(seed=2)}
    runtime = {
        "giris": pd.Series(100.0, index=frame.index), "giris_fiyati": pd.Series(100.0, index=frame.index),
        "giris_stop": pd.Series(98.0, index=frame.index), "giris_hedef": pd.Series(104.0, index=frame.index),
        "bars_since_entry": pd.Series(3.0, index=frame.index), "stop_mesafesi": pd.Series(2.0, index=frame.index),
        "giris_modu": "A",
    }
    failures = []
    checked = 0
    for result in spec.validate_directory(REPO_SPEC):
        card = result.card
        if card.get("spec_durumu") not in ("tam", "dakikalik") or card.get("ozel_kod"):
            continue
        if not (card.get("giris") or card.get("cikis")):
            continue
        try:
            env = gosterge.build_env(frame, card["gostergeler"], benchmarks=benchmarks)
            env.update(runtime)
            for key in ("giris", "cikis"):
                if card.get(key):
                    out = expr.parse(card[key]).evaluate(env, index=frame.index, mtf=lambda tf, s: s)
                    assert out.dtype == bool, f"{key} bool degil: {out.dtype}"
            checked += 1
        except Exception as exc:  # noqa: BLE001 - collect every failing card
            failures.append(f"{result.id}: {type(exc).__name__}: {exc}")
    assert checked >= 15
    assert not failures, "calismayan kartlar:\n" + "\n".join(failures)
