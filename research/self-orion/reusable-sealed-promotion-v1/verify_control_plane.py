#!/usr/bin/env python3
"""Fail-closed verifier for the reusable sealed promotion control plane."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CONTROL_PATH = HERE / "CONTROL_PLANE.json"
PROTOCOL_PATH = HERE / "PROTOCOL.json"
FREEZE_PATH = HERE / "CURRENT_TREE_FREEZE_RECEIPT.json"


class ControlPlaneError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ControlPlaneError(f"cannot read {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ControlPlaneError(f"{path} must contain one JSON object")
    return raw


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ControlPlaneError(message)


def verify_frozen_source(receipt: dict[str, Any]) -> None:
    require(
        receipt.get("schema") == "ORION.SelfOrion.ReusableSealedCurrentTreeFreeze.v1",
        "unexpected freeze-receipt schema",
    )
    require(receipt.get("scientific_authority_delta") == "NONE", "freeze receipt grants authority")
    source_blobs = receipt.get("source_blobs")
    require(isinstance(source_blobs, dict) and source_blobs, "source_blobs must be nonempty")
    for relative, expected in sorted(source_blobs.items()):
        require(isinstance(relative, str) and isinstance(expected, str), "invalid source binding")
        path = REPO / relative
        require(path.is_file(), f"missing frozen source: {relative}")
        observed = git_blob_sha1(path)
        require(observed == expected, f"frozen source drift: {relative}: {observed} != {expected}")


def expected_campaign_config(control: dict[str, Any]) -> dict[str, Any]:
    campaign = control["campaign"]
    expected = {
        "schema": campaign["schema"],
        "protocol_id": control["protocol_id"],
        "campaign_id": campaign["campaign_id"],
        "alpha_total": campaign["alpha_total"],
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "subject_revision": campaign["subject_revision"],
        "initial_chain_digest": campaign["initial_chain_digest"],
        "identities": campaign["identities"],
        "formal_conformance_only": True,
    }
    for field in campaign["authority_fields"]:
        expected[field] = False
    return expected


def verify_campaign(campaign_path: Path, control: dict[str, Any]) -> None:
    config = load(campaign_path / "CAMPAIGN.json")
    require(config == expected_campaign_config(control), "campaign control plane differs from frozen config")

    lines = (campaign_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    require(all(line.strip() for line in lines), "blank campaign event line")
    events = [json.loads(line) for line in lines]
    campaign = control["campaign"]
    require(len(events) == campaign["event_count"], "unexpected campaign event count")
    require(
        [event.get("receipt_id") for event in events] == campaign["receipt_ids"],
        "receipt sequence differs from frozen conformance campaign",
    )
    require(
        [event.get("decision") for event in events] == campaign["event_decisions"],
        "decision sequence differs from frozen conformance campaign",
    )
    require(
        [event.get("disposition") for event in events] == campaign["event_dispositions"],
        "disposition sequence differs from frozen conformance campaign",
    )

    final = load(campaign_path / "FINAL_RECEIPT.json")
    summary = load(campaign_path / "CONFORMANCE_SUMMARY.json")
    require(final.get("formal_terminal") == campaign["formal_terminal"], "wrong final terminal")
    require(summary.get("formal_terminal") == campaign["formal_terminal"], "wrong summary terminal")
    require(summary.get("empirical_authority_delta") == "NONE", "summary grants empirical authority")
    require(
        summary.get("event_decisions") == campaign["event_decisions"],
        "summary decision sequence differs from frozen campaign",
    )


def verify(campaign_path: Path | None = None) -> str:
    control = load(CONTROL_PATH)
    protocol = load(PROTOCOL_PATH)
    receipt = load(FREEZE_PATH)

    require(
        control.get("schema") == "ORION.SelfOrion.ReusableSealedControlPlane.v1",
        "unexpected control-plane schema",
    )
    require(control.get("scientific_authority_delta") == "NONE", "control plane grants authority")
    require(protocol.get("protocol_id") == control.get("protocol_id"), "protocol identity mismatch")
    authority = protocol.get("authority")
    require(isinstance(authority, dict), "protocol authority block missing")
    for field in control["required_protocol_authority_false"]:
        require(authority.get(field) is False, f"protocol authority is not false: {field}")

    for name in control["forbidden_source_outputs"]:
        require(not (HERE / name).exists(), f"generated outcome committed in source packet: {name}")

    verify_frozen_source(receipt)
    if campaign_path is not None:
        verify_campaign(campaign_path, control)
    terminal = control["canonical_terminal"]
    require(
        terminal == "CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN",
        "unexpected canonical terminal",
    )
    return terminal


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", type=Path)
    args = parser.parse_args(argv)
    try:
        print(verify(args.campaign))
    except (ControlPlaneError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"CONTROL_PLANE_REJECTED: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
