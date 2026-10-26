"""Faz 1 geniş aday görünümü: kanıt → kategori → zaman dilimi.

`results/faz1_adaylar.csv`'den (kullanıcı elemesi uygulanmış) üretir:
results/faz1_adaylar_genis.md. Bilgi amaçlıdır, karar değiştirmez.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ADAY = ROOT / "results" / "faz1_adaylar.csv"
SIRA = ROOT / "results" / "tv2" / "siralama.csv"
OUT = ROOT / "results" / "faz1_adaylar_genis.md"
BUGUN = pd.Timestamp.now().normalize()
U7_OOS = pd.Timestamp("2023-01-01")
# Getirisi gerçekçi olmayan, hesap/veri hatası şüphesi taşıyan adaylar (lider denetimi 2026-10-26).
HATA_SUPHESI = {"pcoISSiu", "jTHvkEVo", "9u8pzF0I"}


def kategori(sembol: str) -> tuple[int, str]:
    s = str(sembol).upper()
    if s == "KRIPTO25" or re.search(r"BINANCE|BYBIT|BITFINEX|BITSTAMP|KRAKEN|COINBASE|OKX|BINGX|BLOFIN|BITGET|MEXC|"
                                    r"KUCOIN|PIONEX|USDT|BTC|ETH|XRP|SOL", s):
        return 3, "Kripto"
    if s == "EMTIA" or re.search(r"GOLD|XAU|XAG", s):
        return 4, "Emtia"
    if re.search(r"CME|MNQ|NQ1|ES1", s):
        return 2, "ABD vadeli"
    return 1, "ABD hisse / ETF"


def dakika(tf: str) -> int:
    x = str(tf).upper()
    sabit = {"1D": 1440, "D": 1440, "3D": 4320, "1W": 10080}
    if x in sabit:
        return sabit[x]
    if x.endswith("H"):
        return int(x[:-1]) * 60
    return int(x)


def tf_adi(dk: int) -> str:
    return {1440: "Günlük", 4320: "3 gün", 10080: "Haftalık"}.get(dk, f"{dk // 60} saat" if dk >= 60 else f"{dk} dk")


def _f(x, d: int = 1) -> str:
    return "" if pd.isna(x) else f"{x:.{d}f}"


def main() -> int:
    t = pd.read_csv(ADAY).merge(pd.read_csv(SIRA)[["id", "surum_tarihi"]], left_on="kimlik", right_on="id", how="left")
    t["k"] = t["sembol"].map(kategori)
    t["dk"] = t["tf"].map(dakika)
    bas = pd.to_datetime(t["surum_tarihi"]).fillna(U7_OOS)
    t["islem_yil"] = t["sinama_islem"] / ((BUGUN - bas).dt.days / 365.25)

    def notlar(r) -> str:
        n = []
        if r.kimlik in HATA_SUPHESI:
            n.append("⚠ hesap hatası şüphesi")
        if r.kanit == "güçlü" and r.kaynak == "TV-2" and r.islem_yil < 30:
            n.append("tek enstrüman, yılda <30 işlem")
        if r.kisa_sinama:
            n.append("kısa sınama")
        if isinstance(r.supheli, str) and r.supheli:
            n.append(r.supheli)
        return "; ".join(n)

    L = ["# Faz 1 adaylar — güçlü ve kalan zayıflar", "",
         f"Tarih: {BUGUN.date()}. Toplam **{len(t)}** aday: güçlü **{(t.kanit == 'güçlü').sum()}**, "
         f"zayıf (kullanıcı elemesinden sonra kalan) **{(t.kanit == 'zayıf').sum()}**.", "",
         "**Sütunlar:** TF = zaman dilimi · Hafta = sınamada işlem yapılan hafta · İşlem = sınama işlem sayısı · "
         "İşlem/yıl = sınamada yıllık işlem · Yıllık % = ortak risk ölçeğinde yıllık getiri · p10 = temkinli haftalık "
         "alt sınır (%) · Net % = sınama dönemi net getirisi (U7: 2023 sonrası) · PF = kâr faktörü · MDD = en büyük düşüş %.", "",
         "**Kaynak:** TV-2 = TradingView stratejisi, yazarın sembolünde · U7-u6 = TradingView stratejisi, 25 sembollük "
         "sepette (ABD25 / KRIPTO25) · U7-u4 = kendi stratejimiz, sepette.", ""]
    ozet = pd.crosstab(t["kanit"], t["k"].map(lambda x: x[1]))
    L += ["## Özet", "", "| Kanıt | " + " | ".join(ozet.columns) + " | Toplam |", "|---|" + "---:|" * (len(ozet.columns) + 1)]
    L += [f"| {i} | " + " | ".join(str(v) for v in r) + f" | {r.sum()} |" for i, r in ozet.iterrows()]
    for kanit, baslik in (("güçlü", "Güçlü"), ("zayıf", "Zayıf (kalan)")):
        g0 = t[t["kanit"] == kanit]
        L += ["", f"## {baslik} ({len(g0)})"]
        for k, g in sorted(g0.groupby("k"), key=lambda x: x[0]):
            L += ["", f"### {k[1]} ({len(g)})", "",
                  "| # | TF | Kaynak | Kimlik | Sembol | Hafta | İşlem | İşlem/yıl | Yıllık % | p10 % | Net % | PF | MDD % | Not |",
                  "|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
            for i, r in enumerate(g.sort_values(["dk", "olcekli_yillik_getiri"], ascending=[True, False]).itertuples(), 1):
                kim = f"[{r.kimlik}]({r.url})" if isinstance(r.url, str) and r.url else r.kimlik
                pf = "" if pd.isna(r.pf) or r.pf == float("inf") else f"{r.pf:.2f}"
                L.append(f"| {i} | {tf_adi(r.dk)} | {r.kaynak} | {kim} | {r.sembol} | {r.sinama_hafta} | {r.sinama_islem} | "
                         f"{r.islem_yil:.0f} | {r.olcekli_yillik_getiri * 100:.1f} | {_f(r.alt_sinir_haftalik_p10 * 100, 2)} | "
                         f"{_f(r.sinama_net_yuzde)} | {pf} | {_f(r.mdd * 100)} | {notlar(r)} |")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(t)} aday -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
