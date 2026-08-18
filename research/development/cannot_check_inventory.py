#!/usr/bin/env python3
"""Derive the inventory of every `CANNOT_CHECK` site in `src/orion` (issue #322).

Issue #322 needs a machine-readable inventory that can be *re-derived* after each
dependency changes, not a snapshot taken once. So this is a generator with a
committed output and a `--check` mode, following `research/publication/scoreboard.py`:
the artifact is derived, and drift between derived and committed is a test failure
rather than something a reader has to notice.

Two decisions are load-bearing.

**`UNCLASSIFIED` is not `OTHER`.** A site whose reason cannot be extracted has not
been classified as "none of the above" -- it has not been classified at all. An
earlier draft of this inventory put 197 of 199 sites in `OTHER` with the literal
placeholder `<call_with_CANNOT_CHECK>` as their reason, which reports a checker
that ran as a checker that worked. The two states are counted separately here, and
`unclassified` is the number that has to come down.

**Sites are classified from evidence, never from position.** The rules read the
reason text and the enclosing names. When none matches, the site is `UNCLASSIFIED`;
nothing is assigned a category because it happened to sit in a particular file.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "src" / "orion"
INVENTORY_PATH = Path(__file__).resolve().parent / "cannot_check_inventory.json"
SCHEMA_VERSION = "orion.cannot-check-inventory.v2"

#: Issue #322's blocker vocabulary, plus the explicit "could not classify" state.
CATEGORIES = (
    "MISSING_IDENTITY",
    "MISSING_CUSTODY",
    "MISSING_ACCESS",
    "UNAVAILABLE_PROVIDER",
    "INSUFFICIENT_EVIDENCE",
    "UNCLASSIFIED",
)

#: Ordered (category, substrings) rules, first match wins. Ordering matters: a
#: reason naming both an absent provider and an unbound identity is a provider
#: problem, because supplying the provider is what would produce the identity.
CLASSIFICATION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "UNAVAILABLE_PROVIDER",
        ("provider", "api_key", "apikey", "credential", "entitlement", "model_unavailable", "llm"),
    ),
    (
        "MISSING_CUSTODY",
        ("custody", "protected", "evaluator", "holdout", "held_out", "heldout", "outside_the_answering_lane"),
    ),
    (
        "MISSING_ACCESS",
        ("access", "unreachable", "network", "paywall", "inaccessible", "not_found", "missing_file"),
    ),
    (
        "MISSING_IDENTITY",
        ("unbound", "identity", "revision", "hash", "fingerprint", "subject", "epoch", "not_declared", "undeclared"),
    ),
    (
        "INSUFFICIENT_EVIDENCE",
        (
            "insufficient",
            "no_evidence",
            "no evidence",
            "not_executed",
            "not executed",
            "were executed",
            "unexecuted",
            "not_run",
            "not run",
            "empty",
            "zero_",
            "no_samples",
            "no samples",
            "underpowered",
        ),
    ),
)
# Blocker codes in this repository are snake_case, but reasons also appear as
# prose in receipts and error strings. Both spellings are listed rather than
# normalising separators, which would make `zero_` match "zero " and pull in
# unrelated numeric text.


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _is_cannot_check(node: ast.AST) -> bool:
    """True for the string literal and for `SomeEnum.CANNOT_CHECK`."""

    if isinstance(node, ast.Constant) and node.value == "CANNOT_CHECK":
        return True
    return isinstance(node, ast.Attribute) and node.attr == "CANNOT_CHECK"


#: Statement kinds that *observe* an existing `CANNOT_CHECK` rather than produce
#: one. `if status is Status.CANNOT_CHECK:` is a consumer, not a blocker, and
#: counting it as one inflates the inventory with sites that have nothing to
#: resolve.
OBSERVING_KINDS = frozenset({"BRANCH"})


def _site_kind(statement: ast.AST) -> str:
    if isinstance(statement, ast.Return):
        return "RETURN"
    if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return "ASSIGN"
    if isinstance(statement, ast.Raise):
        return "RAISE"
    if isinstance(statement, (ast.If, ast.While)):
        return "BRANCH"
    if isinstance(statement, ast.Expr):
        return "EXPRESSION"
    if isinstance(statement, ast.ClassDef):
        return "ENUM_MEMBER"
    return "OTHER_STATEMENT"


def _reason_strings(statement: ast.AST) -> tuple[str, ...]:
    """Every string literal in the statement other than `CANNOT_CHECK` itself.

    A `CANNOT_CHECK` carrying a reason nearly always carries it as a sibling
    literal in the same statement -- a returned tuple, a call argument, an appended
    blocker code. Reading the statement rather than the single node is what makes
    the difference between a reason and a placeholder.
    """

    found: list[str] = []
    for node in ast.walk(statement):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value.strip()
            if value and value != "CANNOT_CHECK" and len(value) > 2:
                found.append(value)
    return tuple(dict.fromkeys(found))


def classify(reasons: tuple[str, ...], context: str) -> str:
    """Classify from the reason text and enclosing names, or say so."""

    haystack = " ".join((*reasons, context)).lower()
    for category, needles in CLASSIFICATION_RULES:
        if any(needle in haystack for needle in needles):
            return category
    return "UNCLASSIFIED"


def _enclosing(tree: ast.AST) -> dict[int, tuple[str, ast.AST]]:
    """Map each node id to (qualified enclosing name, enclosing statement)."""

    mapping: dict[int, tuple[str, ast.AST]] = {}

    def walk(node: ast.AST, prefix: str, statement: ast.AST | None) -> None:
        name = prefix
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{prefix}.{node.name}" if prefix else node.name
        current = node if isinstance(node, ast.stmt) else statement
        mapping[id(node)] = (name, current or node)
        for child in ast.iter_child_nodes(node):
            walk(child, name, current)

    walk(tree, "", None)
    return mapping


def collect_sites(source_root: Path = SOURCE_ROOT) -> list[dict[str, object]]:
    sites: list[dict[str, object]] = []
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        enclosing = _enclosing(tree)
        for node in ast.walk(tree):
            if not _is_cannot_check(node):
                continue
            context, statement = enclosing.get(id(node), ("", node))
            reasons = _reason_strings(statement)
            kind = _site_kind(statement)
            role = "OBSERVES" if kind in OBSERVING_KINDS else "EMITS"
            sites.append(
                {
                    "file": str(path.relative_to(source_root)),
                    "lineno": getattr(node, "lineno", 0),
                    "context": context,
                    "kind": kind,
                    "role": role,
                    "reasons": list(reasons),
                    "has_reason": bool(reasons),
                    "category": classify(reasons, context) if role == "EMITS" else "NOT_A_BLOCKER",
                }
            )
    sites.sort(key=lambda site: (site["file"], site["lineno"], site["context"]))
    return sites


def derive_inventory(source_root: Path = SOURCE_ROOT) -> dict[str, object]:
    sites = collect_sites(source_root)
    blockers = [site for site in sites if site["role"] == "EMITS"]
    counts = {category: 0 for category in CATEGORIES}
    for site in blockers:
        counts[str(site["category"])] += 1
    return {
        "schema_version": SCHEMA_VERSION,
        "issue": 322,
        "grants_authority": "NONE",
        "closes_gate": None,
        "source_root": str(source_root.relative_to(REPO_ROOT)),
        "total_sites": len(sites),
        "blocker_sites": len(blockers),
        "observing_sites": len(sites) - len(blockers),
        "with_reason": sum(1 for site in blockers if site["has_reason"]),
        "classification": counts,
        "unclassified_note": (
            "UNCLASSIFIED means the site carried no extractable reason, not that it "
            "was examined and found to be none of the listed categories. Driving this "
            "count down is the work; reclassifying it to OTHER is not."
        ),
        "sites": sites,
    }


def _comparable(payload: dict[str, object]) -> dict[str, object]:
    """The parts that must match; `subject_commit`/`generated_at` are informational."""

    return {key: value for key, value in payload.items() if key not in {"subject_commit", "generated_at"}}


def validate_inventory(committed: dict[str, object], source_root: Path = SOURCE_ROOT) -> list[str]:
    derived = derive_inventory(source_root)
    if _comparable(committed) == _comparable(derived):
        return []
    errors: list[str] = []
    if committed.get("total_sites") != derived["total_sites"]:
        errors.append(
            f"total_sites: committed {committed.get('total_sites')} != derived {derived['total_sites']}"
        )
    if committed.get("classification") != derived["classification"]:
        errors.append(
            f"classification: committed {committed.get('classification')} != derived {derived['classification']}"
        )
    committed_keys = {(s["file"], s["lineno"]) for s in committed.get("sites", [])}  # type: ignore[union-attr]
    derived_keys = {(s["file"], s["lineno"]) for s in derived["sites"]}  # type: ignore[index]
    for missing in sorted(derived_keys - committed_keys)[:10]:
        errors.append(f"site absent from committed inventory: {missing[0]}:{missing[1]}")
    for extra in sorted(committed_keys - derived_keys)[:10]:
        errors.append(f"committed site no longer exists: {extra[0]}:{extra[1]}")
    if not errors:
        errors.append("inventories differ in site detail; regenerate with --write")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the committed inventory")
    parser.add_argument("--check", action="store_true", help="fail if committed differs from derived")
    args = parser.parse_args()

    if args.write:
        payload = derive_inventory()
        payload["subject_commit"] = _git("rev-parse", "HEAD")
        INVENTORY_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {INVENTORY_PATH.relative_to(REPO_ROOT)}: {payload['total_sites']} sites")
        print(json.dumps(payload["classification"], indent=2, sort_keys=True))
        return 0

    if args.check:
        errors = validate_inventory(json.loads(INVENTORY_PATH.read_text(encoding="utf-8")))
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0

    print(json.dumps(derive_inventory(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
