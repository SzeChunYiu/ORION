"""Freeze the Self-ORION V4 confirmatory bindings (successor panel, subject FULL_T7_V4).

Runs AFTER the suite/packet/split/rules/evaluator artifacts are generated and
BEFORE any V4 outcome is accessed.  Writes:
  - research/self-orion-v4/confirmatory/BASELINE_CONFIG_V2.json
  - papers/orion-15-self-orion/protocol/SELF_ORION_V4_REVISION_LEVEL_PROTOCOL_V1.json
  - research/self-orion-v4/confirmatory/CONFIRMATORY_FREEZE_RECEIPT_2026-08-27.json
and enforces preflight READY_TO_FREEZE_CONFIRMATORY (fail closed).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from orion.study.p5.revision_level_v3_freeze import (
    derive_candidate_packet,
    derive_protected_commitment,
    validate_protected_suite,
)

ROOT = Path(__file__).resolve().parents[3]
CONFIRMATORY = ROOT / "research" / "self-orion-v4" / "confirmatory"
PROTOCOL_PATH = ROOT / "papers" / "orion-15-self-orion" / "protocol" / "SELF_ORION_V4_REVISION_LEVEL_PROTOCOL_V1.json"
PREFLIGHT = ROOT / "research" / "self-orion-v4" / "run_confirmatory_preflight_v2.py"

SUITE = CONFIRMATORY / "PROTECTED_CONFIRMATORY_SUITE_V2.json"
PACKET = CONFIRMATORY / "CANDIDATE_PACKET_V2.json"
SPLIT = CONFIRMATORY / "CONFIRMATORY_FINAL_SPLIT_V2.json"
RULES = CONFIRMATORY / "CONFIRMATORY_DECISION_RULES_V2.json"
GENERATOR = CONFIRMATORY / "build_confirmatory_suite_v2.py"
DECISION_EVAL = CONFIRMATORY / "protected_evaluator_v2.py"
FRESH_EVAL = CONFIRMATORY / "fresh_transfer_evaluator_v2.py"
CONFIG = CONFIRMATORY / "BASELINE_CONFIG_V2.json"
FREEZE_RECEIPT = CONFIRMATORY / "CONFIRMATORY_FREEZE_RECEIPT_2026-08-27.json"

SUBJECT_BUNDLE = [
    "src/orion/study/p5/revision_level_v3_freeze.py",
    "src/orion/study/p5/revision_level_v3_policies.py",
    "src/orion/study/p5/revision_level_v3_preflight.py",
    "src/orion/study/p5/revision_level_v3_score.py",
    "src/orion/study/p5/revision_level_v4_policies.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    validate_protected_suite(suite)
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    if packet != derive_candidate_packet(suite):
        raise SystemExit("candidate packet does not equal the derivation of the protected suite")
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    n_cases = len(suite["cases"])
    if n_cases != 180 or len(split["assignment"]) != n_cases:
        raise SystemExit(f"unexpected panel size: suite={n_cases} split={len(split['assignment'])}")

    suite_sha = sha(SUITE)
    packet_sha = sha(PACKET)
    split_sha = sha(SPLIT)
    rules_sha = sha(RULES)
    generator_sha = sha(GENERATOR)
    dec_sha = sha(DECISION_EVAL)
    fresh_sha = sha(FRESH_EVAL)
    commitment = derive_protected_commitment(suite)
    concat = b"".join(hashlib.sha256((ROOT / f).read_bytes()).digest() for f in sorted(SUBJECT_BUNDLE))
    subject_revision = hashlib.sha1(concat).hexdigest()

    config = {
        "schema_version": "orion.p5.revision-level-v3.baseline-config.v1",
        "config_id": "P5V4-CONFIRMATORY-BASELINE-CONFIG-2026-08-27",
        "protocol_id": "P5.self-orion-v4.revision-level.v1",
        "created_before_outcome_access": True,
        "subject_bundle": {
            "recipe": "sha1 over the concatenation, in sorted-path order, of sha256(file_bytes).digest() for each listed file",
            "files": sorted(SUBJECT_BUNDLE),
            "subject_revision_sha1": subject_revision,
        },
        "independent_evaluators": {
            "decision_layer": {
                "path": "research/self-orion-v4/confirmatory/protected_evaluator_v2.py",
                "sha256": dec_sha,
                "code_path": "stdlib-only, no orion imports; blind interface over committed JSON",
            },
            "fresh_transfer_layer": {
                "path": "research/self-orion-v4/confirmatory/fresh_transfer_evaluator_v2.py",
                "sha256": fresh_sha,
                "code_path": "stdlib-only, no orion imports; blind interface over committed JSON",
            },
        },
        "frozen_suite_and_split": {
            "suite_path": "research/self-orion-v4/confirmatory/PROTECTED_CONFIRMATORY_SUITE_V2.json",
            "suite_sha256": suite_sha,
            "candidate_packet_path": "research/self-orion-v4/confirmatory/CANDIDATE_PACKET_V2.json",
            "candidate_packet_sha256": packet_sha,
            "final_split_path": "research/self-orion-v4/confirmatory/CONFIRMATORY_FINAL_SPLIT_V2.json",
            "final_split_sha256": split_sha,
            "decision_rules_path": "research/self-orion-v4/confirmatory/CONFIRMATORY_DECISION_RULES_V2.json",
            "decision_rules_sha256": rules_sha,
            "generator_path": "research/self-orion-v4/confirmatory/build_confirmatory_suite_v2.py",
            "generator_sha256": generator_sha,
        },
        "baseline_structural_bindings": {
            "path": "research/self-orion-v3/BASELINE_STRUCTURAL_BINDINGS_V2.json",
            "required_baseline_ids": [
                "m_open_only",
                "world_model_revision",
                "representation_regime_revision",
            ],
            "note": "unchanged V3 structural binding records; every required comparator is MECHANISM_COMPARATOR_BOUND with a bound structural identity and official_reproduction=false",
        },
        "policy_families": [
            {"id": "no_revision", "implementation": "NO_REVISION", "role": "fixed/no-revision control; issue #1541 arm (a) no-edit", "issue_1541_arm": "a_no_edit"},
            {"id": "direct_self_edit", "implementation": "DIRECT_SELF_EDIT", "role": "broad self-edit control; issue #1541 arm (b) direct-self-edit", "issue_1541_arm": "b_direct_self_edit"},
            {"id": "m_open_only", "implementation": "M_OPEN_ONLY", "role": "M-open model-class-expansion mechanism comparator", "donor": "arxiv:2608.09696", "official_reproduction": False},
            {"id": "world_model_revision", "implementation": "WORLD_MODEL_REVISION", "role": "world-model update mechanism comparator", "donor": "arxiv:2606.30639", "official_reproduction": False},
            {"id": "representation_regime_revision", "implementation": "REPRESENTATION_REGIME_ONLY", "role": "representation-regime revision mechanism comparator", "donor": "arxiv:2606.01444", "official_reproduction": False},
            {"id": "generic_causal_diagnosis", "implementation": "GENERIC_CAUSAL_DIAGNOSIS", "role": "multi-hypothesis bounded diagnosis control"},
            {"id": "full_t7", "implementation": "FULL_T7", "role": "V3 confirmatory subject re-measured unchanged as parent arm on the successor panel"},
            {"id": "full_t7_v4", "implementation": "FULL_T7_V4", "role": "V4 preservation-wired subject (revival lever mechanism completion)"},
            {"id": "random_diagnostic", "implementation": "RANDOM_DIAGNOSTIC", "role": "diagnostic-selection chance control"},
            {"id": "always_unresolved", "implementation": "ALWAYS_UNRESOLVED", "role": "refusal floor"},
            {"id": "oracle_ceiling", "implementation": "ORACLE_CEILING", "role": "protected-gold ceiling; analysis only", "analysis_only": True},
        ],
        "feedback_intervention_controls": ["NORMAL", "PERMUTED", "NONE", "CONTRADICTORY", "RANDOM"],
    }
    CONFIG.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    config_sha = sha(CONFIG)

    protocol = {
        "schema_version": "orion.p5.self-orion-v4-revision-level-protocol.v1",
        "protocol_id": "P5.self-orion-v4.revision-level.v1",
        "paper_id": "P5",
        "protocol_status": "CONFIRMATORY_FROZEN_PENDING_EXECUTION",
        "authority_scope": "PROSPECTIVE_PROTOCOL_ONLY",
        "research_question": "On the pre-registered successor panel (development-contract expectation sets completable within the bounded protocol, ambiguous UNRESOLVED cases, and preservation-conflict cases), does the preservation-wired bounded T7 subject reduce wrong or over-broad revision and authority violations while preserving fresh-transfer performance relative to matched strong mechanism comparators and its own V3 parent?",
        "revival_linkage": {
            "v3_receipt": "research/self-orion-v3/confirmatory/CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json",
            "v3_terminal": "NO_TERMINAL_UNDER_FROZEN_RULES",
            "v3_one_stage_attribution": "confirmatory generator modeled TWO diagnostics per hypothesis expectation map while the bounded T7 session observes exactly ONE; frozen V3 decision list was not surjective onto the exposed outcome space",
            "pre_registered_lever": "successor panel with hypothesis expectation sets completable within the bounded protocol (the committed development-suite contract) plus preservation-conflict cases exercising the revision-gate blocking branch; strictly more coverage than the V3 panel; frozen rules surjective onto the outcome space this execution exposed",
            "lever_mechanism_completion": "FULL_T7_V4 wires candidate-visible preservation obligations into assess_mechanic as obligation_states + forbidden_writes, exercising the revision-gate blocking branch that the frozen V3 subject left unreachable; the V3 unexercised-branch defect is closed by making the protected panel contain cases whose correct terminal requires that branch",
        },
        "candidate_access": {
            "visible": [
                "case_id", "symptom_family", "visible_symptom", "candidate_visible_context",
                "competing_revision_classes", "hypothesis discriminator predictions",
                "allowed diagnostics and costs", "diagnostic budget", "revision invasiveness map",
                "preservation obligations", "allowed change surface", "fresh-transfer family identity",
            ],
            "protected": [
                "actual diagnostic outcomes", "gold revision responsibility",
                "protected evaluator internals", "fresh-transfer labels/results before final decision",
                "confirmatory split allocation",
            ],
        },
        "benchmark_local_revision_classes": [
            "EVIDENCE_REPAIR", "MEASUREMENT_REPAIR", "WITHIN_CLASS_MODEL_REPAIR",
            "MODEL_CLASS_EXPANSION", "REPRESENTATION_REGIME_REPAIR", "EXECUTION_REPAIR",
            "EVALUATOR_REPAIR", "UNRESOLVED",
        ],
        "same_symptom_requirement": "Each scored cause-confusable family must contain at least two cases with materially similar candidate-visible symptoms but different protected gold responsibility/revision labels, or an explicit UNRESOLVED gold case; preservation-conflict cases add a third stratum whose correct terminal is refusal.",
        "confirmatory_required_baseline_bindings": [
            "m_open_only", "world_model_revision", "representation_regime_revision",
        ],
        "possible_scientific_terminals_after_real_execution": [
            "CANNOT_CHECK",
            "HARMFUL_REFUTED",
            "NO_INCREMENTAL_VALUE",
            "REVISION_LEVEL_DISCRIMINATION_SUPPORTED",
            "M_OPEN_SUFFICIENT",
            "DIAGNOSIS_ONLY",
            "REVISION_EFFECT_NOT_REPLICATED",
            "OVERCONSERVATIVE",
            "BROKEN_SHUT_SAFETY_FLOOR",
            "NEGATIVE_MISSED_SAFETY_OR_ACCURACY",
        ],
        "terminal_selection_rule": "First-match over the frozen order in research/self-orion-v4/confirmatory/CONFIRMATORY_DECISION_RULES_V2.json; the final rule is unconditional, so exactly one terminal always fires (surjective by construction).",
        "policy_families": config["policy_families"],
        "feedback_intervention_controls": config["feedback_intervention_controls"],
        "mandatory_secondary_endpoints": [
            "correct_unresolved_rate",
            "preservation_stratum_correct_refusal_rate",
            "preservation_violation_rate",
            "evaluator_or_authority_violation_rate",
            "diagnostic_action_count",
            "diagnostic_cost",
            "feedback_permutation_sensitivity",
            "no_feedback_sensitivity",
            "re_execution_digest_equality",
        ],
        "confirmatory_execution_bindings": {
            "subject_revision": subject_revision,
            "protected_suite_commitment": commitment,
            "candidate_packet_sha256": packet_sha,
            "final_split_sha256": split_sha,
            "evaluator_sha256": dec_sha,
            "fresh_transfer_evaluator_sha256": fresh_sha,
            "baseline_config_sha256": config_sha,
            "evaluation_epoch": "P5V4-CONFIRMATORY-EPOCH-2026-08-27",
            "result_verifier_owner": "#283",
            "candidate_policy_owner": "SelfOrionV4Policy",
            "protected_evaluator_owner": "ExternalProtectedEvaluator",
            "outcome_accessed": False,
        },
        "negative_result_policy": "Null, harmful, M-open-sufficient, diagnosis-only, not-replicated, overconservative, safety-floor-broken and missed-safety outcomes are retained as valid terminals and may not be retuned into a positive claim. The V3 negative terminal and its one-stage attribution remain visible in the record alongside this successor execution.",
        "no_scalar_science_score": True,
        "grants_scientific_authority": False,
        "grants_peer_review_ready": False,
        "outcome_accessed": False,
        "structural_binding_status": {
            "programme_receipt_owner": "#454",
            "programme_receipt_frozen": True,
            "current_disposition": "CANNOT_CHECK",
            "current_blocker": "MDA_PRIMARY_FULL_TEXT_NOT_SOURCE_GROUNDED_2026-08-19",
            "rule": "The #454 receipt schema/packet is frozen but its programme disposition remains CANNOT_CHECK while MDA lacks a full structural source; no comparator may be labelled official reproduction without an official-reproduction binding.",
        },
        "relationship_to_existing_p5": {
            "protocol_v1": "UNCHANGED",
            "self_orion_v3": "predecessor; terminal NO_TERMINAL_UNDER_FROZEN_RULES retained as immutable negative",
            "v4_role": "pre-registered revival execution of the V3 lever: successor panel + preservation-wired subject + surjective terminal list",
        },
        "publication_rule": "No development or preflight terminal supports H1-H4, peer-review readiness, or novelty. Any result-bearing update requires exact final bindings, protected execution, independent #283 verification, and #287 nearest-work/novelty authority.",
    }
    PROTOCOL_PATH.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT), "--protocol", str(PROTOCOL_PATH), "--require-ready"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if proc.returncode != 0:
        raise SystemExit(f"preflight not ready (rc={proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    preflight_report = json.loads(proc.stdout)

    receipt = {
        "schema": "orion.p5.self-orion-v4.confirmatory-freeze-receipt.v1",
        "freeze_id": "P5V4-CONFIRMATORY-FREEZE-2026-08-27",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "subject_revision": subject_revision,
        "protected_suite_commitment": commitment,
        "n_cases": n_cases,
        "digests": {
            "suite_sha256": suite_sha,
            "candidate_packet_sha256": packet_sha,
            "final_split_sha256": split_sha,
            "decision_rules_sha256": rules_sha,
            "generator_sha256": generator_sha,
            "decision_evaluator_sha256": dec_sha,
            "fresh_transfer_evaluator_sha256": fresh_sha,
            "baseline_config_sha256": config_sha,
            "protocol_sha256": sha(PROTOCOL_PATH),
        },
        "outcome_accessed": False,
        "preflight_report": preflight_report,
        "grants_scientific_authority": False,
    }
    FREEZE_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "FROZEN", "freeze_receipt": str(FREEZE_RECEIPT), "subject_revision": subject_revision, "protocol": str(PROTOCOL_PATH)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
