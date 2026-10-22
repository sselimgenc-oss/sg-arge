#!/usr/bin/env python3
"""T13: assemble existing validation outputs into one final strategy report.

This module deliberately performs no backtest or statistical calculation.  It
only applies the documented outcome precedence to CSV/YAML inputs that already
exist, and stays useful while later-stage files have not been generated yet.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_COLUMNS = ["id", "ad", "kaynak", "tarz", "tf", "nihai_durum", "alt_neden", "en_iyi_piyasa", "piyasa_ayrintisi"]
STATUS_RANK = {"Gecti": 3, "Kosullu": 2, "Reddedildi": 1, "Dogrulanamaz": 0}
MISSING_STAGE = "asama 2b henuz yok"


def _read_csv(path: Path) -> pd.DataFrame:
    """Read optional files with a stable empty table when they are not present."""
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _clean(value: object) -> str:
    return "" if value is None or pd.isna(value) else str(value).strip()


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


def _best(rows: pd.DataFrame, status_column: str, reason_column: str = "neden") -> pd.Series | None:
    if rows.empty:
        return None
    ranked = rows.copy()
    ranked["_rank"] = ranked[status_column].map(STATUS_RANK).fillna(-1)
    ranked["_reason"] = ranked[reason_column].fillna("").astype(str) if reason_column in ranked else ""
    return ranked.sort_values(["_rank", "_reason"], ascending=[False, True], kind="stable").iloc[0]


def _underlying_reason(card: dict[str, Any], yeniden: set[str], tarama_rows: pd.DataFrame) -> str:
    identifier = str(card.get("id", ""))
    if identifier in yeniden:
        return "kaynak erisilemedi"
    status = _clean(card.get("spec_durumu"))
    if status in {"kapsam_disi", "sadece_short"}:
        return status.replace("_", " ")
    if status in {"gizli", "ihtiyari", "eksik"}:
        return status
    if card.get("ozel_kod"):
        return "ozel kod" + (f": {_clean(card.get('ozel_kod_nedeni'))}" if _clean(card.get("ozel_kod_nedeni")) else "")
    reasons = " ".join(tarama_rows.get("neden", pd.Series(dtype=str)).fillna("").astype(str)).lower()
    if "dakikalik veri yok" in reasons:
        return "dakikalik veri yok"
    if "motor_destegi_yok" in reasons:
        return "motor destegi yok"
    if "piyasa_ozgu" in reasons:
        return "piyasa ozgu"
    if "orneklem" in reasons or "islem<30" in reasons:
        return "orneklem"
    return "henuz yok"


def _market_detail(identifier: str, tarama: pd.DataFrame, asama2a: pd.DataFrame, asama2b: pd.DataFrame, codex: pd.DataFrame) -> str:
    detail: list[dict[str, str]] = []
    for stage, table, status_col in (("tarama", tarama, "durum"), ("asama2a", asama2a, "karar"), ("asama2b", asama2b, "karar")):
        if table.empty or "id" not in table:
            continue
        for row in table[table["id"].astype(str) == identifier].itertuples(index=False):
            values = row._asdict()
            detail.append({"asama": stage, "piyasa": _clean(values.get("piyasa")), "durum": _clean(values.get(status_col)), "neden": _clean(values.get("neden"))})
    if identifier.startswith("C") and not codex.empty and "satir" in codex:
        for row in codex[codex["satir"].astype(str) == identifier].itertuples(index=False):
            values = row._asdict()
            detail.append({"asama": "replikasyon", "piyasa": _clean(values.get("piyasa")), "durum": _clean(values.get("durum")), "neden": _clean(values.get("neden"))})
    return json.dumps(detail, ensure_ascii=False, separators=(",", ":"))


def _verdict(identifier: str, card: dict[str, Any], yeniden: set[str], tarama: pd.DataFrame, asama2a: pd.DataFrame, asama2b: pd.DataFrame) -> tuple[str, str, str]:
    b_rows = asama2b[asama2b["id"].astype(str) == identifier] if not asama2b.empty and "id" in asama2b else pd.DataFrame()
    b = _best(b_rows, "karar")
    if b is not None and _clean(b["karar"]) in STATUS_RANK:
        return _clean(b["karar"]), _clean(b.get("neden")), _clean(b.get("piyasa"))

    a_rows = asama2a[asama2a["id"].astype(str) == identifier] if not asama2a.empty and "id" in asama2a else pd.DataFrame()
    a_pass = a_rows[a_rows["karar"].astype(str) == "Gecti (null)"] if not a_rows.empty and "karar" in a_rows else pd.DataFrame()
    if not a_pass.empty:
        best = a_pass.iloc[0]
        return "Dogrulanamaz", MISSING_STAGE, _clean(best.get("piyasa"))
    a_rejected = a_rows[a_rows["karar"].astype(str).str.startswith("Reddedildi")] if not a_rows.empty and "karar" in a_rows else pd.DataFrame()
    if not a_rejected.empty:
        best = a_rejected.iloc[0]
        suffix = "BIST USD" if "USD" in _clean(best.get("karar")) else "piyasa betasi"
        return "Reddedildi", f"{suffix}: {_clean(best.get('neden'))}".rstrip(": "), _clean(best.get("piyasa"))

    t_rows = tarama[tarama["id"].astype(str) == identifier] if not tarama.empty and "id" in tarama else pd.DataFrame()
    candidates = t_rows[t_rows["asama2_aday"].map(_bool)] if not t_rows.empty and "asama2_aday" in t_rows else pd.DataFrame()
    if not candidates.empty:
        best = candidates.iloc[0]
        return "Dogrulanamaz", "asama 2a henuz yok", _clean(best.get("piyasa"))
    calculated = t_rows[t_rows["durum"].astype(str) == "Hesaplandi"] if not t_rows.empty and "durum" in t_rows else pd.DataFrame()
    if not calculated.empty:
        best = calculated.iloc[0]
        return "Reddedildi", f"asama 1: {_clean(best.get('neden'))}", _clean(best.get("piyasa"))

    reason = _underlying_reason(card, yeniden, t_rows)
    if reason in {"kapsam disi", "sadece short"}:
        return "Dogrulanamaz", reason, ""
    market = _clean(t_rows.iloc[0].get("piyasa")) if not t_rows.empty else ""
    return "Dogrulanamaz", reason, market


def build_report(spec_dir: Path, results_dir: Path) -> pd.DataFrame:
    """Build, write, and return the deterministic final report table."""
    index = _read_csv(spec_dir / "INDEKS.csv")
    yeniden_frame = _read_csv(spec_dir / "YENIDEN.csv")
    yeniden = set(yeniden_frame.get("id", pd.Series(dtype=str)).astype(str))
    cards = _yaml_cards(spec_dir)
    tarama, asama2a, asama2b, codex = (_read_csv(results_dir / name) for name in ("tarama.csv", "asama2a.csv", "asama2b.csv", "codex21.csv"))
    ids = set(index.get("id", pd.Series(dtype=str)).astype(str)) | set(cards) | {f"C{i:02d}" for i in range(1, 22)}
    rows = []
    for identifier in sorted(ids):
        metadata = _metadata(index, cards, identifier)
        verdict, reason, market = _verdict(identifier, cards.get(identifier, {}), yeniden, tarama, asama2a, asama2b)
        metadata.update(nihai_durum=verdict, alt_neden=reason, en_iyi_piyasa=market,
                        piyasa_ayrintisi=_market_detail(identifier, tarama, asama2a, asama2b, codex))
        rows.append(metadata)
    table = pd.DataFrame(rows).reindex(columns=OUTPUT_COLUMNS)
    table["_rank"] = table["nihai_durum"].map(STATUS_RANK)
    table = table.sort_values(["_rank", "id"], ascending=[False, True], kind="stable").drop(columns="_rank").reset_index(drop=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(results_dir / "sonuc.csv", index=False)
    _write_markdown(table, results_dir / "SONUC.md", [
        name for name in ("tarama.csv", "asama2a.csv", "asama2b.csv", "codex21.csv") if not (results_dir / name).exists()
    ])
    return table


def _write_markdown(table: pd.DataFrame, path: Path, missing: list[str]) -> None:
    counts = table["nihai_durum"].value_counts().to_dict()
    lines = ["# Nihai strateji sonucu (T13)", "", "Bu rapor mevcut dosyaları birleştirir; yeni backtest veya istatistik hesaplamaz.", "",
             "## Ozet", "", f"Toplam: {len(table)} | " + " | ".join(f"{key}: {value}" for key, value in sorted(counts.items())), ""]
    if missing:
        lines += [f"> Henuz yok: {', '.join(missing)}. Bu nedenle ilgili asama bekleyen satirlar `Dogrulanamaz` gorunur.", ""]
    for heading, statuses in (("Gecti ve Kosullu", ("Gecti", "Kosullu")), ("Reddedilenler", ("Reddedildi",)), ("Dogrulanamaz", ("Dogrulanamaz",))):
        subset = table[table["nihai_durum"].isin(statuses)]
        lines += [f"## {heading}", ""]
        if subset.empty:
            lines += ["- Yok.", ""]
            continue
        if heading == "Gecti ve Kosullu":
            groups = [("", subset)]
        else:
            grouped = subset.assign(_neden_grubu=subset["alt_neden"].fillna("").astype(str).str.split(":").str[0])
            groups = list(grouped.groupby("_neden_grubu", dropna=False, sort=True))
        for reason, group in groups:
            if reason:
                lines += [f"### {reason} ({len(group)})", ""]
            lines += ["| ID | Strateji | Durum | En iyi piyasa | Ayrinti |", "|---|---|---|---|---|"]
            for row in group.itertuples():
                lines.append(f"| {row.id} | {row.ad} | {row.nihai_durum} | {row.en_iyi_piyasa or '-'} | {row.alt_neden or '-'} |")
            lines.append("")
    lines += ["## Yontem ve uyarilar", "", "- Piyasa bazli kayitlarda en iyi nihai durum strateji satirina tasinir; tum ayrintilar sonuc.csv icindeki piyasa_ayrintisi JSON alanindadir.",
              "- BIST USD donusumu ve rastgele giris/null bulgulari T6a sonucundan gelir; ayrintili degerlendirme: tartisma/008.",
              "- BIST ve ABD evrenlerinde survivorship yanliligi nedeniyle olumlu sonuc canli kanit degildir."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=ROOT / "docs" / "spec")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    table = build_report(args.spec_dir, args.results_dir)
    print(f"{len(table)} strateji raporlandi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
