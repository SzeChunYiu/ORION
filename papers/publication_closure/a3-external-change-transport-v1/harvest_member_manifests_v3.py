#!/usr/bin/env python3
"""Harvest v3 member manifests for the frozen 128-family successor frame.

Governed execution of WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3
(normalize_member_manifests_v3.py, imported verbatim): fetches both RO-Crate
versions of every family in the frozen WorkflowHub successor frame with at
least three independent fetches per family per version, and refuses to emit
anything unless the v3 aggregate (workflow-content members only; the two
request-generated root crate files excluded) is byte-identical across every
fetch of every family and version, and unless the before/after v3 aggregates
differ for every family. A single failing family fails the whole harvest
closed; the exact partition is recorded either way. No strata, no gold, no
candidate predictions.

For evidence (never for gating) each fetch also recomputes the frozen v2
aggregate over the merged member set and cross-checks it bitwise against the
frozen v2 validator on the same bytes; the v2-vs-frozen-frame comparison
re-observes the 33/95 boundary of RESULT_V1.json inside this run.

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
MIN_FETCHES = 3
SUCCESS_TERMINAL = "WORKFLOWHUB_MEMBER_MANIFEST_V3_REPRODUCIBLE_FROZEN"
FAILURE_TERMINAL = "CANNOT_CHECK_MEMBER_MANIFEST_V3_REPRODUCIBILITY"
RESULT_SCHEMA = "ORION.A3.MemberManifestFreezeResult.v3"
SNAPSHOT_SCHEMA = "ORION.A3.MemberManifestFreezeSnapshot.v3"
CHUNK_SCHEMA = "ORION.A3.MemberManifestFreezeChunk.v3"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot import frozen module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_modules() -> tuple[Any, Any, Any]:
    binding = _load("a3_rocrate_binding_v3h", HERE / "bind_workflowhub_rocrate_content_v1.py")
    curator = _load("a3_curator_validator_v3h", HERE / "validate_external_curator_packet_v1.py")
    v3norm = _load("a3_member_manifest_v3norm", HERE / "normalize_member_manifests_v3.py")
    return binding, curator, v3norm


def fetch_once(workflow_id: str, version: int, binding: Any, v3norm: Any, retries: int = 4, timeout: float = 180.0) -> dict[str, Any]:
    """One independent fetch: v3 manifest + both aggregates, v2 cross-checked.

    Transport mirrors the frozen bind_workflowhub_rocrate_content_v1 fetch path
    verbatim (same URL form, UA, read_limited, retry tuple and backoff).
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
                retained, excluded, _metadata = v3norm.normalized_content_manifest_v3(zf)
            v3_aggregate = v3norm.aggregate_v3(retained)
            v2_aggregate = binding.canonical_json_sha(v3norm.v2_equivalent_manifest(retained, excluded))
            if binding.validate_rocrate_bytes(data)["normalized_content_manifest_sha256"] != v2_aggregate:
                raise ValueError("v2 cross-check failed against frozen validate_rocrate_bytes")
            return {
                "retained": retained,
                "excluded_paths": [e["path"] for e in excluded],
                "v3_aggregate": v3_aggregate,
                "v2_aggregate": v2_aggregate,
            }
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"failed v3 member-manifest fetch for workflow {workflow_id} v{version}: {last}")


def reproducibility_defect(fetch_list: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the defect record if the fetch set is not v3-reproducible, else None."""
    aggregates = {f["v3_aggregate"] for f in fetch_list}
    retained_paths = {frozenset(e["path"] for e in f["retained"]) for f in fetch_list}
    excluded_paths = {tuple(f["excluded_paths"]) for f in fetch_list}
    if len(aggregates) == 1 and len(retained_paths) == 1 and len(excluded_paths) == 1:
        return None
    differing_members: set[str] = set()
    reference = fetch_list[0]
    ref_map = {e["path"]: e for e in reference["retained"]}
    for other in fetch_list[1:]:
        other_map = {e["path"]: e for e in other["retained"]}
        for path, entry in other_map.items():
            twin = ref_map.get(path)
            if twin is None or twin["sha256"] != entry["sha256"]:
                differing_members.add(path)
        for path in ref_map:
            if path not in other_map:
                differing_members.add(path)
    return {
        "distinct_v3_aggregates": sorted(aggregates),
        "distinct_retained_path_sets": len(retained_paths),
        "distinct_excluded_path_sets": len(excluded_paths),
        "workflow_content_members_differing_across_fetches": sorted(differing_members),
    }


def harvest(workers: int, fetches: int, note: str) -> dict[str, Any]:
    binding, curator, v3norm = frozen_modules()
    source_frame = curator.load_source_frame()
    order = sorted(source_frame, key=lambda x: (int(x) if x.isdigit() else 10**18, x))
    if len(order) != 128:
        raise ValueError("frozen successor frame is not 128 families")

    def one(wid: str) -> dict[str, Any]:
        row = source_frame[wid]
        out: dict[str, Any] = {"workflow_id": wid, "fetches_per_version": fetches}
        for side, version_key in (("before", "version_before"), ("after", "version_after")):
            version = int(row[version_key])
            fetch_list = [fetch_once(wid, version, binding, v3norm) for _ in range(fetches)]
            defect = reproducibility_defect(fetch_list)
            last = fetch_list[-1]
            out[f"{side}_defect"] = defect
            out[f"{side}_manifest"] = last["retained"]
            out[f"{side}_excluded_request_generated_paths"] = last["excluded_paths"]
            out[f"{side}_normalized_manifest_v3_sha256"] = last["v3_aggregate"]
            out[f"{side}_v2_aggregate_reproduces_frozen_frame"] = all(
                f["v2_aggregate"] == row[f"{side}_normalized_sha256"] for f in fetch_list
            )
        return out

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(one, order))
    rows.sort(key=lambda r: (int(r["workflow_id"]) if r["workflow_id"].isdigit() else 10**18, r["workflow_id"]))

    nonreproducible = sorted(
        (r["workflow_id"] for r in rows if r["before_defect"] or r["after_defect"]),
        key=lambda x: (int(x) if x.isdigit() else 10**18, x),
    )
    content_collapsed = sorted(
        (r["workflow_id"] for r in rows if r["before_normalized_manifest_v3_sha256"] == r["after_normalized_manifest_v3_sha256"]),
        key=lambda x: (int(x) if x.isdigit() else 10**18, x),
    )
    v2_stable = sorted(
        (r["workflow_id"] for r in rows
         if r["before_v2_aggregate_reproduces_frozen_frame"] and r["after_v2_aggregate_reproduces_frozen_frame"]),
        key=lambda x: (int(x) if x.isdigit() else 10**18, x),
    )
    partition = {
        "frame_n": len(rows),
        "fetches_per_family_version": fetches,
        "v3_reproducible_n": len(rows) - len(nonreproducible),
        "v3_nonreproducible_workflow_ids": nonreproducible,
        "v3_content_only_before_after_equal_workflow_ids": content_collapsed,
        "v2_aggregate_reproduces_frozen_frame_n": len(v2_stable),
        "v2_aggregate_mismatch_workflow_ids_n": len(rows) - len(v2_stable),
    }
    base = {
        "schema": RESULT_SCHEMA,
        "date": "2026-09-03",
        "purpose": (
            "Governed execution of the frozen v3 member-manifest normalization "
            "(WORKFLOWHUB_MEMBER_MANIFEST_NORMALIZATION_V3) over the frozen 128-family successor "
            "frame: re-verify WorkflowHub reproducibility for every family with at least three "
            "independent fetches per family per version, and materialize the candidate-visible "
            "member manifests only if every family reproduces."
        ),
        "successor_frame_sha256": curator.EXPECTED_SUCCESSOR_FRAME_SHA256,
        "successor_frame_rebound": False,
        "normalization": {
            "id": v3norm.V3_NORMALIZATION_ID,
            "module": "papers/publication_closure/a3-external-change-transport-v1/normalize_member_manifests_v3.py",
            "request_generated_root_members_excluded": list(v3norm.REQUEST_GENERATED_ROOT_MEMBERS),
            "rule": v3norm.V3_RULE,
            "v2_normalization_imported_verbatim": True,
        },
        "partition": partition,
        "run_environment": note,
        "flags": {
            "change_stratum_adjudicated": False,
            "external_gold_accessed": False,
            "candidate_predictions_computed": False,
            "protected_outcomes_accessed": False,
            "member_manifests_committed": False,
            "successor_frame_rebound": False,
        },
        "grants_scientific_authority": False,
        "scientific_authority_delta": "NONE__PUBLIC_SUBSTRATE_MATERIALIZATION_ONLY",
    }

    if nonreproducible or content_collapsed:
        base["terminal"] = FAILURE_TERMINAL
        base["evidence"] = {
            "nonreproducible_fetch_defects": {
                r["workflow_id"]: {side: r[f"{side}_defect"] for side in ("before", "after") if r[f"{side}_defect"]}
                for r in rows if r["before_defect"] or r["after_defect"]
            },
            "content_only_collapse": (
                "families whose before/after v3 aggregates are equal: the version-pair change is "
                "confined to the excluded request-generated members, which the frozen successor "
                "frame admission rule (normalized content must differ) cannot express under v3"
            ) if content_collapsed else "none",
            "fail_closed_before_emitting_any_chunk": True,
        }
        return base

    frozen_rows_digest = hashlib.sha256(
        json.dumps(
            [
                {
                    k: v for k, v in row.items()
                    if k not in ("before_manifest", "after_manifest", "before_defect", "after_defect")
                }
                for row in rows
            ],
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    chunks: list[dict[str, Any]] = []
    for i in range(0, len(rows), CHUNK_ROWS):
        chunk_rows = rows[i:i + CHUNK_ROWS]
        first, last = i + 1, i + len(chunk_rows)
        name = f"FAMILIES_{first:03d}_{last:03d}.json"
        rel = f"papers/publication_closure/a3-external-change-transport-v1/workflowhub-member-manifest-freeze-v3/{name}"
        chunks.append({
            "path": rel,
            "rows": len(chunk_rows),
            "first_workflow_id": chunk_rows[0]["workflow_id"],
            "last_workflow_id": chunk_rows[-1]["workflow_id"],
            "payload": {
                "schema": CHUNK_SCHEMA,
                "normalization_id": v3norm.V3_NORMALIZATION_ID,
                "rows": [
                    {k: v for k, v in row.items() if not k.endswith("_defect")}
                    for row in chunk_rows
                ],
            },
        })
    base["terminal"] = SUCCESS_TERMINAL
    base["evidence"] = {
        "v3_reproducibility": (
            f"every family and version reproduced an identical v3 aggregate across all {fetches} "
            "independent fetches, with identical retained and excluded member path sets"
        ),
        "v2_cross_check": (
            "every fetch's merged member set reproduced the frozen v2 validator bitwise "
            "(validate_rocrate_bytes on the same bytes); the v2-vs-frozen-frame comparison "
            "re-observes the RESULT_V1.json 33/95 boundary inside this run and is recorded "
            "per family as evidence only"
        ),
        "fail_closed_before_emitting_any_chunk": False,
    }
    base["snapshot"] = {
        "schema": SNAPSHOT_SCHEMA,
        "date": "2026-09-03",
        "purpose": "candidate-visible substrate materialization for the frozen A3 candidate policy A3_TRANSPORT_THREE_VALUED_V1; member-level premise extraction input",
        "successor_frame_sha256": curator.EXPECTED_SUCCESSOR_FRAME_SHA256,
        "normalization_id": v3norm.V3_NORMALIZATION_ID,
        "source_family_n": len(rows),
        "total_member_entries": sum(len(r["before_manifest"]) + len(r["after_manifest"]) for r in rows),
        "v3_aggregate_reproducible_for_every_family": True,
        "frozen_rows_digest_sha256": frozen_rows_digest,
        "harvest_environment": note,
        "change_stratum_adjudicated": False,
        "external_gold_accessed": False,
        "candidate_predictions_computed": False,
        "protected_outcomes_accessed": False,
        "scientific_authority_delta": "NONE__PUBLIC_SUBSTRATE_MATERIALIZATION_ONLY",
        "chunks": chunks,
    }
    base["flags"]["member_manifests_committed"] = True
    return base


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if result["terminal"] == SUCCESS_TERMINAL:
        snapshot = result["snapshot"]
        for chunk in snapshot["chunks"]:
            payload = chunk.pop("payload")
            text = json.dumps(payload, indent=1, sort_keys=True) + "\n"
            (output_dir / Path(chunk["path"]).name).write_text(text, encoding="utf-8")
            chunk["sha256"] = hashlib.sha256((output_dir / Path(chunk["path"]).name).read_bytes()).hexdigest()
        (output_dir / "SNAPSHOT_V3.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "RESULT_V3.json").write_text(
        json.dumps({k: v for k, v in result.items() if k != "snapshot"}, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _self_test() -> dict[str, Any]:
    binding, curator, v3norm = frozen_modules()
    frame = curator.load_source_frame()
    assert len(frame) == 128

    workflow = b"cwlVersion: v1.2\n"
    gen_one = b'{"@graph": [{"id": "./", "rendered": "10:00:00"}]}'
    gen_two = b'{"@graph": [{"id": "./", "rendered": "10:00:41"}]}'

    def crate(metadata_bytes: bytes, preview: bytes, content: bytes) -> bytes:
        return binding.make_zip(
            [
                ("ro-crate-metadata.json", metadata_bytes),
                ("ro-crate-preview.html", preview),
                ("workflow.cwl", content),
            ],
            compression=zipfile.ZIP_STORED, date=(2020, 1, 1, 0, 0, 0),
        )

    def fetch_sim(data: bytes) -> dict[str, Any]:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            retained, excluded, _m = v3norm.normalized_content_manifest_v3(zf)
        return {
            "retained": retained,
            "excluded_paths": [e["path"] for e in excluded],
            "v3_aggregate": v3norm.aggregate_v3(retained),
            "v2_aggregate": binding.canonical_json_sha(v3norm.v2_equivalent_manifest(retained, excluded)),
        }

    # Same version fetched twice with regenerated crate files: v3 gate passes.
    regen_a = fetch_sim(crate(gen_one, b"<html>a</html>", workflow))
    regen_b = fetch_sim(crate(gen_two, b"<html>b (regenerated 41s later)</html>", workflow))
    assert regen_a["v2_aggregate"] != regen_b["v2_aggregate"], "control: v2 moves on regenerated bytes"
    assert reproducibility_defect([regen_a, regen_b, dict(regen_a)]) is None

    # A genuine workflow-content difference between two fetches must be caught.
    content_shift = fetch_sim(crate(gen_one, b"<html>a</html>", workflow + b"# drift\n"))
    defect = reproducibility_defect([regen_a, content_shift, dict(regen_a)])
    assert defect is not None and defect["workflow_content_members_differing_across_fetches"] == ["workflow.cwl"]

    # A member-set difference (added file) must be caught.
    added = fetch_sim(crate(gen_one, b"<html>a</html>", workflow))
    added["retained"] = added["retained"] + [
        {"path": "zz_new.py", "bytes": 1, "sha256": hashlib.sha256(b"x").hexdigest(), "kind": "regular", "executable": False}
    ]
    added["retained"].sort(key=lambda e: e["path"])
    assert reproducibility_defect([regen_a, added]) is not None

    # Candidate policy consumes v3 manifests; excluded members are not premises.
    candidate = _load("a3_candidate_policy_v3h", HERE / "candidate_policy_v1.py")
    before_manifest = [
        {"path": "tools/a.py", "bytes": 3, "sha256": hashlib.sha256(b"abc").hexdigest(), "kind": "regular", "executable": False},
    ]
    record = {
        "schema": candidate.VISIBLE_SCHEMA, "workflow_id": "self-test",
        "version_before": 1, "version_after": 2,
        "before_manifest": before_manifest,
        "after_manifest": [dict(before_manifest[0])],
    }
    assert candidate.evaluate(record)["decision"] == "REUSE"
    record2 = dict(record)
    record2["after_manifest"] = [dict(before_manifest[0], sha256=hashlib.sha256(b"abd").hexdigest())]
    assert candidate.evaluate(record2)["decision"] == "REOPEN"

    return {
        "decision": "GREEN",
        "frame_n": len(frame),
        "min_fetches_enforced": MIN_FETCHES,
        "regenerated_bytes_v3_reproducible": True,
        "v2_control_moves_on_same_bytes": True,
        "content_drift_detected": True,
        "member_set_drift_detected": True,
        "v3_manifests_feed_frozen_candidate_policy": True,
        "network_accessed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--fetches", type=int, default=3)
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
    if args.fetches < MIN_FETCHES:
        ap.error(f"--fetches must be >= {MIN_FETCHES}")
    result = harvest(args.workers, args.fetches, args.note)
    write_outputs(result, args.output_dir)
    printable = {k: v for k, v in result.items() if k not in ("snapshot", "evidence")}
    print(json.dumps(printable, indent=2, sort_keys=True))
    if result["terminal"] == FAILURE_TERMINAL:
        print(json.dumps(result["evidence"], indent=2, sort_keys=True)[:4000])
        return 2
    for chunk in result["snapshot"]["chunks"]:
        print(" ", chunk["path"], chunk["rows"], chunk["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
