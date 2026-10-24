#!/usr/bin/env python3
"""U1 funnel (docs/GOREV_U1.md, U1d): every pre-registered variant of ``backtests/u1.py`` through the Faz 1 gates.

No new statistics are written here; the stages reuse the Faz 1 code:

* **Stage 2a, IS:** pooled (14 coins) random-entry null test, ``asama2a.null_distribution`` (the pooled trade count and
  holding time of the real book are matched). PF **and** mean R must beat the null's 95th percentile
  (borderline p 0.03-0.10 is rerun with ``--tekrar-yuksek``).
* **Stage 2b, OOS:** 1x/2x/3x cost, +1 bar delayed entry, ``asama2b.block_bootstrap`` MDD95 and
  ``asama2b.deflated_sharpe_ratio`` (14 trials, plus the source's own trial count for the Hat 0 cards).
* **Sibling report:** ``scripts/kardes_rapor.py`` on the OOS pooled trade list.
* **Decision:** Gecti / Kosullu / Reddedildi, gates exactly as GOREV_U1 section 4 and ``asama2b.decide``.

Memory: one variant at a time, the archive of one timeframe is held while its variants run and dropped before the next
(``--tf`` selects timeframes); null workers are capped by free memory (``tarama.bellek_isci``).

    python backtests/u1_huni.py --tf 1H,15m --tekrar 200 --isci 4 --veri-kok data
"""

from __future__ import annotations

import argparse
import gc
import logging
import math
import os
import sys
import zlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtests import asama2a, asama2b, tarama, u1  # noqa: E402
from engine.portfolio import calculate_metrics  # noqa: E402
from scripts import kardes_rapor  # noqa: E402

LOG = logging.getLogger("u1_huni")
BASE_TRIALS = 14  # GOREV_U1 section 0.2
MIN_SIBLING_RATIO = 0.60  # section 4.1
MAX_SYMBOL_SHARE = 0.35  # section 4.3
MIN_OOS_TRADES = 30  # asama2b.decide
MIN_PF_2X = 1.2  # asama2b.decide (Faz 1 funnel: 2x cost)
ANNUALIZATION = 365  # bootstrap/DSR run on one equity close per UTC day, crypto trades every day

COLUMNS = [
    "varyant", "kart", "tf", "is_islem", "is_PF", "is_ortR", "null_tekrar", "null_pf_p95", "null_ortr_p95", "p_pf", "p_ortr",
    "null_gecti", "oos_islem", "oos_ortR", "oos_PF_1x", "oos_PF_2x", "oos_PF_3x", "oos_net_1x", "oos_net_2x", "oos_net_3x",
    "net_gecikme", "mdd_p95", "cagr_p05", "dsr", "dsr_deneme", "kardes_gecen", "kardes_oran", "havuz_pf", "havuz_pf_ci90_alt",
    "havuz_pf_ci90_ust", "en_buyuk_kar_payi", "en_buyuk_kar_sembol", "en_iyi_ay", "en_iyi_ay_haric_pf", "karar", "neden",
]


def trials_for(card: dict[str, Any]) -> int:
    """14 pre-registered trials; the Hat 0 cards add the trial count of their source (T8-07: 256)."""
    extra = int(card.get("deneme_sayisi_kaynakta") or 0) if card["id"] in u1.HAT0 else 0
    return BASE_TRIALS + extra


def decide(row: dict[str, Any]) -> tuple[str, str]:
    """Karar from GOREV_U1 section 4 and the Faz 1 gate order of ``asama2b.decide`` (no new thresholds).

    Reddedildi: a Faz 1 funnel gate fails (null, OOS mean R, 2x PF < 1.2, 3x net <= 0, +1 bar net <= 0, bootstrap MDD95 > 15 %).
    The sibling ratio (section 4.1) is a hard gate too (leader decision, PR #152).
    Kosullu: the funnel passes but symbol share or best month (section 4.3/4.4) fails, or OOS has < 30 trades.
    Gecti: everything passes.
    """
    rejected, conditional = [], []
    if not row.get("null_gecti", False):
        rejected.append("null")
    if row.get("oos_islem", 0) >= MIN_OOS_TRADES and not row.get("oos_ortR", float("nan")) > 0:
        rejected.append("OOS ortR<=0")
    if not row.get("oos_PF_2x", float("nan")) >= MIN_PF_2X:
        rejected.append("2x PF<1.2")
    if not row.get("oos_net_3x", float("nan")) > 0:
        rejected.append("3x net<=0")
    if not row.get("net_gecikme", float("nan")) > 0:
        rejected.append("+1 bar net<=0")
    if not row.get("mdd_p95", float("nan")) <= asama2b.RISK_BUDGET:
        rejected.append("bootstrap MDD95>%15")
    if row.get("oos_islem", 0) < MIN_OOS_TRADES:
        conditional.append("OOS ornek<30")
    if not row.get("kardes_oran", float("nan")) >= MIN_SIBLING_RATIO:  # lider karari: genelleme ana kanit, sert kapi
        rejected.append(f"kardes PF>1,1 orani<%{MIN_SIBLING_RATIO * 100:.0f} ({row.get('kardes_gecen', '?')})")
    if not row.get("en_buyuk_kar_payi", float("nan")) <= MAX_SYMBOL_SHARE:
        conditional.append(f"tek coin kar payi>%{MAX_SYMBOL_SHARE * 100:.0f}")
    if not row.get("en_iyi_ay_haric_pf", float("nan")) > 1.0:
        conditional.append("en iyi ay haric PF<=1")
    if rejected:
        return "Reddedildi", ", ".join(rejected)
    if conditional:
        return "Kosullu", ", ".join(conditional)
    return "Gecti", "bolum 4 olcutlerinin hepsi gecti"


def _daily_returns(result) -> pd.Series:
    return asama2b._validation_returns(result, daily_equity=True)  # noqa: SLF001 - the Faz 1 definition of validation returns


def stage_2a(variant: str, card: dict[str, Any], data: dict[str, pd.DataFrame], reps: int, reps_high: int, workers: int) -> dict[str, Any]:
    """IS pooled null test; returns the 2a columns."""
    start, end = u1.PERIODS["IS"]
    prepared = tarama.prepare(card, data, u1.MARKET, start=start, end=end, kilit=True)
    real = prepared.run(1.0, trusted_inputs=True)
    pf, ortr, count = asama2a.trade_stats(real.trades)
    out: dict[str, Any] = {"is_islem": count, "is_PF": pf, "is_ortR": ortr}
    if count < 5:
        return {**out, "null_gecti": False, "neden_2a": "IS islem<5 (null testi yapilamadi)"}
    seed = asama2a.BASE_SEED ^ zlib.crc32(variant.encode())
    workers = tarama.bellek_isci(workers, data, is_basina=asama2a.NULL_WORKER_DATA_FACTOR)
    null = asama2a.null_distribution(prepared, real.trades, reps, seed, workers)
    p_pf, p_ortr = asama2a.p_value(pf, null["pf"]), asama2a.p_value(ortr, null["ortr"])
    used = reps
    if asama2a.BORDERLINE_P[0] <= max(p_pf, p_ortr) <= asama2a.BORDERLINE_P[1]:
        used = reps_high
        null = asama2a.null_distribution(prepared, real.trades, reps_high, seed + 1, workers)
        p_pf, p_ortr = asama2a.p_value(pf, null["pf"]), asama2a.p_value(ortr, null["ortr"])
    pf95 = float(np.nanpercentile(null["pf"], asama2a.PASS_PERCENTILE))
    ortr95 = float(np.nanpercentile(null["ortr"], asama2a.PASS_PERCENTILE))
    prepared.runtime_cache.clear()
    return {**out, "null_tekrar": used, "null_pf_p95": pf95, "null_ortr_p95": ortr95, "p_pf": p_pf, "p_ortr": p_ortr,
            "null_gecti": bool(pf > pf95 and ortr > ortr95)}


def stage_2b(variant: str, card: dict[str, Any], data: dict[str, pd.DataFrame], boot_reps: int, results_dir: Path) -> dict[str, Any]:
    """OOS: cost stress, +1 bar delay, bootstrap MDD95, DSR and the sibling report of the 1x trade list."""
    start, end = u1.PERIODS["OOS"]
    prepared = tarama.prepare(card, data, u1.MARKET, start=start, end=end, kilit=True)
    annual = tarama.annualization_for(card["tf"], u1.MARKET)
    runs = {mult: prepared.run(mult, trusted_inputs=True) for mult in u1.COSTS}
    delayed = prepared.run(1.0, trusted_inputs=True, extra_delay_bars=1)
    prepared.runtime_cache.clear()
    metrics = {mult: calculate_metrics(result, annualization=annual) for mult, result in runs.items()}
    out: dict[str, Any] = {
        "oos_islem": metrics[1.0]["islem"], "oos_ortR": metrics[1.0]["ortalama_r"],
        **{f"oos_PF_{int(m)}x": metrics[m]["pf"] for m in u1.COSTS}, **{f"oos_net_{int(m)}x": metrics[m]["getiri"] for m in u1.COSTS},
        "net_gecikme": calculate_metrics(delayed, annualization=annual)["getiri"],
    }
    returns = _daily_returns(runs[1.0])
    trials = trials_for(card)
    out["dsr_deneme"] = trials
    if len(returns) >= 3:
        boot = asama2b.block_bootstrap(returns, repetitions=boot_reps, seed=asama2a.BASE_SEED ^ zlib.crc32(variant.encode()), annualization=ANNUALIZATION)
        out.update(mdd_p95=boot["mdd_p95"], cagr_p05=boot["cagr_p05"], dsr=asama2b.deflated_sharpe_ratio(returns, trials))
    else:
        out.update(mdd_p95=float("nan"), cagr_p05=float("nan"), dsr=float("nan"))

    trades = runs[1.0].trades
    safe = variant.replace("[", "_").replace("]", "").replace("=", "-").replace(":", "")
    csv = results_dir / f"islemler_{safe}_OOS.csv"
    trades.to_csv(csv, index=False)  # the same file kardes_rapor.py reads directly
    detail, summary = kardes_rapor.summarize_trades(pd.read_csv(csv), repetitions=boot_reps, seed=asama2a.BASE_SEED)
    kardes_rapor.write_report(detail, summary, results_dir / f"kardes_{safe}.csv", results_dir / f"kardes_{safe}.md")
    out.update(
        kardes_gecen=summary["sibling_pf_gt_1_1_count"], kardes_oran=summary["sibling_pf_gt_1_1_ratio"],
        havuz_pf=summary["pooled_profit_factor"], havuz_pf_ci90_alt=summary["pooled_pf_ci90_low"],
        havuz_pf_ci90_ust=summary["pooled_pf_ci90_high"], en_buyuk_kar_payi=summary["largest_profit_share"],
        en_buyuk_kar_sembol=summary["largest_profit_share_symbol"], en_iyi_ay=summary["best_month_removed"],
        en_iyi_ay_haric_pf=summary["best_month_removed_profit_factor"],
    )
    return out


def evaluate_variant(variant: str, card: dict[str, Any], data: dict[str, pd.DataFrame], *, reps: int, reps_high: int, workers: int,
                     boot_reps: int, results_dir: Path) -> dict[str, Any]:
    row: dict[str, Any] = {column: float("nan") for column in COLUMNS}
    row.update(varyant=variant, kart=card["id"], tf=card["tf"])
    try:
        two_a = stage_2a(variant, card, data, reps, reps_high, workers)
        note = two_a.pop("neden_2a", "")
        row.update(two_a)
        row.update(stage_2b(variant, card, data, boot_reps, results_dir))
        row["karar"], row["neden"] = decide(row)
        if note:
            row["neden"] = f"{note}; {row['neden']}"
    except PermissionError:
        raise  # the lock is never swallowed
    except Exception as exc:  # noqa: BLE001 - one broken variant must not stop the run
        row.update(karar="Hata", neden=f"{type(exc).__name__}: {exc}"[:200])
    gc.collect()
    return row


def write_outputs(table: pd.DataFrame, results_dir: Path) -> None:
    table.to_csv(results_dir / "huni_ozet.csv", index=False)
    counts = table["karar"].value_counts().to_dict()
    lines = ["# U1 huni ozeti", "", "IS: null testi (havuz, 14 coin); OOS: maliyet, +1 bar gecikme, bootstrap MDD95, DSR, kardes raporu. "
             "Kilitli donem acilmadi.", "", "Karar sayilari: " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())), "",
             "| varyant | tf | IS islem | null | OOS islem | OOS PF 1x/2x/3x | +1 bar net | MDD95 | DSR | kardes | en buyuk pay | en iyi ay haric PF | karar | neden |",
             "|---|---|---:|---|---:|---|---:|---:|---:|---|---:|---:|---|---|"]

    def f(value: Any, digits: int = 2) -> str:
        return "-" if value is None or (isinstance(value, float) and math.isnan(value)) else f"{value:.{digits}f}"

    for r in table.to_dict("records"):
        lines.append(
            f"| {r['varyant']} | {r['tf']} | {f(r['is_islem'], 0)} | {r['null_gecti']} | {f(r['oos_islem'], 0)} | "
            f"{f(r['oos_PF_1x'])}/{f(r['oos_PF_2x'])}/{f(r['oos_PF_3x'])} | {f(r['net_gecikme'], 3)} | {f(r['mdd_p95'], 3)} | {f(r['dsr'], 3)} | "
            f"{r['kardes_gecen']} | {f(r['en_buyuk_kar_payi'])} | {f(r['en_iyi_ay_haric_pf'])} | {r['karar']} | {r['neden']} |"
        )
    (results_dir / "huni_ozet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--hat", default="0,2")
    parser.add_argument("--kart-ids", default="", help="comma separated card ids (default: all of the chosen hats)")
    parser.add_argument("--tf", default="", help="only these timeframes, e.g. 1H,15m (default: all; 5m last because of its memory)")
    parser.add_argument("--tekrar", type=int, default=200, help="null repetitions")
    parser.add_argument("--tekrar-yuksek", type=int, default=1000, help="null repetitions for borderline p")
    parser.add_argument("--bootstrap-tekrar", type=int, default=1000)
    parser.add_argument("--isci", type=int, default=0, help="null worker processes (0 = CPU count, capped by free memory)")
    parser.add_argument("--veri-kok", type=Path, default=ROOT / "data")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results" / "u1")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    items = u1.all_variants(tuple(int(h) for h in args.hat.split(",")))
    keep = {c for c in args.kart_ids.split(",") if c}
    if keep:
        items = [(v, c) for v, c in items if c["id"] in keep]
    if args.tf:
        wanted = {t.strip() for t in args.tf.split(",")}
        items = [(v, c) for v, c in items if c["tf"] in wanted]
    order = {"1H": 0, "15m": 1, "5m": 2}
    items.sort(key=lambda item: order.get(item[1]["tf"], 9))  # one archive in memory at a time, 5m last
    workers = args.isci or os.cpu_count() or 1
    args.results_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    loaded_tf, data = None, {}
    for variant, card in items:
        if card["tf"] != loaded_tf:
            data, loaded_tf = {}, card["tf"]
            gc.collect()
            data = u1.load_data(args.veri_kok, loaded_tf, u1.CORE + u1.SIBLINGS)
        if not data:
            LOG.warning("%s: %s verisi yok", variant, loaded_tf)
            continue
        row = evaluate_variant(variant, card, data, reps=args.tekrar, reps_high=args.tekrar_yuksek, workers=workers,
                               boot_reps=args.bootstrap_tekrar, results_dir=args.results_dir)
        LOG.info("%s: %s (%s)", variant, row["karar"], row["neden"])
        rows.append(row)
    if rows:
        write_outputs(pd.DataFrame(rows, columns=COLUMNS), args.results_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
