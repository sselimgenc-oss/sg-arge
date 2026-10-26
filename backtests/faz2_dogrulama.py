"""Faz 2: asıl piyasa verisiyle, TV-2 kapısını değiştirmeden dört doğrulama.

Bu modül yeni bir backtest motoru değildir.  Pine kaynağını ve emir semantiğini
``backtests.tv2`` / ``engine.tv_emulator``dan alır; burada yalnız veri alma,
funding nakit akışı ve MNQ continuous-contract düzeltmesi bulunur.
"""
from __future__ import annotations

import argparse
import calendar
import io
import json
import zipfile
from dataclasses import replace
from pathlib import Path
from typing import Callable

import pandas as pd
import requests

from backtests import tv2
from engine.pine.yorumlayici import PineStrateji
from engine.tv_emulator import Sonuc, calistir, gercekci

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "faz2_dogrulama.csv"
COINBASE = "https://api.exchange.coinbase.com/products/ETH-USD/candles"
VISION = "https://data.binance.vision/data/futures/um/monthly"


def coinbase_mumlari(bas: pd.Timestamp, son: pd.Timestamp, get: Callable = requests.get) -> pd.DataFrame:
    """Coinbase'ın en çok 300 mumluk, ters sıralı yanıtlarını ileri sayfala."""
    adim = pd.Timedelta(15 * 300, unit="min")
    parcalar: list[pd.DataFrame] = []
    cursor = pd.Timestamp(bas, tz="UTC") if pd.Timestamp(bas).tzinfo is None else pd.Timestamp(bas).tz_convert("UTC")
    bitis = pd.Timestamp(son, tz="UTC") if pd.Timestamp(son).tzinfo is None else pd.Timestamp(son).tz_convert("UTC")
    while cursor < bitis:
        sonraki = min(cursor + adim, bitis)
        yanit = get(COINBASE, params={"granularity": 900, "start": cursor.isoformat(), "end": sonraki.isoformat()}, timeout=30)
        yanit.raise_for_status()
        rows = yanit.json()
        if rows:
            # Coinbase: time, low, high, open, close, volume
            parca = pd.DataFrame(rows, columns=["zaman", "low", "high", "open", "close", "volume"])
            parca.index = pd.to_datetime(parca.pop("zaman"), unit="s", utc=True)
            parcalar.append(parca[["open", "high", "low", "close", "volume"]].apply(pd.to_numeric))
        cursor = sonraki
    if not parcalar:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    return pd.concat(parcalar).sort_index().loc[lambda x: ~x.index.duplicated(keep="last")]


def funding_nakit_akisi(islemler: pd.DataFrame, funding: pd.DataFrame) -> pd.DataFrame:
    """Kapalı işlemlere denk gelen funding'i hesapla; pozitif oran uzun için maliyettir."""
    if islemler.empty or funding.empty:
        return pd.DataFrame(columns=["zaman", "nakit"])
    out: list[dict] = []
    for zaman, row in funding.sort_index().iterrows():
        rate = float(row["rate"])
        price = float(row["price"])
        acik = islemler[(islemler["giris_zaman"] <= zaman) & (islemler["cikis_zaman"] > zaman)]
        cash = sum(float(t.yon) * float(t.adet) * price * rate for t in acik.itertuples())
        # long +rate öder: portföyden çıkar; short +rate alır: portföye girer
        out.append({"zaman": zaman, "nakit": -cash})
    return pd.DataFrame(out)


def fundingli_sonuc(sonuc: Sonuc, funding: pd.DataFrame, bas: pd.Timestamp) -> tuple[dict[str, float], float]:
    """Sınama dönemindeki (bas sonrası açılan) işlemlere funding nakit akışını ekleyerek özet döndür."""
    trades = sonuc.islemler[sonuc.islemler["giris_zaman"] >= bas]
    akis = funding_nakit_akisi(trades, funding)
    toplam = float(akis["nakit"].sum()) if not akis.empty else 0.0
    eq = sonuc.ozkaynak[sonuc.ozkaynak.index >= bas].copy()
    for row in akis.itertuples():
        eq.loc[eq.index >= row.zaman] += row.nakit
    # PF için nakit akışını, gerçekleştiği anda ayrı PnL gözlemi olarak sayıyoruz.
    pnl = pd.concat([trades["net"], akis["nakit"]], ignore_index=True) if not akis.empty else trades["net"]
    kar, zarar = pnl[pnl > 0].sum(), -pnl[pnl < 0].sum()
    return {
        "net_yuzde": float((trades["net"].sum() + toplam) / sonuc.ayarlar.initial_capital * 100),
        "pf": float(kar / zarar) if zarar else (float("inf") if kar else float("nan")),
        "mdd": float((1 - eq / eq.cummax()).max()) if len(eq) else float("nan"),
    }, toplam


def _ucuncu_cuma(yil: int, ay: int) -> pd.Timestamp:
    weeks = calendar.monthcalendar(yil, ay)
    fridays = [week[calendar.FRIDAY] for week in weeks if week[calendar.FRIDAY]]
    return pd.Timestamp(yil, ay, fridays[2], tz="UTC")


def mnq_back_adjust(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Çeyreklik devir boşluklarını üçüncü Cuma öncesi pencerede saptayıp geçmişe uygula.

    Sonraki fiyatlar sabit kalır; her pozitif roll farkı eski fiyatlara eklenir.
    """
    out, rolls = df.copy(), []
    closes = df["close"]
    for year in range(df.index.min().year, df.index.max().year + 1):
        for month in (3, 6, 9, 12):
            third = _ucuncu_cuma(year, month)
            lo, hi = third - pd.Timedelta(11, unit="D"), third - pd.Timedelta(2, unit="D")
            candidates = closes.loc[(closes.index >= lo) & (closes.index <= hi)]
            if len(candidates) < 2:
                continue
            gaps = candidates.diff().dropna()
            # Günlük gürültüden belirgin en büyük kapanış boşluğu seçilir. Uyarı (lider): bu sezgisel tespit piyasa
            # hareketini de seçebilir (negatif "boşluklar"); QQQ satırı devir boşluksuz karşılaştırmadır.
            date, gap = gaps.abs().idxmax(), float(gaps.loc[gaps.abs().idxmax()])
            typical = float(closes.diff().abs().median())
            if typical and abs(gap) < typical * 3:
                continue
            before = out.index < date
            out.loc[before, ["open", "high", "low", "close"]] += gap
            rolls.append({"zaman": date.isoformat(), "fark_puan": gap})
    return out, rolls


def _pine(kimlik: str, sembol: str, tf: str, mintick: float, point_value: float = 1.0, kripto: bool = True) -> PineStrateji:
    _modul, kaynak = tv2.strateji(kimlik)
    src = tv2.pine_kaynak(kimlik, kaynak["pub"])
    if not src:
        raise RuntimeError(f"{kimlik}: Pine kaynağı alınamadı")
    modul = PineStrateji(src, sembol=sembol, tf=tf, tz="UTC" if kripto else "America/New_York",
                         mintick=mintick, kimlik=kimlik)  # TV-2 `kos` ile aynı saat dilimi kuralı
    modul.veri_saglayici = tv2._dis_veri
    modul.AYARLAR = replace(modul.AYARLAR, point_value=point_value, mintick=mintick)
    return modul


def surum_tarihi(kimlik: str) -> pd.Timestamp:
    """TV-2 sınama başlangıcı: geçen satırın `surum_tarihi` (yayım sonrası dönem)."""
    satir = json.loads((ROOT / "results" / "tv2" / "satirlar" / f"{kimlik}.json").read_text(encoding="utf-8"))
    return pd.Timestamp(satir["surum_tarihi"], tz="UTC")


def _metrik(sonuc: Sonuc, bas: pd.Timestamp) -> dict[str, float]:
    """TV-2 kapısıyla aynı ölçü: yayım (sürüm) tarihinden sonra açılan işlemler (`tv2._metrik`)."""
    m = tv2._metrik(sonuc, bas, "s")
    return {k[2:]: v for k, v in m.items()}


def devir_acik_pnl_puan(islemler: pd.DataFrame, rolls: list[dict]) -> float:
    """Devir anında açık olan kapanmış işlemlere yazılan hayalî puan PnL'i."""
    total = 0.0
    for roll in rolls:
        zaman = pd.Timestamp(roll["zaman"])
        acik = islemler[(islemler["giris_zaman"] < zaman) & (islemler["cikis_zaman"] >= zaman)]
        total += sum(float(t.yon) * float(t.adet) * float(roll["fark_puan"]) for t in acik.itertuples())
    return total


def kos(kimlik: str, df: pd.DataFrame, sembol: str, tf: str, mintick: float, kripto: bool,
        funding: pd.DataFrame | None = None, point_value: float = 1.0, rolls: list[dict] | None = None) -> dict:
    """Tek doğrulamayı mevcut Pine/emülatör/maliyet zinciriyle çalıştır."""
    modul = _pine(kimlik, sembol, tf, mintick, point_value, kripto)
    sonuc = calistir(modul, df, **gercekci(modul.AYARLAR, kripto=kripto))
    bas = surum_tarihi(kimlik)
    row = {"kimlik": kimlik, "veri": sembol, "sinama_bas": bas.date(), "son": df.index[-1], **_metrik(sonuc, bas)}
    # Sabit adetli stratejilerde net %, yazar sermayesine göre kaldıraçlıdır (9u8pzF0I: 4.500 USD ile 8 MNQ).
    t = sonuc.islemler[sonuc.islemler["giris_zaman"] >= bas]
    nominal = (t["adet"].abs() * t["giris_fiyat"] * point_value) if len(t) else pd.Series(dtype=float)
    row["nominal_kaldirac"] = float(nominal.max() / sonuc.ayarlar.initial_capital) if len(nominal) else float("nan")
    row["net_yuzde_1x"] = row["net_yuzde"] / row["nominal_kaldirac"] if row["nominal_kaldirac"] else float("nan")
    if funding is not None:
        fm, nakit = fundingli_sonuc(sonuc, funding, bas)
        row |= {"funding_nakit": nakit, **{f"fundingli_{k}": v for k, v in fm.items()}}
    if rolls is not None:
        row["devir_acik_pnl_puan"] = devir_acik_pnl_puan(sonuc.islemler, rolls)
    return row


def binance_um_mumlari(aralik: str, bas: pd.Timestamp, son: pd.Timestamp) -> pd.DataFrame:
    """Binance Data Vision aylık UM arşivini indirir; eksik ay hata olarak görünür."""
    months = pd.period_range(bas.to_period("M"), son.to_period("M"), freq="M")
    pieces = []
    for month in months:
        tag = str(month)
        url = f"{VISION}/klines/BTCUSDT/{aralik}/BTCUSDT-{aralik}-{tag}.zip"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            with archive.open(archive.namelist()[0]) as handle:
                raw = pd.read_csv(handle, header=None)
        raw = raw.iloc[:, :6]
        raw.columns = ["zaman", "open", "high", "low", "close", "volume"]
        raw = raw[pd.to_numeric(raw["zaman"], errors="coerce").notna()]  # yeni arşivlerde başlık satırı var
        raw.index = pd.to_datetime(pd.to_numeric(raw.pop("zaman")), unit="ms", utc=True)
        pieces.append(raw.apply(pd.to_numeric))
    return pd.concat(pieces).sort_index().loc[bas:son]


def binance_funding(bas: pd.Timestamp, son: pd.Timestamp, prices: pd.DataFrame) -> pd.DataFrame:
    """Aylık fundingRate arşivleri; oranı aynı/anlık önceki perp kapanışıyla eşleştirir."""
    months = pd.period_range(bas.to_period("M"), son.to_period("M"), freq="M")
    pieces = []
    for month in months:
        url = f"{VISION}/fundingRate/BTCUSDT/BTCUSDT-fundingRate-{month}.zip"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            with archive.open(archive.namelist()[0]) as handle:
                raw = pd.read_csv(handle)
        raw.columns = [str(c).strip().lower() for c in raw.columns]
        zaman = next(c for c in raw if "time" in c)
        rate = next(c for c in raw if "rate" in c)
        frame = pd.DataFrame({"zaman": pd.to_datetime(raw[zaman], unit="ms", utc=True), "rate": pd.to_numeric(raw[rate])})
        pieces.append(frame)
    rates = pd.concat(pieces).sort_values("zaman")
    px = prices[["close"]].rename_axis("zaman").reset_index().sort_values("zaman")
    return pd.merge_asof(rates, px, on="zaman", direction="backward").rename(columns={"close": "price"}).set_index("zaman")


def ilk_sonuc(kimlik: str) -> float:
    table = pd.read_csv(ROOT / "results" / "faz1_tum_sonuclar.csv")
    row = table.loc[table["kimlik"] == kimlik].iloc[0]
    return float(row["sinama_net_yuzde"])


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Faz 2, asıl piyasa veri doğrulaması")
    ap.add_argument("--coinbase-only", action="store_true", help="yalnız Coinbase doğrulamasını indir/çalıştır")
    args = ap.parse_args(argv)
    # Ağdan büyük arşiv indirmek bilinçli bir komutla sınırlıdır; sonuç dosyası yalnız tamamlanan koşuları içerir.
    now = pd.Timestamp.now(tz="UTC").floor("15min")
    bas = pd.Timestamp("2026-03-01", tz="UTC")  # en eski doğrulama Pine sürümünden önce ısınma penceresi
    eth = coinbase_mumlari(bas, now)
    rows = [kos("QCkIgf3z", eth, "COINBASE:ETHUSD", "15", 0.01, True)]
    if not args.coinbase_only:
        # Data Vision aylık arşivi yalnız biten aylar için var; perp koşuları son biten ayın sonunda biter.
        ay_sonu = now.normalize().replace(day=1) - pd.Timedelta(1, unit="min")
        p15 = binance_um_mumlari("15m", bas, ay_sonu)
        fund15 = binance_funding(bas, ay_sonu, p15)
        rows.append(kos("BR74LOKo", p15, "BINANCE:BTCUSDT.P", "15", 0.1, True, fund15))
        p1h = binance_um_mumlari("1h", bas, ay_sonu)
        p3h = tv2._yeniden_ornekle(p1h, 180)
        fund3h = binance_funding(bas, ay_sonu, p1h)
        rows.append(kos("zuEOEYPK", p3h, "BINANCE:BTCUSDT.P", "180", 0.1, True, fund3h))
        # MNQ=F / QQQ ücretsiz 60dk serileri: yfinance sınırı nedeniyle bunlar canlı döneme dair ek kanıttır.
        mnq, _ = tv2._yfinance_gun_ici("MNQ=F", 120)
        if mnq is not None:
            adjusted, rolls = mnq_back_adjust(mnq)
            raw = kos("9u8pzF0I", mnq, "CME_MINI:MNQ1!", "120", .25, False, point_value=2, rolls=rolls)
            raw["varyant"] = "MNQ=F_duzeltilmemis"
            adj = kos("9u8pzF0I", adjusted, "CME_MINI:MNQ1!", "120", .25, False, point_value=2)
            adj["varyant"] = "MNQ=F_back_adjusted"
            qqq60, _ = tv2._yfinance_gun_ici("QQQ", 120)
            rows.extend([raw, adj])
            if qqq60 is not None:
                qqq = kos("9u8pzF0I", qqq60, "NASDAQ:QQQ", "120", .01, False)
                qqq["varyant"] = "QQQ_60m_to_120m_regular_session"
                rows.append(qqq)
    for row in rows:
        row["tv2_ilk_net_yuzde"] = ilk_sonuc(row["kimlik"])
        row["fark_net_yuzde"] = row["net_yuzde"] - row["tv2_ilk_net_yuzde"]
        # Kapı gerçekçi maliyetle: perp satırlarında funding dahil net.
        net = row.get("fundingli_net_yuzde", row["net_yuzde"])
        row["kapi"] = "gecti" if net > 0 else "kaldi"
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
