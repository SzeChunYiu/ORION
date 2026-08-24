#!/usr/bin/env python3
"""Execution-free source/rights/lineage route gate for P5 C2 V12.

The gate materializes only the six V6 candidate-visible components, verifies
their aggregate digest, source-tree lineage and rights mapping, then destroys
the attempt.  It never executes an arm, model, evaluator, benchmark, scorer,
protected datum, repository CI, or test framework.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import tarfile
import tempfile
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
FREEZE = HERE / "P5_C2_V12_EXECUTION_FREEZE.json"
IDENTITY = "C2_SOURCE_NATIVE_VISIBLE_CORE_SUCCESSOR__ORION_V12"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} must contain one JSON object")
    return value


def verify_ref(base: Path, ref: dict[str, Any]) -> Path:
    path = (base / ref["path"]).resolve(strict=True)
    if not path.is_file() or path.stat().st_size != ref["size_bytes"] or sha256(path) != ref["sha256"]:
        raise RuntimeError(f"frozen reference mismatch: {path}")
    return path


def json_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(json_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(json_keys(child))
    return keys


def core_digest(rows: list[dict[str, Any]]) -> str:
    canonical = b"".join(
        row["path"].encode()
        + b"\0"
        + row["sha256"].encode()
        + b"\0"
        + str(row["size_bytes"]).encode()
        + b"\n"
        for row in sorted(rows, key=lambda value: value["path"])
    )
    return sha256_bytes(canonical)


def archive_tree_digest(archive: Path, root_prefix: str) -> tuple[str, int, int]:
    rows: list[dict[str, Any]] = []
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf.getmembers():
            if member.name == root_prefix.rstrip("/"):
                continue
            if not member.name.startswith(root_prefix):
                raise RuntimeError(f"archive member outside root: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"archive link forbidden: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            stream = tf.extractfile(member)
            if stream is None:
                raise RuntimeError(f"archive member unreadable: {member.name}")
            data = stream.read()
            rows.append(
                {
                    "path": member.name[len(root_prefix) :],
                    "mode": oct(member.mode),
                    "size_bytes": len(data),
                    "sha256": sha256_bytes(data),
                }
            )
    rows.sort(key=lambda row: row["path"])
    canonical = b"".join(
        row["path"].encode()
        + b"\0"
        + row["mode"].encode()
        + b"\0"
        + str(row["size_bytes"]).encode()
        + b"\0"
        + row["sha256"].encode()
        + b"\n"
        for row in rows
    )
    return sha256_bytes(canonical), len(rows), sum(row["size_bytes"] for row in rows)


def make_read_only(root: Path) -> None:
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_file():
            path.chmod(0o444)
        elif path.is_dir():
            path.chmod(0o555)
    root.chmod(0o555)


def make_removable(root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)
        elif path.is_file():
            path.chmod(0o644)
    root.chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=HERE / "P5_C2_V12_SOURCE_LINEAGE_ROUTE_RECEIPT.json")
    args = parser.parse_args()
    freeze = load_json(FREEZE)
    if freeze["successor_identity"] != IDENTITY:
        raise RuntimeError("V12 successor identity mismatch")
    if freeze["aggregation_with_v11_authorized"] is not False:
        raise RuntimeError("V11 aggregation was silently authorized")
    if freeze["released_moss_identity_claimed"] is not False:
        raise RuntimeError("distinct successor was relabelled as released MOSS")

    packet = {name: verify_ref(HERE, ref) for name, ref in freeze["packet_artifacts"].items()}
    external = {name: verify_ref(REPO_ROOT, ref) for name, ref in freeze["external_inputs"].items()}
    acceptance = load_json(external["v6_six_arm_acceptance"])
    core = load_json(external["v6_core_index"])
    rights = load_json(external["v6_rights_manifest"])
    provenance = load_json(external["v6_public_provenance"])
    lineage = load_json(packet["source_rights_lineage"])
    basis = load_json(packet["explicit_acceptance_basis"])

    c2_receipts = [row for row in acceptance["receipts"] if row["arm_code"] == "C2"]
    if len(c2_receipts) != 1:
        raise RuntimeError("V6 C2 acceptance receipt is not unique")
    c2 = c2_receipts[0]
    if c2["before"] != {"bound": 7, "blocking": 14}:
        raise RuntimeError("V6 C2 predecessor basis changed")
    if c2["after_shared_core_only"] != {"bound": 9, "blocking": 12}:
        raise RuntimeError("V6 C2 two-field arithmetic changed")
    if set(c2["field_bindings"]) != {
        "inputs.candidate_visible_case_bytes",
        "rights.task_and_benchmark_content",
        "runtime.task_environment",
    }:
        raise RuntimeError("V6 C2 acceptance field set changed")
    if c2["field_bindings"]["runtime.task_environment"]["status"] != "BLOCKING":
        raise RuntimeError("V12 improperly inherited V11 runtime closure")
    if basis["permitted_field_closures"] != [
        "inputs.candidate_visible_case_bytes",
        "rights.task_and_benchmark_content",
    ]:
        raise RuntimeError("V12 field closure scope widened")

    forbidden = set(freeze["forbidden_keys_recursive"])
    scanned_json = 0
    for path in [*packet.values(), external["v6_case_body"], external["v6_core_index"]]:
        if path.suffix == ".json":
            scanned_json += 1
            hits = forbidden.intersection(json_keys(load_json(path)))
            if hits:
                raise RuntimeError(f"forbidden candidate/packet JSON keys in {path}: {sorted(hits)}")

    index_rows = core["components"]
    if len(index_rows) != 6 or core["candidate_visible_component_count"] != 6:
        raise RuntimeError("V6 candidate core does not contain exactly six components")
    if core_digest(index_rows) != core["candidate_visible_core_sha256"]:
        raise RuntimeError("V6 candidate core aggregate digest mismatch")
    for row in index_rows:
        source = REPO_ROOT / "development/p5-common-visible-case-rights-v6-2026-08-23" / row["path"]
        if sha256(source) != row["sha256"] or source.stat().st_size != row["size_bytes"]:
            raise RuntimeError(f"V6 core component drifted: {source}")

    source_row = next(row for row in index_rows if row["role"] == "complete buggy source snapshot")
    archive = REPO_ROOT / "development/p5-common-visible-case-rights-v6-2026-08-23" / source_row["path"]
    source_tree = load_json(external["v6_source_tree_manifest"])
    tree_digest, tree_files, tree_bytes = archive_tree_digest(archive, source_tree["archive_root"])
    if tree_digest != source_tree["canonical_member_manifest_sha256"]:
        raise RuntimeError("source archive canonical tree lineage mismatch")
    if provenance["source_identity"]["buggy_commit"] != source_tree["upstream_commit"]:
        raise RuntimeError("buggy source commit lineage mismatch")
    if provenance["source_identity"]["buggy_tree"] != source_tree["upstream_tree"]:
        raise RuntimeError("buggy source tree lineage mismatch")
    if provenance["source_identity"]["known_public_fix_bytes_in_candidate_core"] is not False:
        raise RuntimeError("known fixed bytes entered candidate core")
    if rights["rights_status"] != "BOUND_FOR_LISTED_SHARED_CASE_COMPONENTS":
        raise RuntimeError("V6 rights status changed")
    if core["rights_manifest"]["sha256"] != sha256(external["v6_rights_manifest"]):
        raise RuntimeError("core-to-rights lineage mismatch")
    if lineage["candidate_visible_core_sha256"] != core["candidate_visible_core_sha256"]:
        raise RuntimeError("V12 lineage manifest core mismatch")

    attempt_parent = Path(tempfile.mkdtemp(prefix="p5-c2-v12-lineage-"))
    attempt = attempt_parent / "attempt"
    visible = attempt / "candidate_visible"
    visible.mkdir(parents=True)
    destroyed = False
    mounted_rows: list[dict[str, Any]] = []
    try:
        for row in index_rows:
            source = REPO_ROOT / "development/p5-common-visible-case-rights-v6-2026-08-23" / row["path"]
            relative = Path(row["path"]).relative_to("candidate_visible")
            destination = visible / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            mounted_rows.append(
                {
                    "path": row["path"],
                    "sha256": sha256(destination),
                    "size_bytes": destination.stat().st_size,
                    "license_spdx_id": row["license_spdx_id"],
                    "role": row["role"],
                    "mode": "0o444",
                }
            )
        make_read_only(visible)
        if core_digest(mounted_rows) != core["candidate_visible_core_sha256"]:
            raise RuntimeError("mounted candidate core aggregate mismatch")
        for path in [visible, *visible.rglob("*")]:
            if stat.S_IMODE(path.stat().st_mode) & 0o222:
                raise RuntimeError(f"candidate-visible source/rights mount is writable: {path}")
        forbidden_components = set(freeze["forbidden_attempt_path_components"])
        bad_paths = [
            path.relative_to(attempt).as_posix()
            for path in attempt.rglob("*")
            if forbidden_components.intersection(path.relative_to(attempt).parts)
        ]
        if bad_paths:
            raise RuntimeError(f"forbidden attempt paths materialized: {bad_paths[:4]}")
    finally:
        make_removable(attempt_parent)
        shutil.rmtree(attempt_parent)
        destroyed = not attempt_parent.exists()
    if not destroyed:
        raise RuntimeError("attempt destruction not verified")

    receipt = {
        "schema_version": "orion.p5.c2.source-rights-lineage-route-receipt.v12",
        "protocol_id": freeze["protocol_id"],
        "successor_identity": IDENTITY,
        "status": "PASS",
        "route_class": "SOURCE_NATIVE_CANDIDATE_VISIBLE_BYTES_RIGHTS_AND_LINEAGE",
        "required_component_count": 6,
        "mounted_component_count": len(mounted_rows),
        "candidate_visible_bytes": sum(row["size_bytes"] for row in mounted_rows),
        "candidate_visible_core_sha256": core_digest(mounted_rows),
        "source_archive_sha256": sha256(archive),
        "source_tree_manifest_sha256": tree_digest,
        "source_tree_regular_files": tree_files,
        "source_tree_regular_bytes": tree_bytes,
        "mounted_components": mounted_rows,
        "rights_status": rights["rights_status"],
        "known_fixed_bytes_in_candidate_core": False,
        "post_outcome_public_development_boundary_retained": True,
        "json_files_scanned_for_forbidden_keys": scanned_json,
        "forbidden_recursive_key_hits": 0,
        "forbidden_attempt_path_hits": 0,
        "all_mounted_bytes_read_only": True,
        "attempt_destruction_verified": destroyed,
        "field_acceptance": {
            "inputs.candidate_visible_case_bytes": "PASS",
            "rights.task_and_benchmark_content": "PASS_FOR_LISTED_SHARED_CORE_ONLY",
        },
        "identity_boundaries": {
            "released_moss_identity_claimed": False,
            "aggregation_with_v11_authorized": False,
            "v11_runtime_task_environment_inherited": False,
        },
        "executed": {
            "route_gate": True,
            "moss": False,
            "model": False,
            "coding_agent": False,
            "evaluator": False,
            "benchmark": False,
            "scorer": False,
            "protected_data": False,
            "repository_ci": False,
            "test_framework": False,
        },
        "terminal": "P5_C2_V12_SIX_OF_SIX_SOURCE_NATIVE_COMPONENTS_PASS__CORE_RIGHTS_AND_LINEAGE_BOUND__DISTINCT_NONAGGREGATED_SUCCESSOR__NO_OUTCOME_EXECUTED",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
