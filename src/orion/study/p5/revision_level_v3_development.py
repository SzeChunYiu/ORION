"""Development-only instrumentation runner for Self-ORION V3.

This runner intentionally uses a public synthetic protected suite.  Its purpose is
to prove custody transformations, policy execution, scorer behavior, and evidence
sensitivity before any confirmatory freeze.  The terminal is implementation-only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from orion.study.p5.revision_level_v3_freeze import (
    derive_candidate_packet,
    derive_protected_commitment,
    validate_protected_suite,
)
from orion.study.p5.revision_level_v3_policies import (
    FeedbackMode,
    PolicyKind,
    ProtectedFeedbackOracle,
    run_revision_policy,
)
from orion.study.p5.revision_level_v3_preflight import (
    BaselineBindingDisposition,
    BaselineStructuralBinding,
    ConfirmatoryExecutionBinding,
    assess_confirmatory_preflight,
)
from orion.study.p5.revision_level_v3_score import score_revision_decisions
from orion.study.p5.freeze import sha256_json


POLICIES = (
    PolicyKind.NO_REVISION,
    PolicyKind.DIRECT_SELF_EDIT,
    PolicyKind.M_OPEN_ONLY,
    PolicyKind.WORLD_MODEL_REVISION,
    PolicyKind.REPRESENTATION_REGIME_ONLY,
    PolicyKind.GENERIC_CAUSAL_DIAGNOSIS,
    PolicyKind.FULL_T7,
    PolicyKind.RANDOM_DIAGNOSTIC,
    PolicyKind.ALWAYS_UNRESOLVED,
    PolicyKind.ORACLE_CEILING,
)

ADAPTIVITY_MODES = (
    FeedbackMode.NORMAL,
    FeedbackMode.PERMUTED,
    FeedbackMode.NONE,
    FeedbackMode.CONTRADICTORY,
    FeedbackMode.RANDOM,
)


def _case_index(suite: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(case["case_id"]): case for case in suite["cases"]}


def _alternate_outcomes(case: Mapping[str, Any]) -> dict[str, str]:
    gold = str(case["protected_gold_revision_class"])
    actual = {str(key): str(value) for key, value in case["protected_diagnostic_outcomes"].items()}
    hypotheses = case["hypotheses"]
    result: dict[str, str] = {}
    for action_id, actual_outcome in actual.items():
        candidates: list[str] = []
        for label, prediction in hypotheses.items():
            if str(label) == gold:
                continue
            for outcome in prediction.get(action_id, []):
                value = str(outcome)
                if value != actual_outcome:
                    candidates.append(value)
        result[action_id] = sorted(set(candidates))[0] if candidates else "CONTRADICTORY_FEEDBACK"
    return result


def _oracle(case: Mapping[str, Any], mode: FeedbackMode) -> ProtectedFeedbackOracle:
    return ProtectedFeedbackOracle(
        case_id=str(case["case_id"]),
        outcome_by_action={str(k): str(v) for k, v in case["protected_diagnostic_outcomes"].items()},
        mode=mode,
        alternate_outcomes=_alternate_outcomes(case),
    )


def _policy_score(suite: Mapping[str, Any], packet: Mapping[str, Any], policy: PolicyKind, mode: FeedbackMode):
    protected = _case_index(suite)
    decisions = []
    for candidate in packet["cases"]:
        case_id = str(candidate["case_id"])
        protected_case = protected[case_id]
        kwargs = {}
        if policy is PolicyKind.ORACLE_CEILING:
            kwargs["protected_gold_revision_class"] = str(protected_case["protected_gold_revision_class"])
        decisions.append(run_revision_policy(policy, candidate, _oracle(protected_case, mode), **kwargs))
    return score_revision_decisions(suite, tuple(decisions))


def _score_row(report) -> dict[str, object]:
    return {
        "revision_accuracy": report.revision_accuracy,
        "correct_revision_count": report.correct_revision_count,
        "false_broad_revision_rate": report.false_broad_revision_rate,
        "false_broad_revision_count": report.false_broad_revision_count,
        "correct_unresolved_count": report.correct_unresolved_count,
        "correct_unresolved_denominator": report.correct_unresolved_denominator,
        "total_diagnostic_actions": report.total_diagnostic_actions,
        "total_diagnostic_cost": report.total_diagnostic_cost,
        "analysis_only": report.analysis_only,
        "eligible_for_superiority_claim": report.eligible_for_superiority_claim,
    }


def _blocked_preflight() -> dict[str, object]:
    binding = ConfirmatoryExecutionBinding(
        protocol_id="P5.self-orion-v3.revision-level.v1",
        subject_revision="UNBOUND",
        protected_suite_commitment="UNBOUND",
        candidate_packet_sha256="UNBOUND",
        final_split_sha256="UNBOUND",
        evaluator_sha256="UNBOUND",
        evaluation_epoch="UNBOUND",
        baseline_config_sha256="UNBOUND",
        fresh_transfer_evaluator_sha256="UNBOUND",
        result_verifier_owner="#283",
        candidate_policy_owner="SelfOrionV3Policy",
        protected_evaluator_owner="ExternalProtectedEvaluator",
        outcome_accessed=False,
    )
    baselines = tuple(
        BaselineStructuralBinding.build(
            baseline_id=baseline_id,
            donor_id=donor_id,
            source_identity=source_identity,
            disposition=BaselineBindingDisposition.CANNOT_CHECK,
            structural_binding_id="",
            official_reproduction=False,
            notes=("#454 programme-wide structural receipt not frozen; T8 implementation may not call this official reproduction",),
        )
        for baseline_id, donor_id, source_identity in (
            ("m_open_only", "arxiv:2608.09696", "MDA:mechanism-class-expansion"),
            ("world_model_revision", "arxiv:2606.30639", "world-model:self-revision-mechanism"),
            ("representation_regime_revision", "arxiv:2606.01444", "representation-regime:transition-mechanism"),
        )
    )
    report = assess_confirmatory_preflight(
        binding,
        baselines,
        required_baseline_ids=("m_open_only", "world_model_revision", "representation_regime_revision"),
    )
    return {
        "status": report.status.value,
        "blockers": list(report.blockers),
        "grants_scientific_authority": report.grants_scientific_authority,
        "grants_p5_peer_review_ready": report.grants_p5_peer_review_ready,
    }


def derive_development_summary(protected_suite: Mapping[str, Any]) -> dict[str, object]:
    validate_protected_suite(protected_suite)
    if protected_suite.get("development_only") is not True:
        raise ValueError("development runner refuses non-development suite")
    packet = derive_candidate_packet(protected_suite)

    policy_scores = {
        policy.value: _score_row(_policy_score(protected_suite, packet, policy, FeedbackMode.NORMAL))
        for policy in POLICIES
    }
    adaptivity = {
        mode.value: _score_row(_policy_score(protected_suite, packet, PolicyKind.FULL_T7, mode))
        for mode in ADAPTIVITY_MODES
    }
    preflight = _blocked_preflight()

    full_normal = float(adaptivity[FeedbackMode.NORMAL.value]["revision_accuracy"])
    full_none = float(adaptivity[FeedbackMode.NONE.value]["revision_accuracy"])
    full_permuted = float(adaptivity[FeedbackMode.PERMUTED.value]["revision_accuracy"])
    oracle = float(policy_scores[PolicyKind.ORACLE_CEILING.value]["revision_accuracy"])
    instrumentation_green = (
        full_normal == 1.0
        and oracle == 1.0
        and full_none < full_normal
        and full_permuted < full_normal
        and preflight["status"] == "CANNOT_CHECK"
        and preflight["grants_scientific_authority"] is False
        and preflight["grants_p5_peer_review_ready"] is False
    )
    terminal = (
        "T8_PROSPECTIVE_EXPERIMENT_IMPLEMENTED_CANNOT_CHECK_OUTCOME"
        if instrumentation_green
        else "T8_DEVELOPMENT_INSTRUMENTATION_RED"
    )
    return {
        "schema": "SelfOrionV3DevelopmentSummary.v1",
        "suite_id": protected_suite["suite_id"],
        "development_only": True,
        "protected_commitment": derive_protected_commitment(protected_suite),
        "candidate_packet_sha256": sha256_json(packet),
        "n_cases": len(packet["cases"]),
        "policy_scores": policy_scores,
        "full_t7_feedback_sensitivity": adaptivity,
        "confirmatory_preflight": preflight,
        "terminal": terminal,
        "scientific_result": "NOT_RUN",
        "supports_p5_h1_h4": False,
        "grants_peer_review_ready": False,
        "closes_issue_455": False,
    }


def load_and_derive(path: Path) -> dict[str, object]:
    return derive_development_summary(json.loads(path.read_text(encoding="utf-8")))


__all__ = [
    "ADAPTIVITY_MODES",
    "POLICIES",
    "derive_development_summary",
    "load_and_derive",
]
