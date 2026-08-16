from dataclasses import replace
import inspect

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from orion.kernel.assurance import (
    AppraisalSignatureStatus,
    AppraisalVerdict,
    VerifierAppraisal,
    appraisal_signing_payload,
    transition_subject_hash,
    verify_appraisal_signature,
)
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


def _plan():
    projection = ProgramProjection(
        PROJECTION_SCHEMA_VERSION,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        (MechanicCell("SEARCH.QUERY.v0", "query", "scope", provisional_dimensions=(MechanicDimension.INPUTS,)),),
    )
    record = AnswerRecord(
        "r1",
        "SEARCH.QUERY.v0",
        MechanicDimension.INPUTS,
        "proposal:test",
        payload=(("input_ids", ("problem",)),),
    )
    expectation = LedgerExpectation(None, projection_hash(projection), "a" * 64, "b" * 64)
    return plan_answer_transition(
        projection,
        record,
        expectation=expectation,
        evidence_snapshot_hash="c" * 64,
    )


def _signed(verdict=AppraisalVerdict.PASS):
    plan = _plan()
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
    unsigned = VerifierAppraisal(
        appraisal_id="appraisal:1",
        subject_hash=transition_subject_hash(plan),
        transition_id=plan.transition_id,
        evidence_snapshot_hash=plan.evidence_snapshot_hash,
        registration_commitment="d" * 64,
        verifier_id="protected-verifier-v1",
        evaluation_epoch_id="epoch:frozen",
        verdict=verdict,
        reason_codes=("registered_test_pass",),
        signature="00" * 64,
    )
    signature = private.sign(appraisal_signing_payload(unsigned)).hex()
    return replace(unsigned, signature=signature), public, plan


def test_all_four_appraisal_verdicts_are_distinct_and_constructible():
    assert {item.value for item in AppraisalVerdict} == {"PASS", "FAIL", "BLOCKED", "CANNOT_CHECK"}
    for verdict in AppraisalVerdict:
        appraisal, public, _ = _signed(verdict)
        report = verify_appraisal_signature(appraisal, registered_public_key_hex=public)
        assert report.status is AppraisalSignatureStatus.VALID
        assert not appraisal.grants_transition_authority
        assert not appraisal.grants_scientific_authority
        assert not report.authorizes_transition


def test_signature_binds_verdict_subject_transition_and_registration():
    appraisal, public, _ = _signed()
    assert verify_appraisal_signature(appraisal, registered_public_key_hex=public).status is AppraisalSignatureStatus.VALID
    for changed in (
        replace(appraisal, verdict=AppraisalVerdict.FAIL),
        replace(appraisal, subject_hash="e" * 64),
        replace(appraisal, transition_id="e" * 64),
        replace(appraisal, registration_commitment="e" * 64),
        replace(appraisal, reason_codes=("changed",)),
    ):
        assert verify_appraisal_signature(changed, registered_public_key_hex=public).status is AppraisalSignatureStatus.INVALID


def test_wrong_registered_key_is_invalid():
    appraisal, _, _ = _signed()
    other = Ed25519PrivateKey.generate().public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()
    assert verify_appraisal_signature(appraisal, registered_public_key_hex=other).status is AppraisalSignatureStatus.INVALID


def test_malformed_registered_key_is_cannot_check():
    appraisal, _, _ = _signed()
    report = verify_appraisal_signature(appraisal, registered_public_key_hex="bad")
    assert report.status is AppraisalSignatureStatus.CANNOT_CHECK


def test_subject_hash_changes_with_candidate_transition():
    plan = _plan()
    changed = replace(plan, evidence_snapshot_hash="f" * 64)
    assert transition_subject_hash(plan) != transition_subject_hash(changed)


def test_production_appraisal_module_has_no_private_key_or_evaluator_injection_api():
    import orion.kernel.assurance as assurance

    names = set(vars(assurance))
    assert "Ed25519PrivateKey" not in names
    assert "sign_appraisal" not in names
    for target in (transition_subject_hash, appraisal_signing_payload, verify_appraisal_signature):
        parameters = set(inspect.signature(target).parameters)
        assert {"private_key", "signing_key", "evaluator", "evaluate", "registry"}.isdisjoint(parameters)
