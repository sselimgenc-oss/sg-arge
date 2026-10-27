"""Akıl sağlığı kapısı (görev 18d), kopya_eksik (18a), dolum_siniri (18c) ve ölü sütunlar (18b). Ağsız."""
from __future__ import annotations

import pandas as pd
import pytest

from copytrade.kapi import SanityError, fill_limit_reached, gate_status, load_rules, merge_shards, sanity_check

RULES = load_rules()
DAY_MS = 86_400_000


def good_row(address="0xa", **over):
    row = {"address": address, "asama1": "Geçti", "adim1": "Geçti", "adim2": "Geçti", "adim3": "Geçti", "adim4": "Geçti",
           "profitable_month_ratio": .6, "max_drawdown": .2, "largest_trade_share": .1, "kisa_islem_payi": .1, "gece_payi": .3,
           "pay_kripto": 1.0, "candle_coverage": 1.0, "plasebo_p": .01, "closed_trades": 80, "history_days": 200,
           "median_holding_hours": 5, "median_leverage": 2.0, "max_leverage": 8.0, "gecikme_30dk_net": .1, "gecikme_120dk_net": .05, "tarz": "intraday"}
    return {**row, **over}


def table(*rows):
    return pd.DataFrame(list(rows))


def test_good_table_passes():
    assert sanity_check(table(good_row("0xa"), good_row("0xb")), RULES) == []


@pytest.mark.parametrize("column,value", [("max_drawdown", 1.5e12), ("max_drawdown", -0.1), ("profitable_month_ratio", 1.2), ("plasebo_p", 2)])
def test_ratio_outside_0_1_fails(column, value):
    problems = sanity_check(table(good_row(**{column: value})), RULES)
    assert any(p.startswith(column) for p in problems)


@pytest.mark.parametrize("value", [201, -1])
def test_leverage_outside_range_fails(value):
    assert any(p.startswith("max_leverage") for p in sanity_check(table(good_row(max_leverage=value)), RULES))


def test_empty_column_fails():
    assert any(p.startswith("median_leverage") and "boş" in p for p in sanity_check(table(good_row(median_leverage=None)), RULES))


def test_constant_column_fails_only_with_enough_rows():
    rows = [good_row(f"0x{i}", max_leverage=5.0) for i in range(int(RULES["saglik_min_satir_sabit_kontrolu"]))]
    assert any(p.startswith("max_leverage") and "sabit" in p for p in sanity_check(table(*rows), RULES))
    assert sanity_check(table(*rows[:3]), RULES) == []      # az satırda sabitlik kontrol edilmez


def test_family_member_without_placebo_fails():
    problems = sanity_check(table(good_row(plasebo_p=None)), RULES)
    assert any(p.startswith("plasebo_p") for p in problems)
    # adım 4'ü geçemeyen satırda plasebo_p boş olabilir
    assert not any(p.startswith("plasebo_p") for p in sanity_check(table(good_row(), good_row("0xb", adim4="Kaldı", plasebo_p=None)), RULES))


def test_merge_refuses_to_publish_on_sanity_failure(tmp_path):
    shard = tmp_path / "shards" / "2026-10-20"
    shard.mkdir(parents=True)
    pd.DataFrame([good_row(max_drawdown=3.0)]).to_csv(shard / "sonuc.csv", index=False)
    root = tmp_path / "out"
    with pytest.raises(SanityError, match="max_drawdown"):
        merge_shards(tmp_path / "shards", root)
    assert not (root / "kapi" / "2026-10-20" / "sonuc.csv").exists()


def base_metrics(**over):
    return {"complete_data": True, "history_days": 200, "closed_trades": 80, "active_months": 8, "median_holding_hours": 3,
            "median_leverage": 2, "max_leverage": 8, "kisa_islem_payi": .25, "profitable_month_ratio": .7, "largest_trade_share": .2,
            "profit_factor_without_best": 1.5, "martingale_signal": False, **over}


def test_missing_copy_fills_make_step3_insufficient_but_static_failure_stays_failed():
    assert gate_status(base_metrics(), .1, None, None, RULES)["adim3"] == "Geçti"
    assert gate_status(base_metrics(kopya_eksik=True), .1, None, None, RULES)["adim3"] == "Yetersiz"
    assert gate_status(base_metrics(kopya_eksik=True, median_leverage=9), .1, None, None, RULES)["adim3"] == "Kaldı"


def test_fill_limit_flag():
    now, start = 400 * DAY_MS, 35 * DAY_MS
    limit = int(RULES["dolum_siniri"])
    make = lambda first_day: [{"time": first_day * DAY_MS + i} for i in range(limit)]
    assert not fill_limit_reached(make(100)[:-1], now, start, None, RULES)                     # sınıra ulaşmadı
    assert fill_limit_reached(make(300), now, start, {"account_age_days": 500}, RULES)         # 365 günlük pencerenin çok gerisinde başlıyor
    assert not fill_limit_reached(make(40), now, start, {"account_age_days": 500}, RULES)      # pencerenin başına yakın: kayıp yok
    assert not fill_limit_reached(make(300), now, start, {"account_age_days": 100}, RULES)     # hesap zaten genç


def test_dead_columns_not_in_evaluated_row():
    import inspect
    from copytrade import kapi
    source = inspect.getsource(kapi.evaluate_address)
    assert "liquid_coin_share" in source and "pop" in source      # satırdan atılıyor


def test_error_rate_over_limit_turns_gate_red():
    rows = [good_row(f"0x{i}") for i in range(19)] + [good_row("0xbad", hata="IndexError: x", asama1="Yetersiz")]
    assert sanity_check(table(*rows), RULES) == []            # 1/20 = %5 sınırda geçer
    rows += [good_row("0xbad2", hata="KeyError: y", asama1="Yetersiz")]
    assert any(p.startswith("hata:") for p in sanity_check(table(*rows), RULES))


def test_single_address_error_does_not_kill_the_shard(monkeypatch):
    import copytrade.kapi as kapi

    def boom(*a, **k):
        raise IndexError("single positional indexer is out-of-bounds")

    class Client:
        requests = 0
        def portfolio(self, address): return boom()

    class Cache:
        requests = 0

    from datetime import datetime, timezone
    row = kapi.evaluate_address({"address": "0xabc", "accountValue": 1000.0}, Client(), Cache(), datetime.now(timezone.utc), 0, 0, None, RULES)
    assert row["sinif"] == "Yetersiz" and row["hata"].startswith("IndexError") and row["neden"].startswith("veri hatası")


def test_ratio_float_noise_within_tolerance_passes_but_real_excess_fails():
    assert sanity_check(table(good_row(pay_kripto=1.0000000000000002)), RULES) == []
    assert sanity_check(table(good_row(pay_kripto=1.0000001)), RULES) != []


def test_net_return_outside_minus1_to_100_fails_the_gate():
    for column, value in (("gecikme_30dk_net", -2.7e6), ("gecikme_120dk_net", 101.0), ("alfa_yillik", -3.3e6)):
        assert any(p.startswith(column) for p in sanity_check(table(good_row(**{column: value})), RULES)), column
    assert sanity_check(table(good_row(gecikme_30dk_net=-1.0, gecikme_120dk_net=100.0)), RULES) == []     # sınırlar dahil


def test_check_net_range_turns_an_implausible_copy_into_a_row_error():
    from copytrade.kapi import check_net_range
    check_net_range({30: 0.2, 120: None}, RULES)
    with pytest.raises(ValueError, match="makul aralık"):
        check_net_range({30: -2.7e6}, RULES)


def test_any_fully_empty_column_fails_unless_listed_as_optional():
    """Eski kapı yalnız EXPECTED_FILLED listesindeki sütunlara bakıyordu; binance_payi / setting_leverage / liquid_coin_share listede olmadığı için
    tamamen boş kalıp yayımlandı. Şimdi listede olmayan her boş sütun kapıyı kırar; isteğe bağlılar `saglik_bos_olabilir`."""
    for column in ("binance_payi", "setting_leverage", "liquid_coin_share"):
        problems = sanity_check(table(good_row(**{column: None}), good_row("0xb", **{column: None})), RULES)
        assert any(p.startswith(column) and "tamamen boş" in p for p in problems), column
    assert sanity_check(table(good_row(plasebo_hata=None), good_row("0xb", plasebo_hata=None)), RULES) == []


def test_every_non_passing_row_must_have_a_reason():
    rows = [good_row("0xa", sinif="Kaldı", neden="adım 3 Kaldı: x"), good_row("0xb", sinif="Yetersiz", neden=None), good_row("0xc", sinif="Geçti", neden=None)]
    assert any(p.startswith("neden:") and "1 satırda" in p for p in sanity_check(table(*rows), RULES))


def test_fail_reason_names_the_first_failing_step_golden():
    """Run 21'de neden 92 satırda boştu. 8bae: adım 1–2 geçti, adım 3 Yetersiz — statik şartlar tutuyor (swing, medyan kaldıraç 1,2x, en yüksek 4x),
    ama tarzın gecikmesinde mum bulunamayan dolum var (kopya_eksik) → "adım 3 Yetersiz: kopya eksik dolum (mum yok)". Diğer adımlar için de ilk düşen adım."""
    from copytrade.kapi import fail_reason, finalize
    base = good_row("0x8bae", adim3="Yetersiz", kopya_eksik=True, tarz="swing", median_leverage=1.2, max_leverage=4.0, kisa_islem_payi=0.05, sinif=None)
    rows = [base,
            good_row("0xb", adim3="Kaldı", tarz="swing", median_leverage=4.5, max_leverage=4.0, kisa_islem_payi=0.05),
            good_row("0xc", adim3="Kaldı", tarz="swing", median_leverage=1.0, max_leverage=4.0, kisa_islem_payi=0.05, kapi_gecikme_dk=120, gecikme_120dk_net=-0.02),
            good_row("0xd", adim4="Kaldı", profitable_month_ratio=0.40, largest_trade_share=0.1, profit_factor_without_best=2.0),
            good_row("0xe", asama1="Yetersiz", max_drawdown=0.45, profitable_month_ratio=0.6, active_months=12, return_12m=0.5),
            good_row("0xf", adim5="Kaldı", plasebo_p=0.2)]
    out = finalize(pd.DataFrame(rows), RULES).set_index("address")
    assert out.loc["0x8bae", "neden"] == "adım 3 Yetersiz: kopya eksik dolum (mum yok)"
    assert out.loc["0xb", "neden"] == "adım 3 Kaldı: medyan kaldıraç 4.5 > 3.0"
    assert out.loc["0xc", "neden"] == "adım 3 Kaldı: kopya neti 120 dk gecikmede -0.02 ≤ 0"
    assert out.loc["0xd", "neden"] == "adım 4 Kaldı: kârlı ay %40 < %49"
    assert out.loc["0xe", "neden"] == "1. aşama Yetersiz: düşüş %45 > %30"
    assert out.loc["0xf", "neden"] == "adım 5 Kaldı: plasebo p 0.2 > 0.05"
    assert fail_reason(good_row("0xg", adim5="Geçti", adim6="Geçti", adim7="Geçti"), RULES) == ""      # her şeyi geçen satır için neden yok
