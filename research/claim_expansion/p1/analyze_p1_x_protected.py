from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from typing import Any

import generate_p1_x_protected_cases as protected
import p1_x_execution as execution

BOOTSTRAP_SEED = 20260819
BOOTSTRAP_REPS = 20000


def _mcnemar_exact(left: list[int], right: list[int]) -> dict[str, Any]:
    b = sum(1 for l, r in zip(left, right, strict=True) if l == 1 and r == 0)
    c = sum(1 for l, r in zip(left, right, strict=True) if l == 0 and r == 1)
    n = b + c
    if n == 0:
        p = 1.0
    else:
        k = min(b, c)
        tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
        p = min(1.0, 2.0 * tail)
    return {"b_left_only_correct": b, "c_right_only_correct": c, "two_sided_p": p}


def _domain_stratified_bootstrap(cases: list[dict[str, Any]], diffs: list[int]) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED)
    indices_by_domain: dict[str, list[int]] = defaultdict(list)
    for index, case in enumerate(cases):
        indices_by_domain[case["domain"]].append(index)
    out = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = []
        for indices in indices_by_domain.values():
            sampled.extend(rng.choice(indices) for _ in indices)
        out.append(sum(diffs[index] for index in sampled) / len(sampled))
    out.sort()
    return out


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("empty")
    pos = q * (len(sorted_values) - 1)
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_values[lo]
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def _holm(pairs: list[tuple[str, float]]) -> dict[str, float]:
    ordered = sorted(pairs, key=lambda item: item[1])
    m = len(ordered)
    adjusted: dict[str, float] = {}
    running = 0.0
    for rank, (name, p) in enumerate(ordered):
        value = min(1.0, (m - rank) * p)
        running = max(running, value)
        adjusted[name] = running
    return adjusted


def analyze() -> dict[str, Any]:
    cases = protected.generate_protected_cases()
    if len(cases) != 400:
        raise RuntimeError(f"protected_count:{len(cases)}")

    arms = list(execution.ARM_FUNCTIONS)
    rows = []
    scores: dict[str, list[int]] = {arm: [] for arm in arms}
    false_reframes: dict[str, int] = {arm: 0 for arm in arms}
    invariant_violations: dict[str, int] = {arm: 0 for arm in arms}

    for case in cases:
        decisions = {arm: execution.run_arm(case, arm) for arm in arms}
        row_scores = {arm: execution.score_esrd(case, decision) for arm, decision in decisions.items()}
        for arm in arms:
            scores[arm].append(row_scores[arm])
            false_reframes[arm] += execution.false_high_level_reframe(case, decisions[arm])
            invariant_violations[arm] += execution.invariant_violation(case, decisions[arm])
        rows.append(
            {
                "case_id": case["case_id"],
                "domain": case["domain"],
                "archetype": case["archetype"],
                "generator_id": case["generator_id"],
                "decisions": decisions,
                "esrd": row_scores,
            }
        )

    p1 = scores["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
    b1 = scores["B1_DONOR_COMPLETE_GREEDY"]
    b2 = scores["B2_SUCCESS_AUTHORIZES_REFRAME"]
    b3 = scores["B3_IDEAL_TYPED_PRODUCT"]
    diffs = [x - y for x, y in zip(p1, b1, strict=True)]
    mean_diff = sum(diffs) / len(diffs)
    boot = _domain_stratified_bootstrap(cases, diffs)
    ci = [_percentile(boot, 0.025), _percentile(boot, 0.975)]

    per_domain: dict[str, dict[str, Any]] = {}
    for domain in protected.DOMAINS:
        idx = [i for i, case in enumerate(cases) if case["domain"] == domain]
        p = sum(p1[i] for i in idx) / len(idx)
        q = sum(b1[i] for i in idx) / len(idx)
        per_domain[domain] = {"n": len(idx), "p1x_esrd": p, "b1_esrd": q, "difference": p - q}

    narrow_idx = [i for i, case in enumerate(cases) if case["archetype"] == "NARROW_REPAIR_SUFFICIENT"]
    p1_narrow = sum(p1[i] for i in narrow_idx) / len(narrow_idx)
    b1_narrow = sum(b1[i] for i in narrow_idx) / len(narrow_idx)
    lower_level_difference = p1_narrow - b1_narrow

    m_b1 = _mcnemar_exact(p1, b1)
    m_b2 = _mcnemar_exact(p1, b2)
    holm = _holm([("P1X_vs_B1", m_b1["two_sided_p"]), ("P1X_vs_B2", m_b2["two_sided_p"])])

    b3_decision_mismatches = sum(
        1
        for row in rows
        if row["decisions"]["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
        != row["decisions"]["B3_IDEAL_TYPED_PRODUCT"]
    )

    non_regression = {
        "lower_level_repair_difference": lower_level_difference,
        "lower_level_margin": -0.02,
        "lower_level_pass": lower_level_difference >= -0.02,
        "false_high_level_reframes_p1x": false_reframes["P1X_MINIMAL_SCIENTIFIC_ESCALATION"],
        "false_high_level_reframes_b1": false_reframes["B1_DONOR_COMPLETE_GREEDY"],
        "false_reframe_rate_difference": (
            false_reframes["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
            - false_reframes["B1_DONOR_COMPLETE_GREEDY"]
        ) / len(cases),
        "false_reframe_margin": 0.02,
        "false_reframe_pass": (
            false_reframes["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
            - false_reframes["B1_DONOR_COMPLETE_GREEDY"]
        ) / len(cases) <= 0.02,
        "p1x_invariant_violations": invariant_violations["P1X_MINIMAL_SCIENTIFIC_ESCALATION"],
        "invariant_pass": invariant_violations["P1X_MINIMAL_SCIENTIFIC_ESCALATION"] == 0,
        "per_domain_floor": -0.05,
        "per_domain_pass": all(item["difference"] > -0.05 for item in per_domain.values()),
    }
    non_regression["all_pass"] = all(
        non_regression[key]
        for key in ("lower_level_pass", "false_reframe_pass", "invariant_pass", "per_domain_pass")
    )

    primary_pass = mean_diff >= 0.10 and ci[0] > 0.0 and non_regression["all_pass"]
    b3_equivalence_pass = b3_decision_mismatches == 0 and b3 == p1

    return {
        "schema_version": "P1_X_PROTECTED_RESULT_V1",
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "n": len(cases),
        "arm_esrd": {
            arm: {"correct": sum(values), "rate": sum(values) / len(values)}
            for arm, values in scores.items()
        },
        "primary": {
            "comparison": "P1X_MINIMAL_SCIENTIFIC_ESCALATION - B1_DONOR_COMPLETE_GREEDY",
            "difference": mean_diff,
            "practical_margin": 0.10,
            "bootstrap_95ci": ci,
            "mcnemar": m_b1,
            "pass": primary_pass,
        },
        "secondary": {
            "P1X_vs_B2_mcnemar": m_b2,
            "holm_adjusted_p": holm,
        },
        "per_domain": per_domain,
        "non_regression": non_regression,
        "b3_equivalence": {
            "decision_mismatches": b3_decision_mismatches,
            "pass": b3_equivalence_pass,
        },
        "false_high_level_reframes": false_reframes,
        "invariant_violations": invariant_violations,
        "rows": rows,
        "terminal": (
            "P1_X_BOUNDED_ARCHITECTURE_RESULT_SUPPORTED"
            if primary_pass and b3_equivalence_pass
            else "P1_X_RESULT_NOT_SUPPORTED"
        ),
    }


def main() -> int:
    json.dump(analyze(), sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
