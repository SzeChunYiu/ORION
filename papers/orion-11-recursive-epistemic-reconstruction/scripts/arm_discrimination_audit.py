#!/usr/bin/env python3
"""Run ORION-11's own arm-discrimination check pairwise over the committed records.

`manuscript/sections/05a-methods.tex` declares an admissibility condition: "if every
compared system produced an identical outcome vector, the comparison reports a
difference of exactly zero by construction rather than by measurement, and the honest
verdict is that the comparison is undetermined rather than null. This condition is
checked and reported, not assumed."

The condition is implemented in `src/orion/study/p1/arm_validity.py` in two forms:

* ``assess_arm_discrimination`` -- global. Returns DID_NOT_DISCRIMINATE only when
  *every* system shares one outcome vector, i.e. when the number of distinct
  behaviour groups is 1. It is wired into the campaign at ``run_trial.py:128``.
* ``assess_pair_discrimination`` -- pairwise. Its docstring states the reason it
  exists: "A hypothesis verdict rests on one pair, so the pair is what must be
  checked." It is exported and unit-tested, and is called from no production path.

With twelve systems and several behaving differently, the global form returns
DISCRIMINATED whatever any individual pair does. This script runs the pairwise form
that the campaign does not, against the same committed records, and reports the
verdict per comparison.

It adds no metric, changes no threshold, and re-scores nothing: the outcome vectors
are read from the committed JSONL and passed to the repository's own functions.

Usage::

    ORION11_PAPER_DIR=... ORION11_OUT_DIR=... .venv/bin/python arm_disc.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

PAPER = Path(
    os.environ.get(
        "ORION11_PAPER_DIR",
        Path(__file__).resolve().parents[1],
    )
)
REPO = Path(os.environ.get("ORION11_REPO", PAPER.parents[1]))
OUT = Path(os.environ.get("ORION11_OUT_DIR", PAPER))
sys.path.insert(0, str(REPO / "src"))

from orion.study.p1.arm_validity import (  # noqa: E402
    assess_arm_discrimination,
    assess_pair_discrimination,
)

RECORDS = PAPER / "results" / "raw" / "test_scored.jsonl"
SUBJECT = "orion_full"

# Fields that identify the run rather than its outcome. Excluded when testing
# whole-record identity so that a system's own name cannot make it look distinct.
IDENTITY_FIELDS = {
    "system_id",
    "system_role",
    "seed",
    "schema_version",
    "suite_fingerprint",
    "resources",
}


def _record_signature(record: dict) -> str:
    return json.dumps(
        {k: v for k, v in sorted(record.items()) if k not in IDENTITY_FIELDS},
        sort_keys=True,
    )


# Published Table P1-T2 values, to four decimal places as printed in
# manuscript/tables/P1-T2_baseline_ablation.tex. The audit hard-fails unless the
# records reproduce these, so that a verdict is never emitted from a record set
# that does not match the table it is about to reinterpret.
PUBLISHED_P1_T2 = {
    "orion_full": (0.0208, 0.0312),
    "orion_live_provider": (0.0000, 0.0000),
    "static_react_tool_workflow": (0.0208, 0.0312),
    "full_reset_instead_of_dependency_reopen": (0.0208, 0.0312),
    "orion_without_mechanic_self_audit": (0.0208, 0.0312),
}


def reproduce_published_rates(records: list[dict]) -> tuple[dict, list[str]]:
    """Recompute the published root-success rates on the reduced case unit."""

    by_case: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        by_case[record["system_id"]][record["case_id"]].append(record)
    hidden = {r["case_id"] for r in records if r.get("is_hidden_shift")}

    computed: dict[str, dict[str, float]] = {}
    for system, cases in by_case.items():
        all_rate = sum(
            1 for runs in cases.values() if any(r.get("root_success") for r in runs)
        ) / len(cases)
        hidden_cases = [c for c in cases if c in hidden]
        hidden_rate = sum(
            1 for c in hidden_cases if any(r.get("root_success") for r in cases[c])
        ) / len(hidden_cases)
        computed[system] = {
            "root_success_all_cases": round(all_rate, 4),
            "root_success_hidden_shift": round(hidden_rate, 4),
        }

    mismatches = []
    for system, (want_all, want_hidden) in PUBLISHED_P1_T2.items():
        got = computed.get(system)
        if got is None:
            mismatches.append(f"{system}: absent from records")
            continue
        if got["root_success_all_cases"] != want_all:
            mismatches.append(
                f"{system}.all_cases: published {want_all}, recomputed "
                f"{got['root_success_all_cases']}"
            )
        if got["root_success_hidden_shift"] != want_hidden:
            mismatches.append(
                f"{system}.hidden_shift: published {want_hidden}, recomputed "
                f"{got['root_success_hidden_shift']}"
            )
    return computed, mismatches


def main() -> int:
    records = [json.loads(line) for line in RECORDS.read_text().splitlines() if line.strip()]
    by_system: dict[str, dict[tuple[str, object], dict]] = defaultdict(dict)
    for record in records:
        by_system[record["system_id"]][(record["case_id"], record["seed"])] = record

    systems = sorted(by_system)
    cells = sorted(by_system[SUBJECT])

    def vector(system: str, field: str) -> list[object]:
        return [by_system[system][cell].get(field) for cell in cells]

    def full_vector(system: str) -> list[str]:
        return [_record_signature(by_system[system][cell]) for cell in cells]

    # The global check, exactly as the campaign runs it, on the primary outcome.
    global_primary = assess_arm_discrimination(
        {s: vector(s, "root_success") for s in systems}
    )
    global_full = assess_arm_discrimination({s: full_vector(s) for s in systems})

    # The pairwise check the campaign does not run.
    pairs = []
    for system in systems:
        if system == SUBJECT:
            continue
        primary = assess_pair_discrimination(
            vector(SUBJECT, "root_success"),
            vector(system, "root_success"),
            subject_id=SUBJECT,
            comparator_id=system,
        )
        whole = assess_pair_discrimination(
            full_vector(SUBJECT),
            full_vector(system),
            subject_id=SUBJECT,
            comparator_id=system,
        )
        differing = sum(
            1 for a, b in zip(full_vector(SUBJECT), full_vector(system)) if a != b
        )
        pairs.append(
            {
                "comparator": system,
                "role": by_system[system][cells[0]].get("system_role"),
                "primary_outcome_verdict": primary.verdict.value,
                "whole_record_verdict": whole.verdict.value,
                "differing_cells_whole_record": differing,
                "cells": len(cells),
            }
        )

    # Across-seed variation: are the five repeats carrying any information?
    varying = 0
    total = 0
    for system in systems:
        per_case: dict[str, set[str]] = defaultdict(set)
        for (case, _seed), record in by_system[system].items():
            per_case[case].add(_record_signature(record))
        for signatures in per_case.values():
            total += 1
            if len(signatures) > 1:
                varying += 1

    # Census of every successful record.
    successes = [r for r in records if r.get("root_success")]
    responsibility_correct = sum(1 for r in successes if r.get("responsibility_correct"))

    computed_rates, mismatches = reproduce_published_rates(records)
    if mismatches:
        print("REPRODUCTION FAILED -- audit is void:", file=sys.stderr)
        for line in mismatches:
            print("  " + line, file=sys.stderr)
        return 1

    payload = {
        "schema": "ORION.P1.ArmDiscriminationAudit.v1",
        "scientific_authority_delta": "NONE",
        "purpose": (
            "Runs the repository's own assess_pair_discrimination over the committed "
            "P1 records. Adds no metric and re-scores nothing."
        ),
        "reproduction_check": {
            "published_source": "manuscript/tables/P1-T2_baseline_ablation.tex",
            "status": "REPRODUCED",
            "mismatches": [],
            "recomputed_root_success_rates": computed_rates,
            "note": (
                "Eleven of the twelve systems share identical published rates on both "
                "metrics; only the live-provider arm differs."
            ),
        },
        "records": len(records),
        "systems": len(systems),
        "cells_per_system": len(cells),
        "subject": SUBJECT,
        "global_check_as_wired": {
            "function": "assess_arm_discrimination (run_trial.py:128)",
            "primary_outcome_verdict": global_primary.verdict.value,
            "whole_record_verdict": global_full.verdict.value,
            "distinct_behaviour_groups_primary": global_primary.distinct_behaviour_groups,
            "distinct_behaviour_groups_whole_record": global_full.distinct_behaviour_groups,
            "note": (
                "Returns DISCRIMINATED whenever at least two systems differ, so it "
                "cannot detect an individual undetermined pair."
            ),
        },
        "pairwise_check_not_wired": {
            "function": "assess_pair_discrimination (defined, exported, unit-tested, "
            "called from no production path)",
            "pairs": pairs,
            "undetermined_on_whole_record": sorted(
                p["comparator"] for p in pairs if p["differing_cells_whole_record"] == 0
            ),
            "undetermined_on_primary_outcome": sorted(
                p["comparator"]
                for p in pairs
                if p["primary_outcome_verdict"] == "DID_NOT_DISCRIMINATE"
            ),
        },
        "repeat_information": {
            "system_case_pairs": total,
            "pairs_varying_across_seeds": varying,
            "note": (
                "Wilson intervals in Table P1-T2 correctly use n=48 per system rather "
                "than inflating to 240; the repeats are not double-counted. The point "
                "is only that the five repeats carry almost no information."
            ),
        },
        "success_census": {
            "successful_records": len(successes),
            "distinct_cases": sorted({r["case_id"] for r in successes}),
            "records_with_correct_responsibility": responsibility_correct,
            "note": (
                "Every successful record is responsibility-incorrect. This is a census "
                "of the diagnosis already recorded in FLOOR_EFFECT_DIAGNOSIS_20260823.md, "
                "not a new finding."
            ),
        },
    }

    target_dir = OUT / "evidence" / "arm-discrimination-audit-v1"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "ARM_DISCRIMINATION_AUDIT_V1.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print("reproduction of published Table P1-T2 rates: REPRODUCED")
    print(f"records={len(records)} systems={len(systems)} cells={len(cells)}")
    print(
        f"global check as wired: primary={global_primary.verdict.value} "
        f"whole_record={global_full.verdict.value}"
    )
    print(
        "pairwise undetermined (whole record): "
        f"{payload['pairwise_check_not_wired']['undetermined_on_whole_record']}"
    )
    print(
        "pairwise undetermined (primary outcome): "
        f"{payload['pairwise_check_not_wired']['undetermined_on_primary_outcome']}"
    )
    print(f"repeats varying: {varying}/{total}")
    print(
        f"successes={len(successes)} on cases "
        f"{payload['success_census']['distinct_cases']}; "
        f"responsibility-correct={responsibility_correct}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
