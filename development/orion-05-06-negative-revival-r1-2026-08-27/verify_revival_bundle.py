#!/usr/bin/env python3
"""Fail-closed verifier for the imported ORION-05/06 LUNARC revival bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUNDLE_REL = Path(
    "development/orion-05-06-negative-revival-r1-2026-08-27/evidence/"
    "run-506b84e6c47558764b95f4482ce6691bb3757723-v2"
)
PROTOCOL_COMMIT = "9f7e66f26148387115354d4853f3f67b7bacc02d"
EXECUTION_COMMIT = "506b84e6c47558764b95f4482ce6691bb3757723"
STAGE_MANIFEST_SHA256 = "75ca8d944f70c451e1d485929ad126c48ab3c4a38eb83fc6e761e38af52da971"
BUNDLE_MANIFEST_SHA256 = "c038cc4175cddf1a65df55c779652fe50d472d292caa7e6ae89937a0e05e92f2"

BOUND_SOURCE_PATHS = (
    "papers/orion-05-tare-expressivity/orion05_r13_parent_certificate_ordering.py",
    "papers/orion-05-tare-expressivity/orion05_xover_budget_revival.py",
    "papers/orion-05-tare-expressivity/rounds/r13-parent-certificate-ordering/ORION05_R13_PROTOCOL.json",
    "papers/orion-05-tare-expressivity/rounds/xover-budget-revival-v1/ORION05_XOVER_BUDGET_REVIVAL_PROTOCOL.json",
    "papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_COVERAGE_PROTOCOL.json",
    "papers/orion-06-recursive-recovery/revival/verify_orion06_negative_coverage.py",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _parse_manifest(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text().splitlines():
        digest, relative = line.split("  ", 1)
        rows.append((digest, relative.removeprefix("./")))
    return rows


def _verify_manifest(base: Path, manifest: Path) -> int:
    rows = _parse_manifest(manifest)
    for expected, relative in rows:
        target = base / relative
        if not target.is_file():
            raise AssertionError({"missing_manifest_file": relative})
        observed = sha256_file(target)
        if observed != expected:
            raise AssertionError({"manifest_hash_mismatch": [relative, expected, observed]})
    return len(rows)


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout


def _git_blob(root: Path, commit: str, path: str) -> bytes:
    return _git(root, "show", f"{commit}:{path}")


def _parse_key_values(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("---"):
            key, value = line.split("=", 1)
            rows[key] = value
    return rows


def _all_checks(row: dict[str, Any]) -> bool:
    groups = ("parent_witness_checks", "sparse_witness_checks", "phase_checks")
    return all(all(value is True for value in row[group].values()) for group in groups)


def verify(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    bundle = root / BUNDLE_REL
    if not bundle.is_dir():
        raise FileNotFoundError(bundle)

    bundle_manifest = bundle / "BUNDLE_SHA256SUMS"
    if sha256_file(bundle_manifest) != BUNDLE_MANIFEST_SHA256:
        raise AssertionError("bundle manifest digest drift")
    bundle_entries = _verify_manifest(bundle, bundle_manifest)

    stage_manifest = bundle / "STAGE_SHA256SUMS"
    if sha256_file(stage_manifest) != STAGE_MANIFEST_SHA256:
        raise AssertionError("stage manifest digest drift")
    stage_rows = {relative: digest for digest, relative in _parse_manifest(stage_manifest)}

    subprocess.run(
        ["git", "merge-base", "--is-ancestor", PROTOCOL_COMMIT, EXECUTION_COMMIT],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    bound_sources: dict[str, str] = {}
    for relative in BOUND_SOURCE_PATHS:
        local_digest = sha256_file(root / relative)
        staged_digest = stage_rows.get(relative)
        execution_digest = sha256_bytes(_git_blob(root, EXECUTION_COMMIT, relative))
        if not staged_digest or len({local_digest, staged_digest, execution_digest}) != 1:
            raise AssertionError(
                {
                    "source_binding_mismatch": {
                        "path": relative,
                        "local": local_digest,
                        "stage": staged_digest,
                        "execution_commit": execution_digest,
                    }
                }
            )
        if "PROTOCOL" in Path(relative).name:
            protocol_digest = sha256_bytes(_git_blob(root, PROTOCOL_COMMIT, relative))
            if protocol_digest != local_digest:
                raise AssertionError({"pre_outcome_protocol_mismatch": relative})
        bound_sources[relative] = local_digest

    remote = _parse_key_values(bundle / "REMOTE_STAGE_VERIFY.txt")
    if remote.get("source_commit") != EXECUTION_COMMIT:
        raise AssertionError("remote source commit drift")
    if remote.get("manifest_failures") != "0" or remote.get("manifest_entries") != "257":
        raise AssertionError({"remote_stage_verification": remote})

    r13_protocol = json.loads(
        (root / "papers/orion-05-tare-expressivity/rounds/r13-parent-certificate-ordering/ORION05_R13_PROTOCOL.json").read_text()
    )
    r13_raw_path = bundle / "r13/result/RAW_ATTEMPTS.jsonl"
    r13_rows = [json.loads(line) for line in r13_raw_path.read_text().splitlines()]
    r13_result = json.loads((bundle / "r13/result/ORION05_R13_RESULT.json").read_text())
    expected_cells = {
        (subject, int(index))
        for subject in r13_protocol["confirmatory_panel"]["subjects"]
        for index in r13_protocol["confirmatory_panel"]["included_heldout_indices"]
    }
    observed_cells = [(row["subject"], int(row["matching_index"])) for row in r13_rows]
    if set(observed_cells) != expected_cells or len(observed_cells) != len(set(observed_cells)):
        raise AssertionError("R13 held-out cell set drift")
    if sha256_file(r13_raw_path) != r13_result["raw_attempts_sha256"]:
        raise AssertionError("R13 raw digest drift")
    if not all(
        row["projection_valid"] is True
        and row["parent_cost"] == row["projected_cost"]
        and row["charged_total_wall_ns"] >= row["parent_wall_ns"]
        and _all_checks(row)
        for row in r13_rows
    ):
        raise AssertionError("R13 witness or accounting failure")
    exposed = set(r13_protocol["confirmatory_panel"]["excluded_exposed_indices"])
    exposed_seen = sorted({index for _, index in observed_cells} & exposed)
    if exposed_seen:
        raise AssertionError({"R13_exposed_indices_seen": exposed_seen})

    xover = json.loads((bundle / "xover/result/ORION05_XOVER_BUDGET_REVIVAL_RESULT.json").read_text())
    if not (
        xover["revival_outcome"] == "RETAINED_NEGATIVE"
        and xover["legacy_direct_dxx_revival"]["status"] == "TIMEOUT"
        and xover["strongest_parent"]["status"] == "COMPLETED"
        and xover["strongest_parent"]["witness_valid"] is True
        and xover["authority"]["whole_panel_revival"] is False
    ):
        raise AssertionError("XOVER disposition drift")

    audit = json.loads((bundle / "o06/ORION06_NEGATIVE_COVERAGE_AUDIT.json").read_text())
    unfinished = sum(row["revival_outcome"] == "UNFINISHED" for row in audit["standalone_rows"])
    observed_outcomes = {row["revival_outcome"] for row in audit["standalone_rows"]}
    if unfinished != 4 or "UNSOLVABLE" in observed_outcomes:
        raise AssertionError("ORION-06 negative classification drift")

    return {
        "schema": "ORION.ORION0506.RevivalBundleVerification.v1",
        "terminal": "ORION0506_REVIVAL_BUNDLE_VERIFIED",
        "scientific_authority_delta": "NONE",
        "bundle": {
            "path": BUNDLE_REL.as_posix(),
            "manifest_entries": bundle_entries,
            "manifest_sha256": BUNDLE_MANIFEST_SHA256,
            "stage_manifest_sha256": STAGE_MANIFEST_SHA256,
        },
        "source_chronology": {
            "pre_outcome_base_recorded_in_protocols": "0a56f4a5a28f31072c6fb3cc910804474dc2f2a6",
            "protocol_commit": PROTOCOL_COMMIT,
            "execution_commit": EXECUTION_COMMIT,
            "current_branch_import_is_additive": True,
            "frozen_protocol_rewritten": False,
            "bound_sources": bound_sources,
        },
        "remote_stage": {
            "host": remote["host"],
            "verified_utc": remote["verified_utc"],
            "manifest_entries": int(remote["manifest_entries"]),
            "manifest_failures": int(remote["manifest_failures"]),
        },
        "r13": {
            "cells": len(r13_rows),
            "unique_cells": len(set(observed_cells)),
            "exposed_indices_seen": exposed_seen,
            "all_witness_checks_pass": True,
            "outcome": r13_result["revival_outcome"],
            "production_null_preserved": r13_result["r12_null_preserved"],
        },
        "xover": {
            "outcome": xover["revival_outcome"],
            "legacy_status": xover["legacy_direct_dxx_revival"]["status"],
            "parent_status": xover["strongest_parent"]["status"],
            "whole_panel_revival": False,
        },
        "orion06_audit": {
            "standalone_rows": len(audit["standalone_rows"]),
            "unfinished": unfinished,
            "cross_domain": audit["cross_domain_general_method"]["revival_outcome"],
        },
        "unsolvable": [],
        "authority": {
            "external_independence": False,
            "novelty": False,
            "journal_or_submission": False,
            "final_freeze": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = verify(args.root)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload)
    print("ORION0506_REVIVAL_BUNDLE=PASS")
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
