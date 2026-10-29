"""Arşivde/lider tablosunda **kalıcılık** keşif testi (``docs/GOREV_KALICILIK.md``): "seçim skoru yüksek hesaplar sonraki haftalarda gerçekten daha iyi gidiyor mu?"

Keşif analizidir: pilotu, seçimi, kapıyı ve eşikleri değiştirmez. Veri: Hyperliquid ``portfolio`` (``accountValueHistory`` ve ``pnlHistory``; dolum sınırına takılmaz).
Getiri = kümülatif PnL farkı / T anındaki pencerenin pozitif hesap değeri medyanı (yatırma/çekme PnL'de yok → etkisi arındırılmış).
**Geleceğe bakma yok:** T anındaki skor yalnız ``t <= T`` noktalarıyla hesaplanır (testle sabit). Hayatta kalan yanlılığı: evren bugünkü lider tablosundan (rapor yazar).
Test (önceden yazılı, ``deneme_defteri.jsonl``'a önkayıtlı): son ``kalicilik_gecmis_gun`` gün, ``kalicilik_adim_gun`` günde bir T; skor (a) 90 gün getiri, (b) Calmar,
(c) 180 gün kârlı ay oranı; 5 dilim; sonraki 28 ve 56 gün getirisi; ölçüt: dilim ortalamalarında düzenli düşüş (Spearman) ve üst − alt farkı; T örtüşmesi için blok bootstrap.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from copytrade.kurallar import load_rules

DAY_MS = 86_400_000
SKORLAR = ("getiri", "calmar", "kar_ay")
SKOR_AD = {"getiri": "(a) 90 gün getiri", "calmar": "(b) Calmar (getiri / maksimum düşüş)", "kar_ay": "(c) 180 gün kârlı ay oranı"}


# ------------------------------------------------------------------ veri
def hesap_olustur(portfolio: list) -> dict[str, list] | None:
    """``portfolio`` yanıtından ``{"av": [[t, değer]], "pnl": [[t, değer]]}`` (``allTime`` penceresi); yoksa ``None``."""
    donemler = {ad: v for ad, v in portfolio if isinstance(v, dict)} if portfolio else {}
    all_time = donemler.get("allTime") or donemler.get("perpAllTime")
    if not all_time:
        return None
    av = [[int(t), float(v)] for t, v in all_time.get("accountValueHistory", [])]
    pnl = [[int(t), float(v)] for t, v in all_time.get("pnlHistory", [])]
    return {"av": av, "pnl": pnl} if av and pnl else None


_SERI: dict[int, pd.Series] = {}


def _seri(noktalar: list) -> pd.Series:
    """Nokta listesi → zaman indeksli seri; aynı liste nesnesi için önbellekli (uzun koşuda tekrar kurma maliyeti)."""
    anahtar = id(noktalar)
    if anahtar not in _SERI or len(_SERI[anahtar]) != len(noktalar):
        _SERI[anahtar] = pd.Series({int(t): float(v) for t, v in noktalar}, dtype=float).sort_index()
    return _SERI[anahtar]


def _son(seri: pd.Series, t_ms: int) -> tuple[int, float] | None:
    """``t <= t_ms`` olan son nokta (zaman, değer); yoksa ``None``. Geleceğe bakmaz."""
    kesik = seri[seri.index <= t_ms]
    return None if kesik.empty else (int(kesik.index[-1]), float(kesik.iloc[-1]))


def payda(hesap: dict, t_ms: int, gun: int) -> float | None:
    """Pencere ``[t − gun, t]`` pozitif hesap değerlerinin medyanı (kapı 1. aşama ile aynı fikir); yoksa ``None``."""
    av = _seri(hesap["av"])
    pencere = av[(av.index >= t_ms - gun * DAY_MS) & (av.index <= t_ms) & (av > 0)]
    return None if pencere.empty else float(pencere.median())


def skorlar(hesap: dict, t_ms: int, rules: dict) -> dict[str, float | None]:
    """T anındaki üç skor; yalnız ``t <= T`` verisi. Pencerenin başında veri yoksa ilgili skor ``None``."""
    pnl = _seri(hesap["pnl"])
    pnl = pnl[pnl.index <= t_ms]                              # geleceğe bakma yok (kesin)
    out: dict[str, float | None] = {k: None for k in SKORLAR}
    g = int(rules["kalicilik_getiri_gun"])
    bas = t_ms - g * DAY_MS
    den = payda(hesap, t_ms, g)
    if not pnl.empty and pnl.index[0] <= bas and den:
        pencere = pnl[pnl.index >= bas]
        ilk = _son(pnl, bas)
        if ilk and len(pencere):
            getiri = (float(pnl.iloc[-1]) - ilk[1]) / den
            egri = den + (pd.concat([pd.Series([ilk[1]], index=[bas]), pencere]) - ilk[1])
            egri = egri.clip(lower=1e-9)
            mdd = float((1.0 - egri / egri.cummax()).max())
            out["getiri"] = getiri
            out["calmar"] = getiri / max(mdd, float(rules["kalicilik_mdd_taban"]))
    kg, ay = int(rules["kalicilik_kar_ay_gun"]), int(rules["kalicilik_ay_gun"])
    if not pnl.empty and pnl.index[0] <= t_ms - kg * DAY_MS:
        sinirlar = [_son(pnl, t_ms - (kg - i * ay) * DAY_MS) for i in range(kg // ay + 1)]
        if all(s is not None for s in sinirlar):
            farklar = [b[1] - a[1] for a, b in zip(sinirlar, sinirlar[1:])]
            out["kar_ay"] = sum(f > 0 for f in farklar) / len(farklar)
    return out


def ileri_getiri(hesap: dict, t_ms: int, gun: int, rules: dict) -> float | None:
    """T..T+gun getirisi (PnL farkı / T anı payda). Pencere sonuna ``kalicilik_veri_bosluk_gun`` günden yakın veri yoksa ``None`` (dışarıda)."""
    pnl = _seri(hesap["pnl"])
    bas, son = _son(pnl, t_ms), _son(pnl, t_ms + gun * DAY_MS)
    den = payda(hesap, t_ms, int(rules["kalicilik_getiri_gun"]))
    if bas is None or son is None or not den or t_ms + gun * DAY_MS - son[0] > int(rules["kalicilik_veri_bosluk_gun"]) * DAY_MS:
        return None
    return (son[1] - bas[1]) / den


def t_anlari(simdi_ms: int, rules: dict) -> list[int]:
    """Eskiden yeniye T anları: son T = şimdi − en uzun ileri pencere; ``kalicilik_gecmis_gun`` gün geriye, ``kalicilik_adim_gun`` adımla."""
    son = simdi_ms - max(int(g) for g in rules["kalicilik_ileri_gun"]) * DAY_MS
    adim, n = int(rules["kalicilik_adim_gun"]), int(rules["kalicilik_gecmis_gun"]) // int(rules["kalicilik_adim_gun"])
    return sorted(son - i * adim * DAY_MS for i in range(n))


# ------------------------------------------------------------------ dilim testi
def t_verisi(hesaplar: dict[str, dict], t_ms: int, rules: dict) -> dict[str, dict[str, Any]]:
    """Bir T için her hesabın üç skoru ve ileri getirileri (bir kez hesaplanır): ``{adres: {"skor": {...}, "ileri": {gün: getiri}}}``."""
    return {a: {"skor": skorlar(h, t_ms, rules), "ileri": {int(g): ileri_getiri(h, t_ms, int(g), rules) for g in rules["kalicilik_ileri_gun"]}} for a, h in hesaplar.items()}


def dilim_testi(veri: dict[str, dict[str, Any]], skor: str, gun: int, rules: dict) -> dict[str, Any] | None:
    """Bir T, skor ve ileri pencere için (``t_verisi`` çıktısı): hesaplar skora göre ``kalicilik_dilim`` dilime (1 = en yüksek skor), dilim ortalama ileri getirisi,
    üst − alt farkı, dilim sırasına karşı Spearman (üst dilim en iyiyse pozitif). Dilim başına ``kalicilik_min_dilim_hesap``'tan az hesap varsa ``None`` (T atlanır)."""
    satirlar = [(a, v["skor"][skor], v["ileri"][gun]) for a, v in veri.items()
                if v["skor"][skor] is not None and v["ileri"][gun] is not None and math.isfinite(v["skor"][skor]) and math.isfinite(v["ileri"][gun])]
    k = int(rules["kalicilik_dilim"])
    if len(satirlar) < k * int(rules["kalicilik_min_dilim_hesap"]):
        return None
    satirlar.sort(key=lambda r: (-r[1], r[0]))
    parcalar = np.array_split(np.array([r[2] for r in satirlar]), k)
    ort = [float(p.mean()) for p in parcalar]
    sira = pd.Series(range(k, 0, -1), dtype=float)           # üst dilim = en büyük sayı
    rho = float(sira.rank().corr(pd.Series(ort).rank()))        # Spearman = sıraların Pearson korelasyonu (scipy yok)
    return {"n": len(satirlar), "dilim_ort": ort, "ust_alt": ort[0] - ort[-1], "rho": rho if math.isfinite(rho) else None}


def blok_bootstrap_ci(degerler: list[float], rules: dict) -> tuple[float, float, float]:
    """T serisinin ortalaması ve blok bootstrap güven aralığı (örtüşen T'ler için; blok ``kalicilik_blok_t``). ``(ortalama, alt, üst)``."""
    x = np.asarray(degerler, dtype=float)
    n = len(x)
    blok = max(1, min(int(rules["kalicilik_blok_t"]), n))
    rng = np.random.default_rng(int(rules["kalicilik_tohum"]))
    baslar = np.arange(n - blok + 1)
    adet = math.ceil(n / blok)
    tahmin = np.empty(int(rules["kalicilik_bootstrap_tekrar"]))
    for i in range(len(tahmin)):
        sec = rng.choice(baslar, size=adet)
        tahmin[i] = x[np.concatenate([np.arange(b, b + blok) for b in sec])[:n]].mean()
    d = float(rules["kalicilik_ci"])
    alt, ust = np.quantile(tahmin, [(1 - d) / 2, 1 - (1 - d) / 2])
    return float(x.mean()), float(alt), float(ust)


def analiz(hesaplar: dict[str, dict], simdi_ms: int, rules: dict | None = None) -> dict[str, Any]:
    """Tüm skorlar × ileri pencereler × T. Döner: ``{"t": [...], "sonuc": {skor: {gun: {...özet}}}}``; her özet: T sayısı, atlanan T, ortalama üst − alt ve %95 aralığı,
    ortalama Spearman, Spearman > 0 olan T oranı, dilim ortalamalarının T ortalaması."""
    rules = rules or load_rules()
    tler = t_anlari(simdi_ms, rules)
    out: dict[str, Any] = {"t": [pd.Timestamp(t, unit="ms", tz="UTC").date().isoformat() for t in tler], "hesap": len(hesaplar), "sonuc": {}}
    veriler = [t_verisi(hesaplar, t, rules) for t in tler]
    for skor in SKORLAR:
        out["sonuc"][skor] = {}
        for gun in (int(g) for g in rules["kalicilik_ileri_gun"]):
            sonuclar = [r for r in (dilim_testi(v, skor, gun, rules) for v in veriler) if r is not None]
            ozet: dict[str, Any] = {"t_sayisi": len(sonuclar), "atlanan_t": len(tler) - len(sonuclar)}
            if len(sonuclar) >= 2:
                ort, alt, ust = blok_bootstrap_ci([r["ust_alt"] for r in sonuclar], rules)
                rhos = [r["rho"] for r in sonuclar if r["rho"] is not None]
                ozet.update(ust_alt=ort, ga_alt=alt, ga_ust=ust, rho=float(np.mean(rhos)) if rhos else None,
                            rho_pozitif=sum(r > 0 for r in rhos) / len(rhos) if rhos else None, n_ort=float(np.mean([r["n"] for r in sonuclar])),
                            dilim_ort=[float(np.mean([r["dilim_ort"][i] for r in sonuclar])) for i in range(int(rules["kalicilik_dilim"]))])
            out["sonuc"][skor][str(gun)] = ozet
    return out


def hukum(ozet: dict[str, Any]) -> str:
    """Sade karar: aralığın alt sınırı > 0 ve ortalama Spearman > 0 → evet; üst sınırı < 0 → ters; yetersiz veri → belirsiz."""
    if "ga_alt" not in ozet:
        return "belirsiz (veri yetersiz)"
    if ozet["ga_alt"] > 0 and (ozet["rho"] or 0) > 0:
        return "evet"
    if ozet["ga_ust"] < 0:
        return "ters yönde"
    return "belirsiz"


# ------------------------------------------------------------------ kopya notu
def kopya_notu(adresler: list[str], hesaplar: dict[str, dict], t_ms: int, gun: int, client: Any, rules: dict | None = None, log=print) -> dict[str, Any]:
    """Üst dilim örneğinde trader getirisi ↔ gecikmeli kopya getirisi (``golge.calistir`` V0, ``kalicilik_kopya_gecikme_dk``). Fark = kopya aşınması.
    API son ``api_dolum_pencere_siniri`` dolumu verir: T..bugün dolum sayısı pencereye ulaşan adres 'pencere dışı' (dışarıda; sessiz eleme yok)."""
    from copytrade import golge
    from copytrade.kapi import CandleCache
    rules = rules or load_rules()
    bitis = t_ms + gun * DAY_MS
    limit = int(rules["api_dolum_pencere_siniri"])
    onbellek = CandleCache(client, t_ms, bitis)
    satirlar, disarida = [], {}
    for adres in adresler:
        hesap = hesaplar[adres]
        trader = ileri_getiri(hesap, t_ms, gun, rules)
        av = _son(_seri(hesap["av"]), t_ms)
        if trader is None or av is None or av[1] <= 0:
            disarida[adres] = "kâr geçmişi eksik"
            continue
        if len(client.fills(adres, t_ms, max_rows=limit)) >= limit:
            disarida[adres] = "pencere dışı (API son dolumlar penceresi)"
            continue
        fills = [f for f in client.fills(adres, t_ms, end_ms=bitis) if t_ms <= int(f["time"]) < bitis]
        satir = {"adres": adres, "trader": trader, "dolum": len(fills)}
        for gecikme in (int(g) for g in rules["kalicilik_kopya_gecikme_dk"]):
            if not fills:
                satir[f"kopya_{gecikme}"] = 0.0
                continue
            c = golge.calistir(fills, onbellek.for_fills(fills), av[1], style="intraday", etiket_ms=t_ms, end_ms=bitis, variant="V0", rules=rules, delay_min=gecikme)["defter"]
            satir[f"kopya_{gecikme}"] = None if c.get("net") is None else float(c["net"])
        satirlar.append(satir)
        log(f"kopya notu {adres[:10]}")
    ort = {}
    for gecikme in (int(g) for g in rules["kalicilik_kopya_gecikme_dk"]):
        cift = [(s["trader"], s[f"kopya_{gecikme}"]) for s in satirlar if s.get(f"kopya_{gecikme}") is not None]
        ort[str(gecikme)] = {"n": len(cift), "trader": float(np.mean([a for a, _ in cift])) if cift else None, "kopya": float(np.mean([b for _, b in cift])) if cift else None,
                             "asinma": float(np.mean([a - b for a, b in cift])) if cift else None}
    nedenler = {n: sum(1 for x in disarida.values() if x == n) for n in sorted(set(disarida.values()))}
    return {"t": pd.Timestamp(t_ms, unit="ms", tz="UTC").date().isoformat(), "gun": gun, "ornek": len(adresler), "disarida": nedenler, "ortalama": ort, "satir": satirlar}


# ------------------------------------------------------------------ sentetik (cevabı bilinen) veri
def sentetik_hesaplar(n: int, simdi_ms: int, kalici_beceri: bool, tohum: int = 0, gun: int = 520) -> dict[str, dict]:
    """Günlük kâr geçmişi olan ``n`` sentetik hesap. ``kalici_beceri``: her hesabın sabit günlük beklenen getirisi var (üst skor sonra da iyi gider); değilse hepsi sıfır
    beklentili. Her hesapta ara sıra yatırma/çekme (hesap değeri atlar, PnL atlamaz) — getiriye sızmamalı. Gerçek veri değildir."""
    rng = np.random.default_rng(tohum)
    out = {}
    for i in range(n):
        mu = rng.normal(0.0006, 0.0008) if kalici_beceri else 0.0
        gunluk = rng.normal(mu, 0.012, gun) * 1000.0            # 1000 $ hesap, sabit boy
        pnl = np.cumsum(gunluk)
        av = 1000.0 + pnl
        for k in rng.integers(30, gun - 30, 3):                    # yatırma/çekme: hesap değeri sıçrar, PnL değil
            av[k:] += rng.choice([-300.0, 500.0])
        av = np.maximum(av, 50.0)
        zaman = [simdi_ms - (gun - j) * DAY_MS for j in range(gun)]
        out[f"0x{i:040x}"] = {"av": [[t, float(v)] for t, v in zip(zaman, av)], "pnl": [[t, float(v)] for t, v in zip(zaman, pnl)]}
    return out


def sentetik_dogrulama(rules: dict | None = None, n: int = 300) -> dict[str, Any]:
    """Cevabı bilinen iki dünya: kalıcı beceri var → test 'evet' (en az bir skor/pencere); yok → hiçbir skor/pencere 'evet' değil. Döner özetler ve geçti bayrağı."""
    rules = rules or load_rules()
    simdi = 1_793_000_000_000
    var = analiz(sentetik_hesaplar(n, simdi, True, 1), simdi, rules)
    yok = analiz(sentetik_hesaplar(n, simdi, False, 2), simdi, rules)
    hukumler = {ad: {s: {g: hukum(o) for g, o in v["sonuc"][s].items()} for s in SKORLAR} for ad, v in (("var", var), ("yok", yok))}
    evet_var = sum(h == "evet" for s in hukumler["var"].values() for h in s.values())
    evet_yok = sum(h == "evet" for s in hukumler["yok"].values() for h in s.values())
    return {"n": n, "var": var, "yok": yok, "hukum": hukumler, "evet_var": evet_var, "evet_yok": evet_yok, "gecti": evet_var >= 4 and evet_yok == 0}


# ------------------------------------------------------------------ rapor
def _f(v: float | None, n: int = 4) -> str:
    return "–" if v is None else f"{v:.{n}f}".replace(".", ",")


def rapor(sonuc: dict[str, Any], deneme_sayisi: dict[str, int], kopya: dict[str, Any] | None, rules: dict | None = None, kaynak: str = "") -> str:
    rules = rules or load_rules()
    S = sonuc["sonuc"]
    evet = [f"{SKOR_AD[s]} · {g} gün" for s in SKORLAR for g, o in S[s].items() if hukum(o) == "evet"]
    ters = [f"{SKOR_AD[s]} · {g} gün" for s in SKORLAR for g, o in S[s].items() if hukum(o) == "ters yönde"]
    L = ["# Kalıcılık testi: skor gelecek getiriyi söylüyor mu?", ""]
    if evet:
        L.append(f"- **Kısmen evet:** {len(evet)} / {len(SKORLAR) * len(rules['kalicilik_ileri_gun'])} skor-pencere çiftinde üst dilim sonra da anlamlı biçimde daha iyi gitti: " + "; ".join(evet) + ".")
    else:
        L.append("- **Kanıt yok:** hiçbir skor-pencere çiftinde üst dilim sonra da güvenle daha iyi gitmedi.")
    if ters:
        L.append("- Ters yönde (üst dilim daha kötü): " + "; ".join(ters) + ".")
    L += [f"- Denenen yalnız üç skor; deneme defterinde toplam {deneme_sayisi['toplam']} deneme kayıtlı. Çok deneme, tek anlamlı sonucun ağırlığını düşürür.",
          "- Bu bir **keşif**; trader getirisidir, gecikmeli kopya değildir. Pilotu, seçimi ve eşikleri değiştirmez.",
          "- Evren bugünkü lider tablosu: **hayatta kalan yanlılığı** var, sonuç iyimser üst sınırdır.", ""]
    L += ["## Tablo", "", f"Hesap {sonuc['hesap']}, T anı {len(sonuc['t'])} ({sonuc['t'][0]} … {sonuc['t'][-1]}); dilim {rules['kalicilik_dilim']}. Aralık: blok bootstrap (blok {rules['kalicilik_blok_t']} T), %{int(100 * float(rules['kalicilik_ci']))}.", "",
          "| Skor | İleri | T | Üst − alt (ort.) | Aralık | Spearman (ort.) | Spearman > 0 | Sonuç |", "|---|---:|---:|---:|---|---:|---:|---|"]
    for s in SKORLAR:
        for g, o in S[s].items():
            L.append(f"| {SKOR_AD[s]} | {g} gün | {o['t_sayisi']} (atlanan {o['atlanan_t']}) | {_f(o.get('ust_alt'))} | [{_f(o.get('ga_alt'))}; {_f(o.get('ga_ust'))}] | {_f(o.get('rho'), 2)} | {_f(o.get('rho_pozitif'), 2)} | {hukum(o)} |")
    L += ["", "Dilim ortalama ileri getirisi (T ortalaması; 1 = en yüksek skor):", "", "| Skor | İleri | " + " | ".join(f"D{i}" for i in range(1, int(rules["kalicilik_dilim"]) + 1)) + " |", "|---|---:|" + "---:|" * int(rules["kalicilik_dilim"])]
    for s in SKORLAR:
        for g, o in S[s].items():
            if "dilim_ort" in o:
                L.append(f"| {SKOR_AD[s]} | {g} gün | " + " | ".join(_f(v) for v in o["dilim_ort"]) + " |")
    if kopya:
        L += ["", "## Kopya notu (üst dilim örneği; trader getirisi ↔ gecikmeli kopya)", "",
              f"- T {kopya['t']}, ileri {kopya['gun']} gün, örnek {kopya['ornek']} hesap; dışarıda: " + (", ".join(f"{n} {c}" for n, c in kopya['disarida'].items()) or "yok") + ".", "",
              "| Gecikme | n | Trader getirisi | Kopya getirisi | Kopya aşınması |", "|---|---:|---:|---:|---:|"]
        for g, o in kopya["ortalama"].items():
            L.append(f"| {g} dk | {o['n']} | {_f(o['trader'])} | {_f(o['kopya'])} | {_f(o['asinma'])} |")
    L += ["", "## Sınırlamalar", "",
          "- Evren: bugünkü lider tablosu (hesap değeri tabanı); batan/silinen hesaplar yok → hayatta kalan yanlılığı.",
          "- Getiri: kümülatif PnL farkı / T anı pencere hesap değeri medyanı; yatırma/çekme PnL'de olmadığı için etkisi arındırılmıştır, payda yine de değişebilir.",
          "- T anları örtüşür (14 gün adım, 28/56 gün ileri): bu yüzden blok bootstrap; yine de bağımsız gözlem sayısı T sayısından azdır.",
          "- Kopya notu tek T ve en çok 100 hesaplık örnek; API son 10.000 dolumu verdiği için çok aktif hesaplar dışarıda kalır.",
          "- " + (kaynak or "Kaynak belirtilmedi.")]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ CLI
def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--topla", action="store_true", help="portfolio verisini çek ve --onbellek altına yaz (parça parça, kaldığı yerden)")
    parser.add_argument("--evren", type=Path, help="kapı evren anlık görüntüsü (kapi --evren-yaz)")
    parser.add_argument("--parca", default="0/1", help="i/n: evrenin i. parçası")
    parser.add_argument("--sure-sn", type=int, default=0, help="toplama için zaman aşımı koruması (sn); dolunca temiz çıkar, kaldığı yerden sürer")
    parser.add_argument("--onbellek", type=Path, default=Path("kalicilik_onbellek"))
    parser.add_argument("--analiz", action="store_true")
    parser.add_argument("--kopya", action="store_true", help="analizden sonra üst dilim örneğinde kopya notu (ağ)")
    parser.add_argument("--sentetik", action="store_true", help="sentetik doğrulama: cevabı bilinen iki dünya")
    parser.add_argument("--rapor", type=Path)
    args = parser.parse_args(argv)
    rules = load_rules()
    if args.sentetik:
        d = sentetik_dogrulama(rules)
        print(json.dumps({k: d[k] for k in ("n", "hukum", "evet_var", "evet_yok", "gecti")}, ensure_ascii=False, indent=1))
        if not d["gecti"]:
            raise SystemExit("Sentetik doğrulama geçmedi: gerçek veriyle rapor yok.")
        return
    if args.topla:
        import time

        from copytrade.kapi import read_universe_snapshot
        from copytrade.tarama import PublicClient, RateLimiter
        i, n = (int(x) for x in args.parca.split("/"))
        adresler = [r["address"].lower() for r in read_universe_snapshot(args.evren)][i::n]
        args.onbellek.mkdir(parents=True, exist_ok=True)
        yol = args.onbellek / f"parca_{i}.json"
        veri = json.loads(yol.read_text()) if yol.exists() else {}
        client, bas = PublicClient(limiter=RateLimiter(1000)), time.monotonic()
        for k, adres in enumerate(adresler, 1):
            if adres in veri:
                continue
            if args.sure_sn and time.monotonic() - bas > args.sure_sn:
                print(f"süre doldu: {len(veri)}/{len(adresler)}; aynı komutla sürer")
                break
            veri[adres] = hesap_olustur(client.portfolio(adres))
            if k % 25 == 0:
                yol.write_text(json.dumps(veri), encoding="utf-8")
        yol.write_text(json.dumps(veri), encoding="utf-8")
        print(f"parça {i}/{n}: {sum(v is not None for v in veri.values())} / {len(adresler)} hesap")
    if args.analiz:
        import time

        from copytrade import deneme
        hesaplar = {a: h for p in sorted(args.onbellek.glob("parca_*.json")) for a, h in json.loads(p.read_text()).items() if h}
        simdi = int(time.time() * 1000)
        sonuc = analiz(hesaplar, simdi, rules)
        kopya = None
        if args.kopya:
            from copytrade.tarama import PublicClient, RateLimiter
            t = t_anlari(simdi, rules)[-1]
            gun = min(int(g) for g in rules["kalicilik_ileri_gun"])
            ust = sorted(((skorlar(h, t, rules)["getiri"], a) for a, h in hesaplar.items() if skorlar(h, t, rules)["getiri"] is not None), key=lambda r: (-r[0], r[1]))
            ust = [a for _, a in ust[: max(1, len(ust) // int(rules["kalicilik_dilim"]))]]
            ust = sorted(ust, key=lambda a: __import__("hashlib").sha256(f"kalicilik-kopya-{a}".encode()).hexdigest())[: int(rules["kalicilik_kopya_ornek"])]
            kopya = kopya_notu(ust, hesaplar, t, gun, PublicClient(limiter=RateLimiter(1000)), rules)
        metin = rapor(sonuc, deneme.sayim(), kopya, rules, kaynak="Kaynak: Hyperliquid `portfolio` (lider tablosu evreni)")
        if args.rapor:
            args.rapor.parent.mkdir(parents=True, exist_ok=True)
            args.rapor.write_text(metin, encoding="utf-8")
        (args.onbellek / "sonuc.json").write_text(json.dumps(sonuc, ensure_ascii=False), encoding="utf-8")
        print(metin)


if __name__ == "__main__":
    main()
