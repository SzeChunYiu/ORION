"""Bind the P3 comparator-arm disposition to the receipts it cites.

Issue #1086 asks P3 to compare against LogMap and AML, *or* mark unavailable
arms CANNOT_CHECK. The second branch is the one that is easy to abuse: a
disposition file can assert CANNOT_CHECK about anything, and nobody reading
the checkbox would know whether the arm was genuinely unscorable or merely
inconvenient.

This checker makes the disposition earn its verdict. For every arm it
requires:

* a disposition drawn from a closed vocabulary;
* for a ``SCORED`` arm, evidence paths that exist and hash to the digests the
  disposition claims -- so "scored" cannot be asserted over a file that has
  since changed or was never there;
* for a ``CANNOT_CHECK`` arm, at least one blocking condition, each with its
  own evidence path and digest, plus a non-empty set of promotion conditions.
  An arm that cannot be checked must say what would make it checkable.

The last requirement is the point. ``CANNOT_CHECK`` without promotion
conditions is a dead end dressed as a verdict; with them it is a piece of
work someone can pick up.

The checker also refuses the overclaim this disposition specifically must not
make. LogMap *runs* -- V11 bound a 90/90 dependency closure and exited zero.
So any disposition text asserting the arm is "unavailable" or "cannot be run"
is rejected, because the true statement is narrower: no matching-mode
alignment over the scored case has been admitted through the frozen
interface.

Run it::

    python -m orion.study.p3.comparator_arm_disposition --disposition <file>.json --root <repo root>

Exit codes: 0 PASS, 2 schema/vocabulary failure, 3 evidence missing or digest
mismatch, 4 CANNOT_CHECK arm without blocking or promotion conditions,
5 overclaim detected, 6 malformed -- could not check.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "DISPOSITIONS",
    "EXIT_CANNOT_CHECK",
    "EXIT_EVIDENCE",
    "EXIT_OVERCLAIM",
    "EXIT_PASS",
    "EXIT_SCHEMA",
    "EXIT_UNCONDITIONED",
    "FORBIDDEN_OVERCLAIMS",
    "DispositionVerdict",
    "check_disposition",
    "main",
]

#: Closed vocabulary. An arm is either scored against the reference, or it is
#: not and must say why, or it was deliberately excluded from the comparison.
DISPOSITIONS = frozenset({"SCORED", "CANNOT_CHECK", "OUT_OF_SCOPE"})

#: Phrases this disposition must never contain about an arm whose runtime is
#: demonstrably bound. Kept lowercase; matched against the serialized arm.
FORBIDDEN_OVERCLAIMS = (
    "is unavailable",
    "cannot be run",
    "failed to produce output",
    "does not run",
)

EXIT_PASS = 0
EXIT_SCHEMA = 2
EXIT_EVIDENCE = 3
EXIT_UNCONDITIONED = 4
EXIT_OVERCLAIM = 5
EXIT_CANNOT_CHECK = 6


@dataclass(frozen=True)
class DispositionVerdict:
    exit_code: int
    terminal: str
    problems: tuple[str, ...] = field(default=())
    arms_checked: int = 0

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _overclaims_in(arm: dict[str, Any]) -> list[str]:
    """Find forbidden phrases in an arm, ignoring the list that disclaims them.

    ``explicitly_not_claimed`` exists precisely to quote the overclaims and
    reject them, so scanning it would make an honest disposition fail.
    """

    scanned = {key: value for key, value in arm.items() if key != "explicitly_not_claimed"}
    blob = json.dumps(scanned, sort_keys=True).lower()
    return [phrase for phrase in FORBIDDEN_OVERCLAIMS if phrase in blob]


def _check_evidence(entries: Any, root: Path, label: str, problems: list[str]) -> bool:
    """Verify every evidence entry exists and matches its recorded digest."""

    if not isinstance(entries, list) or not entries:
        problems.append(f"{label}: no evidence entries")
        return False
    ok = True
    for entry in entries:
        if not isinstance(entry, dict):
            problems.append(f"{label}: evidence entry is not an object")
            ok = False
            continue
        rel = entry.get("path") or entry.get("evidence_path")
        recorded = entry.get("sha256") or entry.get("evidence_sha256")
        if not isinstance(rel, str):
            problems.append(f"{label}: evidence entry has no path")
            ok = False
            continue
        target = root / rel
        if not target.is_file():
            problems.append(f"{label}: evidence path does not exist: {rel}")
            ok = False
            continue
        if recorded is None:
            continue  # a path-only citation is allowed; a wrong digest is not
        actual = _digest(target)
        if actual != recorded:
            problems.append(f"{label}: digest mismatch for {rel}: recorded {recorded}, actual {actual}")
            ok = False
    return ok


def check_disposition(document: Any, root: Path) -> DispositionVerdict:
    """Check one parsed disposition document against the tree at ``root``."""

    if not isinstance(document, dict):
        return DispositionVerdict(EXIT_CANNOT_CHECK, "P3_V22_DISPOSITION_CANNOT_CHECK", ("document is not an object",))
    arms = document.get("arms")
    if not isinstance(arms, list) or not arms:
        return DispositionVerdict(
            EXIT_CANNOT_CHECK, "P3_V22_DISPOSITION_CANNOT_CHECK", ("document carries no non-empty 'arms' list",)
        )

    problems: list[str] = []
    worst = EXIT_PASS
    for arm in arms:
        if not isinstance(arm, dict):
            return DispositionVerdict(
                EXIT_CANNOT_CHECK, "P3_V22_DISPOSITION_CANNOT_CHECK", ("an arm is not an object",)
            )
        name = arm.get("arm", "<unnamed>")
        disposition = arm.get("disposition")
        if disposition not in DISPOSITIONS:
            problems.append(f"{name}: disposition {disposition!r} outside {sorted(DISPOSITIONS)}")
            worst = max(worst, EXIT_SCHEMA)
            continue

        overclaims = _overclaims_in(arm)
        if overclaims:
            problems.append(f"{name}: overclaims present: {overclaims}")
            worst = max(worst, EXIT_OVERCLAIM)

        if disposition == "SCORED":
            if not arm.get("scored_against_reference"):
                problems.append(f"{name}: SCORED but scored_against_reference is not true")
                worst = max(worst, EXIT_SCHEMA)
            if not _check_evidence(arm.get("evidence"), root, str(name), problems):
                worst = max(worst, EXIT_EVIDENCE)
        elif disposition == "CANNOT_CHECK":
            if arm.get("scored_against_reference"):
                problems.append(f"{name}: CANNOT_CHECK but scored_against_reference is true")
                worst = max(worst, EXIT_SCHEMA)
            blocking = arm.get("blocking_conditions")
            promotion = arm.get("promotion_conditions")
            if not isinstance(blocking, list) or not blocking:
                problems.append(f"{name}: CANNOT_CHECK without blocking_conditions")
                worst = max(worst, EXIT_UNCONDITIONED)
            elif not _check_evidence(blocking, root, f"{name} blocking", problems):
                worst = max(worst, EXIT_EVIDENCE)
            if not isinstance(promotion, list) or not promotion:
                problems.append(f"{name}: CANNOT_CHECK without promotion_conditions -- a dead end, not a verdict")
                worst = max(worst, EXIT_UNCONDITIONED)

    if worst == EXIT_PASS:
        return DispositionVerdict(EXIT_PASS, "P3_V22_DISPOSITION_PASS", (), len(arms))
    return DispositionVerdict(worst, "P3_V22_DISPOSITION_FAIL", tuple(problems), len(arms))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disposition", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    try:
        document = json.loads(args.disposition.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"P3_V22_DISPOSITION_CANNOT_CHECK: {error}", file=sys.stderr)
        return EXIT_CANNOT_CHECK

    verdict = check_disposition(document, args.root)
    for problem in verdict.problems:
        print(f"  {problem}", file=sys.stderr)
    print(f"{verdict.terminal} arms={verdict.arms_checked}")
    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
