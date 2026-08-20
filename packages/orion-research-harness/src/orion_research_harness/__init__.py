"""Local host-tool bridge for canonical ORION research runs."""

from .broker import (
    BrokerLLMProvider,
    BrokerRetrievalProvider,
    BrokerVerificationProvider,
    CapabilityBroker,
    HostCapabilityFailed,
    HostCapabilityRequired,
)
from .campaign_runner import initialize_campaign, run_campaign, run_campaign_cycle
from .donor_campaign import build_donor_campaign_manifest
from .protocol import CapabilityRequest, CapabilityResult
from .research_lane import run_research_lane
from .runner import run_problem
from .workspace import ResearchWorkspace

__all__ = [
    "BrokerLLMProvider",
    "BrokerRetrievalProvider",
    "BrokerVerificationProvider",
    "CapabilityBroker",
    "CapabilityRequest",
    "CapabilityResult",
    "HostCapabilityFailed",
    "HostCapabilityRequired",
    "ResearchWorkspace",
    "build_donor_campaign_manifest",
    "initialize_campaign",
    "run_campaign",
    "run_campaign_cycle",
    "run_problem",
    "run_research_lane",
]
