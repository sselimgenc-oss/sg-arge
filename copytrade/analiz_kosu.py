"""12. hafta analizi için uçtan uca koşucu (ön kayıt D v1.3 madde 4–7); ``analiz_d`` fonksiyonlarını çağırır, kendi istatistiği yoktur.

**Tarih kilidi:** ``kurallar.yaml`` ``onkayit_analiz_tarihi`` öncesinde gerçek veriyle çalışmayı reddeder; yalnız ``--sentetik``. Gölge verisi
görülmeden yazıldı; çıktı biçimi ``tests/test_analiz_kosu.py`` altın örneğiyle sabit.
Girdi (gerçek): ``secim.json``; ``getiri`` = {adres: 12 hafta net getiri} (havuzun tamamı, ``pilot_veri`` ile aynı yöntem); isteğe bağlı
``gunluk`` = {"oda": [...], "kontrol": [...], "btc": [...]} (eşit ağırlıklı kohort ve eşleştirilmiş kontrol günlük net getirisi, BTC günlük getirisi).
Birincil: havuzun tamamı puan ↔ net getiri (Spearman). İkincil: oda ↔ kontrol günlük farkı, BTC betası düzeltilmiş. Tanımlayıcı: tarz / kaldıraç kırılımı.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from copytrade import analiz_d, haftalik_rapor
from copytrade.kurallar import load_rules


class TarihKilidi(RuntimeError):
    pass


def kilit(bugun: date, sentetik: bool, rules: dict) -> None:
    acilis = date.fromisoformat(str(rules["onkayit_analiz_tarihi"]))
    if not sentetik and bugun < acilis:
        raise TarihKilidi(f"Gerçek veriyle analiz {acilis} tarihinden önce yapılmaz (ön kayıt; bugün {bugun}). Yalnız --sentetik.")


def sentetik_veri(tohum: int = 0) -> tuple[dict[str, Any], dict[str, float], dict[str, list[float]]]:
    """Tohumlu, gerçek veriyle ilgisiz örnek: 40 adres (puan ile ilişkili getiri), 84 günlük kohort/kontrol/BTC."""
    rng = np.random.default_rng(tohum)
    adresler = {}
    getiri = {}
    for i in range(40):
        adres = f"0x{i:040x}"
        puan = float(rng.normal())
        adresler[adres] = {"puan": puan, "kollar": ["havuz"] + (["oda"] if i < 12 else []), "tarz": "intraday" if i % 2 else "swing",
                           "dilim": f"{'intraday' if i % 2 else 'swing'}/{'alt' if i % 4 < 2 else 'ust'}"}
        getiri[adres] = float(0.3 * puan + rng.normal(scale=0.5))
    gunluk = {"oda": list(rng.normal(0.0005, 0.01, 84)), "kontrol": list(rng.normal(0.0, 0.01, 84)), "btc": list(rng.normal(0.0, 0.02, 84))}
    return {"secim_surumu": "sentetik", "kapi_tarihi": "sentetik", "adresler": adresler}, getiri, gunluk


def kos(secim: dict[str, Any], getiri: dict[str, float], gunluk: dict[str, list[float]] | None, rules: dict | None = None) -> dict[str, Any]:
    rules = rules or load_rules()
    ozet = haftalik_rapor.hesapla(secim, getiri, rules)
    ikincil, kohort_mutlak = None, None
    if gunluk and all(gunluk.get(k) for k in ("oda", "kontrol", "btc")):
        oda_sayisi = sum("oda" in e.get("kollar", []) for e in secim["adresler"].values())
        if oda_sayisi >= int(rules["secim_oda_min"]):
            ikincil = analiz_d.ikincil_fark(gunluk["oda"], gunluk["kontrol"], gunluk["btc"], rules=rules)
            kohort_mutlak = float(np.prod(1.0 + np.asarray(gunluk["oda"], dtype=float)) - 1.0)
    birincil = ozet["birincil"] or analiz_d.spearman_ozeti(None, 0, rules)
    return {"ozet": ozet, "birincil": birincil, "ikincil": ikincil, "kohort_mutlak": kohort_mutlak,
            "karar": analiz_d.karar(birincil, ikincil, kohort_mutlak, rules)}


def _f(value: float | None, digits: int = 3) -> str:
    return "–" if value is None else f"{value:.{digits}f}".replace(".", ",")


def tablo(sonuc: dict[str, Any], etiket: str, tarih: str) -> str:
    b, o, i, k = sonuc["ozet"], sonuc["birincil"], sonuc["ikincil"], sonuc["karar"]
    rows = [("birincil", "n (havuz / eksik)", f"{o['n']} ({b['havuz']} / {b['eksik']})"),
            ("birincil", "veri eksik", "evet" if b["veri_eksik"] else "hayır"),
            ("birincil", "ρ (Spearman)", _f(o["rho"])),
            ("birincil", "tek yönlü p", _f(o["p_tek_yonlu"])),
            ("birincil", "%90 GA", f"[{_f(o['ga90_alt'])}; {_f(o['ga90_ust'])}]")]
    if i:
        rows += [("ikincil", "BTC beta düzeltilmiş günlük fark", _f(i["fark"], 5)), ("ikincil", "β", _f(i["beta"])),
                 ("ikincil", "%95 GA", f"[{_f(i['ga_alt'], 5)}; {_f(i['ga_ust'], 5)}]"), ("ikincil", "gün", str(i["n"])),
                 ("ikincil", "kohort mutlak getiri", _f(sonuc["kohort_mutlak"]))]
    else:
        rows.append(("ikincil", "durum", "yok (oda eşiğin altında ya da günlük seri verilmedi)"))
    rows.append(("karar", "sonuç", k["sonuc"]))
    lines = [f"# 12. hafta analizi — {etiket} — {tarih}", "", f"> {k['gerekce']}", "", "| bölüm | ölçü | değer |", "|---|---|---|"]
    lines += [f"| {a} | {m} | {v} |" for a, m, v in rows]
    lines += ["", "## Tanımlayıcı kırılım (tarz, kaldıraç dilimi)", "", "| grup | n | ρ |", "|---|---|---|"]
    lines += [f"| {g['ad']} | {g['n']} | {'n yetersiz' if g['n'] < haftalik_rapor.MIN_N else _f(g['rho'])} |" for g in b["kirilim"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None, bugun: date | None = None) -> str:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--secim", type=Path)
    parser.add_argument("--getiri", type=Path, help="{adres: 12 hafta net getiri}")
    parser.add_argument("--gunluk", type=Path, help='{"oda": [...], "kontrol": [...], "btc": [...]}')
    parser.add_argument("--sentetik", action="store_true", help="gerçek veri okumadan tohumlu örnekle koş (tarih kilidinden muaf)")
    parser.add_argument("--cikti", type=Path)
    args = parser.parse_args(argv)
    rules = load_rules()
    bugun = bugun or datetime.now(UTC).date()
    kilit(bugun, args.sentetik, rules)
    if args.sentetik:
        secim, getiri, gunluk = sentetik_veri()
    else:
        if not (args.secim and args.getiri):
            parser.error("gerçek koşu için --secim ve --getiri gerekir")
        secim = json.loads(args.secim.read_text(encoding="utf-8"))
        getiri = json.loads(args.getiri.read_text(encoding="utf-8"))
        gunluk = json.loads(args.gunluk.read_text(encoding="utf-8")) if args.gunluk else None
    metin = tablo(kos(secim, getiri, gunluk, rules), "SENTETİK (gerçek veri değil)" if args.sentetik else "GERÇEK", bugun.isoformat())
    if args.cikti:
        args.cikti.write_text(metin, encoding="utf-8")
    print(metin)
    return metin


if __name__ == "__main__":
    main()
