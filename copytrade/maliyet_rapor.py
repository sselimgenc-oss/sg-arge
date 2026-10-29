"""Maliyet duyarlılık raporu (yalnız rapor; karar kodu ve eşikler değişmez): ``arastirma/copytrade/maliyet_duyarlilik.md``.

Üç soru: (1) coin sınıfına (büyük / küçük / HIP-3) göre ölçülen makas (A16), (2) odadaki trader'ların HIP-3 hacim payı,
(3) v1.3 oda puanı üç maliyet senaryosunda ve her senaryoda odaya kimin girip çıktığı.

Yöntem: kopya maliyeti dolum başına ``notional × oran`` olduğundan doğrusaldır. Defter her sınıfın dolumlarıyla ayrı koşulur
(``defter.copy_ledger``; coin'ler birbirinden bağımsız), sınıfın maliyet toplamı ``costs_c`` bulunur. Senaryo puanı
``puan − Σ costs_c × (oran_c / mevcut_oran − 1)``; mevcut maliyet senaryosu kapının yayımladığı puanın kendisidir.
Seçim kodu (``secim.adaylar`` / ``secim.oda_sec``) aynen çalışır; yalnız puan sütunu senaryoya göre değişir.
"""
from __future__ import annotations

import argparse
import json
import statistics
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from copytrade import secim
from copytrade.defter import FundingRates, Market, copy_ledger, cost_rate
from copytrade.kurallar import load_rules
from copytrade.makas_tahmin import coin_makas_ozeti
from copytrade.olcut import perp_fills

SINIFLAR = ("buyuk", "kucuk", "hip3")
SINIF_AD = {"buyuk": "Büyük (BTC, ETH, SOL)", "kucuk": "Küçük (diğer kripto)", "hip3": "HIP-3 (deployer piyasaları)"}
SENARYOLAR = ("a", "b", "c")
SENARYO_AD = {"a": "(a) mevcut maliyet", "b": "(b) A17 §8.2 sınıf maliyetleri, alt uç", "c": "(c) HIP-3 ücreti ×2"}
GUN_MS = 86_400_000


def coin_sinifi(coin: str, rules: dict) -> str:
    """HIP-3 piyasaları ``dex:`` önekiyle gelir; büyük coin'ler kurallardaki liste; geri kalan perp'ler küçük."""
    coin = str(coin)
    if ":" in coin:
        return "hip3"
    return "buyuk" if coin.upper() in {str(c).upper() for c in rules["maliyet_buyuk_coinler"]} else "kucuk"


def sinif_oranlari(rules: dict) -> dict[str, dict[str, float]]:
    """Senaryo → sınıf → tek yön maliyet oranı (notional'a oranla)."""
    taban = cost_rate(rules)
    alt = {sinif: float(value) for sinif, value in rules["maliyet_sinif_alt_uc"].items()}
    hip3_ucret = float(rules["maliyet_taker"]) * float(rules["maliyet_hip3_ucret_carpani"]) + float(rules["maliyet_kayma"])
    return {"a": {sinif: taban for sinif in SINIFLAR},
            "b": {sinif: alt[sinif] for sinif in SINIFLAR},
            "c": {"buyuk": taban, "kucuk": taban, "hip3": hip3_ucret}}


def senaryo_puani(puan: float | None, maliyetler: dict[str, float], oranlar: dict[str, float], taban: float) -> float | None:
    """Kapı puanı − Σ sınıf maliyeti × (senaryo oranı / mevcut oran − 1). Puansız kalır."""
    if puan is None:
        return None
    return puan - sum(float(maliyetler.get(sinif, 0.0)) * (oranlar[sinif] / taban - 1.0) for sinif in SINIFLAR)


def hip3_hacim_payi(fills: list[dict], rules: dict) -> dict[str, float | None]:
    """Perp dolumlarının hacminde sınıf payları (``px × sz``); hacim yoksa ``None``."""
    hacim = {sinif: 0.0 for sinif in SINIFLAR}
    for fill in perp_fills(fills):
        hacim[coin_sinifi(fill.get("coin", ""), rules)] += abs(float(fill.get("px", 0)) * float(fill.get("sz", 0)))
    toplam = sum(hacim.values())
    return {sinif: (hacim[sinif] / toplam if toplam else None) for sinif in SINIFLAR}


def sinif_defterleri(fills: list[dict], market: Market, kapital: Any, gecikme: int, bas_ms: int, bitis_ms: int,
                     rates: FundingRates, rules: dict) -> dict[str, dict[str, float | None]]:
    """Dolumları sınıfa bölüp her sınıf için ayrı kopya defteri: ``{sinif: {"net", "costs"}}`` (costs = mevcut oranla)."""
    kaynak = perp_fills(fills)
    out: dict[str, dict[str, float | None]] = {}
    for sinif in SINIFLAR:
        parca = [f for f in kaynak if coin_sinifi(f["coin"], rules) == sinif]
        sonuc = copy_ledger(parca, market, kapital, gecikme, bas_ms, bitis_ms, rates, rules) if parca else {"net": 0.0, "costs": 0.0}
        out[sinif] = {"net": sonuc["net"], "costs": sonuc.get("costs", 0.0) if sonuc["net"] is not None else None}
    return out


def oda_kumeleri(havuz_satirlari: list[dict[str, Any]], puanlar: dict[str, float | None], rules: dict) -> dict[str, Any]:
    """Puanlar değiştirilmiş havuzla seçim v1.3 aday + oda adımları (aynı kod); döner oda adresleri ve aday sayısı."""
    satirlar = [{**r, "puan": puanlar.get(r["address"])} for r in havuz_satirlari]
    aday = secim.adaylar(satirlar, rules)
    oda = secim.oda_sec(aday, rules)
    return {"oda": [r["address"] for r in oda["oda"]], "aday": len(aday), "kisa": oda["kisa"]}


def degisim(taban: list[str], senaryo: list[str]) -> dict[str, list[str]]:
    return {"giren": sorted(set(senaryo) - set(taban)), "cikan": sorted(set(taban) - set(senaryo))}


def sinif_makas(coin_ozetleri: dict[str, dict], rules: dict) -> dict[str, dict[str, Any]]:
    """Sınıf başına coin sayısı ile coin başına Corwin–Schultz medyanı ve Abdi–Ranaldo makasının medyanı (bps)."""
    out: dict[str, dict[str, Any]] = {}
    for sinif in SINIFLAR:
        coinler = {c: o for c, o in coin_ozetleri.items() if coin_sinifi(c, rules) == sinif}
        cs = [o["corwin_schultz"]["medyan_bps"] for o in coinler.values() if o["corwin_schultz"]["medyan_bps"] is not None]
        ar = [o["abdi_ranaldo"]["makas_bps"] for o in coinler.values() if o["abdi_ranaldo"]["makas_bps"] is not None]
        out[sinif] = {"coin": len(coinler), "cs_medyan_bps": statistics.median(cs) if cs else None,
                      "ar_medyan_bps": statistics.median(ar) if ar else None,
                      "atlanan_mum": sum(o["atlanan_mum"] for o in coinler.values())}
    return out


def _bps(v: float | None) -> str:
    return "–" if v is None else f"{v:.1f}".replace(".", ",")


def _yuzde(v: float | None) -> str:
    return "–" if v is None else f"{100 * v:.1f}".replace(".", ",") + " %"


def _ondalik(v: float | None, n: int = 3) -> str:
    return "–" if v is None else f"{v:.{n}f}".replace(".", ",")


def rapor(veri: dict[str, Any], rules: dict) -> str:
    """Toplanan ham sonuçtan Türkçe, kısa, maddeli rapor."""
    oranlar = sinif_oranlari(rules)
    satirlar = veri["havuz"]
    puanlar = {s: {r["address"]: senaryo_puani(r["puan"], r["maliyet"], oranlar[s], cost_rate(rules)) for r in satirlar} for s in SENARYOLAR}
    kume = {s: oda_kumeleri([{**r, "puan": r["puan"]} for r in satirlar], puanlar[s], rules) for s in SENARYOLAR}
    kim = {r["address"]: r for r in satirlar}
    L = [f"# Maliyet duyarlılık raporu (kapı {veri['kapi_tarihi']}, seçim v1.3)", "",
         "Yalnız rapor. Karar kodu, eşikler ve kapı puanı değişmez; senaryolar puan sütununu değiştirip aynı seçim kodunu koşar.", ""]
    L += ["## Yöntem ve sınırlar", "",
          "- Maliyet dolum başına notional × oran (doğrusal): her sınıfın dolumlarıyla ayrı defter koşuldu, sınıf maliyeti `costs_c` bulundu.",
          "- Senaryo puanı = kapı puanı − Σ `costs_c` × (senaryo oranı / mevcut oran − 1).",
          f"- Mevcut oran (taker + kayma): {_ondalik(100 * cost_rate(rules), 3)} % tek yön.",
          "- Senaryo (b) A17 §8.2'nin **alt uç** tek yön maliyetleri: " + ", ".join(f"{SINIF_AD[s]} {_ondalik(100 * oranlar['b'][s], 3)} %" for s in SINIFLAR) + ".",
          f"- Senaryo (c): HIP-3 taker ücreti ×{rules['maliyet_hip3_ucret_carpani']:g} (HIP-3 oranı {_ondalik(100 * oranlar['c']['hip3'], 3)} %), diğer sınıflar mevcut.",
          "- A17 §8.2'deki HIP-3 Growth Mode satırı kullanılmadı: dolumlardan hangi piyasanın o modda olduğu bilinmiyor (HIP-3 hepsi standart sayıldı).",
          f"- Pencere: son {rules['mum_pencere_gun']} gün dolumları, kapıdaki gibi. Doğrulama: yürütülen dolum sayısı kapı sütunuyla {veri['dolum_eslesme'][0]} / {veri['dolum_eslesme'][1]} adreste aynı.",
          "- Funding çekilmedi (maliyet funding'e bağlı değil); puan her senaryoda kapının yayımladığı değerden başlar.", ""]
    L += ["## 1. Coin sınıfına göre makas (A16, saatlik mumlar)", "",
          "| Sınıf | Coin | Corwin–Schultz medyan (bps) | Abdi–Ranaldo medyan (bps) | Atlanan mum |", "|---|---:|---:|---:|---:|"]
    for sinif, o in veri["makas"].items():
        L.append(f"| {SINIF_AD[sinif]} | {o['coin']} | {_bps(o['cs_medyan_bps'])} | {_bps(o['ar_medyan_bps'])} | {o['atlanan_mum']} |")
    L += ["", "- Bunlar yarım-makas tahminleri değil, tam efektif makas (bps); kopya kaymasının alt sınırı kabaca makasın yarısıdır.",
          "- Saatlik mumdan makas tahmini gürültülüdür; sıfır makasta bile Corwin–Schultz birkaç bps gösterir (A16 testleri).", ""]
    L += ["## 2. Odadaki trader'ların HIP-3 hacim payı (son 200 gün, perp dolum hacmi)", "",
          "| Adres | Tarz | HIP-3 payı | Büyük | Küçük |", "|---|---|---:|---:|---:|"]
    for a in kume["a"]["oda"]:
        r = kim[a]
        p = r["hacim_payi"]
        L.append(f"| `{a[:6]}…{a[-4:]}` | {r['tarz']} | {_yuzde(p['hip3'])} | {_yuzde(p['buyuk'])} | {_yuzde(p['kucuk'])} |")
    oda_payi = [kim[a]["hacim_payi"]["hip3"] for a in kume["a"]["oda"] if kim[a]["hacim_payi"]["hip3"] is not None]
    havuz_payi = [r["hacim_payi"]["hip3"] for r in satirlar if r["hacim_payi"]["hip3"] is not None]
    L += ["", f"- Oda: medyan HIP-3 payı {_yuzde(statistics.median(oda_payi) if oda_payi else None)}, HIP-3 payı > %10 olan {sum(p > 0.10 for p in oda_payi)} / {len(oda_payi)}.",
          f"- Havuz ({len(havuz_payi)} adres): medyan {_yuzde(statistics.median(havuz_payi) if havuz_payi else None)}, > %10 olan {sum(p > 0.10 for p in havuz_payi)}.", ""]
    L += ["## 3. v1.3 oda puanı, üç senaryo", "",
          "| Senaryo | Aday | Oda | Odada kalan (a'ya göre) | Giren | Çıkan | Oda medyan puan |", "|---|---:|---:|---:|---:|---:|---:|"]
    for s in SENARYOLAR:
        d = degisim(kume["a"]["oda"], kume[s]["oda"])
        medyan = statistics.median([puanlar[s][a] for a in kume[s]["oda"] if puanlar[s][a] is not None] or [float("nan")])
        L.append(f"| {SENARYO_AD[s]} | {kume[s]['aday']} | {len(kume[s]['oda'])} | {len(set(kume['a']['oda']) & set(kume[s]['oda']))} | {len(d['giren'])} | {len(d['cikan'])} | {_ondalik(medyan)} |")
    for s in ("b", "c"):
        d = degisim(kume["a"]["oda"], kume[s]["oda"])
        L += ["", f"### {SENARYO_AD[s]}: odaya giren / çıkan", ""]
        if not d["giren"] and not d["cikan"]:
            L.append("- Değişiklik yok.")
            continue
        L += ["| Yön | Adres | Tarz | Puan (a) | Puan (senaryo) | HIP-3 payı |", "|---|---|---|---:|---:|---:|"]
        for yon, adresler in (("giren", d["giren"]), ("çıkan", d["cikan"])):
            for a in adresler:
                r = kim[a]
                L.append(f"| {yon} | `{a[:6]}…{a[-4:]}` | {r['tarz']} | {_ondalik(puanlar['a'][a])} | {_ondalik(puanlar[s][a])} | {_yuzde(r['hacim_payi']['hip3'])} |")
    L += ["", "## Okuma", ""]
    for s in ("b", "c"):
        d = degisim(kume["a"]["oda"], kume[s]["oda"])
        L.append(f"- {SENARYO_AD[s]}: {len(d['giren'])} giren, {len(d['cikan'])} çıkan; oda {len(kume[s]['oda'])} kişi.")
    L.append("- Bu rapor karar değildir: maliyet varsayımı değiştirilmedi, oda yayımlanan v1.3 odasıdır.")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ veri toplama (ağ)
def topla(sonuc_csv: Path, kapi_tarihi: str, cikis: Path, rules: dict | None = None, log=print) -> dict[str, Any]:
    """Havuz adresleri için 200 günlük dolum ve portfolio çeker; sınıf maliyetleri, hacim payları ve coin makas özetlerini yazar.

    Funding çekilmez: sınıf maliyeti (``costs``) funding'e bağlı değil, puan kapının yayımladığı değerden alınır. Kapıyla aynı
    dolum ve piyasa kullanıldığı, yürütülen dolum sayısının kapı sütunuyla eşleşmesiyle doğrulanır (``dolum_eslesme``).
    Kesilirse ``cikis`` dosyasından kaldığı yerden sürer.
    """
    from copytrade.kapi import CandleCache, account_history
    from copytrade.tarama import PublicClient, RateLimiter

    rules = rules or load_rules()
    tablo = pd.read_csv(sonuc_csv, low_memory=False)
    havuz = secim.havuz(tablo, rules)
    kapi_satir = {str(r["address"]).lower(): r for r in tablo.to_dict("records")}
    now = datetime.now(UTC)
    now_ms = int(now.timestamp() * 1000)
    bas_200 = int((now - timedelta(days=int(rules["mum_pencere_gun"]))).timestamp() * 1000)
    client = PublicClient(limiter=RateLimiter(1000))
    cache = CandleCache(client, bas_200, now_ms)
    onceki = json.loads(cikis.read_text(encoding="utf-8")) if cikis.exists() else {"havuz": []}
    satirlar = onceki["havuz"]
    yapilan = {r["address"] for r in satirlar}
    for i, r in enumerate(havuz, 1):
        adres = r["address"]
        if adres in yapilan:
            continue
        gecikme = int(r["kapi_gecikme_dk"])
        fills = [x for x in client.fills(adres, bas_200) if int(x.get("time", 0)) >= bas_200]
        history = account_history(client.portfolio(adres))
        kapital = history if history is not None and len(history) else float(r["account_value"])
        market = Market(cache.for_fills(fills), max_intervals=int(rules["mum_uzaklik_max_aralik"]))
        yurutulen = copy_ledger(perp_fills(fills), market, kapital, gecikme, bas_200, now_ms, None, rules)["executed"]
        siniflar = sinif_defterleri(fills, market, kapital, gecikme, bas_200, now_ms, None, rules)
        satirlar.append({"address": adres, "tarz": r["tarz"], "puan": r["puan"], "gecikme_dk": gecikme,
                         "maliyet": {s: v["costs"] for s, v in siniflar.items()},
                         "yurutulen": yurutulen, "kapi_yurutulen": kapi_satir[adres].get(f"gecikme_{gecikme}dk_dolum"),
                         "hacim_payi": hip3_hacim_payi(fills, rules)})
        log(f"{i}/{len(havuz)} {adres[:10]} gecikme {gecikme} dk, {len(fills)} dolum", flush=True)
        if len(satirlar) % 5 == 0:
            cikis.write_text(json.dumps({"havuz": satirlar}, ensure_ascii=False), encoding="utf-8")
    coinler = {coin: coin_makas_ozeti(cache.get(coin), (50,), rules) for coin in sorted(cache.items) if cache.get(coin)}
    esles = [r["yurutulen"] == r["kapi_yurutulen"] for r in satirlar if r["kapi_yurutulen"] is not None]
    veri = {"kapi_tarihi": kapi_tarihi, "uretildi": now.isoformat(), "havuz": satirlar, "makas": sinif_makas(coinler, rules),
            "dolum_eslesme": [sum(esles), len(esles)]}
    cikis.write_text(json.dumps(veri, ensure_ascii=False), encoding="utf-8")
    return veri


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sonuc", type=Path, required=True, help="kapı sonuc.csv")
    parser.add_argument("--kapi-tarihi", required=True)
    parser.add_argument("--ham", type=Path, required=True, help="toplanan ham JSON (yoksa ağdan toplanır)")
    parser.add_argument("--rapor", type=Path, required=True)
    args = parser.parse_args(argv)
    rules = load_rules()
    veri = json.loads(args.ham.read_text(encoding="utf-8")) if args.ham.exists() and "makas" in json.loads(args.ham.read_text(encoding="utf-8")) else topla(args.sonuc, args.kapi_tarihi, args.ham, rules)
    args.rapor.write_text(rapor(veri, rules), encoding="utf-8")
    print(f"Rapor yazıldı: {args.rapor}")


if __name__ == "__main__":
    main()
