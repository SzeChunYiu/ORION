#!/usr/bin/env python3
"""Make A6's ideal-donor tie a measurement instead of a tautology.

Gate L432 of ORION-paper#49 reads: "ideal typed donor ties exactly (otherwise the
comparison is not isolating the claimed relation)". As shipped, the gate cannot
fail: `merged_candidate` and `information_equivalent_typed_donor` both delegate to
`typed_full_relation`, so `candidate == ideal` is true by construction over all 81
typed states. A control that cannot fail certifies nothing.

This re-derives the ideal donor *independently* -- from the stated semantics of an
information-equivalent typed relation, written against the coordinate alphabet
rather than by calling the candidate -- and ties it against the shipped candidate.
Now the gate can fail, and a later edit to either side is detectable.

Exit codes follow the repo convention: 0 clean, 2 a finding, 3 could not check.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHIPPED = ROOT / "papers/publication_closure/a6-external-authority-study-v1/baselines_v1.py"

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
ADMIT, DENY, CANNOT_CHECK = "ADMIT", "DENY", "CANNOT_CHECK"
COORDS = ("authorization", "provenance", "verification", "scientific_discharge")


def independent_ideal_donor(record: dict[str, str]) -> str:
    """Ideal donor re-derived from the stated semantics, not from the candidate.

    An information-equivalent typed donor sees every target-relevant coordinate and
    must therefore: deny if any coordinate refutes; admit only when every coordinate
    is discharged; otherwise report that it could not check. Written as an explicit
    fold so it shares no code with the candidate.
    """
    seen_unknown = False
    for coord in COORDS:
        value = record[coord]
        if value == FAIL:
            return DENY
        if value == UNKNOWN:
            seen_unknown = True
        elif value != PASS:
            raise ValueError(f"{coord} must be PASS/FAIL/UNKNOWN")
    return CANNOT_CHECK if seen_unknown else ADMIT


def main() -> int:
    if not SHIPPED.is_file():
        print(f"CANNOT CHECK: shipped A6 baselines not found at {SHIPPED}")
        return 3
    spec = importlib.util.spec_from_file_location("a6_shipped", SHIPPED)
    shipped = importlib.util.module_from_spec(spec)
    sys.modules["a6_shipped"] = shipped
    spec.loader.exec_module(shipped)

    disagreements = []
    discriminating = 0
    for values in itertools.product((PASS, FAIL, UNKNOWN), repeat=len(COORDS)):
        record = dict(zip(COORDS, values, strict=True))
        candidate = shipped.merged_candidate(record)
        ideal = independent_ideal_donor(record)
        if candidate != ideal:
            disagreements.append({"record": record, "candidate": candidate, "ideal": ideal})
        incomplete = shipped.strongest_combined_incomplete(record)
        if candidate != incomplete:
            discriminating += 1

    report = {
        "record": "A6_IDEAL_DONOR_TIE_V1",
        "typed_states": 81,
        "tie_is_independent": True,
        "disagreements": disagreements,
        "candidate_discriminates_from_incomplete_donor_states": discriminating,
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    if disagreements:
        print(f"FINDING: candidate and independently derived ideal donor disagree on "
              f"{len(disagreements)} of 81 typed states; the comparison does not isolate "
              f"the claimed relation")
        return 2
    if discriminating == 0:
        print("FINDING: the candidate never differs from the strongest incomplete donor; "
              "the scientific-discharge coordinate is inert and the study is non-discriminating")
        return 2
    print(f"TIE HOLDS against an independent derivation, and the candidate discriminates "
          f"from the strongest incomplete donor on {discriminating}/81 typed states")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
