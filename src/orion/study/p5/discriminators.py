"""Frozen adjacent-level discriminators for the three GLM-5.2 attribution errors.

Each discriminator is evidence, not a repair license. A method change remains
unauthorized until lower-level causes are ruled out under P5.causal-repair.v2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from orion.study.p5.attribution_receipt import IMMUTABLE_RESIDUAL_ERRORS


DISCRIMINATOR_PROTOCOL_ID = "P5.causal-discriminators.v1"
REQUIRED_ERROR_IDS = ("P5-HC-002", "P5-HC-012", "P5-HC-018")


def load_frozen_discriminators(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("discriminator freeze must be a JSON object")
    return dict(payload)


def validate_discriminator_freeze(payload: Mapping[str, Any]) -> None:
    if payload.get("protocol_id") != DISCRIMINATOR_PROTOCOL_ID:
        raise ValueError(f"protocol_id must be {DISCRIMINATOR_PROTOCOL_ID}")
    if payload.get("authorizes_method_change") is not False:
        raise ValueError("discriminator freeze must not license a method change")
    if payload.get("outcome_accessed") is not False:
        raise ValueError("discriminator freeze must precede repair outcomes")
    if payload.get("empirical_authority") != "CANNOT_CHECK":
        raise ValueError("discriminator freeze cannot raise empirical authority")
    discriminators = payload.get("discriminators")
    if not isinstance(discriminators, list) or len(discriminators) != 3:
        raise ValueError("exactly three error discriminators are required")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(discriminators):
        if not isinstance(raw, Mapping):
            raise ValueError(f"discriminators[{index}] must be an object")
        if raw.get("authorizes_method_change") is not False:
            raise ValueError("a discriminator must not license a method change")
        error_id = raw.get("error_id")
        if error_id in by_id:
            raise ValueError(f"duplicate discriminator error_id: {error_id}")
        by_id[str(error_id)] = raw
    if tuple(by_id) != REQUIRED_ERROR_IDS:
        raise ValueError("discriminator freeze must preserve P5-HC-002/012/018 in order")
    expected = {item["case_id"]: item for item in IMMUTABLE_RESIDUAL_ERRORS}
    for error_id, entry in by_id.items():
        seed = expected[error_id]
        if entry.get("gold") != seed["gold"] or entry.get("observed_attribution") != seed["attributed"]:
            raise ValueError(f"{error_id} must preserve the immutable gold/attribution pair")
