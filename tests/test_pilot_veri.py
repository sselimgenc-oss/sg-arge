"""Pilot veri hattı altın örnekleri (yalnız sentetik; gerçek veri yok). 2 adres × 1 hafta, elle hesaplanmış fikstür."""
import json
from datetime import UTC, datetime

import pytest

from copytrade import arsiv, pilot_veri
from copytrade.arsiv import Arsiv

A, B, C = "0x" + "a" * 40, "0x" + "b" * 40, "0x" + "c" * 40
T0 = pilot_veri.ms("2026-10-29")
H = 3_600_000
NOW = datetime(2026, 10, 29, 8, tzinfo=UTC)


def mum(coin, hour, price):
    return [{"s": coin, "t": T0 + hour * H + m * 60_000, "o": str(price), "h": str(price), "l": str(price), "c": str(price)} for m in (0, 30)]


def fill(adres, coin, side, sz, px, hour, minute, start, tid):
    return {"adres": adres, "coin": coin, "side": side, "sz": str(sz), "px": str(px), "startPosition": str(start), "closedPnl": "0",
            "fee": "0", "tid": tid, "time": T0 + hour * H + minute * 60_000}


def secim(oda=(A,)):
    def e(puan, kollar):
        return {"puan": puan, "kollar": kollar, "tarz": "intraday", "hesap_degeri": 1000.0, "medyan_kaldirac": 1.0, "medyan_tutma_saat": 10.0}
    return {"tarih": "2026-10-29", "adresler": {A: e(0.1, ["oda", "havuz"]), B: e(0.2, ["havuz"])}}


def yoklama(tmp_path, zaman_ms):
    gun = tmp_path / "arsiv/tur=kapsam/gun=2026-10-29"
    gun.mkdir(parents=True, exist_ok=True)
    (gun / "yoklamalar.json").write_text(json.dumps([{"tur": "dolum", "ozne": A, "zaman_ms": zaman_ms, "aralik_ms": H}]))


def kur(tmp_path, ilk_saat=0, cos=("BTC",)):
    yoklama(tmp_path, T0 + ilk_saat * H)
    arc = Arsiv(tmp_path / "arsiv", NOW)
    rows = []
    for hour, price in ((0, 100), (1, 100), (2, 100), (3, 100), (4, 100), (5, 110), (6, 110)):
        if hour >= ilk_saat:
            rows += mum("BTC", hour, price)
    arc.append("mum_1dk", rows)
    return arc


GOLD = [fill(A, "BTC", "B", 1, 100, 1, 10, 0, 1), fill(A, "BTC", "A", 1, 110, 4, 10, 1, 2)]
BEKLENEN = 0.01 - 0.001 * (100 + 110) * (0.00045 + 0.0005)       # 1/1000 ölçek, 10 USD fark, iki yön maliyet


def test_altin_ornek_ileri_getiri_kapanmis_islem_ve_pasif_adres(tmp_path):
    arc = kur(tmp_path)
    arc.append("dolum", GOLD)
    sonuc = pilot_veri.uret(tmp_path / "arsiv", secim(), {}, "2026-10-29", tmp_path / "c", now=NOW)
    getiri = json.loads((tmp_path / "c/getiri.json").read_text())
    assert getiri[A] == pytest.approx(BEKLENEN, abs=1e-12)
    assert getiri[B] == 0.0                                       # pasif adres sıfır getirili, paydada kalır
    assert json.loads((tmp_path / "c/kapanmis_islem.json").read_text()) == {A: 1, B: 0}
    assert sonuc == {"havuz": 2, "getiri": 2, "eksik": 0, "pencere_disi": 0, "oda_risk": 1}


class Api:
    """Sahte istemci; gerçek API gibi pencere adresin TÜM dolumları üzerinden sayılır: yalnız son ``kapasite`` dolum erişilebilir, aralık süzgeci ondan sonra."""

    def __init__(self, dolumlar, kapasite=10_000):
        self.dolumlar, self.kapasite, self.istek = dolumlar, kapasite, 0

    def fills(self, adres, start, max_rows=None, end_ms=None):
        self.istek += 1
        pencere = [f for f in self.dolumlar if f["adres"] == adres][-self.kapasite:]
        rows = [{k: v for k, v in f.items() if k != "adres"} for f in pencere if start <= f["time"] <= (end_ms or 1 << 62)]
        return rows[:max_rows] if max_rows is not None else rows

    def info(self, body, weight=1):
        return []

    def candles(self, coin, start, end, interval):
        assert interval == "1h"
        return [{"s": coin, "t": T0 + h * H, "o": "100", "h": "100", "l": "100", "c": "100"} for h in range(0, 3) if T0 + h * H < end]


def test_altin_ornek_bosluk_bir_kez_arsive_yazilir_haftalik_koşu_apiye_gitmez(tmp_path):
    arc = kur(tmp_path, ilk_saat=3)
    arc.append("dolum", [GOLD[1]])                                 # arşiv yalnız 04:10 dolumunu görmüş; 01:10 dolumu boşlukta
    with pytest.raises(RuntimeError, match="boşluk doldurulmadı"):
        pilot_veri.uret(tmp_path / "arsiv", secim(), {}, "2026-10-29", tmp_path / "c", now=NOW)      # doldurmadan haftalık koşu KIRMIZI
    api = Api(GOLD)
    sonuc = pilot_veri.bosluk_doldur(tmp_path / "arsiv", secim(), api, now=NOW)
    assert sonuc["pencere_disi"] == 0 and sonuc["dolum"] == 1 and api.istek == 4        # boşluk dolumu (01:10) + pencere sayımı; iki adres
    pilot_veri.uret(tmp_path / "arsiv", secim(), {}, "2026-10-29", tmp_path / "c", now=NOW)           # API istemcisi parametresi bile yok
    assert json.loads((tmp_path / "c/getiri.json").read_text())[A] == pytest.approx(BEKLENEN, abs=1e-12)
    assert json.loads((tmp_path / "c/kapanmis_islem.json").read_text())[A] == 1


def test_altin_ornek_api_pencere_siniri_dolarsa_adres_pencere_disi_eksik_sayilir(tmp_path, capsys):
    """Sahte istemci yalnız son 10.000 dolumu verir; boşlukta 12.000 dolum var → en eski dolum etiketten sonra → sessiz sıfır değil, eksik."""
    kur(tmp_path, ilk_saat=3)
    cok = [fill(A, "BTC", "B", 1, 100, 0, 0, 0, 0) | {"time": T0 + 1000 + i, "tid": i} for i in range(12_000)]
    sonuc = pilot_veri.bosluk_doldur(tmp_path / "arsiv", secim(), Api(cok), now=NOW)
    assert sonuc["pencere_disi"] == 1
    assert "pencere dışı" in capsys.readouterr().out
    kayit = json.loads(pilot_veri.bosluk_yolu(tmp_path / "arsiv").read_text())
    assert kayit["pencere_disi"] == [A]
    out = pilot_veri.uret(tmp_path / "arsiv", secim(), {}, "2026-10-29", tmp_path / "c", now=NOW)
    assert A not in json.loads((tmp_path / "c/getiri.json").read_text())
    assert out["pencere_disi"] == 1 and out["eksik"] == 1


def test_altin_ornek_aralikta_az_dolum_ama_adresin_penceresi_etiketten_sonra_basliyorsa_pencere_disi(tmp_path, capsys):
    """Lider: aralıkta (etiket → ilk yoklama) yalnız 300 dolum döner, ama adresin son 10.000 dolumu etiketten sonra başlıyor → boşluğun başı erişilemez."""
    kur(tmp_path, ilk_saat=3)
    aralik = [fill(A, "BTC", "B", 1, 100, 0, 0, 0, 0) | {"time": T0 + 5 * H + i, "tid": i} for i in range(300)]
    sonra = [fill(A, "BTC", "B", 1, 100, 0, 0, 0, 0) | {"time": T0 + 5 * H + 1000 + i, "tid": 1000 + i} for i in range(10_000)]
    api = Api(aralik + sonra)
    assert len(api.fills(A, T0, end_ms=T0 + 3 * H)) == 0          # sahte istemci pencereyi taklit eder: aralık verisi artık erişilemez
    sonuc = pilot_veri.bosluk_doldur(tmp_path / "arsiv", secim(), api, now=NOW)
    assert sonuc["pencere_disi"] == 1 and "pencere dışı" in capsys.readouterr().out
    assert json.loads(pilot_veri.bosluk_yolu(tmp_path / "arsiv").read_text())["pencere_disi"] == [A]


def test_altin_ornek_aralikta_300_dolum_donuyor_adresin_toplami_pencerenin_altindaysa_pencere_disi_degil(tmp_path):
    kur(tmp_path, ilk_saat=3)
    az = [fill(A, "BTC", "B", 1, 100, 0, 0, 0, 0) | {"time": T0 + 1000 + i, "tid": i} for i in range(9_999)]
    assert pilot_veri.bosluk_doldur(tmp_path / "arsiv", secim(), Api(az), now=NOW)["pencere_disi"] == 0


def test_oku_gun_ve_adres_suzgeci_ve_ozet_dosyasi(tmp_path):
    arc = kur(tmp_path)
    arc.append("pozisyon", [{"adres": A, "durum": {"x": 1}}, {"adres": B, "durum": {"x": 2}}])
    assert [r["adres"] for r in pilot_veri.oku(tmp_path / "arsiv", "pozisyon", adresler={A})] == [A]
    assert pilot_veri.oku(tmp_path / "arsiv", "pozisyon", gun_baslangic="2026-10-30") == []
    arc.append("dolum", GOLD)
    pilot_veri.uret(tmp_path / "arsiv", secim(), {}, "2026-10-29", tmp_path / "c", now=NOW)
    ozet = json.loads((tmp_path / "c/ozet.json").read_text())
    assert ozet["sure_sn"] >= 0 and ozet["satir"]["dolum"] == 2 and set(ozet) == {"havuz", "getiri", "eksik", "pencere_disi", "oda_risk", "sure_sn", "satir"}   # kol getirisi yok


def test_altin_ornek_mum_eksikse_adres_getiriden_cikar_ve_eksik_sayilir(tmp_path):
    arc = kur(tmp_path)
    arc.append("dolum", [fill(C, "ETH", "B", 1, 50, 1, 10, 0, 9)])      # ETH mumu yok → yürütme eksik → veri eksik
    r = secim()
    r["adresler"][C] = {"puan": 0.3, "kollar": ["havuz"], "tarz": "intraday", "hesap_degeri": 1000.0}
    sonuc = pilot_veri.uret(tmp_path / "arsiv", r, {}, "2026-10-29", tmp_path / "c", now=NOW)
    assert C not in json.loads((tmp_path / "c/getiri.json").read_text())
    assert sonuc["eksik"] == 1 and sonuc["havuz"] == 3


def test_altin_ornek_mum_anahtari_coinleri_birbirine_ezmez(tmp_path):
    arc = Arsiv(tmp_path, NOW)
    arc.append("mum_1dk", [{"s": "BTC", "t": T0, "o": "1", "h": "1", "l": "1", "c": "1"}, {"s": "ETH", "t": T0, "o": "2", "h": "2", "l": "2", "c": "2"}])
    assert {r["s"] for r in pilot_veri.oku(tmp_path, "mum_1dk")} == {"BTC", "ETH"}


def test_altin_ornek_risk_girdisi_yalniz_oda_uyeleri_ve_kaldirac_sicramasi(tmp_path):
    arc = kur(tmp_path)
    arc.append("dolum", GOLD)
    snap = {"marginSummary": {"accountValue": "1000", "totalNtlPos": "3000"}, "assetPositions": []}
    arc.append("pozisyon", [{"adres": A, "durum": snap}])
    arc.now = NOW
    pilot_veri.uret(tmp_path / "arsiv", secim(), {"bayraklar": {A: {"bayrak_katlama_orani": 0.0}}}, "2026-10-29", tmp_path / "c", now=NOW)
    risk = json.loads((tmp_path / "c/risk.json").read_text())
    assert list(risk) == [A]
    from copytrade import risk_isaretleri
    got = risk_isaretleri.uye_isaretleri(risk[A]["etiket"], risk[A]["son"])
    assert got["kaldirac_sicramasi"] is True                      # 3x > 2,5 × medyan 1x
    assert got["tutma_anomalisi"] is False


def test_altin_ornek_kol_bazinda_getiri_cikmaz(tmp_path):
    kur(tmp_path).append("dolum", GOLD)
    pilot_veri.uret(tmp_path / "arsiv", secim(), {}, "2026-10-29", tmp_path / "c", now=NOW)
    for ad in ("getiri", "kapanmis_islem", "risk"):
        metin = (tmp_path / f"c/{ad}.json").read_text()
        assert not any(k in metin for k in ("kontrol", "taban", "elle", "kohort"))
    assert set(json.loads((tmp_path / "c/getiri.json").read_text())) == {A, B}      # yalnız adres → değer


def test_secim_havuzu_arsiv_havuzuna_girer(tmp_path):
    (tmp_path / "copytrade").mkdir()
    (tmp_path / "copytrade/izleme_listesi.yaml").write_text("traderlar: []")
    (tmp_path / "secim.json").write_text(json.dumps(secim()))
    assert arsiv.pool(tmp_path, None, tmp_path / "secim.json") == [A, B]
    assert arsiv.pool(tmp_path, None) == []


def test_arsiv_mum_anahtari_gercek_api_satirinda_coin_icerir():
    assert arsiv.key("mum_1dk", {"s": "BTC", "t": 5}) != arsiv.key("mum_1dk", {"s": "ETH", "t": 5})
