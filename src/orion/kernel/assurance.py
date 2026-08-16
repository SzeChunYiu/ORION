"""Protected verifier appraisal primitives.

A verifier appraisal is a signed observation about one exact candidate
transition subject.  It is *not* authorization and cannot mutate research
state.  This module contains no private-key loader, no evaluator callable and no
state-application seam; protected host composition supplies those outside the
candidate-facing runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .transition import canonical_digest, canonical_json_bytes
from .transition_reducer import TransitionPlan


_HEX = frozenset("0123456789abcdef")


def _sha256(value: str, field: str) -> None:
    if len(value) != 64 or any(character not in _HEX for character in value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")


def _hex_bytes(value: str, size: int, field: str) -> None:
    if len(value) != size * 2 or any(character not in _HEX for character in value):
        raise ValueError(f"{field} must encode exactly {size} bytes as lowercase hex")


class AppraisalVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


class AppraisalSignatureStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class VerifierAppraisal:
    appraisal_id: str
    subject_hash: str
    transition_id: str
    evidence_snapshot_hash: str
    registration_commitment: str
    verifier_id: str
    evaluation_epoch_id: str
    verdict: AppraisalVerdict
    reason_codes: tuple[str, ...]
    signature: str

    def __post_init__(self) -> None:
        for field_name in ("appraisal_id", "verifier_id", "evaluation_epoch_id"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} is required")
        for field_name in (
            "subject_hash",
            "transition_id",
            "evidence_snapshot_hash",
            "registration_commitment",
        ):
            _sha256(getattr(self, field_name), field_name)
        if not self.reason_codes or any(not item.strip() for item in self.reason_codes):
            raise ValueError("appraisal reason codes are required")
        _hex_bytes(self.signature, 64, "signature")

    @property
    def grants_transition_authority(self) -> bool:
        return False

    @property
    def grants_scientific_authority(self) -> bool:
        return False


@dataclass(frozen=True)
class AppraisalSignatureReport:
    status: AppraisalSignatureStatus
    appraisal_id: str
    reasons: tuple[str, ...]

    @property
    def authorizes_transition(self) -> bool:
        return False


def transition_subject_hash(plan: TransitionPlan) -> str:
    """Bind appraisal to the exact candidate transition identity and state delta."""

    return canonical_digest(
        {
            "transition_id": plan.transition_id,
            "pre_state_hash": plan.pre_state_hash,
            "proposed_post_state_hash": plan.proposed_post_state_hash,
            "workflow_version": plan.workflow_version,
            "reducer_version": plan.reducer_version,
            "evidence_snapshot_hash": plan.evidence_snapshot_hash,
            "execution_receipt_hash": plan.execution_receipt_hash,
        },
        domain="orion.transition-appraisal-subject.v1",
    )


def appraisal_signing_payload(appraisal: VerifierAppraisal) -> bytes:
    """Canonical bytes signed by an independently installed verifier.

    Signature bytes themselves are excluded from the signed payload.  The
    function is pure and accepts no signing key.
    """

    return canonical_json_bytes(
        {
            "appraisal_id": appraisal.appraisal_id,
            "subject_hash": appraisal.subject_hash,
            "transition_id": appraisal.transition_id,
            "evidence_snapshot_hash": appraisal.evidence_snapshot_hash,
            "registration_commitment": appraisal.registration_commitment,
            "verifier_id": appraisal.verifier_id,
            "evaluation_epoch_id": appraisal.evaluation_epoch_id,
            "verdict": appraisal.verdict.value,
            "reason_codes": list(appraisal.reason_codes),
        }
    )


def verify_appraisal_signature(
    appraisal: VerifierAppraisal,
    *,
    registered_public_key_hex: str,
) -> AppraisalSignatureReport:
    """Verify signature authenticity only; validity still is not authorization."""

    try:
        _hex_bytes(registered_public_key_hex, 32, "registered_public_key_hex")
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(registered_public_key_hex))
    except (ValueError, TypeError):
        return AppraisalSignatureReport(
            AppraisalSignatureStatus.CANNOT_CHECK,
            appraisal.appraisal_id,
            ("registered_verifier_public_key_invalid",),
        )
    try:
        key.verify(bytes.fromhex(appraisal.signature), appraisal_signing_payload(appraisal))
    except InvalidSignature:
        return AppraisalSignatureReport(
            AppraisalSignatureStatus.INVALID,
            appraisal.appraisal_id,
            ("appraisal_signature_invalid",),
        )
    return AppraisalSignatureReport(
        AppraisalSignatureStatus.VALID,
        appraisal.appraisal_id,
        ("appraisal_signature_matches_registered_verifier_key", "signature_validity_does_not_authorize_transition"),
    )


__all__ = [
    "AppraisalSignatureReport",
    "AppraisalSignatureStatus",
    "AppraisalVerdict",
    "VerifierAppraisal",
    "appraisal_signing_payload",
    "transition_subject_hash",
    "verify_appraisal_signature",
]
