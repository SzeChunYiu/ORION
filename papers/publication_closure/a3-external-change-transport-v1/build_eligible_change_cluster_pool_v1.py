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
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
POOL_SCHEMA = "ORION.A3.EligibleChangeClusterPool.v1"
V3_FREEZE_DIRNAME = "workflowhub-member-manifest-freeze-v3"
V3_SUCCESS_TERMINAL = "WORKFLOWHUB_MEMBER_MANIFEST_V3_REPRODUCIBLE_FROZEN"
V3_FAILURE_TERMINAL = "CANNOT_CHECK_MEMBER_MANIFEST_V3_REPRODUCIBILITY"
V3_NORMALIZATION_ID = "WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3"
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


def _member_manifests_v3(source_frame: dict[str, dict[str, Any]], base_dir: Path | None = None) -> dict[str, Any] | None:
    """Load the frozen v3 member-manifest substrate, fail closed on any defect.

    Returns the pool-binding block (per-family before/after v3 aggregate shas
    plus the substrate identity), None when the v3 harvest result has not been
    materialized yet, or a bound=False record when the harvest failed closed
    (a fail-closed result is a result: the pool stays on the frozen v2-bound
    frame, which remains the admission authority until a governed rebind, and
    records the v3 boundary explicitly instead of crashing or silently
    consuming a substrate that was never materialized). A SUCCESS result with
    partial family coverage, chunk-byte drift against the recorded chunk
    digests, or any before==after v3 collapse is a hard error.
    """
    freeze_dir = (base_dir if base_dir is not None else HERE) / V3_FREEZE_DIRNAME
    result_path = freeze_dir / "RESULT_V3.json"
    if not result_path.is_file():
        # Absence cross-checked two ways before treating as absent.
        if freeze_dir.exists() and any(freeze_dir.iterdir()):
            for entry in freeze_dir.iterdir():
                if entry.suffix == ".json":
                    raise ValueError(f"v3 freeze directory carries files but no RESULT_V3.json: {entry.name}")
        return None
    result = json.loads(result_path.read_text(encoding="utf-8"))
    terminal = result.get("terminal")
    result_sha = hashlib.sha256(result_path.read_bytes()).hexdigest()
    if terminal == V3_FAILURE_TERMINAL:
        partition = result.get("partition", {})
        return {
            "normalization_id": V3_NORMALIZATION_ID,
            "bound": False,
            "result_terminal": terminal,
            "result_sha256": result_sha,
            "v3_reproducible_n": partition.get("v3_reproducible_n"),
            "v3_nonreproducible_workflow_ids": partition.get("v3_nonreproducible_workflow_ids", []),
            "v3_content_only_before_after_equal_workflow_ids": partition.get("v3_content_only_before_after_equal_workflow_ids", []),
            "v2_aggregate_reproduces_frozen_frame_n": partition.get("v2_aggregate_reproduces_frozen_frame_n"),
            "state": (
                "v3 member-manifest harvest failed closed (fail_closed_before_emitting_any_chunk); no v3 "
                "substrate was materialized, no eligible row carries v3 aggregates, and the frozen v2-bound "
                "frame remains the admission authority; the descriptor-only families and any frame rebind are "
                "reserved to freeze governance"
            ),
        }
    if terminal != V3_SUCCESS_TERMINAL:
        raise ValueError(f"unknown v3 member-manifest terminal: {terminal!r}")
    if result.get("successor_frame_sha256") != _frozen_validator().EXPECTED_SUCCESSOR_FRAME_SHA256:
        raise ValueError("v3 member-manifest result does not bind the frozen successor frame")
    normalization = result.get("normalization", {})
    if normalization.get("id") != V3_NORMALIZATION_ID:
        raise ValueError("v3 member-manifest result normalization id mismatch")

    snapshot = json.loads((freeze_dir / "SNAPSHOT_V3.json").read_text(encoding="utf-8"))
    if snapshot.get("normalization_id") != V3_NORMALIZATION_ID:
        raise ValueError("v3 snapshot normalization id mismatch")
    rows_by_id: dict[str, dict[str, Any]] = {}
    for chunk in snapshot.get("chunks", []):
        chunk_path = freeze_dir / Path(str(chunk["path"])).name
        digest = hashlib.sha256(chunk_path.read_bytes()).hexdigest()
        if digest != chunk.get("sha256"):
            raise ValueError(f"v3 chunk digest mismatch: {chunk_path.name}")
        payload = json.loads(chunk_path.read_text(encoding="utf-8"))
        for row in payload["rows"]:
            wid = str(row["workflow_id"])
            if wid in rows_by_id:
                raise ValueError(f"duplicate family in v3 snapshot: {wid}")
            if row["before_normalized_manifest_v3_sha256"] == row["after_normalized_manifest_v3_sha256"]:
                raise ValueError(f"v3 snapshot family collapsed to equal aggregates: {wid}")
            rows_by_id[wid] = row
    if set(rows_by_id) != set(source_frame):
        raise ValueError("v3 snapshot does not exactly cover the frozen 128-family frame")

    return {
        "normalization_id": V3_NORMALIZATION_ID,
        "bound": True,
        "result_terminal": terminal,
        "result_sha256": result_sha,
        "snapshot_sha256": hashlib.sha256((freeze_dir / "SNAPSHOT_V3.json").read_bytes()).hexdigest(),
        "frozen_rows_digest_sha256": snapshot.get("frozen_rows_digest_sha256"),
        "families_bound": len(rows_by_id),
        "rows_by_workflow_id": rows_by_id,
    }


def build(packets: list[dict[str, Any]], v3_base_dir: Path | None = None) -> dict[str, Any]:
    curator = _frozen_validator()
    source_frame = curator.load_source_frame()
    substrate = _member_manifests_v3(source_frame, base_dir=v3_base_dir)
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
        cluster = {
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
        }
        if substrate is not None and substrate.get("bound") is True:
            v3_row = substrate["rows_by_workflow_id"][wid]
            cluster["before_manifest_v3_sha256"] = v3_row["before_normalized_manifest_v3_sha256"]
            cluster["after_manifest_v3_sha256"] = v3_row["after_normalized_manifest_v3_sha256"]
        clusters.append(cluster)

    member_manifest_block: dict[str, Any]
    if substrate is None:
        member_manifest_block = {
            "normalization_id": V3_NORMALIZATION_ID,
            "present": False,
            "bound": False,
            "state": "v3 member-manifest harvest result not yet materialized; pool rows carry frame-side v2 aggregates only",
        }
    elif substrate.get("bound") is not True:
        member_manifest_block = {
            "normalization_id": V3_NORMALIZATION_ID,
            "present": True,
            "bound": False,
            "result_terminal": substrate["result_terminal"],
            "result_sha256": substrate["result_sha256"],
            "v3_reproducible_n": substrate["v3_reproducible_n"],
            "v3_nonreproducible_workflow_ids": substrate["v3_nonreproducible_workflow_ids"],
            "v3_content_only_before_after_equal_workflow_ids": substrate["v3_content_only_before_after_equal_workflow_ids"],
            "v2_aggregate_reproduces_frozen_frame_n": substrate["v2_aggregate_reproduces_frozen_frame_n"],
            "state": substrate["state"],
        }
    else:
        member_manifest_block = {
            "normalization_id": V3_NORMALIZATION_ID,
            "present": True,
            "bound": True,
            "result_terminal": substrate["result_terminal"],
            "result_sha256": substrate["result_sha256"],
            "snapshot_sha256": substrate["snapshot_sha256"],
            "frozen_rows_digest_sha256": substrate["frozen_rows_digest_sha256"],
            "families_bound": substrate["families_bound"],
            "note": "per-family before/after v3 member-manifest aggregates are carried verbatim on every eligible cluster row; the frame-side before_sha256/after_sha256 remain the frozen v2 values and are not rebound by this pool",
        }

    pool = {
        "schema": POOL_SCHEMA,
        "successor_frame_sha256": curator.EXPECTED_SUCCESSOR_FRAME_SHA256,
        "source_family_n": len(source_frame),
        "eligible_cluster_n": len(by_workflow),
        "pending_external_curator_n": len(source_frame) - len(by_workflow),
        "stratum_adjudicated_cluster_n": len(by_workflow),
        "member_manifest_freeze_v3": member_manifest_block,
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


def _synthetic_v3_freeze_dir(source_frame: dict[str, dict[str, Any]], base: Path) -> Path:
    """Write a mechanically valid synthetic v3 freeze dir (pipeline proof only)."""
    freeze = base / V3_FREEZE_DIRNAME
    freeze.mkdir(parents=True)
    rows = []
    for wid in _sorted_frame(source_frame):
        entry = {"path": "workflow.cwl", "bytes": 2, "sha256": hashlib.sha256(wid.encode()).hexdigest(), "kind": "regular", "executable": False}
        rows.append({
            "workflow_id": wid,
            "fetches_per_version": 3,
            "before_manifest": [dict(entry)],
            "after_manifest": [dict(entry, sha256=hashlib.sha256(("after" + wid).encode()).hexdigest())],
            "before_excluded_request_generated_paths": ["ro-crate-metadata.json", "ro-crate-preview.html"],
            "after_excluded_request_generated_paths": ["ro-crate-metadata.json", "ro-crate-preview.html"],
            "before_normalized_manifest_v3_sha256": hashlib.sha256(("before" + wid).encode()).hexdigest(),
            "after_normalized_manifest_v3_sha256": hashlib.sha256(("after" + wid).encode()).hexdigest(),
            "before_v2_aggregate_reproduces_frozen_frame": False,
            "after_v2_aggregate_reproduces_frozen_frame": False,
        })
    chunks = []
    for i in range(0, len(rows), 32):
        block = rows[i:i + 32]
        name = f"FAMILIES_{i + 1:03d}_{i + len(block):03d}.json"
        payload = {"schema": "ORION.A3.MemberManifestFreezeChunk.v3", "normalization_id": V3_NORMALIZATION_ID, "rows": block}
        (freeze / name).write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        chunks.append({
            "path": f"papers/publication_closure/a3-external-change-transport-v1/{V3_FREEZE_DIRNAME}/{name}",
            "rows": len(block),
            "sha256": hashlib.sha256((freeze / name).read_bytes()).hexdigest(),
        })
    snapshot = {
        "schema": "ORION.A3.MemberManifestFreezeSnapshot.v3",
        "normalization_id": V3_NORMALIZATION_ID,
        "successor_frame_sha256": _frozen_validator().EXPECTED_SUCCESSOR_FRAME_SHA256,
        "source_family_n": len(rows),
        "v3_aggregate_reproducible_for_every_family": True,
        "frozen_rows_digest_sha256": hashlib.sha256(b"synthetic").hexdigest(),
        "chunks": chunks,
    }
    (freeze / "SNAPSHOT_V3.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    result = {
        "schema": "ORION.A3.MemberManifestFreezeResult.v3",
        "terminal": V3_SUCCESS_TERMINAL,
        "successor_frame_sha256": snapshot["successor_frame_sha256"],
        "normalization": {"id": V3_NORMALIZATION_ID},
        "partition": {"frame_n": len(rows), "fetches_per_family_version": 3},
    }
    (freeze / "RESULT_V3.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return freeze


def _rewrite_v3_chunk(freeze: Path, chunk_index: int, mutate_rows) -> None:
    """Apply a row mutation to one chunk and re-bind its digest in the snapshot."""
    snapshot = json.loads((freeze / "SNAPSHOT_V3.json").read_text(encoding="utf-8"))
    chunk = snapshot["chunks"][chunk_index]
    chunk_path = freeze / Path(chunk["path"]).name
    payload = json.loads(chunk_path.read_text(encoding="utf-8"))
    mutate_rows(payload["rows"])
    chunk_path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    chunk["sha256"] = hashlib.sha256(chunk_path.read_bytes()).hexdigest()
    (freeze / "SNAPSHOT_V3.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")


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

    # v3 member-manifest substrate binding: a valid full-frame synthetic freeze
    # dir feeds per-family v3 aggregates onto every eligible row and the pool
    # still allocates; each substrate defect fails the build closed.
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _synthetic_v3_freeze_dir(source_frame, base)
        v3_pool = build(packets, v3_base_dir=base)
        if v3_pool["member_manifest_freeze_v3"].get("present") is not True:
            raise ValueError("synthetic v3 substrate not bound into the pool")
        eligible_rows = [c for c in v3_pool["clusters"] if c.get("eligible") is True]
        if len(eligible_rows) != len(source_frame):
            raise ValueError("eligible row count changed under the v3 substrate")
        for cluster in eligible_rows:
            if "before_manifest_v3_sha256" not in cluster or "after_manifest_v3_sha256" not in cluster:
                raise ValueError(f"eligible row missing v3 member-manifest aggregates: {cluster['cluster_id']}")
            if cluster["before_manifest_v3_sha256"] == cluster["after_manifest_v3_sha256"]:
                raise ValueError("v3 aggregates collapsed on an eligible row")
        v3_allocation = allocator.allocate(v3_pool)
        if v3_allocation["terminal"] != "A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN" or v3_allocation["selected_n"] != 128:
            raise ValueError("v3-bound pool failed the frozen allocation")
        _assert_gold_free(v3_pool)

    # Hostile: a failed v3 harvest result is never consumed as substrate; the
    # pool stays buildable on the v2-bound frame and records the boundary.
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        _synthetic_v3_freeze_dir(source_frame, base)
        result_path = base / V3_FREEZE_DIRNAME / "RESULT_V3.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        result["terminal"] = V3_FAILURE_TERMINAL
        result["partition"] = {
            "frame_n": 128,
            "fetches_per_family_version": 3,
            "v3_reproducible_n": 128,
            "v3_nonreproducible_workflow_ids": [],
            "v3_content_only_before_after_equal_workflow_ids": ["106", "360", "384"],
            "v2_aggregate_reproduces_frozen_frame_n": 33,
            "v2_aggregate_mismatch_workflow_ids_n": 95,
        }
        result_path.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        failed_pool = build(packets, v3_base_dir=base)
        block = failed_pool["member_manifest_freeze_v3"]
        if block.get("bound") is not False or block.get("result_terminal") != V3_FAILURE_TERMINAL:
            raise ValueError("failed v3 harvest not recorded in the pool block")
        if block.get("v3_content_only_before_after_equal_workflow_ids") != ["106", "360", "384"]:
            raise ValueError("failed v3 harvest partition not carried into the pool block")
        if any("before_manifest_v3_sha256" in c for c in failed_pool["clusters"]):
            raise AssertionError("failed v3 harvest leaked v3 aggregates onto pool rows")
        failed_alloc = allocator.allocate(failed_pool)
        if failed_alloc["terminal"] != "A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN":
            raise ValueError("pool on the recorded v3 boundary must still allocate under the frozen frame")
        if failed_alloc["selection_manifest_sha256"] != allocation["selection_manifest_sha256"]:
            raise ValueError("recorded-but-unbound v3 boundary changed the allocation digest")

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        freeze = _synthetic_v3_freeze_dir(source_frame, base)
        chunk_path = freeze / "FAMILIES_001_032.json"
        chunk_path.write_bytes(chunk_path.read_bytes() + b"\n")
        try:
            build(packets, v3_base_dir=base)
        except ValueError:
            pass
        else:
            raise AssertionError("tampered v3 chunk bytes accepted as pool substrate")

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        freeze = _synthetic_v3_freeze_dir(source_frame, base)
        _rewrite_v3_chunk(freeze, 0, lambda rows: rows.pop(0))
        try:
            build(packets, v3_base_dir=base)
        except ValueError:
            pass
        else:
            raise AssertionError("partial v3 family coverage accepted as pool substrate")

    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        freeze = _synthetic_v3_freeze_dir(source_frame, base)

        def collapse(rows: list[dict[str, Any]]) -> None:
            rows[0]["after_normalized_manifest_v3_sha256"] = rows[0]["before_normalized_manifest_v3_sha256"]

        _rewrite_v3_chunk(freeze, 0, collapse)
        try:
            build(packets, v3_base_dir=base)
        except ValueError:
            pass
        else:
            raise AssertionError("collapsed v3 family accepted as pool substrate")

    return {
        "decision": "GREEN",
        "source_family_n": len(source_frame),
        "pool_schema": POOL_SCHEMA,
        "synthetic_proof_packets_n": len(packets),
        "allocation_terminal": allocation["terminal"],
        "allocation_selected_n": allocation["selected_n"],
        "allocation_selection_manifest_sha256": allocation["selection_manifest_sha256"],
        "v3_substrate_allocation_terminal": v3_allocation["terminal"],
        "v3_substrate_defects_fail_closed": True,
        "v3_failure_recorded_not_bound": True,
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
