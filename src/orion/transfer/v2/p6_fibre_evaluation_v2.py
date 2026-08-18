from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .canonical import content_digest
from .p6_method_fibres import (
    CompositionContract,
    CompositionStatus,
    FibreMembership,
    FibreStatus,
    MembershipEvidence,
    MethodFibre,
    MethodRealizationView,
    StructuralSignature,
    assess_membership,
    build_fibre,
    check_composition,
)


class ComparatorVerdict(str, Enum):
    SAME = "SAME"
    DIFFERENT = "DIFFERENT"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class BoundMembershipReceipt:
    signature_digest: str
    realization_digest: str
    evidence_digest: str
    membership: FibreMembership
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "P6.BoundMembershipReceipt.v2",
            "signature_digest": self.signature_digest,
            "realization_digest": self.realization_digest,
            "evidence_digest": self.evidence_digest,
            "membership": {
                "status": self.membership.status.value,
                "reasons": list(self.membership.reasons),
            },
            "authority_scope": "BOUNDED_FORMAL_MEMBERSHIP_ONLY",
            "can_authorize_transfer": False,
            "can_claim_novelty": False,
        }

    def verify(self) -> None:
        if self.membership.signature_digest != self.signature_digest:
            raise ValueError("membership signature mismatch")
        if self.membership.realization_digest != self.realization_digest:
            raise ValueError("membership realization mismatch")
        if self.membership.evidence_digest != self.evidence_digest:
            raise ValueError("membership evidence mismatch")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("bound membership digest mismatch")


def assess_membership_bound(
    signature: StructuralSignature,
    realization: MethodRealizationView,
    evidence: MembershipEvidence,
) -> BoundMembershipReceipt:
    signature.verify()
    evidence.verify()
    if evidence.signature_digest != signature.digest:
        raise ValueError("evidence bound to different structural signature")
    if evidence.realization_digest != realization.digest:
        raise ValueError("evidence bound to different realization")
    membership = assess_membership(signature, realization, evidence)
    base = {
        "version": "P6.BoundMembershipReceipt.v2",
        "signature_digest": signature.digest,
        "realization_digest": realization.digest,
        "evidence_digest": evidence.digest,
        "membership": {"status": membership.status.value, "reasons": list(membership.reasons)},
        "authority_scope": "BOUNDED_FORMAL_MEMBERSHIP_ONLY",
        "can_authorize_transfer": False,
        "can_claim_novelty": False,
    }
    out = BoundMembershipReceipt(
        signature.digest,
        realization.digest,
        evidence.digest,
        membership,
        content_digest(base),
    )
    out.verify()
    return out


def build_fibre_bound(
    signature: StructuralSignature,
    receipts: Sequence[BoundMembershipReceipt],
) -> MethodFibre:
    signature.verify()
    seen: set[str] = set()
    unwrapped: list[FibreMembership] = []
    for receipt in receipts:
        receipt.verify()
        if receipt.signature_digest != signature.digest:
            raise ValueError("cross-signature membership receipt")
        if receipt.realization_digest in seen:
            raise ValueError("duplicate realization membership receipt")
        seen.add(receipt.realization_digest)
        unwrapped.append(receipt.membership)
    return build_fibre(signature, unwrapped)


def topology_only(left: MethodRealizationView, right: MethodRealizationView) -> ComparatorVerdict:
    # Surface/topology baseline: action/dependency shape only, intentionally ignores
    # preconditions, invariants, reconstruction, failure and authority semantics.
    same = (len(left.actions), left.dependencies) == (len(right.actions), right.dependencies)
    return ComparatorVerdict.SAME if same else ComparatorVerdict.DIFFERENT


def effect_only(left: MethodRealizationView, right: MethodRealizationView) -> ComparatorVerdict:
    return ComparatorVerdict.SAME if left.effects == right.effects else ComparatorVerdict.DIFFERENT


def untyped_state_machine(left: MethodRealizationView, right: MethodRealizationView) -> ComparatorVerdict:
    same = (
        len(left.actions) == len(right.actions)
        and left.dependencies == right.dependencies
        and left.effects == right.effects
        and left.termination == right.termination
    )
    return ComparatorVerdict.SAME if same else ComparatorVerdict.DIFFERENT


def behavioral_bisimulation_style(left: MethodRealizationView, right: MethodRealizationView) -> ComparatorVerdict:
    """Mechanism-matched comparator inspired by behavioral/bisimulation abstractions.

    This is deliberately not presented as an official implementation of any cited
    paper. It asks whether the two realizations agree on claim-visible transition
    behavior (preconditions/effects/termination), while omitting ORION-specific
    invariant, reconstruction, provenance and authority obligations.
    """
    if set(left.unknown_coordinates) & {"preconditions", "effects", "termination"}:
        return ComparatorVerdict.UNRESOLVED
    if set(right.unknown_coordinates) & {"preconditions", "effects", "termination"}:
        return ComparatorVerdict.UNRESOLVED
    same = (
        left.preconditions == right.preconditions
        and left.effects == right.effects
        and left.termination == right.termination
    )
    return ComparatorVerdict.SAME if same else ComparatorVerdict.DIFFERENT


def evaluate_composition_bound(contract: CompositionContract) -> tuple[CompositionStatus, tuple[str, ...]]:
    return check_composition(contract)


def mutation_guard(receipt: BoundMembershipReceipt) -> None:
    receipt.verify()


def expected_same_from_status(status: FibreStatus) -> ComparatorVerdict:
    if status is FibreStatus.MEMBER:
        return ComparatorVerdict.SAME
    if status is FibreStatus.BLOCKED:
        return ComparatorVerdict.DIFFERENT
    return ComparatorVerdict.UNRESOLVED
