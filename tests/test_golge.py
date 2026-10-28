from copytrade.defter import DAY, HOUR
from copytrade.golge import calistir, kirp_pozisyon, saglama, v2_sinir
from copytrade.kurallar import load_rules
import pytest
from copytrade.kollar import olay_yaz, sec

T0 = 20_833 * DAY
RULES = load_rules()


def fill(minute, side, size, before, px, tid=1):
    return {"time": T0 + minute * 60_000, "coin": "BTC", "side": side, "sz": str(size), "startPosition": str(before), "px": str(px), "tid": tid}


def candles(*prices):
    return {"BTC": [{"t": T0 + hour * HOUR, "o": price, "c": price} for hour, price in enumerate(prices)]}


def test_altin_v0_kismi_kapama_flip_funding_ve_saglama():
    fills = [fill(10, "B", 10, 0, 100), fill(20, "A", 5, 10, 110, 2), fill(30, "A", 10, 5, 120, 3)]
    result = calistir(fills, candles(100, 110, 120, 120), 1000, style="intraday", etiket_ms=T0, end_ms=T0 + 3 * HOUR, variant="V0", delay_min=0)
    assert result["defter"]["executed"] == 3  # kısmi kapanış ve flip defterin tek motorunda
    check = saglama(fills, candles(100, 110, 120, 120), 1000, T0, T0 + 3 * HOUR)
    assert check["costs"] == 0 and check["missing"] == 0


def test_altin_v1_bant_ve_eksik_kacirilan_satiri_kaybolmaz():
    rows = [fill(10, "B", 1, 0, 100), fill(20, "A", 1, 1, 100, 2)]
    result = calistir(rows, candles(100, 103), 1000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR, variant="V1")
    assert any(event["durum"] == "atlandi_bant" for event in result["olaylar"])
    assert any(event["durum"] == "kacirildi" for event in result["olaylar"])


def test_sentetik_sifir_etkili_trader_saglamada_sifir_pnl_uretir():
    rows = [fill(10, "B", 1, 0, 100), fill(20, "A", 1, 1, 100, 2)]
    check = saglama(rows, candles(100, 100), 1000, T0, T0 + HOUR)
    assert check["net"] == 0.0


def test_sentetik_enjekte_edilmis_etki_pozitif_pnl_olarak_yakalanir():
    rows = [fill(10, "B", 1, 0, 100), fill(20, "A", 1, 1, 120, 2)]
    check = saglama(rows, candles(100, 120), 1_000, T0, T0 + HOUR)
    assert check["net"] == 0.02


def test_altin_v2_8_gunde_eksi31_cikar_6_gunde_eksi49_kalir():
    assert v2_sinir("swing", 8, -0.31) == "zarar_kes"
    assert v2_sinir("swing", 6, -0.49) is None
    assert v2_sinir("swing", 14, 0.40) == "kar_al"


def test_altin_3x_asan_ekleme_kirpilir():
    clipped, event = kirp_pozisyon(fill(10, "B", 40, 0, 100), 20 / 1_000, 1_000)
    assert float(clipped["sz"]) == pytest.approx(10.0)
    assert event["durum"] == "kirpildi" and event["tavan_usd"] == 3.0


def test_altin_kontrol_tohumu_ve_olay_arsivi_tekrarlanabilir(tmp_path):
    assert sec(["a", "b", "c"], {"a": 2, "b": 1}, 1, "2026-10-28") == sec(["a", "b", "c"], {"a": 2, "b": 1}, 1, "2026-10-28")
    path = tmp_path / "tur=olay" / "olaylar.jsonl"
    olay_yaz(path, {"durum": "giris", "adres": "a"})
    assert path.read_text().count("giris") == 1
