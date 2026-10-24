"""Pine Script yorumlayıcısı (TV-2): TradingView strateji kodunu çeviri yapmadan bar bar yürütür.

Ayrıştırma `pynescript` (Pine v2-v6 AST). Yürütme modeli Pine'ınkidir: betik her bar kapanışında baştan sona bir kez
çalışır; `var`/`varip` değişkenleri ilk atamadan sonra korunur, diğerleri her bar yeniden hesaplanır; `x[n]` değişkenin n
bar önceki kapanış değeridir; her `ta.*` çağrı yerinin (kullanıcı fonksiyonu içindeyse çağrı zinciri başına) kendi durumu
vardır. Emirler `engine/tv_emulator.Baglam`'a gider (dolum semantiği orada).

Sessiz yanlış sonuç yerine açık hata: desteklenmeyen her yerleşik ad `Desteklenmiyor(ad)` yükseltir; koşucu stratejiyi
"desteklenmiyor: <ad>" diye listeler. Grafik çizimi (plot, label, line, box, table, renkler, uyarılar) sonucu
etkilemediği için yok sayılır.

Belgelenmiş varsayımlar:
- v5 ve öncesinde iki tam sayının bölümü tam sayıdır (sıfıra doğru kesilir), v6'da ondalıklı (Pine v6 değişikliği).
- `and`/`or` v6'da kısa devre, öncekilerde iki taraf da hesaplanır.
- `request.security` yalnız aynı sembol ve grafikten yüksek/eşit zaman dilimi: yüksek dilim barları grafik
  barlarından kurulur; `lookahead_off` (varsayılan) geçmiş barlarda yüksek dilim barı KAPANDIĞI grafik barında yeni
  değeri verir, öncesinde son kapanmış değeri; `lookahead_on` içinde bulunulan yüksek dilim barının son değerini verir
  (`[1]` olmadan geleceği görür; nedensellik denetimi yakalar).
- Zaman fonksiyonları borsa saat dilimindedir (kripto UTC).
"""

from __future__ import annotations

import copy
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
import pandas as pd

import pynescript.ast as A
from pynescript.ast import parse

from engine.pine import ta as T
from engine.tv_emulator import LONG, SHORT, Ayarlar

NA = T.NA
na = T.na


class Desteklenmiyor(Exception):
    """Yorumlayıcının birebir yürütemediği yapı/yerleşik ad."""


class PineHatasi(Exception):
    """Betiğin kendisinin çalışma hatası (runtime.error, dizi sınırı vb.)."""


class _Kir(Exception):
    pass


class _Devam(Exception):
    pass


GORSEL_AD = {"plot", "plotshape", "plotchar", "plotcandle", "plotbar", "plotarrow", "hline", "fill", "bgcolor",
             "barcolor", "alert", "alertcondition", "max_bars_back", "indicator", "study", "library"}
GORSEL_NS = {"label", "line", "box", "table", "linefill", "polyline", "log", "chart.point"}
SABIT_NS = {"color", "shape", "location", "size", "plot", "position", "text", "xloc", "yloc", "extend", "line", "label",
            "hline", "display", "format", "alert", "currency", "scale", "font", "box", "table", "linefill", "chart",
            "barmerge", "session", "order", "adjustment", "backadjustment", "settlement_as_close", "dividends",
            "earnings", "splits", "input", "dayofweek", "strategy.oca", "strategy.direction", "math", "xloc"}
V3_SABIT = {  # v2/v3 namespace'siz renk ve çizim sabitleri (yalnız görsel)
    "aqua", "black", "blue", "fuchsia", "gray", "green", "lime", "maroon", "navy", "olive", "orange", "purple", "red",
    "silver", "teal", "white", "yellow", "line", "stepline", "histogram", "cross", "area", "columns", "circles", "linebr",
    "areabr", "solid", "dotted", "dashed", "dayofweek", "integer", "float", "bool", "string", "source", "resolution",
    "session", "symbol", "time", "price", "color"}
DISPLAY = {"display.none": 0, "display.pane": 1, "display.data_window": 2, "display.price_scale": 4,
           "display.status_line": 8, "display.pine_screener": 16, "display.all": 31}
V4_ADLAR = {  # namespace'siz eski adlar -> v5 adı
    **{k: "ta." + k for k in ("sma", "ema", "rma", "wma", "vwma", "hma", "alma", "atr", "rsi", "crossover", "crossunder",
                               "cross", "highest", "lowest", "highestbars", "lowestbars", "change", "stdev", "dmi",
                               "macd", "stoch", "pivothigh", "pivotlow", "barssince", "valuewhen", "linreg", "cum",
                               "mom", "roc", "percentrank", "vwap", "sar", "supertrend", "cci", "mfi", "tr", "falling",
                               "rising", "variance", "dev", "correlation", "median", "wpr", "obv", "bb", "swma",
                               "tsi", "cmo", "kc", "bbw", "accdist")},
    **{k: "math." + k for k in ("abs", "max", "min", "round", "sqrt", "pow", "log", "log10", "exp", "floor", "ceil",
                                 "sign", "avg", "sin", "cos", "tan", "asin", "acos", "atan", "sum", "todegrees",
                                 "toradians")},
    "security": "request.security", "tostring": "str.tostring", "tonumber": "str.tonumber", "timestamp": "timestamp",
}


@dataclass
class _Yuva:
    """Bir değişkenin (ya da çağrı yeri ifadesinin) bar bar değeri."""
    deger: Any = NA
    gecmis: list = field(default_factory=list)
    kalici: bool = False      # var/varip
    ip: bool = False          # varip: bar içi ek yürütmeler arasında geri sarılmaz
    basladi: bool = False
    atandi: bool = False


class _Cizim:
    """line / box / label: görsel, ama betikler koordinatlarını geri okuyabilir (get_*); yalnız konum alanları tutulur."""

    ALANLAR = {"line": ("x1", "y1", "x2", "y2"), "box": ("left", "top", "right", "bottom"), "label": ("x", "y", "text")}

    def __init__(self, tur: str, alan: dict) -> None:
        self.tur, self.alan = tur, alan


class _Matris:
    """Pine matrix: satır listeleri."""

    def __init__(self, satirlar: list[list]) -> None:
        self.s = satirlar


class _Nesne:
    """Kullanıcı tipi (type) örneği."""

    def __init__(self, tip: str, alanlar: dict) -> None:
        self.__dict__["_tip"] = tip
        self.__dict__["_alan"] = dict(alanlar)

    def __getattr__(self, ad):
        try:
            return self.__dict__["_alan"][ad]
        except KeyError:
            raise PineHatasi(f"{self._tip} tipinde '{ad}' alanı yok") from None


@dataclass
class _Fonksiyon:
    ad: str
    dugum: A.FunctionDef
    yontem: bool


def tf_dakika(tf: str) -> int:
    """'60' / '240' / 'D' / '1D' / 'W' / 'M' / '4H' / '30S' -> dakika (ay = 43200, saniye kesirli)."""
    s = str(tf).strip().upper()
    if s in ("", "0"):
        return 0
    sayi = "".join(ch for ch in s if ch.isdigit()) or "1"
    birim = "".join(ch for ch in s if ch.isalpha())
    n = int(sayi)
    return {"": n, "H": 60 * n, "D": 1440 * n, "W": 10080 * n, "M": 43200 * n, "S": max(n // 60, 0)}.get(birim, n)


def tf_metin(dk: int) -> str:
    if dk % 43200 == 0:
        return f"{dk // 43200 if dk // 43200 > 1 else ''}M"
    if dk % 10080 == 0:
        return f"{dk // 10080 if dk // 10080 > 1 else ''}W"
    if dk % 1440 == 0:
        return f"{dk // 1440 if dk // 1440 > 1 else ''}D"
    return str(dk)


def _kova(zaman: pd.DatetimeIndex, dk: int, tz: str) -> tuple[np.ndarray, np.ndarray]:
    """Her grafik barının yüksek dilim kovasının (başlangıç, bitiş) zamanları (UTC ns)."""
    yerel = zaman.tz_convert(tz)
    if dk % 43200 == 0:
        ay = dk // 43200
        bas = yerel.to_period("M").to_timestamp().tz_localize(tz, ambiguous="NaT", nonexistent="shift_forward")
        aylar = (bas.year * 12 + bas.month - 1)
        aylar = aylar - aylar % ay
        bas = pd.to_datetime({"year": aylar // 12, "month": aylar % 12 + 1, "day": 1}).dt.tz_localize(tz)
        bas = pd.DatetimeIndex(bas)
        bit = pd.DatetimeIndex([b + pd.DateOffset(months=ay) for b in bas])
    elif dk % 10080 == 0:
        gun0 = yerel.normalize()
        bas = gun0 - pd.to_timedelta(gun0.weekday, unit="D")
        hafta = dk // 10080
        if hafta > 1:
            k = ((bas.tz_convert("UTC").asi8 // 1_000_000_000 // 86400 - 4) // 7) % hafta
            bas = bas - pd.to_timedelta(k * 7, unit="D")
        bit = bas + pd.Timedelta(days=7 * hafta)
    elif dk % 1440 == 0:
        bas = yerel.normalize()
        gun = dk // 1440
        if gun > 1:
            k = (bas.tz_localize(None).asi8 // 86_400_000_000_000) % gun
            bas = bas - pd.to_timedelta(k, unit="D")
        bit = bas + pd.Timedelta(days=gun)
    else:
        ns = dk * 60_000_000_000
        u = zaman.asi8
        b = u - u % ns
        return b, b + ns
    return bas.tz_convert("UTC").asi8, bit.tz_convert("UTC").asi8


class Yorumlayici:
    def __init__(self, program: A.Script, df: pd.DataFrame | None, *, tf_dk: int, sembol: str, tz: str = "UTC",
                 mintick: float = 0.01, girdiler: dict | None = None, guvenlik_modu: bool = False) -> None:
        self.p = program
        self.surum = _surum(program)
        self.tf_dk, self.sembol, self.tz, self.mintick = tf_dk, sembol, tz, mintick
        self.guvenlik_modu = guvenlik_modu
        self.yuvalar: dict[tuple, _Yuva] = {}
        self.yuva_listesi: list[_Yuva] = []
        self.durum: dict[tuple, Any] = {}
        self.fonksiyonlar: dict[str, list[_Fonksiyon]] = {}
        self.yontemler: dict[str, list[_Fonksiyon]] = {}
        self.tipler: dict[str, A.TypeDef] = {}
        self.eksik_kutuphane: dict[str, str] = {}
        self.yol: tuple = ()
        self.kapsam: list[dict[str, _Yuva]] = [{}]
        self.ctx = None
        self.i = -1
        self.girdiler = girdiler if girdiler is not None else {}
        self.risk_yon: int | None = None
        self.risk_maks_dd: tuple | None = None
        self.durdu = False
        self.risk_gun_zarar: tuple | None = None       # (değer, tür) strategy.risk.max_intraday_loss
        self.risk_gun_emir: int | None = None          # strategy.risk.max_intraday_filled_orders
        self.risk_gun: int | None = None
        self.risk_ardisik: int | None = None           # strategy.risk.max_cons_loss_days
        self.zararli_gun = 0
        self.gun_durdu: int | None = None              # gün içi sınır aşıldıysa o günün kodu
        self.son_ozkaynak = self.son_dolum = 0.0
        self.zirve = -math.inf
        self.maks_dd = 0.0
        self.guvenlik: dict[str, dict] = {}       # tf metni -> {'yorum': Yorumlayici, 'kayit': {dugum_id: [degerler]}, ...}
        self.guvenlik_kayit: dict[int, list] = {}  # güvenlik modunda: dugum id -> HTF bar değerleri
        self.veri_saglayici = None                  # (sembol, dakika) -> OHLC DataFrame | None (dış sembol)
        self.df = None
        if df is not None:
            self._veri(df)
        self._kaydet(program.body)

    # ------------------------------------------------------------------ veri
    def _veri(self, df: pd.DataFrame) -> None:
        self.df = df
        self.o, self.h, self.l, self.c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
        self.v = df["volume"].to_numpy(float) if "volume" in df else np.zeros(len(df))
        self.zaman_ms = (df.index.asi8 // 1_000_000).astype(np.int64)
        self.n = len(df)
        yerel = df.index.tz_convert(self.tz)
        self.yil, self.ay, self.gun = yerel.year.to_numpy(), yerel.month.to_numpy(), yerel.day.to_numpy()
        self.saat, self.dakika_, self.saniye = yerel.hour.to_numpy(), yerel.minute.to_numpy(), yerel.second.to_numpy()
        self.haftagun = ((yerel.weekday.to_numpy() + 1) % 7) + 1          # Pine: pazar 1 ... cumartesi 7
        self.gun_kodu = (yerel.normalize().asi8 // 86_400_000_000_000)

    def _kaydet(self, govde: list) -> None:
        for d in govde:
            if isinstance(d, A.FunctionDef):
                hedef = self.yontemler if d.method else self.fonksiyonlar
                hedef.setdefault(d.name, []).append(_Fonksiyon(d.name, d, bool(d.method)))
            elif isinstance(d, A.TypeDef):
                self.tipler[d.name] = d
            elif isinstance(d, A.Import):
                self._kutuphane(d)
            elif isinstance(d, A.EnumDef):
                raise Desteklenmiyor("enum")

    def _kutuphane(self, d: A.Import) -> None:
        """`import kullanıcı/ad/sürüm as takma`: dışa açık fonksiyon ve tipler `takma.ad` olarak, iç yardımcılar (çakışmazsa)
        çıplak adla kaydedilir. Kaynak bulunamazsa takma ad 'eksik' işaretlenir; çağrıldığında Desteklenmiyor."""
        yol = f"{d.namespace}/{d.name}/{d.version}"
        takma = d.alias or d.name
        kaynak = KUTUPHANE_SAGLAYICI(d.namespace, d.name, int(d.version)) if KUTUPHANE_SAGLAYICI else None
        if not kaynak:
            self.eksik_kutuphane[takma] = yol
            return
        lib = parse(on_isle(kaynak))
        for x in lib.body:
            if isinstance(x, A.FunctionDef):
                f = _Fonksiyon(x.name, x, bool(x.method))
                if x.method:
                    self.yontemler.setdefault(x.name, []).append(f)
                    continue
                self.fonksiyonlar.setdefault(f"{takma}.{x.name}", []).append(f)
                if x.name not in self.fonksiyonlar:
                    self.fonksiyonlar[x.name] = [f]
            elif isinstance(x, A.TypeDef):
                self.tipler[f"{takma}.{x.name}"] = x
                self.tipler.setdefault(x.name, x)
            elif isinstance(x, A.Import):
                self._kutuphane(x)
            elif isinstance(x, A.EnumDef):
                raise Desteklenmiyor("enum")

    # ------------------------------------------------------------------ bar
    def anlik(self) -> tuple:
        """Bar başı (önceki bar kapanışında kesinleşmiş) durum: bar içi ek yürütmeler bundan başlar."""
        degerler = copy.deepcopy(([(y.deger, y.basladi, y.atandi) for y in self.yuva_listesi], self.durum))
        return degerler, len(self.yuva_listesi), dict(self.yuvalar), dict(self.kapsam[0])

    def geri_sar(self, a: tuple) -> None:
        (degerler, durum), n, yuvalar, kapsam0 = copy.deepcopy(a[0]), a[1], a[2], a[3]
        del self.yuva_listesi[n:]
        self.yuvalar, self.kapsam, self.durum = dict(yuvalar), [dict(kapsam0)], durum
        for y, (d, b, at) in zip(self.yuva_listesi, degerler):
            if not y.ip:
                y.deger, y.basladi, y.atandi = d, b, at

    def adim(self, ctx, i: int, kesinlestir: bool = True) -> None:
        self.ctx, self.i = ctx, i
        if ctx is not None:
            self._risk_kontrol()
        self.kapsam = [self.kapsam[0]]
        self.yol = ()
        for d in self.p.body:
            if isinstance(d, (A.FunctionDef, A.TypeDef, A.Comment)):
                continue
            self._calistir(d)
        if not kesinlestir:
            return
        for y in self.yuva_listesi:
            y.gecmis.append(y.deger if (y.kalici or y.atandi) else NA)
            if not y.kalici:
                y.atandi = False

    def _risk_kontrol(self) -> None:
        self._gun_ici_risk()
        if self.risk_maks_dd is None or self.durdu:
            return
        eq = self.ctx.equity
        self.zirve = max(self.zirve, eq)
        deger, tip = self.risk_maks_dd
        dd = self.zirve - eq
        sinir = deger / 100 * self.zirve if tip == "percent_of_equity" else deger
        if dd >= sinir:
            self.durdu = True
            self.ctx.cancel_all()
            self.ctx.close_all()

    def _gun_ici_risk(self) -> None:
        """Gün içi sınırlar bar kapanışında denetlenir (geçmiş barlarda TradingView de dolumdan sonra denetler;
        bar içi sıra yaklaşık). Aşılınca açık emirler iptal, pozisyon kapanır, gün sonuna kadar giriş yok."""
        c = self.ctx
        gun = int(self.gun_kodu[self.i])
        if gun != self.risk_gun:                       # gün başı: önceki barın kapanışındaki durum taban
            if self.risk_gun is not None:              # biten gün zararlıysa seri uzar, değilse sıfırlanır
                self.zararli_gun = self.zararli_gun + 1 if self.son_ozkaynak < self.gun_ozkaynak else 0
                if self.risk_ardisik is not None and self.zararli_gun >= self.risk_ardisik and not self.durdu:
                    self.durdu = True                  # kalıcı: emirler iptal, pozisyon kapanır
                    c.cancel_all()
                    c.close_all()
            self.risk_gun, self.gun_ozkaynak, self.gun_dolum = gun, self.son_ozkaynak or c.equity, self.son_dolum
        self.son_ozkaynak, self.son_dolum = c.equity, c.dolum_sayisi
        if self.gun_durdu == gun:
            return
        asildi = False
        if self.risk_gun_zarar is not None:
            deger, tip = self.risk_gun_zarar
            sinir = deger / 100 * self.gun_ozkaynak if tip == "percent_of_equity" else deger
            asildi = self.gun_ozkaynak - c.equity >= sinir
        if self.risk_gun_emir is not None and c.dolum_sayisi - self.gun_dolum >= self.risk_gun_emir:
            asildi = True
        if asildi:
            self.gun_durdu = gun
            c.cancel_all()
            c.close_all()

    # ------------------------------------------------------------------ deyimler
    def _govde(self, govde: list, yeni_kapsam: bool = True) -> Any:
        if yeni_kapsam:
            self.kapsam.append({})
        sonuc = NA
        try:
            for d in govde:
                if isinstance(d, A.Comment):
                    continue
                sonuc = self._calistir(d)
        finally:
            if yeni_kapsam:
                self.kapsam.pop()
        return sonuc

    def _calistir(self, d) -> Any:
        t = type(d)
        if t is A.Expr:
            return self._deger(d.value)
        if t is A.Assign:
            return self._ata(d)
        if t is A.ReAssign:
            v = self._deger(d.value)
            self._yeniden_ata(d.target, v)
            return v
        if t is A.AugAssign:
            v = self._ikili(d.op, self._deger(d.target), self._deger(d.value))
            self._yeniden_ata(d.target, v)
            return v
        if t is A.Break:
            raise _Kir()
        if t is A.Continue:
            raise _Devam()
        if t in (A.FunctionDef, A.TypeDef):
            self._kaydet([d])
            return NA
        if t is A.Comment:
            return NA
        if t is A.Import:              # başlangıçta (_kaydet) kaydedildi
            return NA
        return self._deger(d)

    def _yuva(self, ad: str, d, kalici: bool, ip: bool = False) -> _Yuva:
        anahtar = (self.yol, id(d), ad)
        y = self.yuvalar.get(anahtar)
        if y is None:
            y = _Yuva(kalici=kalici, ip=ip)
            self.yuvalar[anahtar] = y
            self.yuva_listesi.append(y)
            y.gecmis = [NA] * max(self.i, 0)
        self.kapsam[-1][ad] = y
        return y

    def _ata(self, d: A.Assign) -> Any:
        kalici = isinstance(d.mode, (A.Var, A.VarIp))
        ip = isinstance(d.mode, A.VarIp)
        hedef = d.target
        if isinstance(hedef, A.Tuple):
            yuvalar = [self._yuva(e.id, d, kalici, ip) for e in hedef.elts]
            if kalici and all(y.basladi for y in yuvalar):
                return NA
            v = self._deger(d.value) if d.value is not None else tuple(NA for _ in yuvalar)
            if isinstance(v, list) and len(v) == len(yuvalar):
                v = tuple(v)
            elif not isinstance(v, tuple) and na(v):   # ör. üst dilimin ilk kapanmış barından önce security: hepsi na
                v = tuple(NA for _ in yuvalar)
            if not isinstance(v, tuple):
                raise PineHatasi("demet ataması demet olmayan değer aldı")
            for y, x in zip(yuvalar, v):
                y.deger, y.basladi, y.atandi = x, True, True
            return v
        y = self._yuva(hedef.id, d, kalici, ip)
        if kalici and y.basladi:
            return y.deger
        v = self._deger(d.value) if d.value is not None else NA
        v = self._tip_cevir(d.type, v)
        y.deger, y.basladi, y.atandi = v, True, True
        return v

    def _tip_cevir(self, tip, v):
        if tip is None or na(v):
            return v
        ad = tip.id if isinstance(tip, A.Name) else None
        if ad == "int" and isinstance(v, float):
            return int(v)
        if ad == "float" and isinstance(v, (int, bool)):
            return float(v)
        return v

    def _bul(self, ad: str) -> _Yuva | None:
        for k in reversed(self.kapsam):
            y = k.get(ad)
            if y is not None:
                return y
        return None

    def _yeniden_ata(self, hedef, v) -> None:
        if isinstance(hedef, A.Name):
            y = self._bul(hedef.id)
            if y is None:
                raise PineHatasi(f"tanımsız değişkene := : {hedef.id}")
            y.deger, y.atandi = v, True
            return
        if isinstance(hedef, A.Attribute):
            nesne = self._deger(hedef.value)
            if not isinstance(nesne, _Nesne):
                raise Desteklenmiyor(f"alan ataması: {_nokta(hedef)}")
            nesne._alan[hedef.attr] = v
            return
        if isinstance(hedef, A.Tuple):
            for e, x in zip(hedef.elts, v):
                self._yeniden_ata(e, x)
            return
        raise Desteklenmiyor(f"atama hedefi {type(hedef).__name__}")

    # ------------------------------------------------------------------ ifadeler
    def _deger(self, e) -> Any:
        t = type(e)
        if t is A.Constant:
            return e.value
        if t is A.Name:
            return self._ad(e.id)
        if t is A.BinOp:
            return self._ikili(e.op, self._deger(e.left), self._deger(e.right))
        if t is A.Compare:
            if isinstance(e.left, A.Attribute) and e.left.attr == "new" and len(e.ops) == 2:
                raise Desteklenmiyor("ayrıştırıcı: tür parametreli .new<...> (ön işlemden kaçtı)")
            sol = self._deger(e.left)
            for op, sag_d in zip(e.ops, e.comparators):
                sag = self._deger(sag_d)
                if not _karsilastir(op, sol, sag):
                    return False
                sol = sag
            return True
        if t is A.BoolOp:
            return self._mantik(e)
        if t is A.UnaryOp:
            x = self._deger(e.operand)
            if isinstance(e.op, A.Not):
                return not _dogru(x)
            if na(x):
                return NA
            return -x if isinstance(e.op, A.USub) else x
        if t is A.Conditional:
            return self._deger(e.body) if _dogru(self._deger(e.test)) else self._deger(e.orelse)
        if t is A.Call:
            return self._cagir(e)
        if t is A.Attribute:
            return self._oznitelik(e)
        if t is A.Subscript:
            return self._gecmis(e)
        if t is A.Tuple:
            return tuple(self._deger(x) for x in e.elts)
        if t is A.If:
            if _dogru(self._deger(e.test)):
                return self._govde(e.body)
            return self._govde(e.orelse) if e.orelse else NA
        if t is A.Switch:
            return self._switch(e)
        if t is A.ForTo:
            return self._for(e)
        if t is A.ForIn:
            return self._for_in(e)
        if t is A.While:
            return self._while(e)
        if t is A.Qualify:
            return self._deger(e.value)
        raise Desteklenmiyor(f"ifade {t.__name__}")

    def _ikili(self, op, a, b):
        t = type(op)
        if t is A.Add and (isinstance(a, str) or isinstance(b, str)):
            return ("" if na(a) else str(a)) + ("" if na(b) else str(b))
        if na(a) or na(b):
            return NA
        if t is A.Add:
            return a + b
        if t is A.Sub:
            return a - b
        if t is A.Mult:
            return a * b
        if t is A.Div:
            if b == 0:
                return NA
            if self.surum < 6 and isinstance(a, int) and isinstance(b, int) and not isinstance(a, bool):
                return int(a / b)
            return a / b
        if t is A.Mod:
            return NA if b == 0 else math.fmod(a, b) if isinstance(a, float) or isinstance(b, float) else int(math.fmod(a, b))
        raise Desteklenmiyor(f"işleç {t.__name__}")

    def _mantik(self, e) -> bool:
        ve = isinstance(e.op, A.And)
        if self.surum >= 6:
            for x in e.values:
                v = _dogru(self._deger(x))
                if ve and not v:
                    return False
                if not ve and v:
                    return True
            return ve
        vals = [_dogru(self._deger(x)) for x in e.values]
        return all(vals) if ve else any(vals)

    def _switch(self, e) -> Any:
        konu = self._deger(e.subject) if e.subject is not None else None
        for c in e.cases:
            if c.pattern is None:
                return self._govde(c.body)
            if e.subject is not None:
                if _esit(konu, self._deger(c.pattern)):
                    return self._govde(c.body)
            elif _dogru(self._deger(c.pattern)):
                return self._govde(c.body)
        return NA

    def _for(self, e) -> Any:
        bas, son = self._deger(e.start), self._deger(e.end)
        if na(bas) or na(son):
            return NA
        adim = self._deger(e.step) if e.step is not None else (1 if son >= bas else -1)
        if adim == 0 or na(adim):
            return NA
        if (son - bas) * adim < 0:
            adim = -adim
        self.kapsam.append({})
        y = self._yuva(e.target.id, e, False)
        sonuc = NA
        try:
            k, sayac = bas, 0
            while (k <= son) if adim > 0 else (k >= son):
                y.deger, y.atandi = k, True
                try:
                    sonuc = self._govde(e.body)
                except _Devam:
                    pass
                except _Kir:
                    break
                k += adim
                sayac += 1
                if sayac > 1_000_000:
                    raise PineHatasi("döngü sınırı")
        finally:
            self.kapsam.pop()
        return sonuc

    def _for_in(self, e) -> Any:
        dizi = self._deger(e.iter)
        if not isinstance(dizi, list):
            raise Desteklenmiyor("for-in dizi olmayan")
        self.kapsam.append({})
        hedef = e.target
        sonuc = NA
        try:
            for k, x in enumerate(list(dizi)):
                if isinstance(hedef, A.Tuple):
                    a, b = (self._yuva(t.id, e, False) for t in hedef.elts)
                    a.deger, b.deger, a.atandi, b.atandi = k, x, True, True
                else:
                    y = self._yuva(hedef.id, e, False)
                    y.deger, y.atandi = x, True
                try:
                    sonuc = self._govde(e.body)
                except _Devam:
                    pass
                except _Kir:
                    break
        finally:
            self.kapsam.pop()
        return sonuc

    def _while(self, e) -> Any:
        sonuc, sayac = NA, 0
        while _dogru(self._deger(e.test)):
            try:
                sonuc = self._govde(e.body)
            except _Devam:
                pass
            except _Kir:
                break
            sayac += 1
            if sayac > 1_000_000:
                raise PineHatasi("döngü sınırı")
        return sonuc

    # ------------------------------------------------------------------ adlar ve geçmiş
    def _ad(self, ad: str) -> Any:
        y = self._bul(ad)
        if y is not None:
            return y.deger
        return self._yerlesik_seri(ad, 0)

    def _yerlesik_seri(self, ad: str, n: int) -> Any:
        if ad in ("na",):
            return NA
        if ad in ("true", "false"):
            return ad == "true"
        k = self.i - int(n)
        if self.df is None:
            raise Desteklenmiyor(f"veri yokken seri: {ad}")
        seri = {"open": self.o, "high": self.h, "low": self.l, "close": self.c, "volume": self.v}.get(ad)
        if seri is not None:
            return float(seri[k]) if 0 <= k <= self.i else NA
        if ad in ("hl2", "hlc3", "ohlc4", "hlcc4"):
            if not 0 <= k <= self.i:
                return NA
            o, h, l, c = self.o[k], self.h[k], self.l[k], self.c[k]
            return {"hl2": (h + l) / 2, "hlc3": (h + l + c) / 3, "ohlc4": (o + h + l + c) / 4, "hlcc4": (h + l + 2 * c) / 4}[ad]
        if ad == "bar_index":
            return k if k >= 0 else NA
        if ad == "last_bar_index":
            return self.n - 1
        if ad in ("time", "time_tradingday"):
            return int(self.zaman_ms[k]) if 0 <= k <= self.i else NA
        if ad == "time_close":
            return int(self.zaman_ms[k] + self.tf_dk * 60_000) if 0 <= k <= self.i else NA
        if ad == "timenow":
            return int(self.zaman_ms[-1])
        if ad in ("year", "month", "dayofmonth", "dayofweek", "hour", "minute", "second", "weekofyear"):
            return self._takvim(ad, k)
        if ad in self.fonksiyonlar:
            raise Desteklenmiyor(f"fonksiyon değer olarak: {ad}")
        if ad in V3_SABIT:
            return ad
        if ad in ("vwap", "tr", "obv", "accdist"):                  # v3/v4 namespace'siz yerleşik seriler
            return self._ta_degisken("ta." + ad) if n == 0 else self._ta_gecmis("ta." + ad, n)
        if ad in ("isintraday", "isdaily", "isweekly", "ismonthly", "isdwm", "isminutes", "isseconds", "period", "multiplier"):
            return self._yerlesik_degisken("timeframe." + ad)
        if ad == "interval":                                          # v2/v3: timeframe.multiplier
            return self._yerlesik_degisken("timeframe.multiplier")
        if ad in ("isconfirmed", "islast", "isfirst", "ishistory", "isrealtime", "isnew"):
            return self._yerlesik_degisken("barstate." + ad)
        raise Desteklenmiyor(f"ad: {ad}")

    def _ta_gecmis(self, ad: str, n: int) -> Any:
        raise Desteklenmiyor(f"{ad}[{n}]")

    def _takvim(self, ad: str, k: int) -> Any:
        if not 0 <= k <= self.i:
            return NA
        if ad == "weekofyear":
            return int(self.df.index[k].tz_convert(self.tz).isocalendar()[1])
        dizi = {"year": self.yil, "month": self.ay, "dayofmonth": self.gun, "dayofweek": self.haftagun, "hour": self.saat,
                "minute": self.dakika_, "second": self.saniye}[ad]
        return int(dizi[k])

    def _gecmis(self, e: A.Subscript) -> Any:
        n = self._deger(e.slice)
        if na(n):
            return NA
        n = int(n)
        if n < 0:            # sabit negatif indeks derlenmez; döngüde oluşan (ör. 1'den -3'e sayan for) yayımlanmış
            return NA        # betiklerde çalışıyor: TradingView hata vermiyor, na kabul edilir
        hedef = e.value
        if isinstance(hedef, A.Name):
            y = self._bul(hedef.id)
            if y is not None:
                if n == 0:
                    return y.deger
                return y.gecmis[-n] if len(y.gecmis) >= n else NA
            return self._yerlesik_seri(hedef.id, n)
        if isinstance(hedef, A.Attribute):
            ad = _nokta(hedef)
            if ad in ("strategy.position_size", "strategy.position_avg_price", "strategy.equity", "strategy.opentrades",
                      "strategy.closedtrades", "strategy.netprofit", "strategy.openprofit", "strategy.wintrades",
                      "strategy.losstrades"):
                return self._ifade_gecmisi(e, n)
        return self._ifade_gecmisi(e, n)

    def _ifade_gecmisi(self, e: A.Subscript, n: int) -> Any:
        """(ifade)[n]: çağrı yerinin kendi kaydı; ifade her bar bu noktada hesaplanır."""
        anahtar = (self.yol, id(e), "__gecmis__")
        kayit = self.durum.get(anahtar)
        if kayit is None:
            kayit = self.durum[anahtar] = {"bar": [], "deger": []}
        v = self._deger(e.value)
        if kayit["bar"] and kayit["bar"][-1] == self.i:
            kayit["deger"][-1] = v
        else:
            kayit["bar"].append(self.i)
            kayit["deger"].append(v)
        if isinstance(v, tuple):
            raise Desteklenmiyor("demet geçmişi")
        hedef_bar = self.i - n
        # Pine: seri geçmişi bar indeksine göredir; ifade her bar hesaplandıysa kayıt bar ile hizalıdır
        if len(kayit["bar"]) > n and kayit["bar"][-1 - n] == hedef_bar:
            return kayit["deger"][-1 - n]
        for b, x in zip(reversed(kayit["bar"]), reversed(kayit["deger"])):
            if b == hedef_bar:
                return x
            if b < hedef_bar:
                break
        return NA

    # ------------------------------------------------------------------ öznitelikler
    def _oznitelik(self, e: A.Attribute) -> Any:
        kok = e
        while isinstance(kok, A.Attribute):
            kok = kok.value
        if isinstance(kok, A.Name) and self._bul(kok.id) is None and kok.id not in self.tipler:
            return self._yerlesik_degisken(_nokta(e))
        nesne = self._deger(e.value)
        if isinstance(nesne, _Nesne):
            return getattr(nesne, e.attr)
        if nesne is None or na(nesne):
            return NA
        raise Desteklenmiyor(f"öznitelik {e.attr} ({type(nesne).__name__})")

    def _yerlesik_degisken(self, ad: str) -> Any:
        c = self.ctx
        s = {
            "strategy.long": LONG, "strategy.short": SHORT,
            "strategy.percent_of_equity": "percent_of_equity", "strategy.fixed": "fixed", "strategy.cash": "cash",
            "strategy.commission.percent": "percent", "strategy.commission.cash_per_contract": "cash_per_contract",
            "strategy.commission.cash_per_order": "cash_per_order",
            "strategy.direction.long": LONG, "strategy.direction.short": SHORT, "strategy.direction.all": 0,
            "strategy.oca.none": "none", "strategy.oca.cancel": "cancel", "strategy.oca.reduce": "reduce",
            "math.pi": math.pi, "math.e": math.e, "math.phi": 1.618033988749895, "math.rphi": 0.618033988749895,
            "syminfo.mintick": self.mintick, "syminfo.tickerid": self.sembol, "syminfo.ticker": self.sembol.split(":")[-1],
            "syminfo.prefix": self.sembol.split(":")[0], "syminfo.timezone": self.tz, "syminfo.pointvalue": 1.0,
            "syminfo.type": "crypto" if self.tz == "UTC" else "stock", "syminfo.root": self.sembol.split(":")[-1],
            "syminfo.currency": _kotasyon(self.sembol), "syminfo.basecurrency": _taban(self.sembol), "syminfo.session": "regular",
            "timeframe.period": tf_metin(self.tf_dk), "timeframe.multiplier": _carpan(self.tf_dk),
            "timeframe.isintraday": self.tf_dk < 1440, "timeframe.isdaily": self.tf_dk % 1440 == 0 and self.tf_dk < 10080,
            "timeframe.isweekly": self.tf_dk % 10080 == 0 and self.tf_dk < 43200, "timeframe.ismonthly": self.tf_dk >= 43200,
            "timeframe.isminutes": self.tf_dk < 1440, "timeframe.isseconds": False, "timeframe.isdwm": self.tf_dk >= 1440,
            "timeframe.isticks": False,
            "barstate.isconfirmed": True, "barstate.ishistory": True, "barstate.isrealtime": False, "barstate.isnew": True,
            "barstate.isfirst": self.i == 0, "barstate.islast": self.i == self.n - 1 if self.df is not None else False,
            "barstate.islastconfirmedhistory": self.i == self.n - 1 if self.df is not None else False,
            "dayofweek.sunday": 1, "dayofweek.monday": 2, "dayofweek.tuesday": 3, "dayofweek.wednesday": 4,
            "dayofweek.thursday": 5, "dayofweek.friday": 6, "dayofweek.saturday": 7,
            "barmerge.lookahead_on": True, "barmerge.lookahead_off": False, "barmerge.gaps_on": True,
            "barmerge.gaps_off": False, "session.regular": "regular", "session.extended": "extended",
            "order.ascending": 1, "order.descending": -1, "na": NA,
        }
        if ad in s:
            return s[ad]
        if ad in DISPLAY:
            return DISPLAY[ad]
        if ad in ("label.all", "line.all", "box.all", "table.all", "linefill.all", "polyline.all"):
            return []
        if ad.startswith("strategy.") and not ad.startswith(("strategy.risk", "strategy.opentrades.", "strategy.closedtrades.")):
            return self._strateji_degisken(ad[9:])
        if ad in ("ta.tr", "ta.obv", "ta.vwap", "ta.accdist", "ta.iii", "ta.nvi", "ta.pvi", "ta.wad", "ta.wvad", "ta.pvt"):
            return self._ta_degisken(ad)
        ns = ad.rsplit(".", 1)[0]
        if ns in SABIT_NS or ad.split(".")[0] in SABIT_NS:
            return ad
        raise Desteklenmiyor(f"ad: {ad}")

    def _strateji_degisken(self, ad: str) -> Any:
        c = self.ctx
        if c is None:
            return 0.0 if ad != "initial_capital" else NA
        kapali = c.kapali
        if ad == "position_size":
            return c.position_size
        if ad == "position_avg_price":
            return c.position_avg_price
        if ad == "equity":
            return c.equity
        if ad == "netprofit":
            return c.netprofit
        if ad == "openprofit":
            return c.openprofit
        if ad == "opentrades":
            return c.opentrades
        if ad == "closedtrades":
            return c.closedtrades
        if ad == "wintrades":
            return sum(1 for t in kapali if t["net"] > 0)
        if ad == "losstrades":
            return sum(1 for t in kapali if t["net"] < 0)
        if ad == "eventrades":
            return sum(1 for t in kapali if t["net"] == 0)
        if ad == "grossprofit":
            return sum(t["net"] for t in kapali if t["net"] > 0)
        if ad == "grossloss":
            return -sum(t["net"] for t in kapali if t["net"] < 0)
        if ad == "initial_capital":
            return c.a.initial_capital
        if ad == "max_drawdown":
            self.zirve = max(self.zirve, c.equity)
            self.maks_dd = max(self.maks_dd, self.zirve - c.equity)
            return self.maks_dd
        if ad == "max_drawdown_percent":
            self.zirve = max(self.zirve, c.equity)
            self.maks_dd_yuzde = max(getattr(self, "maks_dd_yuzde", 0.0), (self.zirve - c.equity) / self.zirve * 100)
            return self.maks_dd_yuzde
        if ad == "netprofit_percent":
            return c.netprofit / c.a.initial_capital * 100
        if ad == "openprofit_percent":
            return c.openprofit / c.a.initial_capital * 100
        if ad == "position_entry_name":
            return c.acik[-1].entry_id if c.acik else ""
        if ad == "cash":
            return "cash"
        raise Desteklenmiyor(f"strategy.{ad}")

    def _ta_degisken(self, ad: str) -> Any:
        anahtar = ("__tavar__", ad)
        nesne = self.durum.get(anahtar)
        h, l, c, v = self.h[self.i], self.l[self.i], self.c[self.i], self.v[self.i]
        if ad == "ta.tr":
            if self.i == 0:
                return NA
            return max(h - l, abs(h - self.c[self.i - 1]), abs(l - self.c[self.i - 1]))
        if nesne is None:
            nesne = self.durum[anahtar] = {"ta.obv": T.Obv, "ta.vwap": T.Vwap}.get(ad, lambda: T.HacimDegiskeni(ad))()
            if nesne is None:
                raise Desteklenmiyor(ad)
        son = self.durum.get(anahtar + ("bar",))
        if son is not None and son[0] == self.i:
            return son[1]
        if isinstance(nesne, T.HacimDegiskeni):
            x = nesne(self.o[self.i], h, l, c, v)
        else:
            x = nesne(c, v) if ad == "ta.obv" else nesne((h + l + c) / 3, v, int(self.gun_kodu[self.i]))
        self.durum[anahtar + ("bar",)] = (self.i, x)
        return x

    # ------------------------------------------------------------------ çağrılar
    def _cagir(self, e: A.Call) -> Any:
        f = e.func
        if isinstance(f, A.Specialize):
            f = f.value
        if isinstance(f, A.Name):
            ad = f.id
            if ad in self.fonksiyonlar:
                return self._kullanici(e, self.fonksiyonlar[ad], None)
            ad = V4_ADLAR.get(ad, ad)
            return self._yerlesik(ad, e)
        if isinstance(f, A.Attribute):
            kok = f
            while isinstance(kok, A.Attribute):
                kok = kok.value
            kullanici = isinstance(kok, A.Name) and (self._bul(kok.id) is not None)
            if not kullanici and isinstance(kok, A.Name) and kok.id in self.tipler and f.attr in ("new", "copy"):
                return self._tip_yeni(kok.id, e) if f.attr == "new" else self._tip_kopya(e)
            if not kullanici and isinstance(kok, A.Name) and kok.id in self.eksik_kutuphane:
                raise Desteklenmiyor(f"import {self.eksik_kutuphane[kok.id]}")
            if not kullanici and isinstance(f.value, (A.Name, A.Attribute)):
                nokta = _nokta(f)
                if nokta in self.fonksiyonlar:
                    return self._kullanici(e, self.fonksiyonlar[nokta], None)
                tip = _nokta(f.value)
                if tip in self.tipler and f.attr in ("new", "copy"):
                    return self._tip_yeni(tip, e) if f.attr == "new" else self._tip_kopya(e)
            if not kullanici and not (isinstance(f.value, A.Call) or isinstance(f.value, A.Subscript)):
                return self._yerlesik(_nokta(f), e)
            nesne = self._deger(f.value)
            return self._yontem(nesne, f.attr, e)
        raise Desteklenmiyor(f"çağrı {type(f).__name__}")

    def _yontem(self, nesne, ad: str, e: A.Call) -> Any:
        if ad in self.yontemler:
            return self._kullanici(e, self.yontemler[ad], nesne)
        if isinstance(nesne, list):
            return self._yerlesik("array." + ad, e, on_arg=nesne)
        if isinstance(nesne, dict):
            return self._yerlesik("map." + ad, e, on_arg=nesne)
        if isinstance(nesne, _Matris):
            return self._yerlesik("matrix." + ad, e, on_arg=nesne)
        if isinstance(nesne, _Cizim):
            return self._yerlesik(f"{nesne.tur}.{ad}", e, on_arg=nesne)
        if nesne is None or (isinstance(nesne, float) and na(nesne)):   # çizim nesnesi (label/line/box) ya da na
            if ad.startswith("get_"):
                raise Desteklenmiyor(f"çizim nesnesinden okuma: {ad}")
            return None
        if isinstance(nesne, _Nesne) and ad == "copy":
            return _Nesne(nesne._tip, nesne._alan)
        raise Desteklenmiyor(f"yöntem {ad} ({type(nesne).__name__})")

    def _argumanlar(self, e: A.Call, on_arg=None) -> tuple[list, dict]:
        konum, adli = [], {}
        if on_arg is not None:
            konum.append(on_arg)
        for a in e.args:
            v = self._deger(a.value)
            if a.name:
                adli[a.name] = v
            else:
                konum.append(v)
        return konum, adli

    def _kullanici(self, e: A.Call, adaylar: list[_Fonksiyon], nesne) -> Any:
        konum, adli = self._argumanlar(e, on_arg=nesne if nesne is not None else None)
        fn = next((a for a in adaylar if _uyar(a.dugum, len(konum), adli)), adaylar[-1])
        d = fn.dugum
        eski_kapsam, eski_yol = self.kapsam, self.yol
        self.yol = self.yol + (id(e),)
        self.kapsam = [self.kapsam[0], {}]
        try:
            for k, p in enumerate(d.args):
                if k < len(konum):
                    v = konum[k]
                elif p.name in adli:
                    v = adli[p.name]
                elif p.default is not None:
                    v = self._deger(p.default)
                else:
                    v = NA
                y = self._yuva(p.name, d, False)
                y.deger, y.atandi = v, True
            return self._govde(d.body, yeni_kapsam=False)
        finally:
            self.kapsam, self.yol = eski_kapsam, eski_yol

    def _tip_yeni(self, tip: str, e: A.Call) -> _Nesne:
        konum, adli = self._argumanlar(e)
        alanlar = {}
        for k, d in enumerate(x for x in self.tipler[tip].body if isinstance(x, A.Assign)):
            ad = d.target.id
            if k < len(konum):
                alanlar[ad] = konum[k]
            elif ad in adli:
                alanlar[ad] = adli[ad]
            else:
                alanlar[ad] = self._deger(d.value) if d.value is not None else NA
        return _Nesne(tip, alanlar)

    def _tip_kopya(self, e: A.Call) -> _Nesne:
        konum, _ = self._argumanlar(e)
        n = konum[0]
        return _Nesne(n._tip, n._alan)

    def _durum(self, e, fabrika):
        anahtar = (self.yol, id(e))
        n = self.durum.get(anahtar)
        if n is None:
            n = self.durum[anahtar] = fabrika()
        return n

    # ------------------------------------------------------------------ yerleşikler
    def _yerlesik(self, ad: str, e: A.Call, on_arg=None) -> Any:
        if ad == "request.security":
            return self._security(e)
        if ad == "request.security_lower_tf":
            return self._alt_dilim(e, dizi=True)
        if ad in ("request.financial", "request.quandl", "request.earnings",
                  "request.dividends", "request.splits", "request.economic", "request.seed", "request.currency_rate"):
            raise Desteklenmiyor(ad)
        konum, adli = self._argumanlar(e, on_arg)
        if ad.split(".")[0] in _Cizim.ALANLAR and ad.count(".") == 1:
            return self._cizim(ad, konum, adli)
        if ad in GORSEL_AD or ad.split(".")[0] in GORSEL_NS or ad.startswith("color.") or ad in ("color",):
            if ad.split(".")[-1].startswith("get_") and ad.split(".")[0] in GORSEL_NS:
                raise Desteklenmiyor(f"çizimden okuma: {ad}")
            return None
        if ad.startswith("strategy"):
            return self._strateji(ad, konum, adli)
        if ad.startswith("input"):
            return self._girdi(ad, konum, adli, e)
        if ad.startswith("ta."):
            return self._ta(ad, konum, adli, e)
        if ad == "math.sum":
            x = _bagla(["source", "length"], konum, adli)
            return self._durum(e, T.Toplam)(x["source"], x["length"])
        if ad.startswith("math."):
            return _matematik(ad[5:], konum, adli, self)
        if ad.startswith("array."):
            return _dizi(ad[6:], konum, adli)
        if ad.startswith("map."):
            return _harita(ad[4:], konum, adli)
        if ad.startswith("matrix."):
            return _matris(ad[7:], konum, adli)
        if ad.startswith("str."):
            return _metin(ad[4:], konum, adli)
        if ad == "na":
            return na(konum[0]) if konum else True
        if ad == "nz":
            x = konum[0]
            yedek = konum[1] if len(konum) > 1 else adli.get("replacement", 0)
            return yedek if na(x) else x
        if ad == "fixnan":
            st = self._durum(e, lambda: {"son": NA})
            if not na(konum[0]):
                st["son"] = konum[0]
            return st["son"]
        if ad == "iff":
            return konum[1] if _dogru(konum[0]) else konum[2]
        if ad == "int":
            return NA if na(konum[0]) else int(konum[0])
        if ad == "float":
            return NA if konum[0] is None else float(konum[0])
        if ad == "bool":
            return _dogru(konum[0])
        if ad == "string":
            return str(konum[0])
        if ad in ("time", "time_close"):
            return self._zaman(ad, konum, adli)
        if ad in ("year", "month", "dayofmonth", "dayofweek", "hour", "minute", "second", "weekofyear"):
            return self._takvim_ms(ad, konum[0] if konum else adli.get("time"), konum[1] if len(konum) > 1 else adli.get("timezone"))
        if ad == "timestamp":
            return self._zaman_damgasi(konum, adli)
        if ad == "timeframe.in_seconds":
            tf = konum[0] if konum else adli.get("timeframe", tf_metin(self.tf_dk))
            return tf_dakika(tf) * 60
        if ad == "timeframe.change":
            tf = tf_dakika(konum[0] if konum else adli["timeframe"])
            if self.i == 0:
                return True
            b, _ = _kova(self.df.index[self.i - 1:self.i + 1], tf, self.tz)
            return bool(b[0] != b[1])
        if ad == "runtime.error":
            raise PineHatasi(f"runtime.error: {konum[0] if konum else ''}")
        if ad in ("ticker.heikinashi", "heikinashi"):
            sem = str(konum[0] if konum else adli.get("symbol", self.sembol))
            return sem if sem.startswith(HA_ONEK) else HA_ONEK + sem      # HA alt koşusunda tickerid zaten HA
        if ad == "ticker.new" or ad.startswith("ticker."):
            if ad == "ticker.standard" or ad == "ticker.modify":
                return konum[0] if konum else self.sembol
            raise Desteklenmiyor(ad)
        if ad == "max":
            return _matematik("max", konum, adli, self)
        raise Desteklenmiyor(ad)

    def _cizim(self, ad: str, konum, adli) -> Any:
        tur, is_ = ad.split(".")
        alanlar = _Cizim.ALANLAR[tur]
        if is_ == "new":
            if konum and isinstance(konum[0], _Nesne):  # chart.point imzası
                raise Desteklenmiyor(f"{ad}(chart.point)")
            b = _bagla(list(alanlar), konum, adli)
            return _Cizim(tur, {k: b.get(k, NA) for k in alanlar})
        nesne = konum[0] if konum else adli.get("id")
        if not isinstance(nesne, _Cizim):               # na kimlik: set no-op, get na
            return NA if is_.startswith("get_") else None
        a = nesne.alan
        if is_ == "copy":
            return _Cizim(tur, dict(a))
        if is_ == "get_price":
            x = konum[1] if len(konum) > 1 else adli["x"]
            if a["x2"] == a["x1"]:
                return a["y1"]
            return a["y1"] + (a["y2"] - a["y1"]) * (x - a["x1"]) / (a["x2"] - a["x1"])
        if is_.startswith("get_") and is_[4:] in alanlar:
            return a[is_[4:]]
        cift = {"set_xy1": ("x1", "y1"), "set_xy2": ("x2", "y2"), "set_lefttop": ("left", "top"),
                "set_rightbottom": ("right", "bottom"), "set_xy": ("x", "y")}
        if is_ in cift:
            a[cift[is_][0]], a[cift[is_][1]] = konum[1], konum[2]
            return None
        if is_.startswith("set_") and is_[4:] in alanlar:
            a[is_[4:]] = konum[1] if len(konum) > 1 else next(iter(v for k, v in adli.items() if k != "id"))
            return None
        if is_.startswith("get_"):
            raise Desteklenmiyor(f"çizimden okuma: {ad}")
        return None                                     # renk, stil, delete ...: görsel

    def _girdi(self, ad: str, konum, adli, e) -> Any:
        anahtar = adli.get("title") or (konum[1] if len(konum) > 1 and isinstance(konum[1], str) else None)
        if anahtar is not None and anahtar in self.girdiler:
            return self.girdiler[anahtar]
        v = adli["defval"] if "defval" in adli else (konum[0] if konum else NA)
        if ad == "input.int" or ad == "input.integer":
            return int(v) if not na(v) else v
        return v

    # ---- strategy.*
    def _strateji(self, ad: str, konum, adli) -> Any:
        if ad == "strategy":
            return None
        c = self.ctx
        if self.guvenlik_modu:
            return None
        if c is None:
            raise Desteklenmiyor("strateji emri bağlam dışı")
        if not _dogru(adli.get("when", True)):
            return None
        if ad.startswith("strategy.risk."):
            return self._risk(ad[14:], konum, adli)
        if ad.startswith("strategy.opentrades.") or ad.startswith("strategy.closedtrades."):
            return self._islem_bilgi(ad, konum, adli)
        if (self.durdu or self.gun_durdu == self.risk_gun) and ad in ("strategy.entry", "strategy.order"):
            return None
        if ad == "strategy.entry":
            b = _bagla(["id", "direction", "qty", "limit", "stop", "oca_name", "oca_type", "comment"], konum, adli)
            yon = b["direction"]
            if "long" in adli:                                    # v2-v4: long=true/false
                yon = adli["long"]
            if isinstance(yon, bool):
                yon = LONG if yon else SHORT
            if self.risk_yon is not None and yon != self.risk_yon:
                c.close_all()                                     # Pine: izin verilmeyen yöndeki giriş çıkış olur
                return None
            c.entry(str(b["id"]), yon, qty=_sayi(b.get("qty")), limit=_sayi(b.get("limit")), stop=_sayi(b.get("stop")),
                    oca=self._oca(b))
            return None
        if ad == "strategy.order":
            b = _bagla(["id", "direction", "qty", "limit", "stop", "oca_name", "oca_type", "comment"], konum, adli)
            yon = b["direction"]
            if "long" in adli:
                yon = adli["long"]
            if isinstance(yon, bool):
                yon = LONG if yon else SHORT
            c.order(str(b["id"]), yon, qty=_sayi(b.get("qty")), limit=_sayi(b.get("limit")), stop=_sayi(b.get("stop")),
                    oca=self._oca(b))
            return None
        if ad == "strategy.default_entry_qty":
            fiyat = konum[0] if konum else adli["fill_price"]
            return c._varsayilan_adet(float(fiyat))
        if ad == "strategy.exit":
            b = _bagla(["id", "from_entry", "qty", "qty_percent", "profit", "limit", "loss", "stop", "trail_price",
                        "trail_points", "trail_offset", "oca_name", "comment"], konum, adli)
            fe = b.get("from_entry")
            c.exit(str(b["id"]), from_entry=None if fe in (None, "") or na(fe) else str(fe), qty=_sayi(b.get("qty")),
                   qty_percent=_sayi(b.get("qty_percent")), profit=_sayi(b.get("profit")), limit=_sayi(b.get("limit")),
                   loss=_sayi(b.get("loss")), stop=_sayi(b.get("stop")), trail_price=_sayi(b.get("trail_price")),
                   trail_points=_sayi(b.get("trail_points")), trail_offset=_sayi(b.get("trail_offset")))
            return None
        if ad == "strategy.close":
            if self.surum < 5:
                b = _bagla(["id", "when", "comment", "qty", "qty_percent"], konum, adli, {"when": True})
                if not _dogru(b["when"]):
                    return None
            else:
                b = _bagla(["id", "comment", "qty", "qty_percent", "alert_message", "immediately"], konum, adli)
            c.close(str(b["id"]), qty=_sayi(b.get("qty")), qty_percent=_sayi(b.get("qty_percent")),
                    immediately=_dogru(b.get("immediately", False)))
            return None
        if ad == "strategy.close_all":
            if self.surum < 5 and konum and not _dogru(konum[0]):
                return None
            c.close_all(immediately=_dogru(adli.get("immediately", False)))
            return None
        if ad == "strategy.cancel":
            if self.surum < 5 and len(konum) > 1 and not _dogru(konum[1]):
                return None
            c.cancel(str(konum[0] if konum else adli["id"]))
            return None
        if ad == "strategy.cancel_all":
            if self.surum < 5 and konum and not _dogru(konum[0]):
                return None
            c.cancel_all()
            return None
        raise Desteklenmiyor(ad)

    def _oca(self, b: dict) -> str | None:
        ad = b.get("oca_name")
        if ad in (None, "") or na(ad):
            return None
        tip = b.get("oca_type") or "none"
        if tip == "reduce":
            raise Desteklenmiyor("oca_type reduce")
        return str(ad) if tip == "cancel" else None

    def _risk(self, ad: str, konum, adli):
        if ad == "allow_entry_in":
            v = konum[0] if konum else adli["value"]
            self.risk_yon = None if v == 0 else v
            return None
        if ad == "max_drawdown":
            self.risk_maks_dd = (float(konum[0] if konum else adli["value"]),
                                 konum[1] if len(konum) > 1 else adli.get("type", "percent_of_equity"))
            return None
        if ad == "max_intraday_loss":
            self.risk_gun_zarar = (float(konum[0] if konum else adli["value"]),
                                   konum[1] if len(konum) > 1 else adli.get("type", "percent_of_equity"))
            return None
        if ad == "max_cons_loss_days":
            self.risk_ardisik = int(konum[0] if konum else adli["count"])
            return None
        if ad == "max_intraday_filled_orders":
            self.risk_gun_emir = int(konum[0] if konum else adli["count"])
            return None
        raise Desteklenmiyor(f"strategy.risk.{ad}")

    def _islem_bilgi(self, ad: str, konum, adli):
        c = self.ctx
        k = int(konum[0] if konum else adli.get("trade_num", 0))
        if ad.startswith("strategy.opentrades."):
            alan = ad[len("strategy.opentrades."):]
            if not 0 <= k < len(c.acik):
                return NA
            t = c.acik[k]
            bilgi = {"entry_price": t.fiyat, "entry_bar_index": t.bar, "size": t.yon * t.adet, "entry_id": t.entry_id,
                     "entry_time": int(self.zaman_ms[t.bar]), "profit": t.yon * (self.c[self.i] - t.fiyat) * t.adet,
                     "commission": t.komisyon}
            return bilgi[alan] if alan in bilgi else _yok(ad)
        alan = ad[len("strategy.closedtrades."):]
        if not 0 <= k < len(c.kapali):
            return NA
        t = c.kapali[k]
        bilgi = {"entry_price": t["giris_fiyat"], "exit_price": t["cikis_fiyat"], "profit": t["net"],
                 "entry_bar_index": t["giris_bar"], "exit_bar_index": t["cikis_bar"], "size": t["yon"] * t["adet"],
                 "entry_id": t["entry_id"], "exit_id": t["exit_id"], "commission": t["komisyon"],
                 "entry_time": int(self.zaman_ms[t["giris_bar"]]), "exit_time": int(self.zaman_ms[t["cikis_bar"]]),
                 "profit_percent": t["net"] / (t["giris_fiyat"] * t["adet"]) * 100 if t["giris_fiyat"] * t["adet"] else NA}
        return bilgi[alan] if alan in bilgi else _yok(ad)

    # ---- ta.*
    def _ta(self, ad: str, konum, adli, e) -> Any:
        k = ad[3:]
        h, l, c, v = self.h[self.i], self.l[self.i], self.c[self.i], self.v[self.i]

        def b(*adlar, **vars_):
            return _bagla(list(adlar), konum, adli, vars_)

        if k == "sma":
            x = b("source", "length")
            return self._durum(e, T.Sma)(x["source"], x["length"])
        if k == "ema":
            x = b("source", "length")
            return self._durum(e, T.Ema)(x["source"], x["length"])
        if k == "rma":
            x = b("source", "length")
            return self._durum(e, T.Rma)(x["source"], x["length"])
        if k == "wma":
            x = b("source", "length")
            return self._durum(e, T.Wma)(x["source"], x["length"])
        if k == "vwma":
            x = b("source", "length")
            return self._durum(e, T.Vwma)(x["source"], x["length"], v)
        if k == "hma":
            x = b("source", "length")
            return self._durum(e, T.Hma)(x["source"], x["length"])
        if k == "alma":
            x = b("series", "length", "offset", "sigma", "floor", floor=False)
            return self._durum(e, T.Alma)(x["series"], x["length"], x["offset"], x["sigma"], x["floor"])
        if k == "swma":
            x = b("source")
            w = self._durum(e, T.Pencere)
            w.ekle(x["source"])
            s = w.son(4)
            return NA if s is None or any(na(q) for q in s) else (s[0] + 2 * s[1] + 2 * s[2] + s[3]) / 6
        if k == "atr":
            x = b("length")
            return self._durum(e, T.Atr)(x["length"], h, l, c)
        if k == "tr":
            x = b("handle_na", handle_na=False)
            return self._durum(e, T.Tr)(h, l, c, x["handle_na"])
        if k == "rsi":
            x = b("source", "length")
            return self._durum(e, T.Rsi)(x["source"], x["length"])
        if k in ("crossover", "crossunder", "cross"):
            x = b("source1", "source2")
            return self._durum(e, lambda: T.Kesisim({"crossover": 1, "crossunder": -1, "cross": 0}[k]))(x["source1"], x["source2"])
        if k in ("highest", "lowest"):
            if len(konum) + len(adli) == 1:
                x = {"source": h if k == "highest" else l, "length": konum[0] if konum else adli["length"]}
            else:
                x = b("source", "length")
            return self._durum(e, lambda: T.EnYuksek(1 if k == "highest" else -1))(x["source"], x["length"])
        if k in ("highestbars", "lowestbars"):
            if len(konum) + len(adli) == 1:
                x = {"source": h if k == "highestbars" else l, "length": konum[0] if konum else adli["length"]}
            else:
                x = b("source", "length")
            return self._durum(e, lambda: T.EnYuksekBar(1 if k == "highestbars" else -1))(x["source"], x["length"])
        if k == "change":
            x = b("source", "length", length=1)
            return self._durum(e, T.Change)(x["source"], x["length"])
        if k == "mom":
            x = b("source", "length")
            once, simdi = self._durum(e, T.Gecmis)(x["source"], x["length"])
            return simdi - once
        if k == "roc":
            x = b("source", "length")
            return self._durum(e, T.Roc)(x["source"], x["length"])
        if k == "stdev":
            x = b("source", "length", "biased", biased=True)
            return self._durum(e, T.Stdev)(x["source"], x["length"], x["biased"])
        if k == "variance":
            x = b("source", "length", "biased", biased=True)
            return self._durum(e, T.Variance)(x["source"], x["length"], x["biased"])
        if k == "dev":
            x = b("source", "length")
            return self._durum(e, T.Dev)(x["source"], x["length"])
        if k == "median":
            x = b("source", "length")
            return self._durum(e, T.Median)(x["source"], x["length"])
        if k == "dmi":
            x = b("diLength", "adxSmoothing")
            return self._durum(e, T.Dmi)(x["diLength"], x["adxSmoothing"], h, l, c)
        if k == "macd":
            x = b("source", "fastlen", "slowlen", "siglen")
            return self._durum(e, T.Macd)(x["source"], x["fastlen"], x["slowlen"], x["siglen"])
        if k == "stoch":
            x = b("source", "high", "low", "length")
            return self._durum(e, T.Stoch)(x["source"], x["high"], x["low"], x["length"])
        if k == "supertrend":
            x = b("factor", "atrPeriod")
            return self._durum(e, T.Supertrend)(x["factor"], x["atrPeriod"], h, l, c)
        if k in ("pivothigh", "pivotlow"):
            if len(konum) + len(adli) == 2:
                x = {"source": h if k == "pivothigh" else l, "leftbars": konum[0] if konum else adli["leftbars"],
                     "rightbars": konum[1] if len(konum) > 1 else adli["rightbars"]}
            else:
                x = b("source", "leftbars", "rightbars")
            return self._durum(e, lambda: T.Pivot(1 if k == "pivothigh" else -1))(x["source"], x["leftbars"], x["rightbars"])
        if k == "barssince":
            x = b("condition")
            return self._durum(e, T.Barssince)(_dogru(x["condition"]))
        if k == "valuewhen":
            x = b("condition", "source", "occurrence", occurrence=0)
            return self._durum(e, T.Valuewhen)(_dogru(x["condition"]), x["source"], x["occurrence"])
        if k == "linreg":
            x = b("source", "length", "offset", offset=0)
            return self._durum(e, T.Linreg)(x["source"], x["length"], x["offset"])
        if k == "cum":
            x = b("source")
            return self._durum(e, T.Cum)(x["source"])
        if k == "percentrank":
            x = b("source", "length")
            return self._durum(e, T.Percentrank)(x["source"], x["length"])
        if k == "cci":
            x = b("source", "length")
            return self._durum(e, T.Cci)(x["source"], x["length"])
        if k == "mfi":
            x = b("series", "length")
            return self._durum(e, T.Mfi)(x["series"], x["length"], v)
        if k == "bb":
            x = b("series", "length", "mult")
            return self._durum(e, T.Bb)(x["series"], x["length"], x["mult"])
        if k == "bbw":
            x = b("series", "length", "mult")
            m, u, d = self._durum(e, T.Bb)(x["series"], x["length"], x["mult"])
            return (u - d) / m * 100 if m else NA
        if k == "kc":
            x = b("series", "length", "mult", "useTrueRange", useTrueRange=True)
            st = self._durum(e, lambda: (T.Ema(), T.Ema(), T.Tr()))
            orta = st[0](x["series"], x["length"])
            aralik = st[2](h, l, c) if x["useTrueRange"] else h - l
            r = st[1](aralik, x["length"])
            return orta, orta + x["mult"] * r, orta - x["mult"] * r
        if k in ("rising", "falling"):
            x = b("source", "length")
            return self._durum(e, lambda: T.Monoton(1 if k == "rising" else -1))(x["source"], x["length"])
        if k == "sar":
            x = b("start", "inc", "max")
            return self._durum(e, T.Sar)(x["start"], x["inc"], x["max"], h, l, c)
        if k == "vwap":
            x = b("source", "anchor", "stdev_mult", source=(h + l + c) / 3)
            carpan = x.get("stdev_mult")
            return self._durum(e, T.Vwap)(x["source"], v, int(self.gun_kodu[self.i]), x.get("anchor"),
                                          None if carpan is None or na(carpan) else float(carpan))
        if k == "correlation":
            x = b("source1", "source2", "length")
            return self._durum(e, T.Korelasyon)(x["source1"], x["source2"], x["length"])
        if k == "wpr":
            x = b("length")
            return self._durum(e, T.Wpr)(x["length"], h, l, c)
        if k == "cmo":
            x = b("series", "length")
            st = self._durum(e, lambda: {"g": T.Gecmis(), "u": T.Toplam(), "d": T.Toplam()})
            once, simdi = st["g"](x["series"], 1)
            m = simdi - once
            u = st["u"](max(m, 0.0) if not na(m) else NA, x["length"])
            d = st["d"](max(-m, 0.0) if not na(m) else NA, x["length"])
            return 100 * (u - d) / (u + d) if (u + d) else NA
        if k in ("percentile_nearest_rank", "percentile_linear_interpolation"):
            x = b("source", "length", "percentage")
            w = self._durum(e, T.Pencere)
            w.ekle(x["source"])
            s_ = w.son(x["length"])
            if s_ is None or any(na(q) for q in s_):
                return NA
            s_ = sorted(s_)
            yuzde = float(x["percentage"])
            if k == "percentile_nearest_rank":
                sira = max(int(math.ceil(yuzde / 100 * len(s_))), 1)
                return s_[min(sira, len(s_)) - 1]
            konum_ = yuzde / 100 * (len(s_) - 1)
            alt = int(math.floor(konum_))
            ust = min(alt + 1, len(s_) - 1)
            return s_[alt] + (s_[ust] - s_[alt]) * (konum_ - alt)
        if k == "tsi":
            x = b("source", "short_length", "long_length")
            st = self._durum(e, lambda: {"g": T.Gecmis(), "a1": T.Ema(), "a2": T.Ema(), "b1": T.Ema(), "b2": T.Ema()})
            once, simdi = st["g"](x["source"], 1)
            m = simdi - once
            pay = st["a2"](st["a1"](m, x["long_length"]), x["short_length"])
            payda = st["b2"](st["b1"](abs(m) if not na(m) else NA, x["long_length"]), x["short_length"])
            return pay / payda if payda else NA
        raise Desteklenmiyor(ad)

    # ---- zaman
    def _zaman(self, ad: str, konum, adli) -> Any:
        tf = konum[0] if konum else adli.get("timeframe", "")
        oturum = konum[1] if len(konum) > 1 else adli.get("session")
        tz = konum[2] if len(konum) > 2 else adli.get("timezone", self.tz)
        dk = tf_dakika(tf) if tf else self.tf_dk
        t = int(self.zaman_ms[self.i])
        if dk != self.tf_dk:
            b, s = _kova(self.df.index[self.i:self.i + 1], dk, self.tz)
            t = int(b[0] // 1_000_000) if ad == "time" else int(s[0] // 1_000_000)
        elif ad == "time_close":
            t += self.tf_dk * 60_000
        if oturum:
            if not _oturumda(self.df.index[self.i], oturum, tz or self.tz):
                return NA
        return t

    def _takvim_ms(self, ad: str, t, tz) -> Any:
        if t is None:
            return self._takvim(ad, self.i)
        if na(t):
            return NA
        from zoneinfo import ZoneInfo
        bolge = _tz(tz) if tz else self.tz
        d = datetime.fromtimestamp(int(t) / 1000, tz=ZoneInfo(bolge) if isinstance(bolge, str) else bolge)
        if ad == "dayofweek":
            return (d.weekday() + 1) % 7 + 1
        if ad == "weekofyear":
            return int(d.isocalendar()[1])
        return {"year": d.year, "month": d.month, "dayofmonth": d.day, "hour": d.hour, "minute": d.minute,
                "second": d.second}[ad]

    def _zaman_damgasi(self, konum, adli) -> Any:
        if konum and isinstance(konum[0], str) and len(konum) == 1:
            ts = pd.Timestamp(konum[0].replace("+0000", "").strip())
            if ts.tzinfo is None:
                ts = ts.tz_localize(self.tz)
            return int(ts.tz_convert("UTC").value // 1_000_000)
        tz = self.tz
        if konum and isinstance(konum[0], str):
            tz, konum = konum[0], konum[1:]
        tz = adli.get("timezone", tz)
        parca = list(konum) + [adli.get(k) for k in ("year", "month", "day", "hour", "minute", "second")[len(konum):]]
        y, m, g, s, d, sn = [(0 if p is None else p) for p in (parca + [0] * 6)[:6]]
        if any(na(p) for p in (y, m, g)):
            return NA
        from zoneinfo import ZoneInfo
        yil, ay = int(y) + (int(m) - 1) // 12, (int(m) - 1) % 12 + 1
        yil = min(max(yil, 1), 9998)
        bolge = _tz(tz)
        ts = datetime(yil, ay, 1, tzinfo=ZoneInfo(bolge) if isinstance(bolge, str) else bolge) + timedelta(days=int(g) - 1, hours=int(s), minutes=int(d),
                                                                      seconds=int(sn))
        return int(ts.timestamp() * 1000)

    # ---- request.security
    def _security(self, e: A.Call) -> Any:
        adlar = ["symbol", "timeframe", "expression", "gaps", "lookahead", "ignore_invalid_symbol", "currency"]
        dugumler: dict[str, Any] = {}
        for k, a in enumerate(e.args):
            dugumler[a.name or adlar[k]] = a.value
        sembol = self._deger(dugumler["symbol"])
        tf = self._deger(dugumler["timeframe"])
        lookahead = _dogru(self._deger(dugumler["lookahead"])) if "lookahead" in dugumler else False
        gaps = _dogru(self._deger(dugumler["gaps"])) if "gaps" in dugumler else False
        kendi = {self.sembol, self.sembol.split(":")[-1], "", None}
        dk = tf_dakika(tf) if tf else self.tf_dk
        ifade = dugumler["expression"]
        if sembol not in kendi and isinstance(sembol, str) and sembol.startswith(HA_ONEK) and sembol[len(HA_ONEK):] in kendi:
            if self.guvenlik_modu:
                return NA
            return self._dis_sembol(e, str(sembol), max(dk, self.tf_dk) if dk else self.tf_dk, lookahead, gaps)
        if sembol not in kendi:
            if self.guvenlik_modu:      # başka sembolün ön koşusundaki ikinci dış sembol: değeri orada gerekmez
                return NA
            return self._dis_sembol(e, str(sembol), max(dk, self.tf_dk) if dk else self.tf_dk, lookahead, gaps)
        if dk == self.tf_dk or dk == 0:
            v = self._deger(ifade)
            if self.guvenlik_modu:
                self.guvenlik_kayit.setdefault(id(e), {})[self.i] = v
            return v
        if dk < self.tf_dk:
            if self.guvenlik_modu:      # başka bir dilimin ön koşusu: bu çağrının değeri orada gerekmez
                return NA
            return self._alt_dilim(e, dizi=False)
        anahtar = tf_metin(dk)
        g = self.guvenlik.get(anahtar)
        if g is None:
            g = self.guvenlik[anahtar] = self._guvenlik_kur(dk)
        kayit = g["yorum"].guvenlik_kayit.get(id(e))
        if kayit is None:
            raise Desteklenmiyor("request.security ifadesi yüksek dilimde hesaplanamadı")
        k_icinde = int(g["harita"][self.i])
        if lookahead:
            v = kayit.get(k_icinde, NA)
            yeni = self.i == 0 or int(g["harita"][self.i - 1]) != k_icinde
        else:
            k_kapali = int(g["kapali"][self.i])
            v = kayit.get(k_kapali, NA) if k_kapali >= 0 else NA
            yeni = self.i == 0 or int(g["kapali"][self.i - 1]) != k_kapali
        if gaps and not yeni:
            return NA
        return v

    def _dis_sembol(self, e: A.Call, sembol: str, dk: int, lookahead: bool, gaps: bool) -> Any:
        """request.security(başka sembol): o sembolün kendi barlarında betik koşulur, ifade değeri kaydedilir; grafik
        barına, kapanışı grafik barı kapanışından sonra olmayan son dış bar verilir (lookahead_off)."""
        anahtar = ("dis", sembol, dk)
        g = self.guvenlik.get(anahtar)
        if g is None:
            if sembol.startswith(HA_ONEK):              # Heikin Ashi: kendi barlarından (yüksek dilimde önce birleştirilir)
                df2 = heikin_ashi(self.df if dk == self.tf_dk else self._birlestir(dk)[0])
            else:
                df2 = self.veri_saglayici(sembol, dk) if self.veri_saglayici is not None else None
            if df2 is None or df2.empty:
                raise Desteklenmiyor(f"request.security başka sembol, veri yok ({sembol})")
            y = Yorumlayici(self.p, df2, tf_dk=dk, sembol=sembol, tz=self.tz, mintick=self.mintick, girdiler=self.girdiler,
                            guvenlik_modu=True)
            y.surum = self.surum
            for k in range(len(df2)):
                y.adim(None, k)
            bas = df2.index.asi8
            bitis = bas + dk * 60_000_000_000
            grafik_bas = self.df.index.asi8
            grafik_kapanis = grafik_bas + self.tf_dk * 60_000_000_000
            g = self.guvenlik[anahtar] = {
                "yorum": y,
                "kapali": np.searchsorted(bitis, grafik_kapanis, side="right") - 1,
                "harita": np.searchsorted(bas, grafik_bas, side="right") - 1,
            }
        kayit = g["yorum"].guvenlik_kayit.get(id(e), {})
        k = int((g["harita"] if lookahead else g["kapali"])[self.i])
        onceki = int((g["harita"] if lookahead else g["kapali"])[self.i - 1]) if self.i > 0 else -2
        v = kayit.get(k, NA) if k >= 0 else NA
        if gaps and k == onceki:
            return NA
        return v

    def _alt_dilim(self, e: A.Call, dizi: bool) -> Any:
        """Düşük dilim: betik kendi sembolünün `dk` dakikalık barlarında koşulur. security_lower_tf grafik barının içindeki
        tüm alt bar değerlerini (dizi), security ise sonuncusunu verir (geçmiş barlarda TradingView davranışı)."""
        adlar = ["symbol", "timeframe", "expression"]
        dugumler = {(a.name or adlar[k]): a.value for k, a in enumerate(e.args)}
        sembol = str(self._deger(dugumler["symbol"]) or self.sembol)
        dk = tf_dakika(self._deger(dugumler["timeframe"]))
        if self.guvenlik_modu:          # alt dilimin kendi koşusu: ifade değeri kaydedilir
            if dk != self.tf_dk:
                return [] if dizi else NA
            v = self._deger(dugumler["expression"])
            self.guvenlik_kayit.setdefault(id(e), {})[self.i] = v
            if not dizi:
                return v
            return tuple([x] for x in v) if isinstance(v, tuple) else [v]
        if dk >= self.tf_dk:
            if dizi:                    # alt dilim grafik diliminden büyük değilse: tek elemanlı dizi
                return [self._deger(dugumler["expression"])]
            raise Desteklenmiyor("request.security düşük zaman dilimi (ayrıştırma)")
        anahtar = ("alt", sembol, dk)
        g = self.guvenlik.get(anahtar)
        if g is None:
            df2 = self.veri_saglayici(sembol, dk) if self.veri_saglayici is not None else None
            if df2 is None or df2.empty:
                raise Desteklenmiyor(f"düşük zaman dilimi verisi yok ({sembol} {dk}dk)")
            df2 = df2[df2.index >= self.df.index[0]]
            y = Yorumlayici(self.p, df2, tf_dk=dk, sembol=sembol, tz=self.tz, mintick=self.mintick, girdiler=self.girdiler,
                            guvenlik_modu=True)
            y.surum = self.surum
            for k in range(len(df2)):
                y.adim(None, k)
            bas = df2.index.asi8
            grafik = self.df.index.asi8
            bitis = np.r_[grafik[1:], grafik[-1] + self.tf_dk * 60_000_000_000]
            g = self.guvenlik[anahtar] = {"yorum": y, "ilk": np.searchsorted(bas, grafik, side="left"),
                                          "son": np.searchsorted(bas, bitis, side="left")}
        kayit = g["yorum"].guvenlik_kayit.get(id(e), {})
        ilk, son = int(g["ilk"][self.i]), int(g["son"][self.i])
        degerler = [kayit.get(k, NA) for k in range(ilk, son)]
        if dizi:
            ifade = dugumler["expression"]
            n = len(ifade.elts) if isinstance(ifade, A.Tuple) else next((len(x) for x in degerler if isinstance(x, tuple)), 0)
            if n:                       # demet ifade: dizilerden oluşan demet (TradingView)
                return tuple([x[j] if isinstance(x, tuple) else NA for x in degerler] for j in range(n))
            return degerler
        return degerler[-1] if degerler else NA

    def _birlestir(self, dk: int) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """Grafik barlarını `dk` dakikalık kovalara birleştirir: (yüksek dilim barları, grafik→kova haritası, kova bitişleri)."""
        bas, bit = _kova(self.df.index, dk, self.tz)
        kovalar, ilk, harita = np.unique(bas, return_index=True, return_inverse=True)
        htf = self.df.assign(_k=harita).groupby("_k").agg(
            open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"),
            volume=("volume", "sum") if "volume" in self.df else ("close", "size"))
        htf.index = pd.to_datetime(kovalar, utc=True)
        return htf, harita, np.asarray(bit)[ilk]

    def _guvenlik_kur(self, dk: int) -> dict:
        htf, harita, bitis = self._birlestir(dk)
        kapanis_grafik = self.df.index.asi8 + self.tf_dk * 60_000_000_000
        # bar i'de kapanmış son yüksek dilim kovası: bitişi <= grafik barı kapanışı olan en büyük k
        kapali = np.searchsorted(bitis, kapanis_grafik, side="right") - 1
        y = Yorumlayici(self.p, htf, tf_dk=dk, sembol=self.sembol, tz=self.tz, mintick=self.mintick,
                        girdiler=self.girdiler, guvenlik_modu=True)
        y.surum = self.surum
        for k in range(len(htf)):
            y.adim(None, k)
        return {"yorum": y, "harita": harita, "kapali": kapali}


# ---------------------------------------------------------------------- yardımcılar
HA_ONEK = "HEIKINASHI|"
KUTUPHANE_SAGLAYICI = None   # (kullanıcı, ad, sürüm) -> Pine kaynağı | None; koşucu (backtests.tv2) bağlar


def heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """TradingView Heikin Ashi barları: kapanış OHLC ortalaması, açılış önceki HA açılış/kapanış ortalaması
    (ilk bar (açılış+kapanış)/2), tepe/dip gerçek uçlarla HA açılış/kapanışın en büyüğü/küçüğü."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    hc = (o + h + l + c) / 4
    ho = np.empty_like(hc)
    ho[0] = (o[0] + c[0]) / 2
    for i in range(1, len(hc)):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    out = df.copy()
    out["open"], out["close"] = ho, hc
    out["high"], out["low"] = np.maximum.reduce([h, ho, hc]), np.minimum.reduce([l, ho, hc])
    return out


KOTASYONLAR = ("USDT", "USDC", "BUSD", "USD", "BTC", "ETH", "EUR", "TRY")


def _kotasyon(sembol: str) -> str:
    ad = sembol.split(":")[-1].replace(".P", "")
    return next((k for k in KOTASYONLAR if ad.endswith(k) and len(ad) > len(k)), "USD")


def _taban(sembol: str) -> str:
    ad = sembol.split(":")[-1].replace(".P", "")
    k = _kotasyon(sembol)
    return ad[: -len(k)] if ad.endswith(k) else ad


def _surum(p: A.Script) -> int:
    for a in getattr(p, "annotations", []) or []:
        s = str(getattr(a, "value", a))
        if "@version=" in s:
            try:
                return int(s.split("@version=")[1].strip()[:1])
            except ValueError:
                pass
    return 0


def surum_metinden(kaynak: str) -> int:
    for satir in kaynak.splitlines():
        if satir.strip().startswith("//@version="):
            try:
                return int(satir.strip().split("=")[1][:1])
            except ValueError:
                return 0
    return 1


def _nokta(e) -> str:
    try:
        return e.__dict__["_nokta"]
    except KeyError:
        pass
    ad = _nokta_hesapla(e)
    e.__dict__["_nokta"] = ad
    return ad


def _nokta_hesapla(e) -> str:
    parca = []
    while isinstance(e, A.Attribute):
        parca.append(e.attr)
        e = e.value
    if isinstance(e, A.Name):
        parca.append(e.id)
    elif isinstance(e, A.Specialize):
        return _nokta(e.value)
    return ".".join(reversed(parca))


def _dogru(x) -> bool:
    if x is None or na(x):
        return False
    return bool(x)


def _esit(a, b) -> bool:
    if na(a) or na(b):
        return False
    return a == b


def _karsilastir(op, a, b) -> bool:
    t = type(op)
    if t is A.Eq:
        return _esit(a, b)
    if t is A.NotEq:
        return False if (na(a) or na(b)) else a != b
    if na(a) or na(b):
        return False
    if t is A.Lt:
        return a < b
    if t is A.LtE:
        return a <= b
    if t is A.Gt:
        return a > b
    if t is A.GtE:
        return a >= b
    raise Desteklenmiyor(f"karşılaştırma {t.__name__}")


def _sayi(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return float(x)
    if isinstance(x, (int, float)):
        return None if na(float(x)) else float(x)
    return None


def _bagla(adlar: list[str], konum: list, adli: dict, varsayilan: dict | None = None) -> dict:
    out = dict(varsayilan or {})
    for k, v in enumerate(konum):
        if k < len(adlar):
            out[adlar[k]] = v
    for k, v in adli.items():
        out[k] = v
    for a in adlar:
        out.setdefault(a, None)
    return out


def _uyar(d: A.FunctionDef, n: int, adli: dict) -> bool:
    gerekli = sum(1 for p in d.args if p.default is None and p.name not in adli)
    return gerekli <= n <= len(d.args)


def _yok(ad):
    raise Desteklenmiyor(ad)


def _carpan(dk: int) -> int:
    for birim in (43200, 10080, 1440):
        if dk % birim == 0:
            return dk // birim
    return dk


def _tz(tz):
    """Pine saat dilimi: IANA adı ya da 'GMT+5:30' / 'UTC-3' biçimi (sabit fark)."""
    tz = str(tz)
    if tz.upper().startswith(("GMT", "UTC")) and len(tz) > 3 and tz[3] in "+-":
        isaret = 1 if tz[3] == "+" else -1
        saat, _, dk = tz[4:].partition(":")
        if not dk and len(saat) > 2:                  # 'GMT+530' / 'GMT+0530'
            saat, dk = saat[:-2], saat[-2:]
        return timezone(isaret * timedelta(hours=int(saat), minutes=int(dk or 0)))
    return tz


def _oturumda(zaman: pd.Timestamp, oturum: str, tz: str) -> bool:
    """Pine oturum metni: 'HHMM-HHMM[:gunler]' (gün 1 = pazar), birden çok aralık virgülle."""
    yerel = zaman.tz_convert(_tz(tz))
    pgun = (yerel.weekday() + 1) % 7 + 1
    dakika = yerel.hour * 60 + yerel.minute
    for parca in str(oturum).split(","):
        parca = parca.strip()
        if not parca:
            continue
        araliklar, _, gunler = parca.partition(":")
        if gunler and str(pgun) not in gunler:
            continue
        if araliklar in ("0000-0000", "24x7"):
            return True
        bas, _, son = araliklar.partition("-")
        b = int(bas[:2]) * 60 + int(bas[2:4])
        s = int(son[:2]) * 60 + int(son[2:4])
        if (b <= dakika < s) if b < s else (dakika >= b or dakika < s):
            return True
    return False


def _matematik(ad: str, konum, adli, y: Yorumlayici) -> Any:
    x = konum[0] if konum else adli.get("number", adli.get("x", adli.get("source")))
    if ad in ("max", "min"):
        if any(na(v) for v in konum):
            return NA
        return max(konum) if ad == "max" else min(konum)
    if ad == "avg":
        return NA if any(na(v) for v in konum) else sum(konum) / len(konum)
    if ad == "sum":
        raise Desteklenmiyor("math.sum (çağrı yeri durumu)")
    if na(x):
        return NA
    if ad == "abs":
        return abs(x)
    if ad == "round":
        hassas = konum[1] if len(konum) > 1 else adli.get("precision")
        if hassas is None:
            return int(math.floor(x + 0.5))
        k = 10 ** int(hassas)
        return math.floor(x * k + 0.5) / k
    if ad == "round_to_mintick":
        return math.floor(x / y.mintick + 0.5) * y.mintick
    tek = {"floor": lambda v: int(math.floor(v)), "ceil": lambda v: int(math.ceil(v)), "sqrt": lambda v: math.sqrt(v) if v >= 0 else NA,
           "log": lambda v: math.log(v) if v > 0 else NA, "log10": lambda v: math.log10(v) if v > 0 else NA, "exp": math.exp,
           "sign": lambda v: (v > 0) - (v < 0), "sin": math.sin, "cos": math.cos, "tan": math.tan,
           "asin": lambda v: math.asin(v) if -1 <= v <= 1 else NA, "acos": lambda v: math.acos(v) if -1 <= v <= 1 else NA,
           "atan": math.atan, "todegrees": math.degrees, "toradians": math.radians}
    if ad in tek:
        return tek[ad](x)
    if ad == "pow":
        b = konum[1] if len(konum) > 1 else adli["exponent"]
        try:
            return NA if na(b) else float(x) ** b
        except (OverflowError, ZeroDivisionError, ValueError):
            return NA
    raise Desteklenmiyor("math." + ad)


def _dizi(ad: str, konum, adli) -> Any:
    if ad.startswith("new"):
        boyut = konum[0] if konum else adli.get("size", 0)
        ilk = konum[1] if len(konum) > 1 else adli.get("initial_value", NA)
        return [ilk] * int(0 if na(boyut) else boyut)
    if ad == "from":
        return list(konum)
    a = konum[0]
    if not isinstance(a, list):
        raise PineHatasi(f"array.{ad} dizi olmayan")
    if ad in ("get", "set", "insert", "remove") and (len(konum) < 2 or na(konum[1])):
        raise PineHatasi(f"array.{ad}: indeks na")
    sayilar = [v for v in a if not na(v)]
    if ad == "size":
        return len(a)
    if ad == "get":
        k = int(konum[1] if len(konum) > 1 else adli["index"])
        if k < 0:
            k += len(a)
        if not 0 <= k < len(a):
            raise PineHatasi("dizi sınır dışı")
        return a[k]
    if ad == "set":
        k = int(konum[1])
        if k < 0:
            k += len(a)
        if not 0 <= k < len(a):
            raise PineHatasi("dizi sınır dışı")
        a[k] = konum[2]
        return None
    if ad == "push":
        a.append(konum[1])
        return None
    if ad == "unshift":
        a.insert(0, konum[1])
        return None
    if ad == "insert":
        a.insert(int(konum[1]), konum[2])
        return None
    if ad == "pop":
        if not a:
            raise PineHatasi("boş diziden pop")
        return a.pop()
    if ad == "shift":
        if not a:
            raise PineHatasi("boş diziden shift")
        return a.pop(0)
    if ad == "remove":
        return a.pop(int(konum[1]))
    if ad == "clear":
        a.clear()
        return None
    if ad == "first":
        return a[0] if a else NA
    if ad == "last":
        return a[-1] if a else NA
    if ad == "sum":
        return sum(sayilar) if sayilar else NA
    if ad == "avg":
        return sum(sayilar) / len(sayilar) if sayilar else NA
    if ad == "min":
        return min(sayilar) if sayilar else NA
    if ad == "max":
        return max(sayilar) if sayilar else NA
    if ad == "range":
        return max(sayilar) - min(sayilar) if sayilar else NA
    if ad == "median":
        if not sayilar:
            return NA
        s = sorted(sayilar)
        k = len(s)
        return s[k // 2] if k % 2 else (s[k // 2 - 1] + s[k // 2]) / 2
    if ad in ("stdev", "variance"):
        if not sayilar:
            return NA
        m = sum(sayilar) / len(sayilar)
        biased = konum[1] if len(konum) > 1 else adli.get("biased", True)
        d = len(sayilar) if biased else len(sayilar) - 1
        var = sum((v - m) ** 2 for v in sayilar) / d if d > 0 else NA
        return math.sqrt(var) if ad == "stdev" and not na(var) else var
    if ad == "includes":
        return konum[1] in a
    if ad == "indexof":
        return a.index(konum[1]) if konum[1] in a else -1
    if ad == "lastindexof":
        return len(a) - 1 - a[::-1].index(konum[1]) if konum[1] in a else -1
    if ad == "copy":
        return list(a)
    if ad == "concat":
        a.extend(konum[1])
        return a
    if ad == "reverse":
        a.reverse()
        return None
    if ad == "sort":
        sira = konum[1] if len(konum) > 1 else adli.get("order", 1)
        a.sort(key=lambda v: (na(v), v), reverse=(sira == -1))
        return None
    if ad == "fill":
        deger = konum[1]
        bas = int(konum[2]) if len(konum) > 2 else 0
        son = int(konum[3]) if len(konum) > 3 else len(a)
        for k in range(bas, son):
            a[k] = deger
        return None
    if ad == "slice":
        return a[int(konum[1]):int(konum[2])]
    if ad == "join":
        ayrac = konum[1] if len(konum) > 1 else ","
        return ayrac.join(str(v) for v in a)
    if ad == "abs":
        return [abs(v) if not na(v) else NA for v in a]
    if ad == "percentrank":
        k = int(konum[1])
        v = a[k]
        return 100.0 * sum(1 for x in a if x <= v) / len(a) if a else NA
    raise Desteklenmiyor("array." + ad)


def _matris(ad: str, konum, adli) -> Any:
    """Pine matrix: yaygın işlemler; desteklenmeyenler (det, inv, eigen ...) açık hata."""
    b = lambda k, ad_, v=None: konum[k] if len(konum) > k else adli.get(ad_, v)   # noqa: E731
    if ad == "new":
        r, c, ilk = b(0, "rows", 0), b(1, "columns", 0), b(2, "initial_value", NA)
        return _Matris([[ilk] * int(c) for _ in range(int(r))])
    m = konum[0]
    if not isinstance(m, _Matris):
        raise PineHatasi(f"matrix.{ad} matris olmayan")
    s = m.s
    if ad == "rows":
        return len(s)
    if ad == "columns":
        return len(s[0]) if s else 0
    if ad == "elements_count":
        return sum(len(r) for r in s)
    if ad in ("get", "set"):
        r, c = b(1, "row"), b(2, "column")
        if na(r) or na(c) or not (0 <= int(r) < len(s)) or not (0 <= int(c) < len(s[int(r)])):
            raise PineHatasi(f"matrix.{ad}: indeks dışı")
        if ad == "get":
            return s[int(r)][int(c)]
        s[int(r)][int(c)] = b(3, "value")
        return None
    if ad == "row":
        return list(s[int(b(1, "row"))])
    if ad == "col":
        return [r[int(b(1, "column"))] for r in s]
    if ad == "add_row":
        k, dizi = b(1, "row", len(s)), b(2, "array_id")
        k = len(s) if na(k) else int(k)
        n = len(s[0]) if s else (len(dizi) if isinstance(dizi, list) else 0)
        s.insert(k, list(dizi) if isinstance(dizi, list) else [NA] * n)
        return None
    if ad == "add_col":
        k, dizi = b(1, "column"), b(2, "array_id")
        k = (len(s[0]) if s else 0) if na(k) or k is None else int(k)
        for j, r in enumerate(s):
            r.insert(k, dizi[j] if isinstance(dizi, list) else NA)
        return None
    if ad == "remove_row":
        k = b(1, "row")
        return s.pop(len(s) - 1 if k is None or na(k) else int(k))
    if ad == "remove_col":
        k = b(1, "column")
        k = (len(s[0]) - 1) if k is None or na(k) else int(k)
        return [r.pop(k) for r in s]
    if ad == "fill":
        v = b(1, "value")
        r0, r1 = b(2, "from_row", 0), b(3, "to_row", len(s))
        c0, c1 = b(4, "from_column", 0), b(5, "to_column", len(s[0]) if s else 0)
        for i in range(int(r0), int(r1)):
            for j in range(int(c0), int(c1)):
                s[i][j] = v
        return None
    if ad == "copy":
        return _Matris([list(r) for r in s])
    if ad == "transpose":
        return _Matris([list(r) for r in zip(*s)])
    if ad in ("avg", "sum", "max", "min", "median", "mode"):
        return _dizi(ad, [[x for r in s for x in r]], {})
    raise Desteklenmiyor(f"matrix.{ad}")


def _harita(ad: str, konum, adli) -> Any:
    """Pine map: anahtar ekleme sırası korunur (Python dict)."""
    if ad == "new":
        return {}
    m = konum[0]
    if not isinstance(m, dict):
        raise PineHatasi(f"map.{ad} harita olmayan")
    if ad == "put":
        eski = m.get(konum[1], NA)
        m[konum[1]] = konum[2]
        return eski
    if ad == "get":
        return m.get(konum[1], NA)
    if ad == "contains":
        return konum[1] in m
    if ad == "remove":
        return m.pop(konum[1], NA)
    if ad == "size":
        return len(m)
    if ad == "keys":
        return list(m.keys())
    if ad == "values":
        return list(m.values())
    if ad == "clear":
        m.clear()
        return None
    if ad == "copy":
        return dict(m)
    if ad == "put_all":
        m.update(konum[1])
        return None
    raise Desteklenmiyor("map." + ad)


def _metin(ad: str, konum, adli) -> Any:
    x = konum[0] if konum else adli.get("value", adli.get("source", ""))
    if ad == "tostring":
        if na(x):
            return "NaN"
        if isinstance(x, bool):
            return "true" if x else "false"
        return str(x)
    if ad == "tonumber":
        try:
            return float(x)
        except (TypeError, ValueError):
            return NA
    if ad == "length":
        return len(x)
    if ad == "contains":
        return konum[1] in x
    if ad == "startswith":
        return x.startswith(konum[1])
    if ad == "endswith":
        return x.endswith(konum[1])
    if ad in ("upper", "lower"):
        return x.upper() if ad == "upper" else x.lower()
    if ad == "replace" or ad == "replace_all":
        return x.replace(konum[1], konum[2])
    if ad == "substring":
        return x[int(konum[1]):int(konum[2])] if len(konum) > 2 else x[int(konum[1]):]
    if ad == "split":
        return x.split(konum[1])
    if ad == "pos":
        k = x.find(konum[1])
        return NA if k < 0 else k
    if ad == "format":
        return str(x)
    if ad == "trim":
        return x.strip()
    raise Desteklenmiyor("str." + ad)


# ---------------------------------------------------------------------- strateji sarmalayıcı
GENERIK = re.compile(r"\b((?:array|matrix|map)\.new)\s*<\s*[\w.]+(?:\s*,\s*[\w.]+)?\s*>\s*\(")


def on_isle(kaynak: str) -> str:
    """pynescript `array.new<float>(...)` ifadesini karşılaştırma (`array.new < float > (...)`) diye ayrıştırıyor:
    tür parametresi anlamı değiştirmediği için ayrıştırmadan önce `array.new(...)` yapılır."""
    return GENERIK.sub(r"\1(", kaynak)


class PineStrateji:
    """Pine kaynağını `engine.tv_emulator.calistir` modül arayüzüne bağlar (AYARLAR / hazirla / bar)."""

    def __init__(self, kaynak: str | A.Script, *, sembol: str, tf: str, tz: str = "UTC", mintick: float = 0.01,
                 kimlik: str = "", surum: int | None = None) -> None:
        self.program = parse(on_isle(kaynak)) if isinstance(kaynak, str) else kaynak
        self.kaynak_metni = kaynak if isinstance(kaynak, str) else None
        self.sembol, self.tf_dk, self.tz, self.mintick, self.kimlik = sembol, tf_dakika(tf), tz, mintick, kimlik
        self._surum = surum or (surum_metinden(self.kaynak_metni) if self.kaynak_metni else (_surum(self.program) or 5))
        self.AYARLAR, self.uyarilar = self._ayarlar()
        self.y: Yorumlayici | None = None
        self.veri_saglayici = None

    def _yorumlayici(self, df) -> Yorumlayici:
        y = Yorumlayici(self.program, df, tf_dk=self.tf_dk, sembol=self.sembol, tz=self.tz, mintick=self.mintick)
        y.surum = self._surum
        y.veri_saglayici = self.veri_saglayici
        return y

    def _ayarlar(self) -> tuple[Ayarlar, list[str]]:
        cagri = next((d.value for d in self.program.body if isinstance(d, A.Expr) and isinstance(d.value, A.Call)
                      and isinstance(d.value.func, A.Name) and d.value.func.id == "strategy"), None)
        if cagri is None:
            raise Desteklenmiyor("strategy() bildirimi yok")
        y = Yorumlayici(self.program, None, tf_dk=self.tf_dk, sembol=self.sembol, tz=self.tz, mintick=self.mintick)
        y.surum = self._surum
        y.i = 0
        adlar = ["title", "shorttitle", "overlay", "format", "precision", "scale", "pyramiding", "calc_on_order_fills",
                 "calc_on_every_tick", "max_bars_back", "backtest_fill_limits_assumption", "default_qty_type",
                 "default_qty_value", "initial_capital", "currency", "slippage", "commission_type", "commission_value",
                 "process_orders_on_close", "close_entries_rule"]
        b: dict[str, Any] = {}
        for k, a in enumerate(cagri.args):
            ad = a.name or (adlar[k] if k < len(adlar) else f"_{k}")
            try:
                b[ad] = y._deger(a.value)
            except Desteklenmiyor:
                b[ad] = None
        uyari = []
        if _dogru(b.get("calc_on_order_fills")):
            uyari.append("calc_on_order_fills: geçmiş barlarda ek yürütmeler barın son değerlerini görür (TradingView ile aynı, canlıda farklı)")
        # close_entries_rule="ANY": çıkışlar from_entry kimliğiyle eşleşen işlemi kapatır; emülatör çıkış hedefini zaten
        # kimliğe göre seçiyor (FIFO yalnız aynı kimliğin işlemleri arasında). Fark yalnız FIFO'da görülür.
        if b.get("backtest_fill_limits_assumption") not in (None, 0):
            uyari.append("backtest_fill_limits_assumption yok sayıldı")
        if _dogru(b.get("calc_on_every_tick")):
            uyari.append("calc_on_every_tick geçmiş barlarda etkisiz")
        varsayilan_sermaye = 1_000_000.0 if self._surum >= 5 else 100_000.0
        a = Ayarlar(
            initial_capital=float(b.get("initial_capital") or varsayilan_sermaye),
            default_qty_type=b.get("default_qty_type") or "fixed",
            default_qty_value=float(b["default_qty_value"]) if b.get("default_qty_value") not in (None,) and not na(b.get("default_qty_value")) else 1.0,
            commission_type=b.get("commission_type") or "percent",
            commission_value=float(b.get("commission_value") or 0.0),
            slippage=int(b.get("slippage") or 0),
            pyramiding=int(b.get("pyramiding") or 0),
            process_orders_on_close=_dogru(b.get("process_orders_on_close")),
            mintick=self.mintick,
            calc_on_order_fills=_dogru(b.get("calc_on_order_fills")),
        )
        return a, uyari

    def hazirla(self, df: pd.DataFrame) -> dict:
        self.y = self._yorumlayici(df)
        return {}

    def ara(self, ctx, i: int) -> None:
        """calc_on_order_fills: dolum sonrası bar içi yürütme; her biri bar başı durumdan başlar, kesinleşmez."""
        if getattr(self, "_anlik_i", None) != i:
            self._anlik, self._anlik_i = self.y.anlik(), i
        else:
            self.y.geri_sar(self._anlik)
        self.y.adim(ctx, i, kesinlestir=False)

    def bar(self, ctx, i: int, v: dict) -> None:
        if getattr(self, "_anlik_i", None) == i:
            self.y.geri_sar(self._anlik)
            self._anlik = self._anlik_i = None
        self.y.adim(ctx, i)
