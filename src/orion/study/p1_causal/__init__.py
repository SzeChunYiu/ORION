"""P1 V2 causal-responsibility scaffolding (#278).

Additive only. Frozen P1 V1 runners, ``PROTOCOL_V1.json``, and V1 result
tables are inputs, never outputs. The #137 diagnosability/licensing modules
are a substrate and are not edited here.
"""

from .belief import (
    AuthorityClass,
    BeliefState,
    UnauthorizedBeliefMutation,
)
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
    "COMPETING_HYPOTHESES",
    "HOSTILE_CONTROLS",
    "PROTOCOL_ID",
    "AuthorityClass",
    "BeliefState",
    "CausalCycle",
    "CauseConfusableBundle",
    "EpistemicAction",
    "HypothesisId",
    "InterventionOutcome",
    "InterventionSpec",
    "LicenseDecision",
    "ProbeCatalog",
    "ProbeSpec",
    "ProtectedGold",
    "PublicMemberView",
    "RefusalReason",
    "UnauthorizedBeliefMutation",
    "UnauthorizedMutationError",
    "apply_intervention",
    "apply_licensed_action",
    "apply_probe",
    "audit_matrix",
    "gold_leak",
    "known_answer_bundles",
    "live_campaign_status",
    "load_protocol",
    "protocol_sha256",
    "reproduce_v1",
    "request_action",
    "run_cycle",
    "run_hostile_controls",
    "select_discriminator",
    "write_receipt",
]
