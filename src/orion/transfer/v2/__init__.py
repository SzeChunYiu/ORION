"""Content-addressed, fail-closed productionization of ORION transfer mechanics.

Everything in this package is local engineering infrastructure or a V2/future-study
hook. It does not mutate or authorize any frozen P1-P5 V1 publication protocol.
"""

from .bounded_epistemic_study import (
    BoundedEpistemicAtomStudy,
    ContractInteractionReport,
    ReachabilityDeltaReport,
    ReachabilityDeltaStatus,
    ReachabilityStatus,
    ReachabilityWitness,
    ResourceBound,
    analyze_contract_interaction,
    build_atom_study,
    build_reachability_witness,
    build_resource_bound,
    compare_reachability,
)
from .canonical import canonical_json, content_digest, verify_digest
from .failure_knowledge import (
    FailureApplicabilityStatus,
    FailureApplicationReport,
    FailureKnowledge,
    assess_failure_applicability,
    build_failure_knowledge,
)
from .manifest import validate_paper_v2_manifest
from .models import TransferReceipt, build_transfer_receipt
from .portfolio import PortfolioReceipt, build_portfolio, verify_portfolio_replay
from .registry import TransferRegistry

__all__ = [
    "BoundedEpistemicAtomStudy",
    "ContractInteractionReport",
    "FailureApplicabilityStatus",
    "FailureApplicationReport",
    "FailureKnowledge",
    "PortfolioReceipt",
    "ReachabilityDeltaReport",
    "ReachabilityDeltaStatus",
    "ReachabilityStatus",
    "ReachabilityWitness",
    "ResourceBound",
    "TransferReceipt",
    "TransferRegistry",
    "analyze_contract_interaction",
    "assess_failure_applicability",
    "build_atom_study",
    "build_failure_knowledge",
    "build_portfolio",
    "build_reachability_witness",
    "build_resource_bound",
    "build_transfer_receipt",
    "canonical_json",
    "compare_reachability",
    "content_digest",
    "validate_paper_v2_manifest",
    "verify_digest",
    "verify_portfolio_replay",
]
