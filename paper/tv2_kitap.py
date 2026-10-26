"""TV-2 Pine kitaplarını paper defterine bağlayan ince katman.

Strateji değerlendirmesi doğrudan :mod:`backtests.tv2` veri yolu ve
``engine.tv_emulator`` ile yapılır. Bu modül sinyal/maliyet kuralı yazmaz;
yalnız dondurulmuş kaynağı doğrular, paper başlangıcından önce emirleri
engeller ve emülatör sonucunu paper defteri biçimine uyarlar.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import requests

from backtests import tv2
from engine.pine.yorumlayici import PineStrateji
from engine.tv_emulator import calistir, gercekci

ROOT = Path(__file__).resolve().parents[1]
KAYNAK_DIZINI = Path(__file__).resolve().parent / "tv2_kaynak"
SURUMLER = KAYNAK_DIZINI / "SURUMLER.csv"
YHO_PUB = "PUB;561a4540b4d14f56b4c68cd3cecade24"


class KaynakDogrulamaHatasi(RuntimeError):
    """Dondurulmuş Pine sürümü kullanılamadığında kitap çalıştırılmaz."""


@dataclass(frozen=True)
class Surum:
    kimlik: str
    surum: str
    sha256: str
    dosya: str


@dataclass
class PaperSonuc:
    equity: pd.Series
    marked_equity: float
    fills: list[dict[str, Any]]
    open_positions: list[dict[str, Any]]
    next_orders: list[dict[str, Any]]
    trades: pd.DataFrame
    btc_bakiye: pd.Series | None = None
    btc_usd_kur: pd.Series | None = None


def surum(kimlik: str) -> Surum:
    with SURUMLER.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["kimlik"] == kimlik:
                return Surum(kimlik, row["surum"], row["sha256"], row.get("dosya") or "")
    raise KaynakDogrulamaHatasi(f"{kimlik}: SURUMLER.csv satırı yok")


def _sha_dogrula(kimlik: str, raw: bytes, expected: str) -> str:
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise KaynakDogrulamaHatasi(f"{kimlik}: SHA256 uyuşmuyor ({actual}, beklenen {expected})")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise KaynakDogrulamaHatasi(f"{kimlik}: kaynak UTF-8 değil") from exc


def kaynak(kimlik: str, *, fetch: Callable[[str], Any] | None = None, actions: bool | None = None) -> str:
    """Her çalışmada sabit sürümün kaynağını ve hash'ini doğrula.

    Lisansı belirtilmeyen yho kaynağı repoya hiç yazılmaz. Yerel test, ağ
    çağrısı yerine ``fetch`` vererek sahte kaynak sağlayabilir.
    """
    meta = surum(kimlik)
    if meta.dosya:
        path = ROOT / meta.dosya
        if not path.exists():
            raise KaynakDogrulamaHatasi(f"{kimlik}: dondurulmuş kaynak dosyası yok")
        return _sha_dogrula(kimlik, path.read_bytes(), meta.sha256)
    if kimlik != "yhoK9cH4":
        raise KaynakDogrulamaHatasi(f"{kimlik}: lisanssız kaynak yolu tanımsız")
    if actions is None:
        actions = os.environ.get("GITHUB_ACTIONS") == "true"
    if not actions and fetch is None:
        raise KaynakDogrulamaHatasi("yhoK9cH4: kaynak yalnız Actions'ta pine-facade'den alınır")
    url = "https://pine-facade.tradingview.com/pine-facade/get/" + urllib.parse.quote(YHO_PUB, safe="") + "/1.0?no_4xx=true"
    try:
        response = fetch(url) if fetch is not None else requests.get(url, timeout=30)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        payload = response.json() if hasattr(response, "json") else json.loads(response)
        text = payload.get("source")
    except Exception as exc:  # facade failures must stop this book, never substitute a source
        raise KaynakDogrulamaHatasi(f"yhoK9cH4: pine-facade kaynak alınamadı ({type(exc).__name__})") from exc
    if not isinstance(text, str):
        raise KaynakDogrulamaHatasi("yhoK9cH4: pine-facade source alanı yok")
    return _sha_dogrula(kimlik, text.encode("utf-8"), meta.sha256)


def isinma_bari(kaynak_metni: str) -> int:
    """Kaynakta bildirilen geçmiş pencere uzunluklarının güvenli üst sınırı."""
    numbers = [int(value) for value in re.findall(r"(?:length|len|period|leftBars|rightBars)\s*=\s*(?:input\w*\()?\s*(\d+)", kaynak_metni, re.I)]
    return max(numbers, default=1) + 2


class _BaslangicKapisi:
    """Gösterge ısınır, fakat paper başlangıcından önce emir üretemez."""

    def __init__(self, inner: PineStrateji, start: pd.Timestamp, stop: pd.Timestamp | None = None) -> None:
        self.inner, self.start, self.stop, self.AYARLAR = inner, start, stop, inner.AYARLAR

    def hazirla(self, df: pd.DataFrame) -> dict:
        return self.inner.hazirla(df)

    def bar(self, ctx: Any, i: int, values: dict) -> None:
        self._calistir(ctx, i, lambda: self.inner.bar(ctx, i, values))

    def ara(self, ctx: Any, i: int) -> None:
        self._calistir(ctx, i, lambda: self.inner.ara(ctx, i))

    def _calistir(self, ctx: Any, i: int, call: Callable[[], None]) -> None:
        if ctx.df.index[i] < self.start:
            return
        if self.stop is None or ctx.df.index[i] < self.stop:
            call()
            return
        # MDD kapısı yalnız yeni risk açılmasını durdurur. Pine'ın exit/close
        # çağrıları ve daha önceki koruyucu emirleri çalışmaya devam eder.
        entry, order = ctx.entry, ctx.order
        ctx.entry = lambda *_args, **_kwargs: None
        ctx.order = lambda *_args, **_kwargs: None
        try:
            call()
        finally:
            ctx.entry, ctx.order = entry, order


def _closed(frame: pd.DataFrame, tf: str) -> pd.DataFrame:
    return tv2._kapanmis(frame, tv2.dakika(tf))  # TV-2'nin kendi kapanmış-bar kuralı


def _paper_sonuc(sonuc: Any, frame: pd.DataFrame, *, sembol: str,
                 btc_kur: pd.Series | None = None) -> PaperSonuc:
    fills = [{**item, "sembol": sembol, "stop": np.nan} for item in sonuc.dolumlar]
    open_positions = [{"sembol": sembol, "giris_tarihi": item["giris_tarihi"], "giris_fiyati": item["giris_fiyati"],
                       "adet": item["adet"], "stop": np.nan, "hedef": np.nan,
                       "son_kapanis": float(frame.loc[frame.index[-1], "close"]), "yon": item["yon"]}
                      for item in sonuc.acik_islemler]
    orders = []
    for item in sonuc.bekleyen_emirler:
        tip = "giris" if item["tur"] in {"giris", "emir"} else "cikis"
        signal = frame.index[item["verildi"]]
        orders.append({"sinyal_tarihi": signal, "sembol": sembol, "tip": tip,
                       "referans_fiyat": float(frame.loc[signal, "close"]), "adet": item["adet"],
                       "stop": item["stop"], "hedef": item["limit"]})
    trades = sonuc.islemler.rename(columns={"exit_id": "exit_reason", "net": "net_pnl"}).copy()
    if "exit_reason" not in trades:
        trades = pd.DataFrame(columns=["exit_reason", "net_pnl"])
    equity = sonuc.ozkaynak.astype(float)
    btc_bakiye = None
    if btc_kur is not None:
        btc_kur = btc_kur.reindex(equity.index).ffill()
        btc_bakiye = equity
        equity = btc_bakiye * btc_kur
    return PaperSonuc(equity=equity, marked_equity=float(equity.iloc[-1]), fills=fills, open_positions=open_positions,
                       next_orders=orders, trades=trades, btc_bakiye=btc_bakiye, btc_usd_kur=btc_kur)


def calistir_kitap(satir: Any, baslangic: pd.Timestamp, sermaye_usd: float, *,
                   veri_al: Callable[[str, str], tuple[pd.DataFrame | None, str]] | None = None,
                   kaynak_al: Callable[[str], str] | None = None,
                   maske_tarihi: pd.Timestamp | None = None) -> tuple[PaperSonuc, pd.Timestamp]:
    """Bir TV-2 satırını TV-2 veri/yorumlayıcı/emülatör yolu ile çalıştır."""
    meta = surum(satir.id)
    source = (kaynak_al or kaynak)(satir.id)
    modul0, info = tv2.strateji(satir.id)
    del modul0
    sembol, tf = str(info["sembol"]), str(info["tf"])
    get = veri_al or tv2.veri
    frame, note = get(sembol, tf)
    if frame is None or frame.empty:
        raise KaynakDogrulamaHatasi(f"{satir.id}: {note}")
    frame = _closed(frame, tf)
    if len(frame) < isinma_bari(source) + 2:
        raise KaynakDogrulamaHatasi(f"{satir.id}: ısınma için yetersiz kapanmış bar ({len(frame)})")
    start = pd.Timestamp(baslangic)
    start = start.tz_localize("UTC") if start.tzinfo is None else start.tz_convert("UTC")
    if frame.index[-1] < start:
        raise KaynakDogrulamaHatasi(f"{satir.id}: başlangıçtan sonra kapanmış bar yok")
    kripto = sembol.upper().startswith("BINANCE:")
    btc_kur = None
    initial = sermaye_usd
    if satir.id == "wcegMOXj":
        btc, btc_note = get("BINANCE:BTCUSDT", tf)
        if btc is None or btc.empty:
            raise KaynakDogrulamaHatasi(f"wcegMOXj: BTCUSD dönüşüm verisi yok ({btc_note})")
        btc = _closed(btc, tf).reindex(frame.index)
        btc_kur = btc["close"].astype(float)
        if btc_kur.loc[start:].dropna().empty:
            raise KaynakDogrulamaHatasi("wcegMOXj: başlangıç için aynı zaman damgalı BTCUSDT kapanışı yok")
        rate0 = float(btc_kur.loc[btc_kur.index >= start].dropna().iloc[0])
        initial = sermaye_usd / rate0
    modul = PineStrateji(source, sembol=sembol, tf=tf, kimlik=satir.id, surum=int(float(meta.surum)))
    gated = _BaslangicKapisi(modul, start, maske_tarihi)
    sonuc = calistir(gated, frame, initial_capital=initial, **gercekci(modul.AYARLAR, kripto))
    return _paper_sonuc(sonuc, frame, sembol=sembol, btc_kur=btc_kur), frame.index[-1]
