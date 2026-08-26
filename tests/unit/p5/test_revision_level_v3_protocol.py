from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5.revision_level_v3_preflight import (
    BaselineBindingDisposition,
    BaselineStructuralBinding,
    ConfirmatoryExecutionBinding,
    ConfirmatoryPreflightStatus,
    assess_confirmatory_preflight,
)

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-15-self-orion"
PROTOCOL = PAPER / "protocol" / "SELF_ORION_V3_REVISION_LEVEL_PROTOCOL_V1.json"
BASELINES = ROOT / "research" / "self-orion-v3" / "BASELINE_STRUCTURAL_BINDINGS_V1.json"


def _load_preflight():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    raw_bindings = json.loads(BASELINES.read_text(encoding="utf-8"))
    raw = protocol["confirmatory_execution_bindings"]
    execution = ConfirmatoryExecutionBinding(
        protocol_id=protocol["protocol_id"],
        subject_revision=raw["subject_revision"],
        protected_suite_commitment=raw["protected_suite_commitment"],
        candidate_packet_sha256=raw["candidate_packet_sha256"],
        final_split_sha256=raw["final_split_sha256"],
        evaluator_sha256=raw["evaluator_sha256"],
        evaluation_epoch=raw["evaluation_epoch"],
        baseline_config_sha256=raw["baseline_config_sha256"],
        fresh_transfer_evaluator_sha256=raw["fresh_transfer_evaluator_sha256"],
        result_verifier_owner=raw["result_verifier_owner"],
        candidate_policy_owner=raw["candidate_policy_owner"],
        protected_evaluator_owner=raw["protected_evaluator_owner"],
        outcome_accessed=raw["outcome_accessed"],
    )
    baselines = tuple(
        BaselineStructuralBinding.build(
            baseline_id=item["baseline_id"],
            donor_id=item["donor_id"],
            source_identity=item["source_identity"],
            disposition=BaselineBindingDisposition(item["disposition"]),
            structural_binding_id=item["structural_binding_id"],
            official_reproduction=item["official_reproduction"],
            notes=tuple(item["notes"]),
        )
        for item in raw_bindings["records"]
    )
    return protocol, baselines, assess_confirmatory_preflight(
        execution,
        baselines,
        required_baseline_ids=tuple(protocol["confirmatory_required_baseline_bindings"]),
    )


def test_current_v3_protocol_preserves_adverse_confirmatory_execution() -> None:
    protocol, baselines, report = _load_preflight()
    assert (
        protocol["protocol_status"]
        == "CONFIRMATORY_EXECUTED_2026-08-24_NO_TERMINAL_UNDER_FROZEN_RULES"
    )
    assert protocol["outcome_accessed"] is True
    assert protocol["grants_scientific_authority"] is False
    assert protocol["grants_peer_review_ready"] is False
    assert report.status is ConfirmatoryPreflightStatus.CANNOT_CHECK
    assert "outcome_accessed_before_confirmatory_freeze" in report.blockers
    assert any("m_open_only" in blocker for blocker in report.blockers)
    assert not any("subject_revision" in blocker for blocker in report.blockers)
    assert not any("world_model_revision" in blocker for blocker in report.blockers)
    assert not any("representation_regime_revision" in blocker for blocker in report.blockers)

    by_id = {binding.baseline_id: binding for binding in baselines}
    assert by_id["m_open_only"].disposition is BaselineBindingDisposition.CANNOT_CHECK
    assert by_id["world_model_revision"].disposition is BaselineBindingDisposition.MECHANISM_COMPARATOR_BOUND
    assert by_id["representation_regime_revision"].disposition is BaselineBindingDisposition.MECHANISM_COMPARATOR_BOUND
    assert by_id["world_model_revision"].structural_binding_id == "ssa:v1:worldevolver-2606.30639v1"
    assert by_id["representation_regime_revision"].structural_binding_id == "ssa:v1:self-revising-2606.01444v1"


def test_protocol_freezes_454_receipt_programme_without_claiming_official_reproduction() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert protocol["explicitly_not_frozen_as_universal_taxonomy"] is True
    for policy in protocol["policy_families"]:
        if "donor" in policy:
            assert policy.get("official_reproduction") is False

    structural = protocol["structural_binding_status"]
    assert structural["programme_receipt_owner"] == "#454"
    assert structural["programme_receipt_frozen"] is True
    assert structural["current_disposition"] == "CANNOT_CHECK"
    assert structural["current_blocker"] == "MDA_PRIMARY_FULL_TEXT_NOT_SOURCE_GROUNDED_2026-08-19"


def test_development_fixture_cannot_close_p5_or_issue_455() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    dev = protocol["development_instrumentation"]
    assert dev["development_only"] is True
    assert dev["may_support_scientific_claim"] is False
    assert dev["may_close_issue_455"] is False
    assert protocol["relationship_to_existing_p5"]["h1_h4"] == "CANNOT_CHECK"
