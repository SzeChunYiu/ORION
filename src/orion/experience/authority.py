from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .model import (
    FailurePatternCandidate,
    PatternVerificationReceipt,
    TaskEpisode,
    failure_pattern_fingerprint,
    failure_pattern_support_reasons,
    task_episode_fingerprint,
)


@dataclass(frozen=True)
class PatternVerifierSigningIdentity:
    verifier_id: str
    key_id: str
    signing_key: bytes
    process_lineage_hash: str
    evaluator_artifact_hash: str
    evidence_lineage_hash: str

    def __post_init__(self) -> None:
        if not self.verifier_id.strip() or not self.key_id.strip():
            raise ValueError(
                "pattern verifier signing identity requires verifier and key ids"
            )
        if len(self.signing_key) != 32:
            raise ValueError(
                "pattern verifier Ed25519 signing key must contain 32 bytes"
            )
        _validate_lineage_hashes(
            self.process_lineage_hash,
            self.evaluator_artifact_hash,
            self.evidence_lineage_hash,
        )


@dataclass(frozen=True)
class PatternVerifierRegistration:
    verifier_id: str
    key_id: str
    verification_key: bytes
    process_lineage_hash: str
    evaluator_artifact_hash: str
    evidence_lineage_hash: str

    def __post_init__(self) -> None:
        if not self.verifier_id.strip() or not self.key_id.strip():
            raise ValueError(
                "pattern verifier registration requires verifier and key ids"
            )
        if len(self.verification_key) != 32:
            raise ValueError(
                "pattern verifier Ed25519 public key must contain 32 bytes"
            )
        _validate_lineage_hashes(
            self.process_lineage_hash,
            self.evaluator_artifact_hash,
            self.evidence_lineage_hash,
        )


@dataclass(frozen=True)
class PatternVerificationTrustStore:
    registrations: tuple[PatternVerifierRegistration, ...] = ()

    def __post_init__(self) -> None:
        identities = [(item.verifier_id, item.key_id) for item in self.registrations]
        if len(set(identities)) != len(identities):
            raise ValueError(
                "pattern verifier registrations must have unique identities"
            )


@dataclass(frozen=True)
class PatternVerificationResolution:
    valid: bool
    process_independent: bool
    evaluator_independent: bool
    evidence_lineage_independent: bool
    reasons: tuple[str, ...]


def _validate_lineage_hashes(*digests: str) -> None:
    if any(
        len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
        for digest in digests
    ):
        raise ValueError("pattern verifier lineage identities must be SHA-256 hashes")


def _receipt_payload(receipt: PatternVerificationReceipt) -> bytes:
    payload = {
        "receipt_id": receipt.receipt_id,
        "pattern_id": receipt.pattern_id,
        "pattern_hash": receipt.pattern_hash,
        "episode_bindings": [list(item) for item in receipt.episode_bindings],
        "verifier_id": receipt.verifier_id,
        "key_id": receipt.key_id,
        "process_lineage_hash": receipt.process_lineage_hash,
        "evaluator_artifact_hash": receipt.evaluator_artifact_hash,
        "evidence_lineage_hash": receipt.evidence_lineage_hash,
        "passed": receipt.passed,
        "reason": receipt.reason,
        "issued_at": receipt.issued_at,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evidence_binding_lineage_hash(episodes: tuple[TaskEpisode, ...]) -> str:
    """Derive one canonical lineage hash from exact episode evidence bindings."""

    payload = [
        [episode.episode_id, [list(item) for item in episode.evidence_bindings]]
        for episode in sorted(episodes, key=lambda item: item.episode_id)
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def mint_pattern_verification_receipt(
    identity: PatternVerifierSigningIdentity,
    candidate: FailurePatternCandidate,
    episodes: tuple[TaskEpisode, ...],
    *,
    passed: bool,
    reason: str,
    issued_at: str,
) -> PatternVerificationReceipt:
    """Mint a content-bound receipt from the protected verifier path."""

    if not reason.strip() or not issued_at.strip():
        raise ValueError("pattern verification requires a reason and issued_at")
    support_reasons = failure_pattern_support_reasons(candidate, episodes)
    if support_reasons:
        raise ValueError(
            "invalid failure-pattern support: " + ",".join(support_reasons)
        )
    bindings = tuple(
        sorted(
            (episode.episode_id, task_episode_fingerprint(episode))
            for episode in episodes
        )
    )
    if len({episode_id for episode_id, _ in bindings}) != len(bindings):
        raise ValueError("pattern verification episodes must have unique identities")
    seed = "|".join(
        (
            candidate.pattern_id,
            failure_pattern_fingerprint(candidate),
            identity.verifier_id,
            identity.key_id,
            issued_at,
            repr(bindings),
        )
    )
    receipt = PatternVerificationReceipt(
        receipt_id="pattern-verification:"
        + hashlib.sha256(seed.encode("utf-8")).hexdigest(),
        pattern_id=candidate.pattern_id,
        pattern_hash=failure_pattern_fingerprint(candidate),
        episode_bindings=bindings,
        verifier_id=identity.verifier_id,
        key_id=identity.key_id,
        process_lineage_hash=identity.process_lineage_hash,
        evaluator_artifact_hash=identity.evaluator_artifact_hash,
        evidence_lineage_hash=identity.evidence_lineage_hash,
        passed=passed,
        reason=reason,
        issued_at=issued_at,
        signature="0" * 128,
    )
    signature = (
        Ed25519PrivateKey.from_private_bytes(identity.signing_key)
        .sign(_receipt_payload(receipt))
        .hex()
    )
    return replace(receipt, signature=signature)


def resolve_pattern_verification(
    context: PatternVerificationTrustStore,
    receipt: PatternVerificationReceipt,
    candidate: FailurePatternCandidate,
    episodes: tuple[TaskEpisode, ...],
) -> PatternVerificationResolution:
    registration = next(
        (
            item
            for item in context.registrations
            if item.verifier_id == receipt.verifier_id and item.key_id == receipt.key_id
        ),
        None,
    )
    if registration is None:
        return PatternVerificationResolution(
            False,
            False,
            False,
            False,
            (f"untrusted_pattern_verifier:{receipt.verifier_id}:{receipt.key_id}",),
        )
    try:
        Ed25519PublicKey.from_public_bytes(registration.verification_key).verify(
            bytes.fromhex(receipt.signature),
            _receipt_payload(receipt),
        )
    except InvalidSignature:
        return PatternVerificationResolution(
            False,
            False,
            False,
            False,
            ("invalid_pattern_verification_signature",),
        )
    lineage_fields = (
        ("process", receipt.process_lineage_hash, registration.process_lineage_hash),
        (
            "evaluator",
            receipt.evaluator_artifact_hash,
            registration.evaluator_artifact_hash,
        ),
        ("evidence", receipt.evidence_lineage_hash, registration.evidence_lineage_hash),
    )
    lineage_mismatches = tuple(
        f"verification_{name}_lineage_mismatch"
        for name, observed, trusted in lineage_fields
        if observed != trusted
    )
    if lineage_mismatches:
        return PatternVerificationResolution(
            False, False, False, False, lineage_mismatches
        )
    if receipt.pattern_id != candidate.pattern_id:
        return PatternVerificationResolution(
            False, False, False, False, ("verification_subject_mismatch",)
        )
    if receipt.pattern_hash != failure_pattern_fingerprint(candidate):
        return PatternVerificationResolution(
            False, False, False, False, ("verification_subject_hash_mismatch",)
        )

    actual = {
        episode.episode_id: task_episode_fingerprint(episode) for episode in episodes
    }
    bound = dict(receipt.episode_bindings)
    if set(bound) != set(actual):
        return PatternVerificationResolution(
            False, False, False, False, ("verification_episode_binding_mismatch",)
        )
    mismatched = tuple(
        episode_id
        for episode_id in sorted(actual)
        if bound[episode_id] != actual[episode_id]
    )
    if mismatched:
        return PatternVerificationResolution(
            False,
            False,
            False,
            False,
            tuple(
                f"verification_episode_content_mismatch:{item}" for item in mismatched
            ),
        )
    process_lineages = {episode.producer_process_lineage_hash for episode in episodes}
    evaluator_lineages = {episode.evaluator_artifact_hash for episode in episodes}
    candidate_evidence_lineage = evidence_binding_lineage_hash(episodes)
    process_independent = (
        None not in process_lineages
        and receipt.process_lineage_hash not in process_lineages
    )
    evaluator_independent = (
        None not in evaluator_lineages
        and receipt.evaluator_artifact_hash not in evaluator_lineages
    )
    evidence_independent = receipt.evidence_lineage_hash != candidate_evidence_lineage
    independence_reasons = tuple(
        reason
        for independent, reason in (
            (process_independent, "verification_process_not_independent"),
            (evaluator_independent, "verification_evaluator_not_independent"),
            (evidence_independent, "verification_evidence_lineage_not_independent"),
        )
        if not independent
    )
    return PatternVerificationResolution(
        True,
        process_independent,
        evaluator_independent,
        evidence_independent,
        independence_reasons,
    )
