#!/usr/bin/env python3
"""Independent model-session audit for the frozen Self-ORION V4 result.

No V4 policy/scorer/runner code is imported. The audit reads frozen bytes,
validates the receipt's raw-file custody hashes, re-derives performance content
from committed metrics, and evaluates both (a) the declared frozen rule text and
(b) the executable runner semantics. A post-outcome implementation discrepancy
is retained rather than repaired in-place; bounded verification is permitted
only if it is non-controlling for the observed terminal.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CONF = ROOT / "research/self-orion-v4/confirmatory"
RECEIPT = CONF / "CONFIRMATORY_EXECUTION_RECEIPT_2026-08-27.json"
RULES = CONF / "CONFIRMATORY_DECISION_RULES_V2.json"
SUITE = CONF / "PROTECTED_CONFIRMATORY_SUITE_V2.json"
PACKET = CONF / "CANDIDATE_PACKET_V2.json"
SPLIT = CONF / "CONFIRMATORY_FINAL_SPLIT_V2.json"
BASELINES = CONF / "BASELINE_CONFIG_V2.json"
DECISION_EVAL = CONF / "protected_evaluator_v2.py"
FRESH_EVAL = CONF / "fresh_transfer_evaluator_v2.py"
RUNNER = CONF / "run_confirmatory_execution_v2.py"
PROTOCOL = ROOT / "papers/orion-15-self-orion/protocol/SELF_ORION_V4_REVISION_LEVEL_PROTOCOL_V1.json"
V3 = ROOT / "research/self-orion-v3/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json"
OUT = Path(__file__).resolve().parent / "SCIENTIFIC_RESULT_VERIFICATION_V1.json"
EVALUATED_SCIENCE_COMMIT = "7e8e347f560f10390e7e71507a7ea01e73c5d400"


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise AssertionError(msg)


def raw_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def policy_metrics(receipt: dict[str, Any], policy: str) -> dict[str, Any]:
    row = receipt["policies"][policy]
    return {
        "accuracy": float(row["decision_layer"]["revision_label_accuracy"]),
        "false_broad": float(row["decision_layer"]["false_broad_revision_rate"]),
        "authority": float(row["decision_layer"]["authority_violation_rate"]),
        "correct_unresolved": float(row["decision_layer"]["correct_unresolved_rate"]),
        "preservation_refusal": float(row["decision_layer"]["preservation_stratum_correct_refusal_rate"]),
        "per_class": {k: float(v) for k, v in row["decision_layer"]["per_gold_class_accuracy"].items()},
        "harm": float(row["fresh_transfer_layer"]["harmful_regression_rate"]),
        "fresh": float(row["fresh_transfer_layer"]["fresh_transfer_success_rate"]),
        "split": {k: float(v) for k, v in row["split_half_accuracy"].items()},
    }


def content(receipt: dict[str, Any], rules: dict[str, Any], policy: str, *, executable_false_broad: bool) -> tuple[bool, dict[str, Any]]:
    metrics = {p: policy_metrics(receipt, p) for p in receipt["policies"]}
    m = metrics[policy]
    margins = rules["margins"]
    non_floor = list(rules["non_floor_policies"])
    strong = list(rules["strong_comparators"])
    repair_classes = [k for k in m["per_class"] if k != "UNRESOLVED"]
    accuracy_ok = m["accuracy"] >= float(margins["min_subject_accuracy"])
    class_ok = all(m["per_class"][k] >= float(margins["min_subject_per_repair_class_accuracy"]) for k in repair_classes)
    if executable_false_broad:
        # Exact implementation in run_confirmatory_execution_v2.py.
        false_broad_ok = m["false_broad"] <= max(metrics[q]["false_broad"] for q in non_floor) + 1e-12
    else:
        # Exact declared condition in CONFIRMATORY_DECISION_RULES_V2.json.
        false_broad_ok = all(m["false_broad"] <= metrics[q]["false_broad"] + 1e-12 for q in non_floor)
    harm_ok = all(m["harm"] <= metrics[q]["harm"] + 1e-12 for q in non_floor)
    authority_ok = all(m["authority"] <= metrics[q]["authority"] + 1e-12 for q in non_floor)
    best_fresh = max(metrics[q]["fresh"] for q in strong)
    fresh_ok = m["fresh"] >= best_fresh - float(margins["fresh_transfer_noninferiority"]) - 1e-12
    half_relations: dict[str, dict[str, bool]] = {}
    halves_ok = True
    for q in strong:
        rel_a = m["split"]["PRIMARY_A"] >= metrics[q]["split"]["PRIMARY_A"]
        rel_b = m["split"]["REPLICATION_B"] >= metrics[q]["split"]["REPLICATION_B"]
        half_relations[q] = {"PRIMARY_A_subject_not_worse": rel_a, "REPLICATION_B_subject_not_worse": rel_b}
        if rel_a != rel_b:
            halves_ok = False
    detail = {
        "accuracy_ok": accuracy_ok,
        "per_repair_class_ok": class_ok,
        "false_broad_no_worse": false_broad_ok,
        "harm_no_worse_than_non_floor": harm_ok,
        "violations_no_worse_than_non_floor": authority_ok,
        "fresh_noninferior_within_margin": fresh_ok,
        "split_half_direction_agreement": halves_ok,
        "half_relations": half_relations,
    }
    return all(v for k, v in detail.items() if k != "half_relations"), detail


def comparator_arms(rules: dict[str, Any]) -> list[str]:
    r = rules["policy_roles"]
    require(r["controls"] == ["RANDOM_DIAGNOSTIC", "ALWAYS_UNRESOLVED"], "control identities drift")
    return [
        r["no_edit_arm"],
        r["direct_self_edit_arm"],
        *r["mechanism_comparators"],
        r["diagnosis_parent"],
        "RANDOM_DIAGNOSTIC",
        r["parent_subject"],
    ]


def unique_rule4_terminal(receipt: dict[str, Any], rules: dict[str, Any], *, executable_false_broad: bool) -> tuple[str, bool, list[str], dict[str, Any]]:
    subject = rules["policy_roles"]["subject"]
    subject_ok, subject_detail = content(receipt, rules, subject, executable_false_broad=executable_false_broad)
    others = []
    for p in comparator_arms(rules):
        ok, _ = content(receipt, rules, p, executable_false_broad=executable_false_broad)
        if ok:
            others.append(p)
    if subject_ok and others:
        return "NO_INCREMENTAL_VALUE", subject_ok, others, subject_detail
    if subject_ok and not others:
        return "REVISION_LEVEL_DISCRIMINATION_SUPPORTED", subject_ok, others, subject_detail
    return "NOT_RULE_3_OR_4", subject_ok, others, subject_detail


def main() -> int:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    v3 = json.loads(V3.read_text(encoding="utf-8"))
    runner_text = RUNNER.read_text(encoding="utf-8")

    require(rules["created_before_outcome_access"] is True, "rules not prospective")
    require(receipt["outcome_accessed"] is True, "V4 outcome absent")
    require(receipt["grants_scientific_authority"] is False, "source receipt self-promoted")
    require(v3["frozen_rule_evaluation"]["terminal"] == "NO_TERMINAL_UNDER_FROZEN_RULES", "V3 negative not retained")
    require(v3["frozen_rule_evaluation"]["no_frozen_terminal_fired"] is True, "V3 no-terminal flag drift")
    require(receipt["cross_check_independent_evaluators"]["all_ok"] is True, "embedded evaluator disagreement")
    require(receipt["h4_digest_determinism"]["all_ok"] is True, "deterministic replay failed")
    for row in receipt["h4_digest_determinism"]["per_policy"].values():
        require(row["n_decisions"] == 180 and row["digest_equal_count"] == 180, "per-policy replay drift")

    # The source runner registers raw file SHA-256 for all custody entries.
    custody_paths = {
        "baseline_config": BASELINES,
        "candidate_packet": PACKET,
        "decision_rules": RULES,
        "final_split": SPLIT,
        "protected_suite": SUITE,
        "protocol": PROTOCOL,
        "decision_evaluator": DECISION_EVAL,
        "fresh_transfer_evaluator": FRESH_EVAL,
        "runner": RUNNER,
    }
    observed: dict[str, str] = {}
    require(set(custody_paths) == set(receipt["custody_sha256"]), "custody key set drift")
    for key, path in sorted(custody_paths.items()):
        digest = raw_sha(path)
        require(digest == receipt["custody_sha256"][key], f"raw custody mismatch {key}: {digest} != {receipt['custody_sha256'][key]}")
        observed[key] = digest

    subject = rules["policy_roles"]["subject"]
    require(subject == "FULL_T7_V4", "subject identity")
    sm = policy_metrics(receipt, subject)
    require(sm["accuracy"] == 1.0, "subject accuracy")
    require(sm["false_broad"] == 0.0 and sm["authority"] == 0.0 and sm["harm"] == 0.0, "subject safety metrics")
    require(sm["preservation_refusal"] == 1.0, "preservation refusal")
    require(abs(sm["fresh"] - 0.8888888888888888) < 1e-15, "fresh transfer")

    # Detect and retain the post-outcome rule-implementation discrepancy.
    declared_condition = rules["performance_content_definition"]["conditions"][2]
    require("every non-floor policy" in declared_condition, "declared false-broad rule drift")
    require("non_floor_fb = max(" in runner_text and "<= non_floor_fb" in runner_text, "expected executable false-broad implementation not found")

    declared_terminal, declared_subject_ok, declared_others, declared_detail = unique_rule4_terminal(
        receipt, rules, executable_false_broad=False
    )
    executable_terminal, executable_subject_ok, executable_others, executable_detail = unique_rule4_terminal(
        receipt, rules, executable_false_broad=True
    )
    terminal = "REVISION_LEVEL_DISCRIMINATION_SUPPORTED"
    require(declared_terminal == terminal, f"declared frozen semantics do not support terminal: {declared_terminal}")
    require(executable_terminal == terminal, f"executable semantics do not support terminal: {executable_terminal}")
    require(declared_subject_ok and executable_subject_ok, "subject performance content failed")
    require(declared_others == [] and executable_others == [], "incremental-value boundary failed")
    require(receipt["frozen_rules_terminal"]["terminal"] == terminal, "source receipt terminal disagrees")
    require(receipt["frozen_rules_terminal"]["rule_trace"] == [{"evidence": {"other_policies_satisfying_content": [], "subject_satisfies_content": True}, "order": 4, "terminal": terminal}], "source rule trace drift")
    require(all(bool(v) for v in receipt["bindings_verification"].values() if isinstance(v, bool)), "binding verification false")
    require(receipt["policies"][rules["policy_roles"]["analysis_only_ceiling"]]["decision_layer"]["revision_label_accuracy"] == 1.0, "oracle ceiling")

    floors = [policy_metrics(receipt, p) for p in rules["floors"]]
    harmful_refuted = sm["harm"] > max(x["harm"] for x in floors) + 1e-12 or sm["authority"] > max(x["authority"] for x in floors) + 1e-12
    require(not harmful_refuted, "harmful-refuted rule would precede rule 4")

    record = {
        "schema": "ORION.ScientificResultVerification.v1",
        "paper_id": "ORION-15",
        "claim_id": "ORION-15.V4.REVISION_LEVEL_DISCRIMINATION",
        "date": "2026-08-27",
        "evaluated_science_commit": EVALUATED_SCIENCE_COMMIT,
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": observed["protocol"],
        "raw_execution_receipt": str(RECEIPT.relative_to(ROOT)),
        "raw_execution_receipt_sha256": raw_sha(RECEIPT),
        "custody_bindings_raw_sha256": observed,
        "verification_method": "separate-model-session raw custody audit plus scorer-independent metric/performance-content/terminal recomputation from frozen committed receipt; no child-commit source execution claimed",
        "source_execution_replay_evidence": {
            "embedded_independent_evaluators_agree": True,
            "deterministic_digest_replay_180_per_policy": True,
            "new_child_commit_execution_claimed": False,
        },
        "v3_negative_retained": "NO_TERMINAL_UNDER_FROZEN_RULES",
        "subject_metrics": sm,
        "declared_frozen_semantics": {
            "terminal": declared_terminal,
            "subject_satisfies_content": declared_subject_ok,
            "other_arms_satisfying_content": declared_others,
            "subject_content_detail": declared_detail,
        },
        "executable_runner_semantics": {
            "terminal": executable_terminal,
            "subject_satisfies_content": executable_subject_ok,
            "other_arms_satisfying_content": executable_others,
            "subject_content_detail": executable_detail,
        },
        "rule_implementation_defect": {
            "detected": True,
            "declared": "false_broad_revision_rate <= every non-floor policy",
            "implemented": "false_broad_revision_rate <= maximum non-floor policy rate",
            "post_outcome_in_place_repair_permitted": False,
            "controlling_for_observed_terminal": False,
            "reason": "Both declared and executable semantics independently yield rule-4 REVISION_LEVEL_DISCRIMINATION_SUPPORTED with FULL_T7_V4 as the unique non-oracle issue-1541 arm satisfying performance content.",
        },
        "recomputed_terminal": terminal,
        "verification_state": "BOUNDED_VERIFIED_WITH_NONCONTROLLING_EXECUTABLE_RULE_DEFECT",
        "grants_human_peer_review_authority": False,
        "grants_external_real_world_validity": False,
        "grants_live_provider_claim": False,
        "evidence_only_not_self_authorizing": True,
        "bounded_claim": "On the frozen 180-case V4 benchmark-local successor panel, FULL_T7_V4 is the unique registered non-oracle issue-1541 arm satisfying the declared frozen performance content: 1.000 revision accuracy, zero false-broad/harm/authority violations, 1.000 preservation-conflict refusal, and fresh-transfer rate 0.889, with split-half direction agreement. The same rule-4 terminal is invariant to the retained executable false-broad implementation defect. This does not establish live-provider or general self-improvement superiority.",
        "terminal": "ORION_15_V4_BOUNDED_VERIFIED_WITH_RULE_DEFECT_RETAINED",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(record["terminal"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"ORION_15_V4_INDEPENDENT_VERIFY=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
