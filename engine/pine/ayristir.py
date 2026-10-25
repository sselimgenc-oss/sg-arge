"""Hızlı Pine ayrıştırma: pynescript'in ANTLR ayrıştırıcısı, SLL tahmin modu (başarısızsa tam LL) ve yorum geçişi yok.

pynescript `parse` iki tam geçiş yapar (kod + yorumlar) ve varsayılan LL modu büyük betiklerde 20-60 sn sürer.
Yorumlayıcı yorum düğümlerini kullanmaz; sürüm `//@version=` metninden okunur. Sonuç (AST) kaynak özetine göre
diskte önbelleğe alınır: aynı betik ve kütüphane bir daha ayrıştırılmaz.
"""

from __future__ import annotations

import hashlib
import os
import pickle
from pathlib import Path

from antlr4 import CommonTokenStream, InputStream
from antlr4.atn.PredictionMode import PredictionMode
from antlr4.error.ErrorStrategy import BailErrorStrategy, DefaultErrorStrategy
from antlr4.error.Errors import ParseCancellationException
from pynescript.ast.builder import PinescriptASTBuilder
from pynescript.ast.grammar.antlr4.error_listener import PinescriptErrorListener
from pynescript.ast.grammar.antlr4.lexer import PinescriptLexer
from pynescript.ast.grammar.antlr4.parser import PinescriptParser

ONBELLEK = Path(os.environ.get("PINE_AST_ONBELLEK", Path(__file__).resolve().parents[2] / "data" / "tv2" / "ast"))
SURUM = "1"   # ayrıştırma ya da ön işleme değişirse artırılır (önbelleği geçersiz kılar)
_bellek: dict[str, object] = {}


def _ayristir(kaynak: str):
    lexer = PinescriptLexer(InputStream(kaynak))
    parser = PinescriptParser(CommonTokenStream(lexer))
    lexer.removeErrorListeners()
    parser.removeErrorListeners()
    parser._interp.predictionMode = PredictionMode.SLL
    parser._errHandler = BailErrorStrategy()
    try:
        agac = parser.start_script()
    except ParseCancellationException:            # SLL yetmedi: aynı belirteçlerle tam LL, normal hata raporu
        parser.reset()
        parser.addErrorListener(PinescriptErrorListener.INSTANCE)
        parser._interp.predictionMode = PredictionMode.LL
        parser._errHandler = DefaultErrorStrategy()
        agac = parser.start_script()
    return PinescriptASTBuilder().visit(agac)


def ayristir(kaynak: str):
    ozet = hashlib.sha1((SURUM + kaynak).encode()).hexdigest()
    if ozet in _bellek:
        return _bellek[ozet]
    yol = ONBELLEK / f"{ozet}.pkl"
    if yol.exists():
        try:
            agac = pickle.loads(yol.read_bytes())
            _bellek[ozet] = agac
            return agac
        except Exception:                          # bozuk önbellek: yeniden ayrıştır
            pass
    agac = _ayristir(kaynak)
    _bellek[ozet] = agac
    try:
        ONBELLEK.mkdir(parents=True, exist_ok=True)
        gecici = yol.with_suffix(f".{os.getpid()}.tmp")
        gecici.write_bytes(pickle.dumps(agac, protocol=pickle.HIGHEST_PROTOCOL))
        gecici.replace(yol)
    except Exception:
        pass
    return agac
