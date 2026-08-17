"""Hostile tests for the staged self-improvement gate.

Every one of issue #141's seven requirements gets the test that shows the gate
REFUSES, not only the one where it passes. The passing case exists once, as the
baseline the refusals are perturbations of.
"""

from __future__ import annotations

import dataclasses
import hashlib
import re

import pytest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from orion.kernel.hard_gates import HardGateObservation, HardGateState
from orion.self_orion import staged_gate
from orion.self_orion.change_control import ChangeControlVerdict
from orion.self_orion.staged_gate import (
    APPRAISABLE_STAGES,
    META_OVERFIT_REASON,
    RESERVED_STAGES,
    STAGE_ORDER,
    AppraisalCannotAuthorize,
    CommitAuthorization,
    ExternalAuthorityRegistration,
    ExternalAuthorityRegistry,
    FreshTransferCase,
    FreshTransferEvidence,
    HostAuthorizationAttestation,
    ProtectedAppraisal,
    ReplayEvidence,
    SelfImprovementCandidate,
    SelfImprovementStage,
    StagedChangeRequest,
    StagedGateReceipt,
    StagedGateReport,
    StageOutcome,
    StageOutOfOrder,
    StageRefusal,
    TransferOutcome,
    appraise_stage,
    appraise_staged_self_improvement,
    authorize_commit,
    mint_host_authorization,
    staged_gate_contract,
)

BASE = "1" * 64
CANDIDATE_REVISION = "2" * 64
PATCH = "3" * 64
FAILURE = "4" * 64
EVALUATOR = "5" * 64
SPLIT = "6" * 64
PRODUCER = "7" * 64
VERIFIER = "8" * 64
APPRAISER = "9" * 64
HOST = "a" * 64

HOST_SEED = bytes(range(32))
SUBJECT_SEED = bytes(range(32, 64))


def _request(**overrides) -> StagedChangeRequest:
    fields = {
        "request_id": "change:1",
        "base_revision_hash": BASE,
        "observed_failure_artifact_hash": FAILURE,
        "frozen_evaluator_artifact_hash": EVALUATOR,
        "frozen_fresh_split_manifest_hash": SPLIT,
        "retained_negative_ids": ("negative:1", "negative:2"),
        "scope_path_prefixes": ("src/orion/mechanics/",),
        "declared_independent_axes": ("domain", "tool"),
        "gate_contract_frozen_at_round": 1,
    }
    fields.update(overrides)
    return StagedChangeRequest(**fields)


def _candidate(**overrides) -> SelfImprovementCandidate:
    fields = {
        "candidate_id": "candidate:1",
        "request_id": "change:1",
        "base_revision_hash": BASE,
        "candidate_revision_hash": CANDIDATE_REVISION,
        "patch_artifact_hash": PATCH,
        "touched_paths": ("src/orion/mechanics/example.py",),
        "producer_process_lineage_hash": PRODUCER,
        "created_at_round": 4,
        "development_feedback_case_ids": ("dev:1",),
    }
    fields.update(overrides)
    return SelfImprovementCandidate(**fields)


def _replay(**overrides) -> ReplayEvidence:
    fields = {
        "evidence_artifact_id": "replay:1",
        "subject_revision_hash": CANDIDATE_REVISION,
        "motivating_failure_artifact_hash": FAILURE,
        "motivating_case_outcome": TransferOutcome.IMPROVED,
        "producer_process_lineage_hash": PRODUCER,
        "verifier_process_lineage_hash": VERIFIER,
        "retained_negative_ids": ("negative:1", "negative:2", "negative:3"),
    }
    fields.update(overrides)
    return ReplayEvidence(**fields)


def _fresh(cases=None, **overrides) -> FreshTransferEvidence:
    fields = {
        "execution_receipt_id": "exec:1",
        "candidate_revision_hash": CANDIDATE_REVISION,
        "required_tests_outcome": HardGateState.PASS,
        "split_manifest_hash": SPLIT,
        "split_frozen_at_round": 2,
        "cases": cases
        or (
            FreshTransferCase("fresh:1", "domain", TransferOutcome.IMPROVED),
            FreshTransferCase("fresh:2", "tool", TransferOutcome.UNCHANGED),
        ),
    }
    fields.update(overrides)
    return FreshTransferEvidence(**fields)


def _appraisal(**overrides) -> ProtectedAppraisal:
    fields = {
        "appraisal_id": "appraisal:1",
        "appraiser_id": "protected-host",
        "appraiser_process_lineage_hash": APPRAISER,
        "subject_revision_hash": CANDIDATE_REVISION,
        "evaluator_artifact_hash": EVALUATOR,
        "evaluator_frozen_at_round": 2,
        "appraised_at_round": 6,
        "development_delta": 1.5,
        "fresh_assurance_delta": 0.5,
        "blocking_invariant_states": (
            ("no_self_merge", HardGateState.PASS),
            ("negative_history_preserved", HardGateState.PASS),
        ),
    }
    fields.update(overrides)
    return ProtectedAppraisal(**fields)


def _appraise(**overrides) -> StagedGateReport:
    fields = {
        "request": _request(),
        "candidate": _candidate(),
        "replay": _replay(),
        "fresh": _fresh(),
        "appraisal": _appraisal(),
    }
    fields.update(overrides)
    return appraise_staged_self_improvement(**fields)


def _registry(lineage: str = HOST, seed: bytes = HOST_SEED) -> ExternalAuthorityRegistry:
    key = Ed25519PrivateKey.from_private_bytes(seed).public_key()
    return ExternalAuthorityRegistry(
        (
            ExternalAuthorityRegistration(
                authority_id="external-host",
                verification_key=key.public_bytes_raw(),
                process_lineage_hash=lineage,
            ),
        )
    )


def _attestation(report, *, lineage=HOST, seed=HOST_SEED, authority_id="external-host"):
    return mint_host_authorization(
        seed,
        authority_id=authority_id,
        authority_process_lineage_hash=lineage,
        subject_revision_hash=report.candidate_revision_hash,
        report_receipt_hash=report.receipt.content_hash,
    )


# --------------------------------------------------------------------------
# baseline
# --------------------------------------------------------------------------


def test_a_fully_evidenced_candidate_reaches_the_recommendation_ceiling_and_stops() -> None:
    report = _appraise()
    assert report.verdict is ChangeControlVerdict.RECOMMEND_HOST_PROMOTION
    assert report.reasons == ()
    for stage in APPRAISABLE_STAGES:
        assert report.stage(stage).state is HardGateState.PASS
        assert report.stage(stage).evaluated
    assert not report.authorizes_commit


# --------------------------------------------------------------------------
# 1. ordering is real
# --------------------------------------------------------------------------


def test_a_later_stage_is_refused_by_name_not_silently_skipped() -> None:
    report = _appraise(candidate=_candidate(request_id="change:other"))
    assert report.stage(SelfImprovementStage.PROPOSAL).state is HardGateState.FAIL
    for stage in APPRAISABLE_STAGES[1:]:
        outcome = report.stage(stage)
        assert outcome.refusal is StageRefusal.PREDECESSOR_FAILED
        assert outcome.blocked_by is SelfImprovementStage.PROPOSAL
        assert outcome.state is HardGateState.CANNOT_CHECK
        assert outcome.reasons == ("stage_not_evaluated:blocked_by:PROPOSAL",)
        # Never evaluated, so nothing about it could have been credited.
        assert outcome.passed_gate_ids == ()
        assert not outcome.evaluated


def test_appraising_a_stage_out_of_order_raises_a_typed_refusal() -> None:
    contract = staged_gate_contract(SelfImprovementStage.SANDBOX, frozen_at_round=1)
    with pytest.raises(StageOutOfOrder) as raised:
        appraise_stage(
            SelfImprovementStage.SANDBOX,
            contract=contract,
            observations=(),
            subject_id="candidate:1",
            round_index=4,
            preceding=(),
        )
    assert raised.value.stage is SelfImprovementStage.SANDBOX
    assert raised.value.detail == "incomplete_predecessor_chain"


def test_a_stage_whose_predecessor_failed_cannot_be_appraised_at_all() -> None:
    failed = StageOutcome(SelfImprovementStage.PROPOSAL, HardGateState.FAIL)
    contract = staged_gate_contract(SelfImprovementStage.EVIDENCE, frozen_at_round=1)
    with pytest.raises(StageOutOfOrder) as raised:
        appraise_stage(
            SelfImprovementStage.EVIDENCE,
            contract=contract,
            observations=(),
            subject_id="candidate:1",
            round_index=4,
            preceding=(failed,),
        )
    assert raised.value.blocked_by is SelfImprovementStage.PROPOSAL
    assert raised.value.blocking_state is HardGateState.FAIL


def test_a_perfect_later_stage_cannot_be_credited_when_an_earlier_one_is_unresolved() -> None:
    """Undeclared scope leaves PROPOSAL unresolved; SANDBOX is flawless anyway."""

    report = _appraise(request=_request(scope_path_prefixes=()))
    assert report.stage(SelfImprovementStage.PROPOSAL).state is HardGateState.CANNOT_CHECK
    assert report.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    sandbox = report.stage(SelfImprovementStage.SANDBOX)
    assert sandbox.refusal is StageRefusal.PREDECESSOR_UNRESOLVED
    assert sandbox.passed_gate_ids == ()


def test_stage_order_is_the_programme_shape() -> None:
    assert [item.value for item in STAGE_ORDER] == [
        "PROPOSAL",
        "EVIDENCE",
        "SANDBOX",
        "APPRAISAL",
        "AUTHORIZATION",
        "COMMIT",
    ]


# --------------------------------------------------------------------------
# 2. non-compensatory across stages
# --------------------------------------------------------------------------


def test_one_failed_stage_is_not_offset_by_every_other_stage_passing() -> None:
    """PROPOSAL, EVIDENCE and SANDBOX are flawless; APPRAISAL is not."""

    report = _appraise(appraisal=_appraisal(subject_revision_hash="b" * 64))
    for stage in APPRAISABLE_STAGES[:3]:
        assert report.stage(stage).state is HardGateState.PASS
    assert report.stage(SelfImprovementStage.APPRAISAL).state is HardGateState.FAIL
    assert report.verdict is ChangeControlVerdict.REJECT
    assert not report.authorizes_commit


def test_a_regression_in_one_fresh_case_is_not_averaged_away_by_many_improvements() -> None:
    cases = tuple(
        FreshTransferCase(f"fresh:{index}", "domain", TransferOutcome.IMPROVED)
        for index in range(19)
    ) + (FreshTransferCase("fresh:19", "tool", TransferOutcome.REGRESSED),)
    report = _appraise(fresh=_fresh(cases=cases))
    assert report.stage(SelfImprovementStage.SANDBOX).state is HardGateState.FAIL
    assert "NO_FRESH_TRANSFER_HARM" in report.stage(SelfImprovementStage.SANDBOX).failed_gate_ids
    assert report.verdict is not ChangeControlVerdict.RECOMMEND_HOST_PROMOTION


def _numeric_atoms(annotation: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", annotation)).intersection(
        {"int", "float", "complex", "Decimal", "Fraction"}
    )


def _reachable_dataclasses(root: type) -> set[type]:
    seen: set[type] = set()
    pending = [root]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        for field in dataclasses.fields(current):
            for atom in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", field.type):
                candidate = getattr(staged_gate, atom, None)
                if isinstance(candidate, type) and dataclasses.is_dataclass(candidate):
                    pending.append(candidate)
    return seen


def test_the_report_carries_no_aggregate_to_trade_against() -> None:
    """No total, count or ratio anywhere a caller reads a verdict from.

    Walks the whole dataclass graph reachable from the report, not just its own
    fields: a count parked on StageOutcome or StagedGateReceipt would be exactly
    as tradeable. `from __future__ import annotations` makes field.type a string.
    """

    offenders: list[str] = []
    for cls in _reachable_dataclasses(StagedGateReport):
        for field in dataclasses.fields(cls):
            if _numeric_atoms(field.type):
                offenders.append(f"{cls.__name__}.{field.name}: {field.type}")
    assert offenders == []
    assert {cls.__name__ for cls in _reachable_dataclasses(StagedGateReport)} >= {
        "StagedGateReport",
        "StageOutcome",
        "StagedGateReceipt",
    }


def test_no_live_report_attribute_is_a_number() -> None:
    """The field-annotation test cannot see properties; this one can."""

    report = _appraise()
    numeric: list[str] = []
    for name in dir(report):
        if name.startswith("_"):
            continue
        value = getattr(report, name)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            numeric.append(name)
    assert numeric == []


def test_the_commit_authorization_carries_no_aggregate_either() -> None:
    offenders = [
        field.name
        for field in dataclasses.fields(CommitAuthorization)
        if _numeric_atoms(field.type)
    ]
    assert offenders == []


# --------------------------------------------------------------------------
# 3. appraisal is not authorization
# --------------------------------------------------------------------------


@pytest.mark.parametrize("stage", RESERVED_STAGES)
def test_an_appraiser_may_not_appraise_a_reserved_stage(stage) -> None:
    contract = staged_gate_contract(stage, frozen_at_round=1)
    with pytest.raises(AppraisalCannotAuthorize) as raised:
        appraise_stage(
            stage,
            contract=contract,
            observations=(),
            subject_id="candidate:1",
            round_index=4,
            preceding=tuple(
                StageOutcome(item, HardGateState.PASS)
                for item in STAGE_ORDER[: STAGE_ORDER.index(stage)]
            ),
        )
    assert raised.value.stage is stage


def test_the_ladder_reserves_authorization_and_commit_to_external_custody() -> None:
    report = _appraise()
    for stage in RESERVED_STAGES:
        outcome = report.stage(stage)
        assert outcome.refusal is StageRefusal.RESERVED_TO_EXTERNAL_AUTHORITY
        assert outcome.state is HardGateState.CANNOT_CHECK
        assert outcome.passed_gate_ids == ()


def test_the_appraiser_cannot_also_be_the_authority() -> None:
    report = _appraise()
    assert report.verdict is ChangeControlVerdict.RECOMMEND_HOST_PROMOTION
    attestation = _attestation(report, lineage=APPRAISER)
    decision = authorize_commit(report, attestation, registry=_registry(lineage=APPRAISER))
    assert not decision.host_may_commit
    assert "gate_failed:AUTHORITY_IS_NOT_THE_APPRAISER" in decision.stage.reasons


def test_an_unregistered_authority_cannot_authorize() -> None:
    report = _appraise()
    attestation = _attestation(report, authority_id="self-appointed-host")
    decision = authorize_commit(report, attestation, registry=_registry())
    assert not decision.host_may_commit
    assert "gate_failed:AUTHORITY_IS_REGISTERED" in decision.stage.reasons
    # Unverifiable rather than verified-false: nothing to check the signature against.
    assert "gate_cannot_check:ATTESTATION_SIGNATURE_VERIFIES" in decision.stage.reasons


def test_a_forged_signature_cannot_authorize() -> None:
    report = _appraise()
    genuine = _attestation(report)
    forged = HostAuthorizationAttestation(
        authority_id=genuine.authority_id,
        authority_process_lineage_hash=genuine.authority_process_lineage_hash,
        subject_revision_hash=genuine.subject_revision_hash,
        report_receipt_hash=genuine.report_receipt_hash,
        signature="0" * 128,
    )
    decision = authorize_commit(report, forged, registry=_registry())
    assert not decision.host_may_commit
    assert "gate_failed:ATTESTATION_SIGNATURE_VERIFIES" in decision.stage.reasons


def test_a_registered_host_authorizes_only_the_appraisal_it_signed() -> None:
    report = _appraise()
    other = _appraise(candidate=_candidate(candidate_revision_hash="c" * 64))
    attestation = _attestation(other)
    decision = authorize_commit(report, attestation, registry=_registry())
    assert not decision.host_may_commit
    assert "gate_failed:ATTESTATION_BINDS_THIS_APPRAISAL" in decision.stage.reasons


def test_a_valid_external_host_authorization_is_reported_but_never_performed() -> None:
    report = _appraise()
    decision = authorize_commit(report, _attestation(report), registry=_registry())
    assert decision.host_may_commit
    assert decision.stage.state is HardGateState.PASS
    # The gate reports the host's decision; the report still authorizes nothing.
    assert not report.authorizes_commit
    assert report.stage(SelfImprovementStage.COMMIT).state is HardGateState.CANNOT_CHECK


def test_a_blocked_appraisal_cannot_be_authorized_even_by_a_genuine_host() -> None:
    report = _appraise(replay=None)
    assert report.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    decision = authorize_commit(report, _attestation(report), registry=_registry())
    assert not decision.host_may_commit
    assert "gate_failed:APPRAISAL_RECOMMENDS_HOST_PROMOTION" in decision.stage.reasons


# --------------------------------------------------------------------------
# 4. fail closed on unobserved stages
# --------------------------------------------------------------------------


def test_an_unobserved_stage_is_cannot_check_and_blocks() -> None:
    report = _appraise(fresh=None)
    sandbox = report.stage(SelfImprovementStage.SANDBOX)
    assert sandbox.state is HardGateState.CANNOT_CHECK
    assert sandbox.passed_gate_ids == ()
    assert set(sandbox.unresolved_gate_ids) == {
        item.gate_id
        for item in staged_gate_contract(
            SelfImprovementStage.SANDBOX, frozen_at_round=1
        ).requirements
    }
    assert report.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    assert report.verdict is not ChangeControlVerdict.RECOMMEND_HOST_PROMOTION


def test_an_unobserved_stage_is_not_the_same_as_a_failed_one() -> None:
    unobserved = _appraise(appraisal=None)
    failed = _appraise(appraisal=_appraisal(subject_revision_hash="b" * 64))
    assert unobserved.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    assert failed.verdict is ChangeControlVerdict.REJECT
    assert unobserved.reasons == ("blocked_at_stage:APPRAISAL:CANNOT_CHECK",)


def test_an_unknown_gate_contract_chronology_blocks_at_the_first_stage() -> None:
    report = _appraise(request=_request(gate_contract_frozen_at_round=None))
    proposal = report.stage(SelfImprovementStage.PROPOSAL)
    assert proposal.state is HardGateState.CANNOT_CHECK
    assert "gate_contract_chronology_unknown" in proposal.reasons
    assert report.verdict is ChangeControlVerdict.CANDIDATE_ONLY


def test_a_fresh_case_nobody_observed_blocks_rather_than_passing() -> None:
    cases = (
        FreshTransferCase("fresh:1", "domain", TransferOutcome.IMPROVED),
        FreshTransferCase("fresh:2", "tool", TransferOutcome.NOT_OBSERVED),
    )
    report = _appraise(fresh=_fresh(cases=cases))
    sandbox = report.stage(SelfImprovementStage.SANDBOX)
    assert sandbox.state is HardGateState.CANNOT_CHECK
    assert "NO_FRESH_TRANSFER_HARM" in sandbox.unresolved_gate_ids


def test_an_undeclared_axis_set_is_unresolved_not_permissive() -> None:
    report = _appraise(request=_request(declared_independent_axes=()))
    sandbox = report.stage(SelfImprovementStage.SANDBOX)
    assert sandbox.state is HardGateState.CANNOT_CHECK
    assert "EVERY_FRESH_CASE_VARIES_A_DECLARED_AXIS" in sandbox.unresolved_gate_ids


# --------------------------------------------------------------------------
# 5. META_OVERFIT is one named verdict, not two reasons
# --------------------------------------------------------------------------


def test_replay_gain_with_fresh_harm_is_named_once_as_meta_overfit() -> None:
    cases = (
        FreshTransferCase("fresh:1", "domain", TransferOutcome.IMPROVED),
        FreshTransferCase("fresh:2", "tool", TransferOutcome.REGRESSED),
    )
    report = _appraise(fresh=_fresh(cases=cases))
    assert report.verdict is ChangeControlVerdict.META_OVERFIT
    assert report.reasons == (META_OVERFIT_REASON,)
    assert len(report.reasons) == 1


def test_development_gain_with_assurance_regression_is_named_once_as_meta_overfit() -> None:
    report = _appraise(appraisal=_appraisal(development_delta=2.0, fresh_assurance_delta=-0.25))
    assert report.verdict is ChangeControlVerdict.META_OVERFIT
    assert report.reasons == (META_OVERFIT_REASON,)


def test_meta_overfit_is_not_decomposed_into_two_independent_reasons() -> None:
    report = _appraise(appraisal=_appraisal(development_delta=2.0, fresh_assurance_delta=-0.25))
    joined = " ".join(report.reasons)
    assert "known_harm:fresh_assurance_regressed" not in report.reasons
    assert joined.count("meta_overfit") == 1
    # Two independent reasons would let a caller weigh gain against regression.
    assert len(report.reasons) == 1


def test_a_hard_harm_still_outranks_meta_overfit() -> None:
    report = _appraise(
        candidate=_candidate(
            touched_paths=("src/orion/self_orion/readiness.py",),
        ),
        appraisal=_appraisal(development_delta=2.0, fresh_assurance_delta=-0.25),
    )
    assert report.verdict is ChangeControlVerdict.REJECT
    assert report.reasons == (
        "known_harm:protected_path_touched:src/orion/self_orion/readiness.py",
    )


def test_a_regression_without_development_gain_is_a_plain_reject() -> None:
    cases = (FreshTransferCase("fresh:1", "domain", TransferOutcome.REGRESSED),)
    report = _appraise(
        replay=_replay(motivating_case_outcome=TransferOutcome.UNCHANGED),
        fresh=_fresh(cases=cases),
        appraisal=_appraisal(development_delta=-1.0, fresh_assurance_delta=-1.0),
    )
    assert report.verdict is ChangeControlVerdict.REJECT
    assert META_OVERFIT_REASON not in report.reasons


# --------------------------------------------------------------------------
# 6. nothing self-promotes
# --------------------------------------------------------------------------


def test_a_candidate_cannot_authorize_itself_even_when_every_stage_passes() -> None:
    """The whole point of requirement 6, at the exact moment it would be tempting."""

    report = _appraise()
    assert report.verdict is ChangeControlVerdict.RECOMMEND_HOST_PROMOTION
    assert all(report.stage(stage).state is HardGateState.PASS for stage in APPRAISABLE_STAGES)

    # The subject holds a key and a lineage, and registers itself as a host.
    subject_key = Ed25519PrivateKey.from_private_bytes(SUBJECT_SEED)
    self_registry = ExternalAuthorityRegistry(
        (
            ExternalAuthorityRegistration(
                authority_id="external-host",
                verification_key=subject_key.public_key().public_bytes_raw(),
                process_lineage_hash=PRODUCER,
            ),
        )
    )
    self_signed = mint_host_authorization(
        SUBJECT_SEED,
        authority_id="external-host",
        authority_process_lineage_hash=PRODUCER,
        subject_revision_hash=report.candidate_revision_hash,
        report_receipt_hash=report.receipt.content_hash,
    )
    decision = authorize_commit(report, self_signed, registry=self_registry)

    # The signature is genuine and the authority is "registered"; it still fails,
    # because the authority's process lineage is the producer's.
    assert "gate_failed:AUTHORITY_IS_NOT_THE_SUBJECT" in decision.stage.reasons
    assert not decision.host_may_commit
    assert not report.authorizes_commit


def test_the_report_never_authorizes_commit_under_any_verdict() -> None:
    for report in (
        _appraise(),
        _appraise(replay=None),
        _appraise(candidate=_candidate(request_id="change:other")),
    ):
        assert report.authorizes_commit is False


def test_the_terminal_stage_is_never_resolved_from_inside() -> None:
    report = _appraise()
    commit = report.stage(SelfImprovementStage.COMMIT)
    assert commit.state is HardGateState.CANNOT_CHECK
    assert commit.refusal is StageRefusal.RESERVED_TO_EXTERNAL_AUTHORITY


# --------------------------------------------------------------------------
# 7. deterministic, content-bound receipts
# --------------------------------------------------------------------------


def test_the_same_inputs_produce_byte_identical_receipts() -> None:
    first = _appraise()
    second = _appraise()
    assert first.receipt.payload == second.receipt.payload
    assert first.receipt.content_hash == second.receipt.content_hash
    assert first.receipt.receipt_id == second.receipt.receipt_id


def test_reordering_fresh_cases_does_not_change_the_receipt() -> None:
    cases = (
        FreshTransferCase("fresh:1", "domain", TransferOutcome.IMPROVED),
        FreshTransferCase("fresh:2", "tool", TransferOutcome.UNCHANGED),
    )
    forward = _appraise(fresh=_fresh(cases=cases))
    backward = _appraise(fresh=_fresh(cases=tuple(reversed(cases))))
    assert forward.receipt.payload == backward.receipt.payload


def test_a_different_patch_produces_a_different_receipt() -> None:
    first = _appraise()
    second = _appraise(candidate=_candidate(patch_artifact_hash="d" * 64))
    assert first.receipt.content_hash != second.receipt.content_hash
    assert first.receipt.receipt_id.startswith("staged-gate:")


def test_the_receipt_hash_is_the_hash_of_its_own_payload() -> None:
    report = _appraise()
    assert hashlib.sha256(report.receipt.payload).hexdigest() == report.receipt.content_hash


def test_a_tampered_receipt_payload_cannot_be_authorized() -> None:
    report = _appraise(replay=None)
    good = _appraise()
    # Splice the passing receipt onto the blocked report and re-point the hash.
    spliced = dataclasses.replace(report, receipt=good.receipt)
    decision = authorize_commit(spliced, _attestation(good), registry=_registry())
    assert not decision.host_may_commit
    assert "receipt_verdict_mismatch" in decision.refusals


def test_an_unreadable_receipt_is_unresolved_never_authorized() -> None:
    report = _appraise()
    attestation = _attestation(report)
    broken = dataclasses.replace(
        report,
        receipt=StagedGateReceipt(
            receipt_id=report.receipt.receipt_id,
            content_hash=report.receipt.content_hash,
            payload=b"not json",
        ),
    )
    decision = authorize_commit(broken, attestation, registry=_registry())
    assert not decision.host_may_commit
    assert decision.refusals == ("receipt_payload_unreadable",)
    assert decision.stage.state is HardGateState.CANNOT_CHECK


def test_a_rewritten_verdict_inside_the_payload_breaks_the_host_signature() -> None:
    blocked = _appraise(replay=None)
    attestation = _attestation(blocked)
    rewritten = blocked.receipt.payload.replace(
        b'"verdict":"CANDIDATE_ONLY"', b'"verdict":"RECOMMEND_HOST_PROMOTION"'
    )
    assert rewritten != blocked.receipt.payload
    forged = StagedGateReceipt(
        receipt_id=blocked.receipt.receipt_id,
        content_hash=blocked.receipt.content_hash,
        payload=rewritten,
    )
    decision = authorize_commit(
        dataclasses.replace(
            blocked,
            receipt=forged,
            verdict=ChangeControlVerdict.RECOMMEND_HOST_PROMOTION,
        ),
        attestation,
        registry=_registry(),
    )
    assert not decision.host_may_commit
    assert "receipt_payload_tampered" in decision.refusals
    assert "gate_failed:ATTESTATION_BINDS_THIS_APPRAISAL" in decision.stage.reasons


# --------------------------------------------------------------------------
# known harm dominates a missing earlier stage (#141 deterministic precedence)
# --------------------------------------------------------------------------


def test_a_known_later_harm_dominates_an_unobserved_earlier_stage() -> None:
    """Leaving PROPOSAL unresolved must not launder a supplied fresh regression."""

    cases = (FreshTransferCase("fresh:1", "domain", TransferOutcome.REGRESSED),)
    report = _appraise(
        request=_request(scope_path_prefixes=()),
        replay=None,
        fresh=_fresh(cases=cases),
        appraisal=None,
    )
    assert report.stage(SelfImprovementStage.PROPOSAL).state is HardGateState.CANNOT_CHECK
    assert report.stage(SelfImprovementStage.SANDBOX).passed_gate_ids == ()
    assert report.verdict is ChangeControlVerdict.REJECT
    assert "known_harm:fresh_transfer_regression:fresh:1" in report.reasons


def test_supplied_later_evidence_can_only_lower_the_verdict_never_raise_it() -> None:
    blocked = _request(scope_path_prefixes=())
    bare = appraise_staged_self_improvement(request=blocked, candidate=_candidate())
    perfect = _appraise(request=blocked)
    harmful = _appraise(
        request=blocked,
        replay=None,
        fresh=_fresh(cases=(FreshTransferCase("f", "domain", TransferOutcome.REGRESSED),)),
        appraisal=None,
    )
    assert bare.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    assert perfect.verdict is ChangeControlVerdict.CANDIDATE_ONLY
    assert harmful.verdict is ChangeControlVerdict.REJECT


# --------------------------------------------------------------------------
# hostile: laundering, custody, chronology, archive deletion
# --------------------------------------------------------------------------


def test_an_observation_minted_under_another_stages_contract_fails_integrity() -> None:
    """Distinct per-stage fingerprints stop cross-stage evidence reuse."""

    proposal = staged_gate_contract(SelfImprovementStage.PROPOSAL, frozen_at_round=1)
    evidence = staged_gate_contract(SelfImprovementStage.EVIDENCE, frozen_at_round=1)
    assert proposal.fingerprint != evidence.fingerprint
    smuggled = HardGateObservation(
        gate_id="MOTIVATING_FAILURE_IS_REPAIRED",
        subject_id="candidate:1",
        state=HardGateState.PASS,
        contract_fingerprint=proposal.fingerprint,
        evidence_ids=("replay:1",),
    )
    outcome = appraise_stage(
        SelfImprovementStage.EVIDENCE,
        contract=evidence,
        observations=(smuggled,),
        subject_id="candidate:1",
        round_index=4,
        preceding=(StageOutcome(SelfImprovementStage.PROPOSAL, HardGateState.PASS),),
    )
    assert outcome.state is HardGateState.FAIL
    assert outcome.failed_gate_ids == ("CONTRACT_INTEGRITY",)


def test_duplicate_fresh_case_ids_are_refused_at_construction() -> None:
    with pytest.raises(ValueError):
        _fresh(
            cases=(
                FreshTransferCase("fresh:1", "domain", TransferOutcome.IMPROVED),
                FreshTransferCase("fresh:1", "domain", TransferOutcome.REGRESSED),
            )
        )


def test_deleting_retained_negative_history_rejects_despite_a_clean_replay() -> None:
    report = _appraise(replay=_replay(retained_negative_ids=("negative:1",)))
    evidence = report.stage(SelfImprovementStage.EVIDENCE)
    assert evidence.state is HardGateState.FAIL
    assert "NEGATIVE_HISTORY_IS_RETAINED" in evidence.failed_gate_ids
    assert report.verdict is ChangeControlVerdict.REJECT
    assert "known_harm:negative_history_deleted:negative:2" in report.reasons


def test_a_fresh_case_already_used_as_candidate_feedback_is_not_fresh() -> None:
    cases = (
        FreshTransferCase("dev:1", "domain", TransferOutcome.IMPROVED),
        FreshTransferCase("fresh:2", "tool", TransferOutcome.UNCHANGED),
    )
    report = _appraise(fresh=_fresh(cases=cases))
    sandbox = report.stage(SelfImprovementStage.SANDBOX)
    assert sandbox.state is HardGateState.FAIL
    assert "FRESH_SPLIT_WAS_NOT_CANDIDATE_FEEDBACK" in sandbox.failed_gate_ids


def test_a_split_that_is_not_the_frozen_split_fails_custody() -> None:
    report = _appraise(fresh=_fresh(split_manifest_hash="e" * 64))
    assert "FRESH_SPLIT_IS_THE_FROZEN_SPLIT" in report.stage(
        SelfImprovementStage.SANDBOX
    ).failed_gate_ids


def test_an_evaluator_that_is_not_the_frozen_evaluator_fails_custody() -> None:
    report = _appraise(appraisal=_appraisal(evaluator_artifact_hash="f" * 64))
    assert "EVALUATOR_IS_THE_FROZEN_EVALUATOR" in report.stage(
        SelfImprovementStage.APPRAISAL
    ).failed_gate_ids


def test_a_self_appraised_candidate_fails_the_protected_stage() -> None:
    report = _appraise(appraisal=_appraisal(appraiser_process_lineage_hash=PRODUCER))
    assert "APPRAISER_IS_NOT_THE_SUBJECT" in report.stage(
        SelfImprovementStage.APPRAISAL
    ).failed_gate_ids
    assert report.verdict is ChangeControlVerdict.REJECT


def test_self_verified_replay_evidence_fails() -> None:
    report = _appraise(replay=_replay(verifier_process_lineage_hash=PRODUCER))
    assert "REPLAY_EVIDENCE_IS_INDEPENDENTLY_VERIFIED" in report.stage(
        SelfImprovementStage.EVIDENCE
    ).failed_gate_ids


def test_an_inflated_candidate_round_trips_the_appraisal_upper_bound() -> None:
    """created_at_round is sandwiched between two rounds the candidate does not set.

    Inflating it past the fresh split and evaluator freeze rounds makes those
    checks trivially true, and then fails against the appraisal round set by a
    lineage-distinct appraiser.
    """

    report = _appraise(
        candidate=_candidate(created_at_round=999),
        fresh=_fresh(split_frozen_at_round=900),
        appraisal=_appraisal(evaluator_frozen_at_round=900),
    )
    # The fixture keeps fresh_assurance_delta positive, so no known harm fires:
    # the REJECT below can only be coming from the failed chronology gate.
    appraisal = report.stage(SelfImprovementStage.APPRAISAL)
    assert "known_harm:fresh_assurance_regressed" not in report.reasons
    assert "FRESH_SPLIT_PREDATES_THE_CANDIDATE" in report.stage(
        SelfImprovementStage.SANDBOX
    ).passed_gate_ids
    assert "EVALUATOR_PREDATES_THE_CANDIDATE" in appraisal.passed_gate_ids
    assert "CANDIDATE_PREDATES_ITS_APPRAISAL" in appraisal.failed_gate_ids
    assert report.verdict is ChangeControlVerdict.REJECT


def test_a_gate_contract_frozen_after_the_candidate_fails_integrity() -> None:
    report = _appraise(request=_request(gate_contract_frozen_at_round=9))
    proposal = report.stage(SelfImprovementStage.PROPOSAL)
    assert proposal.state is HardGateState.FAIL
    assert proposal.failed_gate_ids == ("CONTRACT_INTEGRITY",)


def test_a_candidate_that_changes_nothing_is_refused() -> None:
    report = _appraise(candidate=_candidate(candidate_revision_hash=BASE))
    assert "PROPOSAL_CHANGES_THE_INCUMBENT" in report.stage(
        SelfImprovementStage.PROPOSAL
    ).failed_gate_ids


def test_a_candidate_outside_its_declared_scope_is_refused() -> None:
    report = _appraise(candidate=_candidate(touched_paths=("src/orion/kernel/hard_gates.py",)))
    assert "PROPOSAL_STAYS_INSIDE_DECLARED_SCOPE" in report.stage(
        SelfImprovementStage.PROPOSAL
    ).failed_gate_ids


def test_an_unrepaired_motivating_failure_is_refused() -> None:
    report = _appraise(replay=_replay(motivating_case_outcome=TransferOutcome.UNCHANGED))
    assert "MOTIVATING_FAILURE_IS_REPAIRED" in report.stage(
        SelfImprovementStage.EVIDENCE
    ).failed_gate_ids


def test_replay_evidence_about_a_different_failure_is_refused() -> None:
    report = _appraise(replay=_replay(motivating_failure_artifact_hash="b" * 64))
    assert "REPLAY_EVIDENCE_BINDS_THE_OBSERVED_FAILURE" in report.stage(
        SelfImprovementStage.EVIDENCE
    ).failed_gate_ids


def test_a_failed_protected_invariant_rejects() -> None:
    report = _appraise(
        appraisal=_appraisal(
            blocking_invariant_states=(
                ("no_self_merge", HardGateState.FAIL),
                ("negative_history_preserved", HardGateState.PASS),
            )
        )
    )
    assert report.verdict is ChangeControlVerdict.REJECT
    assert "known_harm:protected_invariant_failed:no_self_merge" in report.reasons
