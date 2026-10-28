from copytrade.defter import DAY, HOUR
from copytrade.golge import Gecikme, calistir, kirp_pozisyon, saglama, v2_sinir
from copytrade.kurallar import load_rules
import pytest
import pandas as pd
from copytrade.kollar import adaylar, cikis, olay_yaz, sec, terfi
from copytrade.tarama import PublicClient
from copytrade.golge_saglama import _summary, pencere_ici_dolumlar, pozisyon_dokumu

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


def test_altin_v2_onkayit_d_ile_ayni_donmus_esikleri_kullanir():
    assert RULES["golge_v2"]["intraday"]["zarar_kes"] == -0.50
    assert RULES["golge_v2"]["swing"]["gun_7"] == {"zarar_kes": -0.30, "kar_al": 0.60}
    assert RULES["golge_v2"]["swing"]["gun_14"] == {"zarar_kes": -0.20, "kar_al": 0.40}


def test_altin_3x_asan_ekleme_kirpilir():
    clipped, event = kirp_pozisyon(fill(10, "B", 40, 0, 100), 20 / 1_000, 1_000)
    assert float(clipped["sz"]) == pytest.approx(10.0)
    assert event["durum"] == "kirpildi" and event["tavan_usd"] == 3.0


def test_altin_v2_8_gunde_eksi31_mumda_maliyetli_cikar():
    rows = [fill(10, "B", 1_000, 0, 100)]
    market = {"BTC": [{"t": T0 + h * HOUR, "o": 100 if h < 8 * 24 else 69, "c": 100 if h < 8 * 24 else 69}
                      for h in range(8 * 24 + 2)]}
    out = calistir(rows, market, 1_000, style="swing", etiket_ms=T0, end_ms=T0 + 9 * 24 * HOUR, variant="V2", delay_min=0)
    assert any(event["durum"] == "v2_cikis" for event in out["olaylar"])
    assert out["defter"]["costs"] > 0


def test_altin_v2_swing_esikleri_fiyat_ve_maliyetle_donuyor():
    rows = [fill(0, "B", 10, 0, 100)]
    market = {"BTC": [{"t": T0 + h * HOUR, "o": 100 if h < 8 * 24 else 69, "c": 100 if h < 8 * 24 else 69}
                      for h in range(9 * 24 + 1)]}
    out = calistir(rows, market, 1_000, style="swing", etiket_ms=T0, end_ms=T0 + 9 * DAY, variant="V2", delay_min=0)
    event = next(item for item in out["olaylar"] if item["durum"] == "v2_cikis")
    assert event["zaman_ms"] == T0 + 8 * DAY
    # 0,01 BTC: giriş 100, zorunlu çıkış 69; iki dolumun taker+kayma maliyeti.
    assert out["defter"]["costs"] == pytest.approx(0.01 * (100 + 69) * 0.00095)


def test_altin_v2_6_gun_eksi49_kalir_15_gun_artı41_kar_alir():
    rows = [fill(0, "B", 10, 0, 100)]
    six = {"BTC": [{"t": T0 + h * HOUR, "o": 51, "c": 51} for h in range(6 * 24 + 1)]}
    assert not any(x["durum"] == "v2_cikis" for x in calistir(rows, six, 1_000, style="swing", etiket_ms=T0,
                                                                 end_ms=T0 + 6 * DAY, variant="V2", delay_min=0)["olaylar"])
    fifteen = {"BTC": [{"t": T0 + h * HOUR, "o": 100 if h < 15 * 24 else 141, "c": 141}
                       for h in range(15 * 24 + 1)]}
    out = calistir(rows, fifteen, 1_000, style="swing", etiket_ms=T0, end_ms=T0 + 15 * DAY, variant="V2", delay_min=0)
    assert any(x["durum"] == "v2_cikis" and x["neden"] == "kar_al" for x in out["olaylar"])


def test_altin_v2_intraday_eksi50_cikar():
    rows = [fill(0, "B", 10, 0, 100)]
    out = calistir(rows, candles(100, 50), 1_000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR,
                   variant="V2", delay_min=0)
    assert any(x["durum"] == "v2_cikis" and x["neden"] == "zarar_kes" for x in out["olaylar"])


def test_altin_likidasyon_golgenin_kendi_teminat_ve_markiyla_cikar():
    rows = [fill(0, "B", 10, 0, 100)]
    out = calistir(rows, candles(100, 0), 1_000, style="intraday", etiket_ms=T0, end_ms=T0 + HOUR,
                   variant="V0", delay_min=0)
    assert any(x["durum"] == "likidasyon" and x["zaman_ms"] == T0 + HOUR for x in out["olaylar"])


def test_altin_gecikme_zinciri_kayit_yoksa_nedenle_bos_kalir_ve_kayitla_dolar():
    rows = [fill(0, "B", 1, 0, 100, 44)]
    empty = calistir(rows, candles(100), 1_000, style="intraday", etiket_ms=T0, end_ms=T0, delay_min=0)
    assert empty["gecikme_zinciri"] == [{"trader_ms": T0, "tespit_ms": None, "telegram_ms": None, "acti_ms": None, "neden": "karar_kaydi_yok"}]
    filled = calistir(rows, candles(100), 1_000, style="intraday", etiket_ms=T0, end_ms=T0, delay_min=0,
                      gecikmeler={44: Gecikme(T0, T0 + 1, T0 + 2, T0 + 3)})
    assert filled["gecikme_zinciri"][0] == {"trader_ms": T0, "tespit_ms": T0 + 1, "telegram_ms": T0 + 2, "acti_ms": T0 + 3, "neden": None}


def test_altin_v2_cikis_sonrasi_kapanis_atlanir_yeni_acilis_kopyalanir():
    rows = [fill(0, "B", 10, 0, 100), fill(9 * 24 * 60, "A", 10, 10, 69, 2),
            fill(10 * 24 * 60, "B", 10, 0, 70, 3)]
    market = {"BTC": [{"t": T0 + h * HOUR, "o": 100 if h < 8 * 24 else 69 if h < 10 * 24 else 70, "c": 70}
                      for h in range(11 * 24 + 1)]}
    out = calistir(rows, market, 1_000, style="swing", etiket_ms=T0, end_ms=T0 + 11 * DAY, variant="V2", delay_min=0)
    assert any(x["durum"] == "atlandi_v2" and x["dolum"]["tid"] == 2 for x in out["olaylar"])
    # Zorunlu çıkış + ilk açılış + sıfırlama sonrası yeni açılış: ters yönlü kapanış yok.
    assert out["defter"]["executed"] == 3
    assert out["defter"]["unrealized_end"] == 0


def test_altin_v2_ekleme_gecmis_mumlari_yeniden_taramaz():
    rows = [fill(0, "B", 10, 0, 100), fill(8 * 24 * 60, "B", 10, 10, 100, 2)]
    market = {"BTC": [{"t": T0 + h * HOUR, "o": 51 if h == 6 * 24 else 100, "c": 100}
                      for h in range(8 * 24 + 1)]}
    out = calistir(rows, market, 1_000, style="swing", etiket_ms=T0, end_ms=T0 + 8 * DAY, variant="V2", delay_min=0)
    assert not any(x["durum"] == "v2_cikis" for x in out["olaylar"])


def test_altin_tavan_hesap_serisi_dolum_anindaki_olcekle_buyur():
    account = pd.Series([1_000.0, 2_000.0], index=pd.to_datetime([T0, T0 + DAY], unit="ms"))
    rows = [fill(0, "B", 30, 0, 100), fill(24 * 60, "B", 60, 30, 100, 2)]
    out = calistir(rows, candles(*([100] * 26)), account, style="intraday", etiket_ms=T0, end_ms=T0 + DAY,
                   variant="V0", delay_min=0)
    # İlk dolum 3x tavana tam gelir; iki kat hesaptaki ikinci ekleme de aynı 3x gölge tavanına göre kırpılır.
    clipped = [x for x in out["olaylar"] if x["durum"] == "kirpildi"]
    assert clipped and float(clipped[0]["yeni_sz"]) == pytest.approx(0.0)


def test_altin_kontrol_tohumu_ve_olay_arsivi_tekrarlanabilir(tmp_path):
    assert sec(["a", "b", "c"], {"a": 2, "b": 1}, 1, "2026-10-28") == sec(["a", "b", "c"], {"a": 2, "b": 1}, 1, "2026-10-28")
    path = tmp_path / "tur=olay" / "olaylar.jsonl"
    olay_yaz(path, {"durum": "giris", "adres": "a"})
    assert path.read_text().count("giris") == 1


def test_altin_kol_terfi_ve_cikis_onkayittaki_kat_kuralidir():
    havuz = [f"a{i}" for i in range(100)]
    assert len(adaylar(havuz)) == 15
    assert not terfi("a0", havuz, 20, 10) and not terfi("a0", havuz, 21, 9)
    assert terfi("a9", havuz, 21, 10)
    aday = [f"a{i}" for i in range(20)]
    assert not cikis("a9", aday) and cikis("a10", aday)


def test_altin_10000_ustu_dolum_zaman_penceresiyle_sayfalanir():
    class Client:
        fills = PublicClient.fills

        def info(self, payload, weight=20):
            start = int(payload["startTime"])
            page_no = (start - T0) // 2_000
            if page_no >= 6:
                return []
            count = 2_000 if page_no < 5 else 1
            return [{"tid": page_no * 2_000 + i, "time": T0 + page_no * 2_000 + i, "coin": "BTC", "sz": "1"}
                    for i in range(count)]

    rows = Client().fills("0xabc", T0)
    assert len(rows) == 10_001 and rows[-1]["tid"] == 10_000


def test_altin_pencere_oncesi_acik_pozisyon_kapanisi_saglama_kiyasindan_cikar():
    old_close = fill(0, "A", 10, 10, 90, 1) | {"closedPnl": "-100"}
    opening = fill(10, "B", 10, 0, 100, 2) | {"closedPnl": "0"}
    closing = fill(20, "A", 10, 10, 110, 3) | {"closedPnl": "100"}
    assert pencere_ici_dolumlar([old_close, opening, closing]) == [opening, closing]
    assert pencere_ici_dolumlar([opening]) == [opening]  # açık kalsa da sonraki kısmi kapanışların tabanı korunur


def test_altin_pencere_ici_flip_kapanisi_alir_yeni_yonu_sonraki_kapanisa_tasir():
    opening = fill(0, "B", 10, 0, 100, 1)
    flip = fill(10, "A", 15, 10, 110, 2) | {"closedPnl": "100"}
    close_short = fill(20, "B", 5, -5, 100, 3) | {"closedPnl": "50"}
    selected = pencere_ici_dolumlar([opening, flip, close_short])
    assert [(row["side"], float(row["sz"]), float(row["startPosition"])) for row in selected] == [
        ("B", 10, 0), ("A", 10, 10), ("A", 5, 0), ("B", 5, -5)]


def test_altin_sabit_olcekli_saglama_hesap_buyumesinden_bagimsizdir():
    account = pd.Series([1_000.0, 2_000.0], index=pd.to_datetime([T0, T0 + HOUR], unit="ms"))
    rows = [fill(0, "B", 10, 0, 100, 1) | {"closedPnl": "0"},
            fill(60, "A", 10, 10, 110, 2) | {"closedPnl": "100"}]
    market = candles(100, 110)
    assert _summary(rows, market, account, T0, T0 + HOUR)["fark"] == pytest.approx(0.05)
    assert _summary(rows, market, account, T0, T0 + HOUR, fixed_scale=True)["fark"] == pytest.approx(0.0)


def test_altin_saglama_toplam_net_ve_eksik_isaretleme_notu():
    """Açık BTC için son mum yoksa gerçekleşmiş kıyas korunur ama sonuç eksik işaretlemeyi açıkça not eder; toplam net de ayrıca kıyaslanır."""
    rows = [fill(0, "B", 10, 0, 100, 1) | {"closedPnl": "0"}]
    summary = _summary(rows, {"BTC": []}, 1_000.0, T0, T0 + HOUR)
    assert summary["mark_missing"] == 1 and summary["not"] == "eksik işaretleme"
    assert summary["trader_toplam_net"] == pytest.approx(summary["golge_toplam_net"])
    assert summary["toplam_net_fark"] == pytest.approx(0.0)


def test_altin_trader_toplam_net_golge_unrealizedini_kullanmaz():
    """Trader 10 BTC @100 açar; pencere sonunda hesap 2000 $, işaret 110. Trader açık K/Z = 10·10/2000=0,05.
    Gölge ise giriş anındaki 1000 $ ölçekle 0,10 taşır; trader toplamı gölgenin 0,10'u değil kendi 0,05'i olmalıdır."""
    account = pd.Series([1_000.0, 2_000.0], index=pd.to_datetime([T0, T0 + HOUR], unit="ms"))
    rows = [fill(0, "B", 10, 0, 100, 1) | {"closedPnl": "0"}]
    summary = _summary(rows, candles(100, 110), account, T0, T0 + HOUR)
    assert summary["trader_toplam_net"] == pytest.approx(0.05)
    assert summary["golge_toplam_net"] == pytest.approx(0.1)
    assert summary["toplam_net_fark"] == pytest.approx(0.05)


def test_altin_kapanir_yeniden_acilir_ve_sonda_acik_kalir_ilk_tur_saglamaya_girer():
    rows = [fill(0, "B", "0.1", 0, 100, 1), fill(10, "A", "0.1", "0.1", 110, 2),
            fill(20, "B", "0.2", 0, 100, 3)]
    selected = pencere_ici_dolumlar(rows)
    assert selected == rows
    diag = pozisyon_dokumu(rows)["BTC"]
    assert diag == {"son_pozisyon": "0.2", "en_kucuk_mutlak_pozisyon": "0.0", "sifira_donus_sayisi": 1}
