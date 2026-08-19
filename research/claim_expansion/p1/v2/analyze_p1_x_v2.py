from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from typing import Any

import generate_p1_x_protected_v2 as protected
import p1_x_execution_v2 as execution

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
    return values[lo] * (1 - frac) + values[hi] * frac


def _bootstrap(cases: list[dict[str, Any]], diffs: list[int]) -> list[float]:
    rng = random.Random(BOOTSTRAP_SEED)
    by_domain: dict[str, list[int]] = defaultdict(list)
    for i, case in enumerate(cases):
        by_domain[case["domain"]].append(i)
    result = []
    for _ in range(BOOTSTRAP_REPS):
        sampled = []
        for indices in by_domain.values():
            sampled.extend(rng.choice(indices) for _ in indices)
        result.append(sum(diffs[i] for i in sampled) / len(sampled))
    return sorted(result)


def _holm(items: list[tuple[str, float]]) -> dict[str, float]:
    ordered = sorted(items, key=lambda x: x[1])
    m = len(ordered)
    running = 0.0
    output = {}
    for rank, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - rank) * p))
        output[name] = running
    return output


def analyze() -> dict[str, Any]:
    cases = protected.generate_cases()
    if len(cases) != 400:
        raise RuntimeError(len(cases))
    arms = list(execution.ARM_FUNCTIONS_V2)
    rows = []
    scores = {arm: [] for arm in arms}
    false_reframes = {arm: 0 for arm in arms}
    invariant_violations = {arm: 0 for arm in arms}

    for case in cases:
        decisions = {arm: execution.run_arm_v2(case, arm) for arm in arms}
        row_scores = {arm: execution.score_esrd(case, decision) for arm, decision in decisions.items()}
        for arm in arms:
            scores[arm].append(row_scores[arm])
            false_reframes[arm] += execution.false_high_level_reframe(case, decisions[arm])
            invariant_violations[arm] += execution.invariant_violation(case, decisions[arm])
        rows.append({"case_id": case["case_id"], "domain": case["domain"], "archetype": case["archetype"], "generator_id": case["generator_id"], "decisions": decisions, "esrd": row_scores})

    p1 = scores["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
    b1 = scores["B1_DONOR_COMPLETE_GREEDY"]
    b2 = scores["B2_SUCCESS_AUTHORIZES_REFRAME"]
    b3 = scores["B3_IDEAL_TYPED_PRODUCT"]
    diffs = [x - y for x, y in zip(p1, b1, strict=True)]
    difference = sum(diffs) / len(diffs)
    boot = _bootstrap(cases, diffs)
    ci = [_percentile(boot, 0.025), _percentile(boot, 0.975)]

    per_domain = {}
    for domain in protected.DOMAINS:
        idx = [i for i, case in enumerate(cases) if case["domain"] == domain]
        p = sum(p1[i] for i in idx) / len(idx)
        q = sum(b1[i] for i in idx) / len(idx)
        per_domain[domain] = {"n": len(idx), "p1x_esrd": p, "b1_esrd": q, "difference": p - q}

    narrow_idx = [i for i, case in enumerate(cases) if case["archetype"] == "NARROW_REPAIR_SUFFICIENT"]
    lower_diff = sum(p1[i] for i in narrow_idx) / len(narrow_idx) - sum(b1[i] for i in narrow_idx) / len(narrow_idx)
    false_diff = (false_reframes["P1X_MINIMAL_SCIENTIFIC_ESCALATION"] - false_reframes["B1_DONOR_COMPLETE_GREEDY"]) / len(cases)
    nonreg = {
        "lower_level_repair_difference": lower_diff,
        "lower_level_pass": lower_diff >= -0.02,
        "false_reframe_rate_difference": false_diff,
        "false_reframe_pass": false_diff <= 0.02,
        "p1x_invariant_violations": invariant_violations["P1X_MINIMAL_SCIENTIFIC_ESCALATION"],
        "invariant_pass": invariant_violations["P1X_MINIMAL_SCIENTIFIC_ESCALATION"] == 0,
        "per_domain_pass": all(item["difference"] > -0.05 for item in per_domain.values()),
    }
    nonreg["all_pass"] = all(nonreg[k] for k in ("lower_level_pass", "false_reframe_pass", "invariant_pass", "per_domain_pass"))

    m1, m2 = _mcnemar(p1, b1), _mcnemar(p1, b2)
    b3_mismatch = sum(1 for row in rows if row["decisions"]["P1X_MINIMAL_SCIENTIFIC_ESCALATION"] != row["decisions"]["B3_IDEAL_TYPED_PRODUCT"])
    primary_pass = difference >= 0.10 and ci[0] > 0.0 and nonreg["all_pass"]
    b3_pass = b3 == p1 and b3_mismatch == 0

    return {
        "schema_version": "P1_X_PROTECTED_RESULT_V2",
        "n": 400,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_reps": BOOTSTRAP_REPS,
        "arm_esrd": {arm: {"correct": sum(values), "rate": sum(values) / 400} for arm, values in scores.items()},
        "primary": {"difference": difference, "practical_margin": 0.10, "bootstrap_95ci": ci, "mcnemar": m1, "pass": primary_pass},
        "secondary": {"P1X_vs_B2_mcnemar": m2, "holm_adjusted_p": _holm([("P1X_vs_B1", m1["two_sided_p"]), ("P1X_vs_B2", m2["two_sided_p"])])},
        "per_domain": per_domain,
        "non_regression": nonreg,
        "false_high_level_reframes": false_reframes,
        "invariant_violations": invariant_violations,
        "b3_equivalence": {"decision_mismatches": b3_mismatch, "pass": b3_pass},
        "rows": rows,
        "terminal": "P1_X_V2_BOUNDED_ARCHITECTURE_RESULT_SUPPORTED" if primary_pass and b3_pass else "P1_X_V2_RESULT_NOT_SUPPORTED",
    }


def main() -> int:
    json.dump(analyze(), sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
