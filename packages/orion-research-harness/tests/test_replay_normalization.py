from __future__ import annotations

from pathlib import Path

from orion_research_harness.workspace import ResearchWorkspace


def test_request_replay_accepts_json_equivalent_payload_shapes(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)

    first = workspace.get_or_create_request(
        capability="CUSTOM",
        payload={1: ("a", "b")},
    )
    replay = workspace.get_or_create_request(
        capability="CUSTOM",
        payload={"1": ["a", "b"]},
    )

    assert replay.request_id == first.request_id
    assert replay.request_digest == first.request_digest


def test_result_replay_accepts_json_equivalent_output_shapes(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    request = workspace.get_or_create_request(capability="CUSTOM", payload={"x": 1})

    first = workspace.ingest_result(
        request.request_id,
        success=True,
        output={1: ("a", "b")},
        executor="host",
    )
    replay = workspace.ingest_result(
        request.request_id,
        success=True,
        output={"1": ["a", "b"]},
        executor="host",
    )

    assert replay.result_digest == first.result_digest


def test_campaign_manifest_replay_accepts_json_equivalent_shapes(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)

    first = workspace.save_campaign_manifest(
        "campaign:test",
        {"campaign_id": "campaign:test", "nested": {1: ("a", "b")}},
    )
    replay = workspace.save_campaign_manifest(
        "campaign:test",
        {"campaign_id": "campaign:test", "nested": {"1": ["a", "b"]}},
    )

    assert replay == first


def test_campaign_state_and_cycle_replay_accept_json_equivalent_shapes(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)

    state_a = {
        "campaign_id": "campaign:test",
        "cycle_index": 0,
        "nested": {1: ("a", "b")},
    }
    state_b = {
        "campaign_id": "campaign:test",
        "cycle_index": 0,
        "nested": {"1": ["a", "b"]},
    }
    assert workspace.save_campaign_state("campaign:test", state_a) == workspace.save_campaign_state(
        "campaign:test", state_b
    )

    cycle_a = {
        "campaign_id": "campaign:test",
        "cycle_index": 0,
        "nested": {1: ("a", "b")},
    }
    cycle_b = {
        "campaign_id": "campaign:test",
        "cycle_index": 0,
        "nested": {"1": ["a", "b"]},
    }
    assert workspace.save_campaign_cycle("campaign:test", cycle_a) == workspace.save_campaign_cycle(
        "campaign:test", cycle_b
    )
