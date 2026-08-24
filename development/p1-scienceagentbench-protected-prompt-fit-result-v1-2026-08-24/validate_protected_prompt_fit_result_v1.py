#!/usr/bin/env python3
"""Validate the additive, body-free adverse protected prompt-fit result lane."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

LANE = Path(__file__).resolve().parent
REPO = LANE.parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
TERMINAL = (
    "P1_SAB_PROTECTED_PROMPT_FIT_PREFLIGHT_V1_FAIL: "
    "prompt template OS_PHASE1 has unreplaced marker or missing LF"
)
EXPECTED_FILES = {
    "DEVELOPMENT_PACKET.md",
    "HANDOFF_V1.md",
    "LIVE_GGUF_STAGING_RECEIPT_V1.json",
    "OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json",
    "PREFLIGHT_EXECUTION_FAILURE_RECEIPT_V1.json",
    "PROMPT_MARKER_COLLISION_DIAGNOSTIC_V1.json",
    "PROTECTED_PROMPT_FIT_RESULT_V1.json",
    "SHA256SUMS",
    "validate_protected_prompt_fit_result_v1.py",
}
UPSTREAMS = {
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_FREEZE_CONTRACT_V1.json": {
        "bytes": 9665,
        "sha256": "67e586c59f6b30beac7cab6e94cf2d176b2a1536a20ac8e9138fc8c7860e98f4",
    },
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py": {
        "bytes": 49039,
        "sha256": "23d0a7a1bfee2060f44e26a418564061d8aca412093ba930351ecf33a913f480",
    },
    "development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/DIRECT_ROUTE_PROMPT_BUNDLE_V1.json": {
        "bytes": 5959,
        "sha256": "03bfbf7e0870f9b385ee8ff9258df9e083fa9baa0813471795b9c80bafd1ebe6",
    },
    "development/p1-scienceagentbench-preflight-2026-08-24/MASK_MANIFEST_V1.json": {
        "bytes": 161005,
        "sha256": "442d9793024a91c752d34b9ad3185af612d1db3759458e91a61911b385cbe758",
    },
    "development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/PROTECTED_PROMPT_FIT_CONTRACT_V1.json": {
        "bytes": 7211,
        "sha256": "d029da6f87f2dd10c222f9fcff743c8efe647b6398e94d9b7499fe5d9b5d9074",
    },
    "development/p1-scienceagentbench-protected-prompt-fit-preflight-v1-2026-08-24/protected_prompt_fit_preflight_v1.py": {
        "bytes": 73080,
        "sha256": "fd462439a1f9d6e39a87fb1045ae0bfe2356b0de3f72cbb2b022def389f20d86",
    },
}

checks = 0


def require(condition: bool, label: str) -> None:
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1
    print(f"P1_SAB_PROTECTED_PROMPT_FIT_RESULT_V1_PASS: {label}")


def reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def reject_nonfinite(value: str) -> Any:
    raise ValueError(f"non-finite JSON number: {value}")


def load_json(name: str) -> dict[str, Any]:
    value = json.loads(
        (LANE / name).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_members,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise AssertionError(f"{name} must contain one JSON object")
    return value


def binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def assert_json_finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise AssertionError("non-finite JSON value")
    if isinstance(value, dict):
        for item in value.values():
            assert_json_finite(item)
    elif isinstance(value, list):
        for item in value:
            assert_json_finite(item)


# Lane shape and immutable merged upstream bindings.
actual_files = {path.name for path in LANE.iterdir() if path.is_file()}
require(actual_files == EXPECTED_FILES, "exact additive lane artifact set")
require(all(binding(REPO / path) == expected for path, expected in UPSTREAMS.items()), "merged upstream byte and SHA-256 bindings")

extraction = load_json("OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json")
require(
    binding(LANE / "OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json")
    == {"bytes": 1307, "sha256": "446064c3a59b8387deec447c8f65fa7f410cbfc9f7934a21a3ed956f083e1acb"},
    "exact outcome-blind extraction receipt",
)
require(
    extraction.get("schema_version") == "orion.p1.scienceagentbench.outcome-blind-row-extraction-receipt.v1"
    and extraction.get("authority") == "OWNER_AUTHORIZED_SEVEN_INPUT_FIELDS_ONLY__NO_GOLD_EVALUATOR_RUBRIC_OR_OUTCOME_AUTHORITY",
    "extraction receipt schema and authority",
)
require(
    extraction.get("projection", {}).get("fields")
    == ["instance_id", "domain", "task_inst", "output_fname", "domain_knowledge", "dataset_folder_tree", "dataset_preview"]
    and extraction.get("projection", {}).get("method") == "PYARROW_PARQUET_READ_TABLE_EXACT_COLUMN_PROJECTION"
    and extraction.get("projection", {}).get("pyarrow_version") == "21.0.0",
    "exact seven-field projection",
)
require(
    extraction.get("counts")
    == {
        "evaluator_fields_decoded": 0,
        "gold_fields_decoded": 0,
        "outcome_fields_decoded": 0,
        "rows": 102,
        "rubric_fields_decoded": 0,
        "value_bindings_checked": 510,
    }
    and extraction.get("official_outcomes_opened") == 0
    and extraction.get("official_tasks_executed") == 0
    and extraction.get("scientific_authority_delta") == "NONE",
    "outcome-blind extraction counts",
)
require(
    extraction.get("authorized_row_source")
    == {
        "bytes": 278882,
        "retention": "PRIVATE_NON_REPOSITORY_TEMP_ROOT_ONLY",
        "sha256": "c1a8901e8ad0ed4a1d5f15533def5e7ec6f514c61192a516f8f273c191e9a023",
    }
    and extraction.get("source")
    == {
        "dataset": "osunlp/ScienceAgentBench",
        "parquet_bytes": 129086,
        "parquet_sha256": "c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147",
        "revision": "9c6e96c9e74572e979b0930ee735041cef528cb7",
        "split": "verified",
    },
    "private source and verified Parquet bindings",
)

staging = load_json("LIVE_GGUF_STAGING_RECEIPT_V1.json")
require(
    binding(LANE / "LIVE_GGUF_STAGING_RECEIPT_V1.json")
    == {"bytes": 1306, "sha256": "3a3f82d3d376ee418aa1db3f20712dc2cf9d84ef1c147b4fccc331651dce2e73"},
    "exact independent live-GGUF receipt",
)
require(
    staging.get("schema_version") == "orion.p1.scienceagentbench.live-gguf-staging-receipt.v1"
    and staging.get("independent_verification", {}).get("completed_before_preflight") is True
    and staging.get("independent_verification", {}).get("measurement_method") == "FULL_FILE_SHA256_AND_BYTE_COUNT",
    "live-GGUF staging schema and independent timing",
)
require(
    staging.get("live_measurement")
    == {
        "live_model_bytes": 18556689568,
        "live_model_sha256": "fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad",
        "measurement_method": "HELD_FILE_DESCRIPTOR_FSTAT_AND_FULL_SHA256",
        "model_filename": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
    }
    and staging.get("source_receipt_sha256") == "3b50b7ec2fc3d4191b19e56391ddcbfdbbdfbc8144a3235e3987ef65f0846ade",
    "exact live model byte and SHA-256 binding",
)
require(
    staging.get("official_tasks_opened") == 0
    and staging.get("official_outcomes_opened") == 0
    and staging.get("scientific_authority_delta") == "NONE",
    "model staging has no task or outcome authority",
)

failure = load_json("PREFLIGHT_EXECUTION_FAILURE_RECEIPT_V1.json")
require(
    failure.get("schema_version") == "orion.p1.scienceagentbench.protected-prompt-fit-execution-failure-receipt.v1"
    and failure.get("authority") == "BODY_FREE_EXECUTION_FAILURE_BINDING_ONLY__NO_PROMPT_FIT_TOKENIZATION_GENERATION_EVALUATION_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
    "failure receipt schema and authority",
)
repo_binding = failure.get("repository", {})
require(
    repo_binding.get("execution_checkout_sha") == "6172ee61e336490b75d3a39bc3a8af86a8946c94"
    and repo_binding.get("merged_preflight_pr") == 1179
    and repo_binding.get("merged_preflight_commit") == "eaef8171de537b2d388c2b1310bccc23a92eaed3"
    and repo_binding.get("merged_preflight_files_modified_for_execution") is False
    and repo_binding.get("remote_staged_public_files") == UPSTREAMS,
    "failure receipt merged-preflight provenance",
)
execution = failure.get("execution", {})
require(
    execution.get("exit_code") == 1
    and execution.get("terminal_line") == TERMINAL
    and execution.get("token_ledger_supplied") is False
    and execution.get("output_exists") is False
    and execution.get("production_receipt_emitted") is False
    and execution.get("stdout_stderr")
    == {
        "bytes": 109,
        "retention": "PRIVATE_NON_REPOSITORY_REMOTE_ROOT_ONLY",
        "sha256": "c0869361865a938f946873051daa7b6f97223c9e90fea23a9834f31acb126693",
    },
    "exact merged CLI failure evidence",
)
require(
    execution.get("first_observed_failure") == {"instance_id": "4", "phase_id": "OS_PHASE1", "attempt": 1}
    and execution.get("failure_stage") == "MERGED_STATIC_PROMPT_RENDERING",
    "first observed failed-closed probe",
)
require(
    failure.get("private_source_receipt")
    == {
        "bytes": 4046,
        "retention": "PRIVATE_NON_REPOSITORY_REMOTE_ROOT_ONLY",
        "sha256": "0588007859d829f57bb0bf24df02424c7fb57ad053b91f914896afe9c753a7a6",
    },
    "private execution receipt binding without payload",
)
require(
    failure.get("input_bindings", {}).get("authorized_rows")
    == {
        "bytes": 278882,
        "retention": "PRIVATE_NON_REPOSITORY_TEMP_ROOT_ONLY",
        "sha256": "c1a8901e8ad0ed4a1d5f15533def5e7ec6f514c61192a516f8f273c191e9a023",
    }
    and failure.get("input_bindings", {}).get("outcome_blind_extraction_receipt")
    == binding(LANE / "OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json")
    and failure.get("input_bindings", {}).get("live_gguf_staging_receipt")
    == binding(LANE / "LIVE_GGUF_STAGING_RECEIPT_V1.json"),
    "failure receipt protected-input and public-receipt bindings",
)
require(
    failure.get("counts")
    == {
        "authorized_protected_tasks_opened_for_preflight": 102,
        "official_outcomes_opened": 0,
        "packet_bodies_retained": 0,
        "prompt_bodies_retained": 0,
        "prompt_fit_receipts_emitted": 0,
        "tasks_executed": 0,
    },
    "failure receipt zero-execution and zero-body counts",
)
require(
    failure.get("typed_result")
    == {
        "dynamic_rr_phase1": "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_AND_EXACT_GGUF_TOKEN_LEDGER_REQUIRED",
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "static_state_independent_prompt_fit": "CANNOT_CHECK_MERGED_PREFLIGHT_FAILED_BEFORE_RECEIPT",
        "token_counts": None,
    },
    "failure receipt typed CANNOT_CHECK result",
)

diagnostic = load_json("PROMPT_MARKER_COLLISION_DIAGNOSTIC_V1.json")
require(
    binding(LANE / "PROMPT_MARKER_COLLISION_DIAGNOSTIC_V1.json")
    == {"bytes": 277147, "sha256": "a65be72d96ecfd65a748cfa9a48f48248250d4a6f234e8340bc81ac5419bcf54"},
    "exact body-free collision diagnostic",
)
require(
    diagnostic.get("schema_version") == "P1_SAB_PRIVATE_PROMPT_MARKER_COLLISION_DIAGNOSTIC_V1"
    and diagnostic.get("authority") == "BODY_FREE_DIAGNOSTIC_ONLY__NO_PROMPT_PACKET_TASK_BODY_TOKENIZATION_GENERATION_EVALUATION_OR_OUTCOME_AUTHORITY",
    "diagnostic schema and authority",
)
require(
    diagnostic.get("method", {}).get("packet_builder") == "merged packetize_bound_row"
    and diagnostic.get("method", {}).get("renderer") == "merged _render_static_prompt"
    and diagnostic.get("method", {}).get("probe_output_fields")
    == ["instance_id", "phase_id", "attempt", "collision_sha256", "status_sha256"]
    and diagnostic.get("method", {}).get("task_packet_prompt_bodies_emitted") == 0,
    "diagnostic reused merged functions and emitted hashes only",
)
probes = diagnostic.get("probes")
require(isinstance(probes, list) and len(probes) == 1224, "diagnostic has 1,224 static probes")
require(
    all(
        isinstance(probe, dict)
        and set(probe) == {"instance_id", "phase_id", "attempt", "collision_sha256", "status_sha256"}
        and HEX64.fullmatch(probe["collision_sha256"]) is not None
        and HEX64.fullmatch(probe["status_sha256"]) is not None
        for probe in probes
    ),
    "diagnostic probe fields are body-free IDs and hashes",
)
expected_combinations = {
    (str(task), phase, attempt)
    for task in range(1, 103)
    for phase in ("RR_PHASE0", "OS_PHASE1", "NR_PHASE0", "NR_PHASE1")
    for attempt in (1, 2, 3)
}
observed_combinations = {(probe["instance_id"], probe["phase_id"], probe["attempt"]) for probe in probes}
require(observed_combinations == expected_combinations, "diagnostic covers each task phase and attempt exactly once")
summary = diagnostic.get("summary", {})
require(
    summary.get("tasks_probed") == 102
    and summary.get("static_prompt_probes") == 1224
    and summary.get("failed_probes") == 24
    and summary.get("passed_probes") == 1200
    and summary.get("affected_task_count") == 4
    and summary.get("first_affected_task_id") == "4"
    and summary.get("affected_task_ids") == ["4", "10", "88", "89"],
    "diagnostic exact affected task set and counts",
)
require(
    summary.get("phase_failure_counts") == {"RR_PHASE0": 0, "OS_PHASE1": 12, "NR_PHASE0": 0, "NR_PHASE1": 12}
    and summary.get("failed_with_double_brace_collision") == 24
    and summary.get("failed_without_double_brace_collision") == 0
    and summary.get("double_brace_collision_probes_that_passed") == 0
    and summary.get("noncollision_probes_that_passed") == 1200,
    "all and only double-brace collision probes failed",
)
require(
    summary.get("causal_diagnostic") == "ALL_AND_ONLY_DOUBLE_BRACE_COLLISION_PROBES_FAILED_CLOSED"
    and summary.get("collision_location") == "CANONICAL_PACKET_JSON_INSERTED_INTO_MERGED_TEMPLATE"
    and summary.get("merged_implementation_modified_or_bypassed") is False,
    "diagnostic cause is bounded and merged implementation unchanged",
)
require(
    diagnostic.get("claim_boundary")
    == {
        "official_outcomes_opened": 0,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "tasks_executed": 0,
        "token_counts": None,
    },
    "diagnostic claim boundary",
)

result = load_json("PROTECTED_PROMPT_FIT_RESULT_V1.json")
require(
    result.get("schema_version") == "orion.p1.scienceagentbench.protected-prompt-fit-result.v1"
    and result.get("status") == "CANNOT_CHECK_MERGED_PREFLIGHT_FAILED_CLOSED",
    "result schema and adverse status",
)
require(
    result.get("receipt_bindings")
    == {
        "execution_failure_receipt": binding(LANE / "PREFLIGHT_EXECUTION_FAILURE_RECEIPT_V1.json"),
        "live_gguf_staging_receipt": binding(LANE / "LIVE_GGUF_STAGING_RECEIPT_V1.json"),
        "outcome_blind_extraction_receipt": binding(LANE / "OUTCOME_BLIND_EXTRACTION_RECEIPT_V2.json"),
        "prompt_marker_collision_diagnostic": binding(LANE / "PROMPT_MARKER_COLLISION_DIAGNOSTIC_V1.json"),
    },
    "result binds every source receipt",
)
require(
    result.get("observed_execution")
    == {
        "exit_code": 1,
        "first_observed_failure": {"instance_id": "4", "phase_id": "OS_PHASE1", "attempt": 1},
        "output_exists": False,
        "production_receipt_emitted": False,
        "terminal_line": TERMINAL,
    },
    "result preserves exact execution failure",
)
result_diag = result.get("body_free_collision_diagnostic", {})
require(
    result_diag.get("tasks_probed") == 102
    and result_diag.get("static_prompt_probes") == 1224
    and result_diag.get("passed_probes") == 1200
    and result_diag.get("failed_probes") == 24
    and result_diag.get("affected_task_ids") == ["4", "10", "88", "89"]
    and result_diag.get("diagnostic") == "ALL_AND_ONLY_DOUBLE_BRACE_COLLISION_PROBES_FAILED_CLOSED"
    and result_diag.get("interpretation") == "POST_FAILURE_DIAGNOSIS_ONLY__DOES_NOT_REPLACE_A_PRODUCTION_PREFLIGHT_RECEIPT",
    "result carries bounded post-failure diagnosis",
)
require(
    result.get("typed_outcome")
    == {
        "all_state_independent_prompts_fit": None,
        "dynamic_rr_phase1": "CANNOT_CHECK_DYNAMIC_RR_PHASE0_STATE_AND_EXACT_GGUF_TOKEN_LEDGER_REQUIRED",
        "exact_gguf_token_ledger_present": False,
        "production_admissibility": "CANNOT_CHECK",
        "scientific_authority_delta": "NONE",
        "state_independent_static_prompt_fit": "CANNOT_CHECK_NO_PRODUCTION_RECEIPT",
        "token_counts": None,
    },
    "result retains null token counts and typed CANNOT_CHECK outcomes",
)
require(
    result.get("counts")
    == {
        "authorized_rows": 102,
        "evaluator_fields_decoded": 0,
        "gold_fields_decoded": 0,
        "official_outcomes_opened": 0,
        "outcome_fields_decoded": 0,
        "packet_bodies_in_repository": 0,
        "private_task_row_sources_in_repository": 0,
        "production_prompt_fit_receipts": 0,
        "prompt_bodies_in_repository": 0,
        "rubric_fields_decoded": 0,
        "tasks_executed": 0,
    },
    "result zero-outcome zero-execution zero-body counts",
)
require(
    result.get("claim_boundary")
    == {
        "credentials_opened": False,
        "evaluation_performed": False,
        "external_model_api_called": False,
        "generation_performed": False,
        "manuscript_or_pdf_changed": False,
        "merged_preflight_implementation_changed_or_bypassed": False,
        "pytest_or_ci_run_for_protected_execution": False,
        "result_is_production_admissibility": False,
        "result_is_prompt_fit_success": False,
        "result_is_scientific_evidence": False,
    },
    "result excludes generation evaluation and scientific promotion",
)
require(
    result.get("repository", {}).get("result_lane")
    == "development/p1-scienceagentbench-protected-prompt-fit-result-v1-2026-08-24/"
    and result.get("repository", {}).get("remote_staged_public_files") == UPSTREAMS,
    "result lane and remote staged public bindings",
)

# JSON body-safety and finite-value audit.
json_objects = [extraction, staging, failure, diagnostic, result]
for value in json_objects:
    assert_json_finite(value)
forbidden_body_keys = {
    "masked_packet",
    "recovered_packet",
    "prompt_body",
    "prompt_text",
    "task_body",
    "gold",
    "evaluator",
    "rubric",
    "outcome",
}

def keys_of(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        found.update(value)
        for item in value.values():
            found.update(keys_of(item))
    elif isinstance(value, list):
        for item in value:
            found.update(keys_of(item))
    return found

require(all(not (keys_of(value) & forbidden_body_keys) for value in json_objects), "no task packet prompt gold evaluator rubric or outcome body keys")


def key_paths(value: Any, prefix: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    found: list[tuple[str, ...]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = prefix + (key,)
            found.append(path)
            found.extend(key_paths(item, path))
    elif isinstance(value, list):
        for item in value:
            found.extend(key_paths(item, prefix))
    return found

row_paths: list[tuple[str, ...]] = []
for label, value in zip(("extraction", "staging", "failure", "diagnostic", "result"), json_objects):
    row_paths.extend((label,) + path for path in key_paths(value) if path[-1] == "rows")
require(row_paths == [("extraction", "counts", "rows")], "rows appears only as the extraction count")
require(
    not any(path.suffix.lower() in {".parquet", ".gguf", ".bin", ".safetensors"} for path in LANE.iterdir())
    and not any("AUTHORIZED_ROWS" in path.name or "TOKEN_LEDGER" in path.name for path in LANE.iterdir()),
    "no protected row source model or token ledger file",
)

# SHA256SUMS covers every artifact except itself and has no extras.
checksum_lines = (LANE / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
checksum_map: dict[str, str] = {}
for line in checksum_lines:
    digest, separator, name = line.partition("  ")
    if separator != "  " or not HEX64.fullmatch(digest) or not name or name in checksum_map:
        raise AssertionError("invalid SHA256SUMS line")
    checksum_map[name] = digest
expected_checksum_names = EXPECTED_FILES - {"SHA256SUMS"}
require(set(checksum_map) == expected_checksum_names, "SHA256SUMS exact artifact coverage")
require(all(binding(LANE / name)["sha256"] == digest for name, digest in checksum_map.items()), "SHA256SUMS content integrity")

print(f"P1_SAB_PROTECTED_PROMPT_FIT_RESULT_V1_VALIDATED checks={checks} status=CANNOT_CHECK tasks_executed=0 outcomes_opened=0")
