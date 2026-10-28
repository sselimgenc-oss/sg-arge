"""Kırmızı bayrak sütunları (docs/GOREV_SECIM_V1.md Ek): her biri elle hesaplanmış altın örnek; bilgi amaçlı, seçimi değiştirmez."""
import pandas as pd
import requests

from copytrade import bayrak, secim
from copytrade.kurallar import load_rules
from tests.test_secim import TABLE, addr

A, M, B = addr("a"), addr("b"), addr("c")


def test_rol():
    assert bayrak.rol({"role": "vault"}) == "vault"
    assert bayrak.rol({"role": "user"}) == "user"
    assert bayrak.rol({"role": "subAccount", "data": {"master": M.upper().replace("0X", "0x")}}) == f"subAccount:{M}"


def test_vault_orani():
    # (300 + 200,5) / 1001 = 0,5
    assert bayrak.vault_orani([{"equity": "300"}, {"equity": "200.5"}], 1001.0) == 0.5
    assert bayrak.vault_orani([], 1000.0) == 0.0 and bayrak.vault_orani([{"equity": "5"}], 0.0) is None


def test_funding_payi_isaretli():
    funding = [{"delta": {"usdc": "10"}}, {"delta": {"usdc": "-2.5"}}, {"delta": {"usdc": "4"}}]       # toplam 11,5
    fills = [{"closedPnl": "20"}, {"closedPnl": "-5"}, {"closedPnl": "10"}]                              # PnL 25
    assert bayrak.funding_payi(funding, fills) == 0.46
    assert bayrak.funding_payi([{"delta": {"usdc": "-3"}}], [{"closedPnl": "6"}]) == -0.5               # işaretli
    assert bayrak.funding_payi(funding, [{"closedPnl": "5"}, {"closedPnl": "-5"}]) is None             # PnL 0 → oran yok


def test_hacim_orani():
    portfolio = [["day", {"vlm": "5"}], ["month", {"vlm": "250000"}], ["allTime", {"vlm": "9"}]]
    assert bayrak.hacim_orani(portfolio, 50000.0) == 5.0                                                 # 250000 / 50000
    assert bayrak.hacim_orani([["day", {"vlm": "5"}]], 50000.0) is None


def test_ters_pozisyon():
    own = {"BTC": 1.0, "ETH": -2.0}
    assert bayrak.ters_pozisyon(own, [{"BTC": 3.0}, {"ETH": -1.0, "SOL": 5.0}]) is False               # aynı yön / farklı coin
    assert bayrak.ters_pozisyon(own, [{"ETH": 4.0}]) is True                                            # ETH: −2 karşı +4
    state = {"assetPositions": [{"position": {"coin": "BTC", "szi": "-0.5"}}, {"position": {"coin": "ETH", "szi": "0.0"}}]}
    assert bayrak.pozisyonlar(state) == {"BTC": -0.5}


class Fake:
    """userRole / userVaultEquities / userFunding / userFills / portfolio / subAccounts / clearinghouseState yanıtlarını taklit eder."""
    def __init__(self, role, positions, subs, fail=()):
        self.role, self.positions, self.subs, self.fail = role, positions, subs, set(fail)

    def info(self, payload, weight=20):
        kind = payload["type"]
        if kind in self.fail:
            raise requests.RequestException(kind)
        if kind == "userRole":
            return self.role
        if kind == "clearinghouseState":
            return {"assetPositions": [{"position": {"coin": c, "szi": str(z)}} for c, z in self.positions[payload["user"]].items()]}
        if kind == "userFunding":
            return [{"time": 1, "delta": {"coin": "BTC", "usdc": "10"}}, {"time": 2, "delta": {"coin": "ETH", "usdc": "-2.5"}}]
        raise AssertionError(kind)

    def vault_equities(self, address):
        if "userVaultEquities" in self.fail:
            raise requests.RequestException("v")
        return [{"equity": "250"}]

    def sub_accounts(self, address):
        return self.subs

    def fills(self, address, start):
        return [{"closedPnl": "30"}]

    def portfolio(self, address):
        return [["month", {"vlm": "5000"}]]


def sub(user, positions):
    return {"subAccountUser": user, "clearinghouseState": {"assetPositions": [{"position": {"coin": c, "szi": str(z)}} for c, z in positions.items()]}}


def test_alt_hesap_ters_sub_hesap_ve_master():
    # A (alt hesap) BTC long; kardeş B BTC short → evet
    client = Fake({"role": "subAccount", "data": {"master": M}}, {A: {"BTC": 1.0}, M: {}}, [sub(A, {"BTC": 1.0}), sub(B, {"BTC": -2.0})])
    assert bayrak.alt_hesap_ters(A, f"subAccount:{M}", client) == "evet"
    # kardeş de long, master'ın kendisi short → evet (master dahil)
    client = Fake({}, {A: {"BTC": 1.0}, M: {"BTC": -1.0}}, [sub(A, {"BTC": 1.0}), sub(B, {"BTC": 2.0})])
    assert bayrak.alt_hesap_ters(A, f"subAccount:{M}", client) == "evet"
    # kendisi hariç tutulur: yalnız kendi pozisyonu varsa ters yok
    client = Fake({}, {A: {"BTC": 1.0}, M: {"BTC": 1.0}}, [sub(A, {"BTC": 1.0}), sub(B, {"ETH": -1.0})])
    assert bayrak.alt_hesap_ters(A, f"subAccount:{M}", client) == "hayır"
    # master olan hesap kendi alt hesaplarına karşı bakılır
    client = Fake({}, {A: {"BTC": 1.0}}, [sub(B, {"BTC": -1.0})])
    assert bayrak.alt_hesap_ters(A, "user", client) == "evet"


def test_hesapla_bes_sutun_ve_kontrol_edilemedi():
    client = Fake({"role": "subAccount", "data": {"master": M}}, {A: {"BTC": 1.0}, M: {}}, [sub(B, {"BTC": -2.0})])
    out = bayrak.hesapla(client, A, 1000.0, now_ms=10**12)
    assert out == {"bayrak_rol": f"subAccount:{M}", "bayrak_vault_orani": 0.25,                          # 250 / 1000
                   "bayrak_funding_payi": 0.25,                                                          # 7,5 / 30
                   "bayrak_alt_hesap_ters": "evet", "bayrak_hacim_orani": 5.0, "bayrak_not": ""}          # 5000 / 1000
    broken = Fake({"role": "vault"}, {A: {}}, [], fail=("userVaultEquities", "userFunding"))
    out = bayrak.hesapla(broken, A, 1000.0, now_ms=10**12)
    assert out["bayrak_rol"] == "vault" and out["bayrak_hacim_orani"] == 5.0 and out["bayrak_alt_hesap_ters"] == "hayır"
    assert out["bayrak_vault_orani"] is None and out["bayrak_funding_payi"] is None
    assert out["bayrak_not"] == "kontrol edilemedi: bayrak_vault_orani, bayrak_funding_payi"
    dead = Fake({}, {A: {}}, [], fail=("userRole", "clearinghouseState"))
    out = bayrak.hesapla(dead, A, 1000.0, now_ms=10**12)
    assert out["bayrak_rol"] is None and out["bayrak_alt_hesap_ters"] == "kontrol edilemedi"
    assert "bayrak_rol" in out["bayrak_not"] and "bayrak_alt_hesap_ters" in out["bayrak_not"]


def test_bayrak_yalniz_aday_kati_ve_secimi_degistirmez():
    rules = load_rules()
    calls = []

    def fn(address, value):
        calls.append(address)
        return {"bayrak_rol": "vault", "bayrak_vault_orani": 0.9, "bayrak_funding_payi": 0.9, "bayrak_alt_hesap_ters": "evet",
                "bayrak_hacim_orani": 99.0, "bayrak_not": ""}

    plain = secim.sec(TABLE, "2026-10-28", [], [], rules)
    flagged = secim.sec(TABLE, "2026-10-28", [], [], rules, fn)
    assert sorted(calls) == [addr("2"), addr("a")]                                       # gerçek kurallarla aday katı (2 adres) dışına istek yok
    assert flagged["sayilar"] == plain["sayilar"] and flagged["kontrol"] == plain["kontrol"]
    assert {a for a, e in flagged["adresler"].items() if e["kol"] == "oda"} == {a for a, e in plain["adresler"].items() if e["kol"] == "oda"}
    assert "bayrak_rol" in flagged["adresler"][addr("a")] and "bayrak_rol" not in flagged["adresler"][addr("d")]
    text = secim.rapor(flagged, TABLE, {"hesap": "v", "kapsam": 1.0, "durum": "tamam"})
    assert "## Kırmızı bayraklar (bilgi; kimseyi elemez" in text
