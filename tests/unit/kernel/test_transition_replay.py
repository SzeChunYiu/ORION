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
from orion.kernel.replay import ReplayFailure, ReplayStatus, replay_protected_ledger
from orion.kernel.store import EntryKind, LedgerStore, LegacyLedgerRequiresMigration, compute_entry_hash
from orion.kernel.support import DependencyStatus, DependencyStatusEvent, SupportSet
from orion.kernel.transition import PROJECTION_SCHEMA_VERSION, REDUCER_VERSION, WORKFLOW_VERSION, ProgramProjection
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension


def _public(private):
    return private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()


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
        unsigned = VerifierAppraisal(
            f"appraisal:{self.calls}",
            transition_subject_hash(plan),
            plan.transition_id,
            evidence_snapshot.snapshot_id,
            self.registration.commitment,
            self.registration.registration_id,
            self.registration.epoch_id,
            self.verdict,
            ("frozen historical appraisal",),
            "00" * 64,
        )
        return replace(unsigned, signature=self.private.sign(appraisal_signing_payload(unsigned)).hex())


def _setup(tmp_path, *, verdict=AppraisalVerdict.PASS):
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
        tuple(AuthorityStatusEvent(f"event:{item.registration_id}", item.registration_id, AuthorityObjectStatus.LIVE, 1, "live") for item in registrations),
        1,
    )
    support = SupportState(
        (SupportSet("primary", ("dep:evidence",)),),
        (DependencyStatusEvent("dep:1", "dep:evidence", DependencyStatus.LIVE, 1, "live"),),
        1,
    )
    manifest = ProtectedHostManifest("host", "evaluator:v1", "policy:v1", "auth-key:v1", "root:v1", "9" * 64)
    host = ProtectedHostAuthorizationService(manifest=manifest, authority_state=authority, support_state=support, signer=_Signer(auth_private))
    evaluator = authority.registration("evaluator:v1")
    assert evaluator is not None
    verifier = _Verifier(evaluator_private, evaluator, verdict)
    store = LedgerStore(tmp_path)
    coordinator = ProtectedTransitionCoordinator(store=store, host=host, verifier=verifier)
    return coordinator, host, store, verifier


def _projection():
    return ProgramProjection(
        PROJECTION_SCHEMA_VERSION,
        WORKFLOW_VERSION,
        REDUCER_VERSION,
        (MechanicCell("SEARCH.QUERY.v0", "query", "scope", provisional_dimensions=(MechanicDimension.INPUTS,)),),
    )


def _record(record_id="r1", supersedes=""):
    return AnswerRecord(record_id, "SEARCH.QUERY.v0", MechanicDimension.INPUTS, "proposal:test", payload=(("input_ids", (record_id,)),), supersedes=supersedes)


def _snapshot(host):
    return HostEvidenceSnapshot(
        root_configuration_hash="a" * 64,
        manifest_hash="b" * 64,
        captured_at_authority_revision=host.authority_revision,
        captured_at_support_revision=host.support_revision,
        required_obligation_ids=(),
        records=(),
    )


def test_replay_uses_only_committed_envelopes_and_calls_no_evaluator(tmp_path):
    coordinator, host, store, verifier = _setup(tmp_path)
    seed = _projection()
    first = coordinator.commit_answer(projection=seed, record=_record("r1"), evidence_snapshot=_snapshot(host))
    second = coordinator.commit_answer(projection=first.committed_projection, record=_record("r2", supersedes="r1"), evidence_snapshot=_snapshot(host))
    calls_before = verifier.calls
    report = replay_protected_ledger(store, seed_projection=seed)
    assert report.status is ReplayStatus.REPLAYED
    assert report.projection == second.committed_projection
    assert len(report.authorized_transaction_ids) == 2
    assert report.nonauthorized_transaction_ids == ()
    assert report.evaluator_calls == 0
    assert verifier.calls == calls_before


def test_nonauthorized_transaction_replays_as_observation_without_state_change(tmp_path):
    coordinator, host, store, verifier = _setup(tmp_path, verdict=AppraisalVerdict.CANNOT_CHECK)
    seed = _projection()
    result = coordinator.commit_answer(projection=seed, record=_record(), evidence_snapshot=_snapshot(host))
    assert not result.state_changed
    report = replay_protected_ledger(store, seed_projection=seed)
    assert report.projection == seed
    assert report.authorized_transaction_ids == ()
    assert len(report.nonauthorized_transaction_ids) == 1
    assert verifier.calls == 1


def test_empty_ledger_replays_exact_seed(tmp_path):
    store = LedgerStore(tmp_path)
    seed = _projection()
    report = replay_protected_ledger(store, seed_projection=seed)
    assert report.status is ReplayStatus.EMPTY
    assert report.projection == seed


def test_legacy_loose_rows_are_migration_required_not_silently_replayed(tmp_path):
    store = LedgerStore(tmp_path)
    store.append(EntryKind.ANSWER, {"record_id": "legacy"})
    with pytest.raises(LegacyLedgerRequiresMigration):
        replay_protected_ledger(store, seed_projection=_projection())


def test_transaction_identity_tamper_is_detected_even_if_local_entry_hash_is_recomputed(tmp_path):
    coordinator, host, store, _ = _setup(tmp_path)
    seed = _projection()
    coordinator.commit_answer(projection=seed, record=_record(), evidence_snapshot=_snapshot(host))
    entry = store.entries()[0]
    payload = dict(entry.payload)
    payload["transaction_id"] = "f" * 64
    forged_hash = compute_entry_hash(entry.sequence, entry.kind, payload, entry.prev_hash)
    store.path.write_text(
        __import__("json").dumps(
            {
                "sequence": entry.sequence,
                "kind": entry.kind.value,
                "payload": payload,
                "prev_hash": entry.prev_hash,
                "entry_hash": forged_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )
    with pytest.raises(ReplayFailure, match="transaction identity mismatch"):
        replay_protected_ledger(store, seed_projection=seed)


def test_historical_authorization_signature_tamper_is_detected(tmp_path):
    coordinator, host, store, _ = _setup(tmp_path)
    seed = _projection()
    coordinator.commit_answer(projection=seed, record=_record(), evidence_snapshot=_snapshot(host))
    entry = store.entries()[0]
    payload = __import__("copy").deepcopy(entry.payload)
    payload["transaction"]["authorization"]["signature"] = "00" * 64
    payload["transaction_id"] = __import__("orion.kernel.transition", fromlist=["canonical_digest"]).canonical_digest(
        payload["transaction"], domain="orion.transition-transaction.v1"
    )
    forged_hash = compute_entry_hash(entry.sequence, entry.kind, payload, entry.prev_hash)
    store.path.write_text(
        __import__("json").dumps(
            {"sequence": 0, "kind": "TRANSITION", "payload": payload, "prev_hash": entry.prev_hash, "entry_hash": forged_hash},
            sort_keys=True,
            separators=(",", ":"),
        ) + "\n"
    )
    with pytest.raises(ReplayFailure, match="authorization signature invalid"):
        replay_protected_ledger(store, seed_projection=seed)
