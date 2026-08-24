"""What the P5 candidate may not see, and what the host must record.

SWE-bench hands a task instance that carries both the problem and its answer.
`gold_patch` is the fix. `test_patch` is the test that detects the fix.
`FAIL_TO_PASS` and `PASS_TO_PASS` name the tests by which resolution is
decided. A candidate that receives any of them is not solving the task, it is
reading the answer -- and its score is a transcription score.

The V4 execution binding already froze the list of fields a candidate may never
see. What it did not do is enforce it, so nothing stopped a packet from
carrying one. This module is that enforcement, and it reads the frozen list from
the committed artifact rather than restating it, so the two cannot drift.

The second half is the other side of the same run. The issue requires the host
to record FAIL_TO_PASS, PASS_TO_PASS, invalid, no-op and harmful edits, and
cost. Those five are not decoration:

* an **invalid** edit does not apply, so it is not evidence about the method;
* a **no-op** edit applies and changes nothing, and counting it as an attempt
  inflates the denominator while counting it as a failure inflates the numerator
  of harm;
* a **harmful** edit breaks tests that previously passed, which is the outcome a
  resolved-rate alone cannot see.

A receipt that omits them can report a resolved-rate that is arithmetically
correct and scientifically empty. So the validator refuses a receipt that is
missing any of them, and refuses one whose counts do not reconcile.

Exit codes: 0 PASS, 2 forbidden field visible to the candidate, 3 outcome record
incomplete, 4 counts do not reconcile, 5 malformed -- could not check.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "EDIT_DISPOSITIONS",
    "EXIT_CANNOT_CHECK",
    "EXIT_FORBIDDEN_FIELD",
    "EXIT_INCOMPLETE_RECORD",
    "EXIT_PASS",
    "EXIT_UNRECONCILED",
    "REQUIRED_OUTCOME_FIELDS",
    "CustodyVerdict",
    "check_candidate_packet",
    "check_outcome_record",
    "load_forbidden_fields",
    "main",
]

FROZEN_REQUIREMENTS = Path(
    "development/p5-swe-agent-execution-binding-v4-2026-08-23/"
    "P5_C1_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json"
)

#: What the host must record for every attempted instance.
REQUIRED_OUTCOME_FIELDS: tuple[str, ...] = (
    "instance_id",
    "fail_to_pass",
    "pass_to_pass",
    "edit_disposition",
    "cost",
)

#: Every way an edit can land. Closed, so an unclassified edit is an error
#: rather than an implicit success.
EDIT_DISPOSITIONS: frozenset[str] = frozenset(
    {"APPLIED_RESOLVED", "APPLIED_UNRESOLVED", "INVALID", "NO_OP", "HARMFUL"}
)

EXIT_PASS = 0
EXIT_FORBIDDEN_FIELD = 2
EXIT_INCOMPLETE_RECORD = 3
EXIT_UNRECONCILED = 4
EXIT_CANNOT_CHECK = 5


@dataclass(frozen=True)
class CustodyVerdict:
    exit_code: int
    terminal: str
    problems: tuple[str, ...] = field(default=())

    @property
    def passed(self) -> bool:
        return self.exit_code == EXIT_PASS


def load_forbidden_fields(root: Path) -> tuple[str, ...] | None:
    """Read the frozen forbidden-field list. Never restate it here."""

    try:
        document = json.loads((root / FROZEN_REQUIREMENTS).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fields = document.get("forbidden_candidate_fields")
    if not isinstance(fields, list) or not fields:
        return None
    return tuple(str(name) for name in fields)


def _walk_keys(node: Any, path: str = "") -> list[tuple[str, str]]:
    """Every key in the packet, at any depth, with the path that reaches it."""

    found: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            found.append((str(key), here))
            found.extend(_walk_keys(value, here))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(_walk_keys(value, f"{path}[{index}]"))
    return found


def check_candidate_packet(packet: Any, forbidden: tuple[str, ...]) -> CustodyVerdict:
    """Refuse a candidate packet that carries any field the freeze forbids.

    The search is by key at any depth. Burying ``gold_patch`` inside a nested
    ``metadata`` object hides it from a reader, not from the candidate.
    """

    if not isinstance(packet, dict):
        return CustodyVerdict(EXIT_CANNOT_CHECK, "P5_CUSTODY_CANNOT_CHECK", ("packet is not an object",))
    if not forbidden:
        return CustodyVerdict(
            EXIT_CANNOT_CHECK, "P5_CUSTODY_CANNOT_CHECK", ("frozen forbidden-field list is unavailable",)
        )

    banned = {name.lower() for name in forbidden}
    problems = [
        f"forbidden field {key!r} is visible to the candidate at {where}"
        for key, where in _walk_keys(packet)
        if key.lower() in banned
    ]
    if problems:
        return CustodyVerdict(EXIT_FORBIDDEN_FIELD, "P5_CUSTODY_FAIL", tuple(sorted(problems)))
    return CustodyVerdict(EXIT_PASS, "P5_CUSTODY_PASS")


def check_outcome_record(record: Any) -> CustodyVerdict:
    """Refuse a host outcome record that cannot support a resolved-rate."""

    if not isinstance(record, dict):
        return CustodyVerdict(EXIT_CANNOT_CHECK, "P5_OUTCOME_CANNOT_CHECK", ("record is not an object",))

    missing = [name for name in REQUIRED_OUTCOME_FIELDS if name not in record]
    if missing:
        return CustodyVerdict(
            EXIT_INCOMPLETE_RECORD,
            "P5_OUTCOME_FAIL",
            (f"outcome record omits {sorted(missing)}; a resolved-rate from it would be unaudited",),
        )

    disposition = record.get("edit_disposition")
    if disposition not in EDIT_DISPOSITIONS:
        return CustodyVerdict(
            EXIT_INCOMPLETE_RECORD,
            "P5_OUTCOME_FAIL",
            (f"edit_disposition {disposition!r} outside {sorted(EDIT_DISPOSITIONS)}",),
        )

    problems: list[str] = []
    for name in ("fail_to_pass", "pass_to_pass"):
        value = record.get(name)
        if not isinstance(value, dict) or "passed" not in value or "total" not in value:
            problems.append(f"{name} must carry both 'passed' and 'total'")
            continue
        passed, total = value["passed"], value["total"]
        if not isinstance(passed, int) or not isinstance(total, int) or isinstance(passed, bool) or isinstance(total, bool):
            problems.append(f"{name}: passed/total must be integers")
        elif passed > total or passed < 0 or total < 0:
            problems.append(f"{name}: passed={passed} total={total} does not reconcile")
    if problems:
        return CustodyVerdict(EXIT_UNRECONCILED, "P5_OUTCOME_FAIL", tuple(problems))

    cost = record.get("cost")
    if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
        return CustodyVerdict(EXIT_UNRECONCILED, "P5_OUTCOME_FAIL", ("cost must be a non-negative number",))

    # A resolved claim has to be consistent with the tests it rests on.
    if disposition == "APPLIED_RESOLVED":
        f2p, p2p = record["fail_to_pass"], record["pass_to_pass"]
        if f2p["passed"] != f2p["total"] or p2p["passed"] != p2p["total"]:
            return CustodyVerdict(
                EXIT_UNRECONCILED,
                "P5_OUTCOME_FAIL",
                ("APPLIED_RESOLVED requires every FAIL_TO_PASS and PASS_TO_PASS test to pass",),
            )
    if disposition == "NO_OP" and record.get("diff_bytes", 0):
        return CustodyVerdict(
            EXIT_UNRECONCILED, "P5_OUTCOME_FAIL", ("NO_OP recorded with a non-empty diff",)
        )
    if disposition == "HARMFUL":
        p2p = record["pass_to_pass"]
        if p2p["passed"] == p2p["total"]:
            return CustodyVerdict(
                EXIT_UNRECONCILED,
                "P5_OUTCOME_FAIL",
                ("HARMFUL recorded while every PASS_TO_PASS test still passes",),
            )
    return CustodyVerdict(EXIT_PASS, "P5_OUTCOME_PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--record", type=Path)
    args = parser.parse_args(argv)

    forbidden = load_forbidden_fields(args.root)
    if forbidden is None:
        print("P5_CUSTODY_CANNOT_CHECK: frozen forbidden-field list unavailable", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    print(f"frozen forbidden fields: {len(forbidden)} -> {', '.join(forbidden)}")

    worst = EXIT_PASS
    for path, checker in ((args.packet, "packet"), (args.record, "record")):
        if path is None:
            continue
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"P5_CANNOT_CHECK: {error}", file=sys.stderr)
            return EXIT_CANNOT_CHECK
        verdict = (
            check_candidate_packet(document, forbidden)
            if checker == "packet"
            else check_outcome_record(document)
        )
        for problem in verdict.problems:
            print(f"  {problem}", file=sys.stderr)
        print(verdict.terminal)
        worst = max(worst, verdict.exit_code)
    return worst


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
