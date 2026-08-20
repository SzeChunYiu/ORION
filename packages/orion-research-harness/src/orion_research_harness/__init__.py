"""Replayable host-tool, canonical-mechanics and scientific-campaign bridge for ORION."""

from .broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .campaign_control import decide_campaign, validate_manifest
from .campaign_protocol import (
    CampaignDecision,
    CampaignState,
    CampaignTransition,
    ProtectedReference,
)
from .campaign_runner import initialize_campaign, run_campaign, run_campaign_cycle
from .mechanics_bridge import (
    atom_calculus_surface,
    compile_workspace_development_fibre,
    mechanic_catalog,
    mechanic_detail,
    mechanics_coverage,
    method_fibre_surface,
    navigate_mechanics,
    rank_workspace_development_fibres,
    run_mechanic_receipts,
    saturation_surface,
)
from .protocol import CapabilityRequest, CapabilityResult
from .runner import run_problem
from .workspace import ResearchWorkspace

__all__ = [
    "BrokerLLMProvider",
    "BrokerRetrievalProvider",
    "BrokerVerificationProvider",
    "CampaignDecision",
    "CampaignState",
    "CampaignTransition",
    "CapabilityBroker",
    "CapabilityRequest",
    "CapabilityResult",
    "HostCapabilityFailed",
    "HostCapabilityRequired",
    "ProtectedReference",
    "ResearchWorkspace",
    "atom_calculus_surface",
    "compile_workspace_development_fibre",
    "decide_campaign",
    "initialize_campaign",
    "mechanic_catalog",
    "mechanic_detail",
    "mechanics_coverage",
    "method_fibre_surface",
    "navigate_mechanics",
    "rank_workspace_development_fibres",
    "run_campaign",
    "run_campaign_cycle",
    "run_mechanic_receipts",
    "run_problem",
    "saturation_surface",
    "validate_manifest",
]
