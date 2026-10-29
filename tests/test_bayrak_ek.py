"""`copytrade/bayrak_ek.py` testleri (Argon A12 altın örnekleri + pencere öncesi pozisyon, bozuk satır, perp süzgeci)."""

from __future__ import annotations

import math

import pytest

from copytrade.bayrak_ek import ekleme_derinligi, martingale_olcusu, tek_coin_yogunlugu


def test_bos_liste_martingale():
    sonuc = martingale_olcusu([], kat_esik=1.5)
    assert sonuc == {"zararda_ekleme_sayisi": 0, "katlama_orani": 0.0, "en_buyuk_kat": 0.0, "atlanan_satir": 0}


def test_bos_liste_tek_coin_yogunlugu():
    sonuc = tek_coin_yogunlugu([])
    assert sonuc == {"hhi": 0.0, "en_buyuk_coin": None, "en_buyuk_pay": 0.0, "coin_sayisi": 0, "atlanan_satir": 0}


def test_bos_liste_ekleme_derinligi():
    sonuc = ekleme_derinligi([])
    assert sonuc["en_fazla_ekleme_sayisi"] == 0
    assert math.isclose(sonuc["en_buyuk_boy_orani"], 0.0, abs_tol=1e-9)


def test_altin_ornek_martingale_klasik_2x():
    dolumlar = [
        {"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "B", "time": "100", "startPosition": "0.0", "dir": "Open Long", "closedPnl": "0.0"},
        {"coin": "BTC", "px": "90.0", "sz": "2.0", "side": "B", "time": "200", "startPosition": "1.0", "dir": "Open Long", "closedPnl": "0.0"},
        {"coin": "BTC", "px": "80.0", "sz": "4.0", "side": "B", "time": "300", "startPosition": "3.0", "dir": "Open Long", "closedPnl": "0.0"},
        {"coin": "BTC", "px": "95.0", "sz": "7.0", "side": "A", "time": "400", "startPosition": "7.0", "dir": "Close Long", "closedPnl": "65.0"},
    ]

    m_res = martingale_olcusu(dolumlar, kat_esik=2.0)
    assert m_res["zararda_ekleme_sayisi"] == 2
    assert math.isclose(m_res["katlama_orani"], 1.0, abs_tol=1e-9)
    assert math.isclose(m_res["en_buyuk_kat"], 2.0, abs_tol=1e-9)

    m_res_yuksek = martingale_olcusu(dolumlar, kat_esik=2.5)
    assert m_res_yuksek["zararda_ekleme_sayisi"] == 2
    assert math.isclose(m_res_yuksek["katlama_orani"], 0.0, abs_tol=1e-9)
    assert math.isclose(m_res_yuksek["en_buyuk_kat"], 2.0, abs_tol=1e-9)


def test_altin_ornek_martingale_karisik_eklemeler():
    dolumlar = [
        {"coin": "ETH", "px": "100.0", "sz": "1.0", "side": "B", "time": "10", "startPosition": "0.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "ETH", "px": "90.0", "sz": "1.5", "side": "B", "time": "20", "startPosition": "1.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "ETH", "px": "80.0", "sz": "3.0", "side": "B", "time": "30", "startPosition": "2.5", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "ETH", "px": "70.0", "sz": "3.0", "side": "B", "time": "40", "startPosition": "5.5", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "ETH", "px": "85.0", "sz": "8.5", "side": "A", "time": "50", "startPosition": "8.5", "dir": "Close Long", "closedPnl": "20"},
    ]

    res = martingale_olcusu(dolumlar, kat_esik=1.5)
    assert res["zararda_ekleme_sayisi"] == 3
    assert math.isclose(res["katlama_orani"], 2.0 / 3.0, abs_tol=1e-6)
    assert math.isclose(res["en_buyuk_kat"], 2.0, abs_tol=1e-9)


def test_altin_ornek_tek_coin_yogunlugu_hhi():
    dolumlar = [
        {"coin": "BTC", "px": "50000", "sz": "1.0", "side": "A", "time": "1", "startPosition": "1.0", "dir": "Close Long", "closedPnl": "40.0"},
        {"coin": "BTC", "px": "51000", "sz": "1.0", "side": "A", "time": "2", "startPosition": "1.0", "dir": "Close Long", "closedPnl": "20.0"},
        {"coin": "ETH", "px": "3000", "sz": "5.0", "side": "A", "time": "3", "startPosition": "5.0", "dir": "Close Long", "closedPnl": "30.0"},
        {"coin": "SOL", "px": "150", "sz": "10.0", "side": "A", "time": "4", "startPosition": "10.0", "dir": "Close Long", "closedPnl": "10.0"},
        {"coin": "AVAX", "px": "30", "sz": "20.0", "side": "A", "time": "5", "startPosition": "20.0", "dir": "Close Long", "closedPnl": "-40.0"},
    ]

    res = tek_coin_yogunlugu(dolumlar)
    assert res["coin_sayisi"] == 4
    assert res["en_buyuk_coin"] == "BTC"
    assert math.isclose(res["en_buyuk_pay"], 0.60, abs_tol=1e-9)
    assert math.isclose(res["hhi"], 0.46, abs_tol=1e-9)


def test_altin_ornek_ekleme_derinligi():
    dolumlar = [
        {"coin": "BTC", "px": "100", "sz": "1.0", "side": "B", "time": "1", "startPosition": "0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "90", "sz": "1.0", "side": "B", "time": "2", "startPosition": "1.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "80", "sz": "2.0", "side": "B", "time": "3", "startPosition": "2.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "70", "sz": "4.0", "side": "B", "time": "4", "startPosition": "4.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "85", "sz": "8.0", "side": "A", "time": "5", "startPosition": "8.0", "dir": "Close Long", "closedPnl": "50"},
        {"coin": "ETH", "px": "200", "sz": "2.0", "side": "B", "time": "6", "startPosition": "0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "ETH", "px": "190", "sz": "2.0", "side": "B", "time": "7", "startPosition": "2.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "ETH", "px": "205", "sz": "4.0", "side": "A", "time": "8", "startPosition": "4.0", "dir": "Close Long", "closedPnl": "30"},
    ]

    res = ekleme_derinligi(dolumlar)
    assert res["en_fazla_ekleme_sayisi"] == 3
    assert math.isclose(res["en_buyuk_boy_orani"], 8.0, abs_tol=1e-9)


def test_tek_coin_tek_karli():
    dolumlar = [
        {"coin": "SOL", "px": "100", "sz": "1.0", "side": "B", "time": "1", "startPosition": "0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "SOL", "px": "120", "sz": "1.0", "side": "A", "time": "2", "startPosition": "1.0", "dir": "Close Long", "closedPnl": "20.0"},
    ]
    res = tek_coin_yogunlugu(dolumlar)
    assert res["coin_sayisi"] == 1
    assert res["en_buyuk_coin"] == "SOL"
    assert math.isclose(res["en_buyuk_pay"], 1.0, abs_tol=1e-9)
    assert math.isclose(res["hhi"], 1.0, abs_tol=1e-9)


def test_tek_coin_eklemesiz_pozisyon():
    dolumlar = [
        {"coin": "SOL", "px": "100", "sz": "5.0", "side": "B", "time": "1", "startPosition": "0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "SOL", "px": "110", "sz": "5.0", "side": "A", "time": "2", "startPosition": "5.0", "dir": "Close Long", "closedPnl": "50"},
    ]
    m_res = martingale_olcusu(dolumlar)
    assert m_res["zararda_ekleme_sayisi"] == 0
    assert m_res["katlama_orani"] == 0.0
    assert m_res["en_buyuk_kat"] == 0.0

    d_res = ekleme_derinligi(dolumlar)
    assert d_res["en_fazla_ekleme_sayisi"] == 0
    assert math.isclose(d_res["en_buyuk_boy_orani"], 1.0, abs_tol=1e-9)


def test_long_ve_short_tam_simetri():
    long_dolumlar = [
        {"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "B", "time": "10", "startPosition": "0.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "90.0", "sz": "2.0", "side": "B", "time": "20", "startPosition": "1.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "80.0", "sz": "4.0", "side": "B", "time": "30", "startPosition": "3.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "95.0", "sz": "7.0", "side": "A", "time": "40", "startPosition": "7.0", "dir": "Close Long", "closedPnl": "65"},
    ]

    short_dolumlar = [
        {"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "A", "time": "10", "startPosition": "0.0", "dir": "Open Short", "closedPnl": "0"},
        {"coin": "BTC", "px": "110.0", "sz": "2.0", "side": "A", "time": "20", "startPosition": "-1.0", "dir": "Open Short", "closedPnl": "0"},
        {"coin": "BTC", "px": "120.0", "sz": "4.0", "side": "A", "time": "30", "startPosition": "-3.0", "dir": "Open Short", "closedPnl": "0"},
        {"coin": "BTC", "px": "105.0", "sz": "7.0", "side": "B", "time": "40", "startPosition": "-7.0", "dir": "Close Short", "closedPnl": "-35"},
    ]

    long_m = martingale_olcusu(long_dolumlar, kat_esik=1.8)
    short_m = martingale_olcusu(short_dolumlar, kat_esik=1.8)

    assert long_m["zararda_ekleme_sayisi"] == short_m["zararda_ekleme_sayisi"] == 2
    assert math.isclose(long_m["katlama_orani"], short_m["katlama_orani"], abs_tol=1e-9)
    assert math.isclose(long_m["en_buyuk_kat"], short_m["en_buyuk_kat"], abs_tol=1e-9)

    long_d = ekleme_derinligi(long_dolumlar)
    short_d = ekleme_derinligi(short_dolumlar)

    assert long_d["en_fazla_ekleme_sayisi"] == short_d["en_fazla_ekleme_sayisi"] == 2
    assert math.isclose(long_d["en_buyuk_boy_orani"], short_d["en_buyuk_boy_orani"], abs_tol=1e-9)
    assert math.isclose(long_d["en_buyuk_boy_orani"], 7.0, abs_tol=1e-9)


def test_karli_ekleme_martingale_sayilmaz():
    dolumlar = [
        {"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "B", "time": "1", "startPosition": "0.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "110.0", "sz": "2.0", "side": "B", "time": "2", "startPosition": "1.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "120.0", "sz": "3.0", "side": "A", "time": "3", "startPosition": "3.0", "dir": "Close Long", "closedPnl": "40"},
    ]
    res = martingale_olcusu(dolumlar, kat_esik=1.0)
    assert res["zararda_ekleme_sayisi"] == 0
    assert res["katlama_orani"] == 0.0
    assert res["en_buyuk_kat"] == 0.0

    d_res = ekleme_derinligi(dolumlar)
    assert d_res["en_fazla_ekleme_sayisi"] == 1
    assert math.isclose(d_res["en_buyuk_boy_orani"], 3.0, abs_tol=1e-9)


def test_tum_coinler_zararda_yogunluk():
    dolumlar = [
        {"coin": "BTC", "px": "50000", "sz": "1.0", "side": "A", "time": "1", "startPosition": "1.0", "dir": "Close Long", "closedPnl": "-100.0"},
        {"coin": "ETH", "px": "3000", "sz": "1.0", "side": "A", "time": "2", "startPosition": "1.0", "dir": "Close Long", "closedPnl": "-50.0"},
    ]
    res = tek_coin_yogunlugu(dolumlar)
    assert res["coin_sayisi"] == 2
    assert res["hhi"] == 0.0
    assert res["en_buyuk_coin"] is None
    assert res["en_buyuk_pay"] == 0.0


def test_karisik_zaman_siralamasi():
    dolumlar = [
        {"coin": "BTC", "px": "80.0", "sz": "4.0", "side": "B", "time": "300", "startPosition": "3.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "100.0", "sz": "1.0", "side": "B", "time": "100", "startPosition": "0.0", "dir": "Open Long", "closedPnl": "0"},
        {"coin": "BTC", "px": "90.0", "sz": "2.0", "side": "B", "time": "200", "startPosition": "1.0", "dir": "Open Long", "closedPnl": "0"},
    ]
    res = martingale_olcusu(dolumlar, kat_esik=2.0)
    assert res["zararda_ekleme_sayisi"] == 2
    assert math.isclose(res["katlama_orani"], 1.0, abs_tol=1e-9)
    assert math.isclose(res["en_buyuk_kat"], 2.0, abs_tol=1e-9)

def fill(coin, side, sz, px, t, before, pnl="0"):
    return {"coin": coin, "px": str(px), "sz": str(sz), "side": side, "time": str(t), "startPosition": str(before), "dir": "", "closedPnl": pnl}


def test_pencere_oncesi_pozisyonda_giris_bilinmez_zararda_ekleme_olculmez():
    """1 BTC long pencere öncesinden taşınıyor (giriş bilinmiyor). 90 ve 80'deki eklemeler 'zararda' sayılmaz (giriş uydurulmaz); 7 BTC'nin
    tamamı kapanınca pozisyon sıfırlanır; sonraki yeni pozisyonda (100 → 90'da 2 BTC ekleme) ölçüm yeniden başlar: 1 zararda ekleme, kat 2."""
    rows = [fill("BTC", "B", 2, 90, 1, 1), fill("BTC", "B", 4, 80, 2, 3), fill("BTC", "A", 7, 85, 3, 7, "-10"),
            fill("BTC", "B", 1, 100, 4, 0), fill("BTC", "B", 2, 90, 5, 1)]
    res = martingale_olcusu(rows, kat_esik=2.0)
    assert res["zararda_ekleme_sayisi"] == 1 and res["katlama_orani"] == 1.0 and res["en_buyuk_kat"] == pytest.approx(2.0)
    old_style = rows[:3]                                                         # yalnız devralınan pozisyon: hiçbir şey ölçülmez
    assert martingale_olcusu(old_style) == {"zararda_ekleme_sayisi": 0, "katlama_orani": 0.0, "en_buyuk_kat": 0.0, "atlanan_satir": 0}


def test_devralinan_pozisyon_ters_donunce_yeni_giris_bilinir():
    """1 BTC long devralınır; 3 BTC satış → 2 BTC short'a döner (giriş = 100, artık bilinir); 110'da 2 BTC short ekleme zararda (px > giriş), kat 1."""
    rows = [fill("BTC", "A", 3, 100, 1, 1, "5"), fill("BTC", "A", 2, 110, 2, -2)]
    res = martingale_olcusu(rows, kat_esik=1.0)
    assert res["zararda_ekleme_sayisi"] == 1 and res["en_buyuk_kat"] == pytest.approx(1.0)


def test_devralinan_pozisyon_bir_coinde_digerini_etkilemez():
    rows = [fill("BTC", "B", 1, 90, 1, 1), fill("ETH", "B", 1, 100, 2, 0), fill("ETH", "B", 2, 90, 3, 1)]
    assert martingale_olcusu(rows)["zararda_ekleme_sayisi"] == 1                  # yalnız ETH ölçülür


def test_bozuk_satirlar_atlanan_satir_olarak_sayilir():
    rows = [fill("BTC", "B", 1, 100, 1, 0), {"coin": "BTC", "px": "abc", "sz": "1", "side": "B", "time": "2"}, {"coin": "BTC", "sz": "1", "side": "B", "time": "3"},
            {"coin": "", "px": "1", "sz": "1", "side": "B", "time": "4"}, {"coin": "BTC", "px": "1", "sz": "1", "side": "X", "time": "5"}, "bozuk",
            {"coin": "BTC", "px": "nan", "sz": "1", "side": "B", "time": "6"}, fill("BTC", "B", 2, 90, 7, 1)]
    for fn in (martingale_olcusu, tek_coin_yogunlugu, ekleme_derinligi):
        assert fn(rows)["atlanan_satir"] == 6
    assert martingale_olcusu(rows)["zararda_ekleme_sayisi"] == 1                  # geçerli satırlar etkilenmez


def test_spot_dolumlar_perp_suzgeciyle_dislanir_ve_atlanan_sayilmaz():
    rows = [fill("BTC", "B", 1, 100, 1, 0), fill("PURR/USDC", "B", 1, 1, 2, 0, "500"), fill("@107", "B", 1, 1, 3, 0, "500")]
    res = tek_coin_yogunlugu(rows)
    assert res["coin_sayisi"] == 1 and res["atlanan_satir"] == 0
    assert tek_coin_yogunlugu([fill("PURR/USDC", "A", 1, 1, 1, 1, "500")])["hhi"] == 0.0


def test_esit_zamanli_dolumlarda_giris_sirasi_korunur_ve_esit_payda_alfabetik():
    rows = [fill("BTC", "B", 1, 100, 5, 0), fill("BTC", "B", 2, 90, 5, 1)]       # aynı ms: giriş sırası (kararlı sıralama)
    assert martingale_olcusu(rows)["zararda_ekleme_sayisi"] == 1
    tie = [fill("ETH", "A", 1, 1, 1, 1, "10"), fill("BTC", "A", 1, 1, 2, 1, "10")]
    assert tek_coin_yogunlugu(tie)["en_buyuk_coin"] == "BTC"
