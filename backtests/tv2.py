"""TV-2 koşucusu: `strategies/tv2/<id>.py` modüllerini yazarın sembolü ve zaman diliminde koşar (docs/TEST_YAPISI.md Adım 0-2).

Her modül için iki sonuç: yazar (strategy() ayarları) ve uygulanabilir (gerçekçi maliyet). Sınama dönemi, test edilen kod
sürümünün tarihinden (`arastirma/tv2_surumler.csv`) sonrasıdır. Çıktı: `results/tv2/sonuclar.csv` (id başına bir satır,
yeniden koşuda güncellenir) ve `results/tv2/getiriler/<id>.csv` (uygulanabilir sonucun günlük net getirisi).

    python -m backtests.tv2 [id ...]      # id verilmezse bütün modüller
"""

from __future__ import annotations

import argparse
import importlib
import pkgutil
import re
from pathlib import Path

import numpy as np
import pandas as pd

from data.fetch import Asset, fetch_binance
from engine.tv_emulator import Sonuc, calistir, gercekci, nedensellik

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "tv2"
OUT = ROOT / "results" / "tv2"
SURUMLER = ROOT / "arastirma" / "tv2_surumler.csv"

KRIPTO_BORSALARI = {"BINANCE", "BYBIT", "OKX", "COINBASE", "BITSTAMP", "KUCOIN", "BITGET", "MEXC", "KRAKEN", "BINANCEUS",
                    "BITFINEX", "GATEIO", "PHEMEX", "CRYPTO", "BLACKBULL"}
BINANCE_ARALIK = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480,
                  "12h": 720, "1d": 1440, "3d": 4320, "1w": 10080}
YFINANCE = {"SPX": "^GSPC", "SPX500": "^GSPC", "US500": "^GSPC", "SPY": "SPY", "NDX": "^NDX", "NAS100": "^NDX", "US100": "^NDX",
            "QQQ": "QQQ", "DJI": "^DJI", "US30": "^DJI", "XAUUSD": "GC=F", "GOLD": "GC=F", "XAGUSD": "SI=F", "USOIL": "CL=F",
            "WTI": "CL=F", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "DAX": "^GDAXI",
            "DE40": "^GDAXI", "GER40": "^GDAXI"}
KAPI_HAFTA = 10


def dakika(tf: str) -> int:
    """TradingView aralığı → dakika ('60', '240', '1D', 'D', '1W', '45', '4H', '3D')."""
    tf = str(tf).strip().upper()
    m = re.fullmatch(r"(\d*)([SDWMH]?)", tf)
    if not m:
        raise ValueError(f"aralık okunamadı: {tf}")
    n, birim = int(m.group(1) or 1), m.group(2)
    return n * {"": 1, "H": 60, "D": 1440, "W": 10080, "M": 43200}.get(birim, 1)


def _binance_sembol(sembol: str) -> str:
    s = sembol.split(":")[-1].replace(".P", "").replace("PERP", "")
    return s[:-3] + "USDT" if s.endswith("USD") and not s.endswith("USDT") else s


def veri(sembol: str, tf: str) -> tuple[pd.DataFrame | None, str]:
    """(OHLC, kaynak notu). Veri yoksa (None, neden). Kapanmamış son bar atılır."""
    borsa, _, ad = sembol.upper().partition(":")
    dk = dakika(tf)
    if borsa in KRIPTO_BORSALARI or ad.endswith(("USDT", "USDT.P", "USDC")):
        bsym = _binance_sembol(sembol.upper())
        taban = max((v for v in BINANCE_ARALIK.values() if dk % v == 0 and v <= dk), default=None)
        if taban is None:
            return None, f"veri_yok: aralık {tf}"
        aralik = next(k for k, v in BINANCE_ARALIK.items() if v == taban)
        yol = CACHE / f"{bsym}_{aralik}.parquet"
        if yol.exists():
            df = pd.read_parquet(yol)
        else:
            df = fetch_binance(Asset(bsym, "KRIPTO", "binance"), aralik)
            if df.empty:
                return None, f"veri_yok: Binance {bsym}"
            CACHE.mkdir(parents=True, exist_ok=True)
            df.to_parquet(yol)
        if taban != dk:
            df = _yeniden_ornekle(df, dk)
        return _kapanmis(df, dk), f"Binance {bsym} {aralik}" + ("" if taban == dk else f" → {tf}")
    if ad.split(".")[0] in YFINANCE and dk >= 1440:
        import yfinance as yf
        kod = YFINANCE[ad.split(".")[0]]
        df = yf.download(kod, period="max", interval="1d" if dk < 10080 else "1wk", auto_adjust=False, progress=False)
        if df.empty:
            return None, f"veri_yok: yfinance {kod}"
        df.columns = [c[0].lower() if isinstance(c, tuple) else str(c).lower() for c in df.columns]
        df.index = pd.to_datetime(df.index, utc=True)
        return _kapanmis(df[["open", "high", "low", "close", "volume"]].dropna(), dk), f"yfinance {kod}"
    return None, "veri_yok: gün içi/yerel piyasa (Dukascopy bekliyor)" if dk < 1440 else f"veri_yok: eşleme yok ({sembol})"


def _yeniden_ornekle(df: pd.DataFrame, dk: int) -> pd.DataFrame:
    kural = f"{dk}min"
    out = df.resample(kural, origin="epoch", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    return out.dropna(subset=["open"])


def _kapanmis(df: pd.DataFrame, dk: int) -> pd.DataFrame:
    simdi = pd.Timestamp.now(tz="UTC")
    return df[df.index + pd.to_timedelta(int(dk), unit="min") <= simdi]


def surum_tarihi(kimlik: str, kaynak: dict | None = None) -> tuple[pd.Timestamp | None, str]:
    """Test edilen sürümün tarihi: modülün KAYNAK['surum_tarihi'], yoksa arastirma/tv2_surumler.csv."""
    if kaynak and kaynak.get("surum_tarihi"):
        return pd.Timestamp(kaynak["surum_tarihi"], tz="UTC"), "temiz"
    if not SURUMLER.exists():
        return None, "tarih_belirsiz"
    tablo = pd.read_csv(SURUMLER, dtype=str)
    satir = tablo[tablo["id"] == kimlik]
    if satir.empty or pd.isna(satir.iloc[0].get("son_surum_tarihi")):
        return None, "tarih_belirsiz"
    return pd.Timestamp(satir.iloc[0]["son_surum_tarihi"], tz="UTC"), "temiz"


def _metrik(sonuc: Sonuc, bas: pd.Timestamp | None, on: str) -> dict[str, float]:
    t = sonuc.islemler
    if bas is not None:
        t = t[t["giris_zaman"] >= bas]
    kar, zarar = t.loc[t["net"] > 0, "net"].sum(), -t.loc[t["net"] < 0, "net"].sum()
    eq = sonuc.ozkaynak if bas is None else sonuc.ozkaynak[sonuc.ozkaynak.index >= bas]
    return {
        f"{on}_islem": len(t),
        f"{on}_net_yuzde": float(t["net"].sum() / sonuc.ayarlar.initial_capital * 100),
        f"{on}_pf": float(kar / zarar) if zarar > 0 else (np.inf if kar > 0 else np.nan),
        f"{on}_mdd": float((1 - eq / eq.cummax()).max()) if len(eq) else np.nan,
        f"{on}_hafta": int(t["giris_zaman"].dt.tz_convert(None).dt.to_period("W").nunique()) if len(t) else 0,
    }


def kos(kimlik: str) -> dict:
    modul = importlib.import_module(f"strategies.tv2.{kimlik}")
    kaynak = modul.KAYNAK
    satir: dict = {"id": kimlik, "sembol": kaynak["sembol"], "tf": kaynak["tf"], "url": kaynak["url"]}
    df, notu = veri(kaynak["sembol"], kaynak["tf"])
    satir["veri"] = notu
    if df is None:
        return satir | {"karar": "veri_yok", "neden": notu}
    satir |= {"bas": df.index[0].date(), "son": df.index[-1].date(), "bar": len(df)}
    hatalar = nedensellik(modul, df)
    kripto = notu.startswith("Binance")
    yazar = calistir(modul, df)
    uyg = calistir(modul, df, **gercekci(modul.AYARLAR, kripto=kripto))
    bas, etiket = surum_tarihi(kimlik, kaynak)
    if bas is not None and (df.index[-1] - bas).days < 365:
        etiket = "yetersiz_kanit"
    satir |= {"surum_tarihi": bas.date() if bas is not None else None, "etiket": etiket}
    satir |= _metrik(yazar, None, "yazar_tum") | _metrik(uyg, None, "uyg_tum")
    if bas is not None:
        satir |= _metrik(yazar, bas, "yazar_sinama") | _metrik(uyg, bas, "uyg_sinama")
        alt = df[df.index >= bas]
        satir["altut_sinama_yuzde"] = float((alt["close"].iloc[-1] / alt["open"].iloc[0] - 1) * 100) if len(alt) else np.nan
    OUT.joinpath("getiriler").mkdir(parents=True, exist_ok=True)
    uyg.ozkaynak.resample("1D").last().dropna().pct_change().dropna().rename("getiri").to_csv(OUT / "getiriler" / f"{kimlik}.csv")
    if hatalar:
        satir |= {"karar": "uygulanamaz", "neden": "nedensellik: " + hatalar[0]}
    elif bas is None:
        satir |= {"karar": "izle", "neden": "sürüm tarihi yok: sınama dönemi belirlenemedi"}
    elif etiket == "yetersiz_kanit":
        satir |= {"karar": "izle", "neden": "sürüm sonrası 1 yıldan az veri"}
    elif satir["uyg_sinama_hafta"] < KAPI_HAFTA:
        satir |= {"karar": "izle", "neden": f"sınamada {satir['uyg_sinama_hafta']} işlem haftası (< {KAPI_HAFTA})"}
    elif satir["uyg_sinama_net_yuzde"] > 0:
        satir |= {"karar": "gecti", "neden": ""}
    else:
        satir |= {"karar": "kaldi", "neden": "uygulanabilir sınama net <= 0"}
    return satir


def tum_moduller() -> list[str]:
    import strategies.tv2 as paket
    return sorted(m.name for m in pkgutil.iter_modules(paket.__path__) if not m.name.startswith("_"))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("idler", nargs="*")
    args = ap.parse_args(argv)
    satirlar = [kos(k) for k in (args.idler or tum_moduller())]
    OUT.mkdir(parents=True, exist_ok=True)
    yol = OUT / "sonuclar.csv"
    yeni = pd.DataFrame(satirlar)
    if yol.exists():
        eski = pd.read_csv(yol)
        yeni = pd.concat([eski[~eski["id"].isin(yeni["id"])], yeni], ignore_index=True)
    yeni.sort_values("id").to_csv(yol, index=False)
    print(pd.DataFrame(satirlar)[["id", "veri", "etiket", "karar", "neden"]].to_string(index=False))


if __name__ == "__main__":
    main()
