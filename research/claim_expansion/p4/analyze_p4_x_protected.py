from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from typing import Any

from generate_p4_x_protected_cases import DOMAINS, generate_cases
from p4_x_execution import run_arms

BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED = 44017
PRACTICAL_MARGIN = 0.10


def _sha_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def analyze() -> dict[str, Any]:
    cases = generate_cases()
    rows = []
    correct = Counter()
    false_promotions = Counter()
    per_domain_diff: dict[str, list[int]] = defaultdict(list)
    b3_mismatch = 0
    b, c = 0, 0

    for case in cases:
        gold = case["protected_gold"]["task_terminal"]
        arms = run_arms(case)
        row = {
            "case_id": case["case_id"],
            "domain": case["domain"],
            "archetype": case["archetype"],
            "gold": gold,
            "decisions": arms,
        }
        rows.append(row)
        p4_ok = arms["P4_X"] == gold
        b1_ok = arms["B1_GENERIC_AUTHORIZATION_PRODUCT"] == gold
        for arm, decision in arms.items():
            correct[arm] += int(decision == gold)
            if decision == "PROMOTE" and gold != "PROMOTE":
                false_promotions[arm] += 1
        per_domain_diff[case["domain"]].append(int(p4_ok) - int(b1_ok))
        if p4_ok and not b1_ok:
            b += 1
        elif b1_ok and not p4_ok:
            c += 1
        b3_mismatch += int(arms["P4_X"] != arms["B3_IDEAL_TYPED_PRODUCT"])

    rng = random.Random(BOOTSTRAP_SEED)
    by_domain = {d: [r for r in rows if r["domain"] == d] for d in DOMAINS}
    diffs = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sampled = []
        for d in DOMAINS:
            pool = by_domain[d]
            sampled.extend(rng.choice(pool) for _ in range(len(pool)))
        delta = sum(
            int(r["decisions"]["P4_X"] == r["gold"])
            - int(r["decisions"]["B1_GENERIC_AUTHORIZATION_PRODUCT"] == r["gold"])
            for r in sampled
        ) / len(sampled)
        diffs.append(delta)
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs)) - 1]

    n = len(rows)
    point = (correct["P4_X"] - correct["B1_GENERIC_AUTHORIZATION_PRODUCT"]) / n
    clean = [r for r in rows if r["archetype"] == "CLEAN_AUTHORIZED"]
    clean_rate = sum(r["decisions"]["P4_X"] == "PROMOTE" for r in clean) / len(clean)
    domain_effects = {d: sum(v) / len(v) for d, v in per_domain_diff.items()}

    result = {
        "schema_version": "P4_X_PROTECTED_RESULT_V1",
        "case_count": n,
        "counts_correct": dict(correct),
        "accuracy": {k: v / n for k, v in correct.items()},
        "p4x_minus_b1": point,
        "bootstrap_95_ci": [lo, hi],
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "mcnemar_b_p4_only_correct": b,
        "mcnemar_c_b1_only_correct": c,
        "false_promotions": dict(false_promotions),
        "p4x_clean_promote_rate": clean_rate,
        "per_domain_p4x_minus_b1": domain_effects,
        "b3_p4x_decision_mismatches": b3_mismatch,
        "rows_sha256": _sha_json(rows),
        "decision": {
            "margin_pass": point >= PRACTICAL_MARGIN and lo > PRACTICAL_MARGIN,
            "zero_p4x_false_promotion": false_promotions["P4_X"] == 0,
            "clean_promotion_pass": clean_rate == 1.0,
            "all_domain_direction_positive": all(x > 0 for x in domain_effects.values()),
            "b3_equivalence_pass": b3_mismatch == 0,
        },
    }
    result["primary_pass"] = all(result["decision"].values())
    return result


if __name__ == "__main__":
    print(json.dumps(analyze(), sort_keys=True, indent=2))
