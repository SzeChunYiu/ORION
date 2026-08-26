"""What P6's mechanized results actually trust, derived rather than asserted.

A formal result is only as strong as the code that had to be correct for it to
hold. P6 states that independent proof review remains outstanding; the other
half of that disclosure is naming what stands in review's place, which is the
in-repository kernel the checkers import and the solver they defer to.

The set is computed by walking the transitive import closure of P6's formal
executables. Writing the list by hand would make the disclosure a claim about
the code rather than a reading of it, and a hand-written list goes stale the
first time an import changes.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

EXIT_PASS = 0
EXIT_DRIFTED = 2
EXIT_CANNOT_CHECK = 3

#: Modules whose correctness P6's mechanized results depend on, as disclosed.
DISCLOSED_KERNEL: tuple[str, ...] = (
    "orion.core.claims",
    "orion.programme.guard_exercise",
    "orion.programme.identity",
    "orion.programme.records",
    "orion.programme.refutation_capacity",
)

#: External solver the results defer to. Not reviewed by this project.
DISCLOSED_SOLVER: tuple[str, ...] = ("z3",)

#: Standard library and test scaffolding, excluded: they are not what a reader
#: means by a trusted base for a formal result.
_STDLIB_PREFIXES = (
    "__", "typing", "dataclasses", "pathlib", "json", "hashlib", "sys", "os",
    "re", "math", "itertools", "collections", "argparse", "subprocess",
    "functools", "enum", "textwrap", "random", "string", "statistics",
    "tempfile", "shutil", "csv", "time", "copy", "abc", "contextlib", "io",
    "operator", "warnings", "types", "unicodedata", "decimal", "fractions",
    "datetime", "uuid", "base64", "struct", "glob", "importlib", "unittest",
)


def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text())
    except (SyntaxError, OSError):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def derive(root: Path | None = None) -> tuple[set[str], set[str]]:
    """Return (orion modules, external non-stdlib) P6's formal code depends on."""
    root = root or Path(__file__).resolve().parents[3]
    formal = root / "papers/orion-16-formal-epistemic-structures-and-mechanics/formal"
    if not formal.is_dir():
        raise FileNotFoundError(formal)
    src = root / "src"
    frontier: set[str] = set()
    for f in sorted(formal.rglob("*.py")):
        frontier |= _imports(f)
    seen: set[str] = set()
    orion: set[str] = set()
    external: set[str] = set()
    while frontier:
        module = frontier.pop()
        if module in seen:
            continue
        seen.add(module)
        if module.startswith("orion"):
            orion.add(module)
            candidate = src / (module.replace(".", "/") + ".py")
            if candidate.is_file():
                frontier |= _imports(candidate)
        elif not module.startswith(_STDLIB_PREFIXES):
            top = module.split(".")[0]
            # local sibling scripts and the papers tree are not a trusted base
            if top not in {"papers"} and not (formal / f"{top}.py").is_file():
                external.add(top)
    return orion, external


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        orion, external = derive(args.root)
    except FileNotFoundError as exc:
        print(f"P6_TRUSTED_BASE_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    print("in-repository kernel P6's mechanized results trust:")
    for m in sorted(orion):
        print(f"   {m}")
    print("external solver deferred to, not reviewed here:")
    for m in sorted(external):
        print(f"   {m}")
    drift_k = orion ^ set(DISCLOSED_KERNEL)
    drift_s = external ^ set(DISCLOSED_SOLVER)
    if drift_k or drift_s:
        print(f"P6_TRUSTED_BASE_DRIFTED: kernel {sorted(drift_k)} solver {sorted(drift_s)}")
        print("the disclosure no longer matches what the code imports")
        return EXIT_DRIFTED
    print("P6_TRUSTED_BASE_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
