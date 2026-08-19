from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from typing import Any

import generate_p2_x_protected_cases as protected
import p2_x_execution as execution

BOOTSTRAP_SEED = 20260819
BOOTSTRAP_REPS = 20000


def _mcnemar(left: list[int], right: list[int]) -> dict[str, Any]:
    b = sum(1 for l, r in zip(left, right, strict=True) if l == 1 and r == 0)
    c = sum(1 for l, r in zip(left, right, strict=True) if l == 0 and r == 1)
    n = b + c
    if n == 0:
        p = 1.0
    else:
        k = min(b, c)
        p = min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))
    return {"b_left_only_correct": b, "c_right_only_correct": c, "two_sided_p": p}


def _percentile(values: list[float], q: float) -> float:
    pos = q * (len(values) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return values[lo]
    frac = pos - lo
    return values[lo] * (1.0 - frac) + values[hi] * frac


def _bootstrap(cases: list[dict[str, Any]], diffs: list[int]) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED)
    by_domain: dict[str, list[int]] = defaultdict(list)
    for i, case in enumerate(cases):
        by_domain[case["domain"]].append(i)
    values = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = []
        for indices in by_domain.values():
            sampled.extend(rng.choice(indices) for _ in indices)
        values.append(sum(diffs[i] for i in sampled) / len(sampled))
    return sorted(values)


def _holm(items: list[tuple[str, float]]) -> dict[str, float]:
    ordered = sorted(items, key=lambda x: x[1])
    m = len(ordered)
    running = 0.0
    result = {}
    for rank, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - rank) * p))
        result[name] = running
    return result


def analyze() -> dict[str, Any]:
    cases = protected.generate_cases()
    if len(cases) != 400:
        raise RuntimeError(f"protected_count:{len(cases)}")
    arms = list(execution.ARM_FUNCTIONS)
    rows = []
    scores = {arm: [] for arm in arms}
    false_closure = {arm: 0 for arm in arms}
    unnecessary_cc = {arm: 0 for arm in arms}

    for case in cases:
        decisions = {arm: execution.run_arm(case, arm) for arm in arms}
        row_scores = {arm: execution.score_escd(case, decision) for arm, decision in decisions.items()}
        for arm in arms:
            scores[arm].append(row_scores[arm])
            false_closure[arm] += execution.false_task_closure(case, decisions[arm])
            unnecessary_cc[arm] += execution.unnecessary_cannot_check_clean(case, decisions[arm])
        rows.append({"case_id": case["case_id"], "domain": case["domain"], "archetype": case["archetype"], "generator_id": case["generator_id"], "decisions": decisions, "escd": row_scores})

    p2 = scores["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"]
    b1 = scores["B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT"]
    b2 = scores["B2_GLOBAL_SUFFICIENCY_AGGREGATOR"]
    b3 = scores["B3_IDEAL_TYPED_ROUTE_PRODUCT"]
    diffs = [x - y for x, y in zip(p2, b1, strict=True)]
    difference = sum(diffs) / len(diffs)
    boot = _bootstrap(cases, diffs)
    ci = [_percentile(boot, 0.025), _percentile(boot, 0.975)]

    per_domain = {}
    for domain in protected.DOMAINS:
        idx = [i for i, case in enumerate(cases) if case["domain"] == domain]
        p = sum(p2[i] for i in idx) / len(idx)
        q = sum(b1[i] for i in idx) / len(idx)
        per_domain[domain] = {"n": len(idx), "p2x_escd": p, "b1_escd": q, "difference": p - q}

    clean_idx = [i for i, case in enumerate(cases) if case["archetype"] == "ALL_OBLIGATIONS_DISCHARGED"]
    clean_p2 = sum(p2[i] for i in clean_idx) / len(clean_idx)
    clean_b1 = sum(b1[i] for i in clean_idx) / len(clean_idx)
    clean_diff = clean_p2 - clean_b1
    m1, m2 = _mcnemar(p2, b1), _mcnemar(p2, b2)
    b3_mismatches = sum(1 for row in rows if row["decisions"]["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"] != row["decisions"]["B3_IDEAL_TYPED_ROUTE_PRODUCT"])

    nonreg = {
        "clean_task_stop_p2x": clean_p2,
        "clean_task_stop_b1": clean_b1,
        "clean_task_stop_difference": clean_diff,
        "clean_task_stop_margin": -0.02,
        "clean_task_stop_pass": clean_diff >= -0.02,
        "p2x_false_task_closures": false_closure["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"],
        "false_task_closure_target": 0,
        "false_task_closure_pass": false_closure["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"] == 0,
        "p2x_unnecessary_cannot_check_clean": unnecessary_cc["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"],
        "unnecessary_cannot_check_pass": unnecessary_cc["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"] == 0,
        "per_domain_floor": -0.05,
        "per_domain_pass": all(item["difference"] > -0.05 for item in per_domain.values()),
    }
    nonreg["all_pass"] = all(nonreg[k] for k in ("clean_task_stop_pass", "false_task_closure_pass", "unnecessary_cannot_check_pass", "per_domain_pass"))
    primary_pass = difference >= 0.10 and ci[0] > 0.0 and nonreg["all_pass"]
    b3_pass = b3 == p2 and b3_mismatches == 0

    return {
        "schema_version": "P2_X_PROTECTED_RESULT_V1",
        "n": 400,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "arm_escd": {arm: {"correct": sum(values), "rate": sum(values) / 400} for arm, values in scores.items()},
        "primary": {"difference": difference, "practical_margin": 0.10, "bootstrap_95ci": ci, "mcnemar": m1, "pass": primary_pass},
        "secondary": {"P2X_vs_B2_mcnemar": m2, "holm_adjusted_p": _holm([("P2X_vs_B1", m1["two_sided_p"]), ("P2X_vs_B2", m2["two_sided_p"])])},
        "per_domain": per_domain,
        "non_regression": nonreg,
        "false_task_closures": false_closure,
        "unnecessary_cannot_check_clean": unnecessary_cc,
        "b3_equivalence": {"decision_mismatches": b3_mismatches, "pass": b3_pass},
        "rows": rows,
        "terminal": "P2_X_BOUNDED_ROUTE_AUTHORITY_RESULT_SUPPORTED" if primary_pass and b3_pass else "P2_X_RESULT_NOT_SUPPORTED",
    }


def main() -> int:
    json.dump(analyze(), sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
