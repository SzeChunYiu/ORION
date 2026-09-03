#!/usr/bin/env python3
"""Deterministically build the A3 EligibleChangeClusterPool from curator packets.

Consumes externally authored, externally validated curator adjudication packets
(validate_external_curator_packet_v1.py is the frozen validator and is imported
verbatim) plus the frozen 128-family WorkflowHub successor frame, and emits an
ORION.A3.EligibleChangeClusterPool.v1 payload for allocate_change_clusters_v1.py.

Gold handling: the adjudication TARGET (REUSE/REOPEN/CANNOT_CHECK) is escrowed
with the external curator and is never copied into the pool. Only the stratum,
custody receipts and frame-side hashes/licences enter the pool. Families of the
frozen frame without a validated packet are materialized as eligible=false rows
awaiting external stratum adjudication, so the frame is always fully
materialized and the allocator fails closed on any shortfall.

Run-time resolution: none. Every output field is a verbatim copy of a validated
packet field, a verbatim copy of the frozen frame, or a deterministic SHA-256
over those verbatim values.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
POOL_SCHEMA = "ORION.A3.EligibleChangeClusterPool.v1"
STRATA = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
GOLD_KEYS = (
    "gold", "reuse_gold", "adjudicated_target", "reuse_reopen_target", "target",
    "candidate_prediction", "baseline_prediction", "outcome", "protected_outcome",
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _frozen_validator() -> Any:
    return _load("a3_curator_validator_v1", HERE / "validate_external_curator_packet_v1.py")


def _frozen_allocator() -> Any:
    return _load("a3_allocator_v1", HERE / "allocate_change_clusters_v1.py")


def licence_receipt_id(frame_row: dict[str, Any]) -> str:
    payload = "|".join((
        "A3-LICENCE-RECEIPT-V1",
        str(frame_row["workflow_id"]),
        str(frame_row["version_before"]),
        str(frame_row["version_after"]),
        str(frame_row["license_before"]),
        str(frame_row["license_after"]),
    ))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sorted_frame(source_frame: dict[str, dict[str, Any]]) -> list[str]:
    return sorted(source_frame, key=lambda x: (int(x) if x.isdigit() else 10**18, x))


def build(packets: list[dict[str, Any]]) -> dict[str, Any]:
    curator = _frozen_validator()
    source_frame = curator.load_source_frame()
    summaries = [curator.validate_packet(packet, source_frame) for packet in packets]
    by_workflow: dict[str, dict[str, Any]] = {}
    seen_clusters: set[str] = set()
    for packet, summary in zip(packets, summaries, strict=True):
        wid = summary["workflow_id"]
        if wid in by_workflow:
            raise ValueError(f"multiple curator packets for workflow {wid}")
        if summary["cluster_id"] in seen_clusters:
            raise ValueError(f"duplicate cluster_id: {summary['cluster_id']}")
        seen_clusters.add(summary["cluster_id"])
        by_workflow[wid] = packet

    clusters: list[dict[str, Any]] = []
    for wid in _sorted_frame(source_frame):
        frame_row = source_frame[wid]
        receipt = licence_receipt_id(frame_row)
        if wid not in by_workflow:
            clusters.append({
                "cluster_id": f"pending-external-curator:{wid}",
                "eligible": False,
                "workflow_id": wid,
                "awaiting_external_curator_stratum": True,
            })
            continue
        packet = by_workflow[wid]
        lineage = packet["lineage"]
        clusters.append({
            "cluster_id": packet["cluster_id"],
            "eligible": True,
            "stratum": packet["adjudication"]["stratum"],
            "workflow_id": wid,
            "source_family_id": lineage["source_family_id"],
            "normalized_organization_lineage": lineage["normalized_organization_lineage"],
            "artifact_lineage_id": lineage["artifact_lineage_id"],
            "before_version_id": str(frame_row["version_before"]),
            "after_version_id": str(frame_row["version_after"]),
            "before_sha256": frame_row["before_normalized_sha256"],
            "after_sha256": frame_row["after_normalized_sha256"],
            "license_before": frame_row["license_before"],
            "license_after": frame_row["license_after"],
            "license_or_rights_receipt_id": receipt,
            "curator_assignment_receipt_id": packet["curator_receipt"]["receipt_sha256"],
            "candidate_visible_packet_frozen": True,
            "candidate_visible_packet_sha256": packet["candidate_visible_packet_sha256"],
        })

    pool = {
        "schema": POOL_SCHEMA,
        "successor_frame_sha256": curator.EXPECTED_SUCCESSOR_FRAME_SHA256,
        "source_family_n": len(source_frame),
        "eligible_cluster_n": len(by_workflow),
        "pending_external_curator_n": len(source_frame) - len(by_workflow),
        "stratum_adjudicated_cluster_n": len(by_workflow),
        "gold_escrow": "adjudication targets remain with the external curator; no gold value is present in this pool",
        "protected_outcomes_accessed": False,
        "candidate_predictions_accessed": False,
        "stratum_adjudication_completed_before_candidate_predictions": True,
        "clusters": clusters,
    }
    _assert_gold_free(pool)
    return pool


def _assert_gold_free(pool: dict[str, Any]) -> None:
    for row in pool["clusters"]:
        bad = set(GOLD_KEYS) & set(row)
        if bad:
            raise ValueError(f"gold-bearing field entered the eligible pool: {sorted(bad)}")


def synthetic_packet(frame_row: dict[str, Any], cluster_id: str, stratum: str, org: str) -> dict[str, Any]:
    """Pipeline-proof packet: mechanically valid custody shape, zero scientific judgment."""
    return {
        "schema": "ORION.A3.ExternalCuratorAdjudicationPacket.v1",
        "source_frame_sha256": "a47d9255aa37de056cb5cdd7c140bcccb487aa3285790655a48abb5e538c2993",
        "cluster_id": cluster_id,
        "source": {
            "workflow_id": frame_row["workflow_id"],
            "version_before": frame_row["version_before"],
            "version_after": frame_row["version_after"],
            "license_before": frame_row["license_before"],
            "license_after": frame_row["license_after"],
            "before_normalized_sha256": frame_row["before_normalized_sha256"],
            "after_normalized_sha256": frame_row["after_normalized_sha256"],
        },
        "lineage": {
            "source_family_id": f"workflowhub:{frame_row['workflow_id']}",
            "normalized_organization_lineage": org,
            "artifact_lineage_id": f"workflowhub-artifact:{frame_row['workflow_id']}",
        },
        "candidate_visible_packet_sha256": hashlib.sha256(cluster_id.encode("utf-8")).hexdigest(),
        "adjudication": {
            "stratum": stratum,
            "target": "CANNOT_CHECK",
            "rationale": "SYNTHETIC PIPELINE PROOF ONLY: no scientific judgment is made or implied.",
            "evidence_refs": ["synthetic:pipeline-proof:1"],
            "disagreement_record": {
                "disagreement_observed": False,
                "resolution": None,
                "notes": "SYNTHETIC PIPELINE PROOF ONLY: no external adjudication occurred.",
            },
        },
        "curator_receipt": {
            "curator_id": "synthetic-pipeline-proof-curator",
            "adjudicated_at_utc": "2099-01-01T00:00:00Z",
            "receipt_sha256": hashlib.sha256(("synthetic-receipt|" + cluster_id).encode("utf-8")).hexdigest(),
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


def _synthetic_batch() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    curator = _frozen_validator()
    source_frame = curator.load_source_frame()
    packets: list[dict[str, Any]] = []
    for i, wid in enumerate(_sorted_frame(source_frame)):
        packets.append(synthetic_packet(
            source_frame[wid],
            cluster_id=f"synthetic-pipeline-proof-{i + 1:03d}",
            stratum=STRATA[i % 4],
            org=f"synthetic-org-{i + 1:03d}",
        ))
    return packets, source_frame


def self_test() -> dict[str, Any]:
    allocator = _frozen_allocator()
    packets, source_frame = _synthetic_batch()
    pool = build(packets)
    if pool["eligible_cluster_n"] != len(source_frame) or pool["pending_external_curator_n"] != 0:
        raise ValueError("synthetic batch did not cover the full frozen frame")

    # Gold must be rejected by the pool contract even when a packet carries it.
    poisoned = json.loads(json.dumps(pool))
    poisoned["clusters"][0]["gold"] = "REOPEN"
    try:
        allocator.validate_pool(poisoned)
    except ValueError as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("gold-bearing pool accepted by the frozen allocator")

    # Full 96+32 allocation over the synthetic proof pool.
    allocation = allocator.allocate(pool)
    if allocation["terminal"] != "A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN":
        raise ValueError(f"unexpected allocation terminal: {allocation['terminal']}")
    if allocation["selected_n"] != 128 or allocation["counts"] != {s: {"primary": 24, "replication": 8} for s in STRATA}:
        raise ValueError("synthetic proof allocation did not reach 96 primary + 32 replication")
    # Determinism under input permutation.
    shuffled = json.loads(json.dumps(pool))
    shuffled["clusters"].reverse()
    if allocator.allocate(shuffled)["selection_manifest_sha256"] != allocation["selection_manifest_sha256"]:
        raise ValueError("allocation is not invariant to pool row order")

    # Partial coverage: uncovered families materialize as ineligible, allocator fails closed.
    partial = build(packets[:96])
    if partial["pending_external_curator_n"] != len(source_frame) - 96:
        raise ValueError("pending families miscounted")
    partial_alloc = allocator.allocate(partial)
    if partial_alloc["terminal"] != "CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL":
        raise ValueError("partial pool must fail closed with the shortfall terminal")

    # Duplicate cluster ids are rejected.
    dup = packets + [dict(packets[0])]
    try:
        build(dup)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate packet accepted")

    return {
        "decision": "GREEN",
        "source_family_n": len(source_frame),
        "pool_schema": POOL_SCHEMA,
        "synthetic_proof_packets_n": len(packets),
        "allocation_terminal": allocation["terminal"],
        "allocation_selected_n": allocation["selected_n"],
        "allocation_selection_manifest_sha256": allocation["selection_manifest_sha256"],
        "partial_coverage_fails_closed": True,
        "gold_never_enters_pool": True,
        "scientific_judgment_made": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packets", nargs="*", type=Path, help="external curator packet JSON path(s)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.self_test:
        result = self_test()
        code = 0
    else:
        if not args.packets:
            ap.error("curator packet path(s) required unless --self-test")
        packets: list[dict[str, Any]] = []
        for path in args.packets:
            payload = json.loads(path.read_text(encoding="utf-8"))
            packets.extend(payload if isinstance(payload, list) else [payload])
        result = build(packets)
        code = 0
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
