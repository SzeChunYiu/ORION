from dataclasses import replace
import os

import pytest
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
    ProtectedAuthorizationSigner,
    authorize_transition,
    seal_authorization,
)
from orion.kernel.evidence import HostEvidenceSnapshot
from orion.kernel.store import (
    EntryKind,
    LedgerStore,
    LegacyLedgerRequiresMigration,
    StaleTransitionExpectation,
    TransactionIdConflict,
)
from orion.kernel.support import DependencyStatus, DependencyStatusEvent, SupportSet
from orion.kernel.transaction import TransitionTransaction
from orion.kernel.transition import (
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    LedgerExpectation,
    ProgramProjection,
    projection_hash,
)
from orion.kernel.transition_reducer import plan_answer_transition, reduce_transition
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension


def _public(private):
    return private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()


class _Signer(ProtectedAuthorizationSigner):
    def __init__(self, private):
        self._private = private

    @property
    def registration_id(self):
        return "auth-key:v1"

    def sign(self, payload: bytes):
        return self._private.sign(payload).hex()


def _authority(evaluator_private, auth_private, *, epoch=1):
    registrations = (
        AuthorityRegistration("evaluator:v1", AuthorityObjectKind.EVALUATOR, "1" * 64, f"epoch:{epoch}", "2" * 64, _public(evaluator_private)),
        AuthorityRegistration("policy:v1", AuthorityObjectKind.POLICY, "3" * 64, f"epoch:{epoch}", "4" * 64),
        AuthorityRegistration("auth-key:v1", AuthorityObjectKind.KEY, "5" * 64, f"epoch:{epoch}", "6" * 64, _public(auth_private)),
        AuthorityRegistration("root:v1", AuthorityObjectKind.TRUST_ROOT, "7" * 64, f"epoch:{epoch}", "8" * 64),
    )
    history = tuple(
        AuthorityStatusEvent(f"event:{epoch}:{item.registration_id}", item.registration_id, AuthorityObjectStatus.LIVE, epoch, "live")
        for item in registrations
    )
    return AuthorityState(registrations, history, epoch)


def _support(*, epoch=1, status=DependencyStatus.LIVE):
    return SupportState(
        (SupportSet("support:primary", ("dep:evidence",)),),
        (DependencyStatusEvent(f"dep:{epoch}", "dep:evidence", status, epoch, "support status"),),
        epoch,
    )


def _projection():
    return ProgramProjection(
        PROJECTION_SCHEMA_VERSION,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        (MechanicCell("SEARCH.QUERY.v0", "query", "scope", provisional_dimensions=(MechanicDimension.INPUTS,)),),
    )


def _record(record_id="r1", supersedes=""):
    return AnswerRecord(
        record_id,
        "SEARCH.QUERY.v0",
        MechanicDimension.INPUTS,
        "proposal:test",
        payload=(("input_ids", (f"input:{record_id}",)),),
        supersedes=supersedes,
    )


def _transaction(
    projection,
    *,
    expected_head=None,
    record=None,
    appraisal_verdict=AppraisalVerdict.PASS,
    authority_epoch=1,
    support_epoch=1,
):
    evaluator_private = Ed25519PrivateKey.generate()
    auth_private = Ed25519PrivateKey.generate()
    authority = _authority(evaluator_private, auth_private, epoch=authority_epoch)
    support = _support(epoch=support_epoch)
    expectation = LedgerExpectation(
        expected_head,
        projection_hash(projection),
        authority.revision,
        support.revision,
    )
    snapshot = HostEvidenceSnapshot(
        root_configuration_hash="a" * 64,
        manifest_hash="b" * 64,
        captured_at_authority_revision=authority.revision,
        captured_at_support_revision=support.revision,
        required_obligation_ids=(),
        records=(),
    )
    plan = plan_answer_transition(
        projection,
        record or _record(),
        expectation=expectation,
        evidence_snapshot_hash=snapshot.snapshot_id,
    )
    evaluator = authority.registration("evaluator:v1")
    assert evaluator is not None
    unsigned = VerifierAppraisal(
        "appraisal:1",
        transition_subject_hash(plan),
        plan.transition_id,
        plan.evidence_snapshot_hash,
        evaluator.commitment,
        evaluator.registration_id,
        evaluator.epoch_id,
        appraisal_verdict,
        ("frozen verdict",),
        "00" * 64,
    )
    appraisal = replace(
        unsigned,
        signature=evaluator_private.sign(appraisal_signing_payload(unsigned)).hex(),
    )
    context = AuthorizationContext(
        plan,
        appraisal,
        authority,
        support,
        expectation,
        "evaluator:v1",
        "policy:v1",
        "auth-key:v1",
        "root:v1",
        True,
    )
    decision = authorize_transition(context)
    authorization = (
        seal_authorization(decision, signer=_Signer(auth_private))
        if decision.authorizes_state_change
        else None
    )
    transaction = TransitionTransaction(
        snapshot,
        appraisal,
        decision,
        authorization,
        plan,
    )
    return transaction, expectation, reduce_transition(projection, plan).projection


def test_authorized_transaction_commits_one_complete_transition_and_advances_research_state(tmp_path):
    store = LedgerStore(tmp_path)
    projection = _projection()
    transaction, expectation, proposed = _transaction(projection)
    entry = store.append_transaction(transaction, expected=expectation)
    assert entry.kind is EntryKind.TRANSITION
    assert entry.payload["transaction_id"] == transaction.transaction_id
    assert len(store.entries()) == 1
    current = store.protected_expectation()
    assert current is not None
    assert current.ledger_head == entry.entry_hash
    assert current.research_state_hash == projection_hash(proposed)
    assert current.authority_revision == expectation.authority_revision
    assert current.support_revision == expectation.support_revision


def test_failed_transaction_is_recorded_but_does_not_advance_research_state(tmp_path):
    store = LedgerStore(tmp_path)
    projection = _projection()
    transaction, expectation, _ = _transaction(
        projection, appraisal_verdict=AppraisalVerdict.FAIL
    )
    entry = store.append_transaction(transaction, expected=expectation)
    assert transaction.committed_post_state_hash == projection_hash(projection)
    current = store.protected_expectation()
    assert current is not None
    assert current.ledger_head == entry.entry_hash
    assert current.research_state_hash == projection_hash(projection)


def test_retry_same_transaction_is_idempotent(tmp_path):
    store = LedgerStore(tmp_path)
    projection = _projection()
    transaction, expectation, _ = _transaction(projection)
    first = store.append_transaction(transaction, expected=expectation)
    second = store.append_transaction(transaction, expected=expectation)
    assert second == first
    assert len(store.entries(EntryKind.TRANSITION)) == 1


def test_same_transaction_id_with_changed_content_is_conflict(tmp_path):
    store = LedgerStore(tmp_path)
    projection = _projection()
    transaction, expectation, _ = _transaction(projection)
    store.append_transaction(transaction, expected=expectation)
    other, _, _ = _transaction(projection, appraisal_verdict=AppraisalVerdict.FAIL)
    object.__setattr__(other, "transaction_id", transaction.transaction_id)
    with pytest.raises(TransactionIdConflict):
        store.append_transaction(other, expected=other.plan.expectation)


def test_stale_ledger_head_is_rejected_under_transaction_lock(tmp_path):
    store = LedgerStore(tmp_path)
    projection = _projection()
    first, first_expectation, proposed = _transaction(projection)
    entry = store.append_transaction(first, expected=first_expectation)
    second, second_expectation, _ = _transaction(
        proposed,
        expected_head="f" * 64,
        record=_record("r2", supersedes="r1"),
    )
    assert second_expectation.ledger_head != entry.entry_hash
    with pytest.raises(StaleTransitionExpectation) as caught:
        store.append_transaction(second, expected=second_expectation)
    assert caught.value.coordinate == "ledger_head"


def test_stale_authority_or_support_revision_is_rejected(tmp_path):
    store = LedgerStore(tmp_path)
    projection = _projection()
    first, first_expectation, proposed = _transaction(projection)
    entry = store.append_transaction(first, expected=first_expectation)

    stale_authority, expected_authority, _ = _transaction(
        proposed,
        expected_head=entry.entry_hash,
        record=_record("r2", supersedes="r1"),
        authority_epoch=2,
    )
    with pytest.raises(StaleTransitionExpectation) as caught:
        store.append_transaction(stale_authority, expected=expected_authority)
    assert caught.value.coordinate == "authority_revision"

    stale_support, expected_support, _ = _transaction(
        proposed,
        expected_head=entry.entry_hash,
        record=_record("r2", supersedes="r1"),
        support_epoch=2,
    )
    with pytest.raises(StaleTransitionExpectation) as caught:
        store.append_transaction(stale_support, expected=expected_support)
    assert caught.value.coordinate == "support_revision"


def test_loose_legacy_rows_cannot_become_protected_genesis_implicitly(tmp_path):
    store = LedgerStore(tmp_path)
    store.append(EntryKind.ANSWER, {"legacy": True})
    projection = _projection()
    transaction, expectation, _ = _transaction(
        projection,
        expected_head=store.head().entry_hash,
    )
    with pytest.raises(LegacyLedgerRequiresMigration):
        store.append_transaction(transaction, expected=expectation)
    with pytest.raises(LegacyLedgerRequiresMigration):
        store.protected_expectation()


def test_direct_loose_transition_append_is_forbidden(tmp_path):
    store = LedgerStore(tmp_path)
    with pytest.raises(ValueError):
        store.append(EntryKind.TRANSITION, {"fake": True})


def test_crash_before_replace_leaves_old_ledger_intact(tmp_path, monkeypatch):
    store = LedgerStore(tmp_path)
    projection = _projection()
    transaction, expectation, _ = _transaction(projection)
    before = store.path.read_bytes()

    def fail_replace(*args, **kwargs):  # noqa: ANN002, ANN003
        raise OSError("simulated crash before replace")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError):
        store.append_transaction(transaction, expected=expectation)
    assert store.path.read_bytes() == before
    assert store.entries() == ()
