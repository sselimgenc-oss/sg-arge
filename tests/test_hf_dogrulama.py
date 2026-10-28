"""HF doğrulama: saf hesaplar (elle hesaplanmış altın örnekler) + yerel hive-bölümlü parquet üzerinde DuckDB sorguları."""
import json
from pathlib import Path

import pandas as pd
import pytest

from copytrade import hf_dogrulama as hf

A, B, C = "0x" + "a" * 40, "0x" + "b" * 40, "0x" + "c" * 40


def test_tarih_yolu():
    assert hf.tarih_yolu(hf.BASE, "account_values", "2025-08-09") == \
        "hf://datasets/ProbioticFarmer/hyperliquid-augmented-copytrading/account_values/date=2025-08-09/*.parquet"
    assert hf.tarih_yolu("/x", "fills") == "/x/fills/date=*/*.parquet"


def test_tarih_bolumleri_ve_bosluklar():
    names = ["account_values/date=2025-08-03", "account_values/date=2025-08-01", "account_values/readme.md", "date=2025-08-01", "date=2025-8-9"]
    assert hf.tarih_bolumleri(names) == ["2025-08-01", "2025-08-03"]
    # 1 Ağustos .. 6 Ağustos arasında 2, 3(var), 4, 5 → eksik: 2, 4, 5
    assert hf.bosluklar(["2025-08-01", "2025-08-03", "2025-08-06"]) == ["2025-08-02", "2025-08-04", "2025-08-05"]
    assert hf.bosluklar(["2025-08-01", "2025-08-02"]) == [] and hf.bosluklar(["2025-08-01"]) == [] and hf.bosluklar([]) == []
    assert hf.bosluklar(["2025-02-27", "2025-03-02"]) == ["2025-02-28", "2025-03-01"]          # ay sonu, 2025 artık yıl değil


def test_goreli_fark_ve_ozet():
    assert hf.goreli_fark(110, 100) == pytest.approx(0.10) and hf.goreli_fark(95, 100) == pytest.approx(0.05)
    assert hf.goreli_fark(5, 0) is None and hf.goreli_fark(90, -100) == pytest.approx(1.9)       # |90 − (−100)| / 100
    # (110,100)→0,10  (95,100)→0,05  (100,100)→0  (7,0)→tanımsız;  min 0, medyan 0,05, max 0,10
    summary = hf.fark_ozeti([(110, 100), (95, 100), (100, 100), (7, 0)])
    assert summary["n"] == 3 and summary["ref_sifir"] == 1
    assert (summary["min"], summary["max"]) == (0.0, pytest.approx(0.10)) and summary["medyan"] == pytest.approx(0.05)
    assert hf.fark_ozeti([])["medyan"] is None


def test_en_yakin_ve_tarihler():
    history = [[1000, 10.0], [5000, 50.0], [9000, 90.0]]
    assert hf.en_yakin(history, 4000) == (50.0, 1000) and hf.en_yakin(history, 7000) == (50.0, 2000)       # eşit uzaklıkta erken nokta
    assert hf.en_yakin([], 1) is None
    every = ["2025-08-01", "2025-08-02", "2025-10-01", "2025-10-31"]
    # hedefler 10-01 (30 gün), 08-02 (90 gün), 05-04 (180 gün → en yakın mevcut: 08-01)
    assert hf.gecmis_tarihler("2025-10-31", every) == ["2025-10-01", "2025-08-02", "2025-08-01"]
    assert hf.gecmis_tarihler("2025-10-31", ["2025-10-31", "2025-10-01"]) == ["2025-10-01"]                  # tekrarlar atılır, en son gün hariç
    assert hf.gecmis_tarihler("2025-10-31", ["2025-10-31"]) == []
    assert hf.gun_ms("1970-01-02") == 86_400_000 + 43_200_000


def test_ledger_adaylari():
    columns = {"account_values": [{"ad": "user", "tur": "VARCHAR"}, {"ad": "account_value", "tur": "DOUBLE"}],
               "ledger_updates": [{"ad": "user", "tur": "VARCHAR"}, {"ad": "usdc_deposit", "tur": "DOUBLE"}],
               "fills": [{"ad": "transfer_flag", "tur": "BOOLEAN"}]}
    assert hf.ledger_adaylari(columns) == {"ledger_updates": ["usdc_deposit"], "fills": ["transfer_flag"]}
    assert hf.ledger_adaylari({"account_values": columns["account_values"]}) == {}


def hive(tmp_path: Path) -> Path:
    """2025-08-01 (A:100+50 iki dex, B:200), 2025-08-03 (A:120, B:210, C:5); 2025-08-02 yok."""
    frames = {"2025-08-01": [(A.upper().replace("0X", "0x"), "", "USDC", 100.0), (A, "xyz", "USDC", 50.0), (B, "", "USDC", 200.0)],
              "2025-08-03": [(A, "", "USDC", 120.0), (B, "", "USDC", 210.0), (C, "", "USDC", 5.0)]}
    for day, rows in frames.items():
        folder = tmp_path / "account_values" / f"date={day}"
        folder.mkdir(parents=True)
        pd.DataFrame(rows, columns=["user", "dex", "collateral_token", "account_value"]).to_parquet(folder / "0.parquet")
    return tmp_path


def test_duckdb_kapsam_satir_ve_degerler(tmp_path: Path):
    base = str(hive(tmp_path))
    con = hf.baglan()
    glob = hf.tarih_yolu(base, "account_values")
    assert hf.gunluk_kapsam(con, glob) == [{"gun": "2025-08-01", "satir": 3, "adres": 2}, {"gun": "2025-08-03", "satir": 3, "adres": 3}]
    assert hf.satir_sayisi(con, glob) == 6
    assert [c["ad"] for c in hf.sutunlar(con, glob)][:4] == ["user", "dex", "collateral_token", "account_value"]
    values = hf.hf_degerleri(con, hf.tarih_yolu(base, "account_values", "2025-08-01"), [A, B, C])
    assert values == {A: {"account_value": 150.0, "satir": 2}, B: {"account_value": 200.0, "satir": 1}}     # A: 100 + 50, büyük/küçük harf birleşir


class FakeClient:
    """clearinghouseState (ana 140 / xyz 10 / spot 5), portfolio geçmişi."""
    def info(self, payload, weight=20):
        if payload["type"] == "perpDexs":
            return [None, {"name": "xyz"}]
        if payload["type"] == "clearinghouseState":
            return {"marginSummary": {"accountValue": "10" if payload.get("dex") else "140"}}
        if payload["type"] == "spotClearinghouseState":
            return {"balances": [{"coin": "USDC", "total": "5"}, {"coin": "BTC", "total": "9"}]}
        raise AssertionError(payload)

    def portfolio(self, address):
        # 1 Ağustos öğle: 150 (HF ile aynı); 3 Ağustos öğle: 100 → HF 120'ye göre fark 0,2
        return [["perpAllTime", {"accountValueHistory": [[hf.gun_ms("2025-08-01"), "150"], [hf.gun_ms("2025-08-03"), "100"]]}]]


def test_capraz_altin_ornek(tmp_path: Path):
    base = str(hive(tmp_path))
    out = hf.capraz(hf.baglan(), base, FakeClient(), [A], "2025-08-03", ["2025-08-01"], now_ms=hf.gun_ms("2025-08-03") + 86_400_000)
    latest, past = out["tarihler"]["2025-08-03"], out["tarihler"]["2025-08-01"]
    assert latest["portfolio"]["n"] == 1 and latest["portfolio"]["medyan"] == pytest.approx(0.2)         # |120 − 100| / 100
    assert past["portfolio"]["medyan"] == 0.0 and "clearinghouse_ana" not in past                        # 150 ↔ 150; geçmişte yalnız portfolio
    assert latest["clearinghouse_ana"]["medyan"] == pytest.approx(20 / 140)                             # |120 − 140| / 140
    assert latest["clearinghouse_ana_hip3"]["medyan"] == pytest.approx(30 / 150)                        # |120 − 150| / 150
    assert latest["clearinghouse_ana_hip3_spot"]["medyan"] == pytest.approx(35 / 155)                   # |120 − 155| / 155
    assert latest["clearinghouse_yas_gun"] == 1.0 and out["hatalar"] == {}


def test_kapi_adresleri(tmp_path: Path):
    day = tmp_path / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    pd.DataFrame({"address": [B.upper().replace("0X", "0x"), A, C], "hesap_degeri_bugun": [5.0, 10.0, None]}).to_csv(day / "sonuc.csv", index=False)
    assert hf.kapi_adresleri(tmp_path, 30) == [A, B]            # değeri boş olan atılır, sıralı, küçük harf
    assert hf.kapi_adresleri(tmp_path, 1) == [A]


def test_calistir_uctan_uca_yerel_ve_hata_kirmizi(tmp_path: Path, monkeypatch):
    base = str(hive(tmp_path / "hf"))
    day = tmp_path / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    pd.DataFrame({"address": [A], "hesap_degeri_bugun": [150.0]}).to_csv(day / "sonuc.csv", index=False)
    output = tmp_path / "o.json"
    monkeypatch.setattr(hf, "baglan", hf.baglan)
    args = hf.argparse.Namespace(root=tmp_path, base=base, alt_kume=["account_values"], output=output)
    result = hf.calistir(args, client=FakeClient())
    assert result["hatalar"] == {}
    assert result["adimlar"]["envanter"]["account_values"]["satir"] == 6 and result["adimlar"]["envanter"]["account_values"]["gun_sayisi"] == 2
    assert result["adimlar"]["kapsam"]["bosluklar"] == ["2025-08-02"] and result["adimlar"]["kapsam"]["adres_max"] == 3
    assert "yok" in result["adimlar"]["ledger"]["sonuc"]
    json.dumps(result, allow_nan=False)
    # veri yoksa hata JSON'a yazılır ve süreç sıfırdan farklı çıkar (|| true ile örtülmez)
    code = hf.main(["--root", str(tmp_path), "--base", str(tmp_path / "yok"), "--alt-kume", "account_values", "--output", str(output)])
    assert code == 1 and json.loads(output.read_text())["hatalar"]
