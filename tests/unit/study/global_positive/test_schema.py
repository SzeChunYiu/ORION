from __future__ import annotations

import dataclasses

from orion.development.protocol import assert_ready_to_implement
from orion.study.global_positive.admission import AdmissionDecision, published_programme_state
from orion.study.global_positive.packet import build_packet
from orion.study.global_positive.portfolio import (
    REQUIRED_SPLIT_IDS,
    freeze_fingerprint,
    load_portfolio,
    portfolio_hash,
)
from orion.study.global_positive.schema import (
    FORBIDDEN_SCALAR_KEYS,
    ProgrammeTerminal,
    load_schema,
    protocol_document,
    protocol_hash,
    schema_hash,
)


def test_schema_names_all_issue_285_dimensions() -> None:
    schema = load_schema()
    assert schema.schema_id == "GlobalPositiveCertificate.v1"
    assert schema.mandatory_ids == (
        "correctness",
        "fresh_transfer",
        "harmful_transfer",
        "false_authority",
        "abstention_correctness",
        "retrieval_recall",
        "obstruction_safety",
        "cost",
        "evaluator_integrity",
    )
    assert schema.primary_utility_ids == ("correctness", "fresh_transfer")
    assert not schema.phase4_operation_authorized
    assert schema.min_prospective_rounds == 2
    assert schema.requires_independent_verification_issue == 283
    assert FORBIDDEN_SCALAR_KEYS.issubset(schema.forbidden_primary_authority)


def test_schema_hash_is_stable_content_address() -> None:
    pinned = "b5dbcdea86814fcb7925d5003d9a8d76536839ba3683baa1ea30b32cf33bdc62"
    assert schema_hash() == pinned
    assert schema_hash() == load_schema().fingerprint
    assert len(schema_hash()) == 64
    assert schema_hash() != portfolio_hash()
    assert freeze_fingerprint() == freeze_fingerprint()


def test_admission_decision_has_no_scalar_authority_field() -> None:
    names = {field.name for field in dataclasses.fields(AdmissionDecision)}
    assert not names & {
        "average_score",
        "global_score",
        "mean_score",
        "scalar_utility",
        "weighted_sum",
    }
    assert "admitted" in names


def test_published_portfolio_has_four_required_unbound_families() -> None:
    freeze = load_portfolio()
    assert len(freeze.required_family_ids) == 4
    assert freeze.required_splits == REQUIRED_SPLIT_IDS
    assert freeze.outcome_accessed is False
    assert freeze.phase4_operation_authorized is False
    for family_id in freeze.required_family_ids:
        slot = freeze.family(family_id)
        assert slot.unbound
        assert slot.slot_status == "CANNOT_CHECK"
        assert len(slot.split_identities) == 4
    optional = freeze.family("hidden_cause_fresh_transfer")
    assert optional.required_for_admission is False
    assert optional.unbound


def test_test_binding_is_not_the_published_v1_identity() -> None:
    published = load_portfolio()
    bound = published.bind_for_tests("nonce-a")
    other = published.bind_for_tests("nonce-b")
    assert bound.fingerprint != published.fingerprint
    assert bound.fingerprint != other.fingerprint
    assert published.fingerprint == load_portfolio().fingerprint


def test_retuned_margins_are_a_different_object() -> None:
    freeze = load_portfolio()
    retuned = freeze.with_margin_document("cost", 0.99)
    assert retuned["retuned_margin"] != retuned["original_margin"]
    assert retuned["portfolio_fingerprint"] == freeze.fingerprint


def test_protocol_forbids_phase4_and_has_not_seen_outcomes() -> None:
    protocol = protocol_document()
    assert protocol["outcome_accessed"] is False
    assert protocol["phase4_operation_authorized"] is False
    assert protocol["min_prospective_rounds_for_global_positive_supported"] == 2
    assert "PHASE_4_SELF_SUSTAINING_RESEARCH_PROGRAM_CLOSED" in protocol["does_not_authorize"]
    assert len(protocol_hash()) == 64


def test_published_programme_terminal_is_cannot_check() -> None:
    decision = published_programme_state()
    assert decision.terminal is ProgrammeTerminal.CANNOT_CHECK
    assert decision.phase4_operation_authorized is False
    assert "required_family_tasks_unbound" in decision.reasons
    assert "insufficient_prospective_rounds" in decision.reasons
    assert "missing_issue_283_verification_receipt" in decision.reasons


def test_development_packet_is_ready_to_implement() -> None:
    packet = build_packet()
    assert_ready_to_implement(packet)
    assert packet.task_id == "issue-285-global-positive-certificate-v1"
