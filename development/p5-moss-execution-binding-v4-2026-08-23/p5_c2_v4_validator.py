#!/usr/bin/env python3
"""Deterministic scientific-contract validation for the P5 C2 V4 packet."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ARM_ID = "C2_DIRECT_SELF_EDIT__MOSS"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name: str) -> Any:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def package_count_pnpm(path: Path) -> int:
    in_packages = False
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "packages:":
            in_packages = True
            continue
        if in_packages and line == "snapshots:":
            break
        if in_packages and line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            count += 1
    return count


def import_parser():
    path = HERE / "p5_c2_native_parser.py"
    spec = importlib.util.spec_from_file_location("p5_c2_native_parser", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(status: str, verdict: str | None = None, *, commit: str | None = None, image: str | None = None) -> bytes:
    iterations: list[dict[str, Any]] = []
    if verdict is not None:
        iterations.append({"iteration": 1, "verdict": verdict, "commitHash": commit, "imageTag": image})
    value = {
        "schemaVersion": 6,
        "mode": "user",
        "evolutionDepth": "shallow",
        "flagBatchId": "outcome-blind-fixture",
        "triggerId": "outcome-blind-trigger",
        "status": status,
        "currentIteration": 1 if iterations else 0,
        "currentStage": "fixture",
        "iterations": iterations,
        # Native development values may exist but must not affect mapping.
        "bestScoreSoFar": 0.75,
        "tasks": {"stage_a": [{"id": "fictional", "baseline_score": 0.5}], "stage_c": []},
    }
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, observed: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "observed": observed})

    json_names = sorted(p.name for p in HERE.glob("*.json") if p.name != "AUDIT_RECEIPT_V4.json")
    parsed = {}
    for name in json_names:
        try:
            parsed[name] = load(name)
            ok = True
        except Exception as exc:  # pragma: no cover - audit path
            ok = False
            parsed[name] = str(exc)
        check(f"json_valid::{name}", ok)

    registry = parsed["P5_C2_V4_FIELD_REGISTRY.json"]
    result = parsed["P5_C2_V4_RESULT.json"]
    protocol = parsed["P5_C2_V4_EXECUTION_BINDING_PROTOCOL.json"]
    rights = parsed["P5_C2_V4_SOURCE_RIGHTS_MANIFEST.json"]
    smoke = parsed["P5_C2_V4_SMOKE_RECEIPT.json"]
    negative = parsed["P5_C2_V4_NEGATIVE_LEDGER.json"]

    required = registry["required_field_paths"]
    fields = registry["fields"]
    bound = [p for p in required if fields[p]["state"] == "BOUND"]
    blocking = [p for p in required if fields[p]["state"] != "BOUND"]
    check("required_fields_21", len(required) == 21 and len(set(required)) == 21, len(required))
    check("all_required_fields_present", set(required) == set(fields), sorted(set(required) ^ set(fields)))
    check("bound_fields_7", bound == registry["bound_fields"] and len(bound) == 7, bound)
    check("blocking_fields_14", blocking == registry["blocking_fields"] and len(blocking) == 14, blocking)
    check("execution_refused", registry["execution_ready"] is False and result["execution"]["c2_executed"] is False)
    check("panel_zero_of_six", result["execution"]["panel_confirmatory_ready_arms"] == 0 and result["execution"]["panel_required_arms"] == 6)
    check("delta_minus_four", result["v4_repairs"]["v3_to_v4_blocker_delta"] == -4)
    check("new_bindings_exact", result["v4_repairs"]["newly_bound_v3_fields"] == ["adapter.native_parser_binding", "model_provider.fallbacks", "resources.wallclock", "runtime.dependency_lock"])
    check("raw_singletons_zero", result["preserved_boundaries"]["raw_native_singleton_licences"] == 0)
    check("v3_counts_preserved", [result["preserved_boundaries"][k] for k in ("v3_synthetic_cases", "v3_supported_singleton_case_records", "v3_unresolved_case_records")] == [231, 40, 191])
    check("claims_cannot_check", all(value == "CANNOT_CHECK" for key, value in result["preserved_claims"].items() if key != "top_tier_publication_readiness"))
    check("publication_not_established", result["preserved_claims"]["top_tier_publication_readiness"] == "NOT_ESTABLISHED")

    host_lock = HERE / "MOSS_HOST_DEPENDENCY_LOCK_V4.uv.lock"
    node_lock = HERE / "MOSS_OPENCLAW_DEPENDENCY_LOCK_V4.pnpm-lock.yaml"
    check("host_lock_hash", sha(host_lock) == "382c5d3ad1eaa6ca85e970dca53b7c423f68878c23ceada8c3f17138c2b84b72", sha(host_lock))
    check("node_lock_hash", sha(node_lock) == "17a36bc38c1817eaee7a7c4264d58b127f5edb6a5054e4952545450cfde0337c", sha(node_lock))
    check("host_lock_entries_11", host_lock.read_text().count("[[package]]") == 11, host_lock.read_text().count("[[package]]"))
    check("node_lock_entries_1196", package_count_pnpm(node_lock) == 1196, package_count_pnpm(node_lock))
    check("parser_hash_bound", sha(HERE / "p5_c2_native_parser.py") == fields["adapter.native_parser_binding"]["binding"]["sha256"])
    check("runner_hash_bound", sha(HERE / "p5_c2_fail_closed_runner.py") == fields["resources.wallclock"]["binding"]["enforcer_sha256"])

    check("source_commit_exact", protocol["source_identity"]["commit_sha"] == "5453f1feebad44c199f5887f852fc5bc7fb7d4da")
    check("source_tree_exact", protocol["source_identity"]["tree_sha"] == "ebfcd6ac3ae00749240a5e2d8a96ad570adaf63f")
    check("source_archive_exact", protocol["source_identity"]["archive_sha256"] == "de6bb0e480749757d8e9b05a66c37c82228ea6d9d1e1cb92b6b32a3b28e5610e")
    check("benchmark_paths_zero", rights["authoritative_tree_audit"]["benchmark_prefixed_paths"] == 0)
    check("tree_receipt_not_truncated", rights["authoritative_tree_audit"]["github_tree_truncated"] is False)
    check("missing_runtime_cannot_check", fields["runtime.task_environment"]["state"] == "CANNOT_CHECK")
    check("benchmark_rights_unbound", fields["rights.task_and_benchmark_content"]["state"] == "UNBOUND")
    check("source_licence_layers_separate", [x["spdx"] for x in rights["licence_layers"][:2]] == ["Apache-2.0", "MIT"])

    parser = import_parser()
    expected = {
        "initialized": "PARTIAL",
        "in_progress": "PARTIAL",
        "swap_pending": "PARTIAL",
        "converged": "COMPLETE_SUCCESS",
        "rolled_back": "ERROR",
        "failed": "ERROR",
        "aborted_max_iter": "ABSTAIN",
        "aborted_streak": "ABSTAIN",
    }
    for status, expected_status in expected.items():
        if status == "converged":
            raw = manifest(status, "converged", commit="a" * 40, image="sha256:" + "b" * 64)
        else:
            raw = manifest(status)
        output = parser.parse_manifest_bytes(raw)
        check(f"parser_status::{status}", output["native_terminal"]["status"] == expected_status, output["native_terminal"]["status"])
        check(f"parser_unresolved::{status}", output["adapter_disposition"]["output"] == "UNRESOLVED")
        check(f"parser_no_score_mapping::{status}", output["source"]["development_scores_used_for_mapping"] is False)

    invalid = parser.parse_manifest_bytes(manifest("converged", "converged", commit=None, image=None))
    check("converged_requires_candidate_identity", invalid["native_terminal"]["status"] == "INVALID")
    try:
        value = json.loads(manifest("initialized"))
        value["protected_score"] = 1
        parser.parse_manifest_bytes(json.dumps(value).encode())
        protected_refused = False
    except parser.NativeParseError:
        protected_refused = True
    check("protected_key_refused", protected_refused)

    runner = subprocess.run(
        [sys.executable, str(HERE / "p5_c2_fail_closed_runner.py"), "--registry", str(HERE / "P5_C2_V4_FIELD_REGISTRY.json"), "--preflight"],
        capture_output=True,
        text=True,
        check=False,
    )
    runner_value = json.loads(runner.stdout)
    check("runner_preflight_refuses", runner.returncode == 3 and runner_value["blocking_field_count"] == 14, {"rc": runner.returncode, "count": runner_value["blocking_field_count"]})
    check("smoke_no_raw_retention", smoke["raw_or_large_payloads_retained"] is False)
    check("smoke_full_native_cannot_check", smoke["full_native_smoke"]["state"] == "CANNOT_CHECK")
    check("negative_ledger_recursive", len(negative["entries"]) >= 6 and all(all(k in x for k in ("cause", "residual", "next_discriminator", "positive_progress")) for x in negative["entries"]), len(negative["entries"]))

    forbidden_suffixes = {".tar", ".gz", ".zip", ".pdf", ".jsonl", ".sqlite", ".db", ".pt", ".bin"}
    retained_forbidden = [p.name for p in HERE.iterdir() if p.is_file() and any(p.name.endswith(s) for s in forbidden_suffixes)]
    check("no_raw_or_large_artifact_types", retained_forbidden == [], retained_forbidden)
    large_files = [p.name for p in HERE.iterdir() if p.is_file() and p.stat().st_size > 1024 * 1024]
    check("no_file_over_one_mib", large_files == [], large_files)

    failures = [item for item in checks if not item["passed"]]
    receipt = {
        "schema_version": "orion.p5.c2.validator-receipt.v4",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failures),
        "checks_failed": len(failures),
        "passed": not failures,
        "failures": failures,
        "checks": checks,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
