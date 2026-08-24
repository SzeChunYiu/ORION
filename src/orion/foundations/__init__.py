"""Finite, falsifiable foundations for auditable scientific transitions."""

from .capability import (
    DiagnosticModel,
    ExpansionCertificate,
    MethodLanguage,
    MethodRule,
    ObstructionCertificate,
    PlacementLaw,
    ResponsibilityModel,
)
from .discharge import (
    DecisionExplanation,
    DischargeRule,
    NormalFormCertificate,
    TransitionContract,
    decide_transition,
    least_closure,
)
from .integrity import EvolutionCertificate
from .model import (
    Artifact,
    BridgeRule,
    Event,
    EventKind,
    ExecutionIntegrity,
    Judgment,
    Obligation,
    ObligationStatus,
    ResourceVector,
    Responsibility,
    ScientificObject,
    ScientificState,
    SupportFamily,
    Terminal,
)
from .sufficiency import FiniteInterface
from .theorems import TheoremResult, run_local_theorems

__all__ = [
    "Artifact",
    "BridgeRule",
    "DecisionExplanation",
    "DiagnosticModel",
    "DischargeRule",
    "Event",
    "EventKind",
    "EvolutionCertificate",
    "ExecutionIntegrity",
    "ExpansionCertificate",
    "FiniteInterface",
    "Judgment",
    "MethodLanguage",
    "MethodRule",
    "NormalFormCertificate",
    "Obligation",
    "ObligationStatus",
    "ObstructionCertificate",
    "PlacementLaw",
    "ResourceVector",
    "Responsibility",
    "ResponsibilityModel",
    "ScientificObject",
    "ScientificState",
    "SupportFamily",
    "Terminal",
    "TheoremResult",
    "TransitionContract",
    "decide_transition",
    "least_closure",
    "run_local_theorems",
]
