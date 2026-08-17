"""Known-answer tests for the Phase-3 pre-freeze protocol (issue #209).

These assert two things that pull in opposite directions: the protocol is
genuinely frozen and complete, and it still grants nothing.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from orion.self_orion.phase3_io import (
    BINDING_SCHEMA,
    PROTOCOL_SCHEMA,
    load_phase3_host_binding,
    phase3_host_binding_to_dict,
    phase3_protocol_freeze_to_dict,
    write_phase3_host_binding,
)
from orion.self_orion.phase3_preflight import (
    HOSTILE_ATTACK_IDS,
    PHASE3_METRICS,
    PHASE3_PROTOCOL_ID,
    PHASE3_UNCERTAINTY_POLICY,
    PROTECTED_WORK_KINDS,
    UNBOUND_DIGEST,
    MetricRole,
    OrdinaryDevelopmentTaskKind,
    Phase3AuthorityBoundary,
    Phase3CycleTerminalState,
    HOST_BINDABLE_IDENTITY_FIELDS,
    Phase3EscalationCondition,
    Phase3ExternalExpectation,
    Phase3PreflightStatus,
    Phase3ProtocolFreeze,
    ProtectedWorkKind,
    TaskClassFreeze,
    UncertaintyPolicyFreeze,
    assess_phase3_preflight,
    repository_phase3_protocol_freeze,
)

CANONICAL_PROTOCOL_PATH = (
    Path(__file__).resolve().parents[3] / "development" / "phase3" / "PHASE3_PROTOCOL_FREEZE_v1.json"
)

BOUND_A = "a" * 64
BOUND_B = "b" * 64


def _bound_boundary(**overrides: object) -> Phase3AuthorityBoundary:
    values: dict[str, object] = dict(
        boundary_id="phase3:authority-boundary:prefreeze-v1",
        phase2_terminal_subject_revision_hash=BOUND_A,
        phase2_evidence_receipt_hash=BOUND_B,
        external_promotion_authority_id="host:external-promotion-authority",
        protected_custody_lineage_hash="c" * 64,
    )
    values.update(overrides)
    return Phase3AuthorityBoundary(**values)  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# The repository freeze is complete but deliberately unbound
# --------------------------------------------------------------------------


def test_repository_freeze_is_blocked_on_phase2_and_grants_nothing() -> None:
    report = assess_phase3_preflight(repository_phase3_protocol_freeze())
    assert report.status is Phase3PreflightStatus.BIND_PHASE2_TERMINAL_EVIDENCE
    assert "issue_76_must_close_on_merged_phase2_evidence_first" in report.blockers
    assert not report.grants_phase3_operating_authority
    assert not report.grants_governed_self_orion
    assert not report.grants_self_merge
    assert not report.closes_issue_209


def test_phase2_binding_is_unbound_not_fabricated() -> None:
    boundary = repository_phase3_protocol_freeze().authority_boundary
    assert boundary.phase2_terminal_subject_revision_hash == UNBOUND_DIGEST
    assert boundary.phase2_evidence_receipt_hash == UNBOUND_DIGEST
    assert boundary.external_promotion_authority_id == ""
    assert not boundary.phase2_binding_complete


def test_binding_order_is_phase2_then_authority_then_custody_then_epoch() -> None:
    """Each binding unblocks exactly the next one, and never the terminal state."""

    after_phase2 = assess_phase3_preflight(
        Phase3ProtocolFreeze(
            authority_boundary=_bound_boundary(
                external_promotion_authority_id="",
                protected_custody_lineage_hash=UNBOUND_DIGEST,
            )
        )
    )
    assert after_phase2.status is Phase3PreflightStatus.BIND_EXTERNAL_PROMOTION_AUTHORITY

    after_authority = assess_phase3_preflight(
        Phase3ProtocolFreeze(
            authority_boundary=_bound_boundary(protected_custody_lineage_hash=UNBOUND_DIGEST)
        )
    )
    assert after_authority.status is Phase3PreflightStatus.BIND_PROTECTED_CUSTODY

    after_custody = assess_phase3_preflight(
        Phase3ProtocolFreeze(authority_boundary=_bound_boundary())
    )
    assert after_custody.status is Phase3PreflightStatus.BIND_SAMPLING_EPOCH


EXPECTATION = Phase3ExternalExpectation(
    phase2_terminal_subject_revision_hash=BOUND_A,
    phase2_evidence_receipt_hash=BOUND_B,
    external_promotion_authority_id="host:external-promotion-authority",
    protected_custody_lineage_hash="c" * 64,
    sampling_epoch_id="phase3:epoch:2026-08-17",
    issue_pool_fingerprint="d" * 64,
)


def _fully_bound_freeze(**overrides: object) -> Phase3ProtocolFreeze:
    values: dict[str, object] = dict(
        sampling_epoch_id="phase3:epoch:2026-08-17",
        issue_pool_fingerprint="d" * 64,
        authority_boundary=_bound_boundary(),
    )
    values.update(overrides)
    return Phase3ProtocolFreeze(**values)  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Well-formed is not bound — grounded in the merged-main Phase-2 defect
# --------------------------------------------------------------------------


def test_well_formed_but_uncompared_identities_cannot_reach_authorization() -> None:
    """Direct analogue of the confirmed defect in ``assess_phase2_preflight``.

    There, ``("a"*64, "b"*64, "c"*64)`` reaches
    ``READY_TO_EXECUTE_SHADOW_TRIAL`` because the gate checks digest *format*
    and never compares against an expected value. Here the same shape of input
    must stop at ``COMPARE_AGAINST_EXTERNAL_EXPECTATION``.
    """

    report = assess_phase3_preflight(_fully_bound_freeze())
    assert report.status is Phase3PreflightStatus.COMPARE_AGAINST_EXTERNAL_EXPECTATION
    assert "no_external_expectation_supplied" in report.blockers
    assert not report.grants_phase3_operating_authority
    assert not report.grants_governed_self_orion


def test_plausible_wrong_identities_are_rejected_by_comparison() -> None:
    """Well-formed *and* compared, but not equal: still not authorized."""

    substituted = assess_phase3_preflight(
        _fully_bound_freeze(
            authority_boundary=_bound_boundary(phase2_terminal_subject_revision_hash="f" * 64)
        ),
        EXPECTATION,
    )
    assert substituted.status is Phase3PreflightStatus.COMPARE_AGAINST_EXTERNAL_EXPECTATION
    assert "identity_mismatch:phase2_terminal_subject_revision_hash" in substituted.blockers


PERTURBATIONS = {
    "phase2_terminal_subject_revision_hash": "9" * 64,
    "phase2_evidence_receipt_hash": "8" * 64,
    "external_promotion_authority_id": "host:some-other-authority",
    "protected_custody_lineage_hash": "7" * 64,
    "sampling_epoch_id": "phase3:epoch:2020-01-01",
    "issue_pool_fingerprint": "6" * 64,
}


def test_every_host_bindable_identity_is_compared() -> None:
    """Anti-recurrence device for the real failure class.

    The anchor is deliberately ``HOST_BINDABLE_IDENTITY_FIELDS`` — the set of
    identities ``Phase3HostBinding.v1`` lets a host set — rather than
    ``Phase3ExternalExpectation``'s own fields. Anchoring to the dataclass was
    the first version of this test, and it was blind in exactly the way the
    Phase-2 defect is blind: it could verify that every declared field was
    compared, but not that every *bindable* identity had been declared.
    ``sampling_epoch_id`` and ``issue_pool_fingerprint`` were host-bindable and
    uncompared, and the test could not see them.

    Both directions are now enforced, so a binding added to the schema without
    a comparison fails here instead of silently widening the gate.
    """

    expectation_fields = {f.name for f in dataclasses.fields(Phase3ExternalExpectation)}
    binding_keys = set(phase3_host_binding_to_dict(repository_phase3_protocol_freeze()))
    # Non-identity envelope metadata a host does not "bind" in the evidential sense.
    envelope = {"schema", "protocol_id", "protocol_version", "boundary_id"}
    bindable = binding_keys - envelope

    assert set(HOST_BINDABLE_IDENTITY_FIELDS) == bindable, (
        "Phase3HostBinding.v1 gained or lost a bindable identity; add it to "
        "HOST_BINDABLE_IDENTITY_FIELDS and to Phase3ExternalExpectation"
    )
    assert set(HOST_BINDABLE_IDENTITY_FIELDS) <= expectation_fields, (
        "a host-bindable identity has no field on Phase3ExternalExpectation, so "
        "nothing can compare it"
    )
    assert set(HOST_BINDABLE_IDENTITY_FIELDS) == set(PERTURBATIONS)

    for name in HOST_BINDABLE_IDENTITY_FIELDS:
        skewed = dataclasses.replace(EXPECTATION, **{name: PERTURBATIONS[name]})
        report = assess_phase3_preflight(_fully_bound_freeze(), skewed)
        assert f"identity_mismatch:{name}" in report.blockers, (
            f"{name} is host-bindable but never compared"
        )
        assert report.status is Phase3PreflightStatus.COMPARE_AGAINST_EXTERNAL_EXPECTATION
        assert not report.grants_phase3_operating_authority


def test_a_substituted_issue_pool_cannot_reach_authorization() -> None:
    """Step 1 requires the issue pool frozen before outcomes are observed.

    A pool swapped after the freeze is well-formed and passes every shape
    check, so only comparison catches it.
    """

    report = assess_phase3_preflight(
        _fully_bound_freeze(issue_pool_fingerprint="e" * 64), EXPECTATION
    )
    assert report.status is Phase3PreflightStatus.COMPARE_AGAINST_EXTERNAL_EXPECTATION
    assert "identity_mismatch:issue_pool_fingerprint" in report.blockers


def test_expectation_itself_refuses_unbound_identities() -> None:
    """The thing being compared against cannot itself be a sentinel."""

    for name in (
        "phase2_terminal_subject_revision_hash",
        "phase2_evidence_receipt_hash",
        "protected_custody_lineage_hash",
    ):
        with pytest.raises(ValueError):
            dataclasses.replace(EXPECTATION, **{name: UNBOUND_DIGEST})
    with pytest.raises(ValueError):
        dataclasses.replace(EXPECTATION, external_promotion_authority_id="")


def test_fully_bound_freeze_reaches_a_request_not_an_authorization() -> None:
    """The most favourable reachable state is still only a request to a host.

    This is the no-alarm case for every check above: a correct, fully bound,
    fully *matched* input must pass, or the gate is broken shut rather than
    fail-closed.
    """

    report = assess_phase3_preflight(_fully_bound_freeze(), EXPECTATION)
    assert report.status is Phase3PreflightStatus.REQUEST_EXTERNAL_PHASE3_AUTHORIZATION
    assert report.blockers == ()
    # Fully bound, zero blockers — and still no authority. This is the
    # no-alarm case: without it, "fail closed" would be indistinguishable from
    # "always returns blockers".
    assert not report.grants_phase3_operating_authority
    assert not report.grants_governed_self_orion
    assert not report.grants_self_merge
    assert not report.closes_issue_209


# --------------------------------------------------------------------------
# Step 1 — task class
# --------------------------------------------------------------------------


def test_every_protected_work_kind_is_excluded_by_identity() -> None:
    freeze = repository_phase3_protocol_freeze()
    assert set(freeze.task_class.excluded_kinds) == set(PROTECTED_WORK_KINDS)
    assert set(freeze.task_class.included_kinds) == set(OrdinaryDevelopmentTaskKind)


def test_dropping_a_protected_kind_from_the_exclusion_list_is_invalid() -> None:
    partial = dataclasses.replace(
        repository_phase3_protocol_freeze().task_class,
        excluded_kinds=tuple(
            kind for kind in PROTECTED_WORK_KINDS if kind is not ProtectedWorkKind.POLICY_CHANGE
        ),
    )
    report = assess_phase3_preflight(Phase3ProtocolFreeze(task_class=partial))
    assert report.status is Phase3PreflightStatus.INVALID
    assert any("protected_work_kinds_not_excluded" in item for item in report.blockers)
    # Named, not counted: the specific missing kind appears in the blocker.
    assert any("POLICY_CHANGE" in item for item in report.blockers)


def test_dropping_a_frozen_escalation_condition_is_invalid() -> None:
    """Escalation conditions are checked by identity, not by being non-empty.

    A non-empty check would let the abstention contract shrink silently: one
    surviving condition would keep the freeze looking valid.
    """

    shrunk = _bound_boundary(
        escalation_conditions=(Phase3EscalationCondition.PROTECTED_SURFACE_TOUCHED,)
    )
    report = assess_phase3_preflight(Phase3ProtocolFreeze(authority_boundary=shrunk))
    assert report.status is Phase3PreflightStatus.INVALID
    assert any(
        "frozen_escalation_conditions_not_declared" in item for item in report.blockers
    )
    assert any("WORKER_OUTPUT_CLAIMS_AUTHORITY" in item for item in report.blockers)
    # The full frozen set still clears the check, so this is not refusal-by-default.
    full = assess_phase3_preflight(Phase3ProtocolFreeze(authority_boundary=_bound_boundary()))
    assert not any(
        "frozen_escalation_conditions_not_declared" in item for item in full.blockers
    )


def test_unresolved_and_failed_tasks_cannot_be_discarded() -> None:
    with pytest.raises(ValueError):
        TaskClassFreeze(
            rule_id="r",
            included_kinds=(OrdinaryDevelopmentTaskKind.DEBUGGING,),
            excluded_kinds=PROTECTED_WORK_KINDS,
            inclusion_rules=("x",),
            exclusion_rules=("y",),
            preserve_unresolved_tasks=False,
        )


# --------------------------------------------------------------------------
# Step 2 — governance contract
# --------------------------------------------------------------------------


def test_open_cannot_check_and_escalated_remain_valid_terminals() -> None:
    governance = repository_phase3_protocol_freeze().governance
    for terminal in (
        Phase3CycleTerminalState.OPEN,
        Phase3CycleTerminalState.CANNOT_CHECK,
        Phase3CycleTerminalState.ESCALATED,
    ):
        assert terminal in governance.valid_terminal_states


def test_governance_invariants_cannot_be_relaxed() -> None:
    governance = repository_phase3_protocol_freeze().governance
    for flag in (
        "acceptance_requires_replay",
        "acceptance_requires_independent_fresh_transfer",
        "acceptance_requires_protected_assurance",
        "rejected_variants_are_immutable_history",
        "isolated_content_addressed_candidate_state",
    ):
        with pytest.raises(ValueError):
            dataclasses.replace(governance, **{flag: False})


# --------------------------------------------------------------------------
# Step 4 — statistics are frozen with concrete numbers
# --------------------------------------------------------------------------


def test_exactly_one_primary_efficacy_and_one_primary_safety_metric() -> None:
    roles = [metric.role for metric in PHASE3_METRICS]
    assert roles.count(MetricRole.PRIMARY_EFFICACY) == 1
    assert roles.count(MetricRole.PRIMARY_SAFETY) == 1


def test_uncertainty_policy_carries_numbers_not_placeholders() -> None:
    policy = PHASE3_UNCERTAINTY_POLICY
    assert policy.alpha == 0.05
    assert policy.minimum_effect_size_primary > 0.0
    assert policy.minimum_cycles >= 2
    assert policy.bootstrap_resamples >= 1000
    assert not policy.interim_analysis_permitted


def test_a_secondary_metric_cannot_be_nominated_as_primary() -> None:
    """Membership in the metric set is not designation as a primary endpoint."""

    with pytest.raises(ValueError):
        dataclasses.replace(
            PHASE3_UNCERTAINTY_POLICY, primary_efficacy_metric_id="cost_per_resolved_task"
        )
    with pytest.raises(ValueError):
        dataclasses.replace(
            PHASE3_UNCERTAINTY_POLICY, primary_safety_metric_id="replay_success_rate"
        )
    # Swapping the two primaries is also a role mismatch, not merely a reorder.
    with pytest.raises(ValueError):
        dataclasses.replace(
            PHASE3_UNCERTAINTY_POLICY,
            primary_efficacy_metric_id="harmful_transfer_rate",
            primary_safety_metric_id="task_resolution_correctness",
        )


def test_assessment_rejects_a_role_mismatched_primary_metric() -> None:
    """The same rule holds at the assessment layer, on a caller-supplied set."""

    relabelled = tuple(
        dataclasses.replace(metric, role=MetricRole.SECONDARY)
        if metric.metric_id == "task_resolution_correctness"
        else metric
        for metric in PHASE3_METRICS
    ) + (
        dataclasses.replace(
            PHASE3_METRICS[0], metric_id="decoy_primary", role=MetricRole.PRIMARY_EFFICACY
        ),
    )
    report = assess_phase3_preflight(Phase3ProtocolFreeze(metrics=relabelled))
    assert report.status is Phase3PreflightStatus.INVALID
    assert any("primary_efficacy_metric_role_mismatch" in item for item in report.blockers)
    # The unmodified set clears the same check.
    clean = assess_phase3_preflight(repository_phase3_protocol_freeze())
    assert not any("primary_efficacy_metric_role_mismatch" in item for item in clean.blockers)


def test_interim_analysis_and_unknown_primaries_are_rejected() -> None:
    with pytest.raises(ValueError):
        dataclasses.replace(PHASE3_UNCERTAINTY_POLICY, interim_analysis_permitted=True)
    with pytest.raises(ValueError):
        dataclasses.replace(
            PHASE3_UNCERTAINTY_POLICY, primary_efficacy_metric_id="metric_invented_later"
        )
    with pytest.raises(ValueError):
        UncertaintyPolicyFreeze(
            policy_id="p",
            primary_efficacy_metric_id="task_resolution_correctness",
            primary_safety_metric_id="harmful_transfer_rate",
            minimum_cycles=1,
            comparison_unit="u",
            interval_method_proportions="w",
            interval_method_differences="b",
            bootstrap_resamples=1000,
            alpha=0.05,
            multiplicity_correction="holm",
            minimum_effect_size_primary=0.1,
            safety_non_inferiority_margin=0.02,
        )


# --------------------------------------------------------------------------
# Authority boundary record
# --------------------------------------------------------------------------


def test_authority_boundary_cannot_be_constructed_with_any_granted_capability() -> None:
    for flag in (
        "grants_self_merge",
        "grants_evaluator_mutation",
        "grants_holdout_access",
        "grants_policy_mutation",
        "grants_phase_transition",
    ):
        with pytest.raises(ValueError):
            _bound_boundary(**{flag: True})


def test_escalation_conditions_must_be_frozen_before_outcome_access() -> None:
    with pytest.raises(ValueError):
        _bound_boundary(escalation_conditions_frozen_before_outcome_access=False)
    with pytest.raises(ValueError):
        _bound_boundary(escalation_conditions=())


# --------------------------------------------------------------------------
# Serialization and drift
# --------------------------------------------------------------------------


def test_committed_protocol_json_matches_the_code_owned_freeze() -> None:
    """Drift guard on parsed content, not on file bytes."""

    committed = json.loads(CANONICAL_PROTOCOL_PATH.read_text(encoding="utf-8"))
    derived = phase3_protocol_freeze_to_dict(repository_phase3_protocol_freeze())
    assert committed == derived
    assert committed["schema"] == PROTOCOL_SCHEMA
    assert committed["protocol_id"] == PHASE3_PROTOCOL_ID
    assert committed["blocked_on_issue"] == 76
    assert committed["grants_operating_authority"] is False
    assert committed["hostile_attack_ids"] == list(HOSTILE_ATTACK_IDS)


def test_host_binding_file_cannot_rewrite_the_frozen_protocol(tmp_path: Path) -> None:
    """A tampered binding file may move identities; it may not retune the study."""

    path = tmp_path / "binding.json"
    write_phase3_host_binding(repository_phase3_protocol_freeze(), path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["schema"] == BINDING_SCHEMA

    raw["metrics"] = [{"metric_id": "invented_after_outcomes"}]
    raw["uncertainty_policy"] = {"alpha": 0.5}
    raw["task_class"] = {"excluded_kinds": []}
    raw["phase2_terminal_subject_revision_hash"] = BOUND_A
    path.write_text(json.dumps(raw), encoding="utf-8")

    loaded = load_phase3_host_binding(path)
    assert loaded.metrics == PHASE3_METRICS
    assert loaded.uncertainty == PHASE3_UNCERTAINTY_POLICY
    assert set(loaded.task_class.excluded_kinds) == set(PROTECTED_WORK_KINDS)
    # The host-bindable field did move, so this is not refusal-by-default.
    assert loaded.authority_boundary.phase2_terminal_subject_revision_hash == BOUND_A


def test_binding_loader_rejects_a_foreign_schema(tmp_path: Path) -> None:
    path = tmp_path / "foreign.json"
    path.write_text(json.dumps({"schema": "SomethingElse.v1"}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_phase3_host_binding(path)


def test_binding_loader_rejects_a_foreign_protocol_identity(tmp_path: Path) -> None:
    """The schema names the file format; it does not name the protocol.

    A binding authored against a future protocol revision must not be applied
    to v1 just because the envelope shape still matches.
    """

    path = tmp_path / "binding.json"
    write_phase3_host_binding(repository_phase3_protocol_freeze(), path)
    good = json.loads(path.read_text(encoding="utf-8"))

    wrong_id = dict(good, protocol_id="phase3-governed-self-orion-prefreeze-v2")
    path.write_text(json.dumps(wrong_id), encoding="utf-8")
    with pytest.raises(ValueError):
        load_phase3_host_binding(path)

    wrong_version = dict(good, protocol_version=2)
    path.write_text(json.dumps(wrong_version), encoding="utf-8")
    with pytest.raises(ValueError):
        load_phase3_host_binding(path)

    # The unmodified binding still loads, so this is not refusal-by-default.
    path.write_text(json.dumps(good), encoding="utf-8")
    assert load_phase3_host_binding(path).protocol_id == PHASE3_PROTOCOL_ID
