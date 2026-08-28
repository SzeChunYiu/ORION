#!/usr/bin/env python3
"""Replay the frozen ORION-11 v2.2.4 primary and replication exactly.

This is a reproducibility harness, not a new experiment.  It grants no merge,
freeze, submission, novelty, external-review, or model-generalization authority.
Every byte mismatch is retained as an adverse replay result.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
from typing import Any


class ReplayError(RuntimeError):
    """Raised when a frozen replay precondition or execution step fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayError(message)


def _resolved_repo_file(repo_root: Path, relative: str) -> Path:
    _require(bool(relative), "bound path is empty")
    root = repo_root.resolve()
    candidate = (root / relative).resolve()
    _require(root in candidate.parents, f"bound path escapes repository: {relative}")
    _require(candidate.is_file(), f"bound file missing: {relative}")
    return candidate


def _verify_bound_file(repo_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    relative = spec.get("path")
    expected = spec.get("sha256")
    _require(isinstance(relative, str), "bound file path must be a string")
    _require(isinstance(expected, str) and len(expected) == 64, f"invalid digest binding: {relative}")
    path = _resolved_repo_file(repo_root, relative)
    actual = sha256_file(path)
    _require(actual == expected, f"digest mismatch: {relative}: expected {expected}, got {actual}")
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": actual,
        "binding_pass": True,
    }


def load_protocol(path: Path) -> dict[str, Any]:
    try:
        protocol = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError(f"protocol load failed: {exc}") from exc
    _require(isinstance(protocol, dict), "protocol root must be an object")
    _require(
        protocol.get("schema_version") == "orion.orion11.lunarc-replay-protocol.v1",
        "unexpected protocol schema",
    )
    lanes = protocol.get("lanes")
    _require(isinstance(lanes, list) and lanes, "protocol lanes must be a non-empty list")
    names = [lane.get("name") for lane in lanes if isinstance(lane, dict)]
    _require(len(names) == len(lanes) and all(isinstance(name, str) for name in names), "lane name missing")
    _require(len(set(names)) == len(names), "duplicate lane name in protocol")
    _require(set(names) == {"primary", "replication"}, "protocol must bind primary and replication lanes")
    return protocol


def _decompress_bound(
    repo_root: Path,
    spec: dict[str, Any],
    destination: Path,
) -> dict[str, Any]:
    compressed = _verify_bound_file(repo_root, spec)
    source = _resolved_repo_file(repo_root, spec["path"])
    try:
        payload = gzip.decompress(source.read_bytes())
    except (OSError, EOFError) as exc:
        raise ReplayError(f"gzip decode failed: {spec['path']}: {exc}") from exc
    expected_plain = spec.get("decompressed_sha256")
    _require(
        isinstance(expected_plain, str) and len(expected_plain) == 64,
        f"missing decompressed digest binding: {spec['path']}",
    )
    actual_plain = hashlib.sha256(payload).hexdigest()
    _require(
        actual_plain == expected_plain,
        f"decompressed digest mismatch: {spec['path']}: expected {expected_plain}, got {actual_plain}",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return {
        "archive": compressed,
        "materialized_path": destination.name,
        "materialized_bytes": len(payload),
        "materialized_sha256": actual_plain,
        "binding_pass": True,
    }


def materialize_world(
    repo_root: Path,
    lane: dict[str, Any],
    destination: Path,
) -> dict[str, Any]:
    inputs = lane.get("inputs")
    _require(isinstance(inputs, dict), f"lane inputs missing: {lane.get('name')}")
    destination.mkdir(parents=True, exist_ok=False)
    public = _decompress_bound(
        repo_root,
        inputs["world_public_gzip"],
        destination / "WORLD_PUBLIC.jsonl",
    )
    protected = _decompress_bound(
        repo_root,
        inputs["protected_response_matrix_gzip"],
        destination / "PROTECTED_RESPONSE_MATRIX.jsonl",
    )
    freeze_spec = inputs["world_freeze"]
    freeze = _verify_bound_file(repo_root, freeze_spec)
    shutil.copyfile(
        _resolved_repo_file(repo_root, freeze_spec["path"]),
        destination / "WORLD_FREEZE.json",
    )
    _require(
        sha256_file(destination / "WORLD_FREEZE.json") == freeze["sha256"],
        "world-freeze copy drift",
    )
    return {
        "world_public": public,
        "protected_response_matrix": protected,
        "world_freeze": freeze,
        "all_input_bindings_pass": True,
    }


def compare_exact(actual: Path, expected: Path) -> dict[str, Any]:
    _require(expected.is_file(), f"expected comparison file missing: {expected}")
    if not actual.is_file():
        return {
            "actual_path": str(actual),
            "expected_path": str(expected),
            "actual_exists": False,
            "expected_bytes": expected.stat().st_size,
            "expected_sha256": sha256_file(expected),
            "byte_equal": False,
            "terminal": "ACTUAL_MISSING__PRESERVE_DISCREPANCY",
        }
    actual_digest = sha256_file(actual)
    expected_digest = sha256_file(expected)
    equal = actual.read_bytes() == expected.read_bytes()
    return {
        "actual_path": str(actual),
        "expected_path": str(expected),
        "actual_exists": True,
        "actual_bytes": actual.stat().st_size,
        "expected_bytes": expected.stat().st_size,
        "actual_sha256": actual_digest,
        "expected_sha256": expected_digest,
        "byte_equal": equal,
        "terminal": "BYTE_IDENTICAL" if equal else "BYTE_DIFFERENT__PRESERVE_DISCREPANCY",
    }


def _run_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    stdout_path: Path,
    stderr_path: Path,
) -> dict[str, Any]:
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr)
    record = {
        "argv": command,
        "returncode": completed.returncode,
        "completed": completed.returncode == 0,
        "stdout": {
            "path": stdout_path.name,
            "bytes": stdout_path.stat().st_size,
            "sha256": sha256_file(stdout_path),
        },
        "stderr": {
            "path": stderr_path.name,
            "bytes": stderr_path.stat().st_size,
            "sha256": sha256_file(stderr_path),
        },
    }
    return record


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError(f"JSON output load failed: {path}: {exc}") from exc
    _require(isinstance(value, dict), f"JSON output root is not an object: {path}")
    return value


def output_summary(result_path: Path, independent_path: Path) -> dict[str, Any]:
    summary = {
        "scientific_terminal": None,
        "independent_verdict": None,
        "score_mismatch_count": None,
        "analysis_mismatch_count": None,
    }
    if result_path.is_file():
        summary["scientific_terminal"] = _json_object(result_path).get("terminal")
    if independent_path.is_file():
        independent = _json_object(independent_path)
        summary.update(
            {
                "independent_verdict": independent.get("verdict"),
                "score_mismatch_count": independent.get("score_mismatch_count"),
                "analysis_mismatch_count": independent.get("analysis_mismatch_count"),
            }
        )
    return summary


def run_lane(
    repo_root: Path,
    protocol: dict[str, Any],
    lane: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    name = lane["name"]
    lane_root = output_root / name
    lane_root.mkdir(parents=True, exist_ok=False)
    world_dir = lane_root / "world"
    run_dir = lane_root / "run"
    expected_dir = lane_root / "expected"
    run_dir.mkdir()
    expected_dir.mkdir()
    world_receipt = materialize_world(repo_root, lane, world_dir)

    execution = _verify_bound_file(repo_root, lane["execution_freeze"])
    expected_outputs = lane["expected_outputs"]
    archived_raw = _decompress_bound(
        repo_root,
        expected_outputs["raw_results_gzip"],
        expected_dir / "RAW_RESULTS.jsonl",
    )
    expected_result = _verify_bound_file(repo_root, expected_outputs["result"])
    expected_independent = _verify_bound_file(repo_root, expected_outputs["independent_verification"])

    environment = os.environ.copy()
    source_path = str(repo_root / "src")
    environment["PYTHONPATH"] = source_path + (
        os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else ""
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    campaign_script = _resolved_repo_file(repo_root, protocol["campaign_script"]["path"])
    verifier_script = _resolved_repo_file(repo_root, protocol["independent_verifier"]["path"])
    execution_path = _resolved_repo_file(repo_root, lane["execution_freeze"]["path"])

    campaign = _run_command(
        [
            sys.executable,
            str(campaign_script),
            "--world-dir",
            str(world_dir),
            "--execution-freeze",
            str(execution_path),
            "--outdir",
            str(run_dir),
        ],
        cwd=repo_root,
        env=environment,
        stdout_path=lane_root / "campaign.stdout",
        stderr_path=lane_root / "campaign.stderr",
    )
    independent_path = run_dir / "INDEPENDENT_VERIFICATION.json"
    if campaign["completed"]:
        independent = _run_command(
            [
                sys.executable,
                str(verifier_script),
                "--world-public",
                str(world_dir / "WORLD_PUBLIC.jsonl"),
                "--protected",
                str(world_dir / "PROTECTED_RESPONSE_MATRIX.jsonl"),
                "--raw-results",
                str(run_dir / "RAW_RESULTS.jsonl"),
                "--execution-freeze",
                str(execution_path),
                "--result",
                str(run_dir / "RESULT.json"),
                "--out",
                str(independent_path),
            ],
            cwd=repo_root,
            env=environment,
            stdout_path=lane_root / "independent.stdout",
            stderr_path=lane_root / "independent.stderr",
        )
    else:
        independent = {
            "completed": False,
            "returncode": None,
            "not_run_reason": "CAMPAIGN_NONZERO_EXIT",
        }

    comparisons = {
        "raw_results": compare_exact(run_dir / "RAW_RESULTS.jsonl", expected_dir / "RAW_RESULTS.jsonl"),
        "result": compare_exact(
            run_dir / "RESULT.json",
            _resolved_repo_file(repo_root, expected_outputs["result"]["path"]),
        ),
        "independent_verification": compare_exact(
            independent_path,
            _resolved_repo_file(repo_root, expected_outputs["independent_verification"]["path"]),
        ),
    }
    all_equal = all(item["byte_equal"] for item in comparisons.values())
    summary = output_summary(run_dir / "RESULT.json", independent_path)
    verifier_pass = (
        independent["completed"]
        and summary["independent_verdict"] == "PASS"
        and summary["score_mismatch_count"] == 0
        and summary["analysis_mismatch_count"] == 0
    )
    exact = campaign["completed"] and verifier_pass and all_equal
    receipt = {
        "lane": name,
        "world_materialization": world_receipt,
        "execution_freeze": execution,
        "expected_bindings": {
            "raw_results": archived_raw,
            "result": expected_result,
            "independent_verification": expected_independent,
        },
        "campaign": campaign,
        "independent_verifier": independent,
        "comparisons": comparisons,
        "all_required_byte_comparisons_pass": all_equal,
        **summary,
        "terminal": "EXACT_ARCHIVE_REPLAY" if exact else "REPLAY_DRIFT__PRESERVE_DISCREPANCY",
    }
    return receipt


def _environment_receipt() -> dict[str, Any]:
    slurm_keys = (
        "SLURM_JOB_ID",
        "SLURM_JOB_NAME",
        "SLURM_JOB_NODELIST",
        "SLURM_JOB_PARTITION",
        "SLURM_CPUS_PER_TASK",
        "SLURM_MEM_PER_NODE",
        "SLURM_SUBMIT_DIR",
    )
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "cpu_count": os.cpu_count(),
        "slurm": {key: os.environ.get(key) for key in slurm_keys},
    }


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    repo_root = args.repo_root.resolve()
    protocol_path = args.protocol.resolve()
    actual_protocol_sha = sha256_file(protocol_path)
    _require(
        actual_protocol_sha == args.expected_protocol_sha256,
        f"protocol digest mismatch: expected {args.expected_protocol_sha256}, got {actual_protocol_sha}",
    )
    protocol = load_protocol(protocol_path)
    source_checks = [
        _verify_bound_file(repo_root, source_spec)
        for source_spec in protocol.get("source_files", [])
    ]
    _require(bool(source_checks), "protocol source_files binding is empty")
    lanes = []
    for lane_spec in protocol["lanes"]:
        try:
            lanes.append(run_lane(repo_root, protocol, lane_spec, args.outdir.resolve()))
        except Exception as exc:
            lanes.append(
                {
                    "lane": lane_spec.get("name"),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "all_required_byte_comparisons_pass": False,
                    "independent_verdict": None,
                    "score_mismatch_count": None,
                    "analysis_mismatch_count": None,
                    "terminal": "REPLAY_LANE_FAILED__PRESERVE_NEGATIVE",
                }
            )
    all_equal = len(lanes) == 2 and all(
        lane.get("all_required_byte_comparisons_pass") is True for lane in lanes
    )
    all_verifiers_pass = all(
        lane.get("independent_verdict") == "PASS"
        and lane.get("score_mismatch_count") == 0
        and lane.get("analysis_mismatch_count") == 0
        for lane in lanes
    )
    receipt = {
        "schema_version": "orion.orion11.lunarc-replay-job-output.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "replay_id": protocol["replay_id"],
        "source_binding": {
            "source_commit": args.source_commit,
            "source_archive_sha256": args.source_archive_sha256,
            "protocol_path": str(args.protocol.relative_to(args.repo_root)),
            "protocol_sha256": actual_protocol_sha,
            "clean_source_mode": "GIT_ARCHIVE_OF_EXACT_BOUND_COMMIT__NO_WORKTREE_STATE",
        },
        "environment": _environment_receipt(),
        "source_file_checks": source_checks,
        "lanes": lanes,
        "all_required_byte_comparisons_pass": all_equal,
        "all_independent_verifiers_pass": all_verifiers_pass,
        "historical_broad_h1_modified": False,
        "historical_prospective_order_status": "CANNOT_CHECK_HISTORICAL_PROSPECTIVE_ORDER",
        "authority": "LUNARC_DETERMINISTIC_REPLAY_ONLY__NO_EXTERNAL_REVIEW_OR_FREEZE_AUTHORITY",
        "terminal": (
            "EXACT_PRIMARY_AND_REPLICATION_ARCHIVE_REPLAY"
            if all_equal and all_verifiers_pass
            else "REPLAY_DISCREPANCY__PRESERVE_NEGATIVE"
        ),
    }
    return receipt, 0 if all_equal and all_verifiers_pass else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--expected-protocol-sha256", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-archive-sha256", required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=False)
    try:
        receipt, returncode = execute(args)
    except Exception as exc:  # Preserve fail-closed execution evidence.
        receipt = {
            "schema_version": "orion.orion11.lunarc-replay-job-output.v1",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source_binding": {
                "source_commit": args.source_commit,
                "source_archive_sha256": args.source_archive_sha256,
                "protocol": str(args.protocol),
                "expected_protocol_sha256": args.expected_protocol_sha256,
            },
            "environment": _environment_receipt(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "all_required_byte_comparisons_pass": False,
            "all_independent_verifiers_pass": False,
            "authority": "NONE__FAILED_REPLAY_GRANTS_NO_AUTHORITY",
            "terminal": "REPLAY_EXECUTION_FAILED__PRESERVE_NEGATIVE",
        }
        returncode = 1
    receipt_path = args.outdir / "LUNARC_REPLAY_JOB_OUTPUT_V1.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"receipt": str(receipt_path), "terminal": receipt["terminal"]}, sort_keys=True))
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
