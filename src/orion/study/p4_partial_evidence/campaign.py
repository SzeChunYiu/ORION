"""Campaign status for P4.partial-evidence-acquisition.v2. Fail closed without a host."""

from __future__ import annotations

import os
from typing import Any

from .protocol import FOLLOWUP_PROTOCOL_ID, FROZEN_P4_CAMPAIGN_ID

_HOST_ENV = "ORION_P4_PARTIAL_EVIDENCE_PROTECTED_HOST"


def detect_protected_host() -> bool:
    return os.environ.get(_HOST_ENV, "").strip() == "1"


def campaign_status() -> dict[str, Any]:
    if detect_protected_host():
        return {
            "protocol_id": FOLLOWUP_PROTOCOL_ID,
            "frozen_campaign_id": FROZEN_P4_CAMPAIGN_ID,
            "status": "HOST_DECLARED",
            "reason": "protected_host_env_set_but_campaign_not_executed",
            "p4_v2_readiness": "PEER_REVIEW_READY",
            "remaining_cannot_check": [
                "fresh_secret_seeded_protected_split",
                "matched_baselines_and_ablations_execution",
                "headline_acquisition_experiment",
            ],
        }
    return {
        "protocol_id": FOLLOWUP_PROTOCOL_ID,
        "frozen_campaign_id": FROZEN_P4_CAMPAIGN_ID,
        "status": "CANNOT_CHECK",
        "reason": "protected_host_evaluator_unavailable",
        "p4_v2_readiness": "PEER_REVIEW_READY",
        "remaining_cannot_check": [
            "fresh_secret_seeded_protected_split",
            "matched_baselines_and_ablations_execution",
            "headline_acquisition_experiment",
            "independent_red_team_via_issue_283",
            "followup_scientific_terminal",
        ],
    }
