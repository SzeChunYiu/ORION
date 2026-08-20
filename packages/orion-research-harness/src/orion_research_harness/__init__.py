"""Replayable host-tool and scientific-campaign bridge for canonical ORION."""

from .broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .campaign_control import decide_campaign, validate_manifest
from .campaign_protocol import CampaignDecision, CampaignState, CampaignTransition, ProtectedReference
from .campaign_runner import initialize_campaign, run_campaign, run_campaign_cycle
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
    "decide_campaign",
    "initialize_campaign",
    "run_campaign",
    "run_campaign_cycle",
    "run_problem",
    "validate_manifest",
]
