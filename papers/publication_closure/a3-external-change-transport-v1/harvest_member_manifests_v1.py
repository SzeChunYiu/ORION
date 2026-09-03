#!/usr/bin/env python3
"""Harvest normalized member manifests for the frozen 128-family successor frame.

Outcome-blind public-substrate materialization: fetches both RO-Crate versions of
every family in the frozen WorkflowHub successor frame, applies the frozen v2
normalization verbatim (imported from bind_workflowhub_rocrate_content_v1.py),
and refuses to emit anything unless every family's aggregate
normalized_content_manifest_sha256 reproduces the value already frozen in the
successor frame. No strata, no gold, no candidate predictions.

Run location: routed to a LUNARC batch job (compute nodes verified to reach
workflowhub.eu). Deterministic output regardless of worker count or ordering.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHUNK_ROWS = 32


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_modules() -> tuple[Any, Any]:
    binding = _load("a3_rocrate_binding_v1", HERE / "bind_workflowhub_rocrate_content_v1.py")
    curator = _load("a3_curator_validator_harvest", HERE / "validate_external_curator_packet_v1.py")
    return binding, curator


def fetch_member_entries(workflow_id: str, version: int, binding: Any, retries: int = 4, timeout: float = 180.0) -> tuple[list[dict[str, Any]], str]:
    """Fetch one RO-Crate version and return (frozen-normalized member entries, aggregate sha).

    Transport and normalization mirror the frozen bind_workflowhub_rocrate_content_v1
    fetch_rocrate path verbatim (same URL form, UA, read_limited, zip validation,
    retry tuple and backoff); the only difference is that the member entries are
    retained in addition to validate_rocrate_bytes's aggregate. The aggregate is
    cross-checked against validate_rocrate_bytes on the same bytes.
    """
    url = f"https://workflowhub.eu/workflows/{urllib.parse.quote(str(workflow_id), safe='')}/ro_crate?version={version}"
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": binding.UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if status != 200:
                    raise RuntimeError(f"HTTP {status}")
                data = binding.read_limited(resp)
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                entries, _metadata = binding.normalized_content_manifest(zf)
            aggregate = binding.canonical_json_sha(entries)
            if binding.validate_rocrate_bytes(data)["normalized_content_manifest_sha256"] != aggregate:
                raise ValueError("aggregate cross-check failed against frozen validate_rocrate_bytes")
            return entries, aggregate
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"failed member-manifest fetch for workflow {workflow_id} v{version}: {last}")


def harvest(workers: int, note: str) -> dict[str, Any]:
    binding, curator = frozen_modules()
    source_frame = curator.load_source_frame()
    order = sorted(source_frame, key=lambda x: (int(x) if x.isdigit() else 10**18, x))
    if len(order) != 128:
        raise ValueError("frozen successor frame is not 128 families")

    def one(wid: str) -> dict[str, Any]:
        row = source_frame[wid]
        before_entries, before_aggregate = fetch_member_entries(wid, int(row["version_before"]), binding)
        after_entries, after_aggregate = fetch_member_entries(wid, int(row["version_after"]), binding)
        return {
            "workflow_id": wid,
            "version_before": int(row["version_before"]),
            "version_after": int(row["version_after"]),
            "before_members": before_entries,
            "after_members": after_entries,
            "before_normalized_content_manifest_sha256": before_aggregate,
            "after_normalized_content_manifest_sha256": after_aggregate,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(one, order))
    rows.sort(key=lambda r: (int(r["workflow_id"]) if r["workflow_id"].isdigit() else 10**18, r["workflow_id"]))

    mismatches = [
        r["workflow_id"] for r in rows
        if r["before_normalized_content_manifest_sha256"] != source_frame[r["workflow_id"]]["before_normalized_sha256"]
        or r["after_normalized_content_manifest_sha256"] != source_frame[r["workflow_id"]]["after_normalized_sha256"]
    ]
    if mismatches:
        raise ValueError(f"member manifests do not reproduce the frozen frame for: {mismatches}")

    frozen_rows_digest = hashlib.sha256(
        json.dumps(
            [{k: v for k, v in row.items() if not k.endswith("_members")} for row in rows],
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    chunks: list[dict[str, Any]] = []
    for i in range(0, len(rows), CHUNK_ROWS):
        chunk_rows = rows[i:i + CHUNK_ROWS]
        first, last = i + 1, i + len(chunk_rows)
        name = f"FAMILIES_{first:03d}_{last:03d}.json"
        rel = f"papers/publication_closure/a3-external-change-transport-v1/workflowhub-member-manifest-freeze-v1/{name}"
        chunks.append({
            "path": rel,
            "rows": len(chunk_rows),
            "first_workflow_id": chunk_rows[0]["workflow_id"],
            "last_workflow_id": chunk_rows[-1]["workflow_id"],
            "payload": {"schema": "ORION.A3.MemberManifestFreezeChunk.v1", "rows": chunk_rows},
        })
    return {
        "schema": "ORION.A3.MemberManifestFreezeSnapshot.v1",
        "date": "2026-09-03",
        "purpose": "candidate-visible substrate materialization for the frozen A3 candidate policy A3_TRANSPORT_THREE_VALUED_V1; member-level premise extraction input",
        "successor_frame_sha256": curator.EXPECTED_SUCCESSOR_FRAME_SHA256,
        "source_family_n": len(rows),
        "total_member_entries": sum(len(r["before_members"]) + len(r["after_members"]) for r in rows),
        "aggregate_reproduces_frozen_frame_for_every_family": True,
        "frozen_rows_digest_sha256": frozen_rows_digest,
        "harvest_environment": note,
        "change_stratum_adjudicated": False,
        "external_gold_accessed": False,
        "candidate_predictions_computed": False,
        "protected_outcomes_accessed": False,
        "scientific_authority_delta": "NONE__PUBLIC_SUBSTRATE_MATERIALIZATION_ONLY",
        "chunks": chunks,
    }


def write_outputs(snapshot: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for chunk in snapshot["chunks"]:
        payload = chunk.pop("payload")
        text = json.dumps(payload, indent=1, sort_keys=True) + "\n"
        (output_dir / Path(chunk["path"]).name).write_text(text, encoding="utf-8")
        chunk["sha256"] = hashlib.sha256((output_dir / Path(chunk["path"]).name).read_bytes()).hexdigest()
    (output_dir / "SNAPSHOT_V1.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def _self_test() -> dict[str, Any]:
    binding, curator = frozen_modules()
    frame = curator.load_source_frame()
    entries_a = [
        {"path": "ro-crate-metadata.json", "bytes": 2, "sha256": hashlib.sha256(b"{}").hexdigest(), "kind": "regular", "executable": False},
        {"path": "workflow.cwl", "bytes": 18, "sha256": hashlib.sha256(b"cwlVersion: v1.2\n").hexdigest(), "kind": "regular", "executable": False},
    ]
    zip_a = binding.make_zip(
        [("ro-crate-metadata.json", b"{}"), ("workflow.cwl", b"cwlVersion: v1.2\n")],
        compression=zipfile.ZIP_STORED, date=(2020, 1, 1, 0, 0, 0),
    )
    zip_b = binding.make_zip(
        [("ro-crate-metadata.json", b"{}"), ("workflow.cwl", b"cwlVersion: v1.2\n# changed\n")],
        compression=zipfile.ZIP_DEFLATED, date=(2026, 1, 1, 0, 0, 0),
    )
    def entries_of(data: bytes) -> list[dict[str, Any]]:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            entries, _ = binding.normalized_content_manifest(zf)
        return entries
    before, after = entries_of(zip_a), entries_of(zip_b)
    assert binding.canonical_json_sha(before) != binding.canonical_json_sha(after)
    candidate = _load("a3_candidate_policy_harvest", HERE / "candidate_policy_v1.py")
    record = {
        "schema": candidate.VISIBLE_SCHEMA, "workflow_id": "self-test",
        "version_before": 1, "version_after": 2,
        "before_manifest": before, "after_manifest": after,
    }
    result = candidate.evaluate(record)
    assert result["decision"] == "REOPEN", result
    assert result["premise_status_counts"]["UNCHANGED"] == 1
    return {
        "decision": "GREEN",
        "frame_n": len(frame),
        "zip_nuisance_normalized_verbatim": True,
        "member_diff_drives_premise_status": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    if args.self_test:
        print(json.dumps(_self_test(), indent=2, sort_keys=True))
        return 0
    if args.output_dir is None:
        ap.error("--output-dir required unless --self-test")
    if not 1 <= args.workers <= 12:
        ap.error("--workers must be 1..12")
    snapshot = harvest(args.workers, args.note)
    write_outputs(snapshot, args.output_dir)
    print(json.dumps({k: v for k, v in snapshot.items() if k != "chunks"}, indent=2, sort_keys=True))
    print("chunks:")
    for chunk in snapshot["chunks"]:
        print(" ", chunk["path"], chunk["rows"], chunk["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
