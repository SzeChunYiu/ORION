#!/usr/bin/env python3
"""Outcome-free structural validator for the P5 C5 V4 packet."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ARM_ID = "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY"
COMMIT = "0f14e910d361196422d9b938f45280919952d4fd"
TREE = "3ca13a51b4fb6ff77013d8886023ee852cbf373e"
EXPECTED_BOUND = 9
EXPECTED_BLOCKING = 12


class ValidationFailure(AssertionError):
    pass


class Checks:
    def __init__(self) -> None:
        self.count = 0

    def ok(self, condition: Any, message: str) -> None:
        self.count += 1
        if not condition:
            raise ValidationFailure(message)


def load_json(name: str, checks: Checks) -> dict[str, Any]:
    path = HERE / name
    checks.ok(path.is_file(), f"missing {name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationFailure(f"invalid JSON {name}: {exc}") from exc
    checks.ok(isinstance(value, dict), f"{name} must contain an object")
    return value


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    c = Checks()
    json_names = [
        "AUDIT_RECEIPT_V4.json",
        "P5_C5_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json",
        "P5_C5_V4_CUSTODY_HANDOFF_SCHEMA.json",
        "P5_C5_V4_EXECUTION_BINDING_PROTOCOL.json",
        "P5_C5_V4_FIELD_REGISTRY.json",
        "P5_C5_V4_INFORMATION_SURFACE.json",
        "P5_C5_V4_NATIVE_OUTPUT_SCHEMA.json",
        "P5_C5_V4_NATIVE_TERMINAL_RULES.json",
        "P5_C5_V4_NEGATIVE_LEDGER.json",
        "P5_C5_V4_RESOURCE_REGISTRY.json",
        "P5_C5_V4_RESULT.json",
        "P5_C5_V4_SMOKE_RECEIPT.json",
        "P5_C5_V4_SOURCE_RIGHTS_MANIFEST.json",
        "P5_C5_V4_SOURCE_TREE_METADATA.json",
        "P5_C5_V4_WRITE_SURFACE_SCHEMA.json",
    ]
    docs = [
        "README.md",
        "SCIENTIFIC_REPORT_V4.md",
        "P5_C5_V4_NEGATIVE_LEDGER.md",
        "DOUBLE_RATCHET_DEPENDENCY_SPEC_V4.toml",
        "DOUBLE_RATCHET_DEPENDENCY_LOCK_V4.uv.lock",
        "p5_c5_native_parser.py",
        "p5_c5_isolated_runner.py",
        "p5_c5_v4_validator.py",
        "build_p5_c5_v4_freeze.py",
        "SHA256SUMS",
    ]
    loaded = {name: load_json(name, c) for name in json_names}
    for name in docs:
        c.ok((HERE / name).is_file(), f"missing {name}")
        c.ok((HERE / name).stat().st_size > 0, f"empty {name}")

    registry = loaded["P5_C5_V4_FIELD_REGISTRY.json"]
    fields = registry.get("fields")
    c.ok(registry.get("arm_id") == ARM_ID, "registry arm mismatch")
    c.ok(isinstance(fields, dict), "fields missing")
    c.ok(len(fields) == 21, "field count is not 21")
    required = registry.get("required_field_paths")
    c.ok(required == sorted(fields), "required fields are not exact/sorted")
    bound = sorted(name for name, item in fields.items() if item.get("state") == "BOUND")
    blocking = sorted(name for name, item in fields.items() if item.get("state") != "BOUND")
    c.ok(len(bound) == EXPECTED_BOUND, "wrong bound count")
    c.ok(len(blocking) == EXPECTED_BLOCKING, "wrong blocker count")
    c.ok(registry.get("bound_field_count") == EXPECTED_BOUND, "registry bound summary mismatch")
    c.ok(registry.get("blocking_field_count") == EXPECTED_BLOCKING, "registry blocker summary mismatch")
    c.ok(registry.get("bound_fields") == bound, "bound field list mismatch")
    c.ok(registry.get("blocking_fields") == blocking, "blocking field list mismatch")
    c.ok(registry.get("execution_ready") is False, "registry must refuse execution")
    c.ok(registry.get("panel_confirmatory_ready_arms") == 0, "panel readiness must be zero")
    for name, item in sorted(fields.items()):
        c.ok(item.get("state") in {"BOUND", "UNBOUND", "CANNOT_CHECK", "UNSUPPORTED"}, f"bad state {name}")
        c.ok(isinstance(item.get("residual"), str) and bool(item["residual"]), f"missing residual {name}")
        c.ok(isinstance(item.get("next_discriminator"), str) and bool(item["next_discriminator"]), f"missing next discriminator {name}")
        if item.get("state") == "BOUND":
            c.ok(item.get("cause") is None, f"bound field has cause {name}")
            c.ok(item.get("binding") is not None, f"bound field lacks binding {name}")
        else:
            c.ok(isinstance(item.get("cause"), str) and bool(item["cause"]), f"blocker lacks cause {name}")

    expected_bound = {
        "adapter.isolated_write_surface",
        "adapter.native_parser_binding",
        "identity.native_entrypoint_bytes",
        "identity.source_license_bytes",
        "identity.source_repository_commit",
        "model_provider.fallbacks",
        "resources.wallclock",
        "runtime.compute",
        "runtime.dependency_lock",
    }
    c.ok(set(bound) == expected_bound, "unexpected bound set")

    result = loaded["P5_C5_V4_RESULT.json"]
    audit = loaded["AUDIT_RECEIPT_V4.json"]
    protocol = loaded["P5_C5_V4_EXECUTION_BINDING_PROTOCOL.json"]
    c.ok(result.get("arm_id") == ARM_ID, "result arm mismatch")
    c.ok(result.get("execution", {}).get("c5_executed") is False, "C5 must not be executed")
    c.ok(result.get("execution", {}).get("execution_ready") is False, "result must refuse execution")
    c.ok(result.get("v4_repairs", {}).get("bound_fields") == EXPECTED_BOUND, "result bound count mismatch")
    c.ok(result.get("v4_repairs", {}).get("blocking_fields") == EXPECTED_BLOCKING, "result blocker count mismatch")
    c.ok(result.get("execution", {}).get("panel_confirmatory_ready_arms") == 0, "result panel readiness mismatch")
    c.ok(result.get("execution", {}).get("panel_required_arms") == 6, "panel denominator mismatch")
    terminal = result.get("terminal")
    c.ok(isinstance(terminal, str) and "TWELVE_C5_FIELDS_BLOCKING" in terminal, "terminal lacks blocker count")
    c.ok("PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK" in terminal, "terminal overclaims science")
    c.ok(protocol.get("current_terminal") == terminal, "protocol terminal mismatch")
    c.ok(audit.get("terminal") == terminal, "audit terminal mismatch")
    c.ok(audit.get("bound_field_count") == EXPECTED_BOUND, "audit bound count mismatch")
    c.ok(audit.get("blocking_field_count") == EXPECTED_BLOCKING, "audit blocker count mismatch")
    c.ok(audit.get("protected_outcomes_opened") == 0, "protected outcome access claimed")
    c.ok(audit.get("stored_split_payloads_opened") == 0, "stored split payload access claimed")
    c.ok(audit.get("result_payloads_opened") == 0, "result payload access claimed")
    c.ok(audit.get("c5_executed") is False, "audit says C5 executed")
    c.ok(audit.get("panel_ready") == "0/6", "audit panel readiness mismatch")

    source = loaded["P5_C5_V4_SOURCE_TREE_METADATA.json"]
    rights = loaded["P5_C5_V4_SOURCE_RIGHTS_MANIFEST.json"]
    c.ok(source.get("commit_sha") == COMMIT, "source commit mismatch")
    c.ok(source.get("tree_sha") == TREE, "source tree mismatch")
    c.ok(source.get("file_count") == 113, "tree file count mismatch")
    c.ok(source.get("blob_bytes") == 888822, "tree byte count mismatch")
    c.ok(source.get("stored_split_payload_paths") == 0, "unexpected stored split payloads")
    c.ok(source.get("result_payload_paths") == 0, "unexpected result payloads")
    c.ok(source.get("clean_tree") is True, "scratch clone not clean")
    c.ok(source.get("detached_head") is True, "scratch clone not detached")
    c.ok(source.get("scratch_clone_read_only") is True, "scratch clone not read-only")
    c.ok(source.get("archive_sha256") == "9426222eefc25878f7e7d1ecd1ff9824c894bc358cb8d5f31ee3c8d4a8db9640", "archive mismatch")
    c.ok(rights.get("source", {}).get("commit_sha") == COMMIT, "rights commit mismatch")
    c.ok(rights.get("source", {}).get("tree_sha") == TREE, "rights tree mismatch")
    c.ok(rights.get("source", {}).get("root_spdx") == "Apache-2.0", "source SPDX mismatch")
    c.ok(rights.get("source_rights_state") == "BOUND", "source rights not bound")
    c.ok(rights.get("task_benchmark_rights_state") == "UNBOUND", "task rights overclaimed")
    c.ok(rights.get("model_service_rights_state") == "UNBOUND", "service rights overclaimed")
    c.ok(rights.get("generated_artifact_rights_state") == "UNBOUND", "artifact rights overclaimed")

    negative = loaded["P5_C5_V4_NEGATIVE_LEDGER.json"]
    c.ok(negative.get("blocking_field_count") == EXPECTED_BLOCKING, "negative blocker count mismatch")
    entries = negative.get("blocking_entries")
    c.ok(isinstance(entries, list) and len(entries) == EXPECTED_BLOCKING, "negative entries mismatch")
    c.ok(sorted(item.get("field_path") for item in entries) == blocking, "negative blocker identities mismatch")
    for item in entries:
        c.ok(bool(item.get("cause")), "negative cause missing")
        c.ok(bool(item.get("residual")), "negative residual missing")
        c.ok(bool(item.get("next_discriminator")), "negative discriminator missing")
    defects = negative.get("scientific_defects")
    c.ok(isinstance(defects, list) and len(defects) == 6, "scientific defect count mismatch")
    c.ok(any(item.get("state") == "UNSUPPORTED" for item in defects), "unsupported fibre not preserved")
    claims = negative.get("preserved_claims")
    c.ok(isinstance(claims, dict) and len(claims) == 9, "claim ledger mismatch")
    for name, state in sorted(claims.items()):
        c.ok(state == "CANNOT_CHECK", f"claim {name} overclaimed")
    c.ok(negative.get("top_tier_publication_readiness") == "NOT_ESTABLISHED", "publication readiness overclaimed")

    smoke = loaded["P5_C5_V4_SMOKE_RECEIPT.json"]
    c.ok(smoke.get("synthetic_cases") == 6, "smoke case count mismatch")
    c.ok(smoke.get("synthetic_cases_passed") == 6, "smoke failures")
    c.ok(smoke.get("raw_native_singleton_licences") == 0, "smoke licensed a raw singleton")
    c.ok(smoke.get("substantive_p5_cases") == 0, "smoke contains substantive P5")
    c.ok(smoke.get("performance") == "CANNOT_CHECK", "smoke overclaims performance")
    c.ok(smoke.get("protected_outcome_accessed") is False, "smoke accessed protected outcome")
    c.ok(smoke.get("terminal") == "SYNTHETIC_CONFORMANCE_ONLY", "smoke terminal mismatch")
    cases = smoke.get("cases")
    c.ok(isinstance(cases, list) and len(cases) == 6, "smoke cases missing")
    c.ok(cases[0].get("terminal") == "EVALUATOR_REPAIR", "positive synthetic mapping failed")
    for item in cases[1:]:
        c.ok(item.get("terminal") == "UNRESOLVED", f"negative smoke did not fail closed: {item}")

    parser_run = subprocess.run(
        [sys.executable, str(HERE / "p5_c5_native_parser.py"), "--self-smoke"],
        text=True,
        capture_output=True,
        check=False,
    )
    c.ok(parser_run.returncode == 0, "parser self-smoke process failed")
    parser_receipt = json.loads(parser_run.stdout)
    c.ok(parser_receipt == smoke, "parser self-smoke drifted from receipt")

    runner_run = subprocess.run(
        [
            sys.executable,
            str(HERE / "p5_c5_isolated_runner.py"),
            "--registry",
            str(HERE / "P5_C5_V4_FIELD_REGISTRY.json"),
            "--preflight",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    c.ok(runner_run.returncode == 3, "runner should fail closed with blockers")
    runner_receipt = json.loads(runner_run.stdout)
    c.ok(runner_receipt.get("blocking_field_count") == EXPECTED_BLOCKING, "runner blocker count mismatch")
    c.ok(runner_receipt.get("blocking_fields") == blocking, "runner blocker identity mismatch")
    c.ok(runner_receipt.get("execution_ready") is False, "runner overclaims readiness")
    c.ok(runner_receipt.get("protected_outcome_accessed") is False, "runner accessed protected outcome")

    resource = loaded["P5_C5_V4_RESOURCE_REGISTRY.json"]
    c.ok(resource.get("v4_bound_compute", {}).get("provider_parallelism") == 64, "parallelism drift")
    c.ok(resource.get("v4_bound_wallclock_seconds", {}).get("whole_c5_run") == 21600, "wallclock drift")
    c.ok(resource.get("fallbacks") == [], "fallback set not empty")
    c.ok(len(resource.get("unbound", [])) == 5, "resource blocker list mismatch")
    c.ok(resource.get("execution_ready") is False, "resources overclaim readiness")
    lock = (HERE / "DOUBLE_RATCHET_DEPENDENCY_LOCK_V4.uv.lock").read_text(encoding="utf-8")
    spec_text = (HERE / "DOUBLE_RATCHET_DEPENDENCY_SPEC_V4.toml").read_text(encoding="utf-8")
    c.ok(lock.count("[[package]]") == 46, "lock package count mismatch")
    for dep in ("boto3", "datasets", "pydantic", "pyyaml"):
        c.ok(f'"{dep}"' in spec_text, f"dependency spec missing {dep}")
    dep_binding = fields["runtime.dependency_lock"]["binding"]
    c.ok(dep_binding.get("package_entries") == 46, "dependency field package count mismatch")
    c.ok(dep_binding.get("lock_sha256") == file_sha256(HERE / "DOUBLE_RATCHET_DEPENDENCY_LOCK_V4.uv.lock"), "lock hash mismatch")
    c.ok(dep_binding.get("spec_sha256") == file_sha256(HERE / "DOUBLE_RATCHET_DEPENDENCY_SPEC_V4.toml"), "spec hash mismatch")

    checksum_path = HERE / "SHA256SUMS"
    manifest: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        c.ok(len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest), f"bad digest {name}")
        c.ok(name not in manifest, f"duplicate checksum {name}")
        manifest[name] = digest
    expected_names = sorted(
        p.name
        for p in HERE.iterdir()
        if p.is_file() and p.name != "SHA256SUMS" and not p.name.startswith(".")
    )
    c.ok(sorted(manifest) == expected_names, "checksum manifest file set mismatch")
    for name, digest in sorted(manifest.items()):
        c.ok(file_sha256(HERE / name) == digest, f"checksum mismatch {name}")

    c.ok(c.count >= audit.get("validator_contract", {}).get("minimum_checks", 10**9), "validator minimum not met")
    summary = {
        "arm_id": ARM_ID,
        "blocking_field_count": EXPECTED_BLOCKING,
        "bound_field_count": EXPECTED_BOUND,
        "checksum_entries": len(manifest),
        "execution_ready": False,
        "panel_ready": "0/6",
        "protected_outcome_accessed": False,
        "terminal": terminal,
        "validator_checks_passed": c.count,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValidationFailure, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"P5_C5_V4_VALIDATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(2)
