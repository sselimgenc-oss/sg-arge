"""Pine `ta.*` göstergelerinin bar bar (artımlı) karşılıkları.

Pine'da her `ta.*` çağrısının kendi durumu vardır (çağrı yeri başına); yorumlayıcı her çağrı yeri için bir nesne
tutar ve o çağrı her yürütüldüğünde nesneyi bir kez günceller. Tanımlar `engine/gosterge.py` ve
`strategies/ozel/tv_ortak.py` ile aynıdır (SMA tohumlu EMA/RMA, sert pivot eşitsizliği, nüfus standart sapması).
`na` = float('nan').
"""

from __future__ import annotations

import math
from collections import deque

NA = float("nan")


def na(x) -> bool:
    return x is None or x != x          # yalnız NaN kendine eşit değildir (sayı dışı tipler için False)


def f(x) -> float:
    if x is None:
        return NA
    if isinstance(x, bool):
        return float(x)
    return float(x)


class Tohumlu:
    """SMA tohumlu özyinelemeli yumuşatma (ema/rma): ilk n ardışık geçerli değerin ortalaması, sonra alpha."""

    def __init__(self) -> None:
        self.durum = NA
        self.tampon: list[float] = []

    def __call__(self, x, n, alpha) -> float:
        x, n = f(x), int(n)
        if na(self.durum):
            if na(x):
                self.tampon.clear()
                return NA
            self.tampon.append(x)
            if len(self.tampon) < n:
                return NA
            self.durum = sum(self.tampon[-n:]) / n
            self.tampon.clear()
            return self.durum
        if not na(x):
            self.durum = alpha * x + (1 - alpha) * self.durum
        return self.durum


class Ema(Tohumlu):
    def __call__(self, x, n):  # type: ignore[override]
        return super().__call__(x, n, 2.0 / (int(n) + 1))


class Rma(Tohumlu):
    def __call__(self, x, n):  # type: ignore[override]
        return super().__call__(x, n, 1.0 / int(n))


def nanli(w: list[float]) -> bool:
    """Pencerede na var mı (C düzeyinde toplam; NaN toplamı NaN yapar)."""
    t = sum(w)
    return t != t


class Pencere:
    """Son n değeri tutan yardımcı (n çağrılar arasında değişebilir; en çok `maks` değer saklanır)."""

    def __init__(self, maks: int = 5000) -> None:
        self.d: list[float] = []
        self.maks = maks

    def ekle(self, x) -> None:
        self.d.append(f(x))
        if len(self.d) > 2 * self.maks:
            del self.d[:-self.maks]

    def son(self, n) -> list[float] | None:
        if n is None or n != n:
            return None
        n = int(n)
        if n <= 0 or len(self.d) < n:
            return None
        return self.d[-n:]


class Sma:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        return sum(w) / len(w)


class Wma:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        n = len(w)
        return sum(v * (k + 1) for k, v in enumerate(w)) / (n * (n + 1) / 2)


class Vwma:
    def __init__(self) -> None:
        self.a, self.b = Sma(), Sma()

    def __call__(self, x, n, hacim):
        pay, payda = self.a(f(x) * f(hacim), n), self.b(hacim, n)
        return pay / payda if payda else NA


class Hma:
    def __init__(self) -> None:
        self.w1, self.w2, self.w3 = Wma(), Wma(), Wma()

    def __call__(self, x, n):
        n = int(n)
        return self.w3(2 * self.w1(x, n // 2) - self.w2(x, n), int(round(math.sqrt(n))))


class Alma:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n, offset=0.85, sigma=6.0, floor=False):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        n = len(w)
        m = math.floor(offset * (n - 1)) if floor else offset * (n - 1)
        s = n / sigma
        agirlik = [math.exp(-((k - m) ** 2) / (2 * s * s)) for k in range(n)]
        return sum(a * v for a, v in zip(agirlik, w)) / sum(agirlik)


class Stdev:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n, biased=True):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        m = sum(w) / len(w)
        d = len(w) if biased else len(w) - 1
        return math.sqrt(sum((v - m) ** 2 for v in w) / d) if d > 0 else NA


class Variance(Stdev):
    def __call__(self, x, n, biased=True):
        s = super().__call__(x, n, biased)
        return s * s


class Dev:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        m = sum(w) / len(w)
        return sum(abs(v - m) for v in w) / len(w)


class Toplam:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        return sum(w)


class EnYuksek:
    """ta.highest / ta.lowest (kaynak verilmezse high/low; yorumlayıcı kaynağı verir)."""

    def __init__(self, yon: int) -> None:
        self.p, self.yon = Pencere(), yon

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        return max(w) if self.yon > 0 else min(w)


class EnYuksekBar:
    """ta.highestbars / lowestbars: en uç değerin kaç bar önce olduğu (negatif)."""

    def __init__(self, yon: int) -> None:
        self.p, self.yon = Pencere(), yon

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        hedef = max(w) if self.yon > 0 else min(w)
        k = max(i for i, v in enumerate(w) if v == hedef)   # en yakın (Pine: son eşit değer)
        return -(len(w) - 1 - k)


class Gecmis:
    """x[n] için çağrı yeri başına kayıt (değişim, momentum, roc)."""

    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        n = int(n)
        if len(self.p.d) <= n:
            return NA, f(x)
        return self.p.d[-1 - n], f(x)


class Change(Gecmis):
    def __call__(self, x, n=1):  # type: ignore[override]
        if isinstance(x, bool):
            once, simdi = super().__call__(x, n)
            return False if na(once) else bool(simdi) != bool(once)
        once, simdi = super().__call__(x, n)
        return simdi - once


class Roc(Gecmis):
    def __call__(self, x, n):  # type: ignore[override]
        once, simdi = super().__call__(x, n)
        return 100 * (simdi - once) / once if once else NA


class Kesisim:
    """ta.crossover (yon 1), crossunder (-1), cross (0)."""

    def __init__(self, yon: int) -> None:
        self.yon, self.a1, self.b1 = yon, NA, NA

    def __call__(self, a, b):
        a, b = f(a), f(b)
        a1, b1 = self.a1, self.b1
        self.a1, self.b1 = a, b
        if any(na(v) for v in (a, b, a1, b1)):
            return False
        yukari = a > b and a1 <= b1
        asagi = a < b and a1 >= b1
        return yukari if self.yon > 0 else asagi if self.yon < 0 else (yukari or asagi)


class Tr:
    def __init__(self) -> None:
        self.c1 = NA

    def __call__(self, h, l, c, handle_na=True):
        c1, self.c1 = self.c1, f(c)
        if na(c1):
            return h - l if handle_na else NA
        return max(h - l, abs(h - c1), abs(l - c1))


class Atr:
    def __init__(self) -> None:
        self.tr, self.rma = Tr(), Rma()

    def __call__(self, n, h, l, c):
        return self.rma(self.tr(h, l, c), n)


class Rsi:
    def __init__(self) -> None:
        self.x1, self.up, self.dn = NA, Rma(), Rma()

    def __call__(self, x, n):
        x = f(x)
        x1, self.x1 = self.x1, x
        d = x - x1 if not (na(x) or na(x1)) else NA
        u = self.up(max(d, 0.0) if not na(d) else NA, n)
        v = self.dn(max(-d, 0.0) if not na(d) else NA, n)
        if na(u) or na(v):
            return NA
        if v == 0:
            return 100.0 if u > 0 else 50.0
        return 100 - 100 / (1 + u / v)


class Macd:
    def __init__(self) -> None:
        self.f, self.s, self.sig = Ema(), Ema(), Ema()

    def __call__(self, x, hizli, yavas, sinyal):
        m = self.f(x, hizli) - self.s(x, yavas)
        s = self.sig(m, sinyal)
        return m, s, m - s


class Stoch:
    def __init__(self) -> None:
        self.hi, self.lo = EnYuksek(1), EnYuksek(-1)

    def __call__(self, x, h, l, n):
        hh, ll = self.hi(h, n), self.lo(l, n)
        return 100 * (f(x) - ll) / (hh - ll) if hh != ll and not na(hh) else NA


class Dmi:
    """ta.dmi(diLength, adxSmoothing) -> (+DI, -DI, ADX), Pine tanımı."""

    def __init__(self) -> None:
        self.h1 = self.l1 = NA
        self.tr, self.r_tr, self.r_p, self.r_m, self.r_adx = Tr(), Rma(), Rma(), Rma(), Rma()

    def __call__(self, di, adx_n, h, l, c):
        h1, l1 = self.h1, self.l1
        self.h1, self.l1 = h, l
        up = h - h1 if not na(h1) else NA
        down = l1 - l if not na(l1) else NA
        plus = (up if up > down and up > 0 else 0.0) if not na(up) else NA
        minus = (down if down > up and down > 0 else 0.0) if not na(down) else NA
        trr = self.r_tr(self.tr(h, l, c), di)
        p = 100 * self.r_p(plus, di) / trr if trr else NA
        m = 100 * self.r_m(minus, di) / trr if trr else NA
        toplam = p + m
        adx = 100 * self.r_adx(abs(p - m) / (toplam if toplam != 0 else 1), adx_n)
        return p, m, adx


class Supertrend:
    """ta.supertrend(factor, atrPeriod) -> (değer, yön); Pine: yön -1 = yükseliş."""

    def __init__(self) -> None:
        self.atr = Atr()
        self.alt1 = self.ust1 = self.st1 = self.c1 = self.atr1 = NA

    def __call__(self, factor, n, h, l, c):
        a = self.atr(n, h, l, c)
        src = (h + l) / 2
        ust, alt = src + factor * a, src - factor * a
        onceki_alt = 0.0 if na(self.alt1) else self.alt1
        onceki_ust = 0.0 if na(self.ust1) else self.ust1
        if not na(alt):
            alt = alt if (alt > onceki_alt or (not na(self.c1) and self.c1 < onceki_alt)) else onceki_alt
        if not na(ust):
            ust = ust if (ust < onceki_ust or (not na(self.c1) and self.c1 > onceki_ust)) else onceki_ust
        if na(self.atr1):
            yon = 1
        elif self.st1 == onceki_ust:
            yon = -1 if c > ust else 1
        else:
            yon = 1 if c < alt else -1
        st = alt if yon == -1 else ust
        self.alt1, self.ust1, self.st1, self.c1, self.atr1 = alt, ust, st, c, a
        return st, yon


class Pivot:
    """ta.pivothigh / pivotlow (sert eşitsizlik): `right` bar sonra değer, değilse na."""

    def __init__(self, yon: int) -> None:
        self.p, self.yon = Pencere(), yon

    def __call__(self, x, sol, sag):
        self.p.ekle(x)
        sol, sag = int(sol), int(sag)
        w = self.p.son(sol + sag + 1)
        if w is None:
            return NA
        v = w[sol]
        if na(v):
            return NA
        diger = w[:sol] + w[sol + 1:]
        if nanli(diger):
            return NA
        return v if (all(v > d for d in diger) if self.yon > 0 else all(v < d for d in diger)) else NA


class Barssince:
    def __init__(self) -> None:
        self.sayac = NA

    def __call__(self, kosul):
        if kosul and not na(kosul):
            self.sayac = 0
        elif not na(self.sayac):
            self.sayac += 1
        return self.sayac


class Valuewhen:
    def __init__(self) -> None:
        self.degerler: deque = deque(maxlen=1000)

    def __call__(self, kosul, x, occurrence=0):
        if kosul and not na(kosul):
            self.degerler.append(x)
        k = int(occurrence)
        return self.degerler[-1 - k] if len(self.degerler) > k else NA


class Linreg:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n, offset=0):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        n = len(w)
        xs = range(n)
        mx, my = (n - 1) / 2, sum(w) / n
        sxx = sum((k - mx) ** 2 for k in xs)
        egim = sum((k - mx) * (v - my) for k, v in zip(xs, w)) / sxx if sxx else 0.0
        kesen = my - egim * mx
        return kesen + egim * (n - 1 - int(offset))


class Cum:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self, x):
        if not na(x):
            self.t += f(x)
        return self.t


class Percentrank:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(int(n) + 1)
        if w is None or nanli(w):
            return NA
        simdi = w[-1]
        return 100.0 * sum(1 for v in w[:-1] if v <= simdi) / int(n)


class Cci:
    def __init__(self) -> None:
        self.sma, self.dev = Sma(), Dev()

    def __call__(self, x, n):
        m, d = self.sma(x, n), self.dev(x, n)
        return (f(x) - m) / (0.015 * d) if d else NA


class Mfi:
    def __init__(self) -> None:
        self.x1 = NA
        self.pos, self.neg = Toplam(), Toplam()

    def __call__(self, x, n, hacim):
        x = f(x)
        x1, self.x1 = self.x1, x
        ch = x - x1 if not na(x1) else NA
        akis = x * f(hacim)
        p = self.pos(akis if not na(ch) and ch > 0 else (0.0 if not na(ch) else NA), n)
        m = self.neg(akis if not na(ch) and ch < 0 else (0.0 if not na(ch) else NA), n)
        if na(p) or na(m):
            return NA
        return 100.0 if m == 0 else 100 - 100 / (1 + p / m)


class Bb:
    def __init__(self) -> None:
        self.sma, self.sd = Sma(), Stdev()

    def __call__(self, x, n, mult):
        m, s = self.sma(x, n), self.sd(x, n)
        return m, m + mult * s, m - mult * s


class Monoton:
    """ta.rising (yon 1) / ta.falling (-1): son n barda kesin artış/azalış."""

    def __init__(self, yon: int) -> None:
        self.p, self.yon = Pencere(), yon

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(int(n) + 1)
        if w is None or nanli(w):
            return False
        simdi = w[-1]
        return all(simdi > v for v in w[:-1]) if self.yon > 0 else all(simdi < v for v in w[:-1])


class Sar:
    """ta.sar(start, inc, max): Pine yerleşik parabolik SAR."""

    def __init__(self) -> None:
        self.bar = 0
        self.sonuc = self.uc = self.af = NA
        self.uzun = True
        self.h1 = self.l1 = self.c1 = NA
        self.h2 = self.l2 = NA

    def __call__(self, baslangic, artis, maks, h, l, c):
        self.bar += 1
        if self.bar == 1:
            self.h1, self.l1, self.c1 = h, l, c
            return NA
        if self.bar == 2:
            self.uzun = c > self.c1
            self.uc = h if self.uzun else l
            self.sonuc = self.l1 if self.uzun else self.h1
            self.af = baslangic
            self.h2, self.l2, self.h1, self.l1, self.c1 = self.h1, self.l1, h, l, c
            return self.sonuc
        sar = self.sonuc + self.af * (self.uc - self.sonuc)
        if self.uzun:
            if l < sar:
                self.uzun, sar, self.uc, self.af = False, max(self.uc, h), l, baslangic
            else:
                if h > self.uc:
                    self.uc, self.af = h, min(self.af + artis, maks)
                sar = min(sar, self.l1, self.l2 if not na(self.l2) else self.l1)
        else:
            if h > sar:
                self.uzun, sar, self.uc, self.af = True, min(self.uc, l), h, baslangic
            else:
                if l < self.uc:
                    self.uc, self.af = l, min(self.af + artis, maks)
                sar = max(sar, self.h1, self.h2 if not na(self.h2) else self.h1)
        self.sonuc = sar
        self.h2, self.l2, self.h1, self.l1, self.c1 = self.h1, self.l1, h, l, c
        return sar


class Vwap:
    """ta.vwap: oturum (UTC gün / borsa günü) başında sıfırlanan hacim ağırlıklı ortalama."""

    def __init__(self) -> None:
        self.gun = None
        self.pv = self.v = self.pv2 = 0.0

    def __call__(self, x, hacim, gun, capa=None, carpan=None):
        """`capa` (anchor) verilirse doğru olduğu barda sıfırlanır, yoksa gün değişiminde. `carpan` verilirse
        (vwap, üst, alt) demeti: bantlar vwap ± carpan x hacim ağırlıklı standart sapma."""
        yeni = bool(capa) if capa is not None and not na(capa) else gun != self.gun
        if yeni or self.gun is None:
            self.gun, self.pv, self.v, self.pv2 = gun, 0.0, 0.0, 0.0
        self.pv += f(x) * f(hacim)
        self.pv2 += f(x) * f(x) * f(hacim)
        self.v += f(hacim)
        orta = self.pv / self.v if self.v else NA
        if carpan is None:
            return orta
        if na(orta):
            return NA, NA, NA
        sd = math.sqrt(max(self.pv2 / self.v - orta * orta, 0.0))
        return orta, orta + carpan * sd, orta - carpan * sd


class Obv:
    def __init__(self) -> None:
        self.c1, self.t = NA, 0.0

    def __call__(self, c, hacim):
        if not na(self.c1):
            self.t += f(hacim) if c > self.c1 else -f(hacim) if c < self.c1 else 0.0
        self.c1 = c
        return self.t


class HacimDegiskeni:
    """ta.accdist / iii / nvi / pvi / pvt / wad / wvad (TradingView başvuru tanımları)."""

    def __init__(self, ad: str) -> None:
        self.ad, self.c1, self.v1, self.t = ad, NA, NA, 0.0
        self.endeks = 1.0

    def __call__(self, o, h, l, c, hacim):
        ad, c1, v1 = self.ad, self.c1, self.v1
        self.c1, self.v1 = c, hacim
        aralik = h - l
        if ad == "ta.iii":
            return NA if aralik == 0 or not hacim else (2 * c - h - l) / (aralik * hacim)
        if ad == "ta.wvad":
            return NA if aralik == 0 else (c - o) / aralik * f(hacim)
        if ad == "ta.accdist":
            self.t += 0.0 if aralik == 0 else (2 * c - l - h) / aralik * f(hacim)
            return self.t
        if ad == "ta.pvt":
            if not na(c1) and c1:
                self.t += (c - c1) / c1 * f(hacim)
            return self.t
        if ad == "ta.wad":
            if not na(c1):
                gain = c - min(l, c1) if c > c1 else c - max(h, c1) if c < c1 else 0.0
                self.t += gain
            return self.t
        onceki = self.endeks or 1.0                    # nvi / pvi
        if not na(c1) and c1 and c:
            kosul = f(hacim) < f(v1) if ad == "ta.nvi" else f(hacim) > f(v1)
            if kosul:
                self.endeks = onceki + (c - c1) / c1 * onceki
        return self.endeks


class Median:
    def __init__(self) -> None:
        self.p = Pencere()

    def __call__(self, x, n):
        self.p.ekle(x)
        w = self.p.son(n)
        if w is None or nanli(w):
            return NA
        s = sorted(w)
        k = len(s)
        return s[k // 2] if k % 2 else (s[k // 2 - 1] + s[k // 2]) / 2


class Korelasyon:
    def __init__(self) -> None:
        self.a, self.b = Pencere(), Pencere()

    def __call__(self, x, y, n):
        self.a.ekle(x)
        self.b.ekle(y)
        wa, wb = self.a.son(n), self.b.son(n)
        if wa is None or wb is None or nanli(wa) or nanli(wb):
            return NA
        ma, mb = sum(wa) / len(wa), sum(wb) / len(wb)
        sa = math.sqrt(sum((v - ma) ** 2 for v in wa))
        sb = math.sqrt(sum((v - mb) ** 2 for v in wb))
        return sum((u - ma) * (v - mb) for u, v in zip(wa, wb)) / (sa * sb) if sa and sb else NA


class Wpr:
    def __init__(self) -> None:
        self.hi, self.lo = EnYuksek(1), EnYuksek(-1)

    def __call__(self, n, h, l, c):
        hh, ll = self.hi(h, n), self.lo(l, n)
        return 100 * (c - hh) / (hh - ll) if hh != ll and not na(hh) else NA
