import pandas as pd
import pytest

from backtests import u7_ozet


def test_v2_decision_keeps_old_funnel_as_information(tmp_path) -> None:
    group = tmp_path / "u4"
    group.mkdir()
    pd.DataFrame([
        {"varyant": "win", "karar": "Reddedildi", "neden": "eski", "oos_net_1x": .01, "oos_islem_hafta": 9},
        {"varyant": "loss", "karar": "Gecti", "neden": "eski", "oos_net_1x": -.01, "oos_islem_hafta": 12},
    ]).to_csv(group / "huni_ozet.csv", index=False)

    output = u7_ozet.build({"u4": group / "huni_ozet.csv"}, tmp_path / "huni_ozet.csv")

    assert output.loc[0, "aile_etiketi"] == "tarih_belirsiz"
    assert output.loc[0, "eski_huni_karari"] == "Reddedildi"
    assert output.loc[0, "adim0"] == "ceviri_testleri"
    assert output.loc[0, "karar_adim2"] == "İzle"  # watch has priority over positive OOS net
    assert bool(output.loc[0, "izle_listesi"])
    assert output.loc[1, "karar_adim2"] == "Kaldı"
    assert output.loc[1, "koruma_listesi"] == "degerlendirilecek"


def test_missing_v2_column_is_an_error(tmp_path) -> None:
    source = tmp_path / "u4.csv"
    pd.DataFrame([{"varyant": "bad", "oos_net_1x": .1}]).to_csv(source, index=False)

    with pytest.raises(ValueError, match="oos_islem_hafta"):
        u7_ozet.build({"u4": source}, tmp_path / "out.csv")
