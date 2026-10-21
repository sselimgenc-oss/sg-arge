"""Strategy card loader, schema validator and consistency report.

Usage::

    python -m engine.spec docs/spec/                    # validate, exit 1 on 'tam' card errors
    python -m engine.spec --kontrol docs/spec/          # also write results/kart_kontrol.md

Cards are never modified. ``tam`` cards must have parsable ``giris``/``cikis``,
defined indicator names and defined ``name.attr`` fields. Other statuses
(eksik, ihtiyari, ...) are checked too but their findings are informational.
``ozel_kod: true`` cards may have empty expressions and names outside the library
(they are ported by hand); syntax errors still count.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import expr as _expr
from . import gosterge as _ind

DURUMLAR = ("gizli", "ihtiyari", "sadece_short", "eksik", "dakikalik", "tam", "kapsam_disi")
TARZLAR = ("day", "swing", "belirsiz")
TF_RE = re.compile(r"^\d+[mHDWMr]$")  # r = renko bricks (not time based)
MTF_RE = re.compile(r"^\d+[mHDWMr](/\d+[mHDWMr])*$")
BASE_NAMES = frozenset({"open", "high", "low", "close", "volume"})
RUNTIME_NAMES = frozenset({"giris", "giris_fiyati", "giris_stop", "giris_hedef", "bars_since_entry", "endeks_close", "stop_mesafesi", "giris_modu"})
REQUIRED = ("id", "ad", "kaynak", "tarz", "tf", "gostergeler", "giris", "cikis", "spec_durumu", "belirsiz", "ozel_kod")
EXPR_FIELDS = ("giris", "cikis")
EXIT_FIELDS = ("stop", "hedef", "iz_suren", "zaman_stop")  # structured exits: a card may rely on them alone
OZEL_NEDENLERI = (
    "bekleyen_emir",       # stop/limit entries, fills inside a bar (engine fills at next open only)
    "seans_saat",          # exchange/server clock windows, session open/close, spread or margin filters
    "desen",               # pivot/pattern recognition (double bottom, ABC, zigzag, fractal levels)
    "durum_makinesi",      # multi-stage state machines
    "ozel_gosterge",       # indicator not in the library and used by fewer than two translatable cards
    "cok_enstruman",       # needs other instruments' data (correlation, rotation inputs)
    "portfoy_rotasyonu",   # allocation between instruments (Composer), leverage phase
    "tanim_belirsiz",      # rule text does not define a needed formula
    "renko",               # non-time bars
    "ml",                  # machine learning / training
    "tick_veri",           # tick or sub-minute data
    "durum_bilgisi",       # exit depends on how the entry was triggered
)


@dataclass
class Issue:
    kod: str            # short machine code
    mesaj: str
    ciddi: bool = True  # False = informational


@dataclass
class CardResult:
    card: dict[str, Any]
    path: Path
    issues: list[Issue] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.card.get("id", self.path.stem))

    @property
    def durum(self) -> str:
        return str(self.card.get("spec_durumu"))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.ciddi]


def load_cards(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    cards = []
    for path in sorted(directory.glob("*.yaml")):
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        cards.append((path, data))
    return cards


def _check_expression(text: Any, field_name: str, defined: set[str], gost: dict[str, Any], issues: list[Issue], *, runtime: bool) -> None:
    if text is None or (isinstance(text, str) and not text.strip()):
        return
    if not isinstance(text, str):
        issues.append(Issue("ifade_tipi", f"{field_name}: metin bekleniyordu, {type(text).__name__} bulundu"))
        return
    try:
        parsed = _expr.parse(text)
    except _expr.ExprError as exc:
        issues.append(Issue("ifade_ayristirilamadi", f"{field_name}: {exc} :: {text[:120]}"))
        return
    allowed = defined | BASE_NAMES | (RUNTIME_NAMES if runtime else set())
    for name in sorted(parsed.names - allowed):
        issues.append(Issue("tanimsiz_ad", f"{field_name}: tanimsiz ad '{name}'"))
    bare = parsed.names - {n for n, _ in parsed.attrs}
    for name in sorted(bare & set(gost)):
        spec = gost[name]
        if isinstance(spec, dict) and spec.get("f") in _ind.REGISTRY and _ind.COLUMNS.get(spec["f"]):
            issues.append(Issue("cok_sutunlu_cirplak", f"{field_name}: '{name}' ({spec['f']}) cok sutunlu, alan secilmeli: {', '.join(_ind.COLUMNS[spec['f']])}"))
    for name, attr in sorted(parsed.attrs):
        spec = gost.get(name)
        if not isinstance(spec, dict) or spec.get("f") not in _ind.REGISTRY:
            continue
        columns = _ind.COLUMNS.get(spec["f"])
        if columns is None or attr not in columns:
            issues.append(Issue("tanimsiz_alan", f"{field_name}: '{name}.{attr}' gecersiz ({spec['f']} alanlari: {', '.join(columns) if columns else 'yok'})"))


def validate_card(path: Path, card: Any, all_ids: set[str]) -> CardResult:
    result = CardResult(card if isinstance(card, dict) else {}, path)
    issues = result.issues
    if not isinstance(card, dict):
        issues.append(Issue("kart_tipi", "kart bir YAML sozlugu degil"))
        return result
    for key in REQUIRED:
        if key not in card:
            issues.append(Issue("eksik_alan", f"zorunlu alan yok: {key}"))
    if card.get("id") is not None and str(card["id"]) != path.stem:
        issues.append(Issue("id_dosya", f"id '{card['id']}' dosya adiyla ({path.stem}) uyusmuyor"))
    if card.get("tarz") not in TARZLAR:
        issues.append(Issue("tarz", f"tarz gecersiz: {card.get('tarz')}"))
    if card.get("spec_durumu") not in DURUMLAR:
        issues.append(Issue("durum", f"spec_durumu gecersiz: {card.get('spec_durumu')}"))
    if not TF_RE.match(str(card.get("tf", ""))):
        issues.append(Issue("tf", f"tf gecersiz: {card.get('tf')}"))
    mtf = card.get("mtf")
    if mtf is not None and not MTF_RE.match(str(mtf)):
        issues.append(Issue("mtf", f"mtf gecersiz: {mtf}"))
    if not isinstance(card.get("belirsiz"), list):
        issues.append(Issue("belirsiz_tipi", "belirsiz bir liste olmali"))
    if not isinstance(card.get("ozel_kod"), bool):
        issues.append(Issue("ozel_kod_tipi", "ozel_kod bool olmali"))
    alias = card.get("alias_of")
    if alias is not None and alias not in all_ids:
        issues.append(Issue("alias", f"alias_of '{alias}' bulunamadi"))

    gost = card.get("gostergeler")
    if not isinstance(gost, dict):
        issues.append(Issue("gostergeler_tipi", "gostergeler bir sozluk olmali"))
        gost = {}
    ozel = bool(card.get("ozel_kod"))
    seen: list[str] = []
    for name, spec in gost.items():
        if not isinstance(spec, dict) or "f" not in spec:
            issues.append(Issue("gosterge_tipi", f"gosterge '{name}' {{f: ...}} sozlugu olmali"))
            continue
        if spec["f"] == _ind.SERI:
            ifade = spec.get("ifade")
            try:
                parsed = _expr.parse(ifade)
            except (_expr.ExprError, TypeError) as exc:
                issues.append(Issue("seri_ifade", f"seri '{name}': ifade ayristirilamadi: {exc}"))
            else:
                known = set(seen) | BASE_NAMES
                for bad in sorted(parsed.names - known):
                    issues.append(Issue("seri_tanimsiz_ad", f"seri '{name}': '{bad}' bu seriden once tanimli degil"))
        elif spec["f"] not in _ind.REGISTRY:
            issues.append(Issue("tanimsiz_gosterge", f"gosterge '{name}': '{spec['f']}' kutuphanede yok", ciddi=not ozel))
        seen.append(name)
        if "tf" in spec and not TF_RE.match(str(spec["tf"])):
            issues.append(Issue("gosterge_tf", f"gosterge '{name}': tf gecersiz: {spec['tf']}"))
    defined = set(gost)

    # exit rules may use entry state (bars_since_entry, giris_fiyati, ...); entries may not
    _check_expression(card.get("giris"), "giris", defined, gost, issues, runtime=False)
    _check_expression(card.get("cikis"), "cikis", defined, gost, issues, runtime=True)
    for block, sub in (("stop", "secenekler"), ("stop", "ifade"), ("hedef", "ifade"), ("kar_kilidi", "stop"), ("kismi_kar", "tetik"), ("kismi_kar", "kalan_stop")):
        value = card.get(block)
        if isinstance(value, dict):
            target = value.get(sub)
            for item in (target if isinstance(target, list) else [target]):
                if isinstance(item, str):
                    _check_expression(item, f"{block}.{sub}", defined, gost, issues, runtime=True)

    if card.get("spec_durumu") == "tam":
        has_exit = any(card.get(key) for key in EXIT_FIELDS)
        for key in EXPR_FIELDS:
            value = card.get(key)
            if not isinstance(value, str) or not value.strip():
                # lider kurali: bos ifade yalniz ozel_kod kartlarda, mantik `belirsiz`'de;
                # istisna: cikisi yalniz yapisal stop/hedef/iz_suren/zaman_stop olan kart
                if key == "cikis" and has_exit:
                    continue
                issues.append(Issue("tam_bos_ifade", f"durum 'tam' ama {key} bos", ciddi=not ozel))
    if ozel and card.get("spec_durumu") in ("tam", "dakikalik"):
        nedeni = card.get("ozel_kod_nedeni")
        if nedeni not in OZEL_NEDENLERI:
            issues.append(Issue("ozel_kod_nedeni", f"ozel_kod kartta gecerli ozel_kod_nedeni yok: {nedeni!r} (gecerli: {', '.join(OZEL_NEDENLERI)})"))
    if not ozel and card.get("ozel_kod_nedeni"):
        issues.append(Issue("ozel_kod_nedeni_gereksiz", "ozel_kod: false kartta ozel_kod_nedeni olmamali"))
    if ozel:
        # ozel_kod kartlarda ifade ozel gostergelere (kutuphanede olmayan adlara) baglanabilir;
        # bu adlar bilgi amaclidir. Sozdizimi hatalari ve gecersiz alanlar hata olarak kalir.
        for issue in issues:
            if issue.kod == "tanimsiz_ad":
                issue.ciddi = False
    return result


def validate_directory(directory: Path) -> list[CardResult]:
    cards = load_cards(directory)
    ids = {str(c.get("id")) for _, c in cards if isinstance(c, dict)}
    return [validate_card(path, card, ids) for path, card in cards]


def _fold(issues: list[Issue], *, tam: bool) -> list[Issue]:
    """Findings count as errors only for 'tam' cards."""
    return issues if tam else [Issue(i.kod, i.mesaj, False) for i in issues]


def render_report(results: list[CardResult]) -> str:
    durum_sayilari = Counter(r.durum for r in results)
    sorunlu = [r for r in results if r.issues]
    tam_hatali = [r for r in results if r.durum == "tam" and r.errors]
    lines = ["# Kart kontrol raporu", "", f"Kart sayisi: {len(results)} | `tam` kartlarda hata: **{len(tam_hatali)}** | sorun bildirilen kart: {len(sorunlu)}", ""]
    lines += ["## Durum dagilimi", "", "| durum | kart |", "|---|---|"]
    lines += [f"| {d} | {durum_sayilari.get(d, 0)} |" for d in DURUMLAR if durum_sayilari.get(d, 0)]
    lines += [""]

    hazir = [r for r in results if r.durum == "tam" and not r.errors and not r.card.get("ozel_kod")]
    hazir_dk = [r for r in results if r.durum == "dakikalik" and not r.errors and not r.card.get("ozel_kod")]
    lines.insert(3, f"T5b taramasina hazir kart (`tam`, hatasiz, `ozel_kod: false`): **{len(hazir)}**; ayrica `dakikalik` (yalniz kripto testi) hazir: **{len(hazir_dk)}**")
    lines.insert(4, "")
    gosterge_kart: dict[str, set[str]] = defaultdict(set)
    ifade_hata: list[tuple[str, str, str]] = []
    ad_say: Counter = Counter()
    for r in results:
        for issue in r.issues:
            if issue.kod == "tanimsiz_gosterge":
                key = re.search(r"'([^']+)' kutuphanede", issue.mesaj).group(1)  # type: ignore[union-attr]
                gosterge_kart[key].add(r.id)
            elif issue.kod == "ifade_ayristirilamadi":
                ifade_hata.append((r.id, r.durum, issue.mesaj))
            elif issue.kod == "tanimsiz_ad":
                ad_say[issue.mesaj.split("'")[1]] += 1

    lines += ["## `tam` kartlarda hatalar (T5'e engel)", ""]
    if not tam_hatali:
        lines += ["Yok.", ""]
    for r in tam_hatali:
        lines.append(f"- **{r.id}**")
        lines += [f"  - [{i.kod}] {i.mesaj}" for i in r.errors]
    lines += [""]

    lines += ["## Kutuphanede olmayan gosterge adlari", "", "| gosterge | kart sayisi | kartlar |", "|---|---|---|"]
    for key, cards in sorted(gosterge_kart.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        ids = ", ".join(sorted(cards)[:8]) + (" ..." if len(cards) > 8 else "")
        lines.append(f"| {key} | {len(cards)} | {ids} |")
    if not gosterge_kart:
        lines.append("| - | 0 | |")
    lines += [""]

    lines += ["## Ayristirilamayan giris/cikis ifadeleri", "", f"Toplam: {len(ifade_hata)} (durum `tam` olanlar once)", ""]
    for id_, durum, mesaj in sorted(ifade_hata, key=lambda x: (x[1] != "tam", x[0])):
        lines.append(f"- {id_} ({durum}): {mesaj}")
    lines += [""]

    if ad_say:
        lines += ["## Tanimsiz adlar (ifadelerde kullanilan, gostergeler'de olmayan)", "", "| ad | kullanim |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in ad_say.most_common()]
        lines += [""]

    other = [r for r in sorunlu if r.durum != "tam" and r not in tam_hatali]
    lines += ["## Diger kartlarda sorun sayisi", "", f"`tam` olmayan {len(other)} kartta bilgi amacli bulgu var (ayrintilar yukaridaki tablolarda); kartlar degistirilmedi.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory", nargs="?", default="docs/spec", help="card directory")
    parser.add_argument("--kontrol", metavar="DIR", help="validate DIR and write the report")
    parser.add_argument("--out", default="results/kart_kontrol.md", help="report path for --kontrol")
    args = parser.parse_args(argv)
    directory = Path(args.kontrol or args.directory)
    results = validate_directory(directory)
    for r in results:
        r.issues = _fold(r.issues, tam=(r.durum == "tam"))
    if args.kontrol:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_report(results) + "\n", encoding="utf-8")
        print(f"rapor yazildi: {out}")
    tam_hatali = [r for r in results if r.durum == "tam" and r.errors]
    print(f"{len(results)} kart, `tam` hatali: {len(tam_hatali)}")
    for r in tam_hatali[:20]:
        print(f"  {r.id}: " + "; ".join(i.mesaj for i in r.errors)[:200])
    return 1 if tam_hatali else 0


if __name__ == "__main__":
    sys.exit(main())
