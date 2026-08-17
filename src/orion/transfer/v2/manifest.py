from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .canonical import content_digest

MANIFEST_VERSION = "ORION_PAPER_V2_MANIFEST_V1"
PAPER_IDS = {f"ORION-P{index}" for index in range(1, 6)}
ADOPTION_CLASSES = {"V2_CANDIDATE", "EXPLORATORY_V2", "PERFORMANCE_HELPER"}


def validate_paper_v2_manifest(payload: Mapping[str, object]) -> str:
    required = {
        "manifest_version",
        "paper_id",
        "mechanism_id",
        "status",
        "adoption_class",
        "outcome_accessed",
        "execution_authority",
        "v1_protocol_mutated",
        "local_evidence_authority",
        "requires_new_protocol_version",
        "source_issue",
        "module",
        "preconditions_for_execution_freeze",
    }
    if set(payload) != required:
        raise ValueError(f"paper V2 manifest fields mismatch: {sorted(set(payload) ^ required)}")
    if payload["manifest_version"] != MANIFEST_VERSION:
        raise ValueError("unsupported paper V2 manifest version")
    if payload["paper_id"] not in PAPER_IDS:
        raise ValueError("unknown paper_id")
    if not isinstance(payload["mechanism_id"], str) or not payload["mechanism_id"]:
        raise ValueError("mechanism_id must be non-empty")
    if payload["status"] != "V2_FUTURE_STUDY":
        raise ValueError("paper V2 manifest must remain V2_FUTURE_STUDY")
    if payload["adoption_class"] not in ADOPTION_CLASSES:
        raise ValueError("invalid adoption_class")
    if payload["outcome_accessed"] is not False:
        raise ValueError("V2 manifest cannot claim outcome access")
    if payload["execution_authority"] != "NONE":
        raise ValueError("V2 manifest has no execution authority")
    if payload["v1_protocol_mutated"] is not False:
        raise ValueError("V2 manifest may not mutate V1 protocol")
    if payload["local_evidence_authority"] != "LOCAL_ENGINEERING_ONLY":
        raise ValueError("V2 manifest local evidence authority must be LOCAL_ENGINEERING_ONLY")
    if payload["requires_new_protocol_version"] is not True:
        raise ValueError("V2 execution requires a new protocol version")
    issue = payload["source_issue"]
    if not isinstance(issue, int) or issue <= 0:
        raise ValueError("source_issue must be a positive integer")
    module = payload["module"]
    if not isinstance(module, str) or not module.startswith("orion.transfer.v2."):
        raise ValueError("module must point to an orion.transfer.v2 integration")
    preconditions = payload["preconditions_for_execution_freeze"]
    if not isinstance(preconditions, list) or not preconditions or not all(isinstance(item, str) and item for item in preconditions):
        raise ValueError("preconditions_for_execution_freeze must be a non-empty string list")
    return content_digest(payload)


def load_and_validate_manifest(path: str | Path) -> tuple[dict[str, object], str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("paper V2 manifest root must be an object")
    return payload, validate_paper_v2_manifest(payload)
