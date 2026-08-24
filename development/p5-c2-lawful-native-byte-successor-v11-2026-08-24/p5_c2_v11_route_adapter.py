#!/usr/bin/env python3
"""Execution-free route gate for the distinct P5 C2 V11 byte successor.

The gate materializes the frozen candidate/host split, checks all six V10 byte
classes, records content and permission evidence, and destroys the attempt.
It intentionally does not invoke MOSS, any model, the frozen evaluator, a
benchmark, a scorer, protected data, repository CI, or a test framework.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tarfile
import tempfile
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
FREEZE = HERE / "P5_C2_V11_EXECUTION_FREEZE.json"
TARGET = Path("src/main/java/org/apache/commons/lang3/math/NumberUtils.java")
IDENTITY = "C2_LAWFUL_NATIVE_BYTE_SUCCESSOR__ORION_V11"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


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


def assert_ref(base: Path, ref: dict[str, Any]) -> Path:
    path = (base / ref["path"]).resolve(strict=True)
    if not path.is_file():
        raise RuntimeError(f"frozen artifact is not a regular file: {path}")
    if path.stat().st_size != ref["size_bytes"] or sha256(path) != ref["sha256"]:
        raise RuntimeError(f"frozen artifact identity mismatch: {path}")
    return path


def walk_json_keys(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.append((prefix, str(key)))
            found.extend(walk_json_keys(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_json_keys(child, f"{prefix}[{index}]"))
    return found


def archive_manifest_digest(archive: Path, root_prefix: str) -> tuple[str, int, int]:
    rows: list[dict[str, Any]] = []
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf.getmembers():
            if member.name == root_prefix.rstrip("/"):
                continue
            if not member.name.startswith(root_prefix):
                raise RuntimeError(f"archive member outside frozen root: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"link member not permitted: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            stream = tf.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
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


def safe_extract(archive: Path, destination: Path, root_prefix: str) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf.getmembers():
            if member.name == root_prefix.rstrip("/"):
                continue
            if not member.name.startswith(root_prefix):
                raise RuntimeError(f"archive member outside frozen root: {member.name}")
            relative = Path(member.name[len(root_prefix) :])
            if not relative.parts or relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"unsafe archive member: {member.name}")
            target = destination / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile() or member.issym() or member.islnk():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = tf.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            target.write_bytes(stream.read())


def content_tree_digest(root: Path) -> tuple[str, int]:
    rows: list[bytes] = []
    count = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"symlink forbidden in attempt tree: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            rows.append(relative.encode() + b"\0" + sha256(path).encode() + b"\n")
            count += 1
    return sha256_bytes(b"".join(rows)), count


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


def copy_mount(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    destination.chmod(0o444)
    return {
        "source_sha256": sha256(source),
        "mounted_sha256": sha256(destination),
        "mounted_mode": oct(stat.S_IMODE(destination.stat().st_mode)),
        "relative_mount": "/".join(destination.parts[-2:]),
    }


def validate_certificate(certificate: dict[str, Any], freeze: dict[str, Any]) -> None:
    expected_top = {
        "schema_version",
        "certificate_id",
        "arm_id",
        "observation_id",
        "declared_class",
        "issuance",
        "basis",
        "complete",
    }
    if set(certificate) != expected_top:
        raise RuntimeError("certificate does not match the closed V3 top-level surface")
    if certificate["schema_version"] != "orion.p5.candidate-visible-class-certificate.v3":
        raise RuntimeError("wrong certificate schema version")
    if certificate["arm_id"] != "C2_DIRECT_SELF_EDIT__MOSS":
        raise RuntimeError("certificate predecessor arm mismatch")
    if certificate["declared_class"] != "EXECUTION_REPAIR" or certificate["complete"] is not True:
        raise RuntimeError("certificate class/completeness mismatch")
    issuance = certificate["issuance"]
    if issuance != {
        "candidate_visible": True,
        "input_native": True,
        "issuer_role": "HOST_INPUT_VALIDATOR",
        "native_output_access": False,
        "phase": "BEFORE_CANDIDATE_ACTION",
        "protected_outcome_access": False,
        "sequence": 0,
    }:
        raise RuntimeError("certificate issuance is not the frozen pre-action issuance")
    basis = certificate["basis"]
    proof = basis["fibre_constancy_attestation"]
    if proof != {
        "declared_class": "EXECUTION_REPAIR",
        "proof_ref_sha256": freeze["external_inputs"]["v3_synthetic_conformance"]["sha256"],
        "status": "PROVED_ON_DECLARED_SYNTHETIC_DOMAIN",
    }:
        raise RuntimeError("certificate synthetic proof binding mismatch")
    if basis["domain_scope_sha256"] != freeze["external_inputs"]["v3_synthetic_domain"]["sha256"]:
        raise RuntimeError("certificate synthetic domain mismatch")
    if not HEX64.fullmatch(basis["domain_scope_sha256"]):
        raise RuntimeError("certificate digest form invalid")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--receipt",
        type=Path,
        default=HERE / "P5_C2_V11_SIX_CLASS_GATE_RECEIPT.json",
    )
    args = parser.parse_args()
    if not FREEZE.is_file():
        raise RuntimeError("execution freeze missing")
    freeze = load_json(FREEZE)
    if freeze["successor_identity"] != IDENTITY:
        raise RuntimeError("successor identity mismatch")
    if freeze["released_moss_identity_claimed"] is not False:
        raise RuntimeError("successor was relabelled as released MOSS")
    if freeze["evaluator_execution_authorized"] is not False:
        raise RuntimeError("route gate cannot authorize evaluator execution")

    packet_paths: dict[str, Path] = {}
    for name, ref in freeze["packet_artifacts"].items():
        packet_paths[name] = assert_ref(HERE, ref)
    external_paths: dict[str, Path] = {}
    for name, ref in freeze["external_inputs"].items():
        external_paths[name] = assert_ref(REPO_ROOT, ref)

    forbidden_keys = set(freeze["forbidden_keys_recursive"])
    key_scan_files = 0
    for path in list(packet_paths.values()) + list(external_paths.values()):
        if path.suffix != ".json":
            continue
        value = load_json(path)
        key_scan_files += 1
        hits = [(where, key) for where, key in walk_json_keys(value) if key in forbidden_keys]
        if hits:
            raise RuntimeError(f"forbidden recursive JSON keys in {path}: {hits[:4]}")

    session = load_json(packet_paths["flag_snapshot"])
    session_manifest = load_json(packet_paths["session_manifest"])
    if session_manifest["candidate_outcome_selected"] is not False:
        raise RuntimeError("session is candidate-outcome selected")
    if session_manifest["outcome_or_feedback_bytes_present"] is not False:
        raise RuntimeError("session includes outcome or feedback bytes")
    if session_manifest["case_selection_boundary"] != "INHERITED_POST_OUTCOME_PUBLIC_DEVELOPMENT_CASE__NOT_CONFIRMATORY":
        raise RuntimeError("session case-selection boundary missing")
    if session["tool_dispatches"] or session["agent_tool_registry_at_flag_time"]:
        raise RuntimeError("session unexpectedly embeds tool/result material")
    chunk_refs = session_manifest["chunks"]
    if session_manifest["chunk_count"] != len(chunk_refs) or not chunk_refs:
        raise RuntimeError("session chunk enumeration incomplete")
    for ref in chunk_refs:
        assert_ref(HERE, ref)
    if session_manifest["flag_snapshot_sha256"] != sha256(packet_paths["flag_snapshot"]):
        raise RuntimeError("FlagSnapshot identity mismatch")

    certificate = load_json(packet_paths["certificate"])
    validate_certificate(certificate, freeze)
    boundary = load_json(packet_paths["certificate_authority_boundary"])
    if boundary["natural_case_fibre_proof"] != "NOT_SUPPLIED":
        raise RuntimeError("synthetic proof was promoted to natural-case fibre authority")
    if boundary["revision_authority"] != "NOT_SUPPLIED":
        raise RuntimeError("certificate was promoted to revision authority")

    runtime = load_json(packet_paths["runtime_lock"])
    for binary_name in ("java", "javac"):
        binary = Path(runtime["executables"][binary_name]["path"])
        if sha256(binary) != runtime["executables"][binary_name]["sha256"]:
            raise RuntimeError(f"runtime binary identity mismatch: {binary_name}")
    cases = load_json(packet_paths["public_cases"])
    if cases["authority"] != "PUBLIC_DEVELOPMENT_ONLY" or len(cases["cases"]) < 6:
        raise RuntimeError("public evaluator cases are incomplete or authority-widened")

    archive = external_paths["v6_source_archive"]
    tree_manifest = load_json(external_paths["v6_source_tree_manifest"])
    root_prefix = tree_manifest["archive_root"]
    tree_digest, member_count, member_bytes = archive_manifest_digest(archive, root_prefix)
    if tree_digest != tree_manifest["canonical_member_manifest_sha256"]:
        raise RuntimeError("V6 source tree digest mismatch")

    policy = load_json(packet_paths["write_reset_policy"])
    if policy["candidate_writable_paths"] != [TARGET.as_posix()]:
        raise RuntimeError("write policy widened")
    if policy["attempt_destruction_required"] is not True:
        raise RuntimeError("attempt destruction not required")

    attempt_parent = Path(tempfile.mkdtemp(prefix="p5-c2-v11-route-gate-"))
    attempt = attempt_parent / "attempt"
    attempt.mkdir()
    destroyed = False
    mounts: list[dict[str, Any]] = []
    before_digest = after_digest = target_before = target_after = ""
    candidate_files = 0
    try:
        source_readonly = attempt / "source_readonly"
        safe_extract(archive, source_readonly, root_prefix)
        candidate_source = attempt / "candidate_work" / "source"
        candidate_source.parent.mkdir(parents=True)
        shutil.copytree(source_readonly, candidate_source)
        make_read_only(source_readonly)
        make_read_only(candidate_source)
        mutable_target = candidate_source / TARGET
        mutable_target.chmod(0o644)

        candidate_inputs = attempt / "candidate_inputs"
        candidate_inputs.mkdir()
        for name in (
            "flag_snapshot",
            "session_manifest",
            "session_chunk_0001",
            "certificate",
            "certificate_authority_boundary",
        ):
            destination = candidate_inputs / packet_paths[name].name
            mounts.append(copy_mount(packet_paths[name], destination))
        for name in ("v6_case_body", "v6_task_specification"):
            destination = candidate_inputs / external_paths[name].name
            mounts.append(copy_mount(external_paths[name], destination))
        make_read_only(candidate_inputs)

        host_controlled = attempt / "host_controlled"
        host_controlled.mkdir()
        for name in (
            "public_evaluator",
            "public_cases",
            "runtime_lock",
            "rights_manifest",
            "write_reset_policy",
            "execution_freeze",
            "license_cc0",
            "license_apache",
            "notice_apache",
            "license_openjdk",
        ):
            source = FREEZE if name == "execution_freeze" else packet_paths[name]
            destination = host_controlled / source.name
            mounts.append(copy_mount(source, destination))
        make_read_only(host_controlled)

        forbidden_components = set(freeze["forbidden_attempt_path_components"])
        forbidden_paths = [
            path.relative_to(attempt).as_posix()
            for path in attempt.rglob("*")
            if any(part in forbidden_components for part in path.relative_to(attempt).parts)
        ]
        if forbidden_paths:
            raise RuntimeError(f"forbidden roots entered attempt: {forbidden_paths[:4]}")

        writable_files = []
        for path in candidate_source.rglob("*"):
            mode = stat.S_IMODE(path.stat().st_mode)
            if mode & 0o222:
                writable_files.append(path.relative_to(candidate_source).as_posix())
        if writable_files != [TARGET.as_posix()]:
            raise RuntimeError(f"candidate write surface mismatch: {writable_files}")
        for protected_root in (source_readonly, candidate_inputs, host_controlled):
            for path in [protected_root, *protected_root.rglob("*")]:
                if stat.S_IMODE(path.stat().st_mode) & 0o222:
                    raise RuntimeError(f"host/read-only mount is writable: {path}")

        before_digest, candidate_files = content_tree_digest(candidate_source)
        target_before = sha256(mutable_target)
        # Deliberately no candidate action and no evaluator invocation.
        after_digest, after_count = content_tree_digest(candidate_source)
        target_after = sha256(mutable_target)
        if candidate_files != after_count or before_digest != after_digest:
            raise RuntimeError("execution-free route gate mutated candidate content")
        if target_before != target_after:
            raise RuntimeError("execution-free route gate mutated the sole writable target")
    finally:
        make_removable(attempt_parent)
        shutil.rmtree(attempt_parent)
        destroyed = not attempt_parent.exists()
    if not destroyed:
        raise RuntimeError("attempt destruction could not be verified")

    class_receipts = [
        {
            "class_id": "session",
            "passed": True,
            "evidence": "FlagSnapshot and complete chunk manifest are frozen; no candidate outcome, run output, evaluator feedback, tool dispatch, or protected byte is present.",
        },
        {
            "class_id": "source_mount",
            "passed": True,
            "evidence": f"V6 archive/tree identity passed for {member_count} files and {member_bytes} bytes; read-only source plus one-file ephemeral write overlay materialized.",
        },
        {
            "class_id": "pre_action_certificate",
            "passed": True,
            "evidence": "Host-issued V3-compatible sequence-0 certificate is candidate-visible and input-native; its separate receipt denies natural-case fibre proof and revision authority.",
        },
        {
            "class_id": "public_evaluator",
            "passed": True,
            "evidence": "Frozen public evaluator, public cases, and pinned JDK lock were mounted outside candidate write authority and were not executed.",
        },
        {
            "class_id": "write_reset_policy",
            "passed": True,
            "evidence": "Allowed/forbidden roots were enforced; before/after digests matched and the attempt directory was destroyed.",
        },
        {
            "class_id": "route_adapter",
            "passed": True,
            "evidence": "The separately named content-addressed ORION V11 adapter mounted every preceding byte class and does not claim released MOSS identity.",
        },
    ]
    receipt = {
        "schema_version": "orion.p5.c2.six-class-route-gate-receipt.v11",
        "protocol_id": freeze["protocol_id"],
        "successor_identity": IDENTITY,
        "released_moss_identity_claimed": False,
        "status": "PASS",
        "required_class_count": 6,
        "passed_class_count": sum(row["passed"] for row in class_receipts),
        "class_receipts": class_receipts,
        "source_archive_sha256": sha256(archive),
        "source_tree_manifest_sha256": tree_digest,
        "candidate_tree_before_sha256": before_digest,
        "candidate_tree_after_sha256": after_digest,
        "mutable_target_before_sha256": target_before,
        "mutable_target_after_sha256": target_after,
        "candidate_regular_file_count": candidate_files,
        "json_files_scanned_for_forbidden_keys": key_scan_files,
        "forbidden_recursive_key_hits": 0,
        "forbidden_attempt_path_hits": 0,
        "mount_count": len(mounts),
        "mounts": mounts,
        "attempt_destruction_verified": destroyed,
        "executed": {
            "route_gate": True,
            "moss": False,
            "model": False,
            "coding_agent": False,
            "benchmark": False,
            "public_evaluator": False,
            "protected_scorer": False,
            "protected_data": False,
            "repository_ci": False,
            "test_framework": False,
        },
        "authority": "BYTE_ROUTE_AND_RUNTIME_TASK_ENVIRONMENT_ONLY__NOT_PERFORMANCE",
        "terminal": "P5_C2_V11_SIX_OF_SIX_FROZEN_BYTE_CLASSES_PASS__DISTINCT_SUCCESSOR_ROUTE_MATERIALIZED__NO_MODEL_BENCHMARK_SCORER_OR_OUTCOME_EXECUTED",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
