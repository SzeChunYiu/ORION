#!/usr/bin/env python3
"""Emit the per-case table behind the mechanical arm's published 62/66 (issue #283).

`research/verification/records/P1.mechanical-arm-62-66.json` is the only one of
eight verification records at `CANNOT_CHECK`, for a stated reason: *"62/66 is
documented only in markdown; independent case-level replay is CANNOT_CHECK"*, and
`layers.denominator_statistics` reads *"cannot audit 62/66 without the case
table"*. A count that exists only as prose cannot be re-derived by a verifier.

Everything needed was already committed -- the 66-case suite under
`protocol/cases/{pilot,test}` and the LLM-free reduction layer in
`orion.study.p1.contradiction` -- so this does not measure anything new. It runs
`top_responsibility` over each case's public view and writes what it saw.

No LLM, no credential, no protected host: the arm reads only the public prompt
and observable resources, and the gold is read from the case only to score.
"""

from __future__ import annotations

import json
import sys
import subprocess
from pathlib import Path

from orion.study.p1.cases import PublicView, Split, load_cases, suite_fingerprint
from orion.study.p1.contradiction import top_responsibility

PAPER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PAPER_ROOT.parents[1]
CASES_ROOT = PAPER_ROOT / "protocol" / "cases"
OUTPUT_PATH = PAPER_ROOT / "evidence" / "MECHANICAL_ARM_CASE_TABLE_V1.json"

#: Responsibilities that are formulation faults. The published control claim is
#: that no negative control receives one of these -- not that controls receive
#: nothing, which is a weaker and different statement.
FORMULATION_RESPONSIBILITIES = frozenset(
    {"REPRESENTATION", "DECOMPOSITION", "MEASUREMENT", "PARENT"}
)


def _label(value: object) -> str | None:
    """Enum -> its wire value. `None` stays `None`: abstention is an outcome."""

    if value is None:
        return None
    return getattr(value, "value", None) or getattr(value, "name", None) or str(value)


def build_table() -> dict[str, object]:
    by_split = {split: load_cases(CASES_ROOT, split=split) for split in Split}
    cases = tuple(case for split in Split for case in by_split[split])
    # Both the combined and the per-split fingerprints. The verification record
    # binds PILOT `7a50a2d5…` and TEST `21b461d8…` separately, so a single
    # all-66 fingerprint would be uncheckable against it -- different population,
    # different hash, and no way for a reader to tell that from a mismatch.
    split_fingerprints = {
        split.value: suite_fingerprint(by_split[split]) for split in Split if by_split[split]
    }
    rows: list[dict[str, object]] = []
    for case in cases:
        view = PublicView(
            case_id=case.case_id,
            public_prompt=case.public_prompt,
            observable_resources=case.observable_resources,
            budget_class=case.budget_class,
        )
        predicted = _label(top_responsibility(view))
        gold = _label(case.protected_gold.responsibility_family)
        rows.append(
            {
                "case_id": case.case_id,
                "split": case.split.value,
                "task_family": case.task_family,
                "is_negative_control": not case.protected_gold.reframe_required,
                "responsibility_gold": gold,
                "responsibility_predicted": predicted,
                "correct": predicted == gold,
                "abstained": predicted is None,
            }
        )
    rows.sort(key=lambda row: str(row["case_id"]))

    controls = [row for row in rows if row["is_negative_control"]]
    formulation = [row for row in rows if not row["is_negative_control"]]
    control_false_positives = [
        row for row in controls if row["responsibility_predicted"] in FORMULATION_RESPONSIBILITIES
    ]
    return {
        "schema_version": "orion.p1.mechanical-arm-case-table.v1",
        "issue": 283,
        "grants_authority": "NONE",
        "closes_gate": None,
        "claim_scope": (
            "Descriptive diagnostic replay of the LLM-free reduction layer. Not H1 "
            "support, not a matched baseline comparison, and not evidence of "
            "external superiority."
        ),
        "suite_fingerprint": suite_fingerprint(cases),
        "split_suite_fingerprints": split_fingerprints,
        "arm_module": "orion.study.p1.contradiction.top_responsibility",
        "summary": {
            "total_cases": len(rows),
            "correct": sum(1 for row in rows if row["correct"]),
            "formulation_cases": len(formulation),
            "formulation_correct": sum(1 for row in formulation if row["correct"]),
            "negative_controls": len(controls),
            "controls_given_a_formulation_responsibility": len(control_false_positives),
            "abstentions": sum(1 for row in rows if row["abstained"]),
        },
        "mismatches": [
            {
                "case_id": row["case_id"],
                "responsibility_gold": row["responsibility_gold"],
                "responsibility_predicted": row["responsibility_predicted"],
            }
            for row in rows
            if not row["correct"]
        ],
        "cases": rows,
    }


def check() -> list[str]:
    """Compare the committed table against a live re-run.

    `subject_commit` is provenance, not substance: it changes on every commit, so
    comparing it would make this check fail on any commit that did not regenerate
    the table -- a checker that cries wolf on its first real run gets switched
    off. Everything that describes what the arm *did* is compared.
    """

    committed = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    derived = build_table()
    ignored = {"subject_commit"}
    left = {key: value for key, value in committed.items() if key not in ignored}
    right = {key: value for key, value in derived.items() if key not in ignored}
    if left == right:
        return []
    errors: list[str] = []
    if left.get("summary") != right.get("summary"):
        errors.append(f"summary: committed {left.get('summary')} != derived {right.get('summary')}")
    if left.get("split_suite_fingerprints") != right.get("split_suite_fingerprints"):
        errors.append("split_suite_fingerprints differ: the frozen suite changed")
    if left.get("mismatches") != right.get("mismatches"):
        errors.append(f"mismatches: committed {left.get('mismatches')} != derived {right.get('mismatches')}")
    if not errors:
        errors.append("committed table differs from a live re-run; regenerate it")
    return errors


def main() -> int:
    if "--check" in sys.argv[1:]:
        errors = check()
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0

    payload = build_table()
    payload["subject_commit"] = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
