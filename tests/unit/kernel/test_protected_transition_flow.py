from dataclasses import replace

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
from orion.kernel.authorization import ProtectedAuthorizationSigner
from orion.kernel.evidence import HostEvidenceSnapshot
from orion.kernel.host import ProtectedHostAuthorizationService, ProtectedHostManifest
from orion.kernel.protected_flow import ProtectedTransitionCoordinator
from orion.kernel.store import LedgerStore, StaleTransitionExpectation
from orion.kernel.support import DependencyStatus, DependencyStatusEvent, SupportSet
from orion.kernel.transition import (
    PROJECTION_SCHEMA_VERSION,
    REDUCER_VERSION,
    WORKFLOW_VERSION,
    ProgramProjection,
    projection_hash,
)
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension


def _public(private):
    return private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()


class _Signer(ProtectedAuthorizationSigner):
    def __init__(self, private):
        self.private = private

    @property
    def registration_id(self):
        return "auth-key:v1"

    def sign(self, payload: bytes):
        return self.private.sign(payload).hex()


class _Verifier:
    def __init__(self, private, registration, verdict=AppraisalVerdict.PASS):
        self.private = private
        self.registration = registration
        self.verdict = verdict
        self.calls = 0

    def appraise(self, *, plan, evidence_snapshot):
        self.calls += 1
        assert evidence_snapshot.snapshot_id == plan.evidence_snapshot_hash
        unsigned = VerifierAppraisal(
            f"appraisal:{self.calls}",
            transition_subject_hash(plan),
            plan.transition_id,
            plan.evidence_snapshot_hash,
            self.registration.commitment,
            self.registration.registration_id,
            self.registration.epoch_id,
            self.verdict,
            ("protected verifier observation",),
            "00" * 64,
        )
        return replace(
            unsigned,
            signature=self.private.sign(appraisal_signing_payload(unsigned)).hex(),
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


def _coordinator(tmp_path, *, verdict=AppraisalVerdict.PASS, authority_status=AuthorityObjectStatus.LIVE):
    evaluator_private = Ed25519PrivateKey.generate()
    auth_private = Ed25519PrivateKey.generate()
    registrations = (
        AuthorityRegistration("evaluator:v1", AuthorityObjectKind.EVALUATOR, "1" * 64, "epoch:1", "2" * 64, _public(evaluator_private)),
        AuthorityRegistration("policy:v1", AuthorityObjectKind.POLICY, "3" * 64, "epoch:1", "4" * 64),
        AuthorityRegistration("auth-key:v1", AuthorityObjectKind.KEY, "5" * 64, "epoch:1", "6" * 64, _public(auth_private)),
        AuthorityRegistration("root:v1", AuthorityObjectKind.TRUST_ROOT, "7" * 64, "epoch:1", "8" * 64),
    )
    history = tuple(
        AuthorityStatusEvent(
            f"status:{item.registration_id}",
            item.registration_id,
            authority_status if item.registration_id == "policy:v1" else AuthorityObjectStatus.LIVE,
            1,
            "frozen host status",
        )
        for item in registrations
    )
    authority = AuthorityState(registrations, history, 1)
    support = SupportState(
        (SupportSet("primary", ("dep:evidence",)),),
        (DependencyStatusEvent("dep:1", "dep:evidence", DependencyStatus.LIVE, 1, "live"),),
        1,
    )
    manifest = ProtectedHostManifest(
        "host:v1",
        "evaluator:v1",
        "policy:v1",
        "auth-key:v1",
        "root:v1",
        "9" * 64,
    )
    host = ProtectedHostAuthorizationService(
        manifest=manifest,
        authority_state=authority,
        support_state=support,
        signer=_Signer(auth_private),
    )
    evaluator = authority.registration("evaluator:v1")
    assert evaluator is not None
    verifier = _Verifier(evaluator_private, evaluator, verdict=verdict)
    store = LedgerStore(tmp_path)
    return ProtectedTransitionCoordinator(store=store, host=host, verifier=verifier), host, store, verifier


def _snapshot(host):
    return HostEvidenceSnapshot(
        root_configuration_hash="a" * 64,
        manifest_hash="b" * 64,
        captured_at_authority_revision=host.authority_revision,
        captured_at_support_revision=host.support_revision,
        required_obligation_ids=(),
        records=(),
    )


def test_positive_control_runs_proposal_snapshot_plan_appraisal_authorization_commit(tmp_path):
    coordinator, host, store, verifier = _coordinator(tmp_path)
    projection = _projection()
    result = coordinator.commit_answer(
        projection=projection,
        record=_record(),
        evidence_snapshot=_snapshot(host),
    )
    assert verifier.calls == 1
    assert result.state_changed
    assert result.transaction.commits_state_change
    assert result.committed_projection.active_record_ids == ("r1",)
    assert result.ledger_entry.payload["transaction_id"] == result.transaction.transaction_id
    assert len(store.entries()) == 1
    assert not result.self_authorized


def test_fail_blocked_and_cannot_check_are_committed_without_state_change(tmp_path):
    for index, verdict in enumerate(
        (AppraisalVerdict.FAIL, AppraisalVerdict.BLOCKED, AppraisalVerdict.CANNOT_CHECK)
    ):
        root = tmp_path / str(index)
        coordinator, host, store, _ = _coordinator(root, verdict=verdict)
        projection = _projection()
        result = coordinator.commit_answer(
            projection=projection,
            record=_record(),
            evidence_snapshot=_snapshot(host),
        )
        assert not result.state_changed
        assert result.committed_projection == projection
        assert result.transaction.authorization is None
        assert len(store.entries()) == 1


def test_stale_or_revoked_host_state_never_changes_research_projection(tmp_path):
    coordinator, host, store, _ = _coordinator(
        tmp_path, authority_status=AuthorityObjectStatus.REVOKED
    )
    projection = _projection()
    result = coordinator.commit_answer(
        projection=projection,
        record=_record(),
        evidence_snapshot=_snapshot(host),
    )
    assert not result.state_changed
    assert result.committed_projection == projection
    assert store.protected_expectation().research_state_hash == projection_hash(projection)


def test_two_authorized_operations_consume_prior_committed_post_state(tmp_path):
    coordinator, host, store, _ = _coordinator(tmp_path)
    first = coordinator.commit_answer(
        projection=_projection(),
        record=_record("r1"),
        evidence_snapshot=_snapshot(host),
    )
    second = coordinator.commit_answer(
        projection=first.committed_projection,
        record=_record("r2", supersedes="r1"),
        evidence_snapshot=_snapshot(host),
    )
    assert first.state_changed and second.state_changed
    assert second.committed_projection.active_record_ids == ("r2",)
    assert second.transaction.plan.pre_state_hash == projection_hash(first.committed_projection)
    assert len(store.entries()) == 2


def test_stale_projection_requires_new_protected_attempt(tmp_path):
    coordinator, host, _, _ = _coordinator(tmp_path)
    projection = _projection()
    first = coordinator.commit_answer(
        projection=projection,
        record=_record("r1"),
        evidence_snapshot=_snapshot(host),
    )
    assert first.state_changed
    with pytest.raises(StaleTransitionExpectation):
        coordinator.commit_answer(
            projection=projection,
            record=_record("stale"),
            evidence_snapshot=_snapshot(host),
        )


def test_snapshot_from_wrong_authority_revision_is_rejected_before_appraisal(tmp_path):
    coordinator, host, store, verifier = _coordinator(tmp_path)
    snapshot = HostEvidenceSnapshot(
        root_configuration_hash="a" * 64,
        manifest_hash="b" * 64,
        captured_at_authority_revision="f" * 64,
        captured_at_support_revision=host.support_revision,
        required_obligation_ids=(),
        records=(),
    )
    with pytest.raises(StaleTransitionExpectation):
        coordinator.commit_answer(
            projection=_projection(),
            record=_record(),
            evidence_snapshot=snapshot,
        )
    assert verifier.calls == 0
    assert store.entries() == ()
