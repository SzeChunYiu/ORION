#!/usr/bin/env python3
"""Fail-closed static checker for the P14 external blinded evaluation contract."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET = HERE / "P14_EXTERNAL_PACKET_SCHEMA_V1.json"
DECISION = HERE / "P14_EXTERNAL_DECISION_SCHEMA_V1.json"
PROTOCOL = HERE / "P14_EXTERNAL_GOVERNANCE_PROTOCOL_V1.md"
FRONTIER = HERE / "P14_EXTERNAL_FRONTIER_DELTA_2026-08-23.md"

FORBIDDEN_PACKET_FIELDS = {
    "gold_disposition",
    "gold_claim",
    "gold_novelty",
    "orion_expected_disposition",
    "correct_answer",
    "expected_terminal",
}


def walk_property_names(node):
    if isinstance(node, dict):
        props = node.get("properties")
        if isinstance(props, dict):
            for key, value in props.items():
                yield key
                yield from walk_property_names(value)
        for key, value in node.items():
            if key != "properties":
                yield from walk_property_names(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_property_names(value)


def main() -> int:
    packet = json.loads(PACKET.read_text())
    decision = json.loads(DECISION.read_text())
    protocol = PROTOCOL.read_text()
    frontier = FRONTIER.read_text()

    assert packet["additionalProperties"] is False
    assert decision["additionalProperties"] is False
    assert packet["properties"]["gold_record_digest"]["type"] == "string"
    packet_fields = set(walk_property_names(packet))
    assert not (packet_fields & FORBIDDEN_PACKET_FIELDS), packet_fields & FORBIDDEN_PACKET_FIELDS

    dispositions = set(decision["properties"]["disposition"]["enum"])
    required_dispositions = {
        "PROMOTE", "SUBSUMED", "INTERACTION_ONLY", "NEGATIVE", "NULL_LIVE",
        "NON_IDENTIFIABLE", "CANNOT_CHECK", "REOPEN", "STOP",
    }
    assert dispositions == required_dispositions

    authority = set(decision["properties"]["authority_status"]["enum"])
    assert authority == {"NOT_AUTHORITY", "CANNOT_CHECK", "EXTERNALLY_AUTHORIZED"}

    for marker in (
        "same evidence bytes",
        ">=60 protected packets",
        ">=3 domains",
        "useful-discovery",
        "original paper authors",
        "may not grade its own",
        "Layer A",
        "Layer B",
    ):
        assert marker.lower() in protocol.lower(), marker

    for donor_marker in (
        "PaperBench",
        "ReplicatorBench",
        "AutoResearchBench",
        "Shadow evaluations",
        "Robin",
        "Co-Scientist",
        "The AI Scientist",
    ):
        assert donor_marker.lower() in frontier.lower(), donor_marker

    # A minimal packet fixture proves that hidden gold is represented only by digest.
    fixture = {
        "schema_version": "P14_EXTERNAL_PACKET_V1",
        "packet_id": "fixture-0001",
        "domain": "test-domain",
        "question": "What claim is supported?",
        "visible_evidence": [{
            "artifact_id": "e1",
            "sha256": "0" * 64,
            "role": "PRIMARY",
            "content_location": "fixture://e1",
        }],
        "allowed_tools": ["search"],
        "resource_budget": {"tool_calls": 10},
        "claim_language": {"max_scope": "fixture", "forbidden_promotions": []},
        "preregistered_decision_points": ["final disposition"],
        "gold_record_digest": "1" * 64,
    }
    assert not (set(fixture) & FORBIDDEN_PACKET_FIELDS)
    assert fixture["gold_record_digest"] and "gold_disposition" not in fixture

    print("P14_EXTERNAL_GOVERNANCE_CONTRACT_V1_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
