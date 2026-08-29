#!/usr/bin/env python3
"""Independent logical check for ORION01.OBSERVABLE_IDENTIFIABILITY.v1.

Reads the frozen parent result as data only. It imports no ORION-01 runner or PyZX module.
The general theorem is deductive; these checks establish that the recorded adverse
witnesses instantiate its premises and that the theorem detector can both fire and stay
silent on controls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def canonical_nf(value):
    return tuple(
        (str(k), tuple(v))
        for k, v in sorted(value.items(), key=lambda kv: int(kv[0]))
    )


def factorisation_conflicts(records):
    """Return O values associated with >1 semantic N value."""
    seen = {}
    conflicts = set()
    for observable, semantic in records:
        semantic = canonical_nf(semantic)
        if observable in seen and seen[observable] != semantic:
            conflicts.add(observable)
        else:
            seen.setdefault(observable, semantic)
    return conflicts


def nonempty_nf_states(nf):
    return sum(bool(v) for v in nf.values())


def check(result_path: Path) -> dict:
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    panel = payload["S2_hidden_operation_control"]
    witnesses = panel["witnesses"]
    mimic = witnesses["MIMIC"]
    false_improvement = witnesses["FALSE_IMPROVEMENT"]

    errors = []

    # The MIMIC premise: same observable, different extensional semantic object.
    if mimic["terminal_complexity_before"] != mimic["terminal_complexity_after"]:
        errors.append("MIMIC observable moved")
    if canonical_nf(mimic["normal_forms_before"]) == canonical_nf(mimic["normal_forms_after"]):
        errors.append("MIMIC semantic object did not move")

    conflicts = factorisation_conflicts([
        (mimic["terminal_complexity_before"], mimic["normal_forms_before"]),
        (mimic["terminal_complexity_after"], mimic["normal_forms_after"]),
    ])
    if not conflicts:
        errors.append("factorisation-conflict detector did not fire on MIMIC")

    # Negative control: identical semantics at the same observable must not create a conflict.
    benign = witnesses["BENIGN"]
    benign_conflicts = factorisation_conflicts([
        (benign["terminal_complexity_before"], benign["normal_forms_before"]),
        (benign["terminal_complexity_after"], benign["normal_forms_after"]),
    ])
    if benign_conflicts:
        errors.append("factorisation-conflict detector false-alarmed on BENIGN")

    # FALSE_IMPROVEMENT premise: metric improves while semantic preservation worsens.
    if not (
        false_improvement["terminal_complexity_after"]
        < false_improvement["terminal_complexity_before"]
    ):
        errors.append("FALSE_IMPROVEMENT metric did not improve")
    if not (
        nonempty_nf_states(false_improvement["normal_forms_after"])
        < nonempty_nf_states(false_improvement["normal_forms_before"])
    ):
        errors.append("FALSE_IMPROVEMENT did not lose normal-form coverage")

    totals = panel["classification_totals"]
    if totals.get("MIMIC", 0) <= 0:
        errors.append("no MIMIC examples recorded")
    if totals.get("FALSE_IMPROVEMENT", 0) <= 0:
        errors.append("no FALSE_IMPROVEMENT examples recorded")

    transitive = panel["by_hidden_operation_kind"]["TRANSITIVE_COMPOSITE"]
    if set(transitive) != {"BENIGN"} or transitive["BENIGN"] <= 0:
        errors.append("redundant TRANSITIVE_COMPOSITE control is not purely BENIGN")

    expected_terminal = "T1_CENSUS_COMPLETE__HIDDEN_OP_WITNESS_FOUND__CONFLUENCE_PARTIAL"
    if payload.get("terminal") != expected_terminal:
        errors.append(f"parent terminal mismatch: {payload.get('terminal')!r}")

    return {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "OBSERVABLE_NONIDENTIFIABILITY_PROVED__PRODUCTION_HIDDEN_OP_STILL_CANNOT_CHECK"
            if not errors else "CANNOT_CHECK_PARENT_WITNESS_BINDING"
        ),
        "mimic_count": totals.get("MIMIC"),
        "false_improvement_count": totals.get("FALSE_IMPROVEMENT"),
        "mimic_observable_collision": (
            mimic["terminal_complexity_before"] == mimic["terminal_complexity_after"]
        ),
        "mimic_semantic_difference": (
            canonical_nf(mimic["normal_forms_before"])
            != canonical_nf(mimic["normal_forms_after"])
        ),
        "benign_no_alarm": not benign_conflicts,
        "false_improvement_metric_decreases": (
            false_improvement["terminal_complexity_after"]
            < false_improvement["terminal_complexity_before"]
        ),
        "false_improvement_semantic_coverage_decreases": (
            nonempty_nf_states(false_improvement["normal_forms_after"])
            < nonempty_nf_states(false_improvement["normal_forms_before"])
        ),
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--result",
        default=(
            "papers/orion-01-certificate-realization/"
            "experiments/move-census-and-confluence-v1/RESULT_V1.json"
        ),
    )
    args = ap.parse_args()
    report = check(Path(args.result))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 5


if __name__ == "__main__":
    raise SystemExit(main())
