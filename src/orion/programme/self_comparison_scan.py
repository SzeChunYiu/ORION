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

The class has three shapes, and the first version of this module caught one:

1. **Aliased name.** ``a = b`` and then ``a != b``. P7, and P8.
2. **Identical call.** ``x = f(args)`` immediately followed by ``y = f(args)``
   and then ``x != y``. P8 published ``ideal_product_mismatches: 0`` from this,
   and an alias-only scan walks straight past it --- which is exactly what
   happened here: this module reported all fifteen papers clean while that shape
   was live in P8.
3. **One rule written twice.** Two functions with identical bodies, compared.
   This is the shape that *named* the class: P6 wrote one rule as
   ``scientific_admissible`` and again as ``ideal_product``.

Three exclusions carry most of the accuracy, and each was added after the scan
called something real a defect:

- **The receiver is part of the callee.** ``left.fingerprint(mode)`` and
  ``right.fingerprint(mode)`` share a method name and an argument list and are
  calls on two different objects. Matching on the attribute name alone reported
  seven such lines in P9, every one a real test.
- **The two calls must be adjacent and written identically.** Anything between
  them can change what the second returns, and that is usually the point: P6's
  hidden-read counterexample calls ``hidden_write_n()`` between two identical
  reads and asserts that they differ.
- **What the comparison feeds decides whether it is a defect.** The failure
  class is a *published zero that no input can disturb*, so only a comparison
  whose branch increments or appends a reported quantity
  (:data:`Context.COUNTS`) is one. The same expression inside an assertion is a
  claim under test --- a determinism test writes ``f(x) == f(x)`` precisely
  because purity is the thing being checked, and five of those are live in this
  repo --- and inside a fixture it can be a deliberate tautology, which P6 builds
  on purpose to prove its instrument can still emit ``FAIL``.

So the scan reports every constant comparison it finds and adjudicates only the
last question. A sweep that called those seven a defect would be as useless as
one that missed P8, in the other direction.
"""

from __future__ import annotations

import ast
from enum import Enum

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

__all__ = [
    "Context",
    "SelfComparison",
    "scan_paths",
    "scan_source",
]

#: Callees whose two identical invocations may legitimately differ, so comparing
#: them is a real test rather than a constant. Anything not listed is reported.
_NONDETERMINISTIC_HINTS = frozenset(
    {"random", "randint", "choice", "shuffle", "uuid4", "now", "today", "time", "monotonic"}
)

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

class Context(str, Enum):
    """What the constant comparison is used for, which decides whether it is a defect.

    The failure class is a *published zero that no input can disturb*, so the
    defect is the comparison whose branch feeds a reported quantity. The same
    expression written as an assertion is a claim under test, and written as a
    fixture is a deliberate tautology --- neither publishes a number.
    """

    #: The branch increments or appends to something. This is the defect shape.
    COUNTS = "COUNTS"
    #: Inside an assert, or in a test. A determinism test writes ``f(x) == f(x)``
    #: precisely because purity is the thing being checked, not something assumed.
    ASSERTS = "ASSERTS"
    #: Neither. Reported for a reader to adjudicate.
    UNCLASSIFIED = "UNCLASSIFIED"

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
    context: Context = Context.UNCLASSIFIED

    @property
    def is_defect(self) -> bool:
        """Only a counted comparison publishes a zero nothing can disturb."""

        return self.context is Context.COUNTS

    @property
    def summary(self) -> str:
        return (
            f"{self.path}:{self.line} in {self.function}(): {self.expression} "
            f"is always {self.constant_value} -- both sides resolve to {self.root!r} "
            f"[{self.context.value}]"
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

def _call_signatures(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, tuple[str, str]]:
    """Names bound once to a call, keyed by the call's exact source shape.

    The second half of the class. P8 published ``ideal_product_mismatches: 0``
    from::

        terminal = scientific_terminal(native_valid, type_flags, ...)
        ideal    = scientific_terminal(native_valid, type_flags, ...)
        if terminal != ideal:
            ideal_product_mismatches += 1

    Two invocations of one function on one argument list. For a deterministic
    callee that is ``x != x``, and the counter is 0 for every input --- but the
    operands are not aliases of a name, so an alias-resolving scan walks straight
    past it. That is exactly what happened: the first version of this module
    reported all fifteen papers clean while this shape was live in P8.

    Returns ``{name: (callee, dumped_call)}``. Nondeterministic callees are
    excluded, because two calls to ``random()`` genuinely may differ.
    """

    out: dict[str, tuple[str, str]] = {}
    counts: dict[str, int] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                counts[target.id] = counts.get(target.id, 0) + 1

    # Only *adjacent* assignments qualify. Anything between the two calls can
    # change what the second one returns, and that is the normal reason to write
    # them: P6's hidden-read counterexample calls ``hidden_write_n()`` between two
    # ``hidden_read_m(1)`` reads and asserts they differ, and the harness archives
    # a failed result, services a request, and archives again. Both were reported
    # as constant by a version of this scan that only matched the call text.
    for block in _statement_blocks(fn):
        for first, second in zip(block, block[1:]):
            pair = _adjacent_identical_calls(first, second)
            if pair is None:
                continue
            left_name, right_name, callee, dumped = pair
            if counts.get(left_name, 0) != 1 or counts.get(right_name, 0) != 1:
                continue
            out[left_name] = (callee, dumped)
            out[right_name] = (callee, dumped)
    return out

def _statement_blocks(node: ast.AST) -> Iterator[list[ast.stmt]]:
    """Every straight-line statement list in the tree, innermost included."""

    for child in ast.walk(node):
        for field in ("body", "orelse", "finalbody"):
            block = getattr(child, field, None)
            if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                yield block

def _adjacent_identical_calls(
    first: ast.stmt, second: ast.stmt
) -> tuple[str, str, str, str] | None:
    """``a = f(x)`` immediately followed by ``b = f(x)``, written identically."""

    if not (isinstance(first, ast.Assign) and isinstance(second, ast.Assign)):
        return None
    if len(first.targets) != 1 or len(second.targets) != 1:
        return None
    left, right = first.targets[0], second.targets[0]
    if not (isinstance(left, ast.Name) and isinstance(right, ast.Name)):
        return None
    if not (isinstance(first.value, ast.Call) and isinstance(second.value, ast.Call)):
        return None
    if ast.dump(first.value) != ast.dump(second.value):
        return None
    callee = _callee_name(first.value)
    if callee is None or callee in _NONDETERMINISTIC_HINTS:
        return None
    return left.id, right.id, callee, ast.dump(first.value)

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

def _body_signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """A function's body with its own parameter names normalised away.

    Two functions that differ only in name and parameter spelling compute the
    same thing, and comparing their results is ``x != x``. This is the shape that
    named the class: P6 wrote one rule as ``scientific_admissible`` and again as
    ``ideal_product`` and compared them, and the difference was two identifiers.
    """

    params = [a.arg for a in fn.args.args] + [a.arg for a in fn.args.kwonlyargs]
    rename = {name: f"__p{i}" for i, name in enumerate(params)}

    class _Normalise(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name) -> ast.AST:
            if node.id in rename:
                return ast.copy_location(ast.Name(id=rename[node.id], ctx=node.ctx), node)
            return node

    body = ast.Module(body=[ast.fix_missing_locations(_Normalise().visit(ast.parse(ast.unparse(st)))) for st in fn.body], type_ignores=[])
    return ast.dump(body)

def scan_source(source: str, *, path: str) -> list[SelfComparison]:
    """Every self-resolving comparison in one module."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    twins: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                twins[node.name] = _body_signature(node)
            except (SyntaxError, RecursionError, AttributeError):
                continue

    out: list[SelfComparison] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        aliases = _alias_map(fn)
        calls = _call_signatures(fn)
        for node in ast.walk(fn):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1:
                continue
            left, right = node.left, node.comparators[0]

            # Inline calls: identical invocations, or two functions whose bodies
            # are the same rule written twice.
            if isinstance(left, ast.Call) and isinstance(right, ast.Call):
                finding = _inline_call_finding(left, right, node, twins, fn=fn, path=path)
                if finding is not None:
                    out.append(finding)
                continue

            if not (isinstance(left, ast.Name) and isinstance(right, ast.Name)):
                continue
            root_left = _resolve(left.id, aliases)
            root_right = _resolve(right.id, aliases)
            same_call = (
                left.id != right.id
                and left.id in calls
                and right.id in calls
                and calls[left.id] == calls[right.id]
            )
            if root_left != root_right and not same_call:
                continue
            if same_call:
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
                        root=f"{calls[left.id][0]}(...) called twice on one argument list",
                        constant_value=_CONSTANT_OPS[op],
                        context=_classify(node, fn),
                    )
                )
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
                    context=_classify(node, fn),
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

def _same_arguments(left: ast.Call, right: ast.Call) -> bool:
    """Positional *and* keyword arguments, compared as written."""

    def shape(call: ast.Call) -> str:
        args = ast.dump(ast.Tuple(elts=list(call.args), ctx=ast.Load()))
        keywords = "|".join(
            f"{kw.arg}={ast.dump(kw.value)}" for kw in sorted(call.keywords, key=lambda k: k.arg or "")
        )
        return f"{args}#{keywords}"

    return shape(left) == shape(right)

def _classify(node: ast.Compare, fn: ast.FunctionDef | ast.AsyncFunctionDef) -> Context:
    """Decide what the comparison feeds, from the statement that contains it."""

    if fn.name.startswith("test_"):
        return Context.ASSERTS
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            if child is not node:
                continue
            if isinstance(parent, ast.Assert):
                return Context.ASSERTS
            if isinstance(parent, ast.If):
                for statement in ast.walk(parent):
                    if isinstance(statement, ast.AugAssign):
                        return Context.COUNTS
                    if (
                        isinstance(statement, ast.Call)
                        and isinstance(statement.func, ast.Attribute)
                        and statement.func.attr == "append"
                    ):
                        return Context.COUNTS
    return Context.UNCLASSIFIED

def _callee_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None

def _inline_call_finding(
    left: ast.Call,
    right: ast.Call,
    node: ast.Compare,
    twins: dict[str, str],
    *,
    fn: ast.FunctionDef | ast.AsyncFunctionDef,
    path: str,
) -> SelfComparison | None:
    op = type(node.ops[0])
    if op not in _CONSTANT_OPS:
        return None
    left_callee, right_callee = _callee_name(left), _callee_name(right)
    if left_callee is None or right_callee is None:
        return None
    if left_callee in _NONDETERMINISTIC_HINTS or right_callee in _NONDETERMINISTIC_HINTS:
        return None

    if not _same_arguments(left, right):
        return None

    # The receiver is part of the callee. ``left.fingerprint(mode)`` and
    # ``right.fingerprint(mode)`` share an attribute name and an argument list
    # and are calls on two different objects; comparing the attribute name alone
    # reported seven such lines in P9 as constant when every one is a real test.
    if ast.dump(left.func) == ast.dump(right.func):
        root = f"{left_callee}(...) called twice on one receiver and one argument list"
    elif (
        isinstance(left.func, ast.Name)
        and isinstance(right.func, ast.Name)
        and left_callee != right_callee
        and left_callee in twins
        and right_callee in twins
        and twins[left_callee] == twins[right_callee]
    ):
        root = (
            f"{left_callee}() and {right_callee}() have identical bodies -- "
            "one rule written twice"
        )
    else:
        return None

    return SelfComparison(
        path=path,
        line=node.lineno,
        function=fn.name,
        operator=op.__name__,
        expression=f"{left_callee}(...) {_OP_TEXT[op]} {right_callee}(...)",
        root=root,
        constant_value=_CONSTANT_OPS[op],
        context=_classify(node, fn),
    )

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
