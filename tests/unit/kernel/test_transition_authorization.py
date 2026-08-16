from dataclasses import replace

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from orion.kernel.assurance import (
    AppraisalVerdict,
    VerifierAppraisal,
    appraisal_signing_payload,
    transition_subject_hash,
)
from orion.kernel.authority_state import (
    AuthorityObjectKind,
    AuthorityObjectStatus,
    AuthorityRegistration,
    AuthorityState,
    AuthorityStatusEvent,
    SupportState,
)
from orion.kernel.authorization import (
    AuthorizationContext,
    AuthorizationSignatureStatus,
    AuthorizationVerdict,
    authorization_signing_payload,
    authorize_transition,
    seal_authorization,
    verify_authorization_signature,
)
from orion.kernel.support import DependencyStatus, DependencyStatusEvent, SupportSet
from orion.kernel.transition import (
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    LedgerExpectation,
    ProgramProjection,
    projection_hash,
)
from orion.kernel.transition_reducer import plan_answer_transition
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension


def _raw_public(private):
    return private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()


def _registrations(evaluator_private, auth_private):
    return (
        AuthorityRegistration("evaluator:v1", AuthorityObjectKind.EVALUATOR, "1" * 64, "epoch:1", "2" * 64, _raw_public(evaluator_private)),
        AuthorityRegistration("policy:v1", AuthorityObjectKind.POLICY, "3" * 64, "epoch:1", "4" * 64),
        AuthorityRegistration("auth-key:v1", AuthorityObjectKind.KEY, "5" * 64, "epoch:1", "6" * 64, _raw_public(auth_private)),
        AuthorityRegistration("root:v1", AuthorityObjectKind.TRUST_ROOT, "7" * 64, "epoch:1", "8" * 64),
    )


def _authority(evaluator_private, auth_private, *, status_overrides=None):
    registrations = _registrations(evaluator_private, auth_private)
    overrides = status_overrides or {}
    history = tuple(
        AuthorityStatusEvent(
            f"status:{item.registration_id}",
            item.registration_id,
            overrides.get(item.registration_id, AuthorityObjectStatus.LIVE),
            1,
            "frozen host status",
        )
        for item in registrations
    )
    return AuthorityState(registrations, history, 1)


def _support(*, dependency_status=DependencyStatus.LIVE):
    return SupportState(
        (SupportSet("support:primary", ("dep:evidence",)),),
        (DependencyStatusEvent("dep:event", "dep:evidence", dependency_status, 1, "frozen support status"),),
        1,
    )


def _projection():
    return ProgramProjection(
        PROJECTION_SCHEMA_VERSION,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        (MechanicCell("SEARCH.QUERY.v0", "query", "scope", provisional_dimensions=(MechanicDimension.INPUTS,)),),
    )


def _record():
    return AnswerRecord(
        "r1", "SEARCH.QUERY.v0", MechanicDimension.INPUTS, "proposal:test",
        payload=(("input_ids", ("problem",)),),
    )


def _fixture(*, appraisal_verdict=AppraisalVerdict.PASS, status_overrides=None, dependency_status=DependencyStatus.LIVE, chronology=True):
    evaluator_private = Ed25519PrivateKey.generate()
    auth_private = Ed25519PrivateKey.generate()
    authority = _authority(evaluator_private, auth_private, status_overrides=status_overrides)
    support = _support(dependency_status=dependency_status)
    projection = _projection()
    expectation = LedgerExpectation(None, projection_hash(projection), authority.revision, support.revision)
    plan = plan_answer_transition(projection, _record(), expectation=expectation, evidence_snapshot_hash="9" * 64)
    evaluator_registration = authority.registration("evaluator:v1")
    assert evaluator_registration is not None
    unsigned = VerifierAppraisal(
        "appraisal:1",
        transition_subject_hash(plan),
        plan.transition_id,
        plan.evidence_snapshot_hash,
        evaluator_registration.commitment,
        evaluator_registration.registration_id,
        evaluator_registration.epoch_id,
        appraisal_verdict,
        ("frozen protected verdict",),
        "00" * 64,
    )
    appraisal = replace(unsigned, signature=evaluator_private.sign(appraisal_signing_payload(unsigned)).hex())
    context = AuthorizationContext(
        plan=plan,
        appraisal=appraisal,
        authority_state=authority,
        support_state=support,
        current_expectation=expectation,
        evaluator_registration_id="evaluator:v1",
        policy_registration_id="policy:v1",
        authorization_key_registration_id="auth-key:v1",
        trust_root_registration_id="root:v1",
        chronology_frozen_before_candidate=chronology,
    )
    return context, auth_private


class _Signer:
    def __init__(self, private):
        self._private = private

    @property
    def registration_id(self):
        return "auth-key:v1"

    def sign(self, payload: bytes):
        return self._private.sign(payload).hex()


def test_happy_path_requires_every_gate_and_only_then_authorizes():
    context, private = _fixture()
    decision = authorize_transition(context)
    assert decision.verdict is AuthorizationVerdict.AUTHORIZED
    assert decision.authorizes_state_change
    assert not decision.grants_scientific_authority
    receipt = seal_authorization(decision, signer=_Signer(private))
    assert receipt.authorizes_state_change
    assert verify_authorization_signature(receipt, authority_state=context.authority_state) is AuthorizationSignatureStatus.VALID


def test_appraisal_verdicts_remain_four_way_at_authorization_boundary():
    expected = {
        AppraisalVerdict.FAIL: AuthorizationVerdict.FAIL,
        AppraisalVerdict.BLOCKED: AuthorizationVerdict.BLOCKED,
        AppraisalVerdict.CANNOT_CHECK: AuthorizationVerdict.CANNOT_CHECK,
    }
    for appraisal_verdict, authorization_verdict in expected.items():
        context, _ = _fixture(appraisal_verdict=appraisal_verdict)
        assert authorize_transition(context).verdict is authorization_verdict


def test_revoked_evaluator_policy_key_or_root_is_noncompensatory_failure():
    for registration_id in ("evaluator:v1", "policy:v1", "auth-key:v1", "root:v1"):
        context, _ = _fixture(status_overrides={registration_id: AuthorityObjectStatus.REVOKED})
        decision = authorize_transition(context)
        assert decision.verdict is AuthorizationVerdict.FAIL
        assert any("revoked" in reason for reason in decision.reason_codes)


def test_stale_or_unknown_protected_registration_cannot_check():
    for status in (AuthorityObjectStatus.STALE, AuthorityObjectStatus.UNKNOWN):
        context, _ = _fixture(status_overrides={"policy:v1": status})
        decision = authorize_transition(context)
        assert decision.verdict is AuthorizationVerdict.CANNOT_CHECK


def test_invalid_appraisal_signature_fails_even_if_every_other_gate_passes():
    context, _ = _fixture()
    bad = replace(context.appraisal, signature="00" * 64)
    decision = authorize_transition(replace(context, appraisal=bad))
    assert decision.verdict is AuthorizationVerdict.FAIL
    assert "appraisal_signature_invalid" in decision.reason_codes


def test_subject_transition_evidence_or_registration_mismatch_fails():
    context, _ = _fixture()
    mutations = (
        replace(context.appraisal, subject_hash="a" * 64),
        replace(context.appraisal, transition_id="a" * 64),
        replace(context.appraisal, evidence_snapshot_hash="a" * 64),
        replace(context.appraisal, registration_commitment="a" * 64),
    )
    for appraisal in mutations:
        decision = authorize_transition(replace(context, appraisal=appraisal))
        assert decision.verdict is AuthorizationVerdict.FAIL


def test_support_failure_fails_and_unknown_support_cannot_check():
    failed, _ = _fixture(dependency_status=DependencyStatus.REVOKED)
    assert authorize_transition(failed).verdict is AuthorizationVerdict.FAIL
    unknown, _ = _fixture(dependency_status=DependencyStatus.UNKNOWN)
    assert authorize_transition(unknown).verdict is AuthorizationVerdict.CANNOT_CHECK


def test_posthoc_chronology_cannot_check():
    context, _ = _fixture(chronology=False)
    decision = authorize_transition(context)
    assert decision.verdict is AuthorizationVerdict.CANNOT_CHECK
    assert "evaluator_or_policy_chronology_not_frozen" in decision.reason_codes


def test_authority_or_support_revision_change_after_appraisal_blocks_old_authorization():
    context, _ = _fixture()
    later_authority = AuthorityState(
        context.authority_state.registrations,
        (*context.authority_state.status_history, AuthorityStatusEvent("later", "policy:v1", AuthorityObjectStatus.LIVE, 2, "new epoch observation")),
        2,
    )
    decision = authorize_transition(replace(context, authority_state=later_authority))
    assert decision.verdict is AuthorizationVerdict.FAIL
    assert "authority_revision_mismatch" in decision.reason_codes

    later_support = SupportState(
        context.support_state.support_sets,
        (*context.support_state.dependency_history, DependencyStatusEvent("later-dep", "dep:evidence", DependencyStatus.LIVE, 2, "new support observation")),
        2,
    )
    decision = authorize_transition(replace(context, support_state=later_support))
    assert decision.verdict is AuthorizationVerdict.FAIL
    assert "support_revision_mismatch" in decision.reason_codes


def test_sealed_authorization_signature_binds_decision_content():
    context, private = _fixture()
    decision = authorize_transition(context)
    receipt = seal_authorization(decision, signer=_Signer(private))
    changed = replace(receipt, reason_codes=("changed",))
    assert verify_authorization_signature(changed, authority_state=context.authority_state) is AuthorizationSignatureStatus.INVALID


def test_wrong_signer_registration_cannot_seal_authorization():
    context, private = _fixture()
    decision = authorize_transition(context)

    class WrongSigner(_Signer):
        @property
        def registration_id(self):
            return "different-key"

    import pytest

    with pytest.raises(ValueError):
        seal_authorization(decision, signer=WrongSigner(private))


def test_authorization_payload_is_stable_for_same_frozen_decision():
    context, _ = _fixture()
    decision = authorize_transition(context)
    assert authorization_signing_payload(decision) == authorization_signing_payload(decision)
