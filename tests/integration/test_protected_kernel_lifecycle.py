from dataclasses import replace

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from orion.kernel.assurance import AppraisalVerdict, VerifierAppraisal, appraisal_signing_payload, transition_subject_hash
from orion.kernel.authority_state import AuthorityObjectKind, AuthorityObjectStatus, AuthorityRegistration, AuthorityState, AuthorityStatusEvent, SupportState
from orion.kernel.authorization import ProtectedAuthorizationSigner
from orion.kernel.evidence import HostEvidenceSnapshot
from orion.kernel.host import ProtectedHostAuthorizationService, ProtectedHostManifest
from orion.kernel.protected_flow import ProtectedTransitionCoordinator
from orion.kernel.replay import replay_protected_ledger
from orion.kernel.store import LedgerStore
from orion.kernel.support import DependencyStatus, DependencyStatusEvent, SupportSet
from orion.kernel.transition import PROJECTION_SCHEMA_VERSION, REDUCER_VERSION, WORKFLOW_VERSION, ProgramProjection
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension


def _public(private):
    return private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()


class _Signer(ProtectedAuthorizationSigner):
    def __init__(self, private): self.private = private
    @property
    def registration_id(self): return "auth-key:v1"
    def sign(self, payload: bytes): return self.private.sign(payload).hex()


class _Verifier:
    def __init__(self, private, registration):
        self.private = private
        self.registration = registration
        self.calls = 0

    def appraise(self, *, plan, evidence_snapshot):
        self.calls += 1
        unsigned = VerifierAppraisal(
            f"appraisal:{self.calls}", transition_subject_hash(plan), plan.transition_id,
            evidence_snapshot.snapshot_id, self.registration.commitment,
            self.registration.registration_id, self.registration.epoch_id,
            AppraisalVerdict.PASS, ("independent protected appraisal",), "00" * 64,
        )
        return replace(unsigned, signature=self.private.sign(appraisal_signing_payload(unsigned)).hex())


def test_protected_answer_commit_replay_and_reopen_are_one_append_only_lifecycle(tmp_path):
    evaluator_private = Ed25519PrivateKey.generate()
    auth_private = Ed25519PrivateKey.generate()
    registrations = (
        AuthorityRegistration("evaluator:v1", AuthorityObjectKind.EVALUATOR, "1" * 64, "epoch:1", "2" * 64, _public(evaluator_private)),
        AuthorityRegistration("policy:v1", AuthorityObjectKind.POLICY, "3" * 64, "epoch:1", "4" * 64),
        AuthorityRegistration("auth-key:v1", AuthorityObjectKind.KEY, "5" * 64, "epoch:1", "6" * 64, _public(auth_private)),
        AuthorityRegistration("root:v1", AuthorityObjectKind.TRUST_ROOT, "7" * 64, "epoch:1", "8" * 64),
    )
    authority = AuthorityState(
        registrations,
        tuple(AuthorityStatusEvent(f"status:{item.registration_id}", item.registration_id, AuthorityObjectStatus.LIVE, 1, "frozen") for item in registrations),
        1,
    )
    support = SupportState(
        (SupportSet("support", ("dep:evidence",)),),
        (DependencyStatusEvent("dep:1", "dep:evidence", DependencyStatus.LIVE, 1, "frozen"),),
        1,
    )
    host = ProtectedHostAuthorizationService(
        manifest=ProtectedHostManifest("host", "evaluator:v1", "policy:v1", "auth-key:v1", "root:v1", "9" * 64),
        authority_state=authority,
        support_state=support,
        signer=_Signer(auth_private),
    )
    evaluator = authority.registration("evaluator:v1")
    assert evaluator is not None
    verifier = _Verifier(evaluator_private, evaluator)
    store = LedgerStore(tmp_path)
    coordinator = ProtectedTransitionCoordinator(store=store, host=host, verifier=verifier)
    seed = ProgramProjection(
        PROJECTION_SCHEMA_VERSION, WORKFLOW_VERSION, REDUCER_VERSION,
        (MechanicCell("SEARCH.QUERY.v0", "query", "scope", provisional_dimensions=(MechanicDimension.INPUTS,)),),
    )
    def snapshot():
        return HostEvidenceSnapshot(
            root_configuration_hash="a" * 64,
            manifest_hash="b" * 64,
            captured_at_authority_revision=host.authority_revision,
            captured_at_support_revision=host.support_revision,
            required_obligation_ids=(),
            records=(),
        )

    committed = coordinator.commit_answer(
        projection=seed,
        record=AnswerRecord("r1", "SEARCH.QUERY.v0", MechanicDimension.INPUTS, "proposal:integration", payload=(("input_ids", ("problem",)),)),
        evidence_snapshot=snapshot(),
    )
    assert committed.state_changed
    assert committed.committed_projection.active_record_ids == ("r1",)
    calls_after_commit = verifier.calls

    replay = replay_protected_ledger(store, seed_projection=seed)
    assert replay.projection == committed.committed_projection
    assert replay.evaluator_calls == 0
    assert verifier.calls == calls_after_commit

    reopened = coordinator.commit_reopen(
        projection=committed.committed_projection,
        mechanic_id="SEARCH.QUERY.v0",
        dimension=MechanicDimension.INPUTS,
        reason="fresh support change reopens current closure",
        evidence_snapshot=snapshot(),
    )
    assert reopened.state_changed
    assert reopened.committed_projection.active_record_ids == ()
    assert tuple(record.record_id for record in reopened.committed_projection.records) == ("r1",)
    assert len(store.entries()) == 2

    replay_after_reopen = replay_protected_ledger(store, seed_projection=seed)
    assert replay_after_reopen.projection == reopened.committed_projection
    assert tuple(record.record_id for record in replay_after_reopen.projection.records) == ("r1",)
