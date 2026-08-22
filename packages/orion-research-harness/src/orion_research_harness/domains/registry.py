from __future__ import annotations

from typing import Any, Mapping

from .orion_q import MAX_R6_CAMPAIGN_MANIFEST
from .orion_q.post_r6o_diagnosis import POST_R6O_DIAGNOSIS_CAMPAIGN_MANIFEST
from .orion_rg import (
    X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST,
    X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST,
    X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST,
)

_BUILTINS = {
    str(MAX_R6_CAMPAIGN_MANIFEST["campaign_id"]): MAX_R6_CAMPAIGN_MANIFEST,
    str(
        POST_R6O_DIAGNOSIS_CAMPAIGN_MANIFEST["campaign_id"]
    ): POST_R6O_DIAGNOSIS_CAMPAIGN_MANIFEST,
    str(X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST["campaign_id"]): X1A_DAVENPORT_3_5_CAMPAIGN_MANIFEST,
    str(X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST["campaign_id"]): X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST,
    str(X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST["campaign_id"]): X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST,
}


def builtin_campaign_ids() -> tuple[str, ...]:
    return tuple(sorted(_BUILTINS))


def load_builtin_campaign(campaign_id: str) -> Mapping[str, Any]:
    try:
        return _BUILTINS[str(campaign_id)]
    except KeyError as exc:
        raise KeyError(f"unknown built-in research campaign: {campaign_id}") from exc
