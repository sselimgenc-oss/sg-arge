"""Faz 3 geçmiş prova, seçim v1.3 uyarlaması (``docs/GOREV_FAZ3.md``; ana tanım ``docs/GOREV_GOLGE.md`` Faz 3).

Her T anı için: seçim v1.3 kuralı (havuz süzgeci, aday, oda, dilim-eşleştirilmiş kontrol; tohum ``secim-v1.3-faz3-<T>``) → T..T+60 gün gölge
(``golge.calistir`` V0/V1/V2) → pencere satırı. **Durdurma 1:** oda ↔ eşleştirilmiş kontrol V0 net getiri farkı (eşit ağırlık, BTC betası düzeltilmiş,
``analiz_d.ikincil_fark`` nokta tahmini) ≤ 0 olan pencere oranı > ``faz3_durdurma_orani`` ise durdurma ÖNERİSİ (karar kullanıcıda). Faz 3 yalnız
durdurabilir, başlatma kanıtı sayılmaz. Kapı, seçim, gölge motoru ve ``analiz_d.py`` değişmez (yalnız çağrılır); sayılar ``kurallar.yaml``'da.

Çekirdek (``pencere_kos``) veri kaynağından bağımsızdır: etiket satırları (kapı satırı biçimi), ileri veri sağlayıcısı, mumlar. Sentetik doğrulama ve gerçek
kaynak aynı çekirdeği kullanır. **Hiçbir pencere ``faz3_son_tarih``'ten sonraya taşmaz.**
Gerçek kaynak: bugünkü leaderboard evreni (hayatta kalan yanlılığı: sonuç "iyimser üst sınır"); HF verisi yalnız lider onayıyla.
"""
from __future__ import annotations

import argparse
import json
import statistics
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from copytrade import analiz_d, golge, rejim, secim
from copytrade.kurallar import load_rules
from copytrade.olcut import perp_fills

SURUM = "v1.3-faz3"
DAY_MS = 86_400_000
HOUR_MS = 3_600_000
VARYANTLAR = ("V0", "V1", "V2")


def ms(gun: date | str) -> int:
    d = gun if isinstance(gun, date) else date.fromisoformat(str(gun))
    return int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp() * 1000)


def pencere_tarihleri(rules: dict) -> list[date]:
    """T anları (eskiden yeniye). Son T = ``faz3_son_tarih`` − ``faz3_ileri_gun``; her pencere ``faz3_adim_gun`` geriye. Hiçbir T + ileri gün son tarihi aşmaz."""
    son = date.fromisoformat(str(rules["faz3_son_tarih"]))
    ileri, adim = int(rules["faz3_ileri_gun"]), int(rules["faz3_adim_gun"])
    son_t = son - timedelta(days=ileri)
    out = sorted(son_t - timedelta(days=adim * i) for i in range(int(rules["faz3_pencere_sayisi"])))
    assert all(t + timedelta(days=ileri) <= son for t in out)
    return out


# ------------------------------------------------------------------ çekirdek
def gunluk_seri(ileri: dict[str, Any], tarz: str, t_ms: int, bitis_ms: int, mumlar: dict[str, list[dict]], variant: str, rules: dict) -> pd.Series | None:
    """Bir adresin T..T+ileri günlük net getirisi (UTC gün; dolum olmayan gün 0). Yürütülemeyen dolum oranı ``onkayit_veri_eksik_max``'ı aşarsa ``None``.
    Dolumsuz (pasif) adres 0'larla tam seri döner (ön kayıt: pasifleşen sıfır getirili gün olarak paydada kalır)."""
    gunler = pd.date_range(pd.Timestamp(t_ms, unit="ms", tz="UTC"), periods=(bitis_ms - t_ms) // DAY_MS, freq="D")
    fills = [f for f in perp_fills(ileri["fills"]) if t_ms <= int(f["time"]) < bitis_ms]
    if not fills:
        return pd.Series(0.0, index=gunler)
    cikti = golge.calistir(fills, {c: mumlar.get(c, []) for c in {str(f["coin"]) for f in fills}}, float(ileri["hesap"]), style=tarz,
                           etiket_ms=t_ms, end_ms=bitis_ms, funding=ileri.get("funding") or [], variant=variant, rules=rules)
    defter = cikti["defter"]
    if defter.get("net") is None:
        return None
    eksik, toplam = int(defter.get("missing", 0)), int(defter.get("missing", 0)) + int(defter.get("executed", 0))
    if analiz_d.veri_eksik(eksik, toplam, rules):
        return None
    return defter["daily"].reindex(gunler, fill_value=0.0).astype(float) if "daily" in defter else None


def _btc_gunluk(mumlar: dict[str, list[dict]], t_ms: int, bitis_ms: int) -> pd.Series:
    rows = sorted((int(c["t"]), float(c["c"])) for c in mumlar.get("BTC", []) if t_ms - DAY_MS <= int(c["t"]) <= bitis_ms)
    kapanis = pd.Series({pd.Timestamp(t, unit="ms", tz="UTC"): v for t, v in rows}).resample("1D").last().dropna()
    return kapanis.pct_change().dropna()


def rejim_etiketi(mumlar: dict[str, list[dict]], t_ms: int, rules: dict) -> str | None:
    """T gününün BTC rejimi (yükseliş/düşüş/yatay/şok); veri yetmezse ``None``. Bilgi, karar değil."""
    rows = sorted((int(c["t"]), float(c["c"])) for c in mumlar.get("BTC", []) if int(c["t"]) < t_ms)
    if not rows:
        return None
    kapanis = pd.Series({pd.Timestamp(t, unit="ms", tz="UTC"): v for t, v in rows}).resample("1D").last().dropna()
    if len(kapanis) < int(rules["faz3_rejim_yuzdelik_pencere_gun"]):
        return None
    etiket = rejim.rejim_etiketle(kapanis, int(rules["faz3_rejim_pencere_gun"]), float(rules["faz3_rejim_getiri_esik"]),
                                  float(rules["faz3_rejim_sok_yuzdelik"]), int(rules["faz3_rejim_yuzdelik_pencere_gun"]))
    son = etiket.iloc[-1]
    return None if son is None or (isinstance(son, float) and np.isnan(son)) else str(son)


def pencere_kos(t: date | str, satirlar: list[dict[str, Any]], ileri_fn: Callable[[str], dict[str, Any] | str | None], mumlar: dict[str, list[dict]],
                rules: dict | None = None, *, tekrar: int | None = None, spearman: bool = True, varyantlar: tuple[str, ...] = VARYANTLAR) -> dict[str, Any]:
    """Tek pencere. ``satirlar``: T anında etiketlenmiş kapı-biçimli satırlar (``adim1/adim2/tarz/puan sütunları``); ``ileri_fn(adres)``: T..T+ileri verisi
    ``{"fills", "funding", "hesap"}``, eksiksiz değilse neden metni ya da ``None`` (dışarıda; sessiz eleme yok, nedenler sayılır)."""
    rules = rules or load_rules()
    t = t if isinstance(t, date) else date.fromisoformat(str(t))
    t_ms, bitis_ms = ms(t), ms(t) + int(rules["faz3_ileri_gun"]) * DAY_MS
    assert bitis_ms <= ms(rules["faz3_son_tarih"]), "pencere faz3_son_tarih'i aşıyor (pilot verisi görülemez)"
    pool = secim.havuz(pd.DataFrame(satirlar), rules)
    aday = secim.adaylar(pool, rules)
    oda_sonuc = secim.oda_sec(aday, rules)
    oda = [r["address"] for r in oda_sonuc["oda"]]
    kontrol = secim.kontrol_sec(pool, oda, t.isoformat(), SURUM)
    tarz = {r["address"]: r["tarz"] for r in pool}
    veri: dict[str, dict[str, Any]] = {}
    disarida: dict[str, str] = {}

    def getir(adres: str) -> dict[str, Any] | None:
        if adres not in veri and adres not in disarida:
            v = ileri_fn(adres)
            if isinstance(v, dict):
                veri[adres] = v
            else:
                disarida[adres] = v or "veri yok"
        return veri.get(adres)

    seriler: dict[tuple[str, str], pd.Series | None] = {}

    def seri(adres: str, variant: str) -> pd.Series | None:
        if (adres, variant) not in seriler:
            v = getir(adres)
            seriler[(adres, variant)] = None if v is None else gunluk_seri(v, tarz[adres], t_ms, bitis_ms, mumlar, variant, rules)
            if v is not None and seriler[(adres, variant)] is None:
                disarida.setdefault(adres, "yürütülemeyen dolum oranı eşiği aştı")
        return seriler[(adres, variant)]

    ciftler = [(o, k) for o, k in sorted(kontrol["eslesme"].items())]
    out: dict[str, Any] = {"t": t.isoformat(), "havuz": len(pool), "aday": len(aday), "oda": len(oda), "kontrol": len(kontrol["eslesme"]),
                           "kisa_oda": bool(oda_sonuc["kisa"]), "eslesmeyen": len(kontrol["eslesmeyen"]), "varyant": {}}
    btc = _btc_gunluk(mumlar, t_ms, bitis_ms)
    for variant in varyantlar:
        ok = [(o, k) for o, k in ciftler if seri(o, variant) is not None and seri(k, variant) is not None]
        satir: dict[str, Any] = {"cift": len(ok)}
        if len(ok) >= 2:
            koh = pd.concat([seri(o, variant) for o, _ in ok], axis=1).mean(axis=1)
            kon = pd.concat([seri(k, variant) for _, k in ok], axis=1).mean(axis=1)
            b = btc.reindex(koh.index, fill_value=0.0)
            r = analiz_d.ikincil_fark(koh.to_numpy(), kon.to_numpy(), b.to_numpy(), tekrar=tekrar, rules=rules)
            satir.update(fark=r["fark"], ga_alt=r["ga_alt"], ga_ust=r["ga_ust"], kohort_net=float((1 + koh).prod() - 1), kontrol_net=float((1 + kon).prod() - 1))
            if variant == "V0":
                oda_seri = [seri(o, "V0") for o, _ in ok]
                out["sigma"] = float(np.mean([s.std() for s in oda_seri]))
                kor = pd.concat(oda_seri, axis=1).corr().to_numpy()
                out["rho"] = float(np.nanmean(kor[np.triu_indices(len(oda_seri), 1)])) if len(oda_seri) > 1 else None
        out["varyant"][variant] = satir
    v0 = out["varyant"]["V0"]
    out["fark"] = v0.get("fark")
    out["gecti"] = None if v0.get("fark") is None else bool(v0["fark"] > 0)           # Durdurma 1: fark ≤ 0 → "geçemedi"
    # bilgi: havuz geneli puan ↔ sonraki 60 gün V0 net getirisi (kalıcılık / birincil Spearman)
    pares = [(float(r["puan"]), float(seri(r["address"], "V0").sum())) for r in pool if spearman and r["puan"] is not None and seri(r["address"], "V0") is not None]
    out["spearman"] = analiz_d.birincil_spearman([p for p, _ in pares], [g for _, g in pares], rules) if len(pares) >= 2 else None
    out["rejim"] = rejim_etiketi(mumlar, t_ms, rules)
    out["disarida"] = {"sayi": len(disarida), "nedenler": {n: sum(1 for x in disarida.values() if x == n) for n in sorted(set(disarida.values()))}}
    out["not"] = "taban kolu yok: geçmiş T günü leaderboard verisi yok"
    return out


def ozet(pencereler: list[dict[str, Any]], rules: dict | None = None) -> dict[str, Any]:
    """Durdurma 1: değerlendirilebilen pencerelerde ``fark ≤ 0`` oranı > ``faz3_durdurma_orani`` → öneri; değerlendirilebilen pencere < ``faz3_min_pencere`` → değerlendirilemedi."""
    rules = rules or load_rules()
    degerlendirilen = [p for p in pencereler if p.get("gecti") is not None]
    gecemeyen = sum(1 for p in degerlendirilen if not p["gecti"])
    oran = gecemeyen / len(degerlendirilen) if degerlendirilen else None
    if len(degerlendirilen) < int(rules["faz3_min_pencere"]):
        sonuc = "değerlendirilemedi"
    else:
        sonuc = "durdurma önerisi" if oran > float(rules["faz3_durdurma_orani"]) else "durdurma yok"
    return {"pencere": len(pencereler), "degerlendirilen": len(degerlendirilen), "gecemeyen": gecemeyen, "gecemeyen_oran": oran, "sonuc": sonuc,
            "esik": float(rules["faz3_durdurma_orani"]), "min_pencere": int(rules["faz3_min_pencere"])}


# ------------------------------------------------------------------ sentetik doğrulama (madde 1)
def sentetik_pencere(tohum: int, q: float, rules: dict, *, n_trader: int = 120, yetenekli_pay: float = 0.5) -> tuple[list[dict], Callable, dict, date]:
    """Rastgele yürüyüş fiyatlı sentetik pencere. ``q`` = yetenekli trader'ın işleminin geleceği bildiği olasılık (0: sıfır etki; etiket ve ileri dönemde ayrı işlemler).
    Fiyatlar saatlik açılış=kapanış, düşük gürültü; trader işlemi sıralı (uzun/kısa, 6–48 saat). Gerçek veri değildir."""
    rng = np.random.default_rng(tohum)
    t = pencere_tarihleri(rules)[0]
    t_ms, gun = ms(t), int(rules["faz3_ileri_gun"])
    bas_ms = t_ms - 30 * DAY_MS
    n_saat = (30 + gun + 2) * 24
    mumlar = {}
    for coin in ("SYN", "BTC"):
        fiyat = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.004, n_saat)))
        mumlar[coin] = [{"t": bas_ms + i * HOUR_MS, "o": float(fiyat[i]), "h": float(fiyat[i]) * 1.0005, "l": float(fiyat[i]) * 0.9995, "c": float(fiyat[min(i + 1, n_saat - 1)])}
                        for i in range(n_saat)]
    opens = np.array([c["o"] for c in mumlar["SYN"]])

    def trader_dolum(n_islem: int, bas: int, uzunluk: int, yetenekli: bool, kimlik: int) -> list[dict]:
        saat, fills, tid = bas, [], 0
        for _ in range(n_islem):
            saat += int(rng.integers(2, max(3, uzunluk // n_islem * 2)))
            tut = int(rng.integers(6, 49))
            if saat + tut >= bas + uzunluk:
                break
            gelecek = opens[saat + tut] - opens[saat]
            yon = (1 if gelecek > 0 else -1) if yetenekli and rng.random() < q else (1 if rng.random() < 0.5 else -1)
            ac, kapat = ("B", "A") if yon > 0 else ("A", "B")
            for k, (zaman, taraf, once) in enumerate(((saat, ac, 0.0), (saat + tut, kapat, float(yon)))):
                fills.append({"time": bas_ms + zaman * HOUR_MS + 600_000, "coin": "SYN", "side": taraf, "sz": "1", "startPosition": str(once),
                              "px": str(opens[zaman]), "tid": kimlik * 10_000 + tid})
                tid += 1
            saat += tut
        return fills

    satirlar, veri_ileri = [], {}
    for i in range(n_trader):
        adres = "0x" + f"{i:040x}"
        tarz = "intraday" if i % 2 == 0 else "swing"
        yetenekli = i < int(n_trader * yetenekli_pay)
        etiket_dolum = trader_dolum(14, 0, 30 * 24, yetenekli, i)
        ileri_dolum = trader_dolum(30, 30 * 24, gun * 24, yetenekli, i + 1000)
        etiket_cikti = golge.calistir(etiket_dolum, {"SYN": mumlar["SYN"]}, 1000.0, style=tarz, etiket_ms=bas_ms, end_ms=t_ms, variant="V0", rules=rules) if etiket_dolum else None
        net = etiket_cikti["defter"]["net"] if etiket_cikti else 0.0
        gecikme = int(rules["kopya_gecikme_dk"][tarz])
        satirlar.append({"address": adres, "adim1": "Geçti", "adim2": "Geçti", "tarz": tarz, "kisa_islem_payi": 0.1, "median_leverage": 1.0, "max_leverage": 1.0 + (i % 5),
                         "kapi_gecikme_dk": gecikme, f"gecikme_{gecikme}dk_net": net, "genc_aday": False, "iliskili_adresler": ""})
        veri_ileri[adres] = {"fills": ileri_dolum, "funding": [], "hesap": 1000.0}
    return satirlar, (lambda a: veri_ileri.get(a)), mumlar, t


from contextlib import contextmanager


@contextmanager
def kural_onbellegi(rules: dict):
    """Uzun koşularda ``kurallar.yaml``'ı her gölge çağrısında yeniden ayrıştırmamak için ``load_rules``'u aynı (değişmeyen) sözlükle sabitler; davranış değişmez."""
    from unittest import mock

    from copytrade import defter
    with mock.patch.object(defter, "load_rules", lambda *a, **k: rules), mock.patch.object(golge, "load_rules", lambda *a, **k: rules):
        yield


def sentetik_dogrulama(rules: dict | None = None, *, n_tohum: int | None = None, q: float = 0.7, tekrar: int = 400, n_trader: int = 120) -> dict[str, Any]:
    """İki senaryo, aynı çekirdek: (1) sıfır etki (q = 0) → ``ga_alt > 0`` oranı = yanlış pozitif; (2) etki enjekte (q) → yakalanma oranı.
    Karar ölçütü ``ikincil_fark`` %95 aralığının alt sınırı > 0 (tek yönlü ~%2,5; MBB küçük örnekte iyimser → bant ``faz3_yanlis_pozitif_bant``)."""
    rules = rules or load_rules()
    n = int(n_tohum or rules["faz3_sentetik_tohum"])
    sonuc: dict[str, Any] = {"tohum": n, "q": q}
    with kural_onbellegi(rules):
        _dogrulama_dongusu(sonuc, rules, n, q, tekrar, n_trader)
    return _dogrulama_karari(sonuc, rules)


def _dogrulama_dongusu(sonuc: dict[str, Any], rules: dict, n: int, q: float, tekrar: int, n_trader: int) -> None:
    for ad, qq in (("sifir_etki", 0.0), ("etki", q)):
        pozitif = nokta = degerli = 0
        for tohum in range(n):
            satirlar, ileri, mumlar, t = sentetik_pencere(tohum if qq == 0 else 10_000 + tohum, qq, rules, n_trader=n_trader)
            p = pencere_kos(t, satirlar, ileri, mumlar, rules, tekrar=tekrar, spearman=False, varyantlar=("V0",))
            v0 = p["varyant"]["V0"]
            if v0.get("fark") is None:
                continue
            degerli += 1
            pozitif += int(v0["ga_alt"] > 0)
            nokta += int(v0["fark"] > 0)
        sonuc[ad] = {"degerli": degerli, "ga_alt_pozitif": pozitif / degerli if degerli else None, "nokta_pozitif": nokta / degerli if degerli else None}


def _dogrulama_karari(sonuc: dict[str, Any], rules: dict) -> dict[str, Any]:
    bant = rules["faz3_yanlis_pozitif_bant"]
    sonuc["gecti"] = bool(sonuc["sifir_etki"]["ga_alt_pozitif"] is not None and bant[0] <= sonuc["sifir_etki"]["ga_alt_pozitif"] <= bant[1]
                          and sonuc["etki"]["ga_alt_pozitif"] is not None and sonuc["etki"]["ga_alt_pozitif"] >= float(rules["faz3_etki_yakalama_min"]))
    return sonuc


# ------------------------------------------------------------------ gerçek kaynak (ağ)
class GecmisIstemci:
    """``PublicClient`` sarmalayıcısı: T anından sonrasını göstermez (kapı değerlendirmesi T'de yapılmış gibi). Portföy, dolum, funding, mum ve
    hesap değeri T ile kesilir; hesap değeri portföy serisinden (T öncesi son değer) türetilir, HIP-3 dex'leri boş sayılır."""

    def __init__(self, client: Any, t_ms: int):
        self.client, self.t_ms = client, t_ms

    def portfolio(self, address: str) -> list:
        kesik = []
        for ad, deger in self.client.portfolio(address):
            if isinstance(deger, dict):
                deger = {**deger, **{k: [p for p in deger.get(k, []) if int(p[0]) <= self.t_ms] for k in ("accountValueHistory", "pnlHistory")}}
            kesik.append([ad, deger])
        return kesik

    def fills(self, address: str, start_ms: int, max_rows: int | None = None, end_ms: int | None = None) -> list[dict]:
        return self.client.fills(address, start_ms, max_rows=max_rows, end_ms=min(end_ms or self.t_ms, self.t_ms))

    def candles(self, coin: str, start_ms: int, end_ms: int, interval: str = "1m") -> list[dict]:
        return self.client.candles(coin, start_ms, min(end_ms, self.t_ms), interval)

    def info(self, payload: dict, weight: int = 20) -> Any:
        tip = payload.get("type")
        if tip == "perpDexs":
            return []
        if tip == "clearinghouseState":
            seri = dict(self.portfolio(payload["user"])).get("allTime", {}).get("accountValueHistory", [])
            return {"marginSummary": {"accountValue": str(float(seri[-1][1]) if seri else 0.0)}}
        if tip == "spotClearinghouseState":
            return {"balances": []}
        if "endTime" in payload:
            payload = {**payload, "endTime": min(int(payload["endTime"]), self.t_ms)}
        return self.client.info(payload, weight)

    def leaderboard(self) -> list[dict]:
        return self.client.leaderboard()


def gercek_kaynak(t: date, adresler: list[str], client: Any, rules: dict, log=print) -> tuple[list[dict], Callable[[str], Any], dict[str, list[dict]]]:
    """Bir T için gerçek veri: kapı değerlendirmesi T'ye kesilmiş istemciyle (``kapi.evaluate_address``), ileri veri ``client``'tan. API yalnız son
    ``api_dolum_pencere_siniri`` dolumu verir: T..bugün dolum sayısı pencereye ulaştıysa adres 'pencere dışı' (dışarıda; sessiz eleme yok)."""
    from copytrade.kapi import CandleCache, evaluate_address
    t_ms = ms(t)
    bitis = t_ms + int(rules["faz3_ileri_gun"]) * DAY_MS
    sarmal = GecmisIstemci(client, t_ms)
    bas_200 = t_ms - int(rules["mum_pencere_gun"]) * DAY_MS
    bas = t_ms - int(rules["fills_lookback_days"]) * DAY_MS
    onbellek = CandleCache(sarmal, bas_200, t_ms)
    satirlar = []
    for adres in adresler:
        deger = float(sarmal.info({"type": "clearinghouseState", "user": adres})["marginSummary"]["accountValue"])        # T anındaki hesap değeri (bugünkü değil)
        lider = {"address": adres, "accountValue": deger, "kaynak": "faz3"}
        satirlar.append(evaluate_address(lider, sarmal, onbellek, datetime.fromtimestamp(t_ms / 1000, UTC), bas, bas_200, None, rules, dexes=[]))
        log(f"T {t} etiket {adres[:10]}")
    limit = int(rules["api_dolum_pencere_siniri"])
    ileri_onbellek = CandleCache(client, t_ms, bitis)
    mumlar: dict[str, list[dict]] = {}

    def ileri_fn(adres: str) -> dict[str, Any] | str | None:
        if len(client.fills(adres, t_ms, max_rows=limit)) >= limit:
            return "pencere dışı (API son dolumlar penceresi)"
        fills = client.fills(adres, t_ms, end_ms=bitis)
        satir = next((r for r in satirlar if r["address"] == adres), {})
        hesap = float(satir.get("account_value") or 0.0)
        if hesap <= 0:
            return "hesap değeri yok"
        for coin, rows in ileri_onbellek.for_fills(fills).items():
            mumlar[coin] = rows
        return {"fills": fills, "funding": [], "hesap": hesap}

    mumlar["BTC"] = CandleCache(client, bas_200, bitis).get("BTC")
    return satirlar, ileri_fn, mumlar


# ------------------------------------------------------------------ rapor
def _f(v: float | None, n: int = 4) -> str:
    return "–" if v is None else f"{v:.{n}f}".replace(".", ",")


def _mmm(degerler: list[float]) -> str:
    return "–" if not degerler else f"{_f(min(degerler))} / {_f(statistics.median(degerler))} / {_f(max(degerler))}"


def rapor(pencereler: list[dict[str, Any]], dogrulama: dict[str, Any] | None, rules: dict | None = None, kaynak: str = "gerçek koşu yok") -> str:
    rules = rules or load_rules()
    o = ozet(pencereler, rules)
    L = ["# Faz 3 geçmiş prova (seçim v1.3 uyarlaması)", "",
         "> Faz 3 yalnız **durdurabilir**; başlatma kanıtı sayılmaz. Karar kullanıcıda. Hiçbir pencere " + str(rules["faz3_son_tarih"]) + " sonrasına taşmaz.", ""]
    L += ["## Sentetik doğrulama (gerçek veriden önce)", ""]
    if dogrulama:
        s, e = dogrulama["sifir_etki"], dogrulama["etki"]
        L += [f"- {dogrulama['tohum']} tohum; karar ölçütü: V0 farkın %95 aralığının alt sınırı > 0.",
              f"- Sıfır etkili trader: yanlış pozitif {_f(s['ga_alt_pozitif'], 3)} (bant {rules['faz3_yanlis_pozitif_bant']}); nokta tahmini > 0 oranı {_f(s['nokta_pozitif'], 3)} (≈ 0,5 beklenir).",
              f"- Enjekte etki (q = {dogrulama['q']}): yakalanma {_f(e['ga_alt_pozitif'], 3)} (asgari {rules['faz3_etki_yakalama_min']}).",
              f"- Sonuç: **{'geçti' if dogrulama['gecti'] else 'GEÇMEDİ: gerçek veriyle rapor yok'}**.", ""]
    else:
        L += ["- Sentetik doğrulama koşulmadı: gerçek veriyle rapor yok.", ""]
    L += ["## Gerçek veri", "", f"- Kaynak: {kaynak}."]
    if not pencereler:
        return "\n".join(L + ["- **Gerçek pencere koşusu yapılmadı**; Durdurma 1 henüz değerlendirilemedi.", ""])
    L += ["- Evren: bugünkü leaderboard — **iyimser üst sınır** (hayatta kalan yanlılığı; geçmiş leaderboard yok).",
          "- Taban kolu yok (geçmiş T günü leaderboard verisi yok).", "",
          "## Pencereler", "", "| T | Havuz | Oda | Kontrol çifti (V0) | Dışarıda | Fark V0 | %95 aralık | V1 fark | V2 fark | ρ (puan↔getiri) | Rejim | Geçti |", "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---|---|"]
    for p in pencereler:
        v = p["varyant"]
        ara = f"[{_f(v['V0'].get('ga_alt'))}; {_f(v['V0'].get('ga_ust'))}]"
        sp = p["spearman"]["rho"] if p.get("spearman") else None
        L.append(f"| {p['t']} | {p['havuz']} | {p['oda']} | {v['V0']['cift']} | {p['disarida']['sayi']} | {_f(p['fark'])} | {ara} | {_f(v['V1'].get('fark'))} | {_f(v['V2'].get('fark'))} | {_f(sp, 3)} | {p.get('rejim') or '–'} | "
                 f"{'–' if p['gecti'] is None else 'evet' if p['gecti'] else 'hayır'} |")
    farklar = [p["fark"] for p in pencereler if p["fark"] is not None]
    L += ["", "## Dağılım (min / medyan / maks)", "",
          f"- Oda adresi: {_mmm([float(p['oda']) for p in pencereler])}; kontrol çifti: {_mmm([float(p['varyant']['V0']['cift']) for p in pencereler])}; dışarıda kalan: {_mmm([float(p['disarida']['sayi']) for p in pencereler])}.",
          f"- V0 günlük fark: {_mmm(farklar)}.", "- Dışarıda kalma nedenleri (toplam): " + (", ".join(f"{n} {c}" for n, c in sorted(
              {k: sum(p['disarida']['nedenler'].get(k, 0) for p in pencereler) for p in pencereler for k in p['disarida']['nedenler']}.items())) or "yok") + "."]
    L += ["", "## Durdurma 1", "",
          f"- Değerlendirilen pencere {o['degerlendirilen']} / {o['pencere']} (asgari {o['min_pencere']}); geçemeyen {o['gecemeyen']} (oran {_f(o['gecemeyen_oran'], 3)}, eşik > {o['esik']}).",
          f"- **Sonuç: {o['sonuc']}.** " + {"durdurma önerisi": "Karar kullanıcıda.", "durdurma yok": "Bu başlatma kanıtı değildir.", "değerlendirilemedi": "Pencere sayısı yetersiz."}[o["sonuc"]]]
    sigma = [p["sigma"] for p in pencereler if p.get("sigma") is not None]
    rho = [p["rho"] for p in pencereler if p.get("rho") is not None]
    if sigma and rho:
        n = max(1, round(statistics.mean(p["oda"] for p in pencereler)))
        d = analiz_d.mde(statistics.median(sigma), min(max(statistics.median(rho), -0.99), 0.99), n, int(rules["faz3_ileri_gun"]), rules)
        L += ["", "## Güç (gerçek varyansla)", "", f"- {d['satir']}"]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ CLI
def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--planla", action="store_true", help="T anlarını JSON listesi olarak yaz (iş akışı matrisi)")
    parser.add_argument("--sentetik", action="store_true", help="sentetik doğrulamayı koş, JSON yaz")
    parser.add_argument("--pencere", help="tek T (YYYY-MM-DD) gerçek koşusu")
    parser.add_argument("--adresler", type=Path, help="evren adresleri (satır başına bir; bugünkü leaderboard anlık görüntüsü)")
    parser.add_argument("--birlestir", type=Path, help="pencere_*.json klasörü → rapor")
    parser.add_argument("--dogrulama", type=Path, help="sentetik doğrulama JSON")
    parser.add_argument("--cikti", type=Path, default=Path("faz3"))
    args = parser.parse_args(argv)
    rules = load_rules()
    args.cikti.mkdir(parents=True, exist_ok=True)
    if args.planla:
        print(json.dumps([t.isoformat() for t in pencere_tarihleri(rules)]))
    elif args.sentetik:
        sonuc = sentetik_dogrulama(rules)
        (args.cikti / "dogrulama.json").write_text(json.dumps(sonuc, indent=1), encoding="utf-8")
        print(json.dumps(sonuc))
        if not sonuc["gecti"]:
            raise SystemExit("Sentetik doğrulama geçmedi: gerçek veriyle rapor yok.")
    elif args.pencere:
        dogrulama = json.loads(args.dogrulama.read_text()) if args.dogrulama and args.dogrulama.exists() else None
        if not dogrulama or not dogrulama.get("gecti"):
            raise SystemExit("Sentetik doğrulama geçmeden gerçek pencere koşulmaz.")
        from copytrade.tarama import PublicClient, RateLimiter
        client = PublicClient(limiter=RateLimiter(1000))
        if args.adresler.suffix == ".json":
            from copytrade.kapi import read_universe_snapshot
            adresler = [r["address"].lower() for r in read_universe_snapshot(args.adresler)]
        else:
            adresler = [a.strip().lower() for a in args.adresler.read_text().splitlines() if a.strip()]
        t = date.fromisoformat(args.pencere)
        satirlar, ileri, mumlar = gercek_kaynak(t, adresler, client, rules)
        sonuc = pencere_kos(t, satirlar, ileri, mumlar, rules)
        (args.cikti / f"pencere_{t.isoformat()}.json").write_text(json.dumps(sonuc, indent=1, default=str), encoding="utf-8")
        print(json.dumps({k: sonuc[k] for k in ("t", "oda", "fark", "gecti")}, default=str))
    elif args.birlestir:
        pencereler = [json.loads(p.read_text()) for p in sorted(args.birlestir.glob("pencere_*.json"))]
        dogrulama = json.loads(args.dogrulama.read_text()) if args.dogrulama and args.dogrulama.exists() else None
        metin = rapor(pencereler, dogrulama, rules, kaynak="bugünkü leaderboard evreni (iyimser üst sınır)")
        (args.cikti / "RAPOR.md").write_text(metin, encoding="utf-8")
        print(metin)
    else:
        parser.error("bir işlem seçin")


if __name__ == "__main__":
    main()
