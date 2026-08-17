"""Live campaign gate. Missing credentials are CANNOT_CHECK, never a zero."""

from __future__ import annotations

import os
from dataclasses import dataclass

CREDENTIAL_ENV_VAR = "ANTHROPIC_API_KEY"


@dataclass(frozen=True)
class CampaignStatus:
    status: str
    reason: str
    credential_present: bool

    def to_payload(self) -> dict:
        return {
            "status": self.status,
            "reason": self.reason,
            "credential_present": self.credential_present,
            "env_var": CREDENTIAL_ENV_VAR,
        }


def live_campaign_status() -> CampaignStatus:
    present = bool(os.environ.get(CREDENTIAL_ENV_VAR))
    if not present:
        return CampaignStatus(
            status="CANNOT_CHECK",
            reason=(
                "ANTHROPIC_API_KEY is unset; the prospective V2 campaign, "
                "matched baselines, and held-out experiment cannot run"
            ),
            credential_present=False,
        )
    return CampaignStatus(
        status="NOT_STARTED",
        reason="credential present but this session does not launch a live campaign",
        credential_present=True,
    )
