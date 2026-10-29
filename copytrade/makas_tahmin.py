"""Mumlardan makas ve kayma tahmini (Argon A16): Corwin–Schultz (2012) ve Abdi–Ranaldo (2017) makas tahmincileri, yönlü kopya kayması.

Saf bellek içi hesap (ağ ve dosya yok); yalnız ölçü/rapor, kapı ve seçim kararına bağlı değildir. Eşik ve yüzdelikler çağırandan gelir.
**Bozuk mumlar atlanır ve sayılır** (``mum_saglik.mum_kontrol``: bozuk, sıçrama, hacimsiz; ``bosluk`` mumu atlanmaz ama ardışık olmayan çiftler tahmincide kullanılmaz).
Kullanılan eşik: ``kurallar.yaml`` ``mum_sicrama_kat`` / ``mum_medyan_pencere``.

Abdi–Ranaldo: her ardışık çift için ``s² = 4 (ln c_t − η_t)(ln c_t − η_{t+1})``, η = (ln h + ln l)/2; özet makas = ``sqrt(max(ortalama(s²), 0))``
(tek tek karekök almak negatif kovaryansları keserek yanlı büyütürdü).
"""
from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np
import pandas as pd

from copytrade.kurallar import load_rules
from copytrade.mum_saglik import BIR_SAAT_MS, mum_kontrol, ozet as mum_ozet

K2 = 3.0 - 2.0 * math.sqrt(2.0)
ATLANAN_SORUNLAR = ("bozuk", "sicrama", "hacimsiz")      # fiyat bilgisi taşımayan / anormal mumlar tahmincilere girmez


def _temiz(mumlar: list[dict[str, Any]], rules: dict | None = None) -> tuple[pd.DataFrame, dict[str, int]]:
    """Mumları ``mum_kontrol`` ile denetler; ``bozuk``/``sicrama``/``hacimsiz`` olanları atar ve sayar. Dönüş: (zamana göre sıralı OHLC çerçevesi, atlanan sayıları)."""
    if not isinstance(mumlar, list):
        raise TypeError(f"Mumlar bir liste olmalıdır, alınan tip: {type(mumlar).__name__}")
    rules = rules or load_rules()
    rows = [m for m in mumlar if isinstance(m, dict) and m.get("t") is not None]
    not_dict = len(mumlar) - len(rows)
    checked = mum_kontrol(rows, float(rules["mum_sicrama_kat"]), int(rules["mum_medyan_pencere"]))
    counts = mum_ozet(checked)
    ordered = sorted(rows, key=lambda m: m["t"])
    keep = [m for m, r in zip(ordered, checked) if not any(kind in r["sorunlar"] for kind in ATLANAN_SORUNLAR)]
    skipped = {"bozuk": counts["bozuk"] + not_dict, "sicrama": counts["sicrama"], "hacimsiz": counts["hacimsiz"]}
    skipped["toplam"] = len(mumlar) - len(keep)
    frame = pd.DataFrame([{"t": int(m["t"]), "o": float(m["o"]), "h": float(m["h"]), "l": float(m["l"]), "c": float(m["c"])} for m in keep],
                         columns=["t", "o", "h", "l", "c"])
    frame["datetime"] = pd.to_datetime(frame["t"], unit="ms", utc=True)
    return frame, skipped


def _ardisik(frame: pd.DataFrame) -> np.ndarray:
    """Çift (i, i+1) gerçekten ardışık saatlik mumlardan mı (aradaki mum atıldıysa ya da boşluk varsa çift kullanılmaz)."""
    return np.diff(frame["t"].to_numpy(dtype=np.int64)) == BIR_SAAT_MS


def corwin_schultz(mumlar: list[dict[str, Any]], rules: dict | None = None) -> pd.Series:
    """Corwin–Schultz (2012) oran cinsinden makas (ikinci mumun UTC zamanıyla indeksli); negatif tahminler 0'a çekilir (literatür). Geceler arası boşluk düzeltmesi uygulanır."""
    df, _ = _temiz(mumlar, rules)
    empty = pd.Series(dtype=float, index=pd.DatetimeIndex([], name="datetime", tz="UTC"), name="corwin_schultz")
    if len(df) < 2:
        return empty
    ok = _ardisik(df)
    h, l, c = (df[k].to_numpy(dtype=float) for k in ("h", "l", "c"))
    log_hl = np.log(h / l)
    beta = log_hl[:-1] ** 2 + log_hl[1:] ** 2
    c_prev, h_next, l_next = c[:-1], h[1:].copy(), l[1:].copy()
    up = l_next > c_prev
    h_next[up] -= (l_next - c_prev)[up]
    l_next[up] = c_prev[up]
    down = h_next < c_prev
    l_next[down] += (c_prev - h_next)[down]
    h_next[down] = c_prev[down]
    gamma = np.log(np.maximum(h[:-1], h_next) / np.minimum(l[:-1], l_next)) ** 2
    alpha = ((math.sqrt(2.0) - 1.0) * np.sqrt(beta)) / K2 - np.sqrt(gamma / K2)
    spread = np.maximum(2.0 * (np.exp(alpha) - 1.0) / (1.0 + np.exp(alpha)), 0.0)
    return pd.Series(spread[ok], index=df["datetime"].iloc[1:][ok], name="corwin_schultz")


def abdi_ranaldo_s2(mumlar: list[dict[str, Any]], rules: dict | None = None) -> pd.Series:
    """Abdi–Ranaldo (2017) çift başına ``s²`` (işaretli; negatif olabilir). Özet makas için ``abdi_ranaldo_makas``."""
    df, _ = _temiz(mumlar, rules)
    empty = pd.Series(dtype=float, index=pd.DatetimeIndex([], name="datetime", tz="UTC"), name="abdi_ranaldo_s2")
    if len(df) < 2:
        return empty
    ok = _ardisik(df)
    log_c, eta = np.log(df["c"].to_numpy(dtype=float)), 0.5 * (np.log(df["h"].to_numpy(dtype=float)) + np.log(df["l"].to_numpy(dtype=float)))
    s2 = 4.0 * (log_c[:-1] - eta[:-1]) * (log_c[:-1] - eta[1:])
    return pd.Series(s2[ok], index=df["datetime"].iloc[1:][ok], name="abdi_ranaldo_s2")


def abdi_ranaldo_makas(s2: pd.Series | np.ndarray) -> float | None:
    """Özet makas (oran) = ``sqrt(max(ortalama(s²), 0))``; veri yoksa ``None``."""
    values = np.asarray(s2, dtype=float)
    return float(math.sqrt(max(float(values.mean()), 0.0))) if len(values) else None


def coin_makas_ozeti(mumlar: list[dict[str, Any]], yuzdelikler: Sequence[float], rules: dict | None = None) -> dict[str, Any]:
    """Coin için makas özeti (baz puan): Corwin–Schultz medyan/ortalama/yüzdelikler, Abdi–Ranaldo özet makası ve ortalama ``s²``, kullanılan/atlanan mum sayıları."""
    if yuzdelikler is None:
        raise ValueError("yuzdelikler parametresi None olamaz; dışarıdan bir dizi olarak verilmelidir.")
    df, skipped = _temiz(mumlar, rules)
    cs = (corwin_schultz(mumlar, rules) * 1e4).to_numpy(dtype=float)
    s2 = abdi_ranaldo_s2(mumlar, rules).to_numpy(dtype=float)
    out: dict[str, Any] = {"mum_sayisi": len(mumlar), "kullanilan_mum": len(df), "atlanan_mum": skipped}
    out["corwin_schultz"] = ({"medyan_bps": float(np.median(cs)), "ortalama_bps": float(np.mean(cs)),
                              "yuzdelikler_bps": {float(p): float(np.percentile(cs, p)) for p in yuzdelikler}} if len(cs)
                             else {"medyan_bps": None, "ortalama_bps": None, "yuzdelikler_bps": {float(p): None for p in yuzdelikler}})
    makas = abdi_ranaldo_makas(s2)
    out["abdi_ranaldo"] = {"makas_bps": makas * 1e4 if makas is not None else None, "ortalama_s2": float(s2.mean()) if len(s2) else None, "cift_sayisi": int(len(s2))}
    return out


def kopya_kaymasi(trader_dolumlari: list[dict[str, Any]], mumlar: list[dict[str, Any]], gecikme_dk: float | int, rules: dict | None = None) -> dict[str, Any]:
    """Trader dolum fiyatı ↔ gecikme sonrası ilk mumun açılışı: yönlü kayma (bps; + = kopyacı için kötü). Bozuk mumlar atlanır (``atlanan_mum``)."""
    if gecikme_dk is None or isinstance(gecikme_dk, bool) or not isinstance(gecikme_dk, (int, float)):
        raise ValueError("gecikme_dk parametresi sayısal (int/float) olmalı ve dışarıdan verilmelidir.")
    if not isinstance(trader_dolumlari, list):
        raise TypeError("trader_dolumlari bir liste olmalıdır.")
    df, skipped = _temiz(mumlar, rules)
    empty = {"toplam_dolum": len(trader_dolumlari), "eslesen_dolum": 0, "eslesmeyen_dolum": len(trader_dolumlari), "medyan_bps": None, "ortalama_bps": None,
             "yuzde_90_bps": None, "iyi_orani": None, "kotu_orani": None, "notr_orani": None, "atlanan_mum": skipped}
    if not trader_dolumlari or df.empty:
        return empty
    times, opens = df["t"].to_numpy(dtype=np.int64), df["o"].to_numpy(dtype=float)
    delay_ms = int(gecikme_dk * 60.0 * 1000.0)
    slips: list[float] = []
    unmatched = 0
    for index, fill in enumerate(trader_dolumlari):
        if not isinstance(fill, dict):
            raise ValueError(f"{index}. dolum bir sözlük değil: {fill}")
        for field in ("px", "side", "time"):
            if field not in fill:
                raise ValueError(f"{index}. dolumda zorunlu alan eksik: '{field}'")
        side = str(fill["side"]).strip().upper()
        if side not in ("B", "A"):
            raise ValueError(f"{index}. dolumda geçersiz yön: '{side}', yalnızca 'B' veya 'A' kabul edilir.")
        try:
            px = float(fill["px"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"{index}. dolum fiyatı floata çevrilemedi: {error}") from error
        if px <= 0:
            raise ValueError(f"{index}. dolum fiyatı pozitif olmalıdır: {px}")
        try:
            time_ms = int(fill["time"])
        except (TypeError, ValueError):
            try:
                time_ms = int(pd.to_datetime(fill["time"]).timestamp() * 1000)
            except Exception as error:
                raise ValueError(f"{index}. dolum zaman damgası çözümlenemedi: {fill['time']}") from error
        position = int(np.searchsorted(times, time_ms + delay_ms, side="left"))
        if position >= len(times):
            unmatched += 1
            continue
        copy = opens[position]
        slips.append(((copy - px) if side == "B" else (px - copy)) / px * 1e4)
    if not slips:
        return {**empty, "eslesmeyen_dolum": unmatched}
    values = np.array(slips)
    return {"toplam_dolum": len(trader_dolumlari), "eslesen_dolum": len(slips), "eslesmeyen_dolum": unmatched, "medyan_bps": float(np.median(values)),
            "ortalama_bps": float(values.mean()), "yuzde_90_bps": float(np.percentile(values, 90.0)), "iyi_orani": float((values < 0).mean()),
            "kotu_orani": float((values > 0).mean()), "notr_orani": float((values == 0).mean()), "atlanan_mum": skipped}
