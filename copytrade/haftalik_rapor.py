"""Haftalık geri bildirim raporu (ön kayıt D v1.3 madde 6; ``docs/GOREV_SECIM_V13.md`` paket D).

**Rotasyon içindir, karar analizi değildir.** Havuz genelinde seçim puanı ↔ o ana kadarki ileri getiri Spearman'ı ve tarz / kaldıraç dilimi kırılımı.
Kol bazında (oda, kontrol, taban, elle) getiri HİÇBİR yerde hesaplanmaz ya da yazılmaz: performans körlüğü 12. haftaya kadar sürer. Girdi: ``secim.json`` ve
``{adres: ileri getiri}`` (gölge defterinin etiket gününden bugüne maliyet sonrası net getirisi; yoksa rapor bunu söyler, sayı uydurmaz).
``--gecis`` ile aynı haftalık çalışma geçiş kaydını da günceller (``copytrade/gecis.py``).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from copytrade import analiz_d, gecis
from copytrade.kurallar import load_rules

MIN_N = 4          # n ≤ 3'te Fisher z tanımsız (analiz_d); kırılımda "n yetersiz"


def _group(name: str, pairs: list[tuple[float, float]], rules: dict) -> dict[str, Any]:
    out = analiz_d.birincil_spearman([p for p, _ in pairs], [g for _, g in pairs], rules)
    return {"ad": name, **out}


def hesapla(result: dict[str, Any], ileri: dict[str, float], rules: dict | None = None) -> dict[str, Any]:
    """Havuz = puanı olan adresler (``havuz`` kolu; taban/elle gibi havuz dışı adresler girmez)."""
    rules = rules or load_rules()
    members = {a.lower(): e for a, e in result["adresler"].items() if e.get("puan") is not None and "havuz" in e["kollar"]}
    returns = {a.lower(): float(v) for a, v in ileri.items() if v is not None}
    have = [a for a in sorted(members) if a in returns]
    missing = len(members) - len(have)
    pairs = {a: (float(members[a]["puan"]), returns[a]) for a in have}
    out: dict[str, Any] = {"n": len(have), "eksik": missing, "havuz": len(members), "veri_eksik": analiz_d.veri_eksik(missing, len(members), rules),
                           "birincil": _group("havuz", list(pairs.values()), rules) if have else None, "kirilim": []}
    cuts: dict[str, list[tuple[float, float]]] = {}
    for a in have:
        e = members[a]
        tarz, _, dilim = str(e.get("dilim") or "").partition("/")
        for name in (f"tarz: {e.get('tarz')}", f"kaldıraç: {dilim}" if dilim else None, str(e.get("dilim")) if dilim else None):
            if name and not name.endswith("None"):
                cuts.setdefault(name, []).append(pairs[a])
    for name in sorted(cuts, key=lambda n: (n.count("/") > 0, n)):
        out["kirilim"].append(_group(name, cuts[name], rules))
    return out


def _fmt(value: float | None, digits: int = 3) -> str:
    return "–" if value is None else f"{value:.{digits}f}".replace(".", ",")


def rapor(result: dict[str, Any], ileri: dict[str, float], tarih: str, rules: dict | None = None) -> str:
    rules = rules or load_rules()
    out = hesapla(result, ileri, rules)
    lines = [f"# Haftalık geri bildirim — {tarih}", "",
             "> Bu rapor **rotasyon içindir**, **karar analizi değildir**. Kol bazında (oda / kontrol / taban / elle) getiri yazılmaz (performans körlüğü, 12. haftaya kadar).", "",
             f"- Seçim {result.get('secim_surumu')} · kapı {result.get('kapi_tarihi')} · havuz {out['havuz']} adres · ileri getirisi olan {out['n']} · eksik {out['eksik']}"
             + (" · **veri eksik** (hafta işaretlendi)" if out["veri_eksik"] else "") + "."]
    if not out["n"]:
        return "\n".join(lines + ["", "**ileri getiri verisi yok** (gölge henüz başlamadı ya da dolum/işaret gelmedi); Spearman hesaplanmadı.", ""])
    b = out["birincil"]
    lines += ["", "## Havuz genelinde puan ↔ ileri getiri (Spearman)", "",
              f"- ρ = {_fmt(b['rho'])} · n = {b['n']} · tek yönlü p = {_fmt(b['p_tek_yonlu'])} · %90 GA [{_fmt(b['ga90_alt'])}; {_fmt(b['ga90_ust'])}]",
              "", "## Kırılım (tarz, kaldıraç dilimi)", "", "| grup | n | ρ | tek yönlü p | %90 GA |", "|---|---|---|---|---|"]
    for g in out["kirilim"]:
        if g["n"] < MIN_N:
            lines.append(f"| {g['ad']} | {g['n']} | n yetersiz | – | – |")
        else:
            lines.append(f"| {g['ad']} | {g['n']} | {_fmt(g['rho'])} | {_fmt(g['p_tek_yonlu'])} | [{_fmt(g['ga90_alt'])}; {_fmt(g['ga90_ust'])}] |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--secim", type=Path, required=True, help="secim.json")
    parser.add_argument("--getiri", type=Path, default=None, help="{adres: ileri getiri} JSON (yoksa rapor 'ileri getiri verisi yok' der)")
    parser.add_argument("--tarih", required=True)
    parser.add_argument("--cikti", type=Path, default=Path("rotasyon"))
    parser.add_argument("--gecis", action="store_true", help="aynı haftalık çalışmada geçiş kaydını da güncelle (kayit.jsonl, degerlendirme.jsonl)")
    args = parser.parse_args(argv)
    result = json.loads(args.secim.read_text(encoding="utf-8"))
    ileri = json.loads(args.getiri.read_text(encoding="utf-8")) if args.getiri else {}
    rules = load_rules()
    args.cikti.mkdir(parents=True, exist_ok=True)
    if args.gecis:
        written = gecis.haftalik(args.cikti / "kayit.jsonl", args.cikti / "degerlendirme.jsonl", result, args.tarih, rules)
        print(f"Geçiş: {len(written)} olay.")
    (args.cikti / f"haftalik_{args.tarih}.md").write_text(rapor(result, ileri, args.tarih, rules), encoding="utf-8")
    print(f"Rapor: {args.cikti / f'haftalik_{args.tarih}.md'}")


if __name__ == "__main__":
    main()
