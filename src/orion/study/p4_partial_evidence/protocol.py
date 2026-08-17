"""Load the frozen P4.partial-evidence-acquisition.v2 protocol. Outcome-blind."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FOLLOWUP_PROTOCOL_ID = "P4.partial-evidence-acquisition.v2"
FROZEN_P4_CAMPAIGN_ID = "P4.protected-authority.v2"

_REPO = Path(__file__).resolve().parents[4]
_ROOT = _REPO / "research" / "p4-partial-evidence-acquisition-v2"


def protocol_root() -> Path:
    return _ROOT


def load_followup_protocol() -> dict[str, Any]:
    protocol = json.loads((_ROOT / "PROTOCOL_V2.json").read_text(encoding="utf-8"))
    if protocol.get("protocol_id") != FOLLOWUP_PROTOCOL_ID:
        raise ValueError("follow-up protocol_id mismatch")
    if protocol.get("incremental_over_protocol") != FROZEN_P4_CAMPAIGN_ID:
        raise ValueError("follow-up must sit over frozen P4.protected-authority.v2")
    if protocol.get("outcome_accessed") is not False:
        raise ValueError("protocol must remain outcome-blind")
    if protocol.get("p4_v2_mutated") is not False:
        raise ValueError("frozen P4 V2 must not be mutated")
    gold = json.loads((_ROOT / "GOLD_V2.json").read_text(encoding="utf-8"))
    envelope = json.loads((_ROOT / "COST_ENVELOPE_V2.json").read_text(encoding="utf-8"))
    merged = dict(protocol)
    merged["gold"] = gold
    merged["cost_envelope"] = envelope
    return merged
