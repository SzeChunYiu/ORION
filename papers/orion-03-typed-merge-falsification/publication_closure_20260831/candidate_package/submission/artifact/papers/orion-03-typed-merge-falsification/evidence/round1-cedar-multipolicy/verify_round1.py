#!/usr/bin/env python3
"""Verify and assemble the frozen ORION-03 Cedar Round-1 evidence.

Python verifies content bindings and cross-language receipt equality.  The
native Cedar semantic decision is executed by the separately pinned Rust
runner; this script never substitutes for that engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
GIT_REPOSITORY = Path(os.environ.get("ORION03_GIT_REPOSITORY", HERE))
SNAPSHOT = HERE / "third_party" / "cedar-integration-tests"
SOURCE_MANIFEST = HERE / "SOURCE_BINDING_V1.json"
PYTHON_RECEIPT = HERE / "PYTHON_ADJUDICATION_V1.json"
RUST_RECEIPT = HERE / "RUST_ADJUDICATION_V1.json"
LEAN_RECEIPT = HERE / "LEAN_ADJUDICATION_V1.json"
HOSTILE_RECEIPT = HERE / "HOSTILE_REVIEW_V1.json"
FINAL_RESULT = HERE / "ROUND1_RESULTS_V1.json"
AGENTGATEWAY = (
    HERE.parent
    / "convergence-v1"
    / "AGENTGATEWAY_ORIGIN_WITNESS_SAFE_MERGE_R11_RESULTS_SUMMARY.json"
)

UPSTREAM_COMMIT = "75989795c75d861270ce6cac38ef9d9e5b220a0c"
UPSTREAM_TREE = "3aed7b26a11a3b85bd29a4b2156437be74c33333"
CEDAR_COMMIT = "bcb8bd93a292b59ae8f1dcf53b9b4176a2d3405d"
PROTOCOL_COMMIT = "e393958512d9f726f0f39fe02ae22520db647d08"
EXECUTOR_COMMIT = "097210a821b4d4f7c76f296d66c2614b8a0dc93f"
SOURCE_TERMINAL = "CONFIRMED_PUBLIC_OFFICIAL_PERMISSION_BEARING"
ROUND_TERMINAL = "D_R11_POLICY_REQUIRES_RICHER_SEMANTICS"
AGENTGATEWAY_TERMINAL = "AGENTGATEWAY_RULESETS_ORIGIN_WITNESS_SAFE"
AGENTGATEWAY_SHA256 = (
    "18f05100d6a982a6274e8fe15920ca708bc2ff40f070cd16a96445aa4b963a35"
)

UPSTREAM_AUTHORITY_KEYS = {
    "authority",
    "authority_origin",
    "evidence_origin",
    "evidence_license",
    "evidence_licence",
    "license",
    "licence",
    "provenance",
    "retracted",
    "retraction",
    "reviewed_source",
    "source_authority",
    "source_license",
    "source_licence",
}


def fail(message: str) -> None:
    raise SystemExit(f"ORION03_R1_VERIFY_FAIL: {message}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read canonical JSON {path}: {exc}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git identity


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_canonical(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def walk_keys(value: Any, prefix: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{prefix}/{key}"
            out.append(here)
            out.extend(walk_keys(child, here))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            out.extend(walk_keys(child, f"{prefix}/{i}"))
    return out


def verify_source() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = read_json(SOURCE_MANIFEST)
    if manifest.get("schema") != "ORION.ORION03.CedarMultiPolicy.SourceBinding.v1":
        fail("wrong source-binding schema")
    upstream = manifest.get("upstream", {})
    expected_upstream = {
        "repository": "cedar-policy/cedar-integration-tests",
        "commit": UPSTREAM_COMMIT,
        "tree": UPSTREAM_TREE,
        "cedar_submodule_commit": CEDAR_COMMIT,
        "license_spdx": "Apache-2.0",
        "official_owner": "cedar-policy",
        "public": True,
        "github_signature_verified": True,
    }
    for key, expected in expected_upstream.items():
        if upstream.get(key) != expected:
            fail(f"source binding upstream {key} drift")
    if manifest.get("authority", {}).get("source_identity") != SOURCE_TERMINAL:
        fail("source identity terminal drift")

    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        fail("source file binding is empty")
    bound_paths = {row.get("path") for row in rows}
    actual_paths = {
        path.relative_to(SNAPSHOT).as_posix()
        for path in SNAPSHOT.rglob("*")
        if path.is_file()
    }
    if bound_paths != actual_paths:
        fail(
            "vendored file set differs from source manifest: "
            f"missing={sorted(bound_paths - actual_paths)} "
            f"extra={sorted(actual_paths - bound_paths)}"
        )
    for row in rows:
        rel = row["path"]
        path = SNAPSHOT / rel
        data = path.read_bytes()
        if len(data) != row.get("bytes"):
            fail(f"byte count drift: {rel}")
        if hashlib.sha256(data).hexdigest() != row.get("sha256"):
            fail(f"SHA-256 drift: {rel}")
        if git_blob_sha1(data) != row.get("git_blob"):
            fail(f"Git blob drift: {rel}")
    notice = re.sub(r"\s+", " ", (SNAPSHOT / "NOTICE").read_text()).strip()
    if notice != "Copyright Cedar Contributors":
        fail("upstream NOTICE drift")
    if "Apache License" not in (SNAPSHOT / "LICENSE").read_text():
        fail("upstream license text drift")
    return manifest, rows


def build_python_receipt() -> dict[str, Any]:
    manifest, rows = verify_source()
    selection = manifest["selection"]
    fixture_paths = selection["fixture_paths"]
    if fixture_paths != [f"tests/multi/{i}.json" for i in range(1, 6)]:
        fail("fixture selection is not the complete frozen multi family")

    request_rows: list[dict[str, Any]] = []
    authority_key_paths: list[str] = []
    policy_counts: dict[str, dict[str, int]] = {}
    total_permits = 0
    total_forbids = 0

    for fixture_rel in fixture_paths:
        fixture = read_json(SNAPSHOT / fixture_rel)
        if fixture.get("shouldValidate") is not True:
            fail(f"fixture not frozen as schema-valid: {fixture_rel}")
        for key_path in walk_keys(fixture):
            key = key_path.rsplit("/", 1)[-1].lower()
            if key in UPSTREAM_AUTHORITY_KEYS:
                authority_key_paths.append(f"{fixture_rel}{key_path}")

        policy_rel = fixture.get("policies")
        entity_rel = fixture.get("entities")
        schema_rel = fixture.get("schema")
        for field, rel in (
            ("policies", policy_rel),
            ("entities", entity_rel),
            ("schema", schema_rel),
        ):
            if not isinstance(rel, str) or not (SNAPSHOT / rel).is_file():
                fail(f"fixture {fixture_rel} has unbound {field} path")

        policy_text = (SNAPSHOT / policy_rel).read_text(encoding="utf-8")
        effects = re.findall(r"(?m)^\s*(permit|forbid)\s*\(", policy_text)
        if not effects:
            fail(f"no policies parsed in {policy_rel}")
        permits = effects.count("permit")
        forbids = effects.count("forbid")
        policy_counts[policy_rel] = {
            "policies": len(effects),
            "permits": permits,
            "forbids": forbids,
        }
        total_permits += permits
        total_forbids += forbids

        requests = fixture.get("requests")
        if not isinstance(requests, list) or not requests:
            fail(f"fixture has no requests: {fixture_rel}")
        for index, request in enumerate(requests):
            decision = request.get("decision")
            reasons = request.get("reason")
            errors = request.get("errors")
            if decision not in {"allow", "deny"}:
                fail(f"invalid decision label in {fixture_rel} request {index}")
            if not isinstance(reasons, list) or not all(
                isinstance(reason, str) for reason in reasons
            ):
                fail(f"invalid reason set in {fixture_rel} request {index}")
            if not isinstance(errors, list):
                fail(f"invalid error set in {fixture_rel} request {index}")
            valid_ids = {f"policy{i}" for i in range(len(effects))}
            if not set(reasons).issubset(valid_ids):
                fail(f"unknown reason policy ID in {fixture_rel} request {index}")
            request_rows.append(
                {
                    "case": f"multi_{Path(fixture_rel).stem}_request_{index}",
                    "decision": decision.upper(),
                    "errors": len(errors),
                    "flat_projection_decision": decision.upper(),
                    "reason_origins": sorted(reasons),
                    "typed_projection_decision": decision.upper(),
                    "typed_provenance_kind": (
                        "NATIVE_POLICY_REASON_SET"
                        if reasons
                        else "DEFAULT_DENY_NO_POLICY_ORIGIN"
                    ),
                }
            )

    request_count = len(request_rows)
    allow_count = sum(row["decision"] == "ALLOW" for row in request_rows)
    deny_count = request_count - allow_count
    reason_cardinality = {
        str(cardinality): sum(
            len(row["reason_origins"]) == cardinality for row in request_rows
        )
        for cardinality in sorted({len(row["reason_origins"]) for row in request_rows})
    }
    nonempty_reason_rows = sum(bool(row["reason_origins"]) for row in request_rows)

    if request_count != selection.get("request_count") or request_count != 15:
        fail("request census drift")
    if {"allow": allow_count, "deny": deny_count} != selection.get(
        "decision_counts_from_public_labels"
    ):
        fail("public decision census drift")
    if reason_cardinality != selection.get(
        "reason_cardinality_counts_from_public_labels"
    ):
        fail("public reason census drift")

    agentgateway = read_json(AGENTGATEWAY)
    if sha256(AGENTGATEWAY) != AGENTGATEWAY_SHA256:
        fail("Agentgateway safe-control binding drift")
    if agentgateway.get("terminal") != AGENTGATEWAY_TERMINAL:
        fail("Agentgateway safe-control terminal drift")
    if (
        agentgateway.get("authority", {}).get("source_bound_real_system_safe_control")
        is not True
        or agentgateway.get("authority", {}).get(
            "whole_project_security_certification"
        )
        is not False
    ):
        fail("Agentgateway authority boundary drift")

    if authority_key_paths:
        preliminary_terminal = "UNRESOLVED_BY_PRECOMMITTED_TERMINAL_RULE"
    else:
        preliminary_terminal = ROUND_TERMINAL

    return {
        "schema": "ORION.ORION03.CedarMultiPolicy.PythonAdjudication.v1",
        "source": {
            "binding": "PASS",
            "commit": UPSTREAM_COMMIT,
            "cedar_submodule_commit": CEDAR_COMMIT,
            "files": len(rows),
            "fixtures": len(fixture_paths),
            "requests": request_count,
        },
        "corpus": {
            "allow": allow_count,
            "deny": deny_count,
            "errors": sum(row["errors"] for row in request_rows),
            "nonempty_reason_sets": nonempty_reason_rows,
            "reason_cardinality": reason_cardinality,
            "policies": total_permits + total_forbids,
            "permits": total_permits,
            "forbids": total_forbids,
            "policy_counts": policy_counts,
        },
        "systems": {
            "native_cedar": "REQUIRED_FROM_RUST_RECEIPT",
            "flat_projection": {
                "decision_agreement_by_definition": request_count,
                "origin_ids_retained": 0,
                "role": "ORIGIN_ERASED_NATIVE_RESPONSE_PROJECTION_ONLY",
            },
            "typed_projection": {
                "decision_agreement_by_definition": request_count,
                "native_nonempty_reason_sets_retained_exactly": nonempty_reason_rows,
                "default_deny_is_not_promoted_to_policy_origin": reason_cardinality.get(
                    "0", 0
                ),
                "role": "NATIVE_POLICY_REASON_RETENTION_ONLY",
            },
        },
        "upstream_source_authority_semantics": {
            "present": bool(authority_key_paths),
            "matching_key_paths": sorted(authority_key_paths),
            "policy_reason_ids_are_not_upstream_evidence_licences": True,
        },
        "request_rows": request_rows,
        "safe_control": {
            "path": AGENTGATEWAY.relative_to(HERE.parents[3]).as_posix(),
            "sha256": AGENTGATEWAY_SHA256,
            "terminal": AGENTGATEWAY_TERMINAL,
            "must_not_be_called_vulnerability": True,
        },
        "preliminary_terminal": preliminary_terminal,
        "authority": {
            "public_labels_visible_to_executor": True,
            "blinded": False,
            "external_independence": "CANNOT_CHECK",
            "hostile_controls_can_grant_real_domain_positive": False,
            "native_engine_authority_requires_rust_receipt": True,
            "novelty": False,
            "journal_authority": False,
            "submission_authorized": False,
        },
    }


def verify_final() -> None:
    expected_python = build_python_receipt()
    if not PYTHON_RECEIPT.is_file():
        fail("missing committed Python adjudication receipt")
    actual_python = read_json(PYTHON_RECEIPT)
    if actual_python != expected_python:
        fail("committed Python receipt does not reproduce")

    rust = read_json(RUST_RECEIPT)
    if rust.get("schema") != "ORION.ORION03.CedarMultiPolicy.RustAdjudication.v1":
        fail("Rust receipt schema drift")
    if rust.get("terminal") != "NATIVE_CEDAR_AND_RUST_CONTROLS_PASS":
        fail("native Cedar/Rust terminal is not PASS")
    if rust.get("upstream", {}).get("integration_commit") != UPSTREAM_COMMIT:
        fail("Rust integration source pin drift")
    if rust.get("upstream", {}).get("cedar_commit") != CEDAR_COMMIT:
        fail("Rust Cedar engine pin drift")
    native = rust.get("native_cedar", {})
    if native.get("fixtures_passed") != 5 or native.get("requests_adjudicated") != 15:
        fail("Rust native Cedar denominator drift")
    controls = rust.get("hostile_and_safe_controls", {})
    if controls.get("passed") != 8 or controls.get("total") != 8:
        fail("Rust hostile-control denominator drift")
    if any(case.get("status") != "PASS" for case in controls.get("cases", [])):
        fail("Rust hostile control did not pass")

    lean = read_json(LEAN_RECEIPT)
    if lean.get("schema") != "ORION.ORION03.CedarMultiPolicy.LeanAdjudication.v1":
        fail("Lean receipt schema drift")
    if lean.get("terminal") != "LEAN_TYPED_AUTHORITY_CORE_PASS":
        fail("Lean terminal is not PASS")
    if lean.get("execution_commit") != EXECUTOR_COMMIT:
        fail("Lean execution commit identity drift")
    commit_check = subprocess.run(
        ["git", "rev-parse", "--verify", f"{EXECUTOR_COMMIT}^{{commit}}"],
        cwd=GIT_REPOSITORY,
        text=True,
        capture_output=True,
        check=False,
    )
    if commit_check.returncode != 0 or commit_check.stdout.strip() != EXECUTOR_COMMIT:
        fail("Lean execution commit is not an exact reachable Git commit")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", EXECUTOR_COMMIT, "HEAD"],
        cwd=GIT_REPOSITORY,
        capture_output=True,
        check=False,
    ).returncode:
        fail("Lean execution commit is not an ancestor of the checked packet")
    lean_source = HERE / "lean" / "Orion03Round1.lean"
    toolchain = (HERE / "lean" / "lean-toolchain").read_text().strip()
    if lean.get("toolchain") != toolchain:
        fail("Lean toolchain binding drift")
    if lean.get("source_sha256") != sha256(lean_source):
        fail("Lean source hash drift")
    if lean.get("theorems_checked") != 4:
        fail("Lean theorem denominator drift")

    hostile = read_json(HOSTILE_RECEIPT)
    if hostile.get("schema") != "ORION.ORION03.CedarMultiPolicy.HostileReview.v1":
        fail("hostile-review schema drift")
    if hostile.get("terminal") != "ORION03_R1_HOSTILE_MUTATION_REVIEW_PASS":
        fail("hostile-review terminal is not PASS")
    if hostile.get("mutations_rejected") != 7 or hostile.get("mutations_total") != 7:
        fail("hostile-review denominator drift")
    if any(
        row.get("status") != "REJECTED_AS_REQUIRED"
        for row in hostile.get("mutations", [])
    ):
        fail("hostile review accepted a mutation")

    result = read_json(FINAL_RESULT)
    if result.get("schema") != "ORION.ORION03.CedarMultiPolicy.Round1Result.v1":
        fail("final result schema drift")
    if result.get("terminal") != ROUND_TERMINAL:
        fail("final terminal violates frozen precedence")
    if result.get("protocol_commit") != PROTOCOL_COMMIT:
        fail("final result protocol commit identity drift")
    if result.get("executor_commit") != EXECUTOR_COMMIT:
        fail("final result executor commit identity drift")
    correction = result.get("custody_correction", {})
    if correction.get("kind") != "ADDITIVE_EXECUTOR_COMMIT_IDENTITY_REPAIR":
        fail("missing additive executor-identity correction")
    if correction.get("corrected_full_executor_commit") != EXECUTOR_COMMIT:
        fail("custody correction does not bind the exact executor commit")
    if correction.get("scientific_terminal_changed") is not False:
        fail("custody correction improperly changes the science terminal")
    if result.get("round", {}).get("consumed") != 1 or result.get("round", {}).get(
        "maximum"
    ) != 3:
        fail("round counter drift")
    receipt_hashes = result.get("receipts", {})
    for label, path in (
        ("python", PYTHON_RECEIPT),
        ("rust", RUST_RECEIPT),
        ("lean", LEAN_RECEIPT),
        ("hostile", HOSTILE_RECEIPT),
    ):
        if receipt_hashes.get(label, {}).get("sha256") != sha256(path):
            fail(f"final result {label} receipt binding drift")
        if receipt_hashes.get(label, {}).get("bytes") != path.stat().st_size:
            fail(f"final result {label} receipt byte-count drift")
    if result.get("safe_control", {}).get("terminal") != AGENTGATEWAY_TERMINAL:
        fail("final result relabeled safe control")
    if result.get("authority", {}).get("real_domain_positive") is not False:
        fail("final result improperly promotes injected controls")
    if result.get("authority", {}).get("external_independence") != "CANNOT_CHECK":
        fail("final result overstates independent adjudication")

    print(
        "ORION03_R1_CEDAR_MULTIPOLICY_VERIFY_PASS "
        f"terminal={ROUND_TERMINAL} requests=15 rust_controls=8 lean_theorems=4"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit-python", type=Path)
    group.add_argument("--check-final", action="store_true")
    args = parser.parse_args()
    if args.emit_python is not None:
        receipt = build_python_receipt()
        write_canonical(args.emit_python, receipt)
        print(
            "ORION03_R1_PYTHON_ADJUDICATION_PASS "
            f"terminal={receipt['preliminary_terminal']} requests=15"
        )
    else:
        verify_final()


if __name__ == "__main__":
    main()
