#!/usr/bin/env python3
"""Validate externally authored A3 curator packets without creating judgments.

The validator binds each packet to the durable 128-family WorkflowHub successor
frame and rejects prediction-visible, source-mismatched, or malformed custody
records. It does not infer a stratum or REUSE/REOPEN/CANNOT_CHECK target.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SNAPSHOT = HERE / "workflowhub-normalized-content-binding-v2" / "SNAPSHOT_V2.json"
SUCCESSOR = HERE / "workflowhub-two-replacement-successor-v1" / "RESULT_V1.json"
EXPECTED_SUCCESSOR_FRAME_SHA256 = "a47d9255aa37de056cb5cdd7c140bcccb487aa3285790655a48abb5e538c2993"
EXPECTED_BASE_SELECTED_ROWS_SHA256 = "2f36f8d5900c904d939e87f7c582281e27445f4045d520754b7b11dcbbc3b882"
STRATA = {
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
}
TARGETS = {"REUSE", "REOPEN", "CANNOT_CHECK"}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def require_hex64(value: Any, label: str) -> str:
    value = require_nonempty(value, label)
    if not HEX64.fullmatch(value):
        raise ValueError(f"{label} must be lowercase SHA-256 hex")
    return value


def load_source_frame() -> dict[str, dict[str, Any]]:
    manifest = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if manifest.get("schema") != "ORION.A3.WorkflowHubNormalizedContentBindingDurableSnapshot.v2":
        raise ValueError("normalized snapshot schema mismatch")
    if manifest.get("selected_rows_sha256") != EXPECTED_BASE_SELECTED_ROWS_SHA256:
        raise ValueError("normalized snapshot selected-row digest mismatch")
    rows: list[dict[str, Any]] = []
    for chunk in manifest["chunks"]:
        path = ROOT / chunk["path"]
        raw = path.read_bytes()
        if sha256_bytes(raw) != chunk["sha256"]:
            raise ValueError(f"normalized snapshot chunk hash mismatch: {chunk['path']}")
        payload = json.loads(raw)
        chunk_rows = payload.get("rows")
        if not isinstance(chunk_rows, list) or len(chunk_rows) != chunk["rows"]:
            raise ValueError(f"normalized snapshot chunk row mismatch: {chunk['path']}")
        rows.extend(chunk_rows)
    retained: dict[str, dict[str, Any]] = {}
    for row in rows:
        wid = str(row["workflow_id"])
        if row.get("status") == "NORMALIZED_CONTENT_BOUND_DIFFERENT":
            retained[wid] = row
    if len(retained) != 126 or set(manifest.get("cannot_check_workflow_ids", [])) != {"402", "444"}:
        raise ValueError("normalized 126/2 source-frame boundary mismatch")

    successor = json.loads(SUCCESSOR.read_text(encoding="utf-8"))
    if successor.get("schema") != "ORION.A3.WorkflowHubTwoReplacementSuccessorDurableResult.v1":
        raise ValueError("successor result schema mismatch")
    if successor.get("terminal") != "WORKFLOWHUB_TWO_REPLACEMENT_SUCCESSOR_CONTENT_BOUND":
        raise ValueError("successor result is not content-bound")
    if successor.get("successor_frame_sha256") != EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("successor frame digest mismatch")
    if successor.get("base", {}).get("base_normalized_selected_rows_sha256") != EXPECTED_BASE_SELECTED_ROWS_SHA256:
        raise ValueError("successor does not bind expected normalized base")
    for row in successor.get("replacements", []):
        wid = str(row["workflow_id"])
        if wid in retained:
            raise ValueError(f"replacement collides with retained source family: {wid}")
        retained[wid] = {
            "workflow_id": wid,
            "version_before": row["version_before"],
            "version_after": row["version_after"],
            "license_before": row["license_before"],
            "license_after": row["license_after"],
            "before_normalized_sha256": row["before_normalized_sha256"],
            "after_normalized_sha256": row["after_normalized_sha256"],
            "status": row["status"],
        }
    if len(retained) != 128 or len(set(retained)) != 128:
        raise ValueError("successor source frame is not 128 unique families")
    return retained


def validate_source(source: dict[str, Any], source_frame: dict[str, dict[str, Any]]) -> None:
    wid = require_nonempty(source.get("workflow_id"), "source.workflow_id")
    if wid not in source_frame:
        raise ValueError(f"workflow {wid} is not in the frozen 128-family successor frame")
    expected = source_frame[wid]
    exact_fields = {
        "version_before": expected["version_before"],
        "version_after": expected["version_after"],
        "license_before": expected["license_before"],
        "license_after": expected["license_after"],
        "before_normalized_sha256": expected["before_normalized_sha256"],
        "after_normalized_sha256": expected["after_normalized_sha256"],
    }
    for key, expected_value in exact_fields.items():
        if source.get(key) != expected_value:
            raise ValueError(f"source.{key} does not match frozen source receipt for workflow {wid}")
    if source["before_normalized_sha256"] == source["after_normalized_sha256"]:
        raise ValueError("source normalized content hashes must differ")


def validate_packet(packet: dict[str, Any], source_frame: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    if source_frame is None:
        source_frame = load_source_frame()
    if packet.get("schema") != "ORION.A3.ExternalCuratorAdjudicationPacket.v1":
        raise ValueError("packet schema mismatch")
    if packet.get("source_frame_sha256") != EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("packet source_frame_sha256 mismatch")
    cluster_id = require_nonempty(packet.get("cluster_id"), "cluster_id")
    source = packet.get("source")
    if not isinstance(source, dict):
        raise ValueError("source must be an object")
    validate_source(source, source_frame)

    lineage = packet.get("lineage")
    if not isinstance(lineage, dict):
        raise ValueError("lineage must be an object")
    for key in ("source_family_id", "normalized_organization_lineage", "artifact_lineage_id"):
        require_nonempty(lineage.get(key), f"lineage.{key}")
    require_hex64(packet.get("candidate_visible_packet_sha256"), "candidate_visible_packet_sha256")

    adjudication = packet.get("adjudication")
    if not isinstance(adjudication, dict):
        raise ValueError("adjudication must be an object")
    stratum = adjudication.get("stratum")
    target = adjudication.get("target")
    if stratum not in STRATA:
        raise ValueError(f"invalid adjudication stratum: {stratum!r}")
    if target not in TARGETS:
        raise ValueError(f"invalid adjudication target: {target!r}")
    require_nonempty(adjudication.get("rationale"), "adjudication.rationale")
    evidence_refs = adjudication.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise ValueError("adjudication.evidence_refs must be a non-empty list")
    for i, ref in enumerate(evidence_refs):
        require_nonempty(ref, f"adjudication.evidence_refs[{i}]")
    disagreement = adjudication.get("disagreement_record")
    if not isinstance(disagreement, dict) or not isinstance(disagreement.get("disagreement_observed"), bool):
        raise ValueError("adjudication.disagreement_record must explicitly record disagreement_observed")
    notes = require_nonempty(disagreement.get("notes"), "adjudication.disagreement_record.notes")
    resolution = disagreement.get("resolution")
    if disagreement["disagreement_observed"]:
        require_nonempty(resolution, "adjudication.disagreement_record.resolution")
    elif resolution not in (None, ""):
        raise ValueError("resolution must be null/empty when no disagreement was observed")
    del notes

    receipt = packet.get("curator_receipt")
    if not isinstance(receipt, dict):
        raise ValueError("curator_receipt must be an object")
    require_nonempty(receipt.get("curator_id"), "curator_receipt.curator_id")
    require_nonempty(receipt.get("adjudicated_at_utc"), "curator_receipt.adjudicated_at_utc")
    require_hex64(receipt.get("receipt_sha256"), "curator_receipt.receipt_sha256")
    required_true = ("independence_attested", "adjudication_started_before_prediction_reveal")
    for key in required_true:
        if receipt.get(key) is not True:
            raise ValueError(f"curator_receipt.{key} must be true")
    required_false = ("orion_predictions_visible", "baseline_predictions_visible", "protected_outcomes_visible")
    for key in required_false:
        if receipt.get(key) is not False:
            raise ValueError(f"curator_receipt.{key} must be false")

    if packet.get("candidate_predictions_in_packet") is not False:
        raise ValueError("candidate_predictions_in_packet must be false")
    if packet.get("baseline_predictions_in_packet") is not False:
        raise ValueError("baseline_predictions_in_packet must be false")
    if packet.get("protected_outcomes_in_packet") is not False:
        raise ValueError("protected_outcomes_in_packet must be false")
    return {"cluster_id": cluster_id, "workflow_id": source["workflow_id"], "stratum": stratum, "target": target}


def validate_packets(packets: list[dict[str, Any]]) -> dict[str, Any]:
    source_frame = load_source_frame()
    summaries = [validate_packet(packet, source_frame) for packet in packets]
    cluster_ids = [row["cluster_id"] for row in summaries]
    if len(cluster_ids) != len(set(cluster_ids)):
        raise ValueError("duplicate cluster_id across curator packets")
    return {
        "schema": "ORION.A3.ExternalCuratorPacketValidationResult.v1",
        "packet_n": len(summaries),
        "source_frame_n": len(source_frame),
        "source_frame_sha256": EXPECTED_SUCCESSOR_FRAME_SHA256,
        "packets": summaries,
        "scientific_authority_delta": "NONE__CUSTODY_VALIDATION_ONLY",
    }


def synthetic_packet(source_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "ORION.A3.ExternalCuratorAdjudicationPacket.v1",
        "source_frame_sha256": EXPECTED_SUCCESSOR_FRAME_SHA256,
        "cluster_id": "synthetic-self-test-cluster",
        "source": {
            "workflow_id": source_row["workflow_id"],
            "version_before": source_row["version_before"],
            "version_after": source_row["version_after"],
            "license_before": source_row["license_before"],
            "license_after": source_row["license_after"],
            "before_normalized_sha256": source_row["before_normalized_sha256"],
            "after_normalized_sha256": source_row["after_normalized_sha256"],
        },
        "lineage": {
            "source_family_id": f"workflowhub:{source_row['workflow_id']}",
            "normalized_organization_lineage": "synthetic-org-lineage",
            "artifact_lineage_id": "synthetic-artifact-lineage",
        },
        "candidate_visible_packet_sha256": "1" * 64,
        "adjudication": {
            "stratum": "representation_schema",
            "target": "CANNOT_CHECK",
            "rationale": "Synthetic validator self-test only; not a scientific judgment.",
            "evidence_refs": ["synthetic:evidence:1"],
            "disagreement_record": {"disagreement_observed": False, "resolution": None, "notes": "Synthetic no-disagreement control."},
        },
        "curator_receipt": {
            "curator_id": "synthetic-self-test-curator",
            "adjudicated_at_utc": "2099-01-01T00:00:00Z",
            "receipt_sha256": "2" * 64,
            "independence_attested": True,
            "adjudication_started_before_prediction_reveal": True,
            "orion_predictions_visible": False,
            "baseline_predictions_visible": False,
            "protected_outcomes_visible": False,
        },
        "candidate_predictions_in_packet": False,
        "baseline_predictions_in_packet": False,
        "protected_outcomes_in_packet": False,
    }


def expect_reject(packet: dict[str, Any], source_frame: dict[str, dict[str, Any]]) -> None:
    try:
        validate_packet(packet, source_frame)
    except ValueError:
        return
    raise AssertionError("hostile curator packet was accepted")


def self_test() -> dict[str, Any]:
    source_frame = load_source_frame()
    first = source_frame[sorted(source_frame, key=lambda x: (int(x) if x.isdigit() else 10**18, x))[0]]
    good = synthetic_packet(first)
    validate_packet(good, source_frame)

    bad_hash = copy.deepcopy(good)
    bad_hash["source"]["before_normalized_sha256"] = "0" * 64
    expect_reject(bad_hash, source_frame)
    bad_target = copy.deepcopy(good)
    bad_target["adjudication"]["target"] = "MAYBE"
    expect_reject(bad_target, source_frame)
    exposed = copy.deepcopy(good)
    exposed["curator_receipt"]["orion_predictions_visible"] = True
    expect_reject(exposed, source_frame)
    wrong_frame = copy.deepcopy(good)
    wrong_frame["source_frame_sha256"] = "0" * 64
    expect_reject(wrong_frame, source_frame)
    unresolved = copy.deepcopy(good)
    unresolved["adjudication"]["disagreement_record"] = {"disagreement_observed": True, "resolution": None, "notes": "Synthetic disagreement."}
    expect_reject(unresolved, source_frame)
    try:
        validate_packets([good, copy.deepcopy(good)])
    except ValueError:
        duplicate_rejected = True
    else:
        raise AssertionError("duplicate cluster ids accepted")
    return {
        "decision": "GREEN",
        "source_frame_n": len(source_frame),
        "source_frame_sha256": EXPECTED_SUCCESSOR_FRAME_SHA256,
        "valid_packet_accepted": True,
        "forged_source_hash_rejected": True,
        "invalid_target_rejected": True,
        "prediction_exposure_rejected": True,
        "wrong_source_frame_rejected": True,
        "unresolved_disagreement_rejected": True,
        "duplicate_cluster_rejected": duplicate_rejected,
        "external_judgments_created": False,
    }


def read_packets(paths: list[Path]) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            packets.extend(payload)
        elif isinstance(payload, dict):
            packets.append(payload)
        else:
            raise ValueError(f"{path} must contain a JSON object or list")
    return packets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
    else:
        if not args.paths:
            ap.error("provide curator packet JSON path(s) or --self-test")
        result = validate_packets(read_packets(args.paths))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
