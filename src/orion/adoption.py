from __future__ import annotations

import ast
import pathlib
from dataclasses import dataclass
from enum import Enum

#: Module-level constant a V2 surface sets to declare its adoption state.
#: Written as a plain string so the declaration is readable by AST without
#: importing the module — an import-time check would be defeated by the very
#: coupling it is meant to detect.
ADOPTION_ATTRIBUTE = "ADOPTION_BOUNDARY"


class AdoptionState(str, Enum):
    """Where a module sits relative to the frozen V1 surfaces.

    Issue #136 requires paper integrations to live in additive V2 harnesses
    "until separately execution-frozen". That makes *having no production
    consumer* the correct state for a V2 surface rather than a defect — the
    opposite of what an orphan audit assumes.

    This distinction was previously carried only in prose at the top of each
    module. An audit for unwired code therefore reported `staged_gate` as an
    orphan when it was behaving exactly as its issue required, and nothing
    would have caught the reverse error either: a V1 runtime path quietly
    importing a V2 surface and adopting it without an execution freeze.
    """

    #: Part of a frozen V1 surface. Ordinary rules apply.
    V1_FROZEN = "V1_FROZEN"
    #: An additive V2 mechanism. Unconsumed by design; being consumed by a V1
    #: runtime path is the defect, not being unconsumed.
    V2_ADDITIVE = "V2_ADDITIVE"
    #: Neither declared. Most of the repository, and not an error.
    UNDECLARED = "UNDECLARED"


@dataclass(frozen=True)
class AdoptionViolation:
    importer: str
    imported: str
    reason: str


def declared_state(path: pathlib.Path) -> AdoptionState:
    """Read a module's declared adoption state without importing it."""

    try:
        tree = ast.parse(path.read_text())
    except (SyntaxError, OSError):
        return AdoptionState.UNDECLARED
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == ADOPTION_ATTRIBUTE:
                value = node.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    try:
                        return AdoptionState(value.value)
                    except ValueError:
                        return AdoptionState.UNDECLARED
    return AdoptionState.UNDECLARED


def _module_name(path: pathlib.Path, root: pathlib.Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    parts = [part for part in relative.parts if part != "__init__"]
    return ".".join(["orion", *parts[1:]]) if parts and parts[0] == "orion" else ".".join(parts)


def find_adoption_violations(source_root: pathlib.Path) -> tuple[AdoptionViolation, ...]:
    """V1-frozen modules that import a V2-additive one.

    The direction matters and only one direction is a fault. A V2 surface may
    read anything it likes from V1 — that is what building on a frozen base
    means. A V1 surface importing V2 has adopted a mechanism that was required
    to stay additive until separately execution-frozen, and it has done so
    without the freeze.
    """

    states: dict[str, AdoptionState] = {}
    trees: dict[str, ast.Module] = {}
    for path in sorted(source_root.rglob("*.py")):
        name = _module_name(path, source_root)
        states[name] = declared_state(path)
        try:
            trees[name] = ast.parse(path.read_text())
        except (SyntaxError, OSError):
            continue

    additive = {name for name, state in states.items() if state is AdoptionState.V2_ADDITIVE}
    violations: list[AdoptionViolation] = []
    for name, tree in trees.items():
        if states.get(name) is not AdoptionState.V1_FROZEN:
            continue
        for node in ast.walk(tree):
            targets: list[str] = []
            if isinstance(node, ast.ImportFrom) and node.module:
                targets.append(node.module)
            elif isinstance(node, ast.Import):
                targets.extend(alias.name for alias in node.names)
            for target in targets:
                if target in additive:
                    violations.append(
                        AdoptionViolation(
                            importer=name,
                            imported=target,
                            reason=(
                                "a V1-frozen module imports a V2-additive surface; "
                                "adoption requires a separate execution freeze"
                            ),
                        )
                    )
    return tuple(violations)


__all__ = [
    "ADOPTION_ATTRIBUTE",
    "AdoptionState",
    "AdoptionViolation",
    "declared_state",
    "find_adoption_violations",
]
