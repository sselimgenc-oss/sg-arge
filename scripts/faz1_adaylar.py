"""Faz 1 aday tablosu: TV-2 ve U7 küme temsilcileri tek tabloda.

Karar değiştirmez, eleme yapmaz; kullanıcının paper seçimi için bilgi tablosudur.
Çıktı: results/faz1_adaylar.csv ve results/faz1_adaylar.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TV2 = ROOT / "results" / "tv2"
U7 = ROOT / "results" / "u7" / "siralama.csv"
SUPHELI = [ROOT / "docs" / "denetim" / "tv2_supheli.md", ROOT / "docs" / "denetim" / "tv2_kripto_disi_supheli.md"]
OUT = ROOT / "results" / "faz1_adaylar"


def _supheli() -> dict[str, str]:
    """Şüphe taraması tablolarındaki `kimlik` → işaret metni."""
    isaret = {}
    for yol in SUPHELI:
        if not yol.exists():
            continue
        for satir in yol.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*`([^`]+)`\s*\|[^|]*\|([^|]*)\|", satir)
            if m:
                isaret[m.group(1)] = m.group(2).strip()
    return isaret


def _tv2() -> pd.DataFrame:
    df = pd.read_csv(TV2 / "siralama.csv")
    df = df[df["temsilci"].astype(str) == "True"]
    isaret = _supheli()
    satirlar = []
    for r in df.itertuples():
        yol = TV2 / "satirlar" / f"{r.id}.json"
        ek = json.loads(yol.read_text(encoding="utf-8")) if yol.exists() else {}
        satirlar.append({
            "kaynak": "TV-2", "kimlik": r.id, "sembol": r.sembol, "tf": r.tf,
            "sinama_hafta": r.sinama_hafta, "sinama_islem": r.sinama_islem,
            "olcekli_yillik_getiri": r.olcekli_yillik_getiri, "alt_sinir_haftalik_p10": r.alt_sinir_haftalik_p10,
            "sinama_net_yuzde": ek.get("uyg_sinama_net_yuzde"), "pf": r.uyg_sinama_pf, "mdd": r.uyg_sinama_mdd,
            "kisa_sinama": bool(ek.get("kisa_sinama", False)), "lookahead_riskli": bool(ek.get("lookahead_riskli", False)),
            "supheli": isaret.get(r.id, ""), "veri": r.veri, "url": ek.get("url", ""),
        })
    return pd.DataFrame(satirlar)


def _u7() -> pd.DataFrame:
    df = pd.read_csv(U7)
    df = df[df["temsilci"].astype(str) == "True"]
    return pd.DataFrame({
        "kaynak": "U7-" + df["grup"], "kimlik": df["varyant"], "sembol": df["piyasa"], "tf": df["tf"],
        "sinama_hafta": df["sinama_hafta"], "sinama_islem": df["sinama_islem"],
        "olcekli_yillik_getiri": df["olcekli_yillik_getiri"], "alt_sinir_haftalik_p10": df["alt_sinir_haftalik_p10"],
        "sinama_net_yuzde": df["oos_net_1x"] * 100, "pf": None, "mdd": None,
        "kisa_sinama": False, "lookahead_riskli": False, "supheli": "", "veri": "", "url": "",
    })


def main() -> int:
    tablo = pd.concat([_tv2(), _u7().astype({"pf": float, "mdd": float})], ignore_index=True)
    # Bilgi sütunu (eleme değil): kısa sınama, şüphe işareti ya da < 30 işlem yoksa "güçlü".
    tablo["kanit"] = ["güçlü" if not (k or s or i < 30) else "zayıf"
                      for k, s, i in zip(tablo["kisa_sinama"], tablo["supheli"], tablo["sinama_islem"])]
    # TV-2 Adım 3 ile aynı yön: temkinli alt sınır (p10) önce; p10 hesaplanamayanlar sonda.
    tablo = tablo.sort_values(["alt_sinir_haftalik_p10", "olcekli_yillik_getiri"], ascending=False,
                              na_position="last").reset_index(drop=True)
    tablo.insert(0, "sira", range(1, len(tablo) + 1))
    tablo.to_csv(OUT.with_suffix(".csv"), index=False)

    def yuzde(x):
        return "" if pd.isna(x) else f"{x:.1f}"

    sayim = tablo["kaynak"].value_counts().to_dict()
    md = ["# Faz 1 aday tablosu", "",
          f"Küme temsilcileri: **{len(tablo)}** ({', '.join(f'{k} {v}' for k, v in sorted(sayim.items()))}). "
          "Hepsi tek kapıyı geçti; bu tablo eleme yapmaz, paper seçimi kullanıcınındır.", "",
          "Yıllık % = ortak risk ölçeğinde yıllık getiri. Net % = sınama dönemi (U7: 2023 sonrası) net getiri. "
          "İşaret: K = kısa sınama (sürüm sonrası < 1 yıl ya da < 10 işlem haftası), L = lookahead riski, S = şüphe taraması.", "",
          f"Kanıt (bilgi, eleme değil): güçlü = kısa sınama yok, şüphe işareti yok, ≥ 30 işlem → "
          f"**{(tablo['kanit'] == 'güçlü').sum()}** güçlü, {(tablo['kanit'] == 'zayıf').sum()} zayıf. "
          "Sıra: temkinli haftalık alt sınır (p10), sonra yıllık getiri.", "",
          "| # | Kanıt | Kaynak | Kimlik | Sembol | TF | Hafta | İşlem | Yıllık % | p10 haftalık % | Net % | PF | MDD % | İşaret |",
          "|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in tablo.itertuples():
        isaret = " ".join(filter(None, ["K" if r.kisa_sinama else "", "L" if r.lookahead_riskli else "",
                                        f"S ({r.supheli})" if r.supheli else ""]))
        kimlik = f"[{r.kimlik}]({r.url})" if r.url else r.kimlik
        md.append(f"| {r.sira} | {r.kanit} | {r.kaynak} | {kimlik} | {r.sembol} | {r.tf} | {r.sinama_hafta} | {r.sinama_islem} | "
                  f"{yuzde(r.olcekli_yillik_getiri * 100)} | {'' if pd.isna(r.alt_sinir_haftalik_p10) else f'{r.alt_sinir_haftalik_p10 * 100:.2f}'} | {yuzde(r.sinama_net_yuzde)} | "
                  f"{'' if pd.isna(r.pf) or r.pf == float('inf') else f'{r.pf:.2f}'} | {'' if pd.isna(r.mdd) else yuzde(r.mdd * 100)} | {isaret} |")
    OUT.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(tablo)} aday -> {OUT.with_suffix('.csv').name}, {OUT.with_suffix('.md').name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
