from __future__ import annotations

import json
from pathlib import Path

from orion.study.p1_causal.absorbed_mechanics import (
    ABSORBED_COMPONENTS,
    ClaimRecord,
    ClaimStatus,
    CounterfactualRepairCandidate,
    DependencyNode,
    DiagnosticProbe,
    ExecutionRequest,
    InquiryRevisionState,
    InterventionEvidence,
    MutationCertificate,
    RecoveryAction,
    VerificationObligation,
    admit_recovery_action,
    choose_information_probe,
    component_registry,
    dependency_impact_closure,
    enforce_certificate,
    inclusion_minimal_successful_repairs,
    missing_verification_obligations,
)

ROOT = Path(__file__).resolve().parents[4]
P1 = ROOT / "research" / "revival" / "p1"
COVERAGE = P1 / "P1_DONOR_ASSIMILATION_COVERAGE_V1.json"
ENGULFMENT = P1 / "P1_DONOR_ENGULFMENT_V1.json"


def test_engulfment_covers_every_merged_nearest_work_row_once() -> None:
    coverage = json.loads(COVERAGE.read_text())
    engulfment = json.loads(ENGULFMENT.read_text())

    expected = {item["id"]: item for item in coverage["rows"]}
    assigned: dict[str, str] = {}
    component_by_id = {item["component_id"]: item for item in engulfment["components"]}

    for component in engulfment["components"]:
        for row_id in component["matrix_rows"]:
            assert row_id in expected
            assert row_id not in assigned
            assigned[row_id] = component["component_id"]

    assert set(assigned) == set(expected)
    assert len(assigned) == coverage["expected_total"] == 36

    for row_id, row in expected.items():
        mode = component_by_id[assigned[row_id]]["integration_mode"]
        if row["disposition"] in {"ADOPT", "ADAPT", "COMPOSE"}:
            assert mode in {
                "EXECUTABLE_SUBSTRATE",
                "FRAMEWORK_ORCHESTRATION",
                "EVALUATION_GOVERNANCE",
                "FRAMEWORK_KNOWLEDGE",
            }
        elif row["disposition"] == "DEFER":
            assert mode == "DEFERRED_WATCHLIST"
        elif row["disposition"] == "REJECT":
            assert mode == "REJECTED"


def test_runtime_component_registry_matches_engulfment_executable_ids() -> None:
    engulfment = json.loads(ENGULFMENT.read_text())
    runtime = component_registry()
    executable = {
        item["component_id"]
        for item in engulfment["components"]
        if item["integration_mode"] == "EXECUTABLE_SUBSTRATE"
    }
    assert executable == set(runtime)
    assert executable == {item.component_id for item in ABSORBED_COMPONENTS}


def test_inquiry_revision_state_is_explicit_scoped_and_revisable() -> None:
    state = InquiryRevisionState().add(
        ClaimRecord(
            claim_id="k1",
            text="baseline explanation",
            scope=("task:A",),
            support_ids=("e1",),
        )
    )
    state = state.update(
        "k1",
        text="qualified explanation",
        status=ClaimStatus.QUALIFIED,
    )
    assert state.active_for_scope("task:A")[0].status is ClaimStatus.QUALIFIED
    state = state.invalidate("k1", refute_id="e2")
    assert state.by_id("k1").status is ClaimStatus.INVALIDATED
    assert state.active_for_scope("task:A") == ()


def test_intervention_evidence_and_active_probe_do_not_mint_authority() -> None:
    evidence = InterventionEvidence(
        intervention_id="i1",
        hypothesized_cause="FORMULATION",
        predicted_observable="residual",
        expected_direction="vanish",
        observed_direction="vanish",
    )
    assert evidence.supports_hypothesis is True
    probe = choose_information_probe(
        ("EVIDENCE", "SEARCH_UNIVERSE"),
        (
            DiagnosticProbe("blind", frozenset(), 1.0),
            DiagnosticProbe(
                "source",
                frozenset({"EVIDENCE", "SEARCH_UNIVERSE"}),
                1.0,
            ),
        ),
    )
    assert probe is not None and probe.probe_id == "source"
    assert not hasattr(evidence, "granted")


def test_counterfactual_minimal_repair_is_absorbed_but_not_authority() -> None:
    result = inclusion_minimal_successful_repairs(
        (
            CounterfactualRepairCandidate("broad", frozenset({"a", "b"}), True),
            CounterfactualRepairCandidate("minimal", frozenset({"a"}), True),
            CounterfactualRepairCandidate("failed", frozenset({"c"}), False),
        )
    )
    assert result.repair_ids == ("minimal",)
    assert result.cardinality == 1
    assert not hasattr(result, "granted")


def test_protected_minimal_repair_can_reject_a_target_flip() -> None:
    candidates = (
        CounterfactualRepairCandidate("unsafe", frozenset({"a"}), True, False),
        CounterfactualRepairCandidate("safe", frozenset({"b"}), True, True),
    )
    raw = inclusion_minimal_successful_repairs(candidates)
    protected = inclusion_minimal_successful_repairs(
        candidates,
        require_protected_ok=True,
    )
    assert raw.repair_ids == ("safe", "unsafe")
    assert protected.repair_ids == ("safe",)


def test_recovery_admission_and_dependency_rollback_are_separate_layers() -> None:
    action = RecoveryAction(
        action_id="expand",
        action_type="EXPAND_SEARCH_UNIVERSE",
        target="W.ACTIVE_DOMAINS",
        admissible_diagnoses=frozenset({"SEARCH_UNIVERSE"}),
    )
    assert admit_recovery_action("SEARCH_UNIVERSE", action).admitted is True
    assert admit_recovery_action("EVIDENCE", action).admitted is False

    nodes = (
        DependencyNode("root", frozenset({"W.ACTIVE_DOMAINS"})),
        DependencyNode("child", frozenset({"DERIVED"}), ("root",)),
        DependencyNode("other", frozenset({"UNRELATED"})),
    )
    assert dependency_impact_closure(nodes, ("W.ACTIVE_DOMAINS",)) == (
        "root",
        "child",
    )


def test_missing_verification_relation_generates_obligation() -> None:
    rows = (
        VerificationObligation("claim:a", "verify:a"),
        VerificationObligation("claim:b", None),
    )
    assert missing_verification_obligations(rows) == ("claim:b",)


def test_certificate_bound_execution_fails_closed_on_scope_epoch_and_drift() -> None:
    certificate = MutationCertificate(
        certificate_id="c1",
        action_id="rewrite",
        scope=frozenset({"W.REPRESENTATIONS"}),
        issued_epoch=4,
        revocation_epoch=7,
        state_digest="abc",
    )
    good = ExecutionRequest("rewrite", "W.REPRESENTATIONS", 5, "abc")
    assert enforce_certificate(certificate, good).admitted is True
    assert enforce_certificate(
        certificate,
        ExecutionRequest("rewrite", "M.METHOD", 5, "abc"),
    ).reason == "scope_mismatch"
    assert enforce_certificate(
        certificate,
        ExecutionRequest("rewrite", "W.REPRESENTATIONS", 7, "abc"),
    ).reason == "revoked_or_expired"
    assert enforce_certificate(
        certificate,
        ExecutionRequest("rewrite", "W.REPRESENTATIONS", 5, "changed"),
    ).reason == "live_state_drift"
