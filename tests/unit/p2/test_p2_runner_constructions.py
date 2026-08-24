"""Every dataclass built in runner.py must match the dataclass as defined.

The #1078 vocabulary refactor changed systems.py and gold.py but never
migrated runner.py, and gold.py says so in its own docstring. The result was
five stale construction sites that raised TypeError the moment they ran --
found one at a time, each only when some path finally exercised it.

This is the audit that finds them all at once. It is the guard the refactor
lacked: any future rename that leaves a caller behind fails here rather than
at runtime, months later, inside a study that then reports zeros.

`SystemTrace` is a known-open exception, recorded rather than skipped. Its
migration is not a rename: route_events/read_events carry the deprecated
RouteEvent/ReadEvent types while the field now expects RouteTrial and
ReadEncounter, so fixing it needs a real type conversion and a decision about
repeat_index. Half-fixing it would be worse than leaving it visible.
"""

from __future__ import annotations

import ast
import dataclasses
import importlib
import pathlib

P2 = pathlib.Path(__file__).resolve().parents[3] / "src/orion/study/p2"

#: Constructions known to be stale, with why they are not fixed here.
KNOWN_OPEN = {
    "SystemTrace": (
        "route_events/read_events hold the deprecated RouteEvent/ReadEvent "
        "types; the fields now expect RouteTrial/ReadEncounter. A type "
        "conversion plus a repeat_index decision, not a rename."
    )
}


def _stale() -> dict[str, dict[str, list[str]]]:
    """Every module in the package, not just runner.py.

    Scoping this to one file was itself the bug's shape: the same rename had
    left callers behind in baselines.py and offline_systems.py, and a
    runner-only audit reported clean while two more sites still raised.
    """
    systems = importlib.import_module("orion.study.p2.systems")
    known = {n: c for n, c in vars(systems).items() if dataclasses.is_dataclass(c)}
    found: dict[str, dict[str, list[str]]] = {}
    nodes = []
    for path in sorted(P2.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            nodes.append((path.name, node))
    for module, node in nodes:
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        cls = known.get(node.func.id)
        if cls is None:
            continue
        fields = {f.name for f in dataclasses.fields(cls)}
        required = {
            f.name
            for f in dataclasses.fields(cls)
            if f.default is dataclasses.MISSING
            and f.default_factory is dataclasses.MISSING
        }
        passed = {kw.arg for kw in node.keywords if kw.arg}
        unknown, missing = sorted(passed - fields), sorted(required - passed)
        if unknown or missing:
            found[node.func.id] = {
                "unknown": unknown,
                "missing": missing,
                "module": module,
            }
    return found


def test_no_new_stale_construction_appears() -> None:
    stale = _stale()
    unexpected = {k: v for k, v in stale.items() if k not in KNOWN_OPEN}
    assert unexpected == {}, (
        f"stale dataclass constructions in runner.py: {unexpected}. "
        "A field was renamed without migrating its callers."
    )


def test_read_and_stop_paths_are_migrated() -> None:
    """The paths P2's own measurements read: reads, stops and reports."""
    stale = _stale()
    for name in ("ReadOutcome", "StopDecision", "ResourceUse", "SystemReport"):
        assert name not in stale, f"{name} is stale: {stale.get(name)}"


def test_the_known_open_defect_is_still_recorded() -> None:
    """If SystemTrace is fixed, this test must be updated rather than the
    defect quietly disappearing from the record."""
    stale = _stale()
    for name in KNOWN_OPEN:
        assert name in stale, (
            f"{name} no longer appears stale. If it was fixed, remove it from "
            "KNOWN_OPEN so the guard tightens instead of silently widening."
        )
