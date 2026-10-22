"""Safe expression language for strategy cards.

Cards carry entry/exit rules as text. This module parses them with Python's
``ast`` and accepts only a whitelist of node types, so there is no ``eval``:

* numbers, strings (timeframes), True/False
* names and one-level attributes (``dmi14.plus``)
* ``x[k]`` with a non-negative integer constant (k-bar lag)
* arithmetic ``+ - * /`` and unary minus
* comparisons ``< <= > >= == !=`` (chains allowed)
* ``and`` / ``or`` / ``not``
* calls to whitelisted functions: ``cross_over``, ``cross_under``, ``mtf``,
  ``ay_islem_gunu_bastan``, ``ay_islem_gunu_sondan``, ``haftanin_gunu``,
  ``yeni_gun``, ``ay_gunu``, ``paskalya``, ``valuewhen``, ``highestsince``, ``lowestsince``,
  ``max``, ``min``, ``abs``, ``eger(kosul, a, b)`` (if/else)

Evaluation is vectorised over pandas Series. NaN comparisons are False.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from . import takvim

FUNCTIONS = frozenset(
    {
        "cross_over",
        "cross_under",
        "mtf",
        "ay_islem_gunu_bastan",
        "ay_islem_gunu_sondan",
        "haftanin_gunu",
        "yeni_gun",
        "ay_gunu",
        "paskalya",
        "valuewhen",
        "highestsince",
        "lowestsince",
        "max",
        "min",
        "abs",
        "eger",
    }
)

_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div)
_ALLOWED_CMPOPS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


class ExprError(ValueError):
    """Raised for unparsable, unsafe or unevaluable expressions."""


@dataclass
class Expr:
    text: str
    tree: ast.Expression
    names: frozenset[str] = field(default_factory=frozenset)
    attrs: frozenset[tuple[str, str]] = field(default_factory=frozenset)
    funcs: frozenset[str] = field(default_factory=frozenset)

    def evaluate(
        self,
        env: Mapping[str, Any],
        *,
        index: pd.Index | None = None,
        mtf: Callable[[str, pd.Series], pd.Series] | None = None,
    ) -> Any:
        """Evaluate against ``env`` (name -> Series/DataFrame/number)."""
        if index is None:
            index = _first_index(env)
        return _Evaluator(env, index, mtf).visit(self.tree.body)


def _first_index(env: Mapping[str, Any]) -> pd.Index | None:
    for value in env.values():
        if isinstance(value, (pd.Series, pd.DataFrame)):
            return value.index
    return None


def parse(text: str) -> Expr:
    """Parse and validate ``text``; raises ExprError on anything unsafe."""
    if not isinstance(text, str) or not text.strip():
        raise ExprError("empty expression")
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except SyntaxError as exc:
        raise ExprError(f"syntax error: {exc.msg}") from exc
    names: set[str] = set()
    attrs: set[tuple[str, str]] = set()
    funcs: set[str] = set()
    _check(tree.body, names, attrs, funcs)
    return Expr(text.strip(), tree, frozenset(names), frozenset(attrs), frozenset(funcs))


def _check(node: ast.AST, names: set, attrs: set, funcs: set) -> None:
    if isinstance(node, ast.BoolOp):
        for value in node.values:
            _check(value, names, attrs, funcs)
    elif isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, (ast.Not, ast.USub, ast.UAdd)):
            raise ExprError(f"operator not allowed: {type(node.op).__name__}")
        _check(node.operand, names, attrs, funcs)
    elif isinstance(node, ast.BinOp):
        if not isinstance(node.op, _ALLOWED_BINOPS):
            raise ExprError(f"operator not allowed: {type(node.op).__name__}")
        _check(node.left, names, attrs, funcs)
        _check(node.right, names, attrs, funcs)
    elif isinstance(node, ast.Compare):
        if not all(isinstance(op, _ALLOWED_CMPOPS) for op in node.ops):
            raise ExprError("comparison operator not allowed")
        _check(node.left, names, attrs, funcs)
        for comparator in node.comparators:
            _check(comparator, names, attrs, funcs)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise ExprError("function not allowed: " + ast.unparse(node.func))
        if node.keywords:
            raise ExprError("keyword arguments are not allowed")
        funcs.add(node.func.id)
        for arg in node.args:
            _check(arg, names, attrs, funcs)
    elif isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, ast.Attribute):
        if not isinstance(node.value, ast.Name):
            raise ExprError("only one-level attributes are allowed: " + ast.unparse(node))
        names.add(node.value.id)
        attrs.add((node.value.id, node.attr))
    elif isinstance(node, ast.Subscript):
        lag = node.slice
        if not (isinstance(lag, ast.Constant) and isinstance(lag.value, int) and not isinstance(lag.value, bool) and lag.value >= 0):
            raise ExprError("lag must be a non-negative integer constant: " + ast.unparse(node))
        _check(node.value, names, attrs, funcs)
    elif isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float, str, bool)):
            raise ExprError(f"constant not allowed: {node.value!r}")
    else:
        raise ExprError(f"syntax not allowed: {type(node).__name__}")


def _as_series(value: Any, index: pd.Index | None) -> pd.Series:
    if isinstance(value, pd.Series):
        return value
    if index is None:
        raise ExprError("no index available to broadcast a scalar")
    return pd.Series(value, index=index)


def _as_bool(value: Any, index: pd.Index | None) -> Any:
    if isinstance(value, pd.Series):
        return value.fillna(False).astype(bool)
    return bool(value)


class _Evaluator:
    def __init__(self, env: Mapping[str, Any], index: pd.Index | None, mtf: Callable | None):
        self.env = env
        self.index = index
        self.mtf = mtf

    def visit(self, node: ast.AST) -> Any:
        method = getattr(self, "_" + type(node).__name__, None)
        if method is None:  # pragma: no cover - parse() already whitelists
            raise ExprError(f"cannot evaluate {type(node).__name__}")
        return method(node)

    def _Constant(self, node: ast.Constant) -> Any:
        return node.value

    def _Name(self, node: ast.Name) -> Any:
        if node.id not in self.env:
            raise ExprError(f"undefined name: {node.id}")
        return self.env[node.id]

    def _Attribute(self, node: ast.Attribute) -> Any:
        base = self._Name(node.value)
        if isinstance(base, (pd.DataFrame, dict)):
            if node.attr not in base:
                raise ExprError(f"{node.value.id} has no field {node.attr}")
            return base[node.attr]
        raise ExprError(f"{node.value.id} has no field {node.attr}")

    def _Subscript(self, node: ast.Subscript) -> Any:
        base = self.visit(node.value)
        lag = node.slice.value
        if isinstance(base, (pd.Series, pd.DataFrame)):
            return base.shift(lag)
        return base

    def _UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            flag = _as_bool(operand, self.index)
            return ~flag if isinstance(flag, pd.Series) else (not flag)
        return -operand if isinstance(node.op, ast.USub) else +operand

    def _BinOp(self, node: ast.BinOp) -> Any:
        left, right = self.visit(node.left), self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(right, (int, float)) and right == 0:
            raise ExprError("division by zero constant")
        return left / right

    def _Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        result: Any = None
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            part = _compare(op, left, right)
            result = part if result is None else _and(result, part, self.index)
            left = right
        return result

    def _BoolOp(self, node: ast.BoolOp) -> Any:
        values = [_as_bool(self.visit(v), self.index) for v in node.values]
        result = values[0]
        for value in values[1:]:
            result = _and(result, value, self.index) if isinstance(node.op, ast.And) else _or(result, value, self.index)
        return result

    def _Call(self, node: ast.Call) -> Any:
        name = node.func.id
        if name == "mtf":
            if len(node.args) != 2 or not (isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                raise ExprError('mtf expects ("<tf>", expression)')
            if self.mtf is None:
                raise ExprError("mtf requires an mtf callable in evaluate()")
            series = _as_series(self.visit(node.args[1]), self.index)
            return self.mtf(node.args[0].value, series)
        args = [self.visit(arg) for arg in node.args]
        if name in ("cross_over", "cross_under"):
            if len(args) != 2:
                raise ExprError(f"{name} expects 2 arguments")
            a, b = _as_series(args[0], self.index), _as_series(args[1], self.index)
            if name == "cross_over":
                return ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False)
            return ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False)
        if name in ("ay_islem_gunu_bastan", "ay_islem_gunu_sondan"):
            if len(args) != 1 or self.index is None:
                raise ExprError(f"{name} expects (k) and an index")
            return getattr(takvim, name)(self.index, int(args[0]))
        if name == "haftanin_gunu":
            if self.index is None:
                raise ExprError("haftanin_gunu needs an index")
            return takvim.haftanin_gunu(self.index)
        if name == "ay_gunu":
            if self.index is None or args:
                raise ExprError("ay_gunu() takes no arguments and needs an index")
            return takvim.ay_gunu(self.index)
        if name == "paskalya":
            if len(args) != 1 or self.index is None:
                raise ExprError("paskalya expects (k) and an index")
            return takvim.paskalya(self.index, int(args[0]))
        if name == "yeni_gun":
            if self.index is None or args:
                raise ExprError("yeni_gun() takes no arguments and needs an index")
            return takvim.yeni_gun(self.index)
        if name in ("valuewhen", "highestsince", "lowestsince"):
            if len(args) != 2:
                raise ExprError(f"{name} expects (condition, series)")
            cond = _as_bool(_as_series(args[0], self.index), self.index)
            series = _as_series(args[1], self.index).astype(float)
            if name == "valuewhen":
                return series.where(cond).ffill()
            group = cond.astype(int).cumsum()
            running = series.groupby(group).cummax() if name == "highestsince" else series.groupby(group).cummin()
            return running.where(group > 0)
        if name == "eger":
            if len(args) != 3:
                raise ExprError("eger expects (condition, if_true, if_false)")
            cond = _as_bool(args[0], self.index)
            if isinstance(cond, pd.Series) or any(isinstance(a, pd.Series) for a in args[1:]):
                cond = _as_series(cond, self.index).astype(bool)
                return pd.Series(np.where(cond, _as_series(args[1], self.index), _as_series(args[2], self.index)), index=cond.index)
            return args[1] if cond else args[2]
        if name in ("max", "min"):
            if len(args) != 2:
                raise ExprError(f"{name} expects 2 arguments")
            func = np.maximum if name == "max" else np.minimum
            return func(args[0], args[1])
        if len(args) != 1:
            raise ExprError("abs expects 1 argument")
        return abs(args[0])


def _compare(op: ast.cmpop, left: Any, right: Any) -> Any:
    if isinstance(op, ast.Lt):
        return left < right
    if isinstance(op, ast.LtE):
        return left <= right
    if isinstance(op, ast.Gt):
        return left > right
    if isinstance(op, ast.GtE):
        return left >= right
    if isinstance(op, ast.Eq):
        return left == right
    return left != right


def _and(a: Any, b: Any, index: pd.Index | None) -> Any:
    if isinstance(a, pd.Series) or isinstance(b, pd.Series):
        return _as_series(a, index) & _as_series(b, index)
    return bool(a) and bool(b)


def _or(a: Any, b: Any, index: pd.Index | None) -> Any:
    if isinstance(a, pd.Series) or isinstance(b, pd.Series):
        return _as_series(a, index) | _as_series(b, index)
    return bool(a) or bool(b)
