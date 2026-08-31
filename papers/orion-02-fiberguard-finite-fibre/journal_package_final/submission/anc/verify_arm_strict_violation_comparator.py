#!/usr/bin/env python3
"""Reconstruct the frozen STUDY_F paired strict-violation comparator fail-closed."""
from __future__ import annotations

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
from typing import Any

GEOMETRY = "STUDY_F_ARM_CONDITIONAL_BOUNDARY_FIBRES"
CONTROL = "STUDY_F_LEXICAL_GOOD_BOUNDARY_NEGATIVE_CONTROL"
CONTROL_SUMMARY = "STUDY_F_LEXICAL_MATCHED_PRIMARY"
EXPECTED_TERMINAL = "C_STUDY_F_ARM_CONDITIONAL_CERTIFICATE_INVALID"
MAX_STRICT_VIOLATION_RATE = 0.10
EXPECTED_N = 44


class ReconstructionError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReconstructionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_two_sided_mcnemar(primary_only: int, control_only: int) -> float:
    discordant = primary_only + control_only
    if discordant == 0:
        return 1.0
    lower = min(primary_only, control_only)
    one_tail_numerator = sum(comb(discordant, k) for k in range(lower + 1))
    return min(1.0, 2.0 * one_tail_numerator / (2**discordant))


def reconstruct(result: dict[str, Any], *, source_sha256: str) -> dict[str, Any]:
    require(result.get("terminal") == EXPECTED_TERMINAL, "STUDY_F terminal drift")
    folds = result.get("folds")
    require(isinstance(folds, dict), "folds must be an object")
    geometry_folds = folds.get(GEOMETRY)
    control_folds = folds.get(CONTROL)
    require(isinstance(geometry_folds, dict), "geometry folds missing")
    require(isinstance(control_folds, dict), "lexical-control folds missing")
    require(set(geometry_folds) == set(control_folds), "geometry/control fold IDs differ")

    pairs: list[dict[str, Any]] = []
    seen: set[str] = set()
    both = primary_only = control_only = neither = 0
    for fold_id in sorted(geometry_folds, key=lambda value: int(value)):
        geometry_fold = geometry_folds[fold_id]
        control_fold = control_folds[fold_id]
        require(isinstance(geometry_fold, dict), f"geometry fold {fold_id} malformed")
        require(isinstance(control_fold, dict), f"control fold {fold_id} malformed")
        selected_arm = geometry_fold.get("primary")
        require(isinstance(selected_arm, str) and selected_arm, f"geometry fold {fold_id} primary missing")
        geometry_tests = geometry_fold.get("test")
        control_tests = control_fold.get("test")
        require(isinstance(geometry_tests, dict), f"geometry fold {fold_id} test map missing")
        require(isinstance(control_tests, dict), f"control fold {fold_id} test map missing")
        geometry_rows = geometry_tests.get(selected_arm)
        control_rows = control_tests.get(selected_arm)
        require(isinstance(geometry_rows, dict), f"geometry fold {fold_id} selected-arm rows missing")
        require(isinstance(control_rows, dict), f"control fold {fold_id} selected-arm rows missing")
        require(set(geometry_rows) == set(control_rows), f"fold {fold_id} paired dataset set differs")
        role_tests = geometry_fold.get("roles", {}).get("test")
        require(isinstance(role_tests, list), f"geometry fold {fold_id} role test set missing")
        require(set(role_tests) == set(geometry_rows), f"geometry fold {fold_id} rows do not match frozen test role")
        require(
            set(control_fold.get("roles", {}).get("test", [])) == set(control_rows),
            f"control fold {fold_id} rows do not match frozen test role",
        )

        for dataset in sorted(geometry_rows):
            require(dataset not in seen, f"dataset appears in more than one test fold: {dataset}")
            seen.add(dataset)
            primary_flag = geometry_rows[dataset].get("violation_strict")
            control_flag = control_rows[dataset].get("violation_strict")
            require(type(primary_flag) is bool, f"primary violation_strict is not Boolean: {dataset}")
            require(type(control_flag) is bool, f"control violation_strict is not Boolean: {dataset}")
            if primary_flag and control_flag:
                both += 1
            elif primary_flag:
                primary_only += 1
            elif control_flag:
                control_only += 1
            else:
                neither += 1
            pairs.append(
                {
                    "control_violation_strict": control_flag,
                    "dataset": dataset,
                    "fold": int(fold_id),
                    "primary_violation_strict": primary_flag,
                    "selected_arm": selected_arm,
                }
            )

    n = len(pairs)
    require(n == EXPECTED_N, f"expected {EXPECTED_N} unique held-out rows, found {n}")
    primary_count = both + primary_only
    control_count = both + control_only
    primary_summary = result.get("primary")
    arms_summary = result.get("arms_summary")
    require(isinstance(primary_summary, dict), "primary summary missing")
    require(isinstance(arms_summary, dict), "arms summary missing")
    control_summary = arms_summary.get(CONTROL_SUMMARY)
    require(isinstance(control_summary, dict), "matched lexical-control summary missing")
    require(primary_summary.get("n") == n, "primary summary n mismatch")
    require(control_summary.get("n") == n, "control summary n mismatch")
    require(primary_summary.get("violations_strict") == primary_count, "primary summary violation count mismatch")
    require(control_summary.get("violations_strict") == control_count, "control summary violation count mismatch")

    primary_rate = primary_count / n
    control_rate = control_count / n
    p_value = exact_two_sided_mcnemar(primary_only, control_only)
    return {
        "schema": "ANON.STUDY_FStrictViolationComparatorCorrection.v1",
        "source": {
            "result_schema": result.get("schema"),
            "sha256": source_sha256,
            "terminal": result.get("terminal"),
        },
        "matching_rule": (
            "For each frozen fold, apply the geometry fold's serialized selected primary arm "
            "to both the geometry and matched lexical-control test maps; pair by dataset name."
        ),
        "n": n,
        "primary": {
            "strict_violations": primary_count,
            "strict_violation_rate": primary_rate,
            "maximum_registered_rate": MAX_STRICT_VIOLATION_RATE,
            "gate": "FAIL" if primary_rate > MAX_STRICT_VIOLATION_RATE else "PASS",
        },
        "matched_lexical_control": {
            "strict_violations": control_count,
            "strict_violation_rate": control_rate,
            "maximum_registered_rate": MAX_STRICT_VIOLATION_RATE,
            "gate": "FAIL" if control_rate > MAX_STRICT_VIOLATION_RATE else "PASS",
        },
        "paired_contingency": {
            "both_violate": both,
            "primary_only_violates": primary_only,
            "control_only_violates": control_only,
            "neither_violates": neither,
        },
        "mcnemar_exact_two_sided_p": p_value,
        "pairs": pairs,
        "correction": {
            "historical_cannot_check_interpretation": "RETRACTED",
            "reason": "The committed fold records do serialize paired violation_strict flags for the geometry-selected arm in both policies.",
            "science_terminal_unchanged": True,
            "geometry_superiority": "NOT_SUPPORTED",
            "lexical_broad_superiority": "NOT_ESTABLISHED",
            "bounded_result": "The geometry policy has six additional strict violations and no fewer on this frozen endpoint; both policies fail the registered 0.10 validity gate.",
        },
        "does_not_certify": [
            "a valid certificate for either policy",
            "broad superiority of lexical selection",
            "unseen-instance or cross-domain transfer",
            "external replication or independence",
        ],
    }


def main() -> int:
    default = Path(__file__).resolve().parent / "failed-executions/3550275/run_a.result.json"
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=default)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(args.results.read_text(encoding="utf-8"))
    report = reconstruct(result, source_sha256=sha256(args.results))
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
