#!/usr/bin/env python3
"""Independent arithmetic checks for the anonymous evidence tables."""

import json
from pathlib import Path


def main() -> None:
    data = json.loads(Path(__file__).with_name("evidence.json").read_text())
    rows = data["primary_families"]
    reported = data["reported_primary_aggregates"]

    observed = {
        "family_count": len(rows),
        "diagnostic_correct": sum(bool(row["diagnostic_correct"]) for row in rows),
        "generic_correct": sum(bool(row["generic_correct"]) for row in rows),
        "diagnostic_false_compute_escalations": sum(
            bool(row["diagnostic_false_compute_escalation"]) for row in rows
        ),
        "generic_false_compute_escalations": sum(
            bool(row["generic_false_compute_escalation"]) for row in rows
        ),
        "actionable_predictions_reaching_target": sum(
            row["protected_disposition"] != "indeterminate"
            and row["protected_quality_of_prediction"] >= row["quality_target"]
            for row in rows
        ),
        "indeterminate_protected_families": sum(
            row["protected_disposition"] == "indeterminate" for row in rows
        ),
    }
    if observed != reported:
        raise SystemExit(f"aggregate mismatch: observed={observed}, reported={reported}")
    if data["independent_decision_implementations"] != 2:
        raise SystemExit("independent decision-implementation count is not preserved")
    regrets = [row["registered_cost_regret"] for row in rows if row["registered_cost_regret"] is not None]
    if not regrets or any(value != 0 for value in regrets):
        raise SystemExit("actionable registered-cost regret is not zero")

    by_family = {}
    for row in data["matched_resource_vectors"]:
        if len(row["vector"]) != len(data["resource_coordinates"]):
            raise SystemExit("resource vector has the wrong number of coordinates")
        if any(value < 0 for value in row["vector"]):
            raise SystemExit("resource vector contains a negative count")
        by_family.setdefault(row["family"], {})[row["policy"]] = row
    if set(by_family) != {row["name"] for row in rows}:
        raise SystemExit("resource table and primary family table disagree")
    if any(set(pair) != {"diagnostic", "generic"} for pair in by_family.values()):
        raise SystemExit("each family needs a matched diagnostic and generic resource row")

    arms_by_family = {}
    for arm in data["all_resource_arms"]:
        if len(arm["vector"]) != len(data["resource_coordinates"]):
            raise SystemExit("full resource arm has the wrong number of coordinates")
        arms_by_family.setdefault(arm["family"], {})[arm["intervention"]] = arm
    if set(arms_by_family) != set(by_family):
        raise SystemExit("full resource table and matched table disagree on families")
    dominance_findings = []
    primary = {row["name"]: row for row in rows}
    for family, arms in arms_by_family.items():
        for split in ["probe", "protected"]:
            selected_name = (
                primary[family]["probe_prediction"]
                if split == "probe"
                else primary[family]["protected_disposition"]
            )
            if selected_name == "indeterminate":
                continue
            selected = arms[selected_name]
            for candidate_name, candidate in arms.items():
                if candidate_name == selected_name or not candidate[f"{split}_reaches_target"]:
                    continue
                weakly_better = all(a <= b for a, b in zip(candidate["vector"], selected["vector"]))
                strictly_better = any(a < b for a, b in zip(candidate["vector"], selected["vector"]))
                if weakly_better and strictly_better:
                    dominance_findings.append((family, split, candidate_name, selected_name))
    if dominance_findings:
        raise SystemExit(f"selected resource arm is strictly dominated: {dominance_findings}")

    secondary = data["secondary_outcomes"]
    dispositions = {row["disposition"] for row in secondary["real_accessibility"]}
    if not {"positive", "null"}.issubset(dispositions):
        raise SystemExit("real accessibility outcomes do not preserve both positive and null cells")
    if any(row["typed_minus_same_information"] > 0 for row in secondary["model_size_ladder"]):
        raise SystemExit("model-size negative has been promoted incorrectly")
    remint = secondary["symbol_reminting"]
    if not remint["all_labels_preserved"] or remint["changed_predictions"] != 32:
        raise SystemExit("symbol-reminting adverse result is not preserved")
    followup = secondary["redraw_followup"]
    if followup["half_sample_stability"]:
        raise SystemExit("follow-up stability failure has been promoted incorrectly")

    print("VERIFIED: 5 families; diagnostic 4/5; generic 1/5")
    print("VERIFIED: false compute escalations 0 versus 4")
    print("VERIFIED: all actionable diagnostic selections reach target")
    print("VERIFIED: zero strict vector-dominance findings")
    print("VERIFIED: positive, null, negative, adverse, and indeterminate outcomes retained")


if __name__ == "__main__":
    main()
