"""CT-Kapı v1.1 (docs/GOREV_TRADER_SECIMI.md): plasebo, tarz, katman, kıyas, kapsam, ilişkili hesap, keşif. Ağsız."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest
import requests

from copytrade import kesif
from copytrade.kapi import (basket_returns, benchmark_kind, binance_availability, binance_symbol, classify_style,
                            delay_for_style, finalize, gate_status, katman, market_shares, merge_shards,
                            missing_addresses, placebo_scores, randomize_trades, short_trade_share)
from copytrade.kurallar import load_rules
from copytrade.tarama import PublicClient

HOUR = 3_600_000
RULES = load_rules()
START, END = pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-05", tz="UTC")


def trade(coin, hours=2, **extra):
    return {"coin": coin, "side": "B", "size_ratio": .1, "holding_hours": hours, **extra}


def per_coin_overlaps(placed):
    for coin in {x["coin"] for x in placed}:
        items = sorted((x for x in placed if x["coin"] == coin), key=lambda x: x["open_time"])
        if any(a["close_time"] > b["open_time"] for a, b in zip(items, items[1:])):
            return True
    return False


# ---------------------------------------------------------------- plasebo
def test_placebo_places_trader_with_simultaneous_positions_in_two_coins():
    # Eski global çakışma yasağı yoğun, çok coinli traderda yerleştiremezdi; şimdi her coin kendi içinde çakışmasız.
    trades = [trade("BTC") for _ in range(20)] + [trade("ETH", 3) for _ in range(20)]
    notes: list[str] = []
    for seed in range(20):
        placed = randomize_trades(trades, START, END, seed, notes)
        assert len(placed) == 40 and not per_coin_overlaps(placed)
        assert all(START <= x["open_time"] and x["close_time"] <= END for x in placed)
    assert notes == []
    first, again = randomize_trades(trades, START, END, 4), randomize_trades(trades, START, END, 4)
    assert first == again
    assert {(x["coin"], x["side"], x["size_ratio"], x["holding_hours"]) for x in first} == {
        (x["coin"], x["side"], x["size_ratio"], x["holding_hours"]) for x in trades}
    # coinler birbirine değebilir: iki coinin toplamı pencereye sığmasa bile her biri tek başına sığar
    heavy = [trade("BTC", 40) for _ in range(2)] + [trade("ETH", 40) for _ in range(2)]  # 160 sa > 96 sa pencere değil: coin başına 80
    assert len(randomize_trades(heavy, START, END, 1)) == 4


def test_coin_that_does_not_fit_even_alone_is_circularly_shifted_with_a_note():
    opened = START + pd.Timedelta(hours=1)
    trades = [trade("BTC", 20, open_time=opened + pd.Timedelta(hours=25 * i), close_time=opened + pd.Timedelta(hours=25 * i + 20))
              for i in range(5)]  # 5 × 20 sa = 100 sa > 96 sa pencere
    notes: list[str] = []
    placed = randomize_trades(trades, START, END, 3, notes)
    assert notes == ["BTC: dairesel kaydırma"] and len(placed) == 5
    assert all(START <= x["open_time"] and x["close_time"] <= END for x in placed)
    assert placed == randomize_trades(trades, START, END, 3)  # tohumla aynı sonuç
    with pytest.raises(ValueError, match="placement unavailable"):
        randomize_trades([trade("BTC", 20) for _ in range(5)], START, END, 3)  # özgün saatler yoksa kaydırılamaz
    with pytest.raises(ValueError, match="does not fit"):
        randomize_trades([trade("BTC", 200)], START, END, 3)


def test_placebo_scores_1000_for_overlapping_two_coin_trader_with_delay():
    fills = [{"time": 0, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0"},
             {"time": HOUR, "coin": "ETH", "side": "B", "sz": "1", "px": "100", "startPosition": "0"},
             {"time": 3 * HOUR, "coin": "BTC", "side": "A", "sz": "1", "px": "101", "startPosition": "1"},
             {"time": 4 * HOUR, "coin": "ETH", "side": "A", "sz": "1", "px": "101", "startPosition": "1"}]
    candles = {coin: [{"t": i * HOUR, "o": str(100 + i % 3)} for i in range(120)] for coin in ("BTC", "ETH")}
    notes: list[str] = []
    scores = placebo_scores(fills, candles, 1_000, pd.Timestamp(0, unit="ms", tz="UTC"),
                            pd.Timestamp(100 * HOUR, unit="ms", tz="UTC"), delay_minutes=120, notes=notes)
    assert len(scores) == 1000 and notes == []
    assert placebo_scores([], candles, 1_000, START, END) == []


# ---------------------------------------------------------------- tarz ve eşikler
def test_style_boundaries():
    assert [classify_style(x, RULES) for x in (None, .99, 1.0, 23.99, 24.0, 200)] == [None, "scalp", "intraday", "intraday", "swing", "swing"]
    assert (delay_for_style("intraday", RULES), delay_for_style("swing", RULES)) == (30, 120)
    assert (delay_for_style("intraday", RULES, "stres_gecikme_dk"), delay_for_style("swing", RULES, "stres_gecikme_dk")) == (120, 480)
    assert RULES["kisa_islem_payi_max"] == .25 and RULES["kisa_islem_dk"] == {"intraday": 15, "swing": 120}


def round_trips(durations_minutes):
    fills, at = [], 0
    for minutes in durations_minutes:
        fills.append({"time": at, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0", "closedPnl": "0", "fee": "0"})
        fills.append({"time": at + minutes * 60_000, "coin": "BTC", "side": "A", "sz": "1", "px": "101", "startPosition": "1", "closedPnl": "1", "fee": "0"})
        at += (minutes + 600) * 60_000
    return fills


def test_short_trade_share_depends_on_style():
    fills = round_trips([10, 20, 180, 300])
    assert short_trade_share(fills, "intraday", RULES) == .25      # yalnız 10 dk < 15 dk
    assert short_trade_share(fills, "swing", RULES) == .5          # 10 ve 20 dk < 120 dk
    assert short_trade_share([], "intraday", RULES) is None


def base_metrics(**over):
    return {"complete_data": True, "history_days": 200, "closed_trades": 80, "active_months": 8, "median_holding_hours": 3,
            "median_leverage": 2, "max_leverage": 8, "kisa_islem_payi": .25, "profitable_month_ratio": .7, "largest_trade_share": .2,
            "profit_factor_without_best": 1.5, "martingale_signal": False, **over}


def test_step3_rules_by_style():
    g = lambda copy_net=.1, **m: gate_status(base_metrics(**m), copy_net, None, None, RULES)["adim3"]
    assert g() == "Geçti"
    assert g(kisa_islem_payi=.26) == "Kaldı"            # scalp ayıklama sınırı
    assert g(median_holding_hours=.5) == "Kaldı"        # scalp
    assert g(copy_net=0) == "Kaldı" and g(copy_net=None) == "Kaldı"
    assert g(median_leverage=3.1) == "Kaldı" and g(max_leverage=10.1) == "Kaldı"
    assert g(median_holding_hours=30) == "Geçti"        # swing
    # alfa t eşiği adım 6 kuralı değişmedi
    assert gate_status(base_metrics(), .1, .05, {"alfa_yillik": 1, "nw_t": 2}, RULES)["adim6"] == "Geçti"


def test_layers():
    ok = {f"adim{i}": "Geçti" for i in range(1, 8)}
    assert katman(ok) == "kopyalanabilir"
    assert katman({**ok, "adim7": "Kaldı", "adim5": "Kaldı"}) == "izleme_adayi"   # 4–7 ne olursa olsun
    assert katman({**ok, "adim7": "Yetersiz"}) == "izleme_adayi"
    assert katman({**ok, "adim3": "Kaldı"}) == "yok" and katman({**ok, "adim1": "Yetersiz"}) == "yok" and katman({}) == "yok"


def test_alpha_benchmark_choice_and_basket():
    assert benchmark_kind(.5, RULES) == "BTC" and benchmark_kind(.4999, RULES) == "sepet" and benchmark_kind(1, RULES) == "BTC"
    fills = [{"coin": "BTC", "px": "100", "sz": "1"}, {"coin": "xyz:NVDA", "px": "100", "sz": "1"}, {"coin": "xyz:GOLD", "px": "100", "sz": "2"}]
    shares = market_shares(fills, {"BTCUSDT", "NVDAUSDT", "XAUUSDT"})
    assert shares["pay_kripto"] == .25 and shares["pay_hisse"] == .25 and shares["pay_emtia"] == .5 and shares["binance_payi"] == 1
    assert market_shares(fills, None)["binance_payi"] is None
    day = 86_400_000
    up = [{"t": i * day, "c": str(100 * 1.1 ** i)} for i in range(3)]
    flat = [{"t": i * day, "c": "50"} for i in range(3)]
    basket = basket_returns({"A": up, "B": flat}, ["A", "B", "yok"])
    assert round(basket.iloc[1], 6) == .05 and round(basket.iloc[2], 6) == .05   # eşit ağırlık: (%10 + %0) / 2


# ---------------------------------------------------------------- Binance karşılığı (HIP-3)
def test_hip3_binance_mapping():
    listed = {"XAUUSDT", "NVDAUSDT", "XAGUSDT", "BZUSDT", "BTCUSDT"}
    assert binance_symbol("xyz:GOLD") == "XAUUSDT" and binance_symbol("xyz:SILVER") == "XAGUSDT"
    assert binance_symbol("xyz:BRENTOIL") == "BZUSDT" and binance_symbol("xyz:NVDA") == "NVDAUSDT"
    assert binance_symbol("kPEPE") == "1000PEPEUSDT" and binance_symbol("@107") == "yok" and binance_symbol("PURR/USDC") == "yok"
    assert [binance_availability(c, listed) for c in ("xyz:GOLD", "xyz:NVDA", "xyz:ZZZZ", "BTC", "@1")] == ["var", "var", "yok", "var", "yok"]
    assert binance_availability("xyz:NVDA", None) == "bilinmiyor"


# ---------------------------------------------------------------- 5xx yeniden deneme, eksikleri tamamla
class FakeResponse:
    def __init__(self, status, body=None):
        self.status_code, self.body = status, body if body is not None else {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self.body


class FakeSession:
    def __init__(self, statuses):
        self.statuses, self.calls = list(statuses), 0

    def request(self, *_a, **_k):
        self.calls += 1
        return FakeResponse(self.statuses.pop(0), {"ok": True})


class NoLimit:
    def acquire(self, _weight):
        pass


def test_server_errors_are_retried_three_times_with_growing_waits():
    sleeps: list[float] = []
    session = FakeSession([500, 502, 200])
    assert PublicClient(session, NoLimit(), sleeps.append).info({"type": "x"}) == {"ok": True}
    assert session.calls == 3 and sleeps == [2, 6]
    failing, sleeps = FakeSession([500, 503, 500, 200]), []
    with pytest.raises(requests.HTTPError):
        PublicClient(failing, NoLimit(), sleeps.append).info({"type": "x"})
    assert failing.calls == 3 and sleeps == [2, 6]
    limited, sleeps = FakeSession([429, 200]), []
    assert PublicClient(limited, NoLimit(), sleeps.append).info({"type": "x"}) == {"ok": True} and sleeps == [5]


def test_missing_addresses_selects_absent_and_data_error_rows():
    leaders = [{"address": a} for a in ("0xa", "0xb", "0xc", "0xd")]
    reference = pd.DataFrame({"address": ["0xa", "0xb", "0xc"], "neden": [None, "veri hatası: HTTPError: 500", None]})
    assert [x["address"] for x in missing_addresses(leaders, reference)] == ["0xb", "0xd"]
    assert missing_addresses(leaders, None) == leaders


def result_row(address, **over):
    row = {"address": address, "asama1": "Geçti", "complete_data": True, "history_days": 400, "account_age_days": 500, "tarz": "swing",
           "adim1": "Geçti", "adim2": "Geçti", "adim3": "Geçti", "adim4": "Geçti", "adim5": "Kaldı", "adim6": "Geçti"}
    return {**row, **over}


def test_merge_completes_existing_day_without_duplicate_rows(tmp_path: Path):
    day = tmp_path / "root" / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    pd.DataFrame([result_row("0xa", katman="izleme_adayi"), {"address": "0xb", "asama1": "Yetersiz", "neden": "veri hatası: HTTPError: 500", "katman": "yok"}]).to_csv(day / "sonuc.csv", index=False)
    (day / "evren.json").write_text('{"evren": 3}')
    shard = tmp_path / "shards" / "stage1-0" / "2026-10-28"
    shard.mkdir(parents=True)
    pd.DataFrame([{"address": "0xb", "asama1": "Yetersiz"}, result_row("0xc", closed_trades=60)]).to_csv(shard / "sonuc.csv", index=False)
    (shard / "evren.json").write_text('{"evren": 3}')
    merge_shards(tmp_path / "shards", tmp_path / "root")
    table = pd.read_csv(day / "sonuc.csv")
    assert sorted(table.address) == ["0xa", "0xb", "0xc"] and table.address.is_unique
    assert "veri hatası" not in " ".join(table.neden.dropna().astype(str))   # hatalı satır yeniden işlenen satırla değişti
    report = (day / "RAPOR.md").read_text(encoding="utf-8")
    assert "İşlenen / evren: 3 / 3" in report and "%100.0" in report and "tarza göre" in report and "izleme_adayi" in report


def test_finalize_adds_layer_and_young_candidate_flag():
    table = pd.DataFrame([result_row("0xold", history_days=365, account_age_days=800),
                          result_row("0xyoung", history_days=250, account_age_days=250),
                          result_row("0xnone", adim3="Kaldı")])
    out = finalize(table, RULES).set_index("address")
    assert out.loc["0xold", "katman"] == "izleme_adayi" and not out.loc["0xold", "genc_aday"]
    assert bool(out.loc["0xyoung", "genc_aday"]) and out.loc["0xyoung", "gecmis_gun"] == 250
    assert out.loc["0xnone", "katman"] == "yok"


# ---------------------------------------------------------------- ilişkili hesap ve keşif.json
ME, SUB, VAULT, PAL, AGENT = (f"0x{n * 40}" for n in "12345")


class RelatedClient:
    def __init__(self, fail=()):
        self.fail = set(fail)

    def _maybe(self, name, value):
        if name in self.fail:
            raise requests.RequestException(name)
        return value

    def sub_accounts(self, address): return self._maybe("subAccounts", [{"name": "s", "subAccountUser": SUB, "master": address}])
    def vault_equities(self, address): return self._maybe("userVaultEquities", [{"vaultAddress": VAULT, "equity": "1"}])
    def vault_details(self, vault): return {"leader": ME}
    def extra_agents(self, address): return self._maybe("extraAgents", [{"address": AGENT, "name": "bot"}])
    def non_funding_ledger(self, address, start): return [
        {"time": 1, "delta": {"type": "internalTransfer", "usdc": "5", "user": ME, "destination": PAL}},
        {"time": 2, "delta": {"type": "deposit", "usdc": "5"}}]


def test_related_accounts_flags_from_fixed_responses():
    found = kesif.related_accounts(RelatedClient(), ME, datetime(2026, 10, 28, tzinfo=UTC))
    assert set(found["adresler"]) == {SUB, VAULT, PAL} and found["ajanlar"] == [AGENT] and found["transfer"] == [PAL]
    assert found["not"] == "alt hesap 1; vault lideri 1; API ajanı 1; iç transfer karşı adres 1"
    degraded = kesif.related_accounts(RelatedClient(fail={"subAccounts"}), ME, datetime(2026, 10, 28, tzinfo=UTC))
    assert "kontrol edilemedi: subAccounts" in degraded["not"] and SUB not in degraded["adresler"]
    assert kesif.counterparties([{"delta": {"type": "withdraw", "user": PAL}}], ME) == []


def test_link_candidates_shared_agent_and_transfer():
    a, b = "0x" + "a" * 40, "0x" + "b" * 40
    info = {a: {"adresler": [], "ajanlar": [AGENT], "transfer": [b], "not": ""},
            b: {"adresler": [], "ajanlar": [AGENT], "transfer": [], "not": "alt hesap 1"}}
    kesif.link_candidates(info)
    assert b in info[a]["adresler"] and a in info[b]["adresler"]
    assert info[a]["not"] == "aday adresle iç transfer; ortak API ajanı" and info[b]["not"] == "alt hesap 1; ortak API ajanı"


def test_weekly_curve_is_365_day_weekly_pnl_over_account():
    day = 86_400_000
    t0 = 1_700_000_000_000
    pnl = [[t0 + i * 7 * day, str(100 * i)] for i in range(60)]
    values = [[t0 + i * 7 * day, "10000"] for i in range(60)]
    curve = kesif.weekly_curve([["allTime", {"pnlHistory": pnl, "accountValueHistory": values}]])
    assert curve[0][1] == 0.0 or curve[0][1] > 0 and len(curve) <= 54
    assert all(len(point) == 2 for point in curve) and curve == sorted(curve)
    assert kesif.weekly_curve([]) == []


def test_kesif_schema_filtering_and_order():
    table = pd.DataFrame([
        result_row("0xnone", katman="yok", genc_aday=False, nw_t=9.0),
        result_row("0xgenc", katman="kopyalanabilir", genc_aday=True, nw_t=5.0, gecmis_gun=250),
        result_row("0xizle1", katman="izleme_adayi", genc_aday=False, nw_t=1.0, gecmis_gun=400, plasebo_p=.03, alfa_kiyas="BTC", pay_kripto=.7, pay_hisse=.3),
        result_row("0xizle2", katman="izleme_adayi", genc_aday=False, nw_t=3.0, gecmis_gun=400),
        result_row("0xkop", katman="kopyalanabilir", genc_aday=False, nw_t=2.0, gecmis_gun=500)])
    out = kesif.build_kesif(table, datetime(2026, 10, 28, tzinfo=UTC), 12461, {"0xkop": [["2026-01-01", 0.0]]},
                            {"0xkop": {"adresler": [SUB], "not": "alt hesap 1"}}, RULES)
    assert [e["adres"] for e in out["adaylar"]] == ["0xkop", "0xgenc", "0xizle2", "0xizle1"]   # katman, genç sonra, alfa_t
    assert out["surum"] == 1 and out["evren"] == 12461 and out["islenen"] == 5 and out["uretildi"].endswith("Z")
    first = out["adaylar"][0]
    assert {"adres", "tarz", "katman", "genc_aday", "gecmis_gun", "kapanan_islem", "aktif_ay", "hesap_degeri", "piyasa_payi", "binance_payi",
            "medyan_tutma_sa", "kisa_islem_payi", "medyan_kaldirac", "max_kaldirac", "kopya", "karli_ay_orani", "en_buyuk_islem_payi",
            "pf_en_iyisiz", "max_dusus", "getiri_12a", "plasebo_p", "alfa_t", "alfa_kiyas", "bhy_q", "adimlar", "iliskili_not", "egri"} <= set(first)
    assert set(first["kopya"]) == {"g30", "g120", "g480"} and set(first["adimlar"]) == {str(i) for i in range(1, 8)}
    assert first["iliskili_not"] == "alt hesap 1" and first["iliskili_adresler"] == SUB and first["egri"] == [["2026-01-01", 0.0]]
    assert out["adaylar"][3]["piyasa_payi"] == {"kripto": .7, "hisse": .3} and out["adaylar"][3]["alfa_kiyas"] == "BTC"
    json.dumps(out, allow_nan=False)                      # NaN/sonsuz yok
    assert first["adimlar"]["5"]["durum"] == "Kaldı" and "plasebo" in first["adimlar"]["5"]["neden"]


def test_none_metrics_fail_the_step_instead_of_raising():
    # Hesaplanamayan ölçüt (None) eskiden TypeError → satır "veri hatası" oluyordu; şimdi adım Kaldı.
    metrics = base_metrics(profit_factor_without_best=None, largest_trade_share=None, median_leverage=None, max_leverage=float("nan"))
    status = gate_status(metrics, .1, None, None, RULES)
    assert status["adim3"] == "Kaldı" and status["adim4"] == "Kaldı"


def test_legacy_same_day_results_are_not_mixed_into_v11_merge(tmp_path: Path):
    day = tmp_path / "root" / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    pd.DataFrame([{"address": "0xold", "asama1": "Geçti", "adim1": "Geçti", "adim2": "Geçti", "adim3": "Geçti"}]).to_csv(day / "sonuc.csv", index=False)  # v1: katman yok
    shard = tmp_path / "shards" / "stage1-0" / "2026-10-28"
    shard.mkdir(parents=True)
    pd.DataFrame([result_row("0xnew")]).to_csv(shard / "sonuc.csv", index=False)
    merge_shards(tmp_path / "shards", tmp_path / "root")
    assert list(pd.read_csv(day / "sonuc.csv").address) == ["0xnew"]
