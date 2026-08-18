"""Reusable donor mechanics absorbed into the Paper-1 ORION substrate.

Strong nearest work is engulfed as reusable framework structure with provenance,
then ORION claims only what survives after composition.  The implementations
here are protocol-level abstractions, not claims of reproducing every donor
system.

Primary structural parents represented here include Iris/AGM-style revisable
information state, REFLECT/CAR-style intervention-backed attribution,
HERALD/CausalFlow-style counterfactual minimal repair, R2Act/DARC-style
diagnosis-to-action admission, EviGraph/TMS/change-impact scoped invalidation,
value-of-information metareasoning, and SEB/PORTICO-style scoped revocable
execution authority.  Source-level provenance remains in the P1 donor
engulfment ledgers.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping


class ClaimStatus(str, Enum):
    ACTIVE = "ACTIVE"
    QUALIFIED = "QUALIFIED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    text: str
    scope: tuple[str, ...]
    support_ids: tuple[str, ...] = ()
    refute_ids: tuple[str, ...] = ()
    status: ClaimStatus = ClaimStatus.ACTIVE


@dataclass(frozen=True)
class InquiryRevisionState:
    """Iris/AGM-style explicit, scoped, revisable information state."""

    claims: tuple[ClaimRecord, ...] = ()

    def by_id(self, claim_id: str) -> ClaimRecord:
        for claim in self.claims:
            if claim.claim_id == claim_id:
                return claim
        raise KeyError(claim_id)

    def add(self, claim: ClaimRecord) -> "InquiryRevisionState":
        if any(item.claim_id == claim.claim_id for item in self.claims):
            raise ValueError(f"duplicate claim:{claim.claim_id}")
        return InquiryRevisionState((*self.claims, claim))

    def update(
        self,
        claim_id: str,
        *,
        text: str | None = None,
        scope: tuple[str, ...] | None = None,
        support_ids: tuple[str, ...] | None = None,
        refute_ids: tuple[str, ...] | None = None,
        status: ClaimStatus | None = None,
    ) -> "InquiryRevisionState":
        current = self.by_id(claim_id)
        revised = replace(
            current,
            text=current.text if text is None else text,
            scope=current.scope if scope is None else scope,
            support_ids=current.support_ids if support_ids is None else support_ids,
            refute_ids=current.refute_ids if refute_ids is None else refute_ids,
            status=current.status if status is None else status,
        )
        return InquiryRevisionState(
            tuple(revised if item.claim_id == claim_id else item for item in self.claims)
        )

    def invalidate(
        self,
        claim_id: str,
        *,
        refute_id: str,
    ) -> "InquiryRevisionState":
        current = self.by_id(claim_id)
        return self.update(
            claim_id,
            refute_ids=tuple(dict.fromkeys((*current.refute_ids, refute_id))),
            status=ClaimStatus.INVALIDATED,
        )

    def active_for_scope(self, scope_token: str) -> tuple[ClaimRecord, ...]:
        return tuple(
            item
            for item in self.claims
            if item.status is not ClaimStatus.INVALIDATED
            and scope_token in item.scope
        )


@dataclass(frozen=True)
class InterventionEvidence:
    """REFLECT/CAR-style causal evidence; evidence is not mutation authority."""

    intervention_id: str
    hypothesized_cause: str
    predicted_observable: str
    expected_direction: str
    observed_direction: str
    evidence_ids: tuple[str, ...] = ()

    @property
    def supports_hypothesis(self) -> bool:
        return self.observed_direction == self.expected_direction


@dataclass(frozen=True)
class DiagnosticProbe:
    probe_id: str
    separates: frozenset[str]
    cost: float

    def __post_init__(self) -> None:
        if self.cost <= 0:
            raise ValueError("probe cost must be positive")


def choose_information_probe(
    live_causes: tuple[str, str],
    probes: Iterable[DiagnosticProbe],
) -> DiagnosticProbe | None:
    """MedAction/VOI-style cheapest discriminator of the live cause pair."""

    target = frozenset(live_causes)
    candidates = [probe for probe in probes if target.issubset(probe.separates)]
    if not candidates:
        candidates = [
            probe
            for probe in probes
            if probe.separates.intersection(target)
        ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item.cost, item.probe_id))


@dataclass(frozen=True)
class CounterfactualRepairCandidate:
    """HERALD/CausalFlow-style candidate evaluated under an intervention."""

    repair_id: str
    edited_atoms: frozenset[str]
    target_success: bool
    protected_ok: bool = True


@dataclass(frozen=True)
class MinimalRepairSet:
    repair_ids: tuple[str, ...]
    cardinality: int | None


def inclusion_minimal_successful_repairs(
    candidates: Iterable[CounterfactualRepairCandidate],
    *,
    require_protected_ok: bool = False,
) -> MinimalRepairSet:
    """Return inclusion-minimal successful counterfactual repairs.

    This explicitly absorbs counterfactual minimal-repair structure.  It does
    not decide scientific K/W/M authority: the output is a repair candidate set
    consumed by later scientific-state constraints.
    """

    eligible = tuple(
        item
        for item in candidates
        if item.target_success and (item.protected_ok or not require_protected_ok)
    )
    minimal: list[CounterfactualRepairCandidate] = []
    for item in eligible:
        if any(
            other.repair_id != item.repair_id
            and other.edited_atoms < item.edited_atoms
            for other in eligible
        ):
            continue
        minimal.append(item)
    ordered = tuple(sorted(item.repair_id for item in minimal))
    cardinality = min((len(item.edited_atoms) for item in minimal), default=None)
    return MinimalRepairSet(ordered, cardinality)


@dataclass(frozen=True)
class RecoveryAction:
    action_id: str
    action_type: str
    target: str
    admissible_diagnoses: frozenset[str]
    declared_cost: float = 1.0


@dataclass(frozen=True)
class RecoveryAdmission:
    diagnosis: str
    action_id: str
    admitted: bool
    reason: str


def admit_recovery_action(
    diagnosis: str,
    action: RecoveryAction,
) -> RecoveryAdmission:
    """R2Act/DARC-style diagnosis-to-action validity gate."""

    admitted = diagnosis in action.admissible_diagnoses
    return RecoveryAdmission(
        diagnosis=diagnosis,
        action_id=action.action_id,
        admitted=admitted,
        reason="diagnosis_matches_action_space" if admitted else "diagnosis_action_mismatch",
    )


@dataclass(frozen=True)
class DependencyNode:
    node_id: str
    coordinates: frozenset[str]
    parent_ids: tuple[str, ...] = ()


def dependency_impact_closure(
    nodes: Iterable[DependencyNode],
    changed_coordinates: Iterable[str],
) -> tuple[str, ...]:
    """EviGraph/TMS/CIA-style minimal transitive downstream invalidation."""

    ordered = tuple(nodes)
    changed = frozenset(changed_coordinates)
    selected = {
        item.node_id
        for item in ordered
        if item.coordinates.intersection(changed)
    }
    progress = True
    while progress:
        progress = False
        for item in ordered:
            if item.node_id in selected:
                continue
            if any(parent in selected for parent in item.parent_ids):
                selected.add(item.node_id)
                progress = True
    return tuple(item.node_id for item in ordered if item.node_id in selected)


@dataclass(frozen=True)
class VerificationObligation:
    object_id: str
    verification_id: str | None

    @property
    def missing(self) -> bool:
        return not self.verification_id


def missing_verification_obligations(
    rows: Iterable[VerificationObligation],
) -> tuple[str, ...]:
    """NASA verification-matrix discipline: an empty relation is an obligation."""

    return tuple(item.object_id for item in rows if item.missing)


@dataclass(frozen=True)
class MutationCertificate:
    """SEB/PORTICO-style certificate-bound mutation contract.

    A certificate records authority produced elsewhere; the broker only enforces
    exact action/scope/epoch/state bindings and never invents authority.
    """

    certificate_id: str
    action_id: str
    scope: frozenset[str]
    issued_epoch: int
    revocation_epoch: int
    state_digest: str


@dataclass(frozen=True)
class ExecutionRequest:
    action_id: str
    target_scope: str
    epoch: int
    state_digest: str


@dataclass(frozen=True)
class BrokerDecision:
    admitted: bool
    reason: str


def enforce_certificate(
    certificate: MutationCertificate,
    request: ExecutionRequest,
) -> BrokerDecision:
    if request.action_id != certificate.action_id:
        return BrokerDecision(False, "action_mismatch")
    if request.target_scope not in certificate.scope:
        return BrokerDecision(False, "scope_mismatch")
    if request.epoch < certificate.issued_epoch:
        return BrokerDecision(False, "pre_issue_epoch")
    if request.epoch >= certificate.revocation_epoch:
        return BrokerDecision(False, "revoked_or_expired")
    if request.state_digest != certificate.state_digest:
        return BrokerDecision(False, "live_state_drift")
    return BrokerDecision(True, "certificate_bound_execution")


@dataclass(frozen=True)
class AbsorbedComponent:
    component_id: str
    role: str
    donor_keys: tuple[str, ...]
    executable_surface: tuple[str, ...]


ABSORBED_COMPONENTS: tuple[AbsorbedComponent, ...] = (
    AbsorbedComponent(
        "INQUIRY_REVISION_STATE",
        "explicit scoped and revisable K/information state",
        ("Iris", "AGM", "Kosmos", "AREX-context"),
        ("InquiryRevisionState", "ClaimRecord"),
    ),
    AbsorbedComponent(
        "CAUSAL_DIAGNOSIS",
        "active inquiry plus intervention-backed causal attribution",
        (
            "REFLECT",
            "CAR",
            "Who&When",
            "MAST",
            "MedAction",
            "OAT",
            "ARTS",
            "CausalRepair",
        ),
        (
            "InterventionEvidence",
            "DiagnosticProbe",
            "choose_information_probe",
            "CausalDependency",
            "CausalContext",
            "dual_slice_causal_context",
        ),
    ),
    AbsorbedComponent(
        "COUNTERFACTUAL_MINIMAL_REPAIR",
        "same-task intervention audit plus inclusion-minimal causal repair",
        ("HERALD", "CausalFlow"),
        ("CounterfactualRepairCandidate", "inclusion_minimal_successful_repairs"),
    ),
    AbsorbedComponent(
        "ADMISSIBLE_RECOVERY",
        "diagnosis-conditioned valid action/target selection",
        ("R2Act", "DARC"),
        ("RecoveryAction", "admit_recovery_action"),
    ),
    AbsorbedComponent(
        "DEPENDENCY_TRUTH_MAINTENANCE",
        "scoped staleness, rollback and transitive dependent invalidation",
        ("EviGraph", "EA-Graph", "Doyle-TMS", "de-Kleer-ATMS", "CIA", "STARTS"),
        ("DependencyNode", "dependency_impact_closure"),
    ),
    AbsorbedComponent(
        "VERIFICATION_OBLIGATION",
        "missing traceability/verification relation becomes a typed obligation",
        ("NASA-SE",),
        ("VerificationObligation", "missing_verification_obligations"),
    ),
    AbsorbedComponent(
        "CERTIFICATE_BOUND_EXECUTION",
        "proposal/admission/execution separation with scoped revocable authority",
        ("SAB", "SEB", "PORTICO"),
        ("MutationCertificate", "ExecutionRequest", "enforce_certificate"),
    ),
)


def component_registry() -> Mapping[str, AbsorbedComponent]:
    return {item.component_id: item for item in ABSORBED_COMPONENTS}


__all__ = [
    "ABSORBED_COMPONENTS",
    "AbsorbedComponent",
    "BrokerDecision",
    "ClaimRecord",
    "ClaimStatus",
    "CounterfactualRepairCandidate",
    "DependencyNode",
    "DiagnosticProbe",
    "ExecutionRequest",
    "InquiryRevisionState",
    "InterventionEvidence",
    "MinimalRepairSet",
    "MutationCertificate",
    "RecoveryAction",
    "RecoveryAdmission",
    "VerificationObligation",
    "admit_recovery_action",
    "choose_information_probe",
    "component_registry",
    "dependency_impact_closure",
    "enforce_certificate",
    "inclusion_minimal_successful_repairs",
    "missing_verification_obligations",
]
