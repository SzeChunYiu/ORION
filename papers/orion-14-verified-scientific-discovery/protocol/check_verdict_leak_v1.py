#!/usr/bin/env python3
"""Reject attack cases whose candidate-visible text states the verdict.

A gold case is supposed to present evidence from which a system must *infer* the
correct authority terminal. If the candidate-visible text also announces the
answer -- "the evidence is genuinely insufficient to support the claim" -- then a
system can score correctly by reading rather than by judging, and the family stops
measuring the capability it names.

This is not hypothetical. In `ATTACK_MANIFEST_V1.jsonl`, all three
`INSUFFICIENT_EVIDENCE` cases end with a sentence naming the verdict, and no case
in the other twelve families does. Those are exactly the cases behind P4's H3, and
`correct_cannot_check_rate` is 1.0 for all eleven panel systems -- the metric has
no observed variance anywhere in the study. A leak of this shape is the simplest
explanation available for a whole-panel ceiling.

The contrast within the manifest makes the intended style clear. The
`POOLED_SUPPORT_WRONG_OWNER` cases also involve insufficient support, and describe
it structurally -- "the pooled evidence only demonstrates refusal direction, not
general steering" -- without naming a verdict. That is inference-demanding. The
`INSUFFICIENT_EVIDENCE` cases state the conclusion instead.

Exit codes: 0 clean, 1 leaks found, 2 the manifest could not be read (distinct from
clean, because "could not check" must never be reported as "checked and fine").
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: The battery in force. V1 is the frozen historical record and is deliberately
#: NOT repaired -- `ATTACK_MANIFEST_V2_SUPERSESSION_V1.md` says so in as many
#: words, because a benchmark whose construction is repaired is a new benchmark
#: and the old one has to stay a reproducible record of what was measured.
#:
#: Pointing the default at V1 therefore made this checker report FAIL forever,
#: on a battery nobody scores, for a leak that was found, documented and fixed in
#: V2. A red that means "the frozen historical artifact is still the way we
#: recorded it" is not a defect report, and a check that can never go green stops
#: being read.
DEFAULT_MANIFEST = HERE / "ATTACK_MANIFEST_V2.jsonl"

#: Kept as the checker's detection-power control, against real data rather than a
#: fixture: V1 must still trip. If it ever comes back clean, the phrase list has
#: been broken and the clean verdict on V2 means nothing.
HISTORICAL_LEAKING_MANIFEST = HERE / "ATTACK_MANIFEST_V1.jsonl"
EXPECTED_HISTORICAL_LEAKS = 3

#: Phrases that assert a verdict rather than describe evidence.
#:
#: Deliberately narrow. "n=5", "no confidence intervals" and "not peer reviewed"
#: are facts a reader must weigh and are exactly what a good case supplies; they
#: are not matched here. What is matched is a sentence that performs the judgement
#: on the reader's behalf.
VERDICT_PHRASES = (
    r"is genuinely insufficient",
    r"is insufficient to support",
    r"evidence is insufficient",
    r"cannot be verified",
    r"cannot be checked",
    r"is not sufficient to",
    r"clearly supports the claim",
    r"fully supports the claim",
    r"directly supports the claim",
    r"adequately supports the claim",
    r"is sufficient to support",
    r"the correct (?:answer|terminal|verdict) is",
)
LEAK = re.compile("|".join(VERDICT_PHRASES), re.IGNORECASE)


def leaks_in(case: dict) -> list[str]:
    """Verdict-stating phrases anywhere in the text the candidate can see."""

    visible = case.get("candidate_visible") or {}
    blob = " ".join(str(value) for value in visible.values())
    return sorted({match.group(0).lower() for match in LEAK.finditer(blob)})


def _historical_control() -> int | None:
    """How many cases still leak in the frozen V1 battery, or None if unreadable.

    Returning None rather than 0 matters: "could not run the control" and "the
    control found nothing" are different worlds, and only one of them is a reason
    to distrust a clean result.
    """

    if not HISTORICAL_LEAKING_MANIFEST.is_file():
        return None
    try:
        rows = [
            json.loads(line)
            for line in HISTORICAL_LEAKING_MANIFEST.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except json.JSONDecodeError:
        return None
    return sum(1 for row in rows if leaks_in(row))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)

    if not args.manifest.is_file():
        print(f"CANNOT_CHECK: no manifest at {args.manifest}", file=sys.stderr)
        return 2
    try:
        cases = [
            json.loads(line)
            for line in args.manifest.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except json.JSONDecodeError as error:
        print(f"CANNOT_CHECK: manifest is not valid JSONL: {error}", file=sys.stderr)
        return 2
    if not cases:
        print("CANNOT_CHECK: manifest is empty", file=sys.stderr)
        return 2

    findings: list[tuple[str, str, list[str]]] = []
    for case in cases:
        hits = leaks_in(case)
        if hits:
            findings.append(
                (case.get("case_id", "<no id>"), case.get("attack_family", "<none>"), hits)
            )

    if not findings:
        # Clean is only meaningful if the phrase list can still catch the leak it
        # was written for. V1 is the known-leaking real battery, so it is the
        # control -- not a fixture, and not something that can drift into
        # agreement with the checker.
        control = _historical_control()
        if control is None:
            print(
                "CANNOT_CHECK: the historical leaking manifest is absent, so a clean "
                "verdict here cannot be distinguished from a broken phrase list",
                file=sys.stderr,
            )
            return 2
        if control != EXPECTED_HISTORICAL_LEAKS:
            print(
                f"CANNOT_CHECK: the control found {control} leaks in "
                f"{HISTORICAL_LEAKING_MANIFEST.name}, expected {EXPECTED_HISTORICAL_LEAKS}. "
                "The phrase list has changed; this run's clean verdict proves nothing.",
                file=sys.stderr,
            )
            return 2
        print(
            f"VERDICT LEAK CHECK: clean ({len(cases)} cases in {args.manifest.name}; "
            f"control: {control} leaks still detected in {HISTORICAL_LEAKING_MANIFEST.name})"
        )
        return 0

    by_family: dict[str, int] = {}
    for _, family, _ in findings:
        by_family[family] = by_family.get(family, 0) + 1

    print(f"VERDICT LEAK CHECK: FAIL — {len(findings)}/{len(cases)} cases state the verdict")
    for case_id, family, hits in findings:
        print(f"  {case_id} [{family}]: {', '.join(hits)}")
    print()
    print("Affected families:")
    for family, count in sorted(by_family.items(), key=lambda kv: -kv[1]):
        print(f"  {family}: {count}")
    print()
    print(
        "A case that names its own verdict is scored by reading, not by judging. Describe\n"
        "the evidence and let the terminal follow from it, as the BLOCK families already do."
    )
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
