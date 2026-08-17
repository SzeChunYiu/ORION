#!/usr/bin/env python3
"""Independent implementation verifier for P1 mutation-necessity v2.2.4.

This verifier is intentionally frozen before the primary confirmatory terminal is
read.  It imports neither ``necessity_scoring`` nor ``necessity_policies`` nor
``necessity_statistics``.  It consumes only serialized public worlds, protected
response matrices, candidate outcomes, the execution receipt, and the archived
aggregate result.  Task scores and primary statistics are reimplemented here
from the written contract.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import gzip
import hashlib
import json
from math import comb
from pathlib import Path
import random
from typing import Any, Iterable, Mapping, Sequence

HIGH_LEVELS = frozenset({"FORMULATION", "SEARCH_UNIVERSE"})
LOW_LEVELS = frozenset({"EVIDENCE", "EXECUTION"})


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_lines(path: Path) -> list[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    mode = "rt"
    with opener(path, mode, encoding="utf-8") as handle:  # type: ignore[arg-type]
        return [json.loads(line) for line in handle if line.strip()]


def _prf(predicted: set[str], gold: set[str]) -> tuple[float, float, float]:
    if not predicted and not gold:
        return 1.0, 1.0, 1.0
    precision = len(predicted & gold) / len(predicted) if predicted else 0.0
    recall = len(predicted & gold) / len(gold) if gold else (1.0 if not predicted else 0.0)
    f1 = 0.0 if precision + recall == 0.0 else 2.0 * precision * recall / (precision + recall)
    return precision, recall, f1


@dataclass(frozen=True)
class IndependentScore:
    task_id: str
    family_id: str
    arm_id: str
    hidden_shift: bool
    negative_control: bool
    protected_root_task_success: bool
    selected_repair_id: str | None
    selected_level: str
    selected_repair_tested: bool
    target_success: bool
    protected_sibling_ok: bool
    protected_sibling_regression: bool
    unnecessary_high_level_reframe: bool
    forbidden_high_level_mutation: bool
    dependency_reopen_precision: float
    dependency_reopen_recall: float
    dependency_reopen_f1: float
    unrelated_closure_reopened: bool
    spent_budget: float

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def score_outcome(
    public: Mapping[str, Any],
    protected: Mapping[str, Any],
    outcome: Mapping[str, Any],
) -> IndependentScore:
    repair_by_id = {str(item["repair_id"]): item for item in public["repairs"]}
    responses = protected["response_by_repair"]
    arm_id = str(outcome.get("arm_id", ""))
    selected_raw = outcome.get("selected_repair_id")
    selected_id = None if selected_raw in (None, "") else str(selected_raw)
    tested_ids = {str(item) for item in outcome.get("tested_repair_ids", ())}
    reopened = {str(item) for item in outcome.get("reopened_ids", ())}
    spent = float(outcome.get("spent_budget", 0.0))

    selected_level = "NONE"
    selected_tested = selected_id is None
    target_success = False
    sibling_ok = True
    sibling_regression = False
    high_level = False
    if selected_id is not None:
        if selected_id not in repair_by_id:
            raise ValueError(f"unknown selected repair:{public['task_id']}:{selected_id}")
        repair = repair_by_id[selected_id]
        selected_level = str(repair["level"])
        high_level = selected_level in HIGH_LEVELS
        selected_tested = selected_id in tested_ids
        response = responses[selected_id]
        target_success = bool(response["target_success"])
        sibling_ok = bool(response["protected_sibling_ok"])
        sibling_regression = not sibling_ok

    gold_ids = {str(item) for item in protected["gold_minimal_repair_ids"]}
    minimal_selected = selected_id is not None and selected_id in gold_ids
    lower_valid_exists = False
    if bool(protected["negative_control"]):
        minimal_levels = {str(repair_by_id[repair_id]["level"]) for repair_id in gold_ids}
        lower_valid_exists = bool(minimal_levels.intersection(LOW_LEVELS))
    unnecessary_high = bool(protected["negative_control"] and high_level and lower_valid_exists)
    forbidden_high = unnecessary_high

    gold_impact = {str(item) for item in protected["gold_dependency_impact_ids"]}
    unrelated = {
        str(item["closure_id"])
        for item in public["dependencies"]
        if str(item["declared_coordinate"]) == "UNRELATED"
    }
    precision, recall, f1 = _prf(reopened, gold_impact)
    unrelated_reopened = bool(reopened.intersection(unrelated))

    if selected_id is None:
        protected_success = False
    elif not selected_tested or not target_success or not sibling_ok:
        protected_success = False
    elif not minimal_selected:
        protected_success = False
    elif high_level:
        protected_success = f1 == 1.0 and not unrelated_reopened
    else:
        protected_success = not reopened and not unrelated_reopened

    return IndependentScore(
        task_id=str(public["task_id"]),
        family_id=str(protected["family_id"]),
        arm_id=arm_id,
        hidden_shift=bool(protected["hidden_shift"]),
        negative_control=bool(protected["negative_control"]),
        protected_root_task_success=protected_success,
        selected_repair_id=selected_id,
        selected_level=selected_level,
        selected_repair_tested=selected_tested,
        target_success=target_success,
        protected_sibling_ok=sibling_ok,
        protected_sibling_regression=sibling_regression,
        unnecessary_high_level_reframe=unnecessary_high,
        forbidden_high_level_mutation=forbidden_high,
        dependency_reopen_precision=precision,
        dependency_reopen_recall=recall,
        dependency_reopen_f1=f1,
        unrelated_closure_reopened=unrelated_reopened,
        spent_budget=spent,
    )


def _close(left: Any, right: Any, tolerance: float = 1e-12) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= tolerance
    return left == right


def score_mismatches(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> tuple[str, ...]:
    mismatches: list[str] = []
    keys = set(expected).union(actual)
    for key in sorted(keys):
        if key not in expected or key not in actual or not _close(expected.get(key), actual.get(key)):
            mismatches.append(f"{key}:{expected.get(key)!r}!={actual.get(key)!r}")
    return tuple(mismatches)


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    lo = min(b, c)
    tail = sum(comb(n, i) for i in range(lo + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def paired_bootstrap(
    left: Sequence[float],
    right: Sequence[float],
    *,
    seed: int,
    resamples: int,
) -> dict[str, float | int]:
    if len(left) != len(right) or not left:
        raise ValueError("paired bootstrap requires equal non-empty vectors")
    n = len(left)
    observed = sum(a - b for a, b in zip(left, right, strict=True)) / n
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(n):
            index = rng.randrange(n)
            total += left[index] - right[index]
        draws.append(total / n)
    draws.sort()
    lo = draws[max(0, int(0.025 * resamples))]
    hi = draws[min(resamples - 1, int(0.975 * resamples) - 1)]
    return {
        "n": n,
        "difference": observed,
        "ci95_low": lo,
        "ci95_high": hi,
        "seed": seed,
        "resamples": resamples,
    }


def holm_many(pvalues: Sequence[float], *, alpha: float = 0.05) -> dict[str, Any]:
    if not pvalues:
        raise ValueError("Holm requires p-values")
    indexed = sorted(enumerate(float(item) for item in pvalues), key=lambda item: item[1])
    passed = [False] * len(pvalues)
    thresholds = [0.0] * len(pvalues)
    stopped = False
    for rank, (index, pvalue) in enumerate(indexed):
        threshold = alpha / float(len(pvalues) - rank)
        thresholds[index] = threshold
        if stopped or pvalue > threshold:
            passed[index] = False
            stopped = True
        else:
            passed[index] = True
    return {
        "alpha": alpha,
        "pvalues": [float(item) for item in pvalues],
        "thresholds_by_input": thresholds,
        "passes_by_input": passed,
        "all_pass": all(passed),
    }


def _by_arm(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Mapping[str, Any]]]:
    output: dict[str, dict[str, Mapping[str, Any]]] = {}
    for row in rows:
        arm = str(row["arm_id"])
        task = str(row["task_id"])
        if task in output.setdefault(arm, {}):
            raise ValueError(f"duplicate score row:{arm}:{task}")
        output[arm][task] = row
    return output


def _paired(
    rows: Sequence[Mapping[str, Any]],
    left_arm: str,
    right_arm: str,
    *,
    subset_field: str | None,
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    by_arm = _by_arm(rows)
    left_map = by_arm[left_arm]
    right_map = by_arm[right_arm]
    if set(left_map) != set(right_map):
        raise ValueError("paired task set mismatch")
    left: list[Mapping[str, Any]] = []
    right: list[Mapping[str, Any]] = []
    for task_id in sorted(left_map):
        a, b = left_map[task_id], right_map[task_id]
        if subset_field is not None:
            if bool(a[subset_field]) != bool(b[subset_field]):
                raise ValueError(f"candidate-dependent subset:{task_id}:{subset_field}")
            if not bool(a[subset_field]):
                continue
        left.append(a)
        right.append(b)
    if not left:
        raise ValueError("empty paired subset")
    return left, right


def binary_contrast(
    rows: Sequence[Mapping[str, Any]],
    *,
    left_arm: str,
    right_arm: str,
    field: str,
    subset_field: str | None,
    seed: int,
    resamples: int,
) -> dict[str, Any]:
    left_rows, right_rows = _paired(rows, left_arm, right_arm, subset_field=subset_field)
    left = [1.0 if bool(item[field]) else 0.0 for item in left_rows]
    right = [1.0 if bool(item[field]) else 0.0 for item in right_rows]
    bootstrap = paired_bootstrap(left, right, seed=seed, resamples=resamples)
    b = sum(a > c for a, c in zip(left, right, strict=True))
    c = sum(c > a for a, c in zip(left, right, strict=True))
    return {
        **bootstrap,
        "field": field,
        "subset_field": subset_field,
        "left_rate": sum(left) / len(left),
        "right_rate": sum(right) / len(right),
        "mcnemar_b": b,
        "mcnemar_c": c,
        "mcnemar_p": exact_mcnemar_p(b, c),
    }


def continuous_contrast(
    rows: Sequence[Mapping[str, Any]],
    *,
    left_arm: str,
    right_arm: str,
    field: str,
    subset_field: str | None,
    seed: int,
    resamples: int,
) -> dict[str, Any]:
    left_rows, right_rows = _paired(rows, left_arm, right_arm, subset_field=subset_field)
    left = [float(item[field]) for item in left_rows]
    right = [float(item[field]) for item in right_rows]
    return {
        **paired_bootstrap(left, right, seed=seed, resamples=resamples),
        "field": field,
        "subset_field": subset_field,
        "left_mean": sum(left) / len(left),
        "right_mean": sum(right) / len(right),
    }


def independent_analysis(
    rows: Sequence[Mapping[str, Any]],
    execution: Mapping[str, Any],
) -> dict[str, Any]:
    full_arm = "orion_mutation_necessity"
    parents = tuple(str(item) for item in execution["h1_parents"])
    control_parent = str(execution["control_parent"])
    params = execution["statistics"]
    seed = int(params["bootstrap_seed"])
    resamples = int(params.get("bootstrap_resamples", 10000))
    margin = float(params["H1_superiority_margin_each_parent"])
    control_ni = float(params["H2_control_protected_success_noninferiority_margin"])
    whole_ni = float(params["total_protected_success_noninferiority_margin"])
    cost_margin = float(params["cost_noninferiority_margin_units"])

    h1: list[dict[str, Any]] = []
    for index, parent in enumerate(parents):
        contrast = binary_contrast(
            rows,
            left_arm=full_arm,
            right_arm=parent,
            field="protected_root_task_success",
            subset_field="hidden_shift",
            seed=seed + index,
            resamples=resamples,
        )
        h1.append({"parent": parent, **contrast})
    holm = holm_many([float(item["mcnemar_p"]) for item in h1])

    control_success = binary_contrast(
        rows,
        left_arm=full_arm,
        right_arm=control_parent,
        field="protected_root_task_success",
        subset_field="negative_control",
        seed=seed + 100,
        resamples=resamples,
    )
    full_controls, _ = _paired(rows, full_arm, control_parent, subset_field="negative_control")
    unnecessary = sum(bool(item["unnecessary_high_level_reframe"]) for item in full_controls)

    whole_grid: list[dict[str, Any]] = []
    cost: list[dict[str, Any]] = []
    for index, parent in enumerate(parents):
        whole_grid.append({
            "parent": parent,
            **binary_contrast(
                rows,
                left_arm=full_arm,
                right_arm=parent,
                field="protected_root_task_success",
                subset_field=None,
                seed=seed + 200 + index,
                resamples=resamples,
            ),
        })
        cost.append({
            "parent": parent,
            **continuous_contrast(
                rows,
                left_arm=full_arm,
                right_arm=parent,
                field="spent_budget",
                subset_field=None,
                seed=seed + 300 + index,
                resamples=resamples,
            ),
        })

    full_all, _ = _paired(rows, full_arm, parents[0], subset_field=None)
    sibling_regressions = sum(bool(item["protected_sibling_regression"]) for item in full_all)
    forbidden = sum(bool(item["forbidden_high_level_mutation"]) for item in full_all)
    gates = {
        "h1_each_parent_practical": all(float(item["difference"]) >= margin for item in h1),
        "h1_each_parent_ci_positive": all(float(item["ci95_low"]) > 0.0 for item in h1),
        "h1_holm": bool(holm["all_pass"]),
        "h2_zero_unnecessary_reframe": unnecessary == 0,
        "h2_control_success_noninferior": float(control_success["ci95_low"]) >= -control_ni,
        "whole_grid_success_noninferior": all(float(item["ci95_low"]) >= -whole_ni for item in whole_grid),
        "zero_protected_sibling_regression": sibling_regressions == 0,
        "zero_forbidden_high_level_mutation": forbidden == 0,
        "cost_within_margin": all(float(item["difference"]) <= cost_margin for item in cost),
    }
    return {
        "full_arm": full_arm,
        "h1_parents": list(parents),
        "h1_hidden_shift": h1,
        "h1_holm": holm,
        "h2_control_parent": control_parent,
        "h2_control_success": control_success,
        "h2_full_unnecessary_reframe_count": unnecessary,
        "whole_grid_success": whole_grid,
        "cost": cost,
        "full_protected_sibling_regression_count": sibling_regressions,
        "full_forbidden_high_level_mutation_count": forbidden,
        "gates": gates,
        "all_support_gates_pass": all(gates.values()),
    }


def _deep_compare(expected: Any, actual: Any, path: str = "") -> list[str]:
    mismatches: list[str] = []
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        for key in sorted(set(expected).union(actual)):
            child = f"{path}.{key}" if path else str(key)
            if key not in expected or key not in actual:
                mismatches.append(f"{child}:missing")
            else:
                mismatches.extend(_deep_compare(expected[key], actual[key], child))
        return mismatches
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [f"{path}:length:{len(expected)}!={len(actual)}"]
        for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
            mismatches.extend(_deep_compare(left, right, f"{path}[{index}]"))
        return mismatches
    if not _close(expected, actual):
        mismatches.append(f"{path}:{expected!r}!={actual!r}")
    return mismatches


def verify(
    *,
    public_path: Path,
    protected_path: Path,
    raw_path: Path,
    execution_path: Path,
    result_path: Path,
) -> dict[str, Any]:
    public_rows = _read_lines(public_path)
    protected_rows = _read_lines(protected_path)
    raw_rows = _read_lines(raw_path)
    execution = json.loads(execution_path.read_text())
    result = json.loads(result_path.read_text())

    public_by_id = {str(row["task_id"]): row for row in public_rows}
    protected_by_id = {str(row["task_id"]): row["protected"] for row in protected_rows}
    if set(public_by_id) != set(protected_by_id):
        raise ValueError("public/protected world identity mismatch")
    if len(public_by_id) != int(execution["n"]):
        raise ValueError("world count mismatch")

    score_rows: list[dict[str, Any]] = []
    score_errors: list[str] = []
    outcome_counts: dict[str, int] = {}
    for index, row in enumerate(raw_rows):
        task_id = str(row["task_id"])
        if task_id not in public_by_id:
            score_errors.append(f"raw[{index}]:unknown_task:{task_id}")
            continue
        recomputed = score_outcome(
            public_by_id[task_id],
            protected_by_id[task_id],
            row["outcome"],
        ).to_payload()
        embedded = row.get("score")
        if not isinstance(embedded, Mapping):
            score_errors.append(f"raw[{index}]:missing_embedded_score")
        else:
            mismatch = score_mismatches(recomputed, embedded)
            score_errors.extend(f"raw[{index}]:{item}" for item in mismatch)
        score_rows.append(recomputed)
        arm = str(recomputed["arm_id"])
        outcome_counts[arm] = outcome_counts.get(arm, 0) + 1

    expected_per_arm = int(execution["n"])
    expected_arms = [*execution["runnable_arms"], *execution["ablation_arms"]]
    for arm in expected_arms:
        if outcome_counts.get(str(arm), 0) != expected_per_arm:
            score_errors.append(
                f"arm_count:{arm}:{outcome_counts.get(str(arm),0)}!={expected_per_arm}"
            )

    runnable = set(str(item) for item in execution["runnable_arms"])
    primary_score_rows = [row for row in score_rows if str(row["arm_id"]) in runnable]
    analysis = independent_analysis(primary_score_rows, execution)
    analysis_errors = _deep_compare(analysis, result["analysis"], "analysis")
    expected_terminal = (
        "P1_MUTATION_NECESSITY_SUPPORTED"
        if analysis["all_support_gates_pass"]
        else "P1_MUTATION_NECESSITY_NOT_SUPPORTED"
    )
    terminal_matches = result.get("terminal") == expected_terminal

    return {
        "schema_version": "ScientificResultVerification.p1.v2.2.4.independent.v1",
        "verdict": "PASS" if not score_errors and not analysis_errors and terminal_matches else "FAIL",
        "protocol_version": str(execution["protocol_version"]),
        "n_worlds": len(public_by_id),
        "n_raw_rows": len(raw_rows),
        "expected_rows": expected_per_arm * len(expected_arms),
        "outcome_counts_by_arm": outcome_counts,
        "score_mismatch_count": len(score_errors),
        "score_mismatches": score_errors[:100],
        "analysis_mismatch_count": len(analysis_errors),
        "analysis_mismatches": analysis_errors[:100],
        "recomputed_analysis": analysis,
        "recomputed_terminal": expected_terminal,
        "archived_terminal": result.get("terminal"),
        "terminal_matches": terminal_matches,
        "input_sha256": {
            "world_public": _sha(public_path),
            "protected_response_matrix": _sha(protected_path),
            "raw_results": _sha(raw_path),
            "execution_freeze": _sha(execution_path),
            "primary_result": _sha(result_path),
        },
        "implementation_boundary": (
            "standard-library independent scorer/statistics; imports no necessity_scoring, "
            "necessity_statistics, necessity_policies, or ORION licensing"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world-public", type=Path, required=True)
    parser.add_argument("--protected", type=Path, required=True)
    parser.add_argument("--raw-results", type=Path, required=True)
    parser.add_argument("--execution-freeze", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = verify(
        public_path=args.world_public,
        protected_path=args.protected,
        raw_path=args.raw_results,
        execution_path=args.execution_freeze,
        result_path=args.result,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
