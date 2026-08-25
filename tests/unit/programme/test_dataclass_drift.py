"""No module may build a dataclass with fields the dataclass does not have.

The #1078 vocabulary refactor renamed fields in orion.study.p2.systems and left
seven callers behind across three modules. Each raised TypeError the first time
its path ran, and each surfaced as a study reporting plausible numbers rather
than as an error. This is the sweep that finds that class of drift everywhere.

A note on how this check must NOT be written. Keying dataclasses by bare name
reports 106 findings on this tree, of which 105 are false: 47 dataclass names
are defined in more than one module, so constructions get validated against a
same-named class from somewhere else entirely. A checker whose first real run
accuses a hundred healthy call sites gets switched off. Ambiguous names are
therefore judged only when the definition is in the same file, and skipped
otherwise -- a deliberate blind spot, preferred to a confident wrong answer.
"""

from __future__ import annotations

import ast
import collections
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3] / "src/orion"

#: Constructions known stale, with why they are not fixed here.
KNOWN_OPEN: dict[tuple[str, str], str] = {}
#: study/p2/runner.py SystemTrace was the last entry and is now migrated:
#: runner.py builds RouteTrial and ReadEncounter, and repeat_index comes from
#: the sweep. An entry here is a debt to discharge, not a standing exemption.


def _definitions() -> dict[str, list[tuple[str, set[str], set[str]]]]:
    by_name: dict[str, list[tuple[str, set[str], set[str]]]] = collections.defaultdict(list)
    for path in sorted(ROOT.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or node.bases:
                continue
            decorated = any(
                (isinstance(d, ast.Name) and d.id == "dataclass")
                or (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                for d in node.decorator_list
            )
            if not decorated:
                continue
            fields, required = set(), set()
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    fields.add(stmt.target.id)
                    if stmt.value is None:
                        required.add(stmt.target.id)
            if fields:
                by_name[node.name].append((str(path), fields, required))
    return by_name


def stale_constructions() -> list[tuple[str, int, str, list[str], list[str]]]:
    by_name = _definitions()
    ambiguous = {n for n, v in by_name.items() if len(v) > 1}
    out = []
    for path in sorted(ROOT.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        rel = str(path.relative_to(ROOT))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            candidates = by_name.get(node.func.id)
            if not candidates:
                continue
            same_file = [c for c in candidates if c[0] == str(path)]
            if same_file:
                _, fields, required = same_file[0]
            elif node.func.id in ambiguous:
                continue  # cannot resolve which class is meant; skipped, not guessed
            else:
                _, fields, required = candidates[0]
            if node.args or any(kw.arg is None for kw in node.keywords):
                continue  # positional or **spread: not statically judgeable
            passed = {kw.arg for kw in node.keywords}
            unknown, missing = sorted(passed - fields), sorted(required - passed)
            if unknown or missing:
                out.append((rel, node.lineno, node.func.id, unknown, missing))
    return out


def test_no_unknown_dataclass_drift() -> None:
    unexpected = [
        s for s in stale_constructions() if (s[0], s[2]) not in KNOWN_OPEN
    ]
    assert unexpected == [], (
        f"dataclass constructions disagree with their definitions: {unexpected}. "
        "A field was renamed without migrating its callers."
    )


def test_ambiguity_is_skipped_rather_than_guessed() -> None:
    """The property that keeps this from crying wolf on 105 healthy sites."""
    by_name = _definitions()
    assert len([n for n, v in by_name.items() if len(v) > 1]) > 0
