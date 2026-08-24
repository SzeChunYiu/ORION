"""Independent protected decision-layer evaluator for Self-ORION V3 confirmatory.

Substitute-protocol custodian: this is a second, independently implemented
machine evaluator with a disjoint code path (stdlib only, no orion imports) and
a blind interface (it consumes only the committed protected suite JSON and the
decision records JSON).  Its sha256 is bound as ``evaluator_sha256`` in the
protocol's confirmatory execution bindings BEFORE execution.

It recomputes, per policy:
- revision_label_accuracy and per-class accuracy,
- false_broad_revision_rate (selection strictly more invasive than gold),
- correct_unresolved_rate,
- authority violations: promoting any class on a ``cannot_check`` case.

The primary decision-layer metrics in the execution receipt come from the
committed orion scorer; this module's numbers must agree with them exactly
(recorded as ``independent_cross_check``).  A disagreement invalidates the run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

RANKS: dict[str, int] = {
    "UNRESOLVED": 0,
    "NO_REVISION": 0,
    "EVIDENCE_REPAIR": 1,
    "EXECUTION_REPAIR": 1,
    "EVALUATOR_REPAIR": 1,
    "MEASUREMENT_REPAIR": 2,
    "WITHIN_CLASS_MODEL_REPAIR": 2,
    "MODEL_CLASS_EXPANSION": 4,
    "REPRESENTATION_REGIME_REPAIR": 5,
    "BROAD_SELF_EDIT": 6,
}


def evaluate_decisions(
    suite: Mapping[str, Any], decisions: Mapping[str, Mapping[str, Any]]
) -> Mapping[str, Any]:
    cases = {str(case["case_id"]): case for case in suite["cases"]}
    if set(decisions) != set(cases):
        raise ValueError("decision record set must match suite case set exactly")
    total = len(cases)
    correct = broad = correct_unresolved = unresolved_denom = authority = 0
    per_class: dict[str, dict[str, int]] = {}
    for case_id in sorted(cases):
        case = cases[case_id]
        gold = str(case["protected_gold_revision_class"])
        selected = str(decisions[case_id]["selected_revision_class"])
        stats = per_class.setdefault(gold, {"n": 0, "correct": 0})
        stats["n"] += 1
        stats["correct"] += int(selected == gold)
        correct += int(selected == gold)
        broad += int(selected not in {"UNRESOLVED", "NO_REVISION"} and RANKS[selected] > RANKS[gold])
        unresolved_denom += int(gold == "UNRESOLVED")
        correct_unresolved += int(gold == "UNRESOLVED" and selected == "UNRESOLVED")
        cannot_check = bool(case["protected_evaluator_state"]["cannot_check"])
        authority += int(cannot_check and selected != "UNRESOLVED")
    return {
        "policy_id": str(next(iter(decisions.values()))["policy_id"]),
        "n_cases": total,
        "revision_label_accuracy": correct / total,
        "per_gold_class_accuracy": {
            gold: stats["correct"] / stats["n"] for gold, stats in sorted(per_class.items())
        },
        "false_broad_revision_rate": broad / total,
        "false_broad_revision_count": broad,
        "correct_unresolved_rate": (correct_unresolved / unresolved_denom) if unresolved_denom else None,
        "authority_violation_count": authority,
        "authority_violation_rate": authority / total,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Independent decision-layer evaluation.")
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True, help="JSON: {policy_id: {case_id: decision}}")
    args = parser.parse_args()
    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    decisions = json.loads(args.decisions.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_decisions(suite, decisions), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
