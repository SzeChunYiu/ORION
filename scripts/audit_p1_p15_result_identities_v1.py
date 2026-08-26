#!/usr/bin/env python3
"""Fail-closed Git-object and byte-binding audit for the 25 P1-P15 result rows.

This checker deliberately does not rerun science or grant publication authority. It
answers only whether the writing ledger points to real commits whose exact result
subtrees, result-binding packets, terminals, and declared artifact bytes are
preserved on a frozen repository subject.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_COMMON = 10
EXPECTED_PAPERS = 15
EXPECTED_TOTAL = EXPECTED_COMMON + EXPECTED_PAPERS
RESULT_ROOT = PurePosixPath("research/orion-epistemic-state-v1/results")
DEFAULT_LEDGER = PurePosixPath("papers/P1_P15_RESULT_BOUND_CLAIM_LEDGER_V1.json")
PACKET_NAME = "RESULT_BINDING_PACKET_V1.json"
SUCCESS = "P1_P15_25_RESULT_IDENTITIES_AND_BYTES_BOUND_NO_RERUN_AUTHORITY"


class AuditError(RuntimeError):
    """Raised for malformed audit inputs or unavailable Git evidence."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def duplicate_safe_pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        need(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=duplicate_safe_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"{label}: invalid UTF-8 JSON: {exc}") from exc
    need(isinstance(value, dict), f"{label}: top-level object required")
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> dict[str, Any]:
    raw = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return {
        "path": path.name,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def run_git(
    root: Path,
    *args: str,
    check: bool = True,
    text: bool = False,
) -> subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=text,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr if text else completed.stderr.decode("utf-8", "replace")
        raise AuditError(f"git {' '.join(args)} failed ({completed.returncode}): {stderr.strip()}")
    return completed


def git_text(root: Path, *args: str) -> str:
    completed = run_git(root, *args, text=True)
    assert isinstance(completed.stdout, str)
    return completed.stdout.strip()


def git_bytes(root: Path, ref: str, path: PurePosixPath) -> bytes:
    completed = run_git(root, "show", f"{ref}:{path.as_posix()}")
    assert isinstance(completed.stdout, bytes)
    return completed.stdout


def exact_commit_exists(root: Path, sha: str) -> bool:
    completed = run_git(root, "cat-file", "-e", f"{sha}^{{commit}}", check=False)
    return completed.returncode == 0


def path_oid(root: Path, ref: str, path: PurePosixPath) -> str | None:
    completed = run_git(root, "rev-parse", f"{ref}:{path.as_posix()}", check=False, text=True)
    if completed.returncode != 0:
        return None
    assert isinstance(completed.stdout, str)
    value = completed.stdout.strip()
    return value if SHA40.fullmatch(value) else None


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    completed = run_git(
        root,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        stderr = completed.stderr.decode("utf-8", "replace")
        raise AuditError(
            f"git merge-base --is-ancestor {ancestor} {descendant} failed: {stderr.strip()}"
        )
    return completed.returncode == 0


def changed_paths(root: Path, commit: str) -> list[str]:
    output = git_text(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "-r",
        commit,
    )
    return sorted({line for line in output.splitlines() if line})


def measure_blob(root: Path, oid: str) -> dict[str, Any]:
    need(SHA40.fullmatch(oid) is not None, f"invalid blob oid: {oid}")
    object_type = git_text(root, "cat-file", "-t", oid)
    need(object_type == "blob", f"{oid}: expected blob, found {object_type}")
    declared_size = int(git_text(root, "cat-file", "-s", oid))
    process = subprocess.Popen(
        ["git", "cat-file", "blob", oid],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    digest = hashlib.sha256()
    observed_size = 0
    while True:
        chunk = process.stdout.read(1024 * 1024)
        if not chunk:
            break
        observed_size += len(chunk)
        digest.update(chunk)
    stderr = b"" if process.stderr is None else process.stderr.read()
    returncode = process.wait()
    need(
        returncode == 0,
        f"git cat-file blob {oid} failed ({returncode}): {stderr.decode('utf-8', 'replace').strip()}",
    )
    need(
        observed_size == declared_size,
        f"blob {oid}: declared size {declared_size}, observed {observed_size}",
    )
    return {
        "oid": oid,
        "bytes": observed_size,
        "sha256": digest.hexdigest(),
    }


def safe_result_dir(job_id: str) -> PurePosixPath:
    need(isinstance(job_id, str) and job_id, "job_id missing")
    need(
        re.fullmatch(r"(?:DES|P(?:[1-9]|1[0-5]))-[A-Z0-9-]+", job_id) is not None,
        f"unsafe or unexpected job_id: {job_id!r}",
    )
    return RESULT_ROOT / job_id


def flatten_ledger(ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    common = ledger.get("common_results")
    papers = ledger.get("papers")
    need(isinstance(common, list), "ledger.common_results must be a list")
    need(isinstance(papers, list), "ledger.papers must be a list")
    need(len(common) == EXPECTED_COMMON, f"expected {EXPECTED_COMMON} common rows")
    need(len(papers) == EXPECTED_PAPERS, f"expected {EXPECTED_PAPERS} paper rows")
    rows: list[dict[str, Any]] = []
    for index, source in enumerate(common):
        need(isinstance(source, dict), f"common row {index} must be an object")
        row = dict(source)
        row["ledger_section"] = "common_results"
        row["paper"] = None
        rows.append(row)
    for index, source in enumerate(papers):
        need(isinstance(source, dict), f"paper row {index} must be an object")
        row = dict(source)
        row["ledger_section"] = "papers"
        rows.append(row)
    need(len(rows) == EXPECTED_TOTAL, f"expected {EXPECTED_TOTAL} total rows")
    return rows


def validate_ledger_shape(ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    need(
        ledger.get("schema") == "orion.p1-p15.result-bound-writing-ledger.v1",
        "unexpected writing-ledger schema",
    )
    need(
        ledger.get("computation_session_paper_authority_delta") == "NONE",
        "computation session must not carry paper authority",
    )
    for field in (
        "frozen_subject",
        "authoritative_integration_merge",
        "code_only_conformance_merge",
    ):
        value = ledger.get(field)
        need(isinstance(value, str) and SHA40.fullmatch(value), f"ledger.{field} invalid")
    rows = flatten_ledger(ledger)
    job_ids: list[str] = []
    shas: list[str] = []
    papers: list[str] = []
    for row in rows:
        job_id = row.get("job_id")
        sha = row.get("sha")
        terminal = row.get("terminal")
        need(isinstance(job_id, str), "row.job_id missing")
        safe_result_dir(job_id)
        need(isinstance(sha, str) and SHA40.fullmatch(sha), f"{job_id}: invalid SHA")
        need(isinstance(terminal, str) and terminal, f"{job_id}: terminal missing")
        job_ids.append(job_id)
        shas.append(sha)
        if row["ledger_section"] == "papers":
            paper = row.get("paper")
            need(
                isinstance(paper, str) and re.fullmatch(r"P(?:[1-9]|1[0-5])", paper),
                f"{job_id}: invalid paper identity",
            )
            papers.append(paper)
    need(len(job_ids) == len(set(job_ids)), "duplicate job_id in writing ledger")
    need(len(shas) == len(set(shas)), "duplicate result SHA in writing ledger")
    need(len(papers) == len(set(papers)) == EXPECTED_PAPERS, "paper denominator mismatch")
    need(
        set(papers) == {f"P{number}" for number in range(1, 16)},
        "paper set must be exactly P1-P15",
    )
    return rows


def protected_writing_paths(paths: Iterable[str]) -> list[str]:
    violations: list[str] = []
    for path in paths:
        lowered = path.lower()
        if path.startswith("papers/") or any(
            marker in lowered
            for marker in (
                "active_claim_authority",
                "claim_ledger",
                "/manuscript/",
                "journal_package",
            )
        ):
            violations.append(path)
    return sorted(set(violations))


def classify_row(row: Mapping[str, Any]) -> str:
    if not row.get("commit_object_exists"):
        return "IDENTITY_OBJECT_MISSING"
    if not row.get("ancestor_of_integration") or not row.get("ancestor_of_subject"):
        return "IDENTITY_ANCESTRY_MISMATCH"
    if row.get("result_subtree_oid_commit") is None:
        return "RESULT_SUBTREE_MISSING_AT_LEDGER_COMMIT"
    if not row.get("result_subtree_stable"):
        return "RESULT_SUBTREE_DRIFT"
    if not row.get("result_commit_touches_expected_subtree"):
        return "INTENDED_COMMIT_RESULT_RELATIONSHIP_MISSING"
    if row.get("protected_writing_path_violations"):
        return "WRITING_BOUNDARY_VIOLATION"
    if not row.get("packet_blob_stable"):
        return "RESULT_BINDING_PACKET_DRIFT"
    if not row.get("packet_job_id_matches"):
        return "RESULT_BINDING_PACKET_JOB_MISMATCH"
    if not row.get("packet_terminal_matches"):
        return "RESULT_BINDING_PACKET_TERMINAL_MISMATCH"
    if not row.get("packet_authority_boundary_valid"):
        return "RESULT_BINDING_PACKET_AUTHORITY_MISMATCH"
    if row.get("binding_errors"):
        return "RESULT_ARTIFACT_BINDING_MISMATCH"
    return "IDENTITY_BOUND_BYTES_VERIFIED_NO_RERUN_AUTHORITY"


def audit_row(
    root: Path,
    ledger_row: Mapping[str, Any],
    *,
    integration_ref: str,
    subject_ref: str,
) -> dict[str, Any]:
    job_id = str(ledger_row["job_id"])
    commit = str(ledger_row["sha"])
    terminal = str(ledger_row["terminal"])
    result_dir = safe_result_dir(job_id)
    packet_path = result_dir / PACKET_NAME
    result: dict[str, Any] = {
        "job_id": job_id,
        "paper": ledger_row.get("paper"),
        "ledger_section": ledger_row["ledger_section"],
        "ledger_commit": commit,
        "ledger_terminal": terminal,
        "result_directory": result_dir.as_posix(),
        "packet_path": packet_path.as_posix(),
        "rerun_performed": False,
        "paper_authority_delta": "NONE",
    }
    exists = exact_commit_exists(root, commit)
    result["commit_object_exists"] = exists
    if not exists:
        result.update(
            {
                "ancestor_of_integration": False,
                "ancestor_of_subject": False,
                "binding_errors": ["commit object missing"],
            }
        )
        result["disposition"] = classify_row(result)
        return result

    result["commit_subject"] = git_text(root, "show", "-s", "--format=%s", commit)
    result["commit_tree"] = git_text(root, "rev-parse", f"{commit}^{{tree}}")
    parents_text = git_text(root, "show", "-s", "--format=%P", commit)
    result["commit_parents"] = [] if not parents_text else parents_text.split()
    result["ancestor_of_integration"] = is_ancestor(root, commit, integration_ref)
    result["ancestor_of_subject"] = is_ancestor(root, commit, subject_ref)

    paths = changed_paths(root, commit)
    prefix = result_dir.as_posix() + "/"
    result["changed_path_count"] = len(paths)
    result["changed_paths"] = paths
    result["outside_result_subtree_paths"] = [path for path in paths if not path.startswith(prefix)]
    result["result_commit_touches_expected_subtree"] = any(
        path.startswith(prefix) for path in paths
    )
    result["protected_writing_path_violations"] = protected_writing_paths(paths)

    commit_tree_oid = path_oid(root, commit, result_dir)
    integration_tree_oid = path_oid(root, integration_ref, result_dir)
    subject_tree_oid = path_oid(root, subject_ref, result_dir)
    result["result_subtree_oid_commit"] = commit_tree_oid
    result["result_subtree_oid_integration"] = integration_tree_oid
    result["result_subtree_oid_subject"] = subject_tree_oid
    result["result_subtree_stable"] = (
        commit_tree_oid is not None
        and commit_tree_oid == integration_tree_oid == subject_tree_oid
    )

    packet_commit_oid = path_oid(root, commit, packet_path)
    packet_subject_oid = path_oid(root, subject_ref, packet_path)
    result["packet_blob_oid_commit"] = packet_commit_oid
    result["packet_blob_oid_subject"] = packet_subject_oid
    result["packet_blob_stable"] = (
        packet_commit_oid is not None and packet_commit_oid == packet_subject_oid
    )
    binding_errors: list[str] = []
    if packet_commit_oid is None or packet_subject_oid is None:
        binding_errors.append("result-binding packet missing")
        result["packet_job_id_matches"] = False
        result["packet_terminal_matches"] = False
        result["packet_authority_boundary_valid"] = False
        result["binding_errors"] = binding_errors
        result["disposition"] = classify_row(result)
        return result

    packet_raw_subject = git_bytes(root, subject_ref, packet_path)
    packet = load_json_bytes(packet_raw_subject, f"{job_id} result-binding packet")
    packet_raw_commit = git_bytes(root, commit, packet_path)
    if packet_raw_commit != packet_raw_subject:
        binding_errors.append("result-binding packet bytes differ between ledger commit and subject")
    result["packet_sha256"] = hashlib.sha256(packet_raw_subject).hexdigest()
    result["packet_bytes"] = len(packet_raw_subject)
    result["packet_schema"] = packet.get("schema")
    result["packet_job_id"] = packet.get("job_id")
    result["packet_exact_terminal"] = packet.get("exact_terminal")
    result["packet_claim_ceiling"] = packet.get("claim_ceiling")
    result["packet_job_id_matches"] = packet.get("job_id") == job_id
    result["packet_terminal_matches"] = packet.get("exact_terminal") == terminal
    result["packet_authority_boundary_valid"] = (
        packet.get("computation_session_paper_authority_delta") == "NONE"
        and packet.get("manuscript_writing_owner") == "P1_P15_REWRITE_LANE"
    )

    bindings = packet.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        binding_errors.append("nonempty bindings list missing")
        bindings = []
    seen_paths: set[str] = set()
    measurements: dict[str, dict[str, Any]] = {}
    verified = 0
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            binding_errors.append(f"binding {index}: object required")
            continue
        path_value = binding.get("path")
        expected_bytes = binding.get("bytes")
        expected_sha256 = binding.get("sha256")
        if not isinstance(path_value, str):
            binding_errors.append(f"binding {index}: path missing")
            continue
        path = PurePosixPath(path_value)
        if path.is_absolute() or ".." in path.parts or "\\" in path_value:
            binding_errors.append(f"binding {index}: unsafe path {path_value!r}")
            continue
        if path_value in seen_paths:
            binding_errors.append(f"binding {index}: duplicate path {path_value}")
            continue
        seen_paths.add(path_value)
        if type(expected_bytes) is not int or expected_bytes < 0:
            binding_errors.append(f"binding {path_value}: byte count invalid")
            continue
        if not isinstance(expected_sha256, str) or not SHA256.fullmatch(expected_sha256):
            binding_errors.append(f"binding {path_value}: SHA-256 invalid")
            continue
        oid_subject = path_oid(root, subject_ref, path)
        oid_commit = path_oid(root, commit, path)
        if oid_subject is None:
            binding_errors.append(f"binding {path_value}: missing on subject")
            continue
        if oid_commit is None:
            binding_errors.append(f"binding {path_value}: missing at ledger commit")
            continue
        if oid_subject != oid_commit:
            binding_errors.append(
                f"binding {path_value}: blob drift {oid_commit} -> {oid_subject}"
            )
            continue
        if oid_subject not in measurements:
            measurements[oid_subject] = measure_blob(root, oid_subject)
        observed = measurements[oid_subject]
        if observed["bytes"] != expected_bytes:
            binding_errors.append(
                f"binding {path_value}: bytes expected {expected_bytes}, observed {observed['bytes']}"
            )
            continue
        if observed["sha256"] != expected_sha256:
            binding_errors.append(
                f"binding {path_value}: SHA-256 expected {expected_sha256}, observed {observed['sha256']}"
            )
            continue
        verified += 1

    result["binding_count"] = len(bindings)
    result["binding_verified_count"] = verified
    result["binding_unique_blob_count"] = len(measurements)
    result["binding_errors"] = binding_errors
    result["disposition"] = classify_row(result)
    return result


def audit(
    root: Path,
    *,
    subject_ref: str,
    ledger_path: PurePosixPath,
    output_dir: Path,
) -> dict[str, Any]:
    root = root.resolve()
    need((root / ".git").exists(), f"not a Git checkout: {root}")
    need(SHA40.fullmatch(subject_ref) is not None, "subject_ref must be an exact SHA")
    need(exact_commit_exists(root, subject_ref), f"subject commit missing: {subject_ref}")
    ledger_raw = git_bytes(root, subject_ref, ledger_path)
    ledger = load_json_bytes(ledger_raw, ledger_path.as_posix())
    rows = validate_ledger_shape(ledger)
    integration_ref = str(ledger["authoritative_integration_merge"])
    need(exact_commit_exists(root, integration_ref), f"integration commit missing: {integration_ref}")
    need(
        is_ancestor(root, integration_ref, subject_ref),
        "authoritative integration merge is not an ancestor of the frozen subject",
    )
    frozen_subject = str(ledger["frozen_subject"])
    need(exact_commit_exists(root, frozen_subject), f"frozen computation subject missing: {frozen_subject}")

    audited_rows = [
        audit_row(
            root,
            row,
            integration_ref=integration_ref,
            subject_ref=subject_ref,
        )
        for row in rows
    ]
    success_count = sum(
        row["disposition"] == "IDENTITY_BOUND_BYTES_VERIFIED_NO_RERUN_AUTHORITY"
        for row in audited_rows
    )
    disposition_counts: dict[str, int] = {}
    for row in audited_rows:
        disposition = str(row["disposition"])
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
    status = "PASS" if success_count == EXPECTED_TOTAL else "FAIL"

    ledger_output = {
        "schema": "ORION.V1.P1P15ResultIdentityLedger.v1",
        "subject_commit": subject_ref,
        "subject_tree": git_text(root, "rev-parse", f"{subject_ref}^{{tree}}"),
        "frozen_computation_subject": frozen_subject,
        "authoritative_integration_merge": integration_ref,
        "source_ledger_path": ledger_path.as_posix(),
        "source_ledger_sha256": hashlib.sha256(ledger_raw).hexdigest(),
        "source_ledger_bytes": len(ledger_raw),
        "rows": audited_rows,
        "paper_authority_delta": "NONE",
        "rerun_authority": "NONE",
    }
    summary = {
        "schema": "ORION.V1.P1P15ResultIdentityAuditSummary.v1",
        "status": status,
        "terminal": SUCCESS if status == "PASS" else "P1_P15_RESULT_IDENTITY_AUDIT_RED",
        "subject_commit": subject_ref,
        "subject_tree": ledger_output["subject_tree"],
        "expected_rows": EXPECTED_TOTAL,
        "audited_rows": len(audited_rows),
        "identity_bound_rows": success_count,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "scientific_rerun_performed": False,
        "paper_authority_delta": "NONE",
        "external_validation": "CANNOT_CHECK",
        "top_tier_readiness": "NOT_GRANTED",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_record = write_json(output_dir / "RESULT_IDENTITY_LEDGER.json", ledger_output)
    summary_record = write_json(output_dir / "SUMMARY.json", summary)
    raw_manifest = {
        "schema": "ORION.V1.P1P15ResultIdentityRawManifest.v1",
        "inputs": [
            {
                "path": ledger_path.as_posix(),
                "ref": subject_ref,
                "bytes": len(ledger_raw),
                "sha256": hashlib.sha256(ledger_raw).hexdigest(),
            }
        ],
        "outputs": [ledger_record, summary_record],
    }
    manifest_record = write_json(output_dir / "RAW_MANIFEST.json", raw_manifest)
    binding_packet = {
        "schema": "ORION.V1.P1P15ResultIdentityBindingPacket.v1",
        "subject_commit": subject_ref,
        "subject_tree": ledger_output["subject_tree"],
        "terminal": summary["terminal"],
        "status": status,
        "bindings": [ledger_record, summary_record, manifest_record],
        "scientific_rerun_performed": False,
        "external_validation": "CANNOT_CHECK",
        "paper_authority_delta": "NONE",
        "non_implications": [
            "P1-P15 scientific rerun complete",
            "P1-P15 publication ready",
            "P1-P15 top-tier ready",
            "external novelty supported",
            "independent reproduction complete",
            "ORION V1 frozen",
        ],
    }
    write_json(output_dir / "RESULT_BINDING_PACKET.json", binding_packet)
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--subject-ref", required=True)
    parser.add_argument("--ledger-path", default=DEFAULT_LEDGER.as_posix())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        summary = audit(
            args.root,
            subject_ref=args.subject_ref,
            ledger_path=PurePosixPath(args.ledger_path),
            output_dir=args.output_dir,
        )
    except AuditError as exc:
        print(f"P1_P15_RESULT_IDENTITY_AUDIT_INVALID: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            f"{summary['terminal']} rows={summary['identity_bound_rows']}/{summary['expected_rows']}"
        )
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
