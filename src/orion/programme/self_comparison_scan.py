"""Find the guard that compares a value with itself, in any paper, from the AST.

``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity``
records a check whose condition no input can satisfy. Its canonical shape is a
comparison whose two sides are the same binding::

    projected_native = native_valid
    if projected_native != native_valid:
        donor_conservativity_violations += 1

``x != x`` is False for every value, so the counter is 0 however many times the
loop runs, and the published zero reads exactly like a guard that was pressed
and held.

The class was recorded against P6. The same guard was later found in P7 and, three
times over, in P8 --- not by any mechanism, because the class had none. This is
that mechanism, and it exists so the question "does this occur anywhere else"
has an answer instead of a silence.

The detector is deliberately narrow. It resolves single-assignment aliases
within a function --- ``a = b`` where neither name is ever rebound --- and flags
a comparison whose two operands resolve to the same root name. It does not
attempt dataflow, and it will not catch a self-comparison laundered through a
container or a call. A narrow detector that is right about what it reports is
worth more here than a broad one that has to be argued with, because the output
of this scan is meant to license a ``SWEPT_CLEAN`` claim about a whole paper.

What it does *not* do is decide intent. ``x == x`` is a legitimate NaN test and
appears in numeric code on purpose. Findings carry the enclosing function and the
source line so a reader can tell the two apart; the scan reports, it does not
adjudicate.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

__all__ = [
    "SelfComparison",
    "scan_paths",
    "scan_source",
]

#: Comparison operators whose result is constant when both sides are one object.
_CONSTANT_OPS: dict[type[ast.cmpop], bool] = {
    ast.NotEq: False,
    ast.Eq: True,
    ast.Lt: False,
    ast.Gt: False,
    ast.LtE: True,
    ast.GtE: True,
    ast.IsNot: False,
    ast.Is: True,
}


@dataclass(frozen=True)
class SelfComparison:
    """A comparison whose operands resolve to one binding."""

    path: str
    line: int
    function: str
    operator: str
    expression: str
    root: str
    constant_value: bool

    @property
    def summary(self) -> str:
        return (
            f"{self.path}:{self.line} in {self.function}(): {self.expression} "
            f"is always {self.constant_value} -- both sides resolve to {self.root!r}"
        )


def _alias_map(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, str]:
    """Names bound exactly once, to a bare name that is itself never rebound."""

    assigns: dict[str, list[ast.expr]] = {}
    rebound: set[str] = set()
    for node in ast.walk(fn):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        elif isinstance(node, ast.For):
            targets = [node.target]
        elif isinstance(node, (ast.While, ast.If)):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                value = getattr(node, "value", None)
                assigns.setdefault(target.id, []).append(value)
            else:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        rebound.add(sub.id)

    aliases: dict[str, str] = {}
    for name, values in assigns.items():
        if len(values) != 1 or name in rebound:
            continue
        value = values[0]
        if isinstance(value, ast.Name):
            aliases[name] = value.id
    return aliases


def _resolve(name: str, aliases: dict[str, str]) -> str:
    seen = {name}
    current = name
    while current in aliases:
        current = aliases[current]
        if current in seen:  # a cycle is not an alias chain
            return current
        seen.add(current)
    return current


def _single_binding(name: str, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True when ``name`` is bound exactly once in the function."""

    count = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.For)):
            targets = [node.target]
        else:
            continue
        for target in targets:
            for sub in ast.walk(target):
                if isinstance(sub, ast.Name) and sub.id == name:
                    count += 1
    return count <= 1


def scan_source(source: str, *, path: str) -> list[SelfComparison]:
    """Every self-resolving comparison in one module."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    out: list[SelfComparison] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        aliases = _alias_map(fn)
        for node in ast.walk(fn):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1:
                continue
            left, right = node.left, node.comparators[0]
            if not (isinstance(left, ast.Name) and isinstance(right, ast.Name)):
                continue
            root_left = _resolve(left.id, aliases)
            root_right = _resolve(right.id, aliases)
            if root_left != root_right:
                continue
            # Only report when the shared root cannot be rebound between the two
            # loads -- otherwise the comparison is of two different values.
            if not _single_binding(root_left, fn):
                continue
            op = type(node.ops[0])
            if op not in _CONSTANT_OPS:
                continue
            out.append(
                SelfComparison(
                    path=path,
                    line=node.lineno,
                    function=fn.name,
                    operator=op.__name__,
                    expression=f"{left.id} {_OP_TEXT[op]} {right.id}",
                    root=root_left,
                    constant_value=_CONSTANT_OPS[op],
                )
            )
    return out


_OP_TEXT: dict[type[ast.cmpop], str] = {
    ast.NotEq: "!=",
    ast.Eq: "==",
    ast.Lt: "<",
    ast.Gt: ">",
    ast.LtE: "<=",
    ast.GtE: ">=",
    ast.Is: "is",
    ast.IsNot: "is not",
}


def _python_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*.py")):
        if any(part in {".venv", "__pycache__", ".git"} for part in path.parts):
            continue
        yield path


def scan_paths(roots: Iterable[Path]) -> list[SelfComparison]:
    """Scan every Python file under each root."""

    out: list[SelfComparison] = []
    for root in roots:
        if root.is_file():
            out.extend(scan_source(root.read_text(errors="ignore"), path=str(root)))
            continue
        if not root.exists():
            continue
        for path in _python_files(root):
            out.extend(scan_source(path.read_text(errors="ignore"), path=str(path)))
    return out
