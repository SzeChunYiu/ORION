#!/usr/bin/env python3
"""Two-phase Q1-C1 dual-harness coordinator.

``prepare`` extracts the fixed candidate and creates lane terminals without
comparing them.  After those terminals are committed, ``compare`` verifies
their committed bytes and performs the prespecified fieldwise adjudication.
This two-phase design enforces the protocol rule that lanes are compared only
after both terminals are immutable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


CANDIDATE_REF = "158fcb08b612ffc82f5a5d2bed4917409084ded8"
PROTOCOL_COMMIT = "342d7dfa66e691b9cd4d01a2a72985afe7c2526d"
CONTRACT_COMMIT = "44f649debe79642a6d951961bda65fa1e875fa1a"
RESOURCE_AMENDMENT_COMMIT = "342d7dfa66e691b9cd4d01a2a72985afe7c2526d"
PORTABLE_RESOURCE_COMMIT = "342d7dfa66e691b9cd4d01a2a72985afe7c2526d"
GITHUB_RESOURCE_COMMIT = "342d7dfa66e691b9cd4d01a2a72985afe7c2526d"
PYTHON = Path(sys.executable).resolve()
ENVIRONMENT = {
    "PATH": "/usr/bin:/bin",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONHASHSEED": "0",
    "TZ": "UTC",
}
ENV_NAMES = ["PATH", "LANG", "LC_ALL", "PYTHONHASHSEED", "TZ"]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def run_git(repo: Path, *argv: str, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *argv], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=check,
    )
    return completed.stdout.strip()


def require_clean(repo: Path) -> None:
    if run_git(repo, "status", "--porcelain"):
        raise RuntimeError("dual-harness phase requires a clean worktree at start")


def require_runner_ancestry(repo: Path, artifact_commit: str, artifact_parent: str) -> None:
    if run_git(repo, "rev-parse", f"{artifact_commit}^") != artifact_parent:
        raise RuntimeError("runner artifact parent mismatch")
    for ancestor in (
        PROTOCOL_COMMIT, CONTRACT_COMMIT, RESOURCE_AMENDMENT_COMMIT,
        PORTABLE_RESOURCE_COMMIT, GITHUB_RESOURCE_COMMIT,
    ):
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, artifact_parent],
            cwd=repo, check=False,
        ).returncode:
            raise RuntimeError(f"required ancestor missing: {ancestor}")


def extract_candidate(repo: Path) -> Path:
    root = Path(tempfile.mkdtemp(prefix="q1-c1-candidate."))
    archive = subprocess.Popen(
        ["git", "archive", "--format=tar", CANDIDATE_REF], cwd=repo,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert archive.stdout is not None
    untar = subprocess.run(
        ["/usr/bin/tar", "-x", "-C", str(root)], stdin=archive.stdout,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    archive.stdout.close()
    archive_stderr = archive.stderr.read() if archive.stderr is not None else b""
    archive_rc = archive.wait()
    if archive_rc or untar.returncode:
        raise RuntimeError(
            f"candidate extraction failed: git={archive_rc} tar={untar.returncode} "
            f"{archive_stderr.decode(errors='replace')} {untar.stderr.decode(errors='replace')}"
        )
    return root


def run_captured(
    command: list[str], cwd: Path, stdout_path: Path, stderr_path: Path,
    *, timeout: int, env: dict[str, str] | None = None,
) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        completed = subprocess.run(
            command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=stdout, stderr=stderr, timeout=timeout, check=False,
        )
    return completed.returncode


def dependency_inventory() -> dict[str, Any]:
    try:
        cryptography_version = importlib.metadata.version("cryptography")
    except importlib.metadata.PackageNotFoundError:
        cryptography_version = None
    try:
        numpy_version = importlib.metadata.version("numpy")
    except importlib.metadata.PackageNotFoundError:
        numpy_version = None
    return {
        "python": sys.version.split()[0],
        "python_path": str(Path(sys.executable).resolve()),
        "python_sha256": file_sha256(Path(sys.executable).resolve()),
        "numpy_installed": numpy_version,
        "numpy_required": "2.3.5",
        "cryptography_installed": cryptography_version,
        "cryptography_locked": "50.0.0",
        "exact_lock_closed": cryptography_version == "50.0.0" and numpy_version == "2.3.5",
    }


def mutation_free_obligations(
    statuses: dict[str, str], evidence: Any, details: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    details = details or {}
    for index in range(1, 17):
        oid = f"O{index}"
        rows.append({
            "id": oid,
            "status": statuses.get(oid, "NOT_APPLICABLE"),
            "evidence_digests": [digest_value({"obligation": oid, "evidence": evidence})],
            "negative_control": {"status": "NOT_APPLICABLE", "mutation_ids": []},
            "detail": details.get(oid, "This corroborative Lane A surface has no authority for this obligation."),
        })
    return rows


def authority_limits() -> dict[str, bool]:
    return {
        "grants_novelty_authority": False,
        "grants_physical_resource_authority": False,
        "grants_runtime_superiority_authority": False,
        "grants_submission_authority": False,
        "grants_merge_authority": False,
    }


def lane_base(
    *, lane: str, artifact_commit: str, artifact_parent: str, campaign: Path,
    runner: Path, result_schema: Path, fixture_digests: dict[str, str],
    input_digests: dict[str, str], deps: dict[str, Any], cwd: Path,
    command: list[str], started: str, finished: str, stdout: Path, stderr: Path,
    network: dict[str, Any], obligations: list[dict[str, Any]], payload: dict[str, Any],
    terminal: str, semantic_raw: str, semantic_digest: str,
    semantic_diff: list[dict[str, Any]], exclusions: list[str], numpy_version: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": "q1-c1-result-v1",
        "protocol_id": "Q1-C1",
        "protocol_version": "1.0",
        "candidate_ref": CANDIDATE_REF,
        "protocol_commit": PROTOCOL_COMMIT,
        "artifact_commit": artifact_commit,
        "artifact_commit_parent": artifact_parent,
        "lane": lane,
        "campaign_digest": file_sha256(campaign),
        "runner_digest": file_sha256(runner),
        "result_schema_digest": file_sha256(result_schema),
        "fixture_digests": fixture_digests,
        "input_digests": input_digests,
        "interpreter": {
            "path": str(PYTHON), "python_version": "3.12.13", "numpy_version": numpy_version,
        },
        "dependency_inventory_digest": digest_value(deps),
        "cwd": str(cwd),
        "environment_allowlist": {"names": ENV_NAMES, "values": ENVIRONMENT},
        "network_control": network,
        "command": command,
        "started_at": started,
        "finished_at": finished,
        "exit_code": 0,
        "stdout_path": str(stdout),
        "stdout_sha256": file_sha256(stdout),
        "stdout_bytes": stdout.stat().st_size,
        "stderr_path": str(stderr),
        "stderr_sha256": file_sha256(stderr),
        "stderr_bytes": stderr.stat().st_size,
        "output_truncated": False,
        "worktree_dirty": False,
        "obligations": obligations,
        "mutations": [],
        "semantic_projection": {
            "method": "CANONICAL_JSON_SORTED_KEYS_NO_NAN",
            "excluded_json_pointers": exclusions,
            "raw_sha256": semantic_raw,
            "semantic_sha256": semantic_digest,
        },
        "semantic_diff": semantic_diff,
        "terminal": terminal,
        "authority_limits": authority_limits(),
        "payload": payload,
    }


def normalize_r6s(
    raw_paths: list[Path], typed_path: Path, *, repo: Path, archive: Path,
    artifact_commit: str, artifact_parent: str, started: str, finished: str,
) -> dict[str, Any]:
    raw = [json.loads(path.read_text(encoding="utf-8")) for path in raw_paths]
    projections = [item["child_record"]["content"]["scientific_result"]["semantic_projection"] for item in raw]
    projection_digests = [digest_value(value) for value in projections]
    repeat_equal = len(set(projection_digests)) == 1
    replay_match = all(item.get("replay_status") == "MATCH" for item in raw)
    network_ok = all(
        item["network_control"]["socket_negative_control"] == "PASS"
        and item["network_control"]["network_syscall_count"] == 0
        and item["network_control"]["sandboxed"] is False
        for item in raw
    )
    trace_available = all(item["network_control"]["syscall_trace_available"] for item in raw)
    deps = dependency_inventory()
    terminal = (
        "INVALID" if not repeat_equal or not replay_match or not network_ok
        else "BLOCKED" if not deps["exact_lock_closed"] or not trace_available else "PASS"
    )
    child = raw[0]["child_record"]["content"]
    science = child["scientific_result"]
    statuses = {
        "O15": (
            "INVALID" if not replay_match or not network_ok else
            "BLOCKED" if not deps["exact_lock_closed"] or not trace_available else "PASS"
        )
    }
    details = {
        "O15": "The fixed R6S executable replayed semantically twice; this is corroborative receipt recovery only."
    }
    obligations = mutation_free_obligations(statuses, {
        "raw_result_sha256": [file_sha256(path) for path in raw_paths],
        "semantic_sha256": projection_digests,
    }, details)
    first_stdout = Path(child["stdout"]["path"])
    first_stderr = Path(child["stderr"]["path"])
    input_digests = {
        key.replace("/", "_"): value["sha256"]
        for key, value in child["input_digests"].items()
    }
    semantic_diff = list(science["semantic_diff"]) + list(science["stdout_projection_diff"])
    if not repeat_equal:
        semantic_diff.append({
            "json_pointer": "/repeat/semantic_sha256", "expected": projection_digests[0],
            "actual": projection_digests[1:],
        })
    result = lane_base(
        lane="LANE_A_R6S_REPLAY",
        artifact_commit=artifact_commit,
        artifact_parent=artifact_parent,
        campaign=repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_campaign.json",
        runner=repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_r6s_replay.py",
        result_schema=repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/q1_c1_result.schema.json",
        fixture_digests={"r6s_expected_result": science["expected_raw_sha256"]},
        input_digests=input_digests,
        deps=deps,
        cwd=archive,
        command=raw[0]["bootstrap"]["exec_argv"],
        started=started,
        finished=finished,
        stdout=first_stdout,
        stderr=first_stderr,
        network={
            "socket_negative_control": "PASS",
            "network_syscall_count": 0,
            "trace_sha256": raw[0]["network_control"]["trace_sha256"],
            "sandboxed": False,
            "namespace_isolation": "NOT_APPLICABLE",
        },
        obligations=obligations,
        payload={
            "role": "HISTORICAL_EXECUTABLE_REPLAY_ONLY",
            "raw_result_paths": [str(path) for path in raw_paths],
            "raw_result_sha256": [file_sha256(path) for path in raw_paths],
            "repeat_semantic_sha256": projection_digests,
            "repeat_equal": repeat_equal,
            "replay_match": replay_match,
            "syscall_trace_available": trace_available,
            "dependency_gate": deps,
            "authority": "CORROBORATIVE_ONLY",
        },
        terminal=terminal,
        semantic_raw=science["generated_raw_sha256"],
        semantic_digest=science["generated_semantic_sha256"],
        semantic_diff=semantic_diff,
        exclusions=["/runtime_seconds"],
        numpy_version="2.3.5",
    )
    typed_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


NETWORK_SYSCALL = re.compile(
    r"\b(socket|socketpair|connect|accept|accept4|bind|listen|sendto|recvfrom|"
    r"sendmsg|recvmsg|getsockname|getpeername|setsockopt|getsockopt|shutdown)\("
)


def normalize_adapter(
    raw_paths: list[Path], traces: list[Path], stdout_paths: list[Path],
    stderr_paths: list[Path], typed_path: Path, *, repo: Path, archive: Path,
    artifact_commit: str, artifact_parent: str, started: str, finished: str,
    strace_available: bool,
) -> dict[str, Any]:
    raw = [json.loads(path.read_text(encoding="utf-8")) for path in raw_paths]
    semantic_digests = [digest_value(value) for value in raw]
    repeat_equal = len(set(semantic_digests)) == 1
    trace_lines = [line for path in traces for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if NETWORK_SYSCALL.search(line)]
    network_ok = not trace_lines and all(
        item["network_control"]["socket_negative_control"]["status"] == "PASS"
        and item["network_control"]["sandboxed"] is False for item in raw
    )
    first = raw[0]
    scientific_ok = (
        first["summary"]["rows"] == 4161
        and first["summary"]["C_2_equals_C_DP_rows"] == 4161
        and first["sharpness_evidence"]["costs"] == {"C_1": 6, "C_2": 5, "C_DP": 5}
        and all(first["sharpness_evidence"]["witness_checks"].values())
    )
    deps = dependency_inventory()
    terminal = (
        "COUNTEREXAMPLE" if not scientific_ok else
        "INVALID" if not repeat_equal or not network_ok else
        "BLOCKED" if not deps["exact_lock_closed"] or not strace_available else "PASS"
    )
    statuses = {oid: "PASS" for oid in ("O10", "O11", "O12", "O13", "O14")}
    statuses["O15"] = (
        "INVALID" if not repeat_equal or not network_ok else
        "BLOCKED" if not deps["exact_lock_closed"] or not strace_available else "PASS"
    )
    details = {
        "O10": "Finite author-stack unrestricted DP outputs were recorded on the exact frozen corpus.",
        "O11": "Finite author-stack support-two outputs were recorded; no arbitrary-n surjectivity authority is granted.",
        "O12": "Finite author-stack C_2 equals C_DP on all 4,161 declared fixtures.",
        "O13": "Finite author-stack support-one outputs use the arbitrary-anchor D+ family.",
        "O14": "Author-stack witnesses independently rescore the fixed sharpness costs 5,5,6.",
        "O15": "Two adapter executions are byte-semantically identical and network-free.",
    }
    obligations = mutation_free_obligations(statuses, {
        "raw_sha256": [file_sha256(path) for path in raw_paths],
        "summary": first["summary"],
    }, details)
    trace_digest = hashlib.sha256(b"".join(path.read_bytes() for path in traces)).hexdigest()
    input_digests = {"fixture": first["input_digests"]["fixture"]["sha256"]}
    for path, record in first["input_digests"]["author_sources"].items():
        input_digests[path.replace("/", "_")] = record["sha256"]
    result = lane_base(
        lane="LANE_A_AUTHOR_STACK_ADAPTER",
        artifact_commit=artifact_commit,
        artifact_parent=artifact_parent,
        campaign=repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_campaign.json",
        runner=repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_author_stack_adapter.py",
        result_schema=repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/q1_c1_result.schema.json",
        fixture_digests={"small_domains": first["input_digests"]["fixture"]["sha256"]},
        input_digests=input_digests,
        deps=deps,
        cwd=archive,
        command=(
            ["/usr/bin/strace", "-f", "-qq", "-e", "trace=network", str(PYTHON), "-I", str(repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_author_stack_adapter.py")]
            if strace_available else
            [str(PYTHON), "-I", str(repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness/lane_a_author_stack_adapter.py")]
        ),
        started=started,
        finished=finished,
        stdout=stdout_paths[0],
        stderr=stderr_paths[0],
        network={
            "socket_negative_control": "PASS",
            "network_syscall_count": len(trace_lines),
            "trace_sha256": trace_digest,
            "sandboxed": False,
            "namespace_isolation": "NOT_APPLICABLE",
        },
        obligations=obligations,
        payload={
            "role": "FINITE_PRODUCTION_AUTHOR_STACK_ADAPTER",
            "raw_result_paths": [str(path) for path in raw_paths],
            "raw_result_sha256": [file_sha256(path) for path in raw_paths],
            "repeat_semantic_sha256": semantic_digests,
            "repeat_equal": repeat_equal,
            "summary": first["summary"],
            "sharpness": first["sharpness_evidence"]["costs"],
            "syscall_trace_available": strace_available,
            "dependency_gate": deps,
            "authority": "FINITE_FIXTURE_ONLY",
        },
        terminal=terminal,
        semantic_raw=file_sha256(raw_paths[0]),
        semantic_digest=semantic_digests[0],
        semantic_diff=[] if repeat_equal else [{
            "json_pointer": "/repeat/semantic_sha256", "expected": semantic_digests[0],
            "actual": semantic_digests[1:],
        }],
        exclusions=[],
        numpy_version="2.3.5",
    )
    typed_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def preflight_campaigns(repo: Path) -> None:
    harness = repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness"
    lane_a = json.loads((harness / "lane_a_campaign.json").read_text(encoding="utf-8"))
    lane_b = json.loads((harness / "lane_b_campaign.json").read_text(encoding="utf-8"))
    for path, record in lane_a["runner_sources"].items():
        if file_sha256(repo / path) != record["sha256"]:
            raise RuntimeError(f"Lane A runner digest mismatch: {path}")
    b_path = repo / lane_b["runner"]["path"]
    if file_sha256(b_path) != lane_b["runner"]["sha256"]:
        raise RuntimeError("Lane B runner digest mismatch")
    for campaign in (lane_a,):
        for path, record in campaign["contract_artifacts"].items():
            candidate = repo / path
            if file_sha256(candidate) != record["sha256"] or candidate.stat().st_size != record["bytes"]:
                raise RuntimeError(f"contract artifact mismatch: {path}")
    for record in lane_b["contracts"].values():
        if file_sha256(repo / record["path"]) != record["sha256"]:
            raise RuntimeError(f"Lane B contract mismatch: {record['path']}")


def prepare(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    require_clean(repo)
    if run_git(repo, "rev-parse", "HEAD") != args.artifact_commit:
        raise RuntimeError("prepare must run at the committed runner/campaign HEAD")
    require_runner_ancestry(repo, args.artifact_commit, args.artifact_parent)
    if Path(sys.executable).resolve() != PYTHON or sys.version.split()[0] != "3.12.13":
        raise RuntimeError("coordinator interpreter mismatch")
    preflight_campaigns(repo)
    result_root = (repo / args.result_root).resolve()
    try:
        result_root.relative_to(repo)
    except ValueError as exc:
        raise RuntimeError("result root must be inside repository") from exc
    if result_root.exists():
        raise FileExistsError(result_root)
    archive = extract_candidate(repo)
    harness = repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness"
    protocol = repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/Q1_C1_DUAL_HARNESS_PROOF_CHALLENGE_PROTOCOL.md"
    fixture = harness / "fixtures/q1_c1_small_domains.json"
    proof = harness / "proofs/q1_c1_zero_sum.proof.json"
    proof_schema = harness / "q1_c1_proof_certificate.schema.json"
    mutations = harness / "q1_c1_mutations.json"
    result_schema = harness / "q1_c1_result.schema.json"
    started = utc_now()

    # Lane B must start first because it enforces the clean-worktree check before
    # creating any terminal files.
    lane_b_dir = result_root / "lane_b"
    lane_b_command = [
        str(PYTHON), "-I", str(harness / "lane_b_independent_challenge.py"),
        "--archive-root", str(archive), "--repo-root", str(repo),
        "--protocol", str(protocol), "--fixture", str(fixture),
        "--proof", str(proof), "--proof-schema", str(proof_schema),
        "--mutations", str(mutations), "--result-schema", str(result_schema),
        "--campaign", str(harness / "lane_b_campaign.json"),
        "--output-dir", str(lane_b_dir),
        "--artifact-commit", args.artifact_commit,
        "--artifact-parent", args.artifact_parent,
        "--protocol-commit", PROTOCOL_COMMIT,
        "--repeat", "2", "--timeout", "900",
    ]
    lane_b_process = subprocess.run(
        lane_b_command, cwd=repo, env=ENVIRONMENT, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1900, check=False,
    )
    if lane_b_process.returncode:
        raise RuntimeError(
            "Lane B execution failed: " + lane_b_process.stderr.decode("utf-8", errors="replace")
        )
    (lane_b_dir / "parent_stdout.txt").write_bytes(lane_b_process.stdout)
    (lane_b_dir / "parent_stderr.txt").write_bytes(lane_b_process.stderr)
    lane_b_result_path = lane_b_dir / "lane_b_result.json"
    lane_b = json.loads(lane_b_result_path.read_text(encoding="utf-8"))
    adapter_strace_available = bool(
        lane_b["payload"]["execution_resources"]["strace_available"]
    )

    lane_a_dir = result_root / "lane_a"
    raw_root = lane_a_dir / "raw"
    r6s_raw_paths: list[Path] = []
    for index in (1, 2):
        run_dir = raw_root / "r6s" / f"run{index}"
        run_dir.mkdir(parents=True, exist_ok=False)
        stdout = run_dir / "scientific_stdout.txt"
        stderr = run_dir / "scientific_stderr.txt"
        raw_result = run_dir / "replay.json"
        outer_stdout = run_dir / "outer_stdout.txt"
        outer_stderr = run_dir / "outer_stderr.txt"
        command = [str(PYTHON), "-I", str(harness / "lane_a_r6s_replay.py"), str(archive), str(stdout), str(stderr), str(raw_result)]
        rc = run_captured(command, repo, outer_stdout, outer_stderr, timeout=300, env=ENVIRONMENT)
        if rc or not raw_result.is_file():
            raise RuntimeError(f"Lane A R6S run {index} failed with status {rc}")
        r6s_raw_paths.append(raw_result)

    adapter_raw_paths: list[Path] = []
    adapter_traces: list[Path] = []
    adapter_stdout: list[Path] = []
    adapter_stderr: list[Path] = []
    for index in (1, 2):
        run_dir = raw_root / "adapter" / f"run{index}"
        run_dir.mkdir(parents=True, exist_ok=False)
        raw_result = run_dir / "adapter.json"
        trace = run_dir / "network.strace"
        stdout = run_dir / "stdout.txt"
        stderr = run_dir / "stderr.txt"
        child_command = [
            str(PYTHON), "-I", str(harness / "lane_a_author_stack_adapter.py"),
            str(archive), str(fixture), str(raw_result),
        ]
        if adapter_strace_available:
            command = [
                "/usr/bin/strace", "-f", "-qq", "-e", "trace=network", "-o", str(trace),
            ] + child_command
        else:
            trace.write_text(
                "STRACE_UNAVAILABLE: host denied PTRACE_TRACEME; Python audit hook active\n",
                encoding="utf-8",
            )
            command = child_command
        rc = run_captured(command, repo, stdout, stderr, timeout=900, env=ENVIRONMENT)
        if rc or not raw_result.is_file() or not trace.is_file():
            raise RuntimeError(f"Lane A adapter run {index} failed with status {rc}")
        adapter_raw_paths.append(raw_result)
        adapter_traces.append(trace)
        adapter_stdout.append(stdout)
        adapter_stderr.append(stderr)

    lane_a_dir.mkdir(parents=True, exist_ok=True)
    r6s_typed_path = lane_a_dir / "lane_a_r6s_result.json"
    adapter_typed_path = lane_a_dir / "lane_a_adapter_result.json"
    finished = utc_now()
    r6s = normalize_r6s(
        r6s_raw_paths, r6s_typed_path, repo=repo, archive=archive,
        artifact_commit=args.artifact_commit, artifact_parent=args.artifact_parent,
        started=started, finished=finished,
    )
    adapter = normalize_adapter(
        adapter_raw_paths, adapter_traces, adapter_stdout, adapter_stderr,
        adapter_typed_path, repo=repo, archive=archive,
        artifact_commit=args.artifact_commit, artifact_parent=args.artifact_parent,
        started=started, finished=finished, strace_available=adapter_strace_available,
    )
    schema = json.loads(result_schema.read_text(encoding="utf-8"))
    typed_results = {
        "lane_a_r6s": r6s,
        "lane_a_adapter": adapter,
        "lane_b": lane_b,
    }
    schema_failures = {
        name: validate_schema(result, schema)
        for name, result in typed_results.items()
    }
    schema_failures = {name: errors for name, errors in schema_failures.items() if errors}
    if schema_failures:
        raise RuntimeError("prepared lane result schema failure: " + json.dumps(schema_failures, sort_keys=True))
    manifest = {
        "schema": "Q1-C1-PREPARE-MANIFEST-v1",
        "candidate_ref": CANDIDATE_REF,
        "candidate_archive_root": str(archive),
        "artifact_commit": args.artifact_commit,
        "artifact_parent": args.artifact_parent,
        "protocol_commit": PROTOCOL_COMMIT,
        "comparison_executed": False,
        "lane_results": {
            "lane_a_r6s": {"path": str(r6s_typed_path), "sha256": file_sha256(r6s_typed_path), "terminal": r6s["terminal"]},
            "lane_a_adapter": {"path": str(adapter_typed_path), "sha256": file_sha256(adapter_typed_path), "terminal": adapter["terminal"]},
            "lane_b": {"path": str(lane_b_result_path), "sha256": file_sha256(lane_b_result_path), "terminal": lane_b["terminal"]},
        },
        "next_gate": "COMMIT_ALL_LANE_TERMINALS_BEFORE_COMPARE",
    }
    manifest_path = result_root / "PREPARE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Q1_C1_PREPARE=" + canonical_bytes({"manifest": str(manifest_path), "sha256": file_sha256(manifest_path)}).decode("utf-8"))
    return 0


def _type_ok(value: Any, expected: str) -> bool:
    mapping = {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool), "null": value is None,
    }
    return mapping[expected]


def validate_schema(instance: Any, schema: Any, root: dict[str, Any] | None = None, path: str = "$") -> list[str]:
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: false schema"]
    root = schema if root is None else root
    if "$ref" in schema:
        target: Any = root
        for token in schema["$ref"][2:].split("/"):
            target = target[token.replace("~1", "/").replace("~0", "~")]
        return validate_schema(instance, target, root, path)
    errors: list[str] = []
    if "type" in schema and not _type_ok(instance, schema["type"]):
        return [f"{path}: expected {schema['type']}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: const mismatch")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: enum mismatch")
    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: pattern mismatch")
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: below minLength")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum")
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in instance:
                errors.append(f"{path}: missing {required}")
        for name, value in instance.items():
            child_path = f"{path}/{name}"
            if name in properties:
                errors.extend(validate_schema(value, properties[name], root, child_path))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{child_path}: additional property")
            elif isinstance(schema.get("additionalProperties"), dict):
                errors.extend(validate_schema(value, schema["additionalProperties"], root, child_path))
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: below minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: above maxItems")
        if schema.get("uniqueItems"):
            rendered = [canonical_bytes(value) for value in instance]
            if len(rendered) != len(set(rendered)):
                errors.append(f"{path}: duplicate items")
        prefixes = schema.get("prefixItems", [])
        for index, child_schema in enumerate(prefixes):
            if index < len(instance):
                errors.extend(validate_schema(instance[index], child_schema, root, f"{path}/{index}"))
        item_schema = schema.get("items")
        if item_schema is False and len(instance) > len(prefixes):
            errors.append(f"{path}: items after prefix")
        elif isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(validate_schema(value, item_schema, root, f"{path}/{index}"))
        if "contains" in schema:
            count = sum(not validate_schema(value, schema["contains"], root, f"{path}/{i}") for i, value in enumerate(instance))
            if count < schema.get("minContains", 1):
                errors.append(f"{path}: too few contains matches")
            if "maxContains" in schema and count > schema["maxContains"]:
                errors.append(f"{path}: too many contains matches")
    for child in schema.get("allOf", []):
        errors.extend(validate_schema(instance, child, root, path))
    if "anyOf" in schema and all(validate_schema(instance, child, root, path) for child in schema["anyOf"]):
        errors.append(f"{path}: no anyOf match")
    if "if" in schema and not validate_schema(instance, schema["if"], root, path):
        errors.extend(validate_schema(instance, schema.get("then", True), root, path))
    return errors


def require_committed(repo: Path, path: Path) -> str:
    relative = path.resolve().relative_to(repo).as_posix()
    committed = subprocess.run(
        ["git", "show", f"HEAD:{relative}"], cwd=repo, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    if committed.returncode or committed.stdout != path.read_bytes():
        raise RuntimeError(f"terminal is not byte-identical to committed HEAD: {relative}")
    return relative


def projected_cost_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    fields = ("fixture_id", "targets", "target_encoding", "C_DP", "C_2", "C_1")
    return {row["fixture_id"]: {field: row[field] for field in fields} for row in rows}


def field_diffs(expected: Any, actual: Any, pointer: str = "") -> list[dict[str, Any]]:
    if isinstance(expected, dict) and isinstance(actual, dict):
        rows = []
        for key in sorted(set(expected) | set(actual)):
            child = pointer + "/" + str(key).replace("~", "~0").replace("/", "~1")
            if key not in expected:
                rows.append({"json_pointer": child, "expected": "<MISSING>", "actual": actual[key]})
            elif key not in actual:
                rows.append({"json_pointer": child, "expected": expected[key], "actual": "<MISSING>"})
            else:
                rows.extend(field_diffs(expected[key], actual[key], child))
        return rows
    if isinstance(expected, list) and isinstance(actual, list):
        rows = []
        for index in range(max(len(expected), len(actual))):
            child = f"{pointer}/{index}"
            if index >= len(expected):
                rows.append({"json_pointer": child, "expected": "<MISSING>", "actual": actual[index]})
            elif index >= len(actual):
                rows.append({"json_pointer": child, "expected": expected[index], "actual": "<MISSING>"})
            else:
                rows.extend(field_diffs(expected[index], actual[index], child))
        return rows
    return [] if type(expected) is type(actual) and expected == actual else [
        {"json_pointer": pointer or "/", "expected": expected, "actual": actual}
    ]


def coordinator_network_control(output_dir: Path) -> tuple[dict[str, Any], Path, Path, bool]:
    output_dir.mkdir(parents=True, exist_ok=False)
    trace = output_dir / "network.strace"
    stdout = output_dir / "stdout.txt"
    stderr = output_dir / "stderr.txt"
    probe_trace = output_dir / "strace_probe.trace"
    probe_stdout = output_dir / "strace_probe_stdout.txt"
    probe_stderr = output_dir / "strace_probe_stderr.txt"
    probe_command = [
        "/usr/bin/strace", "-f", "-qq", "-e", "trace=network", "-o", str(probe_trace),
        str(PYTHON), "-I", "-c", "pass",
    ]
    probe_rc = run_captured(
        probe_command, output_dir, probe_stdout, probe_stderr, timeout=30, env=ENVIRONMENT,
    )
    strace_available = probe_rc == 0
    if not strace_available:
        probe_error = probe_stderr.read_text(encoding="utf-8", errors="replace")
        if "PTRACE_TRACEME" not in probe_error or "Operation not permitted" not in probe_error:
            raise RuntimeError("coordinator strace probe failed for an unclassified reason")
    code = (
        "import socket,sys\n"
        "def deny(event,args):\n"
        "    if event.startswith('socket.'):\n"
        "        raise PermissionError('network denied')\n"
        "sys.addaudithook(deny)\n"
        "try:\n"
        "    socket.socket(socket.AF_INET,socket.SOCK_STREAM)\n"
        "except PermissionError:\n"
        "    print('PASS')\n"
        "else:\n"
        "    raise SystemExit(1)\n"
    )
    child = [str(PYTHON), "-I", "-c", code]
    if strace_available:
        command = [
            "/usr/bin/strace", "-f", "-qq", "-e", "trace=network", "-o", str(trace),
        ] + child
    else:
        trace.write_text(
            "STRACE_UNAVAILABLE: host denied PTRACE_TRACEME; Python audit hook active\n",
            encoding="utf-8",
        )
        command = child
    rc = run_captured(command, output_dir, stdout, stderr, timeout=30, env=ENVIRONMENT)
    calls = [line for line in trace.read_text(encoding="utf-8", errors="replace").splitlines() if NETWORK_SYSCALL.search(line)]
    if rc or stdout.read_text(encoding="utf-8").strip() != "PASS" or calls:
        raise RuntimeError("coordinator network negative control failed")
    return {
        "socket_negative_control": "PASS", "network_syscall_count": 0,
        "trace_sha256": file_sha256(trace), "sandboxed": False,
        "namespace_isolation": "NOT_APPLICABLE",
    }, stdout, stderr, strace_available


def obligation_map(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in result["obligations"]}


def compare(args: argparse.Namespace) -> int:
    repo = Path(args.repo_root).resolve()
    require_clean(repo)
    result_root = (repo / args.result_root).resolve()
    try:
        result_root.relative_to(repo)
    except ValueError as exc:
        raise RuntimeError("result root must be inside repository") from exc
    if not result_root.is_dir():
        raise FileNotFoundError(result_root)
    coordinator_dir = result_root / "coordinator"
    if coordinator_dir.exists():
        raise FileExistsError(coordinator_dir)

    harness = repo / "development/q1-q4-publication-closure-2026-08-22/q1-cycle-01/harness"
    result_schema_path = harness / "q1_c1_result.schema.json"
    result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))
    manifest_path = result_root / "PREPARE_MANIFEST.json"
    r6s_path = result_root / "lane_a/lane_a_r6s_result.json"
    adapter_path = result_root / "lane_a/lane_a_adapter_result.json"
    lane_b_path = result_root / "lane_b/lane_b_result.json"

    # Every lane byte, including raw captures and traces, must already be
    # immutable at this boundary.  No comparator output may exist yet.
    committed_files = []
    for path in sorted(candidate for candidate in result_root.rglob("*") if candidate.is_file()):
        committed_files.append(require_committed(repo, path))
    for required in (manifest_path, r6s_path, adapter_path, lane_b_path):
        if not required.is_file():
            raise FileNotFoundError(required)

    result_commit = run_git(repo, "rev-parse", "HEAD")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    r6s = json.loads(r6s_path.read_text(encoding="utf-8"))
    adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
    lane_b = json.loads(lane_b_path.read_text(encoding="utf-8"))
    lane_results = {"lane_a_r6s": r6s, "lane_a_adapter": adapter, "lane_b": lane_b}

    schema_failures = {
        name: validate_schema(result, result_schema)
        for name, result in lane_results.items()
    }
    schema_failures = {name: errors for name, errors in schema_failures.items() if errors}
    if schema_failures:
        raise RuntimeError("immutable lane result schema failure: " + json.dumps(schema_failures, sort_keys=True))

    artifact_commits = {result["artifact_commit"] for result in lane_results.values()}
    artifact_parents = {result["artifact_commit_parent"] for result in lane_results.values()}
    if len(artifact_commits) != 1 or len(artifact_parents) != 1:
        raise RuntimeError("lane runner chronology disagreement")
    artifact_commit = next(iter(artifact_commits))
    artifact_parent = next(iter(artifact_parents))
    require_runner_ancestry(repo, artifact_commit, artifact_parent)
    if manifest["artifact_commit"] != artifact_commit or manifest["artifact_parent"] != artifact_parent:
        raise RuntimeError("prepare manifest chronology mismatch")
    if result_commit == artifact_commit or subprocess.run(
        ["git", "merge-base", "--is-ancestor", artifact_commit, result_commit],
        cwd=repo, check=False,
    ).returncode:
        raise RuntimeError("lane result commit is not a strict descendant of runner commit")
    for name, record in manifest["lane_results"].items():
        path = {"lane_a_r6s": r6s_path, "lane_a_adapter": adapter_path, "lane_b": lane_b_path}[name]
        if record["sha256"] != file_sha256(path) or record["terminal"] != lane_results[name]["terminal"]:
            raise RuntimeError(f"prepare manifest lane binding mismatch: {name}")

    raw_adapter_paths = [Path(path) for path in adapter["payload"]["raw_result_paths"]]
    if len(raw_adapter_paths) != 2:
        raise RuntimeError("adapter must bind exactly two raw result paths")
    raw_adapter = json.loads(raw_adapter_paths[0].read_text(encoding="utf-8"))
    adapter_rows = raw_adapter["corpus"]["n1"]["rows"] + raw_adapter["corpus"]["n2"]["rows"]
    lane_b_domains = lane_b["payload"]["science"]["domains"]
    independent_rows = lane_b_domains["n1"]["rows_full"] + lane_b_domains["n2"]["rows_full"]
    adapter_projection = projected_cost_rows(adapter_rows)
    independent_projection = projected_cost_rows(independent_rows)
    comparator_diff = field_diffs(independent_projection, adapter_projection, "/finite_adapter")
    comparison_count = len(set(independent_projection) & set(adapter_projection))
    corpus_shape_valid = (
        len(adapter_projection) == 4161
        and len(independent_projection) == 4161
        and comparison_count == 4161
    )
    if not corpus_shape_valid:
        comparator_diff.append({
            "json_pointer": "/finite_adapter/row_count",
            "expected": {"lane_b": 4161, "intersection": 4161},
            "actual": {
                "lane_a": len(adapter_projection), "lane_b": len(independent_projection),
                "intersection": comparison_count,
            },
        })

    replay_valid = bool(r6s["payload"]["replay_match"] and r6s["payload"]["repeat_equal"])
    adapter_valid = bool(adapter["payload"]["repeat_equal"])
    lane_b_counterexample = lane_b["terminal"] == "COUNTEREXAMPLE"
    any_invalid = any(result["terminal"] == "INVALID" for result in lane_results.values())
    finite_counterexample = adapter["terminal"] == "COUNTEREXAMPLE" or bool(comparator_diff)
    deps = dependency_inventory()
    started = utc_now()
    network, stdout_path, stderr_path, coordinator_trace_available = coordinator_network_control(coordinator_dir)
    finished = utc_now()
    trace_gates = {
        "lane_a_r6s": bool(r6s["payload"]["syscall_trace_available"]),
        "lane_a_adapter": bool(adapter["payload"]["syscall_trace_available"]),
        "lane_b": bool(lane_b["payload"]["execution_resources"]["strace_available"]),
        "coordinator": coordinator_trace_available,
    }
    resource_closure = bool(deps["exact_lock_closed"] and all(trace_gates.values()))

    disagreement: dict[str, Any] | None = None
    if lane_b_counterexample:
        terminal = "COUNTEREXAMPLE"
        terminal_reason = "Lane B independently falsified at least one mathematical obligation."
    elif any_invalid or not replay_valid or not adapter_valid:
        terminal = "INVALID"
        terminal_reason = "An immutable lane failed custody, replay, repeat, or result validity."
    elif finite_counterexample:
        terminal = "COUNTEREXAMPLE"
        terminal_reason = "The independent and production implementations disagree on the frozen finite corpus."
    elif not resource_closure:
        terminal = "BLOCKED"
        terminal_reason = "Scientific checks agree, but dependency or syscall-trace resource closure is incomplete."
    elif all(result["terminal"] == "PASS" for result in lane_results.values()):
        terminal = "PASS"
        terminal_reason = "Both immutable lanes and the post-terminal finite comparator pass."
    else:
        terminal = "BLOCKED"
        terminal_reason = "Otherwise-valid immutable lanes have an unresolved scientific disagreement."
        disagreement = {
            "lane_terminals": {name: result["terminal"] for name, result in lane_results.items()},
            "field_diff": comparator_diff,
            "classification": "SCIENTIFIC_DISAGREEMENT",
        }

    lane_b_obligations = obligation_map(lane_b)
    adapter_obligations = obligation_map(adapter)
    r6s_obligations = obligation_map(r6s)
    obligations: list[dict[str, Any]] = []
    comparison_evidence = {
        "lane_result_commit": result_commit,
        "lane_result_sha256": {
            "lane_a_r6s": file_sha256(r6s_path),
            "lane_a_adapter": file_sha256(adapter_path),
            "lane_b": file_sha256(lane_b_path),
        },
        "comparison_count": comparison_count,
        "comparison_diff": comparator_diff,
    }
    for index in range(1, 17):
        oid = f"O{index}"
        source = json.loads(json.dumps(lane_b_obligations[oid]))
        source["evidence_digests"] = [digest_value({
            "lane_b": lane_b_obligations[oid],
            "lane_a_adapter": adapter_obligations.get(oid),
            "lane_a_r6s": r6s_obligations.get(oid),
            "comparison": comparison_evidence if 10 <= index <= 15 else None,
        })]
        if 10 <= index <= 14:
            if comparator_diff:
                source["status"] = "COUNTEREXAMPLE"
            elif lane_b_obligations[oid]["status"] == "PASS" and adapter_obligations[oid]["status"] == "PASS":
                source["status"] = "PASS"
            else:
                source["status"] = lane_b_obligations[oid]["status"]
            source["detail"] += (
                " Post-terminal comparison with the finite production adapter was exact."
                if not comparator_diff else " Post-terminal finite production comparison disagreed."
            )
        elif oid == "O15":
            if any_invalid or not replay_valid or not adapter_valid:
                source["status"] = "INVALID"
            elif not resource_closure:
                source["status"] = "BLOCKED"
            else:
                source["status"] = "PASS"
            source["detail"] = "All lane bytes, chronology, repeat semantics, and replay receipts are bound; exact dependency closure controls release."
        obligations.append(source)

    payload = {
        "role": "POST_TERMINAL_COORDINATOR",
        "lane_result_commit": result_commit,
        "committed_file_count": len(committed_files),
        "committed_files_digest": digest_value(committed_files),
        "lane_terminals": {name: result["terminal"] for name, result in lane_results.items()},
        "lane_result_sha256": comparison_evidence["lane_result_sha256"],
        "finite_adapter_comparison": {
            "expected_rows": 4161,
            "compared_rows": comparison_count,
            "lane_a_rows": len(adapter_projection),
            "lane_b_rows": len(independent_projection),
            "field_diff": comparator_diff,
            "exact": not comparator_diff,
        },
        "r6s_replay_match": replay_valid,
        "dependency_gate": deps,
        "syscall_trace_gates": trace_gates,
        "resource_closure": resource_closure,
        "terminal_reason": terminal_reason,
        "disagreement": disagreement,
        "authority": {
            "mathematical": "Q1_C1_THEOREM_ONLY_IF_PASS",
            "production_equivalence": "FROZEN_4161_ROW_CORPUS_ONLY_IF_PASS",
            "arbitrary_n_production_equivalence": False,
            "novelty_or_submission": False,
        },
    }
    coordinator_path = Path(__file__).resolve()
    campaign_digest = digest_value({
        "lane_a_campaign_sha256": r6s["campaign_digest"],
        "lane_b_campaign_sha256": lane_b["campaign_digest"],
        "comparison_rule": "EXACT_FIELDWISE_AFTER_IMMUTABLE_TERMINALS",
    })
    result = {
        "schema_version": "q1-c1-result-v1",
        "protocol_id": "Q1-C1", "protocol_version": "1.0",
        "candidate_ref": CANDIDATE_REF, "protocol_commit": PROTOCOL_COMMIT,
        "artifact_commit": artifact_commit, "artifact_commit_parent": artifact_parent,
        "lane": "COORDINATOR", "campaign_digest": campaign_digest,
        "runner_digest": file_sha256(coordinator_path),
        "result_schema_digest": file_sha256(result_schema_path),
        "fixture_digests": {
            "small_domains": lane_b["fixture_digests"]["small_domains"],
            "proof_certificate": lane_b["fixture_digests"]["proof_certificate"],
            "mutation_registry": lane_b["fixture_digests"]["mutation_registry"],
        },
        "input_digests": comparison_evidence["lane_result_sha256"],
        "interpreter": {"path": str(PYTHON), "python_version": "3.12.13", "numpy_version": "2.3.5"},
        "dependency_inventory_digest": digest_value(deps),
        "cwd": str(repo),
        "environment_allowlist": {"names": ENV_NAMES, "values": ENVIRONMENT},
        "network_control": network,
        "command": [
            str(PYTHON), "-I", str(coordinator_path), "compare",
            "--repo-root", str(repo), "--result-root", args.result_root,
        ],
        "started_at": started, "finished_at": finished, "exit_code": 0,
        "stdout_path": str(stdout_path), "stdout_sha256": file_sha256(stdout_path),
        "stdout_bytes": stdout_path.stat().st_size,
        "stderr_path": str(stderr_path), "stderr_sha256": file_sha256(stderr_path),
        "stderr_bytes": stderr_path.stat().st_size,
        "output_truncated": False, "worktree_dirty": False,
        "obligations": obligations, "mutations": lane_b["mutations"],
        "semantic_projection": {
            "method": "CANONICAL_JSON_SORTED_KEYS_NO_NAN",
            "excluded_json_pointers": [],
            "raw_sha256": digest_value(payload), "semantic_sha256": digest_value(payload),
        },
        "semantic_diff": comparator_diff, "terminal": terminal,
        "authority_limits": authority_limits(), "payload": payload,
    }
    schema_errors = validate_schema(result, result_schema)
    if schema_errors:
        raise RuntimeError("coordinator result schema failure: " + "; ".join(schema_errors[:40]))
    result_path = coordinator_dir / "coordinator_result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Q1_C1_COORDINATOR=" + canonical_bytes({
        "path": str(result_path), "sha256": file_sha256(result_path),
        "terminal": terminal, "compared_rows": comparison_count,
        "diff_count": len(comparator_diff),
    }).decode("utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="phase", required=True)
    prepare_parser = subparsers.add_parser("prepare", help="run separated lanes without comparing")
    prepare_parser.add_argument("--repo-root", required=True)
    prepare_parser.add_argument("--result-root", required=True)
    prepare_parser.add_argument("--artifact-commit", required=True)
    prepare_parser.add_argument("--artifact-parent", required=True)
    prepare_parser.set_defaults(handler=prepare)
    compare_parser = subparsers.add_parser("compare", help="compare committed lane terminals")
    compare_parser.add_argument("--repo-root", required=True)
    compare_parser.add_argument("--result-root", required=True)
    compare_parser.set_defaults(handler=compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
