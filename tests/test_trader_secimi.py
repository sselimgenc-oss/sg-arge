"""CT-Kapı v1.1 (docs/GOREV_TRADER_SECIMI.md): plasebo, tarz, katman, kıyas, kapsam, ilişkili hesap, keşif. Ağsız."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest
import requests

from copytrade import kesif
from copytrade.kapi import (HESAP_SURUMU, SanityError, activity_metrics, basket_returns, delay_test_days, family_mask, night_share, benchmark_kind, binance_availability, binance_symbol, classify_style,
                            delay_for_style, finalize, gate_status, katman, market_shares, merge_shards,
                            missing_addresses, placebo_scores, randomize_trades, read_binance_universe, short_trade_share)
from copytrade.kurallar import load_rules
from copytrade.tarama import PublicClient

HOUR = 3_600_000
RULES = load_rules()
START, END = pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-05", tz="UTC")


def test_dondurulmus_binance_listesi_tum_parcalarda_ayni_kaynaktir(tmp_path):
    """Altın örnek: planın tek listesi hem sembolü hem engelli kaynağı aynen taşır."""
    path = tmp_path / "binance_vadeli.txt"
    path.write_text("# https://fapi.binance.com/fapi/v1/exchangeInfo | 2026-10-29T00:00:00Z\nBTCUSDT\nETHUSDT\n", encoding="utf-8")
    symbols, note = read_binance_universe(path)
    assert symbols == {"BTCUSDT", "ETHUSDT"} and note == "dondurulmuş"
    path.write_text("# kaynak | erişim engeli: HTTP 451\n", encoding="utf-8")
    assert read_binance_universe(path) == (None, "HTTP 451")


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


def test_placebo_scores_10000_for_overlapping_two_coin_trader_with_delay():
    fills = [{"time": 0, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0"},
             {"time": HOUR, "coin": "ETH", "side": "B", "sz": "1", "px": "100", "startPosition": "0"},
             {"time": 3 * HOUR, "coin": "BTC", "side": "A", "sz": "1", "px": "101", "startPosition": "1"},
             {"time": 4 * HOUR, "coin": "ETH", "side": "A", "sz": "1", "px": "101", "startPosition": "1"}]
    candles = {coin: [{"t": i * HOUR, "o": str(100 + i % 3)} for i in range(120)] for coin in ("BTC", "ETH")}
    notes: list[str] = []
    scores = placebo_scores(fills, candles, 1_000, pd.Timestamp(0, unit="ms", tz="UTC"),
                            pd.Timestamp(100 * HOUR, unit="ms", tz="UTC"), delay_minutes=120, notes=notes)
    assert len(scores) == RULES["plasebo_tekrar"] == 10_000 and notes == []
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
    assert "binance_payi" not in market_shares(fills, None)     # liste alınamadıysa sütun hiç yazılmaz (sessiz boş sütun yok)
    assert "binance_payi" not in market_shares([], None)        # liste yok + hacim 0 → anahtar yok (run 24 hatası)
    assert market_shares([], {"BTCUSDT"})["binance_payi"] is None   # liste var + hacim 0 → tanımlı boş
    assert market_shares([{"coin": "BTC", "px": "100", "sz": "1"}, {"coin": "FOO", "px": "100", "sz": "3"}], {"BTCUSDT"})["binance_payi"] == .25
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
           "adim1": "Geçti", "adim2": "Geçti", "adim3": "Geçti", "adim4": "Geçti", "adim5": "Kaldı", "adim6": "Geçti",
           # akıl sağlığı kapısı (18d) metrik üreten satırda bu sütunların dolu olmasını ister
           "closed_trades": 80, "median_holding_hours": 30, "median_leverage": 2.0, "max_leverage": 8.0, "candle_coverage": 1.0,
           "profitable_month_ratio": .6, "max_drawdown": .2, "gecikme_30dk_net": .1, "gecikme_120dk_net": .05, "kisa_islem_payi": .1,
           "pay_kripto": 1.0, "nw_t": 1.0}
    return {**row, **over}


def test_merge_completes_existing_day_without_duplicate_rows(tmp_path: Path):
    day = tmp_path / "root" / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    # Aynı hesap sürümüyle üretilmiş önceki satırlar (kesilen aynı gün koşusu) korunur; sürümsüz satırlar korunmaz (aşağıdaki test).
    pd.DataFrame([result_row("0xa", katman="izleme_adayi", plasebo_p=.01, hesap=HESAP_SURUMU),
                  {"address": "0xb", "asama1": "Yetersiz", "neden": "veri hatası: HTTPError: 500", "katman": "yok", "hesap": HESAP_SURUMU}]).to_csv(day / "sonuc.csv", index=False)
    (day / "evren.json").write_text('{"evren": 3}')
    shard = tmp_path / "shards" / "stage1-0" / "2026-10-28"
    shard.mkdir(parents=True)
    pd.DataFrame([{"address": "0xb", "asama1": "Yetersiz"}, result_row("0xc", closed_trades=60, plasebo_p=.02)]).to_csv(shard / "sonuc.csv", index=False)
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


def test_related_pool_uses_all_gate_pool_not_only_layers():
    """Altın örnek: katmanı yok adres de adım 1–2 havuzunda bağlantı için taranır."""
    frame = pd.DataFrame([
        {"address": "0xa", "adim1": "Geçti", "adim2": "Geçti", "katman": "yok"},
        {"address": "0xb", "adim1": "Geçti", "adim2": "Geçti", "katman": "izleme_adayi"},
        {"address": "0xc", "adim1": "Yetersiz", "adim2": "Geçti", "katman": "yok"},
    ])
    assert kesif.related_pool(frame) == ["0xa", "0xb"]


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


def test_quick_run_keeps_pre_v11_rows_apart_as_eski_hesap_and_out_of_the_gate(tmp_path: Path):
    """Davranış değişikliği (görev: eski hesap karışmasın): hesap sürümü olmayan / farklı satırlar yeni sonuca girmez, kapıya sokulmaz,
    ``sonuc_eski_hesap.csv.gz``'ye ``durum = eski_hesap`` ile yazılır. Eski satırdaki 1,5e12 düşüş birleştirmeyi artık kırmaz."""
    day = tmp_path / "root" / "kapi" / "2026-10-28"
    day.mkdir(parents=True)
    pd.DataFrame([{"address": "0xold", "asama1": "Geçti", "max_drawdown": 1.5e12}, {"address": "0xnew", "asama1": "Yetersiz", "adim5": "Kaldı"}]).to_csv(day / "sonuc.csv", index=False)
    shard = tmp_path / "shards" / "stage1-0" / "2026-10-28"
    shard.mkdir(parents=True)
    pd.DataFrame([result_row("0xnew", plasebo_p=.04, hesap=HESAP_SURUMU)]).to_csv(shard / "sonuc.csv", index=False)
    statuses = merge_shards(tmp_path / "shards", tmp_path / "root")
    table = pd.read_csv(day / "sonuc.csv").set_index("address")
    assert list(table.index) == ["0xnew"] and table.loc["0xnew", "plasebo_p"] == .04 and table.loc["0xnew", "tarz"] == "swing"
    old = pd.read_csv(day / "sonuc_eski_hesap.csv.gz")
    assert sorted(old.address) == ["0xnew", "0xold"] and set(old.durum) == {"eski_hesap"}
    assert statuses["2026-10-28"]["eski_hesap_satir"] == 2 and statuses["2026-10-28"]["satir_kaynagi"] == {"bu_kosu": 1}


def test_sanity_failure_names_the_source_of_bad_rows(tmp_path: Path):
    shard = tmp_path / "shards" / "stage1-0" / "2026-10-28"
    shard.mkdir(parents=True)
    pd.DataFrame([result_row("0xbad", plasebo_p=.04, max_leverage=1.46e6, hesap=HESAP_SURUMU)]).to_csv(shard / "sonuc.csv", index=False)
    with pytest.raises(SanityError) as caught:
        merge_shards(tmp_path / "shards", tmp_path / "root")
    assert "bu_kosu" in str(caught.value) and "0xbad" in str(caught.value) and "max_leverage" in str(caught.value)


def test_progress_log_reports_stage_times_and_candle_requests():
    from copytrade.kapi import CandleCache, Progress
    lines: list[str] = []

    class Quiet:
        stats = {"istek": 0, "429": 0, "5xx": 0}
        limiter = type("L", (), {"waited": 0.0})()
        def candles(self, *a, **k): self.stats["istek"] += 1; return [{"t": 0, "o": "1"}]

    client = Quiet()
    cache = CandleCache(client, 0, 1)
    progress = Progress("0xabc…1234", client, cache, lines.append)
    cache.get("BTC"); cache.get("BTC"); cache.get("ETH")
    progress.stage("mumlar", "2 coin")
    progress.done("tamam")
    assert "mumlar" in lines[0] and "2 coin" in lines[0]
    assert "yeni mum isteği 2 coin, toplam istek 2" in lines[1] and "TOPLAM" in lines[1] and "mumlar" in lines[1]


def test_response_size_weight_candles_per_60_other_lists_per_20_and_stats_counted():
    class Limiter:
        def __init__(self): self.weights = []
        def acquire(self, weight): self.weights.append(weight)

    class Session:
        def request(self, *_a, **_k): return FakeResponse(200, [{}] * 120)

    limiter = Limiter()
    client = PublicClient(Session(), limiter, lambda _s: None)
    client.info({"type": "candleSnapshot"}, weight=20)
    client.info({"type": "userFills"}, weight=20)
    assert limiter.weights == [20, 2, 20, 6] and client.stats["istek"] == 2


# ---------------------------------------------------------------- görev 10–12: tekrar, aktiflik, rapor ölçütleri
DAY_MS = 86_400_000
NOW_MS = 1_800_000_000_000


def cycles(days_ago_list, coin="BTC"):
    """Her biri 2 saat süren kapanmış düz-düz döngüler; her giriş NOW'dan ``days_ago`` gün önce."""
    fills = []
    for index, ago in enumerate(days_ago_list):
        at = NOW_MS - int(ago * DAY_MS)
        fills.append({"time": at, "coin": coin, "side": "B", "sz": "1", "px": "100", "startPosition": "0", "closedPnl": "0", "fee": "0", "tid": 2 * index})
        fills.append({"time": at + 2 * HOUR, "coin": coin, "side": "A", "sz": "1", "px": "101", "startPosition": "1", "closedPnl": "1", "fee": "0", "tid": 2 * index + 1})
    return fills


def test_activity_thresholds_by_style_and_last_trade_age():
    twenty = cycles([1 + i for i in range(20)])
    assert activity_metrics(twenty, "intraday", NOW_MS, RULES) == {"son90_dongu": 20, "son_islem_gun": 0.9, "aktif": True}
    assert not activity_metrics(cycles([1 + i for i in range(19)]), "intraday", NOW_MS, RULES)["aktif"]       # 19 < 20
    assert activity_metrics(cycles([1, 2, 3, 4, 5]), "swing", NOW_MS, RULES)["aktif"]                          # swing ≥ 5
    assert not activity_metrics(cycles([1, 2, 3, 4]), "swing", NOW_MS, RULES)["aktif"]
    old_last = activity_metrics(cycles([31, 32, 33, 34, 35]), "swing", NOW_MS, RULES)
    assert old_last["son90_dongu"] == 5 and not old_last["aktif"]                                              # son işlem 31 gün önce
    assert activity_metrics(cycles([30.0 - 2 / 24 + 0.01, 40, 50, 60, 70]), "swing", NOW_MS, RULES)["aktif"]   # 30 gün sınırı içinde
    outside = activity_metrics(cycles([1, 2, 3, 4, 95]), "swing", NOW_MS, RULES)
    assert outside["son90_dongu"] == 4 and not outside["aktif"]                                                # 90 gün penceresi dışındaki sayılmaz
    assert activity_metrics([], "swing", NOW_MS, RULES) == {"son90_dongu": 0, "son_islem_gun": None, "aktif": False}


def test_inactivity_makes_step2_insufficient_and_blocks_later_steps():
    status = gate_status(base_metrics(aktif=False), .1, .01, {"alfa_yillik": 1, "nw_t": 3}, RULES)
    assert status["adim2"] == "Yetersiz" and {status[f"adim{i}"] for i in range(3, 8)} == {"Yetersiz"}
    assert gate_status(base_metrics(aktif=True), .1, None, None, RULES)["adim2"] == "Geçti"
    assert gate_status(base_metrics(), .1, None, None, RULES)["adim2"] == "Geçti"      # alan yoksa eski davranış


def test_night_share_is_report_only_tsi_0100_to_0900():
    istanbul = lambda hour: int(pd.Timestamp(f"2026-10-20 {hour:02d}:30", tz="Europe/Istanbul").timestamp() * 1000)
    fills = []
    for index, hour in enumerate([0, 1, 8, 9, 14]):    # gece: 01 ve 08 (00 ve 09 dışarıda)
        fills += [{"time": istanbul(hour) + index * DAY_MS, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0", "closedPnl": "0", "fee": "0"},
                  {"time": istanbul(hour) + index * DAY_MS + HOUR // 2, "coin": "BTC", "side": "A", "sz": "1", "px": "100", "startPosition": "1", "closedPnl": "0", "fee": "0"}]
    assert night_share(fills, RULES) == 2 / 5 and night_share([], RULES) is None
    assert "gece_payi" not in gate_status(base_metrics(gece_payi=1.0), .1, None, None, RULES)     # ölçüt değil


def test_delay_test_days_is_about_200_and_capped_by_first_fill():
    start_200 = NOW_MS - 200 * DAY_MS
    assert delay_test_days([{"time": NOW_MS - 300 * DAY_MS}], NOW_MS, start_200) == 200.0
    assert delay_test_days([{"time": NOW_MS - 50 * DAY_MS}, {"time": NOW_MS}], NOW_MS, start_200) == 50.0
    assert delay_test_days([], NOW_MS, start_200) is None


def test_test_family_is_steps_1_to_4_and_m_in_report(tmp_path: Path):
    from copytrade.kapi import funnel_report
    table = pd.DataFrame([result_row("0xa", plasebo_p=.001), result_row("0xb", plasebo_p=.2), result_row("0xc"),          # üçü de ailede (0xc'nin p'si yok)
                          result_row("0xd", adim4="Kaldı", plasebo_p=.0001),                                             # aile dışı: p hesaplanmış olsa da teste girmez
                          result_row("0xe", adim2="Yetersiz")])
    table["asama1"] = "Geçti"
    assert list(family_mask(table)) == [True, True, True, False, False]
    out = finalize(table, RULES).set_index("address")
    assert out.loc["0xa", "bhy_q"] == pytest.approx(.001 * 3 * (1 + 1 / 2 + 1 / 3))        # m = 3
    assert out.loc["0xa", "adim7"] == "Geçti" and out.loc["0xb", "adim7"] == "Kaldı"
    assert out.loc["0xc", "adim7"] == "Yetersiz" and pd.isna(out.loc["0xc", "bhy_q"])      # p yok → Yetersiz, ama m'ye sayıldı
    assert out.loc["0xd", "adim7"] == "Yetersiz" and pd.isna(out.loc["0xd", "bhy_q"])
    report = funnel_report(out.reset_index(), 5)
    assert "**m = 3**" in report and "tekrar sayısı 10000" in report


def test_gate_copy_ignores_inherited_exposure_so_window_start_does_not_flip_the_sign():
    """0x1404 mutabakatı: pencere öncesinden gelen pozisyonun kapanışı eskiden yeni ters pozisyon sayılıp sonucu −%110'a çeviriyordu."""
    from copytrade.kapi import CandleCache, copy_window_metrics
    now_ms = 1_800_000_000_000
    start = now_ms - 50 * DAY_MS
    market = {"BTC": [{"t": start - DAY_MS + i * HOUR, "o": str(100 + (i % 3))} for i in range(60 * 24)]}

    class Client:
        def candles(self, coin, s, e, interval="1h"): return market[coin]

    def run(fills):
        metrics, nets = copy_window_metrics(fills, [], 1000.0, CandleCache(Client(), start, now_ms), now_ms, 6)
        return nets[30]

    inherited_close = {"time": start, "coin": "BTC", "side": "A", "sz": "5", "px": "100", "startPosition": "5", "closedPnl": "9", "fee": "0", "tid": 1}
    later = [{"time": start + 3 * DAY_MS, "coin": "BTC", "side": "B", "sz": "1", "px": "100", "startPosition": "0", "closedPnl": "0", "fee": "0", "tid": 2},
             {"time": start + 4 * DAY_MS, "coin": "BTC", "side": "A", "sz": "1", "px": "100", "startPosition": "1", "closedPnl": "1", "fee": "0", "tid": 3}]
    assert run([inherited_close] + later) == pytest.approx(run(later))
