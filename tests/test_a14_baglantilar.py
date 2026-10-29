"""A14 bağlantıları (uçtan uca): kapı günlük kopya getirisini yayımlar → seçim raporu oda yoğunlaşması ve puan yarı tutarlılığını bilgi olarak yazar."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from copytrade import secim
from copytrade.kapi import gunluk_kaydet, merge_shards
from copytrade.kurallar import load_rules
from tests.test_secim import TABLE, addr

RULES = load_rules()


def test_yaml_esikleri():
    assert RULES["yogunlasma_min_ortak_gun"] == 10 and RULES["yogunlasma_kume_esik"] == 0.5


def test_gunluk_kaydet_yalniz_adim1_ve_adim2_gecenler_icin():
    series = pd.Series([0.01, -0.02], index=pd.to_datetime(["2026-10-01", "2026-10-02"], utc=True))
    store: dict = {}
    gunluk_kaydet(store, "0xa", {"adim1": "Geçti", "adim2": "Geçti"}, series)
    gunluk_kaydet(store, "0xb", {"adim1": "Geçti", "adim2": "Yetersiz"}, series)
    gunluk_kaydet(store, "0xc", {"adim1": "Geçti", "adim2": "Geçti"}, None)
    gunluk_kaydet(None, "0xd", {"adim1": "Geçti", "adim2": "Geçti"}, series)                       # toplama kapalı: hata yok
    assert list(store) == ["0xa"] and store["0xa"].equals(series)


def _gunluk(base: Path, columns: dict[str, list[float]], folder: str = "stage1-0"):
    day = base / folder / "2026-10-28"
    day.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"address": list(columns), "asama1": "Yetersiz"}).to_csv(day / "sonuc.csv", index=False)
    (day / "evren.json").write_text(json.dumps({"evren": len(columns)}))
    (day / "bitti.json").write_text("{}")
    index = pd.date_range("2026-10-01", periods=len(next(iter(columns.values()))), freq="1D", tz="UTC")
    pd.DataFrame(columns, index=index).to_csv(day / "gunluk.csv.gz", compression="gzip")


def test_birlestirme_parcalarin_ve_onceki_dosyanin_gunluk_getirilerini_birlestirir(tmp_path):
    _gunluk(tmp_path / "shards", {"0xa": [0.01, 0.02, 0.03]}, "stage1-0")
    _gunluk(tmp_path / "shards", {"0xb": [0.0, 0.01, -0.01]}, "stage1-1")
    root = tmp_path / "root"
    previous = root / "kapi/2026-10-28"                                                          # veri dalından gelen önceki dosya (eksik mod)
    previous.mkdir(parents=True)
    index = pd.date_range("2026-10-01", periods=3, freq="1D", tz="UTC")
    pd.DataFrame({"0xc": [0.5, 0.5, 0.5], "0xa": [9.0, 9.0, 9.0]}, index=index).to_csv(previous / "gunluk.csv.gz", compression="gzip")
    merge_shards(tmp_path / "shards", root, 2, "tam")
    merged = pd.read_csv(root / "kapi/2026-10-28/gunluk.csv.gz", index_col=0, parse_dates=True)
    assert sorted(merged.columns) == ["0xa", "0xb", "0xc"] and len(merged) == 3
    assert merged["0xa"].tolist() == [0.01, 0.02, 0.03]                                          # bu koşunun satırı öncekini geçersiz kılar
    assert merged["0xc"].tolist() == [0.5, 0.5, 0.5]                                             # yeniden hesaplanmayan adres önceki dosyadan korunur


def _kapi_dizini(tmp_path, gunluk: pd.DataFrame | None) -> Path:
    day = tmp_path / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    TABLE.to_csv(day / "sonuc.csv", index=False)
    (day / "durum.json").write_text(json.dumps({"durum": "tamam", "kapsam": 1.0, "hesap": "v1.1-test"}), encoding="utf-8")
    if gunluk is not None:
        gunluk.to_csv(day / "gunluk.csv.gz", compression="gzip")
    (tmp_path / "board.json").write_text("[]", encoding="utf-8")
    return day


def _getiriler() -> pd.DataFrame:
    """Havuz (TABLE'daki 11 adres) için 20 günlük getiri: oda üyeleri a ve 2 birebir aynı seri (korelasyon 1); diğerleri sabit getiri düzeyi = puan sırası."""
    index = pd.date_range("2026-10-01", periods=20, freq="1D", tz="UTC")
    rng = np.random.default_rng(3)
    noise = rng.normal(0, 0.0005, 20)                                                             # yarı toplamları ~0: diğerlerinin (0,01–0,08) altında kalır
    columns = {addr(n): list(noise) for n in ("a", "2")}                                         # birebir aynı → tek küme
    for i, n in enumerate(("b", "c", "d", "e", "f", "1", "3", "4")):
        columns[addr(n)] = [0.001 * (i + 1)] * 20                                                # sabit getiri: iki yarıda aynı sıra (rho 1)
    return pd.DataFrame(columns, index=index)


def test_secim_oda_yogunlasmasi_ve_puan_yari_tutarliligi_secim_json_ve_raporda(tmp_path):
    _kapi_dizini(tmp_path, _getiriler())
    secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(tmp_path / "board.json"), "--bayraksiz"])
    out = tmp_path / "secim/2026-10-28-v1.3"
    result = json.loads((out / "secim.json").read_text())
    oda = result["yogunlasma"]["oda"]
    assert oda == {"n": 2, "kume_sayisi": 1, "en_buyuk_kume_payi": 1.0, "etkin_kume_sayisi": 1.0}       # oda: a ve 2 birebir aynı seri
    assert result["yogunlasma"]["puan_tutarliligi"] == {"n": 10, "rho": pytest.approx(1.0)}               # iki yarıda da aynı sıra (a ve 2 eşit → ortalama sıra)
    text = (out / "RAPOR.md").read_text(encoding="utf-8")
    assert "## Oda yoğunlaşması ve puan tutarlılığı (bilgi)" in text and "küme sayısı 1" in text and "en büyük küme payı 1.00" in text and "etkin küme sayısı 1.00" in text
    assert "kimseyi elemez" in text or "seçimi değiştirmez" in text


def test_gunluk_dosyasi_yoksa_rapor_bunu_soyler_ve_secim_ayni_kalir(tmp_path):
    _kapi_dizini(tmp_path, None)
    secim.main(["--root", str(tmp_path), "--output", str(tmp_path / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(tmp_path / "board.json"), "--bayraksiz"])
    out = tmp_path / "secim/2026-10-28-v1.3"
    result = json.loads((out / "secim.json").read_text())
    assert result["yogunlasma"] is None and "Günlük getiri dosyası yok" in (out / "RAPOR.md").read_text(encoding="utf-8")
    with_data = tmp_path / "w"
    with_data.mkdir()
    _kapi_dizini(with_data, _getiriler())
    secim.main(["--root", str(with_data), "--output", str(with_data / "secim"), "--tarih", "2026-10-28", "--taban-dosyasi", str(with_data / "board.json"), "--bayraksiz"])
    other = json.loads((with_data / "secim/2026-10-28-v1.3/secim.json").read_text())
    for key in ("sayilar", "kontrol", "eslesme", "oda_kota"):
        assert other[key] == result[key]                                                         # bilgi bölümü seçimi (oda, kontrol, sayılar) değiştirmez
    assert {a for a, e in other["adresler"].items() if "oda" in e["kollar"]} == {a for a, e in result["adresler"].items() if "oda" in e["kollar"]}
