"""TV-2 sıralama ve kopya ayıklama (docs/TEST_YAPISI.md Adım 3): kapıyı geçenler, eleme değil sıralama.

1. Ortak ölçek: her adayın sürüm sonrası günlük net getirisi yıllık %10 oynaklığa ölçeklenir (yazarın boyutu etkisiz).
2. Belirsizlik: ölçeklenmiş haftalık getiri ortalamasının blok bootstrap %10 alt sınırı (ana ölçüt, yüksek PF değil).
3. Kopya ayıklama: ortak günlerde günlük getiri korelasyonu > 0,8 VE etkin (getirisi sıfır olmayan) günlerin > %50'si
   örtüşen adaylar aynı kümede; her kümeden en iyi sıralı tek temsilci. (İşlem tarihleri yerine etkin gün örtüşmesi.)

    python -m backtests.tv2_sirala            # results/tv2/satirlar + getiriler -> results/tv2/siralama.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtests.asama2b import deflated_sharpe_ratio

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tv2"
HEDEF_OYNAKLIK = 0.10
KORELASYON_ESIK = 0.8
ORTUSME_ESIK = 0.5
BOOT = 2000
BLOK_HAFTA = 4
TOHUM = 20261024


def _getiri(kimlik: str, bas: pd.Timestamp) -> pd.Series:
    s = pd.read_csv(OUT / "getiriler" / f"{kimlik}.csv", index_col=0, parse_dates=True)["getiri"]
    s.index = pd.to_datetime(s.index, utc=True)
    return s[s.index >= bas]


def olcekle(g: pd.Series) -> pd.Series:
    sd = g.std(ddof=1) * np.sqrt(365)
    return g * (HEDEF_OYNAKLIK / sd) if sd and np.isfinite(sd) and sd > 0 else g * np.nan


def alt_sinir(haftalik: pd.Series, rng: np.random.Generator) -> float:
    """Haftalık ortalamanın blok bootstrap %10 yüzdeliği (bloklar BLOK_HAFTA hafta, çakışan başlangıç)."""
    x = haftalik.dropna().to_numpy()
    n = len(x)
    if n < BLOK_HAFTA * 2:
        return np.nan
    bloklar = int(np.ceil(n / BLOK_HAFTA))
    ort = np.empty(BOOT)
    for b in range(BOOT):
        bas = rng.integers(0, n - BLOK_HAFTA + 1, bloklar)
        ornek = np.concatenate([x[s:s + BLOK_HAFTA] for s in bas])[:n]
        ort[b] = ornek.mean()
    return float(np.percentile(ort, 10))


def kumele(seriler: dict[str, pd.Series], sira: list[str]) -> dict[str, str]:
    """Sıradaki her aday, kendinden önceki bir temsilciyle kopya ise onun kümesine girer."""
    temsilci: dict[str, str] = {}
    temsilciler: list[str] = []
    for k in sira:
        a = seriler[k]
        for t in temsilciler:
            b = seriler[t]
            ortak = a.index.intersection(b.index)
            if len(ortak) < 30:
                continue
            x, y = a.loc[ortak], b.loc[ortak]
            if x.std() == 0 or y.std() == 0:
                continue
            kor = float(np.corrcoef(x, y)[0, 1])
            etkin_a, etkin_b = set(ortak[x != 0]), set(ortak[y != 0])
            ortusme = len(etkin_a & etkin_b) / max(min(len(etkin_a), len(etkin_b)), 1)
            if kor > KORELASYON_ESIK and ortusme > ORTUSME_ESIK:
                temsilci[k] = t
                break
        else:
            temsilci[k] = k
            temsilciler.append(k)
    return temsilci


def etkin_deneme_sayisi(seriler: dict[str, pd.Series]) -> float:
    """Return correlation-eigenvalue effective trial count for information only.

    This deliberately does not participate in the ranking or representative
    selection.  Missing dates are treated as zero returns, matching the
    existing copy-clustering input.
    """
    if not seriler:
        return float("nan")
    frame = pd.concat(seriler, axis=1).fillna(0.0)
    if frame.shape[1] == 1:
        return 1.0
    corr = frame.corr().fillna(0.0).to_numpy(dtype=float)
    np.fill_diagonal(corr, 1.0)
    eigenvalues = np.clip(np.linalg.eigvalsh(corr), 0.0, None)
    denominator = float(np.square(eigenvalues).sum())
    if denominator <= 0:
        return float("nan")
    return float(eigenvalues.sum() ** 2 / denominator)


def main() -> None:
    satirlar = [json.loads(p.read_text()) for p in sorted((OUT / "satirlar").glob("*.json"))]
    gecen = [s for s in satirlar if s.get("karar") == "gecti"]
    rng = np.random.default_rng(TOHUM)
    kayit, seriler = [], {}
    for s in gecen:
        bas = pd.Timestamp(s["surum_tarihi"], tz="UTC")
        g = olcekle(_getiri(s["id"], bas))
        seriler[s["id"]] = g.fillna(0.0)
        haftalik = (1 + g.fillna(0.0)).resample("W").prod() - 1
        kayit.append({
            "id": s["id"], "sembol": s.get("sembol"), "tf": s.get("tf"), "surum_tarihi": s.get("surum_tarihi"),
            "sinama_hafta": len(haftalik), "sinama_islem": s.get("uyg_sinama_islem"),
            "olcekli_yillik_getiri": float(haftalik.mean() * 52) if len(haftalik) else np.nan,
            "alt_sinir_haftalik_p10": alt_sinir(haftalik, rng),
            "yazar_boyutu_net_yuzde": s.get("uyg_sinama_net_yuzde"), "uyg_sinama_pf": s.get("uyg_sinama_pf"),
            "uyg_sinama_mdd": s.get("uyg_sinama_mdd"), "altut_sinama_yuzde": s.get("altut_sinama_yuzde"),
            "veri": s.get("veri"), "uyari": s.get("uyari", ""),
        })
    n_eff = etkin_deneme_sayisi(seriler)
    trials = max(1, int(np.ceil(n_eff))) if np.isfinite(n_eff) else 1
    for row in kayit:
        row["n_eff"] = n_eff
        row["dsr"] = deflated_sharpe_ratio(seriler[row["id"]], trials)
    tablo = pd.DataFrame(kayit).sort_values("alt_sinir_haftalik_p10", ascending=False, na_position="last")
    kume = kumele(seriler, list(tablo["id"]))
    tablo["kume_temsilcisi"] = tablo["id"].map(kume)
    tablo["temsilci"] = tablo["id"] == tablo["kume_temsilcisi"]
    tablo.insert(0, "sira", range(1, len(tablo) + 1))
    tablo.to_csv(OUT / "siralama.csv", index=False)
    print(tablo[["sira", "id", "sembol", "tf", "alt_sinir_haftalik_p10", "olcekli_yillik_getiri", "sinama_hafta",
                 "kume_temsilcisi"]].to_string(index=False))


if __name__ == "__main__":
    main()
