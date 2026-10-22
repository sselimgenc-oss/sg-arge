#!/usr/bin/env python3
"""T13/T25: assemble existing validation outputs into one final strategy report (success / failure list).

This module deliberately performs no backtest or statistical calculation.  It only applies the documented outcome
precedence to CSV/YAML/Markdown inputs that already exist, and stays useful while later-stage files have not been
generated yet (a "Henuz yok" line lists the missing ones).

One row per card.  Every (market, timeframe) result is a *record*; the card takes the best record by
``Gecti > Kosullu > Bekliyor > Reddedildi > Dogrulanamaz > Ertelendi > Kapsam disi`` (``Bekliyor`` is the transitional
"a later stage has not run yet" state and disappears once the leader's runs are merged).  A point-in-time (PIT) stage 2b row
replaces the fixed-universe stage 2b row of the same card and market.  Reasons are written ``<asama>: <neden>``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_COLUMNS = [
    "id", "ad", "kaynak", "tarz", "tf", "nihai_durum", "alt_neden", "en_iyi_piyasa", "en_iyi_tf", "piyasa_ayrintisi",
    "pf_is", "oos_getiri", "bootstrap_mdd_p95", "evren", "metrik", "gerekce", "ayrinti_json",
]
STATUS_RANK = {
    "Gecti": 6, "Kosullu": 5, "Bekliyor": 4, "Reddedildi": 3, "Dogrulanamaz": 2, "Ertelendi": 1, "Kapsam disi": 0,
}
STAGE_DEPTH = {"asama2b": 4, "asama2a": 3, "asama1": 2, "kart": 1}
DISPLAY = {
    "Gecti": "Geçti", "Kosullu": "Koşullu", "Bekliyor": "Bekliyor", "Reddedildi": "Reddedildi",
    "Dogrulanamaz": "Doğrulanamaz", "Ertelendi": "Ertelendi", "Kapsam disi": "Kapsam dışı",
}
INPUT_FILES = ("tarama.csv", "tarama_rotasyon.csv", "asama2a.csv", "asama2b.csv", "asama2b_pit.csv", "codex21.csv", "portfoy.md")
CODEX_IDS = {f"C{i:02d}" for i in range(1, 22)}
NOTE_PRIORITY = ("T22", "T21", "T20", "T19", "T16")  # task notes that explain why a card could not be tested


def _read_csv(path: Path) -> pd.DataFrame:
    """Read optional files with a stable empty table when they are not present."""
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _clean(value: object) -> str:
    return "" if value is None or pd.isna(value) else str(value).strip()


def _num(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _yaml_cards(card_dir: Path) -> dict[str, dict[str, Any]]:
    cards = {}
    for path in card_dir.glob("*.yaml"):
        card = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if card.get("id"):
            cards[str(card["id"])] = card
    return cards


def _metadata(index: pd.DataFrame, cards: dict[str, dict[str, Any]], identifier: str) -> dict[str, str]:
    indexed = index[index["id"].astype(str) == identifier] if not index.empty and "id" in index else pd.DataFrame()
    source = indexed.iloc[0].to_dict() if not indexed.empty else {}
    card = cards.get(identifier, {})
    card_source = card.get("kaynak") or {}
    return {
        "id": identifier,
        "ad": _clean(card.get("ad") or source.get("ad") or identifier),
        "kaynak": _clean(card_source.get("dosya") or source.get("kaynak") or card_source.get("url")),
        "tarz": _clean(card.get("tarz") or source.get("tarz")),
        "tf": _clean(card.get("tf") or source.get("tf")),
    }


# ----------------------------------------------------------------------------------------------- reasons
def _task_note(card: dict[str, Any]) -> str:
    """The most recent explanatory ``Txx:`` note of a card, whitespace collapsed (empty when none)."""
    notes = [str(item) for item in (card.get("belirsiz") or [])]
    for prefix in NOTE_PRIORITY:
        hits = [n for n in notes if n.startswith(f"{prefix}:")]
        if hits:
            return re.sub(r"\s+", " ", hits[-1]).strip()[:260]
    return ""


def _skip_reason(neden: str) -> str:
    """Standardised reason of a stage 1 row that could not be computed."""
    text = neden.lower()
    if text.startswith("piyasa_ozgu"):
        return f"piyasa ozgu ({neden.split(':', 1)[-1]})"
    if "dakikalik_veri_yok" in text or "dakikalik veri yok" in text:
        return "dakikalik veri yok"
    if text.startswith("veri_kalitesi"):
        return "BIST 1H veri kalitesi"
    if text.startswith("endeks_yok"):
        return f"endeks serisi yok ({neden.split(':', 1)[-1]})"
    if text.startswith("evren_kucuk"):
        return "evren cok kucuk (8 sembolden az)"
    if text.startswith("veri_yok"):
        return f"veri yok ({neden.split(':', 1)[-1]})" if ":" in neden else "veri yok"
    if text.startswith("motor_destegi_yok"):
        return f"motor destegi yok ({neden.split(':', 1)[-1]})"
    return neden or "tarama sonucu yok"


def _underlying(card: dict[str, Any], yeniden: set[str]) -> tuple[str, str]:
    """(status, reason) of a card from its specification alone (no usable run)."""
    status = _clean(card.get("spec_durumu"))
    nedeni = _clean(card.get("ozel_kod_nedeni"))
    if status == "kapsam_disi":
        return "Kapsam disi", "kapsam disi: strateji degil (meta/ornek)"
    if status == "sadece_short":
        return "Ertelendi", "ertelendi: sadece short (long-only temel modda test yok)"
    if str(card.get("id", "")) in yeniden and (card.get("erisim_engeli") or status == "eksik"):  # ported cards leave the list
        return "Dogrulanamaz", "dogrulanamaz: kaynak erisilemedi"
    if status == "gizli":
        return "Dogrulanamaz", "dogrulanamaz: kural kaynakta gizli"
    if status == "ihtiyari":
        return "Dogrulanamaz", "dogrulanamaz: ihtiyari/yoruma dayali kural (mekanik degil)"
    if status == "eksik":
        suffix = f" (ozel kod: {nedeni})" if card.get("ozel_kod") and nedeni else ""
        return "Dogrulanamaz", f"dogrulanamaz: kaynakta sinyal tanimi yok{suffix}"
    if card.get("ozel_kod"):
        return "Dogrulanamaz", "dogrulanamaz: ozel kod" + (f" ({nedeni})" if nedeni else "")
    return "Dogrulanamaz", "dogrulanamaz: henuz yok"


# ----------------------------------------------------------------------------------------------- records
def _records(identifier: str, tarama: pd.DataFrame, asama2a: pd.DataFrame, asama2b: pd.DataFrame) -> list[dict[str, Any]]:
    """One record per (market, tf) found in any stage: the deepest stage that has a row decides its status."""
    found: dict[tuple[str, str], dict[str, Any]] = {}

    def put(key: tuple[str, str], depth: str, status: str, reason: str, row: Any = None) -> None:
        current = found.get(key)
        if current is None or STAGE_DEPTH[depth] >= STAGE_DEPTH[current["asama"]]:
            record = {"piyasa": key[0], "tf": key[1], "asama": depth, "durum": status, "neden": reason}
            for field in ("pf_is", "metrik"):  # inherit what an earlier stage knew
                if current is not None and current.get(field) not in (None, ""):
                    record[field] = current[field]
            if row is not None:
                pf = _num(row.get("PF_1x"))
                if pf == pf:
                    record["pf_is"] = pf
                if _clean(row.get("metrik")):
                    record["metrik"] = _clean(row.get("metrik"))
            found[key] = record

    for row in (_rows(tarama, identifier)):
        key = (_clean(row.get("piyasa")), _clean(row.get("tf")))
        durum = _clean(row.get("durum"))
        if durum == "Hesaplandi":
            if _bool(row.get("asama2_aday")):
                put(key, "asama1", "Bekliyor", "asama2a: bekliyor", row)
            else:
                put(key, "asama1", "Reddedildi", f"asama1: {_clean(row.get('neden')).replace(',', ', ')}", row)
        else:
            put(key, "asama1", "Dogrulanamaz", f"dogrulanamaz: {_skip_reason(_clean(row.get('neden')))}")
    for row in _rows(asama2a, identifier):
        key = (_clean(row.get("piyasa")), _clean(row.get("tf")) or _tf_of(found, _clean(row.get("piyasa"))))
        karar = _clean(row.get("karar"))
        if karar == "Gecti (null)":
            put(key, "asama2a", "Bekliyor", "asama2b: bekliyor", row)
        elif karar.startswith("Reddedildi"):
            what = "BIST USD kapisi" if "USD" in karar else "null'u gecemedi (piyasa betasi)"
            detail = _clean(row.get("neden"))
            put(key, "asama2a", "Reddedildi", f"asama2a: {what}" + (f" - {detail}" if detail else ""), row)
        elif karar:
            put(key, "asama2a", "Dogrulanamaz", f"dogrulanamaz: asama2a {karar.lower()}" + (f" ({_clean(row.get('neden'))})" if _clean(row.get("neden")) else ""), row)
    for row in _rows(asama2b, identifier):
        key = (_clean(row.get("piyasa")), _clean(row.get("tf")) or _tf_of(found, _clean(row.get("piyasa"))))
        karar = _clean(row.get("karar"))
        if karar in STATUS_RANK:
            reason = f"asama2b: {_clean(row.get('neden')) or 'gerekce sonuc dosyasinda bos'}" if karar != "Gecti" else "asama2b: tum paper kapilari gecti"
            put(key, "asama2b", karar, reason, row)
            record = found[key]
            record.update(
                oos_getiri=_num(row.get("oos_net")), bootstrap_mdd_p95=_num(row.get("bootstrap_mdd_p95")),
                evren=_clean(row.get("evren")), metrik=_clean(row.get("metrik")) or record.get("metrik") or "",
            )
    return list(found.values())


def _tf_of(found: dict[tuple[str, str], dict[str, Any]], market: str) -> str:
    """Stage 2 files of the daily pipeline have no tf column: reuse the one of the stage 1 record of that market."""
    for (m, tf), _ in found.items():
        if m == market:
            return tf
    return ""


def _rows(table: pd.DataFrame, identifier: str) -> list[dict[str, Any]]:
    if table.empty or "id" not in table:
        return []
    return table[table["id"].astype(str) == identifier].to_dict("records")


def _best(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None
    return sorted(
        records,
        key=lambda r: (-STATUS_RANK[r["durum"]], -STAGE_DEPTH[r["asama"]], r["piyasa"], r["tf"]),
    )[0]


def _detail(records: list[dict[str, Any]]) -> str:
    parts = []
    for r in sorted(records, key=lambda r: (-STATUS_RANK[r["durum"]], r["piyasa"], r["tf"])):
        where = "/".join(x for x in (r["piyasa"], r["tf"]) if x)
        parts.append(f"{where}: {r['durum']} ({r['neden']})")
    return "; ".join(parts)


def _codex_pf(codex: pd.DataFrame, identifier: str, market: str) -> float:
    if codex.empty or "satir" not in codex:
        return float("nan")
    rows = codex[(codex["satir"].astype(str) == identifier) & (codex["piyasa"].astype(str) == market)
                 & (codex["donem"].astype(str) == "replikasyon") & (codex["senaryo"].astype(str) == "1x")]
    return _num(rows.iloc[0]["pf"]) if not rows.empty else float("nan")


def _merge_pit(asama2b: pd.DataFrame, pit: pd.DataFrame) -> pd.DataFrame:
    """A PIT stage 2b row replaces the fixed-universe row of the same card and market."""
    if pit.empty or "id" not in pit:
        return asama2b
    if asama2b.empty:
        return pit
    taken = set(zip(pit["id"].astype(str), pit["piyasa"].astype(str)))
    keep = asama2b[[(i, m) not in taken for i, m in zip(asama2b["id"].astype(str), asama2b["piyasa"].astype(str))]]
    return pd.concat([keep, pit], ignore_index=True)


def _combine_scans(tarama: pd.DataFrame, rotation: pd.DataFrame) -> pd.DataFrame:
    if rotation.empty:
        return tarama
    both = pd.concat([tarama, rotation], ignore_index=True)
    keys = [c for c in ("id", "piyasa", "tf") if c in both]
    return both.drop_duplicates(keys, keep="last", ignore_index=True)


def _decide(identifier: str, card: dict[str, Any], yeniden: set[str], records: list[dict[str, Any]], cards: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Final status, reason, best market/tf of one card."""
    best = _best(records)
    if card.get("alias_of") and card["alias_of"] in cards and card["alias_of"] != identifier:
        return {"alias": str(card["alias_of"])}
    underlying_status, underlying_reason = _underlying(card, yeniden)
    if best is not None and STATUS_RANK[best["durum"]] > STATUS_RANK["Dogrulanamaz"]:
        return {"durum": best["durum"], "neden": best["neden"], "piyasa": best["piyasa"], "tf": best["tf"], "kayit": best}
    # nothing was decided by a run: the specification (or the scan's skip reasons) explains the outcome
    if underlying_status in {"Kapsam disi", "Ertelendi"}:
        return {"durum": underlying_status, "neden": underlying_reason, "piyasa": "", "tf": ""}
    spec_blocked = underlying_reason != "dogrulanamaz: henuz yok" or card.get("ozel_kod") or _clean(card.get("spec_durumu")) in {"gizli", "ihtiyari", "eksik"}
    if spec_blocked:
        return {"durum": underlying_status, "neden": underlying_reason, "piyasa": "", "tf": ""}
    if best is not None:
        reasons = sorted({r["neden"].removeprefix("dogrulanamaz: ") for r in records})
        specific = [x for x in reasons if not x.startswith("piyasa ozgu")]  # "other markets cannot run it" is the least informative reason
        reasons = specific or reasons
        return {"durum": "Dogrulanamaz", "neden": "dogrulanamaz: " + "; ".join(reasons), "piyasa": best["piyasa"], "tf": best["tf"]}
    if _clean(card.get("spec_durumu")) in {"tam", "dakikalik"}:
        return {"durum": "Bekliyor", "neden": "asama1: tarama bekliyor", "piyasa": "", "tf": ""}
    return {"durum": underlying_status, "neden": underlying_reason, "piyasa": "", "tf": ""}


def build_report(spec_dir: Path, results_dir: Path) -> pd.DataFrame:
    """Build, write, and return the deterministic final report table."""
    index = _read_csv(spec_dir / "INDEKS.csv")
    yeniden = set(_read_csv(spec_dir / "YENIDEN.csv").get("id", pd.Series(dtype=str)).astype(str))
    cards = _yaml_cards(spec_dir)
    tarama = _combine_scans(_read_csv(results_dir / "tarama.csv"), _read_csv(results_dir / "tarama_rotasyon.csv"))
    asama2a = _read_csv(results_dir / "asama2a.csv")
    asama2b = _merge_pit(_read_csv(results_dir / "asama2b.csv"), _read_csv(results_dir / "asama2b_pit.csv"))
    codex = _read_csv(results_dir / "codex21.csv")
    ids = set(index.get("id", pd.Series(dtype=str)).astype(str)) | set(cards) | CODEX_IDS
    rows: dict[str, dict[str, Any]] = {}
    for identifier in sorted(ids):
        metadata = _metadata(index, cards, identifier)
        if identifier in CODEX_IDS and metadata["ad"] == identifier and not codex.empty and "satir" in codex:
            codex_rows = codex[codex["satir"].astype(str) == identifier]
            if not codex_rows.empty:
                metadata.update(ad=f"Codex Algo 21: {_clean(codex_rows.iloc[0].get('aile'))}", kaynak="Codex Algo 21 raporu", tarz="swing", tf="1D")
        card = cards.get(identifier, {})
        records = _records(identifier, tarama, asama2a, asama2b)
        if identifier in CODEX_IDS and not any(r["asama"] == "asama2b" for r in records):
            # the Codex rows have their own pipeline: a similarly named YAML card's result must not stand in for it
            records = [{"piyasa": "", "tf": "1D", "asama": "asama1", "durum": "Bekliyor", "neden": "asama2b: bekliyor (Codex Algo 2b)"}]
        for record in records:
            if identifier in CODEX_IDS and record["asama"] == "asama2b" and pd.isna(record.get("pf_is", float("nan"))):
                record["pf_is"] = _codex_pf(codex, identifier, record["piyasa"])
        verdict = _decide(identifier, card, yeniden, records, cards)
        metadata["ayrinti_json"] = json.dumps(
            [{k: (None if isinstance(v, float) and v != v else v) for k, v in r.items()} for r in records], ensure_ascii=False, separators=(",", ":"),
        )
        metadata["piyasa_ayrintisi"] = _detail(records)
        metadata["gerekce"] = _task_note(card)
        if "alias" in verdict:
            metadata["_alias"] = verdict["alias"]
            rows[identifier] = metadata
            continue
        best = verdict.get("kayit") or {}
        metadata.update(
            nihai_durum=verdict["durum"], alt_neden=verdict["neden"], en_iyi_piyasa=verdict["piyasa"], en_iyi_tf=verdict["tf"],
            pf_is=best.get("pf_is"), oos_getiri=best.get("oos_getiri"), bootstrap_mdd_p95=best.get("bootstrap_mdd_p95"),
            evren=best.get("evren", ""), metrik=best.get("metrik", ""),
        )
        rows[identifier] = metadata
    for identifier, row in rows.items():  # an alias card takes the verdict of the card it duplicates
        if "_alias" in row:
            main = rows[row["_alias"]]
            row.update({k: main.get(k) for k in ("nihai_durum", "en_iyi_piyasa", "en_iyi_tf", "pf_is", "oos_getiri", "bootstrap_mdd_p95", "evren", "metrik")})
            row["alt_neden"] = f"{main['alt_neden']} (alias: {row['_alias']})"
    table = pd.DataFrame(list(rows.values())).reindex(columns=OUTPUT_COLUMNS)
    table["_rank"] = table["nihai_durum"].map(STATUS_RANK)
    table = table.sort_values(["_rank", "id"], ascending=[False, True], kind="stable").drop(columns="_rank").reset_index(drop=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(results_dir / "SONUC.csv", index=False)
    missing = [name for name in INPUT_FILES if not (results_dir / name).exists()]
    _write_markdown(table, results_dir / "SONUC.md", missing, results_dir / "portfoy.md")
    return table


# ----------------------------------------------------------------------------------------------- markdown
def _fmt(value: Any, fmt: str) -> str:
    number = _num(value)
    return "-" if pd.isna(number) else format(number, fmt)


def _where(row: Any) -> str:
    return "/".join(x for x in (_clean(row.en_iyi_piyasa), _clean(row.en_iyi_tf)) if x) or "-"


def _group_key(reason: str) -> str:
    return reason.split(":", 1)[0].strip()


def _portfolio_summary(path: Path) -> list[str]:
    if not path.exists():
        return ["Henüz yok: `results/portfoy.md`.", ""]
    text = path.read_text(encoding="utf-8")
    match = re.search(r"## Birlesik portfoy.*?(?=\n## )", text, re.S)
    first = text.splitlines()[2] if len(text.splitlines()) > 2 else ""
    lines = [first, "", "**Birleşik portföy (eşit risk, 1/N sermaye):**", *(match.group(0).splitlines()[1:] if match else []), "", "Ayrıntı (adaylar tek tek, korelasyon, yöntem): [`results/portfoy.md`](portfoy.md).", ""]
    return lines


def _write_markdown(table: pd.DataFrame, path: Path, missing: list[str], portfolio: Path) -> None:
    counts = table["nihai_durum"].value_counts()
    lines = ["# Strateji sonuç listesi (başarılı / başarısız)", "",
             "Bu rapor mevcut sonuç dosyalarını birleştirir; yeni backtest veya istatistik hesaplamaz. Kart başına tek nihai durum vardır "
             "(en iyi piyasa/zaman dilimi satırı): **Geçti > Koşullu > Bekliyor > Reddedildi > Doğrulanamaz > Ertelendi > Kapsam dışı**. "
             "`Bekliyor`, sonraki aşamanın henüz koşmadığı geçici durumdur. Diğer piyasalar `results/SONUC.csv` içindeki `piyasa_ayrintisi` sütunundadır.", ""]
    if missing:
        lines += [f"> Henüz yok: {', '.join(missing)}. Bu dosyalara bağlı aşamalar `Bekliyor` görünebilir.", ""]
    lines += ["## Özet sayılar", "", "| Durum | Toplam | Günlük/swing | Gün içi (day) |", "|---|---:|---:|---:|"]
    for status in sorted(STATUS_RANK, key=lambda s: -STATUS_RANK[s]):
        subset = table[table["nihai_durum"] == status]
        if subset.empty:
            continue
        lines.append(f"| {DISPLAY[status]} | {len(subset)} | {int((subset['tarz'] != 'day').sum())} | {int((subset['tarz'] == 'day').sum())} |")
    lines += [f"| **Toplam** | **{len(table)}** | {int((table['tarz'] != 'day').sum())} | {int((table['tarz'] == 'day').sum())} |", ""]

    passed = table[table["nihai_durum"] == "Gecti"]
    lines += ["## Paper trade'e hazır (Geçti)", ""]
    if passed.empty:
        lines += ["- Yok.", ""]
    else:
        lines += ["| ID | Strateji | Piyasa/tf | PF (IS, 1x) | OOS getiri | Bootstrap MDD95 | Evren |", "|---|---|---|---:|---:|---:|---|"]
        for row in passed.itertuples():
            lines.append(f"| {row.id} | {row.ad} | {_where(row)} | {_fmt(row.pf_is, '.2f')} | {_fmt(row.oos_getiri, '.1%')} | {_fmt(row.bootstrap_mdd_p95, '.1%')} | {_clean(row.evren) or '-'} |")
        lines.append("")

    conditional = table[table["nihai_durum"] == "Kosullu"]
    lines += ["## Koşullu", ""]
    if conditional.empty:
        lines += ["- Yok.", ""]
    else:
        lines += ["| ID | Strateji | Piyasa/tf | PF (IS, 1x) | OOS getiri | Bootstrap MDD95 | Şerh |", "|---|---|---|---:|---:|---:|---|"]
        for row in conditional.itertuples():
            lines.append(f"| {row.id} | {row.ad} | {_where(row)} | {_fmt(row.pf_is, '.2f')} | {_fmt(row.oos_getiri, '.1%')} | {_fmt(row.bootstrap_mdd_p95, '.1%')} | {row.alt_neden.removeprefix('asama2b: ')} |")
        lines.append("")

    waiting = table[table["nihai_durum"] == "Bekliyor"]
    if not waiting.empty:
        lines += ["## Bekliyor (sonraki aşama koşmadı)", "", "| ID | Strateji | Piyasa/tf | Bekleyen aşama |", "|---|---|---|---|"]
        lines += [f"| {r.id} | {r.ad} | {_where(r)} | {r.alt_neden} |" for r in waiting.itertuples()]
        lines.append("")

    lines += ["## Önerilen portföy", "", *_portfolio_summary(portfolio)]

    rejected = table[table["nihai_durum"] == "Reddedildi"]
    lines += ["## Reddedildi", ""]
    if rejected.empty:
        lines += ["- Yok.", ""]
    for stage, title in (("asama1", "Aşama 1 (hızlı tarama)"), ("asama2a", "Aşama 2a (rastgele seçim/giriş testi, piyasa betası)"), ("asama2b", "Aşama 2b (OOS, stres, plato, bootstrap)")):
        group = rejected[rejected["alt_neden"].map(_group_key) == stage]
        if group.empty:
            continue
        reasons = group["alt_neden"].str.split(":", n=1).str[1].str.strip()
        lines += [f"### {title}: {len(group)}", "", "| ID | Strateji | Piyasa/tf | Alt neden |", "|---|---|---|---|"]
        lines += [f"| {r.id} | {r.ad} | {_where(r)} | {reason} |" for r, reason in zip(group.itertuples(), reasons)]
        lines.append("")

    for status, heading in (("Dogrulanamaz", "Doğrulanamaz"), ("Ertelendi", "Ertelendi"), ("Kapsam disi", "Kapsam dışı")):
        subset = table[table["nihai_durum"] == status]
        lines += [f"## {heading} ({len(subset)})", ""]
        if subset.empty:
            lines += ["- Yok.", ""]
            continue
        grouped = subset.assign(_neden=subset["alt_neden"].str.split(":", n=1).str[1].str.strip().fillna(""))
        for reason, group in sorted(grouped.groupby("_neden"), key=lambda item: (-len(item[1]), item[0])):
            lines += [f"<details><summary><b>{reason or '-'}</b> ({len(group)})</summary>", "", "| ID | Strateji | Gerekçe (karttaki not) |", "|---|---|---|"]
            lines += [f"| {r.id} | {r.ad} | {_clean(r.gerekce).replace('|', '/') or '-'} |" for r in group.itertuples()]
            lines += ["", "</details>", ""]

    lines += ["## Yöntem özeti", "",
              "Her strateji kartı aynı koşullarda ([`docs/EVRENSEL_KURALLAR.md`](../docs/EVRENSEL_KURALLAR.md), eşikler [`docs/ELEME_KRITERLERI.md`](../docs/ELEME_KRITERLERI.md)) sınandı: "
              "long-only, kaldıraçsız, sinyal kapanmış barla, dolum sonraki açılışta, işlem başı %0,5 risk ve ATR14×3 standart stop (kaynak stopu yoksa). "
              "**Aşama 1** IS dönemde (2020-01 → 2024-09) hızlı tarama yapar: işlem ≥ 30, PF ≥ 1,1 ve 2x maliyette net > 0. "
              "**Aşama 2a** aynı çıkış kurallarıyla rastgele girişli (rotasyon kartlarında rastgele seçimli) bir null dağılımı kurar; kart PF ve ortalama R'de (rotasyonda PF ve CAGR'de) null'un %95'ini geçmelidir, "
              "aksi halde getiri piyasanın kendi sürüklenmesidir (piyasa betası); BIST USD bazında değerlendirilir. "
              "**Aşama 2b** OOS (2024-10 sonrası), ön dönem (2015-2019), 2x/3x maliyet ve +1 bar gecikme stresi, kaynak merkezli parametre platosu (komşuluklarda pozitif oran ≥ %60), "
              "20 günlük block bootstrap ile **MDD95 ≤ %15** ve DSR'yi birlikte uygular. Geçmeyen **Reddedildi**; her kapıyı geçip ön dönem negatif, OOS örneği küçük ya da evren yanlılığı gibi şerhi olan **Koşullu**; hepsini geçen **Geçti**. "
              "Test edilemeyenler (kaynakta sinyal yok, gizli, özel kod, dakikalık veri yok, kaynak erişilemedi) **Doğrulanamaz**, short fazına bırakılanlar **Ertelendi** sayılır; bu başarısızlık değildir.", "",
              "## Uyarılar", "",
              "- BIST ve ABD evrenlerinde survivorship yanlılığı vardır; tarihsel (PIT) evren satırı varsa sabit evren satırının yerine geçer (ABD tam, BIST 2020 sonrası). Olumlu sonuç canlı kanıt değildir.",
              "- Çok sayıda strateji denendiği için şansla geçenler beklenir; DSR paper trading için bilgi niteliğindedir.",
              "- Gün içi kartlarda 1H altı zaman dilimleri yalnız kriptoda (Binance) test edilir; BIST/ABD/emtia için dakikalık veri yoktur."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    table = build_report(args.spec_dir, args.results_dir)
    print(f"{len(table)} strateji raporlandi: " + ", ".join(f"{k}={v}" for k, v in table["nihai_durum"].value_counts().items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
