"""Protected relying-party transition authorization.

This is the sole module allowed to construct ``TransitionAuthorization``. It
combines an exact candidate plan, a signed verifier appraisal, revisioned host
authority state and DNF support state under non-compensatory hard gates.

A verifier PASS is necessary but never sufficient. The decision fails closed
when any protected obligation is stale, unknown, mismatched, revoked or
post-hoc. Candidate-facing runtime modules must not import this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .assurance import (
    AppraisalSignatureStatus,
    AppraisalVerdict,
    VerifierAppraisal,
    transition_subject_hash,
    verify_appraisal_signature,
)
from .authority_state import (
    AuthorityObjectKind,
    AuthorityObjectStatus,
    AuthorityState,
    SupportState,
)
from .support import SupportVerdict
from .transition import LedgerExpectation, canonical_digest, canonical_json_bytes
from .transition_reducer import TransitionPlan


class AuthorizationVerdict(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


class AuthorizationSignatureStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class AuthorizationContext:
    plan: TransitionPlan
    appraisal: VerifierAppraisal
    authority_state: AuthorityState
    support_state: SupportState
    current_expectation: LedgerExpectation
    evaluator_registration_id: str
    policy_registration_id: str
    authorization_key_registration_id: str
    trust_root_registration_id: str
    chronology_frozen_before_candidate: bool


@dataclass(frozen=True)
class AuthorizationDecision:
    authorization_id: str
    transition_id: str
    subject_hash: str
    verdict: AuthorizationVerdict
    reason_codes: tuple[str, ...]
    expectation: LedgerExpectation
    authority_revision: str
    support_revision: str
    authorization_key_registration_id: str

    @property
    def authorizes_state_change(self) -> bool:
        return self.verdict is AuthorizationVerdict.AUTHORIZED

    @property
    def grants_scientific_authority(self) -> bool:
        return False


@dataclass(frozen=True)
class TransitionAuthorization:
    """Sealed relying-party authorization receipt.

    Construction is intentionally confined to this module. Possessing this
    receipt is still not the same as committing a transaction; the store must
    independently compare all expected revisions under one writer lock.
    """

    authorization_id: str
    transition_id: str
    subject_hash: str
    verdict: AuthorizationVerdict
    reason_codes: tuple[str, ...]
    expectation: LedgerExpectation
    authority_revision: str
    support_revision: str
    authorization_key_registration_id: str
    signature: str

    @property
    def authorizes_state_change(self) -> bool:
        return self.verdict is AuthorizationVerdict.AUTHORIZED


class ProtectedAuthorizationSigner(Protocol):
    @property
    def registration_id(self) -> str: ...

    def sign(self, payload: bytes) -> str: ...


def _registration_gate(
    state: AuthorityState,
    registration_id: str,
    kind: AuthorityObjectKind,
    reasons: list[str],
) -> object | None:
    registration = state.registration(registration_id)
    if registration is None:
        reasons.append(f"registration_missing:{kind.value}:{registration_id}")
        return None
    if registration.kind is not kind:
        reasons.append(
            f"registration_kind_mismatch:{registration_id}:{registration.kind.value}:{kind.value}"
        )
        return None
    status = state.current_status(registration_id)
    if status is AuthorityObjectStatus.REVOKED:
        reasons.append(f"registration_revoked:{registration_id}")
        return None
    if status is AuthorityObjectStatus.STALE:
        reasons.append(f"registration_stale:{registration_id}")
        return None
    if status is AuthorityObjectStatus.UNKNOWN:
        reasons.append(f"registration_status_unknown:{registration_id}")
        return None
    return registration


def _verdict_from_reasons(
    reasons: tuple[str, ...], appraisal: VerifierAppraisal
) -> AuthorizationVerdict:
    if appraisal.verdict is AppraisalVerdict.FAIL:
        return AuthorizationVerdict.FAIL
    if appraisal.verdict is AppraisalVerdict.BLOCKED:
        return AuthorizationVerdict.BLOCKED
    if appraisal.verdict is AppraisalVerdict.CANNOT_CHECK:
        return AuthorizationVerdict.CANNOT_CHECK
    demonstrated_failures = {
        "all_registered_support_sets_failed",
    }
    if any(reason in demonstrated_failures for reason in reasons):
        return AuthorizationVerdict.FAIL
    if any(
        "revoked" in reason or "invalid" in reason or "mismatch" in reason
        for reason in reasons
    ):
        return AuthorizationVerdict.FAIL
    if any("blocked" in reason for reason in reasons):
        return AuthorizationVerdict.BLOCKED
    if reasons:
        return AuthorizationVerdict.CANNOT_CHECK
    return AuthorizationVerdict.AUTHORIZED


def authorize_transition(context: AuthorizationContext) -> AuthorizationDecision:
    """Pure relying-party decision over frozen, revision-bound protected data."""

    plan = context.plan
    appraisal = context.appraisal
    reasons: list[str] = []

    expected_subject = transition_subject_hash(plan)
    if appraisal.subject_hash != expected_subject:
        reasons.append("appraisal_subject_mismatch")
    if appraisal.transition_id != plan.transition_id:
        reasons.append("appraisal_transition_mismatch")
    if appraisal.evidence_snapshot_hash != plan.evidence_snapshot_hash:
        reasons.append("appraisal_evidence_snapshot_mismatch")
    if context.current_expectation != plan.expectation:
        reasons.append("current_ledger_expectation_mismatch")
    if context.authority_state.revision != plan.expectation.authority_revision:
        reasons.append("authority_revision_mismatch")
    if context.support_state.revision != plan.expectation.support_revision:
        reasons.append("support_revision_mismatch")
    if not context.chronology_frozen_before_candidate:
        reasons.append("evaluator_or_policy_chronology_not_frozen")

    evaluator = _registration_gate(
        context.authority_state,
        context.evaluator_registration_id,
        AuthorityObjectKind.EVALUATOR,
        reasons,
    )
    policy = _registration_gate(
        context.authority_state,
        context.policy_registration_id,
        AuthorityObjectKind.POLICY,
        reasons,
    )
    key = _registration_gate(
        context.authority_state,
        context.authorization_key_registration_id,
        AuthorityObjectKind.KEY,
        reasons,
    )
    root = _registration_gate(
        context.authority_state,
        context.trust_root_registration_id,
        AuthorityObjectKind.TRUST_ROOT,
        reasons,
    )
    del policy, key, root

    if evaluator is not None:
        registration = context.authority_state.registration(
            context.evaluator_registration_id
        )
        assert registration is not None
        if appraisal.registration_commitment != registration.commitment:
            reasons.append("appraisal_registration_commitment_mismatch")
        if appraisal.verifier_id != registration.registration_id:
            reasons.append("appraisal_verifier_identity_mismatch")
        if appraisal.evaluation_epoch_id != registration.epoch_id:
            reasons.append("appraisal_evaluation_epoch_mismatch")
        signature = verify_appraisal_signature(
            appraisal,
            registered_public_key_hex=registration.public_key_hex,
        )
        if signature.status is AppraisalSignatureStatus.INVALID:
            reasons.append("appraisal_signature_invalid")
        elif signature.status is AppraisalSignatureStatus.CANNOT_CHECK:
            reasons.append("appraisal_signature_cannot_check")

    support = context.support_state.evaluation
    if support.verdict is SupportVerdict.FAIL:
        reasons.append("all_registered_support_sets_failed")
    elif support.verdict is SupportVerdict.CANNOT_CHECK:
        reasons.append("support_state_cannot_check")

    if appraisal.verdict is not AppraisalVerdict.PASS:
        reasons.append(f"appraisal_not_pass:{appraisal.verdict.value}")

    reason_codes = tuple(dict.fromkeys(reasons))
    verdict = _verdict_from_reasons(reason_codes, appraisal)
    payload = {
        "transition_id": plan.transition_id,
        "subject_hash": expected_subject,
        "verdict": verdict.value,
        "reason_codes": list(reason_codes),
        "expectation": {
            "ledger_head": plan.expectation.ledger_head,
            "research_state_hash": plan.expectation.research_state_hash,
            "authority_revision": plan.expectation.authority_revision,
            "support_revision": plan.expectation.support_revision,
        },
        "authority_revision": context.authority_state.revision,
        "support_revision": context.support_state.revision,
        "authorization_key_registration_id": context.authorization_key_registration_id,
    }
    authorization_id = canonical_digest(
        payload, domain="orion.transition-authorization-decision.v1"
    )
    return AuthorizationDecision(
        authorization_id,
        plan.transition_id,
        expected_subject,
        verdict,
        reason_codes,
        plan.expectation,
        context.authority_state.revision,
        context.support_state.revision,
        context.authorization_key_registration_id,
    )


def authorization_signing_payload(decision: AuthorizationDecision) -> bytes:
    return canonical_json_bytes(
        {
            "authorization_id": decision.authorization_id,
            "transition_id": decision.transition_id,
            "subject_hash": decision.subject_hash,
            "verdict": decision.verdict.value,
            "reason_codes": list(decision.reason_codes),
            "expectation": {
                "ledger_head": decision.expectation.ledger_head,
                "research_state_hash": decision.expectation.research_state_hash,
                "authority_revision": decision.expectation.authority_revision,
                "support_revision": decision.expectation.support_revision,
            },
            "authority_revision": decision.authority_revision,
            "support_revision": decision.support_revision,
            "authorization_key_registration_id": decision.authorization_key_registration_id,
        }
    )


def seal_authorization(
    decision: AuthorizationDecision,
    *,
    signer: ProtectedAuthorizationSigner,
) -> TransitionAuthorization:
    if signer.registration_id != decision.authorization_key_registration_id:
        raise ValueError("protected signer does not match the authorized key registration")
    signature = signer.sign(authorization_signing_payload(decision))
    if len(signature) != 128 or any(
        character not in "0123456789abcdef" for character in signature
    ):
        raise ValueError(
            "protected authorization signer must return a 64-byte lowercase-hex signature"
        )
    return TransitionAuthorization(
        decision.authorization_id,
        decision.transition_id,
        decision.subject_hash,
        decision.verdict,
        decision.reason_codes,
        decision.expectation,
        decision.authority_revision,
        decision.support_revision,
        decision.authorization_key_registration_id,
        signature,
    )


def restore_transition_authorization(
    *,
    authorization_id: str,
    transition_id: str,
    subject_hash: str,
    verdict: AuthorizationVerdict,
    reason_codes: tuple[str, ...],
    expectation: LedgerExpectation,
    authority_revision: str,
    support_revision: str,
    authorization_key_registration_id: str,
    signature: str,
) -> TransitionAuthorization:
    """Reconstruct a historical receipt while preserving the constructor choke point."""

    return TransitionAuthorization(
        authorization_id,
        transition_id,
        subject_hash,
        verdict,
        reason_codes,
        expectation,
        authority_revision,
        support_revision,
        authorization_key_registration_id,
        signature,
    )


def verify_authorization_signature(
    authorization: TransitionAuthorization,
    *,
    authority_state: AuthorityState,
) -> AuthorizationSignatureStatus:
    registration = authority_state.live_registration(
        authorization.authorization_key_registration_id,
        kind=AuthorityObjectKind.KEY,
    )
    if registration is None:
        return AuthorizationSignatureStatus.CANNOT_CHECK
    decision = AuthorizationDecision(
        authorization.authorization_id,
        authorization.transition_id,
        authorization.subject_hash,
        authorization.verdict,
        authorization.reason_codes,
        authorization.expectation,
        authorization.authority_revision,
        authorization.support_revision,
        authorization.authorization_key_registration_id,
    )
    try:
        key = Ed25519PublicKey.from_public_bytes(
            bytes.fromhex(registration.public_key_hex)
        )
        key.verify(
            bytes.fromhex(authorization.signature),
            authorization_signing_payload(decision),
        )
    except (ValueError, InvalidSignature):
        return AuthorizationSignatureStatus.INVALID
    return AuthorizationSignatureStatus.VALID


__all__ = [
    "AuthorizationContext",
    "AuthorizationDecision",
    "AuthorizationSignatureStatus",
    "AuthorizationVerdict",
    "ProtectedAuthorizationSigner",
    "TransitionAuthorization",
    "authorization_signing_payload",
    "authorize_transition",
    "restore_transition_authorization",
    "seal_authorization",
    "verify_authorization_signature",
]
