"""P1 V2 causal-responsibility and donor-engulfment substrate.

Additive only. Frozen P1 V1 runners, ``PROTOCOL_V1.json``, and V1 result
tables are inputs, never outputs. Strong nearest-work structures are absorbed
as reusable mechanics with provenance; donor-owned atoms remain credited to
their original sources.
"""

from .absorbed_mechanics import (
    ABSORBED_COMPONENTS,
    AbsorbedComponent,
    BrokerDecision,
    ClaimRecord,
    ClaimStatus,
    CounterfactualRepairCandidate,
    DependencyNode,
    DiagnosticProbe,
    ExecutionRequest,
    InquiryRevisionState,
    InterventionEvidence,
    MinimalRepairSet,
    MutationCertificate,
    RecoveryAction,
    RecoveryAdmission,
    VerificationObligation,
    admit_recovery_action,
    choose_information_probe,
    component_registry,
    dependency_impact_closure,
    enforce_certificate,
    inclusion_minimal_successful_repairs,
    missing_verification_obligations,
)
from .belief import (
    AuthorityClass,
    BeliefState,
    UnauthorizedBeliefMutation,
)
from .causal_context import CausalContext, CausalDependency, dual_slice_causal_context
from .campaign import live_campaign_status
from .cases import (
    CauseConfusableBundle,
    ProtectedGold,
    PublicMemberView,
    gold_leak,
    known_answer_bundles,
)
from .controls import HOSTILE_CONTROLS, run_hostile_controls
from .discriminator import ProbeCatalog, ProbeSpec, select_discriminator
from .engine import CausalCycle, run_cycle
from .hypotheses import COMPETING_HYPOTHESES, HypothesisId
from .intervention import (
    InterventionOutcome,
    InterventionSpec,
    apply_intervention,
    apply_probe,
)
from .licensing import (
    EpistemicAction,
    LicenseDecision,
    RefusalReason,
    UnauthorizedMutationError,
    apply_licensed_action,
    audit_matrix,
    request_action,
)
from .protocol import PROTOCOL_ID, load_protocol, protocol_sha256
from .reproduce_v1 import reproduce_v1, write_receipt

__all__ = [
    "ABSORBED_COMPONENTS",
    "COMPETING_HYPOTHESES",
    "HOSTILE_CONTROLS",
    "PROTOCOL_ID",
    "AbsorbedComponent",
    "AuthorityClass",
    "BeliefState",
    "BrokerDecision",
    "CausalCycle",
    "CausalContext",
    "CausalDependency",
    "CauseConfusableBundle",
    "ClaimRecord",
    "ClaimStatus",
    "CounterfactualRepairCandidate",
    "DependencyNode",
    "DiagnosticProbe",
    "EpistemicAction",
    "ExecutionRequest",
    "HypothesisId",
    "InquiryRevisionState",
    "InterventionEvidence",
    "InterventionOutcome",
    "InterventionSpec",
    "LicenseDecision",
    "MinimalRepairSet",
    "MutationCertificate",
    "ProbeCatalog",
    "ProbeSpec",
    "ProtectedGold",
    "PublicMemberView",
    "RecoveryAction",
    "RecoveryAdmission",
    "RefusalReason",
    "UnauthorizedBeliefMutation",
    "UnauthorizedMutationError",
    "VerificationObligation",
    "admit_recovery_action",
    "apply_intervention",
    "apply_licensed_action",
    "apply_probe",
    "audit_matrix",
    "choose_information_probe",
    "component_registry",
    "dependency_impact_closure",
    "dual_slice_causal_context",
    "enforce_certificate",
    "gold_leak",
    "inclusion_minimal_successful_repairs",
    "known_answer_bundles",
    "live_campaign_status",
    "load_protocol",
    "missing_verification_obligations",
    "protocol_sha256",
    "reproduce_v1",
    "request_action",
    "run_cycle",
    "run_hostile_controls",
    "select_discriminator",
    "write_receipt",
]
