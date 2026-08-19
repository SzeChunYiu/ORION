from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
P1X = HERE.parent
V2 = P1X / "v2"
for path in (str(P1X), str(V2)):
    if path not in sys.path:
        sys.path.insert(0, path)

import generate_p1_x_protected_v2 as generator  # noqa: E402
import p1_x_execution_v2 as execution  # noqa: E402

NAMESPACE = "P1_X_ARCH_INDEPENDENCE_V1_2026-08-19"
COMBINATIONS = (
    "D_FORWARD_R_FORWARD",
    "D_FORWARD_R_REVERSE",
    "D_REVERSE_R_FORWARD",
    "D_REVERSE_R_REVERSE",
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _replace(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [_replace(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: _replace(item, old, new) for key, item in value.items()}
    return value


def generate_arch_cases() -> list[dict[str, Any]]:
    cases = []
    for domain in generator.DOMAINS:
        for archetype in generator.ARCHETYPES:
            for replicate in range(1, 6):
                base = generator.build_case(domain, archetype, replicate)
                old = base["case_id"]
                new = f"P1X-ARCH-{domain}-{archetype}-R{replicate:02d}"
                case = _replace(deepcopy(base), old, new)
                seed = _sha(f"{NAMESPACE}:{new}")
                case["case_id"] = new
                case["seed_commitment"] = seed
                case["generator_id"] = "P1_X_ARCH_INTERFACE_CASE_V1"
                case["candidate_visible"]["evidence"] = [f"{new}:evidence:{seed[:12]}"]
                case["protected_gold"]["provenance_commitment"] = _sha(f"{seed}:ARCH_GOLD_V1")
                cases.append(case)
    return cases


def transform(case: dict[str, Any], combination: str) -> dict[str, Any]:
    output = deepcopy(case)
    if "D_REVERSE" in combination:
        output["registered_narrower_alternatives"].reverse()
    if "R_REVERSE" in combination:
        output["candidate_visible"]["candidate_revisions"].reverse()
        output["candidate_visible"]["revision_proposals"].reverse()
    return output


def run() -> dict[str, Any]:
    cases = generate_arch_cases()
    combo_results = {}
    overall_pass = True
    for combination in COMBINATIONS:
        arm_correct = {arm: 0 for arm in execution.ARM_FUNCTIONS_V2}
        p1x_false_reframes = 0
        p1x_invariant_violations = 0
        b3_mismatches = 0
        budget_violations = 0
        per_domain = {}
        domain_counts = {domain: {"p1x": 0, "b1": 0, "n": 0} for domain in generator.DOMAINS}

        for original in cases:
            case = transform(original, combination)
            decisions = {arm: execution.run_arm_v2(case, arm) for arm in execution.ARM_FUNCTIONS_V2}
            scores = {arm: execution.score_esrd(case, decision) for arm, decision in decisions.items()}
            for arm, value in scores.items():
                arm_correct[arm] += value
            p1x = decisions["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
            b3 = decisions["B3_IDEAL_TYPED_PRODUCT"]
            b3_mismatches += int(p1x != b3)
            p1x_false_reframes += execution.false_high_level_reframe(case, p1x)
            p1x_invariant_violations += execution.invariant_violation(case, p1x)
            budget_violations += sum(int(decision["checks_used"] > case["budget"]["max_interventions"]) for decision in decisions.values())
            record = domain_counts[case["domain"]]
            record["p1x"] += scores["P1X_MINIMAL_SCIENTIFIC_ESCALATION"]
            record["b1"] += scores["B1_DONOR_COMPLETE_GREEDY"]
            record["n"] += 1

        for domain, record in domain_counts.items():
            per_domain[domain] = {
                "n": record["n"],
                "p1x_esrd": record["p1x"] / record["n"],
                "b1_esrd": record["b1"] / record["n"],
                "difference": (record["p1x"] - record["b1"]) / record["n"],
            }

        passed = (
            arm_correct["P1X_MINIMAL_SCIENTIFIC_ESCALATION"] == 200
            and b3_mismatches == 0
            and p1x_false_reframes == 0
            and p1x_invariant_violations == 0
            and budget_violations == 0
            and all(item["difference"] > 0 for item in per_domain.values())
        )
        overall_pass &= passed
        combo_results[combination] = {
            "arm_correct": arm_correct,
            "b3_mismatches": b3_mismatches,
            "p1x_false_high_level_reframes": p1x_false_reframes,
            "p1x_invariant_violations": p1x_invariant_violations,
            "budget_violations": budget_violations,
            "per_domain": per_domain,
            "pass": passed,
        }

    pair_digest = _sha("\n".join(f"{case['case_id']}|{case['seed_commitment']}" for case in cases))
    return {
        "schema_version": "P1_X_ARCHITECTURE_INDEPENDENCE_RESULT_V1",
        "case_count": len(cases),
        "combination_count": len(COMBINATIONS),
        "total_arm_case_evaluations": len(cases) * len(COMBINATIONS) * len(execution.ARM_FUNCTIONS_V2),
        "identity_pairs_sha256": pair_digest,
        "combinations": combo_results,
        "pass": overall_pass,
        "terminal": "P1_X_ARCH_INTERFACE_INDEPENDENCE_SUPPORTED" if overall_pass else "P1_X_ARCH_INTERFACE_INDEPENDENCE_NOT_SUPPORTED",
    }


def main() -> int:
    result = run()
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
