from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionModality(str, Enum):
    MECHANICAL_REQUIRED = "MECHANICAL_REQUIRED"
    MECHANICAL_PREFERRED = "MECHANICAL_PREFERRED"
    HYBRID_SEMANTIC = "HYBRID_SEMANTIC"
    EXTERNAL_SOLVER = "EXTERNAL_SOLVER"
    LLM_PROPOSAL = "LLM_PROPOSAL"


@dataclass(frozen=True)
class CapabilityRoute:
    mechanic_id: str
    modality: ExecutionModality
    rationale: str
    llm_authority: str
    fallback: str

    def __post_init__(self) -> None:
        if any(not value.strip() for value in (self.mechanic_id, self.rationale, self.llm_authority, self.fallback)):
            raise ValueError("capability route requires identity/rationale/authority/fallback")


_MECHANICAL_REQUIRED_PREFIXES = (
    "REOPEN.",
    "SATURATE.",
    "CROSS.AUTHORITY",
    "CROSS.EXPERIENCE",
    "CROSS.EXECUTION",
    "CROSS.MEMORY",
    "CROSS.CONTEXT_POLICY",
)

_MECHANICAL_PREFERRED_PREFIXES = (
    "FRAME.",
    "SEARCH.ROUTE",
    "SEARCH.ROUTE_STOP",
    "SEARCH.RETRIEVE",
    "DETECT.COVERAGE",
    "DETECT.FAILURE",
    "DIAGNOSE.EXPERIENCE_RETRIEVAL",
    "RECONSTRUCT.SEARCH_UNIVERSE",
)

_HYBRID_SEMANTIC_PREFIXES = (
    "ABSORB.SCIENTIFIC_LANGUAGE",
    "ABSORB.CLAIM",
    "ABSORB.REFERENCE_IDENTITY",
    "ABSORB.CONTEXT",
    "ABSORB.REPRESENTATION_MAP",
    "RECONSTRUCT.ATLAS_UPDATE",
    "RECONSTRUCT.GLUE",
    "RECONSTRUCT.PORTRAIT",
    "DETECT.CONTRADICTION",
    "DETECT.GAP",
    "DIAGNOSE.HYPOTHESES",
    "DIAGNOSE.DISCRIMINATOR",
    "DIAGNOSE.ATTRIBUTION",
)

_LLM_PROPOSAL_PREFIXES = (
    "REFRAME.REPRESENTATION",
    "REFRAME.DECOMPOSITION",
    "REFRAME.SEARCH_POLICY",
    "REFRAME.METHOD",
    "REFRAME.OBJECTIVE",
)


def route_capability(mechanic_id: str) -> CapabilityRoute:
    """Choose the least-authoritative capable execution modality.

    The rule is architectural: if a typed deterministic mechanic can discharge the
    operation, ORION uses it before consulting an LLM. LLM output remains a proposal
    even when it is the most useful semantic generator.
    """

    if any(mechanic_id.startswith(prefix) for prefix in _MECHANICAL_REQUIRED_PREFIXES):
        return CapabilityRoute(
            mechanic_id,
            ExecutionModality.MECHANICAL_REQUIRED,
            "The operation governs authority, persistence, replay, reopening, saturation or other protected state and therefore must be executed by typed mechanics once inputs are available.",
            "LLM may explain/propose inputs but may not decide or mutate the protected transition.",
            "Return BLOCKED/CANNOT_CHECK when the mechanical preconditions or required inputs are unavailable.",
        )
    if any(mechanic_id.startswith(prefix) for prefix in _MECHANICAL_PREFERRED_PREFIXES):
        return CapabilityRoute(
            mechanic_id,
            ExecutionModality.MECHANICAL_PREFERRED,
            "The operation has an inspectable algorithmic/graph/control formulation; use that path whenever its typed inputs are available.",
            "LLM may suggest candidates or labels but cannot replace the deterministic controller's decision semantics.",
            "Use a proposal worker only for the missing semantic input, then return to the mechanical mechanic.",
        )
    if any(mechanic_id.startswith(prefix) for prefix in _HYBRID_SEMANTIC_PREFIXES):
        return CapabilityRoute(
            mechanic_id,
            ExecutionModality.HYBRID_SEMANTIC,
            "The operation contains open-ended language/meaning/identity/causal interpretation but also has typed output, provenance and verification contracts.",
            "LLM/NLP output is candidate structure only; exact source selectors, typed constraints and verification determine retained knowledge/authority.",
            "Prefer deterministic parsers/identifiers/formal solvers for subproblems they can discharge; otherwise use a semantic proposal provider.",
        )
    if any(mechanic_id.startswith(prefix) for prefix in _LLM_PROPOSAL_PREFIXES):
        return CapabilityRoute(
            mechanic_id,
            ExecutionModality.LLM_PROPOSAL,
            "Open-ended restructuring/invention benefits from generative search, but the candidate must remain proposal-only.",
            "LLM can generate candidate reframes; it cannot authorize adoption, evaluation criteria changes or scientific authority.",
            "If no semantic generator is available, enumerate mechanical/local alternatives or return CANNOT_CHECK rather than invent hidden changes.",
        )
    return CapabilityRoute(
        mechanic_id,
        ExecutionModality.MECHANICAL_PREFERRED,
        "Unknown/new mechanics default toward inspectable typed execution rather than unconstrained model control.",
        "LLM is supplemental proposal machinery only.",
        "Open a capability/mechanic residual when no executable path is registered.",
    )


class CapabilityRouter:
    def route(self, mechanic_id: str) -> CapabilityRoute:
        return route_capability(mechanic_id)
