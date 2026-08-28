#!/usr/bin/env python3
"""Fail-closed ORION-11 negative-revival and reproducibility audit.

This checker grants no freeze, merge, submission, novelty, or external-authority
status.  It preserves the broad H1 negative, checks the bounded v2.2.4
mechanical receipts, enumerates every adapter map, and retains the RSE donor
subtraction.
"""

from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable


class AuditError(RuntimeError):
    """Raised whenever an audit precondition or bound artifact fails closed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"JSON load failed: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"JSON root is not an object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def verify_manifest(manifest_path: Path, *, allow_missing: bool = False) -> dict[str, Any]:
    """Verify a two-space SHA256SUMS manifest without path traversal."""

    require(manifest_path.is_file(), f"manifest missing: {manifest_path}")
    base = manifest_path.parent.resolve()
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for number, line in enumerate(manifest_path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        require(len(parts) == 2, f"manifest malformed line {number}: {manifest_path}")
        digest, relative = parts
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), f"manifest invalid digest line {number}: {manifest_path}")
        require(relative not in seen, f"manifest duplicate path: {relative}")
        seen.add(relative)
        candidate = (base / relative).resolve()
        require(candidate == base or base in candidate.parents, f"manifest path traversal: {relative}")
        if not candidate.is_file():
            if allow_missing:
                rows.append((relative, "MISSING_ALLOWED"))
                continue
            raise AuditError(f"manifest missing file: {relative}")
        actual = sha256_file(candidate)
        require(actual == digest, f"manifest digest mismatch: {relative}")
        rows.append((relative, actual))
    require(bool(rows), f"manifest empty: {manifest_path}")
    return {"entry_count": len(rows), "verified_paths": [row[0] for row in rows]}


def git_output(root: Path, *args: str, check: bool = True) -> str:
    run = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if check and run.returncode != 0:
        raise AuditError(f"git {chr(32).join(args)} failed: {run.stderr.strip()}")
    return run.stdout.strip()


def git_commit_exists(root: Path, commit: str) -> bool:
    run = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
        text=True,
        capture_output=True,
    )
    return run.returncode == 0


def verify_protocol(root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    require(protocol.get("protocol_status") == "FROZEN_BEFORE_NEW_AUDIT_EXECUTION", "audit protocol is not frozen")
    require(protocol.get("new_audit_outputs_accessed") is False, "audit protocol records prior new-output access")
    require(protocol.get("authority") == "REPRODUCIBILITY_AND_NEGATIVE_DISPOSITION_AUDIT_ONLY", "audit protocol authority drift")
    amendment_path = protocol_path.parent / "PROTOCOL_AMENDMENT_A.json"
    amendment = load_json(amendment_path)
    require(amendment.get("status") == "FROZEN_BEFORE_CORRECTED_AUDIT_REEXECUTION", "audit protocol amendment is not frozen")
    require(amendment.get("base_protocol_sha256") == sha256_file(protocol_path), "audit protocol amendment base drift")
    replacement = amendment.get("allowed_input_replacement", {})
    require(replacement.get("execution_freeze_expected_sha256") == replacement.get("corrected_sha256"), "audit amendment does not restore execution-bound identity")
    require(amendment.get("scientific_fields_changed") == [] and amendment.get("outcome_files_changed") == [], "audit amendment changes scientific outputs")
    amendment_b_path = protocol_path.parent / "PROTOCOL_AMENDMENT_B.json"
    amendment_b = load_json(amendment_b_path)
    require(amendment_b.get("status") == "FROZEN_BEFORE_SECOND_CORRECTED_AUDIT_REEXECUTION", "second audit protocol amendment is not frozen")
    require(amendment_b.get("base_protocol_sha256") == sha256_file(protocol_path), "second audit amendment base drift")
    require(amendment_b.get("prior_amendment_sha256") == sha256_file(amendment_path), "second audit amendment chain drift")
    replacement_b = amendment_b.get("allowed_input_replacement", {})
    repaired_b = root / str(replacement_b.get("path"))
    require(repaired_b.is_file() and sha256_file(repaired_b) == replacement_b.get("corrected_sha256") == replacement_b.get("manifest_expected_sha256"), "second audit identity repair drift")
    require(amendment_b.get("scientific_fields_changed") == [] and amendment_b.get("outcome_files_changed") == [], "second audit amendment changes scientific outputs")
    for relative, expected in protocol.get("inputs_sha256", {}).items():
        candidate = root / relative
        require(candidate.is_file(), f"protocol input missing: {relative}")
        if relative == replacement.get("path"):
            require(expected == replacement.get("old_sha256"), f"audit amendment old identity mismatch: {relative}")
            expected = replacement.get("corrected_sha256")
        require(sha256_file(candidate) == expected, f"protocol input drift: {relative}")
    base = str(protocol["base_origin_main"])
    run = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", base, "HEAD"])
    require(run.returncode == 0, "frozen origin/main base is not an ancestor of HEAD")
    return {
        "audit_id": protocol["audit_id"],
        "base_origin_main": base,
        "input_count": len(protocol["inputs_sha256"]),
        "protocol_sha256": sha256_file(protocol_path),
        "protocol_git_blob_sha1": git_output(root, "hash-object", str(protocol_path.relative_to(root))),
        "authority": protocol["authority"],
        "amendment_sha256": sha256_file(amendment_path),
        "amendment_boundary": amendment["claim_boundary"],
        "second_amendment_sha256": sha256_file(amendment_b_path),
        "second_amendment_boundary": amendment_b["claim_boundary"],
    }


def audit_historical_h1(root: Path) -> dict[str, Any]:
    path = root / "papers/orion-11-recursive-epistemic-reconstruction/results/P1-T2_baseline_ablation_results.json"
    table = load_json(path)
    require(table.get("status") == "OK", "historical H1 table is not coherent")
    comparator_id = str(table.get("comparator", {}).get("system_id"))
    rows = table.get("rows")
    require(isinstance(rows, list), "historical H1 rows missing")
    relevant = {
        str(row.get("system_id")): row
        for row in rows
        if isinstance(row, dict)
        and row.get("scope") == "ALL"
        and row.get("system_id") in {comparator_id, "orion_full"}
    }
    require(set(relevant) == {comparator_id, "orion_full"}, "historical H1 subject/comparator row identity mismatch")
    baseline = relevant[comparator_id]
    subject = relevant["orion_full"]
    b_rate = baseline.get("rate", {})
    s_rate = subject.get("rate", {})
    require((b_rate.get("successes"), b_rate.get("n")) == (1, 48), "historical comparator floor drift")
    require((s_rate.get("successes"), s_rate.get("n")) == (1, 48), "historical subject floor drift")
    difference = subject.get("difference_vs_comparator", {})
    assessment = difference.get("assessment", {})
    require(assessment.get("hypothesis_id") == "P1.H1", "historical H1 identity drift")
    require(assessment.get("verdict") == "NOT_SUPPORTED", "historical broad H1 was promoted")
    require(float(difference.get("absolute_effect")) == 0.0, "historical broad H1 effect drift")
    return {
        "baseline_root_success": "1/48",
        "comparator_system_id": comparator_id,
        "difference": 0.0,
        "subject_root_success": "1/48",
        "terminal": "NOT_SUPPORTED",
    }


def _gzip_digest_and_rows(path: Path, *, collect_task_ids: bool) -> tuple[str, int, tuple[str, ...]]:
    h = hashlib.sha256()
    count = 0
    task_ids: list[str] = []
    try:
        with gzip.open(path, "rb") as handle:
            for raw in handle:
                h.update(raw)
                count += 1
                if collect_task_ids:
                    payload = json.loads(raw)
                    require(isinstance(payload, dict) and isinstance(payload.get("task_id"), str), f"task id missing in {path}")
                    task_ids.append(payload["task_id"])
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"gzip/JSONL read failed: {path}: {exc}") from exc
    if collect_task_ids:
        require(len(task_ids) == len(set(task_ids)), f"duplicate task id in {path}")
    return h.hexdigest(), count, tuple(task_ids)


def _verify_sources(root: Path, freeze: dict[str, Any], label: str) -> int:
    count = 0
    for relative, expected in freeze.get("source_sha256", {}).items():
        candidate = root / relative
        require(candidate.is_file(), f"{label} source missing: {relative}")
        require(sha256_file(candidate) == expected, f"{label} source drift: {relative}")
        count += 1
    require(count > 0, f"{label} has no source bindings")
    return count


def _verify_primary_world_source_amendment(
    root: Path,
    base: Path,
    world_freeze: dict[str, Any],
    execution: dict[str, Any],
) -> int:
    amendment = load_json(base / "EXECUTION_BINDING_AMENDMENT_V2.json")
    require(amendment.get("arms_executed_before_correction") is False, "primary source amendment followed arm execution")
    require(amendment.get("scientific_terminal_observed_before_correction") is False, "primary source amendment followed scientific output access")
    require(amendment.get("confirmatory_worlds_changed") is False and amendment.get("protocol_or_margin_changed") is False, "primary source amendment changed frozen science")
    changes = amendment.get("source_hash_changes", {})
    require(set(changes) == {
        "src/orion/study/p1_causal/absorbed_mechanics.py",
        "src/orion/study/p1_causal/necessity_statistics.py",
    }, "primary source amendment change set drift")
    count = 0
    for relative, frozen_hash in world_freeze.get("source_sha256", {}).items():
        current_hash = sha256_file(root / relative)
        if relative in changes:
            require(frozen_hash == changes[relative].get("old"), f"primary amendment old hash drift: {relative}")
            require(current_hash == changes[relative].get("new"), f"primary amendment new source drift: {relative}")
            require(execution.get("source_sha256", {}).get(relative) == current_hash, f"primary execution does not bind amended source: {relative}")
        else:
            require(current_hash == frozen_hash, f"primary unchanged world source drift: {relative}")
            if relative in execution.get("source_sha256", {}):
                require(execution["source_sha256"][relative] == frozen_hash, f"primary execution/world source mismatch: {relative}")
        count += 1
    return count


def _verify_protocol_chain(root: Path, world_freeze: dict[str, Any]) -> int:
    chain = world_freeze.get("protocol_chain", {})
    nodes = chain.get("nodes")
    require(chain.get("ancestor_pins_validated") is True and isinstance(nodes, list) and len(nodes) == 5, "protocol chain invalid")
    for node in nodes:
        path = root / str(node["path"])
        require(path.is_file(), f"protocol node missing: {path}")
        require(sha256_file(path) == node["sha256"], f"protocol node SHA-256 drift: {path}")
        blob = git_output(root, "hash-object", str(path.relative_to(root)))
        require(blob == node["git_blob_sha"], f"protocol node Git blob drift: {path}")
    return len(nodes)


def audit_necessity_run(root: Path, label: str) -> tuple[dict[str, Any], set[str], list[str]]:
    base = root / "research/revival/p1/confirmatory/v2.2"
    if label == "primary":
        run_dir = base / "primary"
        result_path = run_dir / "PRIMARY_RESULT.json"
        provenance_path = run_dir / "PRIMARY_RUN_PROVENANCE.json"
        execution_path = base / "PRIMARY_EXECUTION_FREEZE_V3.json"
        world_freeze_path = base / "PRIMARY_WORLD_FREEZE.json"
        result_hash_key = "primary_result_sha256"
        history_keys = ["execution_source_head", "archival_head_before_result_commit"]
    elif label == "replication":
        run_dir = base / "replication"
        result_path = run_dir / "REPLICATION_RESULT.json"
        provenance_path = run_dir / "REPLICATION_RUN_PROVENANCE.json"
        execution_path = run_dir / "REPLICATION_EXECUTION_FREEZE.json"
        world_freeze_path = run_dir / "REPLICATION_WORLD_FREEZE.json"
        result_hash_key = "replication_result_sha256"
        history_keys = ["execution_source_head"]
    else:
        raise AuditError(f"unknown necessity run: {label}")

    manifest = verify_manifest(run_dir / "SHA256SUMS")
    result = load_json(result_path)
    provenance = load_json(provenance_path)
    execution = load_json(execution_path)
    world_freeze = load_json(world_freeze_path)
    independent_path = run_dir / "INDEPENDENT_VERIFICATION.json"
    independent = load_json(independent_path)

    require(execution.get("arms_executed") is False and execution.get("outcome_accessed") is False, f"{label} execution freeze is not pre-output")
    require(execution.get("protocol_version") == "P1.epistemic-mutation-necessity.v2.2.4", f"{label} protocol version drift")
    require(int(execution.get("n", -1)) == 2882, f"{label} execution N drift")
    require(sha256_file(world_freeze_path) == execution.get("world_freeze_sha256"), f"{label} world-freeze identity drift")
    require(sha256_file(execution_path) == result.get("execution_freeze_sha256"), f"{label} result/execution binding drift")
    require(sha256_file(result_path) == provenance.get(result_hash_key), f"{label} result/provenance binding drift")
    require(sha256_file(independent_path) == provenance.get("independent_verification_sha256"), f"{label} independent-verification binding drift")

    public_gz = run_dir / "WORLD_PUBLIC.jsonl.gz"
    protected_gz = run_dir / "PROTECTED_RESPONSE_MATRIX.jsonl.gz"
    raw_gz = run_dir / "RAW_RESULTS.jsonl.gz"
    public_sha, public_rows, public_ids = _gzip_digest_and_rows(public_gz, collect_task_ids=True)
    protected_sha, protected_rows, protected_ids = _gzip_digest_and_rows(protected_gz, collect_task_ids=True)
    raw_sha, raw_rows, _ = _gzip_digest_and_rows(raw_gz, collect_task_ids=False)
    require(public_ids == protected_ids, f"{label} public/protected task order mismatch")
    require((public_rows, protected_rows, raw_rows) == (2882, 2882, 40348), f"{label} archived row counts drift")

    expected_gz = {
        "public_world_gz_sha256": public_gz,
        "protected_response_matrix_gz_sha256": protected_gz,
        "raw_results_gz_sha256": raw_gz,
    }
    for key, path in expected_gz.items():
        require(sha256_file(path) == provenance.get(key), f"{label} compressed hash drift: {key}")
    require(public_sha == provenance.get("public_world_sha256") == execution.get("public_sha256"), f"{label} public-world content drift")
    require(protected_sha == provenance.get("protected_response_matrix_sha256") == execution.get("protected_response_matrix_sha256"), f"{label} protected-matrix content drift")
    require(raw_sha == provenance.get("raw_results_sha256") == result.get("raw_results_sha256"), f"{label} raw-result content drift")

    require(result.get("terminal") == "P1_MUTATION_NECESSITY_SUPPORTED", f"{label} terminal drift")
    require(result.get("n_worlds") == 2882 and result.get("n_runnable_arms") == 9 and result.get("n_ablation_arms") == 5, f"{label} result dimensions drift")
    require(result.get("analysis", {}).get("all_support_gates_pass") is True, f"{label} frozen gates do not all pass")
    require(independent.get("verdict") == "PASS", f"{label} independent verification failed")
    require(independent.get("score_mismatch_count") == 0 and independent.get("analysis_mismatch_count") == 0, f"{label} verification mismatches")
    require(independent.get("n_worlds") == 2882 and independent.get("n_raw_rows") == 40348 and independent.get("expected_rows") == 40348, f"{label} independent row counts drift")
    require(independent.get("terminal_matches") is True and independent.get("recomputed_terminal") == result.get("terminal"), f"{label} independent terminal mismatch")
    outcome_counts = independent.get("outcome_counts_by_arm", {})
    require(len(outcome_counts) == 14 and set(outcome_counts.values()) == {2882}, f"{label} arm coverage drift")

    source_checks = _verify_sources(root, execution, f"{label} execution")
    chain_nodes = 0
    if label == "primary":
        source_checks += _verify_primary_world_source_amendment(root, base, world_freeze, execution)
        chain_nodes = _verify_protocol_chain(root, world_freeze)
    else:
        source_checks += _verify_sources(root, world_freeze, f"{label} world")

    missing_commits = []
    for key in history_keys:
        commit = str(provenance.get(key, ""))
        require(len(commit) == 40, f"{label} provenance commit malformed: {key}")
        if not git_commit_exists(root, commit):
            missing_commits.append(commit)

    return (
        {
            "manifest_entries": manifest["entry_count"],
            "n_worlds": public_rows,
            "n_score_rows": raw_rows,
            "protocol_chain_nodes_checked": chain_nodes,
            "source_hash_checks": source_checks,
            "terminal": result["terminal"],
            "verification": "PASS__ZERO_SCORE_OR_ANALYSIS_MISMATCHES",
            "claim_boundary": result.get("claim_boundary"),
        },
        set(public_ids),
        missing_commits,
    )


def audit_necessity(root: Path) -> dict[str, Any]:
    primary, primary_ids, primary_missing = audit_necessity_run(root, "primary")
    replication, replication_ids, replication_missing = audit_necessity_run(root, "replication")
    overlap = primary_ids & replication_ids
    require(not overlap, "primary and replication task identities overlap")
    missing = primary_missing + replication_missing
    require(len(set(missing)) == len(missing), "duplicate historical provenance commit identifiers")
    history = {
        "missing_commits": missing,
        "status": "CANNOT_CHECK_HISTORICAL_PROSPECTIVE_ORDER" if missing else "REACHABLE_HISTORY_VERIFIED",
        "interpretation": (
            "Archived bytes and current bound sources are reproducible; unreachable historical execution-source commits prevent independent confirmation of the claimed original commit-order custody."
            if missing
            else "All referenced historical execution commits are reachable."
        ),
    }
    return {
        "primary": primary,
        "replication": replication,
        "task_id_intersection_count": 0,
        "historical_prospective_order": history,
        "authority_boundary": "CREDENTIAL_FREE_DETERMINISTIC_MECHANICAL_ONLY__NO_EXTERNAL_OR_MODEL_GENERAL_AUTHORITY",
    }


MISSING_OWNER_FIELDS = [
    "EXHAUSTIVE_POSTPUBLICATION_COORDINATE",
    "LICENSED_POSTPUBLICATION_OPERATIONS",
    "FORBIDDEN_POSTPUBLICATION_OPERATIONS",
    "OWNER_RATIFIED_DECISION_TO_POSTPUBLICATION_BRIDGE_OR_EXPLICIT_NONE",
    "TARGET_ERROR_TIMEOUT_MALFORMED_UNSUPPORTED_TERMINAL_BEHAVIOR",
]


def _canonical_mapping(mapping: dict[str, str]) -> str:
    return json.dumps(mapping, sort_keys=True, separators=(",", ":"))


def audit_adapter_payloads(adjudication: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    pair = adjudication.get("pair_matrix", {})
    pair_rows = pair.get("rows")
    require(isinstance(pair_rows, list) and len(pair_rows) == 42, "adapter pair matrix must have 42 rows")
    matrix: dict[str, dict[str, str]] = {}
    seen_pairs: set[tuple[str, str]] = set()
    status_counts: Counter[str] = Counter()
    for row in pair_rows:
        require(isinstance(row, dict), "adapter pair row is not an object")
        source = str(row.get("source_terminal"))
        target = str(row.get("target_decision"))
        status = str(row.get("v8_status"))
        require(status in {"PASS", "REJECT", "CANNOT_CHECK"}, "adapter pair status invalid")
        require((source, target) not in seen_pairs, "adapter pair matrix duplicate row")
        seen_pairs.add((source, target))
        matrix.setdefault(source, {})[target] = status
        status_counts[status] += 1
    sources = sorted(matrix)
    targets = sorted({target for row in matrix.values() for target in row})
    require(len(sources) == 6 and len(targets) == 7, "adapter source/target dimensions drift")
    require(all(set(matrix[source]) == set(targets) for source in sources), "adapter pair matrix is incomplete")
    require(dict(sorted(status_counts.items())) == pair.get("status_counts") == {"CANNOT_CHECK": 30, "PASS": 1, "REJECT": 11}, "adapter pair status counts drift")

    counts: Counter[str] = Counter()
    survivor_by_mapping: dict[str, str] = {}
    for values in itertools.product(targets, repeat=len(sources)):
        mapping = dict(zip(sources, values, strict=True))
        statuses = [matrix[source][target] for source, target in mapping.items()]
        if len(set(values)) != len(values) or "REJECT" in statuses:
            counts["known_rejected"] += 1
        elif all(status == "PASS" for status in statuses):
            counts["fully_certified"] += 1
        else:
            counts["not_disproved_but_uncertified"] += 1
            require(mapping.get("UNRESOLVED") == "UNRESOLVED", "surviving adapter violates fail-closed unresolved mapping")
            canonical = _canonical_mapping(mapping)
            adapter_id = "P1V8-ADAPTER-" + sha256_bytes(canonical.encode())[:16]
            require(canonical not in survivor_by_mapping, "adapter enumeration duplicate survivor")
            survivor_by_mapping[canonical] = adapter_id
    counts["total"] = sum(counts.values())
    enumeration = {
        "fully_certified": counts["fully_certified"],
        "known_rejected": counts["known_rejected"],
        "not_disproved_but_uncertified": counts["not_disproved_but_uncertified"],
        "total": counts["total"],
    }
    require(enumeration == {"fully_certified": 0, "known_rejected": 116929, "not_disproved_but_uncertified": 720, "total": 117649}, "adapter enumeration partition drift")

    rows = registry.get("rows")
    require(registry.get("row_count") == 720 and isinstance(rows, list) and len(rows) == 720, "adapter registry row count drift")
    registry_by_mapping: dict[str, str] = {}
    seen_ids: set[str] = set()
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get("mapping"), dict), "adapter registry malformed row")
        canonical = _canonical_mapping(row["mapping"])
        adapter_id = str(row.get("adapter_id"))
        require(canonical not in registry_by_mapping and adapter_id not in seen_ids, "adapter registry duplicate row")
        require(adapter_id == "P1V8-ADAPTER-" + sha256_bytes(canonical.encode())[:16], "adapter registry noncanonical id")
        require(row.get("actionable_image_count") == 5, "adapter registry actionable image count drift")
        require(row.get("essential_fields_still_missing_for_every_actionable_image") == MISSING_OWNER_FIELDS, "adapter registry missing-owner fields drift")
        require(row.get("positive_status") == "CANNOT_CHECK_UNTIL_OWNER_ALGEBRA", "adapter registry CANNOT_CHECK status drift")
        require(row.get("negative_status") == "NO_AUTHORITATIVE_CONTRADICTION_WITNESS__DO_NOT_INFER_IMPOSSIBILITY", "adapter registry impossibility overclaim")
        registry_by_mapping[canonical] = adapter_id
        seen_ids.add(adapter_id)
    require(registry_by_mapping == survivor_by_mapping, "adapter registry does not exactly match exhaustive survivors")
    return {"enumeration": enumeration, "registry_exact_match": True}


def audit_adapters(root: Path) -> dict[str, Any]:
    directory = root / "development/p1-source-native-target-semantics-v8-2026-08-23"
    manifest = verify_manifest(directory / "SHA256SUMS")
    adjudication = load_json(directory / "P1_V8_ADAPTER_ADJUDICATION_RESULT.json")
    registry = load_json(directory / "P1_V8_720_ADAPTER_REGISTRY.json")
    core = audit_adapter_payloads(adjudication, registry)

    semantic = load_json(directory / "P1_V8_TARGET_SEMANTIC_REGISTRY.json")
    require(semantic.get("target_count") == 7 and semantic.get("actionable_target_count") == 6, "target semantic dimensions drift")
    require(semantic.get("actionable_targets_with_complete_postpublication_denotation") == 0, "target semantic completion drift")
    actionable = [row for row in semantic.get("targets", []) if row.get("target_id") != "UNRESOLVED"]
    require(len(actionable) == 6, "actionable target registry drift")
    require(all(row.get("licensed_postpublication_operations") == "UNBOUND" for row in actionable), "actionable target operations self-authorized")
    require(all(row.get("owner_ratified_postpublication_bridge") is False for row in actionable), "actionable target owner bridge self-authorized")

    owner_schema = load_json(directory / "P1_V8_REQUIRED_OWNER_ALGEBRA_SCHEMA.json")
    require(isinstance(owner_schema.get("required"), list) and len(owner_schema["required"]) == 10, "owner algebra schema drift")

    v13_dir = root / "development/p1-owner-custody-positive-successor-v13-2026-08-24"
    v13_result = load_json(v13_dir / "RESULT_V13.json")
    v13_status = load_json(v13_dir / "AUTHORITY_EXECUTION_STATUS_V13.json")
    require(v13_result.get("adverse_result", {}).get("external_outputs_received") == 0, "external output count drift")
    require(v13_result.get("adverse_result", {}).get("external_outputs_required") == 7, "external output denominator drift")
    require(v13_result.get("adverse_result", {}).get("authority_acts_closed") == 0, "authority acts were silently closed")
    require(v13_result.get("adverse_result", {}).get("authority_acts_required") == 4, "authority-act denominator drift")
    require(v13_status.get("map_audit_authorized") is False, "map audit was self-authorized")
    require(v13_status.get("closed_authority_acts") == 0, "external authority state drift")
    require(all(value is False for value in v13_status.get("authority_acts", {}).values()), "external authority act fabricated")

    return {
        **core,
        "v8_manifest_entries": manifest["entry_count"],
        "in_repo_reauditable": 720,
        "in_repo_resolvable": 0,
        "externally_blocked": 720,
        "setup_failure_count": 0,
        "external_resource": (
            "R7 vocabulary owner or formally delegated custodian must complete, license, content-address, and sign the seven-target owner algebra; host authority, target-corpus rights, and an independent semantic review must then be supplied through an authorized delivery channel."
        ),
        "external_outputs_received": "0/7",
        "authority_acts_closed": "0/4",
        "terminal": "CANNOT_CHECK_EXTERNAL_OWNER_ALGEBRA",
        "boundary": "ALL_720_ARE_ENUMERABLE_IN_REPO__ZERO_ARE_RESOLVABLE_WITHOUT_EXTERNAL_OWNER_AUTHORITY__NOT_IMPOSSIBILITY",
    }


def audit_rse(root: Path) -> dict[str, Any]:
    boundary = (root / "papers/orion-11-recursive-epistemic-reconstruction/RSE_SUCCESSOR_BOUNDARY_V1.md").read_text()
    handoff = (root / "research/paper-programme-v1/RSE_P1_P10_HANDOFF_2026-08-20.md").read_text()
    receipt = load_json(root / "research/extensions/meta-orion-recursive-scientific-evolution/INDEPENDENT_FORMAL_VERIFICATION_V1.json")
    require("donor-subsumed by a fixed generic justification condition language" in boundary, "RSE paper boundary no longer preserves donor subtraction")
    require("GENERIC_JUSTIFICATION_DONOR_SUFFICIENT" in handoff, "RSE handoff terminal missing")
    result = receipt.get("result", {})
    require(result.get("checks", {}).get("RSE.T5") is True, "RSE.T5 independent check failed")
    require("generic justification donor sufficiency" in result.get("interpretation", {}).get("RSE.T5", ""), "RSE.T5 interpretation drift")
    return {
        "terminal": "GENERIC_JUSTIFICATION_DONOR_SUFFICIENT",
        "disposition": "EARNED_SCOPE_NARROWING__PRESERVE_AS_NEGATIVE_SCIENCE",
        "does_not_modify_necessity_successor": True,
        "superiority_claim_authorized": False,
    }


def build_receipt(root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = verify_protocol(root, protocol_path)
    historical = audit_historical_h1(root)
    necessity = audit_necessity(root)
    adapters = audit_adapters(root)
    rse = audit_rse(root)
    return {
        "schema_version": "orion.orion11.negative-revival-audit-receipt.v1",
        "audited_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "audit_passed": True,
        "protocol": protocol,
        "historical_broad_h1": historical,
        "necessity_v2_2_4": necessity,
        "adapter_maps": adapters,
        "rse_donor_subtraction": rse,
        "freeze_authority": "NONE__DO_NOT_FREEZE_OR_MERGE",
        "submission_authority": "NONE__LOCAL_MECHANICAL_RECEIPTS_ARE_NOT_EXTERNAL_REVIEW",
        "terminal": "ORION11_NEGATIVE_REVIVAL_AUDIT_PASS_WITH_PRESERVED_CANNOT_CHECK",
        "claim_boundary": "ORION11_SPECIFIC_REPRODUCIBILITY_AND_NEGATIVE_DISPOSITION_ONLY__NO_GLOBAL_PAPER_FREEZE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    protocol = args.protocol or root / "papers/orion-11-recursive-epistemic-reconstruction/revival/r1-negative-revival-audit/PROTOCOL_FREEZE.json"
    try:
        receipt = build_receipt(root, protocol.resolve())
    except AuditError as exc:
        print(json.dumps({"audit_passed": False, "error": str(exc)}, sort_keys=True))
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "audit_passed": True,
        "terminal": receipt["terminal"],
        "historical_h1": receipt["historical_broad_h1"]["terminal"],
        "adapter_terminal": receipt["adapter_maps"]["terminal"],
        "freeze_authority": receipt["freeze_authority"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
